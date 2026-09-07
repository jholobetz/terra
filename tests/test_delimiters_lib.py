#!/usr/bin/env python3
"""
tests/test_delimiters_lib.py

Unit tests for the centralized scripts.lib.delimiters module.
"""

import pytest
from scripts.lib.delimiters import (
    strip_math_blocks,
    count_unescaped_dollars,
    check_dollar_balance,
    check_bracket_balance,
    find_leaked_macros,
    validate_prose_delimiters,
    extract_math_blocks,
    find_html_in_math,
    validate_no_html_in_math,
)


def test_strip_dollar_math():
    text = "The energy $E = mc^2$ is conserved."
    stripped = strip_math_blocks(text)
    assert "$E = mc^2$" not in stripped
    assert "The energy" in stripped
    assert "is conserved." in stripped


def test_strip_bracket_math():
    text = r"The Coulomb constant \(k_e = \frac{1}{4\pi\varepsilon_0}\) is invariant."
    stripped = strip_math_blocks(text)
    assert r"\frac" not in stripped
    assert "The Coulomb constant" in stripped
    assert "is invariant." in stripped


def test_strip_display_math():
    text = r"Equation: \[ \int_0^\infty e^{-x} dx = 1 \] follows immediately."
    stripped = strip_math_blocks(text)
    assert r"\int" not in stripped
    assert "follows immediately." in stripped


def test_strip_markdown_code():
    text = r"Scales as `T^3`. The factor `g \frac{2\pi^2}{45}` is constant."
    stripped = strip_math_blocks(text)
    assert r"\frac" not in stripped
    assert "Scales as" in stripped


def test_dollar_balance():
    assert check_dollar_balance("$E = mc^2$") is True
    assert check_dollar_balance("Cost is $5.00 and $10.00") is True
    assert check_dollar_balance(r"Escaped \$5 is fine") is True
    assert check_dollar_balance("$E = mc^2") is False


def test_bracket_balance():
    assert check_bracket_balance(r"\(x = y\)") is True
    assert check_bracket_balance(r"\(x = y") is False


def test_find_leaked_macros():
    # Valid - inside math
    assert len(find_leaked_macros(r"Here $x = \frac{1}{2}$")) == 0
    assert len(find_leaked_macros(r"Here \(x = \frac{1}{2}\)")) == 0

    # Invalid - outside math
    leaks = find_leaked_macros(r"Here is an unwrapped \frac{a}{b} macro.")
    assert len(leaks) > 0
    assert leaks[0][0] == r"\frac"


def test_validate_prose_delimiters():
    # Valid dollar math
    errors = validate_prose_delimiters("Energy is $E = mc^2$.")
    assert len(errors) == 0

    # Valid bracket math
    errors = validate_prose_delimiters(r"The constant \(k_e = \frac{1}{4\pi\varepsilon_0}\) is defined.")
    assert len(errors) == 0

    # Unbalanced dollar
    errors = validate_prose_delimiters("Energy is $E = mc^2 without close.")
    assert any("Unbalanced '$'" in e for e in errors)

    # Leaked macro
    errors = validate_prose_delimiters(r"Unwrapped \frac{1}{2} outside math.")
    assert any("Leaked TeX macro" in e for e in errors)


def test_html_in_math_clean_mathematical_inequalities():
    # Mathematical inequalities must NOT trigger HTML infiltration errors
    assert len(validate_no_html_in_math(r"Summation $\sum_{i<j} J_{ij}$ is clean.")) == 0
    assert len(validate_no_html_in_math(r"Inequality \(x < y\) and \(a > b\) is valid.")) == 0
    assert len(validate_no_html_in_math(r"Bra-ket $\langle \psi | \hat{H} | \psi \rangle$ is valid.")) == 0
    assert len(validate_no_html_in_math(r"\sum_{i<j} \mathbf{S}_i \cdot \mathbf{S}_j")) == 0


def test_html_in_math_detects_infiltrated_tags():
    # Infiltrated HTML tags inside math delimiters
    errors1 = validate_no_html_in_math(r"Equation $\psi = <strong>C</strong> \bar{\psi}^T$ is broken.")
    assert len(errors1) > 0
    assert "HTML infiltration" in errors1[0]
    assert "strong" in errors1[0]

    # Infiltrated anchor links inside bracket math
    errors2 = validate_no_html_in_math(r"Term \(a href='/physics/subtopic/spin' class='subtopic-link' c /a\) is broken.")
    assert len(errors2) > 0
    assert any("subtopic-link" in e or "href" in e or "a" in e for e in errors2)

    # Infiltrated HTML entities inside SVG data-tex
    errors3 = validate_no_html_in_math(r'<svg data-tex="\psi = &lt;strong&gt;C&lt;/strong&gt; \bar{\psi}^T"></svg>')
    assert len(errors3) > 0
    assert any("strong" in e for e in errors3)


def test_validate_prose_delimiters_catches_html_in_math():
    errors = validate_prose_delimiters(r"The mass term $m \bar{\psi} <em>\psi</em>$ is invariant.")
    assert any("HTML infiltration" in e for e in errors)
