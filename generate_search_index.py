import json
import re
import os
import sys

class SearchIndexer:
    def __init__(self, content_dir="app/config/content"):
        self.content_dir = content_dir
        self.tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
        self.index = {}

    def run(self):
        from orchestrator import PhysicsOrchestrator
        orch = PhysicsOrchestrator(content_dir=self.content_dir)
        
        # 1. Index Main Topics
        for slug, topic in orch.data["topic_contents"].items():
            self.index[slug] = self._build_entry(slug, topic, "topics/" + slug + ".json")

        # 2. Index Subtopics
        for slug, sub in orch.data["subtopics"].items():
            shard_file = orch.slug_to_shard.get(slug, "misc.json")
            self.index[slug] = self._build_entry(slug, sub, shard_file)

        # 3. Save Index
        with open(os.path.join(self.content_dir, "search_index.json"), "w") as f:
            json.dump(self.index, f, indent=4)
        
        print(f"SUCCESS: Search index generated with {len(self.index)} entries.")

    def _build_entry(self, slug, data, shard):
        content = data.get("content", "")
        title = data.get("title", "Untitled")
        
        # Calculate stats for Weighting
        words = len(re.findall(r'\w+', content))
        latex_count = len(re.findall(r'\\\(|\\\[', content))
        term_score = sum(1 for term in self.tech_terms if term in content.lower())
        
        # Platinum Check (Current standards: 500w, 60 density)
        density_score = (latex_count * 15) + (term_score * 5)
        is_platinum = 1 if (words >= 500 and density_score >= 60) else 0

        # Keyword Extraction
        keywords = set()
        # 1. Bolded terms
        bold_matches = re.findall(r'<strong>(.*?)</strong>', content)
        for b in bold_matches:
            # Strip tags and clean
            clean_b = re.sub(r'<[^>]+>', '', b).strip().lower()
            if len(clean_b) > 2: keywords.add(clean_b)
            
        # 2. Technical Terms
        for term in self.tech_terms:
            if term in content.lower():
                keywords.add(term)
        
        # 3. Formula IDs (as semantic anchors)
        for f_id in data.get("formula_ids", []):
            # Strip any residual HTML if the ID was ingested with tags (safety)
            clean_fid = re.sub(r'<[^>]+>', '', f_id).replace('-', ' ')
            keywords.add(clean_fid)

        # 4. Clean all keywords (No HTML tags, length check)
        final_keywords = set()
        for kw in keywords:
            clean = re.sub(r'<[^>]+>', '', kw).strip().lower()
            if len(clean) > 2 and not clean.startswith('a href'):
                final_keywords.add(clean)

        return {
            "t": title,
            "p": data.get("parents", []),
            "s": shard,
            "k": list(final_keywords),
            "w": density_score,      # Raw density as weight
            "pl": is_platinum        # Platinum flag
        }

if __name__ == "__main__":
    indexer = SearchIndexer()
    indexer.run()
