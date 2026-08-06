# Project Terra: The Knowledge DAG Web Portal (Landing Page Model 3)
**Date**: August 5, 2026  
**File**: `docs/_terra_knowledge_web.md`  
**Purpose**: Architectural and UX design specification for Model 3—the central interactive landing page rendering Terra's Directed Acyclic Graph (DAG) Knowledge Web.

---

## 🏛️ Executive Concept

Model 3 transforms Project Terra's landing page (`/`) into an interactive, 2D/3D visual network graph that proves Terra's core thesis: **Science is not a collection of isolated subjects, but an interconnected web of first-principles.**

Instead of static cards, visitors encounter a living, breathing constellation of human knowledge where **Mathematics** forms the core, branching into **Physics**, **Chemistry**, **Biological Sciences**, and **Earth & Planetary Sciences**.

```
                      [ 🧬 Biology ]        [ 🌍 Earth Sciences ]
                             \                    /
                              \                  /
                         [ 🧪 Chemical Sciences ]
                                   │
                         [ ⚛️ Physical Sciences ]
                                   │
                        [ 📐 Mathematical Core ]
```

---

## 🎨 1. Visual Topography & Node Clusters

Nodes are organized into concentric, color-coded topological rings based on mathematical dependence and derivation hierarchy:

| Ring Level | Department | Accent Color | Representative Nodes |
| :--- | :--- | :--- | :--- |
| **0. Core Engine** | **Mathematics** | Royal Purple (`#7c4dff`) | Calculus, Differential Equations, Linear Algebra, Vector Calculus, Group Theory |
| **1. Primary Principles** | **Physical Sciences** | Cyber Cyan (`#64ffda`) | Newton's Laws, Maxwell's Equations, Schrödinger Equation, Einstein Field Equations, Hamilton-Jacobi PDE |
| **2. Molecular & Structural** | **Chemical Sciences** | Emerald Green (`#00e676`) | Atomic Orbitals, Gibbs Free Energy, Nernst Equation, Arrhenius Kinetics, van 't Hoff Equilibrium |
| **3. Complex Systems** | **Biological Sciences** | Bio Gold (`#aeea00`) | Hodgkin-Huxley Membrane Equations, Replicator Dynamics, Enzyme Kinetics, DNA Hybridization |
| **3. Earth Dynamics** | **Earth & Planetary** | Azure Blue (`#0288d1`) | Geostrophic Wind Balance, Planetary Energy Balance, Seismic Wave Christoffel Equation |

---

## 🔗 2. Directed Edges & Energy Flow Animations

The lines connecting the nodes represent Terra's exact **derivation edges** (`parent_formula_id`, `derivation_type`) stored in the database and JSON shards:

- **Edge Visual Styling**:
  - `DERIVED_FROM`: Solid glowing line connecting master parent equation to child law.
  - `SPECIAL_CASE`: Dashed line for specialized regime equations.
  - `LIMIT_CASE`: Dotted line for asymptotic/limiting cases (e.g., Relativistic $\to$ Classical mechanics).
- **Particle Flow Animation**:
  - Subtle glowing pulse dots travel along the edge lines from parent node to child node, visually demonstrating how mathematical energy and principles flow from Physics into Chemistry, Biology, and Earth Sciences.

---

## 🖱️ 3. User Interaction & Exploration Flow

1. **Ambient Float (Default Hero State)**:
   - Floating physics simulation rendered softly in the background of the hero landing canvas.
   - Minimalist search bar and department filter toggles (`[All]`, `[Physics]`, `[Chemistry]`, `[Biology]`, `[Earth]`, `[Math]`) hover over the graph.
2. **Node Hover State**:
   - Hovering over a node (e.g., **Nernst Equation**) dims unrelated nodes and highlights its exact parent ($E^\circ_{cell}$ & Gibbs Free Energy) and child nodes.
   - Glassmorphic tooltip appears displaying: Title, LaTeX Equation, and Department.
3. **Node Click (Focus & Slide-Over Drawer)**:
   - Clicking a node smoothly zooms the camera onto that concept and opens an omnipresent **Slide-Over Explorer Drawer**:
     - Rendered LaTeX Equation.
     - 1-Sentence Intuitive Physical Summary.
     - Parent & Child Derivation Links.
     - Action Buttons: `[ 🔬 Open in Explainer ]` $\mid$ `[ 📚 Read Subtopic ]` $\mid$ `[ 🧰 Launch Sandbox ]`.

---

## ⚡ 4. Technical Stack & Performance Architecture

- **Rendering Engines**:
  - **Option A (2D Force-Directed Canvas - D3.js / `force-graph`)**: ~45KB bundle size. Renders via HTML5 2D Canvas. 60 FPS performance, lightweight, mobile touch-friendly.
  - **Option B (3D Constellation - `3d-force-graph` / Three.js)**: Immersive 3D galaxy of science nodes with depth of field and spatial camera rotations.
- **Mobile Graceful Degradation**:
  - On mobile devices or lower-power GPUs, a clean **"Graph / Grid View" toggle** allows switching between the interactive network graph and a responsive 2D card grid.

---

## 💡 Key Architectural Benefits

1. **Leverages Existing Database Schema**: Directly renders Terra's `parent_formula_id` and `derivation_type` database relationships in a visually stunning UI.
2. **Instant "WOW" Factor**: Gives visitors an immediate, memorable visual experience upon arriving at `https://terra.../`.
3. **Natural Multi-Department Discovery**: Users naturally discover how Chemistry, Biology, and Earth Sciences grow out of Physics and Mathematics by following the visual lines.
