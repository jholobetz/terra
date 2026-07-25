# 🔬 Architectural Vision: The Ideal Formula Explainer Experience

**Date**: July 26, 2026  
**Project**: Project Terra (Physics Lab & Multi-Domain Science Encyclopedia)  
**Status**: Vision & Architectural Blueprint  

---

## 1. Executive Summary

The **Formula Explainer** is one of the foundational pillar tools of Project Terra. Its core objective is to demystify complex mathematical equations across Physics (and eventually Chemistry and Biology) by taking any formula, opening it up like a clock, and revealing every variable, operator, physical law, coordinate symmetry, and intuitive physical scenario inside.

This document analyzes the structural limitations of the current static JSON formula storage, outlines a transition toward a **Symbolic Abstract Syntax Tree (AST) & Physics Knowledge Graph (DAG)**, and presents a re-imagined user experience for formula deconstruction.

---

## 2. Structural Limitations & Gaps in Current Architecture

While the current formula database contains over 1,584+ curated shards, a flat list of static JSON files presents fundamental architectural limitations:

### A. The "Flat Key-Value" Gap (Lack of Derivation & Hierarchy)
* **Current State**: Formulas are stored as isolated entries in JSON shards (`shard_01.json`, `shard_02.json`, etc.).
* **Limitation**: Science is not a flat list of independent equations; it is a **derivation graph** (DAG) governed by master laws.
* **Example**: An equation like $\nabla \times \mathbf{E} \to 0$ is not a separate, disconnected equation—it is a **derived child limit node** of Faraday's Law ($\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$) under the static constraint $\frac{\partial \mathbf{B}}{\partial t} \to 0$.

### B. String Matching vs. Symbolic Equivalence
* **Current State**: Lookup relies on string/whitespace normalization against predefined database IDs.
* **Limitation**: Mathematics is defined by **algebraic equivalence**, not string identity.
* **Example**: $E = mc^2$, $m = \frac{E}{c^2}$, $E - mc^2 = 0$, and $\frac{E}{mc^2} = 1$ represent the exact same physical relationship, but string-based lookups treat them as separate keys.

### C. Context-Blind Variable Disambiguation
* **Current State**: Variables resolve against a global dictionary with static domain overrides.
* **Limitation**: Physics symbols are heavily overloaded. $T$ can denote *Temperature* (Kelvin), *Tension* (Newtons), *Period* (seconds), or *Kinetic Energy* ($L = T - V$). Without reading the surrounding prose context, static lookups risk assigning incorrect physical units.

### D. Disconnect Between Prose TeX and Shard Registration
* **Current State**: Subtopic articles contain hundreds of inline/display LaTeX equations in prose, while formula metadata lives in separate JSON files.
* **Limitation**: Clicking an inline equation in prose that lacks a pre-compiled JSON shard results in a "Formula Not Found" or blank `--` placeholder.

### E. Multi-Domain Rigidity (Scaling to Project Terra)
* **Current State**: The schema assumes 5D SI unit vectors $[M, L, T, I, \Theta]$ and physical field classifications.
* **Limitation**: Expanding to **Chemistry** (stoichiometric ratios, reaction kinetics $r = k[A]^a[B]^b$) and **Biology** (Michaelis-Menten kinetics $v = \frac{V_{max}[S]}{K_m + [S]}$, Lotka-Volterra predator-prey models) requires dimensionless rate constants and non-SI variables that don't fit into rigid physical unit vectors.

---

## 3. Proposed Architectural Evolution: Symbolic Knowledge Graph Engine

To achieve complete coverage without requiring manual entry of every possible equation variation, the backend evolves into a 4-layer intelligence engine:

```
[User Inputs / Clicks LaTeX Equation]
                 │
                 ▼
 ┌───────────────────────────────────────────────┐
 │ Layer 1: Symbolic AST & Canonical Engine      │  <-- Parses operators, fields & canonicalizes algebra
 └───────────────────────┬───────────────────────┘
                         │
                         ▼
 ┌───────────────────────────────────────────────┐
 │ Layer 2: Science Knowledge Graph (DAG)        │  <-- Traverses parent laws, limits & equivalent forms
 └───────────────────────┬───────────────────────┘
                         │
                         ▼
 ┌───────────────────────────────────────────────┐
 │ Layer 3: Dynamic Explanation Synthesizer       │  <-- Generates rich conceptual cards if no exact shard
 └───────────────────────┬───────────────────────┘
                         │
                         ▼
 [Rich Interactive Explanation Cards Rendered in UI]
```

### Knowledge Graph Node & Edge Types
* **Master Law Nodes**: Fundamental conservation principles, field equations, and fundamental postulates (e.g. Maxwell's Equations, Schrödinger Equation, First Law of Thermodynamics).
* **Derived Nodes**: Asymptotic limits, static cases, 1D approximations, and boundary conditions.
* **Edges**:
  - `DERIVED_FROM`: Mathematical derivation path.
  - `LIMIT_CASE`: Behavior under asymptotic constraint (e.g., $v \ll c$, $\partial/\partial t \to 0$, $\hbar \to 0$).
  - `EQUIVALENT_FORM`: Differential $\xleftrightarrow{}$ Integral forms via Gauss/Stokes theorems.
  - `SPECIAL_CASE`: Geometry-specific or coordinate-specific reduction.

---

## 4. Re-Imagined User Experience (UI/UX Concepts)

### A. Omnipresent In-Context Slide-Over Drawer
Rather than navigating away from an article to a standalone tool page, clicking any equation in prose smoothly slides out an **In-Context Formula Inspector** drawer. Readers maintain their position in the text while gaining full analytical deconstruction.

### B. Interactive Term & Symbol Highlighting Matrix
* **Term Highlighting**: Hovering over a term ($\nabla \times \mathbf{E}$) highlights that specific chunk in gold and focuses the explanation on *Circulation / Curl of the Electric Field*.
* **Symbol Deconstruction**: Every variable displays its **Physical Name**, **SI/Non-SI Units**, **5D Vector Dimensions**, and **Contextual Override**.

### C. Interactive "Limit Toggles" & Asymptotic Sliders
Users can interactively manipulate equation constraints in real-time:
* **Toggle `Static Limit (∂/∂t → 0)`**:
  The term $-\frac{\partial \mathbf{B}}{\partial t}$ visually fades out / strikes through, and the equation smoothly animates into:
  $$\nabla \times \mathbf{E} = 0$$
  *Card Update*: "In the static limit, the electric field becomes conservative and irrotational, allowing the introduction of an electrostatic scalar potential $V$ ($E = -\nabla V$)."
* **Toggle `Relativistic Limit (v → c)`** or **`Quantum Limit (ℏ → 0)`**: Watch equations dynamically transform between classical, relativistic, and quantum regimes.

---

## 5. Case Study: $\nabla \times \mathbf{E} \to 0, \quad \nabla \times \mathbf{B} \to \mu_0 \mathbf{J}$

### Current vs. Re-Imagined Explainer Output

| Query | Current Static JSON System | Re-Imagined Symbolic Engine |
| :--- | :--- | :--- |
| `?latex=\nabla \times \mathbf{E} \to 0, \quad \nabla \times \mathbf{B} \to \mu_0 \mathbf{J}` | Returns `NULL` $\rightarrow$ Displays blank `--` cards | **1. AST Parsing**: Detects Curl operator ($\nabla \times$), Electric Field ($\mathbf{E}$), Magnetic Field ($\mathbf{B}$), Permeability ($\mu_0$), Current Density ($\mathbf{J}$), and Vanishing Limit ($\to 0$).<br><br>**2. Graph Traversal**: Identifies parent nodes *Faraday's Law* and *Ampère-Maxwell Law* under constraint $\frac{\partial}{\partial t} \to 0$.<br><br>**3. Synthesized Card**: Identifies as *"Static Limits of Maxwell's Equations (Electrostatics & Magnetostatics)"* with full physical interpretation and symbol breakdown. |

---

## 6. Incremental Migration Roadmap

1. **Phase A (Preserve Master Nodes)**: Retain the existing 1,584+ JSON formula shards as initial **Master Nodes** in the graph.
2. **Phase B (Graph Edge Schema)**: Extend formula metadata schema to include `parent_formula_id`, `derivation_type`, and `constraints`.
3. **Phase C (Symbolic TeX AST Parser)**: Integrate an AST parser in `public/src/js/core/tex_parser.js` to extract operators, fields, and limits on the fly.
4. **Phase D (Dynamic Fallback Synthesizer)**: Enable the frontend explainer to dynamically generate structured cards whenever an exact database key is absent.
5. **Phase E (In-Context UI Inspector)**: Deploy the slide-over drawer component across all subtopic view templates.
