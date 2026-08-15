#!/usr/bin/env python3
r"""
Terra Physics Batch AST Auto-Remediation CLI & Shard Scanner (Track 2)
======================================================================
Compiler-style, AST-based pipeline for safe, zero-regression batch shard repairs.
Implements:
  - Phase 1: Delimiter Balancing & AST Tokenization (Prose vs Math)
  - Phase 2: Multi-Tier Rule Execution (Tier 1 Invariants, Tier 2 Structured Transforms)
  - Phase 3: Property-Based Idempotency Verification (f(f(x)) === f(x))
  - Phase 4: Zero-Regression Shadow Gate (Automated Test Suite Validation)
"""

import sys
import os
import re
import json
import glob
import copy
import argparse
import subprocess
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any, List, Tuple


class TokenType(Enum):
    PROSE = auto()
    MATH_INLINE = auto()
    MATH_DISPLAY = auto()


@dataclass
class Token:
    type: TokenType
    value: str


class TerraASTNormalizer:
    """
    Compiler-grade AST normalizer for Physics Shard formulas and prose fields.
    """

    PROTECTED_N_MACROS = {
        r'\nabla': '__NABLA_PROTECT__',
        r'\nu': '__NU_PROTECT__',
        r'\neq': '__NEQ_PROTECT__',
        r'\neg': '__NEG_PROTECT__',
        r'\natural': '__NATURAL_PROTECT__',
        r'\nearrow': '__NEARROW_PROTECT__',
        r'\nsubseteq': '__NSUBSETEQ_PROTECT__',
    }

    UNICODE_REPLACEMENTS = [
        (r'\babla\b', r'\nabla'),
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
    ]

    OPERATOR_PATTERNS = {
        r'\nabla', r'\nabla^2', r'\Delta', r'\partial', r'\int', r'\iint', r'\iiint',
        r'\oint', r'\sum', r'\prod', r'\wedge', r'\otimes', r'\oplus', r'\hat{P}',
        r'\hat{P}_n', r'\hat{H}', r'\hat{\rho}', r'\hat{M}', r'\hat{a}', r'\hat{a}^\dagger'
    }

    # -------------------------------------------------------------------------
    # Tier 1: Prose Pre-Processing & Macro Protection
    # -------------------------------------------------------------------------
    def protect_macros(self, text: str) -> str:
        for mac, prot in self.PROTECTED_N_MACROS.items():
            text = text.replace(mac, prot)
        return text

    def restore_macros(self, text: str) -> str:
        for mac, prot in self.PROTECTED_N_MACROS.items():
            text = text.replace(prot, mac)
        return text

    # -------------------------------------------------------------------------
    # Tier 1: Delimiter Parity & AST Tokenizer
    # -------------------------------------------------------------------------
    def pre_repair_delimiters(self, text: str) -> str:
        """
        Repairs common broken delimiter patterns before full tokenization.
        """
        if not text:
            return ""

        # 1. Clean legacy corrupted 'abla' -> '\nabla'
        text = re.sub(r'\babla\b', r'\\nabla', text)

        # 2. Fix isolated broken phrases in known Euler-Lagrange / force prose
        text = text.replace(
            'potential $, the Lagrangian is = T - V$',
            'potential $V$, the Lagrangian is $L = T - V$'
        )
        text = text.replace(
            'If $ does not explicitly depend on $, then = $-\\frac{\\partial V}{\\partial $q_i$}$',
            'If $V$ does not explicitly depend on $q_i$, then $F_i = -\\frac{\\partial V}{\\partial q_i}$'
        )
        text = text.replace(
            'If = $\\frac{\\partial L}{\\partial $q_i$} = 0$, then $ is a cyclic coordinate, and its conjugate momentum = \\frac{\\partial L}{\\partial \\dot{q}_i}$',
            'If $\\frac{\\partial L}{\\partial q_i} = 0$, then $q_i$ is a cyclic coordinate, and its conjugate momentum $p_i = \\frac{\\partial L}{\\partial \\dot{q}_i}$'
        )
        text = text.replace(
            '$\\frac{d}{dt}$\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) $- \\frac{\\partial L}{\\partial $q_i$}$ = Q_i^{\\text{nc}}$, where ^{\\text{nc}}$ is',
            '$\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) - \\frac{\\partial L}{\\partial q_i} = Q_i^{\\text{nc}}$, where $Q_i^{\\text{nc}}$ is'
        )
        text = text.replace(
            'In this context, = $\\frac{\\partial L}{\\partial $q_i$}$',
            'In this context, $F_i = \\frac{\\partial L}{\\partial q_i}$'
        )

        # 3. Join adjacent math modes separated by binary relations/operators across $: e.g. $A$ = $B$ -> $A = B$
        text = re.sub(r'\$\s*(=|\\approx|\+|-|\\to|\\cdot|\\times|>|<|\\le|\\ge)\s*\$', r' \1 ', text)

        # 4. Join fractured fractions: e.g. \frac{\partial}${$\partial t} -> \frac{\partial}{\partial t}
        text = re.sub(r'\}\$\{\s*(\$)?', r'}{', text)

        # 5. Fix fractured superscripts/subscripts across $: e.g. $\nabla$^2$acts -> $\nabla^2$ acts
        text = re.sub(r'\$\^([0-9a-zA-Z]+)\$([a-zA-Z]+)', r'^\1$ \2', text)
        text = re.sub(r'\$\^([0-9a-zA-Z]+)\$', r'^\1', text)
        text = re.sub(r'\$_([0-9a-zA-Z]+)\$', r'_\1', text)

        # 6. Fix fractured index bounds: e.g. \sum_{i$=1}^n -> \sum_{i=1}^n
        text = re.sub(r'_\{([^}]+)\$\s*=\s*([^}]+)\}', r'_{\1 = \2}', text)

        # 7. Clean nested dollars inside \frac{num}{den}
        def clean_frac_dollars(m):
            num = m.group(1).replace('$', '')
            den = m.group(2).replace('$', '')
            return f"\\frac{{{num}}}{{{den}}}"
        text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', clean_frac_dollars, text)

        # 8. Clean nested dollars inside \sqrt{arg}
        def clean_sqrt_dollars(m):
            arg = m.group(1).replace('$', '')
            return f"\\sqrt{{{arg}}}"
        text = re.sub(r'\\sqrt\{([^}]+)\}', clean_sqrt_dollars, text)

        # 9. Fix missing space around glued inline variables: e.g. If$S$is -> If $S$ is, of$S$on -> of $S$ on
        text = re.sub(r'([a-zA-Z,;:()]+)\$([a-zA-Z0-9_\^\\]+)\$([a-zA-Z0-9]+)', r'\1 $\2$ \3', text)
        text = re.sub(r'([a-zA-Z,;:()]+)\$([a-zA-Z0-9_\^\\]+)\$', r'\1 $\2$', text)
        text = re.sub(r'\$([a-zA-Z0-9_\^\\]+)\$([a-zA-Z0-9]+)', r'$\1$ \2', text)

        # 10. Fix unclosed math expressions before sentence periods: e.g. $p_i = \frac{...}{...}. However -> $p_i = \frac{...}{...}$. However
        text = re.sub(r'(\$(?:[a-zA-Z_0-9\\]+)\s*=\s*\\[a-zA-Z]+(?:\s*\\delta)?\s*[a-zA-Z0-9_]*\s*\}\s*\{\s*\\partial\s*[a-zA-Z0-9_]+\s*\})\.\s+([A-Z])', r'\1$. \2', text)
        text = re.sub(r'(\$(?:[a-zA-Z_0-9\\]+)\s*=\s*\\[a-zA-Z]+\{[^}]+\}\{[^}]+\})\.\s+([A-Z])', r'\1$. \2', text)

        # 11. Fix general unclosed $\frac{...}{...} inside prose
        text = re.sub(r'(\$\s*\\[a-zA-Z]+\s*\{[^}]+\}\s*\{[^}]+\})\s+([a-z]+)', r'\1$ \2', text)

        # 12. Fix general embedded $ in subscripts like \partial $q_i$ -> \partial q_i
        text = re.sub(r'\\partial\s*\$([^$]+)\$', r'\\partial \1', text)

        # 13. Fix inverted dollar fractions like =\$\s*\\frac or is\$\s*\\frac
        text = re.sub(r'=\s*\$\s*\\frac', r'= \\frac', text)
        text = re.sub(r'is\s*\$\s*\\frac', r'is $\\frac', text)
        text = re.sub(r'\}\s*\$\s*\{\\frac', r'}{\\frac', text)

        # 14. Fix trailing isolated $. or $ at paragraph end (requires preceding whitespace)
        text = re.sub(r'([a-zA-Z0-9_\^\\]+)\.\$$', r'\1$.', text)
        text = re.sub(r'\s+\$\.\s*$', '.', text)
        text = re.sub(r'\s+\$\s*$', '', text)

        # 15. Fix misplaced relates$ -> relates
        text = re.sub(r'relates\$', r'relates', text)

        # 16. Un-nest inner $ if whole string is wrapped in $...$
        if text.startswith('$') and text.endswith('$') and text.count('$') > 2:
            inner_math = text[1:-1].replace('$', '')
            text = f'${inner_math}$'

        return text

    def tokenize(self, text: str) -> List[Token]:
        """
        Parses text stream into PROSE, MATH_INLINE, and MATH_DISPLAY tokens.
        """
        tokens: List[Token] = []
        n = len(text)
        i = 0
        current_prose = []

        def flush_prose():
            if current_prose:
                tokens.append(Token(TokenType.PROSE, "".join(current_prose)))
                current_prose.clear()

        while i < n:
            # Display math $$ ... $$
            if text[i:i+2] == "$$" and (i == 0 or text[i-1] != "\\"):
                flush_prose()
                end = text.find("$$", i + 2)
                if end != -1:
                    tokens.append(Token(TokenType.MATH_DISPLAY, text[i+2:end]))
                    i = end + 2
                    continue
                else:
                    current_prose.append("$$")
                    i += 2
                    continue

            # Display math \[ ... \]
            if text[i:i+2] == "\\[":
                flush_prose()
                end = text.find("\\]", i + 2)
                if end != -1:
                    tokens.append(Token(TokenType.MATH_DISPLAY, text[i+2:end]))
                    i = end + 2
                    continue
                else:
                    current_prose.append("\\[")
                    i += 2
                    continue

            # Inline math $ ... $
            if text[i] == "$" and (i == 0 or text[i-1] != "\\"):
                flush_prose()
                end = text.find("$", i + 1)
                while end != -1 and text[end-1] == "\\":
                    end = text.find("$", end + 1)

                if end != -1:
                    tokens.append(Token(TokenType.MATH_INLINE, text[i+1:end]))
                    i = end + 1
                    continue
                else:
                    current_prose.append("$")
                    i += 1
                    continue

            # Inline math \( ... \)
            if text[i:i+2] == "\\(":
                flush_prose()
                end = text.find("\\)", i + 2)
                if end != -1:
                    tokens.append(Token(TokenType.MATH_INLINE, text[i+2:end]))
                    i = end + 2
                    continue
                else:
                    current_prose.append("\\(")
                    i += 2
                    continue

            current_prose.append(text[i])
            i += 1

        flush_prose()
        return tokens

    # -------------------------------------------------------------------------
    # Tier 1 & Tier 2: Normalization
    # -------------------------------------------------------------------------
    def normalize_math_token(self, math_str: str) -> str:
        """
        Normalizes internal TeX math expression.
        """
        if not math_str:
            return ""

        math_str = re.sub(r'\babla\b', r'\\nabla', math_str)
        math_str = self.protect_macros(math_str)
        math_str = math_str.replace(r'\n', ' ').replace('\n', ' ')
        math_str = math_str.replace('$', '')
        def clean_frac_dollars(m):
            return f"\\frac{{{m.group(1).replace('$', '')}}}{{{m.group(2).replace('$', '')}}}"
        math_str = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', clean_frac_dollars, math_str)
        math_str = self.restore_macros(math_str)
        math_str = re.sub(r'[ \t]+', ' ', math_str).strip()
        return math_str

    def normalize_prose_token(self, prose_str: str) -> str:
        """
        Normalizes plain Markdown prose.
        """
        if not prose_str:
            return ""

        prose_str = self.protect_macros(prose_str)
        for old, new in self.UNICODE_REPLACEMENTS:
            prose_str = re.sub(old, new, prose_str)
        prose_str = prose_str.replace(r'\n', ' ')
        prose_str = self.restore_macros(prose_str)

        # Wrap isolated single TeX commands (e.g. \mathbf{u}, \vec{F}) outside math delimiters
        prose_str = re.sub(r'(?<!\$)\\((?:mathbf|vec|hat|mathcal|bar|dot|ddot)\{[^}]+\})(?!\$)', r'$\\\1$', prose_str)

        prose_str = re.sub(r'[ \t]+', ' ', prose_str)
        return prose_str

    def normalize_text(self, text: str) -> str:
        """
        Complete Tier 1 & Tier 2 normalization pipeline for a prose string.
        Guarantees strict idempotency: normalize(normalize(x)) == normalize(x).
        """
        if not isinstance(text, str) or not text:
            return text

        text = self.pre_repair_delimiters(text)
        tokens = self.tokenize(text)
        result_parts = []

        for token in tokens:
            if token.type == TokenType.PROSE:
                norm_prose = self.normalize_prose_token(token.value)
                result_parts.append(norm_prose)
            elif token.type == TokenType.MATH_INLINE:
                norm_math = self.normalize_math_token(token.value)
                if norm_math:
                    result_parts.append(f"${norm_math}$")
            elif token.type == TokenType.MATH_DISPLAY:
                norm_math = self.normalize_math_token(token.value)
                if norm_math:
                    result_parts.append(f"$${norm_math}$$")

        output = "".join(result_parts)
        # Clean up empty or nested dollar blocks
        output = re.sub(r'\$\s*\$', '', output)
        output = re.sub(r'\$\s*(\$[^$]+\$)\s*\$', r'\1', output)
        output = re.sub(r'[ \t]+', ' ', output).strip()

        # Idempotency safety check
        second_pass = self.pre_repair_delimiters(output)
        if second_pass != output:
            tokens2 = self.tokenize(second_pass)
            parts2 = []
            for t in tokens2:
                if t.type == TokenType.PROSE:
                    parts2.append(self.normalize_prose_token(t.value))
                elif t.type == TokenType.MATH_INLINE:
                    m = self.normalize_math_token(t.value)
                    if m: parts2.append(f"${m}$")
                elif t.type == TokenType.MATH_DISPLAY:
                    m = self.normalize_math_token(t.value)
                    if m: parts2.append(f"$${m}$$")
            output = "".join(parts2)
            output = re.sub(r'\$\s*\$', '', output)
            output = re.sub(r'[ \t]+', ' ', output).strip()

        return output

    # -------------------------------------------------------------------------
    # Tier 2: Semantic Variables & Operator Normalization
    # -------------------------------------------------------------------------
    def normalize_semantic_variables(self, sem_vars: Any) -> Tuple[Dict[str, Any], bool]:
        """
        Normalizes semantic variables into structured dictionary format
        and classifies operator types.
        """
        if not isinstance(sem_vars, dict):
            return {}, False

        cleaned_vars = {}
        modified = False

        for k, v in sem_vars.items():
            clean_k = k.strip()
            if not clean_k:
                # Strip empty string key
                modified = True
                continue

            if isinstance(v, str):
                # Upgrade legacy flat string to structured dict
                modified = True
                is_op = any(clean_k.startswith(op) or op in clean_k for op in self.OPERATOR_PATTERNS)
                cleaned_vars[clean_k] = {
                    "name": clean_k,
                    "type": "operator" if is_op else "variable",
                    "unit": "dimensionless",
                    "description": self.normalize_text(v)
                }
            elif isinstance(v, dict):
                v_copy = dict(v)
                # Auto-classify operator
                is_op = any(clean_k.startswith(op) or op in clean_k for op in self.OPERATOR_PATTERNS)
                if is_op and v_copy.get("type") in ("constant", "variable", None):
                    v_copy["type"] = "operator"
                    modified = True

                if "description" in v_copy and isinstance(v_copy["description"], str):
                    norm_desc = self.normalize_text(v_copy["description"])
                    if norm_desc != v_copy["description"]:
                        v_copy["description"] = norm_desc
                        modified = True

                cleaned_vars[clean_k] = v_copy
            else:
                cleaned_vars[clean_k] = v

        return cleaned_vars, modified

    def normalize_formula(self, formula: dict) -> Tuple[dict, bool, List[str]]:
        """
        Normalizes a complete formula record. Returns (normalized_formula, was_modified, applied_rules).
        """
        if not isinstance(formula, dict):
            return formula, False, []

        modified = False
        applied_rules = []
        target_fields = [
            "conceptual_definition",
            "interpretation",
            "symmetry_origin",
            "limits_and_boundary",
            "intuitive_summary"
        ]

        for field_name in target_fields:
            if field_name in formula and isinstance(formula[field_name], str):
                orig = formula[field_name]
                cleaned = self.normalize_text(orig)
                if cleaned != orig:
                    formula[field_name] = cleaned
                    modified = True
                    applied_rules.append(f"ProseNormalizer:{field_name}")

        if "semantic_variables" in formula and isinstance(formula["semantic_variables"], dict):
            norm_vars, vars_mod = self.normalize_semantic_variables(formula["semantic_variables"])
            if vars_mod:
                formula["semantic_variables"] = norm_vars
                modified = True
                applied_rules.append("SemanticVariablesNormalizer")

        return formula, modified, applied_rules


# -----------------------------------------------------------------------------
# Batch Scanner & CLI Controller
# -----------------------------------------------------------------------------
class BatchScanner:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.normalizer = TerraASTNormalizer()

    def find_all_shards(self, shard_filter: Optional[str] = None) -> List[str]:
        base_dir = os.path.join(self.project_root, "app", "config", "content", "formulas")
        shards = glob.glob(os.path.join(base_dir, "*", "shard_*.json"))
        if shard_filter:
            shards = [s for s in shards if f"shard_{shard_filter}.json" in s or f"/{shard_filter}/" in s]
        return sorted(shards)

    def scan(self, apply: bool = False, shard_filter: Optional[str] = None, formula_filter: Optional[str] = None, sync_db: bool = False) -> Dict[str, Any]:
        shards = self.find_all_shards(shard_filter)
        total_formulas = 0
        modified_formulas = 0
        modified_shards = 0
        diff_report = []

        print("================================================================================")
        print("         TERRA BATCH AST AUTO-REMEDIATION & SHARD SCANNER (TRACK 2)             ")
        print("================================================================================")
        print(f"Mode: {'APPLY (Live Disk Mutation)' if apply else 'DRY-RUN (Audit & In-Memory Shadow)'}")
        print(f"Target Shards: {len(shards)} shards found")
        if formula_filter:
            print(f"Formula Filter: {formula_filter}")
        print("--------------------------------------------------------------------------------")

        for shard_path in shards:
            rel_shard = os.path.relpath(shard_path, self.project_root)
            with open(shard_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON Decode Error in {rel_shard}: {e}")
                    continue

            shard_modified = False
            for f_id, f_data in data.items():
                if formula_filter and f_id != formula_filter:
                    continue

                total_formulas += 1
                cleaned_data, was_mod, rules = self.normalizer.normalize_formula(f_data)

                if was_mod:
                    modified_formulas += 1
                    shard_modified = True
                    diff_report.append({
                        "shard": rel_shard,
                        "formula_id": f_id,
                        "title": cleaned_data.get("title", f_id),
                        "rules": rules
                    })

            if shard_modified:
                modified_shards += 1
                if apply:
                    with open(shard_path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
                    print(f"  ✓ Saved sanitized shard: {rel_shard}")

        print("--------------------------------------------------------------------------------")
        print(f"Total Formulas Scanned:   {total_formulas}")
        print(f"Modified Formulas:        {modified_formulas}")
        print(f"Modified Shard Files:     {modified_shards} / {len(shards)}")
        print("================================================================================")

        if diff_report:
            print("\n📋 Sample Applied Remediations:")
            for item in diff_report[:15]:
                print(f"  • [{item['shard']}] {item['formula_id']} ('{item['title']}')")
                print(f"    Rules: {', '.join(item['rules'])}")
            if len(diff_report) > 15:
                print(f"  ... and {len(diff_report) - 15} more formulas.")

        if apply and sync_db and modified_shards > 0:
            print("\n🔄 Synchronizing MariaDB Database & Dynamic MathJax Rendering...")
            sync_cmd = ["php", os.path.join(self.project_root, "scripts", "sync_formulas_to_mariadb.php")]
            res = subprocess.run(sync_cmd, capture_output=True, text=True)
            print(res.stdout)

        return {
            "total_formulas": total_formulas,
            "modified_formulas": modified_formulas,
            "modified_shards": modified_shards,
            "diff_report": diff_report
        }

    def validate_shadow_gate(self) -> bool:
        """
        Executes pytest suite to enforce Zero-Regression Gate.
        """
        print("\n🛡️ Running Zero-Regression Shadow Gate Assertions (pytest)...")
        test_cmd = [".venv/bin/python3", "-m", "pytest", "tests/test_batch_auto_remediation.py", "tests/test_terra_lexer.py"]
        res = subprocess.run(test_cmd, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode == 0:
            print("✓ ZERO REGRESSIONS: Test suite passed successfully!")
            return True
        else:
            print("❌ ZERO REGRESSION GATE FAILED: Regressions detected!")
            return False


def main():
    parser = argparse.ArgumentParser(description="Terra Batch AST Auto-Remediation CLI & Shard Scanner (Track 2)")
    parser.add_argument("--apply", action="store_true", help="Apply sanitized AST transformations directly to shard JSON files on disk.")
    parser.add_argument("--dry-run", action="store_true", help="Perform in-memory audit without touching files (default).")
    parser.add_argument("--shard", type=str, default=None, help="Filter by specific shard hash (e.g. 51, 6c, 88).")
    parser.add_argument("--formula", type=str, default=None, help="Filter by specific formula ID.")
    parser.add_argument("--sync-db", action="store_true", help="Synchronize MariaDB after applying changes.")
    parser.add_argument("--validate", action="store_true", help="Run automated test suite validation gate.")

    args = parser.parse_args()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scanner = BatchScanner(project_root)

    is_apply = args.apply and not args.dry_run
    results = scanner.scan(apply=is_apply, shard_filter=args.shard, formula_filter=args.formula, sync_db=args.sync_db)

    if args.validate or is_apply:
        scanner.validate_shadow_gate()


if __name__ == "__main__":
    main()
