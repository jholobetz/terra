#!/usr/bin/env python3
"""
⚡ Repair Formula Prose Math Artifacts
Cleans corrupted unicode text and normalizes unformatted LaTeX math in formula shards.
"""

import os
import glob
import json
import re

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FORMULAS_DIR = os.path.join(PROJECT_ROOT, 'app', 'config', 'content', 'formulas')

def clean_prose_text(text):
    if not isinstance(text, str) or not text:
        return text

    # 1. Fix combining acute accent U+0301 -> \gamma
    cleaned = text.replace('\u0301', '\\gamma ')
    
    # 2. Fix common unicode subscripts and powers
    cleaned = cleaned.replace('L₀', '$L_0$')
    cleaned = cleaned.replace('L₁', '$L_1$')
    cleaned = cleaned.replace('E₀', '$E_0$')
    cleaned = cleaned.replace('m₀', '$m_0$')
    cleaned = cleaned.replace('P₀', '$P_0$')
    cleaned = cleaned.replace('V₀', '$V_0$')
    cleaned = cleaned.replace('T₀', '$T_0$')

    cleaned = cleaned.replace('v²', '$v^2$')
    cleaned = cleaned.replace('c²', '$c^2$')
    cleaned = cleaned.replace('x²', '$x^2$')
    cleaned = cleaned.replace('t²', '$t^2$')
    cleaned = cleaned.replace('r²', '$r^2$')
    cleaned = cleaned.replace('v²/c²', '$v^2/c^2$')

    cleaned = cleaned.replace('√(', '\\sqrt{')
    cleaned = re.sub(r'√([a-zA-Z0-9_]+)', r'\\sqrt{\1}', cleaned)

    cleaned = cleaned.replace('(ν ← c)', '($v \\to c$)')
    cleaned = cleaned.replace('(ν ← 0)', '($v \\to 0$)')
    cleaned = cleaned.replace('(́ ← 1)', '($\\gamma \\to 1$)')
    cleaned = cleaned.replace('(́ ← ∞)', '($\\gamma \\to \\infty$)')
    cleaned = cleaned.replace('ν²', '$v^2$')

    # Fix space around \gamma
    cleaned = re.sub(r'\\gamma([a-zA-Z])', r'\\gamma \1', cleaned)

    # 3. Auto-wrap unwrapped math expressions like L = L_0 / \gamma or E = \gamma mc^2
    def wrap_math_match(m):
        val = m.group(0).strip()
        if re.search(r'^(the|a|an|in|is|of|to|and|or|as|by|if|at|on|for|it|where)$', val, re.IGNORECASE):
            return val
        if '\\' in val or '_' in val or '^' in val or '=' in val:
            # Check trailing punct
            punct = ''
            if val.endswith('.') or val.endswith(',') or val.endswith(';'):
                punct = val[-1]
                val = val[:-1]
            return f"${val}${punct}"
        return m.group(0)

    # Wrap unwrapped math terms containing \gamma, \sqrt, _, ^
    cleaned = re.sub(r'\b[a-zA-Z0-9_\^\\\=\+\-\*\/]+\b(?:\s*[\=\+\-\*\/]\s*[a-zA-Z0-9_\^\\\=\+\-\*\/]+)+', wrap_math_match, cleaned)

    # Clean double dollars or nested math delimiters
    cleaned = cleaned.replace('$$', '$')
    cleaned = re.sub(r'\$\s*\$', '', cleaned)
    
    return cleaned

def process_file(filepath):
    changed = False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        data = json.loads(content)

        if isinstance(data, list):
            for item in data:
                for field in ['conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary']:
                    if field in item and isinstance(item[field], str):
                        original = item[field]
                        cleaned = clean_prose_text(original)
                        if cleaned != original:
                            item[field] = cleaned
                            changed = True
        elif isinstance(data, dict):
            for key, item in data.items():
                if isinstance(item, dict):
                    for field in ['conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary']:
                        if field in item and isinstance(item[field], str):
                            original = item[field]
                            cleaned = clean_prose_text(original)
                            if cleaned != original:
                                item[field] = cleaned
                                changed = True

        if changed:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"✓ Repaired math formatting in {os.path.basename(filepath)}")
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    total_repaired = 0
    for filepath in sorted(glob.glob(os.path.join(FORMULAS_DIR, '*.json'))):
        if process_file(filepath):
            total_repaired += 1
    print(f"⚡ Total shards repaired: {total_repaired}")

if __name__ == '__main__':
    main()
