import json
import glob
import os
import re

SHARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "config", "content", "formulas")

def repair_text_field(text: str) -> str:
    if not text or not isinstance(text, str):
        return text

    # 1. Known macro corruption patterns using raw strings
    text = re.sub(r"\\sqrt\s*\$\s*\{", r"\\sqrt{", text)
    text = re.sub(r"\\frac\s*\$\s*\{", r"\\frac{", text)
    text = re.sub(r"\\sqrt\$\{", r"\\sqrt{", text)
    text = re.sub(r"\\frac\$\{", r"\\frac{", text)
    text = re.sub(r"\$\s*\\mu\$\s*u\$?", r"\\mu \\nu", text)
    text = re.sub(r"\$\s*\\mu\$\s*\\nu", r"\\mu \\nu", text)
    text = re.sub(r"g_\{\$\s*\\mu\$\s*u\}", r"g_{\\mu \\nu}", text)
    text = re.sub(r"G_\{\$\s*\\mu\$\s*u\}", r"G_{\\mu \\nu}", text)
    text = re.sub(r"T_\{\$\s*\\mu\$\s*u\}", r"T_{\\mu \\nu}", text)
    text = re.sub(r"\\to\x27", r"\\to", text)
    text = re.sub(r"abla_", r"\\nabla_", text)
    text = re.sub(r"A_\$\\al\$", r"$A_\\alpha$", text)
    text = re.sub(r"A_\$\\alpha\$", r"$A_\\alpha$", text)
    text = re.sub(r"\\b\{([^\}]+)\}", r"\\mathbf{\1}", text)
    text = re.sub(r"\\b\$", r"$", text)
    text = re.sub(r"(\\frac\{[^{}]+\}\{[^{}]+\})\$([a-zA-Z0-9_\^]+)", r"\1 \2$", text)


    # 2. Fix broken subscript/superscript dollar signs: e.g. A_$\mu$ -> A_\mu, g_{$\mu$} -> g_{\mu}
    text = re.sub(r"([a-zA-Z0-9_\{\}]+)_\$\s*\\([a-zA-Z]+)\s*\$", r"\1_\\\2", text)
    text = re.sub(r"([a-zA-Z0-9_\{\}]+)_\$\s*([a-zA-Z0-9_]+)\s*\$", r"\1_\2", text)
    text = re.sub(r"\\sum\s*\$\s*\\mu", r"\\sum \\mu", text)

    # 3. Fix misplaced trailing dollars only when followed by differential or math variables
    text = re.sub(r"\$(\-?[a-zA-Z0-9]+)\$\s*(d[VStxyzNp]|\\to|\\cdot)", r"$\1 \2$", text)

    # 4. Fix period/bracket inside/outside math mode at end of sentence
    text = re.sub(r"\)\.\$", r"$).", text)
    text = re.sub(r"\.\$", r"$.", text)

    # 5. Remove nested $ inside TeX braces: e.g. \frac{$\partial \psi$}{...} -> \frac{\partial \psi}{...}
    text = re.sub(r"\\frac\{\$([^\$]+)\$\}", r"\\frac{\1}", text)
    text = re.sub(r"\\frac\$\{\$\\sum\$", r"\\frac{\\sum", text)

    # 6. Handle unescaped TeX macros outside $...$
    parts = re.split(r"(\$[^\$]+\$)", text)
    new_parts = []
    tex_macro_pattern = re.compile(r"(\\[a-zA-Z]+(?:\{[^\}]*\}|_[a-zA-Z0-9_\{\}\\]+|\^[a-zA-Z0-9_\{\}\\]+)*)")

    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            clean = re.sub(r"(?<!\\)\$\$", "$", part)
            new_parts.append(clean)
        else:
            if "\\" in part:
                def wrap_tex(m):
                    macro = m.group(0).strip()
                    return f"${macro}$"
                fixed = tex_macro_pattern.sub(wrap_tex, part)
                new_parts.append(fixed)
            else:
                new_parts.append(part)

    text = "".join(new_parts)

    # 7. Merge adjacent math blocks: $a$ $b$ -> $a b$
    text = re.sub(r"\$\s*\$", " ", text)
    text = re.sub(r"\$\s*([^\$]+)\s*\$\s*\$\s*([^\$]+)\s*\$", r"$\1 \2$", text)

    # 8. Final unclosed dollar check
    if text.count("$") % 2 != 0:
        if text.endswith("."):
            text = text[:-1] + "$."
        else:
            text += "$"

    return text

def run():
    shard_files = glob.glob(os.path.join(SHARDS_DIR, "**", "*.json"), recursive=True) + glob.glob(os.path.join(SHARDS_DIR, "*.json"))
    total_repaired = 0
    shards_modified = 0

    for fpath in shard_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, dict):
                continue

            shard_changed = False
            for fid, fval in data.items():
                if not isinstance(fval, dict):
                    continue

                for field in ["conceptual_definition", "interpretation", "limits_and_boundary", "symmetry_origin", "intuitive_summary"]:
                    orig = fval.get(field, "")
                    if not orig or not isinstance(orig, str):
                        continue
                    repaired = repair_text_field(orig)
                    if repaired != orig:
                        fval[field] = repaired
                        shard_changed = True
                        total_repaired += 1

            if shard_changed:
                shards_modified += 1
                with open(fpath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Error processing {fpath}: {e}")

    print(f"Repair Complete: Modified {shards_modified} shards, repaired {total_repaired} fields.")

if __name__ == "__main__":
    run()
