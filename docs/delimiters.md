# 📐 Math Delimiters Architecture & Governance in Terra Physics Lab

---

## 1. Executive Summary & Problem Statement

Across multiple development cycles, the repository has repeatedly encountered recurring test failures and regressions related to **narrative math delimiters** in formula definitions (`conceptual_definition`, `interpretation`, `limits_and_boundary`, `symmetry_origin`).

Attempts to resolve these issues via global heuristic regex scripts (`delimit_all_shard_prose.py`, `convert_narrative_delimiters.py`, `batch_auto_remediation.py`) have resulted in a **"delimiter whack-a-mole" cycle**:
1. A regex script attempts to normalize or wrap prose math across 14,613 shard formulas.
2. Because regular expressions cannot parse context-free grammars or ambiguous prose contexts (such as parenthetical notes, variable ranges, or punctuation), edge cases are corrupted (e.g. `=$\frac`, `}${\frac`, dangling `.$`, or double-wrapped `$\$...$\$`).
3. New test rules are written to detect those corruptions.
4. Another script is run to satisfy the new tests, triggering new edge-case corruptions elsewhere.

This document establishes the diagnostic root causes of this cycle, maps the competing forces across the codebase, and defines the permanent architectural resolution.

---

## 2. The Four Competing Forces

```
                          ┌────────────────────────────────────────────────────────┐
                          │               1. The Pytest Test Suite                 │
                          │  • Strips ONLY `$ ... $`                               │
                          │  • Assumes ANY backslash outside `$` is a leak         │
                          │  • Blind to standard LaTeX `\( ... \)` and `\[ ... \]` │
                          └──────────────────────────┬─────────────────────────────┘
                                                     │
                                     Fails when it sees `\( ... \)`
                                                     ▼
┌──────────────────────────────────────────────────────────────────┐
│             2. Batch Static Normalizers (Python / PHP)           │
│  • Force-replaces `\(` with `$`                                  │
│  • Guesses math boundaries with regex across 14,613 formulas     │
│  • Introduces edge-case corruptions (`=$\frac`, unclosed `$`)    │
└─────────────┬──────────────────────────────────────▲─────────────┘
              │                                      │
    Wraps text with `\(`               Fixes corruptions with regex
              │                                      │
              ▼                                      │
┌─────────────────────────────┐        ┌─────────────┴─────────────┐
│ 3. Frontend Explainer Engine│        │  4. Seeding & LLM Prompts │
│ • Runs 150 lines of regex   │        │ • Older prompts instructed│
│ • Converts bare vars & math │        │   LLMs to use `\( ... \)` │
│   into `\( ... \)` at       │        │ • Curators input standard │
│   runtime                   │        │   LaTeX `\( ... \)`       │
└─────────────────────────────┘        └───────────────────────────┘
```

### Force 1: Brittle, Single-Delimiter Test Assertions
The test suite operates under a strict, non-standard assumption that **only** `$...$` defines math mode in prose:
- In `tests/test_all_formulas_tex_syntax.py`:
  ```python
  text_no_math = re.sub(r"\$[^\$]+\$", "", text)
  match = tex_macro_check.search(text_no_math)
  assert match is None
  ```
- In `tests/test_formula_latex_integrity.py`:
  ```python
  parts = text.split("$")
  for i in range(0, len(parts), 2): # Assumes all even indices are non-math
      if re.search(r"\\(mathbf|vec|hat|mathcal|bar|dot|ddot|frac)\{[^}]+\}", parts[i]):
          corrupted_formulas.append(...)
  ```
When a formula uses standard LaTeX inline delimiters like `\(k_e = \frac{1}{4\pi\varepsilon_0}\)`, the tests perform a naive split on `$`. Because there are no `$` characters, the entire expression is evaluated as "outside math mode", triggering false-positive test failures.

### Force 2: Ingestion Prompts Mandating `\(`
Database ingestion and enrichment prompts historically mandated LaTeX bracket syntax:
- `scripts/seed_physics_database.py` (L102):
  ```python
  "Format any variables in text descriptions with LaTeX inline delimiters: \\( variable \\)."
  ```
- `scripts/auto_seed_gqs.py` (L54):
  ```python
  "Format variables in text with LaTeX inline delimiters: \\( variable \\)."
  ```
As a result, hundreds of formulas legitimately conform to the instructions they were given during generation, directly conflicting with the test suite.

### Force 3: Runtime Client-Side Delimiter Synthesis
In `public/js/equation_explainer.js`, the `wrapTextMathDelimiters(text)` function runs over 100 lines of regex logic dynamically in the browser:
- Detects bare Greek characters (`Γ` $\to$ `\(\Gamma\)`).
- Detects parenthesized variables (`(k_B T)` $\to$ `\((k_B T)\)`).
- Detects un-delimited fractions and operators (`\frac{...}{...}` $\to$ `\(\frac{...}{...}\)`).
- Protects existing `$$`, `$`, `\(`, and `\[` blocks.

Because the frontend already repairs and standardizes prose math at render time, the client experiences zero rendering degradation regardless of whether the backend shard uses `$`, `\(`, or bare mathematical symbols.

### Force 4: Static Shard Rewriting
Running global regular expressions against 14,613 JSON files is fundamentally flawed:
- Math vs English ambiguity: Is `"a"` a variable or the English indefinite article? Is `"(d)"` a label or a differential?
- Punctuation collisions: Quotation marks, commas, and apostrophes frequently cause naive regexes to invert delimiter bounds.
- Each successive normalizer script creates new synthetic anomalies.

---

## 3. Analysis of the Remaining Legacy Test Failures

Of the 3,133 tests currently in the test suite (with 3,121 passing and 12 failing):

| Failure Category | Count | Mechanism | Solution |
| :--- | :---: | :--- | :--- |
| **Raw HTML Markup** | 1 | `majorana-fermions-identity-be21f9b0` has `\psi = <strong>C</strong> \bar{\psi}^T` in its equation field. | Replace `<strong>C</strong>` with `\mathbf{C}` in the shard. |
| **Unbalanced Delimiters** | 1 | `gaussian-surface-733c4578` has 5 `$` signs in `symmetry_origin`. | Close the open delimiter in that specific formula. |
| **False-Positive Delimiter Tests** | 10 | The 8 sample failures in `test_all_formulas_tex_syntax.py` and the 2 full-corpus failures in `test_formula_latex_integrity.py` are caused by the test parser ignoring `\( ... \)` and `\[ ... \]`. | Update the test suite's math-stripping logic to recognize standard LaTeX delimiters. |

---

## 4. Architectural Rules & Governance

To permanently end the delimiter cycle, the repository adopts the following principles:

### Rule 1: Tests Must Be Delimiter-Agnostic
Both MathJax 3.x and modern LaTeX parsers support both `$ ... $` and `\( ... \)` for inline math, as well as `$$ ... $$` and `\[ ... \]` for display math.
The test suite's math-stripping preprocessor must strip **all standard math delimiters** before asserting whether macros are leaked:

```python
def strip_math_blocks(text: str) -> str:
    """Removes all valid display and inline LaTeX math blocks."""
    if not text or not isinstance(text, str):
        return ""
    # 1. Display math blocks
    t = re.sub(r"\\\[[\s\S]*?\\\]", "", text)
    t = re.sub(r"\$\$[\s\S]*?\$\$", "", t)
    # 2. Inline math blocks
    t = re.sub(r"\\\([\s\S]*?\\\)", "", t)
    t = re.sub(r"\$([^\$\n]+?)\$", "", t)
    return t
```

### Rule 2: Shard Storage Integrity Over Heuristic Guessing
- **Never** execute automated global regex substitutions on shards that attempt to guess whether bare English prose words represent variables.
- Shards should store clean, human-readable text with standard math formatting.
- Explicit syntax errors (unclosed brackets, unbalanced `$`, or literal HTML tags) should be targeted directly at the specific formula, not via unconstrained multi-file regex passes.

### Rule 3: Client-Side Leniency (Robustness Principle)
Per Postel's Law (*"Be conservative in what you send, be liberal in what you accept"*):
- The data layer stores valid LaTeX and text.
- The client-side `wrapTextMathDelimiters()` provides rendering fault tolerance for edge cases.
- The CI gates prevent genuine corruptions (broken JSON, control characters, unclosed delimiters) without policing stylistic delimiter preferences (`$` vs `\(`).

### Rule 4: Unified Ingestion Standard
All future generator scripts, curation prompts, and automated enrichment tools must use a single unified standard:
- Primary inline math standard: `$ ... $`
- Secondary accepted standard: `\( ... \)`
- Generator instructions must never instruct models to omit math delimiters entirely.

---

## 5. Centralized Modular Architecture ("Single Point of Flow")

To permanently eliminate the delimiter whack-a-mole cycle, delimiter processing must be consolidated into a **single, unified pipeline** across the repository rather than being handled by disconnected regex snippets.

```
                  ┌──────────────────────────────────────────────┐
                  │                 WRITE PATH                   │
                  │  (Seed Scripts, Curator Edits, Repair Tools) │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │   SINGLE GATEWAY: MathNormalizer::clean()    │
                  │   • Normalizes inline math to $...$          │
                  │   • Balances unclosed delimiters             │
                  │   • Prevents HTML / mangled control chars    │
                  └──────────────────────┬───────────────────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         ▼                               ▼
                 [ 256 JSON Shards ]            [ MariaDB Store ]
                         ▲                               │
                         │                               ▼
┌────────────────────────┴────────┐      ┌──────────────────────────────┐
│       VERIFICATION PATH         │      │          READ PATH           │
│    scripts/lib/delimiters.py    │      │ public/js/MathProseFormatter │
│  • Single test helper           │      │  • Extracted from Explainer  │
│  • Uses identical regex parser  │      │  • Shared by Inspector,      │
│  • Tests & CI import THIS ONLY  │      │    Explainer, Graph tooltips │
└─────────────────────────────────┘      └──────────────────────────────┘
```

### The Three Centralized Pillars

#### 1. The Write Gateway (`PhysicsService::saveFormula` / `MathNormalizer.php`)
Every formula modification—whether initiated via web curator, ingestion script, or CLI tool (`scripts/fixlatex`)—must funnel through a single write sanitizer before being committed to JSON shards or MariaDB:
- **Tolerant Ingress**: Accepts both `$ ... $` and `\( ... \)`.
- **Canonical Normalization**: Standardizes stored inline math to `$ ... $`.
- **Integrity Validation**: Rejects or balances unclosed delimiters, strips HTML tags (`<strong>` $\to$ `\mathbf`), and strips binary control collisions (`\x08ar` $\to$ `\bar`).
- **Guarantee**: No unvalidated or corrupted delimiter pattern can physically enter storage.

#### 2. The Shared Test & CI Module (`scripts/lib/delimiters.py`)
Remove all custom regex splitters from individual test files (`test_all_formulas_tex_syntax.py`, `test_formula_latex_integrity.py`, `integrity_shield.py`).
- Consolidate regex parsing into a single helper library:
  ```python
  from scripts.lib.delimiters import strip_math_blocks, validate_prose_delimiters
  ```
- Any future refinements or delimiter additions are made in **one file**, immediately aligning both the pre-push gatekeeper and the pytest regression net.

#### 3. The Centralized Presentation Module (`MathProseFormatter.js`)
Currently, `wrapTextMathDelimiters()` is locked inside the 5,000-line `equation_explainer.js`, while `formula_inspector.js` and `formula_graph.js` lack access to it.
- Extract this runtime formatter into `public/js/modules/MathProseFormatter.js`.
- Export a standardized `formatProseMath(text)` function used across all frontend surfaces before MathJax typesets.

---

## 6. Golden Principle: "Tolerant Ingress, Canonical Storage"

1. **Authors & Tools are Free**: Curators and LLMs can write standard LaTeX (`\(`) or MathJax (`$`) without worrying about internal storage quirks.
2. **The Funnel Enforces Consistency**: The centralized write gateway converts all inputs into canonical `$ ... $` for storage.
3. **Tests Verify the Standard**: The shared CI module verifies conformance without false positives.
4. **No Global Batch Rewriting**: Shards are never subjected to unconstrained global regex search-and-replace scripts again.

---

## 7. Verification Checklist & Implementation Status

- [x] **All opened `$` or `\(` delimiters properly closed**: Verified across all 14,613 formulas in all 256 shards.
- [x] **All equations free of HTML tags (`<a>`, `<strong>`, `<code>`)**: `majorana-fermions-identity-be21f9b0` sanitized; 0 HTML tags remain.
- [x] **Pre-push gatekeeper (`integrity_shield.py`) green**: 100% Manifold Closure, valid AST mappings, all shields secure.
- [x] **Pytest regression suite at 100.0%**: 3,141 / 3,142 tests passing (0 failures, 1 skipped).
- [x] **Shared Delimiter Module deployed**: `scripts/lib/delimiters.py` imported universally by `test_all_formulas_tex_syntax.py` and `test_formula_latex_integrity.py`.
- [x] **Write Gateway enforced**: `PhysicsService::saveFormula()` canonicalizes prose delimiters and strips equation HTML tags before committing to shards or MariaDB.
- [x] **Frontend Formatter modularized**: `public/js/math_prose_formatter.js` created and loaded across the Equation Explainer, Formula Inspector, and Graph Tooltips.


