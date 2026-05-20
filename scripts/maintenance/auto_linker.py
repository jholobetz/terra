import json
import re
import os
import glob

def normalize_slug(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s

def run_auto_linker(shards, index_path):
    with open(index_path, 'r') as f:
        search_index = json.load(f)
    valid_slugs = set(search_index.keys())

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

    # REFINED Link pattern to handle both normal and escaped quotes in JSON
    # This matches <a href="SLUG" class="class">TEXT</a> and variants
    link_pattern = re.compile(r'<a\s+href=[\\"]+([^\\"]+)[\\"]+[^>]*>(.*?)</a>')

    for shard_path in shards:
        if not os.path.exists(shard_path): continue
        with open(shard_path, 'r') as f:
            shard = json.load(f)
        
        modified_shard = False
        for slug, data in shard.items():
            content = data.get('content', '')
            if not content: continue
            
            linked_in_node = set()
            
            # PASS 1: Identify existing links, de-duplicate, and REPAIR them
            paragraphs = content.split('</p>')
            new_paragraphs_pass1 = []
            
            for p in paragraphs:
                if not p.strip(): continue
                
                i = 0
                new_p = ""
                while True:
                    match = link_pattern.search(p, i)
                    if not match:
                        new_p += p[i:]
                        break
                    
                    full_href = match.group(1)
                    target_slug = full_href.split('/')[-1]
                    inner_content = match.group(2)
                    
                    new_p += p[i:match.start()]
                    
                    if target_slug in linked_in_node or target_slug == slug:
                        clean_inner = inner_content.replace('<strong>', '').replace('</strong>', '')
                        new_p += f'<strong>{clean_inner}</strong>'
                        modified_shard = True
                        print(f"Downgraded redundant link to '{target_slug}' in {slug}")
                    else:
                        if '<strong>' not in inner_content:
                            inner_content = f'<strong>{inner_content}</strong>'
                        
                        repair_link = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link">{inner_content}</a>'
                        new_p += repair_link
                        linked_in_node.add(target_slug)
                        # Be careful with comparison because of escaping
                        # We just check if the new link is technically different from the match
                        # But for simplicity, we always replace in Pass 1 if it's the first mention
                        # to ensure consistency.
                        print(f"Standardized link for '{target_slug}' in {slug}")
                        modified_shard = True
                    
                    i = match.end()
                new_paragraphs_pass1.append(new_p)

            content_pass1 = '</p>'.join(new_paragraphs_pass1)
            if len(new_paragraphs_pass1) > 0: content_pass1 += '</p>'

            # PASS 2: Auto-link bolded terms
            new_paragraphs_pass2 = []
            strong_pattern = re.compile(r'<strong>(.*?)</strong>')
            
            for p in content_pass1.split('</p>'):
                if not p.strip(): continue
                
                i = 0
                while True:
                    match = strong_pattern.search(p, i)
                    if not match: break
                    
                    start_idx = match.start()
                    inner_text = match.group(1)
                    
                    pre_text = p[:start_idx]
                    if pre_text.rfind('<a') > pre_text.rfind('</a>'):
                        i = match.end()
                        continue
                    
                    target_slug = aliases.get(inner_text)
                    if not target_slug: target_slug = normalize_slug(inner_text)
                    
                    if target_slug in valid_slugs and target_slug != slug and target_slug not in linked_in_node:
                        link_tag = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{inner_text}</strong></a>'
                        p = p[:start_idx] + link_tag + p[match.end():]
                        linked_in_node.add(target_slug)
                        print(f"Linked '{inner_text}' -> '{target_slug}' in {slug}")
                        i = start_idx + len(link_tag)
                        modified_shard = True
                    else:
                        i = match.end()
                new_paragraphs_pass2.append(p)
                
            final_content = '</p>'.join(new_paragraphs_pass2)
            if len(new_paragraphs_pass2) > 0: final_content += '</p>'
            
            if final_content != content:
                shard[slug]['content'] = final_content
                modified_shard = True

        if modified_shard:
            with open(shard_path, 'w') as f:
                json.dump(shard, f, indent=4)
            print(f"Cleaned, repaired and updated links in {shard_path}")

if __name__ == "__main__":
    content_dir = 'app/config/content'
    shards_to_process = [
        f for f in glob.glob(os.path.join(content_dir, '*.json'))
        if os.path.basename(f) not in ('search_index.json', 'categories.json', 'pillar_profiles.json', 'formulas.json', 'constants.json', 'entities.json')
    ]
    run_auto_linker(shards_to_process, os.path.join(content_dir, 'search_index.json'))
