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
                <?php $this->render('physics/_equations_partial', ['equations' => $equations, 'breakdowns' => $breakdowns ?? [], 'nonce' => $nonce]); ?>
            </div>
        </aside>
    </div>

    <footer class="simulation-footer">
        <a href="/physics/simulations" class="btn btn-secondary">&larr; Back to Simulations</a>
    </footer>
</article>

<script src="/js/simulations/<?= $slug ?>.js" nonce="<?= $nonce ?>"></script>
