from orchestrator import PhysicsOrchestrator
import execute_sprint

orch = PhysicsOrchestrator()

for slug, data in execute_sprint.sprint_data.items():
    content = data["content"]
    orch.data["subtopics"][slug] = {"parents": data["parents"]}
    orch.registry[data["title"]] = slug
    
orch._refresh_sorted_titles()

for slug, data in execute_sprint.sprint_data.items():
    print(f"\n--- Testing links for: {slug} ---")
    content = data["content"]
    
    # Simulate auto-linking
    linked_content = orch.apply_auto_links(slug, dry_run=True)
    if linked_content is None:
        linked_content = content
        
    # Validation logic
    import re
    links = re.findall(r'href="/physics/(?:subtopic|topic)/([^"]*)"', linked_content)
    print(f"Found {len(links)} links: {links}")
    if len(links) < 5:
        print("FAIL: < 5 links")
    else:
        print("PASS")
