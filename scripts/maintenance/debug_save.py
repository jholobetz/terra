from orchestrator import PhysicsOrchestrator
import json

orch = PhysicsOrchestrator()
slug = "universal-gravitation"
orch.data["subtopics"][slug] = {"title": "Test", "content": "Test content", "parents": ["classical-mechanics"]}

# Run the logic from orchestrator.py
found_shard = False
for shard_name, shard_content in orch.shards.items():
    if slug in shard_content:
        shard_content[slug] = orch.data["subtopics"][slug]
        found_shard = True
        break

if not found_shard:
    target_shard = "classical-mechanics.json"
    orch.shards[target_shard][slug] = orch.data["subtopics"][slug]
    print(f"DEBUG: Added to {target_shard}")

print(f"DEBUG: {slug} in shards['classical-mechanics.json']: {slug in orch.shards['classical-mechanics.json']}")

orch.save(auto_commit=False, unlock_protected=True)
