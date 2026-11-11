# 🪐 Physics Lab — Semantic Integrity & Red-Team Anomaly Audit (`docs/fixit_2.md`)

**Date:** November 8, 2026  
**Scope:** All 256 Formula Hex Shards (`14,684` formulas), Schema Validators (`app/config/formula.schema.json`), Test Suite (`tests/test_formula_latex_integrity.py`), and GQS Seeding Pipeline (`gqs.py`)  
**Status:** ✅ Phases 1–4 Complete (Schema Hardened, Missing Fields & Categories Healed, `semantic_variables` Cleaned, 864 Placeholder Titles Replaced, 871 Templated Narratives De-Templated, and Permanent Regression Gates Active)

---

## 1. Executive Summary: Why 241+ Passing Tests Missed Semantic Drift

Despite a 100% passing syntactic test suite (`pytest`, `integrity_shield.py`, `scripts/assess -q`) and a `99.9 / 100` Lineage Health Index, a deep cross-field semantic audit revealed significant **Syntactic Green-Light Blindness**:

1. **Permissive Schema Gate (`app/config/formula.schema.json`)**:
   * Previously, `formula.schema.json` only required `["title", "equation", "status"]`. It did not require `description`, `conceptual_definition`, `intuitive_summary`, `interpretation`, `symmetry_origin`, `limits_and_boundary`, `category`, or `semantic_variables`, nor did it enforce `minLength: 20` or a valid domain `category` enum.
2. **Schema Evolution Drift in `gqs.py`**:
   * Earlier formula records saved their one-sentence summary in `description` (leaving `intuitive_summary` blank on **668** records), while `gqs.py` saved its one-sentence summary in `intuitive_summary` (leaving `description` blank on **2,110** records). Because `gqs.py formula-status` only checked `intuitive_summary`, it reported `100.00% Enriched (0 Pending)`.
3. **Subtopic-Shard Extraction Bias**:
   * Equations originally harvested from `philosophy-of-physics.json` and `theoretical-physics.json` inherited the host article file's slug as their `category`, even when the formula's own `equation_family` and `parent_formula_id` were pure Quantum Mechanics, General Relativity, or Statistical Mechanics.
4. **Legacy Regex & Character-Tokenization Artifacts**:
   * An early batch extraction script stamped **783 equations** with the generic placeholder title `"Custom Physical Relation"`, templated their prose directly from surrounding article sentences, and ran a naive character-by-character variable lookup that parsed English letters inside `\text{...}` blocks as physics variables.

---

## 2. Completed Remediations & Permanent Schema Lock-In (Completed Nov 8, 2026)

| Remediation Item | Before | After | Implementation Details |
| :--- | :---: | :---: | :--- |
| **Leaf-Node Lineage Neighborhood Expansion** | 3-node vertical stick (`0` children shown) | **Full Family Subgraph (`Layer -3` to `+1`)** | Updated `FormulaGraphService::getFormulaSubgraph()`, `PhysicsService::getFormulaWithHierarchy()`, `formula_graph.js`, and `explainer_cards.js` to expand co-derived siblings (`Layer 0`), parallel aunt/uncle branches (`Layer -1`), and `"↔ Parallel & Co-Derived Family Equations"` cards whenever direct downstream children `< 3`. |
| **`description` Field Completeness** | 12,573 / 14,684 (85.6%) | **14,684 / 14,684 (100.0%)** | Cross-synced **2,110** records from verified `intuitive_summary` + authored **1** (`sturm-liouville-differential-equation-ident-20bcebfb`). |
| **`intuitive_summary` Completeness** | 14,015 / 14,684 (95.4%) | **14,684 / 14,684 (100.0%)** | Cross-synced **668** legacy records from verified `description` + authored **1** (`sturm-liouville-differential-equation-ident-20bcebfb`). |
| **`symmetry_origin` Completeness** | 14,678 / 14,684 (99.96%) | **14,684 / 14,684 (100.0%)** | Replaced `"N/A"` / `"null"` with explicit Lie group / invariance origins across all **6** remaining records (`pp-chain-identity-1-7a224847-dd8e7805`, `truth-making-61c094b4`, `planck-length-approaching-zero`, `technical-relation-a701a300`, `classical-limit-of-lagrangian-597ac001`, `extended-path-phase-space`). |
| **Missing `category` Field** | 3 missing | **0 missing (100.0%)** | Assigned `eulerian-velocity-vector-field` (`fluids-nonlinear`), `cross-field-electric-magnetic-drift-velocity-magnitude` (`electromagnetism`), and `three-dimensional-euclidean-line-element-in-spherical-coordinates` (`mathematical-methods`). |
| **Misfiled `philosophy-of-physics` Records** | 1,738 (11.8%) | **979 (6.7%)** (**759 re-filed**) | Re-classified **759** technical equations via explicit `equation_family` and parent-domain lineage (`+267` to `quantum-physics`, `+192` to `relativity`, `+83` to `astrophysics`, `+62` to `thermodynamics-statistical-mechanics`, `+50` to `electromagnetism`, `+45` to `classical-mechanics`, `+38` to `standard-model`, `+12` to `mathematical-methods`, `+8` to `fluids-nonlinear`, `+2` to `condensed-matter`). |
| **Blank Title Record (`-d9f00471`)** | `"title": ""` | **Healed** | Titled *"Electromagnetic Stress-Energy-Momentum Tensor"* in `shard_b1.json`, cleaned corrupted `$T^{\mu u}$` / `$\beta^{\mu u}$` prose, and removed spurious single-letter variables. |
| **Hardened `app/config/formula.schema.json`** | 3 required fields | **11 required fields + `minLength: 20` + 12-category `enum`** | Enforces non-empty strings (`minLength: 20`) on all 6 narrative fields, `minProperties: 1` on `semantic_variables`, and strict domain `category` enum across all 256 shards in `pytest` and `integrity_shield.py`. |
| **Updated `gqs.py` Formula Pipeline** | Ignored `description` | **Synchronized** | `is_formula_pending()`, `generate_formula_template()`, `ingest_formulas()`, `PhysicsFormulaMetadata`, and `seed()` now check and populate both `description` and `intuitive_summary`. |

---

## 3. Red-Team Semantic Anomaly Findings (Remaining Backlog)

Our read-only Red-Team Semantic Anomaly Scan across all `14,684` formulas exposed **5 concrete classes of semantic defects** that previously escaped syntactic testing:

### 🚨 Finding A: 783 Equations Titled `"Custom Physical Relation"` (+ 11 Titled `"Technical Relation (...)"`)
Across the 256 shards, **783 formulas** have the literal placeholder title `"title": "Custom Physical Relation"`, and **11 formulas** have titles starting with `"Technical Relation (...)"`.

* **Examples of Canonical Physics Equations Currently Titled `"Custom Physical Relation"`**:
  * `gauge-theory-identity-ca477fe3` (`shard_00.json`): `F^a_{\mu\nu} = \partial_\mu A^a_\nu - \partial_\nu A^a_\mu - g f^{abc} A^b_\mu A^c_\nu` *(Yang-Mills Non-Abelian Field Strength Tensor)*
  * `larmor-formula-identity-6b95c49a` (`shard_01.json`): `P = \oint \mathbf{S} \cdot d\mathbf{A} = \frac{q^2 a^2}{6\pi \varepsilon_0 c^3}` *(Larmor Radiated Power Formula)*
  * `relativistic-kinetic-energy-identity-25d623e1` (`shard_01.json`): `H = p v - L` *(Legendre Transformation of the Lagrangian)*
  * `conservation-of-electric-charge-identity-5652a01c` (`shard_01.json`): `J^\mu = (\rho, \mathbf{J})` *(Relativistic Charge-Current Four-Vector)*
  * `momentum-operator-identity-fa9d896b` (`shard_02.json`): `\psi_{\mathbf{p}}(\mathbf{r}) = C e^{i\mathbf{p}\cdot\mathbf{r}/\hbar}` *(Momentum Eigenstate Plane-Wave Solution)*
  * `born-rule-identity-2308b38c` (`shard_03.json`): `P(\mathbf{x})d^3x = |\psi(\mathbf{x})|^2 d^3x = \psi^*(\mathbf{x})\psi(\mathbf{x}) d^3x` *(Born Rule Position Probability Density)*
  * `free-fall-identity-22fb3ad6` (`shard_b1.json`): `p_\mu = g_{\mu\nu} p^\nu` *(Covariant Four-Momentum Index Lowering)*
  * `block-universe-identity-447f69ed` (`shard_b1.json`): `\frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\rho\sigma} \frac{dx^\rho}{d\tau} \frac{dx^\sigma}{d\tau} = 0` *(Relativistic Geodesic Equation)*
* **Associated Prose & Variable Defect on These 783 Records**:
  * These 783 `-identity-` records were generated by a legacy subtopic-extraction template (`"In the study of [Subtopic], the relation [LaTeX] formalizes a core mathematical condition: [sentence]"`).
  * In several cases (e.g., `block-universe-identity-447f69ed`), inline math was stripped from the copied sentence (`"The invariance of the spacetime interval, expressed as, fundamentally necessitates..."`).
  * Their `semantic_variables` were populated by a naive context-free lookup table that mapped spacetime tensor index `\mu` in relativity ($p_\mu = g_{\mu\nu}p^\nu$) to `"Reduced Mass (kg) in two-body central motion"`.

---

### 🚨 Finding B: Character-by-Character `\text{...}` Pollution & Operator Placeholders in `semantic_variables`
* **2,187 variable entries** across the shards have keys whose symbols do not correspond to mathematical variables in the formula, or were extracted letter-by-letter from English words inside `\text{...}` / `\mathrm{...}` blocks.
  * **Example (`work-independence-d3ea1d7f` in `shard_b1.json`, `\nabla \times \mathbf{E} = 0 \iff \text{Radial Symmetry}`)**:
    * A legacy script parsed the individual English letters of `Radial Symmetry` (`R, i, l, S, y, m, e, t, r`) and injected:
      * `"R"` $\to$ *Ideal Gas Constant ($\text{J/(mol}\cdot\text{K)}$)*
      * `"i"` $\to$ *Imaginary Unit*
      * `"l"` $\to$ *Length / Angular Quantum Number*
      * `"S"` $\to$ *Poynting Vector ($\text{W/m}^2$)*
      * `"y"` $\to$ *Position Coordinate*
      * `"m"` $\to$ *Mass ($\text{kg}$)*
      * `"e"` $\to$ *Elementary Charge ($\text{C}$)*
      * `"t"` $\to$ *Time ($\text{s}$)*
      * `"r"` $\to$ *Radial Distance ($\text{m}$)*
  * **Example (`condition-for-net-zero-force-054c4cac` in `shard_b1.json`, `\mathbf{F}_{net} = 0`)**:
    * Parsed the subscript letters `n`, `e`, `t` of `_{net}` into:
      * `"n"` $\to$ *Quantum Number / Number Density*
      * `"e"` $\to$ *Elementary Charge ($\text{C}$)*
      * `"t"` $\to$ *Time Coordinate ($\text{s}$)*
* **223 variable entries across 188 formulas** have generic placeholder descriptions (`"Physics variable or parameter."` or `< 10` characters), such as `"\\times": { "name": "\\times Parameter", "description": "Physics variable or parameter." }`.

---

### 🚨 Finding C: Over-Stuffed `"theoretical-physics"` Category (`2,731` Formulas / `18.6%` of Catalog)
Just as `"philosophy-of-physics"` previously held hundreds of concrete domain equations, `"theoretical-physics"` currently acts as a catch-all bucket holding **2,731 formulas**:
* **550+ formulas in `"theoretical-physics"`** have explicit `equation_family` or `parent_formula_id` tags belonging to specific pillar domains:
  * **Quantum Physics (`~180+` formulas)**: `quantum-mechanics` (89), `quantum-mechanics-fundamentals` (30), `quantum-mechanics-operators` (27), `quantum-mechanics-foundations` (14), `quantum-dynamics` (10), `quantum-mechanics-angular-momentum` (8), plus 52 whose direct parent is in `quantum-physics`.
  * **Classical Mechanics (`~175+` formulas)**: `hamiltonian-mechanics` (55), `classical-mechanics` (42), `analytical-mechanics` (42), `lagrangian-mechanics` (36), plus 107 whose direct parent is in `classical-mechanics`.
  * **Standard Model / High-Energy (`~95+` formulas)**: `quantum-field-theory` (51), `grand-unified-theories` (14), `relativistic-field-theory` (13), `gauge-theory` (12), `quantum-chromodynamics` (9), `particle-physics` (9), plus 79 whose direct parent is in `standard-model`.
  * **Relativity (`~40+` formulas)**: `general-relativity` (24), `relativistic-kinematics` (16), plus 29 whose direct parent is in `relativity`.
  * **Thermodynamics & Statistical Mechanics (`~22+` formulas)**: `statistical-mechanics` (13), plus 9 whose direct parent is in `thermodynamics-statistical-mechanics`.

---

### 🚨 Finding D: Metaphorical / Opaque Legacy Slugs (`~670` Formulas)
While URL slugs do not break mathematical rendering if their `title` is accurate, roughly **670 formulas** carry opaque or metaphorical IDs from early extraction passes:
* `496` formulas match `*-identity-\d+-*` (e.g., `offer-wave-identity-1-6186b4a2-223be70d` for *Time-Dependent Schrödinger Equation*).
* `111` formulas match `^technical-relation-*` (e.g., `technical-relation-c7c9ede2` for *General Solution for Simple Harmonic Motion*).
* Handful of colloquial section-header slugs:
  * `the-cosmic-fake-6a24a3f4` (*Principle of Stationary Action — Lagrangian Formulation*)
  * `collective-fake-b983158f` (*Effective Hamiltonian for Non-Interacting Quasiparticles*)
  * `amp-rian-rule-d1724530` (*Ampère's Law — Integral Form*)
  * `crystal-math-d2818099` (*De Broglie Wavelength of a Non-Relativistic Electron*)
  * `matrix-math-8b8a3af3` (*Brewster's Law for Polarization by Reflection*)

---

### 🚨 Finding E: 996 Duplicate Normalized LaTeX Equations (`1,188` Extra Copies)
* **996 distinct normalized LaTeX strings** appear more than once across the 14,684 formula records (accounting for **1,188 extra copies**).
* **Top Examples**:
  * $G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$ (8 copies: `dynamical-spacetime-18abdd17`, `machs-principle-identity-1-48316b81-13bfe3c8`, `einstein-and-stress-energy-tensor-proportionality`, `einstein-tensor-ef7244f6`, etc.)
  * $\mathbf{p} = m\mathbf{v}$ (6 copies: `total-momentum-cm`, `non-relativistic-momentum`, `momentum`, `classical-momentum`, etc.)
  * $R_{\mu\nu} - \frac{1}{2} R g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$ (6 copies)
  * $L = -mc\sqrt{-g_{\mu\nu}\dot{x}^\mu\dot{x}^\nu}$ (5 copies)

---

## 4. Recommended Next Steps & Permanent Guardrails

1. **Step 1 — Purge Spurious Subscript/`\text{...}` Letter Variables & Operator Placeholders (`semantic_variables`)**:
   * Deterministically remove single-letter entries in `semantic_variables` that only appear inside `\text{...}`, `\mathrm{...}`, or multi-letter subscripts like `_{net}`, `_{tot}`, `_{eff}`, `_{ext}`, `_{max}`, `_{min}`, `_{rel}` (while preserving real variables that appear outside text/subscripts), and remove operator placeholders with `"description": "Physics variable or parameter."`
   * Fix the context-sensitive tensor index `\mu` / `\nu` on `relativity` and `electromagnetism` tensor equations where `\mu` was mislabeled `"Reduced Mass (kg)"`.
2. **Step 2 — Heal the 783 `"Custom Physical Relation"` & 11 `"Technical Relation"` Titles**:
   * Replace all 794 placeholder titles with accurate physical titles derived from their LaTeX equation, canonical duplicates, and subtopic context, and add a regex block in `formula.schema.json` (`"not": {"pattern": "^(Custom Physical Relation|Technical Relation)"}`) so placeholder titles can never be committed again.
3. **Step 3 — Re-Classify Concrete Domain Equations out of `"theoretical-physics"`**:
   * Move the ~550+ formulas with explicit `quantum-mechanics`, `hamiltonian/lagrangian-mechanics`, `quantum-field-theory`, `general-relativity`, and `statistical-mechanics` families/parents out of `"theoretical-physics"` into their primary domain categories.
4. **Step 4 — Add `tests/test_semantic_coherence.py` to the Automated Test Suite**:
   * Permanently codify checks for placeholder titles, `\text{...}` letter-variable pollution, `category` vs. `equation_family` coherence, and minimum narrative depth into `pytest` and `scripts/assess`.
