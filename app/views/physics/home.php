<?php
require_once __DIR__ . '/_topic_icons.php';

// Map topics to landmark equations and neon themes for the 3D Translucent Cubes
$topicCubes = [
    'quantum-physics' => [
        'badge' => 'QUANTUM',
        'theme' => 'var(--accent-quantum)',
        'equation' => 'i\\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi'
    ],
    'relativity' => [
        'badge' => 'RELATIVITY',
        'theme' => 'var(--accent-relativity)',
        'equation' => 'G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}'
    ],
    'classical-mechanics' => [
        'badge' => 'CLASSICAL',
        'theme' => 'var(--accent-classical)',
        'equation' => '\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) = \\frac{\\partial L}{\\partial q_i}'
    ],
    'electromagnetism' => [
        'badge' => 'FIELDS',
        'theme' => 'var(--accent-electromagnetism)',
        'equation' => '\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\frac{1}{c^2} \\frac{\\partial \\mathbf{E}}{\\partial t}'
    ],
    'thermodynamics-statistical-mechanics' => [
        'badge' => 'THERMAL',
        'theme' => 'var(--accent-thermodynamics)',
        'equation' => 'dS \\ge \\frac{dQ}{T}, \\quad S = k_B \\ln \\Omega'
    ],
    'fluids-nonlinear' => [
        'badge' => 'FLUIDS',
        'theme' => 'var(--accent-fluids)',
        'equation' => '\\rho \\frac{D\\mathbf{u}}{Dt} = -\\nabla p + \\mu \\nabla^2 \\mathbf{u}'
    ],
    'theoretical-physics' => [
        'badge' => 'THEORY',
        'theme' => 'var(--accent-theoretical)',
        'equation' => 'S[\\phi] = \\int d^4x \\, \\mathcal{L}(\\phi, \\partial_\\mu \\phi)'
    ],
    'mathematical-methods' => [
        'badge' => 'MATH',
        'theme' => 'var(--accent-math-methods)',
        'equation' => '\\hat{f}(\\xi) = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i x \\xi} dx'
    ],
    'standard-model' => [
        'badge' => 'PARTICLES',
        'theme' => 'var(--accent-standard-model)',
        'equation' => '\\mathcal{L}_{\\text{SM}} = -\\frac{1}{4}F_{\\mu\\nu}^a F^{a\\mu\\nu} + \\bar{\\psi}i\\gamma^\\mu D_\\mu \\psi'
    ],
    'condensed-matter' => [
        'badge' => 'MATTER',
        'theme' => 'var(--accent-condensed)',
        'equation' => 'H = -\\sum_{\\langle i,j \\rangle} J_{ij} \\sigma_i \\sigma_j'
    ],
    'astrophysics' => [
        'badge' => 'COSMOS',
        'theme' => 'var(--accent-astrophysics)',
        'equation' => 'H^2 = \\frac{8\\pi G}{3}\\rho - \\frac{k c^2}{a^2} + \\frac{\\Lambda c^2}{3}'
    ],
    'philosophy-of-physics' => [
        'badge' => 'MIND',
        'theme' => 'var(--accent-philosophy)',
        'equation' => '\\langle \\hat{A} \\rangle = \\text{Tr}(\\rho \\hat{A})'
    ]
];
?>

<!-- Hero Section with Canvas Particles -->
<section class="hero" style="margin-bottom: 20px;">
    <canvas id="hero-canvas"></canvas>
    <div class="hero-content">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="subtitle"><?= htmlspecialchars($subtitle) ?></p>

        <div class="hero-cta" style="margin-top: 24px;">
            <a href="/physics/random" class="btn btn-secondary">🎲 Start Exploring</a>
            <a href="/physics/lab-tools" class="btn btn-primary">Lab Tools</a>
        </div>
    </div>
</section>

<!-- 3D Translucent Glass Cubes Halo Orbit Menu Section -->
<section class="halo-orbit-section" style="margin-top: 20px; margin-bottom: 80px; text-align: center; position: relative;">

    <!-- 3D Halo Orbit Container with Expanded Room -->
    <div id="halo-orbit-container" style="position: relative; width: 100%; height: 520px; margin: 0 auto; perspective: 1200px; cursor: grab; user-select: none; overflow: visible;">
        <!-- Glowing Tilted Wire Ring -->
        <div id="halo-orbit-ring" style="position: absolute; top: 50%; left: 50%; width: 960px; height: 280px; margin-left: -480px; margin-top: -140px; border: 1.5px dashed rgba(100, 255, 218, 0.25); border-radius: 50%; transform: rotateX(72deg); pointer-events: none; box-shadow: 0 0 40px rgba(100, 255, 218, 0.12);"></div>

        <!-- 3D Cubes Wrapper -->
        <div id="halo-cubes-wrapper" style="position: absolute; top: 50%; left: 50%; width: 0; height: 0; transform-style: preserve-3d;">
            <?php foreach ($topics as $topic): 
                $slug = $topic['slug'];
                $meta = get_topic_icon_and_class($slug);
                $cube = $topicCubes[$slug] ?? [];
                $themeColor = $cube['theme'] ?? 'var(--accent-color)';
            ?>
                <!-- Entire 3D Glass Cube is a Clickable Anchor -->
                <a href="/physics/topic/<?= htmlspecialchars($slug) ?>" class="glass-cube" style="--cube-accent: <?= $themeColor ?>;" data-slug="<?= htmlspecialchars($slug) ?>">
                    <!-- 6 Glass Cube Faces -->
                    <div class="cube-face cube-face-front">
                        <div class="cube-badge" style="border-color: <?= $themeColor ?>; color: <?= $themeColor ?>;"><?= $cube['badge'] ?? 'PHYSICS' ?></div>
                        <div class="cube-icon-wrapper"><?= $meta['svg'] ?></div>
                        <h4 class="cube-title"><?= htmlspecialchars($topic['title']) ?></h4>
                        <?php if (!empty($cube['equation'])): ?>
                            <div class="cube-equation-core">
                                <span>$$<?= $cube['equation'] ?>$$</span>
                            </div>
                        <?php endif; ?>
                        <span class="cube-link">Explore Hub &rarr;</span>
                    </div>
                    <div class="cube-face cube-face-back"></div>
                    <div class="cube-face cube-face-left"></div>
                    <div class="cube-face cube-face-right"></div>
                    <div class="cube-face cube-face-top"></div>
                    <div class="cube-face cube-face-bottom"></div>
                </a>
            <?php endforeach; ?>
        </div>
    </div>
</section>

<!-- Option A 3D Translucent Cubes CSS Styling -->
<style>
.glass-cube {
    position: absolute;
    width: 250px;
    height: 210px;
    margin-left: -125px;
    margin-top: -105px;
    transform-style: preserve-3d;
    transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.4s ease;
    text-decoration: none;
    color: inherit;
    display: block;
    cursor: pointer;
}

.cube-face {
    position: absolute;
    width: 100%;
    height: 100%;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1.5px solid var(--cube-accent, var(--accent-color));
    border-radius: 14px;
    box-sizing: border-box;
    box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.03), 0 10px 30px rgba(0,0,0,0.5);
}

.cube-face-front {
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    text-align: center;
    box-sizing: border-box;
    transform: translateZ(20px);
}

.cube-face-back { transform: rotateY(180deg) translateZ(20px); opacity: 0.3; }
.cube-face-left { transform: rotateY(-90deg) translateZ(20px); opacity: 0.2; }
.cube-face-right { transform: rotateY(90deg) translateZ(20px); opacity: 0.2; }
.cube-face-top { transform: rotateX(90deg) translateZ(20px); opacity: 0.2; }
.cube-face-bottom { transform: rotateX(-90deg) translateZ(20px); opacity: 0.2; }

.cube-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    padding: 2px 8px;
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid;
}

.cube-icon-wrapper svg {
    width: 34px;
    height: 34px;
}

.cube-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    color: #ffffff;
    margin: 2px 0;
}

.cube-equation-core {
    background: rgba(2, 6, 23, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 8px;
    width: 100%;
    box-sizing: border-box;
    overflow: hidden;
    scrollbar-width: none;
    -ms-overflow-style: none;
    font-size: 0.82rem;
    color: var(--cube-accent, var(--accent-color));
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
}

.cube-equation-core::-webkit-scrollbar {
    display: none;
}

.cube-equation-core mjx-container {
    margin: 0 !important;
    max-width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

.cube-equation-core mjx-container > svg {
    max-width: 100% !important;
    height: auto !important;
    overflow: visible !important;
}

.cube-link {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--cube-accent, var(--accent-color));
    text-decoration: none;
    transition: opacity 0.2s;
}

.glass-cube.focused .cube-face {
    box-shadow: 0 0 35px var(--cube-accent, var(--accent-color)), inset 0 0 25px rgba(255, 255, 255, 0.1);
    border-color: #ffffff;
}

#hero-search-trigger:hover {
    border-color: #64ffda;
    box-shadow: 0 12px 35px rgba(100, 255, 218, 0.25) !important;
}
</style>

<!-- Scripts -->
<script src="/js/hero_canvas.js" defer></script>
<script src="/js/halo_orbit.js" defer></script>
