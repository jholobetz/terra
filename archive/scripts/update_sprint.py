import json

with open('sprint.json', 'r') as f:
    sprint = json.load(f)

for item in sprint['queue']:
    if item['slug'] == 'retarded-potentials':
        item['status'] = 'platinum'

sprint['next_target'] = 'larmor-formula'

with open('sprint.json', 'w') as f:
    json.dump(sprint, f, indent=4)
