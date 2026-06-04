#!/usr/bin/env python3
import os
import sys
import json
import re
from collections import defaultdict

# Add current directory to path to allow importing from scripts.maintenance
sys.path.append(os.getcwd())

from scripts.maintenance.generate_system_health import score_subtopic, TECH_TERMS
from orchestrator import PhysicsOrchestrator

def main():
    content_dir = "app/config/content"
    artifact_dir = "/Users/holobetj/.gemini/antigravity-cli/brain/bbe38160-17c6-4e20-bcb0-1ae8207f61b0"
    os.makedirs(artifact_dir, exist_ok=True)
    report_path = os.path.join(artifact_dir, "substandard_report.md")

    print("Initializing PhysicsOrchestrator...")
    orch = PhysicsOrchestrator(content_dir=content_dir)
    
    # Track categories
    slug_to_cat = {}
    for cat_slug in orch.data["topics"]:
        shard_name = f"{cat_slug}.json"
        if shard_name in orch.shards:
            for sub_slug in orch.shards[shard_name]:
                slug_to_cat[sub_slug] = cat_slug
        slug_to_cat[cat_slug] = cat_slug

    low_depth_subtopics = []
    low_density_critical = [] # density < 30
    low_density_substandard = [] # 30 <= density < 60
    qualitative_violations = []

    print("Scanning subtopics...")
    for shard_name, shard_data in orch.shards.items():
        if shard_name == "compiled_trie_regex.json":
            continue
        for slug, sub in shard_data.items():
            if "content" not in sub:
                continue
            
            stats = score_subtopic(slug, sub)
            cat_slug = slug_to_cat.get(slug, "legacy-orphans")
            cat_title = orch.data["topics"].get(cat_slug, {}).get("title", cat_slug.replace('-', ' ').title())

            sub_info = {
                "slug": slug,
                "title": sub.get("title", slug),
                "shard": shard_name,
                "category": cat_title,
                "words": stats["words"],
                "density": stats["density_score"],
                "has_lead_violation": stats["has_lead_violation"],
                "has_artifact_violation": stats["has_artifact_violation"]
            }

            if stats["words"] < 650:
                low_depth_subtopics.append(sub_info)
            
            if stats["density_score"] < 30:
                low_density_critical.append(sub_info)
            elif stats["density_score"] < 60:
                low_density_substandard.append(sub_info)

            if stats["has_lead_violation"] or stats["has_artifact_violation"]:
                qualitative_violations.append(sub_info)

    # Sort reports for readability
    low_depth_subtopics.sort(key=lambda x: (x["shard"], x["words"]))
    low_density_critical.sort(key=lambda x: (x["shard"], x["density"]))
    low_density_substandard.sort(key=lambda x: (x["shard"], x["density"]))
    qualitative_violations.sort(key=lambda x: (x["shard"], x["slug"]))

    print("Generating Markdown report...")
    
    with open(report_path, "w") as f:
        f.write("# Organic Platinum Standard (OPS) Audit Report\n\n")
        f.write(f"This report outlines all subtopic nodes that currently fall short of the **Organic Platinum Standard (OPS)** metrics.\n\n")
        
        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total Subtopics Scanned:** {len(orch.data['subtopics'])}\n")
        f.write(f"- **Low-Depth Subtopics (< 650 words):** {len(low_depth_subtopics)}\n")
        f.write(f"- **Critically Low Density (< 30 score):** {len(low_density_critical)}\n")
        f.write(f"- **Sub-standard Density (30 - 59 score):** {len(low_density_substandard)}\n")
        f.write(f"- **Qualitative Violations (Lead/List gates):** {len(qualitative_violations)}\n\n")

        f.write("## 1. Low-Depth Subtopics (< 650 words)\n")
        f.write("These subtopics fail the quantitative depth threshold. A minimum of 650 words of rich technical prose is required.\n\n")
        f.write("| Subtopic Title / Slug | Shard | Category | Word Count |\n")
        f.write("| --- | --- | --- | --- |\n")
        for sub in low_depth_subtopics:
            f.write(f"| [{sub['title']}](file://{os.path.abspath(content_dir)}/{sub['shard']}) <br>`{sub['slug']}` | `{sub['shard']}` | {sub['category']} | **{sub['words']}** |\n")
        f.write("\n")

        f.write("## 2. Critically Low Technical Density (< 30 score)\n")
        f.write("These subtopics have density scores under 30. The target is $\\ge 60$. Density is calculated as: `(LaTeX blocks * 15) + (Tech terms * 5)`.\n\n")
        f.write("| Subtopic Title / Slug | Shard | Category | Density Score |\n")
        f.write("| --- | --- | --- | --- |\n")
        for sub in low_density_critical:
            f.write(f"| [{sub['title']}](file://{os.path.abspath(content_dir)}/{sub['shard']}) <br>`{sub['slug']}` | `{sub['shard']}` | {sub['category']} | **{sub['density']}** |\n")
        f.write("\n")

        f.write("## 3. Sub-standard Technical Density (30 - 59 score)\n")
        f.write("These subtopics are above the critical floor of 30, but still fall short of the full platinum standard requirement of $\\ge 60$.\n\n")
        f.write("| Subtopic Title / Slug | Shard | Category | Density Score |\n")
        f.write("| --- | --- | --- | --- |\n")
        for sub in low_density_substandard:
            f.write(f"| [{sub['title']}](file://{os.path.abspath(content_dir)}/{sub['shard']}) <br>`{sub['slug']}` | `{sub['shard']}` | {sub['category']} | {sub['density']} |\n")
        f.write("\n")

        f.write("## 4. Qualitative Violations\n")
        f.write("These subtopics violate style gates (e.g. title/slug in first 150 chars or unordered list html tags `<ul>`/`<li>`).\n\n")
        if not qualitative_violations:
            f.write("*None found! All subtopics are compliant with qualitative style gates.*\n")
        else:
            f.write("| Subtopic Title / Slug | Shard | Category | Violations |\n")
            f.write("| --- | --- | --- | --- |\n")
            for sub in qualitative_violations:
                v_list = []
                if sub["has_lead_violation"]:
                    v_list.append("Lead sentence contains title/slug")
                if sub["has_artifact_violation"]:
                    v_list.append("Contains forbidden `<ul>`/`<li>` tags")
                f.write(f"| [{sub['title']}](file://{os.path.abspath(content_dir)}/{sub['shard']}) <br>`{sub['slug']}` | `{sub['shard']}` | {sub['category']} | {', '.join(v_list)} |\n")
        f.write("\n")

    print(f"Report generated successfully at: {report_path}")

if __name__ == "__main__":
    main()
