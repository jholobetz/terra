<?php
// Map slugs to classes and custom SVG icons
function get_topic_icon_and_class(string $slug): array {
    switch ($slug) {
        case 'classical-mechanics':
            return [
                'class' => 'card-classical',
                'svg' => '
                    <svg viewBox="0 0 100 100" class="card-icon">
                        <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="1.2" fill="none" stroke-dasharray="3 3" opacity="0.3"/>
                        <ellipse cx="50" cy="50" rx="40" ry="12" stroke="currentColor" stroke-width="1.2" fill="none" transform="rotate(-30 50 50)"/>
                        <ellipse cx="50" cy="50" rx="40" ry="12" stroke="currentColor" stroke-width="1.2" fill="none" transform="rotate(60 50 50)" opacity="0.4"/>
                        <line x1="50" y1="10" x2="50" y2="90" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                        <circle cx="50" cy="50" r="4" fill="currentColor"/>
                        <line x1="50" y1="50" x2="78" y2="34" stroke="var(--accent-classical)" stroke-width="2"/>
                    </svg>'
            ];
        case 'electromagnetism':
            return [
                'class' => 'card-electromagnetism',
                'svg' => '
                    <svg viewBox="0 0 100 100" class="card-icon">
                        <path d="M 50 20 C 10 20, 10 80, 50 80" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                        <path d="M 50 20 C 90 20, 90 80, 50 80" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                        <path d="M 50 10 C -10 10, -10 90, 50 90" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.2"/>
                        <path d="M 50 10 C 110 10, 110 90, 50 90" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.2"/>
                        <rect x="45" y="30" width="10" height="40" rx="3" fill="currentColor" opacity="0.1"/>
                        <line x1="50" y1="23" x2="50" y2="77" stroke="currentColor" stroke-width="2"/>
                        <path d="M 33 50 Q 41.5 40, 50 50 T 67 50" fill="none" stroke="var(--accent-electromagnetism)" stroke-width="2" stroke-linecap="round"/>
                        <circle cx="50" cy="23" r="3" fill="#ef4444"/>
                        <circle cx="50" cy="77" r="3" fill="#3b82f6"/>
                    </svg>'
            ];
        case 'relativity':
            return [
                'class' => 'card-relativity',
                'svg' => '
                    <svg viewBox="0 0 100 100" class="card-icon">
                        <path d="M 10 50 Q 50 75, 90 50" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                        <path d="M 10 60 Q 50 85, 90 60" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                        <path d="M 10 40 Q 50 65, 90 40" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                        <path d="M 50 10 Q 75 50, 50 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"/>
                        <path d="M 40 10 Q 65 50, 40 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                        <path d="M 60 10 Q 85 50, 60 90" fill="none" stroke="currentColor" stroke-width="1" opacity="0.2"/>
                        <polygon points="50,50 30,22 70,22" fill="rgba(139, 92, 246, 0.1)" stroke="currentColor" stroke-width="1.2"/>
                        <polygon points="50,50 30,78 70,78" fill="rgba(139, 92, 246, 0.05)" stroke="currentColor" stroke-width="1.2" opacity="0.5"/>
                        <circle cx="50" cy="50" r="3" fill="var(--accent-relativity)"/>
                    </svg>'
            ];
        case 'quantum-physics':
            return [
                'class' => 'card-quantum',
                'svg' => '
                    <svg viewBox="0 0 100 100" class="card-icon">
                        <path d="M 10 50 C 25 50, 30 20, 35 50 C 40 80, 45 10, 50 50 C 55 90, 60 20, 65 50 C 70 80, 75 50, 90 50" fill="none" stroke="currentColor" stroke-width="1.5"/>
                        <path d="M 10 50 Q 50 5, 90 50" fill="none" stroke="var(--accent-quantum)" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.5"/>
                        <path d="M 10 50 Q 50 95, 90 50" fill="none" stroke="var(--accent-quantum)" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.5"/>
                        <circle cx="50" cy="50" r="3" fill="currentColor"/>
                        <circle cx="43" cy="35" r="2" fill="currentColor" opacity="0.6"/>
                        <circle cx="57" cy="65" r="2" fill="currentColor" opacity="0.6"/>
                    </svg>'
            ];
        default:
            return [
                'class' => 'card-default',
                'svg' => '
                    <svg viewBox="0 0 100 100" class="card-icon">
                        <polygon points="50,15 80,35 80,65 50,85 20,65 20,35" fill="none" stroke="currentColor" stroke-width="1.2"/>
                        <line x1="50" y1="15" x2="50" y2="85" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                        <line x1="20" y1="35" x2="80" y2="65" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                        <line x1="20" y1="65" x2="80" y2="35" stroke="currentColor" stroke-width="0.8" opacity="0.3"/>
                        <circle cx="50" cy="50" r="7" fill="rgba(0, 210, 255, 0.08)" stroke="currentColor" stroke-width="1.2"/>
                    </svg>'
            ];
    }
}
?>

<section class="hero">
    <canvas id="hero-canvas"></canvas>
    <div class="hero-content">
        <h1><?= htmlspecialchars($title) ?></h1>
        <p class="subtitle"><?= htmlspecialchars($subtitle) ?></p>
        <div class="hero-cta">
            <a href="/physics/topic/classical-mechanics" class="btn btn-primary">Start Exploring</a>
            <a href="/physics/simulations" class="btn btn-secondary">Try Simulations</a>
        </div>
    </div>
</section>

<!-- Metrics Banner -->
<div class="metrics-banner">
    <div class="metric-item">
        <span class="metric-value">1,584</span>
        <span class="metric-label">Graduated Subtopics</span>
    </div>
    <div class="metric-item">
        <span class="metric-value">100%</span>
        <span class="metric-label">Organic Platinum Progress</span>
    </div>
    <div class="metric-item">
        <span class="metric-value">5,892</span>
        <span class="metric-label">Math Identity Locks</span>
    </div>
    <div class="metric-item">
        <span class="metric-value">12</span>
        <span class="metric-label">Active Hub Modules</span>
    </div>
</div>

<section class="topics-grid">
    <?php foreach ($topics as $topic): 
        $meta = get_topic_icon_and_class($topic['slug']);
    ?>
        <a href="/physics/topic/<?= htmlspecialchars($topic['slug']) ?>" class="topic-card <?= $meta['class'] ?>">
            <div class="topic-card-header">
                <?= $meta['svg'] ?>
                <h3><?= $topic['title'] ?></h3>
            </div>
            <p><?= htmlspecialchars($topic['description']) ?></p>
            <span class="read-more">Explore Hub &rarr;</span>
        </a>
    <?php endforeach; ?>
</section>

<!-- Include canvas animation -->
<script src="/js/hero_canvas.js" defer></script>
