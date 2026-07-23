import json
import re
import os
import glob

def count_unlinked_strongs(directory):
    total_unlinked = 0
    shard_counts = {}
    
    # load search index
    with open(os.path.join(directory, 'search_index.json'), 'r') as f:
        search_index = json.load(f)
    valid_slugs = set(search_index.keys())

    for filepath in glob.glob(os.path.join(directory, '*.json')):
        if 'search_index' in filepath or 'categories' in filepath or 'pillar_profiles' in filepath:
            continue
            
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except:
                continue
                
        shard_count = 0
        shard_name = os.path.basename(filepath)
        
        for slug, node in data.items():
            if node.get('standard') != 'platinum':
                continue
            content = node.get('content', '')
            if not content:
                continue
                
            paragraphs = content.split('</p>')
            linked_in_node = set()
            for p in paragraphs:
                if not p.strip():
                    continue
                
                strong_pattern = re.compile(r'<strong>(.*?)</strong>')
                i = 0
                while True:
                    match = strong_pattern.search(p, i)
                    if not match:
                        break
                    
                    start_idx = match.start()
                    inner_text = match.group(1)
                    
                    pre_text = p[:start_idx]
                    last_a_open = pre_text.rfind('<a')
                    last_a_close = pre_text.rfind('</a>')
                    
                    if last_a_open > last_a_close:
                        i = match.end()
                        continue
                        
                    target_slug = inner_text.lower().strip()
                    target_slug = re.sub(r'[^a-z0-9\s-]', '', target_slug)
                    target_slug = re.sub(r'[\s]+', '-', target_slug)
                    
                    if target_slug == "maxwell-equations" and "maxwells-equations" in valid_slugs:
                        target_slug = "maxwells-equations"
                    if target_slug == "lorentz-transformations" and "lorentz-transformation" in valid_slugs:
                        target_slug = "lorentz-transformation"
                    if target_slug == "gauss-law" and "gausss-law" in valid_slugs:
                        target_slug = "gausss-law"
                    if target_slug == "curie-temperature" and "curie-temp" in valid_slugs:
                         target_slug = "curie-temp"
                         
                    if target_slug in valid_slugs and target_slug != slug and target_slug not in linked_in_node:
                        shard_count += 1
                        total_unlinked += 1
                        linked_in_node.add(target_slug)
                        
                    i = match.end()
                    
        if shard_count > 0:
            shard_counts[shard_name] = shard_count
            
    print(f"Total unlinked valid strong tags: {total_unlinked}")
    for shard, count in sorted(shard_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {shard}: {count}")

count_unlinked_strongs('app/config/content')
