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
    """
    Parses an SVG string, finds <defs> and resolves all <use> tags to inline <path> tags,
    removing the <defs> block. This normalizes the structural difference between MathJax
    fontCache: 'local' and 'none'.
    """
    # Standardize namespaces so ElementTree doesn't choke on colons
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
    
    # Strip namespaces completely from all tags to make them clean
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}')[-1]
            
    res_str = ElementTree.tostring(root, encoding='utf-8').decode('utf-8')
    return res_str

def clean_svg_structure(svg):
    """Normalize SVG structures by removing dynamic IDs, style attributes, and colors for robust matching."""
    svg = resolve_svg_use_tags(svg)
    # Remove outer style/color attributes
    svg = re.sub(r'color:\s*#[0-9a-fA-F]+;', '', svg)
    svg = re.sub(r'fill=\"#[0-9a-fA-F]+\"', 'fill=\"currentColor\"', svg)
    svg = re.sub(r'stroke=\"#[0-9a-fA-F]+\"', 'stroke=\"currentColor\"', svg)
    svg = re.sub(r'fill=\"red\"', 'fill=\"currentColor\"', svg)
    svg = re.sub(r'stroke=\"red\"', 'stroke=\"currentColor\"', svg)
    # Normalize MathJax dynamic element IDs
    svg = re.sub(r'#math-path-[0-9a-fA-F]+', '#math-path-placeholder', svg)
    svg = re.sub(r'MJX-[0-9a-zA-Z\-_]+', 'MJX-placeholder', svg)
    svg = re.sub(r'id=\"[^\"]*\"', '', svg)
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
    
    # 1. Build Exact and Normalized Reverse Lookup Tables from the SVG Cache
    print("Building reverse mapping from SVG cache...")
    exact_svg_to_latex = {}
    norm_svg_to_latex = {}
    
    for k, v in orch.svg_cache.items():
        parts = k.rsplit('_', 2)
        if len(parts) == 3:
            latex = parts[0]
            exact_svg_to_latex[v] = latex
            norm_v = clean_svg_structure(v)
            norm_svg_to_latex[norm_v] = latex

    print(f"Loaded {len(exact_svg_to_latex)} exact mappings and {len(norm_svg_to_latex)} normalized mappings.")

    svg_pattern = re.compile(r'<svg.*?</svg>', re.DOTALL)
    
    total_svgs_found = 0
    total_svgs_updated = 0
    total_unmatched = 0

    # 2. Inject data-tex into all Subtopic Content Shards
    print("Scanning subtopic content shards for SVGs...")
    for shard_name, shard_content in orch.shards.items():
        shard_updated = False
        for slug, subtopic in shard_content.items():
            subtopic_updated = False
            for key in ["content", "snippet_svg", "hero_math"]:
                if key not in subtopic or not subtopic[key]:
                    continue
                
                val = subtopic[key]
                svg_matches = svg_pattern.findall(val)
                if not svg_matches:
                    continue
                    
                updated_val = val
                val_updated = False
                
                for svg in svg_matches:
                    total_svgs_found += 1
                    if 'data-tex="' in svg:
                        # Already updated in a previous run
                        continue
                        
                    latex = exact_svg_to_latex.get(svg)
                    if not latex:
                        norm_svg = clean_svg_structure(svg)
                        latex = norm_svg_to_latex.get(norm_svg)
                    
                    if latex:
                        escaped_latex = html.escape(latex)
                        updated_svg = svg.replace("<svg ", f'<svg data-tex="{escaped_latex}" ', 1)
                        updated_val = updated_val.replace(svg, updated_svg)
                        total_svgs_updated += 1
                        val_updated = True
                    else:
                        total_unmatched += 1
                
                if val_updated:
                    subtopic[key] = updated_val
                    subtopic_updated = True
            
            if subtopic_updated:
                # Update orchestrator main data structure
                orch.data["subtopics"][slug] = subtopic
                orch.modified_slugs.add(slug)
                shard_updated = True

    # 3. Inject data-tex into all Formula Shards
    print("Scanning formula registry shards for SVGs...")
    for f_id, formula in orch.data["formula_registry"].items():
        eq = formula.get("equation", "")
        if eq.startswith("<svg") and 'data-tex="' not in eq:
            total_svgs_found += 1
            latex = exact_svg_to_latex.get(eq)
            if not latex:
                norm_eq = clean_svg_structure(eq)
                latex = norm_svg_to_latex.get(norm_eq)
                
            if latex:
                escaped_latex = html.escape(latex)
                formula["equation"] = eq.replace("<svg ", f'<svg data-tex="{escaped_latex}" ', 1)
                # Ensure the registry shard gets marked as modified
                # We can do this by using a placeholder subtopic update or by triggering orchestrator save
                total_svgs_updated += 1
            else:
                total_unmatched += 1

    print(f"Scan complete. Found {total_svgs_found} SVGs.")
    print(f"Updated {total_svgs_updated} SVGs with data-tex attributes.")
    print(f"Failed to match {total_unmatched} SVGs in cache.")

    # 4. Save changes back to disk
    # Always save the formula registry in case it changed
    print("Saving modified shards, registries, search index, and manifest to disk...")
    # Save via orchestrator to rebuild search indexes, manifests, and signatures correctly
    # Set force_full=True to ensure formula registry is saved
    orch.save(auto_commit=False, force_full=True)
    print("Database successfully synchronized and saved.")

if __name__ == "__main__":
    main()
