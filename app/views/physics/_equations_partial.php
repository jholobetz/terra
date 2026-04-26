<?php
/**
 * Equations Partial
 * Supports both new 'formulas' object structure and legacy 'equations'/'breakdowns' maps.
 */
$hasFormulas = !empty($formulas) && is_array($formulas);
$hasLegacy = !empty($equations) && is_array($equations);

if ($hasFormulas || $hasLegacy): ?>
<section class="equations-section">
    <h2>Key Equations</h2>
    <p class="instruction">Click a formula to see its breakdown.</p>
    <ul class="equations-list" id="equations-list">
        <?php if ($hasFormulas): ?>
            <?php foreach ($formulas as $f): ?>
                <li class="equation-item" style="list-style: none;">
                    <div class="equation-container">
                        <?php if (!empty($f['title'])): ?>
                            <span class="formula-title"><?= $f['title'] ?></span>
                        <?php endif; ?>
                        <span class="equation">\[ <?= htmlspecialchars($f['equation']) ?> \]</span>
                        <?php if (!empty($f['breakdown'])): ?>
                        <div class="breakdown" style="display: none;">
                            <?= $f['breakdown'] ?>
                        </div>
                        <?php endif; ?>
                    </div>
                </li>
            <?php endforeach; ?>
        <?php else: ?>
            <?php foreach ($equations as $eq): ?>
                <li class="equation-item" style="list-style: none;">
                    <div class="equation-container">
                        <span class="equation">\[ <?= htmlspecialchars($eq) ?> \]</span>
                        <?php if (isset($breakdowns) && is_array($breakdowns) && isset($breakdowns[$eq])): ?>
                        <div class="breakdown" style="display: none;">
                            <?= $breakdowns[$eq] ?>
                        </div>
                        <?php endif; ?>
                    </div>
                </li>
            <?php endforeach; ?>
        <?php endif; ?>
    </ul>
</section>
<?php endif; ?>

<script nonce="<?= $nonce ?? '' ?>">
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
            
            if (!isVisible && typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                MathJax.typesetPromise([breakdown]);
            }
        }
    });
});
</script>
<style>
.formula-title { display: block; margin-bottom: 5px; color: var(--accent); font-size: 1em; font-weight: 600; }
.equation-container { border: 1px solid rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; margin-bottom: 10px; transition: background 0.2s; }
.equation-container:hover { background: rgba(255,255,255,0.05); }
.equation-container.active { border-color: var(--accent); }
</style>
