# Equation Explainer Enhancements & Maintenance Ideas

**Document ID**: `DOC-2026-EQEX-IDEAS-001`  
**Created**: `2026-07-25`  
**Status**: Proposal / Backlog  

---

## 1. Database Shard Sanitization (`semantic_variables` Cleaning)

### Problem Definition
An audit of all 256 formula shards (`app/config/content/formulas/shard_00.json` .. `shard_ff.json`) revealed that **5,396 out of 7,653 formulas** contain legacy delimiter-wrapped keys inside their `semantic_variables` object (e.g., `"\(ds^2\)"`, `"\(dt\)"`, `"\(d\)"`, `"\(s\)"`, `"\(t\)"`).

While the runtime frontend (`public/js/equation_explainer.js`) now actively strips these delimiters and suppresses sub-key collisions at runtime via the `consumedSubtokens` integrity shield, performing a one-time database sanitization is recommended for database hygiene and clean JSON storage.

### Proposed Action: `scripts/maintenance/sanitize_semantic_variables.py`
A Python maintenance script that scans all 256 formula shards and:
1. **Strips LaTeX Delimiters**: Normalizes keys by removing `\( ... \)`, `\[ ... \]`, `$$ ... $$`, `$ ... $`.
2. **Eliminates Redundant Sub-keys**: Removes isolated sub-tokens (e.g., `"d"`, `"s"`, `"t"`) when composite symbols (e.g., `"ds^2"`, `"dt"`) are already defined for the formula.
3. **Deduplicates Entries**: Merges duplicate definitions within the same formula object.
4. **Re-syncs MariaDB**: Automatically invokes `php cli_sync.php` after sanitizing the JSON shards on disk.

---

## 2. Additional Explainer Roadmap Ideas

### 2.1 AST-Based Structural Grouping (TeX AST Rendering)
* Further enhance `renderElementsBreakdown()` to partition variables into visually distinct, categorized cards:
  * **Operators** ($\hat{A}$, $\nabla$, $\partial_\mu$)
  * **Quantum States / Vectors** ($|\psi\rangle$, $\vec{v}$)
  * **Scalars & Amplitudes** ($a, b, c$)
  * **Physical Constants** ($\hbar$, $G$, $c$, $k_B$)

### 2.2 Domain-Scoped Fallback Dictionary Scoping
* Partition `physicsDictionary` into distinct physics domains (Quantum Mechanics, General Relativity, Thermodynamics, Electromagnetism) so un-curated symbol fallbacks default to contextually relevant definitions based on active domain detection.
