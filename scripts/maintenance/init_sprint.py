import sys
import json
import os
from datetime import datetime

ACTIVE_SPRINT_PATH = 'subfiles/active_expansion_sprint.json'

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

    # Load backlog frequencies if available (optional enrichment)
    backlog_freq = {}
    backlog_path = 'subfiles/expansion_backlog.json'
    if os.path.exists(backlog_path):
        try:
            with open(backlog_path, 'r') as f:
                for item in json.load(f):
                    if 'suggested_slug' in item:
                        backlog_freq[item['suggested_slug']] = item.get('frequency')
        except (json.JSONDecodeError, OSError):
            pass

    queue = []
    shards_involved = set()

    # We load shard data lazily to avoid loading the same file multiple times if possible
    loaded_shards = {}

    for slug in slugs:
        si_entry = search_index.get(slug, {})
        shard_name = si_entry.get('s', f'{hub_slug}.json')
        title = si_entry.get('t', slug)
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
            status = 'completed'

        shards_involved.add(shard_name)
        queue.append({
            'slug': slug,
            'title': title,
            'shard': shard_name,
            'frequency': backlog_freq.get(slug),
            'status': status
        })

    active_target = next((item['slug'] for item in queue if item['status'] == 'pending'), None)

    sprint_data = {
        'sprint_id': f'{hub_slug}_pillar_{pillar_index + 1}',
        'theme': pillar_title,
        'hub': hub_slug,
        'pillar': pillar_title,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'shards_involved': sorted(shards_involved),
        'queue': queue,
        'active_target': active_target
    }

    with open(ACTIVE_SPRINT_PATH, 'w') as f:
        json.dump(sprint_data, f, indent=4)
        f.write('\n')

    print(f"✓ Sprint initialized at {ACTIVE_SPRINT_PATH}")
    print(f"  Total items: {len(queue)}")
    print(f"  Active target: {active_target if active_target else 'Sprint Complete'}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 init_sprint.py <hub_slug> <pillar_index>")
        print("Example: python3 init_sprint.py quantum-physics 2")
        sys.exit(1)
    
    init_sprint(sys.argv[1], sys.argv[2])
