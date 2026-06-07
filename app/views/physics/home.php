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
            <a href="/physics/simulations" class="btn btn-primary">Lab Tools</a>
        </div>
    </div>
</section>

<!-- Curriculum Dashboard & Sandbox Grid -->
<div class="dashboard-layout">
    <div class="dashboard-main">
        <!-- Tabbed Curriculum Navigation -->
        <div class="tabs-container" style="margin-top: 0; margin-bottom: 25px;">
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
                <div class="equation-render" style="font-size: 0.85rem; line-height: 1.4;">
                    \[ \mathbf{a} = -g\hat{j} - \class{math-color-current}{C_d} v \mathbf{v} \]
                    \[ \mathbf{v}_0 = \class{math-color-mass}{v_0}(\cos\class{math-color-length}{\theta}\hat{i} + \sin\class{math-color-length}{\theta}\hat{j}) \]
                </div>
            </div>
            
            <div class="canvas-wrapper">
                <canvas id="sandbox-canvas"></canvas>
            </div>
            
            <div class="controls-box">
                <div class="control-group">
                    <label for="slider-velocity">Velocity (<span class="math-color-mass" style="font-style: italic; font-family: serif; font-weight: bold;">v<sub>0</sub></span>): <span id="val-velocity">55</span> m/s</label>
                    <input type="range" id="slider-velocity" min="15" max="100" step="1" value="55">
                </div>
                <div class="control-group">
                    <label for="slider-angle">Angle (<span class="math-color-length" style="font-style: italic; font-family: serif; font-weight: bold;">&theta;</span>): <span id="val-angle">45</span>&deg;</label>
                    <input type="range" id="slider-angle" min="0" max="90" step="1" value="45">
                </div>
                <div class="control-group">
                    <label for="slider-drag">Drag (<span class="math-color-current" style="font-style: italic; font-family: serif; font-weight: bold;">C<sub>d</sub></span>): <span id="val-drag">0.02</span></label>
                    <input type="range" id="slider-drag" min="0.00" max="0.10" step="0.005" value="0.02">
                </div>
                <div style="display: flex; gap: 10px; margin-top: 5px;">
                    <button id="launch-btn" class="btn btn-primary" style="flex: 1; font-size: 0.8rem; padding: 8px;">Fire Cannon!</button>
                    <button id="clear-btn" class="btn btn-secondary" style="font-size: 0.8rem; padding: 8px;">Clear</button>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Scripts -->
<script src="/js/hero_canvas.js" defer></script>
<script src="/js/home_sandbox.js" defer></script>
