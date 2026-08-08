# Project Terra: Physics Lab 3D Translucent Cubes Halo Menu Specification
**Date**: August 7, 2026  
**File**: `docs/_new_front_menu.md`  
**Purpose**: Architectural design specification for the 3D Translucent Glass Cubes Halo Orbit system, replacing traditional 2D cards on the Physics Lab homepage (`http://localhost:8000/`).

---

## 🏛️ Executive Concept

Instead of flat 2D cards, the 12 main physics topics are represented as **3D Translucent Glass Cubes** strung along a tilted cosmic halo wire orbit that appears to lay almost flat in 3D space (`transform: rotateX(72deg)`).

```
                    [ 🌌 Interactive Tilted Halo Orbit ]
                                  
          ┌── (Back Cubes: Scaled 0.72x, Translucent) ──┐
         /                                                \
        /   [Cube] ─── [Cube] ─── [Cube] ─── [Cube]        \  <-- Glowing Tilted Wire
       /                                                    \     (rotateX: 72deg)
      └─── (Front Cubes: Scaled 1.16x, Neon Illuminated) ───┘
```

---

## 🪐 1. Visual & Spatial Architecture

### 1. The Glowing Halo Wire Orbit
- A glowing, subtle cyan/purple elliptical ring (`stroke: rgba(100, 255, 218, 0.25)`, width `880px`, height `260px`) tilted at a ~72° angle so it appears to lay almost flat in 3D space (`perspective: 1200px`, `transform-style: preserve-3d`).
- Micro-particles and energy pulses flow continuously along the wire ring like electric current.

### 2. The 12 Translucent Glass Cubes
- Each cube represents one of the 12 physics topics.
- **CSS 3D Construction**: Built with 6 glass faces (`transform-style: preserve-3d`) using obsidian glass material (`background: rgba(15, 23, 42, 0.45)`, `backdrop-filter: blur(12px)`).
- **Neon Edge Spectrum**: Cube edges light up in that topic's neon category accent color:
  - *Quantum Physics* $\rightarrow$ Neon Pink (`#ff4e88`)
  - *General Relativity* $\rightarrow$ Deep Violet (`#8b5cf6`)
  - *Electromagnetism* $\rightarrow$ Electric Blue (`#00d2ff`)
  - *Classical Mechanics* $\rightarrow$ Emerald Green (`#10b981`)
  - *Astrophysics* $\rightarrow$ Solar Amber (`#f97316`)
- **Suspended Holographic LaTeX Core**: Inside each translucent cube, the topic's defining LaTeX equation ($i\hbar \frac{\partial\Psi}{\partial t} = \hat{H}\Psi$) floats in 3D space like an illuminated hologram.

---

## 🎛️ 2. Interaction & Physics Controls

- **Continuous Orbital Drift**: The 12 cubes slowly orbit along the halo wire at a gentle, smooth pace (`speed = 0.0015`).
- **Mouse Attraction & Hover Elevate**:
  - As the cursor approaches a cube, it is magnetically attracted to the mouse.
  - Hovering over a cube smoothly rotates it upright toward the viewer (`rotateX(0deg)`), enlarging it to full focus while dimming the non-hovered cubes.
- **Depth-of-Field Scaling**:
  - Cubes on the back half of the halo loop appear smaller (scale 0.72x, opacity 0.4), while cubes at the front appear large and crisp (scale 1.16x, full opacity).
- **Drag & Touch to Spin**: Dragging left/right with your mouse or touch swipe spins the halo orbit smoothly.
- **Click to Explore**: Clicking any cube instantly navigates to that Topic Hub (`/physics/topic/quantum-physics`).

---

## ⚡ 3. Technical Implementation Options

1. **Option A: Pure CSS 3D Transforms & Canvas Physics** *(Implemented)*:
   - Uses native HTML 3D CSS transforms (`perspective: 1200px`, `transform-style: preserve-3d`) driven by a ~3KB JavaScript orbital loop (`public/js/halo_orbit.js`). 60 FPS performance, lightweight, and zero external dependencies.
2. **Option B: Three.js 3D WebGL Engine**:
   - Real-time WebGL glass refraction, spatial point lighting, and dynamic shadows as cubes spin around the halo wire.

---

## 📑 4. Significant Layout & Feature Refinements

1. **Removal of Redundant 2D Cards Grid**:
   - Eliminated the flat 2D topic cards below the 3D halo orbit stage, making the 3D Translucent Glass Cubes Halo Orbit the sole, centerpiece navigation system.
2. **Expanded 3D Stage Headroom**:
   - Expanded container height (`height: 500px`), halo ring ellipse (`880px` $\times$ `260px`), and vertical padding (`margin-bottom: 80px`), allowing cubes to float, orbit, and elevate without crowding.
3. **Streamlined Hero Architecture**:
   - Removed section headers above the halo orbit (`The Physics Manifold Orbit` / instruction text) and removed the hero search box overlay under the title for a clean, unobstructed presentation.
4. **Dynamic Random Discovery CTA (`/physics/random`)**:
   - Replaced static "Start Exploring" link with `🎲 Start Exploring` pointing to `/physics/random`, which queries MariaDB/`search_index.json` to launch a fresh random physics subtopic on every click.

---

## 🔬 5. Focus Fighting & "Twitchiness" Diagnostic & Stabilization Plan

### Root Cause Analysis:
1. **Bounding Box Thrashing (`cube.offsetLeft`)**:
   - In `halo_orbit.js`, `mouseenter` used static layout offsets `cube.offsetLeft` / `cube.offsetTop` instead of the dynamic orbital coordinates $(x, y)$. This caused the card to snap back to its origin, immediately triggering `mouseleave`, creating a rapid hover flicker loop.
2. **Overlapping 3D Hitbox Collisions**:
   - Cubes passing behind front cubes in 3D screen space triggered competing `pointer-events`, causing mouse focus to fight between overlapping cards.
3. **CSS Transition vs. RAF Interpolation**:
   - CSS `transition: transform 0.4s` running simultaneously with `requestAnimationFrame` 60 FPS updates caused micro-stutter during ambient drift.
4. **MathJax DOM Recalculation on Hover**:
   - Invoking `MathJax.typesetPromise([cube])` inside `mouseenter` created thread freezes during fast mouse movements.

### 🛠️ 4-Point Stabilization Plan:
1. **Pin Focus to Current Orbital Coordinates $(x_i, y_i)$**:
   - Preserve computed 3D orbital coordinates $(x_i, y_i)$ when focused and elevate only the $z$-axis (`translate3d(x, y, 160px) scale(1.25)`).
2. **Pointer-Events Shielding**:
   - Apply `pointer-events: none` to background cubes while a front card is actively focused.
3. **On-Demand CSS Transitions**:
   - Keep `transition: none` during normal orbital drift and apply `transition: transform 0.3s` only during hover state changes.
4. **Pre-render MathJax**:
   - Typeset MathJax equations on page load rather than dynamically inside hover events.

---

## 🌀 6. Continuous Orbital Rotation Options During Active Selection

Architectural proposals for maintaining orbital simulation drift even while a card is selected or hovered:

1. **Option A: Dynamic Orbital Tracking (Recommended)**:
   - The selected card stays elevated (`z: 160px`) and upright facing the viewer (`scale(1.25)`, `rotateX(0deg)`), but continues floating along the orbital track in sync with the rest of the ring as `baseAngle += speed` updates every frame.
2. **Option B: Center Stage Detachment**:
   - The background halo ring of 11 cubes continues orbiting continuously, while the selected cube detaches from its orbital slot and glides to fixed center stage (`translate3d(0, 0, 220px)`), returning to its slot upon unselect.
3. **Option C: Slow-Motion Kinetic Drift**:
   - When a card is selected, the orbital speed decelerates smoothly to 30% speed (`speed * 0.3`), allowing comfortable reading while preserving subtle background motion.
