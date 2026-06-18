import json
import re
import os
import glob
import sys

sys.path.append(os.getcwd())
from orchestrator import TrieRegexCompiler

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

    aliases_lower = {k.lower(): v for k, v in aliases.items()}

    import hashlib
    def get_cache_hash():
        hasher = hashlib.md5()
        reg = {}
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                reg = json.load(f)
        hasher.update(json.dumps(reg, sort_keys=True).encode('utf-8'))
        
        ent = {}
        entities_path = 'app/config/content/entities.json'
        if os.path.exists(entities_path):
            with open(entities_path, 'r') as f:
                ent = json.load(f)
        hasher.update(json.dumps(ent, sort_keys=True).encode('utf-8'))
        
        if os.path.exists(alias_path):
            with open(alias_path, 'rb') as f:
                hasher.update(f.read())
                
        if os.path.exists(index_path):
            with open(index_path, 'rb') as f:
                hasher.update(f.read())
                
        return hasher.hexdigest()

    cache_path = 'app/config/content/compiled_trie_regex.json'
    loaded_from_cache = False
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
            if cache_data.get('cache_hash') == get_cache_hash():
                compiled_strong = cache_data['bold_strong_pattern']
                strong_trie_pattern = re.compile(rf'<strong>({compiled_strong})</strong>', re.IGNORECASE)
                loaded_from_cache = True
                print("LOAD CACHE: Successfully loaded compiled bold patterns from disk cache in auto_linker.")
        except Exception as e:
            print(f"CACHE WARNING: Failed to load precompiled cache in auto_linker: {str(e)}")

    if not loaded_from_cache:
        trie_words = set(aliases.keys()) | valid_slugs
        trie_compiler = TrieRegexCompiler()
        compiled_trie = trie_compiler.compile(list(trie_words))
        strong_trie_pattern = re.compile(rf'<strong>({compiled_trie})</strong>', re.IGNORECASE)

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
            def replace_link(match):
                nonlocal modified_shard
                full_href = match.group(1)
                inner_content = match.group(2)
                clean_inner = inner_content.replace('<strong>', '').replace('</strong>', '')
                
                if full_href.startswith('/physics/subtopic/'):
                    target_slug = full_href.split('/')[-1]
                    if target_slug not in valid_slugs:
                        modified_shard = True
                        print(f"Downgraded invalid link to '{target_slug}' in {slug}")
                        return f'<strong>{clean_inner}</strong>'
                    
                    if target_slug in linked_in_node or target_slug == slug:
                        modified_shard = True
                        print(f"Downgraded redundant link to '{target_slug}' in {slug}")
                        return f'<strong>{clean_inner}</strong>'
                    else:
                        if '<strong>' not in inner_content:
                            inner_content = f'<strong>{inner_content}</strong>'
                        
                        repair_link = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link">{inner_content}</a>'
                        linked_in_node.add(target_slug)
                        modified_shard = True
                        print(f"Standardized link for '{target_slug}' in {slug}")
                        return repair_link
                else:
                    return match.group(0)

            content_pass1 = link_pattern.sub(replace_link, content)

            # PASS 2: Auto-link bolded terms using Trie-Regex
            def replace_strong(match):
                nonlocal modified_shard
                inner_text = match.group(1)
                
                # Case-insensitive alias matching
                target_slug = aliases_lower.get(inner_text.lower())
                if not target_slug: 
                    target_slug = normalize_slug(inner_text)
                
                if target_slug in valid_slugs and target_slug != slug and target_slug not in linked_in_node:
                    # Safeguard: Ensure it is not already inside a link tag
                    pos = match.start()
                    pre = content_pass1[:pos]
                    last_a_open = pre.rfind('<a')
                    last_a_close = pre.rfind('</a>')
                    if last_a_open > last_a_close:
                        return match.group(0)

                    link_tag = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{inner_text}</strong></a>'
                    linked_in_node.add(target_slug)
                    print(f"Linked '{inner_text}' -> '{target_slug}' in {slug}")
                    modified_shard = True
                    return link_tag
                else:
                    return match.group(0)

            final_content = strong_trie_pattern.sub(replace_strong, content_pass1)

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
        if os.path.basename(f) not in ('search_index.json', 'categories.json', 'pillar_profiles.json', 'formulas.json', 'constants.json', 'entities.json', 'compiled_trie_regex.json', 'notation.json', 'particles.json')
    ]
    run_auto_linker(shards_to_process, os.path.join(content_dir, 'search_index.json'))
