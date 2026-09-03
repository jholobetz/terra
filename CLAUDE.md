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
2. **Execute Repair Engine**: Run the repair tool instantly using terminal commands:
   ```bash
   scripts/fixlatex "<URL|ID|LaTeX>" ["<hint or reference text>"]
   ```
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

### A. The Two Distinct Data Stores
The project maintains two separate storage layers:
1. **Subtopic Prose Shards (`app/config/content/*.json`)**: 14 thematic JSON files (e.g. `astrophysics.json`, `quantum-physics.json`) containing the narrative encyclopedia articles, word metrics, and neighbor links.
2. **Formula Manifold Shards (`app/config/content/formulas/[00-ff]/shard_[00-ff].json`)**: 256 deterministic hex-hashed shards storing all **14,613 formulas**, mathematical definitions, interpretations, limiting cases, derivation parent IDs, and semantic variable dictionaries.

### B. Mathematical Derivation Lineage Graph (DAG)
* Lineage is tracked as an acyclic graph in `app/config/formula_derivation_graph.json` (and `.gz`).
* Formulas connect hierarchically from foundational axioms down to phenomenological identities.
* The **Lineage Health Index (LHI)** continuously benchmarks derivation density on a 0–100 scale (currently at **95.0 / 100**).

### C. Equation Explainer & Dissection Suite
* Located at `/physics/equation-explainer`.
* Deconstructs raw LaTeX into base variables and parameter modifiers.
* Uses dynamic MathJax 3.x vector rendering for interactive exploration and SVG sprites for static encyclopedia hubs.

---

## 🛡️ 5. AI Cost Governance & Deterministic Token Safety Policy

All AI automation scripts, batch runners, and model integrations MUST adhere to the **Deterministic Token Governance Standard** detailed in `docs/token_estimation_and_cost_governance.md`:

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
