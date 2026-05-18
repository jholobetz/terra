import json
import re
import os
import glob
from collections import defaultdict

def generate_unlinked_freq(content_dir, output_file):
    # term -> number of nodes it appears in as unlinked strong
    term_freq = defaultdict(int)
    
    # Identify valid shards
    shard_files = [
        f for f in glob.glob(os.path.join(content_dir, '*.json'))
        if os.path.basename(f) not in ('search_index.json', 'categories.json', 'pillar_profiles.json', 'formulas.json', 'constants.json', 'entities.json')
    ]

    for filepath in shard_files:
        with open(filepath, 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {filepath}: invalid JSON")
                continue
                
        for slug, node in data.items():
            content = node.get('content', '')
            if not content:
                continue
                
            # Track terms seen in THIS node to satisfy "First Mention Only" logic
            unlinked_in_node = set()
            
            # Simple paragraph split to process safely
            paragraphs = content.split('</p>')
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
                    inner_text = match.group(1).strip()
                    
                    # Inside <a> check
                    pre_text = p[:start_idx]
                    last_a_open = pre_text.rfind('<a')
                    last_a_close = pre_text.rfind('</a>')
                    
                    if last_a_open > last_a_close:
                        # This strong is already linked, skip
                        i = match.end()
                        continue
                    
                    # Is this the first unlinked instance of this phrase in this node?
                    if inner_text and inner_text not in unlinked_in_node:
                        term_freq[inner_text] += 1
                        unlinked_in_node.add(inner_text)
                        
                    i = match.end()

    # Sort by frequency descending
    sorted_terms = dict(sorted(term_freq.items(), key=lambda item: item[1], reverse=True))
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(sorted_terms, f, indent=4)
        
    print(f"Discovered {len(sorted_terms)} unique unlinked terms across {len(shard_files)} shards.")
    print(f"Frequency map saved to {output_file}")

if __name__ == "__main__":
    generate_unlinked_freq('app/config/content', 'subfiles/unlinked_terms_freq.json')