<?php

namespace app\controllers;

use flight\Engine;
use Flight;

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
     * Public database index synchronization endpoint.
     */
    public function sync(): void
    {
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
        $content = $this->service()->getPhysicsContent();
        $notation = $content['notation'] ?? [];
        
        // Filter notation where type is 'constant'
        $constants = array_filter($notation, function($item) {
            return ($item['type'] ?? '') === 'constant';
        });
        
        // Fallback to legacy constants if notation is empty
        if (empty($constants)) {
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
        $notation = $content['notation'] ?? [];
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
            'title' => 'Lab Tools Hub'
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
            'currentUser' => $currentUser
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

        $jsonPayload = json_encode($casPayload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);

        $cmd = escapeshellcmd($pythonBin) . ' ' . escapeshellarg($casScript) . ' ' . escapeshellarg($jsonPayload);
        $output = shell_exec($cmd);

        if ($output === null) {
            echo json_encode(['success' => false, 'error' => 'Failed to execute symbolic CAS engine.']);
            return;
        }

        $result = json_decode($output, true);
        if (!$result) {
            echo json_encode(['success' => false, 'error' => 'Invalid response from CAS engine.', 'raw_output' => $output]);
            return;
        }

        echo json_encode($result);
    }

    /**
     * REST Action to define an unregistered LaTeX formula via Gemini AI and save to database.
     */
    public function apiDefineFormula()
    {
        header('Content-Type: application/json; charset=utf-8');
        set_time_limit(120);

        // Security check for production environments
        $appEnv = getenv('APP_ENV') ?: 'development';
        if ($appEnv === 'production') {
            $adminKeyHeader = $_SERVER['HTTP_X_TERRA_ADMIN_KEY'] ?? '';
            $expectedKey = getenv('TERRA_ADMIN_KEY') ?: 'terra_admin_secret_key_123';
            if ($adminKeyHeader !== $expectedKey) {
                http_response_code(403);
                echo json_encode(['success' => false, 'error' => '403 Forbidden: Invalid Security Token']);
                return;
            }
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
            echo json_encode([
                'success' => false,
                'error' => $e->getMessage(),
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
            echo json_encode([
                'success' => false,
                'error' => $e->getMessage(),
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
            echo json_encode([
                'success' => false,
                'error' => $e->getMessage()
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
            echo json_encode([
                'success' => false,
                'error' => $e->getMessage()
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
        if (!$data) {
            $this->app->notFound();
            return;
        }
        $this->renderWithLayout('physics/simulation_page', array_merge($data, [
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

        // Auto-sync stale hub manifests
        if ($isStale || $this->service()->isPreviewActive()) {
            $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
            if (file_exists($manifestPath)) {
                $manifestData = json_decode(file_get_contents($manifestPath), true);
                if ($manifestData) {
                    $this->service()->syncIndividualTopic($slug, $manifestData);
                }
            }
        }

        if (file_exists($cachePath) && !$isStale && !$this->service()->isPreviewActive()) {
            header('Content-Type: text/html; charset=utf-8');
            $html = file_get_contents($cachePath);
            $nonce = $this->app->get('csp_nonce');
            if ($nonce) {
                $html = preg_replace('/nonce=["\']([a-f0-9]{32})["\']/', 'nonce="' . $nonce . '"', $html);
            }
            echo $html;
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

        // Construct subtopics lookup map for subtopic card details
        $subtopicsMap = [];
        foreach ($content['subtopics'] as $subSlug => $sub) {
            if (!is_array($sub)) continue;
            $subtopicsMap[$subSlug] = [
                'title' => $sub['title'] ?? $subSlug,
                'snippet' => $sub['snippet'] ?? '',
                'snippet_svg' => $wrapVariableTriggers($inlineSvgFunc($sub['snippet_svg'] ?? '')),
                'hero_math' => $inlineSvgFunc($sub['hero_math'] ?? '')
            ];
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
            'pillars' => !empty($topic['pillars']) ? (is_string($topic['pillars']) ? json_decode($topic['pillars'], true) : $topic['pillars']) : null,
            'bridges' => $resolvedBridges,
            'intro' => $intro,
            'field' => $topic['field'] ?? null,
            'density' => $topic['density'] ?? null,
            'topicVariableMap' => $topicVariableMap,
            'slug' => $slug
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
            header('Content-Type: text/html; charset=utf-8');
            $html = file_get_contents($cachePath);
            $nonce = $this->app->get('csp_nonce');
            if ($nonce) {
                $html = preg_replace('/nonce=["\']([a-f0-9]{32})["\']/', 'nonce="' . $nonce . '"', $html);
            }
            echo $html;
            return;
        }

        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $subtopic = $this->service()->fetchAndPrepare('subtopics', $slug);
        if (empty($subtopic) || empty($subtopic['title'])) {
            // Check if slug is a notation/symbol reference
            $content = $this->service()->getPhysicsContent();
            if (isset($content['notation'][$slug])) {
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
    protected function renderWithLayout(string $view, array $data = [], ?string $cachePath = null): void
    {
        $isPreview = $this->service()->isPreviewActive();
        $isBuildMode = ($this->app->request()->query->build_mode === '1');

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
            if (!file_exists($dir)) {
                mkdir($dir, 0777, true);
            }
            file_put_contents($cachePath, $html);
        }

        echo $html;
    }

    /**
     * Homepage view action.
     */
    public function index()
    {
        $topics = $this->service()->fetchAllData('topics');
        foreach ($topics as &$topic) {
            $cleanContent = strip_tags($topic['content'] ?? $topic['intro'] ?? '');
            $topic['description'] = mb_strimwidth($cleanContent, 0, 120, "...");
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

        $viewPath = PROJECT_ROOT . '/app/views/physics/topic.php';
        if (file_exists($viewPath) && filemtime($viewPath) > $cacheMtime) {
            return true;
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
     * View action rendering the Unified Platform Assessment & Health Cockpit.
     */
    public function adminAssess()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('HTTP/1.1 403 Forbidden');
            echo 'Forbidden: Admin access restricted to localhost.';
            exit;
        }

        // Read latest telemetry (Schema v1.0)
        $latestPath = PROJECT_ROOT . '/docs/reports/latest.json';
        $latest = [];
        if (file_exists($latestPath)) {
            $latest = json_decode(file_get_contents($latestPath), true) ?: [];
        }

        // Read timeline entries (recent runs)
        $timelinePath = PROJECT_ROOT . '/docs/reports/timeline.jsonl';
        $timeline = [];
        if (file_exists($timelinePath)) {
            $lines = file($timelinePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [];
            $recentLines = array_slice($lines, -25);
            foreach ($recentLines as $line) {
                $decoded = json_decode($line, true);
                if ($decoded) {
                    $timeline[] = $decoded;
                }
            }
        }

        // Load topics for domain selector
        $topics = $this->service()->fetchAllData('topics');

        $this->renderWithLayout('physics/admin/assess', [
            'title' => 'Platform Assessment Console',
            'latest' => $latest,
            'timeline' => $timeline,
            'topics' => $topics
        ]);
    }

    /**
     * Backward-compatible alias for adminDashboard
     */
    public function adminDashboard()
    {
        return $this->adminAssess();
    }

    /**
     * REST Endpoint: Fetch live telemetry and historical timeline
     */
    public function apiAssessTelemetry()
    {
        $latestPath = PROJECT_ROOT . '/docs/reports/latest.json';
        $latest = file_exists($latestPath) ? (json_decode(file_get_contents($latestPath), true) ?: []) : [];

        $timelinePath = PROJECT_ROOT . '/docs/reports/timeline.jsonl';
        $timeline = [];
        if (file_exists($timelinePath)) {
            $lines = file($timelinePath, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES) ?: [];
            $recentLines = array_slice($lines, -30);
            foreach ($recentLines as $line) {
                $decoded = json_decode($line, true);
                if ($decoded) {
                    $timeline[] = $decoded;
                }
            }
        }

        header('Content-Type: application/json');
        echo json_encode([
            'success' => true,
            'telemetry' => $latest,
            'timeline' => $timeline
        ]);
        exit;
    }

    /**
     * REST Endpoint: Trigger assessment runs (quick, heal, changed, domain, shard, full)
     */
    public function apiRunAssess()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true) ?: [];
        $action = $input['action'] ?? 'quick';
        $domain = trim($input['domain'] ?? '');
        $shard = trim($input['shard'] ?? '');

        $flags = [];

        switch ($action) {
            case 'heal':
                $flags[] = '--heal';
                $flags[] = '--quick';
                break;
            case 'changed':
                $flags[] = '--changed';
                break;
            case 'integrity':
                $flags[] = '--integrity';
                break;
            case 'diff':
                $flags[] = '--diff';
                $flags[] = '--quick';
                break;
            case 'domain':
                if (!empty($domain)) {
                    $flags[] = '--domain ' . escapeshellarg($domain);
                } else {
                    $flags[] = '--quick';
                }
                break;
            case 'shard':
                if (!empty($shard)) {
                    $flags[] = '--shard ' . escapeshellarg($shard);
                } else {
                    $flags[] = '--quick';
                }
                break;
            case 'full':
                $flags[] = '--all';
                break;
            case 'quick':
            default:
                $flags[] = '--quick';
                break;
        }

        $flagString = implode(' ', $flags);
        $cmd = "cd " . escapeshellarg(PROJECT_ROOT) . " && bash scripts/assess " . $flagString . " 2>&1";

        exec($cmd, $output, $returnCode);

        // Fetch fresh latest.json
        $latestPath = PROJECT_ROOT . '/docs/reports/latest.json';
        $latest = file_exists($latestPath) ? (json_decode(file_get_contents($latestPath), true) ?: []) : [];

        header('Content-Type: application/json');
        echo json_encode([
            'success' => ($returnCode === 0),
            'return_code' => $returnCode,
            'action' => $action,
            'command' => "scripts/assess " . $flagString,
            'logs' => implode("\n", $output),
            'telemetry' => $latest
        ]);
        exit;
    }

    /**
     * REST Endpoint: Fetch diff comparison against baseline
     */
    public function apiAssessDiff()
    {
        $cmd = "cd " . escapeshellarg(PROJECT_ROOT) . " && bash scripts/assess --diff --quick 2>&1";
        exec($cmd, $output, $returnCode);

        header('Content-Type: application/json');
        echo json_encode([
            'success' => ($returnCode === 0),
            'logs' => implode("\n", $output)
        ]);
        exit;
    }

    /**
     * Deprecated: Redirects legacy WYSIWYG editor requests to the canonical Assessment Console.
     */
    public function wysiwygEditor()
    {
        $this->app->redirect('/physics/admin/assess', 301);
    }

    /**
     * Deprecated: Redirects legacy Critic portal requests to the canonical Assessment Console.
     */
    public function criticPortal()
    {
        $this->app->redirect('/physics/admin/assess', 301);
    }

    /**
     * REST Endpoint: Run the Auto-Linker
     */
    public function apiRunAutoLinker()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        // Run auto_linker script
        $cmd = "cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/auto_linker.py 2>&1";
        exec($cmd, $output, $return_var);

        // Regenerate system health snapshot
        exec("cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/generate_system_health.py > /dev/null 2>&1");

        header('Content-Type: application/json');
        echo json_encode([
            'success' => ($return_var === 0),
            'logs' => implode("\n", $output)
        ]);
        exit;
    }

    /**
     * REST Endpoint: Run Consensus Critic on a slug
     */
    public function apiRunCritic()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $slug = $input['slug'] ?? '';
        $writeCitations = $input['write_citations'] ?? false;

        $slugFlag = !empty($slug) ? " --slug " . escapeshellarg($slug) : "";
        $writeFlag = $writeCitations ? ' --write-citations' : '';
        $cmd = "cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/run_critic.py" . $slugFlag . $writeFlag . " 2>&1";
        exec($cmd, $output, $return_var);

        if ($writeCitations && $return_var === 0) {
            $this->service()->clearCache();
            if (!empty($slug)) {
                $subtopicData = $this->service()->fetchAndPrepare('subtopics', $slug);
                if (!empty($subtopicData)) {
                    $this->service()->syncIndividualSubtopic($slug, $subtopicData);
                }
            } else {
                $this->service()->loadAllShards();
                $this->service()->performSync();
            }
        }

        // Regenerate system health
        exec("cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/generate_system_health.py > /dev/null 2>&1");

        header('Content-Type: application/json');
        echo json_encode([
            'success' => ($return_var === 0),
            'logs' => implode("\n", $output)
        ]);
        exit;
    }

    /**
     * REST Endpoint: Register a new subtopic in semantic_references.json
     */
    public function apiRegisterReference()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $slug = $input['slug'] ?? '';
        $title = $input['title'] ?? '';
        $prose = $input['reference_prose'] ?? '';
        $keywordsInput = $input['keywords'] ?? '';

        if (empty($slug) || empty($title) || empty($prose) || empty($keywordsInput)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'All fields are required.']);
            exit;
        }

        // Parse keywords
        $keywords = array_map('trim', explode(',', $keywordsInput));
        $keywords = array_filter($keywords); // remove empty elements

        $refPath = PROJECT_ROOT . '/app/config/ref_data/semantic_references.json';
        $references = [];
        if (file_exists($refPath)) {
            $references = json_decode(file_get_contents($refPath), true) ?: [];
        }

        // Check if already registered
        if (isset($references[$slug])) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic already registered as reference.']);
            exit;
        }

        // Add the reference
        $references[$slug] = [
            'title' => $title,
            'reference_prose' => $prose,
            'keywords' => array_values($keywords)
        ];

        // Save back to JSON file
        if (file_put_contents($refPath, json_encode($references, JSON_PRETTY_PRINT)) === false) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Failed to write to database file.']);
            exit;
        }

        header('Content-Type: application/json');
        echo json_encode(['success' => true]);
        exit;
    }

    /**
     * REST Endpoint: Update verification citations for a processed subtopic
     */
    public function apiUpdateVerification()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $slug = $input['slug'] ?? '';
        $citations = $input['citations'] ?? [];

        if (empty($slug)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic slug is required.']);
            exit;
        }

        // Get content shard info using PhysicsService helper
        $content = $this->service()->getPhysicsContent($slug);
        $searchIndex = $content['search_index'] ?? [];
        $shardFile = $searchIndex[$slug]['s'] ?? null;
        $baseDir = PROJECT_ROOT . '/app/config/content/';

        if (!$shardFile || !file_exists($baseDir . $shardFile)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Shard file for subtopic not found.']);
            exit;
        }

        // Load the shard file
        $shardData = json_decode(file_get_contents($baseDir . $shardFile), true) ?: [];
        if (!isset($shardData[$slug])) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic not found in content shard.']);
            exit;
        }

        // Keep or create verification block
        $verification = $shardData[$slug]['verification'] ?? [];
        if (empty($verification)) {
            $verification = [
                'verified_date' => date('Y-m-d'),
                'consensus_score' => 1.00,
                'agents' => [
                    'extractor' => 'ManualEditor-v1.0',
                    'critic' => 'ManualEditor-v1.0',
                    'judge' => 'ManualEditor-v1.0'
                ]
            ];
        }

        // Clean & set the citations
        $cleanedCitations = [];
        foreach ($citations as $cit) {
            $authors = $cit['authors'] ?? [];
            if (is_string($authors)) {
                $authors = array_map('trim', explode(',', $authors));
                $authors = array_filter($authors);
            }
            $cleanedCitations[] = [
                'doi' => trim($cit['doi'] ?? ''),
                'title' => trim($cit['title'] ?? ''),
                'authors' => array_values($authors),
                'url' => trim($cit['url'] ?? '')
            ];
        }

        $verification['citations'] = $cleanedCitations;
        $shardData[$slug]['verification'] = $verification;

        // Save back to JSON shard on disk
        if (file_put_contents($baseDir . $shardFile, json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) === false) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Failed to save updated shard back to disk.']);
            exit;
        }

        // Clear service cache and sync to DB
        $this->service()->clearCache();
        $subtopicData = $this->service()->fetchAndPrepare('subtopics', $slug);
        if (!empty($subtopicData)) {
            $this->service()->syncIndividualSubtopic($slug, $subtopicData);
        }

        // Regenerate system health
        exec("cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/generate_system_health.py > /dev/null 2>&1");

        header('Content-Type: application/json');
        echo json_encode(['success' => true]);
        exit;
    }

    /**
     * REST Endpoint: Save draft to batch_payload.json
     */
    public function apiSaveDraft()
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $slug = $input['slug'] ?? '';
        $title = $input['title'] ?? '';
        $content = $input['content'] ?? '';
        $parents = $input['parents'] ?? [];
        $identities = $input['identities'] ?? [];

        if (empty($slug) || empty($content)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Slug and content are required.']);
            exit;
        }

        // Save to payload
        $payloadPath = PROJECT_ROOT . '/subfiles/batch_payload.json';
        $payloads = [];
        if (file_exists($payloadPath)) {
            $payloads = json_decode(file_get_contents($payloadPath), true) ?: [];
        }

        $payloads[$slug] = [
            'title' => $title ?: $slug,
            'content' => $content,
            'standard' => 'platinum',
            'parents' => $parents,
            'identities' => $identities
        ];

        file_put_contents($payloadPath, json_encode($payloads, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

        header('Content-Type: application/json');
        echo json_encode(['success' => true]);
        exit;
    }

    /**
     * REST Endpoint: Fetch subtopic details by slug
     */
    public function apiGetSubtopic($slug)
    {
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        if ($ip !== '127.0.0.1' && $ip !== '::1' && $ip !== 'localhost') {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Forbidden']);
            exit;
        }

        $content = $this->service()->getPhysicsContent($slug);
        $subtopic = $content['subtopics'][$slug] ?? null;

        if (!$subtopic) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic not found']);
            exit;
        }

        // Also resolve the parent category from search index or shard mapping
        $parent = null;
        $searchIndex = $content['search_index'] ?? [];
        if (isset($searchIndex[$slug]['s'])) {
            $parent = str_replace('.json', '', $searchIndex[$slug]['s']);
        }

        // Resolve formulas/identities
        $identities = $subtopic['identities'] ?? [];
        if (empty($identities)) {
            $formulaIds = $subtopic['formula_ids'] ?? [];
            foreach ($formulaIds as $fId) {
                $formula = $this->service()->loadFormula($fId);
                if ($formula) {
                    $latex = '';
                    if (!empty($formula['equation'])) {
                        if (preg_match('/data-tex="([^"]+)"/', $formula['equation'], $matches)) {
                            $latex = html_entity_decode($matches[1], ENT_QUOTES | ENT_HTML5, 'UTF-8');
                        } else {
                            $latex = $formula['equation'];
                        }
                    }
                    // Strip the hex suffix (e.g., -ca9b4fff) to match input raw ID
                    $cleanId = preg_replace('/-[a-f0-9]{8}$/', '', $fId);
                    $identities[] = [
                        'id' => $cleanId,
                        'title' => $formula['title'] ?? '',
                        'equation' => $latex
                    ];
                }
            }
        }

        header('Content-Type: application/json');
        echo json_encode([
            'success' => true,
            'subtopic' => [
                'slug' => $slug,
                'title' => $subtopic['title'] ?? '',
                'content' => $subtopic['content'] ?? '',
                'snippet' => $subtopic['snippet'] ?? '',
                'parents' => $parent ? [$parent] : [],
                'identities' => $identities
            ]
        ]);
        exit;
    }

    /**
     * REST Endpoint: Get Current Authenticated User & Role
     */
    public function apiGetCurrentUser()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        header('Content-Type: application/json');
        echo json_encode([
            'success' => true,
            'user' => [
                'id' => $user->id ?? 0,
                'display_name' => $user->display_name ?? 'Anonymous Visitor',
                'email' => $user->email ?? '',
                'role' => $user->role ?? 'guest',
                'avatar_url' => $user->avatar_url ?? null
            ]
        ]);
        exit;
    }

    /**
     * REST Endpoint: Switch Dev Mock Role (Development Mode Only)
     */
    public function apiSwitchDevRole()
    {
        $input = json_decode(file_get_contents('php://input'), true);
        $role = $input['role'] ?? 'guest';

        $auth = Flight::authService();
        $success = $auth->switchDevRole($role);
        $user = $auth->getCurrentUser();

        header('Content-Type: application/json');
        echo json_encode([
            'success' => $success,
            'user' => [
                'id' => $user->id ?? 0,
                'display_name' => $user->display_name ?? 'Anonymous Visitor',
                'email' => $user->email ?? '',
                'role' => $user->role ?? 'guest',
                'avatar_url' => $user->avatar_url ?? null
            ]
        ]);
        exit;
    }

    /**
     * REST Endpoint: Formula Repair (Single-Developer Authority)
     * Directly commits changes to Git shard, hash registry, and MariaDB.
     */
    public function apiSuggestRepair()
    {
        // In flattened single-developer mode, all suggestions apply directly
        return $this->apiApplyRepair();
    }

    /**
     * REST Endpoint: Direct Formula Repair (Curator / Admin Tier)
     */
    public function apiApplyRepair()
    {
        if (class_exists('\Tracy\Debugger')) {
            \Tracy\Debugger::$showBar = false;
        }

        $auth = Flight::authService();
        $user = $auth->getCurrentUser();
        $isLocalDev = (php_sapi_name() === 'cli' || (isset($_SERVER['REMOTE_ADDR']) && in_array($_SERVER['REMOTE_ADDR'], ['127.0.0.1', '::1', 'localhost'], true)));

        if (!$isLocalDev && !$auth->hasRole('curator', $user)) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $url = $input['url'] ?? '';
        $formulaId = $input['formula_id'] ?? '';
        $latex = $input['latex'] ?? null;
        $prose = $input['prose'] ?? null;
        $hint = $input['hint'] ?? null;

        // 1. Resolve Target (Formula ID takes precedence if valid, then URL query, then LaTeX)
        $target = '';
        if (!empty($formulaId) && $formulaId !== 'synthesized-custom' && !str_starts_with($formulaId, 'synthesized-')) {
            $target = $formulaId;
        } else if (!empty($url) && (strpos($url, 'id=') !== false || strpos($url, 'latex=') !== false)) {
            $target = $url;
        } else if (!empty($latex)) {
            $target = $latex;
        }

        if (empty($target)) {
            header('Content-Type: application/json');
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Valid URL, Formula ID, or LaTeX equation is required.']);
            exit;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $result = $reviewService->repairTarget($target, $hint, $user->id ?? 1, $prose);

            header('Content-Type: application/json');
            echo json_encode([
                'success' => true,
                'message' => 'Formula updated and synchronized successfully via fixlatex engine!',
                'data' => $result
            ]);
        } catch (\Throwable $e) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode([
                'success' => false,
                'error' => 'Failed to apply repair: ' . $e->getMessage()
            ]);
        }
        exit;
    }

    /**
     * REST Endpoint: Get Review Queue
     */
    public function apiGetReviews()
    {
        $status = $_GET['status'] ?? 'pending';
        $formulaId = $_GET['formula_id'] ?? null;

        try {
            $reviewService = Flight::formulaReviewService();
            $reviews = $reviewService->getReviews($status, $formulaId);

            header('Content-Type: application/json');
            echo json_encode(['success' => true, 'reviews' => $reviews]);
        } catch (\Throwable $e) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }

    /**
     * REST Endpoint: Approve Review Suggestion (Curator / Admin Tier)
     */
    public function apiApproveReview()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $reviewId = (int)($input['review_id'] ?? 0);

        if ($reviewId <= 0) {
            header('Content-Type: application/json');
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Valid review ID is required.']);
            exit;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $result = $reviewService->approveReview($reviewId, $user->id);

            header('Content-Type: application/json');
            echo json_encode([
                'success' => true,
                'message' => 'Review approved and changes committed to shard & database!',
                'data' => $result
            ]);
        } catch (\Throwable $e) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }

    /**
     * REST Endpoint: Reject Review Suggestion (Curator / Admin Tier)
     */
    public function apiRejectReview()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            header('Content-Type: application/json');
            http_response_code(403);
            echo json_encode(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.']);
            exit;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $reviewId = (int)($input['review_id'] ?? 0);
        $notes = $input['notes'] ?? null;

        if ($reviewId <= 0) {
            header('Content-Type: application/json');
            http_response_code(400);
            echo json_encode(['success' => false, 'error' => 'Valid review ID is required.']);
            exit;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $reviewService->rejectReview($reviewId, $user->id, $notes);

            header('Content-Type: application/json');
            echo json_encode([
                'success' => true,
                'message' => 'Review rejected.'
            ]);
        } catch (\Throwable $e) {
            header('Content-Type: application/json');
            http_response_code(500);
            echo json_encode(['success' => false, 'error' => $e->getMessage()]);
        }
        exit;
    }
}

