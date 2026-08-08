# The Chemistry Lab: Architectural Vision & Next Phase Outline
**Date**: August 5, 2026  
**File**: `docs/chemlab/chemlab_outline.md`  
**Purpose**: High-level architectural outline and feature specification for expanding Terra into "The Chemistry Lab" phase.

---

## 🏛️ Executive Summary

Following the completion of **The Physics Lab**, **The Chemistry Lab** represents the next expansion of Terra. Built upon Terra's core engine—FlightPHP MVC, JSON shards, AST-based LaTeX parsing, MariaDB FULLTEXT search, and DAG Knowledge Graphs—this next phase introduces specialized chemical syntax parsing, thermodynamic equilibrium solvers, electronic structure visualizers, and reaction kinetics engines.

---

## 🧪 1. Core Syntax & Engine Upgrades (The Foundation)

Before building interactive tools, the platform's parser (`public/src/js/core/tex_parser.js` and `detectDomainFromLatex`) will be upgraded to support chemical notation:

1. **Reaction & Phase Syntax**:
   - Support for equilibrium arrows ($\rightleftharpoons$, $\rightarrow$, $\leftrightarrow$).
   - Phase state indicators ($(s), (l), (g), (aq)$).
   - Stoichiometric balance coefficients.
2. **Thermodynamic Anchors**:
   - State functions ($\Delta H^\circ, \Delta S^\circ, \Delta G^\circ$).
   - Reaction quotients ($Q$) and equilibrium constants ($K_{eq}, K_p, K_c, K_a, K_b, K_{sp}$).
   - Rate constants ($k, E_a$) and activity coefficients ($a_i$).
3. **Nuclear & Isotopic Notation**:
   - Isotopic mass number and atomic number super/subscripts ($^{238}_{\ 92}\text{U} \to ^{234}_{\ 90}\text{Th} + \alpha$).
4. **Chemistry Shard Architecture**:
   - Domain-flagged formula JSON shards (`"domain": "chemistry"`) using the hex subdirectory structure (`formulas/00/` through `ff/`).

---

## 🧰 2. Interactive Chemistry Sandboxes ("The Chemistry Lab Tools")

Analogous to Terra's physics sandboxes (*Noether's Vault*, *Legendre Transformer*, *Anthropic Tuner*, *Dimensional Solver*), Chemistry will introduce 6 specialized interactive sandboxes:

### 1. 🔄 The Reaction & Equilibrium Explorer *(Chemical Equation Explainer)*
- **Concept**: The chemical equivalent of the *Equation Explainer*.
- **Features**:
  - Breaks down balanced equations, stoichiometric ratios, reaction quotients ($Q$), and equilibrium constants ($K_{eq}$).
  - **Le Chatelier Slider**: Interactive temperature ($T$), pressure ($P$), and concentration sliders showing real-time equilibrium position shifts.
  - **van 't Hoff Plotter**: Visualizes how $K_{eq}$ scales with temperature based on reaction enthalpy ($\Delta H^\circ$).

### 2. ⚛️ The Quantum Chemistry & Orbital Sandbox
- **Concept**: Bridges quantum mechanics (Schrödinger wavefunctions) with molecular bonding.
- **Features**:
  - **Atomic Orbital Visualizer**: 2D/3D electron density probability clouds for $s, p, d, f$ orbitals.
  - **Molecular Orbital (MO) Diagram Builder**: Interactive energy-level diagrams for homonuclear and heteronuclear diatomics ($\text{O}_2, \text{N}_2, \text{CO}$), calculating bond order ($ \frac{1}{2}(N_b - N_a) $) and magnetic properties (paramagnetic vs. diamagnetic).

### 3. ⚡ The Electrochemical Cell & Nernst Vault
- **Concept**: Interactive galvanic and electrolytic cell simulator.
- **Features**:
  - Visualizes electron flow through wires, salt bridge ion migration, and electrode oxidation/reduction.
  - Real-time **Nernst Equation Solver**:
    $$E_{cell} = E^\circ_{cell} - \frac{RT}{nF} \ln Q$$
  - Dynamic concentration sliders showing cell potential voltage $E_{cell}$ degrading to $0\text{ V}$ as the cell reaches thermodynamic equilibrium ($Q \to K$).

### 4. 📈 The Chemical Kinetics & Rate Law Chamber
- **Concept**: Explores reaction speeds and molecular collision dynamics.
- **Features**:
  - **Integrated Rate Law Simulator**: Toggles between 0th, 1st, and 2nd-order kinetics ($[A]$ vs. $t$, $\ln[A]$ vs. $t$, $1/[A]$ vs. $t$).
  - **Arrhenius Reaction Barrier**: Interactive Maxwell-Boltzmann energy distribution overlay showing the fraction of molecules exceeding activation energy $E_a$ as temperature changes:
    $$k = A e^{-E_a / RT}$$
  - **Enzyme Kinetics**: Michaelis-Menten saturation curves ($v = \frac{V_{max}[S]}{K_m + [S]}$).

### 5. 🌡️ The Thermodynamics & Phase Diagram Studio
- **Concept**: Interactive phase behavior for pure substances and mixtures.
- **Features**:
  - **$P-T$ Phase Diagrams**: Interactive phase boundaries for $\text{H}_2\text{O}, \text{CO}_2$, highlighting triple points and supercritical fluid regimes.
  - **Gibbs Phase Rule Engine**: Evaluates degrees of freedom $F = C - P + 2$.
  - **Clausius-Clapeyron Boundary Slope**: Calculates vapor pressure curves as a function of vaporization enthalpy ($\Delta H_{vap}$).

### 6. 📊 The Interactive Periodic Table & Trend Heatmap
- **Concept**: A dynamic reference grid linked directly to subtopic articles and formulas.
- **Features**:
  - Heatmap overlays for fundamental trends: Electronegativity (Pauling), First Ionization Energy, Atomic Radius, Electron Affinity, and Effective Nuclear Charge ($Z_{eff}$).

---

## 🌐 3. Interdisciplinary Knowledge Graph (Physics $\leftrightarrow$ Chemistry Edges)

Connecting Physics and Chemistry via shared derivation edges:
- **Statistical Mechanics $\rightarrow$ Thermodynamics**: Partition functions ($Z, q$) linking directly to Gibbs Free Energy ($\Delta G = -RT \ln K$).
- **Quantum Mechanics $\rightarrow$ Chemical Bonding**: Atomic wavefunctions ($\psi$) connecting directly to hybridization ($sp^3, sp^2, sp$) and valence bond theory.
- **Electromagnetism $\rightarrow$ Electrochemistry**: Electric field potential ($V$) connecting to cell EMF ($E^\circ_{cell}$) and Faraday's constant ($F$).

---

## 📅 4. Implementation Roadmap

1. **Phase 1**: Syntax extension (`tex_parser.js`) & Chemistry Domain Classifier.
2. **Phase 2**: Periodic Table Heatmap & Chemical Equation Explainer UI.
3. **Phase 3**: Thermodynamic & Nernst Cell Vault.
4. **Phase 4**: Molecular Orbital & Quantum Chemistry Sandbox.
