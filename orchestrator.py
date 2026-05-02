import json
import re
import os
import subprocess
import shutil
import hashlib
import sys

class PhysicsOrchestrator:
    PROTECTED_TOPICS = {
        "classical-mechanics", "electromagnetism", "relativity", "quantum-physics",
        "standard-model", "astrophysics", "theoretical-physics", "thermodynamics-statistical-mechanics",
        "condensed-matter", "fluids-nonlinear", "mathematical-methods", "philosophy-of-physics"
    }

    def __init__(self, content_dir="app/config/content", registry_path="global_slug_registry.json"):
        self.content_dir = content_dir
        self.registry_path = registry_path
        self.shards = {} # Subtopic shards
        self.topic_shards = {} # Main topic shards
        self.data = {
            "topics": {}, # Meta registry
            "topic_contents": {}, # Loaded content for main topics
            "subtopics": {},
            "formula_registry": {},
            "constants": {},
            "entities": {}
        }
        self.slug_to_shard = {}
        
        # Load Global Slug Registry
        if os.path.exists(self.registry_path):
            with open(self.registry_path, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {}
            
        self._load_content()
        self._refresh_sorted_titles()

    def _load_content(self):
        """Loads all JSON shards from the content directory."""
        # 1. Load Topic Meta Registry
        categories_path = os.path.join(self.content_dir, "categories.json")
        if os.path.exists(categories_path):
            with open(categories_path, "r") as f:
                self.data["topics"] = json.load(f)

        # 2. Load Shards
        for root, dirs, files in os.walk(self.content_dir):
            for file in files:
                if not file.endswith(".json"): continue
                
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, self.content_dir)

                with open(path, "r") as f:
                    content = json.load(f)
                
                if rel_path == "formulas.json":
                    self.data["formula_registry"] = content
                elif rel_path == "constants.json":
                    self.data["constants"] = content
                elif rel_path == "entities.json":
                    self.data["entities"] = content
                elif rel_path == "categories.json":
                    pass # Already loaded
                elif rel_path == "search_index.json":
                    pass
                elif rel_path.startswith("topics/"):
                    slug = file.replace(".json", "")
                    self.topic_shards[slug] = content
                    self.data["topic_contents"][slug] = content
                else:
                    # Subtopic shard
                    self.shards[rel_path] = content
                    for slug in content:
                        self.data["subtopics"][slug] = content[slug]
                        self.slug_to_shard[slug] = rel_path

    def _refresh_sorted_titles(self):
        self.sorted_titles = sorted(self.registry.keys(), key=len, reverse=True)

    def save(self, auto_commit=True, commit_msg=None, unlock_protected=False):
        """Saves all modified shards and registries and optionally commits to Git."""
        # 1. Save Registries
        # Clean topics for categories.json (metadata only)
        clean_topics = {}
        for slug, meta in self.data["topics"].items():
            clean_topics[slug] = {
                "title": meta["title"],
                "shard": meta.get("shard", f"topics/{slug}.json")
            }

        with open(os.path.join(self.content_dir, "categories.json"), "w") as f:
            json.dump(clean_topics, f, indent=4)
        with open(os.path.join(self.content_dir, "formulas.json"), "w") as f:
            json.dump(self.data["formula_registry"], f, indent=4)
        with open(os.path.join(self.content_dir, "constants.json"), "w") as f:
            json.dump(self.data["constants"], f, indent=4)
        with open(os.path.join(self.content_dir, "entities.json"), "w") as f:
            json.dump(self.data["entities"], f, indent=4)
        
        # 2. Save Topic Shards (Protected)
        for slug, content in self.topic_shards.items():
            path = os.path.join(self.content_dir, "topics", f"{slug}.json")
            if os.path.exists(path) and not unlock_protected:
                # Optional: Compare hashes to see if it actually changed
                with open(path, "r") as f:
                    old_content = f.read()
                if old_content != json.dumps(content, indent=4):
                    print(f"SAFEGUARD: Skipping save for PROTECTED topic shard [{slug}]. Use unlock_protected=True to override.")
                    continue
            
            with open(path, "w") as f:
                json.dump(content, f, indent=4)

        # 3. Save Subtopic Shards
        for shard_name, shard_content in self.shards.items():
            for slug in shard_content:
                if slug in self.data["subtopics"]:
                    shard_content[slug] = self.data["subtopics"][slug]
            
            path = os.path.join(self.content_dir, shard_name)
            with open(path, "w") as f:
                json.dump(shard_content, f, indent=4)

        # 4. Save Global Registry
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
        print(f"SUCCESS: Fully sharded save complete in {self.content_dir}")

        if auto_commit:
            self.commit_to_git(commit_msg)

    def commit_to_git(self, message=None):
        """Automates the git commit for content changes."""
        if not message:
            message = "Great Expansion: Content Update " + subprocess.check_output(["date", "+%Y-%m-%d %H:%M"]).decode().strip()
        
        try:
            print(f"Committing to Git: {message}...")
            # Stage only content and registry
            subprocess.run(["git", "add", "app/config/content/"], check=True)
            subprocess.run(["git", "add", "global_slug_registry.json"], check=True)
            # Commit
            subprocess.run(["git", "commit", "-m", message], capture_output=True)
            print("✓ Git commit successful.")
        except Exception as e:
            print(f"WARNING: Git commit failed: {str(e)}")

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
        if slug in self.data["subtopics"]:
            topic = self.data["subtopics"][slug]
        elif slug in self.data["topic_contents"]:
            topic = self.data["topic_contents"][slug]
        else:
            return None
        
        content = topic["content"]
        original_content = content
        
        # 1. Entity Linking (Historical Figures/Facilities)
        content = self._apply_entity_links(content)

        masked_content, placeholders = self.mask_mathjax(content)
        
        # Performance optimization: get titles for current slug once
        current_titles = [t for t, s in self.registry.items() if s == slug]

        for title in self.sorted_titles:
            target_slug = self.registry[title]
            if target_slug == slug or title in current_titles:
                continue
            
            if target_slug in self.data["topic_contents"]:
                url = f"/physics/topic/{target_slug}"
            else:
                url = f"/physics/subtopic/{target_slug}"

            link_html = f'<a href="{url}" class="subtopic-link"><strong>{title}</strong></a>'
            bold_tag = f"<strong>{title}</strong>"
            
            if bold_tag in masked_content:
                # Avoid nesting if already linked
                if f'>{bold_tag}</a>' in masked_content:
                    continue
                masked_content = masked_content.replace(bold_tag, link_html)
            elif f'href="/physics/subtopic/{target_slug}"' not in masked_content and f'href="/physics/topic/{target_slug}"' not in masked_content:
                plain_pattern = re.compile(rf'(?<![=">])\b{re.escape(title)}\b(?![<])')
                masked_content = plain_pattern.sub(lambda m: link_html, masked_content)
        
        final_content = self.unmask_mathjax(masked_content, placeholders)
        final_content = self._sanitize_mathjax(final_content)
        
        if not dry_run:
            topic["content"] = final_content
            
        return final_content if final_content != original_content else None

    def _apply_entity_links(self, content):
        """Internal helper to link entities from entities.json."""
        for e_id, e_data in self.data.get("entities", {}).items():
            link = e_data["link"]
            # Only link if not already linked to this entity (exact href check)
            if f'href="{link}"' in content: continue
            
            variants = [e_data["name"]] + e_data.get("aliases", [])
            # Sort by length descending to match longest first
            variants.sort(key=len, reverse=True)
            
            for var in variants:
                if len(var) < 3: continue
                # Match name not preceded by > or =
                pattern = re.compile(rf'(?<![=">])\b{re.escape(var)}\b', re.IGNORECASE)
                if pattern.search(content):
                    link_html = f'<a href="{link}" class="subtopic-link"><strong>{var}</strong></a>'
                    content = pattern.sub(lambda m: link_html, content)
                    break # Only link the first match of any variant
        return content

    def _sanitize_mathjax(self, content):
        content = content.replace(" > ", " \\gt ")
        content = content.replace(" < ", " \\lt ")
        return content

    def _validate_slug_and_title(self, slug, title):
        """Centralized check for protected slugs and titles."""
        # 1. Protected Slug Check
        if slug in self.PROTECTED_TOPICS:
            return False, f"Slug [{slug}] is a PROTECTED main topic."
        
        # 2. Title Collision Check (prevent subtopics with titles that are main topics)
        # Normalize title to slug-like form for comparison
        norm_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        if norm_title in self.PROTECTED_TOPICS:
            return False, f"Title '{title}' corresponds to a PROTECTED main topic slug [{norm_title}]."
        
        # 3. Registry Conflict Check (is this title already used for a main topic?)
        if title in self.registry:
            existing_slug = self.registry[title]
            if existing_slug in self.PROTECTED_TOPICS:
                return False, f"Title '{title}' is already assigned to PROTECTED main topic [{existing_slug}]."

        return True, None

    def add_subtopic(self, slug, subtopic_data, link_in_parent=True):
        """Adds subtopic to appropriate shard and updates registry. Prevents duplicates."""
        # Safeguard: Prevent overwriting protected main topics or title collisions
        ok, error = self._validate_slug_and_title(slug, subtopic_data.get("title", ""))
        if not ok:
            print(f"ERROR: {error} Cannot add subtopic.")
            return False

        # 1. Mandatory Global Duplicate Check
        if slug in self.data["subtopics"]:
            existing_shard = self.slug_to_shard.get(slug, "Unknown")
            print(f"WARNING: Slug [{slug}] already exists in {existing_shard}. Merging/Updating instead.")
            shard_file = existing_shard
        else:
            parent_slug = subtopic_data.get("parents", ["misc"])[0]
            shard_file = f"{parent_slug}.json"
            if parent_slug in self.data["subtopics"]:
                shard_file = self.slug_to_shard.get(parent_slug, shard_file)
        
        if shard_file not in self.shards:
            self.shards[shard_file] = {}
        
        self.shards[shard_file][slug] = subtopic_data
        self.data["subtopics"][slug] = subtopic_data
        self.slug_to_shard[slug] = shard_file
        self.registry[subtopic_data["title"]] = slug
        self._refresh_sorted_titles()
        self.apply_auto_links(slug)
        return True

    def update_subtopic(self, slug, subtopic_data):
        """Safely updates an existing subtopic."""
        if slug not in self.data["subtopics"]:
            print(f"ERROR: Subtopic [{slug}] does not exist. Use add_subtopic instead.")
            return False
            
        if slug in self.PROTECTED_TOPICS:
            print(f"ERROR: Cannot update PROTECTED main topic [{slug}] via update_subtopic.")
            return False
            
        # Check if title changed and if new title collides
        new_title = subtopic_data.get("title")
        if new_title:
            ok, error = self._validate_slug_and_title(slug, new_title)
            if not ok:
                print(f"ERROR: {error}")
                return False

        shard_file = self.slug_to_shard[slug]
        self.shards[shard_file][slug] = subtopic_data
        self.data["subtopics"][slug] = subtopic_data
        
        if new_title:
            # Update registry if title changed
            old_title = next((t for t, s in self.registry.items() if s == slug), None)
            if old_title and old_title != new_title:
                del self.registry[old_title]
            self.registry[new_title] = slug
            self._refresh_sorted_titles()
            
        self.apply_auto_links(slug)
        return True

    def delete_subtopic(self, slug):
        """Safely removes a subtopic from its shard and the registry."""
        if slug in self.PROTECTED_TOPICS:
            print(f"ERROR: Cannot delete PROTECTED main topic [{slug}].")
            return False
            
        if slug not in self.data["subtopics"]:
            print(f"ERROR: Subtopic [{slug}] not found.")
            return False
            
        shard_file = self.slug_to_shard.get(slug)
        if shard_file and slug in self.shards.get(shard_file, {}):
            del self.shards[shard_file][slug]
            
        if slug in self.data["subtopics"]:
            del self.data["subtopics"][slug]
            
        title = next((t for t, s in self.registry.items() if s == slug), None)
        if title:
            del self.registry[title]
            
        if slug in self.slug_to_shard:
            del self.slug_to_shard[slug]
            
        self._refresh_sorted_titles()
        print(f"✓ Subtopic [{slug}] deleted from {shard_file}.")
        return True

    def ingest_subtopic_platinum(self, slug, subtopic_data):
        """Atomsically adds a subtopic and its local formulas to the registry, returning final IDs."""
        # 1. Extract and register local formulas
        final_ids = subtopic_data.get("formula_ids", [])
        if "formulas" in subtopic_data:
            for f_obj in subtopic_data["formulas"]:
                f_id = self.add_formula(
                    f_obj.get("title"),
                    f_obj.get("equation"),
                    f_obj.get("interpretation") or f_obj.get("breakdown")
                )
                final_ids.append(f_id)
            del subtopic_data["formulas"]
        
        subtopic_data["formula_ids"] = list(set(final_ids))
        
        # 2. Hand over to standard sharding logic
        return self.add_subtopic(slug, subtopic_data)

    def add_formula(self, title, equation, interpretation):
        """Adds a formula to the registry and returns its ID."""
        slug_title = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        eq_hash = hashlib.md5(equation.encode()).hexdigest()[:8]
        f_id = f"{slug_title}-{eq_hash}"
        
        self.data["formula_registry"][f_id] = {
            "title": title,
            "equation": equation,
            "semantic_variables": {},
            "interpretation": interpretation,
            "symmetry_origin": "Great Expansion: Derivation pending.",
            "limits_and_boundary": "Great Expansion: Boundary analysis pending.",
            "status": "platinum-draft"
        }
        return f_id

    def build(self):
        """Pre-renders all subtopics into static HTML for performance."""
        print("Starting Static Build...")
        output_dir = "public/cache/subtopic"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Use Primary Test Server for build
        success_count = 0
        total = len(self.data["subtopics"])

        for i, slug in enumerate(self.data["subtopics"]):
            sys.stdout.write(f"\rBuilding {i+1}/{total}: {slug}...")
            sys.stdout.flush()

            try:
                url = f"http://localhost/physics/subtopic/{slug}?build_mode=1"
                result = subprocess.run(["curl", "-s", "-L", url], capture_output=True, text=True, timeout=5)
                if result.stdout:
                    with open(os.path.join(output_dir, f"{slug}.html"), "w") as f:
                        f.write(result.stdout)
                    success_count += 1
            except Exception as e:
                print(f"\nERROR building {slug}: {str(e)}")

        print(f"\nSUCCESS: Pre-rendered {success_count} static pages in {output_dir}")

    def validate(self):
        print("Running Integrity Shield...")
        result = subprocess.run(["python3", "integrity_shield.py"], capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0

if __name__ == "__main__":
    orchestrator = PhysicsOrchestrator()
    print(f"Orchestrator ready. {len(orchestrator.data['subtopics'])} subtopics loaded from shards.")
    print(f"Main topics sharded: {len(orchestrator.topic_shards)}")
