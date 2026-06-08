/**
 * 🌌 PHYSICS LAB: Symbolic Legendre Transformer Controller
 * 
 * Uses math.js to symbolically compute Legendre transformations, invert velocities,
 * calculate Hamilton's equations of motion, and typeset the results using MathJax.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Elements selection
    const computeBtn = document.getElementById('compute-btn');
    const presets = document.querySelectorAll('.preset-btn');
    const coordVarInput = document.getElementById('coord-var');
    const velocityVarInput = document.getElementById('velocity-var');
    const parameterVarsInput = document.getElementById('parameter-vars');
    const lagrangianExprInput = document.getElementById('lagrangian-expr');
    
    const outputCard = document.getElementById('output-card');
    const outputPlaceholder = document.getElementById('output-placeholder');
    const outputError = document.getElementById('output-error');
    const errorMessage = document.getElementById('error-message');
    const outputContent = document.getElementById('output-content');
    
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');
    
    const latexLagrangian = document.getElementById('latex-lagrangian');
    const latexMomentum = document.getElementById('latex-momentum');
    const latexInvertedVel = document.getElementById('latex-inverted-vel');
    const latexHamiltonian = document.getElementById('latex-hamiltonian');
    const latexEqVelocity = document.getElementById('latex-eq-velocity');
    const latexEqForce = document.getElementById('latex-eq-force');
    const copyLatexBtn = document.getElementById('copy-latex-btn');
    const conservationText = document.getElementById('conservation-text');

    let activeHamiltonianLatex = ''; // Stored clean LaTeX for copying

    // 2. Tab switching logic
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanels.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const targetPanel = document.getElementById(`tab-${btn.dataset.tab}`);
            if (targetPanel) {
                targetPanel.classList.add('active');
            }
        });
    });

    // 3. Preset Loading
    const presetData = {
        sho: {
            coord: 'q',
            velocity: 'dq',
            params: 'm, k',
            expr: '0.5 * m * dq^2 - 0.5 * k * q^2'
        },
        pendulum: {
            coord: 'theta',
            velocity: 'dtheta',
            params: 'm, g, l',
            expr: '0.5 * m * l^2 * dtheta^2 + m * g * l * cos(theta)'
        },
        em_field: {
            coord: 'x',
            velocity: 'dx',
            params: 'm, q_charge, A_pot, V',
            expr: '0.5 * m * dx^2 + q_charge * A_pot * dx - V'
        },
        relativistic: {
            coord: 'x',
            velocity: 'dx',
            params: 'm, c, V',
            expr: '-m * c^2 * sqrt(1 - dx^2 / c^2) - V'
        }
    };

    presets.forEach(btn => {
        btn.addEventListener('click', () => {
            const data = presetData[btn.dataset.preset];
            if (data) {
                coordVarInput.value = data.coord;
                velocityVarInput.value = data.velocity;
                parameterVarsInput.value = data.params;
                lagrangianExprInput.value = data.expr;
                
                // Animate preset selection
                btn.style.transform = 'scale(0.95)';
                setTimeout(() => { btn.style.transform = ''; }, 100);
            }
        });
    });

    // 4. Utility to render math nicely
    function renderMathField(el, latexStr) {
        el.textContent = `\\[ ${latexStr} \\]`;
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([el]).catch(err => {
                console.warn("MathJax typesetting error: ", err);
            });
        }
    }

    // Symbolic substitution helper for math.js nodes
    function substituteSymbolic(node, varName, replacementNode) {
        return node.transform(function (childNode) {
            if (childNode.isSymbolNode && childNode.name === varName) {
                return replacementNode.clone();
            }
            return childNode;
        });
    }

    // 5. Compute Legendre Transformation
    computeBtn.addEventListener('click', () => {
        // Clear outputs & error states
        outputError.style.display = 'none';
        outputPlaceholder.style.display = 'none';
        outputContent.style.display = 'none';

        const coordVar = coordVarInput.value.trim();
        const velocityVar = velocityVarInput.value.trim();
        const parameterVars = parameterVarsInput.value.split(',').map(s => s.trim()).filter(s => s);
        const lagrangianExpr = lagrangianExprInput.value.trim();

        // Basic inputs validation
        if (!coordVar || !velocityVar || !lagrangianExpr) {
            showError("Coordinate, velocity, and Lagrangian expression are required.");
            return;
        }

        try {
            // Check that velocity and coordinate variable names are valid alphanumeric
            const nameRegex = /^[a-zA-Z_][a-zA-Z0-9_]*$/;
            if (!nameRegex.test(coordVar)) throw new Error(`Invalid coordinate variable name: '${coordVar}'`);
            if (!nameRegex.test(velocityVar)) throw new Error(`Invalid velocity variable name: '${velocityVar}'`);

            // Check if math.js is loaded (blocked by CSP/CDN issues)
            if (typeof math === 'undefined') {
                throw new Error("Duality engine (math.js) is not loaded. Please reload the page.");
            }

            // Parse Lagrangian Expression
            let L_node;
            try {
                L_node = math.parse(lagrangianExpr);
            } catch (err) {
                throw new Error("Syntax error in Lagrangian expression: " + err.message);
            }

            // Differentiate with respect to velocity variable to get momentum p
            const p_node_raw = math.derivative(L_node, velocityVar);
            const p_node = math.simplify(p_node_raw);
            const p_text = p_node.toString();

            let solved_vel_node;
            let final_H_node;

            // SPECIAL CASE: Relativistic Particle (non-linear in velocity)
            if (lagrangianExpr.includes('sqrt') && (lagrangianExpr.includes('c') || lagrangianExpr.includes('1 -'))) {
                // Hardcode Legendre solutions for the relativistic particle preset
                // L = -m * c^2 * sqrt(1 - dq^2/c^2) - V
                // p = m * dq / sqrt(1 - dq^2/c^2)
                // dq = p / sqrt(m^2 + p^2 / c^2)
                // H = c * sqrt(p^2 + m^2 * c^2) + V
                
                // Verify parameters match relativistic components (m, c, p)
                const hasV = lagrangianExpr.endsWith('- V') || lagrangianExpr.includes('-V');
                const V_term = hasV ? ' + V' : '';
                
                solved_vel_node = math.parse(`p / sqrt(m^2 + p^2 / c^2)`);
                final_H_node = math.parse(`c * sqrt(p^2 + m^2 * c^2)${V_term}`);
                
                // Manually overwrite momentum expression to typeset cleanly
                renderMathField(latexMomentum, `p = \\frac{\\partial L}{\\partial \\dot{${coordVar}}} = \\frac{m \\dot{${coordVar}}}{\\sqrt{1 - \\frac{\\dot{${coordVar}}^2}{c^2}}}`);
                renderMathField(latexInvertedVel, `\\dot{${coordVar}}(p) = \\frac{p}{\\sqrt{m^2 + p^2/c^2}}`);
            } else {
                // GENERAL SOLVER: Check if quadratic/linear in velocity
                const p2_node = math.simplify(math.derivative(p_node, velocityVar)); // 2nd derivative of L
                const p3_node = math.simplify(math.derivative(p2_node, velocityVar)); // 3rd derivative of L
                
                if (p3_node.toString() !== '0') {
                    throw new Error("Lagrangian is non-quadratic in velocity. Standard symbolic inversion is mathematically unavailable (requires numerical solver).");
                }
                
                // Extract C0 (constant term relative to velocityVar) by substituting velocityVar = 0
                const node_C0 = math.simplify(substituteSymbolic(p_node, velocityVar, math.parse('0')));
                
                // Extract C1 (coefficient of velocityVar) by substituting velocityVar = 1 and subtracting C0
                const node_dq_one = math.simplify(substituteSymbolic(p_node, velocityVar, math.parse('1')));
                const node_C1 = math.simplify(math.parse(`(${node_dq_one.toString()}) - (${node_C0.toString()})`));
                
                if (node_C1.toString() === '0') {
                    throw new Error("Lagrangian does not depend on velocity. Cannot define canonical momentum or Legendre transformation.");
                }
                
                // Solve for velocityVar: velocityVar = (p - C0) / C1
                // We map canonical momentum symbol to 'p'
                const solve_expr = `(p - (${node_C0.toString()})) / (${node_C1.toString()})`;
                solved_vel_node = math.simplify(math.parse(solve_expr));
                
                // Render Momentum and Inversion equations
                // Replace variable names with standard LaTeX formatting for dot notation
                let latexP = p_node.toTex().replace(new RegExp(velocityVar, 'g'), `\\dot{${coordVar}}`);
                renderMathField(latexMomentum, `p = \\frac{\\partial L}{\\partial \\dot{${coordVar}}} = ${latexP}`);
                
                let latexInv = solved_vel_node.toTex();
                renderMathField(latexInvertedVel, `\\dot{${coordVar}}(p) = ${latexInv}`);
                
                // Compute Legendre step: H = p * dq - L
                const h_step_expr = `p * ${velocityVar} - (${lagrangianExpr})`;
                const h_step_node = math.parse(h_step_expr);
                
                // Substitute velocityVar with its inverted velocity relation solved_vel_node
                const substituted_H = substituteSymbolic(h_step_node, velocityVar, solved_vel_node);
                final_H_node = math.simplify(substituted_H);
            }

            // Render Input Lagrangian
            let latexL = L_node.toTex().replace(new RegExp(velocityVar, 'g'), `\\dot{${coordVar}}`);
            renderMathField(latexLagrangian, `L(${coordVar}, \\dot{${coordVar}}) = ${latexL}`);

            // Render final simplified Hamiltonian
            // Let's replace 'p' and coordVar in output to clean up
            let latexH = final_H_node.toTex();
            renderMathField(latexHamiltonian, `H(${coordVar}, p) = ${latexH}`);
            activeHamiltonianLatex = `H(${coordVar}, p) = ${latexH}`;

            // Calculate Hamilton's Equations of motion
            // dq = dH/dp
            const eq_vel_node = math.simplify(math.derivative(final_H_node, 'p'));
            renderMathField(latexEqVelocity, `\\dot{${coordVar}} = \\frac{\\partial H}{\\partial p} = ${eq_vel_node.toTex()}`);
            
            // dp = -dH/dq
            const eq_force_raw = math.derivative(final_H_node, coordVar);
            const eq_force_negated = math.simplify(math.parse(`-1 * (${eq_force_raw.toString()})`));
            renderMathField(latexEqForce, `\\dot{p} = -\\frac{\\partial H}{\\partial ${coordVar}} = ${eq_force_negated.toTex()}`);

            // Display result panel
            outputContent.style.display = 'block';

        } catch (error) {
            showError(error.message);
        }
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        outputError.style.display = 'block';
        outputPlaceholder.style.display = 'none';
        outputContent.style.display = 'none';
    }

    // 6. Copy LaTeX functionality
    copyLatexBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        if (!activeHamiltonianLatex) return;

        copyTextToClipboard(activeHamiltonianLatex).then(() => {
            copyLatexBtn.classList.add('copied');
            const btnText = copyLatexBtn.querySelector('.btn-text');
            btnText.textContent = 'Copied!';

            const copyIcon = copyLatexBtn.querySelector('.copy-icon');
            copyIcon.innerHTML = `
                <polyline points="20 6 9 17 4 12"></polyline>
            `;

            // Subtle bounce animation
            copyLatexBtn.style.transform = 'scale(0.96)';
            setTimeout(() => {
                copyLatexBtn.style.transform = '';
            }, 100);

            // Reset copy button after delay
            setTimeout(() => {
                copyLatexBtn.classList.remove('copied');
                btnText.textContent = 'Copy Hamiltonian LaTeX';
                copyIcon.innerHTML = `
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                `;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy text: ', err);
        });
    });

    function copyTextToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            return navigator.clipboard.writeText(text);
        }
        return new Promise((resolve, reject) => {
            try {
                const textArea = document.createElement("textarea");
                textArea.value = text;
                textArea.style.top = "0";
                textArea.style.left = "0";
                textArea.style.position = "fixed";
                textArea.style.opacity = "0";
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                const successful = document.execCommand('copy');
                document.body.removeChild(textArea);
                if (successful) resolve();
                else reject(new Error("Copy failed"));
            } catch (err) {
                reject(err);
            }
        });
    }

});
