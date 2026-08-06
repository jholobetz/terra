# Project Terra: The 5 Core Sciences Architecture & Gateway Vision
**Date**: August 5, 2026  
**File**: `docs/_5_sciences.md`  
**Purpose**: Architectural design document and department specifications for expanding Project Terra from a single-domain application ("The Physics Lab") into a multi-department 5-science engine.

---

## 🏛️ Executive Summary & Central Gateway Concept

As Project Terra expands beyond **The Physics Lab**, the root domain (`/`) will transition into **The Central Science Gateway**. This portal serves as the unified entry point connecting 5 primary faculties of natural and mathematical sciences:

```
                      [ 🌐 PROJECT TERRA ]
                  Central Science Gateway (/)
                               │
   ┌───────────────┬───────────┼───────────┬───────────────┐
   ▼               ▼           ▼           ▼               ▼
[ ⚛️ Physics ]  [ 🧪 Chem ]  [ 🧬 Bio ]  [ 🌍 Earth ]  [ 📐 Math ]
 (/physics)      (/chemistry) (/biology)   (/earth)     (/math)
```

---

## 🎨 Layout & Gateway Architecture Options

### Option 1: "The Grand Academy Gateway" (Recommended)
- **Central Search Bar**: A unified glassmorphic search bar at `/` querying across all 5 departments simultaneously (e.g., searching `"Entropy"` displays results from Physics Thermodynamics, Chemical Equilibrium, and Biological Information Theory).
- **Department Visual Cards**: Dedicated cards for each department with distinct color accents, featured sandboxes, and topic highlights.
- **The Interdisciplinary Bridge**: Dedicated landing page sections highlighting cross-departmental derivation edges (e.g., *Quantum Mechanics $\leftrightarrow$ Chemical Bonding* or *Statistical Physics $\leftrightarrow$ Gibbs Free Energy*).

### Option 2: "The Scientific IDE & Department Switcher"
- **Global Header Bar**:
  - `[ 🌐 Terra Hub ]` $\mid$ Department Switcher Dropdown: `[ ⚛️ Physics ▾ ]` (`Physics`, `Chemistry`, `Biology`, `Earth Sciences`, `Mathematics`).
  - `[ 🧰 Sandbox Directory ]`: Dropdown listing all interactive tools categorized by department.

---

## 🌐 Department Directory & URL Routing

| Department | Route | Accent Theme Color | Focus Areas |
| :--- | :--- | :--- | :--- |
| **Physics** | `/physics` | Cyber Cyan (`#64ffda`) | Classical Mechanics, Quantum Mechanics, Relativity, Field Theory, Thermodynamics |
| **Chemistry** | `/chemistry` | Emerald Green (`#00e676`) | Physical Chemistry, Chemical Kinetics, Electrochemistry, Orbital Theory, Thermodynamics |
| **Biological Sciences** | `/biology` | Bio Gold / Lime (`#aeea00`) | Biophysics, Enzymology, Membrane Potentials, Evolutionary Dynamics, Population Genetics |
| **Earth & Planetary Sciences** | `/earth` | Deep Azure / Earth (`#0288d1`) | Atmospheric Dynamics, Geophysics, Climate Energy Balance, Seismology, Geochemistry |
| **Mathematics** | `/math` | Royal Purple (`#7c4dff`) | Calculus, Linear Algebra, Differential Equations, Group Theory, Differential Geometry |

---

## 🔬 Department Specifications & Interactive Sandboxes

### 1. ⚛️ Department of Physics (`/physics`)
- **Foundational Models**: Einstein Field Equations, Schrödinger Equation, Maxwell's Equations, Hamilton-Jacobi PDE, First Law of Black Hole Mechanics.
- **Interactive Sandboxes**:
  - **Equation Explainer**: Term-by-term breakdown, semantic variables, limit toggles, and Web Audio API sonification.
  - **Noether's Vault**: Symmetries and Noether conservation laws.
  - **Legendre Transformer**: Interactive canonical transformations ($L \to H$).
  - **Anthropic Constant Tuner**: Real-time tuning of fundamental physical constants.

---

### 2. 🧪 Department of Chemistry (`/chemistry`)
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

### 5. 📐 Department of Mathematics (`/math`)
- **Foundational Models**: Fourier Transform, Taylor Series Expansion, Navier-Stokes Existence & Smoothness, Gauss-Bonnet Theorem, Matrix Eigenvalue Decomposition.
- **Interactive Sandboxes**:
  - **📐 Dimensional Solver & Unit Reduction Engine**: Interactive dimensional analysis and unit balance verification.
  - **📈 Fourier Series & Wavelet Synthesizer**: Deconstructs arbitrary periodic functions into harmonic sine/cosine spectrums.
  - **🧩 Vector Calculus & Field Visualizer**: Interactive 2D/3D vector field visualizer showing Gradient, Divergence, and Curl ($ \nabla f, \nabla \cdot \mathbf{F}, \nabla \times \mathbf{F} $).
