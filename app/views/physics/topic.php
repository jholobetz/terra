<?php
/**
 * Platinum Standard Topic Hub - Unified Dynamic View (Option 1: Research Command Dashboard)
 */

require_once __DIR__ . '/_topic_icons.php';

// Resolve the category theme mapping
$meta = get_topic_icon_and_class($slug);
$theme = $meta['theme'] ?? 'default';

// Determine Level based on technical markers
if (!function_exists('getConceptLevel')) {
    function getConceptLevel($slug, $title) {
        $foundational = ['newton', 'law', 'galileo', 'vector', 'static', 'force', 'energy', 'work', 'torque', 'inertia'];
        $frontier = ['manifold', 'topology', 'tensor', 'bundle', 'chaos', 'nonlinear', 'covariant', 'lie', 'symplectic', 'geodesic', 'action'];
        
        $t = strtolower($title . ' ' . $slug);
        foreach ($frontier as $term) if (strpos($t, $term) !== false) return 'Frontier';
        foreach ($foundational as $term) if (strpos($t, $term) !== false) return 'Foundational';
        return 'Analytical';
    }
}

// Compute Telemetry Metrics
$totalPillars = !empty($pillars) && is_array($pillars) ? count($pillars) : 0;
$allSubtopicSlugs = [];
$levelCounts = ['Foundational' => 0, 'Analytical' => 0, 'Frontier' => 0];

if (!empty($pillars) && is_array($pillars)) {
    foreach ($pillars as $p) {
        if (!empty($p['slugs']) && is_array($p['slugs'])) {
            foreach ($p['slugs'] as $s) {
                if (!isset($allSubtopicSlugs[$s])) {
                    $allSubtopicSlugs[$s] = true;
                    $subTitle = $subtopics_map[$s]['title'] ?? $s;
                    $lvl = getConceptLevel($s, $subTitle);
                    if (isset($levelCounts[$lvl])) {
                        $levelCounts[$lvl]++;
                    }
                }
            }
        }
    }
}
$totalConcepts = count($allSubtopicSlugs);
$totalFormulas = !empty($formulas) && is_array($formulas) ? count($formulas) : (!empty($equations) && is_array($equations) ? count($equations) : 0);
$totalBridges = !empty($bridges) && is_array($bridges) ? count($bridges) : 0;
?>

<article class="topic-content" style="--accent-color: var(--accent-<?= $theme ?>);">
    
    <!-- Option 1: Cosmic Command Header & Telemetry KPI Dashboard -->
    <header class="topic-command-header">
        <div class="topic-header-watermark">
            <?= $meta['svg'] ?>
        </div>

        <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?></div>
        <h1 class="topic-title"><?= htmlspecialchars($title ?? 'Physics Hub') ?></h1>
        <p id="topic-beginning-abstract" class="topic-subtitle"><?= $intro ?? 'Accessing the deep mathematical structure of the physical manifold.' ?></p>

        <!-- Live Domain Telemetry Bar -->
        <div class="topic-telemetry-bar">
            <div class="telemetry-pill">
                <span class="telemetry-icon">🏛️</span>
                <div class="telemetry-data">
                    <span class="telemetry-value"><?= $totalPillars ?></span>
                    <span class="telemetry-label">Pillars</span>
                </div>
            </div>
            <div class="telemetry-pill">
                <span class="telemetry-icon">📜</span>
                <div class="telemetry-data">
                    <span class="telemetry-value"><?= $totalConcepts ?></span>
                    <span class="telemetry-label">Subtopics</span>
                </div>
            </div>
            <div class="telemetry-pill">
                <span class="telemetry-icon">📐</span>
                <div class="telemetry-data">
                    <span class="telemetry-value"><?= $totalFormulas ?></span>
                    <span class="telemetry-label">Identities</span>
                </div>
            </div>
            <div class="telemetry-pill">
                <span class="telemetry-icon">🌉</span>
                <div class="telemetry-data">
                    <span class="telemetry-value"><?= $totalBridges ?></span>
                    <span class="telemetry-label">Bridges</span>
                </div>
            </div>
        </div>

        <!-- Action Bar -->
        <div class="topic-actions-row">
            <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn btn-secondary">🚀 Domain Overview &rarr;</a>
            <a href="/physics/universe-graph" class="btn btn-tertiary">🌌 Derivation Universe Graph</a>
            <a href="/physics/simulations" class="btn btn-tertiary">🧪 Domain Simulations</a>
        </div>
    </header>

    <!-- Top Dock Navigation Bar (Fast Stage Switching) -->
    <div class="topic-dock-wrapper">
        <nav class="topic-stage-dock" aria-label="Topic View Stages">
            <button type="button" class="topic-dock-tab active" data-stage="stage-pillars">
                <span class="tab-icon">🏛️</span>
                <span>Pillars &amp; Concepts</span>
                <span class="topic-dock-badge"><?= $totalConcepts ?></span>
            </button>
            <button type="button" class="topic-dock-tab" data-stage="stage-equations">
                <span class="tab-icon">📐</span>
                <span>Core Identities</span>
                <span class="topic-dock-badge"><?= $totalFormulas ?></span>
            </button>
            <button type="button" class="topic-dock-tab" data-stage="stage-bridges">
                <span class="tab-icon">🌉</span>
                <span>Cross-Disciplinary Bridges</span>
                <span class="topic-dock-badge"><?= $totalBridges ?></span>
            </button>
        </nav>
    </div>

    <div class="content-body">
        
        <!-- STAGE 1: Pillars & Concepts Hub -->
        <div id="stage-pillars" class="topic-stage-pane" style="display: block;">
            
            <?php if (!empty($pillars) && is_array($pillars)): ?>
                
                <!-- Live Search & Multi-Filter Console -->
                <div class="topic-filter-console glass-card">
                    <div class="console-top-row">
                        <div class="console-search-box">
                            <span class="search-lens">🔍</span>
                            <input type="text" id="topic-concept-search" placeholder="Filter concepts by title or keyword..." autocomplete="off" />
                            <button type="button" id="topic-search-clear" style="display: none;">&times;</button>
                        </div>
                        <div class="console-level-chips">
                            <button type="button" class="level-chip-btn active" data-level="all">All Levels (<?= $totalConcepts ?>)</button>
                            <button type="button" class="level-chip-btn level-foundational" data-level="foundational">Foundational (<?= $levelCounts['Foundational'] ?>)</button>
                            <button type="button" class="level-chip-btn level-analytical" data-level="analytical">Analytical (<?= $levelCounts['Analytical'] ?>)</button>
                            <button type="button" class="level-chip-btn level-frontier" data-level="frontier">Frontier (<?= $levelCounts['Frontier'] ?>)</button>
                        </div>
                    </div>

                    <div class="console-bottom-row">
                        <!-- Pillar Filter Tabs -->
                        <div class="pillar-tabs-bar">
                            <button type="button" class="pillar-tab-btn active" data-pillar-idx="all">All Pillars (<?= count($pillars) ?>)</button>
                            <?php foreach ($pillars as $idx => $pillar): ?>
                                <button type="button" class="pillar-tab-btn" data-pillar-idx="<?= $idx ?>"><?= ($idx + 1) ?>. <?= htmlspecialchars($pillar['title']) ?></button>
                            <?php endforeach; ?>
                        </div>
                        <div id="concept-filter-counter" class="concept-filter-counter">
                            Showing all <?= $totalConcepts ?> concepts
                        </div>
                    </div>
                </div>

                <!-- Empty Search Match Banner -->
                <div id="concept-no-results" class="glass-card" style="display: none; padding: 40px; text-align: center; margin-bottom: 30px;">
                    <p style="font-size: 1.1rem; color: #f1f5f9; margin-bottom: 8px;">No concepts match your filter criteria.</p>
                    <p style="font-size: 0.88rem; color: var(--text-muted); margin: 0;">Try adjusting your search query or selecting "All Levels".</p>
                </div>

                <!-- Pillars Content Grids -->
                <?php foreach ($pillars as $idx => $pillar): ?>
                    <section class="concept-pillar" data-pillar-idx="<?= $idx ?>">
                        <div class="pillar-header-group">
                            <span class="pillar-index-badge">PILLAR 0<?= ($idx + 1) ?> // MANIFOLD DOMAIN</span>
                            <h3 class="pillar-header"><?= htmlspecialchars($pillar['title']) ?></h3>
                        </div>
                        <p class="pillar-narrative"><?= $pillar['narrative'] ?></p>
                        <div class="concept-grid">
                            <?php foreach ($pillar['slugs'] as $slugItem): 
                                $sub = $subtopics_map[$slugItem] ?? null;
                                if (!$sub) continue;
                                $level = getConceptLevel($slugItem, $sub['title']);
                            ?>
                                <div class="concept-card" 
                                     data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>"
                                     data-level="<?= strtolower($level) ?>"
                                     data-title="<?= htmlspecialchars(strtolower($sub['title'])) ?>">
                                    <div class="card-glass-sheen"></div>
                                    <div class="concept-anchor">
                                        <span class="level-tag level-<?= strtolower($level) ?>"><?= $level ?></span>
                                        <h4><strong><a href="/physics/subtopic/<?= $slugItem ?>" class="subtopic-link"><?= str_replace('\\\\', '\\', $sub['title']) ?></a></strong></h4>
                                    </div>
                                    
                                    <?php if (!empty($sub['hero_math'])): ?>
                                        <div class="hero-math-badge">
                                            <?= $sub['hero_math'] ?>
                                        </div>
                                    <?php endif; ?>

                                    <div class="concept-detail subtopic-card-abstract">
                                        <p><?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?></p>
                                    </div>
                                    <div class="concept-card-footer">
                                        <span class="explore-subtopic-btn">Explore Deep Dive &rarr;</span>
                                    </div>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </section>
                <?php endforeach; ?>

            <?php else: ?>
                <!-- FALLBACK: CLASSIC STATIC CONTENT -->
                <?= $content ?? '<p>No content available for this topic.</p>' ?>
            <?php endif; ?>

        </div>

        <!-- STAGE 2: Core Identities & Equations Hub -->
        <div id="stage-equations" class="topic-stage-pane" style="display: none;">
            <div class="stage-section-header glass-card" style="margin-bottom: 25px; padding: 24px 28px;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                    <div>
                        <h2 style="font-size: 1.4rem; color: #ffffff; margin: 0 0 6px 0; font-family: 'Space Grotesk', sans-serif;">
                            Key Theoretical Identities
                        </h2>
                        <p style="margin: 0; font-size: 0.92rem; color: var(--text-muted);">
                            Governing algebraic equations, conserved invariants, and canonical derivations in <?= htmlspecialchars($title ?? 'this faculty') ?>.
                        </p>
                    </div>
                    <div class="equation-search-box">
                        <span class="search-lens">🔍</span>
                        <input type="text" id="topic-equation-search" placeholder="Filter equations..." autocomplete="off" />
                    </div>
                </div>
            </div>

            <!-- Equations Catalog Section -->
            <div id="topic-equations-section">
                <?php $this->render('physics/_equations_partial', [
                    'equations' => $equations ?? [],
                    'breakdowns' => $breakdowns ?? [],
                    'formulas' => $formulas ?? [],
                    'nonce' => $nonce,
                    'domain' => $slug
                ]); ?>
            </div>
        </div>

        <!-- STAGE 3: Cross-Disciplinary Bridges Hub -->
        <div id="stage-bridges" class="topic-stage-pane" style="display: none;">
            <div class="stage-section-header glass-card" style="margin-bottom: 25px; padding: 24px 28px;">
                <h2 style="font-size: 1.4rem; color: #ffffff; margin: 0 0 6px 0; font-family: 'Space Grotesk', sans-serif;">
                    Cross-Disciplinary Bridges
                </h2>
                <p style="margin: 0; font-size: 0.92rem; color: var(--text-muted);">
                    Asymptotic limits, correspondence principles, and geometric dualities connecting <?= htmlspecialchars($title ?? 'this faculty') ?> to neighboring physics domains.
                </p>
            </div>

            <?php if (!empty($bridges)): ?>
                <div class="bridge-matrix">
                    <div class="bridge-grid">
                        <?php foreach ($bridges as $b): ?>
                            <div class="bridge-item glass-card">
                                <div class="bridge-badge-row">
                                    <span class="bridge-badge">INTERDISCIPLINARY COUPLING</span>
                                </div>
                                <div class="bridge-item-title">
                                    <?php if (!empty($b['slug'])): ?>
                                        <a href="/physics/topic/<?= $b['slug'] ?>" class="topic-link"><?= htmlspecialchars($b['title']) ?></a>
                                    <?php else: ?>
                                        <?= htmlspecialchars($b['title']) ?>
                                    <?php endif; ?>
                                </div>
                                <p class="bridge-item-desc"><?= htmlspecialchars($b['description']) ?></p>
                                <?php if (!empty($b['slug'])): ?>
                                    <div class="bridge-action">
                                        <a href="/physics/topic/<?= $b['slug'] ?>" class="btn-bridge-explore">Traverse to <?= htmlspecialchars($b['title']) ?> &rarr;</a>
                                    </div>
                                <?php endif; ?>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php else: ?>
                <div class="glass-card" style="padding: 30px; text-align: center; color: var(--text-muted);">
                    No cross-disciplinary bridges currently mapped for this domain.
                </div>
            <?php endif; ?>
        </div>

    </div>

    <script id="topic-var-map" type="application/json">
    <?= json_encode($topicVariableMap ?? [], JSON_HEX_TAG | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE) ?>
    </script>

    <footer class="topic-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Faculty Index</a>
    </footer>
</article>

<!-- Option 1 Interactive Script: Stage Docking, Live Multi-Filter & Card Tilt -->
<script nonce="<?= $nonce ?>">
(function() {
    // 1. Stage Dock Switching
    const dockTabs = document.querySelectorAll('.topic-dock-tab');
    const stagePanes = document.querySelectorAll('.topic-stage-pane');

    dockTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetStage = this.getAttribute('data-stage');
            if (!targetStage) return;

            dockTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');

            stagePanes.forEach(pane => {
                if (pane.id === targetStage) {
                    pane.style.display = 'block';
                    if (targetStage === 'stage-equations' && window.MathJax && window.MathJax.typesetPromise) {
                        window.MathJax.typesetPromise([pane]);
                    }
                } else {
                    pane.style.display = 'none';
                }
            });
        });
    });

    // 2. Live Concept Filtering (Keyword Search + Level Chips + Pillar Selector)
    const conceptSearch = document.getElementById('topic-concept-search');
    const searchClearBtn = document.getElementById('topic-search-clear');
    const levelChips = document.querySelectorAll('.level-chip-btn');
    const pillarBtns = document.querySelectorAll('.pillar-tab-btn');
    const conceptCards = document.querySelectorAll('.concept-card');
    const pillars = document.querySelectorAll('.concept-pillar');
    const counterEl = document.getElementById('concept-filter-counter');
    const noResultsEl = document.getElementById('concept-no-results');

    let currentLevel = 'all';
    let currentPillar = 'all';
    let currentQuery = '';

    function applyConceptFilters() {
        let visibleCount = 0;
        const totalCards = conceptCards.length;

        pillars.forEach(pillar => {
            const pillarIdx = pillar.getAttribute('data-pillar-idx');
            const matchesPillar = (currentPillar === 'all' || currentPillar === pillarIdx);
            let pillarHasVisibleCards = false;

            const cardsInPillar = pillar.querySelectorAll('.concept-card');
            cardsInPillar.forEach(card => {
                const cardLevel = card.getAttribute('data-level') || '';
                const cardTitle = card.getAttribute('data-title') || '';
                const cardSlug = card.getAttribute('data-subtopic-slug') || '';
                const cardSnippet = (card.querySelector('.subtopic-card-abstract') ? card.querySelector('.subtopic-card-abstract').textContent : '').toLowerCase();

                const matchesLevel = (currentLevel === 'all' || currentLevel === cardLevel);
                const matchesSearch = !currentQuery || 
                                      cardTitle.includes(currentQuery) || 
                                      cardSlug.includes(currentQuery) || 
                                      cardSnippet.includes(currentQuery);

                if (matchesPillar && matchesLevel && matchesSearch) {
                    card.style.display = 'flex';
                    pillarHasVisibleCards = true;
                    visibleCount++;
                } else {
                    card.style.display = 'none';
                }
            });

            if (matchesPillar && pillarHasVisibleCards) {
                pillar.style.display = 'block';
            } else {
                pillar.style.display = 'none';
            }
        });

        // Update counter
        if (counterEl) {
            if (visibleCount === totalCards) {
                counterEl.textContent = `Showing all ${totalCards} concepts`;
            } else {
                counterEl.textContent = `Showing ${visibleCount} of ${totalCards} concepts`;
            }
        }

        // Show/Hide No Results Box
        if (noResultsEl) {
            noResultsEl.style.display = (visibleCount === 0) ? 'block' : 'none';
        }
    }

    if (conceptSearch) {
        conceptSearch.addEventListener('input', function() {
            currentQuery = this.value.trim().toLowerCase();
            if (searchClearBtn) {
                searchClearBtn.style.display = currentQuery.length > 0 ? 'inline-block' : 'none';
            }
            applyConceptFilters();
        });
    }

    if (searchClearBtn) {
        searchClearBtn.addEventListener('click', function() {
            if (conceptSearch) {
                conceptSearch.value = '';
                currentQuery = '';
                this.style.display = 'none';
                applyConceptFilters();
                conceptSearch.focus();
            }
        });
    }

    levelChips.forEach(chip => {
        chip.addEventListener('click', function() {
            levelChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            currentLevel = this.getAttribute('data-level') || 'all';
            applyConceptFilters();
        });
    });

    pillarBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation(); // Handle locally to integrate with live multi-filter
            pillarBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            currentPillar = this.getAttribute('data-pillar-idx') || 'all';
            applyConceptFilters();
        });
    });

    // 3. Live Equation Filter
    const equationSearch = document.getElementById('topic-equation-search');
    if (equationSearch) {
        equationSearch.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            const eqItems = document.querySelectorAll('.equation-item');
            eqItems.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (!query || text.includes(query)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // 4. Interactive 3D Parallax Tilt for Glassmorphic Concept Cards
    const cards = document.querySelectorAll('.concept-card');
    cards.forEach(card => {
        let bounds;

        function rotateToMouse(e) {
            if (!bounds) bounds = card.getBoundingClientRect();
            const mouseX = e.clientX;
            const mouseY = e.clientY;
            const leftX = mouseX - bounds.left;
            const topY = mouseY - bounds.top;
            const center = {
                x: leftX - bounds.width / 2,
                y: topY - bounds.height / 2
            };
            
            const tiltX = (center.y / (bounds.height / 2)) * -6;
            const tiltY = (center.x / (bounds.width / 2)) * 6;

            card.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.015, 1.015, 1.015)`;
        }

        card.addEventListener('mouseenter', () => {
            bounds = card.getBoundingClientRect();
            card.style.transition = 'transform 0.1s ease-out, box-shadow 0.3s ease, border-color 0.3s ease';
        });

        card.addEventListener('mousemove', rotateToMouse);

        card.addEventListener('mouseleave', () => {
            card.style.transition = 'transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1), box-shadow 0.3s ease, border-color 0.3s ease';
            card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        });
    });
})();
</script>

<!-- Scoped CSS Styling for Research Command Dashboard -->
<style>
.topic-command-header {
    position: relative;
    padding: 38px 36px 32px;
    margin-bottom: 24px;
    background: radial-gradient(circle at 50% 0%, rgba(100, 255, 218, 0.12) 0%, rgba(15, 23, 42, 0.75) 80%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid var(--accent-color, #64ffda);
    border-radius: 18px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    overflow: hidden;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
}

.header-badge-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 10px;
    display: inline-block;
}

.topic-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 12px;
    line-height: 1.2;
}

.topic-subtitle {
    font-size: 1.05rem;
    color: var(--text-muted, #94a3b8);
    line-height: 1.6;
    max-width: 840px;
    margin: 0 0 24px;
}

/* Domain Telemetry Bar */
.topic-telemetry-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.telemetry-pill {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 8px 16px;
    transition: all 0.2s ease;
}

.telemetry-pill:hover {
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.05);
}

.telemetry-icon {
    font-size: 1.2rem;
}

.telemetry-data {
    display: flex;
    flex-direction: column;
}

.telemetry-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.1;
}

.telemetry-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted, #94a3b8);
    font-weight: 500;
}

.topic-actions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.btn-tertiary {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #cbd5e1;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
}

.btn-tertiary:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
}

/* Stage Dock Tabs */
.topic-dock-wrapper {
    width: 100%;
    margin-bottom: 24px;
}

.topic-stage-dock {
    display: flex;
    gap: 8px;
    padding: 6px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    backdrop-filter: blur(12px);
    overflow-x: auto;
}

.topic-dock-tab {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 18px;
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    color: var(--text-muted, #94a3b8);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.topic-dock-tab:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.04);
}

.topic-dock-tab.active {
    color: #ffffff;
    background: rgba(100, 255, 218, 0.12);
    border-color: rgba(100, 255, 218, 0.35);
    box-shadow: 0 0 15px rgba(100, 255, 218, 0.15);
}

.topic-dock-badge {
    font-size: 0.72rem;
    background: rgba(255, 255, 255, 0.1);
    padding: 2px 7px;
    border-radius: 10px;
    color: #cbd5e1;
}

.topic-dock-tab.active .topic-dock-badge {
    background: var(--accent-color, #64ffda);
    color: #0b1120;
    font-weight: 700;
}

/* In-Topic Filter Console */
.topic-filter-console {
    padding: 20px 24px;
    margin-bottom: 30px;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.console-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.console-search-box, .equation-search-box {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
    min-width: 260px;
    max-width: 440px;
}

.console-search-box input, .equation-search-box input {
    width: 100%;
    padding: 9px 34px 9px 36px;
    background: rgba(11, 17, 32, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    outline: none;
    transition: all 0.2s ease;
}

.console-search-box input:focus, .equation-search-box input:focus {
    border-color: var(--accent-color, #64ffda);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
}

.search-lens {
    position: absolute;
    left: 12px;
    font-size: 0.85rem;
    opacity: 0.6;
    pointer-events: none;
}

#topic-search-clear {
    position: absolute;
    right: 10px;
    background: none;
    border: none;
    color: #94a3b8;
    font-size: 1.1rem;
    cursor: pointer;
    line-height: 1;
}

.console-level-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.level-chip-btn {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 6px 12px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted, #94a3b8);
    cursor: pointer;
    transition: all 0.2s ease;
}

.level-chip-btn:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.25);
}

.level-chip-btn.active {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.3);
}

.level-chip-btn.level-foundational.active {
    background: rgba(52, 211, 153, 0.15);
    border-color: #34d399;
    color: #34d399;
}

.level-chip-btn.level-analytical.active {
    background: rgba(56, 189, 248, 0.15);
    border-color: #38bdf8;
    color: #38bdf8;
}

.level-chip-btn.level-frontier.active {
    background: rgba(192, 132, 252, 0.15);
    border-color: #c084fc;
    color: #c084fc;
}

.console-bottom-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding-top: 12px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.pillar-tabs-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.pillar-tab-btn {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 6px 14px;
    border-radius: 8px;
    background: rgba(11, 17, 32, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--text-muted, #94a3b8);
    cursor: pointer;
    transition: all 0.2s ease;
}

.pillar-tab-btn:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
}

.pillar-tab-btn.active {
    color: #ffffff;
    background: rgba(100, 255, 218, 0.12);
    border-color: var(--accent-color, #64ffda);
}

.concept-filter-counter {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    font-family: 'Space Grotesk', sans-serif;
}

/* Bridges Matrix & Cards */
.bridge-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
}

.bridge-item {
    padding: 24px;
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    gap: 12px;
    transition: all 0.25s ease;
}

.bridge-item:hover {
    border-color: var(--accent-color, #64ffda);
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.bridge-badge-row {
    margin-bottom: 4px;
}

.bridge-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid rgba(100, 255, 218, 0.2);
}

.bridge-item-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: #ffffff;
}

.bridge-item-title a {
    color: #ffffff;
    text-decoration: none;
    transition: color 0.2s ease;
}

.bridge-item-title a:hover {
    color: var(--accent-color, #64ffda);
}

.bridge-item-desc {
    font-size: 0.92rem;
    color: var(--text-muted, #94a3b8);
    line-height: 1.55;
    margin: 0;
    flex: 1;
}

.bridge-action {
    padding-top: 8px;
}

.btn-bridge-explore {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--accent-color, #64ffda);
    text-decoration: none;
    transition: all 0.2s ease;
    display: inline-block;
}

.btn-bridge-explore:hover {
    text-decoration: underline;
}

@media (max-width: 768px) {
    .topic-command-header {
        padding: 24px 20px;
    }
    .topic-title {
        font-size: 1.9rem;
    }
    .console-top-row, .console-bottom-row {
        flex-direction: column;
        align-items: stretch;
    }
    .console-search-box {
        max-width: 100%;
    }
}
</style>
