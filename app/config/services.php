<?php

use flight\Engine;
use flight\database\PdoWrapper;
use flight\debug\database\PdoQueryCapture;
use flight\debug\tracy\TracyExtensionLoader;
use Tracy\Debugger;

/*********************************************
 *         FlightPHP Service Setup           *
 *********************************************
 * This file registers services and integrations
 * for your FlightPHP application. Edit as needed.
 *
 * @var array  $config  From config.php
 * @var Engine $app     FlightPHP app instance
 **********************************************/



/*********************************************
 *           Session Service Setup           *
 *********************************************
 * To enable sessions in FlightPHP, register the session service.
 * Docs: https://docs.flightphp.com/awesome-plugins/session
 *
 * Example:
 *   $app->register('session', \flight\Session::class, [
 *       [
 *           'prefix' 		=> 'flight_session_', 	  // Prefix for the session cookie
 *           'save_path'    => 'path/to/my/sessions', // Path to save session files
 *           // ...other options...
 *       ]
 *   ]);
 *
 * For advanced options, see the plugin documentation above.
 **********************************************/

/*********************************************
 *           Tracy Debugger Setup            *
 *********************************************
 * Tracy is a powerful error handler and debugger for PHP.
 * Docs: https://tracy.nette.org/
 *
 * Key Tracy configuration options:
 *   - Debugger::enable([mode], [ip]);
 *       - mode: Debugger::Development or Debugger::Production
 *       - ip: restrict debug bar to specific IP(s)
 *   - Debugger::$logDirectory: where error logs are stored
 *   - Debugger::$strictMode: show all errors (true/E_ALL), or filter out deprecated notices
 *   - Debugger::$showBar: show/hide debug bar (auto-detected, can be forced)
 *   - Debugger::$maxLen: max length of dumped variables
 *   - Debugger::$maxDepth: max depth of dumped structures
 *   - Debugger::$editor: configure clickable file links (see docs)
 *   - Debugger::$email: send error notifications to email
 *
 * Example Tracy setups:
 *   Debugger::enable(); // Auto-detects environment
 *   Debugger::enable(Debugger::Development); // Explicitly set environment
 *   Debugger::enable('23.75.345.200'); // Restrict debug bar to specific IPs
 *
 * For more options, see https://tracy.nette.org/en/configuration
 **********************************************/
require_once __DIR__ . $ds . '..' . $ds . 'logic' . $ds . 'AuthService.php';
$appEnv = \app\logic\AuthService::resolveAppEnv($config['app_env'] ?? null);
$isProductionEnv = ($appEnv === 'production');

if (class_exists(Debugger::class)) {
	// Explicitly bind Tracy mode to APP_ENV so reverse proxies on 127.0.0.1 never trigger Development mode
	Debugger::enable($isProductionEnv ? Debugger::Production : Debugger::Development);
	Debugger::$logDirectory = __DIR__ . $ds . '..' . $ds . 'log';
	Debugger::$strictMode = !$isProductionEnv;
	if ($isProductionEnv) {
		Debugger::$showBar = false;
	} elseif (Debugger::$showBar === true && php_sapi_name() !== 'cli') {
		$app->set('flight.content_length', false); // Prevent Content-Length conflict with Tracy Debug Bar
		if (class_exists(TracyExtensionLoader::class)) {
			(new TracyExtensionLoader($app)); // Load FlightPHP Tracy extensions when dev dependencies are installed
		}
	}
}

/**********************************************
 *           Database Service Setup           *
 **********************************************/
if (!isset($config['database']['host'])) {
    $app->halt(500, 'Database configuration missing. Please check app/config/config.php');
}

$dsn = 'mysql:host=' . $config['database']['host'] . ';dbname=' . $config['database']['dbname'] . ';charset=utf8mb4';

// Register Flight::db() service
// In development, use PdoQueryCapture when available; in production, always use PdoWrapper for performance.
$showDebugBar = !$isProductionEnv && class_exists(Debugger::class) && (Debugger::$showBar === true);
$pdoClass = ($showDebugBar && class_exists(PdoQueryCapture::class)) ? PdoQueryCapture::class : PdoWrapper::class;
$app->register('db', $pdoClass, [$dsn, $config['database']['user'] ?? null, $config['database']['password'] ?? null]);

/**********************************************
 *         Third-Party Integrations           *
 **********************************************/
// Google OAuth Example:
// $app->register('google_oauth', Google_Client::class, [ $config['google_oauth'] ]);

// Redis Example:
// $app->register('redis', Redis::class, [ $config['redis']['host'], $config['redis']['port'] ]);

$app->register('physicsService', \app\logic\PhysicsService::class, [ $app ]);
$app->register('authService', \app\logic\AuthService::class, []);
$app->register('formulaReviewService', \app\logic\FormulaReviewService::class, []);
$app->register('semanticSearchService', \app\logic\SemanticSearchService::class, []);
$app->register('physicsController', \app\controllers\PhysicsController::class, [ $app ]);
$app->register('adminController', \app\controllers\AdminController::class, [ $app ]);
$app->register('reviewController', \app\controllers\ReviewController::class, [ $app ]);

// Route uncaught exceptions through Flight's error handler in production or when Tracy (--no-dev) is absent
$app->set('flight.handle_errors', $isProductionEnv || !class_exists(Debugger::class));

// Branded 404 and 500 error handlers (HTML for browsers, JSON for /api/* requests)
$app->map('notFound', function () use ($app): void {
	$app->physicsController()->renderNotFound();
});

$app->map('error', function (\Throwable $e) use ($app): void {
	$app->physicsController()->renderServerError($e);
});

// Add more service registrations below as needed
