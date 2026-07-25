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

    cleaned = text

    # Step 1: Full multi-token equation replacements (Exact matches)
    cleaned = cleaned.replace('L = L₀ / ́ = L₀ √(1 - v²/c²)', '$L = \\frac{L_0}{\\gamma} = L_0 \\sqrt{1 - \\frac{v^2}{c^2}}$')
    cleaned = cleaned.replace('́ = 1 / √(1 - v²/c²)', '$\\gamma = \\frac{1}{\\sqrt{1 - \\frac{v^2}{c^2}}}$')
    cleaned = cleaned.replace('L = -mc²√(1 - v²/c²)', '$L = -mc^2 \\sqrt{1 - \\frac{v^2}{c^2}}$')
    cleaned = cleaned.replace('E = mc²/√(1 - v²/c²)', '$E = \\frac{mc^2}{\\sqrt{1 - \\frac{v^2}{c^2}}}$')
    cleaned = cleaned.replace('p = mv/√(1 - v²/c²)', '$p = \\frac{mv}{\\sqrt{1 - \\frac{v^2}{c^2}}}$')
    cleaned = cleaned.replace('L = L₀ √(1 - v²/c²)', '$L = L_0 \\sqrt{1 - \\frac{v^2}{c^2}}$')
    cleaned = cleaned.replace('E = ́mc²', '$E = \\gamma mc^2$')
    cleaned = cleaned.replace('p = ́mv', '$p = \\gamma mv$')
    cleaned = cleaned.replace('L = T - V', '$L = T - V$')
    cleaned = cleaned.replace('S = ∫ L dt', '$S = \\int L dt$')

    # Step 2: Parenthesized limits and arrow expressions
    cleaned = cleaned.replace('(ν ← 0)', '($v \\to 0$)')
    cleaned = cleaned.replace('(ν ← c)', '($v \\to c$)')
    cleaned = cleaned.replace('(́ ← 1)', '($\\gamma \\to 1$)')
    cleaned = cleaned.replace('(́ ← ∞)', '($\\gamma \\to \\infty$)')
    cleaned = cleaned.replace('(L ← L₀)', '($L \\to L_0$)')
    cleaned = cleaned.replace('(L ← 0)', '($L \\to 0$)')

    # Step 3: Fractional & square root terms
    cleaned = cleaned.replace('√(1 - v²/c²)', '$\\sqrt{1 - \\frac{v^2}{c^2}}$')
    cleaned = cleaned.replace('(1 - v²/c²)', '$(1 - v^2/c^2)$')
    cleaned = cleaned.replace('(1 - ν²/c²)', '$(1 - v^2/c^2)$')
    cleaned = cleaned.replace('v²/c²', '$v^2/c^2$')
    cleaned = cleaned.replace('ν²/c²', '$v^2/c^2$')

    # Step 4: Individual symbol replacements
    cleaned = cleaned.replace('\u0301', '$\\gamma$')
    cleaned = cleaned.replace('L₀', '$L_0$')
    cleaned = cleaned.replace('L₁', '$L_1$')
    cleaned = cleaned.replace('E₀', '$E_0$')
    cleaned = cleaned.replace('m₀', '$m_0$')
    cleaned = cleaned.replace('P₀', '$P_0$')
    cleaned = cleaned.replace('V₀', '$V_0$')
    cleaned = cleaned.replace('T₀', '$T_0$')
    cleaned = cleaned.replace('mc²', '$mc^2$')
    cleaned = cleaned.replace('v²', '$v^2$')
    cleaned = cleaned.replace('c²', '$c^2$')
    cleaned = cleaned.replace('x²', '$x^2$')
    cleaned = cleaned.replace('t²', '$t^2$')
    cleaned = cleaned.replace('r²', '$r^2$')

    # Step 5: Clean up any double-wrapped math delimiters
    cleaned = cleaned.replace('$$', '$')
    cleaned = re.sub(r'\$\s*\$', '', cleaned)
    cleaned = re.sub(r'\$\(\$([^\$]+)\$\)\$', r'(\$\1\$)', cleaned)

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
