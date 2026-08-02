/**
 * hub_interactions.js - Client-side interactivity for Platinum Standard Hubs
 */
document.addEventListener('DOMContentLoaded', function() {
    // 1. Formula Expansion Logic
    const list = document.getElementById('equations-list');
    if (list) {
        list.addEventListener('click', function(event) {
            const trigger = event.target.closest('.formula-expand-trigger');
            if (!trigger) return;
            const card = trigger.closest('.platinum-formula-card');
            const body = card.querySelector('.formula-body');
            const icon = trigger.querySelector('.expand-icon');
            if (body) {
                const isHidden = window.getComputedStyle(body).display === 'none';
                if (isHidden) {
                    body.style.display = 'block';
                    card.style.borderColor = 'var(--accent-color)';
                    icon.innerText = '[ Click to Collapse ]';
                    if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) MathJax.typesetPromise([body]);
                } else {
                    body.style.display = 'none';
                    card.style.borderColor = '#233554';
                    icon.innerText = '[ Click to Expand Depth ]';
                }
            }
        });
    }

    // 2. Global MathJax Fallback Trigger (for complex layouts)
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise();
    }

    // 3. Helper: Parse LaTeX Variable Symbols to Candidate MathJax Hex Suffixes
    function getCandidateHexCodes(symbol) {
        if (!symbol) return [];
        // Split by subscript/superscript/function boundaries
        let base = symbol.split(/[_^({]/)[0].trim();
        
        // Recursively unwrap LaTeX wrappers like \mathbf{...}, \mathcal{...}, \hat{...}, \bar{...}, etc.
        let changed = true;
        while (changed) {
            let prev = base;
            base = base.replace(/\\(mathbf|mathcal|hat|bar|vec|boldsymbol|dot|tilde|mathrm|text)\{([a-zA-Z0-9\\]+)\}/g, '$2');
            base = base.replace(/\\(hat|bar|vec|dot|tilde|mathbf|mathcal|boldsymbol|mathrm|text)\s+([a-zA-Z0-9\\])/g, '$2');
            if (base === prev) changed = false;
        }
        
        base = base.trim();
        let candidates = new Set();
        
        const greekLower = {
            'alpha': ['1D6FC', '03B1'],
            'beta': ['1D6FD', '03B2'],
            'gamma': ['1D6FE', '03B3'],
            'delta': ['1D6FF', '03B4'],
            'epsilon': ['1D700', '03B5', '1D71B'],
            'zeta': ['1D701', '03B6'],
            'eta': ['1D702', '03B7'],
            'theta': ['1D703', '03B8', '1D71F'],
            'iota': ['1D704', '03B9'],
            'kappa': ['1D705', '03BA'],
            'lambda': ['1D706', '03BB'],
            'mu': ['1D707', '03BC'],
            'nu': ['1D708', '03BD'],
            'xi': ['1D709', '03BE'],
            'pi': ['1D70B', '03C0'],
            'rho': ['1D70C', '03C1', '1D71A'],
            'sigma': ['1D70E', '03C3'],
            'tau': ['1D70F', '03C4'],
            'upsilon': ['1D710', '03C5'],
            'phi': ['1D711', '03C6', '1D71D'],
            'chi': ['1D712', '03C7'],
            'psi': ['1D713', '03C8'],
            'omega': ['1D714', '03C9']
        };
        
        const greekUpper = {
            'Gamma': ['1D6E2', '0393'],
            'Delta': ['1D6E4', '0394'],
            'Theta': ['1D6E9', '0398'],
            'Lambda': ['1D6EC', '039B'],
            'Xi': ['1D6EF', '039E'],
            'Pi': ['1D6F1', '03A0'],
            'Sigma': ['1D6F4', '03A3'],
            'Upsilon': ['1D6F7', '03A5'],
            'Phi': ['1D6F8', '03A6'],
            'Psi': ['1D6F9', '03A8'],
            'Omega': ['1D6FA', '03A9']
        };
        
        const specialSymbols = {
            'hbar': ['210F'],
            'partial': ['2202'],
            'nabla': ['2207'],
            'oint': ['222E'],
            'int': ['222B'],
            'Box': ['25A1', '2610'],
            'square': ['25A1'],
            'lozenge': ['25CA']
        };

        const mathcalUpper = {
            'A': '1D49C', 'B': '212C', 'C': '1D49E', 'D': '1D49F',
            'E': '2130', 'F': '2131', 'G': '1D4A2', 'H': '210B',
            'I': '2110', 'J': '1D4A5', 'K': '1D4A6', 'L': '2112',
            'M': '2133', 'N': '1D4A9', 'O': '1D4AA', 'P': '1D4AB',
            'Q': '2118', 'R': '211B', 'S': '1D4AE', 'T': '1D4AF',
            'U': '1D4B0', 'V': '1D4B1', 'W': '1D4B2', 'X': '1D4B3',
            'Y': '1D4B4', 'Z': '2128'
        };

        if (base.startsWith('\\')) {
            let name = base.substring(1);
            if (greekLower[name]) {
                greekLower[name].forEach(c => candidates.add(c));
            } else if (greekUpper[name]) {
                greekUpper[name].forEach(c => candidates.add(c));
            } else if (specialSymbols[name]) {
                specialSymbols[name].forEach(c => candidates.add(c));
            }
        } else if (base.length === 1) {
            let char = base;
            let code = char.charCodeAt(0);
            
            // Add direct ASCII code in hex
            candidates.add(code.toString(16).toUpperCase());
            
            // Lowercase standard math letters mapping
            if (code >= 97 && code <= 122) {
                if (char === 'h') {
                    candidates.add('210E'); // Planck constant h
                } else {
                    candidates.add((code + 0x1D3ED).toString(16).toUpperCase());
                }
                candidates.add((code + 0x1D3B9).toString(16).toUpperCase());
                candidates.add((code + 0x1D421).toString(16).toUpperCase());
            }
            // Uppercase standard math letters mapping
            else if (code >= 65 && code <= 90) {
                candidates.add((code + 0x1D3F3).toString(16).toUpperCase());
                candidates.add((code + 0x1D3BF).toString(16).toUpperCase());
                candidates.add((code + 0x1D457).toString(16).toUpperCase());
                if (mathcalUpper[char]) {
                    candidates.add(mathcalUpper[char]);
                }
            }
        }
        
        // Match specific \mathcal if requested
        if (symbol.includes('\\mathcal{')) {
            let m = symbol.match(/\\mathcal\{([A-Z])\}/);
            if (m && mathcalUpper[m[1]]) {
                candidates.add(mathcalUpper[m[1]]);
            }
        }
        
        return Array.from(candidates);
    }

    // 4. Semantic Variable Hover Synchronization Event Delegation
    document.addEventListener('mouseover', function(event) {
        const varTag = event.target.closest('.var-tag');
        if (!varTag) return;
        
        const symbol = varTag.getAttribute('data-symbol');
        if (!symbol) return;
        
        const card = varTag.closest('.platinum-formula-card');
        if (!card) return;
        
        const mathContent = card.querySelector('.math-content');
        if (!mathContent) return;
        
        const candidates = getCandidateHexCodes(symbol);
        if (candidates.length === 0) return;
        
        // Construct selectors for SVG (use) and CHTML (mjx-c)
        let selectors = [];
        candidates.forEach(hex => {
            // SVG hrefs
            selectors.push(`use[href$="-${hex}"]`);
            selectors.push(`use[*|href$="-${hex}"]`);
            selectors.push(`use[href$="-${hex.toLowerCase()}"]`);
            selectors.push(`use[*|href$="-${hex.toLowerCase()}"]`);
            
            // CHTML classes
            selectors.push(`mjx-c.mjx-c${hex}`);
            selectors.push(`mjx-c.mjx-c${hex.toLowerCase()}`);
            selectors.push(`mjx-c[class*="c${hex}"]`);
            selectors.push(`mjx-c[class*="c${hex.toLowerCase()}"]`);
        });
        
        const matchingElements = mathContent.querySelectorAll(selectors.join(','));
        if (matchingElements.length > 0) {
            mathContent.classList.add('has-highlighted');
            matchingElements.forEach(el => {
                el.classList.add('highlighted-term');
            });
        }
    });

    document.addEventListener('mouseout', function(event) {
        const varTag = event.target.closest('.var-tag');
        if (!varTag) return;
        
        const card = varTag.closest('.platinum-formula-card');
        if (!card) return;
        
        const mathContent = card.querySelector('.math-content');
        if (!mathContent) return;
        
        mathContent.classList.remove('has-highlighted');
        const highlighted = mathContent.querySelectorAll('.highlighted-term');
        highlighted.forEach(el => {
            el.classList.remove('highlighted-term');
        });
    });

    // 5. Topic Abstract Single-Letter Variable Hover-Card Logic
    let topicVarMap = {};
    const mapScript = document.getElementById('topic-var-map');
    if (mapScript) {
        try {
            topicVarMap = JSON.parse(mapScript.textContent || '{}');
        } catch (e) {
            console.warn('Failed to parse topic-var-map JSON:', e);
        }
    }

    let hoverPopover = null;
    let hideTimer = null;

    function getOrCreatePopover() {
        if (!hoverPopover) {
            hoverPopover = document.createElement('div');
            hoverPopover.id = 'variable-hover-card-popover';
            hoverPopover.className = 'variable-hover-popover';
            document.body.appendChild(hoverPopover);

            hoverPopover.addEventListener('mouseenter', () => {
                if (hideTimer) clearTimeout(hideTimer);
            });

            hoverPopover.addEventListener('mouseleave', () => {
                hidePopover();
            });
        }
        return hoverPopover;
    }

    function showPopover(trigger, symbol) {
        const data = topicVarMap[symbol] || topicVarMap[symbol.toUpperCase()] || topicVarMap[symbol.toLowerCase()];
        if (!data) return;

        const popover = getOrCreatePopover();
        if (hideTimer) clearTimeout(hideTimer);

        const title = data.name || symbol;
        const unit = data.unit && data.unit !== 'dimensionless' ? `<span class="popover-unit-badge">${data.unit}</span>` : '';
        const desc = data.description ? `<p class="popover-desc">${data.description}</p>` : '';
        
        let formulasHtml = '';
        if (data.formulas && data.formulas.length > 0) {
            const chips = data.formulas.map(f => `<span class="popover-formula-chip">${f}</span>`).join('');
            formulasHtml = `<div class="popover-formulas-label">Appears in:</div><div class="popover-formulas">${chips}</div>`;
        }

        popover.innerHTML = `
            <div class="popover-header">
                <span class="popover-symbol">${symbol}</span>
                <span class="popover-title">${title}</span>
                ${unit}
            </div>
            ${desc}
            ${formulasHtml}
        `;

        // Position calculation with boundary safety
        const rect = trigger.getBoundingClientRect();
        const popWidth = 320;
        let left = rect.left + window.scrollX;
        let top = rect.bottom + window.scrollY + 8;

        // Viewport right edge overflow check
        if (rect.left + popWidth > window.innerWidth - 20) {
            left = Math.max(10, window.innerWidth - popWidth - 20) + window.scrollX;
        }

        // Viewport bottom overflow check
        if (rect.bottom + 200 > window.innerHeight) {
            top = rect.top + window.scrollY - 180;
        }

        popover.style.left = `${left}px`;
        popover.style.top = `${top}px`;
        popover.classList.add('is-visible');
    }

    function hidePopover() {
        hideTimer = setTimeout(() => {
            if (hoverPopover) {
                hoverPopover.classList.remove('is-visible');
            }
        }, 150);
    }

    // Scoped Event Delegation for Topic Beginning Abstract & Subtopic Cards
    document.addEventListener('mouseover', function(e) {
        const trigger = e.target.closest('#topic-beginning-abstract .variable-hover-trigger, .subtopic-card-abstract .variable-hover-trigger');
        if (!trigger) return;

        const symbol = trigger.getAttribute('data-symbol');
        if (symbol) {
            showPopover(trigger, symbol);
        }
    });

    document.addEventListener('mouseout', function(e) {
        const trigger = e.target.closest('#topic-beginning-abstract .variable-hover-trigger, .subtopic-card-abstract .variable-hover-trigger');
        if (!trigger) return;

        hidePopover();
    });
});

