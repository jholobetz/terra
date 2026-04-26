<?php
/**
 * Equations Partial - Platinum Standard
 * Supports structured formula registry data with semantic variables and deep depth.
 */
$hasFormulas = !empty($formulas) && is_array($formulas);

if ($hasFormulas): ?>
<section class="equations-section">
    <h2>Key Theoretical Identities</h2>
    <p class="instruction">Interact with identities to explore their semantic depth.</p>
    <ul class="equations-list" id="equations-list">
        <?php foreach ($formulas as $f): ?>
            <li class="equation-item" style="list-style: none; margin-bottom: 25px;">
                <div class="platinum-formula-card" style="border: 1px solid #233554; border-radius: 12px; background: #112240; overflow: hidden; transition: all 0.3s ease;">
                    
                    <!-- 1. Header: Title & Equation -->
                    <div class="formula-header" style="padding: 20px; border-bottom: 1px solid #233554; cursor: pointer;">
                        <span style="display: block; color: var(--accent); font-weight: 700; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; margin-bottom: 10px;">
                            <?= $f['title'] ?>
                        </span>
                        <div class="math-display" style="font-size: 1.2rem; color: #fff;">
                            \[ <?= htmlspecialchars($f['equation']) ?> \]
                        </div>
                        <div style="text-align: right; font-size: 0.7rem; opacity: 0.5;">[ Click to Expand Depth ]</div>
                    </div>

                    <!-- 2. Deep Dive Body (Hidden by default) -->
                    <div class="formula-body" style="display: none; padding: 20px; background: #0a192f;">
                        
                        <!-- A. Semantic Variables & Constants -->
                        <?php if (!empty($f['semantic_variables'])): ?>
                        <div class="variables-section" style="margin-bottom: 20px;">
                            <h4 style="font-size: 0.9rem; color: var(--accent); border-bottom: 1px solid rgba(100, 255, 218, 0.2); padding-bottom: 5px;">Variables & Constants</h4>
                            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 10px;">
                                <?php foreach ($f['semantic_variables'] as $symbol => $v): ?>
                                    <div class="var-item" style="font-size: 0.9rem;">
                                        <code style="color: #FFD700; font-weight: bold;"><?= htmlspecialchars($symbol) ?></code>: 
                                        <span style="color: #8892b0;">
                                            <?= $v['name'] ?? $v['desc'] ?? 'System variable' ?>
                                            <?php if (($v['type'] ?? '') === 'constant'): ?>
                                                <small style="background: rgba(100,255,218,0.1); padding: 2px 4px; border-radius: 3px; margin-left: 5px;">CONST</small>
                                            <?php endif; ?>
                                        </span>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                        <?php endif; ?>

                        <!-- B. Triple-Depth Breakdown -->
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
        const header = event.target.closest('.formula-header');
        if (!header) return;

        const card = header.closest('.platinum-formula-card');
        const body = card.querySelector('.formula-body');
        
        if (body) {
            const isVisible = body.style.display === 'block';
            body.style.display = isVisible ? 'none' : 'block';
            card.style.borderColor = isVisible ? '#233554' : 'var(--accent)';
            card.style.boxShadow = isVisible ? 'none' : '0 10px 30px -15px rgba(2,12,27,0.7)';
            
            if (!isVisible && typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                MathJax.typesetPromise([body]);
            }
        }
    });
});
</script>
