# Populating Parent-Child Derivation Edges Architecture

**Document ID**: `docs/populating_parent-child_derivation_edges.md`  
**Date**: July 24, 2026  
**Status**: Architectural Specification & Strategy Overview  
**Project**: Terra Physics Encyclopedia & Knowledge Graph Engine  

---

## Executive Summary

To transition Project Terra from a flat catalog of equations to a true **Symbolic Knowledge Graph**, the database schema was extended to support parent-child derivation edges (`parent_formula_id`, `derivation_type`, `constraints`, and `related_formula_ids`).

This document records the current state of relational edge population, how the proof-of-concept benchmark node was integrated, and the strategic roadmap for populating the remaining ~9,600+ formulas across the database.

---

## Current Status Audit

| Metric / Field | Status | Detail |
| :--- | :--- | :--- |
| **Schema Readiness** | **100% Complete** | MariaDB table `formulas` & JSON shards support all graph columns. |
| **PHP Sync Pipeline** | **100% Complete** | `PhysicsService::performSync()` syncs JSON graph fields into MariaDB. |
| **Proof-of-Concept Node** | **Populated** | `maxwell-static-limits` in `shard_51.json` linked as `LIMIT_CASE` child of `ampere-maxwell-law-with-bound-currents`. |
| **Remaining Catalog** | **Pending Population** | ~9,600+ formulas across `shard_1.json` ... `shard_50.json` have `parent_formula_id = ""`. |

---

## Proof-of-Concept Implementation (`maxwell-static-limits`)

In Phase 1, the static limit equations ($\nabla \times \mathbf{E} \to 0, \quad \nabla \times \mathbf{B} \to \mu_0 \mathbf{J}$) were registered in `app/config/content/formulas/shard_51.json` with explicit relational graph metadata:

```json
{
  "id": "maxwell-static-limits",
  "title": "Static Limits of Maxwell's Equations",
  "equation": "\\nabla \\times \\mathbf{E} \\to 0, \\quad \\nabla \\times \\mathbf{B} \\to \\mu_0 \\mathbf{J}",
  "parent_formula_id": "ampere-maxwell-law-with-bound-currents",
  "derivation_type": "LIMIT_CASE",
  "constraints": {
    "partial_t": 0,
    "regime": "electrostatic_magnetostatic"
  },
  "related_formula_ids": [
    "ampere-maxwell-law-with-bound-currents"
  ]
}
```

### Sync Pipeline Execution
Executing `php scripts/cli_sync.php` reads the shard JSON files and executes an SQL upsert:

```sql
INSERT INTO formulas (id, title, equation, parent_formula_id, derivation_type, constraints, related_formula_ids)
VALUES ('maxwell-static-limits', 'Static Limits of Maxwell\'s Equations', ..., 'ampere-maxwell-law-with-bound-currents', 'LIMIT_CASE', '{"partial_t":0,...}', '["ampere-maxwell-law-with-bound-currents"]')
ON DUPLICATE KEY UPDATE 
  parent_formula_id = VALUES(parent_formula_id),
  derivation_type = VALUES(derivation_type),
  constraints = VALUES(constraints),
  related_formula_ids = VALUES(related_formula_ids);
```

This enables `PhysicsService::getFormulaGraph('maxwell-static-limits')` to retrieve parent master laws, child derivative nodes, and related formulas.

---

## Strategies for Populating the Full Catalog (~9,600+ Formulas)

To populate derivation edges across all 51 shard files without manual authoring, three complementary strategies are specified:

### Strategy A: Batch AI Knowledge Graph Wire Script (Primary Recommendation)

A background maintenance script (`scripts/maintenance/wire_knowledge_graph.py`) leverages Gemini AI in batch mode:

```
[Read shard_XX.json (50 formulas)] ──► [Gemini AI Batch Prompt] ──► [Inject parent_formula_id & derivation_type] ──► [php scripts/cli_sync.php]
```

1. **Batching**: Reads each shard file (`shard_1.json` through `shard_50.json`), processing 50 formulas per batch.
2. **Gemini AI Prompting**:
   > *"Given these 50 physics equations (IDs, titles, TeX strings), identify any that are derived from, limits of, or equivalent to master fundamental laws (e.g. Newton's Laws, Maxwell's Equations, Schrödinger Equation, Navier-Stokes, Einstein Field Equations). Return a JSON mapping of `parent_formula_id` and `derivation_type` (`DERIVED_FROM`, `LIMIT_CASE`, `EQUIVALENT_FORM`, `SPECIAL_CASE`)."*
3. **Shard Writing**: Appends the returned graph edges back into `shard_1.json` ... `shard_50.json`.
4. **Database Sync**: Executes `php scripts/cli_sync.php` to sync all 9,600+ relational graph edges into MariaDB in under 10 seconds.

---

### Strategy B: Deterministic Heuristic Linker (Rule-Based Engine)

For formulas with explicit mathematical structures, a deterministic Python script detects relationships without AI calls:

- **Static / Steady-State Limits**: Equations containing $\partial/\partial t \to 0$ or zero time derivatives are automatically linked as `LIMIT_CASE` children to their time-dependent parent equations.
- **Integral vs. Differential Representations**: Integral equations ($\oint \mathbf{E} \cdot d\mathbf{A}$) are automatically linked as `EQUIVALENT_FORM` to differential equations ($\nabla \cdot \mathbf{E}$).
- **Non-Relativistic Limits**: Equations with $v \ll c$ or $\hbar \to 0$ are linked as `LIMIT_CASE` children to their relativistic or quantum master parents.

---

### Strategy C: On-Demand Enrichment via One-Click "Define" Engine

For newly created or custom formulas defined via the **One-Click Gemini AI Engine** (`docs/one_button_formula_definition.md`):

- As Gemini AI generates the formula definition, it automatically determines `parent_formula_id` and `derivation_type` as part of the JSON response schema.
- The new formula is saved to disk and MariaDB with its parent graph edge already wired.

---

## Derivation Types Reference

| Derivation Type | Description | Example |
| :--- | :--- | :--- |
| `DERIVED_FROM` | Directly derived via mathematical manipulation from master law. | Wave Equation derived from Maxwell's Equations. |
| `LIMIT_CASE` | Asymptotic limit when a constraint parameter approaches a boundary ($\partial/\partial t \to 0$, $v \ll c$). | Electrostatics derived from Time-Dependent Electrodynamics. |
| `EQUIVALENT_FORM` | Alternative mathematical representation of the same physical law. | Differential Gauss's Law vs. Integral Gauss's Law. |
| `SPECIAL_CASE` | Specific physical symmetry or geometry restriction applied. | Coulomb's Law as a spherically symmetric special case of Gauss's Law. |
