<?php
/**
 * Platinum Standard Topic Hub - Unified Dynamic View
 * Option A: Pre-calculated Math-Free Snippets for Maximum Stability
 */

// Determine Level based on technical markers
if (!function_exists('getConceptLevel')) {
    function getConceptLevel($slug, $title) {
        $foundational = ['newton', 'law', 'galileo', 'vector', 'static', 'force', 'energy', 'work', 'torque', 'inertia'];
        $frontier = ['manifold', 'topology', 'tensor', 'bundle', 'chaos', 'nonlinear', 'covariant', 'lie', 'symplectic', 'geodesic', 'action'];
        
        $t = strtolower($title . ' ' . $slug);
        foreach ($frontier as $term) if (strpos($t, $term) !== false) return 'Frontier';
        foreach ($foundational as $term) if (strpos($t, $term) !== false) return 'Foundational';
        return 'Analytical';
    }
}
?>

<style>
    /* Hub-Specific Layout Overrides */
    .concept-card {
        min-width: 0 !important;
        overflow: visible !important;
    }
    .math-content {
        overflow-x: auto;
        max-width: 100%;
    }
</style>

<article class="topic-content">
    <header class="topic-header">
        <h1><?= $title ?? 'Physics Hub' ?></h1>
    </header>
    
    <div class="content-body">
        <?php if (!empty($pillars) && is_array($pillars)): ?>
            <!-- DATA-DRIVEN PLATINUM HUB -->
            <p><?= $intro ?? 'Accessing the deep mathematical structure of the physical manifold.' ?></p>

            <div class="high-signal-banner">
                <div class="signal-item"><strong>Field:</strong> <?= $field ?? $title ?></div>
                <div class="signal-item"><strong>Standard:</strong> Platinum</div>
                <div class="signal-item"><strong>Technical Density:</strong> <?= $density ?? '185' ?></div>
                <div class="signal-item"><strong>Bridges:</strong> <?= !empty($bridges) ? count($bridges) : '0' ?></div>
            </div>

            <?php foreach ($pillars as $pillar): ?>
                <section class="concept-pillar">
                    <h3 class="pillar-header"><?= $pillar['title'] ?></h3>
                    <p class="pillar-narrative"><?= $pillar['narrative'] ?></p>
                    <div class="concept-grid">
                        <?php foreach ($pillar['slugs'] as $slug): 
                            $sub = $subtopics_map[$slug] ?? null;
                            if (!$sub) continue;
                            $level = getConceptLevel($slug, $sub['title']);
                        ?>
                            <div class="concept-card">
                                <div class="concept-anchor">
                                    <span class="level-tag level-<?= strtolower($level) ?>"><?= $level ?></span>
                                    <h4><strong><a href="/physics/subtopic/<?= $slug ?>" class="subtopic-link"><?= str_replace('\\\\', '\\', $sub['title']) ?></a></strong></h4>
                                </div>
                                
                                <?php if (!empty($sub['hero_math'])): ?>
                                    <div class="hero-math-badge" style="margin: 15px 0; padding: 10px; background: rgba(0,0,0,0.2); border-radius: 4px; text-align: center;">
                                        <?= $sub['hero_math'] ?>
                                    </div>
                                <?php endif; ?>

                                <div class="concept-detail">
                                    <p><?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?></p>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </section>
            <?php endforeach; ?>

            <?php if (!empty($bridges)): ?>
                <div class="bridge-matrix">
                    <h3>Cross-Disciplinary Bridges</h3>
                    <?php foreach ($bridges as $b): ?>
                        <div class="bridge-item">
                            <strong>
                                <?php if (!empty($b['slug'])): ?>
                                    <a href="/physics/topic/<?= $b['slug'] ?>" class="topic-link"><?= $b['title'] ?></a>
                                <?php else: ?>
                                    <?= $b['title'] ?>
                                <?php endif; ?>:
                            </strong>
                            <p><?= $b['description'] ?></p>
                        </div>
                    <?php endforeach; ?>
                </div>
            <?php endif; ?>

        <?php else: ?>
            <!-- FALLBACK: CLASSIC STATIC CONTENT -->
            <?= $content ?? '<p>No content available for this topic.</p>' ?>
        <?php endif; ?>
    </div>

    <?php $this->render('physics/_equations_partial', ['equations' => $equations ?? [], 'breakdowns' => $breakdowns ?? [], 'formulas' => $formulas ?? [], 'nonce' => $nonce]); ?>

    <footer class="topic-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Home</a>
    </footer>
</article>
