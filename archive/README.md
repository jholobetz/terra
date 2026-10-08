# 🗄️ Project Terra / Physics Lab — Historical Archive

> **Directory Status**: Historical & Deprecated Documentation Archive  
> **Active Specifications**: All authoritative, living documentation is maintained in [`docs/`](../docs/).

---

## 📖 Overview

This directory preserves historical planning documents, superseded technical designs, early prototype explorations, and post-incident reviews from prior development cycles (July–September 2026). 

These files are retained strictly for historical context, Git lineage, and technical retrospective. They do **not** govern active system architecture or CI quality gates.

---

## 🗂️ Categorized Archive Index

### 1. Superseded Milestones & Prototype Specifications
* `sim_fixes.md`: Simulations Observatory modernization blueprint (Phases 1 & 2 completed in `simulations.php`; Phase 3 elevation tracked in `docs/roadmap.md`).
* `Lab_Tools_UI_design_ideas.md`: Next-gen UI design ideas (Unified Cockpit, Legendre Transformer presets, and CAS coupling completed in Phase 2).
* `add_new_subtopics_hypothetical.md`: Hypothetical ingestion guide for thin shards (commands and workflow formalized in `CLAUDE.md` and `docs/roadmap.md`).
* `_eq_ex_modularization.md`: Early deconstruction plan for `equation_explainer.js` (Completed in Phase 1.1).
* `_lab_tools_revamp.md` & `_lab_tools_update_ideas.md`: Early exploratory notes for the Analytical Mechanics Cockpit.
* `lab_tool_chest_2026-09-22.md`: Initial 100-in-1 toolchest brainstorm superseded by `docs/Lab_Tools_UI_design_ideas.md`.
* `fix_equation_by_url_update_v2.md` & `fixlatex_button.md`: Early specifications for the `fixlatex` single-pass engine.
* `batch_auto_remediation_architecture.md`: Retrospective design for one-off equation remediation.
* `genealogy_explorer/`: Prototype predecessor to the Lineage DAG and Universe Graph (`/physics/universe-graph`).

### 2. Early Derivation Graph & Lineage Notes
* `Formula_Lineage_Definition.md`: Initial schema formulation for mathematical parent-child derivation edges.
* `populating_parent-child_derivation_edges.md`: Early sprint notes for connecting isolated formula nodes.
* `update_Mathematical_Lineage_Map.md`: Initial graph compilation scripts (superseded by `scripts/fixlineage`).
* `merge_auto_draft_lineage.md`: Retrospective notes on automated derivation inference.

### 3. Historical Explorations & Retrospectives
* `incident_report_google_billing.md`: Root-cause analysis of early LLM token overruns that led to `docs/cost_governance.md`.
* `_gem_3_8_report.md` & `_report_2026-08-08.md`: Mid-sprint development progress logs.
* `_5_sciences.md`, `_beyond_5_sciences.md`, `_non_terra_sciences.md`: Conceptual vision for Project Terra multi-science expansion.
* `shard_scalability-2026-07-24.md`: Early performance analysis preceding the 256-shard partitioning.

---

## 🏛️ Active Documentation Map

For current architectural rules, development guidelines, and active roadmaps, refer to:
* [`CLAUDE.md`](../CLAUDE.md): Supreme developer guide & commands.
* [`README.md`](../README.md): System overview and metrics.
* [`docs/architecture.md`](../docs/architecture.md): FlightPHP, 256-shard data model, and SymPy CAS.
* [`docs/roadmap.md`](../docs/roadmap.md): Active development roadmap (2026–2027).
* [`docs/cost_governance.md`](../docs/cost_governance.md): Token estimation & spending ceilings.
* [`docs/delimiters.md`](../docs/delimiters.md): Math prose delimiter standards.
* [`docs/OPS 2.0 (The Qualitative Rubric).md`](../docs/OPS%202.0%20%28The%20Qualitative%20Rubric%29.md): Pedagogical quality gates.
