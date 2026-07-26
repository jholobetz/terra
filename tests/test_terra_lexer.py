"""
Phase 2 Test Suite for Terra Hybrid Lexer & AST Normalizer
----------------------------------------------------------
Verifies top-level Pass 1 (Prose vs. Math isolation) and Pass 2 (TeX AST math normalizations).
"""

import pytest
import re
from scripts.terra_lexer import TerraLexer, TokenType


@pytest.fixture
def lexer():
    return TerraLexer()


def test_pass1_prose_and_inline_math_isolation(lexer):
    text = "Density is $\\rho$ and velocity is $\\mathbf{u}$."
    tokens = lexer.pass1_tokenize(text)

    # Tokens: PROSE("Density is "), MATH("\rho"), PROSE(" and velocity is "), MATH("\mathbf{u}"), PROSE(".")
    assert len(tokens) == 5
    assert tokens[0].type == TokenType.PROSE
    assert tokens[0].value == "Density is "
    assert tokens[1].type == TokenType.MATH_INLINE
    assert tokens[1].value == "\\rho"
    assert tokens[2].type == TokenType.PROSE
    assert tokens[2].value == " and velocity is "
    assert tokens[3].type == TokenType.MATH_INLINE
    assert tokens[3].value == "\\mathbf{u}"
    assert tokens[4].type == TokenType.PROSE
    assert tokens[4].value == "."


def test_pass1_display_math_isolation(lexer):
    text = "The energy equation: $$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$$ holds."
    tokens = lexer.pass1_tokenize(text)

    assert len(tokens) == 3
    assert tokens[0].type == TokenType.PROSE
    assert tokens[1].type == TokenType.MATH_DISPLAY
    assert tokens[1].value == "\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0"
    assert tokens[2].type == TokenType.PROSE


def test_protected_n_macros_preserved(lexer):
    sample = "Incompressible flow (\\n\\rho = \\text{constant}), where \\nabla \\cdot \\mathbf{v} = 0."
    normalized = lexer.normalize_text(sample)

    assert "\\nabla" in normalized
    assert "\\rho" in normalized
    assert re.search(r'\babla\b', normalized) is None


def test_inner_dollar_un_nesting(lexer):
    sample = "$P + $\\frac{1}{2}\\rho v^2$ = C$"
    normalized = lexer.normalize_text(sample)

    # Output should have single outer $ $ with inner $ removed
    assert normalized == "$P + \\frac{1}{2}\\rho v^2 = C$"


def test_misplaced_frac_dollar_sanitization(lexer):
    sample = "$\\frac{$a$}{$b$}$"
    normalized = lexer.normalize_text(sample)

    assert normalized == "$\\frac{a}{b}$"


def test_unicode_pseudo_subscript_mapping(lexer):
    sample = "Vector coefficient C_{ₐ-ₜ} and momentum ₓ."
    normalized = lexer.normalize_text(sample)

    assert "$C_{\\mathbf{k}-\\mathbf{G}}$" in normalized
    assert "$\\mathbf{r}$" in normalized


def test_formula_dict_normalization(lexer):
    formula = {
        "conceptual_definition": "Defines density \\n\\rho and gradient \\nabla.",
        "interpretation": "States $\\frac{\\partial \\rho}{\\partial t} > 0$.",
        "semantic_variables": {
            "\\rho": {
                "name": "Density",
                "description": "Fluid density \\n\\rho."
            }
        }
    }

    norm_formula, modified = lexer.normalize_formula(formula)

    assert modified is True
    assert "\\nabla" in norm_formula["conceptual_definition"]
    assert "\\rho" in norm_formula["semantic_variables"]["\\rho"]["description"]
