<?php

namespace app\logic;

use flight\Engine;

/**
 * ShardSyncService
 *
 * Dedicated service for synchronizing version-controlled Git JSON shards
 * (256 formula shards, 13 subtopic domain shards, and topic hubs) into
 * the MariaDB relational engine, managing SHA-256 hash registries,
 * auto-provisioning DDL migrations, and pruning orphaned records.
 */
class ShardSyncService
{
    protected Engine $app;
    protected PhysicsService $physicsService;

    public function __construct(Engine $app, PhysicsService $physicsService)
    {
        $this->app = $app;
        $this->physicsService = $physicsService;
    }

    /**
     * Ensures the MariaDB `formulas` table and all columns/indexes exist using
     * INFORMATION_SCHEMA introspection (zero blind ALTER TABLE exceptions).
     *
     * @param mixed $db PDO wrapper instance
     * @return bool True if any missing column was newly added (requiring a full backfill)
     */
    public function ensureFormulasSchema($db): bool
    {
        if (!$db || !method_exists($db, 'runQuery') || !method_exists($db, 'fetchAll')) {
            return false;
        }

        $db->runQuery("CREATE TABLE IF NOT EXISTS formulas (
            id VARCHAR(255) PRIMARY KEY,
            parent_formula_id VARCHAR(255),
            derivation_type VARCHAR(50),
            lineage_confidence VARCHAR(32) DEFAULT NULL,
            category VARCHAR(64) DEFAULT NULL,
            record_type VARCHAR(32) DEFAULT 'equation',
            equation_family VARCHAR(128) DEFAULT NULL,
            constraints JSON,
            related_formula_ids JSON,
            subcomponents JSON,
            derivation_steps JSON,
            cas_validation JSON,
            title VARCHAR(255) NOT NULL,
            equation MEDIUMTEXT NOT NULL,
            equation_svg MEDIUMTEXT,
            description TEXT,
            conceptual_definition TEXT,
            intuitive_summary TEXT,
            interpretation TEXT,
            symmetry_origin TEXT,
            limits_and_boundary TEXT,
            semantic_variables JSON,
            unit_system VARCHAR(50) DEFAULT 'SI',
            status VARCHAR(50) DEFAULT 'platinum',
            INDEX idx_formulas_category (category),
            INDEX idx_formulas_lineage_conf (lineage_confidence),
            FULLTEXT INDEX ft_formulas (title, conceptual_definition, equation)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $existingCols = [];
        $colRows = $db->fetchAll(
            "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'formulas'"
        ) ?: [];
        foreach ($colRows as $r) {
            $arr = is_object($r) ? (method_exists($r, 'getData') ? $r->getData() : (array) $r) : (array) $r;
            $name = $arr['COLUMN_NAME'] ?? $arr['column_name'] ?? null;
            if ($name) {
                $existingCols[$name] = true;
            }
        }

        $requiredColumns = [
            'parent_formula_id'  => "ADD COLUMN parent_formula_id VARCHAR(255) AFTER id",
            'derivation_type'    => "ADD COLUMN derivation_type VARCHAR(50) AFTER parent_formula_id",
            'lineage_confidence' => "ADD COLUMN lineage_confidence VARCHAR(32) DEFAULT NULL AFTER derivation_type",
            'category'           => "ADD COLUMN category VARCHAR(64) DEFAULT NULL AFTER lineage_confidence",
            'record_type'        => "ADD COLUMN record_type VARCHAR(32) DEFAULT 'equation' AFTER category",
            'equation_family'    => "ADD COLUMN equation_family VARCHAR(128) DEFAULT NULL AFTER record_type",
            'constraints'        => "ADD COLUMN constraints JSON",
            'related_formula_ids'=> "ADD COLUMN related_formula_ids JSON",
            'subcomponents'      => "ADD COLUMN subcomponents JSON",
            'derivation_steps'   => "ADD COLUMN derivation_steps JSON",
            'cas_validation'     => "ADD COLUMN cas_validation JSON",
            'equation_svg'       => "ADD COLUMN equation_svg MEDIUMTEXT AFTER equation",
            'description'        => "ADD COLUMN description TEXT AFTER equation_svg",
        ];

        $columnsAdded = false;
        foreach ($requiredColumns as $col => $ddlClause) {
            if (!isset($existingCols[$col])) {
                $db->runQuery("ALTER TABLE formulas {$ddlClause};");
                $existingCols[$col] = true;
                $columnsAdded = true;
            }
        }

        $existingIdx = [];
        $idxRows = $db->fetchAll(
            "SELECT DISTINCT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'formulas'"
        ) ?: [];
        foreach ($idxRows as $r) {
            $arr = is_object($r) ? (method_exists($r, 'getData') ? $r->getData() : (array) $r) : (array) $r;
            $name = $arr['INDEX_NAME'] ?? $arr['index_name'] ?? null;
            if ($name) {
                $existingIdx[$name] = true;
            }
        }

        if (!isset($existingIdx['idx_formulas_category'])) {
            $db->runQuery("ALTER TABLE formulas ADD INDEX idx_formulas_category (category);");
        }
        if (!isset($existingIdx['idx_formulas_lineage_conf'])) {
            $db->runQuery("ALTER TABLE formulas ADD INDEX idx_formulas_lineage_conf (lineage_confidence);");
        }
        if (!isset($existingIdx['ft_formulas'])) {
            $db->runQuery("ALTER TABLE formulas ADD FULLTEXT INDEX ft_formulas (title, conceptual_definition, equation);");
        }

        return $columnsAdded;
    }

    /**
     * Fast, hash-based transactional upsert of modified JSON formula shards to MariaDB.
     */
    public function syncFormulasToDatabase(bool $force = false): array
    {
        $registryPath = PROJECT_ROOT . '/app/config/formulas_hash_registry.json';
        $hashRegistry = [];

        if (file_exists($registryPath)) {
            $rawRegistry = file_get_contents($registryPath);
            $hashRegistry = json_decode($rawRegistry, true) ?: [];
        }

        $shardFiles = glob(PROJECT_ROOT . '/app/config/content/formulas/*/shard_*.json') ?: [];
        sort($shardFiles);

        $shardsUpdated = 0;
        $shardsFailed = 0;
        $failedErrors = [];
        $formulasSynced = 0;
        $newRegistry = $hashRegistry;
        $db = $this->app->db();
        $hasLiveDb = $db && method_exists($db, 'runQuery') && method_exists($db, 'fetchAll');
        $dbShardHashes = null;

        if ($hasLiveDb) {
            // 1. Optional DDL schema verification (non-fatal for least-privilege DB users)
            try {
                if ($this->ensureFormulasSchema($db)) {
                    $force = true;
                }
            } catch (\Throwable $e) {
                error_log('[ShardSyncService] Schema introspection/DDL skipped (least-privilege DB user): ' . $e->getMessage());
            }

            // 2. Ensure shard_sync_state table exists if DDL is permitted (non-fatal if already migrated)
            try {
                $db->runQuery("CREATE TABLE IF NOT EXISTS shard_sync_state (
                    shard_path VARCHAR(255) PRIMARY KEY,
                    sha256 CHAR(64) NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");
            } catch (\Throwable $e) {
                error_log('[ShardSyncService] CREATE TABLE shard_sync_state skipped (assuming pre-migrated): ' . $e->getMessage());
            }

            // 3. Read DB-backed shard state independently of DDL permissions.
            // Never fall back to Git's formulas_hash_registry.json on a live DB (would tautologically skip all 256 shards).
            $dbShardHashes = [];
            try {
                $stateRows = $db->fetchAll("SELECT shard_path, sha256 FROM shard_sync_state") ?: [];
                foreach ($stateRows as $sr) {
                    $arr = is_object($sr) ? (method_exists($sr, 'getData') ? $sr->getData() : (array)$sr) : (array)$sr;
                    $sPath = $arr['shard_path'] ?? $arr['SHARD_PATH'] ?? null;
                    $sHash = $arr['sha256'] ?? $arr['SHA256'] ?? null;
                    if (is_string($sPath) && is_string($sHash)) {
                        $dbShardHashes[$sPath] = $sHash;
                    }
                }
            } catch (\Throwable $e) {
                error_log('[ShardSyncService] Failed reading shard_sync_state; forcing full shard reconciliation: ' . $e->getMessage());
                $dbShardHashes = [];
            }
        }

        $upsertFullSql = "
            INSERT INTO formulas (
                id, title, category, record_type, equation_family,
                equation, equation_svg, description, conceptual_definition, intuitive_summary,
                interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                parent_formula_id, derivation_type, lineage_confidence,
                subcomponents, derivation_steps, cas_validation,
                constraints, related_formula_ids, status, unit_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                category = VALUES(category),
                record_type = VALUES(record_type),
                equation_family = VALUES(equation_family),
                equation = VALUES(equation),
                equation_svg = VALUES(equation_svg),
                description = VALUES(description),
                conceptual_definition = VALUES(conceptual_definition),
                intuitive_summary = VALUES(intuitive_summary),
                interpretation = VALUES(interpretation),
                symmetry_origin = VALUES(symmetry_origin),
                limits_and_boundary = VALUES(limits_and_boundary),
                semantic_variables = VALUES(semantic_variables),
                parent_formula_id = VALUES(parent_formula_id),
                derivation_type = VALUES(derivation_type),
                lineage_confidence = VALUES(lineage_confidence),
                subcomponents = VALUES(subcomponents),
                derivation_steps = VALUES(derivation_steps),
                cas_validation = VALUES(cas_validation),
                constraints = VALUES(constraints),
                related_formula_ids = VALUES(related_formula_ids),
                status = VALUES(status),
                unit_system = VALUES(unit_system)
        ";

        $upsertFallbackSql = "
            INSERT INTO formulas (
                id, title, equation, conceptual_definition, intuitive_summary,
                interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                parent_formula_id, derivation_type, subcomponents,
                constraints, related_formula_ids, status, unit_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                equation = VALUES(equation),
                conceptual_definition = VALUES(conceptual_definition),
                intuitive_summary = VALUES(intuitive_summary),
                interpretation = VALUES(interpretation),
                symmetry_origin = VALUES(symmetry_origin),
                limits_and_boundary = VALUES(limits_and_boundary),
                semantic_variables = VALUES(semantic_variables),
                parent_formula_id = VALUES(parent_formula_id),
                derivation_type = VALUES(derivation_type),
                subcomponents = VALUES(subcomponents),
                constraints = VALUES(constraints),
                related_formula_ids = VALUES(related_formula_ids),
                status = VALUES(status),
                unit_system = VALUES(unit_system)
        ";

        $encodeJsonField = static function ($val): ?string {
            if (empty($val)) {
                return null;
            }
            return is_string($val) ? $val : json_encode($val, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        };

        foreach ($shardFiles as $filePath) {
            $relativePath = str_replace(PROJECT_ROOT . '/', '', $filePath);
            $fileContent = file_get_contents($filePath);
            $currentHash = hash('sha256', $fileContent);

            $baselineHashes = is_array($dbShardHashes) ? $dbShardHashes : $hashRegistry;
            if (!$force && isset($baselineHashes[$relativePath]) && $baselineHashes[$relativePath] === $currentHash) {
                $newRegistry[$relativePath] = $currentHash;
                continue;
            }

            $data = json_decode($fileContent, true);
            if (!is_array($data)) {
                continue;
            }

            $shardsUpdated++;
            $shardSuccess = true;
            $inTransaction = false;

            try {
                if ($db && method_exists($db, 'beginTransaction') && !$db->inTransaction()) {
                    $db->beginTransaction();
                    $inTransaction = true;
                }

                foreach ($data as $formulaId => $formula) {
                    if (!is_array($formula)) {
                        continue;
                    }

                    $eq = $formula['equation'] ?? '';
                    $cleanEq = $eq;
                    $eqSvg = $formula['equation_svg'] ?? null;
                    if (strpos($eq, '<svg') === 0) {
                        $eqSvg = $eq;
                        if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                            $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                        }
                    }

                    $semanticVars = $encodeJsonField($formula['semantic_variables'] ?? null);
                    $subcomponents = $encodeJsonField($formula['subcomponents'] ?? null);
                    $derivationSteps = $encodeJsonField($formula['derivation_steps'] ?? null);
                    $casValidation = $encodeJsonField($formula['cas_validation'] ?? null);
                    $constraints = $encodeJsonField($formula['constraints'] ?? null);
                    $relatedIds = $encodeJsonField($formula['related_formula_ids'] ?? null);

                    try {
                        $db->runQuery($upsertFullSql, [
                            $formulaId,
                            $formula['title'] ?? '',
                            $formula['category'] ?? null,
                            $formula['record_type'] ?? (str_contains($cleanEq, '=') ? 'equation' : 'symbol_or_term'),
                            $formula['equation_family'] ?? null,
                            $cleanEq,
                            $eqSvg,
                            $formula['description'] ?? '',
                            $formula['conceptual_definition'] ?? '',
                            $formula['intuitive_summary'] ?? '',
                            $formula['interpretation'] ?? '',
                            $formula['symmetry_origin'] ?? '',
                            $formula['limits_and_boundary'] ?? '',
                            $semanticVars,
                            $formula['parent_formula_id'] ?? null,
                            $formula['derivation_type'] ?? null,
                            $formula['lineage_confidence'] ?? null,
                            $subcomponents,
                            $derivationSteps,
                            $casValidation,
                            $constraints,
                            $relatedIds,
                            $formula['status'] ?? 'platinum',
                            $formula['unit_system'] ?? 'SI'
                        ]);
                        $formulasSynced++;
                    } catch (\Throwable $colErr) {
                        $db->runQuery($upsertFallbackSql, [
                            $formulaId,
                            $formula['title'] ?? '',
                            $cleanEq,
                            $formula['conceptual_definition'] ?? '',
                            $formula['intuitive_summary'] ?? '',
                            $formula['interpretation'] ?? '',
                            $formula['symmetry_origin'] ?? '',
                            $formula['limits_and_boundary'] ?? '',
                            $semanticVars,
                            $formula['parent_formula_id'] ?? null,
                            $formula['derivation_type'] ?? null,
                            $subcomponents,
                            $constraints,
                            $relatedIds,
                            $formula['status'] ?? 'platinum',
                            $formula['unit_system'] ?? 'SI'
                        ]);
                        $formulasSynced++;
                    }
                }

                if ($inTransaction) {
                    $db->commit();
                }
            } catch (\Throwable $shardErr) {
                $shardSuccess = false;
                $shardsFailed++;
                $failedErrors[] = "{$relativePath}: " . $shardErr->getMessage();
                if ($inTransaction && $db && method_exists($db, 'inTransaction') && $db->inTransaction()) {
                    $db->rollBack();
                }
                $this->physicsService->lastDbError = $shardErr->getMessage();
                error_log("[ShardSyncService] Shard sync failed for {$relativePath}: " . $shardErr->getMessage());
            }

            if ($shardSuccess) {
                $newRegistry[$relativePath] = $currentHash;
                if ($hasLiveDb && is_array($dbShardHashes)) {
                    try {
                        $db->runQuery(
                            "INSERT INTO shard_sync_state (shard_path, sha256) VALUES (?, ?)
                             ON DUPLICATE KEY UPDATE sha256 = VALUES(sha256), updated_at = CURRENT_TIMESTAMP",
                            [$relativePath, $currentHash]
                        );
                    } catch (\Throwable $stateErr) {
                        // Non-fatal
                    }
                }
            }
        }

        require_once __DIR__ . '/AuthService.php';
        $isProduction = AuthService::resolveAppEnv() === 'production';
        if ((!$isProduction && ($shardsUpdated > 0 || $newRegistry !== $hashRegistry)) || !file_exists($registryPath)) {
            @file_put_contents($registryPath, json_encode($newRegistry, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES), LOCK_EX);
        }

        if ($db && ($shardsUpdated > 0 || $force)) {
            try {
                $diskFormulaIds = [];
                foreach ($shardFiles as $filePath) {
                    $shardData = json_decode(file_get_contents($filePath), true);
                    if (is_array($shardData)) {
                        foreach (array_keys($shardData) as $fId) {
                            $diskFormulaIds[$fId] = true;
                        }
                    }
                }
                $dbRows = $db->fetchAll("SELECT id FROM formulas");
                $orphanedFormulas = [];
                foreach ($dbRows as $row) {
                    $rowId = is_object($row) ? $row->id : ($row['id'] ?? null);
                    if ($rowId && !isset($diskFormulaIds[$rowId])) {
                        $orphanedFormulas[] = $rowId;
                    }
                }
                if (!empty($orphanedFormulas)) {
                    $placeholders = implode(',', array_fill(0, count($orphanedFormulas), '?'));
                    $db->runQuery(
                        "DELETE FROM formulas WHERE id IN ($placeholders)",
                        array_values($orphanedFormulas)
                    );
                }
            } catch (\Throwable $pruneErr) {
                // Non-fatal during partial sync
            }
        }

        return [
            'shards_checked' => count($shardFiles),
            'shards_changed' => $shardsUpdated,
            'shards_failed' => $shardsFailed,
            'errors' => $failedErrors,
            'formulas_synced' => $formulasSynced
        ];
    }

    /**
     * Synchronizes a single subtopic to MariaDB.
     */
    public function syncIndividualSubtopic(string $slug, array $data): void
    {
        if (empty($data['title']) || empty($data['content'])) {
            return;
        }

        $primaryParent = !empty($data['parents']) ? $data['parents'][0] : '';

        $this->app->db()->runQuery(
            "INSERT INTO subtopics (slug, parent_topic, title, content, snippet, snippet_svg, hero_math, equations, breakdowns, formula_data, parents, standard, verification) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
                parent_topic = VALUES(parent_topic), 
                title = VALUES(title), 
                content = VALUES(content), 
                snippet = VALUES(snippet),
                snippet_svg = VALUES(snippet_svg),
                hero_math = VALUES(hero_math),
                equations = VALUES(equations),
                breakdowns = VALUES(breakdowns),
                formula_data = VALUES(formula_data), 
                parents = VALUES(parents), 
                standard = VALUES(standard),
                verification = VALUES(verification)",
            [
                $slug,
                $primaryParent,
                $data['title'],
                $data['content'],
                $data['snippet'] ?? '',
                $data['snippet_svg'] ?? '',
                $data['hero_math'] ?? '',
                json_encode($data['equations'] ?? []),
                json_encode($data['breakdowns'] ?? []),
                json_encode($data['formula_ids'] ?? []),
                json_encode($data['parents'] ?? []),
                $data['standard'] ?? 'legacy',
                !empty($data['verification']) ? json_encode($data['verification']) : null
            ]
        );
    }

    /**
     * Synchronizes a single topic hub manifest or flat topic shard to MariaDB.
     */
    public function syncIndividualTopic(string $slug, array $data): void
    {
        $meta = is_array($data['metadata'] ?? null) ? $data['metadata'] : [];
        $pillars = !empty($data['pillars']) ? (is_string($data['pillars']) ? $data['pillars'] : json_encode($data['pillars'])) : '[]';
        $bridgesRaw = $meta['bridges'] ?? ($data['bridges'] ?? []);
        $bridges = !empty($bridgesRaw) ? (is_string($bridgesRaw) ? $bridgesRaw : json_encode($bridgesRaw)) : '[]';
        $intro = (string)($meta['intro'] ?? ($data['intro'] ?? ''));
        $field = (string)($meta['field'] ?? ($data['field'] ?? ''));
        $density = (string)($meta['density'] ?? ($data['density'] ?? ''));
        $description = (string)($data['description'] ?? $intro);
        $content = (string)($data['content'] ?? '');
        $formulaData = !empty($data['formula_ids'])
            ? (is_string($data['formula_ids']) ? $data['formula_ids'] : json_encode($data['formula_ids']))
            : (!empty($data['formula_data']) ? (is_string($data['formula_data']) ? $data['formula_data'] : json_encode($data['formula_data'])) : '[]');

        $this->app->db()->runQuery(
            "INSERT INTO topics (slug, title, description, content, intro, field, density, pillars, bridges, formula_data) 
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
                title = VALUES(title), 
                description = IF(VALUES(description) != '', VALUES(description), description),
                content = IF(VALUES(content) != '', VALUES(content), content),
                intro = IF(VALUES(intro) != '', VALUES(intro), intro), 
                field = IF(VALUES(field) != '', VALUES(field), field), 
                density = IF(VALUES(density) != '', VALUES(density), density), 
                pillars = VALUES(pillars), 
                bridges = VALUES(bridges),
                formula_data = IF(VALUES(formula_data) != '[]', VALUES(formula_data), formula_data)",
            [
                $slug,
                $data['title'] ?? $slug,
                $description,
                $content,
                $intro,
                $field,
                $density,
                $pillars,
                $bridges,
                $formulaData
            ]
        );
    }

    /**
     * Synchronizes all subtopic shards, topic hubs, and formula shards into MariaDB.
     * Supports differential delta syncing based on file modification timestamps.
     */
    public function performSync(bool $force = false): void
    {
        $this->physicsService->loadAllShards();
        $data = $this->physicsService->getPhysicsContent();
        $db = $this->app->db();

        // 0. Apply any pending numbered schema migrations in scripts/migrations/
        $this->runMigrations();

        // 1. Auto-provision the database tables if they do not exist
        $db->runQuery("CREATE TABLE IF NOT EXISTS topics (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            slug VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            content MEDIUMTEXT,
            pillars JSON,
            intro TEXT,
            bridges JSON,
            field VARCHAR(255),
            density VARCHAR(50),
            equations JSON,
            breakdowns JSON,
            formula_data JSON,
            UNIQUE KEY uk_topics_id (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS subtopics (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            slug VARCHAR(255) PRIMARY KEY,
            parent_topic VARCHAR(255),
            title VARCHAR(255) NOT NULL,
            content MEDIUMTEXT NOT NULL,
            snippet TEXT,
            snippet_svg MEDIUMTEXT,
            hero_math TEXT,
            equations JSON,
            breakdowns JSON,
            formula_data JSON,
            parents JSON,
            standard VARCHAR(50) DEFAULT 'legacy',
            verification JSON,
            UNIQUE KEY uk_subtopics_id (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS simulations (
            id INT UNSIGNED NOT NULL AUTO_INCREMENT,
            slug VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            physics MEDIUMTEXT,
            category VARCHAR(128),
            category_name VARCHAR(128),
            engine VARCHAR(128),
            difficulty VARCHAR(64),
            equations JSON,
            UNIQUE KEY uk_simulations_id (id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $subtopicIdxRows = $db->fetchAll(
            "SELECT DISTINCT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'subtopics'"
        ) ?: [];
        $hasFtSubtopics = false;
        foreach ($subtopicIdxRows as $r) {
            $arr = is_object($r) ? (method_exists($r, 'getData') ? $r->getData() : (array) $r) : (array) $r;
            if (($arr['INDEX_NAME'] ?? $arr['index_name'] ?? '') === 'ft_subtopics') {
                $hasFtSubtopics = true;
                break;
            }
        }
        if (!$hasFtSubtopics) {
            $db->runQuery("ALTER TABLE subtopics ADD FULLTEXT INDEX ft_subtopics (title, content);");
        }

        if ($this->ensureFormulasSchema($db)) {
            $force = true;
        }

        // 2. Sync Topics
        foreach ($data['topics'] ?? [] as $slug => $t) {
            try {
                $db->runQuery(
                    "INSERT INTO topics (slug, title, description, content, pillars, intro, bridges, field, density, equations, breakdowns, formula_data) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON DUPLICATE KEY UPDATE 
                        title = VALUES(title), description = VALUES(description), content = VALUES(content), pillars = VALUES(pillars), intro = VALUES(intro), 
                        bridges = VALUES(bridges), field = VALUES(field), density = VALUES(density), equations = VALUES(equations), 
                        breakdowns = VALUES(breakdowns), formula_data = VALUES(formula_data)",
                    [
                        $slug,
                        $t['title'],
                        $t['description'] ?? ($t['intro'] ?? ''),
                        $t['content'] ?? '',
                        json_encode($t['pillars'] ?? []),
                        $t['intro'] ?? '',
                        json_encode($t['bridges'] ?? []),
                        $t['field'] ?? '',
                        $t['density'] ?? '',
                        json_encode($t['equations'] ?? []),
                        json_encode($t['breakdowns'] ?? []),
                        json_encode($t['formula_ids'] ?? [])
                    ]
                );
            } catch (\Throwable $legacyTopicErr) {
                $db->runQuery(
                    "INSERT INTO topics (slug, title, content, pillars, intro, bridges, field, density, equations, breakdowns, formula_data) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON DUPLICATE KEY UPDATE 
                        title = VALUES(title), content = VALUES(content), pillars = VALUES(pillars), intro = VALUES(intro), 
                        bridges = VALUES(bridges), field = VALUES(field), density = VALUES(density), equations = VALUES(equations), 
                        breakdowns = VALUES(breakdowns), formula_data = VALUES(formula_data)",
                    [
                        $slug,
                        $t['title'],
                        $t['content'] ?? '',
                        json_encode($t['pillars'] ?? []),
                        $t['intro'] ?? '',
                        json_encode($t['bridges'] ?? []),
                        $t['field'] ?? '',
                        $t['density'] ?? '',
                        json_encode($t['equations'] ?? []),
                        json_encode($t['breakdowns'] ?? []),
                        json_encode($t['formula_ids'] ?? [])
                    ]
                );
            }
        }

        // 2b. Sync Simulations
        $simsMap = $data['simulations'] ?? [];
        $simsConfigPath = PROJECT_ROOT . '/app/config/simulations.json';
        if (file_exists($simsConfigPath)) {
            $simsConfig = json_decode((string)file_get_contents($simsConfigPath), true) ?: [];
            foreach ($simsConfig as $simSlug => $simCfg) {
                if (is_array($simCfg)) {
                    $simsMap[$simSlug] = array_merge($simsMap[$simSlug] ?? [], $simCfg);
                }
            }
        }
        foreach ($simsMap as $simSlug => $sim) {
            if (!is_array($sim) || empty($sim['title'])) {
                continue;
            }
            try {
                $db->runQuery(
                    "INSERT INTO simulations (slug, title, description, physics, category, category_name, engine, difficulty, equations)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                     ON DUPLICATE KEY UPDATE
                        title = VALUES(title), description = VALUES(description), physics = VALUES(physics),
                        category = VALUES(category), category_name = VALUES(category_name),
                        engine = VALUES(engine), difficulty = VALUES(difficulty), equations = VALUES(equations)",
                    [
                        (string)$simSlug,
                        $sim['title'],
                        $sim['description'] ?? '',
                        $sim['physics'] ?? ($sim['description'] ?? ''),
                        $sim['category'] ?? '',
                        $sim['category_name'] ?? '',
                        $sim['engine'] ?? '',
                        $sim['difficulty'] ?? '',
                        json_encode($sim['equations'] ?? []),
                    ]
                );
            } catch (\Throwable $simErr) {
                // Non-fatal on legacy custom simulations table schema
            }
        }

        // 3. Sync Subtopics
        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            $this->syncIndividualSubtopic($slug, $st);
        }

        // 4. Sync Formulas via unified SHA-256 hash-driven upsert & orphan pruning
        $formulaSync = $this->syncFormulasToDatabase($force);
        if (($formulaSync['shards_failed'] ?? 0) > 0) {
            $firstErr = $formulaSync['errors'][0] ?? 'Unknown shard DB error';
            throw new \RuntimeException(
                "Formula synchronization failed on {$formulaSync['shards_failed']} shard(s): {$firstErr}"
            );
        }

        // 4a. Compile formula LaTeX index only in non-production studio or when missing (preserves clean git status on server)
        require_once __DIR__ . '/AuthService.php';
        $isProduction = AuthService::resolveAppEnv() === 'production';
        $indexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
        if ((!$isProduction && (($formulaSync['shards_changed'] ?? 0) > 0 || $force)) || !file_exists($indexFile)) {
            $formulasDir = PROJECT_ROOT . '/app/config/content/formulas/';
            $formulaFiles = array_merge(glob($formulasDir . 'shard_*.json') ?: [], glob($formulasDir . '*/shard_*.json') ?: []);
            $latexIndex = file_exists($indexFile) ? (json_decode(file_get_contents($indexFile), true) ?: []) : [];
            foreach ($formulaFiles as $file) {
                $content = json_decode(file_get_contents($file), true) ?: [];
                foreach ($content as $fId => $fData) {
                    $eq = $fData['equation'] ?? '';
                    $cleanEq = $eq;
                    if (strpos($eq, '<svg') === 0) {
                        if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                            $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                        }
                    }
                    $normalized = $this->physicsService->normalizeLatex($cleanEq);
                    if (!empty($normalized)) {
                        $latexIndex[$normalized] = $fId;
                    }
                }
            }
            file_put_contents(
                $indexFile,
                json_encode($latexIndex, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
                LOCK_EX
            );
        }

        // 5. Automatically prune database subtopics
        $this->pruneOrphans(false);
    }

    /**
     * Identifies and optionally prunes database subtopics that no longer exist on disk.
     * Supports dry-run auditing.
     */
    public function pruneOrphans(bool $dryRun = true): array
    {
        $this->physicsService->loadAllShards();
        $content = $this->physicsService->getPhysicsContent();
        $diskSlugs = array_keys($content['subtopics']);

        try {
            $dbRows = $this->app->db()->fetchAll("SELECT slug FROM subtopics") ?: [];
        } catch (\Throwable $e) {
            // Table does not exist yet on a brand-new database prior to initial performSync()
            return [];
        }

        $dbSlugs = [];
        foreach ($dbRows as $row) {
            $s = is_object($row) ? ($row->slug ?? null) : ($row['slug'] ?? null);
            if (is_string($s) && $s !== '') {
                $dbSlugs[] = $s;
            }
        }

        $orphans = array_diff($dbSlugs, $diskSlugs);

        if (empty($orphans)) {
            return [];
        }

        if (!$dryRun) {
            $placeholders = implode(',', array_fill(0, count($orphans), '?'));
            $this->app->db()->runQuery(
                "DELETE FROM subtopics WHERE slug IN ($placeholders)",
                array_values($orphans)
            );
        }

        return array_values($orphans);
    }

    /**
     * Executes pending numbered database migrations (scripts/migrations/NNN_*.{php,sql})
     * in lexical order and records applied filenames + SHA-256 checksums in `schema_migrations`.
     */
    public function runMigrations(?string $migrationsDir = null): array
    {
        $db = $this->app->db();
        if (!$db || !method_exists($db, 'runQuery') || !method_exists($db, 'fetchAll')) {
            return ['checked' => 0, 'applied' => [], 'skipped' => []];
        }

        $dir = $migrationsDir ?? (PROJECT_ROOT . '/scripts/migrations');
        if (!is_dir($dir)) {
            return ['checked' => 0, 'applied' => [], 'skipped' => []];
        }

        $db->runQuery("CREATE TABLE IF NOT EXISTS schema_migrations (
            migration VARCHAR(255) PRIMARY KEY,
            checksum CHAR(64) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $appliedMap = [];
        $rows = $db->fetchAll("SELECT migration FROM schema_migrations") ?: [];
        foreach ($rows as $r) {
            $arr = is_object($r) ? (method_exists($r, 'getData') ? $r->getData() : (array)$r) : (array)$r;
            $name = $arr['migration'] ?? $arr['MIGRATION'] ?? null;
            if (is_string($name) && $name !== '') {
                $appliedMap[$name] = true;
            }
        }

        $entries = scandir($dir) ?: [];
        $files = [];
        foreach ($entries as $entry) {
            if (preg_match('/^\d+_[a-zA-Z0-9_-]+\.(php|sql)$/', $entry) && is_file($dir . '/' . $entry)) {
                $files[] = $entry;
            }
        }
        sort($files, SORT_STRING);

        $execSql = static function (string $sql, array $params = []) use ($db): void {
            $db->runQuery($sql, $params);
        };

        $applied = [];
        $skipped = [];

        foreach ($files as $filename) {
            if (isset($appliedMap[$filename])) {
                $skipped[] = $filename;
                continue;
            }

            $fullPath = $dir . '/' . $filename;
            $checksum = hash_file('sha256', $fullPath) ?: '';
            $ext = strtolower(pathinfo($filename, PATHINFO_EXTENSION));

            if ($ext === 'sql') {
                $rawSql = (string)file_get_contents($fullPath);
                $statements = preg_split('/;\s*(?:\r?\n|$)/', $rawSql) ?: [];
                foreach ($statements as $stmt) {
                    $trimmed = trim($stmt);
                    if ($trimmed !== '' && !str_starts_with($trimmed, '--')) {
                        $execSql($trimmed);
                    }
                }
            } else {
                $runner = static function (string $__migPath, callable $migrationExecSql) use ($db): void {
                    ob_start();
                    try {
                        $ret = include $__migPath;
                        if (is_callable($ret)) {
                            $ret($db, $migrationExecSql);
                        }
                    } finally {
                        ob_end_clean();
                    }
                };
                $runner($fullPath, $execSql);
            }

            $db->runQuery(
                "INSERT INTO schema_migrations (migration, checksum) VALUES (?, ?)
                 ON DUPLICATE KEY UPDATE checksum = VALUES(checksum)",
                [$filename, $checksum]
            );
            $applied[] = $filename;
        }

        return [
            'checked' => count($files),
            'applied' => $applied,
            'skipped' => $skipped,
        ];
    }
}
