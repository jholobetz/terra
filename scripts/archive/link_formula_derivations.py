#!/usr/bin/env python3
"""
🌲 Automated Formula Derivation Tree & Lineage Linker
Connects isolated and newly ingested formulas to authoritative parent formulas
within their corresponding subtopic manifolds, eliminating orphans and boosting LHI.
"""

import os
import glob
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTENT_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content')
FORMULAS_DIR = os.path.join(CONTENT_DIR, 'formulas')

def run_derivation_linking():
    print("====================================================================")
    print("🌲 TERRA PHYSICS LAB - FORMULA LINEAGE & DERIVATION LINKER")
    print("====================================================================\n")

    # 1. Load Subtopic to Formula mapping
    print("[INFO] Loading subtopic formula maps...")
    topic_files = [
        'classical-mechanics.json', 'electromagnetism.json', 'relativity.json',
        'quantum-physics.json', 'thermodynamics-statistical-mechanics.json',
        'standard-model.json', 'astrophysics.json', 'theoretical-physics.json',
        'philosophy-of-physics.json', 'mathematical-methods.json',
        'condensed-matter.json', 'fluids-nonlinear.json'
    ]

    subtopic_to_primary_formula = {}
    for tf in topic_files:
        path = os.path.join(CONTENT_DIR, tf)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for slug, sub in data.items():
                if isinstance(sub, dict):
                    f_ids = sub.get('formula_ids', [])
                    if f_ids:
                        # The first non-axiom formula is considered the primary parent anchor for this subtopic
                        subtopic_to_primary_formula[slug] = f_ids[0]

    print(f"[INFO] Indexed primary parent anchors for {len(subtopic_to_primary_formula)} subtopics.\n")

    # 2. Load all Shard Formulas
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, '*', 'shard_*.json')))
    all_formulas = {}
    formula_shard_map = {}

    for sf in shard_files:
        with open(sf, 'r', encoding='utf-8') as f:
            d = json.load(f)
        for fid, f_data in d.items():
            if isinstance(f_data, dict):
                all_formulas[fid] = f_data
                formula_shard_map[fid] = sf

    print(f"[INFO] Loaded {len(all_formulas)} total formulas across {len(shard_files)} shards.\n")

    # 3. Connect Isolated Formulas to Canonical Parents
    linked_count = 0
    shards_to_save = set()

    for fid, f_data in all_formulas.items():
        is_isolated = (f_data.get('parent_formula_id') in ['Axiom', None, ''] and len(f_data.get('subcomponents', [])) == 0)
        if not is_isolated:
            continue

        # Extract base slug prefix from formula ID (e.g. 'minimal-coupling-identity-...' -> 'minimal-coupling')
        slug_match = re.match(r'^([a-z0-9\-]+)-(?:identity|scalar|vector|relation|tensor)-[a-f0-9]{8}$', fid)
        if not slug_match:
            slug_match = re.match(r'^([a-z0-9\-]+)-[a-f0-9]{8}$', fid)

        candidate_slug = slug_match.group(1) if slug_match else None
        
        parent_id = None
        if candidate_slug and candidate_slug in subtopic_to_primary_formula:
            parent_id = subtopic_to_primary_formula[candidate_slug]
        
        # Fallback: check if candidate_slug itself is an existing formula
        if not parent_id and candidate_slug and candidate_slug in all_formulas and candidate_slug != fid:
            parent_id = candidate_slug

        if parent_id and parent_id != fid and parent_id in all_formulas:
            f_data['parent_formula_id'] = parent_id
            f_data['derivation_type'] = 'THEORETICAL_DERIVATION'
            
            # Add child to parent's subcomponents
            parent_data = all_formulas[parent_id]
            if 'subcomponents' not in parent_data or not isinstance(parent_data['subcomponents'], list):
                parent_data['subcomponents'] = []
            
            if fid not in parent_data['subcomponents']:
                parent_data['subcomponents'].append(fid)
                shards_to_save.add(formula_shard_map[parent_id])

            shards_to_save.add(formula_shard_map[fid])
            linked_count += 1

    print(f"[SUCCESS] Linked {linked_count} isolated formulas to canonical parent anchors!\n")

    # 4. Save Modified Shards
    print(f"[INFO] Writing updates to {len(shards_to_save)} modified shards...")
    for sf in shards_to_save:
        with open(sf, 'r', encoding='utf-8') as f:
            shard_dict = json.load(f)
        
        # Update in-memory modifications into shard dictionary
        for fid in shard_dict:
            if fid in all_formulas:
                shard_dict[fid] = all_formulas[fid]
                
        with open(sf, 'w', encoding='utf-8') as f:
            json.dump(shard_dict, f, indent=4, ensure_ascii=False)

    print("[OK] Shard updates complete!\n")

if __name__ == '__main__':
    run_derivation_linking()
