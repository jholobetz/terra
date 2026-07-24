# One-Click Gemini AI Formula Definition Engine Architecture

**Document ID**: `docs/one_button_formula_definition.md`  
**Date**: July 24, 2026  
**Status**: Architectural Specification & Implementation Roadmap  
**Project**: Terra Physics Encyclopedia & Knowledge Graph Engine  

---

## Executive Summary

As Project Terra expands across Physics, Chemistry, and Biology, encountering mathematical expressions or theoretical identities not yet registered in pre-compiled database shards (such as $G(\mathbf{r}, \mathbf{r}')$ — Position-Space Green's Function) is a natural occurrence. 

Rather than requiring manual form inputs or complex AST heuristic rules, this specification details the **One-Click Gemini AI Formula Definition Engine**. In a single-user / developer environment, clicking a **`[ ✨ Define ]`** button directly triggers Gemini AI to research, draft, validate, and persist a complete, academically rigorous formula definition into permanent database shards in real time.

---

## User Experience Lifecycle (Steps A through E)

```
[Click Undefined Equation on Subtopic] (A)
           │
           ▼
[Navigates to /physics/equation-explainer?latex=G(\mathbf{r}, \mathbf{r}')] (B)
           │
           ▼
[Title renders: "Custom Physical Relation"] (C)  ──►  [ ✨ Define ] Button Visible (D)
                                                          │
                                                          ▼ (User Clicks "Define") (E)
                                             [Spinner: "Gemini AI researching equation..."]
                                                          │
                                                          ▼
                                             [POST /physics/api/define-formula]
                                                          │
                                                          ▼
                                             [Appends to shard_XX.json & Syncs DB]
                                                          │
                                                          ▼
                                             [UI Live-Updates to Full Definition]
```

### Detailed Step-by-Step Flow:

1. **Step A & B (Navigation)**: The user clicks on any undefined equation (e.g. $G(\mathbf{r}, \mathbf{r}')$) across subtopic pages. The browser navigates directly to the full Equation Explainer workbench: `/physics/equation-explainer?latex=G(\mathbf{r}, \mathbf{r}')`.
2. **Step C (Default Fallback Display)**: Because $G(\mathbf{r}, \mathbf{r}')$ is not yet in pre-compiled JSON shards, the page renders with:
   - **Title**: `Custom Physical Relation`
   - **Badge**: `UNREGISTERED / LIVE ANALYSIS`
3. **Step D (The "Define" Button)**: Positioned directly to the right of `Custom Physical Relation` in the header panel is an accent-styled button: **`[ ✨ Define ]`**.
4. **Step E (One-Click AI Generation & Persistence)**:
   - Selecting **`Define`** updates the button state to an animated spinner: *`✨ Gemini AI researching equation...`*.
   - An asynchronous request (`POST /physics/api/define-formula`) passes the LaTeX string to the backend.
   - The backend queries Gemini AI using an engineered prompt requiring Terra's exact Platinum Formula JSON Schema.
   - The server validates the JSON response, appends the formula to the active shard (`shard_XX.json`), and executes `PhysicsService::performSync()` / `cli_sync.php`.
   - The UI updates dynamically **without a full page reload**, replacing `Custom Physical Relation` with **Position-Space Green's Function** and populating all cards, semantic variables, and Knowledge Graph edges.

---

## Engineered Gemini AI System Prompt & Required Schema

To ensure generated formulas seamlessly match all existing 9,600+ Platinum formulas in Terra, the prompt sent to Gemini AI enforces strict JSON formatting:

### System Prompt & Input Payload
```text
SYSTEM PROMPT:
You are an expert theoretical physics knowledge architect for Project Terra.
Analyze the provided LaTeX equation and generate a complete, academically rigorous formula definition matching the EXACT JSON schema below. Output ONLY valid raw JSON. Do not include markdown codeblocks or commentary outside the JSON object.

LaTeX Input: "G(\mathbf{r}, \mathbf{r}')"
```

### Required Output JSON Schema
```json
{
  "id": "greens-function-position-space",
  "title": "Position-Space Green's Function",
  "equation": "G(\\mathbf{r}, \\mathbf{r}')",
  "conceptual_definition": "An impulse response or fundamental solution to a linear differential operator in field theory.",
  "intuitive_summary": "Represents the physical field response at position r caused by a localized point source located at r'.",
  "interpretation": "Solves linear inhomogeneous partial differential equations (L G = \\delta) by convoluting the Green's function with the source density distribution.",
  "symmetry_origin": "Translational invariance in homogeneous space implies G(\\mathbf{r}, \\mathbf{r}') = G(\\mathbf{r} - \\mathbf{r}').",
  "limits_and_boundary": "Satisfies boundary conditions (e.g. Dirichlet or Neumann) on physical surface boundaries.",
  "unit_system": "SI",
  "parent_formula_id": "poisson-equation-electrostatics",
  "derivation_type": "DERIVED_FROM",
  "status": "published",
  "semantic_variables": {
    "G": {
      "name": "Green's Function",
      "unit": "m^{-1}",
      "description": "Field propagator or impulse response function"
    },
    "\\mathbf{r}": {
      "name": "Observation Position Vector",
      "unit": "m",
      "description": "Field evaluation coordinate"
    },
    "\\mathbf{r}'": {
      "name": "Source Position Vector",
      "unit": "m",
      "description": "Source location coordinate"
    }
  }
}
```

---

## Backend API Specification (`POST /physics/api/define-formula`)

### Endpoint Details
- **URL**: `/physics/api/define-formula`
- **Method**: `POST`
- **Payload**: `{ "latex": "G(\\mathbf{r}, \\mathbf{r}')" }`
- **Response**: `{ "success": true, "formula": { ... } }`

### Backend Controller & Service Execution Logic:

```
[REST API Call: POST /physics/api/define-formula]
                   │
                   ▼
[Invoke Gemini AI API via SDK / HTTP client]
                   │
                   ▼
[Validate JSON Schema & Escape Backslashes]
                   │
                   ▼
[Locate Active Shard: app/config/content/formulas/shard_XX.json]
                   │
                   ▼
[Append Formula JSON & Save to File]
                   │
                   ▼
[Execute php scripts/cli_sync.php / performSync()]
                   │
                   ▼
[Return { success: true, formula: [...] } to Frontend]
```

---

## Key Advantages

1. **Zero Manual Entry**: No forms, textareas, or manual variable mapping required.
2. **Zero Escaping Errors**: Eliminates double-backslash syntax errors common in manual JSON editing.
3. **Instant Persistence**: Generated definitions are immediately written to disk and MariaDB, ensuring that future visits across any subtopic page load the official definition instantly.
4. **Full Knowledge Graph Wiring**: Gemini AI automatically identifies parent laws (`parent_formula_id`) and derivation types (`derivation_type`), integrating the new formula into Terra's global Knowledge Graph network.
