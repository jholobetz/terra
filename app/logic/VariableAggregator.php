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
     * Build aggregated subtopic variable payload for Option A & Option B UI components
     */
    public static function buildSubtopicVariables(array $subtopicData): array
    {
        $registry = self::getRegistry();
        $subtopicVars = [];

        // 1. Gather formulas linked to this subtopic
        $formulas = $subtopicData['formulas'] ?? [];
        $equations = $subtopicData['equations'] ?? [];

        // 2. Identify key single-letter symbols used in this subtopic
        $symbolMap = [];

        // Seed with explicit key_variables from subtopic metadata if present
        if (!empty($subtopicData['key_variables']) && \is_array($subtopicData['key_variables'])) {
            foreach ($subtopicData['key_variables'] as $varKey) {
                if (isset($registry[$varKey])) {
                    $item = $registry[$varKey];
                    $symKey = $item['display_symbol'] ?? $item['symbol'];
                    $symbolMap[$symKey] = $item;
                }
            }
        }

        // Process formulas to map symbols to equations
        foreach ($formulas as $fId => $formula) {
            if (!\is_array($formula)) continue;
            $fTitle = $formula['title'] ?? $fId;
            $fEq = $formula['equation'] ?? '';
            $semVars = $formula['semantic_variables'] ?? [];

            foreach ($semVars as $vSym => $vDef) {
                if (!\is_array($vDef)) continue;
                $cleanSym = \trim(\str_replace(['$', '\\mathbf{', '}', '\\'], '', $vSym));
                if (\strlen($cleanSym) === 1 || \in_array($vSym, ['\\hbar', 'k_B', '\\rho', '\\nu', '\\nabla'])) {
                    if (!isset($symbolMap[$cleanSym])) {
                        // Find match in registry or construct from formula semantic_variable
                        $matchedRegistry = null;
                        foreach ($registry as $rKey => $rVal) {
                            if (($rVal['display_symbol'] ?? '') === $cleanSym || \strpos($rVal['symbol'] ?? '', $cleanSym) !== false) {
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

                    // Attach equation reference
                    if (!isset($symbolMap[$cleanSym]['equations'])) {
                        $symbolMap[$cleanSym]['equations'] = [];
                    }
                    if (\count($symbolMap[$cleanSym]['equations']) < 4) {
                        $symbolMap[$cleanSym]['equations'][] = [
                            'id' => $fId,
                            'title' => $fTitle,
                            'equation' => $fEq
                        ];
                    }
                }
            }
        }

        // Fallback: If symbolMap is empty, populate default fundamental mechanics variables
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
}
