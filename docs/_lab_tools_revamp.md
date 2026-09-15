# 🔬 Strategic Architecture: Lab Tools Hub Revamp & Interactive Workbench Specification

> **Document Status**: Proposed / Active Architecture Exploration  
> **Document Reference**: `docs/_lab_tools_revamp.md`  
> **Target Horizon**: 2026–2027 (Phase 2 Roadmap)  
> **Authoritative References**: [`docs/architecture.md`](architecture.md), [`docs/roadmap.md`](roadmap.md), [`CLAUDE.md`](../CLAUDE.md)

---

## 1. Executive Summary & Diagnostic

The **Terra Physics Lab** platform hosts an extensive collection of specialized, mathematically rigorous computational engines and registers. However, the current landing page at [`/physics/lab-tools`](http://localhost:8000/physics/lab-tools) (rendered by `app/views/physics/lab_tools.php`) operates as a static "link farm" of cards, forcing visitors to context-switch across 11 disparate URLs without any in-page interactive capabilities.

This specification outlines the architectural vision for transforming Lab Tools from a static directory into an **Integrated Computational Physics Laboratory & Interactive Workbench**.

---

## 2. Current Inventory of Specialized Engines & Registries

The platform currently includes 11 dedicated engines and registries:

| Engine / Tool | Route | Core Mathematical & Physical Capability | Status |
| :--- | :--- | :--- | :---: |
| **Dimensional Solver** | `/physics/dimensional-solver` (Archived) | Evaluates SI base dimensions ($[M^a L^b T^c I^d]$); archived from standalone page into `docs/archive/dimensional_solver/` pending integrated workbench absorption. | 📦 Archived |
| **Notation Toggle** | `/physics/notation-toggle` | Translates physical laws seamlessly between coordinate-free vectors, tensor index contractions, and Cartan differential forms. |
| **Noether's Vault** | `/physics/noethers-vault` | Maps continuous spacetime and gauge symmetries ($SO(3), U(1)$) to conserved currents with real-time numerical phase-space canvases. |
| **Correspondence Workspace** | `/physics/correspondence-workspace` | Simulates the quantum-classical transition via Ehrenfest's theorem, comparing Gaussian wave packets to Newtonian point particles. |
| **Anthropic Constant Tuner** | `/physics/anthropic-tuner` | Multi-scale cosmological sandbox ($c, G, \hbar, \alpha$) recalculating atomic orbital radii, solar system stability, and stellar fusion lifetimes. |
| **Legendre Transformer** | `/physics/legendre-transformer` | Performs canonical momentum differentiation ($p_i = \partial L / \partial \dot{q}_i$), velocity inversion, and symbolic Hamiltonian construction ($H = \sum p_i \dot{q}_i - L$). |
| **Genealogy Explorer** | `/physics/genealogy-explorer` | Interactive derivation lineage DAG connecting foundational axioms to phenomenological formulas. |
| **Equation Explainer** | `/physics/equation-explainer` | Real-time LaTeX AST tokenization, variable highlight matching, MathJax vector rendering, and SymPy CAS asymptotic boundary limits. |
| **Interactive Simulations** | `/physics/simulations` | Real-time numerical solvers for classical mechanics, wave propagation, electromagnetic fields, and thermodynamic cycles. |
| **Physical Constants Register** | `/physics/constants` | Comprehensive CODATA 2022 constants table with uncertainty bounds, standard values, and SI dimensions. |
| **Physical Symbols Lexicon** | `/physics/symbols` | Universal dictionary of mathematical and physical symbols, operators, and tensor notations. |

---

## 3. Core Architectural Paradigms for the Revamp

### Option A: The Live Active Instrument Bay (Interactive Mini-Widgets)
* **Concept**: Transform `/physics/lab-tools` into an active, humming experimental laboratory floor where each tool card contains a **fully functional, live interactive widget**:
  - **Dimensional Solver Widget**: Type expressions (e.g. `G * M / c^2`) directly into the card to instantly compute dimensions (`[L]`, length / Schwarzschild radius).
  - **Anthropic Tuner Widget**: Interactive slider dials for $\alpha$ and $G$ updating a live mini-cosmic canvas on the card.
  - **Noether's Vault Widget**: Animated symmetry wheel showing rotation/translation invariance and illuminated conserved currents.
  - **Legendre Transformer Widget**: Quick toggle showing Lagrangian $\leftrightarrow$ Hamiltonian phase space conjugate pairs.
  - Clicking `[ Fullscreen Workbench ⤢ ]` elevates any widget into its full dedicated page.
* **Primary Advantage**: Immediate discovery and tactile delight; users can interact with 4 different physics engines in 30 seconds without navigating away.

---

### Option B: The Unified Laboratory Command Deck (Integrated IDE / Console)
* **Concept**: Modeled after professional scientific software (Mathematica, COMSOL, JupyterLab), consolidating all tools into a single, cohesive, zero-reload application workspace.
* **Layout Structure**:
  - **Left Instrument Dock**: Categorized into 3 functional Lab Benches:
    1. 🧮 **Symbolic & Algebraic Workstation** (Dimensional Solver, Legendre Transformer, Notation Toggle).
    2. 🔬 **Physical Sandbox & Symmetries** (Noether's Vault, Quantum Correspondence, Anthropic Tuner, Simulations).
    3. 📚 **Universal Registers & Ontologies** (CODATA Constants, Symbol Lexicon, Derivation Genealogy, Equation Explainer).
  - **Center Main Stage**: Houses the active instrument, loaded dynamically via client-side DOM swapping or asynchronous module mounting.
* **Primary Advantage**: Eliminates fragmented page reloads, providing a serious research workbench feel.

---

### Option C: Workflow-Based Experimental Suites (Chained Physics Pipelines)
* **Concept**: Organize tools around realistic **Scientific Problem-Solving Workflows**:
  1. **"Verify an Identity" Pipeline**:
     - Input Formula $\to$ Check Dimensional Homogeneity $\to$ Evaluate Asymptotic Limits via SymPy CAS $\to$ Trace Lineage in Derivation DAG.
  2. **"Symmetry to Dynamics" Pipeline**:
     - Select Continuous Symmetry $\to$ Generate Conserved Noether Current $\to$ Execute Legendre Transformation $\to$ Simulate Phase Portrait.
  3. **"Cosmological Sensitivity" Pipeline**:
     - Adjust Fundamental Constants $\to$ Recalculate Atomic Bound States $\to$ Audit Planetary Orbits $\to$ Compute Stellar Collapse Thresholds.
* **Primary Advantage**: Pedagogical brilliance; demonstrates how theoretical and computational physicists actually conduct derivations and simulations.

---

## 4. Architectural Comparison Matrix

| Dimension | Option A: Active Instrument Bay | Option B: Unified Command Deck | Option C: Workflow Suites |
| :--- | :---: | :---: | :---: |
| **Visual Wow Factor** | 🌌 Very High (Live canvases & inputs) | 🎛️ High (Sleek professional IDE) | 🔬 High (Guided narrative) |
| **Ease of Discovery** | Instant (Everything visible at once) | Seamless (Tabbed dock) | Guided (Step-by-step) |
| **Implementation Complexity** | Medium (Embed live mini-widgets) | Medium/High (Consolidate into 1 view) | High (Pipe tool outputs together) |
| **User Experience** | Hands-On Scientific Playground | Research Laboratory Console | Guided Masterclass Workspace |

---

## 5. Recommended Implementation Roadmap

1. **Phase 1: Hybrid Instrument Deck Prototype**:
   - Upgrade [`app/views/physics/lab_tools.php`](../app/views/physics/lab_tools.php) to feature live interactive mini-widgets for the top 3 engines:
     - Live Dimensional Solver scratchpad.
     - Live Anthropic multi-scale slider canvas.
     - Live Noether symmetry generator wheel.
2. **Phase 2: Common State & CAS API Integration**:
   - Connect the tools to the asynchronous REST endpoint `/physics/api/cas-evaluate` for live server-side symbolic proofs.
3. **Phase 3: Chained Workflow Mode**:
   - Allow output from the Dimensional Solver to feed directly into the Equation Explainer and Derivation DAG.
