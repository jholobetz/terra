import json
import re
import os
import subprocess
import shutil
import hashlib
import sys

class PhysicsOrchestrator:
    def __init__(self, content_dir="app/config/content", registry_path="global_slug_registry.json"):
        self.content_dir = content_dir
        self.registry_path = registry_path
        self.shards = {}
        self.data = {
            "topics": {},
            "subtopics": {},
            "formula_registry": {},
            "constants": {},
            "entities": {}
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
                elif file == "entities.json":
                    self.data["entities"] = content
                elif file == "search_index.json":
                    self.data["search_index"] = content
                else:
                    # Subtopic shard
                    self.shards[file] = content
                    for slug in content:
                        self.data["subtopics"][slug] = content[slug]
                        self.slug_to_shard[slug] = file

    def _refresh_sorted_titles(self):
        self.sorted_titles = sorted(self.registry.keys(), key=len, reverse=True)

    def save(self, auto_commit=True, commit_msg=None):
        """Saves all modified shards and registries and optionally commits to Git."""
        # 1. Save Registries/Categories
        with open(os.path.join(self.content_dir, "categories.json"), "w") as f:
            json.dump(self.data["topics"], f, indent=4)
        with open(os.path.join(self.content_dir, "formulas.json"), "w") as f:
            json.dump(self.data["formula_registry"], f, indent=4)
        with open(os.path.join(self.content_dir, "constants.json"), "w") as f:
            json.dump(self.data["constants"], f, indent=4)
        with open(os.path.join(self.content_dir, "entities.json"), "w") as f:
            json.dump(self.data["entities"], f, indent=4)
        
        # 2. Save Subtopic Shards
        for shard_name, shard_content in self.shards.items():
            for slug in shard_content:
                if slug in self.data["subtopics"]:
                    shard_content[slug] = self.data["subtopics"][slug]
            
            with open(os.path.join(self.content_dir, shard_name), "w") as f:
                json.dump(shard_content, f, indent=4)

        # 3. Save Global Registry
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=4)
            
        print(f"SUCCESS: Sharded save complete in {self.content_dir}")

        if auto_commit:
            self.commit_to_git(commit_msg)

    def commit_to_git(self, message=None):
        """Automates the git commit for content changes."""
        if not message:
            message = "Great Expansion: Content Update " + subprocess.check_output(["date", "+%Y-%m-%d %H:%M"]).decode().strip()
        
        try:
            print(f"Committing to Git: {message}...")
            # Stage only content and registry
            subprocess.run(["git", "add", "app/config/content/*.json"], check=True)
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
        if slug not in self.data["subtopics"]:
            return None
        
        topic = self.data["subtopics"][slug]
        content = topic["content"]
        original_content = content
        
        # 1. Entity Linking
        content = self._apply_entity_links(content)

        # 2. Mask MathJax AND existing links to prevent corruption
        masked_content, mj_placeholders = self.mask_mathjax(content)
        
        # Mask COMPLETE <a> tags first
        link_placeholders = {}
        link_count = 0
        def link_masker(match):
            nonlocal link_count
            ph = f"##L_MASK_{link_count}##"
            link_placeholders[ph] = match.group(0)
            link_count += 1
            return ph
        
        masked_content = re.sub(r"<a\s+[^>]*>.*?</a>", link_masker, masked_content, flags=re.DOTALL)
        
        # Mask remaining HTML tags (strong, p, etc.)
        tag_placeholders = {}
        tag_count = 0
        def tag_masker(match):
            nonlocal tag_count
            ph = f"##T_MASK_{tag_count}##"
            tag_placeholders[ph] = match.group(0)
            tag_count += 1
            return ph
        
        masked_content = re.sub(r"<[^>]+>", tag_masker, masked_content)
        
        # 3. Single-pass title replacement
        current_titles = [t for t, s in self.registry.items() if s == slug]
        valid_titles = [t for t in self.sorted_titles if self.registry[t] != slug and t not in current_titles]
        
        if valid_titles:
            pattern_str = "\b(" + "|".join(re.escape(t) for t in valid_titles) + ")\b"
            title_pattern = re.compile(pattern_str)
            
            def title_replacer(match):
                title = match.group(0)
                target_slug = self.registry[title]
                # Return as a link that we mask immediately
                nonlocal link_count
                ph = f"##L_MASK_{link_count}##"
                link_placeholders[ph] = f"<a href="/physics/subtopic/{target_slug}" class="subtopic-link"><strong>{title}</strong></a>"
                link_count += 1
                return ph

            masked_content = title_pattern.sub(title_replacer, masked_content)
        
        # 4. Unmask EVERYTHING
        for ph, original in tag_placeholders.items():
            masked_content = masked_content.replace(ph, original)
        for ph, original in link_placeholders.items():
            masked_content = masked_content.replace(ph, original)

        final_content = self.unmask_mathjax(masked_content, mj_placeholders)
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

    def add_subtopic(self, slug, subtopic_data, link_in_parent=True):
        """Adds subtopic to appropriate shard and updates registry. Prevents duplicates."""
        # 0. Protected Slug Check (Main Topics)
        if slug in self.data["topics"]:
            raise Exception(f"CRITICAL: Attempted to overwrite Protected Main Topic: [{slug}]. Operation denied.")

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

    def get_server_url(self):
        """Extracts the primary test server URL from GEMINI.md."""
        gemini_path = ".gemini/GEMINI.md"
        if os.path.exists(gemini_path):
            with open(gemini_path, "r") as f:
                match = re.search(r"Primary Test Server:.*`(http[^`]+)`", f.read())
                if match:
                    return match.group(1).rstrip("/")
        return "http://localhost" # Fallback

    def build_selective(self, slugs):
        """Pre-renders specific subtopics into static HTML."""
        print(f"Starting Selective Build for {len(slugs)} topics...")
        output_dir = "public/cache/subtopic"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_url = self.get_server_url()
        print(f"Targeting Server: {base_url}")
        success_count = 0
        
        for slug in slugs:
            sys.stdout.write(f"  -> Rendering {slug}...")
            sys.stdout.flush()
            try:
                url = f"{base_url}/physics/subtopic/{slug}?preview=0"
                result = subprocess.run(["curl", "-s", "-L", url], capture_output=True, text=True, timeout=15)
                if result.stdout:
                    with open(os.path.join(output_dir, f"{slug}.html"), "w") as f:
                        f.write(result.stdout)
                    success_count += 1
                print(" Done.")
            except Exception as e:
                print(f" FAILED: {str(e)}")
        
        print(f"SUCCESS: Pre-rendered {success_count} static pages.")

    def build(self):
        """Pre-renders all indexed topics into static HTML."""
        print("Starting Full Static Build...")
        output_dir = "public/cache/subtopic"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        base_url = self.get_server_url()
        print(f"Targeting Server: {base_url}")
        
        success_count = 0
        total = len(self.data["search_index"])
        
        for i, slug in enumerate(self.data["search_index"]):
            sys.stdout.write(f"\rBuilding {i+1}/{total}: {slug}...")
            sys.stdout.flush()
            
            try:
                url = f"{base_url}/physics/subtopic/{slug}?preview=0"
                result = subprocess.run(["curl", "-s", "-L", url], capture_output=True, text=True, timeout=10)
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
