from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()

# 1. left-handed-doublet
if "left-handed-doublet" in orch.data["subtopics"]:
    c = orch.data["subtopics"]["left-handed-doublet"]["content"]
    c = c.replace('<a href="/physics/subtopic/<a href="/physics/subtopic/lhc" class="subtopic-link"><strong>lhc</strong></a>-searches" class="subtopic-link"><strong>LHC Searches and New Physics</strong></a>', '<a href="/physics/subtopic/lhc-searches" class="subtopic-link"><strong>LHC Searches and New Physics</strong></a>')
    orch.data["subtopics"]["left-handed-doublet"]["content"] = c
    orch.modified_slugs.add("left-handed-doublet")

# 2. routhian-reduction
if "routhian-reduction" in orch.data["subtopics"]:
    c = orch.data["subtopics"]["routhian-reduction"]["content"]
    c = c.replace('<a href="/physics/subtopic/emmy-<a href="/physics/subtopic/noether" class="subtopic-link"><strong>noether</strong></a>" class="subtopic-link"><strong>Noether</strong></a>', '<a href="/physics/subtopic/emmy-noether" class="subtopic-link"><strong>Emmy Noether</strong></a>')
    orch.data["subtopics"]["routhian-reduction"]["content"] = c
    orch.modified_slugs.add("routhian-reduction")

# 3. action-physics
if "action-physics" in orch.data["subtopics"]:
    c = orch.data["subtopics"]["action-physics"]["content"]
    c = c.replace('<a href="/physics/subtopic/isaac-<a href="/physics/subtopic/newton" class="subtopic-link"><strong>newton</strong></a>" class="subtopic-link"><strong>Newton</strong></a>', '<a href="/physics/subtopic/isaac-newton" class="subtopic-link"><strong>Isaac Newton</strong></a>')
    c = c.replace('<a href="/physics/subtopic/albert-<a href="/physics/subtopic/einstein" class="subtopic-link"><strong>einstein</strong></a>" class="subtopic-link"><strong>Einstein</strong></a>', '<a href="/physics/subtopic/albert-einstein" class="subtopic-link"><strong>Albert Einstein</strong></a>')
    orch.data["subtopics"]["action-physics"]["content"] = c
    orch.modified_slugs.add("action-physics")

if orch.modified_slugs:
    orch.save(auto_commit=True, commit_msg="Surgically repair nested malformed HTML links")
    for slug in orch.modified_slugs:
        orch.build(slug=slug)
    print("SUCCESS: Nested links repaired.")
else:
    print("No modifications made.")
