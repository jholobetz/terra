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
    def save_math(m):
        placeholders.append(m.group(0))
        return f"___MATH_{len(placeholders)-1}___"

    # 1. Protect existing math delimiters
    t = re.sub(r"\$\$[\s\S]*?\$\$", save_math, text)
    t = re.sub(r"\$[^\$]+\$", save_math, t)
    t = re.sub(r"\\\([\s\S]*?\\\)", save_math, t)
    t = re.sub(r"\\\[[\s\S]*?\\\]", save_math, t)

    def protect_and_wrap(m):
        val = m.group(0).strip()
        if not val or "___MATH_" in val:
            return m.group(0)
        punct = ""
        if val[-1] in ".,;:?":
            punct = val[-1]
            val = val[:-1].strip()
        if val.endswith(")") and val.count("(") < val.count(")"):
            punct = ")" + punct
            val = val[:-1].strip()
        wrapped = f"${val}${punct}"
        placeholders.append(wrapped)
        return f"___MATH_{len(placeholders)-1}___"

    # Step A: Match equation blocks starting with a LaTeX command up to sentence punctuation or prose words
    t = re.sub(
        r"\\(?:rho|nu|frac|pi|theta|phi|sigma|omega|mu|lambda|epsilon|delta|hbar|partial)\b[^\n\.\,;:!\?]*?(?=\s+(?:quantifies|represents|is|derived|where|as|in|for|and|with|by|\.|\,|$))",
        protect_and_wrap,
        t
    )

    # Step B: Match remaining isolated LaTeX commands (e.g. \nu, \rho, \frac{h\nu}{k_B T})
    t = re.sub(
        r"\\(?:rho|nu|frac|pi|theta|phi|sigma|omega|mu|lambda|epsilon|delta|hbar|partial|to|approx|infty)\b(?:\{[^{}]*\}|\([^)]*\)|[a-zA-Z0-9_\^])*",
        protect_and_wrap,
        t
    )

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
