import json
import os

shards = {
    "standard-model-overview": "standard-model.json",
    "astrophysics-overview": "astrophysics.json",
    "thermodynamics-statistical-mechanics-overview": "thermodynamics-statistical-mechanics.json",
    "condensed-matter-overview": "condensed-matter.json",
    "fluids-nonlinear-overview": "fluids-nonlinear.json",
    "mathematical-methods-overview": "mathematical-methods.json",
    "philosophy-of-physics-overview": "philosophy-of-physics.json"
}

for slug, shard in shards.items():
    path = os.path.join("app/config/content", shard)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        if slug not in data:
            data[slug] = {}
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)
