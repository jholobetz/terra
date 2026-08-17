#!/usr/bin/env python3
"""
Terra Physics Lab - Shard Anomaly & OCR Corruption Detector
Scans all 13,768 formulas across 256 shards to flag TeX corruptions,
OCR letter substitutions, broken delimiters, and incomplete schemas.
"""

import os
import re
import glob
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARDS_DIR = os.path.join(ROOT_DIR, "app/config/content/formulas")
OUTPUT_MANIFEST = os.path.join(ROOT_DIR, "app/config/audit_remediation_manifest.json")

# Suspicious Patterns
SUSPICIOUS_REGEXES = [
    (r"\b tial\b", "Unescaped partial derivative ( tial)"),
    (r"_\{\s*[a-zA-Z]*u[a-zA-Z]*\s*\}", "Possible Latin 'u' OCR error for Greek '\\nu' in index"),
    (r"\^\{\s*[a-zA-Z]*u[a-zA-Z]*\s*\}", "Possible Latin 'u' OCR error for Greek '\\nu' in superscript index"),
    (r"_\{\s*[a-zA-Z]*v[a-zA-Z]*\s*\}", "Possible Latin 'v' OCR error for Greek '\\nu' in index"),
    (r"\\text\{d\}", "Unstandardized differential d (should be \\mathrm{d})"),
    (r"\\quad\s*\\text\{", "Inline text without proper math separation"),
    (r"\$\s*\$", "Empty math delimiters"),
    (r"\\frac\{[^{}]*\}\{\s*\}", "Empty denominator in fraction"),
    (r"\\sqrt\{\s*\}", "Empty radical"),
    (r"\\left\s*[\(\[\{]\s*$", "Unclosed \\left delimiter"),
    (r"[^\\]\b(?:alpha|beta|gamma|delta|epsilon|theta|lambda|mu|nu|rho|sigma|tau|phi|psi|omega)\b", "Unescaped Greek word in equation"),
]


def check_formula(f_id, f_data):
    anomalies = []
    eq = f_data.get("equation", "")
    interp = f_data.get("interpretation", "")
    concept = f_data.get("conceptual_definition", "")
    summary = f_data.get("intuitive_summary", "")
    symm = f_data.get("symmetry_origin", "")
    limits = f_data.get("limits_and_boundary", "")
    vars_dict = f_data.get("semantic_variables", {})

    # 1. Equation Checks
    if not eq or eq == "REG" or eq == "TODO":
        anomalies.append("Empty or placeholder equation")
    
    for pattern, desc in SUSPICIOUS_REGEXES:
        if re.search(pattern, eq):
            anomalies.append(f"Equation: {desc}")

    # 2. Prose Delimiter Checks
    for field_name, field_val in [("interpretation", interp), ("conceptual_definition", concept), ("limits_and_boundary", limits)]:
        dollar_count = field_val.count("$")
        if dollar_count % 2 != 0:
            anomalies.append(f"{field_name}: Unbalanced dollar delimiters (${dollar_count}$)")
        if " tial" in field_val:
            anomalies.append(f"{field_name}: Unescaped partial derivative ( tial)")
        if re.search(r"G_\{\s*\\mu\s+u\s*\}", field_val):
            anomalies.append(f"{field_name}: Corrupted Einstein tensor index G_{{\\mu u}}")

    # 3. Variable Schema Checks
    if not isinstance(vars_dict, dict) or len(vars_dict) == 0:
        anomalies.append("Empty semantic_variables dictionary")
    else:
        for v_sym, v_info in vars_dict.items():
            if not isinstance(v_info, dict):
                anomalies.append(f"Variable '{v_sym}' has malformed schema")
            elif not v_info.get("name") or not v_info.get("description"):
                anomalies.append(f"Variable '{v_sym}' missing name or description")

    return anomalies


def main():
    print("=========================================================")
    print("Terra Physics Lab - Shard Anomaly & OCR Corruption Scanner")
    print("=========================================================")

    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*/shard_*.json")))
    print(f"[INFO] Scanning {len(shard_files)} shard files...")

    total_formulas = 0
    flagged_formulas = {}

    for sf in shard_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
                for f_id, f_data in data.items():
                    if not isinstance(f_data, dict):
                        continue
                    total_formulas += 1
                    anomalies = check_formula(f_id, f_data)
                    if anomalies:
                        flagged_formulas[f_id] = {
                            "id": f_id,
                            "shard_path": os.path.relpath(sf, ROOT_DIR),
                            "title": f_data.get("title", f_id),
                            "equation": f_data.get("equation", ""),
                            "anomalies": anomalies
                        }
        except Exception as e:
            print(f"[ERROR] Failed to read {sf}: {e}")

    print(f"\n[SCAN COMPLETE]")
    print(f"  - Total Formulas Scanned: {total_formulas}")
    print(f"  - Flagged for Remediation: {len(flagged_formulas)} ({(len(flagged_formulas)/total_formulas)*100:.1f}%)")

    with open(OUTPUT_MANIFEST, "w", encoding="utf-8") as f:
        json.dump(flagged_formulas, f, indent=2)

    print(f"[OK] Saved flagged manifest to {OUTPUT_MANIFEST}")


if __name__ == "__main__":
    main()
