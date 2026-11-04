import os
import pytest
from scripts.maintenance.lineage_resolver import discover_lineage, CORE_AXIOMATIC_PARENTS

def test_lineage_resolver_core_axioms():
    assert len(CORE_AXIOMATIC_PARENTS) >= 10

def test_lineage_resolver_greens_function():
    res = discover_lineage(
        title="Position-Space Green Function",
        equation=r"\nabla^2 G = -\delta^3(r-r')",
        conceptual_definition="Fundamental solution to Poisson operator.",
        interpretation="Defines the impulse response of the Laplacian."
    )
    assert res is not None
    assert "parent_formula_id" in res
    assert res["lhi_score"] >= 80
    assert len(res["subcomponents"]) >= 1

def test_lineage_resolver_lorentz_time():
    res = discover_lineage(
        title="Relativistic Time Transformation",
        equation=r"t = \gamma (t - vx / c^2)",
        conceptual_definition="Lorentz boost relation mixing spatial coordinates and elapsed time.",
        interpretation="Shows observer-dependent simultaneity."
    )
    assert res is not None
    assert "parent_formula_id" in res
    assert res["lhi_score"] >= 80

def test_lineage_resolver_empty_graceful():
    res = discover_lineage(
        title="Hypothetical Uncorrelated Scalar",
        equation=r"\xi = 42",
        conceptual_definition="",
        interpretation=""
    )
    assert res is not None
    assert "parent_formula_id" in res
    assert "subcomponents" in res
    assert isinstance(res["lhi_score"], (int, float))


def test_anti_goodhart_lhi_safeguards_in_memory():
    """
    Red-team in-memory test verifying that:
      1. A star-hub packed with > 25 children is flagged as is_overloaded_hub and demoted out of GREEN.
      2. Children stuffed onto an overloaded hub are also demoted out of GREEN.
      3. A standalone DEFINITION root (0 parents, 0 children) is honored as a valid root rather than penalized as Isolated (0).
    """
    from scripts.maintenance.audit_lineage_health import audit_all

    child_ids = [f"child-{i}" for i in range(26)]
    mock_formulas = {
        "mega-hub": {
            "title": "Synthetic Catch-All Hub",
            "equation": r"\hat{H}\psi = E\psi",
            "parent_formula_id": None,
            "derivation_type": "AXIOMATIC_FOUNDATION",
            "subcomponents": child_ids,
            "symmetry_origin": "Time translation invariance under unitary evolution.",
            "limits_and_boundary": "Reduces to classical Hamilton-Jacobi in the semiclassical limit.",
            "semantic_variables": {"H": "Hamiltonian", "psi": "Wavefunction"},
        },
        "honest-definition-root": {
            "title": "Bravais Lattice Vector Definition",
            "equation": r"\mathbf{R} = n_1 \mathbf{a}_1 + n_2 \mathbf{a}_2 + n_3 \mathbf{a}_3",
            "parent_formula_id": None,
            "derivation_type": "DEFINITION",
            "subcomponents": [],
            "symmetry_origin": "Discrete translational symmetry of the crystal lattice.",
            "limits_and_boundary": "Continuum limit achieved as lattice spacing approaches zero.",
            "semantic_variables": {"R": "Lattice vector", "a_1": "Primitive vector"},
        },
    }
    for cid in child_ids:
        mock_formulas[cid] = {
            "title": f"Synthetic Child {cid}",
            "equation": rf"E_{{{cid}}} = \hbar \omega_{{{cid}}}",
            "parent_formula_id": "mega-hub",
            "derivation_type": "DERIVED_FROM",
            "subcomponents": [],
            "symmetry_origin": "Time translation invariance.",
            "limits_and_boundary": "High frequency limit.",
            "semantic_variables": {"E": "Energy", "omega": "Frequency"},
        }

    results = audit_all(mock_formulas)

    # 1. Overloaded hub (>25 children) must be flagged and penalized out of GREEN
    hub_res = results["mega-hub"]
    assert hub_res["is_overloaded_hub"] is True
    assert hub_res["tier"] != "GREEN"
    assert hub_res["score"] < 75

    # 2. Children hanging off an overloaded hub must also be penalized out of GREEN
    child_res = results["child-0"]
    assert child_res["tier"] != "GREEN"
    assert child_res["score"] < 75

    # 3. Honest standalone DEFINITION root must NOT be penalized as Isolated (0)
    def_res = results["honest-definition-root"]
    assert def_res["is_axiom"] is True
    assert def_res["tier"] == "GREEN"
    assert def_res["score"] >= 75

