"""
tests/test_derivation_steps.py

Validates the schema, syntax, delimiter integrity, and step ordering
of Step-by-Step Derivation Accordions across the 256 formula shards.
"""

import glob
import json
import os
import pytest
from jsonschema import Draft7Validator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formula.schema.json")


def load_formula_schema():
    assert os.path.exists(SCHEMA_PATH), f"Missing schema at {SCHEMA_PATH}"
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_shards():
    shards = glob.glob(os.path.join(FORMULAS_DIR, "*", "*.json"))
    shards.extend(glob.glob(os.path.join(FORMULAS_DIR, "*.json")))
    return shards


def test_schema_defines_derivation_steps():
    """Verify that formula.schema.json specifies derivation_steps and derivation_type."""
    schema = load_formula_schema()
    props = schema.get("additionalProperties", {}).get("properties", {})
    assert "derivation_steps" in props, "formula.schema.json must define derivation_steps"
    assert "derivation_type" in props, "formula.schema.json must define derivation_type"
    
    steps_schema = props["derivation_steps"]
    assert steps_schema.get("type") == "array"
    assert steps_schema.get("items", {}).get("required") == ["step", "latex", "rationale"]


def test_canonical_formulas_have_derivation_steps():
    """Verify that canonical seed formulas have multi-step derivations."""
    canonical_ids = [
        "euler-lagrange-equations-dcda7a85",
        "time-independent-schrodinger-53ae29ae",
        "relativistic-energy-momentum-invariant-f61a9ff1",
        "schwarzschild-metric",
        "wave-equation-physics-816dc899",
        "local-energy-conservation-in-electromagnetism-7fd769fd",
        "dirac-equation-relativistic",
        "algebraic-uncertainty-bound-9e7e0df3",
        "plancks-law",
        "carnot-efficiency-factor-47f8b746",
        "expansion-clock-26a3aced",
        "exact-gravitational-redshift-factor-schwarzschild-5a0de121",
        "hamiltons-equations",
        "virial-theorem",
        "snells-law-of-refraction-74d97afe",
        "larmor-formula-aa594928",
        "relativistic-sum-5e65d748",
        "relativistic-doppler-factor-receding-source-f059487f",
        "de-broglie-relation-8bbf6275",
        "photoelectric-equation-einstein-identity-1-3be3f842-00b8e623",
        "bernoulli-constant-standard-form-ff90fb4b",
        "jeans-mass-critical-threshold-21a223b3",
        "chandrasekhar-limit-88f98df2-31bbfff0-c5efb2d1",
        "stefan-boltzmann-law",
        "total-field-56c1f6d7",
        "matrix-math-8b8a3af3",
        "unified-wave-3e179f6c",
        "technical-relation-02b01ceb",
        "free-waves-2fc9d212",
        "fermi-golden-rule-interaction-024fbf64",
        "maxwell-boltzmann-speed-distribution",
        "dimensional-reduction-42f3bbfb",
        "recombination-era-identity-1-f2d0deec-439586e5",
        "geodesic-equation-in-general-relativity-e9a37d9e",
        "relativistic-edge-6bd78c24",
        "geometric-bending-32fd3f54",
        "noether-rule-58a13a95",
        "higgs-kibble-mechanism-identity-1-246b2a79-548a3047",
        "classical-yukawa-potential-pole-7e982f85",
        "yang-mills-curvature-general-3f6b1546",
        "debye-specific-heat-90ea8693",
        "london-equation-8bf340c8",
        "superconducting-gap-equation-ident-4f2aa7e5",
        "hall-conductivity-quantization-law-5524fc65",
        "navier-stokes-momentum-viscous-form-7b93eee6",
        "tov-equation-identity-1-6e8eb3b1-43637a35",
        "hawking-temperature-schwarzschild",
        "friedmann-acceleration-equation-expansion-4aa65f2c"
    ]
    found = {}
    for shard in get_all_shards():
        with open(shard, "r", encoding="utf-8") as f:
            data = json.load(f)
        for cid in canonical_ids:
            if cid in data:
                found[cid] = data[cid]

    for cid in canonical_ids:
        assert cid in found, f"Canonical formula {cid} not found in shards"
        f_data = found[cid]
        assert "derivation_steps" in f_data, f"{cid} missing derivation_steps"
        steps = f_data["derivation_steps"]
        assert isinstance(steps, list), f"{cid} derivation_steps must be a list"
        assert len(steps) >= 4, f"{cid} expected >= 4 derivation steps, found {len(steps)}"

        for i, s in enumerate(steps):
            assert s["step"] == i + 1, f"{cid} step numbers must be sequential (expected {i+1}, got {s['step']})"
            assert isinstance(s["latex"], str) and len(s["latex"].strip()) > 0, f"{cid} step {i+1} empty latex"
            assert isinstance(s["rationale"], str) and len(s["rationale"].strip()) > 10, f"{cid} step {i+1} empty rationale"


def test_all_derivation_steps_schema_and_tex_integrity():
    """Verify that every formula containing derivation_steps obeys strict schema and TeX syntax."""
    schema = load_formula_schema()
    validator = Draft7Validator(schema)

    total_with_steps = 0
    for shard in get_all_shards():
        with open(shard, "r", encoding="utf-8") as f:
            data = json.load(f)
        for err in validator.iter_errors(data):
            pytest.fail(f"Schema violation in {os.path.basename(shard)}: {err.message}")

        for fid, f_data in data.items():
            if isinstance(f_data, dict) and "derivation_steps" in f_data:
                steps = f_data["derivation_steps"]
                if steps:
                    total_with_steps += 1
                    for st in steps:
                        # Check balanced braces in LaTeX
                        latex = st["latex"]
                        open_braces = latex.count("{") - latex.count("\\{")
                        close_braces = latex.count("}") - latex.count("\\}")
                        assert open_braces == close_braces, f"Unbalanced braces in {fid} step {st.get('step')}: {latex}"

                        # Check balanced dollar delimiters in rationale
                        rat = st["rationale"]
                        unescaped_dollars = rat.count("$") - rat.count("\\$")
                        assert unescaped_dollars % 2 == 0, f"Unbalanced math dollar delimiters in {fid} rationale: {rat}"

    assert total_with_steps >= 48, f"Expected at least 48 formulas with derivation steps, found {total_with_steps}"
