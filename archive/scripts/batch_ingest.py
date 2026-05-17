import os
import sys
import json
import argparse

# Add project root to path
sys.path.append(os.getcwd())

from orchestrator import PhysicsOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Batch ingest OPS-compliant content into the Physics Lab.")
    parser.add_argument("input_file", help="Path to the JSON file containing the subtopic data.")
    parser.add_argument("--auto-commit", action="store_true", help="Automatically commit changes to git.")
    parser.add_argument("--unlock", action="store_true", help="Unlock protected topics for editing.")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"ERROR: Input file not found: {args.input_file}")
        sys.exit(1)
        
    try:
        with open(args.input_file, "r") as f:
            new_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse JSON input: {e}")
        sys.exit(1)
        
    print(f"Initializing Physics Orchestrator...")
    orch = PhysicsOrchestrator()
    
    ingested_count = 0
    for slug, payload in new_data.items():
        if slug not in orch.data["subtopics"]:
            # If it's a brand new subtopic, we initialize it
            print(f"Initializing NEW subtopic: {slug}")
            orch.data["subtopics"][slug] = {
                "title": payload.get("title", slug),
                "content": "",
                "parents": payload.get("parents", []),
                "standard": "legacy"
            }
        
        # Update fields
        orch.data["subtopics"][slug].update(payload)
        orch.modified_slugs.add(slug)
        ingested_count += 1
        print(f"Queued for ingestion: {slug} ({payload.get('standard', 'legacy')})")
        
    if ingested_count > 0:
        print(f"\nPhase 2: Saving to shards and pre-rendering {ingested_count} subtopics...")
        orch.save(auto_commit=args.auto_commit, unlock_protected=args.unlock)
        print(f"\n✓ Batch ingestion complete. {ingested_count} nodes updated.")
    else:
        print("No valid data found in input file. Nothing to do.")

if __name__ == "__main__":
    main()
