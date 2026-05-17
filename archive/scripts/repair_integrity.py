import json
import os
import re

def repair_json_file(file_path):
    with open(file_path, 'r') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False

    modified = False

    # Check if it's a shard (keys are slugs) or a registry (keys are IDs)
    for key, subtopic in data.items():
        if not isinstance(subtopic, dict):
            continue
            
        # 1. Fix Complexity
        if "visual_config" in subtopic and "complexity" in subtopic["visual_config"]:
            if subtopic["visual_config"]["complexity"] > 10:
                subtopic["visual_config"]["complexity"] = 10
                modified = True
        
        # 2. Fix formula_ids references
        if "formula_ids" in subtopic:
            new_ids = []
            for fid in subtopic["formula_ids"]:
                # Pattern: a-href-physics-subtopic-SLUG-class-subtopic-link-LINKTEXT-a-HASH
                if fid.startswith("a-href-"):
                    # Use regex to extract SLUG and HASH
                    # Example: a-href-physics-subtopic-energy-momentum-relation-class-subtopic-link-energy-momentum-relation-a-07bc2f9f
                    # We want: energy-momentum-relation-07bc2f9f
                    match = re.search(r"a-href-physics-subtopic-(.*?)-class-subtopic-link-.*?-a-([a-f0-9]+)$", fid)
                    if match:
                        new_fid = f"{match.group(1)}-{match.group(2)}"
                        new_ids.append(new_fid)
                        modified = True
                    else:
                        new_ids.append(fid)
                else:
                    new_ids.append(fid)
            subtopic["formula_ids"] = new_ids

        # 3. Fix lhc-cern in content
        if "content" in subtopic:
            if "/physics/subtopic/lhc-cern" in subtopic["content"]:
                subtopic["content"] = subtopic["content"].replace("/physics/subtopic/lhc-cern", "/physics/subtopic/lhc-searches")
                modified = True

    # 4. Special handling for formulas.json keys
    if os.path.basename(file_path) == "formulas.json":
        new_data = {}
        for key, val in data.items():
            if key.startswith("a-href-"):
                match = re.search(r"a-href-physics-subtopic-(.*?)-class-subtopic-link-.*?-a-([a-f0-9]+)$", key)
                if match:
                    new_key = f"{match.group(1)}-{match.group(2)}"
                    new_data[new_key] = val
                    modified = True
                else:
                    new_data[key] = val
            else:
                new_data[key] = val
        data = new_data

    if modified:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Repaired {file_path}")
    return modified

content_dir = "app/config/content"
for filename in os.listdir(content_dir):
    if filename.endswith(".json"):
        repair_json_file(os.path.join(content_dir, filename))
