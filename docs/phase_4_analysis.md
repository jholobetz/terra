# Phase 4 Architectural Analysis — Physics Lab (`terra`) Codebase & Tooling Audit

This document provides an objective, code-grounded architectural analysis of the Physics Lab (`terra`) codebase and its developer tooling. Rather than repeating scorecard metrics at face value, this assessment examines the actual implementation mechanics, coupling boundaries, runtime bottlenecks, and maintenance trade-offs across the ~75,000 lines of code and scripts in the repository to inform **Phase 4** engineering priorities.

---

## 1. Empirical Codebase Footprint

| Layer / Directory | Files | Lines of Code | Primary Languages & Role |
| :--- | :---: | :---: | :--- |
| [`app/`](../app) | 443 | ~17,177 | PHP 8 (Flight micro-framework), HTML/PHP view templates, JSON config & 256 formula shards |
| [`public/js/`](../public/js) | 50 | ~25,381 | Vanilla ES6+ JavaScript, WebGL2/GLSL shaders, Canvas 2D simulations, MathJax 3 |
| [`scripts/`](../scripts) | 127 | ~23,078 | Python 3 & PHP CLI maintenance, auditing, healing, and AI batch pipelines |
| [`lib/`](../lib) | 25 | ~3,245 | Python SymPy CAS engine ([`cas_engine.py`](../lib/cas/cas_engine.py)) and derivation prover ([`derivation_prover.py`](../lib/cas/derivation_prover.py)) |
| [`tests/`](../tests) | 32 | ~4,631 | Pytest suite (data invariants, CAS unit tests, PHP CLI bridge tests, static source checks) |

---

## 2. Core Strengths (What Genuinely Works Well)

1. **Deterministic Content & Graph Integrity Gates**
   * Unlike typical content-heavy web applications where broken links, orphan equations, or malformed LaTeX silently accumulate in a relational database, [`integrity_shield.py`](../integrity_shield.py) and [`scripts/assess`](../scripts/assess) enforce strict graph closure across all 1,584 subtopics and 14,683 formulas.
   * Checking the 256 hex shards (`app/config/content/formulas/[00-ff]/shard_[00-ff].json`) and derivation DAG ([`formula_derivation_graph.json`](../app/config/formula_derivation_graph.json)) directly into Git makes content mutations diffable, versioned, and testable in CI without standing up a database server.

2. **Zero-Build, High-Performance Interactive Physics Simulations**
   * The simulation layer ([`webgl_physics_harness.js`](../public/js/lib/webgl_physics_harness.js), [`relativistic-black-hole.js`](../public/js/simulations/relativistic-black-hole.js), [`pendulum.js`](../public/js/simulations/pendulum.js)) is written in dependency-free Vanilla JS and raw WebGL2/GLSL.
   * Avoiding heavy frontend bundler toolchains (Webpack/Vite/React) means zero `node_modules` bloat, zero hydration lag, and immediate 60fps canvas/shader execution.

3. **Pragmatic Hardening of the PHP-to-Python CAS Bridge**
   * Spawning a Python SymPy interpreter from PHP (`shell_exec` in [`PhysicsController::apiCasEvaluate()`](../app/controllers/PhysicsController.php)) is inherently expensive (~160–200ms cold start). However, the implementation mitigates this effectively with:
     * A 2-second `SIGALRM` timeout inside [`cas_engine.py`](../lib/cas/cas_engine.py) to prevent pathological symbolic hangs (e.g., non-terminating integrals or high-order polynomial roots).
     * A SHA-256 content-addressed file cache (`public/cache/cas/`) keyed on payload + script `mtime` (<1ms warm response).
     * A sliding-window IP rate limiter ([`PhysicsController::consumeCasRateLimit()`](../app/controllers/PhysicsController.php)) to prevent process-fork exhaustion.

4. **Strict AI Cost & Token Governance**
   * The AI batch tooling ([`generate_gemini_formula.py`](../scripts/maintenance/generate_gemini_formula.py) and [`cost_governance.md`](cost_governance.md)) enforces pre-flight token counting, hard output token caps, and free-tier defaults rather than firing unbounded LLM requests.

---

## 3. Structural Weaknesses & Technical Debt (Unvarnished Critique)

### A. The "Dual-Layer" Data Model Has a Hidden Production I/O Bug
While the architecture documentation states that MariaDB is the sole production read engine and JSON shards are only an offline fallback, [`PhysicsService::loadFormula()`](../app/logic/PhysicsService.php) currently violates this in production:
* In `PhysicsService.php` (lines 550–566):
  ```php
  // Dual-Layer Resilience: If DB lacks derivation_steps or cas_validation, fallback to Git shard
  if (empty($formula['derivation_steps']) || empty($formula['cas_validation'])) {
      $hexPrefix = substr(md5($fId), 0, 2);
      $shardFile = PROJECT_ROOT . '/app/config/content/formulas/' . $hexPrefix . '/shard_' . $hexPrefix . '.json';
  ```
* **Two compounding issues here**:
  1. Neither [`syncFormulasToDatabase()`](../app/logic/PhysicsService.php) nor [`saveFormula()`](../app/logic/PhysicsService.php) includes a `cas_validation` column in its SQL `INSERT`/`UPDATE` statements. Thus `$formula['cas_validation']` from MariaDB is *always* empty unless manually migrated outside `PhysicsService`.
  2. Even worse, **99.3% of formulas (14,580 out of 14,683) do not have multi-step proofs**, meaning `empty($formula['derivation_steps'])` is `true` for almost every formula in the encyclopedia.
* **Consequence**: On every cold formula lookup in production, `loadFormula()` queries MariaDB **and then immediately reads and `json_decode`s a 150–250 KB JSON shard from disk anyway**, paying both database latency and disk JSON parsing overhead.

### B. Regex-Driven LaTeX-to-SymPy Translation is Fragile by Nature
* Both [`latex_to_sympy_str()`](../lib/cas/cas_engine.py) in `cas_engine.py` and [`batch_cas_prover.py`](../scripts/batch_cas_prover.py) convert LaTeX into SymPy expressions using chained regular expressions rather than a formal grammar/lexer (such as `antlr4`-based `sympy.parsing.latex` or a dedicated recursive-descent TeX tokenizer).
* **Why this matters**:
  * Chained regexes struggle with deeply nested braces (`\frac{\frac{a}{b}}{\sqrt{1 - \frac{v^2}{c^2}}}`), context-dependent superscripts (e.g., tensor contravariant indices $T^{\mu\nu}$ vs. exponentiation $T^{\mu \cdot \nu}$, or $f^{-1}(x)$ vs. reciprocal power), and operator ordering.
  * Furthermore, `cas_engine.py`, `batch_cas_prover.py`, and `derivation_prover.py` each maintain slightly different regex sanitization pipelines and symbol dictionaries. When a formula passes `batch_cas_prover.py` via a domain-specific symbol heuristic or operator regex bypass, it is stamped `VERIFIED` or `OPERATOR_OR_TENSOR`, which can overstate how much true algebraic equivalence SymPy actually proved.

### C. Monolithic God-Files in PHP and Frontend JS
Several core files have grown into multi-thousand-line monoliths that mix concerns:
* [`public/js/equation_explainer.js`](../public/js/equation_explainer.js) (**3,962 LOC**): Handles DOM rendering, LaTeX tokenization, interactive symbol highlighting, MathJax lifecycle hooks, graph visualization, API fetching, modal state, and AI synthesis in a single procedural script without module boundaries.
* [`app/logic/PhysicsService.php`](../app/logic/PhysicsService.php) (**2,055 LOC**): Acts simultaneously as an ORM/database sync engine, JSON shard manager, LaTeX normalizer, HTML/TeX sanitizer, graph hierarchy resolver, and AI prompt synthesizer.
* [`app/views/physics/topic.php`](../app/views/physics/topic.php) (**1,807 LOC**) and [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php) (**1,203 LOC**): View files contain large blocks of inline CSS, data transformation logic, and inline JavaScript alongside HTML markup.

### D. Maintenance Script Sprawl & Logic Duplication
* The [`scripts/`](../scripts) directory contains **127 files (~23,078 LOC)**—more code than the entire PHP backend (`app/` at ~17,177 LOC).
* There are **59 scripts** in `scripts/maintenance/` alone, plus 25 in `scripts/archive/` and 19 in `scripts/`.
* Many of these scripts were written for specific one-off remediation campaigns (fixing parent links, healing isolated nodes, patching LaTeX corruptions, auditing prose) and duplicate shard-loading, LaTeX-normalization, and hash-registry update logic in both Python and PHP instead of routing through a single shared library.
* For example, updating a shard in Python requires remembering to run or invoke hash-registry synchronization separately, whereas PHP updates go through `PhysicsService::saveFormula()`.

### E. Concurrency & Race Conditions in Flat-File State
* In [`PhysicsService::saveFormula()`](../app/logic/PhysicsService.php), every single formula save reads, decodes, mutates, and rewrites the entire [`app/config/formulas_latex_index.json`](../app/config/formulas_latex_index.json) and [`app/config/formulas_hash_registry.json`](../app/config/formulas_hash_registry.json) without `LOCK_EX` file locking or atomic temp-file rename (`rename()`).
* Similarly, [`consumeCasRateLimit()`](../app/controllers/PhysicsController.php) reads and writes JSON timestamp arrays in `/tmp/terra_cas_ratelimit/` without `flock()`. Under concurrent HTTP requests, parallel workers can clobber each other's writes.

---

## 4. Tooling & Test Suite Critique (Signal vs. Theatre)

The project includes **242 passing pytest tests** and a comprehensive [`scripts/assess`](../scripts/assess) console. However, an objective look at [`tests/`](../tests) reveals an important distinction between **behavioral testing** and **static source-string assertions**:

1. **Over-Reliance on `read_text()` Substring Assertions for UI/PHP Tests**
   * Roughly half of the 32 test files in `tests/` validate PHP views and JS modules by reading the source file as a string and asserting that certain substrings or regexes appear in the code (e.g., checking that `"cas_validation"` or `"renderCasBadge"` exists in `equation_explainer.js`).
   * **Weakness**: Source-text checks confirm that code was *not deleted*, but they cannot catch runtime JS `TypeError`s, broken DOM selectors, CSS layout regressions, or PHP runtime exceptions when rendering a view with edge-case data.
2. **Genuine High-Value Tests**
   * By contrast, tests like [`test_cas_engine.py`](../tests/test_cas_engine.py), [`test_derivation_steps.py`](../tests/test_derivation_steps.py), [`test_delimiters_lib.py`](../tests/test_delimiters_lib.py), and [`integrity_shield.py`](../integrity_shield.py) execute real logic against the full dataset and provide genuine regression protection.
3. **Hidden Coupling Between Tests and Working-Tree State**
   * Several tools and tests historically assumed local uncommitted cache/report files (`app/config/cas_validation_report.json`, `.last_sync`, etc.) were present on disk, masking differences between a dirty local workspace and a clean CI checkout.

---

## 5. Highest-Leverage Technical Improvements (Prioritized Candidates for Phase 4)

To harden the engineering foundation before expanding into OPS 2.0 (Phase 5) and Project Terra Multi-Science Expansion (Phase 6), these four refactors offer the highest return on investment:

1. **Fix the Production Shard-Fallback Trap in [`PhysicsService::loadFormula()`](../app/logic/PhysicsService.php)**:
   * Add `cas_validation` to the MariaDB `formulas` table schema and `syncFormulasToDatabase()` / `saveFormula()` queries, and remove `empty($formula['derivation_steps'])` from the shard-fallback condition (since `NULL` / `[]` is the normal expected state for 99.3% of formulas). This immediately eliminates redundant 200KB disk reads on production database hits.
2. **Unify the Python CAS & LaTeX Sanitization Pipeline**:
   * Consolidate the duplicate LaTeX-to-SymPy parsers and dimensional symbol dictionaries across [`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py), [`lib/cas/derivation_prover.py`](../lib/cas/derivation_prover.py), and [`scripts/batch_cas_prover.py`](../scripts/batch_cas_prover.py) into a single canonical module under `lib/cas/`.
3. **Decompose [`PhysicsService.php`](../app/logic/PhysicsService.php) and [`equation_explainer.js`](../public/js/equation_explainer.js)**:
   * Split `PhysicsService.php` into focused domain classes (`FormulaRepository`, `ShardSyncService`, `LatexSanitizer`).
   * Split `equation_explainer.js` (3,962 LOC) into native ES modules (`explainer_graph.js`, `explainer_cas.js`, `explainer_dom.js`) — which still requires zero build step in modern browsers via `<script type="module">`.
4. **Prune & Consolidate [`scripts/maintenance/`](../scripts/maintenance) + Add Atomic File Locking**:
   * Archive one-off historical migration scripts into `scripts/archive/` so `scripts/maintenance/` only houses active operational tools invoked by `gqs.py`, `scripts/assess`, or CI, and enforce atomic writes (`LOCK_EX` / temp-file rename) on flat-file registries.
