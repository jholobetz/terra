<?php

require_once __DIR__ . '/../../vendor/autoload.php';
$config = require __DIR__ . '/../../app/config/config.php';

try {
    $dsn = "mysql:host={$config['database']['host']};dbname={$config['database']['dbname']};charset=utf8mb4";
    $pdo = new PDO($dsn, $config['database']['user'], $config['database']['password'], [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
    ]);

    echo "[INFO] Running RBAC & Review Queue Migration...\n";

    // 1. Create users table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS users (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            oauth_provider ENUM('github', 'google', 'dev_mock') NOT NULL,
            oauth_id VARCHAR(191) NOT NULL,
            email VARCHAR(191) NOT NULL,
            display_name VARCHAR(191) NOT NULL,
            avatar_url VARCHAR(512) NULL,
            role ENUM('guest', 'contributor', 'curator', 'admin') NOT NULL DEFAULT 'contributor',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY uk_oauth (oauth_provider, oauth_id),
            KEY idx_email (email),
            KEY idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ");
    echo "[OK] Table 'users' verified/created.\n";

    // 2. Create formula_reviews table (Staging / Quarantine)
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS formula_reviews (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            formula_id VARCHAR(191) NOT NULL,
            user_id BIGINT UNSIGNED NOT NULL,
            proposed_latex TEXT NULL,
            proposed_prose JSON NULL,
            hint_text TEXT NULL,
            status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
            reviewed_by BIGINT UNSIGNED NULL,
            review_notes TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
            KEY idx_formula_status (formula_id, status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ");
    echo "[OK] Table 'formula_reviews' verified/created.\n";

    // 3. Create formula_audit_logs table
    $pdo->exec("
        CREATE TABLE IF NOT EXISTS formula_audit_logs (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            formula_id VARCHAR(191) NOT NULL,
            user_id BIGINT UNSIGNED NOT NULL,
            action ENUM('direct_repair', 'approved_review', 'rollback', 'batch_sweep') NOT NULL,
            before_snapshot JSON NOT NULL,
            after_snapshot JSON NOT NULL,
            applied_diff TEXT NULL,
            ip_address VARCHAR(45) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            KEY idx_formula_action (formula_id, action)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    ");
    echo "[OK] Table 'formula_audit_logs' verified/created.\n";

    // 4. Seed development users for zero-friction local impersonation
    $devUsers = [
        [
            'oauth_provider' => 'dev_mock',
            'oauth_id' => 'dev_admin_1',
            'email' => 'admin@physicslab.local',
            'display_name' => 'Dr. Terra Admin',
            'avatar_url' => '/images/avatars/admin.png',
            'role' => 'admin'
        ],
        [
            'oauth_provider' => 'dev_mock',
            'oauth_id' => 'dev_curator_1',
            'email' => 'curator@physicslab.local',
            'display_name' => 'Prof. Jane Curator (Physicist)',
            'avatar_url' => '/images/avatars/curator.png',
            'role' => 'curator'
        ],
        [
            'oauth_provider' => 'dev_mock',
            'oauth_id' => 'dev_student_1',
            'email' => 'student@physicslab.local',
            'display_name' => 'Alex Contributor (Student)',
            'avatar_url' => '/images/avatars/student.png',
            'role' => 'contributor'
        ],
        [
            'oauth_provider' => 'dev_mock',
            'oauth_id' => 'dev_guest_1',
            'email' => 'guest@physicslab.local',
            'display_name' => 'Anonymous Visitor',
            'avatar_url' => null,
            'role' => 'guest'
        ]
    ];

    $stmt = $pdo->prepare("
        INSERT INTO users (oauth_provider, oauth_id, email, display_name, avatar_url, role)
        VALUES (?, ?, ?, ?, ?, ?)
        ON DUPLICATE KEY UPDATE display_name = VALUES(display_name), role = VALUES(role)
    ");

    foreach ($devUsers as $u) {
        $stmt->execute([
            $u['oauth_provider'],
            $u['oauth_id'],
            $u['email'],
            $u['display_name'],
            $u['avatar_url'],
            $u['role']
        ]);
    }
    echo "[OK] Default development users seeded successfully.\n";
    echo "[SUCCESS] Migration completed!\n";

} catch (\Throwable $e) {
    echo "[ERROR] Migration failed: " . $e->getMessage() . "\n";
    exit(1);
}
