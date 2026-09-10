import os
import json
import re

formulas_dir = "/Users/holobetj/code/gemini/terra/app/config/content/formulas"

t_suffixes = [
    "imes", "ext", "o\\b", "o\\s", "o[0-9\\-\\\(\\)\\{\\}]", "heta", "au", 
    "ilde", "r\\b", "ensor", "angent", "rifluoro", "race", "op\\b", 
    "an\\b", "anh\\b", "otal", "rans", "ension", "emperature", "ime"
]
t_pattern = re.compile("\t(" + "|".join(t_suffixes) + ")")

n_suffixes = [
    "abla", "u\\b", "u\\s", "u[0-9\\-\\\(\\)\\{\\}]", "umerator", "ormal", "ewton"
]
n_pattern = re.compile("\n(" + "|".join(n_suffixes) + ")")

def fix_string(val):
    if not isinstance(val, str):
        return val
    
    # 1. Standardize \r\n to \n
    val = val.replace("\r\n", "\n")
    
    # 2. Fix backspaces (\x08 -> \b)
    val = val.replace("\x08", "\\b")
    
    # 3. Fix formfeeds (\x0c -> \f)
    val = val.replace("\x0c", "\\f")
    
    # 4. Fix carriage returns (\r -> \r)
    val = val.replace("\r", "\\r")
    
    # 5. Fix tabs (\t -> \t when followed by latex t-suffixes)
    val = t_pattern.sub(r'\\t\1', val)
    
    # 6. Fix newlines (\n -> \n when followed by latex n-suffixes)
    val = n_pattern.sub(r'\\n\1', val)
    
    return val

total_fixed_formulas = 0
total_fixed_fields = 0

for filename in sorted(os.listdir(formulas_dir)):
    if not filename.startswith("shard_") or not filename.endswith(".json"):
        continue
    filepath = os.path.join(formulas_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    shard_modified = False
    for fid, details in data.items():
        formula_modified = False
        for field in ["interpretation", "symmetry_origin", "limits_and_boundary", "conceptual_definition", "intuitive_summary"]:
            if field in details:
                old_val = details[field]
                new_val = fix_string(old_val)
                if old_val != new_val:
                    details[field] = new_val
                    formula_modified = True
                    total_fixed_fields += 1
        if formula_modified:
            total_fixed_formulas += 1
            shard_modified = True
            
    if shard_modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

print(f"Completed fixing shards:")
print(f"  Fixed formulas: {total_fixed_formulas}")
print(f"  Fixed fields: {total_fixed_fields}")
