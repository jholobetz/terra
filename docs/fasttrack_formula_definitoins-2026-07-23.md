# Fast-Track Formula Definition Architecture

**Document ID**: `docs/fasttrack_formula_definitoins-2026-07-23.md`  
**Date**: July 23, 2026  
**Status**: Architectural Vision & Specification  
**Project**: Terra Physics Encyclopedia & Knowledge Graph Engine  

---

## Executive Summary

As Project Terra expands across Physics, Chemistry, and Biology, encountering mathematical expressions or theoretical identities not yet registered in pre-compiled database shards (such as $G(\mathbf{r}, \mathbf{r}')$ — Position-Space Green's Function) is a natural occurrence. 

While the **Phase 3 AST Synthesizer** provides real-time fallback explanations in memory, persisting newly encountered formulas into permanent database shards requires a fast, secure, and rigorous workflow. 

This document specifies the architectural vision for fast-tracking formula creation and updates via 3 complementary pathways, with special focus on **Pathway 2 (Secure CLI Tooling)** and **Pathway 3 (Automated AI Auto-Enrichment Queue)**.

---

## Comparative Pathway Overview

| Feature / Metric | Pathway 1: In-UI Graduation | Pathway 2: Secure CLI Tooling | Pathway 3: AI Auto-Enrichment Queue |
| :--- | :--- | :--- | :--- |
| **Execution Context** | Browser UI Modal | Terminal / SSH Environment | Background Job / Subagent Pipeline |
| **Security Control** | Requires User/Admin Auth Tiers | Inherently Secure (Server Access) | Controlled via Integrity Shields & Staging |
| **Human Effort** | 1-Click Browser Approval | Single Terminal Command | Zero (Fully Autonomous) |
| **Execution Time** | $< 2$ seconds | $< 3$ seconds | Periodic Batch Processing |
| **Current Readiness** | Post-Auth Tier Roadmap | **Immediate Target (Phase 5)** | **Target for Scaled Expansion** |

---

## Pathway 1: In-UI Graduation Modal (Post-Auth Tier Roadmap)

### Concept
When an unregistered formula is entered into the Equation Explainer, the live AST Synthesizer generates a structured breakdown in memory. In an environment with user authentication and admin role permissions:
- A **"✦ Graduate to Shard"** action button appears on the status badge for verified administrators.
- Clicking the button opens an in-page modal pre-filled with the synthesized title, conceptual definition, intuitive summary, interpretations, and semantic variables.
- One-click publishing sends a `POST /api/formulas/graduate` request to commit the shard and sync the database in real time.

> [!NOTE]
> **Status**: Deferred until multi-tier user authentication & role-based access control (RBAC) are integrated into Project Terra.

---

## Pathway 2: Secure CLI Fast-Track Tooling (Immediate Target)

### Concept
Because CLI execution requires system-level server access, it provides a naturally secure, lightweight, and predictable environment for content developers.

### Execution Pattern
```bash
python3 scripts/maintenance/create_formula_shard.py \
  --id "greens-function-position-space" \
  --title "Position-Space Green's Function" \
  --latex "G(\\mathbf{r}, \\mathbf{r}')" \
  --parent "poisson-equation-electrostatics" \
  --type "DERIVED_FROM"
```

### Automated Steps Executed in Under 3 Seconds:
1. **Shard Discovery**: Scans `app/config/content/formulas/shard_*.json` to locate the current active shard file (or rolls over to `shard_52.json` if capped at 50 entries).
2. **Variable Auto-Populator**: Deconstructs TeX operators and populates default field theory variables ($G$: *Green's Function propagator*, $\mathbf{r}$: *Observation vector*, $\mathbf{r}'$: *Source vector*).
3. **Database & Index Sync**: Automatically triggers `php scripts/cli_sync.php` to sync the MariaDB database table and rebuild `formulas_latex_index.json`.

---

## Pathway 3: Automated AI Auto-Enrichment Queue (Deep Dive)

Pathway 3 enables Project Terra's catalog to scale autonomously based on real user search demand without requiring manual authoring for every single identity.

```
+------------------------+      +--------------------------+      +----------------------------+
| User Searches Undefined| ---> | Telemetry Log Queue      | ---> | AI Auto-Enricher Pipeline  |
| Formula G(r, r')       |      | (Hit Count Prioritization|      | (Deconstruction & Drafting)|
+------------------------+      +--------------------------+      +----------------------------+
                                                                                 |
                                                                                 v
+------------------------+      +--------------------------+      +----------------------------+
| Published Shard &      | <--- | Database Sync &          | <--- | Integrity Shield &         |
| Knowledge Graph Edge   |      | Index Rebuild            |      | Semantic Prose Audit       |
+------------------------+      +--------------------------+      +----------------------------+
```

### Step 1: Telemetry & Demand-Driven Queueing
Whenever an unregistered TeX formula is queried:
1. The user receives an instant, in-memory **AST Fallback Explanation**.
2. The system logs the formula string, domain context, and timestamp to a telemetry log (`app/config/queue/pending_unregistered_formulas.json`).
3. Formulas automatically rank by **hit count** so the most highly demanded expressions bubble to the top.

```json
{
  "latex": "G(\\mathbf{r}, \\mathbf{r}')",
  "hit_count": 18,
  "first_seen": "2026-07-23T23:00:00Z",
  "domain_hint": "electromagnetism"
}
```

### Step 2: The AI Auto-Enricher Pipeline
A periodic background agent processes top-queued formulas through a 5-stage synthesis pipeline:

1. **AST Structural Parsing**: Isolates operators ($\nabla^2$, $\partial/\partial t$, $\int$), fields ($G$, $\mathbf{E}$, $\mathbf{B}$), and boundary coordinates ($\mathbf{r}, \mathbf{r}'$).
2. **Academic Prose Drafting**: Drafts rigorous Platinum-standard fields:
   - `title`: Position-Space Green's Function
   - `conceptual_definition`: Impulse response / fundamental solution to a linear differential operator.
   - `intuitive_summary`: Response of a field at position $\mathbf{r}$ caused by a point source at $\mathbf{r}'$.
   - `interpretation`: Convolves with source distributions to solve linear inhomogeneous partial differential equations.
   - `symmetry_origin`: Translational invariance in homogeneous space implies $G(\mathbf{r}, \mathbf{r}') = G(\mathbf{r} - \mathbf{r}')$.
   - `limits_and_boundary`: Satisfies Dirichlet or Neumann boundary conditions on surface boundaries.
3. **Graph Relational Wiring**: Identifies parent master laws (e.g. Poisson's Equation in Electrostatics) and populates `parent_formula_id` and `derivation_type`.

### Step 3: Integrity Shield & Quality Gates
Before any auto-generated shard touches production storage, it is audited by Terra's automated verification suite:

- **Semantic Prose Verifier (`semantic_prose_verifier.py`)**: Computes TF-IDF cosine similarity against verified literature reference text, ensuring academic accuracy (>0.35 threshold).
- **Integrity Shield (`test_integrity_shield.py`)**: Enforces strict JSON schema validation, escaping of backslashes, valid TeX formatting, and non-broken parent graph edges.

### Step 4: Staging Controls & Safety Modes

Pathway 3 supports two operational safety modes:

- **Mode A: Staged Review (Default / Recommended)**:
  Generated entries are written with `"status": "staged-draft"`. Staged entries can be reviewed and batch-promoted to `"status": "published"` via a single CLI command (`python3 scripts/maintenance/approve_staged.py`).
- **Mode B: Fully Autonomous Publishing**:
  Formulas passing 100% of all integrity tests with cosine similarity $>0.50$ are published directly to database shards without human intervention.

---

## Architectural Compatibility

Pathways 2 and 3 share a unified core engine (`PhysicsService` & `cli_sync.php`), ensuring complete data consistency across all formula definition shards:

- **CLI Fast-Track (Pathway 2)** handles immediate manual additions by developers.
- **Auto-Enrichment Queue (Pathway 3)** continuously expands catalog depth in the background based on real-world telemetry.
