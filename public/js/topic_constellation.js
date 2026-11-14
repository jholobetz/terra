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
            nodeG.setAttribute('role', 'link');
            nodeG.setAttribute('tabindex', '0');
            nodeG.setAttribute('aria-label', `${data.title} (Open treatise)`);
            nodeG.style.cursor = 'pointer';

            // Native SVG Tooltip
            const nodeTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
            nodeTitle.textContent = `${data.title} — Click to open treatise`;
            nodeG.appendChild(nodeTitle);

            // Outer Glow Ring
            const aura = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            aura.setAttribute('r', '14');
            aura.setAttribute('class', 'node-aura');
            aura.setAttribute('fill', 'transparent');
            aura.setAttribute('stroke', getTierColor(data.level));
            aura.setAttribute('stroke-width', '1.5');
            aura.setAttribute('opacity', '0.4');

            // Inner Core Body (glow filter applied selectively to active node only)
            const core = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            core.setAttribute('r', '6');
            core.setAttribute('class', 'node-core');
            core.setAttribute('fill', getTierColor(data.level));

            // Label Text (Capsule badge — static geometry initialized once)
            const textBg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            textBg.setAttribute('class', 'node-label-bg');
            textBg.setAttribute('rx', '4');
            textBg.setAttribute('ry', '4');
            textBg.setAttribute('x', '14');
            textBg.setAttribute('y', '-10');
            textBg.setAttribute('height', '16');
            textBg.setAttribute('fill', 'rgba(11, 17, 32, 0.85)');
            textBg.setAttribute('stroke', 'rgba(255, 255, 255, 0.1)');
            textBg.setAttribute('stroke-width', '0.8');

            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('class', 'node-label-text');
            text.setAttribute('x', '20');
            text.setAttribute('y', '2');
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

    // Measure text bounding boxes in a single batch once after DOM insertion (avoids per-frame layout thrashing)
    nodes.forEach(n => {
        let labelWidth = 60;
        try {
            const bbox = n.text.getBBox();
            if (bbox && bbox.width > 0) {
                labelWidth = bbox.width;
            } else {
                labelWidth = (n.data.title || '').length * 5.2;
            }
        } catch (e) {
            labelWidth = (n.data.title || '').length * 5.2;
        }
        n.textBg.setAttribute('width', Math.max(50, Math.round(labelWidth + 12)));
    });

    function getTierColor(level) {
        const l = (level || '').toLowerCase();
        if (l === 'foundational') return '#10b981'; // Emerald
        if (l === 'frontier') return '#d946ef';     // Violet
        return '#00d2ff';                           // Analytical Cyan
    }

    let activeNodeRef = null;

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

        // Highlight active node in SVG & scope GPU glow filter strictly to active node
        activeNodeRef = null;
        nodes.forEach(n => {
            if (n.slug === slug) {
                activeNodeRef = n;
                n.element.classList.add('is-active');
                n.aura.setAttribute('r', '18');
                n.aura.setAttribute('opacity', '0.9');
                n.core.setAttribute('r', '8');
                n.core.setAttribute('filter', 'url(#glow-filter)');
            } else {
                n.element.classList.remove('is-active');
                n.aura.setAttribute('r', '14');
                n.aura.setAttribute('opacity', '0.4');
                n.core.setAttribute('r', '6');
                n.core.removeAttribute('filter');
            }
        });

        // Update gravitational connector ray
        if (activeNodeRef && gravityRay) {
            gravityRay.setAttribute('x1', cx);
            gravityRay.setAttribute('y1', cy);
            gravityRay.setAttribute('x2', activeNodeRef.currentX || cx);
            gravityRay.setAttribute('y2', activeNodeRef.currentY || cy);
            gravityRay.setAttribute('opacity', '0.75');
        }
    }

    function sprintf2(n) {
        return n < 10 ? '0' + n : '' + n;
    }

    // 6. Bind Node Hover and Click Events
    nodes.forEach(n => {
        n.element.addEventListener('mouseenter', () => {
            updateHUD(n.slug);
        });

        n.element.addEventListener('click', (e) => {
            updateHUD(n.slug);
            if (e.metaKey || e.ctrlKey || e.button === 1) {
                window.open(`/physics/subtopic/${n.slug}`, '_blank');
            } else {
                window.location.href = `/physics/subtopic/${n.slug}`;
            }
        });

        n.element.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                window.location.href = `/physics/subtopic/${n.slug}`;
            }
        });
    });

    // 7. Continuous Orbital Animation Loop (Capped at 30 FPS with Lifecycle & Visibility Gating)
    let isPaused = false;
    let isOrbitMode = true;
    let isInViewport = true;
    let isWindowFocused = document.hasFocus ? document.hasFocus() : true;
    let rafId = null;
    let lastFrameTime = 0;
    const frameInterval = 1000 / 30; // Cap at 30fps
    const baseTickMs = 1000 / 60;    // Reference 60Hz tick for cfg.speed

    function shouldAnimate() {
        return !isPaused && isOrbitMode && !document.hidden && isWindowFocused && isInViewport;
    }

    function renderOrbitPositions() {
        for (let i = 0, len = nodes.length; i < len; i++) {
            const n = nodes[i];
            const x = cx + Math.cos(n.angle) * n.cfg.rx;
            const y = cy + Math.sin(n.angle) * n.cfg.ry;
            n.currentX = x;
            n.currentY = y;
            n.element.setAttribute('transform', `translate(${x.toFixed(1)}, ${y.toFixed(1)})`);
        }

        // Update gravitational connector ray to follow active node in real time
        if (activeNodeRef && gravityRay) {
            gravityRay.setAttribute('x2', (activeNodeRef.currentX || cx).toFixed(1));
            gravityRay.setAttribute('y2', (activeNodeRef.currentY || cy).toFixed(1));
        }
    }

    function animateOrbits(timestamp) {
        if (!shouldAnimate()) {
            rafId = null;
            return;
        }

        if (!lastFrameTime) lastFrameTime = timestamp;
        const elapsed = timestamp - lastFrameTime;

        if (elapsed >= frameInterval) {
            const tickScale = Math.min(elapsed / baseTickMs, 3.0);
            lastFrameTime = timestamp - (elapsed % frameInterval);

            for (let i = 0, len = nodes.length; i < len; i++) {
                nodes[i].angle += nodes[i].cfg.speed * tickScale;
            }
            renderOrbitPositions();
        }

        rafId = requestAnimationFrame(animateOrbits);
    }

    function startLoop() {
        if (rafId === null && shouldAnimate()) {
            lastFrameTime = 0;
            rafId = requestAnimationFrame(animateOrbits);
        }
    }

    function stopLoop() {
        if (rafId !== null) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    }

    // Initial static layout + HUD activation + start loop
    renderOrbitPositions();
    if (activeSlug) {
        updateHUD(activeSlug);
    }
    startLoop();

    // Lifecycle & Visibility Listeners
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) stopLoop();
        else startLoop();
    });

    window.addEventListener('focus', () => {
        isWindowFocused = true;
        startLoop();
    });

    window.addEventListener('blur', () => {
        isWindowFocused = false;
        stopLoop();
    });

    const constellationViewport = document.getElementById('constellation-viewport');
    if ('IntersectionObserver' in window && constellationViewport) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                isInViewport = entry.isIntersecting;
                if (isInViewport) startLoop();
                else stopLoop();
            });
        }, { threshold: 0.05 });
        observer.observe(constellationViewport);
    }

    // 8. Orbit Pause / Play Toggle
    if (btnOrbitPause) {
        btnOrbitPause.addEventListener('click', () => {
            isPaused = !isPaused;
            if (isPaused) {
                stopLoop();
                btnOrbitPause.classList.add('is-paused');
                btnOrbitPause.innerHTML = '<span id="orbit-pause-icon">▶</span> Resume Drift';
            } else {
                btnOrbitPause.classList.remove('is-paused');
                btnOrbitPause.innerHTML = '<span id="orbit-pause-icon">⏸</span> Pause Drift';
                startLoop();
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
                    r.setAttribute('stroke', 'rgba(255, 255, 218, 0.05)');
                    r.setAttribute('stroke-width', '0.8');
                }
            });
        });
    });

    // 10. View Mode Switcher (Constellation vs Directory)
    if (btnModeOrbit && btnModeDirectory) {
        btnModeOrbit.addEventListener('click', () => {
            isOrbitMode = true;
            btnModeOrbit.classList.add('active');
            btnModeDirectory.classList.remove('active');
            stageConstellation.style.display = 'block';
            stageDirectory.style.display = 'none';
            startLoop();
        });

        btnModeDirectory.addEventListener('click', () => {
            isOrbitMode = false;
            stopLoop();
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
