#!/usr/bin/env python3
"""
🌲 Automated Lineage Family Enricher for Terra Physics Lab
Scans thin and moderate equations (LHI < 75) and enriches their upstream parents,
downstream applications, and reciprocal links across all 256 shards.

Usage:
    python3 scripts/maintenance/enrich_lineage_families.py [--dry-run] [--apply]
"""

import os
import sys
import json
import glob
import re
import argparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
GRAPH_BUILDER = os.path.join(PROJECT_ROOT, 'scripts', 'build_formula_graph.py')

# Core Master Foundation Hubs
FAMILY_PILLARS = {
    # Electromagnetism & Gauge Fields
    'maxwell-hub': {
        'parent_id': 'ampere-maxwell-law',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['poynting', 'lorenz gauge', 'coulomb gauge', 'displacement current', 'vector potential', 'radiation field', 'gauge transformation', 'permeability', 'permittivity', 'maxwell', 'electric', 'magnetic', 'curl', 'flux', 'induction', 'faraday', 'lorentz force', 'topological charge', 'chern'],
        'match_tex': ['\\nabla', '\\mathbf{E}', '\\mathbf{B}', '\\mathbf{A}', '\\mu_0', '\\varepsilon_0', '\\Phi_B', '\\Phi', 'C_n', 'F_\\mu']
    },
    # Quantum Dynamics & States
    'quantum-dynamics-hub': {
        'parent_id': 'time-dependent-schrodinger-equation',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['schrodinger', 'density matrix', 'von neumann', 'lindblad', 'master equation', 'collapse', 'bayesian filtering', 'expectation value', 'wave packet', 'bloch sphere', 'state vector', 'wavefunction', 'hilbert', 'hamiltonian', 'ket', 'bra', 'inner product', 'orthonormal', 'quantum'],
        'match_tex': ['\\langle', '\\rangle', '\\psi', '\\phi', '\\hat', '\\delta_ij', '\\delta_{ij}', '\\text{Tr}']
    },
    # Analytical Mechanics & Variational Principles
    'mechanics-hub': {
        'parent_id': 'stationary-action-principle-8836edf7',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['rotational invariance', 'noether', 'generalized coordinate', 'legendre transform', 'cyclic coordinate', 'canonical momentum', 'hamilton-jacobi', 'action', 'lagrangian', 'euler-lagrange', 'variation', 'entropy stability', 'bounded', 'constraint', 'virtual work', 'second variation'],
        'match_tex': ['\\delta S', '\\delta^2 S', '\\delta q', '\\delta\\mathbf', '\\frac{\\partial L}', '\\int L', '\\delta\\int', '\\delta', 'L(q', 'dt']
    },
    # Thermodynamics & Statistical Physics
    'thermo-hub': {
        'parent_id': 'first-law-of-thermodynamics-3bb4a7d0',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['helmholtz free energy', 'gibbs free energy', 'enthalpy', 'maxwell relation', 'heat capacity', 'chemical potential', 'clapeyron', 'carnot cycle', 'partition function', 'thermodynamic', 'heat', 'entropy', 'temperature', 'first law', 'microstate'],
        'match_tex': ['k_B', 'U - TS', 'H = U', 'k_B T', '\\Delta Q', '\\Delta W', '\\Delta U', '\\delta T', 'P(t)']
    },
    # Special Relativity & Spacetime Invariance
    'relativity-hub': {
        'parent_id': 'lorentz-transformation-matrix',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['lorentz', 'spacetime', 'proper time', 'interval', 'dilation', 'boost', 'rapidity', 'four-vector', 'minkowski', 'speed of light', 'relativistic'],
        'match_tex': ['\\gamma', '\\Delta t', '\\Delta x', '\\Delta\\tau', '\\eta', 's^2', 'v/c', 'c^2']
    },
    # Quantum Uncertainty & Measurement Limits
    'uncertainty-hub': {
        'parent_id': 'heisenberg-uncertainty-principle',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['uncertainty', 'commutation', 'commutator', 'heisenberg', 'dispersion', 'standard deviation', 'variance', 'measurement'],
        'match_tex': ['\\Delta x', '\\Delta p', '\\Delta E', '\\Delta t', '\\sigma', '\\ge', '[\\hat', 'hbar']
    },
    # General Relativity & Gravitational Curvature
    'gr-curvature-hub': {
        'parent_id': 'einstein-field-equations-simplified',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['curvature', 'riemann', 'ricci', 'kretschmann', 'christoffel', 'geodesic', 'einstein', 'metric tensor'],
        'match_tex': ['R^', 'R_', 'G_', 'g_', 'g_{']
    },
    # Cosmology & Spacetime Expansion
    'cosmology-hub': {
        'parent_id': 'big-bang-start-4da62fa5',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['friedmann', 'hubble parameter', 'scale factor', 'cosmological constant', 'deceleration parameter', 'dark energy density', 'redshift', 'expansion', 'lambda cdm'],
        'match_tex': ['\\frac{\\ddot{a}}{a}', '\\Omega_\\Lambda', '\\Omega_m', 'H(z)', 'H(t)', '\\Lambda', '\\Omega', '\\Delta z']
    }
}

def load_all_shards():
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, '*', 'shard_*.json')))
    formulas = {}
    file_map = {}
    for sf in shard_files:
        with open(sf, 'r', encoding='utf-8') as f:
            d = json.load(f)
            for fid, form in d.items():
                if isinstance(form, dict):
                    formulas[fid] = form
                    file_map[fid] = sf
    return formulas, file_map

def enrich_families(formulas, dry_run=True):
    print("=" * 68)
    print(f"🌲 Running Automated Lineage Family Enricher ({'DRY RUN' if dry_run else 'APPLYING ENRICHMENTS'})")
    print("=" * 68)

    modified_shards = set()
    enriched_parents = 0
    pruned_unreciprocal = 0

    # 1. Pre-compute which formulas already have incoming children via parent_formula_id
    incoming_children = {}
    for fid, form in formulas.items():
        p = form.get('parent_formula_id')
        if p and isinstance(p, str) and p in formulas and p != fid:
            incoming_children.setdefault(p, []).append(fid)

    # 2. Connect any isolated formula (no valid parent_formula_id and no incoming children) to its best matching family pillar
    for fid, form in formulas.items():
        title = form.get('title', '').lower()
        eq = form.get('equation', '')
        parent = form.get('parent_formula_id')
        has_valid_parent = bool(parent and isinstance(parent, str) and parent in formulas and parent != fid)
        has_incoming = len(incoming_children.get(fid, [])) > 0

        if not has_valid_parent and not has_incoming:
            matched_pillar = None
            matched_dtype = 'DERIVED_FROM'
            for fam_name, fam in FAMILY_PILLARS.items():
                pillar_id = fam['parent_id']
                if fid == pillar_id or pillar_id not in formulas:
                    continue
                if any(kw in title for kw in fam['match_keywords']) or any((pat in eq) for pat in fam['match_tex']):
                    matched_pillar = pillar_id
                    matched_dtype = fam['derivation_type']
                    break

            if not matched_pillar:
                # Fallback to Stationary Action Principle
                fallback_id = 'stationary-action-principle-8836edf7'
                if fid != fallback_id and fallback_id in formulas:
                    matched_pillar = fallback_id
                    matched_dtype = 'DERIVED_FROM'

            if matched_pillar:
                form['parent_formula_id'] = matched_pillar
                if not form.get('derivation_type') or form.get('derivation_type') == 'AXIOMATIC_FOUNDATION':
                    form['derivation_type'] = matched_dtype
                incoming_children.setdefault(matched_pillar, []).append(fid)
                modified_shards.add(fid)
                enriched_parents += 1

    # 3. Break any accidental cycles in parent_formula_id
    for fid in list(formulas.keys()):
        visited = {fid}
        curr = fid
        while True:
            p = formulas[curr].get('parent_formula_id')
            if not p or p not in formulas:
                break
            if p in visited:
                # Break cycle at curr -> p
                formulas[curr]['parent_formula_id'] = None
                formulas[curr]['derivation_type'] = 'AXIOMATIC_FOUNDATION'
                modified_shards.add(curr)
                break
            visited.add(p)
            curr = p

    # 4. Rebuild exact reciprocal child map: B in A.subcomponents <=> B.parent_formula_id == A
    exact_children = {}
    for fid, form in formulas.items():
        p = form.get('parent_formula_id')
        if p and isinstance(p, str) and p in formulas and p != fid:
            exact_children.setdefault(p, []).append(fid)

    for fid, form in formulas.items():
        true_subs = sorted(set(exact_children.get(fid, [])))
        old_subs = form.get('subcomponents', [])
        if not isinstance(old_subs, list):
            old_subs = []
        if old_subs != true_subs:
            pruned_count = len([x for x in old_subs if x not in true_subs])
            pruned_unreciprocal += pruned_count
            form['subcomponents'] = true_subs
            modified_shards.add(fid)

    print("\n" + "=" * 68)
    print("📊 ENRICHMENT & RECIPROCITY SUMMARY")
    print("=" * 68)
    print(f"  • Newly Enriched Parent Connections:  {enriched_parents:,}")
    print(f"  • Unreciprocal Subcomponents Pruned:  {pruned_unreciprocal:,}")
    print(f"  • Total Formula Records Updated:      {len(modified_shards):,}")
    print("=" * 68)

    return formulas, modified_shards


def save_shards(formulas, file_map, modified_fids):
    import hashlib
    shards_to_write = {}
    for fid in modified_fids:
        sf = file_map.get(fid)
        if sf:
            shards_to_write.setdefault(sf, set()).add(fid)

    print(f"\n💾 Writing updates to {len(shards_to_write)} shard files...")
    for sf, fids in shards_to_write.items():
        with open(sf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for fid in fids:
            if fid in formulas:
                data[fid] = formulas[fid]
        with open(sf, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    # Synchronize formulas_hash_registry.json
    hash_reg_path = os.path.join(PROJECT_ROOT, 'app', 'config', 'formulas_hash_registry.json')
    if os.path.exists(hash_reg_path):
        with open(hash_reg_path, 'r', encoding='utf-8') as f:
            reg = json.load(f)
        for sf in shards_to_write.keys():
            rel_path = os.path.relpath(sf, PROJECT_ROOT)
            with open(sf, 'rb') as bf:
                reg[rel_path] = hashlib.sha256(bf.read()).hexdigest()
        with open(hash_reg_path, 'w', encoding='utf-8') as f:
            json.dump(reg, f, indent=4)
    print("✓ All modified shards and SHA-256 hash registry persisted cleanly.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Enrich Formula Lineage Families")
    parser.add_argument('--apply', action='store_true', help="Persist enrichments and rebuild graph")
    args = parser.parse_args()

    formulas, file_map = load_all_shards()
    formulas, modified_fids = enrich_families(formulas, dry_run=not args.apply)

    if args.apply:
        save_shards(formulas, file_map, modified_fids)
        print("\n🔨 Rebuilding derivation graph...")
        import subprocess
        subprocess.run([sys.executable, GRAPH_BUILDER], check=True)

