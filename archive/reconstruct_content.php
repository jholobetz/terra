<?php
// Script to dump database to app/config/physics_content.json
require __DIR__ . '/vendor/autoload.php';
$config = require __DIR__ . '/app/config/bootstrap.php';
$config = require __DIR__ . '/app/config/config.php';

$dsn = 'mysql:host=' . $config['database']['host'] . ';dbname=' . $config['database']['dbname'] . ';charset=utf8mb4';
$user = $config['database']['user'];
$pass = $config['database']['password'];
$db = new PDO($dsn, $user, $pass, [PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);

$data = [
    'simulations' => [],
    'topics' => [],
    'subtopics' => [],
];

// 1. Simulations
$sims = $db->query("SELECT * FROM simulations")->fetchAll();
foreach ($sims as $s) {
    $data['simulations'][$s['slug']] = [
        'title' => $s['title'],
        'description' => $s['description'],
        'physics' => $s['physics'],
        'equations' => json_decode($s['equations'], true),
    ];
}

// 2. Topics
$topics = $db->query("SELECT * FROM topics")->fetchAll();
foreach ($topics as $t) {
    $data['topics'][$t['slug']] = [
        'title' => $t['title'],
        'content' => $t['content'],
        'equations' => json_decode($t['equations'], true),
        'breakdowns' => json_decode($t['breakdowns'], true),
        'formulas' => json_decode($t['formula_data'], true),
    ];
}

// 3. Subtopics
$subs = $db->query("SELECT * FROM subtopics")->fetchAll();
foreach ($subs as $s) {
    $data['subtopics'][$s['slug']] = [
        'title' => $s['title'],
        'parent_topic' => $s['parent_topic'],
        'content' => $s['content'],
        'equations' => json_decode($s['equations'], true),
        'breakdowns' => json_decode($s['breakdowns'], true),
        'formulas' => json_decode($s['formula_data'], true),
    ];
}

$json_content = json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);

file_put_contents(__DIR__ . '/app/config/physics_content.json', $json_content);
echo "Reconstruction to JSON complete.
";
