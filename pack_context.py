import json
import os
import re

class ContextPacker:
    def __init__(self, content_dir="app/config/content"):
        self.content_dir = content_dir
        self.data = {
            "topics": {},
            "subtopics": {},
            "formula_registry": {}
        }
        self.load_data()

    def _load_json(self, filename):
        path = os.path.join(self.content_dir, filename)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def load_data(self):
        self.data["topics"] = self._load_json("categories.json")
        self.data["formula_registry"] = self._load_json("formulas.json")
        
        # Load all subtopic shards
        for file in os.listdir(self.content_dir):
            if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json"]:
                shard = self._load_json(file)
                self.data["subtopics"].update(shard)

    def pack_brief(self, target_term, parent_slug):
        """Generates a detailed prompt for a sub-agent."""
        
        # 1. Find Parent Context
        parent = self.data["topics"].get(parent_slug) or self.data["subtopics"].get(parent_slug)
        parent_title = parent.get("title", parent_slug) if parent else parent_slug
        parent_content = parent.get("content", "No parent content found.") if parent else ""

        # 2. Find Sibling Redundancy
        siblings = [s["title"] for s in self.data["subtopics"].values() if s.get("parent_topic") == parent_slug]
        
        # 3. Find Relevant Formulas (Basic keyword match)
        relevant_formulas = []
        keywords = target_term.lower().split()
        for f_id, f_obj in self.data["formula_registry"].items():
            if any(kw in f_obj["title"].lower() for kw in keywords):
                relevant_formulas.append({"id": f_id, "title": f_obj["title"], "eq": f_obj["equation"]})

        # 4. Assemble the Brief
        brief = f"""# RESEARCH BRIEF: {target_term}
**Parent Topic:** {parent_title} ({parent_slug})
**Objective:** Create a University-Level subtopic for "{target_term}".

## 1. Stylistic Reference (Parent Content)
Match the tone and depth of this existing content:
---
{parent_content[:1500]}...
---

## 2. Redundancy Guard (Existing Siblings)
The following topics already exist under this parent. Do NOT repeat their core content:
{", ".join(siblings[:20]) if siblings else "None"}

## 3. Relational Assets (Formula Registry)
The following formulas already exist. Use their IDs if applicable, or suggest a new one if it is missing:
{json.dumps(relevant_formulas[:5], indent=2) if relevant_formulas else "No matching formulas found."}

## 4. Submission Requirements
Return a single JSON object for the "subtopics" map. 
- Use the "formulas" array structure for new formulas.
- Ensure university-level depth (6 sections).
- Include links to existing topics using the <a href="/physics/subtopic/slug" class="subtopic-link"><strong>Title</strong></a> format.
"""
        return brief

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 pack_context.py [Target Term] [Parent Slug]")
    else:
        packer = ContextPacker()
        print(packer.pack_brief(sys.argv[1], sys.argv[2]))
