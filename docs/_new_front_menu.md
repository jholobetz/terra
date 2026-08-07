# Project Terra: Physics Lab 3D Translucent Cubes Halo Menu Specification
**Date**: August 7, 2026  
**File**: `docs/_new_front_menu.md`  
**Purpose**: Architectural design specification for the 3D Translucent Glass Cubes Halo Orbit system, replacing traditional 2D cards on the Physics Lab homepage (`http://localhost:8000/`).

---

## 🏛️ Executive Concept

Instead of flat 2D cards, the 12 main physics topics are represented as **3D Translucent Glass Cubes** strung along a tilted cosmic halo wire orbit that appears to lay almost flat in 3D space (`transform: rotateX(75deg)`).

```
                    [ 🌌 Interactive Tilted Halo Orbit ]
                                  
          ┌── (Back Cubes: Scaled 0.7x, Translucent) ──┐
         /                                                \
        /   [Cube] ─── [Cube] ─── [Cube] ─── [Cube]        \  <-- Glowing Tilted Wire
       /                                                    \     (rotateX: 75deg)
      └─── (Front Cubes: Scaled 1.1x, Neon Illuminated) ────┘
```

---

## 🪐 1. Visual & Spatial Architecture

### 1. The Glowing Halo Wire Orbit
- A glowing, subtle cyan/purple elliptical ring (`stroke: rgba(100, 255, 218, 0.25)`) tilted at a ~75° angle so it appears to lay almost flat in 3D space (`perspective: 1200px`, `transform-style: preserve-3d`).
- Micro-particles and energy pulses flow continuously along the wire ring like electric current.

### 2. The 12 Translucent Glass Cubes
- Each cube represents one of the 12 physics topics.
- **CSS 3D / WebGL Construction**: Built with 6 glass faces (`transform-style: preserve-3d`) using obsidian glass material (`background: rgba(15, 23, 42, 0.45)`, `backdrop-filter: blur(12px)`).
- **Neon Edge Spectrum**: Cube edges light up in that topic's neon category accent color:
  - *Quantum Physics* $\rightarrow$ Neon Pink (`#ff4e88`)
  - *General Relativity* $\rightarrow$ Deep Violet (`#8b5cf6`)
  - *Electromagnetism* $\rightarrow$ Electric Blue (`#00d2ff`)
  - *Classical Mechanics* $\rightarrow$ Emerald Green (`#10b981`)
  - *Astrophysics* $\rightarrow$ Solar Amber (`#f97316`)
- **Suspended Holographic LaTeX Core**: Inside each translucent cube, the topic's defining LaTeX equation ($i\hbar \frac{\partial\Psi}{\partial t} = \hat{H}\Psi$) floats in 3D space like an illuminated hologram.

---

## 🎛️ 2. Interaction & Physics Controls

- **Continuous Orbital Drift**: The 12 cubes slowly orbit along the halo wire at a gentle, smooth pace (or respond to mouse drag to spin the ring).
- **Mouse Attraction & Hover Elevate**:
  - As the cursor approaches a cube, it is magnetically attracted to the mouse.
  - Hovering over a cube smoothly rotates it upright toward the viewer (`rotateX(0deg)`), enlarging it to full focus while dimming the non-hovered cubes.
- **Depth-of-Field Scaling**:
  - Cubes on the back half of the halo loop appear smaller (scale 0.7x, opacity 0.5), while cubes at the front appear large and crisp (scale 1.15x, full opacity).
- **Click to Explore**: Clicking any cube instantly navigates to that Topic Hub (`/physics/topic/quantum-physics`).

---

## ⚡ 3. Technical Implementation Options

1. **Option A: Pure CSS 3D Transforms & Canvas Physics** *(Recommended)*:
   - Uses native HTML 3D CSS transforms (`perspective: 1200px`, `transform-style: preserve-3d`) driven by a ~3KB JavaScript orbital loop. 60 FPS performance, lightweight, and zero external dependencies.
2. **Option B: Three.js 3D WebGL Engine**:
   - Real-time WebGL glass refraction, spatial point lighting, and dynamic shadows as cubes spin around the halo wire.
