"""
🔬 Terra Physics Lab - Unit & Integration Tests for Batch CAS Prover & Unit Parser
Verifies empirical SI unit parsing, LaTeX equation sanitization, multi-worker batch
execution, and dimensional homogeneity detection.
"""

import pytest
pytest.importorskip("sympy")

from lib.cas.unit_parser import (
    parse_unit_string,
    sanitize_unit_string,
    get_dimension_signature
)
from scripts.batch_cas_prover import (
    clean_equation_for_cas,
    evaluate_formula_invariance,
    run_batch_prover
)


def test_unit_string_sanitization():
    assert sanitize_unit_string("m/s^2") == "m / s**(2)"
    assert sanitize_unit_string("kg⋅m/s") == "kg * m / s"
    assert sanitize_unit_string("m⁻¹") == "m**(-1)"
    assert sanitize_unit_string("Joules (J)") == "J"
    assert sanitize_unit_string("{m/s}") == "m / s"


def test_unit_string_parsing_signatures():
    # Momentum: [M L T^-1]
    dim = parse_unit_string("kg⋅m/s")
    assert get_dimension_signature(dim) == {"M": 1, "L": 1, "T": -1}

    # Energy: [M L^2 T^-2]
    dim_e = parse_unit_string("J")
    assert get_dimension_signature(dim_e) == {"M": 1, "L": 2, "T": -2}

    # Entropy / Heat Capacity: [M L^2 T^-2 Theta^-1]
    dim_s = parse_unit_string("J/K")
    assert get_dimension_signature(dim_s) == {"M": 1, "L": 2, "T": -2, "Theta": -1}

    # Inverse length: [L^-1]
    dim_k = parse_unit_string("m⁻¹")
    assert get_dimension_signature(dim_k) == {"L": -1}

    # High energy physics unit: GeV -> Energy
    dim_gev = parse_unit_string("GeV")
    assert get_dimension_signature(dim_gev) == {"M": 1, "L": 2, "T": -2}

    # Dimensionless
    assert parse_unit_string("dimensionless") == 1
    assert get_dimension_signature(1) == {}


def test_clean_equation_for_cas():
    # Strip text annotation
    eq1 = r"E_F = \frac{p_F^2}{2m} \quad (\text{Fermi Energy})"
    clean1 = clean_equation_for_cas(eq1)
    assert clean1 == r"E_F = \frac{p_F^2}{2m}"

    # Handle conjunction \iff
    eq2 = r"ds^2 = 0 \iff c^2 dt^2 - d\mathbf{x}^2 = 0"
    clean2 = clean_equation_for_cas(eq2)
    assert "iff" not in clean2
    assert "=" in clean2

    # Normalize approximate relation
    eq3 = r"F \approx m a"
    clean3 = clean_equation_for_cas(eq3)
    assert clean3 == "F = m a"


def test_evaluate_formula_invariance_homogeneous():
    entry = {
        "title": "Fermi Energy",
        "equation": r"E_F = \frac{p_F^2}{2m} \quad (\text{Fermi Energy})",
        "semantic_variables": {
            "E_F": {"unit": "J"},
            "p_F": {"unit": "kg⋅m/s"},
            "m": {"unit": "kg"}
        }
    }
    res = evaluate_formula_invariance("fermi-energy-test", entry)
    assert res["status"] == "HOMOGENEOUS"
    assert res["is_homogeneous"] is True
    assert "Energy" in res["quantity"]
    assert res["lhs_powers"] == {"M": 1, "L": 2, "T": -2}
    assert res["rhs_powers"] == {"M": 1, "L": 2, "T": -2}


def test_evaluate_formula_invariance_inhomogeneous():
    # Intentionally false equation: Energy = Momentum
    entry = {
        "title": "Mismatched Dimensions Test",
        "equation": "E = p",
        "semantic_variables": {
            "E": {"unit": "J"},
            "p": {"unit": "kg⋅m/s"}
        }
    }
    res = evaluate_formula_invariance("mismatch-test", entry)
    assert res["status"] == "INHOMOGENEOUS"
    assert res["is_homogeneous"] is False
    assert res["lhs_powers"] != res["rhs_powers"]


def test_evaluate_operator_or_tensor():
    entry = {
        "title": "Quantum Bra-Ket",
        "equation": r"\langle \psi | \hat{H} | \psi \rangle = E"
    }
    res = evaluate_formula_invariance("quantum-bra-ket", entry)
    assert res["status"] == "OPERATOR_OR_TENSOR"
    assert res["is_homogeneous"] is None


def test_run_batch_prover_limited_sample():
    # Run multi-worker prover on a 5-item sample from shard 00
    summary = run_batch_prover(shard_hex="00", limit=5, num_workers=2)
    assert "metadata" in summary
    assert summary["metadata"]["total_audited"] == 5
    assert summary["metadata"]["workers"] == 2
    assert summary["metadata"]["elapsed_seconds"] >= 0
    assert "status_distribution" in summary
