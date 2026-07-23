# 🌐 Project Terra: Architecture, Deployment Model & Ecosystem Roadmap

**Document Version:** 1.0.0  
**Date:** July 23, 2026  
**Status:** Active Development Blueprint  
**Repository Path:** `/Users/holobetj/code/gemini/terra`  

---

## 🏛️ 1. Master Ecosystem Vision ("Project Terra")

**Project Terra** is a multi-domain digital encyclopedia and interactive scientific laboratory engine designed to deliver mathematically rigorous, deep-dive academic references paired with interactive theoretical sandboxes.

```
                                  +---------------------------------------+
                                  |            PROJECT TERRA              |
                                  |     (Unified Core Scientific Engine)  |
                                  +---------------------------------------+
                                                      |
         +--------------------------------------------+--------------------------------------------+
         |                                            |                                            |
         v                                            v                                            v
+----------------------------------+     +----------------------------------+     +----------------------------------+
|          PHYSICS LAB             |     |          CHEMISTRY LAB           |     |           BIOLOGY LAB            |
|   (Flagship Module - Active)     |     |       (Future Domain Module)     |     |       (Future Domain Module)     |
| - 13 Physical Domains            |     | - Molecular Dynamics             |     | - Genomics & Biophysics          |
| - 1,584 Subtopics (100% Platinum)|     | - Reaction Kinetics              |     | - Cellular Thermodynamics        |
| - 7,633 Pre-Rendered Formulas    |     | - Quantum Chemistry              |     | - Ecological Systems             |
| - 9 Interactive Lab Tools        |     | - Interactive Orbital Solvers    |     | - Evolutionary Graph Networks    |
+----------------------------------+     +----------------------------------+     +----------------------------------+
```

### Key Principles of Terra Domain Modules:
1. **Shared Core Engine**: Built on a unified FlightPHP MVC backend, sharded JSON disk relational data layer, pre-rendered vector SVG math pipeline, and glassmorphic frontend UI system.
2. **Interactive Variational Tools**: Each domain incorporates custom interactive solvers, notation toggles, and term-by-term identity explainers.
3. **The Organic Platinum Standard (OPS)**: Enforces zero-filler academic prose, continuous non-bulleted paragraphs, high math density, and small-world network topology across all domain topics.

---

## 💻 2. Environment Topology & Development Model

The development, testing, and deployment workflows for Terra follow a clean, self-contained staging-to-production lifecycle:

```
+-----------------------------------------------------------------------------------+
|                        LOCAL DEVELOPMENT ENVIRONMENT (macOS)                       |
+-----------------------------------------------------------------------------------+
|  • FlightPHP Dev Server: Served at http://localhost:8000                          |
|  • Python Runtime: Local virtual environment (.venv/)                             |
|  • Local MariaDB & JSON Disk Shards: 256 Formula Shards + 13 Topic Shards         |
|  • Source Control: Git branch tracking & local commit history                      |
+-----------------------------------------------------------------------------------+
                                         │
                                         │ Push via Git Deployment Pipeline
                                         ▼
+-----------------------------------------------------------------------------------+
|                      INDEPENDENT PRODUCTION SERVER (LAMP Stack)                   |
+-----------------------------------------------------------------------------------+
|  • OS: Linux (Ubuntu / RHEL)                                                      |
|  • Web Server: Apache 2.4+ (mod_rewrite enabled for FlightPHP routing)            |
|  • Database: MariaDB / MySQL 8.0+                                                 |
|  • PHP Runtime: PHP 8.1+ with PDO Extensions                                      |
|  • Ongoing Updates: Future features developed on Mac -> Pushed to LAMP via Git    |
+-----------------------------------------------------------------------------------+
```

### Workflow Mechanics:
- **Local Isolation**: Development is conducted on a macOS workstation using a local FlightPHP environment (`composer start`) and local MariaDB server.
- **Git Replication**: Version control tracks all application code, database schema migrations, content shards, SVG caches, and test suites.
- **Production Deployment**: Upon public launch, the repository will be cloned directly to an independent production LAMP server. Future feature developments, content expansions, and maintenance releases will continue on the Mac environment and be deployed seamlessly to the production LAMP server via Git updates.

---

## 🏗️ 3. Core Technical Stack Architecture

The **Physics Lab** flagship module exemplifies the standard technical architecture for all Terra modules:

```
+-----------------------------------------------------------------------------------+
|  VIEW & PRESENTATION LAYER                                                        |
|  • PHP Views (app/views/physics/*) with FlightPHP layout wrappers                 |
|  • Vanilla CSS Glassmorphism Engine (public/css/physics.css)                      |
|  • Dynamic HTML5 Canvas Particle Engine (public/js/hero_canvas.js)               |
|  • Pre-Rendered Vector Math (MathJax SVG output in #FFD700 gold styling)           |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  CONTROLLER & ROUTING LAYER                                                       |
|  • FlightPHP Micro-Framework (flightphp/core)                                     |
|  • PhysicsController (app/controllers/PhysicsController.php)                      |
|  • REST & Partial AJAX Endpoints                                                  |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  DATA & PERSISTENCE LAYER                                                         |
|  • MariaDB Relational Database (physics_subtopics, physics_formulas, relations)   |
|  • Sharded JSON Disk Storage (13 Topic Shards + 256 Formula Shards)               |
|  • High-Speed Trie Search Index (build_manifest.json, search_index.json)          |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  ORCHESTRATION & QUALITY ENGINEERING LAYER                                        |
|  • PhysicsOrchestrator (orchestrator.py): Batch rendering & TF-IDF indexing       |
|  • Graduation Queue Stack CLI (gqs.py): AI Seeding & OPS Quality Gates            |
|  • Integrity Shield (integrity_shield.py): Entity auto-linker & network auditor   |
|  • Regression Suite (pytest): 102 Automated Health & Security Tests               |
+-----------------------------------------------------------------------------------+
```

---

## 🛠️ 4. Flagship Module Inventory: Physics Lab Interactive Suite

The Physics Lab flagship module includes **9 integrated interactive laboratory tools**:

1. **Equation Explainer**: Deconstructs complex LaTeX identities with real-time term-by-term variable inspection, MathJax rendering, and interactive variable substitution (housed in a full-width top panel).
2. **Dimensional Solver**: Symbolic algebraic engine verifying dimensional consistency $[M^a L^b T^c I^d \Theta^e N^f J^g]$ and deriving unit balance equations.
3. **Noether's Vault**: Maps continuous spacetime and gauge symmetries directly to conserved Noether charges (e.g., time translation $\rightarrow$ energy conservation).
4. **Legendre Transformer**: Performs symbolic mappings between Lagrangian $L(q, \dot{q}, t)$ and Hamiltonian $H(q, p, t)$ formalisms.
5. **Notation Toggle**: Instantly translates physical identities between index notation, differential forms, vector calculus, and Dirac bra-ket notation.
6. **Correspondence Workspace**: Interactive classical vs. quantum trajectory comparison ($\hbar \to 0$).
7. **Anthropic Tuner**: Explores fundamental cosmological constant variations and stellar fusion viability dials.
8. **Genealogy Explorer**: Visual derivation tree connecting foundational axioms to downstream physical laws.
9. **Simulation Sandboxes**: Dynamic HTML5 Canvas physics simulations.

---

## 🚀 5. Multi-Domain Scientific Expansion Roadmap

As Terra evolves beyond Physics, additional science domains will be introduced into the repository structure:

```
app/
├── controllers/
│   ├── PhysicsController.php      # Active Flagship Module
│   ├── ChemistryController.php    # Planned Module
│   └── BiologyController.php      # Planned Module
├── views/
│   ├── physics/                   # Active Domain Views
│   ├── chemistry/                 # Planned Domain Views
│   └── biology/                   # Planned Domain Views
└── config/content/
    ├── physics/                   # Sharded Physics Subtopics & Formulas
    ├── chemistry/                 # Sharded Chemistry Subtopics & Formulas
    └── biology/                   # Sharded Biology Subtopics & Formulas
```

---

## 📄 6. Summary Checklist for Deployment

- [x] FlightPHP MVC core operational at `http://localhost:8000`
- [x] 1,584 Physics Subtopics fully enriched & graduated to 100.00% Organic Platinum Status
- [x] 7,633 Physics Formulas fully enriched and pre-rendered to SVG
- [x] 102 Automated unit tests green in Pytest
- [x] Git local branch clean and tracking all shards and documentation
- [ ] Prepare production deployment script (`deploy.sh`) for target LAMP server
