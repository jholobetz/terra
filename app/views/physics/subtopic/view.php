<article class="topic-content">

    <?php if (!empty($parent_topic)): ?>
    <div class="breadcrumb">
        <a href="/physics">Home</a> &nbsp;&raquo;&nbsp; 
        <a href="/physics/topic/<?= $parent_topic['slug'] ?>"><?= $parent_topic['title'] ?></a> &nbsp;&raquo;&nbsp; 
        <span><?= $title ?></span>
    </div>
    <?php endif; ?>

    <header class="topic-header">
        <h1><?= $title ?></h1>
    </header>
    
    <div class="content-body">
        <?= $content ?>
    </div>

    <?php if (!empty($equations)): ?>
    <section class="equations-section">
        <h2>Key Equations</h2>
        <p class="instruction">Click a formula to see its breakdown.</p>
        <ul class="equations-list" id="equations-list">
            <?php foreach ($equations as $eq): ?>
                <li class="equation-item">
                    <div class="equation-container">
                        <span class="equation">\[ <?= $eq ?> \]</span>
                        <?php if (isset($breakdowns[$eq])): ?>
                        <div class="breakdown" style="display: none;">
                            <?= $breakdowns[$eq] ?>
                        </div>
                        <?php endif; ?>
                    </div>
                </li>
            <?php endforeach; ?>
        </ul>
    </section>
    <?php endif; ?>

    <script nonce="<?= $nonce ?>">
    document.addEventListener('DOMContentLoaded', function() {
        const list = document.getElementById('equations-list');
        if (!list) return;

        list.addEventListener('click', function(event) {
            const container = event.target.closest('.equation-container');
            if (!container) return;

            const breakdown = container.querySelector('.breakdown');
            if (breakdown) {
                const isVisible = breakdown.style.display === 'block';
                breakdown.style.display = isVisible ? 'none' : 'block';
                container.classList.toggle('active', !isVisible);
                
                // Re-render MathJax if content was just shown
                if (!isVisible && window.MathJax) {
                    MathJax.typesetPromise([breakdown]);
                }
            }
        });
    });
    </script>

    <footer class="topic-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Home</a>
    </footer>
</article>