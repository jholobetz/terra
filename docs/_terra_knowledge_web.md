# Project Terra: The Knowledge DAG Web Portal (Master Landing Page Specification)
**Date**: August 5, 2026  
**File**: `docs/_terra_knowledge_web.md`  
**Purpose**: Master architectural and UX design specification for Model 3—the central interactive landing page (`/`) rendering Terra's two-phase Directed Acyclic Graph (DAG) Knowledge Web.

---

## 🏛️ Executive Concept

Model 3 transforms Project Terra's root landing page (`/`) into an interactive, 2D/3D visual network graph that proves Terra's core thesis: **Science is not a collection of isolated subjects, but an interconnected web of first-principles.**

Instead of static cards, visitors encounter a living, breathing constellation of human knowledge. The graph operates with a **Two-Phase Topological Expansion**: **Phase 1** focuses on the foundational **5 Core Sciences**, while **Phase 2** expands outward into **10 Quantitative Fields** spanning space, information, mind, finance, and engineering.

```
                           [ Phase 1: Core 5 Sciences ]
                                        │
                                   ( UI Toggle )
                                        │
                           ▼                         ▼
            [ Phase 2: Applied Outer Rings ]  [ Phase 2: Cosmic & Computational ]
```

---

## 🎨 1. Concentric Topological Ring Map (Rings 0 through 5)

Nodes are organized into concentric, color-coded topological rings based on mathematical dependence and derivation hierarchy:

| Ring Level | Phase | Department | Accent Color | Foundational Derivation Parents | Representative Nodes |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Ring 0** | **Phase 1** | **Mathematics** | Royal Purple (`#7c4dff`) | *Core Foundation Engine* | Calculus, Differential Equations, Linear Algebra, Group Theory |
| **Ring 1** | **Phase 1** | **Physical Sciences** | Cyber Cyan (`#64ffda`) | Derived from Ring 0 Math | Newton's Laws, Maxwell's Equations, Schrödinger Equation, Einstein Field Equations |
| **Ring 2** | **Phase 1** | **Chemical Sciences** | Emerald Green (`#00e676`) | Derived from Ring 1 Quantum & Stat Mech | Atomic Orbitals, Gibbs Free Energy, Nernst Equation, Arrhenius Kinetics |
| **Ring 3** | **Phase 1** | **Biological Sciences** | Bio Gold (`#aeea00`) | Derived from Ring 2 Thermos & Kinetics | Hodgkin-Huxley Membrane Equations, Replicator Dynamics, Enzyme Kinetics |
| **Ring 3** | **Phase 1** | **Earth & Planetary** | Azure Blue (`#0288d1`) | Derived from Ring 1 Fluid Dynamics | Geostrophic Wind Balance, Planetary Energy Balance, Seismic Wave Ray-Tracing |
| **Ring 4** | **Phase 2** | **Astrophysics & Cosmology** | Deep Magenta (`#e040fb`) | Derived from Relativity & Field Theory | FLRW Metric, Schwarzschild Geodesics, HR Stellar Evolution |
| **Ring 4** | **Phase 2** | **Computer Science & Info** | Electric Blue (`#00b0ff`) | Derived from Linear Algebra & Stat Mech | Shannon Entropy, Backpropagation Matrix Calculus, Quantum Gates |
| **Ring 5** | **Phase 2** | **Neuroscience & Cognitive** | Neon Pink (`#ff4081`) | Derived from Biophysics & Info Theory | Synaptic Plasticity (STDP), LIF Neuron Oscillator, EEG Fourier Spectrums |
| **Ring 5** | **Phase 2** | **Econophysics & Finance** | Financial Gold (`#ffd700`) | Derived from Stochastic SDEs & Stat Mech | Black-Scholes Option Pricing PDE, Nash Equilibrium Payoffs |
| **Ring 5** | **Phase 2** | **Engineering & Control** | Safety Orange (`#ff6d00`) | Derived from Fluid Dynamics & SDEs | PID Control Functions, Airfoil Lift/Drag Vectors, Stress-Strain Tensor |

---

## 🔗 2. Directed Edges & Energy Flow Animations

The lines connecting the nodes represent Terra's exact **derivation edges** (`parent_formula_id`, `derivation_type`) stored in the database and JSON shards:

- **Edge Visual Styling**:
  - `DERIVED_FROM`: Solid glowing line connecting master parent equation to child law.
  - `SPECIAL_CASE`: Dashed line for specialized regime equations.
  - `LIMIT_CASE`: Dotted line for asymptotic/limiting cases (e.g., Relativistic $\to$ Classical mechanics).
- **Particle Flow Animation**:
  - Subtle glowing pulse dots travel along the edge lines from parent node to child node, visually demonstrating how mathematical energy and principles flow from Physics into Chemistry, Biology, Earth Sciences, and the Phase 2 outer fields.

---

## 🎛️ 3. User Interaction & Expansion Controls

1. **Phase Expansion Toggle**:
   - Situated in the glassmorphic toolbar floating above the landing hero graph:
     `[ 🌐 Phase 1: Core 5 Sciences ]` $\leftrightarrow$ `[ 🌌 Phase 2: Full Universe (10 Fields) ]`
   - Toggling to **Phase 2** triggers a 60 FPS physics expansion where outer nodes bloom from their parent branches with glowing particle animations.
2. **Dynamic Department Filters**:
   - Dynamic department filter chips:
     `[All]` `[Physics]` `[Chemistry]` `[Biology]` `[Earth]` `[Math]` `[Astro]` `[CS]` `[Neuro]` `[Econ]` `[Engineering]`
3. **Ambient Float (Default Hero State)**:
   - Floating physics simulation rendered softly in the background of the hero landing canvas.
   - Glassmorphic universal search input overlays the hero section.
4. **Node Hover State**:
   - Hovering over any node (e.g., **Nernst Equation**) dims unrelated nodes and highlights its exact parent ($E^\circ_{cell}$ & Gibbs Free Energy) and child nodes.
   - Glassmorphic tooltip appears displaying: Title, LaTeX Equation, and Department.
5. **Node Click (Focus & Slide-Over Drawer)**:
   - Clicking a node smoothly zooms the camera onto that concept and opens an omnipresent **Slide-Over Explorer Drawer**:
     - Rendered LaTeX Equation.
     - 1-Sentence Intuitive Physical Summary.
     - Parent & Child Derivation Links.
     - Action Buttons: `[ 🔬 Open in Explainer ]` $\mid$ `[ 📚 Read Subtopic ]` $\mid$ `[ 🧰 Launch Sandbox ]`.

---

## ⚡ 4. Technical Engine Options & Performance Architecture

- **Rendering Engine Options**:
  - **Option A (2D Force-Directed Canvas - D3.js / `force-graph`)**: ~45KB bundle size. Renders via HTML5 2D Canvas. 60 FPS performance, lightweight, mobile touch-friendly.
  - **Option B (3D Constellation - `3d-force-graph` / Three.js)**: Immersive 3D galaxy of science nodes with depth of field and spatial camera rotations.
- **Mobile Graceful Degradation**:
  - On mobile devices or lower-power GPUs, a clean **"Graph / Grid View" toggle** allows switching between the interactive network graph and a responsive 2D card grid.
