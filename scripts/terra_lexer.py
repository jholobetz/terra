r"""
Terra Physics Formula Lexer & AST Normalizer Module (Phase 1)
--------------------------------------------------------------
Implements a 2-Pass Hybrid State-Machine Lexer to isolate Markdown prose
from LaTeX math expressions and normalize TeX math ASTs with zero external dependencies.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
import re
import json
import os
import glob
import sys


class TokenType(Enum):
    PROSE = auto()
    MATH_INLINE = auto()
    MATH_DISPLAY = auto()


class TeXNodeType(Enum):
    MACRO = auto()
    GROUP = auto()
    OPERATOR = auto()
    CHARS = auto()
    TEXT_MACRO = auto()


@dataclass
class Token:
    type: TokenType
    value: str


@dataclass
class TeXNode:
    type: TeXNodeType
    value: str
    children: list['TeXNode'] = field(default_factory=list)
    args: list['TeXNode'] = field(default_factory=list)


class TerraLexer:
    """
    2-Pass Lexer and Normalizer for Terra Physics Formulas.
    """

    # Protected TeX commands starting with \n that must never be split by prose newlines
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

    def __init__(self):
        pass

    # -------------------------------------------------------------------------
    # PASS 1: Top-Level Tokenizer (Prose vs Math Isolation)
    # -------------------------------------------------------------------------
    def pass1_tokenize(self, text: str) -> list[Token]:
        r"""
        Scans text character-by-character to emit typed PROSE, MATH_INLINE,
        and MATH_DISPLAY tokens while properly handling backslash escapes (\$ vs $).
        """
        tokens: list[Token] = []
        n = len(text)
        i = 0
        current_prose = []

        def flush_prose():
            if current_prose:
                tokens.append(Token(TokenType.PROSE, "".join(current_prose)))
                current_prose.clear()

        while i < n:
            # 1. Handle Display Math $$ ... $$ or \[ ... \]
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

            # 2. Handle Inline Math $ ... $ or \( ... \)
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
    # PASS 2: TeX AST Math Normalizer
    # -------------------------------------------------------------------------
    def pass2_normalize_math(self, math_str: str) -> str:
        """
        Normalizes TeX math content inside an open math token:
        1. Strips inner nested '$' delimiters.
        2. Protects TeX commands starting with \\n (\\nabla, \\nu).
        3. Cleans misplaced '$' inside \\frac{...}.
        4. Normalizes extra internal whitespace.
        """
        if not math_str:
            return ""

        # 0. Fix legacy corrupted 'abla' -> '\nabla'
        math_str = re.sub(r'\babla\b', r'\\nabla', math_str)

        # 1. Protect \n TeX commands
        for mac, prot in self.PROTECTED_N_MACROS.items():
            math_str = math_str.replace(mac, prot)

        # 2. Convert literal escape \n inside math to space
        math_str = math_str.replace(r'\n', ' ').replace('\n', ' ')

        # 3. Strip inner nested '$' signs
        math_str = math_str.replace('$', '')

        # 4. Clean misplaced $ inside \frac{...}
        math_str = re.sub(r'\\frac\{([^}]*)\$([^}]*)\}\{([^}]*)\$([^}]*)\}', r'\\frac{\1\2}{\3\4}', math_str)

        # 5. Restore protected TeX macros
        for mac, prot in self.PROTECTED_N_MACROS.items():
            math_str = math_str.replace(prot, mac)

        # 6. Normalize multiple spaces
        math_str = re.sub(r'[ \t]+', ' ', math_str).strip()
        return math_str

    # -------------------------------------------------------------------------
    # Prose Normalizer
    # -------------------------------------------------------------------------
    def normalize_prose(self, prose_str: str) -> str:
        """
        Normalizes plain text prose:
        1. Protects TeX commands starting with \\n (\\nabla, \\nu).
        2. Converts literal \\n string escapes to space.
        3. Maps legacy pseudo-Unicode symbols (ₐ, ₜ, ₓ, abla -> \nabla).
        4. Restores protected TeX commands.
        5. Normalizes multiple spaces.
        """
        if not prose_str:
            return ""

        # 1. Protect TeX commands starting with \n
        for mac, prot in self.PROTECTED_N_MACROS.items():
            prose_str = prose_str.replace(mac, prot)

        # 2. Map pseudo-Unicode & legacy corrupted symbols (abla -> \nabla)
        for old, new in self.UNICODE_REPLACEMENTS:
            prose_str = re.sub(old, new, prose_str)

        # 3. Replace literal \n sequence with space
        prose_str = prose_str.replace(r'\n', ' ')

        # 4. Restore protected TeX commands
        for mac, prot in self.PROTECTED_N_MACROS.items():
            prose_str = prose_str.replace(prot, mac)

        # 5. Normalize spaces
        prose_str = re.sub(r'[ \t]+', ' ', prose_str)
        return prose_str

    # -------------------------------------------------------------------------
    # Master Normalization Function
    # -------------------------------------------------------------------------
    def normalize_text(self, text: str) -> str:
        """
        Runs Pass 1 and Pass 2 lexing & AST normalization over raw JSON string text.
        """
        if not isinstance(text, str) or not text:
            return text

        # Clean misplaced $ inside \frac{...}
        text = re.sub(r'\\frac\{([^}]*)\$([^}]*)\}\{([^}]*)\$([^}]*)\}', r'\\frac{\1\2}{\3\4}', text)

        # If a single math expression is wrapped in broken outer/inner $, un-nest inner $
        if text.startswith('$') and text.endswith('$') and text.count('$') > 2:
            inner_math = text[1:-1].replace('$', '')
            text = f'${inner_math}$'

        tokens = self.pass1_tokenize(text)
        result_parts = []

        for token in tokens:
            if token.type == TokenType.PROSE:
                norm_prose = self.normalize_prose(token.value)
                result_parts.append(norm_prose)
            elif token.type == TokenType.MATH_INLINE:
                norm_math = self.pass2_normalize_math(token.value)
                if norm_math:
                    result_parts.append(f"${norm_math}$")
            elif token.type == TokenType.MATH_DISPLAY:
                norm_math = self.pass2_normalize_math(token.value)
                if norm_math:
                    result_parts.append(f"$${norm_math}$$")

        output = "".join(result_parts)
        # Clean up empty or nested dollar blocks
        output = re.sub(r'\$\s*\$', '', output)
        output = re.sub(r'\$\s*(\$[^$]+\$)\s*\$', r'\1', output)
        output = re.sub(r'[ \t]+', ' ', output).strip()
        return output

    def normalize_formula(self, formula: dict) -> tuple[dict, bool]:
        """
        Normalizes all text fields in a single formula record dict.
        Returns (modified_formula, was_changed).
        """
        if not isinstance(formula, dict):
            return formula, False

        modified = False
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

        if "semantic_variables" in formula and isinstance(formula["semantic_variables"], dict):
            for v_key, v_info in formula["semantic_variables"].items():
                if isinstance(v_info, dict) and "description" in v_info and isinstance(v_info["description"], str):
                    orig_desc = v_info["description"]
                    cleaned_desc = self.normalize_text(orig_desc)
                    if cleaned_desc != orig_desc:
                        v_info["description"] = cleaned_desc
                        modified = True

        return formula, modified


# -----------------------------------------------------------------------------
# CLI Entrypoint for Phase 1 Dry-Run Auditing & Testing
# -----------------------------------------------------------------------------
def main():
    lexer = TerraLexer()

    if len(sys.argv) > 1 and sys.argv[1] == "--test-string":
        sample = sys.argv[2] if len(sys.argv) > 2 else "Incompressible flow (\\n\\rho = \\text{constant}), where \\nabla \\cdot \\mathbf{v} = 0."
        print(f"INPUT:  {sample}")
        print(f"OUTPUT: {lexer.normalize_text(sample)}")
        return

    print("Phase 1: Terra Hybrid Lexer Module Loaded Successfully.")


if __name__ == "__main__":
    main()
