<?php
/**
 * Targeted Sync Utility - Injects a single slug (topic or subtopic) from JSON into MariaDB.
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

// Use Reflection to access methods
$reflection = new ReflectionClass(get_class($controller));
$syncSubtopic = $reflection->getMethod('syncIndividualSubtopic');
$syncSubtopic->setAccessible(true);

$syncTopic = $reflection->getMethod('syncIndividualTopic');
$syncTopic->setAccessible(true);

// Access the internal data loader
$getContent = $reflection->getMethod('getPhysicsContent');
$getContent->setAccessible(true);
$content = $getContent->invoke($controller, $slug);

if (isset($content['subtopics'][$slug])) {
    $syncSubtopic->invoke($controller, $slug, $content['subtopics'][$slug]);
    echo "✓ MariaDB Injection Successful: Subtopic [$slug]\n";
} elseif (isset($content['topics'][$slug])) {
    $syncTopic->invoke($controller, $slug, $content['topics'][$slug]);
    echo "✓ MariaDB Injection Successful: Main Topic Hub [$slug]\n";
} else {
    echo "✗ Error: Slug [$slug] not found in content shards or topic manifests.\n";
    exit(1);
}
