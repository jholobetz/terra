<?php

namespace app\controllers;

use flight\Engine;
use Flight;

require_once PROJECT_ROOT . '/app/logic/AuthService.php';
require_once PROJECT_ROOT . '/app/logic/VariableAggregator.php';

class PhysicsController
{
    protected Engine $app;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    /**
     * Resolves the decoupled PhysicsService container instance.
     */
    private function service()
    {
        return $this->app->physicsService();
    }

    /**
     * Resolves a fresh AuthService instance reflecting current environment and request headers.
     */
    private function authService(): \app\logic\AuthService
    {
        return new \app\logic\AuthService();
    }

    /**
     * Logs internal exceptions in production and returns a sanitized message safe for public JSON responses.
     */
    private function publicErrorMessage(\Throwable $e, string $fallback = 'Internal server error.'): string
    {
        if ($this->authService()->isProduction()) {
            error_log('[PhysicsController] ' . get_class($e) . ': ' . $e->getMessage());
            return $fallback;
        }
        return $e->getMessage();
    }

    /**
     * Evaluates production readiness across MariaDB, writable log/cache directories,
     * and local SymPy CAS runtime availability without spawning subprocesses or leaking paths.
     */
    public function evaluateHealthChecks(): array
    {
        $dbOk = false;
        try {
            $db = $this->app->db();
            if ($db) {
                if (method_exists($db, 'runQuery')) {
                    $stmt = $db->runQuery('SELECT 1');
                    $dbOk = ($stmt !== false);
                } elseif (method_exists($db, 'query')) {
                    $stmt = $db->query('SELECT 1');
                    $dbOk = ($stmt !== false);
                }
            }
        } catch (\Throwable $e) {
            $dbOk = false;
        }

        $logDir = PROJECT_ROOT . '/app/log';
        $cacheDir = PROJECT_ROOT . '/public/cache';
        if (!is_dir($logDir)) {
            @mkdir($logDir, 0775, true);
        }
        if (!is_dir($cacheDir)) {
            @mkdir($cacheDir, 0775, true);
        }
        $storageOk = is_dir($logDir) && is_writable($logDir) && is_dir($cacheDir) && is_writable($cacheDir);

        $casScript = is_file(PROJECT_ROOT . '/lib/cas/cas_engine.py')
            ? PROJECT_ROOT . '/lib/cas/cas_engine.py'
            : PROJECT_ROOT . '/scripts/lib/cas_engine.py';
        $casScriptOk = is_file($casScript);

        $pythonOk = false;
        $venvPython = PROJECT_ROOT . '/.venv/bin/python3';
        if (is_file($venvPython) && is_executable($venvPython)) {
            $pythonOk = true;
        } else {
            $pathDirs = explode(PATH_SEPARATOR, (string)(getenv('PATH') ?: '/usr/local/bin:/usr/bin:/bin'));
            foreach ($pathDirs as $dir) {
                $candidate = rtrim($dir, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . 'python3';
                if ($dir !== '' && is_file($candidate) && is_executable($candidate)) {
                    $pythonOk = true;
                    break;
                }
            }
        }
        $casOk = $casScriptOk && $pythonOk;

        $allHealthy = $dbOk && $storageOk && $casOk;
        return [
            'status' => $allHealthy ? 'ok' : 'degraded',
            'http_code' => $allHealthy ? 200 : 503,
            'checks' => [
                'database' => $dbOk,
                'storage' => $storageOk,
                'cas_runtime' => $casOk,
            ],
        ];
    }

    /**
     * Zero-leak JSON readiness probe (/healthz and /physics/healthz).
     */
    public function healthz(): void
    {
        if (class_exists('\Tracy\Debugger')) {
            \Tracy\Debugger::$showBar = false;
        }
        if (!headers_sent()) {
            header('Content-Type: application/json; charset=utf-8');
            header('Cache-Control: no-store, no-cache, must-revalidate');
        }
        $report = $this->evaluateHealthChecks();
        http_response_code($report['http_code']);
        echo json_encode([
            'status' => $report['status'],
            'checks' => $report['checks'],
        ], JSON_UNESCAPED_SLASHES);
    }

    /**
     * Database index synchronization endpoint (Admin / Local Studio Only).
     */
    public function sync(): void
    {
        $auth = Flight::authService();
        if (!$auth->hasRole('admin')) {
            http_response_code(403);
            echo '403 Forbidden: Admin privileges required.';
            return;
        }

        $this->service()->performSync();
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        touch($syncLock);
        $this->app->redirect($this->app->request()->referrer ?: '/physics');
    }

    /**
     * Public JSON endpoint serving the search index.
     */
    public function searchIndex(): void
    {
        $path = PROJECT_ROOT . '/app/config/content/search_index.json';
        if (file_exists($path)) {
            $this->app->json(json_decode(file_get_contents($path), true));
        } else {
            $this->app->json([]);
        }
    }

    /**
     * Action redirecting to a randomly selected physics subtopic.
     */
    public function randomSubtopic(): void
    {
        // 1. Try querying database for random subtopic slug
        try {
            $pdo = $this->app->db();
            $stmt = $pdo->query("SELECT slug FROM subtopics ORDER BY RAND() LIMIT 1");
            $slug = $stmt ? $stmt->fetchColumn() : null;

            if ($slug) {
                $this->app->redirect('/physics/subtopic/' . $slug);
                return;
            }
        } catch (\Throwable $e) {
            // DB query uninitialized, fall through to search index
        }

        // 2. Fallback using search index
        try {
            $content = $this->service()->getPhysicsContent();
            $searchIndex = $content['search_index'] ?? [];
            $subtopicSlugs = [];
            foreach ($searchIndex as $item) {
                if (($item['type'] ?? '') === 'subtopic' && !empty($item['slug'])) {
                    $subtopicSlugs[] = $item['slug'];
                }
            }
            if (!empty($subtopicSlugs)) {
                $randomSlug = $subtopicSlugs[array_rand($subtopicSlugs)];
                $this->app->redirect('/physics/subtopic/' . $randomSlug);
                return;
            }
        } catch (\Throwable $e) {
            // Fallback to classical mechanics if all else fails
        }

        $this->app->redirect('/physics/topic/classical-mechanics');
    }

    /**
     * View action rendering physical constants.
     */
    public function constants()
    {
        $notation = $this->service()->getNotation();
        
        // Filter notation where type is 'constant'
        $constants = array_filter($notation, function($item) {
            return ($item['type'] ?? '') === 'constant';
        });
        
        // Fallback to legacy constants if notation is empty
        if (empty($constants)) {
            $content = $this->service()->getPhysicsContent();
            $constants = $content['constants'] ?? [];
        }
        
        $this->renderWithLayout('physics/constants', [
            'title' => 'Fundamental Physical Constants',
            'constants' => $constants
        ]);
    }

    public function symbols()
    {
        $content = $this->service()->getPhysicsContent();
        $notation = $this->service()->getNotation();
        $searchIndex = $content['search_index'] ?? [];
        $topics = $content['topics'] ?? [];
        
        $this->renderWithLayout('physics/symbols', [
            'title' => 'Fundamental Symbols & Notation Reference',
            'notation' => $notation,
            'searchIndex' => $searchIndex,
            'topics' => $topics
        ]);
    }

    /**
     * Deprecated action: redirects legacy Dimensional Solver requests to the Lab Tools hub.
     */
    public function dimensionalSolver()
    {
        \Flight::redirect('/physics/lab-tools', 301);
    }

    /**
     * View action rendering the interactive Multi-Representation Notation Toggle.
     */
    public function notationToggle()
    {
        $this->renderWithLayout('physics/notation_toggle', [
            'title' => 'Multi-Representation Notation Toggle'
        ]);
    }

    /**
     * View action rendering the Symbolic Legendre Transformer.
     */
    public function legendreTransformer()
    {
        $this->renderWithLayout('physics/legendre_transformer', [
            'title' => 'Symbolic Legendre Transformer'
        ]);
    }

    /**
     * View action rendering the Lab Tools landing page.
     */
    public function labTools()
    {
        $this->renderWithLayout('physics/lab_tools', [
            'title' => 'Lab Tools Hub',
            'extra_css' => ['lab_tools.css']
        ]);
    }

    /**
     * View action rendering the interactive Equation Explainer.
     */
    public function equationExplainer()
    {
        $id = $this->app->request()->query['id'] ?? '';
        $latex = $this->app->request()->query['latex'] ?? '';
        $subtopicSlug = $this->app->request()->query['subtopic'] ?? '';
        $domain = $this->app->request()->query['domain'] ?? '';
        
        if (!empty($latex)) {
            $latex = trim($latex, " '\t\n\r\0\x0B\"");
            $quotePos = strpos($latex, "'");
            if ($quotePos !== false && preg_match('/\'\s*(?:\\\\text|\\\\mathrm|\\\\mathbf|[a-zA-Z]{2,})/', substr($latex, $quotePos))) {
                $latex = trim(substr($latex, 0, $quotePos));
            }
        }
        
        $formula = null;
        $subtopics = [];
        $subtopicVariables = [];
        
        if (!empty($id)) {
            $formula = $this->service()->getFormulaWithHierarchy($id);
            if ($formula) {
                $subtopics = $this->service()->getSubtopicsByFormula($id);
            }
        }
        
        if (!$formula && !empty($latex)) {
            $formula = $this->service()->searchFormulaByLatex($latex);
            if ($formula && !empty($formula['id'])) {
                $formula = $this->service()->getFormulaWithHierarchy($formula['id']);
                $subtopics = $this->service()->getSubtopicsByFormula($formula['id']);
            } else if (!$formula) {
                $formula = $this->service()->synthesizeFormulaExplanation($latex);
            }
        }
        if (empty($formula)) {
            $formula = null;
        }
        
        if (!empty($subtopicSlug)) {
            $subtopicData = $this->service()->fetchAndPrepare('subtopics', $subtopicSlug);
            if (!empty($subtopicData)) {
                $subtopicVariables = $subtopicData['variables'] ?? [];
            }
        }
        
        if (($this->app->request()->query['format'] ?? '') === 'json') {
            $this->apiExplain();
            return;
        }

        $currentUser = Flight::authService()->getCurrentUser();

        $this->renderWithLayout('physics/equation_explainer', [
            'title' => 'Interactive Equation Explainer',
            'id' => $id,
            'latex' => $latex,
            'formula' => $formula,
            'subtopics' => $subtopics,
            'subtopicSlug' => $subtopicSlug,
            'subtopicVariables' => $subtopicVariables,
            'domain' => $domain,
            'currentUser' => $currentUser,
            'extra_css' => ['equation_explainer.css']
        ]);
    }

    /**
     * REST Action matching user-submitted raw LaTeX or ID to a database formula with full parent/child hierarchy.
     */
    public function apiExplain()
    {
        header('Content-Type: application/json; charset=utf-8');
        
        $id = $this->app->request()->query['id'] ?? '';
        $latex = $this->app->request()->query['latex'] ?? '';

        if (!empty($latex)) {
            $latex = trim($latex, " '\t\n\r\0\x0B\"");
            $quotePos = strpos($latex, "'");
            if ($quotePos !== false && preg_match('/\'\s*(?:\\\\text|\\\\mathrm|\\\\mathbf|[a-zA-Z]{2,})/', substr($latex, $quotePos))) {
                $latex = trim(substr($latex, 0, $quotePos));
            }
        }

        if (!empty($id)) {
            $formula = $this->service()->getFormulaWithHierarchy($id);
            if ($formula) {
                echo json_encode(['success' => true, 'formula' => $formula]);
                return;
            }
        }
        
        if (empty($latex)) {
            echo json_encode(['success' => false, 'error' => 'No formula ID or LaTeX provided.']);
            return;
        }
        
        $formula = $this->service()->searchFormulaByLatex($latex);
        if ($formula && !empty($formula['id'])) {
            $formula = $this->service()->getFormulaWithHierarchy($formula['id']);
        } else if (!$formula) {
            $formula = $this->service()->synthesizeFormulaExplanation($latex);
        }

        if (empty($formula)) {
            echo json_encode(['success' => false, 'error' => 'Could not analyze or resolve formula.']);
            return;
        }

        echo json_encode(['success' => true, 'formula' => $formula]);
    }

    /**
     * REST Action executing symbolic limit evaluations, series expansions,
     * and dimensional consistency via the local SymPy CAS engine.
     * Hardened with deterministic SHA-256 result caching and per-IP rate limiting.
     */
    public function apiCasEvaluate()
    {
        header('Content-Type: application/json; charset=utf-8');

        $req = $this->app->request();
        $payload = [];

        if ($req->method === 'POST') {
            $rawBody = $req->getBody();
            $decoded = json_decode($rawBody, true);
            if (is_array($decoded)) {
                $payload = $decoded;
            } else {
                $payload = $req->data->getData() ?: [];
            }
        } else {
            $payload = $req->query->getData() ?: [];
        }

        $latex = $payload['latex'] ?? $payload['lagrangian'] ?? '';
        if (empty($latex)) {
            echo json_encode(['success' => false, 'error' => 'No mathematical equation or Lagrangian provided.']);
            return;
        }

        if (strlen((string)$latex) > 2048) {
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Payload exceeds maximum allowed expression length (2048 bytes).']);
            return;
        }

        $casScript = file_exists(PROJECT_ROOT . '/lib/cas/cas_engine.py')
            ? PROJECT_ROOT . '/lib/cas/cas_engine.py'
            : PROJECT_ROOT . '/scripts/lib/cas_engine.py';
        $pythonBin = PROJECT_ROOT . '/.venv/bin/python3';
        if (!file_exists($pythonBin)) {
            $pythonBin = 'python3';
        }

        $mode = $payload['mode'] ?? 'evaluate';
        $casPayload = array_merge([
            'mode' => $mode,
            'latex' => $latex,
            'limit_var' => $payload['limit_var'] ?? null,
            'limit_to' => $payload['limit_to'] ?? null,
            'series_order' => isset($payload['series_order']) ? (int)$payload['series_order'] : 4
        ], $payload);
        ksort($casPayload);

        $jsonPayload = json_encode($casPayload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

        // 1. Check Deterministic SHA-256 CAS Result Cache (<1ms fast path)
        $scriptMtime = file_exists($casScript) ? filemtime($casScript) : 0;
        $parserScript = PROJECT_ROOT . '/lib/cas/latex_parser.py';
        if (file_exists($parserScript)) {
            $scriptMtime = max($scriptMtime, (int)filemtime($parserScript));
        }
        $cacheHash = hash('sha256', $jsonPayload . '|' . $scriptMtime);
        $cacheDir = is_writable(PROJECT_ROOT . '/public/cache')
            ? PROJECT_ROOT . '/public/cache/cas'
            : sys_get_temp_dir() . '/terra_cas_cache';
        $cacheFile = $cacheDir . '/' . $cacheHash . '.json';

        $bypassCache = !empty($payload['nocache']);
        if (!$bypassCache && file_exists($cacheFile)) {
            $cachedRaw = file_get_contents($cacheFile);
            $cachedResult = json_decode($cachedRaw ?: '', true);
            if (is_array($cachedResult) && !empty($cachedResult['success'])) {
                $cachedResult['cached'] = true;
                echo json_encode($cachedResult);
                return;
            }
        }

        // 2. Per-IP Sliding-Window Rate Limiter on Cold Subprocess Spawns
        $auth = $this->authService();
        $isLocalAdmin = $auth->isLocalDevStudio();
        $maxPerWindow = $isLocalAdmin ? 120 : 20;
        $windowSeconds = 60;
        $clientIp = $auth->resolveClientIp();

        if (!$this->consumeCasRateLimit($clientIp, $maxPerWindow, $windowSeconds)) {
            http_response_code(429);
            echo json_encode([
                'success' => false,
                'error' => 'Rate limit exceeded for live symbolic CAS evaluation. Please wait a moment and try again.'
            ]);
            return;
        }

        // 3. Execute Sandboxed SymPy Subprocess
        $cmd = escapeshellcmd($pythonBin) . ' ' . escapeshellarg($casScript) . ' ' . escapeshellarg($jsonPayload);
        $output = shell_exec($cmd);

        if ($output === null) {
            echo json_encode(['success' => false, 'error' => 'Failed to execute symbolic CAS engine.']);
            return;
        }

        $result = json_decode($output, true);
        if (!$result) {
            $errPayload = ['success' => false, 'error' => 'Invalid response from CAS engine.'];
            if (!$auth->isProduction()) {
                $errPayload['raw_output'] = $output;
            } else {
                error_log('[PhysicsController::apiCasEvaluate] Invalid CAS output: ' . substr((string)$output, 0, 500));
            }
            echo json_encode($errPayload);
            return;
        }

        // Persist valid evaluations in deterministic disk cache under LOCK_EX
        if (!empty($result['success'])) {
            if (!is_dir($cacheDir)) {
                @mkdir($cacheDir, 0775, true);
            }
            @file_put_contents($cacheFile, json_encode($result, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
        }

        $result['cached'] = false;
        echo json_encode($result);
    }

    /**
     * Sliding-window rate limiter for expensive API endpoints (stored outside DocumentRoot).
     * Uses flock(LOCK_EX) to prevent race conditions under concurrent HTTP requests.
     */
    public function consumeCasRateLimit(string $clientIp, int $maxRequests, int $windowSeconds, string $scope = 'cas'): bool
    {
        $rlDir = sys_get_temp_dir() . '/terra_cas_ratelimit';
        if (!is_dir($rlDir)) {
            @mkdir($rlDir, 0775, true);
        }

        $bucketKey = ($scope === 'cas') ? $clientIp : ($scope . '|' . $clientIp);
        $bucketFile = $rlDir . '/' . hash('sha256', $bucketKey) . '.json';
        $fp = @fopen($bucketFile, 'c+');
        if ($fp === false) {
            return true;
        }
        if (!flock($fp, LOCK_EX)) {
            fclose($fp);
            return true;
        }

        $now = time();
        $timestamps = [];

        rewind($fp);
        $raw = stream_get_contents($fp);
        if ($raw !== false && $raw !== '') {
            $decoded = json_decode($raw, true);
            if (is_array($decoded)) {
                $cutoff = $now - $windowSeconds;
                foreach ($decoded as $ts) {
                    if (is_int($ts) && $ts > $cutoff) {
                        $timestamps[] = $ts;
                    }
                }
            }
        }

        if (count($timestamps) >= $maxRequests) {
            flock($fp, LOCK_UN);
            fclose($fp);
            return false;
        }

        $timestamps[] = $now;
        ftruncate($fp, 0);
        rewind($fp);
        fwrite($fp, json_encode($timestamps));
        fflush($fp);
        flock($fp, LOCK_UN);
        fclose($fp);
        return true;
    }

    /**
     * REST Action to define an unregistered LaTeX formula via Gemini AI and save to database.
     */
    public function apiDefineFormula()
    {
        header('Content-Type: application/json; charset=utf-8');
        set_time_limit(120);

        $auth = Flight::authService();
        if (!$auth->hasRole('admin')) {
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => '403 Forbidden: Admin or Local Studio authority required.']);
            return;
        }

        try {
            $input = json_decode(file_get_contents('php://input'), true);
            $latex = $input['latex'] ?? $this->app->request()->post['latex'] ?? $this->app->request()->query['latex'] ?? '';

            if (empty($latex)) {
                echo json_encode(['success' => false, 'error' => 'No LaTeX equation provided.']);
                return;
            }

            // Run python generator script
            $python = __DIR__ . '/../../.venv/bin/python3';
            if (!file_exists($python)) {
                $python = 'python3';
            }
            $script = __DIR__ . '/../../scripts/maintenance/generate_gemini_formula.py';
            
            $command = [$python, $script, '--latex', $latex];
            $descriptorspec = [
                0 => ["pipe", "r"],
                1 => ["pipe", "w"],
                2 => ["pipe", "w"]
            ];

            $process = proc_open($command, $descriptorspec, $pipes);
            if (!is_resource($process)) {
                echo json_encode(['success' => false, 'error' => 'Failed to initialize process for formula generator.']);
                return;
            }

            fclose($pipes[0]);
            $output = stream_get_contents($pipes[1]);
            fclose($pipes[1]);
            $stderr = stream_get_contents($pipes[2]);
            fclose($pipes[2]);
            $returnCode = proc_close($process);

            if (empty($output)) {
                echo json_encode([
                    'success' => false, 
                    'error' => 'Failed to execute Gemini formula generator script: ' . ($stderr ?: 'Empty output')
                ]);
                return;
            }

            $res = json_decode(trim($output), true);
            if (!$res) {
                echo json_encode([
                    'success' => false, 
                    'error' => 'Invalid response from formula generator: ' . $output . ($stderr ? ' (stderr: ' . $stderr . ')' : '')
                ]);
                return;
            }

            echo json_encode($res);
        } catch (\Throwable $e) {
            echo json_encode([
                'success' => false,
                'error' => 'Server error while defining formula: ' . $e->getMessage()
            ]);
        }
    }

    /**
     * REST Action to load subtopic variables dynamically (for referrer-based overrides).
     */
    public function apiGetSubtopicVariables(string $slug)
    {
        header('Content-Type: application/json; charset=utf-8');
        $subtopic = $this->service()->fetchAndPrepare('subtopics', $slug);
        if ($subtopic) {
            echo json_encode([
                'success' => true,
                'variables' => $subtopic['variables'] ?? []
            ]);
        } else {
            echo json_encode([
                'success' => false,
                'error' => 'Subtopic not found'
            ]);
        }
    }

    /**
     * API action serving high-performance MariaDB FULLTEXT search results.
     */
    public function apiSearch()
    {
        header('Content-Type: application/json; charset=utf-8');
        $query = $_GET['q'] ?? '';
        $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
        
        $results = $this->service()->searchContent($query, $limit);
        echo json_encode($results);
    }

    /**
     * API action serving dense vector semantic search powered by Vertex AI text-embedding-004.
     */
    public function apiSemanticSearch()
    {
        header('Content-Type: application/json; charset=utf-8');
        $query = $_GET['q'] ?? '';
        $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
        $minScore = isset($_GET['min_score']) ? (float)$_GET['min_score'] : 0.40;

        $auth = $this->authService();
        $maxPerWindow = $auth->isLocalDevStudio() ? 120 : 30;
        if (!$this->consumeCasRateLimit($auth->resolveClientIp(), $maxPerWindow, 60, 'semantic_search')) {
            http_response_code(429);
            echo json_encode([
                'success' => false,
                'error' => 'Rate limit exceeded for semantic search. Please wait a moment and try again.',
                'results' => []
            ]);
            return;
        }

        try {
            $semanticService = Flight::semanticSearchService();
            $results = $semanticService->search($query, $limit, $minScore);
            echo json_encode([
                'success' => true,
                'query' => $query,
                'total' => count($results),
                'results' => $results
            ]);
        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'error' => $this->publicErrorMessage($e, 'Semantic search is temporarily unavailable.'),
                'results' => []
            ]);
        }
    }

    /**
     * API action returning conceptually isomorphic related subtopics computed via dense vectors.
     */
    public function apiRelatedSubtopics(string $slug)
    {
        header('Content-Type: application/json; charset=utf-8');
        try {
            $semanticService = Flight::semanticSearchService();
            $results = $semanticService->getRelatedSubtopics($slug, 4);
            echo json_encode([
                'success' => true,
                'slug' => $slug,
                'total' => count($results),
                'results' => $results
            ]);
        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'error' => $this->publicErrorMessage($e, 'Could not load related subtopics.'),
                'results' => []
            ]);
        }
    }

    /**
     * API action returning local derivation & lineage subgraph for an equation.
     */
    public function apiFormulaGraph(string $id)
    {
        header('Content-Type: application/json; charset=utf-8');
        try {
            $depth = (int) (Flight::request()->query->depth ?? 2);
            if ($depth < 1) $depth = 1;
            if ($depth > 4) $depth = 4;
            require_once __DIR__ . '/../logic/FormulaGraphService.php';
            $subgraph = \App\Logic\FormulaGraphService::getFormulaSubgraph($id, $depth);
            echo json_encode([
                'success' => true,
                'data' => $subgraph
            ]);
        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'error' => $this->publicErrorMessage($e, 'Could not load formula derivation graph.')
            ]);
        }
    }

    /**
     * API action finding shortest derivation path between two formulas.
     */
    public function apiFormulaPath()
    {
        header('Content-Type: application/json; charset=utf-8');
        try {
            $start = Flight::request()->query->start ?? '';
            $end = Flight::request()->query->end ?? '';
            if (empty($start) || empty($end)) {
                echo json_encode(['success' => false, 'error' => 'Both start and end parameters required']);
                return;
            }
            require_once __DIR__ . '/../logic/FormulaGraphService.php';
            $path = \App\Logic\FormulaGraphService::findDerivationPath($start, $end);
            echo json_encode([
                'success' => true,
                'data' => $path
            ]);
        } catch (\Throwable $e) {
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'error' => $this->publicErrorMessage($e, 'Could not compute formula derivation path.')
            ]);
        }
    }

    /**
     * View action rendering the interactive Physics Universe Knowledge Graph.
     */
    public function universeGraph()
    {
        $this->renderWithLayout('physics/universe_graph', [
            'title' => "Physics Universe Graph - Mathematical Lineage & Derivations"
        ]);
    }

    /**
     * View action rendering the interactive Noether's Vault (Symmetry-to-Conservation Mapping).
     */
    public function noethersVault()
    {
        $this->renderWithLayout('physics/noethers_vault', [
            'title' => "Noether's Vault - Symmetry & Conservation"
        ]);
    }

    /**
     * View action rendering the interactive Classical-to-Quantum Correspondence Workspace (Pillar D).
     */
    public function correspondenceWorkspace()
    {
        $this->renderWithLayout('physics/correspondence_workspace', [
            'title' => "Correspondence Workspace - Classical vs Quantum Flows"
        ]);
    }

    /**
     * View action rendering the interactive Anthropic Constant Tuner & Cosmological Scaling Sandbox (Pillar E).
     */
    public function anthropicTuner()
    {
        $this->renderWithLayout('physics/anthropic_tuner', [
            'title' => "Anthropic Constant Tuner & Cosmological Sandbox"
        ]);
    }

    /**
     * Deprecated action: redirects legacy Genealogy Explorer prototype requests to the canonical Universe Graph.
     */
    public function genealogyExplorer()
    {
        \Flight::redirect('/physics/universe-graph', 301);
    }

    /**
     * View action rendering interactive simulations list.
     */
    public function simulations()
    {
        $sims = $this->service()->fetchAllData('simulations');
        $configPath = PROJECT_ROOT . '/app/config/simulations.json';
        $simsConfig = file_exists($configPath) ? (json_decode(file_get_contents($configPath), true) ?: []) : [];

        foreach ($sims as &$s) {
            $slug = $s['slug'] ?? '';
            if (isset($simsConfig[$slug])) {
                $cfg = $simsConfig[$slug];
                foreach ($cfg as $k => $v) {
                    if (!isset($s[$k]) || empty($s[$k]) || ($k === 'equations' && empty($s[$k]))) {
                        $s[$k] = $v;
                    }
                }
                if (is_string($s['equations'] ?? null)) {
                    $s['equations'] = json_decode($s['equations'], true) ?: [];
                }
                if (empty($s['equations']) && !empty($cfg['equations'])) {
                    $s['equations'] = $cfg['equations'];
                }
            }
        }
        unset($s);

        $this->renderWithLayout('physics/simulations', [
            'title' => 'The Living Physics Observatory',
            'simulations' => $sims,
        ]);
    }

    /**
     * View action rendering an individual simulation sandbox page.
     */
    public function viewSimulation(string $slug)
    {
        $data = $this->service()->fetchAndPrepare('simulations', $slug);
        $configPath = PROJECT_ROOT . '/app/config/simulations.json';
        $simsConfig = file_exists($configPath) ? (json_decode(file_get_contents($configPath), true) ?: []) : [];
        if (isset($simsConfig[$slug])) {
            $data = array_merge($data ?: [], $simsConfig[$slug]);
        }
        if (!$data) {
            $this->app->notFound();
            return;
        }
        if (isset($data['equations']) && is_string($data['equations'])) {
            $data['equations'] = json_decode($data['equations'], true) ?: [];
        }
        $this->renderWithLayout('physics/simulation_page', array_merge($data, [
            'slug' => $slug,
            'equations' => $data['equations'] ?? [],
            'physics' => $data['physics'] ?? $data['description'] ?? '',
        ]));
    }

    /**
     * View action rendering a comprehensive Topic Hub.
     */
    public function viewTopic(string $slug)
    {
        $cachePath = PROJECT_ROOT . "/public/cache/topic/{$slug}.html";
        $isStale = $this->isHubCacheStale($slug, $cachePath);

        // Auto-sync stale hub manifests (local development only; production syncs atomically via cli_sync.php)
        if (!$this->authService()->isProduction() && ($isStale || $this->service()->isPreviewActive())) {
            $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
            if (file_exists($manifestPath)) {
                $manifestData = json_decode(file_get_contents($manifestPath), true);
                if ($manifestData) {
                    try {
                        $this->service()->syncIndividualTopic($slug, $manifestData);
                    } catch (\Throwable $e) {
                        // Non-fatal when running in offline/db-unavailable fallback mode
                    }
                }
            }
        }

        if (file_exists($cachePath) && !$isStale && !$this->service()->isPreviewActive()) {
            if (!headers_sent()) {
                header('Content-Type: text/html; charset=utf-8');
            }
            $html = file_get_contents($cachePath);
            $nonce = $this->app->get('csp_nonce') ?? '';
            echo $this->injectLayoutDynamicTokens($html, $nonce, false);
            return;
        }

        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $this->service()->loadAllShards();
        $topic = $this->service()->fetchAndPrepare('topics', $slug);
        if (empty($topic)) {
            $this->app->notFound();
            return;
        }

        $content = $this->service()->getPhysicsContent();
        
        // Load math sprites for dynamic inlining on hub card views
        $sprites = [];
        $spritesPath = PROJECT_ROOT . '/app/config/content/math_sprites.svg';
        if (file_exists($spritesPath)) {
            $spritesContent = file_get_contents($spritesPath);
            preg_match_all('/<path\s+id="([^"]+)"\s+d="([^"]+)"\s*\/?>/', $spritesContent, $matches, PREG_SET_ORDER);
            foreach ($matches as $match) {
                $sprites[$match[1]] = $match[2];
            }
        }

        $inlineSvgFunc = function(string $svg) use ($sprites): string {
            if (empty($svg) || empty($sprites)) return $svg;
            return preg_replace_callback('/<use\s+(?:href|xlink:href)="#(math-path-[a-f0-9]+)"([^>]*)\/?>/i', function($m) use ($sprites) {
                $id = $m[1];
                $attrs = $m[2];
                $d = $sprites[$id] ?? '';
                if ($d) {
                    return '<path id="' . $id . '" d="' . $d . '"' . $attrs . ' />';
                }
                return $m[0];
            }, $svg);
        };

        $wrapVariableTriggers = function(string $html): string {
            if (empty($html)) return $html;
            return preg_replace_callback('/<svg\s+[^>]*data-tex="([^"]+)"[^>]*>.*?<\/svg>/is', function($match) {
                $fullSvg = $match[0];
                $rawTex = $match[1];
                while (strpos($rawTex, '&') !== false) {
                    $prev = $rawTex;
                    $rawTex = html_entity_decode($rawTex, ENT_QUOTES | ENT_HTML5, 'UTF-8');
                    if ($rawTex === $prev) break;
                }
                $tex = trim($rawTex);

                // Reject any math string > 15 chars or containing operators / punctuation / subscripts
                if (strlen($tex) > 15 || strpbrk($tex, "=+-*/^()[]<>:;!,.&~`\"'") !== false) {
                    return $fullSvg;
                }

                // Check allowed TeX macros
                if (preg_match('/\\\\[a-zA-Z]+/i', $tex, $m)) {
                    $cmd = strtolower($m[0]);
                    $allowed = ['\\mathbf', '\\vec', '\\hat', '\\bar', '\\dot', '\\ddot', '\\tilde', '\\mathcal'];
                    if (!in_array($cmd, $allowed)) {
                        return $fullSvg;
                    }
                }

                // Strictly anchored regex matching standalone single-letter variables (e.g. "E", "\mathbf{E}", "q", "\hat{p}")
                if (preg_match('/^\s*(?:\\\\(?:mathbf|vec|hat|mathcal|bar|dot|ddot|tilde))?\\{?([a-zA-Z])\\}?\s*$/i', $tex, $symbolMatch)) {
                    $symbol = $symbolMatch[1];
                    return '<span class="variable-hover-trigger" data-symbol="' . htmlspecialchars($symbol) . '" data-tex="' . htmlspecialchars($match[1]) . '">' . $fullSvg . '</span>';
                }
                return $fullSvg;
            }, $html);
        };

        // Fetch overview subtopic first paragraph for high-signal intro
        $overviewSlug = $slug . '-overview';
        $overviewSub = $this->service()->fetchAndPrepare('subtopics', $overviewSlug);
        $firstParagraph = null;
        if (!empty($overviewSub) && !empty($overviewSub['content'])) {
            if (preg_match('/<p>(.*?)<\/p>/is', $overviewSub['content'], $pMatches)) {
                $firstParagraph = $this->getFirstSentences($pMatches[1], 3);
            }
        }
        $intro = $firstParagraph ?? ($topic['intro'] ?? null);
        $intro = $wrapVariableTriggers($inlineSvgFunc($intro ?? ''));

        // Decode pillars early so we only compile SVG/variable triggers for subtopics in this Topic Hub
        $pillars = !empty($topic['pillars']) ? (is_string($topic['pillars']) ? json_decode($topic['pillars'], true) : $topic['pillars']) : null;
        $targetSlugs = [];
        if (is_array($pillars)) {
            foreach ($pillars as $p) {
                if (!empty($p['slugs']) && is_array($p['slugs'])) {
                    foreach ($p['slugs'] as $s) {
                        $targetSlugs[$s] = true;
                    }
                }
            }
        }

        // Construct subtopics lookup map for subtopic card details
        $subtopicsMap = [];
        if (!empty($targetSlugs)) {
            foreach ($targetSlugs as $subSlug => $_) {
                $sub = $content['subtopics'][$subSlug] ?? null;
                if (!is_array($sub)) continue;
                $subtopicsMap[$subSlug] = [
                    'title' => $sub['title'] ?? $subSlug,
                    'snippet' => $sub['snippet'] ?? '',
                    'snippet_svg' => $wrapVariableTriggers($inlineSvgFunc($sub['snippet_svg'] ?? '')),
                    'hero_math' => $inlineSvgFunc($sub['hero_math'] ?? '')
                ];
            }
        } else {
            foreach ($content['subtopics'] as $subSlug => $sub) {
                if (!is_array($sub)) continue;
                $subtopicsMap[$subSlug] = [
                    'title' => $sub['title'] ?? $subSlug,
                    'snippet' => $sub['snippet'] ?? '',
                    'snippet_svg' => $wrapVariableTriggers($inlineSvgFunc($sub['snippet_svg'] ?? '')),
                    'hero_math' => $inlineSvgFunc($sub['hero_math'] ?? '')
                ];
            }
        }

        // Map cross-pillar bridge links
        $resolvedBridges = [];
        $topicBridges = !empty($topic['bridges']) ? (is_string($topic['bridges']) ? json_decode($topic['bridges'], true) : $topic['bridges']) : [];
        foreach ($topicBridges as $bridgeKey => $desc) {
            if (isset($content['topics'][$bridgeKey])) {
                $resolvedBridges[] = [
                    'title' => $content['topics'][$bridgeKey]['title'],
                    'slug' => $bridgeKey,
                    'description' => $desc
                ];
            } else {
                $resolvedBridges[] = [
                    'title' => $bridgeKey,
                    'slug' => null,
                    'description' => $desc
                ];
            }
        }

        // Build topic variable metadata dictionary using unified VariableAggregator scoped to topic subtopics
        $fetchSubtopicFunc = function(string $sSlug) {
            return $this->service()->fetchAndPrepare('subtopics', $sSlug);
        };
        $topicVariableMap = \App\Logic\VariableAggregator::buildTopicVariables($slug, $topic, $content['subtopics'] ?? [], $fetchSubtopicFunc);

        $this->renderWithLayout('physics/topic', array_merge($topic, [
            'topic' => $topic,
            'subtopics_map' => $subtopicsMap,
            'pillars' => $pillars,
            'bridges' => $resolvedBridges,
            'intro' => $intro,
            'field' => $topic['field'] ?? null,
            'density' => $topic['density'] ?? null,
            'topicVariableMap' => $topicVariableMap,
            'slug' => $slug,
            'extra_css' => ['topic_constellation.css']
        ]), $cachePath);
    }

    /**
     * View action rendering a highly dense Platinum mathematical subtopic.
     */
    public function viewSubtopic(string $slug)
    {
        // 1. Canonical alias redirects
        if ($slug === 'maxwell-equations') {
            \Flight::redirect('/physics/subtopic/maxwells-equations', 301);
            return;
        }

        $cachePath = PROJECT_ROOT . "/public/cache/subtopic/{$slug}.html";
        $isStale = $this->isCacheStale($slug, $cachePath);

        if (file_exists($cachePath) && !$isStale && !$this->service()->isPreviewActive()) {
            if (!headers_sent()) {
                header('Content-Type: text/html; charset=utf-8');
            }
            $html = file_get_contents($cachePath);
            $nonce = $this->app->get('csp_nonce') ?? '';
            echo $this->injectLayoutDynamicTokens($html, $nonce, false);
            return;
        }

        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $subtopic = $this->service()->fetchAndPrepare('subtopics', $slug);
        if (empty($subtopic) || empty($subtopic['title'])) {
            // Check if slug is a notation/symbol reference
            $notation = $this->service()->getNotation();
            if (isset($notation[$slug])) {
                \Flight::redirect('/physics/symbols#' . $slug, 302);
                return;
            }
            $this->app->notFound();
            return;
        }

        $parents = !empty($subtopic['parents']) ? (is_string($subtopic['parents']) ? (json_decode($subtopic['parents'], true) ?: []) : (array)$subtopic['parents']) : [];
        $breadcrumbs = $this->service()->resolveBreadcrumbs($parents);
        $related = $this->service()->getRelatedTopics($slug);
        $subtopicVariables = \App\Logic\VariableAggregator::buildSubtopicVariables($subtopic);

        require_once __DIR__ . '/../logic/LabToolsLauncher.php';
        $firstParent = !empty($parents) ? (is_array($parents) ? reset($parents) : (string)$parents) : '';
        $labLauncher = \App\Logic\LabToolsLauncher::resolve($slug, $firstParent);

        $this->renderWithLayout('physics/subtopic', array_merge($subtopic, [
            'parents' => $parents,
            'breadcrumbs' => $breadcrumbs,
            'related_topics' => $related,
            'title' => $subtopic['title'],
            'content' => $subtopic['content'],
            'equations' => $subtopic['equations'] ?? [],
            'breakdowns' => $subtopic['breakdowns'] ?? [],
            'formulas' => $subtopic['formulas'] ?? [],
            'subtopicVariables' => $subtopicVariables,
            'labLauncher' => $labLauncher
        ]), $cachePath);
    }

    /**
     * Render action embedding pages into standard HTML bootstrap templates.
     */
    public function renderWithLayout(string $view, array $data = [], ?string $cachePath = null): void
    {
        $isStudio = $this->authService()->isLocalDevStudio();
        $isPreview = $this->service()->isPreviewActive();
        $isBuildMode = $isStudio && ($this->app->request()->query->build_mode === '1');

        if ($isPreview) {
            $this->service()->loadAllShards();
            $content = $this->service()->getPhysicsContent();
            
            $topicsList = array_map(function($s, $t) {
                $isDraft = ($t['status'] ?? '') === 'draft';
                $title = $isDraft ? '<span class="draft-badge">DRAFT</span> ' . $t['title'] : $t['title'];
                return ['slug' => $s, 'title' => $title];
            }, array_keys($content['topics']), $content['topics']);
            
            $simsList = array_map(function($s, $t) {
                $isDraft = ($t['status'] ?? '') === 'draft';
                $title = $isDraft ? '<span class="draft-badge">DRAFT</span> ' . $t['title'] : $t['title'];
                return ['slug' => $s, 'title' => $title];
            }, array_keys($content['simulations']), $content['simulations']);
        } else {
            try {
                $topicsList = $this->app->db()->fetchAll("SELECT slug, title FROM topics ORDER BY id ASC");
                $simsList = $this->app->db()->fetchAll("SELECT slug, title FROM simulations ORDER BY id ASC");
            } catch (\Throwable $e) {
                $this->service()->loadAllShards();
                $content = $this->service()->getPhysicsContent();
                $topicsList = array_map(function($s, $t) {
                    return ['slug' => $s, 'title' => $t['title'] ?? $s];
                }, array_keys($content['topics'] ?? []), $content['topics'] ?? []);
                $simsList = array_map(function($s, $t) {
                    return ['slug' => $s, 'title' => $t['title'] ?? $s];
                }, array_keys($content['simulations'] ?? []), $content['simulations'] ?? []);
            }
        }

        $menuTopics = [];
        foreach ($topicsList as $topic) {
            $menuTopics[$topic['slug']] = ['title' => $topic['title']];
        }

        $menuSimulations = [];
        foreach ($simsList as $sim) {
            $menuSimulations[$sim['slug']] = ['title' => $sim['title']];
        }

        $nonce = $this->app->get('csp_nonce') ?? '';
        $viewData = array_merge($data, ['nonce' => $nonce]);
        $bodyContent = $this->app->view()->fetch($view, $viewData) ?: '';

        if ($isPreview && !$isBuildMode) {
            $bodyContent .= '
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
                    <a href="/physics/sync" class="btn btn-primary" style="box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 50px; padding: 12px 24px; text-decoration: none; display: flex; align-items: center; gap: 8px; background-color: #007bff; color: white; border: none; font-family: sans-serif;">
                        <span>🔄</span> <strong>Sync Now</strong>
                    </a>
                </div>';
        }

        $html = $this->app->view()->fetch('physics/layout', array_merge($viewData, [
            'body_content' => $bodyContent,
            'is_preview' => $isPreview && !$isBuildMode,
            'nonce' => $nonce,
            'menu_topics' => $menuTopics,
            'menu_simulations' => $menuSimulations,
        ])) ?: '';

        if ($cachePath && !$isPreview && !$isBuildMode) {
            $dir = dirname($cachePath);
            if (!is_dir($dir)) {
                @mkdir($dir, 0775, true);
            }
            file_put_contents($cachePath, $html, LOCK_EX);
        }

        echo $this->injectLayoutDynamicTokens($html, $nonce, $isPreview && !$isBuildMode);
    }

    /**
     * Injects per-request CSP nonces and the local development studio Admin menu
     * without baking privileged markup into static disk cache files.
     */
    private function injectLayoutDynamicTokens(string $html, string $nonce, bool $isPreview): string
    {
        if ($nonce !== '') {
            $html = preg_replace('/nonce=["\']([a-f0-9]{32})["\']/', 'nonce="' . $nonce . '"', $html);
        }

        $auth = Flight::authService();
        $isDevStudio = $auth && method_exists($auth, 'isLocalDevStudio') && $auth->isLocalDevStudio();

        if (!$isDevStudio) {
            return str_replace('<!-- DEV_STUDIO_NAV_SLOT -->', '', $html);
        }

        $user = $auth->getCurrentUser();
        $currentRole = htmlspecialchars($user->role ?? 'admin');
        $previewToggleUrl = $isPreview ? '?preview=0' : '?preview=1';
        $previewBadge = $isPreview
            ? '<span class="admin-status-pill active">ON</span>'
            : '<span class="admin-status-pill">OFF</span>';

        $roles = ['admin' => 'Admin', 'curator' => 'Curator', 'contributor' => 'Contrib', 'guest' => 'Guest'];
        $roleButtonsHtml = '';
        foreach ($roles as $rKey => $rLabel) {
            $activeClass = ($currentRole === $rKey) ? ' active' : '';
            $roleButtonsHtml .= '<button type="button" class="dev-role-pill' . $activeClass . '" data-dev-role="' . $rKey . '">' . $rLabel . '</button>';
        }

        $reqUrl = parse_url($this->app->request()->url ?? '', PHP_URL_PATH) ?: '';
        $isAdminActive = (bool)preg_match('#^/physics/admin(?:/|$)#', $reqUrl);

        $adminMenuHtml = '
            <div class="dropdown nav-admin-dropdown" id="dev-studio-admin-nav" data-nav-pillar="admin">
                <a href="/physics/admin/assess" class="dropbtn btn btn-admin-studio' . ($isAdminActive ? ' nav-pillar-active' : '') . '" title="Local Developer Studio Controls">
                    🛠️ Admin <span class="nav-caret">&blacktriangledown;</span>
                </a>
                <div class="dropdown-content dropdown-admin-studio">
                    <div class="mega-section-label">Developer Studio Controls</div>
                    <a href="/physics/admin/assess" class="nav-module-link admin-featured-link' . ($isAdminActive ? ' is-current' : '') . '">
                        <span class="module-title">🪐 Assessment &amp; Health Console</span>
                        <span class="module-desc">Live telemetry, ratchets, shard audits &amp; self-healing</span>
                    </a>
                    <a href="/physics/sync" class="nav-module-link">
                        <span class="module-title">🔄 Sync Shards to MariaDB</span>
                        <span class="module-desc">Synchronize Git JSON shards &amp; search index</span>
                    </a>
                    <a href="' . $previewToggleUrl . '" class="nav-module-link">
                        <span class="module-title" style="display:flex; align-items:center; justify-content:space-between;">
                            <span>👁️ Shard Preview Mode</span>
                            ' . $previewBadge . '
                        </span>
                        <span class="module-desc">Toggle live MariaDB vs. offline Git JSON shards</span>
                    </a>
                    <div class="admin-role-switcher-box">
                        <div class="role-switcher-header">
                            <span>🎭 Active Studio Role</span>
                            <code id="dev-current-role-badge">' . strtoupper($currentRole) . '</code>
                        </div>
                        <div class="dev-role-pills-row">
                            ' . $roleButtonsHtml . '
                        </div>
                    </div>
                </div>
            </div>';

        return str_replace('<!-- DEV_STUDIO_NAV_SLOT -->', $adminMenuHtml, $html);
    }

    /**
     * Homepage view action.
     */
    public function index()
    {
        $topics = $this->service()->fetchAllData('topics');
        foreach ($topics as &$topic) {
            $cleanContent = trim(strip_tags($topic['content'] ?? $topic['intro'] ?? ''));
            $sentences = preg_split('/(?<=[.!?])\s+/', $cleanContent, 2);
            $firstSentence = $sentences[0] ?? $cleanContent;
            $topic['description'] = mb_strimwidth($firstSentence, 0, 195, "...");
        }

        $this->renderWithLayout('physics/home', [
            'title' => 'The Physics Lab',
            'subtitle' => 'Explore the fundamental laws of the universe through interactive simulations and detailed explanations.',
            'topics' => $topics
        ]);
    }

    private function isHubCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;
        $cacheMtime = filemtime($cachePath);

        $layoutPath = PROJECT_ROOT . '/app/views/physics/layout.php';
        if (file_exists($layoutPath) && filemtime($layoutPath) > $cacheMtime) {
            return true;
        }

        $viewPath = PROJECT_ROOT . '/app/views/physics/topic.php';
        if (file_exists($viewPath) && filemtime($viewPath) > $cacheMtime) {
            return true;
        }

        $hubAssets = [
            PROJECT_ROOT . '/public/css/physics.css',
            PROJECT_ROOT . '/public/css/topic_constellation.css',
            PROJECT_ROOT . '/public/js/topic_constellation.js',
        ];
        foreach ($hubAssets as $assetPath) {
            if (file_exists($assetPath) && filemtime($assetPath) > $cacheMtime) {
                return true;
            }
        }

        $aggregatorPath = PROJECT_ROOT . '/app/logic/VariableAggregator.php';
        if (file_exists($aggregatorPath) && filemtime($aggregatorPath) > $cacheMtime) {
            return true;
        }

        $registryPath = PROJECT_ROOT . '/app/config/variable_registry.json';
        if (file_exists($registryPath) && filemtime($registryPath) > $cacheMtime) {
            return true;
        }

        $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
        if (!file_exists($manifestPath)) return false;
        return filemtime($manifestPath) > $cacheMtime;
    }

    private function isCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;
        $cacheMtime = filemtime($cachePath);

        $layoutPath = PROJECT_ROOT . '/app/views/physics/layout.php';
        if (file_exists($layoutPath) && filemtime($layoutPath) > $cacheMtime) {
            return true;
        }

        $aggregatorPath = PROJECT_ROOT . '/app/logic/VariableAggregator.php';
        if (file_exists($aggregatorPath) && filemtime($aggregatorPath) > $cacheMtime) {
            return true;
        }

        $launcherPath = PROJECT_ROOT . '/app/logic/LabToolsLauncher.php';
        if (file_exists($launcherPath) && filemtime($launcherPath) > $cacheMtime) {
            return true;
        }

        $subtopicViewPath = PROJECT_ROOT . '/app/views/physics/subtopic.php';
        if (file_exists($subtopicViewPath) && filemtime($subtopicViewPath) > $cacheMtime) {
            return true;
        }

        $content = $this->service()->getPhysicsContent($slug);
        $shardFile = $content['search_index'][$slug]['s'] ?? null;
        if (!$shardFile) return false;

        $shardPath = PROJECT_ROOT . '/app/config/content/' . $shardFile;
        if (!file_exists($shardPath)) return false;

        return filemtime($shardPath) > $cacheMtime;
    }

    private function getFirstSentences(string $html, int $count = 3): string
    {
        $len = strlen($html);
        $inTag = false;
        $sentenceCount = 0;
        $endPos = $len;
        
        for ($i = 0; $i < $len; $i++) {
            $char = $html[$i];
            if ($char === '<') {
                $inTag = true;
            } elseif ($char === '>') {
                $inTag = false;
            } elseif (!$inTag) {
                if (in_array($char, ['.', '!', '?'])) {
                    $prevChar = ($i > 0) ? $html[$i-1] : '';
                    $nextChar = ($i < $len - 1) ? $html[$i+1] : '';
                    
                    if (is_numeric($prevChar) || is_numeric($nextChar)) {
                        continue;
                    }
                    
                    if ($i >= 3) {
                        $last3 = substr($html, $i-3, 3);
                        if ($last3 === 'QED' || $last3 === 'e.g' || $last3 === 'i.e') {
                            continue;
                        }
                    }
                    
                    if ($nextChar === '' || ctype_space($nextChar) || $nextChar === '<') {
                        $sentenceCount++;
                        if ($sentenceCount === $count) {
                            $endPos = $i + 1;
                            break;
                        }
                    }
                }
            }
        }
        
        if ($endPos < $len) {
            return rtrim(substr($html, 0, $endPos)) . ' ...';
        }
        return $html;
    }

    /**
     * Pre-renders Topic Hub and Subtopic HTML cache files in-process without requiring
     * a running local HTTP server or curl subprocesses. Preserves 32-char CSP nonce
     * placeholders and <!-- DEV_STUDIO_NAV_SLOT --> markers for dynamic per-request injection.
     *
     * @param bool        $force      Rebuild even when existing cache file is fresh
     * @param array|null  $onlySlugs  Optional allowlist of slugs to warm (for targeted runs/tests)
     * @param callable|null $onProgress Optional callback(int $done, int $total, string $slug, string $status)
     */
    public function warmHtmlCache(bool $force = false, ?array $onlySlugs = null, ?callable $onProgress = null): array
    {
        $svc = $this->service();
        $wasPreview = $svc->isPreviewActive();

        $prevGetPreview = $_GET['preview'] ?? null;
        $prevGetBuild = $_GET['build_mode'] ?? null;
        $prevCookiePreview = $_COOKIE['physics_preview'] ?? null;
        $prevAppReqUrl = $this->app->request()->url ?? '';
        $prevFlightReqUrl = \Flight::request()->url ?? '';

        // Guarantee a valid 32-hex-char nonce placeholder so injectLayoutDynamicTokens() always matches on cache hit
        $currentNonce = (string)($this->app->get('csp_nonce') ?? '');
        if (!preg_match('/^[a-f0-9]{32}$/', $currentNonce)) {
            $this->app->set('csp_nonce', bin2hex(random_bytes(16)));
        }

        // Guarantee Flight view path is configured even in standalone CLI/test Engine instances
        if (!$this->app->get('flight.views.path')) {
            $this->app->set('flight.views.path', PROJECT_ROOT . '/app/views');
        }

        $hubsBuilt = 0;
        $hubsSkipped = 0;
        $subtopicsBuilt = 0;
        $subtopicsSkipped = 0;
        $errors = [];

        try {
            unset($_GET['preview'], $_GET['build_mode'], $_COOKIE['physics_preview']);
            $svc->setPreviewMode(false);

            $svc->loadAllShards();
            $content = $svc->getPhysicsContent();

            $hubSlugs = array_keys($content['topics'] ?? []);
            $subSlugs = array_keys($content['subtopics'] ?? []);

            if ($onlySlugs !== null) {
                $allow = array_flip($onlySlugs);
                $hubSlugs = array_values(array_filter($hubSlugs, fn($s) => isset($allow[$s])));
                $subSlugs = array_values(array_filter($subSlugs, fn($s) => isset($allow[$s])));
            }

            $total = count($hubSlugs) + count($subSlugs);
            $done = 0;

            foreach ($hubSlugs as $slug) {
                $done++;
                $cachePath = PROJECT_ROOT . "/public/cache/topic/{$slug}.html";
                if ($force && file_exists($cachePath)) {
                    @unlink($cachePath);
                }
                if (!$force && file_exists($cachePath) && !$this->isHubCacheStale($slug, $cachePath)) {
                    $hubsSkipped++;
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'skipped');
                    }
                    continue;
                }

                ob_start();
                try {
                    $targetUrl = "/physics/topic/{$slug}";
                    $this->app->request()->url = $targetUrl;
                    \Flight::request()->url = $targetUrl;
                    $this->viewTopic($slug);
                } catch (\Throwable $e) {
                    $errors[] = "topic/{$slug}: " . $e->getMessage();
                } finally {
                    ob_end_clean();
                }

                if (file_exists($cachePath) && filesize($cachePath) > 0) {
                    $hubsBuilt++;
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'built');
                    }
                } else {
                    $errors[] = "topic/{$slug}: cache file was not written";
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'error');
                    }
                }
            }

            foreach ($subSlugs as $slug) {
                $done++;
                if ($slug === 'maxwell-equations') {
                    $subtopicsSkipped++;
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'skipped');
                    }
                    continue;
                }

                $cachePath = PROJECT_ROOT . "/public/cache/subtopic/{$slug}.html";
                if ($force && file_exists($cachePath)) {
                    @unlink($cachePath);
                }
                if (!$force && file_exists($cachePath) && !$this->isCacheStale($slug, $cachePath)) {
                    $subtopicsSkipped++;
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'skipped');
                    }
                    continue;
                }

                ob_start();
                try {
                    $targetUrl = "/physics/subtopic/{$slug}";
                    $this->app->request()->url = $targetUrl;
                    \Flight::request()->url = $targetUrl;
                    $this->viewSubtopic($slug);
                } catch (\Throwable $e) {
                    $errors[] = "subtopic/{$slug}: " . $e->getMessage();
                } finally {
                    ob_end_clean();
                }

                if (file_exists($cachePath) && filesize($cachePath) > 0) {
                    $subtopicsBuilt++;
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'built');
                    }
                } else {
                    $errors[] = "subtopic/{$slug}: cache file was not written";
                    if ($onProgress) {
                        $onProgress($done, $total, $slug, 'error');
                    }
                }
            }
        } finally {
            $svc->setPreviewMode($wasPreview);
            $this->app->request()->url = $prevAppReqUrl;
            \Flight::request()->url = $prevFlightReqUrl;
            if ($prevGetPreview !== null) {
                $_GET['preview'] = $prevGetPreview;
            }
            if ($prevGetBuild !== null) {
                $_GET['build_mode'] = $prevGetBuild;
            }
            if ($prevCookiePreview !== null) {
                $_COOKIE['physics_preview'] = $prevCookiePreview;
            }
        }

        return [
            'hubs_built' => $hubsBuilt,
            'hubs_skipped' => $hubsSkipped,
            'subtopics_built' => $subtopicsBuilt,
            'subtopics_skipped' => $subtopicsSkipped,
            'errors' => $errors,
        ];
    }

    /**
     * Backward-compatible delegation to AdminController and ReviewController.
     */
    public function __call(string $name, array $arguments)
    {
        $admin = $this->app->adminController();
        if (method_exists($admin, $name)) {
            return $admin->$name(...$arguments);
        }

        $review = $this->app->reviewController();
        if (method_exists($review, $name)) {
            return $review->$name(...$arguments);
        }

        throw new \BadMethodCallException("Undefined method PhysicsController::{$name}()");
    }
}


