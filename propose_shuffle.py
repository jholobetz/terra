import json
import os

def propose_shuffle():
    content_dir = "app/config/content"
    rules = {
        "thermodynamics-statistical-mechanics": ["entropy", "heat", "temperature", "statistical", "thermo", "partition", "ensemble", "boltzmann", "gibbs"],
        "condensed-matter": ["solid", "crystal", "superconductor", "lattice", "phonon", "semiconductor"],
        "fluids-nonlinear": ["fluid", "gas", "viscosity", "turbulence", "chaos", "nonlinear", "navier", "vortex"],
        "mathematical-methods": ["vector", "tensor", "gradient", "divergence", "curl", "calculus", "differential", "algebra", "group", "manifold", "poisson bracket"]
    }

    migration_plan = {cat: [] for cat in rules.keys()}

    for file in os.listdir(content_dir):
        if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "entities.json", "search_index.json"]:
            path = os.path.join(content_dir, file)
            with open(path, "r") as f:
                shard = json.load(f)
            for slug, data in shard.items():
                content = (data.get("title", "") + " " + data.get("content", "")).lower()
                for target_cat, keywords in rules.items():
                    if target_cat in data.get("parents", []): continue
                    if any(kw in content for kw in keywords):
                        migration_plan[target_cat].append({
                            "slug": slug,
                            "title": data.get("title"),
                            "current_shard": file
                        })
                        break

    print("=== PROPOSED TAXONOMY SHUFFLE ===")
    for cat, items in migration_plan.items():
        print(f"\nMove to {cat.upper()} ({len(items)} items):")
        for item in items[:10]:
             print(f"  - [{item['slug']}] {item['title']} (from {item['current_shard']})")
        if len(items) > 10:
            print(f"  ... and {len(items)-10} more.")

if __name__ == "__main__":
    propose_shuffle()
