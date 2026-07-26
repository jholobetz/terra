import json
import glob
import re
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARD_DIR = os.path.join(PROJECT_ROOT, "app/config/content/formulas")

def fix_corrupted_text(text: str) -> str:
    if not isinstance(text, str) or not text:
        return text

    # Protect valid TeX macros starting with \n
    text = text.replace(r'\nabla', '__NABLA_PROTECT__')
    text = text.replace(r'\nu', '__NU_PROTECT__')
    text = text.replace(r'\neq', '__NEQ_PROTECT__')
    text = text.replace(r'\neg', '__NEG_PROTECT__')
    text = text.replace(r'\natural', '__NATURAL_PROTECT__')
    text = text.replace(r'\nearrow', '__NEARROW_PROTECT__')

    # Convert literal \n sequence to space
    text = text.replace(r'\n', ' ')

    # Restore TeX macros
    text = text.replace('__NABLA_PROTECT__', r'\nabla')
    text = text.replace('__NU_PROTECT__', r'\nu')
    text = text.replace('__NEQ_PROTECT__', r'\neq')
    text = text.replace('__NEG_PROTECT__', r'\neg')
    text = text.replace('__NATURAL_PROTECT__', r'\natural')
    text = text.replace('__NEARROW_PROTECT__', r'\nearrow')

    # Normalize multiple spaces
    text = re.sub(r'[ \t]+', ' ', text)

    # Clean misplaced $ inside \frac{...}
    text = re.sub(r'\\frac\{([^}]*)\$([^}]*)\}\{([^}]*)\$([^}]*)\}', r'\\frac{\1\2}{\3\4}', text)

    # Fix nested dollar signs like $P + $\frac{1}{2}$ \rho v^2...$
    def clean_math_block(match):
        inner = match.group(1)
        # remove inner $ signs
        cleaned_inner = inner.replace('$', '')
        return f'${cleaned_inner}$'

    # Clean dollar blocks
    text = re.sub(r'\$([^$]+)\$', clean_math_block, text)

    # Map Unicode pseudo-symbols to clean TeX expressions
    replacements = [
        (r'C_\{ₐ-ₜ\}', r'$C_{\\mathbf{k}-\\mathbf{G}}$'),
        (r'C_\{ₐ-ₜ\'\}', r'$C_{\\mathbf{k}-\\mathbf{G}\'}$'),
        (r'V_\{ₐ-ₜ\'\}', r'$V_{\\mathbf{G}-\\mathbf{G}\'}$'),
        (r'V_\{ₐ-ₜ\}', r'$V_{\\mathbf{G}-\\mathbf{G}}$'),
        (r'λ_\{ₐ-ₜ\}', r'$\\lambda_{\\mathbf{k}-\\mathbf{G}}$'),
        (r'λ_\{ₐ\}', r'$\\lambda_{\\mathbf{k}}$'),
        (r'λ', r'$\\lambda$'),
        (r'\(Ι\)\)', r'$C_{\\mathbf{k}-\\mathbf{G}}$'),
        (r'\(Ιₓ\)', r'$C_{\\mathbf{k}-\\mathbf{G}}$'),
        (r'\(Ι\)', r'$C_{\\mathbf{k}-\\mathbf{G}}$'),
        (r'ₐ - ₜ\'', r'$\\mathbf{k} - \\mathbf{G}\'$'),
        (r'ₐ - ₜ', r'$\\mathbf{k} - \\mathbf{G}$'),
        (r'ₐ - ₑ', r'$\\mathbf{k} - \\mathbf{G}$'),
        (r'ₐ', r'$\\mathbf{k}$'),
        (r'ₜ\'', r'$\\mathbf{G}\'$'),
        (r'ₜ', r'$\\mathbf{G}$'),
        (r'ₓ', r'$\\mathbf{r}$'),
        (r'ₑ → 0', r'$V_{\\mathbf{G}} \\to 0$'),
        (r'ₑ', r'$\\mathbf{R}$'),
        (r'∑_\{ₜ\'\}', r'$\\sum_{\\mathbf{G}\'}$'),
        (r'∑', r'$\\sum$'),
        (r'\(λ_\{', r'($\\lambda_{'),
        (r'\(λ', r'($\\lambda$'),
        (r'(\s)λ(\s)', r'\1$\\lambda$\2'),
    ]

    for old, new in replacements:
        text = re.sub(old, new, text)

    # Clean up empty or nested dollar signs
    text = re.sub(r'\$\s*\$', '', text)
    
    return text.strip()

def process_shard(shard_path: str) -> bool:
    with open(shard_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error reading {shard_path}: {e}")
            return False

    modified = False
    for f_id, formula in data.items():
        if not isinstance(formula, dict):
            continue
        
        for field in ["conceptual_definition", "interpretation", "symmetry_origin", "limits_and_boundary"]:
            if field in formula and isinstance(formula[field], str):
                orig = formula[field]
                cleaned = fix_corrupted_text(orig)
                if cleaned != orig:
                    formula[field] = cleaned
                    modified = True

        if "semantic_variables" in formula and isinstance(formula["semantic_variables"], dict):
            for v_key, v_info in formula["semantic_variables"].items():
                if isinstance(v_info, dict) and "description" in v_info and isinstance(v_info["description"], str):
                    orig_desc = v_info["description"]
                    cleaned_desc = fix_corrupted_text(orig_desc)
                    if cleaned_desc != orig_desc:
                        v_info["description"] = cleaned_desc
                        modified = True

    if modified:
        with open(shard_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    return False

def main():
    shards = glob.glob(os.path.join(SHARD_DIR, "*/*.json"))
    shards.extend(glob.glob(os.path.join(SHARD_DIR, "*.json")))
    print(f"Processing {len(shards)} shards...")

    updated_count = 0
    for shard in shards:
        if process_shard(shard):
            updated_count += 1

    print(f"Done! Updated {updated_count} shard files containing corrupted expressions.")

if __name__ == "__main__":
    main()
