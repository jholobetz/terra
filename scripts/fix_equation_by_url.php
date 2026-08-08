<?php
/**
 * CLI Tool: fix_equation_by_url.php
 * 
 * Audits, decorrupts, and repairs LaTeX, SVG rendering, and database/shard consistency
 * for a formula given a URL, Formula ID, or raw LaTeX query.
 * 
 * Usage:
 *   php scripts/fix_equation_by_url.php "http://localhost:8000/physics/equation-explainer?latex=S%20%3D%20%5Cint%20L(q_i%2C%20%5Cdot%7Bq%7D_i%2C%20t)%20dt"
 *   php scripts/fix_equation_by_url.php "http://localhost:8000/physics/equation-explainer?id=meissner-flux-expulsion-ident-3440877a"
 *   php scripts/fix_equation_by_url.php "meissner-flux-expulsion-ident-3440877a"
 */

if (php_sapi_name() !== 'cli') {
    die("This script can only be run from the command line.\n");
}

$input = $argv[1] ?? '';
if (empty($input)) {
    echo "Usage: php scripts/fix_equation_by_url.php <URL|ID|LaTeX>\n";
    exit(1);
}

echo "=======================================================\n";
echo "Terra Equation Repair Engine\n";
echo "Input: {$input}\n";
echo "=======================================================\n\n";

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

// 2. Connect to MariaDB
try {
    $pdo = new PDO('mysql:host=127.0.0.1;dbname=physicslab;charset=utf8mb4', 'doc', 'DIM^10$ymJ@zz', [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC
    ]);
} catch (\Exception $e) {
    echo "[ERROR] Database connection failed: " . $e->getMessage() . "\n";
    exit(1);
}

// 3. Resolve Target Formula from DB
$formulaRecord = null;
if (!empty($targetId)) {
    $stmt = $pdo->prepare("SELECT * FROM formulas WHERE id = ?");
    $stmt->execute([$targetId]);
    $formulaRecord = $stmt->fetch();
}

if (!$formulaRecord && !empty($targetLatex)) {
    // Try exact equation match first
    $stmt = $pdo->prepare("SELECT * FROM formulas WHERE equation = ?");
    $stmt->execute([$targetLatex]);
    $formulaRecord = $stmt->fetch();

    if (!$formulaRecord) {
        // Try LIKE match
        $stmt = $pdo->prepare("SELECT * FROM formulas WHERE equation LIKE ? LIMIT 1");
        $stmt->execute(['%' . $targetLatex . '%']);
        $formulaRecord = $stmt->fetch();
    }
}

if (!$formulaRecord && !empty($targetId)) {
    echo "[WARN] Formula ID '{$targetId}' not found in database. Searching JSON shards...\n";
}

// 4. Locate Shard File
$formulaId = $formulaRecord['id'] ?? $targetId;
if (empty($formulaId)) {
    echo "[ERROR] Could not resolve formula ID from input.\n";
    exit(1);
}

$hexPrefix = substr(md5($formulaId), 0, 2);
$baseDir = __DIR__ . '/../app/config/content/formulas/';
$shardFile = $baseDir . $hexPrefix . '/shard_' . $hexPrefix . '.json';

if (!file_exists($shardFile)) {
    // Try legacy directory structure
    $shardFile = $baseDir . 'shard_' . $hexPrefix . '.json';
}

if (!file_exists($shardFile)) {
    echo "[ERROR] Shard file for formula ID '{$formulaId}' not found at md5 prefix '{$hexPrefix}'.\n";
    exit(1);
}

echo "[INFO] Target Formula ID: {$formulaId}\n";
echo "[INFO] Canonical Shard Path: {$shardFile}\n\n";

// 5. Load and Audit Shard Data
$shardContent = file_get_contents($shardFile);
$shardData = json_decode($shardContent, true);

if (!isset($shardData[$formulaId])) {
    echo "[ERROR] Formula '{$formulaId}' missing inside shard {$shardFile}.\n";
    exit(1);
}

$formulaData = $shardData[$formulaId];
$originalEq = $formulaData['equation'] ?? '';
$repairsMade = [];

// Clean LaTeX Equation
$cleanEq = $originalEq;
if (!empty($targetLatex) && ($cleanEq === '' || strpos($cleanEq, '<svg') === 0 || strpos($cleanEq, '<div') === 0)) {
    $cleanEq = $targetLatex;
    $repairsMade[] = "Restored raw LaTeX equation from query: {$cleanEq}";
} else if (strpos($cleanEq, 'dp^') !== false && strpos($cleanEq, '\frac') === false) {
    // Convert slash derivative to fraction
    $cleanEq = preg_replace('/dp\^?\\\\?([a-zA-Z]+)\/d\\\\?([a-zA-Z]+)/', '\frac{dp^\1}{d\\\2}', $cleanEq);
    $repairsMade[] = "Converted slash derivative to fraction notation: {$cleanEq}";
}

// Decorrupt Prose Fields
function sanitizeProseTeX(string $text): string {
    // 1. Fix mixed inline TeX constructs like: χ_m = -$\frac{μ_0 N Z e^2}{6m_e}$ ⟨ r^2 ⟩
    $text = preg_replace('/[χ\chi]_[m]\s*=\s*-\s*\$\\s*\\\\frac\{[^}]+\}\{[^}]+\}\s*\$\s*[⟨<]\s*r\^2\s*[⟩>]/u', '$\\chi_m = -\\frac{\\mu_0 N Z e^2}{6m_e} \\langle r^2 \\rangle$', $text);

    // 2. Unicode & plain text symbol replacements
    $text = str_replace('χ_m', '$\\chi_m$', $text);
    $text = str_replace('μ_0', '$\\mu_0$', $text);
    $text = str_replace('4π', '$4\\pi$', $text);
    $text = preg_replace('/(?<!\\\\|\{)m_e(?!\})/u', '$m_e$', $text);
    $text = preg_replace('/[⟨<]\s*r\^2\s*[⟩>]/u', '$\\langle r^2 \\rangle$', $text);
    $text = str_replace('χ_', '$\\chi_m$', $text);

    // 3. Clean up double $$ or nested $6$m_e$}
    $text = str_replace('{6$m_e$}', '{6m_e}', $text);
    $text = preg_replace('/\$\$+/', '$', $text);
    $text = preg_replace('/\\$\\$\\s*/', '$', $text);

    // 4. Standard TeX fixes
    $text = preg_replace('/\\\\frac\{dp\^\$\s*u\}\{dau\}/i', '\\frac{dp^\\mu}{d\\tau}', $text);
    $text = preg_replace('/F\^\{u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
    $text = preg_replace('/F\^\{\$u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
    $text = preg_replace('/U_\$\\rho/i', 'U_\\rho', $text);
    $text = preg_replace('/You_\s*\$\s*u\s*\$to\$/i', 'four-velocity $U_\\mu$ to', $text);
    $text = preg_replace('/extbf/i', '\\mathbf', $text);
    $text = str_replace('dau', '\\tau', $text);
    return $text;
}

if (isset($formulaData['interpretation'])) {
    $newInterp = sanitizeProseTeX($formulaData['interpretation']);
    if ($newInterp !== $formulaData['interpretation']) {
        $formulaData['interpretation'] = $newInterp;
        $repairsMade[] = "Sanitized corrupted TeX strings in 'interpretation'";
    }
}

if (isset($formulaData['limits_and_boundary'])) {
    $newLimits = sanitizeProseTeX($formulaData['limits_and_boundary']);
    if ($newLimits !== $formulaData['limits_and_boundary']) {
        $formulaData['limits_and_boundary'] = $newLimits;
        $repairsMade[] = "Sanitized corrupted TeX strings in 'limits_and_boundary'";
    }
}

// Update Equation in Shard Data
$formulaData['equation'] = $cleanEq;
$shardData[$formulaId] = $formulaData;

// 6. Write Back to JSON Shard File
file_put_contents($shardFile, json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
echo "[OK] Saved updated formula definition to shard: {$shardFile}\n";

// 7. Update MariaDB Database
$stmt = $pdo->prepare("UPDATE formulas SET equation = ?, equation_svg = NULL, interpretation = ?, limits_and_boundary = ?, semantic_variables = ? WHERE id = ?");
$stmt->execute([
    $cleanEq,
    $formulaData['interpretation'] ?? null,
    $formulaData['limits_and_boundary'] ?? null,
    isset($formulaData['semantic_variables']) ? json_encode($formulaData['semantic_variables'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : null,
    $formulaId
]);
echo "[OK] Updated MariaDB formulas table record (equation_svg set to NULL).\n";

if (!empty($repairsMade)) {
    echo "\nSummary of Repairs Applied:\n";
    foreach ($repairsMade as $rep) {
        echo "  - {$rep}\n";
    }
} else {
    echo "\nNo structural TeX corruptions found. SVG blob cleared and LaTeX synced.\n";
}

// 8. Verify via API Request
$verifyUrl = "http://localhost:8000/physics/api/explain?id=" . urlencode($formulaId);
echo "\nVerifying repair via API: {$verifyUrl} ...\n";

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $verifyUrl);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 5);
$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

if ($httpCode === 200 && !empty($response)) {
    $json = json_decode($response, true);
    if (!empty($json['success']) && !empty($json['formula'])) {
        echo "[VERIFIED] API returned HTTP 200 with success = true!\n";
        echo "  - Formula Title: " . ($json['formula']['title'] ?? 'N/A') . "\n";
        echo "  - Clean Equation: " . ($json['formula']['equation'] ?? 'N/A') . "\n";
        echo "  - Equation SVG: " . (is_null($json['formula']['equation_svg'] ?? null) ? 'NULL (Clean Dynamic MathJax)' : 'POPULATED') . "\n";
    } else {
        echo "[WARN] API response status code 200 but returned unexpected payload.\n";
    }
} else {
    echo "[WARN] Could not curl local API endpoint (HTTP {$httpCode}). Make sure dev server is running.\n";
}

echo "\nDone!\n";
