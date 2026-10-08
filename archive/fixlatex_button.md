# 🧮 Fix LaTeX Button: Architecture, Protocol & Parity Guide

This document details the architecture, execution pipeline, and synchronization protocol for the **"Fix LaTeX"** button in the Equation Curation Workspace fly-out drawer, establishing full functional parity with the CLI and Agent directive engine `scripts/fixlatex <URL> [HINT]`.

---

## 1. Executive Overview & Problem Statement

In the Physics Lab ecosystem, equation and narrative sanitization can occur through two distinct interfaces:
1. **CLI / Agent Protocol (`scripts/fixlatex <URL> [HINT]`)**: An automated script/directive that decodes local URLs, locates formula shards on disk, applies deep LaTeX decorruption and prose TeX sanitization, writes directly to shard files, and syncs MariaDB and LaTeX index mapping.
2. **Equation Curation Workspace Fly-out Drawer (UI)**: An interactive in-browser curator panel containing form inputs, live MathJax previews, guidance textareas, and action buttons ("Auto-Draft", "Fix LaTeX", "Save Draft / Propose", "Direct Update").

To ensure seamless curation, clicking **"Fix LaTeX"** in the browser drawer must execute the **identical decorruption, hint-application, and shard/database synchronization pipeline** as the CLI command, updating both the persisted shard on disk and the live browser DOM without requiring a page reload.

---

## 2. Execution Pipeline Comparison

| Step | CLI Engine (`scripts/fixlatex`) | Drawer UI Button ("Fix LaTeX") |
| :--- | :--- | :--- |
| **Trigger** | Terminal: `scripts/fixlatex "<URL>" ["<HINT>"]` | Click `#btn-fix-latex` in Curation Drawer |
| **Target Extraction** | Parses `?id=...` or `?latex=...` from URL query string | Reads `window.location.href`, `this.currentId`, and `this.drawerLatexInput.value` |
| **Hint / Reference** | Command-line argument: `argv[2]` | Textarea: `#drawer-guidance-input` |
| **Execution Engine** | `scripts/fix_equation_by_url.php` | API: `POST /physics/api/apply-repair` $\to$ `FormulaReviewService::repairTarget` |
| **TeX Decorruption** | `decorruptLatex()` & `sanitizeProseTeX()` | `decorruptLatex()` & `sanitizeProse()` |
| **Disk Persistence** | Writes directly to `app/config/content/formulas/[xx]/shard_[xx].json` | Writes directly to `app/config/content/formulas/[xx]/shard_[xx].json` |
| **DB & Index Sync** | Sets `equation_svg = NULL` in MariaDB; updates `formulas_latex_index.json` | Sets `equation_svg = NULL` in MariaDB; updates `formulas_latex_index.json` |
| **UI Updates** | Outputs CLI status summary | Synchronizes top search bar, drawer textareas, scenario cards, and invokes `MathJax.typesetPromise` |

---

## 3. End-to-End Workflow Architecture

```mermaid
sequenceDiagram
    autonumber
    actor Curator as User / Curator
    participant UI as Equation Explainer Drawer
    participant API as PhysicsController (/physics/api/apply-repair)
    participant Service as FormulaReviewService
    participant Shard as Content Shard JSON (Disk)
    participant DB as MariaDB & LaTeX Index

    Curator->>UI: Clicks "Fix LaTeX" button (optional hint in guidance field)
    UI->>API: POST { url, formula_id, latex, hint }
    API->>Service: repairTarget(target, hint, userId, proseOverrides)
    Service->>Shard: Locate and load shard_[xx].json
    Service->>Service: decorruptLatex(equation)
    Service->>Service: sanitizeProse(proseFields)
    opt Reference Hint Provided
        Service->>Service: Parse Markdown sections & inject into formula fields
    end
    Service->>Shard: Write updated formula JSON to disk (LOCK_EX)
    Service->>DB: UPDATE formulas SET equation_svg = NULL; sync index
    Service-->>API: Return clean formula payload
    API-->>UI: Return JSON { success: true, data: { formula, clean_equation } }
    UI->>UI: Update top equation input & drawer fields
    UI->>UI: Re-render main explanation card & scenario list
    UI->>UI: Execute MathJax.typesetPromise across DOM
    UI-->>Curator: Display success badge ("✓ Repair complete! MathJax synced.")
```

---

## 4. Key Components & Implementation Details

### A. Frontend Payload & State Management ([`public/js/equation_explainer.js`](file:///Users/holobetj/code/gemini/terra/public/js/equation_explainer.js))
* **Button Handler**: `triggerFixLatex()`
* **Headers**: Includes `Content-Type: application/json` and `X-Requested-With: XMLHttpRequest` to ensure clean JSON responses.
* **Payload Structure**:
  ```json
  {
    "url": "http://localhost:8000/physics/equation-explainer?id=boltzmann-factor-for-nuclear-binding-energy-4c8015c1",
    "formula_id": "boltzmann-factor-for-nuclear-binding-energy-4c8015c1",
    "latex": "\\exp\\left(\\frac{B_i - B_j}{k_B T}\\right)",
    "hint": "Interpretation: ... Limits: ...",
    "prose": null
  }
  ```
* **DOM Synchronizations**:
  * `this.latexInput.value = cleanEquation` (Main top search bar)
  * `this.drawerLatexInput.value = cleanEquation` (Drawer equation field)
  * `this.drawerFieldInterpretation.value = f.interpretation` (Drawer prose textareas)
  * `this.renderFormula(f, this.currentSubtopics)` (Main conceptual card & scenario breakdown)
  * `window.MathJax.typesetPromise([this.mathRenderTarget, this.conceptualIntroCard, this.aiScenariosList, this.drawerPreviewTarget])` (Full-page vector typesetting)

---

### B. Controller & Error Handling ([`app/controllers/PhysicsController.php`](file:///Users/holobetj/code/gemini/terra/app/controllers/PhysicsController.php))
* **Endpoint**: `POST /physics/api/apply-repair` (`apiApplyRepair`)
* **Debug Isolation**: Automatically sets `\Tracy\Debugger::$showBar = false` for API/AJAX requests in [`SecurityHeadersMiddleware.php`](file:///Users/holobetj/code/gemini/terra/app/middlewares/SecurityHeadersMiddleware.php) to prevent HTML debug bar injection from polluting JSON response streams.
* **Local Development Authorization**: Permits authenticated Curators/Admins and localhost development instances (`127.0.0.1`, `::1`).

---

### C. Backend Repair Engine ([`app/logic/FormulaReviewService.php`](file:///Users/holobetj/code/gemini/terra/app/logic/FormulaReviewService.php))
* **Target Resolution**: Handles full URLs (`?id=...`, `?latex=...`), formula IDs, and raw LaTeX equation strings.
* **Equation Cleaning (`decorruptLatex`)**:
  * Converts slash differentials to fractions: `dp^\mu/d\tau \to \frac{dp^\mu}{d\tau}`.
  * Standardizes missing fraction macros and unescaped Greek characters.
* **Prose Sanitization (`sanitizeProse`)**:
  * Standardizes mathematical variables into LaTeX math mode: e.g. $B_i$, $B_j$, $k_B T$, $T \to 0\text{ K}$, $T \to \infty$.
  * Removes corrupted TeX artifacts (e.g. `\text{\}`, `extbf`, `\bullet \to \cdot`).
  * Fixes sub-indexed and vector displacement boundaries ($|\mathbf{r}_i - \mathbf{R}_I| \to \infty$).
* **Hint Application**: Automatically parses structured reference sections (`Interpretation:`, `Limits:`, `Symmetry:`, `Definition:`) passed via the drawer guidance box.
* **Data Consistency**:
  * Sanitizes `semantic_variables` keys (stripping stray `$` symbols).
  * Updates disk shards with `JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE`.
  * Sets `equation_svg = NULL` in MariaDB.
  * Synchronizes canonical LaTeX mapping in `app/config/formulas_latex_index.json`.

---

## 5. Verification Protocol

When testing the "Fix LaTeX" button on any formula:

1. **Open Formula URL in Browser**:
   ```
   http://localhost:8000/physics/equation-explainer?id=[formula-id]
   ```
2. **Open Curation Drawer**:
   * Click **"Curate / Suggest Fix"** in the top action bar.
3. **Trigger Fix**:
   * Optionally paste reference text or guidance into the **"Guidance & Context Reference / Hint"** textarea.
   * Click **"Fix LaTeX"**.
4. **Confirm Success**:
   * Progress bar advances to 100% with a green checkmark.
   * Drawer equation and narrative textareas update with sanitized LaTeX.
   * Main equation card (`#math-render-target`) and scenario cards typeset immediately.
   * Inspect the corresponding shard file under `app/config/content/formulas/` to verify disk persistence.
