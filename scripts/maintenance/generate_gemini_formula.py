#!/usr/bin/env python3
"""
⚡ Gemini Formula Generator
Takes a raw LaTeX string, calls Gemini AI (via Vertex AI or Google AI Studio) to synthesize a complete
Platinum Formula Definition, saves it to the active shard JSON file, and synchronizes MariaDB + search indexes.

Usage:
    python3 scripts/maintenance/generate_gemini_formula.py --latex "G(\\mathbf{r}, \\mathbf{r}')"
"""

import os
import sys
import json
import re
import argparse
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
GCP_CREDS_PATH = os.path.join(PROJECT_ROOT, 'gcp-credentials.json')

# Import google.genai SDK
try:
    from google import genai
    from google.genai import types
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False

try:
    import keyring
except ImportError:
    keyring = None

def get_gemini_client():
    # 1. Check if GCP Service Account Credentials file exists (Vertex AI mode)
    if os.path.exists(GCP_CREDS_PATH):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDS_PATH
        try:
            with open(GCP_CREDS_PATH, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
                project_id = creds_data.get('project_id', 'gen-lang-client-0170965498')
        except Exception:
            project_id = 'gen-lang-client-0170965498'

        client = genai.Client(vertexai=True, project=project_id, location='us-central1')
        return client, 'gemini-2.5-flash'

    # 2. Check for standard GEMINI_API_KEY environment variable or .env
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        dotenv_path = os.path.join(PROJECT_ROOT, '.env')
        if os.path.exists(dotenv_path):
            with open(dotenv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('GEMINI_API_KEY='):
                        api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break

    if not api_key and keyring:
        try:
            key = keyring.get_password("physics_lab", "gemini_api_key")
            if key and key.startswith('AIzaSy'):
                api_key = key
        except Exception:
            pass

    if api_key and api_key.startswith('AIzaSy'):
        client = genai.Client(api_key=api_key)
        return client, 'gemini-2.0-flash'

    raise ValueError("No valid Gemini authentication found (missing gcp-credentials.json or AIzaSy GEMINI_API_KEY).")

def get_target_shard_file():
    existing_shards = sorted([
        f for f in os.listdir(FORMULAS_DIR)
        if f.startswith('shard_') and f.endswith('.json')
    ], key=lambda x: (len(x), x))

    if not existing_shards:
        return os.path.join(FORMULAS_DIR, 'shard_52.json')

    last_shard = os.path.join(FORMULAS_DIR, existing_shards[-1])
    try:
        with open(last_shard, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if len(data) < 50:
                return last_shard
    except Exception:
        pass

    return os.path.join(FORMULAS_DIR, 'shard_52.json')

def slugify(title):
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s\-]', '', slug)
    slug = re.sub(r'[\s\_]+', '-', slug)
    return slug.strip('-')

SYSTEM_PROMPT = """
You are an expert theoretical physics knowledge architect for Project Terra (Physics & Mathematical Sciences Engine).
Analyze the provided LaTeX equation and generate a complete, academically rigorous formula definition matching the EXACT JSON schema below.

REQUIREMENTS:
1. "title": Formal academic name of the formula or theorem (e.g. "Position-Space Green's Function").
2. "conceptual_definition": 1-2 sentence formal academic definition.
3. "intuitive_summary": 1-2 sentence physical intuition summary.
4. "interpretation": Detailed physical interpretation paragraph.
5. "symmetry_origin": Symmetry derivations, Noether conservation laws, or coordinate invariance.
6. "limits_and_boundary": Limiting cases, asymptotic regimes, or boundary conditions.
7. "parent_formula_id": Slug ID of master parent law if derived (e.g. "poisson-equation-electrostatics", "schrodinger-equation", "maxwell-equations", "einstein-field-equations", or empty string "").
8. "derivation_type": One of ["DERIVED_FROM", "LIMIT_CASE", "EQUIVALENT_FORM", "SPECIAL_CASE", ""].
9. "semantic_variables": Object mapping variable symbols to {"name": "...", "unit": "SI Unit", "description": "..."}.
10. All LaTeX in text fields MUST use valid LaTeX math delimiters like $...$ for inline math expressions.

Output ONLY valid raw JSON matching this structure:
{
  "title": "...",
  "conceptual_definition": "...",
  "intuitive_summary": "...",
  "interpretation": "...",
  "symmetry_origin": "...",
  "limits_and_boundary": "...",
  "parent_formula_id": "...",
  "derivation_type": "...",
  "semantic_variables": {
    "symbol": { "name": "...", "unit": "...", "description": "..." }
  }
}
"""

def sanitize_gemini_latex_json(raw_text):
    result = []
    in_string = False
    i = 0
    length = len(raw_text)
    while i < length:
        char = raw_text[i]
        if char == '"' and (i == 0 or raw_text[i - 1] != '\\'):
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        if in_string and char == '\\':
            if i + 1 < length:
                next_char = raw_text[i + 1]
                if next_char in ('"', '\\', '/'):
                    result.append('\\' + next_char)
                    i += 2
                    continue
                elif next_char == 'u' and i + 5 < length and all(c in '0123456789abcdefABCDEF' for c in raw_text[i+2:i+6]):
                    result.append(raw_text[i:i+6])
                    i += 6
                    continue
                result.append('\\\\')
                i += 1
                continue
            else:
                result.append('\\\\')
                i += 1
                continue
        result.append(char)
        i += 1
    return "".join(result)

def generate_definition(latex_str):
    client, model_name = get_gemini_client()
    prompt = f"{SYSTEM_PROMPT}\n\nLaTeX Equation to Analyze: {latex_str}"

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )

    raw_text = response.text.strip()
    if raw_text.startswith('```json'):
        raw_text = raw_text[7:]
    if raw_text.endswith('```'):
        raw_text = raw_text[:-3]
    raw_text = raw_text.strip()

    clean_json = sanitize_gemini_latex_json(raw_text)

    try:
        data = json.loads(clean_json)
    except Exception:
        try:
            data = json.loads(raw_text)
        except Exception:
            data = {}

    while isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception:
            data = {}
            break

    if not isinstance(data, dict):
        data = {}

    title = data.get('title', 'Custom Physical Relation')
    slug_id = slugify(title)
    if not slug_id:
        slug_id = f"custom-formula-{hash(latex_str) & 0xffffffff}"

    formula_obj = {
        "id": slug_id,
        "title": title,
        "equation": latex_str,
        "conceptual_definition": data.get('conceptual_definition', ''),
        "intuitive_summary": data.get('intuitive_summary', ''),
        "interpretation": data.get('interpretation', ''),
        "symmetry_origin": data.get('symmetry_origin', ''),
        "limits_and_boundary": data.get('limits_and_boundary', ''),
        "unit_system": "SI",
        "parent_formula_id": data.get('parent_formula_id', ''),
        "derivation_type": data.get('derivation_type', ''),
        "status": "published",
        "semantic_variables": data.get('semantic_variables', {})
    }

    return formula_obj

def save_and_sync(formula_obj):
    formula_id = formula_obj['id']
    import hashlib
    hex_hash = hashlib.md5(formula_id.encode('utf-8')).hexdigest()[:2]
    target_shard = os.path.join(FORMULAS_DIR, f"shard_{hex_hash}.json")

    shard_data = {}
    if os.path.exists(target_shard):
        try:
            with open(target_shard, 'r', encoding='utf-8') as f:
                shard_data = json.load(f)
        except Exception:
            shard_data = {}

    if not isinstance(shard_data, dict):
        shard_data = {}

    shard_data[formula_id] = formula_obj

    with open(target_shard, 'w', encoding='utf-8') as f:
        json.dump(shard_data, f, indent=4, ensure_ascii=False)

    # Sync to MariaDB & rebuild search index
    cli_sync_path = os.path.join(PROJECT_ROOT, 'cli_sync.php')
    sync_cmd = ['php', cli_sync_path]
    subprocess.run(sync_cmd, capture_output=True, text=True)

    return target_shard

def main():
    parser = argparse.ArgumentParser(description="Generate Gemini Formula Definition")
    parser.add_argument('--latex', required=True, help="LaTeX equation string")
    args = parser.parse_args()

    try:
        formula_obj = generate_definition(args.latex)
        target_shard = save_and_sync(formula_obj)
        result = {
            "success": True,
            "shard_file": os.path.basename(target_shard),
            "formula": formula_obj
        }
        print(json.dumps(result, ensure_ascii=False))
    except Exception as e:
        error_res = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_res, ensure_ascii=False))
        sys.exit(1)

if __name__ == '__main__':
    main()
