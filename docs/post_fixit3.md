# 🛠️ Post-Audit Optimization & Production Parity Roadmap (`docs/post_fixit3.md`)

**Audit Date**: 2026-11-11  
**Baseline**: Commit `7ce9af626` (Completion of [`archive/fixit_2.md`](../archive/fixit_2.md) and [`archive/fixit_3.md`](../archive/fixit_3.md) across all **14,684** formulas in 256 shards).  
**Scope**: Live audit of the PHP runtime bootstrap ([`PhysicsService.php`](../app/logic/PhysicsService.php)), dual-layer MariaDB synchronization ([`ShardSyncService.php`](../app/logic/ShardSyncService.php)), derived graph/trie indices, frontend provenance surfacing, and disk footprint.

---

## ✅ Priority 1: Slim & Lazy-Load `notation.json` + Hoist Partial Lookups *(COMPLETED)*

* **Original Bottleneck**:
  1. [`app/config/content/notation.json`](../app/config/content/notation.json) weighed **`16.72 MB` (`17,124.4 KB`)** across `348` entries because `240` entries contained dead, unreferenced subtopic HTML/inline-SVG fields (`content`, `snippet_svg`, `hero_math`, `formula_ids`, `parents`, `standard`, `snippet`).
  2. [`PhysicsService::getPhysicsContent()`](../app/logic/PhysicsService.php) eagerly `json_decode()`d `notation.json` on every uncached PHP bootstrap (~60+ MB PHP array heap per request).
  3. [`app/views/physics/_equations_partial.php`](../app/views/physics/_equations_partial.php) re-read and `json_decode()`d `global_slug_registry.json`, `categories.json`, and `notation.json` inside the nested `foreach ($f['semantic_variables'] ...)` loop (and shadowed `$subtopicSlug`).
* **Implemented Resolution**:
  1. **99.2% Footprint Reduction**: Backfilled clean, balanced-MathJax `description` strings for all `240` entries missing `description` and stripped dead subtopic bloat from [`app/config/content/notation.json`](../app/config/content/notation.json), shrinking it from **`17,124.4 KB` (`16.72 MB`) $\to$ `129.5 KB`** while preserving all `348` keys, symbols, values, units, and dimensions.
  2. **On-Demand Memoized Loader**: Added [`PhysicsService::getNotation()`](../app/logic/PhysicsService.php) (`$this->notationCache`) and removed eager `notation.json` loading from `getPhysicsContent()`, updating [`PhysicsController.php`](../app/controllers/PhysicsController.php) (`constants()`, `symbols()`, and the `subtopic()` 404 symbol-redirect check).
  3. **$O(1)$ Hoisted Slug Map in Partial**: Hoisted `array_flip()` lookup maps outside `foreach ($formulas as $f)` in [`_equations_partial.php`](../app/views/physics/_equations_partial.php), lazily loading `notation.json` at most once on fallback, and fixed `$refSubtopicSlug` shadowing.

---

## ✅ Priority 2: Close the MariaDB Column Gap for Newly Enriched Formula Fields *(COMPLETED)*

* **Original Gap**:
  The MariaDB `formulas` table lacked 5 schema fields populated across the 256 Git shards: `category` (`14,684`), `description` (`14,684`), `lineage_confidence` (`14,684`), `record_type` (`14,684`), and `equation_family` (`6,017`). Live production reads (`?preview=0`) via [`PhysicsService::loadFormula()`](../app/logic/PhysicsService.php) returned without those fields.
* **Implemented Resolution**:
  1. Added `category` (`VARCHAR(64)`, indexed via `idx_formulas_category`), `description` (`TEXT`), `lineage_confidence` (`VARCHAR(32)`, indexed via `idx_formulas_lineage_conf`), `record_type` (`VARCHAR(32)`), and `equation_family` (`VARCHAR(128)`) to [`ShardSyncService.php`](../app/logic/ShardSyncService.php) and [`PhysicsService::saveFormula()`](../app/logic/PhysicsService.php).
  2. Extended Dual-Layer Schema Resilience in [`PhysicsService::loadFormula()`](../app/logic/PhysicsService.php) and stripped numeric PDO keys (`PDO::FETCH_BOTH` guard) in both `loadFormula()` and `saveFormula()` (cleaning the 1 legacy numeric-key leak on `photon-energy` in `shard_fd.json` and backfilling `record_type` on the 3 newest shard entries for `14,684 / 14,684` parity).
  3. Migrated and backfilled all **14,684** MariaDB rows via `php cli_sync.php` and expanded `test_disk_to_database_integrity()` in [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) across all 10 prose & metadata columns.

---

## ✅ Priority 3: Unify Duplicate Formula Sync Paths in `ShardSyncService.php` *(COMPLETED)*

* **Original Bottleneck**:
  [`ShardSyncService.php`](../app/logic/ShardSyncService.php) maintained two separate formula-sync engines (`syncFormulasToDatabase()` vs. `performSync()` step 4), decoding all 256 shards twice on every `cli_sync.php` run, leaving `formulas_hash_registry.json` un-updated, and firing 12 blind `ALTER TABLE` statements inside `try/catch`.
* **Implemented Resolution**:
  1. Added idempotent [`ShardSyncService::ensureFormulasSchema()`](../app/logic/ShardSyncService.php) using `INFORMATION_SCHEMA.COLUMNS` and `INFORMATION_SCHEMA.STATISTICS` (zero blind `ALTER TABLE` exceptions; auto-triggers full backfill only when new columns are added).
  2. Consolidated `<svg data-tex="...">` extraction into [`syncFormulasToDatabase()`](../app/logic/ShardSyncService.php) and replaced the duplicate 90-line formula loop in `performSync()` step 4 with `$this->syncFormulasToDatabase($force)`, rebuilding `formulas_latex_index.json` only when shards changed or `$force = true`.

---

## ✅ Priority 4: Re-Sync Derived Graph & Reverse-LaTeX Lookup Artifacts *(COMPLETED)*

* **Original Gap**:
  - [`app/config/formula_derivation_graph.json`](../app/config/formula_derivation_graph.json) (and `.gz`) contained `14,681` nodes (missing the 3 newest formulas) and omitted `lineage_confidence`, `derivation_type`, `record_type`, and `cas_verified` provenance metadata on nodes and edges.
  - [`app/config/formulas_latex_index.json`](../app/config/formulas_latex_index.json) retained 3 stale pre-repair hex-garbage keys from `fixit_3.md` Priority 2 and 4 unsorted Python-ingested keys due to [`normalize_latex_key()`](../lib/pipeline/formula_pipeline.py) omitting commutative factor/term sorting.
* **Implemented Resolution**:
  1. Updated [`scripts/build_formula_graph.py`](../scripts/build_formula_graph.py) and [`FormulaGraphService.php`](../app/logic/FormulaGraphService.php) to include `lineage_confidence`, `derivation_type`, `record_type`, and `cas_verified` on all **14,684** graph nodes (`0` unmapped) and `confidence` on `14,119` links, regenerating both `.json` and `.json.gz`.
  2. Aligned [`normalize_latex_key()`](../lib/pipeline/formula_pipeline.py) 100% with [`LatexSanitizer::normalizeLatex()`](../app/logic/LatexSanitizer.php) (`0 / 14,684` mismatches), pruned the stale keys from `formulas_latex_index.json` (`13,132` clean entries, `0` dangling targets), and updated [`PhysicsService::saveFormula()`](../app/logic/PhysicsService.php) to evict superseded normalized keys on equation edits.
  3. Added automated parity gates `test_derived_graph_and_latex_index_parity` in [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) and `FormulaGraphServiceTest` in [`tests/php/run_php_tests.php`](../tests/php/run_php_tests.php).

---

## 🏅 Priority 5: Surface Provenance Badges & Distinct `description` in the UI *(User-Facing Payoff)*

* **What's Happening Now**:
  Every formula now carries a formal `description` distinct from its `intuitive_summary`, a `lineage_confidence` provenance tier (`curated`, `cas_verified`, `root_axiom`, `heuristic`), and (for `9,318` formulas) a SymPy-certified `cas_validation` block.
* **Proposed Optimization**:
  Update the Equation Explainer (`/physics/equation-explainer`) and Formula Inspector modal to:
  1. Render both the concise technical `description` subtitle and the `intuitive_summary` physical insight without repetition.
  2. Display subtle provenance pills on derivation lineage links distinguishing **Curated Proof** / **CAS-Verified** links from **Structural / Heuristic** links (fulfilling the user-facing transparency mandate of [`GEMINI.md`](../GEMINI.md) §7.3).

---

## 🧹 Priority 6: Purge `37.61 MB` of Stale `.bak` Content Shards *(Instant Disk Hygiene)*

* **What's Happening Now**:
  Two leftover backup files remain inside `app/config/content/`:
  - `app/config/content/theoretical-physics.json.bak` (`21.37 MB`)
  - `app/config/content/philosophy-of-physics.json.bak` (`16.24 MB`)
* **Proposed Optimization**:
  Delete both `.bak` files (reclaiming `37.61 MB`) and ensure `*.bak` is covered in `.gitignore` so backup shards never pollute `app/config/content/` scans.

---

## 📊 Summary Matrix

| Priority | Initiative | Target Component(s) | Primary Benefit | Effort |
| :---: | :--- | :--- | :--- | :---: |
| **P1** | Lazy-load `16.72 MB` `notation.json` | `app/logic/PhysicsService.php` | Cuts ~16.7 MB disk I/O & ~60+ MB RAM per dynamic request | Low |
| **P2** | MariaDB column parity (`description`, `category`, `lineage_confidence`, `record_type`) | `ShardSyncService.php`, `PhysicsService.php`, `test_formula_latex_integrity.py` | 100% shard-to-MariaDB production parity across all 14,684 rows | Low/Med |
| **P3** | Unify duplicate formula sync loops & `INFORMATION_SCHEMA` DDL check | `app/logic/ShardSyncService.php`, `cli_sync.php` | Single SQL write path; ~10x faster incremental `cli_sync.php` | Low/Med |
| **P4** | Rebuild `formula_derivation_graph.json` (`.gz`) & `formulas_latex_index.json` | `scripts/fixlineage`, `formulas_latex_index.json` | 14,684/14,684 node parity + `lineage_confidence` in DAG | Low |
| **P5** | Surface `description` + `lineage_confidence` badges in UI | `equation_explainer.php`, `equation_explainer.js`, `formula_inspector.js` | Exposes formal verification & provenance directly to users | Medium |
| **P6** | Remove stale `.bak` shard backups (`37.61 MB`) | `app/config/content/*.bak`, `.gitignore` | Reclaims `37.61 MB` disk space & prevents stray glob matches | Trivial |
