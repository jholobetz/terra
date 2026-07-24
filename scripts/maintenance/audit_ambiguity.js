/**
 * 🪐 Physics Lab - Formula Variable Ambiguity Auditor
 * 
 * Invokes frontend parsing rules (extractAllMathTokens and detectDomainFromLatex)
 * directly against the database formulas to ensure all variables resolve without ambiguity.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

// Mock browser environment for equation_explainer.js loading
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

// Load actual frontend script (prefer compiled dist bundle)
let jsPath = path.resolve(__dirname, '../../public/js/dist/equation_explainer.bundle.js');
if (!fs.existsSync(jsPath)) {
    jsPath = path.resolve(__dirname, '../../public/js/equation_explainer.js');
}
let jsCode;
try {
    jsCode = fs.readFileSync(jsPath, 'utf8');
} catch (err) {
    console.error(`Error: Could not read frontend script at ${jsPath}`);
    process.exit(1);
}

// Execute in VM to export EquationExplainer
const context = {
    window: global.window,
    document: global.document,
    localStorage: global.localStorage,
    console: console,
    URLSearchParams: URLSearchParams
};
vm.createContext(context);
try {
    const script = jsCode + '\nthis.EquationExplainer = EquationExplainer;';
    vm.runInContext(script, context);
} catch (err) {
    console.error('Error: Failed to evaluate equation_explainer.js in VM context:', err);
    process.exit(1);
}

const EquationExplainer = context.EquationExplainer;
if (!EquationExplainer) {
    console.error('Error: EquationExplainer global not found after VM execution.');
    process.exit(1);
}

// Locate sharded formulas database
const contentDir = path.resolve(__dirname, '../../app/config/content');
const formulasDir = path.join(contentDir, 'formulas');
let formulaRegistry = {};

try {
    if (fs.existsSync(formulasDir)) {
        const files = fs.readdirSync(formulasDir);
        for (const file of files) {
            if (file.startsWith('shard_') && file.endsWith('.json')) {
                const shardData = JSON.parse(fs.readFileSync(path.join(formulasDir, file), 'utf8'));
                Object.assign(formulaRegistry, shardData);
            }
        }
    } else {
        const monolithicPath = path.join(contentDir, 'formulas.json');
        if (fs.existsSync(monolithicPath)) {
            formulaRegistry = JSON.parse(fs.readFileSync(monolithicPath, 'utf8'));
        }
    }
} catch (err) {
    console.error('Error: Failed to load database formulas:', err);
    process.exit(1);
}

console.log(`🔍 Loaded ${Object.keys(formulaRegistry).length} equations. Initiating ambiguity audit...`);

let issuesFound = 0;
const report = [];

for (const [slug, formula] of Object.entries(formulaRegistry)) {
    const latex = formula.formula_latex || '';
    if (!latex) continue;

    // 1. Detect Domain
    const domain = EquationExplainer.detectDomainFromLatex(latex);
    
    // 2. Normalize Semantic Variables (Keys without delimiters)
    const semanticVars = formula.semantic_variables || {};
    const normalizedSemantic = {};
    for (const [key, val] of Object.entries(semanticVars)) {
        const cleanKey = key.trim()
                            .replace(/^\\\(/, '')
                            .replace(/\\\)$/, '')
                            .replace(/^\\\[/, '')
                            .replace(/\\\]$/, '')
                            .replace(/^\$\$/, '')
                            .replace(/\$\$$/, '')
                            .replace(/^\$/, '')
                            .replace(/\$/, '')
                            .trim();
        normalizedSemantic[cleanKey] = val;
    }

    // 3. Extract Tokens
    const tokens = EquationExplainer.extractAllMathTokens(latex, normalizedSemantic);
    const ambiguousSymbols = [];

    // 4. Check each token for ambiguity
    for (const tok of tokens) {
        const symbol = tok.symbol;

        // Skip integration boundaries, differentials, and modifiers
        if (tok.type === 'integration_boundary' || tok.type === 'differential_operator' || tok.type === 'modifier') {
            continue;
        }

        // Skip if explicitly overridden in the database
        if (normalizedSemantic[symbol]) {
            continue;
        }

        // Check dictionary definitions
        const dictEntry = EquationExplainer.physicsDictionary[symbol];
        if (dictEntry) {
            // If the entry has alternatives
            if (dictEntry.alternatives && dictEntry.alternatives.length > 0) {
                // Check if the current domain has a matching alternative
                const hasMatchingDomain = dictEntry.domain === domain || 
                    dictEntry.alternatives.some(alt => alt.domain === domain);
                
                if (!hasMatchingDomain) {
                    ambiguousSymbols.push({
                        symbol,
                        defaultName: dictEntry.name,
                        alternatives: dictEntry.alternatives.map(alt => `${alt.name} (${alt.domain})`)
                    });
                }
            }
        }
    }

    if (ambiguousSymbols.length > 0) {
        issuesFound++;
        report.push({
            slug,
            title: formula.title || slug,
            latex,
            domain: domain || 'unclassified',
            ambiguousSymbols
        });
    }
}

// Print results
if (report.length > 0) {
    console.log(`\n⚠️ AMBIGUITY WARNING: Flagged ${report.length} equations with ambiguous variables:`);
    for (const issue of report) {
        console.log(`\n  📌 Formula: ${issue.title} [slug: ${issue.slug}]`);
        console.log(`     LaTeX:  ${issue.latex}`);
        console.log(`     Domain: ${issue.domain}`);
        console.log(`     Ambiguous Variables:`);
        for (const sym of issue.ambiguousSymbols) {
            console.log(`       - Symbol: ${sym.symbol}`);
            console.log(`         Fallback:     ${sym.defaultName}`);
            console.log(`         Alternatives: ${sym.alternatives.join(', ')}`);
        }
    }
    console.log(`\n❌ Validation Failed: ${issuesFound} equations have ambiguous definitions.`);
    process.exit(1);
} else {
    console.log('\n✅ SHIELD SECURE: All variables in all sharded formulas resolved unambiguously.');
    process.exit(0);
}
