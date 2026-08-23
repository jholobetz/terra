#!/usr/bin/env python3
"""
📊 Lineage Health Index (LHI) Auditor for Terra Physics Lab
Evaluates, scores (0-100), and audits every formula in the encyclopedia for its
mathematical derivation depth, ancestry, and structural richness.

Supports lookup by ID, Search Keyword, LaTeX snippet, or Browser URL.

Usage:
    python3 scripts/maintenance/audit_lineage_health.py [--summary] [--thin-top 20]
    python3 scripts/maintenance/audit_lineage_health.py --formula <id>
    python3 scripts/maintenance/audit_lineage_health.py --search "Bernoulli"
    python3 scripts/maintenance/audit_lineage_health.py --url "http://localhost:8000/physics/equation-explainer?latex=..."
"""

import os
import sys
import json
import glob
import re
import argparse
import urllib.parse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
LATEX_INDEX_PATH = os.path.join(PROJECT_ROOT, 'app', 'config', 'formulas_latex_index.json')

def load_all_formulas():
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
    s = re.sub(r'\\(?:left|right)\b', '', s)
    s = s.replace('{', '').replace('}', '').replace('\\,', '').replace('\\;', '')
    return s

def resolve_formula_id(query, formulas):
    """Resolves formula ID from direct ID, URL, LaTeX, or Keyword"""
    if not query: return None
    query = query.strip()

    # 1. Direct ID match
    if query in formulas:
        return query

    # 2. URL parsing
    if 'http://' in query or 'https://' in query or 'equation-explainer' in query:
        parsed = urllib.parse.urlparse(query)
        qs = urllib.parse.parse_qs(parsed.query)
        if 'id' in qs and qs['id'][0] in formulas:
            return qs['id'][0]
        if 'latex' in qs:
            query = urllib.parse.unquote(qs['latex'][0])

    # 3. Exact LaTeX match
    norm_q = normalize_tex(query)
    for fid, f in formulas.items():
        if normalize_tex(f.get('equation', '')) == norm_q:
            return fid

    # 4. Closest substring match by length (if query is substantial LaTeX)
    if len(norm_q) > 8:
        candidates = []
        for fid, f in formulas.items():
            f_norm = normalize_tex(f.get('equation', ''))
            if f_norm and (norm_q in f_norm or f_norm in norm_q):
                candidates.append((abs(len(f_norm) - len(norm_q)), fid))
        if candidates:
            candidates.sort(key=lambda x: x[0])
            return candidates[0][1]

    # 4. Keyword / Title substring match
    q_lower = query.lower()
    matches = []
    for fid, f in formulas.items():
        if q_lower in fid.lower() or q_lower in f.get('title', '').lower():
            matches.append(fid)
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        print(f"\n🔎 Multiple formulas matched '{query}':")
        for m in matches[:10]:
            print(f"  • ID: {m}  ==>  Title: {formulas[m].get('title')}")
        print("\nSpecify exact ID using: --formula <id>")
        return None

    print(f"❌ Formula not found for query: '{query}'")
    return None

def is_trivial_variable(eq):
    if not eq: return True
    clean = re.sub(r'\s+', '', eq)
    if re.match(r'^[a-zA-Z](\\?[a-zA-Z0-9_^{}]+)?\s*=\s*[0-9]+(\.[0-9]+)?$', clean):
        return True
    if len(clean) <= 4 and '=' in clean:
        return True
    return False

def calculate_lhi(fid, form, formulas, parent_map, child_map):
    upstream_score = 0
    is_axiom = form.get('derivation_type') == 'AXIOMATIC_FOUNDATION'
    has_parent = fid in parent_map
    
    if is_axiom or has_parent:
        upstream_score = 35
    
    children = child_map.get(fid, [])
    non_trivial_children = []
    trivial_children = []
    
    for cid in children:
        child_form = formulas.get(cid, {})
        child_eq = child_form.get('equation', '')
        if is_trivial_variable(child_eq):
            trivial_children.append(cid)
        else:
            non_trivial_children.append(cid)
            
    n_valid = len(non_trivial_children)
    if n_valid >= 3:
        downstream_score = 35
    elif n_valid == 2:
        downstream_score = 25
    elif n_valid == 1:
        downstream_score = 15
    elif len(trivial_children) > 0:
        downstream_score = 5
    else:
        downstream_score = 0

    has_grandparent = False
    if has_parent:
        p_id = parent_map[fid]
        if p_id in parent_map or formulas.get(p_id, {}).get('derivation_type') == 'AXIOMATIC_FOUNDATION':
            has_grandparent = True
            
    has_grandchild = False
    for cid in non_trivial_children:
        if len(child_map.get(cid, [])) > 0:
            has_grandchild = True
            break
            
    depth_score = 0
    if (has_parent or is_axiom) and n_valid > 0:
        depth_score = 10
        if has_grandparent or has_grandchild:
            depth_score = 15
    elif has_parent or n_valid > 0:
        depth_score = 5

    quality_score = 15
    if len(children) > 0 and len(non_trivial_children) == 0:
        quality_score = 5
    elif len(children) == 0 and not has_parent and not is_axiom:
        quality_score = 0

    total_score = max(0, min(100, upstream_score + downstream_score + depth_score + quality_score))

    if total_score >= 75:
        tier = "GREEN"
        status_label = "Rich & Complete"
    elif total_score >= 40:
        tier = "YELLOW"
        status_label = "Moderate"
    elif total_score > 0:
        tier = "RED"
        status_label = "Thin"
    else:
        tier = "BLACK"
        status_label = "Isolated"

    return {
        'id': fid,
        'title': form.get('title', fid),
        'equation': form.get('equation', ''),
        'score': total_score,
        'tier': tier,
        'status_label': status_label,
        'upstream_score': upstream_score,
        'downstream_score': downstream_score,
        'depth_score': depth_score,
        'quality_score': quality_score,
        'parent_id': parent_map.get(fid),
        'is_axiom': is_axiom,
        'children_count': len(children),
        'valid_children_count': len(non_trivial_children),
        'trivial_children_count': len(trivial_children)
    }

def audit_all(formulas):
    parent_map = {}
    child_map = {}

    for fid, f in formulas.items():
        p = f.get('parent_formula_id')
        if p and p in formulas:
            parent_map[fid] = p
            child_map.setdefault(p, []).append(fid)
        for c in f.get('subcomponents', []):
            if c in formulas:
                child_map.setdefault(fid, []).append(c)
                if c not in parent_map:
                    parent_map[c] = fid

    for k in child_map:
        child_map[k] = list(set(child_map[k]))

    results = {}
    for fid, form in formulas.items():
        results[fid] = calculate_lhi(fid, form, formulas, parent_map, child_map)

    return results

def print_summary(results):
    total = len(results)
    green = sum(1 for r in results.values() if r['tier'] == 'GREEN')
    yellow = sum(1 for r in results.values() if r['tier'] == 'YELLOW')
    red = sum(1 for r in results.values() if r['tier'] == 'RED')
    black = sum(1 for r in results.values() if r['tier'] == 'BLACK')
    avg_score = sum(r['score'] for r in results.values()) / total if total > 0 else 0

    print("=" * 68)
    print("📊 TERRA PHYSICS LAB - LINEAGE HEALTH INDEX (LHI) AUDIT REPORT")
    print("=" * 68)
    print(f"Total Formulas Evaluated: {total:,}")
    print(f"Average Encyclopedia LHI: {avg_score:.1f} / 100\n")
    print(f"  🟢 Rich & Complete (Score 75-100): {green:,} ({green/total*100:.1f}%)")
    print(f"  🟡 Moderate        (Score 40-74):  {yellow:,} ({yellow/total*100:.1f}%)")
    print(f"  🔴 Thin            (Score 1-39):   {red:,} ({red/total*100:.1f}%)")
    print(f"  ⚫ Isolated        (Score 0):       {black:,} ({black/total*100:.1f}%)")
    print("=" * 68)

def main():
    parser = argparse.ArgumentParser(description="Audit & Diagnose Formula Lineage Health")
    parser.add_argument('query', nargs='?', help="Formula ID, title, LaTeX snippet, or URL to diagnose")
    parser.add_argument('--summary', action='store_true', help="Print summary metrics")
    parser.add_argument('--thin-top', type=int, default=0, help="List top N thin equations")
    parser.add_argument('--formula', type=str, help="Formula ID, title, LaTeX, or URL to inspect")
    parser.add_argument('--search', type=str, help="Search formulas by title or keyword")
    parser.add_argument('--url', type=str, help="Inspect formula from equation explainer URL")
    parser.add_argument('--export-json', type=str, help="Export audit results to JSON file")
    args = parser.parse_args()

    formulas, file_map = load_all_formulas()
    results = audit_all(formulas)

    target_query = args.query or args.formula or args.search or args.url

    if target_query:
        fid = resolve_formula_id(target_query, formulas)
        if fid and fid in results:
            r = results[fid]
            print(f"\n🔍 Formula Lineage Diagnostic: [{fid}]")
            print(f"  Title: {r['title']}")
            print(f"  Equation: {r['equation']}")
            print(f"  Overall LHI Score: {r['score']} / 100 ({r['status_label']})")
            print(f"  ├─ Upstream Score:   {r['upstream_score']} / 35 (Parent: {r['parent_id'] or 'None'})")
            print(f"  ├─ Downstream Score: {r['downstream_score']} / 35 ({r['valid_children_count']} valid, {r['trivial_children_count']} trivial)")
            print(f"  ├─ Depth Span Score: {r['depth_score']} / 15")
            print(f"  └─ Quality Score:    {r['quality_score']} / 15")
        elif not fid:
            pass
        return

    print_summary(results)

    if args.thin_top > 0:
        thins = [r for r in results.values() if r['tier'] == 'RED']
        thins.sort(key=lambda x: len(x['equation']), reverse=True)
        print(f"\n🔎 Top {min(args.thin_top, len(thins))} High-Priority 'Thin' Equations Needing Enrichment:")
        for idx, r in enumerate(thins[:args.thin_top], 1):
            parent_txt = f"Parent: {r['parent_id'][:25]}" if r['parent_id'] else "No Parent"
            print(f"  {idx:2d}. [{r['id']}] (Score: {r['score']})")
            print(f"      {r['title']} => {r['equation'][:50]}")
            print(f"      Status: {parent_txt} | Children: {r['valid_children_count']} valid, {r['trivial_children_count']} trivial\n")

    if args.export_json:
        with open(args.export_json, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
        print(f"✓ Full audit report exported to {args.export_json}")

if __name__ == '__main__':
    main()
