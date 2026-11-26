# 🛠️ Phase 5 Post-Expansion Polish & Outside-Audit Ideas

> **Status**: Active Working Checklist (Pre-Phase 6 / OPS 2.0)  
> **Created**: 2026-11-25  
> **Baseline**: `1,704` Platinum subtopics (`+120` Phase 5 across 24 batches) · `15,583` canonical formulas · Live on `https://physicslab.ca` (`9d9656f7d`)

---

## ✅ Recently Completed External & Live-Site Audits (2026-11-23)
- **Sitewide External DOI Audit (`8c1f4144f`):** Verified all `1,514 / 1,514` DOIs (`100.0%`) via OpenAlex + Crossref + `doi.org`; repaired `24` broken or wrong-paper citations.
- **Non-DOI External Citation URL Audit (`9d9656f7d`):** Audited `3,349` non-DOI references (`1,706` unique URLs) and repaired all `7` hard `HTTP 404` URLs.
- **Production SEO & Canonical Guard (`9d9656f7d`):** Fixed `PhysicsController::resolveBaseUrl()` production fallback (`http://localhost:8000` → `https://physicslab.ca`); all `1,746 / 1,746` live `sitemap.xml` URLs, `<link rel="canonical">`, and `og:url` tags now resolve to `https://physicslab.ca`.
- **Security Headers Hardening (`194a2d1e7`):** Tightened `Referrer-Policy` (`strict-origin-when-cross-origin`), `Permissions-Policy` (`geolocation=(), camera=(), microphone=()`), and server-side Apache `ServerTokens Prod` / `ServerSignature Off`.
- **W3C HTML5 Cleanup (`9d9656f7d`):** Reduced W3C Nu HTML5 errors across the 6 flagship templates from `107 → 2` (`98.1%`) by hoisting `<style>` blocks into `<head>` in `layout.php`, replacing `<div>` inside `<button>` on Equation Explainer, and fixing skipped heading levels on Hubs & Lab Tools.

---

## 📋 Queued Small-to-Medium Polish & Outside-Audit Tasks

### 1. Quick Hygiene Sweep *(Completed 2026-11-25)* ✅
- [x] **Eliminate the Final 2 W3C HTML5 Errors:**
  - `app/views/physics/home.php`: Changed `<h4 class="cube-title">` to `<h2>`.
  - `app/views/physics/legendre_transformer.php`: Changed top-level card `<h3>` headings to `<h2>` (+ CSS selectors) so all 6 flagship templates hit **0 W3C HTML5 errors**.
- [x] **Resolve the 2 Remaining `Unlinked Entity` Warnings:**
  - Linked `Albert Einstein` in `brownian-motion-langevin-dynamics`.
  - Linked `Richard Feynman` in `brownian-ratchets-molecular-motors`.
- [x] **Sync Phase 5 Counters in Docs & Assessment Script:**
  - Updated `docs/roadmap.md` and made `scripts/maintenance/run_project_assessment.py` compute `+{total_articles - 1584} Phase 5` dynamically (**`+120` subtopics, `1,704` total**).

---

### 2. SymPy CAS Verification Sweep on Option B Formulas (`Batches 16–24`) *(~10 min)*
- [ ] Run `scripts/cascheck` specifically across the **`315` newly authored formulas** from Batches 16–24.
- [ ] Inspect any dimensional homogeneity flags, unit-string inconsistencies, or algebraic edge cases caught by the local SymPy CAS engine and tighten definitions where helpful.

---

### 3. Expand External Scientific Ground-Truth Audits (NIST CODATA 2022 + PDG 2024) *(~15 min)*
- [ ] Currently `integrity_shield.py` only audits **8 CODATA constants** and **8 PDG particles**.
- [ ] Audit *every* constant and particle value on `/physics/constants` and in `app/config/content/entities.json` against official **NIST CODATA 2022** and **PDG 2024** reference values (Avogadro, Rydberg, Bohr magneton, elementary charge, Planck units, proton/electron mass ratio, quarks, mesons, etc.).
- [ ] Expand the automated auditor tables in `integrity_shield.py` so regressions are caught automatically.

---

### 4. Front-End Render-Blocking & Asset Performance Polish *(~15 min)*
- [ ] Defer synchronous `mathjax_config.js` in `app/views/physics/layout.php` (currently loaded without `defer` in `<head>`).
- [ ] Audit whether static pre-rendered SVG subtopic pages even need to eagerly download the `~1.2 MB` `tex-svg-full.js` bundle on initial paint, or whether it can be lazy-loaded only when dynamic MathJax typesetting is needed (e.g., Formula Inspector / Equation Explainer / interactive tools).
- [ ] Benchmark raw load performance (FCP, LCP, TBT, CLS) locally against `http://localhost:8000` without Anubis challenge overhead.
- [ ] *(Optional Server Config)* Add `Header always setifempty` for the 5 universal security headers (`HSTS`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`) on the outer Apache `<VirtualHost *:443>` so Anubis challenge pages and static assets also pass external scanners like SecurityHeaders.com.

---

### 5. Semantic Keyword Cleanup (`semantic_prose_verifier.py` Warnings) *(~15 min)*
- [ ] Clean up the `~47` recurring `Missing Keywords` / low-similarity warnings printed during pre-commit Integrity Shield runs (e.g., diacritic mismatches like `perot` vs `Pérot`, `mossbauer` vs `Mössbauer`, `weizsacker` vs `Weizsäcker`, and hyphenated/unmatched keywords in `app/config/ref_data/semantic_references.json`).
- [ ] Goal: make pre-commit and pre-push Integrity Shield runs noticeably cleaner with near-zero noise.
