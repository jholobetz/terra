#!/usr/bin/env python3
"""
Pillar 3: Live Quality Gate Compliance Watcher
Monitors subfiles/batch_payload.json and prints a real-time compliance scorecard.
Optionally supports --autofix to format neighbor links.
"""

import os
import sys
import json
import argparse
import subprocess

sys.path.append(os.getcwd())
from scripts.maintenance.generate_system_health import score_subtopic
from scripts.maintenance.format_neighbors import format_draft, load_aliases
from orchestrator import PhysicsOrchestrator

PAYLOAD_PATH = "subfiles/batch_payload.json"
CONTENT_DIR = "app/config/content"

def print_scorecard(payload, slug_to_cat):
    print("\n" + "="*95)
    print(" GQS DRAFT COMPLIANCE WATCHER SCORECARD ".center(95, "="))
    print("="*95)
    print(f"{'Subtopic Slug':<32} | {'Word Count':<12} | {'Math Density':<14} | {'Lead-Rule':<10} | {'List/Heading':<12} | {'Status'}")
    print("-"*95)
    
    all_passed = True
    for slug, sub in payload.items():
        cat = slug_to_cat.get(slug)
        s = score_subtopic(slug, sub, category=cat)
        
        # Word count check
        words_status = f"{s['words']} / 650"
        words_ok = s['words'] >= 650
        
        # Density check
        density_status = f"{s['density_score']} / {s['density_target']}"
        density_ok = s['density_score'] >= s['density_target']
        
        # Lead rule check
        lead_status = "✗ Fail" if s['has_lead_violation'] else "✓ Pass"
        lead_ok = not s['has_lead_violation']
        
        # List/Heading check
        lh_status = "✗ Fail" if s['has_artifact_violation'] else "✓ Pass"
        lh_ok = not s['has_artifact_violation']
        
        # Overall status
        is_ready = words_ok and density_ok and lead_ok and lh_ok
        status_str = "READY" if is_ready else "VIOLATION"
        
        if not is_ready:
            all_passed = False
            
        # Add colored markers for terminal output
        # green for READY, red for VIOLATION, red for Fail
        green = "\033[92m"
        red = "\033[91m"
        reset = "\033[0m"
        bold = "\033[1m"
        
        words_color = green if words_ok else red
        density_color = green if density_ok else red
        lead_color = green if lead_ok else red
        lh_color = green if lh_ok else red
        status_color = green + bold if is_ready else red + bold
        
        print(f"{slug:<32} | "
              f"{words_color}{words_status:<12}{reset} | "
              f"{density_color}{density_status:<14}{reset} | "
              f"{lead_color}{lead_status:<10}{reset} | "
              f"{lh_color}{lh_status:<12}{reset} | "
              f"{status_color}{status_str}{reset}")
              
    print("="*95)
    return all_passed

def main():
    parser = argparse.ArgumentParser(description="🪐 check_draft_compliance: Live Quality Gate Compliance Watcher")
    parser.add_argument("--autofix", action="store_true", help="Automatically format neighbor links before checking compliance")
    args = parser.parse_args()

    if not os.path.exists(PAYLOAD_PATH):
        print(f"Error: Batch payload file '{PAYLOAD_PATH}' not found.")
        sys.exit(1)

    with open(PAYLOAD_PATH, "r") as f:
        try:
            payload = json.load(f)
        except Exception as e:
            print(f"Error parsing '{PAYLOAD_PATH}': {e}")
            sys.exit(1)

    if not payload:
        print("Notice: batch_payload.json is empty. No drafts to check.")
        sys.exit(0)

    orch = PhysicsOrchestrator(content_dir=CONTENT_DIR)
    
    # Resolve subtopic category mapping
    slug_to_cat = {}
    for cat_slug in orch.data["topics"]:
        shard_name = f"{cat_slug}.json"
        if shard_name in orch.shards:
            for sub_slug in orch.shards[shard_name]:
                slug_to_cat[sub_slug] = cat_slug
        slug_to_cat[cat_slug] = cat_slug

    if args.autofix:
        print("\n⚡ Running Pillar 2: Auto-formatting neighbor links...")
        search_index_path = os.path.join(CONTENT_DIR, "search_index.json")
        with open(search_index_path, "r") as f:
            search_index = json.load(f)
        aliases = load_aliases()
        
        for slug in list(payload.keys()):
            payload[slug] = format_draft(slug, payload[slug], search_index, aliases)
            
        with open(PAYLOAD_PATH, "w") as f:
            json.dump(payload, f, indent=4)
        print("✓ Saved auto-formatted drafts back to batch_payload.json.\n")

    all_passed = print_scorecard(payload, slug_to_cat)
    
    if all_passed:
        print("\n🎉 All drafts are fully compliant and ready for graduation!")
        sys.exit(0)
    else:
        print("\n⚠️ Violations found. Please correct them in subfiles/batch_payload.json before graduating.")
        sys.exit(1)

if __name__ == "__main__":
    main()
