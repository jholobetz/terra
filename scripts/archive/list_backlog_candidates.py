#!/usr/bin/env python3
"""
List Backlog Candidates Utility
Quickly lists, filters, and groups the top pending subtopic graduation candidates
from the central expansion backlog registry.
"""

import os
import sys
import json
import glob
import argparse

# Color Codes for Gorgeous CLI output
COLOR_HEADER = "\033[95m"
COLOR_TITLE = "\033[94m\033[1m"
COLOR_SUCCESS = "\033[92m"
COLOR_WARNING = "\033[93m"
COLOR_FAIL = "\033[91m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_GRAY = "\033[90m"

BACKLOG_PATH = "subfiles/expansion_backlog.json"
CONTENT_DIR = "app/config/content"

def load_shards():
    """Scans all physical content shards and maps every subtopic slug to its metadata."""
    shard_map = {}
    ignore_files = {
        "categories.json", "formulas.json", "constants.json", 
        "entities.json", "search_index.json", "compiled_trie_regex.json",
        "notation.json", "particles.json", "pillar_profiles.json"
    }
    
    pattern = os.path.join(CONTENT_DIR, "*.json")
    for path in glob.glob(pattern):
        filename = os.path.basename(path)
        if filename in ignore_files or filename.endswith(".bak"):
            continue
        try:
            with open(path, "r") as f:
                shard_data = json.load(f)
            for slug, data in shard_data.items():
                shard_map[slug] = {
                    "shard": filename,
                    "standard": data.get("standard", "legacy"),
                    "title": data.get("title", slug)
                }
        except Exception as e:
            print(f"{COLOR_FAIL}Error reading {filename}: {e}{COLOR_RESET}", file=sys.stderr)
            
    return shard_map

def main():
    parser = argparse.ArgumentParser(
        description="Quickly display and filter top pending graduation candidates from the Physics Lab backlog."
    )
    parser.add_argument(
        "-l", "--limit", type=int, default=20,
        help="Maximum number of candidates to display (default: 20)"
    )
    parser.add_argument(
        "-s", "--shard", type=str, default=None,
        help="Filter candidates by a specific shard file (e.g., astrophysics.json)"
    )
    parser.add_argument(
        "--legacy", action="store_true",
        help="Only show pending candidates that already exist as legacy-tier nodes in a shard"
    )
    parser.add_argument(
        "--uncreated", action="store_true",
        help="Only show pending candidates that do not exist yet in any shard"
    )
    parser.add_argument(
        "--no-color", action="store_true",
        help="Disable ANSI terminal colors in output"
    )
    
    args = parser.parse_args()
    
    # Global color disable flag
    global COLOR_HEADER, COLOR_TITLE, COLOR_SUCCESS, COLOR_WARNING, COLOR_FAIL, COLOR_RESET, COLOR_BOLD, COLOR_GRAY
    if args.no_color or sys.platform == "win32":
        COLOR_HEADER = COLOR_TITLE = COLOR_SUCCESS = COLOR_WARNING = COLOR_FAIL = COLOR_RESET = COLOR_BOLD = COLOR_GRAY = ""

    if not os.path.exists(BACKLOG_PATH):
        print(f"{COLOR_FAIL}Error: Backlog file not found at {BACKLOG_PATH}{COLOR_RESET}")
        sys.exit(1)
        
    try:
        with open(BACKLOG_PATH, "r") as f:
            backlog = json.load(f)
    except Exception as e:
        print(f"{COLOR_FAIL}Error loading backlog: {e}{COLOR_RESET}")
        sys.exit(1)
        
    # Filter for pending entries only
    pending = [x for x in backlog if x.get("status") == "pending"]
    if not pending:
        print(f"{COLOR_SUCCESS}✓ All expansion backlog items are fully graduated!{COLOR_RESET}")
        return

    # Load shard index from disk to cross-reference
    shard_map = load_shards()
    
    candidates = []
    for entry in pending:
        slug = entry.get("suggested_slug", "")
        term = entry.get("term", slug)
        freq = entry.get("frequency", 0)
        
        # Cross reference with physical shard data
        if slug in shard_map:
            shard_info = shard_map[slug]
            candidates.append({
                "slug": slug,
                "term": term,
                "frequency": freq,
                "shard": shard_info["shard"],
                "standard": shard_info["standard"],
                "exists": True
            })
        else:
            candidates.append({
                "slug": slug,
                "term": term,
                "frequency": freq,
                "shard": "[NEW/UNCREATED]",
                "standard": "n/a",
                "exists": False
            })
            
    # Apply filters
    if args.shard:
        target_shard = args.shard.lower()
        if not target_shard.endswith(".json"):
            target_shard += ".json"
        candidates = [x for x in candidates if x["shard"].lower() == target_shard]
        
    if args.legacy:
        candidates = [x for x in candidates if x["exists"] and x["standard"] == "legacy"]
        
    if args.uncreated:
        candidates = [x for x in candidates if not x["exists"]]
        
    # Sort candidates by frequency descending
    candidates.sort(key=lambda x: x["frequency"], reverse=True)
    
    # Slice to limit
    display_list = candidates[:args.limit]
    
    if not display_list:
        print(f"{COLOR_WARNING}No pending candidates found matching the active filters.{COLOR_RESET}")
        return
        
    # Print Table
    print("\n" + "="*95)
    print(f"{COLOR_TITLE} TOP PENDING GRADUATION CANDIDATES (Total Pending: {len(pending)}){COLOR_RESET}".center(95 + (len(COLOR_TITLE) + len(COLOR_RESET) if COLOR_TITLE else 0)))
    print("="*95)
    print(f"{COLOR_BOLD}{'Term Name':<32} | {'Slug':<28} | {'Freq':<5} | {'Shard / Placement':<20} | {'Standard'}{COLOR_RESET}")
    print("-"*95)
    
    for c in display_list:
        # Style standard labels
        if c["standard"] == "legacy":
            std_label = f"{COLOR_WARNING}legacy{COLOR_RESET}"
        elif c["standard"] == "standard":
            std_label = f"{COLOR_SUCCESS}standard{COLOR_RESET}"
        else:
            std_label = f"{COLOR_GRAY}n/a{COLOR_RESET}"
            
        # Style shard labels
        if c["exists"]:
            shard_label = f"{COLOR_RESET}{c['shard']}"
        else:
            shard_label = f"{COLOR_GRAY}[NEW NODE]{COLOR_RESET}"
            
        term_trimmed = c["term"][:32]
        print(f"{term_trimmed:<32} | {c['slug']:<28} | {c['frequency']:<5} | {shard_label:<20} | {std_label}")
        
    print("="*95 + "\n")

if __name__ == "__main__":
    main()
