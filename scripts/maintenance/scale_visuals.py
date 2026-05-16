import json
import re
import os

def scale_visual_complexity():
    from orchestrator import PhysicsOrchestrator
    orch = PhysicsOrchestrator()
    
    all_subtopics = orch.data["subtopics"]
    tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
    
    shards_to_save = set()
    total_updated = 0

    for slug, sub in all_subtopics.items():
        if "content" not in sub:
            continue
            
        content = sub["content"]
        words = len(re.findall(r'\w+', content))
        latex_count = len(re.findall(r'\\\(|\\\[', content))
        term_score = sum(5 for term in tech_terms if term in content.lower())
        density_score = (latex_count * 15) + term_score
        
        # Determine Target Complexity
        # Base: 3
        # Platinum (500w/60d): 15
        # Linear scaling between 200 and 800 words
        word_comp = max(3, min(12, int(words / 50)))
        density_comp = max(0, min(8, int(density_score / 15)))
        
        target_complexity = word_comp + density_comp
        # Hard cap at 20 for engine stability
        target_complexity = min(20, target_complexity)
        
        # Determine Color (Platinum Glow)
        is_platinum = words >= 500 and density_score >= 60
        
        if "visual_config" not in sub:
            # Default if missing
            sub["visual_config"] = {"type": "abstract", "color": "#FFD700", "complexity": 5}
            
        current_config = sub["visual_config"]
        
        # Only update if there's a significant change
        if current_config.get("complexity") != target_complexity or (is_platinum and current_config.get("color") == "#FFD700"):
            current_config["complexity"] = target_complexity
            if is_platinum:
                # Use a more vibrant "Cyan" for Platinum topics
                current_config["color"] = "#64ffda"
            
            total_updated += 1
            shard_file = orch.slug_to_shard.get(slug)
            if shard_file:
                shards_to_save.add(shard_file)

    if total_updated > 0:
        # We manually save shards to avoid auto-commit and ensure only modified ones are written
        for shard_file in shards_to_save:
            shard_path = os.path.join(orch.content_dir, shard_file)
            shard_content = orch.shards[shard_file]
            with open(shard_path, "w") as f:
                json.dump(shard_content, f, indent=4)
        
        print(f"SUCCESS: Visual complexity scaled for {total_updated} subtopics across {len(shards_to_save)} shards.")
    else:
        print("No visual updates required.")

if __name__ == "__main__":
    scale_visual_complexity()
