# Project Terra: Physics Lab Landing Page Card Layout Ideas
**Date**: August 7, 2026  
**File**: `docs/_landing_layout_ideas.md`  
**Purpose**: Architectural design proposals for transforming the Physics Lab homepage (`http://localhost:8000/`) card layout and hero aesthetic while preserving the interactive particle canvas background (`/js/hero_canvas.js`).

---

## 🎨 1. Core Design System Alignment

All proposed card layouts build upon the **Cosmic Obsidian Design System**:
- **Background**: Deep obsidian radial gradient (`background-image: radial-gradient(circle at 50% 0%, #111026 0%, #030712 75%); background-attachment: fixed;`).
- **Card Materials**: Translucent Obsidian Glass (`rgba(15, 23, 42, 0.35)` with `backdrop-filter: blur(12px)` and `border: 1px solid rgba(255, 255, 255, 0.06)`).
- **Neon Spectrum Highlights**: Hover highlights using neon category colors (`#10b981` Classical, `#00d2ff` Electromagnetism, `#8b5cf6` Relativity, `#ff4e88` Quantum, `#f97316` Astrophysics).
- **Typography**: Space Grotesk (headings) and Inter (body text).

---

## 🌟 2. Four Card Layout Options

### Option 1: "Featured Asymmetric Hero Grid" *(Recommended)*
Instead of 12 identical-looking box cards in a uniform grid, give the page **visual rhythm and hierarchy**:

- **3 Flagship Mega-Cards (Double-Width)**:
  - *Quantum Physics*, *General Relativity*, and *Classical Mechanics* get prominent 2-column cards featuring a dark LaTeX equation banner (e.g., $i\hbar \frac{\partial\Psi}{\partial t} = \hat{H}\Psi$) and quick subtopic pills (`[ Wave Functions ]`, `[ Uncertainty ]`, `[ QFT ]`).
- **9 Standard Compact Tiles**:
  - Surrounding standard glass tiles for the other disciplines, creating a rich, editorial magazine-style layout.

---

### 💎 Option 2: "Holographic Dossier Cards" *(Enriched Card Anatomy)*
Keep a clean multi-column grid, but transform what lives *inside* each card so it feels like a high-tech scientific dossier:

```
┌─────────────────────────────────────────────────────────┐
│ ⚛️  QUANTUM PHYSICS                 [ HIGH-ENERGY BADGE ]│
│ ─────────────────────────────────────────────────────── │
│  $$i\hbar \frac{\partial\Psi}{\partial t} = \hat{H}\Psi$$│
│                                                         │
│ Deconstruct wave-particle duality, Hilbert spaces, and  │
│ matrix mechanics.                                       │
│                                                         │
│  [ Wave Function ]  [ Uncertainty ]  [ Schrödinger ]    │
│ ─────────────────────────────────────────────────────── │
│  Explore Hub ───────────────>                           │
└─────────────────────────────────────────────────────────┘
```
- **Top Header**: Category icon + glowing category badge (`QUANTUM`, `FIELDS`, `RELATIVITY`).
- **Central Equation Banner**: Dark glass inset box showcasing the defining LaTeX equation of that field.
- **Subtopic Quick-Tags**: 3-4 clickable subtopic pills inside the card for 1-click navigation.
- **Hover Effect**: Card outline lights up in the category's neon accent color (`#ff4e88` for Quantum, `#8b5cf6` for Relativity).

---

### 🗂️ Option 3: "Grouped Discipline Lanes" *(Categorized Rows)*
Break the monolithic 12-card grid into **3 curated horizontal discipline lanes**:

1. 🟢 **Macroscopic & Classical Realms**
   - *Classical Mechanics*, *Thermodynamics & Stat Mech*, *Fluid Dynamics*
2. 🟣 **Fields, Waves & Spacetime**
   - *Electromagnetism*, *General Relativity*, *Theoretical Physics*, *Math Methods*
3. 🌸 **Quantum, Particles & Cosmos**
   - *Quantum Mechanics*, *Standard Model*, *Condensed Matter*, *Astrophysics*, *Philosophy*

- Each lane has a subtle category header and compact horizontal cards, making browsing much faster and organized.

---

### 🧩 Option 4: "Compact Minimalist Matrix with Live Hover Drawers"
- A sleek, high-density 4-column matrix of compact glass cards.
- Clicking or hovering any card smoothly expands a bottom drawer revealing its full description, foundational equations, and related lab tools.

---

## 🌌 3. Complementary Hero & Page Enhancements

1. **Particle Canvas Integration (`/js/hero_canvas.js`)**:
   - Retain the interactive hero particle canvas where particles bounce and gravitate toward the mouse cursor.
2. **Glassmorphic Hero Search Bar**:
   - Overlay a translucent spotlight search input on top of the hero particle canvas:
     `[ 🔍 Search 3,000+ physics equations, constants, or derivations...   ⌘K ]`
3. **Live Metric Pills**:
   - Floating glass badges: `[ ⚛️ 3,000+ Equations ]` • `[ 🌌 12 Physics Faculties ]` • `[ 🧰 9 Interactive Tools ]`.
4. **Flagship Lab Tools Quick-Access Ribbon**:
   - Horizontal ribbon between Hero and Curriculum grid for quick access to *Dimensional Solver*, *Legendre Transformer*, *Noether's Vault*, *Equation Explainer*, and *Anthropic Tuner*.

---

## 📊 Summary Matrix

| Layout Style | Best For... | Visual Vibe |
| :--- | :--- | :--- |
| **Option 1: Asymmetric Hero Grid** | Creating strong visual interest & featuring core subjects | Editorial, Magazine-like |
| **Option 2: Holographic Dossiers** | Displaying equations & subtopic tags directly on cards | High-Tech, Information-Rich |
| **Option 3: Grouped Lanes** | Clear organization by physical scale (Classical vs Quantum) | Clean, Structured |
| **Option 4: Compact Matrix** | Minimalist view with high density | Sleek, Modern Dashboard |
