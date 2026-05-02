<article class="topic-content">
    <header class="topic-header">
        <h1><?= $title ?? 'Physics Topic' ?></h1>
    </header>
    
    <div class="content-body">
        <?= $content ?? '<p>No content available for this topic.</p>' ?>
    </div>

    <?php $this->render('physics/_equations_partial', ['equations' => $equations ?? [], 'breakdowns' => $breakdowns ?? [], 'formulas' => $formulas ?? [], 'nonce' => $nonce]); ?>

    <footer class="topic-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Home</a>
    </footer>
</article>
