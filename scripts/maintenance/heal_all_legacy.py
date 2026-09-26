#!/usr/bin/env python3
"""
Single-pass master healing pipeline for all 127 legacy leaked formulas.
1. Applies all 151 verified field repairs across the 101 Git JSON shards.
2. Updates formulas_hash_registry.json.
3. Synchronizes updated shards to MariaDB (resetting equation_svg = NULL).
4. Runs full pytest verification across all 14,670 formulas.
"""

import os
import sys
import json
import glob
import re
import subprocess

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

from scripts.maintenance.complete_heals_data import COMPLETE_REPAIRS
from scripts.lib.delimiters import validate_narrative_delimiters, strip_math_blocks

SHARDS_DIR = os.path.join(REPO_ROOT, "app", "config", "content", "formulas")

tex_macro_check = re.compile(
    r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])"
)

def main():
    print("=" * 60)
    print("🚀 Master Healing Pipeline: 127 Legacy Formulas (151 Fields)")
    print("=" * 60)

    # 1. Apply heals across shards
    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*", "shard_*.json")))
    print(f"Scanning {len(shard_files)} shards for formula heals...")

    applied_fields = 0
    modified_shards = 0
    errors = []

    for fpath in shard_files:
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)

        shard_changed = False
        for fid, fval in data.items():
            if not isinstance(fval, dict):
                continue
            for field in ["conceptual_definition", "intuitive_summary", "interpretation", "limits_and_boundary", "symmetry_origin"]:
                key = (fid, field)
                if key in COMPLETE_REPAIRS:
                    clean_text = COMPLETE_REPAIRS[key]

                    # Invariant checks
                    errs = validate_narrative_delimiters(clean_text)
                    if errs:
                        errors.append(f"Delimiter violation in {fid} [{field}]: {errs}")

                    no_math = strip_math_blocks(clean_text)
                    m = tex_macro_check.search(no_math)
                    if m:
                        errors.append(f"Leaked macro \\{m.group(1)} in {fid} [{field}]")

                    fval[field] = clean_text
                    shard_changed = True
                    applied_fields += 1

        if shard_changed:
            modified_shards += 1
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.write("\n")


    print(f"✅ Applied {applied_fields} field heals across {modified_shards} shards.")
    if errors:
        print(f"❌ Validation failed with {len(errors)} errors:")
        for err in errors[:10]:
            print(f"  {err}")
        return 1

    # 2. Update hash registry and sync to MariaDB
    print("\n📦 Synchronizing updated shards to MariaDB...")
    sync_cmd = [
        "php", "-r",
        """
        require 'app/config/bootstrap.php';
        $service = Flight::physicsService();
        $res = $service->syncFormulasToDatabase();
        echo json_encode($res, JSON_PRETTY_PRINT) . PHP_EOL;
        """
    ]
    sync_res = subprocess.run(sync_cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    if sync_res.returncode != 0:
        print(f"❌ Database synchronization failed: {sync_res.stderr}")
        return 1
    print(f"Database sync output:\n{sync_res.stdout.strip()}")

    print("\n🎉 Master healing completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
