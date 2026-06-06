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
                        <span style="color: var(--accent-color); font-weight: 700; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px;">
                            <?= $f['title'] ?>
                        </span>
                        <span class="expand-icon" style="font-size: 0.7rem; opacity: 0.5;">[ Click to Expand Depth ]</span>
                    </div>

                    <div class="formula-math-display" style="padding: 30px 20px; text-align: center; background: #112240;">
                        <div class="math-content" style="font-size: 1.4rem; color: #FFD700;">
                            <?php if (strpos($f['equation'], '<svg') === 0): ?>
                                <?= $f['equation'] ?>
                            <?php else: ?>
                                \[ <?= $f['equation'] ?> \]
                            <?php endif; ?>
                        </div>
                    </div>

                    <div class="formula-body" style="display: none; padding: 20px; background: #0a192f; border-top: 1px solid #233554;">
                        <div class="platinum-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">1. Local Tier: Identity</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5;">
                                    <?= $f['interpretation'] ?? 'Awaiting derivation.' ?>
                                </p>
                            </div>
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">2. Bridge Tier: Symmetry & Origin</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5;">
                                    <?= $f['symmetry_origin'] ?? 'Analysis pending.' ?>
                                </p>
                            </div>
                            <div class="depth-column">
                                <h4 style="font-size: 0.8rem; opacity: 0.7; text-transform: uppercase;">3. Foundational Anchor: Limits</h4>
                                <p style="font-size: 0.95rem; line-height: 1.5;">
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
                                        $varName = is_array($var) ? ($var['name'] ?? $symbol) : $var;
                                        if (is_array($var)) {
                                            $ref = $var['ref'] ?? '';
                                            if (strpos($ref, 'constants/') === 0) {
                                                $constantSlug = str_replace('constants/', '', $ref);
                                                $url = '/physics/constants#' . $constantSlug;
                                            } else if (strpos($ref, 'symbols/') === 0) {
                                                $symbolSlug = str_replace('symbols/', '', $ref);
                                                $url = '/physics/symbols#' . $symbolSlug;
                                            } else if (strpos($ref, 'notation/') === 0) {
                                                $notationSlug = str_replace('notation/', '', $ref);
                                                $url = '/physics/symbols#' . $notationSlug;
                                            } else if (strpos($ref, 'subtopics/') === 0) {
                                                $subtopicSlug = str_replace('subtopics/', '', $ref);
                                                
                                                // Load valid subtopic slugs from the global slug registry
                                                $registry = json_decode(@file_get_contents(PROJECT_ROOT . '/global_slug_registry.json'), true) ?: [];
                                                $validSlugs = array_values($registry);
                                                
                                                // Add topics to valid slugs list
                                                $topics = json_decode(@file_get_contents(PROJECT_ROOT . '/app/config/content/categories.json'), true) ?: [];
                                                foreach ($topics as $t_slug => $t_info) {
                                                    $validSlugs[] = $t_slug;
                                                }
                                                
                                                if (in_array($subtopicSlug, $validSlugs)) {
                                                    $url = '/physics/subtopic/' . $subtopicSlug;
                                                } else {
                                                    // If the slug represents a notation/symbol, map it to the symbols page
                                                    $notation = json_decode(@file_get_contents(PROJECT_ROOT . '/app/config/content/notation.json'), true) ?: [];
                                                    if (isset($notation[$subtopicSlug])) {
                                                        $url = '/physics/symbols#' . $subtopicSlug;
                                                    } else {
                                                        // Fallback to the search engine to prevent 404 errors
                                                        $url = '/physics?search=' . urlencode(str_replace('-', ' ', $subtopicSlug));
                                                    }
                                                }
                                            }
                                        }
                                    ?>
                                    <div class="var-tag" data-symbol="<?= htmlspecialchars($symbol) ?>">
                                        <span style="color: var(--accent-color); font-weight: 700;">\( <?= $symbol ?> \):</span> 
                                        <?php if ($url): ?>
                                            <a href="<?= $url ?>" class="subtopic-link" style="color: #ccd6f6; text-decoration: none; border-bottom: 1px dotted #8892b0;"><strong><?= $varName ?></strong></a>
                                        <?php else: ?>
                                            <span style="color: #ccd6f6;"><?= $varName ?></span>
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
