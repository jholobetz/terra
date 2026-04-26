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
		$router->get('/search-index', [ $app->physicsController(), 'searchIndex' ]);
	});
	
}, [ SecurityHeadersMiddleware::class ]);