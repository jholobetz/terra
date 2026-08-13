<?php
/**
 * CLI Tool: fix_equation_by_url.php (v2 with CLI Flags & Batching)
 * 
 * Audits, decorrupts, and repairs LaTeX, SVG rendering, and database/shard consistency
 * for formulas given URLs, Formula IDs, or raw LaTeX queries.
 * 
 * Usage:
 *   php scripts/fix_equation_by_url.php "http://localhost:8000/physics/equation-explainer?id=meissner-flux-expulsion-ident-3440877a"
 *   php scripts/fix_equation_by_url.php --dry-run "meissner-flux-expulsion-ident-3440877a"
 *   php scripts/fix_equation_by_url.php --json "http://localhost:8000/physics/equation-explainer?latex=\sum..."
 *   php scripts/fix_equation_by_url.php --file=urls.txt --dry-run
 */

if (php_sapi_name() !== 'cli') {
    die("This script can only be run from the command line.\n");
}

if (!defined('FLIGHT_SKIP_START')) {
    define('FLIGHT_SKIP_START', true);
}
require_once __DIR__ . '/../app/config/bootstrap.php';

if (class_exists('\Tracy\Debugger')) {
    \Tracy\Debugger::$showBar = false;
}

// Parse CLI options and flags
$shortopts = "h";
$longopts = ["dry-run", "json", "file:", "help"];
$options = getopt($shortopts, $longopts);

$isDryRun = isset($options['dry-run']);
$isJson = isset($options['json']);
$fileInput = $options['file'] ?? null;
$showHelp = isset($options['h']) || isset($options['help']);

// Extract positional arguments (excluding flag strings)
$positionals = [];
for ($i = 1; $i < count($argv); $i++) {
    $arg = $argv[$i];
    if (strpos($arg, '--') === 0 || (strpos($arg, '-') === 0 && strlen($arg) === 2)) {
        continue;
    }
    if ($i > 1 && ($argv[$i - 1] === '--file' || $argv[$i - 1] === '-f')) {
        continue;
    }
    $positionals[] = $arg;
}

// Collect target inputs
$targets = [];
if (!empty($fileInput)) {
    if (!file_exists($fileInput)) {
        echo "[ERROR] Specified target file not found: {$fileInput}\n";
        exit(1);
    }
    $lines = file($fileInput, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        $trimmed = trim($line);
        if (!empty($trimmed) && strpos($trimmed, '#') !== 0) {
            $targets[] = $trimmed;
        }
    }
}

foreach ($positionals as $pos) {
    $trimmed = trim($pos);
    if (!empty($trimmed) && !in_array($trimmed, $targets, true)) {
        $targets[] = $trimmed;
    }
}

if ($showHelp || empty($targets)) {
    echo "=======================================================\n";
    echo "Terra Equation Repair Engine v2 (CLI Flags Edition)\n";
    echo "=======================================================\n";
    echo "Usage:\n";
    echo "  php scripts/fix_equation_by_url.php [options] <URL|ID|LaTeX> [target2 ...]\n\n";
    echo "Options:\n";
    echo "  --dry-run       Preview decorruption changes without updating disk shards or MariaDB\n";
    echo "  --json          Output repair results as a structured JSON object\n";
    echo "  --file=<path>   Read line-separated targets from a file\n";
    echo "  -h, --help      Show this help message\n\n";
    echo "Examples:\n";
    echo "  php scripts/fix_equation_by_url.php \"http://localhost:8000/physics/equation-explainer?id=meissner-flux-expulsion-ident-3440877a\"\n";
    echo "  php scripts/fix_equation_by_url.php --dry-run \"meissner-flux-expulsion-ident-3440877a\"\n";
    echo "  php scripts/fix_equation_by_url.php --file=broken_urls.txt --json\n";
    exit($showHelp ? 0 : 1);
}

// Decorrupt Prose Fields Helper
function sanitizeProseTeX(string $text): string {
    if (empty($text)) return '';

    // Fast-path early exit for clean prose containing no LaTeX or special TeX characters
    if (strpos($text, '$') === false && strpos($text, '\\') === false && !preg_match('/[χμ⟨]/u', $text)) {
        return $text;
    }

    // 1. Optimized symbol lookup table
    $text = strtr($text, [
        'χ_m' => '$\\chi_m$',
        'μ_0' => '$\\mu_0$',
        '4π'  => '$4\\pi$',
        'dau' => '\\tau',
        'extbf' => '\\mathbf',
    ]);

    // 2. Fix specific legacy corrupted TeX patterns
    $text = preg_replace('/[χ\chi]_[m]\s*=\s*-\s*\$\s*\\\\frac\{[^}]+\}\{[^}]+\}\s*\$\s*[⟨<]\s*r\^2\s*[⟩>]/u', '$\\chi_m = -\\frac{\\mu_0 N Z e^2}{6m_e} \\langle r^2 \\rangle$', $text);

    // 3. Fix fragmented math delimiters in continuity equation
    $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ +$\\nabla \\cdot (\\rho \\mathbf{u})$ = 0$', '$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
    $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ + $\\nabla \\cdot$ ($\\rho \\mathbf{u}$) = 0$', '$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
    $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ > 0$', '$\\frac{\\partial \\rho}{\\partial t} > 0$', $text);
    $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ < 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) < 0$', $text);
    $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ < 0$', '$\\frac{\\partial \\rho}{\\partial t} < 0$', $text);
    $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ > 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) > 0$', $text);
    $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ = 0$', '$\\frac{\\partial \\rho}{\\partial t} = 0$', $text);
    $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ = 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
    $text = str_replace('solenoidality of velocity field \\nabla \\cdot \\mathbf{u} = 0.', 'solenoidality of velocity field $\\nabla \\cdot \\mathbf{u} = 0$.', $text);

    // 4. General fraction and operator fixes
    $text = preg_replace('/\\\\[fF]rac\{\s*\\\\partial\s*([a-zA-Z0-9_\-\\\\]+)\s*\$\s*\}\{\s*\$?\\\\partial\s*\$?\s*([a-zA-Z0-9_\-\\\\]+)\s*\}\$?/u', '$\\frac{\\partial $1}{\\partial $2}$', $text);

    // 5. Additional symbol replacements
    $text = preg_replace('/(?<!\\\\|\{)m_e(?!\})/u', '$m_e$', $text);
    $text = preg_replace('/[⟨<]\s*r\^2\s*[⟩>]/u', '$\\langle r^2 \\rangle$', $text);

    // 6. Clean up double $$
    $text = preg_replace('/\$\$+/', '$', $text);

    // 7. Standard TeX fixes
    $text = preg_replace('/\\\\frac\{dp\^\$\s*u\}\{dau\}/i', '\\frac{dp^\\mu}{d\\tau}', $text);
    $text = preg_replace('/F\^\{u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
    $text = preg_replace('/F\^\{\$u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
    $text = preg_replace('/U_\$\\rho/i', 'U_\\rho', $text);
    $text = preg_replace('/You_\s*\$\s*u\s*\$to\$/i', 'four-velocity $U_\\mu$ to', $text);

    // 8. Fix fragmented sums, vector displacement, and absolute bounds
    $originalInput = $text;
    $text = str_replace("'V($\\mathbf{r}_i$ - $\\mathbf{R}_I$)'", "'$V(\\mathbf{r}_i - \\mathbf{R}_I)$'", $text);
    $text = str_replace("'(\\mathbf{r}_i - \\mathbf{R}_I)$'", "'$V(\\mathbf{r}_i - \\mathbf{R}_I)$'", $text);
    $text = str_replace("'($\\mathbf{r}_i$ - $\\mathbf{R}_I$)'", "'$\\mathbf{r}_i - \\mathbf{R}_I$'", $text);
    $text = str_replace("'$\\sum_{i$, I}'", "'$\\sum_{i, I}$'", $text);
    $text = str_replace("$\\sum_{i$, I}", "$\\sum_{i, I}$", $text);
    $text = str_replace("'|$\\mathbf{r}_i$ - $\\mathbf{R}_I$| $\\to\\infty$'", "'$|\\mathbf{r}_i - \\mathbf{R}_I| \\to \\infty$'", $text);
    $text = str_replace("'|$\\mathbf{r}_i$ - $\\mathbf{R}_I$| $\\to$ 0'", "'$|\\mathbf{r}_i - \\mathbf{R}_I| \\to 0$'", $text);

    // Regex fallbacks for vector displacement with correct variable backreferences ($1, $2, etc.)
    $res = preg_replace('/\'?V\(\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\)\'?/u', '\'$V(\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4})$\'', $text);
    if (!empty($res)) $text = $res;

    $res = preg_replace('/\'?\|\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\|\s*\\$\\to\\\\infty\$\'?/u', '\'$|\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4}| \\to \\infty$\'', $text);
    if (!empty($res)) $text = $res;

    $res = preg_replace('/\'?\|\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\|\s*\\$\\to\\\$\s*0\'?/u', '\'$|\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4}| \\to 0$\'', $text);
    if (!empty($res)) $text = $res;

    // 9. General cleanup of multiple spaces
    $cleaned = trim(preg_replace('/\s+/', ' ', $text));
    return !empty($cleaned) ? $cleaned : $originalInput;
}

// Connect to MariaDB (Dynamic & Graceful Fallback)
$pdo = null;
try {
    if (Flight::has('db')) {
        $pdo = Flight::db();
    } else {
        $dbConfig = $config['database'] ?? [];
        $dsn = 'mysql:host=' . ($dbConfig['host'] ?? '127.0.0.1') . ';dbname=' . ($dbConfig['dbname'] ?? 'physicslab') . ';charset=utf8mb4';
        $pdo = new PDO($dsn, $dbConfig['user'] ?? 'doc', $dbConfig['password'] ?? '', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
        ]);
    }
} catch (\Throwable $e) {
    if (!$isJson) {
        echo "[WARN] MariaDB connection unavailable (" . $e->getMessage() . "). Proceeding in JSON-only repair mode.\n\n";
    }
    $pdo = null;
}

$results = [];

foreach ($targets as $input) {
    $targetResult = [
        'input' => $input,
        'success' => false,
        'dry_run' => $isDryRun,
        'repairs_made' => [],
    ];

    if (!$isJson) {
        echo "=======================================================\n";
        echo "Terra Equation Repair Engine v2" . ($isDryRun ? " [DRY-RUN MODE]" : "") . "\n";
        echo "Input: {$input}\n";
        echo "=======================================================\n\n";
    }

    // 1. Extract Target Parameters
    $targetId = null;
    $targetLatex = null;

    if (strpos($input, 'http://') === 0 || strpos($input, 'https://') === 0 || strpos($input, 'equation-explainer') !== false || strpos($input, '?') !== false) {
        $parsedUrl = parse_url($input);
        $queryString = $parsedUrl['query'] ?? '';
        if (empty($queryString) && strpos($input, '?') !== false) {
            $queryString = substr($input, strpos($input, '?') + 1);
        }
        parse_str($queryString, $queryParams);
        
        if (!empty($queryParams['id'])) {
            $targetId = trim($queryParams['id']);
        }
        if (!empty($queryParams['latex'])) {
            $targetLatex = trim(rawurldecode($queryParams['latex']));
        }
    } else if (preg_match('/^[a-z0-9\-]+$/i', trim($input))) {
        $targetId = trim($input);
    } else {
        $targetLatex = trim($input);
    }

    // 2. Resolve Target Formula from DB or Input
    $formulaRecord = null;
    if ($pdo) {
        try {
            if (!empty($targetId)) {
                $stmt = $pdo->prepare("SELECT * FROM formulas WHERE id = ?");
                $stmt->execute([$targetId]);
                $formulaRecord = $stmt->fetch();
            }

            if (!$formulaRecord && !empty($targetLatex)) {
                $stmt = $pdo->prepare("SELECT * FROM formulas WHERE equation = ?");
                $stmt->execute([$targetLatex]);
                $formulaRecord = $stmt->fetch();

                if (!$formulaRecord) {
                    $escapedLatex = addcslashes($targetLatex, '%_');
                    $stmt = $pdo->prepare("SELECT * FROM formulas WHERE equation LIKE ? LIMIT 1");
                    $stmt->execute(['%' . $escapedLatex . '%']);
                    $formulaRecord = $stmt->fetch();
                }
            }
        } catch (\Throwable $e) {
            if (!$isJson) echo "[WARN] Database lookup error (" . $e->getMessage() . "). Falling back to shard resolution.\n";
        }
    }

    // Fallback: Resolve formula ID via PhysicsService LaTeX Index if DB lookup yields nothing
    if (!$formulaRecord && empty($targetId) && !empty($targetLatex)) {
        try {
            $service = Flight::physicsService();
            $resolvedFormula = $service->searchFormulaByLatex($targetLatex);
            if ($resolvedFormula && !empty($resolvedFormula['id'])) {
                $targetId = $resolvedFormula['id'];
            }
        } catch (\Throwable $e) {
            // Ignore index search errors
        }
    }

    // 3. Locate Shard File
    $formulaId = $formulaRecord['id'] ?? $targetId;
    if (empty($formulaId)) {
        $targetResult['error'] = "Could not resolve formula ID from input.";
        $results[] = $targetResult;
        if (!$isJson) echo "[ERROR] Could not resolve formula ID from input.\n\n";
        continue;
    }

    $hexPrefix = substr(md5($formulaId), 0, 2);
    $baseDir = __DIR__ . '/../app/config/content/formulas/';
    $shardFile = $baseDir . $hexPrefix . '/shard_' . $hexPrefix . '.json';

    if (!file_exists($shardFile)) {
        $shardFile = $baseDir . 'shard_' . $hexPrefix . '.json';
    }

    if (!file_exists($shardFile)) {
        $targetResult['error'] = "Shard file for formula ID '{$formulaId}' not found at prefix '{$hexPrefix}'.";
        $results[] = $targetResult;
        if (!$isJson) echo "[ERROR] Shard file for formula ID '{$formulaId}' not found at md5 prefix '{$hexPrefix}'.\n\n";
        continue;
    }

    $targetResult['formula_id'] = $formulaId;
    $targetResult['shard_file'] = $shardFile;

    if (!$isJson) {
        echo "[INFO] Target Formula ID: {$formulaId}\n";
        echo "[INFO] Canonical Shard Path: {$shardFile}\n\n";
    }

    // 4. Load and Audit Shard Data
    $shardContent = file_get_contents($shardFile);
    $shardData = json_decode($shardContent, true);

    if (!isset($shardData[$formulaId])) {
        $targetResult['error'] = "Formula '{$formulaId}' missing inside shard {$shardFile}.";
        $results[] = $targetResult;
        if (!$isJson) echo "[ERROR] Formula '{$formulaId}' missing inside shard {$shardFile}.\n\n";
        continue;
    }

    $formulaData = $shardData[$formulaId];
    $originalEq = $formulaData['equation'] ?? '';
    $repairsMade = [];

    // Clean LaTeX Equation
    $cleanEq = $originalEq;
    if (!empty($targetLatex) && $cleanEq !== $targetLatex) {
        $cleanEq = $targetLatex;
        $repairsMade[] = "Updated LaTeX equation from target input: {$cleanEq}";
    } else if (strpos($cleanEq, 'dp^') !== false && strpos($cleanEq, '\frac') === false) {
        $cleanEq = preg_replace('/dp\^?\\\\?([a-zA-Z]+)\/d\\\\?([a-zA-Z]+)/', '\frac{dp^\1}{d\\\2}', $cleanEq);
        $repairsMade[] = "Converted slash derivative to fraction notation: {$cleanEq}";
    }

    // Audit Prose Fields
    $proseFields = ['description', 'conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary'];
    foreach ($proseFields as $field) {
        if (isset($formulaData[$field]) && is_string($formulaData[$field])) {
            $sanitized = sanitizeProseTeX($formulaData[$field]);
            if ($sanitized !== $formulaData[$field]) {
                $formulaData[$field] = $sanitized;
                $repairsMade[] = "Sanitized corrupted TeX strings in '{$field}'";
            }
        }
    }

    // Sanitize semantic_variables schema type & key names
    $semVars = $formulaData['semantic_variables'] ?? [];
    if (!is_array($semVars) || empty($semVars)) {
        $formulaData['semantic_variables'] = (object)[];
    } else {
        $cleanSemVars = [];
        foreach ($semVars as $k => $v) {
            $cleanK = str_replace('$', '', trim($k));
            $cleanSemVars[$cleanK] = $v;
        }
        $formulaData['semantic_variables'] = $cleanSemVars;
    }

    $formulaData['equation'] = $cleanEq;
    $shardData[$formulaId] = $formulaData;

    // Sanitize all formulas in shardData to guarantee no neighbor formula re-introduces [] array
    foreach ($shardData as $fKey => &$fVal) {
        if (is_array($fVal)) {
            $sVars = $fVal['semantic_variables'] ?? [];
            if (!is_array($sVars) || empty($sVars)) {
                $fVal['semantic_variables'] = (object)[];
            }
        }
    }
    unset($fVal);

    $targetResult['clean_equation'] = $cleanEq;
    $targetResult['repairs_made'] = $repairsMade;

    // 5. Write Back (unless Dry Run)
    if (!$isDryRun) {
        file_put_contents($shardFile, json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
        if (!$isJson) echo "[OK] Saved updated formula definition to shard: {$shardFile}\n";

        if ($pdo) {
            try {
                $stmt = $pdo->prepare("UPDATE formulas SET equation = ?, equation_svg = NULL, interpretation = ?, symmetry_origin = ?, limits_and_boundary = ?, semantic_variables = ? WHERE id = ?");
                $stmt->execute([
                    $cleanEq,
                    $formulaData['interpretation'] ?? null,
                    $formulaData['symmetry_origin'] ?? null,
                    $formulaData['limits_and_boundary'] ?? null,
                    isset($formulaData['semantic_variables']) ? json_encode($formulaData['semantic_variables'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : null,
                    $formulaId
                ]);
                if (!$isJson) echo "[OK] Updated MariaDB formulas table record (equation_svg set to NULL).\n";
            } catch (\Throwable $e) {
                if (!$isJson) echo "[WARN] MariaDB record update skipped: " . $e->getMessage() . "\n";
            }
        }

        $latexIndexFile = __DIR__ . '/../app/config/formulas_latex_index.json';
        if (file_exists($latexIndexFile)) {
            $indexData = json_decode(file_get_contents($latexIndexFile), true) ?: [];
            $app = Flight::app();
            $service = $app->physicsService();
            $normLatex = $service->normalizeLatex($cleanEq);
            if (!empty($normLatex)) {
                $indexData[$normLatex] = $formulaId;
                file_put_contents($latexIndexFile, json_encode($indexData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
                if (!$isJson) echo "[OK] Updated formulas_latex_index.json mapping for: {$normLatex} -> {$formulaId}\n";
            }
        }
    } else {
        if (!$isJson) echo "[DRY-RUN] Skipped writing to shard file and MariaDB.\n";
    }

    if (!$isJson) {
        if (!empty($repairsMade)) {
            echo "\nSummary of Repairs Applied:\n";
            foreach ($repairsMade as $rep) {
                echo "  - {$rep}\n";
            }
        } else {
            echo "\nNo structural TeX corruptions found. LaTeX synced.\n";
        }
    }

    // 6. In-Process Verification
    if (!$isJson) echo "\nVerifying repair in-process ...\n";
    try {
        $service = Flight::physicsService();
        $formula = $service->loadFormula($formulaId);
        if (!empty($formula)) {
            $targetResult['verified'] = true;
            $targetResult['formula_title'] = $formula['title'] ?? ($formulaData['title'] ?? 'N/A');
            if (!$isJson) {
                echo "[VERIFIED] In-process PhysicsService resolved formula successfully!\n";
                echo "  - Formula Title: " . $targetResult['formula_title'] . "\n";
                echo "  - Clean Equation: " . ($formula['equation'] ?? $cleanEq) . "\n";
                echo "  - Equation SVG: " . (is_null($formula['equation_svg'] ?? null) ? 'NULL (Clean Dynamic MathJax)' : 'POPULATED') . "\n";
            }
        } else {
            $targetResult['verified'] = false;
            if (!$isJson) echo "[WARN] PhysicsService returned empty payload for formula '{$formulaId}'.\n";
        }
    } catch (\Throwable $e) {
        $targetResult['verified'] = false;
        if (!$isJson) echo "[WARN] In-process verification error: " . $e->getMessage() . "\n";
    }

    $targetResult['success'] = true;
    $results[] = $targetResult;

    if (!$isJson) echo "\nDone!\n\n";
}

if ($isJson) {
    echo json_encode(count($results) === 1 ? $results[0] : $results, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\n";
}
