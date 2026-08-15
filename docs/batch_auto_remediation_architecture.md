# Equation Repair Engine: Enhancement Roadmap & Batch Auto-Remediation Architecture

**Document Version:** 1.0  
**Date:** August 2026  
**Status:** Design & Architectural Specification  

---

## 1. Executive Summary

The **Terra Equation Repair Engine** (`scripts/fixlatex` / `scripts/fix_equation_by_url.php`) provides an automated, multi-target pipeline for deconstructing, sanitizing, and updating physics equations across JSON shard files, the MariaDB database, and canonical LaTeX lookup indices.

This document outlines:
1. **Feature Enhancement Roadmap**: High-impact improvements for UI integration, semantic variable extraction, and knowledge graph linkage.
2. **The "Whack-a-Mole" Analysis**: A root-cause diagnosis of why greedy regex sanitizers cause regressions when applied repo-wide.
3. **Batch Auto-Remediation Architecture**: A compiler-style, AST-based blueprint for safe, zero-regression batch shard repairs.

---

## 2. Feature Enhancement Roadmap

### 2.1 In-App Web UI "One-Click Quick Fix" & Live Preview
* **Admin / Developer Overlay**: On `/physics/equation-explainer`, add an edit/repair toggle button that opens a slide-over drawer.
* **Side-by-Side Live MathJax Preview & Diff**: When pasting raw textbook text or LaTeX fixes, show a real-time side-by-side preview with color-coded diffing before saving.
* **Direct Web Dispatch**: Allow saving directly in the browser, dispatching to the repair pipeline and updating both shard files and MariaDB without requiring manual terminal commands.

### 2.2 Smart Semantic Variable & Unit Auto-Discovery
* **Automated Variable Extraction**: When reference prose is provided (e.g., *"where $Q_i^{\text{nc}}$ is the generalized non-conservative force with units of Joules"*), extract newly introduced variables and auto-populate their entries in `semantic_variables` (name, symbol, unit, SI dimensions, tensor type).
* **Dimensional Consistency Verification**: Integrate with the existing dimensional analysis engine to verify that the LHS and RHS dimensions match (e.g., verifying that both sides resolve to $[M][L]^2[T]^{-2}$ for energy equations) and flag dimensional anomalies.

### 2.3 Formula Versioning, Snapshots & Rollback
* **Repair Snapshot History**: Before modifying any shard or database record, archive the previous formula JSON into a local history log (e.g., `app/config/content/history/[formula-id]/timestamp.json`).
* **One-Command Rollback (`scripts/fixlatex --rollback <id|URL>`)**: Instantly restore the previous version if an auto-sanitization made an undesired change.
* **Git Staging Integration (`--commit`)**: Optional flag to automatically stage the affected shard file and index with a pre-formatted commit message.

### 2.4 Multi-Source Ingestion (arXiv / Wikipedia / PDF Snippets)
* **Wikitext & LaTeX Normalizer**: Add native decoders for common copy-paste formats (e.g., Wikipedia math templates `{{math|...}}`, `<math chem>`, LaTeX source files directly from arXiv `.tex` documents).
* **Automated Clean-up of PDF Artifacts**: Strip common ligature and OCR errors (such as `fi` / `fl` ligatures turning into special symbols, hyphens splitting words across lines, and lost superscript formatting).

### 2.5 Knowledge Graph & Automated Subcomponent Linking
* **Sub-Equation Matcher**: When an equation is repaired, analyze its sub-terms (e.g., recognizing that $p_i = \frac{\partial L}{\partial \dot{q}_i}$ and $L = T - V$ exist as standalone formulas) and automatically suggest or populate them in `subcomponents` and Topological Bridges.
* **Parent-Child Derivation Detection**: Automatically classify whether the formula is an `EQUIVALENT_FORM`, `LIMITING_CASE`, or `DERIVATION_STEP` of a parent formula in the ontology.

---

## 3. The "Whack-a-Mole" Dilemma in Batch Auto-Remediation

When transforming on-demand single-formula repair tools into repo-wide batch sweepers, heuristic transformations frequently introduce regressions.

### 3.1 Core Failure Modes

```
               [Single Stray '$']
                       │
       ┌───────────────┴───────────────┐
       ▼                               ▼
[Parity Inverted]              [Text Mutilation]
- Prose treated as Math        - English words wrapped in '$'
- Math treated as Prose        - Substrings stripped by regex
```

1. **Delimiter Parity Inversion (The Odd/Even Dollar Trap)**:
   * Narrative sanitizers often split text by `$` to process prose (even indices) and math (odd indices).
   * A single orphaned `$` inverts the entire parity for the rest of the text, causing prose-cleaners to strip math and math-wrappers to wrap English words.

2. **Non-Idempotent Transformations**:
   * Auto-remediation rules must be **strictly idempotent**:
     $$\text{Sanitize}(\text{Sanitize}(\text{Text})) \equiv \text{Sanitize}(\text{Text})$$
   * If a rule wraps `x` into `$x$`, running it a second time across already-clean shards must not produce `$$x$$` or `$\$x\$$`.

3. **Sub-string Collisions & Negative Lookarounds**:
   * Blind replacements (e.g. `abla` $\to$ `\nabla`, `dau` $\to$ `\tau`) corrupt text if the string already had `\nabla` (turning it into `\\nabla` or `\n\nabla`) or if English words contain those letter combinations.

4. **Physics Subfield Notation Ambiguities**:
   * In **Thermodynamics**, $T$ is temperature and $V$ is volume.
   * In **Classical Mechanics**, $T$ is kinetic energy and $V$ is potential energy.
   * In **General Relativity**, Greek indices $\mu, \nu$ represent spacetime coordinates.
   * In **Quantum Mechanics**, Dirac bra-ket notation ($\langle \psi | \phi \rangle$) conflicts with standard comparison operators ($<$ and $>$).
   * Rules tailored for one domain must not greedily rewrite expressions from another.

---

## 4. Batch Auto-Remediation Architecture

To break the "whack-a-mole" cycle, the engine must evolve from greedy regular expressions to a **compiler-style, AST-based pipeline**.

```
┌────────────────────────────────────────────────────────┐
│                   Raw Shard Files                      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 1: Delimiter Balancing & Tokenizer (AST)        │
│  - Tokenizes stream into PROSE, MATH_BLOCK, MACROS     │
│  - Enforces balanced '$' delimiters before processing  │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 2: Multi-Tier Rule Execution Engine             │
│  - Tier 1: Deterministic Invariants (100% Safe)        │
│  - Tier 2: Lexically-Guarded Formula Transformers      │
│  - Tier 3: Heuristic Flags (Requires Confirmation)     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  Phase 3: Idempotency & In-Memory Shadow Validation    │
│  - Property Test: f(f(x)) === f(x)                     │
│  - Runs pytest suite against in-memory shadow state    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
               ┌───────────────────────┐
               │ Zero Regressions Met? │
               └───┬───────────────┬───┘
                   │ YES           │ NO
                   ▼               ▼
┌─────────────────────────┐  ┌───────────────────────────┐
│ Commit Shards & MariaDB │  │ Abort & Export Fail Diffs │
└─────────────────────────┘  └───────────────────────────┘
```

---

### 4.1 Rule Classification & Tiering

| Tier | Category | Description | Examples |
| :--- | :--- | :--- | :--- |
| **Tier 1** | **Deterministic Invariants** | Syntactically and mathematically certain; safe to auto-apply repo-wide. | Unescaping `\n\n\nabla`, unescaping tabs, fixing orphaned `\text{\}`, removing trailing isolated `.$`. |
| **Tier 2** | **Context-Guarded Transforms** | Applied only when precise lexical and mathematical boundaries match. | Isolated equation wrapping ($F_i = -\frac{\partial V}{\partial q_i}$), Greek letter notation ($\chi_m$, $\mu_0$). |
| **Tier 3** | **Heuristic / Ambiguous** | Requires human review or AST confirmation. | Untyped single-letter variable conversions ($T$, $V$, $E$), non-standard notation. |

---

### 4.2 The Zero-Regression Shadow Gate

Before writing changes to disk or database:
1. **In-Memory Shadow Mutation**: Load shards in-memory and apply Tier 1 and Tier 2 rules.
2. **Automated Assertion Harness**: Run the test suite (`pytest tests/`) against the shadow state.
3. **Strict Gate Condition**:
   $$\text{Failures}_{\text{after}} \le \text{Failures}_{\text{before}}$$
   If any new test failure is detected, the batch operation aborts, rolls back all in-memory changes, and outputs a detailed diagnostic diff identifying the exact formula and rule that caused the regression.

---

## 5. Summary & Next Steps

By combining **AST-based delimiter tokenization**, **strict idempotency guarantees**, and **shadow test-suite validation gates**, the equation repair engine can safely transition from single-URL targeted fixes to a reliable, repo-wide batch auto-remediation system.
