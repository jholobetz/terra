<?php

define('FLIGHT_SKIP_START', true);
require_once __DIR__ . '/../app/config/bootstrap.php';

$force = in_array('--force', $argv ?? [], true) || in_array('-f', $argv ?? [], true);

echo "========================================================\n";
echo "    TERRA FORMULA HASH-BASED MARIADB SYNC              \n";
echo "========================================================\n\n";

try {
    $service = $app->physicsService();
    $res = $service->syncFormulasToDatabase($force);

    echo "    Shards Checked: " . ($res['shards_checked'] ?? 0) . "\n";
    echo "    Shards Changed: " . ($res['shards_changed'] ?? 0) . "\n";
    echo "    Formulas Synced: " . ($res['formulas_synced'] ?? 0) . "\n";
    if (!empty($service->lastDbError)) {
        echo "    [WARN] Last DB Error: {$service->lastDbError}\n";
    }
} catch (\Throwable $e) {
    echo "    [ERROR] " . $e->getMessage() . " in " . $e->getFile() . ":" . $e->getLine() . "\n";
    exit(1);
}
echo "========================================================\n";


