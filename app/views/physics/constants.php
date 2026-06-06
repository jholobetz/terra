<article class="physics-page" style="--accent-color: var(--accent-default);">
    <header class="page-header">
        <span class="category-tag">Fundamental Reference</span>
        <h1>Fundamental Physical Constants</h1>
        <p class="lead-prose">
            The precise values that govern the behavior of the physical universe, from the scale of the vacuum to the macroscopic limits of relativity and quantum mechanics.
        </p>
    </header>

    <div class="constants-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px; margin-top: 40px;">
        <?php foreach ($constants as $slug => $c): ?>
            <section class="constant-card" id="<?= $slug ?>" style="background: #112240; border: 1px solid #233554; border-radius: 12px; padding: 25px; transition: transform 0.3s ease;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px;">
                    <h3 style="margin: 0; font-size: 1.2rem; color: var(--accent-color);"><?= $c['name'] ?></h3>
                    <span style="background: rgba(100, 255, 218, 0.1); color: var(--accent-color); padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 1.1rem; display: inline-block;">
                        \( <?= $c['symbol'] ?> \)
                    </span>
                </div>
                
                <div class="constant-value" style="margin-bottom: 20px;">
                    <span style="font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: #fff; display: block; word-break: break-all;">
                        <?= $c['value'] ?> <span style="font-size: 0.9rem; color: #8892b0;"><?= $c['unit'] ?></span>
                    </span>
                </div>

                <p style="margin: 0; font-size: 0.95rem; color: #ccd6f6; line-height: 1.5;">
                    <?= $c['description'] ?>
                </p>
            </section>
        <?php endforeach; ?>
    </div>

    <footer style="margin-top: 60px; padding-top: 30px; border-top: 1px solid #233554; text-align: center;">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Lab Home</a>
    </footer>
</article>

<style>
    .constant-card:hover {
        transform: translateY(-5px);
        border-color: var(--accent-color);
    }
    .constant-card:target {
        border-color: var(--accent-color);
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.15);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { border-color: #233554; }
        50% { border-color: var(--accent-color); }
        100% { border-color: #233554; }
    }
</style>

