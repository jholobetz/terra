# Unified Auditor Hardening & Shard Data Remediation Plan (`docs/fixit_plan.md`)

**Date:** 2026-11-07  
**Status:** Active Execution Plan  
**Supersedes:** [`archive/test_improvements.md`](../archive/test_improvements.md) and [`archive/high_confidence_in_accuracy.md`](../archive/high_confidence_in_accuracy.md) (plus completed predecessors [`archive/corrupted_strings.md`](../archive/corrupted_strings.md) and [`archive/unfuckit.md`](../archive/unfuckit.md))  
**Guiding Mandate:** Intellectual Honesty & Structural Rigor ([`docs/mandate.md`](mandate.md) & [`CLAUDE.md`](../CLAUDE.md))

---

## 1. Executive Synthesis: Two Halves of the Same Coin

Following the complete remediation of all 257 corrupted LaTeX `equation` strings, 6 explicit garbage records, 17 overloaded star-hubs, and 25 zero-affinity parent–child links, we audited both **our measurement instruments** (the test/assessment scripts) and **our underlying shard data** (all **14,681 formulas** across 256 hex shards).

Those two audits revealed two sides of the exact same problem:
1. **Instrument Blind Spots (`test_improvements.md`)**: Why [`scripts/assess`](../scripts/assess), [`gqs.py status`](../gqs.py), and [`scripts/fixlineage`](../scripts/fixlineage) report `A+ / 99.8` even when underlying issues exist (fail-open `N/A` regexes, frozen cache snapshots, length-only LHI checks, and conflating engine readiness with catalog coverage).
2. **Shard Data Liabilities (`high_confidence_in_accuracy.md`)**: The concrete formula metadata and lineage gaps that those instrument blind spots allowed to hide in the 256 shards (`858` copy-pasted boilerplate records, `783` `"Custom Physical Relation"` titles, `296` desynchronized `semantic_variables` dicts, `172` unmapped domain orphans, `2,833` bare symbols/fragments, `5,535` unverified CAS records, and `14,005` heuristic lineage links).

---

## 2. Current Confidence Matrix Across All Platform Data Layers

| Data Layer | Confidence Level | Current Empirical Reality | Gate Status |
| :--- | :--- | :--- | :--- |
| **LaTeX Equation Syntax (`equation`)** | **High (`100%`)** | All `14,681` equations are syntactically valid LaTeX with `0` prose bleed, `0` raw MathML tags, and `0` control-char corruptions. | **Locked** (`is_corrupted_equation()` in [`audit_lineage_health.py`](../scripts/maintenance/audit_lineage_health.py)) |
| **Graph Shape & Affinity Constraints** | **High (`100%`)** | `0` loops, `100%` reciprocity, `0` overloaded hubs ($>25$, max is `19`), `0` cross-domain zero-affinity links. | **Locked** (`has_parent_child_affinity()` in [`audit_lineage_health.py`](../scripts/maintenance/audit_lineage_health.py)) |
| **Multi-Step Proofs (`derivation_steps`)** | **High (`100%`)** | `103` multi-step derivation proofs verified across all 12 canonical domains ($\ge 8$ per domain). | **Locked** ([`tests/test_derivation_steps.py`](../tests/test_derivation_steps.py)) |
| **Domain Mapping Closure** | **High (`98.8%`)** | `14,509` formulas mapped to canonical domains; **`172` orphan formulas (`1.2%`)** currently marked `"unmapped"` after removing the `"theoretical-physics"` catch-all fallback in [`scripts/build_formula_graph.py`](../scripts/build_formula_graph.py). | **Needs Shard Fix (`172` records)** |
| **Variable Dictionary Alignment (`semantic_variables`)** | **Moderate (`98.0%`)** | **`296` formulas (`2.0%`)** have `semantic_variables` keys where *none* of the listed variable keys appear in the `equation` string. | **Needs Shard Fix + New Gate** |
| **Symmetry & Boundary Prose (`symmetry_origin`, `limits_and_boundary`)** | **Moderate (`94.2%`)** | **`858` formulas (`5.8%`)** share word-for-word copy-pasted boilerplate `symmetry_origin` and `limits_and_boundary` strings (`"Subject to asymptotic boundary conditions and non-relativistic conservation limits."`). *(Note: `783` formulas also carry the default `"Custom Physical Relation"` title, which is a normal lifecycle state for newly introduced prose equations and should be minimized over time rather than gated as a failure).* | **Fix False Boilerplate; Track `"Custom Physical Relation"` as Advisory** |
| **Equation vs. Symbol Classification** | **Moderate (`80.7%`)** | `11,848` records are relational equations (`=`, `\approx`, `<`, `>`, `\to`), while **`2,833` records (`19.3%`)** are standalone variable symbols (`m_2`, `q_i`) or bare numbers (`10^7`, `1/4`). | **Needs Schema Classification** |
| **CAS Dimensional Verification (`cas_validation`)** | **Moderate (`62.3%`)** | `5,924` `HOMOGENEOUS` equations + `3,222` `DIMENSIONAL_EXPRESSION` terms verified (`9,146` total); **`5,535` formulas (`37.7%`)** have no `cas_validation` record. | **Needs CAS Sweep Campaign** |
| **True Mathematical Derivation (`parent_formula_id`)** | **Low-to-Moderate** | `132` links are curated/verified (`0.9%`) and `574` are roots; **`14,005` links (`99.1%`)** are heuristic neighborhood/symbol matches. | **Tracked via `lineage_confidence`** |

---

## 3. Crossover Map: Instrument Blind Spots $\leftrightarrow$ Data Liabilities

| Instrument Blind Spot (`test_improvements.md`) | Corresponding Data Liability (`high_confidence_in_accuracy.md`) | Why Order of Operations Matters |
| :--- | :--- | :--- |
| **1. Fail-Open `N/A` Bug in [`run_project_assessment.py`](../scripts/maintenance/run_project_assessment.py#L223-L260)**<br/>`bash scripts/assess -q` prints `Subtopic Knowledge Web: N/A/1584 Platinum` because regex `r"Graduated \(Platinum\):\s*(\d+)"` fails on the thousands comma in `1,584`, yet still passes `STRICT MODE PASSED`. | *(Subtopic Telemetry Layer)* | Can be fixed immediately in Step 1 so `scripts/assess` never treats `"N/A"` or a crashed sub-auditor as `0` violations. |
| **2. Frozen Cache Snapshot in [`gqs.py status`](../gqs.py#L145-L190)**<br/>Reads `broken_links`, `lead_violations`, and `artifact_violations` from `system_health.json` (`2026-06-18`) without checking if any subtopic `.json` shard was modified more recently. | *(Subtopic Telemetry Freshness)* | Can be fixed immediately in Step 1 by comparing `mtime` of `system_health.json` against `app/config/content/*.json`. |
| **3. Hardcoded Strings & Conflating "Engine Built" with "100% Data Sweep" in [`audit_roadmap_realization()`](../scripts/maintenance/run_project_assessment.py#L469-L519)**<br/>Phase 1 hardcodes `"95.2 / 100"`; Phase 2 & 3 report `100% [COMPLETED]` because `103 > 0` (`0.7%` proofs) and `9,146 >= 5000` (`62.3%` CAS). | **Liability A (`99.1%` Heuristic Lineage) & Liability E (`37.7%` Unverified CAS)** | Can be fixed immediately in Step 1 by wiring live `arch_data` telemetry into Phase 1 and distinguishing **Engine / Parity Readiness (`100%`)** from **Catalog Sweep Coverage (`0.7%` / `62.3%`)**. |
| **4. Catch-All Domain Fallback in [`build_formula_graph.py`](../scripts/build_formula_graph.py)**<br/>Previously dumped unmapped formulas into `"theoretical-physics"`. Now fixed to mark them `"unmapped"`. | **172 Unmapped Orphan Formulas**<br/>`172` formulas in the shards lack `subtopics` or `category` mappings. | Must populate authentic `subtopics`/`category` on those 172 records in Step 2 so `unmapped` drops from `172` to `0`. |
| **5. Length-Only Physical Grounding Check in [`calculate_lhi()`](../scripts/maintenance/audit_lineage_health.py#L431-L441)**<br/>Awards full 20/20 points solely for `len(symmetry_origin) >= 20` and `len(limits_and_boundary) >= 20`, with no check against copy-pasted boilerplate or `"Custom Physical Relation"` titles. | **Liability B (`858` Boilerplate Formulas & `783` `"Custom Physical Relation"` Titles) & Liability D (`296` Desynchronized `semantic_variables`)** | **Must repair the data in Step 2 BEFORE enabling the strict LHI penalty in Step 3**, otherwise enabling the gate first will immediately fail 1,154 formulas. |

---

## 4. Phased Execution Plan

### Phase 1: Harden the Assessment Plumbing (Immediate — Zero Shard Mutations)

1. **Fix the Fail-Open `N/A` Bug in [`scripts/maintenance/run_project_assessment.py`](../scripts/maintenance/run_project_assessment.py)**:
   * Update the `gqs.py status` regexes (lines 223–260) to match comma-formatted integers (`[\d,]+`).
   * Track `gqs_status_ok = (code == 0 and isinstance(platinum_count, int))` and `lineage_status_ok = (code_lin == 0 and isinstance(lhi_score, (int, float)))`.
   * In `verify_strict_invariants()`, fail closed if `platinum_count == "N/A"` or `lhi_score == "N/A"`.
   * Add a red-team unit test in [`tests/test_assess_telemetry.py`](../tests/test_assess_telemetry.py) asserting that `verify_strict_invariants()` returns `False` when `platinum_count` or `lhi_score` is `"N/A"`.
2. **Add Cache Freshness Validation to [`gqs.py`](../gqs.py) (`system_health.json`)**:
   * Compare `os.path.getmtime("system_health.json")` against the newest `mtime` across `app/config/content/*.json`.
   * Display whether `system_health.json` is `FRESH` or `STALE` relative to the subtopic shards, and refresh it if stale.
3. **Wire Live Telemetry & Honest Coverage Labels in [`audit_roadmap_realization()`](../scripts/maintenance/run_project_assessment.py#L469-L519)**:
   * Replace hardcoded Phase 1 strings (`"95.2 / 100"`, `"1,584 / 1,584"`) with live values from `arch_data`.
   * Clarify Phase 2 and Phase 3 item labels to distinguish **Engine & Domain Parity Milestones (100% Complete)** from **Ongoing Catalog Sweeps (`103` multi-step proofs; `9,146 / 14,681` CAS verified)**.

---

### Phase 2: Remediate High-Priority Shard Data Liabilities

1. **Fix the 296 Desynchronized `semantic_variables` Records (`Liability D`)**:
   * Audit all 296 formulas where no `semantic_variables` key appears in `equation`.
   * Re-extract and align `semantic_variables` keys with the actual LaTeX symbols present in each formula's `equation` and `conceptual_definition`.
2. **Resolve the 172 Unmapped Domain Orphans (`Item #4`)**:
   * Assign authentic `subtopics` and `category` values to the 172 formulas currently marked `"unmapped"` in `scripts/build_formula_graph.py` based on their physical content and parent/child neighborhood, reducing `unmapped` nodes from `172` to `0`.
3. **Replace the 858 Copy-Pasted Boilerplate Grounding Records & Enrich `"Custom Physical Relation"` Titles Where Contextually Clear (`Liability B`)**:
   * **Important Lifecycle Rule on `"Custom Physical Relation"`**: Whenever new definitions or prose equations are introduced into the platform (via [`lib/pipeline/formula_pipeline.py`](../lib/pipeline/formula_pipeline.py), [`app/logic/FormulaReviewService.php`](../app/logic/FormulaReviewService.php), or [`app/logic/LatexSanitizer.php`](../app/logic/LatexSanitizer.php)), they are initialized with `"title": "Custom Physical Relation"` (which [`public/js/equation_explainer.js`](../public/js/equation_explainer.js#L1087) also uses to toggle the *"Propose / Register Equation"* curation badge). Therefore, `"Custom Physical Relation"` is a normal, ongoing lifecycle state that we can minimize via opportunistic enrichment, **not** an error condition to block or penalize in CI.
   * **What MUST be fixed and gated**: Replace the 858 identical copy-pasted boilerplate strings in `symmetry_origin` and `limits_and_boundary`:
     * `"Formulated in coordinate-free tensor or vector notation, maintaining spatial rotation and translation invariance across inertial frames."`
     * `"Subject to asymptotic boundary conditions and non-relativistic conservation limits."`
     with authentic, equation-specific `symmetry_origin` and `limits_and_boundary` descriptions (ensuring relativistic and quantum formulas never claim *"non-relativistic conservation limits"*).
   * Follow **Anti-Goodhart Safeguard #4**: inspect and report the **top 5 most-affected shards** and **5 random spot-check samples** before committing.

---

### Phase 3: Lock the New Anti-Boilerplate & Variable-Alignment Gates in CI

Once Phase 2 brings the shard counts of copy-pasted grounding strings and desynchronized `semantic_variables` down to `0`:

1. **Upgrade [`calculate_lhi()`](../scripts/maintenance/audit_lineage_health.py) in `scripts/maintenance/audit_lineage_health.py`**:
   * Pre-compute frequency counts of `symmetry_origin` and `limits_and_boundary` strings across the catalog; if an identical string is repeated across $> 15$ formulas, flag it as `is_boilerplate_grounding = True` and withhold the Physical Grounding score. *(Do NOT penalize `"Custom Physical Relation"` titles, as new prose equations legitimately enter the system with that default title).*
   * Verify that at least one key in `semantic_variables` matches a symbol in `equation` before awarding the +10 `semantic_variables` grounding points.
2. **Add Red-Team & Sitewide Unit Tests in [`tests/test_auto_draft_lineage.py`](../tests/test_auto_draft_lineage.py)**:
   * Test in-memory that copy-pasted boilerplate strings ($>15$ duplicates) and mismatched `semantic_variables` are flagged and penalized.
   * Lock a sitewide assertion that `0` formulas have $>15$-duplicate boilerplate grounding strings or completely desynchronized `semantic_variables`.

---

### Phase 4: Structural Classification & Long-Horizon Verification Campaigns

1. **Classify Standalone Symbols/Expressions vs. Equations (`Liability C` — `2,833` records)**:
   * Add an explicit `record_type` classification (`"equation"` vs. `"relation"` vs. `"symbol_or_term"`) across the shards so the `11,848` relational equations are cleanly distinguished from the `2,833` standalone symbols/expressions (`m_2`, `q_i`, `10^7`).
2. **Expand Symbolic CAS Validation (`Liability E` — `5,535` unverified records)**:
   * Run `scripts/cascheck` across the remaining `5,535` unverified formulas to populate `cas_validation` (`HOMOGENEOUS` or `DIMENSIONAL_EXPRESSION`).
3. **Gradual Upgrade of Heuristic Lineage Links (`Liability A` — `14,005` heuristic links)**:
   * Use SymPy CAS (`scripts/cascheck`) and subtopic derivation chains to progressively verify and upgrade `heuristic` parent–child links to `cas_verified` or `curated`.
