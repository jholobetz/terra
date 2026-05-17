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
            }
        }

        // 2. Conditional Shard Loading (Always check even if physicsContent is set)
        if ($targetSlug) {
            $this->loadShardForSlug($targetSlug);
        } else if ($this->requestedSlug) {
            $this->loadShardForSlug($this->requestedSlug);
        }

        return $this->physicsContent;
    }

    /**
     * Loads a specific JSON shard from disk based on the slug.
     */
    private function loadShardForSlug(string $slug): void
    {
        $baseDir = PROJECT_ROOT . '/app/config/content/';
        
        // 1. Check if it is a main topic shard
        if (isset($this->physicsContent['topics'][$slug]['shard']) && !isset($this->physicsContent['topics'][$slug]['pillars'])) {
            $shardPath = $baseDir . $this->physicsContent['topics'][$slug]['shard'];
            if (file_exists($shardPath)) {
                $topicData = json_decode(file_get_contents($shardPath), true) ?: [];
                $this->physicsContent['topics'][$slug] = array_merge($this->physicsContent['topics'][$slug], $topicData);
            }
        }

        // 2. Check if it is a subtopic shard (via search_index)
        if (isset($this->physicsContent['subtopics'][$slug])) {
            return;
        }

        $shardFile = $this->physicsContent['search_index'][$slug]['s'] ?? null;
        if ($shardFile && file_exists($baseDir . $shardFile)) {
            $shard = json_decode(file_get_contents($baseDir . $shardFile), true) ?: [];
            if (is_array($shard)) {
                $this->physicsContent['subtopics'] = array_merge($this->physicsContent['subtopics'], $shard);
            }
        }
    }

    /**
     * Forces loading of all shards (used for sync or full listings).
     */
    private function loadAllShards(): void
    {
        if ($this->physicsContent === null) {
            $this->getPhysicsContent();
        }
        $baseDir = PROJECT_ROOT . '/app/config/content/';

        // 1. Load Main Topic Shards
        foreach ($this->physicsContent['topics'] as $slug => $meta) {
            if (isset($meta['shard'])) {
                $shardPath = $baseDir . $meta['shard'];
                if (file_exists($shardPath)) {
                    $topicData = json_decode(file_get_contents($shardPath), true) ?: [];
                    $this->physicsContent['topics'][$slug] = array_merge($this->physicsContent['topics'][$slug], $topicData);
                }
            }
        }

        // 2. Load Subtopic Shards
        $files = scandir($baseDir);
        foreach ($files as $file) {
            if (pathinfo($file, PATHINFO_EXTENSION) === 'json' && !in_array($file, ['categories.json', 'formulas.json', 'search_index.json', 'constants.json', 'entities.json', 'pillar_profiles.json'])) {
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
            $this->loadAllShards();
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

        $nonce = $this->app->get('csp_nonce') ?? '';
        $viewData = array_merge($data, ['nonce' => $nonce]);
        $bodyContent = $this->app->view()->fetch($view, $viewData) ?: '';

        $isBuildMode = ($this->app->request()->query->build_mode === '1');

        if ($isPreview && !$isBuildMode) {
            $bodyContent .= '
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
                    <a href="/physics/sync" class="btn btn-primary" style="box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 50px; padding: 12px 24px; text-decoration: none; display: flex; align-items: center; gap: 8px; background-color: #007bff; color: white; border: none; font-family: sans-serif;">
                        <span>🔄</span> <strong>Sync Now</strong>
                    </a>
                </div>';
        }

        $this->app->render('physics/layout', array_merge($viewData, [
            'body_content' => $bodyContent,
            'is_preview' => $isPreview && !$isBuildMode,
            'nonce' => $nonce,
            'menu_topics' => $menuTopics,
            'menu_simulations' => $menuSimulations,
        ]));
    }

    public function index()
    {
        $topics = $this->fetchAllData('topics');
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

    public function sync(): void
    {
        $this->loadAllShards();
        $this->performSync();
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        touch($syncLock);
        $this->app->redirect($this->app->request()->referrer ?: '/physics');
    }

    public function searchIndex(): void
    {
        $path = PROJECT_ROOT . '/app/config/content/search_index.json';
        if (file_exists($path)) {
            $this->app->json(json_decode(file_get_contents($path), true));
        } else {
            $this->app->json([]);
        }
    }

    public function constants()
    {
        $this->loadAllShards();
        $constants = $this->physicsContent['constants'] ?? [];
        
        $this->renderWithLayout('physics/constants', [
            'title' => 'Fundamental Physical Constants',
            'constants' => $constants
        ]);
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
        $cachePath = PROJECT_ROOT . "/public/cache/topic/{$slug}.html";
        $isStale = $this->isHubCacheStale($slug, $cachePath);

        // Auto-sync manifest if stale or preview
        if ($isStale || $this->isPreviewActive()) {
            $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
            if (file_exists($manifestPath)) {
                $manifestData = json_decode(file_get_contents($manifestPath), true);
                if ($manifestData) {
                    $this->syncIndividualTopic($slug, $manifestData);
                }
            }
        }

        if (file_exists($cachePath) && !$isStale && !$this->isPreviewActive()) {
            header('Content-Type: text/html; charset=utf-8');
            readfile($cachePath);
            return;
        }

        // If stale, purge cache
        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $this->requestedSlug = $slug;
        $this->loadAllShards();
        $topic = $this->fetchAndPrepare('topics', $slug);

        if (empty($topic)) {
            $this->app->notFound();
            return;
        }

        $content = $this->getPhysicsContent();
        
        // Build subtopics map for dynamic rendering
        $subtopicsMap = [];
        foreach ($content['subtopics'] as $subSlug => $sub) {
            if (!is_array($sub)) continue;
            $subtopicsMap[$subSlug] = [
                'title' => $sub['title'] ?? $subSlug,
                'snippet' => $sub['snippet'] ?? '',
                'snippet_svg' => $sub['snippet_svg'] ?? '',
                'hero_math' => $sub['hero_math'] ?? ''
            ];
        }

        // Resolve Bridges (Slug to metadata mapping)
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

        $this->renderWithLayout('physics/topic', array_merge($topic, [
            'topic' => $topic,
            'subtopics_map' => $subtopicsMap,
            'pillars' => !empty($topic['pillars']) ? (is_string($topic['pillars']) ? json_decode($topic['pillars'], true) : $topic['pillars']) : null,
            'bridges' => $resolvedBridges,
            'intro' => $topic['intro'] ?? null,
            'field' => $topic['field'] ?? null,
            'density' => $topic['density'] ?? null,
            'slug' => $slug
        ]));
    }

    public function viewSubtopic(string $slug)
    {
        // 1. Static Check with Auto-Invalidation
        $cachePath = PROJECT_ROOT . "/public/cache/subtopic/{$slug}.html";
        $isStale = $this->isCacheStale($slug, $cachePath);

        if (file_exists($cachePath) && !$isStale && !$this->isPreviewActive()) {
            header('Content-Type: text/html; charset=utf-8');
            readfile($cachePath);
            return;
        }

        // If stale, delete it so fetchAndPrepare won't return stale database results if synced
        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $this->requestedSlug = $slug;
        $subtopic = $this->fetchAndPrepare('subtopics', $slug);

        if (empty($subtopic)) {
            $this->app->notFound();
            return;
        }

        $breadcrumbs = $this->resolveBreadcrumbs(!empty($subtopic['parents']) ? (array)$subtopic['parents'] : []);

        // Get Related Topics via Search Index
        $related = $this->getRelatedTopics($slug);

        $this->renderWithLayout('physics/subtopic', array_merge($subtopic, [
            'breadcrumbs' => $breadcrumbs,
            'related_topics' => $related,
            'title' => $subtopic['title'],
            'content' => $subtopic['content'],
            'equations' => $subtopic['equations'] ?? [],
            'breakdowns' => $subtopic['breakdowns'] ?? [],
            'formulas' => $subtopic['formulas'] ?? []
        ]));
    }

    /**
     * Resolves multiple parent slugs into a flat breadcrumb structure.
     * Supports both Topic Hubs and Subtopic parents with recursive lineage tracing.
     */
    private function resolveBreadcrumbs(array $parentSlugs, array $visited = []): array
    {
        $content = $this->getPhysicsContent();
        $hubs = [];
        $intermediates = [];

        foreach ($parentSlugs as $slug) {
            if (in_array($slug, $visited)) continue;
            $visited[] = $slug;

            // 1. Check if it's a Topic Hub (Category)
            if (isset($content['topics'][$slug])) {
                $hubs[$slug] = [
                    'title' => $content['topics'][$slug]['title'],
                    'url' => '/physics/topic/' . $slug
                ];
            } else {
                // 2. Check if it's a Subtopic parent
                $subData = $this->fetchAndPrepare('subtopics', $slug);
                if (!empty($subData) && isset($subData['title'])) {
                    $intermediates[$slug] = [
                        'title' => $subData['title'],
                        'url' => '/physics/subtopic/' . $slug,
                        'parents' => !empty($subData['parents']) ? (array)$subData['parents'] : []
                    ];
                }
            }
        }

        $crumbs = [];
        
        // If we found direct hubs, group them
        if (!empty($hubs)) {
            $crumbs[] = [
                'is_multi' => true,
                'links' => array_values($hubs)
            ];
        }

        // If no direct hubs but we have intermediates, trace the first intermediate upwards
        if (empty($hubs) && !empty($intermediates)) {
            $first = reset($intermediates);
            $ancestors = $this->resolveBreadcrumbs($first['parents'], $visited);
            $crumbs = array_merge($ancestors, [[
                'title' => $first['title'],
                'url' => $first['url']
            ]]);
        } elseif (!empty($intermediates)) {
            // If we have hubs AND intermediates, just append the first intermediate for context
            $first = reset($intermediates);
            $crumbs[] = [
                'title' => $first['title'],
                'url' => $first['url']
            ];
        }

        return $crumbs;
    }

    /**
     * Checks if the cached Hub HTML is older than the source manifest.
     */
    private function isHubCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;

        $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
        if (!file_exists($manifestPath)) return false;

        return filemtime($manifestPath) > filemtime($cachePath);
    }

    /**
     * Checks if the cached HTML file is older than the source JSON shard.
     */
    private function isCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;

        $content = $this->getPhysicsContent($slug);
        $shardFile = $content['search_index'][$slug]['s'] ?? null;
        
        if (!$shardFile) return false;

        $shardPath = PROJECT_ROOT . '/app/config/content/' . $shardFile;
        if (!file_exists($shardPath)) return false;

        return filemtime($shardPath) > filemtime($cachePath);
    }

    /**
     * Surgically syncs a single topic (hub) from JSON manifest to Database.
     */
    private function syncIndividualTopic(string $slug, array $data): void
    {
        $pillars = !empty($data['pillars']) ? json_encode($data['pillars']) : '[]';
        $bridges = !empty($data['metadata']['bridges']) ? json_encode($data['metadata']['bridges']) : '[]';
        
        $this->app->db()->runQuery(
            "INSERT INTO topics (slug, title, intro, field, density, pillars, bridges) 
             VALUES (?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
                title = VALUES(title), 
                intro = VALUES(intro), 
                field = VALUES(field), 
                density = VALUES(density), 
                pillars = VALUES(pillars), 
                bridges = VALUES(bridges)",
            [
                $slug,
                $data['title'],
                $data['metadata']['intro'] ?? '',
                $data['metadata']['field'] ?? '',
                $data['metadata']['density'] ?? '',
                $pillars,
                $bridges
            ]
        );
    }

    /**
     * Surgically syncs a single subtopic from JSON to Database.
     */
    private function syncIndividualSubtopic(string $slug, array $data): void
    {
        // Safety check to ensure we have valid data before syncing
        if (empty($data['title']) || empty($data['content'])) {
            return;
        }

        $primaryParent = !empty($data['parents']) ? $data['parents'][0] : '';

        $this->app->db()->runQuery(
            "INSERT INTO subtopics (slug, parent_topic, title, content, snippet, snippet_svg, hero_math, equations, breakdowns, formula_data, parents, standard) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
                parent_topic = VALUES(parent_topic), 
                title = VALUES(title), 
                content = VALUES(content), 
                snippet = VALUES(snippet),
                snippet_svg = VALUES(snippet_svg),
                hero_math = VALUES(hero_math),
                equations = VALUES(equations),
                breakdowns = VALUES(breakdowns),
                formula_data = VALUES(formula_data), 
                parents = VALUES(parents), 
                standard = VALUES(standard)",
            [
                $slug,
                $primaryParent,
                $data['title'],
                $data['content'],
                $data['snippet'] ?? '',
                $data['snippet_svg'] ?? '',
                $data['hero_math'] ?? '',
                json_encode($data['equations'] ?? []),
                json_encode($data['breakdowns'] ?? []),
                json_encode($data['formula_ids'] ?? []),
                json_encode($data['parents'] ?? []),
                $data['standard'] ?? 'legacy'
            ]
        );
    }

    private function getRelatedTopics(string $currentSlug, int $limit = 3): array
    {
        $content = $this->getPhysicsContent();
        $index = $content['search_index'] ?? [];
        
        if (!isset($index[$currentSlug])) return [];
        
        $currentKeywords = $index[$currentSlug]['k'] ?? [];
        if (empty($currentKeywords)) return [];
        
        $scores = [];
        foreach ($index as $slug => $data) {
            if ($slug === $currentSlug) continue;
            
            $otherKeywords = $data['k'] ?? [];
            $overlap = count(array_intersect($currentKeywords, $otherKeywords));
            
            if ($overlap > 0) {
                if (!empty($data['p']) && !empty($index[$currentSlug]['p']) && $data['p'][0] === $index[$currentSlug]['p'][0]) {
                    $overlap += 2;
                }
                $scores[$slug] = $overlap;
            }
        }
        
        arsort($scores);
        $relatedSlugs = array_slice(array_keys($scores), 0, $limit);
        
        $results = [];
        foreach ($relatedSlugs as $rSlug) {
            $results[] = [
                'slug' => $rSlug,
                'title' => $index[$rSlug]['t']
            ];
        }
        
        return $results;
    }

    private function checkAutoSync(): void
    {
        // Sharded auto-sync would need tracking of multiple files.
        // For now, we will rely on manual sync button in preview.
    }

    protected function performSync(): void
    {
        $this->loadAllShards();
        $data = $this->getPhysicsContent();
        $db = $this->app->db();

        foreach ($data['topics'] ?? [] as $slug => $t) {
            $db->runQuery("INSERT INTO topics (slug, title, content, pillars, intro, bridges, field, density, equations, breakdowns, formula_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE 
                    title = VALUES(title), content = VALUES(content), pillars = VALUES(pillars), intro = VALUES(intro), 
                    bridges = VALUES(bridges), field = VALUES(field), density = VALUES(density), equations = VALUES(equations), 
                    breakdowns = VALUES(breakdowns), formula_data = VALUES(formula_data)", 
                [$slug, $t['title'], $t['content'], json_encode($t['pillars'] ?? []), $t['intro'] ?? '', json_encode($t['bridges'] ?? []), $t['field'] ?? '', $t['density'] ?? '', json_encode($t['equations'] ?? []), json_encode($t['breakdowns'] ?? []), json_encode($t['formula_ids'] ?? [])]);
        }

        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            $primaryParent = !empty($st['parents']) ? $st['parents'][0] : '';
            $db->runQuery("INSERT INTO subtopics (slug, parent_topic, title, content, snippet, snippet_svg, hero_math, equations, breakdowns, formula_data, parents, standard) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE 
                    parent_topic = VALUES(parent_topic), title = VALUES(title), content = VALUES(content), 
                    snippet = VALUES(snippet), snippet_svg = VALUES(snippet_svg), hero_math = VALUES(hero_math), 
                    equations = VALUES(equations), breakdowns = VALUES(breakdowns), formula_data = VALUES(formula_data), 
                    parents = VALUES(parents), standard = VALUES(standard)", 
                [
                    $slug, 
                    $primaryParent, 
                    $st['title'], 
                    $st['content'], 
                    $st['snippet'] ?? '', 
                    $st['snippet_svg'] ?? '', 
                    $st['hero_math'] ?? '', 
                    json_encode($st['equations'] ?? []), 
                    json_encode($st['breakdowns'] ?? []), 
                    json_encode($st['formula_ids'] ?? []),
                    json_encode($st['parents'] ?? []),
                    $st['standard'] ?? 'legacy'
                ]);
        }
    }

    private function isPreviewActive(): bool
    {
        $previewQuery = $this->app->request()->query->preview;
        $buildMode = $this->app->request()->query->build_mode;
        
        if ($previewQuery !== null || $buildMode !== null) {
            $isActive = ($previewQuery === '1' || $buildMode === '1');
            if ($previewQuery !== null) {
                setcookie('physics_preview', $isActive ? '1' : '0', time() + 3600, '/');
            }
            return $isActive;
        }
        return ($_COOKIE['physics_preview'] ?? '0') === '1';
    }

    private function fetchAllData(string $table): array
    {
        if ($this->isPreviewActive()) {
            $this->loadAllShards();
            $content = $this->getPhysicsContent();
            $list = [];
            foreach ($content[$table] ?? [] as $slug => $data) {
                $data['slug'] = $slug;
                $list[] = $data;
            }
            return $list;
        }
        return $this->app->db()->fetchAll("SELECT * FROM {$table} ORDER BY id ASC");
    }

    private function fetchAndPrepare(string $table, string $slug): array
    {
        $content = $this->getPhysicsContent($slug);
        
        // Auto-sync individual node if we are in view mode and cache was stale
        if (!$this->isPreviewActive() && $table === 'subtopics' && isset($content['subtopics'][$slug])) {
            $this->syncIndividualSubtopic($slug, $content['subtopics'][$slug]);
        }

        if ($this->isPreviewActive()) {
            $data = $content[$table][$slug] ?? null;
            if (!$data) return [];
            $data['slug'] = $slug;
            
            $data['formulas'] = [];
            if (!empty($data['formula_ids'])) {
                foreach ($data['formula_ids'] as $f_id) {
                    if (isset($content['formula_registry'][$f_id])) {
                        $data['formulas'][] = $content['formula_registry'][$f_id];
                    }
                }
            }
            return $data;
        }

        $row = $this->app->db()->fetchRow("SELECT * FROM {$table} WHERE slug = ?", [$slug]);
        if (!$row) return [];

        // Normalize to associative array
        $data = [];
        if (is_object($row)) {
            $data = method_exists($row, 'getData') ? $row->getData() : (array) $row;
        } else {
            $data = $row;
        }
        
        $f_ids = !empty($data['formula_data']) ? json_decode($data['formula_data'], true) : [];
        
        $data['formulas'] = [];
        if (!empty($f_ids)) {
            foreach ($f_ids as $f_id) {
                if (isset($content['formula_registry'][$f_id])) {
                    $data['formulas'][] = $content['formula_registry'][$f_id];
                }
            }
        }

        return $data;
    }
}
