# Hybrid Context Classifier for Equation Explainer

This document outlines the architecture and design of the **Hybrid Context Classifier**, a programmatic mechanism designed to dynamically disambiguate physical variables and constants based on their equation context.

---

## 1. The Core Challenge: Semantic Overloading

In physical equations, mathematical symbols are heavily overloaded across different subfields:

*   **$\rho$**:
    *   *Statistical/Classical Mechanics*: Phase Space Probability Density
    *   *Fluid Dynamics*: Mass Density
    *   *Electromagnetism*: Charge Density
    *   *Electrical Engineering*: Resistivity
*   **$H$**:
    *   *Hamiltonian Formulation / Quantum Mechanics*: Hamiltonian (Total Energy)
    *   *Thermodynamics*: Enthalpy
    *   *Electromagnetism*: Magnetic Field Intensity
*   **$d$**:
    *   *Calculus*: Total Differential / Infinitesimal Operator (e.g., $dx$, $dt$)
    *   *Kinematics / Gravity*: Distance (e.g., $F = G\frac{m_1 m_2}{d^2}$)

A simple standalone dictionary lookup fails to differentiate these meanings, leading to ambiguous or incorrect variable descriptions in the Component Breakdown.

---

## 2. Proposed Architecture

The **Hybrid Context Classifier** processes equations in three sequential phases:

```
[ LaTeX Input ] 
       │
       ▼
┌─────────────────────────────┐
│ 1. Syntactic Anchor Pass    │ ──► Identifies structural operators (e.g. Poisson Brackets)
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ 2. Co-occurrence Pass       │ ──► Computes similarity scores against known physics domains
└─────────────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│ 3. Domain Filter Pass       │ ──► Restricts dictionary lookups to the winning domain
└─────────────────────────────┘
       │
       ▼
[ Disambiguated Breakdown ]
```

### Phase 1: Syntactic Anchor Detection (Structural Clues)

Certain mathematical notations are exclusive to specific subfields. We scan the raw LaTeX for these "anchors":

*   **Poisson Brackets**: `{ A, B }` or `\{ A, B \}` $\rightarrow$ **Classical Mechanics (Hamiltonian Formulation)**
*   **Bra-ket Notation**: `\langle \psi | \hat{A} | \psi \rangle` $\rightarrow$ **Quantum Mechanics**
*   **Vector Field Operations**: `\nabla \times \mathbf{B}` or `\nabla \cdot \mathbf{E}` $\rightarrow$ **Electromagnetism**
*   **Thermodynamic Relations**: $dU = TdS - PdV$ $\rightarrow$ **Thermodynamics**

### Phase 2: Symbol Co-occurrence Clustering

The system extracts the unique alphanumeric symbols (e.g. $\{\rho, H, t\}$) and calculates a similarity score against pre-mapped symbol profiles for each physics domain:

*   **$\rho$ + $H$ + $\{, \}$** $\rightarrow$ High correlation with **Classical/Statistical Mechanics**
*   **$\rho$ + $H$ + $\vec{B}$** $\rightarrow$ High correlation with **Electromagnetism**
*   **$T$ + $S$ + $P$ + $V$ + $H$** $\rightarrow$ High correlation with **Thermodynamics**

### Phase 3: Domain-Filtered Dictionary Resolution

Once the domain has been determined (e.g. *Classical Mechanics - Hamiltonian*), dictionary lookup for individual tokens is restricted to that domain:

1.  **For $H$**: The lookup resolves to **Hamiltonian** (skipping Enthalpy).
2.  **For $\rho$**: The lookup resolves to **Phase Space Probability Density** (skipping Mass/Charge Density and Resistivity).
3.  **For $d$**: The parser identifies the fraction structure ($d\rho / dt$) and classifies $d$ as a **Total Differential**, removing "Distance" from the breakdown entirely.

---

## 3. Benefits

1.  **Zero-Friction UX**: Eliminates the need for manual dropdowns or user selection; equations are contextualized instantly as they are typed.
2.  **Cleaner UI**: Eliminates multi-definition listings (e.g. "Total Differential / Distance") in the Component Breakdown, presenting a highly clean, professional list of actual physical quantities.
3.  **Generalization**: Works dynamically on completely custom or modified equations typed by the user, not just seeded database entries.
