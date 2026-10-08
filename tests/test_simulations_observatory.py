"""
Tests for The Simulations Observatory Landing Page & Taxonomy
(docs/sim_fixes.md - Phase 1)
"""

import os
import json
import subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_simulations_json_taxonomy_and_metadata():
    """Verify that all 17 simulations have enriched categories, engines, difficulties, and equations."""
    sims_json_path = os.path.join(PROJECT_ROOT, "app", "config", "simulations.json")
    assert os.path.isfile(sims_json_path), f"Missing simulations.json: {sims_json_path}"

    with open(sims_json_path, "r", encoding="utf-8") as f:
        sims = json.load(f)

    assert len(sims) == 17, f"Expected 17 simulations, found {len(sims)}"

    valid_categories = {
        "classical-mechanics",
        "electromagnetism",
        "relativity",
        "quantum-physics",
        "thermodynamics-statistical-mechanics",
        "fluids-nonlinear",
        "astrophysics"
    }

    for slug, sim in sims.items():
        assert "category" in sim, f"Missing category for {slug}"
        assert sim["category"] in valid_categories, f"Invalid category {sim['category']} for {slug}"
        assert "engine" in sim and len(sim["engine"]) > 0, f"Missing engine for {slug}"
        assert "difficulty" in sim and len(sim["difficulty"]) > 0, f"Missing difficulty for {slug}"
        assert "tags" in sim and len(sim["tags"]) > 0, f"Missing tags for {slug}"
        assert "equations" in sim and len(sim["equations"]) >= 1, f"Missing equations for {slug}"


def test_simulations_observatory_php_rendering():
    """Verify that Flight PHP controller renders the modernized observatory landing page."""
    php_code = """
    define('FLIGHT_SKIP_START', true);
    require 'app/config/bootstrap.php';
    $controller = Flight::physicsController();
    ob_start();
    $controller->simulations();
    $html = ob_get_clean();

    // Check essential elements
    $must_contain = [
        'The Simulations Observatory',
        'Phenomenological Observatory',
        'Looking for Analytical Symmetries or Symbolic CAS Proofs',
        'observatory-hero-section',
        'observatory-hero-canvas',
        'hero-preset-btn',
        'hero-launch-link',
        'sim-search-input',
        'sim-filter-pill',
        'simulations-deck-grid',
        'sim-card',
        'Governing Equation',
        'Relativistic Kerr Black Hole Raytracer',
        'Vortex Street',
        'observatory_hero.js'
    ];

    foreach ($must_contain as $needle) {
        if (strpos($html, $needle) === false && strpos($html, html_entity_decode($needle)) === false) {
            echo "Missing: " . $needle;
            exit(1);
        }
    }
    echo 'OK';
    """
    cmd = ["php", "-r", php_code]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, f"PHP simulations() failed: {result.stderr or result.stdout}"
    assert "OK" in result.stdout


def test_observatory_hero_js_structure():
    """Verify that observatory_hero.js contains the 4 flagship simulation solvers."""
    hero_path = os.path.join(PROJECT_ROOT, "public", "js", "observatory_hero.js")
    assert os.path.isfile(hero_path), f"Missing observatory_hero.js: {hero_path}"

    with open(hero_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Core class and presets
    assert "class ObservatoryHero" in content
    assert "'kerr'" in content
    assert "'chaos'" in content
    assert "'quantum'" in content
    assert "'vortex'" in content

    # Numerical methods
    assert "_rk4Step" in content
    assert "_renderKerr" in content
    assert "_renderChaos" in content
    assert "_renderQuantum" in content
    assert "_renderVortex" in content
    assert "IntersectionObserver" in content


def test_elevated_simulations():
    """Verify that pendulum and projectile-motion have been elevated to university-grade engines."""
    # 1. Pendulum checks
    pendulum_js = os.path.join(PROJECT_ROOT, "public", "js", "simulations", "pendulum.js")
    assert os.path.isfile(pendulum_js)
    with open(pendulum_js, "r", encoding="utf-8") as f:
        p_code = f.read()
    assert "rk4Step" in p_code
    assert "poincarePoints" in p_code
    assert "DETERMINISTIC CHAOS" in p_code
    assert "PHASE SPACE" in p_code

    # 2. Projectile motion checks
    projectile_js = os.path.join(PROJECT_ROOT, "public", "js", "simulations", "projectile-motion.js")
    assert os.path.isfile(projectile_js)
    with open(projectile_js, "r", encoding="utf-8") as f:
        pm_code = f.read()
    assert "R_EARTH_KM" in pm_code
    assert "GM" in pm_code
    assert "stepProjectile" in pm_code
    assert "CIRCULAR ORBIT" in pm_code
    assert "HYPERBOLIC ESCAPE" in pm_code

    # 3. PHP Rendering of both simulation pages
    php_code = """
    define('FLIGHT_SKIP_START', true);
    require 'app/config/bootstrap.php';
    $controller = Flight::physicsController();

    // Check pendulum page
    ob_start();
    $controller->viewSimulation('pendulum');
    $p_html = ob_get_clean();
    if (strpos($p_html, 'Damped-Driven Chaotic Pendulum') === false) {
        echo 'Missing Damped-Driven Chaotic Pendulum in page';
        exit(1);
    }

    // Check projectile-motion page
    ob_start();
    $controller->viewSimulation('projectile-motion');
    $pm_html = ob_get_clean();
    if (strpos($pm_html, "Newton's Orbital Cannon & Escape Trajectories") === false) {
        echo 'Missing Newton Orbital Cannon in page';
        exit(2);
    }

    echo 'OK';
    """
    cmd = ["php", "-r", php_code]
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    assert result.returncode == 0, f"PHP viewSimulation failed: {result.stderr or result.stdout}"
    assert "OK" in result.stdout


