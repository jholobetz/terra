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
            "equation": "E_k = \\frac{1}{2} m v^2",
            "status": "platinum",
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
            "equation": "E_k = \\frac{1}{2} m v^2",
            "status": "platinum",
            "cas_validation": {
                "status": "COMPLETELY_INVALID_STATUS",
                "is_homogeneous": True
            }
        }
    }

    errors = list(validator.iter_errors(invalid_shard))
    assert len(errors) > 0, "Schema must reject invalid cas_validation status enum"


def test_explainer_php_view_contains_cas_badge_markup():
    assert os.path.exists(EXPLAINER_VIEW_PATH)
    with open(EXPLAINER_VIEW_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    assert 'id="cas-verified-badge"' in html, "View must contain #cas-verified-badge"
    assert 'id="cas-verified-text"' in html, "View must contain #cas-verified-text"


def test_explainer_js_handles_cas_validation():
    assert os.path.exists(EXPLAINER_JS_PATH)
    with open(EXPLAINER_JS_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "cas-verified-badge" in code, "equation_explainer.js must reference cas-verified-badge"
    assert "cas_validation" in code, "equation_explainer.js must read cas_validation property"


def test_inspector_js_handles_cas_badge():
    assert os.path.exists(INSPECTOR_JS_PATH)
    with open(INSPECTOR_JS_PATH, "r", encoding="utf-8") as f:
        code = f.read()

    assert "cas_validation" in code, "formula_inspector.js must check cas_validation"
    assert "✓ CAS:" in code, "formula_inspector.js must render CAS badge label"
