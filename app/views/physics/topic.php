<?php
/**
 * Platinum Standard Topic Hub — The Solar Constellation & Orbiting Radial Manifold
 * An interactive celestial knowledge manifold anchoring the central axiomatic core
 * with concentric orbital pillar tracks and planetary concept nodes.
 */

require_once __DIR__ . '/_topic_icons.php';

// Resolve category theme mapping
$meta = get_topic_icon_and_class($slug);
$theme = $meta['theme'] ?? 'default';

// Landmark equations for the Axiomatic Solar Core
$landmarkAxioms = [
    'quantum-physics' => 'i\\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi',
    'relativity' => 'G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}',
    'classical-mechanics' => '\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) = \\frac{\\partial L}{\\partial q_i}',
    'electromagnetism' => '\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\frac{1}{c^2} \\frac{\\partial \\mathbf{E}}{\\partial t}',
    'thermodynamics-statistical-mechanics' => 'dS \\ge \\frac{dQ}{T}, \\quad S = k_B \\ln \\Omega',
    'fluids-nonlinear' => '\\rho \\frac{D\\mathbf{u}}{Dt} = -\\nabla p + \\mu \\nabla^2 \\mathbf{u}',
    'theoretical-physics' => 'S[\\phi] = \\int d^4x \\, \\mathcal{L}(\\phi, \\partial_\\mu \\phi)',
    'mathematical-methods' => '\\hat{f}(\\xi) = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i x \\xi} dx',
    'standard-model' => '\\mathcal{L}_{\\text{SM}} = -\\frac{1}{4}F_{\\mu\\nu}^a F^{a\\mu\\nu} + \\bar{\\psi}i\\gamma^\\mu D_\\mu \\psi',
    'condensed-matter' => 'H = -\\sum_{\\langle i,j \\rangle} J_{ij} \\sigma_i \\sigma_j',
    'astrophysics' => 'H^2 = \\frac{8\\pi G}{3}\\rho - \\frac{k c^2}{a^2} + \\frac{\\Lambda c^2}{3}',
    'philosophy-of-physics' => '\\langle \\hat{A} \\rangle = \\text{Tr}(\\rho \\hat{A})'
];
$coreEquation = $landmarkAxioms[$slug] ?? null;

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
$conceptsList = [];

if (!empty($pillars) && is_array($pillars)) {
    foreach ($pillars as $pIdx => $p) {
        if (!empty($p['slugs']) && is_array($p['slugs'])) {
            foreach ($p['slugs'] as $s) {
                $allSubtopicSlugs[$s] = true;
                $sub = $subtopics_map[$s] ?? null;
                if ($sub) {
                    if ($firstActiveSlug === null) $firstActiveSlug = $s;
                    $level = getConceptLevel($s, $sub['title']);
                    $conceptsList[$s] = [
                        'slug' => $s,
                        'title' => str_replace('\\\\', '\\', $sub['title']),
                        'pillar_idx' => $pIdx,
                        'pillar_title' => preg_replace('/^\d+\.\s*/', '', $p['title']),
                        'pillar_narrative' => $p['narrative'] ?? '',
                        'level' => $level,
                        'hero_math' => $sub['hero_math'] ?? '',
                        'snippet' => $sub['snippet'] ?? '',
                        'snippet_svg' => $sub['snippet_svg'] ?? ''
                    ];
                }
            }
        }
    }
}
$totalConcepts = count($allSubtopicSlugs);
$totalFormulas = !empty($formulas) && is_array($formulas) ? count($formulas) : (!empty($equations) && is_array($equations) ? count($equations) : 0);
$totalBridges = !empty($bridges) && is_array($bridges) ? count($bridges) : 0;
?>

<article class="topic-content solar-constellation-view" style="--accent-color: var(--accent-<?= $theme ?>);">
    
    <!-- Cosmic Command Header -->
    <header class="constellation-header">
        <div class="header-headline-row">
            <div class="header-title-block">
                <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?></div>
                <h1 class="constellation-title">
                    <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="constellation-title-link" title="Read the <?= htmlspecialchars($title ?? 'Physics Hub') ?> Overview Treatise"><?= htmlspecialchars($title ?? 'Physics Hub') ?></a>
                </h1>
            </div>
            <p id="topic-beginning-abstract" class="constellation-subtitle"><?= $intro ?? 'Comprehensive radial manifold of the physical discipline.' ?></p>
        </div>

        <!-- Toolbar: Mode Switcher & Quick Actions -->
        <div class="constellation-toolbar">
            <!-- View Mode Switcher -->
            <div class="view-mode-switch">
                <button type="button" id="btn-mode-orbit" class="btn-mode-pill active">
                    <span class="mode-icon">🌌</span> Solar Constellation
                </button>
                <button type="button" id="btn-mode-directory" class="btn-mode-pill">
                    <span class="mode-icon">📋</span> Curriculum Directory
                </button>
            </div>

            <!-- Orbit Filter / Search Input -->
            <div class="constellation-search-wrapper">
                <span class="search-icon">🔍</span>
                <input type="text" id="directory-filter-input" placeholder="Search planetary concepts..." autocomplete="off" />
                <span id="directory-match-counter" class="match-counter"></span>
            </div>

            <!-- Quick Navigation Actions -->
            <div class="constellation-nav-actions">
                <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn-console-link">🚀 Overview</a>
                <a href="/physics/universe-graph" class="btn-console-link">🌌 Derivation Graph</a>
                <a href="/physics/simulations" class="btn-console-link">🧪 Simulations</a>
            </div>
        </div>
    </header>

    <!-- SECTION 1: THE SOLAR CONSTELLATION ORBITING MANIFOLD (DEFAULT ACTIVE) -->
    <section class="constellation-manifold-stage" id="stage-constellation-mode">
        
        <!-- Celestial Orbit Legend & Track Filter Strip -->
        <div class="celestial-track-bar">
            <div class="track-bar-label">ORBITAL TRACKS:</div>
            <div class="track-pills-list">
                <button type="button" class="orbit-filter-chip active" data-orbit-target="all">
                    <span class="orbit-chip-dot all"></span> All Orbits
                </button>
                <?php if (!empty($pillars) && is_array($pillars)): ?>
                    <?php foreach ($pillars as $pIdx => $pillar): 
                        $cleanPillarTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                    ?>
                        <button type="button" class="orbit-filter-chip" data-orbit-target="<?= $pIdx ?>">
                            <span class="orbit-chip-dot orbit-<?= $pIdx % 4 ?>"></span>
                            <span>Track <?= sprintf('%02d', $pIdx + 1) ?>: <?= htmlspecialchars($cleanPillarTitle) ?></span>
                        </button>
                    <?php endforeach; ?>
                <?php endif; ?>
            </div>
            <div class="orbit-controls-tools">
                <button type="button" id="btn-orbit-pause" class="btn-orbit-tool" title="Pause / Resume continuous orbital rotation">
                    <span id="orbit-pause-icon">⏸</span> Pause Drift
                </button>
            </div>
        </div>

        <!-- Interactive Radial Constellation Canvas Container -->
        <div class="constellation-viewport" id="constellation-viewport">
            
            <!-- Top-Left Corner Highlighted Subtopic Title -->
            <div class="universe-corner-display" id="universe-corner-display">
                <a href="#" id="universe-corner-title" class="universe-corner-title">Select a Concept Node</a>
            </div>

            <!-- SVG Radial Manifold Plane -->
            <svg id="constellation-svg" class="constellation-svg-plane" viewBox="0 0 1100 580" preserveAspectRatio="xMidYMid meet">
                <defs>
                    <!-- Pulsing Radial Gradients for Solar Core -->
                    <radialGradient id="sun-glow-core" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stop-color="var(--accent-color, #64ffda)" stop-opacity="0.9" />
                        <stop offset="40%" stop-color="var(--accent-color, #64ffda)" stop-opacity="0.35" />
                        <stop offset="80%" stop-color="var(--accent-color, #64ffda)" stop-opacity="0.08" />
                        <stop offset="100%" stop-color="transparent" stop-opacity="0" />
                    </radialGradient>
                    <radialGradient id="sun-corona" cx="50%" cy="50%" r="50%">
                        <stop offset="0%" stop-color="var(--accent-color, #64ffda)" stop-opacity="0.5" />
                        <stop offset="100%" stop-color="transparent" stop-opacity="0" />
                    </radialGradient>
                    
                    <!-- Glow Filters -->
                    <filter id="glow-filter" x="-30%" y="-30%" width="160%" height="160%">
                        <feGaussianBlur stdDeviation="4" result="blur" />
                        <feMerge>
                            <feMergeNode in="blur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                    <filter id="intense-glow" x="-50%" y="-50%" width="200%" height="200%">
                        <feGaussianBlur stdDeviation="8" result="blur1" />
                        <feGaussianBlur stdDeviation="3" result="blur2" />
                        <feMerge>
                            <feMergeNode in="blur1" />
                            <feMergeNode in="blur2" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                <!-- Background Subtle Cosmic Coordinates Grid -->
                <g class="constellation-grid-rings" opacity="0.18">
                    <line x1="550" y1="20" x2="550" y2="560" stroke="rgba(255,255,255,0.2)" stroke-dasharray="3,6" />
                    <line x1="30" y1="290" x2="1070" y2="290" stroke="rgba(255,255,255,0.2)" stroke-dasharray="3,6" />
                </g>

                <!-- Dynamic Orbital Tracks Group (Rendered by JS) -->
                <g id="svg-orbital-tracks-group"></g>

                <!-- Dynamic Gravitational Luminous Connector Ray -->
                <line id="svg-gravitational-ray" x1="550" y1="290" x2="550" y2="290" 
                      stroke="var(--accent-color, #64ffda)" stroke-width="2" stroke-dasharray="4,4" 
                      opacity="0" filter="url(#glow-filter)" />

                <!-- Dynamic Planetary Concept Nodes Group (Rendered by JS) -->
                <g id="svg-planetary-nodes-group"></g>

                <!-- Central Axiomatic Solar Sun Core -->
                <g id="solar-sun-core" class="solar-sun-core" transform="translate(550, 290)">
                    <!-- Outer Pulsing Corona -->
                    <circle r="72" fill="url(#sun-glow-core)" class="sun-pulse-ring" />
                    <circle r="44" fill="rgba(11, 17, 32, 0.92)" stroke="var(--accent-color, #64ffda)" stroke-width="2" filter="url(#glow-filter)" />

                    <!-- Axiomatic Core Label -->
                    <text y="-3" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="8" font-weight="700" letter-spacing="1.5" fill="var(--accent-color, #64ffda)">
                        AXIOMATIC CORE
                    </text>
                    <text y="9" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="7" font-weight="600" fill="#94a3b8">
                        <?= strtoupper(htmlspecialchars($slug)) ?>
                    </text>
                </g>
            </svg>
        </div>

        <!-- Horizontal Holographic HUD Telemetry Console (Docked Below Constellation) -->
        <aside class="holographic-hud-deck" id="constellation-hud-deck" aria-live="polite">
            
            <!-- Row 1: Header Bar (Meta Badges, Concept Title, Narrative, Action Buttons) -->
            <div class="hud-row-header">
                <div class="hud-meta-block">
                    <div class="hud-status-bar">
                        <span class="hud-orbit-label" id="hud-orbit-label">ORBIT 01 // FOUNDATIONAL TRACK</span>
                        <span class="hud-level-tag" id="hud-level-tag">Frontier Level</span>
                    </div>

                    <h2 class="hud-concept-title" id="hud-concept-title">
                        <a href="#" id="hud-concept-link" class="hud-title-link">Select a Concept Node</a>
                    </h2>

                    <div class="hud-pillar-narrative" id="hud-pillar-narrative" style="display: none;">
                        <span class="hud-glyph">§</span>
                        <span id="hud-narrative-text" class="hud-narrative-text"></span>
                    </div>
                </div>

                <div class="hud-actions-bar">
                    <a href="#" id="hud-btn-primary" class="btn-hud-primary">
                        <span>Enter Full Treatise</span>
                        <span class="hud-arrow">&rarr;</span>
                    </a>
                    <a href="#" id="hud-btn-explainer" class="btn-hud-secondary" title="Deconstruct equation tokens and CAS limits" style="display: none;">
                        <span>📐 Dissect Equation</span>
                    </a>
                    <a href="/physics/universe-graph" class="btn-hud-subtle" title="Explore in mathematical derivation DAG">
                        <span>🌌 Lineage DAG</span>
                    </a>
                </div>
            </div>

            <!-- Row 2: Governing Mathematical Identity (Wide Horizontal Band) -->
            <div class="hud-row-equation">
                <div class="hud-equation-inset" id="hud-equation-box">
                    <div class="hud-box-header">GOVERNING IDENTITY</div>
                    <div class="hud-equation-display" id="hud-equation-display">
                        <span style="font-size: 0.8rem; color: #64748b; font-style: italic;">Hover or click a planetary node</span>
                    </div>
                </div>
            </div>

            <!-- Row 3: First-Principles Abstract (Wide Horizontal Band) -->
            <div class="hud-row-abstract">
                <div class="hud-abstract-card">
                    <div class="hud-box-header">FIRST-PRINCIPLES ABSTRACT</div>
                    <div class="hud-abstract-body subtopic-card-abstract" id="hud-abstract-body">
                        <p>Explore the solar constellation by hovering or clicking planetary concept nodes orbiting the central axiomatic core.</p>
                    </div>
                </div>
            </div>

        </aside>
    </section>

    <!-- SECTION 2: THE CURRICULUM DIRECTORY (ALTERNATIVE ACCESSIBLE VIEW) -->
    <section class="curriculum-directory-section" id="stage-directory-mode" style="display: none;">
        <?php if (!empty($pillars) && is_array($pillars)): ?>
            <div class="directory-pillar-grid">
                <?php foreach ($pillars as $pIdx => $pillar): 
                    $cleanPillarTitle = preg_replace('/^\d+\.\s*/', '', $pillar['title']);
                ?>
                    <div class="directory-pillar-column" data-pillar-idx="<?= $pIdx ?>">
                        <div class="directory-column-header">
                            <span class="column-track-num">TRACK <?= sprintf('%02d', $pIdx + 1) ?></span>
                            <h3 class="column-title"><?= htmlspecialchars($cleanPillarTitle) ?></h3>
                            <?php if (!empty($pillar['narrative'])): ?>
                                <p class="column-narrative"><?= htmlspecialchars($pillar['narrative']) ?></p>
                            <?php endif; ?>
                        </div>

                        <div class="directory-column-list">
                            <?php foreach ($pillar['slugs'] as $slugItem): 
                                $sub = $subtopics_map[$slugItem] ?? null;
                                if (!$sub) continue;
                                $level = getConceptLevel($slugItem, $sub['title']);
                            ?>
                                <div class="directory-card topic-subtopic-row directory-concept-row"
                                     data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>"
                                     data-title="<?= htmlspecialchars(strtolower($sub['title'])) ?>"
                                     data-level="<?= strtolower($level) ?>">
                                    <a href="/physics/subtopic/<?= $slugItem ?>" class="directory-card-link">
                                        <div class="card-headline">
                                            <span class="card-name"><?= str_replace('\\\\', '\\', $sub['title']) ?></span>
                                            <span class="topic-level-badge level-badge-<?= strtolower($level) ?>"><?= $level ?></span>
                                        </div>
                                        <?php if (!empty($sub['hero_math'])): ?>
                                            <div class="card-mini-math"><?= $sub['hero_math'] ?></div>
                                        <?php endif; ?>
                                    </a>
                                    <!-- Preserved for semantic variable & test assertions -->
                                    <span class="subtopic-card-abstract" style="display: none;">
                                        <?= !empty($sub['snippet_svg']) ? $sub['snippet_svg'] : ($sub['snippet'] ?? '') ?>
                                    </span>
                                </div>
                            <?php endforeach; ?>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </section>

    <!-- Interdisciplinary Connected Faculties (Cross-Bridges) -->
    <?php if (!empty($bridges)): ?>
        <section class="constellation-bridges-strip">
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
    <details class="constellation-equations-drawer" id="topic-equations-drawer">
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

    <!-- Raw Data for Dynamic Client Constellation Engine -->
    <script id="constellation-data" type="application/json">
    <?= json_encode([
        'slug' => $slug,
        'title' => $title,
        'pillars' => $pillars,
        'concepts' => $conceptsList,
        'firstSlug' => $firstActiveSlug
    ], JSON_HEX_TAG | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE) ?>
    </script>

    <script id="topic-var-map" type="application/json">
    <?= json_encode($topicVariableMap ?? [], JSON_HEX_TAG | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE) ?>
    </script>

    <footer class="constellation-footer">
        <a href="/physics" class="btn-console-back">&larr; Back to Faculty Index</a>
    </footer>
</article>

<!-- Solar Constellation Client Controller Script -->
<script src="/js/topic_constellation.js?v=<?= @filemtime(PROJECT_ROOT . '/public/js/topic_constellation.js') ?: 1 ?>" nonce="<?= $nonce ?>" defer></script>
