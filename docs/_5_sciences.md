# Project Terra: The 5 Core Sciences Department Architecture
**Date**: August 5, 2026  
**File**: `docs/_5_sciences.md`  
**Purpose**: Architectural design document specifying the 5 primary scientific faculties, URL routing, theme accents, foundational models, and interactive sandboxes.

---

## 🏛️ Executive Scope

Project Terra's multidisciplinary engine is structured into **5 Primary Scientific Departments**. Each department operates with its own distinct visual theme, equation catalog, topic abstracts, and specialized interactive sandboxes, while remaining interconnected through shared mathematical derivation edges.

```
                                [ 🌐 PROJECT TERRA ]
                                 Multi-Science Engine
                                          │
   ┌───────────────┬──────────────┼──────────────┬───────────────┐
   ▼               ▼              ▼              ▼               ▼
[ ⚛️ Physics ]  [ 🧪 Chem ]     [ 🧬 Bio ]     [ 🌍 Earth ]     [ 📐 Math ]
 (/physics)      (/chemistry)    (/biology)      (/earth)        (/math)
```

---

## 🌐 Department Directory & URL Routing Hierarchy

| Department | Route | Accent Theme Color | Primary Focus Areas |
| :--- | :--- | :--- | :--- |
| **Physics** | `/physics` | Cyber Cyan (`#64ffda`) | Classical Mechanics, Quantum Mechanics, Relativity, Field Theory, Thermodynamics |
| **Chemistry** | `/chemistry` | Emerald Green (`#00e676`) | Physical Chemistry, Chemical Kinetics, Electrochemistry, Orbital Theory, Thermodynamics |
| **Biological Sciences** | `/biology` | Bio Gold / Lime (`#aeea00`) | Biophysics, Enzymology, Membrane Potentials, Evolutionary Dynamics, Population Genetics |
| **Earth & Planetary Sciences** | `/earth` | Deep Azure / Earth (`#0288d1`) | Atmospheric Dynamics, Geophysics, Climate Energy Balance, Seismology, Geochemistry |
| **Mathematics** | `/math` | Royal Purple (`#7c4dff`) | Calculus, Linear Algebra, Differential Equations, Group Theory, Differential Geometry |

---

## 🔬 Department Specifications & Interactive Sandboxes

### 1. ⚛️ Department of Physical Sciences (`/physics`)
- **Foundational Models**: Einstein Field Equations, Schrödinger Equation, Maxwell's Equations, Hamilton-Jacobi PDE, First Law of Black Hole Mechanics.
- **Interactive Sandboxes**:
  - **Equation Explainer**: Term-by-term breakdown, semantic variables, limit toggles, and Web Audio API sonification.
  - **Noether's Vault**: Symmetries and Noether conservation laws.
  - **Legendre Transformer**: Interactive canonical transformations ($L \to H$).
  - **Anthropic Constant Tuner**: Real-time tuning of fundamental physical constants.

---

### 2. 🧪 Department of Chemical Sciences (`/chemistry`)
- **Foundational Models**: Nernst Equation, Arrhenius Reaction Rate, van 't Hoff Equilibrium Equation, Gibbs Free Energy ($\Delta G = \Delta H - T\Delta S$), Schrödinger Molecular Orbital Theory.
- **Interactive Sandboxes**:
  - **🔄 Reaction & Equilibrium Explorer (Chemical Equation Explainer)**: Term breakdown, stoichiometric balancing, and interactive **Le Chatelier sliders** for temperature, pressure, and concentration.
  - **⚛️ Quantum Chemistry & MO Diagram Builder**: Interactive molecular orbital energy levels for diatomics ($\text{O}_2, \text{N}_2$), calculating bond order and magnetic properties.
  - **⚡ Electrochemical Cell & Nernst Vault**: Real-time galvanic cell voltage simulation degradation as $Q \to K$.
  - **📈 Chemical Kinetics & Rate Law Chamber**: Toggles between 0th, 1st, and 2nd-order kinetics with Arrhenius activation energy barrier distribution plots.
  - **🌡️ Thermodynamics & Phase Diagram Studio**: Interactive $P-T$ phase diagrams ($\text{H}_2\text{O}, \text{CO}_2$), Clausius-Clapeyron slope solver, and Gibbs Phase Rule engine ($F = C - P + 2$).
  - **📊 Interactive Periodic Table & Trend Heatmap**: Dynamic periodic table with heatmaps for Electronegativity, Ionization Energy, Atomic Radius, and $Z_{eff}$.

---

### 3. 🧬 Department of Biological Sciences (`/biology`)
- **Foundational Models**: Hodgkin-Huxley Membrane Equations, Fick's Laws of Diffusion, Michaelis-Menten Enzyme Kinetics, Replicator Differential Equation ($\dot{x}_i = x_i(f_i - \bar{f})$), Hardy-Weinberg Equilibrium.
- **Interactive Sandboxes**:
  - **⚡ Action Potential & Membrane Chamber**: Interactive Hodgkin-Huxley ion channel simulator ($Na^+, K^+$ voltage-gated conductance $m, h, n$).
  - **🧬 Macromolecular Thermodynamics Vault**: DNA hybridization melting curves ($\Delta H, \Delta S$), protein folding free energy landscapes, and ribosome translation kinetics.
  - **📊 Evolutionary Dynamics & Replicator Engine**: Interactive phase portrait solver for Lotka-Volterra predator-prey systems and evolutionary game theory.

---

### 4. 🌍 Department of Earth & Planetary Sciences (`/earth`)
- **Foundational Models**: Geostrophic Wind Balance ($f \mathbf{k} \times \mathbf{v} = -\frac{1}{\rho} \nabla P$), Planetary Radiative Equilibrium ($\frac{S_0(1-\alpha)}{4} = \sigma T_{eff}^4$), Seismic Wave Christoffel Equation, Radiometric Decay ($N(t) = N_0 e^{-\lambda t}$).
- **Interactive Sandboxes**:
  - **🌀 Atmospheric Circulation & Coriolis Chamber**: Interactive rotating-planet simulator showing Rossby waves, Hadley cells, and geostrophic wind vector fields.
  - **☀️ Planetary Radiative Energy Balance Model**: Single-layer and N-layer greenhouse atmosphere model with adjustable albedo ($\alpha$), solar constant ($S_0$), and greenhouse gas opacity.
  - **📉 Seismic Ray Tracer & Earth Core Explorer**: Visualizes seismic wave propagation through the crust, mantle, liquid outer core, and solid inner core (P-wave shadow zones).

---

### 5. 📐 Department of Mathematical Sciences (`/math`)
- **Foundational Models**: Fourier Transform, Taylor Series Expansion, Navier-Stokes Existence & Smoothness, Gauss-Bonnet Theorem, Matrix Eigenvalue Decomposition.
- **Interactive Sandboxes**:
  - **📐 Dimensional Solver & Unit Reduction Engine**: Interactive dimensional analysis and unit balance verification.
  - **📈 Fourier Series & Wavelet Synthesizer**: Deconstructs arbitrary periodic functions into harmonic sine/cosine spectrums.
  - **🧩 Vector Calculus & Field Visualizer**: Interactive 2D/3D vector field visualizer showing Gradient, Divergence, and Curl ($ \nabla f, \nabla \cdot \mathbf{F}, \nabla \times \mathbf{F} $).

---

## 🌐 Interdisciplinary Knowledge Graph (Derivation Edges)

Connecting the 5 departments via shared mathematical derivation edges:
- **Statistical Mechanics (Physics) $\rightarrow$ Thermodynamics (Chemistry)**: Partition functions ($Z, q$) linking directly to Gibbs Free Energy ($\Delta G = -RT \ln K$).
- **Quantum Mechanics (Physics) $\rightarrow$ Chemical Bonding (Chemistry)**: Atomic wavefunctions ($\psi$) connecting directly to hybridization ($sp^3, sp^2, sp$) and valence bond theory.
- **Electromagnetism (Physics) $\rightarrow$ Electrochemistry (Chemistry) $\rightarrow$ Biophysics (Biology)**: Electric potential ($V$) connecting to cell EMF ($E^\circ_{cell}$) and nerve action potentials (Hodgkin-Huxley).
- **Fluid Dynamics (Physics) $\rightarrow$ Atmospheric Dynamics (Earth)**: Navier-Stokes equations connecting directly to planetary Coriolis forces and Geostrophic balance.
