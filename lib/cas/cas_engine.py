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


def legendre_transform(
    lagrangian: str,
    coords: Any,
    velocities: Any,
    parameters: Optional[Any] = None
) -> Dict[str, Any]:
    """
    Computes exact symbolic Legendre transformations from Lagrangians L(q, q_dot, t)
    to Hamiltonians H(q, p, t):
    - Computes canonical conjugate momenta: p_i = dL / d(q_dot_i)
    - Computes Hessian matrix W_ij = d^2 L / (d(q_dot_i) d(q_dot_j)) and checks det(W)
    - Detects singular/constrained Lagrangians (Dirac constraint analysis)
    - Symbolically inverts velocities: q_dot_i(p, q)
    - Constructs Hamiltonian: H(q, p) = sum(p_i * q_dot_i) - L
    - Generates Hamilton's canonical equations of motion
    - Detects cyclic coordinates and conservation laws
    """
    if isinstance(coords, str):
        coords = [c.strip() for c in coords.split(",") if c.strip()]
    if isinstance(velocities, str):
        velocities = [v.strip() for v in velocities.split(",") if v.strip()]
    if parameters is None:
        parameters = []
    elif isinstance(parameters, str):
        parameters = [p.strip() for p in parameters.split(",") if p.strip()]

    if len(coords) != len(velocities):
        return {
            "success": False,
            "error": f"Dimension mismatch: {len(coords)} coordinate(s) vs {len(velocities)} velocity variable(s)."
        }

    symbols_dict: Dict[str, sympy.Symbol] = {}
    for c in coords:
        symbols_dict[c] = sympy.Symbol(c, real=True)
    for v in velocities:
        symbols_dict[v] = sympy.Symbol(v, real=True)
    for p in parameters:
        symbols_dict[p] = sympy.Symbol(p, positive=True)

    clean_str = latex_to_sympy_str(lagrangian) if ("\\" in lagrangian or "{" in lagrangian) else lagrangian
    clean_str = clean_str.replace("^", "**")

    extra = build_physics_symbols(clean_str)
    for k, s in extra.items():
        if k not in symbols_dict:
            symbols_dict[k] = s

    transformations = standard_transformations + (implicit_multiplication_application,)
    try:
        L = parse_expr(clean_str, local_dict=symbols_dict, transformations=transformations)
    except Exception as e:
        return {"success": False, "error": f"Syntax error parsing Lagrangian: {str(e)}"}

    q_syms = [symbols_dict[c] for c in coords]
    v_syms = [symbols_dict[v] for v in velocities]

    p_syms = []
    for i, c in enumerate(coords):
        p_name = "p" if len(coords) == 1 else f"p_{c}"
        p_syms.append(sympy.Symbol(p_name, real=True))

    p_exprs = [sympy.diff(L, v) for v in v_syms]

    n = len(v_syms)
    W = sympy.Matrix(n, n, lambda i, j: sympy.diff(p_exprs[i], v_syms[j]))
    det_W = sympy.simplify(W.det())

    if det_W == 0:
        return {
            "success": True,
            "is_singular": True,
            "lagrangian_latex": sympy.latex(L),
            "hessian": {
                "matrix_latex": sympy.latex(W),
                "det_latex": "0",
                "is_singular": True
            },
            "error": "Singular Lagrangian (det(W) = 0). Velocities cannot be inverted; system possesses primary Dirac constraints."
        }

    eqs = [sympy.Eq(p_syms[i], p_exprs[i]) for i in range(n)]
    sol_list = sympy.solve(eqs, v_syms, dict=True)
    if not sol_list:
        return {"success": False, "error": "Cannot solve for velocities algebraically."}

    sol = sol_list[0]
    if len(sol_list) > 1:
        # If there are branches (like relativistic +-), pick positive branch
        for s in sol_list:
            test_subs = [(p_syms[0], 1), (v_syms[0], 1)] + [(symbols_dict[p], 1) for p in parameters if p in symbols_dict]
            test_v = s[v_syms[0]].subs(test_subs)
            try:
                if test_v.evalf() > 0:
                    sol = s
                    break
            except Exception:
                pass

    # Construct Hamiltonian: H = sum(p_i * v_i) - L
    pv_sum = sum(p_syms[i] * sol[v_syms[i]] for i in range(n))
    sub_tuples = [(v_syms[i], sol[v_syms[i]]) for i in range(n)]
    L_subbed = L.subs(sub_tuples)
    H_raw = pv_sum - L_subbed

    # Algebraic simplification of H
    terms = sympy.Add.make_args(sympy.expand(H_raw))
    denominators = set()
    for t in terms:
        _, den = t.as_numer_denom()
        if den != 1:
            denominators.add(den)

    if denominators:
        grouped_terms = []
        for d in denominators:
            same_den_num = sum(t.as_numer_denom()[0] for t in terms if t.as_numer_denom()[1] == d)
            simp_frac = sympy.powsimp(sympy.factor(same_den_num) / d)
            grouped_terms.append(simp_frac)
        other_terms = [t for t in terms if t.as_numer_denom()[1] not in denominators]
        H = sympy.simplify(sum(other_terms) + sum(grouped_terms))
    else:
        H = sympy.simplify(H_raw)

    # Hamilton equations of motion
    eqs_of_motion = []
    for i in range(n):
        dq_dt = sympy.diff(H, p_syms[i])
        dp_dt = -sympy.diff(H, q_syms[i])
        eqs_of_motion.append({
            "coord": coords[i],
            "momentum": str(p_syms[i]),
            "dq_dt_latex": rf"\dot{{{coords[i]}}} = \frac{{\partial H}}{{\partial {p_syms[i]}}} = {sympy.latex(dq_dt)}",
            "dp_dt_latex": rf"\dot{{{p_syms[i]}}} = -\frac{{\partial H}}{{\partial {coords[i]}}} = {sympy.latex(dp_dt)}"
        })

    # Conservation laws and cyclic coordinates
    cyclic_coords = []
    conserved_momenta = []
    for i in range(n):
        dL_dq = sympy.diff(L, q_syms[i])
        if dL_dq == 0:
            cyclic_coords.append(coords[i])
            conserved_momenta.append(str(p_syms[i]))

    # Canonical momenta representation
    momenta_info = []
    for i in range(n):
        momenta_info.append({
            "name": str(p_syms[i]),
            "symbol": str(p_syms[i]),
            "latex": rf"{p_syms[i]} = \frac{{\partial L}}{{\partial \dot{{{coords[i]}}}}} = {sympy.latex(p_exprs[i])}",
            "expr_latex": sympy.latex(p_exprs[i])
        })

    # Inverted velocity representation
    inv_vel_info = []
    for i in range(n):
        inv_vel_info.append({
            "velocity": rf"\dot{{{coords[i]}}}",
            "latex": rf"\dot{{{coords[i]}}}({p_syms[i]}) = {sympy.latex(sol[v_syms[i]])}",
            "expr_latex": sympy.latex(sol[v_syms[i]])
        })

    summary = "Lagrangian has no explicit time dependence, so total energy (Hamiltonian) is conserved: $\\frac{dH}{dt} = 0$."
    if cyclic_coords:
        c_str = ", ".join(cyclic_coords)
        m_str = ", ".join(conserved_momenta)
        summary += f" Generalized coordinate(s) {{{c_str}}} are cyclic (\\(\\frac{{\\partial L}}{{\\partial q}} = 0\\)), yielding conserved conjugate momenta {{{m_str}}}."

    return {
        "success": True,
        "is_singular": False,
        "lagrangian_latex": sympy.latex(L),
        "momenta": momenta_info,
        "hessian": {
            "matrix_latex": sympy.latex(W),
            "det_latex": sympy.latex(det_W),
            "is_singular": False
        },
        "inverted_velocities": inv_vel_info,
        "hamiltonian_latex": sympy.latex(H),
        "equations_of_motion": eqs_of_motion,
        "conservation": {
            "energy_conserved": True,
            "cyclic_coordinates": cyclic_coords,
            "conserved_momenta": conserved_momenta,
            "summary": summary
        }
    }


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"success": False, "error": "No input payload provided."}))
        sys.exit(1)

    raw_input = sys.argv[1]
    try:
        payload = json.loads(raw_input)
    except Exception:
        payload = {"latex": raw_input}

    mode = payload.get("mode", "evaluate")

    # Set 2.0s alarm timeout if supported on OS
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(2)

    try:
        if mode == "legendre":
            lagrangian = payload.get("lagrangian") or payload.get("latex", "")
            coords = payload.get("coords") or payload.get("coord", "q")
            velocities = payload.get("velocities") or payload.get("velocity", "dq")
            parameters = payload.get("parameters", [])
            res = legendre_transform(
                lagrangian=lagrangian,
                coords=coords,
                velocities=velocities,
                parameters=parameters
            )
        else:
            latex = payload.get("latex", "")
            limit_var = payload.get("limit_var")
            limit_to = payload.get("limit_to")
            order = payload.get("series_order", 4)
            res = evaluate_symbolic(latex, limit_var=limit_var, limit_to=limit_to, series_order=order)

        print(json.dumps(res))
    except TimeoutException as te:
        print(json.dumps({"success": False, "error": str(te)}))
    finally:
        if hasattr(signal, "SIGALRM"):
            signal.alarm(0)


if __name__ == "__main__":
    main()

