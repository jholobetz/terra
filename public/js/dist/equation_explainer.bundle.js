(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.EquationExplainer = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {
const fallbackBinders = [
    {
        signature: 'electrostatic_field_energy',
        matchPattern: /\\int_?(\{?V\}?)?.*E.*\^2.*d\\tau|\\int_?(\{?V\}?)?.*\\mathbf\{E\}.*\^2.*d\\tau|u_E/,
        name: 'Electrostatic Field Energy',
        domain: 'electromagnetism',
        variableOverrides: {
            'W': { name: 'Electrostatic Energy', unit: 'J', desc: 'The potential energy stored in the electric field of a distribution of charges.' },
            'u_E': { name: 'Electric Field Energy Density', unit: 'J/m³', desc: 'The energy stored per unit volume in the electric field.' },
            'E': { name: 'Electric Field Strength', unit: 'V/m', desc: 'The magnitude of the electric field vector.' },
            '\\tau': { name: 'Infinitesimal Volume Element', unit: 'm³', desc: 'An infinitesimal region of space over which the volume integration is performed.' }
        }
    },
    {
        signature: 'general_relativity_geodesic',
        matchPattern: /\\frac\{d\^?2\s*[a-zA-Z]+\^?\{?\\mu\}\?\}\{d\\tau\^?2\}|\\Gamma\^?\\mu_\{?\\alpha\\beta\}\?/,
        name: 'Geodesic Equation',
        domain: 'quantum_mechanics',
        variableOverrides: {
            '\\tau': { name: 'Proper Time', unit: 's', desc: 'The time interval elapsed on a clock carried along the worldline of the particle.' },
            's': { name: 'Spacetime Interval', unit: 'm', desc: 'The invariant distance between two events in spacetime.' }
        }
    }
];
const variableDictionary = {
    'm': {
        name: 'Mass',
        defaultUnit: 'kg',
        description: 'A fundamental measure of the amount of matter in an object, which acts as a quantitative measure of inertia (resistance to acceleration) and determines the strength of its gravitational attraction.',
        featuredEquations: [
            { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" },
            { name: "Kinetic Energy", latex: "E_k = \\frac{1}{2} m v^2" }
        ]
    },
    't': {
        name: 'Time',
        defaultUnit: 's',
        description: 'The continuous, progressive sequence of events in which change occurs. It acts as the independent variable in dynamical equations of motion.',
        featuredEquations: [
            { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" },
            { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\frac{d\\mathbf{v}}{dt}" }
        ]
    },
    'x': {
        name: 'Position / Displacement',
        defaultUnit: 'm',
        description: 'A coordinate representing the location of a particle along a specific axis, or the displacement from an equilibrium position.',
        featuredEquations: [
            { name: "Simple Harmonic Oscillator", latex: "\\ddot{x} + \\omega^2 x = 0" }
        ]
    },
    'y': {
        name: 'Position Coordinate',
        defaultUnit: 'm',
        description: 'A coordinate representing the vertical or transverse location of a particle in space.',
        featuredEquations: []
    },
    'z': {
        name: 'Position Coordinate',
        defaultUnit: 'm',
        description: 'A coordinate representing the longitudinal or altitude location of a particle in space.',
        featuredEquations: []
    },
    'r': {
        name: 'Radial Distance / Radius',
        defaultUnit: 'm',
        description: 'The radial distance from a central source or origin, typically used in spherical or cylindrical coordinate systems.',
        featuredEquations: [
            { name: "Universal Gravitation", latex: "\\mathbf{F}_g = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}" },
            { name: "Coulomb's Law", latex: "F_e = \\frac{1}{4\\pi\\epsilon_0} \\frac{q_1 q_2}{r^2}" }
        ]
    },
    '\\mathbf{r}': {
        name: 'Position Vector',
        defaultUnit: 'm',
        description: 'A vector pointing from the coordinate origin to the current spatial location of a particle.',
        featuredEquations: [
            { name: "Torque Definition", latex: "\\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F}" }
        ]
    },
    'v': {
        name: 'Velocity / Speed',
        defaultUnit: 'm/s',
        description: 'The rate of change of position with respect to time.',
        featuredEquations: [
            { name: "Kinetic Energy", latex: "E_k = \\frac{1}{2} m v^2" }
        ]
    },
    '\\mathbf{v}': {
        name: 'Velocity Vector',
        defaultUnit: 'm/s',
        description: 'The vector rate of change of position with respect to time.',
        featuredEquations: [
            { name: "Lorentz Force", latex: "\\mathbf{F} = q(\\mathbf{E} + \\mathbf{v} \\times \\mathbf{B})" }
        ]
    },
    'a': {
        name: 'Acceleration',
        defaultUnit: 'm/s²',
        description: 'The rate of change of velocity with respect to time.',
        featuredEquations: [
            { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" }
        ]
    },
    '\\mathbf{a}': {
        name: 'Acceleration Vector',
        defaultUnit: 'm/s²',
        description: 'The vector rate of change of velocity with respect to time.',
        featuredEquations: []
    },
    'F': {
        name: 'Force Magnitude',
        defaultUnit: 'N',
        description: 'An interaction that, when unopposed, will change the motion of an object.',
        featuredEquations: []
    },
    '\\mathbf{F}': {
        name: 'Force Vector',
        defaultUnit: 'N',
        description: 'The vector representation of an interaction causing acceleration.',
        featuredEquations: [
            { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" }
        ]
    },
    'E': {
        name: 'Energy',
        defaultUnit: 'J',
        description: 'The quantitative property that must be transferred to a body or physical system to perform work on, or to heat, the body.',
        featuredEquations: [
            { name: "Mass-Energy Equivalence", latex: "E = m c^2" }
        ]
    },
    'P': {
        name: 'Pressure / Power',
        defaultUnit: 'Pa',
        description: 'Pressure (force per unit area) or Power (energy per unit time), depending on physical context.',
        featuredEquations: [
            { name: "Ideal Gas Law", latex: "P V = N k_B T" }
        ]
    },
    'p': {
        name: 'Linear Momentum Magnitude',
        defaultUnit: 'kg·m/s',
        description: 'The product of the mass and velocity of an object.',
        featuredEquations: []
    },
    '\\mathbf{p}': {
        name: 'Linear Momentum Vector',
        defaultUnit: 'kg·m/s',
        description: 'The vector product of mass and velocity vector.',
        featuredEquations: [
            { name: "De Broglie Wavelength", latex: "\\lambda = \\frac{h}{p}" }
        ]
    },
    'q': {
        name: 'Electric Charge',
        defaultUnit: 'C',
        description: 'The physical property of matter that causes it to experience a force when placed in an electromagnetic field.',
        featuredEquations: [
            { name: "Coulomb's Law", latex: "F_e = \\frac{1}{4\\pi\\epsilon_0} \\frac{q_1 q_2}{r^2}" }
        ]
    },
    'T': {
        name: 'Absolute Temperature',
        defaultUnit: 'K',
        description: 'A physical quantity that expresses quantitative perceptions of hotness and coldness.',
        featuredEquations: [
            { name: "Ideal Gas Law", latex: "P V = N k_B T" }
        ]
    },
    'V': {
        name: 'Volume / Electric Potential',
        defaultUnit: 'm³',
        description: 'Volume occupied by a system or Electric Potential (Voltage), depending on context.',
        featuredEquations: []
    },
    '\\hbar': {
        name: 'Reduced Planck Constant',
        defaultUnit: 'J·s',
        description: 'The fundamental constant of quantum mechanics, equal to Planck\'s constant divided by 2π.',
        featuredEquations: [
            { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" },
            { name: "Heisenberg Uncertainty Principle", latex: "\\Delta x \\Delta p \\ge \\frac{\\hbar}{2}" }
        ]
    },
    '\\Psi': {
        name: 'Wavefunction',
        defaultUnit: 'm⁻³/²',
        description: 'A mathematical description of the quantum state of an isolated quantum system.',
        featuredEquations: [
            { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" }
        ]
    },
    '\\hat{H}': {
        name: 'Hamiltonian Operator',
        defaultUnit: 'J',
        description: 'The operator corresponding to the total energy of a system in quantum mechanics.',
        featuredEquations: [
            { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" }
        ]
    },
    '\\mathbf{E}': {
        name: 'Electric Field Vector',
        defaultUnit: 'V/m',
        description: 'A vector field surrounding electric charges that exerts force on other charges.',
        featuredEquations: [
            { name: "Gauss's Law", latex: "\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}" }
        ]
    },
    '\\mathbf{B}': {
        name: 'Magnetic Field Vector',
        defaultUnit: 'T',
        description: 'A vector field describing the magnetic influence on moving electric charges.',
        featuredEquations: [
            { name: "Ampère-Maxwell Law", latex: "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}" }
        ]
    },
    'c': {
        name: 'Speed of Light in Vacuum',
        defaultUnit: 'm/s',
        description: 'The universal physical constant that bounds the maximum speed at which all conventional matter and information can travel.',
        featuredEquations: [
            { name: "Mass-Energy Equivalence", latex: "E = m c^2" }
        ]
    },
    'G': {
        name: 'Gravitational Constant',
        defaultUnit: 'N·m²/kg²',
        description: 'An empirical physical constant involved in the calculation of gravitational effects in Newton\'s law of universal gravitation and Einstein\'s general relativity.',
        featuredEquations: [
            { name: "Universal Gravitation", latex: "\\mathbf{F}_g = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}" }
        ]
    },
    'k_B': {
        name: 'Boltzmann Constant',
        defaultUnit: 'J/K',
        description: 'A physical constant that relates the average relative kinetic energy of particles in a gas with the thermodynamic temperature of the gas.',
        featuredEquations: [
            { name: "Equipartition Theorem", latex: "\\langle E_k \\rangle = \\frac{1}{2} k_B T" }
        ]
    },
    '\\epsilon_0': {
        name: 'Vacuum Permittivity',
        defaultUnit: 'F/m',
        description: 'The absolute dielectric permittivity of classical vacuum.',
        featuredEquations: [
            { name: "Coulomb's Law", latex: "F_e = \\frac{1}{4\\pi\\epsilon_0} \\frac{q_1 q_2}{r^2}" }
        ]
    },
    '\\mu_0': {
        name: 'Vacuum Permeability',
        defaultUnit: 'H/m',
        description: 'The magnetic permeability in a classical vacuum.',
        featuredEquations: [
            { name: "Ampère-Maxwell Law", latex: "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\epsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}" }
        ]
    }
};
const symbolAliases = {
    'mass': 'm',
    'time': 't',
    'position': 'x',
    'velocity': 'v',
    'acceleration': 'a',
    'force': 'F',
    'energy': 'E',
    'pressure': 'P',
    'momentum': 'p',
    'charge': 'q',
    'temperature': 'T',
    'volume': 'V',
    'planck': '\\hbar',
    'wavefunction': '\\Psi',
    'hamiltonian': '\\hat{H}',
    'electric_field': '\\mathbf{E}',
    'magnetic_field': '\\mathbf{B}'
};
function detectDomainFromLatex(latex) {
    if (!latex) return null;
    latex = latex.replace(/\\par\b/g, ' ')
                 .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                 .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                 .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                 .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                 .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                 .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');
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
function canonicalizeTex(latex) {
    if (!latex) return '';
    let clean = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\left|\\right/g, '')
                     .replace(/\\quad|\\qquad|\\,/g, ' ')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');
    clean = clean.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^}]+)\}/g, '$2');
    clean = clean.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');
    clean = clean.replace(/\\cssId\{[^}]+\}\{([^}]+)\}/g, '$1');
    let hasFraction = true;
    while (hasFraction) {
        let next = clean.replace(/\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g, '($1)/($2)');
        if (next === clean) {
            hasFraction = false;
        } else {
            clean = next;
        }
    }
    clean = clean.replace(/\\nabla\s*\\times/g, 'curl')
                 .replace(/\\nabla\s*\\cdot/g, 'div')
                 .replace(/\\nabla\^2/g, 'laplacian')
                 .replace(/\\nabla/g, 'grad');
    clean = clean.replace(/\\to\s*0/g, '=0')
                 .replace(/\\rightarrow\s*0/g, '=0');
    clean = clean.replace(/\s+/g, '').replace(/,/g, '');
    clean = clean.toLowerCase();
    return clean;
}
function parseTexToAST(latex) {
    if (!latex) {
        return { raw: '', canonical: '', operators: [], fields: [], relation: null, limits: [] };
    }
    const canonical = canonicalizeTex(latex);
    const tokens = extractAllMathTokens(latex);
    const operators = [];
    const fields = [];
    const limits = [];
    if (/\\nabla\s*\\times|curl/.test(latex) || canonical.includes('curl')) operators.push('curl');
    if (/\\nabla\s*\\cdot|div/.test(latex) || canonical.includes('div')) operators.push('div');
    if (/\\nabla\^2|laplacian/.test(latex) || canonical.includes('laplacian')) operators.push('laplacian');
    if (/\\partial/.test(latex)) operators.push('partial');
    if (/\\int|\\oint/.test(latex)) operators.push('integral');
    if (/\\mathbf\{E\}|\\vec\{E\}|E/.test(latex)) fields.push('E_electric');
    if (/\\mathbf\{B\}|\\vec\{B\}|B/.test(latex)) fields.push('B_magnetic');
    if (/\\mathbf\{J\}|\\vec\{J\}|J/.test(latex)) fields.push('J_current');
    if (/\\mathbf\{A\}|\\vec\{A\}|A/.test(latex)) fields.push('A_potential');
    if (/\bm\b/.test(latex)) fields.push('m_mass');
    if (/\bc\b/.test(latex)) fields.push('c_light');
    if (/\b\hbar\b/.test(latex)) fields.push('hbar');
    let relation = null;
    if (latex.includes('=')) relation = '=';
    else if (latex.includes('\\to') || latex.includes('\\rightarrow')) relation = '\\to';
    if (/\\to\s*0|\\rightarrow\s*0|=0/.test(latex)) {
        limits.push({ type: 'static_limit', target: 'time_derivative', value: 0 });
    }
    return {
        raw: latex,
        canonical: canonical,
        domain: detectDomainFromLatex(latex),
        operators: operators,
        fields: fields,
        relation: relation,
        limits: limits,
        tokens: tokens
    };
}
function extractAllMathTokens(latex) {
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
const EquationExplainer = {
    currentId: null,
    currentLatex: '',
    currentFormula: null,
    currentSubtopics: [],
    navigationStack: [],
    activeBinder: null,
    fallbackBinders,
    variableDictionary,
    symbolAliases,
    detectDomainFromLatex,
    extractAllMathTokens,
    init() {
        if (typeof window !== 'undefined') {
            window.EquationExplainer = this;
        }
    }
};
if (typeof window !== 'undefined') {
    window.EquationExplainer = EquationExplainer;
}
    return typeof EquationExplainer !== 'undefined' ? EquationExplainer : {};
}));