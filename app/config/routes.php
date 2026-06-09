<?php

use app\controllers\ApiExampleController;
use app\controllers\PhysicsController;
use app\middlewares\SecurityHeadersMiddleware;
use flight\Engine;
use flight\net\Router;

/** 
 * @var Router $router 
 * @var Engine $app
 */

// This wraps all routes in the group with the SecurityHeadersMiddleware
$router->group('', function(Router $router) use ($app) {

	$router->get('/', [ $app->physicsController(), 'index' ]);

	$router->get('/hello-world/@name', function($name) {
		echo '<h1>Hello world! Oh hey '.$name.'!</h1>';
	});

	$router->group('/api', function() use ($router, $app) {
		$router->get('/users', [ $app->apiExampleController(), 'getUsers' ]);
		$router->get('/users/@id:[0-9]', [ $app->apiExampleController(), 'getUser' ]);
		$router->post('/users/@id:[0-9]', [ $app->apiExampleController(), 'updateUser' ]);
	});

	$router->group('/physics', function() use ($router, $app) {
		$router->get('/', [ $app->physicsController(), 'index' ]);
		$router->get('/install', [ $app->physicsController(), 'install' ]); // New route for database initialization
		$router->get('/sync', [ $app->physicsController(), 'sync' ]);
		$router->get('/simulations', [ $app->physicsController(), 'simulations' ]);
		$router->get('/simulations/@slug', [ $app->physicsController(), 'viewSimulation' ]);
		$router->get('/topic/@slug', [ $app->physicsController(), 'viewTopic' ]);
		$router->get('/subtopic/@slug', [ $app->physicsController(), 'viewSubtopic' ]);
		$router->get('/constants', [ $app->physicsController(), 'constants' ]);
		$router->get('/symbols', [ $app->physicsController(), 'symbols' ]);
		$router->get('/dimensional-solver', [ $app->physicsController(), 'dimensionalSolver' ]);
		$router->get('/notation-toggle', [ $app->physicsController(), 'notationToggle' ]);
		$router->get('/legendre-transformer', [ $app->physicsController(), 'legendreTransformer' ]);
		$router->get('/noethers-vault', [ $app->physicsController(), 'noethersVault' ]);
		$router->get('/correspondence-workspace', [ $app->physicsController(), 'correspondenceWorkspace' ]);
		$router->get('/anthropic-tuner', [ $app->physicsController(), 'anthropicTuner' ]);
		$router->get('/genealogy-explorer', [ $app->physicsController(), 'genealogyExplorer' ]);
		$router->get('/lab-tools', [ $app->physicsController(), 'labTools' ]);
		$router->get('/search-index', [ $app->physicsController(), 'searchIndex' ]);

		// Admin & Developer Control Panel Routes
		$router->get('/admin/dashboard', [ $app->physicsController(), 'adminDashboard' ]);
		$router->get('/admin/editor', [ $app->physicsController(), 'wysiwygEditor' ]);
		$router->get('/admin/critic', [ $app->physicsController(), 'criticPortal' ]);
		$router->post('/admin/api/run-autolinker', [ $app->physicsController(), 'apiRunAutoLinker' ]);
		$router->post('/admin/api/run-critic', [ $app->physicsController(), 'apiRunCritic' ]);
		$router->post('/admin/api/register-reference', [ $app->physicsController(), 'apiRegisterReference' ]);
		$router->post('/admin/api/update-verification', [ $app->physicsController(), 'apiUpdateVerification' ]);
		$router->post('/admin/api/save-draft', [ $app->physicsController(), 'apiSaveDraft' ]);
		$router->get('/admin/api/get-subtopic/@slug', [ $app->physicsController(), 'apiGetSubtopic' ]);
	});
	
}, [ SecurityHeadersMiddleware::class ]);