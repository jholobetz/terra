import os
import json
import re

content_dir = 'app/config/content'
# Regex to find the specific corruption: href="...<a href=..."
# Note: In JSON shards, quotes are escaped as \"
corruption_pattern = re.compile(r'href=\\?"/physics/(?:subtopic|topic)/<a href=\\?"/physics/(?:subtopic|topic)/([^\\"]+)\\?"[^>]*>(.*?)</a>([^\\"]*)\\?"', re.DOTALL)

def fix_content(content):
    # Fix the specific nested-link-in-href corruption
    # We want to replace it with a single clean link to the larger term if possible, 
    # but the simplest fix is to just extract the text and let auto-linker handle it.
    
    # Example: <a href="/physics/subtopic/<a href="...">Einstein</a>-field-equations">
    # Result: <a href="/physics/subtopic/einstein-field-equations">Einstein-field-equations</a> (or similar)
    
    # Let's just strip the corrupted outer tag and inner tag, leaving the text.
    # The hardened auto-linker will fix it on the next save.
    
    last_content = None
    while content != last_content:
        last_content = content
        # Pattern 1: Nested anchor in href (the one we saw)
        content = corruption_pattern.sub(r'href="/physics/subtopic/\1\3"', content)
        
        # Pattern 2: General nested anchor <a>...<a>...</a>...</a>
        content = re.sub(r'(<a\s+[^>]*>)(.*?)(<a\s+[^>]*>)(.*?)(</a>)(.*?)(</a>)', r'\1\2\4\6\7', content, flags=re.DOTALL)

    return content

for filename in os.listdir(content_dir):
    if not filename.endswith('.json') or filename in ['formulas.json', 'constants.json', 'entities.json', 'search_index.json']:
        continue
        
    path = os.path.join(content_dir, filename)
    with open(path, 'r') as f:
        try:
            data = json.load(f)
        except:
            continue
            
    modified = False
    for slug in data:
        if 'content' in data[slug]:
            original = data[slug]['content']
            fixed = fix_content(original)
            if fixed != original:
                print(f"FIXED corruption in {filename} -> {slug}")
                data[slug]['content'] = fixed
                modified = True
                
    if modified:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

print("Shard Deep Clean Complete.")
