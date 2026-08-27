#!/usr/bin/env python3
"""
⚡ Terra Physics Lab - Vertex AI Lineage & Derivation Enrichment Engine
Systematically audits, sanitizes, and connects formulas using Vertex AI (Gemini 2.5 Flash / Pro).
Generates rich prose, clean TeX delimiters, semantic variables, parent master equation,
derivation relationship, and downstream subcomponents.

Usage:
    # Dry run on 2 isolated formulas
    python3 scripts/maintenance/run_vertex_lineage_enricher.py --filter isolated --limit 2 --dry-run

    # Enrich a specific formula by ID
    python3 scripts/maintenance/run_vertex_lineage_enricher.py --target-id "principle-of-least-action"

    # Batch enrich top 20 thin formulas with 4 threads
    python3 scripts/maintenance/run_vertex_lineage_enricher.py --filter thin --limit 20 --concurrency 4 --rebuild-graph
"""

import os
import sys
import json
import glob
import re
import time
import argparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
GCP_CREDS_PATH = os.path.join(PROJECT_ROOT, 'gcp-credentials.json')
CHECKPOINT_FILE = os.path.join(PROJECT_ROOT, 'app', 'config', 'vertex_enricher_checkpoint.json')

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

shard_file_locks = {}
global_state_lock = threading.Lock()

# -------------------------------------------------------------------------
# Vertex AI / Gemini Client Initialization (3-Profile Architecture)
# -------------------------------------------------------------------------
def _load_env_keys():
    keys = {}
    dotenv_path = os.path.join(PROJECT_ROOT, '.env')
    if os.path.exists(dotenv_path):
        with open(dotenv_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    keys[k.strip()] = v.strip().strip('"').strip("'")
    return keys

def get_gemini_client(model_choice='gemini-3.7-flash', provider='free'):
    if not HAS_GENAI_SDK:
        raise RuntimeError("google-genai SDK not installed. Run: pip install google-genai")

    env_keys = _load_env_keys()
    free_key = os.environ.get('GEMINI_FREE_API_KEY') or env_keys.get('GEMINI_FREE_API_KEY') or os.environ.get('GEMINI_API_KEY') or env_keys.get('GEMINI_API_KEY')
    prepaid_key = os.environ.get('GEMINI_PREPAID_API_KEY') or env_keys.get('GEMINI_PREPAID_API_KEY')

    # Profile 1: Pure Free Tier (Google AI Studio - $0.00 unbilled)
    if provider in ['free', 'aistudio', 'auto']:
        if not free_key:
            raise RuntimeError("Pure Free Tier requested, but GEMINI_FREE_API_KEY not found in .env.")
        client = genai.Client(api_key=free_key)
        return client, model_choice, "Google AI Studio (Pure Free Tier - $0.00)"

    # Profile 2: Prepaid Account Key
    if provider == 'prepaid':
        if not prepaid_key:
            raise RuntimeError("Prepaid Account requested, but GEMINI_PREPAID_API_KEY not found in .env.")
        client = genai.Client(api_key=prepaid_key)
        return client, model_choice, "Google AI Studio (Prepaid Account)"

    # Profile 3: GCP Service Account Credentials (Vertex AI mode)
    if provider == 'vertex':
        if not os.path.exists(GCP_CREDS_PATH):
            raise RuntimeError(f"Vertex AI requested, but {GCP_CREDS_PATH} not found.")
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDS_PATH
        try:
            with open(GCP_CREDS_PATH, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
                project_id = creds_data.get('project_id', 'gen-lang-client-0170965498')
        except Exception:
            project_id = 'gen-lang-client-0170965498'

        client = genai.Client(vertexai=True, project=project_id, location='us-central1')
        return client, model_choice, f"Vertex AI (GCP Project: {project_id})"

    raise RuntimeError(f"Unknown provider: {provider}. Choices are: free, prepaid, vertex.")

# -------------------------------------------------------------------------
# Fast In-Memory Shard Database & Candidate Grounding Index
# -------------------------------------------------------------------------
def load_all_shards():
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, '*', 'shard_*.json')))
    formulas = {}
    file_map = {}
    parent_map = {}
    child_map = {}

    for sf in shard_files:
        with open(sf, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[WARN] Error reading {sf}: {e}")
                continue
            for fid, form in data.items():
                if isinstance(form, dict):
                    formulas[fid] = form
                    file_map[fid] = sf

    for fid, form in formulas.items():
        p = form.get('parent_formula_id')
        if p and p in formulas and p != fid:
            parent_map[fid] = p
            child_map.setdefault(p, []).append(fid)

        subc = form.get('subcomponents', [])
        if isinstance(subc, list):
            for c in subc:
                cid = c if isinstance(c, str) else (c.get('id') if isinstance(c, dict) else None)
                if cid and cid in formulas and cid != fid:
                    child_map.setdefault(fid, []).append(cid)

    return formulas, file_map, parent_map, child_map

def tokenize_string(s):
    if not s: return set()
    s_clean = re.sub(r'[^a-zA-Z0-9_\\]+', ' ', s.lower())
    return set(w for w in s_clean.split() if len(w) > 2)

def find_candidate_pool(target_fid, target_form, formulas, top_k=30):
    """Finds top-K related formulas across the encyclopedia for prompt grounding."""
    t_title = target_form.get('title', '')
    t_eq = target_form.get('equation', '')
    t_tokens = tokenize_string(t_title) | tokenize_string(t_eq) | tokenize_string(target_fid)

    candidates = []
    for fid, form in formulas.items():
        if fid == target_fid:
            continue
        f_title = form.get('title', '')
        f_eq = form.get('equation', '')
        f_tokens = tokenize_string(f_title) | tokenize_string(f_eq) | tokenize_string(fid)

        intersection = len(t_tokens & f_tokens)
        if intersection > 0:
            score = intersection * 3
            if any(sym in f_eq for sym in ['\\nabla', '\\partial', '\\hbar', '\\epsilon', '\\mu', '\\int', '\\mathcal']):
                score += 1
            candidates.append((score, fid, f_title, f_eq))

    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[:top_k]

# -------------------------------------------------------------------------
# Lineage Health Index (LHI) Scoring
# -------------------------------------------------------------------------
def is_trivial_variable(eq):
    if not eq: return True
    clean = re.sub(r'\s+', '', eq)
    if re.match(r'^[a-zA-Z](\\?[a-zA-Z0-9_^{}]+)?\s*=\s*[0-9]+(\.[0-9]+)?$', clean):
        return True
    if len(clean) <= 4 and '=' in clean:
        return True
    return False

def calculate_lhi(fid, form, formulas, parent_map, child_map):
    upstream_score = 0
    is_axiom = form.get('derivation_type') == 'AXIOMATIC_FOUNDATION'
    has_parent = (fid in parent_map) or (bool(form.get('parent_formula_id')) and form.get('parent_formula_id') in formulas)

    if is_axiom or has_parent:
        upstream_score = 35

    children = list(child_map.get(fid, []))
    subc = form.get('subcomponents', [])
    if isinstance(subc, list):
        for c in subc:
            cid = c if isinstance(c, str) else (c.get('id') if isinstance(c, dict) else None)
            if cid and cid in formulas and cid not in children:
                children.append(cid)

    non_trivial_children = []
    trivial_children = []
    for cid in children:
        c_eq = formulas.get(cid, {}).get('equation', '')
        if is_trivial_variable(c_eq):
            trivial_children.append(cid)
        else:
            non_trivial_children.append(cid)

    n_valid = len(non_trivial_children)
    if n_valid >= 3:
        downstream_score = 35
    elif n_valid == 2:
        downstream_score = 25
    elif n_valid == 1:
        downstream_score = 15
    elif len(trivial_children) > 0:
        downstream_score = 5
    else:
        downstream_score = 0

    has_grandparent = False
    p_id = form.get('parent_formula_id') or parent_map.get(fid)
    if p_id and p_id in formulas:
        if p_id in parent_map or formulas.get(p_id, {}).get('derivation_type') == 'AXIOMATIC_FOUNDATION':
            has_grandparent = True

    has_grandchild = False
    for cid in non_trivial_children:
        if len(child_map.get(cid, [])) > 0:
            has_grandchild = True
            break

    depth_score = 0
    if (has_parent or is_axiom) and n_valid > 0:
        depth_score = 10
        if has_grandparent or has_grandchild:
            depth_score = 15
    elif has_parent or n_valid > 0:
        depth_score = 5

    quality_score = 15
    if len(children) > 0 and len(non_trivial_children) == 0:
        quality_score = 5
    elif len(children) == 0 and not has_parent and not is_axiom:
        quality_score = 0

    return max(0, min(100, upstream_score + downstream_score + depth_score + quality_score))

# -------------------------------------------------------------------------
# Vertex AI Prompt & Enrichment Generation
# -------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a Principal Theoretical Physicist and Core Maintainer of the Terra Physics Lab Encyclopedia.
Your task is to enrich and repair physics formula definitions with academic rigor, proper TeX math delimiters ($ ... $),
and complete lineage mapping (parent law, derivation relationship, and subcomponents).

CRITICAL DIRECTIVES:
1. Prose Delimiters: EVERY variable or equation in prose fields (interpretation, conceptual_definition, limits_and_boundary) MUST have matching closed LaTeX delimiters (e.g. $V(x)$, $\\mathbf{E}$, $\\hbar$). Never leave unclosed delimiters like '$E is...' or dangling '$'.
2. Parent & Subcomponents: You MUST select the 'parent_formula_id' and 'subcomponents' exclusively from the provided Candidate Grounding Pool, or set parent_formula_id to null if the equation is a truly fundamental first principle (derivation_type: "AXIOMATIC_FOUNDATION").
3. Semantic Variables: Map every unique physical symbol/operator to standard LaTeX keys with proper physical unit (SI or natural) and concise description.
4. Output Format: Return STRICT JSON matching the required schema. Do NOT wrap output in markdown code blocks.
"""

def robust_json_decode(text):
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text, strict=False)
    except Exception:
        pass

    try:
        # 1. Fix \u followed by non-4-hex chars (e.g. \unit, \uparrow)
        fixed = re.sub(r'\\u(?![0-9a-fA-F]{4})', r'\\\\u', text)
        # 2. Fix unescaped backslashes that are not valid JSON escape sequences
        fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', fixed)
        return json.loads(fixed, strict=False)
    except Exception:
        pass

    # 3. Aggressive character-level TeX backslash parser
    try:
        # Replace unescaped backslashes inside JSON strings
        out = []
        in_string = False
        escaped = False
        i = 0
        while i < len(text):
            char = text[i]
            if char == '"' and not escaped:
                in_string = not in_string
                out.append(char)
            elif in_string:
                if char == '\\':
                    next_char = text[i+1] if i + 1 < len(text) else ''
                    if next_char in ['"', '\\', '/']:
                        out.append(char)
                    elif next_char in ['b', 'f', 'n', 'r', 't']:
                        # Preserve standard whitespace escapes, escape all others
                        out.append(char)
                    elif next_char == 'u' and i + 5 < len(text) and all(c in '0123456789abcdefABCDEF' for c in text[i+2:i+6]):
                        out.append(char)
                    else:
                        out.append('\\\\')
                else:
                    out.append(char)
            else:
                out.append(char)
            escaped = (char == '\\' and not escaped)
            i += 1
        return json.loads("".join(out), strict=False)
    except Exception:
        pass

    # 4. Fallback using dirty-json / regex substitution
    try:
        sanitized = text.replace('\\\\', '\uFFFF')
        sanitized = re.sub(r'\\([a-zA-Z])', r'\\\\\1', sanitized)
        sanitized = sanitized.replace('\uFFFF', '\\\\')
        return json.loads(sanitized, strict=False)
    except Exception as e:
        raise ValueError(f"Unable to parse JSON: {e}\nRaw output:\n{text[:200]}...")

import socket
socket.setdefaulttimeout(45.0)

# -------------------------------------------------------------------------
# Financial & Token Rate Matrix (per 1,000,000 tokens)
# -------------------------------------------------------------------------
MODEL_RATES = {
    'gemini-3.5-flash-lite': {'input': 0.075 / 1e6, 'output': 0.30 / 1e6},
    'gemini-3.7-flash': {'input': 0.075 / 1e6, 'output': 0.30 / 1e6},
    'gemini-3.6-flash': {'input': 0.075 / 1e6, 'output': 0.30 / 1e6},
    'gemini-2.5-flash': {'input': 0.075 / 1e6, 'output': 0.30 / 1e6},
    'gemini-2.5-pro': {'input': 1.25 / 1e6, 'output': 5.00 / 1e6},
    'gemini-3.1-pro-preview': {'input': 1.25 / 1e6, 'output': 5.00 / 1e6},
}

quota_exhausted_event = threading.Event()
budget_circuit_breaker_event = threading.Event()
consecutive_429_count = 0
consecutive_429_lock = threading.Lock()

cost_accounting_lock = threading.Lock()
cumulative_session_spend_usd = 0.0
cumulative_prompt_tokens = 0
cumulative_candidates_tokens = 0
global_max_cost_dollars = 0.0
is_paid_session = False

def generate_enrichment(client, model_name, fid, form, candidates):
    global consecutive_429_count, cumulative_session_spend_usd, cumulative_prompt_tokens, cumulative_candidates_tokens
    if quota_exhausted_event.is_set() or budget_circuit_breaker_event.is_set():
        return None, 0, 0, 0.0

    cand_str = "\n".join([f"- ID: {c[1]} | Title: {c[2]} | Equation: {c[3]}" for c in candidates])

    prompt = f"""Target Formula to Enrich:
- Formula ID: {fid}
- Title: {form.get('title', 'Unknown')}
- LaTeX Equation: {form.get('equation', '')}
- Existing Description: {form.get('description', '')}
- Existing Interpretation: {form.get('interpretation', '')}

Candidate Grounding Pool (TOP {len(candidates)} mathematically related formulas in encyclopedia):
{cand_str}

Respond with STRICT JSON format:
{{
  "title": "string (refined academic title)",
  "description": "string (1-2 sentence core physics summary)",
  "conceptual_definition": "string (clear definition with clean $...$ delimiters)",
  "intuitive_summary": "string (intuitive conceptual insight)",
  "interpretation": "string (rigorous breakdown of every variable with closed $...$ delimiters)",
  "symmetry_origin": "string (Noether conservation law, gauge symmetry, or geometric invariance origin)",
  "limits_and_boundary": "string (asymptotic behavior at limits: T->0, v->c, hbar->0, r->inf)",
  "parent_formula_id": "string (MUST be one of the candidate IDs or null)",
  "derivation_type": "DERIVED_FROM | SPECIAL_CASE | APPROXIMATION | LIMITING_CASE | DEFINITION | GENERALIZATION | AXIOMATIC_FOUNDATION",
  "subcomponents": ["array of 2 to 4 candidate IDs"],
  "semantic_variables": {{
    "\\\\symbol_key": {{
      "name": "string",
      "type": "variable | constant | operator",
      "unit": "string",
      "description": "string"
    }}
  }}
}}
"""
    max_retries = 4
    backoff = 3
    for attempt in range(max_retries):
        if quota_exhausted_event.is_set() or budget_circuit_breaker_event.is_set():
            return None, 0, 0, 0.0
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[SYSTEM_PROMPT, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            with consecutive_429_lock:
                consecutive_429_count = 0

            # Extract token metadata from official response (including Thinking / Reasoning tokens)
            p_tok = 0
            c_tok = 0
            t_tok = 0
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                p_tok = getattr(response.usage_metadata, 'prompt_token_count', 0) or 0
                c_tok = getattr(response.usage_metadata, 'candidates_token_count', 0) or 0
                t_tok = getattr(response.usage_metadata, 'thoughts_token_count', 0) or 0

            # Google bills both candidates (visible output) and thoughts (reasoning) at the output token rate
            total_billable_output_tokens = c_tok + t_tok
            rates = MODEL_RATES.get(model_name, {'input': 0.075 / 1e6, 'output': 0.30 / 1e6})
            formula_cost = (p_tok * rates['input']) + (total_billable_output_tokens * rates['output']) if is_paid_session else 0.0

            with cost_accounting_lock:
                cumulative_session_spend_usd += formula_cost
                cumulative_prompt_tokens += p_tok
                cumulative_candidates_tokens += total_billable_output_tokens
                if global_max_cost_dollars > 0 and cumulative_session_spend_usd >= global_max_cost_dollars:
                    budget_circuit_breaker_event.set()
                    print(f"\n🛑 [CIRCUIT BREAKER] Hard Price Limit Reached: ${cumulative_session_spend_usd:.4f} >= ${global_max_cost_dollars:.2f}! Halting immediately.", flush=True)

            parsed = robust_json_decode(response.text)
            return parsed, p_tok, total_billable_output_tokens, formula_cost
        except Exception as e:
            err_msg = str(e)
            is_quota_err = ("429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg or "Quota exceeded" in err_msg)
            if is_quota_err:
                with consecutive_429_lock:
                    consecutive_429_count += 1
                    if consecutive_429_count >= 3:
                        quota_exhausted_event.set()
                        print("\n🛑 [QUOTA GUARD] Daily Free Tier Quota Limit Reached (HTTP 429 RESOURCE_EXHAUSTED). Stopping batch cleanly!", flush=True)
                        return None, 0, 0, 0.0
            if attempt < max_retries - 1 and not (quota_exhausted_event.is_set() or budget_circuit_breaker_event.is_set()):
                sleep_time = backoff + (5 if is_quota_err else 0)
                time.sleep(sleep_time)
                backoff *= 2
            else:
                if not (quota_exhausted_event.is_set() or budget_circuit_breaker_event.is_set()):
                    print(f"  [ERROR] Vertex AI generation failed for {fid} after {max_retries} attempts: {e}", flush=True)
                return None, 0, 0, 0.0

# -------------------------------------------------------------------------
# Worker Function & Shard File Updater
# -------------------------------------------------------------------------
def process_formula(fid, client, model_name, formulas, file_map, parent_map, child_map, dry_run=False):
    form = formulas.get(fid)
    if not form: return False, 0, 0

    cur_lhi = calculate_lhi(fid, form, formulas, parent_map, child_map)
    candidates = find_candidate_pool(fid, form, formulas, top_k=25)

    print(f"⚙️ [{fid}] Current LHI: {cur_lhi}/100 | Candidates: {len(candidates)}...")
    enrichment, p_tok, c_tok, f_cost = generate_enrichment(client, model_name, fid, form, candidates)
    if not enrichment:
        return False, cur_lhi, cur_lhi

    # Deterministic Validation
    p_id = enrichment.get('parent_formula_id')
    if p_id and (p_id not in formulas or p_id == fid):
        p_id = None
    enrichment['parent_formula_id'] = p_id

    valid_subcomponents = []
    for cid in enrichment.get('subcomponents', []):
        if cid in formulas and cid != fid and cid not in valid_subcomponents:
            valid_subcomponents.append(cid)
    enrichment['subcomponents'] = valid_subcomponents

    # Merge with original formula object
    merged = dict(form)
    for k, v in enrichment.items():
        if v is not None:
            merged[k] = v

    new_lhi = calculate_lhi(fid, merged, formulas, parent_map, child_map)
    cost_tag = f" | Cost: ${f_cost:.5f}" if is_paid_session else ""
    print(f"  ✅ [{fid}] Enriched LHI: {cur_lhi} ➔ {new_lhi}/100 (Parent: {p_id or 'Axiom'}, Subcomponents: {len(valid_subcomponents)}){cost_tag}")

    if dry_run:
        print(f"  [DRY-RUN] Would update {file_map[fid]}")
        return True, cur_lhi, new_lhi

    # Thread-safe atomic write to shard
    shard_path = file_map[fid]
    lock = shard_file_locks.setdefault(shard_path, threading.Lock())
    with lock:
        with open(shard_path, 'r', encoding='utf-8') as f:
            shard_data = json.load(f)
        shard_data[fid] = merged
        with open(shard_path, 'w', encoding='utf-8') as f:
            json.dump(shard_data, f, indent=4, ensure_ascii=False)

    # In-memory update
    formulas[fid] = merged
    if p_id:
        parent_map[fid] = p_id
        child_map.setdefault(p_id, []).append(fid)
    for cid in valid_subcomponents:
        child_map.setdefault(fid, []).append(cid)

    # Save to checkpoint
    with global_state_lock:
        checkpoint = load_checkpoint()
        checkpoint['session_spend_usd'] = cumulative_session_spend_usd
        checkpoint['session_prompt_tokens'] = cumulative_prompt_tokens
        checkpoint['session_candidates_tokens'] = cumulative_candidates_tokens
        checkpoint['max_cost_dollars'] = global_max_cost_dollars
        checkpoint['is_paid_session'] = is_paid_session
        checkpoint['active_model'] = model_name

        checkpoint['processed_ids'][fid] = {
            'timestamp': int(time.time()),
            'old_lhi': cur_lhi,
            'new_lhi': new_lhi,
            'parent_id': p_id,
            'model': model_name,
            'cost_usd': f_cost,
            'prompt_tokens': p_tok,
            'candidates_tokens': c_tok
        }
        save_checkpoint(checkpoint)

    return True, cur_lhi, new_lhi

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {'processed_ids': {}}

def save_checkpoint(data):
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------------------------------------------------------
# Main Execution CLI
# -------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Vertex AI Lineage & Derivation Enrichment Engine")
    parser.add_argument('--filter', choices=['isolated', 'thin', 'moderate', 'all'], default='isolated',
                        help="Filter target formulas by LHI score: isolated (0), thin (1-39), moderate (40-74), all")
    parser.add_argument('--target-id', type=str, help="Target a specific formula ID directly")
    parser.add_argument('--limit', type=int, default=0, help="Maximum formulas to process (0 = all matching in filter)")
    parser.add_argument('--batch-size', type=int, default=8, help="Batch chunk size for graph sync and progress reporting (default: 8)")
    parser.add_argument('--concurrency', type=int, default=8, help="Number of worker threads (default: 8)")
    parser.add_argument('--dry-run', action='store_true', help="Simulate without writing updates to shards")
    parser.add_argument('--rebuild-graph', action='store_true', help="Rebuild derivation graph and sync MariaDB between batches")
    parser.add_argument('--provider', choices=['free', 'aistudio', 'prepaid', 'vertex', 'auto'], default='free',
                        help="API Provider: 'free' (Pure $0.00 Free Tier via GEMINI_FREE_API_KEY), 'prepaid' (Prepaid Project Key), or 'vertex' (GCP Service Account)")
    parser.add_argument('--model', type=str, default='gemini-3.7-flash', help="Gemini model name (default: gemini-3.7-flash)")
    parser.add_argument('--max-cost-dollars', type=float, default=0.0,
                        help="Hard Circuit Breaker: Stop instantly if cumulative spend reaches this dollar amount (0.0 = unlimited)")
    args = parser.parse_args()

    global global_max_cost_dollars, is_paid_session
    global_max_cost_dollars = args.max_cost_dollars
    is_paid_session = (args.provider in ['prepaid', 'vertex'])

    print("=" * 65)
    print("🚀 Terra Physics Lab - Vertex AI Lineage & Derivation Engine")
    cost_banner = f"${args.max_cost_dollars:.2f} Hard Limit" if args.max_cost_dollars > 0 else "Unconstrained"
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE ATOMIC UPDATE'} | Model: {args.model} | Concurrency: {args.concurrency}")
    print(f"Provider: {args.provider} | Budget Cap: {cost_banner}")
    print("=" * 65)

    formulas, file_map, parent_map, child_map = load_all_shards()
    print(f"[INFO] Loaded {len(formulas):,} formulas across 256 shards.")

    client, model_name, provider_desc = get_gemini_client(args.model, args.provider)
    print(f"[INFO] Initialized Engine Client ({model_name}) via {provider_desc}.")

    checkpoint = load_checkpoint()
    already_processed = set(checkpoint.get('processed_ids', {}).keys())
    if already_processed:
        print(f"[INFO] Loaded checkpoint with {len(already_processed):,} previously enriched formulas.")

    # Select target formulas
    target_ids = []
    if args.target_id:
        if args.target_id in formulas:
            target_ids = [args.target_id]
        else:
            print(f"[ERROR] Target formula ID '{args.target_id}' not found in shards.")
            sys.exit(1)
    else:
        for fid, form in formulas.items():
            if fid in already_processed:
                continue
            lhi = calculate_lhi(fid, form, formulas, parent_map, child_map)
            if args.filter == 'isolated' and lhi == 0:
                target_ids.append(fid)
            elif args.filter == 'thin' and 0 < lhi < 40:
                target_ids.append(fid)
            elif args.filter == 'moderate' and 40 <= lhi < 75:
                target_ids.append(fid)
            elif args.filter == 'all':
                if lhi < 80:
                    target_ids.append(fid)

        print(f"[INFO] Found {len(target_ids):,} unprocessed formulas matching filter '{args.filter}'.")
        if args.limit > 0:
            target_ids = target_ids[:args.limit]
            print(f"[INFO] Limit applied: processing first {len(target_ids)} formulas.")

    if not target_ids:
        print("✓ No target formulas to process. Everything in this filter is already enriched!")
        return

    print(f"[INFO] Total Queue: {len(target_ids)} formulas (Chunk Size: {args.batch_size}, Concurrency: {args.concurrency})\n")

    overall_start = time.time()
    last_heartbeat_time = overall_start
    total_processed = 0
    total_successful = 0
    total_lhi_gain = 0

    chunks = [target_ids[i:i + args.batch_size] for i in range(0, len(target_ids), args.batch_size)]

    for chunk_idx, chunk in enumerate(chunks, 1):
        chunk_start = time.time()
        results = []

        with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
            futures = {
                executor.submit(process_formula, fid, client, model_name, formulas, file_map, parent_map, child_map, args.dry_run): fid
                for fid in chunk
            }
            for fut in as_completed(futures):
                fid = futures[fut]
                try:
                    success, old_s, new_s = fut.result()
                    results.append((fid, success, old_s, new_s))
                except Exception as exc:
                    print(f"[ERROR] Worker exception on {fid}: {exc}")

        chunk_elapsed = time.time() - chunk_start
        chunk_success = [r for r in results if r[1]]
        chunk_gain = sum(r[3] - r[2] for r in chunk_success)

        total_processed += len(results)
        total_successful += len(chunk_success)
        total_lhi_gain += chunk_gain

        now = time.time()
        elapsed_total = now - overall_start
        speed = total_processed / elapsed_total if elapsed_total > 0 else 0
        avg_gain = total_lhi_gain / total_successful if total_successful else 0
        remaining = len(target_ids) - total_processed
        etc_mins = (remaining / speed / 60) if speed > 0 else 0
        pct = (total_processed / len(target_ids)) * 100

        # Emit 30s heartbeat or chunk summary
        if now - last_heartbeat_time >= 30 or chunk_idx == len(chunks) or chunk_idx <= 3:
            time_str = time.strftime('%H:%M:%S')
            spend_str = f" | Spent: ${cumulative_session_spend_usd:.4f}" if is_paid_session else " | $0.00 (Free)"
            if is_paid_session and global_max_cost_dollars > 0:
                spend_str += f" / ${global_max_cost_dollars:.2f}"
            print(f"[{time_str}] ⏱️ Chunk [{chunk_idx}/{len(chunks)}] | Done: {total_processed}/{len(target_ids)} ({pct:.1f}%){spend_str} | Speed: {speed:.2f} f/s | Avg LHI: +{avg_gain:.1f} pts | ETC: {etc_mins:.1f}m")
            last_heartbeat_time = now

        if args.rebuild_graph and not args.dry_run and chunk_success:
            os.system("python3 scripts/build_formula_graph.py > /dev/null 2>&1")
            os.system("php scripts/sync_formulas_to_mariadb.php > /dev/null 2>&1")

        if budget_circuit_breaker_event.is_set():
            print(f"\n🛑 Circuit Breaker: Reached budget threshold (${cumulative_session_spend_usd:.4f} >= ${global_max_cost_dollars:.2f}). Stopping runner cleanly!")
            break

        if quota_exhausted_event.is_set():
            print("\n🛑 Quota exhaustion detected across consecutive workers. Stopping runner gracefully!")
            break

    total_elapsed = time.time() - overall_start
    overall_avg_gain = total_lhi_gain / total_successful if total_successful else 0

    print("\n" + "=" * 65)
    print("🏁 ALL BATCH CHUNKS COMPLETE")
    print(f"  • Total Processed:   {total_processed}")
    print(f"  • Total Successful:  {total_successful}")
    if is_paid_session:
        print(f"  • Total Spent:       ${cumulative_session_spend_usd:.4f} (Tokens: {cumulative_prompt_tokens:,} prompt, {cumulative_candidates_tokens:,} comp)")
    else:
        print("  • Total Cost:        $0.00 (Pure Free Tier)")
    print(f"  • Average LHI Gain:  +{overall_avg_gain:.1f} points")
    print(f"  • Total Elapsed:     {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    print("=" * 65)

if __name__ == '__main__':
    main()
