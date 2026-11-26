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

window.ensureMathJax = (function() {
    let pendingPromise = null;
    const configScript = document.currentScript || document.getElementById('mathjax-config-script');
    const mathJaxSrc = (configScript && configScript.getAttribute('data-mathjax-src')) || '/js/lib/tex-svg-full.js';
    const cspNonce = (configScript && (configScript.nonce || configScript.getAttribute('nonce'))) || '';

    return function ensureMathJax() {
        if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
            return Promise.resolve(window.MathJax);
        }
        if (pendingPromise) {
            return pendingPromise;
        }
        pendingPromise = new Promise((resolve, reject) => {
            let script = document.getElementById('MathJax-script');
            const finish = () => {
                if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
                    window.MathJax.startup.promise.then(() => resolve(window.MathJax), reject);
                } else {
                    resolve(window.MathJax);
                }
            };
            if (script) {
                script.addEventListener('load', finish, { once: true });
                script.addEventListener('error', reject, { once: true });
                return;
            }
            script = document.createElement('script');
            script.id = 'MathJax-script';
            script.src = mathJaxSrc;
            script.async = true;
            if (cspNonce) {
                script.setAttribute('nonce', cspNonce);
            }
            script.addEventListener('load', finish, { once: true });
            script.addEventListener('error', reject, { once: true });
            document.head.appendChild(script);
        });
        return pendingPromise;
    };
})();

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
    if (window.hasUnrenderedMath(document.body)) {
        if (window.MathJax && window.MathJax.typesetPromise) {
            window._initialMathJaxTypesetQueued = true;
            window.MathJax.typesetPromise().then(scrollToHash).catch(err => console.warn("MathJax initial typeset error:", err));
        } else if (typeof window.ensureMathJax === 'function') {
            window._initialMathJaxTypesetQueued = true;
            window.ensureMathJax()
                .then(mj => mj && mj.typesetPromise ? mj.typesetPromise() : null)
                .then(scrollToHash)
                .catch(err => console.warn("MathJax lazy typeset error:", err));
        } else {
            scrollToHash();
        }
    } else {
        scrollToHash();
    }
});
