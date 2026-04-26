import json
import re
import os
import sys

# Attempt to import jsonschema, fallback to basic check if not available
try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

class IntegrityShield:
    def __init__(self, content_dir="app/config/content", schema_path="app/config/subtopic.schema.json"):
        self.content_dir = content_dir
        self.schema_path = schema_path
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
        self.all_subtopics = {}
        self.formula_registry = {}
        self.entities = {}
        self.topics = {}
        
        if not os.path.exists(self.content_dir):
            return

        for file in os.listdir(self.content_dir):
            if not file.endswith(".json"): continue
            path = os.path.join(self.content_dir, file)
            
            with open(path, "r") as f:
                content = json.load(f)
            
            if file == "categories.json":
                self.topics = content
            elif file == "formulas.json":
                self.formula_registry = content
            elif file == "entities.json":
                self.entities = content
            elif file == "constants.json":
                pass
            elif file == "search_index.json":
                pass
            else:
                # Subtopic shard
                self.stats["shards"] += 1
                self.all_subtopics.update(content)
                # SCHEMA VALIDATION
                if HAS_JSONSCHEMA and self.schema:
                    try:
                        validate(instance=content, schema=self.schema)
                    except ValidationError as e:
                        self.errors.append(f"Schema Violation in {file}: {e.message}")

        self.all_slugs = set(self.all_subtopics.keys()).union(set(self.topics.keys()))
        self.stats["topics"] = len(self.all_subtopics)

    def check_formulas(self):
        for slug, sub in self.all_subtopics.items():
            for f_id in sub.get("formula_ids", []):
                self.stats["formulas"] += 1
                if f_id not in self.formula_registry:
                    self.errors.append(f"Broken Formula: [{slug}] refs unknown ID '{f_id}'")

    def check_technical_density(self):
        tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
        for slug, sub in self.all_subtopics.items():
            if "content" not in sub: continue
            content = sub["content"]
            latex_count = len(re.findall(r'\\\(|\\\[', content))
            term_score = sum(5 for term in tech_terms if term in content.lower())
            words = len(re.findall(r'\w+', content))
            total_score = (latex_count * 15) + term_score
            if words < 200:
                self.warnings.append(f"Low Depth: [{slug}] word count too low ({words}).")
            if total_score < 20:
                self.warnings.append(f"Non-Technical: [{slug}] density too low (Score: {total_score}).")

    def check_entities(self):
        """Finds entity names in text that are NOT yet linked."""
        for e_id, e_data in self.entities.items():
            name = e_data["name"]
            # Match name not preceded by > or = and not followed by <
            pattern = re.compile(rf'(?<![=">])\b{re.escape(name)}\b(?![<])')
            for slug, sub in self.all_subtopics.items():
                if "content" in sub and pattern.search(sub["content"]):
                    self.warnings.append(f"Unlinked Entity: [{slug}] mentions '{name}'. Auto-link recommended.")

    def check_links(self):
        link_pattern = re.compile(r'href=[\\"]+/physics/(subtopic|topic)/([^\\"]+)[\\"]+')
        def scan(text, source):
            matches = link_pattern.findall(text)
            for _, target in matches:
                self.stats["links"] += 1
                if target not in self.all_slugs:
                    self.errors.append(f"Broken Link: [{source}] -> '{target}'")

        for slug, sub in self.all_subtopics.items():
            if "content" in sub:
                scan(sub["content"], slug)
        for slug, topic in self.topics.items():
            if "content" in topic:
                scan(topic["content"], slug)

    def run(self):
        print(f"\n\033[1m=== INTEGRITY SHIELD (SHARDED) ===\033[0m")
        print(f"Directory: {self.content_dir}")
        print(f"Status: {self.stats['shards']} shards, {self.stats['topics']} topics.")
        
        self.check_formulas()
        self.check_technical_density()
        self.check_entities()
        self.check_links()
        
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
    shield = IntegrityShield()
    success = shield.run()
    sys.exit(0 if success else 1)
