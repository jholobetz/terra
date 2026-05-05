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
        self.mapping = self._get_slug_mapping()

    def _get_slug_mapping(self):
        mapping = {}
        for file in os.listdir(self.content_dir):
            if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json"]:
                path = os.path.join(self.content_dir, file)
                try:
                    with open(path, "r") as f:
                        # We only need the keys, not the full content
                        # This is still a bit heavy for huge files, but better than full load
                        content = json.load(f)
                        for slug in content:
                            mapping[slug] = file
                except Exception:
                    continue
        return mapping

    def _get_concept(self, slug):
        if slug in self.data["topics"]:
            return self.data["topics"][slug]
        
        shard_file = self.mapping.get(slug)
        if shard_file:
            shard = self._load_json(shard_file)
            return shard.get(slug)
        return None

    def pack_brief(self, target_term, parent_slug):
        """Generates a detailed prompt for a sub-agent."""
        
        # 1. Find Parent Context
        parent = self._get_concept(parent_slug)
        parent_title = parent.get("title", parent_slug) if parent else parent_slug
        parent_content = parent.get("content", "No parent content found.") if parent else ""

        # 2. Find Sibling Redundancy
        # We still need to load siblings. This requires a scan.
        # To optimize, we can use the mapping to find which shards to check,
        # but siblings are usually in the same shard as the parent.
        siblings = []
        parent_shard = self.mapping.get(parent_slug)
        if parent_shard:
            shard_data = self._load_json(parent_shard)
            siblings = [s["title"] for s in shard_data.values() if s.get("parent_topic") == parent_slug or parent_slug in s.get("parents", [])]
        
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

## 4. STRICT SUBMISSION REQUIREMENTS (MANDATORY)
Return a single JSON object for the "subtopics" map. You MUST adhere to the following Platinum Standard constraints. Your response will be programmatically rejected if it fails any of these:

1. **WORD COUNT**: Content MUST exceed 650 words. Do not submit short summaries. Expand on the mathematical formalism and ontological implications.
2. **ORGANIC PROSE LAYOUT**: DO NOT use numbered lists or outline formats (e.g., absolutely NO `<h3>1. ...</h3>` or `<ul><li>...`). Write flowing, continuous paragraphs separated by descriptive thematic `<h3>` headers (e.g., `<h3>The Geometric Manifold</h3>`).
3. **MANDATORY LINKING**: You MUST organically weave at least 5 of the 'Existing Siblings' listed above into your prose. Do not put them in a 'Related Links' footer. Integrate them naturally into the sentences.
4. **NO META-TALK**: Do not use educational framing, conversational filler, or introductory phrases. FORBIDDEN PHRASES include: "university-level", "imagine a world", "let's dive into", "in conclusion", "as we have seen". Maintain a dry, senior physicist tone.
5. **FORMULAS**: Use the "formulas" array structure for any NEW formulas you introduce. Include LaTeX derivations in the content body.
"""
        return brief

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python3 pack_context.py [Target Term] [Parent Slug]")
    else:
        packer = ContextPacker()
        print(packer.pack_brief(sys.argv[1], sys.argv[2]))
