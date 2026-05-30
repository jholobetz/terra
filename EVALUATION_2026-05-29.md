# Physics Lab — Project Evaluation

**Date:** 2026-05-29
**Author:** Claude (Opus 4.7, 1M context)
**Scope:** Read-only assessment of repository state, content pipeline, and engineering quality. No code changes.

---

A senior-undergraduate-to-graduate digital physics encyclopedia, built on a FlightPHP web skeleton but operationally dominated by a homegrown **Python content-graduation pipeline** ("GQS" — Graduation Queue Stack) that refactors legacy HTML/JSON shards into a strict "Organic Platinum Standard" (OPS).

## 1. Scale & Shape
- **1,584 subtopics** across **14 sharded JSON shards** in `app/config/content/` (160 MB on disk).
- **18,835 internal links**, **5,032 formula refs**, **7,951 pre-rendered MathJax SVGs** (cached in a single 46 MB `global_svg_cache.json`).
- **~5,400 LOC of Python** across `orchestrator.py` (1,974 lines — the TF-IDF affinity engine), `integrity_shield.py`, `gqs.py`, and ~20 maintenance scripts. Tight, focused, no test directory.
- Web layer is a thin FlightPHP shell (controllers/views/middlewares). README is still the unmodified Flight skeleton boilerplate — clearly not the project's identity.

## 2. Where Graduation Stands
The audit just ran cleanly: **0 broken links, 0 broken formulas**, shield SECURE. But three "sources of truth" disagree on platinum count:

| Source | Platinum | Pending |
|---|---|---|
| `gqs.py status` (CTA, live disk scan) | **783** | 801 |
| `system_health.json` (last refresh 20:21:57 today) | **741** | — |
| `subfiles/expansion_backlog.json` | 673 completed | 4,780 pending |

The CTA is authoritative (it parses disk in real time), but the other two registries have drifted. `expansion_backlog.json` in particular looks miscounted — 4,780 pending against 1,584 total topics implies duplicate or stale entries. Worth a `sync_backlog.py` rerun and a backlog audit.

**Shard progress (overall 49.4%):**
- 100%: classical-mechanics, condensed-matter
- 90%+: fluids-nonlinear (95%), mathematical-methods (89%)
- Mid: quantum-physics 68%, standard-model 63%, astrophysics 56%
- Laggards: electromagnetism 46%, thermodynamics 43%, relativity 42%, theoretical-physics 39%, philosophy-of-physics 36%
- Outlier: **legacy-orphans 14%** (49 nodes still legacy; needs deliberate attention)

## 3. Quality Signals
From `system_health.json`:
- 525 lead-rule violations, 909 non-technical, 896 low-depth, 97 artifact violations, 42 flag violations — i.e., the OPS gate is actively catching prose that doesn't meet the "in media res" / 650–1000-word / continuous-prose mandates. **0 pseudo-platinum** is a healthy signal: nothing is graduating without earning it.
- 314 orphans (topics with weak inbound links). With the OPS "min 2 incoming, 1 cross-hub bridge" rule, orphans are a real graduation blocker.
- Integrity shield surfaced **620 warnings**, all "Low Depth" — i.e., legacy nodes flagged for word count, not structural breakage. No errors.

## 4. Engineering Quality
**Strong:**
- `orchestrator.py` is doing serious work: dynamic TF-IDF hub signatures rebuilt from all 783 platinum nodes per run, with a documented `DF_CEILING_PCT` to filter background vocabulary — a real, non-trivial fix to false-positive "contextual leakage" errors.
- `run_gqs_sprint.py` implements a real transactional sprint: pre-flight git savepoint → static syntax guards → ingestion → integrity audit → rollback on failure. Commit log confirms this works in practice (every sprint has a paired "savepoint" + "graduate 3 nodes" commit pair).
- Token-aware design: collision-free `draft_<slug>.html` templates, log redirection to `logs/graduations/<slug>.log` to keep compiler output out of conversational context, identity-lock merging to prevent legacy formula loss. These are real lessons from operating under LLM context constraints.
- Single CLI entry point (`gqs.py`) wraps the lifecycle cleanly.

**Weak / risk areas:**
- **No automated tests** in the project tree. With 5,400 LOC of pipeline code editing 160 MB of content, this is the biggest structural risk. Integrity shield is a fixture-style check but doesn't cover the scripts themselves.
- **No CI.** `.github/` contains only `copilot-instructions.md`. Pre-commit hooks aren't visible either.
- **Git repo is 239 MB** (a prior cleanup brought it to ~50 MB; it has grown again). 46 MB `global_svg_cache.json` + 32 MB `public/cache/` plus near-continuous "Great Expansion: Content Update" commits (often 3 in the same minute) are inflating it.
- **Three drifting dashboards** (above) — the CTA claims to self-heal but is clearly not the only writer; `system_health.json` and `expansion_backlog.json` need to be regenerated downstream of the CTA, not maintained in parallel.
- **README** is still the FlightPHP skeleton stub — wildly understates what the project actually is.
- Uncommitted workspace: 4 deleted `public/cache/subtopic/*.html` files (variable-mass, pulsar-glitches, single-valued, generalized-torque). The first three match the most-recent graduation commit (`6138f912`); the deletion likely should have been in that commit.

## 5. Velocity
**376 commits in the last 24 hours**, **719 in the last 7 days** — heavy automation. Roughly 1 graduated batch (3 nodes) every ~3–4 minutes during active sprints. The "10.5-day calendar timeline" in `CLAUDE.md` to finish remaining nodes looks plausible at this cadence, but the long tail (philosophy-of-physics, theoretical-physics) is where the qualitative-prose / zero-formula rigor will slow things down.

## 6. Top Recommendations (in order)
1. **Add a tests directory** even with a thin smoke suite: OPS gate regressions, identity-merge correctness, integrity-shield invariants on a small fixture shard. Largest risk-reduction-per-effort.
2. **Reconcile the three dashboards** — make `gqs.py status` the only writer and have `system_health.json` + `expansion_backlog.json` regenerate from it. The current drift will eventually mislead a sprint decision.
3. **Audit `expansion_backlog.json`** — 4,780 pending entries against 1,584 topics is almost certainly polluted with stale/duplicate rows.
4. **Commit the 4 stale `public/cache/` deletions** with the platinum-graduation batch they belong to.
5. **Replace the FlightPHP-skeleton README** with a real project overview. Newcomers (and future-you) lose orientation fast.
6. **Move `global_svg_cache.json` out of git** (it's a derived 46 MB artifact). Will materially shrink repo growth.

Net: this is a high-discipline, well-instrumented content pipeline with real engineering investment in transactional safety and token economy. The gaps are testing, dashboard convergence, and repo hygiene — not the core architecture.
