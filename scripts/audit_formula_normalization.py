r"""
Phase 3: Non-Destructive Formula Normalization Audit Script
------------------------------------------------------------
Scans all 278 formula shard files using TerraLexer to generate a dry-run
diff report of proposed text & TeX math normalizations across 13,710 formulas.
"""

import json
import glob
import os
import sys
import time
from terra_lexer import TerraLexer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARD_DIR = os.path.join(PROJECT_ROOT, "app/config/content/formulas")

def run_audit(apply_changes: bool = False):
    lexer = TerraLexer()
    shards = glob.glob(os.path.join(SHARD_DIR, "*/*.json"))
    shards.extend(glob.glob(os.path.join(SHARD_DIR, "*.json")))
    shards = sorted(list(set(shards)))

    print(f"Starting Phase 3 Audit across {len(shards)} shard files...")
    start_time = time.time()

    total_formulas = 0
    modified_formulas = 0
    modified_shards = 0
    field_counts = {
        "conceptual_definition": 0,
        "interpretation": 0,
        "symmetry_origin": 0,
        "limits_and_boundary": 0,
        "intuitive_summary": 0,
        "semantic_variables": 0
    }

    sample_diffs = []

    for shard_path in shards:
        try:
            with open(shard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {shard_path}: {e}")
            continue

        shard_modified = False
        rel_shard_path = os.path.relpath(shard_path, PROJECT_ROOT)

        for formula_id, formula in data.items():
            if not isinstance(formula, dict):
                continue
            total_formulas += 1

            formula_changed = False
            field_diffs = {}

            target_fields = [
                "conceptual_definition",
                "interpretation",
                "symmetry_origin",
                "limits_and_boundary",
                "intuitive_summary"
            ]

            for f_name in target_fields:
                if f_name in formula and isinstance(formula[f_name], str):
                    orig = formula[f_name]
                    cleaned = lexer.normalize_text(orig)
                    if cleaned != orig:
                        formula_changed = True
                        field_counts[f_name] += 1
                        field_diffs[f_name] = (orig, cleaned)
                        if apply_changes:
                            formula[f_name] = cleaned

            if "semantic_variables" in formula and isinstance(formula["semantic_variables"], dict):
                for v_key, v_info in formula["semantic_variables"].items():
                    if isinstance(v_info, dict) and "description" in v_info and isinstance(v_info["description"], str):
                        orig_desc = v_info["description"]
                        cleaned_desc = lexer.normalize_text(orig_desc)
                        if cleaned_desc != orig_desc:
                            formula_changed = True
                            field_counts["semantic_variables"] += 1
                            field_diffs[f"var:{v_key}"] = (orig_desc, cleaned_desc)
                            if apply_changes:
                                v_info["description"] = cleaned_desc

            if formula_changed:
                modified_formulas += 1
                shard_modified = True
                if len(sample_diffs) < 10:
                    sample_diffs.append({
                        "shard": rel_shard_path,
                        "formula_id": formula_id,
                        "title": formula.get("title", formula_id),
                        "diffs": field_diffs
                    })

        if shard_modified:
            modified_shards += 1
            if apply_changes:
                with open(shard_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

    elapsed = time.time() - start_time
    mode_str = "APPLIED" if apply_changes else "DRY-RUN"

    print("\n" + "=" * 60)
    print(f"           PHASE 3 AUDIT REPORT ({mode_str})           ")
    print("=" * 60)
    print(f"Total Shards Scanned:    {len(shards)}")
    print(f"Total Formulas Checked:  {total_formulas}")
    print(f"Modified Shards:         {modified_shards}")
    print(f"Modified Formulas:       {modified_formulas} ({(modified_formulas/max(1, total_formulas))*100:.1f}%)")
    print(f"Execution Time:          {elapsed:.2f}s")
    print("-" * 60)
    print("Modifications by Field Category:")
    for field_name, count in field_counts.items():
        print(f"  - {field_name:<24}: {count}")
    print("=" * 60)

    if sample_diffs:
        print("\nSAMPLE NORMALIZATION DIFFS (First 5):")
        print("-" * 60)
        for idx, item in enumerate(sample_diffs[:5], 1):
            print(f"\n[{idx}] Formula: {item['title']} ({item['formula_id']})")
            print(f"    File: {item['shard']}")
            for f_key, (orig, cleaned) in list(item['diffs'].items())[:2]:
                print(f"    Field: {f_key}")
                print(f"      ORIG: {orig[:120]}...")
                print(f"      NORM: {cleaned[:120]}...")


if __name__ == "__main__":
    apply_mode = "--apply" in sys.argv
    run_audit(apply_changes=apply_mode)
