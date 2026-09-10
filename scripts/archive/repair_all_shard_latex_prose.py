#!/usr/bin/env python3
"""
⚡ Repair All Shard LaTeX Prose Artifacts
Cleans corrupted control characters, single-backslash escapes, and $ext artifact corruptions
across all formula shard JSON files.
"""

import os
import glob
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

LATEX_KEYWORDS = [
    "rho", "nu", "frac", "pi", "theta", "phi", "sigma", "tau", "omega", "mu",
    "lambda", "epsilon", "delta", "alpha", "beta", "gamma", "chi", "psi", "zeta",
    "eta", "partial", "nabla", "hbar", "cdot", "times", "sqrt", "approx", "equiv",
    "implies", "in", "int", "sum", "lim", "to", "infty", "text"
]

def clean_raw_shard_text(raw: str) -> str:
    # 1. Fix $ext / \(ext artifact corruptions
    raw = re.sub(r"\$ext\{\$ext([a-zA-Z]+)\}", r"\\\\\1", raw)
    raw = re.sub(r"\\\(ext\{\\\)ext([a-zA-Z]+)", r"\\\\\1", raw)
    raw = re.sub(r"\$ext([a-zA-Z]+)", r"\\\\\1", raw)
    raw = re.sub(r"\$ext", r"\\\\text", raw)

    # 2. Fix 'o 0' and 'o ∞' corruptions from stripped \to
    raw = re.sub(r"(\}|\s)o\s*(0|∞|\d+|\\\\infty)", r"\1\\\\to \2", raw)

    # 3. Convert single backslashes before LaTeX keywords in raw JSON strings to double backslashes
    for kw in LATEX_KEYWORDS:
        pattern = r"(?<!\\)\\" + kw + r"(?![a-zA-Z])"
        raw = re.sub(pattern, r"\\\\" + kw, raw)

    return raw

def process_shard(filepath: str) -> bool:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            original_raw = f.read()

        cleaned_raw = clean_raw_shard_text(original_raw)

        # Parse JSON to verify validity and serialize standard formatted output
        data = json.loads(cleaned_raw)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"❌ Error repairing {filepath}: {e}")
        return False

def main():
    shard_pattern = os.path.join(FORMULAS_DIR, "**", "*.json")
    files = sorted(glob.glob(shard_pattern, recursive=True))
    print(f"🚀 Repairing LaTeX prose formatting across {len(files)} formula shards...")

    repaired_count = 0
    for filepath in files:
        if process_shard(filepath):
            repaired_count += 1

    print(f"✅ Successfully repaired and formatted {repaired_count}/{len(files)} shards!")

if __name__ == "__main__":
    main()
