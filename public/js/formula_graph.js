/**
 * Terra Physics Lab - Formula Lineage & Derivation Graph Interactive Visualizer
 * Renders hierarchical mathematical lineage DAGs with interactive pan, zoom,
 * domain clustering, MathJax tooltips, and click-to-traverse navigation.
 */

window.FormulaLineageGraph = class FormulaLineageGraph {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = Object.assign({
            depth: 2,
            width: 800,
            height: 400,
            onNodeClick: null,
            onRootLoaded: null
        }, options);

        this.data = null;
        this.svg = null;
        this.transform = { x: 0, y: 0, k: 1 };
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.selectedNode = null;
        this.nodes = [];
        this.links = [];
        this.animFrame = null;
        this.isFullscreen = false;
        this.hudCollapsed = false;
        this.activeRootNode = null;

        // Domain palette - 12 Canonical Physics Branches
        this.domainColors = {
            'theoretical-physics': { fill: '#c084fc', glow: 'rgba(192, 132, 252, 0.4)', stroke: '#9333ea' },
            'electromagnetism': { fill: '#60a5fa', glow: 'rgba(96, 165, 250, 0.4)', stroke: '#2563eb' },
            'astrophysics': { fill: '#f472b6', glow: 'rgba(244, 114, 182, 0.4)', stroke: '#db2777' },
            'philosophy-of-physics': { fill: '#e879f9', glow: 'rgba(232, 121, 249, 0.4)', stroke: '#c026d3' },
            'classical-mechanics': { fill: '#94a3b8', glow: 'rgba(148, 163, 184, 0.4)', stroke: '#475569' },
            'relativity': { fill: '#38bdf8', glow: 'rgba(56, 189, 248, 0.4)', stroke: '#0284c7' },
            'standard-model': { fill: '#f87171', glow: 'rgba(248, 113, 113, 0.4)', stroke: '#dc2626' },
            'quantum-physics': { fill: '#34d399', glow: 'rgba(52, 211, 153, 0.4)', stroke: '#059669' },
            'thermodynamics-statistical-mechanics': { fill: '#fbbf24', glow: 'rgba(251, 191, 36, 0.4)', stroke: '#d97706' },
            'mathematical-methods': { fill: '#818cf8', glow: 'rgba(129, 140, 248, 0.4)', stroke: '#4f46e5' },
            'fluids-nonlinear': { fill: '#2dd4bf', glow: 'rgba(45, 212, 191, 0.4)', stroke: '#0d9488' },
            'condensed-matter': { fill: '#a78bfa', glow: 'rgba(167, 139, 250, 0.4)', stroke: '#7c3aed' },

            // Backwards compatibility aliases
            'general-relativity': { fill: '#38bdf8', glow: 'rgba(56, 189, 248, 0.4)', stroke: '#0284c7' },
            'special-relativity': { fill: '#818cf8', glow: 'rgba(129, 140, 248, 0.4)', stroke: '#4f46e5' },
            'quantum-mechanics': { fill: '#34d399', glow: 'rgba(52, 211, 153, 0.4)', stroke: '#059669' },
            'quantum-field-theory': { fill: '#c084fc', glow: 'rgba(192, 132, 252, 0.4)', stroke: '#9333ea' },
            'thermodynamics': { fill: '#fbbf24', glow: 'rgba(251, 191, 36, 0.4)', stroke: '#d97706' },
            'fluid-dynamics': { fill: '#2dd4bf', glow: 'rgba(45, 212, 191, 0.4)', stroke: '#0d9488' },
            'nuclear-physics': { fill: '#f87171', glow: 'rgba(248, 113, 113, 0.4)', stroke: '#dc2626' }
        };

        if (this.container) {
            this.init();
        }
    }

    init() {
        this.container.innerHTML = '';
        this.container.style.position = 'relative';
        this.container.style.overflow = 'hidden';
        this.container.style.background = 'radial-gradient(ellipse at center, rgba(15, 23, 42, 0.85) 0%, rgba(2, 6, 23, 0.98) 100%)';
        this.container.style.borderRadius = '12px';
        this.container.style.border = '1px solid rgba(100, 255, 218, 0.2)';
        this.container.style.minHeight = '360px';

        // 1. Controls Header
        const header = document.createElement('div');
        header.style.cssText = 'position: absolute; top: 12px; left: 16px; right: 16px; z-index: 25; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; pointer-events: none;';
        header.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px; pointer-events: auto; flex-wrap: wrap;">
                <span style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; color: var(--accent-default, #64ffda); font-family: 'Space Grotesk', sans-serif;">
                    🌌 Lineage &amp; Derivation Map
                </span>
                <span id="graph-node-count-badge" style="font-size: 0.68rem; padding: 2px 8px; background: rgba(100,255,218,0.12); color: #64ffda; border-radius: 12px; border: 1px solid rgba(100,255,218,0.25);">
                    Loading...
                </span>
                <!-- Full-Screen Quick Search Bar (shown in Full-Screen mode) -->
                <div id="graph-fs-search-wrap" style="display: none; position: relative; min-width: 280px;">
                    <input type="text"
                           id="graph-fs-search-input"
                           placeholder="🔍 Search &amp; center any formula..."
                           autocomplete="off"
                           style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.92); border: 1px solid rgba(100, 255, 218, 0.35); border-radius: 8px; padding: 5px 12px; color: #ffffff; font-size: 0.78rem; font-family: 'Space Grotesk', sans-serif; outline: none; box-shadow: 0 4px 14px rgba(0,0,0,0.5);" />
                    <div id="graph-fs-search-dropdown" style="display: none; position: absolute; top: calc(100% + 4px); left: 0; right: 0; z-index: 100; background: rgba(3, 7, 18, 0.98); border: 1px solid rgba(100, 255, 218, 0.4); border-radius: 8px; max-height: 280px; overflow-y: auto; box-shadow: 0 12px 30px rgba(0,0,0,0.85); backdrop-filter: blur(12px);"></div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; pointer-events: auto; flex-wrap: wrap;">
                <label style="font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 4px; background: rgba(15,23,42,0.85); padding: 2px 6px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);">
                    Depth:
                    <select id="graph-depth-select" style="background: transparent; border: none; color: #64ffda; font-size: 0.72rem; font-weight: 600; outline: none; cursor: pointer;">
                        <option value="1" style="background: #030712;">1 Hop (Direct)</option>
                        <option value="2" selected style="background: #030712;">2 Hops (Lineage)</option>
                        <option value="3" style="background: #030712;">3 Hops (Expanded)</option>
                    </select>
                </label>
                <div style="display: inline-flex; align-items: center; background: rgba(15,23,42,0.85); border: 1px solid rgba(100,255,218,0.25); border-radius: 6px; overflow: hidden;">
                    <button type="button" id="graph-btn-zoom-out" title="Zoom Out" style="background: transparent; border: none; color: #e2e8f0; padding: 3px 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer;">−</button>
                    <button type="button" id="graph-btn-reset" title="Auto-Fit &amp; Reset View" style="background: rgba(100,255,218,0.08); border: none; border-left: 1px solid rgba(100,255,218,0.2); border-right: 1px solid rgba(100,255,218,0.2); color: #e2e8f0; padding: 3px 9px; font-size: 0.72rem; cursor: pointer;">⟲ Fit</button>
                    <button type="button" id="graph-btn-zoom-in" title="Zoom In" style="background: transparent; border: none; color: #e2e8f0; padding: 3px 8px; font-size: 0.8rem; font-weight: 700; cursor: pointer;">+</button>
                </div>
                <button type="button" id="graph-btn-fullscreen" title="Toggle Full-Screen View (Esc to exit)" style="background: rgba(100, 255, 218, 0.14); border: 1px solid rgba(100, 255, 218, 0.45); color: #64ffda; border-radius: 6px; padding: 4px 10px; font-size: 0.73rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; cursor: pointer; display: inline-flex; align-items: center; gap: 5px; transition: all 0.2s;">
                    <span>⛶</span>
                    <span id="graph-btn-fullscreen-label">Full Screen</span>
                </button>
            </div>
        `;
        this.container.appendChild(header);

        // 2. SVG Canvas
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.style.cssText = 'width: 100%; height: 100%; min-height: 360px; cursor: grab; display: block;';
        this.container.appendChild(svg);
        this.svg = svg;

        // Group container for pan/zoom
        this.g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.svg.appendChild(this.g);

        // 3. Floating Active Formula HUD Bar (visible in Full-Screen mode)
        this.fsHud = document.createElement('div');
        this.fsHud.id = 'graph-fs-hud';
        this.fsHud.style.cssText = 'display: none; position: absolute; bottom: 20px; left: 20px; z-index: 30; width: 440px; max-width: calc(100vw - 40px); background: rgba(3, 7, 18, 0.94); border: 1px solid rgba(100, 255, 218, 0.35); border-radius: 12px; padding: 14px 16px; box-shadow: 0 16px 40px rgba(0,0,0,0.8), 0 0 20px rgba(100,255,218,0.12); backdrop-filter: blur(14px); color: #f1f5f9; font-family: "Space Grotesk", sans-serif;';
        this.container.appendChild(this.fsHud);

        // 4. Tooltip container (interactive & clickable)
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'no-inspect';
        this.tooltip.style.cssText = 'position: absolute; display: none; z-index: 50; pointer-events: auto; cursor: pointer; background: rgba(3, 7, 18, 0.96); border: 1px solid rgba(100, 255, 218, 0.4); border-radius: 10px; padding: 12px 16px; max-width: 320px; box-shadow: 0 12px 30px rgba(0,0,0,0.7), 0 0 15px rgba(100,255,218,0.15); backdrop-filter: blur(10px); transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;';
        
        this.tooltip.addEventListener('mouseenter', () => {
            if (this.hideTimeout) {
                clearTimeout(this.hideTimeout);
                this.hideTimeout = null;
            }
            this.tooltip.style.borderColor = 'var(--accent-default, #64ffda)';
            this.tooltip.style.boxShadow = '0 15px 35px rgba(0,0,0,0.8), 0 0 20px rgba(100,255,218,0.3)';
            this.tooltip.style.transform = 'translateY(-2px)';
        });

        this.tooltip.addEventListener('mouseleave', () => {
            this.tooltip.style.transform = 'none';
            this.hideTooltip();
        });

        this.tooltip.addEventListener('click', (e) => {
            e.stopPropagation();
            if (this.hoveredNode) {
                if (this.options.onNodeClick) {
                    this.options.onNodeClick(this.hoveredNode);
                } else {
                    window.location.href = `/physics/equation-explainer?id=${encodeURIComponent(this.hoveredNode.id)}`;
                }
            }
        });

        this.container.appendChild(this.tooltip);

        // Bind interactive event listeners
        this.bindEvents();
    }

    bindEvents() {
        const svg = this.svg;

        // Pan/Drag
        svg.addEventListener('mousedown', (e) => {
            if (e.target.tagName === 'circle' || e.target.tagName === 'text') return;
            this.isDragging = true;
            this.dragStart = { x: e.clientX - this.transform.x, y: e.clientY - this.transform.y };
            svg.style.cursor = 'grabbing';
        });

        window.addEventListener('mousemove', (e) => {
            if (this.isDragging) {
                this.transform.x = e.clientX - this.dragStart.x;
                this.transform.y = e.clientY - this.dragStart.y;
                this.updateTransform();
            }
        });

        window.addEventListener('mouseup', () => {
            if (this.isDragging) {
                this.isDragging = false;
                svg.style.cursor = 'grab';
            }
        });

        // Zoom with mouse wheel
        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
            this.zoomBy(zoomFactor, e.clientX, e.clientY);
        }, { passive: false });

        // Controls
        const resetBtn = this.container.querySelector('#graph-btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetView());
        }

        const zoomInBtn = this.container.querySelector('#graph-btn-zoom-in');
        if (zoomInBtn) {
            zoomInBtn.addEventListener('click', () => this.zoomBy(1.22));
        }

        const zoomOutBtn = this.container.querySelector('#graph-btn-zoom-out');
        if (zoomOutBtn) {
            zoomOutBtn.addEventListener('click', () => this.zoomBy(0.82));
        }

        const fullscreenBtn = this.container.querySelector('#graph-btn-fullscreen');
        if (fullscreenBtn) {
            fullscreenBtn.addEventListener('click', () => this.toggleFullscreen());
        }

        const depthSelect = this.container.querySelector('#graph-depth-select');
        if (depthSelect) {
            depthSelect.addEventListener('change', (e) => {
                this.options.depth = parseInt(e.target.value, 10);
                if (this.currentFormulaId) {
                    this.loadFormula(this.currentFormulaId);
                }
            });
        }

        // Escape key to exit Full-Screen
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isFullscreen) {
                this.toggleFullscreen(false);
            }
        });

        // Bind Full-Screen Quick Search Autocomplete
        this.bindFullscreenSearch();

        // ResizeObserver so hidden tab reveal or container resize automatically re-fits the graph
        if (typeof ResizeObserver !== 'undefined') {
            let lastW = 0;
            this.resizeObserver = new ResizeObserver((entries) => {
                for (const entry of entries) {
                    const w = entry.contentRect.width;
                    if (w > 0 && Math.abs(w - lastW) > 20) {
                        lastW = w;
                        if (this.data && this.data.nodes && this.data.nodes.length > 0) {
                            this.resetView();
                        }
                    }
                }
            });
            this.resizeObserver.observe(this.container);
        } else {
            window.addEventListener('resize', () => {
                if (this.data && this.data.nodes && this.data.nodes.length > 0) {
                    this.resetView();
                }
            });
        }
    }

    zoomBy(factor, clientX = null, clientY = null) {
        const rect = this.svg.getBoundingClientRect();
        const centerX = clientX !== null ? (clientX - rect.left) : (rect.width / 2);
        const centerY = clientY !== null ? (clientY - rect.top) : (rect.height / 2);
        const newK = Math.max(0.28, Math.min(3.5, this.transform.k * factor));

        this.transform.x = centerX - (centerX - this.transform.x) * (newK / this.transform.k);
        this.transform.y = centerY - (centerY - this.transform.y) * (newK / this.transform.k);
        this.transform.k = newK;
        this.updateTransform();
    }

    toggleFullscreen(forceState = null) {
        const nextState = forceState !== null ? Boolean(forceState) : !this.isFullscreen;
        if (nextState === this.isFullscreen) return;
        this.isFullscreen = nextState;

        const labelEl = this.container.querySelector('#graph-btn-fullscreen-label');
        const fsSearchWrap = this.container.querySelector('#graph-fs-search-wrap');

        if (this.isFullscreen) {
            this.savedContainerStyle = {
                position: this.container.style.position,
                top: this.container.style.top,
                left: this.container.style.left,
                right: this.container.style.right,
                bottom: this.container.style.bottom,
                width: this.container.style.width,
                height: this.container.style.height,
                zIndex: this.container.style.zIndex,
                borderRadius: this.container.style.borderRadius,
                boxSizing: this.container.style.boxSizing
            };

            // Portal to document.body so ancestor backdrop-filter/transform cards
            // (such as .glass-card in Equation Explainer) do not create a shifted fixed containing block
            if (this.container.parentNode && this.container.parentNode !== document.body) {
                this.domPlaceholder = document.createElement('div');
                this.domPlaceholder.style.height = this.container.style.height || '620px';
                this.domPlaceholder.style.width = '100%';
                this.container.parentNode.insertBefore(this.domPlaceholder, this.container);
                document.body.appendChild(this.container);
            }

            this.container.style.position = 'fixed';
            this.container.style.top = '0';
            this.container.style.left = '0';
            this.container.style.right = '0';
            this.container.style.bottom = '0';
            this.container.style.width = '100%';
            this.container.style.height = '100%';
            this.container.style.boxSizing = 'border-box';
            this.container.style.zIndex = '9999';
            this.container.style.borderRadius = '0';
            document.body.style.overflow = 'hidden';

            if (labelEl) labelEl.textContent = 'Exit Full Screen (Esc)';
            if (fsSearchWrap) fsSearchWrap.style.display = 'block';
            if (this.fsHud && this.activeRootNode) {
                this.fsHud.style.display = 'block';
                this.updateFullscreenHud(this.activeRootNode);
            }
        } else {
            if (this.domPlaceholder && this.domPlaceholder.parentNode) {
                this.domPlaceholder.parentNode.insertBefore(this.container, this.domPlaceholder);
                this.domPlaceholder.remove();
                this.domPlaceholder = null;
            }

            if (this.savedContainerStyle) {
                this.container.style.position = this.savedContainerStyle.position || 'relative';
                this.container.style.top = this.savedContainerStyle.top || '';
                this.container.style.left = this.savedContainerStyle.left || '';
                this.container.style.right = this.savedContainerStyle.right || '';
                this.container.style.bottom = this.savedContainerStyle.bottom || '';
                this.container.style.width = this.savedContainerStyle.width || '100%';
                this.container.style.height = this.savedContainerStyle.height || '';
                this.container.style.boxSizing = this.savedContainerStyle.boxSizing || '';
                this.container.style.zIndex = this.savedContainerStyle.zIndex || '';
                this.container.style.borderRadius = this.savedContainerStyle.borderRadius || '12px';
            }
            document.body.style.overflow = '';

            if (labelEl) labelEl.textContent = 'Full Screen';
            if (fsSearchWrap) fsSearchWrap.style.display = 'none';
            if (this.fsHud) this.fsHud.style.display = 'none';
        }

        // Re-render with mode-specific node/layer spacing and auto-fit to the new viewport
        if (this.data && this.data.nodes && this.data.nodes.length > 0) {
            setTimeout(() => {
                this.renderGraph(this.data);
            }, 30);
        }
    }

    bindFullscreenSearch() {
        const inputEl = this.container.querySelector('#graph-fs-search-input');
        const dropdownEl = this.container.querySelector('#graph-fs-search-dropdown');
        if (!inputEl || !dropdownEl) return;

        let debounceTimer = null;
        inputEl.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            const q = inputEl.value.trim();
            if (q.length < 2) {
                dropdownEl.style.display = 'none';
                return;
            }
            debounceTimer = setTimeout(async () => {
                try {
                    const res = await fetch(`/physics/api/search?q=${encodeURIComponent(q)}&limit=8`);
                    const items = await res.json();
                    const formulas = (Array.isArray(items) ? items : []).filter(item => item.type === 'formula' && item.slug);
                    if (formulas.length === 0) {
                        dropdownEl.innerHTML = `<div style="padding: 8px 12px; color: #94a3b8; font-size: 0.76rem;">No matching formulas found.</div>`;
                        dropdownEl.style.display = 'block';
                        return;
                    }
                    dropdownEl.innerHTML = formulas.map(f => `
                        <div class="fs-search-item" data-slug="${f.slug}" style="padding: 8px 12px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; flex-direction: column; gap: 2px;">
                            <div style="font-size: 0.8rem; font-weight: 700; color: #f8fafc;">${f.title}</div>
                            <div style="font-size: 0.68rem; color: #64ffda; font-family: monospace;">${f.slug}</div>
                        </div>
                    `).join('');
                    dropdownEl.style.display = 'block';

                    dropdownEl.querySelectorAll('.fs-search-item').forEach(row => {
                        row.addEventListener('mouseenter', () => { row.style.background = 'rgba(100,255,218,0.12)'; });
                        row.addEventListener('mouseleave', () => { row.style.background = 'transparent'; });
                        row.addEventListener('click', () => {
                            const slug = row.getAttribute('data-slug');
                            inputEl.value = '';
                            dropdownEl.style.display = 'none';
                            if (slug) {
                                this.loadFormula(slug);
                            }
                        });
                    });
                } catch (err) {
                    dropdownEl.style.display = 'none';
                }
            }, 180);
        });

        document.addEventListener('click', (e) => {
            if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
                dropdownEl.style.display = 'none';
            }
        });
    }

    updateFullscreenHud(node) {
        if (!this.fsHud || !node) return;
        this.activeRootNode = node;
        if (!this.isFullscreen) return;

        const domainCfg = this.domainColors[node.domain] || { fill: '#64ffda' };
        const isOnUniversePage = window.location.pathname.includes('/universe-graph');

        this.fsHud.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: ${this.hudCollapsed ? '0' : '8px'};">
                <div style="display: flex; align-items: center; gap: 8px; min-width: 0;">
                    <span style="font-size: 0.68rem; text-transform: uppercase; color: ${domainCfg.fill}; font-weight: 700; letter-spacing: 0.06em; white-space: nowrap;">
                        ${node.domain_label || node.domain || 'Physics'}
                    </span>
                    <span style="font-size: 0.68rem; color: #64748b; font-family: monospace; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        ${node.id}
                    </span>
                </div>
                <button type="button" id="graph-fs-hud-toggle" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #cbd5e1; border-radius: 5px; padding: 2px 7px; font-size: 0.68rem; cursor: pointer;">
                    ${this.hudCollapsed ? '▴ Expand' : '▾ Minimize'}
                </button>
            </div>
            <div style="font-size: 1.02rem; font-weight: 700; color: #ffffff; margin-bottom: ${this.hudCollapsed ? '0' : '8px'};">
                ${node.title}
            </div>
            ${!this.hudCollapsed ? `
                ${node.equation ? `
                    <div id="graph-fs-hud-math" style="font-size: 0.96rem; color: #ffd700; background: rgba(2, 6, 23, 0.85); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 7px 11px; margin-bottom: 8px; overflow-x: auto;">
                        \\(${node.equation}\\)
                    </div>
                ` : ''}
                <div style="font-size: 0.78rem; color: #94a3b8; line-height: 1.45; margin-bottom: 12px;">
                    ${node.summary || 'Click any node in the graph to re-center or explore its derivation neighborhood.'}
                </div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <a href="/physics/equation-explainer?id=${encodeURIComponent(node.id)}" id="graph-fs-open-explainer" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: var(--accent-default, #64ffda); color: #020c1b; font-weight: 700; border-radius: 6px; text-decoration: none; font-size: 0.76rem;">
                        <span>🔬 Open in Explainer</span>
                        <span>➔</span>
                    </a>
                    ${!isOnUniversePage ? `
                        <a href="/physics/universe-graph?id=${encodeURIComponent(node.id)}" style="display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px; background: rgba(255,255,255,0.06); border: 1px solid rgba(100,255,218,0.3); color: #e2e8f0; font-weight: 600; border-radius: 6px; text-decoration: none; font-size: 0.76rem;">
                            <span>🌌 Open in Universe Graph</span>
                        </a>
                    ` : ''}
                </div>
            ` : ''}
        `;

        const toggleBtn = this.fsHud.querySelector('#graph-fs-hud-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.hudCollapsed = !this.hudCollapsed;
                this.updateFullscreenHud(this.activeRootNode);
            });
        }

        const openExplainerLink = this.fsHud.querySelector('#graph-fs-open-explainer');
        if (openExplainerLink && !isOnUniversePage && typeof this.options.onNodeClick === 'function') {
            openExplainerLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleFullscreen(false);
                this.options.onNodeClick(node);
            });
        }

        const mathEl = this.fsHud.querySelector('#graph-fs-hud-math');
        if (mathEl && window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([mathEl]).catch(() => {});
        }
    }

    updateTransform() {
        this.g.setAttribute('transform', `translate(${this.transform.x}, ${this.transform.y}) scale(${this.transform.k})`);
    }

    resetView() {
        const rect = this.svg.getBoundingClientRect();
        const w = (rect && rect.width > 0) ? rect.width : (this.container.clientWidth || 800);
        const h = (rect && rect.height > 0) ? rect.height : (this.container.clientHeight || 650);

        if (this.lastBounds && (this.lastBounds.maxX > this.lastBounds.minX || this.lastBounds.maxY > this.lastBounds.minY)) {
            const padX = 150;
            const padY = 120;
            const graphW = Math.max(200, (this.lastBounds.maxX - this.lastBounds.minX) + padX * 2);
            const graphH = Math.max(200, (this.lastBounds.maxY - this.lastBounds.minY) + padY * 2);
            const k = Math.max(0.42, Math.min(1.05, Math.min(w / graphW, h / graphH)));
            const centerX = (this.lastBounds.minX + this.lastBounds.maxX) / 2;
            const centerY = (this.lastBounds.minY + this.lastBounds.maxY) / 2;
            this.transform = {
                x: (w / 2) - centerX * k,
                y: (h / 2) - centerY * k + 12,
                k: k
            };
        } else {
            this.transform = { x: w / 2, y: h / 2, k: 1.0 };
        }
        this.updateTransform();
    }

    async loadFormula(formulaId) {
        this.currentFormulaId = formulaId;
        const badge = this.container.querySelector('#graph-node-count-badge');
        if (badge) badge.innerText = 'Traversing...';

        try {
            const resp = await fetch(`/physics/api/formula-graph/${encodeURIComponent(formulaId)}?depth=${this.options.depth}`);
            const res = await resp.json();

            if (res.success && res.data && res.data.nodes && res.data.nodes.length > 0) {
                this.data = res.data;
                if (res.data.root_node) {
                    this.activeRootNode = res.data.root_node;
                    if (this.isFullscreen && this.fsHud) {
                        this.fsHud.style.display = 'block';
                        this.updateFullscreenHud(res.data.root_node);
                    }
                }
                this.renderGraph(res.data);
                if (badge) {
                    badge.innerText = `${res.data.stats.total_nodes} nodes • ${res.data.stats.total_links} links`;
                }
                if (typeof this.options.onRootLoaded === 'function' && res.data.root_node) {
                    this.options.onRootLoaded(res.data.root_node);
                }
            } else {
                this.renderEmptyState("No direct mathematical lineage recorded for this formula.");
                if (badge) badge.innerText = '0 nodes';
            }
        } catch (e) {
            console.error("Formula graph load error:", e);
            this.renderEmptyState("Graph engine offline.");
        }
    }

    renderEmptyState(message) {
        this.lastBounds = null;
        this.g.innerHTML = `
            <text x="0" y="0" text-anchor="middle" fill="#94a3b8" font-size="13" font-family="'Space Grotesk', sans-serif">
                ${message}
            </text>
        `;
        this.resetView();
    }

    renderGraph(data) {
        const nodes = data.nodes || [];
        const links = data.links || [];
        const rootId = data.root_id;

        this.g.innerHTML = '';

        // 1. Hierarchical Layout by Layer (expanded spacing in Full-Screen mode)
        const layers = {};
        nodes.forEach(n => {
            const l = n.layer || 0;
            if (!layers[l]) layers[l] = [];
            layers[l].push(n);
        });

        const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
        const layerSpacingY = this.isFullscreen ? 195 : 152;
        const nodeSpacingX = this.isFullscreen ? 240 : 188;
        const staggerStepY = this.isFullscreen ? 30 : 22;

        const nodePositions = {};
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;

        layerKeys.forEach(layerIdx => {
            const layerNodes = layers[layerIdx];
            if (layerIdx === 0 && layerNodes.length > 1) {
                const rootPos = layerNodes.findIndex(n => n.is_root);
                if (rootPos !== -1) {
                    const [rootNode] = layerNodes.splice(rootPos, 1);
                    const centerIdx = Math.floor(layerNodes.length / 2);
                    layerNodes.splice(centerIdx, 0, rootNode);
                }
            }
            const totalWidth = (layerNodes.length - 1) * nodeSpacingX;
            const startX = -totalWidth / 2;

            layerNodes.forEach((node, idx) => {
                const x = startX + idx * nodeSpacingX;
                const staggerY = (!node.is_root && layerNodes.length > 4 && idx % 2 === 1) ? staggerStepY : 0;
                const y = layerIdx * layerSpacingY + staggerY;
                nodePositions[node.id] = { x, y, node };
                if (x < minX) minX = x;
                if (x > maxX) maxX = x;
                if (y < minY) minY = y;
                if (y > maxY) maxY = y;
            });
        });

        this.lastBounds = (minX <= maxX) ? { minX, maxX, minY, maxY } : null;
        this.resetView();

        // 2. Draw Curved Directional Links
        const linkGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.g.appendChild(linkGroup);

        links.forEach(link => {
            const src = nodePositions[link.source];
            const tgt = nodePositions[link.target];
            if (!src || !tgt) return;

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            const dx = tgt.x - src.x;
            const dy = tgt.y - src.y;
            const cx1 = src.x + dx * 0.2;
            const cy1 = src.y + dy * 0.5;
            const cx2 = src.x + dx * 0.8;
            const cy2 = src.y + dy * 0.5;

            path.setAttribute('d', `M ${src.x} ${src.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${tgt.x} ${tgt.y}`);
            path.setAttribute('fill', 'none');
            const isSiblingLink = link.direction === 'sibling' || link.type === 'sibling';
            const strokeColor = isSiblingLink
                ? 'rgba(167, 139, 250, 0.48)'
                : (link.direction === 'upstream' ? 'rgba(56, 189, 248, 0.55)' : 'rgba(100, 255, 218, 0.45)');
            path.setAttribute('stroke', strokeColor);
            path.setAttribute('stroke-width', this.isFullscreen ? '2' : '1.6');
            path.setAttribute('stroke-dasharray', isSiblingLink ? '4,3' : (link.type === 'subcomponent' ? '3,3' : 'none'));
            linkGroup.appendChild(path);
        });

        // 3. Draw Nodes
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.g.appendChild(nodeGroup);

        const rootRadius = this.isFullscreen ? 21 : 18;
        const childRadius = this.isFullscreen ? 14 : 12;
        const maxTitleLen = this.isFullscreen ? 34 : 24;

        nodes.forEach(node => {
            const pos = nodePositions[node.id];
            if (!pos) return;

            const isRoot = node.is_root;
            const domainCfg = this.domainColors[node.domain] || { fill: '#64ffda', glow: 'rgba(100,255,218,0.4)', stroke: '#059669' };

            const gNode = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            gNode.setAttribute('transform', `translate(${pos.x}, ${pos.y})`);
            gNode.style.cursor = 'pointer';

            // Glow Circle
            if (isRoot) {
                const glow = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                glow.setAttribute('r', String(rootRadius + 10));
                glow.setAttribute('fill', 'none');
                glow.setAttribute('stroke', 'var(--accent-default, #64ffda)');
                glow.setAttribute('stroke-width', '2');
                glow.setAttribute('opacity', '0.6');
                glow.innerHTML = `<animate attributeName="r" values="${rootRadius + 6};${rootRadius + 14};${rootRadius + 6}" dur="2.5s" repeatCount="indefinite"/>
                                  <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2.5s" repeatCount="indefinite"/>`;
                gNode.appendChild(glow);
            }

            // Main Circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', String(isRoot ? rootRadius : childRadius));
            circle.setAttribute('fill', isRoot ? '#64ffda' : domainCfg.fill);
            circle.setAttribute('stroke', '#0f172a');
            circle.setAttribute('stroke-width', '2.5');
            circle.style.transition = 'all 0.2s ease';
            gNode.appendChild(circle);

            // Label Text
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('y', String(isRoot ? (rootRadius + 15) : (childRadius + 14)));
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('fill', isRoot ? '#ffffff' : '#cbd5e1');
            label.setAttribute('font-size', isRoot ? (this.isFullscreen ? '13' : '12') : (this.isFullscreen ? '11.5' : '10.8'));
            label.setAttribute('font-weight', isRoot ? '700' : '500');
            label.setAttribute('font-family', "'Space Grotesk', sans-serif");
            
            // Truncate long titles cleanly
            const titleText = node.title.length > maxTitleLen ? node.title.substring(0, maxTitleLen - 2) + '…' : node.title;
            label.textContent = titleText;
            gNode.appendChild(label);

            // Hover Events
            gNode.addEventListener('mouseenter', (e) => {
                if (this.hideTimeout) {
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = null;
                }
                circle.setAttribute('r', String(isRoot ? (rootRadius + 4) : (childRadius + 4)));
                this.showTooltip(node, e);
            });

            gNode.addEventListener('mouseleave', () => {
                circle.setAttribute('r', String(isRoot ? rootRadius : childRadius));
                this.hideTimeout = setTimeout(() => {
                    this.hideTooltip();
                }, 300);
            });

            // Click navigation
            gNode.addEventListener('click', (e) => {
                e.stopPropagation();
                if (this.isFullscreen) {
                    // In Full-Screen mode, clicking a node centers the graph on it and updates the HUD
                    this.loadFormula(node.id);
                    if (this.options.onNodeClick && window.location.pathname.includes('/universe-graph')) {
                        this.options.onNodeClick(node);
                    }
                } else if (this.options.onNodeClick) {
                    this.options.onNodeClick(node);
                } else {
                    window.location.href = `/physics/equation-explainer?id=${encodeURIComponent(node.id)}`;
                }
            });

            nodeGroup.appendChild(gNode);
        });
    }

    showTooltip(node, evt) {
        this.hoveredNode = node;
        const rect = this.container.getBoundingClientRect();
        const x = evt.clientX - rect.left + 15;
        const y = evt.clientY - rect.top - 20;

        const domainCfg = this.domainColors[node.domain] || { fill: '#64ffda' };

        this.tooltip.style.left = `${Math.min(x, rect.width - 310)}px`;
        this.tooltip.style.top = `${Math.max(10, Math.min(y, rect.height - 160))}px`;
        this.tooltip.style.display = 'block';

        this.tooltip.innerHTML = `
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                <span style="font-size: 0.68rem; text-transform: uppercase; color: ${domainCfg.fill}; font-weight: 700; letter-spacing: 0.05em;">
                    ${node.domain_label || node.domain}
                </span>
                <span style="font-size: 0.68rem; color: #64ffda; font-weight: 700;">
                    Click to Open ➔
                </span>
            </div>
            <div style="font-size: 0.92rem; font-weight: 600; color: #ffffff; margin-bottom: 6px; line-height: 1.3;">
                ${node.title}
            </div>
            ${node.equation ? `
                <div style="font-size: 0.88rem; color: #ffd700; background: rgba(0,0,0,0.5); padding: 5px 9px; border-radius: 6px; margin-bottom: 6px; overflow-x: auto; font-family: monospace; border: 1px solid rgba(255,255,255,0.06);">
                    $${node.equation}$
                </div>
            ` : ''}
            <div style="font-size: 0.76rem; color: #94a3b8; line-height: 1.4;">
                ${node.summary || 'Click anywhere on this card to examine this formula in the Equation Explainer.'}
            </div>
            <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 0.72rem; color: var(--accent-default, #64ffda); display: flex; align-items: center; justify-content: flex-end; gap: 4px; font-weight: 600;">
                <span>Explore Full Derivation</span>
                <span style="font-size: 0.85rem;">➔</span>
            </div>
        `;

        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([this.tooltip]).catch(() => {});
        }
    }

    hideTooltip() {
        this.tooltip.style.display = 'none';
        this.hoveredNode = null;
    }
};
