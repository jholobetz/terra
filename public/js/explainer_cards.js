/**
 * 🔬 PHYSICS LAB: Equation Explainer Cards & Interactive Panels
 *
 * Extracted from equation_explainer.js to isolate secondary UI card renderers:
 * - Knowledge Graph & Lineage Card
 * - Multi-Step Derivation Accordion
 * - Symbolic CAS Asymptotic Limits & Taylor Series Card
 * - Physical Constraints Pills, Topological Bridges, and AI Scenarios
 */

const ExplainerCards = {
    renderKnowledgeGraphCard(formula) {
        const card = document.getElementById('knowledge-graph-card');
        const details = document.getElementById('knowledge-graph-details');
        const canvasContainer = document.getElementById('formula-lineage-graph-canvas');
        if (!card || !details) return;

        if (!formula || !formula.id) {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'flex';

        if (window.FormulaLineageGraph && canvasContainer) {
            if (!this.lineageGraph) {
                this.lineageGraph = new window.FormulaLineageGraph('formula-lineage-graph-canvas', {
                    onNodeClick: (node) => {
                        this.loadFormulaById(node.id);
                    }
                });
            }
            this.lineageGraph.loadFormula(formula.id);
        }

        const hasSubcomponents = Array.isArray(formula.subcomponents) && formula.subcomponents.length > 0;
        let html = '';

        if (formula.derivation_type) {
            html += `<div style="margin-bottom: 10px;"><strong>Derivation Relationship:</strong> <span class="badge-status badge-platinum" style="font-size: 0.72rem; padding: 2px 6px; background: rgba(100,255,218,0.1); color: var(--accent-default, #64ffda); border: 1px solid rgba(100,255,218,0.3); border-radius: 4px;">${formula.derivation_type}</span></div>`;
        }

        if (formula.parent_formula && formula.parent_formula.id) {
            const p = formula.parent_formula;
            const parentUrl = p.url || `/physics/equation-explainer?id=${encodeURIComponent(p.id)}`;
            const safeParentEq = this.escapeMathForHtml(p.equation || '');
            html += `
                <div style="margin-bottom: 14px; background: rgba(100, 255, 218, 0.05); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 4px; font-weight: 600;">⬆ Parent Master Equation</div>
                    <a href="${parentUrl}" style="color: var(--accent-default, #64ffda); text-decoration: none; font-weight: 600; font-size: 1.05rem; display: inline-flex; align-items: center; gap: 8px;">
                        <span>${p.title}</span>
                        ${safeParentEq ? `<span style="color: #ffd700; font-family: monospace;">($\\;${safeParentEq}\\;$)</span>` : ''}
                    </a>
                </div>
            `;
        } else if (formula.parent_formula_id) {
            const parentUrl = `/physics/equation-explainer?id=${encodeURIComponent(formula.parent_formula_id)}`;
            const parentName = formula.parent_formula_id.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `<div style="margin-bottom: 10px;"><strong>Master Parent Law:</strong> <a href="${parentUrl}" style="color: var(--accent-default, #64ffda); text-decoration: none; border-bottom: 1px dashed rgba(100,255,218,0.4); font-weight: 600;">${parentName}</a></div>`;
        }

        if (Array.isArray(formula.derivation_steps) && formula.derivation_steps.length > 0) {
            html += `
                <div style="margin-bottom: 14px; background: rgba(100, 255, 218, 0.04); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 8px; padding: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.75rem; text-transform: uppercase; color: var(--accent-default, #64ffda); font-weight: 600; display: flex; align-items: center; gap: 6px;">
                            <span>📐</span> Mathematical Derivation Pathway (${formula.derivation_steps.length} Steps)
                        </span>
                        <button type="button" class="btn-jump-to-derivation" style="background: rgba(100, 255, 218, 0.1); border: 1px solid rgba(100, 255, 218, 0.3); border-radius: 4px; color: var(--accent-default, #64ffda); font-size: 0.72rem; padding: 3px 8px; cursor: pointer; font-family: 'Space Grotesk', sans-serif;">
                            View Accordion ↗
                        </button>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 6px;">
                        ${formula.derivation_steps.map((st, i) => `
                            <div style="display: flex; align-items: baseline; gap: 8px; font-size: 0.85rem; color: #cbd5e1;">
                                <span style="font-weight: 700; color: #ffd700; font-family: monospace; font-size: 0.8rem;">[Step ${st.step || (i+1)}]</span>
                                <span style="color: #94a3b8; font-size: 0.84rem;">${this.wrapTextMathDelimiters(st.rationale || '')}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }

        if (hasSubcomponents) {
            html += `
                <div style="margin-top: 10px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 8px; font-weight: 600;">⬇ Formula Component Sub-equations (${formula.subcomponents.length})</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">
            `;
            formula.subcomponents.forEach(child => {
                const childId = typeof child === 'string' ? child : child.id;
                const childTitle = typeof child === 'string' ? childId.replace(/-/g, ' ') : child.title;
                let childEq = (typeof child === 'object' && child.equation) ? child.equation : '';
                if (childEq && (childEq.includes(' ') && !childEq.includes('\\') && !childEq.includes('=') && !childEq.includes('+') && !childEq.includes('-'))) {
                    childEq = '';
                }
                const safeChildEq = this.escapeMathForHtml(childEq);
                const childUrl = `/physics/equation-explainer?id=${encodeURIComponent(childId)}`;
                const mathPart = safeChildEq ? `<span style="font-size: 0.9rem; color: #ffd700;">\\(${safeChildEq}\\)</span>` : '';
                html += `
                    <a href="${childUrl}" style="display: flex; flex-direction: column; gap: 4px; padding: 10px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; text-decoration: none; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(100,255,218,0.4)'; this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.08)'; this.style.transform='none'">
                        <span style="font-size: 0.82rem; color: #f1f5f9; font-weight: 600;">${childTitle}</span>
                        ${mathPart}
                    </a>
                `;
            });
            html += `
                    </div>
                </div>
            `;
        }

        if (formula.constraints) {
            try {
                const c = typeof formula.constraints === 'string' ? JSON.parse(formula.constraints) : formula.constraints;
                const pills = this.formatConstraintsToPills(c);
                if (pills) {
                    html += `<div style="margin-top: 10px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><strong>Active Physical Constraints:</strong> ${pills}</div>`;
                }
            } catch(e) {}
        }
        details.innerHTML = html;

        const jumpBtn = details.querySelector('.btn-jump-to-derivation');
        if (jumpBtn) {
            jumpBtn.addEventListener('click', () => {
                const tab = document.querySelector('.explainer-tab-btn[data-target=stage-narrative]');
                if (tab) tab.click();
                setTimeout(() => {
                    const el = document.getElementById('derivation-accordion-section');
                    if (el) el.scrollIntoView({ behavior: 'smooth' });
                }, 100);
            });
        }
        this.triggerTypeset([details]);
    },

    renderDerivationAccordion(formula) {
        if (!this.derivationAccordionSection || !this.derivationStepsList) return;

        const steps = Array.isArray(formula && formula.derivation_steps) ? formula.derivation_steps : [];
        if (steps.length === 0) {
            this.derivationAccordionSection.style.display = 'none';
            this.derivationStepsList.innerHTML = '';
            return;
        }

        this.derivationAccordionSection.style.display = 'flex';
        if (this.derivationStepsCount) {
            this.derivationStepsCount.textContent = `${steps.length} ${steps.length === 1 ? 'Step' : 'Steps'}`;
        }

        let html = '';
        steps.forEach((s, idx) => {
            const stepNum = s.step !== undefined ? s.step : (idx + 1);
            const rationale = this.wrapTextMathDelimiters(s.rationale || '');
            const cleanLatex = (s.latex || '').trim();
            const safeLatex = this.escapeMathForHtml(cleanLatex);
            const isOpen = idx === 0 ? ' open' : '';
            const rawRationale = (s.rationale || '').replace(/<[^>]*>?/gm, '').replace(/\$+/g, '');

            html += `
                <div class="derivation-step-item${isOpen}" data-step="${stepNum}">
                    <div class="derivation-step-header">
                        <div style="display: flex; align-items: center; gap: 10px; min-width: 0;">
                            <span class="derivation-step-pill">Step ${stepNum}</span>
                            <span class="derivation-step-preview" style="font-size: 0.86rem; color: #f1f5f9; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                ${rawRationale}
                            </span>
                        </div>
                        <span class="derivation-step-chevron">▼</span>
                    </div>
                    <div class="derivation-step-content">
                        ${cleanLatex ? `
                            <div class="derivation-step-eq">
                                \\[ ${safeLatex} \\]
                            </div>
                        ` : ''}
                        <div class="derivation-step-rationale">
                            ${rationale}
                        </div>
                    </div>
                </div>
            `;
        });

        this.derivationStepsList.innerHTML = html;

        if (!this._derivationStepsListenerBound) {
            this.derivationStepsList.addEventListener('click', (e) => {
                const header = e.target.closest('.derivation-step-header');
                if (header && header.parentElement) {
                    header.parentElement.classList.toggle('open');
                }
            });
            this._derivationStepsListenerBound = true;
        }

        if (this.btnToggleAllDerivationSteps) {
            this.btnToggleAllDerivationSteps.onclick = () => {
                const items = this.derivationStepsList.querySelectorAll('.derivation-step-item');
                const anyClosed = Array.from(items).some(item => !item.classList.contains('open'));
                items.forEach(item => {
                    if (anyClosed) {
                        item.classList.add('open');
                    } else {
                        item.classList.remove('open');
                    }
                });
                this.btnToggleAllDerivationSteps.textContent = anyClosed ? 'Collapse All' : 'Expand All';
            };
        }

        this.triggerTypeset([this.derivationStepsList]);
    },

    renderCasLimitsCard(latex, semanticVariables = {}) {
        const card = document.getElementById('cas-limits-card');
        const chipsContainer = document.getElementById('cas-quick-limits');
        const resultBox = document.getElementById('cas-result-box');

        if (!card || !chipsContainer || !resultBox || !latex) return;

        card.style.display = 'flex';
        resultBox.style.display = 'none';
        chipsContainer.innerHTML = '';

        const candidateVars = new Set();
        const strippedLatex = latex.replace(/\\[a-zA-Z]+/g, ' ');
        const varMatches = strippedLatex.match(/[a-zA-Z]/g) || [];
        varMatches.forEach(v => {
            if (!['d', 'e', 'i', 'j'].includes(v.toLowerCase())) {
                candidateVars.add(v);
            }
        });

        const quickLimits = [
            { label: 'Classical Limit (v → 0)', var: 'v', to: '0', test: latex.includes('v') },
            { label: 'Non-Relativistic (c → ∞)', var: 'c', to: 'oo', test: latex.includes('c') },
            { label: 'Classical Correspondence (ℏ → 0)', var: 'hbar', to: '0', test: latex.includes('hbar') || latex.includes('\\hbar') },
            { label: 'Ground State (T → 0)', var: 'T', to: '0', test: latex.includes('T') },
            { label: 'Weak Field (r → ∞)', var: 'r', to: 'oo', test: latex.includes('r') },
            { label: 'Small Angle (θ → 0)', var: 'theta', to: '0', test: latex.includes('theta') || latex.includes('\\theta') },
            { label: 'Zero Frequency (ω → 0)', var: 'omega', to: '0', test: latex.includes('omega') || latex.includes('\\omega') }
        ];

        let hasChips = false;
        quickLimits.forEach(ql => {
            if (ql.test) {
                hasChips = true;
                const btn = document.createElement('button');
                btn.className = 'cas-chip-btn';
                btn.style.cssText = 'padding: 5px 12px; background: rgba(168, 85, 247, 0.08); border: 1px solid rgba(168, 85, 247, 0.25); color: #e9d5ff; border-radius: 6px; font-size: 0.8rem; font-family: "Space Grotesk", sans-serif; font-weight: 500; cursor: pointer; transition: all 0.2s;';
                btn.textContent = ql.label;
                btn.onmouseover = () => { btn.style.background = 'rgba(168, 85, 247, 0.2)'; btn.style.borderColor = '#c084fc'; };
                btn.onmouseout = () => { btn.style.background = 'rgba(168, 85, 247, 0.08)'; btn.style.borderColor = 'rgba(168, 85, 247, 0.25)'; };
                btn.onclick = () => this.evaluateCasLimit(latex, ql.var, ql.to, ql.label);
                chipsContainer.appendChild(btn);
            }
        });

        candidateVars.forEach(v => {
            if (!['v', 'c', 'T', 'r'].includes(v)) {
                const btn = document.createElement('button');
                btn.style.cssText = 'padding: 5px 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); color: #cbd5e1; border-radius: 6px; font-size: 0.8rem; font-family: "Space Grotesk", sans-serif; cursor: pointer; transition: all 0.2s;';
                btn.textContent = `Limit (${v} → 0)`;
                btn.onmouseover = () => { btn.style.borderColor = 'rgba(100, 255, 218, 0.4)'; };
                btn.onmouseout = () => { btn.style.borderColor = 'rgba(255, 255, 255, 0.1)'; };
                btn.onclick = () => this.evaluateCasLimit(latex, v, '0', `Asymptotic Limit (${v} → 0)`);
                chipsContainer.appendChild(btn);
                hasChips = true;
            }
        });

        if (!hasChips) {
            chipsContainer.innerHTML = '<span style="font-size: 0.8rem; color: #64748b; font-style: italic;">No free scalar parameters detected for automated limit expansion.</span>';
        }
    },

    evaluateCasLimit(latex, variable, target, label) {
        const resultBox = document.getElementById('cas-result-box');
        const limitMath = document.getElementById('cas-limit-math');
        const seriesMath = document.getElementById('cas-series-math');
        const loadingSpinner = document.getElementById('cas-loading-spinner');
        const evalTitle = document.getElementById('cas-eval-title');

        if (!resultBox || !limitMath) return;

        resultBox.style.display = 'flex';
        loadingSpinner.style.display = 'inline';
        evalTitle.textContent = label || `Evaluating Limit (${variable} → ${target})`;
        limitMath.innerHTML = '<span style="font-size: 0.9rem; color: #94a3b8;">SymPy AST evaluation in progress...</span>';
        seriesMath.style.display = 'none';

        fetch('/physics/api/cas-evaluate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latex: latex,
                limit_var: variable,
                limit_to: target,
                series_order: 4
            })
        })
        .then(res => res.json())
        .then(data => {
            loadingSpinner.style.display = 'none';
            if (!data.success) {
                limitMath.innerHTML = `<span style="font-size: 0.88rem; color: #f87171;">⚠️ ${data.error || 'Evaluation failed.'}</span>`;
                return;
            }

            let targetDisplay = target === 'oo' ? '\\infty' : target;
            let limitVal = (data.limit && data.limit.result_latex) ? data.limit.result_latex : '?';

            limitMath.innerHTML = `\\[ \\lim_{${variable} \\to ${targetDisplay}} \\left( ${data.parsed_latex} \\right) = ${limitVal} \\]`;

            if (data.series && data.series.leading_terms_latex) {
                seriesMath.style.display = 'block';
                seriesMath.innerHTML = `
                    <div style="font-size: 0.78rem; text-transform: uppercase; color: #a855f7; font-weight: 600; margin-bottom: 4px;">Taylor / Asymptotic Series Expansion</div>
                    <div>\\[ ${data.parsed_latex} \\approx ${data.series.leading_terms_latex} + \\mathcal{O}(${variable}^4) \\]</div>
                `;
            } else {
                seriesMath.style.display = 'none';
            }

            this.triggerTypeset([resultBox]);
        })
        .catch(err => {
            loadingSpinner.style.display = 'none';
            limitMath.innerHTML = `<span style="font-size: 0.88rem; color: #f87171;">Network error executing CAS engine.</span>`;
        });
    },

    formatConstraintsToPills(c) {
        if (!c || typeof c !== 'object') return '';
        const pills = [];
        for (const [key, val] of Object.entries(c)) {
            let label = `${key}: ${val}`;
            if (key === 'partial_t' && (val === 0 || val === '0')) {
                label = 'Time-Independent (\\( \\frac{\\partial}{\\partial t} = 0 \\))';
            } else if (key === 'regime') {
                label = `Regime: ${String(val).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
            } else if (key === 'v_c') {
                label = `Relativistic Limit (\\(v \\to c\\))`;
            } else if (key === 'hbar_0') {
                label = `Classical Limit (\\(\\hbar \\to 0\\))`;
            }
            pills.push(`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; background: rgba(168, 85, 247, 0.12); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); font-weight: 500;">${label}</span>`);
        }
        return pills.join(' ');
    },

    renderBridges(subtopics) {
        if (!subtopics || subtopics.length === 0) {
            this.topologicalBridges.style.display = 'none';
            return;
        }

        this.topologicalBridges.style.display = 'block';
        this.bridgesContainer.innerHTML = '';

        subtopics.forEach(st => {
            const link = document.createElement('a');
            link.href = `${BASE_URL}/physics/subtopic/${st.slug}`;
            link.className = 'bridge-tag';
            link.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                ${st.title}
            `;
            this.bridgesContainer.appendChild(link);
        });
    },

    renderAIScenariosSection(scenarios) {
        this.aiScenariosList.innerHTML = '';
        if (!scenarios || scenarios.length === 0) {
            this.aiScenariosSection.style.display = 'none';
            return;
        }

        this.aiScenariosSection.style.display = 'flex';
        scenarios.forEach(sc => {
            const card = document.createElement('div');
            card.className = 'ai-scenario-card';
            card.style.cssText = 'background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;';
            
            const conditionHtml = this.wrapTextMathDelimiters(sc.condition);
            const implicationHtml = this.wrapTextMathDelimiters(sc.implication);

            card.innerHTML = `
                <h4 style="font-size: 0.9rem; font-weight: 600; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; font-family: 'Space Grotesk', sans-serif;">
                    ${conditionHtml}
                </h4>
                <p style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                    ${implicationHtml}
                </p>
            `;
            this.aiScenariosList.appendChild(card);
        });

        this.triggerTypeset([this.aiScenariosList]);
    }
};

if (typeof window !== 'undefined') {
    window.ExplainerCards = ExplainerCards;
    if (window.EquationExplainer) {
        Object.assign(window.EquationExplainer, ExplainerCards);
    }
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExplainerCards;
}
