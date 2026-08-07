<?php
require_once __DIR__ . '/_topic_icons.php';

// Map topics to landmark equations and subtopic tags for Option 1 Featured Asymmetric Grid
$topicFeatures = [
    'quantum-physics' => [
        'is_featured' => true,
        'badge' => 'QUANTUM REALM',
        'equation' => 'i\hbar \frac{\partial}{\partial t}\Psi = \hat{H}\Psi',
        'tags' => ['Wave Functions', 'Uncertainty Principle', 'Schrödinger Equation', 'Hilbert Spaces']
    ],
    'relativity' => [
        'is_featured' => true,
        'badge' => 'SPACETIME & GRAVITY',
        'equation' => 'R_{\mu\nu} - \frac{1}{2}R g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}',
        'tags' => ['Spacetime Geodesics', 'Schwarzschild Metric', 'Equivalence Principle', 'Gravitational Waves']
    ],
    'classical-mechanics' => [
        'is_featured' => true,
        'badge' => 'FOUNDATIONAL DYNAMICS',
        'equation' => '\frac{d}{dt}\left(\frac{\partial L}{\partial \dot{q}_i}\right) - \frac{\partial L}{\partial q_i} = 0',
        'tags' => ['Lagrangian Formalism', 'Hamiltonian Mechanics', 'Poisson Brackets', 'Kepler Orbits']
    ],
    'electromagnetism' => [
        'equation' => '\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \varepsilon_0 \frac{\partial \mathbf{E}}{\partial t}'
    ],
    'thermodynamics-statistical-mechanics' => [
        'equation' => 'dS \ge \frac{dQ}{T}, \quad S = k_B \ln \Omega'
    ],
    'fluids-nonlinear' => [
        'equation' => '\rho \left(\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}\right) = -\nabla p + \mu \nabla^2 \mathbf{u}'
    ],
    'theoretical-physics' => [
        'equation' => 'S[\phi] = \int d^4x \, \mathcal{L}(\phi, \partial_\mu \phi)'
    ],
    'mathematical-methods' => [
        'equation' => '\hat{f}(\xi) = \int_{-\infty}^{\infty} f(x) e^{-2\pi i x \xi} dx'
    ],
    'standard-model' => [
        'equation' => '\mathcal{L}_{\text{SM}} = -\frac{1}{4}F_{\mu\nu}^a F^{a\mu\nu} + \bar{\psi}i\gamma^\mu D_\mu \psi'
    ],
    'condensed-matter' => [
        'equation' => 'H = -\sum_{\langle i,j \rangle} J_{ij} \sigma_i \sigma_j - h \sum_i \sigma_i'
    ],
    'astrophysics' => [
        'equation' => '\left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{k c^2}{a^2} + \frac{\Lambda c^2}{3}'
    ],
    'philosophy-of-physics' => [
        'equation' => '\langle \hat{A} \rangle = \text{Tr}(\rho \hat{A})'
    ]
];
?>

<section class="hero">
    <canvas id="hero-canvas"></canvas>
    <div class="hero-content">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="subtitle"><?= htmlspecialchars($subtitle) ?></p>

        <!-- Glassmorphic Spotlight Search Bar Overlay -->
        <div style="max-width: 580px; margin: 24px auto 28px;">
            <button id="hero-search-trigger" onclick="document.getElementById('search-modal-trigger').click()" class="search-modal-trigger" style="width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 14px 22px; background: rgba(15, 23, 42, 0.75); backdrop-filter: blur(14px); border: 1px solid rgba(100, 255, 218, 0.35); border-radius: 14px; color: var(--text-color); font-size: 0.95rem; cursor: pointer; transition: all 0.3s ease; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <svg viewBox="0 0 24 24" width="18" height="18" stroke="#64ffda" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span style="color: var(--text-muted);">Search 3,000+ equations, physical constants, or subtopics...</span>
                </div>
                <kbd class="shortcut">⌘K</kbd>
            </button>
        </div>

        <div class="hero-cta">
            <a href="/physics/topic/classical-mechanics" class="btn btn-secondary">Start Exploring</a>
            <a href="/physics/lab-tools" class="btn btn-primary">Lab Tools</a>
        </div>
    </div>
</section>

<!-- Curriculum Dashboard Full Width -->
<div class="dashboard-layout" style="display: block;">
    <div class="dashboard-main" style="width: 100%;">
        <!-- Tabbed Curriculum Navigation -->
        <div class="tabs-container" style="margin-top: 0; margin-bottom: 25px;">
            <button class="tab-btn active" data-domain="all">All Disciplines</button>
            <button class="tab-btn" data-domain="classical">Macroscopic &amp; Classical</button>
            <button class="tab-btn" data-domain="fields">Fields &amp; Covariant</button>
            <button class="tab-btn" data-domain="quantum">Quantum &amp; High-Energy</button>
            <button class="tab-btn" data-domain="space">Space &amp; Cosmology</button>
        </div>
        
        <!-- Asymmetric Featured Grid (Option 1 Full Width) -->
        <div class="topics-grid asymmetric-grid">
            <?php foreach ($topics as $topic): 
                $slug = $topic['slug'];
                $meta = get_topic_icon_and_class($slug);
                $feat = $topicFeatures[$slug] ?? [];
                $isFeatured = $feat['is_featured'] ?? false;
                
                // Map slug to domain group
                $domain = 'classical';
                if (in_array($slug, ['classical-mechanics', 'thermodynamics-statistical-mechanics', 'fluids-nonlinear'])) {
                    $domain = 'classical';
                } elseif (in_array($slug, ['electromagnetism', 'relativity', 'theoretical-physics', 'mathematical-methods'])) {
                    $domain = 'fields';
                } elseif (in_array($slug, ['quantum-physics', 'standard-model', 'condensed-matter', 'philosophy-of-physics'])) {
                    $domain = 'quantum';
                } elseif ($slug === 'astrophysics') {
                    $domain = 'space';
                }
            ?>
                <a href="/physics/topic/<?= htmlspecialchars($slug) ?>" 
                   class="topic-card <?= $meta['class'] ?> <?= $isFeatured ? 'featured-mega-card' : '' ?>" 
                   data-domain="<?= $domain ?>">
                    
                    <div class="card-watermark">
                        <?= $meta['svg'] ?>
                    </div>

                    <!-- Card Header -->
                    <div class="topic-card-header" style="justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <?= $meta['svg'] ?>
                            <h3><?= $topic['title'] ?></h3>
                        </div>
                        <?php if (!empty($feat['badge'])): ?>
                            <span class="mega-badge"><?= $feat['badge'] ?></span>
                        <?php endif; ?>
                    </div>

                    <!-- LaTeX Formula Banner Inset -->
                    <?php if (!empty($feat['equation'])): ?>
                        <div class="card-equation-banner">
                            <span class="math-eq">$$<?= $feat['equation'] ?>$$</span>
                        </div>
                    <?php endif; ?>

                    <p><?= htmlspecialchars($topic['description']) ?></p>

                    <!-- Subtopic Tags (for featured cards) -->
                    <?php if ($isFeatured && !empty($feat['tags'])): ?>
                        <div class="card-tags-row">
                            <?php foreach ($feat['tags'] as $tag): ?>
                                <span class="card-tag-pill"><?= htmlspecialchars($tag) ?></span>
                            <?php endforeach; ?>
                        </div>
                    <?php endif; ?>

                    <span class="read-more">Explore Hub &rarr;</span>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</div>

<!-- Option 1 Card Styling -->
<style>
.asymmetric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
}

@media (max-width: 1100px) {
    .asymmetric-grid {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .asymmetric-grid {
        grid-template-columns: 1fr;
    }
    .featured-mega-card {
        grid-column: span 1 !important;
    }
}

.featured-mega-card {
    grid-column: span 2;
    background: radial-gradient(circle at 0% 0%, rgba(255, 255, 255, 0.04) 0%, rgba(15, 23, 42, 0.5) 100%), var(--card-bg);
    border-width: 1.5px;
}

.mega-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 3px 10px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: var(--text-color);
}

.card-equation-banner {
    margin: 12px 0 6px;
    padding: 10px 16px;
    background: rgba(2, 6, 23, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    text-align: center;
    overflow-x: auto;
    position: relative;
    z-index: 2;
}

.card-equation-banner .mjx-chtml {
    font-size: 1.05rem !important;
    color: var(--accent-color);
}

.card-tags-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin: 12px 0 16px;
    position: relative;
    z-index: 2;
}

.card-tag-pill {
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted);
    transition: all 0.2s ease;
}

.card-tag-pill:hover {
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.3);
}

#hero-search-trigger:hover {
    border-color: #64ffda;
    box-shadow: 0 12px 35px rgba(100, 255, 218, 0.25) !important;
}
</style>

<!-- Scripts -->
<script src="/js/hero_canvas.js" defer></script>
