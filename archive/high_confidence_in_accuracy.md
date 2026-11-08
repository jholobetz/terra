# Formula Catalog Data Confidence & Accuracy Audit (`docs/high_confidence_in_accuracy.md`)

**Date:** 2026-11-07  
**Context:** Following the complete remediation of all 257 corrupted `equation` strings, 6 explicit garbage placeholders, 1,151 prose control-character corruptions, and 25 zero-affinity parent–child links ([`archive/corrupted_strings.md`](../archive/corrupted_strings.md)), this document evaluates the central question:

> **"Now that we have corrected the corrupted strings, do we have high confidence in the accuracy of the data? Everything?"**

The honest answer is **no — not everything.**

We now have **high confidence in the syntactic integrity of the `equation` strings and the structural shape of the graph**, because those layers have been audited, repaired, and locked behind permanent CI gates. However, applying our Anti-Goodhart standard ([`docs/mandate.md`](mandate.md)) to the **rest of the formula metadata and derivation links** across all **14,681 formulas** reveals **five specific areas where the data is still heuristic, templated, or unverified.**

---

## 1. What We DO Have High Confidence In Now

1. **LaTeX Equation Strings (`14,681 / 14,681` — 100%)**:
   * `0` prose-bleed strings, `0` raw MathML fragments, `0` truncated backslash commands (` tial`, `extit{`, `abla`, `imes`, `au_`), `0` unbalanced braces, and `0` unescaped ASCII control characters (`\r`, `\t`, `\x08`, `\x0c`, `\x89`).
   * Locked permanently by [`is_corrupted_equation()`](../scripts/maintenance/audit_lineage_health.py) and [`test_sitewide_zero_corrupted_equations_and_affinity()`](../tests/test_auto_draft_lineage.py).
2. **Graph Topology & Hub Shape (`256 / 256` Shards — 100%)**:
   * `0` circular loops, `100%` reciprocal `parent_formula_id` $\leftrightarrow$ `subcomponents` closure, `0` overloaded star-hubs (max direct children per node is `19`, under the $\le 25$ cap), and `0` zero-affinity parent–child links.
   * Locked permanently by [`has_parent_child_affinity()`](../scripts/maintenance/audit_lineage_health.py) and [`verify_strict_invariants()`](../scripts/maintenance/run_project_assessment.py).
3. **Multi-Step Proofs (`103` Formulas — 100%)**:
   * All 103 multi-step derivation proofs (`derivation_steps`) are algebraically and structurally verified across all 12 canonical domains via [`tests/test_derivation_steps.py`](../tests/test_derivation_steps.py).

---

## 2. Where We Do NOT Have High Confidence Yet (The 5 Remaining Data Liabilities)

### A. 99.1% of Derivation Links Are Still Heuristic, Not Proven (`14,005 / 14,137` links)
From the `Lineage Confidence` breakdown in [`scripts/maintenance/audit_lineage_health.py`](../scripts/maintenance/audit_lineage_health.py):
* **Curated / Verified Links**: `132` (`0.9%`)
* **Heuristic Links**: `14,005` (`99.1%`)
* **Root Definitions / Axioms**: `574`

Eliminating "zero-affinity" links guarantees that a parent and child live in the **same subtopic neighborhood and share mathematical symbols**—so metric prefixes (`10^{-15}`) are no longer parented onto the Eötvös parameter. **However**, sharing a subtopic and a symbol does *not* prove that Equation B is mathematically derived from Equation A, nor does it guarantee the arrow isn't pointing backward (Child $\to$ Parent) between two equations in the same article.

### B. 858 Formulas Have Copy-Pasted Boilerplate Titles & Metadata (`5.8%` of catalog)
An earlier automated ingestion script generated **858 formulas** (`*-identity-*` slugs) using hardcoded placeholder strings just to pass the 20-character length check in [`calculate_lhi()`](../scripts/maintenance/audit_lineage_health.py):
* **783 formulas (`5.3%`)** literally have `"title": "Custom Physical Relation"` instead of the actual physical name of the equation.
* **858 formulas (`5.8%`)** share the exact same word-for-word copy-pasted strings:
  * `"symmetry_origin"`: `"Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance across inertial frames."`
  * `"limits_and_boundary"`: `"Subject to asymptotic boundary conditions and non-relativistic conservation limits."` (even on relativistic or quantum formulas where *"non-relativistic conservation limits"* is physically false!).

### C. 2,833 "Formulas" (`19.3%`) Are Standalone Symbols or Expressions, Not Equations
Nearly **1 in 5 records (`2,833 / 14,681`)** contains **no relational operator** (`=`, `\equiv`, `\approx`, `\sim`, `\propto`, `\to`, `<`, `>`).
* They are bare variable symbols (`m_2`, `q_i`, `\psi^*`), standalone numbers (`10^7`, `1/4`), or isolated term fragments (`\sin\phi`, `d\dot{q}^i`) that were scraped out of inline `$ ... $` prose blocks during an earlier campaign to hit "100% prose equation manifold closure."
* Treating `m_2` (*"Inertial Mass of the Second Particle"*) as a standalone "formula" with a parent derivation, symmetry origin, and boundary limit inflates the formula count and forces artificial metadata onto single symbols.

### D. 296 Formulas Have Desynchronized `semantic_variables` (`2.0%` of catalog)
In **296 formulas**, **none** of the variable keys listed in `"semantic_variables"` actually appear in the `"equation"` string:
* Some of these are from the **257 equations just repaired** (where `"equation"` was restored to its canonical LaTeX, while `"semantic_variables"` still reflects tokens scraped from the old corrupted string or a different notation).
* Others have notation mismatches between `"equation"` (e.g., `\boldsymbol{\tau}`) and `"semantic_variables"` (e.g., `F`, `r`).

### E. 5,535 Formulas (`37.7%`) Have No Symbolic CAS Validation
Across all `14,681` formulas, the `cas_validation` status distribution is:
* **`HOMOGENEOUS` (Verified Equations)**: `5,924` (`40.4%`)
* **`DIMENSIONAL_EXPRESSION` (Terms/Fragments)**: `3,222` (`21.9%`)
* **`MISSING` / `UNVERIFIED`**: `5,535` (`37.7%`)

---

## 3. Summary Confidence Matrix

| Data Layer | Confidence Level | Current Empirical Reality |
| :--- | :--- | :--- |
| **LaTeX Equation Syntax (`equation`)** | **High (`100%`)** | All `14,681` equations are syntactically valid LaTeX with `0` prose bleed or control-char corruption. |
| **Graph Shape & Affinity Constraints** | **High (`100%`)** | `0` loops, `0` overloaded hubs ($>25$), `0` cross-domain zero-affinity links. |
| **Variable Dictionary Alignment (`semantic_variables`)** | **Moderate (`98.0%`)** | `296` formulas have `semantic_variables` keys that do not match the `equation` string. |
| **Titles, Symmetry & Boundary Prose** | **Moderate (`94.2%`)** | `783` formulas are titled `"Custom Physical Relation"` and `858` have copy-pasted boilerplate symmetry/limit text. |
| **CAS Dimensional Verification** | **Moderate (`62.3%`)** | `5,924` equations + `3,222` expressions verified; `5,535` formulas (`37.7%`) have no `cas_validation` record. |
| **True Mathematical Derivation (`parent_formula_id`)** | **Low-to-Moderate** | `132` links are curated/verified (`0.9%`); `14,005` (`99.1%`) are heuristic neighborhood/symbol matches. |

---

## 4. Recommended Next Remediation Priorities

1. **Resynchronize the 296 Desynchronized `semantic_variables` Records**:
   * Audit and repair the 296 formulas where `semantic_variables` keys do not appear in `equation`, and add a CI check ensuring every formula's `semantic_variables` keys correspond to actual symbols in `equation`.
2. **Replace the 783 `"Custom Physical Relation"` Titles & 858 Boilerplate Symmetry/Boundary Strings**:
   * Derive authentic, equation-specific titles from the subtopic context and equation structure, and purge the false copy-pasted boilerplate strings (`"Subject to asymptotic boundary conditions and non-relativistic conservation limits."`).
3. **Separate True Equations (`11,848`) from Sub-Expression / Symbol Definitions (`2,833`)**:
   * Explicitly classify standalone expressions/symbols (`record_type: "symbol_or_term"` vs. `"equation"`) so single variables (`m_2`, `q_i`) and numbers (`10^7`) are not conflated with physical laws.
4. **Expand CAS Verification Coverage & Algebraic Parent–Child Proofs**:
   * Run `scripts/cascheck` across the remaining `5,535` unverified formulas and upgrade heuristic parent–child links to `cas_verified` wherever SymPy can algebraically verify the relation.
