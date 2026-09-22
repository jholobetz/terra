/**
 * 🌌 PHYSICS LAB: SymPy CAS Legendre Transformer Controller
 * 
 * Powered by server-side SymPy Computer Algebra System (/physics/api/cas-evaluate).
 * Symbolically evaluates canonical momenta, inverts velocities, calculates Hessian determinants,
 * handles Dirac constraints/singular Lagrangians, and derives Hamilton's equations of motion.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. DOM Elements selection
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
    const latexHessian = document.getElementById('latex-hessian');
    const latexHamiltonian = document.getElementById('latex-hamiltonian');
    const latexEqVelocity = document.getElementById('latex-eq-velocity');
    const latexEqForce = document.getElementById('latex-eq-force');
    const equationsContainer = document.getElementById('equations-container');
    const copyLatexBtn = document.getElementById('copy-latex-btn');
    const conservationText = document.getElementById('conservation-text');
    const dofText = document.getElementById('dof-text');

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

    // 3. Physical Preset Configurations
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
        },
        central_force: {
            coord: 'r, phi',
            velocity: 'dr, dphi',
            params: 'm, V',
            expr: '0.5 * m * (dr^2 + r^2 * dphi^2) - V'
        },
        singular: {
            coord: 'x',
            velocity: 'dx',
            params: 'm, V',
            expr: 'm * dx - V'
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

    // 4. Utility to render math nicely with MathJax 3.x
    function renderMathField(el, latexStr) {
        if (!el) return;
        el.textContent = `\\[ ${latexStr} \\]`;
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([el]).catch(err => {
                console.warn("MathJax typesetting error: ", err);
            });
        }
    }

    // 5. Compute Legendre Transformation via SymPy CAS API
    computeBtn.addEventListener('click', async () => {
        // Clear outputs & error states
        outputError.style.display = 'none';
        outputPlaceholder.style.display = 'none';
        outputContent.style.display = 'none';

        const coordVar = coordVarInput.value.trim();
        const velocityVar = velocityVarInput.value.trim();
        const parameterVars = parameterVarsInput.value.trim();
        const lagrangianExpr = lagrangianExprInput.value.trim();

        // Basic inputs validation
        if (!coordVar || !velocityVar || !lagrangianExpr) {
            showError("Coordinate, velocity, and Lagrangian expression are required.");
            return;
        }

        // Set Loading State on button
        const originalBtnText = computeBtn.innerHTML;
        computeBtn.disabled = true;
        computeBtn.innerHTML = `
            <span style="display: inline-block; animation: spin 1s linear infinite; margin-right: 8px;">⚙️</span>
            Evaluating SymPy CAS Duality...
        `;

        try {
            const response = await fetch('/physics/api/cas-evaluate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    mode: 'legendre',
                    lagrangian: lagrangianExpr,
                    coords: coordVar,
                    velocities: velocityVar,
                    parameters: parameterVars
                })
            });

            if (!response.ok) {
                throw new Error(`CAS server responded with HTTP status ${response.status}`);
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || "Symbolic CAS computation failed.");
            }

            // Case A: Singular Lagrangian (det W = 0)
            if (data.is_singular) {
                showError(data.error || "Singular Lagrangian (det W = 0): primary Dirac constraints detected.");
                outputContent.style.display = 'block';

                // Still render what we have: Lagrangian and Hessian
                renderMathField(latexLagrangian, `L = ${data.lagrangian_latex}`);
                renderMathField(latexMomentum, `\\text{Singular: Velocities are non-invertible}`);
                renderMathField(latexInvertedVel, `\\text{Constraint: } \\det(W) = 0`);
                if (latexHessian && data.hessian) {
                    renderMathField(latexHessian, `W = ${data.hessian.matrix_latex}, \\quad \\det(W) = 0 \\implies \\text{Primary Constraints}`);
                }
                renderMathField(latexHamiltonian, `\\text{Requires Dirac-Bergmann Constraint Analysis}`);
                return;
            }

            // Case B: Non-singular Lagrangian (Standard Legendre transformation)
            
            // 1. Render Input Lagrangian
            renderMathField(latexLagrangian, `L = ${data.lagrangian_latex}`);

            // 2. Render Canonical Momenta
            if (data.momenta && data.momenta.length > 0) {
                const momentaLatex = data.momenta.map(m => m.latex).join(`, \\quad `);
                renderMathField(latexMomentum, momentaLatex);
            }

            // 3. Render Inverted Velocities
            if (data.inverted_velocities && data.inverted_velocities.length > 0) {
                const invLatex = data.inverted_velocities.map(v => v.latex).join(`, \\quad `);
                renderMathField(latexInvertedVel, invLatex);
            }

            // 4. Render Hessian Matrix and Non-Singularity Check
            if (latexHessian && data.hessian) {
                renderMathField(latexHessian, `W = ${data.hessian.matrix_latex}, \\quad \\det(W) = ${data.hessian.det_latex} \\neq 0 \\implies \\text{Regular}`);
            }

            // 5. Render Final Simplified Hamiltonian
            const hLatex = `H = ${data.hamiltonian_latex}`;
            renderMathField(latexHamiltonian, hLatex);
            activeHamiltonianLatex = hLatex;

            // 6. Render Equations of Motion
            if (data.equations_of_motion && data.equations_of_motion.length > 0) {
                if (equationsContainer && data.equations_of_motion.length > 1) {
                    // Multi-variable: render dedicated card for each pair
                    equationsContainer.innerHTML = '';
                    data.equations_of_motion.forEach(eq => {
                        const pairContainer = document.createElement('div');
                        pairContainer.className = 'math-display-container';
                        pairContainer.innerHTML = `
                            <div class="math-label-bar">
                                <span class="math-label">Coordinate \\(${eq.coord}\\) Canonical Flow:</span>
                            </div>
                            <div class="math-box" style="margin-bottom: 8px;">
                                <div class="math-render-field">\\[ ${eq.dq_dt_latex} \\]</div>
                            </div>
                            <div class="math-box">
                                <div class="math-render-field">\\[ ${eq.dp_dt_latex} \\]</div>
                            </div>
                        `;
                        equationsContainer.appendChild(pairContainer);
                    });
                    if (window.MathJax && window.MathJax.typesetPromise) {
                        window.MathJax.typesetPromise([equationsContainer]);
                    }
                } else {
                    // Single degree of freedom
                    const eq = data.equations_of_motion[0];
                    renderMathField(latexEqVelocity, eq.dq_dt_latex);
                    renderMathField(latexEqForce, eq.dp_dt_latex);
                }
            }

            // 7. Render Phase Space Topology & Conservation Laws
            const numDof = (data.equations_of_motion || []).length || 1;
            if (dofText) {
                const phaseDim = numDof * 2;
                dofText.innerHTML = `The system possesses <strong>${numDof} degree(s) of freedom</strong>. In the Lagrangian formulation, this is represented by the tangent bundle \\(TQ\\) spanned by generalized velocities. In the Hamiltonian formulation, this is mapped to a <strong>${phaseDim}D Symplectic Phase Space Manifold</strong> spanned by conjugate coordinate-momentum pairs \\((q_i, p_i)\\).`;
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise([dofText]);
                }
            }

            if (conservationText && data.conservation) {
                conservationText.innerHTML = data.conservation.summary;
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise([conservationText]);
                }
            }

            // Reveal Result Container
            outputContent.style.display = 'block';

        } catch (error) {
            showError(error.message);
        } finally {
            computeBtn.disabled = false;
            computeBtn.innerHTML = originalBtnText;
        }
    });

    function showError(msg) {
        errorMessage.textContent = msg;
        outputError.style.display = 'block';
        outputPlaceholder.style.display = 'none';
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
