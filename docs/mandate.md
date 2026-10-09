# 🌌 Terra Physics Lab — The Foundational Mandate

> **Status**: Active North Star & Foundational Mandate  
> **Core Purpose**: Describing How It All Connects  
> **Companion Documents**: [`docs/ideas.md`](ideas.md) (Brainstorming Incubator), [`docs/roadmap.md`](roadmap.md) (Engineering Execution), [`CLAUDE.md`](../CLAUDE.md) (Operational Authority)

---

## 1. Executive Vision: The Atlas of Physical Reality

Physics education and literature suffer from a profound and tragic fragmentation. Students, engineers, and researchers are taught physics in isolated silos:
* **Classical Mechanics** is taught as blocks, pulleys, and pendulums.
* **Electromagnetism** is taught as vector calculus around charges and wires.
* **Thermodynamics** is taught as heat engines, steam cycles, and pressure-volume curves.
* **Quantum Mechanics** is taught as wavefunctions and operators in potential wells.
* **Relativity** is taught as moving clocks and curved coordinate grids.

Learners finish their education with separate mental binders, **never realizing that it is all one continuous, breathtaking tapestry**:
* The classical Principle of Stationary Action is the macroscopic stationary-phase limit of Feynman’s quantum path integral as $\hbar \to 0$.
* The temperature of a gas and the event horizon of a black hole are governed by the exact same statistical definition of entropy ($S = k_B \ln \Omega$).
* Conservation of energy, linear momentum, angular momentum, and electric charge are not disconnected empirical rules, but direct mathematical consequences of continuous spacetime and gauge symmetries (Noether's Theorem).
* Maxwell's equations and Einstein's special relativity are the exact same geometric object viewed from different coordinate frames.

**The Foundational Mandate of Project Terra is to build the digital atlas that describes, in every sense, how it all connects.**

---

## 2. The Four Pillars of Connectivity

Every line of code, formula definition, interactive simulation, and technical document in this repository exists to serve one or more of these four pillars:

```
                          ┌───────────────────────────┐
                          │   SYMMETRY & AXIOMS       │
                          │ (Noether, Action, Metric) │
                          └─────────────┬─────────────┘
                                        │
                         "Derived By"   │   "Limits As c -> ∞, ħ -> 0"
                                        ▼
                          ┌───────────────────────────┐
                          │  THE DERIVATION LATTICE   │
                          │ (14,600+ Linked Formulas) │
                          └─────────────┬─────────────┘
                                        │
                        "Topological"   │   "Cross-Domain Bridges"
                                        ▼
    ┌───────────────────────────┬───────────────────────────┐
    │   PHENOMENOLOGY & PROSE   │   INTERACTIVE DYNAMICS    │
    │   How it explains reality │   Sliders & Real-time GPU │
    └───────────────────────────┴───────────────────────────┘
```

### Pillar 1: The Derivation Lattice (The Spine)
* **What it is**: The 14,600+ formula Directed Acyclic Graph (DAG) connected by 44,000+ directed derivation edges.
* **The Connection**: No formula exists as an isolated island. Every phenomenological identity must trace its mathematical ancestry back to foundational action principles, symmetries, and master equations.
* **Verification Gate**: The Lineage Health Index (LHI $\ge 95/100$) and SymPy Computer Algebra System (CAS) derivation edge provers.

### Pillar 2: Topological Cross-Domain Bridges (The Revelations)
* **What it is**: Explicit structural links connecting disparate physics domains.
* **The Connection**: The most transformative moments in physics occur when a concept in one domain unlocks an entirely different domain (e.g., how thermodynamic entropy connects to Shannon information theory, which connects to Bekenstein-Hawking black hole thermodynamics).
* **Verification Gate**: Every subtopic node must maintain cross-hub topological bridges linking across distinct pillar categories.

### Pillar 3: Symmetry Origins & Asymptotic Boundaries (The Roots)
* **What it is**: Explicit documentation and symbolic verification of coordinate invariants and limiting regimes.
* **The Connection**: Physical laws are defined by their symmetries (Lorentz invariance, gauge invariance, diffeomorphism invariance) and their asymptotic boundaries (classical limits as $\hbar \to 0$, non-relativistic limits as $v/c \to 0$, thermodynamic limits as $N \to \infty$).
* **Verification Gate**: Symbolic CAS asymptotic limit solvers and unit/dimensional homogeneity certificates.

### Pillar 4: Sensory Grounding & Interactive Proof (The Living Lab)
* **What it is**: GPU WebGL raytracers, RK4 phase space integrators, and parameter-reactive workbenches.
* **The Connection**: Abstract mathematics becomes physical intuition when a user can perturb a parameter and watch the physical universe react in real time at 60 frames per second.
* **Verification Gate**: Zero-dependency WebGL2 null-geodesic raymarchers, analytical mechanics Legendre transformers, and real-time phase portraits.

---

## 3. Product Definition & Non-Goals

To maintain focus and avoid the capability trap, we establish strict definitions of what Project Terra is and what it is not:

| What Project Terra IS | What Project Terra IS NOT |
| :--- | :--- |
| **An Interactive Computational Physics Manifold** | **A Passive Text Dump** (Not another Wikipedia clone) |
| **An Axiom-to-Phenomenon Derivation Tree** | **A Query-Only Calculator** (Not a closed Wolfram Alpha clone) |
| **A Graduate-Level Research & Learning Lab** | **A Collection of K-12 Toy Applets** (Not another PhET clone) |
| **An Open, Self-Hosted, Offline-Capable Engine** | **A Gamified Quiz / Flashcard SaaS** (Not a Brilliant clone) |
| **A Cryptographically & CAS-Verified Ground Truth** | **An Unchecked Hallucination Surface** |

---

## 4. The Decision Filter

Whenever a feature, phase, script, or refactor is proposed:

> **The Sovereign Question**:  
> *"Does this feature make the connection between physical principles clearer, more rigorous, or more breathtaking to explore?"*

* If the answer is **YES**, it is evaluated, prioritized, and graduated to [`docs/roadmap.md`](roadmap.md).
* If the answer is **NO** (e.g., cosmetic complexity, disconnected games, or administrative bloat), it is respectfully rejected.

---

## 5. Document Ecosystem Triad

1. **[`docs/mandate.md`](mandate.md)** *(This Document)*: The North Star, product identity, and philosophical compass.
2. **[`docs/ideas.md`](ideas.md)**: The creative sandbox for spitballing ideas, "what-if" simulations, and exploratory proposals without rules or rigidity.
3. **[`docs/roadmap.md`](roadmap.md)**: The concrete, phased engineering execution plan with scheduled sprints, benchmarks, and regression gates.
