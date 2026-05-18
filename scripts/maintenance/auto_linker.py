import json
import re
import os

def normalize_slug(text):
    # Basic normalization: lower, strip whitespace, spaces to hyphens
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s

def run_auto_linker(shards, index_path):
    # Load search index
    with open(index_path, 'r') as f:
        search_index = json.load(f)

    valid_slugs = set(search_index.keys())

    # Load global aliases
    aliases = {}
    alias_path = 'subfiles/auto_link_aliases.json'
    if os.path.exists(alias_path):
        with open(alias_path, 'r') as f:
            aliases = json.load(f)

    for shard_path in shards:
        if not os.path.exists(shard_path):
            continue
        
        with open(shard_path, 'r') as f:
            shard = json.load(f)
        
        modified_shard = False
        for slug, data in shard.items():
            if data.get('standard') != 'platinum':
                continue
                
            content = data.get('content', '')
            if not content:
                continue
                
            # Use a more robust regex that ensures <strong> is NOT inside <a>
            # But regex with lookbehinds/aheads for HTML is notoriously difficult.
            # Instead, we'll split by tags and process.
            
            # Simple approach: if a <strong> is found, check the full string for its context.
            # Better approach: parse with a state machine or just be very careful with indices.
            
            paragraphs = content.split('</p>')
            new_paragraphs = []
            linked_in_node = set()
            
            for p in paragraphs:
                if not p.strip():
                    continue
                
                # We will process each paragraph by finding all <strong> tags
                # and replacing them only if they are not preceded by an open <a> tag
                # in the current state of the paragraph.
                
                strong_pattern = re.compile(r'<strong>(.*?)</strong>')
                
                # We'll use a while loop to handle changing string length
                i = 0
                while True:
                    match = strong_pattern.search(p, i)
                    if not match:
                        break
                    
                    start_idx = match.start()
                    inner_text = match.group(1)
                    full_tag = match.group(0)
                    
                    # Robust "is inside <a>" check:
                    # Look at everything before this match. 
                    # If the last '<a' occurs after the last '</a>', we are inside a link.
                    pre_text = p[:start_idx]
                    last_a_open = pre_text.rfind('<a')
                    last_a_close = pre_text.rfind('</a>')
                    
                    if last_a_open > last_a_close:
                        # Inside a link, skip this <strong>
                        i = match.end()
                        continue
                    
                    target_slug = aliases.get(inner_text)
                    if not target_slug:
                        target_slug = normalize_slug(inner_text)
                    
                    if target_slug in valid_slugs and target_slug != slug and target_slug not in linked_in_node:
                        link_tag = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{inner_text}</strong></a>'
                        p = p[:start_idx] + link_tag + p[match.end():]
                        linked_in_node.add(target_slug)
                        print(f"Linked '{inner_text}' -> '{target_slug}' in {slug}")
                        i = start_idx + len(link_tag) # Move past the new link
                    else:
                        i = match.end() # Move past this <strong> without linking
                
                new_paragraphs.append(p)
                
            new_content = '</p>'.join(new_paragraphs)
            if len(new_paragraphs) > 0:
                new_content += '</p>'
                
            if new_content != content:
                shard[slug]['content'] = new_content
                modified_shard = True

        if modified_shard:
            with open(shard_path, 'w') as f:
                json.dump(shard, f, indent=4)
            print(f"Repaired and updated links in {shard_path}")

if __name__ == "__main__":
    import glob
    content_dir = 'app/config/content'
    shards_to_process = [
        f for f in glob.glob(os.path.join(content_dir, '*.json'))
        if os.path.basename(f) not in ('search_index.json', 'categories.json', 'pillar_profiles.json')
    ]
    run_auto_linker(shards_to_process, os.path.join(content_dir, 'search_index.json'))
