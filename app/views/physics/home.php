<?php
require_once __DIR__ . '/_topic_icons.php';
?>

<section class="hero">
    <canvas id="hero-canvas"></canvas>
    <div class="hero-content">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="subtitle"><?= htmlspecialchars($subtitle) ?></p>
        <div class="hero-cta">
            <a href="/physics/topic/classical-mechanics" class="btn btn-secondary">Start Exploring</a>
            <a href="/physics/simulations" class="btn btn-primary">Try Simulations</a>
        </div>
    </div>
</section>

<!-- Tabbed Curriculum Navigation -->
<div class="tabs-container" style="margin-top: 40px; margin-bottom: 25px;">
    <button class="tab-btn active" data-domain="all">All Disciplines</button>
    <button class="tab-btn" data-domain="classical">Macroscopic &amp; Classical</button>
    <button class="tab-btn" data-domain="fields">Fields &amp; Covariant</button>
    <button class="tab-btn" data-domain="quantum">Quantum &amp; High-Energy</button>
    <button class="tab-btn" data-domain="space">Space &amp; Cosmology</button>
</div>

<div class="topics-grid">
    <?php foreach ($topics as $topic): 
        $meta = get_topic_icon_and_class($topic['slug']);
        
        // Map slug to domain group
        $domain = 'classical';
        $slug = $topic['slug'];
        if (in_array($slug, ['classical-mechanics', 'thermodynamics-statistical-mechanics', 'fluids-nonlinear'])) {
            $domain = 'classical';
        } elseif (in_array($slug, ['electromagnetism', 'relativity', 'theoretical-physics', 'mathematical-methods'])) {
            $domain = 'fields';
        } elseif (in_array($slug, ['quantum-physics', 'standard-model', 'condensed-matter', 'philosophy-of-physics'])) {
            $domain = 'quantum';
        } elseif ($slug === 'astrophysics') {
            $domain = 'space';
        }
    ?>
        <a href="/physics/topic/<?= htmlspecialchars($topic['slug']) ?>" class="topic-card <?= $meta['class'] ?>" data-domain="<?= $domain ?>">
            <div class="card-watermark">
                <?= $meta['svg'] ?>
            </div>
            <div class="topic-card-header">
                <?= $meta['svg'] ?>
                <h3><?= $topic['title'] ?></h3>
            </div>
            <p><?= htmlspecialchars($topic['description']) ?></p>
            <span class="read-more">Explore Hub &rarr;</span>
        </a>
    <?php endforeach; ?>
</div>

<!-- Scripts -->
<script src="/js/hero_canvas.js" defer></script>
<script src="/js/home_sandbox.js" defer></script>
