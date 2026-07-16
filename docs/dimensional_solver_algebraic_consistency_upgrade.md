# Proposed UX Upgrades: Dimensional Solver & Algebraic Consistency Engine

This document details recommended interface and algorithmic improvements for the **Dimensional Solver & Algebraic Consistency Engine** to enhance readability, usability, and pedagogical value for students and researchers.

---

## 1. Real-time "As-You-Type" Validation & Linting

### The Current Friction
Currently, users must type an expression and click "Analyze" (or press Enter). If a dimensional clash or syntax error occurs, the entire results section is hidden and replaced by a static red error banner.

### Proposed Improvement
* **Asynchronous Inline Checking**: Bind input changes (`input` event listeners) to a debounced parsing routine that checks syntax and dimensions in real time.
* **Inline Syntax Error Highlighting**: If a syntax or dimensional mismatch is detected, show a red wavy underline beneath the offending character or operator (similar to an IDE's squiggly red line).
* **Ghost Preview**: Display a ghosted preview of the resolved dimension vector (e.g. `[Length]` or `[Force]`) directly inside the input box when the expression is valid, before the user hits submit.

---

## 2. Interactive Operator Keyboard / Formula Builder

### The Current Friction
While users can click registered symbols to append them to the input field, they must still use a keyboard to type operators (`*`, `/`, `^`, `(`, `)`). This presents usability hurdles on touch screens or mobile devices.

### Proposed Improvement
* **Mathematical Keyboard Pad**: Add an interactive grid of mathematical utility buttons below the input box:
  * Arithmetic: `+`, `-`, `*`, `/`
  * Grouping: `(`, `)`
  * Exponents: `x²`, `x³`, `xʸ`
  * Roots: `√x`
* Clicking these buttons will insert the corresponding syntax into the active cursor position in the input field.

---

## 3. Visual Parse Tree Hierarchy

### The Current Friction
The derivation steps are currently presented as a sequential list of text descriptions. This makes it difficult to visualize how dimensions accumulate through compound operations.

### Proposed Improvement
* **Interactive Derivation Tree**: Render a visual, hierarchical syntax tree using SVG or Canvas, showing how the equation is parsed.
* **Dynamic Node Styling**: Each junction (node) of the tree represents a sub-expression. Clicking a node will show its local LaTeX representation and its intermediate 5D dimension vector (e.g., displaying `[Mass · Length / Time²]` for a multiplication node before it gets divided by `[Area]`).

```
                  [Length]  <-- Final Result (m)
                     /
                   [ / ]
                  /     \
    [Length³/Time²]     [Length²/Time²]
           /                   \
         [ * ]                 [ ^2 ]
        /     \                  |
     [ G ]   [ M ]             [ c ]
```

---

## 4. Intelligent Dimensional Synthesis (Recommender)

### The Current Friction
If the user inputs an equation that is dimensionally mismatched, the parser simply fails and stops execution.

### Proposed Improvement
* **Dimensional Vector Difference Solver**: When an algebraic mismatch (e.g., $A + B$) is encountered, calculate the vector difference between the dimensions of $A$ and $B$:
  $$\Delta \mathbf{d} = \mathbf{d}_A - \mathbf{d}_B$$
* **Recommender Suggestions**: Suggest registered constants or variables from the catalog that can resolve the mismatch.
  * *Example*: If the user inputs `E + p` (Energy + Momentum), the engine calculates the difference vector as $[0, 1, -1, 0, 0]$ (Velocity) and suggests: *"Dimensional mismatch: Energy cannot be added to Momentum. Try multiplying Momentum by c (Speed of Light) or v (Velocity) to make the terms compatible."*

---

## 5. Transcendental Function Checking

### The Current Friction
Trigonometric, logarithmic, and exponential functions are currently parsed as plain variables or flag syntax errors.

### Proposed Improvement
* **Function Recognition**: Update tokenization to identify functions like `sin()`, `cos()`, `tan()`, `exp()`, `log()`, and `ln()`.
* **Argument Dimension Validation**: Automatically verify that the argument of any transcendental function is strictly **dimensionless** ($[0,0,0,0,0]$). 
  * If a user types `sin(t)`, flag: *"Dimensional error: The argument of trigonometric function sin() must be dimensionless. Found 't' with dimension [Time]."*
