#!/usr/bin/env python3
"""
🪐 Physics Lab: Resumable Critic Cache Warmer
Scans content shards for unverified, uncached subtopics,
queries live academic APIs with polite rate-limiting, and
saves literature records incrementally to the literature cache.
"""

import os
import sys
import json
import re
import time
import argparse

# Set up project root in path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.append(PROJECT_ROOT)

from scripts.maintenance.run_critic import MultiAgentCritic

def get_unverified_uncached_slugs(critic):
    """Finds all slugs that are unverified in content shards and not present in the literature cache."""
    unverified_slugs = []
    
    # Iterate through all shards mapped in slug_shard_map
    for slug, shard_file in critic.slug_shard_map.items():
        # Skip if already cached
        if slug in critic.literature_cache:
            continue
            
        shard_path = os.path.join(critic.content_dir, shard_file)
        if not os.path.exists(shard_path):
            continue
            
        try:
            with open(shard_path, "r") as f:
                shard_data = json.load(f)
            node = shard_data.get(slug)
            if node and isinstance(node, dict) and "verification" not in node:
                unverified_slugs.append((slug, shard_file, node))
        except Exception:
            continue
            
    return unverified_slugs

def warm_cache():
    parser = argparse.ArgumentParser(description="Politely warm up the literature cache for unverified subtopics.")
    parser.add_argument("-l", "--limit", type=int, default=20, help="Maximum number of new subtopics to query in this run.")
    parser.add_argument("-d", "--delay", type=float, default=4.0, help="Polite delay in seconds between queries.")
    args = parser.parse_args()

    critic = MultiAgentCritic()
    
    print("🔍 Scanning content shards for unverified, uncached subtopics...")
    candidates = get_unverified_uncached_slugs(critic)
    total_candidates = len(candidates)
    
    print(f"📊 Found {total_candidates} unverified, uncached subtopic(s) total.")
    if total_candidates == 0:
        print("✓ All active subtopics are already cached or verified! Nothing to warm.")
        return

    to_process = candidates[:args.limit]
    print(f"🚀 Starting ingestion for up to {len(to_process)} subtopic(s) in this batch (polite delay: {args.delay}s)...")
    
    success_count = 0
    
    for idx, (slug, shard_file, node) in enumerate(to_process):
        title = node.get("title", slug)
        content = node.get("content", "")
        formula_ids = node.get("formula_ids", [])
        parents = node.get("parents", [])
        
        # Extract context
        neighbors = []
        for match in re.finditer(r'href="/physics/subtopic/([^"]+)"', content):
            neighbors.append(match.group(1))
        neighbor_names = [n.replace("-", " ") for n in set(neighbors)]
        latex_equations = re.findall(r'data-tex="([^"]+)"', content)
        
        context = {
            "slug": slug,
            "shard": shard_file,
            "formula_ids": formula_ids,
            "parents": parents,
            "neighbors": neighbor_names,
            "equations": latex_equations,
            "domain": shard_file.replace(".json", "")
        }
        
        # Step 1: Claim Extraction
        claims = critic.extract_claims(content)
        
        print(f"\n────────────────────────────────────────────────────────────────────────────────")
        print(f"[{idx+1}/{len(to_process)}] Harvesting literature for '{title}' ({slug}) in {shard_file}...")
        
        # Combine all literature retrieved across search strategies to form a robust cache
        combined_literature = []
        strategies = ["default", "domain", "title_only"]
        
        for strategy in strategies:
            search_query = critic.formulate_query(title, claims, strategy, context)
            print(f"  📡 Querying '{strategy}': '{search_query}'...")
            
            try:
                # Retrieve from live APIs
                lit = critic.get_literature_live(slug, search_query, context)
                combined_literature.extend(lit)
                print(f"    ↳ Retrieved {len(lit)} paper(s).")
            except Exception as e:
                print(f"    ❌ Error during API query: {e}")
            
            # Rate-limiting delay between strategies
            time.sleep(args.delay)
            
        # Deduplicate combined literature based on normalized title
        seen_titles = set()
        deduped_literature = []
        for paper in combined_literature:
            norm_title = paper["title"].lower().strip()
            norm_title = re.sub(r'[^\w\s]', '', norm_title)
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                deduped_literature.append(paper)
                
        print(f"✓ Cached {len(deduped_literature)} unique paper(s) total for '{slug}'.")
        
        # Write to cache
        critic.literature_cache[slug] = deduped_literature
        try:
            with open(critic.cache_path, "w") as f:
                json.dump(critic.literature_cache, f, indent=2)
            success_count += 1
        except Exception as e:
            print(f"❌ Error writing literature cache file: {e}")
            
        # Generous cooldown between subtopics
        time.sleep(args.delay * 1.5)

    print("\n================================================================================")
    print(f"✓ WARMER COMPLETE: Successfully cached {success_count}/{len(to_process)} subtopics in this batch.")
    print("================================================================================")


if __name__ == "__main__":
    warm_cache()

