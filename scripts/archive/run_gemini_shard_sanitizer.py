#!/usr/bin/env python3
"""
Terra Physics Lab - GCP Vertex AI (Gemini 2.5 Pro) Multi-Threaded Shard Sanitizer Engine
Runs 4 concurrent worker threads to evaluate formulas using Gemini 2.5 Pro on Vertex AI
with thread-safe atomic shard updates, robust TeX JSON parsing, and milestone logging.
"""

import os
import re
import json
import time
import base64
import subprocess
import urllib.request
import urllib.parse
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(ROOT_DIR, "gcp-credentials.json")
MANIFEST_FILE = os.path.join(ROOT_DIR, "app/config/audit_remediation_manifest.json")
CHECKPOINT_FILE = os.path.join(ROOT_DIR, "app/config/shard_sanitizer_checkpoint.json")
PROGRESS_STATUS_FILE = os.path.join(ROOT_DIR, "app/config/shard_sanitizer_status.json")
SHARDS_DIR = os.path.join(ROOT_DIR, "app/config/content/formulas")

CONCURRENCY = 4  # Sweet spot for GCP Vertex AI quota and fast throughput
BATCH_SIZE = 2
LOCATION = "us-central1"
MODEL_NAME = "gemini-2.5-pro"

# Thread safety locks
shard_locks = {}
global_lock = threading.Lock()


class VertexAIAuth:
    def __init__(self, credentials_path):
        with open(credentials_path, "r") as f:
            self.sa = json.load(f)
        self.token = None
        self.expiry = 0
        self._auth_lock = threading.Lock()

    def invalidate_token(self):
        with self._auth_lock:
            self.token = None
            self.expiry = 0

    def get_token(self, force_refresh=False):
        with self._auth_lock:
            now = int(time.time())
            if not force_refresh and self.token and now < self.expiry - 60:
                return self.token

            header = {"alg": "RS256", "typ": "JWT"}
            claim = {
                "iss": self.sa["client_email"],
                "scope": "https://www.googleapis.com/auth/cloud-platform",
                "aud": "https://oauth2.googleapis.com/token",
                "exp": now + 3600,
                "iat": now,
            }

            def b64url(data):
                if isinstance(data, str):
                    data = data.encode("utf-8")
                return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

            unsigned = b64url(json.dumps(header)) + "." + b64url(json.dumps(claim))

            with tempfile.NamedTemporaryFile("w", delete=False) as kf:
                kf.write(self.sa["private_key"])
                key_path = kf.name

            try:
                p = subprocess.Popen(
                    ["openssl", "dgst", "-sha256", "-sign", key_path, "-binary"],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                sig, _ = p.communicate(input=unsigned.encode("utf-8"))
                jwt_token = unsigned + "." + b64url(sig)
            finally:
                if os.path.exists(key_path):
                    os.remove(key_path)

            token_req_data = urllib.parse.urlencode({
                "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                "assertion": jwt_token,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=token_req_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            with urllib.request.urlopen(req) as resp:
                token_res = json.loads(resp.read().decode())
                self.token = token_res.get("access_token")
                self.expiry = now + int(token_res.get("expires_in", 3600))
                return self.token

    @property
    def project_id(self):
        return self.sa.get("project_id")


SYSTEM_PROMPT = """You are a Principal Theoretical Physicist & LaTeX Master Editor for the Terra Physics Laboratory.
Your task is to repair and sanitize formula records from our knowledge base shards.

For each formula provided:
1. "equation": Provide the 100% correct, standard canonical LaTeX equation.
   - If the input equation is "REG" or placeholder, replace it with the standard canonical physics formula for that title.
   - Fix all OCR corruptions (e.g. \\nabla^\\mu G_{\\mu u} -> \\nabla^\\mu G_{\\mu\\nu}, \\partial corrupted as 'tial', Latin letters in tensor indices).
   - Use standard LaTeX commands (\\mathrm{d} for differentials, \\partial for partials, \\approx for approximations).
2. "conceptual_definition": 1-2 sentence rigorous physical definition. Clean all inline TeX ($...$) and prose formatting.
3. "intuitive_summary": 1 clear sentence explaining physical intuition.
4. "interpretation": Rigorous derivation, physical meaning, and mathematical structure with perfectly balanced $...$ delimiters.
5. "symmetry_origin": Symmetries (gauge, spacetime, continuous, discrete) and Noether conservation laws.
6. "limits_and_boundary": Numbered list of exact physical limits (e.g. c->inf non-relativistic, hbar->0 classical, flat spacetime).
7. "semantic_variables": Structured dictionary mapping every variable/constant/operator in the equation to its name, type, SI unit, and description.
8. "status": "platinum"

Return a strict JSON object mapping formula IDs to their sanitized objects:
{
  "formula-id-1": {
    "title": "...",
    "equation": "...",
    "conceptual_definition": "...",
    "intuitive_summary": "...",
    "interpretation": "...",
    "symmetry_origin": "...",
    "limits_and_boundary": "...",
    "status": "platinum",
    "semantic_variables": {
      "\\psi": { "name": "Wave Function", "type": "variable", "unit": "m^{-3/2}", "description": "..." }
    }
  }
}
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
        fixed = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', text)
        return json.loads(fixed, strict=False)


def call_vertex_sanitizer(auth, batch_items):
    project_id = auth.project_id
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{LOCATION}/publishers/google/models/{MODEL_NAME}:generateContent"

    prompt_items = []
    for item in batch_items:
        prompt_items.append({
            "id": item["id"],
            "title": item["title"],
            "current_equation": item["equation"],
            "detected_anomalies": item["anomalies"],
            "current_data": item.get("full_data", {})
        })

    user_text = "Please sanitize and standardize these physical formulas to platinum quality:\n" + json.dumps(prompt_items, indent=2)

    payload = {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.1
        }
    }

    max_retries = 6
    backoff = 2
    for attempt in range(max_retries):
        token = auth.get_token()
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return robust_json_decode(text)
        except urllib.error.HTTPError as e:
            print(f"  [WARN] Vertex AI request attempt {attempt+1} failed: {e}")
            if e.code == 401:
                auth.invalidate_token()
            time.sleep(backoff)
            backoff *= 2
        except Exception as e:
            print(f"  [WARN] Vertex AI request attempt {attempt+1} failed: {e}")
            time.sleep(backoff)
            backoff *= 2

    raise RuntimeError("Failed to call Vertex AI after max retries")


def apply_updates_to_shards(sanitized_batch, manifest):
    by_shard = {}
    for f_id, cleaned_data in sanitized_batch.items():
        if f_id in manifest:
            sf = os.path.join(ROOT_DIR, manifest[f_id]["shard_path"])
            if sf not in by_shard:
                by_shard[sf] = {}
            by_shard[sf][f_id] = cleaned_data

    for sf, formulas in by_shard.items():
        if not os.path.exists(sf):
            continue
        
        # Thread-safe write per shard
        with global_lock:
            if sf not in shard_locks:
                shard_locks[sf] = threading.Lock()
            shard_lock = shard_locks[sf]

        with shard_lock:
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    shard_data = json.load(f)
                
                for f_id, c_data in formulas.items():
                    if f_id in shard_data:
                        orig = shard_data[f_id]
                        orig.update(c_data)
                        orig["status"] = "platinum"
                        shard_data[f_id] = orig
                    else:
                        c_data["id"] = f_id
                        shard_data[f_id] = c_data

                with open(sf, "w", encoding="utf-8") as f:
                    json.dump(shard_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                print(f"  [ERROR] Failed writing updates to {sf}: {e}")


def write_milestone_status(total_manifest, checkpoint_count, elapsed_seconds):
    pct = (checkpoint_count / total_manifest) * 100.0
    rate = checkpoint_count / elapsed_seconds if elapsed_seconds > 0 else 0
    remaining_formulas = max(0, total_manifest - checkpoint_count)
    eta_seconds = remaining_formulas / rate if rate > 0 else 0

    status = {
        "timestamp": time.time(),
        "total_manifest": total_manifest,
        "completed": checkpoint_count,
        "remaining": remaining_formulas,
        "percent_complete": round(pct, 1),
        "elapsed_minutes": round(elapsed_seconds / 60, 1),
        "eta_minutes": round(eta_seconds / 60, 1),
        "concurrency": CONCURRENCY,
        "model": MODEL_NAME
    }

    with open(PROGRESS_STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


def process_single_batch(batch_tuple, auth, manifest):
    batch_idx, batch_items = batch_tuple
    t0 = time.time()
    sanitized = call_vertex_sanitizer(auth, batch_items)
    dt = time.time() - t0
    apply_updates_to_shards(sanitized, manifest)
    return batch_idx, sanitized, dt


def main():
    print("========================================================================")
    print("Terra Physics Lab - GCP Vertex AI (Gemini 2.5 Pro) Multi-Threaded Engine")
    print(f"Project: gen-lang-client-0170965498 | Model: {MODEL_NAME} | Concurrency: {CONCURRENCY}x")
    print("========================================================================")

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[ERROR] Missing {CREDENTIALS_FILE}. Aborting.")
        return

    auth = VertexAIAuth(CREDENTIALS_FILE)
    print(f"[OK] Authenticated GCP Service Account for Project: {auth.project_id}")

    if not os.path.exists(MANIFEST_FILE):
        print(f"[ERROR] Manifest {MANIFEST_FILE} not found. Run audit_shard_anomalies.py first.")
        return

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    total_manifest = len(manifest)
    print(f"[INFO] Total anomalies in manifest: {total_manifest}")

    checkpoint = {}
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                checkpoint = json.load(f)
            print(f"[INFO] Loaded checkpoint with {len(checkpoint)} completed formulas.")
        except Exception as e:
            print(f"[WARN] Could not load checkpoint: {e}")

    remaining_ids = [fid for fid in manifest if fid not in checkpoint]
    print(f"[INFO] Remaining formulas to sanitize: {len(remaining_ids)}")

    if not remaining_ids:
        print("[SUCCESS] All flagged formulas have already been sanitized via GCP Vertex AI!")
        return

    # Attach full data from shard
    items_to_process = []
    for fid in remaining_ids:
        m_info = manifest[fid]
        sf = os.path.join(ROOT_DIR, m_info["shard_path"])
        full_data = {}
        if os.path.exists(sf):
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    s_json = json.load(f)
                    full_data = s_json.get(fid, {})
            except Exception:
                pass
        m_info["full_data"] = full_data
        items_to_process.append(m_info)

    # Chunk into batches
    batches = []
    for b_idx in range(0, len(items_to_process), BATCH_SIZE):
        batch = items_to_process[b_idx : b_idx + BATCH_SIZE]
        batches.append(((b_idx // BATCH_SIZE) + 1, batch))

    total_batches = len(batches)
    print(f"[INFO] Launching {total_batches} Vertex AI batches across {CONCURRENCY} parallel workers...\n")

    start_time = time.time()
    completed_count = len(checkpoint)
    last_milestone_pct = int((completed_count / total_manifest) * 10) * 10

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
        futures = {executor.submit(process_single_batch, b, auth, manifest): b for b in batches}

        for future in as_completed(futures):
            try:
                batch_num, sanitized, dt = future.result()
                with global_lock:
                    for f_id in sanitized:
                        checkpoint[f_id] = True
                    completed_count = len(checkpoint)

                    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as cf:
                        json.dump(checkpoint, cf)

                    elapsed = time.time() - start_time
                    write_milestone_status(total_manifest, completed_count, elapsed)

                    pct = (completed_count / total_manifest) * 100.0
                    current_milestone_pct = int(pct / 10) * 10

                    print(f"  [✓] Worker Finished Batch {batch_num}/{total_batches} ({len(sanitized)} formulas in {dt:.1f}s) | Progress: {completed_count}/{total_manifest} ({pct:.1f}%)")

                    # Log milestone hit
                    if current_milestone_pct > last_milestone_pct:
                        last_milestone_pct = current_milestone_pct
                        print(f"\n========================================================")
                        print(f"  🎉 MILESTONE REACHED: {current_milestone_pct}% COMPLETE ({completed_count}/{total_manifest} formulas)")
                        print(f"  Elapsed: {elapsed/60:.1f} mins | Est. Remaining: {((total_manifest - completed_count) / (completed_count/elapsed))/60:.1f} mins")
                        print(f"========================================================\n")

            except Exception as e:
                print(f"  [ERROR] Worker batch failed: {e}")

    total_dt = time.time() - start_time
    print(f"\n[COMPLETE] Sanitized {len(checkpoint)} formulas across shards in {total_dt/60:.1f} minutes via GCP Vertex AI!")


if __name__ == "__main__":
    main()
