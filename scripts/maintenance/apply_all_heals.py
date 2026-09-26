#!/usr/bin/env python3
"""
Apply all complete heals across formula shards.
Validates each repair with validate_narrative_delimiters and tex_macro_check.
"""

import json
import sys
import os
import re
import glob

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from scripts.maintenance.complete_heals_data import COMPLETE_REPAIRS
from scripts.lib.delimiters import validate_narrative_delimiters, strip_math_blocks



SHARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "app", "config", "content", "formulas")

tex_macro_check = re.compile(
    r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])"
)

def main():
    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*", "shard_*.json")))
    print(f"Scanning {len(shard_files)} shard files...")

    applied_count = 0
    modified_shards = 0
    errors = []

    for fpath in shard_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        shard_modified = False
        for fid, fval in data.items():
            if not isinstance(fval, dict):
                continue
            for field in ["conceptual_definition", "intuitive_summary", "interpretation", "limits_and_boundary", "symmetry_origin"]:
                key = (fid, field)
                if key in COMPLETE_REPAIRS:
                    new_text = COMPLETE_REPAIRS[key]
                    
                    # Validate new_text
                    errs = validate_narrative_delimiters(new_text)
                    if errs:
                        errors.append(f"Delimiter violation in {fid} [{field}]: {errs}")
                    
                    no_math = strip_math_blocks(new_text)
                    match = tex_macro_check.search(no_math)
                    if match:
                        errors.append(f"Leaked macro \\{match.group(1)} in {fid} [{field}]: {no_math}")

                    fval[field] = new_text
                    shard_modified = True
                    applied_count += 1

        if shard_modified:
            modified_shards += 1
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.write("\n")


    print(f"Applied {applied_count} field heals across {modified_shards} shards.")
    if errors:
        print(f"FAILED with {len(errors)} validation errors:")
        for err in errors[:10]:
            print(f"  {err}")
        return 1
    else:
        print("All applied heals passed 100% of delimiter and macro-safety gates!")
        return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
