/**
 * 🌌 PHYSICS LAB: MathJax LaTeX Source & Plain-Text Inspector
 * 
 * Intercepts hovering / clicking on equations to allow students and content developers
 * to inspect and copy both the raw LaTeX source and a cleaned plain-text representation.
 */

const MathJaxInspector = {
    tooltipEl: null,
    hideTimeout: null,
    activeElement: null,

    init() {
        this.injectStyles();
        this.createTooltip();
        this.setupListeners();
    },

    injectStyles() {
        const style = document.createElement('style');
        style.id = 'mathjax-inspector-styles';
        style.textContent = `
            /* CSS Styles */
            .mathjax-inspector-tooltip {
                position: absolute;
                z-index: 10000;
                background: rgba(15, 23, 42, 0.93);
                backdrop-filter: blur(12px) saturate(180%);
                -webkit-backdrop-filter: blur(12px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 12px 14px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5), 
                            0 0 0 1px rgba(255, 255, 255, 0.05),
                            0 0 20px rgba(100, 255, 218, 0.15);
                opacity: 0;
                transform: translateY(6px) scale(0.97);
                transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1), 
                            transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                font-family: 'Space Grotesk', 'Inter', system-ui, -apple-system, sans-serif;
                color: var(--text-color, #f1f5f9);
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 360px;
                min-width: 200px;
                box-sizing: border-box;
            }
            
            .mathjax-inspector-tooltip.visible {
                opacity: 1;
                transform: translateY(0) scale(1);
                pointer-events: auto;
            }

            .mathjax-inspector-section {
                display: flex;
                flex-direction: column;
                gap: 6px;
                width: 100%;
            }
            
            .mathjax-inspector-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                font-size: 0.72rem;
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                color: var(--accent-color, #64ffda);
                border-bottom: 1px solid rgba(255, 255, 255, 0.08);
                padding-bottom: 4px;
            }
            
            .mathjax-inspector-code {
                font-family: 'Fira Code', 'Courier New', Courier, monospace;
                font-size: 0.75rem;
                background: rgba(3, 7, 18, 0.75);
                border-radius: 4px;
                padding: 6px 8px;
                border: 1px solid rgba(255, 255, 255, 0.06);
                color: var(--text-muted, #94a3b8);
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                max-width: 100%;
                direction: ltr;
            }
            
            .mathjax-inspector-btn {
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.1) 0%, rgba(0, 210, 255, 0.1) 100%);
                border: 1px solid rgba(100, 255, 218, 0.3);
                color: var(--accent-color, #64ffda);
                padding: 5px 12px;
                border-radius: 6px;
                font-size: 0.76rem;
                font-weight: 600;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                font-family: inherit;
            }
            
            .mathjax-inspector-btn:hover {
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.2) 0%, rgba(0, 210, 255, 0.2) 100%);
                border-color: rgba(100, 255, 218, 0.6);
                box-shadow: 0 0 10px rgba(100, 255, 218, 0.2);
                transform: translateY(-1px);
            }
            
            .mathjax-inspector-btn:active {
                transform: translateY(0);
            }
            
            .mathjax-inspector-btn.copied {
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(52, 211, 153, 0.15) 100%);
                border-color: rgba(16, 185, 129, 0.6);
                color: #10b981;
                box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
            }
            
            /* Equation highlighting on hover */
            svg[data-tex], mjx-container.MathJax {
                cursor: pointer;
                transition: filter 0.2s cubic-bezier(0.4, 0, 0.2, 1), outline 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            }
            
            svg[data-tex]:hover, mjx-container.MathJax:hover {
                filter: drop-shadow(0 0 6px var(--accent-color, #64ffda));
                outline: 1px dashed rgba(100, 255, 218, 0.25);
                outline-offset: 4px;
            }
        `;
        document.head.appendChild(style);
    },

    createTooltip() {
        const tooltip = document.createElement('div');
        tooltip.className = 'mathjax-inspector-tooltip';
        tooltip.innerHTML = `
            <div class="mathjax-inspector-section">
                <div class="mathjax-inspector-header">
                    <span>LaTeX Source</span>
                </div>
                <div class="mathjax-inspector-code" id="mathjax-inspector-code-val"></div>
                <button class="mathjax-inspector-btn" id="mathjax-inspector-copy-btn">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    <span class="btn-text">Copy LaTeX</span>
                </button>
            </div>
            <div class="mathjax-inspector-section" style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; margin-top: 2px;">
                <div class="mathjax-inspector-header">
                    <span>Plain Text (Search / Solver)</span>
                </div>
                <div class="mathjax-inspector-code" id="mathjax-inspector-text-val"></div>
                <button class="mathjax-inspector-btn" id="mathjax-inspector-copy-text-btn">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                    <span class="btn-text">Copy Plain Text</span>
                </button>
            </div>
            <div class="mathjax-inspector-section" style="border-top: 1px solid rgba(255,255,255,0.08); padding-top: 10px; margin-top: 2px;">
                <button class="mathjax-inspector-btn" id="mathjax-inspector-explain-btn" style="background: linear-gradient(135deg, rgba(100, 255, 218, 0.15) 0%, rgba(0, 210, 255, 0.15) 100%); border-color: rgba(100, 255, 218, 0.45);">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                        <line x1="11" y1="8" x2="11" y2="14"></line>
                        <line x1="8" y1="11" x2="14" y2="11"></line>
                    </svg>
                    <span class="btn-text">Explain Equation 🔬</span>
                </button>
            </div>
        `;
        document.body.appendChild(tooltip);
        this.tooltipEl = tooltip;

        // Prevent hiding when hovering the tooltip itself
        tooltip.addEventListener('mouseenter', () => {
            this.clearHideTimeout();
        });
        tooltip.addEventListener('mouseleave', () => {
            this.startHideTimeout();
        });

        // Setup LaTeX copy button action
        const copyBtn = tooltip.querySelector('#mathjax-inspector-copy-btn');
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.copyLatex();
        });

        // Setup Plain Text copy button action
        const copyTextBtn = tooltip.querySelector('#mathjax-inspector-copy-text-btn');
        copyTextBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.copyPlainText();
        });

        // Setup Explain button action
        const explainBtn = tooltip.querySelector('#mathjax-inspector-explain-btn');
        explainBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            if (!this.activeElement) return;
            
            const latex = this.getLatexForElement(this.activeElement);
            if (latex) {
                const container = this.activeElement.closest('[data-formula-id]');
                const formulaId = container ? container.getAttribute('data-formula-id') : null;
                
                if (window.FormulaInspector) {
                    this.hide();
                    window.FormulaInspector.open(latex, formulaId);
                } else {
                    const baseUrl = (typeof BASE_URL !== 'undefined') ? BASE_URL : '';
                    let url = baseUrl + '/physics/equation-explainer?latex=' + encodeURIComponent(latex);
                    if (formulaId) {
                        url += '&id=' + encodeURIComponent(formulaId);
                    }
                    window.location.href = url;
                }
            }
        });
    },

    setupListeners() {
        const findEquationContainer = (target) => {
            return target.closest('svg[data-tex], [data-tex], .MathJax, mjx-container, .math-content, .formula-math-display, .explainer-link-btn, a[href*="equation-explainer"]');
        };

        // Intercept equation clicks globally to open FormulaInspector drawer
        document.addEventListener('click', (e) => {
            const container = findEquationContainer(e.target);
            if (container) {
                const latex = this.getLatexForElement(container);
                if (latex) {
                    e.preventDefault();
                    e.stopPropagation();

                    const formulaContainer = container.closest('[data-formula-id]');
                    let formulaId = formulaContainer ? formulaContainer.getAttribute('data-formula-id') : null;

                    if (!formulaId && container.href) {
                        try {
                            const u = new URL(container.href, window.location.origin);
                            formulaId = u.searchParams.get('id');
                        } catch (err) {}
                    }
                    
                    const baseUrl = (typeof BASE_URL !== 'undefined') ? BASE_URL : '';
                    let url = baseUrl + '/physics/equation-explainer?latex=' + encodeURIComponent(latex);
                    if (formulaId) {
                        url += '&id=' + encodeURIComponent(formulaId);
                    }
                    window.location.href = url;
                }
            }
        }, true);
    },

    getLatexForElement(el) {
        if (!el) return null;

        // 0. Check link URL query parameters (for explainer links)
        const linkEl = el.closest('a[href*="equation-explainer"]');
        if (linkEl && linkEl.href) {
            try {
                const u = new URL(linkEl.href, window.location.origin);
                let l = u.searchParams.get('latex');
                if (l) {
                    l = l.replace(/^['"\s]+|['"\s]+$/g, '');
                    const quoteIdx = l.indexOf("'");
                    if (quoteIdx > 0 && /'\s*(?:\\text|\\mathrm|\\mathbf|[a-zA-Z]{2,})/.test(l.slice(quoteIdx))) {
                        l = l.substring(0, quoteIdx).trim();
                    }
                    return l;
                }
            } catch (err) {}
        }

        // 1. Direct or ancestor data-tex or data-latex attribute
        const texEl = el.closest('svg[data-tex], [data-tex], [data-latex]');
        if (texEl) {
            const attr = texEl.getAttribute('data-tex') || texEl.getAttribute('data-latex');
            if (attr) return attr;
        }

        // 2. MathJax 3 CHTML container check
        const mathJaxContainer = el.closest('.MathJax, mjx-container, .math-content, .formula-math-display');
        if (mathJaxContainer && window.MathJax && window.MathJax.startup && window.MathJax.startup.document && window.MathJax.startup.document.math) {
            try {
                for (const mathItem of window.MathJax.startup.document.math) {
                    if (mathItem && mathItem.typesetRoot && (
                        mathItem.typesetRoot === mathJaxContainer ||
                        mathItem.typesetRoot.contains(mathJaxContainer) ||
                        mathJaxContainer.contains(mathItem.typesetRoot)
                    )) {
                        return mathItem.math;
                    }
                }
            } catch (err) {
                console.warn("Error finding MathJax 3 MathItem:", err);
            }
        }

        // 3. Inner SVG check inside math container
        const innerSvg = mathJaxContainer?.querySelector('svg[data-tex], [data-tex]');
        if (innerSvg && innerSvg.getAttribute('data-tex')) {
            return innerSvg.getAttribute('data-tex');
        }

        // 4. Fallback check for MathML annotation
        const mmlAnnotation = mathJaxContainer?.querySelector('annotation[encoding="application/x-tex"]');
        if (mmlAnnotation) {
            return mmlAnnotation.textContent.trim();
        }

        // 5. Fallback text content extraction
        if (mathJaxContainer) {
            const text = mathJaxContainer.textContent.trim();
            const clean = text.replace(/^\\\[/, '').replace(/\\\]$/, '').replace(/^\$\$/, '').replace(/\$\$$/, '').replace(/^\$/, '').replace(/\$/, '').trim();
            if (clean.length > 0) {
                return clean;
            }
        }

        return null;
    },

    /**
     * Translates LaTeX formulas into standard mathematical programming/ASCIImath style
     * for seamless compatibility with internal Search & Solver features.
     */
    latexToPlainText(latex) {
        if (!latex) return '';
        
        let text = latex.trim();

        // 1. Strip delimiters if present (e.g. \( ... \) or $$ ... $$)
        text = text.replace(/^\\\(/, '').replace(/\\\)$/, '');
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

    show(container) {
        this.clearHideTimeout();

        if (this.activeElement === container && this.tooltipEl.classList.contains('visible')) {
            return;
        }

        const latex = this.getLatexForElement(container);
        if (!latex) {
            this.hide();
            return;
        }

        const plainText = this.latexToPlainText(latex);
        this.activeElement = container;

        // Populate values
        const codeVal = this.tooltipEl.querySelector('#mathjax-inspector-code-val');
        codeVal.textContent = latex;
        codeVal.title = latex;

        const textVal = this.tooltipEl.querySelector('#mathjax-inspector-text-val');
        textVal.textContent = plainText;
        textVal.title = plainText;

        // Reset button states
        const copyBtn = this.tooltipEl.querySelector('#mathjax-inspector-copy-btn');
        copyBtn.className = 'mathjax-inspector-btn';
        copyBtn.querySelector('.btn-text').textContent = 'Copy LaTeX';
        copyBtn.querySelector('.copy-icon').innerHTML = `
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        `;

        const copyTextBtn = this.tooltipEl.querySelector('#mathjax-inspector-copy-text-btn');
        copyTextBtn.className = 'mathjax-inspector-btn';
        copyTextBtn.querySelector('.btn-text').textContent = 'Copy Plain Text';
        copyTextBtn.querySelector('.copy-icon').innerHTML = `
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        `;

        // Get category accent color
        let accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
        if (!accentColor) accentColor = '#64ffda';

        // Position tooltip
        const rect = container.getBoundingClientRect();
        const tooltipRect = this.tooltipEl.getBoundingClientRect();

        const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
        const scrollY = window.pageYOffset || document.documentElement.scrollTop;

        let top = rect.top + scrollY - tooltipRect.height - 12;
        let left = rect.left + scrollX + (rect.width - tooltipRect.width) / 2;

        if (rect.top - tooltipRect.height - 12 < 10) {
            top = rect.bottom + scrollY + 12;
        }

        const padding = 10;
        const viewportWidth = document.documentElement.clientWidth;
        if (left < padding) {
            left = padding;
        } else if (left + tooltipRect.width > viewportWidth - padding) {
            left = viewportWidth - tooltipRect.width - padding;
        }

        this.tooltipEl.style.top = `${top}px`;
        this.tooltipEl.style.left = `${left}px`;
        this.tooltipEl.style.setProperty('--accent-color', accentColor);
        this.tooltipEl.classList.add('visible');
    },

    hide() {
        this.tooltipEl.classList.remove('visible');
        this.activeElement = null;
    },

    startHideTimeout() {
        this.clearHideTimeout();
        this.hideTimeout = setTimeout(() => {
            this.hide();
        }, 350);
    },

    clearHideTimeout() {
        if (this.hideTimeout) {
            clearTimeout(this.hideTimeout);
            this.hideTimeout = null;
        }
    },

    copyToClipboard(text, btnId) {
        const performCopy = () => {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                return navigator.clipboard.writeText(text);
            }
            
            return new Promise((resolve, reject) => {
                try {
                    const textArea = document.createElement("textarea");
                    textArea.value = text;
                    textArea.style.top = "0";
                    textArea.style.left = "0";
                    textArea.style.position = "fixed";
                    textArea.style.opacity = "0";
                    document.body.appendChild(textArea);
                    textArea.focus();
                    textArea.select();
                    const successful = document.execCommand('copy');
                    document.body.removeChild(textArea);
                    if (successful) resolve();
                    else reject(new Error("Fallback copy failed"));
                } catch (err) {
                    reject(err);
                }
            });
        };

        performCopy().then(() => {
            const copyBtn = this.tooltipEl.querySelector(btnId);
            copyBtn.classList.add('copied');
            const btnText = copyBtn.querySelector('.btn-text');
            btnText.textContent = 'Copied!';

            const copyIcon = copyBtn.querySelector('.copy-icon');
            copyIcon.innerHTML = `<polyline points="20 6 9 17 4 12"></polyline>`;

            copyBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                copyBtn.style.transform = '';
            }, 100);

            setTimeout(() => {
                if (this.activeElement) {
                    this.hide();
                }
            }, 1000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    },

    copyLatex() {
        if (!this.activeElement) return;
        const latex = this.getLatexForElement(this.activeElement);
        if (!latex) return;
        this.copyToClipboard(latex, '#mathjax-inspector-copy-btn');
    },

    copyPlainText() {
        if (!this.activeElement) return;
        const latex = this.getLatexForElement(this.activeElement);
        if (!latex) return;
        const plainText = this.latexToPlainText(latex);
        this.copyToClipboard(plainText, '#mathjax-inspector-copy-text-btn');
    }
};

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MathJaxInspector.init());
} else {
    MathJaxInspector.init();
}
