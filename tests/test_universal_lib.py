#!/usr/bin/env python3
"""
tests/test_universal_lib.py

Unit tests verifying the canonical lib/ package architecture:
- lib.math (delimiters and AST lexer)
- lib.cas (SymPy symbolic computation engine)
- lib.data (manifold closure reference data)
"""

import os
import json
import pytest
from lib.math import (
    strip_math_blocks,
    find_html_in_math,
    count_unescaped_dollars,
    extract_math_blocks,
    TerraLexer,
    TokenType,
)
from lib.cas import evaluate_symbolic, latex_to_sympy_str


def test_lib_math_delimiters():
    text = "The Hamiltonian $\\hat{H} \\Psi = E \\Psi$ governs dynamics."
    stripped = strip_math_blocks(text)
    assert "\\hat{H}" not in stripped
    assert "governs dynamics." in stripped
    assert count_unescaped_dollars(text) == 2


def test_lib_math_lexer():
    lexer = TerraLexer()
    tokens = lexer.pass1_tokenize("Energy $E = mc^2$ is invariant.")
    assert len(tokens) == 3
    assert tokens[0].type == TokenType.PROSE
    assert tokens[1].type == TokenType.MATH_INLINE
    assert tokens[1].value == "E = mc^2"
    assert tokens[2].type == TokenType.PROSE


def test_lib_cas_engine():
    res = evaluate_symbolic("E = m c^2")
    assert res["success"] is True
    assert "m" in res["variables"]
    assert "c" in res["variables"]


def test_lib_data_unmapped_prose_equations():
    data_path = os.path.join("lib", "data", "unmapped_prose_equations.json")
    assert os.path.exists(data_path), "lib/data/unmapped_prose_equations.json must exist"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "total_unique" in data
    assert "closure_percent" in data
    assert data["unmapped_equations_count"] == 0
