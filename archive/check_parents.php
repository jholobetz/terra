<?php
$data = json_decode(file_get_contents('app/config/physics_content.json'), true);
$missing = [];
foreach ($data['subtopics'] as $slug => $st) {
    if (isset($st['parent_topic']) && empty($st['parent_topic'])) {
        $missing[] = $slug;
    }
}
// Also check for the literal string 'breakdowns' being a subtopic
if (isset($data['subtopics']['breakdowns'])) {
    echo "Found 'breakdowns' as a subtopic slug!\n";
}
if (empty($missing)) {
    echo "No missing parent_topics found.\n";
} else {
    echo "Missing parent_topic in slugs: " . implode(', ', $missing) . "\n";
}
