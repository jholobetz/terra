#!/usr/bin/env python3
"""
Pillar 1: Automated Historical LaTeX Recovery Utility
Queries the git repository for the most recent commit of a shard where the
target subtopic's content contains uncompiled LaTeX math, and outputs the raw HTML.
"""

import os
import sys
import json
import argparse
import subprocess

sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

def get_raw_latex_from_history(content_dir, shard_name, slug):
    filepath = os.path.join(content_dir, shard_name)
    cmd = ["git", "log", "--format=%H", "--", filepath]
    try:
        commits = subprocess.check_output(cmd, text=True).strip().split("\n")
    except Exception as e:
        print(f"Git log failed: {e}", file=sys.stderr)
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
    parser = argparse.ArgumentParser(description="Query git history for uncompiled LaTeX content of a subtopic.")
    parser.add_argument("slug", type=str, help="Subtopic slug to recover")
    parser.add_argument("--output", type=str, help="Output file path (default: print to stdout)")
    args = parser.parse_args()

    content_dir = "app/config/content"
    if not os.path.exists(content_dir):
        print(f"Error: Content directory {content_dir} not found.", file=sys.stderr)
        sys.exit(1)

    orch = PhysicsOrchestrator(content_dir=content_dir)
    target_shard = None
    for shard_name, shard_data in orch.shards.items():
        if shard_name == "compiled_trie_regex.json":
            continue
        if args.slug in shard_data:
            target_shard = shard_name
            break

    if not target_shard:
        print(f"Error: Slug '{args.slug}' not found in any database shard.", file=sys.stderr)
        sys.exit(1)

    print(f"Found slug '{args.slug}' in shard '{target_shard}'. Searching git log...", file=sys.stderr)
    raw_content = get_raw_latex_from_history(content_dir, target_shard, args.slug)

    if not raw_content:
        print(f"Error: Could not find uncompiled LaTeX history for '{args.slug}'.", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w") as f:
            f.write(raw_content)
        print(f"✓ Recovered LaTeX written to: {args.output}", file=sys.stderr)
    else:
        print(raw_content)

if __name__ == "__main__":
    main()
