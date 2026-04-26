import json
import re
import os
import sys
import subprocess
from orchestrator import PhysicsOrchestrator

class RefactorEngine:
    def __init__(self):
        self.orch = PhysicsOrchestrator()
        self.tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]

    def score_topic(self, content):
        if not content: return 0
        latex_count = len(re.findall(r'\\\(|\\\[', content))
        term_score = sum(5 for term in self.tech_terms if term in content.lower())
        sections = len(re.findall(r'<h3>', content))
        section_penalty = 0
        if sections < 6:
            section_penalty = (6 - sections) * 20
        return max(0, (latex_count * 15) + term_score - section_penalty)

    def get_lowest_density_targets(self, limit=10):
        scores = []
        for slug, sub in self.orch.data["subtopics"].items():
            score = self.score_topic(sub.get("content", ""))
            scores.append((slug, score))
        scores.sort(key=lambda x: x[1])
        return [s[0] for s in scores[:limit]]

    def generate_research_brief(self, slugs):
        brief = {"instruction": "Upgrade to Platinum Standard.", "targets": {}}
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

    def finalize_ingestion(self, json_path):
        with open(json_path, 'r') as f:
            s = f.read()

        def replacer(match):
            g = match.group(0)
            if g[1] in 'nrtbf\\"': return g
            return '\\\\' + g[1]
        
        fixed_s = re.sub(r'\\.', replacer, s, flags=re.DOTALL)
        
        try:
            data = json.loads(fixed_s)
            slugs = list(data.keys())
            
            # Get valid slugs to prevent broken links
            valid_slugs = set(self.orch.registry.values())
            valid_slugs.update(self.orch.data.get("search_index", {}).keys())
            
            for slug, sub_data in data.items():
                if "formulas" in sub_data:
                    for f_obj in sub_data["formulas"]:
                        if not f_obj.get("title"):
                            f_obj["title"] = f_obj.get("id") or f"Equation for {slug}"
                            
                # Auto-strip hallucinated links
                if "content" in sub_data:
                    content = sub_data["content"]
                    pattern = re.compile(r'<a href="/physics/subtopic/([^"]+)"[^>]*>(.*?)</a>')
                    def link_replacer(match):
                        target = match.group(1)
                        if target in valid_slugs or target in slugs:
                            return match.group(0)
                        else:
                            print(f"  [Auto-Correction] Stripping hallucinated link: {target}")
                            return match.group(2)
                    sub_data["content"] = pattern.sub(link_replacer, content)

                # Auto-strip hallucinated formula IDs
                if "formula_ids" in sub_data:
                    valid_formulas = set(self.orch.data.get("formula_registry", {}).keys())
                    filtered_f_ids = []
                    for f_id in sub_data["formula_ids"]:
                        if f_id in valid_formulas:
                            filtered_f_ids.append(f_id)
                        else:
                            print(f"  [Auto-Correction] Stripping hallucinated formula ID: {f_id}")
                    sub_data["formula_ids"] = filtered_f_ids

                self.orch.ingest_subtopic_platinum(slug, sub_data)
            
            self.orch.save(auto_commit=True, commit_msg=f"RefactorEngine: Automated upgrade for {len(data)} topics.")
            self.trigger_sync()
            self.orch.build_selective(slugs)

            # --- POST-INGESTION SAFETY GATE ---
            if not self.validate_integrity():
                self.rollback()
                return False
            
            print("\033[92m✓ Batch verified and live.\033[0m")
            return True
        except Exception as e:
            print(f"Ingestion Failed: {e}")
            return False

if __name__ == "__main__":
    engine = RefactorEngine()
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        engine.finalize_ingestion(sys.argv[2])
    else:
        targets = engine.get_lowest_density_targets(10)
        print(json.dumps(engine.generate_research_brief(targets), indent=2))
