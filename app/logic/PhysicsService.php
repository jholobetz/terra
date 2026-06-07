<?php

namespace app\logic;

use flight\Engine;

class PhysicsService
{
    protected Engine $app;
    private ?array $physicsContent = null;
    private ?bool $isPreviewMode = null;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    /**
     * Toggles or queries the active preview state.
     */
    public function isPreviewActive(): bool
    {
        if ($this->isPreviewMode !== null) {
            return $this->isPreviewMode;
        }

        $previewQuery = $this->app->request()->query->preview;
        $buildMode = $this->app->request()->query->build_mode;
        
        if ($previewQuery !== null || $buildMode !== null) {
            $isActive = ($previewQuery === '1' || $buildMode === '1');
            return $isActive;
        }

        return ($_COOKIE['physics_preview'] ?? '0') === '1';
    }

    /**
     * Set explicit preview mode (useful for static builders or CLI sync tools).
     */
    public function setPreviewMode(bool $active): void
    {
        $this->isPreviewMode = $active;
    }

    /**
     * Memoized loader for standard physics content files.
     * Integrates dynamic shard lazy loading.
     */
    public function getPhysicsContent(?string $targetSlug = null): array
    {
        if ($this->physicsContent === null) {
            $baseDir = PROJECT_ROOT . '/app/config/content/';
            $this->physicsContent = [
                'topics' => [],
                'subtopics' => [],
                'formula_registry' => [],
                'search_index' => [],
                'simulations' => [],
                'constants' => [],
                'notation' => []
            ];

            if (is_dir($baseDir)) {
                if (file_exists($baseDir . 'categories.json')) {
                    $this->physicsContent['topics'] = json_decode(file_get_contents($baseDir . 'categories.json'), true) ?: [];
                }
                // Formulas are now lazily loaded on-demand via loadFormula()
                // to optimize memory consumption and speed up page bootstrap times.
                if (file_exists($baseDir . 'search_index.json')) {
                    $this->physicsContent['search_index'] = json_decode(file_get_contents($baseDir . 'search_index.json'), true) ?: [];
                }
                if (file_exists($baseDir . 'constants.json')) {
                    $this->physicsContent['constants'] = json_decode(file_get_contents($baseDir . 'constants.json'), true) ?: [];
                }
                if (file_exists($baseDir . 'notation.json')) {
                    $this->physicsContent['notation'] = json_decode(file_get_contents($baseDir . 'notation.json'), true) ?: [];
                }
            }
        }

        if ($targetSlug) {
            $this->loadShardForSlug($targetSlug);
        }

        return $this->physicsContent;
    }

    /**
     * Lazily loads an individual physical JSON shard based on a requested slug.
     */
    public function loadShardForSlug(string $slug): void
    {
        $baseDir = PROJECT_ROOT . '/app/config/content/';
        
        // 1. Topic Hub check
        if (isset($this->physicsContent['topics'][$slug]['shard']) && !isset($this->physicsContent['topics'][$slug]['pillars'])) {
            $shardPath = $baseDir . $this->physicsContent['topics'][$slug]['shard'];
            if (file_exists($shardPath)) {
                $topicData = json_decode(file_get_contents($shardPath), true) ?: [];
                $this->physicsContent['topics'][$slug] = array_merge($this->physicsContent['topics'][$slug], $topicData);
            }
        }

        // 2. Subtopic Shard check
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
     * Loads all subtopic and topic shards from the file system.
     */
    public function loadAllShards(): void
    {
        $this->getPhysicsContent();
        $baseDir = PROJECT_ROOT . '/app/config/content/';

        // Load Main Topic Shards
        foreach ($this->physicsContent['topics'] as $slug => $meta) {
            if (isset($meta['shard'])) {
                $shardPath = $baseDir . $meta['shard'];
                if (file_exists($shardPath)) {
                    $topicData = json_decode(file_get_contents($shardPath), true) ?: [];
                    $this->physicsContent['topics'][$slug] = array_merge($this->physicsContent['topics'][$slug], $topicData);
                }
            }
        }

        // Load Subtopic Shards
        $files = scandir($baseDir);
        foreach ($files as $file) {
            if (pathinfo($file, PATHINFO_EXTENSION) === 'json' && !in_array($file, ['categories.json', 'formulas.json', 'search_index.json', 'constants.json', 'entities.json', 'pillar_profiles.json', 'compiled_trie_regex.json', 'notation.json'])) {
                $shard = json_decode(file_get_contents($baseDir . $file), true) ?: [];
                if (is_array($shard)) {
                    $this->physicsContent['subtopics'] = array_merge($this->physicsContent['subtopics'], $shard);
                }
            }
        }
    }

    /**
     * Scans registry keywords to find related content nodes.
     */
    public function getRelatedTopics(string $currentSlug, int $limit = 3): array
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

    /**
     * Resolves breadcrumbs and traces lineage recursively.
     */
    public function resolveBreadcrumbs(array $parentSlugs, array $visited = []): array
    {
        $content = $this->getPhysicsContent();
        $hubs = [];
        $intermediates = [];

        foreach ($parentSlugs as $slug) {
            if (in_array($slug, $visited)) continue;
            $visited[] = $slug;

            // 1. Topic Hub check
            if (isset($content['topics'][$slug])) {
                $hubs[$slug] = [
                    'title' => $content['topics'][$slug]['title'],
                    'url' => '/physics/topic/' . $slug
                ];
            } else {
                // 2. Subtopic check
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
        if (!empty($hubs)) {
            $crumbs[] = [
                'is_multi' => true,
                'links' => array_values($hubs)
            ];
        }

        if (empty($hubs) && !empty($intermediates)) {
            $first = reset($intermediates);
            $ancestors = $this->resolveBreadcrumbs($first['parents'], $visited);
            $crumbs = array_merge($ancestors, [[
                'title' => $first['title'],
                'url' => $first['url']
            ]]);
        } elseif (!empty($intermediates)) {
            $first = reset($intermediates);
            $crumbs[] = [
                'title' => $first['title'],
                'url' => $first['url']
            ];
        }

        return $crumbs;
    }

    /**
     * Queries files directly during preview state, or triggers secondary MariaDB fallback.
     */
    public function fetchAllData(string $table): array
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

    /**
     * Lazily resolves and loads an individual formula from the 256 hash-based shards.
     */
    public function loadFormula(string $fId): ?array
    {
        if (isset($this->physicsContent['formula_registry'][$fId])) {
            return $this->physicsContent['formula_registry'][$fId];
        }

        $baseDir = PROJECT_ROOT . '/app/config/content/';
        $hexPrefix = substr(md5($fId), 0, 2);
        $shardPath = $baseDir . 'formulas/shard_' . $hexPrefix . '.json';

        if (file_exists($shardPath)) {
            $shardContent = json_decode(file_get_contents($shardPath), true) ?: [];
            if (isset($shardContent[$fId])) {
                $this->physicsContent['formula_registry'][$fId] = $shardContent[$fId];
                return $shardContent[$fId];
            }
        }

        // Fallback to check the loaded registry or look in monolithic formulas.json if it exists
        if (file_exists($baseDir . 'formulas.json')) {
            $monolithic = json_decode(file_get_contents($baseDir . 'formulas.json'), true) ?: [];
            if (isset($monolithic[$fId])) {
                $this->physicsContent['formula_registry'][$fId] = $monolithic[$fId];
                return $monolithic[$fId];
            }
        }

        return null;
    }

    /**
     * Fetches, validates cache invalidations, and maps formula identities.
     */
    public function fetchAndPrepare(string $table, string $slug): array
    {
        $content = $this->getPhysicsContent($slug);
        
        // Dynamic stale-cache fallback
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
                    $formula = $this->loadFormula($f_id);
                    if ($formula) {
                        $data['formulas'][] = $formula;
                    }
                }
            }
            return $data;
        }

        $row = $this->app->db()->fetchRow("SELECT * FROM {$table} WHERE slug = ?", [$slug]);
        if (!$row) return [];

        $data = is_object($row) && method_exists($row, 'getData') ? $row->getData() : (array) $row;
        $f_ids = !empty($data['formula_data']) ? json_decode($data['formula_data'], true) : [];
        
        $data['formulas'] = [];
        if (!empty($f_ids)) {
            foreach ($f_ids as $f_id) {
                $formula = $this->loadFormula($f_id);
                if ($formula) {
                    $data['formulas'][] = $formula;
                }
            }
        }

        return $data;
    }

    /**
     * Synchronizes a single subtopic to MariaDB.
     */
    public function syncIndividualSubtopic(string $slug, array $data): void
    {
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

    /**
     * Synchronizes a single topic hub manifest to MariaDB.
     */
    public function syncIndividualTopic(string $slug, array $data): void
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
     * Synchronizes all subtopic shards and topic hubs into the database.
     */
    public function performSync(): void
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
                [$slug, $t['title'], $t['content'] ?? '', json_encode($t['pillars'] ?? []), $t['intro'] ?? '', json_encode($t['bridges'] ?? []), $t['field'] ?? '', $t['density'] ?? '', json_encode($t['equations'] ?? []), json_encode($t['breakdowns'] ?? []), json_encode($t['formula_ids'] ?? [])]);
        }

        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            $this->syncIndividualSubtopic($slug, $st);
        }

        // Automatically prune database orphans (e.g. subtopics deleted on disk)
        $this->pruneOrphans(false);
    }

    /**
     * Identifies and optionally prunes database subtopics that no longer exist on disk.
     * Supports dry-run auditing.
     */
    public function pruneOrphans(bool $dryRun = true): array
    {
        $this->loadAllShards();
        $content = $this->getPhysicsContent();
        $diskSlugs = array_keys($content['subtopics']);

        $dbRows = $this->app->db()->fetchAll("SELECT slug FROM subtopics");
        $dbSlugs = array_map(fn($row) => $row->slug, $dbRows);

        $orphans = array_diff($dbSlugs, $diskSlugs);

        if (empty($orphans)) {
            return [];
        }

        if (!$dryRun) {
            $placeholders = implode(',', array_fill(0, count($orphans), '?'));
            $this->app->db()->runQuery(
                "DELETE FROM subtopics WHERE slug IN ($placeholders)",
                array_values($orphans)
            );
        }

        return array_values($orphans);
    }
}

