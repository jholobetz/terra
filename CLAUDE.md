# Physics Lab Co-Developer Guide — Universal CLAUDE.md

Welcome! This file serves as the definitive reference guide for all AI systems (like Claude, Cursor, or Gemini) and human developers working on the Physics Lab project. It defines our environment commands, strict validation quality gates, database architecture, and recent milestones.

---

## 🚀 1. Quick Reference Commands

All Python operations must be executed using the project's local virtual environment (`.venv/`).

### 📦 Content Graduation Pipeline
* **Bootstrap Scaffolding**: Automatically creates topological neighbor transitions in `draft.html` and formats `identities.json` placeholders:
  ```bash
  .venv/bin/python3 scripts/maintenance/bootstrap_expansion.py <subtopic-slug>
  ```
* **Retrieve Concept Details**: Crawls shards to safely view JSON metadata without context bloat:
  ```bash
  .venv/bin/python3 scripts/maintenance/retrieve_concept.py <subtopic-slug>
  ```
* **Compile and Graduate Subtopic**: Compiles the draft, auto-links keywords, renders formulas to vector SVGs, updates shards, and commits to Git:
  ```bash
  .venv/bin/python3 scripts/maintenance/commit_node.py <subtopic-slug> draft.html identities.json
  ```
* **Synchronize MariaDB Database (Manual)**: Synchronizes the physical JSON shards on disk with the active SQL database:
  ```bash
  php scripts/maintenance/sync_node.php <subtopic-slug>
  ```

### 🛡️ Validation & Test Suite
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
* **Zero-Artifact Continuous Prose**: Only high-density technical HTML prose is allowed.
  * *Forbidden*: Lists, bullets, or numbered elements (`<ul>`, `<li>`, `<ol>`).
  * *Forbidden*: Fragmented headers or summaries inside content strings.
  * *Syntax Purity*: Wrap all paragraphs in `<p>` tags. Bold key terms using `<strong>` tags only. **Strict ban on markdown double asterisks (`**`) or underscores (`__`) inside content strings.**
* **Word Count**: Strictly between **650 to 1,000 words** of dense, senior undergraduate to graduate-level academic prose.

### B. Topological & Symmetrical Symmetries
* **Small-World Connectivity**: Every Platinum node must establish:
  * Minimum of **5 outgoing links** to neighboring subtopics.
  * Minimum of **2 incoming links** from other subtopics.
  * Minimum of **1 cross-hub bridge** connecting to a completely different Pillar Hub (e.g., Astrophysics linking to Thermodynamics).
* **The Identity Lock**: A node must contain at least **one (1) registered mathematical identity** matching the physical skeleton.
  * *Delimiters ban*: In `identities.json`, the `"equation"` value must be written as **pure, raw LaTeX strings without outer display delimiters** (i.e. no `\\[` or `$$` wrappers), as the compiler wraps them dynamically on render.
* **The Limiting Case Clause**: The prose must mathematically or conceptually demonstrate its Limiting Case (e.g. how General Relativistic scaling reduces to local flat Minkowski spacetime governed by the flat-space energy-momentum relation).

### C. Structural Gateway Constraints
* **Topic Hubs (Categories)**: The 12 primary category entryways (e.g., `astrophysics`, `relativity`) are locked metadata structures and must **never** be modified or subjected to the OPS.
* **Overview Articles**: Corresponding narrative overview articles are designated with the `-overview` suffix (e.g., `theoretical-physics-overview`). These carry the high-density academic overviews and conform strictly to the OPS. **All internal links routing to a primary discipline entryway must point to the overview slug, not the locked category slug.**

---

## ⚙️ 3. Core Platform Architecture

### A. Sharded Relational JSON Database
* The database is stored as unified storage shards inside `app/config/content/` (e.g. `astrophysics.json`, `relativity.json`).
* Concepts are mapped uniquely to exactly **one** physical storage shard.
* Shard slugs are indexed and resolved globally via `search_index.json`.

### B. Dynamic Hub Validation Engine (`orchestrator.py`)
Our context-affinity validation engine has been upgraded to a state-of-the-art dynamic model:
1. **TF-IDF Dynamic Signatures (Upgrade A)**: On initialization, `PhysicsOrchestrator` scans all graduated Platinum subtopics, calculates normalized Term Frequency-Inverse Document Frequency (TF-IDF) vectors, and dynamically overwrites `self.HUB_SIGNATURES` with the top 15 highest-weighted words for each hub.
2. **Full 12-Hub Mapping (Upgrade B)**: Affinity validations are computed dynamically across all **12 curriculum categories** matching our database categories exactly.
3. **Regex Suffix-Matching Bounds (Upgrade C)**: Scoring checks are executed using dynamic suffix-matching regex patterns with word boundary guards:
   ```python
   re.compile(r"\b" + re.escape(word) + r"(?:s|al|ally|ism|ist|ists|ing|ed|er|ers|es|tion|tions|tional|tionally|ity|ities|ic|ical|ically)?\b", re.IGNORECASE)
   ```
   This prevents grammatical extensions in the prose (e.g., "mechanical" or "classicality") from artificially lowering scores.

---

## 🏆 4. Recent Sprints & Milestones

* **May 24, 2026**: Fully completed **Phase 9 (Sprint 2, Node 1)**: Graduated **`expansion-history`** (Expansion History of the Universe) to standard Platinum in `astrophysics.json`, registering `hubble-parameter-evolution` and `friedmann-acceleration-cosmology`.
* **May 24, 2026**: Refactored the core quality-assurance validation pipeline in `orchestrator.py`, implementing **TF-IDF dynamic signatures (Upgrade A)**, **full 12-hub affinity validation (Upgrade B)**, and **suffix-matching regex bounds (Upgrade C)**.
* **May 24, 2026**: Completed **Sprint 1 (Quantum Foundations & Boundary Conditions)**: Graduated **`wave-function`**, **`born-interpretation`**, **`fermions`**, and **`past-hypothesis`** to standard Platinum.
