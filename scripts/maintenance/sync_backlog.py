#!/usr/bin/env python3
import json
import os
import sys

CONTENT_DIR = "app/config/content"
BACKLOG_PATH = "subfiles/expansion_backlog.json"

def scan_disk_standards():
    """Scans all physical JSON shards on disk to extract the real-time standard of each subtopic."""
    subtopics = {}
    if not os.path.exists(CONTENT_DIR):
        print(f"Error: Content directory {CONTENT_DIR} not found.")
        sys.exit(1)
        
    for file in os.listdir(CONTENT_DIR):
        # Scan only subtopic content shards
        if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json", "entities.json", "global_slug_registry.json", "compiled_trie_regex.json", "notation.json", "particles.json", "pillar_profiles.json", "formula_aliases.json"]:
            path = os.path.join(CONTENT_DIR, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for slug, val in data.items():
                        subtopics[slug] = {
                            "title": val.get("title", slug),
                            "shard": file,
                            "standard": val.get("standard", "legacy")
                        }
            except Exception as e:
                print(f"Warning: Could not read shard {file}: {e}")
                continue
                
    return subtopics

def dedupe_backlog(entries):
    """Collapse duplicate suggested_slug rows; promote status when any duplicate is completed.

    Preserves first-appearance order of survivors. Entries without
    suggested_slug are kept verbatim (they can't be duplicates of anything).
    Does not mutate the input list or its entries.
    """
    result = []
    seen_at = {}  # slug -> index in result
    for entry in entries:
        slug = entry.get("suggested_slug")
        if not slug:
            result.append(dict(entry))
            continue
        if slug not in seen_at:
            seen_at[slug] = len(result)
            result.append(dict(entry))
        else:
            survivor = result[seen_at[slug]]
            if entry.get("status") == "completed" and survivor.get("status") != "completed":
                survivor["status"] = "completed"
    return result


def self_heal_backlog(disk_state):
    """Aligns expansion_backlog.json with disk truth and collapses duplicate slugs.

    Returns (healed_count, total_count). total_count reflects entries after
    deduplication, not the raw on-disk row count. The file is rewritten if
    either a status flip or a deduplication occurred.
    """
    if not os.path.exists(BACKLOG_PATH):
        print(f"Warning: Backlog file not found at {BACKLOG_PATH}. Skipping self-healing.")
        return 0, 0

    with open(BACKLOG_PATH, "r") as f:
        backlog = json.load(f)

    original_len = len(backlog)
    backlog = dedupe_backlog(backlog)
    deduped_count = original_len - len(backlog)

    healed_count = 0
    total_count = len(backlog)

    for entry in backlog:
        slug = entry.get("suggested_slug")
        if slug in disk_state:
            real_std = disk_state[slug]["standard"]
            current_status = entry.get("status")

            # Map physical standard directly to status
            expected_status = "completed" if real_std == "platinum" else "pending"

            if current_status != expected_status:
                entry["status"] = expected_status
                healed_count += 1

    if healed_count > 0 or deduped_count > 0:
        with open(BACKLOG_PATH, "w") as f:
            json.dump(backlog, f, indent=4)
            f.write("\n")

    return healed_count, total_count

def print_progress_dashboard(disk_state):
    """Outputs a premium, highly-detailed progress dashboard of the entire database."""
    total_nodes = len(disk_state)
    platinum_nodes = sum(1 for s in disk_state.values() if s["standard"] == "platinum")
    legacy_nodes = total_nodes - platinum_nodes
    progress_pct = (platinum_nodes / total_nodes) * 100 if total_nodes > 0 else 0.0
    
    # Group metrics by shard
    shard_metrics = {}
    for s in disk_state.values():
        shard = s["shard"]
        if shard not in shard_metrics:
            shard_metrics[shard] = {"total": 0, "platinum": 0}
        shard_metrics[shard]["total"] += 1
        if s["standard"] == "platinum":
            shard_metrics[shard]["platinum"] += 1
            
    # Print gorgeous visual report
    print("\n" + "="*80)
    print(" CENTRAL TRACKING AUTHORITY: PHYSICS DATABASE STATUS ".center(80, "="))
    print("="*80)
    print(f"  * Total Subtopics:       {total_nodes:<5}")
    print(f"  * Graduated (Platinum):  \033[92m{platinum_nodes:<5}\033[0m")
    print(f"  * Pending (Legacy):      \033[93m{legacy_nodes:<5}\033[0m")
    
    # Progress Bar
    bar_width = 40
    filled_width = int(round(bar_width * (progress_pct / 100)))
    bar = "█" * filled_width + "-" * (bar_width - filled_width)
    print(f"  * Overall Progress:      [{bar}] \033[92m{progress_pct:.2f}%\033[0m")
    print("-"*80)
    
    # Shard Breakdown Table
    print(f" {'Shard Name':<42} | {'Total':<5} | {'Platinum':<8} | {'Legacy':<6} | {'Progress'}")
    print("-"*80)
    
    for shard in sorted(shard_metrics.keys()):
        metrics = shard_metrics[shard]
        tot = metrics["total"]
        plat = metrics["platinum"]
        leg = tot - plat
        pct = (plat / tot) * 100 if tot > 0 else 0.0
        
        # Color graduation progress cleanly
        pct_color = "\033[92m" if pct == 100.0 else ("\033[93m" if pct > 0 else "")
        reset_color = "\033[0m"
        
        print(f"  {shard:<40} | {tot:<5} | {plat:<8} | {leg:<6} | {pct_color}{pct:.1f}%{reset_color}")
        
    print("="*80 + "\n")

def main():
    print("🤖 [CTA] Scrutinizing physical JSON shards on disk...")
    disk_state = scan_disk_standards()
    
    print("🤖 [CTA] Performing self-healing backlog verification...")
    healed, total = self_heal_backlog(disk_state)
    
    if healed > 0:
        print(f"  \033[92m✓ HEALED: Synchronized {healed} desynchronized targets inside expansion_backlog.json!\033[0m")
    else:
        print("  \033[92m✓ SECURE: All tracking backlog entries perfectly aligned with physical disk state.\033[0m")
        
    print_progress_dashboard(disk_state)

if __name__ == "__main__":
    main()
