import sys
import json
import os

def init_sprint(hub_slug, pillar_index_str):
    try:
        pillar_index = int(pillar_index_str) - 1
    except ValueError:
        print(f"Error: Pillar index '{pillar_index_str}' must be an integer.")
        sys.exit(1)

    manifest_path = os.path.join('hub_manifests', f'{hub_slug}.json')
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest not found at {manifest_path}")
        sys.exit(1)

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    if pillar_index < 0 or pillar_index >= len(manifest.get('pillars', [])):
        print(f"Error: Pillar index {pillar_index + 1} is out of bounds for hub '{hub_slug}'.")
        sys.exit(1)

    pillar = manifest['pillars'][pillar_index]
    pillar_title = pillar.get('title', f"Pillar {pillar_index + 1}")
    slugs = pillar.get('slugs', [])

    print(f"Initializing sprint for Hub: {hub_slug}, Pillar: {pillar_title}")

    # Load search index to find physical shards
    search_index_path = 'app/config/content/search_index.json'
    if os.path.exists(search_index_path):
        with open(search_index_path, 'r') as f:
            search_index = json.load(f)
    else:
        print("Warning: search_index.json not found. Assuming default shards.")
        search_index = {}

    queue = []
    
    # We load shard data lazily to avoid loading the same file multiple times if possible
    loaded_shards = {}

    for slug in slugs:
        shard_name = search_index.get(slug, {}).get('s', f'{hub_slug}.json')
        status = 'pending'
        
        shard_path = os.path.join('app/config/content', shard_name)
        
        if shard_name not in loaded_shards:
            if os.path.exists(shard_path):
                with open(shard_path, 'r') as f:
                    try:
                        loaded_shards[shard_name] = json.load(f)
                    except json.JSONDecodeError:
                        loaded_shards[shard_name] = {}
            else:
                loaded_shards[shard_name] = {}

        shard_data = loaded_shards[shard_name]
        node = shard_data.get(slug, {})
        
        if node.get('standard') == 'platinum':
            status = 'platinum'
            
        queue.append({'slug': slug, 'shard': shard_name, 'status': status})

    next_target = next((item['slug'] for item in queue if item['status'] == 'pending'), 'Pillar Complete')

    sprint_data = {
        'hub': hub_slug,
        'pillar': pillar_title,
        'last_updated': '2026-05-16',
        'queue': queue,
        'next_target': next_target
    }

    with open('sprint.json', 'w') as f:
        json.dump(sprint_data, f, indent=4)

    print(f"✓ Sprint initialized successfully.")
    print(f"  Total items: {len(queue)}")
    print(f"  Next target: {next_target}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 init_sprint.py <hub_slug> <pillar_index>")
        print("Example: python3 init_sprint.py quantum-physics 2")
        sys.exit(1)
    
    init_sprint(sys.argv[1], sys.argv[2])
