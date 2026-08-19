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
            onNodeClick: null
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

        // Domain palette
        this.domainColors = {
            'general-relativity': { fill: '#38bdf8', glow: 'rgba(56, 189, 248, 0.4)', stroke: '#0284c7' },
            'quantum-mechanics': { fill: '#34d399', glow: 'rgba(52, 211, 153, 0.4)', stroke: '#059669' },
            'quantum-field-theory': { fill: '#c084fc', glow: 'rgba(192, 132, 252, 0.4)', stroke: '#9333ea' },
            'thermodynamics': { fill: '#fbbf24', glow: 'rgba(251, 191, 36, 0.4)', stroke: '#d97706' },
            'electromagnetism': { fill: '#60a5fa', glow: 'rgba(96, 165, 250, 0.4)', stroke: '#2563eb' },
            'astrophysics': { fill: '#f472b6', glow: 'rgba(244, 114, 182, 0.4)', stroke: '#db2777' },
            'classical-mechanics': { fill: '#94a3b8', glow: 'rgba(148, 163, 184, 0.4)', stroke: '#475569' },
            'fluid-dynamics': { fill: '#2dd4bf', glow: 'rgba(45, 212, 191, 0.4)', stroke: '#0d9488' },
            'condensed-matter': { fill: '#a78bfa', glow: 'rgba(167, 139, 250, 0.4)', stroke: '#7c3aed' },
            'special-relativity': { fill: '#818cf8', glow: 'rgba(129, 140, 248, 0.4)', stroke: '#4f46e5' },
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
        this.container.style.background = 'radial-gradient(ellipse at center, rgba(15, 23, 42, 0.8) 0%, rgba(3, 7, 18, 0.95) 100%)';
        this.container.style.borderRadius = '12px';
        this.container.style.border = '1px solid rgba(100, 255, 218, 0.2)';
        this.container.style.minHeight = '360px';

        // 1. Controls Header
        const header = document.createElement('div');
        header.style.cssText = 'position: absolute; top: 12px; left: 16px; right: 16px; z-index: 10; display: flex; align-items: center; justify-content: space-between; pointer-events: none;';
        header.innerHTML = `
            <div style="display: flex; align-items: center; gap: 8px; pointer-events: auto;">
                <span style="font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; color: var(--accent-default, #64ffda); font-family: 'Space Grotesk', sans-serif;">
                    🌌 Lineage &amp; Derivation Map
                </span>
                <span id="graph-node-count-badge" style="font-size: 0.68rem; padding: 2px 7px; background: rgba(100,255,218,0.12); color: #64ffda; border-radius: 12px; border: 1px solid rgba(100,255,218,0.25);">
                    Loading...
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 6px; pointer-events: auto;">
                <label style="font-size: 0.72rem; color: #94a3b8; display: flex; align-items: center; gap: 4px;">
                    Depth:
                    <select id="graph-depth-select" style="background: rgba(3,7,18,0.85); border: 1px solid rgba(100,255,218,0.3); color: #64ffda; border-radius: 6px; padding: 2px 6px; font-size: 0.72rem; outline: none; cursor: pointer;">
                        <option value="1">1 Hop (Direct)</option>
                        <option value="2" selected>2 Hops (Lineage)</option>
                        <option value="3">3 Hops (Expanded)</option>
                    </select>
                </label>
                <button id="graph-btn-reset" title="Reset View" style="background: rgba(15,23,42,0.8); border: 1px solid rgba(100,255,218,0.3); color: #e2e8f0; border-radius: 6px; padding: 3px 8px; font-size: 0.72rem; cursor: pointer;">
                    ⟲ Reset
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

        // Tooltip container (interactive & clickable)
        this.tooltip = document.createElement('div');
        this.tooltip.style.cssText = 'position: absolute; display: none; z-index: 50; pointer-events: auto; cursor: pointer; background: rgba(3, 7, 18, 0.96); border: 1px solid rgba(100, 255, 218, 0.4); border-radius: 10px; padding: 12px 16px; max-width: 300px; box-shadow: 0 12px 30px rgba(0,0,0,0.7), 0 0 15px rgba(100,255,218,0.15); backdrop-filter: blur(10px); transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.15s ease;';
        
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
            const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
            const newK = Math.max(0.3, Math.min(3.0, this.transform.k * zoomFactor));
            
            // Zoom toward mouse center
            const rect = svg.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            this.transform.x = mouseX - (mouseX - this.transform.x) * (newK / this.transform.k);
            this.transform.y = mouseY - (mouseY - this.transform.y) * (newK / this.transform.k);
            this.transform.k = newK;
            this.updateTransform();
        }, { passive: false });

        // Controls
        const resetBtn = this.container.querySelector('#graph-btn-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetView());
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
    }

    updateTransform() {
        this.g.setAttribute('transform', `translate(${this.transform.x}, ${this.transform.y}) scale(${this.transform.k})`);
    }

    resetView() {
        const rect = this.svg.getBoundingClientRect();
        this.transform = { x: rect.width / 2, y: rect.height / 2, k: 1.0 };
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
                this.renderGraph(res.data);
                if (badge) {
                    badge.innerText = `${res.data.stats.total_nodes} nodes • ${res.data.stats.total_links} links`;
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
        this.resetView();

        // 1. Hierarchical Layout by Layer
        const layers = {};
        nodes.forEach(n => {
            const l = n.layer || 0;
            if (!layers[l]) layers[l] = [];
            layers[l].push(n);
        });

        const layerKeys = Object.keys(layers).map(Number).sort((a, b) => a - b);
        const layerSpacingY = 110;
        const nodeSpacingX = 160;

        const nodePositions = {};

        layerKeys.forEach(layerIdx => {
            const layerNodes = layers[layerIdx];
            const totalWidth = (layerNodes.length - 1) * nodeSpacingX;
            const startX = -totalWidth / 2;

            layerNodes.forEach((node, idx) => {
                const x = startX + idx * nodeSpacingX;
                const y = layerIdx * layerSpacingY;
                nodePositions[node.id] = { x, y, node };
            });
        });

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
            path.setAttribute('stroke', link.direction === 'upstream' ? 'rgba(56, 189, 248, 0.4)' : 'rgba(100, 255, 218, 0.4)');
            path.setAttribute('stroke-width', '1.5');
            path.setAttribute('stroke-dasharray', link.type === 'subcomponent' ? '3,3' : 'none');
            linkGroup.appendChild(path);
        });

        // 3. Draw Nodes
        const nodeGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        this.g.appendChild(nodeGroup);

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
                glow.setAttribute('r', '28');
                glow.setAttribute('fill', 'none');
                glow.setAttribute('stroke', 'var(--accent-default, #64ffda)');
                glow.setAttribute('stroke-width', '2');
                glow.setAttribute('opacity', '0.6');
                glow.innerHTML = `<animate attributeName="r" values="24;32;24" dur="2.5s" repeatCount="indefinite"/>
                                  <animate attributeName="opacity" values="0.8;0.2;0.8" dur="2.5s" repeatCount="indefinite"/>`;
                gNode.appendChild(glow);
            }

            // Main Circle
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('r', isRoot ? '18' : '12');
            circle.setAttribute('fill', isRoot ? '#64ffda' : domainCfg.fill);
            circle.setAttribute('stroke', '#0f172a');
            circle.setAttribute('stroke-width', '2.5');
            circle.style.transition = 'all 0.2s ease';
            gNode.appendChild(circle);

            // Label Text
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('y', isRoot ? '32' : '24');
            label.setAttribute('text-anchor', 'middle');
            label.setAttribute('fill', isRoot ? '#ffffff' : '#cbd5e1');
            label.setAttribute('font-size', isRoot ? '12' : '10.5');
            label.setAttribute('font-weight', isRoot ? '700' : '500');
            label.setAttribute('font-family', "'Space Grotesk', sans-serif");
            
            // Truncate long titles
            const titleText = node.title.length > 20 ? node.title.substring(0, 18) + '…' : node.title;
            label.textContent = titleText;
            gNode.appendChild(label);

            // Hover Events
            gNode.addEventListener('mouseenter', (e) => {
                if (this.hideTimeout) {
                    clearTimeout(this.hideTimeout);
                    this.hideTimeout = null;
                }
                circle.setAttribute('r', isRoot ? '22' : '16');
                this.showTooltip(node, e);
            });

            gNode.addEventListener('mouseleave', () => {
                circle.setAttribute('r', isRoot ? '18' : '12');
                this.hideTimeout = setTimeout(() => {
                    this.hideTooltip();
                }, 300);
            });

            // Click navigation
            gNode.addEventListener('click', (e) => {
                e.stopPropagation();
                if (this.options.onNodeClick) {
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
