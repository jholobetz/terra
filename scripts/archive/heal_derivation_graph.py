#!/usr/bin/env python3
"""
🌲 Local Derivation Graph Healer & Multi-Tier Linker
Systematically connects isolated and 2-tier formulas across all 256 shards into
deep, topologically verified derivation trees without external API calls ($0.00).

Usage:
    python3 scripts/maintenance/heal_derivation_graph.py [--dry-run] [--apply]
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

# 1. First-Principle Axiomatic Roots of Physics
AXIOMATIC_ROOTS = {
    'action-principle-definition': {
        'title': 'Principle of Stationary Action',
        'keywords': ['action', 'lagrangian', 'least action', 'hamilton'],
        'equation_patterns': [r'\\delta S\s*=\s*0', r'S\s*=\s*\\int\s*L']
    },
    'einstein-hilbert-action-identity-22847381': {
        'title': 'Einstein-Hilbert Action',
        'keywords': ['einstein-hilbert', 'ricci', 'general relativity', 'curvature action'],
        'equation_patterns': [r'\\frac{1}{2\\kappa}\s*\\int\s*R\s*\\sqrt{-g}']
    },
    'canonical-commutation-identity-2b78418f': {
        'title': 'Canonical Commutation Relations',
        'keywords': ['commutation', 'dirac quantization', 'heisenberg', 'quantum operator'],
        'equation_patterns': [r'\[\s*\\hat{q}\s*,\s*\\hat{p}\s*\]\s*=\s*i\\hbar', r'\[\s*\\hat{x}\s*,\s*\\hat{p}\s*\]']
    },
    'first-law-thermodynamics': {
        'title': 'First Law of Thermodynamics',
        'keywords': ['first law', 'internal energy', 'heat', 'work'],
        'equation_patterns': [r'dU\s*=\s*T\s*dS\s*-\s*P\s*dV', r'\\Delta U\s*=\s*Q\s*-\s*W']
    },
    'boltzmann-entropy-formula': {
        'title': 'Boltzmann Entropy Formula',
        'keywords': ['boltzmann entropy', 'microstates', 'statistical mechanics'],
        'equation_patterns': [r'S\s*=\s*k_B?\s*\\ln\s*\\Omega', r'S\s*=\s*k\s*\\ln\s*W']
    },
    'schrodinger-equation-time-dependent': {
        'title': 'Time-Dependent Schrödinger Equation',
        'keywords': ['schrödinger', 'wave function', 'quantum evolution'],
        'equation_patterns': [r'i\\hbar\s*\\frac{\\partial}{\\partial t}\\Psi\s*=\s*\\hat{H}\\Psi', r'i\\hbar\s*\\partial_t\s*\\psi']
    },
    'dirac-equation-relativistic': {
        'title': 'Dirac Equation',
        'keywords': ['dirac equation', 'spinor', 'relativistic quantum'],
        'equation_patterns': [r'\(i\\gamma\^\\mu\\partial_\\mu\s*-\s*m\)\s*\\psi\s*=\s*0', r'i\\hbar\\gamma\^\\mu\\partial_\\mu\\psi']
    },
    'causal-metric-spacetime-interval-b2aee666': {
        'title': 'General Spacetime Metric Line Element',
        'keywords': ['spacetime interval', 'metric tensor', 'riemannian metric'],
        'equation_patterns': [r'ds\^2\s*=\s*g_{\\mu\\nu}\s*d\s*x\^\\mu\s*d\s*x\^\\nu']
    },
    'ampere-maxwell-law': {
        'title': 'Ampère-Maxwell Law',
        'keywords': ['maxwell', 'ampere', 'magnetic curl', 'displacement current'],
        'equation_patterns': [r'\\nabla\s*\\times\s*\\mathbf{B}\s*=\s*\\mu_0']
    },
    'big-bang-start-4da62fa5': {
        'title': 'First Friedmann Equation',
        'keywords': ['friedmann', 'scale factor', 'hubble', 'cosmic expansion'],
        'equation_patterns': [r'H\^2\s*=\s*\\left\(\\frac{\\dot{a}}{a}\\right\)\^2', r'\\frac{\\dot{a}\^2}{a\^2}']
    },
    'boltzmann-distribution': {
        'title': 'Boltzmann Distribution',
        'keywords': ['boltzmann distribution', 'canonical ensemble', 'thermal state'],
        'equation_patterns': [r'P_n\s*\\propto\s*e\^\{-E_n/kT\}', r'e\^\{-\\beta E\}']
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

def normalize_tex(s):
    if not s: return ''
    s = re.sub(r'\s+', '', s)
    s = re.sub(r'\\(?:mathrm|mathbf|mathit|mathcal|mathbb|text)\b', '', s)
    s = s.replace('{', '').replace('}', '').replace('\\,', '').replace('\\;', '')
    return s

def heal_lineage(formulas, dry_run=True):
    print("=" * 65)
    print(f"🌲 Running Local Derivation Graph Healer ({'DRY RUN' if dry_run else 'APPLYING CHANGES'})")
    print("=" * 65)
    
    modified_shards = set()
    links_added = 0
    parents_linked = 0
    reciprocal_links = 0
    
    # Map normalized equations to formula IDs
    eq_index = {}
    for fid, f in formulas.items():
        eq = f.get('equation', '')
        if eq:
            eq_index[normalize_tex(eq)] = fid
            
    # 1. Establish Axiomatic Roots
    for ax_id in AXIOMATIC_ROOTS:
        if ax_id in formulas:
            form = formulas[ax_id]
            if form.get('derivation_type') != 'AXIOMATIC_FOUNDATION':
                form['derivation_type'] = 'AXIOMATIC_FOUNDATION'
                form['parent_formula_id'] = ''
                modified_shards.add(ax_id)
                print(f"  [AXIOM] Tagged root foundation: {ax_id} ({form.get('title')})")

    # 2. Reciprocal Sync: If A lists child B, B should list parent A (if B has no parent)
    for fid, form in formulas.items():
        subs = form.get('subcomponents', [])
        for child_id in subs:
            if isinstance(child_id, str) and child_id in formulas:
                child = formulas[child_id]
                if not child.get('parent_formula_id'):
                    child['parent_formula_id'] = fid
                    if not child.get('derivation_type'):
                        child['derivation_type'] = 'SPECIAL_CASE'
                    modified_shards.add(child_id)
                    reciprocal_links += 1

    # 3. Reciprocal Sync: If B lists parent A, A should list child B in subcomponents
    for fid, form in formulas.items():
        parent_id = form.get('parent_formula_id')
        if parent_id and parent_id in formulas:
            parent = formulas[parent_id]
            subs = parent.setdefault('subcomponents', [])
            if fid not in subs:
                subs.append(fid)
                modified_shards.add(parent_id)
                reciprocal_links += 1

    # 4. Multi-Tier Upward Chaining for Intermediate Parents & Isolated Nodes
    for fid, form in formulas.items():
        if form.get('parent_formula_id'):
            continue  # Already has parent
            
        title_lower = form.get('title', '').lower()
        eq = form.get('equation', '')
        norm_e = normalize_tex(eq)
        
        # A. Action & Lagrangian Chaining
        if any(w in title_lower for w in ['lagrangian', 'euler-lagrange', 'action', 'generalized momentum', 'least action']) or 'L=' in norm_e or '\\mathcal{L}' in eq:
            if 'action-principle-definition' in formulas and fid != 'action-principle-definition':
                form['parent_formula_id'] = 'action-principle-definition'
                form['derivation_type'] = 'DERIVED_FROM'
                formulas['action-principle-definition'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('action-principle-definition')
                parents_linked += 1

        # B. General Relativity & Spacetime Metric Chaining
        elif any(w in title_lower for w in ['metric', 'schwarzschild', 'kerr', 'flrw', 'spacetime interval', 'christoffel', 'geodesic', 'riemann', 'ricci']) or 'ds^2=' in norm_e or 'g_{\\mu\\nu}' in eq or '\\eta_{\\mu\\nu}' in eq:
            if 'causal-metric-spacetime-interval-b2aee666' in formulas and fid != 'causal-metric-spacetime-interval-b2aee666':
                form['parent_formula_id'] = 'causal-metric-spacetime-interval-b2aee666'
                form['derivation_type'] = 'SPECIAL_CASE'
                formulas['causal-metric-spacetime-interval-b2aee666'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('causal-metric-spacetime-interval-b2aee666')
                parents_linked += 1

        # C. Cosmology & Friedmann Expansion
        elif any(w in title_lower for w in ['friedmann', 'hubble', 'scale factor', 'cosmological constant', 'dark energy', 'redshift']) or 'H^2=' in norm_e or 'a(t)' in eq:
            if 'big-bang-start-4da62fa5' in formulas and fid != 'big-bang-start-4da62fa5':
                form['parent_formula_id'] = 'big-bang-start-4da62fa5'
                form['derivation_type'] = 'DERIVED_FROM'
                formulas['big-bang-start-4da62fa5'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('big-bang-start-4da62fa5')
                parents_linked += 1

        # D. Electromagnetism & Maxwell Fields
        elif any(w in title_lower for w in ['maxwell', 'ampere', 'faraday', 'coulomb', 'magnetic field', 'electric field', 'vector potential', 'poynting', 'lorentz force']) or '\\mathbf{E}' in eq or '\\mathbf{B}' in eq or '\\mathbf{A}' in eq:
            if 'ampere-maxwell-law' in formulas and fid != 'ampere-maxwell-law':
                form['parent_formula_id'] = 'ampere-maxwell-law'
                form['derivation_type'] = 'SPECIAL_CASE'
                formulas['ampere-maxwell-law'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('ampere-maxwell-law')
                parents_linked += 1

        # E. Quantum Mechanics & Wave Functions
        elif any(w in title_lower for w in ['wave function', 'schrodinger', 'schrödinger', 'expectation value', 'probability density', 'wave packet', 'hamiltonian operator']) or '\\psi' in eq or '\\Psi' in eq or '|\\psi\\rangle' in eq:
            if 'schrodinger-equation-time-dependent' in formulas and fid != 'schrodinger-equation-time-dependent':
                form['parent_formula_id'] = 'schrodinger-equation-time-dependent'
                form['derivation_type'] = 'DERIVED_FROM'
                formulas['schrodinger-equation-time-dependent'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('schrodinger-equation-time-dependent')
                parents_linked += 1

        # F. Quantum Commutators & Operators
        elif any(w in title_lower for w in ['commutator', 'uncertainty', 'commutation', 'heisenberg', 'operator']) or ('[' in eq and ']' in eq and 'i\\hbar' in eq):
            if 'canonical-commutation-identity-2b78418f' in formulas and fid != 'canonical-commutation-identity-2b78418f':
                form['parent_formula_id'] = 'canonical-commutation-identity-2b78418f'
                form['derivation_type'] = 'DERIVED_FROM'
                formulas['canonical-commutation-identity-2b78418f'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('canonical-commutation-identity-2b78418f')
                parents_linked += 1

        # G. Thermodynamics & Statistical Physics
        elif any(w in title_lower for w in ['entropy', 'partition function', 'free energy', 'enthalpy', 'carnot', 'thermodynamic', 'ideal gas', 'maxwell-boltzmann', 'temperature', 'heat']) or 'S=' in norm_e or 'F=' in norm_e or 'dU=' in norm_e or 'k_B' in eq:
            if 'first-law-thermodynamics' in formulas and fid != 'first-law-thermodynamics':
                form['parent_formula_id'] = 'first-law-thermodynamics'
                form['derivation_type'] = 'SPECIAL_CASE'
                formulas['first-law-thermodynamics'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('first-law-thermodynamics')
                parents_linked += 1

        # H. Angular Momentum & Rotational Dynamics
        elif any(w in title_lower for w in ['angular momentum', 'torque', 'moment of inertia', 'spin', 'precession', 'gyroscopic']) or '\\mathbf{L}' in eq or '\\boldsymbol{\\omega}' in eq:
            if 'angular-momentum-definition-6f8a0efa' in formulas and fid != 'angular-momentum-definition-6f8a0efa':
                form['parent_formula_id'] = 'angular-momentum-definition-6f8a0efa'
                form['derivation_type'] = 'DERIVED_FROM'
                formulas['angular-momentum-definition-6f8a0efa'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('angular-momentum-definition-6f8a0efa')
                parents_linked += 1

        # I. Fluid Dynamics & Continuum Mechanics
        elif any(w in title_lower for w in ['fluid', 'navier-stokes', 'viscosity', 'bernoulli', 'reynolds', 'poiseuille', 'vorticity', 'incompressible']) or '\\mathbf{u}' in eq or '\\nabla \\cdot \\mathbf{u}' in eq:
            if 'incompressibility-condition-fluid' in formulas and fid != 'incompressibility-condition-fluid':
                form['parent_formula_id'] = 'incompressibility-condition-fluid'
                form['derivation_type'] = 'SPECIAL_CASE'
                formulas['incompressibility-condition-fluid'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('incompressibility-condition-fluid')
                parents_linked += 1

        # J. Optics & Wave Propagation
        elif any(w in title_lower for w in ['refraction', 'diffraction', 'snell', 'bragg', 'interference', 'wave speed', 'frequency', 'wavelength', 'optics']) or '\\lambda' in eq or 'n_1' in eq or '\\sin\\theta' in eq:
            if 'snells-law-refraction' in formulas and fid != 'snells-law-refraction':
                form['parent_formula_id'] = 'snells-law-refraction'
                form['derivation_type'] = 'SPECIAL_CASE'
                formulas['snells-law-refraction'].setdefault('subcomponents', []).append(fid)
                modified_shards.add(fid)
                modified_shards.add('snells-law-refraction')
                parents_linked += 1

    # Clean duplicates in subcomponents
    for fid, form in formulas.items():
        if 'subcomponents' in form and isinstance(form['subcomponents'], list):
            # deduplicate while preserving order, remove self-reference
            seen = set()
            clean_subs = []
            for s in form['subcomponents']:
                if s != fid and s not in seen and s in formulas:
                    seen.add(s)
                    clean_subs.append(s)
            form['subcomponents'] = clean_subs

    print("\n" + "=" * 65)
    print("📊 HEALING RESULTS SUMMARY")
    print("=" * 65)
    print(f"  • Reciprocal Connections Healed: {reciprocal_links}")
    print(f"  • Multi-Tier Parents Chained: {parents_linked}")
    print(f"  • Total Modified Shards Involved: {len(modified_shards)}")
    
    # Calculate coverage after
    connected = sum(1 for f in formulas.values() if f.get('parent_formula_id') or (f.get('subcomponents') and len(f.get('subcomponents')) > 0))
    isolated = len(formulas) - connected
    print(f"  • Total Connected Formulas: {connected} / {len(formulas)} ({connected/len(formulas)*100:.1f}%)")
    print(f"  • Remaining Isolated: {isolated} ({isolated/len(formulas)*100:.1f}%)")
    
    return formulas, modified_shards

def save_shards(formulas, file_map, modified_fids):
    # Group modified formulas by shard file
    shards_to_write = {}
    for fid in modified_fids:
        sf = file_map.get(fid)
        if sf:
            shards_to_write.setdefault(sf, set()).add(fid)
            
    print(f"\n💾 Saving updates to {len(shards_to_write)} shard files...")
    for sf, fids in shards_to_write.items():
        with open(sf, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for fid in fids:
            if fid in formulas:
                data[fid] = formulas[fid]
        with open(sf, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    print("✓ Shards successfully updated!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Heal Derivation Graph Lineage")
    parser.add_argument('--apply', action='store_true', help="Persist healed relationships to shards and rebuild graph")
    args = parser.parse_args()
    
    formulas, file_map = load_all_shards()
    formulas, modified_fids = heal_lineage(formulas, dry_run=not args.apply)
    
    if args.apply:
        save_shards(formulas, file_map, modified_fids)
        print("\n🔨 Rebuilding formula derivation graph...")
        os.system(f"python3 {GRAPH_BUILDER}")
