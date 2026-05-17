<?php
/**
 * Hub Reordering Utility - Resets the database 'topics' table to match the order in categories.json.
 */

define('FLIGHT_SKIP_START', true);
require __DIR__ . '/../../app/config/bootstrap.php';

echo "Starting Hub Reordering...\n";

$controller = $app->physicsController();
$db = $app->db();

// 1. Truncate topics table (Safely reset IDs)
echo "Truncating 'topics' table...\n";
$db->runQuery("TRUNCATE TABLE topics");

// 2. Perform fresh sync in the order of categories.json
echo "Performing fresh sync...\n";

// Use Reflection to call performSync
$reflection = new ReflectionClass(get_class($controller));
$loadAllShards = $reflection->getMethod('loadAllShards');
$loadAllShards->setAccessible(true);
$loadAllShards->invoke($controller);

$performSync = $reflection->getMethod('performSync');
$performSync->setAccessible(true);
$performSync->invoke($controller);

echo "✓ Hubs successfully reordered in MariaDB.\n";
