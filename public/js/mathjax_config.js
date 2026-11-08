window.MathJax = {
    tex: {
        packages: {'[+]': ['amsmath', 'amssymb', 'boldsymbol', 'color', 'html']},
        inlineMath: [['\\(', '\\)'], ['$', '$']],
        displayMath: [['\\[', '\\]'], ['$$', '$$']],
        processEscapes: true
    },
    options: {
        enableMenu: false
    }
};

window.hasUnrenderedMath = function(rootEl) {
    const el = rootEl || (typeof document !== 'undefined' ? document.body : null);
    if (!el) return false;
    const text = el.textContent || '';
    return /\\[\(\[]|\$\$|\$[^$\n]+\$/.test(text);
};

document.addEventListener('DOMContentLoaded', () => {
    const scrollToHash = () => {
        const hash = window.location.hash;
        if (hash) {
            try {
                const target = document.querySelector(hash);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } catch (e) {
                console.warn("Invalid hash selector:", hash, e);
            }
        }
    };

    // Fallback typesetting trigger only when unrendered math delimiters exist in the DOM
    if (window.MathJax && window.MathJax.typesetPromise && window.hasUnrenderedMath(document.body)) {
        window._initialMathJaxTypesetQueued = true;
        window.MathJax.typesetPromise().then(scrollToHash).catch(err => console.warn("MathJax initial typeset error:", err));
    } else {
        scrollToHash();
    }
});
