import json

categories = {
    "classical-mechanics": "Classical Mechanics",
    "electromagnetism": "Electromagnetism",
    "relativity": "Relativity",
    "quantum-physics": "Quantum Physics",
    "theoretical-physics": "Theoretical Physics",
    "standard-model": "The Standard Model",
    "astrophysics": "Astrophysics and Cosmology",
    "thermodynamics-statistical-mechanics": "Thermodynamics and Statistical Mechanics",
    "condensed-matter": "Condensed Matter Physics",
    "fluids-nonlinear": "Fluid Dynamics and Nonlinear Systems",
    "mathematical-methods": "Mathematical Methods in Physics",
    "philosophy-of-physics": "Philosophy of Physics"
}

with open('global_slug_registry.json', 'r') as f:
    registry = json.load(f)

for slug, title in categories.items():
    registry[f"Hub: {title}"] = slug

with open('global_slug_registry.json', 'w') as f:
    json.dump(registry, f, indent=4)

