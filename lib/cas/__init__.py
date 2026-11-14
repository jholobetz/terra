"""
🪐 Project Terra - Symbolic CAS Engine
Provides deterministic SymPy evaluation, asymptotic limit checks, and series expansion.
"""

from .latex_parser import (
    latex_to_sympy_str,
    clean_latex_equation,
    clean_equation_for_cas,
    normalize_math_string,
)
from .cas_engine import (
    evaluate_symbolic,
    legendre_transform,
    check_dimensions,
    evaluate_formula_invariance,
    TimeoutException,
)

__all__ = [
    "evaluate_symbolic",
    "legendre_transform",
    "check_dimensions",
    "evaluate_formula_invariance",
    "latex_to_sympy_str",
    "clean_latex_equation",
    "clean_equation_for_cas",
    "normalize_math_string",
    "TimeoutException",
]
