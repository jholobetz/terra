<?php
require_once __DIR__ . '/_topic_icons.php';

// Resolve parent topic slug from breadcrumbs for category-specific theming
$parentSlug = null;
if (!empty($breadcrumbs) && is_array($breadcrumbs)) {
    foreach ($breadcrumbs as $crumb) {
        if (isset($crumb['url']) && strpos($crumb['url'], '/physics/topic/') === 0) {
            $parentSlug = str_replace('/physics/topic/', '', $crumb['url']);
            break;
        }
    }
}

$meta = get_topic_icon_and_class($parentSlug ?? '');
$theme = $meta['theme'] ?? 'default';
?>

<article class="subtopic-content" style="--accent-color: var(--accent-<?= $theme ?>);">
    <nav class="breadcrumb">
        <a href="/physics">Home</a>
        <?php foreach ($breadcrumbs as $crumb): ?>
            <span>&rsaquo;</span>
            <?php if (isset($crumb['is_multi'])): ?>
                <?php foreach ($crumb['links'] as $index => $link): ?>
                    <?= $index > 0 ? ' | ' : '' ?>
                    <a href="<?= htmlspecialchars($link['url']) ?>"><?= $link['title'] ?></a>
                <?php endforeach; ?>
            <?php else: ?>
                <a href="<?= htmlspecialchars($crumb['url']) ?>"><?= $crumb['title'] ?></a>
            <?php endif; ?>
        <?php endforeach; ?>
        <span>&rsaquo;</span>
        <span style="opacity: 1; color: #8892b0;"><?= $title ?></span>
    </nav>

    <header class="subtopic-header">
        <h1><?= $title ?? 'Subtopic' ?></h1>
        <?php if (!empty($verification)): ?>
            <a href="#literature-consensus" class="verification-badge" style="cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; margin-top: 8px; padding: 6px 12px; background: rgba(100, 255, 218, 0.08); border: 1px solid var(--accent-color); border-radius: 4px; font-size: 0.85rem; color: var(--accent-color); font-weight: 500; transition: all 0.2s;" onmouseover="this.style.background='rgba(100, 255, 218, 0.16)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.08)'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <span>Academic Consensus Verified</span>
            </a>
        <?php endif; ?>
    </header>
    
    <div class="content-body">
        <?= $content ?? '<p>No content available for this subtopic.</p>' ?>
    </div>

    <?php $this->render('physics/_equations_partial', [
        'equations' => $equations ?? [],
        'breakdowns' => $breakdowns ?? [],
        'formulas' => $formulas ?? [],
        'nonce' => $nonce,
        'subtopicSlug' => $slug,
        'domain' => $parentSlug
    ]); ?>

    <?php if (!empty($verification)): ?>
        <section id="literature-consensus" class="verification-section" style="margin-top: 50px; padding: 25px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.45) 0%, rgba(3, 7, 18, 0.6) 100%); border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid var(--accent-color); border-radius: 8px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);">
            <h3 style="color: #ccd6f6; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'Space Grotesk', sans-serif;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 4px var(--accent-color));"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <span style="background: linear-gradient(90deg, #f1f5f9 0%, #94a3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Scientific Accreditation & Literature Consensus</span>
            </h3>
            
            <p style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
                This topic has been audited and stamped by the automated physics-lab multi-agent verification system. The contents match the consensus of peer-reviewed academic literature with an alignment score of <strong><?= number_format($verification['consensus_score'] * 100, 0) ?>%</strong>.
            </p>
            
            <div class="verification-meta" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid var(--border-color); font-size: 0.85rem; color: var(--text-muted);">
                <div>
                    <strong style="color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Verification Date</strong>
                    <div style="color: #ccd6f6; margin-top: 3px; font-weight: 500;"><?= htmlspecialchars($verification['verified_date']) ?></div>
                </div>
                <div>
                    <strong style="color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Verification Threshold</strong>
                    <div style="color: #ccd6f6; margin-top: 3px; font-weight: 500;">
                        <?= $verification['consensus_score'] >= 0.50 ? '0.50 (Standard / Mathematical)' : '0.35 (Conceptual / Subjective)' ?>
                    </div>
                </div>
                <div>
                    <strong style="color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Audit Agents</strong>
                    <div style="color: #ccd6f6; margin-top: 3px; font-family: monospace; font-size: 0.8rem;">
                        <?= htmlspecialchars($verification['agents']['critic'] ?? 'LiteratureCritic') ?>
                    </div>
                </div>
            </div>

            <?php if (!empty($verification['citations'])): ?>
                <h4 style="color: var(--accent-color); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0; margin-bottom: 16px; font-weight: 600;">Verified References</h4>
                <ul class="citation-list" style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 14px;">
                    <?php foreach ($verification['citations'] as $cit): ?>
                        <li style="position: relative; padding-left: 24px; transition: transform 0.2s;" onmouseover="this.style.transform='translateX(4px)'" onmouseout="this.style.transform='none'">
                            <span style="position: absolute; left: 0; top: 1px; color: var(--accent-color); font-size: 1.2rem; line-height: 1;">&bull;</span>
                            <div style="font-size: 0.95rem; color: #ccd6f6; font-weight: 500; line-height: 1.4;">
                                <?php if (!empty($cit['url'])): ?>
                                    <a href="<?= htmlspecialchars($cit['url']) ?>" target="_blank" rel="noopener noreferrer" style="color: #ccd6f6; text-decoration: none; border-bottom: 1px dashed rgba(100, 255, 218, 0.4); transition: all 0.2s;" onmouseover="this.style.color='var(--accent-color)'; this.style.borderBottomColor='var(--accent-color)'" onmouseout="this.style.color='#ccd6f6'; this.style.borderBottomColor='rgba(100, 255, 218, 0.4)'">
                                        <?= htmlspecialchars($cit['title']) ?>
                                    </a>
                                <?php else: ?>
                                    <?= htmlspecialchars($cit['title']) ?>
                                <?php endif; ?>
                            </div>
                            <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 4px;">
                                By <?= htmlspecialchars(implode(', ', (array)($cit['authors'] ?? []))) ?>
                                <?php if (!empty($cit['doi'])): ?>
                                    &middot; DOI: <span style="font-family: monospace; opacity: 0.8;"><?= htmlspecialchars($cit['doi']) ?></span>
                                <?php endif; ?>
                            </div>
                        </li>
                    <?php endforeach; ?>
                </ul>
            <?php endif; ?>
        </section>
    <?php endif; ?>

    <?php if (!empty($related_topics)): ?>
        <section class="related-topics" style="margin-top: 50px; padding-top: 30px; border-top: 1px solid #233554;">
            <h3 style="color: #ccd6f6; margin-bottom: 20px;">Further Exploration</h3>
            <div class="related-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <?php foreach ($related_topics as $rel): ?>
                    <a href="/physics/subtopic/<?= $rel['slug'] ?>" class="related-card">
                        <strong><?= $rel['title'] ?></strong>
                        <span>Dive deeper into the related theoretical framework.</span>
                    </a>
                <?php endforeach; ?>
            </div>
        </section>
    <?php endif; ?>

    <footer class="subtopic-footer" style="margin-top: 40px;">
        <?php if (!empty($breadcrumbs)): 
            $lastCrumb = end($breadcrumbs);
        ?>
            <a href="<?= htmlspecialchars($lastCrumb['url']) ?>" class="btn btn-secondary">&larr; Back to <?= $lastCrumb['title'] ?></a>
        <?php endif; ?>
    </footer>
</article>
