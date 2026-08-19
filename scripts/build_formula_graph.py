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
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARDS_DIR = os.path.join(ROOT_DIR, "app/config/content/formulas")
OUTPUT_JSON = os.path.join(ROOT_DIR, "app/config/formula_derivation_graph.json")
OUTPUT_GZ = os.path.join(ROOT_DIR, "app/config/formula_derivation_graph.json.gz")

# Canonical physics domain mappings based on shard directories or title heuristics
DOMAINS = {
    "classical-mechanics": "Classical Mechanics & Dynamics",
    "electromagnetism": "Electromagnetism & Electrodynamics",
    "thermodynamics": "Thermodynamics & Statistical Physics",
    "quantum-mechanics": "Quantum Mechanics",
    "quantum-field-theory": "Quantum Field Theory & Particle Physics",
    "special-relativity": "Special Relativity",
    "general-relativity": "General Relativity & Gravitation",
    "astrophysics": "Astrophysics & Cosmology",
    "condensed-matter": "Condensed Matter & Solid State",
    "optics-photonics": "Optics & Photonics",
    "nuclear-physics": "Nuclear Physics",
    "fluid-dynamics": "Fluid Dynamics & Plasma Physics"
}


def infer_domain(formula_id, title, equation):
    text = (formula_id + " " + title + " " + equation).lower()
    if any(k in text for k in ["metric", "einstein", "curvature", "geodesic", "schwarzschild", "christoffel", "riemann", "bianchi", "tensor"]):
        return "general-relativity"
    if any(k in text for k in ["dirac", "lagrangian", "feynman", "spinor", "propagator", "boson", "fermion", "gauge", "higgs", "qcd", "qft"]):
        return "quantum-field-theory"
    if any(k in text for k in ["schrodinger", "wavefunction", "wave function", "hamiltonian", "commutator", "ket", "bra", "heisenberg", "quantum"]):
        return "quantum-mechanics"
    if any(k in text for k in ["entropy", "boltzmann", "thermodynamic", "carnot", "partition function", "helmholtz", "gibbs", "enthalpy"]):
        return "thermodynamics"
    if any(k in text for k in ["maxwell", "electric field", "magnetic field", "poynting", "dielectric", "lorentz force", "coulomb"]):
        return "electromagnetism"
    if any(k in text for k in ["friedmann", "redshift", "hubble", "cosmology", "black hole", "chandrasekhar", "stellar", "galaxy"]):
        return "astrophysics"
    if any(k in text for k in ["navier", "stokes", "bernoulli", "viscosity", "reynolds", "fluid", "vorticity"]):
        return "fluid-dynamics"
    if any(k in text for k in ["fermi", "band", "bose-einstein", "superconductivity", "phonon", "lattice", "semiconductor"]):
        return "condensed-matter"
    if any(k in text for k in ["lorentz transformation", "rapidity", "four-velocity", "four-momentum", "spacetime interval"]):
        return "special-relativity"
    if any(k in text for k in ["newton", "kepler", "lagrange", "euler", "hooke", "pendulum", "momentum", "torque"]):
        return "classical-mechanics"
    if any(k in text for k in ["cross section", "decay", "radioactive", "fission", "fusion", "alpha decay", "beta decay"]):
        return "nuclear-physics"
    return "classical-mechanics"


def main():
    print("=================================================================")
    print("Terra Physics Lab - Formula Lineage & Derivation Graph Builder")
    print("=================================================================")

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

    print(f"[INFO] Loaded {len(formulas)} formulas into memory.")

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
        domain = infer_domain(fid, title, eq)

        nodes[fid] = {
            "id": fid,
            "title": title,
            "equation": eq,
            "summary": summary,
            "domain": domain,
            "domain_label": DOMAINS.get(domain, domain),
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
        "domains": DOMAINS,
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

    print(f"\n[OK] Graph generated successfully!")
    print(f"  • Total Nodes: {len(nodes):,}")
    print(f"  • Total Direct Links: {len(links):,}")
    print(f"  • Uncompressed: {OUTPUT_JSON} ({json_size_mb:.2f} MB)")
    print(f"  • Gzip Compressed: {OUTPUT_GZ} ({gz_size_mb:.2f} MB)")
    print("=================================================================")


if __name__ == "__main__":
    main()
