import os
import json
import glob
import re
import tempfile

CONTROL_CHARS_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')

was_modified = False

def clean_string(s):
    global was_modified
    if not isinstance(s, str):
        return s
    cleaned, count = CONTROL_CHARS_RE.subn('', s)
    if count > 0:
        was_modified = True
    return cleaned

def clean_data(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            clean_k = clean_string(k)
            # If the key is empty after cleaning, discard it
            if not clean_k:
                continue
            new_dict[clean_k] = clean_data(v)
        return new_dict
    elif isinstance(data, list):
        return [clean_data(item) for item in data]
    elif isinstance(data, str):
        return clean_string(data)
    else:
        return data

def main():
    global was_modified
    shards_dir = "/Users/holobetj/code/gemini/terra/app/config/content/formulas"
    shard_files = glob.glob(os.path.join(shards_dir, "shard_*.json"))
    shard_files.sort()
    
    print(f"Found {len(shard_files)} shards to check.")
    cleaned_count = 0
    
    for filepath in shard_files:
        was_modified = False
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"Error reading {os.path.basename(filepath)}: {e}")
                continue
        
        # Clean data recursively
        cleaned = clean_data(data)
        
        if was_modified:
            cleaned_str = json.dumps(cleaned, indent=4, ensure_ascii=False)
            
            # Save atomically
            temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
            try:
                with open(temp_fd, 'w', encoding='utf-8') as f:
                    f.write(cleaned_str)
                os.replace(temp_path, filepath)
                print(f"Cleaned control characters in {os.path.basename(filepath)}")
                cleaned_count += 1
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                print(f"Error saving {os.path.basename(filepath)}: {e}")
            
    print(f"Cleanup finished. Cleaned {cleaned_count} files.")

if __name__ == "__main__":
    main()
