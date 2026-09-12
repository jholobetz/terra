---
name: mariadb-shard-sync
description: >-
  Audit, synchronize, and maintain the dual data layer between Git JSON shards and production
  MariaDB relational tables. Enforces zero data desynchronization, validates hash registries,
  and handles safe database deployments.
---

# 🗄️ MariaDB Shard Synchronizer Skill

Use this skill whenever deploying changes to production, auditing table-versus-shard parity, or debugging database synchronization issues.

---

## 1. Architectural Model

* **Production Engine (MariaDB)**: Live queries run against `formulas`, `subtopics`, `topics`, and `reviews` tables.
* **Development Source of Truth (Git JSON Shards)**: 256 formula shards (`app/config/content/formulas/[xx]/shard_[xx].json`) and 14 subtopic JSON files in Git.
* **Synchronization Bridge**: [`app/logic/PhysicsService.php`](file:///Users/holobetj/code/gemini/terra/app/logic/PhysicsService.php) with the SHA-256 hash registry [`app/config/formulas_hash_registry.json`](file:///Users/holobetj/code/gemini/terra/app/config/formulas_hash_registry.json).

---

## 2. Synchronization Commands

```bash
# Sync modified JSON formula shards to MariaDB via hash registry
php -r '
require "app/config/bootstrap.php";
$service = Flight::physics();
$res = $service->syncFormulasToDatabase();
echo json_encode($res, JSON_PRETTY_PRINT) . "\n";
'

# Full synchronization of all subtopics and topics to MariaDB
php -r '
require "app/config/bootstrap.php";
$service = Flight::physics();
$service->performSync();
echo "Sync complete.\n";
'

# Check for orphaned database records
php -r '
require "app/config/bootstrap.php";
$service = Flight::physics();
$orphans = $service->pruneOrphans(true);
echo "Orphans found: " . count($orphans) . "\n";
'
```

---

## 3. The 3-Way Atomic Write Funnel

Whenever code writes a formula modification, it MUST use `PhysicsService::saveFormula($fId, $data)`:
1. **JSON Shard**: Writes to `app/config/content/formulas/[xx]/shard_[xx].json`.
2. **MariaDB Table**: Executes `UPDATE formulas SET ... WHERE id = ?`.
3. **LaTeX Index Trie**: Updates `app/config/formulas_latex_index.json` to keep search and aliases aligned.

Never manually edit a MariaDB row without updating its corresponding Git JSON shard, or the system will enter a split-brain state upon next deployment!
