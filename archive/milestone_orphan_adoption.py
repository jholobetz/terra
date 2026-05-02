import json
import os
import re
from orchestrator import PhysicsOrchestrator

class OrphanAdopter(PhysicsOrchestrator):
    def __init__(self, content_path="app/config/physics_content.json", orphan_path="orphan_registry.json"):
        super().__init__(content_path, orphan_path)
        # Sort by length descending to match full phrases before sub-phrases
        self.orphan_titles = sorted(self.registry.keys(), key=len, reverse=True)

    def adopt_in_slug(self, slug):
        if slug not in self.data["subtopics"]:
            return False
        
        topic = self.data["subtopics"][slug]
        content = topic["content"]
        original_content = content
        
        for title in self.orphan_titles:
            target_slug = self.registry[title]
            if target_slug == slug:
                continue
            
            # Case 1: Already bolded but not linked
            bold_pattern = f"<strong>{re.escape(title)}</strong>"
            # Case 2: Plain text mention (University level tends to bold them, but let's be safe)
            # Use negative lookbehind/lookahead to avoid matching inside existing tags or attributes
            plain_pattern = re.compile(rf'(?<![">])\b{re.escape(title)}\b(?![<])')
            
            link_html = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{title}</strong></a>'
            
            if f'href="/physics/subtopic/{target_slug}"' not in content:
                # Replace bold first (using string replace to avoid regex overhead/escaping issues here)
                # But title was escaped for pattern, not for string replace. 
                # Let's use the raw title for string replace.
                raw_bold = f"<strong>{title}</strong>"
                if raw_bold in content:
                    content = content.replace(raw_bold, link_html)
                else:
                    # Only try regex if bold was not found
                    # Use lambda to ensure replacement string is treated as literal
                    content = plain_pattern.sub(lambda m: link_html, content)
        
        if content != original_content:
            topic["content"] = self._sanitize_mathjax(content)
            return True
        return False

def run_orphan_batch(batch_size):
    progress_path = "orphan_milestone_progress.json"
    start_index = 0
    if os.path.exists(progress_path):
        with open(progress_path, "r") as f:
            progress = json.load(f)
            start_index = progress.get("last_processed_index", 0)

    adopter = OrphanAdopter()
    slugs = list(adopter.data["subtopics"].keys())
    
    if start_index >= len(slugs):
        print("ALL TOPICS CHECKED FOR ADOPTION.")
        # Reset progress for full re-scan if needed or just stop
        return len(slugs)

    end_index = min(start_index + batch_size, len(slugs))
    batch_slugs = slugs[start_index:end_index]
    
    print(f"Processing Adoption Batch: {start_index} to {end_index} (Total: {len(slugs)})")
    
    changed_count = 0
    for slug in batch_slugs:
        if adopter.adopt_in_slug(slug):
            changed_count += 1
            
    adopter.save()
    print(f"Batch complete. {changed_count} subtopics adopted at least one orphan.")
    
    with open(progress_path, "w") as f:
        json.dump({"last_processed_index": end_index, "goal": "Orphan Adoption"}, f)
        
    return end_index

if __name__ == "__main__":
    run_orphan_batch(50)
