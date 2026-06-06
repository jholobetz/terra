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


<!-- Curriculum Dashboard & Sandbox Grid -->
<div class="dashboard-layout">
    <div class="dashboard-main">
        <!-- Tabbed Curriculum Navigation -->
        <div class="tabs-container">
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
    </div>
    
    <div class="dashboard-sidebar">
        <!-- Live Interactive Simulation Sandbox Widget -->
        <div class="sandbox-widget">
            <div class="widget-header">
                <h3>Live Simulation Sandbox</h3>
                <span class="badge">Active</span>
            </div>
            
            <div class="equation-box">
                <div class="equation-render">
                    \[ \theta''(t) + {\color{#ff4e88}\gamma}\theta'(t) + \frac{{\color{#00d2ff}g}}{{\color{#10b981}L}}\sin\theta = 0 \]
                </div>
            </div>
            
            <div class="canvas-wrapper">
                <canvas id="sandbox-canvas"></canvas>
            </div>
            
            <div class="controls-box">
                <div class="control-group">
                    <label for="slider-gravity">Gravity (<span style="color:#00d2ff; font-style: italic; font-family: serif; font-weight: bold;">g</span>): <span id="val-gravity">9.8</span> m/s²</label>
                    <input type="range" id="slider-gravity" min="0" max="25" step="0.1" value="9.8">
                </div>
                <div class="control-group">
                    <label for="slider-length">Length (<span style="color:#10b981; font-style: italic; font-family: serif; font-weight: bold;">L</span>): <span id="val-length">1.5</span> m</label>
                    <input type="range" id="slider-length" min="0.5" max="3.0" step="0.1" value="1.5">
                </div>
                <div class="control-group">
                    <label for="slider-damping">Damping (<span style="color:#ff4e88; font-style: italic; font-family: serif; font-weight: bold;">&gamma;</span>): <span id="val-damping">0.10</span></label>
                    <input type="range" id="slider-damping" min="0" max="0.5" step="0.01" value="0.10">
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Scripts -->
<script src="/js/hero_canvas.js" defer></script>
<script src="/js/home_sandbox.js" defer></script>
