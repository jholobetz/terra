<?php

namespace app\logic;

use Flight;
use PDO;

class AuthService
{
    protected ?object $currentUser = null;

    protected const ROLE_HIERARCHY = [
        'guest' => 0,
        'contributor' => 1,
        'curator' => 2,
        'admin' => 3,
    ];

    /**
     * Determines whether the current execution context is the local single-developer studio
     * or carries a valid explicit production admin token.
     */
    public function isLocalDevStudio(): bool
    {
        $appEnv = getenv('APP_ENV') ?: ($_ENV['APP_ENV'] ?? 'development');

        // Allow explicit token authentication when configured with a non-empty environment secret
        $expectedKey = getenv('TERRA_ADMIN_KEY') ?: ($_ENV['TERRA_ADMIN_KEY'] ?? '');
        $providedKey = $_SERVER['HTTP_X_TERRA_ADMIN_KEY'] ?? '';
        if ($expectedKey !== '' && $providedKey !== '' && hash_equals($expectedKey, $providedKey)) {
            return true;
        }

        // Never grant implicit studio authority when APP_ENV is explicitly set to production
        if ($appEnv === 'production') {
            return false;
        }

        if (php_sapi_name() === 'cli' && !isset($_SERVER['REMOTE_ADDR'])) {
            return true;
        }

        $remoteAddr = $_SERVER['REMOTE_ADDR'] ?? '';
        $loopbackIps = ['127.0.0.1', '::1', 'localhost'];
        if (!in_array($remoteAddr, $loopbackIps, true)) {
            return false;
        }

        // Guard against reverse-proxy forwarded external requests appearing as 127.0.0.1
        $forwardedFor = $_SERVER['HTTP_X_FORWARDED_FOR'] ?? ($_SERVER['HTTP_X_REAL_IP'] ?? '');
        if ($forwardedFor !== '') {
            $clientIp = trim(explode(',', $forwardedFor)[0]);
            if (!in_array($clientIp, $loopbackIps, true)) {
                return false;
            }
        }

        return true;
    }

    /**
     * Resolves the current user:
     * - Local Single-Developer Studio: Full Admin developer authority.
     * - Public Web / Production Visitor: Read-only Guest profile.
     */
    public function getCurrentUser(): object
    {
        if ($this->currentUser !== null) {
            return $this->currentUser;
        }

        if ($this->isLocalDevStudio()) {
            $this->currentUser = (object)[
                'id' => 1,
                'display_name' => 'Lead Developer',
                'email' => 'developer@physicslab.local',
                'role' => 'admin',
                'avatar_url' => null
            ];
        } else {
            $this->currentUser = (object)[
                'id' => 0,
                'display_name' => 'Anonymous Visitor',
                'email' => '',
                'role' => 'guest',
                'avatar_url' => null
            ];
        }

        return $this->currentUser;
    }

    /**
     * Evaluates whether the user satisfies the required role tier.
     */
    public function hasRole(string $requiredRole, ?object $user = null): bool
    {
        $targetUser = $user ?? $this->getCurrentUser();
        $userRole = $targetUser->role ?? 'guest';

        $userLevel = self::ROLE_HIERARCHY[$userRole] ?? 0;
        $requiredLevel = self::ROLE_HIERARCHY[$requiredRole] ?? 99;

        return $userLevel >= $requiredLevel;
    }

    /**
     * Switches the active mock role in local development studio mode only.
     */
    public function switchDevRole(string $role): bool
    {
        if (!$this->isLocalDevStudio()) {
            return false;
        }

        if (!isset(self::ROLE_HIERARCHY[$role])) {
            return false;
        }

        $user = $this->getCurrentUser();
        $user->role = $role;
        return true;
    }
}
