import json
import os
import re
import glob
import pytest

SHARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "config", "content", "formulas")

def get_all_shard_formulas():
    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*", "shard_*.json")))
    all_files = shard_files

    formulas = []
    for fpath in all_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for fid, fval in data.items():
                        if isinstance(fval, dict):
                            formulas.append((fid, fval))
        except Exception:
            continue
    return formulas

ALL_FORMULAS = get_all_shard_formulas()

from scripts.lib.delimiters import (
    strip_math_blocks,
    count_unescaped_dollars,
    validate_narrative_delimiters,
)

NARRATIVE_FIELDS = [
    "conceptual_definition",
    "intuitive_summary",
    "interpretation",
    "limits_and_boundary",
    "symmetry_origin",
]

def test_all_formulas_count():
    assert len(ALL_FORMULAS) >= 14600, f"Expected >= 14600 formulas, found {len(ALL_FORMULAS)}"

def test_all_formulas_tex_dollar_balance():
    corrupted = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            dollar_count = count_unescaped_dollars(text)
            if dollar_count % 2 != 0:
                corrupted.append((fid, field, dollar_count, text[:100]))
    assert len(corrupted) == 0, f"Found {len(corrupted)} unclosed dollar signs: {corrupted[:10]}"

def test_all_formulas_narrative_delimiters():
    violations = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            errs = validate_narrative_delimiters(text)
            for err in errs:
                violations.append((fid, field, err))
    assert len(violations) == 0, f"Found {len(violations)} formula narrative delimiter errors: {violations[:10]}"

def test_all_formulas_no_mangled_tex_macros():
    corrupted_pattern = re.compile(r"\\sqrt\$\{|\$g_\{\$\\mu\$ u\}|\\to'|'\+\$\S+'")
    corrupted = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            match = corrupted_pattern.search(text)
            if match:
                corrupted.append((fid, field, match.group(0)))
    assert len(corrupted) == 0, f"Found {len(corrupted)} corrupted TeX macro instances: {corrupted[:10]}"

def test_all_formulas_no_leaked_tex_macros():
    tex_macro_check = re.compile(
        r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])"
    )
    leaked = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            text_no_math = strip_math_blocks(text)
            match = tex_macro_check.search(text_no_math)
            if match:
                leaked.append((fid, field, match.group(0), text[:80]))

    assert len(leaked) == 0, f"Found {len(leaked)} leaked TeX macros outside math mode: {leaked[:10]}"






