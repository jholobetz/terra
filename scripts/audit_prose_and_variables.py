#!/usr/bin/env python3
"""
Automated Global Shard Scanner & Repair Engine (Option A)
--------------------------------------------------------
Scans and repairs all 13,700+ formulas in app/config/content/formulas/*/*.json for:
1. Unmatched $ dollar sign delimiters in prose fields.
2. Illegal nested $ inside LaTeX environments (e.g. \\begin{vmatrix} ... $ ... $ \\end{vmatrix}).
3. Corrupted UTF-8 / byte artifacts (e.g. ⌑, ̂, ⇔, ∃, ∈, ⊨, \\gamma  \\gamma).
4. Invalid semantic_variables keys (wrapped in $, containing HTML, or raw Unicode).
5. Stripped prose placeholders (e.g. "The equation = defines...", "product ()").

Usage:
  python3 scripts/audit_prose_and_variables.py
  python3 scripts/audit_prose_and_variables.py --fix
"""

import sys
import os
import glob
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORMULAS_DIR = PROJECT_ROOT / "app" / "config" / "content" / "formulas"

UNICODE_KEY_MAP = {
    "⌑": "\\lozenge",
    "̂": "\\psi",
    "⇔": "\\iff",
    "∃": "\\exists",
    "∈": "\\in",
    "⊨": "\\vDash",
}

PROSE_FIELDS = ["interpretation", "symmetry_origin", "limits_and_boundary", "conceptual_definition", "intuitive_summary"]

def count_unescaped_dollars(text: str) -> int:
    clean = text.replace(r"\$", "")
    return clean.count("$")

def check_nested_dollars_in_env(text: str) -> bool:
    pattern = r"\\begin\{(vmatrix|matrix|align|equation|array|bmatrix|pmatrix)\}.*?\$"
    return bool(re.search(pattern, text, re.DOTALL))

def fix_nested_dollars_in_env(text: str) -> str:
    """Removes $ delimiters inside \\begin{env}...\\end{env} blocks."""
    def clean_env_block(match):
        block = match.group(0)
        return block.replace("$", "")
    
    pattern = r"\\begin\{(vmatrix|matrix|align|equation|array|bmatrix|pmatrix)\}.*?\\end\{\1\}"
    return re.sub(pattern, clean_env_block, text, flags=re.DOTALL)

def clean_html_math_key(key: str) -> str:
    """Strips HTML/Math display tags from keys."""
    clean = re.sub(r'</?(?:strong|em|math)[^>]*>', '', key)
    clean = re.sub(r'display="[^"]*"', '', clean)
    clean = clean.replace('math', '').replace('/', '').strip()
    if clean.startswith("$") and clean.endswith("$"):
        clean = clean[1:-1].strip()
    return clean

def fix_prose_corrupted_unicode(text: str) -> str:
    """Repairs corrupted unicode artifacts in prose text."""
    text = text.replace("⌑", "\\lozenge")
    text = text.replace("̂", "\\psi")
    text = text.replace("⇔", "\\iff")
    text = text.replace("∃", "\\exists")
    text = text.replace("∈", "\\in")
    text = text.replace("⊨", "\\vDash")
    text = re.sub(r"\\gamma\s+\\gamma", r"\\gamma", text)
    text = re.sub(r"̂\$\\gamma", r"\\psi", text)
    return text

def fix_prose_placeholders(text: str) -> str:
    """Fixes stripped prose placeholders."""
    text = text.replace("The equation = defines", "The equation defines")
    text = text.replace("denoted by (in units", "denoted by $\\mathbf{v}_d$ (in units")
    text = text.replace("cross product ()", "cross product $\\times$")
    text = text.replace("magnitudes of and ,", "magnitudes of $\\mathbf{J}$ and $\\mathbf{B}$,")
    return text

def audit_shards(auto_fix: bool = False):
    shard_files = sorted(glob.glob(str(FORMULAS_DIR / "*" / "*.json")))
    
    total_shards = len(shard_files)
    total_formulas = 0
    issues_by_category = {
        "UNMATCHED_DOLLAR": [],
        "NESTED_DOLLAR_ENV": [],
        "CORRUPTED_UNICODE": [],
        "BAD_SEMANTIC_KEY": [],
        "STRIPPED_PLACEHOLDER": []
    }
    
    modified_shards = 0

    print("=" * 80)
    print(f"  GLOBAL SHARD SCANNER (AUDITING {total_shards} SHARDS)")
    print("=" * 80)

    for shard_path in shard_files:
        rel_path = os.path.relpath(shard_path, PROJECT_ROOT)
        with open(shard_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"❌ Error loading JSON {rel_path}: {e}")
                continue

        shard_modified = False

        for f_id, f_data in data.items():
            if not isinstance(f_data, dict):
                continue
            total_formulas += 1

            # --- 1. Audit Semantic Variables Keys ---
            sem_vars = f_data.get("semantic_variables", {})
            if isinstance(sem_vars, dict):
                new_sem_vars = {}
                sem_vars_changed = False

                for key, val in sem_vars.items():
                    orig_key = key
                    issue_types = []

                    # Key wrapped in dollar signs: "$f$" or "$\\mathbf{f}$"
                    if key.startswith("$") and key.endswith("$") and len(key) > 1:
                        issue_types.append(f"Key wrapped in dollar signs: '{key}'")
                        if auto_fix:
                            key = key[1:-1].strip()
                            sem_vars_changed = True

                    # Key contains Math/HTML tags
                    if "$strongemmath" in key or "display=\"inline\"" in key or "math display=" in key:
                        issue_types.append(f"Key contains HTML/Math tags: '{key}'")
                        if auto_fix:
                            key = clean_html_math_key(key)
                            sem_vars_changed = True

                    # Key contains raw unicode symbols
                    for unichar, repl in UNICODE_KEY_MAP.items():
                        if unichar in key:
                            issue_types.append(f"Key contains raw unicode '{unichar}': '{key}'")
                            if auto_fix:
                                key = key.replace(unichar, repl).strip()
                                sem_vars_changed = True

                    if issue_types:
                        issues_by_category["BAD_SEMANTIC_KEY"].append({
                            "shard": rel_path,
                            "formula_id": f_id,
                            "title": f_data.get("title", f_id),
                            "key": orig_key,
                            "issues": issue_types
                        })

                    new_sem_vars[key] = val

                if auto_fix and sem_vars_changed:
                    f_data["semantic_variables"] = new_sem_vars
                    shard_modified = True

            # --- 2. Audit Prose Fields ---
            for field in PROSE_FIELDS:
                text = f_data.get(field)
                if not text or not isinstance(text, str):
                    continue

                orig_text = text

                # Check nested dollar signs inside TeX environments
                if check_nested_dollars_in_env(text):
                    issues_by_category["NESTED_DOLLAR_ENV"].append({
                        "shard": rel_path,
                        "formula_id": f_id,
                        "title": f_data.get("title", f_id),
                        "field": field,
                        "snippet": text[:120] + "..." if len(text) > 120 else text
                    })
                    if auto_fix:
                        text = fix_nested_dollars_in_env(text)

                # Check corrupted unicode artifacts
                unicode_issues = re.findall(r"⌑|̂|⇔|∃|∈|⊨|\\gamma\s+\\gamma|̂\$\\gamma", text)
                if unicode_issues:
                    issues_by_category["CORRUPTED_UNICODE"].append({
                        "shard": rel_path,
                        "formula_id": f_id,
                        "title": f_data.get("title", f_id),
                        "field": field,
                        "issues": list(set(unicode_issues)),
                        "snippet": text[:120] + "..." if len(text) > 120 else text
                    })
                    if auto_fix:
                        text = fix_prose_corrupted_unicode(text)

                # Check stripped placeholders
                stripped_issues = re.findall(r"\bThe equation\s+=\s+defines\b|\bdenoted by\s+\(in units\b|cross product\s+\(\)|magnitudes of\s+and\s*,", text, re.IGNORECASE)
                if stripped_issues:
                    issues_by_category["STRIPPED_PLACEHOLDER"].append({
                        "shard": rel_path,
                        "formula_id": f_id,
                        "title": f_data.get("title", f_id),
                        "field": field,
                        "issues": list(set(stripped_issues)),
                        "snippet": text[:120] + "..." if len(text) > 120 else text
                    })
                    if auto_fix:
                        text = fix_prose_placeholders(text)

                # Check unmatched dollar signs
                dollar_count = count_unescaped_dollars(text)
                if dollar_count % 2 != 0:
                    issues_by_category["UNMATCHED_DOLLAR"].append({
                        "shard": rel_path,
                        "formula_id": f_id,
                        "title": f_data.get("title", f_id),
                        "field": field,
                        "dollar_count": dollar_count,
                        "snippet": text[:120] + "..." if len(text) > 120 else text
                    })

                if auto_fix and text != orig_text:
                    f_data[field] = text
                    shard_modified = True

        if auto_fix and shard_modified:
            with open(shard_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            modified_shards += 1

    # --- Print Summary Report ---
    print("\n" + "=" * 80)
    print("  AUDIT RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Shards Audited   : {total_shards}")
    print(f"Total Formulas Checked : {total_formulas}")
    print("-" * 80)
    
    total_issues = sum(len(v) for v in issues_by_category.values())
    print(f"1. Unmatched Dollar Signs ($)       : {len(issues_by_category['UNMATCHED_DOLLAR'])}")
    print(f"2. Nested $ inside Math Environments  : {len(issues_by_category['NESTED_DOLLAR_ENV'])}")
    print(f"3. Corrupted Unicode / Byte Artifacts: {len(issues_by_category['CORRUPTED_UNICODE'])}")
    print(f"4. Invalid semantic_variables Keys   : {len(issues_by_category['BAD_SEMANTIC_KEY'])}")
    print(f"5. Stripped Prose Placeholders       : {len(issues_by_category['STRIPPED_PLACEHOLDER'])}")
    print(f"TOTAL ISSUES DETECTED                : {total_issues}")
    print("=" * 80)

    if auto_fix:
        print(f"\n✅ Auto-fix completed. Modified {modified_shards} shard files.")

    return total_issues, issues_by_category

if __name__ == "__main__":
    auto_fix = "--fix" in sys.argv
    total_issues, _ = audit_shards(auto_fix=auto_fix)
    sys.exit(1 if total_issues > 0 and not auto_fix else 0)
