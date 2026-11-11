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

## 🔄 Priority 2: Close the MariaDB Column Gap for Newly Enriched Formula Fields *(Production Parity Win)*

* **What's Happening Now**:
  Across `fixit_2.md` and `fixit_3.md`, four key fields were enriched and strictly gated across all **14,684** shard records:
  1. `description` (formal technical specification, distinct from `intuitive_summary`)
  2. `category` (the 12 canonical physics domains)
  3. `lineage_confidence` (`curated`, `cas_verified`, `root_axiom`, `heuristic`)
  4. `record_type` (`equation` vs. `symbol_or_term`)

  However, inspecting [`ShardSyncService.php`](../app/logic/ShardSyncService.php) (lines 62–87, 379–399, 479–503) and [`PhysicsService::saveFormula()`](../app/logic/PhysicsService.php) (lines 548–567) shows that the MariaDB `formulas` table **does not yet have columns** for `description`, `category`, `lineage_confidence`, or `record_type`.
* **Why It Matters**:
  In production mode (`?preview=0`), [`PhysicsService::loadFormula()`](../app/logic/PhysicsService.php) (lines 345–412) queries MariaDB directly and returns without reading the JSON shard on disk—meaning those 4 fields silently return `null` / missing in live production queries.
* **Proposed Optimization**:
  1. Add `description` (`TEXT`), `category` (`VARCHAR(64)`, indexed), `lineage_confidence` (`VARCHAR(32)`, indexed), and `record_type` (`VARCHAR(32)`) to `ShardSyncService.php` and `PhysicsService::saveFormula()`.
  2. Execute a forced MariaDB sync so all 14,684 rows in MariaDB match the 256 Git shards 1:1.
  3. Expand `test_disk_to_database_integrity()` in [`tests/test_formula_latex_integrity.py`](../tests/test_formula_latex_integrity.py) to verify `description`, `category`, `lineage_confidence`, and `record_type` between disk shards and MariaDB.

---

## ⚡ Priority 3: Unify Duplicate Formula Sync Paths in `ShardSyncService.php` *(~10x Faster Incremental Sync)*

* **What's Happening Now**:
  [`ShardSyncService.php`](../app/logic/ShardSyncService.php) currently maintains **two separate formula-sync implementations**:
  - [`syncFormulasToDatabase()`](../app/logic/ShardSyncService.php) (lines 29–259): SHA-256 hash-driven via `formulas_hash_registry.json`, skipping unchanged shards before `json_decode()`.
  - [`performSync()`](../app/logic/ShardSyncService.php) (lines 451–535, invoked by `cli_sync.php`): `filemtime()`-driven via `.last_sync`, which **reads and `json_decode()`s all 256 shard files on every run** to construct `$diskFormulaIds` for orphan pruning, and executes blind `ALTER TABLE` statements inside `try/catch` blocks on every run.
* **Proposed Optimization**:
  1. Consolidate `performSync()` step 4 to delegate directly to the unified `syncFormulasToDatabase($force)` upsert path so schema columns are maintained in a single SQL definition.
  2. Query `INFORMATION_SCHEMA.COLUMNS` once per sync instead of firing `ALTER TABLE` exceptions on every invocation.
  3. Only run full-catalog orphan scans when shard hashes have changed or `$force = true`.

---

## 🕸️ Priority 4: Re-Sync Derived Graph & Reverse-LaTeX Lookup Artifacts *(Data Index Freshness)*

* **What's Happening Now**:
  Comparing derived index artifacts against the `14,684` formulas in the 256 shards shows:
  - [`app/config/formula_derivation_graph.json`](../app/config/formula_derivation_graph.json) (and `.gz`) currently contains **14,681 nodes** (3 newly added formulas behind the shards) and does not yet include the `lineage_confidence` provenance attribute on graph nodes/edges.
  - [`app/config/formulas_latex_index.json`](../app/config/formulas_latex_index.json) contains `13,139` entries and should be refreshed so the hex-repaired equations from `fixit_3.md` Priority 2 (`\Psi(\mathbf{r}, t)`, `\frac{\mathbf{p} \cdot \mathbf{r}}{\hbar}`, `\mathbf{p} \cdot \mathbf{r}`) resolve cleanly via reverse LaTeX lookup.
* **Proposed Optimization**:
  Rebuild `formula_derivation_graph.json` (and `.gz`) with `lineage_confidence` metadata across all `14,684` nodes, refresh `formulas_latex_index.json`, and add a node-count parity assertion (`len(dag_nodes) == len(all_formulas)`) to the test suite.

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
