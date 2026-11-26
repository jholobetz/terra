# 🎛️ Cosmic Instrument — Universal UI Theme & Template

> **Status**: Active Opt-In Design Standard (Per-Tool & Per-Simulation Adoption — Never Mass-Applied Blindly)  
> **Created**: 2026-11-26  
> **Opt-In Stylesheet**: [`public/css/workbench_theme.css`](../public/css/workbench_theme.css) *(load per route via `'extra_css' => ['workbench_theme.css']`)*  
> **Companion Doc**: [`docs/optics.md`](optics.md) *(Audience & Academic Credibility)*

---

## 1. Design Philosophy

Every interactive workbench and simulation in Physics Lab (and future Chemistry / Mathematics Lab manifolds) should feel like a **precision desktop scientific instrument**, not a marketing landing page:

1. **Above-the-Fold Immediacy**: Keep the header compact (~52 px) so the live canvas, symbolic transformation, or comparison grid appears right at the top of a laptop screen.
2. **Live-on-Load, Result-First**: Never greet the visitor with an empty placeholder wall. Auto-compute or auto-select the flagship preset on load, and put the primary result (`L ⟹ H`, `Form A ⟺ Form B`, or live simulation) at the top of the right stage.
3. **One-Click Exploration**: Pair sliders and tabs with low-friction affordances (`⇄ Compare Side-by-Side`, `⚡ Break / Restore Symmetry`, `Copy LaTeX`, `Reset`) and a live hover/drag context bar instead of repeating paragraphs of helper text under every control.
4. **Overflow-Safe Precision**: Every split grid uses `minmax(0, 1fr)` + `min-width: 0` on the right stage, and every math well / table uses `overflow-x: auto` so wide LaTeX formulas never push past the viewport edge.

---

## 2. Core Design Tokens

| Token / Element | Standard Value |
| :--- | :--- |
| **Max Container Width** | `1260px` (`padding-top: 6px`) |
| **Command Header (`<h1>`)** | `1.65rem`, `Space Grotesk` 700, `line-height: 1.15`, subtle gradient (`#ffffff` → `--theme-color`) |
| **Header Tagline (`<p>`)** | `0.88rem`, `var(--text-muted)`, stacked directly under `<h1>` (`gap: 4px`, `margin-bottom: 16px`, `1px solid rgba(255,255,255,0.07)` bottom border, **no badge clutter**) |
| **Split-Rail Grid** | `grid-template-columns: 285px minmax(0, 1fr)` (`275px–310px` rail), `gap: 20px`, collapses to `1fr` at `≤ 960px` |
| **Sticky Left Rail** | `position: sticky; top: 84px;` (resets to `static` at `≤ 960px`) |
| **Glass Card Surface** | `background: rgba(15, 23, 42, 0.42); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 14px; padding: 18px–20px; backdrop-filter: blur(16px);` |
| **Math / Canvas Well** | `background: rgba(2, 6, 23, 0.75); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px–10px;` |
| **Domain Theme Variables** | `--theme-color`, `--theme-bg-color`, `--theme-border-color` (set on `.wb-container` or `.wb-stage-card`) |

---

## 3. Opt-In Starter Template (`.wb-*` Classes)

Load the shared opt-in stylesheet in `PhysicsController.php`:
```php
$this->renderWithLayout('physics/my_workbench', [
    'title' => 'My Workbench',
    'extra_css' => ['workbench_theme.css'],
]);
```

Minimal semantic HTML skeleton:
```html
<div class="wb-container" style="--theme-color: #38bdf8; --theme-bg-color: rgba(56, 189, 248, 0.10); --theme-border-color: rgba(56, 189, 248, 0.35);">
    <header class="wb-header">
        <h1>Workbench Title</h1>
        <p class="wb-tagline">Concise one-line physical purpose stacked directly under the title.</p>
    </header>

    <div class="wb-grid">
        <aside class="wb-rail" aria-label="Workbench Controls">
            <div class="wb-card wb-rail-card">
                <div class="wb-card-head">
                    <h2>Controls</h2>
                    <button type="button" class="wb-btn-mini">Reset</button>
                </div>
                <!-- Compact presets / 2-line dial rows -->
                <div class="wb-context-bar" aria-live="polite">
                    Hover or drag any control to inspect its physical role.
                </div>
            </div>
        </aside>

        <div class="wb-stage">
            <div class="wb-card">
                <div class="wb-stage-top">
                    <div class="wb-tabs"><!-- Tab buttons --></div>
                    <span class="wb-status-pill is-ok">✓ Active</span>
                </div>

                <!-- Optional Dual / Hero Comparison (A => B or A <=> B) -->
                <div class="wb-dual-grid">
                    <div class="wb-pane"><!-- Primary --></div>
                    <div class="wb-bridge-badge" aria-hidden="true">⟹</div>
                    <div class="wb-pane is-hero"><!-- Derived / Compared --></div>
                </div>

                <!-- Optional Mapping / Translation Ribbon -->
                <div class="wb-ribbon">
                    <span class="wb-ribbon-label">Mapping</span>
                    <div class="wb-ribbon-chips"><!-- MathJax chips --></div>
                </div>

                <!-- Overflow-Safe Table Wrapper -->
                <div class="wb-table-wrap">
                    <table class="wb-table">...</table>
                </div>
            </div>
        </div>
    </div>
</div>
```

---

## 4. Scoped MathJax Helper Pattern

Never call `MathJax.typesetPromise()` with no arguments (it re-scans the entire `document.body`) and never assume `window.MathJax.typesetPromise` exists synchronously on `DOMContentLoaded`:

```js
function typesetWorkbenchMath(elements) {
    const targets = (Array.isArray(elements) ? elements : [elements]).filter(Boolean);
    if (!targets.length) return;
    if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
        window.MathJax.typesetPromise(targets).catch(err => console.warn('MathJax typeset error:', err));
    } else if (typeof window.ensureMathJax === 'function') {
        window.ensureMathJax()
            .then(mj => mj && mj.typesetPromise && mj.typesetPromise(targets))
            .catch(() => {});
    }
}
```

---

## 5. Per-Tool Upgrade Checklist

Before marking any individual workbench or simulation complete, verify all 6 gates:
- [ ] **Compact Header**: Left-aligned `1.65rem` `<h1>`, single-line tagline underneath, no decorative header badge clutter.
- [ ] **Overflow Safety**: `minmax(0, 1fr)` + `min-width: 0` on right stage; `overflow-x: auto` on math wells and tables.
- [ ] **Live-on-Load**: Flagship preset runs automatically on load (no blank placeholder wall).
- [ ] **Heading Hygiene**: Strict `h1 → h2 → h3` order with `0` W3C heading skips.
- [ ] **MathJax & Copy Hygiene**: Scoped `typesetWorkbenchMath([targets])`, zero raw LaTeX/Markdown in DOM text, working `Copy LaTeX` where applicable.
- [ ] **Verified Links & Local Test**: All `/physics/constants#...` and `/physics/symbols#...` anchors verified against `constants.json` / `notation.json`, `php -l` + `node --check` pass, and visually inspected on `http://localhost:8000`.

---

## 6. Universal Adoption Tracker (One Tool at a Time)

### A. Lab Tools, Workbenches & Registries (`10` Active Routes)

| # | Tool / Registry | Route | Status | Notes |
| :-: | :--- | :--- | :---: | :--- |
| 1 | **Unified Physics Laboratory (Cockpit)** | `/physics/lab-tools` | ✅ Aligned (`f7049f7a8`) | Compact header + sticky split-rail System Crucible + 5-tab Prism strip |
| 2 | **Symbolic Legendre Transformer (SymPy CAS)** | `/physics/legendre-transformer` | ✅ Aligned (`b45272bf5`) | Auto-compute on load + `L ⟹ H` hero card + numbered 3-step SymPy CAS pipeline |
| 3 | **Noether's Vault (Symmetry → Conservation)** | `/physics/noethers-vault` | ✅ Aligned (`dbd8e9790`) | Compact header + Noether mapping ribbon + 1-click Break/Restore toggle + fixed LaTeX |
| 4 | **The Physics Rosetta Stone (Notation Toggle)** | `/physics/notation-toggle` | ✅ Aligned (`a1368b8dc`) | Side-by-Side Compare (`⟺`) + Translation Key + Copy LaTeX + 5 laws |
| 5 | **Anthropic Constant Tuner** | `/physics/anthropic-tuner` | ✅ Aligned (`c3e3509e7`) | Compact header + 3 tiled scale viewports + 2-line Universe Dials + live context readout |
| 6 | **Classical-to-Quantum Correspondence Workspace** | `/physics/correspondence-workspace` | ✅ Aligned | Compact header + Correspondence ribbon + 1-click Classical/Quantum toggle + slider context bar |
| 7 | **Equation Explainer & Dissection Suite** | `/physics/equation-explainer` | ⬜ Queued | Individual review |
| 8 | **Universe Derivation Graph (Lineage Map)** | `/physics/universe-graph` | ⬜ Queued | Individual review |
| 9 | **Fundamental Physical Constants (CODATA 2022)** | `/physics/constants` | ⬜ Reference Page | 24 CODATA 2022 constants (single source of truth) |
| 10 | **Symbols & Manifold Lexicon** | `/physics/symbols` | ⬜ Reference Page | 371+ symbols + CODATA 2022 overlay |

### B. Interactive Physics Simulations (`17` Simulations + Gallery)

| # | Simulation | Domain | Route | Status |
| :-: | :--- | :--- | :--- | :---: |
| 0 | **Simulations Gallery Hub** | Hub | `/physics/simulations` | ⬜ Queued |
| 1 | **Chaotic Damped-Driven Pendulum** *(Elevated RK4 + Poincaré)* | Classical & Chaos | `/physics/simulations/pendulum` | ⬜ Queued |
| 2 | **Newton's Orbital Cannon (Projectile Motion)** *(Elevated)* | Classical & Chaos | `/physics/simulations/projectile-motion` | ⬜ Queued |
| 3 | **Double Pendulum** | Classical & Chaos | `/physics/simulations/double-pendulum` | ⬜ Queued |
| 4 | **N-Body Orbital Mechanics** | Classical & Chaos | `/physics/simulations/n-body-orbit` | ⬜ Queued |
| 5 | **Relativistic Kerr Black Hole Raytracer** *(60fps WebGL2 GPU)* | Relativity & Astro | `/physics/simulations/relativistic-black-hole` | ⬜ Queued |
| 6 | **Spacetime Relativity (Minkowski Diagrams)** | Relativity & Astro | `/physics/simulations/spacetime-relativity` | ⬜ Queued |
| 7 | **Gravitational Lensing** | Relativity & Astro | `/physics/simulations/gravitational-lensing` | ⬜ Queued |
| 8 | **Curved Spacetime Geodesic Tracer** | Relativity & Astro | `/physics/simulations/geodesic-tracer` | ⬜ Queued |
| 9 | **Wavefunction Quantum Tunneling** | Quantum | `/physics/simulations/wavefunction-tunneling` | ⬜ Queued |
| 10 | **Feynman Path Integral** | Quantum | `/physics/simulations/path-integral` | ⬜ Queued |
| 11 | **Bell's Inequality & Quantum Entanglement** | Quantum | `/physics/simulations/bells-inequality` | ⬜ Queued |
| 12 | **Electric Field Lines & Equipotentials** | E&M & Waves | `/physics/simulations/electric-field` | ⬜ Queued |
| 13 | **Gauss's Law Flux Sandbox** | E&M & Waves | `/physics/simulations/gauss-law` | ⬜ Queued |
| 14 | **Wave Superposition & Interference** | E&M & Waves | `/physics/simulations/wave-superposition` | ⬜ Queued |
| 15 | **Brownian Motion (Langevin Stochastic)** | Thermo & Fluids | `/physics/simulations/brownian-motion` | ⬜ Queued |
| 16 | **Maxwell's Demon (Entropy & Information)** | Thermo & Fluids | `/physics/simulations/maxwells-demon` | ⬜ Queued |
| 17 | **Kármán Vortex Street (Fluid Dynamics)** | Thermo & Fluids | `/physics/simulations/vortex-street` | ⬜ Queued |
