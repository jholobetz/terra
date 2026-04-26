import json
import re
import os
import subprocess
import shutil
import hashlib

class PhysicsOrchestrator:
    def __init__(self, content_dir="app/config/content", registry_path="global_slug_registry.json"):
        self.content_dir = content_dir
        self.registry_path = registry_path
        self.shards = {}
        self.data = {
            "topics": {},
            "subtopics": {},
            "formula_registry": {},
            "constants": {}
        }
        self.slug_to_shard = {}
        self.load_all_shards()
        self.registry = self._load_json(registry_path)
        self._refresh_sorted_titles()

    def _load_json(self, path):
        if not os.path.exists(path):
            return {}
        with open(path, "r") as f:
            return json.load(f)

    def load_all_shards(self):
        if not os.path.exists(self.content_dir):
            os.makedirs(self.content_dir)
            return

        for file in os.listdir(self.content_dir):
            if file.endswith(".json"):
                path = os.path.join(self.content_dir, file)
                content = self._load_json(path)
                
                if file == "categories.json":
                    self.data["topics"] = content
                elif file == "formulas.json":
                    self.data["formula_registry"] = content
                elif file == "constants.json":
                    self.data["constants"] = content
                else:
                    # Subtopic shard
                    self.shards[file] = content
                    for slug in content:
                        self.data["subtopics"][slug] = content[slug]
                        self.slug_to_shard[slug] = file

    def _refresh_sorted_titles(self):
        self.sorted_titles = sorted(self.registry.keys(), key=len, reverse=True)

    def save(self):
        """Saves all modified shards and registries."""
        # 1. Save Registries/Categories
        with open(os.path.join(self.content_dir, "categories.json"), "w") as f:
            json.dump(self.data["topics"], f, indent=4)
        with open(os.path.join(self.content_dir, "formulas.json"), "w") as f:
            json.dump(self.data["formula_registry"], f, indent=4)
        with open(os.path.join(self.content_dir, "constants.json"), "w") as f:
            json.dump(self.data["constants"], f, indent=4)
        
        # 2. Save Subtopic Shards
        # Re-distribute data back to shards before saving
        for shard_name, shard_content in self.shards.items():
            # Update shard content from master subtopics map
            for slug in shard_content:
                if slug in self.data["subtopics"]:
                    shard_content[slug] = self.data["subtopics"][slug]
            
            with open(os.path.join(self.content_dir, shard_name), "w") as f:
                json.dump(shard_content, f, indent=4)

        # 3. Save Global Registry
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
        print(f"SUCCESS: Sharded save complete in {self.content_dir}")

    def mask_mathjax(self, content):
        placeholders = []
        pattern = re.compile(r'(\\\(.*?\\\)|\\\[.*?\\\])', re.DOTALL)
        def replace(match):
            idx = len(placeholders)
            placeholders.append(match.group(0))
            return f"##MJ_PROTECTED_{idx}##"
        return pattern.sub(replace, content), placeholders

    def unmask_mathjax(self, content, placeholders):
        for i, original in enumerate(placeholders):
            content = content.replace(f"##MJ_PROTECTED_{i}##", original)
        return content

    def apply_auto_links(self, slug, dry_run=False):
        if slug not in self.data["subtopics"]:
            return None
        
        topic = self.data["subtopics"][slug]
        content = topic["content"]
        original_content = content
        
        masked_content, placeholders = self.mask_mathjax(content)
        
        # Performance optimization: get titles for current slug once
        current_titles = [t for t, s in self.registry.items() if s == slug]

        for title in self.sorted_titles:
            target_slug = self.registry[title]
            if target_slug == slug or title in current_titles:
                continue
            
            if f'href="/physics/subtopic/{target_slug}"' in masked_content:
                continue

            link_html = f'<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{title}</strong></a>'
            bold_tag = f"<strong>{title}</strong>"
            
            if bold_tag in masked_content:
                masked_content = masked_content.replace(bold_tag, link_html)
            else:
                plain_pattern = re.compile(rf'(?<![=">])\b{re.escape(title)}\b(?![<])')
                masked_content = plain_pattern.sub(lambda m: link_html, masked_content)
        
        final_content = self.unmask_mathjax(masked_content, placeholders)
        final_content = self._sanitize_mathjax(final_content)
        
        if not dry_run:
            topic["content"] = final_content
            
        return final_content if final_content != original_content else None

    def _sanitize_mathjax(self, content):
        content = content.replace(" > ", " \\gt ")
        content = content.replace(" < ", " \\lt ")
        return content

    def add_subtopic(self, slug, subtopic_data, link_in_parent=True):
        """Adds subtopic to appropriate shard and updates registry."""
        parent_slug = subtopic_data.get("parent_topic", "misc")
        
        # Determine shard (use parent's shard or create new one)
        shard_file = f"{parent_slug}.json"
        if parent_slug in self.data["subtopics"]:
            shard_file = self.slug_to_shard.get(parent_slug, shard_file)
        
        if shard_file not in self.shards:
            self.shards[shard_file] = {}
        
        self.shards[shard_file][slug] = subtopic_data
        self.data["subtopics"][slug] = subtopic_data
        self.slug_to_shard[slug] = shard_file
        
        # Registry update
        self.registry[subtopic_data["title"]] = slug
        self._refresh_sorted_titles()
        
        if link_in_parent:
            # Logic to link in parent would go here, similar to previous version
            pass
            
        self.apply_auto_links(slug)
        return True

    def add_formula(self, title, equation, breakdown):
        """Adds a formula to the registry and returns its ID."""
        slug_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        eq_hash = hashlib.md5(equation.encode()).hexdigest()[:8]
        f_id = f"{slug_title}-{eq_hash}"
        
        self.data["formula_registry"][f_id] = {
            "title": title,
            "equation": equation,
            "breakdown": breakdown
        }
        return f_id

    def validate(self):
        print("Running Integrity Shield...")
        # Since we removed the integrity_shield.py file in cleanup, 
        # I should probably re-add its logic or call the PHP validator.
        result = subprocess.run(["php", "validate_physics_data.php"], capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0

if __name__ == "__main__":
    orchestrator = PhysicsOrchestrator()
    print(f"Orchestrator ready. {len(orchestrator.data['subtopics'])} subtopics loaded from shards.")
