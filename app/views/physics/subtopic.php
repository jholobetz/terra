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
    
    <!-- Cosmic Command Header (Uniform with Topic Hub) -->
    <header class="topic-command-header subtopic-command-header">
        <div class="topic-header-watermark">
            <?= $meta['svg'] ?>
        </div>

        <nav class="breadcrumb subtopic-glass-breadcrumb">
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
            <span style="opacity: 1; color: var(--accent-color, #64ffda); font-weight: 500;"><?= htmlspecialchars($title) ?></span>
        </nav>

        <div class="header-badge-tag">FACULTY OF <?= strtoupper(str_replace('-', ' ', $theme)) ?> // MANIFOLD SUBTOPIC</div>
        <h1 class="topic-title"><?= htmlspecialchars($title ?? 'Subtopic') ?></h1>

        <?php if (!empty($verification)): ?>
            <div class="topic-actions-row" style="margin-top: 14px;">
                <a href="#literature-consensus" class="verification-badge" style="cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; padding: 6px 14px; background: rgba(100, 255, 218, 0.08); border: 1px solid var(--accent-color); border-radius: 20px; font-size: 0.8rem; color: var(--accent-color); font-weight: 600; font-family: 'Space Grotesk', sans-serif; letter-spacing: 0.05em; transition: all 0.25s;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'; this.style.boxShadow='0 0 12px rgba(100, 255, 218, 0.3)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.08)'; this.style.boxShadow='none'">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink: 0;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    <span>Academic Consensus Verified (<?= number_format(($verification['consensus_score'] ?? 1.0) * 100, 0) ?>%)</span>
                </a>
            </div>
        <?php endif; ?>
    </header>
    
    <div class="content-body subtopic-prose-card" id="subtopic-main-prose">
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
        <section id="literature-consensus" class="verification-section" style="margin-top: 50px; padding: 28px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.75) 0%, rgba(3, 7, 18, 0.9) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-left: 4px solid var(--accent-color); border-radius: 14px; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px);">
            <h3 style="color: #ccd6f6; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--accent-color)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="filter: drop-shadow(0 0 4px var(--accent-color));"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                <span style="background: linear-gradient(90deg, #f1f5f9 0%, #94a3b8 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Scientific Accreditation & Literature Consensus</span>
            </h3>
            
            <p style="color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px;">
                This topic has been audited and stamped by the automated physics-lab multi-agent verification system. The contents match the consensus of peer-reviewed academic literature with an alignment score of <strong style="color: var(--accent-color);"><?= number_format($verification['consensus_score'] * 100, 0) ?>%</strong>.
            </p>
            
            <div class="verification-meta" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-size: 0.85rem; color: var(--text-muted);">
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
                <h4 style="color: var(--accent-color); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0; margin-bottom: 16px; font-weight: 600; font-family: 'Space Grotesk', sans-serif;">Verified References</h4>
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
        <section class="related-topics" style="margin-top: 50px; padding-top: 30px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px;">
                <h3 style="color: #ffffff; font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; margin: 0; display: flex; align-items: center; gap: 10px;">
                    <span style="color: var(--accent-color, #64ffda);">◈</span> Further Manifold Exploration
                </h3>
                <span style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace; letter-spacing: 0.1em;">CONNECTED SUBTOPICS</span>
            </div>
            <div class="concept-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px;">
                <?php foreach ($related_topics as $rel): ?>
                    <div class="concept-card related-concept-card" data-subtopic-slug="<?= htmlspecialchars($rel['slug']) ?>" style="cursor: pointer;" onclick="window.location.href='/physics/subtopic/<?= htmlspecialchars($rel['slug']) ?>'">
                        <div class="card-glass-sheen"></div>
                        <div class="concept-anchor">
                            <span class="level-tag level-analytical">Analytical</span>
                            <h4><strong><a href="/physics/subtopic/<?= htmlspecialchars($rel['slug']) ?>" class="subtopic-link"><?= htmlspecialchars($rel['title']) ?></a></strong></h4>
                        </div>
                        <div class="concept-detail subtopic-card-abstract">
                            <p>Explore theoretical mechanics, governing equations, and derivation bridges.</p>
                        </div>
                        <div class="concept-card-footer">
                            <span class="explore-subtopic-btn">Explore Deep Dive &rarr;</span>
                        </div>
                    </div>
                <?php endforeach; ?>
            </div>
        </section>
    <?php endif; ?>

    <footer class="subtopic-footer" style="margin-top: 40px; padding-top: 24px; border-top: 1px solid rgba(255, 255, 255, 0.08); display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 16px;">
        <?php if (!empty($breadcrumbs)): 
            $lastCrumb = end($breadcrumbs);
        ?>
            <a href="<?= htmlspecialchars($lastCrumb['url']) ?>" class="btn btn-secondary" style="font-family: 'Space Grotesk', sans-serif;">&larr; Back to <?= $lastCrumb['title'] ?></a>
        <?php endif; ?>
        <a href="/physics/random" class="btn btn-secondary" style="font-family: 'Space Grotesk', sans-serif; color: #64ffda; border-color: rgba(100, 255, 218, 0.3);">🎲 Discover Random Subtopic</a>
    </footer>
</article>

<!-- Floating Glassmorphic Hover Card Container for Option A -->
<!-- Floating Glassmorphic Hover Card Container for Option A -->
<div id="var-hover-card" style="display: none; position: absolute; z-index: 9999; width: 300px; background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(100, 255, 218, 0.3); border-radius: 8px; padding: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(12px); pointer-events: auto;">
    <div id="var-card-header" style="display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 8px; margin-bottom: 8px;">
        <span id="var-card-symbol" style="font-size: 1.1rem; font-weight: 700; color: #64ffda; font-family: 'Fira Code', monospace;"></span>
        <span id="var-card-unit" style="font-size: 0.75rem; color: #8892b0; font-family: monospace;"></span>
    </div>
    <div id="var-card-name" style="font-size: 0.9rem; font-weight: 600; color: #f1f5f9; margin-bottom: 6px;"></div>
    <div id="var-card-desc" style="font-size: 0.8rem; color: #94a3b8; line-height: 1.4; margin-bottom: 10px;"></div>
    <div id="var-card-eqs-title" style="font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64ffda; margin-bottom: 4px;">Subtopic Formulas</div>
    <div id="var-card-eqs-list" style="display: flex; flex-direction: column; gap: 6px; font-size: 0.75rem; color: #cbd5e1;"></div>
</div>

<script<?= $nonce ? ' nonce="' . $nonce . '"' : '' ?>>
window.SUBTOPIC_VARIABLES = <?= json_encode($subtopicVariables ?? [], JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_QUOT | JSON_HEX_AMP) ?>;

document.addEventListener('DOMContentLoaded', () => {
    const vars = window.SUBTOPIC_VARIABLES || {};
    const hoverCard = document.getElementById('var-hover-card');
    if (!hoverCard || Object.keys(vars).length === 0) return;

    const cardSym = document.getElementById('var-card-symbol');
    const cardUnit = document.getElementById('var-card-unit');
    const cardName = document.getElementById('var-card-name');
    const cardDesc = document.getElementById('var-card-desc');
    const cardEqsList = document.getElementById('var-card-eqs-list');

    let isOverNode = false;
    let isOverCard = false;

    function updateCardVisibility() {
        if (isOverNode || isOverCard) {
            hoverCard.style.display = 'block';
        } else {
            hoverCard.style.display = 'none';
        }
    }

    hoverCard.addEventListener('mouseenter', () => {
        isOverCard = true;
        updateCardVisibility();
    });

    hoverCard.addEventListener('mouseleave', () => {
        isOverCard = false;
        updateCardVisibility();
    });

    // Helper: Clean TeX string to extract core variable symbol key (single variable tokens only)
    function getSymbolKeyFromTex(tex) {
        if (!tex) return null;
        let clean = tex.trim();
        // Skip equations or complex relational expressions
        if (clean.includes('=') || clean.includes('\\int') || clean.includes('\\sum') || clean.includes('\\prod') || clean.includes('\\frac')) {
            return null;
        }
        clean = clean.replace(/\\(mathbf|vec|hat|tilde|mathrm|boldsymbol)\{([^}]+)\}/g, '$2');
        clean = clean.replace(/[\$\\{\}]/g, '').trim();
        if (/^-?\d+(\.\d+)?$/.test(clean)) return null;
        
        if (vars[clean]) return clean;
        const base = clean.split('_')[0].trim();
        if (vars[base]) return base;

        return null;
    }

    // Helper to populate and typeset hover card content with MathJax
    function populateHoverCard(data, symKey) {
        const rawSym = data.symbol || data.display_symbol || symKey;
        const formattedSym = (rawSym.indexOf('\\(') !== -1 || rawSym.indexOf('$') !== -1) ? rawSym : `\\(${rawSym}\\)`;
        cardSym.innerHTML = formattedSym;
        cardUnit.textContent = data.unit ? `[${data.unit}]` : '';
        cardName.textContent = data.name || symKey;
        cardDesc.textContent = data.description || '';

        cardEqsList.innerHTML = '';
        if (data.equations && data.equations.length > 0) {
            data.equations.forEach(eq => {
                const d = document.createElement('div');
                d.style.cssText = 'background: rgba(255,255,255,0.05); padding: 6px 8px; border-radius: 4px; border-left: 2px solid #64ffda; display: flex; flex-direction: column; gap: 4px;';
                const rawEq = eq.equation || '';
                const formattedEq = (rawEq.indexOf('\\(') !== -1 || rawEq.indexOf('$') !== -1) ? rawEq : `\\(${rawEq}\\)`;
                const baseUrl = (typeof BASE_URL !== 'undefined') ? BASE_URL : '';
                const explainerUrl = baseUrl + `/physics/equation-explainer?latex=${encodeURIComponent(rawEq)}${eq.id ? '&id=' + encodeURIComponent(eq.id) : ''}`;
                d.innerHTML = `
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                        <span style="font-weight:600; color:#e2e8f0; font-size:0.75rem;">${eq.title}:</span>
                        <a href="${explainerUrl}" class="explainer-link-btn" style="font-size: 0.68rem; font-weight: 600; color: #64ffda; text-decoration: none; border: 1px solid rgba(100, 255, 218, 0.3); padding: 1px 6px; border-radius: 4px; background: rgba(100, 255, 218, 0.08); transition: all 0.2s;" onmouseover="this.style.background='rgba(100, 255, 218, 0.2)'" onmouseout="this.style.background='rgba(100, 255, 218, 0.08)'">Analyze &rarr;</a>
                    </div>
                    <div style="color:#64ffda; font-size:0.8rem;">${formattedEq}</div>
                `;
                cardEqsList.appendChild(d);
            });
        } else {
            cardEqsList.innerHTML = '<span style="opacity: 0.6; font-style: italic;">No specific formulas listed</span>';
        }

        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([cardSym, cardEqsList]).catch(err => console.warn('MathJax hover card typeset warning:', err));
        }
    }

    const mainProse = document.getElementById('subtopic-main-prose');
    if (mainProse) {
        // Query all inline math SVGs or data-tex containers in subtopic prose
        const mathNodes = mainProse.querySelectorAll('svg[data-tex], [data-tex]');
        
        mathNodes.forEach(node => {
            // Option 2: Skip nodes inside standalone display equation cards/containers
            if (node.closest('.formula-card, .equation-card, .display-math, [display="true"]')) {
                return;
            }

            const tex = node.getAttribute('data-tex');
            const symKey = getSymbolKeyFromTex(tex);
            
            if (symKey && vars[symKey]) {
                // Style as interactive variable token
                node.classList.add('var-math-token');
                node.setAttribute('data-sym', symKey);
                node.style.cursor = 'pointer';
                node.style.borderBottom = '1.5px dotted #64ffda';
                node.style.borderRadius = '2px';
                node.style.transition = 'all 0.2s';

                // Option A Hover Card Listener
                node.addEventListener('mouseenter', (e) => {
                    const data = vars[symKey];
                    if (!data) return;

                    populateHoverCard(data, symKey);

                    isOverNode = true;
                    updateCardVisibility();

                    const rect = node.getBoundingClientRect();
                    hoverCard.style.left = `${rect.left + window.scrollX}px`;
                    hoverCard.style.top = `${rect.bottom + window.scrollY + 8}px`;

                    // Option B Bidirectional Sync: Highlight sidebar badge
                    const sidebarItem = document.querySelector(`.var-legend-item[data-sym="${symKey}"]`);
                    if (sidebarItem) {
                        sidebarItem.style.background = 'rgba(100, 255, 218, 0.16)';
                        sidebarItem.style.borderColor = 'rgba(100, 255, 218, 0.5)';
                    }
                });

                node.addEventListener('mouseleave', () => {
                    isOverNode = false;
                    setTimeout(() => { updateCardVisibility(); }, 150);

                    const sidebarItem = document.querySelector(`.var-legend-item[data-sym="${symKey}"]`);
                    if (sidebarItem) {
                        sidebarItem.style.background = 'rgba(255, 255, 255, 0.03)';
                        sidebarItem.style.borderColor = 'rgba(255, 255, 255, 0.06)';
                    }
                });

                // Prevent accidental page redirects on single-letter variable clicks
                node.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const data = vars[symKey];
                    if (!data) return;

                    populateHoverCard(data, symKey);
                    isOverNode = true;
                    updateCardVisibility();

                    const rect = node.getBoundingClientRect();
                    hoverCard.style.left = `${rect.left + window.scrollX}px`;
                    hoverCard.style.top = `${rect.bottom + window.scrollY + 8}px`;
                });
            }
        });
    }

    // Option B Sidebar Legend Hover Events (Bidirectional Sync to Prose SVGs)
    document.querySelectorAll('.var-legend-item').forEach(item => {
        const symKey = item.getAttribute('data-sym');
        
        item.addEventListener('mouseenter', () => {
            const data = vars[symKey];
            if (!data) return;

            populateHoverCard(data, symKey);

            isOverNode = true;
            updateCardVisibility();

            const rect = item.getBoundingClientRect();
            hoverCard.style.left = `${rect.left + window.scrollX - 310}px`;
            hoverCard.style.top = `${rect.top + window.scrollY}px`;

            // Highlight all matching math SVGs in prose
            if (mainProse) {
                mainProse.querySelectorAll(`.var-math-token[data-sym="${symKey}"]`).forEach(n => {
                    n.style.background = 'rgba(100, 255, 218, 0.2)';
                    n.style.boxShadow = '0 0 8px rgba(100, 255, 218, 0.5)';
                });
            }
        });

        item.addEventListener('mouseleave', () => {
            isOverNode = false;
            setTimeout(() => { updateCardVisibility(); }, 150);

            if (mainProse) {
                mainProse.querySelectorAll(`.var-math-token[data-sym="${symKey}"]`).forEach(n => {
                    n.style.background = 'transparent';
                    n.style.boxShadow = 'none';
                });
            }
        });
    });
});
</script>

<!-- Interactive 3D Parallax Tilt & Subtopic Styling -->
<script nonce="<?= $nonce ?>">
(function() {
    document.querySelectorAll('.related-concept-card').forEach(card => {
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
            const tiltX = (center.y / (bounds.height / 2)) * -6;
            const tiltY = (center.x / (bounds.width / 2)) * 6;
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

<style>
.subtopic-command-header {
    margin-bottom: 24px;
}

.subtopic-glass-breadcrumb {
    margin-bottom: 12px;
    font-size: 0.85rem;
}

.subtopic-prose-card {
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.5) 0%, rgba(3, 7, 18, 0.7) 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 3px solid var(--accent-color, #64ffda);
    border-radius: 12px;
    padding: 28px 32px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
}

.subtopic-prose-card a:not(.btn):not(.concept-card):not(.verification-badge):not(.explainer-link-btn),
.content-body a:not(.btn):not(.concept-card):not(.verification-badge):not(.explainer-link-btn) {
    color: var(--secondary-color, #b485ff);
    text-decoration: none;
    border-bottom: 1px dashed rgba(180, 133, 255, 0.45);
    font-weight: 500;
    transition: all 0.2s ease;
    padding-bottom: 1px;
}

.subtopic-prose-card a:not(.btn):not(.concept-card):not(.verification-badge):not(.explainer-link-btn):hover,
.content-body a:not(.btn):not(.concept-card):not(.verification-badge):not(.explainer-link-btn):hover {
    color: #ffffff;
    border-bottom-style: solid;
    border-bottom-color: var(--secondary-color, #b485ff);
    text-shadow: 0 0 10px rgba(180, 133, 255, 0.5);
}
</style>
