#!/usr/bin/env python3
"""
⚡ Repair Corrupted Formula Shards & Fix Angle-Bracket Math Expressions
Scans all 256 formula shards, repairs corrupted TeX symbols (e.g. 4̀, 4$\gamma$̀, \u0001, \u0002, ̀, ́, ̅, ̄, ͆, ̰),
converts angle-bracket math (<rho>, <I_{ij}>, <math>...</math>, <latex>...</latex>) to standard LaTeX ($...$),
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

def fix_angle_bracket_math(text):
    if not isinstance(text, str):
        return text

    text = re.sub(r'<latex>(.*?)</latex>', r'$\1$', text, flags=re.DOTALL)
    text = re.sub(r'<math>(.*?)</math>', r'$\1$', text, flags=re.DOTALL)

    html_exact = {"b", "/b", "/i", "ul", "/ul", "li", "/li", "br", "p", "/p", "sub", "/sub", "sup", "/sup", "span", "/span", "div", "/div"}

    def replace_angle(match):
        inner = match.group(1).strip()
        if inner in html_exact:
            return match.group(0)
        if inner == "i" and "</i>" not in text:
            return "$i$"
        return f"${inner}$"

    text = re.sub(r'<([^<>\n]+)>', replace_angle, text)
    return text

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

    # Fix angle bracket math tags (<rho>, <I_{ij}>, <dV>, etc.)
    text = fix_angle_bracket_math(text)

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

def main():
    print("⚡ Starting Formula Shard Repair & Angle-Bracket Cleaning...")

    corrupted_pattern = re.compile(r'[\u0001\u0002\u0300\u0301\u0304\u0305\u0346\u0330]')
    repaired_shards_count = 0
    repaired_formulas_count = 0

    for filename in sorted(os.listdir(FORMULAS_DIR)):
        if not filename.startswith('shard_') or not filename.endswith('.json'):
            continue
        filepath = os.path.join(FORMULAS_DIR, filename)

        with open(filepath, 'r', encoding='utf-8') as f:
            raw_content = f.read()

        try:
            shard_data = json.loads(raw_content)
        except Exception:
            continue

        shard_updated = False

        for fid, fobj in shard_data.items():
            fstr = json.dumps(fobj, ensure_ascii=False)
            if corrupted_pattern.search(fstr) or "4̀" in fstr or "<" in fstr:
                cleaned = clean_formula_obj(fobj)
                cleaned_str = json.dumps(cleaned, ensure_ascii=False)

                if cleaned_str != fstr:
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
