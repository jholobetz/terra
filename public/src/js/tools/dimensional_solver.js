/**
 * 🪐 Cosmic Obsidian - Dimensional Solver & Algebraic Consistency Engine (ES Module)
 */

import { SYMBOL_MAP, addDimensions, subtractDimensions, multiplyDimension, formatDimensionVector } from '../core/dimensional_engine.js';

export const DimensionalSolver = {
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

// Auto-initialize when loaded in browser window
if (typeof window !== 'undefined') {
    window.DimensionalSolver = DimensionalSolver;
}
