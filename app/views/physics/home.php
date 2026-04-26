<section class="hero">
    <h1><?= $title ?></h1>
    <p class="subtitle"><?= $subtitle ?></p>
    <div class="hero-cta">
        <a href="/physics/topic/classical-mechanics" class="btn btn-primary">Start Exploring</a>
        <a href="/physics/simulations" class="btn btn-secondary">Try Simulations</a>
    </div>
</section>

<section class="topics-grid">
    <?php foreach ($topics as $topic): ?>
        <a href="/physics/topic/<?= htmlspecialchars($topic['slug']) ?>" class="topic-card">
            <h3><?= $topic['title'] ?></h3>
            <p><?= htmlspecialchars($topic['description']) ?></p>
            <span class="read-more">Learn more &rarr;</span>
        </a>
    <?php endforeach; ?>
</section>
