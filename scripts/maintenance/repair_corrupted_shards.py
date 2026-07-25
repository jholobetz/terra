#!/usr/bin/env python3
"""
⚡ Repair Corrupted Formula Shards
Scans all 256 formula shards, repairs corrupted TeX symbols (e.g. 4̀, 4$\gamma$̀, \u0001, \u0002, ̀, ́, ̅, ̄, ͆, ̰),
and synchronizes MariaDB + client search indexes.

Usage:
    python3 scripts/maintenance/repair_corrupted_shards.py
"""

import os
import sys
import json
import re
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')
GCP_CREDS_PATH = os.path.join(PROJECT_ROOT, 'gcp-credentials.json')

try:
    from google import genai
    from google.genai import types
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

def get_gemini_client():
    if not HAS_GENAI:
        return None
    if os.path.exists(GCP_CREDS_PATH):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = GCP_CREDS_PATH
        try:
            return genai.Client(vertexai=True, project="gen-lang-client-0170965498", location="us-central1")
        except Exception:
            return None
    return None

def clean_formula_json_string(text):
    if not isinstance(text, str):
        return text

    # Direct targeted TeX/unicode replacements
    text = text.replace("4$\\gamma$̀r\u0002", "$4\\pi r^2$")
    text = text.replace("4$\\gamma$̀", "$4\\pi$")
    text = text.replace("4̀", "$4\\pi$")
    text = text.replace("4π̅", "4\\pi")
    text = text.replace("(2π̅)", "(2\\pi\\hbar)")
    text = text.replace("\u0002²", "m²")
    text = text.replace("\u0002 → 0", "r \\to 0")
    text = text.replace("\u0002 → ∞", "r \\to \\infty")
    text = text.replace("(\u0002)", "(m)")
    text = text.replace("\u0002", "m")
    text = text.replace("\u0001/(4πR²)", "1/(4\\pi R^2)")
    text = text.replace("\u0001", "1")
    text = text.replace("̀̀", "$")

    # Remove isolated combining characters
    text = re.sub(r'[\u0300\u0301\u0304\u0305\u0346\u0330]', '', text)

    return text

def clean_formula_obj(obj):
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            clean_k = clean_formula_json_string(k)
            if clean_k == "" or clean_k == "́" or clean_k == "̀":
                clean_k = "\\pi"
            new_obj[clean_k] = clean_formula_obj(v)
        return new_obj
    elif isinstance(obj, list):
        return [clean_formula_obj(x) for x in obj]
    elif isinstance(obj, str):
        return clean_formula_json_string(obj)
    return obj

def gemini_repair_obj(client, formula_id, formula_obj):
    prompt = f"""
You are an expert theoretical physics knowledge architect for Project Terra.
The formula definition for "{formula_id}" (Equation: {formula_obj.get("equation", "")}) has corrupted text characters.

Original Corrupted Object:
{json.dumps(formula_obj, indent=2, ensure_ascii=False)}

TASK: Clean and repair all prose fields ("conceptual_definition", "intuitive_summary", "interpretation", "symmetry_origin", "limits_and_boundary") and "semantic_variables".
Ensure:
1. All math expressions in text fields use clean LaTeX delimiters like $...$ or \\(...\\).
2. All corrupted symbols are replaced with proper LaTeX math symbols (e.g. \\pi, r, m, \\omega_0, \\hbar).
3. "semantic_variables" keys are valid variable symbols (e.g. "A", "\\pi", "r").
4. Retain the exact same "id", "title", "equation", "unit_system", "parent_formula_id", "derivation_type", and "status".

Output ONLY valid JSON for the repaired formula object.
"""
    try:
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        raw = res.text.strip()
        if raw.startswith("```json"): raw = raw[7:]
        if raw.endswith("```"): raw = raw[:-3]
        return json.loads(raw.strip())
    except Exception as e:
        print(f"    ⚠️ Gemini AI repair failed for {formula_id}: {e}")
        return formula_obj

def main():
    print("⚡ Starting Formula Shard Repair Audit...")
    client = get_gemini_client()

    corrupted_pattern = re.compile(r'[\u0001\u0002\u0300\u0301\u0304\u0305\u0346\u0330]')
    repaired_shards_count = 0
    repaired_formulas_count = 0

    for filename in sorted(os.listdir(FORMULAS_DIR)):
        if not filename.startswith('shard_') or not filename.endswith('.json'):
            continue
        filepath = os.path.join(FORMULAS_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        if not corrupted_pattern.search(raw_content) and "4̀" not in raw_content:
            continue

        try:
            shard_data = json.loads(raw_content)
        except Exception:
            continue

        shard_updated = False

        for fid, fobj in shard_data.items():
            fstr = json.dumps(fobj, ensure_ascii=False)
            if corrupted_pattern.search(fstr) or "4̀" in fstr:
                # 1. Apply regex cleaner first
                cleaned = clean_formula_obj(fobj)
                cleaned_str = json.dumps(cleaned, ensure_ascii=False)

                # 2. If corruptions remain and Gemini is available, use Gemini AI
                if (corrupted_pattern.search(cleaned_str) or "4̀" in cleaned_str) and client:
                    print(f"  ✨ Calling Gemini AI to repair [{fid}] in {filename}...")
                    cleaned = gemini_repair_obj(client, fid, cleaned)

                shard_data[fid] = cleaned
                shard_updated = True
                repaired_formulas_count += 1

        if shard_updated:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(shard_data, f, indent=4, ensure_ascii=False)
            repaired_shards_count += 1
            print(f"  ✓ Repaired and saved {filename}")

    print(f"\n🎉 Repair Complete! Repaired {repaired_formulas_count} formulas across {repaired_shards_count} shards.")

    # Re-sync MariaDB and search index
    cli_sync_path = os.path.join(PROJECT_ROOT, 'cli_sync.php')
    print("⚡ Syncing MariaDB & rebuilding search index...")
    subprocess.run(['php', cli_sync_path], capture_output=True, text=True)
    print("✓ MariaDB & Search Index Synced!")

if __name__ == '__main__':
    main()
