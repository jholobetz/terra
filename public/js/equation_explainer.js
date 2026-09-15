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

    getDynamicOverrides(latex) {
        const overrides = {};
        if (!latex) return overrides;

        // Layer 3: Subscript and Syntactic Grammar checks
        if (/T\^([a-d])|T\_([a-d])|T\^\{([a-d])\}|T\_\{([a-d])\}/.test(latex)) {
            overrides['T'] = { 
                name: 'SU(3) Gauge Generator', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.' 
            };
        }
        
        if (/T\_[0if]|T\_\{[0if]\}/.test(latex)) {
            overrides['T'] = { 
                name: 'Temperature', 
                type: 'variable', 
                unit: 'K', 
                description: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.' 
            };
        }

        if (/Y\_[lL]\^([mM])|Y\_\{[lL]\}\^\{([mM])\}/.test(latex)) {
            overrides['Y'] = { 
                name: 'Spherical Harmonic', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'Angular wavefunction solutions to Laplace\'s equation in spherical coordinates.' 
            };
        }
        
        if (/Y\s*\/\s*2|\frac\{\s*Y\s*\}\{\s*2\s*\}/.test(latex)) {
            overrides['Y'] = { 
                name: 'Weak Hypercharge', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'The generator of the U(1) weak hypercharge gauge group.' 
            };
        }

        // Layer 2: Heuristic Token Co-occurrence (Semantic Clustering)
        const tokens = this.extractAllMathTokens(latex).map(t => t.symbol);
        
        const SEMANTIC_CLUSTERS = [
            {
                domain: 'thermodynamics',
                indicators: ['P', 'V', 'n', 'R', 'S', 'Q', 'U', '\\Delta', 'k_B'],
                overrides: {
                    'T': { name: 'Temperature', type: 'variable', unit: 'K', description: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.' },
                    'k': { name: 'Boltzmann Constant', type: 'constant', unit: 'J/K', description: 'A physical constant relating the average kinetic energy of particles in a gas with the thermodynamic temperature.' },
                    'P': { name: 'Pressure', type: 'variable', unit: 'Pa', description: 'Force applied perpendicular to the surface of an object per unit area.' },
                    'S': { name: 'Entropy', type: 'variable', unit: 'J/K', description: 'A thermodynamic quantity representing the degree of disorder or randomness in a system.' }
                }
            },
            {
                domain: 'harmonic_motion',
                indicators: ['f', '\\omega', '\\nu', '\\lambda', '\\sin', '\\cos', 'A'],
                overrides: {
                    'T': { name: 'Time Period', type: 'variable', unit: 's', description: 'The time taken for one complete cycle of a repeating wave or oscillation.' }
                }
            },
            {
                domain: 'dynamics',
                indicators: ['F', 'm', 'a', '\\theta', '\\mu_s', 'g', 'N'],
                overrides: {
                    'T': { name: 'Tension', type: 'variable', unit: 'N', description: 'The pulling force transmitted axially by means of a string, cable, or chain.' },
                    'k': { name: 'Spring Constant', type: 'variable', unit: 'N/m', description: 'The force constant representing the stiffness of a spring (Hooke\'s Law).' }
                }
            },
            {
                domain: 'gauge_theory',
                indicators: ['D_\\mu', 'g_s', 'W_\\mu', 'B_\\mu', '\\tau^a', 'G_\\mu^a', 'T^a', '\\tau', 'Y', 'g', 'g\''],
                overrides: {
                    'T': { name: 'SU(3) Gauge Generator', type: 'variable', unit: 'dimensionless', description: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.' },
                    'Y': { name: 'Weak Hypercharge', type: 'variable', unit: 'dimensionless', description: 'The generator of the U(1) weak hypercharge gauge group.' }
                }
            }
        ];

        let bestDomain = null;
        let maxOverlap = 0;

        SEMANTIC_CLUSTERS.forEach(cluster => {
            const overlap = cluster.indicators.filter(ind => tokens.includes(ind) || latex.includes(ind)).length;
            if (overlap >= 2 && overlap > maxOverlap) {
                maxOverlap = overlap;
                bestDomain = cluster;
            }
        });

        const effectiveDomain = this.activeDomain || this.detectDomainFromLatex(latex) || 'classical_mechanics';
        const activeCluster = SEMANTIC_CLUSTERS.find(c => c.domain === effectiveDomain);
        if (activeCluster) {
            Object.entries(activeCluster.overrides).forEach(([sym, val]) => {
                if (!overrides[sym]) {
                    overrides[sym] = val;
                }
            });
        }

        if (bestDomain) {
            Object.entries(bestDomain.overrides).forEach(([sym, val]) => {
                if (!overrides[sym]) {
                    overrides[sym] = val;
                }
            });
        }

        return overrides;
    },

    isSingleSymbol(latex) {
        const cleaned = latex.trim().replace(/^\\\[/, '').replace(/\\\]$/, '').replace(/^\$\$/, '').replace(/\$\$/, '').replace(/^\$/, '').replace(/\$/, '').trim();
        const innerMatch = cleaned.match(/^\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol)\{([a-zA-Z\\]+)\}$/);
        if (innerMatch) {
            return innerMatch[2].length <= 10;
        }
        const simpleCleaned = cleaned.replace(/\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol|mathrm|mathsf)/g, '').replace(/[\{\}]/g, '');
        return simpleCleaned.length <= 4 && !/[=+\-*\/<>|]/.test(simpleCleaned);
    },

    resolveSymbolInfo(symbol, type = null) {
        let cleanSymbol = symbol.trim().replace(/^\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol)\{([a-zA-Z\\]+)\}$/, '$2').replace(/[\{\}]/g, '');
        const effectiveDomain = this.activeDomain || (this.currentLatex ? this.detectDomainFromLatex(this.currentLatex) : null) || 'classical_mechanics';
        
        // 0. Check active fallback binder overrides
        if (this.activeBinder && this.activeBinder.variableOverrides) {
            const override = this.activeBinder.variableOverrides[symbol] || this.activeBinder.variableOverrides[cleanSymbol];
            if (override) {
                return {
                    name: override.name,
                    type: override.type || 'variable',
                    description: override.desc || override.description,
                    unit: override.unit || 'dimensionless',
                    featuredEquations: []
                };
            }
        }

        // 1. Check integration boundary overrides
        if (type === 'integration_boundary') {
            if (symbol === 'C') {
                return {
                    name: 'Integration Curve / Path Contour',
                    type: 'operator',
                    description: 'The closed or open boundary path over which the line integral is evaluated.',
                    unit: 'dimensionless'
                };
            } else if (symbol === 'S') {
                return {
                    name: 'Integration Surface',
                    type: 'operator',
                    description: 'The two-dimensional surface over which the surface integral is evaluated.',
                    unit: 'dimensionless'
                };
            } else if (symbol === 'V') {
                return {
                    name: 'Integration Volume',
                    type: 'operator',
                    description: 'The three-dimensional volume region over which the volume integral is evaluated.',
                    unit: 'dimensionless'
                };
            }
        }

        // 2. Check fundamental constants first
        const constants = window.PHYSICS_CONSTANTS || {};
        const constantEquations = {
            'c': [{ name: "Mass-Energy Equivalence", latex: "E = mc^2" }, { name: "Speed of Light Relation", latex: "c = \\frac{1}{\\sqrt{\\epsilon_0 \\mu_0}}" }],
            'hbar': [{ name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" }, { name: "Heisenberg Uncertainty Principle", latex: "\\Delta x \\Delta p \\ge \\frac{\\hbar}{2}" }],
            'G': [{ name: "Universal Gravitation", latex: "F = G \\frac{m_1 m_2}{r^2}" }, { name: "Einstein Field Equations", latex: "G_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}" }],
            'k_B': [{ name: "Boltzmann Entropy Formula", latex: "S = k_B \\ln \\Omega" }, { name: "Ideal Gas Law", latex: "P V = N k_B T" }],
            'epsilon_0': [{ name: "Gauss's Law", latex: "\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}" }, { name: "Speed of Light Relation", latex: "c = \\frac{1}{\\sqrt{\\epsilon_0 \\mu_0}}" }],
            'mu_0': [{ name: "Ampere's Law", latex: "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}" }, { name: "Speed of Light Relation", latex: "c = \\frac{1}{\\sqrt{\\epsilon_0 \\mu_0}}" }]
        };

        for (const [key, details] of Object.entries(constants)) {
            if (details.symbol === symbol || details.symbol === cleanSymbol) {
                return {
                    name: details.name,
                    type: 'constant',
                    description: details.description || details.desc || 'Fundamental physical constant.',
                    value: details.value,
                    unit: details.unit,
                    featuredEquations: constantEquations[key] || []
                };
            }
        }
        
        // 3. Check variable dictionary with context override
        const dictEntry = this.variableDictionary[cleanSymbol] || this.variableDictionary[symbol];
        if (dictEntry) {
            let activeCtx = null;
            if (effectiveDomain && dictEntry.contexts && dictEntry.contexts[effectiveDomain]) {
                activeCtx = dictEntry.contexts[effectiveDomain];
            } else if (dictEntry.contexts) {
                const firstCtxKey = Object.keys(dictEntry.contexts)[0];
                activeCtx = dictEntry.contexts[firstCtxKey];
            }
            
            return {
                name: activeCtx ? activeCtx.name : dictEntry.name,
                type: 'variable',
                description: activeCtx ? activeCtx.description : dictEntry.description,
                unit: activeCtx ? (activeCtx.unit || dictEntry.defaultUnit) : dictEntry.defaultUnit,
                featuredEquations: dictEntry.featuredEquations || []
            };
        }

        // 4. Check legacy physicsDictionary with active domain override support
        const legacyEntry = this.physicsDictionary[cleanSymbol] || this.physicsDictionary[symbol];
        if (legacyEntry) {
            let activeLegacy = legacyEntry;
            let match = null;
            if (legacyEntry.alternatives) {
                match = legacyEntry.alternatives.find(alt => alt.domain === effectiveDomain);
            }
            if (match) {
                activeLegacy = {
                    name: match.name,
                    type: match.type || legacyEntry.type,
                    unit: match.unit || legacyEntry.unit,
                    desc: match.desc || legacyEntry.desc
                };
            } else if (legacyEntry.domain === effectiveDomain) {
                activeLegacy = legacyEntry;
            }
            
            return {
                name: activeLegacy.name,
                type: activeLegacy.type || 'variable',
                description: activeLegacy.desc || activeLegacy.description || 'Physics variable.',
                unit: activeLegacy.unit || 'dimensionless',
                featuredEquations: []
            };
        }
        
        // 5. Fallback
        const cleanName = symbol.replace(/^\\/, '');
        const formattedName = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
        return {
            name: formattedName + ' Variable',
            type: 'variable',
            description: 'This symbol represents a variable or quantity within the current physical equation.',
            unit: 'dimensionless',
            featuredEquations: []
        };
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

        // Initialize Curator Drawer & Dev Role Switcher
        this.initCuratorDrawer();
        this.initDevRoleSwitcher();
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

    triggerAutoDraft() {
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;
        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to auto-draft.', true);
            return;
        }

        const btnAutoDraft = document.getElementById('drawer-btn-autodraft');
        const originalHtml = btnAutoDraft ? btnAutoDraft.innerHTML : '';
        if (btnAutoDraft) {
            btnAutoDraft.disabled = true;
            btnAutoDraft.style.opacity = '0.7';
            btnAutoDraft.innerHTML = `<span style="display:inline-block; width:9px; height:9px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:explainer-spin 0.8s linear infinite; margin-right:4px;"></span> Drafting...`;
        }

        // Inject spin keyframe if not present
        if (!document.getElementById('explainer-spin-style')) {
            const style = document.createElement('style');
            style.id = 'explainer-spin-style';
            style.textContent = `@keyframes explainer-spin { 100% { transform: rotate(360deg); } }`;
            document.head.appendChild(style);
        }

        const adminKey = localStorage.getItem('terra_admin_key') || '';

        fetch(`${BASE_URL}/physics/api/define-formula`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Terra-Admin-Key': adminKey
            },
            body: JSON.stringify({ latex: latex })
        })
        .then(res => res.json())
        .then(data => {
            if (btnAutoDraft) {
                btnAutoDraft.disabled = false;
                btnAutoDraft.style.opacity = '1';
                btnAutoDraft.innerHTML = originalHtml;
            }

            if (data.success && data.formula) {
                const f = data.formula;
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = f.title || '';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = f.interpretation || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = f.symmetry_origin || '';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = f.limits_and_boundary || '';
                this.showDrawerAlert('✓ Auto-draft populated into fields! Review in Live Preview before saving.');
                this.updateDrawerLivePreview();
            } else {
                // Fallback: AST overview synthesis
                const synthesis = this.synthesizeCustomOverview(latex);
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = this.currentFormula ? this.currentFormula.title : 'Custom Physical Relation';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = synthesis.intro || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = 'Invariance derived from constitutive dynamical equations.';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = synthesis.summary || '';
                this.showDrawerAlert('✓ Auto-draft synthesized from equation AST. Review before submitting.');
                this.updateDrawerLivePreview();
            }
        })
        .catch(err => {
            if (btnAutoDraft) {
                btnAutoDraft.disabled = false;
                btnAutoDraft.style.opacity = '1';
                btnAutoDraft.innerHTML = originalHtml;
            }
            const synthesis = this.synthesizeCustomOverview(latex);
            if (this.drawerFieldTitle) this.drawerFieldTitle.value = this.currentFormula ? this.currentFormula.title : 'Custom Physical Relation';
            if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = synthesis.intro || '';
            if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = 'Invariance derived from constitutive dynamical equations.';
            if (this.drawerFieldLimits) this.drawerFieldLimits.value = synthesis.summary || '';
            this.showDrawerAlert('✓ Auto-draft synthesized from equation AST.');
            this.updateDrawerLivePreview();
        });
    },

    showActionProgress(percent, msg, isDone = false, isError = false) {
        const container = document.getElementById('drawer-action-progress-container');
        const fill = document.getElementById('drawer-progress-bar-fill');
        const statusMsg = document.getElementById('drawer-progress-status-msg');
        const percentLabel = document.getElementById('drawer-progress-percent');
        const statusText = document.getElementById('drawer-progress-status-text');

        if (!container || !fill || !statusMsg || !percentLabel) return;

        container.style.display = 'flex';
        fill.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        percentLabel.textContent = `${Math.round(percent)}%`;
        statusMsg.textContent = msg;

        if (isError) {
            fill.style.background = '#f43f5e';
            if (statusText) statusText.style.color = '#f43f5e';
        } else if (isDone) {
            fill.style.background = '#64ffda';
            if (statusText) statusText.style.color = '#64ffda';
        } else {
            fill.style.background = 'linear-gradient(90deg, #38bdf8, #64ffda)';
            if (statusText) statusText.style.color = '#38bdf8';
        }
    },

    hideActionProgress(delay = 1000) {
        setTimeout(() => {
            const container = document.getElementById('drawer-action-progress-container');
            if (container) {
                container.style.display = 'none';
            }
        }, delay);
    },

    triggerFixLatex() {
        const latex = (this.drawerLatexInput ? this.drawerLatexInput.value.trim() : '') || this.currentLatex;
        if (!latex) {
            this.showDrawerAlert('Please provide a LaTeX equation to fix.', true);
            return;
        }

        const btnFixLatex = document.getElementById('drawer-btn-fixlatex');
        const originalHtml = btnFixLatex ? btnFixLatex.innerHTML : '';
        if (btnFixLatex) {
            btnFixLatex.disabled = true;
            btnFixLatex.style.opacity = '0.7';
            btnFixLatex.innerHTML = `<span style="display:inline-block; width:9px; height:9px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:explainer-spin 0.8s linear infinite; margin-right:4px;"></span> Fixing...`;
        }

        // Progress Stage 1: Initializing
        this.showActionProgress(15, 'Validating syntax & searching formula index...');

        const formulaId = this.currentId || (this.currentFormula ? this.currentFormula.id : '') || 'synthesized-custom';
        const hint = this.drawerHintInput ? this.drawerHintInput.value.trim() : '';

        const payload = {
            url: window.location.href,
            formula_id: formulaId,
            latex: latex,
            hint: hint
        };

        // Simulated smooth micro-progress while network request executes
        const t1 = setTimeout(() => this.showActionProgress(45, 'Sanitizing TeX tokens & structuring narrative...'), 180);
        const t2 = setTimeout(() => this.showActionProgress(75, 'Updating JSON shard & synchronizing MariaDB...'), 420);

        // AbortController with 20s timeout safeguard
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 20000);

        const baseUrl = (typeof BASE_URL !== 'undefined') ? BASE_URL : '';
        fetch(`${baseUrl}/physics/api/apply-repair`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(payload),
            signal: controller.signal
        })
        .then(async res => {
            clearTimeout(timeoutId);
            clearTimeout(t1);
            clearTimeout(t2);
            let data;
            try {
                data = await res.json();
            } catch (e) {
                throw new Error(`HTTP ${res.status}: Server returned invalid response.`);
            }
            if (!res.ok && data && data.error) {
                throw new Error(data.error);
            }
            return data;
        })
        .then(data => {
            if (btnFixLatex) {
                btnFixLatex.disabled = false;
                btnFixLatex.style.opacity = '1';
                btnFixLatex.innerHTML = originalHtml;
            }

            if (data.success && data.data && data.data.formula) {
                this.showActionProgress(100, '✓ Repair complete! MathJax synced.', true, false);
                this.hideActionProgress(1400);

                const f = data.data.formula;
                this.currentFormula = f;
                this.currentId = f.id;
                this.currentLatex = data.data.clean_equation || f.equation;

                // Synchronize top main formula bar and drawer inputs
                if (this.latexInput) this.latexInput.value = this.currentLatex;
                if (this.drawerLatexInput) this.drawerLatexInput.value = this.currentLatex;
                if (this.drawerFieldTitle) this.drawerFieldTitle.value = f.title || '';
                if (this.drawerFieldInterpretation) this.drawerFieldInterpretation.value = f.interpretation || '';
                if (this.drawerFieldSymmetry) this.drawerFieldSymmetry.value = f.symmetry_origin || '';
                if (this.drawerFieldLimits) this.drawerFieldLimits.value = f.limits_and_boundary || '';

                if (this.drawerFormulaIdLabel) {
                    this.drawerFormulaIdLabel.textContent = `Formula ID: ${f.id}`;
                }

                // Render main UI, recompile MathJax equation and scenarios
                this.renderFormula(f, this.currentSubtopics || []);
                this.compileMathJax(this.currentLatex);
                this.updateDrawerLivePreview();

                // Re-render and typeset all target containers
                const targets = [];
                if (this.mathRenderTarget) targets.push(this.mathRenderTarget);
                if (this.conceptualIntroCard) targets.push(this.conceptualIntroCard);
                if (this.aiScenariosList) targets.push(this.aiScenariosList);
                if (this.drawerPreviewTarget) targets.push(this.drawerPreviewTarget);
                if (targets.length > 0) {
                    this.triggerTypeset(targets);
                }

                this.showDrawerAlert('✓ LaTeX decorrupted, hint applied, and shard/database synchronized!');

                // Update URL query state to registered formula ID
                if (window.history && window.history.replaceState) {
                    const newUrl = window.location.pathname + '?id=' + encodeURIComponent(f.id);
                    window.history.replaceState(null, '', newUrl);
                }
            } else {
                this.showActionProgress(100, `Error: ${data.error || 'Failed to fix LaTeX.'}`, false, true);
                this.hideActionProgress(3000);
                this.showDrawerAlert(data.error || 'Failed to fix LaTeX.', true);
            }
        })
        .catch(err => {
            clearTimeout(timeoutId);
            clearTimeout(t1);
            clearTimeout(t2);

            if (btnFixLatex) {
                btnFixLatex.disabled = false;
                btnFixLatex.style.opacity = '1';
                btnFixLatex.innerHTML = originalHtml;
            }

            const isTimeout = err.name === 'AbortError';
            const errorMsg = isTimeout ? 'Request timed out after 20 seconds.' : (err.message || 'Error while running Fix LaTeX.');

            this.showActionProgress(100, errorMsg, false, true);
            this.hideActionProgress(3000);

            console.error('Fix LaTeX error:', err);
            this.showDrawerAlert(errorMsg, true);
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

        // Initialize / Load interactive Formula Lineage Graph
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

        // 1. Parent Master Equation Link
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

        // 2. Child Subcomponents Grid
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
                // Filter out non-TeX prose strings mistakenly stored as child.equation
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
        this.triggerTypeset([details]);
    },

    renderCasLimitsCard(latex, semanticVariables = {}) {
        const card = document.getElementById('cas-limits-card');
        const chipsContainer = document.getElementById('cas-quick-limits');
        const resultBox = document.getElementById('cas-result-box');
        const limitMath = document.getElementById('cas-limit-math');
        const seriesMath = document.getElementById('cas-series-math');
        const loadingSpinner = document.getElementById('cas-loading-spinner');
        const evalTitle = document.getElementById('cas-eval-title');

        if (!card || !chipsContainer || !resultBox || !latex) return;

        // Reset display
        card.style.display = 'flex';
        resultBox.style.display = 'none';
        chipsContainer.innerHTML = '';

        // Derive candidate variables from formula by first stripping LaTeX control sequences
        const candidateVars = new Set();
        const strippedLatex = latex.replace(/\\[a-zA-Z]+/g, ' ');
        const varMatches = strippedLatex.match(/[a-zA-Z]/g) || [];
        varMatches.forEach(v => {
            if (!['d', 'e', 'i', 'j'].includes(v.toLowerCase())) {
                candidateVars.add(v);
            }
        });

        // Common physical asymptotic limit presets
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

        // Add generic chips for any remaining free variables
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
            let lhsDisplay = data.lhs ? `${data.lhs} \\to ` : '';
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

    /**
     * Extracts all elements/symbols in the LaTeX equation, merges with official mapping,
     * resolves default values, and renders them in order of appearance.
     */
    detectDomainFromLatex(latex) {
        if (!latex) return null;
        latex = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');
        
        // 1. Syntactic / Structural Anchor Detection (Rule-Based overrides)
        // Relativistic field theory / Gauge theory / General Relativity: D_\mu, \partial_\mu, \gamma^\mu, \Gamma^\mu, g_{\mu\nu}, R_{\mu\nu}, etc.
        if (/(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)_(?:\\mu|\\nu|\\alpha|\\beta|\\sigma|\\rho)/.test(latex) || /(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)\^(?:\\mu|\\nu|\\alpha|\\beta|\\sigma|\\rho)/.test(latex)) {
            return 'quantum_mechanics';
        }
        
        // Vector calculus / Stokes' / Curl / Circulation: \oint_C, \iint_S, \nabla \times
        if (/\\(oint|iint|iiint|int)_\{?[CSV]\}?/.test(latex) || /\\nabla\s*\\times/.test(latex)) {
            if (/(?:\\mathbf\{E\}|\\mathbf\{B\}|\\mathbf\{J\}|\\epsilon_0|\\mu_0|q|e|\\Phi)/.test(latex)) {
                return 'electromagnetism';
            }
            return 'classical_mechanics';
        }

        // Poisson brackets: \{ A, B \} or \{ \rho, H \}
        if (/\\\{\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*,\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*\\\}/.test(latex)) {
            return 'classical_mechanics';
        }
        
        // Bra-ket notation: \langle ... \rangle or \mid
        if (/\\langle|\\rangle|\\mid/.test(latex)) {
            return 'quantum_mechanics';
        }
        
        // Mathematical Logic & Philosophy of Physics notation: \forall, \exists, \vdash, \models, \iff, \subset, \in, \cup, \cap
        if (/\\(forall|exists|nexists|vdash|dashv|models|vDash|Vdash|nVdash|nvdash|iff|implies|impliedby|subset|subseteq|supset|supseteq|cap|cup|in|notin|ni|setminus|emptyset|varnothing)\b/.test(latex)) {
            return 'philosophy_of_physics';
        }

        // Thermodynamic differentials: dU, dS, dV, dH, dG, dQ
        if (/\b(dU|dS|dV|dH|dG|dQ|dW)\b/.test(latex)) {
            return 'thermodynamics';
        }
        
        // Helper to check if a specific symbol is present in the LaTeX string with safe boundary checks
        const hasSymbol = (sym) => {
            if (sym.startsWith('\\')) {
                const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                return new RegExp(escaped + '(?![a-zA-Z])').test(latex);
            }
            return new RegExp('(?<![a-zA-Z\\\\])' + sym + '(?![a-zA-Z])').test(latex);
        };

        const counts = {
            classical_mechanics: 0,
            thermodynamics: 0,
            electromagnetism: 0,
            quantum_mechanics: 0,
            optics: 0,
            philosophy_of_physics: 0
        };
        
        // Check for domain anchors with boundary safety
        const ANCHORS = {
            philosophy_of_physics: [
                '\\forall', '\\exists', '\\vdash', '\\models', '\\iff', '\\implies', '\\subset', '\\subseteq', '\\cup', '\\cap', '\\equiv'
            ],
            thermodynamics: [
                'T', 'S', 'Q', 'U', 'H', '\\Omega', '\\ln', 'k_B', 'R', 'P', 'V',
                '\\beta', '\\mu', 'N_A'
            ],
            electromagnetism: [
                '\\mathbf{E}', '\\mathbf{B}', '\\mathbf{J}', '\\rho', '\\epsilon_0',
                '\\mu_0', '\\Phi', '\\mathbf{A}', 'q', 'e', 'E_x', 'E_y', 'E_z',
                'B_x', 'B_y', 'B_z', '\\nabla'
            ],
            quantum_mechanics: [
                '\\hbar', '\\Psi', '\\psi', '\\hat{H}', '\\phi', '\\hat{p}', '\\hat{x}',
                '\\mid', '\\rangle', '\\langle', 'i', '\\hat{A}',
                '\\hat{B}', '\\dagger'
            ],
            optics: [
                'n', '\\lambda', 'f', '\\theta', '\\omega', 'k', 'I', 'I_0',
                '\\sin', '\\cos', '\\nu'
            ],
            classical_mechanics: [
                'x', 'v', 'a', 'F', 'm', 'p', 't', '\\tau', 'g', 'r', 'L', 'K'
            ]
        };

        for (const [domain, symbols] of Object.entries(ANCHORS)) {
            symbols.forEach(sym => {
                if (hasSymbol(sym)) {
                    counts[domain] = (counts[domain] || 0) + 1;
                }
            });
        }
        
        // Apply co-occurrence multipliers
        if (hasSymbol('T') && hasSymbol('V') && (hasSymbol('L') || hasSymbol('\\mathcal{L}'))) {
            counts.classical_mechanics += 4.0;
        }
        if (hasSymbol('F') && hasSymbol('m') && hasSymbol('a')) {
            counts.classical_mechanics += 4.0;
        }
        if (hasSymbol('P') && hasSymbol('V') && hasSymbol('T')) {
            counts.thermodynamics += 4.0;
        }
        if (hasSymbol('k_B') && hasSymbol('T')) {
            counts.thermodynamics += 3.0;
        }
        if (hasSymbol('\\epsilon_0') || hasSymbol('\\mu_0')) {
            counts.electromagnetism += 4.0;
        }
        if (hasSymbol('\\mathbf{E}') && hasSymbol('\\mathbf{B}')) {
            counts.electromagnetism += 4.0;
        }
        if (hasSymbol('\\hbar') && (hasSymbol('\\psi') || hasSymbol('\\Psi'))) {
            counts.quantum_mechanics += 5.0;
        }
        if (hasSymbol('n') && hasSymbol('\\lambda')) {
            counts.optics += 3.0;
        }

        let bestDomain = null;
        let maxCount = 0;
        for (const [domain, count] of Object.entries(counts)) {
            if (count > maxCount) {
                maxCount = count;
                bestDomain = domain;
            }
        }
        
        return bestDomain || 'classical_mechanics';
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

    extractAllMathTokens(latex, officialVariables = {}) {
        if (!latex) return [];
        latex = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');

        const found = [];
        const seen = new Set();
        const consumedSubtokens = new Set();

        const addToken = (symbol, type) => {
            if (!symbol || seen.has(symbol)) return;
            seen.add(symbol);
            found.push({ symbol, type });
        };

        // Pure structural formatting commands and delimiters to completely ignore
        const pureSyntaxDelimiters = [
            '\\rangle', '\\langle', '\\mid', '|', '(', ')', '[', ']', '{', '}', '+', '-', '=', '/', 
            '\\cdot', '\\times', '\\div', '\\left', '\\right', '\\text', '\\mathrm', '\\mathsf',
            '\\colon', '\\quad', '\\qquad', '\\dots', '\\cdots', '\\ldots', '\\ddots', '\\vdots',
            '\\circ', '\\bullet'
        ];
        pureSyntaxDelimiters.forEach(d => {
            consumedSubtokens.add(d);
            consumedSubtokens.add(d.replace(/^\\/, ''));
        });

        // Priority 1: Match against officialVariables from formula database
        if (officialVariables && typeof officialVariables === 'object') {
            const sortedOfficialKeys = Object.keys(officialVariables).sort((a, b) => b.length - a.length);
            sortedOfficialKeys.forEach(key => {
                if (!key || consumedSubtokens.has(key) || consumedSubtokens.has(key.replace(/^\\/, ''))) return;
                const escaped = key.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(escaped, 'g');
                if (regex.test(latex)) {
                    const offObj = officialVariables[key];
                    const type = (offObj && typeof offObj === 'object' && offObj.type) ? offObj.type : ((typeof offObj === 'string' && /operator/i.test(offObj)) || key.startsWith('\\hat') || key.includes('\\partial') || key.includes('\\nabla') ? 'operator' : 'variable');
                    addToken(key, type);

                    // Track sub-tokens to consume
                    const subParts = key.match(/\\[a-zA-Z]+|[a-zA-Z]/g) || [];
                    subParts.forEach(part => {
                        const cleanPart = part.replace(/^\\/, '');
                        if (cleanPart.length > 0) {
                            consumedSubtokens.add(cleanPart);
                            consumedSubtokens.add(part);
                            consumedSubtokens.add('\\' + cleanPart);
                        }
                    });
                }
            });
        }

        // Extract subscripts as modifiers from original raw latex
        const subscriptModRegex = /_\{([^\}]+)\}|_([a-zA-Z\\]+)/g;
        let subModMatch;
        while ((subModMatch = subscriptModRegex.exec(latex)) !== null) {
            let content = subModMatch[1] || subModMatch[2];
            content = content.replace(/\\(text|mathrm|mathsf|mathrm)\{([^\}]+)\}/g, '$2').trim();
            if ((/^[a-zA-Z]{2,}$/.test(content) || this.modifierGlossary[content]) && !consumedSubtokens.has(content)) {
                addToken(content, 'modifier');
            }
        }

        // Extract superscripts as modifiers from original raw latex
        const superscriptModRegex = /\^\{([^\}]+)\}|\^([a-zA-Z0-9+\-\*\\/]+|\*|\+|0|\-|\\dagger|\\circ|\\prime)/g;
        let superModMatch;
        while ((superModMatch = superscriptModRegex.exec(latex)) !== null) {
            let content = superModMatch[1] || superModMatch[2];
            content = content.trim();
            const isStandardModifier = this.modifierGlossary[content] || 
                                       content === '\'' || 
                                       content === '\\prime' ||
                                       /^(T|\top|\dagger|\circ|\*|\ast|\+|-|0)$/.test(content);
            if (isStandardModifier) {
                addToken(content, 'modifier');
            } else if (/\\(dagger|circ|prime)\b/.test(content)) {
                const cmdMatch = content.match(/\\(dagger|circ|prime)/);
                if (cmdMatch) {
                    addToken('\\' + cmdMatch[1], 'modifier');
                }
            } else if (/^[a-zA-Z]{2,}$/.test(content) && !/^[0-9]+$/.test(content)) {
                addToken(content, 'modifier');
            }
        }

        let text = latex.trim();

        // Pre-scan for specific physical constants with subscripts (to prevent stripping their subscripts)
        const constantSubscriptRegex = /\\(epsilon|mu|k|a|m|g|G|N)_(?:0|\{0\}|B|\{B\}|e|\{e\}|p|\{p\}|n|\{n\}|F|\{F\}|A|\{A\})(?![a-zA-Z])/g;
        let constMatch;
        while ((constMatch = constantSubscriptRegex.exec(text)) !== null) {
            const fullMatch = constMatch[0];
            // Normalize: strip curly braces from subscript for token representation
            const normalizedSymbol = fullMatch.replace(/_\{([^\}]+)\}/, '_$1');
            addToken(normalizedSymbol, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for integration boundaries: \oint_C, \iint_S, \int_a^b (run on original text before subscripts are stripped)
        const integralBoundaryRegex = /\\(int|oint|iint|iiint)_\{?([a-zA-Z0-9]+)\}?/g;
        let boundaryMatch;
        while ((boundaryMatch = integralBoundaryRegex.exec(text)) !== null) {
            const boundaryVar = boundaryMatch[2];
            if (boundaryVar && /^[a-zA-Z]$/.test(boundaryVar)) {
                addToken(boundaryVar, 'integration_boundary');
            }
        }

        // 1. Strip LaTeX structure environments
        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, ' ').replace(/\\end\{[a-zA-Z]+\}/g, ' ');

        // 1.1. Pre-scan for official database keys to keep them grouped as unified terms
        if (officialVariables) {
            const sortedOfficialKeys = Object.keys(officialVariables).sort((a, b) => b.length - a.length);
            for (const sym of sortedOfficialKeys) {
                if (this.latexContainsSymbol(text, sym)) {
                    const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
                    addToken(sym, isOperator ? 'operator' : 'variable');
                    
                    // Replace matched symbol in text to avoid partial matching later
                    let pattern;
                    const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                    if (sym.startsWith('\\')) {
                        pattern = escaped + '(?![a-zA-Z])';
                    } else if (/^[a-zA-Z0-9_\{\}\^\dagger]+$/.test(sym)) {
                        pattern = '\\b' + escaped + '\\b';
                    } else {
                        pattern = escaped;
                    }
                    const regex = new RegExp(pattern, 'g');
                    text = text.replace(regex, ' ');
                }
            }
        }

        // 1.5. Parse subscripts BEFORE stripping visual modifiers to detect \text{...} wrappers
        text = text.replace(/_\{([^\}]+)\}/g, (match, content) => {
            // Strip text labels inside \text{...} or \mathrm{...}
            let cleanContent = content;
            let hasLabelText = true;
            while (hasLabelText) {
                const nextContent = cleanContent.replace(/\\(text|mathrm|mathsf|mathrm)\{((?:[^{}]|\{[^{}]*\})*)\}/g, ' ');
                if (nextContent === cleanContent) {
                    hasLabelText = false;
                } else {
                    cleanContent = nextContent;
                }
            }

            // Extract Greek letters (control sequences starting with backslash)
            const greekPattern = /\\[a-zA-Z]+/g;
            const greekMatches = cleanContent.match(greekPattern) || [];

            // Extract single Roman letters
            const plainText = cleanContent.replace(/\\[a-zA-Z]+/g, '').trim();
            const isLabelWord = plainText.length >= 3 && !/\d/.test(plainText);

            let activeIndices = [...greekMatches];
            if (!isLabelWord && plainText.length > 0) {
                const letters = plainText.match(/[a-zA-Z]/g) || [];
                activeIndices.push(...letters);
            }

            return activeIndices.length > 0 ? ' ' + activeIndices.join(' ') + ' ' : ' ';
        });

        text = text.replace(/_([a-zA-Z0-9])/g, (match, char) => {
            if (/[a-zA-Z]/.test(char)) {
                return ' ' + char + ' ';
            }
            return ' ';
        });

        // Pre-scan for mathcal variables: \mathcal{L} or \mathcal{H}
        const mathcalRegex = /\\mathcal\{([a-zA-Z])\}/g;
        let mathcalMatch;
        while ((mathcalMatch = mathcalRegex.exec(text)) !== null) {
            const fullMatch = mathcalMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }



        // 2. Strip visual modifiers: \hat{H} -> H, \mathbf{p} -> p
        let hasStyles = true;
        while (hasStyles) {
            const nextText = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextText === text) {
                hasStyles = false;
            } else {
                text = nextText;
            }
        }
        text = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');


        // Check for spacetime derivatives: \partial_\mu, \partial^\mu, \partial_\nu, \partial^\nu
        const spacetimeDerivRegex = /\\partial_(?:\\mu|\\nu|\\alpha|\\beta|[a-zA-Z0-9])|\\partial\^(?:\\mu|\\nu|\\alpha|\\beta|[a-zA-Z0-9])/g;
        const spaceMatches = [...text.matchAll(spacetimeDerivRegex)];
        for (const spaceMatch of spaceMatches) {
            const fullMatch = spaceMatch[0];
            addToken(fullMatch, 'spacetime_derivative');
            const idxVar = fullMatch.includes('_') ? fullMatch.split('_')[1] : fullMatch.split('^')[1];
            if (idxVar) {
                addToken(idxVar, 'variable');
            }
        }
        text = text.replace(spacetimeDerivRegex, ' ');

        // Check for partial derivatives: \frac{\partial \Psi}{\partial t}
        const partialRegex = /\\frac\{\\partial\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{\\partial\s*([a-zA-Z\\]+)\}/g;
        let partMatch;
        while ((partMatch = partialRegex.exec(text)) !== null) {
            const fullMatch = partMatch[0];
            const numVar = partMatch[1];
            const denVar = partMatch[2];
            
            addToken(fullMatch, 'operator');
            
            if (numVar) {
                const cleanNum = numVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanNum)) {
                    addToken(cleanNum, 'variable');
                }
            }
            if (denVar) {
                const cleanDen = denVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanDen)) {
                    addToken(cleanDen, 'variable');
                }
            }
            
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for total derivatives: \frac{d\rho}{dt}
        const totalDerivRegex = /\\frac\{d\^?[0-9]*\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{d\s*([a-zA-Z\\]+)\^?[0-9]*\}/g;
        let totMatch;
        while ((totMatch = totalDerivRegex.exec(text)) !== null) {
            const fullMatch = totMatch[0];
            const numVar = totMatch[1];
            const denVar = totMatch[2];
            
            addToken(fullMatch, 'operator');
            
            if (numVar) {
                const cleanNum = numVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanNum)) {
                    addToken(cleanNum, 'variable');
                }
            }
            if (denVar) {
                const cleanDen = denVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanDen)) {
                    addToken(cleanDen, 'variable');
                }
            }

            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for integration differentials: d\mathbf{l}, d\mathbf{S}, d\vec{r}, dx, dy, dt, dm, dV, dA
        const differentialRegex = /\bd(?:\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([a-zA-Z])\}|([a-zA-Z]))\b/g;
        let diffMatch;
        while ((diffMatch = differentialRegex.exec(text)) !== null) {
            const fullMatch = diffMatch[0];
            const baseVar = diffMatch[2] || diffMatch[3];
            
            // Add 'd' as differential operator
            addToken('d', 'differential_operator');
            
            // Add base variable
            if (baseVar) {
                addToken(baseVar, 'variable');
            }
            
            // Replace the full match to avoid standalone 'd' or baseVar from matching later
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }


        // Check for dot derivatives: \dot{q} or \dot q
        const dotRegex = /\\(dot|ddot)\{([a-zA-Z\\]+)\}|\\(dot|ddot)\s*([a-zA-Z])/g;
        let dotMatch;
        while ((dotMatch = dotRegex.exec(text)) !== null) {
            const fullMatch = dotMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for subscripts: q_i or k_B
        const subscriptRegex = /([a-zA-Z\\]+)_([a-zA-Z0-9]+|\{[a-zA-Z0-9]+\})/g;
        let subMatch;
        while ((subMatch = subscriptRegex.exec(text)) !== null) {
            const fullMatch = subMatch[0];
            if (fullMatch.startsWith('\\partial') || fullMatch.startsWith('\\nabla')) continue;
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // 3. Scan for standard physical constants symbols from constants.json first
        const constants = window.PHYSICS_CONSTANTS || {};
        for (const [key, details] of Object.entries(constants)) {
            const sym = details.symbol;
            if (this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'constant');
                // Replace matched constant in text with space to avoid partial matching later
                let pattern;
                const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                if (sym.startsWith('\\')) {
                    pattern = escaped + '(?![a-zA-Z])';
                } else if (/^[a-zA-Z0-9_\{\}]+$/.test(sym)) {
                    pattern = '\\b' + escaped + '\\b';
                } else {
                    pattern = escaped;
                }
                const regex = new RegExp(pattern, 'g');
                text = text.replace(regex, ' ');
            }
        }

        // 5. Strip braces, colons, semicolons, and commas
        text = text.replace(/[\{\}:;,]/g, ' ');

        // 5b. Split adjacent plain Roman letters (Strategy A)
        // E.g., F = \frac d dt (mv) -> F = \frac d d t (m v)
        text = text.replace(/(\\[a-zA-Z]+)|([a-zA-Z]+)/g, (match, latexCmd, plainWord) => {
            if (latexCmd) {
                return latexCmd;
            }
            if (plainWord && plainWord.length > 1) {
                return plainWord.split('').join(' ');
            }
            return plainWord;
        });

        // 6. Scan for explicit standard mathematical and logical operators
        const standardOperators = [
            '\\forall', '\\exists', '\\nexists', '\\in', '\\notin', '\\ni', '\\owns',
            '\\subset', '\\subseteq', '\\supset', '\\supseteq', '\\cap', '\\cup', '\\setminus',
            '\\vdash', '\\dashv', '\\models', '\\vDash', '\\Vdash', '\\nVdash', '\\nvdash',
            '\\iff', '\\implies', '\\impliedby', '\\Rightarrow', '\\Leftarrow', '\\Leftrightarrow',
            '\\land', '\\lor', '\\neg', '\\lnot', '\\top', '\\bot',
            '\\int', '\\oint', '\\iint', '\\iiint', '\\sum', '\\prod', '\\partial', '\\nabla', '\\Delta',
            '\\sqrt', '\\Tr', '\\det',
            '\\approx', '\\equiv', '\\sim', '\\simeq', '\\cong', '\\propto', '\\asymp', '\\doteq',
            '\\le', '\\ge', '\\leq', '\\geq', '\\ne', '\\neq', '\\ll', '\\gg', '\\pm', '\\mp', '\\to', '\\mapsto'
        ];

        standardOperators.forEach(op => {
            if (!consumedSubtokens.has(op) && this.latexContainsSymbol(text, op)) {
                addToken(op, 'operator');
                consumedSubtokens.add(op);
                consumedSubtokens.add(op.replace(/^\\/, ''));
            }
        });

        // 7. Scan for multi-character LaTeX Greek letters & variables
        const greekPattern = /\\[a-zA-Z]+/g;
        let match;
        while ((match = greekPattern.exec(text)) !== null) {
            const sym = match[0];
            const ignoredCmds = new Set([
                '\\frac', '\\left', '\\right', '\\cdot', '\\times', '\\div', 
                '\\colon', '\\quad', '\\qquad', '\\dots', '\\cdots', '\\ldots', '\\ddots', '\\vdots',
                '\\circ', '\\bullet', '\\ast', '\\star',
                '\\boldsymbol', '\\mathbf', '\\mathsf', '\\mathrm', '\\text', '\\mathcal', 
                '\\vec', '\\hat', '\\bar', '\\tilde', '\\dot', '\\ddot', '\\underline'
            ]);
            if (ignoredCmds.has(sym) || consumedSubtokens.has(sym) || consumedSubtokens.has(sym.replace(/^\\/, ''))) continue;
            
            const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
            addToken(sym, isOperator ? 'operator' : 'variable');
        }

        // 8. Scan for single Roman letters (a-z, A-Z)
        text = text.replace(/\\[a-zA-Z]+/g, ' ');
        const romanPattern = /[a-zA-Z]/g;
        while ((match = romanPattern.exec(text)) !== null) {
            const sym = match[0];
            if (!consumedSubtokens.has(sym) && this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'variable');
            }
        }

        // Sort found tokens by order of appearance in the original LaTeX string
        // using a cleaned LaTeX string to avoid false positives inside formatting commands
        const getCleanSearchString = (str) => {
            let clean = str;
            // 1. Replace \text{...} and \mathrm{...} environments with spaces
            clean = clean.replace(/\\(text|mathrm|mathsf)\{([^\}]+)\}/g, match => ' '.repeat(match.length));
            // 2. Replace structural/formatting commands with spaces
            const structuralRegex = /\\(frac|left|right|sqrt|cdot|times|div|iff|implies|impliedby|forall|exists|nexists|in|notin|ni|subset|subseteq|supset|supseteq|cap|cup|setminus|emptyset|vdash|dashv|models|vDash|Vdash|nVdash|nvdash|Rightarrow|Leftarrow|Leftrightarrow|rightarrow|leftarrow|leftrightarrow|to|mapsto|land|lor|neg|lnot|top|bot|approx|equiv|sim|simeq|cong|propto|asymp|doteq|ge|le|geq|leq|ne|neq|ll|gg|pm|mp|colon|quad|qquad|dots|cdots|ldots|circ|bullet|ast|star|boldsymbol|mathbf|mathsf|mathrm|text|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\b/g;
            clean = clean.replace(structuralRegex, match => ' '.repeat(match.length));
            // 3. Replace word-like subscripts of 3+ letters (e.g. _{ext}, _ext) with spaces
            clean = clean.replace(/_\{[a-zA-Z]{3,\}\}/g, match => ' '.repeat(match.length));
            clean = clean.replace(/_[a-zA-Z]{3,}/g, match => ' '.repeat(match.length));
            return clean;
        };

        const cleanStylesForSorting = (str) => {
            let res = str;
            let hasStyles = true;
            while (hasStyles) {
                const next = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
                if (next === res) {
                    hasStyles = false;
                } else {
                    res = next;
                }
            }
            res = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');
            return res;
        };

        const cleanSearch = getCleanSearchString(latex);
        const cleanLatex = cleanStylesForSorting(latex);

        found.sort((a, b) => {
            let indexA = -1;
            if (a.type === 'modifier') {
                const escaped = a.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexA = match ? match.index : latex.indexOf(a.symbol);
            } else {
                const hasStructuralA = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(a.symbol);
                indexA = hasStructuralA ? cleanLatex.indexOf(a.symbol) : cleanSearch.indexOf(a.symbol);
            }
            
            let indexB = -1;
            if (b.type === 'modifier') {
                const escaped = b.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexB = match ? match.index : latex.indexOf(b.symbol);
            } else {
                const hasStructuralB = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(b.symbol);
                indexB = hasStructuralB ? cleanLatex.indexOf(b.symbol) : cleanSearch.indexOf(b.symbol);
            }
            
            return indexA - indexB;
        });

        return found;
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

    tokenizeLatexSymbols(latex) {
        // Obsoleted: Replaced by the comprehensive extractAllMathTokens() above
        return [];
    },

    latexContainsSymbol(latex, sym) {
        // Escape regex special chars
        const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        let regexStr = escaped;
        
        if (sym.startsWith('\\')) {
            regexStr = escaped + '(?![a-zA-Z])';
        } else {
            regexStr = '(?<![a-zA-Z\\\\_])' + escaped + '(?![a-zA-Z])';
        }

        const regex = new RegExp(regexStr);
        return regex.test(latex);
    },

    setupSolverLink(latex) {
        // Deprecated: standalone dimensional solver removed in favor of upcoming integrated lab tools workbench
    },

    /**
     * Translates LaTeX formulas into standard mathematical programming/ASCIImath style
     * for seamless compatibility with the Dimensional Solver.
     */
    latexToPlainText(latex) {
        if (!latex) return '';
        
        let text = latex.trim().replace(/\\par\b/g, ' ');

        // 1. Strip delimiters if present
        text = text.replace(/^\\\(/, '').replace(/\\\)$/, '');
        text = text.replace(/^\\\[/, '').replace(/\\\]$/, '');
        text = text.replace(/^\$\$/, '').replace(/\$\$$/, '');
        text = text.replace(/^\$/, '').replace(/\$/, '');

        // 2. Normalize derivatives and common fraction structures
        text = text.replace(/\\frac\{d\}\{d([a-zA-Z])\}/g, 'd/d$1');
        text = text.replace(/\\frac\{\\partial\}\{\\partial\s*([a-zA-Z])\}/g, 'partial/partial $1');
        
        // General fractions: \frac{A}{B} -> (A) / (B)
        let hasFraction = true;
        while (hasFraction) {
            const nextText = text.replace(/\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g, '($1)/($2)');
            if (nextText === text) {
                hasFraction = false;
            } else {
                text = nextText;
            }
        }

        // 3. Strip visual style/font command wrappers: e.g. \mathbf{F} -> F
        let hasStyles = true;
        while (hasStyles) {
            const nextText = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextText === text) {
                hasStyles = false;
            } else {
                text = nextText;
            }
        }
        
        // Command blocks without curly braces: e.g. \mathbf F -> F
        text = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s+([a-zA-Z0-9])/g, '$2');

        // 4. Clean braces around exponents & subscripts: e.g. _{ext} -> _ext, ^{2} -> ^2
        text = text.replace(/_\{([^}]+)\}/g, '_$1');
        text = text.replace(/\^\{([^}]+)\}/g, '^$1');

        // 5. Map LaTeX Greek letters & symbols to plain text identifiers
        const greekMap = {
            '\\hbar': 'hbar',
            '\\epsilon_0': 'eps0',
            '\\epsilon': 'epsilon',
            '\\mu_0': 'mu0',
            '\\mu': 'mu',
            '\\pi': 'pi',
            '\\omega': 'omega',
            '\\rho': 'rho',
            '\\sigma': 'sigma',
            '\\lambda': 'lambda',
            '\\nu': 'nu',
            '\\theta': 'theta',
            '\\xi': 'xi',
            '\\eta': 'eta',
            '\\partial': 'partial',
            '\\delta': 'delta',
            '\\Delta': 'Delta',
            '\\alpha': 'alpha',
            '\\beta': 'beta',
            '\\gamma': 'gamma',
            '\\tau': 'tau',
            '\\phi': 'phi',
            '\\psi': 'psi',
            '\\chi': 'chi',
            '\\zeta': 'zeta',
            '\\dots': '...',
            '\\infty': 'inf'
        };
        
        for (const [latexSym, plainSym] of Object.entries(greekMap)) {
            const escapedSym = latexSym.replace(/\\/g, '\\\\');
            const reg = new RegExp(escapedSym, 'g');
            text = text.replace(reg, plainSym);
        }

        // 6. Replace operators
        text = text.replace(/\\cdot/g, ' * ');
        text = text.replace(/\\times/g, ' * ');
        text = text.replace(/\\ast/g, ' * ');
        text = text.replace(/\\star/g, ' * ');
        text = text.replace(/\\div/g, ' / ');

        // 7. Simplify brackets
        text = text.replace(/\\left\(/g, '(').replace(/\\right\)/g, ')');
        text = text.replace(/\\left\[/g, '[').replace(/\\right\]/g, ']');
        text = text.replace(/\\left\\\{/g, '{').replace(/\\right\\\}/g, '}');

        // 8. Simplify matrix blocks
        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, '[').replace(/\\end\{[a-zA-Z]+\}/g, ']');
        text = text.replace(/&/g, ', ').replace(/\\\\/g, ', ');

        // 9. Final cleanups: strip stray backslashes before variables and extra whitespaces
        text = text.replace(/\\([a-zA-Z]+)/g, '$1');
        text = text.replace(/\s+/g, ' ');
        text = text.replace(/\*\s*\*/g, '*');
        text = text.trim();

        return text;
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
            
            // Automatically detect and wrap parenthesized LaTeX expressions in math delimiters
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
    },

    wrapTextMathDelimiters(text) {
        if (typeof window !== 'undefined' && window.MathProseFormatter && typeof window.MathProseFormatter.format === 'function') {
            return window.MathProseFormatter.format(text);
        }
        if (typeof text !== 'string' || !text) return text;
        
        const placeholders = [];
        let tempText = text.replace(/\r\n/g, '\n');
        tempText = tempText.replace(/\\n(?=\s*(?:\d+\.|\*|-))/g, '\n');
        tempText = tempText.replace(/\\par\b/g, ' ');
        
        function protect(match) {
            placeholders.push(match);
            return `\uE000MATH_${placeholders.length - 1}\uE000`;
        }

        const greekMap = {
            'Γ': '\\Gamma', 'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta',
            'ε': '\\epsilon', 'θ': '\\theta', 'λ': '\\lambda', 'μ': '\\mu', 'ν': '\\nu',
            'π': '\\pi', 'ρ': '\\rho', 'σ': '\\sigma', 'τ': '\\tau', 'φ': '\\phi',
            'ψ': '\\psi', 'ω': '\\omega', 'Ω': '\\Omega', 'Δ': '\\Delta'
        };

        // 1. Protect existing MathJax delimiters ($$, $, \(\), \[\]) NON-GREEDILY FIRST
        tempText = tempText.replace(/\\\[[\s\S]*?\\\]/g, protect);
        tempText = tempText.replace(/\\\([\s\S]*?\\\)/g, protect);
        tempText = tempText.replace(/\$\$[\s\S]*?\$\$/g, protect);
        tempText = tempText.replace(/\$([^\$\n]+?)\$/g, protect);

        // 2. Fix un-delimited equation patterns like "Γ = \frac..." or "var = \frac..."
        tempText = tempText.replace(/([A-Za-z\u0370-\u03FF]+)\s*=\s*(\\[a-zA-Z]+(?:\{[^{}]*\}|\([^)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^\/\*\+\-])+)/g, (match, lhs, rhs) => {
            if (match.includes('\uE000')) return match;
            let cleanLhs = lhs.trim();
            if (greekMap[cleanLhs]) cleanLhs = greekMap[cleanLhs];
            return protect(`\\(${cleanLhs} = ${rhs.trim()}\\)`);
        });

        // 3. Convert limiting case phrases like "(T) approaches zero" or "Γ approaches infinity"
        tempText = tempText.replace(/(\([a-zA-Z0-9_\^ ]+\)|[A-Za-z\u0370-\u03FF]+)\s+approaches\s+(zero|infinity|0|\\infty)/gi, (match, sym, target) => {
            if (match.includes('\uE000')) return match;
            let cleanSym = sym.replace(/^\(|\)$/g, '').trim();
            if (greekMap[cleanSym]) cleanSym = greekMap[cleanSym];
            const texTarget = (target.toLowerCase() === 'infinity') ? '\\infty' : '0';
            return protect(`\\(${cleanSym} \\to ${texTarget}\\)`);
        });

        // Helper for checking if text in parens is a math variable vs English prose
        function isMathParen(innerStr) {
            const s = innerStr.trim();
            if (!s) return false;
            if (s.includes(',') || s.includes(';')) return false;
            if (/\b(or|in|and|of|for|at|to|is|with|where|if|not|by|on|the|an|e\.g\.|i\.e\.|eigenfunctions?|eigenvalues?)\b/i.test(s)) return false;
            if (/^[a-zA-Z]{3,}$/.test(s)) return false;
            const units = ['C', 'J', 'K', 's', 'V', 'W', 'Pa', 'Hz', 'N', 'rad', 'mol'];
            if (units.includes(s)) return false;
            const words = s.split(/\s+/);
            if (words.length > 1) {
                const allMath = words.every(w => /^[a-zA-Z0-9_\^\\]+$/.test(w) && !/^[a-zA-Z]{3,}$/.test(w));
                if (!allMath) return false;
            }
            return true;
        }

        // 4. Convert parenthesized variable notations in prose like (Ze)^2, (k_B T), (Z), (e), (a), (k_B), (T)
        tempText = tempText.replace(/\((?:[a-zA-Z0-9_\^\s]|\\_[a-zA-Z0-9]+)+\)(?:\^[0-9a-zA-Z{}]+)?/g, (match) => {
            if (match.includes('\uE000')) return match;
            const innerStr = match.slice(1, match.indexOf(')')).trim();
            if (!isMathParen(innerStr)) return match;
            if (match.includes('^')) {
                const exp = match.slice(match.indexOf(')') + 1);
                return protect(`\\((${innerStr})${exp}\\)`);
            } else {
                return protect(`\\(${innerStr}\\)`);
            }
        });

        // 5. Convert standalone Greek letters in prose to LaTeX (e.g. Γ -> \(\Gamma\))
        tempText = tempText.replace(/([ΓαβγδεθλμνπρστφψωΩΔ])/g, (match) => {
            if (match.includes('\uE000')) return match;
            const tex = greekMap[match] || match;
            return protect(`\\(${tex}\\)`);
        });

        // 5.2. Convert un-delimited subscripted variables or operations (e.g. B_i - B_j, B_i > B_j, k_B T, B_i, B_j)
        tempText = tempText.replace(/\b([A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+)(?:\s*[-+><=]\s*[A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+))*(?:\s+[A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+))?)\b/g, (match) => {
            if (match.includes('\uE000')) return match;
            if (/^[a-zA-Z]{3,}$/.test(match)) return match;
            return protect(`\\(${match}\\)`);
        });

        // 5.5. Wrap complete un-delimited fraction and vector LaTeX expressions (e.g. \frac{d^2 \mathbf{r}}{dt^2})
        tempText = tempText.replace(/\\(?:frac|sqrt)\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})*|(?:[a-zA-Z]*\\(?:hat|vec|mathbf|mathrm|text|tilde|bar)\{[^}]+\}[a-zA-Z0-9_\^']*(?:\([^)]+\))?|[a-zA-Z]+\(\\[a-zA-Z]+\{[^}]+\}[^)]*\)|\|(?:\\[a-zA-Z]+\{[^}]+\}|[a-zA-Z0-9_\^'\s\-\+\\to\format])+\|)/g, match => {
            if (match.includes('\uE000')) return match;
            return protect(`\\(${match.trim()}\\)`);
        });

        // 6. Wrap remaining un-delimited LaTeX backslash tokens (excluding control whitespace)
        tempText = tempText.replace(/(?:(?<!\\)\\([a-zA-Z]+)(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\([^)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^])*)/g, match => {
            if (match.includes('\uE000')) return match;
            let trimmed = match.trim();
            if (!trimmed || trimmed === '\\' || trimmed === '\\n' || trimmed === '\\r' || trimmed === '\\t') return match;
            let trailingPunct = '';
            const punctMatch = trimmed.match(/[,.;:\)]+$/);
            if (punctMatch) {
                trailingPunct = punctMatch[0];
                trimmed = trimmed.substring(0, trimmed.length - trailingPunct.length);
            }
            const wrapped = `\\(${trimmed}\\)${trailingPunct}`;
            return protect(wrapped);
        });

        // 7. Parse Markdown formatting (bullet points, bold, italic, numbered lists)
        tempText = tempText.replace(/(?:^|\n)\s*[\*\-]\s+(.+)/g, (m, line) => '\n<div style="margin: 4px 0 4px 12px;">• ' + line + '</div>');
        tempText = tempText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        tempText = tempText.replace(/(?<!\*)\*(\S[^*]*?\S|\S)\*(?!\*)/g, '<em>$1</em>');
        tempText = tempText.replace(/(?:\r?\n)+(?=\d+\.\s+)/g, '<br><br>');
        tempText = tempText.replace(/\r?\n/g, '<br>');

        // 8. Restore protected math placeholders safely
        for (let i = 0; i < placeholders.length; i++) {
            let p = placeholders[i];
            if (p.startsWith('$') && !p.startsWith('$$') && p.endsWith('$')) {
                p = `\\(${p.slice(1, -1).trim()}\\)`;
            }
            p = p.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            tempText = tempText.replace(`\uE000MATH_${i}\uE000`, () => p);
        }

        return tempText;
    },

    synthesizeCustomOverview(latex) {
        let title = "Custom Physics Relation";
        let intro = "This mathematical expression represents a physical relation between variables.";
        let summary = "It is used to calculate the relative dynamics of the physical system.";
        let scenarios = [];

        // 0. Detect Static Limits of Maxwell's Equations
        if ((latex.includes('\\nabla \\times') || latex.includes('curl')) && (latex.includes('\\to 0') || latex.includes('=0') || latex.includes('\\to\\mathbf{0}')) && (latex.includes('\\mathbf{B}') || latex.includes('B'))) {
            title = "Static Limits of Maxwell's Equations";
            intro = "The steady-state or static limits of Maxwell's equations govern electromagnetic phenomena when charge distributions and currents are non-varying in time.";
            summary = "Under static conditions where fields do not change over time, the electric field is irrotational (curl-free), while magnetic fields are generated purely by steady electric current density.";
            scenarios = [
                {
                    condition: "Interpretation (Local Identity)",
                    implication: "In the static limit, the induced electric field from changing magnetic fields vanishes (\\nabla \\times \\mathbf{E} = 0), allowing the electric field to be represented as the gradient of a scalar electrostatic potential (\\mathbf{E} = -\\nabla V). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density (\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J})."
                },
                {
                    condition: "Symmetry & Coordinate Invariance",
                    implication: "Originates from time-translation invariance (\\partial / \\partial t = 0) and local gauge symmetry under steady current distributions."
                },
                {
                    condition: "Limiting Cases & Boundaries",
                    implication: "Valid in non-radiating, low-frequency, or zero-frequency steady-state electrodynamics where inductive and displacement currents are negligible."
                }
            ];
        }
        // 1. Detect Gauss's Law / Divergence
        else if (latex.includes('\\nabla \\cdot') || latex.includes('\\text{div}')) {
            title = "Vector Field Divergence Relation";
            let fieldSymbol = 'E';
            const match = latex.match(/\\nabla\s*\\cdot\s*(\\mathbf\{[A-Z]\}|[A-Za-z])/);
            if (match) {
                fieldSymbol = match[1];
            }
            intro = `The mathematical statement represents the <strong>Divergence</strong> of the vector field $${fieldSymbol}$. This is a foundational relation in field theory, measuring whether a given point in space acts as a source or a sink for the field lines.`;
            summary = `It states that the net flux of the field exiting an infinitesimal volume around a point is determined by the local source density.`;
            scenarios = [
                {
                    condition: `Positive Divergence (\\( \\nabla \\cdot ${fieldSymbol} > 0 \\))`,
                    implication: "The point acts as a source. Field lines diverge outward from this region (e.g., positive charges acting as sources of electric fields)."
                },
                {
                    condition: `Negative Divergence (\\( \\nabla \\cdot ${fieldSymbol} < 0 \\))`,
                    implication: "The point acts as a sink. Field lines converge inward toward this region (e.g., negative charges acting as sinks of electric fields)."
                },
                {
                    condition: `Zero Divergence (\\( \\nabla \\cdot ${fieldSymbol} = 0 \\))`,
                    implication: "The field is solenoidal. Field lines pass through the volume continuously without starting or stopping (e.g., magnetic fields, where the absence of magnetic monopoles guarantees zero divergence)."
                }
            ];
        }
        // 2. Detect Maxwell-Faraday / Curl
        else if (latex.includes('\\nabla \\times') || latex.includes('\\text{curl}')) {
            title = "Vector Field Curl Relation";
            let fieldSymbol = 'E';
            const match = latex.match(/\\nabla\s*\\times\s*(\\mathbf\{[A-Z]\}|[A-Za-z])/);
            if (match) {
                fieldSymbol = match[1];
            }
            intro = `The mathematical statement defines the <strong>Curl</strong> of the vector field $${fieldSymbol}$. This operator measures the rotational intensity, vorticity, or circulation of the field around a point.`;
            summary = `It quantifies the tendency of the vector field lines to curl or rotate around a given axis.`;
            scenarios = [
                {
                    condition: `Non-Zero Curl (\\( \\nabla \\times ${fieldSymbol} \\neq 0 \\))`,
                    implication: "The field possesses circulation or rotational eddies, indicating the presence of vortex sources (e.g., induced electric fields resulting from changing magnetic flux)."
                },
                {
                    condition: `Zero Curl (\\( \\nabla \\times ${fieldSymbol} = 0 \\))`,
                    implication: "The field is conservative or irrotational. Its line integral around any closed loop is zero, allowing it to be represented as the gradient of a scalar potential."
                }
            ];
        }
        // 3. Detect Schrödinger / Time-dependent Rate equation
        else if (latex.includes('\\partial') && latex.includes('\\partial t') || latex.includes('\\dot') || latex.includes('\\frac{d}{dt}') || latex.includes('\\ddot')) {
            title = "Time-Dependent Evolution Relation";
            intro = "This formula defines the <strong>temporal evolution</strong> (dynamics) of a physical system. It establishes how the state vector or physical quantities change with time.";
            summary = "It maps the rate of change of the system variables directly to the governing operator forces or energies.";
            scenarios = [
                {
                    condition: "Positive Time Derivative (\\( d/dt > 0 \\))",
                    implication: "The physical quantity or state magnitude is increasing or accumulating over time."
                },
                {
                    condition: "Negative Time Derivative (\\( d/dt < 0 \\))",
                    implication: "The physical quantity is decreasing, decaying, or dissipating over time."
                },
                {
                    condition: "Zero Time Derivative (\\( d/dt = 0 \\))",
                    implication: "The system is in a stationary state, steady-state configuration, or thermal equilibrium."
                }
            ];
        }
        // 4. Detect Action / Integrals
        else if (latex.includes('\\int') || latex.includes('\\oint')) {
            intro = "This formula represents an <strong>integral accumulation</strong> of physical quantities across a specific mathematical domain (boundary path, surface area, or volume space).";
            summary = "It summates local densities to calculate a global macroscopic quantity (such as total energy, mass, charge, or action).";
            scenarios = [
                {
                    condition: "Closed Loop Integration (\\( \\oint \\))",
                    implication: "Accumulates quantities along a closed path or boundary. If the result is zero, the system is conservative; if non-zero, it represents net circulation or enclosed sources."
                },
                {
                    condition: "Infinite Bounds (\\( -\\infty \\) to \\( \\infty \\))",
                    implication: "Accumulates the quantity across all space (e.g., probability normalization in quantum mechanics summing to exactly 1)."
                }
            ];
        }
        // 5. Detect Gauge Symmetries / Lie Groups (e.g. SU(3)_C x SU(2)_L x U(1)_Y)
        else if (latex.includes('SU(') || latex.includes('U(1)') || latex.includes('SO(')) {
            intro = "This formula defines the <strong>Gauge Symmetry Group</strong> governing the interactions of a field theory. Product groups of this type specify the mathematical structure of force-carrying fields and charge conservation.";
            summary = "Each factor in the symmetry group dictates a specific type of charge conservation and its corresponding gauge bosons.";
            scenarios = [];
            
            if (latex.includes('SU(3)')) {
                scenarios.push({
                    condition: "SU(3) Color Symmetry",
                    implication: "Dictates the strong nuclear force (Quantum Chromodynamics). Governs color-charged interactions mediated by 8 gluons, exhibiting confinement and asymptotic freedom."
                });
            }
            if (latex.includes('SU(2)')) {
                scenarios.push({
                    condition: "SU(2) Weak Isospin Symmetry",
                    implication: "Governs the electroweak weak isospin sector. Acts on left-handed chirality states and is mediated by 3 gauge bosons."
                });
            }
            if (latex.includes('U(1)')) {
                scenarios.push({
                    condition: "U(1) Symmetries",
                    implication: "Governs abelian phase transformations. Often represents Weak Hypercharge (U(1)_Y) in electroweak theory, or Electromagnetism (U(1)_em) mediated by a single massless boson (photon)."
                });
            }
            if (latex.includes('\\times')) {
                scenarios.push({
                    condition: "Electroweak Symmetry Breaking",
                    implication: "At low energy scales, the Higgs mechanism breaks the electroweak SU(2)_L x U(1)_Y symmetry down to electromagnetic U(1)_em, mixing gauge fields into physical W+, W-, Z bosons and the photon."
                });
            }
        } else {
            scenarios = [
                {
                    condition: "Scaling Limits (Direct Proportionality)",
                    implication: "Increasing the numerator variables results in a proportional increase in the left-hand side of the relation."
                },
                {
                    condition: "Inverse Scaling (Inverse Proportionality)",
                    implication: "Increasing the denominator variables causes the left-hand side quantity to decay."
                }
            ];
        }

        return { title, intro, summary, scenarios };
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

if (typeof window !== 'undefined') {
    window.EquationExplainer = EquationExplainer;
}

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => EquationExplainer.init());
} else {
    EquationExplainer.init();
}

