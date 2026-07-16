# 🔬 Physics Lab: Equation Explainer Expansion Plan (Overview-Driven)

This document outlines the conceptual roadmap for upgrading the **Equation Explainer** to resolve, define, and explain every formula, identity, and constant featured in the Physics Lab platform, using the `classical-mechanics-overview` subtopic as our primary testbed.

---

## 📐 Overview Page Testbed: Content Analysis

The [classical-mechanics-overview](file:///Users/holobetj/code/gemini/terra/app/config/content/classical-mechanics.json) subtopic features three distinct tiers of mathematical content:

1.  **Full Identities (Primary Cards)**:
    *   Newton's Second Law: $\mathbf{F} = \frac{d\mathbf{p}}{dt}$ (`newtons-second-law-def`)
    *   Simple Harmonic Oscillator: $\ddot{x} + \omega^2 x = 0$ (`classical-mechanics-overview-identity-2-sho-0b0025c1`)
    *   Universal Gravitation: $\mathbf{F}_g = -G \frac{m_1 m_2}{r^2} \hat{\mathbf{r}}$ (`classical-mechanics-overview-identity-3-gravitation-bad723bb`)
2.  **Intermediate Relations (Inline Math)**:
    *   Angular Frequency: $\omega = \sqrt{k/m}$
    *   Rotational Torque: $\boldsymbol{\tau} = \mathbf{r} \times \mathbf{F}$
    *   Rotational Dynamics: $\boldsymbol{\tau} = \frac{d\mathbf{L}}{dt}$
3.  **Fundamental Constants & Variables (Single Symbols)**:
    *   Constants: Gravitational Constant $G$, Spring Stiffness $k$
    *   Variables: Momentum $\mathbf{p}$, Velocity $\mathbf{v}$, Time $t$, Mass $m$, Angular Momentum $\mathbf{L}$, Position Vector $\mathbf{r}$, Acceleration $\mathbf{a}$

---

## 🛠️ The Three-Tier Equation Explainer Resolution

To produce fulsome, context-sensitive explanations for all math elements, the Equation Explainer will support three operational modes:

### Tier 1: Fulsome Full Identities
When explaining a registered compound identity, the Explainer will render a deep three-tier academic breakdown:
*   **Derivation Pathway**: Interactive explanation of the formula's mathematical derivation (e.g., how the SHO equation balances inertia $m\ddot{x}$ against Hooke's restoring force $-kx$).
*   **Symmetry & Physical Origin**: Detailed explanation of the underlying invariants (e.g., time-translation symmetry leading to energy conservation via Noether's theorem; translation/rotation invariance in Newtonian gravity).
*   **Limiting Cases & Boundaries**: An analytical breakdown of parameter limits (e.g., stiffness limit $k \to 0$ reducing to free particle motion; inertial limit $m \to 0$ yielding infinite frequency; boundary conditions for periodic orbits).

### Tier 2: LaTeX Pattern Matching for Inline Relations
When a user clicks "Explain" on an unregistered inline relation (e.g., $\omega = \sqrt{k/m}$ or $\boldsymbol{\tau} = \mathbf{r} \times \mathbf{F}$):
*   The Explainer runs a canonical LaTeX normalization step to strip formatting/braces.
*   It cross-references the normalized LaTeX string against the concept registry.
*   It resolves the query directly to its corresponding concept (e.g., mapping `\omega = \sqrt{k/m}` to the concept of **Natural Frequency/Resonance**, and `\boldsymbol{\tau} = \mathbf{r} \times \mathbf{F}` to **Torque**).

### Tier 3: Symbol Mode (Constants & Variables)
When a single symbol is queried (e.g., `/physics/explain?latex=G` or `/physics/explain?latex=\mathbf{p}`), the Explainer transitions into a dedicated **Symbol View**:
*   **Physical Constants**: If the symbol matches a key constant (like $G$), it queries [constants.json](file:///Users/holobetj/code/gemini/terra/app/config/content/constants.json), displaying its exact numerical value, unit system, and physical role in both classical and general relativistic gravitation.
*   **Disambiguated Variables**: The Explainer accepts the referring subtopic context (e.g. `classical-mechanics-overview`) as an input parameter. If the context is mechanics:
    *   $k$ is resolved to **Spring Stiffness** (in $\text{N/m}$) instead of the thermodynamic Boltzmann Constant.
    *   $T$ is resolved to **Tension Force** (in $\text{N}$) instead of Temperature.
    *   $\mathbf{p}$ is resolved to **Linear Momentum**, explaining its vector nature and its algebraic role as the active generator of spatial translations.

---

## 🔄 Interactive drill-down Navigation

To unite these tiers, the **Equation Component Breakdown** panel is upgraded from a static list to an interactive explorer:
1.  **Drill-Down**: Clicking a component in the variable list (such as the constant $G$ inside the Universal Gravitation equation) transitions the main viewport to explain that constant/variable.
2.  **Trace-Back**: Breadcrumbs (e.g., `Newton's Law of Gravitation › G`) let the user easily return to the parent formula.

---

## 🔍 Inline Relations Evaluation & Concept Mapping Strategy

### 📊 Audit of the Classical Mechanics Shard (`classical-mechanics.json`)
*   **Total Subtopics in Shard**: 62
*   **Total Unique Math Elements**: 925
*   **Single Symbols (Constants/Variables)**: 377
*   **Compound Relations (Equations/Expressions)**: 548 (spanning 599 instances in total)

### 📈 Linking to Parent Concepts
We can leverage our database of 5,279 registered formulas to explain these inline relations with minimal database expansion:

1.  **Canonical Matches (83 Relations)**:
    Out of the 599 compound relations, **83 of them already have a 1-to-1 canonical match** with a registered formula in our database. Normalizing and cross-referencing these LaTeX strings allows the Equation Explainer to instantly load a detailed page:
    *   `Q_j = \sum \mathbf{F}_i \cdot \frac{\partial \mathbf{r}_i}{\partial q_j}` maps to `generalized-force-law-014c3b75` (*Generalized Force Law*).
    *   `\mathbf{F} = m \mathbf{a}` maps to `invariance-of-acceleration-6499bb83` (*Invariance of Acceleration*).
    *   `\frac{df}{dt} = \{f, \mathcal{H}\} + \frac{\partial f}{\partial t}` maps to `canonical-algebra-2545fae5` (*Canonical Algebra*).
    *   `\mu = \frac{m_1 m_2}{m_1 + m_2}` maps to `harmonic-mean-2c2e8b1a` (*Harmonic Mean*).
    *   `S_0 = \int \mathbf{p} \cdot d\mathbf{q}` maps to `abbreviated-action-integral-49049c20` (*The Abbreviated Action*).

2.  **LaTeX Aliases for the Long-Tail (516 Relations)**:
    For unmatched equations that are algebraic or notation variations, we can map multiple LaTeX variants to a single parent formula ID in the [formula_aliases.json](file:///Users/holobetj/code/gemini/terra/app/config/content/formula_aliases.json) registry:
    *   `1/\mu = 1/m_1 + 1/m_2` and `\mu = \frac{m_1 m_2}{m_1 + m_2}` both alias to `harmonic-mean-2c2e8b1a`.
    *   `E = T + V` and `E = T + U` both alias to `conservation-of-mechanical-energy`.

3.  **Decomposition Fallback**:
    If an inline expression doesn't have a direct or aliased match, the Equation Explainer will dynamically decompose it into its known symbols, resolving their meanings contextually.
