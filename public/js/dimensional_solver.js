/**
 * Cosmic Obsidian - Dimensional Solver & Algebraic Consistency Engine
 * Parses physical formulas, evaluates dimensional integrity, and reduces equations to SI base dimensions.
 */

// Predefined mapping of standard symbols to 5D vectors: [Mass, Length, Time, Current, Temperature]
const SYMBOL_MAP = {
    // Constants
    'hbar': { vector: [1, 2, -1, 0, 0], symbol: '\\hbar', name: 'Reduced Planck Constant', unit: 'J·s' },
    'h': { vector: [1, 2, -1, 0, 0], symbol: 'h', name: 'Planck Constant', unit: 'J·s' },
    'c': { vector: [0, 1, -1, 0, 0], symbol: 'c', name: 'Speed of Light', unit: 'm/s' },
    'G': { vector: [-1, 3, -2, 0, 0], symbol: 'G', name: 'Gravitational Constant', unit: 'm³/(kg·s²)' },
    'k_B': { vector: [1, 2, -2, 0, -1], symbol: 'k_B', name: 'Boltzmann Constant', unit: 'J/K' },
    'eps0': { vector: [-1, -3, 4, 2, 0], symbol: '\\epsilon_0', name: 'Vacuum Permittivity', unit: 'F/m' },
    'mu0': { vector: [1, 1, -2, -2, 0], symbol: '\\mu_0', name: 'Vacuum Permeability', unit: 'N/A²' },
    'e': { vector: [0, 0, 1, 1, 0], symbol: 'e', name: 'Elementary Charge', unit: 'C' },
    'm_e': { vector: [1, 0, 0, 0, 0], symbol: 'm_e', name: 'Electron Mass', unit: 'kg' },
    'pi': { vector: [0, 0, 0, 0, 0], symbol: '\\pi', name: 'Pi (Constant)', unit: 'dimensionless' },
    
    // Variables
    'm': { vector: [1, 0, 0, 0, 0], symbol: 'm', name: 'Mass', unit: 'kg' },
    'M': { vector: [1, 0, 0, 0, 0], symbol: 'M', name: 'Mass', unit: 'kg' },
    't': { vector: [0, 0, 1, 0, 0], symbol: 't', name: 'Time', unit: 's' },
    'r': { vector: [0, 1, 0, 0, 0], symbol: 'r', name: 'Radius / Position', unit: 'm' },
    'x': { vector: [0, 1, 0, 0, 0], symbol: 'x', name: 'Position', unit: 'm' },
    'y': { vector: [0, 1, 0, 0, 0], symbol: 'y', name: 'Position', unit: 'm' },
    'z': { vector: [0, 1, 0, 0, 0], symbol: 'z', name: 'Position', unit: 'm' },
    'd': { vector: [0, 1, 0, 0, 0], symbol: 'd', name: 'Distance', unit: 'm' },
    'L': { vector: [0, 1, 0, 0, 0], symbol: 'L', name: 'Length', unit: 'm' },
    'v': { vector: [0, 1, -1, 0, 0], symbol: 'v', name: 'Velocity', unit: 'm/s' },
    'a': { vector: [0, 1, -2, 0, 0], symbol: 'a', name: 'Acceleration', unit: 'm/s²' },
    'F': { vector: [1, 1, -2, 0, 0], symbol: 'F', name: 'Force', unit: 'N' },
    'E': { vector: [1, 2, -2, 0, 0], symbol: 'E', name: 'Energy', unit: 'J' },
    'P': { vector: [1, -1, -2, 0, 0], symbol: 'P', name: 'Pressure', unit: 'Pa' },
    'p': { vector: [1, 1, -1, 0, 0], symbol: 'p', name: 'Momentum', unit: 'kg·m/s' },
    'q': { vector: [0, 0, 1, 1, 0], symbol: 'q', name: 'Electric Charge', unit: 'C' },
    'I': { vector: [0, 0, 0, 1, 0], symbol: 'I', name: 'Electric Current', unit: 'A' },
    'T': { vector: [0, 0, 0, 0, 1], symbol: 'T', name: 'Temperature', unit: 'K' },
    'f': { vector: [0, 0, -1, 0, 0], symbol: 'f', name: 'Frequency', unit: 'Hz' },
    'nu': { vector: [0, 0, -1, 0, 0], symbol: '\\nu', name: 'Frequency', unit: 'Hz' },
    'omega': { vector: [0, 0, -1, 0, 0], symbol: '\\omega', name: 'Angular Frequency', unit: 'rad/s' },
    'rho': { vector: [1, -3, 0, 0, 0], symbol: '\\rho', name: 'Mass Density', unit: 'kg/m³' },
    'sigma': { vector: [1, 0, -3, 0, -4], symbol: '\\sigma', name: 'Stefan-Boltzmann Constant', unit: 'W/(m²·K⁴)' },
    'Lambda': { vector: [0, -2, 0, 0, 0], symbol: '\\Lambda', name: 'Cosmological Constant', unit: 'm⁻²' }
};

// Dynamic symbol map containing resolved notation items
const RESOLVED_SYMBOL_MAP = {};

// Initialize RESOLVED_SYMBOL_MAP with predefined SYMBOL_MAP
Object.assign(RESOLVED_SYMBOL_MAP, SYMBOL_MAP);

class DimensionalAnalysisError extends Error {
    constructor(message, suggestions = []) {
        super(message);
        this.name = 'DimensionalAnalysisError';
        this.suggestions = suggestions;
    }
}

function getSuggestionsForMismatch(vA, vB, labelA, labelB) {
    const diff = [];
    const negDiff = [];
    for (let i = 0; i < 5; i++) {
        diff.push(vA[i] - vB[i]);
        negDiff.push(vB[i] - vA[i]);
    }
    
    const suggestions = [];
    
    for (const [key, item] of Object.entries(RESOLVED_SYMBOL_MAP)) {
        if (vectorsEqual(item.vector, diff) && !vectorsEqual(item.vector, [0, 0, 0, 0, 0])) {
            suggestions.push(`Multiply \\(${labelB}\\) by <code>${key}</code> (\\(${item.symbol}\\)) or divide \\(${labelA}\\) by <code>${key}</code> (\\(${item.symbol}\\))`);
        }
        if (vectorsEqual(item.vector, negDiff) && !vectorsEqual(item.vector, [0, 0, 0, 0, 0])) {
            suggestions.push(`Multiply \\(${labelA}\\) by <code>${key}</code> (\\(${item.symbol}\\)) or divide \\(${labelB}\\) by <code>${key}</code> (\\(${item.symbol}\\))`);
        }
    }
    
    return suggestions.slice(0, 4);
}

function getSuggestionsForDimensionless(vA, labelA) {
    const target = [0, 0, 0, 0, 0];
    const negVec = vA.map(x => -x);
    
    const suggestions = [];
    
    for (const [key, item] of Object.entries(RESOLVED_SYMBOL_MAP)) {
        if (vectorsEqual(item.vector, vA) && !vectorsEqual(item.vector, target)) {
            suggestions.push(`Divide \\(${labelA}\\) by <code>${key}</code> (\\(${item.symbol}\\))`);
        }
        if (vectorsEqual(item.vector, negVec) && !vectorsEqual(item.vector, target)) {
            suggestions.push(`Multiply \\(${labelA}\\) by <code>${key}</code> (\\(${item.symbol}\\))`);
        }
    }
    
    return suggestions.slice(0, 4);
}

/**
 * Initializes the symbol map with notation data.
 */
function initSymbolMap() {
    const data = window.NOTATION_DATA || {};
    for (const [key, item] of Object.entries(data)) {
        const identifier = getPlainIdentifier(key, item);
        
        // If not already in map, resolve vector
        if (!RESOLVED_SYMBOL_MAP[identifier]) {
            let vec = [0, 0, 0, 0, 0];
            if (item.dimensions) {
                vec = parseDimensionOrUnitString(item.dimensions);
            } else if (item.unit) {
                vec = parseDimensionOrUnitString(item.unit);
            }
            
            RESOLVED_SYMBOL_MAP[identifier] = {
                vector: vec,
                symbol: item.symbol,
                name: item.name || key,
                unit: item.unit || item.dimensions || 'dimensionless'
            };
        }
    }
}

// Known concepts mapping for resolution badges
const CONCEPT_MAP = [
    { name: 'Dimensionless', vector: [0, 0, 0, 0, 0], class: 'badge-dimensionless' },
    { name: 'Mass', vector: [1, 0, 0, 0, 0], class: 'badge-mass' },
    { name: 'Length / Position', vector: [0, 1, 0, 0, 0], class: 'badge-length' },
    { name: 'Time', vector: [0, 0, 1, 0, 0], class: 'badge-time' },
    { name: 'Electric Current', vector: [0, 0, 0, 1, 0], class: 'badge-current' },
    { name: 'Temperature', vector: [0, 0, 0, 0, 1], class: 'badge-temperature' },
    { name: 'Area', vector: [0, 2, 0, 0, 0], class: 'badge-area' },
    { name: 'Volume', vector: [0, 3, 0, 0, 0], class: 'badge-volume' },
    { name: 'Velocity / Speed', vector: [0, 1, -1, 0, 0], class: 'badge-velocity' },
    { name: 'Acceleration', vector: [0, 1, -2, 0, 0], class: 'badge-acceleration' },
    { name: 'Force', vector: [1, 1, -2, 0, 0], class: 'badge-force' },
    { name: 'Energy / Work / Heat', vector: [1, 2, -2, 0, 0], class: 'badge-energy' },
    { name: 'Power', vector: [1, 2, -3, 0, 0], class: 'badge-power' },
    { name: 'Pressure', vector: [1, -1, -2, 0, 0], class: 'badge-pressure' },
    { name: 'Momentum', vector: [1, 1, -1, 0, 0], class: 'badge-momentum' },
    { name: 'Electric Charge', vector: [0, 0, 1, 1, 0], class: 'badge-charge' },
    { name: 'Electric Potential / Voltage', vector: [1, 2, -3, -1, 0], class: 'badge-voltage' },
    { name: 'Frequency', vector: [0, 0, -1, 0, 0], class: 'badge-frequency' },
    { name: 'Mass Density', vector: [1, -3, 0, 0, 0], class: 'badge-density' },
    { name: 'Action / Planck\'s Quantum', vector: [1, 2, -1, 0, 0], class: 'badge-action' },
    { name: 'Stefan-Boltzmann Constant', vector: [1, 0, -3, 0, -4], class: 'badge-derived' },
    { name: 'Vacuum Permittivity', vector: [-1, -3, 4, 2, 0], class: 'badge-derived' },
    { name: 'Vacuum Permeability', vector: [1, 1, -2, -2, 0], class: 'badge-derived' },
    { name: 'Gravitational Constant', vector: [-1, 3, -2, 0, 0], class: 'badge-derived' }
];

// Precedence system for expressions (for shunting-yard and LaTeX grouping)
const PRECEDENCE = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
    '^': 3,
    'u-': 4 // Unary minus
};

/**
 * Normalizes unicode superscript powers to regular powers.
 */
function unicodeToNormalExponents(str) {
    const map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
        '⁻': '-', '⁺': '+'
    };
    let result = '';
    for (let i = 0; i < str.length; i++) {
        const char = str[i];
        result += map[char] !== undefined ? map[char] : char;
    }
    return result;
}

/**
 * Resolves a clean physical identifier key for the equation editor.
 */
function getPlainIdentifier(key, item) {
    // If exact symbol maps directly, preserve it
    for (const [id, details] of Object.entries(SYMBOL_MAP)) {
        if (details.symbol === item.symbol || id === key) {
            return id;
        }
    }
    // Clean-up key string
    let clean = key.toLowerCase()
                   .replace(/[^a-z0-9_]/g, '_')
                   .replace(/^_+|_+$/g, '');
    if (clean === 'h_bar') return 'hbar';
    if (clean === 'k_b') return 'k_B';
    if (clean === 'epsilon_0') return 'eps0';
    if (clean === 'mu_0') return 'mu0';
    return clean;
}

/**
 * Map unit name to a 5D dimension vector.
 */
function mapUnitNameToVector(name) {
    name = name.trim().toLowerCase();
    if (['kg', 'kilogram', 'kilograms', 'mass'].includes(name)) return [1, 0, 0, 0, 0];
    if (['m', 'meter', 'meters', 'length'].includes(name)) return [0, 1, 0, 0, 0];
    if (['s', 'second', 'seconds', 'time'].includes(name)) return [0, 0, 1, 0, 0];
    if (['a', 'ampere', 'amperes', 'current'].includes(name)) return [0, 0, 0, 1, 0];
    if (['k', 'kelvin', 'kelvins', 'temperature'].includes(name)) return [0, 0, 0, 0, 1];
    
    // Derived
    if (['j', 'joule', 'joules', 'energy', 'work', 'heat'].includes(name)) return [1, 2, -2, 0, 0];
    if (['n', 'newton', 'newtons', 'force'].includes(name)) return [1, 1, -2, 0, 0];
    if (['w', 'watt', 'watts', 'power'].includes(name)) return [1, 2, -3, 0, 0];
    if (['pa', 'pascal', 'pascals', 'pressure'].includes(name)) return [1, -1, -2, 0, 0];
    if (['c', 'coulomb', 'coulombs', 'charge'].includes(name)) return [0, 0, 1, 1, 0];
    if (['f', 'farad', 'farads'].includes(name)) return [-1, -2, 4, 2, 0];
    if (['v', 'volt', 'volts', 'voltage'].includes(name)) return [1, 2, -3, -1, 0];
    if (['hz', 'hertz', 'frequency'].includes(name)) return [0, 0, -1, 0, 0];
    if (['t', 'tesla', 'teslas'].includes(name)) return [1, 0, -2, -1, 0];
    if (['volume'].includes(name)) return [0, 3, 0, 0, 0];
    if (['area'].includes(name)) return [0, 2, 0, 0, 0];
    
    return [0, 0, 0, 0, 0];
}

/**
 * Parses space/multiplication-separated words in a sub-unit string.
 */
function parseTokens(partStr, multiplier, resultVec) {
    const tokens = partStr.split(/[\s*]+/).filter(t => t.trim().length > 0);
    tokens.forEach(token => {
        const match = token.match(/^([a-zA-Z\u0395-\u03a9\u03b1-\u03c9_]+)\^?(-?\d+(?:\.\d+)?)?/);
        if (match) {
            const unitName = match[1].toLowerCase();
            const exponent = match[2] ? parseFloat(match[2]) : 1;
            const unitVec = mapUnitNameToVector(unitName);
            const totalPower = exponent * multiplier;
            
            for (let i = 0; i < 5; i++) {
                resultVec[i] += unitVec[i] * totalPower;
            }
        }
    });
}

/**
 * Dynamically converts dimension strings or unit formulas into 5D vectors.
 */
function parseDimensionOrUnitString(str) {
    if (!str) return [0, 0, 0, 0, 0];
    str = str.trim();
    if (['dimensionless', 'probability', 'constant'].includes(str.toLowerCase())) {
        return [0, 0, 0, 0, 0];
    }
    
    // Normalize unicode exponents
    str = unicodeToNormalExponents(str);
    
    // Strip descriptive parentheses (e.g. "Force / Area (Pascals)" -> "Force / Area")
    str = str.replace(/\([^)]*\)/g, '').trim();
    
    // Check if it is a pure dimension letter
    if (str === 'L') return [0, 1, 0, 0, 0];
    if (str === 'M') return [1, 0, 0, 0, 0];
    if (str === 'T') return [0, 0, 1, 0, 0];
    if (str === 'I') return [0, 0, 0, 1, 0];
    if (str === 'Theta' || str === '\\Theta') return [0, 0, 0, 0, 1];
    
    // LaTeX patterns: e.g. L^{-3/2} or M^1
    const latexPattern = /([MLTI\Theta\theta]|\\mathsf\{[MLTI\Theta\theta]\}|\\Theta)\^?\{?(-?\d+(?:\.\d+)?(?:\/\d+)?)\}?/g;
    let match;
    let vec = [0, 0, 0, 0, 0];
    let foundLatex = false;
    let tempStr = str.replace(/\\mathsf/g, '').replace(/\\text/g, '');
    
    while ((match = latexPattern.exec(tempStr)) !== null) {
        foundLatex = true;
        const sym = match[1].replace(/[\{\}]/g, '').replace('\\', '');
        let power = parseFloat(match[2]);
        if (match[2].includes('/')) {
            const parts = match[2].split('/');
            power = parseFloat(parts[0]) / parseFloat(parts[1]);
        }
        
        let idx = -1;
        if (sym === 'M') idx = 0;
        else if (sym === 'L') idx = 1;
        else if (sym === 'T') idx = 2;
        else if (sym === 'I') idx = 3;
        else if (sym === 'Theta' || sym === '\u0398' || sym === 'theta') idx = 4;
        
        if (idx !== -1) {
            vec[idx] += power;
        }
    }
    
    if (foundLatex) {
        return vec;
    }
    
    // Text parsing (e.g. "J·s" or "m/s" or "Energy / Volume")
    str = str.replace(/[\u22c5\u2022\u2219*]/g, ' * ');
    const parts = str.split('/');
    const numerator = parts[0] || '';
    const denominator = parts[1] || '';
    
    let resultVec = [0, 0, 0, 0, 0];
    parseTokens(numerator, 1, resultVec);
    parseTokens(denominator, -1, resultVec);
    
    return resultVec;
}

/**
 * Checks equality between two 5D vectors within floating point tolerance.
 */
function vectorsEqual(v1, v2) {
    for (let i = 0; i < 5; i++) {
        if (Math.abs(v1[i] - v2[i]) > 1e-9) {
            return false;
        }
    }
    return true;
}

/**
 * Maps a vector to its known physical concept.
 */
function resolveConcept(vec) {
    for (const concept of CONCEPT_MAP) {
        if (vectorsEqual(concept.vector, vec)) {
            return concept;
        }
    }
    return { name: 'Unknown / Complex Derivative', class: 'badge-unknown' };
}

/**
 * Formats a 5D vector to standard LaTeX format.
 */
function formatVectorToLaTeX(vec) {
    const symbols = ['\\mathsf{M}', '\\mathsf{L}', '\\mathsf{T}', '\\mathsf{I}', '\\mathsf{\\Theta}'];
    let parts = [];
    let allZero = true;
    for (let i = 0; i < 5; i++) {
        if (vec[i] !== 0) {
            allZero = false;
            // Rounded to avoid floating point residues (e.g. 1.0000000000000002)
            const powerVal = Math.round(vec[i] * 100) / 100;
            parts.push(`${symbols[i]}^{${powerVal}}`);
        }
    }
    return allZero ? '\\text{dimensionless}' : parts.join(' \\cdot ');
}

/**
 * Formats a 5D vector to standard LaTeX format with class color-coding.
 */
function formatVectorToLaTeXColored(vec) {
    const symbols = ['\\mathsf{M}', '\\mathsf{L}', '\\mathsf{T}', '\\mathsf{I}', '\\mathsf{\\Theta}'];
    const classes = [
        'math-color-mass',
        'math-color-length',
        'math-color-time',
        'math-color-current',
        'math-color-temp'
    ];
    let parts = [];
    let allZero = true;
    for (let i = 0; i < 5; i++) {
        if (vec[i] !== 0) {
            allZero = false;
            const powerVal = Math.round(vec[i] * 100) / 100;
            parts.push(`\\class{${classes[i]}}{${symbols[i]}}^{${powerVal}}`);
        }
    }
    return allZero ? '\\class{math-color-dimensionless}{\\text{dimensionless}}' : parts.join(' \\cdot ');
}

/**
 * Formats a 5D vector to SI base units equivalent in LaTeX.
 */
function formatVectorToSIUnits(vec) {
    const units = ['\\text{kg}', '\\text{m}', '\\text{s}', '\\text{A}', '\\text{K}'];
    let parts = [];
    let allZero = true;
    for (let i = 0; i < 5; i++) {
        if (vec[i] !== 0) {
            allZero = false;
            const powerVal = Math.round(vec[i] * 100) / 100;
            parts.push(`${units[i]}^{${powerVal}}`);
        }
    }
    return allZero ? '\\text{dimensionless}' : parts.join(' \\cdot ');
}

/**
 * Tokenizes a raw string formula.
 */
function tokenize(str) {
    const tokens = [];
    let i = 0;
    
    // Remove space to simplify matching
    str = str.replace(/\s+/g, '');
    
    while (i < str.length) {
        const char = str[i];
        
        if (char === '(' || char === ')') {
            tokens.push({ type: 'PAREN', value: char });
            i++;
            continue;
        }
        
        if (['+', '-', '*', '/', '^'].includes(char)) {
            tokens.push({ type: 'OPERATOR', value: char });
            i++;
            continue;
        }
        
        // Match numbers, including scientific notation and decimals
        const numMatch = str.substring(i).match(/^\d+(\.\d+)?([eE][+-]?\d+)?/);
        if (numMatch) {
            tokens.push({ type: 'NUMBER', value: parseFloat(numMatch[0]) });
            i += numMatch[0].length;
            continue;
        }
        
        // Match identifiers (variable names, letters, constants, or functions)
        const idMatch = str.substring(i).match(/^[a-zA-Z_][a-zA-Z0-9_]*/);
        if (idMatch) {
            const val = idMatch[0];
            const knownFunctions = ['sin', 'cos', 'tan', 'exp', 'log', 'ln'];
            if (knownFunctions.includes(val)) {
                tokens.push({ type: 'FUNCTION', value: val });
            } else {
                tokens.push({ type: 'IDENTIFIER', value: val });
            }
            i += val.length;
            continue;
        }
        
        throw new Error(`Unexpected character in formula: '${char}'`);
    }
    return tokens;
}

/**
 * Identifies and converts binary operators to unary operators (e.g. unary minus 'u-').
 */
function identifyUnaryOperators(tokens) {
    const processed = [];
    for (let idx = 0; idx < tokens.length; idx++) {
        const token = tokens[idx];
        if (token.type === 'OPERATOR' && (token.value === '-' || token.value === '+')) {
            const isUnary = idx === 0 || 
                            processed[idx - 1].type === 'OPERATOR' || 
                            processed[idx - 1].type === 'UNARY_OPERATOR' ||
                            (processed[idx - 1].type === 'PAREN' && processed[idx - 1].value === '(');
            if (isUnary) {
                if (token.value === '-') {
                    processed.push({ type: 'UNARY_OPERATOR', value: 'u-' });
                }
                // Unary + is a no-op, ignore
                continue;
            }
        }
        processed.push(token);
    }
    return processed;
}

/**
 * Shunting-Yard Algorithm to convert infix tokens to RPN (Reverse Polish Notation).
 */
function infixToRPN(tokens) {
    const outputQueue = [];
    const operatorStack = [];
    
    tokens.forEach(token => {
        if (token.type === 'NUMBER' || token.type === 'IDENTIFIER') {
            outputQueue.push(token);
        } else if (token.type === 'FUNCTION') {
            operatorStack.push(token);
        } else if (token.type === 'UNARY_OPERATOR') {
            operatorStack.push(token);
        } else if (token.type === 'OPERATOR') {
            const o1 = token.value;
            let top = operatorStack[operatorStack.length - 1];
            
            while (
                top && 
                (top.type === 'UNARY_OPERATOR' || top.type === 'OPERATOR') &&
                (PRECEDENCE[top.value] > PRECEDENCE[o1] || 
                 (PRECEDENCE[top.value] === PRECEDENCE[o1] && o1 !== '^'))
            ) {
                outputQueue.push(operatorStack.pop());
                top = operatorStack[operatorStack.length - 1];
            }
            operatorStack.push(token);
        } else if (token.type === 'PAREN' && token.value === '(') {
            operatorStack.push(token);
        } else if (token.type === 'PAREN' && token.value === ')') {
            let top = operatorStack[operatorStack.length - 1];
            while (top && !(top.type === 'PAREN' && top.value === '(')) {
                outputQueue.push(operatorStack.pop());
                top = operatorStack[operatorStack.length - 1];
            }
            if (!top) {
                throw new Error("Mismatched parentheses (extra right parenthesis).");
            }
            operatorStack.pop(); // Remove '('
            
            // Pop function if present
            const newTop = operatorStack[operatorStack.length - 1];
            if (newTop && newTop.type === 'FUNCTION') {
                outputQueue.push(operatorStack.pop());
            }
        }
    });
    
    while (operatorStack.length > 0) {
        const top = operatorStack.pop();
        if (top.type === 'PAREN') {
            throw new Error("Mismatched parentheses (extra left parenthesis).");
        }
        outputQueue.push(top);
    }
    
    return outputQueue;
}

/**
 * Fallback mapping for standard letters if they aren't explicitly declared in registry.
 */
function getFallbackSymbol(id) {
    const match = id.match(/^(m|mass)/i);
    if (match) return { vector: [1, 0, 0, 0, 0], latex: 'm', name: 'Mass (Fallback)' };
    
    const rMatch = id.match(/^(r|radius|x|y|z|d|distance|L|length)/i);
    if (rMatch) return { vector: [0, 1, 0, 0, 0], latex: id, name: 'Length (Fallback)' };
    
    const tMatch = id.match(/^(t|time)/i);
    if (tMatch) return { vector: [0, 0, 1, 0, 0], latex: 't', name: 'Time (Fallback)' };
    
    const vMatch = id.match(/^(v|velocity|c)/i);
    if (vMatch) return { vector: [0, 1, -1, 0, 0], latex: id, name: 'Velocity (Fallback)' };
    
    const aMatch = id.match(/^(a|accel)/i);
    if (aMatch) return { vector: [0, 1, -2, 0, 0], latex: 'a', name: 'Acceleration (Fallback)' };
    
    const eMatch = id.match(/^(E|energy)/i);
    if (eMatch) return { vector: [1, 2, -2, 0, 0], latex: 'E', name: 'Energy (Fallback)' };
    
    return null;
}

/**
 * Core evaluation loop of Reverse Polish Notation using a stack.
 */
function evaluateRPN(rpnQueue, steps) {
    const stack = [];
    
    rpnQueue.forEach(token => {
        if (token.type === 'NUMBER') {
            stack.push({
                type: 'number',
                val: token.value,
                vector: [0, 0, 0, 0, 0],
                latex: token.value.toString(),
                precedence: 99
            });
        } else if (token.type === 'IDENTIFIER') {
            const id = token.value;
            let sym = RESOLVED_SYMBOL_MAP[id];
            let stepMsg = '';
            
            if (!sym) {
                // Try fallback symbols mapping (like m, r, t, etc.)
                const fallback = getFallbackSymbol(id);
                if (fallback) {
                    sym = {
                        vector: fallback.vector,
                        symbol: fallback.latex,
                        name: fallback.name,
                        unit: 'inferred'
                    };
                    stepMsg = `Resolved variable <code>${id}</code> to fallback concept <strong>${fallback.name}</strong>: \\(${formatVectorToLaTeXColored(fallback.vector)}\\)`;
                } else {
                    // Default to dimensionless
                    sym = {
                        vector: [0, 0, 0, 0, 0],
                        symbol: id,
                        name: `Unknown '${id}'`,
                        unit: 'dimensionless'
                    };
                    stepMsg = `Variable <code>${id}</code> not in registry: resolved as dimensionless \\([0, 0, 0, 0, 0]\\)`;
                }
            } else {
                stepMsg = `Resolved registry identifier <code>${id}</code> to <strong>${sym.name}</strong>: \\(${formatVectorToLaTeXColored(sym.vector)}\\)`;
            }
            
            steps.push({
                description: stepMsg,
                latex: sym.symbol,
                vector: sym.vector
            });
            
            stack.push({
                type: 'variable',
                name: id,
                vector: [...sym.vector],
                latex: sym.symbol,
                precedence: 99
            });
        } else if (token.type === 'UNARY_OPERATOR') {
            const A = stack.pop();
            if (!A) throw new Error("Invalid expression structure (stack empty for unary minus).");
            
            const wrappedA = A.precedence < 4 ? `\\left( ${A.latex} \\right)` : A.latex;
            
            stack.push({
                type: 'expression',
                vector: [...A.vector],
                latex: `-${wrappedA}`,
                precedence: 4
            });
        } else if (token.type === 'FUNCTION') {
            const A = stack.pop();
            if (!A) throw new Error(`Invalid expression structure (stack empty for function '${token.value}').`);
            
            // Verify argument is dimensionless
            if (!vectorsEqual(A.vector, [0, 0, 0, 0, 0])) {
                const suggestions = getSuggestionsForDimensionless(A.vector, A.latex);
                throw new DimensionalAnalysisError(
                    `Dimensional Error: Argument of function ${token.value}() must be dimensionless. ` +
                    `Found argument \\(${A.latex}\\) with dimensions \\(${formatVectorToLaTeX(A.vector)}\\).`,
                    suggestions
                );
            }
            
            const latexFn = `\\${token.value}`;
            
            steps.push({
                description: `Evaluated function <code>${token.value}</code> with dimensionless argument \\(${A.latex}\\) \\(\\rightarrow\\) result is dimensionless`,
                latex: `${latexFn}\\left( ${A.latex} \\right)`,
                vector: [0, 0, 0, 0, 0]
            });
            
            stack.push({
                type: 'expression',
                vector: [0, 0, 0, 0, 0],
                latex: `${latexFn}\\left( ${A.latex} \\right)`,
                precedence: 99
            });
        } else if (token.type === 'OPERATOR') {
            const op = token.value;
            const B = stack.pop();
            const A = stack.pop();
            
            if (!A || !B) {
                throw new Error(`Invalid expression structure (stack empty for binary operator '${op}').`);
            }
            
            const prec = PRECEDENCE[op];
            const wrapA = A.precedence < prec ? `\\left( ${A.latex} \\right)` : A.latex;
            const wrapB = B.precedence < prec ? `\\left( ${B.latex} \\right)` : B.latex;
            
            if (op === '+' || op === '-') {
                // Verify algebraic consistency (operands must have matching dimensions)
                if (!vectorsEqual(A.vector, B.vector)) {
                    const suggestions = getSuggestionsForMismatch(A.vector, B.vector, A.latex, B.latex);
                    throw new DimensionalAnalysisError(
                        `Dimensional Clash Error: Cannot ${op === '+' ? 'add' : 'subtract'} incompatible dimensions: ` +
                        `\\(${A.latex}\\) which is \\(${formatVectorToLaTeX(A.vector)}\\) and ` +
                        `\\(${B.latex}\\) which is \\(${formatVectorToLaTeX(B.vector)}\\)`,
                        suggestions
                    );
                }
                
                const concept = resolveConcept(A.vector);
                steps.push({
                    description: `Verified algebraic consistency of ${op === '+' ? 'addition' : 'subtraction'}: both operands are <strong>${concept.name}</strong>: \\(${formatVectorToLaTeXColored(A.vector)}\\)`,
                    latex: `${wrapA} ${op} ${wrapB}`,
                    vector: A.vector
                });
                
                stack.push({
                    type: 'expression',
                    vector: [...A.vector],
                    latex: `${wrapA} ${op} ${wrapB}`,
                    precedence: prec
                });
            } else if (op === '*') {
                const resultVec = [];
                for (let i = 0; i < 5; i++) {
                    resultVec.push(A.vector[i] + B.vector[i]);
                }
                
                steps.push({
                    description: `Multiplied expressions: \\(${A.latex}\\) and \\(${B.latex}\\) \\(\\rightarrow\\) adds dimensions`,
                    latex: `${wrapA} \\cdot ${wrapB}`,
                    vector: resultVec
                });
                
                stack.push({
                    type: 'expression',
                    vector: resultVec,
                    latex: `${wrapA} \\cdot ${wrapB}`,
                    precedence: prec
                });
            } else if (op === '/') {
                const resultVec = [];
                for (let i = 0; i < 5; i++) {
                    resultVec.push(A.vector[i] - B.vector[i]);
                }
                
                // Group fractions inside \frac for premium typeset look
                const latexFrac = `\\frac{${A.latex}}{${B.latex}}`;
                
                steps.push({
                    description: `Divided expressions: \\(${A.latex}\\) by \\(${B.latex}\\) \\(\\rightarrow\\) subtracts dimensions`,
                    latex: latexFrac,
                    vector: resultVec
                });
                
                stack.push({
                    type: 'expression',
                    vector: resultVec,
                    latex: latexFrac,
                    precedence: 99 // grouped
                });
            } else if (op === '^') {
                // Exponent must be dimensionless
                if (!vectorsEqual(B.vector, [0, 0, 0, 0, 0])) {
                    const suggestions = getSuggestionsForDimensionless(B.vector, B.latex);
                    throw new DimensionalAnalysisError(
                        `Dimensional Error: Exponent must be dimensionless. Found exponent \\(${B.latex}\\) ` +
                        `with dimensions \\(${formatVectorToLaTeX(B.vector)}\\)`,
                        suggestions
                    );
                }
                
                let exponentVal = 1;
                if (B.val !== undefined && !isNaN(B.val)) {
                    exponentVal = B.val;
                } else {
                    const parsed = parseFloat(B.latex);
                    if (!isNaN(parsed)) {
                        exponentVal = parsed;
                    } else {
                        // Fallback warning for variable exponents
                        steps.push({
                            description: `Warning: Exponent <code>${B.latex}</code> is non-numeric/variable. Assuming scaling power of 1.`,
                            latex: `{${wrapA}}^{${B.latex}}`,
                            vector: A.vector
                        });
                    }
                }
                
                const resultVec = [];
                for (let i = 0; i < 5; i++) {
                    resultVec.push(A.vector[i] * exponentVal);
                }
                
                steps.push({
                    description: `Evaluated power exponent: raising to power of ${exponentVal} \\(\\rightarrow\\) multiplies dimensions`,
                    latex: `{${wrapA}}^{${B.latex}}`,
                    vector: resultVec
                });
                
                stack.push({
                    type: 'expression',
                    vector: resultVec,
                    latex: `{${wrapA}}^{${B.latex}}`,
                    precedence: prec
                });
            }
        }
    });
    
    if (stack.length !== 1) {
        throw new Error("Invalid expression formula. Check mathematical operators and parentheses.");
    }
    
    return stack[0];
}

/**
 * Triggers MathJax typesetting asynchronously.
 */
function typesetMath(elements = null) {
    if (window.MathJax) {
        const run = () => {
            if (window.MathJax.typesetPromise) {
                const target = elements ? (Array.isArray(elements) ? elements : [elements]) : null;
                window.MathJax.typesetPromise(target)
                    .catch(err => console.warn("MathJax typeset error:", err));
            }
        };
        
        // Defer typesetting using a 150ms timeout to ensure DOM changes are painted
        // and any concurrent MathJax initial/startup passes have completed.
        setTimeout(() => {
            if (window.MathJax.typesetPromise) {
                run();
            } else if (window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise.then(run);
            } else {
                setTimeout(run, 100);
            }
        }, 150);
    }
}

function renderTokenPill(token) {
    let bg, border, color;
    switch (token.type) {
        case 'NUMBER':
            bg = 'rgba(52, 211, 153, 0.08)';
            border = 'rgba(52, 211, 153, 0.2)';
            color = '#34d399';
            break;
        case 'IDENTIFIER':
            bg = 'rgba(96, 165, 250, 0.08)';
            border = 'rgba(96, 165, 250, 0.2)';
            color = '#60a5fa';
            break;
        case 'FUNCTION':
            bg = 'rgba(192, 132, 252, 0.08)';
            border = 'rgba(192, 132, 252, 0.2)';
            color = '#c084fc';
            break;
        case 'OPERATOR':
        case 'UNARY_OPERATOR':
            bg = 'rgba(251, 191, 36, 0.08)';
            border = 'rgba(251, 191, 36, 0.2)';
            color = '#fbbf24';
            break;
        case 'PAREN':
            bg = 'rgba(156, 163, 175, 0.08)';
            border = 'rgba(156, 163, 175, 0.2)';
            color = '#9ca3af';
            break;
        default:
            bg = 'rgba(255, 255, 255, 0.05)';
            border = 'rgba(255, 255, 255, 0.1)';
            color = '#ffffff';
    }
    
    return `<div style="background: ${bg}; border: 1px solid ${border}; color: ${color}; padding: 4px 10px; border-radius: 6px; font-size: 0.76rem; display: flex; flex-direction: column; align-items: center; gap: 2px;">` +
           `<span style="font-weight: bold; font-family: 'Fira Code', monospace;">${token.value}</span>` +
           `<span style="font-size: 0.58rem; opacity: 0.6; text-transform: uppercase;">${token.type}</span>` +
           `</div>`;
}

function renderRPNPill(token) {
    let color = '#ffffff';
    if (token.type === 'IDENTIFIER') color = '#60a5fa';
    if (token.type === 'FUNCTION') color = '#c084fc';
    if (token.type === 'OPERATOR' || token.type === 'UNARY_OPERATOR') color = '#fbbf24';
    if (token.type === 'NUMBER') color = '#34d399';
    
    return `<div style="background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); color: ${color}; padding: 6px 12px; border-radius: 6px; font-weight: bold; font-family: 'Fira Code', monospace; font-size: 0.8rem;">${token.value}</div>`;
}

function toggleInspector() {
    const panel = document.getElementById('inspector-panel');
    const icon = document.getElementById('inspector-toggle-icon');
    if (!panel || !icon) return;
    if (panel.style.display === 'none') {
        panel.style.display = 'flex';
        icon.textContent = '[Hide Details]';
    } else {
        panel.style.display = 'none';
        icon.textContent = '[Show Details]';
    }
}
window.toggleInspector = toggleInspector;

/**
 * Main analysis routine.
 */
function analyzeFormula(rawFormula = '') {
    if (!rawFormula) {
        const inputEl = document.getElementById('formula-input');
        if (inputEl) {
            rawFormula = inputEl.value.trim();
        }
    }
    
    if (!rawFormula) {
        const outputPanel = document.getElementById('output-panel');
        if (outputPanel) outputPanel.style.display = 'none';
        const errorPanel = document.getElementById('error-panel');
        if (errorPanel) errorPanel.style.display = 'none';
        const inspectorCard = document.getElementById('inspector-card');
        if (inspectorCard) inspectorCard.style.display = 'none';
        return;
    }
    
    const steps = [];
    
    try {
        // 1. Tokenize & clean
        const tokens = tokenize(rawFormula);
        
        // Render Token Stream
        const tokenContainer = document.getElementById('token-stream-container');
        if (tokenContainer) {
            tokenContainer.innerHTML = tokens.map(t => renderTokenPill(t)).join('');
        }
        
        // 2. Identify unary operations
        const processedTokens = identifyUnaryOperators(tokens);
        
        // 3. Shunting-Yard RPN Conversion
        const rpn = infixToRPN(processedTokens);
        
        // Render RPN Queue
        const rpnContainer = document.getElementById('rpn-queue-container');
        if (rpnContainer) {
            const pills = rpn.map(t => renderRPNPill(t));
            const divider = `<div style="display: flex; align-items: center; color: rgba(255,255,255,0.2); font-weight: bold; margin: 0 4px;">&rarr;</div>`;
            rpnContainer.innerHTML = pills.join(divider);
        }
        
        // 4. Evaluate stack
        const result = evaluateRPN(rpn, steps);
        
        // 5. Map resolved concept
        const concept = resolveConcept(result.vector);
        
        // Update DOM elements
        const resolvedConceptSpan = document.getElementById('resolved-concept');
        resolvedConceptSpan.textContent = concept.name;
        // Apply class
        resolvedConceptSpan.className = 'concept-badge ' + (concept.class || 'badge-unknown');
        
        // Render Math Preview
        document.getElementById('math-expression-render').innerHTML = `\\[ ${result.latex} \\]`;
        
        // Render SI Dimension Vector
        document.getElementById('dimension-vector-render').innerHTML = `\\[ ${formatVectorToLaTeXColored(result.vector)} \\]`;
        
        // Render SI Units Equivalent
        document.getElementById('si-units-render').innerHTML = `\\[ ${formatVectorToSIUnits(result.vector)} \\]`;
        
        // Populate steps list
        const stepsUl = document.getElementById('derivation-steps');
        stepsUl.innerHTML = '';
        
        steps.forEach((step, idx) => {
            const li = document.createElement('li');
            li.innerHTML = `<strong>Step ${idx + 1}:</strong> ${step.description} ` +
                           `<div style="margin-top: 4px; font-size: 0.82rem; color: var(--accent-color);">` +
                           `\\(\\rightarrow ${step.latex}\\) \\(\\quad\\left[ ${formatVectorToLaTeXColored(step.vector)} \\right]\\)</div>`;
            stepsUl.appendChild(li);
        });
        
        // Show output panels
        showOutput();
        
        // Typeset Math
        typesetMath();
        
    } catch (error) {
        showError(error);
    }
}

/**
 * Helper to display the output panel and hide errors.
 */
function showOutput() {
    document.getElementById('output-panel').style.display = 'block';
    document.getElementById('error-panel').style.display = 'none';
    const inspectorCard = document.getElementById('inspector-card');
    if (inspectorCard) inspectorCard.style.display = 'block';
}

/**
 * Helper to display the error panel and hide output.
 */
function showError(err) {
    document.getElementById('output-panel').style.display = 'none';
    const errPanel = document.getElementById('error-panel');
    errPanel.style.display = 'flex';
    
    const inspectorCard = document.getElementById('inspector-card');
    if (inspectorCard) inspectorCard.style.display = 'none';
    
    const errMessage = document.getElementById('error-message');
    
    if (err && err.name === 'DimensionalAnalysisError') {
        let html = `<div style="font-weight: 600; margin-bottom: 6px;">${err.message}</div>`;
        if (err.suggestions && err.suggestions.length > 0) {
            html += `<div class="dimensional-suggestions" style="margin-top: 12px; border-top: 1px solid rgba(239, 68, 68, 0.2); padding-top: 10px;">`;
            html += `<div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.5px; color: #fdba74; margin-bottom: 6px; font-weight: bold;">Suggested Dimensional Adjustments:</div>`;
            html += `<ul style="margin: 0; padding-left: 18px; display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: #fecaca;">`;
            err.suggestions.forEach(s => {
                html += `<li>${s}</li>`;
            });
            html += `</ul></div>`;
        }
        errMessage.innerHTML = html;
        typesetMath(errMessage);
    } else {
        errMessage.textContent = err ? (err.message || err) : 'An unknown error occurred.';
    }
}

/**
 * Populates reference registry table dynamically.
 */
function populateRegistry() {
    const tbody = document.getElementById('reference-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    const items = Object.entries(window.NOTATION_DATA || {});
    
    items.forEach(([key, item]) => {
        // Resolve plain text variable slug
        const identifier = getPlainIdentifier(key, item);
        
        // Resolve 5D dimensions
        const details = RESOLVED_SYMBOL_MAP[identifier];
        const vec = details ? details.vector : [0, 0, 0, 0, 0];
        
        const tr = document.createElement('tr');
        tr.setAttribute('data-identifier', identifier);
        tr.setAttribute('data-search', `${identifier} ${item.name || ''} ${item.symbol || ''} ${item.unit || item.dimensions || ''}`.toLowerCase());
        
        const tdSymbol = document.createElement('td');
        tdSymbol.className = 'ref-sym';
        tdSymbol.innerHTML = `\\(${item.symbol}\\)`;
        
        const tdName = document.createElement('td');
        tdName.innerHTML = `<strong>${item.name || key}</strong>` +
                           `<div style="font-size: 0.76rem; color: var(--text-muted); line-height: 1.2; margin-top: 2px;">` +
                           `${item.description || ''}</div>`;
        
        const tdDim = document.createElement('td');
        tdDim.className = 'ref-dim';
        tdDim.innerHTML = `\\(${formatVectorToLaTeXColored(vec)}\\)`;
        
        tr.appendChild(tdSymbol);
        tr.appendChild(tdName);
        tr.appendChild(tdDim);
        
        // Mouse click insertion handler
        tr.addEventListener('click', () => {
            const input = document.getElementById('formula-input');
            const start = input.selectionStart;
            const end = input.selectionEnd;
            const text = input.value;
            const before = text.substring(0, start);
            const after = text.substring(end, text.length);
            
            // Auto spacing insertions
            const spaceBefore = (start > 0 && text[start - 1] !== ' ' && text[start - 1] !== '(') ? ' ' : '';
            const spaceAfter = (end < text.length && text[end] !== ' ' && text[end] !== ')') ? ' ' : '';
            
            input.value = before + spaceBefore + identifier + spaceAfter + after;
            input.selectionStart = input.selectionEnd = start + spaceBefore.length + identifier.length;
            input.focus();
            
            // Update analysis
            analyzeFormula(input.value);
        });
        
        tbody.appendChild(tr);
    });
    
    // Typeset the table notation symbols
    typesetMath(tbody);
}

/**
 * Initialize components when DOM is fully loaded.
 */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize dynamic symbol map
    initSymbolMap();
    
    // 2. Populate sidebar registry
    populateRegistry();
    
    // 3. Register click triggers for Quick Load Examples
    document.querySelectorAll('.example-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const formula = btn.getAttribute('data-formula');
            document.getElementById('formula-input').value = formula;
            analyzeFormula(formula);
        });
    });
    
    // 4. Action button triggers analysis
    document.getElementById('solve-btn').addEventListener('click', () => {
        analyzeFormula();
    });

    // Clear button triggers input reset and panels hide
    const clearBtn = document.getElementById('clear-formula-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const input = document.getElementById('formula-input');
            if (input) {
                input.value = '';
                input.focus();
            }
            const outputPanel = document.getElementById('output-panel');
            if (outputPanel) {
                outputPanel.style.display = 'none';
            }
            const errorPanel = document.getElementById('error-panel');
            if (errorPanel) {
                errorPanel.style.display = 'none';
            }
            const inspectorCard = document.getElementById('inspector-card');
            if (inspectorCard) {
                inspectorCard.style.display = 'none';
            }
        });
    }
    
    // 5. Enter key triggers analysis in input box
    const formulaInput = document.getElementById('formula-input');
    if (formulaInput) {
        formulaInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                analyzeFormula();
            }
        });
        
        let debounceTimeout = null;
        formulaInput.addEventListener('input', () => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                analyzeFormula();
            }, 150); // 150ms debounce
        });
    }
    
    // 5a. Register click triggers for math keyboard operators
    document.querySelectorAll('.operator-keyboard .keyboard-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.getElementById('formula-input');
            if (input) {
                const val = btn.getAttribute('data-val');
                const start = input.selectionStart;
                const end = input.selectionEnd;
                const text = input.value;
                const before = text.substring(0, start);
                const after = text.substring(end, text.length);
                
                input.value = before + val + after;
                input.selectionStart = input.selectionEnd = start + val.length;
                input.focus();
                
                // Immediately update analysis
                analyzeFormula(input.value);
            }
        });
    });
    
    // 6. Sidebar search query listener
    const searchInput = document.getElementById('registry-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase().trim();
            const rows = document.querySelectorAll('#reference-tbody tr');
            
            rows.forEach(row => {
                const searchText = row.getAttribute('data-search') || '';
                row.style.display = searchText.includes(query) ? '' : 'none';
            });
        });
    }
    
    // 7. Parser inspector toggle listener
    const inspectorHeader = document.getElementById('inspector-toggle-header');
    if (inspectorHeader) {
        inspectorHeader.addEventListener('click', toggleInspector);
    }
});

// Run registry mappings pre-computation
initSymbolMap();
