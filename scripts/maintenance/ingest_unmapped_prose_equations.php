<?php
/**
 * 📥 Canonical Ingestion Engine for Unmapped Prose Equations
 * Converts unmapped physical identities from subtopic prose into fully-structured
 * Platinum formula entries in the 256 formula shards using PhysicsService::saveFormula().
 */

require_once __DIR__ . '/../../vendor/autoload.php';
require_once __DIR__ . '/../../app/config/bootstrap.php';

use App\Logic\PhysicsService;

$app = Flight::app();
$service = new PhysicsService($app);

$isDryRun = in_array('--dry-run', $argv);
$limit = null;
foreach ($argv as $arg) {
    if (strpos($arg, '--limit=') === 0) {
        $limit = (int)substr($arg, 8);
    }
}

echo "=======================================================\n";
echo "📥 Canonical Prose Equation Ingestion Engine" . ($isDryRun ? " [DRY-RUN]" : "") . "\n";
echo "=======================================================\n\n";

// 1. Load Unmapped Equations Report
$reportFile = __DIR__ . '/../../scratch/unmapped_prose_equations.json';
if (!file_exists($reportFile)) {
    die("[ERROR] Report file not found at: {$reportFile}\n");
}
$reportData = json_decode(file_get_contents($reportFile), true) ?: [];
$unmapped = $reportData['unmapped_equations'] ?? [];

// Filter out equations that were already indexed in earlier passes
$indexFile = __DIR__ . '/../../app/config/formulas_latex_index.json';
$latexIndex = json_decode(file_get_contents($indexFile), true) ?: [];

$candidates = [];
foreach ($unmapped as $item) {
    $norm = $item['normalized_key'];
    if (!isset($latexIndex[$norm])) {
        // Also check if already resolvable via service
        $existing = $service->searchFormulaByLatex($item['raw_tex']);
        if (!$existing) {
            $candidates[] = $item;
        }
    }
}

echo "[INFO] Found " . count($candidates) . " genuine unmapped physical equations to ingest.\n";
if ($limit) {
    $candidates = array_slice($candidates, 0, $limit);
    echo "[INFO] Processing limited batch of " . count($candidates) . " formulas.\n";
}

echo "\n";

// 2. Helper to extract title and semantic variables
function extractSemanticVariables(string $latex): array {
    $vars = [];
    
    // Common physics variable symbol map
    $symbolMap = [
        '\\mathbf{R}_{CM}' => ['name' => 'Center of Mass Position Vector', 'type' => 'vector', 'unit' => 'm', 'description' => 'Position vector of the system center of mass in 3D Euclidean space.'],
        '\\mathbf{r}_i' => ['name' => 'Particle Position Vector', 'type' => 'vector', 'unit' => 'm', 'description' => 'Position vector of the i-th individual particle.'],
        'm_i' => ['name' => 'Particle Mass', 'type' => 'scalar', 'unit' => 'kg', 'description' => 'Inertial mass of the i-th particle.'],
        'M' => ['name' => 'Total Mass', 'type' => 'scalar', 'unit' => 'kg', 'description' => 'Total combined mass of the physical system.'],
        '\\mathcal{H}' => ['name' => 'Hamiltonian Function', 'type' => 'scalar', 'unit' => 'J', 'description' => 'Total energy function in phase space coordinates $(q, p)$.'],
        '\\mathcal{L}' => ['name' => 'Lagrangian Function', 'type' => 'scalar', 'unit' => 'J', 'description' => 'Difference between kinetic and potential energy in state space.'],
        'p_i' => ['name' => 'Canonical Momentum', 'type' => 'scalar', 'unit' => 'kg m/s', 'description' => 'Conjugate generalized momentum corresponding to coordinate $q_i$.'],
        'q^i' => ['name' => 'Generalized Coordinate', 'type' => 'scalar', 'unit' => 'dimensionless / m', 'description' => 'Degrees of freedom parameterizing system configuration.'],
        '\\dot{q}^i' => ['name' => 'Generalized Velocity', 'type' => 'scalar', 'unit' => '1/s / m/s', 'description' => 'Time rate of change of generalized coordinate $q^i$.'],
        't' => ['name' => 'Time Parameter', 'type' => 'scalar', 'unit' => 's', 'description' => 'Temporal coordinate.'],
        'V_{eff}' => ['name' => 'Effective Potential', 'type' => 'scalar', 'unit' => 'J', 'description' => 'Combined true potential and centrifugal barrier potential.'],
        '\\mu' => ['name' => 'Reduced Mass', 'type' => 'scalar', 'unit' => 'kg', 'description' => 'Effective inertial mass in two-body central motion.'],
        'l' => ['name' => 'Angular Momentum Magnitude', 'type' => 'scalar', 'unit' => 'kg m^2 / s', 'description' => 'Conserved orbital angular momentum.'],
        'f_\\alpha' => ['name' => 'Constraint Function', 'type' => 'scalar', 'unit' => 'dimensionless', 'description' => 'Holonomic geometric constraint relation.'],
        '\\delta S' => ['name' => 'Action Variation', 'type' => 'scalar', 'unit' => 'J s', 'description' => 'First variation of Hamilton\'s principle action integral.']
    ];

    foreach ($symbolMap as $sym => $info) {
        if (strpos($latex, $sym) !== false) {
            $vars[$sym] = $info;
        }
    }

    return $vars;
}

// 3. Ingestion Loop
$ingestedCount = 0;

foreach ($candidates as $idx => $item) {
    $rawTex = $item['raw_tex'];
    $subtopics = $item['found_in'];
    $primarySub = !empty($subtopics) ? $subtopics[0] : 'theoretical-physics';

    // Generate synthesized explanation
    $synth = $service->synthesizeFormulaExplanation($rawTex);
    
    // Generate clean unique ID
    $title = $synth['title'] ?? 'Physical Relation';
    $slugTitle = strtolower(preg_replace('/[^a-zA-Z0-9]+/', '-', trim($title)));
    $slugTitle = trim($slugTitle, '-');
    if (empty($slugTitle) || $slugTitle === 'custom-physical-relation' || $slugTitle === 'physical-relation') {
        $slugTitle = $primarySub . '-identity';
    }
    
    $hashSuffix = substr(md5($rawTex), 0, 8);
    $formulaId = $slugTitle . '-' . $hashSuffix;

    $semVars = extractSemanticVariables($rawTex);

    $formulaRecord = [
        'title' => $title,
        'equation' => $rawTex,
        'conceptual_definition' => $synth['intro'] ?? "Fundamental mathematical relation formulated within {$primarySub}.",
        'intuitive_summary' => $synth['summary'] ?? "Defines key conservation, boundary, or dynamical balance relations in the physical manifold.",
        'interpretation' => $synth['interpretation'] ?? "The formula establishes how configuration coordinates or field variations evolve under physical constraints.",
        'symmetry_origin' => $synth['symmetry'] ?? "Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance.",
        'limits_and_boundary' => $synth['limits'] ?? "Subject to asymptotic boundary conditions and non-relativistic conservation limits.",
        'semantic_variables' => (object)$semVars,
        'derivation_type' => 'THEORETICAL_DERIVATION',
        'status' => 'platinum',
        'parent_formula_id' => 'Axiom',
        'subcomponents' => []
    ];

    $num = $idx + 1;
    echo "  [{$num}] Formula ID: {$formulaId}\n";
    echo "      Title:    {$formulaRecord['title']}\n";
    echo "      Equation: {$formulaRecord['equation']}\n";
    echo "      Subtopic: {$primarySub}\n";

    if (!$isDryRun) {
        $saved = $service->saveFormula($formulaId, $formulaRecord);
        if ($saved) {
            echo "      ✓ Ingested to Shard & DB!\n\n";
            $ingestedCount++;
        } else {
            echo "      ✗ Ingestion failed.\n\n";
        }
    } else {
        echo "      [DRY-RUN] Skipped write.\n\n";
    }
}

echo "=======================================================\n";
echo "Ingestion Summary: " . ($isDryRun ? "Tested {$limit} candidates in dry-run mode." : "Successfully ingested {$ingestedCount} formulas.") . "\n";
echo "=======================================================\n";
