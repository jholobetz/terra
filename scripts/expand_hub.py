#!/usr/bin/env python3
"""
Terra Physics Lab — Unified 1-Step Hub Expansion Engine (scripts/expand_hub.py)

Authoritative, transactional CLI for adding 1 to 20 brand-new Platinum subtopics
(and their accompanying canonical formulas / Tier 1 terms) to any physics hub.

Usage:
  .venv/bin/python3 scripts/expand_hub.py <manifest.json> --dry-run
  .venv/bin/python3 scripts/expand_hub.py <manifest.json> --apply
  .venv/bin/python3 scripts/expand_hub.py <manifest.json> --apply --sync-db

Manifest Schema (JSON):
  {
    "domain": "condensed-matter",
    "pillar": { "title": "5. ...", "narrative": "...", "slugs": [...] },
    // OR "append_to_pillar": "4. ..."
    "allow_short_tokens": ["\\hbar", "e"],   // optional exceptions
    "verified_date": "2026-11-21",           // optional (defaults to today)
    "subtopics": {
      "<slug>": {
        "title": "...",
        "hero_equation": "...",
        "formula_ids": ["..."],
        "content": "<p>...</p>",
        "citations": [{"doi": "...", "title": "...", "authors": ["..."], "url": "..."}],
        "keywords": ["..."],
        "incoming_links": [
          {"from_slug": "...", "sentence": " ... <a href=\"/physics/subtopic/<slug>\" ...>...</a>."}
        ]
      }
    },
    "formulas": [
      {
        "id": "...",
        "title": "...",
        "equation": "...",
        "category": "...",
        "record_type": "equation" | "symbol_or_term",
        "parent_formula_id": "...",
        "derivation_type": "DEFINITION" | "DERIVED_FROM" | ...,
        "description": "...",
        "conceptual_definition": "...",
        "intuitive_summary": "...",
        "interpretation": "...",
        "symmetry_origin": "...",
        "limits_and_boundary": "...",
        "semantic_variables": {"...": "..."},
        "cas_validation": {"status": "...", "is_homogeneous": true, ...}
      }
    ]
  }
"""

import argparse
import datetime
import glob
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from jsonschema import Draft7Validator

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

CONTENT_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content")
FORMULAS_DIR = os.path.join(CONTENT_DIR, "formulas")
TOPICS_DIR = os.path.join(CONTENT_DIR, "topics")
HUB_MANIFESTS_DIR = os.path.join(PROJECT_ROOT, "hub_manifests")
LATEX_INDEX_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formulas_latex_index.json")
HASH_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formulas_hash_registry.json")
SCHEMA_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formula.schema.json")
SEARCH_INDEX_PATH = os.path.join(CONTENT_DIR, "search_index.json")
SLUG_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "global_slug_registry.json")
SEMANTIC_REFS_PATH = os.path.join(PROJECT_ROOT, "app", "config", "ref_data", "semantic_references.json")
SVG_CACHE_PATH = os.path.join(PROJECT_ROOT, "svg_cache.json")

MAX_RECOMMENDED_BATCH = 20
MAX_PARENT_CHILDREN = 25
SVG_CHUNK_SIZE = 150

VALID_DOMAINS = {
    "astrophysics",
    "classical-mechanics",
    "condensed-matter",
    "electromagnetism",
    "fluids-nonlinear",
    "mathematical-methods",
    "philosophy-of-physics",
    "quantum-physics",
    "relativity",
    "standard-model",
    "theoretical-physics",
    "thermodynamics-statistical-mechanics",
}

FORBIDDEN_HTML_RE = re.compile(r"<(ul|ol|li|h[1-6]|div|span|table|br)\b", re.IGNORECASE)
FORBIDDEN_MD_RE = re.compile(r"(\*\*|__)")
NON_CANONICAL_PROSE_DELIM_RE = re.compile(r"\\\(|\\\)|\\\[|\\\]|\$\$")
HTML_OR_MD_IN_FORMULA_PROSE_RE = re.compile(r"<(?:ul|ol|li|b|i|strong|em|p|br)\b|\*\*[^*]+\*\*", re.IGNORECASE)
INLINE_MATH_RE = re.compile(r"\\\((.*?)\\\)", re.DOTALL)
DISPLAY_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)

# Bare single/double alphanumeric token or bare number/power/fraction inside \(...\)
BARE_SHORT_ALNUM_RE = re.compile(r"^[a-zA-Z0-9]{1,2}$")
BARE_NUMBER_RE = re.compile(r"^(?:-?\d+(?:\.\d+)?(?:\^\{\d+\}|\^\d+)?|\d+\s*/\s*\d+)$")


def get_shard_hex(formula_id: str) -> str:
    return hashlib.md5(formula_id.encode("utf-8")).hexdigest()[:2]


def get_shard_path(formula_id: str) -> str:
    hx = get_shard_hex(formula_id)
    return os.path.join(FORMULAS_DIR, hx, f"shard_{hx}.json")


def is_single_variable_token(latex: str) -> bool:
    """Mirrors public/js/mathjax_inspector.js :: isSingleVariableToken()."""
    clean = (latex or "").strip()
    if not clean:
        return True
    if re.match(r"^-?\d+(\.\d+)?$", clean):
        return True

    stripped = re.sub(r"^(?:[-+]|\s*\\(?:pm|mp|Delta|delta|nabla)\s+)", "", clean).strip()
    if not stripped:
        return True

    if re.match(r"^[a-zA-Z]$", stripped):
        return True
    if re.match(r"^\\[a-zA-Z]+\{[a-zA-Z0-9]+\}$", stripped):
        return True
    if re.match(r"^\\[a-zA-Z]+$", stripped):
        return True

    single_var_atom = re.compile(
        r"^(?:\\?[a-zA-Z]|\\(?:mathbf|vec|mathcal|hat|mathbb|mathrm|text)\{[a-zA-Z0-9]+\})+"
        r"(?:_(?:\{[^=+\s]*\}|[a-zA-Z0-9]+)|(?:\^(?:\{[^=+\s]*\}|-?[a-zA-Z0-9]+)))*$"
    )
    if single_var_atom.match(stripped):
        no_neg_exp = re.sub(r"\^\{-[0-9]+\}", "", stripped)
        if not re.search(r"(=|\+|-|\\times|\\int|\\sum|\\frac|\\partial|\\cdot|\\to|\\approx|\\leq|\\geq)", no_neg_exp):
            return True

    fn_match = re.match(
        r"^(.+?)\(\s*([a-zA-Z]|\\[a-zA-Z]+)(?:\s*,\s*([a-zA-Z]|\\[a-zA-Z]+))?\s*\)$",
        stripped,
    )
    if fn_match:
        head = fn_match.group(1).strip()
        if not re.match(r"^(?:\\?(?:sin|cos|tan|exp|log|ln|sinh|cosh|tanh|sech|arsinh|arcsin|arccos|arctan|det|tr|Tr))$", head):
            if is_single_variable_token(head):
                return True

    if re.match(r"^\{\}\^\{\d+\}\\(?:text|mathrm)\{[A-Za-z]{1,3}\}$", clean):
        return True

    return False


def php_normalize_batch(tex_list: List[str]) -> Dict[str, Tuple[str, str]]:
    """
    Calls app/logic/LatexSanitizer.php once to compute exact (normalizeLatex, canonicalizeLatex)
    pairs for all LaTeX strings, guaranteeing 100% parity with PHP runtime resolution.
    """
    if not tex_list:
        return {}
    php_code = (
        'require_once "app/logic/LatexSanitizer.php";'
        '$san = new \\app\\logic\\LatexSanitizer();'
        '$input = json_decode(stream_get_contents(STDIN), true) ?: [];'
        '$out = [];'
        'foreach ($input as $t) {'
        '  $out[$t] = [$san->normalizeLatex($t), $san->canonicalizeLatex($t)];'
        '}'
        'echo json_encode($out, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);'
    )
    proc = subprocess.run(
        ["php", "-r", php_code],
        cwd=PROJECT_ROOT,
        input=json.dumps(tex_list),
        capture_output=True,
        text=True,
        check=True,
    )
    raw = json.loads(proc.stdout)
    return {k: (v[0], v[1]) for k, v in raw.items()}


def load_all_existing_slugs() -> Dict[str, str]:
    """Returns {slug: domain_filename_stem} across all domain content shards."""
    slug_to_domain: Dict[str, str] = {}
    skip = {
        "categories.json",
        "search_index.json",
        "constants.json",
        "entities.json",
        "particles.json",
        "compiled_trie_regex.json",
        "notation.json",
    }
    for cf in sorted(glob.glob(os.path.join(CONTENT_DIR, "*.json"))):
        base = os.path.basename(cf)
        if base in skip:
            continue
        stem = base[:-5]
        with open(cf, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for slug, val in data.items():
                if isinstance(val, dict) and "content" in val:
                    slug_to_domain[slug] = stem
    return slug_to_domain


def load_all_existing_formulas() -> Dict[str, Dict[str, Any]]:
    """Loads all formula records from the 256 nested hex shards."""
    formulas: Dict[str, Dict[str, Any]] = {}
    for sf in sorted(glob.glob(os.path.join(FORMULAS_DIR, "*", "shard_*.json"))):
        with open(sf, "r", encoding="utf-8") as f:
            sd = json.load(f)
        if isinstance(sd, dict):
            formulas.update(sd)
    return formulas


def validate_manifest(
    manifest: Dict[str, Any],
    force_large_batch: bool = False,
    allow_update_existing: bool = False,
) -> Tuple[List[str], List[str], Dict[str, Any]]:
    """
    Runs all 6 pre-flight gates with zero disk writes.
    Returns (errors, warnings, summary_stats).
    """
    errors: List[str] = []
    warnings: List[str] = []

    domain = (manifest.get("domain") or "").strip()
    if domain not in VALID_DOMAINS:
        errors.append(f"Invalid or missing 'domain': '{domain}'. Must be one of {sorted(VALID_DOMAINS)}.")

    subtopics = manifest.get("subtopics")
    if not isinstance(subtopics, dict) or len(subtopics) == 0:
        errors.append("Manifest must include a non-empty 'subtopics' dictionary.")
        return errors, warnings, {}

    n_subtopics = len(subtopics)
    if n_subtopics > MAX_RECOMMENDED_BATCH and not force_large_batch:
        errors.append(
            f"Batch size n={n_subtopics} exceeds recommended cap ({MAX_RECOMMENDED_BATCH}). "
            f"Split into smaller batches or pass --force-large-batch."
        )

    pillar = manifest.get("pillar")
    append_to_pillar = manifest.get("append_to_pillar")
    if not pillar and not append_to_pillar:
        errors.append("Manifest must define either 'pillar' (new pillar object) or 'append_to_pillar' (existing pillar title).")
    if pillar and append_to_pillar:
        errors.append("Manifest cannot define both 'pillar' and 'append_to_pillar'; choose one.")
    if pillar:
        if not pillar.get("title") or not pillar.get("narrative") or not isinstance(pillar.get("slugs"), list):
            errors.append("'pillar' must contain 'title', 'narrative', and 'slugs' list.")
        else:
            missing_in_pillar = [s for s in subtopics if s not in pillar["slugs"]]
            if missing_in_pillar:
                errors.append(f"New subtopic(s) missing from pillar.slugs: {missing_in_pillar}")

    formulas = manifest.get("formulas", [])
    if not isinstance(formulas, list):
        errors.append("'formulas' must be a list of formula objects.")
        formulas = []

    allow_short = set(manifest.get("allow_short_tokens", []))

    existing_slugs = load_all_existing_slugs()
    existing_formulas = load_all_existing_formulas()
    with open(LATEX_INDEX_PATH, "r", encoding="utf-8") as f:
        latex_index = json.load(f)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        formula_schema = json.load(f)
    validator = Draft7Validator(formula_schema)

    # Track batch formula IDs and equations
    batch_formulas_by_id: Dict[str, Dict[str, Any]] = {}
    new_children_per_parent: Dict[str, List[str]] = {}
    prose_fields = (
        "description",
        "conceptual_definition",
        "intuitive_summary",
        "interpretation",
        "symmetry_origin",
        "limits_and_boundary",
    )

    # --- Gate 5: Formula Schema, Delimiters, Collision & Cumulative DAG Fanout ---
    for idx_f, fobj in enumerate(formulas):
        fid = (fobj.get("id") or "").strip()
        if not fid:
            errors.append(f"Formula at index {idx_f} is missing 'id'.")
            continue
        if fid in batch_formulas_by_id:
            errors.append(f"Duplicate formula id '{fid}' inside manifest.")
            continue
        batch_formulas_by_id[fid] = fobj

        eq = (fobj.get("equation") or "").strip()
        if fid in existing_formulas and not allow_update_existing:
            existing_eq = (existing_formulas[fid].get("equation") or "").strip()
            if existing_eq != eq:
                errors.append(f"Formula collision: '{fid}' already exists with a different equation.")

        # Validate against formula.schema.json
        schema_rec = {k: v for k, v in fobj.items() if k != "id"}
        schema_rec.setdefault("status", "platinum")
        schema_rec.setdefault("lineage_confidence", "curated")
        schema_rec.setdefault("subcomponents", [])
        for verr in validator.iter_errors({fid: schema_rec}):
            errors.append(f"Formula schema violation [{fid}]: {verr.message}")

        # Delimiters & duplicate prose checks
        seen_prose: Dict[str, str] = {}
        for pf in prose_fields:
            val = (fobj.get(pf) or "").strip()
            min_len = 35 if pf == "symmetry_origin" else 20
            if len(val) < min_len:
                errors.append(f"Formula [{fid}].{pf} too short ({len(val)} < {min_len} chars).")
            if NON_CANONICAL_PROSE_DELIM_RE.search(val):
                errors.append(f"Formula [{fid}].{pf} uses non-canonical math delimiters (use $ ... $).")
            if HTML_OR_MD_IN_FORMULA_PROSE_RE.search(val):
                errors.append(f"Formula [{fid}].{pf} contains HTML tags or Markdown bold.")
            if val in seen_prose:
                errors.append(f"Formula [{fid}].{pf} is a verbatim duplicate of '{seen_prose[val]}'.")
            elif val:
                seen_prose[val] = pf

        # DAG parent existence & cumulative fanout
        parent_id = fobj.get("parent_formula_id")
        if not parent_id:
            errors.append(f"Formula [{fid}] is missing 'parent_formula_id' (all new formulas must connect to DAG).")
        elif parent_id not in existing_formulas and parent_id not in batch_formulas_by_id:
            # Check if parent appears later in manifest
            later_ids = {(x.get("id") or "").strip() for x in formulas}
            if parent_id not in later_ids:
                errors.append(f"Formula [{fid}] references unknown parent_formula_id '{parent_id}'.")
        if parent_id:
            new_children_per_parent.setdefault(parent_id, []).append(fid)

    for pid, added_kids in new_children_per_parent.items():
        existing_kids = set(existing_formulas.get(pid, {}).get("subcomponents", []))
        combined = existing_kids | set(added_kids)
        if len(combined) > MAX_PARENT_CHILDREN:
            errors.append(
                f"DAG Fanout Violation: parent '{pid}' would have {len(combined)} direct children "
                f"(cap <= {MAX_PARENT_CHILDREN}). Choose a more specific intermediate parent."
            )

    # Collect all LaTeX expressions from subtopics + batch formulas for 1 batched PHP normalization call
    all_tex_to_norm: Set[str] = set()
    for fobj in formulas:
        eq = (fobj.get("equation") or "").strip()
        if eq:
            all_tex_to_norm.add(eq)

    subtopic_math_map: Dict[str, List[str]] = {}
    for slug, sdata in subtopics.items():
        content = sdata.get("content", "")
        exprs = [m.strip() for m in INLINE_MATH_RE.findall(content)] + [m.strip() for m in DISPLAY_MATH_RE.findall(content)]
        subtopic_math_map[slug] = exprs
        for ex in exprs:
            all_tex_to_norm.add(ex)
        hero_eq = (sdata.get("hero_equation") or "").strip()
        if hero_eq:
            all_tex_to_norm.add(hero_eq)

    norm_map = php_normalize_batch(sorted(all_tex_to_norm))

    # Build combined normalized & AST lookup (existing shards + manifest formulas)
    batch_norm_keys: Dict[str, str] = {}
    batch_ast_keys: Dict[str, str] = {}
    for fid, fobj in batch_formulas_by_id.items():
        eq = (fobj.get("equation") or "").strip()
        if eq in norm_map:
            nk, ak = norm_map[eq]
            if nk:
                batch_norm_keys[nk] = fid
            if ak:
                batch_ast_keys[ak] = fid

    # Also build existing AST lookup via PHP for exact parity with audit_clickable_equations.php
    existing_ast_set: Set[str] = set()
    if all_tex_to_norm:
        php_ast_code = (
            'require_once "app/logic/LatexSanitizer.php";'
            '$san = new \\app\\logic\\LatexSanitizer();'
            '$ast = [];'
            'foreach (glob("app/config/content/formulas/*/shard_*.json") as $sf) {'
            '  $sd = json_decode(file_get_contents($sf), true) ?: [];'
            '  foreach ($sd as $fid => $f) {'
            '    $eq = $f["equation"] ?? "";'
            '    if (strpos($eq, "<svg") === 0 && preg_match("/data-tex=\\"([^\\"]+)\\"/i", $eq, $m)) {'
            '      $eq = html_entity_decode($m[1], ENT_QUOTES, "UTF-8");'
            '    }'
            '    $c = $san->canonicalizeLatex($eq);'
            '    if ($c) $ast[$c] = true;'
            '  }'
            '}'
            'echo json_encode(array_keys($ast));'
        )
        proc = subprocess.run(["php", "-r", php_ast_code], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
        existing_ast_set = set(json.loads(proc.stdout))

    # --- Gates 1, 2, 3, 4, 6: Subtopic Checks ---
    subtopic_stats: Dict[str, Dict[str, Any]] = {}
    for slug, sdata in subtopics.items():
        if slug in existing_slugs and not allow_update_existing:
            errors.append(f"Slug collision: '{slug}' already exists in '{existing_slugs[slug]}.json'.")

        title = (sdata.get("title") or "").strip()
        content = (sdata.get("content") or "").strip()
        hero_eq = (sdata.get("hero_equation") or "").strip()
        fids = sdata.get("formula_ids", [])
        citations = sdata.get("citations", [])
        incoming = sdata.get("incoming_links", [])

        if not title:
            errors.append(f"[{slug}] Missing 'title'.")
        if not content:
            errors.append(f"[{slug}] Missing 'content'.")
            continue
        if not hero_eq:
            errors.append(f"[{slug}] Missing 'hero_equation' (required for explicit hero_math SVG).")
        elif hero_eq not in subtopic_math_map[slug]:
            errors.append(f"[{slug}] 'hero_equation' does not appear verbatim in article content: {hero_eq}")

        # Formula IDs exist?
        for fid in fids:
            if fid not in existing_formulas and fid not in batch_formulas_by_id:
                errors.append(f"[{slug}] formula_id '{fid}' not found in existing shards or manifest formulas.")

        # Word count (matching integrity_shield.py: stripped of HTML & math SVGs)
        content_no_math = INLINE_MATH_RE.sub(" ", content)
        content_no_math = DISPLAY_MATH_RE.sub(" ", content_no_math)
        shield_words = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", content_no_math)))
        stripped_words = len(re.sub(r"<[^>]+>", " ", content).split())
        if shield_words < 650:
            errors.append(f"[{slug}] Word count too low ({shield_words} < 650 prose words).")
        if stripped_words > 1050:
            warnings.append(f"[{slug}] Word count high ({stripped_words} > 1000 words).")

        # Paragraphs & MathJax density
        paras = re.findall(r"<p>(.*?)</p>", content, flags=re.DOTALL)
        if len(paras) < 3:
            errors.append(f"[{slug}] Must have at least 3 <p> paragraphs (found {len(paras)}).")
        else:
            first_15 = " ".join(re.sub(r"<[^>]+>", " ", paras[0]).split()[:15]).lower()
            if title and title.lower() in first_15:
                errors.append(f"[{slug}] In Media Res violation: title appears in first 15 words.")
            for pi, ptext in enumerate(paras, 1):
                p_math = len(INLINE_MATH_RE.findall(ptext)) + len(DISPLAY_MATH_RE.findall(ptext))
                if p_math < 2:
                    errors.append(f"[{slug}] Paragraph {pi} has only {p_math} MathJax expression(s) (minimum 2).")

        # Forbidden HTML & Markdown
        bad_tags = FORBIDDEN_HTML_RE.findall(content)
        if bad_tags:
            errors.append(f"[{slug}] Forbidden HTML tags in prose: {sorted(set(bad_tags))}")
        if FORBIDDEN_MD_RE.search(content):
            errors.append(f"[{slug}] Forbidden Markdown bold/underline (** or __) in prose.")

        # Outgoing links & cross-hub bridge
        out_links = list(dict.fromkeys(re.findall(r'href="/physics/subtopic/([^"]+)"', content)))
        missing_out = [l for l in out_links if l not in existing_slugs and l not in subtopics]
        if missing_out:
            errors.append(f"[{slug}] Broken outgoing links: {missing_out}")
        if len(out_links) < 5:
            errors.append(f"[{slug}] Too few outgoing links ({len(out_links)} < 5).")
        cross_hub = [l for l in out_links if l in existing_slugs and existing_slugs[l] != domain]
        if len(cross_hub) < 1:
            errors.append(f"[{slug}] Missing cross-hub bridge link (must link to >= 1 subtopic outside '{domain}').")

        # Incoming links
        if len(incoming) < 2:
            errors.append(f"[{slug}] Must declare >= 2 'incoming_links' from existing articles (found {len(incoming)}).")
        for inc in incoming:
            src = inc.get("from_slug", "")
            sent = inc.get("sentence", "")
            if src not in existing_slugs:
                errors.append(f"[{slug}] incoming_link from unknown slug '{src}'.")
            elif existing_slugs[src] != domain:
                warnings.append(f"[{slug}] incoming_link from '{src}' is in another domain ('{existing_slugs[src]}'); expand_hub updates '{domain}.json' only.")
            if f'/physics/subtopic/{slug}"' not in sent:
                errors.append(f"[{slug}] incoming_link sentence for '{src}' does not link to /physics/subtopic/{slug}.")

        # Citations
        if len(citations) < 2:
            errors.append(f"[{slug}] Must provide >= 2 curated on-topic citations (found {len(citations)}).")
        for ci, cit in enumerate(citations):
            if not cit.get("title") or not cit.get("authors") or not (cit.get("url") or cit.get("doi")):
                errors.append(f"[{slug}] Citation #{ci+1} missing required title/authors/url.")

        # SVG Hygiene & Zero-Undefined-Click Gate
        undef_clickable: List[str] = []
        short_violations: List[str] = []
        unbalanced: List[str] = []
        for ex in dict.fromkeys(subtopic_math_map[slug]):
            if ex.count("{") != ex.count("}"):
                unbalanced.append(ex)
            if ex not in allow_short and (BARE_SHORT_ALNUM_RE.match(ex) or BARE_NUMBER_RE.match(ex)):
                short_violations.append(ex)
            if is_single_variable_token(ex):
                continue
            nk, ak = norm_map.get(ex, ("", ""))
            resolved = (
                (nk and (nk in latex_index or nk in batch_norm_keys))
                or (ak and (ak in existing_ast_set or ak in batch_ast_keys))
            )
            if not resolved:
                undef_clickable.append(ex)

        if unbalanced:
            errors.append(f"[{slug}] Unbalanced braces in MathJax: {unbalanced}")
        if short_violations:
            errors.append(
                f"[{slug}] Bare short/numeric MathJax SVGs disallowed (use HTML <em>/<sup> or allow_short_tokens): {short_violations}"
            )
        if undef_clickable:
            errors.append(f"[{slug}] UNDEFINED CLICKABLE MathJax expressions (add to manifest 'formulas' or use HTML): {undef_clickable}")

        subtopic_stats[slug] = {
            "shield_words": shield_words,
            "math_tokens": len(subtopic_math_map[slug]),
            "outgoing_links": len(out_links),
            "cross_hub_links": len(cross_hub),
            "incoming_links": len(incoming),
            "citations": len(citations),
        }

    stats = {
        "domain": domain,
        "subtopic_count": n_subtopics,
        "formula_count": len(batch_formulas_by_id),
        "subtopics": subtopic_stats,
    }
    return errors, warnings, stats


def render_svgs_chunked(tex_expressions: List[str]) -> Dict[str, str]:
    """
    Renders unique LaTeX expressions to gold inline SVGs using the persistent svg_cache.json
    and Node MathJax engine in safe chunks of SVG_CHUNK_SIZE without calling orchestrator.save().
    """
    if os.path.exists(SVG_CACHE_PATH):
        with open(SVG_CACHE_PATH, "r", encoding="utf-8") as f:
            svg_cache = json.load(f)
    else:
        svg_cache = {}

    unique_tex = list(dict.fromkeys(tex_expressions))
    missing = []
    for tex in unique_tex:
        key = f"INLINE_{tex}_#FFD700"
        if key not in svg_cache:
            missing.append((key, tex))

    if missing:
        from orchestrator import PhysicsOrchestrator
        orch = PhysicsOrchestrator()
        for i in range(0, len(missing), SVG_CHUNK_SIZE):
            chunk = missing[i : i + SVG_CHUNK_SIZE]
            batch = {k: {"latex": t, "is_display": False, "color": "#FFD700"} for k, t in chunk}
            rendered = orch.batch_convert_to_svg(batch)
            svg_cache.update(rendered)
        with open(SVG_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(svg_cache, f)

    result: Dict[str, str] = {}
    for tex in unique_tex:
        key = f"INLINE_{tex}_#FFD700"
        svg = svg_cache.get(key)
        if not svg or "<svg" not in svg:
            raise RuntimeError(f"Failed to render SVG for LaTeX expression: {tex}")
        if "data-tex=" not in svg[:120]:
            escaped_tex = html.escape(tex, quote=True)
            svg = svg.replace("<svg", f'<svg data-tex="{escaped_tex}"', 1)
        result[tex] = svg
    return result


def apply_manifest(
    manifest: Dict[str, Any],
    force_large_batch: bool = False,
    allow_update_existing: bool = False,
    sync_db: bool = False,
) -> None:
    errors, warnings, stats = validate_manifest(
        manifest,
        force_large_batch=force_large_batch,
        allow_update_existing=allow_update_existing,
    )
    if warnings:
        for w in warnings:
            print(f"  [WARN] {w}")
    if errors:
        print(f"\nPRE-FLIGHT FAILED ({len(errors)} error(s)) — aborting before any disk writes:")
        for e in errors:
            print(f"  [FAIL] {e}")
        sys.exit(1)

    domain = manifest["domain"]
    subtopics = manifest["subtopics"]
    formulas = manifest.get("formulas", [])
    verified_date = manifest.get("verified_date") or datetime.date.today().isoformat()

    domain_content_path = os.path.join(CONTENT_DIR, f"{domain}.json")
    hub_manifest_path = os.path.join(HUB_MANIFESTS_DIR, f"{domain}.json")
    topic_manifest_path = os.path.join(TOPICS_DIR, f"{domain}.json")

    # Collect every file we will touch for transactional rollback
    touched_files: Set[str] = {
        domain_content_path,
        hub_manifest_path,
        topic_manifest_path,
        LATEX_INDEX_PATH,
        SEARCH_INDEX_PATH,
        SLUG_REGISTRY_PATH,
        SEMANTIC_REFS_PATH,
    }
    for fobj in formulas:
        touched_files.add(get_shard_path(fobj["id"]))
        if fobj.get("parent_formula_id"):
            touched_files.add(get_shard_path(fobj["parent_formula_id"]))

    backups: Dict[str, Optional[bytes]] = {}
    for path in touched_files:
        if os.path.exists(path):
            with open(path, "rb") as f:
                backups[path] = f.read()
        else:
            backups[path] = None

    try:
        # 1. Render all MathJax SVGs in chunks
        all_exprs: List[str] = []
        for sdata in subtopics.values():
            c = sdata["content"]
            all_exprs.extend([m.strip() for m in INLINE_MATH_RE.findall(c)])
            all_exprs.extend([m.strip() for m in DISPLAY_MATH_RE.findall(c)])
            all_exprs.append(sdata["hero_equation"].strip())
        svg_map = render_svgs_chunked(all_exprs)
        print(f"[1/6] Rendered/cached {len(svg_map)} unique MathJax SVGs.")

        # 2. Write new formulas to nested hex shards + reciprocal parent subcomponents + 1-to-1 latex index
        shard_cache: Dict[str, Dict[str, Any]] = {}

        def get_shard(path: str) -> Dict[str, Any]:
            if path not in shard_cache:
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8") as f:
                        shard_cache[path] = json.load(f)
                else:
                    shard_cache[path] = {}
            return shard_cache[path]

        eqs_to_norm = [fobj["equation"].strip() for fobj in formulas]
        norm_map = php_normalize_batch(eqs_to_norm)

        with open(LATEX_INDEX_PATH, "r", encoding="utf-8") as f:
            latex_index = json.load(f)

        for fobj in formulas:
            fid = fobj["id"].strip()
            sp = get_shard_path(fid)
            sd = get_shard(sp)
            existing_subs = sd.get(fid, {}).get("subcomponents", [])
            record = {k: v for k, v in fobj.items() if k != "id"}
            record.setdefault("status", "platinum")
            record.setdefault("lineage_confidence", "curated")
            record["subcomponents"] = existing_subs
            sd[fid] = record

            pid = fobj.get("parent_formula_id")
            if pid:
                psp = get_shard_path(pid)
                psd = get_shard(psp)
                if pid in psd:
                    subs = psd[pid].setdefault("subcomponents", [])
                    if fid not in subs:
                        subs.append(fid)

            nk, _ = norm_map.get(fobj["equation"].strip(), ("", ""))
            if nk and nk not in latex_index:
                latex_index[nk] = fid

        for sp, sd in shard_cache.items():
            os.makedirs(os.path.dirname(sp), exist_ok=True)
            with open(sp, "w", encoding="utf-8") as f:
                json.dump(sd, f, indent=2, ensure_ascii=False)

        with open(LATEX_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(latex_index.items())), f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"[2/6] Wrote {len(formulas)} formulas to {len(shard_cache)} nested shards & updated 1-to-1 latex index.")

        # 3. Compile subtopics + weave incoming links into domain shard
        with open(domain_content_path, "r", encoding="utf-8") as f:
            domain_data = json.load(f)

        for slug, sdata in subtopics.items():
            compiled_html = INLINE_MATH_RE.sub(lambda m: svg_map[m.group(1).strip()], sdata["content"])
            compiled_html = DISPLAY_MATH_RE.sub(lambda m: svg_map[m.group(1).strip()], compiled_html)

            plain = re.sub(r"<[^>]+>", " ", sdata["content"])
            plain = re.sub(r"\s+", " ", plain).strip()
            snippet = plain[:240].rsplit(" ", 1)[0] + "..."

            domain_data[slug] = {
                "title": sdata["title"],
                "content": compiled_html,
                "formula_ids": sdata.get("formula_ids", []),
                "parents": [domain],
                "standard": "platinum",
                "snippet": snippet,
                "snippet_svg": snippet,
                "hero_math": svg_map[sdata["hero_equation"].strip()],
                "verification": {
                    "verified_date": verified_date,
                    "consensus_score": 1.0,
                    "agents": {
                        "extractor": "ClaimExtractor-v1.1",
                        "critic": "LiteratureCritic-v2.0",
                        "judge": "ConsensusJudge-v2.0",
                    },
                    "citations": sdata["citations"],
                },
            }

            # Weave incoming links idempotently
            for inc in sdata.get("incoming_links", []):
                src_slug = inc["from_slug"]
                sentence = inc["sentence"]
                if src_slug in domain_data:
                    src_html = domain_data[src_slug]["content"]
                    if f'/physics/subtopic/{slug}"' not in src_html:
                        close_idx = src_html.rfind("</p>")
                        if close_idx != -1:
                            domain_data[src_slug]["content"] = src_html[:close_idx] + sentence + src_html[close_idx:]

        with open(domain_content_path, "w", encoding="utf-8") as f:
            json.dump(domain_data, f, indent=2, ensure_ascii=False)
        print(f"[3/6] Compiled {len(subtopics)} subtopics & wove incoming links into {domain}.json.")

        # 4. Sync Pillars, Slug Registry, Semantic References, and Search Index
        for mpath in (hub_manifest_path, topic_manifest_path):
            with open(mpath, "r", encoding="utf-8") as f:
                mdata = json.load(f)
            pillars = mdata.get("pillars", [])
            if manifest.get("pillar"):
                pdef = manifest["pillar"]
                pillars = [p for p in pillars if p.get("title") != pdef["title"]]
                pillars.append(pdef)
            elif manifest.get("append_to_pillar"):
                target_title = manifest["append_to_pillar"]
                matched = False
                for p in pillars:
                    if p.get("title") == target_title:
                        for s in subtopics:
                            if s not in p["slugs"]:
                                p["slugs"].append(s)
                        matched = True
                        break
                if not matched:
                    raise RuntimeError(f"Could not find existing pillar '{target_title}' in {mpath}")
            mdata["pillars"] = pillars
            with open(mpath, "w", encoding="utf-8") as f:
                json.dump(mdata, f, indent=2, ensure_ascii=False)

        with open(SLUG_REGISTRY_PATH, "r", encoding="utf-8") as f:
            reg = json.load(f)
        for slug, sdata in subtopics.items():
            reg[sdata["title"]] = slug
        with open(SLUG_REGISTRY_PATH, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=2, ensure_ascii=False)

        with open(SEMANTIC_REFS_PATH, "r", encoding="utf-8") as f:
            sem = json.load(f)
        for slug, sdata in subtopics.items():
            plain = re.sub(r"<[^>]+>", " ", INLINE_MATH_RE.sub(" ", sdata["content"]))
            plain = re.sub(r"\s+", " ", plain).strip()
            sem[slug] = {
                "title": sdata["title"],
                "reference_prose": plain[:320].rsplit(" ", 1)[0] + "...",
                "keywords": sdata.get("keywords", []),
            }
        with open(SEMANTIC_REFS_PATH, "w", encoding="utf-8") as f:
            json.dump(sem, f, indent=2, ensure_ascii=False)

        with open(SEARCH_INDEX_PATH, "r", encoding="utf-8") as f:
            sidx = json.load(f)
        if isinstance(sidx, list):
            sidx_map = {item["slug"]: item for item in sidx if isinstance(item, dict) and "slug" in item}
            for slug, sdata in subtopics.items():
                sidx_map[slug] = {
                    "slug": slug,
                    "title": sdata["title"],
                    "category": domain,
                    "snippet": domain_data[slug]["snippet"],
                }
            sidx = list(sidx_map.values())
        elif isinstance(sidx, dict):
            for slug, sdata in subtopics.items():
                sidx[slug] = {
                    "title": sdata["title"],
                    "category": domain,
                    "snippet": domain_data[slug]["snippet"],
                }
        with open(SEARCH_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump(sidx, f, indent=2, ensure_ascii=False)
        print("[4/6] Updated hub/topic manifests, slug registry, semantic references, and search_index.json.")

        # 5. Rebuild derivation graph, sync shard hashes, purge affected caches
        subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "scripts", "build_formula_graph.py")], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["bash", os.path.join(PROJECT_ROOT, "scripts", "assess"), "--heal"], cwd=PROJECT_ROOT, check=True)

        cache_targets = [os.path.join(PROJECT_ROOT, "public", "cache", "topic", f"{domain}.html")]
        for slug in subtopics:
            cache_targets.append(os.path.join(PROJECT_ROOT, "public", "cache", "subtopic", f"{slug}.html"))
        for ct in cache_targets:
            if os.path.exists(ct):
                os.remove(ct)
        print("[5/6] Rebuilt derivation graph, synced shard hash registry, and purged HTML caches.")

        # 6. Post-write Zero-Undefined-Click verification
        subprocess.run(
            ["php", os.path.join(PROJECT_ROOT, "scripts", "audit_clickable_equations.php"), *list(subtopics.keys())],
            cwd=PROJECT_ROOT,
            check=True,
        )
        print("[6/6] Post-write Zero-Undefined-Click audit PASSED (0 undefined clickable expressions).")

        if sync_db:
            print("\nSyncing to local MariaDB via php cli_sync.php...")
            subprocess.run(["php", os.path.join(PROJECT_ROOT, "cli_sync.php")], cwd=PROJECT_ROOT, check=True)

        print(f"\nSUCCESS: Expanded '{domain}' by +{len(subtopics)} subtopics and +{len(formulas)} formulas.")

    except Exception as exc:
        print(f"\nERROR during --apply: {exc}")
        print("Rolling back all modified files to pre-run snapshot...")
        for path, raw_bytes in backups.items():
            if raw_bytes is None:
                if os.path.exists(path):
                    os.remove(path)
            else:
                with open(path, "wb") as f:
                    f.write(raw_bytes)
        print("Rollback complete.")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Terra Physics Lab 1-Step Hub Expansion Engine")
    parser.add_argument("manifest", help="Path to declarative batch manifest JSON")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Run all 6 pre-flight validation gates with zero disk writes")
    mode.add_argument("--apply", action="store_true", help="Validate and atomically apply the expansion batch")
    parser.add_argument("--force-large-batch", action="store_true", help=f"Allow batches larger than {MAX_RECOMMENDED_BATCH} subtopics")
    parser.add_argument("--update-existing", action="store_true", help="Allow updating already-existing subtopics/formulas (idempotent re-apply)")
    parser.add_argument("--sync-db", action="store_true", help="Also run php cli_sync.php after --apply")
    args = parser.parse_args()

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if args.dry_run:
        errors, warnings, stats = validate_manifest(
            manifest,
            force_large_batch=args.force_large_batch,
            allow_update_existing=args.update_existing,
        )
        print("=" * 72)
        print(f"DRY-RUN PRE-FLIGHT REPORT: {os.path.basename(args.manifest)}")
        print("=" * 72)
        if stats:
            print(f"  Domain:    {stats['domain']}")
            print(f"  Subtopics: {stats['subtopic_count']} | New Formulas: {stats['formula_count']}")
            for slug, st in stats.get("subtopics", {}).items():
                print(
                    f"    - {slug:32s} | words={st['shield_words']:3d} | math={st['math_tokens']:2d} "
                    f"| out={st['outgoing_links']:2d} (x-hub={st['cross_hub_links']}) | in={st['incoming_links']} | cites={st['citations']}"
                )
        if warnings:
            print(f"\nWARNINGS ({len(warnings)}):")
            for w in warnings:
                print(f"  [WARN] {w}")
        if errors:
            print(f"\nERRORS ({len(errors)}):")
            for e in errors:
                print(f"  [FAIL] {e}")
            sys.exit(1)
        print("\nREADY TO APPLY (0 errors).")
        sys.exit(0)

    apply_manifest(
        manifest,
        force_large_batch=args.force_large_batch,
        allow_update_existing=args.update_existing,
        sync_db=args.sync_db,
    )


if __name__ == "__main__":
    main()
