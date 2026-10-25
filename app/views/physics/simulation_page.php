<article class="simulation-view">
    <header class="simulation-header">
        <h1><?= $title ?></h1>
        <p class="description"><?= $description ?></p>
    </header>

    <div class="simulation-layout">
        <div class="canvas-panel">
            <div id="canvas-container" class="canvas-container">
                <canvas id="simulation-canvas"></canvas>
            </div>
        </div>

        <aside class="controls-panel">
            <h3>Controls</h3>
            <div id="controls" class="controls">
                <!-- Controls will be injected here by simulation script -->
            </div>
            
            <div class="physics-info">
                <h4>The Physics</h4>
                <p><?= $physics ?></p>
                <?php if (!empty($formulas) && is_array($formulas)): ?>
                    <?php $this->render('physics/_equations_partial', ['formulas' => $formulas, 'equations' => $equations ?? [], 'breakdowns' => $breakdowns ?? [], 'nonce' => $nonce]); ?>
                <?php elseif (!empty($equations) && is_array($equations)): ?>
                    <div class="equations">
                        <?php foreach ($equations as $eq): ?>
                            <div class="sim-equation-item" style="margin: 10px 0; padding: 8px 10px; background: rgba(2, 6, 23, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; color: #ffd700; overflow-x: auto;">
                                \[ <?= $eq ?> \]
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
        </aside>
    </div>

    <footer class="simulation-footer">
        <a href="/physics/simulations" class="btn btn-secondary">&larr; Back to Simulations</a>
    </footer>
</article>

<?php
$harnessVer = @filemtime(PROJECT_ROOT . '/public/js/lib/webgl_physics_harness.js') ?: 1;
$simJsVer = @filemtime(PROJECT_ROOT . "/public/js/simulations/{$slug}.js") ?: 1;
?>
<script src="/js/lib/webgl_physics_harness.js?v=<?= $harnessVer ?>" nonce="<?= $nonce ?>"></script>
<script src="/js/simulations/<?= $slug ?>.js?v=<?= $simJsVer ?>" nonce="<?= $nonce ?>"></script>
