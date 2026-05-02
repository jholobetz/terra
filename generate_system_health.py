import json
import re
import os
import sys
from datetime import datetime

class HealthDashboard:
    def __init__(self, content_dir="app/config/content"):
        self.content_dir = content_dir
        self.tech_terms = ["manifold", "operator", "unitary", "tensor", "symmetry", "conservation", "variational", "hamiltonian", "lagrangian", "eigenvalue", "generator"]
        self.health_data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "global_stats": {
                "total_subtopics": 0,
                "total_words": 0,
                "total_formula_refs": 0,
                "total_links": 0,
                "average_word_count": 0,
                "average_density_score": 0
            },
            "platinum_scorecard": {
                "platinum_count": 0,
                "platinum_percentage": 0,
                "low_depth_count": 0,
                "non_technical_count": 0
            },
            "integrity_summary": {
                "broken_links": 0,
                "broken_formulas": 0,
                "orphans_count": 0
            },
            "shard_health": {}
        }
        self.all_subtopics = {}
        self.all_slugs = set()
        self.incoming_links = {}

    def load_data(self):
        from orchestrator import PhysicsOrchestrator
        self.orch = PhysicsOrchestrator(content_dir=self.content_dir)
        self.all_subtopics = self.orch.data["subtopics"]
        self.formula_registry = self.orch.data["formula_registry"]
        self.topics = self.orch.data["topics"]
        self.all_slugs = set(self.all_subtopics.keys()).union(set(self.topics.keys()))
        
        for slug in self.all_slugs:
            self.incoming_links[slug] = 0

    def analyze(self):
        total_score = 0
        link_pattern = re.compile(r'href=[\\"]+/physics/(subtopic|topic)/([^\\"]+)[\\"]+')
        
        for shard_name, shard_data in self.orch.shards.items():
            shard_stats = {"count": 0, "platinum": 0, "avg_words": 0, "avg_density": 0}
            shard_words = 0
            shard_density = 0
            
            for slug, sub in shard_data.items():
                if "content" not in sub: continue
                
                content = sub["content"]
                # Stats
                words = len(re.findall(r'\w+', content))
                latex_count = len(re.findall(r'\\\(|\\\[', content))
                term_score = sum(5 for term in self.tech_terms if term in content.lower())
                density_score = (latex_count * 15) + term_score
                
                # Update Shard
                shard_stats["count"] += 1
                shard_words += words
                shard_density += density_score
                
                # Check Platinum (500w, 60 density)
                is_platinum = words >= 500 and density_score >= 60
                if is_platinum:
                    shard_stats["platinum"] += 1
                    self.health_data["platinum_scorecard"]["platinum_count"] += 1
                
                if words < 500:
                    self.health_data["platinum_scorecard"]["low_depth_count"] += 1
                if density_score < 30:
                    self.health_data["platinum_scorecard"]["non_technical_count"] += 1
                    
                # Link Scan for Orphans
                matches = link_pattern.findall(content)
                for _, target in matches:
                    self.health_data["global_stats"]["total_links"] += 1
                    if target in self.incoming_links:
                        self.incoming_links[target] += 1
                    else:
                        self.health_data["integrity_summary"]["broken_links"] += 1
                
                # Formula check
                for f_id in sub.get("formula_ids", []):
                    self.health_data["global_stats"]["total_formula_refs"] += 1
                    if f_id not in self.formula_registry:
                        self.health_data["integrity_summary"]["broken_formulas"] += 1

                self.health_data["global_stats"]["total_subtopics"] += 1
                self.health_data["global_stats"]["total_words"] += words
                total_score += density_score

            if shard_stats["count"] > 0:
                shard_stats["avg_words"] = round(shard_words / shard_stats["count"], 1)
                shard_stats["avg_density"] = round(shard_density / shard_stats["count"], 1)
                self.health_data["shard_health"][shard_name] = shard_stats

        # Finals
        count = self.health_data["global_stats"]["total_subtopics"]
        if count > 0:
            self.health_data["global_stats"]["average_word_count"] = round(self.health_data["global_stats"]["total_words"] / count, 1)
            self.health_data["global_stats"]["average_density_score"] = round(total_score / count, 1)
            self.health_data["platinum_scorecard"]["platinum_percentage"] = round((self.health_data["platinum_scorecard"]["platinum_count"] / count) * 100, 2)
        
        # Orphans
        self.health_data["integrity_summary"]["orphans_count"] = sum(1 for s, c in self.incoming_links.items() if c == 0 and s not in self.topics)

    def save(self):
        with open("system_health.json", "w") as f:
            json.dump(self.health_data, f, indent=4)
        print(f"SUCCESS: System Health Dashboard generated.")
        print(f"Platinum Score: {self.health_data['platinum_scorecard']['platinum_percentage']}%")

if __name__ == "__main__":
    dashboard = HealthDashboard()
    dashboard.load_data()
    dashboard.analyze()
    dashboard.save()
