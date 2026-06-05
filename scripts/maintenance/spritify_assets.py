import os
import json
import re
import hashlib

def spritify_svg(svg_code, sprites):
    """
    Parses a single SVG string, extracts all <path d="..."> elements,
    registers unique path strings into the global sprites dictionary,
    and replaces them with <use href="#math-path-<hash>"/> references.
    """
    if not svg_code or not svg_code.startswith("<svg"):
        return svg_code, False

    # Regex to match paths: captures attributes (group 1) and d value (group 2)
    path_pattern = re.compile(r'<path([^>]*d="([^"]+)"[^>]*)>(?:</path>)?')
    
    matches = path_pattern.findall(svg_code)
    if not matches:
        return svg_code, False

    modified = False
    
    def replace_path(match):
        nonlocal modified
        attrs_str = match.group(1)
        d_val = match.group(2)
        
        # Generate a stable 10-char hash of the path definition
        h = hashlib.md5(d_val.strip().encode('utf-8')).hexdigest()[:10]
        pid = f"math-path-{h}"
        
        if d_val not in sprites:
            sprites[d_val] = pid
            
        modified = True
        
        # Strip the d="..." attribute from the reference attributes
        clean_attrs = re.sub(r'\s*d="[^"]+"', '', attrs_str)
        clean_attrs = clean_attrs.rstrip(' /')
        
        return f'<use href="#{pid}"{clean_attrs} />'

    new_svg = path_pattern.sub(replace_path, svg_code)
    return new_svg, modified

def process_json_recursive(obj, sprites):
    """
    Recursively traverses a JSON structure (dict, list) and spritifies any SVG string.
    Returns True if any modification was made.
    """
    modified = False
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if isinstance(v, str) and "<svg" in v:
                new_v, mod = spritify_svg(v, sprites)
                if mod:
                    obj[k] = new_v
                    modified = True
            elif isinstance(v, (dict, list)):
                if process_json_recursive(v, sprites):
                    modified = True
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str) and "<svg" in v:
                new_v, mod = spritify_svg(v, sprites)
                if mod:
                    obj[i] = new_v
                    modified = True
            elif isinstance(v, (dict, list)):
                if process_json_recursive(v, sprites):
                    modified = True
    return modified

def main():
    content_dir = "app/config/content"
    svg_cache_path = "global_svg_cache.json"
    sprites_path = os.path.join(content_dir, "math_sprites.svg")
    
    print("🚀 Initiating SVG Math Vector Sprite Sheet Optimization...")

    # Load existing sprites if any
    sprites = {}
    if os.path.exists(sprites_path):
        try:
            with open(sprites_path, "r") as f:
                content = f.read()
            paths = re.findall(r'<path\s+id="([^"]+)"\s+d="([^"]+)"\s*/?>', content)
            for pid, d in paths:
                sprites[d] = pid
            print(f"  [Sprites] Loaded {len(sprites)} existing glyph paths from {sprites_path}.")
        except Exception as e:
            print(f"  [Sprites] Failed to load existing sprite sheet: {e}")

    # 1. Process global_svg_cache.json
    cache_modified = False
    if os.path.exists(svg_cache_path):
        print(f"  [Cache] Reading persistent SVG cache: {svg_cache_path}...")
        try:
            with open(svg_cache_path, "r") as f:
                svg_cache = json.load(f)
            
            orig_size = os.path.getsize(svg_cache_path)
            print(f"  [Cache] Current persistent cache has {len(svg_cache)} entries. Size: {orig_size / (1024*1024):.2f} MB.")
            
            spritified_cache = {}
            for key, svg_code in svg_cache.items():
                new_svg, mod = spritify_svg(svg_code, sprites)
                spritified_cache[key] = new_svg
                if mod:
                    cache_modified = True
                    
            if cache_modified:
                with open(svg_cache_path, "w") as f:
                    json.dump(spritified_cache, f, indent=4)
                new_size = os.path.getsize(svg_cache_path)
                print(f"  [Cache] SAVED: Spritified cache written back to {svg_cache_path}.")
                print(f"  [Cache] Size reduced from {orig_size / (1024*1024):.2f} MB to {new_size / (1024*1024):.2f} MB ({(orig_size - new_size) / orig_size * 100:.1f}% reduction!).")
        except Exception as e:
            print(f"  [Cache] ERROR optimizing SVG cache: {e}")

    # 2. Write compiled sprite sheet
    if sprites:
        try:
            sprite_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">',
                '  <defs>'
            ]
            # Sort by ID for deterministic output
            for d_val, pid in sorted(sprites.items(), key=lambda x: x[1]):
                sprite_lines.append(f'    <path id="{pid}" d="{d_val}" />')
            sprite_lines.extend([
                '  </defs>',
                '</svg>'
            ])
            
            os.makedirs(os.path.dirname(sprites_path), exist_ok=True)
            with open(sprites_path, "w") as f:
                f.write("\n".join(sprite_lines))
            print(f"  [Sprites] WRITTEN: {len(sprites)} unique paths saved to {sprites_path}.")

            # Also save to public/ directory for static external reference & browser caching
            public_sprites_path = os.path.join("public", "math_sprites.svg")
            os.makedirs(os.path.dirname(public_sprites_path), exist_ok=True)
            with open(public_sprites_path, "w") as f:
                f.write("\n".join(sprite_lines))
            print(f"  [Sprites] WRITTEN: {len(sprites)} unique paths saved to {public_sprites_path}.")
        except Exception as e:
            print(f"  [Sprites] ERROR writing sprite sheet: {e}")

    # 3. Process database JSON shards
    print("  [Shards] Scanning and recursively spritifying sharded JSON files...")
    shard_count = 0
    
    for filename in os.listdir(content_dir):
        if not filename.endswith(".json") or filename == "categories.json" or filename == "search_index.json":
            continue
            
        filepath = os.path.join(content_dir, filename)
        try:
            with open(filepath, "r") as f:
                shard_data = json.load(f)
                
            orig_shard_size = os.path.getsize(filepath)
            
            # Recursively process the JSON structure
            shard_modified = process_json_recursive(shard_data, sprites)

            if shard_modified:
                with open(filepath, "w") as f:
                    json.dump(shard_data, f, indent=4)
                new_shard_size = os.path.getsize(filepath)
                pct = (orig_shard_size - new_shard_size) / orig_shard_size * 100
                print(f"    ✓ [Shard] Optimized {filename}: reduced from {orig_shard_size/1024:.1f} KB to {new_shard_size/1024:.1f} KB ({pct:.1f}% reduction).")
                shard_count += 1
        except Exception as e:
            print(f"    ✗ [Shard] ERROR processing {filename}: {e}")

    print(f"  [Shards] Completed: {shard_count} shards optimized.")

    # 4. Integrate sprite sheet into layout.php
    layout_path = "app/views/physics/layout.php"
    if os.path.exists(layout_path):
        print(f"  [Layout] Embedding math_sprites.svg hook into {layout_path}...")
        try:
            with open(layout_path, "r") as f:
                layout_content = f.read()
                
            # We want to embed the sprite sheet right after the <body> tag starts
            # Check if it is already embedded
            if "math_sprites.svg" not in layout_content:
                body_tag = "<body>"
                embed_code = r"""<body>
    <!-- Load math sprites asynchronously for static external reference & browser caching -->
    <script>
        (function() {
            fetch('/math_sprites.svg')
                .then(res => {
                    if (!res.ok) throw new Error('SVG load failed');
                    return res.text();
                })
                .then(svg => {
                    const div = document.createElement('div');
                    div.style.display = 'none';
                    div.innerHTML = svg.replace(/^<\?xml[^?]*\?>\s*/, '');
                    document.body.insertBefore(div, document.body.firstChild);
                })
                .catch(err => console.error('Math sprites fetch failed:', err));
        })();
    </script>"""
                if body_tag in layout_content:
                    layout_content = layout_content.replace(body_tag, embed_code)
                    with open(layout_path, "w") as f:
                        f.write(layout_content)
                    print("  [Layout] Successfully injected sprites async loading script after <body> tag!")
                else:
                    print("  [Layout] WARNING: Could not find <body> tag in layout.php to inject sprites!")
            else:
                print("  [Layout] Sprite sheet hook already present in layout.php.")
        except Exception as e:
            print(f"  [Layout] ERROR injecting into layout.php: {e}")

if __name__ == "__main__":
    main()
