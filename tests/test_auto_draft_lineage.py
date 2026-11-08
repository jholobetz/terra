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


def test_corrupted_equation_and_zero_affinity_detection_in_memory():
    """
    Red-team in-memory test verifying that:
      1. Corrupted equation strings (prose bleed, raw MathML, truncated commands) are flagged and capped at RED.
      2. Zero-affinity parent-child links (0 shared math symbols, subtopics, or concept keywords) are flagged and demoted out of GREEN.
    """
    from scripts.maintenance.audit_lineage_health import audit_all, is_corrupted_equation

    assert is_corrupted_equation("approaches the speed of light", "Speed Limit")[0] is True
    assert is_corrupted_equation('math xmlns="http://www.w3.org/1998/Math/MathML"', "Freq")[0] is True
    assert is_corrupted_equation(r"p = \frac{ tial L}{ tial v}", "Momentum")[0] is True
    assert is_corrupted_equation(r"E = mc^2", "Mass-Energy Equivalence")[0] is False

    mock_formulas = {
        "unrelated-parent": {
            "title": "Ideal Gas Law",
            "equation": r"P V = n R T",
            "parent_formula_id": None,
            "derivation_type": "EMPIRICAL_LAW",
            "subcomponents": ["zero-affinity-child", "corrupted-child"],
            "symmetry_origin": "Spatial homogeneity and isotropy of thermal equilibrium.",
            "limits_and_boundary": "Valid in the dilute gas limit at low density.",
            "semantic_variables": {"P": "Pressure", "V": "Volume", "T": "Temperature"},
        },
        "zero-affinity-child": {
            "title": "Femto Metric Prefix Multiplier",
            "equation": r"10^{-15}",
            "parent_formula_id": "unrelated-parent",
            "derivation_type": "DERIVED_FROM",
            "subcomponents": [],
            "symmetry_origin": "Decimal scaling convention in SI metrology.",
            "limits_and_boundary": "Exact constant multiplier across all regimes.",
            "semantic_variables": {"10^{-15}": "Femto factor"},
        },
        "corrupted-child": {
            "title": "Corrupted Prose Bleed Formula",
            "equation": "approaches zero as the density decreases in the outer envelope",
            "parent_formula_id": "unrelated-parent",
            "derivation_type": "DERIVED_FROM",
            "subcomponents": [],
            "symmetry_origin": "Spatial homogeneity and isotropy of thermal equilibrium.",
            "limits_and_boundary": "Valid in the dilute gas limit at low density.",
            "semantic_variables": {"P": "Pressure"},
        },
    }

    results = audit_all(mock_formulas)
    assert results["zero-affinity-child"]["has_parent_affinity"] is False
    assert results["zero-affinity-child"]["tier"] != "GREEN"
    assert results["corrupted-child"]["is_corrupted_equation"] is True
    assert results["corrupted-child"]["tier"] == "RED"


def test_sitewide_zero_corrupted_equations_and_affinity():
    """Verifies that all formula shards have 0 corrupted equations and 0 zero-affinity parent-child links."""
    from scripts.maintenance.audit_lineage_health import load_all_formulas, audit_all

    formulas, _ = load_all_formulas()
    results = audit_all(formulas)
    corrupted = [fid for fid, r in results.items() if r.get("is_corrupted_equation")]
    zero_aff = [fid for fid, r in results.items() if r.get("parent_id") and not r.get("has_parent_affinity", True)]

    assert corrupted == [], f"Found corrupted formula equations: {corrupted[:10]}"
    assert zero_aff == [], f"Found zero-affinity parent-child links: {zero_aff[:10]}"

    # Also verify 0 desynchronized semantic_variables and 0 duplicated boilerplate prose >15 across shards
    from collections import Counter
    from scripts.maintenance.audit_lineage_health import has_aligned_semantic_variables
    from scripts.build_formula_graph import (
        load_canonical_domains,
        build_ground_truth_domain_map,
        resolve_all_domains,
    )

    desync_sem = [
        fid for fid, f in formulas.items()
        if not has_aligned_semantic_variables(f.get("equation", ""), f.get("semantic_variables"))
    ]
    assert desync_sem == [], f"Found desynchronized/empty semantic_variables: {desync_sem[:10]}"

    for field in ["conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary"]:
        cnt = Counter((f.get(field) or "").strip() for f in formulas.values() if (f.get(field) or "").strip())
        over_15 = [(val[:60], c) for val, c in cnt.most_common(5) if c > 15]
        assert over_15 == [], f"Field {field} has copy-pasted boilerplate duplicated >15 times: {over_15}"

    categories = load_canonical_domains()
    f2d, s2d = build_ground_truth_domain_map(categories)
    resolved_domains = resolve_all_domains(formulas, f2d, s2d)
    unmapped = [fid for fid, dom in resolved_domains.items() if dom == "unmapped"]
    assert unmapped == [], f"Found unmapped domain orphans: {unmapped[:10]}"


def test_boilerplate_and_semantic_variables_gate_in_memory():
    """Verifies that copy-pasted boilerplate and misaligned semantic_variables receive 0 quality points."""
    from scripts.maintenance.audit_lineage_health import audit_all

    mock_formulas = {
        "boilerplate-node": {
            "title": "Boilerplate Test Formula",
            "equation": "F = m a",
            "parent_formula_id": None,
            "derivation_type": "AXIOMATIC_FOUNDATION",
            "subcomponents": [],
            "symmetry_origin": "Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance.",
            "limits_and_boundary": "Subject to asymptotic boundary conditions and non-relativistic conservation limits.",
            "semantic_variables": {"\\xi": "Unrelated variable not in equation"},
        }
    }
    res = audit_all(mock_formulas)
    assert res["boilerplate-node"]["quality_score"] == 0



