"""
🪐 Project Terra - Mathematical Infrastructure
Provides TeX/Markdown AST lexing, delimiter normalization, and formatting checks.
"""

from .delimiters import (
    strip_math_blocks,
    find_html_in_math,
    count_unescaped_dollars,
    validate_narrative_delimiters,
    extract_math_blocks,
)
from .lexer import (
    TerraLexer,
    TokenType,
    TeXNodeType,
    Token,
    TeXNode,
)

__all__ = [
    "strip_math_blocks",
    "find_html_in_math",
    "count_unescaped_dollars",
    "validate_narrative_delimiters",
    "extract_math_blocks",
    "TerraLexer",
    "TokenType",
    "TeXNodeType",
    "Token",
    "TeXNode",
]
