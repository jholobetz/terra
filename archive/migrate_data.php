<?php

/**
 * Migration script to move hardcoded physics data into the SQLite database.
 * Run this from the terminal: php migrate_data.php
 */

// Prevent Flight from starting the engine during migration
define('FLIGHT_SKIP_START', true);
require __DIR__ . '/app/config/bootstrap.php';
/** @var flight\Engine $app */

$db = $app->db();

// Auto-initialize the schema if the database is fresh
try {
    $db->runQuery("SELECT 1 FROM topics LIMIT 1");
} catch (\PDOException $e) {
    echo "Database tables not found in MariaDB. Initializing schema from database_init.sql...\n";
    $sqlPath = __DIR__ . '/database_init.sql';
    if (file_exists($sqlPath)) {
        $sql = file_get_contents($sqlPath);
        $db->runQuery($sql);
        echo "Schema initialized.\n";
    }
}

echo "Starting migration...\n";

$contentPath = __DIR__ . '/app/config/physics_content.json';
if (!file_exists($contentPath)) {
    die("Error: Content file not found at $contentPath\n");
}
$data = json_decode(file_get_contents($contentPath), true);

foreach ($data['simulations'] ?? [] as $slug => $item) {
    if (($item['status'] ?? '') === 'draft') {
        $db->runQuery("DELETE FROM simulations WHERE slug = ?", [$slug]);
        continue;
    }
    $db->runQuery("REPLACE INTO simulations (slug, title, description, physics, equations) VALUES (?, ?, ?, ?, ?)", [
        $slug, $item['title'], $item['description'], $item['physics'], json_encode($item['equations'])
    ]);
}
echo "Simulations migrated.\n";

foreach ($data['topics'] ?? [] as $slug => $item) {
    if (($item['status'] ?? '') === 'draft') {
        $db->runQuery("DELETE FROM topics WHERE slug = ?", [$slug]);
        continue;
    }
    $db->runQuery("REPLACE INTO topics (slug, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?)", [
        $slug, $item['title'], $item['content'], json_encode($item['equations']), json_encode($item['breakdowns'] ?? []), json_encode($item['formulas'] ?? [])
    ]);
}
echo "Topics migrated.\n";

foreach ($data['subtopics'] ?? [] as $slug => $item) {
    if (($item['status'] ?? '') === 'draft') {
        $db->runQuery("DELETE FROM subtopics WHERE slug = ?", [$slug]);
        continue;
    }
    $db->runQuery("REPLACE INTO subtopics (slug, parent_topic, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?, ?)", [
        $slug, $item['parent_topic'], $item['title'], $item['content'], json_encode($item['equations']), json_encode($item['breakdowns'] ?? []), json_encode($item['formulas'] ?? [])
    ]);
}
echo "Subtopics migrated.\n";

echo "Migration complete!\n";