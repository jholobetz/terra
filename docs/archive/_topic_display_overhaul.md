# Project Terra: Topic Display Page Visual Overhaul Specification
**Date**: August 7, 2026  
**File**: `docs/_topic_display_overhaul.md`  
**Purpose**: Design proposals to transform Topic Hub pages (e.g. `/physics/topic/quantum-physics`) into high-impact, interactive scientific command centers aligning with the Cosmic Obsidian Design System.

---

## 🏛️ Executive Summary

Topic Hub pages serve as the main entry point into a scientific discipline (e.g. *Quantum Physics*, *General Relativity*, *Classical Mechanics*). This specification outlines **4 core visual and architectural proposals** to elevate the topic display from static lists into a modern, interactive dashboard.

---

## 🌌 1. Cosmic Command Header with Quick Metric Chips

Upgrade the standard header into a **Glassmorphic Command Header**:

- **Category Neon Glow Backdrop**: The header background receives a subtle glowing radial tint matching the domain (e.g. Neon Pink `#ff4e88` for *Quantum*, Deep Violet `#8b5cf6` for *Relativity*, Emerald `#10b981` for *Classical*).
- **Interactive Metric Chips**: A row of translucent glass badges right below the title:
  - `[ ⚛️ 4 Concept Pillars ]`
  - `[ 📜 28 Subtopics ]`
  - `[ 📐 142 Equations ]`
  - `[ 🌉 3 Cross-Bridges ]`
- **Primary Action Bar**:
  - `[ 🚀 Jump to Overview ]`
  - `[ 🧰 Launch Topic Workbench ]`
  - `[ 📜 Filter Formulas ]`

---

## 🗂️ 2. Interactive Pillar Navigator Tabs

Currently, all concept pillars stack vertically in one long scrolling view. Introduce a **Pillar Navigator Bar**:

- **Pillar Filter Tabs**: Allow visitors to switch between concept pillars smoothly using sleek glass tabs:
  - `[ All Pillars ]`
  - `[ 1. Foundational Quantum ]`
  - `[ 2. Wave Mechanics & Operators ]`
  - `[ 3. Field Theory ]`
- **Benefits**:
  - Eliminates long vertical scrolling fatigue.
  - Helps users jump directly into specific sub-fields.

---

## 💎 3. Glassmorphic Concept Cards (`.concept-card` Overhaul)

Transform the subtopic cards inside each pillar into **Holographic Concept Cards**:

```
┌──────────────────────────────────────────────────────────┐
│  FRONTIER LEVEL                                          │
│  The Schrödinger Equation                                │
│ ──────────────────────────────────────────────────────── │
│         $$i\hbar \frac{\partial\Psi}{\partial t} = \hat{H}\Psi$$         │
│ ──────────────────────────────────────────────────────── │
│  Deconstruct wave-particle duality, state vectors, and   │
│  time evolution in Hilbert space.                        │
│                                                          │
│  Explore Subtopic Hub ─────────────────────────────────> │
└──────────────────────────────────────────────────────────┘
```

### Key Design Enhancements:
1. **Level Accent Borders**:
   - 🟢 `Foundational`: Soft Emerald border highlight (`#10b981`)
   - 🔷 `Analytical`: Electric Cyan border highlight (`#00d2ff`)
   - 🟣 `Frontier`: Deep Violet/Fuchsia border highlight (`#d946ef`)
2. **Dark Glass LaTeX Inset**: Render the subtopic's hero LaTeX equation inside a centered, dark glass inset box.
3. **Whole Card Clickable**: Clicking anywhere on the concept card navigates directly to `/physics/subtopic/{slug}`.

---

## 🌉 4. Visual Interconnection Node Matrix (Cross-Bridges)

Transform plain text cross-disciplinary bridges into **Interconnection Glass Nodes**:

- Visual cards showing how Quantum Physics bridges into *Classical Mechanics* (Correspondence Principle), *Electromagnetism* (QED), and *Philosophy of Physics* (Measurement Problem).
- Hovering over a bridge node illuminates the connection path with animated glowing lines.

---

## 📊 Summary Comparison

| Proposal | Primary Benefit | Visual Impact |
| :--- | :--- | :--- |
| **1. Cosmic Command Header** | Instant domain metrics & high-impact visual identity | High |
| **2. Pillar Navigator Tabs** | Organized filtering; eliminates long vertical scrolling | Medium/High |
| **3. Glassmorphic Concept Cards** | Enriches subtopic cards with LaTeX insets & level glows | Very High |
| **4. Visual Bridge Matrix** | Visualizes scientific interconnections across fields | High |
