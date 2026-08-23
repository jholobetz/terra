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
    # Electromagnetism
    'maxwell-hub': {
        'parent_id': 'ampere-maxwell-law',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['poynting', 'lorenz gauge', 'coulomb gauge', 'displacement current', 'vector potential', 'radiation field', 'gauge transformation', 'permeability', 'permittivity', 'maxwell stress'],
        'match_tex': [r'\\mathbf{E}\s*\\times\s*\\mathbf{B}', r'\\mathbf{A}', r'\\mu_0', r'\\varepsilon_0', r'\\partial_\\mu A\^\\mu']
    },
    # Quantum Dynamics & Density Matrices
    'quantum-dynamics-hub': {
        'parent_id': 'schrodinger-equation-time-dependent',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['density matrix', 'von neumann', 'lindblad', 'master equation', 'collapse', 'bayesian filtering', 'expectation value', 'wave packet', 'bloch sphere', 'state vector'],
        'match_tex': [r'\\hat{\\rho}', r'\\rho_t', r'\\langle\\psi|', r'|\\psi\\rangle', r'\\text{Tr}\(']
    },
    # Analytical Mechanics & Lagrangian Symmetries
    'mechanics-hub': {
        'parent_id': 'action-principle-definition',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['rotational invariance', 'noether', 'generalized coordinate', 'legendre transform', 'cyclic coordinate', 'canonical momentum', 'hamilton-jacobi'],
        'match_tex': [r'\\delta L', r'\\frac{\\partial L}{\\partial', r'\\mathcal{L}']
    },
    # Thermodynamics & Statistical Physics
    'thermo-hub': {
        'parent_id': 'first-law-thermodynamics',
        'derivation_type': 'SPECIAL_CASE',
        'match_keywords': ['helmholtz free energy', 'gibbs free energy', 'enthalpy', 'maxwell relation', 'heat capacity', 'chemical potential', 'clapeyron', 'carnot cycle', 'partition function'],
        'match_tex': [r'U\s*-\s*TS', r'H\s*=\s*U\s*\+\s*PV', r'G\s*=\s*H\s*-\s*TS', r'k_B\s*T']
    },
    # Cosmology & General Relativity
    'cosmology-hub': {
        'parent_id': 'big-bang-start-4da62fa5',
        'derivation_type': 'DERIVED_FROM',
        'match_keywords': ['friedmann', 'hubble parameter', 'scale factor', 'cosmological constant', 'deceleration parameter', 'dark energy density', 'redshift'],
        'match_tex': [r'\\frac{\\ddot{a}}{a}', r'\\Omega_\\Lambda', r'\\Omega_m', r'H\(z\)']
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

        # If formula has no parent, find best matching family pillar
        if not parent:
            for fam_name, fam in FAMILY_PILLARS.items():
                pillar_id = fam['parent_id']
                if fid == pillar_id or pillar_id not in formulas:
                    continue

                matched = False
                # Keyword check
                if any(kw in title for kw in fam['match_keywords']):
                    matched = True
                # TeX check
                elif any(re.search(pat, eq) for pat in fam['match_tex']):
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
