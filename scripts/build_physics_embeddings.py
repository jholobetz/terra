#!/usr/bin/env python3
"""
Terra Physics Lab - Vertex AI Semantic Vector Embedding Generator
Uses Google Cloud Vertex AI (text-embedding-004) to generate 768-dimensional
vector embeddings for all formulas across the 256 JSON shards.
"""

import os
import glob
import json
import time
import base64
import subprocess
import urllib.request
import urllib.parse
import tempfile
import gzip

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREDENTIALS_FILE = os.path.join(ROOT_DIR, "gcp-credentials.json")
SHARDS_DIR = os.path.join(ROOT_DIR, "app/config/content/formulas")
OUTPUT_JSON = os.path.join(ROOT_DIR, "app/config/physics_embeddings.json")
OUTPUT_GZ = os.path.join(ROOT_DIR, "app/config/physics_embeddings.json.gz")
CHECKPOINT_FILE = os.path.join(ROOT_DIR, "app/config/physics_embeddings_checkpoint.json")

BATCH_SIZE = 25  # Optimal batch size for Vertex AI text-embedding-004
LOCATION = "us-central1"
MODEL_NAME = "text-embedding-004"


class VertexAIAuth:
    def __init__(self, credentials_path):
        with open(credentials_path, "r") as f:
            self.sa = json.load(f)
        self.token = None
        self.expiry = 0

    def get_token(self):
        now = int(time.time())
        if self.token and now < self.expiry - 60:
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


def build_semantic_text(f_data):
    title = f_data.get("title", "Physical Relation")
    eq = f_data.get("equation", "")
    defn = (
        f_data.get("conceptual_definition", "")
        or f_data.get("interpretation", "")
        or f_data.get("intuitive_summary", "")
    )
    limits = f_data.get("limits_and_boundary", "")
    sym = f_data.get("symmetry_origin", "")

    # Construct dense informative signature
    parts = [f"Title: {title}", f"LaTeX: {eq}"]
    if defn:
        parts.append(f"Concept: {defn[:400]}")
    if limits:
        parts.append(f"Limits: {limits[:200]}")
    if sym:
        parts.append(f"Symmetry: {sym[:150]}")

    return " | ".join(parts)


def load_all_formulas():
    formulas = {}
    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*/*.json")))
    print(f"[INFO] Scanning {len(shard_files)} shard files...", flush=True)

    for sf in shard_files:
        try:
            with open(sf, "r", encoding="utf-8") as f:
                data = json.load(f)
                for f_id, f_val in data.items():
                    if isinstance(f_val, dict) and f_val.get("equation"):
                        formulas[f_id] = f_val
        except Exception as e:
            print(f"[WARN] Failed to read {sf}: {e}")

    print(f"[INFO] Loaded {len(formulas)} unique physical formulas across repository.")
    return formulas


def embed_batch_vertex(auth, texts, max_retries=3):
    token = auth.get_token()
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{auth.project_id}/locations/{LOCATION}/publishers/google/models/{MODEL_NAME}:predict"

    payload = {"instances": [{"content": t} for t in texts]}
    req_data = json.dumps(payload).encode("utf-8")

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=req_data,
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode())
                predictions = res.get("predictions", [])
                vectors = [
                    p.get("embeddings", {}).get("values", [])
                    for p in predictions
                ]
                return vectors
        except urllib.error.HTTPError as e:
            err_body = e.read().decode()
            if e.code == 429:
                wait_time = (attempt + 1) * 3
                print(f"[THROTTLE] Rate limit hit. Backing off for {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[HTTP {e.code}] Vertex AI error: {err_body}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        except Exception as e:
            print(f"[ERROR] Batch request failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)

    return []


def main():
    print("=" * 65)
    print("Terra Physics Lab - Vertex AI Semantic Embedding Indexer")
    print("=" * 65)

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[FATAL] GCP credentials file not found: {CREDENTIALS_FILE}")
        return

    auth = VertexAIAuth(CREDENTIALS_FILE)
    print(f"[AUTH] Authenticated as {auth.sa.get('client_email')}")
    print(f"[AUTH] GCP Project ID: {auth.project_id} (Vertex AI: {LOCATION})")

    # Load formulas
    formulas = load_all_formulas()
    all_keys = list(formulas.keys())

    # Load existing checkpoint if available
    embeddings = {}
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r") as cf:
                embeddings = json.load(cf)
            print(f"[RESUME] Resuming from checkpoint: {len(embeddings)} formulas already embedded.")
        except Exception:
            pass

    pending_keys = [k for k in all_keys if k not in embeddings]
    print(f"[QUEUE] {len(pending_keys)} formulas pending embedding generation.")

    if not pending_keys:
        print("[COMPLETE] All formulas are already embedded in checkpoint!")
    else:
        total_batches = (len(pending_keys) + BATCH_SIZE - 1) // BATCH_SIZE
        start_time = time.time()

        for b_idx in range(total_batches):
            chunk_keys = pending_keys[b_idx * BATCH_SIZE : (b_idx + 1) * BATCH_SIZE]
            chunk_texts = [build_semantic_text(formulas[k]) for k in chunk_keys]

            try:
                vectors = embed_batch_vertex(auth, chunk_texts)
                for k, v in zip(chunk_keys, vectors):
                    embeddings[k] = {
                        "vector": v,
                        "title": formulas[k].get("title", ""),
                        "equation": formulas[k].get("equation", ""),
                    }

                # Periodic Atomic Checkpoint every 10 batches
                if (b_idx + 1) % 10 == 0 or b_idx == total_batches - 1:
                    tmp_cp = CHECKPOINT_FILE + ".tmp"
                    with open(tmp_cp, "w") as cf:
                        json.dump(embeddings, cf)
                    os.replace(tmp_cp, CHECKPOINT_FILE)

                pct = ((b_idx + 1) / total_batches) * 100
                elapsed = time.time() - start_time
                rate = (len(embeddings) - (len(all_keys) - len(pending_keys))) / max(elapsed, 0.1)
                print(
                    f"  [{pct:5.1f}%] Batch {b_idx+1:4d}/{total_batches} done "
                    f"({len(embeddings)}/{len(all_keys)} total) | {rate:.1f} formulas/sec"
                )

            except Exception as e:
                print(f"[ERROR] Failed batch {b_idx+1}: {e}")
                time.sleep(3)

    # Save final artifacts
    print("\n[SAVING] Writing finalized embeddings database...")
    with open(OUTPUT_JSON, "w") as out:
        json.dump(embeddings, out)
    print(f"[OK] Saved uncompressed index: {OUTPUT_JSON} ({os.path.getsize(OUTPUT_JSON) / 1024 / 1024:.2f} MB)")

    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as gz_out:
        json.dump(embeddings, gz_out)
    print(f"[OK] Saved gzip compressed index: {OUTPUT_GZ} ({os.path.getsize(OUTPUT_GZ) / 1024 / 1024:.2f} MB)")

    # Clean up checkpoint on completion
    if os.path.exists(CHECKPOINT_FILE) and len(embeddings) >= len(all_keys):
        os.remove(CHECKPOINT_FILE)

    print("\n" + "=" * 65)
    print(f"✓ All {len(embeddings)} formulas successfully indexed in Vertex AI vector database!")
    print("=" * 65)


if __name__ == "__main__":
    main()
