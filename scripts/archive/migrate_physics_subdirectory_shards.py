#!/usr/bin/env python3
"""
Migrates physics formula JSON shards from flat layout (`formulas/shard_XX.json`)
to 2-level hexadecimal subdirectories (`formulas/XX/shard_XX.json`).
"""

import os
import sys
import glob
import shutil

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app/config/content/formulas")

def migrate_shards():
    print(f"📦 Starting Physics Subdirectory Shard Migration in {FORMULAS_DIR}...")

    if not os.path.exists(FORMULAS_DIR):
        print(f"❌ Error: Formulas directory does not exist at {FORMULAS_DIR}")
        sys.exit(1)

    flat_shard_files = [
        f for f in os.listdir(FORMULAS_DIR)
        if f.startswith("shard_") and f.endswith(".json") and os.path.isfile(os.path.join(FORMULAS_DIR, f))
    ]

    print(f"  - Found {len(flat_shard_files)} flat shard files to migrate.")

    if not flat_shard_files:
        print("  - All shards are already migrated into subdirectories!")
        return

    moved_count = 0
    for filename in sorted(flat_shard_files):
        # Extract prefix from shard_XX.json -> XX
        prefix = filename.replace("shard_", "").replace(".json", "")
        if len(prefix) != 2:
            print(f"  ⚠️ Warning: Unexpected shard filename format: {filename}, skipping.")
            continue

        subdir = os.path.join(FORMULAS_DIR, prefix)
        os.makedirs(subdir, exist_ok=True)

        src_path = os.path.join(FORMULAS_DIR, filename)
        dst_path = os.path.join(subdir, filename)

        shutil.move(src_path, dst_path)
        moved_count += 1

    print(f"✅ Successfully migrated {moved_count} physics shard files into 2-level subdirectories (`formulas/XX/shard_XX.json`).")

if __name__ == "__main__":
    migrate_shards()
