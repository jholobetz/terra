from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()

target_slugs = [
    "left-handed-doublet",
    "success-argument",
    "routhian-reduction"
]

for slug in target_slugs:
    if slug in orch.data["subtopics"]:
        content = orch.data["subtopics"][slug]["content"]
        # Remove the related-concepts injected HTML
        cleaned_content = re.sub(r"<div class='related-concepts'><p><strong>Related Explanations:</strong> .*?</p></div>", "", content, flags=re.DOTALL)
        
        if content != cleaned_content:
            orch.data["subtopics"][slug]["content"] = cleaned_content
            orch.modified_slugs.add(slug)
            print(f"Removed Guaranteed Link Seeding from [{slug}].")

if orch.modified_slugs:
    orch.save(auto_commit=True, commit_msg="Remove artificial Guaranteed Link Seeding from recent topics to match pure Platinum Standard")
    for slug in orch.modified_slugs:
        orch.build(slug=slug)
    print("SUCCESS: Cleaned topics saved and built.")
else:
    print("No seeded links found to remove.")
