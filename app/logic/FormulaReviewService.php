<?php

namespace app\logic;

use Flight;
use PDO;

class FormulaReviewService
{
    protected ?PhysicsService $physicsService = null;

    public function __construct()
    {
        $this->physicsService = Flight::physicsService();
    }

    /**
     * Resolves the canonical JSON shard path for a given formula ID.
     */
    public function getShardPathForFormula(string $formulaId): ?string
    {
        $hash = substr(md5($formulaId), 0, 2);
        $shardPath = PROJECT_ROOT . "/app/config/content/formulas/{$hash}/shard_{$hash}.json";
        if (file_exists($shardPath)) {
            $data = json_decode(file_get_contents($shardPath), true);
            if (isset($data[$formulaId])) {
                return $shardPath;
            }
        }

        // Fallback: search all 256 shards
        $baseDir = PROJECT_ROOT . '/app/config/content/formulas';
        $shards = glob("{$baseDir}/*/shard_*.json");
        foreach ($shards as $file) {
            $data = json_decode(file_get_contents($file), true);
            if (is_array($data) && isset($data[$formulaId])) {
                return $file;
            }
        }

        return null;
    }

    /**
     * Resolves an existing shard or creates a canonical shard path for new formulas.
     */
    public function getOrCreateShardPathForFormula(string &$formulaId, string $defaultTitle = ''): string
    {
        $existing = $this->getShardPathForFormula($formulaId);
        if ($existing) {
            return $existing;
        }

        // If it's a synthesized or temporary ID, generate a clean slug ID
        if (empty($formulaId) || str_starts_with($formulaId, 'synthesized-')) {
            $slug = !empty($defaultTitle) ? strtolower(trim(preg_replace('/[^a-zA-Z0-9]+/', '-', $defaultTitle), '-')) : 'custom-relation';
            if (empty($slug)) $slug = 'custom-relation';
            $formulaId = $slug . '-' . substr(md5(uniqid((string)mt_rand(), true)), 0, 8);
        }

        $hash = substr(md5($formulaId), 0, 2);
        $shardDir = PROJECT_ROOT . "/app/config/content/formulas/{$hash}";
        if (!is_dir($shardDir)) {
            mkdir($shardDir, 0755, true);
        }

        return "{$shardDir}/shard_{$hash}.json";
    }

    /**
     * Creates a staged review suggestion (Contributor Tier).
     */
    public function createSuggestion(int $userId, string $formulaId, ?string $proposedLatex, ?array $proposedProse, ?string $hintText): int
    {
        $pdo = Flight::db();
        $stmt = $pdo->prepare("
            INSERT INTO formula_reviews (formula_id, user_id, proposed_latex, proposed_prose, hint_text, status)
            VALUES (?, ?, ?, ?, ?, 'pending')
        ");

        $proseJson = !empty($proposedProse) ? json_encode($proposedProse, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : null;
        $stmt->execute([
            $formulaId,
            $userId,
            $proposedLatex,
            $proseJson,
            $hintText
        ]);

        return (int)$pdo->lastInsertId();
    }

    /**
     * Fetches reviews filtered by status or formulaId.
     */
    public function getReviews(string $status = 'pending', ?string $formulaId = null): array
    {
        $pdo = Flight::db();
        $sql = "
            SELECT r.*, u.display_name AS author_name, u.role AS author_role, u.avatar_url AS author_avatar,
                   rev.display_name AS reviewer_name
            FROM formula_reviews r
            JOIN users u ON r.user_id = u.id
            LEFT JOIN users rev ON r.reviewed_by = rev.id
            WHERE 1=1
        ";
        $params = [];

        if ($status !== 'all') {
            $sql .= " AND r.status = ?";
            $params[] = $status;
        }
        if (!empty($formulaId)) {
            $sql .= " AND r.formula_id = ?";
            $params[] = $formulaId;
        }

        $sql .= " ORDER BY r.created_at DESC LIMIT 100";
        $stmt = $pdo->prepare($sql);
        $stmt->execute($params);

        $results = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($results as &$row) {
            if (!empty($row['proposed_prose'])) {
                $row['proposed_prose'] = json_decode($row['proposed_prose'], true);
            }
        }

        return $results;
    }

    /**
     * Approves a review and executes the repair pipeline (Curator / Admin Tier).
     */
    public function approveReview(int $reviewId, int $reviewerId): array
    {
        $pdo = Flight::db();
        $stmt = $pdo->prepare("SELECT * FROM formula_reviews WHERE id = ? AND status = 'pending'");
        $stmt->execute([$reviewId]);
        $review = $stmt->fetch(PDO::FETCH_ASSOC);

        if (!$review) {
            throw new \InvalidArgumentException("Pending review #{$reviewId} not found.");
        }

        $formulaId = $review['formula_id'];
        $proposedLatex = $review['proposed_latex'];
        $proposedProse = !empty($review['proposed_prose']) ? json_decode($review['proposed_prose'], true) : [];
        $hintText = $review['hint_text'];

        // Execute direct repair / registration
        $result = $this->directRepair($reviewerId, $formulaId, $proposedLatex, $proposedProse, $hintText, 'approved_review');

        // Update review status
        $updateStmt = $pdo->prepare("UPDATE formula_reviews SET status = 'approved', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?");
        $updateStmt->execute([$reviewerId, $reviewId]);

        return $result;
    }

    /**
     * Rejects a review suggestion with notes.
     */
    public function rejectReview(int $reviewId, int $reviewerId, ?string $notes = null): bool
    {
        $pdo = Flight::db();
        $stmt = $pdo->prepare("UPDATE formula_reviews SET status = 'rejected', reviewed_by = ?, review_notes = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?");
        return $stmt->execute([$reviewerId, $notes, $reviewId]);
    }

    /**
     * In-Process Equation Repair & Decorruption Engine (Matches CLI fixlatex exactly).
     */
    public function repairTarget(string $target, ?string $hint = null, int $userId = 1, ?array $proseOverrides = null): array
    {
        $targetId = null;
        $targetLatex = null;

        $target = trim($target);
        if (strpos($target, 'http://') === 0 || strpos($target, 'https://') === 0 || strpos($target, '?') !== false || strpos($target, 'equation-explainer') !== false) {
            $queryString = parse_url($target, PHP_URL_QUERY);
            if (empty($queryString) && strpos($target, '?') !== false) {
                $queryString = substr($target, strpos($target, '?') + 1);
            }
            if (!empty($queryString)) {
                parse_str($queryString, $params);
                if (!empty($params['id'])) {
                    $targetId = trim($params['id']);
                }
                if (!empty($params['latex'])) {
                    $targetLatex = trim($params['latex']);
                }
            }
        } else if (preg_match('/^[a-z0-9\-_]+$/i', $target) && strpos($target, '\\') === false && strpos($target, '=') === false) {
            $targetId = $target;
        } else {
            $targetLatex = $target;
        }

        // Resolve Formula ID if only LaTeX was provided
        if (empty($targetId) && !empty($targetLatex)) {
            $matched = $this->physicsService->searchFormulaByLatex($targetLatex);
            if ($matched && !empty($matched['id'])) {
                $targetId = $matched['id'];
            } else {
                $title = $proseOverrides['title'] ?? 'Custom Physical Relation';
                $slug = preg_replace('/[^a-z0-9]+/', '-', strtolower($title));
                $slug = trim($slug, '-');
                $targetId = (!empty($slug) ? $slug : 'formula') . '-' . substr(md5($targetLatex), 0, 8);
            }
        }

        if (empty($targetId)) {
            $targetId = 'formula-' . substr(md5($target), 0, 8);
        }

        return $this->directRepair($userId, $targetId, $targetLatex, $proseOverrides, $hint, 'direct_repair');
    }

    /**
     * Executes direct equation and prose repair / creation on shard, MariaDB, and index (Curator / Admin Tier).
     */
    public function directRepair(int $userId, string $formulaId, ?string $latex = null, ?array $prose = null, ?string $hint = null, string $action = 'direct_repair'): array
    {
        $defaultTitle = $prose['title'] ?? 'Custom Physical Relation';
        $shardFile = $this->getOrCreateShardPathForFormula($formulaId, $defaultTitle);
        $shardData = file_exists($shardFile) ? (json_decode(file_get_contents($shardFile), true) ?: []) : [];

        $isNew = !isset($shardData[$formulaId]);
        $repairsMade = [];

        if ($isNew) {
            $formulaData = [
                'id' => $formulaId,
                'title' => $prose['title'] ?? 'Custom Physical Relation',
                'equation' => $latex ?? '',
                'conceptual_definition' => $prose['conceptual_definition'] ?? '',
                'intuitive_summary' => $prose['intuitive_summary'] ?? '',
                'interpretation' => $prose['interpretation'] ?? '',
                'symmetry_origin' => $prose['symmetry_origin'] ?? '',
                'limits_and_boundary' => $prose['limits_and_boundary'] ?? '',
                'unit_system' => 'SI',
                'status' => 'published',
                'semantic_variables' => (object)[]
            ];
            $beforeSnapshot = [];
            $repairsMade[] = "Registered new formula '{$formulaId}' into shard " . basename($shardFile);
        } else {
            $formulaData = $shardData[$formulaId];
            $beforeSnapshot = $formulaData;
        }

        // 1. Update & Decorrupt LaTeX equation
        $cleanEq = $formulaData['equation'] ?? '';
        if (!empty($latex)) {
            $cleanEq = $latex;
        }
        $decorruptedEq = $this->decorruptLatex($cleanEq);
        if ($decorruptedEq !== $cleanEq) {
            $cleanEq = $decorruptedEq;
            $repairsMade[] = "Decorrupted LaTeX equation: {$cleanEq}";
        }

        // 2. Merge prose overrides if provided
        if (!empty($prose) && is_array($prose)) {
            foreach ($prose as $field => $val) {
                if (is_string($val) && ($isNew || trim($val) !== '') && (!isset($formulaData[$field]) || $formulaData[$field] !== $val)) {
                    $sanitizedVal = $this->sanitizeProse($val);
                    if ($isNew || $sanitizedVal !== ($formulaData[$field] ?? '')) {
                        $formulaData[$field] = $sanitizedVal;
                        $repairsMade[] = "Updated narrative field: '{$field}'";
                    }
                }
            }
        }

        // 3. Apply hint / reference text parser if provided
        if (!empty($hint)) {
            $this->applyHintText($formulaData, $cleanEq, $hint, $repairsMade);
        }

        // 4. Sanitize prose fields
        $proseFields = ['description', 'conceptual_definition', 'intuitive_summary', 'interpretation', 'symmetry_origin', 'limits_and_boundary'];
        foreach ($proseFields as $f) {
            if (isset($formulaData[$f]) && is_string($formulaData[$f])) {
                $sanitized = $this->sanitizeProse($formulaData[$f]);
                if ($sanitized !== $formulaData[$f]) {
                    $formulaData[$f] = $sanitized;
                    $repairsMade[] = "Sanitized math delimiters in '{$f}'";
                }
            }
        }

        // 5. Sanitize semantic variables
        $semVars = $formulaData['semantic_variables'] ?? [];
        if (!is_array($semVars) || empty($semVars)) {
            $formulaData['semantic_variables'] = (object)[];
        } else {
            $cleanSemVars = [];
            foreach ($semVars as $k => $v) {
                $cleanK = str_replace('$', '', trim($k));
                $cleanSemVars[$cleanK] = $v;
            }
            $formulaData['semantic_variables'] = $cleanSemVars;
        }

        // 6. Commit to Shard File
        $formulaData['equation'] = $cleanEq;
        $shardData[$formulaId] = $formulaData;

        // Clean neighbor formula semantic_variables format
        foreach ($shardData as $fKey => &$fVal) {
            if (is_array($fVal)) {
                $sVars = $fVal['semantic_variables'] ?? [];
                if (!is_array($sVars) || empty($sVars)) {
                    $fVal['semantic_variables'] = (object)[];
                }
            }
        }
        unset($fVal);

        file_put_contents($shardFile, json_encode($shardData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);

        // 7. Commit to MariaDB (INSERT or UPDATE with equation_svg = NULL for clean client MathJax)
        $pdo = Flight::db();
        $dbStmt = $pdo->prepare("
            INSERT INTO formulas (id, title, equation, equation_svg, conceptual_definition, intuitive_summary, interpretation, symmetry_origin, limits_and_boundary, semantic_variables, status)
            VALUES (?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, 'published')
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                equation = VALUES(equation),
                equation_svg = NULL,
                conceptual_definition = VALUES(conceptual_definition),
                intuitive_summary = VALUES(intuitive_summary),
                interpretation = VALUES(interpretation),
                symmetry_origin = VALUES(symmetry_origin),
                limits_and_boundary = VALUES(limits_and_boundary),
                semantic_variables = VALUES(semantic_variables),
                status = 'published'
        ");

        $dbStmt->execute([
            $formulaId,
            $formulaData['title'] ?? 'Custom Physical Relation',
            $cleanEq,
            $formulaData['conceptual_definition'] ?? null,
            $formulaData['intuitive_summary'] ?? null,
            $formulaData['interpretation'] ?? null,
            $formulaData['symmetry_origin'] ?? null,
            $formulaData['limits_and_boundary'] ?? null,
            isset($formulaData['semantic_variables']) ? json_encode($formulaData['semantic_variables'], JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) : null
        ]);

        // 8. Synchronize formulas_latex_index.json
        $latexIndexFile = PROJECT_ROOT . '/app/config/formulas_latex_index.json';
        if (file_exists($latexIndexFile)) {
            $indexData = json_decode(file_get_contents($latexIndexFile), true) ?: [];
            $normLatex = $this->physicsService->normalizeLatex($cleanEq);
            if (!empty($normLatex)) {
                $indexData[$normLatex] = $formulaId;
                file_put_contents($latexIndexFile, json_encode($indexData, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE), LOCK_EX);
            }
        }

        $afterSnapshot = $formulaData;

        // 9. Record Audit Log
        $auditStmt = $pdo->prepare("
            INSERT INTO formula_audit_logs (formula_id, user_id, action, before_snapshot, after_snapshot, applied_diff, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ");
        $ip = $_SERVER['REMOTE_ADDR'] ?? '127.0.0.1';
        $auditStmt->execute([
            $formulaId,
            $userId,
            $action,
            json_encode($beforeSnapshot, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
            json_encode($afterSnapshot, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE),
            implode("; ", $repairsMade),
            $ip
        ]);

        return [
            'formula_id' => $formulaId,
            'shard_file' => $shardFile,
            'clean_equation' => $cleanEq,
            'repairs_made' => $repairsMade,
            'formula' => $formulaData
        ];
    }

    /**
     * Decorrupts LaTeX equation strings (e.g. converting slash derivatives and restoring math operators).
     */
    public function decorruptLatex(string $latex): string
    {
        $clean = trim($latex);
        if (empty($clean)) return '';

        // 1. Extract clean LaTeX if raw SVG or HTML was passed
        if (strpos($clean, 'data-tex=') !== false && preg_match('/data-tex="([^"]+)"/i', $clean, $m)) {
            $clean = html_entity_decode($m[1], ENT_QUOTES | ENT_HTML5, 'UTF-8');
        } else if (strpos($clean, '<svg') !== false || strpos($clean, '<div') !== false) {
            $clean = strip_tags($clean);
            $clean = html_entity_decode($clean, ENT_QUOTES | ENT_HTML5, 'UTF-8');
        }

        // 2. Strip equation delimiter wrappers: \[ ... \], $$ ... $$, \( ... \)
        $clean = preg_replace('/^\\\\\[\s*/', '', $clean);
        $clean = preg_replace('/\s*\\\\\]$/', '', $clean);
        $clean = preg_replace('/^\$\$\s*/', '', $clean);
        $clean = preg_replace('/\s*\$\$$/', '', $clean);
        $clean = preg_replace('/^\\\\\(\s*/', '', $clean);
        $clean = preg_replace('/\s*\\\\\)$/', '', $clean);
        $clean = trim($clean);

        // 3. Slash derivative conversion: dp^u/dtau -> \frac{dp^\mu}{d\tau}, dp/dt -> \frac{dp}{dt}
        if (preg_match('/dp\^?\\\\?([a-zA-Z]+)\/d\\\\?([a-zA-Z]+)/', $clean)) {
            $clean = preg_replace('/dp\^?\\\\?([a-zA-Z]+)\/d\\\\?([a-zA-Z]+)/', '\\frac{dp^\\1}{d\\\\\\2}', $clean);
        }
        if (preg_match('/dp\/dt/', $clean)) {
            $clean = preg_replace('/dp\/dt/', '\\frac{dp}{dt}', $clean);
        }

        $clean = strtr($clean, [
            'dau' => '\\tau',
            'extbf' => '\\mathbf',
            '\\par' => ' ',
        ]);

        return trim($clean);
    }

    /**
     * Sanitizes prose strings with precision math delimiter boundaries and paragraph preservation.
     */
    public function sanitizeProse(string $text): string
    {
        if (empty($text)) return '';

        // Fast-path early exit for clean prose containing no LaTeX or special TeX characters
        if (strpos($text, '$') === false && strpos($text, '\\') === false && !preg_match('/[χμ⟨∇]/u', $text)) {
            return $text;
        }

        $originalInput = $text;

        // 1. Optimized symbol lookup table & unescaped character corruptions
        $text = strtr($text, [
            'χ_m' => '$\\chi_m$',
            'μ_0' => '$\\mu_0$',
            '4π'  => '$4\\pi$',
            'dau' => '\\tau',
            'extbf' => '\\mathbf',
            '\\text{\\} \\text{' => '$\\epsilon_0$',
            '\\text{\\} \\text$' => '$\\epsilon_0$',
            '\\text{\\}' => '$\\epsilon_0$',
        ]);

        // Replace orphaned 'abla' or '\\n\\nabla' that resulted from corrupted '\nabla'
        $text = preg_replace('/(?<![a-zA-Z])abla\b/u', '\\nabla', $text);
        $text = preg_replace('/\\\\n\\\\nabla/u', '\\nabla', $text);
        $text = preg_replace('/\\\\n\s*\\\\nabla/u', '\\nabla', $text);
        $text = preg_replace('/\\$\\s*\\\\n\\s*\\$\\s*\\\\nabla/u', '$\\nabla', $text);

        // 2. Fix specific legacy corrupted TeX patterns
        $text = preg_replace('/[χ\chi]_[m]\s*=\s*-\s*\$\s*\\\\frac\{[^}]+\}\{[^}]+\}\s*\$\s*[⟨<]\s*r\^2\s*[⟩>]/u', '$\\chi_m = -\\frac{\\mu_0 N Z e^2}{6m_e} \\langle r^2 \\rangle$', $text);
        $text = preg_replace('/-\$\s*\\\\frac\{\\\\rho\}\{"\}\s*\$/u', '$-\\frac{\\rho}{\\epsilon_0}$', $text);
        $text = preg_replace('/\\\\frac\{\\\\rho\}\{"\}/u', '\\frac{\\rho}{\\epsilon_0}', $text);

        // 3. Fix fragmented math delimiters in continuity and electrostatics equations
        $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ +$\\nabla \\cdot (\\rho \\mathbf{u})$ = 0$', '$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
        $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ + $\\nabla \\cdot$ ($\\rho \\mathbf{u}$) = 0$', '$\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
        $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ > 0$', '$\\frac{\\partial \\rho}{\\partial t} > 0$', $text);
        $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ < 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) < 0$', $text);
        $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ < 0$', '$\\frac{\\partial \\rho}{\\partial t} < 0$', $text);
        $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ > 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) > 0$', $text);
        $text = str_replace('$\\frac{\\partial \\rho}{\\partial t}$ = 0$', '$\\frac{\\partial \\rho}{\\partial t} = 0$', $text);
        $text = str_replace('$\\nabla \\cdot (\\rho \\mathbf{u})$ = 0$', '$\\nabla \\cdot (\\rho \\mathbf{u}) = 0$', $text);
        $text = str_replace('solenoidality of velocity field \\nabla \\cdot \\mathbf{u} = 0.', 'solenoidality of velocity field $\\nabla \\cdot \\mathbf{u} = 0$.', $text);

        // Fix Poisson/Laplace corruptions
        $text = preg_replace('/\\\\nabla\s+imes\s+E\s*=\s*0/u', '$\\nabla \\times \\mathbf{E} = 0$', $text);
        $text = preg_replace('/\\\\nabla\s+\\\\bullet\s+E\s*=\s*\\$?\\\\[fF]rac\{\\\\rho\}\{[^}]+\}\$?/u', '$\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}$', $text);
        $text = preg_replace('/E\s*=\s*-\s*\\\\nabla\s+V/u', '$\\mathbf{E} = -\\nabla V$', $text);
        $text = preg_replace('/\\\\nabla\s+\\\\bullet\s+\(-\s*\\\\nabla\s+V\)\s*=\s*\\$?\\\\[fF]rac\{\\\\rho\}\{[^}]+\}\$?/u', '$\\nabla \\cdot (-\\nabla V) = \\frac{\\rho}{\\epsilon_0}$', $text);
        $text = preg_replace('/\\\\nabla\^2\s+V\s*=\s*-\s*\\$?\\\\[fF]rac\{\\\\rho\}\{[^}]+\}\$?/u', '$\\nabla^2 V = -\\frac{\\rho}{\\epsilon_0}$', $text);
        $text = preg_replace('/\\\\nabla\^2\s+V\s*=\s*0/u', '$\\nabla^2 V = 0$', $text);
        $text = str_replace('$\\bullet$', '$\\cdot$', $text);
        $text = preg_replace('/r\s*\$o\s*\\\\text\{\s*infinity,\s*\}\s*\$\s*V\s*\\$\\to\\\$\s*0/u', '$r \\to \\infty$, $V \\to 0$', $text);

        // Fix broken ext{ / $\rho ext{$ patterns
        $text = preg_replace('/([a-zA-Z0-9_\-\\\\]+)\s+ext\{\s*([^}]+)\s*\}/u', '$\1$ \\2', $text);
        $text = preg_replace('/\\$\\s*\\\\rho\s+ext\\{\\s*\\$/u', '$\\rho$', $text);
        $text = preg_replace('/\\$\\s*\\\\rho\\s*\\$/u', '$\\rho$', $text);
        $text = preg_replace('/\\}\s*\\$\\s*\\\\rho\\s*\\$\s*ext\\{/u', '$\\rho$', $text);
        $text = preg_replace('/\\}\s*V\s*ext\\{/u', '$V$', $text);
        $text = preg_replace('/\\\\nabla\^2\s+V\s+ext\{/u', '$\\nabla^2 V$', $text);

        // 4. General fraction and operator fixes
        $text = preg_replace('/\\\\[fF]rac\{\s*\\\\partial\s*([a-zA-Z0-9_\-\\\\]+)\s*\$\s*\}\{\s*\$?\\\\partial\s*\$?\s*([a-zA-Z0-9_\-\\\\]+)\s*\}\$?/u', '$\\frac{\\partial $1}{\\partial $2}$', $text);

        // 5. Additional symbol replacements
        $text = preg_replace('/(?<!\\\\|\{)m_e(?!\})/u', '$m_e$', $text);
        $text = preg_replace('/[⟨<]\s*r\^2\s*[⟩>]/u', '$\\langle r^2 \\rangle$', $text);

        // 6. Clean up double $$
        $text = preg_replace('/\$\$+/', '$', $text);

        // 7. Standard TeX fixes
        $text = preg_replace('/\\\\frac\{dp\^\$\s*u\}\{dau\}/i', '\\frac{dp^\\mu}{d\\tau}', $text);
        $text = preg_replace('/F\^\{u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
        $text = preg_replace('/F\^\{\$u\$\\\\rho\$\}/i', 'F^{\\mu\\rho}', $text);
        $text = preg_replace('/U_\$\\rho/i', 'U_\\rho', $text);
        $text = preg_replace('/You_\s*\$\s*u\s*\$to\$/i', 'four-velocity $U_\\mu$ to', $text);

        // 8. Fix fragmented sums, vector displacement, and absolute bounds
        $text = str_replace("'V(\$\\mathbf{r}_i$ - \$\\mathbf{R}_I$)'", "'\$V(\\mathbf{r}_i - \\mathbf{R}_I)\$'", $text);
        $text = str_replace("'(\\mathbf{r}_i - \\mathbf{R}_I)\$'", "'\$V(\\mathbf{r}_i - \\mathbf{R}_I)\$'", $text);
        $text = str_replace("'(\$\\mathbf{r}_i$ - \$\\mathbf{R}_I$)'", "'\$\\mathbf{r}_i - \\mathbf{R}_I\$'", $text);
        $text = str_replace("'\$\\sum_{i$, I}'", "'\$\\sum_{i, I}\$'", $text);
        $text = str_replace("\$\\sum_{i$, I}", "\$\\sum_{i, I}\$", $text);
        $text = str_replace("'|\$\\mathbf{r}_i$ - \$\\mathbf{R}_I$| \$\\to\\infty$'", "'\$|\\mathbf{r}_i - \\mathbf{R}_I| \\to \\infty\$'", $text);
        $text = str_replace("'|\$\\mathbf{r}_i$ - \$\\mathbf{R}_I$| \$\\to\$ 0'", "'\$|\\mathbf{r}_i - \\mathbf{R}_I| \\to 0\$'", $text);

        $res = preg_replace('/\'?V\(\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\)\'?/u', '\'$V(\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4})\'', $text);
        if (!empty($res)) $text = $res;

        $res = preg_replace('/\'?\|\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\|\s*\$\\\\to\\\\infty\$\'?/u', '\'$|\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4}| \\to \\infty$\'', $text);
        if (!empty($res)) $text = $res;

        $res = preg_replace('/\'?\|\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\s*-\s*\$\\\\mathbf\{([a-zA-Z]+)\}_([a-zA-Z0-9]+)\$\|\s*\$\\\\to\$\s*0\'?/u', '\'$|\\mathbf{$1}_{$2} - \\mathbf{$3}_{$4}| \\to 0$\'', $text);
        if (!empty($res)) $text = $res;

        // 9. Precision Math Delimiter Sanitizer
        $parts = explode('$', $text);
        for ($i = 0; $i < count($parts); $i += 2) {
            $segment = $parts[$i];
            
            // Wrap fraction equations: e.g. F_i = -\frac{\partial V}{\partial q_i}
            $segment = preg_replace_callback('/(?<![a-zA-Z0-9$\\\\])((?:[A-Za-z](?:_[a-zA-Z0-9]+)?\s*=\s*)?(?:-\\s*)?\\\\frac\{[^{}]+\}\{[^{}]+\}(?:\s*=\s*0)?)(?![a-zA-Z0-9$])/u', function($m) {
                return '$' . trim($m[1]) . '$';
            }, $segment);

            // Wrap Euler-Lagrange differential form
            $segment = preg_replace_callback('/(?<![a-zA-Z0-9$\\\\])(\\\\frac\{d\}\{dt\}\\\\left\(\\\\frac\{\\\\partial L\}\{\\\\partial \\\\dot\{q\}_i\}\\\\right\)\s*-\s*\\\\frac\{\\\\partial L\}\{\\\\partial q_i\}\s*=\s*Q_i(?:\^\{?\\\\?text\{nc\}|nc\}?|\^\{nc\}))(?![a-zA-Z0-9$])/u', function($m) {
                $math = str_replace('Q_i^{nc}', 'Q_i^{\\text{nc}}', $m[1]);
                $math = str_replace('Q_i^nc', 'Q_i^{\\text{nc}}', $math);
                return '$' . trim($math) . '$';
            }, $segment);

            // Wrap logic quantifiers and ontological predicates
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(\\\\exists\s+[a-zA-Z0-9]+(?:\s*:\s*[PQR]\([a-zA-Z0-9]+\))?(?:\s*(?:\\\\implies|\\\\iff|→)\s*(?:\\\\text\{Ont\}|Ont)\([a-zA-Z0-9]+\))?)(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(\\\\exists\s+[a-zA-Z0-9]+|\\\\forall\s+[a-zA-Z0-9]+)(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])([PQR]\([a-zA-Z0-9]+\))(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(?:\\\\text\{Ont\}|Ont)\(([a-zA-Z0-9]+)\)(?![a-zA-Z0-9$])/u', '$\\text{Ont}($1)$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(\\\\implies|\\\\iff)(?![a-zA-Z0-9$])/u', '$$1$', $segment);

            // Wrap sub-indexed thermodynamic and physical variables (e.g. B_i - B_j, k_B T, B_i, B_j)
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])([A-Za-z]_[a-zA-Z0-9]+\s*[-+><=]\s*[A-Za-z]_[a-zA-Z0-9]+)(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(k_B\s*T|k_B)(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])(T\s*\\\\to\s*0(?:\s*\\\\text\{K\}|K)?|T\s*\\\\to\s*\\\\infty|v\s*\\\\to\s*c|\\\\hbar\s*\\\\to\s*0)(?![a-zA-Z0-9$])/u', '$$1$', $segment);

            // Wrap common isolated relations
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])L\s*=\s*T\s*-\s*V(?![a-zA-Z0-9$])/u', '$L = T - V$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])p_i\s*=\s*\\\\frac\{\\\\partial L\}\{\\\\partial \\\\dot\{q\}_i\}(?![a-zA-Z0-9$])/u', '$p_i = \\frac{\\partial L}{\\partial \\dot{q}_i}$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])Q_i\^?\{?nc\}?(?![a-zA-Z0-9$])/u', '$Q_i^{\\text{nc}}$', $segment);
            $segment = preg_replace('/(?<![a-zA-Z0-9$\\\\])([FqpB]_[a-zA-Z0-9]+)(?![a-zA-Z0-9$])/u', '$$1$', $segment);
            
            $parts[$i] = $segment;
        }
        $text = implode('$', $parts);

        // 10. Clean duplicate dollars and normalize spacing while preserving paragraph newlines
        $text = preg_replace('/\$+/', '$', $text);
        $text = preg_replace('/\$\s*\$/', '', $text);
        $lines = explode("\n", $text);
        $lines = array_map(function($line) {
            return trim(preg_replace('/[ \t]+/', ' ', $line));
        }, $lines);
        $cleaned = trim(implode("\n", $lines));
        return !empty($cleaned) ? $cleaned : $originalInput;
    }

    /**
     * Parses free-form reference text with headings into targeted formula fields.
     */
    protected function applyHintText(array &$formulaData, string &$cleanEq, string $hintText, array &$repairsMade): void
    {
        $normalized = str_replace(["\r\n", "\r"], "\n", $hintText);
        $headingPatterns = [
            'limits_and_boundary' => '/(?:^|\n)(?:#{1,4}\s*)?(?:3\.\s*Foundational\s*Anchor:\s*Limits|Limiting\s*Cases\s*&?\s*Boundaries|Limits\s*&?\s*Boundaries|Limiting\s*Cases)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Interpretation|Symmetry|Conceptual|Intuitive|Equation|$)))/is',
            'interpretation'      => '/(?:^|\n)(?:#{1,4}\s*)?(?:1\.\s*Constitutive\s*Identity:\s*Interpretation|Interpretation\s*\(Local\s*Identity\)|Interpretation)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Symmetry|Limiting|Limits|Conceptual|Intuitive|Equation|$)))/is',
            'symmetry_origin'     => '/(?:^|\n)(?:#{1,4}\s*)?(?:2\.\s*Invariance\s*Vector:\s*Symmetry|Symmetry\s*&?\s*Coordinate\s*Invariance|Symmetry\s*Origin|Symmetry)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Interpretation|Limiting|Limits|Conceptual|Intuitive|Equation|$)))/is',
            'conceptual_definition' => '/(?:^|\n)(?:#{1,4}\s*)?(?:Conceptual\s*Definition|Definition)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Interpretation|Symmetry|Limiting|Limits|Intuitive|Equation|$)))/is',
            'intuitive_summary'   => '/(?:^|\n)(?:#{1,4}\s*)?(?:Intuitive\s*Summary|Summary)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Interpretation|Symmetry|Limiting|Limits|Conceptual|Equation|$)))/is',
            'equation'            => '/(?:^|\n)(?:#{1,4}\s*)?(?:Equation|Formula\s*LaTeX|LaTeX)[:\s]*(.*?)(?=(?:\n(?:#{1,4}\s*)?(?:Interpretation|Symmetry|Limiting|Limits|Conceptual|Intuitive|$)))/is',
        ];

        $matchedAny = false;
        foreach ($headingPatterns as $field => $pattern) {
            if (preg_match($pattern, $normalized, $matches)) {
                $content = trim($matches[1]);
                if (!empty($content)) {
                    $matchedAny = true;
                    if ($field === 'equation') {
                        $cleanEq = $content;
                        $repairsMade[] = "Overrode LaTeX equation from reference section: {$cleanEq}";
                    } else {
                        $formulaData[$field] = $this->sanitizeProse($content);
                        $repairsMade[] = "Updated '{$field}' from reference text section";
                    }
                }
            }
        }

        // If no specific headings matched, append/update limits_and_boundary or general hint
        if (!$matchedAny && strlen($hintText) > 10) {
            if (stripos($hintText, 'limit') !== false || stripos($hintText, 'boundary') !== false) {
                $formulaData['limits_and_boundary'] = $this->sanitizeProse($hintText);
                $repairsMade[] = "Updated 'limits_and_boundary' from plain reference text";
            }
        }
    }
}
