<?php

namespace app\logic;

use flight\Engine;

class PhysicsService
{
    protected Engine $app;
    private ?array $physicsContent = null;
    private ?bool $isPreviewMode = null;
    private ?array $formulaAliases = null;
    public ?string $lastDbError = null;
    public bool $lastDbSaved = false;

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
     * Fast, hash-based synchronization of modified JSON formula shards to MariaDB.
     */
    public function syncFormulasToDatabase(): array
    {
        $registryPath = PROJECT_ROOT . '/app/config/formulas_hash_registry.json';
        $hashRegistry = [];

        if (file_exists($registryPath)) {
            $rawRegistry = file_get_contents($registryPath);
            $hashRegistry = json_decode($rawRegistry, true) ?: [];
        }

        $shardFiles = glob(PROJECT_ROOT . '/app/config/content/formulas/*/*.json');
        $shardFiles = array_merge($shardFiles, glob(PROJECT_ROOT . '/app/config/content/formulas/*.json'));

        $shardsUpdated = 0;
        $formulasSynced = 0;
        $newRegistry = [];

        foreach ($shardFiles as $filePath) {
            $relativePath = str_replace(PROJECT_ROOT . '/', '', $filePath);
            $fileContent = file_get_contents($filePath);
            $currentHash = hash('sha256', $fileContent);

            $newRegistry[$relativePath] = $currentHash;

            if (isset($hashRegistry[$relativePath]) && $hashRegistry[$relativePath] === $currentHash) {
                continue;
            }

            $shardsUpdated++;
            $data = json_decode($fileContent, true);
            if (!is_array($data)) {
                continue;
            }

            foreach ($data as $formulaId => $formula) {
                if (!is_array($formula)) {
                    continue;
                }

                try {
                    $this->app->db()->runQuery(
                        "UPDATE formulas SET title = ?, equation = ?, interpretation = ?, limits_and_boundary = ?, conceptual_definition = ?, intuitive_summary = ?, symmetry_origin = ? WHERE id = ?",
                        [
                            $formula['title'] ?? '',
                            $formula['equation'] ?? '',
                            $formula['interpretation'] ?? '',
                            $formula['limits_and_boundary'] ?? '',
                            $formula['conceptual_definition'] ?? '',
                            $formula['intuitive_summary'] ?? '',
                            $formula['symmetry_origin'] ?? '',
                            $formulaId
                        ]
                    );
                    $formulasSynced++;
                } catch (\Throwable $e) {
                    // Ignore missing database rows
                }
            }
        }

        file_put_contents($registryPath, json_encode($newRegistry, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

        return [
            'shards_checked' => count($shardFiles),
            'shards_changed' => $shardsUpdated,
            'formulas_synced' => $formulasSynced
        ];
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
            if (pathinfo($file, PATHINFO_EXTENSION) === 'json' && !in_array($file, ['categories.json', 'formulas.json', 'search_index.json', 'constants.json', 'entities.json', 'pillar_profiles.json', 'compiled_trie_regex.json', 'notation.json', 'formula_aliases.json', 'formulas_latex_index.json', 'unindexed_subcomponents.json', 'subcomponents_checkpoint.json'])) {
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
                    if (isset($formula['constraints'])) {
                        $formula['constraints'] = is_string($formula['constraints'])
                            ? (json_decode($formula['constraints'], true) ?: [])
                            : $formula['constraints'];
                    }
                    if (isset($formula['related_formula_ids'])) {
                        $formula['related_formula_ids'] = is_string($formula['related_formula_ids'])
                            ? (json_decode($formula['related_formula_ids'], true) ?: [])
                            : $formula['related_formula_ids'];
                    }
                    if (isset($formula['subcomponents'])) {
                        $formula['subcomponents'] = is_string($formula['subcomponents'])
                            ? (json_decode($formula['subcomponents'], true) ?: [])
                            : $formula['subcomponents'];
                    }
                    if (!empty($formula['equation'])) {
                        $formula['latex_source'] = $formula['equation'];
                    }
                    if (!empty($formula['equation_svg'])) {
                        $formula['equation'] = $formula['equation_svg'];
                    }
                    $formula = $this->sanitizeFormulaText($formula);
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
        $shardPaths = [
            $baseDir . 'formulas/' . $hexPrefix . '/shard_' . $hexPrefix . '.json',
            $baseDir . 'formulas/shard_' . $hexPrefix . '.json'
        ];

        foreach ($shardPaths as $shardPath) {
            if (file_exists($shardPath)) {
                $shardContent = json_decode(file_get_contents($shardPath), true) ?: [];
                if (isset($shardContent[$fId])) {
                    $formula = $this->sanitizeFormulaText($shardContent[$fId]);
                    $this->physicsContent['formula_registry'][$fId] = $formula;
                    return $formula;
                }
            }
        }

        // Fallback to check the loaded registry or look in monolithic formulas.json if it exists
        if (file_exists($baseDir . 'formulas.json')) {
            $monolithic = json_decode(file_get_contents($baseDir . 'formulas.json'), true) ?: [];
            if (isset($monolithic[$fId])) {
                $formula = $this->sanitizeFormulaText($monolithic[$fId]);
                $this->physicsContent['formula_registry'][$fId] = $formula;
                return $formula;
            }
        }

        return null;
    }

    /**
     * Atomically saves or updates a formula across:
     *  1. The target JSON hash shard (app/config/content/formulas/[xx]/shard_[xx].json)
     *  2. The MariaDB formulas table (with dynamic MathJax reset)
     *  3. The formulas_latex_index.json lookup mapping
     *
     * @param string $fId Formula ID
     * @param array $data Complete formula record data
     * @return bool True on success, false on failure
     */
    public function saveFormula(string $fId, array $data): bool
    {
        if (empty($fId) || empty($data)) {
            return false;
        }

        // 1. Sanitize equation against HTML tags and formatting leaks
        if (!empty($data['equation']) && is_string($data['equation'])) {
            $eq = $data['equation'];
            $eq = preg_replace('/<(?:strong|b)>(.*?)<\/(?:strong|b)>/i', '\\mathbf{$1}', $eq);
            $eq = preg_replace('/<(?:em|i)>(.*?)<\/(?:em|i)>/i', '\\mathit{$1}', $eq);
            $eq = strip_tags($eq);
            $data['equation'] = trim($eq);
        }

        // 2. Sanitize all prose fields against control collisions and normalize math delimiters
        $proseFields = ['conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary', 'description'];
        foreach ($proseFields as $field) {
            if (!empty($data[$field]) && is_string($data[$field])) {
                $val = $data[$field];
                $val = str_replace(["\x08ar{", "\x08\\bar{", "ar{"], '\bar{', $val);
                $val = str_replace(["\x08eta", "\x08"], ['\beta', ''], $val);
                $val = str_replace(["\x0crac", "\x0c"], ['\frac', ''], $val);
                $val = preg_replace('/[\x00-\x08\x0b\x0c\x0e-\x1f]/', '', $val);

                // Clean double backslashes before standard LaTeX macros
                $val = preg_replace('/\\\\\\\\(mathcal|mathbf|oint|iint|frac|dot|ddot|vec|hat|bar|nabla|partial|sum|int|text|sigma|tau|mu|nu|rho|lambda)/', '\\$1', $val);

                // Clean stray escaped dollars
                $val = str_replace(['\\$', '\\ $'], '$', $val);

                // Canonicalize inline bracket delimiters \( ... \) to standard $ ... $
                $val = preg_replace('/\\\\\((.*?)\\\\\)/s', '$$1$', $val);

                // Fix misplaced equals or fraction delimiters
                $val = preg_replace('/=\$\s*\\\\frac/', '= \\frac', $val);
                $val = preg_replace('/is\$\s*\\\\frac/', 'is \\frac', $val);

                // Convert literal '\n' before numbered lists or bullet items to actual newlines
                $val = preg_replace('/\\\\n(?=\s*(?:\d+\.|\*|-))/u', "\n", $val);

                $data[$field] = trim($val);
            }
        }

        // 2. Determine target JSON shard path
        $hex = substr(md5($fId), 0, 2);
        $shardDir = PROJECT_ROOT . '/app/config/content/formulas/' . $hex;
        $shardPath = $shardDir . '/shard_' . $hex . '.json';

        if (!is_dir($shardDir)) {
            mkdir($shardDir, 0755, true);
        }

        $shardData = [];
        if (file_exists($shardPath)) {
            $shardData = json_decode(file_get_contents($shardPath), true) ?: [];
        }

        // Ensure semantic_variables is an object in JSON (never empty array [])
        if (!isset($data['semantic_variables']) || !is_array($data['semantic_variables']) || empty($data['semantic_variables'])) {
            $data['semantic_variables'] = (object)[];
        }

        // Update shard array
        $shardData[$fId] = $data;

        // Sanitize all entries in shard to guarantee no neighboring formula has [] for semantic_variables
        foreach ($shardData as $key => &$entry) {
            if (is_array($entry)) {
                if (!isset($entry['semantic_variables']) || !is_array($entry['semantic_variables']) || empty($entry['semantic_variables'])) {
                    $entry['semantic_variables'] = (object)[];
                }
            }
        }
        unset($entry);

        // Save JSON shard atomically with proper formatting
        $jsonEncoded = json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        if (file_put_contents($shardPath, $jsonEncoded) === false) {
            error_log("Failed to write formula to shard: {$shardPath}");
            return false;
        }

        // 3. Update MariaDB record if database connection is available
        $this->lastDbSaved = false;
        $this->lastDbError = null;
        try {
            if ($this->app && \Flight::has('db')) {
                $db = $this->app->db();
                $existing = $db->fetchRow("SELECT id FROM formulas WHERE id = ?", [$fId]);

                $semanticVars = !empty($data['semantic_variables']) ? (is_string($data['semantic_variables']) ? $data['semantic_variables'] : json_encode($data['semantic_variables'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;
                $constraints = !empty($data['constraints']) ? (is_string($data['constraints']) ? $data['constraints'] : json_encode($data['constraints'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;
                $subcomponents = !empty($data['subcomponents']) ? (is_string($data['subcomponents']) ? $data['subcomponents'] : json_encode($data['subcomponents'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;
                $relatedIds = !empty($data['related_formula_ids']) ? (is_string($data['related_formula_ids']) ? $data['related_formula_ids'] : json_encode($data['related_formula_ids'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;

                if ($existing) {
                    $db->runQuery(
                        "UPDATE formulas SET 
                            title = ?, 
                            equation = ?, 
                            conceptual_definition = ?, 
                            intuitive_summary = ?, 
                            interpretation = ?, 
                            symmetry_origin = ?, 
                            limits_and_boundary = ?, 
                            semantic_variables = ?, 
                            parent_formula_id = ?, 
                            derivation_type = ?, 
                            subcomponents = ?, 
                            constraints = ?, 
                            related_formula_ids = ?, 
                            status = ?, 
                            unit_system = ?, 
                            equation_svg = NULL 
                        WHERE id = ?",
                        [
                            $data['title'] ?? null,
                            $data['equation'] ?? null,
                            $data['conceptual_definition'] ?? null,
                            $data['intuitive_summary'] ?? null,
                            $data['interpretation'] ?? null,
                            $data['symmetry_origin'] ?? null,
                            $data['limits_and_boundary'] ?? null,
                            $semanticVars,
                            $data['parent_formula_id'] ?? null,
                            $data['derivation_type'] ?? null,
                            $subcomponents,
                            $constraints,
                            $relatedIds,
                            $data['status'] ?? 'platinum',
                            $data['unit_system'] ?? null,
                            $fId
                        ]
                    );
                } else {
                    $db->runQuery(
                        "INSERT INTO formulas (id, title, equation, conceptual_definition, intuitive_summary, interpretation, symmetry_origin, limits_and_boundary, semantic_variables, parent_formula_id, derivation_type, subcomponents, constraints, related_formula_ids, status, unit_system, equation_svg) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                        [
                            $fId,
                            $data['title'] ?? null,
                            $data['equation'] ?? null,
                            $data['conceptual_definition'] ?? null,
                            $data['intuitive_summary'] ?? null,
                            $data['interpretation'] ?? null,
                            $data['symmetry_origin'] ?? null,
                            $data['limits_and_boundary'] ?? null,
                            $semanticVars,
                            $data['parent_formula_id'] ?? null,
                            $data['derivation_type'] ?? null,
                            $subcomponents,
                            $constraints,
                            $relatedIds,
                            $data['status'] ?? 'platinum',
                            $data['unit_system'] ?? null
                        ]
                    );
                }
                $this->lastDbSaved = true;
            } else {
                $this->lastDbError = "Database service not registered in Flight container.";
            }
        } catch (\Throwable $e) {
            $this->lastDbError = $e->getMessage();
            error_log("Database saveFormula failed for {$fId}: " . $e->getMessage());
        }

        // 4. Update formulas_latex_index.json lookup mapping
        if (!empty($data['equation'])) {
            $indexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
            $index = [];
            if (file_exists($indexFile)) {
                $index = json_decode(file_get_contents($indexFile), true) ?: [];
            }
            $normalizedKey = $this->normalizeLatex($data['equation']);
            if (!empty($normalizedKey)) {
                $index[$normalizedKey] = $fId;
                file_put_contents($indexFile, json_encode($index, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
            }
        }

        // 5. Update runtime in-memory cache
        $this->physicsContent['formula_registry'][$fId] = $data;

        return true;
    }

    /**
     * Sanitizes malformed TeX escape sequences in formula prose fields.
     */
    private function sanitizeFormulaText(array $formula): array
    {
        $fields = ['interpretation', 'limits_and_boundary', 'symmetry_origin', 'conceptual_definition', 'intuitive_summary'];
        foreach ($fields as $field) {
            if (!empty($formula[$field]) && is_string($formula[$field])) {
                $txt = $formula[$field];
                $txt = str_replace('\\backslash)', ')', $txt);
                $txt = str_replace('\\backslash', '\\', $txt);
                $formula[$field] = $txt;
            }
        }
        return $formula;
    }

    /**
     * Resolves a formula with its full parent/child hierarchy objects attached.
     */
    public function getFormulaWithHierarchy(string $fId): ?array
    {
        $formula = $this->loadFormula($fId);
        if (!$formula) {
            return null;
        }

        $formula['id'] = $fId;

        // 1. Resolve Parent Formula if present
        if (!empty($formula['parent_formula_id'])) {
            $parentId = $formula['parent_formula_id'];
            $parentObj = $this->loadFormula($parentId);

            if (!$parentObj) {
                $fallbackMap = [
                    'gauss-law-electrostatics' => 'gausss-law',
                    'schrodinger-equation' => 'time-dependent-schrodinger-equation',
                    'coulombs-law' => 'coulombs-law-vector-form-cf57b988',
                    'poissons-equation' => 'poisson-equation-for-electrostatics',
                    'maxwells-equations' => 'maxwells-equations-differential-forms-1349f485',
                    'lorentz-transformations' => 'lorentz-transformation-matrix'
                ];
                if (isset($fallbackMap[$parentId])) {
                    $parentId = $fallbackMap[$parentId];
                    $parentObj = $this->loadFormula($parentId);
                }
            }

            if ($parentObj) {
                $formula['parent_formula'] = [
                    'id' => $parentId,
                    'title' => $parentObj['title'] ?? 'Parent Formula',
                    'equation' => $parentObj['equation'] ?? '',
                    'url' => '/physics/equation-explainer?id=' . urlencode($parentId)
                ];
            }
        }

        // 2. Resolve Subcomponents if present
        if (!empty($formula['subcomponents']) && is_array($formula['subcomponents'])) {
            $resolvedChildren = [];
            foreach ($formula['subcomponents'] as $childId) {
                if (is_string($childId)) {
                    $childObj = $this->loadFormula($childId);
                    if ($childObj) {
                        $resolvedChildren[] = [
                            'id' => $childId,
                            'title' => $childObj['title'] ?? 'Subcomponent Equation',
                            'equation' => $childObj['equation'] ?? '',
                            'url' => '/physics/equation-explainer?id=' . urlencode($childId)
                        ];
                    }
                } elseif (is_array($childId) && !empty($childId['id'])) {
                    $childIdStr = $childId['id'];
                    $childObj = $this->loadFormula($childIdStr);
                    if ($childObj) {
                        $resolvedChildren[] = [
                            'id' => $childIdStr,
                            'title' => $childObj['title'] ?? ($childId['title'] ?? 'Subcomponent Equation'),
                            'equation' => $childObj['equation'] ?? ($childId['equation'] ?? ''),
                            'url' => '/physics/equation-explainer?id=' . urlencode($childIdStr)
                        ];
                    }
                }
            }
            $formula['subcomponents'] = $resolvedChildren;
        } else {
            $formula['subcomponents'] = [];
        }

        return $formula;
    }

    /**
     * Traverses the Science Knowledge Graph for a given formula ID.
     * Returns the target node, parent formula node (if derived), child derivative nodes,
     * and related formula nodes.
     */
    public function getFormulaGraph(string $formulaId): array
    {
        $formula = $this->loadFormula($formulaId);
        if (!$formula) {
            return ['node' => null, 'parent' => null, 'children' => [], 'related' => []];
        }

        $formula['id'] = $formulaId;
        $db = $this->app->db();

        $parent = null;
        if (!empty($formula['parent_formula_id'])) {
            $parent = $this->loadFormula($formula['parent_formula_id']);
            if ($parent) {
                $parent['id'] = $formula['parent_formula_id'];
            }
        }

        $children = [];
        try {
            $childRows = $db->fetchAll(
                "SELECT id, title, equation, derivation_type, constraints 
                 FROM formulas 
                 WHERE parent_formula_id = ?",
                [$formulaId]
            );
            foreach ($childRows as $row) {
                $children[] = [
                    'id' => $row['id'],
                    'title' => $row['title'],
                    'equation' => $row['equation'],
                    'derivation_type' => $row['derivation_type'],
                    'constraints' => !empty($row['constraints']) ? json_decode($row['constraints'], true) : null
                ];
            }
        } catch (\Exception $e) {
            // DB fallback
        }

        $related = [];
        $relatedIds = $formula['related_formula_ids'] ?? [];
        if (!empty($relatedIds)) {
            foreach ($relatedIds as $relId) {
                $relNode = $this->loadFormula($relId);
                if ($relNode) {
                    $related[] = [
                        'id' => $relId,
                        'title' => $relNode['title'],
                        'equation' => $relNode['equation'] ?? ''
                    ];
                }
            }
        }

        return [
            'node' => $formula,
            'parent' => $parent,
            'children' => $children,
            'related' => $related
        ];
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
        $f_ids = !empty($data['formula_data']) ? (is_string($data['formula_data']) ? json_decode($data['formula_data'], true) : $data['formula_data']) : [];
        $data['formula_ids'] = $f_ids;

        if (isset($data['parents']) && is_string($data['parents'])) {
            $data['parents'] = json_decode($data['parents'], true) ?: [];
        }

        if (isset($data['equations']) && is_string($data['equations'])) {
            $data['equations'] = json_decode($data['equations'], true) ?: [];
        }

        if (isset($data['breakdowns']) && is_string($data['breakdowns'])) {
            $data['breakdowns'] = json_decode($data['breakdowns'], true) ?: [];
        }
        
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
     * Supports differential delta syncing based on file modification timestamps.
     */
    public function performSync(bool $force = false): void
    {
        $this->loadAllShards();
        $data = $this->getPhysicsContent();
        $db = $this->app->db();
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        $lastSyncTime = file_exists($syncLock) ? filemtime($syncLock) : 0;

        // 1. Auto-provision the database tables if they do not exist
        $db->runQuery("CREATE TABLE IF NOT EXISTS topics (
            slug VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content MEDIUMTEXT,
            pillars JSON,
            intro TEXT,
            bridges JSON,
            field VARCHAR(255),
            density VARCHAR(50),
            equations JSON,
            breakdowns JSON,
            formula_data JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS subtopics (
            slug VARCHAR(255) PRIMARY KEY,
            parent_topic VARCHAR(255),
            title VARCHAR(255) NOT NULL,
            content MEDIUMTEXT NOT NULL,
            snippet TEXT,
            snippet_svg MEDIUMTEXT,
            hero_math TEXT,
            equations JSON,
            breakdowns JSON,
            formula_data JSON,
            parents JSON,
            standard VARCHAR(50) DEFAULT 'legacy',
            verification JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS formulas (
            id VARCHAR(255) PRIMARY KEY,
            parent_formula_id VARCHAR(255),
            derivation_type VARCHAR(50),
            constraints JSON,
            related_formula_ids JSON,
            subcomponents JSON,
            title VARCHAR(255) NOT NULL,
            equation MEDIUMTEXT NOT NULL,
            equation_svg MEDIUMTEXT,
            conceptual_definition TEXT,
            intuitive_summary TEXT,
            interpretation TEXT,
            symmetry_origin TEXT,
            limits_and_boundary TEXT,
            semantic_variables JSON,
            unit_system VARCHAR(50) DEFAULT 'SI',
            status VARCHAR(50) DEFAULT 'published'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN equation_svg MEDIUMTEXT AFTER equation;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN parent_formula_id VARCHAR(255) AFTER id;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN derivation_type VARCHAR(50) AFTER parent_formula_id;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN constraints JSON AFTER derivation_type;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN related_formula_ids JSON AFTER constraints;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD COLUMN subcomponents JSON AFTER related_formula_ids;");
        } catch (\Exception $e) {
            // Column already exists, ignore
        }

        // Provision FULLTEXT search indexes
        try {
            $db->runQuery("ALTER TABLE subtopics ADD FULLTEXT INDEX ft_subtopics (title, content);");
        } catch (\Exception $e) {
            // Index already exists, ignore
        }
        try {
            $db->runQuery("ALTER TABLE formulas ADD FULLTEXT INDEX ft_formulas (title, conceptual_definition, equation);");
        } catch (\Exception $e) {
            // Index already exists, ignore
        }

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

        // 4. Sync Formulas (Grouped Transactionally & Differentially)
        $formulasDir = PROJECT_ROOT . '/app/config/content/formulas/';
        $formulaFiles = array_merge(glob($formulasDir . 'shard_*.json') ?: [], glob($formulasDir . '*/shard_*.json') ?: []);
        
        $db->runQuery("START TRANSACTION");
        try {
            $diskFormulaIds = [];
            $syncedShards = 0;
            $skippedShards = 0;

            foreach ($formulaFiles as $file) {
                $isModified = $force || (filemtime($file) > $lastSyncTime);
                $content = json_decode(file_get_contents($file), true) ?: [];

                foreach ($content as $fId => $fData) {
                    $diskFormulaIds[] = $fId;

                    if ($isModified) {
                        $eq = $fData['equation'] ?? '';
                        $cleanEq = $eq;
                        $eqSvg = $fData['equation_svg'] ?? null;

                        if (strpos($eq, '<svg') === 0) {
                            $eqSvg = $eq;
                            if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                                $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                            }
                        }

                        $db->runQuery(
                            "INSERT INTO formulas (
                                id, parent_formula_id, derivation_type, constraints, related_formula_ids, subcomponents,
                                title, equation, equation_svg, conceptual_definition, intuitive_summary, 
                                interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                                unit_system, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON DUPLICATE KEY UPDATE 
                                parent_formula_id = VALUES(parent_formula_id),
                                derivation_type = VALUES(derivation_type),
                                constraints = VALUES(constraints),
                                related_formula_ids = VALUES(related_formula_ids),
                                subcomponents = VALUES(subcomponents),
                                title = VALUES(title),
                                equation = VALUES(equation),
                                equation_svg = VALUES(equation_svg),
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
                                $fData['parent_formula_id'] ?? null,
                                $fData['derivation_type'] ?? null,
                                !empty($fData['constraints']) ? json_encode($fData['constraints']) : null,
                                !empty($fData['related_formula_ids']) ? json_encode($fData['related_formula_ids']) : null,
                                !empty($fData['subcomponents']) ? json_encode($fData['subcomponents']) : null,
                                $fData['title'],
                                $cleanEq,
                                $eqSvg,
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

                if ($isModified) {
                    $syncedShards++;
                } else {
                    $skippedShards++;
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
     * Alias for searchFormulaByLatex
     */
    public function findFormulaByLatex(string $latex): ?array
    {
        return $this->searchFormulaByLatex($latex);
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

        // Secondary Fallback: Match by AST Canonical Signature
        $baseDir = PROJECT_ROOT . '/app/config/content/formulas/';
        $files = array_merge(glob($baseDir . 'shard_*.json') ?: [], glob($baseDir . '*/shard_*.json') ?: []);

        $targetCanonical = $this->canonicalizeLatex($latex);
        if (!empty($targetCanonical)) {
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
                    
                    if ($this->canonicalizeLatex($cleanEq) === $targetCanonical) {
                        $formula['id'] = $fId;
                        return $formula;
                    }
                }
            }
        }
        
        return null;
    }

    /**
     * Canonicalizes LaTeX mathematical strings to AST-level algebraic signatures.
     */
    public function canonicalizeLatex(string $latex): string
    {
        if (empty($latex)) return '';
        $clean = preg_replace('/\\\\par\b/', ' ', $latex);
        $clean = preg_replace('/\\\\left|\\\\right/', '', $clean);
        $clean = preg_replace('/\\\\quad|\\\\qquad|\\\\,/', ' ', $clean);
        $clean = preg_replace('/\\\\varepsilon(?![a-zA-Z])/', '\\epsilon', $clean);
        $clean = preg_replace('/\\\\vartheta(?![a-zA-Z])/', '\\theta', $clean);
        $clean = preg_replace('/\\\\varphi(?![a-zA-Z])/', '\\phi', $clean);
        $clean = preg_replace('/\\\\varrho(?![a-zA-Z])/', '\\rho', $clean);
        $clean = preg_replace('/\\\\varpi(?![a-zA-Z])/', '\\pi', $clean);
        $clean = preg_replace('/\\\\varsigma(?![a-zA-Z])/', '\\sigma', $clean);

        // Strip visual styling commands
        $clean = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\\{([^}]+)\\}/', '$2', $clean);
        $clean = preg_replace('/\\\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\\\[a-zA-Z]+|[a-zA-Z0-9])/', '$2', $clean);
        $clean = preg_replace('/\\\\cssId\\{[^}]+\\}\\{([^}]+)\\}/', '$1', $clean);

        // Canonicalize fractions
        $hasFraction = true;
        while ($hasFraction) {
            $next = preg_replace('/\\\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/', '($1)/($2)', $clean);
            if ($next === $clean) {
                $hasFraction = false;
            } else {
                $clean = $next;
            }
        }

        // Canonicalize vector operators
        $clean = preg_replace('/\\\\nabla\s*\\\\times/', 'curl', $clean);
        $clean = preg_replace('/\\\\nabla\s*\\\\cdot/', 'div', $clean);
        $clean = preg_replace('/\\\\nabla\^2/', 'laplacian', $clean);
        $clean = preg_replace('/\\\\nabla/', 'grad', $clean);

        // Canonicalize limits: \to 0 -> =0
        $clean = preg_replace('/\\\\to\s*0/', '=0', $clean);
        $clean = preg_replace('/\\\\rightarrow\s*0/', '=0', $clean);

        // Strip whitespace and commas
        $clean = preg_replace('/\s+/', '', $clean);
        $clean = str_replace(',', '', $clean);
        return strtolower($clean);
    }

    /**
     * Synthesizes a structured formula explanation dynamically from LaTeX AST parsing
     * when a formula is missing from pre-compiled JSON shards.
     */
    public function synthesizeFormulaExplanation(string $latex): array
    {
        if (empty($latex)) {
            return [];
        }

        $canonical = $this->canonicalizeLatex($latex);
        
        $title = "Custom Physical Relation";
        $domain = "classical_mechanics";
        $intro = "This mathematical identity represents a physical relationship between variables and differential operators.";
        $summary = "It defines how physical fields or particle states evolve and interact.";
        $interpretation = "The left-hand side of the relation establishes how spatial gradients or field variations are balanced by the right-hand side source or rate terms.";
        $symmetry = "Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance.";
        $limits = "Subject to boundary constraints where field quantities decay or approach stationary states.";

        // 1. Classical Mechanics & Force / Acceleration / Newton's Second Law
        if (strpos($canonical, 'f=m') !== false || strpos($canonical, 'f=ma') !== false || (strpos($canonical, 'f=') !== false && (strpos($canonical, 'd^2') !== false || strpos($canonical, 'dt^2') !== false))) {
            $domain = "classical_mechanics";
            $title = "Newton's Second Law of Motion (Differential Form)";
            $intro = "Relates the net vector force acting on a particle to its mass and the second time derivative of position (acceleration).";
            $summary = "The net vector force equals mass times instantaneous acceleration: \\mathbf{F} = m \\frac{d^2 \\mathbf{r}}{dt^2}.";
            $interpretation = "The differential operator \\frac{d^2 \\mathbf{r}}{dt^2} represents the instantaneous acceleration vector \\mathbf{a}. Multiplying by inertial mass $m$ determines the net force required to change the particle's state of motion.";
            $symmetry = "Galilean-invariant under constant velocity transformations; invariant under 3D spatial rotations and translations.";
            $limits = "Valid for constant-mass particles at non-relativistic speeds ($v \\ll c$) in inertial reference frames.";
        }
        // 2. Electromagnetism & Curl / Maxwell Limits
        elseif (strpos($canonical, 'curl') !== false || strpos($canonical, 'div') !== false) {
            $domain = "electromagnetism";
            if ((strpos($canonical, 'curle=0') !== false || strpos($canonical, 'curl=0') !== false) || (strpos($canonical, 'curle') !== false && strpos($canonical, 'curlb') !== false)) {
                $title = "Static Limits of Maxwell's Equations";
                $intro = "The steady-state or static limits of Maxwell's equations govern electromagnetic phenomena when charge distributions and currents are non-varying in time.";
                $summary = "Under static conditions where fields do not change over time, the electric field is irrotational (curl-free), while magnetic fields are generated purely by steady electric current density.";
                $interpretation = "In the static limit, the induced electric field from changing magnetic fields vanishes (\\nabla \\times \\mathbf{E} = 0), allowing the electric field to be represented as the gradient of a scalar electrostatic potential (\\mathbf{E} = -\\nabla V). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density (\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}).";
                $symmetry = "Originates from time-translation invariance (\\partial / \\partial t = 0) and local gauge symmetry under steady current distributions.";
                $limits = "Valid in non-radiating, low-frequency, or zero-frequency steady-state electrodynamics where inductive and displacement currents are negligible.";
            } elseif (strpos($canonical, 'curle') !== false) {
                $title = "Faraday's Law of Induction / Electric Field Curl";
                $intro = "Defines the curl of the electric field, relating rotational electric field circulation to changing magnetic fields.";
                $summary = "Changing magnetic flux generates an induced circulation in the surrounding electric field.";
                $interpretation = "The curl operator (\\nabla \\times \\mathbf{E}) measures the local vorticity or circulation of the electric field lines per unit area.";
                $symmetry = "Lorentz-covariant under relativistic transformations; invariant under spatial rotations.";
                $limits = "In the static limit (\\partial \\mathbf{B}/\\partial t = 0), the curl vanishes, reducing the field to electrostatic conservative form.";
            } elseif (strpos($canonical, 'curlb') !== false) {
                $title = "Ampère-Maxwell Law / Magnetic Field Curl";
                $intro = "Relates the spatial circulation of the magnetic field to electric current density and displacement currents.";
                $summary = "Magnetic field lines curl around moving electric charges and time-varying electric fields.";
                $interpretation = "The circulation of \\mathbf{B} around a closed loop is driven by the net current enclosed by that loop.";
                $symmetry = "Preserves gauge symmetry under electromagnetic gauge transformations.";
                $limits = "In vacuum with zero current density (\\mathbf{J}=0, \\partial \\mathbf{E}/\\partial t = 0), the curl vanishes.";
            }
        } elseif (strpos($canonical, 'delta') !== false || strpos($canonical, '\delta') !== false || strpos($latex, '\delta') !== false || strpos(strtolower($latex), 'bounded') !== false || strpos(strtolower($latex), 'field') !== false) {
            $isField = (strpos(strtolower($latex), 'field') !== false || strpos($canonical, 'phi') !== false || strpos($canonical, 'psi') !== false);
            $domain = "field_theory";
            $title = $isField ? 'Second Variation of Action in Field Theory ($\delta^2 S_{\text{field}}$)' : 'Second Variation of Action / Entropy Stability ($\delta^2 S_{\text{bounded}}$)';
            $intro = $isField
                ? 'The second variation of action in field theory, denoted as $\delta^2 S_{\text{field}}[\phi]$, represents the second-order functional derivative operator $\frac{\delta^2 S}{\delta \phi(x) \delta \phi(y)}$ acting on field perturbations $\delta \phi(x)$. It governs the local stability of classical vacuum states, soliton solutions, and cosmological background fields.'
                : 'Represents the second-order variation of action or thermodynamic entropy ($\delta^2 S$), used to establish local stability, convexity of thermodynamic potentials, and bounded oscillation modes in physical systems.';
            $summary = $isField
                ? 'The second variation of field action determines whether small field perturbations oscillate harmonically around a stable vacuum or grow exponentially due to tachyonic instability.'
                : 'A bounded second variation ($\delta^2 S \le 0$ or $|\delta^2 S| < \infty$) guarantees that small fluctuations around an equilibrium path or thermodynamic state remain stable and bounded over time.';
            $interpretation = $isField
                ? 'While setting the first variation to zero ($\delta S[\phi] = 0$) yields the classical field equations of motion (e.g., Klein-Gordon, Maxwell, or Einstein field equations), the second variation $\delta^2 S_{\text{field}}$ defines the fluctuation Hessian operator. A positive-definite second variation ($\delta^2 S_{\text{field}} > 0$) guarantees vacuum stability, whereas a negative eigenvalue ($\delta^2 S_{\text{field}} < 0$) signals a tachyonic mode leading to spontaneous symmetry breaking or vacuum decay. In quantum field theory, $\delta^2 S_{\text{field}}$ forms the inverse propagator kernel $\mathcal{D}^{-1}(x,y)$ for path-integral 1-loop quantum corrections.'
                : 'While the first variation ($\delta S = 0$) identifies stationary solutions (equations of motion or equilibrium states), the second variation ($\delta^2 S$) dictates system stability. A bounded or negative-definite second variation ensures that perturbation energies remain localized without exponential growth.';
            $symmetry = $isField
                ? 'Stemming from Hamilton\'s Principle of Stationary Action extended to continuous field degrees of freedom ($S[\phi] = \int \mathcal{L}(\phi, \partial_\mu \phi) \, d^4x$), the second variation operator preserves Poincaré spacetime invariance and gauge symmetries of the field Lagrangian.'
                : 'Derived from Hamilton\'s Principle of Least Action and the Second Law of Thermodynamics under variational field transformations.';
            $limits = $isField
                ? 'In the weak-field or linear perturbation regime ($\delta \phi \to 0$), higher-order functional derivatives $\mathcal{O}(\delta \phi^3)$ are negligible, reducing field dynamics to linear wave propagation. Under infinite spatial boundaries, field perturbations $\delta \phi(x)$ are required to satisfy square-integrable asymptotic fall-off conditions ($\delta \phi \to 0$ as $|x| \to \infty$).'
                : 'In the linear perturbation limit ($\delta S \to 0$), higher-order non-linear terms are negligible, reducing the variation to harmonic stability analysis.';
        }

        return [
            'id' => 'synthesized-' . substr(md5($latex), 0, 8),
            'title' => $title,
            'equation' => $latex,
            'conceptual_definition' => $intro,
            'intuitive_summary' => $summary,
            'interpretation' => $interpretation,
            'symmetry_origin' => $symmetry,
            'limits_and_boundary' => $limits,
            'unit_system' => 'SI',
            'status' => 'synthesized-ast'
        ];
    }

    /**
     * Normalizes LaTeX mathematical strings to ignore white spaces, styles, and braces.
     */
    public function normalizeLatex(string $latex): string
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
        $normalized = strtolower($normalized);

        // Normalize algebraic structure (commutative sorting of products and sums)
        $normalized = $this->normalizeAlgebraicStructure($normalized);

        return $normalized;
    }

    private function sortTermFactors(string $term, array $multiSymbols): string
    {
        $temp = $term;
        $factors = [];

        // 1. Extract division blocks (e.g. /2)
        $pattern = '/\/(?:[0-9]+|dtau|dtheta|dphi|dchi|deta|domega|dlambda|dpsi|ds|dt|dx|dy|dz|dr|dp|dq|df|dg|dh|dk|epsilon|theta|phi|rho|pi|sigma|tau|int|oint|iint|iiint|partial|nabla|hbar|psi|lambda|omega|gamma|mu|nu|eta|delta|beta|alpha|chi|zeta|[a-zA-Z])/';
        $temp = preg_replace_callback($pattern, function($matches) use (&$factors) {
            $factors[] = $matches[0];
            return '';
        }, $temp);

        // 2. Extract multi-character symbols (with optional exponents like ^2 or 2)
        foreach ($multiSymbols as $sym) {
            $regex = '/' . preg_quote($sym, '/') . '(?:\^[0-9]+|[0-9]+)?/';
            $temp = preg_replace_callback($regex, function($matches) use (&$factors) {
                $factors[] = $matches[0];
                return ' ';
            }, $temp);
        }

        // 3. Extract remaining single letters/variables with optional exponents (e.g. e^2, e2, c)
        $temp = preg_replace_callback('/[a-zA-Z](?:\^[0-9]+|[0-9]+)?/', function($matches) use (&$factors) {
            $factors[] = $matches[0];
            return ' ';
        }, $temp);

        // 4. Extract any remaining numbers
        $temp = preg_replace_callback('/[0-9]+/', function($matches) use (&$factors) {
            $factors[] = $matches[0];
            return ' ';
        }, $temp);

        // Sort factors alphabetically and join
        sort($factors);
        return implode('', $factors);
    }

    private function normalizeAlgebraicStructure(string $latex): string
    {
        // Split LHS and RHS by '='
        $parts = explode('=', $latex);
        $normalizedParts = [];
        
        $multiSymbols = [
            'dtau', 'dtheta', 'dphi', 'dchi', 'deta', 'domega', 'dlambda', 'dpsi', 'ds', 'dt', 'dx', 'dy', 'dz', 'dr', 'dp', 'dq', 'df', 'dg', 'dh', 'dk',
            'epsilon', 'theta', 'phi', 'rho', 'pi', 'sigma', 'tau', 'int', 'oint', 'iint', 'iiint', 
            'partial', 'nabla', 'hbar', 'psi', 'lambda', 'omega', 'gamma', 'mu', 'nu', 'eta', 'delta', 
            'beta', 'alpha', 'chi', 'zeta'
        ];

        foreach ($parts as $part) {
            // Split by '+' and '-' while keeping the operators
            $tokens = preg_split('/([+\-])/', $part, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);
            
            $currentSign = '+';
            $terms = [];
            
            foreach ($tokens as $tok) {
                if ($tok === '+' || $tok === '-') {
                    $currentSign = $tok;
                } else {
                    $sortedTerm = $this->sortTermFactors($tok, $multiSymbols);
                    if (!empty($sortedTerm)) {
                        $terms[] = [
                            'sign' => $currentSign,
                            'term' => $sortedTerm
                        ];
                    }
                    $currentSign = '+';
                }
            }
            
            // Sort terms alphabetically by the term itself (ignoring sign for sorting consistency)
            usort($terms, function($a, $b) {
                return strcmp($a['term'], $b['term']);
            });
            
            // Re-join terms
            $joined = '';
            foreach ($terms as $i => $t) {
                if ($i === 0) {
                    if ($t['sign'] === '-') {
                        $joined .= '-';
                    }
                    $joined .= $t['term'];
                } else {
                    $joined .= $t['sign'] . $t['term'];
                }
            }
            $normalizedParts[] = $joined;
        }
        
        return implode('=', $normalizedParts);
    }

    /**
     * High-Performance Search Endpoint utilizing MariaDB FULLTEXT Indexing
     * with fallback fuzzy LIKE queries and snippet highlighting.
     */
    public function searchContent(string $query, int $limit = 10): array
    {
        $cleanQuery = trim($query);
        if (empty($cleanQuery)) {
            return ['query' => '', 'total' => 0, 'results' => []];
        }

        $db = $this->app->db();
        $results = [];
        $seenSlugs = [];

        // 1. Search Subtopics (Primary Encyclopedia Articles) via MariaDB FULLTEXT / LIKE
        try {
            $maxLimit = (int)$limit;
            $rows = $db->runQuery(
                "SELECT slug, title, content, 
                        MATCH(title, content) AGAINST(? IN NATURAL LANGUAGE MODE) AS score
                 FROM subtopics 
                 WHERE MATCH(title, content) AGAINST(? IN NATURAL LANGUAGE MODE)
                 ORDER BY score DESC 
                 LIMIT {$maxLimit}",
                [$cleanQuery, $cleanQuery]
            )->fetchAll();

            if (empty($rows)) {
                $likeParam = '%' . $cleanQuery . '%';
                $rows = $db->runQuery(
                    "SELECT slug, title, content, 1.0 AS score
                     FROM subtopics
                     WHERE title LIKE ? OR content LIKE ?
                     LIMIT {$maxLimit}",
                    [$likeParam, $likeParam]
                )->fetchAll();
            }

            foreach ($rows as $row) {
                $slug = $row['slug'] ?? '';
                if (empty($slug) || isset($seenSlugs[$slug])) continue;
                $seenSlugs[$slug] = true;

                $plainContent = strip_tags($row['content'] ?? '');
                $snippet = '';
                
                $pos = stripos($plainContent, $cleanQuery);
                if ($pos !== false) {
                    $start = max(0, $pos - 40);
                    $snippet = '...' . substr($plainContent, $start, 120) . '...';
                } else {
                    $snippet = substr($plainContent, 0, 120) . '...';
                }

                $results[] = [
                    'type' => 'subtopic',
                    'slug' => $slug,
                    'title' => $row['title'],
                    'snippet' => $snippet,
                    'url' => '/physics/subtopic/' . $slug
                ];
            }
        } catch (\Throwable $e) {
            // Fallback for in-memory file-system mode
            $this->loadAllShards();
            $content = $this->getPhysicsContent();
            $allSubtopics = $content['subtopics'] ?? [];
            foreach ($allSubtopics as $slug => $st) {
                if (count($results) >= $limit) break;
                if (isset($seenSlugs[$slug])) continue;
                if (stripos($st['title'] ?? '', $cleanQuery) !== false || stripos($st['content'] ?? '', $cleanQuery) !== false) {
                    $seenSlugs[$slug] = true;
                    $results[] = [
                        'type' => 'subtopic',
                        'slug' => $slug,
                        'title' => $st['title'] ?? $slug,
                        'snippet' => substr(strip_tags($st['content'] ?? ''), 0, 120) . '...',
                        'url' => '/physics/subtopic/' . $slug
                    ];
                }
            }
        }

        // 2. Search Topics / Subject Hubs if space remains
        if (count($results) < $limit) {
            try {
                $remaining = (int)$limit - count($results);
                $topicRows = $db->runQuery(
                    "SELECT slug, title, description 
                     FROM topics 
                     WHERE title LIKE ? OR description LIKE ?
                     LIMIT {$remaining}",
                    ['%' . $cleanQuery . '%', '%' . $cleanQuery . '%']
                )->fetchAll();

                foreach ($topicRows as $tr) {
                    $results[] = [
                        'type' => 'topic',
                        'slug' => $tr['slug'],
                        'title' => $tr['title'],
                        'snippet' => substr(strip_tags($tr['description'] ?? ''), 0, 120) . '...',
                        'url' => '/physics/topic/' . $tr['slug']
                    ];
                }
            } catch (\Throwable $e) {
                // ignore
            }
        }

        // 2. Search Formulas if room available
        if (count($results) < $limit) {
            $remaining = $limit - count($results);
            try {
                $formulaRows = $db->runQuery(
                    "SELECT id, title, conceptual_definition 
                     FROM formulas 
                     WHERE title LIKE ? OR id LIKE ? OR conceptual_definition LIKE ?
                     LIMIT ?",
                    ['%' . $cleanQuery . '%', '%' . $cleanQuery . '%', '%' . $cleanQuery . '%', $remaining]
                );

                foreach ($formulaRows as $f) {
                    $results[] = [
                        'type' => 'formula',
                        'slug' => $f['id'],
                        'title' => $f['title'],
                        'snippet' => substr(strip_tags($f['conceptual_definition'] ?? ''), 0, 120) . '...',
                        'url' => '/physics/equation-explainer?id=' . $f['id']
                    ];
                }
            } catch (\Exception $e) {
                // Ignore formula fallback errors
            }
        }

        return [
            'query' => $cleanQuery,
            'total' => count($results),
            'results' => $results
        ];
    }
}

