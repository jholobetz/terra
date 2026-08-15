<?php

require_once __DIR__ . '/../vendor/autoload.php';
$config = require __DIR__ . '/../app/config/config.php';
require_once __DIR__ . '/../app/config/bootstrap.php';

echo "======================================================\n";
echo "Physics Lab RBAC & Formula Review System Verification\n";
echo "======================================================\n\n";

$pdo = Flight::db();
$auth = Flight::authService();
$reviewService = Flight::formulaReviewService();

// 1. Verify Seeded Users
echo "[TEST 1] Verifying Seeded RBAC Users...\n";
$users = $pdo->query("SELECT id, role, display_name FROM users WHERE oauth_provider = 'dev_mock' ORDER BY role")->fetchAll(PDO::FETCH_ASSOC);
if (count($users) < 4) {
    echo "  [FAIL] Expected at least 4 dev users, found " . count($users) . "\n";
    exit(1);
}
foreach ($users as $u) {
    echo "  [OK] User #{$u['id']} - Role: {$u['role']} ({$u['display_name']})\n";
}

// 2. Verify Role Hierarchy Permissions
echo "\n[TEST 2] Verifying Role Hierarchy Gates...\n";
$auth->switchDevRole('guest');
$guest = $auth->getCurrentUser();
assert(!$auth->hasRole('contributor', $guest), "Guest should NOT have contributor access");
echo "  [OK] Guest cannot access Contributor actions.\n";

$auth->switchDevRole('contributor');
$contributor = $auth->getCurrentUser();
assert($auth->hasRole('contributor', $contributor), "Contributor should have contributor access");
assert(!$auth->hasRole('curator', $contributor), "Contributor should NOT have curator access");
echo "  [OK] Contributor has Suggestion privileges, but blocked from direct curation.\n";

$auth->switchDevRole('curator');
$curator = $auth->getCurrentUser();
assert($auth->hasRole('contributor', $curator), "Curator should have contributor access");
assert($auth->hasRole('curator', $curator), "Curator should have curator access");
echo "  [OK] Curator has Direct Curation & Approval privileges.\n";

// 3. Test Contributor Staging Workflow
echo "\n[TEST 3] Testing Contributor Staged Review Workflow...\n";
$formulaId = 'generalized-force-component-lagrangian-definition';
$testLatex = 'F_i = \frac{\partial L}{\partial q_i}';
$testHint = "Limiting Cases & Boundaries: 1. Conservative Systems: Verified.";

$reviewId = $reviewService->createSuggestion($contributor->id, $formulaId, $testLatex, ['limits_and_boundary' => $testHint], $testHint);
echo "  [OK] Suggestion #{$reviewId} created for {$formulaId}.\n";

$pendingReviews = $reviewService->getReviews('pending', $formulaId);
$found = false;
foreach ($pendingReviews as $r) {
    if ((int)$r['id'] === $reviewId) {
        $found = true;
        break;
    }
}
assert($found, "Review #{$reviewId} should be in pending review queue");
echo "  [OK] Review #{$reviewId} confirmed in pending queue.\n";

// 4. Test Curator Approval & Audit Logging
echo "\n[TEST 4] Testing Curator Approval & Audit Log Synchronization...\n";
$approveResult = $reviewService->approveReview($reviewId, $curator->id);
echo "  [OK] Review #{$reviewId} approved and applied directly.\n";

// Check audit log record
$auditStmt = $pdo->prepare("SELECT * FROM formula_audit_logs WHERE formula_id = ? ORDER BY created_at DESC LIMIT 1");
$auditStmt->execute([$formulaId]);
$log = $auditStmt->fetch(PDO::FETCH_ASSOC);
assert($log !== false, "Audit log entry must be created");
assert($log['action'] === 'approved_review', "Audit action must be 'approved_review'");
echo "  [OK] Audit log verified: action={$log['action']}, user_id={$log['user_id']}\n";

// 5. Test Shard & DB Synchronization
echo "\n[TEST 5] Verifying Shard and MariaDB sync...\n";
$shardFile = $reviewService->getShardPathForFormula($formulaId);
$shardData = json_decode(file_get_contents($shardFile), true);
assert(isset($shardData[$formulaId]), "Shard must contain formula");
assert($shardData[$formulaId]['equation'] === $testLatex, "Shard equation must match approved latex");

$dbFormula = $pdo->query("SELECT * FROM formulas WHERE id = '{$formulaId}'")->fetch(PDO::FETCH_ASSOC);
assert($dbFormula['equation'] === $testLatex, "MariaDB equation must match approved latex");
assert($dbFormula['equation_svg'] === null, "MariaDB equation_svg must be NULL for dynamic MathJax");
echo "  [OK] Shard and MariaDB verified in perfect sync.\n";

echo "\n[SUCCESS] ALL RBAC & FORMULA REVIEW INTEGRATION TESTS PASSED!\n";
echo "======================================================\n";
