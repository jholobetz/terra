import json
import os
import re

def debug_integrity():
    with open('app/config/content/categories.json', 'r') as f:
        categories = json.load(f)
    
    all_slugs = set()
    shards = []
    for cat_slug, info in categories.items():
        # Shard paths are actually in app/config/content/ or app/config/content/topics/
        # categories.json says "topics/classical-mechanics.json"
        shard_rel_path = info['shard']
        shard_path = os.path.join('app/config/content', shard_rel_path)
        
        if os.path.exists(shard_path):
            shards.append((cat_slug, shard_path))
            with open(shard_path, 'r') as f:
                data = json.load(f)
                for sub in data:
                    all_slugs.add(sub['slug'])
        else:
            print(f"WARNING: Shard path {shard_path} not found.")

    formula_path = 'app/config/content/formulas.json'
    if os.path.exists(formula_path):
        with open(formula_path, 'r') as f:
            formulas = json.load(f)
        formula_registry = set(formulas.keys())
    else:
        print(f"WARNING: Formulas file {formula_path} not found.")
        formula_registry = set()

    link_pattern = re.compile(r'<a href="/physics/subtopic/([^"]+)"')

    print("--- Integrity Debug Report ---")
    
    broken_links_count = 0
    broken_formulas_count = 0

    for cat_slug, shard_path in shards:
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
                        broken_links_count += 1
                
                # Check formulas
                for f_id in sub.get('formula_ids', []):
                    if f_id not in formula_registry:
                        print(f"BROKEN FORMULA in [{slug}]: formula ID '{f_id}' not found.")
                        broken_formulas_count += 1
    
    print(f"Total Broken Links: {broken_links_count}")
    print(f"Total Broken Formulas: {broken_formulas_count}")

if __name__ == "__main__":
    debug_integrity()
