#!/usr/bin/env python3
"""
Phase 3: Automated Ingestion Pipeline for Subcomponent Equations using Google GenAI (Vertex AI / Gemini 2.5 Flash).

Reads `app/config/unindexed_subcomponents.json`, deduplicates sub-expressions,
asynchronously generates schema-compliant formula objects via Gemini API with
bounded 25-worker concurrency, populates parent/child relationships, and updates
physics formula shards in `app/config/content/formulas/{prefix}/shard_{prefix}.json`.
"""

import os
import sys
import json
import glob
import hashlib
import re
import asyncio
import random
import argparse
from typing import Dict, List, Any
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

INPUT_CATALOG = os.path.join(PROJECT_ROOT, "app/config/unindexed_subcomponents.json")
FORMULAS_DIR = os.path.join(PROJECT_ROOT, "app/config/content/formulas")
LATEX_INDEX_FILE = os.path.join(PROJECT_ROOT, "app/config/content/formulas_latex_index.json")
CHECKPOINT_FILE = os.path.join(PROJECT_ROOT, "app/config/subcomponents_checkpoint.json")

CONCURRENCY_LIMIT = 25

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def get_shard_prefix(formula_id: str) -> str:
    return hashlib.md5(formula_id.encode('utf-8')).hexdigest()[:2]

def normalize_latex(latex: str) -> str:
    if not latex:
        return ""
    latex = re.sub(r'\\(mathbf|vec|text|cssId|style|class)\{[^}]*\}', '', latex)
    latex = re.sub(r'[\s\$\\\{\}\(\)]', '', latex)
    return "".join(sorted(latex.lower()))

def load_formula_registry() -> Dict[str, Dict[str, Any]]:
    registry = {}
    for root, _, files in os.walk(FORMULAS_DIR):
        for f in files:
            if f.startswith("shard_") and f.endswith(".json"):
                with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                    try:
                        registry.update(json.load(fp))
                    except Exception:
                        pass
    return registry

def load_latex_index() -> Dict[str, str]:
    if os.path.exists(LATEX_INDEX_FILE):
        with open(LATEX_INDEX_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_checkpoint() -> Dict[str, Any]:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_subcomponents": [], "generated_formula_ids": []}

def save_checkpoint(checkpoint: Dict[str, Any]):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump(checkpoint, f, indent=4)

def prepare_subcomponent_queue() -> List[Dict[str, Any]]:
    with open(INPUT_CATALOG, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    latex_index = load_latex_index()
    indexed_normalized = set(latex_index.keys())

    subcomponent_map = {}

    for master in catalog.get("master_formulas", []):
        m_id = master["formula_id"]
        m_title = master["title"]
        m_eq = master["master_equation"]

        for sub_tex in master.get("missing_subcomponents", []):
            norm = normalize_latex(sub_tex)
            if not norm or len(norm) < 2:
                continue
            if norm in indexed_normalized:
                continue

            if norm not in subcomponent_map:
                subcomponent_map[norm] = {
                    "raw_tex": sub_tex,
                    "normalized_tex": norm,
                    "masters": [],
                    "frequency": 0
                }
            subcomponent_map[norm]["masters"].append({
                "formula_id": m_id,
                "title": m_title,
                "master_equation": m_eq
            })
            subcomponent_map[norm]["frequency"] += 1

    queue = list(subcomponent_map.values())
    queue.sort(key=lambda x: x["frequency"], reverse=True)
    return queue

def sanitize_latex_json(raw_text: str) -> str:
    raw_text = re.sub(r"^```json\s*", "", raw_text.strip(), flags=re.IGNORECASE)
    raw_text = re.sub(r"```$", "", raw_text.strip())

    # Protect true JSON escape sequences
    raw_text = raw_text.replace("\\\\", "\x01")
    raw_text = raw_text.replace("\\\"", "\x02")

    # Any remaining single backslash before a character should be double-escaped
    raw_text = re.sub(r"\\([^\x01\x02])", r"\\\\\1", raw_text)

    # Restore true JSON escape sequences
    raw_text = raw_text.replace("\x02", "\\\"")
    raw_text = raw_text.replace("\x01", "\\\\")

    return raw_text

async def generate_formula_object(
    client: genai.Client,
    sub: Dict[str, Any],
    semaphore: asyncio.Semaphore,
    max_retries: int = 4
) -> Dict[str, Any]:
    async with semaphore:
        raw_tex = sub["raw_tex"]
        primary_master = sub["masters"][0]
        master_title = primary_master["title"]
        master_eq = primary_master["master_equation"]

        prompt = f"""
You are a theoretical physics formula cataloger.
Create a complete, rigorous JSON formula record for the subcomponent mathematical equation: ${raw_tex}$.

This equation is a component inside the master formula '{master_title}' (${master_eq}$).

IMPORTANT: Escape all LaTeX backslashes in JSON strings as double backslashes (e.g. \\\\frac, \\\\theta, \\\\mathbf, \\\\mu, \\\\psi).

Return ONLY valid JSON matching this exact schema:
{{
    "title": "Descriptive Scientific Title (string, 3-7 words)",
    "description": "Concise summary of the equation (string, 1-2 sentences)",
    "conceptual_definition": "Fulsome conceptual definition in physics (string, 2-4 sentences)",
    "interpretation": "Detailed physical interpretation of what this equation represents (string, 3-5 sentences)",
    "limits_and_boundary": "Physical limits, asymptotic behavior, or boundary conditions (string)",
    "symmetry_origin": "Symmetries or conservation laws underlying this formula (string)",
    "unit_system": "SI",
    "derivation_type": "DERIVED_FROM",
    "equation_family": "Appropriate domain cluster slug e.g. thermodynamic-relations or relativistic-kinematics",
    "semantic_variables": {{
        "var_name": "Full description of variable including units and physical meaning"
    }}
}}
"""

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )

        for attempt in range(max_retries):
            try:
                response = await client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=config
                )
                cleaned_text = sanitize_latex_json(response.text)
                data = json.loads(cleaned_text)
                data["equation"] = raw_tex
                data["status"] = "published"
                data["parent_formula_id"] = primary_master["formula_id"]
                data["subcomponents"] = []

                # Create ID
                title_slug = slugify(data.get("title", raw_tex))
                tex_hash = hashlib.md5(raw_tex.encode('utf-8')).hexdigest()[:8]
                data["id"] = f"{title_slug}-{tex_hash}"

                return data
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"  ❌ Failed to generate formula for '${raw_tex}$': {e}")
                    return None
                await asyncio.sleep((2 ** attempt) + random.uniform(0.1, 1.0))

def save_formula_to_shard(formula_data: Dict[str, Any]):
    f_id = formula_data["id"]
    prefix = get_shard_prefix(f_id)
    subdir = os.path.join(FORMULAS_DIR, prefix)
    os.makedirs(subdir, exist_ok=True)
    shard_file = os.path.join(subdir, f"shard_{prefix}.json")

    shard_data = {}
    if os.path.exists(shard_file):
        with open(shard_file, "r", encoding="utf-8") as f:
            try:
                shard_data = json.load(f)
            except Exception:
                pass

    shard_data[f_id] = formula_data

    with open(shard_file, "w", encoding="utf-8") as f:
        json.dump(shard_data, f, indent=4, ensure_ascii=False)

def link_subcomponents_to_masters(generated_formulas: List[Dict[str, Any]], queue_map: Dict[str, Dict[str, Any]]):
    """Appends child formula IDs to master equations' subcomponents array."""
    formula_registry = load_formula_registry()

    updated_shards = set()
    for formula in generated_formulas:
        f_id = formula["id"]
        norm = normalize_latex(formula["equation"])

        if norm in queue_map:
            for master_ref in queue_map[norm]["masters"]:
                m_id = master_ref["formula_id"]
                if m_id in formula_registry:
                    master_data = formula_registry[m_id]
                    if "subcomponents" not in master_data or not isinstance(master_data["subcomponents"], list):
                        master_data["subcomponents"] = []
                    if f_id not in master_data["subcomponents"]:
                        master_data["subcomponents"].append(f_id)

                    # Save updated master formula
                    m_prefix = get_shard_prefix(m_id)
                    m_shard_file = os.path.join(FORMULAS_DIR, m_prefix, f"shard_{m_prefix}.json")
                    if os.path.exists(m_shard_file):
                        with open(m_shard_file, "r", encoding="utf-8") as f:
                            s_content = json.load(f)
                        s_content[m_id] = master_data
                        with open(m_shard_file, "w", encoding="utf-8") as f:
                            json.dump(s_content, f, indent=4, ensure_ascii=False)
                        updated_shards.add(m_shard_file)

    print(f"  - Updated parent subcomponents array across {len(updated_shards)} master equation shards.")

def update_latex_index(generated_formulas: List[Dict[str, Any]]):
    latex_index = load_latex_index()
    for formula in generated_formulas:
        norm = normalize_latex(formula["equation"])
        if norm:
            latex_index[norm] = formula["id"]
    with open(LATEX_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(latex_index, f, indent=4, ensure_ascii=False)
    print(f"  - Updated LaTeX index (`formulas_latex_index.json`) with {len(generated_formulas)} new mappings.")

async def main_async(limit: int = 100):
    if not GENAI_AVAILABLE:
        print("❌ Error: `google.genai` SDK is not installed.")
        sys.exit(1)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY is missing from environment.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    checkpoint = load_checkpoint()
    completed_norms = set(checkpoint.get("completed_subcomponents", []))

    queue = prepare_subcomponent_queue()
    unprocessed_queue = [item for item in queue if item["normalized_tex"] not in completed_norms]

    if limit > 0:
        unprocessed_queue = unprocessed_queue[:limit]

    print(f"🚀 Starting Phase 3 Subcomponent Ingestion for {len(unprocessed_queue)} candidate equations...")
    print(f"  - Concurrency: {CONCURRENCY_LIMIT} parallel async workers via Gemini 2.5 Flash")

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    queue_map = {item["normalized_tex"]: item for item in unprocessed_queue}

    tasks = [
        generate_formula_object(client, sub, semaphore)
        for sub in unprocessed_queue
    ]

    results = await asyncio.gather(*tasks)

    valid_results = [r for r in results if r is not None]
    print(f"  - Generated {len(valid_results)} valid schema-compliant subcomponent formula objects.")

    for formula in valid_results:
        save_formula_to_shard(formula)
        norm = normalize_latex(formula["equation"])
        checkpoint["completed_subcomponents"].append(norm)
        checkpoint["generated_formula_ids"].append(formula["id"])

    save_checkpoint(checkpoint)
    link_subcomponents_to_masters(valid_results, queue_map)
    update_latex_index(valid_results)

    print("✅ Batch Ingestion Complete!")

def main():
    parser = argparse.ArgumentParser(description="Phase 3 Subcomponent Ingestion Pipeline")
    parser.add_argument("--limit", type=int, default=100, help="Maximum number of subcomponents to process (default: 100, 0 for all)")
    args = parser.parse_args()

    asyncio.run(main_async(limit=args.limit))

if __name__ == "__main__":
    main()
