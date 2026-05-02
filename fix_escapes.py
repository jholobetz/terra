import os
import re

def fix_json_escapes(path):
    if not os.path.exists(path):
        return
    with open(path, 'r') as f:
        content = f.read()
    
    # Replace literal \\n with \n (which JSON decodes to a newline byte)
    # Replace literal \\t with \t
    # Replace literal \\r with \r
    # We must be careful not to touch \\ followed by ( or [ if we want to keep them.
    
    new_content = content.replace('\\\\n', '\\n')
    new_content = new_content.replace('\\\\t', '\\t')
    new_content = new_content.replace('\\\\r', '\\r')
    
    if new_content != content:
        with open(path, 'w') as f:
            f.write(new_content)
        print(f"Fixed escapes in {path}")

content_dir = 'app/config/content'
for root, dirs, files in os.walk(content_dir):
    for file in files:
        if file.endswith('.json'):
            fix_json_escapes(os.path.join(root, file))
