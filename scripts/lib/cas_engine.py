#!/usr/bin/env python3
"""
🔬 Terra Physics Lab - Symbolic Computer Algebra System (CAS) Engine
Evaluates physical limits, series expansions, and dimensional consistency
from LaTeX expressions using SymPy with deterministic execution and safety timeouts.
"""

import sys
import json
import re
import signal
from typing import Dict, Any, Optional

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Symbolic evaluation timed out (2.0s hard ceiling).")


def latex_to_sympy_str(latex: str) -> str:
    """
    Sanitizes and converts LaTeX math strings into SymPy-parseable syntax.
    """
    s = latex.strip()
    # Strip delimiters
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)

    # Strip operator sums, products, and integrals (with indices/limits) for CAS algebraic evaluation
    s = re.sub(r"\\(?:sum|prod|int|iint|iiint|oint)(?:_\{[^{}]*\}|_[0-9a-zA-Z])?(?:\^\{[^{}]*\}|\^[0-9a-zA-Z])?", " ", s)

    # Strip formatting macros
    s = re.sub(r"\\(mathbf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|underline)\{([^}]+)\}", r"\2", s)
    s = re.sub(r"\\cssId\{[^}]+\}\{([^}]+)\}", r"\1", s)

    # Fractions: \frac{A}{B} -> ((A)/(B))
    while r"\frac" in s:
        next_s = re.sub(r"\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"((\1)/(\2))", s)
        if next_s == s:
            break
        s = next_s

    # Square roots: \sqrt{A} -> sqrt(A)
    s = re.sub(r"\\sqrt\{((?:[^{}]|\{[^{}]*\})*)\}", r"sqrt(\1)", s)

    # Absolute values: |A| -> (abs(A))
    s = re.sub(r"\|([^|]+)\|", r"(abs(\1))", s)

    # Insert spaces between adjacent TeX control words: e.g. \pi\epsilon -> \pi \epsilon
    s = re.sub(r"\\([a-zA-Z]+)(?=\\)", r"\\\1 ", s)

    # Greek letters and common physical constants (longest first to avoid prefix collisions)
    greeks = [
        "epsilon", "upsilon", "Upsilon", "lambda", "Lambda", "alpha", "gamma", "delta", "theta",
        "kappa", "sigma", "Sigma", "omega", "Omega", "hbar", "beta", "zeta", "iota", "mu", "nu",
        "xi", "Xi", "pi", "Pi", "rho", "tau", "phi", "Phi", "chi", "psi", "Psi", "Gamma", "Delta", "Theta"
    ]
    for g in greeks:
        s = re.sub(r"\\" + g + r"(?![a-zA-Z])", g, s)

    # Subscripts: clean curly braces a_{i} -> a_i
    s = re.sub(r"_\{([^}]+)\}", r"_\1", s)

    # Exponents: ^{...} -> **(...), ^x -> **x
    s = re.sub(r"\^\{([^}]+)\}", r"**(\1)", s)
    s = re.sub(r"\^([0-9a-zA-Z])", r"**\1", s)

    # Multiplication and spacing
    s = re.sub(r"\\cdot|\\times", "*", s)
    s = re.sub(r"\\(left|right|quad|qquad|\,|\;|\!)", " ", s)

    # Clean any remaining LaTeX control sequences (e.g. \neq, \sim, \approx)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)

    # Replace TeX braces with parentheses
    s = s.replace("{", "(").replace("}", ")")
    return s


def build_physics_symbols(sympy_str: str) -> Dict[str, sympy.Symbol]:
    """
    Extracts variable names and defines positive physics symbols.
    """
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", sympy_str)
    reserved = {"sqrt", "sin", "cos", "tan", "exp", "log", "ln", "sinh", "cosh", "tanh", "pi", "E", "I", "O", "abs", "Abs"}
    symbols_dict = {}
    for tok in set(tokens):
        if tok not in reserved:
            symbols_dict[tok] = sympy.Symbol(tok, positive=True)
    return symbols_dict


def evaluate_symbolic(
    latex: str,
    limit_var: Optional[str] = None,
    limit_to: Optional[str] = None,
    series_order: int = 4
) -> Dict[str, Any]:
    """
    Evaluates LaTeX expressions symbolically:
    - Parses expression AST
    - Computes asymptotic limit if requested
    - Computes Taylor series expansion around limit point
    """
    clean_latex = latex.strip()
    # If expression contains '=', evaluate the RHS or difference
    lhs_str = None
    rhs_str = clean_latex
    if "=" in clean_latex:
        parts = clean_latex.split("=", 1)
        lhs_str = parts[0].strip()
        rhs_str = parts[1].strip()

    sympy_str = latex_to_sympy_str(rhs_str)
    symbols_dict = build_physics_symbols(sympy_str)

    try:
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(sympy_str, local_dict=symbols_dict, transformations=transformations)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse mathematical expression: {str(e)}",
            "sympy_str": sympy_str
        }

    result = {
        "success": True,
        "parsed_latex": sympy.latex(expr),
        "variables": sorted([str(s) for s in expr.free_symbols]),
        "lhs": lhs_str
    }

    # Evaluate Limit if requested
    if limit_var and limit_var in symbols_dict:
        var_sym = symbols_dict[limit_var]
        
        # Parse limit target (0, oo, etc.)
        target = 0
        if limit_to in ("oo", "infinity", "\\infty"):
            target = sympy.oo
        elif limit_to is not None:
            try:
                target = sympy.sympify(limit_to)
            except Exception:
                target = 0

        try:
            lim_val = sympy.limit(expr, var_sym, target)
            result["limit"] = {
                "variable": limit_var,
                "target": str(target),
                "result_latex": sympy.latex(lim_val)
            }
        except Exception as e:
            result["limit"] = {
                "variable": limit_var,
                "target": str(target),
                "error": str(e)
            }

        # Series expansion around limit point (if target is 0)
        if target == 0:
            try:
                ser = sympy.series(expr, var_sym, target, series_order)
                ser_no_o = ser.removeO()
                result["series"] = {
                    "variable": limit_var,
                    "order": series_order,
                    "expansion_latex": sympy.latex(ser),
                    "leading_terms_latex": sympy.latex(ser_no_o)
                }
            except Exception as e:
                result["series"] = {"error": str(e)}

    return result


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input payload provided."}))
        sys.exit(1)

    raw_input = sys.argv[1]
    try:
        payload = json.loads(raw_input)
    except Exception:
        payload = {"latex": raw_input}

    latex = payload.get("latex", "")
    limit_var = payload.get("limit_var")
    limit_to = payload.get("limit_to")
    order = payload.get("series_order", 4)

    # Set 2.0s alarm timeout if supported on OS
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)

    try:
        res = evaluate_symbolic(latex, limit_var=limit_var, limit_to=limit_to, series_order=order)
        print(json.dumps(res))
    except TimeoutException as te:
        print(json.dumps({"success": False, "error": str(te)}))
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


if __name__ == "__main__":
    main()
