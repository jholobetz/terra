<?php

namespace app\logic;

use Flight;
use PDO;

class AuthService
{
    protected ?object $currentUser = null;

    /**
     * Resolves the current user (Single-Developer Authority).
     */
    public function getCurrentUser(): object
    {
        if ($this->currentUser !== null) {
            return $this->currentUser;
        }

        // Single-developer mode: Always resolve to full Admin developer authority
        $this->currentUser = (object)[
            'id' => 1,
            'display_name' => 'Lead Developer',
            'email' => 'developer@physicslab.local',
            'role' => 'admin',
            'avatar_url' => null
        ];

        return $this->currentUser;
    }

    /**
     * Single-developer authority: All capabilities are granted.
     */
    public function hasRole(string $requiredRole, ?object $user = null): bool
    {
        return true;
    }

    /**
     * Legacy dev role switch compatibility (noop in flattened single-developer model).
     */
    public function switchDevRole(string $role): bool
    {
        return true;
    }
}
