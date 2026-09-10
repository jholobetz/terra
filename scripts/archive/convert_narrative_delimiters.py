import os
import json
import glob
import tempfile

def convert_string(s):
    if not isinstance(s, str):
        return s
    # Convert display math delimiters to inline math delimiters
    s = s.replace('\\[', '\\(')
    s = s.replace('\\]', '\\)')
    return s

def clean_formula_narratives(data):
    if not isinstance(data, dict):
        return data
        
    for f_id, f_data in data.items():
        if not isinstance(f_data, dict):
            continue
        
        # Target narrative fields for delimiter conversion
        fields_to_convert = [
            'conceptual_definition',
            'intuitive_summary',
            'interpretation',
            'symmetry_origin',
            'limits_and_boundary'
        ]
        
        for field in fields_to_convert:
            if field in f_data and isinstance(f_data[field], str):
                f_data[field] = convert_string(f_data[field])
                
        # Also clean semantic variables description fields if they contain delimiters
        if 'semantic_variables' in f_data and isinstance(f_data['semantic_variables'], dict):
            for var_sym, var_info in f_data['semantic_variables'].items():
                if isinstance(var_info, dict):
                    if 'description' in var_info and isinstance(var_info['description'], str):
                        var_info['description'] = convert_string(var_info['description'])
                    if 'desc' in var_info and isinstance(var_info['desc'], str):
                        var_info['desc'] = convert_string(var_info['desc'])
                        
    return data

def main():
    shards_dir = "/Users/holobetj/code/gemini/terra/app/config/content/formulas"
    shard_files = glob.glob(os.path.join(shards_dir, "shard_*.json"))
    shard_files.sort()
    
    print(f"Found {len(shard_files)} shards to process.")
    updated_count = 0
    
    for filepath in shard_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error reading {os.path.basename(filepath)}: {e}")
                continue
                
        # Modify the narratives in-place
        modified_data = clean_formula_narratives(data)
        
        # Serialize to JSON and write back
        json_str = json.dumps(modified_data, indent=4, ensure_ascii=False)
        
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                f.write(json_str)
            os.replace(temp_path, filepath)
            updated_count += 1
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"Error saving {os.path.basename(filepath)}: {e}")
            
    print(f"Delimiter conversion complete. Updated {updated_count} files.")

if __name__ == "__main__":
    main()
