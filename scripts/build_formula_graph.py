#!/usr/bin/env python3
"""
Terra Physics Lab - Formula Lineage & Derivation Graph Builder
Extracts hierarchical parent-child relationships, subcomponents, boundary limits,
and mathematical lineage across all 13,772 formulas in 256 shards.
Outputs:
- app/config/formula_derivation_graph.json
- app/config/formula_derivation_graph.json.gz
"""

import os
import glob
import json
import gzip
from collections import Counter

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT_DIR, "app/config/content")
SHARDS_DIR = os.path.join(CONTENT_DIR, "formulas")
CATEGORIES_FILE = os.path.join(CONTENT_DIR, "categories.json")
OUTPUT_JSON = os.path.join(ROOT_DIR, "app/config/formula_derivation_graph.json")
OUTPUT_GZ = os.path.join(ROOT_DIR, "app/config/formula_derivation_graph.json.gz")


def load_canonical_domains():
    if not os.path.exists(CATEGORIES_FILE):
        raise FileNotFoundError(f"Missing categories file: {CATEGORIES_FILE}")
    with open(CATEGORIES_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {k: v.get("title", k) for k, v in raw.items()}


def build_ground_truth_domain_map(categories):
    """
    Scans the 12 canonical topic files in app/config/content/{domain}.json
    and maps every explicitly curated formula_id and subtopic to its authentic domain.
    """
    formula_to_domain = {}
    subtopic_to_domain = {}

    for cat_id in categories.keys():
        cat_path = os.path.join(CONTENT_DIR, f"{cat_id}.json")
        if not os.path.exists(cat_path):
            continue
        try:
            with open(cat_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for subtopic_id, subtopic in data.items():
                subtopic_to_domain[subtopic_id] = cat_id
                if isinstance(subtopic, dict):
                    # Direct formula_ids
                    for fid in subtopic.get("formula_ids", []):
                        if isinstance(fid, str):
                            formula_to_domain[fid] = cat_id
                    # Also inspect section formulas if present
                    for sec in subtopic.get("sections", []):
                        if isinstance(sec, dict):
                            for fid in sec.get("formulas", []):
                                if isinstance(fid, str):
                                    formula_to_domain[fid] = cat_id
                                elif isinstance(fid, dict) and "id" in fid:
                                    formula_to_domain[fid["id"]] = cat_id
        except Exception as e:
            print(f"[WARN] Error reading {cat_path}: {e}")

    return formula_to_domain, subtopic_to_domain


def resolve_all_domains(formulas, formula_to_domain, subtopic_to_domain):
    """
    Resolves domain for all formulas using:
    1. Direct ground-truth topic mapping.
    2. Multi-pass graph lineage inheritance (parents, subcomponents, prerequisites).
    3. Subtopic prefix resolution.
    4. Controlled unmapped fallback (flagged explicitly).
    """
    resolved = dict(formula_to_domain)

    # 1. Multi-pass graph propagation
    changed = True
    passes = 0
    while changed and passes < 10:
        changed = False
        passes += 1
        for fid, fval in formulas.items():
            if fid in resolved:
                continue

            # Check parent_formula_id
            parent = fval.get("parent_formula_id")
            if parent and parent in resolved:
                resolved[fid] = resolved[parent]
                changed = True
                continue

            # Check subcomponents
            for sc in fval.get("subcomponents", []):
                sc_id = sc if isinstance(sc, str) else (sc.get("id") if isinstance(sc, dict) else None)
                if sc_id and sc_id in resolved:
                    resolved[fid] = resolved[sc_id]
                    changed = True
                    break
            if fid in resolved:
                continue

            # Check prerequisites
            for pr in fval.get("prerequisites", []):
                pr_id = pr if isinstance(pr, str) else (pr.get("id") if isinstance(pr, dict) else None)
                if pr_id and pr_id in resolved:
                    resolved[fid] = resolved[pr_id]
                    changed = True
                    break

    # 2. Subtopic prefix matching for newly ingested or derived identities
    prefix_matched = 0
    for fid in formulas.keys():
        if fid in resolved:
            continue
        for subtopic_id, dom in subtopic_to_domain.items():
            if fid.startswith(subtopic_id):
                resolved[fid] = dom
                prefix_matched += 1
                break

    # 3. Controlled fallback (flagged, never silently dumped to classical)
    orphan_count = 0
    for fid in formulas.keys():
        if fid not in resolved:
            orphan_count += 1
            resolved[fid] = "theoretical-physics"

    if orphan_count > 0:
        print(f"[WARN] {orphan_count} orphan formulas could not be mapped and were assigned to 'theoretical-physics'.")

    return resolved


def main():
    print("=================================================================")
    print("Terra Physics Lab - Formula Lineage & Derivation Graph Builder")
    print("=================================================================")

    categories = load_canonical_domains()
    print(f"[INFO] Loaded {len(categories)} canonical physics domains from categories.json")

    formula_to_domain, subtopic_to_domain = build_ground_truth_domain_map(categories)
    print(f"[INFO] Ground truth: {len(formula_to_domain):,} formulas mapped directly from domain topic files.")

    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*/shard_*.json")))
    print(f"[INFO] Scanning {len(shard_files)} shard files...")

    formulas = {}
    all_formula_ids = set()

    for sf in shard_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
                for fid, f_data in data.items():
                    if isinstance(f_data, dict):
                        f_data["id"] = fid
                        formulas[fid] = f_data
                        all_formula_ids.add(fid)
        except Exception as e:
            print(f"[WARN] Error reading {sf}: {e}")

    print(f"[INFO] Loaded {len(formulas):,} total formulas from shards.")

    resolved_domains = resolve_all_domains(formulas, formula_to_domain, subtopic_to_domain)

    nodes = {}
    links = []
    seen_links = set()

    def add_link(source, target, link_type, label=""):
        if not source or not target or source == target:
            return
        if source not in all_formula_ids or target not in all_formula_ids:
            return
        edge_key = f"{source}->{target}:{link_type}"
        if edge_key not in seen_links:
            seen_links.add(edge_key)
            links.append({
                "source": source,
                "target": target,
                "type": link_type,
                "label": label
            })

    # Build nodes & links
    for fid, formula in formulas.items():
        title = formula.get("title", fid)
        eq = formula.get("equation", "")
        summary = formula.get("intuitive_summary", "")
        domain = resolved_domains.get(fid, "theoretical-physics")

        nodes[fid] = {
            "id": fid,
            "title": title,
            "equation": eq,
            "summary": summary,
            "domain": domain,
            "domain_label": categories.get(domain, domain),
            "status": formula.get("status", "platinum")
        }

        # 1. Subcomponents Link (Parent -> Child)
        subcomps = formula.get("subcomponents", [])
        if isinstance(subcomps, list):
            for sc in subcomps:
                if isinstance(sc, str) and sc in all_formula_ids:
                    add_link(fid, sc, "subcomponent", "Subcomponent")
                elif isinstance(sc, dict) and "id" in sc and sc["id"] in all_formula_ids:
                    add_link(fid, sc["id"], "subcomponent", sc.get("role", "Subcomponent"))

        # 2. Prerequisites / Parent Links
        prereqs = formula.get("prerequisites", [])
        if isinstance(prereqs, list):
            for pr in prereqs:
                if isinstance(pr, str) and pr in all_formula_ids:
                    add_link(pr, fid, "derivation", "Derives")

        # 3. Related Formulas
        related = formula.get("related_formulas", [])
        if isinstance(related, list):
            for rf in related:
                if isinstance(rf, str) and rf in all_formula_ids:
                    add_link(fid, rf, "related", "Related")

    # Build adjacency index for fast subgraph extraction
    upstream = {}   # node -> list of parents/prereqs
    downstream = {} # node -> list of children/applications

    for link in links:
        s = link["source"]
        t = link["target"]
        if t not in upstream:
            upstream[t] = []
        upstream[t].append({"id": s, "type": link["type"], "label": link["label"]})

        if s not in downstream:
            downstream[s] = []
        downstream[s].append({"id": t, "type": link["type"], "label": link["label"]})

    graph_payload = {
        "metadata": {
            "total_nodes": len(nodes),
            "total_links": len(links),
            "generated_at": int(os.path.getmtime(SHARDS_DIR))
        },
        "domains": categories,
        "nodes": nodes,
        "links": links,
        "upstream": upstream,
        "downstream": downstream
    }

    # Save uncompressed and gzip compressed
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(graph_payload, f, indent=2, ensure_ascii=False)

    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as f:
        json.dump(graph_payload, f, ensure_ascii=False)

    json_size_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    gz_size_mb = os.path.getsize(OUTPUT_GZ) / (1024 * 1024)

    # Print domain breakdown
    print("\n--- Domain Distribution ---")
    domain_counts = Counter(node["domain"] for node in nodes.values())
    for dom, cnt in domain_counts.most_common():
        label = categories.get(dom, dom)
        pct = (cnt / len(nodes)) * 100
        print(f"  • {label:42s}: {cnt:5,d} ({pct:5.2f}%)")

    print(f"\n[OK] Graph generated successfully!")
    print(f"  • Total Nodes: {len(nodes):,}")
    print(f"  • Total Direct Links: {len(links):,}")
    print(f"  • Uncompressed: {OUTPUT_JSON} ({json_size_mb:.2f} MB)")
    print(f"  • Gzip Compressed: {OUTPUT_GZ} ({gz_size_mb:.2f} MB)")
    print("=================================================================")


if __name__ == "__main__":
    main()
