<?php

namespace app\controllers;

use flight\Engine;
use Flight;

class AdminController
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
     * Enforces Local Single-Developer Studio or Admin token authority.
     */
    public function requireAdminAuthority(bool $jsonResponse = true): void
    {
        $auth = Flight::authService();
        if (!$auth->hasRole('admin')) {
            http_response_code(403);
            if ($jsonResponse) {
                header('Content-Type: application/json');
                echo json_encode(['success' => false, 'error' => 'Forbidden: Local studio or admin privileges required.']);
            } else {
                header('HTTP/1.1 403 Forbidden');
                echo 'Forbidden: Admin access restricted to localhost studio.';
            }
            exit;
        }
    }

    /**
     * View action rendering the Unified Platform Assessment & Health Cockpit.
     */
    public function adminAssess()
    {
        $this->requireAdminAuthority(false);

        $latestPath = PROJECT_ROOT . '/docs/reports/latest.json';
        $latest = [];
        if (file_exists($latestPath)) {
            $latest = json_decode(file_get_contents($latestPath), true) ?: [];
        }

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

        $topics = $this->service()->fetchAllData('topics');

        $this->app->physicsController()->renderWithLayout('physics/admin/assess', [
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
        $this->requireAdminAuthority(true);

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
        $this->requireAdminAuthority(true);

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
        $this->requireAdminAuthority(true);

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
        $this->requireAdminAuthority(true);

        $cmd = "cd " . escapeshellarg(PROJECT_ROOT) . " && PYTHONPATH=. .venv/bin/python3 scripts/maintenance/auto_linker.py 2>&1";
        exec($cmd, $output, $return_var);

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
        $this->requireAdminAuthority(true);

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
        $this->requireAdminAuthority(true);

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

        $keywords = array_map('trim', explode(',', $keywordsInput));
        $keywords = array_filter($keywords);

        $refPath = PROJECT_ROOT . '/app/config/ref_data/semantic_references.json';
        $references = [];
        if (file_exists($refPath)) {
            $references = json_decode(file_get_contents($refPath), true) ?: [];
        }

        if (isset($references[$slug])) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic already registered as reference.']);
            exit;
        }

        $references[$slug] = [
            'title' => $title,
            'reference_prose' => $prose,
            'keywords' => array_values($keywords)
        ];

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
        $this->requireAdminAuthority(true);

        $input = json_decode(file_get_contents('php://input'), true);
        $slug = $input['slug'] ?? '';
        $citations = $input['citations'] ?? [];

        if (empty($slug)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic slug is required.']);
            exit;
        }

        $content = $this->service()->getPhysicsContent($slug);
        $searchIndex = $content['search_index'] ?? [];
        $shardFile = $searchIndex[$slug]['s'] ?? null;
        $baseDir = PROJECT_ROOT . '/app/config/content/';

        if (!$shardFile || !file_exists($baseDir . $shardFile)) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Shard file for subtopic not found.']);
            exit;
        }

        $shardData = json_decode(file_get_contents($baseDir . $shardFile), true) ?: [];
        if (!isset($shardData[$slug])) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic not found in content shard.']);
            exit;
        }

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

        if (file_put_contents($baseDir . $shardFile, json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE)) === false) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Failed to save updated shard back to disk.']);
            exit;
        }

        $this->service()->clearCache();
        $subtopicData = $this->service()->fetchAndPrepare('subtopics', $slug);
        if (!empty($subtopicData)) {
            $this->service()->syncIndividualSubtopic($slug, $subtopicData);
        }

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
        $this->requireAdminAuthority(true);

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
        $this->requireAdminAuthority(true);

        $content = $this->service()->getPhysicsContent($slug);
        $subtopic = $content['subtopics'][$slug] ?? null;

        if (!$subtopic) {
            header('Content-Type: application/json');
            echo json_encode(['success' => false, 'error' => 'Subtopic not found']);
            exit;
        }

        $parent = null;
        $searchIndex = $content['search_index'] ?? [];
        if (isset($searchIndex[$slug]['s'])) {
            $parent = str_replace('.json', '', $searchIndex[$slug]['s']);
        }

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
}
