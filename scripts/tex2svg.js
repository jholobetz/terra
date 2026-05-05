/*************************************************************************
 *  tex2svg.js - MathJax 3 SSR Utility for Physics Lab
 *  BATCH MODE: Processes multiple formulas in one process spawn.
 *************************************************************************/

const { mathjax } = require('mathjax-full/js/mathjax.js');
const { TeX } = require('mathjax-full/js/input/tex.js');
const { SVG } = require('mathjax-full/js/output/svg.js');
const { liteAdaptor } = require('mathjax-full/js/adaptors/liteAdaptor.js');
const { RegisterHTMLHandler } = require('mathjax-full/js/handlers/html.js');
const { AllPackages } = require('mathjax-full/js/input/tex/AllPackages.js');
const fs = require('fs');

// 1. Setup Adaptor and Handler
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);

// 2. Initialize MathJax
const tex = new TeX({ 
    packages: AllPackages.filter(p => p !== 'bussproofs' && p !== 'physics')
});
const svg = new SVG({ fontCache: 'local' });
const html = mathjax.document('', { InputJax: tex, OutputJax: svg });

function convert(latex, isDisplay) {
    try {
        const node = html.convert(latex, {
            display: isDisplay,
            em: 16,
            ex: 8,
            containerWidth: 80 * 16
        });
        let svgHtml = adaptor.innerHTML(node);
        const styleMatch = svgHtml.match(/style="([^"]*)"/);
        const mjStyle = styleMatch ? styleMatch[1] : '';
        const finalStyle = `color: #FFD700; ${mjStyle}`;
        return svgHtml.replace(/style="[^"]*"/, `style="${finalStyle}"`);
    } catch (err) {
        return `<span class="math-error">${err.message}</span>`;
    }
}

// 3. Batch Processing Logic
if (process.argv.length > 2) {
    // Single mode (Legacy CLI compatibility)
    const latex = process.argv[2] || '';
    const isDisplay = process.argv[3] === 'display';
    process.stdout.write(convert(latex, isDisplay));
} else {
    // Batch mode (JSON from stdin)
    let inputData = '';
    process.stdin.on('data', chunk => { inputData += chunk; });
    process.stdin.on('end', () => {
        try {
            const batch = JSON.parse(inputData);
            const results = {};
            for (const [key, item] of Object.entries(batch)) {
                results[key] = convert(item.latex, item.is_display);
            }
            process.stdout.write(JSON.stringify(results));
        } catch (err) {
            console.error('Batch Processing Error:', err.message);
            process.exit(1);
        }
    });
}
