# 🌲 Formula Lineage Architecture & Healing Engine Specification

This document defines the mathematical foundation, scoring rubrics, graph structure, and automated repair mechanics governing formula derivation lineage in **Terra Physics Lab**.

---

## 1. Architectural Philosophy: Derivation Lineage Graph (DAG)

Rather than maintaining physics formulas as disconnected static catalog items, the encyclopedia models all **14,614 physical formulas** as an interconnected **Directed Acyclic Graph (DAG)** of mathematical lineage. 

```
                          ┌────────────────────────┐
                          │   Axiomatic Master     │
                          │   Foundation / Action  │
                          │     (e.g., δS = 0)     │
                          └───────────┬────────────┘
                                      │ DERIVED_FROM
                                      ▼
                          ┌────────────────────────┐
                          │    General Equation    │
                          │  (e.g., Euler-Lagrange)│
                          └───────────┬────────────┘
                                      │ SPECIAL_CASE
                                      ▼
                          ┌────────────────────────┐
                          │  Phenomenological Law  │
                          │ (e.g., Hamilton's Eq)  │
                          └───────────┬────────────┘
                                      │ LIMITING_CASE / APPROXIMATION
                                      ▼
                          ┌────────────────────────┐
                          │  Subcomponent / Bound  │
                          │(e.g., Harmonic Pot.)   │
                          └────────────────────────┘
```

### Lineage Attributes in Formula Shards:
Each formula defined in [`app/config/content/formulas/[00-ff]/shard_[00-ff].json`](file:///Users/holobetj/code/gemini/terra/app/config/content/formulas) carries structural metadata defining its coordinates in the derivation manifold:
* `parent_formula_id`: The canonical ID of the upstream foundational law or master equation.
* `derivation_type`: The formal physical and mathematical relationship to the parent:
  - `AXIOMATIC_FOUNDATION`: Fundamental first principles (e.g., Principle of Stationary Action, Einstein-Hilbert Action, Schrödinger Equation).
  - `DERIVED_FROM`: Exact mathematical consequence through formal transformation, integration, or operator representation.
  - `SPECIAL_CASE`: Specific physical reduction (e.g., electrostatic limit of Maxwell's equations, Schwarzschild metric from Einstein Field Equations).
  - `LIMITING_CASE`: Asymptotic reduction (e.g., non-relativistic limit $v \ll c$, classical limit $\hbar \to 0$, zero-temperature limit $T \to 0$).
  - `APPROXIMATION`: Physical truncation (e.g., Born approximation, WKB method, Mean-field theory).
  - `DEFINITION`: Foundational physical convention or operational definition.
* `subcomponents`: An array of formula IDs representing downstream child equations, branch terms, or irreducible components.

---

## 2. Quantitative Metric: Lineage Health Index (LHI)

The **Lineage Health Index (LHI)** continuously benchmarks derivation completeness on a **0 to 100** integer scale, calculated by [`scripts/maintenance/audit_lineage_health.py`](file:///Users/holobetj/code/gemini/terra/scripts/maintenance/audit_lineage_health.py).

### LHI Scoring Rubric (100 Points Total)

| Component | Max Points | Evaluation Criteria |
| :--- | :---: | :--- |
| **Upstream Ancestry** | **35 pts** | • **35 pts**: Has a validated `parent_formula_id` or is flagged as `AXIOMATIC_FOUNDATION`<br>• **0 pts**: Missing upstream parent |
| **Downstream Branching** | **35 pts** | • **35 pts**: $\ge 3$ non-trivial child subcomponents<br>• **25 pts**: Exactly 2 non-trivial child subcomponents<br>• **15 pts**: Exactly 1 non-trivial child subcomponent<br>• **5 pts**: Has trivial scalar/variable assignments only<br>• **0 pts**: Zero downstream subcomponents |
| **Derivation Depth Span** | **15 pts** | • **15 pts**: Multi-tier derivation spanning grandparents or grandchildren<br>• **10 pts**: Direct parent and child presence<br>• **5 pts**: Single-direction ancestry only (parent only or child only)<br>• **0 pts**: No depth connectivity |
| **Semantic Integrity** | **15 pts** | • **15 pts**: Robust non-trivial expressions<br>• **5 pts**: Children contain trivial scalar constants<br>• **0 pts**: Isolated with zero connections |

### Health Tiers

* 🟢 **Rich & Complete (Score 75–100)**: Fully integrated into the global derivation DAG, featuring verified upstream ancestors, downstream applications, and deep topological span.
* 🟡 **Moderate (Score 40–74)**: Connected to an upstream parent or downstream child, but lacking multi-tier depth or sufficient subcomponent diversity.
* 🔴 **Thin (Score 1–39)**: Weak connectivity (often single trivial assignment or unverified reference).
* ⚫ **Isolated (Score 0)**: Orphaned node. Has no upstream parent, no downstream subcomponents, and is not designated as an axiomatic foundation.

---

## 3. The Lineage Healing Protocol

### What "Healing" Executes Under the Hood
When isolated or thin formula nodes are healed, the automated pipeline performs four structured steps:

1. **Physical Semantic Matching**:
   The engine evaluates the isolated equation's title, conceptual definition, and TeX expression against foundational domain pillars:
   - **Electromagnetism**: Maps Maxwell-Lorentz relations to Ampère-Maxwell or Gauss laws.
   - **Quantum Dynamics**: Maps density matrix, Lindblad, or state-vector identities to the Time-Dependent Schrödinger Equation.
   - **Analytical Mechanics**: Maps canonical conjugate variables and cyclic coordinate theorems to the Principle of Stationary Action or Euler-Lagrange equations.
   - **Thermodynamics & Statistical Mechanics**: Maps Maxwell relations, free energies, and entropy bounds to the First/Second Laws of Thermodynamics.
   - **General Relativity & Cosmology**: Maps scale factor evolutions, deceleration parameters, and horizon bounds to the Friedmann equations or Einstein Field Equations.

2. **Bidirectional Graph Linking**:
   - Sets the target formula's `parent_formula_id` and assigns its `derivation_type` (e.g., `SPECIAL_CASE` or `DERIVED_FROM`).
   - Opens the parent formula's hex shard on disk and appends the target formula ID into the parent's `subcomponents` array, establishing a verified reciprocal parent $\leftrightarrow$ child link.

3. **Shard & Relational Persistence**:
   - Commits the updated JSON structures across the corresponding hex shards in `app/config/content/formulas/[00-ff]/shard_[00-ff].json`.
   - Synchronizes the updated fields (`parent_formula_id`, `derivation_type`, `subcomponents`) with the MariaDB `formulas` table.

4. **Derivation Graph Recompilation**:
   - Runs [`scripts/build_formula_graph.py`](file:///Users/holobetj/code/gemini/terra/scripts/build_formula_graph.py).
   - Audits the resulting graph for circular dependencies (ensuring strict DAG compliance with **zero circular loops**).
   - Compiles and serializes the updated graph to disk:
     - [`app/config/formula_derivation_graph.json`](file:///Users/holobetj/code/gemini/terra/app/config/formula_derivation_graph.json)
     - [`app/config/formula_derivation_graph.json.gz`](file:///Users/holobetj/code/gemini/terra/app/config/formula_derivation_graph.json.gz)

---

## 4. Lineage CLI Tooling & Workflows

| Tool | Invocation | Primary Purpose |
| :--- | :--- | :--- |
| **Lineage Health Auditor** | `scripts/fixlineage --summary` | Audits sitewide LHI score, distributions, and tier metrics across all 14,614 formulas. |
| **Single-Formula Diagnostic** | `scripts/fixlineage --formula <id>` | Inspects upstream parent, child counts, depth span, and point breakdown for a specific node. |
| **Family Pillar Enricher** | `python3 scripts/maintenance/enrich_lineage_families.py --dry-run` | Heuristic rule-based scanner that identifies parents for unlinked formulas based on TeX symbols and physical keywords. Add `--apply` to persist to shards and rebuild the graph. |
| **Direct Manual Linker** | `scripts/link_lineage --formula <id> --parent <pid> [--type SPECIAL_CASE]` | Explicit deterministic CLI to connect a specific child formula to an upstream parent, update reciprocal subcomponents, sync MariaDB, and recompile the DAG. |
| **Vertex AI Deep Enricher** | `python3 scripts/maintenance/run_vertex_lineage_enricher.py --filter isolated --limit 10` | AI-assisted derivation engine utilizing Google Gemini to synthesize deep derivations, semantic variables, and parent relations under strict token governance. |

---

## 5. Architectural Safeguards

1. **Zero-Loop Invariant**:
   Lineage paths must strictly flow from foundational axioms down to phenomenological equations. Circular dependencies ($A \to B \to A$) cause immediate build failure during graph serialization.
2. **Deterministic Hex Partitioning**:
   Lineage links span across different hex shards (`shard_00.json` through `shard_ff.json`) via mathematical hashing (`md5($id)[0:2]`), ensuring that linking formulas does not create file-locking bottlenecks.
3. **Non-Destructive Overwrites**:
   Automated family enrichers only target formulas where `parent_formula_id` is currently unassigned (`null` or empty string), strictly preserving existing human-curated or higher-order parent mappings.
