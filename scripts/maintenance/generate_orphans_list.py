import os
import sys
import json
import re
from collections import defaultdict

def list_orphans():
    content_dir = "app/config/content"
    
    # Add root to sys.path so we can import orchestrator
    sys.path.append(os.getcwd())
    try:
        from orchestrator import PhysicsOrchestrator
    except ImportError:
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
        from orchestrator import PhysicsOrchestrator
        
    orch = PhysicsOrchestrator(content_dir=content_dir)
    all_subtopics = orch.data["subtopics"]
    
    incoming_links = defaultdict(int)
    link_pattern = re.compile(r'href=[\\"]+/physics/(subtopic|topic)/([^\\"]+)[\\"]+')
    
    # For every subtopic, look for links
    for shard_name, shard_data in orch.shards.items():
        for slug, sub in shard_data.items():
            if "content" not in sub:
                continue
            content = sub["content"]
            matches = link_pattern.findall(content)
            for _, target in matches:
                incoming_links[target] += 1
                
    # An orphan is a subtopic slug that has 0 incoming links (excluding utility shard notation entries)
    orphans = []
    for slug, sub in all_subtopics.items():
        if "content" in sub and incoming_links[slug] == 0:
            # Gather standard status, shard name, and title
            shard_name = "unknown"
            for s_name, shard_data in orch.shards.items():
                if slug in shard_data:
                    shard_name = s_name
                    break
            orphans.append({
                "slug": slug,
                "title": sub.get("title", ""),
                "standard": sub.get("standard", "legacy"),
                "shard": shard_name
            })
            
    # Sort orphans by shard, then by standard (platinum first), then alphabetically by slug
    orphans.sort(key=lambda x: (x["shard"], x["standard"] != "platinum", x["slug"]))
    
    # Save as JSON
    json_path = "subfiles/orphans.json"
    with open(json_path, "w") as f:
        json.dump(orphans, f, indent=4)
        
    # Save as MD
    md_path = "subfiles/orphans.md"
    with open(md_path, "w") as f:
        f.write("# 🌌 Physics Lab: Orphan Subtopics (0 Inbound Links)\n\n")
        f.write(f"Total Orphans Found: **{len(orphans)}**\n\n")
        f.write("Orphan subtopics have **0 inbound links** from other subtopics. Under the **Organic Platinum Standard (OPS)**, a graduated node must have a **minimum of 2 incoming links** and **1 cross-hub bridge**.\n\n")
        
        # Group by shard
        by_shard = defaultdict(list)
        for o in orphans:
            by_shard[o["shard"]].append(o)
            
        for shard_name in sorted(by_shard.keys()):
            f.write(f"## 📁 {shard_name}\n\n")
            f.write("| Subtopic Title | Slug | Standard |\n")
            f.write("| :--- | :--- | :--- |\n")
            for o in by_shard[shard_name]:
                std_badge = "🟢 `platinum`" if o["standard"] == "platinum" else "⚪ `legacy`"
                f.write(f"| {o['title']} | `{o['slug']}` | {std_badge} |\n")
            f.write("\n")
            
    print(f"SUCCESS: Found {len(orphans)} orphans.")
    print(f"Saved JSON list to: {json_path}")
    print(f"Saved Markdown report to: {md_path}")

if __name__ == "__main__":
    list_orphans()
