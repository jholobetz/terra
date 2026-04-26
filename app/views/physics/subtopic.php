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

    <?php $this->render('physics/_equations_partial', ['equations' => $equations, 'breakdowns' => $breakdowns, 'nonce' => $nonce]); ?>

    <footer class="subtopic-footer">
        <?php if (!empty($breadcrumbs)): 
            $lastCrumb = end($breadcrumbs);
        ?>
            <a href="<?= htmlspecialchars($lastCrumb['url']) ?>" class="btn btn-secondary">&larr; Back to <?= $lastCrumb['title'] ?></a>
        <?php endif; ?>
    </footer>
</article>