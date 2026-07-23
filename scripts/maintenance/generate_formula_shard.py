#!/usr/bin/env python3
"""
🪐 Physics Lab: Automated Formula Shard Curation, Auditing, & Generation Tool
Handles batch-auditing and enrichment of all 5,000+ formulas, as well as
on-demand interactive creation of new sharded database records.
"""

import os
import sys
import re
import json
import argparse
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app/config/content/formulas")
CONSTANTS_PATH = os.path.join(PROJECT_ROOT, "app/config/content/constants.json")

def load_js_dictionaries():
    """Load variable dictionaries and fallback binders from public/js/equation_explainer.js via exporter helper."""
    exporter_path = os.path.join(SCRIPT_DIR, "export_js_dictionaries.js")
    try:
        output = subprocess.check_output(["node", exporter_path], stderr=subprocess.DEVNULL).decode("utf-8")
        return json.loads(output)
    except Exception as e:
        print(f"Error loading JS dictionaries: {e}", file=sys.stderr)
        return {"variableDictionary": {}, "physicsDictionary": {}, "fallbackBinders": []}

def load_constants():
    """Load physical constants from constants.json."""
    if os.path.exists(CONSTANTS_PATH):
        try:
            with open(CONSTANTS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading constants: {e}", file=sys.stderr)
    return {}

def extract_all_math_tokens(latex_str):
    """
    Python equivalent of the frontend extractAllMathTokens tokenizer.
    Extracts variables, constants, modifiers, and integration boundaries.
    """
    tokens = []
    seen = set()

    def add_token(sym, tok_type):
        sym = sym.strip()
        if not sym or sym in seen:
            return
        # Skip numeric constants
        if re.match(r'^[0-9]+$', sym):
            return
        seen.add(sym)
        tokens.append({"symbol": sym, "type": tok_type})

    # Normalize Greek variants
    text = latex_str.strip()
    text = re.sub(r'\\varepsilon(?![a-zA-Z])', r'\\epsilon', text)
    text = re.sub(r'\\vartheta(?![a-zA-Z])', r'\\theta', text)
    text = re.sub(r'\\varphi(?![a-zA-Z])', r'\\phi', text)
    text = re.sub(r'\\varrho(?![a-zA-Z])', r'\\rho', text)
    text = re.sub(r'\\varpi(?![a-zA-Z])', r'\\pi', text)
    text = re.sub(r'\\varsigma(?![a-zA-Z])', r'\\sigma', text)

    # Pre-scan physical constants with subscripts to prevent stripping
    const_sub_regex = r'\\(epsilon|mu|k|a|m|g|G|N)_(?:0|\{0\}|B|\{B\}|e|\{e\}|p|\{p\}|n|\{n\}|F|\{F\}|A|\{A\})(?![a-zA-Z])'
    for match in re.finditer(const_sub_regex, text):
        full_match = match.group(0)
        norm_sym = re.sub(r'_\{([^\}]+)\}', r'_\1', full_match)
        add_token(norm_sym, 'variable')
        text = text.replace(full_match, ' ')

    # Pre-scan integration boundaries: \int_V, \oint_C, etc.
    boundary_regex = r'\\(int|oint|iint|iiint)_\{?([a-zA-Z0-9]+)\}?'
    for match in re.finditer(boundary_regex, text):
        boundary_var = match.group(2)
        if boundary_var and re.match(r'^[a-zA-Z]$', boundary_var):
            add_token(boundary_var, 'integration_boundary')

    # Strip environments
    text = re.sub(r'\\begin\{[a-zA-Z]+\}', ' ', text)
    text = re.sub(r'\\end\{[a-zA-Z]+\}', ' ', text)

    # Parse subscripts
    def sub_replace(m):
        content = m.group(1)
        clean = re.sub(r'\\text\{([^\}]+)\}', r'\1', content)
        clean = re.sub(r'\\mathrm\{([^\}]+)\}', r'\1', clean)
        clean = re.sub(r'\\(mathrm|text|mathsf|mathbf|boldsymbol)', '', clean)
        if re.match(r'^[a-zA-Z]$', clean):
            add_token(clean, 'variable')
        elif re.match(r'^\\[a-zA-Z]+$', clean):
            add_token(clean, 'variable')
        return ' '

    text = re.sub(r'_\{([^\}]+)\}', sub_replace, text)

    # Parse remaining simple subscripts
    def simple_sub_replace(m):
        char = m.group(1)
        if re.match(r'[a-zA-Z]', char):
            return ' ' + char + ' '
        return ' '

    text = re.sub(r'_([a-zA-Z0-9])', simple_sub_replace, text)

    # Strip visual modifiers: \hat{H} -> H, \mathbf{p} -> p
    has_styles = True
    while has_styles:
        next_text = re.sub(r'\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}', r'\2', text)
        if next_text == text:
            has_styles = False
        else:
            text = next_text

    # Extract Greek letters and mathcal
    mathcal_regex = r'\\mathcal\{([a-zA-Z])\}'
    for match in re.finditer(mathcal_regex, text):
        full_match = match.group(0)
        add_token(full_match, 'variable')
        text = text.replace(full_match, ' ')

    # Extract words/commands
    word_regex = r'(\\[a-zA-Z]+|[a-zA-Z])'
    for match in re.finditer(word_regex, text):
        sym = match.group(1)
        # Skip operator symbols
        if sym in ['\\frac', '\\sqrt', '\\sum', '\\prod', '\\int', '\\oint', '\\iint', '\\iiint', '\\partial', '\\iff', '\\to', '\\nabla', '\\cdot']:
            continue
        add_token(sym, 'variable')

    return tokens

def resolve_symbol_info(symbol, tok_type, domain, js_dicts, constants):
    """Resolve symbol name, type, description, and unit."""
    clean_symbol = symbol.strip().replace('\\', '').replace('{', '').replace('}', '')

    # 1. Check integration boundaries
    if tok_type == 'integration_boundary':
        if symbol == 'C':
            return {"name": "Integration Curve / Path Contour", "type": "operator", "unit": "dimensionless", "description": "The closed or open boundary path over which the line integral is evaluated."}
        elif symbol == 'S':
            return {"name": "Integration Surface", "type": "operator", "unit": "dimensionless", "description": "The two-dimensional surface over which the surface integral is evaluated."}
        elif symbol == 'V':
            return {"name": "Integration Volume", "type": "operator", "unit": "dimensionless", "description": "The three-dimensional volume region over which the volume integral is evaluated."}

    # 2. Check constants
    for key, details in constants.items():
        if details.get("symbol") == symbol or details.get("symbol") == clean_symbol:
            return {
                "name": details.get("name"),
                "type": "constant",
                "unit": details.get("unit"),
                "description": details.get("description", "Fundamental physical constant.")
            }

    # 3. Check variable dictionary
    var_dict = js_dicts.get("variableDictionary", {})
    dict_entry = var_dict.get(clean_symbol) or var_dict.get(symbol)
    if dict_entry:
        active_ctx = None
        if domain and "contexts" in dict_entry and domain in dict_entry["contexts"]:
            active_ctx = dict_entry["contexts"][domain]
        elif "contexts" in dict_entry and dict_entry["contexts"]:
            first_key = list(dict_entry["contexts"].keys())[0]
            active_ctx = dict_entry["contexts"][first_key]

        return {
            "name": active_ctx["name"] if active_ctx else dict_entry["name"],
            "type": "variable",
            "unit": active_ctx.get("unit", dict_entry.get("defaultUnit")) if active_ctx else dict_entry.get("defaultUnit"),
            "description": active_ctx["description"] if active_ctx else dict_entry.get("description")
        }

    # 4. Check physics dictionary fallback
    phys_dict = js_dicts.get("physicsDictionary", {})
    legacy_entry = phys_dict.get(clean_symbol) or phys_dict.get(symbol)
    if legacy_entry:
        active_legacy = legacy_entry
        match = None
        if "alternatives" in legacy_entry and legacy_entry["alternatives"]:
            for alt in legacy_entry["alternatives"]:
                if alt.get("domain") == domain:
                    match = alt
                    break
        if match:
            active_legacy = {
                "name": match["name"],
                "type": match.get("type", legacy_entry.get("type", "variable")),
                "unit": match.get("unit", legacy_entry.get("unit", "dimensionless")),
                "desc": match.get("desc", legacy_entry.get("desc"))
            }
        return {
            "name": active_legacy["name"],
            "type": active_legacy.get("type", "variable"),
            "unit": active_legacy.get("unit", "dimensionless"),
            "description": active_legacy.get("desc", "Physics parameter.")
        }

    # 5. General fallback
    return {
        "name": f"{symbol} Parameter",
        "type": "variable",
        "unit": "dimensionless",
        "description": "Physics variable or parameter."
    }

def audit_shards(js_dicts, constants, domain_override=None):
    """Audit all sharded JSON files, enriching missing semantic variables."""
    print("🔍 Auditing 256 database shards for missing variable definitions...")
    
    total_formulas = 0
    total_enriched_vars = 0
    shards_updated = 0

    if not os.path.exists(FORMULAS_DIR):
        print(f"Error: Formulas directory not found at {FORMULAS_DIR}")
        return

    for filename in sorted(os.listdir(FORMULAS_DIR)):
        if not filename.startswith("shard_") or not filename.endswith(".json"):
            continue

        shard_path = os.path.join(FORMULAS_DIR, filename)
        with open(shard_path, "r", encoding="utf-8") as f:
            shard_data = json.load(f)

        shard_modified = False
        for formula_id, details in shard_data.items():
            total_formulas += 1
            equation_svg = details.get("equation", "")
            
            # Extract raw latex from SVG data-tex attribute
            match = re.search(r'data-tex="([^"]+)"', equation_svg)
            if not match:
                continue
            
            latex_formula = match.group(1)
            # Unescape HTML entities in LaTeX
            latex_formula = latex_formula.replace("&gt;", ">").replace("&lt;", "<").replace("&amp;", "&")

            # Get domain (can be mapped from reference categories or custom domain)
            # Default to electromagnetism if not easily inferred
            domain = domain_override or "electromagnetism"
            
            # Find all math tokens
            tokens = extract_all_math_tokens(latex_formula)
            
            # Enrich semantic_variables
            if "semantic_variables" not in details:
                details["semantic_variables"] = {}

            sem_vars = details["semantic_variables"]
            
            # Strip delimiters from keys in existing semantic_variables
            clean_sem_vars = {}
            for k, v in sem_vars.items():
                ck = k.replace("\\(", "").replace("\\)", "").strip()
                clean_sem_vars[ck] = v

            for tok in tokens:
                symbol = tok["symbol"]
                # Check variations (raw symbol, or wrapped in delimiters)
                has_key = False
                for variant in [symbol, f"\\({symbol}\\)", f"\\({symbol} \\)"]:
                    if variant in sem_vars or symbol in clean_sem_vars:
                        has_key = True
                        break

                if not has_key:
                    # Missing definition! Resolve it contextually
                    resolved = resolve_symbol_info(symbol, tok["type"], domain, js_dicts, constants)
                    
                    # Store as escaped key
                    escaped_key = f"\\({symbol}\\)"
                    sem_vars[escaped_key] = {
                        "name": resolved["name"],
                        "type": resolved["type"],
                        "unit": resolved["unit"],
                        "description": resolved["description"]
                    }
                    total_enriched_vars += 1
                    shard_modified = True
                    print(f"  + [{formula_id}] Enriched {symbol} -> '{resolved['name']}' ({resolved['unit']})")

        if shard_modified:
            shards_updated += 1
            with open(shard_path, "w", encoding="utf-8") as f:
                json.dump(shard_data, f, indent=4)

    print("\n=======================================================")
    print(f"✅ Audit Completed.")
    print(f"Total Formulas Inspected: {total_formulas}")
    print(f"Total New Variables Enriched: {total_enriched_vars}")
    print(f"Total Shard Files Updated: {shards_updated}")
    print("=======================================================")

    if shards_updated > 0:
        print("Reindexing database cache...")
        subprocess.run(["php", "cli_sync.php"], cwd=PROJECT_ROOT)

def generate_interactive_shard(latex, name, domain, js_dicts, constants):
    """Generate a clean draft JSON shard for a new equation on-demand."""
    tokens = extract_all_math_tokens(latex)
    semantic_vars = {}
    
    for tok in tokens:
        symbol = tok["symbol"]
        resolved = resolve_symbol_info(symbol, tok["type"], domain, js_dicts, constants)
        escaped_key = f"\\({symbol}\\)"
        semantic_vars[escaped_key] = {
            "name": resolved["name"],
            "type": resolved["type"],
            "unit": resolved["unit"],
            "description": resolved["description"]
        }

    # Draft payload
    draft = {
        "title": name,
        "equation": f"<svg data-tex=\"{latex}\">...[MathJax-to-SVG Placeholder]...</svg>",
        "semantic_variables": semantic_vars,
        "interpretation": "A description of the physical meaning, behavior, and role of the equation...",
        "symmetry_origin": "The conservation laws, symmetries (gauge, spatial), or coordinate transformations...",
        "limits_and_boundary": "How the equation behaves at extreme limits (T -> 0, E -> infinity, boundary regions)...",
        "status": "draft"
    }

    # Create drafts directory if it doesn't exist
    drafts_dir = os.path.join(FORMULAS_DIR, "drafts")
    os.makedirs(drafts_dir, exist_ok=True)

    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    draft_path = os.path.join(drafts_dir, f"{slug}.json")

    with open(draft_path, "w", encoding="utf-8") as f:
        json.dump(draft, f, indent=4)

    print("\n=======================================================")
    print(f"🎉 Draft Shard JSON Created!")
    print(f"Title: {name}")
    print(f"LaTeX: {latex}")
    print(f"File Saved: {draft_path}")
    print("=======================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🪐 Formula Shard Curation, Auditing, & Generation Tool")
    parser.add_argument("--audit", action="store_true", help="Audit all 256 shards to auto-fill missing definitions")
    parser.add_argument("--latex", type=str, help="LaTeX equation string to shard on-demand")
    parser.add_argument("--name", type=str, help="Commonly used name representing the equation")
    parser.add_argument("--domain", type=str, default="electromagnetism", help="Physics domain (e.g. electromagnetism, thermodynamics)")
    args = parser.parse_args()

    js_dicts = load_js_dictionaries()
    constants = load_constants()

    if args.audit:
        audit_shards(js_dicts, constants, args.domain)
    elif args.latex and args.name:
        generate_interactive_shard(args.latex, args.name, args.domain, js_dicts, constants)
    else:
        parser.print_help()
