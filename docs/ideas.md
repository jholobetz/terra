# 💡 Terra Physics Lab — The Idea Incubator & Concept Sandbox

> **Status**: Active Idea Incubator & Concept Sandbox (Non-binding)  
> **Purpose**: A frictionless scratchpad for spitballing ideas, "what-if" features, visual concepts, and future explorations without the constraints of formal rules, grading, or test suites.  
> **Companion Documents**: [`docs/mandate.md`](mandate.md) (The North Star), [`docs/roadmap.md`](roadmap.md) (Phased Engineering Schedule)

---

## 🧭 About This Sandbox

This document is intentionally informal. There are no formatting rubrics, word count gates, or OPS requirements here. Anyone contributing to Project Terra can jot down ideas, propose wild simulations, question existing assumptions, or sketch future architectures.

When an idea matures and aligns with our North Star in [`docs/mandate.md`](mandate.md) (*"Describing How It All Connects"*), it can be formally scoped and graduated to [`docs/roadmap.md`](roadmap.md).

---

## 🔮 1. "What If" Visualizations & Simulations

Crazy or ambitious simulation ideas to make the abstract visible:

* **Kerr-Newman Ergosphere & Penrose Process Visualizer**:
  * An interactive WebGL workbench where users can fire a particle into a rotating, charged black hole's ergosphere, split it into two, and extract net rotational energy ($E_{\text{out}} > E_{\text{in}}$).
* **Quantum Zeno Effect Simulator**:
  * An interactive Bloch sphere or wavepacket where clicking rapidly "observes" the system, freezing its unitary time evolution in real time.
* **General Relativistic Gravitational Lensing Sandbox**:
  * Move a point mass, binary system, or gravitational wave ripple in front of a background starfield or galaxy grid to see caustic curves, Einstein rings, and micro-lensing light curves.
* **Relativistic Doppler & Beaming Audio Synthesizer**:
  * Connect the Web Audio synthesizer in the cosmic arena to relativistic motion ($v \to c$) so users *hear* the pitch shift and amplitude amplification as an emitter approaches at $0.99c$.
* **Feynman Path Integral Wave Demonstrator**:
  * Show thousands of classical paths interfering constructively near the classical stationary action path ($\delta S = 0$) and destructively elsewhere.

---

## 🗺️ 2. UX, Navigation & "How It All Connects" Explorations

Ideas to make exploring the 14,600+ formula knowledge graph feel like flying through a galaxy:

* **3D Galaxy Derivation Explorer**:
  * A Three.js / WebGL force-directed 3D cosmological map where foundational axioms are massive central galactic cores, and derived formulas form spiral arms branching outwards.
* **The "Derivation Journey" Breadcrumb**:
  * When a user navigates between equations, show an interactive lineage breadcrumb trail (*Principle of Least Action &rarr; Euler-Lagrange &rarr; Geodesic Equation &rarr; Schwarzschild Metric*).
* **"Surprise Me With a Bridge" Button**:
  * A serendipity button that takes the user on a 3-hop journey between two completely unrelated fields (e.g., from *Thermodynamic Heat Engines* to *Hawking Radiation* or *Semiconductor Bandgaps*).
* **Interactive Proof Comparison Sliders**:
  * Split-screen view comparing a classical Newtonian derivation side-by-side with its Einsteinian relativistic counterpart to highlight exactly where $1/\sqrt{1 - v^2/c^2}$ enters the algebra.

---

## 🧮 3. Symbolic CAS & Computational Experiments

Ideas for expanding the mathematical backbone:

* **Automated "Missing Link" Detector**:
  * Train a graph embedding or heuristic scanner on the Lineage DAG to find equations that *should* be connected by a mathematical limit or substitution but currently lack an edge.
* **Inverse Symbol & Dimension Solver**:
  * Let a user paste an arbitrary physical equation; the CAS automatically solves for the unknown variable's SI and natural dimensions and suggests which physical quantity it represents.
* **Multi-Parameter Taylor Expansion Slider**:
  * A slider that interactively sweeps the truncation order $N$ of a series expansion (e.g. $N=1, 2, 3, 5, 10$) so students visually witness the exact radius of convergence.

---

## 🎓 4. Pedagogical & Narrative Experiments

Ideas for enhancing the narrative and human element:

* **Historical Clashes & Paradox Workbenches**:
  * Interactive modules dissecting famous physics paradoxes (Twin Paradox, Gibbs Paradox, Ehrenfest Paradox, Klein Paradox) and showing how the math resolves them.
* **Interactive Dimensional Analysis Scratchpad (Buckingham $\Pi$ Theorem)**:
  * A tool where users input the variables involved in a physical problem (e.g., fluid drag: $\rho, v, D, \mu$) and the engine automatically derives the dimensionless groups (Reynolds number).

---

## 📝 5. Spitballing Scratchpad & Rough Notes

*Add quick bullet points, raw links, or fleeting thoughts here:*

* *(Date: 2026-10-08)* — Could we add an export button on formula cards that generates ready-to-run Python/SymPy or Jupyter notebook snippets for that exact formula?
* *(Date: 2026-10-08)* — Think about mobile UX for the equation dissector: can we have a horizontal bottom sheet for variable definitions so the equation stays sticky at the top?
* *(Date: 2026-10-09)* — **Production Deployment & Server Footprint Architecture**:
  * **DocumentRoot Isolation**: Web server (Nginx/Apache) root strictly points to `/public`. The public web only directly accesses CSS, JS, compiled MathJax SVG/assets, and pre-rendered static HTML cache (`public/cache/subtopic/*.html`).
  * **Production Artifact Pruning**: In deployment packages (Docker container or server release tarball), exclude dev-only assets (`/tests`, `/docs`, `.git`, dev scratch files) while retaining `/public`, `/app`, `/vendor`, and `/lib` (SymPy CAS engine).
  * **Performance Profile**: Subtopic and topic reading requests are served directly from the static disk cache at static-site speeds (<10ms) without hitting MariaDB. Dynamic features (`/physics/api/cas-evaluate`, search, equation explainer) invoke PHP and Python on demand.
  * **Single-Developer Model vs. Future Tiers**: Keep local development flattened (direct write to Git shards + MariaDB sync). When public community contributions are eventually needed in production, design a lightweight public submission/review tier specifically tailored for production rollout.
