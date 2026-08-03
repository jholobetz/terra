<?php

namespace App\Logic;

class VariableAggregator
{
    private static ?array $registry = null;

    /**
     * Load canonical variable registry from app/config/variable_registry.json
     */
    public static function getRegistry(): array
    {
        if (self::$registry === null) {
            $path = PROJECT_ROOT . '/app/config/variable_registry.json';
            if (\file_exists($path)) {
                $content = \file_get_contents($path);
                self::$registry = \json_decode($content, true) ?? [];
            } else {
                self::$registry = [];
            }
        }
        return self::$registry;
    }

    /**
     * Clean raw TeX symbol to extract base variable key
     */
    public static function cleanSymbol(string $sym): string
    {
        $clean = \trim(\str_replace(['$', '\\mathbf{', '\\vec{', '\\mathrm{', '\\boldsymbol{', '}', '\\'], '', $sym));
        $parts = \explode('_', $clean);
        return $parts[0];
    }

    /**
     * Build aggregated subtopic variable payload for Option A & Option B UI components
     */
    public static function buildSubtopicVariables(array $subtopicData): array
    {
        $registry = self::getRegistry();
        $symbolMap = [];

        // 1. Seed with explicit key_variables from subtopic metadata if present
        if (!empty($subtopicData['key_variables']) && \is_array($subtopicData['key_variables'])) {
            foreach ($subtopicData['key_variables'] as $varKey) {
                if (isset($registry[$varKey])) {
                    $item = $registry[$varKey];
                    $symKey = $item['display_symbol'] ?? self::cleanSymbol($item['symbol']);
                    $symbolMap[$symKey] = $item;
                }
            }
        }

        // 2. Process formulas linked to this subtopic
        $formulas = $subtopicData['formulas'] ?? [];
        foreach ($formulas as $fId => $formula) {
            if (!\is_array($formula)) continue;
            $fTitle = $formula['title'] ?? $fId;
            $fEq = $formula['equation'] ?? '';
            $semVars = $formula['semantic_variables'] ?? [];

            foreach ($semVars as $vSym => $vDef) {
                if (!\is_array($vDef)) continue;
                $cleanSym = self::cleanSymbol($vSym);
                
                if (\strlen($cleanSym) === 1 || \in_array($vSym, ['\\hbar', 'k_B', '\\rho', '\\nu', '\\nabla', '\\omega'])) {
                    if (!isset($symbolMap[$cleanSym])) {
                        // Exact symbol matching against registry
                        $matchedRegistry = null;
                        foreach ($registry as $rKey => $rVal) {
                            $rClean = self::cleanSymbol($rVal['symbol'] ?? '');
                            $rDisp = $rVal['display_symbol'] ?? '';
                            if ($rClean === $cleanSym || $rDisp === $cleanSym) {
                                $matchedRegistry = $rVal;
                                break;
                            }
                        }

                        if ($matchedRegistry) {
                            $symbolMap[$cleanSym] = $matchedRegistry;
                        } else {
                            $symbolMap[$cleanSym] = [
                                'symbol' => $vSym,
                                'display_symbol' => $cleanSym,
                                'name' => $vDef['name'] ?? $cleanSym,
                                'unit' => $vDef['unit'] ?? '',
                                'domain' => 'General Physics',
                                'description' => $vDef['description'] ?? ''
                            ];
                        }
                    }

                    // Attach equation reference with deduplication
                    if (!isset($symbolMap[$cleanSym]['equations'])) {
                        $symbolMap[$cleanSym]['equations'] = [];
                    }

                    $alreadyAdded = false;
                    foreach ($symbolMap[$cleanSym]['equations'] as $existingEq) {
                        if (($existingEq['title'] ?? '') === $fTitle || ($existingEq['equation'] ?? '') === $fEq) {
                            $alreadyAdded = true;
                            break;
                        }
                    }

                    if (!$alreadyAdded && \count($symbolMap[$cleanSym]['equations']) < 4) {
                        $symbolMap[$cleanSym]['equations'][] = [
                            'id' => $fId,
                            'title' => $fTitle,
                            'equation' => $fEq
                        ];
                    }
                }
            }
        }

        // 3. Scan subtopic content prose for any embedded data-tex symbols (e.g. k, \omega)
        $prose = $subtopicData['content'] ?? '';
        if (!empty($prose)) {
            \preg_match_all('/data-tex=["\']([^"\']+)["\']/i', $prose, $texMatches);
            if (!empty($texMatches[1])) {
                foreach ($texMatches[1] as $tex) {
                    $cleanSym = self::cleanSymbol($tex);
                    if ((\strlen($cleanSym) === 1 || \in_array($tex, ['\\hbar', 'k_B', '\\rho', '\\nu', '\\nabla', '\\omega'])) && !isset($symbolMap[$cleanSym])) {
                        foreach ($registry as $rKey => $rVal) {
                            $rClean = self::cleanSymbol($rVal['symbol'] ?? '');
                            $rDisp = $rVal['display_symbol'] ?? '';
                            if ($rClean === $cleanSym || $rDisp === $cleanSym) {
                                $symbolMap[$cleanSym] = $rVal;
                                break;
                            }
                        }
                    }
                }
            }
        }

        // 4. Fallback: If symbolMap is empty, populate default fundamental mechanics variables
        if (empty($symbolMap)) {
            $defaultKeys = ['v_velocity', 'm_mass', 'F_force', 'p_momentum', 'E_energy', 'a_acceleration', 't_time'];
            foreach ($defaultKeys as $dKey) {
                if (isset($registry[$dKey])) {
                    $item = $registry[$dKey];
                    $symKey = $item['display_symbol'];
                    $symbolMap[$symKey] = $item;
                }
            }
        }

        return $symbolMap;
    }

    /**
     * Build aggregated topic variable payload by scanning subtopics belonging to the specified topic
     */
    public static function buildTopicVariables(string $topicSlug, array $topicData, array $allSubtopics, ?callable $fetchSubtopicFunc = null): array
    {
        $topicSubSlugs = [];

        // 1. Add overview subtopic
        $overviewSlug = $topicSlug . '-overview';
        $topicSubSlugs[$overviewSlug] = true;

        // 2. Add subtopics listed in topic pillars
        $pillars = $topicData['pillars'] ?? [];
        if (\is_string($pillars)) {
            $pillars = \json_decode($pillars, true) ?: [];
        }
        if (!empty($pillars) && \is_array($pillars)) {
            foreach ($pillars as $pillar) {
                if (!empty($pillar['slugs']) && \is_array($pillar['slugs'])) {
                    foreach ($pillar['slugs'] as $sSlug) {
                        $topicSubSlugs[$sSlug] = true;
                    }
                }
            }
        }

        // 3. Add subtopics referencing parent_topic or parents
        foreach ($allSubtopics as $sSlug => $sub) {
            if (!\is_array($sub)) continue;
            $parentTopic = $sub['parent_topic'] ?? '';
            $parents = (array)($sub['parents'] ?? []);
            if ($parentTopic === $topicSlug || \in_array($topicSlug, $parents, true)) {
                $topicSubSlugs[$sSlug] = true;
            }
        }

        // 4. Aggregate variables across all matched topic subtopics
        $topicVariableMap = [];
        foreach (\array_keys($topicSubSlugs) as $sSlug) {
            $subData = null;
            if ($fetchSubtopicFunc !== null) {
                $subData = $fetchSubtopicFunc($sSlug);
            } elseif (isset($allSubtopics[$sSlug]) && \is_array($allSubtopics[$sSlug])) {
                $subData = $allSubtopics[$sSlug];
            }

            if (empty($subData) || !\is_array($subData)) continue;

            $subVars = self::buildSubtopicVariables($subData);
            foreach ($subVars as $sym => $varData) {
                if (!isset($topicVariableMap[$sym])) {
                    $topicVariableMap[$sym] = [
                        'name' => $varData['name'] ?? $sym,
                        'unit' => $varData['unit'] ?? 'dimensionless',
                        'description' => $varData['description'] ?? '',
                        'formulas' => []
                    ];
                }

                if (!empty($varData['equations']) && \is_array($varData['equations'])) {
                    foreach ($varData['equations'] as $eq) {
                        $eqTitle = $eq['title'] ?? '';
                        if (!empty($eqTitle) && \count($topicVariableMap[$sym]['formulas']) < 3 && !\in_array($eqTitle, $topicVariableMap[$sym]['formulas'], true)) {
                            $topicVariableMap[$sym]['formulas'][] = $eqTitle;
                        }
                    }
                }
            }
        }

        return $topicVariableMap;
    }
}
