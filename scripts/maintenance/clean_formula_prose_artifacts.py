#!/usr/bin/env python3
r"""
scripts/maintenance/clean_formula_prose_artifacts.py

Deterministic cleanup of mechanical LLM boilerplate ("interpreted as follows:"),
raw Markdown bold (**...**), and raw Markdown bullet lists (\n* ...) across all
256 formula shards (app/config/content/formulas/*/shard_*.json).

Guarantees:
  - Protects all display and inline math blocks ($...$, $$...$$, \(...\), \[...\])
    via placeholder masking before text transformations.
  - Validates every modified string with validate_narrative_delimiters().
  - Synchronizes app/config/formulas_hash_registry.json and MariaDB (if online).
"""

import argparse
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from lib.math.delimiters import validate_narrative_delimiters

SHARDS_GLOB = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas", "*", "shard_*.json")
HASH_REGISTRY_PATH = os.path.join(PROJECT_ROOT, "app", "config", "formulas_hash_registry.json")

PROSE_FIELDS = (
    "interpretation",
    "conceptual_definition",
    "intuitive_summary",
    "symmetry_origin",
    "limits_and_boundary",
    "description",
)

# Regex to tokenize math blocks so we never alter anything inside math mode
MATH_TOKEN_RE = re.compile(
    r"(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\\\([\s\S]*?\\\)|(?<!\\)\$(?:[^$\\]|\\.)+?\$)"
)

# 1. Leading or mid-text "interpreted as follows:" boilerplate
BOILERPLATE_CLAUSE_RE = re.compile(
    r"(?:(?:^|(?<=[.!?]\s))(?:"
    r"(?:Mathematically|Physically|Specifically|Here|In\s+this\s+context),\s+)?"
    r"(?:the|this|it)\s+(?:(?:\w+\s+){0,3})?"
    r"(?:formula|equation|relation|expression|identity|statement|term|law|condition|form)?\s*"
    r"(?:__MATH_\d+__\s*)?"
    r"(?:is|can\s+be|may\s+be)\s+interpreted\s+as\s+follows\s*:\s*)"
    r"|(?:(?:,\s*|\s+)(?:which\s+)?(?:is|can\s+be)\s+interpreted\s+as\s+follows\s*:\s*)"
    r"|(?:interpreted\s+as\s+follows\s*:\s*)",
    re.IGNORECASE,
)


def capitalize_first_alpha(s: str) -> str:
    """Capitalizes the first alphabetical character if the string starts with lowercase prose."""
    s = s.lstrip()
    if not s:
        return s
    if s[0].islower():
        return s[0].upper() + s[1:]
    return s


def clean_prose_text(text: str) -> str:
    """Cleans boilerplate, markdown bold, and markdown bullets while preserving math blocks."""
    if not text or not isinstance(text, str):
        return text

    original = text

    # Step 0: Convert literal '\n' before bullets into actual newlines if any remain
    s = re.sub(r"\\n(?=\s*[\*-]\s+)", "\n", original)

    # Step 1: Mask all math blocks with placeholders __MATH_i__
    math_blocks = []

    def _mask_math(m):
        idx = len(math_blocks)
        math_blocks.append(m.group(0))
        return f"__MATH_{idx}__"

    masked = MATH_TOKEN_RE.sub(_mask_math, s)

    has_boilerplate = bool(re.search(r"interpreted\s+as\s+follows", masked, re.IGNORECASE))
    has_bold = "**" in masked
    has_bullets = bool(re.search(r"(?:^|\n)\s*[\*-]\s+", masked))

    if not (has_boilerplate or has_bold or has_bullets):
        return original

    # Step 2: Strip raw Markdown bold **...** (and leftover **)
    if has_bold:
        masked = re.sub(r"\*\*([^*\n]+)\*\*", r"\1", masked)
        masked = masked.replace("**", "")

    # Step 3: Remove "interpreted as follows:" boilerplate clauses
    def _replace_boilerplate(m):
        full_match = m.group(0)
        start = m.start()
        # If matched mid-sentence after a comma or space without sentence boundary, end sentence cleanly
        if start > 0 and masked[start - 1] not in ".!?\n":
            return ". "
        return ""

    if re.search(r"interpreted\s+as\s+follows", masked, re.IGNORECASE):
        masked = BOILERPLATE_CLAUSE_RE.sub(_replace_boilerplate, masked)
        # Clean up any double periods or leading punctuation
        masked = re.sub(r"\.\s*\.", ".", masked)
        masked = re.sub(r"^\s*[.,;:]\s*", "", masked)

    # Step 4: Convert raw Markdown bullet lists (\n* ... or ^* ...) into continuous prose sentences
    if re.search(r"(?:^|\n)\s*[\*-]\s+", masked):
        raw_lines = masked.split("\n")
        cleaned_Parts = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped:
                continue
            bullet_m = re.match(r"^[\*-]\s+(.*)$", stripped)
            if bullet_m:
                item = bullet_m.group(1).strip()
                # Convert "$X$: Represents..." into "$X$ represents..." or "$X$: The..." into "$X$ denotes the..."
                colon_m = re.match(r"^((?:__MATH_\d+__|[^:]{1,40})):\s+([A-Z])(.*)$", item)
                if colon_m:
                    subj, first_char, rest = colon_m.group(1).strip(), colon_m.group(2), colon_m.group(3)
                    lower_word_m = re.match(r"^([a-zA-Z]+)", first_char + rest)
                    first_word = lower_word_m.group(1).lower() if lower_word_m else ""
                    if first_word in (
                        "represents", "denotes", "is", "are", "measures", "quantifies",
                        "describes", "defines", "indicates", "specifies", "gives", "accounts",
                        "captures", "characterizes", "governs", "relates", "expresses", "acts",
                    ):
                        item = f"{subj} {first_char.lower()}{rest}"
                    elif re.match(r"^__MATH_\d+__$", subj) and first_word in ("the", "a", "an"):
                        item = f"{subj} denotes {first_char.lower()}{rest}"
                if item and item[-1] not in ".!?":
                    item += "."
                cleaned_Parts.append(item)
            else:
                # Normal paragraph/intro line before or after bullets
                if stripped.endswith(":"):
                    stripped = stripped[:-1].rstrip() + "."
                elif stripped[-1] not in ".!?":
                    stripped += "."
                cleaned_Parts.append(stripped)
        masked = " ".join(cleaned_Parts)

    # Normalize multiple spaces / newlines into clean single spaces
    masked = re.sub(r"\s*\n+\s*", " ", masked)
    masked = re.sub(r" {2,}", " ", masked).strip()
    masked = capitalize_first_alpha(masked)

    # Step 5: Unmask math blocks
    def _unmask_math(m):
        idx = int(m.group(1))
        return math_blocks[idx]

    unmasked = re.sub(r"__MATH_(\d+)__", _unmask_math, masked)

    # Safety check: if delimiter validation fails on the new text but passed on original, revert!
    orig_errors = validate_narrative_delimiters(original)
    new_errors = validate_narrative_delimiters(unmasked)
    if len(new_errors) > len(orig_errors):
        return original

    return unmasked


def main():
    parser = argparse.ArgumentParser(description="Clean boilerplate and markdown artifacts in formula prose.")
    parser.add_argument("--dry-run", action="store_true", help="Scan and preview changes without modifying files.")
    args = parser.parse_args()

    shard_files = sorted(glob.glob(SHARDS_GLOB))
    modified_shards = 0
    modified_formulas = 0
    modified_fields = 0

    rem_interpreted = 0
    rem_bold = 0
    rem_bullet = 0
    sample_diffs = []

    for sf in shard_files:
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)

        shard_changed = False
        for fid, form in data.items():
            if not isinstance(form, dict):
                continue
            formula_changed = False
            for pf in PROSE_FIELDS:
                val = form.get(pf)
                if not val or not isinstance(val, str):
                    continue
                cleaned = clean_prose_text(val)
                if cleaned != val:
                    form[pf] = cleaned
                    formula_changed = True
                    shard_changed = True
                    modified_fields += 1
                    if len(sample_diffs) < 8:
                        sample_diffs.append((fid, pf, val[:160], cleaned[:160]))

                # Check if any artifacts remain after cleaning
                # Check outside math blocks for bold/bullets
                no_math = MATH_TOKEN_RE.sub(" ", cleaned)
                if re.search(r"interpreted\s+as\s+follows\s*:", no_math, re.IGNORECASE):
                    rem_interpreted += 1
                if re.search(r"\*\*[^*]+\*\*", no_math):
                    rem_bold += 1
                if re.search(r"(?:^|\n)\s*[\*-]\s+", no_math):
                    rem_bullet += 1

            if formula_changed:
                modified_formulas += 1

        if shard_changed:
            modified_shards += 1
            if not args.dry_run:
                with open(sf, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                    f.write("\n")

    print(f"Shards Modified:             {modified_shards} / {len(shard_files)}")
    print(f"Formulas Cleaned:            {modified_formulas}")
    print(f"Prose Fields Cleaned:        {modified_fields}")
    print(f"Remaining 'interpreted as':  {rem_interpreted}")
    print(f"Remaining '**bold**':        {rem_bold}")
    print(f"Remaining '\\n* ' bullets:    {rem_bullet}")

    if sample_diffs:
        print("\n--- Sample Cleaned Fields ---")
        for fid, pf, before, after in sample_diffs[:5]:
            print(f"[{fid}] ({pf})")
            print(f"  BEFORE: {before!r}")
            print(f"  AFTER : {after!r}")

    if not args.dry_run:
        # Synchronize MariaDB via PhysicsService if reachable, which also updates formulas_hash_registry.json
        php_sync = (
            "define('FLIGHT_SKIP_START', true); "
            "require 'app/config/bootstrap.php'; "
            "$res = Flight::physicsService()->syncFormulasToDatabase(true); "
            "echo json_encode($res);"
        )
        res = subprocess.run(["php", "-r", php_sync], capture_output=True, text=True, cwd=PROJECT_ROOT)
        if res.returncode == 0:
            print(f"MariaDB Sync Result:         {res.stdout.strip()}")
        else:
            print(f"MariaDB Sync Warning:        {res.stderr.strip()}")


if __name__ == "__main__":
    main()
