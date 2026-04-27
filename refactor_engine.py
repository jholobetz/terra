import json
import re
import os
import sys
import subprocess
import hashlib
from orchestrator import PhysicsOrchestrator

class RefactorEngine:
    def __init__(self):
        self.orch = PhysicsOrchestrator()
        self.tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]

    def score_topic(self, content):
        if not content: return 0
        # 1. LaTeX Density (Weight: 15 per instance)
        latex_count = len(re.findall(r'\\\(|\\\[', content))
        
        # 2. Technical Keyword Depth (Weight: 5 per term)
        term_score = sum(5 for term in self.tech_terms if term in content.lower())
        
        # 3. Section Depth (Platinum: 4 to 8 sections)
        sections = len(re.findall(r'<h3>', content))
        section_penalty = 0
        if sections < 4:
            section_penalty = (4 - sections) * 25
        elif sections > 8:
            section_penalty = (sections - 8) * 10 
        
        # 4. Word Count (The "Thinness" Guard)
        text_only = re.sub(r'<[^>]+>', '', content)
        words = len(re.findall(r'\w+', text_only))
        word_penalty = 0
        if words < 500:
            word_penalty = (500 - words) // 2 
        
        return max(0, (latex_count * 15) + term_score - section_penalty - word_penalty)

    def get_lowest_density_targets(self, limit=10):
        scores = []
        for slug, sub in self.orch.data["subtopics"].items():
            score = self.score_topic(sub.get("content", ""))
            scores.append((slug, score))
        scores.sort(key=lambda x: x[1])
        return [s[0] for s in scores[:limit]]

    def get_surgical_grounding(self, targets):
        """Builds a highly relevant grounding list based on target parents."""
        relevant_slugs = set(targets)
        for slug in targets:
            sub = self.orch.data["subtopics"].get(slug, {})
            parents = sub.get("parents", [])
            relevant_slugs.update(parents)
            for other_slug, other_data in self.orch.data["subtopics"].items():
                if any(p in other_data.get("parents", []) for p in parents):
                    relevant_slugs.add(other_slug)
                if len(relevant_slugs) > 300: break
        
        return list(relevant_slugs)[:300]

    def generate_research_brief(self, slugs):
        grounding = self.get_surgical_grounding(slugs)
        brief = {
            "instruction": "Upgrade to Platinum Standard (4-8 sections, >800 words, university-level depth).",
            "hallucination_control": "STRICT MINIMIZE HALLUCINATIONS. ONLY link to the provided grounding slugs.",
            "targets": {},
            "grounding_data": {
                "authorized_slugs": grounding,
                "mandatory_formulas": "Define ALL new equations in the 'formulas' array."
            }
        }
        for slug in slugs:
            sub = self.orch.data["subtopics"][slug]
            brief["targets"][slug] = {
                "title": sub["title"],
                "existing_links": re.findall(r'href="([^"]+)"', sub.get("content", "")),
                "parents": sub.get("parents", [])
            }
        return brief

    def trigger_sync(self):
        base_url = self.orch.get_server_url()
        sync_url = f"{base_url}/physics/sync"
        print(f"Triggering Database Sync: {sync_url}")
        subprocess.run(["curl", "-s", "-L", sync_url], capture_output=True, timeout=15)

    def rollback(self):
        """Reverts the last commit and re-syncs the database."""
        print("\033[91mCRITICAL ERROR DETECTED. INITIATING ROLLBACK...\033[0m")
        subprocess.run(["git", "reset", "--hard", "HEAD~1"])
        self.trigger_sync()
        print("\033[92mRollback complete. System restored to previous known-good state.\033[0m")

    def validate_integrity(self):
        """Runs integrity shield and returns True if clean (no errors)."""
        print("Validating batch integrity...")
        result = subprocess.run(["python3", "integrity_shield.py"], capture_output=True, text=True)
        if "ERRORS FOUND" in result.stdout:
            print(result.stdout)
            return False
        return True

    def clear_cache_for_slugs(self, slugs):
        """Removes static HTML cache files for the given slugs."""
        cache_dir = "public/cache/subtopic"
        for slug in slugs:
            cache_file = os.path.join(cache_dir, f"{slug}.html")
            if os.path.exists(cache_file):
                print(f"Clearing cache for {slug}...")
                os.remove(cache_file)

    def sanitize_payload(self, data):
        """Autonomous Sanitization: Fixes field names and formatting drifts."""
        sanitized = {}
        valid_slugs = set(self.orch.registry.values())
        valid_slugs.update(self.orch.data.get("search_index", {}).keys())
        valid_slugs.update(self.orch.data.get("topics", {}).keys()) # Include main topics
        all_batch_slugs = set(data.keys())

        for slug, sub_data in data.items():
            if "formulas" in sub_data:
                for f_obj in sub_data["formulas"]:
                    if "latex" in f_obj and "equation" not in f_obj:
                        f_obj["equation"] = f_obj["latex"]
                    if "interpretation" in f_obj and "breakdown" not in f_obj:
                        f_obj["breakdown"] = f_obj["interpretation"]
                    if not f_obj.get("title"):
                        f_obj["title"] = f"Identity for {slug}"
                    if not f_obj.get("breakdown"):
                        f_obj["breakdown"] = "Fulsome technical derivation."

            if "content" in sub_data:
                content = sub_data["content"]
                content = re.sub(r'^Here is the upgraded content:|^Sure, here is the JSON:|^File written\.', '', content, flags=re.IGNORECASE).strip()
                
                # Robust Link Auto-Correction
                # Use a non-greedy attribute match but stop at tag end
                link_pattern = re.compile(r'<a\s+href=[\\\"\'/]+physics/(subtopic|topic)/([^\\\"\' >]+)[\\\"\' ]+[^>]*>(.*?)</a>')
                
                def link_replacer(match):
                    l_type = match.group(1)
                    target = match.group(2)
                    inner_text = match.group(3)
                    
                    if target in valid_slugs or target in all_batch_slugs:
                        return match.group(0)
                    else:
                        print(f"  [Auto-Sanitize] Stripping hallucinated link: {target}")
                        return inner_text
                
                sub_data["content"] = link_pattern.sub(link_replacer, content)

            if "formula_ids" in sub_data:
                valid_formulas = set(self.orch.data.get("formula_registry", {}).keys())
                sub_data["formula_ids"] = [f for f in sub_data["formula_ids"] if f in valid_formulas]

            sanitized[slug] = sub_data
        return sanitized

    def finalize_ingestion(self, json_path):
        with open(json_path, 'r') as f:
            s = f.read()

        def replacer(match):
            g = match.group(0)
            if g[1] in 'nrtbf\\"': return g
            return '\\\\' + g[1]
        fixed_s = re.sub(r'\\.', replacer, s, flags=re.DOTALL)
        
        try:
            raw_data = json.loads(fixed_s)
            data = self.sanitize_payload(raw_data)
            slugs = list(data.keys())
            
            for slug, sub_data in data.items():
                self.orch.ingest_subtopic_platinum(slug, sub_data)
            
            self.orch.save(auto_commit=True, commit_msg=f"RefactorEngine: Platinum Alignment Pass for {len(data)} topics.")
            self.trigger_sync()
            self.clear_cache_for_slugs(slugs)
            self.orch.build_selective(slugs)

            if not self.validate_integrity():
                self.rollback()
                return False
            
            print("\033[92m✓ Batch verified and live.\033[0m")
            return True
        except Exception as e:
            print(f"Ingestion Failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    engine = RefactorEngine()
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        engine.finalize_ingestion(sys.argv[2])
    else:
        targets = engine.get_lowest_density_targets(10)
        print(json.dumps(engine.generate_research_brief(targets), indent=2))
