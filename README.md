# 🌌 Physics Lab: Senior-Undergraduate & Graduate Digital Physics Encyclopedia

Physics Lab is a university-level digital physics encyclopedia designed to deliver mathematically rigorous, topologically dense academic articles. The web frontend is built on a streamlined **FlightPHP** MVC framework, while the underlying database is a sharded, flat-file relational JSON structure on disk. Content transitions and style gates are governed by a transactional **Python Content-Graduation Pipeline** that enforces the **Organic Platinum Standard (OPS)**.

> [!NOTE]
> **Project Terra Blueprint & Deployment Model:** Physics Lab is the flagship domain module of **Project Terra**, an overarching scientific laboratory and reference ecosystem. The project is currently developed locally on macOS (`http://localhost:8000`), tracked with local Git repositories, and designed to be deployed to an independent production LAMP stack. Additional scientific domain modules (e.g., Chemistry Lab, Biology Lab) will be integrated into this shared core engine. For details, see [docs/terra_project_blueprint.md](file:///Users/holobetj/code/gemini/terra/docs/terra_project_blueprint.md).

---

## 🚀 1. Quickstart & Commands

All Python-based data maintenance, content generation, and quality compilation operations must run using the project's local virtual environment (`.venv/`).

### 🌐 Web Server (FlightPHP Frontend)
The frontend serves the encyclopedia, manages URL routing to subtopics, renders LaTeX equations dynamically using lightweight MathJax SVG references, and hosts local node audits.
* **Prerequisites**: PHP 8.0+ and Composer.
* **Launch Local Server**:
  ```bash
  composer install
  composer start
  ```
  The application is served at `http://localhost:8000`.

### 🐍 Pipeline & Content CLI (Python Backend)
The Python pipeline controls database status, refactoring, validation, and content ingestion.
* **Prerequisites**: Python 3.10+ and active `.venv/`.
* **Check Status & Quality Metrics**:
  ```bash
  .venv/bin/python3 gqs.py status
  ```
* **Run Pytest Regression Suite**:
  ```bash
  .venv/bin/python3 -m pytest tests/
  ```
* **Run Sitewide Integrity Audit**:
  ```bash
  .venv/bin/python3 integrity_shield.py
  ```

---

## 🏛️ 2. The Organic Platinum Standard (OPS)

Every subtopic article in the encyclopedia is validated against strict quality gates enforced by `integrity_shield.py` and the pipeline compiler:

### ✍️ Qualitative Prose Mandates
1. **The "In Media Res" Lead**: The opening sentence of the article must lead directly with a physical principle, identity, or derivation. Introductory filler (e.g., *"This article covers..."* or *"The [Topic] is..."*) is strictly forbidden. The subtopic's title must not appear within the first 15 words.
2. **Zero-Artifact Continuous Prose**: Only high-density, university-level academic HTML paragraphs wrapped in `<p>` are allowed. Lists (`<ul>`, `<ol>`), fragmented headers (`<h2>`, `<h3>`), and markdown formatting (such as `**` or `__`) inside the content strings are strictly prohibited.
3. **Anti-Formulaic Integration**: Standard glossary introductions (e.g., *"This is defined by the following equation:"* or *"...where x is mass"* immediately following an equation) are forbidden. Equations and variable symbols must be woven organically as grammatical continuations of physical sentences.
4. **Visual Texture & Math Density**: Every paragraph in every node—including conceptual or philosophical articles—must contain at least **2 to 4 distinct inline MathJax expressions** (e.g., \( g_{\mu\nu} \), \( |\Psi\rangle \)) to eliminate visual "walls of text."
5. **Explicit Variable Coupling**: Physical variables, operators, or spaces must be coupled directly with their mathematical representations on first mention (e.g., writing "metric tensor \( g_{\mu\nu} \)" instead of just "metric tensor").
6. **Plain English Word Count Cushion**: Standard subtopics must contain **650 to 1,000 words** of prose. Because the parser strips LaTeX formulas before measuring depth, developers must draft a generous plain-prose cushion (~800 words) to clear the static floor. Primary category Hub Overviews (`-overview` slugs) are elevated to a **800 to 1,000 word** target.

### 🕸️ Topological & Connectivity Symmetries
To graduate a node to Platinum standard, it must establish a resilient small-world network topology:
* **Outgoing Links**: A minimum of **5 outgoing links** to neighboring concepts.
* **Incoming Links**: A minimum of **2 incoming links** from other concepts.
* **Cross-Hub Bridge**: A minimum of **1 bridge link** connecting to a completely different primary pillar category (e.g., Thermodynamics bridging to Astrophysics).

---

## 📂 3. Repository Directory Structure

```
physics-lab/
│
├── app/                        # FlightPHP MVC Application
│   ├── controllers/            # Route controllers (PhysicsController.php)
│   ├── config/                 # Application config & content database
│   │   ├── content/            # The Sharded JSON Relational Database
│   │   │   ├── astrophysics.json
│   │   │   ├── classical-mechanics.json
│   │   │   ├── ... (13 Content Shards)
│   │   │   ├── search_index.json      # Global content index mapping
│   │   │   └── math_sprites.svg       # Consolidated vector MathJax glyphs
│   │   ├── routes.php          # Frontend URL routing
│   │   └── services.php        # Dependency injection configuration
│   └── views/                  # UI Layouts & HTML Templates
│       └── physics/
│           ├── layout.php      # Base HTML template containing SVG sprite sheet
│           └── subtopic.php    # Single subtopic rendering template
│
├── scripts/
│   └── maintenance/            # Python Content Maintenance Scripts
│       ├── auto_linker.py      # Keyword auto-linking state machine
│       ├── run_gqs_sprint.py   # Transactional sprint orchestrator
│       ├── spritify_assets.py  # MathJax SVG sprite sheet compiler
│       ├── generate_system_health.py # Health dashboard updater
│       └── ...
│
├── tests/                      # Automated Regression Suite
│   ├── test_ops_gates.py       # OPS style gate checks (dry-run mode)
│   ├── test_integrity_shield.py # Strict schema & linkage regression checks
│   ├── test_sync_backlog.py    # Backlog verification assertions
│   └── ...
│
├── subfiles/                   # Pipeline registries and queues
│   ├── auto_link_aliases.json  # Search aliases for keyword auto-linking
│   ├── hub_signatures.json     # Cached TF-IDF signatures for categories
│   └── system_health.json      # Compiled database metrics
│
├── orchestrator.py             # TF-IDF Affinity & Context-Affinity Engine
├── integrity_shield.py         # The Sitewide Quality Assurance Gate
├── gqs.py                      # Graduation Queue Stack CLI
└── README.md                   # Project documentation
```

---

## 🏛️ 4. Key Architectural Systems

### 🗄️ Relational JSON Database Sharding
The database is fully flat-file and relational, sharded by physical physics categories inside `app/config/content/`. Shard membership is mapped globally in `app/config/content/search_index.json`. This maintains high disk-read speeds without requiring heavy external database servers in development.

### 🔗 Aho-Corasick Multi-Pattern Auto-Linker
To prevent **Catastrophic Backtracking** during keyword scanning, the compiler runs a native string-matching Aho-Corasick state machine (`scripts/maintenance/auto_linker.py`). It compiles registered synonyms and aliases into a tree, scanning plain-text prose and automatically wrapping key physics concepts in relative anchor links in linear $\mathcal{O}(L + M)$ time.

### 🎨 MathJax SVG Sprite Sheets
To optimize page load times and avoid git database bloat, MathJax equations are parsed during compilation, and raw path vectors are consolidated into a single sprite sheet: `app/config/content/math_sprites.svg`. Individual inline HTML equations reference these paths via lightweight `<use href="#math-path-<hash>"/>` tags, shrinking equation markup size by over 90%.

### 🧠 TF-IDF Context-Affinity Engine (`orchestrator.py`)
To prevent "contextual leakage" (e.g., discussing too much astrophysics in a thermodynamics node), `PhysicsOrchestrator` computes dynamic Term Frequency-Inverse Document Frequency (TF-IDF) signatures for each of the 12 curriculum hubs:
* **Background Vocabulary Filtering**: A `DF_CEILING_PCT` (default `0.60`) filters out background vocabulary (words appearing in >60% of all platinum documents, such as `energy`, `field`, `manifold`) to eliminate false positives.
* **Persistent Signature Cache**: Rebuilding signatures is optimized using a signature cache `subfiles/hub_signatures.json`, validated by a stable MD5 hash of all active Platinum subtopics to keep orchestration startup under 5ms.

### 🎨 Category Theming & Design System
To ensure a consistent, color-coded visual hierarchy across the encyclopedia's 12 primary physics categories, the frontend implements a CSS custom property scoping system:
* **Dynamic Scoping**: The wrapper element of Category Hubs (`topic.php`) and Subtopic Detail pages (`subtopic.php`) sets `--accent-color: var(--accent-<theme>);` dynamically based on the parent category resolved from the shared `_topic_icons.php` asset registry.
* **Theme Tokens**: A neon token palette is defined globally in `public/css/physics.css` (e.g., `--accent-classical: #10b981` (emerald), `--accent-relativity: #8b5cf6` (deep violet)).
* **Glassmorphic Components**: UI elements like `.concept-card`, `.related-card`, and equations panels dynamically resolve hover borders, neon shadow glows, and link decorations using native CSS `color-mix(in srgb, var(--accent-color) X%, transparent)` bounds.
* **Dynamic Watermarks**: Custom-designed category vector SVGs are reused dynamically as subtle background watermarks inside hubs, header headers, and simulation launcher cards to unify the visual identity.
* **Navbar Theme Rollouts**: Navbar menu headers and their dropdown items are styled with secondary (violet) and primary (cyan) themes, using transparent bridge overlays to maintain cursor-hover stability.

---

## 🛠️ 5. Content-Graduation CLI Guide

The GQS pipeline manages the transition of content from draft to production:

```bash
# 1. Scrutinize the database health and backlog priority stack
.venv/bin/python3 gqs.py status

# 2. Refill the Graduation Queue Stack (GQS) with pending backlog items
.venv/bin/python3 gqs.py refill <N>

# 3. Scaffold the next batch target into subfiles/batch_payload.json
.venv/bin/python3 gqs.py template <N>

# 4. (After editing payload drafts) Perform transactional syntax & style checks
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N> --dry-run

# 5. Graduate, compile, auto-link, and commit the sprint transaction
.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>
```

### 🛡️ Transactional Sprint Safety
To ensure zero content loss during automated runs, `run_gqs_sprint.py` executes a **Three-Stage Transaction Loop**:
1. **Savepoint**: Generates an automated local git savepoint commit of your workspace draft state before launching operations, recording a precise rollback hash.
2. **Arrest**: Verifies OPS prose rules and attempts MathJax vector rendering. Any failure immediately rolls back the workspace to the savepoint hash, preserving local drafts without polluting the git tree.
3. **Amend**: On successful ingestion, compiles and consolidates the changes into one clean, final graduation commit.

---

## 🛠️ 6. Maintenance Scripts Directory

Here is a summary of the load-bearing scripts located in `scripts/maintenance/`:

* **`auto_linker.py`**: Runs keyword scanning and builds relative anchor links.
* **`run_gqs_sprint.py`**: Executes a quality-guarded sprint loop for GQS queue targets.
* **`spritify_assets.py`**: Compresses MathJax SVGs in shards and caches, updating the global `math_sprites.svg` sheet.
* **`generate_system_health.py`**: Evaluates word counts, densities, qualitative violations, and compiles the `system_health.json` ledger.
* **`generate_orphans_list.py`**: Identifies subtopics with 0 incoming links and writes reports to `subfiles/orphans.md` and `subfiles/orphans.json`.
* **`sync_backlog.py`**: Performs real-time scanning of shard standards to sync the central tracking backlog and deduplicate slugs.
* **`hallucination_shield.py`**: Audits LaTeX symbols in mathematical markup against plain-text anchor words to detect notation drift.
* **`commit_node.py`**: Graduations compiler that takes single-node draft HTML, renders MathJax to SVG, performs auto-linking, and writes to database shards.
* **`batch_ingest.py`**: Performs token-saving subprocess compilation for multiple drafted subtopics sequentially.
