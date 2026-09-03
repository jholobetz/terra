/**
 * 🔬 Project Terra - In-Context Formula Inspector Drawer
 * Omnipresent glassmorphic slide-over drawer that deconstructs any equation in-place.
 */

const FormulaInspector = {
    drawerEl: null,
    backdropEl: null,
    currentLatex: '',
    currentFormulaId: null,

    init() {
        this.injectStyles();
        this.createDrawerDOM();
        this.bindEvents();
    },

    injectStyles() {
        if (document.getElementById('formula-inspector-styles')) return;
        const style = document.createElement('style');
        style.id = 'formula-inspector-styles';
        style.textContent = `
            .formula-inspector-backdrop {
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background: rgba(3, 7, 18, 0.6);
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                z-index: 99990;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .formula-inspector-backdrop.visible {
                opacity: 1;
                pointer-events: auto;
            }

            .formula-inspector-drawer {
                position: fixed;
                top: 0;
                right: 0;
                width: 480px;
                max-width: 90vw;
                height: 100vh;
                background: rgba(15, 23, 42, 0.96);
                backdrop-filter: blur(16px) saturate(180%);
                -webkit-backdrop-filter: blur(16px) saturate(180%);
                border-left: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: -10px 0 40px rgba(0, 0, 0, 0.7);
                z-index: 99999;
                transform: translateX(100%);
                transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1);
                display: flex;
                flex-direction: column;
                box-sizing: border-box;
                font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
                color: #f1f5f9;
            }
            .formula-inspector-drawer.open {
                transform: translateX(0);
            }

            .drawer-header {
                padding: 20px 24px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
            }
            .drawer-title {
                font-size: 1.15rem;
                font-weight: 700;
                color: #ffffff;
                margin: 0;
                font-family: 'Space Grotesk', sans-serif;
            }
            .drawer-close-btn {
                background: transparent;
                border: none;
                color: var(--text-muted, #94a3b8);
                font-size: 1.4rem;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: color 0.2s;
            }
            .drawer-close-btn:hover {
                color: var(--accent-default, #64ffda);
            }

            .drawer-body {
                flex: 1;
                overflow-y: auto;
                padding: 24px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }

            .drawer-math-preview {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(3, 7, 18, 0.95) 100%);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 10px;
                padding: 24px 16px;
                text-align: center;
                font-size: 1.4rem;
                color: #ffd700;
                overflow-x: auto;
                max-width: 100%;
                box-sizing: border-box;
                scrollbar-width: thin;
                scrollbar-color: rgba(100, 255, 218, 0.25) transparent;
            }

            .drawer-card {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                padding: 16px;
            }
            .drawer-card-title {
                font-size: 0.76rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                color: var(--accent-default, #64ffda);
                margin: 0 0 8px 0;
                font-weight: 600;
            }

            .drawer-footer {
                padding: 16px 24px;
                border-top: 1px solid rgba(255, 255, 255, 0.08);
                display: flex;
                gap: 12px;
            }
            .drawer-btn-primary {
                flex: 1;
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.15) 0%, rgba(0, 210, 255, 0.15) 100%);
                border: 1px solid rgba(100, 255, 218, 0.3);
                color: var(--accent-default, #64ffda);
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 0.85rem;
                font-weight: 600;
                font-family: 'Space Grotesk', sans-serif;
                cursor: pointer;
                text-align: center;
                text-decoration: none;
                transition: all 0.2s;
            }
            .drawer-btn-primary:hover {
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.25) 0%, rgba(0, 210, 255, 0.25) 100%);
                border-color: var(--accent-default, #64ffda);
            }
        `;
        document.head.appendChild(style);
    },

    createDrawerDOM() {
        if (document.getElementById('formula-inspector-drawer')) return;

        this.backdropEl = document.createElement('div');
        this.backdropEl.className = 'formula-inspector-backdrop';

        this.drawerEl = document.createElement('div');
        this.drawerEl.id = 'formula-inspector-drawer';
        this.drawerEl.className = 'formula-inspector-drawer';
        this.drawerEl.innerHTML = `
            <div class="drawer-header">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 4px; height: 16px; background: var(--accent-default, #64ffda); border-radius: 2px;"></span>
                    <h3 id="drawer-formula-title" class="drawer-title">Inspecting Equation...</h3>
                </div>
                <button id="drawer-close-btn" class="drawer-close-btn">&times;</button>
            </div>
            <div class="drawer-body">
                <div id="drawer-math-target" class="drawer-math-preview">
                    <!-- Rendered LaTeX -->
                </div>

                <div id="drawer-concept-card" class="drawer-card">
                    <h4 class="drawer-card-title">✦ Conceptual Definition</h4>
                    <p id="drawer-concept-text" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">Loading definition...</p>
                </div>

                <div id="drawer-variables-card" class="drawer-card" style="display: none;">
                    <h4 class="drawer-card-title">🔬 Variables &amp; Physical Constants</h4>
                    <div id="drawer-variables-list" style="display: flex; flex-direction: column; gap: 8px;"></div>
                </div>

                <div id="drawer-summary-card" class="drawer-card">
                    <h4 class="drawer-card-title">💡 Intuitive Summary</h4>
                    <p id="drawer-summary-text" style="margin: 0; font-size: 0.9rem; line-height: 1.5; color: #94a3b8; font-style: italic;">Loading summary...</p>
                </div>

                <div id="drawer-graph-card" class="drawer-card" style="display: none;">
                    <h4 class="drawer-card-title">🕸️ Knowledge Graph Ancestry</h4>
                    <div id="drawer-graph-content" style="font-size: 0.85rem; line-height: 1.4; color: #cbd5e1;"></div>
                </div>
            </div>
            <div class="drawer-footer">
                <a id="drawer-workbench-btn" href="/physics/equation-explainer" class="drawer-btn-primary">
                    Open in Full Equation Explainer &rarr;
                </a>
            </div>
        `;

        document.body.appendChild(this.backdropEl);
        document.body.appendChild(this.drawerEl);
    },

    bindEvents() {
        const closeBtn = this.drawerEl.querySelector('#drawer-close-btn');
        closeBtn.addEventListener('click', () => this.close());
        this.backdropEl.addEventListener('click', () => this.close());

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen()) {
                this.close();
            }
        });
    },

    isOpen() {
        return this.drawerEl && this.drawerEl.classList.contains('open');
    },

    open(latex, formulaId = null) {
        if (!latex) return;
        this.currentLatex = latex;
        this.currentFormulaId = formulaId;

        const titleEl = this.drawerEl.querySelector('#drawer-formula-title');
        const targetEl = this.drawerEl.querySelector('#drawer-math-target');
        const conceptText = this.drawerEl.querySelector('#drawer-concept-text');
        const summaryText = this.drawerEl.querySelector('#drawer-summary-text');
        const variablesCard = this.drawerEl.querySelector('#drawer-variables-card');
        const variablesList = this.drawerEl.querySelector('#drawer-variables-list');
        const graphCard = this.drawerEl.querySelector('#drawer-graph-card');
        const graphContent = this.drawerEl.querySelector('#drawer-graph-content');
        const workbenchBtn = this.drawerEl.querySelector('#drawer-workbench-btn');

        titleEl.textContent = 'Inspecting Equation...';
        targetEl.innerHTML = `\\[ ${latex} \\]`;
        conceptText.textContent = 'Analyzing identity...';
        summaryText.textContent = 'Analyzing intuition...';
        variablesCard.style.display = 'none';
        variablesList.innerHTML = '';
        graphCard.style.display = 'none';

        workbenchBtn.href = `/physics/equation-explainer?latex=${encodeURIComponent(latex)}${formulaId ? '&id=' + formulaId : ''}`;

        this.backdropEl.classList.add('visible');
        this.drawerEl.classList.add('open');

        // Typeset MathJax
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([targetEl]).catch(err => console.warn(err));
        }

        // Fetch formula data & graph from API
        const apiUrl = `/physics/equation-explainer?format=json${formulaId ? '&id=' + encodeURIComponent(formulaId) : ''}${latex ? '&latex=' + encodeURIComponent(latex) : ''}`;
        fetch(apiUrl)
            .then(res => res.json())
            .catch(() => null)
            .then(data => {
                if (data && data.formula) {
                    const f = data.formula;
                    const formatMath = (txt) => (window.MathProseFormatter && typeof window.MathProseFormatter.format === 'function') ? window.MathProseFormatter.format(txt) : txt;
                    conceptText.innerHTML = formatMath(f.conceptual_definition) || 'Physical relationship between operators and fields.';
                    summaryText.innerHTML = formatMath(f.intuitive_summary) || 'Calculates the relative dynamics of the system.';

                    // Populate Semantic Variables
                    if (f.semantic_variables && typeof f.semantic_variables === 'object' && Object.keys(f.semantic_variables).length > 0) {
                        variablesCard.style.display = 'block';
                        let varsHtml = '';
                        for (const [sym, vInfo] of Object.entries(f.semantic_variables)) {
                            const name = (vInfo && vInfo.name) ? vInfo.name : sym;
                            const unit = (vInfo && vInfo.unit && vInfo.unit !== 'dimensionless') ? ` [${vInfo.unit}]` : '';
                            const desc = (vInfo && vInfo.description) ? ` — ${formatMath(vInfo.description)}` : '';
                            varsHtml += `
                                <div style="display: flex; align-items: baseline; gap: 8px; font-size: 0.86rem; color: #cbd5e1; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 6px; padding: 6px 10px;">
                                    <span style="color: var(--accent-default, #64ffda); font-weight: 600; font-family: monospace;">\\(${sym}\\)</span>
                                    <span><strong>${name}</strong><span style="color: #94a3b8; font-size: 0.8rem;">${unit}</span>${desc}</span>
                                </div>`;
                        }

                        variablesList.innerHTML = varsHtml;
                    }

                    if (f.parent_formula_id || f.derivation_type || f.constraints) {
                        graphCard.style.display = 'block';
                        let html = '';
                        if (f.derivation_type) {
                            html += `<div style="margin-bottom: 6px;"><strong>Derivation Type:</strong> <span style="color: var(--accent-default, #64ffda); font-weight: 600;">${f.derivation_type}</span></div>`;
                        }
                        if (f.parent_formula_id) {
                            const pName = f.parent_formula_id.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                            html += `<div style="margin-bottom: 6px;"><strong>Master Parent Law:</strong> <a href="/physics/equation-explainer?id=${encodeURIComponent(f.parent_formula_id)}" style="color: var(--accent-default, #64ffda); text-decoration: none; border-bottom: 1px dashed rgba(100,255,218,0.4); font-weight: 600;">${pName}</a></div>`;
                        }
                        if (f.constraints) {
                            try {
                                const c = typeof f.constraints === 'string' ? JSON.parse(f.constraints) : f.constraints;
                                const pills = [];
                                for (const [k, v] of Object.entries(c)) {
                                    let lbl = `${k}: ${v}`;
                                    if (k === 'partial_t' && (v === 0 || v === '0')) lbl = 'Time-Independent (\\(\\partial/\\partial t = 0\\))';
                                    else if (k === 'regime') lbl = `Regime: ${String(v).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
                                    pills.push(`<span style="display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 0.76rem; background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); margin-top: 4px;">${lbl}</span>`);
                                }
                                html += `<div style="margin-top: 6px;"><strong>Physical Constraints:</strong><br>${pills.join(' ')}</div>`;
                            } catch(e) {}
                        }
                        graphContent.innerHTML = html;
                    }
                } else {
                    titleEl.textContent = 'Custom Physics Identity';
                    conceptText.innerHTML = 'This mathematical statement represents a physical relation between variables and vector differential operators.';
                    summaryText.innerHTML = 'It defines how physical fields or particle states evolve and interact under boundary constraints.';
                }

                if (window.MathJax && window.MathJax.typesetPromise) {
                    const elsToTypeset = [conceptText, summaryText];
                    if (variablesList) elsToTypeset.push(variablesList);
                    window.MathJax.typesetPromise(elsToTypeset).catch(err => console.warn(err));
                }
            });
    },

    close() {
        if (this.backdropEl) this.backdropEl.classList.remove('visible');
        if (this.drawerEl) this.drawerEl.classList.remove('open');
    }
};

// Global export & auto init
if (typeof window !== 'undefined') {
    window.FormulaInspector = FormulaInspector;
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => FormulaInspector.init());
    } else {
        FormulaInspector.init();
    }
}
