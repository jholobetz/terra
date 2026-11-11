"""
🔬 Terra Physics Lab - Unit & Integration Tests for CAS Badging & Data Layer Tagging
Verifies schema compliance of cas_validation metadata, batch tagging execution,
and UI template badging integration.
"""

import os
import json
import pytest
from jsonschema import Draft7Validator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formula.schema.json")
EXPLAINER_VIEW_PATH = os.path.join(PROJECT_ROOT, "app", "views", "physics", "equation_explainer.php")
EXPLAINER_JS_PATH = os.path.join(PROJECT_ROOT, "public", "js", "equation_explainer.js")
INSPECTOR_JS_PATH = os.path.join(PROJECT_ROOT, "public", "js", "formula_inspector.js")


def load_formula_schema():
    assert os.path.exists(SCHEMA_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_schema_includes_cas_validation_definition():
    schema = load_formula_schema()
    props = schema["additionalProperties"]["properties"]
    assert "cas_validation" in props, "formula.schema.json must define cas_validation"

    cas_props = props["cas_validation"]["properties"]
    assert "status" in cas_props
    assert "is_homogeneous" in cas_props
    assert "quantity" in cas_props
    assert "dimension_latex" in cas_props
    assert "verified_at" in cas_props


def test_schema_validates_sample_with_cas_validation():
    schema = load_formula_schema()
    validator = Draft7Validator(schema)

    sample_shard = {
        "sample-formula-id": {
            "title": "Kinetic Energy",
            "category": "classical-mechanics",
            "record_type": "equation",
            "lineage_confidence": "cas_verified",
            "equation": "E_k = \\frac{1}{2} m v^2",
            "status": "platinum",
            "description": "Defines the non-relativistic translational kinetic energy $E_k$ of a point mass $m$ moving at speed $v$ in an inertial frame.",
            "conceptual_definition": "Translational energy stored in the motion of a massive body relative to an inertial observer.",
            "intuitive_summary": "Doubling a body's speed quadruples the mechanical work required to bring it to rest.",
            "interpretation": "Integrates the net mechanical power $F \\cdot v$ expended along a trajectory from rest up to speed $v$.",
            "symmetry_origin": "Emerges as the spatial translational Noether invariant at leading quadratic order in $v/c$ of the Poincaré group.",
            "limits_and_boundary": "Valid in the non-relativistic regime $v \\ll c$ where the Lorentz factor satisfies $\\gamma - 1 \\approx v^2 / (2c^2)$.",
            "semantic_variables": {
                "E_k": {"name": "Kinetic Energy", "unit": "J"},
                "m": {"name": "Mass", "unit": "kg"},
                "v": {"name": "Velocity", "unit": "m/s"}
            },
            "cas_validation": {
                "status": "HOMOGENEOUS",
                "is_homogeneous": True,
                "quantity": "Energy / Work / Hamiltonian",
                "dimension_latex": "[\\text{M} \\cdot \\text{L}^{2} / (\\text{T}^{2})]",
                "verified_at": 1789243000
            }
        }
    }

    errors = list(validator.iter_errors(sample_shard))
    assert len(errors) == 0, f"Schema validation error on valid cas_validation: {errors}"


def test_schema_rejects_invalid_cas_status():
    schema = load_formula_schema()
    validator = Draft7Validator(schema)

    invalid_shard = {
        "sample-formula-id": {
            "title": "Kinetic Energy",
            "category": "classical-mechanics",
            "record_type": "equation",
            "lineage_confidence": "cas_verified",
            "equation": "E_k = \\frac{1}{2} m v^2",
            "status": "platinum",
            "description": "Defines the non-relativistic translational kinetic energy $E_k$ of a point mass $m$ moving at speed $v$ in an inertial frame.",
            "conceptual_definition": "Translational energy stored in the motion of a massive body relative to an inertial observer.",
            "intuitive_summary": "Doubling a body's speed quadruples the mechanical work required to bring it to rest.",
            "interpretation": "Integrates the net mechanical power $F \\cdot v$ expended along a trajectory from rest up to speed $v$.",
            "symmetry_origin": "Emerges as the spatial translational Noether invariant at leading quadratic order in $v/c$ of the Poincaré group.",
            "limits_and_boundary": "Valid in the non-relativistic regime $v \\ll c$ where the Lorentz factor satisfies $\\gamma - 1 \\approx v^2 / (2c^2)$.",
            "semantic_variables": {
                "E_k": {"name": "Kinetic Energy", "unit": "J"},
                "m": {"name": "Mass", "unit": "kg"},
                "v": {"name": "Velocity", "unit": "m/s"}
            },
            "cas_validation": {
                "status": "COMPLETELY_INVALID_STATUS",
                "is_homogeneous": True
            }
        }
    }

    errors = list(validator.iter_errors(invalid_shard))
    assert any("COMPLETELY_INVALID_STATUS" in str(e) for e in errors), "Schema must reject invalid cas_validation status enum"


def test_explainer_php_view_contains_cas_badge_markup():
    assert os.path.exists(EXPLAINER_VIEW_PATH)
    with open(EXPLAINER_VIEW_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="cas-verified-badge"' in html, "View must contain #cas-verified-badge"
    assert 'id="cas-verified-text"' in html, "View must contain #cas-verified-text"
    assert 'id="lineage-provenance-badge"' in html, "View must contain #lineage-provenance-badge"
    assert 'id="record-type-badge"' in html, "View must contain #record-type-badge"
    assert 'id="formula-description-subtitle"' in html, "View must contain #formula-description-subtitle"


def test_explainer_js_handles_cas_validation():
    assert os.path.exists(EXPLAINER_JS_PATH)
    with open(EXPLAINER_JS_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "cas-verified-badge" in code, "equation_explainer.js must reference cas-verified-badge"
    assert "cas_validation" in code, "equation_explainer.js must read cas_validation property"
    assert "lineage-provenance-badge" in code, "equation_explainer.js must populate lineage-provenance-badge"
    assert "formula-description-subtitle" in code, "equation_explainer.js must populate formula-description-subtitle"
    assert "lineage_confidence" in code, "equation_explainer.js must read lineage_confidence"


def test_inspector_js_handles_cas_badge():
    assert os.path.exists(INSPECTOR_JS_PATH)
    with open(INSPECTOR_JS_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "cas_validation" in code, "formula_inspector.js must check cas_validation"
    assert "✓ CAS:" in code, "formula_inspector.js must render CAS badge label"
    assert "drawer-description-text" in code, "formula_inspector.js must render distinct description lead"
    assert "lineage_confidence" in code, "formula_inspector.js must surface lineage_confidence badge"


def test_explainer_cards_and_graph_surface_provenance():
    cards_js = os.path.join(PROJECT_ROOT, "public", "js", "explainer_cards.js")
    graph_js = os.path.join(PROJECT_ROOT, "public", "js", "formula_graph.js")
    with open(cards_js, "r", encoding="utf-8") as cf:
        cards_code = cf.read()
    with open(graph_js, "r", encoding="utf-8") as gf:
        graph_code = gf.read()

    assert "renderProvenancePill" in cards_code
    assert "lineage_confidence" in cards_code
    assert "renderNodeProvenanceBadges" in graph_code
    assert "isHeuristicDerivation" in graph_code


def test_sitewide_shards_tagged_with_cas_validation():
    from tests.conftest import get_cached_formulas
    formulas = get_cached_formulas()
    total_formulas = len(formulas)
    tagged_count = sum(
        1 for entry in formulas
        if isinstance(entry.get("cas_validation"), dict)
        and entry["cas_validation"].get("is_homogeneous") is True
    )

    assert total_formulas >= 14600, f"Full sitewide catalog must contain >= 14,600 formulas (found {total_formulas})"
    assert tagged_count >= 9000, f"At least 9,000 formulas must be tagged with cas_validation in Git shards (found {tagged_count})"


def test_physics_service_persists_cas_validation_and_avoids_shard_fallback():
    """
    Behavioral test verifying that:
    1. PhysicsService::loadFormula() does NOT fall back to reading JSON shards from disk
       when the MariaDB row schema already contains `derivation_steps` and `cas_validation`
       (even when derivation_steps is NULL, as is true for 99.3% of formulas).
    2. PhysicsService::loadFormula() DOES fall back to the Git JSON shard if the MariaDB
       table schema is missing the `cas_validation` column.
    """
    import subprocess

    php_code = r"""
    define('PROJECT_ROOT', getcwd());
    require_once PROJECT_ROOT . '/vendor/autoload.php';
    require_once PROJECT_ROOT . '/app/logic/PhysicsService.php';

    class MockDbWithCasColumn {
        public function fetchRow($sql, $params = []) {
            return [
                'id' => $params[0],
                'title' => 'DB Loaded Formula',
                'equation' => 'E = m c^2',
                'derivation_steps' => null,
                'cas_validation' => json_encode([
                    'status' => 'HOMOGENEOUS',
                    'is_homogeneous' => true,
                    'quantity' => 'Energy (from DB)'
                ])
            ];
        }
    }

    class MockDbLegacySchemaWithoutCasColumn {
        public function fetchRow($sql, $params = []) {
            return [
                'id' => $params[0],
                'title' => 'Legacy DB Row Without CAS Column',
                'equation' => 'E = m c^2'
                // Note: derivation_steps and cas_validation keys do NOT exist in row array
            ];
        }
    }

    $app1 = new \flight\Engine();
    $app1->register('db', 'MockDbWithCasColumn');
    $svc1 = new \app\logic\PhysicsService($app1);
    $svc1->setPreviewMode(false);

    // Query an ID that exists in shard_00 ('stefan-boltzmann-law') - since DB has the columns,
    // loadFormula() must keep 'Energy (from DB)' and NOT overwrite it from shard_00.json!
    $res1 = $svc1->loadFormula('stefan-boltzmann-law');
    if (($res1['cas_validation']['quantity'] ?? '') !== 'Energy (from DB)') {
        fwrite(STDERR, "FAIL: loadFormula() unnecessarily read disk shard when DB column existed!\n");
        exit(1);
    }

    // Now test legacy unmigrated DB schema missing cas_validation column:
    // loadFormula() MUST fall back to shard_00.json and populate cas_validation.
    $app2 = new \flight\Engine();
    $app2->register('db', 'MockDbLegacySchemaWithoutCasColumn');
    $svc2 = new \app\logic\PhysicsService($app2);
    $svc2->setPreviewMode(false);

    $res2 = $svc2->loadFormula('stefan-boltzmann-law');
    if (empty($res2['cas_validation']['is_homogeneous'])) {
        fwrite(STDERR, "FAIL: loadFormula() did not fall back to disk shard when DB lacked cas_validation column!\n");
        exit(2);
    }

    echo "OK\n";
    """

    proc = subprocess.run(
        ["php", "-r", php_code],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=10
    )
    assert proc.returncode == 0, f"PHP behavioral test failed: {proc.stderr}\n{proc.stdout}"
    assert "OK" in proc.stdout


