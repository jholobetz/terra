from orchestrator import PhysicsOrchestrator
import time

def test_performance():
    orch = PhysicsOrchestrator()
    print(f"Loaded {len(orch.data['subtopics'])} subtopics.")
    
    # 1. Test Incremental Save
    slug = "action-physics" # Existing slug
    if slug in orch.data["subtopics"]:
        print(f"\nTesting Incremental Save for [{slug}]...")
        start = time.time()
        # Mock an update
        sub = orch.data["subtopics"][slug]
        orch.update_subtopic(slug, sub) 
        orch.save(auto_commit=False)
        print(f"Incremental Save took: {time.time() - start:.2f}s")

    # 2. Test Batch SVG Rendering
    print("\nTesting Batch SVG Rendering...")
    # Add a new subtopic with many unique formulas
    new_slug = "perf-test-topic"
    new_data = {
        "title": "Performance Test Topic",
        "content": "Formula 1: \\( E=mc^2 \\). Formula 2: \\[ F=ma \\]. Formula 3: \\( \\nabla \\cdot B = 0 \\).",
        "parents": ["theoretical-physics"]
    }
    orch.add_subtopic(new_slug, new_data)
    start = time.time()
    orch.save(auto_commit=False)
    print(f"Batch Save (with 3 new formulas) took: {time.time() - start:.2f}s")
    
    # 3. Test Parallel Build (Surgical)
    print("\nTesting Surgical Build...")
    start = time.time()
    orch.build(slug=new_slug)
    print(f"Surgical Build took: {time.time() - start:.2f}s")

    # Clean up
    orch.delete_subtopic(new_slug)
    orch.save(auto_commit=False)

if __name__ == "__main__":
    test_performance()
