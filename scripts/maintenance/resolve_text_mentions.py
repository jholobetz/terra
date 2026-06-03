import os
import sys
import json
import re
import glob
from collections import defaultdict

# Add root directory to path
sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

def safe_wrap_term_in_strong(html_content, term):
    """Safely wraps the first plain-text occurrence of a term in <strong> tags,

    avoiding existing HTML tags and active links.
    """
    # Split HTML into tags and text segments
    parts = re.split(r'(<[^>]+>)', html_content)
    
    for i in range(len(parts)):
        # Even indices represent plain text, odd indices represent HTML tags
        if i % 2 == 0:
            text = parts[i]
            # Use word boundary to match exact terms case-insensitively
            pattern = r'\b(' + re.escape(term) + r')\b'
            
            # Search for the term in the plain text segment
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Check if we are currently inside an active <a> link
                preceding_html = "".join(parts[:i])
                last_a_open = preceding_html.rfind('<a')
                last_a_close = preceding_html.rfind('</a>')
                
                # If the last opened link is not closed, we are inside an <a> block
                if last_a_open > last_a_close:
                    continue
                
                # Wrap the first occurrence in <strong>
                wrapped_text = re.sub(pattern, r'<strong>\1</strong>', text, count=1, flags=re.IGNORECASE)
                parts[i] = wrapped_text
                return "".join(parts), True
                
    return html_content, False

def main():
    content_dir = "app/config/content"
    orch = PhysicsOrchestrator(content_dir=content_dir)
    
    # Load orphans
    with open("subfiles/orphans.json", "r") as f:
        orphans = json.load(f)
        
    # Load aliases mapping
    aliases = {}
    alias_path = 'subfiles/auto_link_aliases.json'
    if os.path.exists(alias_path):
        with open(alias_path, 'r') as f:
            aliases = json.load(f)
            
    registry_path = 'global_slug_registry.json'
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            registry = json.load(f)
            aliases.update(registry)
            
    # Reverse aliases mapping: slug -> list of alias terms
    slug_aliases = defaultdict(list)
    for term, slug in aliases.items():
        slug_aliases[slug].append(term)
        
    # For every orphan, compile its search terms (title + aliases)
    orphan_terms = {}
    for o in orphans:
        slug = o["slug"]
        terms = [o["title"]]
        if slug in slug_aliases:
            terms.extend(slug_aliases[slug])
        # De-duplicate and filter short terms
        terms = list(set([t.lower().strip() for t in terms if t and len(t) > 2]))
        orphan_terms[slug] = terms
        
    # We will walk through all shards and modify them in memory first
    shards_modified = set()
    adopted_orphans = set()
    
    for shard_path, shard_data in orch.shards.items():
        modified_shard = False
        
        for parent_slug, parent_data in shard_data.items():
            content = parent_data.get("content", "")
            if not content:
                continue
                
            # Try to match any orphan
            for o in orphans:
                orphan_slug = o["slug"]
                if parent_slug == orphan_slug:
                    continue
                
                # Check search terms for this orphan
                terms = orphan_terms[orphan_slug]
                wrapped = False
                
                for term in terms:
                    new_content, success = safe_wrap_term_in_strong(content, term)
                    if success:
                        content = new_content
                        wrapped = True
                        print(f"Adopted orphan '{orphan_slug}' in '{parent_slug}' by wrapping '{term}' in <strong>.")
                        adopted_orphans.add(orphan_slug)
                        break # Done with this orphan in this parent
                
                if wrapped:
                    parent_data["content"] = content
                    modified_shard = True
                    
        if modified_shard:
            shards_modified.add(shard_path)
            
    # Save modified shards back to disk
    for shard_path in shards_modified:
        full_path = os.path.join(content_dir, shard_path)
        with open(full_path, 'w') as f:
            # We must output the updated shard content from orch.shards
            # Find the match
            for name, shard_data in orch.shards.items():
                if name == shard_path:
                    json.dump(shard_data, f, indent=4)
                    print(f"Saved updated shard: {full_path}")
                    break
                    
    print(f"\n==================================================")
    print(f"PHASE 1 SUMMARY:")
    print(f"  * Total Orphans Processed: {len(orphans)}")
    print(f"  * Total Orphans Adopted:   {len(adopted_orphans)}")
    print(f"  * Shards Modified:         {len(shards_modified)}")
    print(f"==================================================")

if __name__ == "__main__":
    main()
