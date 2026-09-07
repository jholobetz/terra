<?php
/**
 * Platinum Standard Topic Hub - Compact Academic Directory (Option A)
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
            <div class="directory-actions">
                <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn-tool">🚀 Overview</a>
                <a href="/physics/universe-graph" class="btn-tool">🌌 Derivation Graph</a>
                <a href="/physics/simulations" class="btn-tool">🧪 Simulations</a>
            </div>
        </div>
    </header>

    <!-- Multi-Column Pillar Directory Grid -->
    <div class="content-body" style="margin-bottom: 24px;">
        <?php if (!empty($pillars) && is_array($pillars)): ?>
            <div class="directory-pillars-grid">
                <?php foreach ($pillars as $idx => $pillar): 
                    $pillarSubCount = !empty($pillar['slugs']) ? count($pillar['slugs']) : 0;
                    $cleanTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                ?>
                    <section class="concept-pillar directory-pillar-col" data-pillar-idx="<?= $idx ?>">
                        <div class="pillar-col-header">
                            <span class="pillar-col-num"><?= sprintf('%02d', $idx + 1) ?></span>
                            <h3 class="pillar-col-title"><?= htmlspecialchars($cleanTitle) ?></h3>
                            <span class="pillar-col-count"><?= $pillarSubCount ?></span>
                        </div>

                        <ul class="directory-rows-list">
                            <?php foreach ($pillar['slugs'] as $slugItem): 
                                $sub = $subtopics_map[$slugItem] ?? null;
                                if (!$sub) continue;
                                $level = getConceptLevel($slugItem, $sub['title']);
                            ?>
                                <li class="concept-card directory-row-item" 
                                    data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>"
                                    data-title="<?= htmlspecialchars(strtolower($sub['title'])) ?>"
                                    data-level="<?= strtolower($level) ?>">
                                    <span class="row-level-dot dot-<?= strtolower($level) ?>" title="<?= $level ?> Level"></span>
                                    <a href="/physics/subtopic/<?= $slugItem ?>" class="subtopic-link">
                                        <?= str_replace('\\\\', '\\', $sub['title']) ?>
                                    </a>
                                    <!-- Preserved for semantic variable & testing hooks -->
                                    <span class="subtopic-card-abstract" style="display: none;">
                                        <?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?>
                                    </span>
                                </li>
                            <?php endforeach; ?>
                        </ul>
                    </section>
                <?php endforeach; ?>
            </div>
        <?php else: ?>
            <div class="glass-card" style="padding: 24px; text-align: center;">
                <?= $content ?? '<p>No concepts currently listed for this directory.</p>' ?>
            </div>
        <?php endif; ?>
    </div>

    <!-- Interdisciplinary Bridges (Compact Footer Bar) -->
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

<!-- Fast Instant Filter & Drawer Script -->
<script nonce="<?= $nonce ?>">
(function() {
    const filterInput = document.getElementById('directory-filter-input');
    const matchCounter = document.getElementById('directory-match-counter');
    const rows = document.querySelectorAll('.directory-row-item');
    const cols = document.querySelectorAll('.directory-pillar-col');
    const totalCount = rows.length;

    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            let visibleCount = 0;

            cols.forEach(col => {
                let colHasMatch = false;
                const colRows = col.querySelectorAll('.directory-row-item');

                colRows.forEach(row => {
                    const title = row.getAttribute('data-title') || '';
                    const slug = row.getAttribute('data-subtopic-slug') || '';
                    if (!query || title.includes(query) || slug.includes(query)) {
                        row.style.display = 'flex';
                        colHasMatch = true;
                        visibleCount++;
                    } else {
                        row.style.display = 'none';
                    }
                });

                if (colHasMatch) {
                    col.style.opacity = '1';
                    col.style.pointerEvents = 'auto';
                } else {
                    col.style.opacity = query ? '0.2' : '1';
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

<!-- Scoped CSS for Option A Compact Academic Directory -->
<style>
.compact-directory {
    max-width: 1380px;
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
    max-width: 420px;
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

/* Dense Multi-Column Pillars Grid */
.directory-pillars-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
    gap: 16px;
}

.directory-pillar-col {
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 14px 16px;
    transition: opacity 0.2s, border-color 0.2s;
    display: flex;
    flex-direction: column;
}

.directory-pillar-col:hover {
    border-color: rgba(255, 255, 255, 0.16);
    background: rgba(15, 23, 42, 0.7);
}

.pillar-col-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.pillar-col-num {
    font-family: 'Space Grotesk', monospace;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.08);
    padding: 2px 5px;
    border-radius: 4px;
}

.pillar-col-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.pillar-col-count {
    font-size: 0.72rem;
    font-weight: 600;
    color: #64748b;
    background: rgba(255, 255, 255, 0.04);
    padding: 2px 6px;
    border-radius: 10px;
}

/* Concept Rows */
.directory-rows-list {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.directory-row-item {
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 6px 8px;
    border-radius: 6px;
    transition: background 0.15s ease, transform 0.15s ease;
}

.directory-row-item:hover {
    background: rgba(255, 255, 255, 0.06);
    transform: translateX(3px);
}

.row-level-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
}

.dot-foundational {
    background: #34d399;
    box-shadow: 0 0 6px rgba(52, 211, 153, 0.4);
}

.dot-analytical {
    background: #38bdf8;
    box-shadow: 0 0 6px rgba(56, 189, 248, 0.4);
}

.dot-frontier {
    background: #c084fc;
    box-shadow: 0 0 6px rgba(192, 132, 252, 0.4);
}

.directory-row-item .subtopic-link {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    color: #e2e8f0;
    text-decoration: none;
    line-height: 1.35;
    flex: 1;
    transition: color 0.15s ease;
}

.directory-row-item:hover .subtopic-link {
    color: var(--accent-color, #64ffda);
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
    .directory-pillars-grid {
        grid-template-columns: 1fr;
    }
}
</style>
