import os
import sys
import json
import re
import html

# Add root directory to path so we can import orchestrator
sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

def normalize_latex(latex):
    if not latex:
        return ""
    # Strip delimiters
    latex = re.sub(r'^\\\(|\\\)$|^\$\$|\$\$$', '', latex)
    # Strip all whitespaces
    latex = re.sub(r'\s+', '', latex)
    return latex

def main():
    content_dir = "app/config/content"
    orch = PhysicsOrchestrator(content_dir=content_dir)
    
    print("Building formula-to-subtopics mapping...")
    formula_to_subtopics = {}
    for shard_name, shard_content in orch.shards.items():
        if shard_name == "compiled_trie_regex.json":
            continue
        for slug, subtopic in shard_content.items():
            f_ids = subtopic.get("formula_ids", [])
            for f_id in f_ids:
                formula_to_subtopics.setdefault(f_id, []).append({
                    "slug": slug,
                    "title": subtopic.get("title", ""),
                    "shard": shard_name
                })
                
    # 1. Group formulas by normalized LaTeX equations
    print("Grouping formulas by equation...")
    latex_groups = {}
    for f_id, formula in orch.data["formula_registry"].items():
        eq = formula.get("equation", "")
        latex = eq
        if eq.startswith("<svg"):
            match = re.search(r'data-tex="([^"]+)"', eq)
            if match:
                latex = html.unescape(match.group(1))
                
        norm_latex = normalize_latex(latex)
        if norm_latex and norm_latex != "REG":
            latex_groups.setdefault(norm_latex, []).append(f_id)
            
    # 2. Process duplicate groups
    aliases = {}
    merge_count = 0
    deleted_count = 0
    
    for norm_latex, f_ids in latex_groups.items():
        if len(f_ids) <= 1:
            continue
            
        # Select Primary ID
        # Metric: count non-empty metadata fields
        best_id = None
        best_score = -1
        
        for f_id in f_ids:
            formula = orch.data["formula_registry"][f_id]
            score = 0
            for field in ["symmetry_origin", "interpretation", "limits_and_boundary", "semantic_variables", "unit_system"]:
                val = formula.get(field)
                if val:
                    if isinstance(val, dict) and len(val) > 0:
                        score += 1
                    elif isinstance(val, str) and len(val.strip()) > 0:
                        score += 1
            # Tie breaker: prefer formula referenced by most subtopics, or shorter ID
            ref_count = len(formula_to_subtopics.get(f_id, []))
            score = (score * 1000) + (ref_count * 10) - len(f_id)
            
            if score > best_score:
                best_score = score
                best_id = f_id
                
        print(f"Duplicate Equation group for LaTeX: {norm_latex[:50]}...")
        print(f"  -> Selected Primary ID: {best_id}")
        
        primary_formula = orch.data["formula_registry"][best_id]
        
        # Merge metadata into primary
        for f_id in f_ids:
            if f_id == best_id:
                continue
                
            redundant_formula = orch.data["formula_registry"][f_id]
            for field in ["symmetry_origin", "interpretation", "limits_and_boundary", "unit_system"]:
                if not primary_formula.get(field) and redundant_formula.get(field):
                    primary_formula[field] = redundant_formula[field]
                    
            # Merge semantic variables
            primary_vars = primary_formula.setdefault("semantic_variables", {})
            redundant_vars = redundant_formula.get("semantic_variables", {})
            if isinstance(primary_vars, dict) and isinstance(redundant_vars, dict):
                for var_name, var_info in redundant_vars.items():
                    if var_name not in primary_vars:
                        primary_vars[var_name] = var_info
                        
            aliases[f_id] = best_id
            merge_count += 1
            
            # Update referencing subtopics to use the Primary ID
            referencing = formula_to_subtopics.get(f_id, [])
            for ref in referencing:
                slug = ref["slug"]
                shard = ref["shard"]
                subtopic = orch.shards[shard][slug]
                
                # Replace ID in list and deduplicate
                old_list = subtopic.get("formula_ids", [])
                new_list = []
                for i in old_list:
                    if i == f_id:
                        if best_id not in new_list:
                            new_list.append(best_id)
                    else:
                        if i not in new_list:
                            new_list.append(i)
                subtopic["formula_ids"] = new_list
                
                # Mark as modified in orchestrator
                orch.modified_slugs.add(slug)
                
            # Delete redundant formula from registry
            del orch.data["formula_registry"][f_id]
            deleted_count += 1
            
    print(f"Merged {merge_count} redundant formulas. Deleted {deleted_count} records from memory registry.")
    
    # 3. Contextualize distinct equations with duplicate titles (Scenario B)
    print("Contextualizing formulas with duplicate titles...")
    title_groups = {}
    for f_id, formula in orch.data["formula_registry"].items():
        title_groups.setdefault(formula.get("title", ""), []).append(f_id)
        
    rename_count = 0
    for title, f_ids in title_groups.items():
        if len(f_ids) <= 1:
            continue
            
        # These share the same title but represent distinct equations
        print(f"Duplicate Title group for '{title}': {len(f_ids)} formulas found.")
        for f_id in f_ids:
            formula = orch.data["formula_registry"][f_id]
            referencing = formula_to_subtopics.get(f_id, [])
            if referencing:
                sub_title = referencing[0]["title"]
                # Clean up subtopic title (remove HTML tags if any)
                sub_title = re.sub(r'<[^>]*>', '', sub_title)
                new_title = f"{title} ({sub_title})"
                formula["title"] = new_title
                print(f"  -> Renamed {f_id} title to: {new_title}")
                rename_count += 1
            else:
                # If no subtopic is referencing, check topic parents or just append ID slug info
                slug_info = f_id.split("-")
                context = slug_info[0].capitalize()
                new_title = f"{title} ({context})"
                formula["title"] = new_title
                print(f"  -> Renamed {f_id} title (no subtopic) to: {new_title}")
                rename_count += 1
                
    print(f"Renamed {rename_count} duplicate titles with context.")
    
    # 4. Save aliases registry
    alias_filepath = os.path.join(content_dir, "formula_aliases.json")
    print(f"Writing aliases map to {alias_filepath}...")
    with open(alias_filepath, "w") as f:
        json.dump(aliases, f, indent=4)
        
    # 5. Save changes using orchestrator
    print("Saving modified formula registry, subtopic shards, search index, and manifest to disk...")
    orch.save(auto_commit=False, force_full=True)
    print("Database deduplication successfully completed and saved.")

if __name__ == "__main__":
    main()
