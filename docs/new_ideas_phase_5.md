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

### 2. SymPy CAS Verification Sweep on Option B Formulas (`Batches 16–24`) *(Completed 2026-11-25)* ✅
- [x] Upgraded [`lib/cas/latex_parser.py`](../lib/cas/latex_parser.py) & [`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py) (`1e2e0f875`): normalized square brackets `[...]` → `(...)`, generalized coordinate function-argument stripping (`V(r)` → `V`, `B(Z, A)` → `B`), isolated primary equations on `, \quad` multi-equation lines, classified matrices as `OPERATOR_OR_TENSOR`, and handled dimensionless trig-like functions (`HOMOGENEOUS`: `114 → 171`, `PARSE_ERROR`: `109 → 54`, `22/22` tests passing).
- [x] Wired automatic SymPy CAS pre-flight (`[WARN]` by default + `--strict-cas` opt-in hard gate) and authoritative `"verified_by": "sympy_cas"` stamping directly into [`scripts/expand_hub.py`](../scripts/expand_hub.py).
- [x] Executed one-time authoritative SymPy CAS stamp across all `188` SymPy-verified Option B formulas (`171 HOMOGENEOUS` + `17 OPERATOR_OR_TENSOR`) and synchronized shard hashes + MariaDB.

---

### 3. Expand External Scientific Ground-Truth Audits (NIST CODATA 2022 + PDG 2024) *(Completed 2026-11-25)* ✅
- [x] Upgraded [`app/config/content/constants.json`](../app/config/content/constants.json) & [`app/config/ref_data/codata_2022.json`](../app/config/ref_data/codata_2022.json) from `8 → 24` fundamental constants with true **NIST CODATA 2022** values (fixing CODATA 2018 drift on $\alpha$, $\varepsilon_0$, and $\mu_0$, and adding $h, e, N_A, R, m_e, m_p, m_n, m_u, R_\infty, a_0, \mu_B, \mu_N, F, \ell_P, t_P, m_P$ directly to `/physics/constants`).
- [x] Upgraded [`app/config/content/particles.json`](../app/config/content/particles.json) & [`app/config/ref_data/pdg_2024.json`](../app/config/ref_data/pdg_2024.json) from `8 → 20` Standard Model + composite hadron particles with true **PDG 2024** values (fixing PDG 2022 drift on Higgs, $W$, $Z$, and $\tau$, and adding all 6 quarks, 3 neutrinos, photon, gluon, and charged pion $\pi^\pm$).
- [x] Fixed `<h1> → <h3>` heading skip in [`app/views/physics/constants.php`](../app/views/physics/constants.php) and verified 14 cross-constant physical identities (`rel_diff < 1e-8`) alongside `nist_constants_verifier.py` (`24/24`) and `pdg_particle_verifier.py` (`20/20`).

---

### 4. Front-End Render-Blocking & Asset Performance Polish *(Completed 2026-11-25)* ✅
- [x] Deferred [`mathjax_config.js`](../public/js/mathjax_config.js) in [`app/views/physics/layout.php`](../app/views/physics/layout.php) (`0` render-blocking `<script>` tags in `<head>` across all routes).
- [x] Implemented route-aware MathJax loading + CSP-nonce-safe `window.ensureMathJax()` lazy loader: skips eager `2.2 MB` `tex-svg-full.js` on math-free landing routes (`/`, `/physics`, `/physics/topic/*`, `/physics/simulations`) while preserving eager `defer` loading on math-bearing routes (`/physics/subtopic/*`, `/physics/constants`, `/physics/equation-explainer`, `/physics/lab-tools`, etc.) and wiring on-demand typesetting into [`public/js/search_engine.js`](../public/js/search_engine.js).
- [x] Benchmarked rendered routes locally (`0` blocking head scripts across all 5 flagship routes; `tex-svg-full.js` omitted on Home, Hub, and Simulations Gallery) and verified `composer test` (`32/32`).
- [ ] *(Optional Server Config — outside repo)* Add `Header always setifempty` for the 5 universal security headers on the outer Apache `<VirtualHost *:443>` if you want external scanners to see them on Anubis challenge pages.

---

### 5. Semantic Keyword Cleanup (`semantic_prose_verifier.py` Warnings) *(~15 min)*
- [ ] Clean up the `~47` recurring `Missing Keywords` / low-similarity warnings printed during pre-commit Integrity Shield runs (e.g., diacritic mismatches like `perot` vs `Pérot`, `mossbauer` vs `Mössbauer`, `weizsacker` vs `Weizsäcker`, and hyphenated/unmatched keywords in `app/config/ref_data/semantic_references.json`).
- [ ] Goal: make pre-commit and pre-push Integrity Shield runs noticeably cleaner with near-zero noise.
