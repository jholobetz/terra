<?php
/**
 * Equations Partial - Platinum Standard (Stable Expansion Version)
 */
$hasFormulas = !empty($formulas) && is_array($formulas);

if ($hasFormulas): ?>
<section class="equations-section">
    <h2>Key Theoretical Identities</h2>
    <p class="instruction">Interact with identities to explore their semantic depth.</p>
    <ul class="equations-list" id="equations-list">
        <?php foreach ($formulas as $f): ?>
            <li class="equation-item" style="list-style: none; margin-bottom: 25px;">
                <div class="platinum-formula-card" 
                     style="border: 1px solid #233554; border-radius: 12px; background: #112240; overflow: hidden; transition: all 0.3s ease;">
                    
                    <div class="formula-expand-trigger" style="padding: 15px 20px; background: rgba(100, 255, 218, 0.05); border-bottom: 1px solid #233554; cursor: pointer; display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--accent); font-weight: 700; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;">
                            <?= $f['title'] ?>
                        </span>
                        <span class="expand-icon" style="font-size: 0.7rem; opacity: 0.5;">[ Click to Expand Depth ]</span>
                    </div>

                    <div class="formula-math-display" style="padding: 30px 20px; text-align: center; background: #112240;">
                        <div class="math-content" style="font-size: 1.4rem; color: #fff;">
                            \[ <?= htmlspecialchars($f['equation']) ?> \]
                        </div>
                    </div>

                    <div class="formula-body" style="display: none; padding: 20px; background: #0a192f; border-top: 1px solid #233554;">
                        <div class="platinum-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">1. Physical Interpretation</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5;">
                                    <?= $f['interpretation'] ?? 'Awaiting derivation.' ?>
                                </p>
                            </div>
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">2. Symmetry & Origin</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5; color: #8892b0;">
                                    <?= $f['symmetry_origin'] ?? 'Analysis pending.' ?>
                                </p>
                            </div>
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">3. Limits & Boundary</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5; color: #8892b0;">
                                    <?= $f['limits_and_boundary'] ?? 'Case analysis pending.' ?>
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </li>
        <?php endforeach; ?>
    </ul>
</section>
<?php endif; ?>

<script nonce="<?= $nonce ?? '' ?>">
document.addEventListener('DOMContentLoaded', function() {
    const list = document.getElementById('equations-list');
    if (!list) return;

    list.addEventListener('click', function(event) {
        const trigger = event.target.closest('.formula-expand-trigger');
        if (!trigger) return;
        const card = trigger.closest('.platinum-formula-card');
        const body = card.querySelector('.formula-body');
        const icon = trigger.querySelector('.expand-icon');
        if (body) {
            const isHidden = window.getComputedStyle(body).display === 'none';
            if (isHidden) {
                body.style.display = 'block';
                card.style.borderColor = 'var(--accent)';
                icon.innerText = '[ Click to Collapse ]';
                if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) MathJax.typesetPromise([body]);
            } else {
                body.style.display = 'none';
                card.style.borderColor = '#233554';
                icon.innerText = '[ Click to Expand Depth ]';
            }
        }
    });
});
</script>
