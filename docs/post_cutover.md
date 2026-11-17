# 🛰️ Terra Physics Lab — Post-Cutover Burn-In & Operations Guide

> **Status**: Active Post-Cutover Burn-In & Evaluation Checklist  
> **Canonical Production Target**: [`https://physicslab.ca`](https://physicslab.ca) (`/srv/www/terra`, Debian 13 + Apache 2.4 + `php8.4-fpm` + MariaDB + `.venv`)  
> **Companion Documents**: [`CLAUDE.md`](../CLAUDE.md), [`docs/architecture.md`](architecture.md), [`docs/roadmap.md`](roadmap.md), [`docs/ideas.md`](ideas.md)

---

## 1. The Post-Cutover Mindset Shift

Crossing from a private local development studio (`http://localhost:8000`) to a live public HTTPS domain (`https://physicslab.ca`) shifts engineering priorities from **raw feature velocity** to **operational stability and burn-in verification**. Before starting the next major feature horizon (**Phase 5** in [`docs/roadmap.md`](roadmap.md)), the live deployment should be exercised across real browsers, dynamic subprocess boundaries, unattended system timers, and routine Git delta updates.

---

## 2. Live Functional Smoke-Testing (Beyond `/healthz`)

The readiness probe (`/healthz` in [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php)) is intentionally lightweight (`< 5ms`): it verifies MariaDB connectivity (`SELECT 1`), writable `app/log/` and `public/cache/` directories, and `.venv/bin/python3` executable presence without spawning a Python process on every probe.

A complete live browser pass on `https://physicslab.ca` should exercise the dynamic runtime boundaries:

* [x] **Live SymPy CAS Subprocess Execution** *(Verified 2026-11-17)*:
  * Triggered **Compute Legendre Duality** on `/physics/legendre-transformer` and direct `POST /physics/api/cas-evaluate`.
  * Confirmed `php8.4-fpm` (`www-data`) spawns `/srv/www/terra/.venv/bin/python3 lib/cas/cas_engine.py`, imports `sympy`, and returns valid symbolic Legendre / Dirac-constraint JSON under production permissions.
* [x] **Search & Related-Subtopics Manifold Pipeline** *(Verified 2026-11-17)*:
  * Verified Spotlight Search (`Cmd+K` / `/physics/api/search`) on MariaDB keyword queries.
  * Unified both `subtopic.php` ("Further Manifold Exploration") and `/physics/api/related-subtopics/@slug` onto deterministic, 100% Git-tracked `PhysicsService::getRelatedTopics()` (scoring prose graph links + parent/sibling lineage + shared `formula_ids`/keywords + cross-pillar bridge guarantee, with zero untracked `.scp` file dependency).
* [ ] **Browser DevTools Console, CSP & Compression Audit**:
  * Inspect DevTools (`Console` + `Network`) across a Topic Hub, a Subtopic article, `/physics/universe-graph`, and `/physics/simulations/relativistic-black-hole`.
  * Confirm **`0` CSP violations**, **`0` `404` asset requests**, and active `Content-Encoding: gzip` (`mod_deflate`) on large vendored libraries (`tex-svg-full.js`, `math.min.js`, `formula_derivation_graph.json.gz`).

---

## 3. Reverse-Proxy & Client IP Rate-Limiting Verification

During initial log inspection, Apache recorded `[client 127.0.0.1:...]` on external requests to `https://physicslab.ca`:

* [ ] **Verify Forwarding Headers Behind Loopback Proxies/Tunnels**:
  * [`AuthService::resolveClientIp()`](../app/logic/AuthService.php) trusts `127.0.0.1` as a local proxy and extracts the caller's real IP from `X-Forwarded-For` or `X-Real-IP`.
  * If a local reverse proxy sits in front of Apache *without* forwarding `X-Forwarded-For` / `X-Real-IP`, every external visitor resolves to `'127.0.0.1'` and shares a single `20 req/min` sliding-window rate-limit bucket for CAS and semantic search.
  * **Quick Check**: Load a page from an external network (e.g., phone on cellular data) and inspect `/var/log/apache2/*access*.log` (or forwarded headers) to confirm distinct visitor IPs are preserved.

---

## 4. Unattended Reliability ("Set-and-Forget" Server Checks)

Three quick checks on Debian 13 prevent silent operational failures weeks or months after launch:

* [ ] **Reboot Auto-Start Survival**:
  ```bash
  systemctl is-enabled apache2 php8.4-fpm mariadb
  ```
  Confirm all three print `enabled` so an unexpected host reboot restores `https://physicslab.ca` automatically.
* [ ] **60-Day Let's Encrypt TLS Renewal Dry-Run**:
  ```bash
  sudo certbot renew --dry-run
  ```
  Proves Certbot's HTTP-01 challenge reaches `/.well-known/acme-challenge/` cleanly through [`public/.htaccess`](../public/.htaccess).
* [ ] **Canonical Host & HTTPS Redirects (`301`)**:
  ```bash
  curl -I http://physicslab.ca/
  curl -I https://www.physicslab.ca/
  ```
  Verify both redirect cleanly (`301`) to `https://physicslab.ca` so search engines never index duplicate hosts.
* [ ] **Disable Production Xdebug (If Loaded)**:
  * If `php-xdebug` is enabled in `php8.4-fpm` or `apache2` (indicated by multi-line `PHP Stack trace:` notices in Apache error logs), disabling it for web SAPIs (`sudo phpdismod -s fpm xdebug && sudo phpdismod -s apache2 xdebug && sudo systemctl reload php8.4-fpm apache2`) reduces CPU and memory overhead on dynamic requests.

---

## 5. Public Exposure, Bots & Log Hygiene

Once a domain appears in public Certificate Transparency logs and serves a `1,600+`-URL `/sitemap.xml`, search crawlers, AI scrapers, and automated `.env` / `wp-admin` scanners probe it continuously:

* **Built-In Defenses Active**:
  * [`public/.htaccess`](../public/.htaccess) blocks dotfile probes (`403 Forbidden`, exempting `/.well-known/`).
  * `/robots.txt` disallows `/physics/admin` and `/physics/api/`.
  * Pre-warmed HTML disk caches (`public/cache/`) serve encyclopedia traffic at static-file speed without touching MariaDB.
  * Branded `404` / `500` views return clean responses with zero stack-trace or path leakage.
  * Debian 13's built-in `/etc/logrotate.d/apache2` and `/etc/logrotate.d/php8.4-fpm` automatically rotate, compress, and prune server logs.
* **First-Week Observation**:
  * Periodically review `/var/log/apache2/*error*.log` and `*access*.log` during the first week of evaluation to spot any unexpected `404` links, slow requests, or crawler bursts.

---

## 6. Disciplined Dev $\rightarrow$ Git $\rightarrow$ Prod Rhythm

Post-cutover stability relies on strict separation between the **authoring workshop** and the **production target**:

1. **Author & Break Things Locally (`macOS Studio`)**:
   * Perform edits, prose/equation refinements, and schema changes locally at `http://localhost:8000`.
   * Run `composer test` and `bash scripts/assess -q` before pushing.
2. **Avoid Ad-Hoc Server File Mutations**:
   * Keep `/srv/www/terra` git-clean so `git pull --ff-only` never hits split-brain conflicts.
   * Remember that `app/config/config.php` is `640` with group `www-data`—in-place file-replacement commands (`sed -i`) reset group ownership unless `chgrp www-data` is re-applied (now also auto-guarded in [`scripts/update_prod.sh`](../scripts/update_prod.sh)).
3. **Deploy & Roll Back Predictably**:
   * Routine code/asset deploy: `bash scripts/update_prod.sh`
   * Fast shard/equation delta (`~2–5s`): `bash scripts/update_prod.sh --quick`
   * Instant recovery if `/healthz` or visual QA flags an issue: `bash scripts/update_prod.sh --rollback`

---

## 7. First-Time Visitor Evaluation Lens & Candidate Next Steps

Evaluating `https://physicslab.ca` across desktop and mobile **from a first-time outsider's perspective** (without assuming familiarity with internal concepts like OPS, shards, GQS, or the DAG) helps prioritize post-burn-in improvements outside Phases 6–7:

1. **Public Visitor Framing & Mobile UX**:
   * Dedicated `/physics/about` overview page + richer footer links (`About`, `Universe Graph`, `Constants`, `Sitemap`), allowing the homepage hero subtitle to return to a concise physics tagline while keeping the exploratory project disclaimer prominent.
   * Surfacing unlisted routes (`/physics/dimensional-solver`, `/physics/genealogy-explorer`) in the `Lab Tools` mega-navigation.
   * Responsive viewport pass (`375px`–`768px`) across the homepage `#halo-orbit-ring`, mega-menus, and Equation Explainer variable dissector.
2. **"How It All Connects" Discovery Features** ([`docs/ideas.md`](ideas.md)):
   * *"Surprise Me With a Bridge"* cross-domain multi-hop launcher, Equation Explainer derivation journey breadcrumbs, and one-click *"Copy as SymPy / Python"* export snippets.
3. **Mathematical & Interactive Depth**:
   * Expanding multi-step derivation proofs beyond the initial `104` canonical proofs toward all high-traffic Topic Hub equations, interactive series/classical-limit sliders in the Equation Explainer, Wave 2 simulation elevations, or deferred `fluids-nonlinear.json` curriculum enrichment (`2.8`).
4. **Zero-Cookie Server Traffic Summary**:
   * Optional read-only diagnostic script on Debian 13 summarizing Apache `access.log` hits and `404`s with zero cookies or third-party trackers.
