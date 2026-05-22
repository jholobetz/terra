<?php
define('FLIGHT_SKIP_START', true);
require __DIR__ . '/app/config/bootstrap.php';

echo "Starting CLI Synchronization (Safe Mode)...\n";

try {
    $service = $app->physicsService();
    $service->setPreviewMode(true);

    echo "Loading all shards...\n";
    $service->loadAllShards();

    // Check for database orphans first to report them
    $orphans = $service->pruneOrphans(true);
    if (!empty($orphans)) {
        echo "Found " . count($orphans) . " stale database records to be pruned:\n";
        foreach ($orphans as $slug) {
            echo "  - $slug\n";
        }
    } else {
        echo "No orphaned database records detected.\n";
    }

    echo "Performing database sync and pruning...\n";
    $service->performSync();

    $syncLock = __DIR__ . '/app/config/.last_sync';
    touch($syncLock);
    
    echo "✓ Synchronization and Clean-up Complete.\n";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

