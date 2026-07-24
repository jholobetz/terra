/**
 * 🪐 Project Terra - TeX & Math Tokenizer Module
 * Single Source of Truth for LaTeX parsing, domain detection, and AST tokenization.
 */

export function detectDomainFromLatex(latex) {
    if (!latex) return null;
    latex = latex.replace(/\\par\b/g, ' ')
                 .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                 .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                 .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                 .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                 .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                 .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');
    
    // 1. Syntactic / Structural Anchor Detection (Rule-Based overrides)
    if (/(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)_(?:\\mu|\\nu|\\alpha|\\beta)/.test(latex) || /(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)\^(?:\\mu|\\nu|\\alpha|\\beta)/.test(latex)) {
        return 'quantum_mechanics';
    }
    
    if (/\\(oint|iint|iiint|int)_\{?[CSV]\}?/.test(latex) || /\\nabla\s*\\times/.test(latex)) {
        if (/(?:\\mathbf\{E\}|\\mathbf\{B\}|\\mathbf\{J\}|\\epsilon_0|\\mu_0|q|e|\\Phi)/.test(latex)) {
            return 'electromagnetism';
        }
        return 'classical_mechanics';
    }

    if (/\\\{\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*,\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*\\\}/.test(latex)) {
        return 'classical_mechanics';
    }
    
    if (/\\langle|\\rangle|\\mid/.test(latex)) {
        return 'quantum_mechanics';
    }
    
    if (/\b(dU|dS|dV|dH|dG|dQ|dW)\b/.test(latex)) {
        return 'thermodynamics';
    }
    
    // 2. Co-occurrence / Match Counts
    const ANCHORS = {
        thermodynamics: [
            'T', 'S', 'Q', 'U', 'H', '\\Omega', '\\ln', 'k_B', 'R', 'P', 'V',
            '\\beta', '\\mu', 'N_A'
        ],
        electromagnetism: [
            '\\mathbf{E}', '\\mathbf{B}', '\\mathbf{J}', '\\rho', '\\epsilon_0',
            '\\mu_0', '\\Phi', '\\mathbf{A}', 'q', 'e', 'E_x', 'E_y', 'E_z',
            'B_x', 'B_y', 'B_z', '\\nabla \\times', '\\nabla \\cdot'
        ],
        quantum_mechanics: [
            '\\hbar', '\\Psi', '\\psi', '\\hat{H}', '\\phi', '\\hat{p}', '\\hat{x}',
            '\\mid', '\\rangle', '\\langle', 'i', '\\psi^*', '\\Psi^*', '\\hat{A}',
            '\\hat{B}', '\\psi_n', 'E_n', '\\dagger'
        ],
        optics: [
            'n', '\\lambda', 'f', '\\theta', '\\omega', 'k', 'I', 'I_0',
            '\\sin', '\\cos', '\\lambda', '\\nu'
        ]
    };
    
    const counts = {
        classical_mechanics: 0,
        thermodynamics: 0,
        electromagnetism: 0,
        quantum_mechanics: 0,
        optics: 0
    };
    
    for (const [domain, symbols] of Object.entries(ANCHORS)) {
        symbols.forEach(sym => {
            const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const pattern = /^[a-zA-Z0-9]+$/.test(sym) 
                ? new RegExp('\\b' + escaped + '\\b', 'g')
                : new RegExp(escaped, 'g');
                
            const matches = latex.match(pattern);
            if (matches) {
                counts[domain] += matches.length;
            }
        });
    }
    
    const classicalAnchors = ['x', 'v', 'a', 'F', 'm', 'p', 't', '\\tau', 'g', 'r'];
    classicalAnchors.forEach(sym => {
        const pattern = new RegExp('\\b' + sym + '\\b', 'g');
        const matches = latex.match(pattern);
        if (matches) {
            counts.classical_mechanics += matches.length;
        }
    });
    
    const hasSymbol = (sym) => {
        const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        const pattern = /^[a-zA-Z0-9]+$/.test(sym) 
            ? new RegExp('\\b' + escaped + '\\b')
            : new RegExp(escaped);
        return pattern.test(latex);
    };

    if (hasSymbol('T') && hasSymbol('V') && (hasSymbol('L') || hasSymbol('\\mathcal{L}'))) {
        counts.classical_mechanics += 3.0;
    }
    if (hasSymbol('F') && hasSymbol('m') && hasSymbol('a')) {
        counts.classical_mechanics += 2.0;
    }
    if (hasSymbol('r') && hasSymbol('p') && (hasSymbol('L') || hasSymbol('I'))) {
        counts.classical_mechanics += 2.0;
    }
    
    if (hasSymbol('P') && hasSymbol('V') && hasSymbol('T')) {
        counts.thermodynamics += 3.0;
    }
    if (hasSymbol('k_B') && hasSymbol('T')) {
        counts.thermodynamics += 2.0;
    }
    if (hasSymbol('U') && hasSymbol('S') && hasSymbol('T')) {
        counts.thermodynamics += 2.5;
    }
    if (hasSymbol('S') && hasSymbol('Q') && hasSymbol('T')) {
        counts.thermodynamics += 3.0;
    }
    
    if (hasSymbol('\\epsilon_0') && hasSymbol('\\mu_0')) {
        counts.electromagnetism += 3.0;
    }
    if (hasSymbol('\\epsilon_0')) {
        counts.electromagnetism += 1.5;
    }
    if (hasSymbol('\\epsilon_0') && (hasSymbol('\\mathbf{E}') || hasSymbol('E'))) {
        counts.electromagnetism += 3.0;
    }
    if (hasSymbol('\\mathbf{E}') && hasSymbol('\\mathbf{B}')) {
        counts.electromagnetism += 2.5;
    }
    if (hasSymbol('q') && (hasSymbol('\\mathbf{E}') || hasSymbol('\\mathbf{B}'))) {
        counts.electromagnetism += 2.0;
    }
    
    if (hasSymbol('\\hbar') && (hasSymbol('\\psi') || hasSymbol('\\Psi'))) {
        counts.quantum_mechanics += 3.0;
    }
    if (hasSymbol('i') && hasSymbol('\\hbar') && hasSymbol('\\partial')) {
        counts.quantum_mechanics += 2.5;
    }
    if (hasSymbol('\\hat{H}') && hasSymbol('E')) {
        counts.quantum_mechanics += 2.0;
    }
    
    if (hasSymbol('n') && hasSymbol('\\lambda')) {
        counts.optics += 2.0;
    }
    if (hasSymbol('\\omega') && hasSymbol('k')) {
        counts.optics += 2.0;
    }

    let maxDomain = 'classical_mechanics';
    let maxCount = counts.classical_mechanics;
    
    for (const [domain, count] of Object.entries(counts)) {
        if (count > maxCount) {
            maxCount = count;
            maxDomain = domain;
        }
    }
    
    return maxCount > 0 ? maxDomain : 'classical_mechanics';
}

export function extractAllMathTokens(latex) {
    if (!latex) return [];
    
    let clean = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\left|\\right/g, '')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');

    const tokens = new Set();
    const tokenRegex = /(\\mathbf\{[a-zA-Z0-9]+\}|\\boldsymbol\{[a-zA-Z0-9\\]+\}|\\hat\{[a-zA-Z0-9\\]+\}|\\ddot\{[a-zA-Z0-9\\]+\}|\\dot\{[a-zA-Z0-9\\]+\}|\\bar\{[a-zA-Z0-9\\]+\}|\\vec\{[a-zA-Z0-9\\]+\}|\\(?:hbar|epsilon_0|mu_0|k_B|alpha|beta|gamma|delta|epsilon|zeta|eta|theta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|partial|nabla)|[a-zA-Z])/g;

    let match;
    while ((match = tokenRegex.exec(clean)) !== null) {
        tokens.add(match[0]);
    }

    return Array.from(tokens);
}
