import glob
import json
import os
import re
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

def get_all_shard_files():
    shards = glob.glob(os.path.join(FORMULAS_DIR, "*", "*.json"))
    shards.extend(glob.glob(os.path.join(FORMULAS_DIR, "*.json")))
    return shards

def load_all_formulas():
    formulas = []
    for filepath in get_all_shard_files():
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    for formula_id, f_data in data.items():
                        if isinstance(f_data, dict):
                            f_data["_id"] = formula_id
                            f_data["_filepath"] = filepath
                            formulas.append(f_data)
            except Exception as e:
                pytest.fail(f"Failed to parse JSON file {filepath}: {e}")
    return formulas

ALL_FORMULAS = load_all_formulas()

def test_formulas_exist():
    assert len(ALL_FORMULAS) > 1000, f"Expected >1000 formulas, found {len(ALL_FORMULAS)}"

def test_no_literal_newline_artifacts():
    corrupted = []
    for f in ALL_FORMULAS:
        text = f"{f.get('conceptual_definition', '')} {f.get('interpretation', '')} {f.get('limits_and_boundary', '')}"
        if re.search(r'\bLagrangian,\s*\\n,', text, re.IGNORECASE) or re.search(r'\\n\s*=\s*0\s*for all\s*\\n', text, re.IGNORECASE):
            corrupted.append(f.get("_id"))
    assert len(corrupted) == 0, f"Found literal \\n artifacts in formulas: {corrupted}"

def test_no_corrupted_unicode_ocr_glyphs():
    corrupted = []
    bad_glyphs = ["∨_C", "∫²_S", "⁵X⁰", "⁵Y⁰", "⁵Z⁰", "µ₀", "μ₀", "⁲⁽"]
    for f in ALL_FORMULAS:
        text = json.dumps(f, ensure_ascii=False)
        for glyph in bad_glyphs:
            if glyph in text:
                corrupted.append((f.get("_id"), glyph))
                break
    assert len(corrupted) == 0, f"Found corrupted OCR/Unicode glyphs in formulas: {corrupted}"

def test_no_corrupted_titles():
    corrupted = []
    for f in ALL_FORMULAS:
        title = f.get("title", "")
        if "Hamilton\\delta" in title or "\\delta\\delta S-Field" in title:
            corrupted.append((f.get("_id"), title))
    assert len(corrupted) == 0, f"Found corrupted titles: {corrupted}"

def test_no_raw_unwrapped_tex_macros():
    unwrapped = []
    for f in ALL_FORMULAS:
        text = f"{f.get('conceptual_definition', '')} {f.get('interpretation', '')}"
        for line in text.split("\n"):
            for match in re.finditer(r"\\(frac|oint|iint)\b", line):
                st = match.start()
                db = len(re.findall(r"(?<!\\)\$", line[:st]))
                da = len(re.findall(r"(?<!\\)\$", line[st:]))
                pb = len(re.findall(r"\\\(", line[:st]))
                pa = len(re.findall(r"\\\)", line[st:]))
                if (db == 0 and pb == 0) and (da == 0 and pa == 0):
                    unwrapped.append((f.get("_id"), match.group(0)))
                    break
    assert len(unwrapped) == 0, f"Found unwrapped TeX macros in prose: {unwrapped}"

def test_no_html_markup_in_formula_equations():
    corrupted = []
    for f in ALL_FORMULAS:
        eq = f.get("equation", "")
        if re.search(r"<\/?(a|strong|em|code|div|span|p)\b", eq, re.IGNORECASE) or "href=" in eq or "subtopic-link" in eq or "latex.codecogs" in eq:
            corrupted.append((f.get("_id"), eq))
    assert len(corrupted) == 0, f"Found HTML markup or raw image links in formula equation fields: {corrupted}"

def test_no_html_inside_subtopic_svg_data_tex():
    content_dir = os.path.join(PROJECT_ROOT, "app", "config", "content")
    corrupted_svgs = []
    for file_name in os.listdir(content_dir):
        if file_name.endswith(".json") and file_name != "search_index.json":
            file_path = os.path.join(content_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r'<svg\s+[^>]*data-tex=["\']([^"\']*)["\']', content, re.IGNORECASE)
                for tex in matches:
                    if "href=" in tex or "<a" in tex or "&lt;a" in tex or "subtopic-link" in tex:
                        corrupted_svgs.append((file_name, tex[:80]))
    assert len(corrupted_svgs) == 0, f"Found HTML tags embedded inside SVG data-tex attributes: {corrupted_svgs}"

