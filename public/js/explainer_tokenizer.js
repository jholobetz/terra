/**
 * 🔬 PHYSICS LAB: Equation Explainer Tokenizer & AST Heuristics
 *
 * Extracted from equation_explainer.js to isolate pure LaTeX tokenization,
 * semantic clustering, domain detection, and AST heuristic synthesis from DOM controllers.
 */

const ExplainerTokenizer = {
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
        const constants = (typeof window !== 'undefined' && window.PHYSICS_CONSTANTS) || {};
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
        const varDict = this.variableDictionary || {};
        const dictEntry = varDict[cleanSymbol] || varDict[symbol];
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
        const physDict = this.physicsDictionary || {};
        const legacyEntry = physDict[cleanSymbol] || physDict[symbol];
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
        
        // Mathematical Logic & Philosophy of Physics notation
        if (/\\(forall|exists|nexists|vdash|dashv|models|vDash|Vdash|nVdash|nvdash|iff|implies|impliedby|subset|subseteq|supset|supseteq|cap|cup|in|notin|ni|setminus|emptyset|varnothing)\b/.test(latex)) {
            return 'philosophy_of_physics';
        }

        // Thermodynamic differentials: dU, dS, dV, dH, dG, dQ
        if (/\b(dU|dS|dV|dH|dG|dQ|dW)\b/.test(latex)) {
            return 'thermodynamics';
        }
        
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

    extractAllMathTokens(latex, officialVariables = {}) {
        if (!latex) return [];

        let hasHtmlMacros = true;
        while (hasHtmlMacros) {
            const nextLatex = latex.replace(/\\(class|cssId|style|href)\{[^{}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextLatex === latex) {
                hasHtmlMacros = false;
            } else {
                latex = nextLatex;
            }
        }
        latex = latex.replace(/\\(class|cssId|style|href)\b/g, ' ').trim();
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
        const modGlossary = this.modifierGlossary || {};
        const physDict = this.physicsDictionary || {};

        const addToken = (symbol, type) => {
            if (!symbol || seen.has(symbol)) return;
            seen.add(symbol);
            found.push({ symbol, type });
        };

        const pureSyntaxDelimiters = [
            '\\rangle', '\\langle', '\\mid', '|', '(', ')', '[', ']', '{', '}', '+', '-', '=', '/', 
            '\\cdot', '\\times', '\\div', '\\left', '\\right', '\\text', '\\mathrm', '\\mathsf',
            '\\colon', '\\quad', '\\qquad', '\\dots', '\\cdots', '\\ldots', '\\ddots', '\\vdots',
            '\\circ', '\\bullet', '\\class', '\\cssId', '\\style', '\\href', '\\color'
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
            if ((/^[a-zA-Z]{2,}$/.test(content) || modGlossary[content]) && !consumedSubtokens.has(content)) {
                addToken(content, 'modifier');
            }
        }

        // Extract superscripts as modifiers from original raw latex
        const superscriptModRegex = /\^\{([^\}]+)\}|\^([a-zA-Z0-9+\-\*\\/]+|\*|\+|0|\-|\\dagger|\\circ|\\prime)/g;
        let superModMatch;
        while ((superModMatch = superscriptModRegex.exec(latex)) !== null) {
            let content = superModMatch[1] || superModMatch[2];
            content = content.trim();
            const isStandardModifier = modGlossary[content] || 
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

        const constantSubscriptRegex = /\\(epsilon|mu|k|a|m|g|G|N)_(?:0|\{0\}|B|\{B\}|e|\{e\}|p|\{p\}|n|\{n\}|F|\{F\}|A|\{A\})(?![a-zA-Z])/g;
        let constMatch;
        while ((constMatch = constantSubscriptRegex.exec(text)) !== null) {
            const fullMatch = constMatch[0];
            const normalizedSymbol = fullMatch.replace(/_\{([^\}]+)\}/, '_$1');
            addToken(normalizedSymbol, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        const integralBoundaryRegex = /\\(int|oint|iint|iiint)_\{?([a-zA-Z0-9]+)\}?/g;
        let boundaryMatch;
        while ((boundaryMatch = integralBoundaryRegex.exec(text)) !== null) {
            const boundaryVar = boundaryMatch[2];
            if (boundaryVar && /^[a-zA-Z]$/.test(boundaryVar)) {
                addToken(boundaryVar, 'integration_boundary');
            }
        }

        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, ' ').replace(/\\end\{[a-zA-Z]+\}/g, ' ');

        if (officialVariables) {
            const sortedOfficialKeys = Object.keys(officialVariables).sort((a, b) => b.length - a.length);
            for (const sym of sortedOfficialKeys) {
                if (this.latexContainsSymbol(text, sym)) {
                    const isOperator = physDict[sym] && physDict[sym].type === 'operator';
                    addToken(sym, isOperator ? 'operator' : 'variable');
                    
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

        text = text.replace(/_\{([^\}]+)\}/g, (match, content) => {
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

            const greekPattern = /\\[a-zA-Z]+/g;
            const greekMatches = cleanContent.match(greekPattern) || [];

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

        const mathcalRegex = /\\mathcal\{([a-zA-Z])\}/g;
        let mathcalMatch;
        while ((mathcalMatch = mathcalRegex.exec(text)) !== null) {
            const fullMatch = mathcalMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

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

        const differentialRegex = /\bd(?:\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([a-zA-Z])\}|([a-zA-Z]))\b/g;
        let diffMatch;
        while ((diffMatch = differentialRegex.exec(text)) !== null) {
            const fullMatch = diffMatch[0];
            const baseVar = diffMatch[2] || diffMatch[3];
            
            addToken('d', 'differential_operator');
            
            if (baseVar) {
                addToken(baseVar, 'variable');
            }
            
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        const dotRegex = /\\(dot|ddot)\{([a-zA-Z\\]+)\}|\\(dot|ddot)\s*([a-zA-Z])/g;
        let dotMatch;
        while ((dotMatch = dotRegex.exec(text)) !== null) {
            const fullMatch = dotMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

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

        const constants = (typeof window !== 'undefined' && window.PHYSICS_CONSTANTS) || {};
        for (const [key, details] of Object.entries(constants)) {
            const sym = details.symbol;
            if (this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'constant');
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

        text = text.replace(/[\{\}:;,]/g, ' ');

        text = text.replace(/(\\[a-zA-Z]+)|([a-zA-Z]+)/g, (match, latexCmd, plainWord) => {
            if (latexCmd) {
                return latexCmd;
            }
            if (plainWord && plainWord.length > 1) {
                return plainWord.split('').join(' ');
            }
            return plainWord;
        });

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

        const greekPattern = /\\[a-zA-Z]+/g;
        let match;
        while ((match = greekPattern.exec(text)) !== null) {
            const sym = match[0];
            const ignoredCmds = new Set([
                '\\frac', '\\left', '\\right', '\\cdot', '\\times', '\\div', 
                '\\colon', '\\quad', '\\qquad', '\\dots', '\\cdots', '\\ldots', '\\ddots', '\\vdots',
                '\\circ', '\\bullet', '\\ast', '\\star',
                '\\boldsymbol', '\\mathbf', '\\mathsf', '\\mathrm', '\\text', '\\mathcal', 
                '\\vec', '\\hat', '\\bar', '\\tilde', '\\dot', '\\ddot', '\\underline',
                '\\class', '\\cssId', '\\style', '\\href', '\\color'
            ]);
            if (ignoredCmds.has(sym) || consumedSubtokens.has(sym) || consumedSubtokens.has(sym.replace(/^\\/, ''))) continue;
            
            const isOperator = physDict[sym] && physDict[sym].type === 'operator';
            addToken(sym, isOperator ? 'operator' : 'variable');
        }

        text = text.replace(/\\[a-zA-Z]+/g, ' ');
        const romanPattern = /[a-zA-Z]/g;
        while ((match = romanPattern.exec(text)) !== null) {
            const sym = match[0];
            if (!consumedSubtokens.has(sym) && this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'variable');
            }
        }

        const getCleanSearchString = (str) => {
            let clean = str;
            clean = clean.replace(/\\(text|mathrm|mathsf)\{([^\}]+)\}/g, match => ' '.repeat(match.length));
            const structuralRegex = /\\(frac|left|right|sqrt|cdot|times|div|iff|implies|impliedby|forall|exists|nexists|in|notin|ni|subset|subseteq|supset|supseteq|cap|cup|setminus|emptyset|vdash|dashv|models|vDash|Vdash|nVdash|nvdash|Rightarrow|Leftarrow|Leftrightarrow|rightarrow|leftarrow|leftrightarrow|to|mapsto|land|lor|neg|lnot|top|bot|approx|equiv|sim|simeq|cong|propto|asymp|doteq|ge|le|geq|leq|ne|neq|ll|gg|pm|mp|colon|quad|qquad|dots|cdots|ldots|circ|bullet|ast|star|boldsymbol|mathbf|mathsf|mathrm|text|mathcal|vec|hat|bar|tilde|dot|ddot|underline|class|cssId|style|href|color)\b/g;
            clean = clean.replace(structuralRegex, match => ' '.repeat(match.length));
            clean = clean.replace(/_\{[a-zA-Z]{3,\}\}/g, match => ' '.repeat(match.length));
            clean = clean.replace(/_[a-zA-Z]{3,}/g, match => ' '.repeat(match.length));
            return clean;
        };

        const cleanStylesForSorting = (str) => {
            let res = str;
            let hasStyles = true;
            while (hasStyles) {
                const next = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline|class|cssId|style|href)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
                if (next === res) {
                    hasStyles = false;
                } else {
                    res = next;
                }
            }
            res = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline|class|cssId|style|href)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');
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

    tokenizeLatexSymbols(latex) {
        return [];
    },

    latexContainsSymbol(latex, sym) {
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

    latexToPlainText(latex) {
        if (!latex) return '';
        
        let text = latex.trim().replace(/\\par\b/g, ' ');

        text = text.replace(/^\\\(/, '').replace(/\\\)$/, '');
        text = text.replace(/^\\\[/, '').replace(/\\\]$/, '');
        text = text.replace(/^\$\$/, '').replace(/\$\$$/, '');
        text = text.replace(/^\$/, '').replace(/\$/, '');

        text = text.replace(/\\frac\{d\}\{d([a-zA-Z])\}/g, 'd/d$1');
        text = text.replace(/\\frac\{\\partial\}\{\\partial\s*([a-zA-Z])\}/g, 'partial/partial $1');
        
        let hasFraction = true;
        while (hasFraction) {
            const nextText = text.replace(/\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g, '($1)/($2)');
            if (nextText === text) {
                hasFraction = false;
            } else {
                text = nextText;
            }
        }

        let hasStyles = true;
        while (hasStyles) {
            const nextText = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextText === text) {
                hasStyles = false;
            } else {
                text = nextText;
            }
        }
        
        text = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s+([a-zA-Z0-9])/g, '$2');

        text = text.replace(/_\{([^}]+)\}/g, '_$1');
        text = text.replace(/\^\{([^}]+)\}/g, '^$1');

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

        text = text.replace(/\\cdot/g, ' * ');
        text = text.replace(/\\times/g, ' * ');
        text = text.replace(/\\ast/g, ' * ');
        text = text.replace(/\\star/g, ' * ');
        text = text.replace(/\\div/g, ' / ');

        text = text.replace(/\\left\(/g, '(').replace(/\\right\)/g, ')');
        text = text.replace(/\\left\[/g, '[').replace(/\\right\]/g, ']');
        text = text.replace(/\\left\\\{/g, '{').replace(/\\right\\\}/g, '}');

        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, '[').replace(/\\end\{[a-zA-Z]+\}/g, ']');
        text = text.replace(/&/g, ', ').replace(/\\\\/g, ', ');

        text = text.replace(/\\([a-zA-Z]+)/g, '$1');
        text = text.replace(/\s+/g, ' ');
        text = text.replace(/\*\s*\*/g, '*');
        text = text.trim();

        return text;
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

        tempText = tempText.replace(/\\\[[\s\S]*?\\\]/g, protect);
        tempText = tempText.replace(/\\\([\s\S]*?\\\)/g, protect);
        tempText = tempText.replace(/\$\$[\s\S]*?\$\$/g, protect);
        tempText = tempText.replace(/\$([^\$\n]+?)\$/g, protect);

        tempText = tempText.replace(/([A-Za-z\u0370-\u03FF]+)\s*=\s*(\\[a-zA-Z]+(?:\{[^{}]*\}|\([^)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^\/\*\+\-])+)/g, (match, lhs, rhs) => {
            if (match.includes('\uE000')) return match;
            let cleanLhs = lhs.trim();
            if (greekMap[cleanLhs]) cleanLhs = greekMap[cleanLhs];
            return protect(`\\(${cleanLhs} = ${rhs.trim()}\\)`);
        });

        tempText = tempText.replace(/(\([a-zA-Z0-9_\^ ]+\)|[A-Za-z\u0370-\u03FF]+)\s+approaches\s+(zero|infinity|0|\\infty)/gi, (match, sym, target) => {
            if (match.includes('\uE000')) return match;
            let cleanSym = sym.replace(/^\(|\)$/g, '').trim();
            if (greekMap[cleanSym]) cleanSym = greekMap[cleanSym];
            const texTarget = (target.toLowerCase() === 'infinity') ? '\\infty' : '0';
            return protect(`\\(${cleanSym} \\to ${texTarget}\\)`);
        });

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

        tempText = tempText.replace(/([ΓαβγδεθλμνπρστφψωΩΔ])/g, (match) => {
            if (match.includes('\uE000')) return match;
            const tex = greekMap[match] || match;
            return protect(`\\(${tex}\\)`);
        });

        tempText = tempText.replace(/\b([A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+)(?:\s*[-+><=]\s*[A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+))*(?:\s+[A-Za-z](?:_[a-zA-Z0-9]+|\^[a-zA-Z0-9]+))?)\b/g, (match) => {
            if (match.includes('\uE000')) return match;
            if (/^[a-zA-Z]{3,}$/.test(match)) return match;
            return protect(`\\(${match}\\)`);
        });

        tempText = tempText.replace(/\\(?:frac|sqrt)\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})*|(?:[a-zA-Z]*\\(?:hat|vec|mathbf|mathrm|text|tilde|bar)\{[^}]+\}[a-zA-Z0-9_\^']*(?:\([^)]+\))?|[a-zA-Z]+\(\\[a-zA-Z]+\{[^}]+\}[^)]*\)|\|(?:\\[a-zA-Z]+\{[^}]+\}|[a-zA-Z0-9_\^'\s\-\+\\to\format])+\|)/g, match => {
            if (match.includes('\uE000')) return match;
            return protect(`\\(${match.trim()}\\)`);
        });

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

        tempText = tempText.replace(/(?:^|\n)\s*[\*\-]\s+(.+)/g, (m, line) => '\n<div style="margin: 4px 0 4px 12px;">• ' + line + '</div>');
        tempText = tempText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        tempText = tempText.replace(/(?<!\*)\*(\S[^*]*?\S|\S)\*(?!\*)/g, '<em>$1</em>');
        tempText = tempText.replace(/(?:\r?\n)+(?=\d+\.\s+)/g, '<br><br>');
        tempText = tempText.replace(/\r?\n/g, '<br>');

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
    }
};

if (typeof window !== 'undefined') {
    window.ExplainerTokenizer = ExplainerTokenizer;
    if (window.EquationExplainer) {
        Object.assign(window.EquationExplainer, ExplainerTokenizer);
    }
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExplainerTokenizer;
}
