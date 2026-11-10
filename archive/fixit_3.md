# 🛠️ Formula Manifold Audit III: Residual Blind Spots & Self-Check Roadmap (`docs/fixit_3.md`)

**Audit Date**: 2026-11-08  
**Scope**: Full 256-shard deep scan across all **14,684** formulas following completion of [`archive/fixit_2.md`](../archive/fixit_2.md) (Priorities 1–4, commit `fb2cdc6e6`).

---

## ✅ Baseline: What Is Already Locked Down (`archive/fixit_2.md`)

All priorities from `archive/fixit_2.md` are **100% resolved and gated** by [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) and [`app/config/formula.schema.json`](../app/config/formula.schema.json):
- **0** placeholder formula titles (`"Custom Physical Relation"`, `"Technical Relation"`, `"Unknown Formula"`).
- **0** generic variable fallback labels (`"Physical Quantity"`, `"Constant or Parameter"`, `"Dimensionless Parameter"`, `"Vector / Tensor Component"`, `"Differential Quantity"`, `"State Function or Operator"`).
- **0** `\text{...}` ghost-word variable keys or bare LaTeX structural commands (`\frac`, `\int`, `\left`, `\right`, etc.) in `semantic_variables`.
- **0** mechanical narrative prefixes (`"Physically, the ... governs..."`, `"Specifically, its mathematical structure..."`, `"At its foundation, this relation expresses..."`).
- **0** duplicate `conceptual_definition == interpretation` or `symmetry_origin == intuitive_summary` fields.
- **0** cross-hub domain bleed sentences or malformed `semantic_variables` brace/backslash keys.

---

## 🔍 5 Remaining Areas of Concern (Live Audit Across 14,684 Formulas)

### ✅ Priority 1: Self-Referential Variable Definitions & Parameterized Fallbacks (`2,347` variables across `839` formulas) — *COMPLETED*

* **What Was Resolved**:
  * Resolved all **2,131** self-referential / 1-character variable entries (`name == key`) plus **216** parameterized fallback strings (`"Physical Quantity (\pi)"`, `"Physical Quantity (z)"`, etc.) = **2,347** variables across **839 formulas** in **239 shards**.
  * Normalized **223** malformed variable keys (`'I_hat'` $\to$ `'\hat{I}'`, `'T^munu'` $\to$ `'T^{\mu\nu}'`, `'\(\mathbf{E}\)'` $\to$ `'\mathbf{E}'`, `'lambda_1'` $\to$ `'\lambda_1'`, etc.).
  * Locked in permanent regression assertions in [`test_semantic_variables_schema_strict()`](../tests/test_formula_latex_integrity.py) forbidding `vname == key`, `len(vname) <= 1`, and parameterized fallback substrings (`r"\b(Physical Quantity|Constant or Parameter|...)\b"`).

---

### ✅ Priority 2: Hex-Byte Corrupted Equations & Residual Placeholder Records (`5` formulas) — *COMPLETED*

* **What Was Resolved**:
  1. [`quantum-wave-function-symbol-a70d1c54`](../app/config/content/formulas/85/shard_85.json) (`The Quantum Wave Function Symbol $\Psi$`):
     * Repaired `equation` from `"0xC20xA00xCF0x88"` to `"\\Psi(\\mathbf{r}, t)"`, pruned hex-artifact variables (`x`, `C`, `A`, `F`), added `\mathbf{r}` and `t`, and updated `cas_validation` to `[\text{L}^{-3/2}]`.
  2. [`plane-wave-phase-argument-03b4af97`](../app/config/content/formulas/9b/shard_9b.json) (`Quantum Mechanical Plane Wave Spatial Phase Argument`):
     * Repaired `equation` from `"0xE20x800x930xC20xA0"` to `"\\frac{\\mathbf{p} \\cdot \\mathbf{r}}{\\hbar}"`, pruned hex-artifact variables (`x`, `E`, `C`, `A`), and updated `cas_validation` to `[1] \text{ (Dimensionless)}`.
  3. [`momentum-position-dot-product-37631088`](../app/config/content/formulas/f3/shard_f3.json) (`Momentum-Position Scalar Product`):
     * Repaired `equation` from `"0xC20xA00xC20xA00xC20xA0"` to `"\\mathbf{p} \\cdot \\mathbf{r}"`, pruned hex-artifact variables (`x`, `C`, `A`), and updated `cas_validation` to `[\text{M} \cdot \text{L}^{2} / \text{T}]`.
  4. [`non-mathematical-string-placeholder-721457a6`](../app/config/content/formulas/63/shard_63.json) (`Plane Wave Solution`):
     * Replaced the placeholder `description` referencing `'$0xC20xA0$'` with a formal technical specification of the monochromatic plane-wave solution and set `equation_family` to `"wave-mechanics"`.
  5. [`missing-terms-8a0b93e4`](../app/config/content/formulas/55/shard_55.json) (`Canonical Non-Commutativity in the EPR Paradox`):
     * Replaced placeholder title `"Missing Terms"`, cleaned all `0xC20xA0` and `eq 0` corruptions across `interpretation`, `symmetry_origin`, `limits_and_boundary`, and `conceptual_definition`, and differentiated `description`.
  * Locked in permanent regression assertions in [`test_no_placeholder_titles_or_templated_prefixes()`](../tests/test_formula_latex_integrity.py) banning `0x[0-9A-Fa-f]{2}` across `equation`, `title`, and all 6 narrative fields, plus banning `"Missing Terms"` in `title`.

---

### ✅ Priority 3: Non-Canonical Math Delimiters (`51` fields), Raw HTML/Markdown (`33` fields), & Short Symmetry Labels (`8` fields) — *COMPLETED*

* **What Was Resolved**:
  * **Canonicalized 51 Math Delimiter Fields**: Converted all `\(...\)`, `\[...\]`, and `$$...$$` occurrences across `title` and the 6 narrative fields to canonical `$ ... $` (and repaired `\mu` distance-modulus variable definition in `second-variation-of-action-entropy-stability-delta-2-s-text-bounded-81e0d708`).
  * **Converted 33 Raw HTML/Markdown Narrative Fields**: Transformed all `<ul><li><b>...</b></li></ul>`, `<br>`, `* **Bullet**:`, and broken `$` delimiter strings (`geometric-guiding-ed3c1821`, `integral-form-gauss-7f72d118`, `cpt-operator-6d3e7c21`, `covariant-metric-tensor-component-7d207d2c`) into clean, continuous prose with balanced `$ ... $` delimiters.
  * **Expanded 8 Label-Only `symmetry_origin` Strings**: Replaced all 8 short labels (`< 35` chars, such as `"Geometric Invariance"` and `"Correspondence Principle"`) with full equation-specific explanations ($\ge 140$ chars).
  * **Locked in Permanent Regression Gates** in [`test_no_placeholder_titles_or_templated_prefixes()`](../tests/test_formula_latex_integrity.py) banning `\(...\)`, `\[...\]`, `$$`, raw HTML tags (`<(?:ul|ol|li|b|i|strong|em|p|br)\b`), Markdown bold (`\*\*[^*]+\*\*`), and `symmetry_origin` strings under 35 characters.

---

### ✅ Priority 4: `description == intuitive_summary` Duplication (`2,784` formulas) & Split-Command Math Delimiters (`18` fields) — *COMPLETED*

* **What Was Resolved**:
  * **Differentiated All 2,784 `description == intuitive_summary` Records Across All 256 Shards**:
    * For records with multi-sentence `conceptual_definition`, extracted the opening formal specification into `description` while preserving the accessible summary in `intuitive_summary`.
    * For records with a terse formal `description` (`"Defines..."`, `"This equation defines..."`), synthesized `intuitive_summary` from the highest-scoring physical-insight sentence in the record's own narrative fields.
    * For records with a single-sentence `conceptual_definition`, synthesized a crisp, formula-specific formal `description` from the record's own `title`, `derivation_type`, and `semantic_variables` (`$ ... $` symbol coupling), avoiding dangling contextual pronouns or subtopic drift.
  * **Repaired All 18 Split-Command Math Delimiter Fields** (`$\hat${$\rho$}`, `$\bar${$\theta}$`, `$\dot${$\omega$}_1`, etc.).
  * **Locked in Permanent Regression Gates** in [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) verifying that **all 15 pairs** of the 6 narrative fields (`description`, `conceptual_definition`, `intuitive_summary`, `interpretation`, `symmetry_origin`, `limits_and_boundary`) have **0** verbatim duplicates across all 14,684 formulas, validating `description` math delimiters, and banning split-command math delimiters (`split_math_re`).

---

### ✅ Priority 5: Sitewide `cas_validation` Sweep & `lineage_confidence` Provenance Tagging (`14,684` formulas) — *COMPLETED*

* **What Was Resolved**:
  * **Resolved All Stale `INHOMOGENEOUS` & `UNVERIFIED` Shards**:
    * Certified [`cross-field-electric-magnetic-drift-velocity-magnitude`](../app/config/content/formulas/98/shard_98.json) ($v_d = E/B$) and [`natural-classical-mechanical-lagrangian`](../app/config/content/formulas/2b/shard_2b.json) ($L = \frac{1}{2}m\dot{q}^2 - V(q)$) as `HOMOGENEOUS` and pruned all 8 raw Python exception `UNVERIFIED` stubs from the shards (`0` `INHOMOGENEOUS` and `0` `UNVERIFIED` remaining in shards).
    * Re-ran `scripts/cascheck --all --tag` across all **14,684** formulas and refreshed [`app/config/cas_validation_report.json`](../app/config/cas_validation_report.json).
  * **Populated `lineage_confidence` & Normalized `derivation_type` Across All 14,684 Formulas**:
    * Tagged 100% of the formula catalog with transparent provenance tiers (`"curated"`, `"root_axiom"`, `"cas_verified"`, `"heuristic"`) per [`GEMINI.md`](../GEMINI.md) §7.3.
    * Normalized all `76` non-canonical `derivation_type` strings (`"DEFINITIONAL"`, `"MATHEMATICAL_DEFINITION"`, `"LIMIT_CASE"`, `"AXIOMATIC"`, etc.) to the canonical 10-value schema enum.
  * **Locked in Permanent Regression Gates** in [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) and [`app/config/formula.schema.json`](../app/config/formula.schema.json) enforcing `lineage_confidence`, canonical `derivation_type`, and zero `INHOMOGENEOUS` / `UNVERIFIED` shard stubs.

---

## 📊 Summary Matrix

| Priority | Blind Spot / Category | Affected Records | Severity | Target Gate |
| :--- | :--- | :---: | :---: | :--- |
| **Priority 1** | ✅ Self-referential & fallback variable names (`name == key` / 1-char) | **839 formulas** (`2,347` vars) | **COMPLETED** | `test_formula_latex_integrity.py` |
| **Priority 2** | ✅ Hex-byte corrupted `equation` & prose strings (`0xC20xA0...`) | **5 formulas** | **COMPLETED** | `test_formula_latex_integrity.py` |
| **Priority 3** | ✅ Non-canonical delimiters (`51`), HTML/MD (`33`), short symmetry (`8`) | **92 fields** (`56` shards) | **COMPLETED** | `test_formula_latex_integrity.py` |
| **Priority 4** | ✅ Verbatim `description == intuitive_summary` duplication & split math | **2,784 formulas** (`256` shards) | **COMPLETED** | `test_formula_latex_integrity.py` |
| **Priority 5** | ✅ Sitewide `cas_validation` sweep + `lineage_confidence` & `derivation_type` | **14,684 formulas** (`256` shards) | **COMPLETED** | `test_formula_latex_integrity.py` + `formula.schema.json` |
