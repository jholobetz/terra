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
     * Resolves the effective application environment across OS env vars,
     * Apache SetEnv / mod_rewrite (REDIRECT_APP_ENV), $_ENV, and config.php
     * ('app_env' -> TERRA_CONFIG_APP_ENV), accommodating Debian PHP's default
     * variables_order="GPCS" and PHP-FPM clear_env=yes settings.
     */
    public static function resolveAppEnv(?string $configAppEnv = null): string
    {
        $osEnv = getenv('APP_ENV');
        $candidates = [
            ($osEnv !== false && $osEnv !== '') ? $osEnv : null,
            $_SERVER['APP_ENV'] ?? null,
            $_SERVER['REDIRECT_APP_ENV'] ?? null,
            $_ENV['APP_ENV'] ?? null,
            $configAppEnv,
            defined('TERRA_CONFIG_APP_ENV') ? constant('TERRA_CONFIG_APP_ENV') : null,
        ];

        foreach ($candidates as $val) {
            if (is_string($val) && trim($val) !== '') {
                return strtolower(trim($val));
            }
        }

        return 'development';
    }

    /**
     * Returns true when the effective application environment is 'production'.
     */
    public function isProduction(): bool
    {
        return self::resolveAppEnv() === 'production';
    }

    /**
     * Resolves the client IP safely for rate-limiting and audit logging.
     * Ignores X-Forwarded-For / X-Real-IP headers unless REMOTE_ADDR belongs
     * to a trusted reverse proxy (loopback or TRUSTED_PROXY_IPS), preventing
     * header-rotation spoofing by direct external callers.
     */
    public function resolveClientIp(): string
    {
        $remoteAddr = trim((string)($_SERVER['REMOTE_ADDR'] ?? ''));

        $trustedProxies = ['127.0.0.1', '::1', 'localhost'];
        $extraProxies = (string)(getenv('TRUSTED_PROXY_IPS') ?: ($_ENV['TRUSTED_PROXY_IPS'] ?? ''));
        if ($extraProxies !== '') {
            foreach (explode(',', $extraProxies) as $ip) {
                $trimmed = trim($ip);
                if ($trimmed !== '') {
                    $trustedProxies[] = $trimmed;
                }
            }
        }

        // Direct external connection: never trust client-supplied forwarding headers
        if ($remoteAddr !== '' && !in_array($remoteAddr, $trustedProxies, true)) {
            return $remoteAddr;
        }

        // Behind a trusted proxy: walk X-Forwarded-For right-to-left to pick the rightmost non-proxy hop
        $forwardedFor = (string)($_SERVER['HTTP_X_FORWARDED_FOR'] ?? '');
        if ($forwardedFor !== '') {
            $hops = array_reverse(explode(',', $forwardedFor));
            foreach ($hops as $hop) {
                $candidate = trim($hop);
                if (
                    $candidate !== ''
                    && !in_array($candidate, $trustedProxies, true)
                    && filter_var($candidate, FILTER_VALIDATE_IP) !== false
                ) {
                    return $candidate;
                }
            }
        }

        $realIp = trim((string)($_SERVER['HTTP_X_REAL_IP'] ?? ''));
        if (
            $realIp !== ''
            && !in_array($realIp, $trustedProxies, true)
            && filter_var($realIp, FILTER_VALIDATE_IP) !== false
        ) {
            return $realIp;
        }

        return $remoteAddr !== '' ? $remoteAddr : 'unknown';
    }

    /**
     * Determines whether the current execution context is the local single-developer studio
     * or carries a valid explicit production admin token.
     */
    public function isLocalDevStudio(): bool
    {
        // Allow explicit token authentication when configured with a non-empty environment secret
        $expectedKey = getenv('TERRA_ADMIN_KEY') ?: ($_ENV['TERRA_ADMIN_KEY'] ?? '');
        $providedKey = $_SERVER['HTTP_X_TERRA_ADMIN_KEY'] ?? '';
        if ($expectedKey !== '' && $providedKey !== '' && hash_equals($expectedKey, $providedKey)) {
            return true;
        }

        // Never grant implicit studio authority when APP_ENV is explicitly set to production
        if ($this->isProduction()) {
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
