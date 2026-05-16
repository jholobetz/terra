from orchestrator import PhysicsOrchestrator
import re

orch = PhysicsOrchestrator()
target_slugs = ['left-handed-doublet', 'light-cone', 'routhian-reduction', 'action-physics', 'newtons-second-law']

print("--- Broken Link Contexts ---")
for slug in target_slugs:
    content = orch.data["subtopics"].get(slug, {}).get("content", "")
    
    if slug == "left-handed-doublet":
        matches = re.finditer(r'.{0,40}<a href=.{0,40}', content)
        for m in matches:
            if 'href="' not in m.group(0): # malformed
                print(f"[{slug}] {m.group(0)}")
            elif 'href="/physics' not in m.group(0):
                 print(f"[{slug}] {m.group(0)}")
    
    elif slug == "light-cone":
        matches = re.finditer(r'.{0,40}causality.{0,40}', content)
        for m in matches:
            print(f"[{slug}] {m.group(0)}")
            
    elif slug == "routhian-reduction":
        matches = re.finditer(r'.{0,40}emmy-.{0,40}', content)
        for m in matches:
            print(f"[{slug}] {m.group(0)}")
            
    elif slug == "action-physics":
        matches = re.finditer(r'.{0,40}isaac-.{0,40}', content)
        for m in matches:
            print(f"[{slug}] {m.group(0)}")
        matches = re.finditer(r'.{0,40}albert-.{0,40}', content)
        for m in matches:
            print(f"[{slug}] {m.group(0)}")
            
    elif slug == "newtons-second-law":
        matches = re.finditer(r'.{0,40}href="[^"]*momentum[^"]*".{0,40}', content)
        for m in matches:
            print(f"[{slug}] {m.group(0)}")
