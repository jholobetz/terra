# 📦 Scripts Archive

This directory contains historical, one-off migration scripts, legacy fixers, and retired prototype utilities. They have been preserved for historical reference and provenance, but are no longer part of the active production or maintenance workflow.

## 🏛️ Superseded Functionality

| Archived Script | Superseded By | Description |
| :--- | :--- | :--- |
| `repair_47_delimiters.py` | `lib.math.delimiters` & `integrity_shield.py` | One-off delimiter repair from Sprint 7. |
| `repair_corrupted_shards.py` | `sanitize_shard_control_chars.py` | One-off unicode/null repair. |
| `repair_all_shard_latex_prose.py` | `lib.math.delimiters` | Historical batch regex fixer. |
| `repair_formula_prose_math.py` | `lib.math.delimiters` | Historical math delimiter repair. |
| `clean_control_chars.py` | `sanitize_shard_control_chars.py` | Legacy blind control char stripper (deprecated). |
| `fix_all_control_chars.py` | `sanitize_shard_control_chars.py` | Legacy control character fixer. |
| `fix_reg_equations.py` | `map_prose_equation_aliases.php` | Historical registered equation patcher. |
| `convert_narrative_delimiters.py` | `lib.math.delimiters` | Early dollar/bracket converter. |
| `delimit_all_shard_prose.py` | `lib.math.delimiters` | Early global regex delimiter patcher. |
| `despritify_assets.py` | MathJax 3.x dynamic rendering | Decoupled static SVG sprites in favor of MathJax. |
| `spritify_assets.py` | MathJax 3.x dynamic rendering | Deprecated sprite generator. |
| `strip_title_html.py` | `integrity_shield.py` | One-off header tag stripper. |
| `remove_formatting_vars.py` | `lib.math.lexer` | Historical variable cleanup. |
| `migrate_physics_subdirectory_shards.py` | Shard architecture | One-time partition into `app/config/content/formulas/[00-ff]/`. |
| `reorder_hubs.php` | `app/config/categories.json` | One-time category ordering. |
| `build_platinum_hub.py` | `gqs.py` & `run_gqs_sprint.py` | Early hub prototype builder. |
| `warm_critic_cache.py` | `run_critic.py` | One-off cache pre-warmer. |
| `run_seeding_loop.sh` | MariaDB ingestion pipeline | Initial database population shell loop. |
| `audit_formula_normalization.py` | `integrity_shield.py` & `lib.math.lexer` | Dry-run normalization diff scanner. |
