# Physics Lab Co-Developer Guide — Universal CLAUDE.md

This document is the **Supreme Authority** for all architectural, stylistic, and procedural decisions in the Physics Lab project. All AI systems and human developers MUST adhere to these mandates to maintain the "Organic Platinum Standard" (OPS) of a university-level digital physics encyclopedia and mathematical manifold.

---

## 🚀 1. Quick Reference Commands

All Python operations must be executed using the project's local virtual environment (`.venv/`). The system interpreter should never be used for maintenance tasks.

### 🎛️ Unified Session Controller (Recommended)
Our unified developer CLI manages the entire GQS pipeline lifecycle, offering automatic backlog synchronization, status dashboards, structure-compliant templating, and compilation:
```bash
# Check current database metrics, active drafts, and next priority targets
.venv/bin/python3 gqs.py status

# Automatically scaffold the next N GQS targets into subfiles/batch_payload.json
.venv/bin/python3 gqs.py template <N>

# Graduate and compile all drafted targets in subfiles/batch_payload.json
.venv/bin/python3 gqs.py ingest

# Run a structural and formula validation audit (site-wide or single slug)
.venv/bin/python3 gqs.py audit [slug]

# Replenish the pre-resolved GQS stack depth and sync the active sprint
.venv/bin/python3 gqs.py refill [N]
```

### 🧮 Direct Equation & Lineage Repair Tooling
* **Direct URL Equation Repair (`fixlatex`)**: Audits, decorrupts, and repairs LaTeX equations, resets dynamic MathJax rendering, and syncs shard definitions:
  ```bash
  scripts/fixlatex "<URL|ID|LaTeX>" ["<optional hint>"]
  # Examples:
  # scripts/fixlatex "http://localhost:8000/physics/equation-explainer?id=schrodinger-equation"
  # scripts/fixlatex "\mathbf{F} = m \mathbf{a}" "Newton's Second Law"
  ```
* **Lineage Health Index (LHI) & Graph Audit (`fixlineage`)**: Audits the mathematical derivation tree (DAG), detects circular loops, and reports LHI metrics across all 14,613 formulas:
  ```bash
  # Check overall encyclopedia lineage score and distribution:
  scripts/fixlineage --summary

  # Audit a specific formula or heal isolated nodes:
  scripts/fixlineage --target-id <formula-id>
  scripts/fixlineage --heal
  ```

### 🛡️ Guarded Sprint Orchestrator (Token-Saver & Zero-Interruption)
Consolidates the entire GQS cycle into a single transaction, automating syntax checking, compilation, and post-graduation audits with local git backups and self-healing rollbacks:
```bash
# Execute an autonomous, quality-guarded sprint for N stack targets
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>

# Run static syntax and OPS style checks without compiling (Dry-Run Mode)
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N> --dry-run
```

### 🛡️ Validation & Test Suite
* **Unified Platform Health & Assessment Auditor (`scripts/assess`)**:
  Runs a modular health assessment across tests, documentation, and diagnostics:
  ```bash
  # Core assessment (Pytest + platform scorecard)
  scripts/assess

  # Hybrid deep assessment (Tests + Docs review + Lineage LHI + CAS latency)
  scripts/assess --all

  # Diagnostics and docs audit only (skipping pytest for speed)
  scripts/assess --no-tests --diagnostics --docs

  # Output an AI Agent Prompt with live telemetry for narrative report generation
  scripts/assess --prompt
  ```
* **Automated Pytest Suite**: Runs the full regression net (3,100+ tests covering schemas, invariants, delimiters, and syntax):
  ```bash
  .venv/bin/python3 -m pytest tests/
  ```
* **Sitewide Integrity Shield Audit**: Scans all 14 content shards, 256 formula shards, 14,613 formulas, 100% manifold closure, and MathJax renderings:
  ```bash
  .venv/bin/python3 integrity_shield.py
  ```
* **Prose Equation Manifold Audit**: Checks whether every LaTeX equation in prose resolves to a canonical identity:
  ```bash
  php scripts/audit_prose_equations.php
  ```

---

## 🧮 2. Direct URL Equation Repair Protocol (AI Agent Directive)

Whenever the user provides a local `equation-explainer` URL (matching `http://localhost:8000/physics/equation-explainer...`) or a formula ID/LaTeX snippet in the prompt, with or without an accompanying hint or reference text:

1. **Automatic Intent Recognition**: Classify the input immediately as an Equation Repair / TeX Decorruption task.
2. **Execute Repair Engine (Single-Pass Protocol)**:
   - Run the repair tool in **exactly one** terminal invocation:
     ```bash
     scripts/fixlatex "<URL|ID|LaTeX>" ["<hint or reference text>"]
     ```
   - **Zero-Interruption Mandate (No Repetitive Modals)**:
     - **Strict Ban on Terminal Inspection Commands**: Never run `git diff`, `git status`, or shell file inspections via `run_command`. The agent's file tools already track changes in memory.
     - **Strict Ban on Ad-Hoc Terminal Scripts**: Never run one-off `python3 -c` or `php -r` patch commands via `run_command`.
     - **Use Sandboxed Editor for Manual Touch-ups**: If shard prose requires additional manual editing beyond what `fixlatex` handles, edit the shard file directly using the agent's built-in file editing tool (`replace_file_content`), which runs safely inside the sandbox with 0 user prompts.
3. **Verify Integrity**: Confirm that:
   - The formula definition in `app/config/content/formulas/[xx]/shard_[xx].json` is updated.
   - TeX corruptions in prose fields (`description`, `interpretation`, etc.) are sanitized.
   - MariaDB record is updated with `equation_svg = NULL` to trigger clean dynamic MathJax rendering.
   - `app/config/formulas_latex_index.json` mapping is synchronized.
4. **Synthesize Output**: Return a concise summary detailing:
   - Resolved Formula ID
   - Target Shard Path
   - Cleaned LaTeX equation
   - Summary of applied prose decorruptions and hint updates

---

## 🏛️ 3. The Organic Platinum Standard (OPS) Quality Gates

To graduate a subtopic from standard "legacy" to "platinum," it must pass these strict guidelines enforced by `integrity_shield.py`:

### A. Qualitative Prose Mandates
* **The "In Media Res" Lead**: The first sentence of the first paragraph must lead directly with a physical principle, identity, or derivation.
  * *Forbidden*: Starting with "The [Topic] is..." or "This concept refers to...".
  * *Forbidden*: Mentioning the subtopic's title inside the first 15 words of the opening paragraph.
  * *Forbidden*: Self-referential meta-talk ("In this article...", "This summary covers...").
  * *Example*: *"The invariance of the spacetime interval under Lorentz transformations necessitates a pseudo-Riemannian metric..."*
* **Zero-Artifact Continuous Prose**: Only high-density technical HTML prose is allowed.
  * *Forbidden*: Lists, bullets, or numbered elements (`<ul>`, `<li>`, `<ol>`).
  * *Forbidden*: Fragmented headers or summaries inside content strings.
  * *Syntax Purity*: Wrap all paragraphs in `<p>` tags. Bold key terms using `<strong>` tags only. **Strict ban on markdown double asterisks (`**`) or underscores (`__`) inside JSON content strings.**
* **The Anti-Formulaic Integration Rule**: Formulaic introductory phrases for mathematical equations (e.g., *"This is defined by the following equation..."*, *"The formula for this is..."*) are strictly forbidden. Mathematical equations must be woven organically as grammatical continuations of physical sentences.
* **MathJax Frequency & Rich Variable Density**: Every single paragraph of every graduated subtopic node—including purely conceptual, interpretive, or philosophical nodes—MUST contain at least **2 to 4 distinct inline MathJax expressions** (e.g. \( g_{\mu\nu} \), \( |\Psi^+\rangle \), \( \hat{H} \)) to eliminate visual "walls of text."
* **Explicit Variable Coupling**: Never reference a physics field, parameter, coordinate, or concept purely by name if it has a standard symbol representation; couple it immediately to its mathematical symbol (e.g., writing "metric tensor \( g_{\mu\nu} \)" instead of just "the metric tensor").
* **Word Count Cushion**: Standard subtopics must contain **650 to 1,000 words** of stripped prose (~800-950 raw words). Category Hub Overviews (`-overview` slugs) are targeted at **800 to 1,000 words**.

### B. Topological Symmetries
* Minimum of **5 outgoing links** to neighboring subtopics.
* Minimum of **2 incoming links** from other subtopics.
* Minimum of **1 cross-hub bridge** connecting to a completely different primary Pillar Hub.

---

## 🏛️ 4. Core Platform Architecture

### A. The Fundamental Data Model: Production MariaDB vs. Development Shards
The platform maintains a deliberate dual-layer operational model:
1. **Production Operational Engine (MariaDB)**:
   * In production, live queries run against the **MariaDB** relational store (`formulas`, `subtopics`, `topics`, `reviews`).
   * When `PhysicsService::loadFormula()` or `fetchAndPrepare()` is called, it queries indexed MariaDB tables directly (leveraging InnoDB memory buffer pools).
   * Static subtopic views are served via the high-performance disk cache (`public/cache/subtopic/{slug}.html`), bypassing database load on repeat visits.
   * **The 256 JSON shards are NOT an operational bottleneck in production.**
2. **Development & Offline Source of Truth (Git JSON Shards)**:
   * The **256 hex shards** (`app/config/content/formulas/[00-ff]/shard_[00-ff].json`) and **14 subtopic files** (`app/config/content/*.json`) serve as the **version-controlled source of truth in Git**.
   * They enable offline development, Git branching/diffs, preview mode (`?preview=1`), and automated CI test suites (`pytest`, `integrity_shield.py`, `gqs.py`) without requiring a live, running database daemon.
   * Shard file reads on disk are strictly an offline development, preview, or database-unavailable fallback mechanism.
3. **The Service Synchronization Bridge (`PhysicsService.php`)**:
   * Bridges the two layers: `PhysicsService::saveFormula()` serves as the single write funnel, atomically updating the Git JSON shard, MariaDB record, and reverse LaTeX trie (`formulas_latex_index.json`).
   * Deployment synchronization (`syncFormulasToDatabase()`) uses SHA-256 hash registries (`formulas_hash_registry.json`) to detect changed shards and update MariaDB in batch.

### B. Mathematical Derivation Lineage Graph (DAG)
* Lineage is tracked as an acyclic graph in `app/config/formula_derivation_graph.json` (and `.gz`).
* Formulas connect hierarchically from foundational axioms down to phenomenological identities.
* The **Lineage Health Index (LHI)** continuously benchmarks derivation density on a 0–100 scale (currently at **95.2 / 100**, with **0 isolated nodes**).

### C. Equation Explainer & Dissection Suite
* Located at `/physics/equation-explainer`.
* Deconstructs raw LaTeX into base variables and parameter modifiers.
* Uses dynamic MathJax 3.x vector rendering for interactive exploration and SVG sprites for static encyclopedia hubs.

### D. Centralized Math Delimiter Architecture
* Delimiter parsing, sanitization, and presentation flow through a unified pipeline (`docs/delimiters.md`):
  * **Backend Write Funnel**: `PhysicsService::saveFormula()` canonicalizes prose math to `$ ... $`, strips HTML tags, and sanitizes escapes before committing to shards or MariaDB.
  * **Shared Test Helper**: Tests and CI gates import `scripts.lib.delimiters` (`strip_math_blocks`, `validate_narrative_delimiters`) for unified, delimiter-agnostic verification.
  * **Frontend Formatter**: `public/js/math_prose_formatter.js` formats math prose dynamically for the Equation Explainer, Formula Inspector, and Graph Tooltips.


---

## 🛠️ 5. Live Platform Capability Matrix & Audit-First Protocol

### A. The Mandatory "Audit-First" Engineering Protocol
To eliminate counter-productive amnesia, glossing over existing features, or reinventing existing code:
1. **Pre-Flight Asset Audit**: Before proposing, architecting, or discussing any roadmap phase or feature, all AI assistants and developers MUST inspect existing repository files (`lib/`, `app/logic/`, `public/js/`, `scripts/`) to identify already implemented components.
2. **Grounding in Code Reality**: Always state what is **already operational** before outlining incremental deltas. Never assume an engine or tool is unbuilt simply because an overall roadmap phase is not yet marked 100%.
3. **Execution vs. Tooling Distinction**: Distinguish clearly between an **Engine/Tool** (software that exists and runs) and a **Data Sweep/Campaign** (applying that engine across the 14,613 formulas or 1,584 subtopics).

### B. Live Platform Capability Matrix (Do NOT Reinvent or Re-propose)
| Capability / System | Implementation Path | Live Status & Capabilities | Verification Command |
| :--- | :--- | :--- | :--- |
| **Symbolic CAS Engine** | [`lib/cas/cas_engine.py`](file:///Users/holobetj/code/gemini/terra/lib/cas/cas_engine.py)<br/>[`/physics/api/cas-evaluate`](file:///Users/holobetj/code/gemini/terra/app/controllers/PhysicsController.php#L288) | **Operational (168ms latency)**. Performs symbolic velocity inversions $\dot{q}_i(q, p)$, velocity Hessian matrices $W_{ij}$, singular constraint detection, Legendre transformations to Hamiltonians $H = \sum p\dot{q} - L$, asymptotic limits ($x \to 0, \infty$), Taylor expansions, and SI dimensional homogeneity checks. | `.venv/bin/python3 -m pytest tests/test_cas_engine.py` |
| **Analytical Mechanics Workbench** | [`public/js/legendre_transformer.js`](file:///Users/holobetj/code/gemini/terra/public/js/legendre_transformer.js)<br/>[`app/views/physics/legendre_transformer.php`](file:///Users/holobetj/code/gemini/terra/app/views/physics/legendre_transformer.php) | **Operational**. 10 publication-grade classical & relativistic presets (Harmonic, Pendulum, Duffing, Relativistic, EM Vector Potential, Rotating Frame, Central Force, Kepler, 3D Spherical, Singular Constrained). | Browser at `/physics/legendre-transformer` |
| **WebGL Raytracing Harness** | [`public/js/lib/webgl_physics_harness.js`](file:///Users/holobetj/code/gemini/terra/public/js/lib/webgl_physics_harness.js)<br/>[`public/js/simulations/relativistic-black-hole.js`](file:///Users/holobetj/code/gemini/terra/public/js/simulations/relativistic-black-hole.js) | **Operational (60fps GPU)**. Zero-dependency WebGL2/GLSL raytracer. Null geodesic raymarching in Boyer-Lindquist coordinates for Kerr ($a \le 0.998$) & Schwarzschild black holes, Doppler beaming ($g^4$), gravitational redshift, accretion disk temperature models, and Einstein ring lensing. | `.venv/bin/python3 -m pytest tests/test_webgl_simulations.py` |
| **Elevated Dynamic Simulations** | [`public/js/simulations/pendulum.js`](file:///Users/holobetj/code/gemini/terra/public/js/simulations/pendulum.js)<br/>[`public/js/simulations/projectile-motion.js`](file:///Users/holobetj/code/gemini/terra/public/js/simulations/projectile-motion.js) | **Operational**. RK4 chaotic damped-driven pendulum with real-time Poincaré sections and period-doubling cascades; Newton's orbital cannon with circular, elliptical, and hyperbolic escape trajectories. | Browser at `/physics/simulations` |
| **Hero Stage Cosmic Arena** | [`public/js/cosmic_arena.js`](file:///Users/holobetj/code/gemini/terra/public/js/cosmic_arena.js)<br/>[`public/js/lab_cockpit.js`](file:///Users/holobetj/code/gemini/terra/public/js/lab_cockpit.js) | **Operational**. 60fps high-DPI canvas engine on `/physics/lab-tools`. 4 physical regimes, Web Audio harmonic frequency synthesis, color-coupled telemetry HUD, and interactive What-If micro-challenges. | Browser at `/physics/lab-tools` |
| **Cross-Encyclopedia Lab Hydration** | [`app/logic/LabToolsLauncher.php`](file:///Users/holobetj/code/gemini/terra/app/logic/LabToolsLauncher.php)<br/>[`app/views/physics/subtopic.php`](file:///Users/holobetj/code/gemini/terra/app/views/physics/subtopic.php) | **Operational**. 1,584/1,584 subtopics mapped to deep-linked interactive instruments, duality workbenches, and simulations with URL state pre-hydration and in-prose cockpit bridge cards. | `.venv/bin/python3 -m pytest tests/test_lab_tools_hydration.py` |
| **Multi-Step Derivations Engine** | `equation_explainer.php`<br/>[`tests/test_derivation_steps.py`](file:///Users/holobetj/code/gemini/terra/tests/test_derivation_steps.py) | **Operational (102 verified proofs sitewide)**. Collapsible derivation accordions with MathJax typesetting, sequential step schema, TeX brace balance, and universal Domain Parity ($\ge 8$ proofs across all 12 platform domains). | `.venv/bin/python3 -m pytest tests/test_derivation_steps.py` |
| **Lineage DAG & LHI** | `scripts/fixlineage`<br/>`formula_derivation_graph.json` | **Operational**. Lineage Health Index of 95.2/100, 0 isolated nodes, 44,558 derivation edges. | `scripts/fixlineage --summary` |
| **Dual-Layer Hash Synchronizer** | `app/config/formulas_hash_registry.json`<br/>`PhysicsService.php` | **Operational**. 256/256 formula shards synchronized with zero hash drift. | `scripts/assess --roadmap --no-tests` |

---

## 🛡️ 6. AI Cost Governance & Deterministic Token Safety Policy

All AI automation scripts, batch runners, and model integrations MUST adhere to the **Deterministic Token Governance Standard** detailed in `docs/cost_governance.md`:

1. **Pure Free Tier as Default**:
   * Interactive formula drafting and local developer tooling MUST default to `provider="free"` utilizing Google AI Studio keys (`GEMINI_FREE_API_KEY`).
   * This tier is hard-locked at **$0.00** at Google's infrastructure level and physically cannot incur credit card debt.
2. **Deterministic Pre-Flight Token Counting**:
   * Never guess input tokens. Sizing must be performed using `client.models.count_tokens()` prior to dispatching any generative calls.
3. **Hard-Capped Worst-Case Outputs**:
   * Every batch generation request must strictly bound `max_output_tokens` (e.g., 800) and `thinking_budget` (e.g., 512).
   * Unbounded or open-ended reasoning configurations in batch operations are strictly prohibited.
4. **Mandatory Non-Zero Budget Ceilings**:
   * If running paid cloud pipelines, `--max-cost-dollars` MUST require an explicit non-zero value (e.g., defaulting to $1.00, NEVER defaulting to 0.0 / unlimited).
   * Budget checks must occur **pre-dispatch** (before network requests are fired), preventing in-flight concurrent thread debt.
5. **Mandatory Canary Calibration**:
   * Any batch run exceeding 10 items must execute a 5-item canary sample, display empirical token and dollar statistics, and require explicit user authorization before proceeding.
