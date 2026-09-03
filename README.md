# 🌌 Physics Lab: Senior-Undergraduate & Graduate Digital Physics Encyclopedia

Physics Lab is a university-level digital physics encyclopedia and computational manifold designed to deliver mathematically rigorous, topologically dense academic articles and formula derivations. 

The web frontend is built on a streamlined **FlightPHP** MVC framework, while the underlying data layer is partitioned across a **256-shard deterministic mathematical formula manifold** and **14 thematic subtopic prose shards** on disk, synchronized with a **MariaDB** query engine. Content transitions and mathematical rigor are governed by the **Organic Platinum Standard (OPS)**, automated derivation graph audits (Lineage Health Index), and pre-push integrity shields.

> [!NOTE]
> **Project Terra Blueprint & Deployment Model:** Physics Lab is the flagship domain module of **Project Terra**, an overarching scientific laboratory and reference ecosystem. The project is developed locally on macOS (`http://localhost:8000`), tracked via Git, and deployed to an independent production LAMP stack. For details, see [docs/terra_project_blueprint.md](file:///Users/holobetj/code/gemini/terra/docs/terra_project_blueprint.md).

---

## 📊 Quantitative Scale & System Metrics

| Metric | Current Status | Description |
| :--- | :---: | :--- |
| **Cataloged Formulas** | **14,613** | Fully indexed, with semantic variables, symmetry origins, and limits |
| **Formula Data Shards** | **256** (`00`–`ff`) | Deterministic $O(1)$ hex-hashed flat-file JSON shards (`shard_xx.json`) |
| **Lineage Health Index (LHI)** | **95.0 / 100** | Derivation density score across parent-child mathematical DAG |
| **Manifold Closure** | **100.0%** | Zero unmapped physical formulas detected in encyclopedia prose |
| **Subtopic Articles** | **1,584** | High-density graduate-level articles across 12 primary domains |
| **Automated Test Coverage** | **3,141 / 3,142 Passing (100.0%)** | Pytest regression suite covering schemas, math delimiters, and syntax |

---

## 🚀 1. Quickstart & Commands

All Python-based data maintenance, content generation, and quality compilation operations must run using the project's local virtual environment (`.venv/`).

### 🌐 Web Server (FlightPHP Frontend)
The frontend serves the encyclopedia, manages URL routing to subtopics, renders dynamic MathJax 3.x vector equations, and hosts the interactive Equation Explainer workbench.
* **Prerequisites**: PHP 8.0+ and Composer.
* **Launch Local Server**:
  ```bash
  composer install
  composer start
  ```
  The application is served at `http://localhost:8000`.

### 🐍 Pipeline & Content CLI (Python Backend)
* **Check Status & Quality Metrics**:
  ```bash
  .venv/bin/python3 gqs.py status
  ```
* **Run Lineage Health Index (LHI) Audit**:
  ```bash
  scripts/fixlineage --summary
  ```
* **Repair / Decorrupt Equation via URL or ID (`fixlatex`)**:
  ```bash
  scripts/fixlatex "http://localhost:8000/physics/equation-explainer?id=<formula-id>"
  ```
* **Run Pytest Regression Suite**:
  ```bash
  .venv/bin/python3 -m pytest tests/
  ```
* **Run Sitewide Integrity Shield Audit**:
  ```bash
  .venv/bin/python3 integrity_shield.py
  ```

---

## 🏛️ 2. Key Architectural Systems

### 🧮 1. The Mathematical Formula Manifold (256 Hex Shards)
Rather than maintaining an unwieldy single JSON file, all **14,613 formulas** are distributed across 256 deterministic hex shards located in `app/config/content/formulas/[00-ff]/shard_[00-ff].json`. 
- Target shard paths are computed mathematically in $O(1)$ time via `md5($id)[0:2]`.
- Eliminates file-locking bottlenecks, enables parallel asynchronous batch read/writes, and synchronizes seamlessly with MariaDB tables.

### 🌳 2. The Derivation Lineage Graph (DAG)
Formulas in the encyclopedia are not isolated mathematical expressions; they form an interconnected directed acyclic graph (DAG) of physical lineage:
- **Parent Master Equations**: Foundational axioms (e.g. Einstein Field Equations, Dirac Equation, $SO(10)$ Grand Unification).
- **Derivation Classifications**: `DERIVED_FROM`, `SPECIAL_CASE`, `APPROXIMATION`, `LIMITING_CASE`, `DEFINITION`, `AXIOMATIC_FOUNDATION`.
- **Subcomponents**: Phenomological branching terms and irreducible representations.
- **Graph Storage**: Serialized in `app/config/formula_derivation_graph.json` and gzip-compressed for fast client delivery.

### 🔬 3. Equation Explainer & Dissection Suite
An interactive laboratory workbench accessible at `/physics/equation-explainer`:
- **Symbolic Breakdown**: Isolates base physical parameters from operational subscripts, superscripts, and tensor indices.
- **Dynamic MathJax 3.x Engine**: Full vector zooming, interactive term inspection, and real-time AST synthesis.
- **Curator Drawer**: In-browser curation suite allowing physicists to draft, inspect, verify, and graduate mathematical formulas with instant shard synchronization.

### 🎨 4. Dual-Engine Math Pipeline
- **Static Reading (Encyclopedia Hubs)**: Pre-rendered SVG sprites (`math_sprites.svg`) allow instant First Contentful Paint (FCP) without client-side parsing lag.
- **Dynamic Exploration (Explainer Workbench)**: MathJax 3.x vector rendering directly from raw TeX sources, providing dynamic symbol tooltips, term highlighting, and copy-ready LaTeX.

---

## 🏛️ 3. The Organic Platinum Standard (OPS)

Every subtopic article in the encyclopedia is validated against strict quality gates enforced by `integrity_shield.py`:

### ✍️ Qualitative Prose Mandates
1. **The "In Media Res" Lead**: The opening sentence must lead directly with a physical principle, identity, or derivation. Introductory filler (e.g., *"This article covers..."* or *"The [Topic] is..."*) is strictly forbidden. The subtopic title must not appear in the first 15 words.
2. **Zero-Artifact Continuous Prose**: Only high-density, university-level academic HTML paragraphs wrapped in `<p>` are allowed. Lists (`<ul>`, `<ol>`), fragmented headers (`<h2>`, `<h3>`), and markdown formatting (such as `**` or `__`) inside content strings are strictly prohibited.
3. **Anti-Formulaic Integration**: Standard glossary introductions (e.g., *"This is defined by the following equation:"* or *"...where x is mass"* immediately following an equation) are forbidden. Equations and variable symbols must be woven organically as grammatical continuations of physical sentences.
4. **Visual Texture & Math Density**: Every paragraph in every node—including conceptual or philosophical articles—must contain at least **2 to 4 distinct inline MathJax expressions** (e.g., \( g_{\mu\nu} \), \( |\Psi\rangle \)).
5. **Explicit Variable Coupling**: Physical variables, operators, or spaces must be coupled directly with their mathematical representations on first mention (e.g., writing "metric tensor \( g_{\mu\nu} \)" instead of just "metric tensor").
6. **Word Count Cushion**: Standard subtopics must contain **650 to 1,000 words** of stripped prose (~800-950 raw words). Category Hub Overviews (`-overview` slugs) are targeted at **800 to 1,000 words**.

### 🕸️ Topological Connectivity Symmetries
* **Outgoing Links**: A minimum of **5 outgoing links** to neighboring concepts.
* **Incoming Links**: A minimum of **2 incoming links** from other concepts.
* **Cross-Hub Bridge**: A minimum of **1 bridge link** connecting to a completely different primary pillar category.

---

## 📂 4. Repository Directory Structure

```
physics-lab/
│
├── app/                              # FlightPHP MVC Application
│   ├── controllers/                  # Route controllers (PhysicsController.php)
│   ├── logic/                        # Core service layer (PhysicsService.php)
│   ├── config/                       # Application configuration & content
│   │   ├── content/                  # The Sharded Data Manifold
│   │   │   ├── formulas/             # 256 Deterministic Formula Shards (00/ to ff/)
│   │   │   │   ├── 00/shard_00.json
│   │   │   │   └── ...
│   │   │   ├── astrophysics.json     # Thematic subtopic prose shards
│   │   │   ├── relativity.json       # ... (14 Total Subtopic Shards)
│   │   │   ├── formulas_latex_index.json # High-performance canonical TeX trie
│   │   │   ├── formula_derivation_graph.json.gz # Lineage DAG
│   │   │   ├── search_index.json     # Global content index mapping
│   │   │   └── math_sprites.svg      # Consolidated vector MathJax glyphs
│   │   ├── routes.php                # Frontend URL routing
│   │   └── services.php              # Dependency injection configuration
│   └── views/                        # UI Layouts & HTML Templates
│       └── physics/
│           ├── layout.php            # Base HTML template containing SVG sprite sheet
│           ├── subtopic.php          # Single subtopic rendering template
│           └── equation_explainer.php# Flagship interactive formula workbench
│
├── scripts/                          # Maintenance & Repair Tooling
│   ├── fixlatex                      # CLI tool: URL & formula TeX decorruptor
│   ├── fixlineage                    # CLI tool: Derivation graph health auditor
│   └── maintenance/                  # Automation & Pipeline Scripts
│       ├── auto_linker.py            # Aho-Corasick auto-linking engine
│       ├── run_gqs_sprint.py         # Transactional sprint orchestrator
│       ├── lineage_resolver.py       # Derivation graph lineage inference
│       └── ...
│
├── tests/                            # Automated Pytest Suite (3,100+ tests)
├── docs/                             # Architecture Reports, Sprints & Governance
├── orchestrator.py                   # TF-IDF Context-Affinity Engine
├── integrity_shield.py               # Sitewide Quality Assurance & Manifold Gate
├── gqs.py                            # Graduation Queue Stack CLI
└── README.md                         # Project documentation
```

---

## 🛡️ 5. AI Cost Governance & Token Safety Standard

All AI automation scripts in this repository adhere to the **Deterministic Token Estimation Standard** detailed in [`docs/token_estimation_and_cost_governance.md`](file:///Users/holobetj/code/gemini/terra/docs/token_estimation_and_cost_governance.md):
1. **Pure Free-Tier Default**: Interactive drafting and automated local tools default to Google AI Studio's Free Tier (`GEMINI_FREE_API_KEY`) capped at **$0.00**.
2. **Pre-Flight Token Counting**: Input payloads are sized via `client.models.count_tokens()` before dispatching calls.
3. **Hard Output Caps**: Thinking budgets and maximum output tokens are bounded mathematically.
4. **Mandatory Budget Ceilings**: Batch runners enforce strict, non-zero dollar cutoffs (`--max-cost-dollars`).
