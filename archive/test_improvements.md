# Meta-Audit of Platform Assessment & Testing Infrastructure (`docs/test_improvements.md`)

**Date:** 2026-10-29  
**Context:** Following the implementation of the 5 Structural Anti-Goodhart Safeguards (`docs/mandate.md` & `docs/unfuckit.md`) and the in-memory red-team test for `calculate_lhi()`, we audited `scripts/maintenance/run_project_assessment.py`, `gqs.py`, `scripts/build_formula_graph.py`, and `scripts/maintenance/audit_lineage_health.py` to answer the question:
> *"Are there any other 'tests of tests' (meta-audits) we can perform so that we are not over-exaggerating our successes?"*

This audit uncovered **5 concrete blind spots and exaggerations** where our current assessment and testing tools either fail-open (`N/A` treated as `0` violations), read frozen cache snapshots, hardcode strings/booleans, or silently dump unmapped items into catch-all buckets.

---

## 1. The "Fail-Open" Bug in `scripts/assess` (`N/A` Treated as `0 Violations`)

### The Evidence
When running `bash scripts/assess -q`, the scorecard printed:
```text
🏛️ Subtopic Knowledge Web:  N/A/1584 Platinum (100%) | Broken Links: 0
```
Yet the assessment still exited `0` with **`STRICT MODE PASSED`**.

### Root Cause (`scripts/maintenance/run_project_assessment.py`, lines 223–260)
1. **Comma-Formatting Regex Mismatch**:
   * `gqs.py status` prints `Graduated (Platinum):  1,584 (100.0%)` with a thousands comma.
   * `run_project_assessment.py` uses `re.search(r"Graduated \(Platinum\):\s*(\d+)", out)`, which fails on the comma (or stops at `1`), leaving `platinum_count = "N/A"` when `gqs.py status` either fails to match or errors out inside a restricted environment.
2. **Zero-Defaulting on Subprocess Failure**:
   * Before running `gqs.py status`, `run_project_assessment.py` initializes:
     ```python
     broken_links = 0
     lead_violations = 0
     artifact_violations = 0
     orphan_count = 0
     ```
   * It never checks whether `code == 0` or whether the regexes actually matched. If `gqs.py status` crashes, times out, or changes output format, all violation counters stay at `0` and `verify_strict_invariants()` passes!

### Proposed Improvement & Meta-Test ("Fail-Closed Subprocess Invariant")
* **Fix in `run_project_assessment.py`**:
  * Update regexes to parse comma-formatted integers (`[\d,]+`).
  * Record `gqs_status_ok = (code == 0 and isinstance(platinum_count, int))` and `lineage_status_ok = (code_lin == 0 and isinstance(lhi_score, (int, float)))`.
  * In `verify_strict_invariants()`, require both sub-auditors to succeed and return numeric values; if either is `"N/A"` or non-zero, immediately append a strict failure violation (`"Subtopic auditor failed or returned N/A (Fail-Closed Gate)"`).
* **Meta-Test in `tests/test_assess_telemetry.py`**:
  * Pass a telemetry payload with `platinum_count: "N/A"` or `lhi_score: "N/A"` into `verify_strict_invariants()` and assert that it fails (`passed is False`).

---

## 2. Frozen Cache Snapshot in `gqs.py status` (`system_health.json`)

### The Evidence
When running `.venv/bin/python3 gqs.py status`, the quality breakdown header reads:
```text
========= QUALITY BREAKDOWN (system_health.json @ 2026-06-18 15:11:39) =========
  Broken links:              0
  Lead-rule (In Media Res):  0
  Artifact (lists/bullets):  0
  Topological Orphans:       0
```

### Root Cause (`gqs.py`, lines 145–190)
* While `gqs.py status` counts total subtopics live from the 14 JSON shards (`app/config/content/*.json`), its quality violation metrics (`broken_links`, `lead_violations`, `artifact_violations`, `orphan_count`) are read from a static cached file (`system_health.json`) generated on `2026-06-18`.
* If someone edits a subtopic JSON shard and introduces a broken link or a `<ul>` list without re-running `integrity_shield.py`, `gqs.py status` (and therefore `scripts/assess -q`) continues reporting `0` violations from the old snapshot.

### Proposed Improvement & Meta-Test ("Cache Freshness Check")
* **Fix in `gqs.py` & `run_project_assessment.py`**:
  * Compare the modification timestamp (`mtime`) of `system_health.json` against the newest `mtime` across `app/config/content/*.json`.
  * If any subtopic shard is newer than `system_health.json`, mark `health_cache_stale = True` (or trigger a fast incremental audit / regenerate `system_health.json`) so stale zeros are never reported as live verification.

---

## 3. Hardcoded Strings & Inflated "100% COMPLETED" Booleans in `audit_roadmap_realization()`

### The Evidence & Root Cause (`scripts/maintenance/run_project_assessment.py`, lines 469–519)
1. **Literal Hardcoded Strings in Phase 1 (lines 469–478)**:
   ```python
   roadmap["phase_1"] = {
       "title": "Phase 1: Stabilization & Hardening",
       "status": "COMPLETED",
       "progress_pct": 100,
       "items": [
           ("100% OPS 1.0 Subtopics", "1,584 / 1,584 Articles Graduated", True),
           ("Derivation Lineage DAG", "LHI Score: 95.2 / 100 (0 Isolated)", True),
           ("Modular ES6 Explainer", "Simulations & Curator Decoupled", True),
       ]
   }
   ```
   Phase 1 does not read live telemetry at all—it prints `"95.2 / 100"` and `"1,584 / 1,584"` with hardcoded `True` booleans even if `arch_data` has different live values.

2. **File-Existence-as-Completion (line 492)**:
   ```python
   ("Lab Tools State Hydration", "1,584 / 1,584 Subtopics Mapped", launcher_exists)
   ```
   It claims `1,584 / 1,584 Subtopics Mapped` solely by checking `os.path.exists("app/logic/LabToolsLauncher.php")`.

3. **Conflating "Engine Built" with "100% Catalog Coverage" (lines 493 & 508)**:
   * `("Multi-Step Derivations", f"{proof_steps_count} / {total_formulas} Formulas (~0.7%)", proof_steps_count > 0)`
     * Only **103 of 14,687 formulas (0.7%)** have multi-step derivations (`proof_steps`), yet because `proof_steps_count > 0` is `True`, Phase 2 displays `100% [COMPLETED]`.
   * `("Sitewide Invariance Proofs", f"{cas_verified_count:,} / {total_formulas:,} Formulas Verified via CAS (62.3%)", cas_verified_count >= 5000)`
     * **9,149 of 14,687 formulas (62.3%)** are CAS-verified (leaving 5,538 unverified), yet because `9149 >= 5000` is `True`, Phase 3 displays `100% [COMPLETED]`.
   * Per **Protocol 5.A.3 (Execution vs. Tooling Distinction)**, our *engines* and *domain parity milestones* ($\ge 8$ proofs per domain) are 100% operational, but the *catalog-wide data sweeps* are at `0.7%` and `62.3%`.

### Proposed Improvement
* Wire Phase 1 directly to the live `arch_data` telemetry (`platinum_count`, `total_subtopics`, `lhi_score`, `isolated_nodes`, `overloaded_hubs == 0`).
* Distinguish **Engine & Domain Parity Readiness** from **Catalog Sweep Progress** in the Phase 2 and Phase 3 labels (or compute weighted progress from actual coverage) so the scorecard never implies that `0.7%` or `62.3%` equals a 100% completed catalog sweep.

---

## 4. Silent Catch-All Domain Fallback in `scripts/build_formula_graph.py`

### The Evidence
When `scripts/build_formula_graph.py` runs (including during `scripts/fixlineage --heal`), it prints:
```text
[WARN] 158 orphan formulas could not be mapped and were assigned to 'theoretical-physics'.
```

### Root Cause (`scripts/build_formula_graph.py`, lines 126–134)
```python
if not assigned_subtopic:
    assigned_subtopic = "theoretical-physics"
    unmapped_count += 1
```
When a formula has no matching subtopic slug in `subtopics`, `build_formula_graph.py` silently dumps it into `"theoretical-physics"`. This is the exact same catch-all antipattern as `stationary-action-principle-8836edf7` that we prohibited under **Safeguard #2 (Strict Ban on Silent Catch-All Fallbacks)**.

### Proposed Improvement
* Resolve the 158 unmapped formulas to their genuine physical subtopics (via their `category` / `topic` / parent-child subtopic affinity) or explicitly track `unmapped_subtopic_count` in the graph metadata rather than silently stuffing them into `"theoretical-physics"`.

---

## 5. Boilerplate / Copy-Paste Gaming in LHI's Physical Grounding Score

### The Evidence & Root Cause (`scripts/maintenance/audit_lineage_health.py`, lines 239–250)
Currently, `calculate_lhi()` awards the full **30 / 30 Physical Grounding points** purely on string length:
* `len(symmetry_origin) >= 20` (+10 pts)
* `len(limits_and_boundary) >= 20` (+10 pts)
* `len(semantic_variables) >= 1` (+10 pts)

If a batch script stamps the exact same 25-character generic boilerplate sentence into `symmetry_origin` or `limits_and_boundary` across 500 formulas, every single one receives full marks (`30 / 30`).

### Proposed Improvement & Meta-Test ("Anti-Boilerplate Uniqueness Check")
* **Fix in `audit_lineage_health.py`**:
  * Pre-compute frequency counts of `symmetry_origin` and `limits_and_boundary` strings across the catalog during the audit pass.
  * If an identical `symmetry_origin` or `limits_and_boundary` string is copy-pasted across $> 15$ distinct formulas, flag it as `is_boilerplate_grounding` and withhold the grounding bonus.
* **Meta-Test in `tests/test_auto_draft_lineage.py`**:
  * Extend `test_anti_goodhart_lhi_safeguards_in_memory()` to verify that copy-pasted boilerplate strings across $> 15$ nodes are penalized.
