<?php
/**
 * Physics Data Validator
 * Performs integrity and linguistic checks on app/config/physics_content.json
 */

define('FLIGHT_SKIP_START', true);
require __DIR__ . '/vendor/autoload.php';

$jsonPath = __DIR__ . '/app/config/physics_content.json';

echo "\033[1;34m=== Physics Data Validator ===\033[0m\n";

// 1. Basic File Check
if (!file_exists($jsonPath)) {
    echo "\033[1;31m[ERROR]\033[0m JSON file not found at $jsonPath\n";
    exit(1);
}

// 2. JSON Validity
$content = file_get_contents($jsonPath);
$data = json_decode($content, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo "\033[1;31m[ERROR]\033[0m Invalid JSON structure: " . json_last_error_msg() . "\n";
    exit(1);
}
echo "✓ JSON structure is valid.\n";

$errors = [];
$warnings = [];

$topics = $data['topics'] ?? [];
$subtopics = $data['subtopics'] ?? [];
$allSlugs = array_unique(array_merge(array_keys($topics), array_keys($subtopics)));

// 3. Content Analysis
$doubledPatterns = ['\bthe the\b', '\bis is\b', '\bof of\b', '\bin in\b', '\bit it\b', '\bthat that\b', '\bas as\b', '4D 4D'];

foreach ($subtopics as $slug => $st) {
    $title = $st['title'] ?? '';
    $text = $st['content'] ?? '';
    $parent = $st['parent_topic'] ?? '';

    // Check doubled words
    foreach ($doubledPatterns as $pattern) {
        if (preg_match('/' . $pattern . '/i', $title) || preg_match('/' . $pattern . '/i', $text)) {
            $errors[] = "Subtopic [\033[1;33m$slug\033[0m]: Found repeated words matching pattern '$pattern'";
        }
    }

    // Check redundant 4D (suspicious prefixes)
    if (preg_match('/\b4D\s+(university|nature|history|logical|information|beginning|total|causal)\b/i', $text)) {
        $warnings[] = "Subtopic [\033[1;33m$slug\033[0m]: Potential redundant '4D' prefix found.";
    }

    // Check Orphaned Parents
    if (!empty($parent) && !in_array($parent, $allSlugs)) {
        $errors[] = "Subtopic [\033[1;33m$slug\033[0m]: Parent topic '\033[1;31m$parent\033[0m' does not exist.";
    }
}

// 4. Circular Dependency Check
function detect_cycle($slug, $subtopics, $path = []) {
    if (in_array($slug, $path)) return true;
    if (!isset($subtopics[$slug])) return false;
    $parent = $subtopics[$slug]['parent_topic'] ?? '';
    if (empty($parent) || !isset($subtopics[$parent])) return false;
    return detect_cycle($parent, $subtopics, array_merge($path, [$slug]));
}

foreach ($subtopics as $slug => $st) {
    if (detect_cycle($slug, $subtopics)) {
        $errors[] = "Subtopic [\033[1;33m$slug\033[0m]: Circular dependency detected in parent hierarchy.";
    }
}

// 5. Output Results
if (empty($errors) && empty($warnings)) {
    echo "\033[1;32m✓ All checks passed! Data is clean.\033[0m\n";
} else {
    if (!empty($errors)) {
        echo "\n\033[1;31mERRORS FOUND (" . count($errors) . "):\033[0m\n";
        foreach ($errors as $err) echo "  - $err\n";
    }
    if (!empty($warnings)) {
        echo "\n\033[1;35mWARNINGS (" . count($warnings) . "):\033[0m\n";
        foreach ($warnings as $warn) echo "  - $warn\n";
    }
    
    if (!empty($errors)) exit(1);
}
