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
# Vertex AI / Gemini Client Initialization
# -------------------------------------------------------------------------
def get_gemini_client(model_choice='gemini-2.5-flash', provider='auto'):
    if not HAS_GENAI_SDK:
        raise RuntimeError("google-genai SDK not installed. Run: pip install google-genai")

    # 1. Check for standard GEMINI_API_KEY (Google AI Studio Free Tier)
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
            if key:
                api_key = key
        except Exception:
            pass

    if provider == 'aistudio' or (provider == 'auto' and api_key and not os.path.exists(GCP_CREDS_PATH)):
        if not api_key:
            raise RuntimeError("Google AI Studio mode selected but no GEMINI_API_KEY found in .env or environment.")
        client = genai.Client(api_key=api_key)
        return client, model_choice, "Google AI Studio (Free Tier)"

    # 2. GCP Service Account Credentials (Vertex AI mode)
    if (provider == 'vertex' or provider == 'auto') and os.path.exists(GCP_CREDS_PATH):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDS_PATH
        try:
            with open(GCP_CREDS_PATH, 'r', encoding='utf-8') as f:
                creds_data = json.load(f)
                project_id = creds_data.get('project_id', 'gen-lang-client-0170965498')
        except Exception:
            project_id = 'gen-lang-client-0170965498'

        client = genai.Client(vertexai=True, project=project_id, location='us-central1')
        return client, model_choice, f"Vertex AI (GCP Project: {project_id})"

    if api_key:
        client = genai.Client(api_key=api_key)
        return client, model_choice, "Google AI Studio (Free Tier)"

    raise RuntimeError("No Vertex AI credentials (gcp-credentials.json) or GEMINI_API_KEY found.")

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

    # 3. Aggressive fallback for TeX JSON payloads
    try:
        # Escape all single backslashes in property values
        def repl(m):
            s = m.group(0)
            return s.replace('\\', '\\\\')
        
        fixed_lines = []
        for line in text.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                fixed_lines.append(f"{k}:{re.sub(r'(?<!\\\\)\\\\(?![\"\\\\/bfnrtu])', r'\\\\\\\\', v)}")
            else:
                fixed_lines.append(line)
        return json.loads('\n'.join(fixed_lines), strict=False)
    except Exception as e:
        raise ValueError(f"Unable to parse JSON: {e}\nRaw output:\n{text[:200]}...")

import socket
socket.setdefaulttimeout(45.0)

def generate_enrichment(client, model_name, fid, form, candidates):
    cand_str = "\n".join([f"- ID: {c[1]} | Title: {c[2]} | Equation: {c[3]}" for c in candidates])

    prompt = f"""Target Formula to Enrich:
- Formula ID: {fid}
- Title: {form.get('title', 'Unknown')}
- LaTeX Equation: {form.get('equation', '')}
- Existing Description: {form.get('description', '')}
- Existing Interpretation: {form.get('interpretation', '')}

Candidate Grounding Pool (Select Parent ID and Subcomponents from here):
{cand_str if cand_str else "(No high-scoring matches - use fundamental first principles or create clean self-contained variables)"}

Provide the complete enriched formula JSON object with these exact keys:
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
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[SYSTEM_PROMPT, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json"
                )
            )
            return robust_json_decode(response.text)
        except Exception as e:
            if attempt < max_retries - 1:
                # Add extra delay if 429 rate limit
                sleep_time = backoff + (5 if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e) else 0)
                time.sleep(sleep_time)
                backoff *= 2
            else:
                print(f"  [ERROR] Vertex AI generation failed for {fid} after {max_retries} attempts: {e}", flush=True)
                return None

# -------------------------------------------------------------------------
# Worker Function & Shard File Updater
# -------------------------------------------------------------------------
def process_formula(fid, client, model_name, formulas, file_map, parent_map, child_map, dry_run=False):
    form = formulas.get(fid)
    if not form: return False, 0, 0

    cur_lhi = calculate_lhi(fid, form, formulas, parent_map, child_map)
    candidates = find_candidate_pool(fid, form, formulas, top_k=25)

    print(f"⚙️ [{fid}] Current LHI: {cur_lhi}/100 | Candidates: {len(candidates)}...")
    enrichment = generate_enrichment(client, model_name, fid, form, candidates)
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
    print(f"  ✅ [{fid}] Enriched LHI: {cur_lhi} ➔ {new_lhi}/100 (Parent: {p_id or 'Axiom'}, Subcomponents: {len(valid_subcomponents)})")

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
        checkpoint['processed_ids'][fid] = {
            'timestamp': int(time.time()),
            'old_lhi': cur_lhi,
            'new_lhi': new_lhi,
            'parent_id': p_id
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
    parser.add_argument('--provider', choices=['auto', 'aistudio', 'vertex'], default='auto',
                        help="API Provider: 'aistudio' (Google AI Studio Free Tier via GEMINI_API_KEY) or 'vertex' (GCP Vertex AI)")
    parser.add_argument('--model', type=str, default='gemini-2.5-flash', help="Gemini model name (default: gemini-2.5-flash)")
    args = parser.parse_args()

    print("=" * 65)
    print("🚀 Terra Physics Lab - Vertex AI Lineage & Derivation Engine")
    print(f"Mode: {'DRY RUN' if args.dry_run else 'LIVE ATOMIC UPDATE'} | Model: {args.model} | Concurrency: {args.concurrency}")
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
            print(f"[{time_str}] ⏱️ Chunk [{chunk_idx}/{len(chunks)}] | Done: {total_processed}/{len(target_ids)} ({pct:.1f}%) | Speed: {speed:.2f} f/s | Avg LHI: +{avg_gain:.1f} pts | ETC: {etc_mins:.1f}m")
            last_heartbeat_time = now

        if args.rebuild_graph and not args.dry_run and chunk_success:
            os.system("python3 scripts/build_formula_graph.py > /dev/null 2>&1")
            os.system("php scripts/sync_formulas_to_mariadb.php > /dev/null 2>&1")

    total_elapsed = time.time() - overall_start
    overall_avg_gain = total_lhi_gain / total_successful if total_successful else 0

    print("\n" + "=" * 65)
    print("🏁 ALL BATCH CHUNKS COMPLETE")
    print(f"  • Total Processed:   {total_processed}")
    print(f"  • Total Successful:  {total_successful}")
    print(f"  • Average LHI Gain:  +{overall_avg_gain:.1f} points")
    print(f"  • Total Elapsed:     {total_elapsed:.2f}s ({total_elapsed/60:.2f} minutes)")
    print("=" * 65)

if __name__ == '__main__':
    main()
