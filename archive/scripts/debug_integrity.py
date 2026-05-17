import json
import os
import re

def debug_integrity():
    with open('app/config/content/categories.json', 'r') as f:
        categories = json.load(f)
    
    all_slugs = set()
    shards = []
    for cat in categories:
        shard_path = f"app/config/content/{cat['slug']}.json"
        if os.path.exists(shard_path):
            shards.append(shard_path)
            with open(shard_path, 'r') as f:
                data = json.load(f)
                for sub in data:
                    all_slugs.add(sub['slug'])

    with open('app/config/content/formulas.json', 'r') as f:
        formulas = json.load(f)
    formula_registry = set(formulas.keys())

    link_pattern = re.compile(r'<a href="/physics/subtopic/([^"]+)"')

    print("--- Integrity Debug Report ---")
    
    for shard_path in shards:
        with open(shard_path, 'r') as f:
            data = json.load(f)
            for sub in data:
                slug = sub['slug']
                content = sub.get('content', '')
                
                # Check links
                links = link_pattern.findall(content)
                for target in links:
                    if target not in all_slugs:
                        print(f"BROKEN LINK in [{slug}]: target '{target}' not found.")
                
                # Check formulas
                for f_id in sub.get('formula_ids', []):
                    if f_id not in formula_registry:
                        print(f"BROKEN FORMULA in [{slug}]: formula ID '{f_id}' not found.")

if __name__ == "__main__":
    debug_integrity()
