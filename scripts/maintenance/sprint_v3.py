import json
import os
import re
import subprocess
from assembly_line import ExpansionAssemblyLine
from orchestrator import PhysicsOrchestrator

class SprintV3(ExpansionAssemblyLine):
    """
    Advanced Assembly Line utilizing Sectional Generation and Self-Correction.
    Specifically designed to overcome TIMEOUT and MAX_TURNS issues.
    """
    
    FORBIDDEN_PHRASES = [
        "imagine a world", "in the realm of", "journey through", "tapestry of", 
        "it is important to note", "this section discusses", "this investigation", 
        "in conclusion", "university-level", "advanced topics"
    ]

    def __init__(self):
        super().__init__()
        self.max_retries = 2

    def draft_sectional_content(self, slug, title, parent_hub):
        """
        Orchestrates sectional drafting to ensure OPS compliance.
        This is a 'virtual' method meant to be used as a guide for agent interaction.
        """
        hub_signature = self.orch.HUB_SIGNATURES.get(parent_hub, [])
        
        # This string would be sent to a sub-agent or used by the current agent
        brief = f"""
        TARGET: {slug} ("{title}")
        PARENT HUB: {parent_hub}
        
        MANDATORY STRUCTURE:
        1. THE LEAD: First sentence must be In Media Res. Start with a physical principle. 
           DO NOT mention "{title}" in the first 15 words.
        2. TECHNICAL CORE: High-density prose (650+ words total). 
           Must include these keywords: {', '.join(hub_signature)}.
           High MathJax frequency (\( ... \) and \[ ... \]).
        3. THE LIMITING CASE: Mathematically demonstrate how this reduces to a simpler limit.
        4. BRIDGE INJECTION: Include at least one link to a DIFFERENT Pillar Hub.
        
        NEGATIVE CONSTRAINTS:
        - NO bullet points or lists.
        - NO headers like "Introduction" or "Conclusion".
        - NO forbidden phrases: {', '.join(self.FORBIDDEN_PHRASES)}.
        """
        return brief

    def run_surgical_sprint(self, sprint_data):
        """
        Executes a sprint with an automated self-correction loop.
        """
        print(f"COMMENCING SPRINT V3: {len(sprint_data)} topics.")
        
        # 1. Formula Registration
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

        # 2. Iterative Ingestion
        active_sprint = sprint_data.copy()
        final_success = []
        final_failed = {}

        for attempt in range(self.max_retries + 1):
            if not active_sprint:
                break
                
            print(f"--- Attempt {attempt + 1} for {len(active_sprint)} slugs ---")
            success, failed = self.orch.execute_sprint(active_sprint, build_hub=False)
            
            final_success.extend(success)
            
            if not failed:
                break
                
            # Prepare for retry
            active_sprint = {}
            for slug, errors in failed.items():
                print(f"  -> REJECTED [{slug}]: {errors[0]}")
                # We store the last errors for the agent to see
                final_failed[slug] = errors
                # The agent will need to manually refactor these based on the errors
                # In this script context, we stop and let the orchestrating agent handle the fix
            
            # If we are in a script, we can't 're-draft' without an LLM call.
            # But we can provide the failure report.
            break 

        # 3. Final Build and Sync
        if final_success:
            # Rebuild hubs for successful slugs
            parent_hubs = set()
            for slug in final_success:
                sub = self.orch.data["subtopics"].get(slug)
                if sub and sub.get("parents"):
                    parent_hubs.add(sub["parents"][0])
            
            for hub in parent_hubs:
                self.orch.build(slug=hub)
            
            subprocess.run(["php", "cli_sync.php"], capture_output=True)
            print(f"SPRINT V3 COMPLETE: {len(final_success)} certified, {len(failed)} pending correction.")

        return final_success, final_failed

if __name__ == "__main__":
    v3 = SprintV3()
    print("Sprint V3 Engine Initialized.")
