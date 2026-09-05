/**
 * public/js/math_prose_formatter.js
 * 
 * Centralized client-side Math and Prose Formatter for Terra Physics Lab.
 * Deconstructs bare math, handles Markdown parsing, and wraps mathematical expressions
 * cleanly in MathJax inline \( ... \) delimiters for uniform browser rendering.
 * 
 * Shared by:
 *  - Equation Explainer (equation_explainer.js)
 *  - Formula Inspector hovercards (formula_inspector.js)
 *  - Formula Graph interactive tooltips (formula_graph.js)
 */

(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.MathProseFormatter = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {

    const greekMap = {
        'Γ': '\\Gamma', 'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta',
        'ε': '\\epsilon', 'θ': '\\theta', 'λ': '\\lambda', 'μ': '\\mu', 'ν': '\\nu',
        'π': '\\pi', 'ρ': '\\rho', 'σ': '\\sigma', 'τ': '\\tau', 'φ': '\\phi',
        'ψ': '\\psi', 'ω': '\\omega', 'Ω': '\\Omega', 'Δ': '\\Delta'
    };

    const units = ['C', 'J', 'K', 's', 'V', 'W', 'Pa', 'Hz', 'N', 'rad', 'mol'];

    function isMathParen(innerStr) {
        const s = innerStr.trim();
        if (!s) return false;
        if (s.includes(',') || s.includes(';')) return false;
        if (/\b(or|in|and|of|for|at|to|is|with|where|if|not|by|on|the|an|e\.g\.|i\.e\.|eigenfunctions?|eigenvalues?)\b/i.test(s)) return false;
        if (/^[a-zA-Z]{3,}$/.test(s)) return false;
        if (units.includes(s)) return false;
        const words = s.split(/\s+/);
        if (words.length > 1) {
            const allMath = words.every(w => /^[a-zA-Z0-9_\^\\]+$/.test(w) && !/^[a-zA-Z]{3,}$/.test(w));
            if (!allMath) return false;
        }
        return true;
    }

    function format(text) {
        if (typeof text !== 'string' || !text) return text || '';

        const placeholders = [];
        let tempText = text.replace(/\r\n/g, '\n');
        tempText = tempText.replace(/\\n(?=\s*(?:\d+\.|\*|-))/g, '\n');
        tempText = tempText.replace(/\\par\b/g, ' ');

        function protect(match) {
            placeholders.push(match);
            return `\uE000MATH_${placeholders.length - 1}\uE000`;
        }

        // 1. Protect existing MathJax delimiters ($$, $, \(\), \[\]) non-greedily first
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
    }

    return {
        format: format,
        isMathParen: isMathParen,
        greekMap: greekMap
    };
}));
