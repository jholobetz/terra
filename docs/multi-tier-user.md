# Multi-Tier User Authentication & Content Curation Architecture

**Document Version:** 2.0  
**Date:** August 2026  
**Status:** Architectural Specification & Implementation Roadmap  
**Target Systems:** Flight PHP Microframework, MariaDB, JSON Shard Storage, Web Frontend  

---

## 1. Executive Summary

This specification defines the multi-tier authentication and role-based access control (RBAC) architecture for the **Terra Physics Platform**. It addresses the security requirements of an open public web application while maintaining high developer velocity across a dual **Development (`localhost`) vs. Production** deployment lifecycle.

It establishes:
1. **The Security Threat Model** for open-web equation and prose editing.
2. **The 4-Tier Role Hierarchy** (`Guest`, `Contributor`, `Curator`, `Administrator`).
3. **The Dual-Driver Authentication Engine** (Live Federated OAuth2 in production; zero-friction one-click impersonation in local development).
4. **The Staging & Quarantine Pipeline** (`formula_reviews` table preventing unauthorized shard mutation).
5. **Immediate Implementation Strategies** for fluid launch timelines.

---

## 2. Security Threat Model for Open Web Editing

Allowing public web clients to modify physics equations and narrative prose introduces significant attack vectors that require strict mitigation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                          Public Attack Vectors                         │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Shard & Database    │ Malicious actors or automated bots overwriting   │
│ Vandalism / Spam    │ canonical physics formulas with corrupt data.    │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Stored XSS &        │ Malicious scripts injected via TeX/HTML payloads │
│ MathJax Injection   │ executing in other visitors' browsers.           │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Regex Denial of     │ Crafted LaTeX expressions with catastrophic      │
│ Service (ReDoS)     │ backtracking stalling PHP worker threads.        │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Path Traversal      │ Malicious formula IDs attempting directory       │
│ & File Corruption   │ traversal outside `app/config/content/formulas/`.│
└─────────────────────┴──────────────────────────────────────────────────┘
```

---

## 3. The 4-Tier Role & Privilege Hierarchy

To balance open community contributions with strict academic integrity, permissions are segregated into four tiers:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Role Hierarchy & Privileges                     │
├─────────────┬──────────────────────────────────────────────────────────┤
│ Tier 0      │ Anonymous Guest (Visitor / Reader)                       │
│             │ • Read-only access to formulas, graphs, sandboxes.       │
│             │ • Can use interactive solvers and simulation sandboxes.  │
├─────────────┼──────────────────────────────────────────────────────────┤
│ Tier 1      │ Contributor (Student / Physics Enthusiast)               │
│             │ • Can suggest equation/prose fixes in the Web UI.        │
│             │ • Submissions land in `formula_reviews` quarantine table.│
│             │ • Authorship attribution tracked on approved edits.      │
├─────────────┼──────────────────────────────────────────────────────────┤
│ Tier 2      │ Curator (Verified Physicist / Domain Expert)             │
│             │ • Can review, diff, edit, and approve suggested fixes.   │
│             │ • Can directly invoke `fixlatex` pipeline on formulas.   │
│             │ • Writes directly to Shard JSON & MariaDB tables.        │
├─────────────┼──────────────────────────────────────────────────────────┤
│ Tier 3      │ Administrator (Core Maintainer)                          │
│             │ • Full Shard & Database sync rights.                     │
│             │ • Can trigger repo-wide batch sweeps and rollback logs.  │
│             │ • User role management, API keys, and audit log access.  │
└─────────────┴──────────────────────────────────────────────────────────┘
```

---

## 4. Development vs. Production Dual-Driver Model

To avoid requiring live OAuth callback URLs, internet connectivity, or client secrets during local development, the system employs a **Dual-Driver Auth Adapter**:

```
                              ┌─────────────────────────────┐
                              │     AuthAdapterFactory      │
                              └──────────────┬──────────────┘
                                             │
                      ┌──────────────────────┴──────────────────────┐
                      ▼                                             ▼
       ┌─────────────────────────────┐               ┌─────────────────────────────┐
       │   Production (Live OAuth)   │               │   Development (Mock RBAC)   │
       ├─────────────────────────────┤               ├─────────────────────────────┤
       │ • GitHub / Google OAuth2    │               │ • Quick-Switch Dev Toolbar  │
       │ • Strict CSRF & State Token │               │ • Zero internet required    │
       │ • Encrypted Session Cookie  │               │ • Impersonate Any Tier      │
       └─────────────────────────────┘               └─────────────────────────────┘
```

### 4.1 Production Mode (`APP_ENV=production`)
* **Federated Identity (GitHub & Google OAuth2)**:
  * Eliminates password storage, hashing overhead, and credential stuffing attacks on MariaDB.
  * Offloads two-factor authentication (2FA) enforcement to upstream providers.
* **Session Security**:
  * Employs encrypted, `HttpOnly`, `SameSite=Strict`, `Secure` session cookies.
  * Enforces state parameter verification on all OAuth callbacks to prevent login CSRF.

### 4.2 Development Mode (`APP_ENV=development`)
* **One-Click Role Impersonation**:
  * A lightweight, floating dev toolbar on `localhost:8000` allows clicking one button to switch roles:
    * `[Switch to Guest]`
    * `[Switch to Contributor]`
    * `[Switch to Curator]`
    * `[Switch to Admin]`
* **Zero External Dependencies**:
  * Works 100% offline without network requests, OAuth client keys, or mock callback servers.

---

## 5. Database Schema Specifications (MariaDB)

Three relational tables manage user identity, the staging review quarantine, and historical audit logs:

```sql
-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    oauth_provider ENUM('github', 'google', 'dev_mock') NOT NULL,
    oauth_id VARCHAR(191) NOT NULL,
    email VARCHAR(191) NOT NULL,
    display_name VARCHAR(191) NOT NULL,
    avatar_url VARCHAR(512),
    role ENUM('guest', 'contributor', 'curator', 'admin') NOT NULL DEFAULT 'contributor',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_oauth (oauth_provider, oauth_id),
    KEY idx_email (email),
    KEY idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Staged Review Queue (Quarantine for Tier 1 Contributor Suggestions)
CREATE TABLE IF NOT EXISTS formula_reviews (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    formula_id VARCHAR(191) NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    proposed_latex TEXT,
    proposed_prose JSON,
    hint_text TEXT,
    status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    reviewed_by BIGINT UNSIGNED NULL,
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    KEY idx_formula_status (formula_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Audit Log (Tracks every change committed to Shards/DB)
CREATE TABLE IF NOT EXISTS formula_audit_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    formula_id VARCHAR(191) NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,
    action ENUM('direct_repair', 'approved_review', 'rollback', 'batch_sweep') NOT NULL,
    before_snapshot JSON NOT NULL,
    after_snapshot JSON NOT NULL,
    applied_diff TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    KEY idx_formula_action (formula_id, action)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 6. Flight PHP Middleware & Route Protection Architecture

Route-level middleware enforces role-based access control cleanly without polluting controller logic:

```php
// app/middleware/AuthMiddleware.php

// 1. Global Session Hydration
Flight::route('/physics/*', function() {
    $sessionToken = Flight::request()->cookies['terra_session'] ?? null;
    
    // In development mode, check for dev impersonation cookie
    if (Flight::get('env') === 'development' && isset(Flight::request()->cookies['dev_mock_role'])) {
        $mockRole = Flight::request()->cookies['dev_mock_role'];
        Flight::set('currentUser', (object)[
            'id' => 1,
            'display_name' => "Dev {$mockRole}",
            'role' => $mockRole,
            'is_dev' => true
        ]);
        return true;
    }
    
    $user = AuthService::resolveUser($sessionToken);
    Flight::set('currentUser', $user ?? (object)['role' => 'guest']);
    return true;
});

// 2. Role Verification Factory
function requireRole(array $allowedRoles) {
    return function() use ($allowedRoles) {
        $user = Flight::get('currentUser');
        if (!in_array($user->role ?? 'guest', $allowedRoles, true)) {
            if (Flight::request()->ajax) {
                Flight::json([
                    'success' => false,
                    'error' => 'Forbidden: Insufficient role privileges.'
                ], 403);
            } else {
                Flight::redirect('/login?redirect=' . urlencode(Flight::request()->url));
            }
            return false;
        }
        return true;
    };
}

// 3. Protected API Routes Mapping

// Contributor Tier: Submit Suggestion to Review Quarantine
Flight::route('POST /api/physics/suggest-repair', requireRole(['contributor', 'curator', 'admin']), function() {
    $data = Flight::request()->data;
    ReviewService::createSuggestion(Flight::get('currentUser')->id, $data);
    Flight::json(['success' => true, 'message' => 'Suggestion submitted for review.']);
});

// Curator Tier: Direct Repair Pipeline Execution & Approval
Flight::route('POST /api/physics/apply-repair', requireRole(['curator', 'admin']), function() {
    $data = Flight::request()->data;
    $result = PhysicsRepairService::executeRepair($data->formula_id, $data->latex, $data->hint);
    AuditService::logRepair(Flight::get('currentUser')->id, $result);
    Flight::json(['success' => true, 'data' => $result]);
});

// Admin Tier: Repository Batch Sweep & User Management
Flight::route('POST /api/physics/admin/batch-sweep', requireRole(['admin']), function() {
    $report = BatchRepairService::runAll();
    Flight::json(['success' => true, 'report' => $report]);
});
```

---

## 7. Implementation Options for Fluid Launch Timelines

When the launch timeline is undetermined (days, weeks, or months away), the following implementation strategies provide maximum utility today with zero throwaway code:

| Strategy | Scope Built Today | Launch Day Action | Pros |
| :--- | :--- | :--- | :--- |
| **Option 1: Core RBAC + Dev Switcher** *(Recommended)* | • Full schema (`users`, `formula_reviews`, `audit_logs`)<br>• Flight middleware & API routes<br>• In-App Quick Fix Drawer<br>• Dev Role Switcher | Add `GITHUB_CLIENT_ID` and `SECRET` to `.env` (5 mins) | **100% Launch-Ready today**; full in-app editing and review workflow active on localhost immediately. |
| **Option 2: Review Queue & Live Diff First** | • Staging quarantine (`formula_reviews`)<br>• In-browser side-by-side MathJax diff preview<br>• Approval CLI tool | Hook auth middleware to endpoints (1 hour) | Focuses purely on the review workflow before session setup. |
| **Option 3: Staging Key Hybrid** | • Everything in Option 1<br>• CLI Token Generator (`scripts/generate-token`) | Switch from token gating to OAuth (5 mins) | Allows deploying to a private staging server/VPS prior to public launch. |

---

## 8. Summary & Next Steps

Implementing **Option 1 (Core RBAC + Dev Switcher)** delivers immediate developer productivity:
* You gain an in-browser equation repair drawer and side-by-side diffing immediately on `localhost:8000`.
* The staging queue guarantees that public users cannot corrupt production shards upon launch.
* The system is 100% launch-ready with zero code rewrites required.
