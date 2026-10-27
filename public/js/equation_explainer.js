/**
 * 🔬 PHYSICS LAB: Interactive Equation Explainer
 * 
 * Manages the LaTeX equation compiler workbench, handles real-time lookups to the database,
 * performs fallback symbol tokenization, and connects analytical tools together.
 */

const EquationExplainer = {
    // State variables
    currentId: null,
    currentLatex: '',
    currentFormula: null,
    currentSubtopics: [],
    navigationStack: [],
    activeBinder: null,

    fallbackBinders: (typeof window !== 'undefined' && window.ExplainerDictionary && window.ExplainerDictionary.fallbackBinders) || [],
    variableDictionary: (typeof window !== 'undefined' && window.ExplainerDictionary && window.ExplainerDictionary.variableDictionary) || {},

    init() {
        if (typeof window !== 'undefined') {
            if (window.ExplainerDictionary) Object.assign(this, window.ExplainerDictionary);
            if (window.ExplainerTokenizer) Object.assign(this, window.ExplainerTokenizer);
            if (window.ExplainerCards) Object.assign(this, window.ExplainerCards);
            if (window.ExplainerSimulations) Object.assign(this, window.ExplainerSimulations);
            if (window.ExplainerCurator) Object.assign(this, window.ExplainerCurator);
        }
        this.activeDomain = '';
        this.cacheElements();
        this.loadReferrerContext();
        this.loadUserCustomizations();
        this.bindEvents();
        this.loadInitialState();
    },

    loadReferrerContext() {
        const urlParams = new URLSearchParams(window.location.search);
        
        // 1. Resolve Active Domain
        const domainParam = urlParams.get('domain') || window.INITIAL_DOMAIN;
        if (domainParam) {
            const DOMAIN_MAP = {
                'classical-mechanics': 'classical_mechanics',
                'thermodynamics-statistical-mechanics': 'thermodynamics',
                'electromagnetism': 'electromagnetism',
                'quantum-physics': 'quantum_mechanics',
                'quantum_mechanics': 'quantum_mechanics',
                'particle-physics': 'quantum_mechanics',
                'standard-model': 'quantum_mechanics',
                'optics': 'optics'
            };
            this.activeDomain = DOMAIN_MAP[domainParam] || domainParam;
            if (this.activeDomainSelect && this.activeDomain) {
                this.activeDomainSelect.value = this.activeDomain;
            }
        }
        
        // 2. Resolve Subtopic variables (from Query param or injected script state)
        const subtopicParam = urlParams.get('subtopic') || window.SUBTOPIC_SLUG;
        if (subtopicParam) {
            window.SUBTOPIC_SLUG = subtopicParam;
            if (!window.SUBTOPIC_VARIABLES || Object.keys(window.SUBTOPIC_VARIABLES).length === 0) {
                fetch(`${BASE_URL}/physics/api/subtopic-variables/${subtopicParam}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.SUBTOPIC_VARIABLES = data.variables || {};
                            if (this.latexInput && this.latexInput.value.trim()) {
                                this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                            }
                        }
                    })
                    .catch(err => console.warn('Could not fetch subtopic variables:', err));
            }
        }

        // 3. Resolve HTTP Referrer Context (when deep linking from a subtopic page without parameters)
        const referrer = document.referrer;
        if (!subtopicParam && referrer && referrer.includes('/physics/subtopic/')) {
            const parts = referrer.split('/');
            const subtopicSlug = parts[parts.length - 1].split('?')[0];
            window.SUBTOPIC_SLUG = subtopicSlug;
            
            // Fetch variables for the referrer subtopic
            fetch(`${BASE_URL}/physics/api/subtopic-variables/${subtopicSlug}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.SUBTOPIC_VARIABLES = data.variables || {};
                        if (this.latexInput && this.latexInput.value.trim()) {
                            this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                        }
                    }
                })
                .catch(err => console.warn('Could not fetch subtopic variables from referrer:', err));
            
            // Map the referrer subtopic back to its physics domain
            fetch(`${BASE_URL}/physics/search-index`)
                .then(res => res.json())
                .then(index => {
                    const entry = index[subtopicSlug];
                    if (entry && entry.s) {
                        const shard = entry.s.replace('.json', '');
                        const DOMAIN_MAP = {
                            'classical-mechanics': 'classical_mechanics',
                            'thermodynamics-statistical-mechanics': 'thermodynamics',
                            'electromagnetism': 'electromagnetism',
                            'quantum-physics': 'quantum_mechanics',
                            'particle-physics': 'quantum_mechanics',
                            'standard-model': 'quantum_mechanics',
                            'optics': 'optics'
                        };
                        this.activeDomain = DOMAIN_MAP[shard] || '';
                        if (this.activeDomain) {
                            console.log(`Detected active domain: ${this.activeDomain} from referrer subtopic ${subtopicSlug}`);
                            if (this.activeDomainSelect) {
                                this.activeDomainSelect.value = this.activeDomain;
                            }
                            if (this.latexInput && this.latexInput.value.trim() && !this.currentId) {
                                this.renderElementsBreakdown(this.latexInput.value.trim(), {});
                            }
                        }
                    }
                })
                .catch(err => console.warn('Could not determine referrer context:', err));
        } else if (!domainParam && !subtopicParam) {
            // Legacy context param fallback
            const contextParam = urlParams.get('context');
            if (contextParam) {
                const DOMAIN_MAP = {
                    'classical-mechanics': 'classical_mechanics',
                    'thermodynamics-statistical-mechanics': 'thermodynamics',
                    'electromagnetism': 'electromagnetism',
                    'quantum-physics': 'quantum_mechanics',
                    'particle-physics': 'quantum_mechanics',
                    'standard-model': 'quantum_mechanics',
                    'optics': 'optics'
                };
                this.activeDomain = DOMAIN_MAP[contextParam] || contextParam;
                if (this.activeDomainSelect && this.activeDomain) {
                    this.activeDomainSelect.value = this.activeDomain;
                }
            }
        }
    },

    drillDownIntoSymbol(symbol, info) {
        this.pushToNavigationStack();
        this.updateUrlParams(symbol, null);
        if (this.latexInput) {
            this.latexInput.value = symbol;
        }
        this.compileMathJax(symbol);
        this.renderSymbolExplanation(symbol, info ? (info.tokenType || info.type) : null);
    },

    pushToNavigationStack() {
        const currentItem = {
            id: this.currentId,
            latex: this.currentLatex,
            formula: this.currentFormula,
            subtopics: this.currentSubtopics,
            title: this.formulaTitle.textContent || this.formulaTitle.innerHTML
        };
        if (this.navigationStack.length > 0) {
            const last = this.navigationStack[this.navigationStack.length - 1];
            if (last.latex === currentItem.latex) return;
        }
        this.navigationStack.push(currentItem);
    },

    popNavigationStack() {
        if (this.navigationStack.length === 0) return;
        const previous = this.navigationStack.pop();
        
        this.currentId = previous.id;
        this.currentLatex = previous.latex;
        this.currentFormula = previous.formula;
        this.currentSubtopics = previous.subtopics;
        
        this.latexInput.value = previous.latex;
        
        this.compileMathJax(previous.latex);
        if (previous.formula) {
            this.renderFormula(previous.formula, previous.subtopics);
        } else {
            this.renderCustomExplanation(previous.latex);
        }
        
        this.updateUrlParams(previous.latex, previous.id);
        this.renderBreadcrumbs();
    },

    updateUrlParams(latex, id) {
        const url = new URL(window.location);
        if (latex) {
            url.searchParams.set('latex', latex);
        } else {
            url.searchParams.delete('latex');
        }
        if (id) {
            url.searchParams.set('id', id);
        } else {
            url.searchParams.delete('id');
        }
        window.history.pushState({}, '', url);
    },

    renderBreadcrumbs() {
        const container = document.getElementById('explainer-breadcrumbs');
        if (!container) return;
        
        console.log("Rendering breadcrumbs, navigation stack length:", this.navigationStack.length);
        
        if (this.navigationStack.length === 0) {
            container.style.display = 'none';
            container.innerHTML = '';
            return;
        }
        
        try {
            container.style.display = 'flex';
            container.innerHTML = '';
            
            const backBtn = document.createElement('button');
            backBtn.style.background = 'transparent';
            backBtn.style.border = 'none';
            backBtn.style.color = 'var(--accent-default, #64ffda)';
            backBtn.style.cursor = 'pointer';
            backBtn.style.fontSize = '0.8rem';
            backBtn.style.padding = '0';
            backBtn.style.display = 'inline-flex';
            backBtn.style.alignItems = 'center';
            backBtn.style.gap = '4px';
            backBtn.style.marginRight = '8px';
            backBtn.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                Back
            `;
            backBtn.addEventListener('click', () => {
                this.popNavigationStack();
            });
            container.appendChild(backBtn);
            
            this.navigationStack.forEach((item, index) => {
                const link = document.createElement('span');
                link.style.cursor = 'pointer';
                link.style.textDecoration = 'underline';
                link.style.textUnderlineOffset = '2px';
                link.style.color = 'var(--text-muted, #94a3b8)';
                
                let text = '';
                if (item.formula) {
                    text = item.title.replace(/\([^\)]+\)/g, '').trim();
                } else {
                    text = '\\( ' + (item.latex || '') + ' \\)';
                }
                
                link.innerHTML = text;
                link.addEventListener('click', () => {
                    while (this.navigationStack.length > index) {
                        this.popNavigationStack();
                    }
                });
                container.appendChild(link);
                
                const separator = document.createElement('span');
                separator.textContent = ' › ';
                separator.style.color = 'rgba(255,255,255,0.2)';
                container.appendChild(separator);
            });
            
            const currentLabel = document.createElement('span');
            currentLabel.style.color = '#ffffff';
            currentLabel.style.fontWeight = '500';
            currentLabel.textContent = '\\( ' + (this.latexInput ? this.latexInput.value : '') + ' \\)';
            container.appendChild(currentLabel);
            
            this.triggerTypeset([container]);
        } catch (e) {
            console.error("Error rendering breadcrumbs:", e);
        }
    },

    renderSymbolExplanation(latex, type = null) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        const symbol = latex.trim();
        
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';
        if (this.aiSimulationCard) this.aiSimulationCard.style.display = 'none';
        if (this.solverRedirectContainer) this.solverRedirectContainer.style.display = 'none';

        let symbolInfo = this.resolveSymbolInfo(symbol, type);

        this.formulaTitle.innerHTML = `${symbolInfo.name} (\\( ${symbol} \\))`;
        if (this.formulaBadge) {
            this.formulaBadge.style.display = 'inline-block';
            if (symbolInfo.type === 'constant') {
                this.formulaBadge.className = 'badge-status';
                this.formulaBadge.style.background = 'rgba(234, 179, 8, 0.1)';
                this.formulaBadge.style.color = '#eab308';
                this.formulaBadge.style.border = '1px solid rgba(234, 179, 8, 0.25)';
                this.formulaBadge.textContent = 'Physical Constant';
            } else {
                this.formulaBadge.className = 'badge-status';
                this.formulaBadge.style.background = 'rgba(59, 130, 246, 0.1)';
                this.formulaBadge.style.color = '#3b82f6';
                this.formulaBadge.style.border = '1px solid rgba(59, 130, 246, 0.25)';
                this.formulaBadge.textContent = 'Physical Variable';
            }
        }

        if (this.conceptualIntroCard) {
            this.conceptualIntroCard.style.display = 'flex';
            
            let valRow = '';
            if (symbolInfo.type === 'constant' && symbolInfo.value) {
                valRow = `
                    <div style="margin-top: 8px; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-family: 'Fira Code', monospace; font-size: 0.88rem;">
                        <span style="color: var(--text-muted, #94a3b8);">Numerical Value:</span>
                        <strong style="color: #fbbf24; margin-left: 6px;">${symbolInfo.value}</strong> 
                        <span style="color: #a8a29e; margin-left: 6px;">${symbolInfo.unit || ''}</span>
                    </div>
                `;
            } else if (symbolInfo.unit && symbolInfo.unit !== 'dimensionless') {
                valRow = `
                    <div style="margin-top: 8px; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-family: 'Fira Code', monospace; font-size: 0.88rem;">
                        <span style="color: var(--text-muted, #94a3b8);">Standard SI Unit:</span>
                        <strong style="color: var(--accent-default, #64ffda); margin-left: 6px;">${symbolInfo.unit}</strong>
                    </div>
                `;
            }

            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Symbol Definition
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${this.wrapTextMathDelimiters(symbolInfo.description)}
                </div>
                ${valRow}
            `;
        }

        this.renderSymbolContextEquations(symbol, symbolInfo);
        this.renderBreadcrumbs();
        this.triggerTypeset([this.formulaTitle, this.conceptualIntroCard]);
    },

    renderSymbolContextEquations(symbol, symbolInfo) {
        this.symbolsList.innerHTML = '';
        
        let equations = symbolInfo.featuredEquations || [];
        
        if (equations.length === 0) {
            this.symbolsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic; padding: 10px;">Select another equation in the editor to see it breakdown into its components.</div>';
            return;
        }

        const header = document.createElement('div');
        header.style.fontSize = '0.85rem';
        header.style.textTransform = 'uppercase';
        header.style.letterSpacing = '0.05em';
        header.style.color = 'var(--text-muted, #94a3b8)';
        header.style.marginBottom = '12px';
        header.style.fontFamily = "'Space Grotesk', sans-serif";
        header.textContent = `Featured Equations with ${symbol}`;
        this.symbolsList.appendChild(header);

        equations.forEach(eq => {
            const row = document.createElement('div');
            row.className = 'symbol-row';
            row.style.cursor = 'pointer';
            row.style.transition = 'all 0.2s';
            row.style.border = '1px solid rgba(255, 255, 255, 0.04)';
            
            row.addEventListener('mouseover', () => {
                row.style.background = 'rgba(100, 255, 218, 0.03)';
                row.style.borderColor = 'rgba(100, 255, 218, 0.2)';
            });
            row.addEventListener('mouseout', () => {
                row.style.background = '';
                row.style.borderColor = 'rgba(255, 255, 255, 0.04)';
            });
            
            row.addEventListener('click', () => {
                this.navigationStack = [];
                this.latexInput.value = eq.latex;
                this.handleInputChange();
            });

            row.innerHTML = `
                <div class="symbol-badge" style="background: rgba(100, 255, 218, 0.05); border-color: rgba(100, 255, 218, 0.15); color: var(--accent-default, #64ffda); font-size: 0.8rem; padding: 4px 8px; border-radius: 4px; font-family: 'Space Grotesk', sans-serif;">EQ</div>
                <div class="symbol-content-wrapper" style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <strong style="color: #ffffff; font-size: 0.92rem;">${eq.name}</strong>
                    <div style="font-family: 'Fira Code', monospace; font-size: 0.82rem; color: var(--text-muted, #94a3b8); margin-top: 2px;">$${eq.latex}$</div>
                </div>
            `;
            this.symbolsList.appendChild(row);
        });

        this.triggerTypeset([this.symbolsList]);
    },

    loadUserCustomizations() {
        try {
            // Load custom definitions from local storage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('physics_explainer_custom_')) {
                    const symbol = key.replace('physics_explainer_custom_', '');
                    const value = JSON.parse(localStorage.getItem(key));
                    if (value) {
                        this.userCustomizations[symbol] = value;
                    }
                }
            }
        } catch (err) {
            console.warn('Could not load user customizations:', err);
        }
    },

    cacheElements() {
        this.latexInput = document.getElementById('latex-input');
        this.clearBtn = document.getElementById('clear-input-btn');
        this.copyBtn = document.getElementById('copy-input-btn');
        this.mathRenderTarget = document.getElementById('math-render-target');
        this.compilerStatus = document.getElementById('compiler-status');
        
        this.formulaTitle = document.getElementById('formula-title');
        this.formulaBadge = document.getElementById('formula-badge');
        this.conceptualIntroCard = document.getElementById('conceptual-intro-card');
        
        this.aiScenariosSection = document.getElementById('ai-scenarios-section');
        this.aiScenariosList = document.getElementById('ai-scenarios-list');
        this.aiSimulationCard = document.getElementById('ai-simulation-card');
        this.sandboxCanvas = document.getElementById('sandbox-canvas');
        this.sandboxSliders = document.getElementById('sandbox-sliders');
        this.sonifyToggleBtn = document.getElementById('sonify-toggle-btn');
        
        this.officialBreakdown = document.getElementById('official-breakdown');
        this.symbolsBreakdown = document.getElementById('symbols-breakdown');
        this.symbolsList = document.getElementById('symbols-list');
        this.operatorsSection = document.getElementById('operators-section');
        this.operatorsList = document.getElementById('operators-list');
        this.modifiersSection = document.getElementById('modifiers-section');
        this.modifiersList = document.getElementById('modifiers-list');
        this.topologicalBridges = document.getElementById('topological-bridges');
        this.bridgesContainer = document.getElementById('bridges-container');
        this.explainerPlaceholder = document.getElementById('explainer-placeholder');
        this.solverRedirectContainer = document.getElementById('solver-redirect-container');
        this.solverRedirectLink = document.getElementById('solver-redirect-link');
        this.activeDomainSelect = document.getElementById('active-domain-select');
        this.autocompleteDropdown = document.getElementById('latex-autocomplete-dropdown');
        this.explainerNavTabs = document.getElementById('explainer-nav-tabs');
        this.tabButtons = document.querySelectorAll('.explainer-tab-btn');
        this.tabPanes = document.querySelectorAll('.explainer-tab-pane');

        this.derivationAccordionSection = document.getElementById('derivation-accordion-section');
        this.derivationStepsList = document.getElementById('derivation-steps-list');
        this.derivationStepsCount = document.getElementById('derivation-steps-count');
        this.btnToggleAllDerivationSteps = document.getElementById('btn-toggle-all-derivation-steps');
    },

    bindEvents() {
        // Tab switching
        if (this.tabButtons) {
            this.tabButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const targetId = btn.getAttribute('data-target');
                    this.switchTab(targetId);
                });
            });
        }

        if (this.activeDomainSelect) {
            this.activeDomainSelect.addEventListener('change', (e) => {
                this.activeDomain = e.target.value;
                if (this.latexInput && this.latexInput.value.trim()) {
                    this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                }
            });
        }

        // Close autocomplete when clicking outside
        document.addEventListener('click', (e) => {
            if (this.autocompleteDropdown && this.latexInput && !this.latexInput.contains(e.target) && !this.autocompleteDropdown.contains(e.target)) {
                this.autocompleteDropdown.style.display = 'none';
            }
        });

        // Handle browser back/forward buttons natively
        window.addEventListener('popstate', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            const latex = urlParams.get('latex');
            
            this.navigationStack = []; // Reset stack on external history change
            
            if (id) {
                fetch(`${BASE_URL}/physics/api/explain?latex=` + encodeURIComponent(latex || '') + `&id=${id}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success && data.formula) {
                            this.currentId = data.formula.id;
                            this.currentLatex = data.formula.latex_source || this.getCleanLatexFromEq(data.formula.equation);
                            this.latexInput.value = this.currentLatex;
                            this.compileMathJax(this.currentLatex);
                            this.renderFormula(data.formula, []);
                            this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                                if (this.currentId === data.formula.id) {
                                    this.currentSubtopics = subtopics;
                                    this.renderBridges(subtopics);
                                }
                            });
                        }
                    });
            } else if (latex) {
                this.latexInput.value = latex;
                this.compileMathJax(latex);
                if (this.isSingleSymbol(latex)) {
                    this.renderSymbolExplanation(latex);
                } else {
                    this.lookupFormulaByLatex(latex);
                }
            } else {
                this.resetExplanation();
            }
        });

        // Debounced input compiling and autocomplete
        this.latexInput.addEventListener('input', () => {
            this.setCompilerStatus('Compiling...', '#fbbf24');
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.handleInputChange();
                if (this.latexInput && this.latexInput.value.trim()) {
                    this.fetchAutocompleteSuggestions(this.latexInput.value.trim());
                } else if (this.autocompleteDropdown) {
                    this.autocompleteDropdown.style.display = 'none';
                }
            }, 300);
        });

        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.latexInput.value = '';
            if (this.autocompleteDropdown) this.autocompleteDropdown.style.display = 'none';
            this.handleInputChange();
            this.latexInput.focus();
        });

        // Copy button to copy LaTeX input to clipboard
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => {
                const latex = this.latexInput.value;
                if (!latex) return;
                
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(latex).then(() => {
                        this.copyBtn.textContent = 'Copied!';
                        this.copyBtn.style.color = 'var(--accent-default, #64ffda)';
                        setTimeout(() => {
                            this.copyBtn.textContent = 'Copy';
                            this.copyBtn.style.color = '#eab308';
                        }, 1500);
                    });
                } else {
                    // Fallback
                    this.latexInput.select();
                    document.execCommand('copy');
                    this.copyBtn.textContent = 'Copied!';
                    this.copyBtn.style.color = 'var(--accent-default, #64ffda)';
                    setTimeout(() => {
                        this.copyBtn.textContent = 'Copy';
                        this.copyBtn.style.color = '#eab308';
                    }, 1500);
                }
            });
        }

        // Sonification toggle
        if (this.sonifyToggleBtn) {
            this.sonifyToggleBtn.addEventListener('click', () => {
                this.toggleSonification();
            });
        }

        // Initialize Curator Drawer
        this.initCuratorDrawer();
    },

    switchTab(targetId) {
        if (!this.tabButtons || !this.tabPanes) return;

        // Update button states
        this.tabButtons.forEach(btn => {
            if (btn.getAttribute('data-target') === targetId) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });

        // Update stage visibility
        this.tabPanes.forEach(pane => {
            if (pane.id === targetId) {
                if (pane.classList.contains('explainer-grid')) {
                    pane.style.display = 'grid';
                } else {
                    pane.style.display = 'flex';
                }
            } else {
                pane.style.display = 'none';
            }
        });

        // If switching to Lineage graph stage, trigger reset/fit on full-width canvas
        if (targetId === 'stage-lineage' && this.lineageGraph) {
            requestAnimationFrame(() => {
                if (this.currentFormula && this.currentFormula.id) {
                    this.lineageGraph.loadFormula(this.currentFormula.id);
                } else if (this.lineageGraph.resetView) {
                    this.lineageGraph.resetView();
                }
            });
        }

        // Trigger MathJax typeset on the activated stage
        const activePane = document.getElementById(targetId);
        if (activePane) {
            this.triggerTypeset([activePane]);
        }
    },

    loadInitialState() {
        if (window.INITIAL_FORMULA) {
            // Server pre-loaded from formula ID or initial lookup
            const formula = window.INITIAL_FORMULA;
            this.currentId = formula.id;
            this.currentLatex = formula.latex_source || this.getCleanLatexFromEq(formula.equation);
            this.latexInput.value = this.currentLatex;
            
            this.compileMathJax(this.currentLatex);
            this.renderFormula(formula, window.INITIAL_SUBTOPICS || []);
        } else if (window.INITIAL_LATEX) {
            // Just raw LaTeX passed
            let rawLatex = (window.INITIAL_LATEX || '').trim().replace(/^['"\s]+|['"\s]+$/g, '');
            const quotePos = rawLatex.indexOf("'");
            if (quotePos > 0 && /'\s*(?:\\text|\\mathrm|\\mathbf|[a-zA-Z]{2,})/.test(rawLatex.slice(quotePos))) {
                rawLatex = rawLatex.substring(0, quotePos).trim();
            }
            this.latexInput.value = rawLatex;
            this.handleInputChange();
        } else {
            // Set defaults or display placeholder
            this.resetExplanation();
        }
    },

    getCleanLatexFromEq(eqStr) {
        if (!eqStr) return '';
        if (eqStr.includes('data-tex=')) {
            const match = eqStr.match(/data-tex="([^"]+)"/);
            if (match) return this.decodeHtmlEntities(match[1]).replace(/\\par\b/g, ' ');
        }
        if (eqStr.trim().startsWith('<svg') || eqStr.trim().startsWith('<div') || eqStr.trim().startsWith('<g')) {
            return '';
        }
        return eqStr.replace(/^\\\[/, '').replace(/\\\]$/, '').trim().replace(/\\par\b/g, ' ');
    },

    decodeHtmlEntities(str) {
        const txt = document.createElement("textarea");
        txt.innerHTML = str;
        return txt.value;
    },

    escapeMathForHtml(str) {
        if (typeof str !== 'string' || !str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    },

    handleInputChange() {
        let latex = (this.latexInput ? this.latexInput.value : '').trim().replace(/^['"\s]+|['"\s]+$/g, '');
        const quotePos = latex.indexOf("'");
        if (quotePos > 0 && /'\s*(?:\\text|\\mathrm|\\mathbf|[a-zA-Z]{2,})/.test(latex.slice(quotePos))) {
            latex = latex.substring(0, quotePos).trim();
            if (this.latexInput) this.latexInput.value = latex;
        }
        this.currentLatex = latex;
        this.currentId = null; // Typing custom formula clears registered ID

        if (latex === '') {
            this.mathRenderTarget.innerHTML = '<span style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.1rem; opacity: 0.5;">Enter an equation to compile...</span>';
            this.setCompilerStatus('Ready', '#10b981');
            this.resetExplanation();
            return;
        }

        // 1. Compile MathJax preview
        this.compileMathJax(latex);

        // 2. Immediately render local component breakdown (0ms instant UI feedback)
        this.renderElementsBreakdown(latex, this.officialVariables || {});

        // 3. Route single symbols directly
        if (this.isSingleSymbol(latex)) {
            this.renderSymbolExplanation(latex);
            return;
        }

        // 4. Perform database lookup
        this.lookupFormulaByLatex(latex);
    },

    async fetchAutocompleteSuggestions(query) {
        if (!this.autocompleteDropdown) return;
        const clean = (query || '').trim();
        if (clean.length < 2) {
            this.autocompleteDropdown.style.display = 'none';
            return;
        }

        try {
            // Query search API (matches both keywords, formula titles, and semantic concepts)
            let res = await fetch(`${BASE_URL}/physics/api/search?q=${encodeURIComponent(clean)}&limit=6`);
            let data = await res.json();
            let items = (data.results || []).filter(r => r.type === 'formula' && r.equation);

            // If few formula matches, try semantic search
            if (items.length < 2) {
                const semRes = await fetch(`${BASE_URL}/physics/api/semantic-search?q=${encodeURIComponent(clean)}&limit=5`);
                if (semRes.ok) {
                    const semData = await semRes.json();
                    if (semData.results && semData.results.length > 0) {
                        const existingIds = new Set(items.map(i => i.id));
                        for (const sr of semData.results) {
                            if (!existingIds.has(sr.id)) {
                                items.push({
                                    type: 'formula',
                                    id: sr.id,
                                    title: sr.title,
                                    equation: sr.equation,
                                    confidence: sr.confidence
                                });
                            }
                        }
                    }
                }
            }

            if (items.length === 0) {
                this.autocompleteDropdown.style.display = 'none';
                return;
            }

            this.autocompleteDropdown.innerHTML = items.map(item => `
                <div class="latex-suggestion-item" data-eq="${encodeURIComponent(item.equation)}" style="padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,0.06); cursor: pointer; transition: background 0.15s; display: flex; flex-direction: column; gap: 4px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-family: 'Space Grotesk', sans-serif; font-size: 0.85rem; font-weight: 600; color: #ffffff;">${item.title}</span>
                        ${item.confidence ? `<span style="font-size: 0.7rem; color: #10b981; background: rgba(16, 185, 129, 0.15); padding: 1px 6px; border-radius: 4px;">✨ ${item.confidence} Match</span>` : ''}
                    </div>
                    <div style="font-family: 'Fira Code', monospace; font-size: 0.8rem; color: #64ffda; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        \\(${item.equation}\\)
                    </div>
                </div>
            `).join('');

            this.autocompleteDropdown.querySelectorAll('.latex-suggestion-item').forEach(el => {
                el.addEventListener('mouseenter', () => el.style.background = 'rgba(100, 255, 218, 0.12)');
                el.addEventListener('mouseleave', () => el.style.background = 'transparent');
                el.addEventListener('click', (e) => {
                    const eq = decodeURIComponent(el.getAttribute('data-eq'));
                    this.latexInput.value = eq;
                    this.autocompleteDropdown.style.display = 'none';
                    this.handleInputChange();
                });
            });

            this.autocompleteDropdown.style.display = 'block';

            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this.autocompleteDropdown]).catch(e => {});
            }
        } catch (e) {
            console.warn('Autocomplete fetch failed:', e);
        }
    },

    compileMathJax(latex) {
        if (typeof latex !== 'string' || !latex) return;
        
        let cleanedLatex = latex.replace(/\\par\b/g, ' ').trim();
        
        const knownTexCmds = new Set([
            'delta', 'alpha', 'beta', 'gamma', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa',
            'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
            'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega',
            'frac', 'sqrt', 'left', 'right', 'partial', 'infty', 'approx', 'to', 'le', 'ge', 'ne', 'equiv',
            'sim', 'simeq', 'propto', 'nabla', 'cdot', 'times', 'div', 'pm', 'mp', 'ast', 'star',
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp', 'lim', 'max', 'min', 'sum', 'int', 'prod',
            'lozenge', 'iff', 'exists', 'in', 'vDash', 'vdash', 'models', 'forall', 'subset', 'supset',
            'cup', 'cap', 'implies', 'Rightarrow', 'Leftarrow', 'Leftrightarrow', 'coprod', 'oint', 'iint', 'iiint',
            'dim', 'det', 'ker', 'tr', 'diag', 'rank', 'supp', 'span', 'bra', 'ket', 'braket',
            'text', 'mathrm', 'mathbf', 'mathcal', 'mathbb', 'operatorname', 'quad', 'qquad', 'vec', 'hat', 'bar', 'dot', 'ddot', 'tilde',
            'begin', 'end', 'pmatrix', 'matrix', 'bmatrix', 'vmatrix', 'Vmatrix', 'cases', 'align', 'aligned', 'gather', 'gathered', 'split', 'array', 'multline'
        ]);

        // 1. Protect existing backslashed LaTeX macros and macro environments (e.g. \text{enc}, \mathbf{v}_d, \begin{pmatrix}...\end{pmatrix})
        const macroPlaceholders = [];
        let tempLatex = cleanedLatex.replace(/(?:\\(?:text|mathrm|mathbf|mathcal|mathbb|operatorname|vec|hat|bar|dot|ddot|tilde|frac|sqrt|color)\{(?:[^{}]|\{[^{}]*\})*\}|\\(?:begin|end)\{[a-zA-Z*]+\}|\\[a-zA-Z]+|\\[^a-zA-Z])/g, (match) => {
            macroPlaceholders.push(match);
            return `___TEXMACRO_${macroPlaceholders.length - 1}___`;
        });

        // 2. Wrap un-escaped Multi-Letter variables/words in \text{} unless known TeX commands
        tempLatex = tempLatex.replace(/\b([a-zA-Z]{2,})\b/g, (match) => {
            if (knownTexCmds.has(match) || knownTexCmds.has(match.toLowerCase())) {
                return `\\${match}`;
            }
            return `\\text{${match}}`;
        });

        // 3. Restore backslashed LaTeX macros
        for (let i = 0; i < macroPlaceholders.length; i++) {
            tempLatex = tempLatex.replace(`___TEXMACRO_${i}___`, () => macroPlaceholders[i]);
        }

        let formattedLatex = tempLatex;

        // Enforce equation delimiters
        let mathMarkup = formattedLatex;
        if (!formattedLatex.startsWith('\\[') && !formattedLatex.startsWith('\\(') && !formattedLatex.startsWith('$$') && !formattedLatex.startsWith('$')) {
            mathMarkup = '\\[ ' + formattedLatex + ' \\]';
        }

        this.mathRenderTarget.textContent = mathMarkup;

        const runCompile = (retryCount = 0) => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                if (window.MathJax.typesetClear) {
                    try {
                        window.MathJax.typesetClear([this.mathRenderTarget]);
                    } catch (e) {}
                }
                window.MathJax.typesetPromise([this.mathRenderTarget])
                    .then(() => {
                        this.setCompilerStatus('Ready', '#10b981');
                    })
                    .catch((err) => {
                        console.error('MathJax Compilation Error:', err);
                        this.setCompilerStatus('Syntax Error', '#ef4444');
                    });
            } else if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
                this.setCompilerStatus('Loading Engine...', '#f59e0b');
                window.MathJax.startup.promise.then(() => {
                    if (window.MathJax.typesetClear) {
                        try {
                            window.MathJax.typesetClear([this.mathRenderTarget]);
                        } catch (e) {}
                    }
                    window.MathJax.typesetPromise([this.mathRenderTarget])
                        .then(() => {
                            this.setCompilerStatus('Ready', '#10b981');
                        })
                        .catch((err) => {
                            console.error('MathJax Compilation Error (deferred):', err);
                            this.setCompilerStatus('Syntax Error', '#ef4444');
                        });
                });
            } else if (retryCount < 30) {
                this.setCompilerStatus('Loading Engine...', '#f59e0b');
                setTimeout(() => runCompile(retryCount + 1), 100);
            } else {
                this.setCompilerStatus('Renderer Offline', '#f59e0b');
            }
        };

        runCompile();
    },

    triggerTypeset(elements) {
        if (!elements || elements.length === 0) return;

        const runTypeset = (retryCount = 0) => {
            if (window.MathJax && window.MathJax.typesetPromise) {
                if (window.MathJax.typesetClear) {
                    try {
                        window.MathJax.typesetClear(elements);
                    } catch (err) {
                        console.warn('MathJax typesetClear failed:', err);
                    }
                }
                window.MathJax.typesetPromise(elements)
                    .catch(err => console.warn('MathJax typesetting failed:', err));
            } else if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise.then(() => {
                    if (window.MathJax.typesetClear) {
                        try {
                            window.MathJax.typesetClear(elements);
                        } catch (e) {}
                    }
                    window.MathJax.typesetPromise(elements)
                        .catch(err => console.warn('MathJax typesetting failed (deferred):', err));
                });
            } else if (retryCount < 30) {
                setTimeout(() => runTypeset(retryCount + 1), 100);
            }
        };

        runTypeset();
    },

    setCompilerStatus(text, color) {
        if (!this.compilerStatus) return;
        this.compilerStatus.textContent = text;
        this.compilerStatus.style.color = color;
        const dot = this.compilerStatus.querySelector('span') || document.createElement('span');
        dot.style.background = color;
        // Only show if actively compiling or erroring; hide on Ready
        if (text === 'Compiling...' || text.includes('Error')) {
            this.compilerStatus.style.display = 'inline-flex';
            if (text === 'Compiling...') {
                dot.style.animation = 'pulse 1s infinite alternate';
            } else {
                dot.style.animation = '';
            }
        } else {
            this.compilerStatus.style.display = 'none';
        }
    },

    lookupFormulaByLatex(latex) {
        // Request database matching
        fetch(`${BASE_URL}/physics/api/explain?latex=` + encodeURIComponent(latex))
            .then(res => res.json())
            .then(data => {
                if (data.success && data.formula) {
                    // Match found! Load official sharded content
                    this.currentId = data.formula.id;
                    
                    // Render formula immediately
                    this.renderFormula(data.formula, []);

                    // Fetch referencing subtopics in background
                    this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                        if (this.currentId === data.formula.id) {
                            this.currentSubtopics = subtopics;
                            this.renderBridges(subtopics);
                        }
                    });
                } else {
                    // Unregistered equation: parse variables and constants locally
                    this.renderCustomExplanation(latex);
                }
            })
            .catch(err => {
                console.warn('API lookup failed, falling back to local analysis:', err);
                this.renderCustomExplanation(latex);
            });
    },

    fetchSubtopicsForFormula(id) {
        return fetch(`${BASE_URL}/physics/search-index`)
            .then(res => res.json())
            .then(index => {
                const results = [];
                const cleanId = id.replace(/-/g, ' ');
                for (const [slug, item] of Object.entries(index)) {
                    const isSubtopic = item.s && !item.s.startsWith('topics/');
                    if (isSubtopic && item.k) {
                        const hasFormula = item.k.some(kw => kw === cleanId || kw === id.toLowerCase() || kw.includes(cleanId));
                        if (hasFormula) {
                            results.push({
                                slug: slug,
                                title: item.t
                            });
                        }
                    }
                }
                return results;
            })
            .catch(err => {
                console.warn('Could not load referencing subtopics:', err);
                return [];
            });
    },

    loadFormulaById(id) {
        if (!id) return;
        fetch(`${BASE_URL}/physics/api/explain?id=${encodeURIComponent(id)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.formula) {
                    this.currentId = data.formula.id;
                    this.currentLatex = data.formula.latex_source || this.getCleanLatexFromEq(data.formula.equation);
                    if (this.latexInput) {
                        this.latexInput.value = this.currentLatex;
                    }
                    this.compileMathJax(this.currentLatex);
                    
                    // Render formula immediately
                    this.renderFormula(data.formula, []);

                    this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                        if (this.currentId === data.formula.id) {
                            this.currentSubtopics = subtopics;
                            this.renderBridges(subtopics);
                        }
                    });
                    
                    const url = new URL(window.location);
                    url.searchParams.set('id', data.formula.id);
                    url.searchParams.delete('latex');
                    window.history.pushState({}, '', url);
                }
            })
            .catch(err => console.warn('Could not load formula by id:', err));
    },

    renderFormula(formula, subtopics) {
        this.currentFormula = formula;
        this.currentSubtopics = subtopics;

        // Display status
        this.explainerPlaceholder.style.display = 'none';
        if (this.explainerNavTabs) this.explainerNavTabs.style.display = 'flex';
        
        // Ensure active stage is displayed
        let activeTab = document.querySelector('.explainer-tab-btn.active');
        let activeStageId = activeTab ? activeTab.getAttribute('data-target') : 'stage-narrative';
        this.switchTab(activeStageId);

        this.officialBreakdown.style.display = 'none'; // Keep legacy tiers container hidden, we map them below
        this.symbolsBreakdown.style.display = 'block';
        
        // Populate Title and Badge
        this.formulaTitle.textContent = formula.title;
        
        // Status formatting
        const status = formula.status || 'platinum-draft';
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status ' + (status.includes('draft') || status.includes('synthesized') ? 'badge-draft' : 'badge-platinum');
            this.formulaBadge.textContent = status.replace('-', ' ').toUpperCase();
        }

        // CAS Verification Badge
        const casBadge = document.getElementById('cas-verified-badge');
        const casText = document.getElementById('cas-verified-text');
        if (casBadge && casText) {
            const casVal = formula.cas_validation;
            if (casVal && casVal.is_homogeneous) {
                casBadge.style.display = 'inline-flex';
                const qty = casVal.quantity || 'Homogeneous';
                casText.textContent = `CAS: ${qty}`;
                const dimInfo = casVal.dimension_latex ? ` [${casVal.dimension_latex}]` : '';
                casBadge.title = `Symbolic CAS Verified: Homogeneous physical dimensions${dimInfo}`;
            } else {
                casBadge.style.display = 'none';
            }
        }

        // Update Curation Drawer button label contextually
        const btnCuratorLabel = document.getElementById('btn-curator-label');
        if (btnCuratorLabel) {
            const isSynthesized = formula.status === 'synthesized-ast' || formula.title === 'Custom Physical Relation' || formula.is_synthesized || !formula.id;
            btnCuratorLabel.textContent = isSynthesized ? 'Propose / Register Equation' : 'Curate / Suggest Fix';
        }

        const synthesis = this.synthesizeCustomOverview(this.currentLatex);

        // Populate Conceptual Definition / Google-style summary at the top
        if (this.conceptualIntroCard) {
            const definition = this.wrapTextMathDelimiters(formula.conceptual_definition || synthesis.intro);
            const summary = this.wrapTextMathDelimiters(formula.intuitive_summary || synthesis.summary);
            
            this.conceptualIntroCard.style.display = 'flex';
            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Explanation
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${definition}
                </div>
                <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                    ${summary}
                </div>
            `;
            this.triggerTypeset([this.conceptualIntroCard]);
        }

        // Build and render scenarios
        let scenarios = formula.scenarios;
        if (!scenarios || scenarios.length === 0) {
            // Map legacy tiers to scenarios
            scenarios = [];
            if (formula.interpretation && formula.interpretation !== 'No interpretation provided.') {
                scenarios.push({
                    condition: 'Interpretation (Local Identity)',
                    implication: formula.interpretation
                });
            }
            if (formula.symmetry_origin && formula.symmetry_origin !== 'Symmetry derivations pending.') {
                scenarios.push({
                    condition: 'Symmetry & Coordinate Invariance',
                    implication: formula.symmetry_origin
                });
            }
            if (formula.limits_and_boundary && formula.limits_and_boundary !== 'Boundary analysis pending.') {
                scenarios.push({
                    condition: 'Limiting Cases & Boundaries',
                    implication: formula.limits_and_boundary
                });
            }

            // If still empty, use synthesis fallback
            if (scenarios.length === 0) {
                scenarios = synthesis.scenarios;
            }
        }
        this.renderAIScenariosSection(scenarios);

        // Render Knowledge Graph Ancestry card
        this.renderKnowledgeGraphCard(formula);

        // Render Step-by-Step Derivation Accordion
        this.renderDerivationAccordion(formula);

        // Deconstruct EVERY element in the LaTeX string, merging database semantic definitions for left panel hover list
        this.renderElementsBreakdown(this.currentLatex, formula.semantic_variables || {});

        // Populate Topological Bridges
        this.renderBridges(subtopics);

        // Setup Dimensional Solver Link
        this.setupSolverLink(this.currentLatex);

        // Render Symbolic CAS & Asymptotic Limits Card
        this.renderCasLimitsCard(this.currentLatex, formula.semantic_variables || {});

        // Initialize sandbox simulator
        this.initSandbox(this.currentLatex, formula.semantic_variables || {});
    },

    renderCustomExplanation(latex) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        // Hide old layout elements
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';

        // Deconstruct EVERY element in the custom LaTeX string first to populate activeBinder
        this.renderElementsBreakdown(latex, {});

        // Synthesize dynamic AI Overview
        const synthesis = this.synthesizeCustomOverview(latex);

        // Title and Badge
        this.formulaTitle.textContent = this.activeBinder ? this.activeBinder.name : (synthesis.title || 'Custom Physics Formula');
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status badge-unregistered';
            this.formulaBadge.textContent = 'Live Analysis';
        }

        if (this.conceptualIntroCard) {
            this.conceptualIntroCard.style.display = 'flex';
            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Explanation
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${this.wrapTextMathDelimiters(synthesis.intro)}
                </div>
                <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                    ${this.wrapTextMathDelimiters(synthesis.summary)}
                </div>
            `;
            this.triggerTypeset([this.conceptualIntroCard]);
        }

        // Render AI scenarios
        this.renderAIScenariosSection(synthesis.scenarios);

        // Setup Dimensional Solver Link
        this.setupSolverLink(latex);

        // Render Symbolic CAS & Asymptotic Limits Card
        this.renderCasLimitsCard(latex, {});

        // Initialize sandbox simulator
        this.initSandbox(latex, {});
    },

    renderElementsBreakdown(latex, officialVariables) {
        if (this.symbolsBreakdown) {
            this.symbolsBreakdown.style.display = 'block';
        }
        this.symbolsList.innerHTML = '';
        if (this.operatorsList) {
            this.operatorsList.innerHTML = '';
        }
        if (this.modifiersList) {
            this.modifiersList.innerHTML = '';
        }
        
        // Save officialVariables for redraw on domain change, normalizing keys and filtering out corrupted operator/delimiter tokens
        this.officialVariables = {};
        const structuralBlacklist = new Set([
            '\\rangle', '\\langle', '\\mid', '|', '(', ')', '[', ']', '{', '}', '+', '-', '=', '/', 
            '\\cdot', '\\times', '\\div', '\\left', '\\right', '\\text', '\\mathrm', '\\mathsf',
            '\\colon', '\\quad', '\\qquad', '\\dots', '\\cdots', '\\ldots', '\\ddots', '\\vdots',
            '\\circ', '\\bullet'
        ]);

        if (officialVariables) {
            for (const [key, val] of Object.entries(officialVariables)) {
                const cleanKey = key.trim()
                                    .replace(/^\\\(/, '')
                                    .replace(/\\\)$/, '')
                                    .replace(/^\\\[/, '')
                                    .replace(/\\\]$/, '')
                                    .replace(/^\$\$/, '')
                                    .replace(/\$\$$/, '')
                                    .replace(/^\$/, '')
                                    .replace(/\$/, '')
                                    .trim();

                // Skip structural delimiters or placeholder corrupted parameters
                if (structuralBlacklist.has(cleanKey) || structuralBlacklist.has('\\' + cleanKey)) {
                    continue;
                }
                if (typeof val === 'object' && val !== null) {
                    if (val.description === 'Physics variable or parameter.' && (val.name || '').endsWith(' Parameter')) {
                        continue;
                    }
                }
                this.officialVariables[cleanKey] = val;
            }
        }
        
        // Match fallback binders if present
        this.activeBinder = null;
        if (latex) {
            for (const binder of this.fallbackBinders) {
                if (binder.matchPattern.test(latex)) {
                    this.activeBinder = binder;
                    if (!this.activeDomain) {
                        this.activeDomain = binder.domain;
                        if (this.activeDomainSelect) {
                            this.activeDomainSelect.value = binder.domain;
                        }
                    }
                    console.log(`Matched fallback binder: ${binder.name}`);
                    break;
                }
            }
        }
        
        const effectiveDomain = this.activeDomain || this.detectDomainFromLatex(latex) || 'classical_mechanics';

        const tokens = this.extractAllMathTokens(latex, this.officialVariables);
        
        if (tokens.length === 0) {
            this.symbolsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">No math variables, constants, or operators detected.</div>';
            if (this.operatorsSection) {
                this.operatorsSection.style.display = 'none';
            }
            if (this.modifiersSection) {
                this.modifiersSection.style.display = 'none';
            }
            return;
        }

        const dynamicOverrides = this.getDynamicOverrides(latex);
        let hasModifiers = false;
        let hasOperators = false;

        tokens.forEach(tok => {
            const symbol = tok.symbol;
            let info = null;
            
            if (tok.type === 'modifier') {
                hasModifiers = true;
            }

            if (tok.type === 'integration_boundary') {
                let name = 'Integration Boundary / Domain';
                let desc = 'The domain, region, curve, or boundary over which the integral is evaluated.';
                if (symbol === 'C') {
                    name = 'Integration Curve / Path Contour';
                    desc = 'The closed or open boundary path over which the line integral is evaluated.';
                } else if (symbol === 'S') {
                    name = 'Integration Surface';
                    desc = 'The two-dimensional surface over which the surface integral is evaluated.';
                } else if (symbol === 'V') {
                    name = 'Integration Volume';
                    desc = 'The three-dimensional volume region over which the volume integral is evaluated.';
                }
                info = {
                    name: name,
                    type: 'operator',
                    tokenType: 'integration_boundary',
                    description: desc,
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (tok.type === 'operator' && symbol.includes('\\frac{')) {
                const isPartial = symbol.includes('\\partial');
                const isTotal = symbol.includes('\\frac{d');
                
                if (isPartial || isTotal) {
                    const cleanSym = symbol.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|vec|hat|bar|tilde|dot|ddot|underline)/g, '');
                    const match = cleanSym.match(/\\frac\{(?:\\partial|d)\^?[0-9]*\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{(?:\\partial|d)\s*([a-zA-Z\\]+)\^?[0-9]*\}/);
                    
                    let name = isPartial ? 'Partial Derivative' : 'Ordinary Derivative';
                    let desc = isPartial 
                        ? 'Represents the rate of change of a multi-variable function with respect to one variable, holding other variables constant.' 
                        : 'Represents the instantaneous rate of change of a dependent variable with respect to an independent variable.';
                    
                    if (match) {
                        const num = match[1];
                        const den = match[2];
                        
                        const denEntry = this.officialVariables[den] || this.physicsDictionary[den];
                        const denName = denEntry ? denEntry.name.split('/')[0].trim() : den;
                        
                        if (num) {
                            const numEntry = this.officialVariables[num] || this.physicsDictionary[num];
                            const numName = numEntry ? numEntry.name.split('/')[0].trim() : num;
                            
                            name = `${isPartial ? 'Partial' : 'Total'} Derivative of ${numName} with respect to ${denName}`;
                            desc = `Represents how the quantity ${numName.toLowerCase()} changes with respect to the variable ${denName.toLowerCase()}.`;
                        } else {
                            name = `${isPartial ? 'Partial' : 'Total'} Derivative Operator`;
                            desc = `The differential operator representing the rate of change with respect to the variable ${denName.toLowerCase()}.`;
                        }
                    }
                    
                    info = {
                        name: name,
                        type: 'operator',
                        description: desc,
                        unit: 'operator',
                        source: 'heuristic'
                    };
                }
            } else if (tok.type === 'spacetime_derivative') {
                const isContravariant = symbol.includes('^');
                info = {
                    name: isContravariant ? 'Contravariant Spacetime Derivative' : 'Covariant Spacetime Derivative',
                    type: 'operator',
                    description: isContravariant 
                        ? 'Partial derivative with respect to a contravariant coordinate index, raising the coordinate index in tensor calculus.' 
                        : 'Partial derivative with respect to a covariant coordinate index, lowering the coordinate index in tensor calculus.',
                    unit: 'operator',
                    source: 'heuristic'
                };
            } else if (tok.type === 'differential_operator') {
                info = {
                    name: 'Differential Operator',
                    type: 'operator',
                    description: 'Represents an infinitesimal change or differential element in calculus (e.g. dx, dt).',
                    unit: 'operator',
                    source: 'heuristic'
                };
            } else if (this.userCustomizations[symbol]) {
                info = { ...this.userCustomizations[symbol], type: tok.type, source: 'user' };
            } else if (window.SUBTOPIC_VARIABLES && window.SUBTOPIC_VARIABLES[symbol]) {
                const local = window.SUBTOPIC_VARIABLES[symbol];
                info = {
                    name: local.name || symbol,
                    type: local.type || tok.type,
                    description: local.description || 'Contextual subtopic reference.',
                    unit: local.unit || 'dimensionless',
                    ref: window.SUBTOPIC_SLUG ? 'subtopic/' + window.SUBTOPIC_SLUG : null,
                    source: 'subtopic_context'
                };
            } else if (this.officialVariables[symbol]) {
                const official = this.officialVariables[symbol];
                if (typeof official === 'string') {
                    const firstCommaIndex = official.indexOf(',');
                    let name = symbol;
                    let desc = official;
                    let unit = 'dimensionless';
                    if (firstCommaIndex !== -1) {
                        name = official.substring(0, firstCommaIndex).trim();
                        desc = official.substring(firstCommaIndex + 1).trim();
                        desc = desc.charAt(0).toUpperCase() + desc.slice(1);
                    } else {
                        name = symbol;
                    }
                    const unitMatch = official.match(/measured in ([^.]+)/i);
                    if (unitMatch) {
                        unit = unitMatch[1].trim();
                    }
                    const isOperator = /operator/i.test(official) || symbol.startsWith('\\partial') || symbol.startsWith('\\nabla') || symbol.startsWith('\\hat');
                    const isConstant = /constant/i.test(official);
                    info = {
                        name: name,
                        type: isOperator ? 'operator' : (isConstant ? 'constant' : (tok.type || 'variable')),
                        description: desc,
                        unit: unit,
                        ref: null,
                        source: 'database'
                    };
                } else {
                    info = {
                        name: official.name || symbol,
                        type: official.type || tok.type,
                        description: official.description || 'Sharded variable reference.',
                        unit: official.unit || 'dimensionless',
                        ref: official.ref || null,
                        source: 'database'
                    };
                }
            } else if (tok.type === 'modifier' && this.modifierGlossary[symbol]) {
                const glossaryEntry = this.modifierGlossary[symbol];
                info = {
                    name: glossaryEntry.name,
                    type: 'modifier',
                    description: glossaryEntry.desc,
                    unit: 'modifier',
                    source: 'glossary'
                };
            } else if (/\\(int|oint|iint|iiint)/.test(symbol)) {
                info = {
                    name: 'Definite/Indefinite Integral',
                    type: tok.type,
                    description: 'Accumulates quantities over the differential range.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (/\\frac\{\\partial/.test(symbol)) {
                info = {
                    name: 'Partial Derivative',
                    type: tok.type,
                    description: 'Represents the rate of change of the numerator with respect to the denominator.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (/\\frac\{d/.test(symbol)) {
                info = {
                    name: 'Total Derivative',
                    type: tok.type,
                    description: 'Represents the total rate of change of a quantity with respect to an independent variable.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (/\\(dot|ddot)/.test(symbol)) {
                info = {
                    name: 'Time Derivative',
                    type: tok.type,
                    description: 'Represents the rate of change with respect to time.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else {
                // Try constants.json
                const constants = window.PHYSICS_CONSTANTS || {};
                let foundConstant = null;
                for (const [key, details] of Object.entries(constants)) {
                    if (details.symbol === symbol) {
                        foundConstant = details;
                        break;
                    }
                }
                
                if (foundConstant) {
                    info = {
                        name: foundConstant.name,
                        type: 'constant',
                        description: foundConstant.description,
                        unit: foundConstant.unit,
                        ref: 'constants/' + foundConstant.symbol,
                        source: 'constants'
                    };
                } else if (dynamicOverrides[symbol]) {
                    info = { ...dynamicOverrides[symbol], source: 'dynamic' };
                } else if (this.physicsDictionary[symbol]) {
                    const dictEntry = this.physicsDictionary[symbol];
                    let activeEntry = dictEntry;
                    
                    // Check if there is an override matching the active domain
                    let match = null;
                    if (dictEntry.alternatives) {
                        match = dictEntry.alternatives.find(alt => alt.domain === effectiveDomain);
                    }
                    if (match) {
                        activeEntry = {
                            name: match.name,
                            type: match.type || dictEntry.type,
                            unit: match.unit || dictEntry.unit,
                            desc: match.desc || dictEntry.desc,
                            alternatives: dictEntry.alternatives
                        };
                    } else if (dictEntry.domain === effectiveDomain) {
                        activeEntry = dictEntry;
                    }
                    
                    info = {
                        name: activeEntry.name,
                        type: activeEntry.type || tok.type,
                        description: activeEntry.desc || activeEntry.description,
                        unit: activeEntry.unit || 'dimensionless',
                        alternatives: dictEntry.alternatives,
                        source: 'dictionary'
                    };
                } else {
                    const cleanName = symbol.replace(/^\\/, '');
                    const formattedName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
                    info = {
                        name: formattedName + (tok.type === 'modifier' ? ' Modifier' : (tok.type === 'operator' ? ' Operator' : ' Variable')),
                        type: tok.type,
                        description: tok.type === 'modifier' ? 'Custom modifier constraint. Click Edit to customize definition.' : (tok.type === 'operator' ? 'Mathematical or logical operator.' : 'Custom variable. Click Edit to customize name, unit, and definition.'),
                        unit: tok.type === 'modifier' ? 'modifier' : (tok.type === 'operator' ? 'operator' : 'dimensionless'),
                        source: 'fallback'
                    };
                }
            }

            if (info && info.type === 'modifier') {
                hasModifiers = true;
            } else if (info && info.type === 'operator') {
                hasOperators = true;
            }

            this.renderVariableRow(symbol, info);
        });

        if (this.operatorsSection) {
            this.operatorsSection.style.display = hasOperators ? 'block' : 'none';
        }

        if (this.modifiersSection) {
            this.modifiersSection.style.display = hasModifiers ? 'block' : 'none';
        }

        const typesetTargets = [this.symbolsList];
        if (hasOperators && this.operatorsList) {
            typesetTargets.push(this.operatorsList);
        }
        if (hasModifiers && this.modifiersList) {
            typesetTargets.push(this.modifiersList);
        }
        this.triggerTypeset(typesetTargets);
    },

    bindRowEvents(targetRow, symbol, info) {
        // Highlight on hover
        targetRow.addEventListener('mouseenter', () => {
            this.highlightSymbolInMath(symbol, true);
        });
        targetRow.addEventListener('mouseleave', () => {
            this.highlightSymbolInMath(symbol, false);
        });

        // Edit button
        const editBtn = targetRow.querySelector('.edit-var-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleVarEditForm(targetRow, symbol, info);
            });
        }

        // Drill down click handler on badge
        const badge = targetRow.querySelector('.symbol-badge');
        if (badge) {
            badge.style.cursor = 'pointer';
            badge.addEventListener('click', (e) => {
                e.stopPropagation();
                this.drillDownIntoSymbol(symbol, info);
            });
        }

        // Drill down click handler on name
        const nameLbl = targetRow.querySelector('.var-name-lbl');
        if (nameLbl) {
            nameLbl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.drillDownIntoSymbol(symbol, info);
            });
        }

        // Alternate disambiguation options
        const altBtns = targetRow.querySelectorAll('.alt-disambig-btn');
        altBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const newName = btn.getAttribute('data-name');
                const newType = btn.getAttribute('data-type');
                const newUnit = btn.getAttribute('data-unit');
                const newDesc = btn.getAttribute('data-desc');

                const updatedInfo = {
                    name: newName,
                    type: newType,
                    unit: newUnit,
                    description: newDesc
                };

                this.userCustomizations[symbol] = updatedInfo;
                try {
                    localStorage.setItem('physics_explainer_custom_' + symbol, JSON.stringify(updatedInfo));
                } catch (err) {
                    console.warn('Could not write custom variable definitions to localStorage:', err);
                }

                const updatedRow = this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, targetRow);
                EquationExplainer.triggerTypeset([updatedRow]);
            });
        });
    },

    renderVariableRow(symbol, info, existingRow = null) {
        const row = existingRow || document.createElement('div');
        row.className = 'symbol-row';
        row.setAttribute('data-symbol', symbol);
        
        let typeClass = '';
        let badgeTypeLabel = 'Variable';
        if (info.type === 'constant') {
            typeClass = 'constant-type';
            badgeTypeLabel = 'Constant';
        } else if (info.type === 'operator') {
            typeClass = 'operator-type';
            badgeTypeLabel = 'Operator';
        } else if (info.type === 'modifier') {
            typeClass = 'modifier-type';
            badgeTypeLabel = 'Modifier';
        }

        // Wrap badge symbol in MathJax delimiters so it renders as a mathematical character
        let displaySymbol = symbol;
        if (symbol === '\\sqrt') {
            displaySymbol = '\\sqrt{\\phantom{x}}';
        }
        const mathjaxSymbol = `$${displaySymbol}$`;

        // Build name link or strong label
        const displayName = (info.name && /[\\[\]_{}^]/.test(info.name) && !info.name.includes('<')) ? `$${info.name}$` : (info.name || symbol);
        let nameHtml = `<span class="var-name-lbl" style="color: var(--accent-default, #64ffda); text-decoration: none; font-size: 0.92rem; font-weight: 600; cursor: pointer; border-bottom: 1px dashed rgba(100,255,218,0.3); transition: border-color 0.2s;" onmouseover="this.style.borderColor='var(--accent-default)'" onmouseout="this.style.borderColor='rgba(100,255,218,0.3)'">${displayName}</span>`;

        let disambigHtml = '';
        const dictEntry = this.physicsDictionary[symbol];
        if (dictEntry && dictEntry.alternatives) {
            const allOptions = [
                { name: dictEntry.name, type: dictEntry.type || 'variable', unit: dictEntry.unit || 'dimensionless', description: dictEntry.desc || dictEntry.description || '' },
                ...dictEntry.alternatives.map(alt => ({
                    name: alt.name,
                    type: alt.type || 'variable',
                    unit: alt.unit || 'dimensionless',
                    description: alt.desc || alt.description || ''
                }))
            ];
            const availableOptions = allOptions.filter(opt => opt.name.toLowerCase() !== info.name.toLowerCase());
            if (availableOptions.length > 0) {
                disambigHtml = `
                    <div class="disambiguation-box" style="margin-top: 6px; font-size: 0.74rem; color: var(--text-muted, #94a3b8); display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                        <span>Context overrides:</span>
                        ${availableOptions.map(opt => `
                            <button class="alt-disambig-btn" 
                                    data-name="${opt.name}" 
                                    data-type="${opt.type}" 
                                    data-unit="${opt.unit}" 
                                    data-desc="${opt.description}"
                                    style="background: rgba(100,255,218,0.05); border: 1px solid rgba(100,255,218,0.15); color: var(--accent-default, #64ffda); padding: 1px 6px; border-radius: 3px; cursor: pointer; font-size: 0.72rem; font-family: inherit; transition: all 0.2s;"
                                    onmouseover="this.style.background='rgba(100,255,218,0.12)'"
                                    onmouseout="this.style.background='rgba(100,255,218,0.05)'">
                                ${opt.name}
                            </button>
                        `).join('')}
                    </div>
                `;
            }
        }

        row.innerHTML = `
            <div class="symbol-badge ${typeClass}" title="${badgeTypeLabel}" style="cursor: pointer;">${mathjaxSymbol}</div>
            <div class="symbol-content-wrapper" style="flex: 1; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${nameHtml}
                        <button class="edit-var-btn" style="background: transparent; border: none; color: var(--text-muted, #94a3b8); cursor: pointer; padding: 2px; display: inline-flex; align-items: center; justify-content: center; transition: color 0.2s;" title="Edit Definition">
                             <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"/></svg>
                        </button>
                    </div>
                    <span class="var-unit-lbl" style="font-size: 0.76rem; font-family: 'Fira Code', clock, monospace; color: #a8a29e; background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04); ${info.unit && info.unit !== 'dimensionless' && info.unit !== 'operator' && info.unit !== 'modifier' ? '' : 'display: none;'}">${info.unit || ''}</span>
                </div>
                <div class="var-desc-lbl" style="font-size: 0.82rem; color: var(--text-muted, #94a3b8); line-height: 1.4;">${info.description || info.desc || ''}</div>
                ${disambigHtml}
            </div>
        `;

        if (existingRow) {
            const newRow = row.cloneNode(true);
            row.parentNode.replaceChild(newRow, row);
            this.bindRowEvents(newRow, symbol, info);
            return newRow;
        }

        this.bindRowEvents(row, symbol, info);

        if (!existingRow) {
            if (info.type === 'modifier') {
                if (this.modifiersList) this.modifiersList.appendChild(row);
            } else if (info.type === 'operator') {
                if (this.operatorsList) this.operatorsList.appendChild(row);
                else this.symbolsList.appendChild(row);
            } else {
                this.symbolsList.appendChild(row);
            }
        }
        return row;
    },

    toggleVarEditForm(row, symbol, info) {
        const wrapper = row.querySelector('.symbol-content-wrapper');
        
        wrapper.innerHTML = `
            <div class="edit-var-form" style="display: flex; flex-direction: column; gap: 8px; width: 100%; padding: 4px 0; box-sizing: border-box;">
                <div style="display: flex; gap: 10px;">
                    <input type="text" class="edit-var-name" value="${info.name}" placeholder="Variable Name" style="flex: 2; padding: 4px 8px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; color: #fff; font-size: 0.85rem; font-family: inherit; outline: none;">
                    <input type="text" class="edit-var-unit" value="${info.unit === 'dimensionless' || info.unit === 'operator' ? '' : (info.unit || '')}" placeholder="Unit (e.g. m/s)" style="flex: 1; padding: 4px 8px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; color: #fff; font-size: 0.85rem; font-family: inherit; outline: none;">
                </div>
                <textarea class="edit-var-desc" rows="2" placeholder="Describe what this component represents..." style="width: 100%; padding: 6px 8px; background: #030712; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; color: #fff; font-size: 0.82rem; font-family: inherit; line-height: 1.3; resize: vertical; outline: none; box-sizing: border-box;">${info.description || info.desc || ''}</textarea>
                <div style="display: flex; gap: 8px; justify-content: flex-end;">
                    <button class="save-var-btn" style="background: var(--accent-default, #64ffda); border: none; color: #030712; padding: 3px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s;">Save</button>
                    <button class="cancel-var-btn" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #fff; padding: 3px 10px; border-radius: 4px; font-size: 0.76rem; cursor: pointer; transition: background 0.2s;">Cancel</button>
                </div>
            </div>
        `;

        const saveBtn = wrapper.querySelector('.save-var-btn');
        const cancelBtn = wrapper.querySelector('.cancel-var-btn');

        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const newName = wrapper.querySelector('.edit-var-name').value.trim() || symbol;
            const newUnit = wrapper.querySelector('.edit-var-unit').value.trim() || 'dimensionless';
            const newDesc = wrapper.querySelector('.edit-var-desc').value.trim() || '';

            const updatedInfo = {
                name: newName,
                unit: newUnit,
                description: newDesc,
                type: info.type
            };

            this.userCustomizations[symbol] = updatedInfo;
            try {
                localStorage.setItem('physics_explainer_custom_' + symbol, JSON.stringify(updatedInfo));
            } catch (err) {
                console.warn('Could not write custom variable definitions to localStorage:', err);
            }

            const updatedRow = this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, row);

            // Retypeset the row
            EquationExplainer.triggerTypeset([updatedRow]);
        });

        cancelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const updatedRow = this.renderVariableRow(symbol, info, row);

            // Retypeset the row
            EquationExplainer.triggerTypeset([updatedRow]);
        });

        wrapper.querySelector('.edit-var-name').focus();
    },

    highlightSymbolInMath(symbol, active) {
        // Strip leading backslash for HTML text searching
        const cleanSymbol = symbol.startsWith('\\') ? symbol.substring(1) : symbol;
        
        // Find elements in preview box containing symbol
        const mathBox = document.getElementById('math-render-target');
        if (!mathBox) return;

        const elements = mathBox.querySelectorAll('mjx-container, svg, mjx-c, use, text');
        elements.forEach(el => {
            let matches = false;
            
            if (el.tagName === 'mjx-c' || el.tagName === 'text') {
                const cMatch = el.getAttribute('c');
                if (cMatch && cMatch.toLowerCase() === cleanSymbol.toLowerCase()) {
                    matches = true;
                } else if (el.textContent === cleanSymbol) {
                    matches = true;
                }
            } else if (el.tagName === 'use') {
                const href = el.getAttribute('href') || el.getAttribute('xlink:href') || '';
                if (href.toLowerCase().includes(cleanSymbol.toLowerCase())) {
                    matches = true;
                }
            }

            if (matches) {
                if (active) {
                    el.style.filter = 'drop-shadow(0 0 5px var(--accent-default, #64ffda))';
                    el.style.fill = 'var(--accent-default, #64ffda)';
                    el.style.stroke = 'var(--accent-default, #64ffda)';
                    el.style.strokeWidth = '10px';
                } else {
                    el.style.filter = '';
                    el.style.fill = '';
                    el.style.stroke = '';
                    el.style.strokeWidth = '';
                }
            }
        });
    },

    resetExplanation() {
        this.stopSandbox();
        this.stopSonification();
        
        this.explainerPlaceholder.style.display = 'flex';
        if (this.explainerNavTabs) this.explainerNavTabs.style.display = 'none';
        if (this.tabPanes) {
            this.tabPanes.forEach(pane => pane.style.display = 'none');
        }
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'none';
        if (this.modifiersSection) this.modifiersSection.style.display = 'none';
        if (this.modifiersList) this.modifiersList.innerHTML = '';
        this.topologicalBridges.style.display = 'none';
        if (this.conceptualIntroCard) this.conceptualIntroCard.style.display = 'none';
        if (this.aiScenariosSection) this.aiScenariosSection.style.display = 'none';
        if (this.aiSimulationCard) this.aiSimulationCard.style.display = 'none';
        
        this.formulaTitle.textContent = 'Selecting Equation...';
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status badge-unregistered';
            this.formulaBadge.textContent = 'Live Analysis';
        }
        if (this.solverRedirectContainer) {
            this.solverRedirectContainer.style.display = 'none';
        }
    },

    setupSolverLink(latex) {
        // Deprecated: standalone dimensional solver removed in favor of upcoming integrated lab tools workbench
    },

    /* ==========================================================================
       INTERACTIVE SIMULATIONS & SONIFICATION (Delegated to ExplainerSimulations)
       ========================================================================== */

    initSandbox(latex, variables) {
        if (window.ExplainerSimulations && window.ExplainerSimulations.initSandbox) {
            return window.ExplainerSimulations.initSandbox.call(this, latex, variables);
        }
    },

    stopSandbox() {
        if (window.ExplainerSimulations && window.ExplainerSimulations.stopSandbox) {
            return window.ExplainerSimulations.stopSandbox.call(this);
        }
    },

    toggleSonification() {
        if (window.ExplainerSimulations && window.ExplainerSimulations.toggleSonification) {
            return window.ExplainerSimulations.toggleSonification.call(this);
        }
    },

    stopSonification() {
        if (window.ExplainerSimulations && window.ExplainerSimulations.stopSonification) {
            return window.ExplainerSimulations.stopSonification.call(this);
        }
    },

    /* ==========================================================================
       CURATION WORKSPACE & MULTI-TIER RBAC (Delegated to ExplainerCurator)
       ========================================================================== */

    initCuratorDrawer() {
        if (window.ExplainerCurator && window.ExplainerCurator.initCuratorDrawer) {
            return window.ExplainerCurator.initCuratorDrawer.call(this);
        }
    },

    openCuratorDrawer() {
        if (window.ExplainerCurator && window.ExplainerCurator.openCuratorDrawer) {
            return window.ExplainerCurator.openCuratorDrawer.call(this);
        }
    },

    closeCuratorDrawer() {
        if (window.ExplainerCurator && window.ExplainerCurator.closeCuratorDrawer) {
            return window.ExplainerCurator.closeCuratorDrawer.call(this);
        }
    }
};

// Synchronize sub-modules in browser and Node/CLI environments
if (typeof window !== 'undefined') {
    if (window.ExplainerDictionary) Object.assign(EquationExplainer, window.ExplainerDictionary);
    if (window.ExplainerTokenizer) Object.assign(EquationExplainer, window.ExplainerTokenizer);
    if (window.ExplainerCards) Object.assign(EquationExplainer, window.ExplainerCards);
    if (window.ExplainerSimulations) Object.assign(EquationExplainer, window.ExplainerSimulations);
    if (window.ExplainerCurator) Object.assign(EquationExplainer, window.ExplainerCurator);
    window.EquationExplainer = EquationExplainer;
} else if (typeof require === 'function') {
    try { Object.assign(EquationExplainer, require('./explainer_dictionary.js')); } catch (e) {}
    try { Object.assign(EquationExplainer, require('./explainer_tokenizer.js')); } catch (e) {}
    try { Object.assign(EquationExplainer, require('./explainer_cards.js')); } catch (e) {}
    try { Object.assign(EquationExplainer, require('./explainer_curator.js')); } catch (e) {}
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = EquationExplainer;
}

// Start initialization
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => EquationExplainer.init());
    } else {
        EquationExplainer.init();
    }
}

