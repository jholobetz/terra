"""
🔬 Terra Physics Lab - CAS Unit Parser
Parses empirical physics unit strings (e.g. "kg⋅m/s", "J/K", "m/s^2", "GeV", "dimensionless")
into exact SymPy physical dimensions for dimensional homogeneity verification.
"""

import re
from typing import Optional, Dict, Any
import sympy
from sympy.parsing.sympy_parser import parse_expr, standard_transformations
from sympy.physics.units import (
    length, mass, time, current, temperature, amount_of_substance, luminous_intensity
)
from sympy.physics.units.systems.si import dimsys_SI

# Base SI Dimensions
DIM_MASS = mass
DIM_LENGTH = length
DIM_TIME = time
DIM_CURRENT = current
DIM_TEMPERATURE = temperature
DIM_AMOUNT = amount_of_substance
DIM_LUMINOUS = luminous_intensity

# Derived Physical Dimensions
DIM_VELOCITY = DIM_LENGTH / DIM_TIME
DIM_ACCELERATION = DIM_LENGTH / (DIM_TIME**2)
DIM_FORCE = DIM_MASS * DIM_LENGTH / (DIM_TIME**2)
DIM_ENERGY = DIM_MASS * (DIM_LENGTH**2) / (DIM_TIME**2)
DIM_POWER = DIM_MASS * (DIM_LENGTH**2) / (DIM_TIME**3)
DIM_PRESSURE = DIM_MASS / (DIM_LENGTH * (DIM_TIME**2))
DIM_MOMENTUM = DIM_MASS * DIM_LENGTH / DIM_TIME
DIM_ACTION = DIM_MASS * (DIM_LENGTH**2) / DIM_TIME
DIM_CHARGE = DIM_CURRENT * DIM_TIME
DIM_VOLTAGE = DIM_MASS * (DIM_LENGTH**2) / ((DIM_TIME**3) * DIM_CURRENT)
DIM_MAGNETIC_B = DIM_MASS / (DIM_CURRENT * (DIM_TIME**2))
DIM_MAGNETIC_FLUX = DIM_MASS * (DIM_LENGTH**2) / (DIM_CURRENT * (DIM_TIME**2))
DIM_CAPACITANCE = ((DIM_TIME**4) * (DIM_CURRENT**2)) / (DIM_MASS * (DIM_LENGTH**2))
DIM_RESISTANCE = DIM_MASS * (DIM_LENGTH**2) / ((DIM_TIME**3) * (DIM_CURRENT**2))
DIM_INDUCTANCE = DIM_MASS * (DIM_LENGTH**2) / ((DIM_TIME**2) * (DIM_CURRENT**2))
DIM_FREQUENCY = 1 / DIM_TIME
DIM_ENTROPY = DIM_ENERGY / DIM_TEMPERATURE

# Standard Unit Lookup Table
ATOMIC_UNITS: Dict[str, Any] = {
    # Base SI units
    "m": DIM_LENGTH,
    "meter": DIM_LENGTH,
    "meters": DIM_LENGTH,
    "metre": DIM_LENGTH,
    "metres": DIM_LENGTH,
    "s": DIM_TIME,
    "sec": DIM_TIME,
    "second": DIM_TIME,
    "seconds": DIM_TIME,
    "kg": DIM_MASS,
    "kilogram": DIM_MASS,
    "kilograms": DIM_MASS,
    "g": DIM_MASS,
    "gram": DIM_MASS,
    "grams": DIM_MASS,
    "a": DIM_CURRENT,
    "amp": DIM_CURRENT,
    "ampere": DIM_CURRENT,
    "amperes": DIM_CURRENT,
    "k": DIM_TEMPERATURE,
    "kelvin": DIM_TEMPERATURE,
    "mol": DIM_AMOUNT,
    "mole": DIM_AMOUNT,
    "moles": DIM_AMOUNT,
    "cd": DIM_LUMINOUS,
    "candela": DIM_LUMINOUS,

    # Dimensionless units
    "1": 1,
    "rad": 1,
    "radian": 1,
    "radians": 1,
    "sr": 1,
    "steradian": 1,
    "deg": 1,
    "degree": 1,
    "degrees": 1,
    "count": 1,

    # Derived SI units
    "n": DIM_FORCE,
    "newton": DIM_FORCE,
    "newtons": DIM_FORCE,
    "j": DIM_ENERGY,
    "joule": DIM_ENERGY,
    "joules": DIM_ENERGY,
    "w": DIM_POWER,
    "watt": DIM_POWER,
    "watts": DIM_POWER,
    "pa": DIM_PRESSURE,
    "pascal": DIM_PRESSURE,
    "pascals": DIM_PRESSURE,
    "c": DIM_CHARGE,
    "coulomb": DIM_CHARGE,
    "coulombs": DIM_CHARGE,
    "v": DIM_VOLTAGE,
    "volt": DIM_VOLTAGE,
    "volts": DIM_VOLTAGE,
    "t": DIM_MAGNETIC_B,
    "tesla": DIM_MAGNETIC_B,
    "teslas": DIM_MAGNETIC_B,
    "wb": DIM_MAGNETIC_FLUX,
    "weber": DIM_MAGNETIC_FLUX,
    "f": DIM_CAPACITANCE,
    "farad": DIM_CAPACITANCE,
    "ohm": DIM_RESISTANCE,
    "h": DIM_INDUCTANCE,
    "henry": DIM_INDUCTANCE,
    "hz": DIM_FREQUENCY,
    "hertz": DIM_FREQUENCY,

    # Energy units (eV family)
    "ev": DIM_ENERGY,
    "kev": DIM_ENERGY,
    "mev": DIM_ENERGY,
    "gev": DIM_ENERGY,
    "tev": DIM_ENERGY,

    # Pressure & Astrophysics
    "bar": DIM_PRESSURE,
    "atm": DIM_PRESSURE,
    "torr": DIM_PRESSURE,
    "ly": DIM_LENGTH,
    "pc": DIM_LENGTH,
    "kpc": DIM_LENGTH,
    "mpc": DIM_LENGTH,
    "au": DIM_LENGTH,
    "angstrom": DIM_LENGTH,
    "amu": DIM_MASS,
    "da": DIM_MASS,
}

DIMENSIONLESS_SYNONYMS = {
    "dimensionless", "none", "n/a", "na", "null", "unitless", "-", "--",
    "pure number", "ratio", "arbitrary", "varies", "unspecified"
}

SUPERSCRIPT_MAP = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "⁻": "-", "⁺": "+"
}


def sanitize_unit_string(raw_unit: str) -> str:
    """
    Cleans raw encyclopedia unit text into a standardized algebraic expression.
    """
    s = raw_unit.strip()

    # Strip outermost matched quotes, brackets, or braces if entire string is wrapped
    for open_b, close_b in [("(", ")"), ("[", "]"), ("{", "}"), ("'", "'"), ('"', '"')]:
        if s.startswith(open_b) and s.endswith(close_b):
            s = s[1:-1].strip()

    # Extract unit if formatted like "Joules (J)" or "Volts [V]"
    paren_match = re.search(r"\(([A-Za-z0-9/·⋅*^ -]+)\)", raw_unit)
    if paren_match:
        cand = paren_match.group(1).strip()
        if cand.lower() not in DIMENSIONLESS_SYNONYMS:
            s = cand

    # Normalize multiplication dots: ·, ⋅, \cdot (do not break existing **)
    s = re.sub(r"[·⋅]|\s*\\cdot\s*", " * ", s)

    # Replace superscript unicode powers: m⁻¹ -> m**(-1), m² -> m**(2)
    def _sub_sup(m):
        seq = "".join(SUPERSCRIPT_MAP.get(c, c) for c in m.group(0))
        return f"**({seq})"

    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺]+", _sub_sup, s)

    # Convert ^2 or ^{...} to **2
    s = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", s)
    s = re.sub(r"\^([+-]?[0-9]+(?:\.[0-9]+)?(?:/[0-9]+)?)", r"**(\1)", s)

    # Handle standard division
    s = s.replace("/", " / ")

    # Normalize whitespace
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_unit_string(raw_unit: Optional[str]) -> Optional[Any]:
    """
    Parses a unit string from formula semantic_variables into a SymPy dimension.
    Returns:
        SymPy dimension expression, 1 for dimensionless, or None if unparseable.
    """
    if not raw_unit:
        return 1

    clean = sanitize_unit_string(raw_unit)
    if not clean or clean.lower() in DIMENSIONLESS_SYNONYMS:
        return 1

    # Tokenize by operators, signed numbers, and parentheses
    tokens = re.findall(r"[A-Za-z]+|\*\*|\*|/|\(|\)|[+-]?[0-9]+(?:\.[0-9]+)?", clean)
    if not tokens:
        return None

    local_dict = {}
    expr_tokens = []

    for t in tokens:
        lower_t = t.lower()
        if lower_t in ATOMIC_UNITS:
            var_name = f"unit_{lower_t}"
            local_dict[var_name] = ATOMIC_UNITS[lower_t]
            expr_tokens.append(var_name)
        elif t in ("*", "/", "(", ")", "**") or re.match(r"^[+-]?[0-9]+(?:\.[0-9]+)?$", t):
            expr_tokens.append(t)
        else:
            # Unrecognized unit token
            return None

    expr_str = " ".join(expr_tokens)
    # Fix implicit multiplications like "unit_kg unit_m" -> "unit_kg * unit_m"
    expr_str = re.sub(r"(unit_[a-z]+)\s+(unit_[a-z]+)", r"\1 * \2", expr_str)

    try:
        dim_expr = parse_expr(expr_str, local_dict=local_dict, transformations=standard_transformations)
        return dim_expr
    except Exception:
        return None


def get_dimension_signature(dim_expr: Any) -> Dict[str, Any]:
    """
    Returns the [M, L, T, I, Theta, N, J] dimension dictionary from a SymPy dimension expression.
    """
    if dim_expr == 1 or dim_expr is None:
        return {}

    try:
        deps = dimsys_SI.get_dimensional_dependencies(dim_expr)
    except Exception:
        return {}

    mapping = {
        mass: "M",
        length: "L",
        time: "T",
        current: "I",
        temperature: "Theta",
        amount_of_substance: "N",
        luminous_intensity: "J"
    }

    powers = {}
    for d, p in deps.items():
        for base_unit, symbol in mapping.items():
            if d == base_unit or str(d) == str(base_unit):
                powers[symbol] = int(p) if (hasattr(p, 'is_integer') and p.is_integer) or (isinstance(p, (int, float)) and int(p) == p) else float(p)
    return powers
