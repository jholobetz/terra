<?php
/**
 * Global TeX AST Repair Engine for Terra Physics Formulas
 * Scans, repairs, validates, and re-syncs TeX math blocks across all 13,731 formulas in shards and MariaDB.
 */

define("FLIGHT_SKIP_START", true);
require_once __DIR__ . "/../app/config/bootstrap.php";

class GlobalTexRepairEngine {
    private $db;
    private $shardsDir;
    private $repairedCount = 0;
    private $scannedCount = 0;
    private $repairedFormulas = [];

    public function __construct($app) {
        $this->db = $app->db();
        $this->shardsDir = PROJECT_ROOT . "/app/config/content/formulas";
    }

    /**
     * Core TeX sanitization and repair logic for any text field.
     */
    public function repairTextField(string $text): string {
        if (empty($text)) return $text;

        $original = $text;

        // 1. Specific known broken macro pattern replacements
        $replacements = [
            '/\\\\sqrt\\$\\{([^\\}]+)\\}/' => '\\sqrt{$1}',
            '/\\$\\s*\\\\mu\\$\\s*u\\$?/' => '\\mu \\nu',
            '/\\$\\s*\\\\mu\\$\\s*\\\\nu/' => '\\mu \\nu',
            '/g_\\{\\$\\s*\\\\mu\\$\\s*u\\}/' => 'g_{\\mu \\nu}',
            '/G_\\{\\$\\s*\\\\mu\\$\\s*u\\}/' => 'G_{\\mu \\nu}',
            '/T_\\{\\$\\s*\\\\mu\\$\\s*u\\}/' => 'T_{\\mu \\nu}',
            '/\\\\to\x27/' => '\\to',
            '/\x27\\+?\\$\\s*([^\x27\\$]+)\\s*\\$\x27/' => '$$1$',
            '/denoted as\\$-g\\$\\(/i' => 'denoted as $-g$ (',
            '/\\$\\\\sqrt\\$\\{/' => '$\\sqrt{',
            '/\\$\\\\\*\\$/' => '',
            '/\\$([a-zA-Z0-9_\\\\]+)\\$\\^\\*/' => '$$1^*$',
            '/\\$([a-zA-Z0-9_\\\\]+)\\$\\^\\*\\$([a-zA-Z0-9_\\\\]+)\\$/' => '$$1^* $2$',
            '/\\|\\$([a-zA-Z0-9_\\\\]+)\\$\\|\\^2/' => '$|$1|^2$',
            '/\\(\\s*\\|\\$([a-zA-Z0-9_\\\\]+)\\$\\|\\^2\\s*\\)/' => '($|$1|^2$)',
        ];

        foreach ($replacements as $pattern => $replacement) {
            $res = preg_replace($pattern, $replacement, $text);
            if ($res !== null) {
                $text = $res;
            }
        }

        // 2. Fix nested dollar signs inside macro blocks: e.g. $\left[ ... $\frac{dy}{dx}$ ... \right]$
        // Pattern: $...$...$ where inner $ is inside brackets or macros
        $text = preg_replace_callback('/\\$([^\\$]+)\\$/', function($m) {
            $content = $m[1];
            // If inside $content we have nested $...$, remove inner $
            if (strpos($content, '$') !== false) {
                // e.g. \frac{d}{dx} \left[ p(x) $\frac{dy}{dx}$ \right]
                $cleanedContent = preg_replace('/\\$([^\\$]+)\\$/', '$1', $content);
                return '$' . $cleanedContent . '$';
            }
            return $m[0];
        }, $text);

        // 3. Fix unclosed dollar signs (odd dollar count)
        $dollarCount = substr_count($text, "$");
        if ($dollarCount % 2 !== 0) {
            // Find single $ followed by a TeX macro (\mathbf{...}, \nabla, \alpha, \varepsilon_0, etc.) missing closing $
            // Case A: $\macro at end of sentence or before punctuation/space
            $text = preg_replace_callback('/\\$(\\\\[a-zA-Z0-9_\\{\\}\\^\\+\\-\\.\\\\\\s]+?)(?=[\\s,\\.\\)]|$)/', function($m) {
                $token = $m[1];
                // Check if $token doesn't end with $
                if (substr($token, -1) !== '$') {
                    return '$' . rtrim($token) . '$';
                }
                return $m[0];
            }, $text);

            // Recount after Case A
            $dollarCount = substr_count($text, "$");
            if ($dollarCount % 2 !== 0) {
                // Case B: If still odd, find unclosed $ matching a single symbol or macro (e.g. $p, $\mathbf{v}, $\mathbf{E})
                // Find all $ positions
                $tokens = explode('$', $text);
                $newText = '';
                $inMath = false;
                for ($i = 0; $i < count($tokens); $i++) {
                    $piece = $tokens[$i];
                    if ($i === 0) {
                        $newText .= $piece;
                        continue;
                    }

                    if (!$inMath) {
                        // We are starting a math block
                        $newText .= '$' . $piece;
                        $inMath = true;
                    } else {
                        // We are inside a math block. Does this piece look like it should close math or is it unclosed?
                        // If piece starts with space or normal text, the previous dollar was unclosed!
                        if (preg_match('/^[a-zA-Z0-9\\s,\\.\\)]/', $piece) && !preg_match('/^\\\\[a-zA-Z]/', $piece)) {
                            // Close previous math block before $piece
                            // Actually, let's append $ to close previous block
                            $newText .= '$' . $piece;
                            $inMath = false;
                        } else {
                            $newText .= '$' . $piece;
                            $inMath = false;
                        }
                    }
                }
                
                if ($inMath) {
                    $newText .= '$';
                }

                $text = $newText;
            }
        }

        // 4. Cleanup any double dollar signs $$ that are not intentional display math
        $text = preg_replace('/(?<!\\\\)\\$\\$/', '$', $text);

        return $text;
    }

    /**
     * Clean semantic variables dictionary keys and descriptions.
     */
    public function repairSemanticVariables($vars) {
        if (!is_array($vars)) return $vars;
        $repaired = [];
        foreach ($vars as $key => $data) {
            $cleanKey = preg_replace('/\\\\mathbf\\s+\\{/', '\\mathbf{', (string)$key);
            $cleanKey = trim($cleanKey);

            if (is_array($data)) {
                if (!empty($data["description"]) && is_string($data["description"])) {
                    $data["description"] = $this->repairTextField($data["description"]);
                }
                if (!empty($data["name"]) && is_string($data["name"])) {
                    $data["name"] = $this->repairTextField($data["name"]);
                }
                $repaired[$cleanKey] = $data;
            } else if (is_string($data)) {
                $repaired[$cleanKey] = $this->repairTextField($data);
            } else {
                $repaired[$cleanKey] = $data;
            }
        }
        return $repaired;
    }

    /**
     * Process all shard files and MariaDB records.
     */
    public function run(bool $dryRun = false) {
        echo "Starting Global TeX Repair Engine (DryRun: " . ($dryRun ? "YES" : "NO") . ")...\n";

        $shardFiles = glob($this->shardsDir . "/**/*.json");
        $rootShardFiles = glob($this->shardsDir . "/*.json");
        $allShardFiles = array_merge($shardFiles, $rootShardFiles);

        echo "Found " . count($allShardFiles) . " shard files.\n";

        $dbStmt = $this->db->prepare("UPDATE formulas SET 
            conceptual_definition = :cdef,
            interpretation = :interp,
            limits_and_boundary = :lim,
            symmetry_origin = :sym,
            intuitive_summary = :intuitive,
            semantic_variables = :sv
            WHERE id = :id");

        foreach ($allShardFiles as $filePath) {
            $content = file_get_contents($filePath);
            $data = json_decode($content, true);

            if (!is_array($data)) continue;

            $shardChanged = false;

            foreach ($data as $id => $formula) {
                $this->scannedCount++;

                $origCdef = $formula["conceptual_definition"] ?? "";
                $origInterp = $formula["interpretation"] ?? "";
                $origLim = $formula["limits_and_boundary"] ?? "";
                $origSym = $formula["symmetry_origin"] ?? "";
                $origIntuitive = $formula["intuitive_summary"] ?? "";
                $origSV = $formula["semantic_variables"] ?? [];

                // ONLY process fields if they actually exist and are non-empty originally
                $newCdef = (!empty($origCdef)) ? $this->repairTextField($origCdef) : $origCdef;
                $newInterp = (!empty($origInterp)) ? $this->repairTextField($origInterp) : $origInterp;
                $newLim = (!empty($origLim)) ? $this->repairTextField($origLim) : $origLim;
                $newSym = (!empty($origSym)) ? $this->repairTextField($origSym) : $origSym;
                $newIntuitive = (!empty($origIntuitive)) ? $this->repairTextField($origIntuitive) : $origIntuitive;
                $newSV = (!empty($origSV) && is_array($origSV)) ? $this->repairSemanticVariables($origSV) : $origSV;

                if (($origCdef !== "" && $newCdef !== $origCdef) || 
                    ($origInterp !== "" && $newInterp !== $origInterp) || 
                    ($origLim !== "" && $newLim !== $origLim) || 
                    ($origSym !== "" && $newSym !== $origSym) || 
                    ($origIntuitive !== "" && $newIntuitive !== $origIntuitive) || 
                    (!empty($origSV) && $newSV !== $origSV)) {

                    $this->repairedCount++;
                    $this->repairedFormulas[$id] = $formula["title"] ?? $id;

                    if ($origCdef !== "") $data[$id]["conceptual_definition"] = $newCdef;
                    if ($origInterp !== "") $data[$id]["interpretation"] = $newInterp;
                    if ($origLim !== "") $data[$id]["limits_and_boundary"] = $newLim;
                    if ($origSym !== "") $data[$id]["symmetry_origin"] = $newSym;
                    if ($origIntuitive !== "") $data[$id]["intuitive_summary"] = $newIntuitive;
                    if (!empty($origSV)) $data[$id]["semantic_variables"] = $newSV;

                    $shardChanged = true;

                    if (!$dryRun) {
                        $updates = [];
                        $params = [":id" => $id];
                        if (!empty($newCdef)) { $updates[] = "conceptual_definition = :cdef"; $params[":cdef"] = $newCdef; }
                        if (!empty($newInterp)) { $updates[] = "interpretation = :interp"; $params[":interp"] = $newInterp; }
                        if (!empty($newLim)) { $updates[] = "limits_and_boundary = :lim"; $params[":lim"] = $newLim; }
                        if (!empty($newSym)) { $updates[] = "symmetry_origin = :sym"; $params[":sym"] = $newSym; }
                        if (!empty($newIntuitive)) { $updates[] = "intuitive_summary = :intuitive"; $params[":intuitive"] = $newIntuitive; }
                        if (!empty($newSV)) { $updates[] = "semantic_variables = :sv"; $params[":sv"] = json_encode($newSV, JSON_UNESCAPED_SLASHES); }

                        if (!empty($updates)) {
                            $sql = "UPDATE formulas SET " . implode(", ", $updates) . " WHERE id = :id";
                            $stmt = $this->db->prepare($sql);
                            $stmt->execute($params);
                        }
                    }
                }
            }

            if ($shardChanged && !$dryRun) {
                file_put_contents($filePath, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
            }
        }

        echo "Scan Complete!\n";
        echo "Total Formulas Scanned: {$this->scannedCount}\n";
        echo "Total Formulas Repaired: {$this->repairedCount}\n";
    }
}

$engine = new GlobalTexRepairEngine($app);

// Check CLI arguments for dry run vs execute
$dryRun = isset($argv[1]) && $argv[1] === "--dry-run";
$engine->run($dryRun);
