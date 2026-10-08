<?php
require_once __DIR__ . '/_topic_icons.php';

// Calculate counts per category
$categoryCounts = [
    'all' => count($simulations),
    'classical-mechanics' => 0,
    'electromagnetism' => 0,
    'relativity' => 0,
    'quantum-physics' => 0,
    'thermodynamics-statistical-mechanics' => 0,
    'fluids-nonlinear' => 0,
    'astrophysics' => 0,
];

foreach ($simulations as $sim) {
    $cat = $sim['category'] ?? get_simulation_category($sim['slug']);
    if (isset($categoryCounts[$cat])) {
        $categoryCounts[$cat]++;
    }
}
?>

<div class="simulations-observatory-wrapper" style="padding: 10px 0 60px 0;">
    <!-- ================================================================= -->
    <!-- OBSERVATORY HEADER                                                -->
    <!-- ================================================================= -->
    <header class="simulations-header" style="margin-bottom: 28px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
            <span class="arena-pill-badge" style="background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                Phenomenological Observatory
            </span>
            <span style="color: var(--text-muted); font-size: 0.85rem;">•</span>
            <span style="color: var(--text-muted); font-size: 0.85rem;"><?= count($simulations) ?> Real-Time Numerical Engines</span>
        </div>
        <h1 style="font-size: 2.9rem; margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 50%, var(--accent-classical) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            The Simulations Observatory
        </h1>
        <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 820px;">
            Explore dynamic physical phenomena through real-time numerical solvers, Runge-Kutta integrators, and GPU-accelerated spacetime raytracers across classical, quantum, and relativistic regimes.
        </p>
    </header>

    <!-- ================================================================= -->
    <!-- HERO STAGE: THE LIVING OBSERVATORY VIEWPORT                       -->
    <!-- ================================================================= -->
    <section class="observatory-hero-section" style="margin-bottom: 35px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 18px; padding: 22px; backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);">
        <!-- Hero Header: Title & Preset Buttons -->
        <div style="display: flex; align-items: flex-start; justify-content: space-between; gap: 20px; flex-wrap: wrap; margin-bottom: 18px;">
            <div style="max-width: 580px;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span id="hero-live-indicator" style="display: inline-block; width: 8px; height: 8px; background: #10b981; border-radius: 50%; box-shadow: 0 0 8px #10b981;"></span>
                    <span id="hero-badge" style="font-size: 0.76rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: #38bdf8;">
                        GENERAL RELATIVITY • GPU NULL GEODESICS
                    </span>
                </div>
                <h2 id="hero-title" style="font-size: 1.6rem; margin: 0 0 6px 0; color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-weight: 700;">
                    Relativistic Kerr Black Hole Raytracer
                </h2>
                <div id="hero-desc" style="color: var(--text-muted); font-size: 0.88rem; line-height: 1.5;">
                    Simulating photons and a relativistic accretion disk around a spinning Kerr singularity ($a/M = 0.94$). Gravitational redshift and Doppler beaming ($I_{\text{obs}} = g^4 I_{\text{emit}}$) intensely brighten the approaching disk.
                </div>
            </div>

            <!-- Marquee Preset Switcher Buttons -->
            <div class="hero-preset-group" style="display: flex; gap: 8px; flex-wrap: wrap;">
                <button class="hero-preset-btn active" data-preset="kerr" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 8px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                    🌌 Kerr Black Hole
                </button>
                <button class="hero-preset-btn" data-preset="chaos" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                    ⏳ Double Pendulum
                </button>
                <button class="hero-preset-btn" data-preset="quantum" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                    👻 Quantum Tunneling
                </button>
                <button class="hero-preset-btn" data-preset="vortex" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 8px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                    🌊 Kármán Vortex
                </button>
            </div>
        </div>

        <!-- Canvas Container with Interactive Insets -->
        <div style="position: relative; width: 100%; border-radius: 12px; overflow: hidden; background: #030712; border: 1px solid rgba(255, 255, 255, 0.08);">
            <canvas id="observatory-hero-canvas" style="width: 100%; height: 380px; display: block; cursor: crosshair;"></canvas>

            <!-- Top Controls Overlay -->
            <div style="position: absolute; top: 14px; right: 14px; display: flex; gap: 8px; z-index: 10;">
                <button id="hero-play-pause" class="btn btn-secondary" style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; font-size: 0.78rem; padding: 6px 12px; border-radius: 6px; cursor: pointer; backdrop-filter: blur(8px);">
                    ❚❚ Pause
                </button>
                <button id="hero-reset" class="btn btn-secondary" style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; font-size: 0.78rem; padding: 6px 12px; border-radius: 6px; cursor: pointer; backdrop-filter: blur(8px);">
                    ↺ Reset
                </button>
                <a id="hero-launch-link" href="/physics/simulations/relativistic-black-hole" class="btn btn-primary" style="background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: #fff; font-size: 0.78rem; font-weight: 600; padding: 6px 14px; border-radius: 6px; text-decoration: none; display: inline-flex; align-items: gap: 4px; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.35);">
                    Launch Full Sandbox &rarr;
                </a>
            </div>

            <!-- Telemetry Bar Bottom Inset -->
            <div style="position: absolute; bottom: 0; left: 0; right: 0; background: linear-gradient(0deg, rgba(3, 7, 18, 0.95) 0%, rgba(3, 7, 18, 0.6) 75%, transparent 100%); padding: 16px 20px 14px 20px; display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; z-index: 10;">
                <div style="display: flex; gap: 24px; flex-wrap: wrap;">
                    <div>
                        <span id="hero-telem-label-1" style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); display: block; font-weight: 600;">Singularity Spin (a/M)</span>
                        <strong id="hero-telem-val-1" style="color: #38bdf8; font-size: 0.95rem; font-family: monospace;">0.94</strong>
                    </div>
                    <div>
                        <span id="hero-telem-label-2" style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); display: block; font-weight: 600;">Event Horizon (r₊)</span>
                        <strong id="hero-telem-val-2" style="color: #34d399; font-size: 0.95rem; font-family: monospace;">1.34 M</strong>
                    </div>
                    <div>
                        <span id="hero-telem-label-3" style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); display: block; font-weight: 600;">Photon Sphere (r_ph)</span>
                        <strong id="hero-telem-val-3" style="color: #fbbf24; font-size: 0.95rem; font-family: monospace;">2.05 M</strong>
                    </div>
                    <div>
                        <span id="hero-telem-label-4" style="font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); display: block; font-weight: 600;">Max Doppler Boost (g⁴)</span>
                        <strong id="hero-telem-val-4" style="color: #c084fc; font-size: 0.95rem; font-family: monospace;">5.2×</strong>
                    </div>
                </div>

                <!-- Equation Preview -->
                <div id="hero-equation" style="color: #ffd700; font-size: 0.85rem; max-width: 440px; overflow-x: auto;">
                    \[ ds^2 = -\left(1 - \frac{2Mr}{\rho^2}\right)dt^2 - \frac{4Mar\sin^2\theta}{\rho^2}dtd\phi + \dots \]
                </div>
            </div>
        </div>
    </section>

    <!-- ================================================================= -->
    <!-- ARCHITECTURAL CROSS-BRIDGE BANNER TO LAB TOOLS                     -->
    <!-- ================================================================= -->
    <div class="observatory-bridge-banner" style="background: linear-gradient(135deg, rgba(56, 189, 248, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 14px; padding: 18px 24px; margin-bottom: 35px; display: flex; align-items: center; justify-content: space-between; gap: 20px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 16px;">
            <div style="width: 44px; height: 44px; border-radius: 10px; background: rgba(56, 189, 248, 0.15); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; flex-shrink: 0; border: 1px solid rgba(56, 189, 248, 0.3);">
                🧮
            </div>
            <div>
                <strong style="color: #ffffff; font-size: 1rem; display: block; margin-bottom: 2px;">
                    Looking for Analytical Symmetries or Symbolic CAS Proofs?
                </strong>
                <span style="color: var(--text-muted); font-size: 0.88rem;">
                    Switch from visual sandboxes to variational mechanics, Legendre transforms, and Noether current integrals in the Unified Lab Tools Cockpit.
                </span>
            </div>
        </div>
        <a href="/physics/lab-tools" class="btn btn-primary" style="background: linear-gradient(135deg, #0284c7, #2563eb); border: none; padding: 10px 18px; border-radius: 8px; color: #fff; font-size: 0.88rem; font-weight: 600; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; box-shadow: 0 4px 14px rgba(2, 132, 199, 0.25); white-space: nowrap;">
            Launch Lab Tools Cockpit &rarr;
        </a>
    </div>

    <!-- ================================================================= -->
    <!-- FILTER BAR: CATEGORY PILLS & REAL-TIME SEARCH                      -->
    <!-- ================================================================= -->
    <div class="observatory-controls-bar" style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 18px 20px; margin-bottom: 30px; backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); display: flex; flex-direction: column; gap: 16px;">
        
        <!-- Search & Telemetry Row -->
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap;">
            <div style="position: relative; flex: 1; min-width: 280px;">
                <span style="position: absolute; left: 14px; top: 50%; transform: translateY(-50%); font-size: 1rem; color: var(--text-muted); pointer-events: none;">🔍</span>
                <input 
                    type="text" 
                    id="sim-search-input" 
                    placeholder="Search by concept, equation, or keyword (e.g. chaos, kerr, wave, tunneling, rk4)..." 
                    style="width: 100%; box-sizing: border-box; background: rgba(2, 6, 23, 0.7); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 10px; padding: 11px 16px 11px 40px; color: #ffffff; font-size: 0.92rem; outline: none; transition: all 0.2s;"
                    onfocus="this.style.borderColor='var(--accent-default)'; this.style.boxShadow='0 0 0 2px rgba(56, 189, 248, 0.2)';"
                    onblur="this.style.borderColor='rgba(255, 255, 255, 0.12)'; this.style.boxShadow='none';"
                />
            </div>
            <div style="display: flex; align-items: center; gap: 10px;">
                <span id="sim-count-badge" style="background: rgba(255, 255, 255, 0.06); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 6px 14px; font-size: 0.84rem; color: var(--text-muted); font-weight: 500;">
                    Showing <strong id="sim-visible-count" style="color: #38bdf8;"><?= count($simulations) ?></strong> of <?= count($simulations) ?>
                </span>
            </div>
        </div>

        <!-- Domain Taxonomy Filter Pills -->
        <div class="sim-filter-pills" style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
            <span style="font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-right: 4px;">Domains:</span>
            
            <button class="sim-filter-pill active" data-category="all" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 600; cursor: pointer; transition: all 0.2s;">
                All (<?= $categoryCounts['all'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="classical-mechanics" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                🪐 Mechanics (<?= $categoryCounts['classical-mechanics'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="electromagnetism" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                ⚡ Electromagnetism (<?= $categoryCounts['electromagnetism'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="relativity" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                🌌 Relativity (<?= $categoryCounts['relativity'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="quantum-physics" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                ⚛️ Quantum (<?= $categoryCounts['quantum-physics'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="thermodynamics-statistical-mechanics" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                🔥 Thermodynamics (<?= $categoryCounts['thermodynamics-statistical-mechanics'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="fluids-nonlinear" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                🌊 Fluids (<?= $categoryCounts['fluids-nonlinear'] ?>)
            </button>
            <button class="sim-filter-pill" data-category="astrophysics" style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border: 1px solid rgba(255, 255, 255, 0.08); padding: 6px 14px; border-radius: 8px; font-size: 0.84rem; font-weight: 500; cursor: pointer; transition: all 0.2s;">
                🔭 Celestial (<?= $categoryCounts['astrophysics'] ?>)
            </button>
        </div>
    </div>

    <!-- ================================================================= -->
    <!-- OBSERVATORY GRID: RICH DYNAMIC SCIENTIFIC CARDS                   -->
    <!-- ================================================================= -->
    <section class="topics-grid" id="simulations-deck-grid">
        <?php foreach ($simulations as $sim): 
            $catSlug = $sim['category'] ?? get_simulation_category($sim['slug']);
            $meta = get_topic_icon_and_class($catSlug);
            $engine = $sim['engine'] ?? 'Numerical Simulation';
            $difficulty = $sim['difficulty'] ?? 'Intermediate';
            $tags = $sim['tags'] ?? [];
            $equations = $sim['equations'] ?? [];
            $primaryEq = !empty($equations) ? $equations[0] : null;

            // Difficulty Color Tag
            $diffColor = '#38bdf8'; // blue
            $diffBg = 'rgba(56, 189, 248, 0.12)';
            if (stripos($difficulty, 'Introductory') !== false) {
                $diffColor = '#34d399'; // green
                $diffBg = 'rgba(52, 211, 153, 0.12)';
            } elseif (stripos($difficulty, 'Advanced') !== false) {
                $diffColor = '#fbbf24'; // amber
                $diffBg = 'rgba(251, 191, 36, 0.12)';
            } elseif (stripos($difficulty, 'Graduate') !== false || stripos($difficulty, 'Relativistic') !== false) {
                $diffColor = '#c084fc'; // purple
                $diffBg = 'rgba(192, 132, 252, 0.12)';
            }

            // Engine Tag
            $isWebGL = stripos($engine, 'WebGL') !== false;
            $engineColor = $isWebGL ? '#ec4899' : '#0ea5e9';
            $engineBg = $isWebGL ? 'rgba(236, 72, 153, 0.12)' : 'rgba(14, 165, 233, 0.12)';
        ?>
        <a 
            href="/physics/simulations/<?= htmlspecialchars($sim['slug']) ?>" 
            class="topic-card <?= $meta['class'] ?> sim-card"
            data-category="<?= htmlspecialchars($catSlug) ?>"
            data-slug="<?= htmlspecialchars($sim['slug']) ?>"
            data-title="<?= htmlspecialchars(strtolower($sim['title'])) ?>"
            data-desc="<?= htmlspecialchars(strtolower($sim['description'])) ?>"
            data-keywords="<?= htmlspecialchars(strtolower(implode(' ', $tags) . ' ' . $engine . ' ' . $difficulty . ' ' . ($primaryEq ?? ''))) ?>"
            style="min-height: 380px; justify-content: flex-start;"
        >
            <div class="card-watermark">
                <?= $meta['svg'] ?>
            </div>

            <!-- Card Header -->
            <div class="topic-card-header">
                <?= $meta['svg'] ?>
                <div>
                    <h3 style="margin: 0 0 6px 0;"><?= htmlspecialchars($sim['title']) ?></h3>
                    <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                        <span style="background: <?= $engineBg ?>; color: <?= $engineColor ?>; border: 1px solid <?= $engineColor ?>40; border-radius: 4px; padding: 2px 7px; font-size: 0.72rem; font-weight: 600;">
                            <?= htmlspecialchars($engine) ?>
                        </span>
                        <span style="background: <?= $diffBg ?>; color: <?= $diffColor ?>; border: 1px solid <?= $diffColor ?>40; border-radius: 4px; padding: 2px 7px; font-size: 0.72rem; font-weight: 600;">
                            <?= htmlspecialchars($difficulty) ?>
                        </span>
                    </div>
                </div>
            </div>

            <!-- Description -->
            <p style="margin: 12px 0 16px 0; flex-grow: 0;"><?= htmlspecialchars($sim['description']) ?></p>

            <!-- Mathematical Scaffolding Callout Box -->
            <?php if ($primaryEq): ?>
            <div class="sim-card-equation-box" style="background: rgba(2, 6, 23, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 16px; font-size: 0.88rem; overflow-x: auto;">
                <div style="font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 4px; font-weight: 600;">
                    Governing Equation
                </div>
                <div class="sim-math-token" style="color: #ffd700; text-align: center;">
                    \[ <?= $primaryEq ?> \]
                </div>
            </div>
            <?php endif; ?>

            <!-- Pedagogical Tags Row -->
            <?php if (!empty($tags)): ?>
            <div style="display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 16px; margin-top: auto;">
                <?php foreach ($tags as $tag): ?>
                <span style="background: rgba(255, 255, 255, 0.04); color: var(--text-muted); border-radius: 4px; padding: 2px 6px; font-size: 0.72rem;">
                    #<?= htmlspecialchars($tag) ?>
                </span>
                <?php endforeach; ?>
            </div>
            <?php endif; ?>

            <!-- Launch Sandbox Footer Button -->
            <span class="read-more" style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 12px; margin-top: auto;">
                <span>Launch Interactive Sandbox</span>
                <span style="font-size: 1.1rem; transition: transform 0.2s;">&rarr;</span>
            </span>
        </a>
        <?php endforeach; ?>
    </section>

    <!-- Empty State when filter yields 0 matches -->
    <div id="sim-no-results" style="display: none; text-align: center; padding: 60px 20px; background: rgba(15, 23, 42, 0.4); border-radius: 16px; border: 1px dashed rgba(255, 255, 255, 0.12); margin-top: 20px;">
        <span style="font-size: 2.8rem; display: block; margin-bottom: 12px;">🔭</span>
        <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.3rem;">No simulation engines matched your filter</h3>
        <p style="color: var(--text-muted); font-size: 0.95rem; margin: 0 0 18px 0; max-width: 480px; margin-left: auto; margin-right: auto;">
            Try adjusting your search query or domain category pill to explore other physical systems.
        </p>
        <button id="sim-reset-filters-btn" class="btn btn-secondary" style="background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(255, 255, 255, 0.15); color: #fff; padding: 8px 18px; border-radius: 8px; cursor: pointer;">
            Reset All Filters
        </button>
    </div>
</div>

<!-- ===================================================================== -->
<!-- CLIENT-SIDE OBSERVATORY FILTERING & SEARCH CONTROLLER                 -->
<!-- ===================================================================== -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('sim-search-input');
    const filterPills = document.querySelectorAll('.sim-filter-pill');
    const cards = document.querySelectorAll('.sim-card');
    const countBadge = document.getElementById('sim-visible-count');
    const noResults = document.getElementById('sim-no-results');
    const resetBtn = document.getElementById('sim-reset-filters-btn');

    let activeCategory = 'all';
    let searchQuery = '';

    function applyFilters() {
        let visibleCount = 0;
        const query = searchQuery.trim().toLowerCase();

        cards.forEach(card => {
            const cardCat = card.getAttribute('data-category');
            const cardTitle = card.getAttribute('data-title') || '';
            const cardDesc = card.getAttribute('data-desc') || '';
            const cardKeywords = card.getAttribute('data-keywords') || '';
            const cardSlug = card.getAttribute('data-slug') || '';

            const matchesCategory = (activeCategory === 'all' || cardCat === activeCategory);
            const matchesSearch = !query || 
                cardTitle.includes(query) || 
                cardDesc.includes(query) || 
                cardKeywords.includes(query) || 
                cardSlug.includes(query);

            if (matchesCategory && matchesSearch) {
                card.classList.remove('hidden');
                visibleCount++;
            } else {
                card.classList.add('hidden');
            }
        });

        if (countBadge) {
            countBadge.textContent = visibleCount;
        }

        if (noResults) {
            noResults.style.display = (visibleCount === 0) ? 'block' : 'none';
        }
    }

    // Category Pill Clicks
    filterPills.forEach(pill => {
        pill.addEventListener('click', function() {
            filterPills.forEach(p => {
                p.classList.remove('active');
                p.style.background = 'rgba(255, 255, 255, 0.04)';
                p.style.color = 'var(--text-muted)';
                p.style.borderColor = 'rgba(255, 255, 255, 0.08)';
            });

            this.classList.add('active');
            this.style.background = 'rgba(56, 189, 248, 0.15)';
            this.style.color = '#38bdf8';
            this.style.borderColor = 'rgba(56, 189, 248, 0.4)';

            activeCategory = this.getAttribute('data-category') || 'all';
            applyFilters();
        });
    });

    // Real-Time Search Typing
    if (searchInput) {
        searchInput.addEventListener('input', function(e) {
            searchQuery = e.target.value;
            applyFilters();
        });
    }

    // Reset Filters Button
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (searchInput) searchInput.value = '';
            searchQuery = '';
            const allPill = document.querySelector('.sim-filter-pill[data-category="all"]');
            if (allPill) allPill.click();
        });
    }

    // Ensure MathJax renders formulas cleanly in cards
    if (window.MathJax && MathJax.typesetPromise) {
        MathJax.typesetPromise();
    }
});
</script>

<script src="/js/observatory_hero.js" defer></script>
