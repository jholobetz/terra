<?php
/**
 * Platinum Standard Topic Hub - Compact Academic Accordion Directory
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

// Compute Metrics
$totalPillars = !empty($pillars) && is_array($pillars) ? count($pillars) : 0;
$allSubtopicSlugs = [];
if (!empty($pillars) && is_array($pillars)) {
    foreach ($pillars as $p) {
        if (!empty($p['slugs']) && is_array($p['slugs'])) {
            foreach ($p['slugs'] as $s) {
                $allSubtopicSlugs[$s] = true;
            }
        }
    }
}
$totalConcepts = count($allSubtopicSlugs);
$totalFormulas = !empty($formulas) && is_array($formulas) ? count($formulas) : (!empty($equations) && is_array($equations) ? count($equations) : 0);
$totalBridges = !empty($bridges) && is_array($bridges) ? count($bridges) : 0;
?>

<article class="topic-content compact-directory" style="--accent-color: var(--accent-<?= $theme ?>);">
    
    <!-- Minimalist Compact Directory Header -->
    <header class="directory-header">
        <div class="header-headline-row">
            <div>
                <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?></div>
                <h1 class="directory-title"><?= htmlspecialchars($title ?? 'Physics Hub') ?></h1>
                <p id="topic-beginning-abstract" class="directory-subtitle"><?= $intro ?? 'Comprehensive academic directory of the physical manifold.' ?></p>
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

        <!-- Quick Filter & Action Bar -->
        <div class="directory-toolbar">
            <div class="directory-search-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="directory-filter-input" placeholder="Quick filter concepts in <?= htmlspecialchars($title ?? 'this faculty') ?>..." autocomplete="off" />
                <span id="directory-match-counter" class="match-counter"></span>
            </div>
            
            <div class="directory-accordion-controls">
                <button type="button" id="btn-expand-all" class="btn-tool-subtle">Expand All</button>
                <button type="button" id="btn-collapse-all" class="btn-tool-subtle">Collapse All</button>
            </div>

            <div class="directory-actions">
                <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn-tool">🚀 Overview</a>
                <a href="/physics/universe-graph" class="btn-tool">🌌 Derivation Graph</a>
                <a href="/physics/simulations" class="btn-tool">🧪 Simulations</a>
            </div>
        </div>
    </header>

    <!-- Stacked Full-Width Grouped Subtopics Directory -->
    <div class="content-body" style="margin-bottom: 24px;">
        <?php if (!empty($pillars) && is_array($pillars)): ?>
            <div class="directory-accordion-stack" id="directory-accordion-stack">
                <?php foreach ($pillars as $idx => $pillar): 
                    $pillarSubCount = !empty($pillar['slugs']) ? count($pillar['slugs']) : 0;
                    $cleanTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                ?>
                    <section class="topic-pillar-card directory-accordion-item" data-pillar-idx="<?= $idx ?>">
                        <button type="button" class="accordion-trigger topic-pillar-trigger" aria-expanded="false" data-pillar-toggle="<?= $idx ?>">
                            <div class="trigger-left">
                                <span class="accordion-chevron">▶</span>
                                <span class="pillar-num"><?= sprintf('%02d', $idx + 1) ?></span>
                                <h3 class="pillar-title"><?= htmlspecialchars($cleanTitle) ?></h3>
                            </div>
                            <div class="trigger-right">
                                <span class="pillar-count-tag"><?= $pillarSubCount ?> concepts</span>
                            </div>
                        </button>

                        <div class="accordion-content" style="display: none;">
                            <div class="topic-subtopics-list">
                                <?php foreach ($pillar['slugs'] as $slugItem): 
                                    $sub = $subtopics_map[$slugItem] ?? null;
                                    if (!$sub) continue;
                                    $level = getConceptLevel($slugItem, $sub['title']);
                                ?>
                                    <div class="topic-subtopic-row directory-concept-row" 
                                         data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>"
                                         data-title="<?= htmlspecialchars(strtolower($sub['title'])) ?>"
                                         data-level="<?= strtolower($level) ?>">
                                        <a href="/physics/subtopic/<?= $slugItem ?>" class="topic-subtopic-link directory-subtopic-link subtopic-link">
                                            <span class="topic-subtopic-title"><?= str_replace('\\\\', '\\', $sub['title']) ?></span>
                                            <span class="topic-subtopic-meta">
                                                <span class="topic-level-badge level-badge-<?= strtolower($level) ?>"><?= $level ?></span>
                                                <span class="topic-row-arrow">&rarr;</span>
                                            </span>
                                        </a>
                                        <!-- Preserved for semantic variable & testing hooks -->
                                        <span class="subtopic-card-abstract" style="display: none;">
                                            <?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?>
                                        </span>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        </div>
                    </section>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="glass-card" style="padding: 24px; text-align: center;">
                <?= $content ?? '<p>No concepts currently listed for this directory.</p>' ?>
            </div>
        <?php endif; ?>
    </div>

    <!-- Interdisciplinary Bridges (Compact Strip) -->
    <?php if (!empty($bridges)): ?>
        <div class="directory-bridges-strip">
            <span class="bridges-strip-label">CONNECTED FACULTIES:</span>
            <div class="bridges-strip-links">
                <?php foreach ($bridges as $b): ?>
                    <a href="<?= !empty($b['slug']) ? '/physics/topic/' . $b['slug'] : '#' ?>" 
                       class="bridge-strip-pill" 
                       title="<?= htmlspecialchars($b['description']) ?>">
                        <?= htmlspecialchars($b['title']) ?> &rarr;
                    </a>
                <?php endforeach; ?>
            </div>
        </div>
    <?php endif; ?>

    <!-- Core Theoretical Identities Drawer -->
    <details class="directory-drawer" id="topic-equations-drawer">
        <summary class="drawer-header-toggle">
            <span class="drawer-title">📐 Key Theoretical Identities (<?= $totalFormulas ?>)</span>
            <span class="drawer-hint">[ Click to Toggle Formula Catalog ]</span>
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

    <footer class="directory-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Faculty Index</a>
    </footer>
</article>

<!-- Interactive Accordion, Filter & Expansion Script -->
<script nonce="<?= $nonce ?>">
(function() {
    const items = document.querySelectorAll('.directory-accordion-item');
    const filterInput = document.getElementById('directory-filter-input');
    const matchCounter = document.getElementById('directory-match-counter');
    const btnExpandAll = document.getElementById('btn-expand-all');
    const btnCollapseAll = document.getElementById('btn-collapse-all');
    const allRows = document.querySelectorAll('.topic-subtopic-row, .directory-concept-row');
    const totalCount = allRows.length;

    // Helper: Toggle Accordion Item
    function toggleAccordion(item, forceOpen = null) {
        const trigger = item.querySelector('.accordion-trigger');
        const content = item.querySelector('.accordion-content');
        if (!trigger || !content) return;

        const shouldOpen = (forceOpen !== null) ? forceOpen : (content.style.display === 'none');
        if (shouldOpen) {
            content.style.display = 'block';
            item.classList.add('open');
            trigger.setAttribute('aria-expanded', 'true');
        } else {
            content.style.display = 'none';
            item.classList.remove('open');
            trigger.setAttribute('aria-expanded', 'false');
        }
    }

    // Bind Accordion Header Clicks
    items.forEach(item => {
        const trigger = item.querySelector('.accordion-trigger');
        if (trigger) {
            trigger.addEventListener('click', function() {
                toggleAccordion(item);
            });
        }
    });

    // Expand All / Collapse All Controls
    if (btnExpandAll) {
        btnExpandAll.addEventListener('click', function() {
            items.forEach(item => toggleAccordion(item, true));
        });
    }

    if (btnCollapseAll) {
        btnCollapseAll.addEventListener('click', function() {
            items.forEach(item => toggleAccordion(item, false));
        });
    }

    // Instant Filter & Smart Auto-Expand
    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            let visibleCount = 0;

            items.forEach(item => {
                const rows = item.querySelectorAll('.topic-subtopic-row, .directory-concept-row');
                let pillarHasMatch = false;

                rows.forEach(row => {
                    const title = row.getAttribute('data-title') || '';
                    const slug = row.getAttribute('data-subtopic-slug') || '';
                    if (!query || title.includes(query) || slug.includes(query)) {
                        row.style.display = 'block';
                        pillarHasMatch = true;
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });

                if (query) {
                    if (pillarHasMatch) {
                        item.style.display = 'block';
                        item.style.opacity = '1';
                        toggleAccordion(item, true); // Auto-expand matching pillars
                    } else {
                        item.style.display = 'none';
                    }
                } else {
                    item.style.display = 'block';
                    item.style.opacity = '1';
                    toggleAccordion(item, false); // Return to compact collapsed state on clear
                }
            });

            if (matchCounter) {
                if (query) {
                    matchCounter.textContent = `${visibleCount}/${totalCount}`;
                } else {
                    matchCounter.textContent = '';
                }
            }
        });
    }

    // Lazy typeset equations when drawer is toggled open
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

<!-- Scoped CSS for Single Full-Width Stacked Accordion Directory -->
<style>
.compact-directory {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 10px;
}

/* Minimalist Directory Header */
.directory-header {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid var(--accent-color, #64ffda);
    border-radius: 12px;
    padding: 20px 24px 18px;
    margin-bottom: 20px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
}

.header-headline-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 16px;
}

.header-badge-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 4px;
}

.directory-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.85rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 4px;
    line-height: 1.2;
}

.directory-subtitle {
    font-size: 0.92rem;
    color: var(--text-muted, #94a3b8);
    margin: 0;
    max-width: 780px;
    line-height: 1.4;
}

.header-meta-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(11, 17, 32, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 0.8rem;
    color: #cbd5e1;
    font-family: 'Space Grotesk', sans-serif;
    white-space: nowrap;
}

.header-meta-badge strong {
    color: #ffffff;
}

.meta-sep {
    color: rgba(255, 255, 255, 0.2);
}

/* Toolbar & Quick Search */
.directory-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.directory-search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
    max-width: 380px;
}

.directory-search-wrapper input {
    width: 100%;
    padding: 7px 55px 7px 32px;
    background: rgba(11, 17, 32, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.84rem;
    outline: none;
    transition: all 0.2s;
}

.directory-search-wrapper input:focus {
    border-color: var(--accent-color, #64ffda);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.15);
}

.search-icon {
    position: absolute;
    left: 10px;
    font-size: 0.78rem;
    opacity: 0.5;
    pointer-events: none;
}

.match-counter {
    position: absolute;
    right: 10px;
    font-size: 0.75rem;
    font-family: 'Space Grotesk', sans-serif;
    color: var(--accent-color, #64ffda);
    font-weight: 600;
}

.directory-accordion-controls {
    display: flex;
    align-items: center;
    gap: 6px;
}

.btn-tool-subtle {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--text-muted, #94a3b8);
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 5px 10px;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-tool-subtle:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.2);
    background: rgba(255, 255, 255, 0.08);
}

.directory-actions {
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-tool {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
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

.btn-tool:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
}

/* Stacked Accordion Structure */
.directory-accordion-stack {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.directory-accordion-item {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    overflow: hidden;
    transition: border-color 0.2s, background 0.2s;
}

.directory-accordion-item:hover {
    border-color: rgba(255, 255, 255, 0.18);
    background: rgba(15, 23, 42, 0.75);
}

.directory-accordion-item.open {
    border-color: rgba(100, 255, 218, 0.3);
}

/* Accordion Trigger Header Bar */
.accordion-trigger {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 13px 20px;
    background: transparent;
    border: none;
    cursor: pointer;
    text-align: left;
    user-select: none;
    transition: background 0.15s;
}

.accordion-trigger:hover {
    background: rgba(255, 255, 255, 0.03);
}

.trigger-left {
    display: flex;
    align-items: center;
    gap: 12px;
}

.accordion-chevron {
    font-size: 0.72rem;
    color: var(--text-muted, #94a3b8);
    transition: transform 0.2s ease, color 0.2s ease;
    width: 12px;
    display: inline-block;
}

.directory-accordion-item.open .accordion-chevron {
    transform: rotate(90deg);
    color: var(--accent-color, #64ffda);
}

.pillar-num {
    font-family: 'Space Grotesk', monospace;
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
    padding: 2px 6px;
    border-radius: 4px;
}

.pillar-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    letter-spacing: 0.01em;
}

.trigger-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.pillar-count-tag {
    font-size: 0.75rem;
    font-weight: 600;
    color: #64748b;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 3px 9px;
    border-radius: 12px;
}

.directory-accordion-item.open .pillar-count-tag {
    color: #cbd5e1;
    border-color: rgba(255, 255, 255, 0.12);
}

/* Accordion Content & Stacked Grouped Subtopics */
.accordion-content {
    padding: 10px 16px 14px;
    background: rgba(11, 17, 32, 0.45);
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.topic-subtopics-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
    margin: 0;
    padding: 0;
    list-style: none;
}

.topic-subtopic-row,
.directory-concept-row {
    display: block !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
    background: transparent !important;
    border: none !important;
}

.topic-subtopic-link,
.directory-subtopic-link {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 10px 16px !important;
    border-radius: 6px !important;
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-bottom: none !important;
    text-decoration: none !important;
    text-align: left !important;
    transition: background 0.15s ease, border-color 0.15s ease, transform 0.15s ease !important;
}

.topic-subtopic-link:hover,
.directory-subtopic-link:hover {
    background: rgba(255, 255, 255, 0.06) !important;
    border-color: rgba(100, 255, 218, 0.25) !important;
    transform: translateX(3px) !important;
}

.topic-subtopic-title {
    flex: 1 1 auto !important;
    text-align: left !important;
    justify-content: flex-start !important;
    margin: 0 !important;
    padding: 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
    color: #e2e8f0 !important;
    line-height: 1.4 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

.topic-subtopic-link:hover .topic-subtopic-title,
.directory-subtopic-link:hover .topic-subtopic-title {
    color: var(--accent-color, #64ffda) !important;
}

.topic-subtopic-meta {
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    flex-shrink: 0 !important;
    margin-left: 16px !important;
}

.topic-level-badge,
.concept-level-badge {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.68rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    padding: 2px 7px !important;
    border-radius: 4px !important;
    border: 1px solid transparent !important;
}

.level-badge-foundational {
    color: #6ee7b7 !important;
    background: rgba(52, 211, 153, 0.08) !important;
    border-color: rgba(52, 211, 153, 0.2) !important;
}

.level-badge-analytical {
    color: #7dd3fc !important;
    background: rgba(56, 189, 248, 0.08) !important;
    border-color: rgba(56, 189, 248, 0.2) !important;
}

.level-badge-frontier {
    color: #d8b4fe !important;
    background: rgba(192, 132, 252, 0.08) !important;
    border-color: rgba(192, 132, 252, 0.2) !important;
}

.topic-row-arrow,
.concept-row-arrow {
    color: #475569 !important;
    font-size: 0.88rem !important;
    transition: transform 0.15s ease, color 0.15s ease !important;
}

.topic-subtopic-link:hover .topic-row-arrow,
.directory-subtopic-link:hover .topic-row-arrow,
.topic-subtopic-link:hover .concept-row-arrow {
    color: var(--accent-color, #64ffda) !important;
    transform: translateX(3px) !important;
}

/* Bridges Strip */
.directory-bridges-strip {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    background: rgba(15, 23, 42, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 20px;
}

.bridges-strip-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--accent-color, #64ffda);
}

.bridges-strip-links {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.bridge-strip-pill {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    color: #cbd5e1;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 3px 10px;
    border-radius: 4px;
    text-decoration: none;
    transition: all 0.2s;
}

.bridge-strip-pill:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.06);
}

/* Collapsible Equations Drawer */
.directory-drawer {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    margin-bottom: 24px;
    overflow: hidden;
}

.drawer-header-toggle {
    padding: 14px 20px;
    cursor: pointer;
    font-family: 'Space Grotesk', sans-serif;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(255, 255, 255, 0.02);
    user-select: none;
    transition: background 0.2s;
}

.drawer-header-toggle:hover {
    background: rgba(255, 255, 255, 0.05);
}

.drawer-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
}

.drawer-hint {
    font-size: 0.75rem;
    color: var(--text-muted, #94a3b8);
}

.drawer-body {
    padding: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

/* Footer */
.directory-footer {
    padding: 16px 0 32px;
}

@media (max-width: 768px) {
    .header-headline-row {
        flex-direction: column;
    }
    .directory-toolbar {
        flex-direction: column;
        align-items: stretch;
    }
    .directory-search-wrapper {
        max-width: 100%;
    }
}
</style>
