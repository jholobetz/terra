import glob
import json
import os
import re
import subprocess
import pytest
from scripts.lib.delimiters import strip_math_blocks, validate_narrative_delimiters

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
        outside = strip_math_blocks(text)
        match = re.search(r"\\(frac|oint|iint)\b", outside)
        if match:
            unwrapped.append((f.get("_id"), match.group(0)))
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

def test_formula_narrative_math_delimiters():
    corrupted_formulas = []
    fields_to_check = ["conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary"]
    
    for f in ALL_FORMULAS:
        formula_id = f.get("_id")
        for key in fields_to_check:
            text = f.get(key, "")
            if not text or not isinstance(text, str):
                continue
            errors = validate_narrative_delimiters(text)
            for err in errors:
                corrupted_formulas.append((formula_id, key, err))

    assert len(corrupted_formulas) == 0, f"Found {len(corrupted_formulas)} formula narrative delimiter errors: {corrupted_formulas[:10]}"



def fetch_mariadb_formulas():
    autoload_path = os.path.join(PROJECT_ROOT, "vendor", "autoload.php")
    config_path = os.path.join(PROJECT_ROOT, "app", "config", "config.php")
    
    php_code = f'''
    require '{autoload_path}';
    $config = require '{config_path}';
    $dbConfig = $config['database'] ?? [];
    $dsn = 'mysql:host=' . ($dbConfig['host'] ?? '127.0.0.1') . ';dbname=' . ($dbConfig['dbname'] ?? 'physicslab') . ';charset=utf8mb4';
    try {{
        $pdo = new PDO($dsn, $dbConfig['user'] ?? 'doc', $dbConfig['password'] ?? '', [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION]);
        $stmt = $pdo->query('SELECT id, equation, interpretation, symmetry_origin, limits_and_boundary FROM formulas');
        $data = [];
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {{
            $data[$row['id']] = $row;
        }}
        echo json_encode($data, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    }} catch (\\Throwable $e) {{
        echo json_encode(null);
    }}
    '''
    res = subprocess.run(["php", "-r", php_code], capture_output=True, text=True, cwd=PROJECT_ROOT)
    if res.returncode == 0 and res.stdout.strip():
        try:
            return json.loads(res.stdout.strip())
        except Exception:
            return None
    return None


def test_disk_to_database_integrity():
    db_map = fetch_mariadb_formulas()
    if db_map is None:
        pytest.skip("MariaDB database is offline or unreachable.")

    mismatches = []
    fields_to_compare = ["interpretation", "symmetry_origin", "limits_and_boundary"]

    for f in ALL_FORMULAS:
        formula_id = f.get("_id")
        if not formula_id or formula_id not in db_map:
            continue

        db_row = db_map[formula_id]
        for key in fields_to_compare:
            shard_val = (f.get(key) or "").strip()
            db_val = (db_row.get(key) or "").strip()
            if shard_val != db_val:
                mismatches.append((formula_id, key, f"Shard: '{shard_val[:30]}...' != MariaDB: '{db_val[:30]}...'"))

    assert len(mismatches) == 0, f"Found {len(mismatches)} desynchronizations between disk shards and MariaDB: {mismatches[:10]}"

def test_semantic_variables_schema_strict():
    """Asserts that all formula records across all 256 shards have valid semantic_variables objects without corrupt key names or invalid types."""
    invalid_schema = []

    for f in ALL_FORMULAS:
        formula_id = f.get("_id") or f.get("id", "unknown")
        sem_vars = f.get("semantic_variables")

        if not isinstance(sem_vars, dict):
            invalid_schema.append(f"{formula_id}: type is {type(sem_vars).__name__}, expected dict")
            continue

        for key in sem_vars.keys():
            if "$" in key:
                invalid_schema.append(f"{formula_id}: variable key contains raw '$' delimiter: '{key}'")

    assert len(invalid_schema) == 0, f"Found {len(invalid_schema)} semantic_variables schema violations: {invalid_schema[:10]}"
