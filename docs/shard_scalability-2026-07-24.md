# Database Shard Scalability & Evolution Architecture

**Document ID**: `docs/shard_scalability-2026-07-24.md`  
**Date**: July 24, 2026  
**Status**: Architectural Specification & Pipeline Scaling Strategy  
**Project**: Terra Physics Encyclopedia & Knowledge Graph Engine  

---

## Executive Summary

As Project Terra scales from thousands of physics formulas to tens of thousands of identities across Physics, Chemistry, and Biology, the number of JSON definition shards (`shard_XX.json`) will naturally grow. 

This document analyzes filesystem limits, Git performance, and PHP/MariaDB execution efficiency across Terra's target 3-stage deployment pipeline:

$$\text{Mac Dev (APFS)} \longrightarrow \text{Git Remote (GitHub)} \longrightarrow \text{LAMP Server (Linux / Apache / MariaDB / PHP)}$$

---

## Scale Threshold Analysis: How Many Shards Is "Too Many"?

| Shard Count | Formula Volume | Performance & Developer Experience (DX) Status |
| :--- | :--- | :--- |
| **1 to 200 Shards** | 0 – 10,000 | **Optimal (Current State)**. Directory scanning in PHP takes $< 10$ ms. Git status and diffs are instant. |
| **200 to 2,000 Shards** | 10,000 – 100,000 | **Acceptable, but Cluttered**. SSD directory reads take ~30 ms. Git status begins to show slight overhead. |
| **2,000+ Shards** | 100,000+ | **Threshold Trigger for Architecture Evolution**. Single-directory JSON sharding becomes inefficient. |

### Bottlenecks of 2,000+ Flat Shards:
1. **Git Repository Overhead**: Tracking thousands of tiny individual `.json` files bloats the `.git` tree and slows down `git pull` / `git push`.
2. **Directory Read (`opendir` / `glob`) Latency**: Sequential file scanning during database sync (`cli_sync.php`) consumes unnecessary CPU cycles on Linux servers.
3. **Block Allocation Waste**: File systems allocate minimum 4 KB disk blocks. Storing thousands of 1 KB JSON files wastes physical storage.

---

## Strategy Evaluation Across Deployment Stages

### Strategy 1: Increase Shard Capacity (e.g., 50 ➔ 250 / 500 Formulas per Shard)

- **Mac Dev (APFS)**: Project directory stays clean. Searching formulas via `Cmd+F` inside 400 KB JSON files is instant.
- **Git Remote (GitHub)**: Reduces total file count by **90%** (20 files instead of 200). Keeps `git clone` and repository status fast.
- **LAMP Server**: `git pull` on Linux server is instant. `cli_sync.php` opens only 20 files to populate MariaDB, finishing deployment sync in **< 0.2s**.

> **Verdict**: **Best Immediate Upgrade**. Extremely simple to adjust with near-zero code risk, giving your LAMP server deployment a huge speed boost.

---

### Strategy 2: Domain Subdirectory Partitioning (`formulas/electromagnetism/shard_1.json`)

```text
app/config/content/formulas/
  ├── electromagnetism/
  │   ├── shard_1.json
  │   └── shard_2.json
  ├── quantum_mechanics/
  │   └── shard_1.json
  ├── thermodynamics/
  │   └── shard_1.json
  └── astrophysics/
      └── shard_1.json
```

- **Mac Dev (APFS)**: **Best DX (Developer Experience)**. Files match Terra's domain mental model.
- **Git Remote (GitHub)**: **Virtually eliminates Git merge conflicts**. Developers working on different science domains touch isolated subfolders.
- **LAMP Server**: Organizes server file permissions cleanly; maps 1:1 with MariaDB category queries.

> **Verdict**: **Best Long-Term File Structure**. Keeps the codebase clean, human-readable, and modular as Terra expands into Chemistry and Biology.

---

### Strategy 3: MariaDB as Primary Source of Truth (Database-First)

- **Mac Dev (APFS)**: Allows live editing using visual SQL tools (TablePlus, phpMyAdmin), but requires exporting changes back to Git seed files.
- **Git Remote (GitHub)**: Git tracks clean `.sql` migration files or database dumps instead of thousands of JSON files.
- **LAMP Server**: **Optimal Production Performance**. Apache + PHP + MariaDB is the most battle-tested stack in history. MariaDB caches index trees in RAM (InnoDB Buffer Pool), serving queries in **< 0.1 ms**.

> **Verdict**: **Best for High-Scale Production (100,000+ Formulas)**. Leverages MariaDB's native B-tree index optimizations and RAM caching.

---

### Strategy 4: Compiled SQLite / Compressed Binary Seed (`formulas.sqlite`)

- **Mac Dev (APFS)**: Single file; allows testing without a running MariaDB server instance, but binary files cannot be inspected with text editors.
- **Git Remote (GitHub)**: **Bad for Git history**. Git cannot store line-by-line text diffs for binary SQLite files, causing `.git` repository bloat on every update.
- **LAMP Server**: No database server setup needed, but lacks the high-concurrency write performance and InnoDB RAM caching of MariaDB.

> **Verdict**: **Not Recommended** for this Git + LAMP pipeline.

---

## Recommended Hybrid Evolution Roadmap

```
[Phase 0: Current Scale]       [Phase A: 10k-50k Scale]          [Phase B: 50k+ Production Scale]
Flat Shards (50 items)   --->  Domain Folders + 250 Capacity ---> MariaDB Primary + JSON Seed Archives
(1-200 JSON files)             (20-200 JSON files)               (1 File / Direct MariaDB RAM Cache)
```

1. **Current Phase (0 – 10,000 Formulas)**:
   Maintain current flat JSON shards (50 items/shard). Performs flawlessly at current scale.
2. **Phase A (10,000 – 50,000 Formulas)**:
   Combine **Strategy 1 & Strategy 2**: Group shards into **Domain Subdirectories** (`formulas/electromagnetism/shard_1.json`) and scale capacity to **250 items per shard**. This keeps Git repo size small and file counts under 100.
3. **Phase B (50,000+ Formulas on Production LAMP)**:
   Transition to **Strategy 3 (MariaDB-First)**: MariaDB handles all live production lookups on your LAMP server via RAM-cached B-tree indexes, while JSON domain shards serve as version-controlled seed archives in Git.
