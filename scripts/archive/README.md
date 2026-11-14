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
| `build_physics_embeddings.py` | Google AI Studio embeddings / `ai_models.json` | Historical Vertex AI `text-embedding-004` batch formula embedder. |
| `build_subtopic_embeddings.py` | Google AI Studio embeddings / `ai_models.json` | Historical Vertex AI `text-embedding-004` batch subtopic embedder. |
| `run_gemini_shard_sanitizer.py` | `gqs.py` & `generate_gemini_formula.py` | Historical Vertex AI Gemini 2.5 Pro multi-threaded shard sanitizer. |
| `run_vertex_lineage_enricher.py` | `fixlineage` & `generate_gemini_formula.py` | Historical Vertex AI Gemini 2.5 lineage & derivation enricher. |
| `seed_flagship_derivations.py` | Shard `derivation_steps` & `lib.cas.derivation_prover` | One-time Tier 1 flagship derivation seeding campaign. |
| `seed_tier2_derivations.py` | Shard `derivation_steps` & `lib.cas.derivation_prover` | One-time Tier 2 derivation seeding campaign. |
| `seed_tier3_derivations.py` | Shard `derivation_steps` & `lib.cas.derivation_prover` | One-time Tier 3 derivation seeding campaign. |
| `seed_tier4_derivations.py` | Shard `derivation_steps` & `lib.cas.derivation_prover` | One-time Tier 4 domain-parity derivation seeding campaign. |
| `apply_all_heals.py` | `scripts/fixlatex` & `LatexSanitizer.php` | One-time batch formula repair runner. |
| `complete_heals_data.py` | `scripts/fixlatex` | Static dictionary payload for one-time batch formula repair. |
| `heal_all_legacy.py` | `scripts/fixlatex` | One-time legacy formula LaTeX healer. |
| `heal_legacy_macro_leaks.py` | `LatexSanitizer.php` | One-time macro leak cleanup script. |
| `heal_residual_isolated.py` | `scripts/fixlineage --heal` | One-time isolated DAG node healer. |
| `sanitize_all_shards.py` | `LatexSanitizer.php` | One-time shard prose sanitization sweep. |
| `inject_tex_attributes.py` | Dynamic MathJax 3.x rendering | Legacy static `data-tex` attribute injector. |
| `seed_physics_database.py` | `gqs.py seed` & `generate_gemini_formula.py` | Legacy un-gated Gemini formula seeder (superseded by `--allow-external-api` governance). |
| `auto_seed_gqs.py` | `gqs.py formula-auto-seed` | Legacy keyless seeder mandating `\(` inline delimiters. |
| `generate_subcomponent_formulas_vertex.py` | `generate_gemini_formula.py` | Retired Phase 3 Vertex AI batch subcomponent seeder. |
| `ops_batch_template.md` | `gqs.py template` | Retired JSON prompt template for early batch drafting. |
| `math_verification_shield.py` | `lib.cas` & `scripts/cascheck` | Prototype SymPy dimensional solver (`L, M, T` manual symbols). |
| `global_tex_repair_engine.php` | `scripts/fixlatex` & `LatexSanitizer.php` | One-off global TeX AST repair sweep. |
| `audit_prose_and_variables.py` | `integrity_shield.py` & `LatexSanitizer.php` | One-off global shard prose and variable scanner. |
| `audit_shard_anomalies.py` | `integrity_shield.py` | One-off OCR corruption and shard anomaly detector. |
| `clean_formula_prose_artifacts.py` | `LatexSanitizer.php` & `scripts.lib.delimiters` | One-off formula prose artifact cleanup script. |
| `sanitize_shard_control_chars.py` | `LatexSanitizer.php` | One-off shard TeX control-character sanitizer. |
| `retrieve_raw_latex.py` | `scripts/fixlatex` | Historical LaTeX recovery helper. |
| `reimport_shards_to_mariadb.php` | `scripts/sync_formulas_to_mariadb.php` & `ShardSyncService.php` | Legacy partial 6-column MariaDB re-importer. |
| `heal_derivation_graph.py` | `scripts/fixlineage` & `enrich_lineage_families.py` | Early local multi-tier derivation graph healer. |
| `link_formula_derivations.py` | `scripts/link_lineage` & `scripts/fixlineage` | Early automated formula lineage linker. |
| `audit_equation_components.py` | `audit_prose_equations.php` | Phase 1 subcomponent equation discovery prototype. |
| `deduplicate_formulas.py` | `PhysicsService::saveFormula()` | One-time formula deduplication campaign script. |
| `generate_formula_shard.py` | `PhysicsService::saveFormula()` | Legacy standalone formula shard generator. |
| `export_js_dictionaries.js` | `explainer_dictionary.js` | One-off JS dictionary exporter used by `generate_formula_shard.py`. |
| `map_prose_equation_aliases.php` | `audit_prose_equations.php` & `ingest_unmapped_prose_equations.php` | One-off prose equation alias matcher. |
| `auto_register_references.py` | `gqs.py` & `orchestrator.py` | Historical semantic reference registration script. |
| `check_draft_compliance.py` | `gqs.py audit` & `integrity_shield.py` | Pre-GQS live quality-gate draft watcher. |
| `format_neighbors.py` | `auto_linker.py` & `orchestrator.py` | Pre-GQS neighbor bolding formatter. |
| `generate_adoption_suggestions.py` | `gqs.py` & `auto_linker.py` | One-off cross-link adoption suggestion generator. |
| `generate_hub_tracker.py` | `gqs.py status` & `scripts/assess` | Legacy hub completion tracker. |
| `generate_orphans_list.py` | `gqs.py status` & `integrity_shield.py` | One-off orphan subtopic list dumper. |
| `generate_search_index.py` | `orchestrator.py` | Standalone search index prototype superseded by `orchestrator.py`. |
| `generate_substandard_report.py` | `gqs.py status` & `scripts/assess` | Legacy pre-graduation substandard article reporter. |
| `generate_unlinked_freq.py` | `auto_linker.py` | One-off unlinked term frequency counter. |
| `list_backlog_candidates.py` | `gqs.py status` & `sync_backlog.py` | Legacy backlog candidate printer. |
| `maintenance_watcher.py` | `gqs.py ingest` & `run_gqs_sprint.py` | Retired inbox file-watcher daemon. |
| `retrieve_concept.py` | `gqs.py` | Legacy single-concept JSON reader helper. |
| `scaffold_upgrade.py` | `gqs.py template` | Pre-GQS subtopic upgrade scaffolder. |

