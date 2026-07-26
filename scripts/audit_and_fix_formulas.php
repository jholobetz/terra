<?php

define('PROJECT_ROOT', dirname(__DIR__));
require_once PROJECT_ROOT . '/vendor/autoload.php';

$config = require PROJECT_ROOT . '/app/config/config.php';
$app = Flight::app();
require PROJECT_ROOT . '/app/config/services.php';
$db = $app->db();

echo "========================================================\n";
echo "  EXTENSIVE TERRA FORMULA AUDIT & REPAIR               \n";
echo "========================================================\n\n";

$shardFiles = glob(PROJECT_ROOT . '/app/config/content/formulas/*/*.json');
$shardFiles = array_merge($shardFiles, glob(PROJECT_ROOT . '/app/config/content/formulas/*.json'));

$totalFormulas = 0;
$repairedCount = 0;

$directReplacements = [
    '\\Delta\\delta\\delta S' => '\\Delta S',
    '\\delta\\delta\\delta S' => '\\delta S',
    '\\delta\\delta\\delta' => '\\delta',
    '\\delta\\delta S-Field' => '\\delta^2 S_{\\text{field}}',
    '\\delta\\delta S bounded' => '\\delta^2 S \\ge 0',
    'surface\\delta\\delta S that' => 'surface $S$ that',
    'surface\\delta\\delta S' => 'surface $S$',
    'integral\\delta\\delta S' => 'integral $S$',
    'action\\delta\\delta S' => 'action $S$',
    '\\delta\\delta S' => '\\delta S',
    'Hamilton\\delta\\delta S-Field' => 'Hamilton\'s Principal Function',
    'Hamilton\\delta' => 'Hamilton\'s',
    '∨_C' => '\\oint_C',
    '∨' => '\\oint',
    '∫²_S' => '\\iint_S',
    '∫²' => '\\iint',
    '⁵X⁰' => 'X',
    '⁵Y⁰' => 'Y',
    '⁵Z⁰' => 'Z',
    'µ₀' => '\\mu_0',
    '⁲⁽' => '^2(',
    '⁲' => '^2',
    '⁽' => '(',
    '⁾' => ')',
    'ⁱ' => '_i',
    '™' => '',
    '⁮' => '',
    '⁯' => '',
    'âŒā' => '\\dot{q}',
    'ᵏ' => 'T',
    'ℙ' => 'V',
    'μ₀' => '\\mu_0',
    'µ₀' => '\\mu_0',
    '$$SU(3)_c$$' => '$SU(3)_c$',
    'SU(3)\\_c' => '$SU(3)_c$',
    'yielding characteristic solutions (eigenfunctions) and their corresponding values (eigenvalues)' => 'yielding characteristic solution functions $y(x)$ (eigenfunctions) and their corresponding values $\\lambda$ (eigenvalues)',
    'yielding characteristic solutions\nand their corresponding values\n' => 'yielding characteristic solution functions $y(x)$ (eigenfunctions) and their corresponding values $\\lambda$ (eigenvalues)'
];

foreach ($shardFiles as $filePath) {
    $content = file_get_contents($filePath);
    $data = json_decode($content, true);

    if (!is_array($data)) {
        continue;
    }

    $fileModified = false;

    foreach ($data as $formulaId => &$formula) {
        if (!is_array($formula)) {
            continue;
        }

        $totalFormulas++;
        $formulaModified = false;

        $textFields = [
            'title',
            'equation',
            'conceptual_definition',
            'intuitive_summary',
            'interpretation',
            'symmetry_origin',
            'limits_and_boundary'
        ];

        // Clean keys and values in semantic_variables
        if (!empty($formula['semantic_variables']) && is_array($formula['semantic_variables'])) {
            $newSem = [];
            $semChanged = false;
            foreach ($formula['semantic_variables'] as $varKey => $varVal) {
                $cleanKey = str_replace(['µ₀', 'μ₀', '∨_C', '∫²_S', '⁵X⁰', '⁲⁽'], ['\\mu_0', '\\mu_0', '\\oint_C', '\\iint_S', 'X', '^2('], $varKey);
                if ($cleanKey !== $varKey) $semChanged = true;
                if (is_array($varVal)) {
                    foreach ($varVal as $vk => &$vv) {
                        if (is_string($vv)) {
                            $cleanVv = str_replace(['µ₀', 'μ₀', '∨_C', '∫²_S', '⁵X⁰', '⁲⁽'], ['\\mu_0', '\\mu_0', '\\oint_C', '\\iint_S', 'X', '^2('], $vv);
                            if ($cleanVv !== $vv) {
                                $vv = $cleanVv;
                                $semChanged = true;
                            }
                        }
                    }
                }
                $newSem[$cleanKey] = $varVal;
            }
            if ($semChanged) {
                $formula['semantic_variables'] = $newSem;
                $formulaModified = true;
                $fileModified = true;
            }
        }

        foreach ($textFields as $field) {
            if (empty($formula[$field]) || !is_string($formula[$field])) {
                continue;
            }

            $original = $formula[$field];
            $updated = $original;

            // 1. Direct replacements
            foreach ($directReplacements as $bad => $good) {
                if (strpos($updated, $bad) !== false) {
                    $updated = str_replace($bad, $good, $updated);
                }
            }

            // 2. Fix \n variable artifacts in prose
            $updated = preg_replace('/Lagrangian,\s*\\\\n,/i', 'Lagrangian, $L$,', $updated);
            $updated = preg_replace('/kinetic energy\s*\(\s*\\\\n\s*\)/i', 'kinetic energy ($T$)', $updated);
            $updated = preg_replace('/potential energy\s*\(\s*\\\\n\s*\)/i', 'potential energy ($V$)', $updated);
            $updated = preg_replace('/\\\\n\s*=\s*T\s*-\s*V/i', '$L = T - V$', $updated);
            $updated = preg_replace('/\\\\n\s*≈\s*T/i', '$L \\approx T$', $updated);
            $updated = preg_replace('/\\\\n\s*≈\s*-V/i', '$L \\approx -V$', $updated);
            $updated = preg_replace('/\\\\n\s*=\s*0\s*for all\s*\\\\n/i', '$\\dot{q}_i = 0$ for all $q_i$', $updated);
            $updated = preg_replace('/\\\\n\s*=\s*0/i', '$0$', $updated);

            // Replace remaining literal \n surrounded by spaces or math context with empty string or variable fallback
            $updated = preg_replace('/\s+\\\\n\s+/', ' ', $updated);

            // 3. Fix nested/malformed dollar signs like "$ p = $\frac{1}{2}$ \theta_{total} $"
            $updated = preg_replace('/\$\s*([a-zA-Z0-9_\^ ]+)\s*=\s*\$\\s*\\\\frac/i', '$$1 = \\\\frac', $updated);
            $updated = preg_replace('/\$\s*\$([^\$]+)\$\s*\$/', '$$1$', $updated);
            $updated = preg_replace('/\$\s*(\\\\frac\{[^{}]*\}\{[^{}]*\})\s*\$/', '$$1$', $updated);

            // 4. Auto-wrap unwrapped TeX macros like \frac{a}{b}, \oint_C, \iint_S
            $updated = preg_replace_callback('/(?<!\$|\\\\[\\(\\\[])(\\\\(?:frac|oint|iint)(?:\{[^{}]*\}|_[a-zA-Z0-9_]+|\^[a-zA-Z0-9_]+|\([^\)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^])*)/', function($m) {
                return '$' . $m[1] . '$';
            }, $updated);

            if ($updated !== $original) {
                $formula[$field] = $updated;
                $formulaModified = true;
                $fileModified = true;
            }
        }

        if ($formulaModified) {
            $repairedCount++;

            // Sync to MariaDB
            try {
                $db->runQuery(
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
            } catch (\Throwable $e) {
                // Ignore DB missing rows
            }
        }
    }

    if ($fileModified) {
        file_put_contents($filePath, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    }
}

echo "\n========================================================\n";
echo "    EXTENSIVE REPAIR COMPLETE                          \n";
echo "    Total Formulas Inspected: {$totalFormulas}         \n";
echo "    Total Formulas Repaired:  {$repairedCount}          \n";
echo "========================================================\n";
