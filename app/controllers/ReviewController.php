<?php

namespace app\controllers;

use flight\Engine;
use Flight;

class ReviewController
{
    protected Engine $app;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    private function jsonResponse(array $payload, int $status = 200): void
    {
        $this->app->json($payload, $status);
    }

    private function safeErrorMessage(\Throwable $e, string $fallback): string
    {
        $auth = Flight::authService();
        if ($auth->isProduction()) {
            error_log('[ReviewController] ' . $e->getMessage());
            return $fallback;
        }
        return $fallback . ': ' . $e->getMessage();
    }

    /**
     * REST Endpoint: Get Current Authenticated User & Role
     */
    public function apiGetCurrentUser()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        $this->jsonResponse([
            'success' => true,
            'user' => [
                'id' => $user->id ?? 0,
                'display_name' => $user->display_name ?? 'Anonymous Visitor',
                'email' => $user->email ?? '',
                'role' => $user->role ?? 'guest',
                'avatar_url' => $user->avatar_url ?? null
            ]
        ]);
    }

    /**
     * REST Endpoint: Switch Dev Mock Role (Development Mode Only)
     */
    public function apiSwitchDevRole()
    {
        $input = json_decode(file_get_contents('php://input'), true);
        $role = $input['role'] ?? 'guest';

        $auth = Flight::authService();
        $success = $auth->switchDevRole($role);
        $user = $auth->getCurrentUser();

        $this->jsonResponse([
            'success' => $success,
            'user' => [
                'id' => $user->id ?? 0,
                'display_name' => $user->display_name ?? 'Anonymous Visitor',
                'email' => $user->email ?? '',
                'role' => $user->role ?? 'guest',
                'avatar_url' => $user->avatar_url ?? null
            ]
        ], $success ? 200 : 403);
    }

    /**
     * REST Endpoint: Formula Repair (Local Studio / Curator Authority)
     * Commits changes to Git shard, hash registry, and MariaDB when authorized.
     */
    public function apiSuggestRepair()
    {
        return $this->apiApplyRepair();
    }

    /**
     * REST Endpoint: Direct Formula Repair (Curator / Admin Tier)
     */
    public function apiApplyRepair()
    {
        if (class_exists('\Tracy\Debugger')) {
            \Tracy\Debugger::$showBar = false;
        }

        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            $this->jsonResponse(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.'], 403);
            return;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $url = $input['url'] ?? '';
        $formulaId = $input['formula_id'] ?? '';
        $latex = $input['latex'] ?? null;
        $prose = $input['prose'] ?? null;
        $hint = $input['hint'] ?? null;

        // 1. Resolve Target (Formula ID takes precedence if valid, then URL query, then LaTeX)
        $target = '';
        if (!empty($formulaId) && $formulaId !== 'synthesized-custom' && !str_starts_with($formulaId, 'synthesized-')) {
            $target = $formulaId;
        } else if (!empty($url) && (strpos($url, 'id=') !== false || strpos($url, 'latex=') !== false)) {
            $target = $url;
        } else if (!empty($latex)) {
            $target = $latex;
        }

        if (empty($target)) {
            $this->jsonResponse(['success' => false, 'error' => 'Valid URL, Formula ID, or LaTeX equation is required.'], 400);
            return;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $result = $reviewService->repairTarget($target, $hint, $user->id ?: 1, $prose);

            $this->jsonResponse([
                'success' => true,
                'message' => 'Formula updated and synchronized successfully via fixlatex engine!',
                'data' => $result
            ]);
        } catch (\Throwable $e) {
            $this->jsonResponse([
                'success' => false,
                'error' => $this->safeErrorMessage($e, 'Failed to apply repair')
            ], 500);
        }
    }

    /**
     * REST Endpoint: Get Review Queue (Curator / Admin Tier)
     */
    public function apiGetReviews()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            $this->jsonResponse(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.'], 403);
            return;
        }

        $status = $_GET['status'] ?? 'pending';
        $formulaId = $_GET['formula_id'] ?? null;

        try {
            $reviewService = Flight::formulaReviewService();
            $reviews = $reviewService->getReviews($status, $formulaId);

            $this->jsonResponse(['success' => true, 'reviews' => $reviews]);
        } catch (\Throwable $e) {
            $this->jsonResponse(['success' => false, 'error' => $this->safeErrorMessage($e, 'Review operation failed')], 500);
        }
    }

    /**
     * REST Endpoint: Approve Review Suggestion (Curator / Admin Tier)
     */
    public function apiApproveReview()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            $this->jsonResponse(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.'], 403);
            return;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $reviewId = (int)($input['review_id'] ?? 0);

        if ($reviewId <= 0) {
            $this->jsonResponse(['success' => false, 'error' => 'Valid review ID is required.'], 400);
            return;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $result = $reviewService->approveReview($reviewId, $user->id);

            $this->jsonResponse([
                'success' => true,
                'message' => 'Review approved and changes committed to shard & database!',
                'data' => $result
            ]);
        } catch (\Throwable $e) {
            $this->jsonResponse(['success' => false, 'error' => $this->safeErrorMessage($e, 'Review operation failed')], 500);
        }
    }

    /**
     * REST Endpoint: Reject Review Suggestion (Curator / Admin Tier)
     */
    public function apiRejectReview()
    {
        $auth = Flight::authService();
        $user = $auth->getCurrentUser();

        if (!$auth->hasRole('curator', $user)) {
            $this->jsonResponse(['success' => false, 'error' => 'Permission denied: Curator or Admin privileges required.'], 403);
            return;
        }

        $input = json_decode(file_get_contents('php://input'), true);
        $reviewId = (int)($input['review_id'] ?? 0);
        $notes = $input['notes'] ?? null;

        if ($reviewId <= 0) {
            $this->jsonResponse(['success' => false, 'error' => 'Valid review ID is required.'], 400);
            return;
        }

        try {
            $reviewService = Flight::formulaReviewService();
            $reviewService->rejectReview($reviewId, $user->id, $notes);

            $this->jsonResponse([
                'success' => true,
                'message' => 'Review rejected.'
            ]);
        } catch (\Throwable $e) {
            $this->jsonResponse(['success' => false, 'error' => $this->safeErrorMessage($e, 'Review operation failed')], 500);
        }
    }
}
