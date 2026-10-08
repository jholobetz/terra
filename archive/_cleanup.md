# 🧹 Terra Physics Lab — Codebase Cleanup & Architectural Hygiene Plan

> **Status**: Proposed / Active Backlog  
> **Target Date**: September 2026  
> **Context**: Post-Horizon 2 Stabilization (100% OPS, LHI 95.2, 0 Isolated Nodes, Symbolic CAS Integrated)

---

## Executive Summary

With the core physical manifold stabilized, all 1,584 subtopics graduated, and 100% derivation graph connectivity achieved (44,558 direct links), the focus shifts toward **codebase hygiene, dead code reduction, and modularization**. 

This document outlines the four high-impact architectural cleanup priorities designed to reduce bundle size, eliminate cognitive overhead, and ensure long-term maintainability.

---

## 1. Modularization of the Client Monolith (`public/js/equation_explainer.js`)
* **Priority**: High  
* **Impact**: High (performance, code readability, bundle decoupling)  
* **Current State**: [equation_explainer.js](file:///Users/holobetj/code/gemini/terra/public/js/equation_explainer.js) is **5,297 lines long**—the single largest file in the entire repository.

### Problem Analysis
`equation_explainer.js` currently conflates five distinct domain responsibilities:
1. **LaTeX Compiler & MathJax Runner**: `compileMathJax`, macro protection regexes, and environment handlers.
2. **Symbolic CAS Engine & Asymptotic Limits**: `renderCasLimitsCard`, quick chips, and async `/api/cas-evaluate` communication.
3. **Curator Drawer & Suggestion Modal**: `drawerFieldTitle`, `drawerFieldLimits`, and save actions.
4. **Canvas Physics Simulation Sandbox**: 2D/3D visualizers, Lorentz boosts, and particle orbits (~1,800 lines).
5. **Topological Bridges & Knowledge Graph UI**: `renderKnowledgeGraphCard`, `renderBridges`, and node navigation.

### Remediation Plan
* Follow the pattern established by extracting `math_prose_formatter.js`.
* Extract Canvas physics simulations into `public/js/explainer_simulations.js`.
* Extract Curator Drawer logic into `public/js/explainer_curator.js`.
* **Target**: Reduce `equation_explainer.js` by ~2,500 lines, improving initialization time and isolation for unit testing.

---

## 2. Archive & Purge of Obsolete Scratch Scripts (`scratch/`)
* **Priority**: High  
* **Impact**: High (reduces disk footprint and repository noise)  
* **Current State**: The `scratch/` directory contains **55 one-off scripts and HTML files** dating back to early July.

### Problem Analysis
* **30+ Legacy Fixers**: Scripts such as `fix_nested_brace_dollars.py`, `fix_orphaned_dollars.py`, `fix_fraction_extensions.py`, and `repair_formula_delimiters.py` were one-off historical migrations. All canonical delimiter logic now permanently lives in `scripts/lib/delimiters.py` and `integrity_shield.py`.
* **Stale HTML Test Files**: Massive static HTML dumps (`newtons_third_law.html` [277 KB], `explainer_page.html` [163 KB], `jeans_explainer_page.html` [135 KB]) lingering in the repo tree.

### Remediation Plan
* Move obsolete historical one-off scripts into `docs/archive/historical_scratch/` or remove them entirely.
* Delete stale HTML debug files.
* Ensure `scratch/` is properly governed in `.gitignore` so temporary diagnostic outputs do not pollute git status.

---

## 3. Consolidation & Deprecation in `scripts/maintenance/`
* **Priority**: Medium  
* **Impact**: Medium (developer experience, operational clarity)  
* **Current State**: `scripts/maintenance/` contains **73 utility scripts** (~1.3 MB).

### Problem Analysis
* Several scripts are redundant or have been superseded by canonical CLI tools:
  - `repair_47_delimiters.py`, `repair_corrupted_shards.py`, and `repair_all_shard_latex_prose.py` were sprint-specific and are no longer executed.
  - `auto_register_references.py` and `auto_linker.py` have overlapping responsibilities with `scripts/maintenance/lineage_resolver.py` and `scripts/fixlineage`.

### Remediation Plan
* Consolidate redundant utilities into canonical scripts:
  - Keep `fixlatex` and `fix_equation_by_url.php` as the primary equation repair tool.
  - Keep `fixlineage` and `enrich_lineage_families.py` as the primary lineage tools.
  - Keep `integrity_shield.py` as the primary verification tool.
* Retire deprecated one-off scripts to `scripts/archive/`.

---

## 4. Static Assets & Dead Route Audit
* **Priority**: Low / Polish  
* **Impact**: Low (clean architecture)  
* **Current State**: Multiple legacy routes and view templates exist from earlier prototype sprints.

### Problem Analysis
* Certain experimental views in `app/views/physics/` (e.g., experimental tuner views) and routes in `app/config/routes.php` should be audited for dead code.
* Commented-out debugging markup in `equation_explainer.php` and `formula_page.php`.

### Remediation Plan
* Audit all routes in `app/config/routes.php` against controller actions to ensure 100% active usage.
* Remove commented-out dead HTML/JS blocks in view templates.

---

## Implementation Sequence

| Phase | Task | Estimated Time | Token Impact |
| :--- | :--- | :---: | :---: |
| **Phase 1** | Clean up `scratch/` (purge stale HTML, archive legacy fixers) | ~5–10 mins | Very Low |
| **Phase 2** | Decompose `public/js/equation_explainer.js` (extract simulations & curator) | ~25–35 mins | Low |
| **Phase 3** | Consolidate and archive deprecated `scripts/maintenance/` tools | ~15–20 mins | Low |
| **Phase 4** | Route & template dead-code pass | ~10–15 mins | Very Low |
