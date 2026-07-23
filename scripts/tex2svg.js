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
const svg = new SVG({ fontCache: 'none' });
const html = mathjax.document('', { InputJax: tex, OutputJax: svg });

function convert(latex, isDisplay, color = '#FFD700') {
    try {
        const node = html.convert(latex, {
            display: isDisplay,
            em: 16,
            ex: 8,
            containerWidth: 80 * 16
        });
        let svgHtml = adaptor.innerHTML(node);
        
        // Remove hardcoded MathJax styles if any and inject our theme color
        // The SVG from MathJax with fontCache: 'none' has inline paths
        const styleMatch = svgHtml.match(/style="([^"]*)"/);
        const mjStyle = styleMatch ? styleMatch[1] : '';
        const finalStyle = `color: ${color}; ${mjStyle}`;
        
        if (styleMatch) {
            svgHtml = svgHtml.replace(/style="[^"]*"/, `style="${finalStyle}"`);
        } else {
            svgHtml = svgHtml.replace('<svg ', `<svg style="${finalStyle}" `);
        }
        
        return svgHtml;
    } catch (err) {
        return `<span class="math-error">${err.message}</span>`;
    }
}

// 3. Batch Processing Logic
if (process.argv.length > 2) {
    if (process.argv[2] === '--daemon') {
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout,
            terminal: false
        });
        rl.on('line', (line) => {
            try {
                if (!line.trim()) return;
                const item = JSON.parse(line);
                const svg = convert(item.latex, item.is_display, item.color || '#FFD700');
                console.log(JSON.stringify({ svg: svg }));
            } catch (err) {
                console.log(JSON.stringify({ error: err.message }));
            }
        });
    } else {
        // Single mode (Legacy CLI compatibility)
        const latex = process.argv[2] || '';
        const isDisplay = process.argv[3] === 'display';
        const color = process.argv[4] || '#FFD700';
        process.stdout.write(convert(latex, isDisplay, color));
    }
} else {
    // Batch mode (JSON from stdin)
    let inputData = '';
    process.stdin.on('data', chunk => { inputData += chunk; });
    process.stdin.on('end', () => {
        try {
            const batch = JSON.parse(inputData);
            const results = {};
            for (const [key, item] of Object.entries(batch)) {
                results[key] = convert(item.latex, item.is_display, item.color || '#FFD700');
            }
            process.stdout.write(JSON.stringify(results));
        } catch (err) {
            console.error('Batch Processing Error:', err.message);
            process.exit(1);
        }
    });
}
