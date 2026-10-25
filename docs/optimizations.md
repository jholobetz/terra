# ⚡ Terra Physics Lab — Client & Server Performance Optimization Catalog

> **Status**: Active Technical Blueprint  
> **Scope**: Frontend Canvas/WebGL Engines, Global Layout & MathJax Pipeline, Spotlight Search, and Backend Hub Compilation  
> **Related**: [`CLAUDE.md`](../CLAUDE.md), [`docs/roadmap.md`](roadmap.md), [`docs/architecture.md`](architecture.md)

---

## 0. Completed Baseline Optimizations (`commit 4e28cbe2`)

* **Front Page 3D Halo Orbit (`public/js/halo_orbit.js`) & Hero Canvas (`public/js/hero_canvas.js`)**:
  * Capped animation frame rate at **30 FPS** (`frameInterval = 1000 / 30`) with delta-time velocity normalization (`baseTickMs = 1000 / 60`).
  * Full lifecycle gating via `IntersectionObserver`, `document.hidden` (`visibilitychange`), and `window` `blur`/`focus`.
* **Topic Hub Solar Constellation Manifold (`app/views/physics/topic.php`)**:
  * Capped orbital drift at **30 FPS** with delta-time normalization across 60Hz and 120Hz ProMotion displays.
  * Hoisted all static SVG badge measurements (`n.text.getBBox()`) and static attribute writes (`x`, `y`, `width`, `height`) out of `animateOrbits()` into a single one-time initialization pass (eliminating 14,500–34,000 synchronous layout flushes per second).
  * Scoped SVG `<filter id="glow-filter">` (`feGaussianBlur`) strictly to the active/hovered planetary node rather than all 121–283 background nodes.
  * Added true `cancelAnimationFrame` lifecycle gating on **"Pause Drift"**, **"Curriculum Directory"** mode switch, `IntersectionObserver` viewport exit, background tab, and window blur.

---

## 1. Interactive Canvas & GPU Simulation Loops (CPU / GPU / Battery)

### 1.1 Unified Physics Cockpit (`/physics/lab-tools` — [`public/js/lab_cockpit.js`](../public/js/lab_cockpit.js))
* **Current Bottlenecks**:
  1. **Pseudo-Pause**: Clicking **Pause** sets `this.isRunning = false`, which skips `stepPhysics()`, but [`this.loop()`](../public/js/lab_cockpit.js#L758-L766) continues executing at **60–120 FPS**, clearing/redrawing the entire high-DPI canvas (`renderCanvas()`) and rewriting DOM telemetry (`updateTelemetry()`) on every frame for a frozen simulation state.
  2. **Uncapped Refresh Rate & Fixed Step**: Uses raw `requestAnimationFrame` with a hardcoded `0.016` step (`this.simTime += 0.016`), running at 2x speed and 120 FPS on ProMotion displays.
  3. **No Viewport or Window Focus Gating**: Scrolling down `/physics/lab-tools` to inspect the Flagship Analytical Engines cards or switching windows leaves the canvas redrawing offscreen.
  4. **Per-Frame Grid & Path Reconstruction**: [`renderCanvas()`](../public/js/lab_cockpit.js#L861-L870) issues individual `beginPath()` / `stroke()` calls for every grid line on every tick instead of batching into a single path.
* **Remediation**:
  * Halt `requestAnimationFrame` completely when `this.isRunning === false`, when scrolled out of the viewport (`IntersectionObserver`), or when the tab/window is unfocused (`visibilitychange` / `blur`).
  * Throttle the loop to a configurable target (e.g., **30 FPS** or **60 FPS**) with delta-time physics sub-stepping.
  * Batch the background coordinate grid into a single `ctx.beginPath()` / `ctx.stroke()` call.

### 1.2 WebGL2 Shader Harness & Kerr Black Hole Raytracer ([`public/js/lib/webgl_physics_harness.js`](../public/js/lib/webgl_physics_harness.js))
* **Current Bottlenecks**:
  1. **Unpaused Background GPU Raymarching**: [`WebGLPhysicsHarness.start()`](../public/js/lib/webgl_physics_harness.js#L729-L738) previously ran per-pixel Boyer-Lindquist null geodesic raymarching at Retina resolution (`dpr = 2`) at uncapped 60–120 FPS with no `IntersectionObserver` or `visibilitychange` auto-pause. Switching tabs or scrolling down to read the physics treatise left the GPU at high load.
* **Remediation**:
  * Throttle `WebGLPhysicsHarness` to **30 FPS** (`targetFps: 30`) while retaining `preserveDrawingBuffer: true` so skipped 60Hz/120Hz compositor frames never blank the canvas.
  * Add automatic lifecycle gating (`IntersectionObserver`, `visibilitychange`) and explicit Play/Pause control so all WebGL simulations inherit zero-drain offscreen behavior automatically.

### 1.3 Equation Explainer Vector Field Sandbox ([`public/js/explainer_simulations.js`](../public/js/explainer_simulations.js))
* **Current Bottlenecks**:
  1. **Uncapped Loop & Offscreen Execution**: [`startSandboxLoop()`](../public/js/explainer_simulations.js#L117-L164) runs an uncapped `requestAnimationFrame` loop with no `IntersectionObserver` or window `blur` gating. When a user scrolls down `/physics/equation-explainer` to read variable breakdowns, multi-step proofs, or the lineage graph, the canvas continues rendering offscreen.
  2. **Per-Line Grid Strokes & `shadowBlur`**: Issues ~35 separate `beginPath()` / `stroke()` calls per frame for the 20px background grid ([L133-L144](../public/js/explainer_simulations.js#L133-L144)) and evaluates `ctx.shadowBlur = 10` across pixel-by-pixel wave paths.
* **Remediation**:
  * Cap at **30 FPS**, batch the background grid into a single path, and pause the loop via `IntersectionObserver`, `visibilitychange`, and `window` `blur`.

### 1.4 Flagship Duality Workbenches (`noethers_vault.js`, `correspondence_workspace.js`, `anthropic_tuner.js`)
* **Current Bottlenecks**:
  1. **Noether's Vault ([`public/js/noethers_vault.js`](../public/js/noethers_vault.js#L329))**: Runs an uncapped `requestAnimationFrame` loop rendering **two** canvases (`#vault-canvas` and `#chart-canvas`) simultaneously on every tick with no pause button, no FPS cap, and no viewport/focus gating.
  2. **Correspondence Workspace ([`public/js/correspondence_workspace.js`](../public/js/correspondence_workspace.js#L338-L350))**: Solves a Crank-Nicolson tridiagonal matrix system (`N = 120`) and redraws wavefunctions + phase-space particles at uncapped 60–120 FPS without viewport/focus gating.
  3. **Anthropic Constant Tuner ([`public/js/anthropic_tuner.js`](../public/js/anthropic_tuner.js#L84))**: Continuously animates Bohr orbitals, planetary orbits, and stellar corona gradients at uncapped 60–120 FPS even when the canvas is scrolled out of view or the window is unfocused.
* **Remediation**:
  * Standardize all three workbenches onto a **30 FPS** delta-normalized loop with `IntersectionObserver`, `visibilitychange`, and `window` `blur`/`focus` gating.

### 1.5 Elevated Canvas Simulations (`pendulum.js` & `projectile-motion.js`)
* **Current Bottlenecks**:
  1. **Unbounded Trajectory Array Memory Leak in Newton's Cannon ([`public/js/simulations/projectile-motion.js`](../public/js/simulations/projectile-motion.js#L277))**: Declares `const maxPathPoints = 1200` ([L109](../public/js/simulations/projectile-motion.js#L109)), but `stepProjectile()` pushes 8 points per frame into `p.path` **without ever shifting old points**. For a bound circular or elliptical orbit, `p.path` grows by ~500–960 points per second (exceeding 30,000+ vertices after 1 minute) and strokes all of them with `ctx.shadowBlur = 8` every frame.
  2. **Per-Frame Gradient Allocation**: `projectile-motion.js` calls `ctx.createRadialGradient(...)` twice on every frame ([L326-L338](../public/js/simulations/projectile-motion.js#L326-L338)) for static Earth and atmosphere gradients that only change on `resize()`.
  3. **Pseudo-Pause & Uncapped Loops**: Both [`pendulum.js`](../public/js/simulations/pendulum.js#L259-L271) and [`projectile-motion.js`](../public/js/simulations/projectile-motion.js#L299-L310) keep running their `requestAnimationFrame` render loops at 60–120 FPS when paused (`isRunning = false`) or when the browser window is unfocused.
* **Remediation**:
  * Enforce `if (p.path.length > maxPathPoints) p.path.shift();` in `projectile-motion.js` and cache the Earth/atmosphere `CanvasGradient` objects inside `resize()`.
  * Add true `cancelAnimationFrame` pause, `IntersectionObserver`, `visibilitychange`, and `window` `blur`/`focus` gating to both simulations.

---

## 2. Global Page-Load & MathJax Pipeline (`layout.php` & `hub_interactions.js`)

### 2.1 Render-Blocking Scripts in `<head>` ([`app/views/physics/layout.php`](../app/views/physics/layout.php#L14-L17))
* **Issue**: `math_prose_formatter.js` and `hub_interactions.js` are loaded in `<head>` without `defer`, blocking HTML parser progression before First Contentful Paint (FCP).
* **Fix**: Add `defer` to `math_prose_formatter.js` and `hub_interactions.js` in `layout.php`.

### 2.2 Redundant Full-Document MathJax Scan ([`public/js/hub_interactions.js`](../public/js/hub_interactions.js#L31-L33))
* **Issue**: On `DOMContentLoaded`, `hub_interactions.js` unconditionally invokes `window.MathJax.typesetPromise()` across the entire document, even on pre-compiled subtopic pages (`/physics/subtopic/*`) where equations are already baked into inline `<svg data-tex="...">` sprites.
* **Fix**: Guard the global `typesetPromise()` call so it only runs when unrendered math delimiters (`\[`, `\(`, `$$`) exist in the DOM.

### 2.3 Memoized Variable Hover Selectors ([`public/js/hub_interactions.js`](../public/js/hub_interactions.js#L188-L227))
* **Issue**: Every `mouseover` on a `.var-tag` re-runs regex unwrapping and constructs ~80 CSS attribute selectors (`use[href$="-HEX"]`, `mjx-c.mjx-cHEX`).
* **Fix**: Cache compiled selector strings per `symbol` in a `Map` for `O(1)` lookup on hover.

---

## 3. Spotlight Search Modal (`search_engine.js`)

### 3.1 Lazy Fallback Index Loading ([`public/js/search_engine.js`](../public/js/search_engine.js#L27-L49))
* **Issue**: Opening the search modal (`⌘K`) immediately calls `loadIndex()`, fetching and parsing `/physics/search-index` (the entire offline JSON index), even though `performSearch()` queries `/physics/api/search` and only uses `searchData` inside `catch (err)` as an offline fallback.
* **Fix**: Remove eager `loadIndex()` from `openModal()` and call `await loadIndex()` lazily inside `performFallbackSearch(query)` only if `/physics/api/search` is unreachable. Add an `AbortController` to cancel superseded in-flight API queries during fast typing.

---

## 4. Backend Topic Hub Compilation (`PhysicsController.php`)

### 4.1 Scoped Subtopic Map Construction ([`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L885-L894))
* **Issue**: When compiling an uncached or preview Topic Hub (`viewTopic()`), the controller iterates over **all 1,584 subtopics** in `$content['subtopics']` and executes regex SVG sprite inlining (`$inlineSvgFunc`) and variable trigger wrapping (`$wrapVariableTriggers`) on every single subtopic, even though a topic hub only renders the ~20–280 subtopics listed in its own `$topic['pillars']`.
* **Fix**: Collect the ~20–280 target slugs from `$topic['pillars']` first and only run `$inlineSvgFunc` / `$wrapVariableTriggers` on those matching subtopics, reducing uncached/preview Topic Hub build work by **80–95%**.
