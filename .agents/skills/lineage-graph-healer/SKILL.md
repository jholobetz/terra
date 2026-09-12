---
name: lineage-graph-healer
description: >-
  Audit, heal, and maintain the mathematical derivation Directed Acyclic Graph (DAG) across
  all 14,614 formulas. Resolves isolated or thin formula nodes, enforces loop-free acyclicity,
  maintains reciprocal parent-child links across 256 shards, and benchmarks the Lineage Health Index (LHI).
---

# 🌲 Lineage Graph Healer Skill

Use this skill whenever inspecting formula derivations, auditing isolated nodes, connecting parent-child equations, or resolving DAG graph cycles.

---

## 1. Lineage Architecture & Shard Partitioning

* **The 256 Shards**: Formulas live in `app/config/content/formulas/[00-ff]/shard_[00-ff].json` indexed by `md5($id)[0:2]`.
* **The Graph Model**: Serialized in `app/config/formula_derivation_graph.json` and gzip-compressed for fast client delivery.
* **Lineage Keys**:
  * `parent_formula_id`: Canonical ID of the upstream foundational law or master equation.
  * `derivation_type`: `AXIOMATIC_FOUNDATION`, `DERIVED_FROM`, `SPECIAL_CASE`, `LIMITING_CASE`, `APPROXIMATION`, or `DEFINITION`.
  * `subcomponents`: Array of canonical formula IDs representing downstream child equations or terms.

---

## 2. Core CLI Commands

Always run Python commands from the `.venv/` virtual environment:

```bash
# Check sitewide Lineage Health Index (LHI) summary and tier distribution
scripts/fixlineage --summary

# Diagnose a specific formula node
scripts/fixlineage --target-id <formula-id>

# Run heuristic lineage healer to connect isolated nodes to domain pillars
scripts/fixlineage --heal

# Test derivation graph build and assert zero circular loops
.venv/bin/python3 scripts/build_formula_graph.py
```

---

## 3. The 4-Step Healing Protocol

When connecting an isolated or thin formula to the lineage graph:

1. **Identify Upstream Physical Pillar**:
   * Map the formula's domain and physical meaning to foundational axioms:
     * *Electrodynamics* &rarr; Maxwell's equations, Lorentz force
     * *Quantum Mechanics* &rarr; Schrödinger equation, Dirac equation
     * *Classical / Lagrangian* &rarr; Principle of Stationary Action, Euler-Lagrange
     * *Thermodynamics* &rarr; First/Second Laws, Boltzmann entropy
     * *General Relativity* &rarr; Einstein Field Equations, Hilbert Action

2. **Establish Bidirectional Linkage**:
   * Open the target formula's hex shard:
     * Set `parent_formula_id = "<parent-id>"`
     * Set `derivation_type = "SPECIAL_CASE"` (or appropriate type)
   * Open the parent formula's hex shard:
     * Append the target formula's ID to the parent's `subcomponents` array.
   * *Reciprocity is mandatory*—a parent must reference its children, and a child its parent.

3. **Synchronize MariaDB & Hash Registry**:
   * If MariaDB is available, update the `formulas` table rows (`parent_formula_id`, `derivation_type`, `subcomponents`).
   * Update SHA-256 hashes in `app/config/formulas_hash_registry.json`.

4. **Recompile the Derivation Graph**:
   * Execute `.venv/bin/python3 scripts/build_formula_graph.py`.
   * Assert the build succeeds with **0 circular loops**.
   * Verify LHI score remains $\ge 95.0 / 100$ with **0 isolated nodes**.
