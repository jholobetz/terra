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
require_once PROJECT_ROOT . '/app/logic/SemanticSearchService.php';
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
        } finally {
            gc_collect_cycles();
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
    $origGet = $_GET ?? [];
    $origCookie = $_COOKIE ?? [];
    $trackedKeys = ['APP_ENV', 'TERRA_ADMIN_KEY', 'TRUSTED_PROXY_IPS', 'DISABLE_EXTERNAL_EMBEDDING_API'];
    $origPutenv = [];
    foreach ($trackedKeys as $tk) {
        $origPutenv[$tk] = getenv($tk);
    }

    try {
        foreach ($trackedKeys as $tk) {
            putenv($tk);
            unset($_ENV[$tk]);
        }
        unset(
            $_SERVER['REMOTE_ADDR'],
            $_SERVER['HTTP_X_FORWARDED_FOR'],
            $_SERVER['HTTP_X_REAL_IP'],
            $_SERVER['HTTP_X_TERRA_ADMIN_KEY'],
            $_SERVER['APP_ENV'],
            $_SERVER['REDIRECT_APP_ENV']
        );
        $_GET = [];
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
        $_GET = $origGet;
        $_COOKIE = $origCookie;
        foreach ($origPutenv as $tk => $val) {
            if ($val === false) {
                putenv($tk);
            } else {
                putenv("{$tk}={$val}");
            }
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

    $related = $svc->getRelatedTopics('special-relativity', 4);
    $t->assertSame(4, count($related));
    $t->assertTrue(!empty($related[0]['slug']));
    $t->assertTrue(!empty($related[0]['title']));
    $t->assertTrue(!empty($related[0]['domain']));
    $t->assertTrue(!empty($related[0]['url']));
    $t->assertTrue(!empty($related[0]['snippet']), 'Related topics must include real physical snippets');
    $t->assertFalse(
        str_contains($related[0]['snippet'], 'Explore theoretical mechanics, governing equations'),
        'Related topics must not use legacy hardcoded boilerplate snippets'
    );

    // Ensure deterministic cross-pillar bridge guarantee when limit >= 2
    $hasBridge = false;
    foreach ($related as $item) {
        if (!empty($item['is_bridge'])) {
            $hasBridge = true;
            break;
        }
    }
    $t->assertTrue($hasBridge, 'getRelatedTopics must include at least one cross-pillar bridge candidate');

    // Ensure subtopic.php contains zero CSP-violating inline onclick attributes
    $subtopicViewSrc = (string)file_get_contents(PROJECT_ROOT . '/app/views/physics/subtopic.php');
    $t->assertFalse(str_contains($subtopicViewSrc, 'onclick='), 'subtopic.php must not contain inline onclick handlers');

    // Ensure /physics/api/related-subtopics/@slug delegates to unified PhysicsService::getRelatedTopics
    $controllerSrc = (string)file_get_contents(PROJECT_ROOT . '/app/controllers/PhysicsController.php');
    $t->assertContains('$this->service()->getRelatedTopics($slug, 4)', $controllerSrc);
});

$runner->run('PhysicsServiceTest', 'testLazyNotationLoadingAndSlimSchema', function (NativePhpTestRunner $t) {
    $notationPath = PROJECT_ROOT . '/app/config/content/notation.json';
    $t->assertTrue(filesize($notationPath) < 512 * 1024, 'notation.json must remain slim (< 512 KB)');

    $app = new \flight\Engine();
    $svc = new \app\logic\PhysicsService($app);

    // 1. Eager getPhysicsContent() must NOT decode notation.json
    $contentBefore = $svc->getPhysicsContent();
    $t->assertSame(0, count($contentBefore['notation']), 'notation must not be eagerly loaded by getPhysicsContent()');

    // 2. On-demand getNotation() loads all 348 entries with clean descriptions and zero dead HTML bloat
    $notation = $svc->getNotation();
    $t->assertSame(348, count($notation), 'Must load all 348 notation entries');
    $t->assertTrue(isset($notation['h-bar']['value']), 'Fundamental constants must preserve CODATA values');
    foreach ($notation as $slug => $entry) {
        $t->assertFalse(isset($entry['content']), "Dead content field must not exist on {$slug}");
        $t->assertFalse(isset($entry['snippet_svg']), "Dead snippet_svg field must not exist on {$slug}");
        $t->assertTrue(!empty($entry['description']), "Description must be populated on {$slug}");
    }

    // 3. Hydrates physicsContent['notation'] and resets cleanly on clearCache()
    $t->assertSame(348, count($svc->getPhysicsContent()['notation']));
    $svc->clearCache();
    $t->assertSame(0, count($svc->getPhysicsContent()['notation']));
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
    $t->assertContains('INFORMATION_SCHEMA.COLUMNS', $src);
    foreach (['category', 'description', 'lineage_confidence', 'record_type', 'equation_family'] as $col) {
        $t->assertContains($col, $src, "ShardSyncService must sync enriched column {$col}");
    }
    $t->assertContains('$this->syncFormulasToDatabase($force)', $src, 'performSync must delegate formula sync to unified syncFormulasToDatabase');

    $svcSrc = (string)file_get_contents(PROJECT_ROOT . '/app/logic/PhysicsService.php');
    foreach (['category', 'description', 'lineage_confidence', 'record_type', 'equation_family'] as $col) {
        $t->assertContains("{$col} = ?", $svcSrc, "PhysicsService::saveFormula must update column {$col}");
    }

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

// ============================================================================
// 8. FormulaGraphService & Reverse-LaTeX Lookup Suite
// ============================================================================
$runner->run('FormulaGraphServiceTest', 'testSubgraphProvenanceAndReverseLatexParity', function (NativePhpTestRunner $t) {
    require_once PROJECT_ROOT . '/app/logic/FormulaGraphService.php';

    // 1. Newly added shard formulas resolve in the compiled derivation graph with provenance metadata
    foreach ([
        'cross-field-electric-magnetic-drift-velocity-magnitude',
        'eulerian-velocity-vector-field',
        'three-dimensional-euclidean-line-element-in-spherical-coordinates',
    ] as $newId) {
        $sub = \App\Logic\FormulaGraphService::getFormulaSubgraph($newId, 1);
        $t->assertTrue(($sub['stats']['total_nodes'] ?? 0) >= 2, "Subgraph for {$newId} must contain root + parent");
        $root = $sub['root_node'] ?? [];
        $t->assertSame($newId, $root['id'] ?? null);
        $t->assertTrue(!empty($root['lineage_confidence']), "Root node {$newId} must expose lineage_confidence");
        $t->assertTrue(!empty($root['record_type']), "Root node {$newId} must expose record_type");
        $t->assertTrue(is_bool($root['cas_verified'] ?? null), "Root node {$newId} must expose boolean cas_verified");
    }

    // 2. Derivation links carry edge confidence
    $driftSub = \App\Logic\FormulaGraphService::getFormulaSubgraph('cross-field-electric-magnetic-drift-velocity-magnitude', 1);
    $derivEdges = array_values(array_filter($driftSub['links'] ?? [], fn($l) => ($l['type'] ?? '') === 'derivation'));
    $t->assertTrue(count($derivEdges) >= 1, 'Expected at least 1 upstream derivation edge');
    $t->assertSame('cas_verified', $derivEdges[0]['confidence'] ?? null, 'Derivation edge must forward lineage_confidence');

    // 3. Reverse LaTeX lookup resolves hex-repaired equations cleanly in offline shard mode
    $app = new \flight\Engine();
    $app->register('db', stdClass::class);
    $svc = new \app\logic\PhysicsService($app);
    $prevPreview = $_GET['preview'] ?? null;
    $_GET['preview'] = '1';
    try {
        foreach ([
            '\\Psi(\\mathbf{r}, t)' => 'quantum-wave-function-symbol-a70d1c54',
            '\\frac{\\mathbf{p} \\cdot \\mathbf{r}}{\\hbar}' => 'plane-wave-phase-argument-03b4af97',
            '\\mathbf{p} \\cdot \\mathbf{r}' => 'momentum-position-dot-product-37631088',
        ] as $tex => $expectedId) {
            $found = $svc->searchFormulaByLatex($tex);
            $t->assertTrue(is_array($found), "Reverse LaTeX lookup must resolve {$tex}");
            $t->assertSame($expectedId, $found['id'] ?? null);
        }

        // 4. Hierarchy hydration forwards lineage_confidence & record_type on parent and downstream children
        $hier = $svc->getFormulaWithHierarchy('cross-field-electric-magnetic-drift-velocity-magnitude');
        $t->assertTrue(!empty($hier['description']), 'Hydrated formula must expose description');
        $t->assertSame('cas_verified', $hier['lineage_confidence'] ?? null);
        $t->assertTrue(!empty($hier['parent_formula']['lineage_confidence']), 'Parent formula must expose lineage_confidence');
        $parentHier = $svc->getFormulaWithHierarchy('lorentz-force-law');
        $t->assertTrue(!empty($parentHier['subcomponents']), 'Lorentz force law must hydrate subcomponents');
        $t->assertTrue(!empty($parentHier['subcomponents'][0]['lineage_confidence']), 'Hydrated child subcomponent must expose lineage_confidence');
    } finally {
        if ($prevPreview === null) {
            unset($_GET['preview']);
        } else {
            $_GET['preview'] = $prevPreview;
        }
    }
});

// ============================================================================
// 9. Stage 1 Production Hardening Suite
// ============================================================================
$runner->run('ProductionHardeningTest', 'testPreviewModeBlockedForPublicAndProductionVisitors', function (NativePhpTestRunner $t) {
    // 1. Production environment ignores ?preview=1, ?build_mode=1, and physics_preview cookie
    withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $_GET['preview'] = '1';
        $_GET['build_mode'] = '1';
        $_COOKIE['physics_preview'] = '1';
        $app = new \flight\Engine();
        $svc = new \app\logic\PhysicsService($app);
        $t->assertFalse($svc->isPreviewActive(), 'Production visitors must never activate shard preview mode');

        // Explicit CLI override via setPreviewMode(true) remains functional for cli_sync.php
        $svc->setPreviewMode(true);
        $t->assertTrue($svc->isPreviewActive(), 'Explicit CLI setPreviewMode(true) must still work');
    });

    // 2. External public IP in development also cannot trigger ?preview=1
    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '203.0.113.55'], function () use ($t) {
        $_GET['preview'] = '1';
        $_COOKIE['physics_preview'] = '1';
        $app = new \flight\Engine();
        $svc = new \app\logic\PhysicsService($app);
        $t->assertFalse($svc->isPreviewActive(), 'External IPs must not bypass cache via ?preview=1');
    });

    // 3. Local loopback studio retains ?preview=1
    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $_GET['preview'] = '1';
        $app = new \flight\Engine();
        $svc = new \app\logic\PhysicsService($app);
        $t->assertTrue($svc->isPreviewActive(), 'Local studio must retain ?preview=1 workflow');
    });
});

$runner->run('ProductionHardeningTest', 'testClientIpSpoofingResistanceAndScopedRateLimiter', function (NativePhpTestRunner $t) {
    // 1. Direct external caller cannot spoof X-Forwarded-For or X-Real-IP
    withIsolatedEnv(
        ['APP_ENV' => 'production'],
        [
            'REMOTE_ADDR' => '203.0.113.88',
            'HTTP_X_FORWARDED_FOR' => '1.2.3.4',
            'HTTP_X_REAL_IP' => '5.6.7.8',
        ],
        function () use ($t) {
            $auth = new \app\logic\AuthService();
            $t->assertSame('203.0.113.88', $auth->resolveClientIp(), 'Untrusted REMOTE_ADDR must ignore forged proxy headers');
        }
    );

    // 2. Behind trusted loopback proxy, right-to-left hop parsing ignores attacker-prepended X-Forwarded-For entry
    withIsolatedEnv(
        ['APP_ENV' => 'production'],
        [
            'REMOTE_ADDR' => '127.0.0.1',
            'HTTP_X_FORWARDED_FOR' => '9.9.9.9, 198.51.100.77',
        ],
        function () use ($t) {
            $auth = new \app\logic\AuthService();
            $t->assertSame('198.51.100.77', $auth->resolveClientIp(), 'Right-to-left hop extraction must defeat prepended spoofed IPs');
        }
    );

    // 3. Scoped rate limiter isolates semantic_search from cas buckets
    $app = new \flight\Engine();
    $ctrl = new \app\controllers\PhysicsController($app);
    $ip = '198.51.100.200_' . uniqid();
    $casBucket = sys_get_temp_dir() . '/terra_cas_ratelimit/' . hash('sha256', $ip) . '.json';
    $semBucket = sys_get_temp_dir() . '/terra_cas_ratelimit/' . hash('sha256', 'semantic_search|' . $ip) . '.json';
    try {
        $t->assertTrue($ctrl->consumeCasRateLimit($ip, 1, 60, 'cas'));
        $t->assertFalse($ctrl->consumeCasRateLimit($ip, 1, 60, 'cas'));
        $t->assertTrue($ctrl->consumeCasRateLimit($ip, 1, 60, 'semantic_search'), 'semantic_search bucket must be independent from cas');
        $t->assertFalse($ctrl->consumeCasRateLimit($ip, 1, 60, 'semantic_search'));
    } finally {
        @unlink($casBucket);
        @unlink($semBucket);
    }
});

$runner->run('ProductionHardeningTest', 'testErrorSanitizationCostFirewallAndNoDevGuards', function (NativePhpTestRunner $t) {
    $app = new \flight\Engine();
    $ctrl = new \app\controllers\PhysicsController($app);
    $refErr = new ReflectionMethod($ctrl, 'publicErrorMessage');

    // 1. Development returns detailed exception text; production returns sanitized fallback
    withIsolatedEnv(['APP_ENV' => 'development'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t, $ctrl, $refErr) {
        $msg = $refErr->invoke($ctrl, new RuntimeException('SQLSTATE[HY000] secret host details'), 'Safe error.');
        $t->assertContains('SQLSTATE', $msg);
    });
    withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '203.0.113.10'], function () use ($t, $ctrl, $refErr) {
        $prevErrLog = ini_set('error_log', '/dev/null');
        try {
            $msg = $refErr->invoke($ctrl, new RuntimeException('SQLSTATE[HY000] secret host details'), 'Safe error.');
            $t->assertSame('Safe error.', $msg);
        } finally {
            if ($prevErrLog !== false) {
                ini_set('error_log', $prevErrLog);
            }
        }
    });

    // 2. SemanticSearchService defaults external API disabled in production unless explicitly overridden
    withIsolatedEnv(['APP_ENV' => 'production'], [], function () use ($t) {
        $sem = new \app\logic\SemanticSearchService();
        $t->assertTrue($sem->isExternalApiDisabled(), 'Production must default live external embedding API to disabled');
    });
    withIsolatedEnv(['APP_ENV' => 'production', 'DISABLE_EXTERNAL_EMBEDDING_API' => '0'], [], function () use ($t) {
        $sem = new \app\logic\SemanticSearchService();
        $t->assertFalse($sem->isExternalApiDisabled(), 'Explicit DISABLE_EXTERNAL_EMBEDDING_API=0 must allow opt-in');
    });

    // 3. Verify services.php --no-dev guards, Tracy Bar content_length guard, migration guard, and stale stub removal
    $servicesSrc = (string)file_get_contents(PROJECT_ROOT . '/app/config/services.php');
    $t->assertContains('Debugger::Production', $servicesSrc);
    $t->assertContains("set('flight.content_length', false)", $servicesSrc);
    $t->assertContains('class_exists(TracyExtensionLoader::class)', $servicesSrc);
    $t->assertContains('class_exists(PdoQueryCapture::class)', $servicesSrc);

    $migSrc = (string)file_get_contents(PROJECT_ROOT . '/scripts/migrations/001_create_rbac_and_review_tables.php');
    $t->assertContains("appEnv === 'production'", $migSrc);
    $t->assertFalse(file_exists(PROJECT_ROOT . '/app/config/PhysicsService.php'), 'Empty app/config/PhysicsService.php stub must remain deleted');
});

// ============================================================================
// 10. Stage 2 Debian Packaging, Readiness Probe & Cache Warmer Suite
// ============================================================================
$runner->run('Stage2PackagingTest', 'testDebianAppEnvResolutionAcrossServerRedirectAndConfig', function (NativePhpTestRunner $t) {
    // 1. Debian variables_order="GPCS": getenv() & $_ENV empty, Apache SetEnv populates $_SERVER['APP_ENV']
    withIsolatedEnv([], ['APP_ENV' => 'Production', 'REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $t->assertSame('production', \app\logic\AuthService::resolveAppEnv());
        $auth = new \app\logic\AuthService();
        $t->assertTrue($auth->isProduction());
        $t->assertFalse($auth->isLocalDevStudio(), 'Production via $_SERVER[APP_ENV] must disable studio auto-admin');
    });

    // 2. Apache mod_rewrite internal redirect prefixes SetEnv vars as REDIRECT_APP_ENV
    withIsolatedEnv([], ['REDIRECT_APP_ENV' => 'production', 'REMOTE_ADDR' => '127.0.0.1'], function () use ($t) {
        $t->assertSame('production', \app\logic\AuthService::resolveAppEnv());
        $sem = new \app\logic\SemanticSearchService();
        $t->assertTrue($sem->isExternalApiDisabled(), 'SemanticSearchService must honor REDIRECT_APP_ENV=production');
    });

    // 3. PHP-FPM clear_env=yes fallback to config.php ('app_env')
    withIsolatedEnv([], [], function () use ($t) {
        $t->assertSame('production', \app\logic\AuthService::resolveAppEnv('production'));
        $t->assertSame('development', \app\logic\AuthService::resolveAppEnv());
    });

    // 4. OS getenv('APP_ENV') takes precedence over config fallback
    withIsolatedEnv(['APP_ENV' => 'staging'], [], function () use ($t) {
        $t->assertSame('staging', \app\logic\AuthService::resolveAppEnv('production'));
    });
});

$runner->run('Stage2PackagingTest', 'testZeroLeakHealthzReadinessProbe', function (NativePhpTestRunner $t) {
    // 1. Degraded state when database service is unreachable/unconfigured
    $appBad = new \flight\Engine();
    $appBad->register('db', stdClass::class);
    $ctrlBad = new \app\controllers\PhysicsController($appBad);
    $badReport = $ctrlBad->evaluateHealthChecks();
    $t->assertSame('degraded', $badReport['status']);
    $t->assertSame(503, $badReport['http_code']);
    $t->assertFalse($badReport['checks']['database']);
    $t->assertTrue($badReport['checks']['storage']);
    $t->assertTrue($badReport['checks']['cas_runtime']);

    // 2. Healthy state when database responds to SELECT 1
    $healthyDb = new class {
        public function runQuery(string $sql): object
        {
            return (object)['sql' => $sql];
        }
    };
    $appOk = new \flight\Engine();
    $appOk->set('db_mock', $healthyDb);
    $appOk->map('db', fn() => $healthyDb);
    $ctrlOk = new \app\controllers\PhysicsController($appOk);
    $okReport = $ctrlOk->evaluateHealthChecks();
    $t->assertSame('ok', $okReport['status']);
    $t->assertSame(200, $okReport['http_code']);
    $t->assertTrue($okReport['checks']['database']);

    ob_start();
    try {
        $ctrlOk->healthz();
        $rawJson = (string)ob_get_clean();
    } catch (Throwable $e) {
        ob_end_clean();
        throw $e;
    }
    $decoded = json_decode($rawJson, true);
    $t->assertSame('ok', $decoded['status'] ?? null);
    $t->assertSame(['database' => true, 'storage' => true, 'cas_runtime' => true], $decoded['checks'] ?? null);
    $t->assertFalse(str_contains($rawJson, PROJECT_ROOT), 'healthz JSON must never leak filesystem paths');
});

$runner->run('Stage2PackagingTest', 'testInProcessWarmHtmlCacheAndPythonManifests', function (NativePhpTestRunner $t) {
    // 1. Verify minimal Debian PEP 668 requirements.txt vs requirements-dev.txt
    $reqProd = (string)file_get_contents(PROJECT_ROOT . '/requirements.txt');
    $reqDev = (string)file_get_contents(PROJECT_ROOT . '/requirements-dev.txt');
    $t->assertContains('sympy==', $reqProd);
    $t->assertContains('mpmath==', $reqProd);
    $t->assertFalse(str_contains($reqProd, 'google-genai'), 'Production requirements.txt must omit external AI SDKs');
    $t->assertFalse(str_contains($reqProd, 'pytest'), 'Production requirements.txt must omit dev test runners');
    $t->assertContains('-r requirements.txt', $reqDev);
    $t->assertContains('pytest==', $reqDev);

    $cliSyncSrc = (string)file_get_contents(PROJECT_ROOT . '/cli_sync.php');
    $t->assertContains('--warm-cache', $cliSyncSrc);
    $t->assertContains('--force-cache', $cliSyncSrc);
    $t->assertContains('--cache-only', $cliSyncSrc);

    // 2. Verify in-process warmHtmlCache builds fresh HTML with 32-hex nonce + DEV_STUDIO_NAV_SLOT, then skips on incremental run
    Flight::register('authService', \app\logic\AuthService::class);
    $app = new \flight\Engine();
    $app->set('flight.views.path', PROJECT_ROOT . '/app/views');
    $app->register('db', stdClass::class);
    $app->register('authService', \app\logic\AuthService::class);
    $app->register('physicsService', \app\logic\PhysicsService::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $hubCache = PROJECT_ROOT . '/public/cache/topic/classical-mechanics.html';
    $subCache = PROJECT_ROOT . '/public/cache/subtopic/generalized-coordinates.html';
    $hadHub = file_exists($hubCache) ? file_get_contents($hubCache) : null;
    $hadSub = file_exists($subCache) ? file_get_contents($subCache) : null;
    $prevErrLog = ini_set('error_log', '/dev/null');

    try {
        withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t, $ctrl, $hubCache, $subCache) {
            $first = $ctrl->warmHtmlCache(true, ['classical-mechanics', 'generalized-coordinates']);
            $t->assertSame([], $first['errors'], 'warmHtmlCache must complete with 0 errors');
            $t->assertSame(1, $first['hubs_built']);
            $t->assertSame(1, $first['subtopics_built']);

            $hubHtml = (string)file_get_contents($hubCache);
            $subHtml = (string)file_get_contents($subCache);
            $t->assertTrue((bool)preg_match('/nonce="[a-f0-9]{32}"/', $hubHtml), 'Cached hub HTML must preserve 32-hex CSP nonce placeholder');
            $t->assertTrue((bool)preg_match('/nonce="[a-f0-9]{32}"/', $subHtml), 'Cached subtopic HTML must preserve 32-hex CSP nonce placeholder');
            $t->assertContains('<!-- DEV_STUDIO_NAV_SLOT -->', $subHtml, 'Cached HTML must preserve dynamic studio nav slot');
            $t->assertContains('nav-pillar-active', $subHtml, 'Cached subtopic HTML must mark Topics nav pillar active');
            $t->assertFalse(str_contains($subHtml, 'preview-banner'), 'Cached HTML must never bake preview-mode banner');

            $second = $ctrl->warmHtmlCache(false, ['classical-mechanics', 'generalized-coordinates']);
            $t->assertSame(0, $second['hubs_built']);
            $t->assertSame(1, $second['hubs_skipped'], 'Fresh hub cache must be skipped on incremental warm');
            $t->assertSame(0, $second['subtopics_built']);
            $t->assertSame(1, $second['subtopics_skipped'], 'Fresh subtopic cache must be skipped on incremental warm');
        });
    } finally {
        if ($prevErrLog !== false) {
            ini_set('error_log', $prevErrLog);
        }
        if ($hadHub === null) {
            @unlink($hubCache);
        } else {
            file_put_contents($hubCache, $hadHub, LOCK_EX);
        }
        if ($hadSub === null) {
            @unlink($subCache);
        } else {
            file_put_contents($subCache, $hadSub, LOCK_EX);
        }
    }
});

// ============================================================================
// 11. Stage 3 Error Views, SEO Metadata, Favicon, robots.txt & sitemap.xml Suite
// ============================================================================
$runner->run('Stage3WebPolishTest', 'testBranded404And500HtmlAndJsonResponses', function (NativePhpTestRunner $t) {
    Flight::register('authService', \app\logic\AuthService::class);
    $app = new \flight\Engine();
    $app->set('flight.views.path', PROJECT_ROOT . '/app/views');
    $app->register('db', stdClass::class);
    $app->register('authService', \app\logic\AuthService::class);
    $app->register('physicsService', \app\logic\PhysicsService::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $prevErrLog = ini_set('error_log', '/dev/null');
    try {
        withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '203.0.113.20'], function () use ($t, $app, $ctrl) {
            // 1. Browser HTML 404 response
            $app->request()->url = '/physics/subtopic/does-not-exist-anywhere';
            $ctrl->renderNotFound();
            $t->assertSame(404, $app->response()->status());
            $html404 = $app->response()->getBody();
            $t->assertContains('Page Not Found', $html404);
            $t->assertContains('noindex, nofollow', $html404);
            $t->assertFalse(str_contains($html404, 'rel="canonical"'), '404 pages must omit canonical link');
            $t->assertTrue(!empty($app->response()->getHeader('Content-Security-Policy')), '404 must emit CSP header');

            // 2. API JSON 404 response
            $app->request()->url = '/physics/api/nonexistent-endpoint';
            $ctrl->renderNotFound();
            $t->assertSame(404, $app->response()->status());
            $json404 = json_decode($app->response()->getBody(), true);
            $t->assertSame(404, $json404['status'] ?? null);
            $t->assertSame('Endpoint not found.', $json404['error'] ?? null);

            // 3. Browser HTML 500 response (zero internal message/trace leakage in production)
            $app->request()->url = '/physics/lab-tools';
            $ctrl->renderServerError(new RuntimeException('PDO secret host 10.0.0.99 failure'), false);
            $t->assertSame(500, $app->response()->status());
            $html500 = $app->response()->getBody();
            $t->assertContains('Unexpected Server Error', $html500);
            $t->assertContains('noindex, nofollow', $html500);
            $t->assertFalse(str_contains($html500, '10.0.0.99'), 'Production 500 HTML must never leak exception details');

            // 4. API JSON 500 response (sanitized in production)
            $app->request()->url = '/physics/api/explain';
            $ctrl->renderServerError(new RuntimeException('PDO secret host 10.0.0.99 failure'), false);
            $t->assertSame(500, $app->response()->status());
            $json500 = json_decode($app->response()->getBody(), true);
            $t->assertSame(500, $json500['status'] ?? null);
            $t->assertSame('Internal server error.', $json500['error'] ?? null);
        });
    } finally {
        if ($prevErrLog !== false) {
            ini_set('error_log', $prevErrLog);
        }
    }
});

$runner->run('Stage3WebPolishTest', 'testSeoMetadataCanonicalOpenGraphFaviconAndFooterHygiene', function (NativePhpTestRunner $t) {
    $t->assertTrue(is_file(PROJECT_ROOT . '/public/favicon.svg'), 'public/favicon.svg must exist');

    Flight::register('authService', \app\logic\AuthService::class);
    $app = new \flight\Engine();
    $app->set('flight.views.path', PROJECT_ROOT . '/app/views');
    $app->set('terra.app_url', 'https://physics.example.org');
    $app->register('db', stdClass::class);
    $app->register('authService', \app\logic\AuthService::class);
    $app->register('physicsService', \app\logic\PhysicsService::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $subCache = PROJECT_ROOT . '/public/cache/subtopic/generalized-coordinates.html';
    $hadSub = file_exists($subCache) ? file_get_contents($subCache) : null;
    $prevErrLog = ini_set('error_log', '/dev/null');

    try {
        // Test Host-header poisoning resistance in production
        withIsolatedEnv(
            ['APP_ENV' => 'production'],
            ['REMOTE_ADDR' => '203.0.113.50', 'HTTP_HOST' => 'evil-attacker.invalid'],
            function () use ($t, $ctrl, $subCache) {
                $t->assertSame('https://physics.example.org', $ctrl->resolveBaseUrl(), 'Production base URL must ignore forged Host header');

                $res = $ctrl->warmHtmlCache(true, ['generalized-coordinates']);
                $t->assertSame([], $res['errors']);
                $html = (string)file_get_contents($subCache);

                $t->assertContains('<meta name="description" content="Mapping the physical configurations of a system', $html);
                $t->assertContains('<link rel="canonical" href="https://physics.example.org/physics/subtopic/generalized-coordinates">', $html);
                $t->assertContains('<meta property="og:type" content="article">', $html);
                $t->assertContains('<meta property="og:url" content="https://physics.example.org/physics/subtopic/generalized-coordinates">', $html);
                $t->assertContains('<link rel="icon" type="image/svg+xml" href="/favicon.svg">', $html);
                $t->assertFalse(str_contains($html, 'onmouseover='), 'Public layout must contain zero inline JS event handlers');
                $t->assertFalse(str_contains($html, '/physics/admin/assess'), 'Cached public HTML must not expose admin console link');
            }
        );
    } finally {
        if ($prevErrLog !== false) {
            ini_set('error_log', $prevErrLog);
        }
        if ($hadSub === null) {
            @unlink($subCache);
        } else {
            file_put_contents($subCache, $hadSub, LOCK_EX);
        }
    }
});

$runner->run('Stage3WebPolishTest', 'testRobotsTxtAndSitemapXmlGeneration', function (NativePhpTestRunner $t) {
    Flight::register('authService', \app\logic\AuthService::class);
    $app = new \flight\Engine();
    $app->set('terra.app_url', 'https://physics.example.org');
    $app->register('db', stdClass::class);
    $app->register('authService', \app\logic\AuthService::class);
    $app->register('physicsService', \app\logic\PhysicsService::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $sitemapCache = PROJECT_ROOT . '/public/cache/sitemap.xml';
    $hadSitemap = file_exists($sitemapCache) ? file_get_contents($sitemapCache) : null;

    try {
        // 1. Verify /robots.txt directives and dynamic Sitemap URL
        $ctrl->robotsTxt();
        $t->assertSame(200, $app->response()->status());
        $robots = $app->response()->getBody();
        $t->assertContains('Disallow: /physics/admin/', $robots);
        $t->assertContains('Disallow: /physics/api/', $robots);
        $t->assertContains('Disallow: /healthz', $robots);
        $t->assertContains('Sitemap: https://physics.example.org/sitemap.xml', $robots);

        // 2. Verify /sitemap.xml structure, coverage, and canonical exclusions
        $app->response()->clearBody();
        $xml = $ctrl->buildSitemapXml(true);
        $t->assertContains('<?xml version="1.0" encoding="UTF-8"?>', $xml);
        $t->assertContains('<loc>https://physics.example.org/physics/topic/classical-mechanics</loc>', $xml);
        $t->assertContains('<loc>https://physics.example.org/physics/simulations/pendulum</loc>', $xml);
        $t->assertContains('<loc>https://physics.example.org/physics/subtopic/generalized-coordinates</loc>', $xml);
        $t->assertFalse(str_contains($xml, '/physics/subtopic/maxwell-equations<'), 'Redirect alias maxwell-equations must be excluded from sitemap');
        $t->assertFalse(str_contains($xml, '/physics/admin'), 'Admin routes must never appear in sitemap.xml');
        $t->assertTrue(substr_count($xml, '<url>') >= 1600, 'Sitemap must index all 1,580+ subtopics, 12 hubs, simulations, and workbenches');

        $parsed = simplexml_load_string($xml);
        $t->assertTrue($parsed !== false, 'Generated sitemap.xml must be well-formed XML');
    } finally {
        if ($hadSitemap === null) {
            @unlink($sitemapCache);
        } else {
            file_put_contents($sitemapCache, $hadSitemap, LOCK_EX);
        }
    }
});

// ============================================================================
// 12. Stage 4 Ongoing-Revision Cache, Migrations, .htaccess & Deploy Script Suite
// ============================================================================
$runner->run('Stage4DeploymentTest', 'testJsAssetCacheBustingAndFormulaShardCacheInvalidation', function (NativePhpTestRunner $t) {
    // 1. Verify every local <script src="/js/..."> tag across views carries ?v= cache-busting
    $viewsToAudit = [
        'layout.php',
        'home.php',
        'legendre_transformer.php',
        'anthropic_tuner.php',
        'correspondence_workspace.php',
        'noethers_vault.php',
        'notation_toggle.php',
        'lab_tools.php',
        'simulations.php',
        'simulation_page.php',
        'topic.php',
        'equation_explainer.php',
        'universe_graph.php',
    ];
    foreach ($viewsToAudit as $viewFile) {
        $src = (string)file_get_contents(PROJECT_ROOT . '/app/views/physics/' . $viewFile);
        if (preg_match_all('/<script\b[^>]*\bsrc="(\/js\/[^"]+)"/i', $src, $matches)) {
            foreach ($matches[1] as $scriptSrc) {
                $t->assertContains('?v=', $scriptSrc, "Script tag in {$viewFile} must carry ?v=filemtime cache-busting");
            }
        }
    }

    // 2. Verify modifying a referenced hex formula shard invalidates the subtopic HTML cache on incremental warm
    Flight::register('authService', \app\logic\AuthService::class);
    $app = new \flight\Engine();
    $app->set('flight.views.path', PROJECT_ROOT . '/app/views');
    $app->register('db', stdClass::class);
    $app->register('authService', \app\logic\AuthService::class);
    $app->register('physicsService', \app\logic\PhysicsService::class, [$app]);
    $ctrl = new \app\controllers\PhysicsController($app);

    $subCache = PROJECT_ROOT . '/public/cache/subtopic/generalized-coordinates.html';
    $hadSub = file_exists($subCache) ? file_get_contents($subCache) : null;

    // generalized-coordinates references 'degrees-of-freedom-9057cc89'
    $targetFormulaId = 'degrees-of-freedom-9057cc89';
    $hex = substr(md5($targetFormulaId), 0, 2);
    $formulaShardPath = PROJECT_ROOT . "/app/config/content/formulas/{$hex}/shard_{$hex}.json";
    $origShardMtime = (int)filemtime($formulaShardPath);
    $prevErrLog = ini_set('error_log', '/dev/null');

    try {
        withIsolatedEnv(['APP_ENV' => 'production'], ['REMOTE_ADDR' => '127.0.0.1'], function () use ($t, $ctrl, $subCache, $formulaShardPath) {
            $build1 = $ctrl->warmHtmlCache(true, ['generalized-coordinates']);
            $t->assertSame(1, $build1['subtopics_built']);

            $build2 = $ctrl->warmHtmlCache(false, ['generalized-coordinates']);
            $t->assertSame(0, $build2['subtopics_built']);
            $t->assertSame(1, $build2['subtopics_skipped']);

            // Simulate a fixlatex update to the referenced formula's hex shard
            $cacheMtime = (int)filemtime($subCache);
            touch($formulaShardPath, $cacheMtime + 10);

            $build3 = $ctrl->warmHtmlCache(false, ['generalized-coordinates']);
            $t->assertSame(1, $build3['subtopics_built'], 'Formula shard update must invalidate referencing subtopic HTML cache');
            $t->assertSame(0, $build3['subtopics_skipped']);
        });
    } finally {
        touch($formulaShardPath, $origShardMtime);
        clearstatcache(true, $formulaShardPath);
        if ($prevErrLog !== false) {
            ini_set('error_log', $prevErrLog);
        }
        if ($hadSub === null) {
            @unlink($subCache);
        } else {
            file_put_contents($subCache, $hadSub, LOCK_EX);
        }
    }
});

$runner->run('Stage4DeploymentTest', 'testSchemaMigrationsRunnerAndProductionSeedGuard', function (NativePhpTestRunner $t) {
    $mockDb = new class {
        public array $queries = [];
        public array $appliedRows = [];

        public function runQuery(string $sql, array $params = []): object
        {
            $this->queries[] = ['sql' => trim($sql), 'params' => $params];
            if (str_starts_with(trim($sql), 'INSERT INTO schema_migrations') && !empty($params[0])) {
                $this->appliedRows[$params[0]] = ['migration' => $params[0], 'checksum' => $params[1] ?? ''];
            }
            return (object)['ok' => true];
        }

        public function fetchAll(string $sql): array
        {
            if (str_contains($sql, 'FROM schema_migrations')) {
                return array_values($this->appliedRows);
            }
            return [];
        }
    };

    $app = new \flight\Engine();
    $app->map('db', fn() => $mockDb);
    $svc = new \app\logic\PhysicsService($app);

    // 1. Test lexical ordering (.sql + .php) and idempotency via schema_migrations ledger
    $tmpDir = sys_get_temp_dir() . '/terra_mig_test_' . uniqid();
    mkdir($tmpDir, 0775, true);
    file_put_contents($tmpDir . '/001_init.sql', "CREATE TABLE IF NOT EXISTS demo_a (id INT PRIMARY KEY);\n");
    file_put_contents($tmpDir . '/002_seed.php', "<?php\n\$migrationExecSql('CREATE TABLE IF NOT EXISTS demo_b (id INT PRIMARY KEY)');\n");

    try {
        $first = $svc->runMigrations($tmpDir);
        $t->assertSame(2, $first['checked']);
        $t->assertSame(['001_init.sql', '002_seed.php'], $first['applied']);
        $t->assertSame([], $first['skipped']);

        $second = $svc->runMigrations($tmpDir);
        $t->assertSame([], $second['applied'], 'Second run must skip already-applied migrations');
        $t->assertSame(['001_init.sql', '002_seed.php'], $second['skipped']);
    } finally {
        @unlink($tmpDir . '/001_init.sql');
        @unlink($tmpDir . '/002_seed.php');
        @rmdir($tmpDir);
    }

    // 2. Test real scripts/migrations/001_create_rbac_and_review_tables.php under APP_ENV=production
    $mockDb->queries = [];
    $mockDb->appliedRows = [];
    withIsolatedEnv(['APP_ENV' => 'production'], [], function () use ($t, $svc, $mockDb) {
        $prodMig = $svc->runMigrations(PROJECT_ROOT . '/scripts/migrations');
        $t->assertTrue(in_array('001_create_rbac_and_review_tables.php', $prodMig['applied'], true), '001 migration must be applied');

        $allSql = implode("\n", array_column($mockDb->queries, 'sql'));
        $t->assertContains('CREATE TABLE IF NOT EXISTS users', $allSql);
        $t->assertContains('CREATE TABLE IF NOT EXISTS formula_reviews', $allSql);
        $t->assertContains('CREATE TABLE IF NOT EXISTS formula_audit_logs', $allSql);
        $t->assertFalse(str_contains($allSql, 'INSERT INTO users'), 'Production migration must not seed dev_mock users');
    });

    // 3. Verify pruneOrphans(true) returns [] gracefully on a brand-new empty DB before subtopics table exists
    $emptyNewDb = new class {
        public function fetchAll(string $sql): array
        {
            throw new RuntimeException("SQLSTATE[42S02]: Base table or view not found: 1146 Table 'terra.subtopics' doesn't exist");
        }
    };
    $appFresh = new \flight\Engine();
    $appFresh->map('db', fn() => $emptyNewDb);
    $svcFresh = new \app\logic\PhysicsService($appFresh);
    $t->assertSame([], $svcFresh->pruneOrphans(true), 'pruneOrphans must not crash on fresh empty database');
});

$runner->run('Stage4DeploymentTest', 'testHtaccessCompressionAcmeExemptionAndUpdateProdScript', function (NativePhpTestRunner $t) {
    $htaccess = (string)file_get_contents(PROJECT_ROOT . '/public/.htaccess');
    $t->assertContains('AddOutputFilterByType DEFLATE', $htaccess);
    $t->assertContains('application/javascript', $htaccess);
    $t->assertContains('max-age=31536000, immutable', $htaccess);
    $t->assertContains('!^/\.well-known/', $htaccess, '.htaccess must exempt /.well-known/ for Let\'s Encrypt renewals');
    $t->assertContains('RewriteRule (?:^|/)\. - [F,L]', $htaccess);

    $apacheExample = (string)file_get_contents(PROJECT_ROOT . '/deploy/apache/physicslab.ca-le-ssl.conf.example');
    $t->assertContains('ServerName physicslab.ca', $apacheExample);
    $t->assertContains('DocumentRoot /srv/www/terra/public', $apacheExample);
    $t->assertContains('SetEnv APP_ENV production', $apacheExample);

    $sqlProv = (string)file_get_contents(PROJECT_ROOT . '/deploy/mariadb/provision_terra.sql');
    $t->assertContains("'terra_app'@'localhost'", $sqlProv);
    $t->assertFalse(str_contains($sqlProv, 'GRANT ALL'), 'MariaDB user must follow least-privilege grants');

    $tuning = (string)file_get_contents(PROJECT_ROOT . '/deploy/mariadb/99-terra-tuning.cnf');
    $t->assertContains('innodb_buffer_pool_size', $tuning);

    $updateScriptPath = PROJECT_ROOT . '/scripts/update_prod.sh';
    $t->assertTrue(is_file($updateScriptPath) && is_executable($updateScriptPath), 'scripts/update_prod.sh must exist and be executable');
    $updateSrc = (string)file_get_contents($updateScriptPath);
    $t->assertContains('git pull --ff-only', $updateSrc);
    $t->assertContains('--quick', $updateSrc);
    $t->assertContains('--rollback', $updateSrc);
    $t->assertContains('--resolve "${DOMAIN}:443:127.0.0.1"', $updateSrc);

    // Guard against PHP 8.4+ E_STRICT deprecation and bare include_path requires in production bootstrap/config
    $bootstrapSrc = (string)file_get_contents(PROJECT_ROOT . '/app/config/bootstrap.php');
    $configSampleSrc = (string)file_get_contents(PROJECT_ROOT . '/app/config/config_sample.php');
    $t->assertFalse(str_contains($bootstrapSrc, 'E_STRICT'), 'bootstrap.php must not reference PHP 8.4-deprecated E_STRICT');
    $t->assertFalse(str_contains($configSampleSrc, 'E_STRICT'), 'config_sample.php must not reference PHP 8.4-deprecated E_STRICT');
    $t->assertFalse(str_contains($bootstrapSrc, "require('config.php')"), 'bootstrap.php must use __DIR__ for config.php');
    $t->assertFalse(str_contains($bootstrapSrc, "require('services.php')"), 'bootstrap.php must use __DIR__ for services.php');
    $t->assertFalse(str_contains($bootstrapSrc, "require('routes.php')"), 'bootstrap.php must use __DIR__ for routes.php');

    // Guard against non-root polkit pkttyagent errors and config.php group-loss lockouts in update_prod.sh
    $t->assertContains('--no-ask-password', $updateSrc, 'update_prod.sh must avoid spawning polkit pkttyagent');
    $t->assertContains('app/config/config.php', $updateSrc, 'update_prod.sh must verify/restore www-data group access on config.php');
    $t->assertContains('chmod 640 "${cfg_file}"', $updateSrc, 'update_prod.sh must preserve 640 mode on config.php');
});

$jsonFlag = in_array('--json', $argv ?? [], true);
exit($runner->summary($jsonFlag));
