const fs = require('fs');
const path = require('path');

const jsPath = path.join(__dirname, '../../public/js/equation_explainer.js');
const jsCode = fs.readFileSync(jsPath, 'utf8');

// Mock browser globals to run the script in a VM-like context
global.window = {
    PHYSICS_CONSTANTS: {}
};
global.document = {
    readyState: 'loading',
    addEventListener: () => {},
    getElementById: () => null
};
global.localStorage = {
    getItem: () => null
};

// Evaluate the script
eval(jsCode + "\nmodule.exports = EquationExplainer;");

const EquationExplainer = module.exports;

const exported = {
    variableDictionary: EquationExplainer.variableDictionary,
    physicsDictionary: EquationExplainer.physicsDictionary,
    fallbackBinders: EquationExplainer.fallbackBinders
};

console.log(JSON.stringify(exported, null, 2));
