# 🛰️ Terra Physics Lab — Post-Cutover Burn-In & Operations Guide

> **Status**: Archived Historical Record (Post-Cutover Burn-In Completed `8 / 8` — 2026-11-17)  
> **Canonical Production Target**: [`https://physicslab.ca`](https://physicslab.ca) (`/srv/www/terra`, Debian 13 + Apache 2.4 + `php8.4-fpm` + MariaDB + `.venv`)  
> **Companion Documents**: [`CLAUDE.md`](../CLAUDE.md), [`docs/architecture.md`](../docs/architecture.md), [`docs/roadmap.md`](../docs/roadmap.md), [`docs/ideas.md`](../docs/ideas.md), [`archive/final_stages.md`](final_stages.md)

---

## 1. The Post-Cutover Mindset Shift

Crossing from a private local development studio (`http://localhost:8000`) to a live public HTTPS domain (`https://physicslab.ca`) shifts engineering priorities from **raw feature velocity** to **operational stability and burn-in verification**. Before starting the next major feature horizon (**Phase 5** in [`docs/roadmap.md`](../docs/roadmap.md)), the live deployment should be exercised across real browsers, dynamic subprocess boundaries, unattended system timers, and routine Git delta updates.

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
* [x] **Compression, Security Headers & Dynamic CSP Nonce Audit** *(Verified 2026-11-17)*:
  * Verified `Content-Encoding: gzip` + `Cache-Control: public, max-age=31536000, immutable` + `Vary: Accept-Encoding` on static JS (`tex-svg-full.js`).
  * Verified `Content-Encoding: gzip` (`38.5 KB` payload including SVG math sprites), `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, and per-request cryptographic `Content-Security-Policy` `'nonce-...'` rotation on cached HTML subtopic pages (`/physics/subtopic/schwarzschild-metric`).

---

## 3. Reverse-Proxy (Anubis) & Client IP Rate-Limiting Verification

* [x] **Pre-Anubis / Post-Anubis Proxy Topology Verified** *(Verified 2026-11-17)*:
  * Apache terminates public HTTPS (`access_pre-anubis_https_physicslab.log`, recording real caller IPs), passes traffic through **Anubis** anti-scraper protection, and forwards verified requests to the backend listener (`access_post-anubis_https_physicslab.log` on `127.0.0.1`).
  * [`AuthService::resolveClientIp()`](../app/logic/AuthService.php) already trusts `127.0.0.1` and extracts `X-Forwarded-For` / `X-Real-IP` forwarded by the proxy/Anubis layer so per-IP CAS rate-limiting buckets remain isolated per visitor.

---

## 4. Unattended Reliability ("Set-and-Forget" Server Checks)

Three quick checks on Debian 13 prevent silent operational failures weeks or months after launch:

* [x] **Reboot Auto-Start Survival** *(Verified 2026-11-17)*:
  * Verified `apache2`, `php8.4-fpm`, and `mariadb` are `enabled`, and `anubis@physicslab.ca.service` (`Anubis Web AI Firewall Instance - physicslab.ca`) is `loaded active running`.
* [x] **60-Day Let's Encrypt TLS Renewal Dry-Run** *(Verified 2026-11-17)*:
  ```bash
  sudo certbot renew --dry-run
  ```
  Verified: `Congratulations, all simulated renewals succeeded: /etc/letsencrypt/live/physicslab.ca/fullchain.pem (success)`.
* [x] **Canonical Host & HTTPS Redirects (`301`)** *(Verified 2026-11-17)*:
  * Verified `http://physicslab.ca/` returns `301 Moved Permanently` $\rightarrow$ `https://physicslab.ca/`.
  * Canonical host policy is bare **`https://physicslab.ca`** only (matching `jholobetz.ca`); unintended registrar `www` DNS record removed in DNS panel.
* [x] **Disable Production Xdebug** *(Verified 2026-11-17)*:
  * Detected `20-xdebug.ini` across `apache2`, `fpm`, and `cli`; disabled via `sudo phpdismod xdebug` and reloaded `php8.4-fpm` + `apache2` to eliminate Zend hook overhead and stack-trace log noise.

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
2. **"How It All Connects" Discovery Features** ([`docs/ideas.md`](../docs/ideas.md)):
   * *"Surprise Me With a Bridge"* cross-domain multi-hop launcher, Equation Explainer derivation journey breadcrumbs, and one-click *"Copy as SymPy / Python"* export snippets.
3. **Mathematical & Interactive Depth**:
   * Expanding multi-step derivation proofs beyond the initial `104` canonical proofs toward all high-traffic Topic Hub equations, interactive series/classical-limit sliders in the Equation Explainer, Wave 2 simulation elevations, or deferred `fluids-nonlinear.json` curriculum enrichment (`2.8`).
4. **Zero-Cookie Server Traffic Summary**:
   * Optional read-only diagnostic script on Debian 13 summarizing Apache `access.log` hits and `404`s with zero cookies or third-party trackers.
