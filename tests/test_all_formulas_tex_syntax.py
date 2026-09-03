import json
import os
import re
import glob
import pytest

SHARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "config", "content", "formulas")

def get_all_shard_formulas():
    shard_files = glob.glob(os.path.join(SHARDS_DIR, "**", "*.json"), recursive=True)
    root_shard_files = glob.glob(os.path.join(SHARDS_DIR, "*.json"))
    all_files = shard_files + root_shard_files

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

from scripts.lib.delimiters import strip_math_blocks, count_unescaped_dollars

@pytest.mark.parametrize("fid, formula", ALL_FORMULAS[:1000])  # Sample check for fast CI performance
def test_formula_tex_dollar_balance(fid, formula):
    fields = ["conceptual_definition", "interpretation", "limits_and_boundary", "symmetry_origin"]
    for field in fields:
        text = formula.get(field, "")
        if not text:
            continue
        dollar_count = count_unescaped_dollars(text)
        assert dollar_count % 2 == 0, f"Formula [{fid}] field [{field}] has unclosed dollar signs (count={dollar_count}). Text: {text[:100]}..."

@pytest.mark.parametrize("fid, formula", ALL_FORMULAS[:1000])
def test_formula_no_mangled_tex_macros(fid, formula):
    fields = ["conceptual_definition", "interpretation", "limits_and_boundary", "symmetry_origin"]
    corrupted_pattern = re.compile(r"\\sqrt\$\{|\$g_\{\$\\mu\$ u\}|\\to'|\x27\+\$\S+\x27")
    for field in fields:
        text = formula.get(field, "")
        if not text:
            continue
        match = corrupted_pattern.search(text)
        assert match is None, f"Formula [{fid}] field [{field}] contains corrupted TeX macro '{match.group(0)}'."

@pytest.mark.parametrize("fid, formula", ALL_FORMULAS[:1000])
def test_formula_no_leaked_tex_macros(fid, formula):
    fields = ["conceptual_definition", "interpretation", "limits_and_boundary", "symmetry_origin"]
    tex_macro_check = re.compile(r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])")
    for field in fields:
        text = formula.get(field, "")
        if not text:
            continue
        text_no_math = strip_math_blocks(text)
        match = tex_macro_check.search(text_no_math)
        assert match is None, f"Formula [{fid}] field [{field}] leaks TeX macro '{match.group(0)}' outside math mode."


