<?php
/**
 * Targeted Sync Utility - Injects a single slug from JSON into MariaDB.
 * Usage: php sync_node.php <slug>
 */

define('FLIGHT_SKIP_START', true);
require __DIR__ . '/../../app/config/bootstrap.php';

if ($argc < 2) {
    echo "Usage: php sync_node.php <slug>\n";
    exit(1);
}

$slug = $argv[1];
$controller = $app->physicsController();

// Use Reflection to access the private sync method
$reflection = new ReflectionClass(get_class($controller));
$syncMethod = $reflection->getMethod('syncIndividualSubtopic');
$syncMethod->setAccessible(true);

// Access the internal data loader
$getContent = $reflection->getMethod('getPhysicsContent');
$getContent->setAccessible(true);
$content = $getContent->invoke($controller, $slug);

if (isset($content['subtopics'][$slug])) {
    $syncMethod->invoke($controller, $slug, $content['subtopics'][$slug]);
    echo "✓ MariaDB Injection Successful: [$slug]\n";
} else {
    echo "✗ Error: Slug [$slug] not found in content shards.\n";
    exit(1);
}
