# Usefulness of the Local Variable Editor in Equation Explainer

This document outlines the design philosophy and use cases for the local variable/constant editing feature built into the client-side Equation Explainer frontend.

---

## 1. Feature Architecture and Scoping

When a user edits a variable name, standard unit, or description via the UI's built-in editor:
* **Storage Location**: The customization is saved on the user's local machine in `localStorage` under the key prefix `physics_explainer_custom_{symbol}` (e.g. `physics_explainer_custom_A`).
* **Session Persistence**: Unlike standard session-based memory, `localStorage` is persistent. The custom definition survives tab closures, browser restarts, and system reboots.
* **Symbol-Level Scope**: The override is applied globally by the symbol name itself. Thus, custom edits for a specific symbol (e.g., $A$) will be loaded for any equation containing that symbol within the user's browser.
* **Server Integrity**: Edits do not modify the server-side sharded JSON database (`app/config/content/formulas/`) or the `formulas` relational database table.

---

## 2. Core Use Cases

### A. Heuristic Correction for Custom Equations
When a student or content editor inputs a **custom, unregistered LaTeX equation** (which is not pre-registered in the database), the explainer falls back to a local heuristic parsing engine. 
* **The Problem**: A symbol like $A$ is highly ambiguous in physics—it could represent *Area* (default SI unit: $\text{m}^2$) or *Vector Potential* (default SI unit: $\text{T}\cdot\text{m}$), among others. Heuristics default to the most statistically common variable mapping (e.g., Area).
* **The Solution**: The local editor allows users analyzing custom equations to override the heuristic default so that the breakdown cards, hover panels, and tooltips display correct physical concepts.

### B. Personalized Study Notes & Lecture Alignment
The digital encyclopedia is designed for university-level physics students.
* **The Problem**: Standard textbook definitions of parameters or operators can sometimes be too abstract or verbose for a student's immediate study needs.
* **The Solution**: Students can edit descriptions to simplify definitions, anchor them to specific course lecture notes, or align notations (e.g., specifying that in their class, $d$ stands for a specific distance constraint).

### C. Live Sandbox Simulation Integration
The Equation Explainer dynamically maps parsed variables to the controls of the **Interactive Simulation Sandbox** widget on the page.
* **The Problem**: Simulator control panels and sliders default to generic names.
* **The Solution**: Editing the variable name or units in the breakdown list dynamically propagates the updated labels to the simulation controls and tooltips, providing a personalized simulation workshop.

### D. Rapid Content Prototyping for Developers
Content curators and developers drafting new physics nodes can use the interactive editor as a preview tool.
* **The Problem**: Writing JSON configuration structures directly is error-prone and hard to visualize.
* **The Solution**: Developers can load their draft equation in the Equation Explainer, refine the variable names, descriptions, and units in the GUI to see how the cards typeset, and copy the refined copy directly into the database JSON shards when ready.
