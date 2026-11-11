import json
import os
import re
import subprocess
import pytest
from scripts.lib.delimiters import (
    validate_narrative_delimiters,
    find_html_in_math,
)
from tests.conftest import get_cached_formulas

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALL_FORMULAS = get_cached_formulas()

NARRATIVE_FIELDS = [
    "conceptual_definition",
    "intuitive_summary",
    "interpretation",
    "symmetry_origin",
    "limits_and_boundary",
]


def test_formulas_exist():
    assert len(ALL_FORMULAS) >= 14600, f"Expected >= 14600 formulas, found {len(ALL_FORMULAS)}"


def test_no_literal_newline_artifacts():
    from scripts.lib.delimiters import strip_math_blocks
    corrupted = []
    boilerplate = []
    markdown_artifacts = []
    for f in ALL_FORMULAS:
        fid = f.get("_id")
        text = f"{f.get('conceptual_definition', '')} {f.get('interpretation', '')} {f.get('limits_and_boundary', '')}"
        if re.search(r'\bLagrangian,\s*\\n,', text, re.IGNORECASE) or re.search(r'\\n\s*=\s*0\s*for all\s*\\n', text, re.IGNORECASE):
            corrupted.append(fid)
        for field in ("interpretation", "conceptual_definition", "intuitive_summary", "symmetry_origin", "limits_and_boundary", "description"):
            val = f.get(field) or ""
            if not isinstance(val, str) or not val:
                continue
            no_math = strip_math_blocks(val)
            if re.search(r"interpreted\s+as\s+follows\s*:", no_math, re.IGNORECASE):
                boilerplate.append((fid, field))
            if re.search(r"\*\*[^*]+\*\*", no_math) or re.search(r"(?:^|\n)\s*[\*-]\s+", no_math):
                markdown_artifacts.append((fid, field))
    assert len(corrupted) == 0, f"Found literal \\n artifacts in formulas: {corrupted}"
    assert len(boilerplate) == 0, f"Found 'interpreted as follows:' boilerplate in formulas: {boilerplate[:10]}"
    assert len(markdown_artifacts) == 0, f"Found raw Markdown (**bold** or bullet list) in formulas: {markdown_artifacts[:10]}"


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


def test_no_mangled_tex_macros():
    corrupted_pattern = re.compile(r"\\sqrt\$\{|\$g_\{\$\\mu\$ u\}|\\to'|'\+\$\S+'")
    corrupted = []
    for f in ALL_FORMULAS:
        fid = f.get("_id")
        for field in NARRATIVE_FIELDS:
            text = f.get(field, "")
            if not text or not isinstance(text, str):
                continue
            match = corrupted_pattern.search(text)
            if match:
                corrupted.append((fid, field, match.group(0)))
    assert len(corrupted) == 0, f"Found {len(corrupted)} corrupted TeX macro instances: {corrupted[:10]}"


def test_no_html_markup_in_formula_equations():
    corrupted = []
    for f in ALL_FORMULAS:
        eq = f.get("equation", "")
        violations = find_html_in_math(eq, is_raw_tex=True)
        if violations or "latex.codecogs" in eq:
            corrupted.append((f.get("_id"), eq, violations))
    assert len(corrupted) == 0, f"Found HTML markup or raw image links in formula equation fields: {corrupted}"

def test_no_html_inside_subtopic_svg_data_tex():
    content_dir = os.path.join(PROJECT_ROOT, "app", "config", "content")
    corrupted_svgs = []
    for file_name in os.listdir(content_dir):
        if file_name.endswith(".json") and file_name not in [
            "search_index.json", "categories.json", "constants.json", "entities.json",
            "compiled_trie_regex.json", "notation.json", "particles.json", "pillar_profiles.json",
            "formula_aliases.json", "formulas_latex_index.json", "unindexed_subcomponents.json",
            "subcomponents_checkpoint.json", "formula_derivation_graph.json", "formulas_hash_registry.json"
        ]:
            file_path = os.path.join(content_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                matches = re.findall(r'<svg\s+[^>]*data-tex=["\']([^"\']*)["\']', content, re.IGNORECASE)
                for tex in matches:
                    violations = find_html_in_math(tex)
                    if violations:
                        corrupted_svgs.append((file_name, tex[:80], violations))
    assert len(corrupted_svgs) == 0, f"Found HTML tags embedded inside SVG data-tex attributes: {corrupted_svgs}"

def test_formula_narrative_math_delimiters():
    corrupted_formulas = []
    fields_to_check = ["description", "conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary"]
    
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
    error_reporting(0);
    ini_set('display_errors', '0');
    ini_set('memory_limit', '512M');
    require '{autoload_path}';
    $config = require '{config_path}';
    $dbConfig = $config['database'] ?? [];
    $dsn = 'mysql:host=' . ($dbConfig['host'] ?? '127.0.0.1') . ';dbname=' . ($dbConfig['dbname'] ?? 'physicslab') . ';charset=utf8mb4';
    try {{
        $pdo = new PDO($dsn, $dbConfig['user'] ?? 'doc', $dbConfig['password'] ?? '', [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        ]);
        $stmt = $pdo->query('SELECT id, equation, description, conceptual_definition, intuitive_summary, interpretation, symmetry_origin, limits_and_boundary, category, lineage_confidence, record_type, equation_family FROM formulas');
        while ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {{
            echo json_encode($row, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "\\n";
        }}
    }} catch (\\Throwable $e) {{
        echo "__DB_ERROR__";
    }}
    '''
    res = subprocess.run(["php", "-r", php_code], capture_output=True, text=True, cwd=PROJECT_ROOT)
    out = res.stdout.strip()
    if res.returncode == 0 and out and not out.startswith("__DB_ERROR__"):
        try:
            data = {}
            for line in out.splitlines():
                if line:
                    row = json.loads(line)
                    data[row["id"]] = row
            return data
        except Exception:
            return None
    return None


def test_disk_to_database_integrity():
    db_map = fetch_mariadb_formulas()
    if db_map is None:
        pytest.skip("MariaDB database is offline or unreachable.")

    mismatches = []
    missing_in_db = []
    fields_to_compare = [
        "description",
        "conceptual_definition",
        "intuitive_summary",
        "interpretation",
        "symmetry_origin",
        "limits_and_boundary",
        "category",
        "lineage_confidence",
        "record_type",
        "equation_family",
    ]

    for f in ALL_FORMULAS:
        formula_id = f.get("_id")
        if not formula_id:
            continue
        if formula_id not in db_map:
            missing_in_db.append(formula_id)
            continue

        db_row = db_map[formula_id]
        for key in fields_to_compare:
            shard_val = (f.get(key) or "").strip()
            db_val = (db_row.get(key) or "").strip()
            if shard_val != db_val:
                mismatches.append((formula_id, key, f"Shard: '{shard_val[:30]}...' != MariaDB: '{db_val[:30]}...'"))

    assert len(missing_in_db) == 0, f"Found {len(missing_in_db)} shard formulas missing in MariaDB: {missing_in_db[:10]}"
    assert len(mismatches) == 0, f"Found {len(mismatches)} desynchronizations between disk shards and MariaDB: {mismatches[:10]}"

def test_semantic_variables_schema_strict():
    """Asserts that all formula records across all 256 shards have valid semantic_variables objects without corrupt key names, self-referential names, or fallback placeholders."""
    invalid_schema = []
    fallback_re = re.compile(
        r"\b(Physical Quantity|Constant or Parameter|Dimensionless Parameter|"
        r"Vector / Tensor Component|Differential Quantity|State Function or Operator|Unknown Variable)\b",
        re.IGNORECASE,
    )

    for f in ALL_FORMULAS:
        formula_id = f.get("_id") or f.get("id", "unknown")
        sem_vars = f.get("semantic_variables")

        if not isinstance(sem_vars, dict):
            invalid_schema.append(f"{formula_id}: type is {type(sem_vars).__name__}, expected dict")
            continue

        for key, vinfo in sem_vars.items():
            if "$" in key:
                invalid_schema.append(f"{formula_id}: variable key contains raw '$' delimiter: '{key}'")
            if key.endswith("\\") or key.count("{") != key.count("}"):
                invalid_schema.append(f"{formula_id}: variable key has malformed braces or trailing backslash: '{key}'")
            vname = (vinfo.get("name") or "").strip() if isinstance(vinfo, dict) else str(vinfo).strip()
            clean_key = key.strip("$\\ ")
            if not vname or len(vname) <= 1 or vname == key.strip() or vname == clean_key:
                invalid_schema.append(f"{formula_id}: variable '{key}' has self-referential or 1-char name: '{vname}'")
            elif fallback_re.search(vname):
                invalid_schema.append(f"{formula_id}: variable '{key}' has generic fallback name: '{vname}'")
            if isinstance(vinfo, dict):
                vdesc = (vinfo.get("description") or "").strip()
                if vdesc == "Physics variable or parameter." or (0 < len(vdesc) < 10):
                    invalid_schema.append(f"{formula_id}: variable '{key}' has stub description: '{vdesc}'")

    assert len(invalid_schema) == 0, f"Found {len(invalid_schema)} semantic_variables schema violations: {invalid_schema[:10]}"


def test_no_placeholder_titles_or_templated_prefixes():
    """Enforces Priority 2 & Priority 3 anti-regression gates across all 256 shards (14,684 formulas)."""
    violations = []
    valid_categories = {
        "astrophysics", "classical-mechanics", "condensed-matter", "electromagnetism",
        "fluids-nonlinear", "mathematical-methods", "philosophy-of-physics", "quantum-physics",
        "relativity", "standard-model", "theoretical-physics", "thermodynamics-statistical-mechanics"
    }
    bad_title_re = re.compile(r"^(?:custom physical relation|technical relation\b|unknown formula$|missing terms$)", re.IGNORECASE)
    hex_byte_re = re.compile(r"0x[0-9A-Fa-f]{2}")
    non_canonical_delim_re = re.compile(r"\\\(|\\\)|\\\[|\\\]|\$\$")
    html_or_md_re = re.compile(r"<(?:ul|ol|li|b|i|strong|em|p|br)\b|\*\*[^*]+\*\*", re.IGNORECASE)
    split_math_re = re.compile(r"\$\\(?:hat|vec|bar|tilde|dot|ddot|mathbf|mathcal|mathrm|text|frac|sqrt)\$\{\$")
    bad_prefix_re = re.compile(
        r"^(?:In the study of\s+.+?formalizes a core mathematical condition:|"
        r"Expresses the quantitative condition\s+\$.+?\$\s+governing|"
        r"In the physical context of\s+.+?links the active degrees of freedom|"
        r"Arises within\s+.+?through the transformation and invariance structure of)",
        re.DOTALL,
    )

    valid_lineage_confidence = {"curated", "cas_verified", "root_axiom", "heuristic"}
    valid_derivation_types = {
        "AXIOMATIC_FOUNDATION", "DEFINITION", "DERIVED_FROM", "SPECIAL_CASE",
        "GENERALIZATION", "LIMITING_CASE", "APPROXIMATION", "EMPIRICAL_LAW",
        "THEORETICAL_DERIVATION", "PHENOMENOLOGICAL",
    }
    prose_fields = ("description", "conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary")
    for f in ALL_FORMULAS:
        fid = f.get("_id") or f.get("id", "unknown")
        title = (f.get("title") or "").strip()
        eq = (f.get("equation") or "").strip()
        if not title or bad_title_re.search(title):
            violations.append((fid, "title", f"Placeholder or empty title: '{title}'"))
        if hex_byte_re.search(title):
            violations.append((fid, "title", f"Contains raw hex-byte sequence: '{title}'"))
        if non_canonical_delim_re.search(title):
            violations.append((fid, "title", f"Contains non-canonical math delimiter in title: '{title}'"))
        if hex_byte_re.search(eq):
            violations.append((fid, "equation", f"Contains raw hex-byte sequence: '{eq}'"))
        cat = (f.get("category") or "").strip()
        if cat not in valid_categories:
            violations.append((fid, "category", f"Invalid or missing category: '{cat}'"))
        rt = (f.get("record_type") or "").strip()
        if rt not in ("equation", "symbol_or_term"):
            violations.append((fid, "record_type", f"Invalid or missing record_type: '{rt}'"))
        num_keys = [k for k in f.keys() if str(k).isdigit()]
        if num_keys:
            violations.append((fid, "numeric_keys", f"Leaked numeric keys in shard record: {num_keys}"))
        lc = (f.get("lineage_confidence") or "").strip()
        if lc not in valid_lineage_confidence:
            violations.append((fid, "lineage_confidence", f"Invalid or missing lineage_confidence: '{lc}'"))
        dt = (f.get("derivation_type") or "").strip()
        if dt not in valid_derivation_types:
            violations.append((fid, "derivation_type", f"Non-canonical derivation_type: '{dt}'"))
        cv = f.get("cas_validation")
        if isinstance(cv, dict) and cv.get("status") in ("INHOMOGENEOUS", "UNVERIFIED"):
            violations.append((fid, "cas_validation", f"Residual uncertified CAS status in shard: '{cv.get('status')}'"))
        seen_vals = {}
        for field in prose_fields:
            val = (f.get(field) or "").strip()
            min_len = 35 if field == "symmetry_origin" else 20
            if len(val) < min_len:
                violations.append((fid, field, f"Field too short ({len(val)} < {min_len} chars): '{val}'"))
            elif bad_prefix_re.match(val):
                violations.append((fid, field, f"Contains legacy mechanical boilerplate prefix: '{val[:55]}...'"))
            if hex_byte_re.search(val):
                violations.append((fid, field, f"Contains raw hex-byte sequence in {field}"))
            if non_canonical_delim_re.search(val):
                violations.append((fid, field, f"Contains non-canonical math delimiter in {field}"))
            if html_or_md_re.search(val):
                violations.append((fid, field, f"Contains raw HTML tag or Markdown bold in {field}"))
            if split_math_re.search(val):
                violations.append((fid, field, f"Contains split-command math delimiter in {field}"))
            if val in seen_vals:
                violations.append((fid, field, f"Verbatim duplicate of {seen_vals[val]}"))
            elif val:
                seen_vals[val] = field

    assert len(violations) == 0, f"Found {len(violations)} placeholder title or templated prose violations: {violations[:10]}"


def test_derived_graph_and_latex_index_parity():
    """Enforces Priority 4 node-count & provenance parity across formula_derivation_graph.json(.gz) and formulas_latex_index.json."""
    import gzip

    shard_ids = {f["_id"] for f in ALL_FORMULAS if f.get("_id")}
    dag_json_path = os.path.join(PROJECT_ROOT, "app", "config", "formula_derivation_graph.json")
    dag_gz_path = os.path.join(PROJECT_ROOT, "app", "config", "formula_derivation_graph.json.gz")
    latex_idx_path = os.path.join(PROJECT_ROOT, "app", "config", "formulas_latex_index.json")

    assert os.path.exists(dag_json_path), "Missing formula_derivation_graph.json"
    assert os.path.exists(dag_gz_path), "Missing formula_derivation_graph.json.gz"
    assert os.path.exists(latex_idx_path), "Missing formulas_latex_index.json"

    with open(dag_json_path, "r", encoding="utf-8") as f:
        dag = json.load(f)
    with gzip.open(dag_gz_path, "rt", encoding="utf-8") as gf:
        dag_gz = json.load(gf)

    nodes = dag.get("nodes", {})
    assert dag.get("metadata") == dag_gz.get("metadata"), "Uncompressed and gzipped derivation graph metadata diverged"
    assert len(nodes) == len(dag_gz.get("nodes", {})), "Uncompressed and gzipped derivation graph node counts diverged"

    missing_in_dag = sorted(shard_ids - set(nodes.keys()))
    extra_in_dag = sorted(set(nodes.keys()) - shard_ids)
    assert not missing_in_dag, f"Found {len(missing_in_dag)} shard formulas missing from derivation graph: {missing_in_dag[:10]}"
    assert not extra_in_dag, f"Found {len(extra_in_dag)} dangling nodes in derivation graph: {extra_in_dag[:10]}"

    valid_conf = {"curated", "cas_verified", "root_axiom", "heuristic"}
    missing_prov = [
        nid for nid, nd in nodes.items()
        if nd.get("lineage_confidence") not in valid_conf
        or nd.get("record_type") not in ("equation", "symbol_or_term")
        or not isinstance(nd.get("cas_verified"), bool)
    ]
    assert not missing_prov, f"Found {len(missing_prov)} graph nodes missing provenance fields: {missing_prov[:10]}"

    unmapped_nodes = [nid for nid, nd in nodes.items() if nd.get("domain") == "unmapped"]
    assert not unmapped_nodes, f"Found {len(unmapped_nodes)} unmapped domain nodes in derivation graph: {unmapped_nodes[:10]}"

    with open(latex_idx_path, "r", encoding="utf-8") as lf:
        latex_idx = json.load(lf)

    dangling_targets = []
    hex_residue_keys = []
    for k, target in latex_idx.items():
        targets = target if isinstance(target, list) else [target]
        for tid in targets:
            if tid not in shard_ids:
                dangling_targets.append((k, tid))
        if k.startswith("0a0") or ("xxxx" in k and any(d in k for d in ("c2", "f0", "93", "88", "80"))):
            hex_residue_keys.append((k, target))

    assert not dangling_targets, f"Found {len(dangling_targets)} dangling formula IDs in formulas_latex_index.json: {dangling_targets[:10]}"
    assert not hex_residue_keys, f"Found {len(hex_residue_keys)} stale hex-residue keys in formulas_latex_index.json: {hex_residue_keys[:10]}"
