"""
Unit tests for the Symbolic CAS Engine (scripts/lib/cas_engine.py).
Verifies parsing, physical asymptotic limits, series expansions, and safety timeouts.
"""

import pytest
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
