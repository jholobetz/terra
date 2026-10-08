# 🌐 Expanding the Knowledge Web: Hypothetical Subtopic Ingestion Guide

> **Document Status**: Archived Tutorial & Expansion Blueprint  
> **Document Reference**: `archive/add_new_subtopics_hypothetical.md`  
> **Date**: 2026-10-04 (Archived: 2026-10-07)  
> **Target Scenario**: Fleshing out thin encyclopedia shards (e.g., `fluids-nonlinear.json`)  
> **Related References**: [`CLAUDE.md`](../CLAUDE.md), [`README.md`](../README.md), [`docs/roadmap.md`](../docs/roadmap.md)

---

## 1. Executive Summary

In the **Terra Physics Lab** platform, expanding the encyclopedia—such as enriching a relatively thin domain like **Fluid Dynamics & Nonlinear Systems** (currently 20 subtopics) compared to comprehensive hubs like Astrophysics (281 subtopics) or Electromagnetism (254 subtopics)—is fundamentally different from adding articles to a static blog or wiki.

Physics Lab operates as an **interconnected mathematical and topological manifold**. Every subtopic article and physical formula is coupled into a multi-layer relational architecture:
1. **The Subtopic Shards**: 14 thematic JSON shards (`app/config/content/*.json`) and MariaDB `subtopics` table.
2. **The Formula Manifold**: 14,671+ equations partitioned across 256 deterministic hex shards (`app/config/content/formulas/[00-ff]/shard_[xx].json`) and MariaDB `formulas` table.
3. **The Derivation Lineage DAG**: A directed acyclic graph maintaining the Lineage Health Index (LHI $\ge 95.0$, with 0 isolated nodes).
4. **The Topological Link Graph**: Enforces strict inbound/outbound connectivity and cross-hub bridges.
5. **The Organic Platinum Standard (OPS)**: Enforces academic prose quality, In Media Res physical openings, and rich inline MathJax density.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   THE 5-LAYER KNOWLEDGE EXPANSION CASCADE              │
├────────────────────────────────────────────────────────────────────────┤
│ 1. CURRICULUM TOPOLOGY     Select missing foundational & graduate nodes │
│ 2. OPS PROSE GRADUATION    Write zero-artifact continuous academic TeX │
│ 3. GRAPH RE-LINKING        Enforce 5 out / 2 in / 1 cross-hub bridge   │
│ 4. FORMULA MANIFOLD & DAG  Catalog equations, maintain LHI (95.2+)     │
│ 5. DUAL-LAYER SYNC & TEST  Update Git shards, MariaDB, and Pytest net  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Baseline Diagnostic: The "Thin Shard" Dilemma

As audited via `gqs.py status`, `fluids-nonlinear.json` currently contains only **20 subtopics** (all 100% Platinum):
* *Core Fluids*: `navier-stokes-equations`, `euler-fluid-equations`, `bernoulli-principle`, `potential-flow`, `kelvins-circulation-theorem`, `reynolds-number`, `boundary-layer-theory`, `stokes-flow`, `poiseuille-flow`.
* *Turbulence & Hydrodynamic Instabilities*: `kolmogorov-cascade`, `hydrodynamic-stability`, `astrophysical-fluid-dynamics`, `stellar-wind-hydro`, `supersonic-jets`.
* *Nonlinear Dynamics & Chaos*: `bifurcation-theory`, `strange-attractors`, `lyapunov-exponents`, `molecular-chaos`, `magnetohydrodynamics-basis`.

While mathematically pristine and fully graduated, critical senior-undergraduate and graduate-level theoretical topics are currently absent:
* **Fluid Instabilities & Vorticity**: Rayleigh-Taylor instability, Kelvin-Helmholtz shear instability, Rayleigh-Bénard thermal convection, Kármán vortex shedding, Helmholtz vorticity conservation theorems.
* **Nonlinear Waves & Soliton Manifolds**: Korteweg-de Vries (KdV) solitons, Burgers' nonlinear diffusion equation, shock waves and Rankine-Hugoniot jump conditions, shallow water wave equations.
* **Advanced Nonlinear & Chaotic Systems**: The Lorenz attractor system, Poincaré-Bendixson theorem, KAM (Kolmogorov-Arnold-Moser) theorem, period-doubling cascades & Feigenbaum constants, Kuramoto synchronization model, and fractal phase-space dimensions.
* **Quantum & Relativistic Fluids**: Two-fluid model of Superfluid Helium ($^4\text{He}$), Gross-Pitaevskii quantum fluid dynamics, and relativistic hydrodynamics.

---

## 3. The End-to-End Ingestion Lifecycle

When executing an expansion sprint for a thin shard, developers and automated agents must adhere to the following sequence:

### Step 1: Scaffold Targets via the Graduation Queue Stack (GQS)
Candidate slugs are queued into the Central Tracking Authority (CTA) and scaffolded into the active compilation payload:
```bash
# Example: scaffold the next N candidate targets into subfiles/batch_payload.json
.venv/bin/python3 gqs.py template <N>
```
Each entry in `subfiles/batch_payload.json` provides standard schema properties:
* `title`: Academic subtopic title.
* `content`: Draft HTML body text.
* `parents`: Parent category hub (e.g., `["fluids-nonlinear"]`).
* `formula_ids`: Associated canonical formula IDs.
* `standard`: Initial quality classification (`"platinum"` upon completion).

### Step 2: OPS Prose Authoring & Qualitative Invariants
Prose must pass the strict gates evaluated by `integrity_shield.py`:
* **The "In Media Res" Lead**: The article must open directly with a fundamental physical identity, conservation law, or derivation. It cannot begin with *"The [Topic] is..."* or *"This concept refers to..."*, and the subtopic title must not appear within the first 15 words of the opening sentence.
* **Zero-Artifact Continuous Prose**: High-density academic HTML paragraphs wrapped exclusively in `<p>` and `<strong>`. **No bullet lists (`<ul>`, `<ol>`, `<li>`), fragmented headers (`<h2>`, `<h3>`), or markdown formatting (`**`, `__`) inside JSON content strings.**
* **Anti-Formulaic Integration**: Mathematical identities must be introduced as natural grammatical continuations of physical sentences (avoiding phrases like *"This is defined by the following equation:"*).
* **Rich Inline MathJax Texture**: Every paragraph must integrate **2 to 4 distinct inline MathJax expressions** (e.g., \( \nabla \times \mathbf{v} \), \( \text{Re}_c \), \( \lambda_{\text{max}} \)), coupling physical variables directly to their mathematical notation.
* **Word Count Cushion**: Standard subtopic articles must contain **650 to 1,000 words** of stripped prose (~800–950 raw words).

### Step 3: Topological Graph Invariants & Back-Linking
In a sparse shard, maintaining topological symmetry requires deliberate relational engineering:
1. **Outgoing Links ($\ge 5$)**: The new subtopic links to adjacent fluid mechanics and mathematical concepts.
2. **Cross-Hub Bridges ($\ge 1$)**: Fluid Dynamics connects naturally to other core pillar hubs:
   * **Astrophysics**: Accretion disk viscosity ($\alpha$-disks), solar wind, pulsar relativistic jets.
   * **Thermodynamics & Statistical Mechanics**: Dissipative entropy production, Boltzmann transport, viscous heat dissipation.
   * **Classical Mechanics**: Hamiltonian chaos, action-angle variables, symplectic phase space.
   * **Relativity**: Relativistic energy-momentum tensor $T^{\mu\nu} = (\rho + p)u^\mu u^\nu + p g^{\mu\nu}$.
3. **Incoming Links ($\ge 2$ / Zero Orphans)**:
   * A new node cannot exist as an isolated leaf node. Existing subtopics (e.g., `navier-stokes-equations` or `hydrodynamic-stability`) must be updated to link *inbound* to the new subtopic.
   * The automated Aho-Corasick auto-linking engine (`scripts/maintenance/auto_linker.py`) scans the encyclopedia for natural keyword mentions to establish inbound references.

### Step 4: Formula Manifold & Derivation DAG Linkage (LHI Preservation)
New governing equations (e.g., the KdV equation $\partial_t u + u \partial_x u + \partial_x^3 u = 0$, or the Lorenz attractor differential system) must be formally cataloged:
1. **100% Manifold Closure**: All display equations must resolve to a registered formula ID (`php scripts/audit_prose_equations.php`).
2. **Deterministic Hex Sharding**: Formulas are mapped to one of the 256 hex shards (`app/config/content/formulas/[00-ff]/shard_[xx].json`) via `md5($id)[0:2]`.
3. **Lineage Health Index (LHI)**:
   * New formulas must be wired into the parent-child derivation DAG (`formula_derivation_graph.json.gz`).
   * Formulas must possess classified derivation relationships (`DERIVED_FROM`, `SPECIAL_CASE`, `APPROXIMATION`, `LIMITING_CASE`).
   * "Floating" unlinked formulas degrade the encyclopedia's **95.2 LHI** score. Developers must run `scripts/fixlineage --heal` or manually define reciprocal derivation edges to guarantee **0 isolated nodes**.
4. **Step-by-Step Derivations**: High-value foundational identities should receive collapsible mathematical proofs (`derivation_steps`) for display in the Equation Explainer and Formula Inspector.

### Step 5: Compilation, Database Ingestion, and Regression Testing
Once drafted in `subfiles/batch_payload.json`, the sprint is compiled and verified:
```bash
# Ingest and graduate drafted subtopics into shards and database
.venv/bin/python3 gqs.py ingest

# Run full regression suite and sitewide integrity shields
.venv/bin/python3 integrity_shield.py
.venv/bin/python3 -m pytest tests/
```
The ingestion process:
* Writes validated subtopics to `app/config/content/fluids-nonlinear.json`.
* Updates MariaDB relational records in `subtopics` and `formulas`.
* Recalculates `formulas_hash_registry.json` and synchronizes `formulas_latex_index.json`.
* Purges stale static HTML disk caches in `public/cache/subtopic/`.

---

## 4. Integration with Interactive Laboratories

Expanding the `fluids-nonlinear` shard directly reinforces the platform's visual and analytical tools:
* **The Kármán Vortex Street Engine** ([`public/js/simulations/vortex-street.js`](file:///Users/holobetj/code/gemini/terra/public/js/simulations/vortex-street.js)): Visualizes 2D Navier-Stokes boundary layer separation and periodic vortex shedding.
* **The Double Pendulum Chaos Engine** ([`public/js/simulations/double-pendulum.js`](file:///Users/holobetj/code/gemini/terra/public/js/simulations/double-pendulum.js)): Demonstrates Runge-Kutta 4th-order (RK4) integration, sensitive dependence on initial conditions, and Lyapunov divergence.
* **The Lab Tools Cockpit (`/physics/lab-tools`)**: Provides SymPy CAS symbolic proofs, variational mechanics, and phase-space orbits for nonlinear Lagrangians and Hamiltonians.

New subtopics in fluid dynamics and nonlinear chaos can link directly to these interactive sandboxes, grounding abstract continuum mechanics in visual computation.

---

## 5. Summary Execution Checklist

| Phase | Milestone / Action | Tool / Command | Verification Criteria |
| :--- | :--- | :--- | :--- |
| **1. Planning** | Target Curation | Review missing fluid/chaos nodes | 10–20 high-affinity graduate topics |
| **2. Scaffolding** | Payload Generation | `.venv/bin/python3 gqs.py template <N>` | Populates `subfiles/batch_payload.json` |
| **3. Authoring** | OPS Content Drafting | Sandboxed editing | In Media Res lead, no lists, 2–4 MathJax/para, 650–1,000 words |
| **4. Topology** | Inbound Link Injection | `scripts/maintenance/auto_linker.py` | Guarantees $\ge 2$ inbound links (0 orphans) |
| **5. Bridging** | Cross-Hub Connections | Manual semantic links | Connects to Astrophysics, Relativity, Thermo, Mechanics |
| **6. Lineage** | DAG & LHI Auditing | `scripts/fixlineage --heal` | Connects new equations into DAG; preserves LHI $\ge 95.0$ |
| **7. Gatekeeper** | Ingestion & Test Net | `gqs.py ingest` + `pytest` | 100% passing tests, 0 broken links, clean MariaDB sync |
