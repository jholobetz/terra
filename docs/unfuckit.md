# Intellectual Honesty & Structural Rigor: Lineage Graph & UI Reform Plan

If our North Star is **"Describing How It All Connects"** ([`docs/mandate.md`](mandate.md)), then we should choose **intellectual honesty and structural rigor over a gamed 99.3% vanity metric**.

Right now, the lineage system has three specific problems that we can solve cleanly and systematically without breaking the platform. Here is the 4-step plan I recommend:

---

### Step 1: Stop the Bleed — Retire Blind Regex Auto-Parenting
In [`scripts/maintenance/enrich_lineage_families.py`](../scripts/maintenance/enrich_lineage_families.py), any unparented formula is currently matched against broad LaTeX substrings (`\hat`, `\langle`, `\psi`, `\nabla`, `\delta`) and dumped onto one of **8 Core Hubs** (or `stationary-action-principle-8836edf7` as a global catch-all).
- **What we should do**:
  - Remove the global catch-all fallback and broad single-token regex matching (`\hat`, `\langle`, `\phi`) from `enrich_lineage_families.py`.
  - A script should **never** attach a formula to a master equation unless they share subtopic lineage, verified physical variables, or an explicit curated mapping.

---

### Step 2: Fix the Metric — Make the LHI Auditor Honest ([`audit_lineage_health.py`](../scripts/maintenance/audit_lineage_health.py))
Right now, `fixlineage` gives `95 / 100` to any formula attached to a hub, and rewards hubs for having hundreds of children. We should update the LHI scoring rules to enforce a **true hierarchical tree** instead of a star-burst:
1. **Allow Honest Root Nodes (`DEFINITION`, `AXIOMATIC_FOUNDATION`, `EMPIRICAL_LAW`)**:
   - Not every equation is "derived from" another equation in the database. A Bravais lattice vector ($\mathbf{R} = n_1\mathbf{a}_1 + n_2\mathbf{a}_2 + n_3\mathbf{a}_3$) is a **geometric definition**, not a child of the Schrödinger equation. Definitions and axioms should be valid root nodes without forcing a fake `parent_formula_id`.
2. **Penalize "Mega-Hub" Star Packing**:
   - In real physics, a single master equation has **5 to 20 direct 1-hop children**, which in turn branch into their own children (forming a deep multi-level tree). If a single node has $> 25$ direct children, the auditor should flag it as an **Overloaded Star Hub** needing intermediate branching.
3. **Check Subtopic / Variable Affinity**:
   - Flag parent–child links where the child shares zero physical variables with the parent and has no subtopic bridge connecting them.

---

### Step 3: Fix the Schema & UI Conflation ([`public/js/explainer_cards.js`](../public/js/explainer_cards.js))
The Equation Explainer UI currently labels `formula.subcomponents` as **"⬇ Formula Component Sub-equations"**, even though the backend stores **downstream derived equations** in that array.
- **What we should do**:
  1. **Rename the UI section** to **"⬇ Direct Derived & Downstream Equations"** (and badge each card with its relationship: `DERIVED FROM`, `SPECIAL CASE`, `ASYMPTOTIC LIMIT`).
  2. **Deduplicate & Cap the Grid**: Filter out near-duplicate formulas (e.g., identical $\hat{H}|\psi\rangle = E|\psi\rangle$ cards from different subtopics) and display the **top 12 canonical children** by default, with a clean **"Show All (N)"** expand button + search filter so large hubs never flood the page.

---

### Step 4: De-Pack the Mega-Hubs into True Multi-Tier Trees (Starting with TDSE)
Using `time-dependent-schrodinger-equation` as our blueprint, we transform its flat 229-node star burst into a genuine physics hierarchy:
1. **Fix TDSE's Own Upstream Parent**:
   - Remove the inverted parent (`probability-continuity-equation-4c9de9fa`) and set `time-dependent-schrodinger-equation` as an `AXIOMATIC_FOUNDATION` (or derived from the Unitary Time-Evolution / Feynman Path Integral action), moving the Probability Continuity Equation to be its **child**.
2. **Keep Only True 1-Hop Children on TDSE (~12–15 Core Equations)**:
   - *Time-Independent Schrödinger Equation* ($\hat{H}|\psi\rangle = E|\psi\rangle$)
   - *Probability Continuity Equation* ($\partial_t \rho + \nabla \cdot \mathbf{J} = 0$)
   - *Ehrenfest Theorem* ($\frac{d}{dt}\langle \hat{A} \rangle = \frac{1}{i\hbar}\langle [\hat{A},\hat{H}]\rangle + \langle \frac{\partial \hat{A}}{\partial t}\rangle$)
   - *Von Neumann Equation* ($i\hbar \dot{\hat{\rho}} = [\hat{H}, \hat{\rho}]$)
   - *Unitary Time-Evolution Propagator* ($\hat{U}(t,t_0)$)
   - *Heisenberg Equation of Motion*, *TDSE in Position Basis*, *Fermi's Golden Rule*, etc.
3. **Push 2-Hop Children Down & Evict False Positives**:
   - Stationary state solutions (harmonic oscillator, hydrogen atom, WKB, tunneling) become children of the **Time-Independent Schrödinger Equation**.
   - Open-system decoherence and Lindblad master equations become children of the **Von Neumann Equation**.
   - Non-quantum false positives (Bravais lattice vectors, WIMP freeze-out, Artin braid relations, Virasoro algebra) are detached from TDSE and linked to their actual subtopic parents or marked as `DEFINITION` / `AXIOMATIC_FOUNDATION`.

---

### How Should We Proceed?
Before we change any data, I recommend we first run a **quick read-only audit of the current derivation graph** to see:
1. Exactly how many "Mega-Hubs" (like TDSE with 229 children) exist across all 14,687 formulas.
2. What percentage of the 14,687 formulas are hanging off those Mega-Hubs vs. having organic subtopic-level parents.

---

## 🛡️ Part 2: Root-Cause Postmortem & The 5 Anti-Goodhart Safeguards

### Anatomy of the Mistake: Why Did We Fall Into Goodhart's Trap?
1. **An Absolute Law ("Zero Isolated Nodes") Met Messy Reality**:
   - Treating `0 parents and 0 children` as a failure (`Score 0 — Isolated`) forced standalone definitions (e.g. Bravais lattice vectors) and limiting operators to invent fake parent links.
2. **The "One-Way Ratchet" Locked In the Shortcut**:
   - Once `enrich_lineage_families.py` inflated LHI to `99.3 / 100` in `docs/reports/latest.json`, the monotonic ratchet in `scripts/maintenance/run_project_assessment.py` caused `scripts/assess` to fail whenever synthetic edges were removed.
3. **Asymmetric Effort (Bulk Regex vs. Semantic Curation)**:
   - Without shape constraints in the auditor, a 30-line keyword/LaTeX fallback loop satisfied the numeric gate in seconds.
4. **Aggregate Scores Hid Tail Pathologies**:
   - Because 84.6% of the database genuinely had 1–24 children per parent, the `99.3 / 100` average masked the 17 overloaded hubs (2,268 formulas) in the extreme tail.

### The 5 Structural Anti-Goodhart Safeguards (Codified in `CLAUDE.md`, `GEMINI.md`, and `docs/mandate.md`)
1. **Pair Every Completeness Metric with a Structural Shape Constraint**:
   - Never measure coverage alone. Pair coverage with a distribution/shape invariant (e.g., max direct children per formula $\le 25$, plus shared symbol or subtopic affinity).
2. **Strict Ban on Silent Catch-All Fallbacks in Data-Mutating Scripts**:
   - Data-enrichment scripts must never fall back to a default catch-all parent (like `stationary-action-principle-8836edf7`) to hit 100%. Unmatched items must remain `UNMAPPED` or honest roots (`DEFINITION`, `AXIOMATIC_FOUNDATION`, `EMPIRICAL_LAW`).
3. **Separate "Coverage" from "Verified Truth"**:
   - Track `lineage_confidence` (`curated` / `cas_verified` vs. `heuristic`) so scorecards never conflate regex guesses with verified ground truth.
4. **Mandatory Extreme-Tail & Random Spot Check Before Committing Batch Scripts**:
   - Any batch script modifying $> 50$ records must report the top 5 most-affected nodes (e.g. top parents by child count) and 5 random samples before commit.
5. **Honest Baseline Recalibration Over Synthetic Ratchets**:
   - Recalibrate `docs/reports/latest.json` whenever purging synthetic/false edges so monotonic ratchets never block data cleanup.

