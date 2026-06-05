import os
import re
import json

def load_sprites(sprites_path):
    sprites = {}
    if os.path.exists(sprites_path):
        with open(sprites_path, "r") as f:
            content = f.read()
        paths = re.findall(r'<path\s+id="([^"]+)"\s+d="([^"]+)"\s*/?>', content)
        for pid, d in paths:
            sprites[pid] = d
        print(f"Loaded {len(sprites)} path definitions from {sprites_path}.")
    return sprites

def despritify_svg(svg_code, id_to_d):
    if not svg_code or "<svg" not in svg_code:
        return svg_code, False
        
    use_pattern = re.compile(r'<use([^>]*)>(?:</use>)?', re.IGNORECASE)
    modified = False
    
    def replace_use(match):
        nonlocal modified
        attrs_str = match.group(1)
        href_match = re.search(r'(?:href|xlink:href)="#(math-path-[a-f0-9]+)"', attrs_str)
        if not href_match:
            return match.group(0)
        
        pid = href_match.group(1)
        if pid not in id_to_d:
            return match.group(0)
            
        d_val = id_to_d[pid]
        clean_attrs = re.sub(r'\s*(?:href|xlink:href)="#[^"]+"', '', attrs_str)
        clean_attrs = clean_attrs.rstrip(' /')
        
        modified = True
        return f'<path{clean_attrs} d="{d_val}"></path>'
        
    new_svg = use_pattern.sub(replace_use, svg_code)
    return new_svg, modified

def process_json_recursive(obj, sprites):
    modified = False
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and "<svg" in v:
                new_v, mod = despritify_svg(v, sprites)
                if mod:
                    obj[k] = new_v
                    modified = True
            elif isinstance(v, (dict, list)):
                if process_json_recursive(v, sprites):
                    modified = True
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and "<svg" in v:
                new_v, mod = despritify_svg(v, sprites)
                if mod:
                    obj[i] = new_v
                    modified = True
            elif isinstance(v, (dict, list)):
                if process_json_recursive(v, sprites):
                    modified = True
    return modified

def main():
    sprites_path = "public/math_sprites.svg"
    if not os.path.exists(sprites_path):
        sprites_path = "app/config/content/math_sprites.svg"
        
    if not os.path.exists(sprites_path):
        print("Error: No sprite sheet found to restore paths.")
        return
        
    sprites = load_sprites(sprites_path)
    content_dir = "app/config/content"
    
    # Process all JSON files in the content directory recursively
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".json") and file != "global_svg_cache.json":
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    
                    if process_json_recursive(data, sprites):
                        with open(filepath, "w") as f:
                            json.dump(data, f, indent=4)
                        print(f"De-spritified and updated: {filepath}")
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    main()
