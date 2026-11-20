<?php

namespace app\logic;

use flight\Engine;

require_once __DIR__ . '/AuthService.php';
require_once __DIR__ . '/LatexSanitizer.php';
require_once __DIR__ . '/ShardSyncService.php';

class PhysicsService
{
    protected Engine $app;
    private LatexSanitizer $sanitizer;
    private ShardSyncService $syncService;
    private ?array $physicsContent = null;
    private ?array $notationCache = null;
    private ?bool $isPreviewMode = null;
    private ?array $formulaAliases = null;
    public ?string $lastDbError = null;
    public bool $lastDbSaved = false;

    public function __construct(Engine $app)
    {
        $this->app = $app;
        $this->sanitizer = new LatexSanitizer();
        $this->syncService = new ShardSyncService($app, $this);
    }

    /**
     * Clears the memory cache of physics content, forcing a reload from disk.
     */
    public function clearCache(): void
    {
        $this->physicsContent = null;
        $this->notationCache = null;
    }

    /**
     * Fast, hash-based transactional upsert of modified JSON formula shards to MariaDB.
     */
    public function syncFormulasToDatabase(bool $force = false): array
    {
        return $this->syncService->syncFormulasToDatabase($force);
    }

    /**
     * Toggles or queries the active preview state.
     * Restricted to local developer studio or explicit CLI setPreviewMode(true)
     * so anonymous visitors cannot bypass MariaDB and HTML disk caches via ?preview=1.
     */
    public function isPreviewActive(): bool
    {
        if ($this->isPreviewMode !== null) {
            return $this->isPreviewMode;
        }

        $auth = new AuthService();
        if (!$auth->isLocalDevStudio()) {
            return false;
        }

        $previewQuery = $this->app->request()->query->preview ?? ($_GET['preview'] ?? null);
        $buildMode = $this->app->request()->query->build_mode ?? ($_GET['build_mode'] ?? null);

        if ($previewQuery !== null || $buildMode !== null) {
            return ($previewQuery === '1' || $buildMode === '1');
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
                // notation.json is lazily loaded on-demand via getNotation()
                $simPath = PROJECT_ROOT . '/app/config/simulations.json';
                if (file_exists($simPath)) {
                    $this->physicsContent['simulations'] = json_decode(file_get_contents($simPath), true) ?: [];
                }
            }
        }

        if ($targetSlug) {
            $this->loadShardForSlug($targetSlug);
        }

        return $this->physicsContent;
    }

    /**
     * Lazily loads and memoizes the notation and fundamental constants registry.
     */
    public function getNotation(): array
    {
        if ($this->notationCache === null) {
            $notationPath = PROJECT_ROOT . '/app/config/content/notation.json';
            $this->notationCache = file_exists($notationPath)
                ? (json_decode(file_get_contents($notationPath), true) ?: [])
                : [];
            if ($this->physicsContent !== null) {
                $this->physicsContent['notation'] = $this->notationCache;
            }
        }

        return $this->notationCache;
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
                $topicData = $this->applyHubManifestOverlay($slug, $topicData);
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

        // Load Main Topic Shards (with authoritative hub_manifests/*.json overlay)
        foreach ($this->physicsContent['topics'] as $slug => $meta) {
            if (isset($meta['shard'])) {
                $shardPath = $baseDir . $meta['shard'];
                if (file_exists($shardPath)) {
                    $topicData = json_decode(file_get_contents($shardPath), true) ?: [];
                    $topicData = $this->applyHubManifestOverlay((string)$slug, $topicData);
                    $this->physicsContent['topics'][$slug] = array_merge($this->physicsContent['topics'][$slug], $topicData);
                }
            }
        }

        // Load Canonical Subtopic Shards (Explicit Allowlist)
        $subtopicShards = [
            'astrophysics.json',
            'classical-mechanics.json',
            'condensed-matter.json',
            'electromagnetism.json',
            'fluids-nonlinear.json',
            'legacy-orphans.json',
            'mathematical-methods.json',
            'philosophy-of-physics.json',
            'quantum-physics.json',
            'relativity.json',
            'standard-model.json',
            'theoretical-physics.json',
            'thermodynamics-statistical-mechanics.json'
        ];
        foreach ($subtopicShards as $file) {
            if (file_exists($baseDir . $file)) {
                $shard = json_decode(file_get_contents($baseDir . $file), true) ?: [];
                if (is_array($shard)) {
                    $this->physicsContent['subtopics'] = array_merge($this->physicsContent['subtopics'], $shard);
                }
            }
        }
    }

    /**
     * Overlays authoritative hub_manifests/{$slug}.json pillars & metadata onto a topic hub shard
     * so production cli_sync.php and offline/preview renders never drift from hub_manifests/.
     */
    private function applyHubManifestOverlay(string $slug, array $topicData): array
    {
        $manifestPath = PROJECT_ROOT . '/hub_manifests/' . $slug . '.json';
        if (!file_exists($manifestPath)) {
            return $topicData;
        }
        $manifest = json_decode((string)file_get_contents($manifestPath), true);
        if (!is_array($manifest)) {
            return $topicData;
        }

        if (!empty($manifest['title'])) {
            $topicData['title'] = $manifest['title'];
        }
        if (!empty($manifest['pillars']) && is_array($manifest['pillars'])) {
            $topicData['pillars'] = $manifest['pillars'];
        }
        $meta = is_array($manifest['metadata'] ?? null) ? $manifest['metadata'] : [];
        if (!empty($meta['intro'])) {
            $topicData['intro'] = $meta['intro'];
        }
        if (!empty($meta['field'])) {
            $topicData['field'] = $meta['field'];
        }
        if (!empty($meta['density'])) {
            $topicData['density'] = $meta['density'];
        }
        if (!empty($meta['bridges']) && is_array($meta['bridges'])) {
            $topicData['bridges'] = $meta['bridges'];
        }

        return $topicData;
    }

    /**
     * Resolves related subtopics deterministically using 100% Git-tracked manifold topology:
     *   1. Explicit outgoing prose cross-links (<a href="/physics/subtopic/...">)
     *   2. Direct parent/child or sibling parent lineage
     *   3. Shared formula_ids and search_index concept tokens
     *   4. Guaranteed cross-pillar bridge diversity ("Describing How It All Connects")
     *
     * Used identically by both subtopic.php (static HTML cache) and /physics/api/related-subtopics/@slug.
     */
    public function getRelatedTopics(string $currentSlug, int $limit = 3): array
    {
        if ($limit < 1 || $currentSlug === '') {
            return [];
        }

        $content = $this->getPhysicsContent($currentSlug);
        $index = $content['search_index'] ?? [];
        $topics = $content['topics'] ?? [];

        $currentNode = $content['subtopics'][$currentSlug] ?? null;
        if ($currentNode === null && !isset($index[$currentSlug])) {
            $fetched = $this->fetchAndPrepare('subtopics', $currentSlug);
            if (!empty($fetched) && is_array($fetched)) {
                $currentNode = $fetched;
            }
        }

        if ($currentNode === null && !isset($index[$currentSlug])) {
            return [];
        }

        // 1. Outgoing topological prose links from current article HTML
        $outgoingMap = [];
        $htmlContent = (string)($currentNode['content'] ?? '');
        if ($htmlContent !== '' && preg_match_all('~/physics/subtopic/([a-z0-9-]+)~', $htmlContent, $matches)) {
            foreach ($matches[1] as $linkedSlug) {
                if ($linkedSlug !== $currentSlug) {
                    $outgoingMap[$linkedSlug] = true;
                }
            }
        }

        // 2. Parent lineage lookup map
        $rawParents = $currentNode['parents'] ?? ($index[$currentSlug]['p'] ?? []);
        if (is_string($rawParents)) {
            $rawParents = json_decode($rawParents, true) ?: [$rawParents];
        }
        $currentParentMap = [];
        foreach ((array)$rawParents as $p) {
            if (is_string($p) && $p !== '') {
                $currentParentMap[$p] = true;
            }
        }

        // 3. Keyword & normalized formula_id lookup map (works even before search_index rebuild)
        $currentKeywordMap = [];
        foreach ((array)($index[$currentSlug]['k'] ?? []) as $kw) {
            if (is_string($kw) && $kw !== '') {
                $currentKeywordMap[$kw] = true;
            }
        }
        foreach ((array)($currentNode['formula_ids'] ?? []) as $fid) {
            if (is_string($fid) && $fid !== '') {
                $currentKeywordMap[str_replace('-', ' ', strtolower($fid))] = true;
            }
        }

        $currentShard = $this->resolveLogicalShard($currentSlug, $index, $topics);

        // Candidate pool: all search_index nodes + any brand-new outgoing linked slugs
        $candidateSlugs = array_keys($index);
        foreach (array_keys($outgoingMap) as $outSlug) {
            if (!isset($index[$outSlug])) {
                $candidateSlugs[] = $outSlug;
            }
        }

        $scored = [];
        foreach ($candidateSlugs as $slug) {
            if ($slug === $currentSlug) {
                continue;
            }

            $data = $index[$slug] ?? [];
            $score = 0.0;

            if (isset($outgoingMap[$slug])) {
                $score += 10.0;
            }

            $otherParents = (array)($data['p'] ?? []);
            if (isset($currentParentMap[$slug]) || in_array($currentSlug, $otherParents, true)) {
                $score += 8.0;
            } else {
                foreach ($otherParents as $op) {
                    if (is_string($op) && isset($currentParentMap[$op])) {
                        $score += 6.0;
                        break;
                    }
                }
            }

            if (!empty($currentKeywordMap) && !empty($data['k'])) {
                $overlap = 0;
                foreach ($data['k'] as $okw) {
                    if (is_string($okw) && isset($currentKeywordMap[$okw])) {
                        $overlap++;
                    }
                }
                if ($overlap > 0) {
                    $score += $overlap * 1.5;
                }
            }

            if ($score <= 0.0) {
                continue;
            }

            if (str_ends_with($slug, '-overview')) {
                $score -= 6.0;
            }

            if ($score > 0.0) {
                $scored[] = [
                    'slug' => $slug,
                    'score' => $score,
                    'shard' => $this->resolveLogicalShard($slug, $index, $topics),
                ];
            }
        }

        if (empty($scored)) {
            return [];
        }

        usort($scored, static function (array $a, array $b): int {
            $cmp = $b['score'] <=> $a['score'];
            return $cmp !== 0 ? $cmp : strcmp($a['slug'], $b['slug']);
        });

        $selected = array_slice($scored, 0, $limit);

        // 4. Cross-pillar bridge guarantee: ensure at least 1 cross-domain bridge when limit >= 2
        if ($limit >= 2 && count($selected) === $limit && $currentShard !== '') {
            $hasBridge = false;
            foreach ($selected as $item) {
                if ($item['shard'] !== '' && $item['shard'] !== $currentShard) {
                    $hasBridge = true;
                    break;
                }
            }
            if (!$hasBridge) {
                $totalCandidates = count($scored);
                for ($i = $limit; $i < $totalCandidates; $i++) {
                    $cand = $scored[$i];
                    if ($cand['shard'] !== '' && $cand['shard'] !== $currentShard && $cand['score'] >= 6.0) {
                        $selected[$limit - 1] = $cand;
                        break;
                    }
                }
            }
        }

        // 5. Lazily enrich only the winning slugs with domain titles and clean physical snippets
        $results = [];
        foreach ($selected as $item) {
            $rSlug = $item['slug'];
            $rShard = $item['shard'];
            $this->loadShardForSlug($rSlug);
            $winnerNode = $this->physicsContent['subtopics'][$rSlug] ?? null;
            if ($winnerNode === null) {
                $fetchedWinner = $this->fetchAndPrepare('subtopics', $rSlug);
                if (!empty($fetchedWinner) && is_array($fetchedWinner)) {
                    $winnerNode = $fetchedWinner;
                }
            }

            $title = (string)($winnerNode['title'] ?? ($index[$rSlug]['t'] ?? $rSlug));
            $domain = $this->resolveShardDomainTitle($rShard, $topics);
            $snippet = $this->extractCleanSubtopicSnippet(is_array($winnerNode) ? $winnerNode : []);
            $isBridge = ($rShard !== '' && $currentShard !== '' && $rShard !== $currentShard);

            $results[] = [
                'slug' => $rSlug,
                'title' => $title,
                'domain' => $domain,
                'url' => '/physics/subtopic/' . $rSlug,
                'snippet' => $snippet,
                'is_bridge' => $isBridge,
            ];
        }

        return $results;
    }

    /**
     * Resolves a subtopic's logical primary pillar shard (walking parent links for legacy-orphans.json).
     */
    private function resolveLogicalShard(string $slug, array $index, array $topics, array $seen = []): string
    {
        if (isset($seen[$slug])) {
            return '';
        }
        $seen[$slug] = true;

        if (isset($topics[$slug])) {
            return $slug . '.json';
        }

        $entry = $index[$slug] ?? [];
        $shard = (string)($entry['s'] ?? '');
        if ($shard !== '' && $shard !== 'legacy-orphans.json') {
            return $shard;
        }

        foreach ((array)($entry['p'] ?? []) as $parentSlug) {
            if (is_string($parentSlug) && $parentSlug !== '') {
                $resolved = $this->resolveLogicalShard($parentSlug, $index, $topics, $seen);
                if ($resolved !== '' && $resolved !== 'legacy-orphans.json') {
                    return $resolved;
                }
            }
        }

        return $shard;
    }

    /**
     * Maps a primary content shard filename (e.g. 'astrophysics.json') to its canonical Pillar title.
     */
    private function resolveShardDomainTitle(string $shardFile, array $topics): string
    {
        if ($shardFile === '') {
            return 'Physics';
        }
        $stem = basename($shardFile, '.json');
        if (isset($topics[$stem]['title']) && is_string($topics[$stem]['title'])) {
            return $topics[$stem]['title'];
        }
        if ($stem === 'legacy-orphans') {
            return 'Foundational Physics';
        }
        return ucwords(str_replace('-', ' ', $stem));
    }

    /**
     * Extracts a clean, plain-text summary snippet for related-subtopic cards.
     */
    private function extractCleanSubtopicSnippet(array $node, int $maxChars = 165): string
    {
        $snippet = trim((string)($node['snippet'] ?? ''));
        if ($snippet === '' && !empty($node['content'])) {
            $raw = (string)$node['content'];
            if (preg_match('~<p[^>]*>(.*?)</p>~is', $raw, $m)) {
                $raw = $m[1];
            }
            $raw = preg_replace('~<svg\b[^>]*>.*?</svg>~is', '', $raw) ?? $raw;
            $snippet = trim(preg_replace('/\s+/', ' ', strip_tags($raw)) ?? '');
        }

        if ($snippet === '') {
            return 'Explore governing principles, mathematical derivations, and topological connections.';
        }

        if (mb_strlen($snippet, 'UTF-8') > $maxChars) {
            $cut = mb_substr($snippet, 0, $maxChars, 'UTF-8');
            $lastSpace = mb_strrpos($cut, ' ', 0, 'UTF-8');
            if ($lastSpace !== false && $lastSpace > (int)($maxChars * 0.6)) {
                $cut = mb_substr($cut, 0, $lastSpace, 'UTF-8');
            }
            $snippet = rtrim($cut, " \t\n\r\0\x0B,.;:-") . '…';
        }

        return $snippet;
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
        try {
            return $this->app->db()->fetchAll("SELECT * FROM {$table} ORDER BY id ASC");
        } catch (\Throwable $e) {
            $this->loadAllShards();
            $content = $this->getPhysicsContent();
            $list = [];
            foreach ($content[$table] ?? [] as $slug => $data) {
                $data['slug'] = $slug;
                $list[] = $data;
            }
            return $list;
        }
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
                    foreach (array_keys($formula) as $rawKey) {
                        if (is_int($rawKey) || ctype_digit((string) $rawKey)) {
                            unset($formula[$rawKey]);
                        }
                    }
                    if (!empty($formula)) {
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
                        $hasStepsCol = array_key_exists('derivation_steps', $formula);
                        $hasCasCol = array_key_exists('cas_validation', $formula);
                        $hasEnrichedCols = array_key_exists('description', $formula)
                            && array_key_exists('category', $formula)
                            && array_key_exists('lineage_confidence', $formula)
                            && array_key_exists('record_type', $formula)
                            && array_key_exists('equation_family', $formula);

                        if (isset($formula['derivation_steps'])) {
                            $formula['derivation_steps'] = is_string($formula['derivation_steps'])
                                ? (json_decode($formula['derivation_steps'], true) ?: [])
                                : $formula['derivation_steps'];
                        }
                        if (isset($formula['cas_validation'])) {
                            $formula['cas_validation'] = is_string($formula['cas_validation'])
                                ? (json_decode($formula['cas_validation'], true) ?: null)
                                : $formula['cas_validation'];
                        }
                        // Dual-Layer Schema Resilience: Only read the Git shard from disk if the MariaDB table
                        // schema has not yet been migrated to include the full enriched column set.
                        if (!$hasStepsCol || !$hasCasCol || !$hasEnrichedCols) {
                            $hexPrefix = substr(md5($fId), 0, 2);
                            $shardFile = PROJECT_ROOT . '/app/config/content/formulas/' . $hexPrefix . '/shard_' . $hexPrefix . '.json';
                            if (file_exists($shardFile)) {
                                $rawShard = json_decode(file_get_contents($shardFile), true);
                                if (!$hasStepsCol && !empty($rawShard[$fId]['derivation_steps'])) {
                                    $formula['derivation_steps'] = $rawShard[$fId]['derivation_steps'];
                                }
                                if (empty($formula['derivation_type']) && !empty($rawShard[$fId]['derivation_type'])) {
                                    $formula['derivation_type'] = $rawShard[$fId]['derivation_type'];
                                }
                                if (!$hasCasCol && !empty($rawShard[$fId]['cas_validation'])) {
                                    $formula['cas_validation'] = $rawShard[$fId]['cas_validation'];
                                }
                                foreach (['description', 'category', 'lineage_confidence', 'record_type', 'equation_family'] as $enrichedField) {
                                    if (!array_key_exists($enrichedField, $formula) && isset($rawShard[$fId][$enrichedField])) {
                                        $formula[$enrichedField] = $rawShard[$fId][$enrichedField];
                                    }
                                }
                            }
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
                }
            } catch (\Throwable $e) {
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
                    $formula = $shardContent[$fId];
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

        // Strip any numeric keys (e.g. from PDO::FETCH_BOTH) so they never leak into shards
        foreach (array_keys($data) as $rawKey) {
            if (is_int($rawKey) || ctype_digit((string) $rawKey)) {
                unset($data[$rawKey]);
            }
        }

        // 1. Sanitize equation against HTML tags and formatting leaks
        if (!empty($data['equation']) && is_string($data['equation'])) {
            $data['equation'] = $this->sanitizer->sanitizeEquation($data['equation']);
        }

        // 2. Sanitize all prose fields against control collisions and normalize math delimiters
        $data = $this->sanitizer->sanitizeProseFields($data);

        // 2. Determine target JSON shard path
        $hex = substr(md5($fId), 0, 2);
        $shardDir = PROJECT_ROOT . '/app/config/content/formulas/' . $hex;
        $shardPath = $shardDir . '/shard_' . $hex . '.json';

        if (!is_dir($shardDir)) {
            mkdir($shardDir, 0755, true);
        }

        $previousEquation = '';
        $jsonFlags = JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE;
        $jsonEncoded = $this->updateJsonFileLocked($shardPath, function (array $shardData) use ($fId, &$data, &$previousEquation) {
            $previousEquation = $shardData[$fId]['equation'] ?? '';
            // Preserve existing cas_validation if not explicitly supplied and equation is unchanged
            if (!isset($data['cas_validation']) && isset($shardData[$fId]['cas_validation'])) {
                $oldEq = $shardData[$fId]['equation'] ?? '';
                $newEq = $data['equation'] ?? '';
                if ($oldEq === $newEq) {
                    $data['cas_validation'] = $shardData[$fId]['cas_validation'];
                }
            }

            // Preserve enriched metadata fields from existing shard entry on partial updates
            foreach (['category', 'record_type', 'lineage_confidence', 'equation_family', 'description'] as $metaField) {
                if (empty($data[$metaField]) && !empty($shardData[$fId][$metaField])) {
                    $data[$metaField] = $shardData[$fId][$metaField];
                }
            }
            if (empty($data['record_type'])) {
                $data['record_type'] = str_contains($data['equation'] ?? '', '=') ? 'equation' : 'symbol_or_term';
            }
            if (empty($data['lineage_confidence'])) {
                $data['lineage_confidence'] = empty($data['parent_formula_id']) ? 'root_axiom' : 'curated';
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
            return $shardData;
        }, $jsonFlags);

        if ($jsonEncoded === null) {
            error_log("Failed to write formula to shard: {$shardPath}");
            return false;
        }

        // Automatically synchronize the SHA-256 hash registry for this shard under LOCK_EX
        $registryPath = PROJECT_ROOT . '/app/config/formulas_hash_registry.json';
        if (file_exists($registryPath)) {
            $relativePath = str_replace(PROJECT_ROOT . '/', '', $shardPath);
            $shardHash = hash('sha256', $jsonEncoded);
            $this->updateJsonFileLocked($registryPath, function (array $reg) use ($relativePath, $shardHash) {
                $reg[$relativePath] = $shardHash;
                return $reg;
            }, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
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
                $derivationSteps = !empty($data['derivation_steps']) ? (is_string($data['derivation_steps']) ? $data['derivation_steps'] : json_encode($data['derivation_steps'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;
                $casValidation = !empty($data['cas_validation']) ? (is_string($data['cas_validation']) ? $data['cas_validation'] : json_encode($data['cas_validation'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;
                $relatedIds = !empty($data['related_formula_ids']) ? (is_string($data['related_formula_ids']) ? $data['related_formula_ids'] : json_encode($data['related_formula_ids'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)) : null;

                if ($existing) {
                    try {
                        $db->runQuery(
                            "UPDATE formulas SET 
                                title = ?, 
                                category = ?, 
                                record_type = ?, 
                                equation_family = ?, 
                                equation = ?, 
                                description = ?, 
                                conceptual_definition = ?, 
                                intuitive_summary = ?, 
                                interpretation = ?, 
                                symmetry_origin = ?, 
                                limits_and_boundary = ?, 
                                semantic_variables = ?, 
                                parent_formula_id = ?, 
                                derivation_type = ?, 
                                lineage_confidence = ?, 
                                subcomponents = ?, 
                                derivation_steps = ?, 
                                cas_validation = ?, 
                                constraints = ?, 
                                related_formula_ids = ?, 
                                status = ?, 
                                unit_system = ?, 
                                equation_svg = NULL 
                            WHERE id = ?",
                            [
                                $data['title'] ?? null,
                                $data['category'] ?? null,
                                $data['record_type'] ?? null,
                                $data['equation_family'] ?? null,
                                $data['equation'] ?? null,
                                $data['description'] ?? null,
                                $data['conceptual_definition'] ?? null,
                                $data['intuitive_summary'] ?? null,
                                $data['interpretation'] ?? null,
                                $data['symmetry_origin'] ?? null,
                                $data['limits_and_boundary'] ?? null,
                                $semanticVars,
                                $data['parent_formula_id'] ?? null,
                                $data['derivation_type'] ?? null,
                                $data['lineage_confidence'] ?? null,
                                $subcomponents,
                                $derivationSteps,
                                $casValidation,
                                $constraints,
                                $relatedIds,
                                $data['status'] ?? 'platinum',
                                $data['unit_system'] ?? null,
                                $fId
                            ]
                        );
                    } catch (\Throwable $colErr) {
                        // Fallback in case schema migration has not run yet
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
                    }
                } else {
                    try {
                        $db->runQuery(
                            "INSERT INTO formulas (id, title, category, record_type, equation_family, equation, description, conceptual_definition, intuitive_summary, interpretation, symmetry_origin, limits_and_boundary, semantic_variables, parent_formula_id, derivation_type, lineage_confidence, subcomponents, derivation_steps, cas_validation, constraints, related_formula_ids, status, unit_system, equation_svg) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)",
                            [
                                $fId,
                                $data['title'] ?? null,
                                $data['category'] ?? null,
                                $data['record_type'] ?? null,
                                $data['equation_family'] ?? null,
                                $data['equation'] ?? null,
                                $data['description'] ?? null,
                                $data['conceptual_definition'] ?? null,
                                $data['intuitive_summary'] ?? null,
                                $data['interpretation'] ?? null,
                                $data['symmetry_origin'] ?? null,
                                $data['limits_and_boundary'] ?? null,
                                $semanticVars,
                                $data['parent_formula_id'] ?? null,
                                $data['derivation_type'] ?? null,
                                $data['lineage_confidence'] ?? null,
                                $subcomponents,
                                $derivationSteps,
                                $casValidation,
                                $constraints,
                                $relatedIds,
                                $data['status'] ?? 'platinum',
                                $data['unit_system'] ?? null
                            ]
                        );
                    } catch (\Throwable $colErr) {
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
                }
                $this->lastDbSaved = true;
            } else {
                $this->lastDbError = "Database service not registered in Flight container.";
            }
        } catch (\Throwable $e) {
            $this->lastDbError = $e->getMessage();
            error_log("Database saveFormula failed for {$fId}: " . $e->getMessage());
        }

        // 4. Update formulas_latex_index.json lookup mapping under LOCK_EX
        if (!empty($data['equation'])) {
            $normalizedKey = $this->normalizeLatex($data['equation']);
            $oldNormalizedKey = ($previousEquation !== '' && $previousEquation !== $data['equation'])
                ? $this->normalizeLatex($previousEquation)
                : '';
            if (!empty($normalizedKey)) {
                $indexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
                $this->updateJsonFileLocked($indexFile, function (array $index) use ($normalizedKey, $oldNormalizedKey, $fId) {
                    if ($oldNormalizedKey !== '' && $oldNormalizedKey !== $normalizedKey && ($index[$oldNormalizedKey] ?? null) === $fId) {
                        unset($index[$oldNormalizedKey]);
                    }
                    $index[$normalizedKey] = $fId;
                    return $index;
                }, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
            }
        }

        // 5. Update runtime in-memory cache
        $this->physicsContent['formula_registry'][$fId] = $data;

        return true;
    }

    /**
     * Atomically reads, mutates, and writes a JSON map file under an exclusive advisory lock (LOCK_EX).
     * Returns the encoded JSON string on success or null on failure.
     */
    private function updateJsonFileLocked(string $filePath, callable $mutator, int $jsonFlags = JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE): ?string
    {
        $fp = @fopen($filePath, 'c+');
        if ($fp === false) {
            return null;
        }
        if (!flock($fp, LOCK_EX)) {
            fclose($fp);
            return null;
        }

        rewind($fp);
        $raw = stream_get_contents($fp);
        $decoded = ($raw !== false && $raw !== '') ? (json_decode($raw, true) ?: []) : [];
        if (!is_array($decoded)) {
            $decoded = [];
        }

        $updated = $mutator($decoded);
        $encoded = json_encode($updated, $jsonFlags);
        if ($encoded === false) {
            flock($fp, LOCK_UN);
            fclose($fp);
            return null;
        }

        ftruncate($fp, 0);
        rewind($fp);
        $written = fwrite($fp, $encoded);
        fflush($fp);
        flock($fp, LOCK_UN);
        fclose($fp);

        return ($written === false) ? null : $encoded;
    }

    /**
     * Sanitizes malformed TeX escape sequences in formula prose fields.
     */
    private function sanitizeFormulaText(array $formula): array
    {
        return $this->sanitizer->sanitizeFormulaText($formula);
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
                    'lineage_confidence' => $parentObj['lineage_confidence'] ?? null,
                    'record_type' => $parentObj['record_type'] ?? null,
                    'url' => '/physics/equation-explainer?id=' . urlencode($parentId)
                ];

                // 1b. Resolve Co-Derived Siblings & Parallel Family Equations
                $siblings = [];
                $seenSibIds = [$fId => true, $parentId => true];
                $parentSubs = $parentObj['subcomponents'] ?? [];
                if (is_array($parentSubs)) {
                    foreach ($parentSubs as $sibItem) {
                        $sibId = is_string($sibItem) ? $sibItem : ($sibItem['id'] ?? '');
                        if (!$sibId || isset($seenSibIds[$sibId])) continue;
                        $sibObj = $this->loadFormula($sibId);
                        if ($sibObj) {
                            $seenSibIds[$sibId] = true;
                            $siblings[] = [
                                'id' => $sibId,
                                'title' => $sibObj['title'] ?? 'Co-Derived Equation',
                                'equation' => $sibObj['equation'] ?? '',
                                'derivation_type' => 'CO_DERIVED_SIBLING',
                                'lineage_confidence' => $sibObj['lineage_confidence'] ?? null,
                                'record_type' => $sibObj['record_type'] ?? null,
                                'url' => '/physics/equation-explainer?id=' . urlencode($sibId)
                            ];
                        }
                        if (count($siblings) >= 8) break;
                    }
                }

                // If direct parent has few other children, include parallel branches from grandparent
                if (count($siblings) < 6 && !empty($parentObj['parent_formula_id'])) {
                    $gpId = $parentObj['parent_formula_id'];
                    $gpObj = $this->loadFormula($gpId);
                    if ($gpObj && !empty($gpObj['subcomponents']) && is_array($gpObj['subcomponents'])) {
                        $seenSibIds[$gpId] = true;
                        foreach ($gpObj['subcomponents'] as $uncleItem) {
                            $uncleId = is_string($uncleItem) ? $uncleItem : ($uncleItem['id'] ?? '');
                            if (!$uncleId || isset($seenSibIds[$uncleId])) continue;
                            $uncleObj = $this->loadFormula($uncleId);
                            if ($uncleObj) {
                                $seenSibIds[$uncleId] = true;
                                $siblings[] = [
                                    'id' => $uncleId,
                                    'title' => $uncleObj['title'] ?? 'Parallel Branch Equation',
                                    'equation' => $uncleObj['equation'] ?? '',
                                    'derivation_type' => 'PARALLEL_BRANCH',
                                    'lineage_confidence' => $uncleObj['lineage_confidence'] ?? null,
                                    'record_type' => $uncleObj['record_type'] ?? null,
                                    'url' => '/physics/equation-explainer?id=' . urlencode($uncleId)
                                ];
                            }
                            if (count($siblings) >= 8) break;
                        }
                    }
                }
                $formula['sibling_formulas'] = $siblings;
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
                            'title' => $childObj['title'] ?? 'Derived Equation',
                            'equation' => $childObj['equation'] ?? '',
                            'derivation_type' => $childObj['derivation_type'] ?? 'DERIVED_FROM',
                            'lineage_confidence' => $childObj['lineage_confidence'] ?? null,
                            'record_type' => $childObj['record_type'] ?? null,
                            'url' => '/physics/equation-explainer?id=' . urlencode($childId)
                        ];
                    }
                } elseif (is_array($childId) && !empty($childId['id'])) {
                    $childIdStr = $childId['id'];
                    $childObj = $this->loadFormula($childIdStr);
                    if ($childObj) {
                        $resolvedChildren[] = [
                            'id' => $childIdStr,
                            'title' => $childObj['title'] ?? ($childId['title'] ?? 'Derived Equation'),
                            'equation' => $childObj['equation'] ?? ($childId['equation'] ?? ''),
                            'derivation_type' => $childObj['derivation_type'] ?? ($childId['derivation_type'] ?? 'DERIVED_FROM'),
                            'lineage_confidence' => $childObj['lineage_confidence'] ?? ($childId['lineage_confidence'] ?? null),
                            'record_type' => $childObj['record_type'] ?? ($childId['record_type'] ?? null),
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
        
        // Dynamic stale-cache fallback (local development only; production syncs atomically via cli_sync.php)
        if (
            !$this->isPreviewActive()
            && AuthService::resolveAppEnv() !== 'production'
            && $table === 'subtopics'
            && isset($content['subtopics'][$slug])
        ) {
            try {
                $this->syncIndividualSubtopic($slug, $content['subtopics'][$slug]);
            } catch (\Throwable $e) {
                // Non-fatal when running in offline/db-unavailable fallback mode
            }
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

        $row = null;
        try {
            $row = $this->app->db()->fetchRow("SELECT * FROM {$table} WHERE slug = ?", [$slug]);
        } catch (\Throwable $e) {
            $row = null;
        }

        if (!$row || (is_object($row) && method_exists($row, 'count') && count($row) === 0)) {
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

        $data = is_object($row) && method_exists($row, 'getData') ? $row->getData() : (array) $row;
        if (empty($data)) return [];
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

        if (isset($data['pillars']) && is_string($data['pillars'])) {
            $data['pillars'] = json_decode($data['pillars'], true) ?: [];
        }

        if (isset($data['bridges']) && is_string($data['bridges'])) {
            $data['bridges'] = json_decode($data['bridges'], true) ?: [];
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
        $this->syncService->syncIndividualSubtopic($slug, $data);
    }

    /**
     * Synchronizes a single topic hub manifest to MariaDB.
     */
    public function syncIndividualTopic(string $slug, array $data): void
    {
        $this->syncService->syncIndividualTopic($slug, $data);
    }

    /**
     * Synchronizes all subtopic shards and topic hubs into the database.
     * Supports differential delta syncing based on file modification timestamps.
     */
    public function performSync(bool $force = false): void
    {
        $this->syncService->performSync($force);
    }

    /**
     * Runs pending numbered database migrations in scripts/migrations/ using schema_migrations ledger.
     */
    public function runMigrations(?string $migrationsDir = null): array
    {
        return $this->syncService->runMigrations($migrationsDir);
    }

    /**
     * Identifies and optionally prunes database subtopics that no longer exist on disk.
     * Supports dry-run auditing.
     */
    public function pruneOrphans(bool $dryRun = true): array
    {
        return $this->syncService->pruneOrphans($dryRun);
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
            $strippedUnderscore = str_replace('_', '', $targetLatex);
            if ($strippedUnderscore !== $targetLatex && isset($index[$strippedUnderscore])) {
                $fId = $index[$strippedUnderscore];
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
        return $this->sanitizer->canonicalizeLatex($latex);
    }

    /**
     * Synthesizes a structured formula explanation dynamically from LaTeX AST parsing
     * when a formula is missing from pre-compiled JSON shards.
     */
    public function synthesizeFormulaExplanation(string $latex): array
    {
        return $this->sanitizer->synthesizeFormulaExplanation($latex);
    }

    /**
     * Normalizes LaTeX mathematical strings to ignore white spaces, styles, and braces.
     */
    public function normalizeLatex(string $latex): string
    {
        return $this->sanitizer->normalizeLatex($latex);
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
                    $snippet = '...' . mb_substr($plainContent, $start, 120, 'UTF-8') . '...';
                } else {
                    $snippet = mb_substr($plainContent, 0, 120, 'UTF-8') . '...';
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
                        'snippet' => mb_substr(strip_tags($st['content'] ?? ''), 0, 120, 'UTF-8') . '...',
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
                        'snippet' => mb_substr(strip_tags($tr['description'] ?? ''), 0, 120, 'UTF-8') . '...',
                        'url' => '/physics/topic/' . $tr['slug']
                    ];
                }
            } catch (\Throwable $e) {
                // ignore
            }
        }

        // 3. Search Formulas if room available
        if (count($results) < $limit) {
            $remaining = max(1, (int)$limit - count($results));
            try {
                $formulaRows = $db->runQuery(
                    "SELECT id, title, equation, conceptual_definition 
                     FROM formulas 
                     WHERE title LIKE ? OR id LIKE ? OR conceptual_definition LIKE ?
                     LIMIT {$remaining}",
                    ['%' . $cleanQuery . '%', '%' . $cleanQuery . '%', '%' . $cleanQuery . '%']
                )->fetchAll();

                foreach ($formulaRows as $f) {
                    $results[] = [
                        'type' => 'formula',
                        'id' => $f['id'],
                        'slug' => $f['id'],
                        'title' => $f['title'],
                        'equation' => $f['equation'] ?? '',
                        'snippet' => mb_substr(strip_tags($f['conceptual_definition'] ?? ''), 0, 120, 'UTF-8') . '...',
                        'url' => '/physics/equation-explainer?id=' . $f['id']
                    ];
                }
            } catch (\Throwable $e) {
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

