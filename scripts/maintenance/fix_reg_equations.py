import os
import sys
import json
import re
import html
from xml.etree import ElementTree

# Add root directory to path so we can import orchestrator
sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

def resolve_svg_use_tags(svg_str):
    svg_str = svg_str.replace('xlink:href', 'href')
    svg_str = svg_str.replace('xmlns:xlink', 'xmlns_xlink')
    svg_str = re.sub(r'\s+xmlns:[^\s=]+="[^"]*"', '', svg_str)
    
    try:
        root = ElementTree.fromstring(svg_str)
    except Exception:
        return svg_str

    defs_node = None
    for elem in root.iter():
        if elem.tag.endswith('defs'):
            defs_node = elem
            break

    defs_paths = {}
    if defs_node is not None:
        for path in defs_node.iter():
            if path.tag.endswith('path'):
                path_id = path.get('id')
                if path_id:
                    defs_paths[path_id] = dict(path.attrib)
                    defs_paths[path_id].pop('id', None)
        
        for parent in root.iter():
            if defs_node in parent:
                parent.remove(defs_node)
                break

    def resolve_node(node):
        to_replace = []
        for i, child in enumerate(node):
            if child.tag.endswith('use'):
                href = child.get('href')
                if href and href.startswith('#'):
                    path_id = href[1:]
                    if path_id in defs_paths:
                        new_node = ElementTree.Element(child.tag.split('}')[-1])
                        new_node.tag = child.tag.replace('use', 'path')
                        new_node.attrib = dict(defs_paths[path_id])
                        to_replace.append((i, new_node))
            else:
                resolve_node(child)
                
        for i, new_node in to_replace:
            node[i] = new_node

    resolve_node(root)
    
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[-1]
            
    res_str = ElementTree.tostring(root, encoding='utf-8').decode('utf-8')
    return res_str

def clean_svg_structure(svg):
    svg = resolve_svg_use_tags(svg)
    svg = re.sub(r'color:\s*#[0-9a-fA-F]+;', '', svg)
    svg = re.sub(r'fill="#[0-9a-fA-F]+"', 'fill="currentColor"', svg)
    svg = re.sub(r'stroke="#[0-9a-fA-F]+"', 'stroke="currentColor"', svg)
    svg = re.sub(r'fill="red"', 'fill="currentColor"', svg)
    svg = re.sub(r'stroke="red"', 'stroke="currentColor"', svg)
    svg = re.sub(r'#math-path-[0-9a-fA-F]+', '#math-path-placeholder', svg)
    svg = re.sub(r'MJX-[0-9a-zA-Z\-_]+', 'MJX-placeholder', svg)
    svg = re.sub(r'id="[^"]*"', '', svg)
    svg = re.sub(r'\s+data-c="[^"]*"', '', svg)
    svg = re.sub(r'\s+width="[^"]*"', '', svg)
    svg = re.sub(r'\s+height="[^"]*"', '', svg)
    svg = re.sub(r'\s+style="[^"]*"', '', svg)
    svg = re.sub(r'\s+viewBox="[^"]*"', '', svg)
    svg = re.sub(r'\s+transform="[^"]*"', '', svg)
    svg = re.sub(r'^<svg.*?>', '<svg>', svg)
    svg = re.sub(r'\s+', ' ', svg).strip()
    return svg

def main():
    content_dir = "app/config/content"
    orch = PhysicsOrchestrator(content_dir=content_dir)
    
    print("Loading SVG Cache...")
    if not os.path.exists("global_svg_cache.json"):
        print("Error: global_svg_cache.json not found in root.")
        sys.exit(1)
        
    with open("global_svg_cache.json", "r") as f:
        svg_cache = json.load(f)
        
    print("Building reverse mapping from SVG cache...")
    norm_svg_to_latex = {}
    for k, v in svg_cache.items():
        parts = k.rsplit('_', 2)
        if len(parts) == 3:
            latex = parts[0]
            norm_v = clean_svg_structure(v)
            norm_svg_to_latex[norm_v] = latex
            
    print(f"Lookup map populated with {len(norm_svg_to_latex)} entries.")
    
    total_found = 0
    total_fixed = 0
    total_unmatched = 0
    
    print("Scanning formula registry shards for REG placeholder SVGs...")
    for f_id, formula in orch.data["formula_registry"].items():
        eq = formula.get("equation", "")
        if 'data-tex="REG"' in eq or eq == 'REG':
            total_found += 1
            norm_eq = clean_svg_structure(eq)
            latex = norm_svg_to_latex.get(norm_eq)
            
            if latex:
                escaped_latex = html.escape(latex)
                formula["equation"] = eq.replace('data-tex="REG"', f'data-tex="{escaped_latex}"', 1)
                total_fixed += 1
            else:
                print(f"WARNING: Unmatched REG formula ID: {f_id} | Title: {formula.get('title')}")
                total_unmatched += 1
                
    print(f"Scan complete. Found {total_found} REG placeholder formulas.")
    print(f"Successfully matched and fixed {total_fixed}/{total_found} formulas.")
    if total_unmatched > 0:
        print(f"Failed to match {total_unmatched} formulas. Check warnings above.")
        
    if total_fixed > 0:
        print("Saving modified formula registry shards and manifest to disk...")
        orch.save(auto_commit=False, force_full=True)
        print("Formula shards updated successfully.")
    else:
        print("No changes to write.")

if __name__ == "__main__":
    main()
