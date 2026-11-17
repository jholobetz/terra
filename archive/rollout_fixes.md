# 🚀 Terra Physics Lab — Development-to-Production Rollout Blueprint

> **Status**: Archived Historical Record (Stages 1–3 Completed; Stage 4 & Operations in [`docs/final_stages.md`](../docs/final_stages.md))  
> **Target Production Host**: **Debian 13 (Trixie) + Apache 2.4 + PHP 8 (8.4) + MariaDB + Python 3 `.venv` (`sympy`)** (`https://physicslab.ca`)  
> **Authoring & Release Model**: Local macOS Studio $\to$ GitHub $\to$ `git clone` / `git pull --ff-only` in `/srv/www/terra` (`DocumentRoot /srv/www/terra/public`)  
> **Authoritative References**: [`docs/final_stages.md`](../docs/final_stages.md), [`CLAUDE.md`](../CLAUDE.md), [`docs/architecture.md`](../docs/architecture.md), [`docs/ideas.md`](../docs/ideas.md), [`docs/roadmap.md`](../docs/roadmap.md), [`docs/cost_governance.md`](../docs/cost_governance.md)

---

## 1. Confirmed Target Architecture & Baseline Capabilities

### 1.1 Confirmed Production Stack & Operating Model
Per [`README.md`](../README.md#L8), [`docs/architecture.md`](../docs/architecture.md#L190-L198), [`docs/ideas.md`](../docs/ideas.md#L79-L83), and live server provisioning:
* **Operating System & Web Stack**: **Debian 13 (Trixie)** running **Apache 2.4** (`DocumentRoot` strictly pointed to `/public` using [`public/.htaccess`](../public/.htaccess)), **PHP 8** (Debian 13 native PHP 8.4 with OPcache), and **MariaDB**.
* **Authoring Model (v1 Launch)**: **Immutable Git-Driven Production** — all content/formula authoring and curation stays in the local macOS Studio $\to$ Git $\to$ synchronized into MariaDB via [`cli_sync.php`](../cli_sync.php). Public visitors are strictly read-only (`guest`), eliminating production-vs-Git split-brain.
* **Directory Isolation (`DocumentRoot /srv/www/terra/public`)**: Cloning via `git clone` into `/srv/www/terra` while pointing Apache's `DocumentRoot` strictly to `/srv/www/terra/public` keeps `.git/`, `app/config/config.php`, `vendor/`, `tests/`, `docs/`, and `cli_sync.php` outside the web root, while [`.gitignore`](../.gitignore) ensures `git pull --ff-only` never overwrites server-owned state (`config.php`, `vendor/`, `.venv/`, `app/log/`, `public/cache/`, `*_embeddings.json.gz`).
* **Filesystem Privilege Separation (`www-data`)**: Code, `vendor/`, `lib/`, and all 256 JSON shards remain **read-only** to Apache's `www-data` worker; only `app/log/` and `public/cache/` grant group-write (`2775` setgid `www-data`).

### 1.2 Baseline Production Safeguards Already Live
* **Strict Security Headers & Dynamic CSP Nonces**: [`SecurityHeadersMiddleware.php`](../app/middlewares/SecurityHeadersMiddleware.php#L18-L40) emits per-request `Content-Security-Policy` (`script-src 'self' 'nonce-...'`), HSTS, `X-Frame-Options: SAMEORIGIN`, and `X-Content-Type-Options: nosniff`. [`PhysicsController::injectLayoutDynamicTokens()`](../app/controllers/PhysicsController.php#L1168-L1179) dynamically rewrites fresh CSP nonces into disk-cached HTML pages and strips the `🛠️ Admin` studio menu for public visitors.
* **Vendored Client Math Stack**: MathJax ([`public/js/lib/tex-svg-full.js`](../public/js/lib/tex-svg-full.js)) and [`public/js/lib/math.min.js`](../public/js/lib/math.min.js) are served locally from `public/js/lib/` with zero third-party JS CDN dependencies.
* **Admin & Mutating Route Locks**: [`AuthService::isLocalDevStudio()`](../app/logic/AuthService.php#L84-L120) disables implicit localhost admin privileges whenever `APP_ENV=production`, gating `/physics/admin/*`, `/physics/sync`, `/physics/api/define-formula`, and `/physics/api/*-repair` behind `403 Forbidden` unless `X-Terra-Admin-Key` matches `TERRA_ADMIN_KEY`.
* **CAS Subprocess Safeguards**: [`PhysicsController::apiCasEvaluate()`](../app/controllers/PhysicsController.php#L319-L440) enforces a `2,048`-byte input cap, deterministic SHA-256 disk caching (`<1ms` hit), per-IP `flock(LOCK_EX)` sliding-window rate limiting (`20 req/min`), and a `2.0s` `SIGALRM` hard ceiling in [`lib/cas/cas_engine.py`](../lib/cas/cas_engine.py#L50-L51).
* **Dual-Layer MariaDB Parity**: [`ShardSyncService.php`](../app/logic/ShardSyncService.php) provides `INFORMATION_SCHEMA` auto-DDL, transactional batch synchronization, and SHA-256 hash verification across all `14,684` formulas and `1,584` OPS Platinum subtopics (`257` Pytest + `21` PHPUnit tests passing).

---

## 2. Stage 1: Critical Application Security Hardening *(✅ Completed)*

### 2.1 Unauthenticated `?preview=1` Cache-Bypass DoS *(✅ Completed)*
* **Files**: [`app/logic/PhysicsService.php`](../app/logic/PhysicsService.php#L47-L71), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L1085-L1089)
* **Resolution**: Gated `PhysicsService::isPreviewActive()` and `$isBuildMode` behind `AuthService::isLocalDevStudio()` so anonymous visitors and bots cannot trigger shard reloads or bypass HTML disk caching via `?preview=1`, `?build_mode=1`, or `physics_preview` cookies, while preserving explicit `setPreviewMode(true)` for [`cli_sync.php`](../cli_sync.php).

### 2.2 Force Tracy Debugger into `Debugger::Production` Behind Reverse Proxies *(✅ Completed)*
* **Files**: [`app/config/services.php`](../app/config/services.php#L64-L93), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L36-L44)
* **Resolution**: Bound Tracy mode explicitly to `APP_ENV === 'production' ? Debugger::Production : Debugger::Development`, guarded `TracyExtensionLoader` and `PdoQueryCapture` with `class_exists()` for `composer install --no-dev` compatibility, and sanitized internal exception / CAS `raw_output` payloads on public JSON endpoints when `APP_ENV=production`.

### 2.3 API Rate-Limiting & Cost Firewall Tightening *(✅ Completed)*
* **Files**: [`app/logic/AuthService.php`](../app/logic/AuthService.php#L28-L82), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L393-L454), [`app/logic/SemanticSearchService.php`](../app/logic/SemanticSearchService.php#L36-L77)
* **Resolution**: Added `AuthService::resolveClientIp()` (ignoring `X-Forwarded-For` / `X-Real-IP` unless `REMOTE_ADDR` is a trusted proxy and walking `X-Forwarded-For` right-to-left), wired per-IP sliding-window rate limiting onto `/physics/api/semantic-search`, and defaulted live outbound Gemini embedding calls to disabled when `APP_ENV=production` unless `DISABLE_EXTERNAL_EMBEDDING_API=0` is explicitly set.

### 2.4 Filesystem Permissions, Prod Migration Guard & Stale File Cleanup *(✅ Completed)*
* **Resolution**: Tightened HTML cache directory creation from `0777` to `0775` with atomic `LOCK_EX` writes in [`PhysicsController::renderWithLayout()`](../app/controllers/PhysicsController.php#L1153-L1159), gated `dev_mock` user seeding out of `APP_ENV=production` in [`scripts/migrations/001_create_rbac_and_review_tables.php`](../scripts/migrations/001_create_rbac_and_review_tables.php#L73-L129), and removed the empty 0-byte `app/config/PhysicsService.php` stub.

---

## 3. Stage 2: Debian 13 Packaging, Config Propagation, Cache Warmer & `/healthz` *(✅ Completed)*

### 3.1 Debian PHP `app_env` Propagation & PHP 8.4 Cleanliness *(✅ Completed)*
* **Files**: [`app/logic/AuthService.php`](../app/logic/AuthService.php#L25-L52), [`app/config/config_sample.php`](../app/config/config_sample.php#L67-L76), [`app/config/bootstrap.php`](../app/config/bootstrap.php#L56-L78), [`app/logic/SemanticSearchService.php`](../app/logic/SemanticSearchService.php#L58-L77)
* **Resolution**: Added `AuthService::resolveAppEnv()` resolving across `getenv('APP_ENV')`, `$_SERVER['APP_ENV']`, `$_SERVER['REDIRECT_APP_ENV']` (Apache `mod_rewrite` internal redirects), `$_ENV['APP_ENV']`, and `config.php` (`'app_env'` $\to$ `TERRA_CONFIG_APP_ENV`), eliminating Debian `variables_order = "GPCS"` and PHP-FPM `clear_env = yes` blind spots. Audited all PHP signatures for PHP 8.4 implicit nullable cleanliness (`0` violations) and suppressed `E_DEPRECATED`/`E_STRICT` with `display_errors = 0` when `app_env === 'production'`.

### 3.2 Minimal Debian PEP 668 Python Manifests (`requirements.txt` vs. `requirements-dev.txt`) *(✅ Completed)*
* **Files**: [`requirements.txt`](../requirements.txt), [`requirements-dev.txt`](../requirements-dev.txt)
* **Resolution**: Split Python dependencies into a minimal pure-Python production manifest ([`requirements.txt`](../requirements.txt): `sympy==1.14.0`, `mpmath==1.3.0`, zero C/Fortran compiler toolchain required inside Debian 13's PEP 668 `.venv/`) and a full Studio/CI manifest ([`requirements-dev.txt`](../requirements-dev.txt)).

### 3.3 Zero-Leak Readiness Probe (`/healthz` & `/physics/healthz`) *(✅ Completed)*
* **Files**: [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L52-L131), [`app/config/routes.php`](../app/config/routes.php#L25-L29), [`app/middlewares/SecurityHeadersMiddleware.php`](../app/middlewares/SecurityHeadersMiddleware.php#L42-L54)
* **Resolution**: Added `< 5ms` `GET /healthz` and `GET /physics/healthz` endpoints checking MariaDB (`SELECT 1`), writable `app/log/` + `public/cache/` directories, and local CAS script/interpreter presence, returning `200 OK` (`{"status":"ok","checks":{...}}`) or `503 Service Unavailable` with Tracy disabled and zero path/version leakage.

### 3.4 In-Process PHP CLI Cache Warmer (`php cli_sync.php --warm-cache`) *(✅ Completed)*
* **Files**: [`cli_sync.php`](../cli_sync.php), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L1475-L1626)
* **Resolution**: Added `PhysicsController::warmHtmlCache()` and `--warm-cache`, `--force-cache`, `--cache-only`, and `--help` flags on [`cli_sync.php`](../cli_sync.php) to pre-render all `12` Topic Hubs and `1,584` Subtopics in-process via output buffering (`LOCK_EX`), preserving 32-char CSP nonce placeholders, active pillar state, and `<!-- DEV_STUDIO_NAV_SLOT -->` without requiring a local HTTP server or `curl` loop.

---

## 4. Stage 3: Public Web Polish, Branded Error Views & SEO Discovery *(✅ Completed)*

### 4.1 Minimal Error Views (`404` / `500`) & `--no-dev` Exception Handling *(✅ Completed)*
* **Files**: [`app/views/physics/error_404.php`](../app/views/physics/error_404.php), [`app/views/physics/error_500.php`](../app/views/physics/error_500.php), [`app/config/services.php`](../app/config/services.php#L112-L122), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L218-L329), [`app/middlewares/SecurityHeadersMiddleware.php`](../app/middlewares/SecurityHeadersMiddleware.php#L26-L37)
* **Resolution**: Added minimal neutral `404` and `500` views inside [`app/views/physics/layout.php`](../app/views/physics/layout.php) (`noindex, nofollow` + CSP headers) for browser visitors and clean JSON payloads (`{"error": ..., "status": 404|500}`) for `/api/*` callers; enabled `flight.handle_errors` when `APP_ENV=production` or when Tracy (`--no-dev`) is absent; guarded `Debugger::$showBar` with `class_exists()`.

### 4.2 Dynamic SEO, Canonical URLs, OpenGraph, Favicon, `robots.txt` & `sitemap.xml` *(✅ Completed)*
* **Files**: [`app/views/physics/layout.php`](../app/views/physics/layout.php#L1-L36), [`public/favicon.svg`](../public/favicon.svg), [`app/config/routes.php`](../app/config/routes.php#L16-L20), [`app/config/bootstrap.php`](../app/config/bootstrap.php#L43-L51), [`app/controllers/PhysicsController.php`](../app/controllers/PhysicsController.php#L133-L216), [`cli_sync.php`](../cli_sync.php)
* **Resolution**: Added Host-header-safe `resolveBaseUrl()` driven by `$config['app_url']`, automatic plain-text `<meta name="description">`, `<link rel="canonical">`, and OpenGraph tags in [`app/views/physics/layout.php`](../app/views/physics/layout.php), removed public footer admin link + CSP-violating inline event attributes, added placeholder [`public/favicon.svg`](../public/favicon.svg) (`301` from `/favicon.ico`), and wired dynamic `/robots.txt` + cached `/sitemap.xml` (`1,600+` canonical URLs, regenerable via `php cli_sync.php --sitemap` or `--warm-cache`).

---

## 5. Stage 4: Moved to Active Blueprint ([`docs/final_stages.md`](../docs/final_stages.md))

Stage 4 (Debian 13 Apache `.htaccess` tuning, MariaDB least-privilege provisioning, ongoing-revision cache/migration safeguards, and the Git-native `scripts/update_prod.sh` pipeline) is tracked in [`docs/final_stages.md`](../docs/final_stages.md).
