/**
 * 🔬 PHYSICS LAB: Interactive Equation Explainer (ES Module)
 * Connects analytical tools together and performs real-time variable deconstruction.
 */

import { variableDictionary, fallbackBinders, symbolAliases } from '../core/physics_dictionary.js';
import { detectDomainFromLatex, extractAllMathTokens } from '../core/tex_parser.js';

export const EquationExplainer = {
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

// Auto-initialize when loaded in browser window
if (typeof window !== 'undefined') {
    window.EquationExplainer = EquationExplainer;
}
