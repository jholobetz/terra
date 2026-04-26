<?php
define('FLIGHT_SKIP_START', true);
require __DIR__ . '/vendor/autoload.php';
$config = require __DIR__ . '/app/config/config.php';

$dsn = 'mysql:host=' . $config['database']['host'] . ';dbname=' . $config['database']['dbname'] . ';charset=utf8mb4';
$user = $config['database']['user'];
$pass = $config['database']['password'];

try {
    $pdo = new PDO($dsn, $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_OBJ
    ]);
} catch (PDOException $e) {
    die("DB Connection failed: " . $e->getMessage());
}

echo "Starting Deduplication...\n";

// Map of slugs to REMOVE => slugs to KEEP
$merges = [
    'dark-energy' => 'dark-energy-theory',
    'hamiltons-canonical-equations' => 'hamiltons-equations',
    'boundary-condition-magnetism' => 'magnetic-boundary-conditions',
    'neutron-star' => 'neutron-stars',
    'non-local' => 'quantum-non-locality',
    'quine-criterion' => 'quinean-ontology',
    'square-integrable-functions' => 'square-integrable',
    'cosmic-microwave-background' => 'cmb-theory',
    'wave-equation-physics' => 'electromagnetic-wave-equation',
    'the-equation-of-motion' => 'newtons-second-law',
    'moment-of-inertia' => 'inertia-tensor',
    'invariant-interval' => 'spacetime-interval',
    'the-lagrangian' => 'lagrangian',
    'logic-basis-redirect' => 'logical-basis-ontology',
    'quantum-vacuum' => 'quantum-vacuum-ontology',
    'pauli-exclusion' => 'pauli-exclusion-principle',
    'principle-of-least-action' => 'action-principle',
    'proton-proton-chain' => 'pp-chain',
    'time-invariance' => 'time-translation-invariance',
    'wheeler-feynman-absorber' => 'wheeler-feynman-theory'
];

$deletedCount = 0;
$updatedRefs = 0;

foreach ($merges as $oldSlug => $newSlug) {
    // 1. Update any children that point to the old slug
    $stmt = $pdo->prepare("UPDATE subtopics SET parent_topic = ? WHERE parent_topic = ?");
    $stmt->execute([$newSlug, $oldSlug]);
    $updatedRefs += $stmt->rowCount();

    // 2. Delete the old slug
    $stmt = $pdo->prepare("DELETE FROM subtopics WHERE slug = ?");
    $stmt->execute([$oldSlug]);
    $deletedCount += $stmt->rowCount();
    
    echo "Merged [\033[1;33m$oldSlug\033[0m] into [\033[1;32m$newSlug\033[0m]\n";
}

// 3. Automated check for IDENTICAL content (MD5 match)
echo "Checking for identical content blocks...\n";
$stmt = $pdo->query("SELECT slug, content FROM subtopics");
$all = $stmt->fetchAll();
$hashes = [];
$autoDeleted = 0;

foreach ($all as $row) {
    $hash = md5($row->content);
    if (isset($hashes[$hash])) {
        $keepSlug = $hashes[$hash];
        $dropSlug = $row->slug;
        
        // Don't delete if we just merged it or if it's the same slug
        if ($keepSlug === $dropSlug) continue;
        
        // Update refs
        $up = $pdo->prepare("UPDATE subtopics SET parent_topic = ? WHERE parent_topic = ?");
        $up->execute([$keepSlug, $dropSlug]);
        
        // Delete
        $del = $pdo->prepare("DELETE FROM subtopics WHERE slug = ?");
        $del->execute([$dropSlug]);
        $autoDeleted += $del->rowCount();
        echo "Auto-merged identical content: [\033[1;33m$dropSlug\033[0m] -> [\033[1;32m$keepSlug\033[0m]\n";
    } else {
        $hashes[$hash] = $row->slug;
    }
}

echo "\nSummary:\n";
echo "- Explicitly merged: $deletedCount\n";
echo "- Identical content merged: $autoDeleted\n";
echo "- Parent references updated: $updatedRefs\n";
