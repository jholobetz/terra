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
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')

# Import Lineage Discovery & Resolution Engine
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'scripts', 'maintenance'))
try:
    from lineage_resolver import discover_lineage
except ImportError:
    discover_lineage = None

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

from lib.ai.models import get_flash_model

def get_gemini_client():
    if not HAS_GENAI_SDK:
        raise ValueError("google-genai SDK not installed.")

    # 1. Pure Free Tier Default (Google AI Studio - $0.00 via GEMINI_FREE_API_KEY / GEMINI_API_KEY)
    env_keys = {}
    dotenv_path = os.path.join(PROJECT_ROOT, '.env')
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        env_keys[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass

    api_key = (
        os.environ.get('GEMINI_FREE_API_KEY')
        or env_keys.get('GEMINI_FREE_API_KEY')
        or os.environ.get('GEMINI_API_KEY')
        or env_keys.get('GEMINI_API_KEY')
    )

    if not api_key and keyring:
        try:
            api_key = keyring.get_password("physics_lab", "gemini_api_key")
        except Exception:
            pass

    if api_key:
        client = genai.Client(api_key=api_key)
        model_name = get_flash_model()
        return client, model_name

    # 2. GCP Vertex AI is permanently disabled to guarantee $0.00 spend.
    raise ValueError("No valid GEMINI_FREE_API_KEY found. Vertex AI is permanently disabled to guarantee $0.00 cost.")

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

def synthesize_local_definition(latex_str):
    latex = latex_str.strip()
    title = "Custom Physical Relation"
    conceptual_def = f"This mathematical relation establishes a fundamental physical balance or dynamical identity governing ${latex}$."
    intuitive_sum = "It relates spatial variations or field configurations directly to corresponding physical sources or rates."
    interpretation = f"The expression ${latex}$ encapsulates an identity relating field observables or coordinates to physical source distributions or evolutionary dynamics."
    symmetry_origin = "Maintains translational and coordinate invariance consistent with the underlying field formulation."
    limits_and_boundary = "Valid across non-relativistic asymptotic regimes and smooth continuous boundary conditions."
    semantic_vars = {}

    # Heuristics based on equation structure
    if "\\nabla^2" in latex or "laplacian" in latex.lower():
        title = "Laplacian Potential Relation"
        conceptual_def = f"Defines a spatial second-order differential relation describing field curvature and source distributions: ${latex}$."
        intuitive_sum = "Relates the local concavity of a potential field directly to source densities or acceleration terms."
        interpretation = f"The Laplacian operator $\\nabla^2$ quantifies the difference between the field value at a point and its local spatial average, balanced by ${latex}$."
        symmetry_origin = "Invariant under 3D spatial rotations $SO(3)$ and spatial translations."
        limits_and_boundary = "Reduces to Laplace's equation $\\nabla^2 \\phi = 0$ in source-free asymptotic boundary domains."
    elif "\\nabla \\times" in latex or "curl" in latex.lower():
        title = "Vorticity Circulation Relation"
        conceptual_def = f"Establishes the rotational curl or circulation of a vector field: ${latex}$."
        intuitive_sum = "Measures the tendency of vector field lines to circulate around microscopic vortex lines."
        interpretation = f"The curl equation ${latex}$ determines whether the field possesses non-zero circulation along closed loops."
        symmetry_origin = "Preserves gauge covariance and rotational symmetry under spatial coordinate frames."
        limits_and_boundary = "Vorticity vanishes in irrotational or static scalar potential limits."
    elif "\\partial" in latex and "\\partial t" in latex:
        title = "Time-Dependent Evolution Relation"
        conceptual_def = f"Governs the temporal evolution and dynamic rate of change of the physical state: ${latex}$."
        intuitive_sum = "Predicts how the system state propagates from initial conditions forward in time."
        interpretation = f"The partial time derivative in ${latex}$ couples the rate of temporal variation directly to spatial gradients or driving forces."
        symmetry_origin = "Originates from continuous time-translation symmetry and energy balance."
        limits_and_boundary = "Reduces to stationary steady-state configurations when $\\partial / \\partial t \\to 0$."
    elif "f(z)" in latex or "g(z)" in latex or "/(z" in latex:
        title = "Meromorphic Complex Potential Relation"
        conceptual_def = f"Defines a complex-analytic or meromorphic physical relation in the complex plane: ${latex}$."
        intuitive_sum = "Describes physical field potentials using holomorphic function theory with isolated singularities."
        interpretation = f"The function ${latex}$ models 2D potential flows, conformal mappings, or Cauchy residue representations."
        symmetry_origin = "Invariant under conformal transformations $SO(2,1)$ and Cauchy-Riemann analyticity."
        limits_and_boundary = "Exhibits isolated pole singularity as $z \\to z_0$ with non-zero residue."
    elif "\\int" in latex:
        title = "Integral Conservation Law"
        conceptual_def = f"Expresses an accumulated global macroscopic quantity integrated over domain bounds: ${latex}$."
        intuitive_sum = "Summates microscopic densities across the spatial domain to determine total conserved charges."
        interpretation = f"The integral accumulation ${latex}$ balances boundary flux against interior domain sources."
        symmetry_origin = "Reflects global conservation laws via Noether's theorem."
        limits_and_boundary = "Converges under square-integrable boundary conditions at spatial infinity."

    return {
        "title": title,
        "conceptual_definition": conceptual_def,
        "intuitive_summary": intuitive_sum,
        "interpretation": interpretation,
        "symmetry_origin": symmetry_origin,
        "limits_and_boundary": limits_and_boundary,
        "parent_formula_id": "",
        "derivation_type": "",
        "semantic_variables": semantic_vars
    }

def invoke_antigravity_agent(latex_str):
    """
    Invokes the local headless Antigravity CLI agent ('agy -p') to analyze and draft
    the physics equation without requiring developer API keys or daily quota caps.
    """
    import shutil
    agy_bin = os.path.expanduser('~/.local/bin/agy')
    if not os.path.exists(agy_bin):
        agy_bin = shutil.which('agy')

    if not agy_bin or not os.path.exists(agy_bin):
        return None, "agy binary not found"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"LaTeX Equation to Analyze: {latex_str}\n\n"
        "IMPORTANT: Output valid JSON matching the exact schema only. "
        "Do not include any conversational preamble, explanation, or markdown backticks."
    )

    cmd = [
        agy_bin,
        '-p', prompt,
        '--output-format', 'text',
        '--disable-slash-commands',
        '--print-timeout', '60s'
    ]

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=75
        )
        if proc.returncode != 0 or not proc.stdout.strip():
            return None, f"agy exited with code {proc.returncode}: {proc.stderr.strip()[:150]}"

        raw_text = proc.stdout.strip()
        if '```json' in raw_text:
            raw_text = raw_text.split('```json', 1)[1]
            if '```' in raw_text:
                raw_text = raw_text.split('```', 1)[0]
        elif '```' in raw_text:
            raw_text = raw_text.split('```', 1)[1]
            if '```' in raw_text:
                raw_text = raw_text.split('```', 1)[0]
        raw_text = raw_text.strip()

        if not raw_text.startswith('{') and '{' in raw_text:
            raw_text = raw_text[raw_text.find('{'):raw_text.rfind('}') + 1]

        clean_json = sanitize_gemini_latex_json(raw_text)
        data = json.loads(clean_json)
        while isinstance(data, str):
            data = json.loads(data)

        if isinstance(data, dict) and data.get("conceptual_definition"):
            return data, "antigravity_agent"
    except Exception as e:
        return None, f"Agent invocation failed: {type(e).__name__}: {str(e)}"

    return None, "Invalid JSON returned by agent"

def generate_definition(latex_str):
    data = {}
    is_fallback = False
    fallback_reason = None
    source = "gemini_api"

    # 1. Primary Engine: Local Antigravity Agent (Zero API keys, zero 20-call daily cap)
    agent_data, agent_status = invoke_antigravity_agent(latex_str)
    if agent_data and isinstance(agent_data, dict) and agent_data.get("conceptual_definition"):
        data = agent_data
        source = "antigravity_agent"
    else:
        # 2. Fallback Engine: Google AI Studio API key cascade
        try:
            client, model_name = get_gemini_client()
            prompt = f"{SYSTEM_PROMPT}\n\nLaTeX Equation to Analyze: {latex_str}"

            # Resilient multi-model cascade across free-tier candidate models
            models_to_try = [model_name]
            try:
                from lib.ai.models import get_flash_candidates
                candidates = get_flash_candidates()
                if candidates:
                    models_to_try = candidates
            except Exception:
                pass

            response = None
            last_exception = None
            active_model = model_name
            import time

            for m_name in models_to_try:
                active_model = m_name
                for attempt in range(1, 3):
                    try:
                        response = client.models.generate_content(
                            model=m_name,
                            contents=prompt,
                            config=types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.2,
                                max_output_tokens=2500,
                            ),
                        )
                        if response and response.text:
                            source = f"gemini_api ({m_name})"
                            break
                    except Exception as attempt_err:
                        last_exception = attempt_err
                        err_msg = str(attempt_err)
                        # If daily quota limit is hit, do NOT sleep/retry this model; switch immediately to next candidate
                        if "GenerateRequestsPerDay" in err_msg or "limit: 20" in err_msg:
                            break
                        if ("503" in err_msg or "UNAVAILABLE" in err_msg) and attempt < 2:
                            time.sleep(1)
                            continue
                        break
                if response and response.text:
                    break

            if not response or not response.text:
                if last_exception:
                    raise last_exception
                raise ValueError("No response received from model")

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
        except Exception as e:
            # Fall back gracefully to high-quality local AST / heuristic synthesis
            is_fallback = True
            source = "heuristic_fallback"
            fallback_reason = f"{type(e).__name__}: {str(e)}"
            data = synthesize_local_definition(latex_str)


    if not isinstance(data, dict) or not data.get("conceptual_definition"):
        is_fallback = True
        source = "heuristic_fallback"
        if not fallback_reason:
            fallback_reason = "Empty or malformed JSON returned by model"
        local_fallback = synthesize_local_definition(latex_str)
        if isinstance(data, dict):
            for k, v in local_fallback.items():
                if not data.get(k):
                    data[k] = v
        else:
            data = local_fallback

    title = data.get('title', 'Custom Physical Relation')
    base_slug = slugify(title)
    if not base_slug:
        base_slug = f"custom-formula-{hash(latex_str) & 0xffffffff}"

    # Collision Guard: check if slug exists with a DIFFERENT equation
    slug_id = base_slug
    import hashlib
    hex_hash = hashlib.md5(slug_id.encode('utf-8')).hexdigest()[:2]
    check_shard = os.path.join(FORMULAS_DIR, hex_hash, f"shard_{hex_hash}.json")
    if os.path.exists(check_shard):
        try:
            with open(check_shard, 'r', encoding='utf-8') as f:
                existing_shard = json.load(f)
                if slug_id in existing_shard:
                    existing_eq = existing_shard[slug_id].get('equation', '').strip()
                    # If equations differ, create a disambiguated formulation variant
                    if existing_eq and existing_eq != latex_str.strip():
                        eq_hash = hashlib.md5(latex_str.strip().encode('utf-8')).hexdigest()[:8]
                        slug_id = f"{base_slug}-{eq_hash}"
        except Exception:
            pass

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
        "semantic_variables": data.get('semantic_variables', {}),
        "is_fallback": is_fallback,
        "source": source,
        "fallback_reason": fallback_reason
    }

    # Auto-resolve and verify derivation lineage
    lineage_info = {}
    if discover_lineage:
        try:
            lineage_info = discover_lineage(
                title=title,
                equation=latex_str,
                conceptual_definition=formula_obj.get("conceptual_definition", ""),
                interpretation=formula_obj.get("interpretation", ""),
                existing_parent=formula_obj.get("parent_formula_id", "")
            )
            if lineage_info:
                formula_obj["parent_formula_id"] = lineage_info.get("parent_formula_id", "")
                formula_obj["derivation_type"] = lineage_info.get("derivation_type", "DERIVED_FROM")
                formula_obj["subcomponents"] = lineage_info.get("subcomponents", [])
        except Exception:
            pass

    return formula_obj, lineage_info

def parent_exists(parent_id):
    if not parent_id:
        return True
    import hashlib
    hex_hash = hashlib.md5(parent_id.encode('utf-8')).hexdigest()[:2]
    parent_shard = os.path.join(FORMULAS_DIR, hex_hash, f"shard_{hex_hash}.json")
    if os.path.exists(parent_shard):
        try:
            with open(parent_shard, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return parent_id in data
        except Exception:
            pass
    return False

def validate_tex_prose(text):
    if not text:
        return True, ""
    dollars = text.count('$')
    if dollars % 2 != 0:
        return False, f"Unbalanced dollar sign math delimiters (found {dollars} '$' signs)"
    if '\\(' in text or '\\)' in text or '\\[' in text or '\\]' in text:
        return False, "Contains raw escaped LaTeX bracket macros (\\(, \\), \\[, \\])"
    return True, ""

def validate_formula_obj(formula_obj):
    # 1. Required fields check
    for req_field in ['id', 'title', 'conceptual_definition', 'interpretation']:
        if not formula_obj.get(req_field):
            raise ValueError(f"Formula payload missing required field: '{req_field}'")

    # 2. TeX prose validation across narrative fields
    prose_fields = ['conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary']
    for field in prose_fields:
        val = formula_obj.get(field, '')
        valid, err = validate_tex_prose(val)
        if not valid:
            raise ValueError(f"TeX validation failed in '{field}': {err}")

    # 3. Parent link integrity validation & automatic sanitization
    parent_id = formula_obj.get('parent_formula_id', '')
    if parent_id and not parent_exists(parent_id):
        # Sanitize unverified parent link to preserve integrity
        formula_obj['parent_formula_id'] = ''
        formula_obj['derivation_type'] = ''

    return True

from lib.pipeline.formula_pipeline import FormulaIngestionPipeline

def save_and_sync(formula_obj, subtopic_slug=None, dry_run=False):
    pipeline = FormulaIngestionPipeline(project_root=PROJECT_ROOT)
    return pipeline.ingest(formula_obj, subtopic_slug=subtopic_slug, dry_run=dry_run)

def main():
    parser = argparse.ArgumentParser(description="Generate Gemini Formula Definition")
    parser.add_argument('--latex', required=True, help="LaTeX equation string")
    parser.add_argument('--subtopic', required=False, default=None, help="Subtopic slug to link")
    parser.add_argument('--dry-run', action='store_true', help="Validate and prove without saving")
    args = parser.parse_args()

    try:
        formula_obj, lineage_info = generate_definition(args.latex)
        result = save_and_sync(formula_obj, subtopic_slug=args.subtopic, dry_run=args.dry_run)
        if lineage_info and "lineage" not in result:
            result["lineage"] = lineage_info
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

