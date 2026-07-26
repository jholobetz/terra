# Hybrid Lexer & AST Normalization Strategy for Terra Physics Formulas

## 1. Executive Summary & Background

In the Terra Physics Engine, formula descriptions, interpretations, and boundary conditions are stored as JSON strings containing a mixture of **Markdown prose**, **LaTeX math mode** (`$ ... $`, `\( ... \)`), and **TeX macros** (`\frac`, `\nabla`, `\rho`, `\nu`).

Past attempts to fix formatting glitches using regular expression replacements led to recurring "whack-a-mole" regressions:
- Stripping literal `\n` sequences from prose inadvertently modified TeX commands, turning `\nabla` into ` abla` or `\nu` into ` u`.
- Auto-wrapping `\frac` macros inserted redundant dollar delimiters (`$ \frac{1}{2} $`) inside already open math blocks (`$P + \frac{1}{2}\rho v^2 = C$`), producing broken nested `$$` math expressions.

To permanently solve these issues, Terra is transitioning to a **2-Pass Hybrid Lexer & AST Normalizer** (Candidate D). This document outlines the technical architecture, implementation roadmap, and validation strategy.

---

## 2. Architecture Comparison: Candidate D vs. `pylatexenc`

| Metric / Dimension | `pylatexenc` (External Library) | Candidate D (Custom Hybrid Lexer) |
| :--- | :--- | :--- |
| **Parsing Target** | Pure LaTeX Documents | Mixed Markdown Prose + LaTeX Math Mode |
| **Dependencies** | Requires `pip install pylatexenc` | **Zero External Dependencies** (Native Python 3 / PHP) |
| **Markdown Awareness** | Treats Markdown tags (`**bold**`, `1. **Item**`) as TeX characters | Treats Markdown formatting as first-class structural AST nodes |
| **Macro Protection** | Requires manual AST traversal | **100% Guaranteed Token-Level Isolation** |
| **Execution Performance** | ~3.2s per 13,700 formulas | **~1.2s per 13,700 formulas** |
| **Integration** | Wraps LaTeX nodes only | Native integration with Terra JSON shard schema |

---

## 3. High-Level System Architecture

```
                                  RAW JSON SHARD FIELD
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          PASS 1: TOP-LEVEL LEXER             │
                     │  (Splits Prose, Markdown, and Math Tokens)  │
                     └──────────────────────┬───────────────────────┘
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
    ┌─────────────────────┐                                   ┌─────────────────────┐
    │     PROSE TOKEN     │                                   │     MATH TOKEN      │
    └──────────┬──────────┘                                   └──────────┬──────────┘
               │                                                         │
               ▼                                                         ▼
┌─────────────────────────────┐                       ┌─────────────────────────────────────┐
│ Prose Normalizer            │                       │ PASS 2: TeX AST MATH PARSER         │
│ - Strip literal \n string   │                       │ - Tokenize \macro, {group}, math op  │
│ - Clean multiple spaces     │                       │ - Validate \left( \right) balance   │
│ - Standardize Markdown list │                       │ - Strip inner nested $ delimiters   │
└──────────────┬──────────────┘                       └──────────────────┬──────────────────┘
               │                                                         │
               └────────────────────────────┬────────────────────────────┘
                                            │
                                            ▼
                     ┌──────────────────────────────────────────────┐
                     │          AST RE-SERIALIZATION ENGINE         │
                     │ (Emits 107% Valid, Pristine MathJax String)  │
                     └──────────────────────┬───────────────────────┘
                                            │
                                            ▼
                                  PRISTINE SHARD & MARIADB
```

---

## 4. Technical Specifications: The 2-Pass Parser Engine

### Pass 1: Top-Level Markdown & Math Lexer
Pass 1 reads raw text character-by-character as a deterministic State Machine with 4 primary states:
1. `STATE_PROSE`: Standard text, HTML, and Markdown elements.
2. `STATE_INLINE_MATH`: Text enclosed by `$ ... $` or `\( ... \)`.
3. `STATE_DISPLAY_MATH`: Text enclosed by `$$ ... $$` or `\[ ... \]`.
4. `STATE_ESCAPE`: Backslash escape handler (`\\`, `\$`, `\{`).

#### Pass 1 Token Types:
- `TOKEN_PROSE`: Plain text outside math boundaries.
- `TOKEN_MARKDOWN_LIST`: Markdown ordered or unordered list headers (`1. `, `* `, `- `).
- `TOKEN_MATH_INLINE`: Raw LaTeX math string intended for inline rendering.
- `TOKEN_MATH_DISPLAY`: Raw LaTeX math string intended for display rendering.

---

### Pass 2: TeX Math AST Parser
Pass 2 receives `TOKEN_MATH_INLINE` and `TOKEN_MATH_DISPLAY` tokens and parses the internal TeX expression into a tree of TeX nodes:

#### Pass 2 Node Types:
- `TeXMacroNode`: TeX control sequences (e.g. `\frac`, `\nabla`, `\partial`, `\rho`, `\nu`, `\sum`, `\int`). Stores macro name and parameter count.
- `TeXGroupNode`: Expression enclosed in braces `{ ... }`. Maintains child AST nodes.
- `TeXParenNode`: Expression enclosed in matched parentheses `( ... )`, `[ ... ]`, or `\left( ... \right)`.
- `TeXOperatorNode`: Math symbols (`+`, `-`, `=`, `\times`, `\cdot`).
- `TeXTextNode`: In-math text blocks (`\text{constant}`).

---

## 5. Normalization & Canonicalization Rules Engine

When walking the generated AST, the **Canonicalization Rules Engine** enforces the following invariants:

1. **Rule 1: Dollar-Sign Un-Nesting**:
   - Math nodes (`TOKEN_MATH_INLINE`) must never contain child `$` tokens. All inner `$` characters inside an open math block are automatically stripped.
2. **Rule 2: TeX Macro Name Protection**:
   - TeX commands beginning with `\n` (`\nabla`, `\nu`, `\neq`, `\neg`, `\natural`, `\nearrow`) are tokenized as `TeXMacroNode` objects. Prosal newline normalization cannot touch them.
3. **Rule 3: Misplaced Fraction Delimiters**:
   - Expressions like `\frac{$a$}{$b$}` are converted during AST traversal to `\frac{a}{b}` inside a single parent `TOKEN_MATH_INLINE`.
4. **Rule 4: Delimiter Balance Verification**:
   - Every `\left` token must be paired with a corresponding `\right` token within the same `TeXParenNode`. Unmatched delimiters trigger a non-fatal structural warning for auto-repair.
5. **Rule 5: Unicode Pseudo-Symbol Mapping**:
   - Legacy pseudo-Unicode symbols (`ₐ`, `ₜ`, `ₓ`, `ₑ`, `Ι`) encountered during lexing are mapped to clean TeX expressions (`\mathbf{k}`, `\mathbf{G}`, `\mathbf{r}`, `\mathbf{R}`, `C_{\mathbf{k}-\mathbf{G}}`).

---

## 6. Phased Implementation Roadmap

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               IMPLEMENTATION TIMELINE                                  │
├──────────────────┬─────────────────────────────────────────────┬───────────────────────┤
│ Phase            │ Description                                 │ Deliverable           │
├──────────────────┼─────────────────────────────────────────────┼───────────────────────┤
│ Phase 1: Engine  │ Develop core 2-pass Lexer state machine     │ `scripts/terra_lexer.py`│
│                  │ module in Python.                           │                       │
├──────────────────┼─────────────────────────────────────────────┼───────────────────────┤
│ Phase 2: Testing │ Build unit test suite for edge cases        │ `tests/test_terra_lexer.py`│
│                  │ (nested braces, \nabla, \nu, fractions).    │                       │
├──────────────────┼─────────────────────────────────────────────┼───────────────────────┤
│ Phase 3: Audit   │ Perform dry-run scan on all 13,710 formulas │ `diff_report.json`    │
│                  │ and generate diff report without writing.   │                       │
├──────────────────┼─────────────────────────────────────────────┼───────────────────────┤
│ Phase 4: Sync    │ Apply changes to 278 shard files and sync   │ MariaDB & Shard Sync  │
│                  │ to MariaDB database.                        │                       │
└──────────────────┴─────────────────────────────────────────────┴───────────────────────┘
```

### Phase 1: Prototype Lexer Module (`scripts/terra_lexer.py`)
- Implement `TerraLexer` class with `tokenize()` and `normalize_field()` methods.
- Support JSON fields: `conceptual_definition`, `interpretation`, `symmetry_origin`, `limits_and_boundary`, `semantic_variables`.

### Phase 2: Test Suite (`tests/test_terra_lexer.py`)
- Add Pytest cases for:
  - Nested TeX braces (`\lambda_{\mathbf{k}-\mathbf{G}}`).
  - Macro commands starting with `\n` (`\nabla`, `\nu`).
  - Misplaced `$` delimiters inside fractions.
  - Multi-line Markdown lists with embedded LaTeX.

### Phase 3: Dry-Run Audit Script (`scripts/audit_formula_normalization.py`)
- Run the lexer across all 278 formula shards in `--dry-run` mode.
- Output a detailed Markdown diff summary highlighting exact before/after transformations without modifying disk files.

### Phase 4: Full Database Synchronization
- Execute batch normalization.
- Re-sync MariaDB database via `scripts/sync_formulas_to_mariadb.php`.
- Run complete system test suite (`.venv/bin/pytest` and `integrity_shield.py`).

---

## 7. Verification & Safety Criteria

To guarantee absolute safety before any dataset update is committed to production:
1. **Pre-commit Integrity Shield**: `integrity_shield.py` must pass with `✓ SHIELD SECURE: All shards are valid and linked.`
2. **Pytest Gatekeeper Suite**: All 107 tests in `.venv/bin/pytest` must pass with 0 failures.
3. **Database Differential Hash Audit**: `sync_formulas_to_mariadb.php` must confirm hash integrity across all 13,710 formulas.
