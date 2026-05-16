import json
from orchestrator import PhysicsOrchestrator

orch = PhysicsOrchestrator()
sub = orch.data["subtopics"]["success-argument"]
c = sub["content"]

c = c.replace('href="/physics/subtopic/electron"', 'href="/physics/subtopic/leptons"')
c = c.replace('href="/physics/subtopic/epistemology"', 'href="/physics/subtopic/epistemic"')

if sub["content"] != c:
    sub["content"] = c
    orch.modified_slugs.add("success-argument")
    orch.save(auto_commit=True, commit_msg="Fix remaining broken links in success-argument")
    orch.build(slug="success-argument")
    print("SUCCESS: Broken links repaired.")
else:
    print("No changes needed.")
