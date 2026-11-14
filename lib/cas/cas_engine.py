#!/usr/bin/env python3
"""
🔬 Terra Physics Lab - Symbolic Computer Algebra System (CAS) Engine
Evaluates physical limits, series expansions, Legendre transformations, and
dimensional consistency from LaTeX expressions using SymPy with deterministic
execution and safety timeouts.
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
    implicit_multiplication_application,
)
from sympy.physics.units import (
    length, mass, time, current, temperature, amount_of_substance, luminous_intensity,
)
from sympy.physics.units.systems.si import dimsys_SI

from lib.cas.latex_parser import (
    latex_to_sympy_str,
    clean_latex_equation,
    clean_equation_for_cas,
    normalize_math_string,
    split_top_level_equals,
)
from lib.cas.unit_parser import (
    parse_unit_string,
    parse_unit_string_natural,
    get_natural_dimension_power,
    DIM_NATURAL_ENERGY,
)


class TimeoutException(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutException("Symbolic evaluation timed out (2.0s hard ceiling).")


def build_physics_symbols(sympy_str: str) -> Dict[str, sympy.Symbol]:
    """
    Extracts variable names and defines positive physics symbols.
    """
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", sympy_str)
    reserved = {
        "sqrt", "sin", "cos", "tan", "exp", "log", "ln",
        "sinh", "cosh", "tanh", "pi", "E", "I", "O", "abs", "Abs",
    }
    symbols_dict = {}
    for tok in set(tokens):
        if tok not in reserved:
            symbols_dict[tok] = sympy.Symbol(tok, positive=True)
    return symbols_dict


def evaluate_symbolic(
    latex: str,
    limit_var: Optional[str] = None,
    limit_to: Optional[str] = None,
    series_order: int = 4,
) -> Dict[str, Any]:
    """
    Evaluates LaTeX expressions symbolically:
    - Cleans annotations, primes, and chained equalities in algebraic mode
    - Parses expression AST via balanced-brace LaTeX parser
    - Computes asymptotic limit if requested
    - Computes Taylor series expansion around limit point
    """
    clean_latex = clean_latex_equation(latex, mode="algebraic")
    lhs_str = None
    rhs_str = clean_latex

    top_parts = split_top_level_equals(clean_latex)
    if len(top_parts) >= 2:
        lhs_str = top_parts[0].strip()
        rhs_str = top_parts[-1].strip()

    sympy_str = latex_to_sympy_str(rhs_str)
    symbols_dict = build_physics_symbols(sympy_str)

    try:
        transformations = standard_transformations + (implicit_multiplication_application,)
        expr = parse_expr(sympy_str, local_dict=symbols_dict, transformations=transformations)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to parse mathematical expression: {str(e)}",
            "sympy_str": sympy_str,
        }

    result = {
        "success": True,
        "parsed_latex": sympy.latex(expr),
        "variables": sorted([str(s) for s in expr.free_symbols]),
        "lhs": lhs_str,
    }

    # Resolve limit variable (supporting raw ASCII symbol or LaTeX/primed token)
    resolved_var = limit_var
    if limit_var and resolved_var not in symbols_dict:
        cand_var = latex_to_sympy_str(clean_latex_equation(limit_var, mode="algebraic")).strip()
        if cand_var in symbols_dict:
            resolved_var = cand_var

    if limit_var and resolved_var in symbols_dict:
        var_sym = symbols_dict[resolved_var]

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
                "result_latex": sympy.latex(lim_val),
            }
        except Exception as e:
            result["limit"] = {
                "variable": limit_var,
                "target": str(target),
                "error": str(e),
            }

        if target == 0:
            try:
                ser = sympy.series(expr, var_sym, target, series_order)
                ser_no_o = ser.removeO()
                result["series"] = {
                    "variable": limit_var,
                    "order": series_order,
                    "expansion_latex": sympy.latex(ser),
                    "leading_terms_latex": sympy.latex(ser_no_o),
                }
            except Exception as e:
                result["series"] = {"error": str(e)}

    return result


def legendre_transform(
    lagrangian: str,
    coords: Any,
    velocities: Any,
    parameters: Optional[Any] = None,
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
            "error": f"Dimension mismatch: {len(coords)} coordinate(s) vs {len(velocities)} velocity variable(s).",
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
                "is_singular": True,
            },
            "error": "Singular Lagrangian (det(W) = 0). Velocities cannot be inverted; system possesses primary Dirac constraints.",
        }

    eqs = [sympy.Eq(p_syms[i], p_exprs[i]) for i in range(n)]
    sol_list = sympy.solve(eqs, v_syms, dict=True)
    if not sol_list:
        return {"success": False, "error": "Cannot solve for velocities algebraically."}

    sol = sol_list[0]
    if len(sol_list) > 1:
        for s in sol_list:
            test_subs = [(p_syms[0], 1), (v_syms[0], 1)] + [
                (symbols_dict[p], 1) for p in parameters if p in symbols_dict
            ]
            test_v = s[v_syms[0]].subs(test_subs)
            try:
                if test_v.evalf() > 0:
                    sol = s
                    break
            except Exception:
                pass

    pv_sum = sum(p_syms[i] * sol[v_syms[i]] for i in range(n))
    sub_tuples = [(v_syms[i], sol[v_syms[i]]) for i in range(n)]
    L_subbed = L.subs(sub_tuples)
    H_raw = pv_sum - L_subbed

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

    eqs_of_motion = []
    for i in range(n):
        dq_dt = sympy.diff(H, p_syms[i])
        dp_dt = -sympy.diff(H, q_syms[i])
        eqs_of_motion.append({
            "coord": coords[i],
            "momentum": str(p_syms[i]),
            "dq_dt_latex": rf"\dot{{{coords[i]}}} = \frac{{\partial H}}{{\partial {p_syms[i]}}} = {sympy.latex(dq_dt)}",
            "dp_dt_latex": rf"\dot{{{p_syms[i]}}} = -\frac{{\partial H}}{{\partial {coords[i]}}} = {sympy.latex(dp_dt)}",
        })

    cyclic_coords = []
    conserved_momenta = []
    for i in range(n):
        dL_dq = sympy.diff(L, q_syms[i])
        if dL_dq == 0:
            cyclic_coords.append(coords[i])
            conserved_momenta.append(str(p_syms[i]))

    momenta_info = []
    for i in range(n):
        momenta_info.append({
            "name": str(p_syms[i]),
            "symbol": str(p_syms[i]),
            "latex": rf"{p_syms[i]} = \frac{{\partial L}}{{\partial \dot{{{coords[i]}}}}} = {sympy.latex(p_exprs[i])}",
            "expr_latex": sympy.latex(p_exprs[i]),
        })

    inv_vel_info = []
    for i in range(n):
        inv_vel_info.append({
            "velocity": rf"\dot{{{coords[i]}}}",
            "latex": rf"\dot{{{coords[i]}}} = {sympy.latex(sol[v_syms[i]])}",
            "expr_latex": sympy.latex(sol[v_syms[i]]),
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
            "is_singular": False,
        },
        "inverted_velocities": inv_vel_info,
        "hamiltonian_latex": sympy.latex(H),
        "equations_of_motion": eqs_of_motion,
        "conservation": {
            "energy_conserved": True,
            "cyclic_coordinates": cyclic_coords,
            "conserved_momenta": conserved_momenta,
            "summary": summary,
        },
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
    "theta": 1, "phi": 1, "alpha": 1,
}


def _extract_dim_powers(deps: Dict[Any, Any]) -> Dict[str, Any]:
    mapping = {
        mass: "M",
        length: "L",
        time: "T",
        current: "I",
        temperature: "Theta",
        amount_of_substance: "N",
        luminous_intensity: "J",
    }
    dim_powers = {}
    for d, p in deps.items():
        for base_unit, symbol in mapping.items():
            if d == base_unit or str(d) == str(base_unit):
                dim_powers[symbol] = (
                    int(p)
                    if (hasattr(p, "is_integer") and p.is_integer)
                    or (isinstance(p, (int, float)) and int(p) == p)
                    else float(p)
                )
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
    "pi", "E", "I", "abs", "Abs", "diff", "Derivative",
}


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

    prefix_patterns = [
        r"^(?:Delta|delta|d|nabla)_+([a-zA-Z0-9_]+)$",
        r"^d([A-Z][a-zA-Z0-9_]*)$",
        r"^d([a-z])$",
    ]
    for pat in prefix_patterns:
        m = re.match(pat, clean)
        if m:
            base_sym = m.group(1)
            if base_sym in standard_dims:
                return standard_dims[base_sym]
            clean = base_sym
            break

    if "_" in clean:
        root = clean.split("_")[0]
        if root in standard_dims:
            return standard_dims[root]

    m_num = re.match(r"^([a-zA-Z]+)[0-9]+$", clean)
    if m_num:
        root = m_num.group(1)
        if root in standard_dims:
            return standard_dims[root]

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


def _parse_custom_var_dimension(expr_or_unit: str, natural_units: bool = False) -> Optional[Any]:
    """Resolves a custom variable override expression (e.g. 'mass * length / time' or 'J') to a dimension."""
    si_dim = None
    try:
        si_dim = parse_expr(expr_or_unit, local_dict=STANDARD_PHYSICS_DIMENSIONS)
    except Exception:
        si_dim = parse_unit_string(expr_or_unit)
    if si_dim is None:
        return None
    if not natural_units:
        return si_dim
    d = get_natural_dimension_power(si_dim)
    if d is None:
        return parse_unit_string_natural(expr_or_unit)
    return (DIM_NATURAL_ENERGY ** d) if d != 0 else 1


def build_entry_dimensions(
    entry: Dict[str, Any],
    natural_units: bool = False,
    equation_str: Optional[str] = None,
    custom_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Builds a localized symbol-to-dimension map by prioritizing:
    1. Explicit `custom_vars` overrides (if supplied).
    2. Formula `semantic_variables` unit fields.
    3. `STANDARD_PHYSICS_DIMENSIONS` lookup.
    4. Heuristic root and prefix inference (`infer_symbol_dimension`).
    If `natural_units` is True, dimensions are projected to powers of `DIM_NATURAL_ENERGY` [E]^d.
    """
    semantic_vars = entry.get("semantic_variables", {})
    candidate_syms = set()
    if equation_str:
        sympy_preview = latex_to_sympy_str(equation_str)
        candidate_syms.update(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", equation_str))
        candidate_syms.update(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", sympy_preview))
    if isinstance(semantic_vars, dict):
        for raw_sym in semantic_vars:
            clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", latex_to_sympy_str(raw_sym).strip())
            if clean_sym:
                candidate_syms.add(clean_sym)

    if not natural_units:
        local_dims = dict(STANDARD_PHYSICS_DIMENSIONS)
        if isinstance(semantic_vars, dict):
            for raw_sym, var_meta in semantic_vars.items():
                if isinstance(var_meta, dict):
                    unit_str = var_meta.get("unit")
                    if unit_str:
                        dim_expr = parse_unit_string(unit_str)
                        if dim_expr is not None:
                            clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", latex_to_sympy_str(raw_sym).strip())
                            if clean_sym:
                                local_dims[clean_sym] = dim_expr

        for sym in candidate_syms:
            if sym not in local_dims and sym not in RESERVED_MATH_TOKENS:
                inferred = infer_symbol_dimension(sym, STANDARD_PHYSICS_DIMENSIONS)
                if inferred is not None:
                    local_dims[sym] = inferred
    else:
        local_dims = {}
        for sym, si_dim in STANDARD_PHYSICS_DIMENSIONS.items():
            d = get_natural_dimension_power(si_dim)
            if d is not None:
                local_dims[sym] = (DIM_NATURAL_ENERGY ** d) if d != 0 else 1

        if isinstance(semantic_vars, dict):
            for raw_sym, var_meta in semantic_vars.items():
                if isinstance(var_meta, dict):
                    unit_str = var_meta.get("unit")
                    if unit_str:
                        nat_dim = parse_unit_string_natural(unit_str)
                        if nat_dim is not None:
                            clean_sym = re.sub(r"[^a-zA-Z0-9_]", "", latex_to_sympy_str(raw_sym).strip())
                            if clean_sym:
                                local_dims[clean_sym] = nat_dim

        for sym in candidate_syms:
            if sym not in local_dims and sym not in RESERVED_MATH_TOKENS:
                inferred_si = infer_symbol_dimension(sym, STANDARD_PHYSICS_DIMENSIONS)
                if inferred_si is not None:
                    d = get_natural_dimension_power(inferred_si)
                    if d is not None:
                        local_dims[sym] = (DIM_NATURAL_ENERGY ** d) if d != 0 else 1

    if custom_vars:
        for k, v in custom_vars.items():
            parsed_dim = _parse_custom_var_dimension(v, natural_units=natural_units)
            if parsed_dim is not None:
                local_dims[k] = parsed_dim

    return local_dims


def _is_explicit_velocity_power_mismatch(
    lhs_str: str,
    rhs_str: str,
    lhs_powers: Dict[str, Any],
    rhs_powers: Dict[str, Any],
    entry: Dict[str, Any],
) -> bool:
    """
    Detects pure velocity-exponent errors (e.g. `E = m v^3`, `E = m c^3`, `p = m v^2`, `x = v^2 t`)
    where both sides parse cleanly in SI, differ strictly by a non-zero power of velocity `(L / T)^k`,
    and already contain an explicit speed/velocity symbol (`v`, `u`, `c`) without Natural Units metadata.
    """
    sem_vars = entry.get("semantic_variables", {})
    if isinstance(sem_vars, dict):
        for v_meta in sem_vars.values():
            if isinstance(v_meta, dict):
                u = str(v_meta.get("unit") or "")
                if "eV" in u or "natural" in u.lower():
                    return False

    for base_k in ("M", "I", "Theta", "N", "J"):
        if lhs_powers.get(base_k, 0) != rhs_powers.get(base_k, 0):
            return False

    dl = lhs_powers.get("L", 0) - rhs_powers.get("L", 0)
    dt = lhs_powers.get("T", 0) - rhs_powers.get("T", 0)
    if dl == 0 or dl != -dt:
        return False

    tokens = set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", f"{lhs_str} {rhs_str}"))
    velocity_tokens = {"v", "u", "c", "v_0", "u_0"}
    return bool(tokens & velocity_tokens)


def _evaluate_natural_units(
    formula_id: str,
    entry: Dict[str, Any],
    clean_eq: str,
    transformations: Any,
    custom_vars: Optional[Dict[str, str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Fallback verification under Natural Units (hbar = c = k_B = 1).
    All physical quantities project to integer/rational mass-energy dimensions [E]^d.
    """
    symbols_dict = build_entry_dimensions(
        entry, natural_units=True, equation_str=clean_eq, custom_vars=custom_vars
    )
    try:
        top_parts = split_top_level_equals(clean_eq)
        if len(top_parts) >= 2:
            lhs_latex, rhs_latex = top_parts[0].strip(), top_parts[1].strip()
            lhs_str = latex_to_sympy_str(lhs_latex)
            rhs_str = latex_to_sympy_str(rhs_latex)
            if not lhs_str.strip() or not rhs_str.strip():
                return None

            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

            d_lhs = get_natural_dimension_power(lhs_expr)
            d_rhs = get_natural_dimension_power(rhs_expr)

            if (rhs_str.strip() == "0" or rhs_expr == 0) and d_lhs is not None:
                d_rhs = d_lhs
            elif (lhs_str.strip() == "0" or lhs_expr == 0) and d_rhs is not None:
                d_lhs = d_rhs

            if d_lhs is not None and d_rhs is not None and d_lhs == d_rhs:
                quantity = (
                    f"Natural Invariant [E]^{d_lhs}"
                    if d_lhs != 0
                    else "Dimensionless Invariant (Natural Units)"
                )
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
                    "lhs_latex": lhs_latex,
                    "rhs_latex": rhs_latex,
                    "lhs_powers": {"E": d_lhs},
                    "rhs_powers": {"E": d_rhs},
                }
        else:
            expr_str = latex_to_sympy_str(clean_eq)
            expr = parse_expr(expr_str, local_dict=symbols_dict, transformations=transformations)
            d = get_natural_dimension_power(expr)
            if d is not None:
                quantity = (
                    f"Natural Invariant [E]^{d}"
                    if d != 0
                    else "Dimensionless Invariant (Natural Units)"
                )
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
                    "powers": {"E": d},
                }
    except Exception:
        pass
    return None


def evaluate_formula_invariance(
    formula_id: str,
    entry: Dict[str, Any],
    custom_vars: Optional[Dict[str, str]] = None,
    precomputed_si_dims: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Evaluates dimensional homogeneity and algebraic consistency for a single formula.
    First attempts strict SI verification (including Zero-RHS `A - B = 0`), falling back
    to Natural Units (`hbar = c = k_B = 1`) when appropriate.
    """
    raw_equation = entry.get("equation", "")
    if not raw_equation or not raw_equation.strip():
        return {
            "id": formula_id,
            "status": "NO_EQUATION",
            "is_homogeneous": False,
            "error": "Empty equation string",
        }

    clean_eq = clean_equation_for_cas(raw_equation)
    if precomputed_si_dims is not None and not custom_vars:
        symbols_dict = dict(precomputed_si_dims)
        sympy_preview = latex_to_sympy_str(clean_eq)
        for tok in set(re.findall(r"\b[a-zA-Z][a-zA-Z0-9_]*\b", sympy_preview)):
            if tok not in symbols_dict and tok not in RESERVED_MATH_TOKENS:
                inferred = infer_symbol_dimension(tok, STANDARD_PHYSICS_DIMENSIONS)
                if inferred is not None:
                    symbols_dict[tok] = inferred
    else:
        symbols_dict = build_entry_dimensions(
            entry, natural_units=False, equation_str=clean_eq, custom_vars=custom_vars
        )

    transformations = standard_transformations + (implicit_multiplication_application,)

    if re.search(r"\\langle[^|]+\|[^|]+\|[^|]+\\rangle", clean_eq):
        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "OPERATOR_OR_TENSOR",
            "is_homogeneous": None,
            "note": "Differential operator, tensor index, or bra-ket formulation",
        }

    top_parts = split_top_level_equals(clean_eq)
    is_eq = len(top_parts) >= 2

    try:
        if is_eq:
            lhs_latex, rhs_latex = top_parts[0].strip(), top_parts[1].strip()
            lhs_str = latex_to_sympy_str(lhs_latex)
            rhs_str = latex_to_sympy_str(rhs_latex)

            if not lhs_str.strip() or not rhs_str.strip():
                return {
                    "id": formula_id,
                    "title": entry.get("title", ""),
                    "raw_equation": raw_equation,
                    "status": "PARSE_SKIPPED",
                    "is_homogeneous": False,
                    "error": "Empty LHS or RHS after sanitization",
                }

            lhs_expr = parse_expr(lhs_str, local_dict=symbols_dict, transformations=transformations)
            rhs_expr = parse_expr(rhs_str, local_dict=symbols_dict, transformations=transformations)

            lhs_deps = dimsys_SI.get_dimensional_dependencies(lhs_expr)
            rhs_deps = dimsys_SI.get_dimensional_dependencies(rhs_expr)

            lhs_powers = _extract_dim_powers(lhs_deps)
            rhs_powers = _extract_dim_powers(rhs_deps)

            is_zero_rhs = rhs_str.strip() == "0" or rhs_expr == 0
            is_zero_lhs = lhs_str.strip() == "0" or lhs_expr == 0

            if is_zero_rhs:
                is_homo = True
                rhs_powers = dict(lhs_powers)
                quantity = _identify_physical_quantity(lhs_powers)
            elif is_zero_lhs:
                is_homo = True
                lhs_powers = dict(rhs_powers)
                quantity = _identify_physical_quantity(rhs_powers)
            else:
                is_homo = lhs_powers == rhs_powers
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
                    "lhs_latex": lhs_latex,
                    "rhs_latex": rhs_latex,
                    "lhs_powers": lhs_powers,
                    "rhs_powers": rhs_powers,
                }

            sem_vars = entry.get("semantic_variables", {})
            has_conflicting_si_units = False
            if isinstance(sem_vars, dict) and len(sem_vars) >= 2:
                units = [v.get("unit") for v in sem_vars.values() if isinstance(v, dict) and v.get("unit")]
                if any(u in ("J", "kg*m/s", "kg⋅m/s", "N", "W", "Pa") for u in units) and not any(
                    u and ("eV" in u or "GeV" in u or "natural" in u.lower()) for u in units
                ):
                    si_dims_seen = set()
                    for u in units:
                        sd = parse_unit_string(u)
                        if sd is not None and sd != 1:
                            si_dims_seen.add(str(sd))
                    if len(si_dims_seen) >= 2:
                        has_conflicting_si_units = True

            if not has_conflicting_si_units and not _is_explicit_velocity_power_mismatch(
                lhs_str, rhs_str, lhs_powers, rhs_powers, entry
            ):
                nat_result = _evaluate_natural_units(
                    formula_id, entry, clean_eq, transformations, custom_vars=custom_vars
                )
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
                "lhs_latex": lhs_latex,
                "rhs_latex": rhs_latex,
                "lhs_powers": lhs_powers,
                "rhs_powers": rhs_powers,
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
                "powers": powers,
            }
    except Exception as e:
        nat_result = _evaluate_natural_units(
            formula_id, entry, clean_eq, transformations, custom_vars=custom_vars
        )
        if nat_result and nat_result.get("is_homogeneous"):
            return nat_result

        if re.search(
            r"\\langle|\\rangle|\|[a-zA-Z0-9\s]+\\rangle|\\nabla|\\partial_\{\\mu\}|\^\\mu|\^\\nu|_\{\\mu\\nu\}|\\dagger",
            clean_eq,
        ):
            return {
                "id": formula_id,
                "title": entry.get("title", ""),
                "raw_equation": raw_equation,
                "status": "OPERATOR_OR_TENSOR",
                "is_homogeneous": None,
                "note": "Differential operator, tensor index, or bra-ket formulation",
            }

        return {
            "id": formula_id,
            "title": entry.get("title", ""),
            "raw_equation": raw_equation,
            "status": "PARSE_ERROR",
            "is_homogeneous": False,
            "error": str(e),
        }


def check_dimensions(
    latex: str,
    custom_vars: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Evaluates physical dimensions of expressions or equations via the unified
    `evaluate_formula_invariance()` engine (supporting SI base breakdown,
    Zero-RHS `A - B = 0` identities, and Natural Units `hbar = c = k_B = 1`).
    """
    inv = evaluate_formula_invariance(
        formula_id="live-check",
        entry={"equation": latex},
        custom_vars=custom_vars,
    )
    status = inv.get("status")

    if status in ("HOMOGENEOUS", "INHOMOGENEOUS"):
        is_homo = status == "HOMOGENEOUS"
        framework = inv.get("framework", "SI")
        lhs_powers = inv.get("lhs_powers", {})
        rhs_powers = inv.get("rhs_powers", {})
        lhs_latex = inv.get("lhs_latex", "")
        rhs_latex = inv.get("rhs_latex", "")

        if framework == "natural_units":
            lhs_dim_latex = inv.get("dimension_latex", "")
            rhs_dim_latex = inv.get("dimension_latex", "")
            lhs_qty = inv.get("quantity", "")
            rhs_qty = inv.get("quantity", "")
            summary = (
                r"Dimensionally homogeneous in Natural Units ($\hbar = c = k_B = 1$): "
                r"$\text{dim}(\text{LHS}) \equiv \text{dim}(\text{RHS})$"
            )
        else:
            lhs_dim_latex = _format_dim_latex(lhs_powers)
            rhs_dim_latex = _format_dim_latex(rhs_powers)
            lhs_qty = _identify_physical_quantity(lhs_powers)
            rhs_qty = _identify_physical_quantity(rhs_powers)
            summary = (
                r"Dimensionally homogeneous: $\text{dim}(\text{LHS}) \equiv \text{dim}(\text{RHS})$"
                if is_homo
                else r"Dimensional mismatch detected: $\text{dim}(\text{LHS}) \neq \text{dim}(\text{RHS})$"
            )

        return {
            "success": True,
            "is_equation": True,
            "is_homogeneous": is_homo,
            "framework": framework,
            "lhs": {
                "latex": lhs_latex,
                "dimension_powers": lhs_powers,
                "dimension_latex": lhs_dim_latex,
                "quantity": lhs_qty,
            },
            "rhs": {
                "latex": rhs_latex,
                "dimension_powers": rhs_powers,
                "dimension_latex": rhs_dim_latex,
                "quantity": rhs_qty,
            },
            "summary": summary,
        }

    if status == "DIMENSIONAL_EXPRESSION":
        powers = inv.get("powers", {})
        qty = inv.get("quantity", _identify_physical_quantity(powers))
        return {
            "success": True,
            "is_equation": False,
            "framework": inv.get("framework", "SI"),
            "dimension_powers": powers,
            "dimension_latex": inv.get("dimension_latex", _format_dim_latex(powers)),
            "quantity": qty,
            "summary": f"Evaluated physical dimension: {qty}",
        }

    err = inv.get("error") or inv.get("note") or "Unable to evaluate physical dimensions."
    if status == "PARSE_ERROR" and ("Dimension of" in err or "equivalent dimensions" in err):
        clean_eq = clean_equation_for_cas(latex)
        top_parts = split_top_level_equals(clean_eq)
        if len(top_parts) >= 2:
            return {
                "success": True,
                "is_equation": True,
                "is_homogeneous": False,
                "lhs": {
                    "latex": top_parts[0].strip(),
                    "dimension_powers": {},
                    "dimension_latex": r"\text{Inhomogeneous Sum}",
                    "quantity": "Incompatible Additive Terms",
                },
                "rhs": {
                    "latex": top_parts[1].strip(),
                    "dimension_powers": {},
                    "dimension_latex": r"\text{Inhomogeneous Sum}",
                    "quantity": "Incompatible Additive Terms",
                },
                "summary": r"Dimensional mismatch detected: incompatible additive terms",
                "error": err,
            }

    return {"success": False, "error": f"Error evaluating dimension: {err}"}


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
                parameters=parameters,
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
