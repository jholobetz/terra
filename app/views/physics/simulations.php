<?php
require_once __DIR__ . '/_topic_icons.php';
?>

<section class="simulations-header" style="margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px;">
    <h1 style="font-size: 2.8rem; margin: 0 0 8px 0; background: linear-gradient(135deg, #ffffff 65%, var(--accent-default)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;"><?= $title ?></h1>
    <p style="color: var(--text-muted); font-size: 1.1rem; margin: 0; max-width: 600px;">Interact with fundamental physical principles through these interactive models.</p>
</section>

<section class="topics-grid">
    <?php foreach ($simulations as $sim): 
        $topicSlug = get_simulation_category($sim['slug']);
        $meta = get_topic_icon_and_class($topicSlug);
    ?>
    <a href="/physics/simulations/<?= htmlspecialchars($sim['slug']) ?>" class="topic-card <?= $meta['class'] ?>">
        <div class="card-watermark">
            <?= $meta['svg'] ?>
        </div>
        <div class="topic-card-header">
            <?= $meta['svg'] ?>
            <h3><?= htmlspecialchars($sim['title']) ?></h3>
        </div>
        <p><?= htmlspecialchars($sim['description']) ?></p>
        <span class="read-more">Launch Simulation &rarr;</span>
    </a>
    <?php endforeach; ?>
</section>
