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
