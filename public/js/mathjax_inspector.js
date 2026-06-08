/**
 * 🌌 PHYSICS LAB: MathJax LaTeX Source Inspector
 * 
 * Intercepts hovering / clicking on equations to allow students and content developers
 * to inspect and copy the raw LaTeX source.
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
                background: rgba(15, 23, 42, 0.9);
                backdrop-filter: blur(12px) saturate(180%);
                -webkit-backdrop-filter: blur(12px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 8px;
                padding: 10px 14px;
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
                gap: 8px;
                max-width: 340px;
                min-width: 180px;
                box-sizing: border-box;
            }
            
            .mathjax-inspector-tooltip.visible {
                opacity: 1;
                transform: translateY(0) scale(1);
                pointer-events: auto;
            }
            
            .mathjax-inspector-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 12px;
                font-size: 0.75rem;
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
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.12) 0%, rgba(0, 210, 255, 0.12) 100%);
                border: 1px solid rgba(100, 255, 218, 0.35);
                color: var(--accent-color, #64ffda);
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 0.8rem;
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
                background: linear-gradient(135deg, rgba(100, 255, 218, 0.22) 0%, rgba(0, 210, 255, 0.22) 100%);
                border-color: rgba(100, 255, 218, 0.7);
                box-shadow: 0 0 12px rgba(100, 255, 218, 0.3);
                transform: translateY(-1px);
            }
            
            .mathjax-inspector-btn:active {
                transform: translateY(0);
            }
            
            .mathjax-inspector-btn.copied {
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(52, 211, 153, 0.2) 100%);
                border-color: rgba(16, 185, 129, 0.7);
                color: #10b981;
                box-shadow: 0 0 12px rgba(16, 185, 129, 0.3);
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

        // Setup copy button action
        const copyBtn = tooltip.querySelector('#mathjax-inspector-copy-btn');
        copyBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.copyLatex();
        });
    },

    setupListeners() {
        const findEquationContainer = (target) => {
            return target.closest('svg[data-tex], .MathJax, mjx-container');
        };

        // Event delegation on mouseover
        document.body.addEventListener('mouseover', (e) => {
            const container = findEquationContainer(e.target);
            if (container) {
                // If moving from inside the same container, ignore
                if (e.relatedTarget && container.contains(e.relatedTarget)) {
                    return;
                }
                this.show(container);
            }
        });

        // Event delegation on mouseout
        document.body.addEventListener('mouseout', (e) => {
            const container = findEquationContainer(e.target);
            if (container) {
                // If moving to another element inside the same container, ignore
                if (e.relatedTarget && container.contains(e.relatedTarget)) {
                    return;
                }
                this.startHideTimeout();
            }
        });

        // Mobile / click support
        document.body.addEventListener('click', (e) => {
            const container = findEquationContainer(e.target);
            if (container) {
                e.preventDefault();
                e.stopPropagation();

                if (this.activeElement === container && this.tooltipEl.classList.contains('visible')) {
                    // Click on the active equation copies immediately
                    this.copyLatex();
                } else {
                    this.show(container);
                }
            } else if (!this.tooltipEl.contains(e.target)) {
                this.hide();
            }
        });
    },

    getLatexForElement(el) {
        // 1. Direct or ancestor data-tex attribute (covers pre-rendered SVGs)
        const svgEl = el.closest('svg[data-tex], [data-tex]');
        if (svgEl && svgEl.getAttribute('data-tex')) {
            return svgEl.getAttribute('data-tex');
        }

        // 2. MathJax 3 CHTML container check
        const mathJaxContainer = el.closest('.MathJax, mjx-container, .math-content');
        if (mathJaxContainer && window.MathJax && window.MathJax.startup && window.MathJax.startup.document && window.MathJax.startup.document.math) {
            try {
                // MathJax math list is an iterable, not a standard Array. Iterate via for...of.
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

        // 3. Fallback check for any sub-tags or attributes or assistive MathML
        const mmlAnnotation = el.closest('.MathJax, mjx-container')?.querySelector('annotation[encoding="application/x-tex"]');
        if (mmlAnnotation) {
            return mmlAnnotation.textContent.trim();
        }

        return null;
    },

    show(container) {
        this.clearHideTimeout();

        // Avoid layout thrashing if we are already showing the tooltip for this equation
        if (this.activeElement === container && this.tooltipEl.classList.contains('visible')) {
            return;
        }

        const latex = this.getLatexForElement(container);
        if (!latex) {
            this.hide();
            return;
        }

        this.activeElement = container;

        // Populate values
        const codeVal = this.tooltipEl.querySelector('#mathjax-inspector-code-val');
        codeVal.textContent = latex;
        codeVal.title = latex; // Show full on hover

        // Reset copy button state
        const copyBtn = this.tooltipEl.querySelector('#mathjax-inspector-copy-btn');
        copyBtn.className = 'mathjax-inspector-btn';
        const btnText = copyBtn.querySelector('.btn-text');
        btnText.textContent = 'Copy LaTeX';
        const copyIcon = copyBtn.querySelector('.copy-icon');
        copyIcon.innerHTML = `
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        `;

        // Get active category accent color if available
        let accentColor = getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim();
        if (!accentColor) accentColor = '#64ffda';

        // Position tooltip
        const rect = container.getBoundingClientRect();
        const tooltipRect = this.tooltipEl.getBoundingClientRect();

        // Calculate page coordinates
        const scrollX = window.pageXOffset || document.documentElement.scrollLeft;
        const scrollY = window.pageYOffset || document.documentElement.scrollTop;

        let top = rect.top + scrollY - tooltipRect.height - 12; // 12px gap above
        let left = rect.left + scrollX + (rect.width - tooltipRect.width) / 2;

        // Boundary check: if overflows top of screen, show below
        if (rect.top - tooltipRect.height - 12 < 10) {
            top = rect.bottom + scrollY + 12; // 12px gap below
        }

        // Boundary check: left and right edges
        const padding = 10;
        const viewportWidth = document.documentElement.clientWidth;
        if (left < padding) {
            left = padding;
        } else if (left + tooltipRect.width > viewportWidth - padding) {
            left = viewportWidth - tooltipRect.width - padding;
        }

        this.tooltipEl.style.top = `${top}px`;
        this.tooltipEl.style.left = `${left}px`;

        // Apply theme color
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

    copyLatex() {
        if (!this.activeElement) return;

        const latex = this.getLatexForElement(this.activeElement);
        if (!latex) return;

        const performCopy = () => {
            if (navigator.clipboard && navigator.clipboard.writeText) {
                return navigator.clipboard.writeText(latex);
            }
            
            // Fallback copy for non-secure HTTP contexts
            return new Promise((resolve, reject) => {
                try {
                    const textArea = document.createElement("textarea");
                    textArea.value = latex;
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
            // Visual confirmation
            const copyBtn = this.tooltipEl.querySelector('#mathjax-inspector-copy-btn');
            copyBtn.classList.add('copied');
            const btnText = copyBtn.querySelector('.btn-text');
            btnText.textContent = 'Copied!';

            // Checkmark SVG icon
            const copyIcon = copyBtn.querySelector('.copy-icon');
            copyIcon.innerHTML = `
                <polyline points="20 6 9 17 4 12"></polyline>
            `;

            // Subtle pulse
            copyBtn.style.transform = 'scale(0.95)';
            setTimeout(() => {
                copyBtn.style.transform = '';
            }, 100);

            // Hide after a brief delay
            setTimeout(() => {
                if (this.activeElement) {
                    this.hide();
                }
            }, 1000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    }
};

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => MathJaxInspector.init());
} else {
    MathJaxInspector.init();
}
