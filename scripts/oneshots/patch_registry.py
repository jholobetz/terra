import json

categories = [
    ("classical-mechanics", "Classical Mechanics"),
    ("electromagnetism", "Electromagnetism"),
    ("relativity", "Relativity"),
    ("quantum-physics", "Quantum Physics"),
    ("theoretical-physics", "Theoretical Physics"),
    ("standard-model", "The Standard Model"),
    ("astrophysics", "Astrophysics and Cosmology"),
    ("thermodynamics-statistical-mechanics", "Thermodynamics and Statistical Mechanics"),
    ("condensed-matter", "Condensed Matter Physics"),
    ("fluids-nonlinear", "Fluid Dynamics and Nonlinear Systems"),
    ("mathematical-methods", "Mathematical Methods in Physics"),
    ("philosophy-of-physics", "Philosophy of Physics")
]

# 1. Update slug_shard_map.json
with open('slug_shard_map.json', 'r') as f:
    shard_map = json.load(f)

for slug, title in categories:
    overview_slug = f"{slug}-overview"
    shard_name = f"{slug}.json"
    shard_map[overview_slug] = shard_name

with open('slug_shard_map.json', 'w') as f:
    json.dump(shard_map, f, indent=4)

# 2. Update global_slug_registry.json
with open('global_slug_registry.json', 'r') as f:
    registry = json.load(f)

for slug, title in categories:
    overview_slug = f"{slug}-overview"
    key = f"{title} Overview"
    if key not in registry:
        registry[key] = overview_slug
    # Add another one for convenience if we just mention it
    key2 = title
    # We might not want to override the base title if it points to the hub, but let's check.
    # Actually let's just add the " Overview" ones.

with open('global_slug_registry.json', 'w') as f:
    json.dump(registry, f, indent=4)

print("Updated map and registry.")
