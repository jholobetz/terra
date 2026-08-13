<?php
/**
 * Platinum Standard Topic Hub - Unified Dynamic View (Proposal 1 & 2)
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
?>

<article class="topic-content" style="--accent-color: var(--accent-<?= $theme ?>);">
    
    <!-- Proposal 1: Cosmic Command Header -->
    <header class="topic-command-header">
        <div class="topic-header-watermark">
            <?= $meta['svg'] ?>
        </div>

        <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?></div>
        <h1 class="topic-title"><?= htmlspecialchars($title ?? 'Physics Hub') ?></h1>
        <p id="topic-beginning-abstract" class="topic-subtitle"><?= $intro ?? 'Accessing the deep mathematical structure of the physical manifold.' ?></p>

        <!-- Action Bar -->
        <div class="topic-actions-row">
            <a href="/physics/subtopic/<?= htmlspecialchars($slug) ?>-overview" class="btn btn-secondary">🚀 Explore Overview &rarr;</a>
        </div>
    </header>

    <div class="content-body">
        <?php if (!empty($pillars) && is_array($pillars)): ?>
            <!-- Proposal 2: Pillar Navigator Tabs -->
            <div class="pillar-tabs-bar">
                <button class="pillar-tab-btn active" data-pillar-idx="all">All Pillars (<?= count($pillars) ?>)</button>
                <?php foreach ($pillars as $idx => $pillar): ?>
                    <button class="pillar-tab-btn" data-pillar-idx="<?= $idx ?>"><?= ($idx + 1) ?>. <?= htmlspecialchars($pillar['title']) ?></button>
                <?php endforeach; ?>
            </div>

            <!-- DATA-DRIVEN PLATINUM HUB -->
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
                            <div class="concept-card" data-subtopic-slug="<?= htmlspecialchars($slugItem) ?>">
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

            <?php if (!empty($bridges)): ?>
                <div class="bridge-matrix">
                    <div class="bridge-matrix-header">
                        <span class="bridge-badge">INTERDISCIPLINARY</span>
                        <h3>Cross-Disciplinary Bridges</h3>
                    </div>
                    <div class="bridge-grid">
                        <?php foreach ($bridges as $b): ?>
                            <div class="bridge-item">
                                <div class="bridge-item-title">
                                    <?php if (!empty($b['slug'])): ?>
                                        <a href="/physics/topic/<?= $b['slug'] ?>" class="topic-link"><?= htmlspecialchars($b['title']) ?></a>
                                    <?php else: ?>
                                        <?= htmlspecialchars($b['title']) ?>
                                    <?php endif; ?>
                                </div>
                                <p class="bridge-item-desc"><?= htmlspecialchars($b['description']) ?></p>
                            </div>
                        <?php endforeach; ?>
                    </div>
                </div>
            <?php endif; ?>

        <?php else: ?>
            <!-- FALLBACK: CLASSIC STATIC CONTENT -->
            <?= $content ?? '<p>No content available for this topic.</p>' ?>
        <?php endif; ?>
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

    <script id="topic-var-map" type="application/json">
    <?= json_encode($topicVariableMap ?? [], JSON_HEX_TAG | JSON_HEX_AMP | JSON_UNESCAPED_UNICODE) ?>
    </script>

    <footer class="topic-footer">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Home</a>
    </footer>
</article>

<!-- Proposal 2 Pillar Navigator & Interactive 3D Card Tilt Script -->
<script nonce="<?= $nonce ?>">
(function() {
    function handlePillarClick(e) {
        const btn = e.target.closest('.pillar-tab-btn');
        if (!btn) return;

        const targetIdx = btn.getAttribute('data-pillar-idx');
        const container = btn.closest('.topic-content');
        if (!container) return;

        const tabBtns = container.querySelectorAll('.pillar-tab-btn');
        const pillars = container.querySelectorAll('.concept-pillar');

        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        pillars.forEach(pillar => {
            const pillarIdx = pillar.getAttribute('data-pillar-idx');
            if (targetIdx === 'all' || targetIdx === pillarIdx) {
                pillar.style.display = 'block';
            } else {
                pillar.style.display = 'none';
            }
        });
    }

    document.addEventListener('click', handlePillarClick);

    // Interactive 3D Parallax Tilt for Glassmorphic Concept Cards
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
            
            // Max 7 deg tilt
            const tiltX = (center.y / (bounds.height / 2)) * -7;
            const tiltY = (center.x / (bounds.width / 2)) * 7;

            card.style.transform = `perspective(1000px) rotateX(${tiltX.toFixed(2)}deg) rotateY(${tiltY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;
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

<!-- CSS Styling -->
<style>
.topic-command-header {
    position: relative;
    padding: 36px 32px 32px;
    margin-bottom: 30px;
    background: radial-gradient(circle at 50% 0%, rgba(100, 255, 218, 0.12) 0%, rgba(15, 23, 42, 0.6) 80%);
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
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--accent-color, #64ffda);
    margin-bottom: 8px;
    display: inline-block;
}

.topic-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 10px;
    line-height: 1.2;
}

.topic-subtitle {
    font-size: 1.05rem;
    color: var(--text-muted, #94a3b8);
    line-height: 1.6;
    max-width: 820px;
    margin: 0 0 24px;
}

.topic-actions-row {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
}

.pillar-tabs-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 32px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.pillar-tab-btn {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: var(--text-muted, #94a3b8);
    cursor: pointer;
    transition: all 0.25s ease;
}

.pillar-tab-btn:hover {
    color: #ffffff;
    border-color: var(--accent-color, #64ffda);
    background: rgba(15, 23, 42, 0.85);
}

.pillar-tab-btn.active {
    color: #ffffff;
    background: rgba(100, 255, 218, 0.15);
    border-color: var(--accent-color, #64ffda);
    box-shadow: 0 0 15px rgba(100, 255, 218, 0.2);
}
</style>
