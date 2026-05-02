import json
with open('app/config/content/categories.json', 'r') as f:
    data = json.load(f)
with open('test_out.json', 'w') as f:
    json.dump(data, f, indent=4)
