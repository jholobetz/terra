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
        $formulasSynced = 0;
        $newRegistry = $hashRegistry;
        $db = $this->app->db();

        if ($db) {
            try {
                $db->runQuery("ALTER TABLE formulas ADD COLUMN derivation_steps JSON AFTER subcomponents;");
                $force = true;
            } catch (\Throwable $e) {
                // Column already exists
            }
            try {
                $db->runQuery("ALTER TABLE formulas ADD COLUMN cas_validation JSON AFTER derivation_steps;");
                $force = true;
            } catch (\Throwable $e) {
                // Column already exists
            }
        }

        $upsertWithStepsSql = "
            INSERT INTO formulas (
                id, title, equation, conceptual_definition, intuitive_summary,
                interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                parent_formula_id, derivation_type, subcomponents, derivation_steps, cas_validation,
                constraints, related_formula_ids, status, unit_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

        foreach ($shardFiles as $filePath) {
            $relativePath = str_replace(PROJECT_ROOT . '/', '', $filePath);
            $fileContent = file_get_contents($filePath);
            $currentHash = hash('sha256', $fileContent);

            if (!$force && isset($hashRegistry[$relativePath]) && $hashRegistry[$relativePath] === $currentHash) {
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

                    $encodeJsonField = static function ($val): ?string {
                        if (empty($val)) {
                            return null;
                        }
                        return is_string($val) ? $val : json_encode($val, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
                    };

                    $semanticVars = $encodeJsonField($formula['semantic_variables'] ?? null);
                    $subcomponents = $encodeJsonField($formula['subcomponents'] ?? null);
                    $derivationSteps = $encodeJsonField($formula['derivation_steps'] ?? null);
                    $casValidation = $encodeJsonField($formula['cas_validation'] ?? null);
                    $constraints = $encodeJsonField($formula['constraints'] ?? null);
                    $relatedIds = $encodeJsonField($formula['related_formula_ids'] ?? null);

                    try {
                        $db->runQuery($upsertWithStepsSql, [
                            $formulaId,
                            $formula['title'] ?? '',
                            $formula['equation'] ?? '',
                            $formula['conceptual_definition'] ?? '',
                            $formula['intuitive_summary'] ?? '',
                            $formula['interpretation'] ?? '',
                            $formula['symmetry_origin'] ?? '',
                            $formula['limits_and_boundary'] ?? '',
                            $semanticVars,
                            $formula['parent_formula_id'] ?? null,
                            $formula['derivation_type'] ?? null,
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
                            $formula['equation'] ?? '',
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
                if ($inTransaction && $db && method_exists($db, 'inTransaction') && $db->inTransaction()) {
                    $db->rollBack();
                }
                $this->physicsService->lastDbError = $shardErr->getMessage();
            }

            if ($shardSuccess) {
                $newRegistry[$relativePath] = $currentHash;
            }
        }

        file_put_contents($registryPath, json_encode($newRegistry, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

        return [
            'shards_checked' => count($shardFiles),
            'shards_changed' => $shardsUpdated,
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
     * Synchronizes a single topic hub manifest to MariaDB.
     */
    public function syncIndividualTopic(string $slug, array $data): void
    {
        $pillars = !empty($data['pillars']) ? json_encode($data['pillars']) : '[]';
        $bridges = !empty($data['metadata']['bridges']) ? json_encode($data['metadata']['bridges']) : '[]';

        $this->app->db()->runQuery(
            "INSERT INTO topics (slug, title, intro, field, density, pillars, bridges) 
             VALUES (?, ?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE 
                title = VALUES(title), 
                intro = VALUES(intro), 
                field = VALUES(field), 
                density = VALUES(density), 
                pillars = VALUES(pillars), 
                bridges = VALUES(bridges)",
            [
                $slug,
                $data['title'],
                $data['metadata']['intro'] ?? '',
                $data['metadata']['field'] ?? '',
                $data['metadata']['density'] ?? '',
                $pillars,
                $bridges
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
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        $lastSyncTime = file_exists($syncLock) ? filemtime($syncLock) : 0;

        // 1. Auto-provision the database tables if they do not exist
        $db->runQuery("CREATE TABLE IF NOT EXISTS topics (
            slug VARCHAR(255) PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content MEDIUMTEXT,
            pillars JSON,
            intro TEXT,
            bridges JSON,
            field VARCHAR(255),
            density VARCHAR(50),
            equations JSON,
            breakdowns JSON,
            formula_data JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS subtopics (
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
            verification JSON
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $db->runQuery("CREATE TABLE IF NOT EXISTS formulas (
            id VARCHAR(255) PRIMARY KEY,
            parent_formula_id VARCHAR(255),
            derivation_type VARCHAR(50),
            constraints JSON,
            related_formula_ids JSON,
            subcomponents JSON,
            derivation_steps JSON,
            cas_validation JSON,
            title VARCHAR(255) NOT NULL,
            equation MEDIUMTEXT NOT NULL,
            equation_svg MEDIUMTEXT,
            conceptual_definition TEXT,
            intuitive_summary TEXT,
            interpretation TEXT,
            symmetry_origin TEXT,
            limits_and_boundary TEXT,
            semantic_variables JSON,
            unit_system VARCHAR(50) DEFAULT 'SI',
            status VARCHAR(50) DEFAULT 'published'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;");

        $alterQueries = [
            "ALTER TABLE formulas ADD COLUMN equation_svg MEDIUMTEXT AFTER equation;",
            "ALTER TABLE formulas ADD COLUMN parent_formula_id VARCHAR(255) AFTER id;",
            "ALTER TABLE formulas ADD COLUMN derivation_type VARCHAR(50) AFTER parent_formula_id;",
            "ALTER TABLE formulas ADD COLUMN constraints JSON AFTER derivation_type;",
            "ALTER TABLE formulas ADD COLUMN related_formula_ids JSON AFTER constraints;",
            "ALTER TABLE formulas ADD COLUMN subcomponents JSON AFTER related_formula_ids;",
            "ALTER TABLE formulas ADD COLUMN derivation_steps JSON AFTER subcomponents;",
            "ALTER TABLE formulas ADD COLUMN cas_validation JSON AFTER derivation_steps;",
            "ALTER TABLE subtopics ADD FULLTEXT INDEX ft_subtopics (title, content);",
            "ALTER TABLE formulas ADD FULLTEXT INDEX ft_formulas (title, conceptual_definition, equation);"
        ];
        foreach ($alterQueries as $sql) {
            try {
                $db->runQuery($sql);
            } catch (\Exception $e) {
                // Column or index already exists, ignore
            }
        }

        // 2. Sync Topics
        foreach ($data['topics'] ?? [] as $slug => $t) {
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

        // 3. Sync Subtopics
        foreach ($data['subtopics'] ?? [] as $slug => $st) {
            $this->syncIndividualSubtopic($slug, $st);
        }

        // 4. Sync Formulas (Grouped Transactionally & Differentially)
        $formulasDir = PROJECT_ROOT . '/app/config/content/formulas/';
        $formulaFiles = array_merge(glob($formulasDir . 'shard_*.json') ?: [], glob($formulasDir . '*/shard_*.json') ?: []);

        $db->runQuery("START TRANSACTION");
        try {
            $diskFormulaIds = [];

            foreach ($formulaFiles as $file) {
                $isModified = $force || (filemtime($file) > $lastSyncTime);
                $content = json_decode(file_get_contents($file), true) ?: [];

                foreach ($content as $fId => $fData) {
                    $diskFormulaIds[] = $fId;

                    if ($isModified) {
                        $eq = $fData['equation'] ?? '';
                        $cleanEq = $eq;
                        $eqSvg = $fData['equation_svg'] ?? null;

                        if (strpos($eq, '<svg') === 0) {
                            $eqSvg = $eq;
                            if (preg_match('/data-tex="([^"]+)"/i', $eq, $matches)) {
                                $cleanEq = html_entity_decode($matches[1], ENT_QUOTES, 'UTF-8');
                            }
                        }

                        $db->runQuery(
                            "INSERT INTO formulas (
                                id, parent_formula_id, derivation_type, constraints, related_formula_ids, subcomponents, derivation_steps, cas_validation,
                                title, equation, equation_svg, conceptual_definition, intuitive_summary, 
                                interpretation, symmetry_origin, limits_and_boundary, semantic_variables,
                                unit_system, status
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ON DUPLICATE KEY UPDATE 
                                parent_formula_id = VALUES(parent_formula_id),
                                derivation_type = VALUES(derivation_type),
                                constraints = VALUES(constraints),
                                related_formula_ids = VALUES(related_formula_ids),
                                subcomponents = VALUES(subcomponents),
                                derivation_steps = VALUES(derivation_steps),
                                cas_validation = VALUES(cas_validation),
                                title = VALUES(title),
                                equation = VALUES(equation),
                                equation_svg = VALUES(equation_svg),
                                conceptual_definition = VALUES(conceptual_definition),
                                intuitive_summary = VALUES(intuitive_summary),
                                interpretation = VALUES(interpretation),
                                symmetry_origin = VALUES(symmetry_origin),
                                limits_and_boundary = VALUES(limits_and_boundary),
                                semantic_variables = VALUES(semantic_variables),
                                unit_system = VALUES(unit_system),
                                status = VALUES(status)",
                            [
                                $fId,
                                $fData['parent_formula_id'] ?? null,
                                $fData['derivation_type'] ?? null,
                                !empty($fData['constraints']) ? json_encode($fData['constraints']) : null,
                                !empty($fData['related_formula_ids']) ? json_encode($fData['related_formula_ids']) : null,
                                !empty($fData['subcomponents']) ? json_encode($fData['subcomponents']) : null,
                                !empty($fData['derivation_steps']) ? json_encode($fData['derivation_steps']) : null,
                                !empty($fData['cas_validation']) ? json_encode($fData['cas_validation'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : null,
                                $fData['title'],
                                $cleanEq,
                                $eqSvg,
                                $fData['conceptual_definition'] ?? null,
                                $fData['intuitive_summary'] ?? null,
                                $fData['interpretation'] ?? null,
                                $fData['symmetry_origin'] ?? null,
                                $fData['limits_and_boundary'] ?? null,
                                isset($fData['semantic_variables']) ? json_encode($fData['semantic_variables']) : null,
                                $fData['unit_system'] ?? 'SI',
                                $fData['status'] ?? 'published'
                            ]
                        );
                    }
                }
            }

            // Prune orphaned database formulas
            $dbRows = $db->fetchAll("SELECT id FROM formulas");
            $dbFormulaIds = array_map(fn($row) => $row->id, $dbRows);
            $orphanedFormulas = array_diff($dbFormulaIds, $diskFormulaIds);
            if (!empty($orphanedFormulas)) {
                $placeholders = implode(',', array_fill(0, count($orphanedFormulas), '?'));
                $db->runQuery(
                    "DELETE FROM formulas WHERE id IN ($placeholders)",
                    array_values($orphanedFormulas)
                );
            }

            $db->runQuery("COMMIT");

            // 4a. Compile formula LaTeX index for fast lookup (preserving existing prose aliases)
            $indexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
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
                PROJECT_ROOT . '/app/config/formulas_latex_index.json',
                json_encode($latexIndex, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE)
            );
        } catch (\Exception $e) {
            $db->runQuery("ROLLBACK");
            throw $e;
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

        $dbRows = $this->app->db()->fetchAll("SELECT slug FROM subtopics");
        $dbSlugs = array_map(fn($row) => $row->slug, $dbRows);

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
}
