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


