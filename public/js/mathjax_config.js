window.MathJax = {
    tex: {
        packages: {'[+]': ['amsmath', 'boldsymbol']},
        inlineMath: [['\\(', '\\)'], ['$', '$']],
        displayMath: [['\\[', '\\]'], ['$$', '$$']],
        processEscapes: true
    },
    options: {
        enableMenu: false
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise().then(() => {
            const hash = window.location.hash;
            if (hash) {
                try {
                    const target = document.querySelector(hash);
                    if (target) {
                        // Smoothly scroll to the target element after layout shifts settle
                        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                } catch (e) {
                    console.warn("Invalid hash selector:", hash, e);
                }
            }
        });
    }
});
