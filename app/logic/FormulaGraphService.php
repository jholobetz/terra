<?php
namespace App\Logic;

class FormulaGraphService {
    private static ?array $graphData = null;
    private static string $graphFile = __DIR__ . '/../config/formula_derivation_graph.json';
    private static string $graphGzFile = __DIR__ . '/../config/formula_derivation_graph.json.gz';

    /**
     * Load graph database into memory on first access (with gz compression fallback)
     */
    private static function loadGraph(): array {
        if (self::$graphData !== null) {
            return self::$graphData;
        }

        // Formula graph has 14k+ nodes and 44k+ links, require adequate memory to decode
        if ((int)ini_get('memory_limit') < 512) {
            ini_set('memory_limit', '512M');
        }

        if (file_exists(self::$graphGzFile) && function_exists('gzdecode')) {
            $raw = file_get_contents(self::$graphGzFile);
            $decoded = gzdecode($raw);
            if ($decoded !== false) {
                self::$graphData = json_decode($decoded, true) ?: [];
                return self::$graphData;
            }
        }

        if (file_exists(self::$graphFile)) {
            $raw = file_get_contents(self::$graphFile);
            self::$graphData = json_decode($raw, true) ?: [];
            return self::$graphData;
        }

        self::$graphData = ['nodes' => [], 'links' => [], 'upstream' => [], 'downstream' => []];
        return self::$graphData;
    }

    /**
     * Extract a local subgraph centered around a specific formula ID
     * Upstream (Foundations) -> Target Node -> Downstream (Applications/Limits)
     */
    public static function getFormulaSubgraph(string $formulaId, int $depth = 2): array {
        $graph = self::loadGraph();
        $nodes = $graph['nodes'] ?? [];
        $upstream = $graph['upstream'] ?? [];
        $downstream = $graph['downstream'] ?? [];

        if (!isset($nodes[$formulaId])) {
            return [
                'root_id' => $formulaId,
                'nodes' => [],
                'links' => [],
                'stats' => [
                    'total_nodes' => 0,
                    'total_links' => 0,
                    'upstream_count' => 0,
                    'downstream_count' => 0
                ]
            ];
        }

        $visitedNodes = [$formulaId => 0]; // id => distance/depth
        $subgraphLinks = [];
        $seenLinks = [];
        $directChildren = $downstream[$formulaId] ?? [];
        $isSparseLeaf = count($directChildren) < 3;
        $upstreamDepth = ($isSparseLeaf && empty($directChildren)) ? max($depth, 3) : $depth;

        // 1. Traverse Upstream (Parents / Prerequisites / Axioms)
        $currentLayer = [$formulaId];
        for ($d = 1; $d <= $upstreamDepth; $d++) {
            $nextLayer = [];
            foreach ($currentLayer as $currId) {
                $parents = $upstream[$currId] ?? [];
                foreach ($parents as $p) {
                    $pid = $p['id'];
                    $edgeKey = "$pid->$currId";
                    if (!isset($seenLinks[$edgeKey])) {
                        $seenLinks[$edgeKey] = true;
                        $subgraphLinks[] = [
                            'source' => $pid,
                            'target' => $currId,
                            'type' => $p['type'] ?? 'derivation',
                            'label' => $p['label'] ?? 'Derives',
                            'direction' => 'upstream'
                        ];
                    }
                    if (!isset($visitedNodes[$pid])) {
                        $visitedNodes[$pid] = -$d;
                        $nextLayer[] = $pid;
                    }
                }
            }
            $currentLayer = $nextLayer;
        }

        // 2. Traverse Downstream (Subcomponents / Limiting Cases / Consequences)
        $currentLayer = [$formulaId];
        $maxPerLayer = 12;
        for ($d = 1; $d <= $depth; $d++) {
            $nextLayer = [];
            $layerAddedCount = 0;
            $maxPerParent = ($d === 1) ? $maxPerLayer : max(3, (int)ceil($maxPerLayer / max(1, count($currentLayer))));
            foreach ($currentLayer as $currId) {
                if ($layerAddedCount >= $maxPerLayer) break;
                $children = $downstream[$currId] ?? [];
                $parentAdded = 0;
                foreach ($children as $c) {
                    if ($layerAddedCount >= $maxPerLayer || $parentAdded >= $maxPerParent) break;
                    $cid = $c['id'];
                    $edgeKey = "$currId->$cid";
                    if (!isset($seenLinks[$edgeKey])) {
                        $seenLinks[$edgeKey] = true;
                        $subgraphLinks[] = [
                            'source' => $currId,
                            'target' => $cid,
                            'type' => $c['type'] ?? 'subcomponent',
                            'label' => $c['label'] ?? 'Subcomponent',
                            'direction' => 'downstream'
                        ];
                    }
                    if (!isset($visitedNodes[$cid])) {
                        $visitedNodes[$cid] = $d;
                        $nextLayer[] = $cid;
                        $layerAddedCount++;
                        $parentAdded++;
                    }
                }
            }
            $currentLayer = $nextLayer;
        }

        // 2b. Leaf & Sparse Neighborhood Expansion (Co-Derived Siblings & Parallel Branches)
        if ($isSparseLeaf) {
            $directParentIds = array_keys(array_filter($visitedNodes, fn($v) => $v === -1));
            $grandparentIds = array_keys(array_filter($visitedNodes, fn($v) => $v === -2));

            // Expand co-derived siblings from direct parent(s) at Layer 0
            $siblingsAdded = 0;
            $siblingIds = [];
            foreach ($directParentIds as $pid) {
                foreach (($downstream[$pid] ?? []) as $sibEdge) {
                    if ($siblingsAdded >= 6) break;
                    $sibId = $sibEdge['id'];
                    if ($sibId === $formulaId) continue;
                    $edgeKey = "$pid->$sibId";
                    if (!isset($seenLinks[$edgeKey])) {
                        $seenLinks[$edgeKey] = true;
                        $subgraphLinks[] = [
                            'source' => $pid,
                            'target' => $sibId,
                            'type' => 'sibling',
                            'label' => 'Co-Derived Sibling',
                            'direction' => 'sibling'
                        ];
                    }
                    if (!isset($visitedNodes[$sibId])) {
                        $visitedNodes[$sibId] = 0;
                        $siblingIds[] = $sibId;
                        $siblingsAdded++;
                    }
                }
            }

            // Expand parallel branches (aunts/uncles) from grandparent(s) at Layer -1
            $unclesAdded = 0;
            $uncleIds = [];
            foreach ($grandparentIds as $gpId) {
                foreach (($downstream[$gpId] ?? []) as $uncleEdge) {
                    if ($unclesAdded >= 5) break;
                    $uncleId = $uncleEdge['id'];
                    if (in_array($uncleId, $directParentIds, true)) continue;
                    $edgeKey = "$gpId->$uncleId";
                    if (!isset($seenLinks[$edgeKey])) {
                        $seenLinks[$edgeKey] = true;
                        $subgraphLinks[] = [
                            'source' => $gpId,
                            'target' => $uncleId,
                            'type' => 'sibling',
                            'label' => 'Parallel Branch',
                            'direction' => 'sibling'
                        ];
                    }
                    if (!isset($visitedNodes[$uncleId])) {
                        $visitedNodes[$uncleId] = -1;
                        $uncleIds[] = $uncleId;
                        $unclesAdded++;
                    }
                }
            }

            // If Layer 0 still has < 4 nodes, include up to 2 children per parallel branch at Layer 0
            if ($siblingsAdded < 3 && !empty($uncleIds)) {
                foreach ($uncleIds as $uncleId) {
                    $cousinPerUncle = 0;
                    foreach (($downstream[$uncleId] ?? []) as $cousinEdge) {
                        if ($siblingsAdded >= 5 || $cousinPerUncle >= 2) break;
                        $cousinId = $cousinEdge['id'];
                        $edgeKey = "$uncleId->$cousinId";
                        if (!isset($seenLinks[$edgeKey])) {
                            $seenLinks[$edgeKey] = true;
                            $subgraphLinks[] = [
                                'source' => $uncleId,
                                'target' => $cousinId,
                                'type' => 'sibling',
                                'label' => 'Parallel Derivative',
                                'direction' => 'sibling'
                            ];
                        }
                        if (!isset($visitedNodes[$cousinId])) {
                            $visitedNodes[$cousinId] = 0;
                            $siblingIds[] = $cousinId;
                            $siblingsAdded++;
                            $cousinPerUncle++;
                        }
                    }
                }
            }

            // Expand up to 2 downstream children of Layer 0 siblings at Layer +1
            $nephewsAdded = 0;
            foreach ($siblingIds as $sibId) {
                $perSib = 0;
                foreach (($downstream[$sibId] ?? []) as $nephewEdge) {
                    if ($nephewsAdded >= 6 || $perSib >= 2) break;
                    $nephewId = $nephewEdge['id'];
                    $edgeKey = "$sibId->$nephewId";
                    if (!isset($seenLinks[$edgeKey])) {
                        $seenLinks[$edgeKey] = true;
                        $subgraphLinks[] = [
                            'source' => $sibId,
                            'target' => $nephewId,
                            'type' => $nephewEdge['type'] ?? 'subcomponent',
                            'label' => $nephewEdge['label'] ?? 'Derived Equation',
                            'direction' => 'downstream'
                        ];
                    }
                    if (!isset($visitedNodes[$nephewId])) {
                        $visitedNodes[$nephewId] = 1;
                        $nephewsAdded++;
                        $perSib++;
                    }
                }
            }
        }

        // 3. Assemble full node records
        $subgraphNodes = [];
        foreach ($visitedNodes as $nid => $layerDepth) {
            if (isset($nodes[$nid])) {
                $nodeData = $nodes[$nid];
                $nodeData['is_root'] = ($nid === $formulaId);
                $nodeData['is_sibling'] = ($nid !== $formulaId && $layerDepth <= 0 && !in_array($nid, array_column($upstream[$formulaId] ?? [], 'id'), true));
                $nodeData['layer'] = $layerDepth;
                $subgraphNodes[] = $nodeData;
            }
        }

        return [
            'root_id' => $formulaId,
            'root_node' => $nodes[$formulaId],
            'nodes' => $subgraphNodes,
            'links' => $subgraphLinks,
            'stats' => [
                'total_nodes' => count($subgraphNodes),
                'total_links' => count($subgraphLinks),
                'upstream_count' => count(array_filter($visitedNodes, fn($v) => $v < 0)),
                'downstream_count' => count(array_filter($visitedNodes, fn($v) => $v > 0)),
                'sibling_count' => max(0, count(array_filter($visitedNodes, fn($v) => $v === 0)) - 1)
            ]
        ];
    }

    /**
     * Resolve a user query (exact ID or title/keyword) to a canonical node ID in the graph.
     */
    private static function resolveNodeId(string $query, array $nodes): ?string {
        $q = trim($query);
        if ($q === '') return null;
        if (isset($nodes[$q])) return $q;

        $qLower = mb_strtolower($q);
        // 1. Exact case-insensitive title or ID match
        foreach ($nodes as $id => $n) {
            if (mb_strtolower($id) === $qLower || mb_strtolower($n['title'] ?? '') === $qLower) {
                return $id;
            }
        }
        // 2. Substring match on title (preferring nodes with children/parents)
        $bestId = null;
        foreach ($nodes as $id => $n) {
            $titleLower = mb_strtolower($n['title'] ?? '');
            if ($titleLower !== '' && str_contains($titleLower, $qLower)) {
                return $id;
            }
        }
        return $bestId;
    }

    /**
     * Compute the shortest mathematical derivation path between two formulas using BFS.
     * Checks directed downstream first, then directed upstream, then bidirectional bridge.
     */
    public static function findDerivationPath(string $startId, string $endId): array {
        $graph = self::loadGraph();
        $nodes = $graph['nodes'] ?? [];
        $downstream = $graph['downstream'] ?? [];
        $upstream = $graph['upstream'] ?? [];

        $resolvedStart = self::resolveNodeId($startId, $nodes);
        $resolvedEnd = self::resolveNodeId($endId, $nodes);

        if (!$resolvedStart || !$resolvedEnd) {
            return ['found' => false, 'message' => 'Start or target formula not found in graph.'];
        }
        $startId = $resolvedStart;
        $endId = $resolvedEnd;

        // Helper for BFS traversal
        $runBfs = function(string $mode) use ($startId, $endId, $nodes, $downstream, $upstream): ?array {
            $queue = [[$startId]];
            $visited = [$startId => true];
            $maxDepth = 10;

            while (!empty($queue)) {
                $path = array_shift($queue);
                if (count($path) > $maxDepth) continue;
                $curr = end($path);

                if ($curr === $endId) {
                    $pathNodes = array_map(fn($id) => $nodes[$id] ?? ['id' => $id], $path);
                    return [
                        'found' => true,
                        'mode' => $mode,
                        'hops' => count($path) - 1,
                        'path_ids' => $path,
                        'path_nodes' => $pathNodes
                    ];
                }

                $neighbors = [];
                if ($mode === 'downstream' || $mode === 'bridge') {
                    foreach ($downstream[$curr] ?? [] as $n) $neighbors[] = $n['id'];
                }
                if ($mode === 'upstream' || $mode === 'bridge') {
                    foreach ($upstream[$curr] ?? [] as $n) $neighbors[] = $n['id'];
                }

                foreach ($neighbors as $nid) {
                    if (!isset($visited[$nid])) {
                        $visited[$nid] = true;
                        $newPath = $path;
                        $newPath[] = $nid;
                        $queue[] = $newPath;
                    }
                }
            }
            return null;
        };

        $res = $runBfs('downstream') ?? $runBfs('upstream') ?? $runBfs('bridge');
        if ($res !== null) {
            return $res;
        }

        return ['found' => false, 'message' => 'No derivation path found between these equations.'];
    }
}
