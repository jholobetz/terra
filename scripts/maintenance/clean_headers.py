from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()
target_slugs = ["euler-lagrange-field-form", "reduced-dynamics", "holonomic-constraints"]

for slug in target_slugs:
    if slug in orch.data["subtopics"]:
        content = orch.data["subtopics"][slug]["content"]
        # Remove numbers from h3 tags like '<h3>1. ' or '<h3>2. '
        # Regex: match <h3> followed by any digits and a dot and a space.
        cleaned_content = re.sub(r'<h3>\d+\.\s*', '<h3>', content)
        
        if content != cleaned_content:
            orch.data["subtopics"][slug]["content"] = cleaned_content
            orch.modified_slugs.add(slug)
            print(f"Cleaned headers for [{slug}].")

if orch.modified_slugs:
    orch.save(auto_commit=True, commit_msg="Enforce organic prose layout on recent topics")
    for slug in orch.modified_slugs:
        orch.build(slug=slug)
    print("SUCCESS: Cleaned topics saved and built.")
else:
    print("No changes needed.")
