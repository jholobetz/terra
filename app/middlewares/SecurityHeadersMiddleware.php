<?php
declare(strict_types=1);

namespace app\middlewares;

use flight\Engine;
use Tracy\Debugger;

class SecurityHeadersMiddleware
{
	protected Engine $app;

	public function __construct(Engine $app)
	{
		$this->app = $app;
	}

	public function before(array $params): void
	{
		$nonce = $this->app->get('csp_nonce') ?? '';
		if ($nonce === '') {
			$nonce = bin2hex(random_bytes(16));
			$this->app->set('csp_nonce', $nonce);
		}

		// Disable Tracy debug bar on API endpoints and AJAX requests to ensure clean JSON responses
		$url = $this->app->request()->url;
		if (strpos($url, '/api/') !== false || strpos($url, '/api') === 0 || $this->app->request()->ajax) {
			Debugger::$showBar = false;
		}

		$csp = "default-src 'self'; script-src 'self' 'nonce-{$nonce}'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:;";
		$this->app->response()->header('X-Frame-Options', 'SAMEORIGIN');
		$this->app->response()->header("Content-Security-Policy", $csp);
		$this->app->response()->header('X-XSS-Protection', '1; mode=block');
		$this->app->response()->header('X-Content-Type-Options', 'nosniff');
		$this->app->response()->header('Referrer-Policy', 'no-referrer-when-downgrade');
		$this->app->response()->header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
		$this->app->response()->header('Permissions-Policy', 'geolocation=()');
	}
}