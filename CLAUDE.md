# Physics Lab Co-Developer Guide — Universal CLAUDE.md

This document is the **Supreme Authority** for all architectural, stylistic, and procedural decisions in the Physics Lab project. All AI systems and human developers MUST adhere to these mandates to maintain the "Organic Platinum Standard" (OPS) of a university-level digital encyclopedia.

---

## 🚀 1. Quick Reference Commands

All Python operations must be executed using the project's local virtual environment (`.venv/`). The system interpreter should never be used for maintenance tasks.

### 🎛️ Unified Session Controller (Recommended)
Our unified developer CLI manages the entire GQS pipeline lifecycle, offering automatic backlog synchronization, status dashboards, structure-compliant templating, and compilation:
```bash
# Check current database metrics, active drafts, and next priority targets.
# Surfaces three sections in one screen: the live CTA disk dashboard, the
# Quality Breakdown (flagged vs organic platinum counts, qualitative
# violations, and integrity summary read from system_health.json), and the
# top GQS queue targets. No mental reconciliation across files required.
.venv/bin/python3 gqs.py status

# Automatically scaffold the next N GQS targets into subfiles/batch_payload.json
.venv/bin/python3 gqs.py template <N>

# Graduate and compile all drafted targets in subfiles/batch_payload.json
.venv/bin/python3 gqs.py ingest

# Run a structural and formula validation audit (site-wide or single slug)
.venv/bin/python3 gqs.py audit [slug]

# Replenish the pre-resolved GQS stack depth and sync the active sprint
.venv/bin/python3 gqs.py refill [N]

# Automatically scan, register, AI-seed, render, and sync missing equations
# rate_tier: "free" (default, uses AI Studio key with 5s delay) or "vertex" (uses GCP Vertex AI in parallel)
.venv/bin/python3 gqs.py formula-auto-seed <limit> [rate_tier]
```

### 🛡️ Guarded Sprint Orchestrator (Token-Saver & Zero-Interruption)
Consolidates the entire GQS cycle into a single transaction, automating syntax checking, compilation, and post-graduation audits with local git backups and self-healing rollbacks:
```bash
# Execute an autonomous, quality-guarded sprint for N stack targets
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>

# Run static syntax and OPS style checks without compiling (Dry-Run Mode)
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N> --dry-run
```

### 📦 Content Operations and Utilities
* **Retrieve Concept Details**: Crawls shards to safely view JSON metadata without context bloat:
  ```bash
  .venv/bin/python3 scripts/maintenance/retrieve_concept.py <subtopic-slug>
  ```
* **Synchronize MariaDB Database (Manual)**: Synchronizes the physical JSON shards on disk with the active SQL database:
  ```bash
  php scripts/maintenance/sync_node.php <subtopic-slug>
  ```

### 🔄 Substandard Subtopic Upgrade Pipeline
For existing subtopics that are already flagged as platinum on disk but fail depth (< 650 words) or density (< 60) quality gates, use this high-efficiency upgrade pipeline:
* **Step 1: Scaffold & Recover Raw LaTeX**: Identify worst-offending nodes, pull their uncompiled history from Git, and populate `subfiles/batch_payload.json`:
  ```bash
  .venv/bin/python3 scripts/maintenance/scaffold_upgrade.py --count <N> --recover-latex
  ```
* **Step 2: Expand Prose & Weave Math**: Expand the content inside `subfiles/batch_payload.json` to 800+ words (providing a word count cushion since LaTeX blocks are stripped during compliance checks) and insert mathematically localized equations.
* **Step 3: Auto-Format Neighbors & Verify Compliance**: Auto-insert neighbor link tags and run static syntax/style guards:
  ```bash
  .venv/bin/python3 scripts/maintenance/check_draft_compliance.py --autofix
  ```
* **Step 4: Compile & Graduate**: Run the transaction-backed GQS sprint coordinator to compile, build SVGs, verify integrity, and commit to Git:
  ```bash
  .venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>
  ```

### 🛡️ Validation & Test Suite
* **Automated Pytest Suite**: Runs the full regression net (~1 second locally, ~30 seconds on CI). Covers OPS prose-gate validation, formula-id merge invariants, the integrity shield against fixture shards, CTA backlog reconciliation (heal + dedupe), the system_health platinum classifier, and the `gqs.py status` quality renderer. Also wired to CI via `.github/workflows/tests.yml` on every push and pull request to `master`:
  ```bash
  .venv/bin/python3 -m pytest tests/
  ```
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
* **MathJax SVG Sprite Sheet Optimizer**: Optimizes, extracts, and spritifies all MathJax SVGs in content shards and persistent caches:
  ```bash
  .venv/bin/python3 scripts/maintenance/spritify_assets.py
  ```
* **Semantic Hallucination & Drift Shield**: Audits typeset LaTeX symbols against physical prose explanation anchors, checks for leaked display delimiters inside paragraphs, validates balanced delimiters, and prevents consecutive glossary-style listing patterns:
  ```bash
  .venv/bin/python3 scripts/maintenance/hallucination_shield.py [--slug <slug>]
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
* **The "Anti-Formulaic Integration" Rule**: Formulaic introductory phrases for mathematical equations (e.g., *"This is defined by the following equation..."*, *"The formula for this is..."*, or *"The Wigner function can be written as..."*) are strictly forbidden. Mathematical equations must be woven organically as grammatical continuations of physical sentences (e.g., *"...which yields the Majorana mass term, \(\mathcal{L} = ...\), that breaks..."*).
* **Positional Variation for Equations**: Primary mathematical identities are dynamically allocated across the entire paragraph range (from Paragraph 1 to the final Paragraph $N$). Equations must reside where they logically belong in the physical narrative:
  * *Paragraph 1 Placement (Axiomatic Approach)*: Serves as the ultimate "In Media Res" start. Perfect for fundamental, self-evident equations (e.g. the Dirac or Schrödinger equations) that require no introductory hand-waving and immediately govern the opening sentences.
  * *Middle Paragraph Placement (Derivational Approach)*: Serves as the transitional bridge in an active physical derivation or mechanical argument.
  * *Paragraph $N$ Placement (Synthesizing/Limiting Approach)*: Acts as the mathematical crown of the narrative, serving as the observational metric or the mathematical engine of the classical reduction.
* **Immediate Physical Coupling (The Anti-Glossary Rule)**: No mathematical formula can sit isolated, and we strictly forbid the "where..." glossary pattern. Do not define terms in a glossary-style list immediately following an equation (e.g., *"...written as [Eq], where B is..., \mu_0 is..., and J is..."*). Instead, actively weave all symbols, coefficients, and operators into a continuous physical narrative that explains their dynamic interaction, roles, and physical mechanisms within the system.
* **Rigorous Pure-Prose (Zero-Formula) Guidelines**: Conceptual, philosophical, or interpretative nodes that do not utilize equations must establish alternative standards of academic rigor:
  1. Maintain university-level density using high-precision physical/philosophical terminology (e.g., *counterfactual definiteness*, *ontological commitment*, *superselection sectors*).
  2. Implement formal logical syllogisms or thought experiments as structural surrogates for mathematical derivations.
  3. Increase topological bridge connectivity to contextualize and map the relationships between neighboring mathematical nodes.
* **Link Preservation**: When refactoring, developers MUST first extract all existing internal links and ensure they are contextually re-integrated into the new draft.
* **Technical Density & Tone**: Strictly between **650 to 1,000 words** of dense, senior undergraduate to graduate-level academic prose. **For primary Category Hub Overview articles (designated with the `-overview` suffix), this baseline is elevated to a strict target range of 800 to 1,000 words to ensure adequate coverage of the core curriculum and topological link capacity.**
* **MathJax Frequency & Rich Variable Density**: Weave precise, high-density inline mathematical symbols, variables, tensors, and operators (e.g., \( \Phi \), \( p^\mu \), \( \langle \phi | \psi \rangle \)) on their first mention and consistently throughout the text. These serve as visual and cognitive landmarks that ground the technical physics, eliminate the visual "wall of text" feel, and reflect true graduate-level textbook density.
  * **NON-NEGOTIABLE TARGET**: Every single paragraph of every graduated subtopic node—including purely conceptual, interpretive, or philosophical nodes—MUST contain at least 2 to 4 distinct inline MathJax expressions (e.g. \( g_{\mu\nu} \), \( |\Psi^+\rangle \), \( \hat{H} \)) to maintain visual texture and eliminate the plain-text 'wall of text' aesthetic. Pure-prose passages with zero typeset math are strictly prohibited.
  * **Explicit Variable Coupling (Strict Requirement)**: Never reference a physics field, parameter, coordinate, or concept purely by name if it has a standard symbol representation; couple it immediately to its mathematical symbol (e.g., writing "metric tensor \( g_{\mu\nu} \)" instead of just "the metric tensor", "Hilbert space \( \mathcal{H} \)" instead of "Hilbert space", or "action functional \( S[\phi] \)" instead of "the action"). All subsequent references should be symbolically anchored.
  * **Weft of Intermediate Math & Compatibility Relations**: Weave short, precise, inline mathematical statements, commutation relations (e.g., \( [x_i, p_j] = i\hbar\delta_{ij} \)), metric compatibility relations (e.g., \( \nabla_\rho g_{\mu\nu} = 0 \)), or connection formulas (e.g., \( \Gamma^\lambda_{\mu\nu} = \Gamma^\lambda_{\nu\mu} \)) directly into the sentences. Every paragraph should have multiple LaTeX equations, tensors, or operators embedded within physical sentences.
  * **Plain English Word Count Cushion (Crucial Static Guardrail Check)**: Because the static style checker strips all LaTeX blocks (e.g. \( ... \) and \[ ... \]) before calculating word counts, writing highly mathematical nodes significantly inflates the "stripped" word count drop. The writer **MUST** write a generous plain-English word cushion (e.g. drafting 800-950 words total to easily clear the 650-word minimum once LaTeX blocks are stripped).
  * **Anti-Drift & Anti-Pattern Guard**: While the density of variables is high, the prose MUST remain completely organic. The developer is strictly forbidden from letting structural patterns drift or using repetitive sentence structures across different nodes (e.g., matching the same transition formulas, introductory phrases, or paragraph patterns). Each subtopic's narrative must arise organically from its unique physics.
* **Prose Structural Variety**: The number of paragraphs MUST vary organically between 4 and 6 (or more) depending on the complexity of the topic. The developer is strictly forbidden from standardizing on a fixed paragraph count across multiple subtopics in a sprint. The division of paragraphs must reflect the logical structure of the argument.
* **Organically Distributed Linkages**: Symmetrical subtopic links must be distributed organically across multiple paragraphs (e.g., paragraphs 1 to N-1). Do NOT bunch all neighbor bolds/links in a single paragraph (especially the first paragraph), as it creates visual clutter and disrupts reading flow. The GQS template builder automatically shards neighbor lists across paragraphs, and agents must strictly adhere to these distributed guidelines.

### B. Topological & Symmetrical Symmetries
* **Small-World Connectivity**: Every Platinum node must establish:
  * Minimum of **5 outgoing links** to neighboring subtopics.
  * Minimum of **2 incoming links** from other subtopics.
  * Minimum of **1 cross-hub bridge** connecting to a completely different Pillar Hub (e.g., Astrophysics linking to Thermodynamics).
* **Organic Formula Integration**: Mathematical equations must be integrated in a purely organic, topic-driven manner. While the GQS pipeline systematically registers mathematically localized "Identity Locks" (Formula IDs) unique to each topic to prevent generic placeholder pollution, their incorporation in the prose must flow naturally according to the logical requirements of the narrative. Conceptual, interpretive, or philosophical subtopics (e.g., *scientific-realism*, *anthropic-principle*, *epistemic-boundary*) are graduated as high-density qualitative academic prose with zero registered formulas. Curation of equations must be driven entirely by the logical and narrative requirements of the topic to maintain an organic flow, satisfying the following criteria when formulas are included:
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
* **Overview Articles**: Corresponding narrative overview articles are designated with the `-overview` suffix (e.g., `theoretical-physics-overview`). These carry the high-density academic overviews and conform strictly to the OPS. **They must adhere to a strict target range of 800 to 1,000 words (elevated from the standard 650-word minimum) and must contain at least 5 outbound links to map the subtopics of their respective hub.** All internal links routing to a primary discipline entryway must point to the narrative Overview Subtopic slug, not the locked category slug, to avoid category routing dead-ends.

### E. Mandatory GQS & Scaffold Upgrade Workflows
* **Strict Ban on Direct Shard Editing**: AI agents and developers MUST NOT edit the prose, math formulas, or data structures directly within the sharded database files (`app/config/content/*.json`). Direct manual edits bypass LaTeX-to-SVG compilation, auto-linking, and validation tests, resulting in un-rendered raw LaTeX math syntax, broken pages, and desynchronized MathJax SVG cache/sprite mappings.
* **Upgrading Existing Platinum Nodes**:
  - Always run the upgrade utility first with the target slug and `--recover-latex` flag:
    ```bash
    .venv/bin/python3 scripts/maintenance/scaffold_upgrade.py --slug <slug> --recover-latex
    ```
  - This extracts the raw LaTeX equations (`\( ... \)` and `\[ ... \]`) from Git history to prevent loss of mathematical formulas or attempts to edit unreadable pre-rendered `<path>` elements, outputting a clean draft structure into `subfiles/batch_payload.json`.
* **Graduating Legacy Backlog Nodes**:
  - Scaffold the next stack target into the batch payload using the unified controller CLI:
    ```bash
    .venv/bin/python3 gqs.py template <N>
    ```
  - Edit and expand the target content inside `subfiles/batch_payload.json` ensuring full compliance with the OPS Gates (§2.A).
* **Ingestion and Validation**:
  - Ingest the drafted changes using either the unified controller:
    ```bash
    .venv/bin/python3 gqs.py ingest
    ```
  - Or the transaction-guarded sprint coordinator:
    ```bash
    .venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>
    ```

### F. Pedagogical Symbol Deconstruction (Forced Pedagogy)
To ensure the Equation Explainer acts as a fulsome information conduit, equations must be completely deconstructed to separate physical dimensions from their situational parameters:
* **Separation of Concerns**: In the component breakdown UI, **Base Variables & Constants** (such as Force \( \mathbf{F} \) or Velocity \( \mathbf{v} \)) must be rendered separately from **Subscripts, Superscripts & Modifiers** (such as \( \text{ext} \), \( \text{abs} \), or \( \dagger \)).
* **Standard Modifiers Glossary**: Subscripts and superscripts representing standard physical states, operations, or constraints (e.g. \( \circ \) for standard state, \( \dagger \) for adjoints, and \( \text{net} \), \( \text{eff} \), \( \text{ext} \) for boundaries) must be looked up in a centralized glossary and explained.
* **No Discarding Rule**: Subscripts and superscripts are never discarded during heuristic tokenization. If they are not found in the standard glossary, they must be parsed as custom modifiers to prompt explanation.

---

## 🏛️ 3. Core Platform Architecture

### A. Sharded Relational JSON Database
* The database is stored as unified storage shards inside `app/config/content/` (e.g. `astrophysics.json`, `relativity.json`). There are 14 physical shards on disk, corresponding to the 12 logical curriculum category hubs plus two additional utility shards: `legacy-orphans.json` (which stores unassigned legacy topics) and `notation.json`.
* Concepts are mapped uniquely to exactly **one** physical storage shard.
* Shard slugs are indexed and resolved globally via `search_index.json`.

### B. Dynamic Hub Validation Engine (`orchestrator.py`)
Our context-affinity validation engine uses a dynamic state-of-the-art model:
1. **TF-IDF Dynamic Signatures**: On initialization, `PhysicsOrchestrator` scans all graduated Platinum subtopics, calculates normalized Term Frequency-Inverse Document Frequency (TF-IDF) vectors, and dynamically compiles `self.HUB_SIGNATURES` with the top 15 highest-weighted words for each hub. To eliminate the linear $\mathcal{O}(N)$ processing latency of full corpus scanning, a persistent TF-IDF signature cache is maintained at `subfiles/hub_signatures.json`, validated by a stable MD5 hash of all active Platinum subtopics (slugs, titles, and contents). This reduces orchestrator startup from ~1.2s to <5ms.
2. **Full 12-Hub Mapping**: Affinity validations are computed dynamically across all **12 curriculum categories** matching our database categories exactly.
3. **Regex Suffix-Matching Bounds**: Scoring checks are executed using dynamic suffix-matching regex patterns with word boundary guards:
   ```python
   re.compile(r"\b" + re.escape(word) + r"(?:s|al|ally|ism|ist|ists|ing|ed|er|ers|es|tion|tions|tional|tionally|ity|ities|ic|ical|ically)?\b", re.IGNORECASE)
   ```
   This prevents grammatical extensions in the prose (e.g., "mechanical" or "classicality") from artificially lowering scores.
4. **Background-Vocabulary DF Ceiling**: A `DF_CEILING_PCT` class constant on `PhysicsOrchestrator` (default `0.60`) filters tokens appearing in more than 60% of platinum documents out of signature compilation. Eliminates corpus-background pollution — words like `energy`, `manifold`, and `vacuum` — that produced false-positive `Contextual Leakage` errors during graduation validation.

## C. The Background Watcher Protocol (Zero-Prompt Pipeline)
For single-node ad-hoc expansions, refactoring can be executed via an autonomous background watcher protocol:
1. **Turn 1 (Silent Retrieval)**: Execute native `read_file` calls or retrieve concept details to gather legacy content. Perform the "verify and skip" check internally.
2. **Turn 2 (Silent Graduation)**: Draft new HTML and identities to temporary file locations. Trigger the commit by writing a trigger payload (specifying the paths to the draft files) to `scripts/maintenance/inbox/`.
3. **The Watcher Protocol**: `maintenance_watcher.py` autonomously executes `commit_node.py` (SVG rendering, auto-linking, MariaDB sync, and Git commits).

## D. The Token-Saver Batch Protocol
For upgrading substandard nodes and processing GQS queue items in groups (the primary pipeline), the batch protocol is used:
1. **Batch-Safe Scaffolding**: `gqs.py template <N>` scaffolds the next queue targets or substandard nodes directly into `subfiles/batch_payload.json`, preventing manual template collisions.
2. **Silent Log Redirection**: The batch ingester (`batch_ingest.py`) runs the compiler as an isolated subprocess, writing detailed link and validation logging to `logs/graduations/<slug>.log`. Only the success/warning summary is printed in the terminal, preventing 30k+ token log payloads from inflating conversational memory.
3. **Collision-Free Compilation**: Automatically writes slug-specific temporary drafts (`draft_<slug>.html` and `identities_<slug>.json`) during compilation and deletes them upon completion, keeping the git status clean.
4. **Identity-Lock Merging**: The compiler (`commit_node.py`) is patched to dynamically combine newly registered premium identities with the subtopic's existing legacy formulas:
   ```python
   combined_fids = new_fids + [fid for fid in existing_fids if fid not in new_fids]
   ```
   This guarantees that high-density theoretical identities are never lost during graduation.
5. **Auto-Backlog Sync**: Successful graduates are automatically marked as `completed` inside `subfiles/expansion_backlog.json` at the system level.

## E. Central Tracking Authority (CTA)
To ensure absolute mathematical consistency across all source registries and progress tracking views:
1. **Real-time Disk Parsing**: The sync engine (`sync_backlog.py`) directly parses all 14 physical content JSON shards to extract the *exact ground truth* standard (`platinum` vs `legacy`) for all 1,584 subtopics, completely bypassing intermediate database steps.
2. **Self-Healing Backlog Registry**: Compares disk truth against `subfiles/expansion_backlog.json` and dynamically heals desynchronizations, setting status to `"completed"` for disk Platinum entries and `"pending"` for legacy ones.
3. **Duplicate-Slug Dedupe (Self-Healing)**: `self_heal_backlog` also collapses entries sharing a `suggested_slug` on every sync via the pure `dedupe_backlog` function. Punctuation variants that resolve to the same slug (e.g., `"Conservation"` and `"Conservation:"` → `conservation`) are merged, with status promoted to `completed` when any duplicate had it. First-appearance order is preserved; entries without `suggested_slug` are kept verbatim. The backlog file is rewritten only when the heal pass or the dedupe pass produced a change.
4. **Database Status Dashboard**: Calculates total subtopics, platinum count, legacy count, and overall progress percentage, outputting a beautiful visual progress bar and category/shard breakdown table.
5. **Auto-Teardown Gate**: The tracking engine is integrated directly into the `batch_ingest.py` post-ingestion flow, guaranteeing the central backlog registry self-heals after every successful batch ingestion.
6. **Two Platinum Definitions (Critical Distinction)**: The project exposes two distinct platinum counts that future contributors MUST keep separate. Conflating them was the source of the dashboard-drift incident resolved in this codebase:
    * **Flagged Platinum** (`flagged_platinum_count` in `system_health.json`): the raw disk count of subtopics with `standard == "platinum"`. This is the authoritative live count and matches the CTA dashboard exactly.
    * **Organic Platinum** (`organic_platinum_count`): the strict subset that additionally passes the §2.A lead-rule and artifact-violation gates. Always `≤ flagged_platinum_count`.
    * **Flag Violations** (`flag_violations`): the difference between the two — slugs flagged as platinum but failing the qualitative checks. By construction, `flagged_platinum_count == organic_platinum_count + flag_violations`.
    * **Substandard Nodes**: Flagged/Organic nodes that fail quantitative gates (depth < 650 words or density < 60). These do not count as qualitative "Flag Violations" but represent the target queue for substandard upgrade sprints.
    * `gqs.py status` surfaces both counts side-by-side with the gap explained, so users never have to reconcile across files in their head.

### F. The Graduation Queue Stack (GQS) Pipeline
To scale content ingestion while maintaining absolute OPS qualitative compliance, the project organizes work via a central queue stack pre-computed in `subfiles/graduation_queue_stack.json`:
1. **Pre-Computation (`generate_sprint_queue.py`)**: Automatically resolves target metrics (deterministic paragraph counts, neighbor linkages, cross-hub bridges, and registered math identities) for the top pending backlog items.
2. **Backlog Math Registry (`subfiles/backlog_math_registry.json`)**: Serves as the single source of truth for pre-assigned, mathematically localized identities. The queue generator queries this registry first. If a subtopic is registered, it loads the localized template; if missing, it scaffolds a `"PLACEHOLDER"` template.
3. **Decoupled Compiler Ingestion**: The batch ingester (`batch_ingest.py`) is decoupled to prioritize the customized mathematical `"identities"` fields directly from `subfiles/batch_payload.json` rather than dragging the fallback values from the stack file.
4. **Unified CLI Controller (`gqs.py`)**: Consolidates backlog synchronization, templating, ingestion, and validation into a single command-line interface. Keeps `subfiles/active_expansion_sprint.json` in absolute lockstep.
5. **Compliance-Guaranteed Scaffolding (`gqs.py template <N>`)**: Scaffolds the exact schema-compliant JSON structures inside `subfiles/batch_payload.json` for active queue items, pre-annotated with deterministic paragraph boundaries, bold-link target guidelines, and structured math `"identities"`.
6. **Subprocess Ingestion (`gqs.py ingest` -> `batch_ingest.py`)**: Sequentially compiles drafted prose against payload and stack metadata, auto-renders MathJax equations to SVGs, updates relational shards, marks backlog items completed, pops them from the stack, and refills the stack.

### G. Guarded Sprint Orchestrator (`run_gqs_sprint.py`)
To prevent quality drift under zero-interruption autonomous runs, the GQS pipeline is wrapped in a strict three-stage transaction loop that guarantees a clean git history tree and zero lost changes:
1. **Pre-Flight Git Savepoint**: Creates an automated, staged git commit snapshot (`chore: automated pre-flight GQS savepoint...`) representing the workspace draft state before launching operations, recording a precise rollback hash.
2. **Pre-Compilation Static Syntax Guards**: Scans `subfiles/batch_payload.json` to verify that all drafted prose strictly adheres to the OPS Gates (word limits 650–1,000, 4–6 organic paragraphs, no forbidden starter definitions, no raw LaTeX leakages, no markdown lists or headers). *Also enforces the Placeholder Fail-Safe, aborting the transaction immediately if the payload contains scaffolded "PLACEHOLDER" text in any math block or title.*

3. **In-Flight Compilation Arrest**: Intercepts `gqs.py ingest` exit codes. If any compilation or MathJax pre-rendering fails, the script triggers an automatic rollback.
4. **Post-Compilation Integrity Audits**: Invokes `integrity_shield.py` and `orchestrator.py` on the graduated shards. Any broken links, duplicated entries, or context affinity leaks will trigger an automatic rollback.
5. **Self-Healing Transactional Rollback**: On any quality gate or compilation failure:
   ```bash
   git reset --hard <savepoint-hash>
   git reset HEAD~1
   ```
   This completely removes the pre-flight commit from the git history and preserves the user's uncommitted draft files in the working directory for manual correction, leaving zero trace of spurious commits.
6. **Git Success Commit Consolidation**: Stages and commits all metadata and shard updates into a single transaction on success, utilizing `git commit --amend` to combine the pre-flight savepoint and the compiled changes into one clean, final graduate commit. This ensures a clean git log without intermediate "savepoint" clutter.

### H. SVG Math Vector Sprite Sheets (`math_sprites.svg`)
To minimize database JSON shard sizes, reduce git repository bloat, and improve browser rendering latency, the compilation pipeline implements dynamic vector spritification for MathJax SVGs:
1. **Glyph Extraction & Sprite Compilation**: During `convert_to_svg`, any generated MathJax SVG is parsed, and all raw `<path d="..." />` elements are extracted. Unique path definitions are consolidated into a single, global sprite sheet: `app/config/content/math_sprites.svg`.
2. **References via Use Elements**: Inline mathematical SVG markup is rewritten to replace heavy path descriptors with lightweight `<use href="#math-path-<hash>"/>` tags. This reduces the size of each inline equation by ~90% (from ~5KB to ~300 bytes).
3. **Persistent Cache & Shards Optimization**: Re-running the optimizer (`spritify_assets.py`) shrunked the persistent cache `global_svg_cache.json` from **50.37 MB to 14.90 MB (70.4% reduction)** and all 14 sharded JSON files by **10% to 18%**.
4. **Layout Integration**: The sprite sheet is dynamically embedded directly inside `app/views/physics/layout.php` immediately after the `<body>` tag, enabling instantaneous site-wide mathematical rendering.

### I. Aho-Corasick Auto-linking Engine
To safeguard compilation performance and prevent the risk of **Catastrophic Backtracking** during paragraph keyword scanning, the auto-linker utilizes a native string matching engine:
1. **State Machine Compilation**: A native, lightweight Aho-Corasick state machine with failure transitions is built dynamically in `_refresh_sorted_titles` from the active subtopic registry.
2. **Linear-Time Multi-Pattern Matching**: Plain text auto-linking scans text and resolves matches in a single, linear pass ($\mathcal{O}(L + M)$ where $L$ is the text length), completely bypassing the exponential time complexity of regular expression backtracking.
3. **Preserved Symmetries & Guards**: Parity is maintained with all contextual boundary guards (`\b`), lookbehinds (`(?<![=">])`), lookaheads (`(?![<])`), and semantic TECHNICAL ANCHORS context checks.

### J. Automated Pytest Suite (`tests/`)
The `tests/` directory is the regression net for every architectural invariant described above. Six in-process and black-box test files cover the highest-leverage seams:
1. **`test_ops_gates.py`**: drives `run_gqs_sprint.py --dry-run` against a tempdir-based payload fixture and asserts each OPS gate from §2.A fires correctly (in-media-res lead, paragraph structure, word band, markdown residue, math-display delimiters, list/header bans).
2. **`test_identity_lock.py`**: pins the `merge_formula_ids` helper extracted from `commit_node.py` — the load-bearing one-line invariant that prevents legacy formula loss during graduation when new identities are registered.
3. **`test_integrity_shield.py`**: exercises `IntegrityShield` against a synthetic fixture `content_dir`, covering broken links, broken formula references, MathJax-error markup, duplicate slugs across shards, density warnings, raw-LaTeX SSR violations, unrendered math displays, and entity auto-link warnings.
4. **`test_sync_backlog.py`**: covers both `scan_disk_standards` (disk-truth extraction) and `self_heal_backlog` (heal + dedupe). Includes a critical anti-regression test that the function keys off `suggested_slug`, not `slug`.
5. **`test_system_health.py`**: pins `score_subtopic`, the per-node classifier extracted from `generate_system_health.py` that drives the `flagged_platinum_count` and `organic_platinum_count` counters described in §3.E.
6. **`test_gqs_status.py`**: covers `print_quality_breakdown` (graceful no-op on missing/malformed `system_health.json`, correct rendering of the dual platinum classification).

**Operating discipline**: keep the suite green. Every refactor in this document — especially the surgical extractions (`merge_formula_ids`, `dedupe_backlog`, `score_subtopic`, `print_quality_breakdown`) — was paired with tests that lock down byte-identical behavior. The suite runs in ~1 second locally and on every push and pull request to `master` via `.github/workflows/tests.yml`.

### K. Interactive Drill-Down & Modifier Parsing Architecture
The client-side Equation Explainer frontend implements an advanced parser and navigation stack to dissect LaTeX formulas:
1. **Interactive Sub-Symbol Drill-Down**: Clicking a variable triggers "Drill-Down Mode", updating the editor input and retypesetting individual math blocks. Frontend navigation state is tracked via browser history (`popstate`) so that clicking back cleanly pops the stack and restores the parent equation.
2. **Subscripts & Superscripts Modifier Parser**: Parses subscripts (`_`) and superscripts (`^`) from the raw LaTeX using regex patterns, classifying them against `modifierGlossary` or treating them as custom constraints to prevent loss of parameter descriptions.
3. **Exposition Panel Organization**: Establishes a clean visual partition: the left column acts as the "Dissection Workshop" (LaTeX input, MathJax preview, Variables/Modifiers breakdown), and the right column acts as the "Exposition Suite" (Narratives, physical scenarios, and topological bridges linking the equation out to the rest of the encyclopedia).
4. **Collision-Free Clean Index Matching**: Sorts variables and modifiers left-to-right matching their mathematical visual flow. Replaces structural commands (e.g. `\mathbf`, `\frac`) and descriptive subscript text with blank spaces of the exact same length to generate a parallel string layout where `indexOf` matches are guaranteed to be collision-free.

### L. GitHub Actions CI Environment
* **Workflow Runners**: CI builds run under Node.js 24 and Python 3.14 on macOS and Linux environments.
* **Deprecation Safety**: Workflows defined in `.github/workflows/tests.yml` must target modern actions version packages (`actions/checkout@v6` and `actions/setup-python@v6`) to ensure warnings-free runs.

### M. API Concurrency & Rate-Limiting Policy
Whenever implementing or executing scripting components that invoke external LLM APIs (especially Vertex AI / Google AI Studio paid tiers), developers must respect the default platform rate limits (e.g., 200,000 TPM / 300 RPM ceilings) to prevent `ResourceExhausted` blocks:
1. **Concurrency Cap**: Thread pool limits must not exceed **3 concurrent workers** under heavy loads.
2. **Polite Staggering**: Implement a mandatory staggered cooldown delay (minimum **1.0 seconds**) between requests to prevent concurrent socket bursts and smooth out the rate distribution.

---

## 🏆 4. Session Progress & Tracking

Session progress is managed entirely dynamically by the system. AI co-developers and humans should **never** manually log sprint milestones in this file. Instead, view the live progress dashboard, shard completion percentages, and active target queue at any time by running:

```bash
.venv/bin/python3 gqs.py status
```
