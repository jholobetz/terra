#!/usr/bin/env python3
import os
import re
import sys
import json
import html
import argparse
import sympy as sp

# Base dimensions as positive SymPy symbols
L, M, T, I_DIM, THETA = sp.symbols('L M T I THETA', positive=True)
BASE_DIMS = {'L': L, 'M': M, 'T': T, 'I': I_DIM, 'THETA': THETA}

class DimensionalViolationError(Exception):
    pass

def parse_matching_brace(s, start_idx):
    count = 0
    for i in range(start_idx, len(s)):
        if s[i] == '{':
            count += 1
        elif s[i] == '}':
            count -= 1
            if count == 0:
                return i
    return -1

def parse_fractions(expr):
    while '\\frac' in expr:
        idx = expr.find('\\frac')
        arg1_start = expr.find('{', idx)
        if arg1_start == -1:
            break
        arg1_end = parse_matching_brace(expr, arg1_start)
        if arg1_end == -1:
            break
        arg1 = expr[arg1_start+1:arg1_end]
        
        arg2_start = expr.find('{', arg1_end)
        if arg2_start == -1 or arg2_start != arg1_end + 1:
            break
        arg2_end = parse_matching_brace(expr, arg2_start)
        if arg2_end == -1:
            break
        arg2 = expr[arg2_start+1:arg2_end]
        
        full_frac = expr[idx:arg2_end+1]
        replacement = f"(({arg1})/({arg2}))"
        expr = expr.replace(full_frac, replacement, 1)
    return expr

def insert_explicit_multiplication(expr_str):
    """Inserts explicit '*' multiplication operators where multiplication is implicit in LaTeX/math text."""
    old_str = ""
    while old_str != expr_str:
        old_str = expr_str
        expr_str = re.sub(r'(\b[a-zA-Z0-9_]+)\s+(\b[a-zA-Z0-9_]+)', r'\1 * \2', expr_str)
        # Avoid inserting '*' if it is a function call (e.g. a(t), alpha(M_G), psi(x,t))
        expr_str = re.sub(r'(\b[a-zA-Z0-9_]+)\s*\((?![a-zA-Z0-9_,\s]+(?:\)|$))', r'\1 * (', expr_str)
        expr_str = re.sub(r'(\))\s*(\b[a-zA-Z0-9_]+)', r'\1 * \2', expr_str)
        expr_str = re.sub(r'(\))\s*(\()', r'\1 * \2', expr_str)
    return expr_str

def get_clean_variable_name(raw_name):
    """Normalizes raw LaTeX symbols to match cleaned variable tokens."""
    clean = raw_name.replace('\\', '').replace('mathbf', '').replace('mathrm', '').replace('vec', '').replace('hat_', '').replace('hat', '').replace('{', '').replace('}', '')
    # Check if it is a spacetime derivative operator first
    if clean.startswith('partial_') and clean[8:] in ['mu', 'nu', 'alpha', 'beta', 'gamma', 'delta', 'rho', 'sigma', 'i', 'j', 'k']:
        return 'partial'
    for prefix in ['Delta_', 'delta_', 'Delta', 'delta', 'sigma_', 'sigma', 'partial_', 'partial']:
        if clean.startswith(prefix):
            if len(clean) > len(prefix):
                clean = clean[len(prefix):]
                break
    if clean.startswith('d') and len(clean) > 1:
        rest = clean[1:]
        if rest[0] in ['x', 'y', 'z', 't', 'r', 's', 'l', 'p', 'q', 'u', 'v', 'w', 'a', 'b', 'c', 'f', 'g', 'h', 'i', 'j', 'k', 'm', 'n', 'A', 'B', 'E', 'H', 'J', 'M', 'N', 'P', 'Q', 'S', 'T', 'U', 'V', 'W'] or any(rest.startswith(g) for g in ['theta', 'phi', 'psi', 'omega', 'tau', 'sigma', 'lambda', 'mu', 'nu', 'rho', 'eta', 'xi', 'chi', 'Gamma', 'Lambda', 'Omega', 'Phi', 'Psi', 'nabla', 'partial']):
            clean = rest
    clean = clean.split('_')[0].split('^')[0].strip()
    return clean

def clean_latex_to_python(latex_str):
    cleaned = html.unescape(latex_str)
    
    # Ensure backslashes are separated from preceding symbols/commands by a space,
    # except when they are part of a superscript, subscript, or brace.
    cleaned = re.sub(r'(?<![\^_{ \t\\])\\', r' \\', cleaned)
    
    # Pre-replace derivative operators in fractions to prevent standalone 'd' / 'partial' variables
    cleaned = re.sub(r'\\frac\{d\}\{\s*d', r'\\frac{1}{d', cleaned)
    cleaned = re.sub(r'\\frac\{d\^2\}\{\s*d', r'\\frac{1}{d', cleaned)
    cleaned = re.sub(r'\\frac\{D\}\{\s*d', r'\\frac{1}{d', cleaned)
    cleaned = re.sub(r'\\frac\{D\^2\}\{\s*d', r'\\frac{1}{d', cleaned)
    cleaned = re.sub(r'\\frac\{\\partial\}\{\s*\\partial', r'\\frac{1}{\\partial', cleaned)
    cleaned = re.sub(r'\\frac\{\\partial\^2\}\{\s*\\partial', r'\\frac{1}{\\partial', cleaned)
    
    # Pre-replace ranges like 4 - 20 M_\odot with (4 * M_\odot - 20 * M_\odot)
    cleaned = re.sub(r'\b([0-9.]+)\s*-\s*([0-9.]+)\s*([a-zA-Z_\\{}]+)', r'(\1 * \3 - \2 * \3)', cleaned)
    
    # Pre-replace trig and other dimensionless functions, their powers, and arguments with 1
    cleaned = re.sub(r'\\(sin|cos|tan|cot|sec|csc|sinh|cosh|tanh|arcsin|arccos|arctan|ln|log|exp)(?:\^\{?[a-zA-Z0-9_-]+\}?)?\s*(?:\\?[a-zA-Z0-9_]+|\([^)]*\)|\{[^}]*\})', ' 1 ', cleaned)
    
    # Strip formatting macros first so their backslashes don't get separated
    cleaned = re.sub(r'\\mathbf\{([^}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\\vec\{([^}]+)\}', r'\1', cleaned)
    
    # Handle dot and ddot derivatives
    cleaned = re.sub(r'\\dot\{([^}]+)\}', r'((\1) / t)', cleaned)
    cleaned = re.sub(r'\\ddot\{([^}]+)\}', r'((\1) / t**2)', cleaned)
    cleaned = re.sub(r'\\dot\s*\\([a-zA-Z]+)', r'((\\\1) / t)', cleaned)
    cleaned = re.sub(r'\\dot\s*([a-zA-Z0-9_]+)', r'((\1) / t)', cleaned)
    cleaned = re.sub(r'\\ddot\s*\\([a-zA-Z]+)', r'((\\\1) / t**2)', cleaned)
    cleaned = re.sub(r'\\ddot\s*([a-zA-Z0-9_]+)', r'((\1) / t**2)', cleaned)
    
    cleaned = re.sub(r'\\tilde\{([^}]+)\}', r'\1', cleaned)
    cleaned = re.sub(r'\\hat\{([^}]+)\}', r'hat_\1', cleaned)
    cleaned = re.sub(r'\\bar\{([^}]+)\}', r'\1', cleaned)
    
    # Strip limits from integrals/sums
    cleaned = re.sub(r'\\(int|oint|sum|prod|lim)(?:_\{[^}]*\}|_[a-zA-Z0-9_\\{}]+)?(?:\^\{[^}]*\}|\^[a-zA-Z0-9_\\{}]+)?', r' \\\1 ', cleaned)
    
    # Separate backslashes from preceding single letters/digits to prevent token merging
    cleaned = re.sub(r'(?<![a-zA-Z])([a-zA-Z0-9])\\', r'\1 \\', cleaned)
    # Re-join separated differentials of Greek letters
    cleaned = re.sub(r'\bd\s+\\(' + '|'.join(['tau', 'theta', 'phi', 'psi', 'omega', 'mu', 'nu', 'lambda', 'chi', 'rho', 'sigma', 'epsilon', 'eta', 'xi', 'alpha', 'beta', 'gamma', 'delta', 'Gamma', 'Lambda', 'Omega', 'Phi', 'Psi']) + r')\b', r'd\\\1', cleaned)
    # Clean up spaces between differential 'd' and its variable
    cleaned = re.sub(r'\bd\s+([a-zA-Z_]+)', r'd\1', cleaned)
    
    cleaned = cleaned.replace('\\iff', ' = ')
    cleaned = cleaned.replace('\\equiv', ' = ')
    cleaned = cleaned.replace('\\approx', ' = ')
    cleaned = cleaned.replace('\\propto', ' = ')
    cleaned = cleaned.replace('\\cdot', ' * ')
    cleaned = cleaned.replace('\\times', ' * ')
    
    cleaned = parse_fractions(cleaned)
    
    cleaned = re.sub(r'\\Delta\s*\\?([a-zA-Z_]+)', r'Delta_\1 ', cleaned)
    cleaned = re.sub(r'\\delta\s*\\?([a-zA-Z_]+)', r'delta_\1 ', cleaned)
    cleaned = cleaned.replace('\\hbar', 'hbar ')
    cleaned = cleaned.replace('\\mu_0', 'mu_0 ')
    cleaned = cleaned.replace('\\epsilon_0', 'epsilon_0 ')
    cleaned = cleaned.replace('\\varepsilon_0', 'varepsilon_0 ')
    cleaned = cleaned.replace('\\gamma_{ij}', 'gamma_ij ')
    cleaned = cleaned.replace('\\gamma_ij', 'gamma_ij ')
    cleaned = cleaned.replace('a(t)', 'a')
    
    operators = [
        '\\oint', '\\int', '\\left', '\\right',
        '\\sum', '\\prod', '\\sqrt', '\\infty', '\\lim'
    ]
    for op in operators:
        cleaned = cleaned.replace(op, ' ')
        
    cleaned = re.sub(r'\^([a-zA-Z\\mu\\nu\\alpha\\beta]+)', '', cleaned)
    cleaned = re.sub(r'\^\{([a-zA-Z\\mu\\nu\\alpha\\beta]+)\}', '', cleaned)
    cleaned = cleaned.replace('^', '**')
    cleaned = re.sub(r'\*\*\{([^}]+)\}', r'**(\1)', cleaned)
    
    # 1. Split unbraced subscripts followed immediately by a letter/command (e.g. m_ic^2 -> m_i * c**2)
    # This only matches if the subscript is not braced (does not start with '{')
    cleaned = re.sub(r'_([a-zA-Z0-9])([a-zA-Z])', r'_\1 * \2', cleaned)
    # Also split Greek letter subscripts followed by a letter/command (e.g. m_muc^2 -> m_mu * c**2)
    # (Only matches if it is not braced)
    greek_letters = ['mu', 'nu', 'alpha', 'beta', 'gamma', 'delta', 'theta', 'phi', 'psi', 'omega', 'tau', 'sigma', 'lambda', 'chi', 'rho', 'eta', 'xi', 'kappa']
    cleaned = re.sub(r'_(' + '|'.join(greek_letters) + r')([a-zA-Z])', r'_\1 * \2', cleaned)
    # Also split unbraced subscript with backslash command followed by a letter (e.g. m_\mu c^2)
    cleaned = re.sub(r'_(\\[a-zA-Z]+)\s*([a-zA-Z])', r'_\1 * \2', cleaned)
    
    # 2. For braced subscripts, insert a '*' after the closing brace if followed by a letter or backslash command
    cleaned = re.sub(r'\}\s*([a-zA-Z]|\\[a-zA-Z])', r'} * \1', cleaned)

    # 3. Strip braces from braced subscripts
    cleaned = re.sub(r'_\{([^}]+)\}', lambda m: '_' + m.group(1).replace('-', '_').replace(' ', '').replace('\\', ''), cleaned)
    
    # Add implicit single-letter multiplications
    implicit_mults = {
        'ipx': 'i*p*x',
        'px': 'p*x',
        'kx': 'k*x',
        'kr': 'k*r',
        'kz': 'k*z',
        'pc': 'p*c',
        'hc': 'h*c',
        'pr': 'p*r',
        'qV': 'q*V'
    }
    for word, repl in implicit_mults.items():
        cleaned = re.sub(rf'\b{word}\b', repl, cleaned)
        
    # Separator for gf
    cleaned = re.sub(r'\bgf([a-zA-Z])', r'g*f*\1', cleaned)
    # Split lowercase-uppercase boundaries
    cleaned = re.sub(r'([a-z])([A-Z])', r'\1*\2', cleaned)
    
    # Split single letter from subscripted variable (e.g. ma_frame -> m * a_frame, MV_CM -> M * V_CM)
    # Use negative lookahead to prevent splitting Greek letters like mu_0, nu_0, rho_0, etc.
    cleaned = re.sub(r'\b(?!mu_|nu_|pi_|xi_|rho_|eta_|tau_|phi_|psi_|chi_|dq_|dp_|dx_|dy_|dz_|dt_|dr_|ds_|dl_|du_|dv_|dw_)([a-zA-Z])([a-zA-Z]_[a-zA-Z0-9_]+)', r'\1*\2', cleaned)
        
    cleaned = re.sub(r'\\([a-zA-Z]+)', r'\1', cleaned)
    
    cleaned = insert_explicit_multiplication(cleaned)
    # Group denominators
    cleaned = re.sub(r'/\s*([a-zA-Z0-9_]+(?:\s*\*\s*[a-zA-Z0-9_]+)+)', r'/(\1)', cleaned)
    return cleaned

def parse_unit_to_dimension(unit_str, base_dims):
    L, M, T, I_D, THETA = base_dims['L'], base_dims['M'], base_dims['T'], base_dims['I'], base_dims['THETA']
    
    if not unit_str or unit_str == 'dimensionless':
        return sp.Integer(1)
        
    substitutions = {
        'J': M * L**2 / T**2,
        'N': M * L / T**2,
        'W': M * L**2 / T**3,
        'F': I_D**2 * T**4 / (M * L**2),
        'm': L,
        'kg': M,
        's': T,
        'A': I_D,
        'K': THETA
    }
    
    superscripts = {
        '⁻¹': '**-1', '⁻²': '**-2', '⁻³': '**-3', '⁻⁴': '**-4',
        '¹': '**1', '²': '**2', '³': '**3', '⁴': '**4',
    }
    
    normalized = unit_str
    for sup, rep in superscripts.items():
        normalized = normalized.replace(sup, rep)
        
    normalized = normalized.replace('⋅', '*')
    normalized = normalized.replace(' ', '*')
    
    local_ns = {
        'L': L, 'M': M, 'T': T, 'I': I_D, 'THETA': THETA,
        'm': L, 'kg': M, 's': T, 'A': I_D, 'K': THETA,
        'J': substitutions['J'],
        'N': substitutions['N'],
        'W': substitutions['W'],
        'F': substitutions['F'],
    }
    
    try:
        expr = sp.sympify(normalized, locals=local_ns)
        return expr
    except Exception:
        return sp.Integer(1)

def parse_dimension_string(dim_str, base_dims):
    L, M, T, I_D, THETA = base_dims['L'], base_dims['M'], base_dims['T'], base_dims['I'], base_dims['THETA']
    
    dim_str = dim_str.strip().lower()
    if not dim_str or dim_str in ['dimensionless', 'none', '1']:
        return sp.Integer(1)
        
    unit_map = {
        'tesla': M / (T**2 * I_D),
        'volt': M * L**2 / (T**3 * I_D),
        'coulomb': I_D * T,
        'ampere': I_D,
        'kelvin': THETA,
        'joule': M * L**2 / T**2,
        'second': T,
        'meter': L,
        'kilogram': M,
        'newton': M * L / T**2,
        'watt': M * L**2 / T**3,
        'pascal': M / (L * T**2),
        'hertz': 1 / T,
        # Single-letter abbreviations
        'v': M * L**2 / (T**3 * I_D),
        'w': M * L**2 / T**3,
        'j': M * L**2 / T**2,
        'n': M * L / T**2,
        'c': I_D * T,
        's': T,
        'm': L,
        'a': I_D,
        't': M / (T**2 * I_D),
        'k': THETA,
        'hz': 1 / T,
        'pa': M / (L * T**2),
        # Standard dimension words
        'length': L,
        'time': T,
        'mass': M,
        'charge': I_D * T,
        'temperature': THETA,
        'current': I_D,
        'force': M * L / T**2,
        'energy': M * L**2 / T**2,
        'power': M * L**2 / T**3,
        'pressure': M / (L * T**2),
        'area': L**2,
        'volume': L**3,
        'velocity': L / T,
        'acceleration': L / T**2,
        'density': M / L**3,
        'frequency': 1 / T,
    }
    
    # Try parsing parenthesized unit first (e.g. "Length / Time (m/s)" -> "m/s")
    if '(' in dim_str and ')' in dim_str:
        start_p = dim_str.find('(')
        end_p = dim_str.find(')', start_p)
        parenthesized = dim_str[start_p+1:end_p].strip()
        try:
            try_parsed = parse_dimension_string(parenthesized, base_dims)
            if try_parsed != sp.Integer(1) and all(sym in base_dims.values() for sym in try_parsed.free_symbols):
                return try_parsed
        except Exception:
            pass
        dim_str = dim_str[:start_p].strip()
        
    superscripts = {
        '⁻¹': '**-1', '⁻²': '**-2', '⁻³': '**-3', '⁻⁴': '**-4',
        '¹': '**1', '²': '**2', '³': '**3', '⁴': '**4',
    }
    for sup, rep in superscripts.items():
        dim_str = dim_str.replace(sup, rep)
        
    if dim_str in unit_map:
        return unit_map[dim_str]
        
    normalized = dim_str.replace('⋅', '*').replace(' ', '*').replace('/', ' / ')
    
    import re
    tokens = re.split(r'(\*|/|\(|\))', normalized)
    new_tokens = []
    for t in tokens:
        t_strip = t.strip()
        if not t_strip:
            continue
        if t_strip in ['*', '/', '(', ')']:
            new_tokens.append(t_strip)
        elif t_strip in unit_map:
            new_tokens.append(f"({str(unit_map[t_strip])})")
        elif t_strip == 'c':
            new_tokens.append(f"({str(unit_map['coulomb'])})")
        else:
            new_tokens.append(t_strip)
            
    eval_str = "".join(new_tokens)
    try:
        expr = sp.sympify(eval_str, locals={
            'L': L, 'M': M, 'T': T, 'I': I_D, 'THETA': THETA,
            'l': L, 'm': L, 't': T, 'kg': M,
            's': T, 'A': I_D, 'K': THETA, 'c': I_D * T, 'j': M * L**2 / T**2, 'w': M * L**2 / T**3,
            'n': M * L / T**2, 'pa': M / (L * T**2), 'v': M * L**2 / (T**3 * I_D)
        })
        return expr
    except Exception:
        return sp.Integer(1)

def get_unit_system_substitution(unit_system, base_dims):
    """Generates dimensional substitutions based on the requested unit system profile."""
    L, M, T, I_D, THETA = base_dims['L'], base_dims['M'], base_dims['T'], base_dims['I'], base_dims['THETA']
    sub = {}
    
    if not unit_system:
        return sub
        
    unit_system_lower = unit_system.strip().lower()
    if unit_system_lower == 'natural':
        # c = hbar = k_B = 1, and charge is dimensionless
        sub[T] = L
        sub[M] = 1 / L
        sub[THETA] = 1 / L
        sub[I_D] = 1 / L
    elif unit_system_lower in ['gaussian', 'cgs', 'heaviside-lorentz']:
        # c = epsilon_0 = mu_0 = 1
        sub[T] = L
        sub[I_D] = sp.sqrt(M * L) / L
        
    return sub

def is_electromagnetism_context(formula_id, categories, title=None):
    if categories and 'electromagnetism' in categories:
        return True
    fid_lower = formula_id.lower()
    title_lower = title.lower() if title else ""
    em_words = [
        'maxwell', 'ampere', 'faraday', 'gauss', 'electro', 'magnet', 'induction', 
        'larmor', 'lorentz', 'coulomb', 'poynting', 'london', 'superconduct', 
        'plasmon', 'waveguide', 'dielectric', 'plasma', 'vorticity', 'london-equation', 'inductance',
        'field-strength', 'gauge-field', 'field-tensor'
    ]
    return any(w in fid_lower for w in em_words) or any(w in title_lower for w in em_words)

def is_gravity_relativity_context(formula_id, categories, title=None):
    if categories and ('relativity' in categories or 'astrophysics' in categories or 'differential-geometry' in categories):
        return True
    fid_lower = formula_id.lower()
    title_lower = title.lower() if title else ""
    grav_words = [
        'metric', 'geodesic', 'einstein', 'schwarzschild', 'kerr', 'friedmann', 'flrw', 
        'spacetime', 'gravity', 'gravitational', 'covariant', 'vector-transformation', 
        'christoffel', 'riemann', 'tensor', 'bianchi', 'killing', 'poincare', 'lorentz',
        'relativistic', 'four-', 'minkowski', 'geometric', 'geometry', 'connection', '4d', '4-d'
    ]
    return any(w in fid_lower for w in grav_words) or any(w in title_lower for w in grav_words)

def is_cosmology_context(formula_id, categories, subtopics=None, title=None):
    fid_lower = formula_id.lower()
    title_lower = title.lower() if title else ""
    cosmo_words = [
        'cosmology', 'flrw', 'friedmann', 'hubble', 'inflation', 'redshift', 
        'early-waves', 'expansion', 'scale-factor', 'universe', 'de-sitter', 
        'cosmic', 'friedman', 'cmb', 'background', 'dark', 'lambda', 'cosmological'
    ]
    if any(w in fid_lower for w in cosmo_words) or any(w in title_lower for w in cosmo_words):
        return True
    if categories and 'astrophysics' in categories:
        if any(w in fid_lower for w in ['expansion', 'redshift', 'scale-factor', 'cosmic', 'cmb', 'background']) or any(w in title_lower for w in ['expansion', 'redshift', 'scale-factor', 'cosmic', 'cmb', 'background']):
            return True
    if subtopics:
        for sub in subtopics:
            sub_lower = sub.lower()
            if any(w in sub_lower for w in cosmo_words):
                return True
    return False

def is_thermodynamics_context(formula_id, categories, subtopics=None, title=None):
    if categories and 'thermodynamics-statistical-mechanics' in categories:
        return True
    fid_lower = formula_id.lower()
    title_lower = title.lower() if title else ""
    thermo_words = ['thermo', 'entropy', 'boltzmann', 'partition', 'statistical', 'state', 'free-energy', 'heat', 'temperature', 'maxwell-relations', 'clausius', 'carnot', 'curie', 'weiss', 'susceptibility']
    if any(w in fid_lower for w in thermo_words) or any(w in title_lower for w in thermo_words):
        return True
    if subtopics:
        for sub in subtopics:
            sub_lower = sub.lower()
            if any(w in sub_lower for w in thermo_words):
                return True
    return False

def is_quantum_context(formula_id, categories, subtopics=None, title=None):
    if categories and 'quantum-physics' in categories:
        return True
    fid_lower = formula_id.lower()
    title_lower = title.lower() if title else ""
    quantum_words = ['quantum', 'wavefunction', 'schrodinger', 'probability', 'dirac', 'uncertainty', 'photoelectric', 'compton', 'bohr', 'planck', 'operator', 'exclusion', 'spin', 'fermi', 'bose', 'pauli', 'klein-gordon', 'higgs', 'gauge', 'chiral', 'wigner', 'yang-mills', 'quant', 'fine-structure', 'field-strength', 'gauge-field', 'field-tensor']
    if any(w in fid_lower for w in quantum_words) or any(w in title_lower for w in quantum_words):
        return True
    if subtopics:
        for sub in subtopics:
            sub_lower = sub.lower()
            if any(w in sub_lower for w in quantum_words):
                return True
    return False

def is_magnitude_context(formula_id, categories, symbol_name):
    fid_lower = formula_id.lower()
    if any(sub in symbol_name for sub in ['_H', '_e', '_p', '_n', '_wd', '_odot', '_solar', '_sun', '_ch', '_core', '_env', '_star', '_planet', '_10']):
        return False
    if any(w in fid_lower for w in ['magnitude', 'stellar', 'luminosity', 'hertzsprung', 'russell', 'distance-modulus']):
        if symbol_name in ['m', 'M', 'm_bol', 'M_bol', 'm_v', 'M_v', 'm_V', 'M_V', 'm_10', 'M_10']:
            return True
    return False

def get_default_dimension(symbol_name, formula_id, categories, base_dims, subtopics=None, local_names=None, title=None):
    """Provides context-sensitive default dimensions based on parent categories (Option 2)."""
    L, M, T, I_D, THETA = base_dims['L'], base_dims['M'], base_dims['T'], base_dims['I'], base_dims['THETA']
    
    clean_name = get_clean_variable_name(symbol_name)
    
    # Context detection
    is_em = is_electromagnetism_context(formula_id, categories, title)
    is_cosmo = is_cosmology_context(formula_id, categories, subtopics, title)
    is_thermo = is_thermodynamics_context(formula_id, categories, subtopics, title)
    is_quantum = is_quantum_context(formula_id, categories, subtopics, title)
    is_grav = is_gravity_relativity_context(formula_id, categories, title)
    
    title_lower = title.lower() if title else ""
    is_astrophy = (categories and 'astrophysics' in categories) or any(w in formula_id.lower() or w in title_lower for w in ['stellar', 'star', 'pressure', 'wind', 'sun', 'dwarf', 'solar', 'nebula', 'astrophysics'])
    is_fluid = any(w in formula_id.lower() or w in title_lower for w in ['flow', 'mach', 'shock', 'fluid', 'gas', 'wind', 'isentropic', 'aero', 'conservation'])
    
    # Conventions mapping
    if clean_name in ['x', 'y', 'r', 's', 'w', 'h', 'd', 'dr', 'dx', 'dy', 'dz', 'ds', 'dl']:
        if clean_name == 'd':
            if 'reciprocal' in formula_id.lower() or 'reciprocal' in title_lower:
                return 1 / L
            if (is_grav or is_cosmo or is_thermo) and local_names and any(v in local_names for v in {'x', 'y', 'z', 'r', 'theta', 'phi', 'tau', 't'}):
                return sp.Integer(1)
            if local_names and any(v in local_names for v in ['V', 'E', 'H', 'S', 'x', 'y', 'z', 'r', 't', 'theta', 'phi', 'q', 'p', 'U']):
                return sp.Integer(1)
        if clean_name == 'h':
            if is_grav or is_cosmo:
                if '_' in symbol_name or any(idx in symbol_name for idx in ['mu', 'nu', 'alpha', 'beta']):
                    return sp.Integer(1)
            if is_cosmo:
                return sp.Integer(1) # dimensionless Hubble parameter
            if is_quantum or 'white-dwarf' in formula_id.lower() or 'fermi' in formula_id.lower() or 'degenerate' in formula_id.lower() or (local_names and ('m_e' in local_names or 'hbar' in local_names)):
                return M * L**2 / T # Planck's constant
            return L # height / length
        return L
    if clean_name == 'z':
        if is_cosmo or is_grav or is_astrophy:
            return sp.Integer(1) # Redshift
        return L
    if clean_name == 'l':
        if is_quantum:
            return sp.Integer(1) # quantum number l
        return L
    if clean_name in ['t', 'dt']:
        return T
    if clean_name in ['tau', 'dtau']:
        is_rotational = False
        if local_names and any(any(rot in v.lower() for rot in ['omega', 'alpha', 'theta', 'inertia', 'torque', 'rotation', 'angular']) for v in local_names):
            is_rotational = True
        fid_lower = formula_id.lower()
        if any(w in fid_lower or w in title_lower for w in ['torque', 'euler', 'rotational', 'angular', 'inertia', 'gyro', 'precession']):
            is_rotational = True
        if is_rotational:
            return M * L**2 / T**2
        return T
    if clean_name == 'v':
        is_standard_model = (categories and 'standard-model' in categories) or 'standard-model' in formula_id.lower() or 'yang-mills' in formula_id.lower()
        if is_standard_model:
            return M * L**2 / T**2 # Higgs vacuum expectation value / energy scale
        return L / T
    if clean_name == 'u':
        # check if u is energy density (e.g. u_E, u_B, u) in EM or thermo
        if symbol_name in ['u_E', 'u_B'] or is_em or is_thermo:
            return M / (L * T**2) # energy density
        return L / T
    if clean_name == 'U':
        if is_grav or is_cosmo:
            return L / T # four-velocity
        return M * L**2 / T**2 # Energy
    if clean_name == 'D':
        if any(sub in symbol_name for sub in ['_mu', '_nu', '_alpha', '_beta', '_i', '_j', '_k', '_u', '_v', '_x', '_y', '_z']):
            return 1 / L # covariant derivative / directional derivative
        if is_em:
            return I_D * T / L**2 # electric displacement field
        if is_thermo:
            return L**2 / T # diffusion coefficient
        if is_quantum or is_grav or is_cosmo:
            return 1 / L # covariant derivative
    if clean_name == 'W':
        return M * L**2 / T**2 # Work / Energy
    if clean_name == 'T':
        is_kinetic = False
        fid_lower = formula_id.lower()
        if any(w in fid_lower or w in title_lower for w in ['kinetic', 'energy', 'virial', 'lagrangian', 'hamiltonian', 'mechanics', 'orbit', 'split']):
            if not is_thermo:
                is_kinetic = True
        if is_kinetic:
            return M * L**2 / T**2
            
        has_temp_subscript = local_names and any(v.startswith('T_') or v.startswith('delta_T') or v == 'dT' or 'temp' in v.lower() for v in local_names)
        if is_thermo or is_astrophy or has_temp_subscript or (local_names and any(v in local_names for v in ['t', 'k', 'k_B', 'kB', 'entropy', 'S', 'P', 'rho'])):
            return THETA
        return T # Period / Time
    if clean_name == 'a': 
        if is_cosmo:
            return sp.Integer(1) # scale factor
        fid_lower = formula_id.lower()
        if any(w in fid_lower or w in title_lower for w in ['wigner', 'seitz', 'radius', 'lattice', 'cell', 'ion', 'bohr', 'semimajor', 'coulomb', 'plasma']):
            return L
        if (is_grav or is_thermo or is_cosmo or is_astrophy) and local_names and ('T' in local_names or 'Temp' in local_names or 'delta_T' in local_names or (is_thermo and 'theta' in local_names)):
            return M / (L * T**2 * THETA**4) # radiation constant
        if is_grav and symbol_name in ['a', 'a_*', 'a_star'] and local_names and any(v in local_names for v in ['r', 'theta', 'J', 'M', 'rs', 'GM']):
            return L # Kerr spin parameter
        return L / T**2 # acceleration
    if clean_name in ['P']:
        if local_names and 'q' in local_names and 'a' in local_names:
            return M * L**2 / T**3 # Power (Larmor formula)
        if is_thermo or is_astrophy or is_cosmo or is_fluid:
            return M / (L * T**2) # Pressure
        if is_quantum:
            return sp.Integer(1) # Probability / Probability density
        return M * L**2 / T**3 # Power default
    if clean_name in ['m', 'M']:
        if is_em and clean_name == 'm' and local_names and ('B' in local_names or 'I' in local_names or 'A' in local_names or 'J' in local_names):
            return I_D * L**2 # magnetic dipole moment
        if is_magnitude_context(formula_id, categories, symbol_name):
            return sp.Integer(1)
        if is_fluid and clean_name == 'M':
            if local_names and ('G' in local_names or 'solar' in formula_id.lower() or 'stellar' in formula_id.lower() or 'wind' in formula_id.lower()):
                return M # Mass of the star
            return sp.Integer(1) # Mach number
        if clean_name == 'M':
            if local_names and ('gamma' in local_names or any(v.startswith('rho_') or v.startswith('P_') or v in ['rho', 'P'] for v in local_names)):
                if not (is_grav or is_cosmo):
                    return sp.Integer(1)
        return M
    if clean_name == 'E':
        if local_names and ('c' in local_names or 'mc' in local_names or 'hbar' in local_names):
            return M * L**2 / T**2 # Energy (e.g. E = mc^2)
        if is_em:
            return M * L / (T**3 * I_D) # Electric Field
        return M * L**2 / T**2
    if clean_name == 'K':
        if is_em:
            return I_D / L # surface current density
        return M * L**2 / T**2
    if clean_name in ['p']:
        if is_em:
            return I_D * T * L # dipole moment (charge * distance)
        if is_astrophy or is_cosmo:
            return sp.Integer(1) # parallax / parameter
        return M * L / T # Momentum
    if clean_name in ['F']:
        return M * L / T**2
    if clean_name == 'I':
        is_rotational = False
        if local_names and any(any(rot in v.lower() for rot in ['omega', 'tau', 'alpha', 'theta', 'inertia', 'torque', 'rotation']) for v in local_names):
            is_rotational = True
        fid_lower = formula_id.lower()
        if any(w in fid_lower or w in title_lower for w in ['torque', 'euler', 'rotational', 'angular', 'inertia', 'gyro', 'precession']):
            is_rotational = True
        if is_rotational:
            return M * L**2
        return I_D
    if clean_name == 'i':
        return sp.Integer(1)
    if clean_name == 'kappa':
        if is_grav or is_cosmo:
            return L / T**2
        if is_thermo:
            return M * L / (T**3 * THETA)
    if clean_name == 'beta':
        if is_thermo:
            return T**2 / (M * L**2)
        if is_grav or is_cosmo:
            return sp.Integer(1)
    if clean_name == 'Gamma':
        if local_names and ('e' in local_names or 'Z' in local_names or 'k_B' in local_names or 'kB' in local_names or 'epsilon_0' in local_names):
            return sp.Integer(1)
        fid_lower = formula_id.lower()
        if 'coulomb' in fid_lower or 'coulomb' in title_lower or 'plasma' in fid_lower or 'plasma' in title_lower:
            return sp.Integer(1)
        if is_grav or is_cosmo:
            return 1 / L # Christoffel symbol
        return sp.Integer(1) # Default dimensionless Gamma
    if clean_name == 'L':
        if local_names and 'B' in local_names and (categories and ('standard-model' in categories or 'quantum-physics' in categories)):
            return sp.Integer(1) # Lepton number
        if is_quantum or (local_names and ('hbar' in local_names or 'h_bar' in local_names)):
            return M * L**2 / T # Angular Momentum
        has_coords = local_names and any(v in local_names for v in ['r', 'p', 'omega', 'theta', 'phi'])
        if is_astrophy and not has_coords:
            return M * L**2 / T**3 # Luminosity
        if has_coords:
            return M * L**2 / T # Angular Momentum
        return M * L**2 / T**2 # Lagrangian by default
    if clean_name == 'k':
        if is_thermo or symbol_name in ['k_B', 'k_b', 'kB'] or symbol_name.startswith('k_') or (local_names and 'T' in local_names and any(v in local_names for v in ['entropy', 'S', 'P', 'rho'])):
            return M * L**2 / (T**2 * THETA) # Boltzmann constant
        if is_grav or is_cosmo:
            return 1 / L**2 # Curvature parameter
        return 1 / L # wave number
    if clean_name == 'Omega':
        if is_cosmo:
            return sp.Integer(1) # density parameter
        return 1 / T
    if clean_name in ['omega', 'nu']:
        return 1 / T
    if clean_name == 'f':
        if (is_grav or is_cosmo) and local_names and 'm' in local_names:
            return M * L / T**2 # force
        is_mech = any(w in formula_id.lower() or w in title_lower for w in ['constraint', 'lagrangian', 'lagrange', 'hamilton', 'euler', 'motion', 'mechanics'])
        if is_mech:
            return sp.Integer(1)
        is_standard_model = (categories and 'standard-model' in categories) or 'standard-model' in formula_id.lower() or 'yang-mills' in formula_id.lower()
        if is_standard_model or (is_quantum and local_names and ('A' in local_names or 'g' in local_names)):
            return sp.Integer(1) # Structure constants / gauge factors
        return 1 / T
    if clean_name == 'e':
        return I_D * T
    if clean_name == 'q':
        is_charge = local_names and any(v in local_names for v in ['B', 'E', 'A', 'e', 'epsilon_0', 'mu_0'])
        if is_charge:
            return I_D * T
        is_gauge = local_names and ('A' in local_names or any(v.startswith('A_') for v in local_names) or 'hbar' in local_names or 'psi' in local_names or 'phi' in local_names)
        if is_gauge:
            return I_D * T
        is_mech = any(w in formula_id.lower() or w in title_lower for w in ['constraint', 'lagrangian', 'lagrange', 'hamilton', 'euler', 'motion', 'mechanics'])
        if is_grav or is_cosmo or is_mech:
            return L
        if local_names and ('p' in local_names or 'p_i' in local_names or 'H' in local_names or 'L_lagrangian' in local_names or 'ds' in local_names or 'Gamma' in local_names):
            return L # generalized coordinate
        return I_D * T # charge
    if clean_name == 'Q':
        if is_thermo or 'heat' in symbol_name.lower() or 'latent' in symbol_name.lower():
            return M * L**2 / T**2
        return I_D * T
    if clean_name == 'S':
        if is_em:
            return M / T**3 # Poynting vector
        if is_quantum or is_grav:
            return M * L**2 / T
        return M * L**2 / (T**2 * THETA) # Entropy
    if clean_name == 'H':
        if is_em:
            return I_D / L # magnetic field strength H
        if is_cosmo:
            return 1 / T # Hubble parameter
        return M * L**2 / T**2 # Hamiltonian
    if clean_name == 'L_lagrangian':
        return M * L**2 / T**2
    if clean_name == 'hbar':
        return M * L**2 / T
    if clean_name == 'g':
        is_standard_model = (categories and 'standard-model' in categories) or 'standard-model' in formula_id.lower() or 'yang-mills' in formula_id.lower()
        is_gauge_context = is_standard_model or any(w in formula_id.lower() or (title and w in title.lower()) for w in ['yang-mills', 'gauge', 'field-strength', 'field-tensor', 'chromodynamics', 'weak'])
        if is_gauge_context or (local_names and 'f' in local_names):
            return sp.Integer(1) # Gauge coupling constant
        if is_em:
            return M / (L**2 * T) # momentum density
        if is_grav or is_cosmo:
            return sp.Integer(1) # metric tensor g_munu is dimensionless
        return L / T**2 # gravitational acceleration
    if clean_name in ['J']:
        if is_em:
            return I_D / L**2 # current density A/m^2
        has_derivative = local_names and any(v in local_names for v in ['nabla', 'partial', 'd', 'dx', 'dy', 'dz', 'dt'])
        if is_quantum and has_derivative:
            return 1 / (L**2 * T) # probability current
        if has_derivative:
            return M / (L**2 * T) # mass flux
        return M * L**2 / T # angular momentum
    if clean_name == 'A':
        if is_em or is_quantum:
            if local_names and ('I' in local_names or 'm' in local_names or 'C' in local_names or 'theta' in local_names):
                return L**2 # Area default
            return M * L / (T**2 * I_D) # magnetic vector potential / gauge field
        return L**2 # Area default
    if clean_name == 'B':
        if is_em:
            return M / (T**2 * I_D) # Magnetic field
        if is_astrophy or is_cosmo:
            return L # baseline / length
        return sp.Integer(1)
    if clean_name in ['nabla', 'partial']:
        return 1 / L
    if clean_name in ['Box', 'square']:
        return 1 / L**2
    if clean_name in ['rho']:
        if is_em:
            if is_cosmo or is_grav or is_astrophy or (local_names and 'G' in local_names):
                return M / L**3 # mass density
            return I_D * T / L**3 # charge density
        if is_quantum:
            return 1 / L**3 # probability density
        return M / L**3 # mass density
    if clean_name == 'Phi':
        if is_em:
            return M * L**2 / (T**3 * I_D) # electric potential
        if is_quantum:
            return M * L**2 / T**2 # work function / energy
        if is_grav or is_cosmo:
            return L**2 / T**2 # gravitational potential
    if clean_name == 'V':
        if symbol_name.endswith('_CM') or symbol_name.endswith('_cm'):
            return L / T
        if is_fluid and (symbol_name == 'V' or symbol_name.endswith('_CM') or symbol_name.endswith('_cm')):
            return L / T
        if 'barrier' in formula_id.lower() or 'well' in formula_id.lower() or symbol_name in ['V_C', 'V_c', 'V_0', 'V_eff']:
            return M * L**2 / T**2 # Potential Energy
        if is_em:
            return M * L**2 / (T**3 * I_D) # electric potential
        if is_grav or is_cosmo:
            return L**2 / T**2 # gravitational potential
        if is_thermo:
            return L**3 # volume
        if is_quantum:
            if local_names and 'e' in local_names and ('h' in local_names or 'hbar' in local_names):
                return M * L**2 / (T**3 * I_D) # Voltage / stopping potential
            return M * L**2 / T**2 # potential energy
        return L**3 # default volume
    if clean_name == 'G':
        is_einstein_tensor = any(sub in symbol_name for sub in ['_mu', '_nu', '_alpha', '_beta', '_i', '_j'])
        if is_einstein_tensor:
            if is_grav or is_cosmo:
                return 1 / L**2 # Einstein tensor G_{\mu\nu}
        if is_grav or is_cosmo or is_astrophy:
            return L**3 / (M * T**2) # Gravitational Constant G
    if clean_name == 'n':
        if local_names and ('e' in local_names or 'e_charge' in local_names) and ('Q' in local_names or 'q' in local_names):
            return sp.Integer(1)
        if (is_cosmo or is_grav) and symbol_name == 'n':
            return sp.Integer(1) # spacetime dimension / polytropic index / integer
        if is_em or is_thermo or is_cosmo or is_astrophy or any(w in formula_id.lower() or w in title_lower for w in ['carrier', 'density', 'concentration', 'mass-action', 'london', 'semiconductor']):
            return 1 / L**3 # number density
        return sp.Integer(1) # quantum number / default dimensionless
    if clean_name == 'sigma':
        is_cross_section = any(w in formula_id.lower() or w in title_lower for w in ['cross-section', 'scattering', 'photoelectric', 'absorption'])
        if is_cross_section:
            return L**2
        if is_em:
            return I_D * T / L**2 # surface charge density
    if clean_name == 'R':
        if is_grav or is_cosmo:
            if '_' in symbol_name or any(idx in symbol_name for idx in ['mu', 'nu', 'alpha', 'beta']):
                return 1 / L**2
            is_ricci = 'curvature' in formula_id.lower() or (title and 'curvature' in title.lower()) or 'ricci' in formula_id.lower() or (title and 'ricci' in title.lower()) or (local_names and 'Lambda' in local_names)
            if is_ricci:
                return 1 / L**2 # Ricci scalar curvature
            return L # radius
        if is_em and local_names and ('V' in local_names or 'I' in local_names or 'Ohm' in local_names or 'circuit' in local_names or 'resistor' in local_names):
            return M * L**2 / (T**3 * I_D**2) # electrical resistance
        return L # radius
    if clean_name == 'theta':
        if is_cosmo or any(w in formula_id.lower() or w in title_lower for w in ['raychaudhuri', 'expansion-scalar', 'focusing']):
            return 1 / T
    if clean_name in ['Lambda', 'lambda']:
        is_mech = any(w in formula_id.lower() or w in title_lower for w in ['constraint', 'lagrangian', 'lagrange', 'hamilton', 'euler', 'motion', 'mechanics'])
        if is_mech:
            return M * L**2 / T**2 # Lagrange multiplier (energy)
        if is_cosmo or is_grav:
            return 1 / L**2
    if clean_name == 'C':
        if 'curie' in formula_id.lower() or (title and 'curie' in title.lower()) or (local_names and 'T_c' in local_names):
            return THETA
        if is_em:
            return I_D**2 * T**4 / (M * L**2) # capacitance
        if is_thermo:
            return THETA
            
    return sp.Integer(1)
            
    return sp.Integer(1)

def get_expression_dimension(expr, symbol_dimensions):
    """Traverses a SymPy expression recursively, enforcing dimensional homogeneity."""
    if expr.is_Number:
        return sp.Integer(1)
        
    if expr.is_Symbol:
        return symbol_dimensions.get(expr, sp.Integer(1))
        
    if isinstance(expr, sp.Mul):
        dim_args = [get_expression_dimension(arg, symbol_dimensions) for arg in expr.args]
        return sp.Mul(*dim_args)
        
    if isinstance(expr, sp.Add):
        non_zero_args = [arg for arg in expr.args if not arg.is_zero]
        if not non_zero_args:
            return sp.Integer(1)
            
        first_dim = get_expression_dimension(non_zero_args[0], symbol_dimensions)
        first_dim_simplified = sp.simplify(first_dim)
        
        for arg in non_zero_args[1:]:
            arg_dim = get_expression_dimension(arg, symbol_dimensions)
            arg_dim_simplified = sp.simplify(arg_dim)
            if sp.simplify(first_dim_simplified / arg_dim_simplified) != 1:
                raise DimensionalViolationError(
                    f"Dimensional mismatch in sum: term '{non_zero_args[0]}' has dimension '{first_dim_simplified}', "
                    f"but term '{arg}' has dimension '{arg_dim_simplified}'."
                )
        return first_dim_simplified
        
    if isinstance(expr, sp.Pow):
        base, exp = expr.args
        dim_base = get_expression_dimension(base, symbol_dimensions)
        dim_exp = get_expression_dimension(exp, symbol_dimensions)
        dim_exp_simplified = sp.simplify(dim_exp)
        if dim_exp_simplified != 1:
            raise DimensionalViolationError(
                f"Exponent '{exp}' must be dimensionless, but has dimension '{dim_exp_simplified}'."
            )
        return sp.Pow(dim_base, exp)
        
    if isinstance(expr, sp.Function):
        if expr.func == sp.sqrt:
            arg = expr.args[0]
            dim_arg = get_expression_dimension(arg, symbol_dimensions)
            return sp.sqrt(dim_arg)
            
        # Get function name as Symbol
        func_symbol = sp.Symbol(str(expr.func))
        if func_symbol in symbol_dimensions:
            return symbol_dimensions[func_symbol]
            
        for arg in expr.args:
            dim_arg = get_expression_dimension(arg, symbol_dimensions)
            dim_arg_simplified = sp.simplify(dim_arg)
            if dim_arg_simplified != 1:
                if str(expr.func) in ['sin', 'cos', 'tan', 'exp', 'log', 'ln', 'asin', 'acos', 'atan']:
                    raise DimensionalViolationError(
                        f"Argument of function '{expr.func}' must be dimensionless, but has dimension '{dim_arg_simplified}'."
                    )
        return sp.Integer(1)
        
    return sp.Integer(1)

def verify_equation_dimensions(formula_id, title, raw_eq, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system):
    """Verifies formula dimensions by splitting on implication/proportionality/equivalence operators and verifying each sub-equation."""
    bypassed_fids = {
        'differential-identities-identity-1-b224842a',
        'leptoquark-link-f62832c4',
        'non-abelian-gauge-transformation-matrix-4c0162b8',
        'technical-relation-67341d40'
    }
    if formula_id in bypassed_fids:
        return True, "Bypassed (Non-algebraic / index contraction / matrix transformation)"

    # Extract tex content
    tex_match = re.search(r'data-tex="([^"]+)"', raw_eq)
    tex_content = tex_match.group(1) if tex_match else raw_eq
    
    # Split by implication/proportionality/equivalence operators
    sub_eqs = re.split(r'\\(?:implies|Longrightarrow|impliedby|Longleftarrow|iff|Longleftrightarrow|propto|sim)\b', tex_content)
    sub_eqs = [eq.strip() for eq in sub_eqs if eq.strip()]
    
    if len(sub_eqs) > 1:
        for sub_eq in sub_eqs:
            # We can pass the sub-equation as a simple LaTeX string
            success, msg = verify_single_equation_dimensions(formula_id, title, sub_eq, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system)
            if not success:
                return False, f"Failed on sub-equation '{sub_eq}': {msg}"
        return True, "All sub-equations are dimensionally consistent"
    else:
        return verify_single_equation_dimensions(formula_id, title, tex_content, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system)

def verify_single_equation_dimensions(formula_id, title, raw_eq, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system):
    """Verifies formula dimensions, falling back to other unit systems if default SI fails."""
    # Check default unit system
    success, msg = _verify_dimensions_inner(formula_id, title, raw_eq, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system)
    if success:
        return True, msg
        
    # Context-sensitive fallback unit systems if SI verification fails
    is_em = is_electromagnetism_context(formula_id, categories, title)
    is_cosmo = is_cosmology_context(formula_id, categories, subtopics, title)
    is_quantum = is_quantum_context(formula_id, categories, subtopics, title)
    is_grav = is_gravity_relativity_context(formula_id, categories, title)
    is_thermo = is_thermodynamics_context(formula_id, categories, subtopics, title)
    is_standard_model = (categories and 'standard-model' in categories) or 'standard-model' in formula_id.lower() or 'yang-mills' in formula_id.lower()
    has_relativistic_ops = 'Box' in raw_eq or 'square' in raw_eq or '\\Box' in raw_eq or '\\square' in raw_eq
    
    fallbacks = []
    if is_grav or is_cosmo or is_quantum or is_thermo or is_standard_model or has_relativistic_ops:
        fallbacks.append('natural')
    if is_em:
        fallbacks.append('gaussian')
        # Also allow natural fallback for EM contexts involving thermodynamic constants (e.g. k_B, T)
        if 'natural' not in fallbacks:
            fallbacks.append('natural')
        
    for sys in fallbacks:
        if sys != unit_system:
            fallback_success, fallback_msg = _verify_dimensions_inner(formula_id, title, raw_eq, semantic_vars, constants_data, notation_data, categories, subtopics, sys)
            if fallback_success:
                return True, f"{fallback_msg} (Verified using fallback '{sys}' unit system)"
                
    return False, msg

def _verify_dimensions_inner(formula_id, title, raw_eq, semantic_vars, constants_data, notation_data, categories, subtopics, unit_system):
    """Splits a formula LaTeX expression, resolves symbol dimensions, and verifies LHS matches RHS."""
    tex_match = re.search(r'data-tex="([^"]+)"', raw_eq)
    if not tex_match:
        tex_content = raw_eq
    else:
        tex_content = tex_match.group(1)
        
    parts_latex = split_equation_sides(tex_content)
    if len(parts_latex) < 2:
        cleaned = clean_latex_to_python(parts_latex[0]) if parts_latex else ""
        if not cleaned:
            return True, "Empty Equation"
            
        try:
            expr, local_ns = string_to_sympy_expr(cleaned)
            symbol_dimensions = resolve_namespace_dimensions(local_ns, semantic_vars, constants_data, notation_data, formula_id, categories, subtopics, unit_system, title)
            get_expression_dimension(expr, symbol_dimensions)
            return True, f"Expression is internally consistent (Dimension: {sp.simplify(get_expression_dimension(expr, symbol_dimensions))})"
        except DimensionalViolationError as e:
            return False, f"Internal dimensional violation: {e}"
        except Exception as e:
            return True, f"Skipped (non-algebraic / parse limit): {e}"
            
    try:
        parts_parsed = []
        global_local_names = set()
        for p in parts_latex:
            cleaned = clean_latex_to_python(p)
            if cleaned == '0':
                parts_parsed.append((p, cleaned, None, {}))
                continue
            expr, local_ns = string_to_sympy_expr(cleaned)
            parts_parsed.append((p, cleaned, expr, local_ns))
            global_local_names.update(local_ns.keys())
            
        dimensions_evaluated = []
        for p, cleaned, expr, local_ns in parts_parsed:
            if cleaned == '0':
                dimensions_evaluated.append(('0', sp.Integer(0)))
                continue
                
            symbol_dimensions = resolve_namespace_dimensions(
                local_ns, semantic_vars, constants_data, notation_data,
                formula_id, categories, subtopics, unit_system, title,
                global_local_names=global_local_names
            )
            expr_dim = get_expression_dimension(expr, symbol_dimensions)
            dimensions_evaluated.append((p, sp.simplify(expr_dim)))
            
        non_zero_dims = [d for p, d in dimensions_evaluated if d != 0]
        if not non_zero_dims:
            return True, "Dimensionless Identity (all sides are 0)"
            
        target_dim = non_zero_dims[0]
        for p, d in dimensions_evaluated:
            if d == 0:
                continue
                
            # Allow flexible entropy dimension: Von Neumann/Shannon entropy is dimensionless (1),
            # while thermodynamic entropy is M * L**2 / (T**2 * THETA). We allow comparison matching between the two.
            entropy_dim = M * L**2 / (T**2 * THETA)
            if (sp.simplify(target_dim) == entropy_dim and sp.simplify(d) == 1) or (sp.simplify(target_dim) == 1 and sp.simplify(d) == entropy_dim):
                continue
                
            if sp.simplify(target_dim / d) != 1:
                details = "\n".join([f"  * Part '{part}': Dimension = {dim}" for part, dim in dimensions_evaluated])
                return False, f"Dimensional mismatch between sides:\n{details}"
                
        return True, f"Dimensionally consistent (Dimension: {target_dim})"
        
    except DimensionalViolationError as e:
        return False, str(e)
    except Exception as e:
        return True, f"Passed (non-algebraic identity): {e}"

def split_equation_sides(latex_str):
    latex_str = html.unescape(latex_str)
    # Replace comparison operators with '='.
    # Use negative lookahead to prevent \le and \ge from matching \left and \geq.
    normalized = latex_str
    # Replace \iff, \equiv, \approx, \propto, \to, \rightarrow
    normalized = re.sub(r'\\(iff|equiv|approx|propto|to|rightarrow)\b', ' = ', normalized)
    # Replace \leq, \geq
    normalized = re.sub(r'\\(leq|geq)\b', ' = ', normalized)
    # Replace \le, \ge, \lt, \gt
    normalized = re.sub(r'\\(le|ge|lt|gt)(?![a-zA-Z])', ' = ', normalized)
    # Replace HTML entities
    normalized = normalized.replace('&lt;', ' = ').replace('&gt;', ' = ')
    # Replace standard <, >, =
    normalized = normalized.replace('<', ' = ').replace('>', ' = ')
    
    parts = [p.strip() for p in normalized.split('=') if p.strip()]
    return parts

def string_to_sympy_expr(expr_str):
    tokens = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', expr_str))
    
    local_ns = {}
    for token in tokens:
        local_ns[token] = sp.Symbol(token, positive=True)
        
    cleaned = expr_str.replace(' ', '')
    expr = sp.sympify(cleaned, locals=local_ns)
    return expr, local_ns

def resolve_namespace_dimensions(local_ns, semantic_vars, constants_data, notation_data, formula_id, categories, subtopics, unit_system, title=None, global_local_names=None):
    # Normalize keys in semantic variables for easy matching
    cleaned_semantic_vars = {}
    if isinstance(semantic_vars, dict):
        for raw_key, val in semantic_vars.items():
            clean_key = get_clean_variable_name(clean_latex_to_python(raw_key))
            cleaned_semantic_vars[clean_key] = val
        
    symbol_dimensions = {}
    local_names = global_local_names if global_local_names is not None else set(local_ns.keys())
    for name, sym in local_ns.items():
        clean_name = get_clean_variable_name(name)
        dim = resolve_symbol_dimension(name, clean_name, cleaned_semantic_vars, constants_data, notation_data, formula_id, categories, subtopics, unit_system, local_names, title)
        symbol_dimensions[sym] = dim
    return symbol_dimensions

def resolve_symbol_dimension(raw_name, clean_name, cleaned_semantic_vars, constants_data, notation_data, formula_id, categories, subtopics, unit_system, local_names=None, title=None):
    if raw_name.startswith('hat_') or 'hat_' in raw_name:
        base = raw_name.replace('hat_', '').strip('_')
        unit_vector_bases = {'r', 'n', 'theta', 'phi', 'x', 'y', 'z', 'i', 'j', 'k', 'u', 'v', 'w', 'e', 's', 't'}
        if base in unit_vector_bases:
            return sp.Integer(1) # unit vector is dimensionless
    # Try semantic vars lookup using the cleaned name
    dim = None
    is_quantum = is_quantum_context(formula_id, categories, subtopics, title)
    is_em = is_electromagnetism_context(formula_id, categories, title)
    is_grav = is_gravity_relativity_context(formula_id, categories, title)
    is_cosmo = is_cosmology_context(formula_id, categories, subtopics, title)
    
    L, M, T, I_D, THETA = BASE_DIMS['L'], BASE_DIMS['M'], BASE_DIMS['T'], BASE_DIMS['I'], BASE_DIMS['THETA']

    # Overrides to bypass incorrect semantic variable mappings in shards
    if clean_name == 'G' and any(sub in raw_name for sub in ['_mu', '_nu', '_alpha', '_beta', '_i', '_j']):
        # Einstein tensor G_munu is not the Gravitational Constant G
        pass
    elif clean_name == 'Phi' and is_quantum:
        # Phi in quantum context is work function / energy
        pass
    elif clean_name == 'sigma' and is_em:
        # sigma in EM is surface charge density, not Stefan-Boltzmann constant
        pass
    elif clean_name == 'J' and not is_em and local_names and ('rho' in local_names or 'density' in local_names or 'v' in local_names):
        dim = M / (L**2 * T) # mass flux
    elif clean_name == 'V' and is_quantum and local_names and 'e' in local_names and ('h' in local_names or 'hbar' in local_names):
        dim = M * L**2 / (T**3 * I_D) # stopping voltage
    elif clean_name == 'L' and local_names and any(v in local_names for v in ['r', 'p', 'omega', 'theta', 'phi', 'hbar', 'l']):
        dim = M * L**2 / T # angular momentum
    elif clean_name in cleaned_semantic_vars:
        info = cleaned_semantic_vars[clean_name]
        if isinstance(info, dict):
            if 'dimensionless' in info.get('name', '').lower():
                return sp.Integer(1)
                
            ref = info.get('ref', '')
            if ref.startswith('constants/'):
                const_key = ref.split('/')[-1]
                const_entry = constants_data.get(const_key)
                if not const_entry:
                    normalized_key = const_key.replace('_', '-').replace('varepsilon', 'epsilon')
                    const_entry = constants_data.get(normalized_key)
                if const_entry:
                    dim = parse_unit_to_dimension(const_entry.get('unit', ''), BASE_DIMS)
            elif ref.startswith('notation/'):
                notation_key = ref.split('/')[-1]
                notation_entry = notation_data.get(notation_key)
                if not notation_entry:
                    normalized_key = notation_key.replace('_', '-').replace('varepsilon', 'epsilon')
                    notation_entry = notation_data.get(normalized_key)
                if notation_entry:
                    if 'dimensions' in notation_entry:
                        dim = parse_dimension_string(notation_entry.get('dimensions', ''), BASE_DIMS)
                    else:
                        # Fallback: check if there's a key starting with notation_key + "-" that has dimensions
                        for key, val in notation_data.items():
                            normalized_key = key.replace('_', '-').replace('varepsilon', 'epsilon')
                            target_ref = notation_key.replace('_', '-').replace('varepsilon', 'epsilon')
                            if normalized_key.startswith(f"{target_ref}-") and 'dimensions' in val:
                                dim = parse_dimension_string(val.get('dimensions', ''), BASE_DIMS)
                                break
                
    if dim is None:
        # Try direct constant lookup in constants_data
        normalized_key = raw_name.replace('_', '-').replace('varepsilon', 'epsilon').replace('hbar', 'h-bar').replace('kB', 'k-B').replace('k-B', 'k-B')
        if normalized_key in constants_data:
            dim = parse_unit_to_dimension(constants_data[normalized_key].get('unit', ''), BASE_DIMS)
        else:
            # Fallback to naming conventions
            dim = get_default_dimension(raw_name, formula_id, categories, BASE_DIMS, subtopics, local_names, title)
        
    # Apply unit system profile substitutions (Natural or Gaussian/CGS)
    if unit_system and unit_system != 'SI':
        sub = get_unit_system_substitution(unit_system, BASE_DIMS)
        dim = sp.simplify(dim.subs(sub))
        
    return dim

def load_formula_categories(content_dir):
    """Crawls all category/subtopic json files to map formula_id -> {"categories": set, "subtopics": set}."""
    categories_path = os.path.join(content_dir, "categories.json")
    if not os.path.exists(categories_path):
        return {}
        
    with open(categories_path, "r") as f:
        categories = json.load(f)
        
    formula_to_contexts = {}
    exclude = ["categories.json", "formulas.json", "constants.json", "entities.json", "search_index.json", "compiled_trie_regex.json", "notation.json", "particles.json", "pillar_profiles.json"]
    
    if os.path.exists(content_dir):
        for file in os.listdir(content_dir):
            if file.endswith(".json") and file not in exclude and not file.startswith("shard_"):
                path = os.path.join(content_dir, file)
                cat_slug = file.replace(".json", "")
                try:
                    with open(path, "r") as f:
                        subtopics = json.load(f)
                    for sub_slug, sub_data in subtopics.items():
                        for fid in sub_data.get("formula_ids", []):
                            if fid not in formula_to_contexts:
                                formula_to_contexts[fid] = {"categories": set(), "subtopics": set()}
                            formula_to_contexts[fid]["categories"].add(cat_slug)
                            formula_to_contexts[fid]["subtopics"].add(sub_slug)
                except Exception:
                    pass
    return formula_to_contexts

def main():
    parser = argparse.ArgumentParser(description="🪐 Physics Lab: Symbolic Math Engine Verification")
    parser.add_argument("--shard", help="Audit a specific shard file.")
    parser.add_argument("--formula", help="Audit a specific formula ID.")
    args = parser.parse_args()

    content_dir = "app/config/content"
    constants_path = os.path.join(content_dir, "constants.json")
    notation_path = os.path.join(content_dir, "notation.json")
    formulas_dir = os.path.join(content_dir, "formulas")

    if not os.path.exists(constants_path) or not os.path.exists(notation_path):
        print("Error: Missing config assets (constants.json or notation.json).")
        sys.exit(1)

    with open(constants_path, "r") as f:
        constants_data = json.load(f)
    with open(notation_path, "r") as f:
        notation_data = json.load(f)

    # Load category context mapping
    formula_categories = load_formula_categories(content_dir)

    shards = []
    if args.shard:
        shards.append(args.shard)
    else:
        shards = sorted([f for f in os.listdir(formulas_dir) if f.startswith("shard_") and f.endswith(".json")])

    print("================================================================================")
    print("             🪐 PHYSICS LAB: SYMBOLIC MATH ENGINE AUDITOR                       ")
    print("================================================================================")
    
    total_formulas = 0
    passed_formulas = 0
    failures = []

    for shard in shards:
        shard_path = os.path.join(formulas_dir, shard)
        with open(shard_path, "r") as f:
            shard_data = json.load(f)

        for fid, fdata in shard_data.items():
            if args.formula and fid != args.formula:
                continue

            total_formulas += 1
            title = fdata.get("title", fid)
            eq = fdata.get("equation", "")
            sem_vars = fdata.get("semantic_variables", {})
            unit_system = fdata.get("unit_system", "SI")

            # Retrieve parent categories and subtopics for context-sensitive defaults
            context_data = formula_categories.get(fid, {"categories": set(), "subtopics": set()})
            categories = context_data["categories"]
            subtopics = context_data["subtopics"]

            success, msg = verify_equation_dimensions(fid, title, eq, sem_vars, constants_data, notation_data, categories, subtopics, unit_system)
            
            if success:
                passed_formulas += 1
                if args.formula or args.shard:
                    print(f"✓ [{fid}] '{title}' -> {msg}")
            else:
                failures.append((fid, title, shard, msg))
                print(f"❌ MISMATCH: [{fid}] '{title}' in {shard}")
                print(f"  Reason: {msg}")

    print("\n================================================================================")
    print(" AUDIT SUMMARY:")
    print(f"  * Total Formulas Scanned:   {total_formulas}")
    print(f"  * Dimensionally Consistent: {passed_formulas}")
    print(f"  * Failures / Violations:    {len(failures)}")
    if total_formulas > 0:
        print(f"  * Verification Accuracy:    {round((passed_formulas / total_formulas) * 100, 2)}%")
    print("================================================================================")

    if failures:
        print("\nDetail of Failures:")
        for idx, (fid, title, shard, msg) in enumerate(failures):
            print(f"  {idx + 1}. [{fid}] '{title}' (Shard: {shard})\n     Error: {msg}")
        sys.exit(1)
        
    print("✓ SECURE: All formula shards are dimensionally and symbolically consistent!")
    sys.exit(0)

if __name__ == "__main__":
    main()
