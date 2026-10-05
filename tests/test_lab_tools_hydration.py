"""
Tests for Lab Tools State Hydration & Deep-Linking (Phase 2.5)
Verifies that all 5 flagship analytical instruments and the Unified Cockpit
support URL state hydration, preset pre-loading, and deep-linking.
"""

import os
import subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_lab_tools_views_php_rendering():
    """Verify that Flight PHP controller renders all 5 Lab Tools views plus the cockpit hub."""
    php_code = """
    define('FLIGHT_SKIP_START', true);
    require 'app/config/bootstrap.php';
    $controller = Flight::physicsController();

    $actions = [
        'labTools' => ['The Unified Physics Laboratory', 'cockpit-crucible-section'],
        'legendreTransformer' => ['Symbolic Legendre Transformer', 'preset-btn'],
        'noethersVault' => ["Noether's Vault", 'symmetry-list'],
        'correspondenceWorkspace' => ['Classical-to-Quantum Correspondence Workspace', 'mode-select-box'],
        'anthropicTuner' => ['Anthropic Constant Tuner', 'tuner-preset-btn'],
        'notationToggle' => ['Multi-Representation Notation Toggle', 'theory-list']
    ];

    $results = [];
    foreach ($actions as $action => $checks) {
        ob_start();
        $controller->$action();
        $html = ob_get_clean();
        $missing = [];
        foreach ($checks as $needle) {
            if (strpos($html, $needle) === false) {
                $missing[] = $needle;
            }
        }
        $results[$action] = [
            'length' => strlen($html),
            'missing' => $missing
        ];
    }
    echo json_encode($results);
    """

    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert res.returncode == 0, f"PHP rendering failed: {res.stderr}\n{res.stdout}"
    import json
    data = json.loads(res.stdout)

    for action, res_data in data.items():
        assert len(res_data["missing"]) == 0, f"Action {action} missing expected markers: {res_data['missing']}"
        assert res_data["length"] > 500, f"Action {action} returned suspiciously short HTML ({res_data['length']} bytes)"


def test_legendre_transformer_url_hydration():
    """Verify that legendre_transformer.js supports URL state hydration and presets."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "legendre_transformer.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "URLSearchParams" in content, "legendre_transformer.js must use URLSearchParams"
    assert "applyPreset" in content, "legendre_transformer.js must have applyPreset function"
    assert "urlParams.get('preset')" in content or 'urlParams.get("preset")' in content, "Must check preset param"
    assert "replaceState" in content, "Must sync browser URL on preset change"

    # Verify all 10 physical presets are present
    expected_presets = [
        "sho", "pendulum", "duffing", "relativistic", "em_field",
        "coriolis", "central_force", "kepler", "spherical_3d", "singular"
    ]
    for preset in expected_presets:
        assert f"{preset}:" in content, f"Missing preset {preset} in legendre_transformer.js"

    # Also verify that the PHP view contains preset buttons for each
    php_path = os.path.join(PROJECT_ROOT, "app", "views", "physics", "legendre_transformer.php")
    with open(php_path, "r", encoding="utf-8") as f:
        php_content = f.read()
    for preset in expected_presets:
        assert f'data-preset="{preset}"' in php_content, f"Missing button for preset {preset} in PHP view"


def test_noethers_vault_url_hydration():
    """Verify that noethers_vault.js hydrates symmetry from URL query parameters."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "noethers_vault.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "URLSearchParams" in content, "noethers_vault.js must use URLSearchParams"
    assert "requestedSymmetry" in content, "noethers_vault.js must check for symmetry param"
    assert "replaceState" in content, "Must sync URL on symmetry change"

    # Verify core symmetries
    for sym_id in ["time_translation", "space_translation", "space_rotation", "gauge_u1", "lorentz_boost"]:
        assert f'id: "{sym_id}"' in content, f"Missing symmetry {sym_id} in noethers_vault.js"


def test_correspondence_workspace_url_hydration():
    """Verify that correspondence_workspace.js hydrates mode and potential from URL."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "correspondence_workspace.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "URLSearchParams" in content, "correspondence_workspace.js must use URLSearchParams"
    assert "reqMode" in content or "urlParams.get(\"mode\")" in content, "Must check mode param"
    assert "reqPot" in content or "urlParams.get(\"pot\")" in content, "Must check pot param"
    assert "replaceState" in content, "Must sync URL on mode/potential change"


def test_anthropic_tuner_url_hydration():
    """Verify that anthropic_tuner.js supports named presets and individual dial URL parameters."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "anthropic_tuner.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "TUNER_PRESETS" in content, "anthropic_tuner.js must define TUNER_PRESETS"
    assert "URLSearchParams" in content, "anthropic_tuner.js must use URLSearchParams"
    assert "applyPreset" in content, "anthropic_tuner.js must define applyPreset"
    assert "setDialValue" in content, "anthropic_tuner.js must define setDialValue"
    assert "replaceState" in content, "Must sync URL on dial adjustment"

    # Verify preset keys
    for preset in ["standard", "weak_gravity", "collapse", "quantum_realm", "weak_alpha"]:
        assert f"{preset}:" in content, f"Missing preset {preset} in anthropic_tuner.js"


def test_notation_toggle_url_hydration():
    """Verify that notation_toggle.js hydrates theory and representation from URL."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "notation_toggle.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "URLSearchParams" in content, "notation_toggle.js must use URLSearchParams"
    assert "syncURLParams" in content, "notation_toggle.js must define syncURLParams"
    assert "replaceState" in content, "Must sync URL on theory/representation switch"

    # Verify theories
    for theory in ["maxwell", "einstein", "schrodinger", "dirac"]:
        assert f'id: "{theory}"' in content, f"Missing theory {theory} in notation_toggle.js"


def test_cockpit_deep_links_resolve_correctly():
    """Verify that lab_cockpit.js contains valid deepLink query parameters matching the instruments."""
    js_path = os.path.join(PROJECT_ROOT, "public", "js", "lab_cockpit.js")
    with open(js_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "/physics/legendre-transformer?preset=sho" in content
    assert "/physics/legendre-transformer?preset=relativistic" in content
    assert "/physics/legendre-transformer?preset=pendulum" in content
    assert "/physics/notation-toggle?theory=maxwell&rep=relativistic_tensor" in content
    assert "/physics/correspondence-workspace?mode=ehrenfest&pot=barrier" in content
    assert "/physics/anthropic-tuner?preset=collapse" in content


def test_subtopic_encyclopedia_launchers_resolution():
    """Verify that LabToolsLauncher resolves appropriate interactive targets for diverse subtopics."""
    php_code = """
    require_once 'app/logic/LabToolsLauncher.php';

    $testCases = [
        ['slug' => 'lagrangian-mechanics', 'parent' => 'classical-mechanics', 'expected_tool' => 'Analytical Mechanics Workbench', 'expected_param' => 'preset=sho'],
        ['slug' => 'noethers-theorem', 'parent' => 'theoretical-physics', 'expected_tool' => "Noether's Vault", 'expected_param' => 'symmetry=time_translation'],
        ['slug' => 'schrodinger-equation', 'parent' => 'quantum-physics', 'expected_tool' => 'Correspondence Workspace', 'expected_param' => 'mode=ehrenfest'],
        ['slug' => 'fine-structure-constant', 'parent' => 'astrophysics', 'expected_tool' => 'The Multiverse Creator', 'expected_param' => 'preset=weak_alpha'],
        ['slug' => 'maxwells-equations', 'parent' => 'electromagnetism', 'expected_tool' => 'The Rosetta Stone of Physics', 'expected_param' => 'theory=maxwell'],
        ['slug' => 'pendulum', 'parent' => 'classical-mechanics', 'expected_tool' => 'Simulations Observatory', 'expected_param' => '/physics/simulations/pendulum'],
        ['slug' => 'keplers-second-law', 'parent' => 'astrophysics', 'expected_tool' => 'Analytical Mechanics Workbench', 'expected_param' => 'preset=kepler'],
        ['slug' => 'rotational-dynamics', 'parent' => 'classical-mechanics', 'expected_tool' => 'Analytical Mechanics Workbench', 'expected_param' => 'preset=coriolis'],
        // Generic fallback test
        ['slug' => 'unknown-arbitrary-topic', 'parent' => 'quantum-physics', 'expected_tool' => 'Correspondence Workspace', 'expected_param' => 'correspondence-workspace'],
        ['slug' => 'unknown-arbitrary-topic', 'parent' => '', 'expected_tool' => 'The Unified Physics Laboratory', 'expected_param' => '/physics/lab-tools']
    ];

    $results = [];
    foreach ($testCases as $tc) {
        $launcher = \\App\\Logic\\LabToolsLauncher::resolve($tc['slug'], $tc['parent']);
        $results[] = [
            'slug' => $tc['slug'],
            'url' => $launcher['url'],
            'tool_name' => $launcher['tool_name'],
            'has_tool' => strpos($launcher['tool_name'], $tc['expected_tool']) !== false,
            'has_param' => strpos($launcher['url'], $tc['expected_param']) !== false,
            'is_valid_url' => strpos($launcher['url'], '/physics/') === 0
        ];
    }
    echo json_encode($results);
    """

    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert res.returncode == 0, f"Launcher resolution test failed: {res.stderr}\n{res.stdout}"
    import json
    results = json.loads(res.stdout)
    for r in results:
        assert r["has_tool"], f"Tool name mismatch for {r['slug']}: got {r['tool_name']}"
        assert r["has_param"], f"URL parameter mismatch for {r['slug']}: got {r['url']}"
        assert r["is_valid_url"], f"Invalid URL for {r['slug']}: got {r['url']}"


def test_subtopic_html_rendering_with_launchers():
    """Verify that Flight PHP renders subtopics with both the header launcher badge and cockpit bridge."""
    php_code = """
    define('FLIGHT_SKIP_START', true);
    require 'app/config/bootstrap.php';
    require_once 'app/logic/LabToolsLauncher.php';

    $launcher = \\App\\Logic\\LabToolsLauncher::resolve('lagrangian-mechanics', 'classical-mechanics');

    Flight::view()->set([
        'title' => 'Lagrangian Mechanics',
        'slug' => 'lagrangian-mechanics',
        'content' => '<p>The stationary action principle defines mechanical motion.</p>',
        'breadcrumbs' => [['url' => '/physics/topic/classical-mechanics', 'title' => 'Classical Mechanics']],
        'parents' => ['classical-mechanics'],
        'labLauncher' => $launcher,
        'verification' => ['consensus_score' => 0.98, 'verified_date' => '2026-10-01', 'citations' => []],
        'nonce' => 'testnonce'
    ]);

    ob_start();
    Flight::view()->render('physics/subtopic');
    $html = ob_get_clean();

    $checks = [
        'lab-launcher-badge' => strpos($html, 'lab-launcher-badge') !== false,
        'subtopic-cockpit-bridge' => strpos($html, 'subtopic-cockpit-bridge') !== false,
        'Analytical Mechanics Workbench' => strpos($html, 'Analytical Mechanics Workbench') !== false,
        'legendre-transformer?preset=sho' => strpos($html, 'legendre-transformer?preset=sho') !== false
    ];

    echo json_encode($checks);
    """

    res = subprocess.run(
        ["php", "-r", php_code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True
    )

    assert res.returncode == 0, f"Subtopic rendering failed: {res.stderr}\n{res.stdout}"
    import json
    checks = json.loads(res.stdout)
    for check_name, passed in checks.items():
        assert passed, f"Failed assertion: subtopic HTML missing {check_name}"

