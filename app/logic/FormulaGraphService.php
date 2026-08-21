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

        // 1. Traverse Upstream (Parents / Prerequisites / Axioms)
        $currentLayer = [$formulaId];
        for ($d = 1; $d <= $depth; $d++) {
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
        $maxPerLayer = 30;
        for ($d = 1; $d <= $depth; $d++) {
            $nextLayer = [];
            foreach ($currentLayer as $currId) {
                $children = $downstream[$currId] ?? [];
                $addedCount = 0;
                foreach ($children as $c) {
                    if ($addedCount >= $maxPerLayer) break;
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
                        $addedCount++;
                    }
                }
            }
            $currentLayer = $nextLayer;
        }

        // 3. Assemble full node records
        $subgraphNodes = [];
        foreach ($visitedNodes as $nid => $layerDepth) {
            if (isset($nodes[$nid])) {
                $nodeData = $nodes[$nid];
                $nodeData['is_root'] = ($nid === $formulaId);
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
                'downstream_count' => count(array_filter($visitedNodes, fn($v) => $v > 0))
            ]
        ];
    }

    /**
     * Compute the shortest mathematical derivation path between two formulas using BFS
     */
    public static function findDerivationPath(string $startId, string $endId): array {
        $graph = self::loadGraph();
        $nodes = $graph['nodes'] ?? [];
        $downstream = $graph['downstream'] ?? [];

        if (!isset($nodes[$startId]) || !isset($nodes[$endId])) {
            return ['found' => false, 'error' => 'Start or end formula not found'];
        }

        $queue = [[$startId]];
        $visited = [$startId => true];

        while (!empty($queue)) {
            $path = array_shift($queue);
            $curr = end($path);

            if ($curr === $endId) {
                $pathNodes = array_map(fn($id) => $nodes[$id] ?? ['id' => $id], $path);
                return [
                    'found' => true,
                    'hops' => count($path) - 1,
                    'path_ids' => $path,
                    'path_nodes' => $pathNodes
                ];
            }

            foreach ($downstream[$curr] ?? [] as $neighbor) {
                $nid = $neighbor['id'];
                if (!isset($visited[$nid])) {
                    $visited[$nid] = true;
                    $newPath = $path;
                    $newPath[] = $nid;
                    $queue[] = $newPath;
                }
            }
        }

        return ['found' => false, 'message' => 'No direct derivation path found between these equations.'];
    }
}
