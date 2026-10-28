#!/usr/bin/env python3
"""
🌲 Subtopic-Grounded & Anti-Goodhart Lineage Rebalancer for Terra Physics Lab
Enforces Intellectual Honesty and Structural Rigor (docs/mandate.md & docs/unfuckit.md):
  1. Zero single-token regex auto-parenting and zero catch-all fallback hubs.
  2. Fixes upstream inversions on core master laws (e.g., TDSE, Continuity, Friedmann).
  3. De-packs overloaded star hubs (> 20 children) into subtopic-authentic local
     hierarchies, shared-variable domain sub-branches, or honest root definitions.
  4. Enforces loop-free DAG ancestry and exact parent <-> subcomponents reciprocity.
  5. Reports Mandatory Extreme-Tail & Random Spot Checks (Safeguard #4).

Usage:
    .venv/bin/python3 scripts/maintenance/enrich_lineage_families.py [--dry-run] [--apply]
"""

import os
import sys
import json
import glob
import random
import argparse
from collections import Counter, defaultdict

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
CONTENT_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content')
GRAPH_BUILDER = os.path.join(PROJECT_ROOT, 'scripts', 'build_formula_graph.py')

MAX_CHILDREN_CAP = 18

VALID_DERIVATION_TYPES = {
    'AXIOMATIC_FOUNDATION',
    'DERIVED_FROM',
    'SPECIAL_CASE',
    'LIMITING_CASE',
    'APPROXIMATION',
    'DEFINITION',
    'THEORETICAL_DERIVATION',
    'GENERALIZATION',
}

CURATED_TDSE_KEEP = {
    'time-independent-schrodinger-equation',
    'probability-continuity-equation-4c9de9fa',
    'time-evolution-of-expectation-value',
    'quantum-time-evolution-operator-e717a9a3',
    'ensemble-expectation-trace-02d3c609',
    'wavefunction-position-space',
    'operator-expectation-value-a7c515e7',
    'born-rule-probability-14a3780a',
    'delta-normalization-relation-08f2e931',
    'probability-uniqueness-df884d2f',
    'group-velocity',
    'the-path-integral-ab6eacde',
    'energy-observable-c33d8980',
    'rectangular-barrier-transmission-216afbe1',
    'energy-momentum-recoil-balance-24e0aa53',
}

CURATED_UPSTREAM_FIXES = {
    'lagrangian-density-for-schrodinger-equation': ('stationary-action-principle-8836edf7', 'SPECIAL_CASE'),
    'time-dependent-schrodinger-equation': ('lagrangian-density-for-schrodinger-equation', 'DERIVED_FROM'),
    'probability-continuity-equation-4c9de9fa': ('time-dependent-schrodinger-equation', 'DERIVED_FROM'),
    'time-evolution-of-expectation-value': ('time-dependent-schrodinger-equation', 'DERIVED_FROM'),
    'quantum-time-evolution-operator-e717a9a3': ('time-dependent-schrodinger-equation', 'DERIVED_FROM'),
    'big-bang-start-4da62fa5': ('einstein-field-equations-simplified', 'DERIVED_FROM'),
    'taylor-expansion-mechanics-identity-1-9fffb077-1ccd2384': ('energy-hill-aac310fe', 'APPROXIMATION'),
    'angular-momentum-definition-6f8a0efa': ('newtons-second-law-momentum-form-38ff65b7', 'DEFINITION'),
    'torque-definition': ('angular-momentum-definition-6f8a0efa', 'DERIVED_FROM'),
}

GENERIC_VARS = {'t', 'x', 'y', 'z', 'r', 'n', 'i', 'j', 'k', 'm', 'c', 'v', 'a', 'f', 'g', 'N', 'V', 'T', 'E', 'p'}


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


def load_subtopic_topology(formulas):
    cat_file = os.path.join(CONTENT_DIR, 'categories.json')
    with open(cat_file, 'r', encoding='utf-8') as f:
        categories = json.load(f)

    formula_to_subtopics = defaultdict(list)
    subtopic_formulas = defaultdict(list)
    subtopic_parents = defaultdict(list)
    subtopic_domain = {}

    for cat_id in categories.keys():
        cat_path = os.path.join(CONTENT_DIR, f"{cat_id}.json")
        if not os.path.exists(cat_path):
            continue
        with open(cat_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for sub_id, sub in data.items():
            if not isinstance(sub, dict):
                continue
            subtopic_domain[sub_id] = cat_id
            subtopic_parents[sub_id] = [p for p in sub.get('parents', []) if isinstance(p, str)]
            fids = [fid for fid in sub.get('formula_ids', []) if isinstance(fid, str) and fid in formulas]
            for sec in sub.get('sections', []):
                if isinstance(sec, dict):
                    for fid in sec.get('formulas', []):
                        fid_s = fid if isinstance(fid, str) else (fid.get('id') if isinstance(fid, dict) else None)
                        if fid_s and fid_s in formulas and fid_s not in fids:
                            fids.append(fid_s)
            subtopic_formulas[sub_id] = fids
            for fid in fids:
                if sub_id not in formula_to_subtopics[fid]:
                    formula_to_subtopics[fid].append(sub_id)

    sorted_subs = sorted(subtopic_domain.keys(), key=len, reverse=True)
    for fid in formulas:
        if not formula_to_subtopics[fid]:
            for sub_id in sorted_subs:
                if fid.startswith(sub_id + '-'):
                    formula_to_subtopics[fid].append(sub_id)
                    if fid not in subtopic_formulas[sub_id]:
                        subtopic_formulas[sub_id].append(fid)
                    break

    return formula_to_subtopics, subtopic_formulas, subtopic_parents, subtopic_domain


def is_good_parent_candidate(fid, form):
    title = (form.get('title') or '').strip()
    eq = (form.get('equation') or '').strip()
    if not title or len(title) < 12:
        return False
    bad_titles = ('custom physical relation', 'no motion', 'identity', 'parameter', 'constant')
    if title.lower() in bad_titles or 'custom physical relation' in title.lower():
        return False
    if len(eq) < 10 or '=' not in eq:
        return False
    return True


def would_create_cycle(child_id, new_parent_id, parent_map):
    if not new_parent_id or child_id == new_parent_id:
        return True
    curr = new_parent_id
    visited = {child_id}
    steps = 0
    while curr and steps < 50:
        if curr in visited:
            return True
        visited.add(curr)
        curr = parent_map.get(curr)
        steps += 1
    return False


def get_var_symbols(form, specific_only=False):
    sv = form.get('semantic_variables')
    if isinstance(sv, dict):
        res = {k.strip() for k in sv.keys() if len(k.strip()) > 0}
        if specific_only:
            res = {k for k in res if k not in GENERIC_VARS}
        return res
    return set()


def normalize_derivation_type(dtype, has_parent):
    if dtype and isinstance(dtype, str) and dtype != 'UNDEFINED':
        return dtype
    return 'DERIVED_FROM' if has_parent else 'AXIOMATIC_FOUNDATION'


def enrich_families(formulas, dry_run=True):
    print("=" * 68)
    print(f"🌲 Running Subtopic-Grounded Lineage Rebalancer ({'DRY RUN' if dry_run else 'APPLYING UPDATES'})")
    print("=" * 68)

    formula_to_subtopics, subtopic_formulas, subtopic_parents, subtopic_domain = load_subtopic_topology(formulas)

    modified_shards = set()
    pruned_unreciprocal = 0
    stats = Counter()
    samples = defaultdict(list)

    parent_map = {}
    for fid, f in formulas.items():
        p = f.get('parent_formula_id')
        if isinstance(p, str) and p in formulas and p != fid:
            parent_map[fid] = p

    # 1. Apply Curated Upstream Inversion Fixes
    for cid, (new_p, new_dt) in CURATED_UPSTREAM_FIXES.items():
        if cid in formulas and new_p in formulas:
            effective_dt = formulas[cid].get('derivation_type') if formulas[cid].get('derivation_steps') else new_dt
            if formulas[cid].get('parent_formula_id') != new_p or formulas[cid].get('derivation_type') != effective_dt:
                formulas[cid]['parent_formula_id'] = new_p
                formulas[cid]['derivation_type'] = effective_dt
                parent_map[cid] = new_p
                modified_shards.add(cid)
                stats['curated_upstream_fixes'] += 1

    # 2. De-pack Overloaded Hubs (> MAX_CHILDREN_CAP children)
    child_map = defaultdict(list)
    for cid, pid in parent_map.items():
        child_map[pid].append(cid)

    overloaded = sorted(
        [p for p, ch in child_map.items() if len(ch) > 20],
        key=lambda p: len(child_map[p]),
        reverse=True
    )

    for hub_id in overloaded:
        children = list(child_map[hub_id])
        if len(children) <= MAX_CHILDREN_CAP:
            continue

        hub_subs = set(formula_to_subtopics.get(hub_id, []))
        hub_doms = {subtopic_domain.get(s) for s in hub_subs if s in subtopic_domain}
        hub_vars = get_var_symbols(formulas[hub_id])

        scored = []
        for cid in children:
            score = 0
            if hub_id == 'time-dependent-schrodinger-equation' and cid in CURATED_TDSE_KEEP:
                score += 100
            c_subs = set(formula_to_subtopics.get(cid, []))
            c_doms = {subtopic_domain.get(s) for s in c_subs if s in subtopic_domain}
            c_vars = get_var_symbols(formulas[cid])
            if c_subs & hub_subs:
                score += 20
            if c_doms & hub_doms:
                score += 10
            if len(child_map.get(cid, [])) > 0:
                score += 8
            score += min(5, len(c_vars & hub_vars))
            if is_good_parent_candidate(cid, formulas[cid]):
                score += 3
            scored.append((score, cid))

        scored.sort(key=lambda x: (-x[0], x[1]))
        keep_limit = 15 if hub_id == 'time-dependent-schrodinger-equation' else MAX_CHILDREN_CAP
        kept_ids = [cid for _, cid in scored[:keep_limit]]
        evicted_ids = [cid for _, cid in scored[keep_limit:]]

        child_map[hub_id] = kept_ids

        for cid in evicted_ids:
            reassigned = False
            c_subs = formula_to_subtopics.get(cid, [])
            c_doms = {subtopic_domain.get(s) for s in c_subs if s in subtopic_domain}
            c_vars = get_var_symbols(formulas[cid])

            # Strategy A: Best canonical formula in the same subtopic with < MAX_CHILDREN_CAP children
            best_sub_cand = None
            best_sub_score = -1
            for s in c_subs:
                for idx, cand in enumerate(subtopic_formulas.get(s, [])):
                    if cand != cid and cand != hub_id and len(child_map[cand]) < MAX_CHILDREN_CAP:
                        if is_good_parent_candidate(cand, formulas[cand]) and not would_create_cycle(cid, cand, parent_map):
                            cand_vars = get_var_symbols(formulas[cand])
                            sc = (10 if idx == 0 else 5) + len(c_vars & cand_vars) * 3 + (4 if len(child_map[cand]) > 0 else 0)
                            if sc > best_sub_score:
                                best_sub_score = sc
                                best_sub_cand = cand
            if best_sub_cand:
                parent_map[cid] = best_sub_cand
                formulas[cid]['parent_formula_id'] = best_sub_cand
                child_map[best_sub_cand].append(cid)
                modified_shards.add(cid)
                reassigned = True
                stats['A_same_subtopic'] += 1
                samples['A_same_subtopic'].append((cid, hub_id, best_sub_cand))

            # Strategy B: Best canonical formula in a parent subtopic from the subtopic knowledge graph
            if not reassigned:
                best_psub_cand = None
                best_psub_score = -1
                for s in c_subs:
                    for p_sub in subtopic_parents.get(s, []):
                        for idx, cand in enumerate(subtopic_formulas.get(p_sub, [])):
                            if cand != cid and cand != hub_id and len(child_map[cand]) < MAX_CHILDREN_CAP:
                                if is_good_parent_candidate(cand, formulas[cand]) and not would_create_cycle(cid, cand, parent_map):
                                    cand_vars = get_var_symbols(formulas[cand])
                                    sc = (10 if idx == 0 else 5) + len(c_vars & cand_vars) * 3
                                    if sc > best_psub_score:
                                        best_psub_score = sc
                                        best_psub_cand = cand
                if best_psub_cand:
                    parent_map[cid] = best_psub_cand
                    formulas[cid]['parent_formula_id'] = best_psub_cand
                    child_map[best_psub_cand].append(cid)
                    modified_shards.add(cid)
                    reassigned = True
                    stats['B_parent_subtopic'] += 1
                    samples['B_parent_subtopic'].append((cid, hub_id, best_psub_cand))

            # Strategy C: Push 1 hop down ONLY if child shares domain AND specific physical symbols with a kept canonical child
            if not reassigned:
                c_spec_vars = get_var_symbols(formulas[cid], specific_only=True)
                best_branch = None
                best_overlap = 0
                branch_pool = list(kept_ids)
                for k in kept_ids:
                    branch_pool.extend(child_map.get(k, []))
                for cand in branch_pool:
                    if cand != cid and cand != hub_id and len(child_map[cand]) < MAX_CHILDREN_CAP:
                        if not is_good_parent_candidate(cand, formulas[cand]):
                            continue
                        cand_subs = formula_to_subtopics.get(cand, [])
                        cand_doms = {subtopic_domain.get(s) for s in cand_subs if s in subtopic_domain}
                        if c_doms and cand_doms and not (c_doms & cand_doms):
                            continue
                        if not would_create_cycle(cid, cand, parent_map):
                            ov = len(c_spec_vars & get_var_symbols(formulas[cand], specific_only=True))
                            if ov >= 1 and (ov > best_overlap or (ov == best_overlap and best_branch and len(child_map[cand]) < len(child_map[best_branch]))):
                                best_overlap = ov
                                best_branch = cand
                if best_branch:
                    parent_map[cid] = best_branch
                    formulas[cid]['parent_formula_id'] = best_branch
                    child_map[best_branch].append(cid)
                    modified_shards.add(cid)
                    reassigned = True
                    stats['C_shared_var_subbranch'] += 1
                    samples['C_shared_var_subbranch'].append((cid, hub_id, best_branch))

            # Strategy D: Honest Root Node (DEFINITION / AXIOMATIC_FOUNDATION) — Never use a catch-all bucket!
            if not reassigned:
                parent_map.pop(cid, None)
                formulas[cid]['parent_formula_id'] = None
                new_dt = 'AXIOMATIC_FOUNDATION' if len(child_map.get(cid, [])) > 0 else 'DEFINITION'
                formulas[cid]['derivation_type'] = new_dt
                modified_shards.add(cid)
                stats['D_honest_root'] += 1
                samples['D_honest_root'].append((cid, hub_id, new_dt))

    # 3. Break any accidental cycles in parent_formula_id and normalize derivation_type
    for fid, form in formulas.items():
        visited = {fid}
        curr = fid
        while True:
            p = formulas[curr].get('parent_formula_id')
            if not p or p not in formulas:
                break
            if p in visited:
                formulas[curr]['parent_formula_id'] = None
                formulas[curr]['derivation_type'] = 'AXIOMATIC_FOUNDATION'
                modified_shards.add(curr)
                break
            visited.add(p)
            curr = p

        has_p = bool(form.get('parent_formula_id') and form.get('parent_formula_id') in formulas)
        norm_dt = normalize_derivation_type(form.get('derivation_type'), has_p)
        if form.get('derivation_type') != norm_dt:
            form['derivation_type'] = norm_dt
            modified_shards.add(fid)

    # 4. Rebuild exact reciprocal child map: B in A.subcomponents <=> B.parent_formula_id == A
    exact_children = defaultdict(list)
    for fid, form in formulas.items():
        p = form.get('parent_formula_id')
        if p and isinstance(p, str) and p in formulas and p != fid:
            exact_children[p].append(fid)

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

    # 5. Mandatory Extreme-Tail & Random Spot Check Report (Safeguard #4)
    final_counts = Counter({fid: len(ch) for fid, ch in exact_children.items()})
    overloaded_after = sum(1 for c in final_counts.values() if c > 25)

    print("\n" + "=" * 68)
    print("📊 REBALANCING & RECIPROCITY SUMMARY")
    print("=" * 68)
    print(f"  • Curated Upstream Fixes:             {stats['curated_upstream_fixes']:,}")
    print(f"  • Re-parented to Same Subtopic (A):   {stats['A_same_subtopic']:,}")
    print(f"  • Re-parented to Parent Subtopic (B): {stats['B_parent_subtopic']:,}")
    print(f"  • Re-parented to Domain Sub-Branch(C):{stats['C_shared_var_subbranch']:,}")
    print(f"  • Promoted to Honest Root (D):        {stats['D_honest_root']:,}")
    print(f"  • Unreciprocal Subcomponents Pruned:  {pruned_unreciprocal:,}")
    print(f"  • Overloaded Hubs (>25 children):     {overloaded_after} (Max children on any hub: {final_counts.most_common(1)[0][1] if final_counts else 0})")
    print(f"  • Total Formula Records Updated:      {len(modified_shards):,}")
    print("=" * 68)

    print("\n🔎 EXTREME-TAIL SPOT CHECK: Top 5 Most Populated Parent Hubs")
    for idx, (pid, cnt) in enumerate(final_counts.most_common(5), 1):
        print(f"  {idx}. {pid:46s} | {cnt:2d} children | {formulas[pid].get('title')}")

    if sum(len(v) for v in samples.values()) > 0:
        random.seed(42)
        all_samples = []
        for k, v in samples.items():
            for item in v:
                all_samples.append((k, item[0], item[1], item[2]))
        picks = random.sample(all_samples, min(5, len(all_samples)))
        print("\n🎲 RANDOM SPOT CHECK: 5 Sampled Reassignments")
        for strat, cid, old_p, new_p in picks:
            c_title = formulas[cid].get('title', cid)
            new_title = formulas[new_p].get('title', new_p) if new_p in formulas else new_p
            print(f"  • [{strat}] {cid} ({c_title})")
            print(f"      {old_p}  -->  {new_p} ({new_title})")

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
    parser = argparse.ArgumentParser(description="Subtopic-Grounded & Anti-Goodhart Lineage Rebalancer")
    parser.add_argument('--apply', action='store_true', help="Persist updates and rebuild derivation graph")
    parser.add_argument('--dry-run', action='store_true', help="Run simulation without modifying shard files")
    args = parser.parse_args()

    formulas, file_map = load_all_shards()
    formulas, modified_fids = enrich_families(formulas, dry_run=not args.apply)

    if args.apply:
        save_shards(formulas, file_map, modified_fids)
        print("\n🔨 Rebuilding derivation graph...")
        import subprocess
        subprocess.run([sys.executable, GRAPH_BUILDER], check=True)
