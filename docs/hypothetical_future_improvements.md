# Architecture Proposal: Unified Variable Resolution & Hover-Card System

## Overview & Background

This document outlines proposed future improvements for the variable hover-card and single-letter symbol resolution architecture in Terra. 

Currently, Terra has **three separate subsystems** that handle variable hover-cards and symbol resolution across different views:

1. **Subtopic View (`subtopic.php` & `VariableAggregator.php`)**:
   - Scoped strictly to formulas linked to the active subtopic.
   - Uses canonical definitions from `variable_registry.json`.
   - Rendered via inline JavaScript (`#var-hover-card`).

2. **Topic View (`topic.php` & `hub_interactions.js`)**:
   - Executes an unscoped SQL query (`SELECT title, semantic_variables FROM formulas`) across all ~13,700+ database rows.
   - Applies a "first-match-wins" strategy without domain filtering.
   - Rendered via `hub_interactions.js` (`#variable-hover-card-popover`).

3. **Equation Explainer (`equation_explainer.js`)**:
   - Uses a client-side tokenizer, domain auto-detection, and local/global dictionaries (`physicsDictionary`, `variableDictionary`).

Because these three views use different data aggregation paths and frontend JavaScript renderers, single-letter variables (e.g., $F$, $E$, $P$, $V$) can display inconsistent titles or fallback descriptions across different pages (e.g., $F$ rendering as "Electromagnetic Field Tensor" on the Classical Mechanics topic page vs. "Force Vector" on the subtopic page).

---

## Proposed Future Improvements

### 1. Unify Variable Resolution in `VariableAggregator` (Single Backend Source of Truth)

- **Problem**: `PhysicsController::topic()` executes its own ad-hoc SQL query (`SELECT title, semantic_variables FROM formulas`) across all formulas in the database, bypassing the domain-aware `VariableAggregator` logic used by subtopics.
- **Proposed Architecture**: Create a unified backend method:
  ```php
  VariableAggregator::buildTopicVariables(string $topicSlug, array $subtopicSlugs): array
  ```
- **Mechanism**:
  1. Collect all subtopic slugs belonging to the target topic (e.g., `classical-mechanics` $\to$ `classical-mechanics-overview`, `lagrangian-mechanics`, `hamiltonian-mechanics`, etc.).
  2. Aggregate variable definitions **strictly from formulas linked within those subtopics**, rather than querying the entire database globally.
  3. Guarantee that single-letter symbols on topic pages (such as $F$ on `/physics/topic/classical-mechanics`) resolve to their domain-correct definitions (e.g., **Force Vector**).

---

### 2. Domain Context Overrides in `variable_registry.json`

- **Problem**: Single-letter symbols ($F, E, P, V, T, S, H$) have inherently different physical meanings in different branches of physics.
- **Proposed Schema**: Enhance `app/config/variable_registry.json` to support explicit domain-keyed overrides:
  ```json
  "F": {
    "display_symbol": "F",
    "default": {
      "name": "Force Vector",
      "unit": "N",
      "description": "Vector push or pull acting upon an object."
    },
    "domains": {
      "classical-mechanics": {
        "name": "Force Vector",
        "unit": "N",
        "description": "Vector sum of external interactions acting on a mass ($F = ma$)."
      },
      "electromagnetism": {
        "name": "Electromagnetic Field Tensor (Component)",
        "unit": "V/m",
        "description": "Antisymmetric rank-2 tensor $F_{\\mu\\nu}$ unifying E and B fields."
      },
      "thermodynamics": {
        "name": "Helmholtz Free Energy",
        "unit": "J",
        "description": "Thermodynamic potential measuring useful work obtainable from a closed system."
      }
    }
  }
  ```

---

### 3. Consolidated Frontend Hover-Card Component (`variable_hover_card.js`)

- **Problem**: `subtopic.php` contains inline JavaScript for `#var-hover-card`, while `topic.php` relies on `hub_interactions.js` (`#variable-hover-card-popover`).
- **Proposed Solution**: Extract hover-card rendering into a standalone reusable module (`public/js/components/variable_hover_card.js`):
  - **Unified Styling**: Identical glassmorphic dark-mode design across all views.
  - **Shared Positioning**: Unified viewport overflow bounds checking and smooth fade-in/out transitions.
  - **MathJax Integration**: Single robust MathJax typesetting queue for rendering math snippets inside hover-card popovers.

---

### 4. Smart Candidate Ranking for Fallbacks

- **Problem**: When a formula or page contains an unlisted symbol, the fallback database query picks the first row returned by MariaDB.
- **Proposed Solution**: Rank candidate definitions by a relevance score:
  1. **Category/Domain Match**: Match formulas tagged with the current topic slug (+10 points).
  2. **Platinum Status**: Prefer verified Platinum formulas over draft formulas (+5 points).
  3. **Usage Frequency**: Prefer symbols used in more core equations within that subfield (+3 points).

---

## Summary of Key Benefits

1. **100% Consistency**: A single-letter symbol like $F$ will consistently render as **Force Vector** across topic pages, subtopics, and formula cards in Classical Mechanics.
2. **Context-Aware Precision**: Moving between `/physics/topic/classical-mechanics` and `/physics/topic/thermodynamics` will seamlessly switch $F$ between **Force Vector** and **Helmholtz Free Energy**.
3. **Clean Codebase**: Eliminates duplicate inline hover scripts in favor of a single JS component and centralized backend aggregator.
