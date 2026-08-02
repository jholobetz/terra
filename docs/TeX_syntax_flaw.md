# TeX Syntax Flaw Diagnostic & Permanent Resolution Plan

## Overview & Diagnostic Scan Results
During diagnostic testing of SVG rendering errors across the **Equation Explainer** feature in Terra, a comprehensive scan was executed across all **13,731 physics formulas** stored in the 256 JSON shard files (`app/config/content/formulas/`) and the MariaDB `formulas` table.

- **Total Formulas Scanned**: 13,731
- **Total Formulas with TeX Corruptions**: 3,940 (~28.7%)
- **Primary Symptom**: Clicking equation links in Equation Explainer triggers MathJax SVG rendering errors when formulas contain corrupted LaTeX delimiters in narrative fields.

---

## Root Causes of TeX Corruptions
Historical data ingestion and automated LLM generation introduced four recurring patterns of TeX math corruption across `conceptual_definition`, `interpretation`, `limits_and_boundary`, `symmetry_origin`, `intuitive_summary`, and `semantic_variables`:

1. **Unclosed / Odd `$ ` Delimiters**:
   - *Example*: `The electric field vector $\mathbf{E} is squared in magnitude...`
   - *Issue*: Missing closing `$` causes entire paragraphs of plain text to bleed into math mode, throwing SVG parser exceptions.

2. **Inverted & Nested Math Spans**:
   - *Example*: `$\frac{d}{dx} \left[ p(x) $\frac{dy}{dx}$ \right] + q(x)y = 0$` or `$|$\mathbf{E}$|^2$`
   - *Issue*: Dollar signs nested inside existing TeX brackets (`\left[ ... \right]`) toggle math mode off and on repeatedly.

3. **Mangled LaTeX Macro Expressions**:
   - *Example*: `\sqrt${-g}`, `$g_{$\mu$ u}$`, `\to'`, `'+$\pi^0$'`
   - *Issue*: Malformed macro sub-expressions, broken subscript indices (`u` instead of `\nu`), or unescaped single quotes around symbols.

4. **Split Vector & Variable Names**:
   - *Example*: `\\delta \\mathbf {Z}(t)` or `p $\to$ e^+ + $\pi^0$`
   - *Issue*: Spaces inside `\\mathbf {Z}` break key lookup in `semantic_variables`, while split math blocks break equation component matching.

---

## 4-Step Permanent Resolution Plan

### Step 1: Global TeX AST Repair Engine
Build a standalone PHP/Python repair engine that iterates through all 13,731 formulas across all 256 JSON shards and MariaDB records to automatically balance and repair TeX math blocks:
- Auto-balance odd `$` counts around single LaTeX symbols and expressions.
- Strip nested `$` signs inside TeX macro blocks (`\left[ ... \right]`, `\frac{...}{...}`, `\sqrt{...}`).
- Fix macro corruptions (`\sqrt${...}` $\to$ `\sqrt{...}`, `$g_{$\mu$ u}$` $\to$ `$g_{\mu \nu}$`, `\to'` $\to$ `\to`).
- Normalize variable keys in `semantic_variables` to match cleaned LaTeX tokens.

### Step 2: Automated Headless MathJax Verification
Run a headless MathJax rendering validator across all formula fields in the database:
- Synthetically parse every narrative field.
- Flag any edge cases that produce MathJax syntax warnings or SVG errors for targeted auto-correction.

### Step 3: Atomic Shard & Database Re-Sync
- Write the sanitized formula fields back to their respective JSON shards in `app/config/content/formulas/`.
- Execute a single bulk `UPDATE` transaction across MariaDB to ensure the database matches the shard files.

### Step 4: Permanent CI Linter Integration
Add a automated test suite (`tests/test_all_formulas_tex_syntax.py` / `tests/test_topic_variable_hover.py`):
- Run in CI to verify that 100% of formulas in the repository compile cleanly into valid SVG without math syntax errors.
