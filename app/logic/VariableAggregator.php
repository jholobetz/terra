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
                
                if (\strlen($cleanSym) === 1 || \in_array($vSym, ['\\hbar', 'k_B', '\\rho', '\\nu', '\\nabla'])) {
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

        // 3. Fallback: If symbolMap is empty, populate default fundamental mechanics variables
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
