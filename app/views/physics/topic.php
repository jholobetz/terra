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
                <h1 class="constellation-title"><?= htmlspecialchars($title ?? 'Physics Hub') ?></h1>
                <p id="topic-beginning-abstract" class="constellation-subtitle"><?= $intro ?? 'Comprehensive radial manifold of the physical discipline.' ?></p>
            </div>
            <div class="header-meta-badge">
                <span class="meta-item"><strong><?= $totalPillars ?></strong> Orbital Tracks</span>
                <span class="meta-sep">/</span>
                <span class="meta-item"><strong><?= $totalConcepts ?></strong> Planetary Nodes</span>
                <?php if ($totalFormulas > 0): ?>
                    <span class="meta-sep">/</span>
                    <span class="meta-item"><strong><?= $totalFormulas ?></strong> Identities</span>
                <?php endif; ?>
            </div>
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
                    
                    <!-- Faculty SVG Glyph Inside Core -->
                    <g transform="translate(-16, -24) scale(0.32)">
                        <?= $meta['svg'] ?>
                    </g>

                    <!-- Axiomatic Core Label -->
                    <text y="18" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="8" font-weight="700" letter-spacing="1.5" fill="var(--accent-color, #64ffda)">
                        AXIOMATIC CORE
                    </text>
                    <text y="28" text-anchor="middle" font-family="'Space Grotesk', sans-serif" font-size="7" font-weight="600" fill="#94a3b8">
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
<script nonce="<?= $nonce ?>">
(function() {
    // 1. Parse Constellation Data
    let constData = {};
    try {
        constData = JSON.parse(document.getElementById('constellation-data').textContent || '{}');
    } catch(e) {
        console.error('Failed to parse constellation data:', e);
        return;
    }

    const concepts = constData.concepts || {};
    const pillars = constData.pillars || [];
    const svgTracksGroup = document.getElementById('svg-orbital-tracks-group');
    const svgNodesGroup = document.getElementById('svg-planetary-nodes-group');
    const gravityRay = document.getElementById('svg-gravitational-ray');

    // HUD Elements
    const hudDeck = document.getElementById('constellation-hud-deck');
    const hudOrbitLabel = document.getElementById('hud-orbit-label');
    const hudLevelTag = document.getElementById('hud-level-tag');
    const hudConceptTitle = document.getElementById('hud-concept-title');
    const hudConceptLink = document.getElementById('hud-concept-link');
    const hudPillarNarrative = document.getElementById('hud-pillar-narrative');
    const hudNarrativeText = document.getElementById('hud-narrative-text');
    const hudEquationBox = document.getElementById('hud-equation-box');
    const hudEquationDisplay = document.getElementById('hud-equation-display');
    const hudAbstractBody = document.getElementById('hud-abstract-body');
    const hudBtnPrimary = document.getElementById('hud-btn-primary');
    const hudBtnExplainer = document.getElementById('hud-btn-explainer');
    const universeCornerTitle = document.getElementById('universe-corner-title');

    // View Mode Toggles
    const btnModeOrbit = document.getElementById('btn-mode-orbit');
    const btnModeDirectory = document.getElementById('btn-mode-directory');
    const stageConstellation = document.getElementById('stage-constellation-mode');
    const stageDirectory = document.getElementById('stage-directory-mode');
    const btnOrbitPause = document.getElementById('btn-orbit-pause');
    const orbitPauseIcon = document.getElementById('orbit-pause-icon');

    // 2. Orbital Geometry Setup
    // Center point of the solar sun in SVG viewBox (1100 x 580)
    const cx = 550;
    const cy = 290;

    // Define elliptical radii for each pillar track
    // (Tilted perspective gives depth: rx is wide, ry is squashed)
    const baseRx = 150;
    const stepRx = 80;
    const baseRy = 85;
    const stepRy = 45;

    const orbitConfigs = pillars.map((p, idx) => ({
        rx: baseRx + idx * stepRx,
        ry: baseRy + idx * stepRy,
        title: p.title,
        narrative: p.narrative || '',
        slugs: p.slugs || [],
        speed: 0.0012 / (1 + idx * 0.4) // Keplerian: inner orbits move faster
    }));

    // 3. Render Orbital Tracks in SVG
    if (svgTracksGroup) {
        orbitConfigs.forEach((cfg, idx) => {
            const track = document.createElementNS('http://www.w3.org/2000/svg', 'ellipse');
            track.setAttribute('cx', cx);
            track.setAttribute('cy', cy);
            track.setAttribute('rx', cfg.rx);
            track.setAttribute('ry', cfg.ry);
            track.setAttribute('fill', 'none');
            track.setAttribute('stroke', 'rgba(255, 255, 255, 0.12)');
            track.setAttribute('stroke-width', '1.2');
            track.setAttribute('stroke-dasharray', '5, 8');
            track.setAttribute('class', `orbit-track-ring orbit-ring-${idx}`);
            track.setAttribute('data-orbit-idx', idx);
            svgTracksGroup.appendChild(track);

            // Track Label along the ellipse curve
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('x', cx - cfg.rx + 10);
            label.setAttribute('y', cy - 6);
            label.setAttribute('fill', 'rgba(148, 163, 184, 0.6)');
            label.setAttribute('font-family', "'Space Grotesk', sans-serif");
            label.setAttribute('font-size', '8');
            label.setAttribute('font-weight', '600');
            label.setAttribute('letter-spacing', '1');
            label.textContent = `ORBIT ${idx + 1}`;
            svgTracksGroup.appendChild(label);
        });
    }

    // 4. Build Planetary Concept Nodes
    let nodes = [];
    let activeSlug = constData.firstSlug || null;

    orbitConfigs.forEach((cfg, pIdx) => {
        const count = cfg.slugs.length;
        if (count === 0) return;

        cfg.slugs.forEach((slug, sIdx) => {
            const data = concepts[slug];
            if (!data) return;

            const initialAngle = (sIdx / count) * Math.PI * 2;
            const nodeG = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            nodeG.setAttribute('class', 'celestial-node');
            nodeG.setAttribute('data-slug', slug);
            nodeG.setAttribute('data-pillar-idx', pIdx);
            nodeG.style.cursor = 'pointer';

            // Outer Glow Ring
            const aura = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            aura.setAttribute('r', '14');
            aura.setAttribute('class', 'node-aura');
            aura.setAttribute('fill', 'transparent');
            aura.setAttribute('stroke', getTierColor(data.level));
            aura.setAttribute('stroke-width', '1.5');
            aura.setAttribute('opacity', '0.4');

            // Inner Core Body
            const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            core.setAttribute('r', '6');
            core.setAttribute('class', 'node-core');
            core.setAttribute('fill', getTierColor(data.level));
            core.setAttribute('filter', 'url(#glow-filter)');

            // Label Text (Capsule badge)
            const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            textBg.setAttribute('class', 'node-label-bg');
            textBg.setAttribute('rx', '4');
            textBg.setAttribute('ry', '4');
            textBg.setAttribute('fill', 'rgba(11, 17, 32, 0.85)');
            textBg.setAttribute('stroke', 'rgba(255, 255, 255, 0.1)');
            textBg.setAttribute('stroke-width', '0.8');

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('class', 'node-label-text');
            text.setAttribute('font-family', "'Space Grotesk', sans-serif");
            text.setAttribute('font-size', '9');
            text.setAttribute('font-weight', '600');
            text.setAttribute('fill', '#e2e8f0');
            text.textContent = data.title;

            nodeG.appendChild(aura);
            nodeG.appendChild(core);
            nodeG.appendChild(textBg);
            nodeG.appendChild(text);
            svgNodesGroup.appendChild(nodeG);

            nodes.push({
                slug: slug,
                data: data,
                pillarIdx: pIdx,
                element: nodeG,
                aura: aura,
                core: core,
                textBg: textBg,
                text: text,
                angle: initialAngle,
                cfg: cfg
            });
        });
    });

    function getTierColor(level) {
        const l = (level || '').toLowerCase();
        if (l === 'foundational') return '#10b981'; // Emerald
        if (l === 'frontier') return '#d946ef';     // Violet
        return '#00d2ff';                           // Analytical Cyan
    }

    // 5. Update HUD Inspector Deck with Concept Data
    function updateHUD(slug) {
        const data = concepts[slug];
        if (!data) return;

        activeSlug = slug;

        // Context header
        hudOrbitLabel.textContent = `ORBIT ${sprintf2(data.pillar_idx + 1)} // ${data.pillar_title.toUpperCase()}`;
        hudLevelTag.textContent = `${data.level} Level`;
        hudLevelTag.className = `hud-level-tag level-${data.level.toLowerCase()}`;

        // Title and Link
        hudConceptTitle.innerHTML = `<a href="/physics/subtopic/${slug}" class="hud-title-link">${data.title}</a>`;
        hudBtnPrimary.href = `/physics/subtopic/${slug}`;

        if (universeCornerTitle) {
            universeCornerTitle.innerHTML = data.title;
            universeCornerTitle.href = `/physics/subtopic/${slug}`;
            if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                MathJax.typesetPromise([universeCornerTitle]).catch(() => {});
            }
        }

        // Pillar Narrative
        if (data.pillar_narrative) {
            hudNarrativeText.textContent = data.pillar_narrative;
            hudPillarNarrative.style.display = 'flex';
        } else {
            hudPillarNarrative.style.display = 'none';
        }

        // Hero Math
        if (data.hero_math) {
            hudEquationDisplay.innerHTML = data.hero_math;
            hudBtnExplainer.href = `/physics/equation-explainer?id=${slug}`;
            hudBtnExplainer.style.display = 'inline-flex';
            if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
                MathJax.typesetPromise([hudEquationDisplay]);
            }
        } else {
            hudEquationDisplay.innerHTML = `<span style="font-size: 0.8rem; color: #64748b; font-style: italic;">Conceptual Physical Principle</span>`;
            hudBtnExplainer.style.display = 'none';
        }

        // Abstract
        if (data.snippet_svg) {
            hudAbstractBody.innerHTML = data.snippet_svg;
        } else if (data.snippet) {
            hudAbstractBody.innerHTML = `<p>${data.snippet}</p>`;
        } else {
            hudAbstractBody.innerHTML = `<p>Comprehensive monograph detailing ${data.title} inside the physics manifold.</p>`;
        }

        // Update gravitational connector ray
        const activeNode = nodes.find(n => n.slug === slug);
        if (activeNode && gravityRay) {
            gravityRay.setAttribute('x1', cx);
            gravityRay.setAttribute('y1', cy);
            gravityRay.setAttribute('x2', activeNode.currentX || cx);
            gravityRay.setAttribute('y2', activeNode.currentY || cy);
            gravityRay.setAttribute('opacity', '0.75');
        }

        // Highlight active node in SVG
        nodes.forEach(n => {
            if (n.slug === slug) {
                n.element.classList.add('is-active');
                n.aura.setAttribute('r', '18');
                n.aura.setAttribute('opacity', '0.9');
                n.core.setAttribute('r', '8');
            } else {
                n.element.classList.remove('is-active');
                n.aura.setAttribute('r', '14');
                n.aura.setAttribute('opacity', '0.4');
                n.core.setAttribute('r', '6');
            }
        });
    }

    function sprintf2(n) {
        return n < 10 ? '0' + n : '' + n;
    }

    // 6. Bind Node Hover and Click Events
    nodes.forEach(n => {
        n.element.addEventListener('mouseenter', () => {
            updateHUD(n.slug);
        });

        n.element.addEventListener('click', () => {
            updateHUD(n.slug);
        });
    });

    // 7. Continuous Orbital Animation Loop
    let isPaused = false;

    function animateOrbits() {
        if (!isPaused) {
            nodes.forEach(n => {
                n.angle += n.cfg.speed;
            });
        }

        // Position nodes on their respective orbital ellipses
        nodes.forEach(n => {
            const x = cx + Math.cos(n.angle) * n.cfg.rx;
            const y = cy + Math.sin(n.angle) * n.cfg.ry;
            n.currentX = x;
            n.currentY = y;

            n.element.setAttribute('transform', `translate(${x}, ${y})`);

            // Position label badge next to the planet
            const bbox = n.text.getBBox();
            n.textBg.setAttribute('x', 14);
            n.textBg.setAttribute('y', -10);
            n.textBg.setAttribute('width', Math.max(50, bbox.width + 12));
            n.textBg.setAttribute('height', 16);
            n.text.setAttribute('x', 20);
            n.text.setAttribute('y', 2);
        });

        // Update gravitational connector ray to follow active node in real time
        if (activeSlug && gravityRay) {
            const activeNode = nodes.find(n => n.slug === activeSlug);
            if (activeNode) {
                gravityRay.setAttribute('x2', activeNode.currentX || cx);
                gravityRay.setAttribute('y2', activeNode.currentY || cy);
            }
        }

        requestAnimationFrame(animateOrbits);
    }

    // Start animation loop
    requestAnimationFrame(animateOrbits);

    // Initial HUD Activation
    if (activeSlug) {
        updateHUD(activeSlug);
    }

    // 8. Orbit Pause / Play Toggle
    if (btnOrbitPause) {
        btnOrbitPause.addEventListener('click', () => {
            isPaused = !isPaused;
            if (isPaused) {
                btnOrbitPause.classList.add('is-paused');
                btnOrbitPause.innerHTML = '<span id="orbit-pause-icon">▶</span> Resume Drift';
            } else {
                btnOrbitPause.classList.remove('is-paused');
                btnOrbitPause.innerHTML = '<span id="orbit-pause-icon">⏸</span> Pause Drift';
            }
        });
    }

    // 9. Orbit Filter Chips (Focus on specific orbital track)
    const filterChips = document.querySelectorAll('.orbit-filter-chip');
    filterChips.forEach(chip => {
        chip.addEventListener('click', function() {
            filterChips.forEach(c => c.classList.remove('active'));
            this.classList.add('active');

            const target = this.getAttribute('data-orbit-target');
            nodes.forEach(n => {
                if (target === 'all' || target === String(n.pillarIdx)) {
                    n.element.style.opacity = '1';
                    n.element.style.pointerEvents = 'auto';
                } else {
                    n.element.style.opacity = '0.15';
                    n.element.style.pointerEvents = 'none';
                }
            });

            const rings = document.querySelectorAll('.orbit-track-ring');
            rings.forEach(r => {
                const idx = r.getAttribute('data-orbit-idx');
                if (target === 'all' || target === idx) {
                    r.setAttribute('stroke', 'rgba(100, 255, 218, 0.45)');
                    r.setAttribute('stroke-width', '1.8');
                } else {
                    r.setAttribute('stroke', 'rgba(255, 255, 255, 0.05)');
                    r.setAttribute('stroke-width', '0.8');
                }
            });
        });
    });

    // 10. View Mode Switcher (Constellation vs Directory)
    if (btnModeOrbit && btnModeDirectory) {
        btnModeOrbit.addEventListener('click', () => {
            btnModeOrbit.classList.add('active');
            btnModeDirectory.classList.remove('active');
            stageConstellation.style.display = 'block';
            stageDirectory.style.display = 'none';
        });

        btnModeDirectory.addEventListener('click', () => {
            btnModeDirectory.classList.add('active');
            btnModeOrbit.classList.remove('active');
            stageConstellation.style.display = 'none';
            stageDirectory.style.display = 'block';
        });
    }

    // 11. Real-Time Search Filtering across both views
    const filterInput = document.getElementById('directory-filter-input');
    const matchCounter = document.getElementById('directory-match-counter');

    if (filterInput) {
        filterInput.addEventListener('input', function() {
            const query = this.value.trim().toLowerCase();
            let matchCount = 0;
            let firstMatch = null;

            // Filter celestial nodes in Constellation view
            nodes.forEach(n => {
                const title = (n.data.title || '').toLowerCase();
                const slug = n.slug.toLowerCase();
                const level = (n.data.level || '').toLowerCase();

                if (!query || title.includes(query) || slug.includes(query) || level.includes(query)) {
                    n.element.style.display = 'block';
                    n.element.style.opacity = '1';
                    matchCount++;
                    if (!firstMatch) firstMatch = n.slug;
                } else {
                    n.element.style.opacity = '0.08';
                }
            });

            // Filter cards in Directory view
            const dirCards = document.querySelectorAll('.directory-card');
            dirCards.forEach(card => {
                const title = card.getAttribute('data-title') || '';
                const slug = card.getAttribute('data-subtopic-slug') || '';
                const level = card.getAttribute('data-level') || '';

                if (!query || title.includes(query) || slug.includes(query) || level.includes(query)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });

            if (matchCounter) {
                matchCounter.textContent = query ? `${matchCount}/${nodes.length}` : '';
            }

            if (query && firstMatch) {
                updateHUD(firstMatch);
            }
        });
    }

    // 12. Lazy Typeset Equations when Drawer is Toggled Open
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

<!-- Scoped CSS for The Solar Constellation / Orbiting Radial Manifold -->
<style>
.solar-constellation-view {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 16px;
    color: #f1f5f9;
}

/* Header */
.constellation-header {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-top: 2px solid var(--accent-color, #64ffda);
    border-radius: 14px;
    padding: 22px 26px 18px;
    margin-bottom: 20px;
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

.constellation-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px;
    line-height: 1.15;
}

.constellation-subtitle {
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

/* Toolbar */
.constellation-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    padding-top: 14px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.view-mode-switch {
    display: flex;
    gap: 6px;
    background: rgba(11, 17, 32, 0.85);
    padding: 4px;
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-mode-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: transparent;
    border: none;
    border-radius: 6px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-muted, #94a3b8);
    cursor: pointer;
    transition: all 0.2s;
}

.btn-mode-pill:hover {
    color: #ffffff;
}

.btn-mode-pill.active {
    background: var(--accent-color, #64ffda);
    color: #020617;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(100, 255, 218, 0.25);
}

.constellation-search-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    flex: 1;
    max-width: 340px;
}

.constellation-search-wrapper input {
    width: 100%;
    padding: 7px 50px 7px 32px;
    background: rgba(11, 17, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    outline: none;
    transition: all 0.2s;
}

.constellation-search-wrapper input:focus {
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

.constellation-nav-actions {
    display: flex;
    align-items: center;
    gap: 8px;
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

/* SECTION 1: THE SOLAR CONSTELLATION STAGE */
.constellation-manifold-stage {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px 20px 20px;
    margin-bottom: 24px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
    position: relative;
    overflow: hidden;
}

/* Track Filter Strip */
.celestial-track-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    margin-bottom: 12px;
}

.track-bar-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--accent-color, #64ffda);
}

.track-pills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}

.orbit-filter-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(11, 17, 32, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 4px 10px;
    border-radius: 16px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    color: #cbd5e1;
    cursor: pointer;
    transition: all 0.2s;
}

.orbit-filter-chip:hover {
    border-color: rgba(255, 255, 255, 0.25);
    color: #ffffff;
}

.orbit-filter-chip.active {
    background: rgba(100, 255, 218, 0.12);
    border-color: var(--accent-color, #64ffda);
    color: #ffffff;
}

.orbit-chip-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.orbit-chip-dot.all { background: var(--accent-color, #64ffda); }
.orbit-chip-dot.orbit-0 { background: #10b981; }
.orbit-chip-dot.orbit-1 { background: #00d2ff; }
.orbit-chip-dot.orbit-2 { background: #d946ef; }
.orbit-chip-dot.orbit-3 { background: #f59e0b; }

.btn-orbit-tool {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
    padding: 4px 10px;
    border-radius: 6px;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-orbit-tool:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
}

.btn-orbit-tool.is-paused {
    color: var(--accent-color, #64ffda);
    border-color: var(--accent-color, #64ffda);
}

/* Viewport for Full-Width SVG Stage */
.constellation-viewport {
    position: relative;
    width: 100%;
    min-height: 520px;
    background: radial-gradient(ellipse at 50% 50%, rgba(15, 23, 42, 0.45) 0%, rgba(2, 6, 23, 0.98) 75%);
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

.universe-corner-display {
    position: absolute;
    top: 20px;
    left: 24px;
    z-index: 5;
    pointer-events: auto;
    max-width: 480px;
}

.universe-corner-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    color: #ffffff;
    text-decoration: none;
    line-height: 1.25;
    display: inline-block;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.9), 0 0 20px rgba(0, 0, 0, 0.6);
    transition: color 0.2s, text-shadow 0.2s;
}

.universe-corner-title:hover {
    color: var(--accent-color, #64ffda);
    text-shadow: 0 0 12px var(--accent-color, #64ffda);
}

.constellation-svg-plane {
    width: 100%;
    height: 520px;
    display: block;
}

/* Celestial Nodes in SVG */
.celestial-node {
    transition: transform 0.05s linear;
}

.celestial-node:hover .node-aura {
    opacity: 1;
    stroke-width: 2.5;
}

.celestial-node:hover .node-label-bg {
    fill: rgba(15, 23, 42, 0.95);
    stroke: var(--accent-color, #64ffda);
}

.celestial-node:hover .node-label-text {
    fill: #ffffff;
    font-weight: 700;
}

.celestial-node.is-active .node-label-bg {
    stroke: var(--accent-color, #64ffda);
    fill: rgba(100, 255, 218, 0.15);
}

/* Horizontal Holographic HUD Telemetry Console (Docked at Bottom) */
.holographic-hud-deck {
    position: relative;
    width: 100%;
    box-sizing: border-box;
    margin-top: 18px;
    background: rgba(11, 17, 32, 0.92);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top: 2px solid var(--accent-color, #64ffda);
    border-radius: 12px;
    padding: 20px 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    display: flex;
    flex-direction: column;
    gap: 14px;
    z-index: 10;
}

.hud-row-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.hud-meta-block {
    display: flex;
    flex-direction: column;
    gap: 4px;
    flex: 1;
    min-width: 280px;
}

.hud-row-equation {
    width: 100%;
}

.hud-row-abstract {
    width: 100%;
}

@media (max-width: 768px) {
    .universe-corner-display {
        top: 14px;
        left: 16px;
        max-width: 80%;
    }
    .universe-corner-title {
        font-size: 1.15rem;
    }
    .hud-row-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .hud-actions-bar {
        width: 100%;
    }
    .constellation-svg-plane {
        height: 380px;
    }
    .constellation-viewport {
        min-height: 380px;
    }
}

.hud-status-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}

.hud-orbit-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: var(--accent-color, #64ffda);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.hud-level-tag {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 4px;
    white-space: nowrap;
}
.hud-level-tag.level-foundational {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.hud-level-tag.level-analytical {
    background: rgba(0, 210, 255, 0.15);
    color: #00d2ff;
    border: 1px solid rgba(0, 210, 255, 0.3);
}
.hud-level-tag.level-frontier {
    background: rgba(217, 70, 239, 0.15);
    color: #d946ef;
    border: 1px solid rgba(217, 70, 239, 0.3);
}

.hud-concept-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.45rem;
    font-weight: 700;
    line-height: 1.25;
    margin: 0 0 4px;
}

.hud-title-link {
    color: #ffffff;
    text-decoration: none;
    transition: color 0.2s;
}

.hud-title-link:hover {
    color: var(--accent-color, #64ffda);
}

.hud-pillar-narrative {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    background: rgba(2, 6, 23, 0.6);
    border-left: 2px solid var(--accent-color, #64ffda);
    padding: 6px 10px;
    border-radius: 0 6px 6px 0;
    margin-top: 4px;
    margin-bottom: 0;
}

.hud-glyph {
    color: var(--accent-color, #64ffda);
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
}

.hud-narrative-text {
    font-size: 0.8rem;
    color: #94a3b8;
    line-height: 1.35;
    font-style: italic;
}

.hud-box-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.64rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 6px;
}

.hud-equation-inset {
    background: rgba(2, 6, 23, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 12px 20px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    margin-bottom: 0;
    width: 100%;
}

.hud-equation-display {
    display: flex;
    justify-content: center;
    align-items: center;
    overflow-x: auto;
    padding: 4px 0;
    width: 100%;
}

.hud-equation-display svg {
    max-height: 38px;
    width: auto;
    filter: drop-shadow(0 0 10px rgba(100, 255, 218, 0.2));
}

.hud-abstract-card {
    background: rgba(2, 6, 23, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 12px 18px;
    margin-bottom: 0;
    width: 100%;
    box-sizing: border-box;
}

.hud-abstract-body {
    font-size: 0.86rem;
    line-height: 1.45;
    color: #cbd5e1;
}

.hud-abstract-body p {
    margin: 0 0 6px;
}
.hud-abstract-body p:last-child {
    margin-bottom: 0;
}

.hud-actions-bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    padding: 0;
    border: none;
}

.btn-hud-primary {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-color, #64ffda);
    color: #020617;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 8px 16px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(100, 255, 218, 0.25);
}

.btn-hud-primary:hover {
    background: #ffffff;
    transform: translateY(-1px);
}

.hud-arrow {
    transition: transform 0.2s;
}
.btn-hud-primary:hover .hud-arrow {
    transform: translateX(3px);
}

.btn-hud-secondary {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255, 255, 255, 0.04);
    color: #e2e8f0;
    border: 1px solid rgba(255, 255, 255, 0.12);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    padding: 8px 12px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-hud-secondary:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(255, 255, 255, 0.25);
    color: #ffffff;
}

.btn-hud-subtle {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: transparent;
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 8px 10px;
    border-radius: 6px;
    text-decoration: none;
    transition: all 0.2s;
}

.btn-hud-subtle:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.18);
}

/* SECTION 2: THE CURRICULUM DIRECTORY */
.curriculum-directory-section {
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 22px;
    margin-bottom: 24px;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.45);
}

.directory-pillar-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 18px;
}

.directory-pillar-column {
    background: rgba(11, 17, 32, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
}

.directory-column-header {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding-bottom: 12px;
    margin-bottom: 12px;
}

.column-track-num {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    color: var(--accent-color, #64ffda);
    display: block;
    margin-bottom: 4px;
}

.column-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 6px;
}

.column-narrative {
    font-size: 0.8rem;
    color: var(--text-muted, #94a3b8);
    line-height: 1.35;
    margin: 0;
    font-style: italic;
}

.directory-column-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.directory-card {
    background: rgba(2, 6, 23, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 10px 12px;
    transition: all 0.15s;
}

.directory-card:hover {
    border-color: var(--accent-color, #64ffda);
    background: rgba(100, 255, 218, 0.04);
    transform: translateY(-1px);
}

.directory-card-link {
    text-decoration: none;
    display: block;
}

.card-headline {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

.card-name {
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
}

.directory-card:hover .card-name {
    color: var(--accent-color, #64ffda);
}

.card-mini-math {
    margin-top: 6px;
    display: flex;
    justify-content: center;
}
.card-mini-math svg {
    max-height: 24px;
    width: auto;
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
    background: rgba(16, 185, 129, 0.12);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.25);
}
.level-badge-analytical {
    background: rgba(0, 210, 255, 0.12);
    color: #00d2ff;
    border: 1px solid rgba(0, 210, 255, 0.25);
}
.level-badge-frontier {
    background: rgba(217, 70, 239, 0.12);
    color: #d946ef;
    border: 1px solid rgba(217, 70, 239, 0.25);
}

/* Connected Faculties Bridges Strip */
.constellation-bridges-strip {
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
.constellation-equations-drawer {
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

.constellation-footer {
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
