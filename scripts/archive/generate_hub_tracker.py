import os
import sys
import json

# Add project root to path
sys.path.append(os.getcwd())

from orchestrator import PhysicsOrchestrator

def generate_tracker():
    print("Initializing Orchestrator to read current standards...")
    orch = PhysicsOrchestrator()
    
    tracker = {}
    
    # Iterate through all 12 protected hubs
    for hub_slug in orch.PROTECTED_TOPICS:
        if hub_slug not in orch.topic_shards:
            continue
            
        topic_data = orch.topic_shards[hub_slug]
        pillars = topic_data.get("pillars", [])
        
        hub_status = "completed"
        hub_pillars = []
        
        for i, pillar in enumerate(pillars):
            pillar_slugs = pillar.get("slugs", [])
            pillar_status = "completed"
            
            for slug in pillar_slugs:
                if slug in orch.data["subtopics"]:
                    sub_data = orch.data["subtopics"][slug]
                    # Check if the node is platinum
                    if sub_data.get("standard") != "platinum":
                        pillar_status = "unfinished"
                        break
                else:
                    # If it doesn't exist, it's definitely not platinum
                    pillar_status = "unfinished"
                    break
            
            hub_pillars.append({
                "index": i + 1,
                "title": pillar.get("title", f"Pillar {i+1}"),
                "status": pillar_status,
                "total_nodes": len(pillar_slugs)
            })
            
            if pillar_status == "unfinished":
                hub_status = "unfinished"
                
        tracker[hub_slug] = {
            "title": topic_data.get("title", hub_slug),
            "status": hub_status,
            "pillars": hub_pillars
        }
    
    tracker_path = "subfiles/hub_tracker.json"
    with open(tracker_path, "w") as f:
        json.dump(tracker, f, indent=4)
        
    print(f"✓ Tracker generated successfully at {tracker_path}")

if __name__ == "__main__":
    generate_tracker()
