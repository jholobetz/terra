<?php

namespace app\logic;

use Flight;
use PDO;

class AuthService
{
    protected ?object $currentUser = null;

    const ROLE_HIERARCHY = [
        'guest' => 0,
        'contributor' => 1,
        'curator' => 2,
        'admin' => 3
    ];

    /**
     * Resolves the current user from session or development mock impersonation.
     */
    public function getCurrentUser(): object
    {
        if ($this->currentUser !== null) {
            return $this->currentUser;
        }

        $devRole = $_COOKIE['dev_mock_role'] ?? null;
        $sessionToken = $_COOKIE['terra_session'] ?? null;

        $pdo = Flight::db();

        // 1. In Local Development Mode, support instant dev role switcher
        if ($devRole && in_array($devRole, ['guest', 'contributor', 'curator', 'admin'], true)) {
            try {
                $stmt = $pdo->prepare("SELECT * FROM users WHERE oauth_provider = 'dev_mock' AND role = ? LIMIT 1");
                $stmt->execute([$devRole]);
                $user = $stmt->fetch(PDO::FETCH_OBJ);
                if ($user) {
                    $this->currentUser = $user;
                    return $this->currentUser;
                }
            } catch (\Throwable $e) {
                // fallback to synthesized guest
            }
        }

        // 2. Default to Admin in local CLI / localhost if no cookie is set yet
        if (php_sapi_name() === 'cli' || (isset($_SERVER['REMOTE_ADDR']) && in_array($_SERVER['REMOTE_ADDR'], ['127.0.0.1', '::1'], true) && !$devRole)) {
            try {
                $stmt = $pdo->prepare("SELECT * FROM users WHERE oauth_provider = 'dev_mock' AND role = 'admin' LIMIT 1");
                $stmt->execute();
                $user = $stmt->fetch(PDO::FETCH_OBJ);
                if ($user) {
                    $this->currentUser = $user;
                    return $this->currentUser;
                }
            } catch (\Throwable $e) {}
        }

        // 3. Fallback to Anonymous Guest
        $this->currentUser = (object)[
            'id' => 0,
            'display_name' => 'Anonymous Visitor',
            'email' => 'guest@physicslab.local',
            'role' => 'guest',
            'avatar_url' => null
        ];

        return $this->currentUser;
    }

    /**
     * Checks if the user meets or exceeds the required privilege level.
     */
    public function hasRole(string $requiredRole, ?object $user = null): bool
    {
        $user = $user ?? $this->getCurrentUser();
        $userLevel = self::ROLE_HIERARCHY[$user->role ?? 'guest'] ?? 0;
        $requiredLevel = self::ROLE_HIERARCHY[$requiredRole] ?? 0;

        return $userLevel >= $requiredLevel;
    }

    public function switchDevRole(string $role): bool
    {
        if (!in_array($role, ['guest', 'contributor', 'curator', 'admin'], true)) {
            return false;
        }

        $_COOKIE['dev_mock_role'] = $role;

        if (php_sapi_name() !== 'cli' && !headers_sent()) {
            setcookie('dev_mock_role', $role, [
                'expires' => time() + (86400 * 30),
                'path' => '/',
                'httponly' => false,
                'samesite' => 'Lax'
            ]);
        }

        $this->currentUser = null;
        return true;
    }
}
