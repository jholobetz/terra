#!/usr/bin/env python3
"""
🔍 Subcomponent Equation Discovery Engine (Phase 1)

Scans all 7,000+ formulas across the 256 shards, extracts math sub-expressions
from prose fields (interpretation, conceptual_definition, limits_and_boundary, symmetry_origin),
filters out single variables and units, cross-references against formulas_latex_index.json,
and generates a structured audit report of missing/unindexed subcomponent formulas.
"""

import os
import sys
import json
import glob
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
INDEX_FILE = os.path.join(PROJECT_ROOT, 'app', 'config', 'formulas_latex_index.json')
REPORT_FILE = os.path.join(PROJECT_ROOT, 'app', 'config', 'unindexed_subcomponents.json')

# Single-variable / constant / unit tokens to filter out
SINGLE_TOKENS = {
    't', 'x', 'y', 'z', 'u', 'v', 'w', 'p', 'q', 'r', 's', 'a', 'b', 'c', 'd', 'e', 'f', 'g',
    'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
    '\\alpha', '\\beta', '\\gamma', '\\delta', '\\epsilon', '\\varepsilon', '\\zeta', '\\eta',
    '\\theta', '\\vartheta', '\\iota', '\\kappa', '\\lambda', '\\mu', '\\nu', '\\xi', '\\pi',
    '\\varpi', '\\rho', '\\varrho', '\\sigma', '\\varsigma', '\\tau', '\\upsilon', '\\phi',
    '\\varphi', '\\chi', '\\psi', '\\omega', '\\Gamma', '\\Delta', '\\Theta', '\\Lambda',
    '\\Xi', '\\Pi', '\\Sigma', '\\Upsilon', '\\Phi', '\\Psi', '\\Omega',
    'hbar', 'c', 'g', 'e', 'kB', 'G', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'rad/s', 'j/k', 'm/s', 'kg/m^3', 'pa', 'mol', 'm^3', 'c/m^3', 'joules', 'kelvin',
    'stokes', 'planck', 'newton', 'pascal', 'kelvin', 'joule', 'watt', 'volt', 'ampere',
    '=', '+', '-', '<', '>', '\\approx', '\\propto', '\\sim', '\\neq', '\\leq', '\\geq'
}

def normalize_latex(latex_str):
    if not isinstance(latex_str, str):
        return ""
    normalized = latex_str.strip()

    # Greek var replacements
    normalized = re.sub(r'\\varepsilon(?![a-zA-Z])', r'\\epsilon', normalized)
    normalized = re.sub(r'\\vartheta(?![a-zA-Z])', r'\\theta', normalized)
    normalized = re.sub(r'\\varphi(?![a-zA-Z])', r'\\phi', normalized)
    normalized = re.sub(r'\\varrho(?![a-zA-Z])', r'\\rho', normalized)
    normalized = re.sub(r'\\varpi(?![a-zA-Z])', r'\\pi', normalized)
    normalized = re.sub(r'\\varsigma(?![a-zA-Z])', r'\\sigma', normalized)

    # Strip outer delimiters
    normalized = re.sub(r'^\\\(', '', normalized)
    normalized = re.sub(r'\\\)$', '', normalized)
    normalized = re.sub(r'^\\\[', '', normalized)
    normalized = re.sub(r'\\\]$', '', normalized)
    normalized = re.sub(r'^\$\$', '', normalized)
    normalized = re.sub(r'\$\$$', '', normalized)
    normalized = re.sub(r'^\$', '', normalized)
    normalized = re.sub(r'\$$', '', normalized)

    # Strip styling commands
    normalized = re.sub(r'\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^}]+)\}', r'\2', normalized)
    normalized = re.sub(r'\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])', r'\2', normalized)
    normalized = re.sub(r'\\cssId\{[^}]+\}\{([^}]+)\}', r'\1', normalized)

    # Fraction normalization
    while '\\frac{' in normalized:
        next_norm = re.sub(r'\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1/\2', normalized)
        if next_norm == normalized:
            break
        normalized = next_norm

    # Canonicalize characters (alpha-sorted lowercase letters/digits/operators)
    chars = [c.lower() for c in normalized if c.isalnum() or c in '+-*/=^_/']
    chars.sort()
    return "".join(chars)

def extract_math_expressions(text):
    if not isinstance(text, str):
        return []
    # Match $ ... $ or $$ ... $$ or \( ... \) or \[ ... \]
    patterns = [
        r'\$\$(.*?)\$\$',
        r'\$(.*?)\$',
        r'\\\((.*?)\\\)',
        r'\\\[(.*?)\\\]'
    ]
    matches = []
    for pat in patterns:
        for m in re.findall(pat, text, re.DOTALL):
            cleaned = m.strip()
            if cleaned:
                matches.append(cleaned)
    return matches

# Trivial 2-character differential tokens to filter out
SIMPLE_DIFFERENTIATION_TOKENS = {
    'dt', 'dx', 'dy', 'dz', 'dr', 'dp', 'dq', 'ds', 'du', 'dv', 'dh', 'da', 'df', 'dg', 'de',
    'dS', 'dU', 'dV', 'dH', 'dA', 'dF', 'dG', 'dE', 'dP', 'dN', 'd\\mathbf{x}', 'ds^2', 'dt^2',
    'dx^2', 'dy^2', 'dz^2', 'dr^2', 'dp^2', 'dq^2', 'S_{future}', 'S_{past}'
}

def is_valid_subcomponent(expr):
    clean = expr.strip()
    if not clean:
        return False

    # Check if single variable / constant / unit token
    if clean in SINGLE_TOKENS or clean in SIMPLE_DIFFERENTIATION_TOKENS:
        return False

    # Filter out pure limit to zero expressions like 'dt \to 0', '|d\mathbf{x}| \to 0'
    if re.search(r'\\to\s*0', clean):
        return False

    # Check normalized string length
    norm = normalize_latex(clean)
    if len(norm) < 3:
        return False

    # Must contain math operators, multiple variables, exponents, fractions, or derivatives
    has_math_structure = any(
        char in clean for char in ['=', '+', '-', '*', '/', '^', '_', '\\sum', '\\int', '\\partial', '\\nabla', '\\oint', '\\frac', '\\sqrt']
    ) or len(re.findall(r'[a-zA-Z]{2,}', clean)) > 1

    return has_math_structure

def main():
    print("🔍 Launching Subcomponent Discovery Engine (Phase 1)...")

    # Load LaTeX Index
    if not os.path.exists(INDEX_FILE):
        print(f"❌ Index file missing at {INDEX_FILE}")
        sys.exit(1)

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        latex_index = json.load(f)

    indexed_normalized = set(latex_index.keys())

    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, "shard_*.json")))
    print(f"  - Loaded {len(latex_index)} indexed formulas across {len(shard_files)} shards.")

    total_formulas = 0
    total_subexpressions = 0
    indexed_count = 0
    unindexed_count = 0

    master_catalog = []

    for filepath in shard_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                continue

        for f_id, f_data in data.items():
            total_formulas += 1
            master_eq = f_data.get('equation', '')
            title = f_data.get('title', 'Untitled Formula')

            prose_fields = [
                f_data.get('conceptual_definition', ''),
                f_data.get('interpretation', ''),
                f_data.get('limits_and_boundary', ''),
                f_data.get('symmetry_origin', ''),
                f_data.get('intuitive_summary', '')
            ]

            all_extracted = []
            for field in prose_fields:
                all_extracted.extend(extract_math_expressions(field))

            # Filter valid compound subcomponents
            unique_subexprs = list(set(all_extracted))
            valid_subcomponents = [expr for expr in unique_subexprs if is_valid_subcomponent(expr)]

            missing_for_this_master = []
            found_for_this_master = []

            for expr in valid_subcomponents:
                total_subexpressions += 1
                norm = normalize_latex(expr)

                if norm in indexed_normalized:
                    indexed_count += 1
                    found_for_this_master.append({
                        "raw_latex": expr,
                        "formula_id": latex_index[norm]
                    })
                else:
                    unindexed_count += 1
                    missing_for_this_master.append(expr)

            if missing_for_this_master:
                master_catalog.append({
                    "formula_id": f_id,
                    "title": title,
                    "master_equation": master_eq,
                    "missing_subcomponents_count": len(missing_for_this_master),
                    "missing_subcomponents": missing_for_this_master,
                    "indexed_subcomponents_count": len(found_for_this_master),
                    "indexed_subcomponents": found_for_this_master
                })

    report = {
        "summary": {
            "total_formulas_scanned": total_formulas,
            "total_subexpressions_found": total_subexpressions,
            "indexed_subcomponents_count": indexed_count,
            "unindexed_subcomponents_count": unindexed_count,
            "master_formulas_with_unindexed_subcomponents": len(master_catalog)
        },
        "master_formulas": master_catalog
    }

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n✅ Subcomponent Discovery Audit Complete!")
    print(f"   - Total Formulas Scanned: {total_formulas}")
    print(f"   - Total Sub-Expressions Extracted: {total_subexpressions}")
    print(f"   - Already Indexed Subcomponents: {indexed_count}")
    print(f"   - Un-indexed Subcomponents Discovered: {unindexed_count}")
    print(f"   - Master Formulas Requiring Subcomponent Records: {len(master_catalog)}")
    print(f"   - Audit Report Saved To: {REPORT_FILE}")

if __name__ == '__main__':
    main()
