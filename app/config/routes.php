<?php

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

	$router->group('/physics', function() use ($router, $app) {
		$router->get('/', [ $app->physicsController(), 'index' ]);
		$router->get('/random', [ $app->physicsController(), 'randomSubtopic' ]);
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
		$router->get('/equation-explainer', [ $app->physicsController(), 'equationExplainer' ]);
		$router->get('/api/explain', [ $app->physicsController(), 'apiExplain' ]);
		$router->post('/api/cas-evaluate', [ $app->physicsController(), 'apiCasEvaluate' ]);
		$router->get('/api/cas-evaluate', [ $app->physicsController(), 'apiCasEvaluate' ]);
		$router->post('/api/define-formula', [ $app->physicsController(), 'apiDefineFormula' ]);
		$router->get('/api/subtopic-variables/@slug', [ $app->physicsController(), 'apiGetSubtopicVariables' ]);
		$router->get('/api/search', [ $app->physicsController(), 'apiSearch' ]);
		$router->get('/api/semantic-search', [ $app->physicsController(), 'apiSemanticSearch' ]);
		$router->get('/api/related-subtopics/@slug', [ $app->physicsController(), 'apiRelatedSubtopics' ]);
		$router->get('/api/formula-graph/@id', [ $app->physicsController(), 'apiFormulaGraph' ]);
		$router->get('/api/formula-path', [ $app->physicsController(), 'apiFormulaPath' ]);
		$router->get('/universe-graph', [ $app->physicsController(), 'universeGraph' ]);
		$router->get('/search-index', [ $app->physicsController(), 'searchIndex' ]);

		// Multi-Tier Auth & Formula Review API Routes
		$router->get('/api/auth/me', [ $app->reviewController(), 'apiGetCurrentUser' ]);
		$router->post('/api/auth/switch-role', [ $app->reviewController(), 'apiSwitchDevRole' ]);
		$router->post('/api/suggest-repair', [ $app->reviewController(), 'apiSuggestRepair' ]);
		$router->post('/api/apply-repair', [ $app->reviewController(), 'apiApplyRepair' ]);
		$router->get('/api/reviews', [ $app->reviewController(), 'apiGetReviews' ]);
		$router->post('/api/reviews/approve', [ $app->reviewController(), 'apiApproveReview' ]);
		$router->post('/api/reviews/reject', [ $app->reviewController(), 'apiRejectReview' ]);

		// Admin & Developer Control Panel Routes
		$router->get('/admin', [ $app->adminController(), 'adminAssess' ]);
		$router->get('/admin/assess', [ $app->adminController(), 'adminAssess' ]);
		$router->get('/admin/dashboard', [ $app->adminController(), 'adminAssess' ]);
		$router->get('/admin/editor', [ $app->adminController(), 'wysiwygEditor' ]);
		$router->get('/admin/critic', [ $app->adminController(), 'criticPortal' ]);
		$router->get('/admin/api/assess-telemetry', [ $app->adminController(), 'apiAssessTelemetry' ]);
		$router->post('/admin/api/run-assess', [ $app->adminController(), 'apiRunAssess' ]);
		$router->get('/admin/api/assess-diff', [ $app->adminController(), 'apiAssessDiff' ]);
		$router->post('/admin/api/run-autolinker', [ $app->adminController(), 'apiRunAutoLinker' ]);
		$router->post('/admin/api/run-critic', [ $app->adminController(), 'apiRunCritic' ]);
		$router->post('/admin/api/register-reference', [ $app->adminController(), 'apiRegisterReference' ]);
		$router->post('/admin/api/update-verification', [ $app->adminController(), 'apiUpdateVerification' ]);
		$router->post('/admin/api/save-draft', [ $app->adminController(), 'apiSaveDraft' ]);
		$router->get('/admin/api/get-subtopic/@slug', [ $app->adminController(), 'apiGetSubtopic' ]);
	});
	
}, [ SecurityHeadersMiddleware::class ]);