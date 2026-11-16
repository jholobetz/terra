<?php
define('FLIGHT_SKIP_START', true);

$args = array_slice($argv ?? [], 1);
if (in_array('--help', $args, true) || in_array('-h', $args, true)) {
    echo "Usage: php cli_sync.php [options]\n\n";
    echo "Options:\n";
    echo "  --warm-cache    Incrementally pre-render missing/stale Topic Hub and Subtopic HTML caches\n";
    echo "  --force-cache   Force full rebuild of all 12 Topic Hubs and 1,584 Subtopic HTML caches\n";
    echo "  --cache-only    Skip MariaDB synchronization and only warm HTML disk caches\n";
    echo "  -h, --help      Show this help message\n";
    exit(0);
}

$forceCache = in_array('--force-cache', $args, true);
$warmCache = $forceCache || in_array('--warm-cache', $args, true) || in_array('--cache-only', $args, true);
$cacheOnly = in_array('--cache-only', $args, true);

require __DIR__ . '/app/config/bootstrap.php';

try {
    $service = $app->physicsService();

    if (!$cacheOnly) {
        echo "Starting CLI Synchronization (Safe Mode)...\n";
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
        $service->performSync(true);

        $syncLock = __DIR__ . '/app/config/.last_sync';
        touch($syncLock);

        echo "✓ Synchronization and Clean-up Complete.\n";
    }

    if ($warmCache) {
        $modeLabel = $forceCache ? 'FORCE REBUILD' : 'INCREMENTAL';
        echo "\nWarming static HTML disk cache ({$modeLabel})...\n";
        $t0 = microtime(true);
        $ctrl = $app->physicsController();
        $stats = $ctrl->warmHtmlCache($forceCache, null, function (int $done, int $total) {
            if ($done % 100 === 0 || $done === $total) {
                $pct = $total > 0 ? number_format(($done / $total) * 100, 1) : '100.0';
                echo "\r  Progress: {$done} / {$total} ({$pct}%)";
                flush();
            }
        });
        $elapsed = number_format(microtime(true) - $t0, 2);
        echo "\n✓ HTML Cache Warm-up Complete in {$elapsed}s: "
            . "{$stats['hubs_built']} hubs built ({$stats['hubs_skipped']} fresh), "
            . "{$stats['subtopics_built']} subtopics built ({$stats['subtopics_skipped']} fresh).\n";

        if (!empty($stats['errors'])) {
            echo "⚠ Cache warm-up encountered " . count($stats['errors']) . " error(s):\n";
            foreach (array_slice($stats['errors'], 0, 10) as $err) {
                echo "  - {$err}\n";
            }
            exit(1);
        }
    }
} catch (\Throwable $e) {
    fwrite(STDERR, "Error: " . $e->getMessage() . "\n");
    exit(1);
}
