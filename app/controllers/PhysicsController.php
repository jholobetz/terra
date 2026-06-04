<?php

namespace app\controllers;

use flight\Engine;

class PhysicsController
{
    protected Engine $app;

    public function __construct(Engine $app)
    {
        $this->app = $app;
    }

    /**
     * Resolves the decoupled PhysicsService container instance.
     */
    private function service()
    {
        return $this->app->physicsService();
    }

    /**
     * Public database index synchronization endpoint.
     */
    public function sync(): void
    {
        $this->service()->performSync();
        $syncLock = PROJECT_ROOT . '/app/config/.last_sync';
        touch($syncLock);
        $this->app->redirect($this->app->request()->referrer ?: '/physics');
    }

    /**
     * Public JSON endpoint serving the search index.
     */
    public function searchIndex(): void
    {
        $path = PROJECT_ROOT . '/app/config/content/search_index.json';
        if (file_exists($path)) {
            $this->app->json(json_decode(file_get_contents($path), true));
        } else {
            $this->app->json([]);
        }
    }

    /**
     * View action rendering physical constants.
     */
    public function constants()
    {
        $content = $this->service()->getPhysicsContent();
        $constants = $content['constants'] ?? [];
        
        $this->renderWithLayout('physics/constants', [
            'title' => 'Fundamental Physical Constants',
            'constants' => $constants
        ]);
    }

    /**
     * View action rendering interactive simulations list.
     */
    public function simulations()
    {
        $sims = $this->service()->fetchAllData('simulations');
        $this->renderWithLayout('physics/simulations', [
            'title' => 'Interactive Simulations',
            'simulations' => $sims,
        ]);
    }

    /**
     * View action rendering an individual simulation sandbox page.
     */
    public function viewSimulation(string $slug)
    {
        $data = $this->service()->fetchAndPrepare('simulations', $slug);
        if (!$data) {
            $this->app->notFound();
            return;
        }
        $this->renderWithLayout('physics/simulation_page', array_merge($data, [
            'physics' => $data['physics'] ?? $data['description'] ?? '',
        ]));
    }

    /**
     * View action rendering a comprehensive Topic Hub.
     */
    public function viewTopic(string $slug)
    {
        $cachePath = PROJECT_ROOT . "/public/cache/topic/{$slug}.html";
        $isStale = $this->isHubCacheStale($slug, $cachePath);

        // Auto-sync stale hub manifests
        if ($isStale || $this->service()->isPreviewActive()) {
            $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
            if (file_exists($manifestPath)) {
                $manifestData = json_decode(file_get_contents($manifestPath), true);
                if ($manifestData) {
                    $this->service()->syncIndividualTopic($slug, $manifestData);
                }
            }
        }

        if (file_exists($cachePath) && !$isStale && !$this->service()->isPreviewActive()) {
            header('Content-Type: text/html; charset=utf-8');
            readfile($cachePath);
            return;
        }

        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $this->service()->loadAllShards();
        $topic = $this->service()->fetchAndPrepare('topics', $slug);
        if (empty($topic)) {
            $this->app->notFound();
            return;
        }

        $content = $this->service()->getPhysicsContent();
        
        // Construct subtopics lookup map for subtopic card details
        $subtopicsMap = [];
        foreach ($content['subtopics'] as $subSlug => $sub) {
            if (!is_array($sub)) continue;
            $subtopicsMap[$subSlug] = [
                'title' => $sub['title'] ?? $subSlug,
                'snippet' => $sub['snippet'] ?? '',
                'snippet_svg' => $sub['snippet_svg'] ?? '',
                'hero_math' => $sub['hero_math'] ?? ''
            ];
        }

        // Map cross-pillar bridge links
        $resolvedBridges = [];
        $topicBridges = !empty($topic['bridges']) ? (is_string($topic['bridges']) ? json_decode($topic['bridges'], true) : $topic['bridges']) : [];
        foreach ($topicBridges as $bridgeKey => $desc) {
            if (isset($content['topics'][$bridgeKey])) {
                $resolvedBridges[] = [
                    'title' => $content['topics'][$bridgeKey]['title'],
                    'slug' => $bridgeKey,
                    'description' => $desc
                ];
            } else {
                $resolvedBridges[] = [
                    'title' => $bridgeKey,
                    'slug' => null,
                    'description' => $desc
                ];
            }
        }

        $this->renderWithLayout('physics/topic', array_merge($topic, [
            'topic' => $topic,
            'subtopics_map' => $subtopicsMap,
            'pillars' => !empty($topic['pillars']) ? (is_string($topic['pillars']) ? json_decode($topic['pillars'], true) : $topic['pillars']) : null,
            'bridges' => $resolvedBridges,
            'intro' => $topic['intro'] ?? null,
            'field' => $topic['field'] ?? null,
            'density' => $topic['density'] ?? null,
            'slug' => $slug
        ]), $cachePath);
    }

    /**
     * View action rendering a highly dense Platinum mathematical subtopic.
     */
    public function viewSubtopic(string $slug)
    {
        $cachePath = PROJECT_ROOT . "/public/cache/subtopic/{$slug}.html";
        $isStale = $this->isCacheStale($slug, $cachePath);

        if (file_exists($cachePath) && !$isStale && !$this->service()->isPreviewActive()) {
            header('Content-Type: text/html; charset=utf-8');
            readfile($cachePath);
            return;
        }

        if ($isStale && file_exists($cachePath)) {
            unlink($cachePath);
        }

        $subtopic = $this->service()->fetchAndPrepare('subtopics', $slug);
        if (empty($subtopic)) {
            $this->app->notFound();
            return;
        }

        $breadcrumbs = $this->service()->resolveBreadcrumbs(!empty($subtopic['parents']) ? (array)$subtopic['parents'] : []);
        $related = $this->service()->getRelatedTopics($slug);

        $this->renderWithLayout('physics/subtopic', array_merge($subtopic, [
            'breadcrumbs' => $breadcrumbs,
            'related_topics' => $related,
            'title' => $subtopic['title'],
            'content' => $subtopic['content'],
            'equations' => $subtopic['equations'] ?? [],
            'breakdowns' => $subtopic['breakdowns'] ?? [],
            'formulas' => $subtopic['formulas'] ?? []
        ]), $cachePath);
    }

    /**
     * Render action embedding pages into standard HTML bootstrap templates.
     */
    protected function renderWithLayout(string $view, array $data = [], ?string $cachePath = null): void
    {
        $isPreview = $this->service()->isPreviewActive();
        $isBuildMode = ($this->app->request()->query->build_mode === '1');

        if ($isPreview) {
            $this->service()->loadAllShards();
            $content = $this->service()->getPhysicsContent();
            
            $topicsList = array_map(function($s, $t) {
                $isDraft = ($t['status'] ?? '') === 'draft';
                $title = $isDraft ? '<span class="draft-badge">DRAFT</span> ' . $t['title'] : $t['title'];
                return ['slug' => $s, 'title' => $title];
            }, array_keys($content['topics']), $content['topics']);
            
            $simsList = array_map(function($s, $t) {
                $isDraft = ($t['status'] ?? '') === 'draft';
                $title = $isDraft ? '<span class="draft-badge">DRAFT</span> ' . $t['title'] : $t['title'];
                return ['slug' => $s, 'title' => $title];
            }, array_keys($content['simulations']), $content['simulations']);
        } else {
            $topicsList = $this->app->db()->fetchAll("SELECT slug, title FROM topics ORDER BY id ASC");
            $simsList = $this->app->db()->fetchAll("SELECT slug, title FROM simulations ORDER BY id ASC");
        }

        $menuTopics = [];
        foreach ($topicsList as $topic) {
            $menuTopics[$topic['slug']] = ['title' => $topic['title']];
        }

        $menuSimulations = [];
        foreach ($simsList as $sim) {
            $menuSimulations[$sim['slug']] = ['title' => $sim['title']];
        }

        $nonce = $this->app->get('csp_nonce') ?? '';
        $viewData = array_merge($data, ['nonce' => $nonce]);
        $bodyContent = $this->app->view()->fetch($view, $viewData) ?: '';

        if ($isPreview && !$isBuildMode) {
            $bodyContent .= '
                <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
                    <a href="/physics/sync" class="btn btn-primary" style="box-shadow: 0 4px 12px rgba(0,0,0,0.3); border-radius: 50px; padding: 12px 24px; text-decoration: none; display: flex; align-items: center; gap: 8px; background-color: #007bff; color: white; border: none; font-family: sans-serif;">
                        <span>🔄</span> <strong>Sync Now</strong>
                    </a>
                </div>';
        }

        $html = $this->app->view()->fetch('physics/layout', array_merge($viewData, [
            'body_content' => $bodyContent,
            'is_preview' => $isPreview && !$isBuildMode,
            'nonce' => $nonce,
            'menu_topics' => $menuTopics,
            'menu_simulations' => $menuSimulations,
        ])) ?: '';

        if ($cachePath && !$isPreview && !$isBuildMode) {
            $dir = dirname($cachePath);
            if (!file_exists($dir)) {
                mkdir($dir, 0777, true);
            }
            file_put_contents($cachePath, $html);
        }

        echo $html;
    }

    /**
     * Homepage view action.
     */
    public function index()
    {
        $topics = $this->service()->fetchAllData('topics');
        foreach ($topics as &$topic) {
            $cleanContent = strip_tags($topic['content'] ?? $topic['intro'] ?? '');
            $topic['description'] = mb_strimwidth($cleanContent, 0, 120, "...");
        }

        $this->renderWithLayout('physics/home', [
            'title' => 'The Physics Lab',
            'subtitle' => 'Explore the fundamental laws of the universe through interactive simulations and detailed explanations.',
            'topics' => $topics
        ]);
    }

    private function isHubCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;
        $manifestPath = PROJECT_ROOT . "/hub_manifests/{$slug}.json";
        if (!file_exists($manifestPath)) return false;
        return filemtime($manifestPath) > filemtime($cachePath);
    }

    private function isCacheStale(string $slug, string $cachePath): bool
    {
        if (!file_exists($cachePath)) return true;
        $content = $this->service()->getPhysicsContent($slug);
        $shardFile = $content['search_index'][$slug]['s'] ?? null;
        if (!$shardFile) return false;

        $shardPath = PROJECT_ROOT . '/app/config/content/' . $shardFile;
        if (!file_exists($shardPath)) return false;

        return filemtime($shardPath) > filemtime($cachePath);
    }
}
