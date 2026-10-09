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
from lib.cas.cas_engine import STANDARD_PHYSICS_DIMENSIONS
from scripts.batch_cas_prover import (
    clean_equation_for_cas,
    evaluate_formula_invariance,
    infer_symbol_dimension,
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


def test_expanded_empirical_lexicon_signatures():
    # CGS Force & Energy: dyne -> [M L T^-2], erg -> [M L^2 T^-2]
    assert get_dimension_signature(parse_unit_string("dyn")) == {"M": 1, "L": 1, "T": -2}
    assert get_dimension_signature(parse_unit_string("erg")) == {"M": 1, "L": 2, "T": -2}

    # Astrophysics: Solar Mass -> [M], Lightyear -> [L], Parsec -> [L]
    assert get_dimension_signature(parse_unit_string("M_sun")) == {"M": 1}
    assert get_dimension_signature(parse_unit_string("ly")) == {"L": 1}
    assert get_dimension_signature(parse_unit_string("kpc")) == {"L": 1}

    # Nuclear & Particle: GeV/c^2 -> Mass [M], GeV/c -> Momentum [M L T^-1], barn -> Area [L^2]
    assert get_dimension_signature(parse_unit_string("GeV/c^2")) == {"M": 1}
    assert get_dimension_signature(parse_unit_string("MeV/c")) == {"M": 1, "L": 1, "T": -1}
    assert get_dimension_signature(parse_unit_string("barn")) == {"L": 2}
    assert get_dimension_signature(parse_unit_string("fm")) == {"L": 1}

    # Prefixes & Composites: km, nm, ns, MHz
    assert get_dimension_signature(parse_unit_string("km")) == {"L": 1}
    assert get_dimension_signature(parse_unit_string("nm")) == {"L": 1}
    assert get_dimension_signature(parse_unit_string("ns")) == {"T": 1}
    assert get_dimension_signature(parse_unit_string("GHz")) == {"T": -1}

    # Implicit space multiplication: W m^-2 K^-4 (Stefan-Boltzmann)
    sb_dim = parse_unit_string("W m**-2 K**-4")
    assert get_dimension_signature(sb_dim) == {"M": 1, "T": -3, "Theta": -4}

    # Pure angle & informational dimensionless
    assert parse_unit_string("rad") == 1
    assert parse_unit_string("deg") == 1
    assert parse_unit_string("bit") == 1
    assert parse_unit_string("count") == 1



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


def test_evaluate_formula_invariance_natural_units():
    # Relativistic energy-momentum relation in natural units (c = 1): E^2 = p^2 + m^2
    # In SI, adding p^2 to m^2 fails dimensionally. In Natural Units, [E] = [p] = [m] -> [E]^2.
    entry = {
        "title": "Relativistic Dispersion Relation",
        "equation": "E^2 = p^2 + m^2",
        "semantic_variables": {
            "E": {"unit": "GeV"},
            "p": {"unit": "GeV/c"},
            "m": {"unit": "GeV/c^2"}
        }
    }
    res = evaluate_formula_invariance("dispersion-natural-test", entry)
    assert res["status"] == "HOMOGENEOUS"
    assert res["is_homogeneous"] is True
    assert res["framework"] == "natural_units"
    assert res["natural_power"] == 2
    assert res["lhs_powers"] == {"E": 2}
    assert res["rhs_powers"] == {"E": 2}


def test_infer_symbol_dimension():
    # Subscript stripping: E_F -> Energy [M L^2 T^-2], p_0 -> Momentum [M L T^-1], T_c -> Temperature [Theta]
    dim_e = infer_symbol_dimension("E_F", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_e) == {"M": 1, "L": 2, "T": -2}

    dim_p = infer_symbol_dimension("p_0", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_p) == {"M": 1, "L": 1, "T": -1}

    dim_t = infer_symbol_dimension("T_c", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_t) == {"Theta": 1}

    dim_m = infer_symbol_dimension("m_1", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_m) == {"M": 1}

    # Differential prefix stripping: Delta_S -> Entropy [M L^2 T^-2 Theta^-1], dx -> Length [L]
    dim_ds = infer_symbol_dimension("Delta_S", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_ds) == {"M": 1, "L": 2, "T": -2, "Theta": -1}

    dim_deltax = infer_symbol_dimension("Delta_x", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_deltax) == {"L": 1}

    dim_dt = infer_symbol_dimension("Delta_t", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_dt) == {"T": 1}

    # Fundamental constants
    dim_mu0 = infer_symbol_dimension("mu_0", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_mu0) == {"M": 1, "L": 1, "T": -2, "I": -2}

    dim_eps0 = infer_symbol_dimension("epsilon_0", STANDARD_PHYSICS_DIMENSIONS)
    assert get_dimension_signature(dim_eps0) == {"M": -1, "L": -3, "T": 4, "I": 2}


def test_evaluate_formula_invariance_subscript_inference():
    # Equation where E_F and p_F have NO units provided in semantic_variables
    entry = {
        "title": "Fermi Energy Without Shard Units",
        "equation": r"E_F = \frac{p_F^2}{2 m}",
        "semantic_variables": {
            "m": {"unit": "kg"}
            # E_F and p_F omitted or have null unit
        }
    }
    res = evaluate_formula_invariance("fermi-inference-test", entry)
    assert res["status"] == "HOMOGENEOUS"
    assert res["is_homogeneous"] is True
    assert "Energy" in res["quantity"]
    assert res["lhs_powers"] == {"M": 1, "L": 2, "T": -2}
    assert res["rhs_powers"] == {"M": 1, "L": 2, "T": -2}




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
