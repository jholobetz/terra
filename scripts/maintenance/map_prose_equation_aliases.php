<?php
/**
 * 🔗 Automated Prose Equation Alias Matcher
 * Maps notational, algebraic, and structural equation variants from subtopic prose
 * directly to existing canonical formula IDs in formulas_latex_index.json.
 */

require_once __DIR__ . '/../../vendor/autoload.php';
require_once __DIR__ . '/../../app/config/bootstrap.php';

use App\Logic\PhysicsService;

$app = Flight::app();
$service = new PhysicsService($app);

echo "=======================================================\n";
echo "🔗 Automated Prose Equation Alias Matcher\n";
echo "=======================================================\n\n";

// 1. Load Unmapped Equations Report
$reportFile = __DIR__ . '/../../scratch/unmapped_prose_equations.json';
if (!file_exists($reportFile)) {
    die("[ERROR] Unmapped equations report not found at: {$reportFile}\nRun scripts/audit_prose_equations.php first.\n");
}
$reportData = json_decode(file_get_contents($reportFile), true) ?: [];
$unmappedEquations = $reportData['unmapped_equations'] ?? [];
echo "[INFO] Loaded " . count($unmappedEquations) . " unmapped physical equations to evaluate.\n";

// 2. Load Existing Canonical LaTeX Index
$indexFile = __DIR__ . '/../../app/config/formulas_latex_index.json';
$latexIndex = [];
if (file_exists($indexFile)) {
    $latexIndex = json_decode(file_get_contents($indexFile), true) ?: [];
}
echo "[INFO] Current LaTeX index size: " . count($latexIndex) . " entries.\n";

// 3. Pre-load all 13,700+ formulas from 256 Shards into In-Memory Lookup Structures
echo "[INFO] Loading all formula shards into memory...\n";
$baseDir = __DIR__ . '/../../app/config/content/formulas/';
$shardFiles = glob($baseDir . '*/shard_*.json') ?: glob($baseDir . 'shard_*.json') ?: [];

$formulaRegistry = [];
$normalizedToId = [];
$canonicalToId = [];
$titleToId = [];

foreach ($shardFiles as $sf) {
    $shardData = json_decode(file_get_contents($sf), true) ?: [];
    foreach ($shardData as $fId => $formula) {
        $formulaRegistry[$fId] = $formula;
        $title = strtolower(trim($formula['title'] ?? ''));
        if (!empty($title)) {
            $titleToId[$title] = $fId;
        }

        $eq = $formula['equation'] ?? '';
        if (empty($eq)) continue;

        if (strpos($eq, '<svg') === 0 && preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
            $eq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
        }

        $norm = $service->normalizeLatex($eq);
        if (!empty($norm)) {
            $normalizedToId[$norm] = $fId;
        }

        $canon = $service->canonicalizeLatex($eq);
        if (!empty($canon)) {
            $canonicalToId[$canon] = $fId;
        }
    }
}
echo "[INFO] Loaded " . count($formulaRegistry) . " canonical formulas across " . count($shardFiles) . " shards.\n\n";

// 4. Fuzzy & Structural Variant Matcher Function
function matchFormulaVariant(string $rawTex, PhysicsService $service, array $normalizedToId, array $canonicalToId, array $formulaRegistry): ?array {
    $norm = $service->normalizeLatex($rawTex);
    $canon = $service->canonicalizeLatex($rawTex);

    // Direct checks
    if (isset($normalizedToId[$norm])) {
        return ['id' => $normalizedToId[$norm], 'method' => 'normalized_match'];
    }
    if (isset($canonicalToId[$canon])) {
        return ['id' => $canonicalToId[$canon], 'method' => 'canonical_ast'];
    }

    // Heuristic 1: Stripped vector/calligraphic/styling aggressive simplification
    $stripped = preg_replace('/\\\\(mathbf|mathcal|mathbb|mathrm|text|boldsymbol|vec|hat|bar|tilde|dot|ddot)\{([^}]+)\}/', '$2', $rawTex);
    $stripped = preg_replace('/\\\\(mathbf|mathcal|mathbb|mathrm|text|boldsymbol|vec|hat|bar|tilde|dot|ddot)\s*(\\\\[a-zA-Z]+|[a-zA-Z0-9])/', '$2', $stripped);
    $stripped = preg_replace('/\\\\(left|right|quad|qquad|\\,)/', '', $stripped);
    $strippedNorm = $service->normalizeLatex($stripped);
    $strippedCanon = $service->canonicalizeLatex($stripped);

    if (isset($normalizedToId[$strippedNorm])) {
        return ['id' => $normalizedToId[$strippedNorm], 'method' => 'stripped_styling'];
    }
    if (isset($canonicalToId[$strippedCanon])) {
        return ['id' => $canonicalToId[$strippedCanon], 'method' => 'stripped_ast'];
    }

    // Heuristic 2: Commutative LHS = RHS swap
    if (strpos($rawTex, '=') !== false) {
        $parts = explode('=', $rawTex, 2);
        $swapped = trim($parts[1]) . ' = ' . trim($parts[0]);
        $swappedNorm = $service->normalizeLatex($swapped);
        $swappedCanon = $service->canonicalizeLatex($swapped);

        if (isset($normalizedToId[$swappedNorm])) {
            return ['id' => $normalizedToId[$swappedNorm], 'method' => 'swapped_equality'];
        }
        if (isset($canonicalToId[$swappedCanon])) {
            return ['id' => $canonicalToId[$swappedCanon], 'method' => 'swapped_ast'];
        }
    }

    // Heuristic 3: Derivative notation equivalence (\dot{q} <-> \frac{dq}{dt}, \partial_t <-> \frac{\partial}{\partial t})
    $dotReplaced = preg_replace('/\\\\frac\{d([a-zA-Z])\}\{dt\}/', '\\\\dot{$1}', $rawTex);
    $dotReplaced = preg_replace('/\\\\frac\{d\^2([a-zA-Z])\}\{dt\^2\}/', '\\\\ddot{$1}', $dotReplaced);
    if ($dotReplaced !== $rawTex) {
        $dotCanon = $service->canonicalizeLatex($dotReplaced);
        if (isset($canonicalToId[$dotCanon])) {
            return ['id' => $canonicalToId[$dotCanon], 'method' => 'derivative_dot_ast'];
        }
    }

    // Heuristic 4: Constant factor / index variation simplification (\sum_{i=1}^N -> \sum)
    $sumSimplified = preg_replace('/\\\\sum_\{[^}]+\}\^\{[^}]+\}/', '\\\\sum', $rawTex);
    $sumSimplified = preg_replace('/\\\\sum_\{[^}]+\}/', '\\\\sum', $sumSimplified);
    if ($sumSimplified !== $rawTex) {
        $sumCanon = $service->canonicalizeLatex($sumSimplified);
        if (isset($canonicalToId[$sumCanon])) {
            return ['id' => $canonicalToId[$sumCanon], 'method' => 'summation_index_ast'];
        }
    }

    return null;
}

// 5. Evaluation Loop
$matchedAliases = [];
$unmatchedCount = 0;

echo "Evaluating candidate alias matches across unmapped equations...\n";

foreach ($unmappedEquations as $item) {
    $rawTex = $item['raw_tex'];
    $normKey = $item['normalized_key'];
    
    $match = matchFormulaVariant($rawTex, $service, $normalizedToId, $canonicalToId, $formulaRegistry);
    if ($match) {
        $fId = $match['id'];
        $method = $match['method'];
        $matchedAliases[$normKey] = [
            'formula_id' => $fId,
            'raw_tex' => $rawTex,
            'method' => $method,
            'formula_title' => $formulaRegistry[$fId]['title'] ?? 'Formula'
        ];
    } else {
        $unmatchedCount++;
    }
}

echo "\n=======================================================\n";
echo "📊 ALIAS MATCHING RESULTS\n";
echo "=======================================================\n";
echo "Total Unmapped Evaluated: " . count($unmappedEquations) . "\n";
echo "Successfully Matched:     " . count($matchedAliases) . " (" . number_format((count($matchedAliases)/count($unmappedEquations))*100, 1) . "%)\n";
echo "Remaining Novel Formulas: " . $unmatchedCount . "\n";
echo "=======================================================\n\n";

if (!empty($matchedAliases)) {
    echo "Sample Matched Aliases:\n";
    $sample = array_slice($matchedAliases, 0, 12);
    foreach ($sample as $key => $info) {
        echo "  ✓ [{$info['method']}] {$info['raw_tex']}\n";
        echo "      -> Maps to: {$info['formula_id']} (\"{$info['formula_title']}\")\n\n";
    }

    // 6. Write Back to formulas_latex_index.json
    $addedCount = 0;
    foreach ($matchedAliases as $normKey => $info) {
        if (!isset($latexIndex[$normKey])) {
            $latexIndex[$normKey] = $info['formula_id'];
            $addedCount++;
        }
    }

    file_put_contents($indexFile, json_encode($latexIndex, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
    echo "[OK] Updated {$indexFile} with {$addedCount} new aliases! (Total index entries: " . count($latexIndex) . ")\n\n";
}

echo "Done!\n";
