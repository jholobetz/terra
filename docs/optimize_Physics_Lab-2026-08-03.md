# Strategic Optimization Roadmap for Terra Physics Lab

---

## 1. Overview

This document outlines architectural, performance, educational, and dataset quality optimizations for the Terra Physics Lab. The goal is to maximize page load speeds, eliminate MathJax rendering bottlenecks, expand interactive learning tools, and provide robust offline capabilities.

---

## 2. Frontend Performance & Rendering Optimizations

### A. Viewport-Triggered MathJax Typesetting (Lazy Math Rendering)
- **Current State**: Long subtopic pages containing dozens of equations trigger MathJax 3 to typeset every formula on page load at once, causing CPU spikes.
- **Optimization**: Implement an `IntersectionObserver` in `mathjax_config.js` to defer MathJax typesetting until a formula card scrolls into the user's viewport.
- **Impact**: **60–80% faster initial page load** and smoother 60fps scrolling on mobile devices.

### B. Asset Minification & HTTP/2 Push / Brotli Compression
- **Current State**: Multiple unminified JS scripts (`equation_explainer.js`, `hub_interactions.js`, `search_engine.js`) are fetched via separate HTTP requests.
- **Optimization**: 
  - Add a build script (ESBuild / Vite) to bundle and minify JS/CSS into single hashed production assets (`app.min.js`, `physics.min.css`).
  - Enable **Brotli compression** on HTTP responses for static assets and HTML caches.
- **Impact**: Reduces HTTP overhead by ~65% and accelerates cold-cache rendering.

### C. HTTP `Stale-While-Revalidate` & ETag Caching
- **Optimization**: Enhance `PhysicsController.php` response headers for cached topic/subtopic HTML:
  ```http
  Cache-Control: public, max-age=3600, stale-while-revalidate=86400
  ETag: "hash-of-shard"
  ```
- **Impact**: Browsers render instantly from disk cache while silently verifying background updates with the server.

---

## 3. Search & Data Query Acceleration

### A. IndexedDB Caching & Compressed Search Index
- **Current State**: Spotlight Search (`search_engine.js`) fetches `search_index.json` (~1.5 MB) on page load.
- **Optimization**:
  - Store `search_index.json` in browser `IndexedDB` with version tracking.
  - Upgrade client-side search to a lightweight trie index or **FlexSearch.js**.
- **Impact**: Sub-millisecond instant search across all ~13,700+ formulas with zero network latency on repeat visits.

### B. MariaDB Query & APCu In-Memory Caching
- **Optimization**: Cache `PhysicsService::getFormulaWithHierarchy()` and `getSubtopicsByFormula()` query results in **APCu** (PHP in-memory cache) or Redis.
- **Impact**: Eliminates SQL database queries entirely for non-cached dynamic endpoints.

---

## 4. Advanced Educational & Interactive Tools

### A. Visual TeX Equation Composer
- **Feature**: Add an interactive symbol palette to the **Equation Explainer** and **Dimensional Solver**:
  - Clicking buttons ($\oint$, $\nabla \times$, $\frac{\partial}{\partial t}$, $\mathbf{B}$, $\hbar$) inserts clean LaTeX snippets directly into the input box.
- **Impact**: Removes the barrier of needing to know exact TeX syntax for students exploring custom equations.

### B. Symbolic Mathematics Engine (WebAssembly SymPy / Algebrite)
- **Feature**: Integrate a client-side WebAssembly SymPy engine:
  - Automatically evaluate symbolic derivatives (e.g., $\frac{d}{dt} [\sin(\omega t)] \to \omega \cos(\omega t)$).
  - Automatically verify dimensional consistency (e.g., confirm $N \cdot s = kg \cdot m/s$).
- **Impact**: Transforms the Dimensional Solver into a live computer algebra system (CAS).

### C. 3D WebGL Vector Field Visualizer (Three.js)
- **Feature**: Upgrade the 2D simulation canvas to an interactive 3D WebGL canvas for vector calculus:
  - Visualize 3D curl ($\nabla \times \mathbf{v}$) as rotating streamlines in fluid flow.
  - Visualize electromagnetic wave propagation ($\mathbf{E} \times \mathbf{B}$).
- **Impact**: Delivers an interactive visual demonstration of complex 3D vector fields.

---

## 5. Dataset Engineering & Automated Quality Control

### A. Strict Pre-Commit TeX Delimiter Linter
- **Feature**: Expand `scripts/audit_prose_and_variables.py` into a Git pre-commit hook that automatically checks all 293 shards for:
  1. Unclosed `$` dollar sign delimiters.
  2. Nested `$` inside `\left...` or `\frac` blocks.
  3. Raw unwrapped TeX macros outside math mode.
- **Impact**: Permanently prevents broken MathJax SVG rendering bugs from reaching production.

### B. Incremental Hash Sync Engine
- **Feature**: Enhance `formulas_hash_registry.json` to perform differential syncs, inspecting git diffs so `sync_formulas_to_mariadb.php` only processes changed JSON keys.
- **Impact**: Reduces database sync time from seconds down to milliseconds.

---

## 6. Progressive Web App (PWA) & Full Offline Mode

### Feature: Complete Offline Reference Encyclopedia
- Add a `manifest.json` and a Service Worker (`sw.js`).
- Cache core pages, MathJax web fonts, and CSS/JS assets locally.
- **Impact**: Allows users to install Terra as a standalone desktop or mobile application that functions completely offline without internet connectivity.

---

## 7. Recommended Implementation Priorities

| Priority | Optimization | Target Area | Effort | Impact |
| :--- | :--- | :--- | :---: | :---: |
| **P1** | **Viewport-Triggered MathJax Typesetting** | Performance | Medium | 🚀 Massive (60-80% faster load) |
| **P1** | **Strict Pre-Commit TeX Delimiter Linter** | Quality Control | Low | 🛡️ High (Prevents SVG crashes) |
| **P2** | **Visual TeX Equation Palette** | UX / Explainer | Low | ✨ High (Ease of use) |
| **P2** | **IndexedDB Search Index Caching** | Search Engine | Medium | ⚡ High (Instant offline search) |
| **P3** | **PWA Service Worker (Offline Mode)** | Mobile / Desktop | Medium | 📱 High (Offline encyclopedia) |
| **P3** | **3D WebGL Streamline Simulator** | Lab Tools | High | 🎨 High (Visual wow factor) |
