<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title ?? 'Physics Lab') ?> - Terra</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- MathJax Static-Safe Configuration -->
    <script src="/js/mathjax_config.js" nonce="<?= $nonce ?>"></script>
    <script src="/js/math_prose_formatter.js" nonce="<?= $nonce ?>"></script>
    <script src="/js/lib/tex-svg-full.js" id="MathJax-script" nonce="<?= $nonce ?>" defer></script>
    <script src="/js/hub_interactions.js" nonce="<?= $nonce ?>"></script>
    <link rel="stylesheet" href="/css/physics.css?v=<?= @filemtime(PROJECT_ROOT . '/public/css/physics.css') ?: 1 ?>">
    <script nonce="<?= $nonce ?>">
        const BASE_URL = '<?= (Flight::request()->base && Flight::request()->base !== '.') ? rtrim(Flight::request()->base, '/') : '' ?>';
    </script>
</head>
<body class="physics-lab">

    <?php if ($is_preview ?? false): ?>
        <div class="preview-banner">
            PREVIEW MODE ACTIVE: Viewing changes from sharded JSON files 
            &nbsp;&nbsp;|&nbsp;&nbsp; 
            <a href="?preview=0">Exit Preview</a>
        </div>
    <?php endif; ?>

    <header class="main-header">
        <div class="container nav-wrapper">
            <a href="/physics" class="logo">Physics Lab</a>
            
            <div class="search-trigger-container">
                <button id="search-modal-trigger" class="search-modal-trigger">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span>Search...</span>
                    <kbd class="shortcut">⌘K</kbd>
                </button>
            </div>

            <?php
            $topicAccentColors = [
                'classical-mechanics' => 'var(--accent-classical)',
                'electromagnetism' => 'var(--accent-electromagnetism)',
                'relativity' => 'var(--accent-relativity)',
                'quantum-physics' => 'var(--accent-quantum)',
                'astrophysics' => 'var(--accent-astrophysics)',
                'thermodynamics-statistical-mechanics' => 'var(--accent-thermodynamics)',
                'fluids-nonlinear' => 'var(--accent-fluids)',
                'condensed-matter' => 'var(--accent-condensed)',
                'condensed-matter-optics' => 'var(--accent-condensed)',
                'standard-model' => 'var(--accent-standard-model)',
                'particle-nuclear-physics' => 'var(--accent-standard-model)',
                'theoretical-physics' => 'var(--accent-theoretical)',
                'quantum-field-theory-high-energy' => 'var(--accent-theoretical)',
                'mathematical-methods' => 'var(--accent-math-methods)',
                'mathematical-methods-computational' => 'var(--accent-math-methods)',
                'philosophy-of-physics' => 'var(--accent-philosophy)',
                'foundations-philosophy-of-physics' => 'var(--accent-philosophy)',
                'legacy-orphans' => 'var(--accent-default)',
                'biophysics-complex-systems' => 'var(--accent-default)',
            ];
            $flagshipSimSlugs = ['relativistic-black-hole', 'pendulum', 'projectile-motion'];

            $reqUrl = parse_url(Flight::request()->url ?? '', PHP_URL_PATH) ?: '';
            $isTopicsActive = (bool)preg_match('#^/physics/(?:topic|subtopic)(?:/|$)#', $reqUrl);
            $isSimsActive = (bool)preg_match('#^/physics/simulations(?:/|$)#', $reqUrl);
            $isLabActive = (bool)preg_match('#^/physics/(?:lab-tools|legendre-transformer|noethers-vault|correspondence-workspace|notation-toggle|anthropic-tuner|equation-explainer|universe-graph|constants|symbols)(?:/|$)#', $reqUrl);
            ?>
            <nav class="primary-nav-bar" aria-label="Main Navigation">
                <!-- 1. TOPICS PILLAR -->
                <div class="dropdown" data-nav-pillar="topics">
                    <a href="/physics" class="dropbtn btn btn-secondary<?= $isTopicsActive ? ' nav-pillar-active' : '' ?>">Topics <span class="nav-caret">&blacktriangledown;</span></a>
                    <div class="dropdown-content dropdown-mega dropdown-mega-topics">
                        <?php $pillarCount = !empty($menu_topics) ? count($menu_topics) : 12; ?>
                        <div class="mega-section-label"><?= $pillarCount ?> Encyclopedia Pillar Hubs</div>
                        <div class="mega-topics-grid">
                            <?php foreach ($menu_topics as $slug => $topic):
                                $dotColor = $topicAccentColors[$slug] ?? 'var(--accent-default)';
                                $isCurrentTopic = ($reqUrl === '/physics/topic/' . $slug);
                            ?>
                                <a href="/physics/topic/<?= htmlspecialchars($slug) ?>" class="mega-topic-item<?= $isCurrentTopic ? ' is-current' : '' ?>" style="--topic-dot-color: <?= $dotColor ?>;">
                                    <span class="topic-color-dot" style="background: <?= $dotColor ?>; box-shadow: 0 0 8px <?= $dotColor ?>;"></span>
                                    <span class="topic-item-title"><?= $topic['title'] ?></span>
                                </a>
                            <?php endforeach; ?>
                        </div>
                        <div class="mega-dropdown-footer">
                            <a href="/physics/random" class="mega-footer-link">🎲 Random Subtopic</a>
                            <a href="/physics" class="mega-footer-link accent">🌌 View All <?= $pillarCount ?> Pillars &rarr;</a>
                        </div>
                    </div>
                </div>

                <!-- 2. SIMULATIONS PILLAR -->
                <div class="dropdown" data-nav-pillar="simulations">
                    <a href="/physics/simulations" class="dropbtn btn btn-simulations-nav<?= $isSimsActive ? ' nav-pillar-active' : '' ?>">Simulations <span class="nav-caret">&blacktriangledown;</span></a>
                    <div class="dropdown-content dropdown-mega dropdown-mega-sims">
                        <a href="/physics/simulations" class="mega-featured-banner sims-banner">
                            <div class="banner-top-row">
                                <span class="banner-title">🔭 The Simulations Observatory</span>
                                <span class="banner-cta">Explore All &rarr;</span>
                            </div>
                            <span class="banner-desc"><?= count($menu_simulations ?: []) ?: 16 ?> Real-Time Numerical Solvers, RK4 Integrators &amp; WebGL2 GPU Sandboxes</span>
                        </a>

                        <div class="mega-section-label">Flagship Elevated Sandboxes</div>
                        <div class="mega-flagship-sims">
                            <a href="/physics/simulations/relativistic-black-hole" class="nav-module-link<?= $reqUrl === '/physics/simulations/relativistic-black-hole' ? ' is-current' : '' ?>">
                                <span class="module-title">🌌 Relativistic Kerr Black Hole</span>
                                <span class="module-desc">WebGL2 GPU null geodesic raytracer, Doppler beaming &amp; accretion disk</span>
                            </a>
                            <a href="/physics/simulations/pendulum" class="nav-module-link<?= $reqUrl === '/physics/simulations/pendulum' ? ' is-current' : '' ?>">
                                <span class="module-title">⏳ Chaotic Driven Pendulum</span>
                                <span class="module-desc">RK4 nonlinear solver with real-time Poincaré phase sections</span>
                            </a>
                            <a href="/physics/simulations/projectile-motion" class="nav-module-link<?= $reqUrl === '/physics/simulations/projectile-motion' ? ' is-current' : '' ?>">
                                <span class="module-title">🚀 Projectile &amp; Newton's Cannon</span>
                                <span class="module-desc">Sub-orbital kinematics, circular orbits &amp; escape trajectories</span>
                            </a>
                        </div>

                        <?php if (!empty($menu_simulations)): ?>
                            <div class="mega-section-label" style="margin-top: 6px;">Interactive Sandbox Directory</div>
                            <div class="mega-sims-directory-grid">
                                <?php foreach ($menu_simulations as $simSlug => $sim):
                                    if (in_array($simSlug, $flagshipSimSlugs, true)) continue;
                                    $isCurrentSim = ($reqUrl === '/physics/simulations/' . $simSlug);
                                ?>
                                    <a href="/physics/simulations/<?= htmlspecialchars($simSlug) ?>" class="mega-sim-pill<?= $isCurrentSim ? ' is-current' : '' ?>">
                                        <?= $sim['title'] ?>
                                    </a>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>

                <!-- 3. LAB TOOLS PILLAR -->
                <div class="dropdown" data-nav-pillar="lab-tools">
                    <a href="/physics/lab-tools" class="dropbtn btn btn-primary<?= $isLabActive ? ' nav-pillar-active' : '' ?>">Lab Tools <span class="nav-caret">&blacktriangledown;</span></a>
                    <div class="dropdown-content dropdown-content-tertiary dropdown-mega dropdown-mega-lab">
                        <a href="/physics/lab-tools" class="mega-featured-banner lab-banner">
                            <div class="banner-top-row">
                                <span class="banner-title">⚡ Unified Physics Cockpit &amp; Cosmic Arena</span>
                                <span class="banner-cta">Launch Lab &rarr;</span>
                            </div>
                            <span class="banner-desc">6 Physical Systems &bull; 5 Transformation Prisms &bull; Live SymPy CAS</span>
                        </a>

                        <div class="mega-two-col">
                            <div class="mega-col">
                                <div class="mega-section-label">Analytical &amp; Duality Workbenches</div>
                                <a href="/physics/legendre-transformer" class="nav-module-link<?= $reqUrl === '/physics/legendre-transformer' ? ' is-current' : '' ?>">
                                    <span class="module-title">Analytical Mechanics Workbench</span>
                                    <span class="module-desc">SymPy CAS Lagrangian &harr; Hamiltonian Legendre mapping</span>
                                </a>
                                <a href="/physics/noethers-vault" class="nav-module-link<?= $reqUrl === '/physics/noethers-vault' ? ' is-current' : '' ?>">
                                    <span class="module-title">The Symmetry Playground</span>
                                    <span class="module-desc">Noether's Vault: Lie symmetries &amp; conserved currents <em>J<sup>&mu;</sup></em></span>
                                </a>
                                <a href="/physics/correspondence-workspace" class="nav-module-link<?= $reqUrl === '/physics/correspondence-workspace' ? ' is-current' : '' ?>">
                                    <span class="module-title">Quantum-to-Classical Bridge</span>
                                    <span class="module-desc">Correspondence Workspace: Ehrenfest &amp; Wigner flow</span>
                                </a>
                                <a href="/physics/notation-toggle" class="nav-module-link<?= $reqUrl === '/physics/notation-toggle' ? ' is-current' : '' ?>">
                                    <span class="module-title">The Rosetta Stone</span>
                                    <span class="module-desc">Notation Toggle: Vectors &harr; Tensors &harr; Differential Forms</span>
                                </a>
                                <a href="/physics/anthropic-tuner" class="nav-module-link<?= $reqUrl === '/physics/anthropic-tuner' ? ' is-current' : '' ?>">
                                    <span class="module-title">The Multiverse Creator</span>
                                    <span class="module-desc">Anthropic Tuner: Cosmological dials (<em>G, c, &hbar;, &alpha;</em>)</span>
                                </a>
                            </div>

                            <div class="mega-col">
                                <div class="mega-section-label">Manifold Explorers &amp; Registers</div>
                                <a href="/physics/equation-explainer" class="nav-module-link<?= $reqUrl === '/physics/equation-explainer' ? ' is-current' : '' ?>">
                                    <span class="module-title">Equation Explainer</span>
                                    <span class="module-desc">Deconstruct LaTeX identities, dimensions &amp; CAS proofs</span>
                                </a>
                                <a href="/physics/universe-graph" class="nav-module-link<?= $reqUrl === '/physics/universe-graph' ? ' is-current' : '' ?>">
                                    <span class="module-title">Physics Universe Graph</span>
                                    <span class="module-desc">14,683-formula derivation DAG &amp; shortest-path solver</span>
                                </a>
                                <a href="/physics/constants" class="nav-module-link<?= $reqUrl === '/physics/constants' ? ' is-current' : '' ?>">
                                    <span class="module-title">Fundamental Physical Constants</span>
                                    <span class="module-desc">Exact SI values, uncertainties &amp; dimensional groups</span>
                                </a>
                                <a href="/physics/symbols" class="nav-module-link<?= $reqUrl === '/physics/symbols' ? ' is-current' : '' ?>">
                                    <span class="module-title">Symbols &amp; Manifold Lexicon</span>
                                    <span class="module-desc">Tensor indices, differential operators &amp; field notation</span>
                                </a>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- 4. LOCAL DEV STUDIO ADMIN SLOT (Populated dynamically only in local dev studio) -->
                <!-- DEV_STUDIO_NAV_SLOT -->
            </nav>
        </div>
    </header>

    <main class="container">
        <?= $body_content ?>
    </main>

    <footer class="main-footer">
        <p>&copy; <?= date('Y') ?> Physics Lab Digital Encyclopedia. All rights reserved. &nbsp;&bull;&nbsp; <a href="/physics/admin/assess" style="color: var(--text-muted); text-decoration: none; font-size: 0.85rem; transition: color 0.2s;" onmouseover="this.style.color='#64ffda'" onmouseout="this.style.color='var(--text-muted)'">🪐 Assessment Console</a></p>
    </footer>

    <!-- Spotlight Search Modal -->
    <div id="search-modal" class="search-modal">
        <div class="search-modal-backdrop"></div>
        <div class="search-modal-container">
            <div class="search-modal-content">
                <div class="search-modal-header">
                    <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" id="modal-search-input" placeholder="Search equations, topics, and constants..." autocomplete="off">
                    <button class="close-modal-btn">&times;</button>
                </div>
                <div class="search-modal-body">
                    <div class="search-tips">
                        <span>Press <kbd>Esc</kbd> to close</span>
                        <span>Use <kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
                    </div>
                    <div id="modal-search-results" class="modal-search-results">
                        <div class="search-placeholder">
                            <p>Search the mathematical manifold</p>
                            <small>Type to search subtopics, physical constants, or defining equations...</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/js/search_engine.js" nonce="<?= $nonce ?>" defer></script>
    <script src="/js/formula_inspector.js" nonce="<?= $nonce ?>" defer></script>
    <script src="/js/mathjax_inspector.js" nonce="<?= $nonce ?>" defer></script>
    <script src="/js/derivation_accordions.js" nonce="<?= $nonce ?>" defer></script>
    <script nonce="<?= $nonce ?>">
        document.addEventListener('click', function (e) {
            // 1. Dev Role Switcher handler
            const roleBtn = e.target.closest('.dev-role-pill');
            if (roleBtn) {
                e.preventDefault();
                const role = roleBtn.getAttribute('data-dev-role');
                if (!role) return;
                fetch('/physics/api/auth/switch-role', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ role: role })
                })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (data && data.success) {
                        window.location.reload();
                    }
                });
                return;
            }

            // 2. Click-to-pin / caret toggle support for top-right dropdowns
            const caret = e.target.closest('.nav-caret');
            const dropBtn = e.target.closest('.dropdown > .dropbtn');
            if (caret && dropBtn) {
                e.preventDefault();
                const parentDropdown = dropBtn.closest('.dropdown');
                const wasOpen = parentDropdown.classList.contains('is-open');
                document.querySelectorAll('.primary-nav-bar .dropdown.is-open').forEach(function (d) {
                    d.classList.remove('is-open');
                });
                if (!wasOpen) {
                    parentDropdown.classList.add('is-open');
                }
                return;
            }

            // Close any pinned dropdown when clicking outside
            if (!e.target.closest('.primary-nav-bar .dropdown')) {
                document.querySelectorAll('.primary-nav-bar .dropdown.is-open').forEach(function (d) {
                    d.classList.remove('is-open');
                });
            }
        });

        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                document.querySelectorAll('.primary-nav-bar .dropdown.is-open').forEach(function (d) {
                    d.classList.remove('is-open');
                });
            }
        });
    </script>
</body>
</html>