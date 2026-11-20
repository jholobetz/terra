"""
Sandboxed SymPy Expression Parser for Physics Lab CAS.

Eliminates arbitrary Python code execution via sympy.sympify() / parse_expr() by:
1. Pre-validating raw expression strings to reject dunders, attribute access,
   string literals, container literals, statement separators, and Python keywords.
2. Executing parse_expr() with an explicit allowlist global_dict where
   "__builtins__" is set to an empty dict {}.
"""

import re
from typing import Any, Dict, Optional, Tuple

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr as _raw_parse_expr,
    standard_transformations,
)

MAX_SAFE_EXPR_LENGTH = 4096

# Rejects Python container/string/statement/escape/decorator syntax not valid in SymPy math
_FORBIDDEN_SYNTAX_RE = re.compile(r"(__|[\[\]{};:\"'`\\\n\r@~]|\.[A-Za-z_])")

# Rejects Python control-flow & reflection keywords as standalone identifiers
_FORBIDDEN_KEYWORDS_RE = re.compile(
    r"\b(?:import|from|lambda|eval|exec|compile|open|getattr|setattr|delattr|"
    r"globals|locals|vars|builtins|breakpoint|input|type|object|class|def|"
    r"return|yield|raise|try|except|finally|with|for|while|if|else|elif|del|"
    r"assert|pass|async|await|print|help|dir|id|chr|ord|bytes|bytearray|"
    r"memoryview|super|classmethod|staticmethod|property)\b"
)

# Explicit SymPy-only global namespace with __builtins__ completely emptied
SAFE_SYMPY_GLOBALS: Dict[str, Any] = {
    "__builtins__": {},
    # Core SymPy constructors required by parse_expr transformations
    "Symbol": sympy.Symbol,
    "Integer": sympy.Integer,
    "Float": sympy.Float,
    "Rational": sympy.Rational,
    "Number": sympy.Number,
    "Tuple": sympy.Tuple,
    "Pow": sympy.Pow,
    "Add": sympy.Add,
    "Mul": sympy.Mul,
    "Mod": sympy.Mod,
    "Function": sympy.Function,
    "Derivative": sympy.Derivative,
    "Integral": sympy.Integral,
    "Sum": sympy.Sum,
    "Product": sympy.Product,
    "Limit": sympy.Limit,
    "Eq": sympy.Eq,
    "Ne": sympy.Ne,
    "Lt": sympy.Lt,
    "Le": sympy.Le,
    "Gt": sympy.Gt,
    "Ge": sympy.Ge,
    # Constants
    "pi": sympy.pi,
    "E": sympy.E,
    "I": sympy.I,
    "oo": sympy.oo,
    "zoo": sympy.zoo,
    "nan": sympy.nan,
    # Mathematical functions
    "sin": sympy.sin,
    "cos": sympy.cos,
    "tan": sympy.tan,
    "cot": sympy.cot,
    "sec": sympy.sec,
    "csc": sympy.csc,
    "asin": sympy.asin,
    "acos": sympy.acos,
    "atan": sympy.atan,
    "atan2": sympy.atan2,
    "acot": sympy.acot,
    "asec": sympy.asec,
    "acsc": sympy.acsc,
    "sinh": sympy.sinh,
    "cosh": sympy.cosh,
    "tanh": sympy.tanh,
    "coth": sympy.coth,
    "sech": sympy.sech,
    "csch": sympy.csch,
    "asinh": sympy.asinh,
    "acosh": sympy.acosh,
    "atanh": sympy.atanh,
    "exp": sympy.exp,
    "log": sympy.log,
    "ln": sympy.log,
    "sqrt": sympy.sqrt,
    "cbrt": sympy.cbrt,
    "Abs": sympy.Abs,
    "abs": sympy.Abs,
    "sign": sympy.sign,
    "floor": sympy.floor,
    "ceiling": sympy.ceiling,
    "factorial": sympy.factorial,
    "gamma": sympy.gamma,
    "erf": sympy.erf,
    "erfc": sympy.erfc,
    "re": sympy.re,
    "im": sympy.im,
    "conjugate": sympy.conjugate,
    "arg": sympy.arg,
    "Max": sympy.Max,
    "Min": sympy.Min,
    "diff": sympy.diff,
    "Heaviside": sympy.Heaviside,
    "DiracDelta": sympy.DiracDelta,
    "KroneckerDelta": sympy.KroneckerDelta,
    "Piecewise": sympy.Piecewise,
}


# Rejects numeric power towers (e.g. 10**(-10**123), 9**(9**9)) and huge literal integer exponents (> 999)
_POWER_TOWER_RE = re.compile(r"\b\d+\s*\*\*\s*\(?\s*[+-]?\s*\d+\s*\*\*\s*\(?\s*[+-]?\s*\d+")
_HUGE_EXPONENT_RE = re.compile(r"\*\*\s*\(?\s*[+-]?\s*(\d{4,})\s*\)?")


class UnsafeExpressionError(ValueError):
    """Raised when an input string contains forbidden Python syntax or tokens."""


def validate_safe_expr_str(expr_str: str) -> str:
    """Validates that expr_str contains only safe mathematical expression syntax."""
    if not isinstance(expr_str, str):
        raise UnsafeExpressionError("Expression must be a string.")
    if len(expr_str) > MAX_SAFE_EXPR_LENGTH:
        raise UnsafeExpressionError(
            f"Expression exceeds maximum safe length ({MAX_SAFE_EXPR_LENGTH} chars)."
        )
    if _FORBIDDEN_SYNTAX_RE.search(expr_str):
        raise UnsafeExpressionError("Expression contains forbidden syntax.")
    if _FORBIDDEN_KEYWORDS_RE.search(expr_str):
        raise UnsafeExpressionError("Expression contains forbidden keyword.")
    if _POWER_TOWER_RE.search(expr_str):
        raise UnsafeExpressionError("Numeric power tower exceeds safe evaluation bounds.")
    for m in _HUGE_EXPONENT_RE.finditer(expr_str):
        if int(m.group(1)) > 1000:
            raise UnsafeExpressionError("Numeric exponent exceeds safe evaluation bound (1000).")
    return expr_str


def safe_parse_expr(
    expr_str: str,
    local_dict: Optional[Dict[str, Any]] = None,
    transformations: Tuple[Any, ...] = standard_transformations,
) -> Any:
    """
    Sandboxed drop-in replacement for sympy.parsing.sympy_parser.parse_expr().
    """
    clean = validate_safe_expr_str(expr_str)
    # Copy SAFE_SYMPY_GLOBALS so parse_expr cannot mutate the shared dict
    safe_globals = dict(SAFE_SYMPY_GLOBALS)
    safe_locals = dict(local_dict) if local_dict else {}
    return _raw_parse_expr(
        clean,
        local_dict=safe_locals,
        global_dict=safe_globals,
        transformations=transformations,
    )


def safe_sympify_scalar(val: Any) -> Any:
    """
    Sandboxed replacement for sympy.sympify() on limit targets and scalar values.
    """
    if isinstance(val, (int, float, sympy.Basic)):
        return sympy.sympify(val)
    if isinstance(val, str):
        s = val.strip()
        if s.lower() in ("oo", "inf", "infinity", "\\infty"):
            return sympy.oo
        if s.lower() in ("-oo", "-inf", "-infinity", "-\\infty"):
            return -sympy.oo
        return safe_parse_expr(s, local_dict={}, transformations=standard_transformations)
    raise UnsafeExpressionError("Unsupported scalar type for symbolic parsing.")
