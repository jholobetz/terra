# Single-Letter Variable Hover-Card Discrepancy & Resolution Options

## Problem Statement

When viewing topic pages (e.g., [`/physics/topic/classical-mechanics`](http://localhost:8000/physics/topic/classical-mechanics)) versus subtopic overview pages (e.g., [`/physics/subtopic/classical-mechanics-overview`](http://localhost:8000/physics/subtopic/classical-mechanics-overview)), identical single-letter math variables display inconsistent or non-contextual information in their hover cards. 

For example, hovering over $F$ in the opening abstract of Classical Mechanics:
- **Topic Page (`/physics/topic/classical-mechanics`)**: Displays *"Electromagnetic Field Tensor (component)"* ❌
- **Subtopic Page (`/physics/subtopic/classical-mechanics-overview`)**: Displays *"Force Vector"* ✅

---

## Cause Analysis

The discrepancy stems from two different data-gathering mechanisms used in the backend controllers:

### 1. Topic View (`/physics/topic/classical-mechanics`)
- **Mechanism**: Unscoped Global Database Query.
- **Implementation**: In `PhysicsController::topic()`, the controller queries all ~13,700+ formulas across the entire database:
  ```php
  SELECT title, semantic_variables FROM formulas WHERE semantic_variables IS NOT NULL AND semantic_variables != ''
  ```
- **First-Match-Wins Trap**: As MariaDB iterates through rows across all domains (electrodynamics, thermodynamics, quantum mechanics, etc.), the query populates `$topicVariableMap[$sym]` using `if (!isset($topicVariableMap[$sym]))`. The **very first database row** encountered that contains symbol $F$ locks in the title for $F$. Because row return order is non-deterministic, an electrodynamics formula defining $F_{\mu\nu}$ ("Electromagnetic Field Tensor (component)") was encountered first in table order, locking in $F$ as the Field Tensor for the entire Classical Mechanics topic page.

### 2. Subtopic View (`/physics/subtopic/classical-mechanics-overview`)
- **Mechanism**: Locally Scoped Subtopic Aggregation.
- **Implementation**: In `PhysicsController::viewSubtopic()`, the controller delegates variable resolution to `VariableAggregator::buildSubtopicVariables()`, which scans **only formulas linked to that specific subtopic**.
- **Context Preservation**: Formulas within `classical-mechanics-overview` (such as Newton's Second Law $F = ma$) define $F$ as *"Force Vector"*. Because the search is scoped strictly to Classical Mechanics Overview, $F$ evaluates to **Force Vector**.

---

## Comparison Summary

| View | Query Strategy | Scope | Result for $F$ |
| :--- | :--- | :--- | :--- |
| **Topic Page** (`/physics/topic/*`) | First-match-wins SQL scan | **Global** (All 13,700+ formulas) | **Electromagnetic Field Tensor** ❌ |
| **Subtopic Page** (`/physics/subtopic/*`) | Scoped formula aggregation | **Local** (Only Classical Mechanics) | **Force Vector** ✅ |

---

## Additional Technical Nuances with Single-Letter Variables

1. **Case Sensitivity Collisions ($v$ vs. $V$, $p$ vs. $P$)**:
   - $v$ (velocity) vs. $V$ (volume / potential).
   - In `hub_interactions.js`, fallback lookups like `topicVarMap[symbol.toUpperCase()]` can accidentally map lowercase $v$ to uppercase $V$ (**Volume**).
2. **Formatting Stripping ($\mathbf{F}$ vs. $F$ vs. $\mathcal{F}$)**:
   - `wrapVariableTriggers` strips TeX commands (`\mathbf`, `\vec`, `\mathcal`), mapping vector force $\mathbf{F}$, scalar force $F$, and Fourier transform $\mathcal{F}$ all to `F`.
3. **Structural Operators ($d$, $i$, $t$, $x$)**:
   - Differential operator $d$ in $dt$ or index $i$ in $\sum_{i=1}^N$ get wrapped as variable triggers, generating unnecessary hover-cards for non-variable symbols.

---

## Solution Options

### 🔹 Option 1: Topic-Scoped Database Query (Quickest Backend Fix)
- **Concept**: Update `PhysicsController::topic()` to restrict its MariaDB formula scan to **only formulas associated with subtopics under that specific topic**, rather than querying the entire database globally.
- **Mechanism**:
  1. Retrieve all subtopic slugs belonging to the current topic (e.g., `classical-mechanics-overview`, `lagrangian-mechanics`, etc.).
  2. Query only formulas linked to those subtopic slugs.
  3. Build `$topicVariableMap` from topic-relevant formulas.
- **Pros**: Rapid implementation; immediately fixes wrong-domain symbols like $F$ on topic pages without changing frontend JS.
- **Cons**: Keeps custom SQL logic in the controller rather than consolidating into a service class.

### 🔹 Option 2: Unified `VariableAggregator::buildTopicVariables()` (Recommended - Clean Architecture)
- **Concept**: Refactor `PhysicsController::topic()` to delegate variable map generation to `VariableAggregator`, using the exact same aggregation engine used by subtopics.
- **Mechanism**:
  1. Add `VariableAggregator::buildTopicVariables($topicSlug, $subtopicsMap)` in `app/logic/VariableAggregator.php`.
  2. Aggregate formulas across all subtopics in the topic tree.
  3. Match symbols against `variable_registry.json` using the topic's domain (e.g., `Classical Mechanics`).
- **Pros**: Clean, DRY (Don't Repeat Yourself) architecture; unifies topic and subtopic hover-card data pipelines completely.
- **Cons**: Requires minor refactoring in `VariableAggregator.php` and `PhysicsController.php`.

### 🔹 Option 3: Domain-Keyed Registry Overrides + Unified Aggregator (Most Robust & Scalable)
- **Concept**: Combines **Option 2** with explicit domain-keyed symbol entries in `app/config/variable_registry.json`.
- **Mechanism**:
  1. Add domain override entries in `variable_registry.json` for overloaded single-letter symbols ($F, E, P, V, T, S$).
  2. When rendering any topic or subtopic, `VariableAggregator` checks if the symbol has an explicit override for the active domain (e.g., $F$ in `classical-mechanics` $\to$ **Force Vector**; $F$ in `electromagnetism` $\to$ **Field Tensor**).
  3. Falls back to local formula definitions if no explicit domain override is set.
- **Pros**: Solves cross-domain symbol collisions sitewide for both topics and subtopics; provides total editorial control over symbol definitions.
- **Cons**: Requires updating `variable_registry.json` for major single-letter physics variables.
