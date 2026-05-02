import re
import json

import sys

input_file = sys.argv[1] if len(sys.argv) > 1 else 'refactor_batch_b.json'
output_file = sys.argv[2] if len(sys.argv) > 2 else 'refactor_batch_b_fixed.json'

with open(input_file, 'r') as f:
    s = f.read()

# Replace any \ that is not followed by a valid JSON escape character
def replacer(match):
    g = match.group(0)
    if g[1] in 'nrtbf\\"':
        return g
    return r'\\' + g[1]

fixed = re.sub(r'\\.', replacer, s, flags=re.DOTALL)

try:
    data = json.loads(fixed)
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print("Successfully fixed JSON.")
except Exception as e:
    print(f"Failed to fix JSON: {e}")
    # Print a bit of context around the error
    match = re.search(r'char (\d+)', str(e))
    if match:
        pos = int(match.group(1))
        print(f"Error at pos {pos}: {s[max(0, pos-20):pos+20]}")
