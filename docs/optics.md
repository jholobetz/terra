# 🔭 Audience, Positioning & Academic Optics

> **Purpose**: A standing reference for how **Physics Lab (`https://physicslab.ca`)** is perceived by physics professors, graduate students, and technical peers — what earns credibility, where skepticism arises, and how we should frame and evolve the platform.  
> **Created**: 2026-11-25  
> **Platform North Star**: *"Describing How It All Connects"* ([`docs/mandate.md`](mandate.md))

---

## 🎯 Core Verdict

Physics Lab is **mature enough to present to physics professors and graduate students — provided it is framed honestly**. Most physicists will **not** dismiss it as generic "AI slop" because it ships real computational, mathematical, and verification infrastructure that LLM-wrapper sites never build. However, a sharp specialist *will* recognize AI-assisted prose cadence and spot where graduate-level depth is still thin.

---

## ✅ What Earns Academic Credibility (Why It Is *Not* AI Slop)

1. **Zero Hallucinated Citations**:
   * `1,514 / 1,514` (`100%`) live-verified DOIs (audited against OpenAlex, Crossref, and `doi.org`) and audited external URLs.
   * Hallucinated references are the fastest trigger for an academic to close a tab — clearing this bar completely separates Physics Lab from unverified AI sites.
2. **Real Mathematical & Computational Engines**:
   * **Legendre Transformer** (`/physics/legendre-transformer`): Live **SymPy CAS** backend computing velocity Hessians $W_{ij}$, detecting singular constraints, and deriving Hamiltonians dynamically.
   * **Kerr Black Hole Raytracer** (`/physics/simulations/relativistic-black-hole`): Real WebGL2 null-geodesic integration in Boyer-Lindquist coordinates ($a \le 0.998$) with Doppler beaming ($g^4$) and gravitational redshift.
   * **Derivation Lineage DAG** (`/physics/universe-graph`): `15,583` canonical formulas and `14,119` derivation edges connecting axioms to phenomenological laws across 12 domains.
   * **Equation Explainer** (`/physics/equation-explainer`): Structural dissection of LaTeX expressions into variables, dimensions, and physical roles.
3. **Deterministic Ground-Truth Guardrails**:
   * **NIST CODATA 2022** (`24` fundamental constants, single-source-of-truth across `/physics/constants` and `/physics/symbols`).
   * **PDG 2024** (`20` Standard Model + composite hadron properties).
   * **`10,135+` SymPy CAS dimensional-homogeneity checks** and automated pre-commit / pre-push Integrity Shield verification (`0` broken links, `0` semantic warnings).

---

## ⚠️ Where Professors & Graduate Students Will Push Back

1. **Recognizable AI Prose Cadence**:
   * Reading 3–4 subtopics back-to-back reveals a uniform rhythm and density (`~650–1,000` words, 5–7 dense paragraphs, similar rhetorical arcs). Even when the physics is accurate, experienced academics sense AI-assisted authoring.
2. **Conceptual Synthesis vs. Textbook Rigor**:
   * At `~800` words per subtopic, articles function as **high-density conceptual maps and quick-references**, not substitutes for Sakurai, Jackson, Peskin & Schroeder, or Landau–Lifshitz.
   * Domain specialists will notice:
     * Only `104 / 15,583` (`~0.7%`) of formulas currently have step-by-step multi-step derivations.
     * Occasional unstated **conventions** across linked articles (metric signature $(-,+,+,+)$ vs $(+,-,-,-)$, Fourier $2\pi$ conventions, Gaussian vs SI electrodynamics).
     * Compressed edge-case caveats (regularization schemes, boundary conditions, domains of validity).
3. **Pedagogical Sandboxes vs. Research Instruments**:
   * Workbenches such as **Anthropic Tuner**, **Noether's Vault**, and **Correspondence Workspace** are strong undergraduate-to-early-graduate **pedagogical visualizations**, not research tools. Over-claiming them invites skepticism; presenting them as interactive pedagogy lands well.
4. **Click-Through Polish**:
   * Always run a quick manual click-through of any demo path before presenting; unclicked secondary routes can occasionally hide UI or anchor-link edge cases.

---

## 🧭 Positioning & Presentation Playbook

### How to Frame the Platform
* **Describe it accurately**: An **interactive physics knowledge graph, conceptual synthesis engine, and computational teaching lab** (*"Describing How It All Connects"*), not a peer-reviewed textbook replacement.
* **Be transparent about the workflow**: State openly that it is **AI-co-authored with deterministic verification guardrails** (SymPy CAS, live DOI verification, CODATA 2022 / PDG 2024 audits). Transparency disarms the "AI slop" reflex immediately.
* **Invite domain red-teaming**: Ask specialists: *"Look up your subfield and tell me where sign conventions, caveats, or derivations fall short."* Academics respect intellectual honesty and enjoy critiquing rigor — their feedback directly informs future depth upgrades.

### Strongest 3-Minute Demo Path
1. **`/physics/legendre-transformer`** — Live SymPy CAS velocity Hessian, singular constraint detection, and Hamiltonian derivation.
2. **`/physics/simulations/relativistic-black-hole`** — 60fps WebGL2 Kerr black hole null-geodesic raytracer.
3. **`/physics/universe-graph`** — Shortest-path Derivation Route Finder across `15,583` formulas.
4. **`/physics/topic/standard-model`** *(Orbital Menu)* → any flagship subtopic → **`/physics/equation-explainer`**.
