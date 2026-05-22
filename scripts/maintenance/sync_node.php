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
$service = $app->physicsService();
$service->setPreviewMode(true);

$content = $service->getPhysicsContent($slug);

if (isset($content['subtopics'][$slug])) {
    $service->syncIndividualSubtopic($slug, $content['subtopics'][$slug]);
    echo "✓ MariaDB Injection Successful: Subtopic [$slug]\n";
} elseif (isset($content['topics'][$slug])) {
    $service->syncIndividualTopic($slug, $content['topics'][$slug]);
    echo "✓ MariaDB Injection Successful: Main Topic Hub [$slug]\n";
} else {
    echo "✗ Error: Slug [$slug] not found in content shards or topic manifests.\n";
    exit(1);
}
