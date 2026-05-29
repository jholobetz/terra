# Physics Lab Co-Developer Guide — Universal CLAUDE.md

This document is the **Supreme Authority** for all architectural, stylistic, and procedural decisions in the Physics Lab project. All AI systems and human developers MUST adhere to these mandates to maintain the "Gold Standard" of a university-level digital encyclopedia.

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

### 🛡️ Guarded Sprint Orchestrator (Token-Saver & Zero-Interruption)
Consolidates the entire GQS cycle into a single transaction, automating syntax checking, compilation, and post-graduation audits with local git backups and self-healing rollbacks:
```bash
# Execute an autonomous, quality-guarded sprint for N stack targets
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>

# Run static syntax and OPS style checks without compiling (Dry-Run Mode)
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N> --dry-run
```

### 📦 Content Graduation Pipeline
* **Bootstrap Scaffolding**: Automatically creates topological neighbor transitions in standard or batch-safe modes:
  ```bash
  # Standard Mode (Default: draft.html & identities.json)
  .venv/bin/python3 scripts/maintenance/bootstrap_expansion.py <subtopic-slug>
  
  # Batch Mode (Collision-free: draft_<slug>.html & identities_<slug>.json)
  .venv/bin/python3 scripts/maintenance/bootstrap_expansion.py <subtopic-slug> --batch
  ```
* **Retrieve Concept Details**: Crawls shards to safely view JSON metadata without context bloat:
  ```bash
  .venv/bin/python3 scripts/maintenance/retrieve_concept.py <subtopic-slug>
  ```
* **Compile and Graduate Subtopic**: Compiles the draft, auto-links keywords, renders formulas to vector SVGs, updates shards, and commits to Git:
  ```bash
  .venv/bin/python3 scripts/maintenance/commit_node.py <subtopic-slug> draft.html
  ```
* **Batch Graduation (Token-Saver Mode)**: Silently compiles multiple drafts sequentially to prevent token bloat, resolves collision-free templates (`draft_<slug>.html`), syncs backlog registries, and prints a visual summary report:
  ```bash
  .venv/bin/python3 scripts/maintenance/batch_graduate.py <slug1> [slug2] [slug3] ...
  ```
* **Synchronize MariaDB Database (Manual)**: Synchronizes the physical JSON shards on disk with the active SQL database:
  ```bash
  php scripts/maintenance/sync_node.php <subtopic-slug>
  ```

### 🛡️ Validation & Test Suite
* **Central Tracking Authority (CTA) Sync**: Scans physical shards in real-time, self-heals desynchronizations in the expansion backlog, and displays the database status dashboard:
  ```bash
  .venv/bin/python3 scripts/maintenance/sync_backlog.py
  ```
* **Single-Node Integrity Audit**: Runs all schema, formula, and topological checks on a single slug:
  ```bash
  .venv/bin/python3 integrity_shield.py <subtopic-slug>
  ```
* **Full Sitewide Integrity Audit**: Scans all 14 content shards, 1,584 subtopics, 20,000+ links, and MathJax renderings:
  ```bash
  .venv/bin/python3 integrity_shield.py
  ```

---

## 🏛️ 2. The Organic Platinum Standard (OPS) Quality Gates

To graduate a subtopic from standard "legacy" to "platinum," it must pass these strict, non-negotiable guidelines enforced by the `integrity_shield.py` quality gate:

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
* **Link Preservation**: When refactoring, developers MUST first extract all existing internal links and ensure they are contextually re-integrated into the new draft.
* **Technical Density & Tone**: Strictly between **650 to 1,000 words** of dense, senior undergraduate to graduate-level academic prose.
* **MathJax Frequency**: High density of LaTeX (\( ... \) or \[ ... \]). Prose must calculate, not just describe.
* **Prose Structural Variety**: The number of paragraphs MUST vary organically between 4 and 6 (or more) depending on the complexity of the topic. The developer is strictly forbidden from standardizing on a fixed paragraph count across multiple subtopics in a sprint. The division of paragraphs must reflect the logical structure of the argument.
* **Organically Distributed Linkages**: Symmetrical subtopic links must be distributed organically across multiple paragraphs (e.g., paragraphs 1 to N-1). Do NOT bunch all neighbor bolds/links in a single paragraph (especially the first paragraph), as it creates visual clutter and disrupts reading flow. The GQS template builder automatically shards neighbor lists across paragraphs, and agents must strictly adhere to these distributed guidelines.

### B. Topological & Symmetrical Symmetries
* **Small-World Connectivity**: Every Platinum node must establish:
  * Minimum of **5 outgoing links** to neighboring subtopics.
  * Minimum of **2 incoming links** from other subtopics.
  * Minimum of **1 cross-hub bridge** connecting to a completely different Pillar Hub (e.g., Astrophysics linking to Thermodynamics).
* **The Identity Lock & Organic Curation**: A node is strictly forbidden from graduating if it contains fewer than **one (1) registered theoretical identity**. Curation of equations registered in the "Key Theoretical Identities" section must be organic (1 to N) and driven by the mathematical skeleton required for a university-level understanding. Every registered identity must meet at least one of these criteria:
  1. **Defining Law**: Establishes the primary physical behavior.
  2. **Limiting Case**: Demonstrates the connection to a classical or simpler regime.
  3. **Operational Metric**: Defines the primary observational or experimental relationship.
  * **Anti-Over-Standardization Mandate**: The developer or AI agent is strictly forbidden from using generic parent-hub default equations (such as repeatedly using the *Friedmann Equation* across all astrophysics nodes, or the *Schrödinger Time Evolution Operator* across all quantum nodes) simply to satisfy compilation requirements. Placeholder templates scaffolded by the GQS queue generator represent safety baselines only. The final graduated content must use highly specific, mathematically localized equations unique to the concept (e.g., using the *Kerr metric* boundary components for the ergosphere, the *Lane-Emden equations* for stellar structure, or the *Bell-CHSH inequality* for locality bounds) to prevent repetitive prose structure and maintain structural variety.
* **Pure Equation Values**: In `identities.json`, the `"equation"` value must be written as **pure, raw LaTeX strings without outer display delimiters** (i.e. no `\\[` or `$$` wrappers), as the compiler wraps them dynamically on render.
* **The Limiting Case Clause**: Every Platinum node must mathematically or conceptually demonstrate its Limiting Case (e.g., how General Relativistic scaling reduces to local flat Minkowski spacetime). The agent is strictly forbidden from using formulaic lead-ins like "The limiting case of...". Technical requirements must be woven into the narrative organically.

### C. Unified Notation Registry
Adhere to the project's established notation dialect across all equations:
* **Einstein Summation** for all tensor index contractions.
* **Over-dots** for all explicit time derivatives (e.g., $\dot{x}$, $\ddot{x}$).
* **Bold Vectors** for all classical spatial vector fields (e.g., $\mathbf{E}$, $\mathbf{B}$, $\mathbf{v}$).

### D. Structural Gateway Constraints
* **Topic Hubs (Categories)**: The 12 primary category entryways (e.g., `astrophysics`, `relativity`) serve as locked logical metadata structures and **DO NOT** conform to the OPS. They must **never** be altered.
* **Overview Articles**: Corresponding narrative overview articles are designated with the `-overview` suffix (e.g., `theoretical-physics-overview`). These carry the high-density academic overviews and conform strictly to the OPS. **All internal links routing to a primary discipline entryway must point to the narrative Overview Subtopic slug, not the locked category slug, to avoid category routing dead-ends.**

---

## 🏛️ 3. Core Platform Architecture

### A. Sharded Relational JSON Database
* The database is stored as unified storage shards inside `app/config/content/` (e.g. `astrophysics.json`, `relativity.json`).
* Concepts are mapped uniquely to exactly **one** physical storage shard.
* Shard slugs are indexed and resolved globally via `search_index.json`.

### B. Dynamic Hub Validation Engine (`orchestrator.py`)
Our context-affinity validation engine uses a dynamic state-of-the-art model:
1. **TF-IDF Dynamic Signatures**: On initialization, `PhysicsOrchestrator` scans all graduated Platinum subtopics, calculates normalized Term Frequency-Inverse Document Frequency (TF-IDF) vectors, and dynamically compiles `self.HUB_SIGNATURES` with the top 15 highest-weighted words for each hub.
2. **Full 12-Hub Mapping**: Affinity validations are computed dynamically across all **12 curriculum categories** matching our database categories exactly.
3. **Regex Suffix-Matching Bounds**: Scoring checks are executed using dynamic suffix-matching regex patterns with word boundary guards:
   ```python
   re.compile(r"\b" + re.escape(word) + r"(?:s|al|ally|ism|ist|ists|ing|ed|er|ers|es|tion|tions|tional|tionally|ity|ities|ic|ical|ically)?\b", re.IGNORECASE)
   ```
   This prevents grammatical extensions in the prose (e.g., "mechanical" or "classicality") from artificially lowering scores.
4. **Background-Vocabulary DF Ceiling**: A `DF_CEILING_PCT` class constant on `PhysicsOrchestrator` (default `0.60`) filters tokens appearing in more than 60% of platinum documents out of signature compilation. Eliminates corpus-background pollution — words like `energy`, `manifold`, and `vacuum` — that produced false-positive `Contextual Leakage` errors during graduation validation.

### C. The Background Watcher Protocol (Zero-Prompt Pipeline)
To maximize efficiency, the refactoring of subtopics can be executed via an autonomous background watcher protocol:
1. **Turn 1 (Silent Retrieval)**: Execute native `read_file` calls or retrieve concept details to gather legacy content. Perform the "verify and skip" check internally.
2. **Turn 2 (Silent Graduation)**: Draft new HTML into `draft.html` and identities into `identities.json`. Trigger the commit by writing a trigger payload to `scripts/maintenance/inbox/`.
3. **The Watcher Protocol**: `maintenance_watcher.py` autonomously executes `commit_node.py` (SVG rendering, auto-linking, MariaDB sync, and Git commits).

### D. The Token-Saver Batch Protocol
To maximize token economy and maintain perfect graduation consistency:
1. **Batch-Safe Scaffolding**: Passing the `--batch` or `-b` flag to `bootstrap_expansion.py` outputs slug-specific templates (`draft_<slug>.html` and `identities_<slug>.json`) to prevent placeholder overwrite collisions when preparing multiple nodes concurrently.
2. **Silent Log Redirection**: The batch orchestrator (`batch_graduate.py`) runs the compiler as an isolated subprocess, writing detailed link and validation logging to `logs/graduations/<slug>.log`. Only the success/warning summary is printed in the terminal, preventing 30k+ token log payloads from inflating conversational memory.
3. **Collision-Free Compilation**: Automatically resolves, compiles, and deletes slug-specific templates upon graduation, keeping the git status clean.
4. **Identity-Lock Merging**: The compiler (`commit_node.py`) is patched to dynamically combine newly registered premium identities with the subtopic's existing legacy formulas:
   ```python
   combined_fids = new_fids + [fid for fid in existing_fids if fid not in new_fids]
   ```
   This guarantees that high-density theoretical identities are never lost during graduation.
5. **Auto-Backlog Sync**: Successful graduates are automatically marked as `completed` inside `subfiles/expansion_backlog.json` at the system level.

### E. Central Tracking Authority (CTA)
To ensure absolute mathematical consistency across all source registries and progress tracking views:
1. **Real-time Disk Parsing**: The sync engine (`sync_backlog.py`) directly parses all 14 physical content JSON shards to extract the *exact ground truth* standard (`platinum` vs `legacy`) for all 1,584 subtopics, completely bypassing intermediate database steps.
2. **Self-Healing Backlog Registry**: It compares disk truth against `subfiles/expansion_backlog.json` and dynamically heals desynchronizations, setting status to `"completed"` for disk Platinum entries and `"pending"` for legacy ones.
3. **Database Status Dashboard**: Calculates total subtopics, platinum count, legacy count, and overall progress percentage, outputting a beautiful visual progress bar and category/shard breakdown table.
4. **Auto-Teardown Gate**: The tracking engine is integrated directly into the `batch_graduate.py` teardown, guaranteeing the central backlog registry self-heals after every successful batch graduation.

### F. The Graduation Queue Stack (GQS) Pipeline
To scale content ingestion while maintaining absolute OPS qualitative compliance, the project organizes work via a central queue stack pre-computed in `subfiles/graduation_queue_stack.json`:
1. **Pre-Computation (`generate_sprint_queue.py`)**: Automatically resolves target metrics (deterministic paragraph counts, neighbor linkages, cross-hub bridges, and registered math identities) for the top pending backlog items based on frequency.
2. **Unified CLI Controller (`gqs.py`)**: Consolidates backlog synchronization, templating, ingestion, and validation into a single command-line interface. Keeps `subfiles/active_expansion_sprint.json` in absolute lockstep.
3. **Compliance-Guaranteed Scaffolding (`gqs.py template <N>`)**: Scaffolds the exact schema-compliant JSON structures inside `subfiles/batch_payload.json` for active queue items, pre-annotated with deterministic paragraph boundaries and bold-link target guidelines.
4. **Subprocess Ingestion (`gqs.py ingest` -> `batch_ingest.py`)**: Sequentially compiles drafted prose against stack metadata, auto-renders MathJax equations to SVGs, updates relational shards, marks backlog items completed, pops them from the stack, and refills the stack.

### G. Guarded Sprint Orchestrator (`run_gqs_sprint.py`)
To prevent quality drift under zero-interruption autonomous runs, the GQS pipeline is wrapped in a strict three-stage transaction loop:
1. **Pre-Flight Git Savepoint**: Creates an automated git commit snapshot of the clean workspace before launching operations, recording a precise rollback hash.
2. **Pre-Compilation Static Syntax Guards**: Scans `subfiles/batch_payload.json` to verify that all drafted prose strictly adheres to the OPS Gates (word limits 650–1,000, 4–6 organic paragraphs, no forbidden starter definitions, no raw LaTeX leakages, no markdown lists or headers). *Aborts if style gates are breached.*
3. **In-Flight Compilation Arrest**: Intercepts `gqs.py ingest` exit codes. If any compilation or MathJax pre-rendering fails, the script triggers an automatic rollback.
4. **Post-Compilation Integrity Audits**: Invokes `integrity_shield.py` and `orchestrator.py` on the graduated shards. Any broken links, duplicated entries, or context affinity leaks will trigger an automatic rollback:
   ```bash
   git reset --hard <savepoint-hash>
   ```
5. **Git Success Commit**: Stages and commits all metadata and shard updates into a single transaction on success, restoring the repository to a clean state.

---

## 🗺️ 4. Project Roadmap & Topological Growth

Having finalized the 12 primary Topic Hubs, the curriculum expands into the **Second and Third Shells** of the knowledge graph:

### A. Recursive Graduation (The Deep Rigor Mandate)
* **Scope**: Any subtopic reachable via a direct link from a Platinum node must itself graduate to Platinum standard.
* **Priority**: Nodes linked from three or more independent Platinum nodes (e.g., `total-dynamics`, `scientific-realism`) are "Master Connectors" and must be prioritized for high-density refactoring (target 1,000 words).

### B. Topological Tightening & Organic Growth
To ensure maximum graph density, the project utilizes a continuous audit of physical entities:
* **Phase A: Auto-Linking (Structural Integrity)**: Any term wrapped in `<strong>` tags that exists in `global_slug_registry.json` but is not yet linked on its first mention within a node must be automatically upgraded to an anchor link (`<a href="..."><strong>...</strong></a>`).
* **Phase B: Backlog Population (Organic Expansion)**: Bold terms that appear across three or more independent nodes but lack a dedicated subtopic in the registry are identified as "Expansion Candidates." High-frequency candidates (20+ nodes, e.g., `Block Universe`, `Big Bang`) are prioritized for curriculum expansion.
* **Progress Tracking**: Progress is tracked in `subfiles/hub_tracker.json`. Current Hub status: 100% Graduated.

### C. Project Goal: 100% OPS Token-Aware Graduation Roadmap
To graduate the remaining 939 pending legacy nodes to the Organic Platinum Standard, the project adheres to a token-aware and rate-limit conscious goal:
* **Context Accumulation & Compaction Safe Boundary**: Sprints are batched in groups of 3 nodes (~6,500 tokens/sprint). Context compaction and resettlement is scheduled every 15 sprints (~45 nodes) with a 5-minute overhead window to keep conversational intelligence sharp.
* **API Rate-Limit Cooling**: Incorporates a 10-second cooling latency per sprint to completely bypass RPM/TPM transient limitations.
* **Refined Continuous Execution Time**: **~11.32 hours** of active, uninterrupted pipeline processing.
* **Refined Collaborative Calendar Timeline**: **~10.5 days** of active pairing at standard daily rhythms, ensuring mathematically localized identities are curators-driven and qualitatively rich.

---

## 🏆 5. Session Progress & Tracking

Session progress is managed entirely dynamically by the system. AI co-developers and humans should **never** manually log sprint milestones in this file. Instead, view the live progress dashboard, shard completion percentages, and active target queue at any time by running:

```bash
.venv/bin/python3 gqs.py status
```
