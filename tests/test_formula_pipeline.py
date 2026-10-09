#!/usr/bin/env python3
"""
🧪 Pytest Suite for Terra Unified Formula Ingestion Pipeline (Roadmap §3.2)
Tests all 5 stages, collision guards, CAS proofs, DAG reciprocal wiring,
hash registry synchronization, and rollback safety.
"""

import os
import sys
import json
import pytest
import tempfile
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lib.pipeline.formula_pipeline import (
    FormulaIngestionPipeline,
    slugify,
    get_shard_hex,
    normalize_latex_key,
    sanitize_prose_text
)


def test_slugify_and_hex():
    assert slugify("Position-Space Green Function") == "position-space-green-function"
    assert slugify("Maxwell's Equations in Vacuum") == "maxwells-equations-in-vacuum"
    assert len(get_shard_hex("position-space-green-function")) == 2


def test_normalize_latex_key():
    k1 = normalize_latex_key(r"E = \frac{1}{2} m v^2")
    k2 = normalize_latex_key(r"E=\frac{1}{2}mv^2")
    assert k1 == k2
    assert "frac" not in k1
    assert "1/2" in k1


def test_sanitize_prose_text():
    dirty = r"The field is\$\frac{1}{2} and \(x = 5\) with \x08ar{x}."
    cleaned = sanitize_prose_text(dirty)
    assert r"is \frac" in cleaned
    assert "$x = 5$" in cleaned
    assert r"\bar{x}" in cleaned
    assert "\x08" not in cleaned


def test_stage1_validation_and_collision_guard():
    pipeline = FormulaIngestionPipeline(sync_db=False, rebuild_graph=False)

    # Missing equation raises ValueError
    with pytest.raises(ValueError, match="missing required 'equation'"):
        pipeline.stage1_validate_and_prepare({"title": "Test"})

    # HTML tags in equation are stripped
    payload = {
        "title": "Unique New Particle Kinetic Energy",
        "equation": "<b>E</b> = \\frac{1}{2} m v^2",
        "conceptual_definition": "Kinetic energy \\(E\\)."
    }
    prep = pipeline.stage1_validate_and_prepare(payload)
    assert "\\mathbf{E}" in prep["equation"]
    assert "<b>" not in prep["equation"]
    assert "$E$" in prep["conceptual_definition"]
    assert prep["id"] == "unique-new-particle-kinetic-energy"
    assert isinstance(prep["semantic_variables"], dict)


def test_stage1_collision_guard_disambiguation():
    pipeline = FormulaIngestionPipeline(sync_db=False, rebuild_graph=False)

    # Identical equation to existing formula preserves ID
    prep_same = pipeline.stage1_validate_and_prepare({
        "id": "light-cone-boundary-d970bdae",
        "title": "Light Cone Boundary",
        "equation": "ds^2 = 0 \\iff c^2 dt^2 - d\\mathbf{x}^2 = 0"
    })
    assert prep_same["id"] == "light-cone-boundary-d970bdae"

    # Differing equation to existing formula gets disambiguated with hash suffix
    prep_diff = pipeline.stage1_validate_and_prepare({
        "id": "light-cone-boundary-d970bdae",
        "title": "Light Cone Boundary",
        "equation": "ds^2 = c^2 dt^2 - dx^2 - dy^2 - dz^2"
    })
    assert prep_diff["id"].startswith("light-cone-boundary-d970bdae-")
    assert prep_diff["id"] != "light-cone-boundary-d970bdae"


def test_stage2_lineage_resolution_and_reciprocal_wiring():
    pipeline = FormulaIngestionPipeline(sync_db=False, rebuild_graph=False)

    payload = {
        "id": "test-relativistic-momentum-xyz",
        "title": "Relativistic Momentum Component",
        "equation": r"p = \gamma m v",
        "conceptual_definition": "Relativistic momentum with Lorentz gamma factor."
    }
    prep = pipeline.stage1_validate_and_prepare(payload)
    wired, parent_update = pipeline.stage2_wire_bidirectional_dag(prep)

    assert wired["parent_formula_id"] != ""
    assert wired["derivation_type"] != ""
    if parent_update:
        p_path, p_data = parent_update
        p_id = wired["parent_formula_id"]
        assert p_id in p_data
        assert "test-relativistic-momentum-xyz" in p_data[p_id]["subcomponents"]


def test_stage3_cas_invariance_prover():
    pipeline = FormulaIngestionPipeline(sync_db=False, rebuild_graph=False)

    # Homogeneous equation
    homo_data = {
        "id": "test-kinetic-energy",
        "title": "Test Kinetic Energy",
        "equation": "E = \\frac{1}{2} m v^2"
    }
    prep = pipeline.stage1_validate_and_prepare(homo_data)
    proven = pipeline.stage3_verify_cas_invariance(prep)
    assert proven["cas_validation"]["status"] == "verified"
    assert proven["cas_validation"]["is_homogeneous"] is True

    # Inhomogeneous equation
    inhomo_data = {
        "id": "test-mismatch-energy",
        "title": "Test Mismatch Energy",
        "equation": "E = m v^3"
    }
    prep2 = pipeline.stage1_validate_and_prepare(inhomo_data)
    proven2 = pipeline.stage3_verify_cas_invariance(prep2)
    assert proven2["cas_validation"]["status"] == "mismatch"
    assert proven2["cas_validation"]["is_homogeneous"] is False


def test_dry_run_ingest():
    pipeline = FormulaIngestionPipeline(sync_db=False, rebuild_graph=False)
    test_formula = {
        "title": "Harmonic Oscillator Restoring Force",
        "equation": "F = -k x",
        "conceptual_definition": "Hooke's law describing linear restorative force.",
        "interpretation": "Displacement induces proportional restoring force.",
        "symmetry_origin": "Spatial translation invariance around potential minimum.",
        "limits_and_boundary": "Valid in small oscillation linear regime."
    }
    res = pipeline.ingest(test_formula, dry_run=True)
    assert res["success"] is True
    assert res["dry_run"] is True
    assert res["formula_id"] == "harmonic-oscillator-restoring-force"
    assert "shard_file" in res
    assert "cas_validation" in res
    assert res["cas_validation"]["status"] == "verified"


def test_isolated_sandbox_stage4_dual_layer_sync_and_rollback():
    """Tests Stage 4 dual layer sync and rollback using an isolated temporary workspace."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create minimal mock project hierarchy
        formulas_dir = os.path.join(tmpdir, "app", "config", "content", "formulas")
        os.makedirs(formulas_dir, exist_ok=True)
        reg_path = os.path.join(tmpdir, "app", "config", "formulas_hash_registry.json")
        with open(reg_path, "w") as f:
            json.dump({}, f)
        latex_idx_path = os.path.join(tmpdir, "app", "config", "formulas_latex_index.json")
        with open(latex_idx_path, "w") as f:
            json.dump({}, f)

        pipeline = FormulaIngestionPipeline(project_root=tmpdir, sync_db=False, rebuild_graph=False)

        test_data = {
            "title": "Mock Gravitational Force",
            "equation": "F = G m_1 m_2 / r^2",
            "conceptual_definition": "Newton's law of universal gravitation."
        }
        res = pipeline.ingest(test_data)
        assert res["success"] is True
        assert res["hash_registry_updated"] is True

        # Verify shard was written and hash registry updated
        shard_path = res["shard_path"]
        assert os.path.exists(shard_path)
        with open(reg_path, "r") as f:
            reg = json.load(f)
        rel_shard = os.path.relpath(shard_path, tmpdir)
        assert rel_shard in reg

        # Verify rollback on simulated failure
        class FailingPipeline(FormulaIngestionPipeline):
            def _sync_database_formula(self, formula_data):
                raise RuntimeError("Simulated Database Crash")

        failing_pipe = FailingPipeline(project_root=tmpdir, sync_db=True, rebuild_graph=False)
        fail_data = {
            "title": "Failing Formula",
            "equation": "x = y"
        }
        with pytest.raises(RuntimeError, match="rolled back"):
            failing_pipe.ingest(fail_data)
