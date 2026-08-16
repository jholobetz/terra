<?php

namespace app\logic;

use Flight;

class SemanticSearchService
{
    private string $embeddingsPath;
    private string $embeddingsGzPath;
    private ?array $embeddingsIndex = null;
    private ?string $apiKey = null;
    private ?string $gcpProjectId = null;
    private ?string $credentialsPath = null;
    private ?string $cachedOAuthToken = null;
    private int $tokenExpiry = 0;

    public function __construct()
    {
        $this->embeddingsPath = PROJECT_ROOT . '/app/config/physics_embeddings.json';
        $this->embeddingsGzPath = PROJECT_ROOT . '/app/config/physics_embeddings.json.gz';
        $this->credentialsPath = PROJECT_ROOT . '/gcp-credentials.json';

        // Load environment variables if not loaded
        if (file_exists(PROJECT_ROOT . '/.env')) {
            $env = parse_ini_file(PROJECT_ROOT . '/.env');
            $this->apiKey = $env['GEMINI_API_KEY'] ?? getenv('GEMINI_API_KEY') ?: null;
            $this->gcpProjectId = $env['GCP_PROJECT_ID'] ?? getenv('GCP_PROJECT_ID') ?: 'gen-lang-client-0170965498';
        }
    }

    /**
     * Lazy-loads the vector database into memory from JSON or GZIP.
     */
    public function loadIndex(): ?array
    {
        if ($this->embeddingsIndex !== null) {
            return $this->embeddingsIndex;
        }

        if (file_exists($this->embeddingsPath)) {
            $json = file_get_contents($this->embeddingsPath);
            $this->embeddingsIndex = json_decode($json, true);
        } elseif (file_exists($this->embeddingsGzPath)) {
            $json = gzdecode(file_get_contents($this->embeddingsGzPath));
            $this->embeddingsIndex = json_decode($json, true);
        } elseif (file_exists(PROJECT_ROOT . '/app/config/physics_embeddings_checkpoint.json')) {
            $json = file_get_contents(PROJECT_ROOT . '/app/config/physics_embeddings_checkpoint.json');
            $this->embeddingsIndex = json_decode($json, true);
        }

        return $this->embeddingsIndex;
    }

    /**
     * Generates a 768-dim embedding vector for a query using Vertex AI or AI Studio endpoint.
     */
    public function embedQuery(string $text): ?array
    {
        // Try Vertex AI endpoint first using Service Account Token
        $token = $this->getOAuthToken();
        if ($token && $this->gcpProjectId) {
            $url = "https://us-central1-aiplatform.googleapis.com/v1/projects/{$this->gcpProjectId}/locations/us-central1/publishers/google/models/text-embedding-004:predict";
            $payload = [
                'instances' => [
                    ['content' => $text]
                ]
            ];

            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_POST => true,
                CURLOPT_POSTFIELDS => json_encode($payload),
                CURLOPT_HTTPHEADER => [
                    "Authorization: Bearer {$token}",
                    "Content-Type: application/json"
                ],
                CURLOPT_TIMEOUT => 8
            ]);

            $res = curl_exec($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

            if ($code === 200 && $res) {
                $data = json_decode($res, true);
                $values = $data['predictions'][0]['embeddings']['values'] ?? null;
                if (!empty($values)) {
                    return $values;
                }
            }
        }

        // Fallback to Gemini AI Studio API key
        if ($this->apiKey) {
            $url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={$this->apiKey}";
            $payload = [
                'model' => 'models/gemini-embedding-001',
                'content' => [
                    'parts' => [['text' => $text]]
                ]
            ];

            $ch = curl_init($url);
            curl_setopt_array($ch, [
                CURLOPT_RETURNTRANSFER => true,
                CURLOPT_POST => true,
                CURLOPT_POSTFIELDS => json_encode($payload),
                CURLOPT_HTTPHEADER => ["Content-Type: application/json"],
                CURLOPT_TIMEOUT => 8
            ]);

            $res = curl_exec($ch);
            $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

            if ($code === 200 && $res) {
                $data = json_decode($res, true);
                return $data['embedding']['values'] ?? null;
            }
        }

        return null;
    }

    /**
     * Executes dense semantic vector search across all indexed formulas.
     */
    public function search(string $query, int $limit = 10, float $minScore = 0.40): array
    {
        $query = trim($query);
        if (empty($query)) {
            return [];
        }

        $index = $this->loadIndex();
        if (empty($index)) {
            return [];
        }

        $queryVector = $this->embedQuery($query);
        if (empty($queryVector)) {
            return [];
        }

        $queryNorm = sqrt(array_sum(array_map(fn($x) => $x * $x, $queryVector)));
        if ($queryNorm <= 0.0) {
            return [];
        }

        $qLen = count($queryVector);
        $scored = [];

        foreach ($index as $formulaId => $entry) {
            $vec = $entry['vector'] ?? null;
            if (!is_array($vec) || count($vec) !== $qLen) {
                continue;
            }

            // Dot product
            $dot = 0.0;
            $vNormSq = 0.0;
            for ($i = 0; $i < $qLen; $i++) {
                $dot += $queryVector[$i] * $vec[$i];
                $vNormSq += $vec[$i] * $vec[$i];
            }

            $sim = ($vNormSq > 0) ? ($dot / ($queryNorm * sqrt($vNormSq))) : 0.0;

            if ($sim >= $minScore) {
                $scored[] = [
                    'id' => $formulaId,
                    'title' => $entry['title'] ?? $formulaId,
                    'equation' => $entry['equation'] ?? '',
                    'similarity' => round($sim, 4),
                    'confidence' => round($sim * 100, 1) . '%'
                ];
            }
        }

        // Sort descending by cosine similarity
        usort($scored, fn($a, $b) => $b['similarity'] <=> $a['similarity']);

        return array_slice($scored, 0, $limit);
    }

    /**
     * Generates or returns active OAuth2 token from service account credentials.
     */
    private function getOAuthToken(): ?string
    {
        $now = time();
        if ($this->cachedOAuthToken && $now < $this->tokenExpiry - 60) {
            return $this->cachedOAuthToken;
        }

        if (!file_exists($this->credentialsPath)) {
            return null;
        }

        $sa = json_decode(file_get_contents($this->credentialsPath), true);
        if (!$sa || empty($sa['client_email']) || empty($sa['private_key'])) {
            return null;
        }

        $header = ['alg' => 'RS256', 'typ' => 'JWT'];
        $claim = [
            'iss' => $sa['client_email'],
            'scope' => 'https://www.googleapis.com/auth/cloud-platform',
            'aud' => 'https://oauth2.googleapis.com/token',
            'exp' => $now + 3600,
            'iat' => $now
        ];

        $b64Header = rtrim(strtr(base64_encode(json_encode($header)), '+/', '-_'), '=');
        $b64Claim = rtrim(strtr(base64_encode(json_encode($claim)), '+/', '-_'), '=');
        $unsigned = "{$b64Header}.{$b64Claim}";

        $pkey = openssl_pkey_get_private($sa['private_key']);
        if (!$pkey) {
            return null;
        }

        openssl_sign($unsigned, $signature, $pkey, OPENSSL_ALGO_SHA256);
        $b64Sig = rtrim(strtr(base64_encode($signature), '+/', '-_'), '=');
        $jwt = "{$unsigned}.{$b64Sig}";

        $ch = curl_init('https://oauth2.googleapis.com/token');
        curl_setopt_array($ch, [
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => http_build_query([
                'grant_type' => 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion' => $jwt
            ]),
            CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded'],
            CURLOPT_TIMEOUT => 8
        ]);

        $res = curl_exec($ch);
        $code = curl_getinfo($ch, CURLINFO_HTTP_CODE);

        if ($code === 200 && $res) {
            $data = json_decode($res, true);
            $this->cachedOAuthToken = $data['access_token'] ?? null;
            $this->tokenExpiry = $now + (int)($data['expires_in'] ?? 3600);
            return $this->cachedOAuthToken;
        }

        return null;
    }
}
