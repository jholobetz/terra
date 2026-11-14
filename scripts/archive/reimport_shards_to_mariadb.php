<?php
define("FLIGHT_SKIP_START", true);
require_once __DIR__ . "/../app/config/bootstrap.php";

$db = $app->db();
$shardsDir = PROJECT_ROOT . "/app/config/content/formulas";

$shardFiles = glob($shardsDir . "/**/*.json");
$rootShardFiles = glob($shardsDir . "/*.json");
$allFiles = array_merge($shardFiles, $rootShardFiles);

echo "Re-importing " . count($allFiles) . " shard files to MariaDB...\n";

$stmt = $db->prepare("UPDATE formulas SET 
    conceptual_definition = :cdef,
    interpretation = :interp,
    limits_and_boundary = :lim,
    symmetry_origin = :sym,
    intuitive_summary = :intuitive,
    semantic_variables = :sv
    WHERE id = :id");

$count = 0;

foreach ($allFiles as $filePath) {
    $content = file_get_contents($filePath);
    $data = json_decode($content, true);
    if (!is_array($data)) continue;

    foreach ($data as $id => $formula) {
        if (!is_array($formula)) continue;

        $cdef = $formula["conceptual_definition"] ?? "";
        $interp = $formula["interpretation"] ?? "";
        $lim = $formula["limits_and_boundary"] ?? "";
        $sym = $formula["symmetry_origin"] ?? "";
        $intuitive = $formula["intuitive_summary"] ?? "";
        
        $svRaw = $formula["semantic_variables"] ?? new stdClass();
        $sv = is_string($svRaw) ? $svRaw : json_encode($svRaw, JSON_UNESCAPED_SLASHES);
        if (empty($sv) || $sv === '""') {
            $sv = '{}';
        }

        $stmt->execute([
            ":cdef" => $cdef,
            ":interp" => $interp,
            ":lim" => $lim,
            ":sym" => $sym,
            ":intuitive" => $intuitive,
            ":sv" => $sv,
            ":id" => $id
        ]);
        $count++;
    }
}

echo "Successfully re-imported $count formula records into MariaDB!\n";
