# Physics Lab / Project Terra — Post-Launch Full-Codebase Audit

> **Status**: Read-Only Full-Codebase Post-Launch Audit — **2026-11-19**  
> **Baseline Commit**: `5ec4b2185` (`origin/master`, live on `https://physicslab.ca`)  
> **Scope**: 6 parallel read-only audit tracks covering PHP controllers/services/middleware, dual-layer MariaDB/JSON synchronization, views/JS/CSS/WebGL simulations, Python SymPy CAS & maintenance tooling, the live 14,684-formula / 1,584-subtopic data manifold, and the Pytest/PHPUnit/CI verification harness.  
> **Policy**: Zero source files were modified during this evaluation. Every finding below cites exact `file:line` evidence for prioritized review and remediation planning.

---

## 1. Executive Scorecard

| Severity | Count | Summary |
| :--- | :---: | :--- |
| **P0 — Critical** | **7** | Public SymPy CAS Python RCE, least-privilege DB sync silent skip, disabled subcomponent integrity check, active LaTeX/prose corruptors (`\bar{}`, `Landau`), destructive error fallbacks, and untested API/Admin/Sync layers. |
| **P1 — High** | **27** | Flight v3 HTTP status clobbering (`200 OK`), `exit;` dropping CSP/HSTS headers, exposed `public/cache/*`, broken MariaDB formula search, CSP-blocked curator buttons & hover/focus handlers, broken Universe Graph search, CAS timeout swallowing, `gqs.py` / `scripts/assess` bugs, and live data manifold broken links. |
| **P2 — Medium** | **15** | Stored/reflected DOM injection in curator/graph views, unhandled `fetch()` promises, CSP/HSTS hardening gaps, OOM risk in 512M workers, Cost Governance CLI gaps, and weakened/tautological tests. |
| **P3 — Low** | **9** | `~203.3 MB` of orphaned/duplicate JSON artifacts, 8 dead JS files, stale hardcoded counts in templates, inconsistent `BASE_URL`, PSR-4 case mismatches, and minor hygiene items. |
| **Total** | **58** | **Actionable, evidence-backed findings across all 6 tracks.** |

### Verified Clean Baselines (What Passed Inspection)
- **All 17 interactive simulations** in [`app/config/simulations.json`](../app/config/simulations.json) map 1-to-1 to [`public/js/simulations/`](../public/js/simulations/), pass `node --check` syntax validation, and match DOM IDs in [`simulation_page.php`](../app/views/physics/simulation_page.php).
- **All 25 PHP views** carry `nonce="<?= $nonce ?>"` on every executable `<script>` tag, with zero `localhost:8000`, local file URIs, `eval(`, `new Function(`, or `javascript:` URLs in first-party views, JS, or CSS.
- **All `/physics/*` routes** referenced in views and JS resolve cleanly against [`app/config/routes.php`](../app/config/routes.php).
- **All 12 Topic Hub manifests** (`hub_manifests/*.json`) are synchronized with [`app/config/content/topics/`](../app/config/content/topics/) (verified post-`5ec4b2185`), and all **256 formula shards** match [`formulas_hash_registry.json`](../app/config/formulas_hash_registry.json).

---

## 2. P0 — Critical Findings (Immediate Remediation Required)

### P0-1. Arbitrary Python Remote Code Execution (RCE) in Public SymPy CAS Engine
- **Track**: Track 4 (Python & Tooling) + Track 2 (Routes & Security)
- **Locations**: [`lib/cas/cas_engine.py#L97`](../lib/cas/cas_engine.py#L97), [`#L127`](../lib/cas/cas_engine.py#L127), [`#L211`](../lib/cas/cas_engine.py#L211), [`#L593`](../lib/cas/cas_engine.py#L593), [`#L742-L743`](../lib/cas/cas_engine.py#L742-L743), [`#L778`](../lib/cas/cas_engine.py#L778), [`#L868-L869`](../lib/cas/cas_engine.py#L868-L869), [`#L950`](../lib/cas/cas_engine.py#L950); [`lib/cas/derivation_prover.py#L286`](../lib/cas/derivation_prover.py#L286), [`#L299-L300`](../lib/cas/derivation_prover.py#L299-L300); exposed via unauthenticated `POST /physics/api/cas-evaluate` in [`app/controllers/PhysicsController.php#L797-L859`](../app/controllers/PhysicsController.php#L797-L859).
- **Evidence**: `parse_expr()` and `sympy.sympify()` invoke Python `eval()` with default `__builtins__` exposed (`__import__` is not shadowed). Inputs such as `limit_to`, `custom_vars`, and raw `lagrangian` bypass `latex_to_sympy_str()` and reach `sympify()` / `parse_expr()` directly. Verified in `.venv/bin/python3` that a crafted payload executes arbitrary OS commands under the `www-data` PHP-FPM user.
- **Remediation**: Lock down `global_dict={'__builtins__': {}}` with an explicit allowlist of SymPy symbols/functions across every `parse_expr()` / `sympify()` call; reject dunder tokens (`__`), attribute access (`.`), and non-math syntax via an AST pre-validator before parsing; and strictly validate/allowlist all JSON payload keys in `PhysicsController::apiCasEvaluate()`.

### P0-2. Least-Privilege DB User Silently Skips All 256 Formula Shard Syncs
- **Track**: Track 1 (Sync & Parity)
- **Locations**: [`app/logic/ShardSyncService.php#L154-L178`](../app/logic/ShardSyncService.php#L154-L178), [`#L252-L256`](../app/logic/ShardSyncService.php#L252-L256).
- **Evidence**: `ensureFormulasSchema()` and `CREATE TABLE IF NOT EXISTS shard_sync_state` execute inside the same `try` block immediately before reading `shard_sync_state`. On a least-privilege production DB user lacking `CREATE`/`ALTER` DDL privileges, the `catch` block triggers, sets `$dbShardHashes = null`, falls back to the Git-tracked `formulas_hash_registry.json`, compares it against itself, and reports `shards_changed = 0` with exit code `0`—silently skipping all 256 formula shards during deployment.
- **Remediation**: Separate schema DDL checks from `SELECT` reads of `shard_sync_state`; treat a `shard_sync_state` read failure as a hard sync error (non-zero exit) rather than falling back to the Git hash registry.

### P0-3. `integrity_shield.py` Silently Disables 100% of Broken Subcomponent Checks
- **Track**: Track 4 (Python & Tooling) + Track 6 (Test & Coverage)
- **Location**: [`integrity_shield.py#L214-L218`](../integrity_shield.py#L214-L218).
- **Evidence**: The dangling subcomponent check contains an inverted type guard (`and not isinstance(child_id, str)`), which always evaluates to `False` for string formula IDs. As a result, broken string subcomponent references across all 14,684 formulas are silently ignored during sitewide integrity audits.
- **Remediation**: Remove the inverted `not isinstance(child_id, str)` condition, run `integrity_shield.py` to surface any previously masked broken subcomponent links, and add a unit test with a synthetic broken subcomponent to guarantee the gate fails loudly.

### P0-4. Formula Pipeline Prose Sanitizer Corrupts Valid `\bar{...}` (and `\star{...}`)
- **Track**: Track 4 (Python & Tooling)
- **Location**: [`lib/pipeline/formula_pipeline.py#L199`](../lib/pipeline/formula_pipeline.py#L199).
- **Evidence**: An unconditional `.replace("ar{", r"\bar{")` turns valid `\bar{x}` into `\b\bar{x}` and corrupts `\star{...}` whenever formula prose passes through the sanitizer.
- **Remediation**: Replace the bare substring replacement with a word-boundary / negative-lookbehind regex (e.g., matching control-character `\x08ar{` or standalone unescaped tokens) and add regression tests for `\bar{x}`, `\star{x}`, and `\varphi`.

### P0-5. `fix_equation_by_url.php` Corrupts `Landau` $\to$ `Lan\tau`
- **Track**: Track 4 (Python & Tooling)
- **Location**: [`scripts/fix_equation_by_url.php#L153`](../scripts/fix_equation_by_url.php#L153).
- **Evidence**: `'dau' => '\\tau'` inside `strtr()` lacks any word boundary or control-character anchor, silently turning *Landau levels*, *Landau-Ginzburg*, and *Landau damping* into `Lan\tau` whenever `fixlatex` runs on affected prose.
- **Remediation**: Remove `'dau' => '\\tau'` from `strtr()` (or match only actual corrupted control bytes `\x09au` / specific malformed patterns) and add regression coverage in `tests/php/run_php_tests.php`.

### P0-6. Transient Read Error Wipes Entire Hash Registry or LaTeX Reverse Index
- **Track**: Track 4 (Python & Tooling)
- **Location**: [`lib/pipeline/formula_pipeline.py#L536-L564`](../lib/pipeline/formula_pipeline.py#L536-L564).
- **Evidence**: On any `Exception` reading `formulas_hash_registry.json` or `formulas_latex_index.json`, the code resets `hash_reg = {}` or `latex_idx = {}` and immediately overwrites the file on disk with a single-entry dictionary—destroying all 14,684 mappings on a transient lock or decode error.
- **Remediation**: Fail fast on read/parse exceptions instead of defaulting to `{}` (only initialize `{}` when the file genuinely does not exist), and use atomic temp-file + `os.replace()` writes.

### P0-7. Zero Behavioral Test Coverage on Critical API, Admin, Review, and Sync Surfaces + Selective `pre-push` Hook
- **Track**: Track 6 (Test & Coverage)
- **Locations**: [`tests/php/run_php_tests.php`](../tests/php/run_php_tests.php), `.git/hooks/pre-push` (lines 6–11).
- **Evidence**:
  - **0 behavioral tests** cover all 9 public JSON API endpoints (`/physics/api/*`), `AdminController` (0/14 actions), `ReviewController` (0/7 actions), `FormulaReviewService` (0/10 methods), and `ShardSyncService::performSync()`.
  - The local `.git/hooks/pre-push` hook only triggers `composer test` / `pytest` on specific file patterns, skipping both suites entirely on pure PHP/JS/view changes.
- **Remediation**: Add behavioral HTTP/service tests for public JSON APIs, RBAC/Review workflows, and `ShardSyncService::performSync()` (including least-privilege DB simulation), and update the `pre-push` hook to run `composer test` on any `app/` or `public/` diff.

---

## 3. P1 — High Findings (Functional, Auth, Parity, CSP & Data Manifold)

### A. HTTP, Auth & Security Surface (Track 2)

1. **P1-1. Flight v3 Clobbers Native `http_response_code()` Back to `200 OK`**
   - **Location**: [`app/controllers/PhysicsController.php#L128`](../app/controllers/PhysicsController.php#L128), [`#L514`](../app/controllers/PhysicsController.php#L514), [`#L804`](../app/controllers/PhysicsController.php#L804), [`#L860`](../app/controllers/PhysicsController.php#L860), [`#L966`](../app/controllers/PhysicsController.php#L966), [`#L1079`](../app/controllers/PhysicsController.php#L1079), [`#L1098`](../app/controllers/PhysicsController.php#L1098), [`#L1122`](../app/controllers/PhysicsController.php#L1122), [`#L1148`](../app/controllers/PhysicsController.php#L1148), [`#L1176`](../app/controllers/PhysicsController.php#L1176).
   - **Impact**: Degraded `/healthz` (`503`), CAS/search rate limits (`429`), `403`, and `500` API responses are silently overwritten to `HTTP 200 OK` by Flight v3's `Response::sendHeaders()`. Use `Flight::response()->status($code)` / `Flight::json($data, $code)` consistently.

2. **P1-2. `AdminController` & `ReviewController` Call `exit;`, Dropping All `SecurityHeadersMiddleware` Headers**
   - **Locations**: [`app/controllers/AdminController.php#L40`](../app/controllers/AdminController.php#L40) (and lines 117, 189, 207, 243, 282, 333, 418, 459, 520); [`app/controllers/ReviewController.php#L36`](../app/controllers/ReviewController.php#L36) (and lines 65, 93, 117, 138, 153, 170, 185, 195, 213, 228, 239, 256).
   - **Impact**: Calling `exit;` terminates execution before Flight's response lifecycle completes, stripping CSP, HSTS, `X-Frame-Options`, and `X-Content-Type-Options` from admin and review responses. Replace `echo json_encode(...); exit;` with `Flight::json(..., $code); return;`.

3. **P1-3. `public/.htaccess` Directly Exposes `public/cache/*` Over HTTP**
   - **Location**: [`public/.htaccess#L11-L13`](../public/.htaccess#L11-L13).
   - **Impact**: Because `RewriteCond %{REQUEST_FILENAME} !-f` passes existing files directly to Apache without blocking `/cache/`, clients can directly fetch `/cache/embeddings_query_cache.json`, `/cache/cas/*.json`, and raw `/cache/subtopic/*.html` (completely bypassing PHP `SecurityHeadersMiddleware` CSP/HSTS headers and per-request nonce injection). Add a `RewriteRule ^cache/ - [F,L]` rule (or move cache outside `public/`).

4. **P1-4. `AuthService::isLocalDevStudio()` Reads Spoofable Leftmost `X-Forwarded-For[0]`**
   - **Location**: [`app/logic/AuthService.php#L136-L143`](../app/logic/AuthService.php#L136-L143).
   - **Impact**: Unlike `resolveClientIp()` (which walks right-to-left over trusted proxies), `isLocalDevStudio()` inspects the leftmost `X-Forwarded-For[0]`. Behind a loopback reverse proxy (such as Anubis) if `APP_ENV` is ever misconfigured away from `production`, an attacker can spoof `X-Forwarded-For: 127.0.0.1`.

5. **P1-5. Unvalidated `$slug` Used in Filesystem Cache Read & `unlink()`**
   - **Location**: [`app/controllers/PhysicsController.php#L1296`](../app/controllers/PhysicsController.php#L1296), [`#L1301`](../app/controllers/PhysicsController.php#L1301), [`#L1318`](../app/controllers/PhysicsController.php#L1318), [`#L1325`](../app/controllers/PhysicsController.php#L1325), [`#L1496`](../app/controllers/PhysicsController.php#L1496), [`#L1503`](../app/controllers/PhysicsController.php#L1503), [`#L1510`](../app/controllers/PhysicsController.php#L1510).
   - **Impact**: `$slug` is concatenated into cache paths without a strict `/^[a-z0-9-]+$/` guard against URL-decoded path traversal (`%2F`, `../`).

6. **P1-6. `GET /physics/sync` CSRF & Open Redirect via `Referer`**
   - **Locations**: [`app/config/routes.php#L26`](../app/config/routes.php#L26), [`app/controllers/PhysicsController.php#L510-L523`](../app/controllers/PhysicsController.php#L510-L523).
   - **Impact**: State-mutating sync is exposed over `GET` without CSRF protection and redirects directly to an unvalidated `HTTP_REFERER` header. Restrict to `POST` with CSRF validation and same-origin redirect allowlisting.

7. **P1-7. `apiCasEvaluate()` Unbounded `$payload` Passthrough & Anonymous `nocache=1` Disk Exhaustion**
   - **Location**: [`app/controllers/PhysicsController.php#L803-L842`](../app/controllers/PhysicsController.php#L803-L842), [`#L890-L895`](../app/controllers/PhysicsController.php#L890-L895).
   - **Impact**: `array_merge([...], $payload)` overwrites `(int)`-cast `series_order` and passes arbitrary keys/sizes past the 2,048-byte check; anonymous callers passing `nocache=1` can write unbounded `.json` files into `public/cache/cas/`.

8. **P1-8. `AuthService::switchDevRole()` Does Not Persist Across Requests**
   - **Location**: [`app/logic/AuthService.php#L197-L210`](../app/logic/AuthService.php#L197-L210).
   - **Impact**: Mutates only the in-memory object without writing to `$_SESSION` or a dev cookie, so the role switcher in `layout.php` immediately reverts on page reload.

9. **P1-9. Unclamped `limit` (`LIMIT -1` SQL Error / Full-Table Dump) & Array Query Param `TypeError` 500s**
   - **Location**: [`app/controllers/PhysicsController.php#L662-L668`](../app/controllers/PhysicsController.php#L662-L668), [`#L734-L738`](../app/controllers/PhysicsController.php#L734-L738), [`#L1056-L1075`](../app/controllers/PhysicsController.php#L1056-L1075), [`#L1163-L1164`](../app/controllers/PhysicsController.php#L1163-L1164).
   - **Impact**: Negative or huge `limit` values cause SQL errors or full-table dumps; passing array query params (e.g., `?q[]=x`) triggers unhandled `TypeError` 500s.

### B. Dual-Layer Sync, MariaDB Parity & Cache Invalidation (Track 1)

10. **P1-10. `PhysicsService::searchContent()` Formula Search Silently Broken on MariaDB**
    - **Location**: [`app/logic/PhysicsService.php#L1693-L1713`](../app/logic/PhysicsService.php#L1693-L1713).
    - **Impact**: Binding `LIMIT ?` as a string triggers a MariaDB SQL syntax error, and the query chain is missing `->fetchAll()`. The surrounding `catch (\Exception)` silently swallows the error, causing DB-backed formula searches to return zero formula matches.

11. **P1-11. `FormulaReviewService::directRepair()` Drops 13 MariaDB Columns, Downgrades `platinum` $\to$ `published`, Omits `LOCK_EX`, & Dirties Production Git Tree**
    - **Location**: [`app/logic/FormulaReviewService.php#L328-L380`](../app/logic/FormulaReviewService.php#L328-L380).
    - **Impact**: Direct repairs overwrite formula rows with a subset of columns (clearing 13 metadata fields), hardcode `status = 'published'` (downgrading `'platinum'` records), write `formulas_hash_registry.json` without `LOCK_EX`, and modify Git-tracked shard files on production—which will subsequently break `git pull --ff-only` in `scripts/update_prod.sh`.

12. **P1-12. `ShardSyncService::syncFormulasToDatabase()` Swallows Per-Shard DB Errors & Exits `0`**
    - **Locations**: [`app/logic/ShardSyncService.php#L349-L355`](../app/logic/ShardSyncService.php#L349-L355), [`cli_sync.php#L68-L73`](../cli_sync.php#L68-L73).
    - **Impact**: Individual shard SQL failures are caught and logged without incrementing an error exit code, allowing `cli_sync.php` and `update_prod.sh` to report a clean deployment despite partial database corruption.

13. **P1-13. `SemanticSearchService::search()` Performs N+1 Full-Table Scans of `subtopics`**
    - **Location**: [`app/logic/SemanticSearchService.php#L337-L356`](../app/logic/SemanticSearchService.php#L337-L356).
    - **Impact**: Calls `fetchAllData('subtopics')` inside the 14,684-formula scoring loop *before* `array_slice()`, causing severe latency and DB load on semantic search queries. Hoist the subtopic map outside the loop and resolve metadata only after slicing top-K results.

14. **P1-14. `ShardSyncService::syncIndividualTopic()` Wipes Metadata on Flat Shard Input & Omits 5 Columns**
    - **Locations**: [`app/logic/ShardSyncService.php#L465-L489`](../app/logic/ShardSyncService.php#L465-L489), [`scripts/maintenance/sync_node.php#L25`](../scripts/maintenance/sync_node.php#L25).
    - **Impact**: Expects a wrapped structure that does not match flat topic shard JSON when invoked from `sync_node.php`, wiping topic metadata and omitting 5 columns compared to `performSync()`.

15. **P1-15. Dev/Preview vs. Production Schema Shape Discrepancies**
    - **Locations**: [`app/logic/PhysicsService.php#L716-L750`](../app/logic/PhysicsService.php#L716-L750) (`loadFormula()`), [`#L1381-L1401`](../app/logic/PhysicsService.php#L1381-L1401) (`fetchAndPrepare('topics', $slug)`).
    - **Impact**: `loadFormula()` only populates `latex_source` and swaps `equation_svg` in DB mode (not JSON fallback mode); `fetchAndPrepare('topics', $slug)` fails to `json_decode()` `pillars` and `bridges` from MariaDB rows.

16. **P1-16. HTML Cache Invalidation Blind Spots**
    - **Location**: [`app/controllers/PhysicsController.php#L1821-L1883`](../app/controllers/PhysicsController.php#L1821-L1883).
    - **Impact**: `isHubCacheStale()` misses mtimes for `app/config/content/topics/{slug}.json`, `app/config/content/{slug}.json`, `categories.json`, and `math_sprites.svg`; `isCacheStale()` misses `variable_registry.json` and `search_index.json`.

### C. Views, Templates & Client-Side JS (Track 3 + Track 6)

17. **P1-17. CSP-Blocked Inline `onclick` Breaks Curator Review Approve & Reject Buttons**
    - **Location**: [`public/js/explainer_curator.js#L413-L414`](../public/js/explainer_curator.js#L413-L414).
    - **Impact**: `SecurityHeadersMiddleware` enforces `script-src 'self' 'nonce-...'` without `'unsafe-inline'`. The inline `onclick="EquationExplainer.approveReview(...)"` and `rejectReview(...)` handlers are blocked by CSP, preventing Curators/Admins from approving or rejecting suggestions in the Equation Explainer review drawer.

18. **P1-18. Full-Screen Formula Search in `FormulaLineageGraph` Always Returns Empty (API Schema Mismatch)**
    - **Location**: [`public/js/formula_graph.js#L375-L386`](../public/js/formula_graph.js#L375-L386).
    - **Impact**: Fetches `/physics/api/search?q=...&limit=8` and expects a top-level array with `item.slug`, whereas the endpoint returns `{ query, total, results: [...] }` where formula entries use `item.id`. Consequently, full-screen search on `/physics/universe-graph` and `/physics/equation-explainer` always renders `"No matching formulas found."`.

19. **P1-19. CSP-Blocked Inline `onfocus`/`onblur` and `onmouseover`/`onmouseout` Across 3 Frontend Files**
    - **Locations**: [`app/views/physics/simulations.php#L164-L165`](../app/views/physics/simulations.php#L164-L165), [`public/js/equation_explainer.js#L1859`](../public/js/equation_explainer.js#L1859), [`#L1885-L1886`](../public/js/equation_explainer.js#L1885-L1886), [`public/js/explainer_cards.js#L177`](../public/js/explainer_cards.js#L177), [`#L218`](../public/js/explainer_cards.js#L218).
    - **Impact**: Blocked by CSP, breaking interactive focus/hover styles and emitting console violation errors. Replace with CSS `:focus` / `:hover` rules.

### D. Python CAS, Maintenance Tooling & Deploy Scripts (Track 4)

20. **P1-20. `cas_engine.py` Swallows `SIGALRM` Timeouts & Has Uncaught Crashes; `latex_parser.py` Mis-parses `\nabla^2 V`**
    - **Locations**: [`lib/cas/cas_engine.py#L46`](../lib/cas/cas_engine.py#L46), [`#L108`](../lib/cas/cas_engine.py#L108), [`#L138`](../lib/cas/cas_engine.py#L138), [`#L253`](../lib/cas/cas_engine.py#L253), [`#L261`](../lib/cas/cas_engine.py#L261), [`#L966`](../lib/cas/cas_engine.py#L966), [`#L1112`](../lib/cas/cas_engine.py#L1112); [`lib/cas/latex_parser.py#L544`](../lib/cas/latex_parser.py#L544).
    - **Impact**: Broad `except Exception:` blocks catch `TimeoutError` raised by `SIGALRM`, defeating execution time limits; `latex_parser.py` translates `\nabla^2 V` into `VPhi / (L**2)` instead of a Laplacian representation.

21. **P1-21. `gqs.py formula-ingest` Uses Wrong Shard Path & Wipes `formula_payload.json`**
    - **Location**: [`gqs.py#L324-L330`](../gqs.py#L324-L330), [`#L545-L550`](../gqs.py#L545-L550), [`#L597-L598`](../gqs.py#L597-L598).
    - **Impact**: Looks for `formulas/shard_{xx}.json` instead of `formulas/{xx}/shard_{xx}.json`, skips every item in the batch, and then unconditionally wipes `formula_payload.json` to `{}`.

22. **P1-22. `fix_equation_by_url.php` Skips DB Fallback Under `--json`, Reports `success: true` on Failure, & Unescaped SQL `LIKE`**
    - **Location**: [`scripts/fix_equation_by_url.php#L451`](../scripts/fix_equation_by_url.php#L451), [`#L628-L673`](../scripts/fix_equation_by_url.php#L628-L673), [`#L713`](../scripts/fix_equation_by_url.php#L713).
    - **Impact**: JSON-mode callers (including the Admin console) miss DB fallback resolution and receive `success: true` even when repair fails; raw backslashes in LaTeX are not escaped for MariaDB `LIKE`.

23. **P1-23. `scripts/assess` Telemetry & Audit Bugs**
    - **Location**: [`scripts/maintenance/run_project_assessment.py#L437-L442`](../scripts/maintenance/run_project_assessment.py#L437-L442), [`#L1457`](../scripts/maintenance/run_project_assessment.py#L1457), [`#L1808`](../scripts/maintenance/run_project_assessment.py#L1808), [`#L2258`](../scripts/maintenance/run_project_assessment.py#L2258), [`#L2277`](../scripts/maintenance/run_project_assessment.py#L2277), [`#L2295-L2312`](../scripts/maintenance/run_project_assessment.py#L2295-L2312).
    - **Impact**:
      - `--diff` overwrites `docs/reports/latest.json` *before* diffing against it (always producing a zero diff).
      - `--changed` and `--shard` validate a non-existent `"latex"` key instead of `"equation"`.
      - `--all` mutates `formulas_hash_registry.json` during a supposedly read-only audit.

24. **P1-24. `run_gqs_sprint.py` Ignores `git commit` Failure & Risks Reverting Prior Legitimate Commit**
    - **Location**: [`scripts/maintenance/run_gqs_sprint.py#L72-L77`](../scripts/maintenance/run_gqs_sprint.py#L72-L77), [`#L209-L223`](../scripts/maintenance/run_gqs_sprint.py#L209-L223).
    - **Impact**: Sets `committed = True` without checking the exit code of `git commit`; if a subsequent rollback runs `git reset HEAD~1`, it can undo the previous unrelated commit.

25. **P1-25. `update_prod.sh --rollback` Leaves Production in Detached `HEAD` & Skips Dependency Sync**
    - **Location**: [`scripts/update_prod.sh#L199-L205`](../scripts/update_prod.sh#L199-L205).
    - **Impact**: Checking out a prior SHA directly detaches `HEAD` (breaking subsequent `git pull --ff-only` deploys until manually re-attached) and does not reconcile `composer.lock` or `requirements.txt`.

### E. Live Data Manifold & Test Blind Spots (Track 5 + Track 6)

26. **P1-26. Live Data Manifold Broken References**
    - **Locations & Counts**:
      - **1 broken hub card slug**: `dark-energy-density` in [`hub_manifests/astrophysics.json`](../hub_manifests/astrophysics.json) and [`app/config/content/topics/astrophysics.json`](../app/config/content/topics/astrophysics.json) (live slug is `dark-energy-theory`).
      - **8 mangled HTML-link `formula_ids`** across [`astrophysics.json`](../app/config/content/topics/astrophysics.json), [`classical-mechanics.json`](../app/config/content/topics/classical-mechanics.json), [`electromagnetism.json`](../app/config/content/topics/electromagnetism.json), [`relativity.json`](../app/config/content/topics/relativity.json), and [`standard-model.json`](../app/config/content/topics/standard-model.json).
      - **81 of 108 `origin_subtopic` links broken** in [`app/config/content/notation.json`](../app/config/content/notation.json).
      - **5 broken `parents` slugs**: `integrable-systems` in [`app/config/content/legacy-orphans.json`](../app/config/content/legacy-orphans.json) and `variational-principles` on 4 articles in [`theoretical-physics.json`](../app/config/content/topics/theoretical-physics.json) (live slug is `variational-principle`).
      - **1 broken alias** in [`app/config/content/formula_aliases.json`](../app/config/content/formula_aliases.json) (`relativistic-energy-momentum-relation` $\to$ `energy-momentum-relation-rest-mass-momentum`).
      - **`global_slug_registry.json` drift**: 15 live subtopics missing and 3 orphaned slugs (`dark-energy-cosmology`, `dark-energy-density`, `laplace-equation`) in [`global_slug_registry.json`](../global_slug_registry.json).

27. **P1-27. Major Unrendered Views, Zero JS Syntax Gate, & Ignored `audit_prose_equations.php` Exit Code**
    - **Locations**: [`integrity_shield.py#L443-L453`](../integrity_shield.py#L443-L453), [`tests/php/run_php_tests.php`](../tests/php/run_php_tests.php).
    - **Impact**: 11/12 topic hubs, 14/17 simulations, `home.php`, `equation_explainer.php`, `universe_graph.php`, `constants.php`, and `symbols.php` are never rendered in automated tests; `node --check` is never executed on `public/js/**/*.js`; and `integrity_shield.py` ignores non-zero exit codes from `scripts/audit_prose_equations.php`.

---

## 4. P2 — Medium Findings (Hardening, XSS, Reliability & Cost Governance)

1. **P2-1. Stored HTML/DOM Injection in Curator Review Drawer** ([`public/js/explainer_curator.js#L405-L409`](../public/js/explainer_curator.js#L405-L409)) — `author_name`, `author_role`, `proposed_latex`, and `hint_text` are interpolated raw into `innerHTML`. Escape via a DOM text helper before rendering.
2. **P2-2. Unescaped URL/API Strings in `innerHTML` & Unencoded Path/Query Interpolation** ([`public/js/equation_explainer.js#L63`](../public/js/equation_explainer.js#L63), [`#L303`](../public/js/equation_explainer.js#L303), [`#L609`](../public/js/equation_explainer.js#L609); [`app/views/physics/universe_graph.php#L271-L272`](../app/views/physics/universe_graph.php#L271-L272), [`#L345-L346`](../app/views/physics/universe_graph.php#L345-L346), [`#L360`](../app/views/physics/universe_graph.php#L360)) — Escape HTML before `innerHTML` assignment and wrap URL parameters in `encodeURIComponent()`.
3. **P2-3. Unhandled `fetch()` Promise Rejections & Missing `response.ok` Checks** ([`layout.php#L297-L307`](../app/views/physics/layout.php#L297-L307), [`explainer_curator.js#L425-L459`](../public/js/explainer_curator.js#L425-L459) including missing `notes === null` cancel guard on `prompt()`, [`equation_explainer.js#L609-L625`](../public/js/equation_explainer.js#L609-L625), [`universe_graph.php#L262-L263`](../app/views/physics/universe_graph.php#L262-L263), [`formula_graph.js#L375-L376`](../public/js/formula_graph.js#L375-L376), [`formula_inspector.js#L283-L284`](../public/js/formula_inspector.js#L283-L284), [`explainer_cards.js#L457-L467`](../public/js/explainer_cards.js#L457-L467)).
4. **P2-4. Malformed Inline CSS on Simulations Observatory Hero** ([`app/views/physics/simulations.php#L94`](../app/views/physics/simulations.php#L94)) — `align-items: gap: 4px;` is missing `center;`, invalidating both properties on `#hero-launch-link`.
5. **P2-5. Unguarded `filemtime()` in Script Cache-Busters** ([`app/views/physics/universe_graph.php#L171`](../app/views/physics/universe_graph.php#L171), [`app/views/physics/equation_explainer.php#L604-L610`](../app/views/physics/equation_explainer.php#L604-L610)) — Use `@filemtime(...) ?: 1` as in `layout.php`.
6. **P2-6. Security Header Hardening Gaps** ([`app/middlewares/SecurityHeadersMiddleware.php#L39-L46`](../app/middlewares/SecurityHeadersMiddleware.php#L39-L46)) — CSP omits `base-uri 'self'`, `object-src 'none'`, `frame-ancestors 'self'`, and `form-action 'self'`; sends deprecated `X-XSS-Protection`; and emits HSTS even over plain HTTP.
7. **P2-7. `bootstrap.php` Ignores Apache `SetEnv APP_ENV` for `display_errors = 0`** ([`app/config/bootstrap.php#L36-L42`](../app/config/bootstrap.php#L36-L42)) — Only checks `$config['app_env']` instead of also consulting `getenv('APP_ENV')` / `$_SERVER['APP_ENV']`.
8. **P2-8. Raw Exception / `stderr` Leaks, Fail-Open Unpruned Rate Limiter, & Un-locked Draft Save** ([`app/controllers/ReviewController.php#L135`](../app/controllers/ReviewController.php#L135), [`#L168`](../app/controllers/ReviewController.php#L168), [`#L211`](../app/controllers/ReviewController.php#L211), [`#L254`](../app/controllers/ReviewController.php#L254); [`app/controllers/PhysicsController.php#L1010-L1028`](../app/controllers/PhysicsController.php#L1010-L1028); [`app/controllers/AdminController.php#L455`](../app/controllers/AdminController.php#L455)).
9. **P2-9. Memory Limit Downgrade & Inconsistent `.json` vs `.json.gz` Preference** ([`app/logic/FormulaGraphService.php#L18-L20`](../app/logic/FormulaGraphService.php#L18-L20), [`app/logic/SemanticSearchService.php`](../app/logic/SemanticSearchService.php)) — `FormulaGraphService` downgrades `memory_limit` when already `-1` or `2G`, while `SemanticSearchService` prefers the 235 MB uncompressed `physics_embeddings.json` over `.json.gz` (OOM risk in 512M HTTP workers).
10. **P2-10. `PhysicsService` UTF-8 `substr()`, Unallowlisted `$table` Interpolation, & Unwrapped DB Call** ([`app/logic/PhysicsService.php#L609`](../app/logic/PhysicsService.php#L609), [`#L1264`](../app/logic/PhysicsService.php#L1264), [`#L1359`](../app/logic/PhysicsService.php#L1359), [`#L1629`](../app/logic/PhysicsService.php#L1629)) — Use `mb_substr()`, allowlist `$table` names, and guard `getFormulaGraph()`.
11. **P2-11. Cost Governance Policy Gaps in External Gemini CLI Scripts** ([`gqs.py#L640-L781`](../gqs.py#L640-L781), [`#L1004-L1161`](../gqs.py#L1004-L1161); [`scripts/maintenance/generate_gemini_formula.py#L336-L346`](../scripts/maintenance/generate_gemini_formula.py#L336-L346)) — Discard `count_tokens` results and omit `--max-cost-dollars` / `[y/N]` confirmation required by [`docs/cost_governance.md`](cost_governance.md) Pillars 1, 3, and 4.
12. **P2-12. `run_project_assessment.py` Silent Exception Swallowing & False-Pristine Fallbacks** ([`scripts/maintenance/run_project_assessment.py#L443`](../scripts/maintenance/run_project_assessment.py#L443), [`#L1341`](../scripts/maintenance/run_project_assessment.py#L1341), [`#L1606`](../scripts/maintenance/run_project_assessment.py#L1606)) — Hardcodes `A+` or prints pristine status when internal checks raise exceptions.
13. **P2-13. `fix_equation_by_url.php` Collapses `$$` to `$` & `cli_sync.php` Flag Precedence Bug** ([`scripts/fix_equation_by_url.php#L294`](../scripts/fix_equation_by_url.php#L294), [`cli_sync.php#L21-L23`](../cli_sync.php#L21-L23)) — `--sitemap --warm-cache` flag ordering can skip cache warming.
14. **P2-14. Minor Data Manifold Schema Anomalies** — 2 subtopics with mismatched `<p>`/`</p>` tags (`scleronomic-constraints` in [`classical-mechanics.json`](../app/config/content/topics/classical-mechanics.json), `invariant-reality` in [`relativity.json`](../app/config/content/topics/relativity.json)) and 1 formula missing `subcomponents` (`lorentzian-metric-signature-east-coast-spacelike-convention-e1b842e0`).
15. **P2-15. Weakened, Tautological, or Workspace-Mutating Test Suites** ([`tests/test_auth_security.py#L43-L62`](../tests/test_auth_security.py#L43-L62) only lints 9 PHP files and pins permissive ratchet `passed >= 16`; [`tests/test_assess_telemetry.py#L236`](../tests/test_assess_telemetry.py#L236) mutates live workspace and couples to disk `latest.json`; [`tests/test_audit_and_path_safety.py#L25-L70`](../tests/test_audit_and_path_safety.py#L25-L70) is tautological; [`tests/test_formula_latex_integrity.py#L174`](../tests/test_formula_latex_integrity.py#L174) skips on *any* DB error including SQL schema errors).

---

## 5. P3 — Low Findings (Hygiene, Dead Code & Cleanup)

1. **P3-1. `~203.3 MB` of Orphaned / Duplicate JSON Artifacts in `app/config/`** — 11 unused files including `195.4 MB` `global_svg_cache.json`, duplicate `1.4 KB` `app/config/content/formulas_latex_index.json`, `build_manifest.json`, and archived checkpoints.
2. **P3-2. Stale Hardcoded Counts in Templates** — [`layout.php#L150`](../app/views/physics/layout.php#L150) (fallback `16` vs 17 simulations), [`layout.php#L230`](../app/views/physics/layout.php#L230) (`14,683` vs 14,684), [`universe_graph.php#L12`](../app/views/physics/universe_graph.php#L12) (`14,681 Formulas • 14,108 Derivation Links` vs 14,684 / 14,119), and hardcoded `14,684` in [`equation_explainer.php#L12`](../app/views/physics/equation_explainer.php#L12).
3. **P3-3. 8 Unreferenced / Dead JS Assets in `public/js/`** — `cosmic_arena.js`, `diagram_engine.js`, `home_sandbox.js`, `simulations.js`, `genealogy_explorer.js`, `dist/equation_explainer.bundle.js`, `lib/tex-chtml-full.js`, and `lib/tex-mml-chtml.js`.
4. **P3-4. Inconsistent `BASE_URL` Usage** — [`layout.php#L62`](../app/views/physics/layout.php#L62) defines `BASE_URL`, while 10+ views/JS modules hardcode root-relative `/physics/...`.
5. **P3-5. Fragile Simulation Initialization** — [`public/js/simulations/gauss-law.js#L1-L4`](../public/js/simulations/gauss-law.js#L1-L4) runs immediately without `DOMContentLoaded` or DOM null guards; 12 other simulation modules omit `if (!canvas) return;`.
6. **P3-6. Minor PHP Encoding Hygiene** — [`equation_explainer.php#L593-L601`](../app/views/physics/equation_explainer.php#L593-L601) omits `JSON_HEX_*` flags on inline `json_encode()`; [`simulation_page.php#L48`](../app/views/physics/simulation_page.php#L48) omits `htmlspecialchars()` on `$slug`.
7. **P3-7. PSR-4 Namespace Case Mismatch** — `App\Logic` vs `app/logic/` in [`FormulaGraphService.php`](../app/logic/FormulaGraphService.php), [`LabToolsLauncher.php`](../app/logic/LabToolsLauncher.php), and [`VariableAggregator.php`](../app/logic/VariableAggregator.php).
8. **P3-8. `scripts/fixlineage` Uses System `python3`** — [`scripts/fixlineage#L11`](../scripts/fixlineage#L11) should invoke `.venv/bin/python3`.
9. **P3-9. `robots.txt` & Unwired Destructive Test Script** — The dynamic `/robots.txt` route in [`app/config/routes.php`](../app/config/routes.php) (`Disallow: /physics/admin/`) misses `/physics/admin` without trailing slash; [`tests/test_rbac_and_review_system.php`](../tests/test_rbac_and_review_system.php) is unwired and mutates live DB state if run directly.

---

## 6. Recommended Remediation Sequence

To minimize production risk and maximize leverage, remediations should be executed in four focused batches:

| Batch | Target Findings | Goal |
| :--- | :--- | :--- |
| **Batch 1 — Emergency Production Security & Data Safety** | `P0-1`, `P0-2`, `P1-1`, `P1-2`, `P1-3`, `P1-4`, `P1-5`, `P1-6`, `P1-7`, `P2-1`, `P2-2`, `P2-6` | Eliminate public SymPy CAS RCE, block `/cache/` HTTP exposure, fix Flight v3 status clobbering & `exit;` header stripping, fix least-privilege `ShardSyncService` silent skip, and patch DOM injection. |
| **Batch 2 — Live User-Facing Functionality & Data Manifold** | `P1-10`, `P1-13`, `P1-16`, `P1-17`, `P1-18`, `P1-19`, `P1-26`, `P2-3`, `P2-4`, `P2-14` | Restore MariaDB formula search, fix N+1 semantic search, restore Curator Approve/Reject & Universe Graph search, remove remaining inline CSP violations, and repair all broken hub/notation/parent/alias/registry links. |
| **Batch 3 — Pipeline, Audit Gate & Deploy Reliability** | `P0-3`, `P0-4`, `P0-5`, `P0-6`, `P1-11`, `P1-12`, `P1-14`, `P1-15`, `P1-20`–`P1-25`, `P2-11`–`P2-13` | Re-enable `integrity_shield.py` subcomponent checks, fix `\bar{}` / `Landau` corruptors, harden hash-registry writes, fix `scripts/assess`, `gqs.py`, `fixlatex`, and `update_prod.sh --rollback`. |
| **Batch 4 — Phase 5 Test Hardening & Repo Hygiene** | `P0-7`, `P1-8`, `P1-9`, `P1-27`, `P2-7`–`P2-10`, `P2-15`, `P3-1`–`P3-9` | Add behavioral tests for public APIs, Admin/Review, `ShardSyncService`, all 12 hubs, and JS syntax (`node --check`); tighten `pre-push`; purge `~203 MB` of orphaned JSON and 8 dead JS files. |
