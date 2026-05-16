import json

with open('app/config/content/electromagnetism.json', 'r') as f:
    data = json.load(f)

content = data['retarded-potentials']['content']
content = content.replace("<strong>Standard Model</strong>", "<strong>Quantum Field Theory</strong>")

data['retarded-potentials']['content'] = content

with open('app/config/content/electromagnetism.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Updated retarded-potentials content.")
