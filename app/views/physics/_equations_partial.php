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
                            \[ <?= $f['equation'] ?> \]
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

                        <?php if (!empty($f['semantic_variables'])): ?>
                        <div class="variable-definitions" style="margin-top: 25px; padding-top: 15px; border-top: 1px solid rgba(100, 255, 218, 0.1);">
                            <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase; margin-bottom: 10px;">4. Semantic Variables</h4>
                            <div style="display: flex; flex-wrap: wrap; gap: 15px;">
                                <?php foreach ($f['semantic_variables'] as $symbol => $var): 
                                    $url = '';
                                    if (strpos($var['ref'], 'constants/') === 0) {
                                        $url = '/physics/constants'; // Generic for now, or link to a specific constant anchor
                                    } else if (strpos($var['ref'], 'subtopics/') === 0) {
                                        $url = '/physics/subtopic/' . str_replace('subtopics/', '', $var['ref']);
                                    }
                                ?>
                                    <div class="var-tag" style="background: rgba(100, 255, 218, 0.05); padding: 5px 12px; border-radius: 4px; border: 1px solid rgba(100, 255, 218, 0.2); font-size: 0.85rem;">
                                        <span style="color: var(--accent); font-weight: 700;">\( <?= $symbol ?> \):</span> 
                                        <?php if ($url): ?>
                                            <a href="<?= $url ?>" style="color: #ccd6f6; text-decoration: none; border-bottom: 1px dotted #8892b0;"><?= $var['name'] ?></a>
                                        <?php else: ?>
                                            <span style="color: #ccd6f6;"><?= $var['name'] ?></span>
                                        <?php endif; ?>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                        <?php endif; ?>
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
