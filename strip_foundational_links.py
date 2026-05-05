from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()

# Target slugs that were updated during the sprints
target_slugs = [
    "euler-lagrange-field-form",
    "reduced-dynamics",
    "holonomic-constraints",
    "left-handed-doublet",
    "success-argument",
    "routhian-reduction"
]

for slug in target_slugs:
    if slug in orch.data["subtopics"]:
        content = orch.data["subtopics"][slug]["content"]
        # Remove the foundational-link injected HTML
        cleaned_content = re.sub(r'<p class="foundational-link">.*?</p>\s*', '', content, flags=re.DOTALL)
        
        if content != cleaned_content:
            orch.data["subtopics"][slug]["content"] = cleaned_content
            orch.modified_slugs.add(slug)
            print(f"Removed foundational link from [{slug}].")

if orch.modified_slugs:
    orch.save(auto_commit=True, commit_msg="Remove foundational link from recent topics to match Platinum Standard")
    for slug in orch.modified_slugs:
        orch.build(slug=slug)
    print("SUCCESS: Cleaned topics saved and built.")
else:
    print("No foundational links found to remove.")
