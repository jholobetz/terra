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

ROOT_DERIVATION_TYPES = {
    'AXIOMATIC_FOUNDATION',
    'DEFINITION',
    'EMPIRICAL_LAW',
    'POSTULATE',
    'FUNDAMENTAL_CONSTANT',
    'THEORETICAL_DERIVATION',
}

MAX_DIRECT_CHILDREN = 25

ALLOWED_MATH_WORDS = {
    'const', 'constant', 'even', 'odd', 'true', 'false', 'null', 'zero', 'free',
    'matter', 'radiation', 'total', 'max', 'min', 'eff', 'crit', 'obs', 'init',
    'final', 'rest', 'kin', 'pot', 'ext', 'int', 'stat', 'sys', 'env', 'sinh',
    'cosh', 'tanh', 'coth', 'sech', 'csch', 'arcsin', 'arccos', 'arctan', 'grad',
    'curl', 'div', 'diag', 'rank', 'span', 'supp', 'sign', 'sinc', 'erfc',
}

TRUNCATED_CMD_PATTERNS = [
    r'(?<![\\a-zA-Z])(?:extit|extbf|ext)\{',
    r'(?<![\\a-zA-Z])(?:rangle|langle)(?=\b|_|\^)',
    r'(?<![\\a-zA-Z])(?:tial|abla|imes|ightarrow|infty|propto|approx|equiv|sqrt|frac)(?=\b|_|\^)',
    r'(?<![\\a-zA-Z])au(?=_|\^)',
]

STOP_WORDS = {
    'the', 'of', 'in', 'for', 'and', 'to', 'a', 'an', 'with', 'by', 'from', 'on', 'at', 'as', 'is',
    'law', 'equation', 'formula', 'relation', 'identity', 'condition', 'definition', 'principle',
    'general', 'form', 'rule', 'theorem', 'term', 'state', 'system', 'function', 'value',
    'model', 'theory', 'effect', 'property', 'constant', 'variable', 'parameter', 'factor',
    'first', 'second', 'third', 'total', 'net', 'local', 'global', 'standard', 'simple',
}

LATEX_COMMANDS_IGNORE = {
    'frac', 'sqrt', 'left', 'right', 'mathrm', 'mathbf', 'mathit', 'mathcal', 'mathbb', 'text',
    'partial', 'int', 'oint', 'sum', 'prod', 'lim', 'to', 'rightarrow', 'iff', 'implies',
    'approx', 'sim', 'propto', 'equiv', 'neq', 'le', 'ge', 'leq', 'geq', 'pm', 'mp', 'times',
    'cdot', 'dots', 'cdots', 'quad', 'qquad', 'hat', 'vec', 'bar', 'tilde', 'dot', 'ddot', 'overline',
    'sin', 'cos', 'tan', 'exp', 'ln', 'log', 'det', 'Tr', 'Re', 'Im',
    'langle', 'rangle', 'vert', 'Vert', 'not', 'begin', 'end', 'matrix', 'pmatrix', 'bmatrix',
}


def braces_balanced(s):
    s_clean = re.sub(r'\\[{}]', '', s)
    depth = 0
    for ch in s_clean:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def is_corrupted_equation(eq, title=''):
    if not eq or not eq.strip():
        return True, 'empty'
    c = eq.strip()
    low_c = c.lower()
    low_t = (title or '').lower()
    if c in ('\\text{N/A}', 'N/A', '\\text{Unrecoverable Fragment}', 'b1,b2,b3'):
        return True, 'placeholder'
    if any(w in low_t for w in ('uninterpretable', 'undefined mathematical', 'not a latex equation', 'syntactically invalid')):
        return True, 'invalid_title'
    if any(ord(ch) < 32 or (127 <= ord(ch) <= 159) for ch in c) or re.search(r'\\f(?![a-zA-Z])', c) or r'\ries' in c:
        return True, 'control_char'
    if any(u in c for u in ('∑', 'ℇ', '•', '℃', '̂', '̇Φ')):
        return True, 'garbled_unicode'
    if any(bad in low_c for bad in ('xmlns', 'mathml', 'inline-formula', '/math', '/mi', '/msub', '/mrow', 'mathvariant', 'itemize', '/momsub', '/code/')):
        return True, 'raw_markup_tag'
    for pat in TRUNCATED_CMD_PATTERNS:
        if re.search(pat, c):
            return True, 'truncated_cmd'
    if re.search(r'(?<!\\)\\$', c) or re.search(r'[=/_^]$', c) or re.search(r'(?<!\\),$', c) or re.search(r'(?<![\^_])[+\-*]$', c):
        return True, 'dangling_end'
    if not braces_balanced(c):
        return True, 'unbalanced_braces'
    s = re.sub(r'\\(?:begin|end)\s*\{[^}]*\}', ' ', c)
    s = re.sub(r'\\(?:text|mathrm|mathbf|mathit|mathcal|mathbb|operatorname|textbf|textit)\s*\{[^}]*\}', ' ', s)
    s = re.sub(r'[_^]\s*\{[^}]*\}', ' ', s)
    s = re.sub(r'\\[a-zA-Z]+', ' ', s)
    words = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', s) if w.lower() not in ALLOWED_MATH_WORDS]
    if len(words) >= 2:
        return True, 'prose_bleed'
    if len(words) == 1 and len(re.sub(r'[a-zA-Z\s,.\'\";:()\-]', '', c)) == 0:
        return True, 'pure_text'
    return False, ''


def extract_math_tokens(form):
    tokens = set()
    sv = form.get('semantic_variables')
    if isinstance(sv, dict):
        for k in sv.keys():
            clean = re.sub(r'\\(?:mathbf|mathrm|mathit|mathcal|mathbb|text|hat|vec|bar|tilde|dot|ddot|overline)\b', '', k)
            clean = clean.replace('{', '').replace('}', '').replace(' ', '')
            if clean:
                tokens.add(clean.lower())
            root = re.split(r'[_^]', clean)[0].strip()
            if root and len(root) >= 1 and root not in ('\\', '-', '+'):
                tokens.add(root.lower())
    eq = form.get('equation') or ''
    eq_no_text = re.sub(r'\\(?:text|mathrm)\{[^}]*\}', '', eq)
    for m in re.finditer(r'\\([a-zA-Z]+)', eq_no_text):
        cmd = m.group(1)
        if cmd not in LATEX_COMMANDS_IGNORE:
            tokens.add('\\' + cmd.lower())
            tokens.add(cmd.lower())
    eq_stripped = re.sub(r'\\[a-zA-Z]+', ' ', eq_no_text)
    for m in re.finditer(r'\b([a-zA-Z])(?:_\{?[a-zA-Z0-9]+\}?)?', eq_stripped):
        tokens.add(m.group(0).replace('{', '').replace('}', '').lower())
        tokens.add(m.group(1).lower())
    return tokens


def extract_concept_keywords(fid, form):
    text = f"{fid} {form.get('title') or ''} {form.get('conceptual_definition') or ''}".lower()
    text = re.sub(r'\b[0-9a-f]{8}\b', ' ', text)
    words = re.findall(r'[a-z]{4,}', text)
    kws = {w for w in words if w not in STOP_WORDS}
    stems = {w[:6] for w in kws if len(w) >= 6}
    return kws | stems


CURATED_AFFINITY_KEEP = {
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
    'lagrangian-density-for-schrodinger-equation',
    'time-dependent-schrodinger-equation',
    'big-bang-start-4da62fa5',
    'taylor-expansion-mechanics-identity-1-9fffb077-1ccd2384',
    'angular-momentum-definition-6f8a0efa',
    'torque-definition',
}


def has_parent_child_affinity(fid, form, pid, pform, subtopic_ctx=None):
    if (
        bool(form.get('derivation_steps'))
        or form.get('lineage_confidence') in ('curated', 'cas_verified')
        or fid in CURATED_AFFINITY_KEEP
    ):
        return True
    c_vars = extract_math_tokens(form)
    p_vars = extract_math_tokens(pform)
    shared_vars = bool(c_vars & p_vars)

    c_kw = extract_concept_keywords(fid, form)
    p_kw = extract_concept_keywords(pid, pform)
    shared_kw = c_kw & p_kw

    c_subs = set(form.get('subtopics') or [])
    p_subs = set(pform.get('subtopics') or [])
    same_sub = bool(c_subs & p_subs)
    linked_sub = False
    same_dom = False
    explicit_cross_domain = False

    if subtopic_ctx:
        f2s, sub_neighbors, sub_dom = subtopic_ctx
        c_subs = c_subs | set(f2s.get(fid, []))
        p_subs = p_subs | set(f2s.get(pid, []))
        same_sub = bool(c_subs & p_subs)
        linked_sub = any(sub_neighbors.get(cs, set()) & p_subs for cs in c_subs)
        c_doms = {sub_dom.get(s) for s in c_subs if s in sub_dom}
        if form.get('category'):
            c_doms.add(form['category'])
        p_doms = {sub_dom.get(s) for s in p_subs if s in sub_dom}
        if pform.get('category'):
            p_doms.add(pform['category'])
        same_dom = bool(c_doms & p_doms)
        explicit_cross_domain = bool(c_doms and p_doms and not same_dom)

    has_aff = bool(
        shared_vars
        or same_sub
        or linked_sub
        or len(shared_kw) >= 2
        or (same_dom and len(shared_kw) >= 1)
    )
    if explicit_cross_domain and not (linked_sub or shared_vars or len(shared_kw) >= 2):
        has_aff = False
    return has_aff



def has_loop_free_ancestry(fid, parent_map, max_steps=25):
    """Returns (depth, loop_free) tracing parent_map upward from fid."""
    visited = {fid}
    curr = fid
    depth = 0
    while curr in parent_map and depth < max_steps:
        nxt = parent_map[curr]
        if nxt in visited:
            return depth, False
        visited.add(nxt)
        curr = nxt
        depth += 1
    return depth, True


KNOWN_BOILERPLATE_STRINGS = {
    "Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance.",
    "Subject to asymptotic boundary conditions and non-relativistic conservation limits.",
    "Defines key conservation, boundary, or dynamical balance relations in the physical manifold.",
    "The left-hand side of the relation establishes how spatial gradients or field variations are balanced by the right-hand side source or rate terms.",
}


def has_aligned_semantic_variables(eq: str, sem_vars) -> bool:
    """Returns True if sem_vars is a non-empty dict and at least one key appears in eq."""
    if not isinstance(sem_vars, dict) or len(sem_vars) < 1 or not eq:
        return False
    for k in sem_vars.keys():
        k_clean = k.strip("$ ").strip()
        if k_clean and k_clean in eq:
            return True
    return False


def calculate_lhi(fid, form, formulas, parent_map, reciprocal_child_map, subtopic_ctx=None, boilerplate_strings=None):
    """
    Role-Aware, Anti-Goodhart & Reciprocity-Enforced Lineage Health Index (0-100):
      1. Upstream Lineage & Tree Depth (40 pts)
      2. Reciprocal Graph Closure, Shape Cap (<= 25 children) & Derivation Type (30 pts)
      3. Physical Grounding: Symmetry, Limits & Variables (30 pts)
    """
    has_parent = fid in parent_map
    reciprocal_children = reciprocal_child_map.get(fid, [])
    declared_subs = [c for c in form.get('subcomponents', []) if isinstance(c, str) and c in formulas]
    unreciprocal_subs = [c for c in declared_subs if formulas.get(c, {}).get('parent_formula_id') != fid]

    dtype = form.get('derivation_type', '')
    is_axiom = (dtype in ROOT_DERIVATION_TYPES and not has_parent) or (not has_parent and len(reciprocal_children) > 0)
    is_overloaded_hub = len(reciprocal_children) > MAX_DIRECT_CHILDREN
    eq = form.get('equation', '')
    corrupted, corrupt_reason = is_corrupted_equation(eq, form.get('title', ''))

    has_affinity = True
    if has_parent:
        p_id = parent_map[fid]
        has_affinity = has_parent_child_affinity(fid, form, p_id, formulas[p_id], subtopic_ctx=subtopic_ctx)

    conf = form.get('lineage_confidence') or ('curated' if form.get('derivation_steps') else ('root' if not has_parent else 'heuristic'))

    # Strict Isolation Gate: if a formula has no valid parent, no reciprocal children, and is not a declared root definition/axiom, it is Isolated (0).
    if not has_parent and len(reciprocal_children) == 0 and not is_axiom:
        return {
            'id': fid,
            'title': form.get('title', fid),
            'equation': eq,
            'score': 0,
            'tier': 'BLACK',
            'status_label': 'Isolated',
            'upstream_score': 0,
            'downstream_score': 0,
            'depth_score': 0,
            'quality_score': 0,
            'parent_id': None,
            'is_axiom': False,
            'is_overloaded_hub': False,
            'is_corrupted_equation': corrupted,
            'has_parent_affinity': False,
            'lineage_confidence': conf,
            'children_count': len(declared_subs),
            'valid_children_count': 0,
            'trivial_children_count': 0,
            'unreciprocal_children_count': len(unreciprocal_subs),
        }

    # Bucket 1: Upstream Lineage & Tree Depth (up to 40 pts: 25 upstream + 15 depth)
    parent_is_overloaded = has_parent and len(reciprocal_child_map.get(parent_map[fid], [])) > MAX_DIRECT_CHILDREN
    upstream_score = 25 if ((has_parent and has_affinity) or is_axiom) else 0
    if parent_is_overloaded and upstream_score > 0:
        upstream_score -= 10
    ancestry_depth, loop_free = has_loop_free_ancestry(fid, parent_map)

    depth_score = 0
    if loop_free and not parent_is_overloaded and not is_overloaded_hub and (has_affinity or is_axiom):
        if ancestry_depth >= 2:
            depth_score = 15
        elif ancestry_depth == 1:
            p_id = parent_map[fid]
            if len(reciprocal_child_map.get(p_id, [])) >= 2 or formulas.get(p_id, {}).get('derivation_type') in ROOT_DERIVATION_TYPES:
                depth_score = 15
            else:
                depth_score = 10
        elif is_axiom:
            if len(reciprocal_children) > 0:
                has_grandchild = any(len(reciprocal_child_map.get(c, [])) > 0 for c in reciprocal_children)
                depth_score = 15 if (has_grandchild or len(reciprocal_children) >= 2) else 12
            else:
                # Honest standalone root definition/postulate
                depth_score = 12

    # Bucket 2: Reciprocal Graph Closure, Hub Shape Constraint & Derivation Type (up to 30 pts)
    reciprocity_score = 20
    if has_parent:
        p_id = parent_map[fid]
        parent_subs = formulas.get(p_id, {}).get('subcomponents', [])
        if fid not in parent_subs:
            reciprocity_score -= 10
        if not has_affinity:
            reciprocity_score = max(0, reciprocity_score - 15)
    if unreciprocal_subs:
        reciprocity_score = max(0, reciprocity_score - 10 * len(unreciprocal_subs))
    if is_overloaded_hub:
        reciprocity_score = 0
    elif parent_is_overloaded:
        reciprocity_score = max(0, reciprocity_score - 10)

    trivial = is_trivial_variable(eq)
    type_score = 0
    if dtype in VALID_DERIVATION_TYPES or is_axiom or (isinstance(dtype, str) and len(dtype) >= 4 and dtype != 'UNDEFINED'):
        type_score += 5
    if not trivial and not corrupted:
        type_score += 5

    downstream_score = reciprocity_score + type_score

    # Bucket 3: Physical Grounding — Symmetry, Limits & Variables (up to 30 pts)
    quality_score = 0
    sym_orig = (form.get('symmetry_origin') or '').strip()
    lim_bound = (form.get('limits_and_boundary') or '').strip()
    sem_vars = form.get('semantic_variables')
    bp_set = KNOWN_BOILERPLATE_STRINGS | (boilerplate_strings or set())

    if sym_orig not in bp_set:
        if len(sym_orig) >= 20:
            quality_score += 10
        elif len(sym_orig) > 0:
            quality_score += 5

    if lim_bound not in bp_set:
        if len(lim_bound) >= 20:
            quality_score += 10
        elif len(lim_bound) > 0:
            quality_score += 5

    if has_aligned_semantic_variables(eq, sem_vars):
        quality_score += 10

    total_score = max(0, min(100, upstream_score + depth_score + downstream_score + quality_score))
    if corrupted:
        total_score = min(total_score, 25)

    if total_score >= 75 and not is_overloaded_hub and not corrupted and has_affinity:
        tier = "GREEN"
        status_label = "Rich & Complete"
    elif total_score >= 40 and not corrupted:
        tier = "YELLOW"
        if is_overloaded_hub:
            status_label = "Overloaded Hub (>25 children)"
        elif not has_affinity:
            status_label = "Zero Parent-Child Affinity"
        else:
            status_label = "Moderate"
    elif total_score > 0:
        tier = "RED"
        status_label = f"Corrupted Equation ({corrupt_reason})" if corrupted else "Thin"
    else:
        tier = "BLACK"
        status_label = "Isolated"

    non_trivial_children = [c for c in reciprocal_children if not is_trivial_variable(formulas.get(c, {}).get('equation', ''))]
    trivial_children = [c for c in reciprocal_children if is_trivial_variable(formulas.get(c, {}).get('equation', ''))]

    return {
        'id': fid,
        'title': form.get('title', fid),
        'equation': eq,
        'score': total_score,
        'tier': tier,
        'status_label': status_label,
        'upstream_score': upstream_score,
        'downstream_score': downstream_score,
        'depth_score': depth_score,
        'quality_score': quality_score,
        'parent_id': parent_map.get(fid),
        'is_axiom': is_axiom,
        'is_overloaded_hub': is_overloaded_hub,
        'is_corrupted_equation': corrupted,
        'has_parent_affinity': has_affinity,
        'lineage_confidence': conf,
        'children_count': len(reciprocal_children),
        'valid_children_count': len(non_trivial_children),
        'trivial_children_count': len(trivial_children),
        'unreciprocal_children_count': len(unreciprocal_subs),
    }


def _build_subtopic_context(formulas):
    content_dir = os.path.join(PROJECT_ROOT, 'app', 'config', 'content')
    cat_file = os.path.join(content_dir, 'categories.json')
    if not os.path.exists(cat_file):
        return None
    try:
        with open(cat_file, 'r', encoding='utf-8') as f:
            cats = json.load(f)
        f2s = {}
        sub_neighbors = {}
        sub_dom = {}
        for dom in cats.keys():
            p = os.path.join(content_dir, f'{dom}.json')
            if not os.path.exists(p):
                continue
            with open(p, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for sid, sdata in data.items():
                if not isinstance(sdata, dict):
                    continue
                sub_dom[sid] = dom
                for fid in sdata.get('formula_ids', []):
                    if isinstance(fid, str):
                        f2s.setdefault(fid, []).append(sid)
                for sec in sdata.get('sections', []):
                    if isinstance(sec, dict):
                        for fid in sec.get('formulas', []):
                            if isinstance(fid, str):
                                f2s.setdefault(fid, []).append(sid)
                for rel in sdata.get('parents', []) + sdata.get('related', []) + sdata.get('related_subtopics', []) + sdata.get('prerequisites', []):
                    if isinstance(rel, str):
                        sub_neighbors.setdefault(sid, set()).add(rel)
                        sub_neighbors.setdefault(rel, set()).add(sid)
        for fid in formulas:
            if fid not in f2s:
                for sid in sub_dom:
                    if fid.startswith(sid + '-'):
                        f2s.setdefault(fid, []).append(sid)
        return (f2s, sub_neighbors, sub_dom)
    except Exception:
        return None


def audit_all(formulas):
    parent_map = {}
    reciprocal_child_map = {}

    for fid, f in formulas.items():
        p = f.get('parent_formula_id')
        if p and isinstance(p, str) and p in formulas and p != fid:
            parent_map[fid] = p
            reciprocal_child_map.setdefault(p, []).append(fid)

    for k in reciprocal_child_map:
        reciprocal_child_map[k] = sorted(set(reciprocal_child_map[k]))

    subtopic_ctx = _build_subtopic_context(formulas) if len(formulas) > 500 else None

    from collections import Counter
    sym_cnt = Counter((f.get('symmetry_origin') or '').strip() for f in formulas.values() if (f.get('symmetry_origin') or '').strip())
    lim_cnt = Counter((f.get('limits_and_boundary') or '').strip() for f in formulas.values() if (f.get('limits_and_boundary') or '').strip())
    boilerplate_strings = {s for s, c in sym_cnt.items() if c > 15} | {s for s, c in lim_cnt.items() if c > 15}

    results = {}
    for fid, form in formulas.items():
        results[fid] = calculate_lhi(
            fid, form, formulas, parent_map, reciprocal_child_map,
            subtopic_ctx=subtopic_ctx, boilerplate_strings=boilerplate_strings
        )

    return results

def print_summary(results):
    total = len(results)
    green = sum(1 for r in results.values() if r['tier'] == 'GREEN')
    yellow = sum(1 for r in results.values() if r['tier'] == 'YELLOW')
    red = sum(1 for r in results.values() if r['tier'] == 'RED')
    black = sum(1 for r in results.values() if r['tier'] == 'BLACK')
    overloaded = sum(1 for r in results.values() if r.get('is_overloaded_hub'))
    zero_affinity = sum(1 for r in results.values() if r.get('parent_id') and not r.get('has_parent_affinity', True))
    corrupted = sum(1 for r in results.values() if r.get('is_corrupted_equation'))
    curated_links = sum(1 for r in results.values() if r.get('lineage_confidence') in ('curated', 'cas_verified'))
    heuristic_links = sum(1 for r in results.values() if r.get('lineage_confidence') == 'heuristic')
    root_nodes = sum(1 for r in results.values() if not r.get('parent_id'))
    max_children = max((r.get('children_count', 0) for r in results.values()), default=0)
    avg_score = sum(r['score'] for r in results.values()) / total if total > 0 else 0

    print("=" * 68)
    print("📊 TERRA PHYSICS LAB - LINEAGE HEALTH INDEX (LHI) AUDIT REPORT")
    print("=" * 68)
    print(f"Total Formulas Evaluated: {total:,}")
    print(f"Average Encyclopedia LHI: {avg_score:.1f} / 100")
    print(f"Max Direct Children/Hub:  {max_children} (Cap <= {MAX_DIRECT_CHILDREN}, Overloaded Hubs: {overloaded})")
    print(f"Zero-Affinity Links:      {zero_affinity} | Corrupted Equations: {corrupted}")
    print(f"Lineage Confidence:       {curated_links:,} Curated/Verified | {heuristic_links:,} Heuristic | {root_nodes:,} Roots\n")
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
    parser.add_argument('--heal', action='store_true', help="Heal isolated and thin formula nodes by attaching family pillars and rebuilding derivation graph")
    args = parser.parse_args()

    if args.heal:
        print("🩹 Initiating Automated Formula Lineage Healing Protocol...")
        enricher_path = os.path.join(PROJECT_ROOT, 'scripts', 'maintenance', 'enrich_lineage_families.py')
        import subprocess
        res = subprocess.run([sys.executable, enricher_path, '--apply'])
        if res.returncode != 0:
            print("❌ Healing failed during family enrichment.")
            sys.exit(res.returncode)
        print("\n✨ Re-evaluating Lineage Health Index post-healing...")
        formulas, file_map = load_all_formulas()
        results = audit_all(formulas)
        print_summary(results)
        return

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
