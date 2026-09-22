# 🔬 Outside-the-Box Architectural Spec: The Next-Generation Lab Tools UI

> **Document Status**: Authoritative Architecture & UX Design Exploration  
> **Document Reference**: `docs/Lab_Tools_UI_design_ideas.md`  
> **Date**: 2026-09-22  
> **Target Horizon**: Phase 2 Roadmap (2026–2027)  
> **Authoritative References**: [`docs/lab_tool_chest_2026-09-22.md`](lab_tool_chest_2026-09-22.md), [`docs/architecture.md`](architecture.md), [`docs/roadmap.md`](roadmap.md), [`CLAUDE.md`](../CLAUDE.md)

---

## 1. Executive Vision: Moving Beyond the "Link Farm" and the Skeuomorphic Toy

In digital science education and digital reference platforms, computational tools almost universally fall into two inadequate paradigms:
1. **The Inert Encyclopedia** (Wikipedia, MathWorld): Static LaTeX formulas on flat pages, completely detached from live simulation or symbolic algebra.
2. **The Skeuomorphic Toy Sandbox** (PhET, literal breadboard emulators): Sliders and buttons, but mathematically shallow, restricted to grade-school physics, and decoupled from university-level theoretical physics.

Initial conceptual brainstorming examined the **Dr. STEM 100-in-1 Electronic Experiments Lab** ([Amazon reference](https://www.amazon.ca/Dr-STEM-Toys-Electrical-Experiments/dp/B094V9LN5R)). While the literal hardware aesthetic (plastic knobs, jumper wires, and analog VU meters) is too skeuomorphic and nostalgic for a publication-grade digital physics encyclopedia, its **underlying philosophy is profound**:

> **Physics is not a collection of isolated, disconnected subpages; it is a single, interconnected, reactive computational continuum.**

With **14,666 verified formulas, 1,584 graduated platinum articles, a complete derivation DAG with 0 isolated nodes, and a live server-side SymPy CAS engine**, the **Terra Physics Lab** platform has the foundational assets to create something that does not exist anywhere else: **The Dynamic Medium for Theoretical Physics** (inspired by Bret Victor's *Explorable Explanations*, modern nodal compute engines, and high-energy physics control manifolds).

---

## 2. The Three "Outside-the-Box" Paradigms

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              THE "OUTSIDE THE BOX" PARADIGM SPECTRUM                                   │
├──────────────────────────────┬───────────────────────────────┬─────────────────────────────────────────┤
│ PARADIGM 1:                  │ PARADIGM 2:                   │ PARADIGM 3:                             │
│ The Duality & Transformation │ The Reactive Mathematical     │ The Nodal Computational Pipeline        │
│ Chamber                      │ Worldline (Bret Victor)       │ (The Physics Synthesizer)               │
├──────────────────────────────┼───────────────────────────────┼─────────────────────────────────────────┤
│ • Any physics system in center│ • Formulas ARE the controls   │ • Graph canvas connecting theory nodes  │
│ • Symmetries, Legendre, Scale│ • Scrub variables to morph    │ • Wire an Action → Solver → Phase Space │
│   act as "refraction prisms" │   equations & phase space     │   like Unreal Blueprints or Max/MSP     │
│ • Unified morphing interface │ • Unified 3-plane reactive HUD│ • Visual derivation & simulation chain  │
└──────────────────────────────┴───────────────────────────────┴─────────────────────────────────────────┘
```

---

### 🔮 Paradigm 1: The Duality & Transformation Chamber (The Unified Lens)

#### Core Philosophy
In theoretical physics, physical realities do not care about coordinate systems or formalisms. An electron in an electromagnetic field or a planetary geodesic is the exact same underlying geometry whether expressed as:
- A Lagrangian on a tangent bundle $TQ$ spanned by $(q, \dot{q})$
- A Hamiltonian on a symplectic phase space $T^*Q$ spanned by $(q, p)$
- A 4D Minkowski tensor contraction $\partial_\mu F^{\mu\nu} = \mu_0 J^\nu$
- An exterior differential form on a smooth manifold $d{\star}F = \mu_0 J$
- A quantum wave packet $|\psi(x,t)|^2$ subject to the Schrödinger PDE

Instead of housing these as isolated tools on separate URLs ("Noether's Vault", "Legendre Transformer", "Notation Toggle", "Correspondence Workspace"), **they become transformation prisms applied to a single active physical system**.

```
                           ┌───────────────────────────────┐
                           │      ACTIVE PHYSICAL ENTITY   │
                           │    (Loaded from 14,666 DAG    │
                           │   or User Lagrangian/Action)  │
                           └───────────────┬───────────────┘
                                           │
         ┌──────────────────┬──────────────┴─────┬───────────────────┐
         ▼                  ▼                    ▼                   ▼
 🧮 LEGENDRE PRISM    🏛️ NOETHER PRISM     ⚛️ CORRESPONDENCE    📐 CARTAN PRISM
 (Tangent Bundle →    (Symmetry Spacetime   (Classical Ray →    (Gibbs 3-Vectors →
  Phase Space Orbit)   Rotations & Drift)   Quantum Waveform)    Differential Forms)
```

#### User Experience & Interaction
1. **The Central System Crucible**: The user selects or pastes any physical identity (e.g. *Relativistic Particle*, *Double Pendulum*, *Einstein-Maxwell Field*, *Central Force Orbit*).
2. **The Transformation Prisms (Perimeter Ring)**:
   * **The Legendre Prism**: Shifts the active system between Lagrangian and Hamiltonian phase space. It calls our server-side SymPy CAS engine to evaluate the Hessian $W_{ij} = \frac{\partial^2 L}{\partial \dot{q}_i \partial \dot{q}_j}$, verify $\det(W) \neq 0$, algebraically invert velocities, and construct $H(q, p)$.
   * **The Noether Prism**: Applies continuous coordinate variations ($t \to t + \epsilon$, $\mathbf{r} \to \mathbf{r} + \boldsymbol{\epsilon}$). Symmetries illuminate as glowing golden topological rings; broken symmetries visibly bleed out conserved current flux in real time.
   * **The Correspondence Prism**: A continuous dial for $\hbar$ that smoothly morphs a Newtonian deterministic ray into a spreading quantum wave packet and Wigner quasi-probability flow.
   * **The Cartan Prism**: Translates the active equations between Gibbs vector calculus, 4-tensors, and Cartan exterior differential forms with zero page reloads.
   * **The Cosmic Scale Prism**: Zooms through fundamental constants ($c, G, \hbar, \alpha$) from the Planck scale ($10^{-35}\text{ m}$) to cosmological horizons ($10^{26}\text{ m}$).

---

### ⚡ Paradigm 2: The Reactive Mathematical Worldline (The Bret Victor Console)

#### Core Philosophy
Current software forces users to type numbers into text boxes and gaze passively at MathJax equations. In this paradigm, **the mathematical formula itself is the interactive instrument**. The equation is not a dead picture; every variable is a tactile, scrubbable control.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               THE REACTIVE MATHEMATICAL WORLDLINE                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PLANE 1: LIVE SCRUBBABLE MATH      │ PLANE 2: THE PHASE MANIFOLD       │ PLANE 3: ASYMPTOTIC HORIZON  │
├─────────────────────────────────────┼───────────────────────────────────┼──────────────────────────────┤
│                                     │                                   │                              │
│   L = ½ [m] [q̇]² − ½ [k] [q]²       │         p                         │     SymPy CAS Boundary:      │
│         ▲                                     │     ╭───────╮           │                              │
│       drag m = 2.4 kg                         │    │    ●    │          │     lim   Ek = ½ m v²        │
│                                               │     ╰───────╯           │     v→0                      │
│   As you scrub [m], the phase space ──┼───────┼───────────────► q       │                              │
│   ellipse squashes in real time!    │         │                         │     lim   Ek = ∞             │
│                                     │   (Orbit dynamically scales)      │     v→c   (Light Cone Wall)  │
│   Toggle [q̇] → [p] (Legendre)       │                                   │                              │
│   Math flips algebraically into:    │   Vector Field & Wigner Flow      │   Buckingham-π Dimensions:   │
│   H = [p]² / (2[m]) + ½ [k] [q]²    │   illuminated in real time        │   [M] [L]² [T]⁻² (Energy)    │
│                                     │                                   │                              │
└─────────────────────────────────────┴───────────────────────────────────┴──────────────────────────────┘
```

#### Synchronized Three-Plane Architecture
* **Plane 1: The Live Mathematical Medium**:
  * Hovering or dragging on any variable in the rendered LaTeX formula ($m$, $k$, $v$, $c$, $\hbar$) turns the symbol into a high-precision scrub dial.
  * Dragging velocity $v \to c$ triggers an asymptotic boundary indicator: the denominator glows amber, the mass term spikes, and the light cone steepens.
* **Plane 2: The Geometric & Phase Manifold**:
  * An HTML5 Canvas / WebGL vector field that reacts simultaneously to the scrubbed variables. Orbits deform, wave packets squeeze, and phase-space trajectories adjust in lockstep with the algebraic parameters.
* **Plane 3: The Asymptotic & Dimensional Horizon**:
  * Powered by SymPy CAS, this plane computes limits ($\lim_{v \to 0}$, $\lim_{c \to \infty}$, $\lim_{\hbar \to 0}$), Taylor series expansions, and Buckingham-$\pi$ dimensional groups automatically as equations change.

---

### 🔌 Paradigm 3: The Nodal Computational Physics Pipeline (The Physics Synthesizer)

#### Core Philosophy
Inspired by visual shader editors (Unreal Engine Blueprints, Blender Geometry Nodes) and modular audio synthesizers (Eurorack, Max/MSP), but elevated strictly to **pure theoretical physics**.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                               NODAL COMPUTATIONAL PIPELINE (CANVAS)                                    │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                        │
│   ┌──────────────────────┐         ┌─────────────────────────┐         ┌───────────────────────────┐   │
│   │ [NODE: Action / L]   │         │ [NODE: Legendre CAS]    │         │ [NODE: Symplectic Solver] │   │
│   │ L = ½m(ṙ² + r²φ̇²)−V  │ ────►───│ Inverts velocities      │ ────►───│ Computes phase portrait   │   │
│   │ Coordinates: {r, φ}  │ [p_i]   │ Hessian: det(W) ≠ 0     │ [H]     │ & Poincaré section        │   │
│   └──────────────────────┘         └─────────────────────────┘         └───────────────────────────┘   │
│               │                                                                      ▲                 │
│               ▼ [q_i]                                                                │                 │
│   ┌──────────────────────┐                                                           │                 │
│   │ [NODE: Noether Vault]│ ──────────────────────────────────────────────────────────┘                 │
│   │ Detects cyclic φ     │ Conserved Angular Momentum: L_z = m r² φ̇ = const                           │
│   └──────────────────────┘                                                                             │
│                                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

#### How It Works
* The user works on an infinite, zoomable dark-matter canvas.
* Instead of audio signals or textures, the wires carry **mathematical physics structures**:
  * `[Lagrangian Functional L(q, q̇)]`
  * `[Conjugate Momenta p_i]`
  * `[Hamiltonian H(q, p)]`
  * `[Symmetry Group G]`
  * `[Spacetime Metric g_μν]`
* **Plugging a Lagrangian Node into a Legendre Node**: Automatically runs the server-side SymPy CAS script, checks $\det(W)$, and outputs the Hamiltonian.
* **Plugging a Hamiltonian Node into a Symplectic Integrator Node**: Immediately opens a live canvas plotting phase-space orbits and Poincaré recurrence surfaces.
* **Plugging an Action Node into a Noether Node**: Audits the Euler-Lagrange variation, detects cyclic coordinates, and computes the conserved 4-current $J^\mu$.

---

## 4. The Recommended Synthesis: The Unified Physics Cockpit

To achieve immediate usability without requiring users to construct complex graphs from scratch on day one, we recommend a **synthesis of Paradigm 1 (The Duality Chamber) and Paradigm 2 (The Reactive Three-Plane Console)**:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                             THE UNIFIED PHYSICS COCKPIT (/physics/lab-tools)                           │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  SYSTEM CRUCIBLE: [ 🌌 Landmark Presets ▾ ] or [ ✍️ Custom System Input ]                             │
│  Active: Relativistic Harmonic Oscillator in Scalar Potential V(x)                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PRISM SELECTOR TABS:                                                                                  │
│  [ 🧮 Variational & Phase ]  [ 🏛️ Symmetries & Currents ]  [ ⚛️ Ehrenfest Quantum ]  [ 📐 Geometry ]    │
├──────────────────────────────────────┬─────────────────────────────────────────────────────────────────┤
│ LEFT: SCRUBBABLE EQUATION HUD        │ RIGHT: DUAL-TRACE MULTI-MANIFOLD CANVAS                         │
├──────────────────────────────────────┼─────────────────────────────────────────────────────────────────┤
│                                      │                                                                 │
│  L = −[m]c² √(1 − [v]²/c²) − [V]     │  ┌───────────────────────────────────────────────────────────┐  │
│                                      │  │                                                           │  │
│  SymPy CAS Inversion:                │  │  p                                                        │  │
│  p = m v / √(1 − v²/c²)              │  │  ▲        ╭─────────╮                                     │  │
│                                      │  │  │       │     ●     │  (Live RK4 Phase Space Orbit)      │  │
│  Hessian:                            │  │  │        ╰─────────╯                                     │  │
│  det(W) = m c³ / (c² − v²)^(3/2) ≠ 0 │  │  └──────────────────────► q                               │  │
│  Status: REGULAR (NON-SINGULAR)      │  │                                                           │  │
│                                      │  └───────────────────────────────────────────────────────────┘  │
│  Hamiltonian:                        │                                                                 │
│  H = c √(p² + m²c²) + V              │  [ ▶ Pause / Run ]  [ ↺ Reset Phase ]  [ ⤢ Full Workbench ]    │
└──────────────────────────────────────┴─────────────────────────────────────────────────────────────────┘
```

### Core Capabilities of the Cockpit:
1. **Zero-Reload Continuity**: Users remain within a single, unified workspace while analyzing variational mechanics, symmetries, quantum transitions, and differential forms.
2. **Dual-Layer Communication**:
   * Frontend: Responsive MathJax 3.x vector rendering and HTML5 Canvas numerical solvers.
   * Backend: Asynchronous REST calls to `/physics/api/cas-evaluate` backed by [`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py).
3. **Cross-Encyclopedia Launch Hooks**: Every subtopic article in the encyclopedia contains an `[ Open in Lab Tools Cockpit ]` hook that pre-populates the Cockpit with that article's exact Lagrangian or Hamiltonian.

---

## 5. Architectural & Technical Blueprint

### Technology Stack & Component Mapping

| Subsystem | Technology | Responsibility |
| :--- | :--- | :--- |
| **Backend Core** | PHP 8.2+ / FlightPHP | Master routing, API orchestration, and JSON payload handling (`/physics/api/cas-evaluate`). |
| **Symbolic Engine** | Python 3.14 / SymPy | Sandboxed execution in `lib/cas/cas_engine.py`: velocity inversion, Hessian matrices, series expansions, asymptotic limits. |
| **Mathematical Typesetting** | MathJax 3.x Vector Engine | Dynamic typesetting of AST tokens, formula highlighting, and interactive variable scrubbers. |
| **Numerical Solvers** | ES6 / HTML5 Canvas 2D | Real-time RK4 classical integrators, Crank-Nicolson quantum PDE solvers, and Wigner flow visualizers. |
| **State Management** | Modular Vanilla ES6 | Zero-dependency state manager coordinating active physical system, parameters, and active prism view. |

---

## 6. Phased Implementation Roadmap

| Phase | Milestone | Deliverable | Target Timeline |
| :--- | :--- | :--- | :--- |
| **Phase 2.1** | **Prototype Pruning** | Redirect legacy `/physics/genealogy-explorer` $\to$ `/physics/universe-graph` (Completed). | ✅ Done |
| **Phase 2.2** | **SymPy CAS Legendre Engine** | Connect `/physics/legendre-transformer` to `cas_engine.py` for arbitrary Lagrangians & Hessians (Completed). | ✅ Done |
| **Phase 2.3** | **Unified Physics Cockpit UI** | Redesign `/physics/lab-tools` landing page into the Unified Physics Cockpit with live Crucible & Prism Selector. | Next Sprint |
| **Phase 2.4** | **Scrubbable Formula Engine** | Introduce in-situ variable dragging on MathJax expressions linked to canvas manifolds. | Sprint 2 |
| **Phase 2.5** | **Cross-Encyclopedia Ingestion** | Add `[ Open in Cockpit ]` launcher hooks across all 1,584 graduated subtopic encyclopedia articles. | Sprint 3 |

---

## 7. The "Attract & Educate" Strategy: Transforming High Math into Irresistible Visual Wonder

### A. The Inverted Pedagogical Model
To attract broad attention while teaching university-level theoretical physics, we invert the traditional academic model:

> **Traditional Model**: Abstract Axiom $\to$ Greek Math Proof $\to$ Obscure Application. *(Intimidating, sterile, high bounce rate).*  
> **Attract & Educate Model**: **Visceral Spectacle $\to$ Tactile Intuition $\to$ Mathematical Truth.** *(Captivating, accessible, mathematically uncompromising).*

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        THE "ATTRACT & EDUCATE" PEDAGOGICAL FUNNEL                                      │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  LEVEL 1: THE VISUAL HOOK (Instant Dopamine & Aesthetic Awe)                                          │
│  Glowing 60fps Canvas / WebGL: swirling phase portraits, splitting wave packets, orbital chaos.       │
│  "Touch it and something immediately beautiful happens."                                              │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  LEVEL 2: THE TACTILE INTUITION ("What Happens If...?")                                                │
│  Provocative challenge sliders: "What if gravity varied with time?" / "Can a particle jump a wall?"    │
│  Physical cause-and-effect connects directly to the user's fingertips.                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  LEVEL 3: THE MATHEMATICAL REVEAL (Uncompromising Rigor)                                               │
│  Color-coupled MathJax equations + SymPy CAS proofs. Every variable is paired with its visual flow:   │
│  p is emerald, q is cyan, V is amber. The math explains the beauty.                                    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### B. The Hero Stage: "The Cosmic Arena"
When entering [`/physics/lab-tools`](file:///Users/holobetj/code/gemini/terra/app/views/physics/lab_tools.php), the header is anchored by a dynamic, interactive **Cosmic Arena**:
* **Live 60fps Particle & Potential Mesh**: Interactive dark-matter canvas responding in real time to cursor movements, gravitational wells, and quantum potential barriers.
* **Marquee Carousel of "Physics Mysteries"**: Quick-launch buttons that immediately load dramatic, visually stunning physical phenomena:
  1. 🌀 **"The Butterfly of Chaos"**: A double pendulum tracing iridescent fractal attractors in phase space.
  2. 👻 **"The Quantum Ghost"**: A Gaussian wave packet striking an insurmountable energy barrier and visibly splitting into reflected and transmitted probability waves.
  3. 💥 **"Tuning the Universe to Death"**: Cranking the gravitational dial $G$ until planetary orbits collapse and white dwarfs undergo Chandrasekhar supernova.
  4. ⚡ **"The Breaking of Energy"**: A swinging pendulum where time itself is wobbled, watching the energy meter waver and spike out of conservation.

---

### C. Color-Coupled Mathematical Scaffolding
To eliminate the intimidating "monochromatic wall of Greek symbols," formulas and visual elements share an authoritative, synchronized color palette:

* In the equation:
  $$H(q, p) = \frac{p^2}{2m} + V(q)$$
  * Generalized Coordinate $q$: **Bright Cyan (`#38bdf8`)**.
  * Canonical Momentum $p$: **Vibrant Emerald (`#34d399`)**.
  * Potential Field $V$: **Golden Amber (`#fbbf24`)**.
  * Inertial Mass $m$: **Soft Violet (`#c084fc`)**.
* In the accompanying canvas manifold:
  * The particle trajectory trail is **Cyan**.
  * The instantaneous momentum vector is **Emerald**.
  * The potential energy barrier contour is **Amber**.
* **Bidirectional Interaction**: Hovering over $p$ in the MathJax formula pulses the Emerald momentum vector in the simulation; dragging the slider expands the orbit in lockstep.

---

### D. Provocative "What-If?" Micro-Challenges
Instead of passive instructions ("Enter Lagrangian and click solve"), the interface presents playful, curiosity-driven challenges:

* 🎯 **Challenge 1: The Symmetry Thief**:
  * *"Try to break energy conservation without breaking momentum conservation."*
  * User adjusts temporal vs. spatial perturbation sliders. When correctly configured, an achievement badge illuminates: *“Noether's First Theorem Proven!”*
* 🎯 **Challenge 2: The Quantum Escape**:
  * *"Tune Planck's constant $\hbar$ until a classical particle can tunnel through a 5-volt barrier."*
  * As $\hbar$ scales from microscopic to macroscopic, quantum fuzziness visibly envelopes the particle until it bleeds through the potential wall.
* 🎯 **Challenge 3: The Degenerate Matrix**:
  * *"Find a Lagrangian that breaks the Legendre Transformer."*
  * Testing $L = m\dot{x} - V(x)$ triggers a matrix warning: *“Hessian $\det(W) = 0$! You just uncovered a primary Dirac gauge constraint!”*

---

### E. Multi-Sensory Audio-Tactile Synthesis (Web Audio API)
Physics is fundamentally wave mechanics and harmonic resonance. Subtle audio feedback reinforces physical intuition:
* **Quantum Tunneling**: A gentle harmonic chime when probability amplitude crosses a potential barrier.
* **Harmonic Resonance**: A soothing sine tone that modulates in pitch as the user scrubs frequency $\omega$ or mass $m$.
* **Symmetry Breaking**: A low, resonant sub-bass dissonance the moment time symmetry is perturbed, giving immediate auditory intuition to energy non-conservation.

---

### F. Re-Imagining the Headline Instruments
The specialized computational engines are re-titled to emphasize curiosity and engagement without sacrificing mathematical depth:

| Current Tool | New Engaging Identity | The Visual Hook & Play Experience | The Serious Math Payoff |
| :--- | :--- | :--- | :--- |
| **Noether's Vault** | 🏛️ **The Symmetry Playground** | Drag dials to tilt space or wobble time. Watch the energy and momentum needles waver and fail in real time. | Lie group generators ($H = i\hbar\partial_t, \mathbf{p} = -i\hbar\nabla$), stress-energy tensor divergence $\partial_\mu T^{\mu\nu} = 0$. |
| **Correspondence Workspace** | ⚛️ **The Quantum-to-Classical Bridge** | Slide between "Isaac Newton mode" (sharp point particle) and "Erwin Schrödinger mode" (spreading wave packet). | Crank-Nicolson quantum PDE solver, Ehrenfest's theorem $\frac{d\langle p \rangle}{dt} = -\langle \nabla V \rangle$, Wigner flow. |
| **Legendre Transformer** | 🧮 **The Analytical Mechanics Workbench** | Input any mechanical system; watch velocities algebraically invert and phase-space orbits unfold on an oscilloscope. | SymPy CAS algebraic solving, Hessian matrix $W_{ij}$, non-singularity $\det W \neq 0$, Hamilton's equations. |
| **Anthropic Tuner** | 🌌 **The Multiverse Creator** | Turn the dials of $G, c, \hbar, \alpha$. Watch atoms inflate, planetary orbits destabilize, and stars collapse into black holes. | Dimensional scaling, Bohr radius $a_0 = \frac{\hbar^2}{m_e e^2}$, Chandrasekhar gravitational collapse limit. |
| **Notation Toggle** | 📐 **The Rosetta Stone of Physics** | One-click toggle that morphs electric fields between 3D vector arrows, 4D spacetime tensors, and geometric differential forms. | Gibbs vectors vs. relativistic Minkowski tensors $\partial_\mu F^{\mu\nu} = \mu_0 J^\nu$ vs. Cartan forms $dF = 0, d{\star}F = \mu_0 J$. |

