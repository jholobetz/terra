<?php
define('FLIGHT_SKIP_START', true);
require __DIR__ . '/app/config/bootstrap.php';
$controller = $app->physicsController();
$slugs = ['coulombs-law', 'gausss-law', 'electric-potential'];

$reflection = new ReflectionClass(get_class($controller));

$syncMethod = $reflection->getMethod('syncIndividualSubtopic');
$syncMethod->setAccessible(true);

$loadShardMethod = $reflection->getMethod('loadShardForSlug');
$loadShardMethod->setAccessible(true);

$getContentMethod = $reflection->getMethod('getPhysicsContent');
$getContentMethod->setAccessible(true);

foreach($slugs as $slug) {
    echo "Syncing $slug...\n";
    $loadShardMethod->invoke($controller, $slug);
    $content = $getContentMethod->invoke($controller, $slug);
    if (isset($content['subtopics'][$slug])) {
        $syncMethod->invoke($controller, $slug, $content['subtopics'][$slug]);
        echo "✓ $slug synced.\n";
    } else {
        echo "✗ $slug not found in content shards.\n";
    }
}
