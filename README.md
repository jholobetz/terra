# 🌌 Physics Lab: Senior-Undergraduate & Graduate Physics Encyclopedia

Physics Lab is a university-level digital physics encyclopedia designed to present high-density, mathematically rigorous academic articles. The web frontend is built on a streamlined **FlightPHP** MVC framework, while the content is powered by a sharded relational JSON database on disk and managed via a transactional **Python Content-Graduation Pipeline** that enforces the **Organic Platinum Standard (OPS)**.

---

## 🚀 1. Project Quickstart

### 🌐 Web Server (PHP Frontend)
The frontend serves the encyclopedia, handles routing to subtopics, renders LaTeX equations using pre-compiled SVGs, and runs single-node integrity checks.
* **Prerequisites**: PHP 8.0+ and Composer.
* **Launch Development Server**:
  ```bash
  composer install
  composer start
  ```
  Then, navigate to `http://localhost:8000` in your web browser.

### 🐍 Content & Pipeline CLI (Python Backend)
All database updates, quality audits, content generation, and pipeline refactoring are run from the project's local virtual environment (`.venv/`).
* **Prerequisites**: Python 3.10+.
* **Check Database Metrics & Backlog Status**:
  ```bash
  .venv/bin/python3 gqs.py status
  ```
* **Run Sitewide Integrity Audit**:
  ```bash
  .venv/bin/python3 integrity_shield.py
  ```
* **Run Regression Tests**:
  ```bash
  .venv/bin/python3 -m pytest tests/
  ```

---

## 🏛️ 2. The Organic Platinum Standard (OPS) Quality Gates

Every article in the encyclopedia is validated against strict quality gates enforced by `integrity_shield.py` and the pipeline compiler:

### ✍️ Qualitative Prose Mandates
* **The "In Media Res" Lead**: The first sentence of the first paragraph must lead directly with a physical principle, identity, or derivation. It is forbidden to start with self-referential talk (e.g., *"In this article..."*) or mention the subtopic's title within the first 15 words.
* **Zero-Artifact Continuous Prose**: Only high-density, university-level academic HTML paragraphs wrapped in `<p>` are allowed. Lists (`<ul>`, `<ol>`), headers (`<h2>`, `<h3>`), and markdown formatting (such as `**` or `__`) inside the content strings are strictly prohibited.
* **Anti-Formulaic Integration**: Standard glossary introductions (e.g., *"This is defined by the following equation:"* or *"...where x is mass"* immediately following an equation) are forbidden. Equations and variable symbols must be woven organically as grammatical continuations of physical sentences.
* **Visual Texture & Math Density**: Every paragraph in every node—including conceptual or philosophical articles—must contain at least **2 to 4 distinct inline MathJax expressions** (e.g., \( g_{\mu\nu} \), \( |\Psi\rangle \)) to eliminate visual "walls of text."
* **Explicit Variable Coupling**: Physical variables, operators, or spaces must be coupled directly with their mathematical representations on first mention (e.g., writing "metric tensor \( g_{\mu\nu} \)" instead of just "metric tensor").
* **Plain English Word Count Cushion**: Standard subtopics must contain **650 to 1,000 words** of prose. Because the parser strips LaTeX formulas before measuring depth, developers must draft a generous plain-prose cushion (~800 words) to clear the static floor. Primary category Hub Overviews (`-overview` slugs) are elevated to a **800 to 1,000 word** target.

### 🕸️ Topological & Connectivity Symmetries
To graduate a node to Platinum standard, it must establish a resilient small-world network topology:
* **Outgoing Links**: A minimum of **5 outgoing links** to neighboring concepts.
* **Incoming Links**: A minimum of **2 incoming links** from other concepts.
* **Cross-Hub Bridge**: A minimum of **1 bridge link** connecting to a completely different primary pillar category (e.g., Thermodynamics bridging to Astrophysics).

---

## 📂 3. Platform Architecture

```
physics-lab/
│
├── app/                        # FlightPHP MVC Application
│   ├── controllers/            # Route controllers (PhysicsController.php)
│   ├── config/                 # Application config & content database
│   │   ├── content/            # The Sharded JSON Relational Database
│   │   │   ├── astrophysics.json
│   │   │   ├── classical-mechanics.json
│   │   │   ├── electromagnetism.json
│   │   │   ├── ... (13 Content Shards)
│   │   │   ├── search_index.json      # Global content index mapping
│   │   │   └── math_sprites.svg       # Consolidated vector MathJax glyphs
│   │   └── routes.php          # Frontend URL routing
│   └── views/                  # UI Layouts & HTML Templates
│
├── tests/                      # Python Automated Regression Suite
│   ├── test_gqs_status.py      # Dashboard and status CLI assertions
│   ├── test_integrity_shield.py # Strict schema & linkage regression checks
│   ├── test_ops_gates.py       # OPS style gate checks (dry-run mode)
│   └── ... (6 test files)
│
├── subfiles/                   # Pipeline registries and queues
│   ├── auto_link_aliases.json  # Search aliases for keyword auto-linking
│   ├── orphans.md              # Live record of unlinked graph nodes
│   └── system_health.json      # Latest compiled database metrics
│
├── orchestrator.py             # TF-IDF Affinity & Context-Affinity Engine
├── integrity_shield.py         # The Sitewide Quality Assurance Gate
├── gqs.py                      # Graduation Queue Stack CLI
└── README.md                   # Project documentation
```

### 🗄️ Relational JSON Database Sharding
The database is fully flat-file and relational, sharded by physical physics categories inside `app/config/content/`. Shard membership is mapped globally in `app/config/content/search_index.json`. This maintains high disk-read speeds without requiring heavy external database servers in development.

### 🔗 Aho-Corasick Multi-Pattern Auto-Linker
To prevent **Catastrophic Backtracking** during keyword scanning, the compiler runs a native string-matching Aho-Corasick state machine (`scripts/maintenance/auto_linker.py`). It compiles registered synonyms and aliases into a tree, scanning plain-text prose and automatically wrapping key physics concepts in relative anchor links in linear $\mathcal{O}(L + M)$ time.

### 🎨 MathJax SVG Sprite Sheets
To optimize page load times and avoid git database bloat, MathJax equations are parsed during compilation, and raw path vectors are consolidated into a single sprite sheet: `app/config/content/math_sprites.svg`. Individual inline HTML equations reference these paths via lightweight `<use href="#math-path-<hash>"/>` tags, shrinking equation markup size by over 90%.

---

## 🛠️ 4. The Content-Graduation CLI Guide

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
1. **Savepoint**: Generates a local git savepoint commit of your workspace draft state.
2. **Arrest**: Verifies OPS prose rules and attempts MathJax vector rendering. Any failure immediately rolls back the workspace to the savepoint hash, preserving local drafts without polluting the git tree.
3. **Amend**: On successful ingestion, compiles and consolidates the changes into one clean, final graduation commit.
