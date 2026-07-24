#!/usr/bin/env node
/**
 * 🪐 Project Terra - Frontend ES Module Bundler & Minifier
 * Combines modular ES scripts from public/src/js into production-ready assets in public/js/dist/.
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '../../');
const SRC_DIR = path.join(PROJECT_ROOT, 'public/src/js');
const DIST_DIR = path.join(PROJECT_ROOT, 'public/js/dist');

// Ensure output dist directory exists
if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
}

function bundleFile(srcRelPath, distFileName, globalExportName) {
    const srcPath = path.join(SRC_DIR, srcRelPath);
    if (!fs.existsSync(srcPath)) {
        console.error(`❌ Error: Source file not found at ${srcPath}`);
        return;
    }

    let code = fs.readFileSync(srcPath, 'utf8');

    // Inline relative module imports (simple static resolver for ES modules)
    const importRegex = /import\s+\{([^}]+)\}\s+from\s+['"]([^'"]+)['"];?/g;
    code = code.replace(importRegex, (match, imports, relPath) => {
        const importFile = path.resolve(path.dirname(srcPath), relPath);
        if (fs.existsSync(importFile)) {
            let importCode = fs.readFileSync(importFile, 'utf8');
            // Remove export statements
            importCode = importCode.replace(/export\s+const\s+/g, 'const ')
                                   .replace(/export\s+function\s+/g, 'function ')
                                   .replace(/export\s+default\s+/g, '');
            return `\n/* Inlined from ${path.basename(importFile)} */\n` + importCode;
        }
        return match;
    });

    // Strip remaining export statements for browser IIFE format
    code = code.replace(/export\s+const\s+/g, 'const ')
               .replace(/export\s+function\s+/g, 'function ')
               .replace(/export\s+default\s+/g, '');

    // Wrap in UMD / IIFE enclosure
    const bundledCode = `(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        module.exports = factory();
    } else {
        root.${globalExportName} = factory();
    }
}(typeof self !== 'undefined' ? self : this, function() {
${code}
    return typeof ${globalExportName} !== 'undefined' ? ${globalExportName} : {};
}));`;

    // Simple minification (strip comments and compress multi-lines)
    const minifiedCode = bundledCode
        .replace(/\/\*[\s\S]*?\*\/|([^:]|^)\/\/.*/g, '$1') // strip comments
        .replace(/\n\s*\n/g, '\n') // strip blank lines
        .trim();

    const distPath = path.join(DIST_DIR, distFileName);
    fs.writeFileSync(distPath, minifiedCode, 'utf8');

    const origSize = (fs.statSync(srcPath).size / 1024).toFixed(1);
    const bundledSize = (fs.statSync(distPath).size / 1024).toFixed(1);
    console.log(`  ✓ Bundled [${srcRelPath}] -> public/js/dist/${distFileName} (${origSize} KB -> ${bundledSize} KB)`);
}

console.log('⚡ Building Production Frontend JS Bundles...');
bundleFile('tools/equation_explainer.js', 'equation_explainer.bundle.js', 'EquationExplainer');
bundleFile('tools/dimensional_solver.js', 'dimensional_solver.bundle.js', 'DimensionalSolver');
console.log('✓ Frontend Bundling Complete!');
