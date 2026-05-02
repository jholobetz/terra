<?php
$data = json_decode(file_get_contents('app/config/physics_content.json'), true);
$pdo = new PDO('mysql:host=localhost;dbname=physicslab', 'doc', 'DIM^10$ymJ@zz');
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

echo "Starting diagnostic sync...\n";

foreach ($data['topics'] ?? [] as $slug => $t) {
    try {
        $stmt = $pdo->prepare("REPLACE INTO topics (slug, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?)");
        $stmt->execute([
            $slug, 
            $t['title'], 
            $t['content'], 
            json_encode($t['equations'] ?? []), 
            json_encode($t['breakdowns'] ?? []), 
            json_encode($t['formulas'] ?? [])
        ]);
        echo "Topic $slug OK\n";
    } catch (Exception $e) {
        echo "Topic $slug ERROR: " . $e->getMessage() . "\n";
    }
}

foreach ($data['subtopics'] ?? [] as $slug => $st) {
    try {
        $stmt = $pdo->prepare("REPLACE INTO subtopics (slug, parent_topic, title, content, equations, breakdowns, formula_data) VALUES (?, ?, ?, ?, ?, ?, ?)");
        $stmt->execute([
            $slug, 
            $st['parent_topic'] ?? '', 
            $st['title'], 
            $st['content'], 
            json_encode($st['equations'] ?? []), 
            json_encode($st['breakdowns'] ?? []), 
            json_encode($st['formulas'] ?? [])
        ]);
        echo "Subtopic $slug OK\n";
    } catch (Exception $e) {
        echo "Subtopic $slug ERROR: " . $e->getMessage() . "\n";
    }
}
