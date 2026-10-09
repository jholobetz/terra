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
DIM_AREA = DIM_LENGTH**2
DIM_VOLUME = DIM_LENGTH**3
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
DIM_SURFACE_TENSION = DIM_FORCE / DIM_LENGTH
DIM_VISCOSITY_DYNAMIC = DIM_PRESSURE * DIM_TIME
DIM_VISCOSITY_KINEMATIC = (DIM_LENGTH**2) / DIM_TIME
DIM_CONDUCTANCE = 1 / DIM_RESISTANCE
DIM_CURRENT_DENSITY = DIM_CURRENT / (DIM_LENGTH**2)

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
    "secs": DIM_TIME,
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
    "kelvins": DIM_TEMPERATURE,
    "mol": DIM_AMOUNT,
    "mole": DIM_AMOUNT,
    "moles": DIM_AMOUNT,
    "cd": DIM_LUMINOUS,
    "candela": DIM_LUMINOUS,
    "candelas": DIM_LUMINOUS,

    # Metric Length Prefixes
    "km": DIM_LENGTH,
    "kilometer": DIM_LENGTH,
    "kilometers": DIM_LENGTH,
    "dm": DIM_LENGTH,
    "decimeter": DIM_LENGTH,
    "cm": DIM_LENGTH,
    "centimeter": DIM_LENGTH,
    "centimeters": DIM_LENGTH,
    "mm": DIM_LENGTH,
    "millimeter": DIM_LENGTH,
    "millimeters": DIM_LENGTH,
    "um": DIM_LENGTH,
    "micrometer": DIM_LENGTH,
    "micrometers": DIM_LENGTH,
    "micron": DIM_LENGTH,
    "microns": DIM_LENGTH,
    "nm": DIM_LENGTH,
    "nanometer": DIM_LENGTH,
    "nanometers": DIM_LENGTH,
    "pm": DIM_LENGTH,
    "picometer": DIM_LENGTH,
    "picometers": DIM_LENGTH,
    "fm": DIM_LENGTH,
    "femtometer": DIM_LENGTH,
    "femtometers": DIM_LENGTH,
    "fermi": DIM_LENGTH,
    "fermis": DIM_LENGTH,
    "angstrom": DIM_LENGTH,
    "angstroms": DIM_LENGTH,
    "bohr": DIM_LENGTH,

    # Astrophysics Length & Mass
    "ly": DIM_LENGTH,
    "lightyear": DIM_LENGTH,
    "lightyears": DIM_LENGTH,
    "light_year": DIM_LENGTH,
    "light_years": DIM_LENGTH,
    "pc": DIM_LENGTH,
    "parsec": DIM_LENGTH,
    "parsecs": DIM_LENGTH,
    "kpc": DIM_LENGTH,
    "kiloparsec": DIM_LENGTH,
    "kiloparsecs": DIM_LENGTH,
    "mpc": DIM_LENGTH,
    "megaparsec": DIM_LENGTH,
    "megaparsecs": DIM_LENGTH,
    "gpc": DIM_LENGTH,
    "au": DIM_LENGTH,
    "r_sun": DIM_LENGTH,
    "rsun": DIM_LENGTH,
    "r_earth": DIM_LENGTH,
    "rearth": DIM_LENGTH,
    "m_sun": DIM_MASS,
    "msun": DIM_MASS,
    "m_earth": DIM_MASS,
    "mearth": DIM_MASS,
    "m_jup": DIM_MASS,
    "mjup": DIM_MASS,
    "l_sun": DIM_POWER,
    "lsun": DIM_POWER,

    # Time & Frequency
    "ms": DIM_TIME,
    "millisecond": DIM_TIME,
    "milliseconds": DIM_TIME,
    "us": DIM_TIME,
    "microsecond": DIM_TIME,
    "microseconds": DIM_TIME,
    "ns": DIM_TIME,
    "nanosecond": DIM_TIME,
    "nanoseconds": DIM_TIME,
    "ps": DIM_TIME,
    "picosecond": DIM_TIME,
    "picoseconds": DIM_TIME,
    "fs": DIM_TIME,
    "femtosecond": DIM_TIME,
    "femtoseconds": DIM_TIME,
    "min": DIM_TIME,
    "minute": DIM_TIME,
    "minutes": DIM_TIME,
    "h": DIM_TIME,
    "hr": DIM_TIME,
    "hrs": DIM_TIME,
    "hour": DIM_TIME,
    "hours": DIM_TIME,
    "d": DIM_TIME,
    "day": DIM_TIME,
    "days": DIM_TIME,
    "yr": DIM_TIME,
    "year": DIM_TIME,
    "years": DIM_TIME,
    "myr": DIM_TIME,
    "gyr": DIM_TIME,
    "hz": DIM_FREQUENCY,
    "hertz": DIM_FREQUENCY,
    "khz": DIM_FREQUENCY,
    "kilohertz": DIM_FREQUENCY,
    "mhz": DIM_FREQUENCY,
    "megahertz": DIM_FREQUENCY,
    "ghz": DIM_FREQUENCY,
    "gigahertz": DIM_FREQUENCY,
    "thz": DIM_FREQUENCY,
    "rpm": DIM_FREQUENCY,

    # Mass & Particle Units
    "mg": DIM_MASS,
    "milligram": DIM_MASS,
    "milligrams": DIM_MASS,
    "ug": DIM_MASS,
    "microgram": DIM_MASS,
    "micrograms": DIM_MASS,
    "ng": DIM_MASS,
    "nanogram": DIM_MASS,
    "pg": DIM_MASS,
    "tonne": DIM_MASS,
    "tonnes": DIM_MASS,
    "ton": DIM_MASS,
    "tons": DIM_MASS,
    "amu": DIM_MASS,
    "u": DIM_MASS,
    "da": DIM_MASS,
    "dalton": DIM_MASS,
    "daltons": DIM_MASS,

    # Force & Pressure
    "n": DIM_FORCE,
    "newton": DIM_FORCE,
    "newtons": DIM_FORCE,
    "kn": DIM_FORCE,
    "kilonewton": DIM_FORCE,
    "mn": DIM_FORCE,
    "millinewton": DIM_FORCE,
    "dyn": DIM_FORCE,
    "dyne": DIM_FORCE,
    "dynes": DIM_FORCE,
    "pa": DIM_PRESSURE,
    "pascal": DIM_PRESSURE,
    "pascals": DIM_PRESSURE,
    "kpa": DIM_PRESSURE,
    "kilopascal": DIM_PRESSURE,
    "kilopascals": DIM_PRESSURE,
    "mpa": DIM_PRESSURE,
    "megapascal": DIM_PRESSURE,
    "gpa": DIM_PRESSURE,
    "bar": DIM_PRESSURE,
    "bars": DIM_PRESSURE,
    "mbar": DIM_PRESSURE,
    "millibar": DIM_PRESSURE,
    "atm": DIM_PRESSURE,
    "atmosphere": DIM_PRESSURE,
    "atmospheres": DIM_PRESSURE,
    "torr": DIM_PRESSURE,
    "torrs": DIM_PRESSURE,
    "mmhg": DIM_PRESSURE,
    "psi": DIM_PRESSURE,

    # Energy & Power
    "j": DIM_ENERGY,
    "joule": DIM_ENERGY,
    "joules": DIM_ENERGY,
    "kj": DIM_ENERGY,
    "kilojoule": DIM_ENERGY,
    "kilojoules": DIM_ENERGY,
    "mj": DIM_ENERGY,
    "megajoule": DIM_ENERGY,
    "gj": DIM_ENERGY,
    "ev": DIM_ENERGY,
    "electronvolt": DIM_ENERGY,
    "electronvolts": DIM_ENERGY,
    "kev": DIM_ENERGY,
    "kiloelectronvolt": DIM_ENERGY,
    "mev": DIM_ENERGY,
    "megaelectronvolt": DIM_ENERGY,
    "gev": DIM_ENERGY,
    "gigaelectronvolt": DIM_ENERGY,
    "tev": DIM_ENERGY,
    "teraelectronvolt": DIM_ENERGY,
    "erg": DIM_ENERGY,
    "ergs": DIM_ENERGY,
    "cal": DIM_ENERGY,
    "calorie": DIM_ENERGY,
    "calories": DIM_ENERGY,
    "kcal": DIM_ENERGY,
    "kilocalorie": DIM_ENERGY,
    "ry": DIM_ENERGY,
    "rydberg": DIM_ENERGY,
    "hartree": DIM_ENERGY,
    "w": DIM_POWER,
    "watt": DIM_POWER,
    "watts": DIM_POWER,
    "mw": DIM_POWER,
    "milliwatt": DIM_POWER,
    "kw": DIM_POWER,
    "kilowatt": DIM_POWER,
    "kilowatts": DIM_POWER,
    "gw": DIM_POWER,
    "tw": DIM_POWER,

    # Electromagnetism
    "c": DIM_CHARGE,
    "coulomb": DIM_CHARGE,
    "coulombs": DIM_CHARGE,
    "mc": DIM_CHARGE,
    "uc": DIM_CHARGE,
    "nc": DIM_CHARGE,
    "pc_charge": DIM_CHARGE,
    "v": DIM_VOLTAGE,
    "volt": DIM_VOLTAGE,
    "volts": DIM_VOLTAGE,
    "mv": DIM_VOLTAGE,
    "millivolt": DIM_VOLTAGE,
    "kv": DIM_VOLTAGE,
    "kilovolt": DIM_VOLTAGE,
    "kilovolts": DIM_VOLTAGE,
    "ma": DIM_CURRENT,
    "milliamp": DIM_CURRENT,
    "milliampere": DIM_CURRENT,
    "ua": DIM_CURRENT,
    "microamp": DIM_CURRENT,
    "na": DIM_CURRENT,
    "ohm": DIM_RESISTANCE,
    "ohms": DIM_RESISTANCE,
    "kohm": DIM_RESISTANCE,
    "kiloohm": DIM_RESISTANCE,
    "mohm": DIM_RESISTANCE,
    "megaohm": DIM_RESISTANCE,
    "siemens": DIM_CONDUCTANCE,
    "mho": DIM_CONDUCTANCE,
    "f": DIM_CAPACITANCE,
    "farad": DIM_CAPACITANCE,
    "farads": DIM_CAPACITANCE,
    "mf": DIM_CAPACITANCE,
    "uf": DIM_CAPACITANCE,
    "microfarad": DIM_CAPACITANCE,
    "nf": DIM_CAPACITANCE,
    "pf": DIM_CAPACITANCE,
    "henry": DIM_INDUCTANCE,
    "henries": DIM_INDUCTANCE,
    "mh": DIM_INDUCTANCE,
    "uh": DIM_INDUCTANCE,
    "nh": DIM_INDUCTANCE,
    "t": DIM_MAGNETIC_B,
    "tesla": DIM_MAGNETIC_B,
    "teslas": DIM_MAGNETIC_B,
    "mt": DIM_MAGNETIC_B,
    "ut": DIM_MAGNETIC_B,
    "gauss": DIM_MAGNETIC_B,
    "wb": DIM_MAGNETIC_FLUX,
    "weber": DIM_MAGNETIC_FLUX,

    # Volume, Area & Cross Section
    "l": DIM_VOLUME,
    "liter": DIM_VOLUME,
    "liters": DIM_VOLUME,
    "litre": DIM_VOLUME,
    "litres": DIM_VOLUME,
    "ml": DIM_VOLUME,
    "milliliter": DIM_VOLUME,
    "milliliters": DIM_VOLUME,
    "cc": DIM_VOLUME,
    "barn": DIM_AREA,
    "barns": DIM_AREA,
    "b": DIM_AREA,

    # Dimensionless & Angle Units
    "1": 1,
    "rad": 1,
    "radian": 1,
    "radians": 1,
    "sr": 1,
    "steradian": 1,
    "steradians": 1,
    "deg": 1,
    "degree": 1,
    "degrees": 1,
    "arcmin": 1,
    "arcsec": 1,
    "mas": 1,
    "count": 1,
    "counts": 1,
    "photon": 1,
    "photons": 1,
    "particle": 1,
    "particles": 1,
    "electron": 1,
    "electrons": 1,
    "proton": 1,
    "protons": 1,
    "neutron": 1,
    "neutrons": 1,
    "nucleon": 1,
    "nucleons": 1,
    "atom": 1,
    "atoms": 1,
    "molecule": 1,
    "molecules": 1,
    "state": 1,
    "states": 1,
    "mode": 1,
    "modes": 1,
    "event": 1,
    "events": 1,
    "cycle": 1,
    "cycles": 1,
    "channel": 1,
    "channels": 1,
    "quantum": 1,
    "quanta": 1,
    "bit": 1,
    "bits": 1,
    "byte": 1,
    "bytes": 1,
    "nat": 1,
    "nats": 1,
    "db": 1,
    "decibel": 1,
    "decibels": 1,
}

DIMENSIONLESS_SYNONYMS = {
    "dimensionless", "none", "n/a", "na", "null", "unitless", "-", "--",
    "pure number", "ratio", "arbitrary", "varies", "unspecified",
    "phase", "quantum number", "normalized", "probability", "amplitude",
    "constant", "factor", "pure", "a.u.", "au", "fraction", "index",
    "order", "spin", "parity", "multiplicity", "degeneracy", "scale factor",
    "dimensionless ratio", "dimensionless scalar", "pure scalar", "scalar"
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
    paren_match = re.search(r"\(([A-Za-z0-9/·⋅*^ _-]+)\)", raw_unit)
    if paren_match:
        cand = paren_match.group(1).strip()
        if cand.lower() not in DIMENSIONLESS_SYNONYMS:
            s = cand

    # Clean LaTeX macros: \mathrm{...}, \text{...}, \textnormal{...}
    s = re.sub(r"\\(?:mathrm|text|textnormal|textbf|textit)\{([^{}]+)\}", r" \1 ", s)

    # Normalize solar subscripts: _\odot, _{\odot}, \odot -> _sun
    s = s.replace(r"_{\odot}", "_sun").replace(r"_\odot", "_sun").replace(r"\odot", "_sun")

    # Clean LaTeX spacing: \,, \;, \quad, \qquad, ~, etc.
    s = re.sub(r"\\[,;!]|\\quad|\\qquad|~", " ", s)

    # Normalize unicode symbols:
    s = s.replace("µ", "u").replace("μ", "u")
    s = s.replace("Ω", "ohm").replace("\\Omega", "ohm")
    s = s.replace("Å", "angstrom").replace("\\AA", "angstrom")
    s = s.replace("°", "deg").replace("^{\\circ}", "deg")
    s = s.replace("%", "1")

    # Particle physics energy/c mass and momentum replacements
    # e.g., "GeV/c^2", "MeV/c**2", "eV/c^2" -> mass dimension (kg)
    s = re.sub(r"\b([a-zA-Z]*ev)\s*/\s*c\s*(?:\^|\*\*)\s*2\b", "kg", s, flags=re.IGNORECASE)
    # e.g., "GeV/c", "MeV/c" -> momentum dimension (kg * m / s)
    s = re.sub(r"\b([a-zA-Z]*ev)\s*/\s*c\b", "kg * m / s", s, flags=re.IGNORECASE)

    # Normalize multiplication dots: ·, ⋅, \cdot (do not break existing **)
    s = re.sub(r"[·⋅]|\s*\\cdot\s*", " * ", s)

    # Strip scientific notation multipliers like \times 10^3 or \times 10^{3}
    s = re.sub(r"\\times\s*10\^\{?[+-]?[0-9]+\}?", " ", s)

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

    # Tokenize by operators, signed numbers, and identifier tokens (including underscores)
    tokens = re.findall(r"[A-Za-z_]+|\*\*|\*|/|\(|\)|[+-]?[0-9]+(?:\.[0-9]+)?", clean)
    if not tokens:
        return None

    local_dict = {}
    converted_tokens = []

    for t in tokens:
        lower_t = t.lower()
        if lower_t in ATOMIC_UNITS:
            var_name = f"unit_{lower_t}"
            local_dict[var_name] = ATOMIC_UNITS[lower_t]
            converted_tokens.append(var_name)
        elif t in ("*", "/", "(", ")", "**") or re.match(r"^[+-]?[0-9]+(?:\.[0-9]+)?$", t):
            converted_tokens.append(t)
        else:
            # Unrecognized unit token
            return None

    # Insert implicit multiplications between adjacent operand tokens
    # Operands end with: unit_*, a number, or ')'
    # Operands start with: unit_*, or '('
    expr_tokens = []
    for i, tok in enumerate(converted_tokens):
        if i > 0:
            prev = converted_tokens[i - 1]
            prev_can_end = (prev.startswith("unit_") or prev == ")" or bool(re.match(r"^[+-]?[0-9]+(?:\.[0-9]+)?$", prev)))
            curr_can_start = (tok.startswith("unit_") or tok == "(")
            if prev_can_end and curr_can_start:
                expr_tokens.append("*")
        expr_tokens.append(tok)

    expr_str = " ".join(expr_tokens)

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


# Natural Units (hbar = c = k_B = 1) Single-Dimension Base
DIM_NATURAL_ENERGY = sympy.physics.units.energy


def get_natural_dimension_power(dim_expr: Any) -> Optional[int | float]:
    """
    Computes the single energy/mass dimension power d in natural units (hbar = c = k_B = 1):
        d_nat = M - L - T + Theta + I
    Returns:
        int or float power of [E]^d, or None if unparseable.
    """
    if dim_expr == 1 or dim_expr is None:
        return 0

    powers = get_dimension_signature(dim_expr)
    if not powers and dim_expr != 1:
        return 0

    m = powers.get("M", 0)
    l = powers.get("L", 0)
    t = powers.get("T", 0)
    theta = powers.get("Theta", 0)
    i = powers.get("I", 0)

    d = m - l - t + theta + i
    return int(d) if (isinstance(d, (int, float)) and int(d) == d) else round(float(d), 2)


def parse_unit_string_natural(raw_unit: Optional[str]) -> Any:
    """
    Parses a unit string directly into a single Natural Units dimension [E]^d.
    """
    si_dim = parse_unit_string(raw_unit)
    if si_dim is None:
        return None
    d = get_natural_dimension_power(si_dim)
    if d == 0:
        return 1
    return DIM_NATURAL_ENERGY ** d
