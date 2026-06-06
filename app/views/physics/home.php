<?php
require_once __DIR__ . '/_topic_icons.php';
?>

<section class="hero">
    <canvas id="hero-canvas"></canvas>
    <div class="hero-content">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="subtitle"><?= htmlspecialchars($subtitle) ?></p>
        <div class="hero-cta">
            <a href="/physics/topic/classical-mechanics" class="btn btn-primary">Start Exploring</a>
            <a href="/physics/simulations" class="btn btn-secondary">Try Simulations</a>
        </div>
    </div>
</section>



<section class="topics-grid">
    <?php foreach ($topics as $topic): 
        $meta = get_topic_icon_and_class($topic['slug']);
    ?>
        <a href="/physics/topic/<?= htmlspecialchars($topic['slug']) ?>" class="topic-card <?= $meta['class'] ?>">
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
</section>

<!-- Include canvas animation -->
<script src="/js/hero_canvas.js" defer></script>
