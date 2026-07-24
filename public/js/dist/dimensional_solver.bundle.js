(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.DimensionalSolver = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {
const SYMBOL_MAP = {
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
function addDimensions(v1, v2) {
    return v1.map((val, idx) => val + v2[idx]);
}
function subtractDimensions(v1, v2) {
    return v1.map((val, idx) => val - v2[idx]);
}
function multiplyDimension(v1, scalar) {
    return v1.map(val => val * scalar);
}
function formatDimensionVector(v) {
    const units = ['M', 'L', 'T', 'I', 'Θ'];
    const parts = [];
    v.forEach((val, idx) => {
        if (val !== 0) {
            parts.push(val === 1 ? units[idx] : `${units[idx]}^${val}`);
        }
    });
    return parts.length > 0 ? parts.join('·') : 'Dimensionless [1]';
}
const DimensionalSolver = {
    SYMBOL_MAP,
    addDimensions,
    subtractDimensions,
    multiplyDimension,
    formatDimensionVector,
    init() {
        if (typeof window !== 'undefined') {
            window.DimensionalSolver = this;
        }
    }
};
if (typeof window !== 'undefined') {
    window.DimensionalSolver = DimensionalSolver;
}
    return typeof DimensionalSolver !== 'undefined' ? DimensionalSolver : {};
}));