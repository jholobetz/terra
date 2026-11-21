<?php
/**
 * Terra Physics Lab — Zero-Undefined-Click Prose Equation Auditor
 *
 * Mirrors public/js/mathjax_inspector.js :: isSingleVariableToken() to verify that
 * every clickable <svg data-tex="..."> expression in target subtopic(s) resolves to a
 * real canonical formula in formulas_latex_index.json or the shard AST index.
 *
 * Usage:
 *   php scripts/audit_clickable_equations.php <slug1> [slug2 ...]
 *   php scripts/audit_clickable_equations.php --domain fluids-nonlinear
 */

require_once __DIR__ . '/../app/logic/LatexSanitizer.php';

$root = dirname(__DIR__);
$san = new \app\logic\LatexSanitizer();
$idx = json_decode(file_get_contents($root . '/app/config/formulas_latex_index.json'), true) ?: [];

// Build AST index from all 256 formula shards
$ast = [];
foreach (glob($root . '/app/config/content/formulas/*/shard_*.json') as $sf) {
    $sd = json_decode(file_get_contents($sf), true) ?: [];
    foreach ($sd as $fid => $f) {
        $eq = $f['equation'] ?? '';
        if (strpos($eq, '<svg') === 0 && preg_match('/data-tex="([^"]+)"/i', $eq, $m)) {
            $eq = html_entity_decode($m[1], ENT_QUOTES, 'UTF-8');
        }
        $canon = $san->canonicalizeLatex($eq);
        if ($canon && !isset($ast[$canon])) {
            $ast[$canon] = $fid;
        }
    }
}

function isSingleVariableToken(string $latex): bool
{
    $clean = trim($latex);
    if ($clean === '') return true;
    if (preg_match('/^-?\d+(\.\d+)?$/', $clean)) return true;

    $strippedPrefix = trim(preg_replace('/^(?:[-+]|\s*\\\\(?:pm|mp|Delta|delta|nabla)\s+)/', '', $clean));
    if ($strippedPrefix === '') return true;

    // 1. Single Latin letter
    if (preg_match('/^[a-zA-Z]$/', $strippedPrefix)) return true;

    // 2. Single formatted letter macro
    if (preg_match('/^\\\\[a-zA-Z]+\{[a-zA-Z0-9]+\}$/', $strippedPrefix)) return true;

    // 3. Single Greek letter / standalone TeX symbol
    if (preg_match('/^\\\\[a-zA-Z]+$/', $strippedPrefix)) return true;

    // 4. Single variable with simple subscript/superscript
    $singleVarAtom = '/^(?:\\\\?[a-zA-Z]|\\\\(?:mathbf|vec|mathcal|hat|mathbb|mathrm|text)\{[a-zA-Z0-9]+\})+(?:_(?:\{[^=+\s]*\}|[a-zA-Z0-9]+)|(?:\^(?:\{[^=+\s]*\}|-?[a-zA-Z0-9]+)))*$/';
    if (preg_match($singleVarAtom, $strippedPrefix)) {
        $noNegExp = preg_replace('/\^\{-[0-9]+\}/', '', $strippedPrefix);
        if (!preg_match('/(=|\+|-|\\\\times|\\\\int|\\\\sum|\\\\frac|\\\\partial|\\\\cdot|\\\\to|\\\\approx|\\\\leq|\\\\geq)/', $noNegExp)) {
            return true;
        }
    }

    // 5. Simple function notation f(x), u(x, t), \mathrm{Ra}(k)
    if (preg_match('/^(.+?)\(\s*([a-zA-Z]|\\\\[a-zA-Z]+)(?:\s*,\s*([a-zA-Z]|\\\\[a-zA-Z]+))?\s*\)$/', $strippedPrefix, $m)) {
        $head = trim($m[1]);
        if (!preg_match('/^(?:\\\\?(?:sin|cos|tan|exp|log|ln|sinh|cosh|tanh|sech|arsinh|arcsin|arccos|arctan|det|tr|Tr))$/', $head)) {
            if (isSingleVariableToken($head)) {
                return true;
            }
        }
    }

    // 6. Simple nuclide/isotope notation
    if (preg_match('/^\{\}\^\{\d+\}\\\\(?:text|mathrm)\{[A-Za-z]{1,3}\}$/', $clean)) return true;

    return false;
}

// Parse CLI arguments
$args = array_slice($argv, 1);
if (empty($args)) {
    fwrite(STDERR, "Usage: php scripts/audit_clickable_equations.php <slug1> [slug2 ...] | --domain <domain>\n");
    exit(2);
}

$targetSlugs = [];
$domainFilter = null;
for ($i = 0; $i < count($args); $i++) {
    if ($args[$i] === '--domain' && isset($args[$i + 1])) {
        $domainFilter = $args[++$i];
    } else {
        $targetSlugs[] = $args[$i];
    }
}

$allSubtopics = [];
$contentFiles = $domainFilter
    ? [$root . "/app/config/content/{$domainFilter}.json"]
    : glob($root . '/app/config/content/*.json');

foreach ($contentFiles as $cf) {
    $base = basename($cf);
    if (in_array($base, ['categories.json', 'search_index.json', 'constants.json', 'entities.json', 'particles.json', 'compiled_trie_regex.json', 'notation.json'], true)) {
        continue;
    }
    if (!file_exists($cf)) continue;
    $data = json_decode(file_get_contents($cf), true);
    if (!is_array($data)) continue;
    foreach ($data as $slug => $entry) {
        if (!is_array($entry) || !isset($entry['content'])) continue;
        if (!empty($targetSlugs) && !in_array($slug, $targetSlugs, true)) continue;
        $allSubtopics[$slug] = $entry;
    }
}

$totalUndefined = 0;
foreach ($allSubtopics as $slug => $entry) {
    $content = $entry['content'] ?? '';
    preg_match_all('/data-tex="([^"]+)"/i', $content, $m);
    $unique = array_values(array_unique(array_map(fn($x) => html_entity_decode($x, ENT_QUOTES, 'UTF-8'), $m[1])));

    $defined = [];
    $undefined = [];
    $nonClick = 0;

    foreach ($unique as $tex) {
        if (isSingleVariableToken($tex)) {
            $nonClick++;
            continue;
        }
        $norm = $san->normalizeLatex($tex);
        $canon = $san->canonicalizeLatex($tex);
        if (isset($idx[$norm]) || ($canon && isset($ast[$canon]))) {
            $defined[] = $tex;
        } else {
            $undefined[] = $tex;
        }
    }

    $totalUndefined += count($undefined);
    $status = count($undefined) === 0 ? 'OK' : 'NEEDS_DEF';
    echo sprintf("[%s] %-34s | defined=%2d | undefined_clickable=%2d | non_clickable=%2d\n", $status, $slug, count($defined), count($undefined), $nonClick);
    foreach ($undefined as $u) {
        echo "    -> {$u}\n";
    }
}

echo "\nTotal undefined clickable expressions: {$totalUndefined}\n";
exit($totalUndefined > 0 ? 1 : 0);
