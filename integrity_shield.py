import json
import re
import os
import sys

# Attempt to import jsonschema, fallback to basic check if not available
try:
    from jsonschema import Draft7Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

class IntegrityShield:
    def __init__(self, content_dir="app/config/content", schema_path="app/config/subtopic.schema.json", target_slug=None):
        self.content_dir = content_dir
        self.schema_path = schema_path
        self.target_slug = target_slug
        self.errors = []
        self.warnings = []
        self.stats = {"links": 0, "formulas": 0, "topics": 0, "shards": 0}
        self.load_schema()
        self.load_data()

    def load_schema(self):
        if os.path.exists(self.schema_path):
            with open(self.schema_path, "r") as f:
                self.schema = json.load(f)
        else:
            self.schema = None

    def load_data(self):
        search_index_path = os.path.join(self.content_dir, "search_index.json")
        formulas_path = os.path.join(self.content_dir, "formulas.json")
        entities_path = os.path.join(self.content_dir, "entities.json")
        categories_path = os.path.join(self.content_dir, "categories.json")
        
        with open(search_index_path, "r") as f:
            search_index = json.load(f)
        with open(formulas_path, "r") as f:
            self.formula_registry = json.load(f)
        with open(entities_path, "r") as f:
            self.entities = json.load(f)
        with open(categories_path, "r") as f:
            self.topics = json.load(f)
            
        self.target_shard = None
        if self.target_slug:
            entry = search_index.get(self.target_slug)
            if entry and isinstance(entry, dict):
                self.target_shard = entry.get("s")
            elif isinstance(entry, str):
                self.target_shard = entry
            
        if self.target_slug and self.target_shard:
            # OPTIMIZED single-target path
            shard_path = os.path.join(self.content_dir, self.target_shard)
            with open(shard_path, "r") as f:
                shard_data = json.load(f)
            self.all_subtopics = {self.target_slug: shard_data.get(self.target_slug, {})}
            self.all_slugs = set(search_index.keys()).union(set(self.topics.keys()))
            self.stats["topics"] = 1
            self.stats["shards"] = 1
            
            class MockOrchestrator:
                def __init__(self, registry, protected_topics):
                    self.registry = registry
                    self.PROTECTED_TOPICS = protected_topics
            protected_topics = {
                "classical-mechanics", "electromagnetism", "relativity", "quantum-physics",
                "standard-model", "astrophysics", "theoretical-physics", "thermodynamics-statistical-mechanics"
            }
            registry_path = "global_slug_registry.json"
            registry = {}
            if os.path.exists(registry_path):
                with open(registry_path, "r") as f:
                    registry = json.load(f)
            self.orch = MockOrchestrator(registry, protected_topics)
        else:
            # Standard full crawl path
            from orchestrator import PhysicsOrchestrator
            self.orch = PhysicsOrchestrator(content_dir=self.content_dir)
            self.all_subtopics = self.orch.data["subtopics"]
            self.all_slugs = set(self.all_subtopics.keys()).union(set(self.topics.keys()))
            self.stats["topics"] = len(self.all_subtopics)
            self.stats["shards"] = len(self.orch.shards)

        if HAS_JSONSCHEMA and self.schema:
            validator = Draft7Validator(self.schema)
            files_to_validate = [self.target_shard] if self.target_shard else os.listdir(self.content_dir)
            for file in files_to_validate:
                if not file: continue
                if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "entities.json", "search_index.json", "compiled_trie_regex.json"]:
                    path = os.path.join(self.content_dir, file)
                    with open(path, "r") as f:
                        content = json.load(f)
                    for err in validator.iter_errors(content):
                        slug = err.path[0] if err.path else "<root>"
                        if self.target_slug and slug != self.target_slug:
                            continue
                        self.errors.append(f"Schema Violation in {file} :: {slug}: {err.message}")

        if not self.target_slug:
            self.all_slugs = set(self.all_subtopics.keys()).union(set(self.topics.keys()))
            self.stats["topics"] = len(self.all_subtopics)
            self.stats["shards"] = len(self.orch.shards)

    def check_formulas(self):
        subtopics_to_check = [self.target_slug] if self.target_slug else self.all_subtopics.keys()
        for slug in subtopics_to_check:
            sub = self.all_subtopics.get(slug)
            if not sub: continue
            for f_id in sub.get("formula_ids", []):
                self.stats["formulas"] += 1
                if f_id not in self.formula_registry:
                    self.errors.append(f"Broken Formula: [{slug}] refs unknown ID '{f_id}'")
                else:
                    eq = self.formula_registry[f_id].get("equation", "")
                    if "merror" in eq or "mjx-error" in eq or "math-error" in eq or re.search(r'(fill|stroke)=[\\"\']?red[\\"\']?', eq):
                        self.errors.append(
                            f"MathJax Rendering Error: [{slug}] refs formula '{f_id}' "
                            f"which contains MathJax compilation errors (red-text markup or math-error)."
                        )

    def check_duplicates(self):
        """Ensures every subtopic slug exists in exactly one shard and no protected slugs in subtopic shards."""
        slug_map = {}
        protected_topics = self.orch.PROTECTED_TOPICS

        for file in os.listdir(self.content_dir):
            if not file.endswith(".json") or file in ["categories.json", "formulas.json", "constants.json", "entities.json", "search_index.json", "compiled_trie_regex.json"]:
                continue

            # Skip the topics directory as it's handled separately or contains the protected ones
            if "topics/" in file: continue 

            path = os.path.join(self.content_dir, file)
            with open(path, "r") as f:
                shard_content = json.load(f)
                if self.target_slug:
                    if self.target_slug in shard_content:
                        if self.target_slug in protected_topics:
                            self.errors.append(f"PROTECTED SLUG VIOLATION: [{self.target_slug}] found in subtopic shard {file}")
                        if self.target_slug in slug_map:
                            self.errors.append(f"CRITICAL DUPLICATE: [{self.target_slug}] exists in both {slug_map[self.target_slug]} and {file}")
                        slug_map[self.target_slug] = file
                else:
                    for slug in shard_content:
                        if slug in protected_topics:
                            self.errors.append(f"PROTECTED SLUG VIOLATION: [{slug}] found in subtopic shard {file}")

                        if slug in slug_map:
                            self.errors.append(f"CRITICAL DUPLICATE: [{slug}] exists in both {slug_map[slug]} and {file}")
                        slug_map[slug] = file

    def check_technical_density(self):
        tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
        subtopics_to_check = [self.target_slug] if self.target_slug else self.all_subtopics.keys()
        for slug in subtopics_to_check:
            sub = self.all_subtopics.get(slug)
            if not sub or "content" not in sub: continue
            content = sub["content"]
            content_no_svg = re.sub(r'<svg.*?</svg>', '', content, flags=re.DOTALL)
            latex_count = len(re.findall(r'\\\(|\\\[', content)) + content.count("<svg")
            term_score = sum(5 for term in tech_terms if term in content_no_svg.lower())
            words = len(re.findall(r'\w+', content_no_svg))
            total_score = (latex_count * 15) + term_score
            if words < 500:
                self.warnings.append(f"Low Depth: [{slug}] word count too low ({words}).")
            if total_score < 30:
                self.warnings.append(f"Non-Technical: [{slug}] density too low (Score: {total_score}).")

    def check_entities(self):
        """Finds entity names in text that are NOT yet linked."""
        subtopics_to_check = [self.target_slug] if self.target_slug else self.all_subtopics.keys()
        for e_id, e_data in self.entities.items():
            name = e_data["name"]
            # Match name not preceded by > or = and not followed by <
            pattern = re.compile(rf'(?<![=">])\b{re.escape(name)}\b(?![<])')
            for slug in subtopics_to_check:
                sub = self.all_subtopics.get(slug)
                if not sub or "content" not in sub: continue
                if pattern.search(sub["content"]):
                    self.warnings.append(f"Unlinked Entity: [{slug}] mentions '{name}'. Auto-link recommended.")

    def check_registry(self):
        """Ensures all protected topics are pinned in the registry."""
        if self.target_slug and self.target_slug not in self.orch.PROTECTED_TOPICS:
            return
        registry_reverse = {v: k for k, v in self.orch.registry.items()}
        for slug in self.orch.PROTECTED_TOPICS:
            if self.target_slug and slug != self.target_slug:
                continue
            if slug not in registry_reverse:
                self.errors.append(f"REGISTRY MISSING: Protected topic [{slug}] not found in global registry.")

    def check_links(self):
        link_pattern = re.compile(r'href=[\\"]+/physics/(subtopic|topic)/([^\\"]+)[\\"]+')
        def scan(text, source):
            matches = link_pattern.findall(text)
            for _, target in matches:
                self.stats["links"] += 1
                if target not in self.all_slugs:
                    self.errors.append(f"Broken Link: [{source}] -> '{target}'")

        if self.target_slug:
            sub = self.all_subtopics.get(self.target_slug)
            if sub and "content" in sub:
                scan(sub["content"], self.target_slug)
            topic = self.topics.get(self.target_slug)
            if topic and "content" in topic:
                scan(topic["content"], self.target_slug)
        else:
            for slug, sub in self.all_subtopics.items():
                if "content" in sub:
                    scan(sub["content"], slug)
            for slug, topic in self.topics.items():
                if "content" in topic:
                    scan(topic["content"], slug)

    def check_latex_formatting(self):
        """Ensures Platinum subtopics do not contain raw LaTeX delimiters."""
        subtopics_to_check = [self.target_slug] if self.target_slug else self.all_subtopics.keys()
        for slug in subtopics_to_check:
            sub = self.all_subtopics.get(slug)
            if not sub: continue
            if sub.get("standard") == "platinum":
                content = sub.get("content", "")
                # Pattern for \( or \[ or \) or \]
                if re.search(r'\\{1,2}\[|\\{1,2}\(|\\{1,2}\]|\\{1,2}\)', content):
                    self.errors.append(f"SSR VIOLATION: [{slug}] is Platinum but contains raw LaTeX delimiters. Pre-rendering required.")

    def run(self):
        print(f"\n\033[1m=== INTEGRITY SHIELD (SHARDED) ===\033[0m")
        print(f"Directory: {self.content_dir}")
        if self.target_slug:
            print(f"Status: Targeted audit on slug '{self.target_slug}' in shard '{self.target_shard}'")
        else:
            print(f"Status: {self.stats['shards']} shards, {self.stats['topics']} topics.")
        
        self.check_duplicates()
        self.check_formulas()
        self.check_registry()
        self.check_technical_density()
        self.check_entities()
        self.check_links()
        self.check_latex_formatting()
        
        print(f"Stats:  {self.stats['links']} links, {self.stats['formulas']} formula refs.")
        
        if not HAS_JSONSCHEMA:
            print("\033[93mNOTE: 'jsonschema' library not found. Skipping structural validation.\033[0m")

        if self.errors:
            print(f"\n\033[91mERRORS FOUND ({len(self.errors)}):\033[0m")
            for err in self.errors[:15]:
                print(f"  - {err}")
            if len(self.errors) > 15:
                print(f"  ... and {len(self.errors)-15} more.")
            return False
        
        if self.warnings:
            print(f"\n\033[93mWARNINGS ({len(self.warnings)}):\033[0m")
            for warn in self.warnings[:5]:
                print(f"  - {warn}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings)-5} more.")

        print("\n\033[92m✓ SHIELD SECURE: All shards are valid and linked.\033[0m")
        return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    shield = IntegrityShield(target_slug=target)
    success = shield.run()
    sys.exit(0 if success else 1)
