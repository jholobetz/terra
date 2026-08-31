<?php
/**
 * 🔍 Subtopic Prose Equation Harvester & Delta Auditor (Optimized High-Speed)
 * Scans all 1,527 subtopics with in-memory AST indexing and live progress bar.
 */

require_once __DIR__ . '/../vendor/autoload.php';
require_once __DIR__ . '/../app/config/bootstrap.php';

use App\Logic\PhysicsService;

$app = Flight::app();
$service = new PhysicsService($app);

echo "=======================================================\n";
echo "🔍 Subtopic Prose LaTeX Harvester & Delta Auditor\n";
echo "=======================================================\n\n";

// 1. Load canonical LaTeX Index
$indexFile = __DIR__ . '/../app/config/formulas_latex_index.json';
$latexIndex = [];
if (file_exists($indexFile)) {
    $latexIndex = json_decode(file_get_contents($indexFile), true) ?: [];
}
echo "[INFO] Loaded canonical LaTeX index with " . count($latexIndex) . " indexed equation keys.\n";

// 2. Pre-index all Shard Formulas in Memory for Instant AST Matching
echo "[INFO] Pre-compiling AST index from formula shards in-memory...\n";
$baseDir = __DIR__ . '/../app/config/content/formulas/';
$shardFiles = glob($baseDir . '*/shard_*.json') ?: glob($baseDir . 'shard_*.json') ?: [];
$astIndex = [];

foreach ($shardFiles as $sf) {
    $shardData = json_decode(file_get_contents($sf), true) ?: [];
    foreach ($shardData as $fId => $formula) {
        $eq = $formula['equation'] ?? '';
        if (empty($eq)) continue;
        
        $cleanEq = $eq;
        if (strpos($eq, '<svg') === 0 && preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
            $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
        }
        
        $canon = $service->canonicalizeLatex($cleanEq);
        if (!empty($canon) && !isset($astIndex[$canon])) {
            $astIndex[$canon] = $fId;
        }
    }
}
echo "[INFO] Built in-memory AST lookup index with " . count($astIndex) . " canonical signatures.\n\n";

// 3. Load all Subtopics from 12 Major Domains
$contentDir = __DIR__ . '/../app/config/content';
$topicSlugs = [
    'classical-mechanics', 'electromagnetism', 'relativity', 'quantum-physics',
    'thermodynamics-statistical-mechanics', 'standard-model', 'astrophysics',
    'theoretical-physics', 'philosophy-of-physics', 'mathematical-methods',
    'condensed-matter', 'fluids-nonlinear'
];

$subtopics = [];
foreach ($topicSlugs as $slug) {
    $path = $contentDir . '/' . $slug . '.json';
    if (file_exists($path)) {
        $data = json_decode(file_get_contents($path), true) ?: [];
        foreach ($data as $subSlug => $sub) {
            if (is_array($sub)) {
                $subtopics[$subSlug] = $sub;
            }
        }
    }
}
echo "[INFO] Successfully loaded " . count($subtopics) . " subtopics across all 12 major domains.\n\n";

// 4. Extraction & Harvesting Pass
$totalOccurrences = 0;
$uniqueExpressions = [];

foreach ($subtopics as $slug => $sub) {
    $content = $sub['content'] ?? '';
    if (empty($content)) continue;

    // A. SVG data-tex
    if (preg_match_all('/<svg[^>]+data-tex="([^"]+)"/i', $content, $m)) {
        foreach ($m[1] as $raw) {
            $tex = trim(html_entity_decode($raw, ENT_QUOTES, 'UTF-8'));
            if (empty($tex)) continue;
            $totalOccurrences++;
            $uniqueExpressions[$tex]['subtopics'][] = $slug;
            $uniqueExpressions[$tex]['sources'][] = 'data-tex';
        }
    }

    // B. Display block \[ ... \]
    if (preg_match_all('/\\\\\[(.*?)\\\\\]/s', $content, $m)) {
        foreach ($m[1] as $raw) {
            $tex = trim($raw);
            if (empty($tex)) continue;
            $totalOccurrences++;
            $uniqueExpressions[$tex]['subtopics'][] = $slug;
            $uniqueExpressions[$tex]['sources'][] = 'display-block';
        }
    }

    // C. Display block $$ ... $$
    if (preg_match_all('/\$\$(.*?)\$\$/s', $content, $m)) {
        foreach ($m[1] as $raw) {
            $tex = trim($raw);
            if (empty($tex)) continue;
            $totalOccurrences++;
            $uniqueExpressions[$tex]['subtopics'][] = $slug;
            $uniqueExpressions[$tex]['sources'][] = 'double-dollar';
        }
    }

    // D. Explainer links
    if (preg_match_all('/equation-explainer\?latex=([^"\'\s&]+)/i', $content, $m)) {
        foreach ($m[1] as $raw) {
            $tex = trim(rawurldecode($raw));
            if (empty($tex)) continue;
            $totalOccurrences++;
            $uniqueExpressions[$tex]['subtopics'][] = $slug;
            $uniqueExpressions[$tex]['sources'][] = 'explainer-link';
        }
    }
}

$totalUnique = count($uniqueExpressions);
echo "[HARVEST COMPLETE] Found {$totalOccurrences} total equation occurrences ({$totalUnique} unique expressions).\n\n";

// Helper function to render a progress bar
function renderProgressBar($done, $total, $barLength = 40) {
    $percent = $total > 0 ? ($done / $total) : 1;
    $filled = (int)round($barLength * $percent);
    $empty = $barLength - $filled;
    $bar = str_repeat("█", $filled) . str_repeat("░", $empty);
    $pctText = number_format($percent * 100, 1) . "%";
    echo "\r  [{$bar}] {$pctText} ({$done}/{$total})";
    flush();
}

echo "Auditing unique math expressions against LaTeX index & AST signatures:\n";

// 5. In-Memory Resolution & Classification Pass with Live Progress Bar
$resolvedCount = 0;
$unmappedEquations = [];
$unmappedFragments = [];
$current = 0;

foreach ($uniqueExpressions as $rawTex => $meta) {
    $current++;
    if ($current % 100 === 0 || $current === $totalUnique) {
        renderProgressBar($current, $totalUnique);
    }

    $norm = $service->normalizeLatex($rawTex);
    
    // Check 1: Direct normalized LaTeX index match
    if (isset($latexIndex[$norm])) {
        $resolvedCount++;
        continue;
    }

    // Check 2: In-memory AST canonical signature match
    $canon = $service->canonicalizeLatex($rawTex);
    if (!empty($canon) && isset($astIndex[$canon])) {
        $resolvedCount++;
        continue;
    }

    // Unresolved: Classify whether it is an equation/identity
    $isEquation = (
        strpos($rawTex, '=') !== false ||
        strpos($rawTex, '\le') !== false ||
        strpos($rawTex, '\ge') !== false ||
        strpos($rawTex, '\to') !== false ||
        strpos($rawTex, '\rightarrow') !== false ||
        strpos($rawTex, '\approx') !== false ||
        strpos($rawTex, '\equiv') !== false ||
        strpos($rawTex, '\propto') !== false ||
        strpos($rawTex, '<') !== false ||
        strpos($rawTex, '>') !== false
    );
    
    $entry = [
        'raw_tex' => $rawTex,
        'normalized_key' => $norm,
        'sources' => array_unique($meta['sources']),
        'found_in' => array_values(array_unique($meta['subtopics'])),
        'sample_url' => 'http://localhost:8000/physics/equation-explainer?latex=' . rawurlencode($rawTex)
    ];

    if ($isEquation) {
        $unmappedEquations[] = $entry;
    } else {
        $unmappedFragments[] = $entry;
    }
}

echo "\n\n";

// 6. Output Summary & Statistics
$closurePct = $totalUnique > 0 ? ($resolvedCount / $totalUnique) * 100 : 100;

echo "=======================================================\n";
echo "📊 MANIFOLD RESOLUTION SUMMARY\n";
echo "=======================================================\n";
echo "Total Unique Expressions:     {$totalUnique}\n";
echo "Resolved via Index / AST:     {$resolvedCount} (" . number_format($closurePct, 2) . "%)\n";
echo "Unmapped Physical Identities: " . count($unmappedEquations) . "\n";
echo "Unmapped Math Fragments:      " . count($unmappedFragments) . "\n";
echo "Manifold Closure Metric:      " . number_format($closurePct, 3) . "%\n";
echo "=======================================================\n\n";

if (!empty($unmappedEquations)) {
    echo "📋 Top Unmapped Physical Identities (Priority Candidates for Alias Index):\n";
    $sample = array_slice($unmappedEquations, 0, 15);
    foreach ($sample as $idx => $item) {
        $num = $idx + 1;
        $sub = implode(', ', array_slice($item['found_in'], 0, 2));
        echo "  [{$num}] TeX: {$item['raw_tex']}\n";
        echo "      Subtopic:   {$sub}\n";
        echo "      URL:        {$item['sample_url']}\n\n";
    }
}

// 7. Save JSON Delta Report
$scratchDir = __DIR__ . '/../scratch';
if (!is_dir($scratchDir)) {
    mkdir($scratchDir, 0755, true);
}
$reportPath = $scratchDir . '/unmapped_prose_equations.json';
file_put_contents($reportPath, json_encode([
    'timestamp' => date('c'),
    'total_unique' => $totalUnique,
    'resolved_count' => $resolvedCount,
    'closure_percent' => $closurePct,
    'unmapped_equations_count' => count($unmappedEquations),
    'unmapped_fragments_count' => count($unmappedFragments),
    'unmapped_equations' => $unmappedEquations,
    'unmapped_fragments' => $unmappedFragments
], JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));

echo "[REPORT SAVED] Full delta details saved to: {$reportPath}\n";
