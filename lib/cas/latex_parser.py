#!/usr/bin/env python3
"""
🔬 Terra Physics Lab - Canonical Balanced-Brace LaTeX Parser & Sanitizer
Single source of truth for LaTeX-to-SymPy conversion, algebraic vs. dimensional
equation pre-cleaning, and canonical math string normalization across `lib/cas/`.

Eliminates fixed-depth regex brace limits via deterministic character-level
balanced-brace scanning with zero external dependencies beyond Python stdlib.
"""

import re
from typing import Callable, List, Optional, Tuple


# Formatting and decorator macros whose braced argument represents the underlying symbol
DECORATOR_COMMANDS: Tuple[str, ...] = (
    "mathbf", "mathrm", "mathsf", "mathbb", "mathcal", "mathfrak",
    "boldsymbol", "operatorname", "text",
    "vec", "hat", "bar", "tilde", "underline", "overline",
)

# Big calculus / summation operators whose index bounds are stripped before SymPy AST parsing
BIG_OPERATORS: Tuple[str, ...] = (
    "iiint", "iint", "oint", "int", "sum", "prod",
)

# Greek letter and physical constant control words (longest first to prevent prefix collisions)
GREEK_AND_CONSTANT_COMMANDS: Tuple[str, ...] = (
    "epsilon", "upsilon", "Upsilon", "Lambda", "alpha", "gamma", "delta", "theta",
    "kappa", "sigma", "Sigma", "omega", "Omega", "hbar", "beta", "zeta", "iota",
    "mu", "nu", "xi", "Xi", "pi", "Pi", "rho", "tau", "phi", "Phi", "chi",
    "psi", "Psi", "Gamma", "Delta", "Theta", "eta", "ell",
)


def extract_delimited_arg(
    s: str,
    open_pos: int,
    open_ch: str = "{",
    close_ch: str = "}",
) -> Optional[Tuple[str, int]]:
    """
    Extracts the balanced content inside `open_ch ... close_ch` starting at `open_pos`.
    Respects backslash-escaped characters (e.g. `\\{`, `\\}`).
    Returns `(inner_text, index_after_closing_delimiter)` or `None` if unbalanced.
    """
    if open_pos < 0 or open_pos >= len(s) or s[open_pos] != open_ch:
        return None
    depth = 1
    i = open_pos + 1
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            i += 2
            continue
        if ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return s[open_pos + 1 : i], i + 1
        i += 1
    return None


def extract_braced_arg(s: str, open_pos: int) -> Optional[Tuple[str, int]]:
    """Extracts balanced `{...}` content starting at `open_pos`."""
    return extract_delimited_arg(s, open_pos, "{", "}")


def replace_command_1arg(
    s: str,
    commands: Tuple[str, ...],
    transform_fn: Callable[[str, str], str],
) -> str:
    """
    Recursively replaces 1-argument LaTeX macros `\\cmd{...}` at arbitrary brace depth.
    Inner macros are transformed bottom-up before `transform_fn(cmd, inner)` is applied.
    """
    if "\\" not in s:
        return s
    cmd_re = re.compile(r"\\(" + "|".join(re.escape(c) for c in commands) + r")(?![a-zA-Z])")
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        m = cmd_re.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        ws = m.end()
        while ws < n and s[ws].isspace():
            ws += 1
        if ws < n and s[ws] == "{":
            extracted = extract_braced_arg(s, ws)
            if extracted is not None:
                inner, end_pos = extracted
                inner_transformed = replace_command_1arg(inner, commands, transform_fn)
                out.append(s[pos : m.start()])
                out.append(transform_fn(m.group(1), inner_transformed))
                pos = end_pos
                continue
        out.append(s[pos : m.end()])
        pos = m.end()
    return "".join(out)


def replace_command_2arg(
    s: str,
    commands: Tuple[str, ...],
    transform_fn: Callable[[str, str, str], str],
) -> str:
    """
    Recursively replaces 2-argument LaTeX macros `\\cmd{arg1}{arg2}` at arbitrary brace depth.
    """
    if "\\" not in s:
        return s
    cmd_re = re.compile(r"\\(" + "|".join(re.escape(c) for c in commands) + r")(?![a-zA-Z])")
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        m = cmd_re.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        ws1 = m.end()
        while ws1 < n and s[ws1].isspace():
            ws1 += 1
        if ws1 < n and s[ws1] == "{":
            ext1 = extract_braced_arg(s, ws1)
            if ext1 is not None:
                arg1, pos1 = ext1
                ws2 = pos1
                while ws2 < n and s[ws2].isspace():
                    ws2 += 1
                if ws2 < n and s[ws2] == "{":
                    ext2 = extract_braced_arg(s, ws2)
                    if ext2 is not None:
                        arg2, pos2 = ext2
                        a1_done = replace_command_2arg(arg1, commands, transform_fn)
                        a2_done = replace_command_2arg(arg2, commands, transform_fn)
                        out.append(s[pos : m.start()])
                        out.append(transform_fn(m.group(1), a1_done, a2_done))
                        pos = pos2
                        continue
        out.append(s[pos : m.end()])
        pos = m.end()
    return "".join(out)


def _replace_sqrt(s: str) -> str:
    """
    Recursively converts `\\sqrt{A}` -> `sqrt(A)` and `\\sqrt[n]{A}` -> `((A)**(1/(n)))`
    at arbitrary brace nesting depth.
    """
    if r"\sqrt" not in s:
        return s
    sqrt_re = re.compile(r"\\sqrt(?![a-zA-Z])")
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        m = sqrt_re.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        ws = m.end()
        while ws < n and s[ws].isspace():
            ws += 1
        root_arg: Optional[str] = None
        if ws < n and s[ws] == "[":
            ext_root = extract_delimited_arg(s, ws, "[", "]")
            if ext_root is not None:
                root_arg, ws = ext_root
                while ws < n and s[ws].isspace():
                    ws += 1
        if ws < n and s[ws] == "{":
            ext_rad = extract_braced_arg(s, ws)
            if ext_rad is not None:
                rad, end_pos = ext_rad
                rad_done = _replace_sqrt(rad)
                out.append(s[pos : m.start()])
                if root_arg is not None:
                    root_done = _replace_sqrt(root_arg)
                    out.append(f"(({rad_done})**(1/({root_done})))")
                else:
                    out.append(f"sqrt({rad_done})")
                pos = end_pos
                continue
        out.append(s[pos : m.end()])
        pos = m.end()
    return "".join(out)


def _strip_big_operators(s: str, only_equal_bounds: bool = False) -> str:
    """
    Strips `\\sum`, `\\prod`, `\\int`, `\\iint`, `\\iiint`, `\\oint` along with
    any attached `_...` and `^...` bounds at arbitrary brace depth.
    If `only_equal_bounds` is True, only strips operators whose bounds contain `=`.
    """
    if "\\" not in s:
        return s
    op_re = re.compile(r"\\(?:" + "|".join(BIG_OPERATORS) + r")(?![a-zA-Z])")
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        m = op_re.search(s, pos)
        if not m:
            out.append(s[pos:])
            break
        cur = m.end()
        has_eq_in_bound = False
        while cur < n:
            ws = cur
            while ws < n and s[ws].isspace():
                ws += 1
            if ws < n and s[ws] in ("_", "^"):
                b_start = ws + 1
                while b_start < n and s[b_start].isspace():
                    b_start += 1
                if b_start < n and s[b_start] == "{":
                    ext = extract_braced_arg(s, b_start)
                    if ext is not None:
                        b_text, cur = ext
                        if "=" in b_text:
                            has_eq_in_bound = True
                        continue
                elif b_start < n and s[b_start] == "\\":
                    cm = re.match(r"\\[a-zA-Z]+", s[b_start:])
                    if cm:
                        cur = b_start + cm.end()
                        continue
                elif b_start < n and s[b_start].isalnum():
                    cur = b_start + 1
                    continue
            break
        if only_equal_bounds and not has_eq_in_bound:
            out.append(s[pos:cur])
        else:
            out.append(s[pos : m.start()])
            out.append(" ")
        pos = cur
    return "".join(out)


def _replace_subscripts(s: str) -> str:
    """
    Recursively unwraps `_{...}` -> `_...` at arbitrary brace depth, converting
    internal commas inside subscripts (e.g. `v_{x,0}` -> `v_x_0`) so SymPy never
    interprets subscripted symbols as tuples.
    """
    if "_{" not in s:
        return s
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        idx = s.find("_{", pos)
        if idx == -1:
            out.append(s[pos:])
            break
        if idx > 0 and s[idx - 1] == "\\":
            out.append(s[pos : idx + 2])
            pos = idx + 2
            continue
        ext = extract_braced_arg(s, idx + 1)
        if ext is not None:
            inner, end_pos = ext
            inner_done = _replace_subscripts(inner).replace(",", "_")
            out.append(s[pos:idx])
            out.append("_" + inner_done)
            pos = end_pos
            continue
        out.append(s[pos : idx + 2])
        pos = idx + 2
    return "".join(out)


def _replace_superscripts(s: str) -> str:
    """
    Recursively converts `^{...}` -> `**(...)` at arbitrary brace depth, followed
    by single-token exponents `^x` -> `**x`.
    """
    if "^" not in s:
        return s
    out: List[str] = []
    pos = 0
    n = len(s)
    while pos < n:
        idx = s.find("^{", pos)
        if idx == -1:
            out.append(s[pos:])
            break
        if idx > 0 and s[idx - 1] == "\\":
            out.append(s[pos : idx + 2])
            pos = idx + 2
            continue
        ext = extract_braced_arg(s, idx + 1)
        if ext is not None:
            inner, end_pos = ext
            inner_done = _replace_superscripts(inner)
            out.append(s[pos:idx])
            out.append(f"**({inner_done})")
            pos = end_pos
            continue
        out.append(s[pos : idx + 2])
        pos = idx + 2
    res = "".join(out)
    res = re.sub(r"\^([0-9a-zA-Z])", r"**\1", res)
    return res


def _convert_algebraic_time_dots(s: str) -> str:
    """
    Converts `\\ddot{q}` -> `ddq` and `\\dot{q}` -> `dq` (including Greek symbols
    such as `\\dot{\\phi}` -> `dphi`) so phase-space velocities remain distinct
    algebraic symbols rather than collapsing to `q` or dividing by `t`.
    """
    if r"\dot" not in s and r"\ddot" not in s:
        return s

    def _clean_dot_target(prefix: str, inner: str) -> str:
        clean = replace_command_1arg(inner, DECORATOR_COMMANDS, lambda _c, x: x)
        clean = _replace_subscripts(clean).strip()
        if clean.startswith("\\"):
            clean = clean[1:].strip()
        if clean == "lambda":
            clean = "lam"
        if re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", clean):
            return f"{prefix}{clean}"
        return clean

    s = replace_command_1arg(s, ("ddot",), lambda _, inner: _clean_dot_target("dd", inner))
    s = replace_command_1arg(s, ("dot",), lambda _, inner: _clean_dot_target("d", inner))
    s = re.sub(r"\\ddot\s*\\([a-zA-Z]+)", lambda m: _clean_dot_target("dd", m.group(1)), s)
    s = re.sub(r"\\dot\s*\\([a-zA-Z]+)", lambda m: _clean_dot_target("d", m.group(1)), s)
    s = re.sub(r"\\ddot\s+([a-zA-Z][a-zA-Z0-9_]*)", r"dd\1", s)
    s = re.sub(r"\\dot\s+([a-zA-Z][a-zA-Z0-9_]*)", r"d\1", s)
    return s


def split_top_level_equals(s: str) -> List[str]:
    """
    Splits a math string on `=` characters that occur strictly at top-level
    grouping depth (outside `{...}`, `(...)`, and `[...]`).
    """
    parts: List[str] = []
    cur: List[str] = []
    depth = 0
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "\\":
            cur.append(s[i : i + 2])
            i += 2
            continue
        if ch in "({[":
            depth += 1
            cur.append(ch)
        elif ch in ")}]":
            if depth > 0:
                depth -= 1
            cur.append(ch)
        elif ch == "=" and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return parts


def _strip_outer_math_delimiters(s: str) -> str:
    """Strips outer `\\[...\\]`, `$$...$$`, `$...$`, or `\\(...\\)` math delimiters."""
    s = s.strip()
    s = re.sub(r"^\\\[|\\\]$", "", s)
    s = re.sub(r"^\$\$|\$\$$", "", s)
    s = re.sub(r"^\$|\$$", "", s)
    s = re.sub(r"^\\\(|\\\)$", "", s)
    return s.strip()


def _normalize_greek_variants(s: str) -> str:
    """Normalizes stylistic Greek LaTeX variants to their canonical control words."""
    s = re.sub(r"\\varepsilon(?![a-zA-Z])", r"\\epsilon", s)
    s = re.sub(r"\\varphi(?![a-zA-Z])", r"\\phi", s)
    s = re.sub(r"\\vartheta(?![a-zA-Z])", r"\\theta", s)
    s = re.sub(r"\\varrho(?![a-zA-Z])", r"\\rho", s)
    return s


def _strip_text_annotations(s: str) -> str:
    """
    Strips trailing text annotations such as `\\quad (\\text{Fermi Energy})`,
    `\\quad \\text{...}`, and conditional clauses `\\text{where ...}` / `\\text{for ...}`
    using balanced delimiter scanning.
    """
    # Strip \quad (\text{...}) or trailing (\text{...})
    while True:
        m = re.search(r"(?:\\quad\s*|\\qquad\s*)\(", s)
        if not m:
            break
        ext = extract_delimited_arg(s, m.end() - 1, "(", ")")
        if ext is not None:
            inner, end_pos = ext
            if r"\text" in inner or end_pos >= len(s.rstrip()):
                s = s[: m.start()] + s[end_pos:]
                continue
        break

    # Strip trailing (\text{...}) at end of string without \quad
    m_end = re.search(r"\(\s*\\text\{", s)
    if m_end:
        ext = extract_delimited_arg(s, m_end.start(), "(", ")")
        if ext is not None and ext[1] >= len(s.rstrip()):
            s = s[: m_end.start()]

    # Strip \quad \text{...}
    while True:
        m = re.search(r"(?:\\quad|\\qquad)\s*\\text\s*\{", s)
        if not m:
            break
        brace_pos = s.find("{", m.start())
        ext = extract_braced_arg(s, brace_pos)
        if ext is not None:
            _, end_pos = ext
            s = s[: m.start()] + s[end_pos:]
            continue
        break

    # Strip \text{where ...} and \text{for ...}
    while True:
        m = re.search(r"\\text\s*\{\s*(?:where|for)\b", s)
        if not m:
            break
        brace_pos = s.find("{", m.start())
        ext = extract_braced_arg(s, brace_pos)
        if ext is not None:
            _, end_pos = ext
            s = s[: m.start()] + s[end_pos:]
            continue
        break

    return s.strip()


def clean_latex_equation(latex: str, mode: str = "dimensional") -> str:
    """
    Pre-cleans a raw LaTeX equation or expression prior to SymPy parsing.

    Modes:
    - `"dimensional"` (default): Strips annotations, normalizes relations (`\\approx`, `<`, `>`, etc.)
      to `=`, lowers time derivatives (`\\dot{x}` -> `(x / t)`), and lowers differential/vector
      operators (`\\nabla` -> `/ L`, `\\frac{\\partial A}{\\partial x}` -> `(A / x)`) for SI/Natural
      dimensional homogeneity checking.
    - `"algebraic"`: Strips annotations, normalizes primes (`x'` -> `x_prime`), conjugation,
      error margins, and chained equalities while preserving algebraic structure (`\\dot{q}` -> `dq`,
      no division by `t` or `L`).
    """
    if mode not in ("dimensional", "algebraic"):
        raise ValueError(f"Unsupported clean_latex_equation mode: {mode!r}")

    s = _strip_outer_math_delimiters(latex)
    s = _strip_text_annotations(s)

    # Handle conjunctions (\iff, \implies): select the primary equality clause
    for conj in (r"\iff", r"\implies"):
        if conj in s:
            parts = s.split(conj)
            rhs_has_eq = len(split_top_level_equals(parts[1])) >= 2 or (
                mode == "dimensional" and bool(re.search(r"\\approx|\\equiv|\\sim|\\propto", parts[1]))
            )
            s = parts[1].strip() if rhs_has_eq else parts[0].strip()
            break

    if mode == "dimensional":
        s = re.sub(
            r"\\approx|\\equiv|\\sim|\\propto|\\geq|\\leq|\\ge(?![a-zA-Z])|\\le(?![a-zA-Z])|>|<",
            "=",
            s,
        )
    else:
        s = re.sub(r"\\approx|\\equiv|\\sim", "=", s)

    # Strip complex conjugation and hermitian adjoint operators
    s = re.sub(r"\^\{\s*\*\s*\}|\^\*", "", s)
    s = re.sub(r"\^\{\s*\\dagger\s*\}|\^\\dagger", "", s)
    s = re.sub(r"\\dagger(?![a-zA-Z])", "", s)

    # Normalize arcseconds / double primes and single primes
    s = re.sub(r"([0-9]+(?:\.[0-9]+)?)\s*''", r"\1", s)
    s = re.sub(r"''", "_dprime", s)
    s = re.sub(r"([a-zA-Z0-9_]+)'", r"\1_prime", s)

    # Strip measurement error margins: 2.73 \pm 0.02 -> 2.73
    s = re.sub(r"\\pm\s*[0-9]+(?:\.[0-9]+)?", "", s)

    # Normalize solar/astronomical subscript symbols: M_\odot -> M_sun
    s = re.sub(r"([MRL])_\{?\\odot\}?", r"\1_sun", s)

    # Normalize finite differences: \Delta S -> Delta_S
    s = re.sub(r"\\Delta\s*([a-zA-Z])", r"Delta_\1", s)

    if mode == "dimensional":
        # Normalize repeated integrals: \int \int -> \int
        s = re.sub(r"\\int\s*\\int\s*\\int", r"\\int", s)
        s = re.sub(r"\\int\s*\\int", r"\\int", s)

        # Normalize tensor mixed indices: R^\rho_{\sigma\mu\nu} -> R_rhosigmamunu
        s = re.sub(r"\b([RTFGC]|\\Gamma)\^\{?([a-zA-Z])\}?_\{?([a-zA-Z]+)\}?", r"\1_\2\3", s)

        # Dimensional lowering of time derivatives: \ddot{x} -> (x / (t**2)), \dot{M} -> (M / t)
        s = re.sub(r"\\ddot\{?([a-zA-Z])\}?(?:_\{?[a-zA-Z0-9_]+\}?)?", r"(\1 / (t**2))", s)
        s = re.sub(r"\\dot\{?([a-zA-Z])\}?(?:_\{?[a-zA-Z0-9_]+\}?)?", r"(\1 / t)", s)

        # Normalize differentials: d\mathbf{x} -> dx, \mathrm{d}\mathbf{l} -> dl
        s = re.sub(
            r"\\(?:mathrm\{d\}|mathrm\{D\}|d(?![a-zA-Z]))\s*(?:\\mathbf|\\boldsymbol|\\vec)?\{?([a-zA-Z])\}?",
            r"d\1",
            s,
        )

        # Normalize 4D volume elements: d^4x -> d4x
        s = re.sub(r"d\^4\s*(?:\\mathbf\{x\}|x)", "d4x", s)

        # Normalize partial derivatives to dimensional quotients
        s = re.sub(
            r"\\frac\{\\partial\s*(?:\\mathbf\{([a-zA-Z])\}|([a-zA-Z]))\}\{\\partial\s*([a-zA-Z])\}",
            r"(\1\2 / \3)",
            s,
        )

        # Disambiguate vector EM fields from scalar Energy / Action
        s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{E\}", "E_field", s)
        s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{J\}", "J_current", s)
        s = re.sub(r"\\(?:mathbf|boldsymbol|vec)\{B\}", "B", s)

        # Dimensional lowering of vector differential operators (div, grad, curl, laplacian)
        s = re.sub(r"\\nabla\^2\s*(?:\\mathbf\{([a-zA-Z])\}|([a-zA-Z])|\\Phi|\\phi)", r"(\1\2Phi / (L**2))", s)
        s = re.sub(r"\\nabla\s*\\times\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)
        s = re.sub(r"\\nabla\s*\\cdot\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)
        s = re.sub(r"\\nabla\s*(?:\\mathbf\{([a-zA-Z_]+)\}|([a-zA-Z]))", r"(\1\2 / L)", s)

        # Normalize quantum expectation values and normalized bra-ket states
        s = re.sub(r"\\langle\s*\\sigma\s*v\s*\\rangle", "(sigma * v)", s)
        s = re.sub(r"\\langle\s*([a-zA-Z0-9_]+)\s*\\rangle", r"(\1)", s)
        s = re.sub(r"\\langle\s*[^{}|]+\s*\|\s*[^{}|]+\s*\\rangle", " 1 ", s)
        if not re.search(r"\\langle[^|]+\|[^|]+\|[^|]+\\rangle", s):
            s = re.sub(r"\|[a-zA-Z0-9_\s\(\)\^\{\}\*]+\\rangle", " 1 ", s)
            s = re.sub(r"\\langle[a-zA-Z0-9_\s\(\)\^\{\}\*]+\|", " 1 ", s)

        # Normalize metric tensor quadratic forms
        s = re.sub(
            r"(?:\\eta|g|\\gamma)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*([a-zA-Z])\^\{?[a-zA-Z0-9_]\}?\s*([a-zA-Z])\^\{?[a-zA-Z0-9_]\}?",
            r"(\1 * \2)",
            s,
        )
        s = re.sub(
            r"(?:\\eta|g|\\gamma)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*\(([^()]+)\)\^\{?[a-zA-Z0-9_]\}?\s*\(([^()]+)\)\^\{?[a-zA-Z0-9_]\}?",
            r"((\1) * (\2))",
            s,
        )
        s = re.sub(
            r"(?:g|\\gamma|\\eta)(?:_\{?[a-zA-Z0-9_,]+\}?)?\s*d[a-zA-Z]\^\{?[a-zA-Z0-9_]\}?\s*d[a-zA-Z]\^\{?[a-zA-Z0-9_]\}?",
            "(dx**2)",
            s,
        )
        s = re.sub(r"(?:\\eta|g|h|\\gamma)_\{?\\mu\\nu\}?", " 1 ", s)

        # Normalize explicit time-argument notation: x(t) -> x, a(t) -> a
        s = re.sub(r"([a-zA-Z0-9_]+)\s*\([t]\)", r"\1", s)
    else:
        # Algebraic mode: preserve \ddot{q} -> ddq and \dot{q} -> dq without dividing by t
        s = _convert_algebraic_time_dots(s)

    # Strip big operators whose bounds contain '=' (e.g. \sum_{i=1}^{3N}) before splitting '='
    s = _strip_big_operators(s, only_equal_bounds=True)

    # Collapse chained top-level equalities (A = B = C)
    top_parts = split_top_level_equals(s)
    if len(top_parts) > 2:
        if mode == "algebraic":
            s = f"{top_parts[0].strip()} = {top_parts[-1].strip()}"
        else:
            s = f"{top_parts[0]} = {top_parts[1]}"

    return s.strip()


def clean_equation_for_cas(latex: str) -> str:
    """
    Backward-compatible dimensional pre-cleaner alias (`mode="dimensional"`).
    """
    return clean_latex_equation(latex, mode="dimensional")


def latex_to_sympy_str(latex: str) -> str:
    """
    Converts a LaTeX math expression into SymPy-parseable syntax using deterministic
    balanced-brace scanning (supporting arbitrary nesting depth for fractions, roots,
    decorators, operator bounds, subscripts, and superscripts).
    """
    s = _strip_outer_math_delimiters(latex)
    s = _normalize_greek_variants(s)

    # Normalize \dfrac and \tfrac to \frac
    s = re.sub(r"\\(?:d|t)frac(?![a-zA-Z])", r"\\frac", s)

    # Strip big operators (\sum, \prod, \int, ...) with arbitrarily nested bounds
    s = _strip_big_operators(s, only_equal_bounds=False)

    # Unwrap formatting and decorator macros at arbitrary nesting depth
    s = replace_command_1arg(s, DECORATOR_COMMANDS, lambda _cmd, inner: inner)
    s = replace_command_2arg(s, ("cssId",), lambda _cmd, _id, inner: inner)

    # Convert remaining algebraic time-dot macros (\dot{q} -> dq, \ddot{q} -> ddq)
    s = _convert_algebraic_time_dots(s)

    # Normalize primes exposed after decorator unwrapping (e.g. \mathbf{r}' -> r_prime)
    s = re.sub(r"([0-9]+(?:\.[0-9]+)?)\s*''", r"\1", s)
    s = re.sub(r"([a-zA-Z0-9_]+)\s*''", r"\1_dprime", s)
    s = re.sub(r"([a-zA-Z0-9_]+)\s*'", r"\1_prime", s)

    # Strip conjugation / adjoint superscripts that would otherwise form invalid **( * )
    s = re.sub(r"\^\{\s*\*\s*\}|\^\*", "", s)
    s = re.sub(r"\^\{\s*\\dagger\s*\}|\^\\dagger", "", s)

    # Fractions and roots at arbitrary brace depth
    s = replace_command_2arg(s, ("frac",), lambda _cmd, num, den: f"(({num})/({den}))")
    s = _replace_sqrt(s)

    # Absolute values: \left| A \right|, \lvert A \rvert, |A| -> (abs(A))
    s = re.sub(r"\\(?:left\s*\||right\s*\||lvert|rvert)", "|", s)
    s = re.sub(r"\|([^|]+)\|", r"(abs(\1))", s)

    # Separate adjacent TeX control words: \pi\epsilon -> \pi \epsilon
    s = re.sub(r"\\([a-zA-Z]+)(?=\\)", r"\\\1 ", s)

    # Map \lambda -> lam (avoiding Python keyword `lambda`) and Greek letters -> symbol names
    s = re.sub(r"\\lambda(?![a-zA-Z])", "lam", s)
    for g in GREEK_AND_CONSTANT_COMMANDS:
        s = re.sub(r"\\" + g + r"(?![a-zA-Z])", g, s)

    # Balanced subscripts and superscripts
    s = _replace_subscripts(s)
    s = _replace_superscripts(s)

    # Multiplication and spacing macros
    s = re.sub(r"\\cdot|\\times", "*", s)
    s = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg|quad|qquad|\,|\;|\!|\:)", " ", s)

    # Strip any remaining LaTeX control sequences (e.g. \neq, \sim, \approx)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)

    # Replace remaining grouping braces with parentheses
    s = s.replace("{", "(").replace("}", ")")
    return s


def normalize_math_string(s: str) -> str:
    """
    Canonicalizes a LaTeX math string into a compact structural fingerprint for
    derivation step matching, using balanced-brace unwrapping for decorators and fractions.
    """
    if not s:
        return ""
    s = _strip_outer_math_delimiters(s)
    s = _strip_text_annotations(s)
    s = _normalize_greek_variants(s)

    # Unwrap font/decorator wrappers and \cssId at arbitrary nesting depth
    s = replace_command_1arg(s, DECORATOR_COMMANDS, lambda _cmd, inner: inner)
    s = replace_command_2arg(s, ("cssId",), lambda _cmd, _id, inner: inner)

    # Strip sizing macros
    s = re.sub(r"\\(?:left|right|big|Big|bigg|Bigg)\b", "", s)

    # Normalize time / proper-time derivatives to dot notation
    s = re.sub(
        r"\\frac\{\\?(?:d|partial)\^2\s*([a-zA-Z0-9_\\^\{\}]+)\}\{\\?(?:d|partial)\s*(?:t|\\tau)\^2\}",
        r"\\ddot{\1}",
        s,
    )
    s = re.sub(
        r"\\frac\{\\?(?:d|partial)\s*([a-zA-Z0-9_\\^\{\}]+)\}\{\\?(?:d|partial)\s*(?:t|\\tau)\}",
        r"\\dot{\1}",
        s,
    )

    # Normalize \exp(...) -> e^{...} using balanced parentheses
    while r"\exp" in s:
        m = re.search(r"\\exp\s*\(", s)
        if not m:
            break
        ext = extract_delimited_arg(s, m.end() - 1, "(", ")")
        if ext is None:
            break
        inner, end_pos = ext
        s = s[: m.start()] + f"e^{{{inner}}}" + s[end_pos:]

    # Normalize \dfrac, \tfrac -> \frac and expand \frac{A}{B} -> A/B at arbitrary depth
    s = re.sub(r"\\(?:d|t)frac(?![a-zA-Z])", r"\\frac", s)
    s = replace_command_2arg(s, ("frac",), lambda _cmd, num, den: f"{num}/{den}")

    # Normalize sum bounds (\sum_{i=1}^N, \sum_{i} -> \sum_i)
    s = re.sub(r"\\sum_\{?([a-zA-Z])(?:=[^}^]+)?\}?(?:\^\{?[a-zA-Z0-9\\]+\}?)?", r"\\sum_\1", s)

    # Normalize variational test function aliases (\dot{\eta}^i -> \delta\dot{q}^i, \eta^i -> \delta q^i)
    s = re.sub(r"\\dot\{?\\eta\}?\^i", r"\\delta\\dot{q}^i", s)
    s = re.sub(r"\\eta\^i", r"\\delta q^i", s)

    # Normalize relational symbols
    s = re.sub(r"\\(?:equiv|approx|propto|sim|to|rightarrow|xrightarrow\{[^{}]*\})", "=", s)
    s = re.sub(r"\\(?:le|leq)\b", "<=", s)
    s = re.sub(r"\\(?:ge|geq)\b", ">=", s)

    # Strip delimiters, parens, brackets, braces, underscores, carets, whitespace, and punctuation spacing
    s = re.sub(r"[\(\)\[\]\{\}\s\\,;!\|'_\^]+|\\,|\\;|\\!|\\quad|\\qquad", "", s)
    return s
