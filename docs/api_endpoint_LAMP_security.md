# API Endpoint Security Architecture for LAMP Deployments

**Document ID**: `docs/api_endpoint_LAMP_security.md`  
**Date**: July 24, 2026  
**Status**: Architectural Specification & Security Standard  
**Project**: Terra Physics Encyclopedia & Knowledge Graph Engine  

---

## Executive Summary

The **One-Click Gemini AI `Define` Button Engine** introduces an API endpoint (`POST /physics/api/define-formula`) that generates complete formula definitions, appends JSON records to database shards (`shard_XX.json`), and updates MariaDB in real time.

While open API endpoints are convenient in a local Mac development environment, deploying to a public **LAMP server** (Linux / Apache / MariaDB / PHP) introduces two major threat vectors:
1. **API Quota Exhaustion & Financial Cost**: Unauthenticated web users or malicious bots spamming the endpoint to exhaust Gemini API quotas.
2. **Database Vandalism**: Unauthorized requests writing junk or malicious payloads into production database shards.

This document specifies a **5-Layer Security Architecture** that completely secures the endpoint on public LAMP servers while keeping the developer experience 100% seamless.

---

## 5-Layer Security Architecture

```
[Incoming POST Request] ──► [Layer 1: Env & Secret Key] ──► [Layer 2: Rate Limiter] ──► [Layer 3: Payload Sanitizer] ──► [Gemini AI & DB Sync]
                                     │
                          (Invalid Key / Unauthorized)
                                     │
                                     ▼
                          [403 Forbidden (< 1 ms)]
```

---

### Layer 1: Secret Developer Token Guard (`X-Terra-Admin-Key`)

- A strong secret key is defined in server configuration or environment variables (`app/config/config.php`):
  ```php
  'admin_define_key' => process.env('TERRA_ADMIN_KEY') ?: 'terra_dev_secret_key_default'
  ```
- **Browser Authentication**: On your local browser or admin console, the secret key is saved once in `localStorage` (`localStorage.setItem('terra_admin_key', 'your-secret-key')`).
- **AJAX Header**: When clicking **`[ ✨ Define ]`**, JavaScript attaches the header:
  ```javascript
  headers: {
      'Content-Type': 'application/json',
      'X-Terra-Admin-Key': localStorage.getItem('terra_admin_key') || ''
  }
  ```
- **PHP Enforcement**: If the incoming `X-Terra-Admin-Key` header is missing or does not match the server secret key, PHP immediately aborts execution with `403 Forbidden` in **< 1 millisecond**, consuming zero Gemini API quota or database resources.

---

### Layer 2: Environment Gating (`APP_ENV=development` vs `production`)

- **Local Mac (`APP_ENV=development`)**: Token enforcement is relaxed for rapid development, allowing local execution automatically.
- **LAMP Production (`APP_ENV=production`)**: Strict token enforcement is mandatory. Any request without a valid admin token is blocked.

---

### Layer 3: Rate Limiting & Anti-Spam Throttling

To protect against brute-force key guessing or API quota exhaustion:
- The PHP controller tracks request frequency per IP address in session memory:
  - **Limit**: Maximum **5 definition requests per 10 minutes** per IP.
- Excess requests return `429 Too Many Requests`.

---

### Layer 4: TeX Payload Sanitization & Schema Validation

Before passing input to Gemini AI or writing to disk:
1. **Input Payload Cap**: Capped at maximum 500 characters to prevent buffer overflow or prompt injection.
2. **TeX Character Sanitization**: Strips executable code markers (`<?php`, `<script>`, shell escape characters).
3. **Strict JSON Schema Validation**: The JSON returned by Gemini AI must pass Terra's strict schema validator (`title`, `conceptual_definition`, `intuitive_summary`, `interpretation`, `symmetry_origin`, `limits_and_boundary`, `semantic_variables`) before writing to disk.

---

### Layer 5: Audit Trail Logging & Shard Synchronization

Every formula defined on the production LAMP server is logged to an audit trail (`app/config/logs/definition_audit.log`):
```text
[2026-07-24 18:25:00] FORMULA DEFINED: id="greens-function-position-space" | IP=127.0.0.1 | Shard=shard_52.json
```
Production shard updates can be easily pulled down to your local Mac development environment via `git pull`.

---

## Threat Mitigation Matrix

| Threat Vector | Without Security | With 5-Layer Security Architecture |
| :--- | :--- | :--- |
| **Public Web Users** | Can trigger API calls | Blocked instantly (`403 Forbidden`) |
| **Malicious Bots / Scrapers** | Can exhaust Gemini API quota | Blocked by Token Guard & Rate Limiter |
| **Database Vandalism** | Junk data added to MariaDB | Prevented via Token Guard & Schema Validation |
| **Developer Overhead** | Low | **Zero Overhead** (Saved once in browser `localStorage`) |
