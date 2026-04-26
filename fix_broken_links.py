import json
import re
import os
from orchestrator import PhysicsOrchestrator

orch = PhysicsOrchestrator()
orch.load_all_shards()

valid_slugs = set(orch.registry.values())
valid_slugs.update(orch.data.get("search_index", {}).keys())

def link_replacer(match):
    target = match.group(1)
    if target in valid_slugs:
        return match.group(0)
    else:
        print(f"Stripping hallucinated link: {target}")
        return match.group(2)

pattern = re.compile(r'<a href="/physics/subtopic/([^"]+)"[^>]*>(.*?)</a>')

changes = 0
for slug, sub_data in orch.data["subtopics"].items():
    if "content" in sub_data:
        old_content = sub_data["content"]
        new_content = pattern.sub(link_replacer, old_content)
        if old_content != new_content:
            sub_data["content"] = new_content
            orch.add_subtopic(slug, sub_data)
            changes += 1

if changes > 0:
    orch.save(auto_commit=True, commit_msg=f"Auto-fix {changes} subtopics with broken links.")
else:
    print("No broken links found.")
