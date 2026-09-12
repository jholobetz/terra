<?php
/**
 * Platinum Standard Topic Hub — Master-Detail Command Console
 * High-density pedagogical curriculum navigator paired with a live holographic detail stage.
 */

require_once __DIR__ . '/_topic_icons.php';

// Resolve category theme mapping
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

// Compute Metrics
$totalPillars = !empty($pillars) && is_array($pillars) ? count($pillars) : 0;
$allSubtopicSlugs = [];
$firstActiveSlug = null;
if (!empty($pillars) && is_array($pillars)) {
    foreach ($pillars as $p) {
        if (!empty($p['slugs']) && is_array($p['slugs'])) {
            foreach ($p['slugs'] as $s) {
                $allSubtopicSlugs[$s] = true;
                if ($firstActiveSlug === null && !empty($subtopics_map[$s])) {
                    $firstActiveSlug = $s;
                }
            }
        }
    }
}
$totalConcepts = count($allSubtopicSlugs);
$totalFormulas = !empty($formulas) && is_array($formulas) ? count($formulas) : (!empty($equations) && is_array($equations) ? count($equations) : 0);
$totalBridges = !empty($bridges) && is_array($bridges) ? count($bridges) : 0;
?>

<article class="topic-content master-detail-console" style="--accent-color: var(--accent-<?= $theme ?>);">
    
    <!-- Cosmic Command Header -->
    <header class="console-header">
        <div class="header-headline-row">
            <div class="header-title-block">
                <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?></div>
                <h1 class="console-title"><?= htmlspecialchars($title ?? 'Physics Hub') ?></h1>
                <p id="topic-beginning-abstract" class="console-subtitle"><?= $intro ?? 'Comprehensive academic directory of the physical manifold.' ?></p>
            </div>
            <div class="header-meta-badge">
                <span class="meta-item"><strong><?= $totalPillars ?></strong> Pillars</span>
                <span class="meta-sep">/</span>
                <span class="meta-item"><strong><?= $totalConcepts ?></strong> Concepts</span>
                <?php if ($totalFormulas > 0): ?>
                    <span class="meta-sep">/</span>
                    <span class="meta-item"><strong><?= $totalFormulas ?></strong> Identities</span>
                <?php endif; ?>
            </div>
        </div>

        <!-- Toolbar Quick Actions -->
        <div class="console-toolbar">
            <div class="console-search-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="directory-filter-input" placeholder="Quick filter concepts in <?= htmlspecialchars($title ?? 'this faculty') ?>..." autocomplete="off" />
                <span id="directory-match-counter" class="match-counter"></span>
            </div>
            
            <div class="console-nav-actions">
                <button type="button" id="btn-expand-all" class="btn-console-tool" title="Expand All Pillars">Expand All</button>
                <button type="button" id="btn-collapse-all" class="btn-console-tool" title="Collapse All Pillars">Collapse All</button>
                <span class="nav-sep">|</span>
                <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn-console-link">🚀 Overview</a>
                <a href="/physics/universe-graph" class="btn-console-link">🌌 Derivation Graph</a>
                <a href="/physics/simulations" class="btn-console-link">🧪 Simulations</a>
            </div>
        </div>
    </header>

    <!-- Master-Detail Split Console Grid -->
    <div class="console-workspace-grid">
        
        <!-- LEFT RAIL: Curriculum Trajectory Navigator -->
        <aside class="console-navigator-rail" id="console-navigator">
            <div class="rail-header-label">
                <span>CURRICULUM TRAJECTORY</span>
                <span class="rail-count-badge"><?= $totalConcepts ?> nodes</span>
            </div>

            <?php if (!empty($pillars) && is_array($pillars)): ?>
                <div class="curriculum-pillar-stack" id="curriculum-stack">
                    <?php foreach ($pillars as $pIdx => $pillar): 
                        $pillarSubCount = !empty($pillar['slugs']) ? count($pillar['slugs']) : 0;
                        $cleanTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                        $isFirstPillar = ($pIdx === 0);
                    ?>
                        <section class="pillar-group <?= $isFirstPillar ? 'is-open' : 'is-open' ?>" data-pillar-idx="<?= $pIdx ?>">
                            <!-- Pillar Station Header -->
                            <button type="button" class="pillar-station-btn" aria-expanded="true" data-pillar-toggle="<?= $pIdx ?>">
                                <div class="station-left">
                                    <span class="station-chevron">▼</span>
                                    <span class="station-num"><?= sprintf('%02d', $pIdx + 1) ?></span>
                                    <span class="station-title"><?= htmlspecialchars($cleanTitle) ?></span>
                                </div>
                                <span class="station-badge-count"><?= $pillarSubCount ?></span>
                            </button>

                            <!-- Subtopic Items under this Pillar -->
                            <div class="pillar-concepts-tray" id="tray-<?= $pIdx ?>">
                                <?php foreach ($pillar['slugs'] as $slugItem): 
                                    $sub = $subtopics_map[$slugItem] ?? null;
                                    if (!$sub) continue;
                                    $level = getConceptLevel($slugItem, $sub['title']);
                                    $isActive = ($slugItem === $firstActiveSlug);
                                ?>
                                    <div class="console-concept-item topic-subtopic-row directory-concept-row <?= $isActive ? 'is-active' : '' ?>" 
                                         data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>"
                                         data-title="<?= htmlspecialchars(strtolower($sub['title'])) ?>"
                                         data-level="<?= strtolower($level) ?>"
                                         data-pillar-idx="<?= $pIdx ?>"
                                         tabindex="0"
                                         role="button">
                                        <div class="concept-item-indicator"></div>
                                        <div class="concept-item-content">
                                            <span class="concept-title"><?= str_replace('\\\\', '\\', $sub['title']) ?></span>
                                        </div>
                                        <span class="topic-level-badge level-badge-<?= strtolower($level) ?>"><?= $level ?></span>
                                        
                                        <!-- Preserved hidden abstract for semantic variable hover & test assertions -->
                                        <span class="subtopic-card-abstract" style="display: none;">
                                            <?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?>
                                        </span>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </section>
                    <?php endforeach; ?>
                </div>
            <?php else: ?>
                <div class="glass-card" style="padding: 20px; text-align: center; color: var(--text-muted);">
                    <?= $content ?? '<p>No curriculum concepts defined for this faculty.</p>' ?>
                </div>
            <?php endif; ?>
        </aside>

        <!-- RIGHT MAIN STAGE: Live Holographic Inspection Stage -->
        <main class="console-detail-stage" id="console-detail-stage" aria-live="polite">
            <?php if (!empty($pillars) && is_array($pillars)): ?>
                <?php foreach ($pillars as $pIdx => $pillar): 
                    $cleanPillarTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                    foreach ($pillar['slugs'] as $slugItem): 
                        $sub = $subtopics_map[$slugItem] ?? null;
                        if (!$sub) continue;
                        $level = getConceptLevel($slugItem, $sub['title']);
                        $isActive = ($slugItem === $firstActiveSlug);
                ?>
                    <div class="concept-dossier-card <?= $isActive ? 'is-active' : '' ?>" 
                         id="dossier-<?= htmlspecialchars($slugItem) ?>"
                         data-slug="<?= htmlspecialchars($slugItem) ?>"
                         data-pillar-idx="<?= $pIdx ?>"
                         style="<?= $isActive ? 'display: block;' : 'display: none;' ?>">
                        
                        <!-- Dossier Trajectory Header -->
                        <div class="dossier-header-bar">
                            <div class="dossier-track-label">
                                <span class="dossier-pillar-tag">PILLAR <?= sprintf('%02d', $pIdx + 1) ?></span>
                                <span class="dossier-track-dot">&bull;</span>
                                <span class="dossier-pillar-name"><?= htmlspecialchars($cleanPillarTitle) ?></span>
                            </div>
                            <div class="dossier-chips">
                                <span class="dossier-level-badge level-badge-<?= strtolower($level) ?>"><?= $level ?> Level</span>
                                <span class="dossier-domain-badge"><?= strtoupper(htmlspecialchars($field ?? $theme)) ?></span>
                            </div>
                        </div>

                        <!-- Concept Headline -->
                        <h2 class="dossier-title">
                            <a href="/physics/subtopic/<?= htmlspecialchars($slugItem) ?>" class="dossier-title-link">
                                <?= str_replace('\\\\', '\\', $sub['title']) ?>
                            </a>
                        </h2>

                        <!-- Pillar Pedagogical Framing / Narrative -->
                        <?php if (!empty($pillar['narrative'])): ?>
                            <div class="dossier-pillar-narrative">
                                <span class="narrative-glyph">§</span>
                                <div class="narrative-text"><?= htmlspecialchars($pillar['narrative']) ?></div>
                            </div>
                        <?php endif; ?>

                        <!-- Hero Mathematical Identity Box -->
                        <?php if (!empty($sub['hero_math'])): ?>
                            <div class="dossier-math-container">
                                <div class="dossier-box-label">GOVERNING MATHEMATICAL IDENTITY</div>
                                <div class="dossier-math-display">
                                    <?= $sub['hero_math'] ?>
                                </div>
                            </div>
                        <?php endif; ?>

                        <!-- First-Principles Abstract -->
                        <div class="dossier-abstract-container">
                            <div class="dossier-box-label">FIRST-PRINCIPLES ABSTRACT</div>
                            <div class="dossier-abstract-body subtopic-card-abstract">
                                <?php if (!empty($sub['snippet_svg'])): ?>
                                    <?= $sub['snippet_svg'] ?>
                                <?php elseif (!empty($sub['snippet'])): ?>
                                    <p><?= htmlspecialchars($sub['snippet']) ?></p>
                                <?php else: ?>
                                    <p>Comprehensive academic monograph detailing <?= htmlspecialchars($sub['title']) ?> inside the <?= htmlspecialchars($title ?? 'physics') ?> manifold.</p>
                                <?php endif; ?>
                            </div>
                        </div>

                        <!-- Launch Actions -->
                        <div class="dossier-actions-footer">
                            <a href="/physics/subtopic/<?= htmlspecialchars($slugItem) ?>" class="btn-dossier-primary">
                                <span>Enter Full Treatise</span>
                                <span class="btn-arrow">&rarr;</span>
                            </a>
                            <?php if (!empty($sub['hero_math'])): ?>
                                <a href="/physics/equation-explainer?id=<?= htmlspecialchars($slugItem) ?>" class="btn-dossier-secondary" title="Deconstruct equation tokens and CAS limits">
                                    <span>📐 Dissect Equation</span>
                                </a>
                            <?php endif; ?>
                            <a href="/physics/universe-graph" class="btn-dossier-subtle" title="Explore in mathematical derivation DAG">
                                <span>🌌 Lineage DAG</span>
                            </a>
                        </div>

                    </div>
                <?php endforeach; endforeach; ?>
            <?php endif; ?>
        </main>

    </div>

    <!-- Connected Faculties (Interdisciplinary Bridges Strip) -->
    <?php if (!empty($bridges)): ?>
        <section class="console-bridges-strip">
            <div class="bridges-strip-label">CONNECTED FACULTIES</div>
            <div class="bridges-strip-grid">
                <?php foreach ($bridges as $b): ?>
                    <a href="<?= !empty($b['slug']) ? '/physics/topic/' . htmlspecialchars($b['slug']) : '#' ?>" 
                       class="bridge-console-card" 
                       title="<?= htmlspecialchars($b['description']) ?>">
                        <div class="bridge-card-header">
                            <span class="bridge-title"><?= htmlspecialchars($b['title']) ?></span>
                            <span class="bridge-arrow">&rarr;</span>
                        </div>
                        <?php if (!empty($b['description'])): ?>
                            <div class="bridge-card-desc"><?= htmlspecialchars($b['description']) ?></div>
                        <?php endif; ?>
                    </a>
                <?php endforeach; ?>
            </div>
        </section>
    <?php endif; ?>

    <!-- Core Theoretical Identities Drawer -->
    <details class="console-equations-drawer" id="topic-equations-drawer">
        <summary class="drawer-header-toggle">
            <span class="drawer-title">📐 Key Theoretical Identities Catalog (<?= $totalFormulas ?>)</span>
            <span class="drawer-hint">[ Click to Toggle Formula Cards ]</span>
        </summary>
        <div id="topic-equations-section" class="drawer-body">
            <?php $this->render('physics/_equations_partial', [
                'equations' => $equations ?? [],
                'breakdowns' => $breakdowns ?? [],
                'formulas' => $formulas ?? [],
                'nonce' => $nonce,
                'domain' => $slug
            ]); ?>
        </div>
    </details>

    <script id="topic-var-map" type="application/json">
    <?= json_encode($topicVariableMap ?? [], JSON_HEX_TAG | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE) ?>
    </script>

    <footer class="console-footer">
        <a href="/physics" class="btn-console-back">&larr; Back to Faculty Index</a>
    </footer>
</article>

<!-- Interactive Master-Detail Console Controller Script -->
<script nonce="<?= $nonce ?>">
(function() {
    const conceptItems = document.querySelectorAll('.console-concept-item');
    const dossierCards = document.querySelectorAll('.concept-dossier-card');
    const pillarGroups = document.querySelectorAll('.pillar-group');
    const filterInput = document.getElementById('directory-filter-input');
    const matchCounter = document.getElementById('directory-match-counter');
    const btnExpandAll = document.getElementById('btn-expand-all');
    const btnCollapseAll = document.getElementById('btn-collapse-all');
    const stageContainer = document.getElementById('console-detail-stage');

    // Activate a Concept Item and Reveal its Dossier Card
    function activateConcept(slug, shouldScroll = false) {
        if (!slug) return;

        // 1. Update active states on left rail
        conceptItems.forEach(item => {
            if (item.getAttribute('data-subtopic-slug') === slug) {
                item.classList.add('is-active');
                // Ensure parent pillar is open
                const parentPillar = item.closest('.pillar-group');
                if (parentPillar && !parentPillar.classList.contains('is-open')) {
                    togglePillar(parentPillar, true);
                }
            } else {
                item.classList.remove('is-active');
            }
        });

        // 2. Reveal matching dossier card on right stage
        dossierCards.forEach(card => {
            if (card.getAttribute('data-slug') === slug) {
                card.style.display = 'block';
                // Trigger CSS fade animation
                card.classList.add('is-active');
                if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                    MathJax.typesetPromise([card]);
                }
            } else {
                card.style.display = 'none';
                card.classList.remove('is-active');
            }
        });

        // 3. Scroll stage into view on small screens if stacked
        if (shouldScroll && window.innerWidth < 960 && stageContainer) {
            stageContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // Bind Click and Keyboard Events to Concept Items
    conceptItems.forEach(item => {
        item.addEventListener('click', function(e) {
            const slug = this.getAttribute('data-subtopic-slug');
            activateConcept(slug, true);
        });

        item.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const slug = this.getAttribute('data-subtopic-slug');
                activateConcept(slug, true);
            }
        });
    });

    // Keyboard Arrow Navigation between Concepts
    const navigatorRail = document.getElementById('console-navigator');
    if (navigatorRail) {
        navigatorRail.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                const visibleItems = Array.from(conceptItems).filter(item => item.style.display !== 'none' && item.closest('.pillar-group').classList.contains('is-open'));
                const activeIndex = visibleItems.findIndex(item => item.classList.contains('is-active'));
                
                let nextIndex = activeIndex;
                if (e.key === 'ArrowDown') {
                    nextIndex = (activeIndex + 1 < visibleItems.length) ? activeIndex + 1 : 0;
                } else if (e.key === 'ArrowUp') {
                    nextIndex = (activeIndex - 1 >= 0) ? activeIndex - 1 : visibleItems.length - 1;
                }

                if (visibleItems[nextIndex]) {
                    e.preventDefault();
                    visibleItems[nextIndex].focus();
                    const slug = visibleItems[nextIndex].getAttribute('data-subtopic-slug');
                    activateConcept(slug, false);
                }
            }
        });
    }

    // Toggle Single Pillar Accordion
    function togglePillar(pillarGroup, forceOpen = null) {
        const btn = pillarGroup.querySelector('.pillar-station-btn');
        const tray = pillarGroup.querySelector('.pillar-concepts-tray');
        if (!btn || !tray) return;

        const isOpen = (forceOpen !== null) ? forceOpen : !pillarGroup.classList.contains('is-open');
        if (isOpen) {
            pillarGroup.classList.add('is-open');
            btn.setAttribute('aria-expanded', 'true');
            tray.style.display = 'flex';
        } else {
            pillarGroup.classList.remove('is-open');
            btn.setAttribute('aria-expanded', 'false');
            tray.style.display = 'none';
        }
    }

    // Bind Pillar Station Header Buttons
    pillarGroups.forEach(group => {
        const btn = group.querySelector('.pillar-station-btn');
        if (btn) {
            btn.addEventListener('click', function() {
                togglePillar(group);
            });
        }
    });

    // Expand All / Collapse All Controls
    if (btnExpandAll) {
        btnExpandAll.addEventListener('click', function() {
            pillarGroups.forEach(group => togglePillar(group, true));
        });
    }

    if (btnCollapseAll) {
        btnCollapseAll.addEventListener('click', function() {
            pillarGroups.forEach(group => togglePillar(group, false));
        });
    }

    // Real-Time Filter & Search
    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            let visibleCount = 0;
            let firstMatchedSlug = null;

            pillarGroups.forEach(group => {
                const items = group.querySelectorAll('.console-concept-item');
                let groupHasMatch = false;

                items.forEach(item => {
                    const title = item.getAttribute('data-title') || '';
                    const slug = item.getAttribute('data-subtopic-slug') || '';
                    const level = item.getAttribute('data-level') || '';

                    if (!query || title.includes(query) || slug.includes(query) || level.includes(query)) {
                        item.style.display = 'flex';
                        groupHasMatch = true;
                        visibleCount++;
                        if (!firstMatchedSlug) firstMatchedSlug = slug;
                    } else {
                        item.style.display = 'none';
                    }
                });

                if (query) {
                    if (groupHasMatch) {
                        group.style.display = 'block';
                        togglePillar(group, true); // Auto-expand matching pillar
                    } else {
                        group.style.display = 'none';
                    }
                } else {
                    group.style.display = 'block';
                }
            });

            if (matchCounter) {
                matchCounter.textContent = query ? `${visibleCount}/${conceptItems.length}` : '';
            }

            // If active item was filtered out, activate first matched item
            if (query && firstMatchedSlug) {
                const activeItem = document.querySelector('.console-concept-item.is-active');
                if (!activeItem || activeItem.style.display === 'none') {
                    activateConcept(firstMatchedSlug, false);
                }
            }
        });
    }

    // Lazy Typeset Equations when Drawer is Toggled Open
    const eqDrawer = document.getElementById('topic-equations-drawer');
    if (eqDrawer) {
        eqDrawer.addEventListener('toggle', function() {
            if (this.open && window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this]);
            }
        });
    }
})();
</script>

<!-- Scoped CSS for Master-Detail Command Console -->
<style>
.master-detail-console {
    max-width: 1360px;
    margin: 0 auto;
    padding: 0 16px;
    color: #f1f5f9;
}

/* Cosmic Command Header */
.console-header {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid var(--accent-color, #64ffda);
    border-radius: 14px;
    padding: 22px 26px 18px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.header-headline-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 18px;
}

.header-title-block {
    flex: 1;
    min-width: 320px;
}

.header-badge-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 4px;
}

.console-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px;
    line-height: 1.15;
}

.console-subtitle {
    font-size: 0.94rem;
    color: var(--text-muted, #94a3b8);
    margin: 0;
    max-width: 820px;
    line-height: 1.45;
}

.header-meta-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(11, 17, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 6px 16px;
    border-radius: 24px;
    font-size: 0.82rem;
    color: #cbd5e1;
    font-family: 'Space Grotesk', sans-serif;
    white-space: nowrap;
}

.header-meta-badge strong {
    color: #ffffff;
}

.meta-sep {
    color: rgba(255, 255, 255, 0.25);
}

/* Toolbar & Quick Actions */
.console-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.console-search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
    max-width: 380px;
}

.console-search-wrapper input {
    width: 100%;
    padding: 8px 55px 8px 34px;
    background: rgba(11, 17, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.84rem;
    outline: none;
    transition: all 0.2s ease;
}

.console-search-wrapper input:focus {
    border-color: var(--accent-color, #64ffda);
    box-shadow: 0 0 12px rgba(100, 255, 218, 0.2);
}

.search-icon {
    position: absolute;
    left: 10px;
    font-size: 0.8rem;
    opacity: 0.5;
    pointer-events: none;
}

.match-counter {
    position: absolute;
    right: 12px;
    font-size: 0.75rem;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--accent-color, #64ffda);
    font-weight: 600;
}

.console-nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-console-tool {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.74rem;
    font-weight: 600;
    color: var(--text-muted, #94a3b8);
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 6px 10px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-console-tool:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.2);
}

.nav-sep {
    color: rgba(255, 255, 255, 0.15);
    margin: 0 2px;
}

.btn-console-link {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    color: #cbd5e1;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 6px 12px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s;
    white-space: nowrap;
}

.btn-console-link:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
}

/* Master-Detail Split Console Grid */
.console-workspace-grid {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 22px;
    align-items: start;
    margin-bottom: 24px;
}

@media (max-width: 960px) {
    .console-workspace-grid {
        grid-template-columns: 1fr;
    }
}

/* LEFT RAIL: Curriculum Trajectory Navigator */
.console-navigator-rail {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    max-height: calc(100vh - 160px);
    display: flex;
    flex-direction: column;
}

.rail-header-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: rgba(11, 17, 32, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--accent-color, #64ffda);
}

.rail-count-badge {
    color: var(--text-muted, #94a3b8);
    font-weight: 500;
}

.curriculum-pillar-stack {
    overflow-y: auto;
    padding: 8px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    scrollbar-width: thin;
    scrollbar-color: rgba(255, 255, 255, 0.15) transparent;
}

.curriculum-pillar-stack::-webkit-scrollbar {
    width: 5px;
}
.curriculum-pillar-stack::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}

.pillar-group {
    background: rgba(11, 17, 32, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    overflow: hidden;
    transition: all 0.2s;
}

.pillar-group:hover {
    border-color: rgba(255, 255, 255, 0.14);
}

.pillar-station-btn {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 12px;
    background: transparent;
    border: none;
    color: #ffffff;
    cursor: pointer;
    font-family: inherit;
    text-align: left;
    transition: background 0.15s;
}

.pillar-station-btn:hover {
    background: rgba(255, 255, 255, 0.03);
}

.station-left {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.station-chevron {
    font-size: 0.65rem;
    color: var(--accent-color, #64ffda);
    transition: transform 0.2s;
}

.pillar-group:not(.is-open) .station-chevron {
    transform: rotate(-90deg);
}

.station-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
    padding: 2px 5px;
    border-radius: 4px;
}

.station-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.84rem;
    font-weight: 600;
    color: #e2e8f0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.station-badge-count {
    font-size: 0.7rem;
    color: var(--text-muted, #94a3b8);
    background: rgba(255, 255, 255, 0.04);
    padding: 2px 6px;
    border-radius: 10px;
    margin-left: 6px;
}

.pillar-concepts-tray {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 0 4px 6px 8px;
    border-top: 1px solid rgba(255, 255, 255, 0.04);
}

.pillar-group:not(.is-open) .pillar-concepts-tray {
    display: none;
}

/* Concept Item Row */
.console-concept-item {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    padding: 7px 10px;
    border-radius: 6px;
    cursor: pointer;
    background: transparent;
    border: 1px solid transparent;
    transition: all 0.15s ease;
    user-select: none;
}

.console-concept-item:hover {
    background: rgba(255, 255, 255, 0.04);
    transform: translateX(2px);
}

.console-concept-item.is-active {
    background: rgba(100, 255, 218, 0.08);
    border-color: rgba(100, 255, 218, 0.25);
}

.concept-item-indicator {
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 0;
    background: var(--accent-color, #64ffda);
    border-radius: 2px;
    transition: height 0.15s;
}

.console-concept-item.is-active .concept-item-indicator {
    height: 60%;
}

.concept-item-content {
    flex: 1;
    min-width: 0;
}

.concept-title {
    font-size: 0.84rem;
    font-weight: 500;
    color: #cbd5e1;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.console-concept-item.is-active .concept-title {
    color: #ffffff;
    font-weight: 600;
}

/* Level Badges */
.topic-level-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.65rem;
    font-weight: 600;
    padding: 2px 6px;
    border-radius: 4px;
    white-space: nowrap;
}

.level-badge-foundational {
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.2);
}

.level-badge-analytical {
    background: rgba(0, 210, 255, 0.1);
    color: #00d2ff;
    border: 1px solid rgba(0, 210, 255, 0.2);
}

.level-badge-frontier {
    background: rgba(217, 70, 239, 0.1);
    color: #d946ef;
    border: 1px solid rgba(217, 70, 239, 0.2);
}

/* RIGHT MAIN STAGE: Live Holographic Detail Stage */
.console-detail-stage {
    position: sticky;
    top: 20px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 28px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    min-height: 520px;
}

.concept-dossier-card {
    animation: dossierFadeIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes dossierFadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}

.dossier-header-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 12px;
}

.dossier-track-label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.06em;
}

.dossier-pillar-tag {
    color: var(--accent-color, #64ffda);
}

.dossier-track-dot {
    color: rgba(255, 255, 255, 0.2);
}

.dossier-pillar-name {
    color: var(--text-muted, #94a3b8);
}

.dossier-chips {
    display: flex;
    gap: 6px;
}

.dossier-level-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
}

.dossier-domain-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.04);
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.dossier-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 16px;
}

.dossier-title-link {
    color: #ffffff;
    text-decoration: none;
    transition: color 0.2s;
}

.dossier-title-link:hover {
    color: var(--accent-color, #64ffda);
}

/* Pillar Pedagogical Framing Narrative */
.dossier-pillar-narrative {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: rgba(11, 17, 32, 0.7);
    border-left: 3px solid var(--accent-color, #64ffda);
    border-radius: 0 8px 8px 0;
    padding: 10px 14px;
    margin-bottom: 20px;
}

.narrative-glyph {
    color: var(--accent-color, #64ffda);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1rem;
    line-height: 1.2;
}

.narrative-text {
    font-size: 0.88rem;
    color: #94a3b8;
    line-height: 1.45;
    font-style: italic;
}

/* Box Labels */
.dossier-box-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 8px;
}

/* Hero Math Identity Inset */
.dossier-math-container {
    background: rgba(2, 6, 23, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 20px;
    box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.5);
}

.dossier-math-display {
    display: flex;
    justify-content: center;
    align-items: center;
    overflow-x: auto;
    padding: 8px 0;
}

.dossier-math-display svg {
    max-height: 48px;
    width: auto;
    filter: drop-shadow(0 0 12px rgba(100, 255, 218, 0.15));
}

/* Abstract Container */
.dossier-abstract-container {
    background: rgba(11, 17, 32, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 16px 18px;
    margin-bottom: 24px;
}

.dossier-abstract-body {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #cbd5e1;
}

.dossier-abstract-body p {
    margin: 0 0 10px;
}
.dossier-abstract-body p:last-child {
    margin-bottom: 0;
}

/* Actions Footer */
.dossier-actions-footer {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 18px;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-dossier-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-color, #64ffda);
    color: #020617;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 700;
    padding: 10px 20px;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s ease;
    box-shadow: 0 4px 16px rgba(100, 255, 218, 0.25);
}

.btn-dossier-primary:hover {
    background: #ffffff;
    box-shadow: 0 6px 20px rgba(100, 255, 218, 0.4);
    transform: translateY(-1px);
}

.btn-arrow {
    transition: transform 0.2s;
}
.btn-dossier-primary:hover .btn-arrow {
    transform: translateX(3px);
}

.btn-dossier-secondary {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.12);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 10px 16px;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-dossier-secondary:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.25);
    color: #ffffff;
}

.btn-dossier-subtle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: transparent;
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 10px 14px;
    border-radius: 8px;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-dossier-subtle:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.18);
}

/* Connected Faculties Bridges Strip */
.console-bridges-strip {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 24px;
}

.bridges-strip-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 12px;
}

.bridges-strip-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
}

.bridge-console-card {
    background: rgba(11, 17, 32, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 12px 14px;
    text-decoration: none;
    transition: all 0.2s;
}

.bridge-console-card:hover {
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.04);
    transform: translateY(-1px);
}

.bridge-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}

.bridge-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #ffffff;
}

.bridge-arrow {
    color: var(--accent-color, #64ffda);
    font-size: 0.84rem;
    transition: transform 0.2s;
}
.bridge-console-card:hover .bridge-arrow {
    transform: translateX(3px);
}

.bridge-card-desc {
    font-size: 0.78rem;
    color: var(--text-muted, #94a3b8);
    line-height: 1.35;
}

/* Equations Drawer */
.console-equations-drawer {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    margin-bottom: 24px;
    overflow: hidden;
}

.drawer-header-toggle {
    padding: 16px 20px;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(11, 17, 32, 0.7);
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    user-select: none;
}

.drawer-header-toggle:hover {
    background: rgba(255, 255, 255, 0.03);
}

.drawer-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #e2e8f0;
}

.drawer-hint {
    font-size: 0.75rem;
    color: var(--accent-color, #64ffda);
    opacity: 0.8;
}

.drawer-body {
    padding: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.console-footer {
    padding: 16px 0 32px;
    text-align: center;
}

.btn-console-back {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--text-muted, #94a3b8);
    text-decoration: none;
    padding: 8px 18px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    transition: all 0.2s;
}

.btn-console-back:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.2);
}
</style>
