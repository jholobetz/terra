import json
import os
import re

content_dir = 'app/config/content'
slugs = ['special-orthogonal-group-so3', 'torque', 'axial-vector', 'rotational-dynamics', 'rigid-body', 'minkowski-metric', 'length-contraction-formula', 'time-dilation-formula', 'electroweak-symmetry-group', 'mass-eigenstates']

def fix_links(content):
    # Find all <a href="/physics/subtopic/...">...</a>
    # Replace with <a href="/physics/subtopic/..." class="subtopic-link"><strong>...</strong></a>
    
    # We want to match: <a href="(/physics/subtopic/[^"]+)"(?: class="[^"]*")?>(?:<strong>)?(.*?)(?:</strong>)?</a>
    
    def repl(m):
        url = m.group(1)
        inner = m.group(2)
        # Strip any existing strong tags just in case
        inner = re.sub(r'</?strong>', '', inner)
        return f'<a href="{url}" class="subtopic-link"><strong>{inner}</strong></a>'
        
    pattern = re.compile(r'<a href="(/physics/subtopic/[^"]+)"(?: class="[^"]*")?>(?:<strong>)?(.*?)(?:</strong>)?</a>')
    return pattern.sub(repl, content)

for filename in ['classical-mechanics.json', 'relativity.json', 'standard-model.json']:
    path = os.path.join(content_dir, filename)
    with open(path, 'r') as f:
        data = json.load(f)
    
    modified = False
    for slug, payload in data.items():
        if slug in slugs:
            old_content = payload.get('content', '')
            new_content = fix_links(old_content)
            if new_content != old_content:
                payload['content'] = new_content
                modified = True
                print(f"Fixed links for {slug}")
                
    if modified:
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
