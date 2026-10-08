# 🔬 Architectural Blueprint & Modernization Spec: The Simulations Observatory

> **Document Status**: Archived / Implemented Blueprint  
> **Document Reference**: `archive/sim_fixes.md`  
> **Date**: 2026-09-30 (Archived: 2026-10-07)  
> **Target Horizon**: Interactive Simulations Modernization (`/physics/simulations`)  
> **Related References**: [`archive/Lab_Tools_UI_design_ideas.md`](Lab_Tools_UI_design_ideas.md), [`docs/roadmap.md`](../docs/roadmap.md)

---

## 1. Executive Summary & Diagnostic Assessment

The Physics Lab platform currently possesses **17 specialized simulation engines** defined in `app/config/simulations.json` and implemented across `public/js/simulations/*.js`. These simulations represent an impressive breadth of computational physics—ranging from introductory mechanics to advanced numerical Runge-Kutta 4th-order (RK4) integrators, Monte Carlo quantum probability samplers, and GPU-accelerated general relativistic Kerr null geodesic raytracers.

### Implementation Retrospective (October 2026):
* **Phase 1 (UI Taxonomy & Domain Filters)**: Completed and live on `/physics/simulations`.
* **Phase 2 (Ambient Hero Stage)**: Completed and live on `/physics/simulations`.
* **Phase 3 (Elevation of Pendulum & Projectile Motion)**: Tracked in `docs/roadmap.md` (Phase 2 Roadmap).

---

## 2. Core Architectural Philosophy: The Living Physics Observatory

We elevate `/physics/simulations` from a static card list into **The Living Physics Observatory**:
* **Visceral Engagement Pre-Click**: The observatory should feel computationally alive the moment a user arrives.
* **Instant Tactile Discovery**: Zero-friction client-side filtering by domain and real-time concept search.
* **Clear Conceptual Hierarchy**: Rigorous coupling between phenomenological visual sandboxes and the analytical/symbolic tools in `/physics/lab-tools`.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE LIVING PHYSICS OBSERVATORY (/physics/simulations)                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  HERO STAGE: "Featured Simulation of the Day" (Live 60fps Ambient Viewport)                            │
│  Active: Relativistic Kerr Black Hole Raytracer (GPU null geodesics & Doppler beaming)                │
│  [ Launch Fullscreen ]   [ Explore Next Preset: Double Pendulum Chaos ]                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  ARCHITECTURAL BRIDGE BANNER:                                                                          │
│  "Looking for analytical SymPy CAS derivations or variational mechanics? Launch Lab Tools Cockpit →"   │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  FILTER & SEARCH BAR:                                                                                  │
│  [ 🔍 Search simulations by concept, equation, or keyword... ]                                        │
│  [ All (17) ] [ 🪐 Mechanics (4) ] [ ⚡ EM (2) ] [ 🌌 Relativity (4) ] [ ⚛️ Quantum (3) ] [ 🔥 Thermo (2) ]│
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  OBSERVATORY GRID: DYNAMIC SIMULATION CARDS                                                            │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐  ┌──────────────────────────────┐  │
│  │ 🌌 KERR BLACK HOLE           │  │ ⏳ DOUBLE PENDULUM           │  │ 👻 QUANTUM TUNNELING         │  │
│  │ [ Mini Animated WebGL Canvas]│  │ [ Dynamic Waveform / Trail ] │  │ [ Live Evanescent Barrier ]  │  │
│  │ ds² = -(1 - 2Mr/ρ²)dt² ...   │  │ L = T - V                    │  │ iħ ∂ψ/∂t = Ĥ ψ               │  │
│  │ Tags: [GPU WebGL] [Advanced] │  │ Tags: [RK4 Chaos] [Lyapunov] │  │ Tags: [PDE] [Wave Packet]    │  │
│  │ [ Launch Sandbox → ]         │  │ [ Launch Sandbox → ]         │  │ [ Launch Sandbox → ]         │  │
│  └──────────────────────────────┘  └──────────────────────────────┘  └──────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. High-Impact Modernization Proposals

### A. The Ambient Hero Stage ("Featured Phenomenon")
Anchor the top of `/physics/simulations` with a dynamic, low-overhead live viewport displaying a rotating featured simulation:
* **Default Preset**: The Relativistic Kerr Black Hole or the Chaotic Double Pendulum.
* **Marquee Preset Switcher**: Quick-launch buttons allowing instant switching between highlight phenomena:
  1. 🌌 **The Black Hole Horizon**: Relativistic raytracing and Doppler accretion disk.
  2. 🌀 **The Butterfly of Chaos**: Dual pendulums diverging via Lyapunov exponential separation.
  3. 👻 **The Quantum Ghost**: Gaussian wave packet splitting into reflected and transmitted waves.
  4. 🎲 **Maxwell's Demon**: Real-time sorting of particles and thermodynamic entropy tracking.

### B. Domain Categorization & Filter Pills
Group the 17 simulations into intuitive, responsive category filters:
1. **All (17)**: Complete observatory catalog.
2. **🪐 Classical Mechanics (4)**:
   - `pendulum` — Simple Pendulum
   - `double-pendulum` — Double Pendulum (RK4 Chaos)
   - `projectile-motion` — Projectile Motion with Drag
   - `wave-superposition` — Wave Superposition & Interference
3. **⚡ Electromagnetism (2)**:
   - `electric-field` — Multi-charge Electric Field Visualizer
   - `gauss-law` — Gauss's Law Surface Flux Visualizer
4. **🌌 Relativity & Spacetime (4)**:
   - `spacetime-relativity` — Minkowski Spacetime Diagram
   - `gravitational-lensing` — Schwarzschild Gravitational Lensing
   - `geodesic-tracer` — Boyer-Lindquist Curved Spacetime Geodesic Tracer
   - `relativistic-black-hole` — GPU Relativistic Kerr Black Hole Raytracer
5. **⚛️ Quantum Physics (3)**:
   - `wavefunction-tunneling` — Quantum Tunneling & Schrödinger Well
   - `path-integral` — Feynman Path Integral Sum-Over-Histories
   - `bells-inequality` — Bell's Inequality & CHSH Locality Test
6. **🔥 Thermodynamics & Statistical Mechanics (2)**:
   - `brownian-motion` — Brownian Motion & Diffusion
   - `maxwells-demon` — Maxwell's Demon & Information Entropy
7. **🌊 Nonlinear Dynamics & Celestial (2)**:
   - `vortex-street` — Kármán Vortex Street Fluid Shedding
   - `n-body-orbit` — N-Body Gravitational Dynamics

### C. Rich Scientific Cards
Modernize the card layout with high-density scientific metadata:
1. **Mathematical Scaffolding**: Render the primary governing LaTeX equation on the card face using MathJax.
2. **Computational Engine Tags**:
   - `[ WebGL Shader ]`
   - `[ Numerical RK4 ]`
   - `[ Monte Carlo ]`
   - `[ 2D Canvas ]`
3. **Pedagogical Complexity Badges**:
   - `[ Introductory / Fundamentals ]`
   - `[ Intermediate ]`
   - `[ Advanced / Relativistic ]`
4. **Interactive Hover Sparklines / Micro-Canvas**:
   - Hovering over a card triggers a gentle, ambient motion or trail effect corresponding to that system's behavior.

### D. Instant Real-Time Search & Concept Filtering
A lightweight client-side filter input at the top:
* Searching `"chaos"` filters immediately to *Double Pendulum* and *Vortex Street*.
* Searching `"entropy"` isolates *Maxwell's Demon* and *Brownian Motion*.
* Searching `"quantum"` isolates *Tunneling*, *Path Integral*, and *Bell's Inequality*.
* Searching `"photon"` isolates *Gravitational Lensing*, *Bell's Inequality*, and *Kerr Black Hole*.

### E. Architectural Cross-Bridge: Lab Tools vs. Simulations
Clarify the complementary relationship across the site:
* **The Lab Tools Cockpit (`/physics/lab-tools`)**: The *Analytical Workshop* — variational mechanics, SymPy CAS symbolic proofs, coordinate transformations, and parameter scrubbing.
* **The Simulations Deck (`/physics/simulations`)**: The *Phenomenological Observatory* — 17 dedicated visual playgrounds exploring specific dynamic phenomena from fluid vortices to curved spacetime.
* **Cross-Link Banner**: *"Looking for symbolic derivations, Legendre transforms, or Noether symmetries? Launch the Unified Lab Tools Cockpit →"*

---

## 4. Phased Implementation Roadmap

| Phase | Milestone | Scope & Deliverables | Target Status |
| :--- | :--- | :--- | :--- |
| **Phase 1** | **UI Taxonomy & Metadata** | Group simulations into domain pills (Classical, EM, Relativity, Quantum, Thermo, Fluids). Add real-time client-side search. Enrich card headers with difficulty badges, engine tags, and MathJax governing equations. | ✅ Completed |
| **Phase 2** | **Hero Stage & Visual Energy** | Deploy live ambient canvas at the top of `/physics/simulations` with a preset switcher for top flagship simulations. Add card hover visual effects and the cross-link bridge to `/physics/lab-tools`. | ✅ Completed |
| **Phase 3** | **Sandbox Viewport Polish** | Enhance individual simulation sandboxes (`app/views/physics/simulation_page.php`) with modern glassmorphic controls, synchronized parameter readouts, and links to relevant encyclopedia subtopics. | Backlog |

---

## 5. Individual Simulation Audit: Pruning & Enhancement Matrix

A rigorous assessment of all 17 existing simulations to determine academic rigor, technical execution, redundancy, and upgrade potential.

### A. The 10 High-Value "Crown Jewels" (Spotlight & Preserve)
These models are mathematically rigorous, publication-grade, and visually captivating:

| Simulation Slug | Title & Phenomenon | Mathematical Core | Pedagogical & Technical Value |
| :--- | :--- | :--- | :--- |
| `relativistic-black-hole` | **Relativistic Kerr Black Hole** | $ds^2$, $I_{\text{obs}} = g^4 I_{\text{emit}}$ | Full WebGL GPU null geodesic raytracer with gravitational redshift and relativistic Doppler beaming. |
| `path-integral` | **Feynman Path Integral** | $\Psi = \int \mathcal{D}[x(t)] e^{\frac{i}{\hbar}S}$ | Visualizes quantum sum-over-histories; destructive phase interference yielding the classical path of least action. |
| `bells-inequality` | **Bell's Inequality Locality Test** | CHSH inequality, Tsirelson bound $2\sqrt{2}$ | Recreates the EPR thought experiment with photon polarization angles to experimentally violate local realism. |
| `double-pendulum` | **Double Pendulum Chaos** | Runge-Kutta 4th-order (RK4) | Traces dual pendulums with microscopic initial perturbation $\Delta\theta_0 = 10^{-4}$ rad to demonstrate Lyapunov divergence and the butterfly effect. |
| `geodesic-tracer` | **Curved Spacetime Geodesic Tracer** | Boyer-Lindquist Kerr metric | 1,000+ lines calculating equatorial orbital precession, frame-dragging (Lense-Thirring), and photon spheres. |
| `wavefunction-tunneling` | **Quantum Tunneling & Barrier** | Schrödinger wave packet PDE | Live Gaussian wave packet striking an energy barrier and splitting into transmitted and reflected components. |
| `maxwells-demon` | **Maxwell's Demon & Information** | $S_{\text{gas}} + S_{\text{demon}} \ge 0$ | Real-time sorting of particles and thermodynamic entropy tracking (Landauer's principle). |
| `vortex-street` | **Kármán Vortex Street** | Navier-Stokes Reynolds flow | Unsteady flow separation and alternating vortex shedding under non-linear fluid dynamics. |
| `gravitational-lensing` | **Schwarzschild Gravitational Lensing** | Geodesic deflection $\theta \approx \frac{4GM}{c^2b}$ | Interactive source drag generating dual images, Einstein rings, and relativistic light deflection. |
| `spacetime-relativity` | **Minkowski Spacetime Diagram** | Lorentz transformations | Moving reference frames, light cones, coordinate axis tilting, length contraction, and time dilation. |

---

### B. The 2 Candidates for Academic Elevation (Upgrade Over Deletion)

Two simulations currently present elementary, Physics 101 concepts that do not reflect the university-level depth of the encyclopedia:

#### 1. Simple Pendulum (`pendulum`)
* **Current Limitations**: Single bob swinging in 1D with basic air damping and kinetic/potential energy bars. Lacks depth compared to the Cockpit's Harmonic Oscillator and the simulation catalog's Double Pendulum.
* **Proposed Elevation: The Damped-Driven Nonlinear Pendulum & Chaos Bifurcation**:
  $$\frac{d^2\theta}{dt^2} + \gamma \frac{d\theta}{dt} + \sin\theta = F_0 \cos(\omega t)$$
  - Add an embedded phase-space orbit $(\theta, \dot{\theta})$ and Poincaré recurrence strobe.
  - As the user increases the external driving force $F_0$, the system undergoes period-doubling cascades into deterministic chaos.

#### 2. Projectile Motion (`projectile-motion`)
* **Current Limitations**: Standard 2D flat-ground cannon with air resistance.
* **Proposed Elevation: Newton's Orbital Cannon & Escape Trajectories**:
  - Transition from flat terrain to a spherical gravitating planet.
  - Sub-orbital velocities $\to$ parabolic ballistic arcs.
  - First cosmic velocity $v_0 = \sqrt{GM/R} \approx 7.9\text{ km/s}$ $\to$ circular orbital insertion.
  - Escape velocity $v_{\text{esc}} = \sqrt{2GM/R} \approx 11.2\text{ km/s}$ $\to$ parabolic/hyperbolic solar escape trajectories.
  - Bridges kinematics directly into Keplerian orbital mechanics.

---

### C. Resolution of Conceptual Overlaps

1. **The Black Hole Trio**:
   - `gravitational-lensing`: **Observational Astronomy** (Einstein rings, starfield distortions, double images).
   - `geodesic-tracer`: **Orbital & Geodesic Mechanics** (photon sphere, frame dragging, precession in Boyer-Lindquist coordinates).
   - `relativistic-black-hole`: **First-Person Optical Relativistic Physics** (GPU raytracing, Doppler beaming, accretion disk redshift).
   - *Strategy*: Retain all three; clarify unique perspectives using distinct card tags.

2. **The Electromagnetism Pair**:
   - `electric-field`: **Vector Field Geometry** (dipole fields, vector grids, equipotential lines).
   - `gauss-law`: **Integral Calculus & Flux** (closed surface flux $\oint \mathbf{E} \cdot d\mathbf{A} = Q_{\text{enc}}/\varepsilon_0$).
   - *Strategy*: Retain both as complementary spatial and analytical perspectives.

3. **Thermodynamics & Diffusion**:
   - `brownian-motion`: Rigorously verifies Einstein's diffusion relation $\langle x^2 \rangle = 2Dt$ via Mean Square Displacement (MSD) tracking.
   - `maxwells-demon`: Demonstrates information entropy and Landauer's bound.
   - *Strategy*: Retain both.

---

### D. High-Priority Additions to Fill Theoretical Gaps (Future Horizon)

If expanding the catalog or replacing redundant modules:
1. **2D Ising Model & Ferromagnetic Phase Transition**:
   - 2D spin lattice governed by $H = -J \sum_{\langle i,j \rangle} \sigma_i \sigma_j$.
   - Demonstrates spontaneous symmetry breaking and critical fluctuations near the Curie temperature $T_c$.
2. **Fourier Synthesis & Harmonic Oscillator Modes**:
   - Interactive wave synthesizer building square, triangle, and sawtooth waveforms from discrete Fourier harmonics ($n = 1, 3, 5\dots$).
