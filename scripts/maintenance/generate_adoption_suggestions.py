import os
import sys
import json
import re
from collections import defaultdict

# Add root directory to path so we can import orchestrator
sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

def clean_and_tokenize(text):
    """Simple stopword-filtered tokenization for similarity comparison."""
    if not text:
        return set()
    # Strip HTML tags
    clean_text = re.sub(r'<[^>]+>', ' ', text.lower())
    # Keep only alphabetic characters
    words = re.findall(r'[a-z]{3,}', clean_text)
    # Filter common stopwords
    stop_words = {
        "the", "and", "for", "with", "that", "this", "these", "those",
        "from", "into", "onto", "upon", "about", "above", "below",
        "have", "has", "had", "will", "would", "shall", "should", "can",
        "could", "are", "was", "were", "been", "their", "them", "they",
        "its", "our", "your", "his", "her", "than", "thus", "therefore",
        "here", "there", "where", "when", "why", "how", "what", "which",
        "other", "some", "such", "only", "same", "also", "each", "both"
    }
    return set(w for w in words if w not in stop_words)

def main():
    content_dir = "app/config/content"
    orch = PhysicsOrchestrator(content_dir=content_dir)
    all_subtopics = orch.data["subtopics"]
    
    # Reload live orphans
    # Scan all shards to get fresh incoming links counts
    incoming_links = defaultdict(int)
    link_pattern = re.compile(r'href=[\\"]+/physics/(subtopic|topic)/([^\\"]+)[\\"]+')
    
    for shard_name, shard_data in orch.shards.items():
        for slug, sub in shard_data.items():
            content = sub.get("content", "")
            matches = link_pattern.findall(content)
            for _, target in matches:
                incoming_links[target] += 1
                
    # Filter orphans
    orphans = []
    for slug, sub in all_subtopics.items():
        if incoming_links[slug] == 0:
            # Locate shard
            shard_name = "unknown"
            for s_name, shard_data in orch.shards.items():
                if slug in shard_data:
                    shard_name = s_name
                    break
            orphans.append({
                "slug": slug,
                "title": sub.get("title", ""),
                "shard": shard_name
            })
            
    orphans.sort(key=lambda x: (x["shard"], x["slug"]))
    
    # Tokenize all platinum subtopics once for speed
    tokenized_subtopics = {}
    for slug, sub in all_subtopics.items():
        tokenized_subtopics[slug] = clean_and_tokenize(sub.get("content", ""))
        
    suggestions_map = {}
    
    for o in orphans:
        orphan_slug = o["slug"]
        orphan_title = o["title"]
        orphan_shard = o["shard"]
        orphan_tokens = tokenized_subtopics.get(orphan_slug, set())
        
        candidates = []
        
        for parent_slug, parent_tokens in tokenized_subtopics.items():
            if parent_slug == orphan_slug:
                continue
                
            parent_sub = all_subtopics[parent_slug]
            
            # Find shard of parent
            parent_shard = "unknown"
            for s_name, shard_data in orch.shards.items():
                if parent_slug in shard_data:
                    parent_shard = s_name
                    break
                    
            # Compute token overlap similarity
            overlap = len(orphan_tokens.intersection(parent_tokens))
            
            # Apply Scoring Adjustments:
            score = overlap
            explanation = f"{overlap} overlapping terms"
            
            # 1. Shard Category Boost (+50 points to prioritize local category link)
            if parent_shard == orphan_shard:
                score += 50
                explanation += " + Category Boost"
                
            # 2. Overview Node Boost (+100 points for category overview)
            shard_base = orphan_shard.replace(".json", "")
            if parent_slug == f"{shard_base}-overview":
                score += 100
                explanation += " + Hub Overview Boost"
                
            # Skip if score is 0 and not the overview
            if score <= 0:
                continue
                
            candidates.append({
                "slug": parent_slug,
                "title": parent_sub.get("title", parent_slug),
                "shard": parent_shard,
                "score": score,
                "explanation": explanation
            })
            
        # Sort candidates by score descending
        candidates.sort(key=lambda x: x["score"], reverse=True)
        suggestions_map[orphan_slug] = candidates[:5]
        
    # Write JSON results
    with open("subfiles/adoption_suggestions.json", "w") as f:
        json.dump(suggestions_map, f, indent=4)
        
    # Write Markdown report
    with open("subfiles/adoption_suggestions.md", "w") as f:
        f.write("# 📂 Physics Lab: Adoptive Parent Suggestions for Orphans\n\n")
        f.write(f"Total Orphans Analyzed: **{len(orphans)}**\n\n")
        f.write("This report lists the top 5 suggested parent nodes for each orphan subtopic, calculated via token-overlap similarity, shard category alignment, and overview-hub boosts.\n\n")
        
        # Group by shard
        by_shard = defaultdict(list)
        for o in orphans:
            by_shard[o["shard"]].append(o)
            
        for shard_name in sorted(by_shard.keys()):
            f.write(f"## 📁 {shard_name}\n\n")
            
            for o in by_shard[shard_name]:
                slug = o["slug"]
                f.write(f"### 📭 `{slug}`: {o['title']}\n")
                f.write("| Suggested Parent Slug | Title | Shard | Score | Explanation |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- |\n")
                
                sugs = suggestions_map.get(slug, [])
                for s in sugs:
                    f.write(f"| `{s['slug']}` | {s['title']} | `{s['shard']}` | {s['score']} | {s['explanation']} |\n")
                f.write("\n")
                
    print(f"SUCCESS: Generated suggestions for {len(orphans)} orphans.")
    print("Saved JSON map to subfiles/adoption_suggestions.json")
    print("Saved Markdown report to subfiles/adoption_suggestions.md")

if __name__ == "__main__":
    main()
