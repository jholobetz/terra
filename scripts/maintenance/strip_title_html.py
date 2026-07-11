import os
import json
import re

formulas_dir = "/Users/holobetj/code/gemini/terra/app/config/content/formulas"
total_stripped = 0

tag_pattern = re.compile(r'</?[a-zA-Z][^>]*>')

for filename in sorted(os.listdir(formulas_dir)):
    if not filename.startswith("shard_") or not filename.endswith(".json"):
        continue
    filepath = os.path.join(formulas_dir, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    shard_modified = False
    for fid, details in data.items():
        title = details.get("title", "")
        if tag_pattern.search(title):
            new_title = tag_pattern.sub("", title)
            details["title"] = new_title
            shard_modified = True
            total_stripped += 1
            print(f"  [{fid}]: {repr(title)} -> {repr(new_title)}")
            
    if shard_modified:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

print(f"Successfully stripped HTML from {total_stripped} formula titles.")
