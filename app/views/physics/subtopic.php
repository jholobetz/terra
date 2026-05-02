<article class="subtopic-content">
    <nav class="breadcrumb">
        <a href="/physics">Home</a>
        <?php foreach ($breadcrumbs as $crumb): ?>
            <span>&rsaquo;</span>
            <a href="<?= htmlspecialchars($crumb['url']) ?>"><?= $crumb['title'] ?></a>
        <?php endforeach; ?>
        <span>&rsaquo;</span>
        <span style="opacity: 1; color: #8892b0;"><?= $title ?></span>
    </nav>

    <header class="subtopic-header">
        <h1><?= $title ?? 'Subtopic' ?></h1>
    </header>
    
    <div class="content-body">
        <?= $content ?? '<p>No content available for this subtopic.</p>' ?>
    </div>

    <?php $this->render('physics/_equations_partial', ['equations' => $equations ?? [], 'breakdowns' => $breakdowns ?? [], 'formulas' => $formulas ?? [], 'nonce' => $nonce]); ?>

    <?php if (!empty($related_topics)): ?>
        <section class="related-topics" style="margin-top: 50px; padding-top: 30px; border-top: 1px solid #233554;">
            <h3 style="color: #ccd6f6; margin-bottom: 20px;">Further Exploration</h3>
            <div class="related-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <?php foreach ($related_topics as $rel): ?>
                    <a href="/physics/subtopic/<?= $rel['slug'] ?>" class="related-card" style="background: #112240; padding: 20px; border-radius: 8px; text-decoration: none; border: 1px solid #233554; transition: all 0.3s ease; display: block;">
                        <strong style="color: var(--accent); display: block; margin-bottom: 5px;"><?= $rel['title'] ?></strong>
                        <span style="font-size: 0.85rem; color: #8892b0;">Dive deeper into the related theoretical framework.</span>
                    </a>
                <?php endforeach; ?>
            </div>
        </section>
    <?php endif; ?>

    <footer class="subtopic-footer" style="margin-top: 40px;">
        <?php if (!empty($breadcrumbs)): 
            $lastCrumb = end($breadcrumbs);
        ?>
            <a href="<?= htmlspecialchars($lastCrumb['url']) ?>" class="btn btn-secondary">&larr; Back to <?= $lastCrumb['title'] ?></a>
        <?php endif; ?>
    </footer>
</article>
