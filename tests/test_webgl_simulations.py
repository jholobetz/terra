"""
Tests for WebGL Physics Harness and Relativistic Black Hole Simulation
(Roadmap Item 2.3 — Option A)
"""

import os
import re
import json
import subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_webgl_harness_structure():
    """Verify that WebGLPhysicsHarness is properly structured and contains core APIs."""
    harness_path = os.path.join(PROJECT_ROOT, "public", "js", "lib", "webgl_physics_harness.js")
    assert os.path.isfile(harness_path), f"Missing harness file: {harness_path}"

    with open(harness_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Core class and export checks
    assert "class WebGLPhysicsHarness" in content
    assert "global.WebGLPhysicsHarness = WebGLPhysicsHarness" in content

    # Essential methods
    expected_methods = [
        "_initContext",
        "_initQuadBuffer",
        "setShaders",
        "_compileShader",
        "setUniform",
        "_applyStandardUniforms",
        "updateCameraVectors",
        "setCameraOrbit",
        "_bindEvents",
        "resize",
        "start",
        "pause",
        "render",
        "createPingPongFBO",
        "swapPingPong",
        "capturePNG"
    ]
    for method in expected_methods:
        assert method in content, f"Missing method in WebGLPhysicsHarness: {method}"


def test_relativistic_black_hole_simulation():
    """Verify that relativistic-black-hole.js contains valid GLSL shader and physical parameters."""
    sim_path = os.path.join(PROJECT_ROOT, "public", "js", "simulations", "relativistic-black-hole.js")
    assert os.path.isfile(sim_path), f"Missing simulation file: {sim_path}"

    with open(sim_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Verify instantiation of harness
    assert "new WebGLPhysicsHarness" in code

    # Verify GLSL 300 es fragment shader
    assert "#version 300 es" in code
    assert "precision highp float;" in code
    assert "out vec4 fragColor;" in code

    # Verify essential physical uniforms in GLSL
    glsl_uniforms = [
        "u_resolution",
        "u_time",
        "u_cam_pos",
        "u_cam_dir",
        "u_cam_up",
        "u_cam_right",
        "u_spin",
        "u_mass",
        "u_disk_bright",
        "u_disk_outer",
        "u_isco",
        "u_r_plus",
        "u_doppler_enabled",
        "u_disk_enabled",
        "u_stars_enabled"
    ]
    for u in glsl_uniforms:
        assert f"uniform " in code and u in code, f"Missing uniform in black hole shader: {u}"

    # Verify relativistic physics equations in shader & JS
    assert "computeRelativisticQuantities" in code
    assert "r_± = M ± sqrt(M^2 - a^2)" in code or "rPlus = M + Math.sqrt" in code
    assert "aGrav" in code
    assert "aDrag" in code
    assert "vPhi" in code
    assert "beaming" in code

    # Verify UI presets
    assert 'data-preset="gargantua"' in code
    assert 'data-preset="m87"' in code
    assert 'data-preset="schwarzschild"' in code
    assert 'data-preset="extreme"' in code


def test_simulation_registration():
    """Verify that relativistic-black-hole is registered in simulations.json and _topic_icons.php."""
    # Check simulations.json
    sims_json_path = os.path.join(PROJECT_ROOT, "app", "config", "simulations.json")
    assert os.path.isfile(sims_json_path), f"Missing simulations.json: {sims_json_path}"

    with open(sims_json_path, "r", encoding="utf-8") as f:
        sims = json.load(f)

    assert "relativistic-black-hole" in sims
    rbh = sims["relativistic-black-hole"]
    assert rbh["slug"] == "relativistic-black-hole"
    assert "Relativistic Kerr Black Hole Raytracer" in rbh["title"]
    assert len(rbh["equations"]) >= 3

    # Check _topic_icons.php category mapping
    icons_path = os.path.join(PROJECT_ROOT, "app", "views", "physics", "_topic_icons.php")
    with open(icons_path, "r", encoding="utf-8") as f:
        icons_code = f.read()

    assert "'relativistic-black-hole'" in icons_code


def test_simulation_php_rendering():
    """Verify that Flight PHP controller renders the simulation page and catalog without errors."""
    php_code = """
    define('FLIGHT_SKIP_START', true);
    require 'app/config/bootstrap.php';
    $controller = Flight::physicsController();
    ob_start();
    $controller->viewSimulation('relativistic-black-hole');
    $html = ob_get_clean();
    if (strpos($html, 'Relativistic Kerr Black Hole Raytracer') === false) {
        exit(1);
    }
    if (strpos($html, 'webgl_physics_harness.js') === false) {
        exit(2);
    }
    if (strpos($html, 'relativistic-black-hole.js') === false) {
        exit(3);
    }
    echo 'OK';
    """
    cmd = ["php", "-r", php_code]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, f"PHP viewSimulation failed: {result.stderr or result.stdout}"
    assert "OK" in result.stdout
