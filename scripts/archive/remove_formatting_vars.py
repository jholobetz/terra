import os
import json
import re

formulas_dir = "/Users/holobetj/code/gemini/terra/app/config/content/formulas"

pure_formatting_cmds = {
    "left", "right", "xrightarrow", "xleftarrow", "overleftarrow", "overrightarrow", 
    "overleftrightarrow", "underleftarrow", "underrightarrow", "underleftrightarrow", 
    "overline", "underline", "overbrace", "underbrace", "widehat", "widetilde", 
    "begin", "end", "mathbb", "mathcal", "mathbf", "mathsf", "mathrm", "text", "boldsymbol"
}

def is_pure_formatting(key):
    # Remove delimiters
    clean = key.strip()
    clean = clean.replace(r"\(", "").replace(r"\)", "").replace(r"\[", "").replace(r"\]", "")
    clean = clean.replace("$", "").replace("{", "").replace("}", "").strip()
    
    # Remove leading backslash if present
    if clean.startswith("\\"):
        clean_word = clean[1:]
    else:
        clean_word = clean
        
    if clean_word in pure_formatting_cmds:
        return True
        
    # Also handle things like \left[ or \right) or \left|
    for cmd in ["left", "right", "begin", "end"]:
        if clean_word.startswith(cmd):
            rest = clean_word[len(cmd):].strip()
            # If the rest contains only non-alphanumeric chars
            if not rest or not re.search(r'[a-zA-Z0-9]', rest):
                return True
                
    return False

total_removed = 0
shards_modified = 0

for filename in sorted(os.listdir(formulas_dir)):
    if not filename.startswith("shard_") or not filename.endswith(".json"):
        continue
    filepath = os.path.join(formulas_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    shard_modified = False
    for fid, details in data.items():
        sem_vars = details.get("semantic_variables", {})
        if not isinstance(sem_vars, dict):
            continue
            
        keys_to_remove = [k for k in sem_vars.keys() if is_pure_formatting(k)]
        if keys_to_remove:
            for k in keys_to_remove:
                del sem_vars[k]
                total_removed += 1
            shard_modified = True
            
    if shard_modified:
        shards_modified += 1
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

print(f"Completed formatting keys cleanup:")
print(f"  Removed {total_removed} formatting keys from {shards_modified} shards.")
