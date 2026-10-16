import json
import os
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def _eval_auth_scenario(env_vars: dict, server_vars: dict) -> dict:
    """Runs a sandboxed PHP snippet to evaluate AuthService behavior under specific env/server state."""
    php_code = """
    require 'vendor/autoload.php';
    require_once 'app/logic/AuthService.php';
    foreach (json_decode($argv[1], true) as $k => $v) {
        $_SERVER[$k] = $v;
    }
    $auth = new \\app\\logic\\AuthService();
    $user = $auth->getCurrentUser();
    echo json_encode([
        'is_studio' => $auth->isLocalDevStudio(),
        'role' => $user->role,
        'has_curator' => $auth->hasRole('curator', $user),
        'has_admin' => $auth->hasRole('admin', $user),
        'can_switch_admin' => $auth->switchDevRole('admin'),
    ]);
    """
    full_env = os.environ.copy()
    full_env.pop("APP_ENV", None)
    full_env.pop("TERRA_ADMIN_KEY", None)
    full_env.update(env_vars)

    res = subprocess.run(
        ["php", "-r", php_code, json.dumps(server_vars)],
        cwd=str(WORKSPACE_ROOT),
        env=full_env,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(res.stdout.strip())


def test_php_syntax_auth_and_controller():
    """Verifies zero PHP syntax errors in AuthService, decomposed Services, and all split Controllers."""
    for rel_path in [
        "app/logic/AuthService.php",
        "app/logic/LatexSanitizer.php",
        "app/logic/ShardSyncService.php",
        "app/logic/PhysicsService.php",
        "app/controllers/PhysicsController.php",
        "app/controllers/AdminController.php",
        "app/controllers/ReviewController.php",
        "app/config/routes.php",
        "app/config/services.php",
    ]:
        res = subprocess.run(
            ["php", "-l", rel_path],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"PHP lint failed for {rel_path}: {res.stderr}"


def test_local_studio_grants_admin_authority():
    """Verifies local development loopback requests retain frictionless single-developer admin authority."""
    out = _eval_auth_scenario(
        {"APP_ENV": "development"},
        {"REMOTE_ADDR": "127.0.0.1"},
    )
    assert out["is_studio"] is True
    assert out["role"] == "admin"
    assert out["has_curator"] is True
    assert out["has_admin"] is True
    assert out["can_switch_admin"] is True


def test_public_visitor_restricted_to_guest():
    """Verifies external IP addresses are strictly read-only guests and cannot escalate roles."""
    out = _eval_auth_scenario(
        {"APP_ENV": "development"},
        {"REMOTE_ADDR": "203.0.113.42"},
    )
    assert out["is_studio"] is False
    assert out["role"] == "guest"
    assert out["has_curator"] is False
    assert out["has_admin"] is False
    assert out["can_switch_admin"] is False


def test_reverse_proxy_external_ip_blocked():
    """Verifies external requests forwarded through a local reverse proxy (127.0.0.1) are treated as guests."""
    out = _eval_auth_scenario(
        {"APP_ENV": "development"},
        {"REMOTE_ADDR": "127.0.0.1", "HTTP_X_FORWARDED_FOR": "198.51.100.77, 127.0.0.1"},
    )
    assert out["is_studio"] is False
    assert out["role"] == "guest"
    assert out["has_curator"] is False
    assert out["has_admin"] is False
    assert out["can_switch_admin"] is False


def test_production_env_blocks_implicit_studio_even_on_loopback():
    """Verifies APP_ENV=production disables implicit studio admin authority without an explicit token."""
    out = _eval_auth_scenario(
        {"APP_ENV": "production"},
        {"REMOTE_ADDR": "127.0.0.1"},
    )
    assert out["is_studio"] is False
    assert out["role"] == "guest"
    assert out["has_admin"] is False


def test_production_admin_key_override():
    """Verifies explicit TERRA_ADMIN_KEY header grants admin authority in production."""
    out = _eval_auth_scenario(
        {"APP_ENV": "production", "TERRA_ADMIN_KEY": "super_secret_prod_token"},
        {"REMOTE_ADDR": "203.0.113.42", "HTTP_X_TERRA_ADMIN_KEY": "super_secret_prod_token"},
    )
    assert out["is_studio"] is True
    assert out["role"] == "admin"
    assert out["has_admin"] is True


def test_controller_split_and_cas_ratelimit():
    """Verifies AdminController and ReviewController separation and CAS sliding-window rate limiting."""
    php_code = """
    define('PROJECT_ROOT', getcwd());
    require 'vendor/autoload.php';
    require_once 'app/controllers/PhysicsController.php';
    require_once 'app/controllers/AdminController.php';
    require_once 'app/controllers/ReviewController.php';

    $app = Flight::app();
    $app->register('adminController', \\app\\controllers\\AdminController::class, [$app]);
    $app->register('reviewController', \\app\\controllers\\ReviewController::class, [$app]);
    $ctrl = new \\app\\controllers\\PhysicsController($app);

    $testIp = '198.51.100.250_' . uniqid();
    $r1 = $ctrl->consumeCasRateLimit($testIp, 2, 60);
    $r2 = $ctrl->consumeCasRateLimit($testIp, 2, 60);
    $r3 = $ctrl->consumeCasRateLimit($testIp, 2, 60);

    // Clean up test bucket file
    $bucket = sys_get_temp_dir() . '/terra_cas_ratelimit/' . hash('sha256', $testIp) . '.json';
    if (file_exists($bucket)) {
        @unlink($bucket);
    }

    echo json_encode([
        'r1' => $r1,
        'r2' => $r2,
        'r3' => $r3,
        'has_admin_assess' => method_exists($app->adminController(), 'adminAssess'),
        'has_review_apply' => method_exists($app->reviewController(), 'apiApplyRepair'),
    ]);
    """
    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=str(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(res.stdout.strip())
    assert out["r1"] is True
    assert out["r2"] is True
    assert out["r3"] is False
    assert out["has_admin_assess"] is True
    assert out["has_review_apply"] is True


def test_service_and_explainer_decomposition():
    """Verifies LatexSanitizer, ShardSyncService, ExplainerTokenizer, and ExplainerCards decomposition."""
    php_code = """
    define('PROJECT_ROOT', getcwd());
    require 'vendor/autoload.php';
    require_once 'app/logic/LatexSanitizer.php';
    require_once 'app/logic/ShardSyncService.php';

    $sanitizer = new \\app\\logic\\LatexSanitizer();
    $norm1 = $sanitizer->normalizeLatex('\\\\mathbf{F} = m \\\\mathbf{a}');
    $norm2 = $sanitizer->normalizeLatex('F = a m');
    $synth = $sanitizer->synthesizeFormulaExplanation('\\\\mathbf{F} = m \\\\mathbf{a}');

    echo json_encode([
        'commutes' => ($norm1 === $norm2),
        'synth_title' => $synth['title'] ?? '',
    ]);
    """
    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=str(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(res.stdout.strip())
    assert out["commutes"] is True
    assert "Newton's Second Law" in out["synth_title"]

    # Verify JS decomposition files exist and export expected methods
    for js_rel, expected_fn in [
        ("public/js/explainer_tokenizer.js", "extractAllMathTokens("),
        ("public/js/explainer_cards.js", "renderKnowledgeGraphCard("),
        ("public/js/explainer_curator.js", "triggerFixLatex("),
    ]:
        js_path = WORKSPACE_ROOT / js_rel
        assert js_path.exists(), f"Missing decomposed JS module: {js_rel}"
        assert expected_fn in js_path.read_text(encoding="utf-8")


def test_atomic_json_file_locking():
    """Verifies PhysicsService::updateJsonFileLocked performs atomic read-modify-write under LOCK_EX."""
    php_code = """
    define('PROJECT_ROOT', getcwd());
    require 'vendor/autoload.php';
    require_once 'app/logic/PhysicsService.php';

    $svc = new \\app\\logic\\PhysicsService(new \\flight\\Engine());
    $ref = new \\ReflectionMethod($svc, 'updateJsonFileLocked');

    $tmpFile = sys_get_temp_dir() . '/terra_lock_test_' . uniqid() . '.json';
    $ref->invoke($svc, $tmpFile, function(array $map) {
        $map['alpha'] = 1;
        return $map;
    });
    $ref->invoke($svc, $tmpFile, function(array $map) {
        $map['beta'] = 2;
        return $map;
    });

    $final = json_decode(file_get_contents($tmpFile), true);
    @unlink($tmpFile);
    echo json_encode($final);
    """
    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=str(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    out = json.loads(res.stdout.strip())
    assert out == {"alpha": 1, "beta": 2}


def test_native_php_unit_suite():
    """Executes the full native PHP unit test suite (tests/php/run_php_tests.php) and verifies zero failures."""
    res = subprocess.run(
        ["php", "tests/php/run_php_tests.php", "--json"],
        cwd=str(WORKSPACE_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(res.stdout.strip())
    assert payload["failed"] == 0, f"Native PHP unit tests failed: {payload}"
    assert payload["passed"] >= 16
    assert payload["assertions"] >= 35

