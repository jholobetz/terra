# Pre-Commit Git Integrity Audit Engine (`integrity_shield.py`)

## Overview

The Git pre-commit hook in Project Terra is powered by **`integrity_shield.py`**, which is automatically executed by `.git/hooks/pre-commit` every time a developer or agent runs `git commit`. 

If any check fails (non-zero exit code), **the commit is automatically aborted**, preventing corrupted, malformed, or scientifically invalid data from entering the Git revision history.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           GIT PRE-COMMIT HOOK                                  │
│                       (.venv/bin/python3 integrity_shield.py)                   │
└───────────────────────┬─────────────────────────────────┬───────────────────────┘
                        │                                 │
         ┌──────────────┴──────────────┐   ┌──────────────┴──────────────┐
         │    Static & Schema Audits   │   │  Domain Physics & Alignment │
         └──────────────┬──────────────┘   └──────────────┬──────────────┘
                        │                                 │
  1. JSON Schema Validation             5. NIST CODATA 2022 Constants
  2. MathJax & SVG Pre-Rendering        6. PDG 2024 Particle Alignment
  3. Internal Link Integrity            7. Semantic Prose Drift Check
  4. Anti-Duplicate & Structure         8. Variable Ambiguity Audit
```

---

## Core Integrity Audit Pillars

### 1. Structural & JSON Schema Validation
* **Subtopic & Formula Schemas**: Validates all content files and all 256 formula shards (`shard_00.json` .. `shard_ff.json`) against strict Draft-7 JSON schemas (`subtopic.schema.json` and `formula.schema.json`).
* **Required Fields**: Guarantees required fields (`title`, `equation`, `conceptual_definition`, `interpretation`, `semantic_variables`) are present, non-empty, and typed correctly.

### 2. MathJax Compilation & Pre-Rendering Audit
* **Math Error Shield**: Scans equations for compilation failures (`mjx-error`, `merror`, red-text fallback markup).
* **SVG Verification**: For "Platinum" level content, ensures display math is pre-rendered into fully inlined, self-contained SVG tags.
* **Anti-Spritified Check**: Rejects obsolete `math-path-` sprite references to guarantee standalone rendering.

### 3. Graph Link & Reference Integrity
* **Zero Broken Links**: Scans all `href="/physics/subtopic/..."` and `/physics/topic/...` links across all prose. Rejects the commit if any link points to a non-existent slug.
* **Orphaned Formula Shield**: Verifies that every formula ID referenced by a subtopic exists in a valid formula shard.

### 4. NIST CODATA & PDG 2024 Reference Verifiers
* **NIST CODATA 2022 (`nist_constants_verifier.py`)**: Checks physical constants stored in `app/config/content/constants.json` against official NIST CODATA reference values ($c$, $\hbar$, $e$, $k_B$, $G$, $\varepsilon_0$, etc.).
* **PDG 2024 Particle Data (`pdg_particle_verifier.py`)**: Checks particle properties in `particles.json` against official 2024 Particle Data Group tables (masses, spins, charges, lifetimes).

### 5. Semantic Prose & Scientific Alignment
* **Semantic Drift Shield (`semantic_prose_verifier.py`)**: Compares scientific explanations against `app/config/ref_data/semantic_references.json` using keyword extraction and similarity thresholds to detect factual hallucinations or key concept omissions.

### 6. Formula Variable Ambiguity Audit
* **Node.js Ambiguity Engine (`scripts/maintenance/audit_ambiguity.js`)**: Scans `semantic_variables` across formula definitions to detect symbol collisions (e.g., distinguishing when $A$ means *Area* vs *Vector Potential* vs *Operator* $\hat{A}$).

### 7. Structural Integrity & Protected Registry
* **Duplicate Prevention**: Confirms every subtopic slug exists in exactly one shard file.
* **Protected Topic Registry**: Ensures top-level discipline topics (`relativity`, `quantum-physics`, `electromagnetism`, `classical-mechanics`, etc.) are pinned in `global_slug_registry.json` and not polluted inside subtopic shards.
* **Prose Layout Rules**: Blocks raw HTML header tags (`<h1>`–`<h6>`), enforcing continuous `<p>` prose formatting.

### 8. Technical Density & Depth Scoring
* **Academic Rigor Metric**: Calculates a density score based on LaTeX math density, SVG presence, and domain terminology (*manifold, unitary, Lagrangian, Hamiltonian, tensor, variational*). Emits warnings if word count or mathematical density falls below academic standards.

---

## Execution Command & Integration

To manually run the pre-commit integrity shield outside of `git commit`:

```bash
# Run complete audit across all 256 shards
.venv/bin/python3 integrity_shield.py

# Run targeted audit on a single subtopic slug
.venv/bin/python3 integrity_shield.py "quantum-harmonic-oscillator"
```
