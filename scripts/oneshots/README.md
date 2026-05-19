# One-shot scripts

Scripts in this directory ran once against a specific corpus state and are kept for **reference only**. They are not part of the active pipeline. Do not re-run them blindly — they may corrupt current data, since they were written against the state they operated on at the time.

When you write a new migration / patch script, place it here once it has run successfully and update this README with a one-line entry. If it might need to run again (e.g., it's idempotent and reusable), put it in `scripts/` instead.

## Archive

| Script | When it ran | What it did |
|---|---|---|
| `patch_registry.py` | 2026-05 | Added `<hub>-overview` → shard mappings to `slug_shard_map.json` for all 12 protected hubs. |
| `patch_shards.py` | 2026-05 | Seeded empty `{}` entries for 7 missing `<hub>-overview` slugs in their respective subtopic shards. Later populated with content. |
| `fix_registry.py` | 2026-05 | Added `"Hub: <Title>" → <slug>` entries to `global_slug_registry.json` for all 12 protected hubs. |
| `generate_alias_map.py` | 2026-05 | Wrote a hand-curated batch of `Term → slug` aliases to the auto-linker alias map (`subfiles/auto_link_aliases.json`). |
