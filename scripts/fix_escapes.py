import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYLOAD_PATH = os.path.join(PROJECT_ROOT, "subfiles/formula_payload.json")

with open(PAYLOAD_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix LaTeX characters that JSON parser interprets as invalid escapes
# Replace single-backslash commands with double-backslash
replacements = {
    r"\mu": r"\\mu",
    r"\nu": r"\\nu",
    r"\lambda": r"\\lambda",
    r"\Gamma": r"\\Gamma",
    r"\partial": r"\\partial",
    r"\mathbf": r"\\mathbf",
    r"\phi": r"\\phi",
    r"\mathcal": r"\\mathcal",
    r"\epsilon": r"\\epsilon",
    r"\alpha": r"\\alpha",
    r"\pi": r"\\pi",
    r"\psi": r"\\psi",
    r"\bar": r"\\bar",
    r"\ddot": r"\\ddot",
    r"\dot": r"\\dot",
    r"\Omega": r"\\Omega",
    r"\Lambda": r"\\Lambda",
    r"\theta": r"\\theta",
    r"\ell": r"\\ell",
    r"\times": r"\\times"
}

# We need to make sure we don't double-escape if they are already double-escaped.
# So first normalize all double-escapes to single escapes, then apply the double-escape to all of them.
for key, val in replacements.items():
    # Convert \\command to \command
    content = content.replace(val, key)
    # Convert \command to \\command
    content = content.replace(key, val)

# Verify if it is valid JSON now
try:
    data = json.loads(content)
    print("✓ JSON is now valid!")
    with open(PAYLOAD_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
except Exception as e:
    print(f"⚠️ Validation failed: {e}")
