#!/usr/bin/env python3
"""
🌌 Formula Lineage Discovery & Resolution Engine
Resolves optimal axiomatic parents, derivation relations, and downstream
specializations for any given formula definition.
"""

import os
import sys
import glob
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

# Catalog of primary master laws / axiomatic foundations
CORE_AXIOMATIC_PARENTS = [
    ("schrodinger-equation", ["schrodinger", "wavefunction", "hamiltonian", "quantum", "operator", "psi", "eigenstate"]),
    ("maxwells-equations-vacuum-formalism-c392d9cd", ["maxwell", "electric field", "magnetic field", "poynting", "electromagnetic", "vector potential"]),
    ("einstein-field-equations", ["einstein", "metric", "curvature", "ricci", "stress-energy", "geodesic", "schwarzschild", "spacetime"]),
    ("poissons-and-laplaces-equations-3d29b9ae", ["poisson", "laplace", "greens function", "potential", "charge density", "delta"]),
    ("first-law-of-thermodynamics", ["thermodynamics", "heat", "internal energy", "work", "enthalpy", "entropy"]),
    ("second-law-of-thermodynamics", ["entropy", "carnot", "irreversible", "clausius", "temperature"]),
    ("navier-stokes-momentum-equation", ["fluid", "navier-stokes", "viscosity", "reynolds", "velocity field", "pressure gradient", "continuity"]),
    ("euler-lagrange-equations-of-motion", ["lagrangian", "action", "euler-lagrange", "generalized coordinates", "principle of least action"]),
    ("hamiltons-equations-of-motion", ["hamiltonian", "canonical", "phase space", "poisson bracket", "momentum"]),
    ("dirac-equation", ["dirac", "spinor", "gamma matrices", "clifford algebra", "relativistic quantum"]),
    ("lorentz-transformation", ["lorentz", "boost", "minkowski", "gamma factor", "spacetime interval", "proper time", "proper length"]),
    ("canonical-commutation-relation", ["commutator", "uncertainty", "heisenberg", "position operator", "momentum operator", "parity"]),
    ("noethers-current", ["noether", "symmetry", "conserved current", "invariance", "conservation of energy", "momentum tensor"]),
    ("ideal-gas-law", ["gas", "boltzmann", "ideal gas", "isothermal", "adiabatic"]),
    ("de-broglie-wavelength", ["de broglie", "matter wave", "planck", "wavelength", "momentum-wavelength"])
]

def load_lineage_database():
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, "*", "shard_*.json")))
    formulas = {}
    parent_map = {}
    child_map = {}
    
    for sf in shard_files:
        with open(sf, "r", encoding="utf-8") as f:
            d = json.load(f)
            for fid, form in d.items():
                if not isinstance(form, dict): continue
                formulas[fid] = form
                
                pid = form.get("parent_formula_id")
                if pid and pid != fid:
                    parent_map[fid] = pid
                    child_map.setdefault(pid, []).append(fid)
                    
                subs = form.get("subcomponents", [])
                if isinstance(subs, list):
                    for cid in subs:
                        if cid and cid != fid:
                            child_map.setdefault(fid, []).append(cid)
                            
    # Deduplicate children
    for fid in child_map:
        child_map[fid] = list(dict.fromkeys(child_map[fid]))
        
    return formulas, parent_map, child_map

def normalize_text(text):
    if not text: return ""
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())

def discover_lineage(title, equation, conceptual_definition="", interpretation="", existing_parent=None, formulas_db=None):
    if formulas_db is None:
        formulas, parent_map, child_map = load_lineage_database()
    else:
        formulas, parent_map, child_map = formulas_db

    combined_text = f"{title} {equation} {conceptual_definition} {interpretation}".lower()
    norm_combined = normalize_text(combined_text)
    
    resolved_parent_id = None
    derivation_type = "DERIVED_FROM"
    
    # 1. Check if existing parent is valid
    if existing_parent and existing_parent in formulas:
        resolved_parent_id = existing_parent
    else:
        # Check title/slug direct match in formulas
        for fid, f in formulas.items():
            if fid == existing_parent:
                resolved_parent_id = fid
                break
                
    # 2. Heuristic domain keyword matching to master axiomatic laws
    if not resolved_parent_id:
        best_axiom = None
        best_score = 0
        for axiom_id, keywords in CORE_AXIOMATIC_PARENTS:
            if axiom_id in formulas:
                score = sum(1 for kw in keywords if kw in combined_text)
                if score > best_score:
                    best_score = score
                    best_axiom = axiom_id
                    
        if best_axiom and best_score >= 2:
            resolved_parent_id = best_axiom

    # 3. Graph search across all 13,780 formulas for semantic affinity
    if not resolved_parent_id:
        scored_candidates = []
        for fid, f in formulas.items():
            f_title = f.get("title", "")
            f_eq = f.get("equation", "")
            f_type = f.get("derivation_type", "")
            
            # Prefer formulas with established ancestry or axiomatic foundation
            is_good_parent = fid in parent_map or f_type == "AXIOMATIC_FOUNDATION" or len(child_map.get(fid, [])) > 2
            if not is_good_parent: continue
            
            score = 0
            # Title overlap
            t_words = [w for w in normalize_text(f_title).split() if len(w) > 3]
            for tw in t_words:
                if tw in norm_combined:
                    score += 3
                    
            if score > 5:
                scored_candidates.append((score, fid))
                
        if scored_candidates:
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            resolved_parent_id = scored_candidates[0][1]

    # 4. Discover downstream subcomponents / children
    subcomponents = []
    child_candidates = []
    
    # Look for formulas in the same domain or referencing the current equation symbols
    title_words = [w for w in normalize_text(title).split() if len(w) > 3]
    for fid, f in formulas.items():
        if fid == resolved_parent_id: continue
        f_title = f.get("title", "")
        f_norm = normalize_text(f_title)
        
        # Don"t link giant parent hubs as children
        if len(child_map.get(fid, [])) > 15: continue
        
        overlap = sum(1 for tw in title_words if tw in f_norm)
        if overlap >= 2:
            child_candidates.append((overlap, fid))
            
    if child_candidates:
        child_candidates.sort(key=lambda x: x[0], reverse=True)
        subcomponents = [c[1] for c in child_candidates[:3]]

    # Determine derivation type
    if "limit" in title.lower() or "approximation" in title.lower() or "boundary" in title.lower():
        derivation_type = "LIMIT_CASE"
    elif "special" in title.lower() or "case" in title.lower() or "uniform" in title.lower():
        derivation_type = "SPECIAL_CASE"
    elif resolved_parent_id:
        derivation_type = "DERIVED_FROM"
    else:
        derivation_type = "AXIOMATIC_FOUNDATION"

    # Compute prospective LHI Score
    upstream_score = 35 if resolved_parent_id or derivation_type == "AXIOMATIC_FOUNDATION" else 0
    downstream_score = 35 if len(subcomponents) >= 3 else (25 if len(subcomponents) == 2 else (15 if len(subcomponents) == 1 else 0))
    depth_score = 15 if (resolved_parent_id and len(subcomponents) > 0) else 5
    quality_score = 15
    lhi_score = upstream_score + downstream_score + depth_score + quality_score

    parent_title = formulas[resolved_parent_id].get("title") if resolved_parent_id and resolved_parent_id in formulas else None
    children_titles = [formulas[cid].get("title", cid) for cid in subcomponents if cid in formulas]

    return {
        "parent_formula_id": resolved_parent_id or "",
        "derivation_type": derivation_type,
        "subcomponents": subcomponents,
        "lhi_score": lhi_score,
        "parent_title": parent_title,
        "children_titles": children_titles
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_title = sys.argv[1]
        eq = sys.argv[2] if len(sys.argv) > 2 else ""
        res = discover_lineage(test_title, eq)
        print(json.dumps(res, indent=2))
    else:
        print("Usage: python3 lineage_resolver.py "<Title>" ["<Equation>"]")
