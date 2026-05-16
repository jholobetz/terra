import json
import os
import re
import subprocess
from orchestrator import PhysicsOrchestrator
from pack_context import ContextPacker

class ExpansionAssemblyLine:
    """
    Orchestrates the 'Great Expansion' and 'Platinum Refactoring' workflows.
    Automates context packing, sub-agent briefing, and atomic ingestion.
    """
    def __init__(self):
        self.orch = PhysicsOrchestrator()
        self.packer = ContextPacker()
        self.backlog_path = "subfiles/expansion_backlog.json"
        self.checkpoint_path = "subfiles/sprint_checkpoint.json"
        
    def load_checkpoint(self):
        if os.path.exists(self.checkpoint_path):
            with open(self.checkpoint_path, "r") as f:
                return json.load(f)
        return {"session_id": None, "topics": {}}

    def save_checkpoint(self, data):
        with open(self.checkpoint_path, "w") as f:
            json.dump(data, f, indent=4)

    def prepare_sprint(self, slugs):
        """Initializes a new sprint session in the checkpoint file."""
        checkpoint = {
            "session_id": os.urandom(4).hex(),
            "topics": {slug: {"status": "PENDING", "errors": [], "content": None} for slug in slugs}
        }
        self.save_checkpoint(checkpoint)
        print(f"SPRINT INITIALIZED: Session {checkpoint['session_id']} for {len(slugs)} topics.")
        return checkpoint

    def update_topic_state(self, slug, status, content=None, errors=None):
        """Updates the state of a specific topic in the checkpoint."""
        checkpoint = self.load_checkpoint()
        if slug in checkpoint["topics"]:
            checkpoint["topics"][slug]["status"] = status
            if content: checkpoint["topics"][slug]["content"] = content
            if errors: checkpoint["topics"][slug]["errors"] = errors
            self.save_checkpoint(checkpoint)

    def identify_refactor_candidates(self, limit=5):
        """Finds 'Legacy' topics that fall below the Platinum Standard."""
        candidates = []
        for slug, sub in self.orch.data["subtopics"].items():
            if sub.get("standard") != "platinum":
                # Calculate word count to prioritize the thinnest
                text = re.sub(r'<.*?>', '', sub.get("content", ""))
                words = len(text.split())
                candidates.append({"slug": slug, "words": words, "parent": sub.get("parents", ["misc"])[0]})
        
        # Sort by thinnest first
        candidates.sort(key=lambda x: x["words"])
        return candidates[:limit]

    def generate_expansion_briefs(self, terms_with_parents):
        """
        Generates a batch of high-context briefs for sub-agents.
        terms_with_parents: list of (term, parent_slug)
        """
        briefs = {}
        for term, parent in terms_with_parents:
            brief = self.packer.pack_brief(term, parent)
            briefs[term] = brief
        return briefs

    def check_expansion_gate(self):
        """Enforces the '10% Expansion Gate' mandate from GEMINI.md."""
        total = len(self.orch.data["subtopics"])
        legacy = sum(1 for sub in self.orch.data["subtopics"].values() if sub.get("standard") != "platinum")
        legacy_ratio = legacy / total if total > 0 else 0
        
        print(f"EXPANSION GATE: {legacy_ratio:.1%} legacy topics ({legacy}/{total}).")
        if legacy_ratio > 0.10:
            print("GATE CLOSED: Non-Platinum topics exceed 10%. Prioritize REFACTORING over expansion.")
            return False
        print("GATE OPEN: System meets technical density targets.")
        return True

    def generate_correction_brief(self, slug, content, errors):
        """Generates a targeted brief to fix validation errors in a draft."""
        error_list = "\n".join([f"- {e}" for e in errors])
        brief = f"""# CORRECTION BRIEF: {slug}
Your previous submission for "{slug}" was REJECTED by the automated Platinum Validator.

## 1. Validation Errors
You MUST fix the following issues:
{error_list}

## 2. Original Content (for reference)
---
{content}
---

## 3. Mandatory Instructions
- Re-write the content to resolve ALL errors listed above.
- Maintain the Platinum Standard (650+ words, organic prose, 5+ links).
- Do NOT use numbered headers.
- Do NOT use forbidden phrases.
- Return ONLY the updated JSON for this slug.
"""
        return brief

    def run_pillar_sprint(self, sprint_data, is_expansion=True):
        """
        Executes an ingestion of a batch of Platinum-grade topics with Partial Acceptance.
        Returns (successful_slugs, failed_slugs_with_errors)
        """
        if is_expansion and not self.check_expansion_gate():
            return [], {}
            
        print(f"COMMENCING PILLAR SPRINT: {len(sprint_data)} topics.")
        
        # 1. Formula Registration Loop
        for slug, data in sprint_data.items():
            if "formulas" in data:
                final_ids = data.get("formula_ids", [])
                for f_obj in data["formulas"]:
                    f_id = self.orch.add_formula(
                        f_obj["title"],
                        f_obj["equation"],
                        f_obj.get("interpretation", "Derivation pending.")
                    )
                    final_ids.append(f_id)
                data["formula_ids"] = list(set(final_ids))
                del data["formulas"]

        # 2. Ingestion with Partial Acceptance
        successful_slugs, failed_slugs = self.orch.execute_sprint(sprint_data)
        
        if successful_slugs:
            print(f"PILLAR SPRINT UPDATE: Synced {len(successful_slugs)} topics.")
            for slug in successful_slugs:
                self.update_topic_state(slug, "COMPLETED")
            # Sync to DB
            subprocess.run(["php", "cli_sync.php"], capture_output=True)
            
        if failed_slugs:
            print(f"PILLAR SPRINT WARNING: {len(failed_slugs)} topics rejected.")
            for slug, errors in failed_slugs.items():
                self.update_topic_state(slug, "REJECTED", errors=errors)
            
        return successful_slugs, failed_slugs

    def get_backlog_batch(self, limit=5):
        """Pops a batch of terms from the expansion backlog."""
        if not os.path.exists(self.backlog_path):
            return []
            
        with open(self.backlog_path, "r") as f:
            backlog = json.load(f)
            
        batch = backlog[:limit]
        # We don't remove them yet; that happens after successful ingestion
        return batch

if __name__ == "__main__":
    line = ExpansionAssemblyLine()
    print("Assembly Line initialized.")
    candidates = line.identify_refactor_candidates(3)
    print(f"Top Refactor Candidates: {json.dumps(candidates, indent=2)}")
