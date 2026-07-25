#!/usr/bin/env python3
"""
⚡ Automated Full-Shard Formula Sanitizer
Scans all 256 formula shards (shard_00.json .. shard_ff.json), cleans control characters,
repairs broken TeX math delimiters, standardizes Dirac bra-ket notation, purges spurious
formatting fallback variables, and saves cleanly formatted JSON shards.
"""

import os
import sys
import json
import glob
import re
import tempfile
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')

# Spurious variable keys to purge from semantic_variables
SPURIOUS_VAR_KEYS = {
    r"\(\quad\)", r"\quad", r"\(\langle\)", r"\(\rangle\)", r"\langle", r"\rangle",
    r"\(\delta\)", r"\delta", r"\(P\)", r"\(a\)", r"\(n\)", r"\P\)", r"\a\)", r"\n\)",
    r"\(\psi\)", r"\(\Psi\)", r"\(\mu\)", r"\(\Omega\)", r"\(L\)", r"\(x\)", r"\(d\)"
}

def sanitize_text(text):
    if not isinstance(text, str):
        return text

    # 1. Repair backspace \x08 / \b -> \delta when used as math symbol
    text = re.sub(r'[\x08]', r'\\delta', text)
    # Fix raw \b left before uppercase/lowercase/symbol
    text = re.sub(r'(?<!\\)\b S\b', r'\\delta S', text)
    text = re.sub(r'(?<!\\)\b ∫', r'\\delta \\int', text)

    # 2. Repair tab \x09 / \t wrapping math expressions \t(expr)\t -> $(expr)$
    text = re.sub(r'\t\((.*?)\)\t', r'$\1$', text)
    text = re.sub(r'\t([\w\=\+\-\*\/\^\\\s\(\)\{\}\|]+)\t', r'$\1$', text)
    text = re.sub(r'\t', '', text)

    # 3. Clean remaining non-printable control characters (\x00-\x07, \x0b, \x0c, \x0e-\x1f)
    text = re.sub(r'[\x00-\x07\x0b\x0c\x0e-\x1f]', '', text)

    # 4. Standardize legacy \( and \) delimiters to $
    # Avoid replacing already-escaped double backslashes in JSON string contexts
    text = re.sub(r'\\\(', '$', text)
    text = re.sub(r'\\\)', '$', text)
    text = re.sub(r'\\\[', '$$', text)
    text = re.sub(r'\\\]', '$$', text)

    # 5. Fix nested/duplicate dollar signs like $ $ -> $ or $\( -> $
    text = re.sub(r'\$\s*\$', '', text)
    text = re.sub(r'\$\s*\$([^\$]+)\$\s*\$', r'$\1$', text)

    # 6. Fix corrupted bra-ket unicode notation
    text = re.sub(r'\|ψ_n⟩\s*\\rangle', r'$|\\psi_n\\rangle$', text)
    text = re.sub(r'\|ψ_n⟩', r'$|\\psi_n\\rangle$', text)
    text = re.sub(r'\|Ψ⟩', r'$|\\Psi\\rangle$', text)
    text = re.sub(r'< Ψ \|', r'$\\langle \\Psi |$', text)
    text = re.sub(r'<\s*\\psi\s*\|\s*\\Psi\s*>', r'$\\langle \\psi | \\Psi \\rangle$', text)

    # 7. Normalize multiple spaces inside equations/text
    text = re.sub(r'[ \t]{2,}', ' ', text)

    return text.strip()

def sanitize_variables(variables, equation=""):
    if not isinstance(variables, dict):
        return variables

    new_vars = {}
    for key, var_data in variables.items():
        clean_key = sanitize_text(key)

        # Check if key is in spurious list
        if key in SPURIOUS_VAR_KEYS or clean_key in SPURIOUS_VAR_KEYS:
            continue

        # If var_data is a dict, sanitize its fields
        if isinstance(var_data, dict):
            sanitized_var = {}
            for k, v in var_data.items():
                if isinstance(v, str):
                    sanitized_var[k] = sanitize_text(v)
                else:
                    sanitized_var[k] = v
            new_vars[clean_key] = sanitized_var
        else:
            new_vars[clean_key] = var_data

    return new_vars

def sanitize_formula(formula_obj):
    if not isinstance(formula_obj, dict):
        return formula_obj

    fields_to_sanitize = [
        'title', 'conceptual_definition', 'intuitive_summary',
        'interpretation', 'symmetry_origin', 'limits_and_boundary'
    ]

    for field in fields_to_sanitize:
        if field in formula_obj and isinstance(formula_obj[field], str):
            formula_obj[field] = sanitize_text(formula_obj[field])

    if 'semantic_variables' in formula_obj:
        eq = formula_obj.get('equation', '')
        formula_obj['semantic_variables'] = sanitize_variables(formula_obj['semantic_variables'], equation=eq)

    return formula_obj

def sanitize_shard(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"❌ Error loading {os.path.basename(filepath)}: {e}")
            return False, 0

    if not isinstance(data, dict):
        return False, 0

    modified = False
    repaired_formulas = 0

    new_data = {}
    for formula_id, formula_obj in data.items():
        original_json = json.dumps(formula_obj, sort_keys=True)
        sanitized_obj = sanitize_formula(formula_obj)
        sanitized_json = json.dumps(sanitized_obj, sort_keys=True)

        if original_json != sanitized_json:
            modified = True
            repaired_formulas += 1

        new_data[formula_id] = sanitized_obj

    if modified:
        cleaned_str = json.dumps(new_data, indent=4, ensure_ascii=False) + "\n"
        temp_fd, temp_path = tempfile.mkstemp(dir=os.path.dirname(filepath))
        try:
            with open(temp_fd, 'w', encoding='utf-8') as f:
                f.write(cleaned_str)
            os.replace(temp_path, filepath)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            print(f"❌ Error saving {os.path.basename(filepath)}: {e}")
            return False, 0

    return modified, repaired_formulas

def main():
    shard_files = sorted(glob.glob(os.path.join(FORMULAS_DIR, "shard_*.json")))
    print(f"🧹 Starting Full-Shard Formula Sanitization across {len(shard_files)} shards...")

    total_modified_shards = 0
    total_repaired_formulas = 0

    for filepath in shard_files:
        filename = os.path.basename(filepath)
        modified, count = sanitize_shard(filepath)
        if modified:
            total_modified_shards += 1
            total_repaired_formulas += count
            print(f"  ✓ Repaired {count} formulas in {filename}")

    print(f"\n✨ Sanitization Complete!")
    print(f"   - Modified Shards: {total_modified_shards} / {len(shard_files)}")
    print(f"   - Repaired Formulas: {total_repaired_formulas}")

if __name__ == '__main__':
    main()
