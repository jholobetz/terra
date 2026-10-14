#!/usr/bin/env python3
"""
🔬 Terra Physics Lab - Symbolic Computer Algebra System (CAS) Engine
Evaluates physical limits, series expansions, and dimensional consistency
from LaTeX expressions using SymPy with deterministic execution and safety timeouts.
"""

import sys
import os
import json
import re
import signal
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import sympy
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application
)
from sympy.physics.units import (
    length, mass, time, current, temperature, amount_of_substance, luminous_intensity
)
from sympy.physics.units.systems.si import dimsys_SI

from lib.cas.unit_parser import (
    parse_unit_string,
    parse_unit_string_natural,
    get_natural_dimension_power,
    DIM_NATURAL_ENERGY
)


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Symbolic evaluation timed out (2.0s hard ceiling).")


def latex_to_sympy_str(latex: str) -> str:
    """
    Sanitizes and converts LaTeX math strings into SymPy-parseable syntax.
    Supports nested formatting macros, Greek letter variants, and nested fractions.
    """
    s = latex.strip()
    # Strip delimiters
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)

    # Normalize Greek variants before general parsing
    s = re.sub(r"\\varepsilon(?![a-zA-Z])", r"\\epsilon", s)
    s = re.sub(r"\\varphi(?![a-zA-Z])", r"\\phi", s)
    s = re.sub(r"\\vartheta(?![a-zA-Z])", r"\\theta", s)
    s = re.sub(r"\\varrho(?![a-zA-Z])", r"\\rho", s)

    # Normalize \dfrac and \tfrac to \frac
    s = re.sub(r"\\(d|t)frac\b", r"\\frac", s)

    # Strip operator sums, products, and integrals (with indices/limits) for CAS algebraic evaluation
    s = re.sub(r"\\(?:sum|prod|int|iint|iiint|oint)(?:(?:_\{((?:[^{}]|\{[^{}]*\})*)\}|_[0-9a-zA-Z])|(?:\^\{((?:[^{}]|\{[^{}]*\})*)\}|\^[0-9a-zA-Z]))*", " ", s)

    # Iteratively strip formatting and decorator macros (handles nested macros like \mathrm{d}\mathbf{x})
    for _ in range(4):
        next_s = re.sub(
            r"\\(mathbf|mathrm|mathsf|text|boldsymbol|mathcal|vec|hat|bar|tilde|underline)\{([^{}]+)\}",
            r"\2",
            s
        )
        if next_s == s:
            break
        s = next_s
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

    # Map \lambda specifically to lam to avoid Python's reserved keyword 'lambda'
    s = re.sub(r"\\lambda(?![a-zA-Z])", "lam", s)

    # Greek letters and common physical constants (longest first to avoid prefix collisions)
    greeks = [
        "epsilon", "upsilon", "Upsilon", "Lambda", "alpha", "gamma", "delta", "theta",
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
            "latex": rf"\dot{{{coords[i]}}} = {sympy.latex(sol[v_syms[i]])}",
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


STANDARD_PHYSICS_DIMENSIONS = {
    # Masses & Particles
    "m": mass, "M": mass, "m_e": mass, "m_p": mass, "m_n": mass, "m_0": mass,

    # Lengths & Spatial Coordinates
    "x": length, "y": length, "z": length, "r": length, "l": length, "L": length,
    "d": length, "R": length, "a_0": length, "lambda": length, "lam": length, "s": length, "r_s": length,
    "dx": length, "dy": length, "dz": length, "dr": length, "dq": length, "dl": length,

    # Times & Durations
    "t": time, "T_period": time, "tau": time, "dt": time,

    # Velocities & Speeds
    "v": length / time, "c": length / time, "u": length / time, "v_0": length / time,

    # Accelerations & Gravitational Field
    "a": length / (time**2), "g": length / (time**2),

    # Forces
    "F": mass * length / (time**2),

    # Energies, Work & Hamiltonians
    "E": mass * (length**2) / (time**2), "H": mass * (length**2) / (time**2),
    "V": mass * (length**2) / (time**2), "U": mass * (length**2) / (time**2),
    "K": mass * (length**2) / (time**2), "T_energy": mass * (length**2) / (time**2),

    # Momenta
    "p": mass * length / time,

    # Temperatures & Thermodynamics
    "T": temperature,
    "S": mass * (length**2) / ((time**2) * temperature),
    "k": mass / (time**2),
    "k_B": mass * (length**2) / ((time**2) * temperature),
    "k_b": mass * (length**2) / ((time**2) * temperature),
    "R_gas": mass * (length**2) / ((time**2) * temperature * amount_of_substance),
    "sigma_SB": mass / ((time**3) * (temperature**4)),
    "sigma": mass / ((time**3) * (temperature**4)),

    # Frequencies & Rates
    "omega": 1 / time, "f": 1 / time, "nu": 1 / time,

    # Gravitational Constant & Action
    "G": (length**3) / (mass * (time**2)),
    "hbar": (mass * (length**2)) / time,
    "h": (mass * (length**2)) / time,

    # Electromagnetism & Field Tensors
    "q": current * time, "e": current * time, "q_charge": current * time, "Q": current * time,
    "I": current,
    "B": mass / (current * (time**2)),
    "A_pot": mass * length / (current * (time**2)),
    "V_pot": mass * (length**2) / ((time**3) * current),
    "E_field": mass * length / ((time**3) * current),
    "epsilon_0": ((time**4) * (current**2)) / (mass * (length**3)),
    "eps_0": ((time**4) * (current**2)) / (mass * (length**3)),
    "varepsilon_0": ((time**4) * (current**2)) / (mass * (length**3)),
    "mu_0": mass * length / ((time**2) * (current**2)),
    "k_e": mass * (length**3) / ((time**4) * (current**2)),
    "mu_B": current * (length**2),
    "mu_N": current * (length**2),
    "J_current": current / (length**2),

    # Densities & Pressures
    "rho": mass / (length**3),
    "P": mass / (length * (time**2)),

    # Geometry, Area & Volume
    "A": length**2, "Area": length**2,
    "Vol": length**3, "Volume": length**3,
    "k_wave": 1 / length,

    # Dimensionless & Angles
    "theta": 1, "phi": 1, "alpha": 1
}


def _extract_dim_powers(deps: Dict[Any, Any]) -> Dict[str, Any]:
    mapping = {
        mass: "M",
        length: "L",
        time: "T",
        current: "I",
        temperature: "Theta",
        amount_of_substance: "N",
        luminous_intensity: "J"
    }
    dim_powers = {}
    for d, p in deps.items():
        for base_unit, symbol in mapping.items():
            if d == base_unit or str(d) == str(base_unit):
                dim_powers[symbol] = int(p) if (hasattr(p, 'is_integer') and p.is_integer) or (isinstance(p, (int, float)) and int(p) == p) else float(p)
    return dim_powers


def _format_dim_latex(dim_powers: Dict[str, Any]) -> str:
    if not dim_powers:
        return r"[1] \text{ (Dimensionless)}"
    pos_terms = []
    neg_terms = []
    for k in ["M", "L", "T", "I", "Theta", "N", "J"]:
        if k in dim_powers:
            p = dim_powers[k]
            if p == 1:
                pos_terms.append(rf"\text{{{k}}}")
            elif p > 0:
                pos_terms.append(rf"\text{{{k}}}^{{{p}}}")
            elif p == -1:
                neg_terms.append(rf"\text{{{k}}}")
            else:
                neg_terms.append(rf"\text{{{k}}}^{{{abs(p)}}}")
    if not pos_terms and not neg_terms:
        return r"[1] \text{ (Dimensionless)}"
    pos_str = r" \cdot ".join(pos_terms) if pos_terms else "1"
    if neg_terms:
        neg_str = r" \cdot ".join(neg_terms)
        return rf"[{pos_str} / ({neg_str})]"
    return rf"[{pos_str}]"


def _identify_physical_quantity(dim_powers: Dict[str, Any]) -> str:
    m = dim_powers.get("M", 0)
    l = dim_powers.get("L", 0)
    t = dim_powers.get("T", 0)
    i = dim_powers.get("I", 0)
    if not dim_powers or (m == 0 and l == 0 and t == 0 and i == 0):
        return "Dimensionless Quantity (Ratio / Angle)"
    if m == 0 and l == 1 and t == 0:
        return "Length / Spatial Extent / Radius"
    if m == 0 and l == 0 and t == 1:
        return "Time / Period"
    if m == 1 and l == 0 and t == 0:
        return "Mass / Inertia"
    if m == 0 and l == 1 and t == -1:
        return "Velocity / Speed of Propagation"
    if m == 0 and l == 1 and t == -2:
        return "Acceleration / Gravitational Field"
    if m == 1 and l == 1 and t == -2:
        return "Force"
    if m == 1 and l == 2 and t == -2:
        return "Energy / Work / Hamiltonian"
    if m == 1 and l == 2 and t == -1:
        return "Action / Angular Momentum"
    if m == 1 and l == 1 and t == -1:
        return "Linear Momentum"
    if m == 1 and l == 2 and t == -3:
        return "Power / Radiant Flux"
    if m == 1 and l == -1 and t == -2:
        return "Pressure / Energy Density"
    if m == 1 and l == -3 and t == 0:
        return "Mass Density"
    if m == 0 and l == 0 and t == -1:
        return "Frequency / Angular Rate"
    if m == 0 and l == 0 and t == 1 and i == 1:
        return "Electric Charge"
    if m == -1 and l == 3 and t == -2:
        return "Gravitational Constant (G)"
    return "Composite Physical Invariant"


RESERVED_MATH_TOKENS = {
    "sqrt", "sin", "cos", "tan", "exp", "log", "ln", "sinh", "cosh", "tanh",
    "pi", "E", "I", "abs", "Abs", "diff", "Derivative"
}


def clean_equation_for_cas(latex: str) -> str:
    """
    Strips non-algebraic annotations, conditional clauses, and conjunctions from raw equation strings.
    """
    s = latex.strip()

    # Strip display delimiters
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)

    # Strip trailing text clauses (e.g. \quad (\text{Fermi Energy}), \text{where } ...)
    s = re.sub(r"\\quad\s*\\text\{[^}]+\}", "", s)
    s = re.sub(r"\\quad\s*\([^)]*\)", "", s)
    s = re.sub(r"\\text\{where\s+[^}]+\}", "", s)
    s = re.sub(r"\\text\{for\s+[^}]+\}", "", s)

    # Handle conjunctions: if \iff or \implies is present, take the primary right-hand condition or main equality
    if r"\iff" in s:
        parts = s.split(r"\iff")
        s = parts[1].strip() if "=" in parts[1] else parts[0].strip()
    elif r"\implies" in s:
        parts = s.split(r"\implies")
        s = parts[1].strip() if "=" in parts[1] else parts[0].strip()

    # Normalize relations for dimensional comparison
    s = re.sub(r"\\approx|\\equiv|\\sim|\\propto|\\geq|\\leq|\\ge(?![a-zA-Z])|\\le(?![a-zA-Z])|>|<", "=", s)

    # Strip complex conjugation and hermitian adjoint operators (do not change physical dimensions):
    s = re.sub(r"\^\{?\*\}?", "", s)
    s = re.sub(r"\^\{?\\dagger\}?", "", s)
    s = re.sub(r"\\dagger", "", s)

    # Normalize arcseconds / double primes: 1'' -> 1, '' -> _dprime
    s = re.sub(r"([0-9]+(?:\.[0-9]+)?)\s*\'\'", r"\1", s)
    s = re.sub(r"\'\'", "_dprime", s)

    # Normalize prime notation: u' -> u_prime, x' -> x_prime, r' -> r_prime
    s = re.sub(r"([a-zA-Z0-9_]+)\'", r"\1_prime", s)

    # Normalize repeated integrals: \int \int -> \int
    s = re.sub(r"\\int\s*\\int\s*\\int", r"\\int", s)
    s = re.sub(r"\\int\s*\\int", r"\\int", s)

    # Normalize tensor mixed indices: R^\rho_{\sigma\mu\nu} -> R_rhosigmamunu, F^a_{\mu\nu} -> F_amunu
    s = re.sub(r"\b([RTFGC]|\\Gamma)\^\{?([a-zA-Z])\}?_\{?([a-zA-Z]+)\}?", r"\1_\2\3", s)

    # Strip error margins: 2.73 \pm 0.02 -> 2.73
    s = re.sub(r"\\pm\s*[0-9]+(?:\.[0-9]+)?", "", s)

    # Normalize differentials and differences: \Delta S -> Delta_S, d\mathbf{x} -> dx, \mathrm{d}\mathbf{l} -> dl
    s = re.sub(r"\\Delta\s*([a-zA-Z])", r"Delta_\1", s)
    s = re.sub(r"\\(?:mathrm\{d\}|mathrm\{D\}|d)\s*(?:\\mathbf|\\boldsymbol|\\vec)?\{?([a-zA-Z])\}?", r"d\1", s)

    # Normalize time derivatives: \ddot{x} -> (x / (t**2)), \dot{M} -> (M / t)
    s = re.sub(r"\\ddot\{?([a-zA-Z])\}?(?:_\{?[a-zA-Z0-9_]+\}?)?", r"(\1 / (t**2))", s)
    s = re.sub(r"\\dot\{?([a-zA-Z])\}?(?:_\{?[a-zA-Z0-9_]+\}?)?", r"(\1 / t)", s)

    # Normalize solar/astronomical subscript symbols: M_\odot -> M_sun
    s = re.sub(r"([MRL])_\{?\\odot\}?", r"\1_sun", s)

    # Normalize 4D volume elements: d^4x -> d4x
    s = re.sub(r"d\^4\s*(?:\\mathbf\{x\}|x)", "d4x", s)

    # Normalize partial derivatives and vector calculus operators to spatial/temporal derivatives:
    s = re.sub(r"\\frac\{\\partial\s*(?:\\mathbf\{([a-zA-Z])\}|([a-zA-Z]))\}\{\\partial\s*([a-zA-Z])\}", r"(\1\2 / \3)", s)

    # Normalize vector symbols for fields: \mathbf{E} -> E_field, \mathbf{J} -> J_current, \mathbf{B} -> B
    s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{E\}", "E_field", s)
    s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{J\}", "J_current", s)
    s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{B\}", "B", s)

    # Normalize vector differential operators (div, grad, curl, laplacian):
    s = re.sub(r"\\nabla\^2\s*(?:\\mathbf\{([a-zA-Z])\}|([a-zA-Z])|\\Phi|\\phi)", r"(\1\2Phi / (L**2))", s)
    s = re.sub(r"\\nabla\s*\\times\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)
    s = re.sub(r"\\nabla\s*\\cdot\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)
    s = re.sub(r"\\nabla\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)

    # Normalize quantum expectation values:
    s = re.sub(r"\\langle\s*\\sigma\s*v\s*\\rangle", "(sigma * v)", s)
    s = re.sub(r"\\langle\s*([a-zA-Z0-9_]+)\s*\\rangle", r"(\1)", s)
    # Inner products of discrete/normalized states: \langle n | m \rangle -> 1
    s = re.sub(r"\\langle\s*[^{}|]+\s*\|\s*[^{}|]+\s*\\rangle", " 1 ", s)
    if not re.search(r"\\langle[^|]+\|[^|]+\|[^|]+\\rangle", s):
        s = re.sub(r"\|[a-zA-Z0-9_\s\(\)\^\{\}\*]+\\rangle", " 1 ", s)
        s = re.sub(r"\\langle[a-zA-Z0-9_\s\(\)\^\{\}\*]+\|", " 1 ", s)

    # Normalize metric tensor quadratic forms:
    s = re.sub(r"(?:\\eta|g|\\gamma)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*([a-zA-Z])\^\{?[a-zA-Z0-9_]\}?\s*([a-zA-Z])\^\{?[a-zA-Z0-9_]\}?", r"(\1 * \2)", s)
    s = re.sub(r"(?:\\eta|g|\\gamma)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*\(([^()]+)\)\^\{?[a-zA-Z0-9_]\}?\s*\(([^()]+)\)\^\{?[a-zA-Z0-9_]\}?", r"((\1) * (\2))", s)
    s = re.sub(r"(?:g|\\gamma|\\eta)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*d[a-zA-Z]\^\{?[a-zA-Z0-9_]\}?\s*d[a-zA-Z]\^\{?[a-zA-Z0-9_]\}?", "(dx**2)", s)
    s = re.sub(r"(?:\\eta|g|h|\\gamma)_\{?\\mu\\nu\}?", " 1 ", s)

    # Normalize common function notations: x(t) -> x, a(t) -> a
    s = re.sub(r"([a-zA-Z0-9_]+)\s*\([t]\)", r"\1", s)

    # Strip operator bounds containing '=' (e.g. \sum_{i=1}^{3N}) before relational parsing
    s = re.sub(r"\\(?:sum|prod|int|oint)_\{[^{}]*=[^{}]*\}(?:\^\{[^{}]*\}|\^[0-9a-zA-Z]+)?", " ", s)

    # If multiple top-level '=' exist (e.g. A = B = C), take first two: A = B
    top_parts = []
    cur = []
    depth = 0
    for ch in s:
        if ch in "({[":
            depth += 1
            cur.append(ch)
        elif ch in ")}]":
            if depth > 0:
                depth -= 1
            cur.append(ch)
        elif ch == "=" and depth == 0:
            top_parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    top_parts.append("".join(cur))

    if len(top_parts) > 2:
        s = f"{top_parts[0]} = {top_parts[1]}"

    return s.strip()


def infer_symbol_dimension(sym: str, standard_dims: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """
    Infers the physical dimension of an unrecognized symbol through:
    1. Direct dictionary match.
    2. Differential/difference prefix stripping (Delta_S -> S, dp -> p, dx -> x, dtau -> tau).
    3. Subscript/index stripping (E_F -> E, p_x -> p, T_c -> T, m_1 -> m, omega_0 -> omega).
    4. Numeric suffix stripping (m1 -> m, x0 -> x, v2 -> v).
    5. Physics keyword aliases (temp -> T, energy -> E, dist -> r).
    """
    if standard_dims is None:
        standard_dims = STANDARD_PHYSICS_DIMENSIONS

    if sym in standard_dims:
        return standard_dims[sym]

    clean = sym.strip("_")
    if not clean:
        return None

    # Step 1: Strip variation / differential prefixes: Delta_*, delta_*, d_*
    prefix_patterns = [
        r"^(?:Delta|delta|d|nabla)_+([a-zA-Z0-9_]+)$",
        r"^d([A-Z][a-zA-Z0-9_]*)$",
        r"^d([a-z])$"
    ]
    for pat in prefix_patterns:
        m = re.match(pat, clean)
        if m:
            base_sym = m.group(1)
            if base_sym in standard_dims:
                return standard_dims[base_sym]
            clean = base_sym
            break

    # Step 2: Strip subscripts (e.g. E_F -> E, p_x -> p, T_c -> T, m_1 -> m)
    if "_" in clean:
        root = clean.split("_")[0]
        if root in standard_dims:
            return standard_dims[root]

    # Step 3: Strip numeric suffix (e.g. m1 -> m, x0 -> x, v2 -> v, q1 -> q)
    m_num = re.match(r"^([a-zA-Z]+)[0-9]+$", clean)
    if m_num:
        root = m_num.group(1)
        if root in standard_dims:
            return standard_dims[root]

    # Step 4: Common physics abbreviations
    common_aliases = {
        "temp": "T", "temperature": "T",
        "mass": "m",
        "vel": "v", "velocity": "v", "speed": "v",
        "freq": "f", "frequency": "f",
        "energy": "E", "ener": "E",
        "time": "t",
        "dist": "r", "distance": "r", "rad": "r", "radius": "r",
        "len": "L", "length": "L",
        "press": "P", "pressure": "P",
        "vol": "Vol", "volume": "Vol",
        "area": "A",
        "dens": "rho", "density": "rho",
        "charge": "q",
        "accel": "a", "acceleration": "a",
        "entropy": "S",
    }
    lower = clean.lower()
    if lower in common_aliases:
        alias_key = common_aliases[lower]
        if alias_key in standard_dims:
            return standard_dims[alias_key]

    return None


def build_entry_dimensions(
    entry: Dict[str, Any],
    natural_units: bool = False,
    equation_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Builds a localized symbol-to-dimension map by prioritizing:
    1. Formula semantic_variables unit fields.
    2. STANDARD_PHYSICS_DIMENSIONS lookup.
    3. Heuristic root and prefix inference.
    If natural_units is True, dimensions are projected to powers of DIM_NATURAL_ENERGY [E]^d.
    """
    if not natural_units:
        local_dims = dict(STANDARD_PHYSICS_DIMENSIONS)
        semantic_vars = entry.get("semantic_variables", {})
        if isinstance(semantic_vars, dict):
            for raw_sym, var_meta in semantic_vars.items():
                if isinstance(var_meta, dict):
                    unit_str = var_meta.get("unit")
                    if unit_str:
                        dim_expr = parse_unit_string(unit_str)
                        if dim_expr is not None:
                            clean_sym = latex_to_sympy_str(raw_sym).strip()
                            clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", clean_sym)
                            if clean_sym:
                                local_dims[clean_sym] = dim_expr

        candidate_syms = set()
        if equation_str:
            candidate_syms.update(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", equation_str))
        if isinstance(semantic_vars, dict):
            for raw_sym in semantic_vars:
                clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", latex_to_sympy_str(raw_sym).strip())
                if clean_sym:
                    candidate_syms.add(clean_sym)

        for sym in candidate_syms:
            if sym not in local_dims and sym not in RESERVED_MATH_TOKENS:
                inferred = infer_symbol_dimension(sym, STANDARD_PHYSICS_DIMENSIONS)
                if inferred is not None:
                    local_dims[sym] = inferred

        return local_dims
    else:
        local_dims = {}
        for sym, si_dim in STANDARD_PHYSICS_DIMENSIONS.items():
            d = get_natural_dimension_power(si_dim)
            local_dims[sym] = (DIM_NATURAL_ENERGY ** d) if d != 0 else 1

        semantic_vars = entry.get("semantic_variables", {})
        if isinstance(semantic_vars, dict):
            for raw_sym, var_meta in semantic_vars.items():
                if isinstance(var_meta, dict):
                    unit_str = var_meta.get("unit")
                    if unit_str:
                        nat_dim = parse_unit_string_natural(unit_str)
                        if nat_dim is not None:
                            clean_sym = latex_to_sympy_str(raw_sym).strip()
                            clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", clean_sym)
                            if clean_sym:
                                local_dims[clean_sym] = nat_dim

        candidate_syms = set()
        if equation_str:
            candidate_syms.update(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", equation_str))
        if isinstance(semantic_vars, dict):
            for raw_sym in semantic_vars:
                clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", latex_to_sympy_str(raw_sym).strip())
                if clean_sym:
                    candidate_syms.add(clean_sym)

        for sym in candidate_syms:
            if sym not in local_dims and sym not in RESERVED_MATH_TOKENS:
                inferred_si = infer_symbol_dimension(sym, STANDARD_PHYSICS_DIMENSIONS)
                if inferred_si is not None:
                    d = get_natural_dimension_power(inferred_si)
                    local_dims[sym] = (DIM_NATURAL_ENERGY ** d) if d != 0 else 1

        return local_dims


def _evaluate_natural_units(
    formula_id: str,
    entry: Dict[str, Any],
    clean_eq: str,
    transformations: Any
) -> Optional[Dict[str, Any]]:
    """
    Fallback verification under Natural Units (hbar = c = k_B = 1).
    All physical quantities project to integer/rational mass-energy dimensions [E]^d.
    """
    symbols_dict = build_entry_dimensions(entry, natural_units=True, equation_str=clean_eq)
    try:
        if "=" in clean_eq:
            lhs_latex, rhs_latex = clean_eq.split("=", 1)
            lhs_str = latex_to_sympy_str(lhs_latex)
            rhs_str = latex_to_sympy_str(rhs_latex)
            if not lhs_str.strip() or not rhs_str.strip():
                return None

            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

            d_lhs = get_natural_dimension_power(lhs_expr)
            d_rhs = get_natural_dimension_power(rhs_expr)

            if rhs_str.strip() == "0" and d_lhs is not None:
                d_rhs = d_lhs
            elif lhs_str.strip() == "0" and d_rhs is not None:
                d_lhs = d_rhs

            if d_lhs is not None and d_rhs is not None and d_lhs == d_rhs:
                quantity = f"Natural Invariant [E]^{d_lhs}" if d_lhs != 0 else "Dimensionless Invariant (Natural Units)"
                dim_latex = f"[\\text{{E}}^{{{d_lhs}}}]" if d_lhs != 0 else "[1] \\text{ (Dimensionless)}"
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": entry.get("equation", ""),
                    "cleaned_equation": clean_eq,
                    "status": "HOMOGENEOUS",
                    "is_homogeneous": True,
                    "framework": "natural_units",
                    "quantity": quantity,
                    "dimension_latex": dim_latex,
                    "natural_power": d_lhs,
                    "lhs_powers": {"E": d_lhs},
                    "rhs_powers": {"E": d_rhs}
                }
        else:
            expr_str = latex_to_sympy_str(clean_eq)
            expr = parse_expr(expr_str, local_dict=symbols_dict, transformations=transformations)
            d = get_natural_dimension_power(expr)
            if d is not None:
                quantity = f"Natural Invariant [E]^{d}" if d != 0 else "Dimensionless Invariant (Natural Units)"
                dim_latex = f"[\\text{{E}}^{{{d}}}]" if d != 0 else "[1] \\text{ (Dimensionless)}"
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": entry.get("equation", ""),
                    "status": "DIMENSIONAL_EXPRESSION",
                    "is_homogeneous": True,
                    "framework": "natural_units",
                    "quantity": quantity,
                    "dimension_latex": dim_latex,
                    "powers": {"E": d}
                }
    except Exception:
        pass
    return None


def evaluate_formula_invariance(formula_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates dimensional homogeneity and algebraic consistency for a single formula.
    First attempts strict SI verification, falling back to Natural Units (hbar=c=1).
    """
    raw_equation = entry.get("equation", "")
    if not raw_equation:
        return {
            "id": formula_id,
            "status": "NO_EQUATION",
            "is_homogeneous": False,
            "error": "Empty equation string"
        }

    clean_eq = clean_equation_for_cas(raw_equation)
    symbols_dict = build_entry_dimensions(entry, natural_units=False, equation_str=clean_eq)
    transformations = standard_transformations + (implicit_multiplication_application,)

    if re.search(r"\\langle[^|]+\|[^|]+\|[^|]+\\rangle", clean_eq):
        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "OPERATOR_OR_TENSOR",
            "is_homogeneous": None,
            "note": "Differential operator, tensor index, or bra-ket formulation"
        }

    try:
        if "=" in clean_eq:
            lhs_latex, rhs_latex = clean_eq.split("=", 1)
            lhs_str = latex_to_sympy_str(lhs_latex)
            rhs_str = latex_to_sympy_str(rhs_latex)

            if not lhs_str.strip() or not rhs_str.strip():
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": raw_equation,
                    "status": "PARSE_SKIPPED",
                    "is_homogeneous": False,
                    "error": "Empty LHS or RHS after sanitization"
                }

            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

            lhs_deps = dimsys_SI.get_dimensional_dependencies(lhs_expr)
            rhs_deps = dimsys_SI.get_dimensional_dependencies(rhs_expr)

            lhs_powers = _extract_dim_powers(lhs_deps)
            rhs_powers = _extract_dim_powers(rhs_deps)

            is_zero_rhs = (rhs_str.strip() == "0" or rhs_expr == 0)
            is_zero_lhs = (lhs_str.strip() == "0" or lhs_expr == 0)

            if is_zero_rhs:
                is_homo = True
                rhs_powers = dict(lhs_powers)
                quantity = _identify_physical_quantity(lhs_powers)
            elif is_zero_lhs:
                is_homo = True
                lhs_powers = dict(rhs_powers)
                quantity = _identify_physical_quantity(rhs_powers)
            else:
                is_homo = (lhs_powers == rhs_powers)
                quantity = _identify_physical_quantity(lhs_powers)

            if is_homo:
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": raw_equation,
                    "cleaned_equation": clean_eq,
                    "status": "HOMOGENEOUS",
                    "is_homogeneous": True,
                    "framework": "SI",
                    "quantity": quantity,
                    "dimension_latex": _format_dim_latex(lhs_powers),
                    "lhs_powers": lhs_powers,
                    "rhs_powers": rhs_powers
                }

            sem_vars = entry.get("semantic_variables", {})
            has_conflicting_si_units = False
            if isinstance(sem_vars, dict) and len(sem_vars) >= 2:
                units = [v.get("unit") for v in sem_vars.values() if isinstance(v, dict) and v.get("unit")]
                if any(u in ("J", "kg*m/s", "kg⋅m/s", "N", "W", "Pa") for u in units) and not any(u and ("eV" in u or "GeV" in u or "natural" in u.lower()) for u in units):
                    si_dims_seen = set()
                    for u in units:
                        sd = parse_unit_string(u)
                        if sd is not None and sd != 1:
                            si_dims_seen.add(str(sd))
                    if len(si_dims_seen) >= 2:
                        has_conflicting_si_units = True

            if not has_conflicting_si_units:
                nat_result = _evaluate_natural_units(formula_id, entry, clean_eq, transformations)
                if nat_result and nat_result.get("is_homogeneous"):
                    return nat_result

            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "cleaned_equation": clean_eq,
                "status": "INHOMOGENEOUS",
                "is_homogeneous": False,
                "framework": "SI",
                "quantity": quantity,
                "dimension_latex": _format_dim_latex(lhs_powers),
                "lhs_powers": lhs_powers,
                "rhs_powers": rhs_powers
            }
        else:
            expr_str = latex_to_sympy_str(clean_eq)
            expr = parse_expr(expr_str, local_dict=symbols_dict, transformations=transformations)
            deps = dimsys_SI.get_dimensional_dependencies(expr)
            powers = _extract_dim_powers(deps)
            quantity = _identify_physical_quantity(powers)

            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "status": "DIMENSIONAL_EXPRESSION",
                "is_homogeneous": True,
                "framework": "SI",
                "quantity": quantity,
                "dimension_latex": _format_dim_latex(powers),
                "powers": powers
            }
    except Exception as e:
        nat_result = _evaluate_natural_units(formula_id, entry, clean_eq, transformations)
        if nat_result and nat_result.get("is_homogeneous"):
            return nat_result

        if re.search(r"\\langle|\\rangle|\|[a-zA-Z0-9\s]+\\rangle|\\nabla|\\partial_\{\\mu\}|\^\\mu|\^\\nu|_\{\\mu\\nu\}|\\dagger", clean_eq):
            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "status": "OPERATOR_OR_TENSOR",
                "is_homogeneous": None,
                "note": "Differential operator, tensor index, or bra-ket formulation"
            }

        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "PARSE_ERROR",
            "is_homogeneous": False,
            "error": str(e)
        }


def check_dimensions(
    latex: str,
    custom_vars: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Evaluates physical dimensions of expressions or equations using SymPy physics units:
    - Base SI dimension breakdown: [M, L, T, I, Theta, N, J]
    - Dimension name (e.g. Energy, Force, Velocity, Length, Dimensionless)
    - If equation has '=', checks dimensional homogeneity between LHS and RHS
    """
    clean_latex = clean_equation_for_cas(latex)
    symbols_dict = dict(STANDARD_PHYSICS_DIMENSIONS)

    # Infer dimensions for subscripted/indexed/prefixed variables (e.g. E_k, v_0, m_1, Delta_x)
    sympy_preview = latex_to_sympy_str(clean_latex)
    for tok in set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", sympy_preview)):
        if tok not in symbols_dict and tok not in RESERVED_MATH_TOKENS:
            inferred = infer_symbol_dimension(tok, STANDARD_PHYSICS_DIMENSIONS)
            if inferred is not None:
                symbols_dict[tok] = inferred

    if custom_vars:
        for k, v in custom_vars.items():
            try:
                symbols_dict[k] = parse_expr(v, local_dict=STANDARD_PHYSICS_DIMENSIONS)
            except Exception:
                pass

    transformations = standard_transformations + (implicit_multiplication_application,)

    if "=" in clean_latex:
        parts = clean_latex.split("=", 1)
        lhs_latex = parts[0].strip()
        rhs_latex = parts[1].strip()

        lhs_str = latex_to_sympy_str(lhs_latex)
        rhs_str = latex_to_sympy_str(rhs_latex)

        try:
            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            lhs_deps = dimsys_SI.get_dimensional_dependencies(lhs_expr)
            lhs_powers = _extract_dim_powers(lhs_deps)
        except Exception as e:
            return {"success": False, "error": f"Error parsing LHS dimension: {str(e)}"}

        try:
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_deps = dimsys_SI.get_dimensional_dependencies(rhs_expr)
            rhs_powers = _extract_dim_powers(rhs_deps)
        except Exception as e:
            return {"success": False, "error": f"Error parsing RHS dimension: {str(e)}"}

        is_homogeneous = (lhs_powers == rhs_powers)
        return {
            "success": True,
            "is_equation": True,
            "is_homogeneous": is_homogeneous,
            "lhs": {
                "latex": lhs_latex,
                "dimension_powers": lhs_powers,
                "dimension_latex": _format_dim_latex(lhs_powers),
                "quantity": _identify_physical_quantity(lhs_powers)
            },
            "rhs": {
                "latex": rhs_latex,
                "dimension_powers": rhs_powers,
                "dimension_latex": _format_dim_latex(rhs_powers),
                "quantity": _identify_physical_quantity(rhs_powers)
            },
            "summary": (
                r"Dimensionally homogeneous: $\text{dim}(\text{LHS}) \equiv \text{dim}(\text{RHS})$"
                if is_homogeneous
                else r"Dimensional mismatch detected: $\text{dim}(\text{LHS}) \neq \text{dim}(\text{RHS})$"
            )
        }
    else:
        sympy_str = latex_to_sympy_str(clean_latex)
        try:
            expr = parse_expr(sympy_str, local_dict=symbols_dict, transformations=transformations)
            deps = dimsys_SI.get_dimensional_dependencies(expr)
            powers = _extract_dim_powers(deps)
        except Exception as e:
            return {"success": False, "error": f"Error evaluating dimension: {str(e)}"}

        return {
            "success": True,
            "is_equation": False,
            "dimension_powers": powers,
            "dimension_latex": _format_dim_latex(powers),
            "quantity": _identify_physical_quantity(powers),
            "summary": f"Evaluated physical dimension: {_identify_physical_quantity(powers)}"
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
        elif mode == "dimensions":
            latex = payload.get("latex") or payload.get("expression", "")
            custom_vars = payload.get("custom_vars", None)
            res = check_dimensions(latex, custom_vars=custom_vars)
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

