"""
🔬 Terra Physics Lab - Unit & Integration Tests for Derivation Invariance Prover
Verifies symbolic parent-child reductions, intermediate proof step audits,
and batch derivation scorecard metrics across the 102 multi-step proofs.
"""

import pytest
pytest.importorskip("sympy")

from lib.cas.derivation_prover import (
    normalize_math_string,
    verify_symbolic_reduction,
    verify_derivation_chain,
    run_derivation_audit
)


def test_normalize_math_string():
    s1 = r"\mathbf{F} = m \mathbf{a}"
    s2 = r"F = m a"
    assert normalize_math_string(s1) == normalize_math_string(s2)

    s3 = r"\sigma_A \sigma_B \ge \frac{1}{2} |\langle [A, B] \rangle|"
    s4 = r"\sigma_A\sigma_B \ge \frac{1}{2}|\langle [A, B]\rangle|"
    assert normalize_math_string(s3) == normalize_math_string(s4)


def test_symbolic_reduction_relativistic_momentum_limit():
    # As c -> oo, relativistic momentum p = mv / sqrt(1 - v^2/c^2) -> mv
    res = verify_symbolic_reduction(
        parent_latex=r"p = \frac{m v}{\sqrt{1 - \frac{v^2}{c^2}}}",
        child_latex=r"p = m v",
        limit_var="c",
        limit_target="oo"
    )
    assert res["success"] is True
    assert res["is_equivalent"] is True
    assert res["difference"] == "0"


def test_symbolic_reduction_lorentz_factor_limit():
    # As v -> 0, gamma = 1 / sqrt(1 - v^2/c^2) -> 1
    res = verify_symbolic_reduction(
        parent_latex=r"\gamma = \frac{1}{\sqrt{1 - \frac{v^2}{c^2}}}",
        child_latex=r"\gamma = 1",
        limit_var="v",
        limit_target=0
    )
    assert res["success"] is True
    assert res["is_equivalent"] is True
    assert res["difference"] == "0"


def test_symbolic_reduction_direct_algebraic_identity():
    # Direct algebraic equivalence test without limits
    res = verify_symbolic_reduction(
        parent_latex=r"E = \frac{p^2}{2m}",
        child_latex=r"E = 0.5 \frac{p^2}{m}"
    )
    assert res["success"] is True
    assert res["is_equivalent"] is True


def test_verify_derivation_chain_synthetic():
    entry = {
        "title": "Synthetic Step Proof Test",
        "equation": "E_k = \\frac{1}{2} m v^2",
        "derivation_type": "DERIVED_FROM",
        "parent_formula_id": "work-energy-theorem",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "W = \\int F dx",
                "rationale": "Definition of mechanical work done along displacement dx."
            },
            {
                "step": 2,
                "latex": "F = m \\frac{dv}{dt}",
                "rationale": "Newton's second law for constant mass."
            },
            {
                "step": 3,
                "latex": "W = \\int m \\frac{dv}{dt} dx = \\int m v dv",
                "rationale": "Change of integration variable using v = dx/dt."
            },
            {
                "step": 4,
                "latex": "W = \\frac{1}{2} m v^2",
                "rationale": "Evaluate definite integral from rest to velocity v."
            },
            {
                "step": 5,
                "latex": "E_k = \\frac{1}{2} m v^2",
                "rationale": "Equate accumulated kinetic energy to net work done."
            }
        ]
    }

    res = verify_derivation_chain("synthetic-kinetic-energy", entry)
    assert res["has_proof"] is True
    assert res["total_steps"] == 5
    assert res["is_consecutive"] is True
    assert res["terminates_correctly"] is True
    assert res["is_proof_certified"] is True


def test_run_derivation_audit_full_catalog():
    # Audit all 102 verified proofs sitewide
    summary = run_derivation_audit()
    meta = summary["metadata"]
    assert meta["total_proofs"] == 102
    assert meta["consecutive_count"] == 102  # 100% of proofs must have strictly consecutive step numbering
    assert meta["certified_count"] >= 70    # High confidence baseline certification
    assert meta["terminated_count"] >= 70
    assert meta["elapsed_seconds"] < 5.0    # Sub-5-second execution
    assert len(summary["derivation_type_distribution"]) >= 10
