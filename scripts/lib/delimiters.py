#!/usr/bin/env python3
"""
scripts/lib/delimiters.py

Centralized, authoritative math delimiter module for Terra Physics Lab.
Provides delimiter-agnostic math stripping, validation, and normalization
used across Pytest suites, pre-push CI gatekeepers, and maintenance scripts.
"""

import re
from typing import List, Tuple, Optional

# Regular expression to match display math:
# - \begin{env}...\end{env}
# - \[...\]
# - $$...$$
DISPLAY_MATH_RE = re.compile(
    r"\\begin\{(?:equation|align|gather|multline|bmatrix|pmatrix|matrix|split)\*?\}[\s\S]*?\\end\{(?:equation|align|gather|multline|bmatrix|pmatrix|matrix|split)\*?\}|"
    r"\\\[[\s\S]*?\\\]|"
    r"\$\$[\s\S]*?\$\$",
    re.MULTILINE
)

# Regular expression to match inline math:
# - \(...\)
# - $...$ (ignoring escaped \$)
INLINE_MATH_BRACKET_RE = re.compile(r"\\\([\s\S]*?\\\)")
INLINE_MATH_DOLLAR_RE = re.compile(r"(?<!\\)\$((?:[^$\\]|\\.)+?)\$", re.DOTALL)

# Markdown code blocks or spans (often used for short math formulas or code)
MARKDOWN_CODE_RE = re.compile(r"`[^`]+`")

# Common LaTeX macros that belong strictly in math mode
COMMON_TEX_MACROS_PATTERN = (
    r"\\(to|mu|lambda|theta|partial|nabla|int|oint|iint|sum|prod|frac|sqrt|"
    r"alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|iota|kappa|nu|xi|omicron|rho|"
    r"sigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|"
    r"Upsilon|Phi|Psi|Omega|infty|cdot|times|pm|mp|leq|geq|neq|approx|equiv|sim|"
    r"hat|bar|vec|dot|ddot|tilde|mathbf|mathrm|mathcal|mathbb|mathit|text|operatorname)(?![a-zA-Z])"
)
TEX_MACRO_RE = re.compile(COMMON_TEX_MACROS_PATTERN)


def strip_math_blocks(text: str, replace_with: str = " ") -> str:
    """
    Removes all valid display, inline, and code math blocks from text.
    Handles:
      1. Display environments (\\begin{...}...\\end{...}, \\[...\\], $$...$$)
      2. Inline LaTeX bracket math (\\(...\\))
      3. Inline dollar math ($...$)
      4. Inline markdown code spans (`...`)
    Returns the remaining non-math prose.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Strip display math
    t = DISPLAY_MATH_RE.sub(replace_with, text)
    # 2. Strip inline brackets
    t = INLINE_MATH_BRACKET_RE.sub(replace_with, t)
    # 3. Strip inline dollars
    t = INLINE_MATH_DOLLAR_RE.sub(replace_with, t)
    # 4. Strip markdown code spans
    t = MARKDOWN_CODE_RE.sub(replace_with, t)

    return t


def count_unescaped_dollars(text: str) -> int:
    """Counts the number of unescaped '$' signs in text."""
    if not text or not isinstance(text, str):
        return 0
    return len(re.findall(r"(?<!\\)\$", text))


def check_dollar_balance(text: str) -> bool:
    """Returns True if unescaped dollar signs are balanced (even count)."""
    return count_unescaped_dollars(text) % 2 == 0


def check_bracket_balance(text: str) -> bool:
    """Returns True if \\( and \\) are balanced."""
    if not text or not isinstance(text, str):
        return True
    opens = len(re.findall(r"\\\(", text))
    closes = len(re.findall(r"\\\)", text))
    return opens == closes


def find_leaked_macros(text: str) -> List[Tuple[str, int, str]]:
    """
    Finds LaTeX macros that leak outside of valid math mode.
    Returns a list of (macro_name, start_position, snippet).
    """
    if not text or not isinstance(text, str):
        return []

    # First strip all valid math
    clean_prose = strip_math_blocks(text, replace_with=" ")

    leaks = []
    for match in TEX_MACRO_RE.finditer(clean_prose):
        start = match.start()
        snippet = clean_prose[max(0, start - 20):min(len(clean_prose), start + 40)].strip()
        leaks.append((match.group(0), start, snippet))

    return leaks


def validate_prose_delimiters(text: str) -> List[str]:
    """
    Canonical validator for narrative prose fields.
    Returns a list of error descriptions (empty list if valid).
    """
    if not text or not isinstance(text, str):
        return []

    errors = []

    # 1. Check dollar balance
    dollar_count = count_unescaped_dollars(text)
    if dollar_count % 2 != 0:
        errors.append(f"Unbalanced '$' count ({dollar_count})")

    # 2. Check bracket math balance
    if not check_bracket_balance(text):
        errors.append("Unbalanced '\\(' and '\\)' delimiters")

    # 3. Misplaced inverted delimiters like =$\frac or }${\frac
    if re.search(r"=\$\s*\\frac|\}\$\{\\frac|\$\s*=\s*\$\\frac|is\$\s*\\frac", text):
        errors.append("Misplaced '$' around fraction or equals sign")

    # 4. Trailing isolated dollar sign (ending with ' $' or isolated '$' with no opening pair)
    if text.endswith(" $") or (text.endswith(".$") and dollar_count == 1):
        errors.append("Trailing isolated '$' at end of paragraph")

    # 5. Check for leaked macros outside math mode
    leaks = find_leaked_macros(text)
    if leaks:
        macro_names = ", ".join(sorted(set(m[0] for m in leaks))[:5])
        errors.append(f"Leaked TeX macro outside math mode: {macro_names}")

    # 6. Check for HTML infiltration inside math blocks
    html_in_math = validate_no_html_in_math(text)
    errors.extend(html_in_math)

    return errors


UNWRAPPED_ARG_MACRO_RE = re.compile(r"\\(mathbf|vec|hat|mathcal|bar|dot|ddot|frac)\{[^}]+\}")

HTML_TAG_NAMES = (
    r"a|abbr|b|blockquote|body|br|button|caption|cite|code|col|colgroup|dd|del|dfn|div|dl|dt|"
    r"em|fieldset|figcaption|figure|footer|form|h[1-6]|head|header|hr|html|i|iframe|img|input|"
    r"ins|kbd|label|legend|li|link|main|map|mark|meta|nav|noscript|object|ol|optgroup|option|"
    r"output|p|param|picture|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|small|source|"
    r"span|strong|style|sub|summary|sup|svg|table|tbody|td|template|textarea|tfoot|th|thead|"
    r"time|title|tr|track|u|ul|var|video|wbr"
)

HTML_IN_MATH_RE = re.compile(
    rf"</?(?:{HTML_TAG_NAMES})\b[^>]*>|"
    rf"&lt;/?(?:{HTML_TAG_NAMES})\b[^&]*&gt;|"
    r"\b(?:href|class)=[\"'][^\"'>\s]*[\"']",
    re.IGNORECASE
)


def extract_math_blocks(text: str) -> List[Tuple[str, str]]:
    """
    Extracts all math blocks from text as (delimiter_type, math_content).
    Handles display environments, bracket math, and dollar math.
    """
    if not text or not isinstance(text, str):
        return []

    blocks = []
    for m in DISPLAY_MATH_RE.finditer(text):
        blocks.append(("display", m.group(0)))
    for m in INLINE_MATH_BRACKET_RE.finditer(text):
        blocks.append(("bracket", m.group(0)))
    for m in INLINE_MATH_DOLLAR_RE.finditer(text):
        blocks.append(("dollar", m.group(1)))

    return blocks


def find_html_in_math(text: str, is_raw_tex: bool = False) -> List[Tuple[str, str]]:
    r"""
    Finds HTML tags or attributes embedded inside math blocks (or within raw LaTeX).
    If is_raw_tex is True, the entire string is treated as math mode (e.g. formula 'equation' field).
    Otherwise, only text inside math delimiters ($...$, \(...\), \[...\], $$...$$, or data-tex) is checked.
    Returns list of (snippet, html_match).
    """
    if not text or not isinstance(text, str):
        return []

    violations = []
    # If explicitly raw LaTeX (e.g. formula 'equation' field)
    if is_raw_tex:
        matches = HTML_IN_MATH_RE.findall(text)
        for m in matches:
            violations.append((text[:60].strip(), m))
        return violations

    # Extract all math blocks
    blocks = extract_math_blocks(text)
    for _, block in blocks:
        matches = HTML_IN_MATH_RE.findall(block)
        for m in matches:
            violations.append((block[:60].strip(), m))

    # Also check SVG data-tex attributes
    for dt_m in re.finditer(r'<svg\s+[^>]*data-tex=["\']([^"\']*)["\']', text, re.IGNORECASE):
        tex = dt_m.group(1)
        matches = HTML_IN_MATH_RE.findall(tex)
        for m in matches:
            violations.append((tex[:60].strip(), m))

    return violations


def validate_no_html_in_math(text: str, is_raw_tex: bool = False) -> List[str]:
    """
    Validates that text does not contain HTML markup or attribute tags inside math blocks.
    Returns list of error messages.
    """
    violations = find_html_in_math(text, is_raw_tex=is_raw_tex)
    if not violations:
        return []
    return [f"HTML infiltration in math block: '{html_tag}' inside '{snippet}'" for snippet, html_tag in violations]


def find_unwrapped_macros(text: str) -> List[str]:
    """Finds unwrapped TeX commands with arguments (e.g. \\frac{...}, \\mathbf{...}) outside math mode."""
    if not text or not isinstance(text, str):
        return []
    outside = strip_math_blocks(text)
    return [m.group(0) for m in UNWRAPPED_ARG_MACRO_RE.finditer(outside)]


def validate_narrative_delimiters(text: str) -> List[str]:
    """
    Validates narrative prose fields using delimiter-agnostic math mode detection.
    Catches:
      1. Unbalanced dollar signs (taking escaped \\$ into account)
      2. Misplaced delimiters around fractions or equals
      3. Trailing isolated dollar sign (e.g. ' $' or isolated unclosed '.$')
      4. Unwrapped TeX command macros outside valid math delimiters
      5. HTML tags or attributes embedded inside math blocks
    """
    if not text or not isinstance(text, str):
        return []

    errors = []
    dollar_count = count_unescaped_dollars(text)
    if dollar_count % 2 != 0:
        errors.append(f"Unbalanced '$' count ({dollar_count})")

    if re.search(r"=\$\s*\\frac|\}\$\{\\frac|\$\s*=\s*\$\\frac|is\$\s*\\frac", text):
        errors.append("Misplaced '$' around fraction/equals")

    if text.endswith(" $") or (text.endswith(".$") and dollar_count == 1):
        errors.append("Trailing isolated '$'")

    unwrapped = find_unwrapped_macros(text)
    if unwrapped:
        errors.append(f"Unwrapped TeX macro outside math mode: {unwrapped[0]}")

    html_errors = validate_no_html_in_math(text)
    errors.extend(html_errors)

    return errors
