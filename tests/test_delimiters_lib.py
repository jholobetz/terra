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
