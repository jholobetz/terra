window.MathJax = {
    tex: {
        packages: {'[+]': ['amsmath', 'boldsymbol', 'color', 'html']},
        inlineMath: [['\\(', '\\)'], ['$', '$']],
        displayMath: [['\\[', '\\]'], ['$$', '$$']],
        processEscapes: true
    },
    options: {
        enableMenu: false
    }
};

document.addEventListener('DOMContentLoaded', () => {
    // Fallback typesetting trigger if loaded dynamically or already active
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise().then(() => {
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
        }).catch(err => console.warn("MathJax initial typeset error:", err));
    }
});
