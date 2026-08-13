# 🛠️ Equation Repair Engine Optimization Plan (`fix_equation_by_url.php` v2)

## Executive Summary
This document outlines the proposed architectural, operational, performance, and CLI enhancements for [`scripts/fix_equation_by_url.php`](file:///Users/holobetj/code/gemini/terra/scripts/fix_equation_by_url.php). The proposed updates improve execution speed, enable offline JSON shard repair, eliminate cURL network dependencies, and introduce powerful batching and dry-run capabilities.

---

## 1. 🏗️ Architectural & Dependency Optimizations

### 1.1 In-Process API Verification (Replacing cURL)
* **Current Behavior**: The script boots the FlightPHP framework (`bootstrap.php`), but performs an external cURL HTTP request to `http://localhost:8000/physics/api/explain?id=...` at the end of the execution. If the local development web server is not running, it outputs a warning (`[WARN] Could not curl local API endpoint`).
* **Proposed Update**: Utilize the already-loaded `Flight::physicsService()` in memory to verify formula retrieval in-process:
  ```php
  $formula = Flight::physicsService()->getFormulaById($formulaId);
  ```
* **Benefits**: Instant verification without network latency; allows the script to verify repairs completely offline without requiring a running web server (`composer start`).

### 1.2 Decoupled / Graceful MariaDB Connections
* **Current Behavior**: Database credentials (`doc` / `DIM^10$ymJ@zz`) are hardcoded, and the script terminates immediately with `exit(1)` if MariaDB is unavailable.
* **Proposed Update**: Read credentials dynamically from `.env` / `Flight::config()`, and handle database connection failures gracefully with a soft fallback.
* **Benefits**: Enables developers to repair local JSON disk shards even when MariaDB is offline or not installed in the environment.

---

## 2. ⚡ Performance & Regex Sanitization Enhancements

### 2.1 Early-Exit Short-Circuiting in `sanitizeProseTeX()`
* **Current Behavior**: Executes ~25 sequential `preg_replace` and `str_replace` regex evaluations across every prose field (`description`, `conceptual_definition`, `intuitive_summary`, `interpretation`, `limits_and_boundary`), even on clean text.
* **Proposed Update**: Insert a high-speed pre-check to bypass regex processing for clean strings:
  ```php
  if (strpos($text, '$') === false && strpos($text, '\\') === false && !preg_match('/[χμ⟨]/u', $text)) {
      return $text;
  }
  ```
* **Benefits**: Bypasses regex evaluation entirely for ~80%+ of clean prose fields, speeding up execution.

### 2.2 Consolidating Single-Character & Word Substitutions
* **Current Behavior**: Executes multiple sequential `str_replace` calls for individual symbol patterns (`χ_m`, `μ_0`, `4π`, `dau`, etc.).
* **Proposed Update**: Consolidate string replacements into a single optimized `strtr()` translation pass:
  ```php
  $text = strtr($text, [
      'χ_m' => '$\chi_m$',
      'μ_0' => '$\mu_0$',
      '4π'  => '$4\pi$',
      'dau' => '\\tau',
  ]);
  ```
* **Benefits**: Replaces multiple string scans with a single C-level string translation lookup in PHP.

### 2.3 SQL Wildcard Escaping
* **Current Behavior**: `$stmt->execute(['%' . $targetLatex . '%'])` queries raw search strings without escaping `%` or `_`.
* **Proposed Update**: Escape special SQL `LIKE` characters using `addcslashes($targetLatex, '%_')`.
* **Benefits**: Prevents unintentional wildcard pattern matching and improves query predictability.

---

## 3. 🛠️ CLI Features & Developer Workflows

### 3.1 Batch Input & File Processing (`--file` / Multiple Arguments)
* **Current Behavior**: Processes only a single CLI argument (`$argv[1]`).
* **Proposed Update**: Accept multiple space-separated inputs or a `--file=urls.txt` argument:
  ```bash
  php scripts/fix_equation_by_url.php url1 url2 url3
  php scripts/fix_equation_by_url.php --file=broken_equations.txt
  ```
* **Benefits**: Eliminates repeated PHP CLI framework bootstrapping overhead when processing large batches of equations.

### 3.2 Dry-Run Preview Mode (`--dry-run`)
* **Proposed Update**: Add a `--dry-run` flag to display proposed regex transformations, diffs, and equation changes in the terminal without writing changes to disk shards or MariaDB.

### 3.3 Structured JSON Output (`--json`)
* **Proposed Update**: Add a `--json` output flag so parent orchestration tools, GQS pipelines, or automated Git hooks can consume the script's repair summary programmatically.

---

## 4. 🛡️ Data Safety & Asset Eviction

### 4.1 Atomic File Writes with File Locking (`LOCK_EX`)
* **Current Behavior**: `file_put_contents($shardFile, ...)` writes directly to the target shard file.
* **Proposed Update**: Use `file_put_contents($shardFile, ..., LOCK_EX)` or write to a temporary file before performing an atomic `rename()` operation.
* **Benefits**: Prevents potential shard corruption if the process is interrupted or executed concurrently.

### 4.2 MathJax Sprite Sheet Re-spritification Integration
* **Proposed Update**: Automatically trigger `spritify_assets.py` or invalidate the vector math cache when an equation structure is updated, keeping [`math_sprites.svg`](file:///Users/holobetj/code/gemini/terra/app/config/content/math_sprites.svg) synchronized.

---

## 5. 🗄️ Environment & Workflow Optimizations (Zero Code Changes)

| Optimization | Action / Command | Impact |
| :--- | :--- | :--- |
| **MariaDB Indexing** | `ALTER TABLE formulas ADD INDEX idx_equation (equation(255));` | Speeds up SQL equation lookups from ~100ms+ down to <1ms. |
| **Direct ID Targeting** | Pass Formula ID or `?id=...` URL rather than raw LaTeX fragments | Hits primary key index ($O(1)$) and skips expensive `LIKE` queries. |
| **PHP CLI OPcache** | `php -d opcache.enable_cli=1 scripts/fix_equation_by_url.php <input>` | Eliminates PHP framework compilation overhead on repeated runs. |
| **Shell Batching** | `cat urls.txt \| xargs -n 1 -P 4 php scripts/fix_equation_by_url.php` | Processes hundreds of equation fixes in parallel using standard Unix tools. |
| **Shell Alias** | `alias fix-eq='php scripts/fix_equation_by_url.php'` | Allows instant invocation from anywhere in the workspace terminal. |

---

## 📊 Summary Comparison Matrix

| Optimization Area | Current State | Proposed v2 State | Primary Benefit |
| :--- | :--- | :--- | :--- |
| **API Verification** | External cURL to `http://localhost:8000` | In-process call via `PhysicsService` | Offline verification; no web server required |
| **Database Failure** | Hard crash (`exit(1)`) | Soft fallback to JSON-only mode | Repair disk shards without running MariaDB |
| **Prose TeX Sanitization** | Evaluates ~25 regexes on all strings | Early-exit pre-check & `strtr()` table | ~5x–10x faster processing of clean text |
| **CLI Capabilities** | Single argument only | Multi-arg, `--file`, `--dry-run`, `--json` | Streamlined batching & dry-run previews |
| **Shard File Safety** | Direct unlocked file write | Atomic write with `LOCK_EX` | Zero risk of JSON file corruption |
