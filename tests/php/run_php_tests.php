<?php
declare(strict_types=1);

/**
 * Terra Physics Lab — Native PHP Unit Test Suite
 *
 * Zero-dependency native PHP 8 unit test runner exercising core backend
 * services (AuthService, LatexSanitizer, VariableAggregator, LabToolsLauncher,
 * PhysicsService, ShardSyncService, and PhysicsController).
 *
 * Usage:
 *   php tests/php/run_php_tests.php [--json]
 *   composer test
 */

define('PROJECT_ROOT', dirname(__DIR__, 2));
ini_set('memory_limit', '512M');
require_once PROJECT_ROOT . '/vendor/autoload.php';
require_once PROJECT_ROOT . '/app/logic/AuthService.php';
require_once PROJECT_ROOT . '/app/logic/LatexSanitizer.php';
require_once PROJECT_ROOT . '/app/logic/ShardSyncService.php';
require_once PROJECT_ROOT . '/app/logic/PhysicsService.php';
require_once PROJECT_ROOT . '/app/logic/VariableAggregator.php';
require_once PROJECT_ROOT . '/app/logic/LabToolsLauncher.php';
require_once PROJECT_ROOT . '/app/controllers/PhysicsController.php';
require_once PROJECT_ROOT . '/app/controllers/AdminController.php';
require_once PROJECT_ROOT . '/app/controllers/ReviewController.php';

class NativePhpTestRunner
{
    private array $results = [];
    private int $passed = 0;
    private int $failed = 0;
    private int $assertions = 0;

    public function assertTrue(bool $condition, string $message = 'Expected true, got false'): void
    {
        $this->assertions++;
        if (!$condition) {
            throw new RuntimeException($message);
        }
    }

    public function assertFalse(bool $condition, string $message = 'Expected false, got true'): void
    {
        $this->assertions++;
        if ($condition) {
            throw new RuntimeException($message);
        }
    }

    public function assertSame(mixed $expected, mixed $actual, string $message = ''): void
    {
        $this->assertions++;
        if ($expected !== $actual) {
            $expStr = var_export($expected, true);
            $actStr = var_export($actual, true);
            $prefix = $message !== '' ? "{$message}: " : '';
            throw new RuntimeException("{$prefix}Expected {$expStr}, got {$actStr}");
        }
    }

    public function assertContains(string $needle, string $haystack, string $message = ''): void
    {
        $this->assertions++;
        if (!str_contains($haystack, $needle)) {
            $prefix = $message !== '' ? "{$message}: " : '';
            throw new RuntimeException("{$prefix}Expected '{$haystack}' to contain '{$needle}'");
        }
    }

    public function run(string $suite, string $name, callable $fn): void
    {
        $t0 = hrtime(true);
        try {
            $fn($this);
            $ms = round((hrtime(true) - $t0) / 1e6, 2);
            $this->passed++;
            $this->results[] = [
                'suite' => $suite,
                'name' => $name,
                'status' => 'PASSED',
                'duration_ms' => $ms,
            ];
        } catch (Throwable $e) {
            $ms = round((hrtime(true) - $t0) / 1e6, 2);
            $this->failed++;
            $this->results[] = [
                'suite' => $suite,
                'name' => $name,
                'status' => 'FAILED',
                'duration_ms' => $ms,
                'error' => $e->getMessage(),
                'line' => $e->getLine(),
            ];
        }
    }

    public function summary(bool $jsonMode = false): int
    {
        $total = $this->passed + $this->failed;
        if ($jsonMode) {
            echo json_encode([
                'total' => $total,
                'passed' => $this->passed,
                'failed' => $this->failed,
                'assertions' => $this->assertions,
                'tests' => $this->results,
            ], JSON_UNESCAPED_SLASHES);
            return $this->failed === 0 ? 0 : 1;
        }

        echo "============================================================================\n";
        echo "🐘 TERRA PHYSICS LAB — NATIVE PHP UNIT TEST SUITE\n";
        echo "============================================================================\n";
        foreach ($this->results as $r) {
            $badge = $r['status'] === 'PASSED' ? '✓ PASS' : '✗ FAIL';
            printf("  %s  %-24s :: %-40s (%5.2f ms)\n", $badge, $r['suite'], $r['name'], $r['duration_ms']);
            if ($r['status'] === 'FAILED') {
                echo "          ↳ Error (line {$r['line']}): {$r['error']}\n";
            }
        }
        echo "----------------------------------------------------------------------------\n";
        printf(
            "Summary: %d / %d tests passed (%d assertions, %d failed)\n",
            $this->passed,
            $total,
            $this->assertions,
            $this->failed
        );
        echo "============================================================================\n";

        return $this->failed === 0 ? 0 : 1;
    }
}

/**
 * Helper to execute an AuthService test with isolated $_SERVER / $_ENV / $_COOKIE state.
 */
function withIsolatedEnv(array $env, array $server, callable $callback): mixed
{
    $origServer = $_SERVER;
    $origEnv = $_ENV;
    $origCookie = $_COOKIE ?? [];
    $origAppEnv = getenv('APP_ENV');
    $origAdminKey = getenv('TERRA_ADMIN_KEY');

    try {
        putenv('APP_ENV');
        putenv('TERRA_ADMIN_KEY');
        unset($_ENV['APP_ENV'], $_ENV['TERRA_ADMIN_KEY']);
        unset($_SERVER['REMOTE_ADDR'], $_SERVER['HTTP_X_FORWARDED_FOR'], $_SERVER['HTTP_X_REAL_IP'], $_SERVER['HTTP_X_TERRA_ADMIN_KEY']);
        $_COOKIE = [];

        foreach ($env as $k => $v) {
            putenv("{$k}={$v}");
            $_ENV[$k] = $v;
        }
        foreach ($server as $k => $v) {
            $_SERVER[$k] = $v;
        }
        return $callback();
    } finally {
        $_SERVER = $origServer;
        $_ENV = $origEnv;
        $_COOKIE = $origCookie;
        if ($origAppEnv === false) {
            putenv('APP_ENV');
        } else {
            putenv("APP_ENV={$origAppEnv}");
        }
        if ($origAdminKey === false) {
            putenv('TERRA_ADMIN_KEY');
        } else {
            putenv("TERRA_ADMIN_KEY={$origAdminKey}");
        }
    }
}

$runner = new NativePhpTestRunner();

// ============================================================================
// 1. AuthService Suite
// ============================================================================
$runner->run('AuthServiceTest', 'testLocalLoopbackGrantsStudioAdmin', function (NativePhpTestRunner $t) {
    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $auth = new \app\logic\AuthService();
        $user = $auth->getCurrentUser();
        $t->assertTrue($auth->isLocalDevStudio());
        $t->assertSame('admin', $user->role);
        $t->assertTrue($auth->hasRole('guest', $user));
        $t->assertTrue($auth->hasRole('contributor', $user));
        $t->assertTrue($auth->hasRole('curator', $user));
        $t->assertTrue($auth->hasRole('admin', $user));
    });
});

$runner->run('AuthServiceTest', 'testExternalPublicIpResolvesToGuest', function (NativePhpTestRunner $t) {
    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '203.0.113.55'], function () use ($t) {
        $auth = new \app\logic\AuthService();
        $user = $auth->getCurrentUser();
        $t->assertFalse($auth->isLocalDevStudio());
        $t->assertSame('guest', $user->role);
        $t->assertTrue($auth->hasRole('guest', $user));
        $t->assertFalse($auth->hasRole('contributor', $user));
        $t->assertFalse($auth->hasRole('curator', $user));
        $t->assertFalse($auth->hasRole('admin', $user));
        $t->assertFalse($auth->switchDevRole('admin'));
    });
});

$runner->run('AuthServiceTest', 'testForwardedReverseProxyBlocksExternalVisitor', function (NativePhpTestRunner $t) {
    withIsolatedEnv(
        ['APP_ENV' => 'development'],
        ['REMOTE_ADDR' => '127.0.0.1', 'HTTP_X_FORWARDED_FOR' => '198.51.100.42, 127.0.0.1'],
        function () use ($t) {
            $auth = new \app\logic\AuthService();
            $t->assertFalse($auth->isLocalDevStudio());
            $t->assertSame('guest', $auth->getCurrentUser()->role);
            $t->assertFalse($auth->hasRole('curator'));
        }
    );
});

$runner->run('AuthServiceTest', 'testProductionEnvRequiresExplicitAdminKey', function (NativePhpTestRunner $t) {
    withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $auth = new \app\logic\AuthService();
        $t->assertFalse($auth->isLocalDevStudio());
        $t->assertSame('guest', $auth->getCurrentUser()->role);
    });

    withIsolatedEnv(
        ['APP_ENV' => 'production', 'TERRA_ADMIN_KEY' => 'prod-secret-999'],
        ['REMOTE_ADDR' => '203.0.113.99', 'HTTP_X_TERRA_ADMIN_KEY' => 'prod-secret-999'],
        function () use ($t) {
            $auth = new \app\logic\AuthService();
            $t->assertTrue($auth->isLocalDevStudio());
            $t->assertSame('admin', $auth->getCurrentUser()->role);
            $t->assertTrue($auth->hasRole('admin'));
        }
    );
});

// ============================================================================
// 2. LatexSanitizer Suite
// ============================================================================
$runner->run('LatexSanitizerTest', 'testSanitizeEquationHtmlTags', function (NativePhpTestRunner $t) {
    $s = new \app\logic\LatexSanitizer();
    $cleaned = $s->sanitizeEquation('  <strong>F</strong> = m <em>a</em> <script>alert(1)</script> ');
    $t->assertSame('\\mathbf{F} = m \\mathit{a} alert(1)', $cleaned);
});

$runner->run('LatexSanitizerTest', 'testSanitizeProseFieldsDelimitersAndControlChars', function (NativePhpTestRunner $t) {
    $s = new \app\logic\LatexSanitizer();
    $dirty = [
        'interpretation' => "The formula \$F = ma\$ is interpreted as follows: the field \\( E \\) and \x0crac{1}{2} with \x08eta and \\\$x\\\$ works.",
        'conceptual_definition' => "Double slash \\\\frac{a}{b} with **bold markdown** is normalized.",
        'limits_and_boundary' => "Valid in two regimes:\n* **Low speed**: \$v \\ll c\$\n* **Constant mass**: \$dm/dt = 0\$",
    ];
    $clean = $s->sanitizeProseFields($dirty);
    $t->assertFalse(stripos($clean['interpretation'], 'interpreted as follows') !== false, 'Boilerplate lead should be stripped');
    $t->assertContains('$ E $', $clean['interpretation']);
    $t->assertContains('\\frac{1}{2}', $clean['interpretation']);
    $t->assertContains('\\beta', $clean['interpretation']);
    $t->assertContains('$x$', $clean['interpretation']);
    $t->assertContains('\\frac{a}{b}', $clean['conceptual_definition']);
    $t->assertFalse(str_contains($clean['conceptual_definition'], '**'), 'Markdown bold should be stripped');
    $t->assertFalse(str_contains($clean['limits_and_boundary'], "\n*"), 'Markdown bullets should be flattened into prose');
});

$runner->run('LatexSanitizerTest', 'testCanonicalizeAndCommutativeNormalizeLatex', function (NativePhpTestRunner $t) {
    $s = new \app\logic\LatexSanitizer();
    $sig1 = $s->normalizeLatex('\\mathbf{F} = m \\mathbf{a}');
    $sig2 = $s->normalizeLatex('F = a m');
    $t->assertSame($sig1, $sig2, 'Commutative multiplication should normalize to identical signature');

    $canon1 = $s->canonicalizeLatex('\\left( \\frac{1}{2} m v^2 \\right)');
    $canon2 = $s->canonicalizeLatex('( (1)/(2) m v^2 )');
    $t->assertSame($canon1, $canon2, 'Fractions and \\left/\\right should canonicalize identically');
});

$runner->run('LatexSanitizerTest', 'testSynthesizeFormulaExplanation', function (NativePhpTestRunner $t) {
    $s = new \app\logic\LatexSanitizer();
    $synth = $s->synthesizeFormulaExplanation('\\mathbf{F} = m \\mathbf{a}');
    $t->assertContains("Newton's Second Law", $synth['title'] ?? '');
    $t->assertSame('synthesized-ast', $synth['status'] ?? '');
    $t->assertTrue(!empty($synth['conceptual_definition']));
});

// ============================================================================
// 3. VariableAggregator Suite
// ============================================================================
$runner->run('VariableAggregatorTest', 'testCleanSymbolExtractsBaseIdentifier', function (NativePhpTestRunner $t) {
    $t->assertSame('F', \App\Logic\VariableAggregator::cleanSymbol('$\\mathbf{F}_{net}$'));
    $t->assertSame('psi', \App\Logic\VariableAggregator::cleanSymbol('\\psi_0'));
    $t->assertSame('E', \App\Logic\VariableAggregator::cleanSymbol('\\vec{E}'));
});

$runner->run('VariableAggregatorTest', 'testBuildSubtopicVariablesDeduplicatesEquations', function (NativePhpTestRunner $t) {
    $sampleSubtopic = [
        'title' => 'Relativistic Dynamics',
        'formulas' => [
            'f1' => [
                'title' => 'Mass-Energy Equivalence',
                'equation' => 'E = m c^2',
                'semantic_variables' => [
                    'E' => ['name' => 'Total Energy', 'unit' => 'J', 'description' => 'Relativistic energy'],
                    'm' => ['name' => 'Rest Mass', 'unit' => 'kg', 'description' => 'Invariant mass'],
                ],
            ],
            'f2' => [
                'title' => 'Mass-Energy Equivalence',
                'equation' => 'E = m c^2',
                'semantic_variables' => [
                    'E' => ['name' => 'Total Energy', 'unit' => 'J', 'description' => 'Duplicate formula entry'],
                ],
            ],
        ],
    ];
    $vars = \App\Logic\VariableAggregator::buildSubtopicVariables($sampleSubtopic);
    $t->assertTrue(count($vars) >= 2);
    foreach ($vars as $v) {
        if (($v['display_symbol'] ?? '') === 'E') {
            $t->assertSame(1, count($v['equations'] ?? []), 'Duplicate equations must be deduplicated');
        }
    }
});

// ============================================================================
// 4. LabToolsLauncher Suite
// ============================================================================
$runner->run('LabToolsLauncherTest', 'testResolveSpecificDomainAndDefaultMappings', function (NativePhpTestRunner $t) {
    // 1. Direct match
    $kepler = \App\Logic\LabToolsLauncher::resolve('keplers-second-law', 'astrophysics');
    $t->assertContains('preset=kepler', $kepler['url']);

    // 2. Domain fallback
    $quantum = \App\Logic\LabToolsLauncher::resolve('unmapped-custom-quantum-node', 'quantum-physics');
    $t->assertSame('quantum', $quantum['theme']);

    // 3. Default cockpit fallback
    $default = \App\Logic\LabToolsLauncher::resolve('completely-unknown-slug-xyz', 'unknown-domain');
    $t->assertSame('/physics/lab-tools', $default['url']);
    $t->assertSame('default', $default['theme']);
});

// ============================================================================
// 5. PhysicsService Suite
// ============================================================================
$runner->run('PhysicsServiceTest', 'testLoadAllShardsUsesStrictAllowlist', function (NativePhpTestRunner $t) {
    $app = new \flight\Engine();
    $svc = new \app\logic\PhysicsService($app);
    $svc->loadAllShards();
    $content = $svc->getPhysicsContent();

    $t->assertSame(1584, count($content['subtopics']), 'Must load exactly 1,584 canonical subtopics');
    $t->assertFalse(isset($content['subtopics']['topics']), 'Auxiliary JSON files must not leak into subtopics');
});

$runner->run('PhysicsServiceTest', 'testGetRelatedTopicsAndPreviewMode', function (NativePhpTestRunner $t) {
    $app = new \flight\Engine();
    $svc = new \app\logic\PhysicsService($app);

    $svc->setPreviewMode(true);
    $t->assertTrue($svc->isPreviewActive());
    $svc->setPreviewMode(false);
    $t->assertFalse($svc->isPreviewActive());

    $related = $svc->getRelatedTopics('special-relativity', 3);
    $t->assertSame(3, count($related));
    $t->assertTrue(!empty($related[0]['slug']));
});

$runner->run('PhysicsServiceTest', 'testAtomicJsonFileLocking', function (NativePhpTestRunner $t) {
    $app = new \flight\Engine();
    $svc = new \app\logic\PhysicsService($app);
    $ref = new ReflectionMethod($svc, 'updateJsonFileLocked');

    $tmpFile = sys_get_temp_dir() . '/terra_php_unit_lock_' . uniqid() . '.json';
    try {
        $ref->invoke($svc, $tmpFile, fn(array $m) => array_merge($m, ['k1' => 'v1']));
        $ref->invoke($svc, $tmpFile, fn(array $m) => array_merge($m, ['k2' => 'v2']));
        $decoded = json_decode((string)file_get_contents($tmpFile), true);
        $t->assertSame(['k1' => 'v1', 'k2' => 'v2'], $decoded);
    } finally {
        if (file_exists($tmpFile)) {
            @unlink($tmpFile);
        }
    }
});

// ============================================================================
// 6. ShardSyncService Suite
// ============================================================================
$runner->run('ShardSyncServiceTest', 'testSyncFormulasUsesTransactionalUpsert', function (NativePhpTestRunner $t) {
    $src = (string)file_get_contents(PROJECT_ROOT . '/app/logic/ShardSyncService.php');
    $t->assertContains('INSERT INTO formulas', $src);
    $t->assertContains('ON DUPLICATE KEY UPDATE', $src);
    $t->assertContains('$db->beginTransaction()', $src);
    $t->assertContains('$db->commit()', $src);

    // When force=false and all 256 hashes match registry, 0 shards should require DB writes
    $app = new \flight\Engine();
    $app->register('db', stdClass::class);
    $svc = new \app\logic\PhysicsService($app);
    $res = $svc->syncFormulasToDatabase(false);
    $t->assertSame(256, $res['shards_checked'], 'Should inspect all 256 shards');
    $t->assertSame(0, $res['shards_changed'], 'Up-to-date hash registry should skip unmodified shards');
});

// ============================================================================
// 7. PhysicsController & Rate Limiter Suite
// ============================================================================
$runner->run('PhysicsControllerTest', 'testSlidingWindowCasRateLimiterAndControllerDelegation', function (NativePhpTestRunner $t) {
    $app = new \flight\Engine();
    $app->register('adminController', \app\controllers\AdminController::class, [$app]);
    $app->register('reviewController', \app\controllers\ReviewController::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $ip = '198.51.100.88_' . uniqid();
    $bucket = sys_get_temp_dir() . '/terra_cas_ratelimit/' . hash('sha256', $ip) . '.json';
    try {
        $t->assertTrue($ctrl->consumeCasRateLimit($ip, 2, 60));
        $t->assertTrue($ctrl->consumeCasRateLimit($ip, 2, 60));
        $t->assertFalse($ctrl->consumeCasRateLimit($ip, 2, 60), 'Third call within window must be rate-limited');
    } finally {
        if (file_exists($bucket)) {
            @unlink($bucket);
        }
    }

    // Verify 3-pillar layout markup & environment-gated Dev Studio Admin button
    $layoutSrc = (string)file_get_contents(PROJECT_ROOT . '/app/views/physics/layout.php');
    $t->assertContains('dropdown-mega-topics', $layoutSrc);
    $t->assertContains('dropdown-mega-sims', $layoutSrc);
    $t->assertContains('dropdown-mega-lab', $layoutSrc);
    $t->assertContains('<!-- DEV_STUDIO_NAV_SLOT -->', $layoutSrc);

    Flight::register('authService', \app\logic\AuthService::class);
    $ref = new ReflectionMethod($ctrl, 'injectLayoutDynamicTokens');

    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t, $ref, $ctrl) {
        $rendered = $ref->invoke($ctrl, '<nav><!-- DEV_STUDIO_NAV_SLOT --></nav>', 'abc123', false);
        $t->assertContains('dev-studio-admin-nav', $rendered, 'Local studio should inject Admin dropdown');
        $t->assertContains('/physics/admin/assess', $rendered);
    });

    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '203.0.113.55'], function () use ($t, $ref, $ctrl) {
        $rendered = $ref->invoke($ctrl, '<nav><!-- DEV_STUDIO_NAV_SLOT --></nav>', 'abc123', false);
        $t->assertFalse(str_contains($rendered, 'dev-studio-admin-nav'), 'External visitor must not see Admin dropdown');
    });
});

$jsonFlag = in_array('--json', $argv ?? [], true);
exit($runner->summary($jsonFlag));
