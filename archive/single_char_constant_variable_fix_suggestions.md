# Architectural Strategy & Proposals: Single-Letter Variable & Constant Handling

> **Context**: Subtopic overview pages (such as `http://localhost:8000/physics/subtopic/classical-mechanics-overview`) contain fundamental single-letter variables and constants (e.g., $v$, $m$, $F$, $E$, $p$, $t$, $c$, $G$). These symbols are critical to physics comprehension, but naive global hyperlinking creates ambiguity (e.g., $v$ linking to vector $\mathbf{v}$ vs. scalar speed $v$ vs. specific volume $v$).

---

## 1. The Core Challenge

1. **High Conceptual Importance vs. Contextual Ambiguity**:
   - Single letters represent foundational quantities ($v$ = velocity/speed, $m$ = mass, $F$ = force, $E$ = energy, $T$ = temperature/tension/period).
   - However, a single letter like **$v$** is inherently ambiguous across physics domains: it can represent a 3D vector ($\mathbf{v}$), a 1D scalar speed ($v$), specific volume ($v$), or wave phase velocity ($v_p$).

2. **The Linking Trap & Clutter**:
   - Directing a user from a generic letter $v$ in Classical Mechanics to a single hardcoded equation URL (e.g., `\mathbf{v}`) can be misleading when the text discusses kinetic energy ($K = \frac{1}{2}mv^2$) or fluid dynamics.
   - Over-linking standalone letters in prose causes visual clutter and "link fatigue".

---

## 2. Proposed Architectural Strategies

### Option A: Contextual Hover Tooltips (Non-Navigational Highlighting) ⭐ *(Recommended)*

- **Concept**:
  Style single-letter symbols with a distinct math variable badge (e.g., `<span class="variable-token">$v$</span>`) instead of a traditional `<a>` hyperlink.
- **User Experience**:
  Hovering over **$v$** in *Classical Mechanics* displays a lightweight popover card:
  - **Current Context**: Velocity Vector ($\mathbf{v}$) or Speed ($v$) $[\text{m/s}]$.
  - **Key Formulas in this Subtopic**:
    - $\mathbf{p} = m\mathbf{v}$ (Linear Momentum)
    - $K = \frac{1}{2}mv^2$ (Kinetic Energy)
    - $\mathbf{a} = \frac{d\mathbf{v}}{dt}$ (Acceleration)
- **Advantages**:
  - Prevents false or rigid redirects to a single hardcoded equation.
  - Delivers instant inline context without requiring the user to leave the subtopic page.

---

### Option B: Subtopic Symbol Legend / "Variables in this Section" Sidebar

- **Concept**:
  Keep body prose text free of clickable links for standalone single letters. Instead, render a dedicated **"Key Quantities & Symbols"** sidebar on the subtopic page.
- **User Experience**:
  In *Classical Mechanics*, a clean sidebar panel lists:
  - $\mathbf{v}$ — Velocity Vector
  - $m$ — Mass
  - $\mathbf{p}$ — Momentum
  - $F$ — Net Force
  - Clicking any symbol in the legend temporarily highlights every equation on the subtopic page where that symbol appears.
- **Advantages**:
  - Keeps prose text clean and readable.
  - Groups variables explicitly by subtopic domain so $v$ is framed as classical velocity rather than thermodynamic specific volume.

---

### Option C: Disambiguated "Symbol Explorer" Modal

- **Concept**:
  Clicking any single-letter symbol opens an interactive **Symbol Explorer** modal dialog.
- **User Experience**:
  The modal presents a disambiguation view:
  1. **Primary Meaning in Classical Mechanics**: Velocity ($\mathbf{v} = \frac{d\mathbf{r}}{dt}$).
  2. **Other Meanings in Physics**: Specific Volume ($v$), Wave Speed ($v$).
  3. **Related Equations**: Direct links to all matching equations in the database.
- **Advantages**:
  - Turns variable ambiguity into an educational exploration feature.
  - Gives users complete agency to choose which specific formula they intended to examine.

---

### Option D: Scoped MathJax Auto-Linking (Strict TeX Delimiters Only)

- **Concept**:
  Only auto-link single letters if they are explicitly wrapped in TeX math delimiters (e.g., `$\mathbf{v}$` or `$v_x$`) AND match a subtopic-specific variable mapping.
- **User Experience**:
  - Plain English words ("a", "I", "in") are never linked.
  - Only formatted math symbols `$\mathbf{v}$` link directly to their primary equation explainer URL.
- **Advantages**:
  - Simple to enforce programmatically via `TerraLexer`.
  - Eliminates false positive links on common English prose letters.

---

## 3. Comparison Matrix

| Option | Readability Impact | Context Accuracy | Implementation Complexity | User Experience |
| :--- | :--- | :--- | :--- | :--- |
| **Option A (Hover Cards)** | High (No blue link clutter) | High (Shows multi-meaning) | Medium | Excellent (Instant inline preview) |
| **Option B (Symbol Legend)** | Very High (Clean prose) | High (Domain-scoped) | Low | Great (Structured overview) |
| **Option C (Symbol Explorer Modal)** | Medium | Very High (Comprehensive) | Medium | Educational & Interactive |
| **Option D (Strict TeX Auto-Link)** | Low-Medium (Still creates links) | Medium | Low | Good (Eliminates English prose bugs) |

---

## 4. Recommended Combined Approach

Combine **Option A (Inline Hover Cards)** for quick reading with **Option B (Subtopic Symbol Legend)**:
1. Subtopic prose stays clean without aggressive link-blue on every single letter.
2. Single-letter symbols get a subtle gold/teal variable badge styling.
3. Hovering gives multi-equation context tailored specifically to the current subtopic without forcing a disruptive page jump.
