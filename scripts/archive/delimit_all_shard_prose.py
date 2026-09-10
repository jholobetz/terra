#!/usr/bin/env python3
"""
delimit_all_shard_prose.py

Scans all 256 formula shard JSON files in app/config/content/formulas/
and explicitly encloses un-delimited LaTeX expressions in formula prose fields
(interpretation, limits_and_boundary, symmetry_origin, conceptual_definition, intuitive_summary)
in standard '$ ... $' MathJax delimiters.
"""

import os
import glob
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

PROSE_KEYS = ["interpretation", "limits_and_boundary", "symmetry_origin", "conceptual_definition", "intuitive_summary"]

def wrap_math_in_prose(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    placeholders = []
    def save_math(val_str):
        placeholders.append(val_str)
        return f"___MATH_{len(placeholders)-1}___"

    greek_map = {
        "Γ": "\\Gamma", "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta",
        "ε": "\\epsilon", "θ": "\\theta", "λ": "\\lambda", "μ": "\\mu", "ν": "\\nu",
        "π": "\\pi", "ρ": "\\rho", "σ": "\\sigma", "τ": "\\tau", "φ": "\\phi",
        "ψ": "\\psi", "ω": "\\omega", "Ω": "\\Omega", "Δ": "\\Delta"
    }

    t = text

    # Step 0: Fix un-delimited equation patterns like "Γ = $\frac..." or "var = $\frac..."
    def full_eq_fix(m):
        lhs = m.group(1).strip()
        rhs = m.group(2).strip()
        if lhs in greek_map:
            lhs = greek_map[lhs]
        return f"${lhs} = {rhs}$"

    t = re.sub(r"([A-Za-z\u0370-\u03FF]+)\s*=\s*\$([^\$]+)\$", full_eq_fix, t)

    # 1. Protect existing math delimiters
    t = re.sub(r"\$\$[\s\S]*?\$\$", lambda m: save_math(m.group(0)), t)
    t = re.sub(r"\$[^\$]+\$", lambda m: save_math(m.group(0)), t)
    t = re.sub(r"\\\([\s\S]*?\\\)", lambda m: save_math(m.group(0)), t)
    t = re.sub(r"\\\[[\s\S]*?\\\]", lambda m: save_math(m.group(0)), t)

    # 2. Limiting cases like "(T) approaches zero" or "Γ approaches infinity"
    def limit_repl(m):
        sym = m.group(1).strip("() ").strip()
        target = m.group(2).strip().lower()
        if sym in greek_map:
            sym = greek_map[sym]
        tex_target = "\\infty" if target == "infinity" else "0"
        return save_math(f"${sym} \\to {tex_target}$")

    t = re.sub(r"(\([a-zA-Z0-9_\^ ]+\)|[A-Za-z\u0370-\u03FF]+)\s+approaches\s+(zero|infinity|0|\\infty)", limit_repl, t, flags=re.IGNORECASE)

    # 3. Parenthesized variables like (Ze)^2, (k_B T), (Z), (e), (a), (k_B), (T)
    def paren_var_repl(m):
        matched = m.group(0)
        inner = re.sub(r"^\(|\)$", "", matched.split("^")[0]).strip()
        if "," in inner or len(inner.split()) > 2 or inner in ["C", "J", "K", "m", "s", "V", "W", "Pa", "Hz", "N", "T", "rad", "mol"]:
            return matched
        if "^" in matched:
            exp = matched[matched.index("^"):]
            val = f"$({inner}){exp}$"
        else:
            val = f"${inner}$"
        return save_math(val)

    t = re.sub(r"\((?:[a-zA-Z0-9_\^\s]|\\_[a-zA-Z0-9]+)+\)(?:\^[0-9a-zA-Z{}]+)?", paren_var_repl, t)

    # 4. Standalone Greek letters in prose
    def greek_repl(m):
        g = m.group(0)
        return save_math(f"${greek_map[g]}$")

    t = re.sub(r"([ΓαβγδεθλμνπρστφψωΩΔ])", greek_repl, t)

    # 5. Isolated LaTeX commands
    def tex_cmd_repl(m):
        val = m.group(0).strip()
        punct = ""
        if val and val[-1] in ".,;:?":
            punct = val[-1]
            val = val[:-1].strip()
        return save_math(f"${val}$") + punct

    t = re.sub(r"\\(?:rho|nu|frac|pi|theta|phi|sigma|omega|mu|lambda|epsilon|delta|hbar|partial|to|approx|infty)\b(?:\{[^{}]*\}|\([^)]*\)|[a-zA-Z0-9_\^])*", tex_cmd_repl, t)

    # Restore placeholders
    for i, p in enumerate(placeholders):
        t = t.replace(f"___MATH_{i}___", p)

    return t

def process_shards():
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, "**", "shard_*.json"), recursive=True))
    print(f"Scanning {len(shard_files)} formula shard files...")

    modified_files = 0
    total_formulas_updated = 0

    for shard_path in shard_files:
        with open(shard_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error loading {shard_path}: {e}")
                continue

        shard_changed = False
        for formula_id, formula in data.items():
            if not isinstance(formula, dict):
                continue

            for key in PROSE_KEYS:
                if key in formula and isinstance(formula[key], str):
                    original = formula[key]
                    updated = wrap_math_in_prose(original)
                    if updated != original:
                        formula[key] = updated
                        shard_changed = True

            if shard_changed:
                total_formulas_updated += 1

        if shard_changed:
            with open(shard_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            modified_files += 1

    print(f"Done! Modified {modified_files} shard files ({total_formulas_updated} formulas updated).")

if __name__ == "__main__":
    process_shards()
