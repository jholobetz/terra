# Independent Engineering & Content Audit — Argon First Report

**Date**: October 13, 2026  
**Auditor**: Argon (Independent First-Principles Codebase & Data Review)  
**Scope**: Full-stack evaluation of the Physics Lab repository (PHP backend, Python CAS & tooling, JSON shards, security posture, and test suite) conducted independently of the project's internal assessment tools (`scripts/assess`, `integrity_shield.py`, and `gqs.py`).

---

## Executive Verdict

Physics Lab is an ambitious, impressive interactive physics platform with several genuinely strong technical achievements—most notably its zero-dependency WebGL2 black hole raytracer, its interactive Analytical Mechanics workbench, and a well-structured SymPy CAS wrapper ([`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py)).

However, when evaluated from an external software engineering, security, and scientific data-curation standpoint, the project suffers from **"Goodhart's Law" (when a metric becomes a target, it ceases to be a good measure)**. Because the project's internal assessment tools enforce strict "100% / 0 Defect" ratchets, several parts of the codebase and dataset have been engineered or patched specifically to make the internal scorecard turn green—sometimes at the expense of production security, backend architecture, and scientific rigor.

---

## 1. Security & Production Readiness (Critical Findings)

If deployed to a public server in its current state, the application has critical authorization and Denial-of-Service (DoS) vulnerabilities:

1. **Hardcoded Admin Authority for All Visitors ([`app/logic/AuthService.php`](../app/logic/AuthService.php))**
   - `AuthService::getCurrentUser()` (lines 15–31) unconditionally resolves every visitor to `'role' => 'admin'` (`Lead Developer`), and `AuthService::hasRole()` (lines 36–39) literally consists of `return true;`.
   - Any controller endpoint that relies on `$auth->hasRole('curator', $user)` or `$auth->hasRole('admin', $user)`—including `PhysicsController::apiApplyRepair()`—grants full write access to anonymous internet users.
2. **Unauthenticated Public Write Funnel (`/physics/api/suggest-repair`)**
   - In [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php) (lines 1682–1685), the public `apiSuggestRepair()` endpoint directly aliases `$this->apiApplyRepair()`, which calls `PhysicsService::saveFormula()` and overwrites both the Git JSON shards on disk and the MariaDB `formulas` table.
3. **Unauthenticated Heavy Sync Trigger (`GET /physics/sync`)**
   - [`app/config/routes.php`](../app/config/routes.php) (line 21) exposes `GET /physics/sync` (`PhysicsController::sync()`), allowing any visitor or web crawler to trigger `PhysicsService::performSync()` on demand.
4. **Cold Subprocess Spawning per HTTP Request (`/physics/api/cas-evaluate`)**
   - In [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php) (lines 288–337), every HTTP POST spawns a fresh OS shell and Python interpreter via `shell_exec('.venv/bin/python3 lib/cas/cas_engine.py ...')`.
   - While internal benchmarks report `"7ms latency"` (measured inside an already-warm Python process), spawning a cold Python + SymPy process over HTTP takes **~150–250ms** of CPU time per request and has no rate limiting—making it trivial to exhaust server CPU/memory with concurrent requests.

---

## 2. Backend Architecture & Database Engineering

1. **Monolithic "God Classes"**
   - [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php) is **1,862 lines** long with **40+ route handlers**, mixing public HTML views, search APIs, CAS evaluation, AI formula generation (`shell_exec` to `gqs.py`), review moderation, and admin console triggers in a single class.
   - [`app/logic/PhysicsService.php`](../app/logic/PhysicsService.php) is **1,950 lines** long, combining PDO database queries, file-system JSON shard parsing, regex LaTeX sanitization, breadcrumb graph traversal, and SVG sprite manipulation.
2. **Flawed Database Synchronization (`PhysicsService::syncFormulasToDatabase()`)**
   - **Update-Only Bug**: In [`app/logic/PhysicsService.php`](../app/logic/PhysicsService.php) (lines 66–77), `syncFormulasToDatabase()` prepares an `UPDATE formulas SET ... WHERE id = ?` statement instead of an `INSERT INTO formulas ... ON DUPLICATE KEY UPDATE`. If a new formula is added to a JSON shard and `syncFormulasToDatabase()` runs, it will silently update `0` rows in MariaDB if the `id` does not already exist.
   - **Unbatched N+1 Queries Without a Transaction**: When shards change, it executes individual `UPDATE` queries inside a nested `foreach` loop without wrapping them in `$pdo->beginTransaction()` / `$pdo->commit()`, risking partial state and slow I/O.
3. **Brittle Exclusion Lists in `PhysicsService::loadAllShards()`**
   - Instead of reading an explicit manifest of the 13 subtopic shard filenames, `loadAllShards()` (lines 247–255) runs `scandir('app/config/content/')` and loads *every* `.json` file except a hardcoded blacklist of 13 filenames. Any new auxiliary `.json` file placed in `app/config/content/` is accidentally merged into `$this->physicsContent['subtopics']`.

---

## 3. Data & Scientific Content Quality (Independent Sample)

Inspecting raw formula shards (e.g., [`app/config/content/formulas/3f/shard_3f.json`](../app/config/content/formulas/3f/shard_3f.json)) and subtopic JSON files directly reveals a contrast between genuine quality and automated filler:

1. **Synthetic / Hallucinated Lineage Edges (Gaming the LHI Score)**
   - The internal scorecard reports a **95.2/100 Lineage Health Index** and **0 Isolated Nodes** across 14,682 formulas.
   - However, inspecting how `0 Isolated Nodes` was achieved reveals automated graph padding:
     - In [`scripts/maintenance/run_project_assessment.py`](../scripts/maintenance/run_project_assessment.py) (line 1498), the `--heal` function patches any isolated formula by inventing a synthetic parent slug `f"axiom-{domain.lower().replace(' ', '-')}"`.
     - In [`app/config/content/formulas/3f/shard_3f.json`](../app/config/content/formulas/3f/shard_3f.json) (lines 89–95), the formula `discovery-event-abf7cc1a` ($\epsilon \approx 2.28 \times 10^{-3}$ for neutral kaon CP violation) lists `"subcomponents": ["yukawa-limit-78bb72d6", "success-rate-0c8c402e"]`—links that have no mathematical derivation relationship to kaon CP violation.
2. **Repetitive Boilerplate in Formula Prose**
   - In [`app/config/content/formulas/3f/shard_3f.json`](../app/config/content/formulas/3f/shard_3f.json), nearly every single formula's `interpretation` field begins with the exact same mechanical prefix:
     > *"The formula `<LaTeX>` is interpreted as follows: ..."*
   - While subtopic prose enforces a strict "Anti-Formulaic Integration Rule," the 14,682 formula descriptions rely heavily on this exact formulaic template.
3. **OPS 1.0 Prose Trade-Offs (Readability vs. Uniformity)**
   - **Strength**: Every subtopic article is 650–1,000 words, free of broken markdown or AI meta-talk, and rich in notation.
   - **Weakness**: Because OPS 1.0 strictly bans subheadings (`<h3>`), bulleted lists (`<ul>`/`<li>`), and tables, and forces 2–4 MathJax expressions into *every* paragraph, articles render as dense walls of 4–6 long `<p>` blocks. For a student or researcher trying to quickly scan boundary conditions, assumptions, or key takeaways, continuous prose is harder to scan than structured reference text.

---

## 4. Testing & Telemetry Integrity ("Grading Its Own Homework")

1. **Inflated Test Count in Documentation**
   - [`GEMINI.md`](../GEMINI.md) and [`docs/roadmap.md`](roadmap.md) claim **"3,100+ tests"** / **"3,150+ Pytest tests in ~13s"**.
   - In reality, running `.venv/bin/python3 -m pytest tests/` collects **236 test items** across 31 files and takes **~26–28 seconds**.
2. **Zero Native PHP Unit Tests**
   - Despite the web application being written in PHP (FlightPHP), there is no PHPUnit test suite ([`composer.json`](../composer.json) only requires `flightphp/core` and `monolog/monolog`). Core PHP services (`PhysicsService`, `FormulaReviewService`, `VariableAggregator`, `LabToolsLauncher`) are tested only indirectly via regex scans or a handful of Python `php -r` subprocess wrappers.
3. **Hardcoded Fallback Telemetry in `run_project_assessment.py`**
   - In [`scripts/maintenance/run_project_assessment.py`](../scripts/maintenance/run_project_assessment.py) (lines 469–473), if the lineage graph probe fails or errors out, the `except Exception:` block silently falls back to hardcoded success numbers (`lhi_score = 95.2`, `isolated_nodes = 0`, `dag_edges = 44691`), masking potential failures.

---

## 5. Genuine Bright Spots (What Works Exceptionally Well)

To be completely fair, several parts of the project stand out as genuinely well-engineered:
- **Frontend Interactive Engines**: The WebGL2 relativistic black hole raytracer ([`public/js/simulations/relativistic-black-hole.js`](../public/js/simulations/relativistic-black-hole.js)), the chaotic pendulum with live Poincaré sections ([`public/js/simulations/pendulum.js`](../public/js/simulations/pendulum.js)), and the Legendre Transformer ([`public/js/legendre_transformer.js`](../public/js/legendre_transformer.js)) are responsive, dependency-free, and mathematically authentic.
- **SymPy CAS Engine ([`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py))**: Cleanly implements AST depth/node-count security guards, POSIX `SIGALRM` timeouts, Legendre velocity Hessian checks, and SI dimensional homogeneity verification.
- **Cross-Encyclopedia Hydration ([`app/logic/LabToolsLauncher.php`](../app/logic/LabToolsLauncher.php))**: Every subtopic seamlessly links into relevant interactive calculators or simulations with pre-populated URL parameters.

---

## Summary of Priority Recommendations

| Priority | Area | Actionable Fix |
| :--- | :--- | :--- |
| **P0 (Security)** | [`app/logic/AuthService.php`](../app/logic/AuthService.php) & Write Routes | Gate `hasRole() => true`, `/physics/sync`, `/physics/api/suggest-repair`, and `/physics/admin/*` behind a strict local/environment check (`APP_ENV === 'development'` + `127.0.0.1` IP check or real session auth). |
| **P1 (Data Sync)** | [`app/logic/PhysicsService.php`](../app/logic/PhysicsService.php) | Replace the unbatched `UPDATE` loop in `syncFormulasToDatabase()` with a transactional `INSERT INTO formulas ... ON DUPLICATE KEY UPDATE` batch upsert. |
| **P1 (Telemetry)** | [`scripts/maintenance/run_project_assessment.py`](../scripts/maintenance/run_project_assessment.py) & Docs | Remove hardcoded fallback metrics in `except` blocks so broken probes fail loudly, and update docs to reflect the true Pytest count (236 tests). |
| **P2 (Architecture)** | [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php) | Split the 1,862-line controller into focused controllers (`EncyclopediaController`, `FormulaApiController`, `AdminController`). |
| **P2 (Content DAG)** | [`app/config/formula_derivation_graph.json`](../app/config/formula_derivation_graph.json) | Prune synthetic `axiom-*` dummy parents and non-physical subcomponent edges—even if it lowers the LHI score from 95.2 to an honest ~80—so every derivation link is scientifically valid. |
