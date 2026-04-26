import json
import os
from orchestrator import PhysicsOrchestrator

def run_batch(batch_size):
    progress_path = "milestone_progress.json"
    start_index = 0
    if os.path.exists(progress_path):
        with open(progress_path, "r") as f:
            progress = json.load(f)
            start_index = progress.get("last_processed_index", 0)

    orchestrator = PhysicsOrchestrator()
    slugs = list(orchestrator.data["subtopics"].keys())
    
    if batch_size == -1:
        end_index = len(slugs)
    else:
        end_index = min(start_index + batch_size, len(slugs))
    
    batch_slugs = slugs[start_index:end_index]
    
    if start_index >= len(slugs):
        print("ALL TOPICS PROCESSED.")
        return len(slugs)

    print(f"Processing: {start_index} to {end_index} (Total: {len(slugs)})")
    
    changed_count = 0
    for slug in batch_slugs:
        if orchestrator.apply_auto_links(slug):
            changed_count += 1
            
    orchestrator.save()
    print(f"Update complete. Modified {changed_count} subtopics.")
    
    with open(progress_path, "w") as f:
        json.dump({"last_processed_index": end_index, "goal": "Project-Wide Interlinking"}, f)
        
    return end_index

if __name__ == "__main__":
    run_batch(50)
