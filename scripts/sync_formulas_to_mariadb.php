<?php

define('PROJECT_ROOT', dirname(__DIR__));
require_once PROJECT_ROOT . '/vendor/autoload.php';

$config = require PROJECT_ROOT . '/app/config/config.php';
$app = Flight::app();
require PROJECT_ROOT . '/app/config/services.php';
$db = $app->db();

$registryPath = PROJECT_ROOT . '/app/config/formulas_hash_registry.json';
$hashRegistry = [];

if (file_exists($registryPath)) {
    $rawRegistry = file_get_contents($registryPath);
    $hashRegistry = json_decode($rawRegistry, true) ?: [];
}

$shardFiles = glob(PROJECT_ROOT . '/app/config/content/formulas/*/*.json');
$shardFiles = array_merge($shardFiles, glob(PROJECT_ROOT . '/app/config/content/formulas/*.json'));

$shardsUpdated = 0;
$formulasSynced = 0;
$newRegistry = [];

echo "========================================================\n";
echo "    TERRA FORMULA HASH-BASED MARIADB SYNC              \n";
echo "========================================================\n\n";

foreach ($shardFiles as $filePath) {
    $relativePath = str_replace(PROJECT_ROOT . '/', '', $filePath);
    $fileContent = file_get_contents($filePath);
    $currentHash = hash('sha256', $fileContent);

    $newRegistry[$relativePath] = $currentHash;

    // Skip if hash matches registry
    if (isset($hashRegistry[$relativePath]) && $hashRegistry[$relativePath] === $currentHash) {
        continue;
    }

    // Shard was modified or is new -> sync to MariaDB
    $shardsUpdated++;
    $data = json_decode($fileContent, true);
    if (!is_array($data)) {
        continue;
    }

    foreach ($data as $formulaId => $formula) {
        if (!is_array($formula)) {
            continue;
        }

        try {
            $semVarsJson = isset($formula['semantic_variables']) ? json_encode($formula['semantic_variables'], JSON_UNESCAPED_UNICODE) : null;
            $db->runQuery(
                "UPDATE formulas SET title = ?, equation = ?, interpretation = ?, limits_and_boundary = ?, conceptual_definition = ?, intuitive_summary = ?, symmetry_origin = ?, semantic_variables = ?, equation_svg = NULL WHERE id = ?",
                [
                    $formula['title'] ?? '',
                    $formula['equation'] ?? '',
                    $formula['interpretation'] ?? '',
                    $formula['limits_and_boundary'] ?? '',
                    $formula['conceptual_definition'] ?? '',
                    $formula['intuitive_summary'] ?? '',
                    $formula['symmetry_origin'] ?? '',
                    $semVarsJson,
                    $formulaId
                ]
            );
            $formulasSynced++;
        } catch (\Throwable $e) {
            // Ignore missing rows
        }
    }
}

// Save updated hash registry
file_put_contents($registryPath, json_encode($newRegistry, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

echo "    Shards Checked: " . count($shardFiles) . "\n";
echo "    Shards Changed: {$shardsUpdated}\n";
echo "    Formulas Synced: {$formulasSynced}\n";
echo "========================================================\n";
