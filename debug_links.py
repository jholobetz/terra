from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()
content = "<p>The Lagrangian Density of the Standard Model in General Relativity.</p>"
# Fake subtopic for context
orch.data["subtopics"]["test-slug"] = {"parents": ["theoretical-physics"]}

# Manual masking for test
masked, placeholders = orch.mask_mathjax(content)
print(f"Masked: {masked}")

# Run the core of apply_auto_links
parents = ["theoretical-physics"]
for title, target_slug in orch.registry.items():
    if target_slug == "test-slug": continue
    if title in masked:
        print(f"Match found for: {title} -> {target_slug}")
    
    # Check regex
    plain_pattern = re.compile(rf'(?<![=">])\b{re.escape(title)}\b(?![<])')
    if plain_pattern.search(masked):
        print(f"Regex match found for: {title}")
