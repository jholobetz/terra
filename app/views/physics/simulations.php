<section class="simulations-header">
    <h1><?= $title ?></h1>
    <p>Interact with fundamental physical principles through these interactive models.</p>
</section>

<section class="topics-grid">
    <?php foreach ($simulations as $sim): ?>
    <a href="/physics/simulations/<?= htmlspecialchars($sim['slug']) ?>" class="topic-card">
        <h3><?= $sim['title'] ?></h3>
        <p><?= $sim['description'] ?></p>
        <span class="read-more">Launch Simulation &rarr;</span>
    </a>
    <?php endforeach; ?>
</section>
