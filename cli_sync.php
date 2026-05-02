<?php
define('FLIGHT_SKIP_START', true);
require __DIR__ . '/app/config/bootstrap.php';

echo "Starting CLI Synchronization (Safe Mode)...\n";

try {
    $controller = $app->physicsController();

    // Use Reflection to call private/protected methods
    $reflection = new ReflectionClass(get_class($controller));
    
    echo "Loading all shards...\n";
    $loadAllShards = $reflection->getMethod('loadAllShards');
    $loadAllShards->setAccessible(true);
    $loadAllShards->invoke($controller);

    echo "Performing database sync...\n";
    $performSync = $reflection->getMethod('performSync');
    $performSync->setAccessible(true);
    $performSync->invoke($controller);

    $syncLock = __DIR__ . '/app/config/.last_sync';
    touch($syncLock);
    
    echo "✓ Synchronization Complete.\n";
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
