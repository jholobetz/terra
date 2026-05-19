# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project shape

This repo is **two systems welded together**:

1. **A Flight PHP web app** (`app/`, `public/`) that serves a physics encyclopedia at routes like `/physics/topic/<slug>` and `/physics/subtopic/<slug>`. The PHP side is mostly a thin read-only renderer over JSON content.
2. **A Python + Node content pipeline** (`orchestrator.py`, `scripts/maintenance/*`, `scripts/tex2svg.js`) that authors, validates, links, and SVG-renders that JSON content.

Most "development" here means editing content via the pipeline, not changing PHP. Treat the PHP layer as stable infrastructure unless the user explicitly asks to modify it.

## The content pipeline (read this before touching content)

Authoritative spec for content style and structure: **`GEMINI.md`** (Organic Platinum Standard / OPS). It governs prose density, link minimums, identity registration, and the "Limiting Case Clause." Do not edit content without consulting it.

### Storage model — sharded relational JSON

- `app/config/content/<pillar>.json` — subtopic shards (e.g. `relativity.json`). Each file is a dict keyed by slug. A slug lives in **exactly one** subtopic shard.
- `app/config/content/topics/<slug>.json` — the 12 protected primary topic hubs (`PROTECTED_TOPICS` in `orchestrator.py`). Don't modify these without explicit permission.
- `app/config/content/formulas.json` — global registry of theoretical identities; subtopics reference entries by `formula_ids`.
- `app/config/content/search_index.json` — slug → title/snippet lookup used by auto-linker and FE search.
- `global_slug_registry.json` — title → slug map used to resolve links.
- `hub_manifests/*.json` — "curated playlists" defining which slugs surface in each hub view (logical topology, separate from physical shard).
- `global_svg_cache.json` — persistent MathJax → SVG cache (large; touched by orchestrator, generally don't hand-edit).
- `sprint.json`, `subfiles/hub_tracker.json` — work queue and graduation progress.

### Retrieving content

Use the dedicated retriever — **never grep/read shard JSON directly** for content discovery (causes context bloat / corruption risk per OPS protocol):

```
PYTHONPATH=. python3 scripts/maintenance/retrieve_concept.py <slug>
```

It auto-builds `slug_shard_map.json` and strips heavy SVG fields from the payload.

### The "Zero-Prompt" commit workflow

Content changes go through the watcher, not direct shard edits:

1. Write the new subtopic HTML to `draft.html` and new identities (if any) to `identities.json` at repo root.
2. Drop a trigger JSON into `scripts/maintenance/inbox/` shaped like `{ "slug": "...", "html": "draft.html", "identities": "identities.json" }`.
3. `maintenance_watcher.py` (long-running) picks it up and runs `commit_node.py`, which: registers identities → updates shard → runs auto-linker → renders SVG via Node → rebuilds hub caches → syncs MariaDB → runs Integrity Shield → advances `sprint.json`. On failure it restores the `.bak` shard.

Run the watcher with:

```
PYTHONPATH=. python3 scripts/maintenance/maintenance_watcher.py
```

`commit_node.py` enforces a **minimum of 1 registered identity per slug** to graduate to `standard: "platinum"` — it aborts otherwise.

### Quality gate

`integrity_shield.py` is the automated arbiter (lead violations, `**` artifacts, word count, broken formula refs, duplicate slugs across shards, protected-slug violations). Run standalone with `PYTHONPATH=. python3 integrity_shield.py`. It is also invoked at the end of every `commit_node.py` run.

### Auto-linking

`scripts/maintenance/auto_linker.py` walks platinum shards and upgrades `<strong>Term</strong>` to `<a href="..."><strong>Term</strong></a>` where `Term` (or an alias from `subfiles/auto_link_aliases.json`) resolves via `search_index.json`. `orchestrator.AMBIGUOUS_TERMS` / `TERM_ANCHORS` gate generic words like "Field", "Mass", "Spin" so they only link with a technical anchor word nearby.

### Math rendering

LaTeX → SVG happens via `scripts/tex2svg.js` (MathJax 3 SSR over `liteAdaptor`). It supports a one-shot CLI mode and a batch-from-stdin mode that `orchestrator.batch_convert_to_svg` uses. Results are memoized in `global_svg_cache.json`. Pre-rendering associated formulas is part of `commit_node.py`.

## Running the web app

```
composer install
cp app/config/config_sample.php app/config/config.php  # first time only
composer start        # → http://localhost:8000
# or
docker-compose up -d
```

Entry point is `public/index.php` → `app/config/bootstrap.php` → `services.php` + `routes.php`. Routes are wrapped in `SecurityHeadersMiddleware`. Controllers live in `app/controllers/`; views in `app/views/physics/`.

The PHP layer **reads the same JSON shards** the Python pipeline writes, with lazy shard loading driven by the requested slug (`PhysicsController::loadShardForSlug`). Hub pages are also pre-rendered into `public/cache/topic/` and `public/cache/subtopic/` by the orchestrator.

There is also a `sync_node.php` script invoked by `commit_node.py` that injects a single slug into MariaDB — the DB is a secondary index, not the source of truth.

## Conventions worth knowing

- Python scripts assume `PYTHONPATH=.` and run from repo root.
- Subtopic shards have `.bak` siblings; `commit_node.py` rewrites them on every commit and uses them as the rollback path. Don't delete `.bak` files casually.
- The 12 slugs in `orchestrator.PROTECTED_TOPICS` are LOCKED — they live in `topics/` and bypass the OPS. The Integrity Shield flags any subtopic shard that contains one of these slugs.
- Bold emphasis in content uses `<strong>` only — `**markdown**` is an OPS artifact violation.
- When a slug graduates, it goes to `standard: "platinum"`; the auto-linker only operates on platinum entries.

## What lives at repo root vs. what doesn't

Repo root holds operational state files (`sprint.json`, `build_manifest.json`, `global_svg_cache.json`, `slug_shard_map.json`, `identities.json`, `draft*.html`, `id_*.json`) and pipeline scripts (`orchestrator.py`, `integrity_shield.py`, `patch_*.py`, `count_unlinked.py`, `generate_alias_map.py`, `fix_registry.py`). These are part of the active workflow — expect them to be modified by pipeline runs.
