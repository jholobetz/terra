#!/usr/bin/env python3
"""
Terra Physics Lab - Vertex AI Subtopic Article-Level Vector Embedding Generator
Uses Google Cloud Vertex AI (text-embedding-004) to generate 768-dimensional
vector embeddings for all ~1,527 Subtopic Encyclopedia Articles.
"""

import os
import re
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
CONTENT_DIR = os.path.join(ROOT_DIR, "app/config/content")
OUTPUT_JSON = os.path.join(ROOT_DIR, "app/config/subtopic_embeddings.json")
OUTPUT_GZ = os.path.join(ROOT_DIR, "app/config/subtopic_embeddings.json.gz")
CHECKPOINT_FILE = os.path.join(ROOT_DIR, "app/config/subtopic_embeddings_checkpoint.json")

BATCH_SIZE = 25  # Optimal batch size for Vertex AI text-embedding-004
LOCATION = "us-central1"
MODEL_NAME = "text-embedding-004"

DOMAIN_FILES = [
    ("astrophysics.json", "Astrophysics & Cosmology"),
    ("classical-mechanics.json", "Classical Mechanics & Dynamics"),
    ("condensed-matter.json", "Condensed Matter & Solid State Physics"),
    ("electromagnetism.json", "Electromagnetism & Electrodynamics"),
    ("fluids-nonlinear.json", "Fluid Mechanics & Nonlinear Dynamics"),
    ("mathematical-methods.json", "Mathematical Methods & Differential Geometry"),
    ("philosophy-of-physics.json", "Philosophy of Physics & Foundations"),
    ("quantum-physics.json", "Quantum Mechanics & Quantum Information"),
    ("relativity.json", "Special & General Relativity"),
    ("standard-model.json", "High Energy Physics & Standard Model"),
    ("theoretical-physics.json", "Theoretical Physics & Field Theory"),
    ("thermodynamics-statistical-mechanics.json", "Thermodynamics & Statistical Mechanics")
]


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


def strip_html_and_svg(html_str):
    if not html_str:
        return ""
    # Remove SVG tags and their contents
    cleaned = re.sub(r"<svg[\s\S]*?</svg>", " ", html_str)
    # Remove HTML tags
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    # Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def build_subtopic_semantic_text(title, domain_name, raw_content):
    clean_text = strip_html_and_svg(raw_content)
    # Extract first 1200 characters of rich conceptual prose
    prose_snippet = clean_text[:1200]
    return f"Title: {title} | Domain: {domain_name} | Concept & Overview: {prose_snippet}"


def call_vertex_embeddings_batch(auth, texts):
    """
    Calls GCP Vertex AI text-embedding-004 endpoint with a batch of texts.
    Returns list of 768-dim float vectors.
    """
    token = auth.get_token()
    project_id = auth.project_id
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{LOCATION}/publishers/google/models/{MODEL_NAME}:predict"

    instances = []
    for t in texts:
        instances.append({
            "content": t[:2048],
            "task_type": "RETRIEVAL_DOCUMENT"
        })

    payload = json.dumps({"instances": instances}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }
    )

    max_retries = 5
    backoff = 2
    for attempt in range(max_retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                predictions = result.get("predictions", [])
                vectors = []
                for p in predictions:
                    emb = p.get("embeddings", {}).get("values", [])
                    vectors.append(emb)
                return vectors
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"  [WARN] Vertex AI HTTP error {e.code} on attempt {attempt+1}: {err_body}")
            if e.code == 429 or e.code >= 500:
                time.sleep(backoff)
                backoff *= 2
            else:
                raise
        except Exception as e:
            print(f"  [WARN] Request failed on attempt {attempt+1}: {e}")
            time.sleep(backoff)
            backoff *= 2

    raise RuntimeError("Max retries exceeded while calling Vertex AI API")


def main():
    print("===============================================================")
    print("Terra Physics Lab - Vertex AI Subtopic Article Embedding Engine")
    print(f"Model: {MODEL_NAME} | Dimensions: 768 | Location: {LOCATION}")
    print("===============================================================")

    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[ERROR] Missing {CREDENTIALS_FILE}. Aborting.")
        return

    auth = VertexAIAuth(CREDENTIALS_FILE)
    print(f"[OK] Authenticated GCP Service Account for project: {auth.project_id}")

    # 1. Load All Subtopics across Domain Files
    subtopic_records = []
    seen_slugs = set()

    for filename, domain_title in DOMAIN_FILES:
        filepath = os.path.join(CONTENT_DIR, filename)
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                for slug, item in data.items():
                    if not isinstance(item, dict) or "title" not in item:
                        continue
                    if slug in seen_slugs:
                        continue
                    seen_slugs.add(slug)
                    
                    title = item.get("title", slug)
                    raw_content = item.get("content", "")
                    clean_snippet = strip_html_and_svg(raw_content)[:200]
                    semantic_text = build_subtopic_semantic_text(title, domain_title, raw_content)

                    subtopic_records.append({
                        "slug": slug,
                        "title": title,
                        "domain": domain_title,
                        "snippet": clean_snippet + "...",
                        "semantic_text": semantic_text
                    })
        except Exception as e:
            print(f"[ERROR] Failed to read {filename}: {e}")

    total_subtopics = len(subtopic_records)
    print(f"[INFO] Loaded {total_subtopics} unique Subtopic Articles across all domains.")

    # 2. Check for existing checkpoint
    embeddings_db = {}
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                embeddings_db = json.load(f)
            print(f"[INFO] Loaded checkpoint with {len(embeddings_db)} existing embeddings.")
        except Exception as e:
            print(f"[WARN] Failed to load checkpoint: {e}")

    # Filter remaining
    todo_records = [r for r in subtopic_records if r["slug"] not in embeddings_db]
    print(f"[INFO] Remaining articles to vectorize: {len(todo_records)}")

    if not todo_records:
        print("[INFO] All subtopic articles already embedded! Generating final outputs...")
    else:
        # Process in batches
        start_time = time.time()
        for i in range(0, len(todo_records), BATCH_SIZE):
            batch = todo_records[i : i + BATCH_SIZE]
            texts = [r["semantic_text"] for r in batch]
            
            t0 = time.time()
            vectors = call_vertex_embeddings_batch(auth, texts)
            dt = time.time() - t0

            for r, vec in zip(batch, vectors):
                embeddings_db[r["slug"]] = {
                    "slug": r["slug"],
                    "title": r["title"],
                    "domain": r["domain"],
                    "snippet": r["snippet"],
                    "vector": [round(x, 6) for x in vec]
                }

            pct = (len(embeddings_db) / total_subtopics) * 100.0
            print(f"  -> Vectorized batch {i//BATCH_SIZE + 1}/{(len(todo_records) + BATCH_SIZE - 1)//BATCH_SIZE} "
                  f"({len(batch)} items in {dt:.2f}s) | Progress: {len(embeddings_db)}/{total_subtopics} ({pct:.1f}%)")

            # Checkpoint every 5 batches
            if (i // BATCH_SIZE) % 5 == 0:
                with open(CHECKPOINT_FILE, "w", encoding="utf-8") as cf:
                    json.dump(embeddings_db, cf)

        total_elapsed = time.time() - start_time
        print(f"[OK] Completed all batches in {total_elapsed:.1f}s.")

    # 3. Write Final Production Vector DB Files
    print(f"[INFO] Writing production vector DB to {OUTPUT_JSON}...")
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(embeddings_db, f, indent=2)

    print(f"[INFO] Writing compressed vector DB to {OUTPUT_GZ}...")
    with gzip.open(OUTPUT_GZ, "wt", encoding="utf-8") as gz:
        json.dump(embeddings_db, gz)

    # Clean up checkpoint
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)

    raw_mb = os.path.getsize(OUTPUT_JSON) / (1024 * 1024)
    gz_mb = os.path.getsize(OUTPUT_GZ) / (1024 * 1024)
    print(f"[SUCCESS] Subtopic Article Dense Vector Database Built!")
    print(f"  - Total Articles: {len(embeddings_db)}")
    print(f"  - JSON Size: {raw_mb:.2f} MB")
    print(f"  - GZIP Size: {gz_mb:.2f} MB")


if __name__ == "__main__":
    main()
