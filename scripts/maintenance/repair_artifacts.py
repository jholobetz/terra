import json
import re
import os
import glob

def repair_artifacts(content_dir):
    shard_files = glob.glob(os.path.join(content_dir, '*.json'))
    
    # Regex to match **text** but be careful not to match across line breaks if they exist
    # though in these JSONs content is usually a single line per string.
    artifact_pattern = re.compile(r'\*\*(.*?)\*\*')

    for filepath in shard_files:
        if os.path.basename(filepath) in ('search_index.json', 'categories.json', 'pillar_profiles.json', 'formulas.json', 'constants.json', 'entities.json'):
            continue
            
        with open(filepath, 'r') as f:
            try:
                shard = json.load(f)
            except json.JSONDecodeError:
                print(f"Skipping {filepath}: invalid JSON")
                continue
        
        modified = False
        for slug, node in shard.items():
            for key, value in node.items():
                if isinstance(value, str) and '**' in value:
                    new_value = artifact_pattern.sub(r'<strong>\1</strong>', value)
                    if new_value != value:
                        node[key] = new_value
                        modified = True
                        print(f"Repaired artifacts in {slug}:{key}")
        
        if modified:
            with open(filepath, 'w') as f:
                json.dump(shard, f, indent=4)
            print(f"Updated {filepath}")

if __name__ == "__main__":
    repair_artifacts('app/config/content')
