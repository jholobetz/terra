# 🌌 Fusion Architecture: Auto-Draft & Lineage Discovery Engine

This document outlines the architectural design, workflow integration, and implementation plan for **merging the Auto-Draft generation pipeline with the Formula Lineage Discovery Engine (`fixlineage`)** in Project Terra.

---

## 🧭 1. Executive Summary & Problem Definition

In Project Terra, mathematical identities have two distinct requirements:
1. **Intra-Formula Semantic Definition**: Academic title, LaTeX equation, prose explanations (`conceptual_definition`, `interpretation`, `symmetry_origin`, `limits_and_boundary`), and SI semantic variables.
2. **Inter-Formula Topological Lineage**: Upstream axiomatic parent (`parent_formula_id`), derivation relation (`derivation_type`), downstream children (`subcomponents`), and Lineage Health Index (**LHI: 0–100**).

### The Inherent Disconnect
Previously, these two systems operated in isolation:
* Running `fixlineage` on an unindexed or raw LaTeX equation **failed or returned no-ops** because the formula had no definition, no domain context, and no entry in the shards or database.
* Running `Auto-Draft` (via `generate_gemini_formula.py` or the in-browser Curator Drawer) synthesized prose definitions but frequently left the lineage fields empty (`parent_formula_id: ""`, `subcomponents: []`), resulting in newly minted **topological orphans** (LHI < 50).

### The Core Insight
> **Lineage requires a definition, and definitions require immediate lineage placement.**  
> When a new formula is drafted from a raw LaTeX string or AST, that is the single best moment to discover its parent law, attach its boundary specializations, verify its LHI score (≥ 80), and compile it into the global 23,000+ edge derivation graph.

---

## 🏛️ 2. Architectural Flow & Data Pipeline

```
                     ┌─────────────────────────────────────────┐
                     │ Raw / Unindexed LaTeX Equation or AST   │
                     │  (e.g., \nabla^2 G = -\delta^3(r - r")) │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │  STAGE 1: Auto-Draft Generation Engine  │
                     │  (generate_gemini_formula.py / Gemini)  │
                     │  • Synthesize Academic Title            │
                     │  • Generate Rigorous LaTeX Prose Fields │
                     │  • Extract SI Semantic Variables        │
                     │  • Identify Physical Discipline Domain  │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │  STAGE 2: Lineage Discovery & Scoring   │
                     │  (audit_lineage_health.py / Subsystem)  │
                     │  • Query 13,780-node Derivation Graph   │
                     │  • Resolve Optimal Axiomatic Parent     │
                     │  • Attach Candidate Subcomponents       │
                     │  • Assert LHI Score Target (LHI ≥ 80)   │
                     └────────────────────┬────────────────────┘
                                          │
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │  STAGE 3: Unified Persistence & Sync    │
                     │  • Save to Canonical Shard (shard_xx)   │
                     │  • Update MariaDB (equation_svg = NULL) │
                     │  • Sync formulas_latex_index.json       │
                     │  • Rebuild formula_derivation_graph.gz  │
                     └─────────────────────────────────────────┘
```

---

## 🧬 3. Component Details & Enhancements

### A. Stage 1: Context-Aware Auto-Drafting (`generate_gemini_formula.py`)
* The Auto-Draft prompt is supplied with a curated catalog of primary master parent laws (e.g. *Poisson"s Equation*, *Schrödinger Equation*, *Maxwell-Ampère Law*, *Euler-Lagrange Equation*, *Einstein Field Equations*, *Continuity Equation*).
* Prompts enforce that `parent_formula_id` must match a real existing formula slug whenever applicable.

### B. Stage 2: Automated Lineage Discovery Hook
* Immediately after Stage 1 generates the provisional formula object in memory:
  1. If `parent_formula_id` is blank or invalid, the engine runs vector/keyword proximity matching against known formula titles and equation patterns.
  2. The system retrieves downstream candidate formulas (formulas referencing the new formula or operating as special cases/boundary limits).
  3. The `audit_lineage_health.py` diagnostic calculates the prospective **LHI Score** (Upstream: 35 pts, Downstream: 35 pts, Depth: 15 pts, Quality: 15 pts).
  4. If LHI < 70, the resolver auto-attaches adjacent domain identities to satisfy derivation tree completeness.

### C. Stage 3: Instant Persistence & Graph Recompilation
* Once approved, the new node is committed:
  1. Shard written to `app/config/content/formulas/[xx]/shard_[xx].json`.
  2. MariaDB record inserted with `equation_svg = NULL` to enable instantaneous client-side MathJax rendering.
  3. `formulas_latex_index.json` indexed with normalized LaTeX key.
  4. `scripts/build_formula_graph.py` triggered to compile `app/config/formula_derivation_graph.json` and its compressed `.gz` asset.

---

## 💻 4. CLI & Interface Upgrades

### 1. Enhanced CLI: `gqs.py formula-auto-seed` / `scripts/autodraft`
Provide a dedicated CLI invocation for seeding and repairing equations with lineage:
```bash
# Synthesize formula definition AND auto-resolve parent/children in one step:
.venv/bin/python3 scripts/maintenance/generate_gemini_formula.py --latex "\nabla^2 G(\mathbf{r},\mathbf{r}") = -\delta^3(\mathbf{r}-\mathbf{r}")" --auto-link
```

**Output:**
```text
✨ Auto-Draft Synthesized: [Laplacian Green"s Function Differential Definition]
🔗 Lineage Auto-Discovery:
  • Parent Linked: greens-function-defining-operator-ident-b0ffa880 (SPECIAL_CASE)
  • Children Linked: electrostatic-potential-of-a-point-charge, dirichlet-boundary-condition-for-greens-function-61801a9d
  • Lineage Health Index (LHI): 90 / 100 [Rich & Complete]
💾 Shard & Graph Recompiled:
  • Saved to: app/config/content/formulas/38/shard_38.json
  • MariaDB Synced (equation_svg = NULL)
  • Derivation Graph: 13,790 nodes, 23,192 edges
```

### 2. Equation Explainer Fly-out Drawer (UI)
* When a user inputs an unindexed LaTeX formula and clicks **Auto-Draft**:
  * The frontend makes a POST request to `/api/define-formula`.
  * The response payload returns **both** the rich prose definitions and the **Derivation Tree Preview** (Parent breadcrumb + child chips).
  * Clicking "Save Formula" commits both definition and lineage graph edges simultaneously.

---

## 📋 5. Implementation Roadmap

- [ ] **Phase 1: Lineage Discovery Module**: Extract `discover_lineage_candidates(formula_title, equation, domain)` as an importable Python helper from `audit_lineage_health.py`.
- [ ] **Phase 2: Hook into `generate_gemini_formula.py`**: Call candidate discovery directly inside `generate_gemini_formula.py` after AI generation to auto-fill `parent_formula_id` and `subcomponents`.
- [ ] **Phase 3: Controller Graph Rebuild Hook**: Ensure `PhysicsController::apiDefineFormula` executes graph synchronization upon successful formula persistence.
- [ ] **Phase 4: Test & Verify**: Add automated regression tests in `tests/test_auto_draft_lineage.py` verifying that newly drafted formulas have $\\text{LHI} \\ge 80$.
