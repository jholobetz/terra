<?php

namespace app\logic;

use flight\Engine;

class PhysicsService
{
    protected Engine $app;
    private ?array $physicsContent = null;
    private ?bool $isPreviewMode = null;
    private ?array $formulaAliases = null;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    /**
     * Clears the memory cache of physics content, forcing a reload from disk.
     */
    public function clearCache(): void
    {
        $this->physicsContent = null;
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
            if (pathinfo($file, PATHINFO_EXTENSION) === 'json' && !in_array($file, ['categories.json', 'formulas.json', 'search_index.json', 'constants.json', 'entities.json', 'pillar_profiles.json', 'compiled_trie_regex.json', 'notation.json', 'formula_aliases.json'])) {
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
        if ($this->formulaAliases === null) {
            $aliasPath = PROJECT_ROOT . '/app/config/content/formula_aliases.json';
            if (file_exists($aliasPath)) {
                $this->formulaAliases = json_decode(file_get_contents($aliasPath), true) ?: [];
            } else {
                $this->formulaAliases = [];
            }
        }
        if (isset($this->formulaAliases[$fId])) {
            $fId = $this->formulaAliases[$fId];
        }

        if (isset($this->physicsContent['formula_registry'][$fId])) {
            return $this->physicsContent['formula_registry'][$fId];
        }

        // Live Production Mode: Query MariaDB table with error fallback
        if (!$this->isPreviewActive()) {
            try {
                $row = $this->app->db()->fetchRow("SELECT * FROM formulas WHERE id = ?", [$fId]);
                if ($row) {
                    $formula = is_object($row) && method_exists($row, 'getData') ? $row->getData() : (array) $row;
                    if (isset($formula['semantic_variables'])) {
                        $formula['semantic_variables'] = is_string($formula['semantic_variables'])
                            ? (json_decode($formula['semantic_variables'], true) ?: [])
                            : $formula['semantic_variables'];
                    }
                    $this->physicsContent['formula_registry'][$fId] = $formula;
                    return $formula;
                }
            } catch (\Exception $e) {
                error_log("Database loadFormula failed, falling back to shards: " . $e->getMessage());
            }
        }

        // Development/Fallback Mode: Load from local JSON shards
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
                        $formula['id'] = $f_id;
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
        
        if (isset($data['verification']) && is_string($data['verification'])) {
            $data['verification'] = json_decode($data['verification'], true);
        }

        $data['formulas'] = [];
        if (!empty($f_ids)) {
            foreach ($f_ids as $f_id) {
                 $formula = $this->loadFormula($f_id);
                 if ($formula) {
                     $formula['id'] = $f_id;
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
            "INSERT INTO subtopics (slug, parent_topic, title, content, snippet, snippet_svg, hero_math, equations, breakdowns, formula_data, parents, standard, verification) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                standard = VALUES(standard),
                verification = VALUES(verification)",
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
                $data['standard'] ?? 'legacy',
                !empty($data['verification']) ? json_encode($data['verification']) : null
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

        // 1. Auto-provision the formulas table if it does not exist
        $db->runQuery("CREATE TABLE IF NOT EXISTS formulas (
            id VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            equation MEDIUMTEXT NOT NULL,
            conceptual_definition TEXT,
            intuitive_summary TEXT,
            interpretation TEXT,
            symmetry_origin TEXT,
            limits_and_boundary TEXT,
            semantic_variables JSON,
            unit_system VARCHAR(50) DEFAULT 'SI',
            status VARCHAR(50) DEFAULT 'published'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        // 2. Sync Topics
        foreach ($data['topics'] ?? [] as $slug => $t) {
            $db->runQuery("INSERT INTO topics (slug, title, content, pillars, intro, bridges, field, density, equations, breakdowns, formula_data) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON DUPLICATE KEY UPDATE 
                    title = VALUES(title), content = VALUES(content), pillars = VALUES(pillars), intro = VALUES(intro), 
                    bridges = VALUES(bridges), field = VALUES(field), density = VALUES(density), equations = VALUES(equations), 
                    breakdowns = VALUES(breakdowns), formula_data = VALUES(formula_data)", 
                [$slug, $t['title'], $t['content'] ?? '', json_encode($t['pillars'] ?? []), $t['intro'] ?? '', json_encode($t['bridges'] ?? []), $t['field'] ?? '', $t['density'] ?? '', json_encode($t['equations'] ?? []), json_encode($t['breakdowns'] ?? []), json_encode($t['formula_ids'] ?? [])]);
        }

        // 3. Sync Subtopics
        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            $this->syncIndividualSubtopic($slug, $st);
        }

        // 4. Sync Formulas (Grouped Transactionally for Performance)
        $formulasDir = PROJECT_ROOT . '/app/config/content/formulas/';
        $formulaFiles = glob($formulasDir . 'shard_*.json');
        
        $db->runQuery("START TRANSACTION");
        try {
            $diskFormulaIds = [];
            foreach ($formulaFiles as $file) {
                $content = json_decode(file_get_contents($file), true) ?: [];
                foreach ($content as $fId => $fData) {
                    $diskFormulaIds[] = $fId;
                    $db->runQuery(
                        "INSERT INTO formulas (
                            id, title, equation, conceptual_definition, intuitive_summary, 
                            interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                            unit_system, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON DUPLICATE KEY UPDATE 
                            title = VALUES(title),
                            equation = VALUES(equation),
                            conceptual_definition = VALUES(conceptual_definition),
                            intuitive_summary = VALUES(intuitive_summary),
                            interpretation = VALUES(interpretation),
                            symmetry_origin = VALUES(symmetry_origin),
                            limits_and_boundary = VALUES(limits_and_boundary),
                            semantic_variables = VALUES(semantic_variables),
                            unit_system = VALUES(unit_system),
                            status = VALUES(status)",
                        [
                            $fId,
                            $fData['title'],
                            $fData['equation'],
                            $fData['conceptual_definition'] ?? null,
                            $fData['intuitive_summary'] ?? null,
                            $fData['interpretation'] ?? null,
                            $fData['symmetry_origin'] ?? null,
                            $fData['limits_and_boundary'] ?? null,
                            isset($fData['semantic_variables']) ? json_encode($fData['semantic_variables']) : null,
                            $fData['unit_system'] ?? 'SI',
                            $fData['status'] ?? 'published'
                        ]
                    );
                }
            }
            
            // Prune orphaned database formulas
            $dbRows = $db->fetchAll("SELECT id FROM formulas");
            $dbFormulaIds = array_map(fn($row) => $row->id, $dbRows);
            $orphanedFormulas = array_diff($dbFormulaIds, $diskFormulaIds);
            if (!empty($orphanedFormulas)) {
                $placeholders = implode(',', array_fill(0, count($orphanedFormulas), '?'));
                $db->runQuery(
                    "DELETE FROM formulas WHERE id IN ($placeholders)",
                    array_values($orphanedFormulas)
                );
            }

            $db->runQuery("COMMIT");

            // 4a. Compile formula LaTeX index for fast lookup
            $latexIndex = [];
            foreach ($formulaFiles as $file) {
                $content = json_decode(file_get_contents($file), true) ?: [];
                foreach ($content as $fId => $fData) {
                    $eq = $fData['equation'] ?? '';
                    $cleanEq = $eq;
                    if (strpos($eq, '<svg') === 0) {
                        if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                            $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                        }
                    }
                    $normalized = $this->normalizeLatex($cleanEq);
                    if (!empty($normalized)) {
                        $latexIndex[$normalized] = $fId;
                    }
                }
            }
            file_put_contents(
                PROJECT_ROOT . '/app/config/formulas_latex_index.json',
                json_encode($latexIndex, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)
            );
        } catch (\Exception $e) {
            $db->runQuery("ROLLBACK");
            throw $e;
        }

        // 5. Automatically prune database subtopics
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

    /**
     * Finds all subtopics that reference a specific formula ID.
     */
    public function getSubtopicsByFormula(string $formulaId): array
    {
        $allSubtopics = $this->fetchAllData('subtopics');
        $matched = [];
        foreach ($allSubtopics as $subtopic) {
            $fIds = [];
            if (isset($subtopic['formula_data'])) {
                // From DB: JSON string or array
                $fIds = is_string($subtopic['formula_data']) 
                    ? (json_decode($subtopic['formula_data'], true) ?: []) 
                    : (array) $subtopic['formula_data'];
            } else if (isset($subtopic['formula_ids'])) {
                // From Shard: Array
                $fIds = $subtopic['formula_ids'];
            }
            
            if (in_array($formulaId, $fIds)) {
                $matched[] = [
                    'slug' => $subtopic['slug'] ?? '',
                    'title' => $subtopic['title'] ?? 'Untitled Subtopic'
                ];
            }
        }
        return $matched;
    }

    /**
     * Searches for a formula entry by matching its LaTeX equation.
     */
    public function searchFormulaByLatex(string $latex): ?array
    {
        $targetLatex = $this->normalizeLatex($latex);
        if (empty($targetLatex)) return null;

        // Use fast pre-compiled index lookup if available
        $indexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
        if (file_exists($indexFile)) {
            $index = json_decode(file_get_contents($indexFile), true) ?: [];
            if (isset($index[$targetLatex])) {
                $fId = $index[$targetLatex];
                $formula = $this->loadFormula($fId);
                if ($formula) {
                    $formula['id'] = $fId;
                    return $formula;
                }
            }
        }

        // Fallback to disk scan if index doesn't exist or doesn't match
        $baseDir = PROJECT_ROOT . '/app/config/content/formulas/';
        $files = glob($baseDir . 'shard_*.json');
        
        foreach ($files as $file) {
            $content = json_decode(file_get_contents($file), true) ?: [];
            foreach ($content as $fId => $formula) {
                $eq = $formula['equation'] ?? '';
                $cleanEq = $eq;
                if (strpos($eq, '<svg') === 0) {
                    if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                        $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                    }
                }
                
                if ($this->normalizeLatex($cleanEq) === $targetLatex) {
                    $formula['id'] = $fId;
                    return $formula;
                }
            }
        }
        
        return null;
    }

    /**
     * Normalizes LaTeX mathematical strings to ignore white spaces, styles, and braces.
     */
    private function normalizeLatex(string $latex): string
    {
        $normalized = $latex;
        $normalized = preg_replace('/\\\\varepsilon(?![a-zA-Z])/', '\\epsilon', $normalized);
        $normalized = preg_replace('/\\\\vartheta(?![a-zA-Z])/', '\\theta', $normalized);
        $normalized = preg_replace('/\\\\varphi(?![a-zA-Z])/', '\\phi', $normalized);
        $normalized = preg_replace('/\\\\varrho(?![a-zA-Z])/', '\\rho', $normalized);
        $normalized = preg_replace('/\\\\varpi(?![a-zA-Z])/', '\\pi', $normalized);
        $normalized = preg_replace('/\\\\varsigma(?![a-zA-Z])/', '\\sigma', $normalized);
        // Strip delimiters
        $normalized = preg_replace('/^\\\\\\(/', '', $normalized);
        $normalized = preg_replace('/\\\\\\)$/', '', $normalized);
        $normalized = preg_replace('/^\\\\\\[/', '', $normalized);
        $normalized = preg_replace('/\\\\\\]$/', '', $normalized);
        $normalized = preg_replace('/^\$\$/', '', $normalized);
        $normalized = preg_replace('/\$\$$/', '', $normalized);
        $normalized = preg_replace('/^\$/', '', $normalized);
        $normalized = preg_replace('/\$$/', '', $normalized);
        
        // Strip visual styling commands like \vec, \mathbf, \hat, \mathrm, \cssId
        $normalized = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\\{([^}]+)\\}/', '$2', $normalized);
        $normalized = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\\\[a-zA-Z]+|[a-zA-Z0-9])/', '$2', $normalized);
        
        // Strip MathJax \cssId{...}{...} wraps to compare only pure math
        $normalized = preg_replace('/\\\\cssId\\{[^}]+\\}\\{([^}]+)\\}/', '$1', $normalized);
        
        // Canonicalize LaTeX fraction commands: \frac{A}{B} -> A/B
        $hasFraction = true;
        while ($hasFraction) {
            $next = preg_replace('/\\\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/', '$1/$2', $normalized);
            if ($next === $normalized) {
                $hasFraction = false;
            } else {
                $normalized = $next;
            }
        }

        // Strip subscripts for robust comparison: e.g. _{ext} -> "", _0 -> ""
        $normalized = preg_replace('/_\{[^}]+\}/', '', $normalized);
        $normalized = preg_replace('/_[a-zA-Z0-9]/', '', $normalized);

        // Strip whitespaces, backslashes, and braces
        $normalized = preg_replace('/[^a-zA-Z0-9_\\^\\-=+\\/*()\\[\\]<>\.,;?]/', '', $normalized);
        
        return strtolower($normalized);
    }
}

