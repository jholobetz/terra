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

		// Disable Tracy debug bar on API endpoints, health probes, machine-readable discovery files, and AJAX requests
		$url = $this->app->request()->url;
		$isMachineEndpoint = strpos($url, '/api/') !== false
			|| strpos($url, '/api') === 0
			|| strpos($url, '/healthz') !== false
			|| $url === '/robots.txt'
			|| $url === '/sitemap.xml'
			|| $url === '/favicon.ico'
			|| $this->app->request()->ajax;
		if ($isMachineEndpoint && class_exists(Debugger::class)) {
			Debugger::$showBar = false;
		}

		$csp = "default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'self'; form-action 'self'; script-src 'self' 'nonce-{$nonce}'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data:;";
		$this->app->response()->header('X-Frame-Options', 'SAMEORIGIN');
		$this->app->response()->header("Content-Security-Policy", $csp);
		$this->app->response()->header('X-Content-Type-Options', 'nosniff');
		$this->app->response()->header('Referrer-Policy', 'strict-origin-when-cross-origin');
		$isHttps = (!empty($_SERVER['HTTPS']) && strtolower((string)$_SERVER['HTTPS']) !== 'off')
			|| strtolower((string)($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '')) === 'https'
			|| (int)($_SERVER['SERVER_PORT'] ?? 0) === 443;
		if ($isHttps) {
			$this->app->response()->header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload');
		}
		$this->app->response()->header('Permissions-Policy', 'geolocation=(), camera=(), microphone=()');
	}
}