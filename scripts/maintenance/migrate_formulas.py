#!/usr/bin/env python3
import os
import json
import hashlib
import shutil

content_dir = "app/config/content"
old_formulas_path = os.path.join(content_dir, "formulas.json")
formulas_dir = os.path.join(content_dir, "formulas")

def get_shard_prefix(f_id):
    return hashlib.md5(f_id.encode("utf-8")).hexdigest()[:2]

def migrate():
    if not os.path.exists(old_formulas_path):
        print(f"ERROR: {old_formulas_path} does not exist. Migration aborted.")
        return False

    print(f"Reading existing formulas from {old_formulas_path}...")
    with open(old_formulas_path, "r") as f:
        formulas = json.load(f)

    print(f"Found {len(formulas)} formulas in global registry.")
    
    # Group formulas by their 2-character MD5 hex prefix
    sharded_formulas = {}
    for f_id, data in formulas.items():
        prefix = get_shard_prefix(f_id)
        if prefix not in sharded_formulas:
            sharded_formulas[prefix] = {}
        sharded_formulas[prefix][f_id] = data

    # Create target directory
    os.makedirs(formulas_dir, exist_ok=True)
    print(f"Writing {len(sharded_formulas)} shards under {formulas_dir}...")

    # Write all shards (00 to ff)
    # To keep the database clean and predictable, we write empty/existing files for all possible 256 prefixes
    for i in range(256):
        prefix = f"{i:02x}"
        shard_path = os.path.join(formulas_dir, f"shard_{prefix}.json")
        shard_data = sharded_formulas.get(prefix, {})
        with open(shard_path, "w") as f:
            json.dump(shard_data, f, indent=4)

    print("✓ Sharding completed successfully.")
    
    # Backup and remove the old monolithic formulas.json
    bak_path = old_formulas_path + ".bak_sharded"
    shutil.move(old_formulas_path, bak_path)
    print(f"Moved old formulas.json to backup: {bak_path}")
    print("Migration complete!")
    return True

if __name__ == "__main__":
    migrate()
