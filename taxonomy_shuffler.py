import json
import os

def shuffle():
    content_dir = "app/config/content"
    
    # Precise title-based rules for first-pass shuffle
    rules = {
        "thermodynamics-statistical-mechanics": ["entropy", "thermodynamic", "statistical mechanics", "boltzmann", "partition function", "heat", "temperature"],
        "condensed-matter": ["superconductor", "crystal", "semiconductor", "solid state", "lattice", "phonon"],
        "fluids-nonlinear": ["fluid dynamics", "viscosity", "turbulence", "chaos", "nonlinear", "navier-stokes"],
        "mathematical-methods": ["vector calculus", "differential geometry", "group theory", "complex analysis", "matrix", "tensor calculus"]
    }

    shards = {}
    for file in os.listdir(content_dir):
        if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "entities.json", "search_index.json", "shard_index.json"]:
            with open(os.path.join(content_dir, file), "r") as f:
                shards[file] = json.load(f)

    moves_made = 0
    for cat in rules.keys():
        shard_name = f"{cat}.json"
        if shard_name not in shards:
            shards[shard_name] = {}

    for target_cat, keywords in rules.items():
        target_shard = f"{target_cat}.json"
        
        for shard_name, content in list(shards.items()):
            if shard_name == target_shard: continue
            
            to_move = []
            for slug, data in content.items():
                title = data.get("title", "").lower()
                if any(kw in title for kw in keywords):
                    to_move.append(slug)
            
            for slug in to_move:
                # Update Parents (Primary home becomes the new cat)
                shards[shard_name][slug]["parents"] = [target_cat]
                # Move to new Shard
                shards[target_shard][slug] = shards[shard_name].pop(slug)
                moves_made += 1

    for shard_name, content in shards.items():
        with open(os.path.join(content_dir, shard_name), "w") as f:
            json.dump(content, f, indent=4)

    print(f"SUCCESS: Shuffle complete. {moves_made} topics re-parented.")

if __name__ == "__main__":
    shuffle()
