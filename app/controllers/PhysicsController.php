<?php

namespace app\controllers;

use flight\Engine;

class PhysicsController
{
    protected Engine $app;
    private ?array $physicsContent = null;

    private ?string $requestedSlug = null;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    /**
     * Memoized loader for the physics content file.
     * Supports lazy-loading specific shards based on the requested slug.
     */
    private function getPhysicsContent(?string $targetSlug = null): array
    {
        if ($this->physicsContent === null) {
            $baseDir = PROJECT_ROOT . '/app/config/content/';
            $this->physicsContent = [
                'topics' => [],
                'subtopics' => [],
                'formula_registry' => [],
                'search_index' => [],
                'simulations' => []
            ];

            if (is_dir($baseDir)) {
                // 1. Always load Registries
                if (file_exists($baseDir . 'categories.json')) {
                    $this->physicsContent['topics'] = json_decode(file_get_contents($baseDir . 'categories.json'), true) ?: [];
                }
                if (file_exists($baseDir . 'formulas.json')) {
                    $this->physicsContent['formula_registry'] = json_decode(file_get_contents($baseDir . 'formulas.json'), true) ?: [];
                }
                if (file_exists($baseDir . 'search_index.json')) {
                    $this->physicsContent['search_index'] = json_decode(file_get_contents($baseDir . 'search_index.json'), true) ?: [];
                }

                // 2. Conditional Shard Loading
                if ($targetSlug) {
                    $this->loadShardForSlug($targetSlug);
                } else if ($this->requestedSlug) {
                    $this->loadShardForSlug($this->requestedSlug);
                }
            }
        }
        return $this->physicsContent;
    }

    /**
     * Loads a specific JSON shard from disk based on the slug.
     */
    private function loadShardForSlug(string $slug): void
    {
        $baseDir = PROJECT_ROOT . '/app/config/content/';
        // Use 's' key from search_index for the shard filename
        $shardFile = $this->physicsContent['search_index'][$slug]['s'] ?? null;
        
        if ($shardFile && file_exists($baseDir . $shardFile)) {
            $shard = json_decode(file_get_contents($baseDir . $shardFile), true) ?: [];
            $this->physicsContent['subtopics'] = array_merge($this->physicsContent['subtopics'], $shard);
        }
    }

    /**
     * Forces loading of all shards (used for sync or full listings).
     */
    private function loadAllShards(): void
    {
        $baseDir = PROJECT_ROOT . '/app/config/content/';
        $files = scandir($baseDir);
        foreach ($files as $file) {
            if (strpos($file, '.json') !== false && !in_array($file, ['categories.json', 'formulas.json', 'shard_index.json', 'constants.json'])) {
                $shard = json_decode(file_get_contents($baseDir . $file), true) ?: [];
                if (is_array($shard)) {
                    $this->physicsContent['subtopics'] = array_merge($this->physicsContent['subtopics'], $shard);
                }
            }
        }
    }

    /**
     * Helper method to render views with the main layout.
     */
    protected function renderWithLayout(string $view, array $data = []): void
    {
        $isPreview = $this->isPreviewActive();
        
        if (!$isPreview) {
            $this->checkAutoSync();
        }

        // Fetch navigation items from appropriate source
        if ($isPreview) {
            $content = $this->getPhysicsContent();
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
            $topicsList = $this->app->db()->fetchAll("SELECT slug, title FROM topics ORDER BY id ASC");
            $simsList = $this->app->db()->fetchAll("SELECT slug, title FROM simulations ORDER BY id ASC");
        }

        $menuTopics = [];
        foreach ($topicsList as $topic) {
            $menuTopics[$topic['slug']] = ['title' => $topic['title']];
        }

        $menuSimulations = [];
        foreach ($simsList as $sim) {
            $menuSimulations[$sim['slug']] = ['title' => $sim['title']];
        }

        // Fallback for nonce to prevent 500 if not set in bootstrap
        $nonce = $this->app->get('csp_nonce') ?? '';

        // Render the specific view and capture its output
        $viewData = array_merge($data, ['nonce' => $nonce]);
        $bodyContent = $this->app->view()->fetch($view, $viewData) ?: '';

        // Inject a floating "Sync Now" button when in Preview Mode
        if ($isPreview) {
            $bodyContent .= '
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
                    <a href="/physics/sync" class="btn btn-primary" style="box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 50px; padding: 12px 24px; text-decoration: none; display: flex; align-items: center; gap: 8px; background-color: #007bff; color: white; border: none; font-family: sans-serif;">
                        <span>🔄</span> <strong>Sync Now</strong>
                    </a>
                </div>';
        }

        $this->app->render('physics/layout', array_merge($viewData, [
            'body_content' => $bodyContent,
            'is_preview' => $isPreview,
            'nonce' => $nonce,
            'menu_topics' => $menuTopics,
            'menu_simulations' => $menuSimulations,
        ]));
    }

    public function index()
    {
        $topics = $this->fetchAllData('topics');
        
        // Process content to create short descriptions
        foreach ($topics as &$topic) {
            $cleanContent = strip_tags($topic['content']);
            $topic['description'] = mb_strimwidth($cleanContent, 0, 120, "...");
        }

        $this->renderWithLayout('physics/home', [
            'title' => 'The Physics Lab',
            'subtitle' => 'Explore the fundamental laws of the universe through interactive simulations and detailed explanations.',
            'topics' => $topics
        ]);
    }

    public function install()
    {
        $sqlPath = PROJECT_ROOT . '/database_init.sql';
        if (file_exists($sqlPath)) {
            $sql = file_get_contents($sqlPath);
            $this->app->db()->runQuery($sql);
            echo "<h1>Success</h1><p>Database schema initialized in MariaDB.</p>";
            echo '<a href="/physics">Go to The Physics Lab</a>';
        } else {
            $this->app->halt(500, 'Schema file not found at ' . $sqlPath);
        }
    }

    public function sync(): void
    {
        $this->loadAllShards();
        $this->performSync();
        
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        touch($syncLock);

        $this->app->redirect($this->app->request()->referrer ?: '/physics');
    }

    public function simulations()
    {
        $this->loadAllShards();
        $sims = $this->fetchAllData('simulations');
        $this->renderWithLayout('physics/simulations', [
            'title' => 'Interactive Simulations',
            'simulations' => $sims,
        ]);
    }

    public function viewSimulation(string $slug)
    {
        $this->requestedSlug = $slug;
        $data = $this->fetchAndPrepare('simulations', $slug);
        if (!$data) {
            $this->app->notFound();
            return;
        }
        $this->renderWithLayout('physics/simulation_page', array_merge($data, [
            'physics' => $data['physics'] ?? $data['description'] ?? '',
        ]));
    }

    public function viewTopic(string $slug)
    {
        $this->requestedSlug = $slug;
        $topic = $this->fetchAndPrepare('topics', $slug);

        if (empty($topic)) {
            $this->app->notFound();
            return;
        }

        $this->renderWithLayout('physics/topic', array_merge($topic, [
            'slug' => $slug,
        ]));
    }

    public function viewSubtopic(string $slug)
    {
        $this->requestedSlug = $slug;
        $subtopic = $this->fetchAndPrepare('subtopics', $slug);

        if (empty($subtopic)) {
            $this->app->notFound();
            return;
        }

        $breadcrumbs = [];
        // Use primary parent (index 0) for breadcrumbs
        $currentParentSlug = !empty($subtopic['parents']) ? $subtopic['parents'][0] : ($subtopic['parent_topic'] ?? '');

        // Trace parents upwards
        while (!empty($currentParentSlug)) {
            $foundParent = false;

            // 1. Check if it is a main Topic
            $topicRow = $this->app->db()->fetchRow("SELECT title, slug FROM topics WHERE slug = ?", [$currentParentSlug]);
            $pData = method_exists($topicRow, 'getData') ? $topicRow->getData() : (array) $topicRow;
            
            if (!empty($pData) && isset($pData['title'])) {
                array_unshift($breadcrumbs, [
                    'title' => $pData['title'],
                    'url' => '/physics/topic/' . $pData['slug']
                ]);
                $currentParentSlug = ''; // Top level reached
                $foundParent = true;
            } 
            
            // 2. Check if it is a Subtopic
            if (!$foundParent) {
                $subRow = $this->app->db()->fetchRow("SELECT title, slug, parent_topic FROM subtopics WHERE slug = ?", [$currentParentSlug]);
                $pData = method_exists($subRow, 'getData') ? $subRow->getData() : (array) $subRow;
                
                if (!empty($pData) && isset($pData['title'])) {
                    array_unshift($breadcrumbs, [
                        'title' => $pData['title'],
                        'url' => '/physics/subtopic/' . $pData['slug']
                    ]);
                    $currentParentSlug = $pData['parent_topic'] ?? '';
                    $foundParent = true;
                }
            }

            if (!$foundParent) break;
        }

        $this->renderWithLayout('physics/subtopic', array_merge($subtopic, [
            'slug' => $slug,
            'breadcrumbs' => $breadcrumbs,
            'breadcrumb_active_title' => $subtopic['title']
        ]));
    }

    /**
     * Automatically syncs MariaDB if the physics_content.php file has been updated.
     */
    private function checkAutoSync(): void
    {
        if ($this->isPreviewActive()) return;

        $contentFile = PROJECT_ROOT . '/app/config/physics_content.json';
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';

        if (!file_exists($contentFile)) return;

        $lastSync = file_exists($syncLock) ? filemtime($syncLock) : 0;

        if (filemtime($contentFile) > $lastSync) {
            $this->performSync();
            touch($syncLock);
        }
    }

    private function performSync(): void
    {
        $data = $this->getPhysicsContent();
        $db = $this->app->db();

        foreach ($data['simulations'] ?? [] as $slug => $s) {
            if (($s['status'] ?? '') === 'draft') {
                $db->runQuery("DELETE FROM simulations WHERE slug = ?", [$slug]);
                continue;
            }
            $db->runQuery("REPLACE INTO simulations (slug, title, description, physics, equations) VALUES (?, ?, ?, ?, ?)", 
                [$slug, $s['title'], $s['description'], $s['physics'], json_encode($s['equations'] ?? [])]);
        }

        foreach ($data['topics'] ?? [] as $slug => $t) {
            if (($t['status'] ?? '') === 'draft') {
                $db->runQuery("DELETE FROM topics WHERE slug = ?", [$slug]);
                continue;
            }
            $db->runQuery("REPLACE INTO topics (slug, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?)", 
                [$slug, $t['title'], $t['content'], json_encode($t['equations'] ?? []), json_encode($t['breakdowns'] ?? []), json_encode($t['formula_ids'] ?? [])]);
        }

        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            if (isset($st["status"]) && $st["status"] === "draft") {
                $db->runQuery("DELETE FROM subtopics WHERE slug = ?", [$slug]);
                continue;
            }
            // Use the primary parent for the legacy database column
            $primaryParent = !empty($st['parents']) ? $st['parents'][0] : ($st['parent_topic'] ?? '');

            $db->runQuery("REPLACE INTO subtopics (slug, parent_topic, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                [$slug, $primaryParent, $st['title'], $st['content'], json_encode($st['equations'] ?? []), json_encode($st['breakdowns'] ?? []), json_encode($st['formula_ids'] ?? [])]);
        }
    }

    /**
     * Checks if preview mode is active based on query param or cookie.
     */
    private function isPreviewActive(): bool
    {
        $previewQuery = $this->app->request()->query->preview;
        if ($previewQuery !== null) {
            setcookie('physics_preview', $previewQuery, time() + 3600, '/');
            return $previewQuery === '1';
        }
        return ($_COOKIE['physics_preview'] ?? '0') === '1';
    }

    /**
     * Fetches all rows from either the database or the config file.
     */
    private function fetchAllData(string $table): array
    {
        if ($this->isPreviewActive()) {
            $this->loadAllShards();
            $content = $this->getPhysicsContent();
            $list = [];
            foreach ($content[$table] ?? [] as $slug => $data) {
                $data['slug'] = $slug;
                if (($data['status'] ?? '') === 'draft') {
                    $data['title'] = '<span class="draft-badge">DRAFT</span> ' . $data['title'];
                }
                $list[] = $data;
            }
            return $list;
        }
        return $this->app->db()->fetchAll("SELECT * FROM {$table} ORDER BY id ASC");
    }

    /**
     * Fetches a row from the database and prepares JSON fields.
     */
    private function fetchAndPrepare(string $table, string $slug): array
    {
        $content = $this->getPhysicsContent();
        if ($this->isPreviewActive()) {
            $data = $content[$table][$slug] ?? null;
            if (!$data) return [];
            $data['slug'] = $slug;
            if (($data['status'] ?? '') === 'draft') {
                $data['title'] = '<span class="draft-badge">DRAFT</span> ' . $data['title'];
            }
            
            // Resolve formula IDs from registry
            $data['formulas'] = [];
            if (!empty($data['formula_ids'])) {
                foreach ($data['formula_ids'] as $f_id) {
                    if (isset($content['formula_registry'][$f_id])) {
                        $data['formulas'][] = $content['formula_registry'][$f_id];
                    }
                }
            }
            
            $data['equations'] = $data['equations'] ?? [];
            $data['breakdowns'] = $data['breakdowns'] ?? [];
            return $data;
        }

        $row = $this->app->db()->fetchRow("SELECT * FROM {$table} WHERE slug = ?", [$slug]);
        if (!$row) return [];

        $data = is_object($row) ? $row->getData() : $row;
        $data['formula_ids'] = !empty($data['formula_data']) ? json_decode($data['formula_data'], true) : [];
        
        // Resolve formula IDs from registry in DB mode too
        $data['formulas'] = [];
        if (!empty($data['formula_ids'])) {
            foreach ($data['formula_ids'] as $f_id) {
                if (isset($content['formula_registry'][$f_id])) {
                    $data['formulas'][] = $content['formula_registry'][$f_id];
                }
            }
        }

        $data['equations'] = !empty($data['equations']) ? json_decode($data['equations'], true) : [];
        $data['breakdowns'] = !empty($data['breakdowns']) ? json_decode($data['breakdowns'], true) : [];

        return $data;
    }
}
