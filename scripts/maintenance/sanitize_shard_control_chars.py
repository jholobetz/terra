#!/usr/bin/env python3
"""
🛡️ Shard TeX Control Character & Corrupted Token Sanitizer
Restores unescaped TeX control character collisions and broken prefixes:
- \bar{\nu} (corrupted to ar{\nu})
- \bar{X} (corrupted to ar{X})
- \beta (corrupted to \x08eta or eta)
- \frac (corrupted to \x0crac or rac{)
- \nu, \nabla (corrupted by raw newline \n)
- \tau, \theta, \text, \times, \to (corrupted by tab \t)
"""

import os
import glob
import json
import re

def restore_tex_control_chars(text: str) -> str:
    if not isinstance(text, str):
        return text
    
    # 1. Fix broken \bar prefixes (caused by \b backspace stripping)
    text = text.replace(r'ar{\nu', r'\bar{\nu}')
    text = text.replace(r'ar{\mu', r'\bar{\mu}')
    text = text.replace(r'ar{\tau', r'\bar{\tau}')
    text = text.replace(r'ar{\psi', r'\bar{\psi}')
    text = text.replace(r'ar{q', r'\bar{q}')
    text = text.replace(r'ar{u', r'\bar{u}')
    text = text.replace(r'ar{d', r'\bar{d}')
    text = text.replace(r'ar{s', r'\bar{s}')
    text = text.replace(r'ar{c', r'\bar{c}')
    text = text.replace(r'ar{b', r'\bar{b}')
    text = text.replace(r'ar{t', r'\bar{t}')
    text = text.replace(r'ar{\mathbf', r'\bar{\mathbf')
    text = text.replace(r'ar{K', r'\bar{K}')
    text = text.replace(r'ar{B', r'\bar{B}')
    text = text.replace(r'ar{D', r'\bar{D}')
    text = text.replace(r'ar{p', r'\bar{p}')
    text = text.replace(r'ar{n', r'\bar{n}')
    text = text.replace(r'ar{\theta', r'\bar{\theta}')
    text = text.replace(r'ar{\lambda', r'\bar{\lambda}')

    # 2. Fix 0x08 (backspace) and broken \beta
    text = text.replace('\x08eta', r'\beta')
    text = text.replace('\x08', '')
    text = re.sub(r'(\$[^$]*?)(\b|(?<=[^a-zA-Z\\]))eta\b([^$]*?\$)', r'\1\\beta\3', text)

    # 3. Fix 0x0C (formfeed) and broken \frac
    text = text.replace('\x0crac', r'\frac')
    text = text.replace('\x0c rac', r'\frac')
    text = text.replace('\x0c', '')
    text = re.sub(r'(\$[^$]*?)(\b|(?<=[^a-zA-Z\\]))rac\{', r'\1\\frac{', text)

    # 4. Fix 0x09 (tab) collisions
    text = text.replace('\tau', r'\tau')
    text = text.replace('\theta', r'\theta')
    text = text.replace('\text', r'\text')
    text = text.replace('\times', r'\times')
    text = text.replace('\to', r'\to')
    text = text.replace('\tan', r'\tan')
    text = text.replace('\tr', r'\tr')
    text = text.replace('\tilde', r'\tilde')
    text = text.replace('\top', r'\top')
    text = text.replace('\tensor', r'\tensor')
    text = text.replace('\t', ' ')

    # 5. Fix 0x0A (newline) math collisions (\nu, \nabla)
    # Restore newline before 'u' in math blocks
    def fix_math_newlines(match):
        math_content = match.group(0)
        math_content = re.sub(r'(^|[\s_^{\\(])\n\s*u([\s_^{^\\),.;\-]|$)', r'\1\\nu\2', math_content)
        math_content = re.sub(r'(^|[\s_^{\\(])\n\s*nabla([\s_^{^\\),.;\-]|$)', r'\1\\nabla\2', math_content)
        math_content = re.sub(r'\\n\s*u([\s_^{^\\),.;\-]|$)', r'\\nu\1', math_content)
        math_content = re.sub(r'\\n\s*nabla([\s_^{^\\),.;\-]|$)', r'\\nabla\1', math_content)
        return math_content

    text = re.sub(r'\$[^\$]+\$', fix_math_newlines, text)
    text = re.sub(r'\\\[[^\]]+\\\]', fix_math_newlines, text)

    return text

def sanitize_value(val):
    if isinstance(val, str):
        return restore_tex_control_chars(val)
    elif isinstance(val, dict):
        return {k: sanitize_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_value(elem) for elem in val]
    return val

def run_sanitization():
    shards = sorted(glob.glob('app/config/content/formulas/*/shard_*.json'))
    print(f"[INFO] Scanning and sanitizing {len(shards)} formula shards...")
    
    shards_modified = 0
    total_formulas_cleaned = 0
    
    for s_path in shards:
        with open(s_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        try:
            data = json.loads(raw_content)
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON in {s_path}: {e}")
            continue
        
        modified = False
        cleaned_data = {}
        
        for f_id, f_data in data.items():
            cleaned_f = sanitize_value(f_data)
            if cleaned_f != f_data:
                modified = True
                total_formulas_cleaned += 1
            cleaned_data[f_id] = cleaned_f
        
        if modified:
            with open(s_path, 'w', encoding='utf-8') as f:
                json.dump(cleaned_data, f, indent=4, ensure_ascii=False)
            shards_modified += 1
            
    print(f"\n[SUMMARY] Sanitization pass complete:")
    print(f"  - Shards modified: {shards_modified} / {len(shards)}")
    print(f"  - Formulas repaired: {total_formulas_cleaned}")

if __name__ == '__main__':
    run_sanitization()
