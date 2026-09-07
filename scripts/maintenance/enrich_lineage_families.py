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
    enriched_children = 0

    for fid, form in formulas.items():
        title = form.get('title', '').lower()
        eq = form.get('equation', '')
        parent = form.get('parent_formula_id')

        # If formula has no valid parent in formula registry or is an isolated 'Axiom', find best matching family pillar
        needs_parent = (not parent) or (parent == 'Axiom' and not form.get('subcomponents'))
        if needs_parent:
            for fam_name, fam in FAMILY_PILLARS.items():
                pillar_id = fam['parent_id']
                if fid == pillar_id or pillar_id not in formulas:
                    continue

                matched = False
                # Keyword check
                if any(kw in title for kw in fam['match_keywords']):
                    matched = True
                # TeX check (substring or regex)
                elif any((pat in eq) for pat in fam['match_tex']):
                    matched = True

                if matched:
                    form['parent_formula_id'] = pillar_id
                    form['derivation_type'] = fam['derivation_type']
                    formulas[pillar_id].setdefault('subcomponents', []).append(fid)
                    modified_shards.add(fid)
                    modified_shards.add(pillar_id)
                    enriched_parents += 1
                    break

    # Reciprocal child cleanup & deduplication
    for fid, form in formulas.items():
        if 'subcomponents' in form and isinstance(form['subcomponents'], list):
            seen = set()
            clean_subs = []
            for s in form['subcomponents']:
                if s != fid and s not in seen and s in formulas:
                    seen.add(s)
                    clean_subs.append(s)
            if len(clean_subs) != len(form['subcomponents']):
                form['subcomponents'] = clean_subs
                modified_shards.add(fid)

    print("\n" + "=" * 68)
    print("📊 ENRICHMENT SUMMARY")
    print("=" * 68)
    print(f"  • Newly Enriched Parent Connections: {enriched_parents}")
    print(f"  • Total Shards Impacted: {len(modified_shards)}")
    print("=" * 68)

    return formulas, modified_shards

def save_shards(formulas, file_map, modified_fids):
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
    print("✓ All modified shards persisted cleanly.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Enrich Formula Lineage Families")
    parser.add_argument('--apply', action='store_true', help="Persist enrichments and rebuild graph")
    args = parser.parse_args()

    formulas, file_map = load_all_shards()
    formulas, modified_fids = enrich_families(formulas, dry_run=not args.apply)

    if args.apply:
        save_shards(formulas, file_map, modified_fids)
        print("\n🔨 Rebuilding derivation graph...")
        os.system(f"python3 {GRAPH_BUILDER}")
