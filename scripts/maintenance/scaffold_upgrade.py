#!/usr/bin/env python3
"""
Scaffold Upgrade Utility
Finds substandard 'platinum' subtopics (low depth or low density) on disk and
scaffolds them into subfiles/batch_payload.json for expansion/rewriting to full OPS standards.
"""

import os
import sys
import json
import argparse
import subprocess
sys.path.append(os.getcwd())

from scripts.maintenance.generate_system_health import score_subtopic
from orchestrator import PhysicsOrchestrator

PAYLOAD_PATH = "subfiles/batch_payload.json"

def get_raw_latex_from_history(shard_name, slug):
    """Search git history for the most recent commit of shard_name where slug contains uncompiled LaTeX."""
    filepath = os.path.join("app/config/content", shard_name)
    cmd = ["git", "log", "--format=%H", "--", filepath]
    try:
        commits = subprocess.check_output(cmd, text=True).strip().split("\n")
    except Exception:
        return None
    for commit in commits:
        if not commit:
            continue
        try:
            show_cmd = ["git", "show", f"{commit}:{filepath}"]
            content_str = subprocess.check_output(show_cmd, text=True)
            data = json.loads(content_str)
            if slug in data:
                content = data[slug].get("content", "")
                if "\\(" in content or "\\[" in content or "$$" in content:
                    return content
        except Exception:
            continue
    return None

def main():
    parser = argparse.ArgumentParser(description="🪐 Physics Lab: Scaffold Substandard Platinum Nodes for Upgrade")
    parser.add_argument("--slug", type=str, help="Specific subtopic slug to scaffold")
    parser.add_argument("--shard", type=str, help="Filter substandard nodes by shard name (e.g., classical-mechanics.json)")
    parser.add_argument("--count", type=int, help="Number of worst-offending subtopics to scaffold")
    parser.add_argument("--list", action="store_true", help="List all substandard subtopics without scaffolding")
    parser.add_argument("--recover-latex", action="store_true", help="Attempt to recover uncompiled raw LaTeX draft from Git history")
    args = parser.parse_args()

    content_dir = "app/config/content"
    if not os.path.exists(content_dir):
        print(f"Error: Content directory {content_dir} not found.")
        sys.exit(1)

    print("Analyzing database shards for substandard platinum nodes...")
    orch = PhysicsOrchestrator(content_dir=content_dir)

    # 1. Resolve subtopic categories and parent hubs
    slug_to_cat = {}
    for cat_slug in orch.data["topics"]:
        shard_name = f"{cat_slug}.json"
        if shard_name in orch.shards:
            for sub_slug in orch.shards[shard_name]:
                slug_to_cat[sub_slug] = cat_slug
        slug_to_cat[cat_slug] = cat_slug

    substandard_nodes = []

    for shard_name, shard_data in orch.shards.items():
        if shard_name == "compiled_trie_regex.json":
            continue
        if args.shard and shard_name != args.shard and shard_name != f"{args.shard}.json":
            continue
        for slug, sub in shard_data.items():
            if "content" not in sub:
                continue

            # We only target nodes that are flagged as platinum but fail the strict quantitative gates
            if sub.get("standard") != "platinum":
                continue

            stats = score_subtopic(slug, sub, category=slug_to_cat.get(slug))
            
            # Substandard if words < 650 or density < density_target
            is_low_depth = stats["words"] < 650
            is_low_density = stats["density_score"] < stats["density_target"]

            if is_low_depth or is_low_density:
                substandard_nodes.append({
                    "slug": slug,
                    "title": sub.get("title", slug),
                    "shard": shard_name,
                    "parent_hub": slug_to_cat.get(slug, shard_name.replace(".json", "")),
                    "words": stats["words"],
                    "density": stats["density_score"],
                    "density_target": stats["density_target"],
                    "is_low_depth": is_low_depth,
                    "is_low_density": is_low_density,
                    "sub": sub
                })

    # Sort substandard nodes by a combined penalty score:
    # Lower word count and lower density get prioritized.
    # We normalize them: words/650 + density/density_target (lower is worse)
    def priority_score(node):
        w_ratio = min(1.0, node["words"] / 650.0)
        d_ratio = min(1.0, node["density"] / float(node["density_target"]))
        return w_ratio + d_ratio

    substandard_nodes.sort(key=priority_score)

    total_substandard = len(substandard_nodes)
    print(f"Found {total_substandard} substandard platinum nodes in total (either < 650 words or < density_target).")

    if args.list or (not args.slug and not args.count):
        # List mode
        print("\n" + "="*80)
        print(" TOP 20 SUBSTANDARD PLATINUM NODES:".center(80))
        print("="*80)
        print(f"{'Index':<5} | {'Slug':<30} | {'Words':<6} | {'Density':<7} | {'Defect(s)'}")
        print("-"*80)
        for i, node in enumerate(substandard_nodes[:20]):
            defects = []
            if node["is_low_depth"]:
                defects.append(f"Low Depth ({node['words']}/650)")
            if node["is_low_density"]:
                defects.append(f"Low Density ({node['density']}/{node['density_target']})")
            defects_str = ", ".join(defects)
            print(f"{i+1:02d}    | {node['slug']:<30} | {node['words']:<6} | {node['density']:<7} | {defects_str}")
        print("="*80)
        print("\n👉 To scaffold nodes for upgrading, run:")
        print("   .venv/bin/python3 scripts/maintenance/scaffold_upgrade.py --count N  (scaffolds the top N worst nodes)")
        print("   .venv/bin/python3 scripts/maintenance/scaffold_upgrade.py --slug <slug>  (scaffolds a specific node)")
        sys.exit(0)

    # Scaffolding mode
    targets = []
    if args.slug:
        # Find specific slug
        match = next((n for n in substandard_nodes if n["slug"] == args.slug), None)
        if not match:
            print(f"Error: Specific slug '{args.slug}' is not classified as substandard, or doesn't exist.")
            sys.exit(1)
        targets = [match]
    elif args.count:
        targets = substandard_nodes[:args.count]

    # Load existing payload or initialize empty
    payload = {}
    if os.path.exists(PAYLOAD_PATH):
        try:
            with open(PAYLOAD_PATH, "r") as f:
                payload = json.load(f)
        except Exception:
            payload = {}

    print(f"\nScaffolding {len(targets)} subtopics into {PAYLOAD_PATH}...")

    for node in targets:
        slug = node["slug"]
        sub = node["sub"]
        
        content = sub.get("content", "")
        recovered = False
        if args.recover_latex:
            print(f"🔍 Searching Git history for raw LaTeX content for '{slug}'...")
            hist_content = get_raw_latex_from_history(node["shard"], slug)
            if hist_content:
                content = hist_content
                recovered = True
                print(f"  ✓ Recovered uncompiled LaTeX draft from Git history.")
            else:
                print(f"  ⚠️ Could not find uncompiled historical LaTeX. Falling back to current SVG content.")
        
        # Keep identities empty so the compiler preserves existing formula registrations in the shard.
        payload[slug] = {
            "title": sub.get("title", slug),
            "content": content,
            "standard": "platinum",
            "parents": sub.get("parents", [node["parent_hub"]]),
            "identities": []
        }
        
        print(f"  * Scaffolded: \033[1m{slug}\033[0m")
        print(f"      Current Word Count: {node['words']} (Needs {650 - node['words']}+ words to reach 650)")
        print(f"      Current Density: {node['density']} (Needs to reach {node['density_target']})")

    with open(PAYLOAD_PATH, "w") as f:
        json.dump(payload, f, indent=4)

    print(f"\n✓ SUCCESS: Saved {len(targets)} targets to {PAYLOAD_PATH}.")
    print("👉 Edit subfiles/batch_payload.json to expand/upgrade the prose & math.")
    print("👉 When ready, run:")
    print("   .venv/bin/python3 scripts/maintenance/run_gqs_sprint.py")


if __name__ == "__main__":
    main()
