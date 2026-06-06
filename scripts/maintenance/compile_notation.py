#!/usr/bin/env python3
"""
🪐 Physics Lab - Compile Notation Registry
Aggregates all semantic variables from formula shards and compiles them into app/config/content/notation.json.
"""
import os
import json

def normalize_slug(slug):
    s = slug.lower().replace("_", "-")
    mapping = {
        "hbar": "h-bar",
        "h-bar": "h-bar",
        "kb": "k-B",
        "k-b": "k-B",
        "epsilon-0": "epsilon-0",
        "epsilon_0": "epsilon-0",
        "mu-0": "mu-0",
        "mu_0": "mu-0",
        "sigma-sb": "sigma-sb",
        "sigma_sb": "sigma-sb",
        "g-f": "constants/G_F", # placeholder for GF lookup mappings
    }
    return mapping.get(s, s)

def compile_notation(content_dir="app/config/content"):
    notation_path = os.path.join(content_dir, "notation.json")
    
    # Load legacy constants for values and units
    constants_path = os.path.join(content_dir, "constants.json")
    legacy_constants = {}
    if os.path.exists(constants_path):
        with open(constants_path, "r") as f:
            try:
                legacy_constants = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load constants.json: {e}")
                
    # Load existing notation registry
    if os.path.exists(notation_path):
        with open(notation_path, "r") as f:
            try:
                notation = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load existing notation.json ({e}). Starting fresh.")
                notation = {}
    else:
        notation = {}
        
    initial_count = len(notation)
    new_added = 0
    updated_count = 0
    
    # Traverse sharded formulas
    formulas_dir = os.path.join(content_dir, "formulas")
    if os.path.exists(formulas_dir):
        for file_name in os.listdir(formulas_dir):
            if file_name.startswith("shard_") and file_name.endswith(".json"):
                shard_path = os.path.join(formulas_dir, file_name)
                try:
                    with open(shard_path, "r") as f:
                        shard_data = json.load(f)
                except Exception as e:
                    print(f"Error reading shard {shard_path}: {e}")
                    continue
                
                for formula_id, formula in shard_data.items():
                    sem_vars = formula.get("semantic_variables", {})
                    if not isinstance(sem_vars, dict):
                        continue
                        
                    for symbol, var_info in sem_vars.items():
                        if not isinstance(var_info, dict):
                            continue
                            
                        ref = var_info.get("ref", "")
                        if not ref or "/" not in ref:
                            continue
                            
                        # Extract the slug (e.g. "constants/c" -> "c", "notation/electric-field" -> "electric-field")
                        ref_parts = ref.split("/", 1)
                        ref_category = ref_parts[0]
                        slug = ref_parts[1]
                        
                        # Determine default type from reference category or var_info
                        default_type = var_info.get("type", "variable")
                        if ref_category == "constants":
                            default_type = "constant"
                        elif ref_category == "subtopics" and default_type == "constant":
                            # Default variables in subtopics are variables unless specified
                            default_type = "variable"
                        
                        var_name = var_info.get("name", slug.replace("-", " ").title())
                        
                        # Add or update in the notation registry
                        if slug not in notation:
                            # Build a clean description including its first-referenced location
                            formula_title = formula.get('title', 'Unknown Formula')
                            origin = formula.get("origin_subtopic", "")
                            
                            legacy_key = normalize_slug(slug)
                            legacy_info = legacy_constants.get(legacy_key, {})
                            
                            notation[slug] = {
                                "symbol": symbol,
                                "name": var_name,
                                "type": default_type,
                                "description": f"Aggregated reference variable from formula identities. First referenced in: {formula_title}.",
                                "origin_subtopic": origin if origin else slug
                            }
                            
                            if default_type == "constant":
                                if "value" in legacy_info:
                                    notation[slug]["value"] = legacy_info["value"]
                                if "unit" in legacy_info:
                                    notation[slug]["unit"] = legacy_info["unit"]
                                if "description" in legacy_info:
                                    notation[slug]["description"] = legacy_info["description"]
                                    
                            new_added += 1
                        else:
                            # Update existing entries if they are missing fields
                            entry = notation[slug]
                            changed = False
                            if "type" not in entry or not entry["type"]:
                                entry["type"] = default_type
                                changed = True
                            if "name" not in entry or not entry["name"]:
                                entry["name"] = var_name
                                changed = True
                            if "symbol" not in entry or not entry["symbol"]:
                                entry["symbol"] = symbol
                                changed = True
                                
                            # If it is a constant, retroactively populate missing value/unit/description
                            if entry.get("type") == "constant":
                                legacy_key = normalize_slug(slug)
                                legacy_info = legacy_constants.get(legacy_key, {})
                                if "value" not in entry and "value" in legacy_info:
                                    entry["value"] = legacy_info["value"]
                                    changed = True
                                if "unit" not in entry and "unit" in legacy_info:
                                    entry["unit"] = legacy_info["unit"]
                                    changed = True
                                    
                            if changed:
                                updated_count += 1
                                
    # Write back to notation.json
    with open(notation_path, "w") as f:
        json.dump(notation, f, indent=4)
        
    print(f"✓ Static Notation Registry Synced.")
    print(f"  - Initial entries: {initial_count}")
    print(f"  - New entries compiled: {new_added}")
    print(f"  - Updated entries: {updated_count}")
    print(f"  - Final entries: {len(notation)}")

if __name__ == "__main__":
    # Running from project root
    compile_notation()
