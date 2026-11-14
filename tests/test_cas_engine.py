"""
Unit tests for the Symbolic CAS Engine (scripts/lib/cas_engine.py).
Verifies parsing, physical asymptotic limits, series expansions, and safety timeouts.
"""

import pytest
pytest.importorskip("sympy")

from scripts.lib.cas_engine import evaluate_symbolic, latex_to_sympy_str


def test_latex_to_sympy_str_conversion():
    # Fractions & roots
    latex = r"\frac{1}{\sqrt{1 - \frac{v^2}{c^2}}}"
    sympy_str = latex_to_sympy_str(latex)
    assert "sqrt" in sympy_str
    assert "v**2" in sympy_str
    assert "c**2" in sympy_str

    # Greek letters
    latex_greek = r"\hbar \omega + \frac{1}{2} k_B T"
    sympy_str_greek = latex_to_sympy_str(latex_greek)
    assert "hbar" in sympy_str_greek
    assert "omega" in sympy_str_greek


def test_symbolic_limit_evaluation():
    # Lorentz factor gamma as v -> 0
    latex = r"\frac{1}{\sqrt{1 - \frac{v^2}{c^2}}}"
    res = evaluate_symbolic(latex, limit_var="v", limit_to="0")
    assert res["success"] is True
    assert res["limit"]["result_latex"] == "1"
    assert "variables" in res
    assert "v" in res["variables"]
    assert "c" in res["variables"]


def test_symbolic_series_expansion():
    # Relativistic kinetic energy expansion as v -> 0: Ek = (gamma - 1) * m * c^2 -> (1/2) * m * v^2
    latex = r"E = (\frac{1}{\sqrt{1 - \frac{v^2}{c^2}}} - 1) m c^2"
    res = evaluate_symbolic(latex, limit_var="v", limit_to="0", series_order=4)
    assert res["success"] is True
    assert res["limit"]["result_latex"] == "0"
    assert "series" in res
    assert r"\frac{m v^{2}}{2}" in res["series"]["leading_terms_latex"]


def test_infinite_limit_c_to_infinity():
    # Relativistic momentum as c -> oo: p = m * v / sqrt(1 - v^2/c^2) -> m * v
    latex = r"p = \frac{m v}{\sqrt{1 - \frac{v^2}{c^2}}}"
    res = evaluate_symbolic(latex, limit_var="c", limit_to="oo")
    assert res["success"] is True
    assert res["limit"]["result_latex"] == "m v"


def test_equation_with_lhs():
    latex = r"F = m a"
    res = evaluate_symbolic(latex)
    assert res["success"] is True
    assert res["lhs"] == "F"
    assert set(res["variables"]) == {"a", "m"}


def test_many_body_hamiltonian_with_sums_and_abs():
    latex = r"\hat{H} = \sum_{i} \frac{\hat{p}_i^2}{2m} + \sum_{i, I} V(\mathbf{r}_i - \mathbf{R}_I) + \frac{1}{2}\sum_{i \neq j} \frac{e^2}{4\pi\epsilon_0 |\mathbf{r}_i - \mathbf{R}_j|}"
    res = evaluate_symbolic(latex, limit_var="e", limit_to="0")
    assert res["success"] is True
    assert "e" in res["variables"]
    assert "m" in res["variables"]
    assert "limit" in res


def test_legendre_transform_sho():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * m * dq^2 - 0.5 * k * q^2",
        coords="q",
        velocities="dq",
        parameters="m, k"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert "m" in res["momenta"][0]["latex"]
    assert "p" in res["inverted_velocities"][0]["latex"]
    assert "p^{2}" in res["hamiltonian_latex"]
    assert len(res["equations_of_motion"]) == 1
    assert "k q" in res["equations_of_motion"][0]["dp_dt_latex"]


def test_legendre_transform_relativistic():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="-m * c^2 * sqrt(1 - dq^2 / c^2) - V",
        coords="q",
        velocities="dq",
        parameters="m, c, V"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert r"\sqrt{c^{2} m^{2} + p^{2}}" in res["hamiltonian_latex"]
    assert "V" in res["hamiltonian_latex"]
    assert "q" in res["conservation"]["cyclic_coordinates"]


def test_legendre_transform_2d_central_force():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * m * (dr^2 + r^2 * dphi^2) - V",
        coords="r, phi",
        velocities="dr, dphi",
        parameters="m, V"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert len(res["momenta"]) == 2
    assert len(res["inverted_velocities"]) == 2
    assert len(res["equations_of_motion"]) == 2
    assert "phi" in res["conservation"]["cyclic_coordinates"]


def test_legendre_transform_singular_constraint():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="m * dx - V",
        coords="x",
        velocities="dx",
        parameters="m, V"
    )
    assert res["success"] is True
    assert res["is_singular"] is True
    assert res["hessian"]["det_latex"] == "0"
    assert "primary Dirac constraints" in res["error"]


def test_legendre_transform_kepler_problem():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * mu * (dr^2 + r^2 * dphi^2) + G * M * mu / r",
        coords="r, phi",
        velocities="dr, dphi",
        parameters="mu, G, M"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert len(res["momenta"]) == 2
    assert "phi" in res["conservation"]["cyclic_coordinates"]
    assert "p_{\\phi}" in res["hamiltonian_latex"] or "p_{phi}" in res["hamiltonian_latex"]


def test_legendre_transform_coriolis_rotating_frame():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * m * (dx^2 + dy^2) + m * omega * (x * dy - y * dx) - 0.5 * k * (x^2 + y^2)",
        coords="x, y",
        velocities="dx, dy",
        parameters="m, omega, k"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert len(res["momenta"]) == 2
    # Check that Hessian determinant is m^2
    assert "m^{2}" in res["hessian"]["det_latex"]
    # Verify non-diagonal velocity coupling leads to momentum cross terms
    assert "omega" in res["hamiltonian_latex"]


def test_legendre_transform_duffing_oscillator():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * m * dq^2 - 0.5 * k * q^2 - 0.25 * beta_param * q^4",
        coords="q",
        velocities="dq",
        parameters="m, k, beta_param"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert "beta_{param}" in res["hamiltonian_latex"]
    assert len(res["equations_of_motion"]) == 1


def test_legendre_transform_spherical_3d():
    from scripts.lib.cas_engine import legendre_transform
    res = legendre_transform(
        lagrangian="0.5 * m * (dr^2 + r^2 * dtheta^2 + r^2 * sin(theta)^2 * dphi^2) - 0.5 * k * r^2",
        coords="r, theta, phi",
        velocities="dr, dtheta, dphi",
        parameters="m, k"
    )
    assert res["success"] is True
    assert res["is_singular"] is False
    assert len(res["momenta"]) == 3
    assert len(res["equations_of_motion"]) == 3
    assert "phi" in res["conservation"]["cyclic_coordinates"]
    assert "sin" in res["hessian"]["det_latex"]


def test_check_dimensions_homogeneous_equation():
    from scripts.lib.cas_engine import check_dimensions
    res = check_dimensions("E = m c^2")
    assert res["success"] is True
    assert res["is_equation"] is True
    assert res["is_homogeneous"] is True
    assert res["lhs"]["dimension_powers"] == {"M": 1, "L": 2, "T": -2}
    assert res["rhs"]["dimension_powers"] == {"M": 1, "L": 2, "T": -2}
    assert "Energy" in res["lhs"]["quantity"]


def test_check_dimensions_expression_and_schwarzschild():
    from scripts.lib.cas_engine import check_dimensions
    res_expr = check_dimensions(r"\frac{G M}{c^2}")
    assert res_expr["success"] is True
    assert res_expr["is_equation"] is False
    assert res_expr["dimension_powers"] == {"L": 1}
    assert "Length" in res_expr["quantity"]

    res_eq = check_dimensions(r"r_s = \frac{2 G M}{c^2}")
    assert res_eq["success"] is True
    assert res_eq["is_homogeneous"] is True


def test_unified_cas_pipeline_and_symbol_inference():
    from lib.cas.cas_engine import (
        latex_to_sympy_str,
        clean_equation_for_cas,
        infer_symbol_dimension,
        check_dimensions,
        evaluate_formula_invariance
    )

    # 1. Nested formatting macros, Greek variants, and \dfrac
    nested = r"\dfrac{\mathrm{d}\mathbf{x}}{\mathrm{d}t} + \varepsilon_0 \varphi"
    parsed = latex_to_sympy_str(nested)
    assert "mathbf" not in parsed
    assert "mathrm" not in parsed
    assert "epsilon_0" in parsed
    assert "phi" in parsed

    # 2. Subscript and differential prefix dimension inference in check_dimensions()
    res_sub = check_dimensions(r"E_k = \frac{1}{2} m_1 v_0^2")
    assert res_sub["success"] is True
    assert res_sub["is_homogeneous"] is True
    assert "Energy" in res_sub["lhs"]["quantity"]

    res_diff = check_dimensions(r"\Delta x \approx v_0 \Delta t")
    assert res_diff["success"] is True
    assert res_diff["is_homogeneous"] is True
    assert "Length" in res_diff["lhs"]["quantity"]

    # 3. Direct formula invariance evaluation from lib.cas.cas_engine
    inv = evaluate_formula_invariance("test-ke", {
        "title": "Kinetic Energy",
        "equation": r"E_k = \frac{1}{2} m v^2"
    })
    assert inv["status"] == "HOMOGENEOUS"
    assert inv["is_homogeneous"] is True
    assert infer_symbol_dimension("Delta_E") is not None
    assert "=" in clean_equation_for_cas(r"p \approx m v")


def test_balanced_brace_deep_nesting_parser():
    from lib.cas.latex_parser import (
        latex_to_sympy_str,
        clean_latex_equation,
        normalize_math_string,
    )
    import scripts.lib.cas_engine as compat_cas
    import lib.cas.cas_engine as core_cas

    # Canonical object identity across lib.cas.latex_parser, lib.cas.cas_engine, and scripts.lib.cas_engine
    assert compat_cas.latex_to_sympy_str is core_cas.latex_to_sympy_str
    assert core_cas.latex_to_sympy_str is latex_to_sympy_str
    assert compat_cas.evaluate_symbolic is core_cas.evaluate_symbolic
    assert compat_cas.check_dimensions is core_cas.check_dimensions

    # 4+ nested brace levels across \sqrt, \frac, subscripts, and nested exponents
    deep_latex = r"\sqrt{1 - \frac{v_{x,0}^{2^{(k)}}}{c^{2}}}"
    res = evaluate_symbolic(deep_latex, limit_var="v_x_0", limit_to="0")
    assert res["success"] is True
    assert res["limit"]["result_latex"] == "1"

    # Cube root \sqrt[3]{...} with nested fraction and decorators
    cube_root = r"r = \sqrt[3]{\frac{G \mathbf{\hat{M}_{0}} T^{2}}{4 \pi^{2}}}"
    res_cube = evaluate_symbolic(cube_root)
    assert res_cube["success"] is True
    assert {"G", "M_0", "T"}.issubset(set(res_cube["variables"]))

    # Deeply nested \frac inside normalize_math_string
    n1 = normalize_math_string(r"\frac{\frac{a_{1}}{b_{1}}}{\frac{c_{1}}{d_{1}}}")
    n2 = normalize_math_string(r"(a_1 / b_1) / (c_1 / d_1)")
    assert n1 == n2

    # Algebraic vs dimensional time-derivative mode separation
    alg = clean_latex_equation(r"T = \frac{1}{2} m \dot{q}^2", mode="algebraic")
    dim = clean_latex_equation(r"T = \frac{1}{2} m \dot{q}^2", mode="dimensional")
    assert "dq" in alg and "/ t" not in alg
    assert "/ t" in dim


def test_evaluate_symbolic_annotations_primes_and_chained_equals():
    # Trailing \quad (\text{...}) annotation should not break algebraic evaluation
    res_ann = evaluate_symbolic(
        r"E_F = \frac{p_F^2}{2m} \quad (\text{Fermi Energy})",
        limit_var="p_F",
        limit_to="0",
    )
    assert res_ann["success"] is True
    assert res_ann["lhs"] == "E_F"
    assert res_ann["limit"]["result_latex"] == "0"

    # Primed coordinates (Lorentz transformation)
    res_prime = evaluate_symbolic(
        r"t' = \gamma \left( t - \frac{v x'}{c^2} \right)",
        limit_var="c",
        limit_to="oo",
    )
    assert res_prime["success"] is True
    assert res_prime["lhs"] == "t_prime"
    assert "x_prime" in res_prime["variables"]

    # Chained equality: LHS symbol paired with terminal explicit RHS expression
    res_chain = evaluate_symbolic(
        r"p = \gamma m v = \frac{m v}{\sqrt{1 - \frac{v^2}{c^2}}}",
        limit_var="c",
        limit_to="oo",
    )
    assert res_chain["success"] is True
    assert res_chain["lhs"] == "p"
    assert res_chain["limit"]["result_latex"] == "m v"


def test_check_dimensions_zero_rhs_and_natural_units_parity():
    from lib.cas.cas_engine import check_dimensions

    # 1. Zero-RHS homogeneous identity (F - m a = 0)
    res_zero = check_dimensions("F - m a = 0")
    assert res_zero["success"] is True
    assert res_zero["is_equation"] is True
    assert res_zero["is_homogeneous"] is True
    assert res_zero["lhs"]["dimension_powers"] == {"M": 1, "L": 1, "T": -2}
    assert res_zero["rhs"]["dimension_powers"] == {"M": 1, "L": 1, "T": -2}

    # 2. Zero-RHS inhomogeneous sum (F - m v = 0) must be rejected
    res_bad_zero = check_dimensions("F - m v = 0")
    assert res_bad_zero["success"] is True
    assert res_bad_zero["is_homogeneous"] is False

    # 3. Natural Units (hbar = c = k_B = 1) relativistic dispersion (E^2 = p^2 + m^2)
    res_nat = check_dimensions("E^2 = p^2 + m^2")
    assert res_nat["success"] is True
    assert res_nat["is_equation"] is True
    assert res_nat["is_homogeneous"] is True
    assert res_nat["framework"] == "natural_units"
    assert res_nat["lhs"]["dimension_powers"] == {"E": 2}

    # 4. Explicit velocity-exponent error (E = m v^3) must never be rescued by c = 1
    res_vel_err = check_dimensions("E = m v^3")
    assert res_vel_err["success"] is True
    assert res_vel_err["is_homogeneous"] is False



