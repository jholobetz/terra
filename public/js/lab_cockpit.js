/**
 * 🌌 PHYSICS LAB: The Unified Physics Cockpit Engine (lab_cockpit.js)
 * Phase 2.3 - The System Crucible & Multi-Prism Transformation Chamber
 * 
 * Coordinates the live 60fps high-DPI numerical physics simulation, server-side
 * SymPy CAS evaluations, and real-time prism switching across 5 theoretical formalisms:
 *   1. Variational & Phase Mechanics (Lagrangian, Legendre Duality, Hessian, Hamiltonian)
 *   2. Spacetime Symmetries & Noether Currents (Continuous Lie Groups & Perturbations)
 *   3. Ehrenfest Quantum Correspondence (Wave Packet Tunneling & Semiclassical Limits)
 *   4. Rosetta Formalisms (Gibbs Vectors, Relativistic Tensors, Cartan Differential Forms)
 *   5. Dimensional Homogeneity & Buckingham-π (SI Base Units & Invariants)
 */

(function() {
    'use strict';

    // =========================================================================
    // 1. PHYSICAL SYSTEMS CATALOG (THE CRUCIBLE)
    // =========================================================================
    const CRUCIBLE_SYSTEMS = {
        sho: {
            id: 'sho',
            name: 'Harmonic Oscillator',
            icon: '🌀',
            tag: 'Quadratic V(q)',
            coords: 'q',
            velocities: 'dq',
            params: 'm, k',
            lagrangianExpr: '0.5 * m * dq^2 - 0.5 * k * q^2',
            latexLagrangian: '\\mathcal{L} = \\frac{1}{2}m\\dot{q}^2 - \\frac{1}{2}\\class{scrub-token scrub-k}{k}q^2',
            sliderParam: { name: 'Spring Stiffness (k)', min: 0.2, max: 3.0, step: 0.1, default: 1.0, unit: ' N/m' },
            deepLink: '/physics/legendre-transformer?preset=sho',
            deepLinkText: 'Inspect in Analytical Mechanics Workbench →',
            rosetta: {
                gibbs: '\\mathbf{F} = -\\class{scrub-token scrub-k}{k}\\mathbf{x} \\quad\\Longrightarrow\\quad m\\ddot{\\mathbf{x}} + \\class{scrub-token scrub-k}{k}\\mathbf{x} = 0',
                tensor: 'm\\frac{d^2 x^i}{dt^2} + k\\delta^i_j x^j = 0',
                forms: 'd\\mathbf{p} + k\\mathbf{q} \\wedge dt = 0 \\quad (\\text{Symplectic 2-Form } \\omega = dp \\wedge dq)'
            },
            symmetries: {
                continuous: 'Time Translation (t → t + ε)',
                conserved: 'Total Energy (Hamiltonian H = T + V)',
                formula: '\\frac{dH}{dt} = -\\frac{\\partial \\mathcal{L}}{\\partial t} = 0'
            },
            quantum: {
                equation: '-\\frac{\\hbar^2}{2m}\\frac{d^2\\psi}{dx^2} + \\frac{1}{2}\\class{scrub-token scrub-k}{k} x^2\\psi = E\\psi',
                groundEnergy: 'E_0 = \\frac{1}{2}\\hbar\\omega \\quad (\\omega = \\sqrt{k/m})',
                wigner: 'Concentric elliptic phase-space contours'
            },
            dimensions: {
                latex: 'E = \\frac{1}{2}m v^2 + \\frac{1}{2}\\class{scrub-token scrub-k}{k} x^2',
                quantity: 'Energy / Work / Hamiltonian',
                powers: { M: 1, L: 2, T: -2 }
            }
        },
        relativistic: {
            id: 'relativistic',
            name: 'Relativistic Particle',
            icon: '🪐',
            tag: 'Lorentz Invariant',
            coords: 'x',
            velocities: 'dx',
            params: 'm, c, V',
            lagrangianExpr: '-m * c^2 * sqrt(1 - dx^2 / c^2) - V',
            latexLagrangian: '\\mathcal{L} = -mc^2\\sqrt{1 - \\class{scrub-token scrub-v}{\\dot{x}}^2/c^2} - V(x)',
            sliderParam: { name: 'Velocity Ratio (v / c)', min: 0.1, max: 0.98, step: 0.02, default: 0.60, unit: ' c' },
            deepLink: '/physics/legendre-transformer?preset=relativistic',
            deepLinkText: 'Evaluate Relativistic Hessian in SymPy CAS →',
            rosetta: {
                gibbs: '\\mathbf{p} = \\frac{m\\class{scrub-token scrub-v}{\\mathbf{v}}}{\\sqrt{1 - v^2/c^2}}, \\quad \\mathbf{F} = \\frac{d\\mathbf{p}}{dt}',
                tensor: 'P^\\mu = m U^\\mu = \\left(\\frac{E}{c}, \\mathbf{p}\\right), \\quad P_\\mu P^\\mu = -m^2 c^2',
                forms: 'd(\\star P) = 0 \\quad (\\text{Minkowski Metric } \\eta_{\\mu\\nu} = \\text{diag}(-1,1,1,1))'
            },
            symmetries: {
                continuous: 'Poincaré Invariance (Translations + Lorentz Boosts SO(3,1))',
                conserved: 'Relativistic 4-Momentum P^μ and Energy-Momentum Invariant',
                formula: 'E^2 - p^2 c^2 = m^2 c^4'
            },
            quantum: {
                equation: '(\\Box - m^2 c^2/\\hbar^2)\\psi = 0 \\quad (\\text{Klein-Gordon / Dirac Equation})',
                groundEnergy: 'E = \\sqrt{p^2 c^2 + m^2 c^4}',
                wigner: 'Relativistically squeezed hyperbolic light cone flow'
            },
            dimensions: {
                latex: 'E^2 = p^2 c^2 + m^2 c^4',
                quantity: 'Energy / Relativistic Mass-Energy',
                powers: { M: 1, L: 2, T: -2 }
            }
        },
        chaos: {
            id: 'chaos',
            name: 'Double Pendulum',
            icon: '⏳',
            tag: 'Chaotic Attractor',
            coords: 'theta1, theta2',
            velocities: 'w1, w2',
            params: 'm1, m2, l1, l2, g',
            lagrangianExpr: '0.5*(m1+m2)*l1^2*w1^2 + 0.5*m2*l2^2*w2^2 + m2*l1*l2*w1*w2*cos(theta1-theta2) + (m1+m2)*g*l1*cos(theta1) + m2*g*l2*cos(theta2)',
            latexLagrangian: '\\mathcal{L} = \\frac{1}{2}(m_1+m_2)l_1^2\\dot{\\theta}_1^2 + \\frac{1}{2}m_2 \\class{scrub-token scrub-l2}{l_2}^2\\dot{\\theta}_2^2 + m_2 l_1 \\class{scrub-token scrub-l2}{l_2} \\dot{\\theta}_1\\dot{\\theta}_2\\cos(\\theta_1-\\theta_2) - V',
            sliderParam: { name: 'Arm Length Ratio (l₂ / l₁)', min: 0.2, max: 2.0, step: 0.05, default: 1.0, unit: '' },
            deepLink: '/physics/legendre-transformer?preset=pendulum',
            deepLinkText: 'Analyze Nonlinear Coupling in CAS Workbench →',
            rosetta: {
                gibbs: '\\boldsymbol{\\tau} = \\mathbf{r}_1 \\times (m_1 \\mathbf{g}) + \\mathbf{r}_2 \\times (m_2 \\mathbf{g})',
                tensor: 'M_{ij}(\\theta)\\ddot{\\theta}^j + C_{ijk}(\\theta)\\dot{\\theta}^j\\dot{\\theta}^k + G_i(\\theta) = 0',
                forms: 'd\\omega = 0 \\quad (\\text{Poincaré Recurrence on Symplectic Manifold } T^*T^2)'
            },
            symmetries: {
                continuous: 'Time Translation Invariance (Autonomous Non-Dissipative)',
                conserved: 'Total Mechanical Energy E = T + V (Positive Lyapunov Exponent λ > 0)',
                formula: '\\frac{dE}{dt} = 0, \\quad \\Delta \\theta(t) \\sim \\Delta \\theta(0) e^{\\lambda t}'
            },
            quantum: {
                equation: '\\hat{H}\\Psi = E_n\\Psi \\quad (\\text{Wigner-Dyson Level Repulsion / Quantum Chaos})',
                groundEnergy: 'P(s) = \\frac{\\pi}{2} s \\exp\\left(-\\frac{\\pi}{4} s^2\\right)',
                wigner: 'Ergodic fractal phase space scarring'
            },
            dimensions: {
                latex: 'E = \\frac{1}{2} m \\class{scrub-token scrub-l2}{l}^2 \\dot{\\theta}^2 + m g \\class{scrub-token scrub-l2}{l} (1 - \\cos\\theta)',
                quantity: 'Energy / Work / Hamiltonian',
                powers: { M: 1, L: 2, T: -2 }
            }
        },
        em_field: {
            id: 'em_field',
            name: 'Charged Particle in EM Field',
            icon: '⚡',
            tag: 'Gauge Potential',
            coords: 'x',
            velocities: 'dx',
            params: 'm, q_charge, A_pot, V',
            lagrangianExpr: '0.5 * m * dx^2 + q_charge * A_pot * dx - V',
            latexLagrangian: '\\mathcal{L} = \\frac{1}{2}m\\dot{\\mathbf{x}}^2 + q\\class{scrub-token scrub-A}{\\mathbf{A}}\\cdot\\dot{\\mathbf{x}} - q\\Phi',
            sliderParam: { name: 'Vector Potential Scale (A)', min: 0.1, max: 3.0, step: 0.1, default: 1.0, unit: ' T·m' },
            deepLink: '/physics/notation-toggle?theory=maxwell&rep=relativistic_tensor',
            deepLinkText: 'Inspect Gauge Formalisms in Rosetta Stone →',
            rosetta: {
                gibbs: '\\mathbf{F} = q(\\mathbf{E} + \\mathbf{v} \\times \\mathbf{B}) \\quad (\\text{Lorentz Force Law})',
                tensor: 'm\\frac{dU^\\mu}{d\\tau} = q F^{\\mu\\nu} U_\\nu, \\quad F_{\\mu\\nu} = \\partial_\\mu A_\\nu - \\partial_\\nu A_\\mu',
                forms: 'F = dA, \\quad dF = 0, \\quad d\\star F = \\mu_0 J \\quad (\\text{Cartan Exterior Forms})'
            },
            symmetries: {
                continuous: 'U(1) Local Gauge Symmetry (A_μ → A_μ + ∂_μ χ)',
                conserved: 'Canonical Momentum Shift p = mv + qA, Electric Charge Conservation',
                formula: '\\partial_\\mu J^\\mu = 0 \\quad (\\text{Noether Conservation of Electric Charge})'
            },
            quantum: {
                equation: '\\frac{1}{2m}(-i\\hbar\\nabla - q\\class{scrub-token scrub-A}{\\mathbf{A}})^2\\psi + q\\Phi\\psi = i\\hbar\\frac{\\partial\\psi}{\\partial t}',
                groundEnergy: '\\Delta \\phi = \\frac{q}{\\hbar}\\oint \\mathbf{A}\\cdot d\\mathbf{x} \\quad (\\text{Aharonov-Bohm Effect})',
                wigner: 'Landau level spiral phase orbits'
            },
            dimensions: {
                latex: 'F = q (E + v \\class{scrub-token scrub-A}{B})',
                quantity: 'Force',
                powers: { M: 1, L: 1, T: -2 }
            }
        },
        quantum_barrier: {
            id: 'quantum_barrier',
            name: 'Quantum Tunneling Barrier',
            icon: '👻',
            tag: 'Wave Packet',
            coords: 'x',
            velocities: 'dx',
            params: 'm, V0',
            lagrangianExpr: '0.5 * m * dx^2 - V0',
            latexLagrangian: 'i\\hbar\\frac{\\partial \\psi}{\\partial t} = -\\frac{\\hbar^2}{2m}\\frac{\\partial^2 \\psi}{\\partial x^2} + \\class{scrub-token scrub-V0}{V_0}\\,\\Theta(x)\\psi',
            sliderParam: { name: 'Barrier Potential (V₀)', min: 0.5, max: 5.0, step: 0.1, default: 2.2, unit: ' eV' },
            deepLink: '/physics/correspondence-workspace?mode=ehrenfest&pot=barrier',
            deepLinkText: 'Simulate Wigner Flow in Correspondence Workspace →',
            rosetta: {
                gibbs: '\\frac{d\\langle x \\rangle}{dt} = \\frac{\\langle p \\rangle}{m}, \\quad \\frac{d\\langle p \\rangle}{dt} = -\\left\\langle \\frac{\\partial V}{\\partial x} \\right\\rangle \\quad (\\text{Ehrenfest})',
                tensor: 'T_{\\mu\\nu} = \\frac{\\hbar^2}{2m}\\left(\\partial_\\mu \\psi^* \\partial_\\nu \\psi + \\partial_\\nu \\psi^* \\partial_\\mu \\psi\\right) - \\eta_{\\mu\\nu}\\mathcal{L}',
                forms: 'd\\star j = 0 \\quad (j = \\frac{\\hbar}{2mi}(\\psi^*\\nabla\\psi - \\psi\\nabla\\psi^*) \\text{ Probability Current})'
            },
            symmetries: {
                continuous: 'Global Phase Invariance (ψ → e^{iα} ψ)',
                conserved: 'Total Probability Flux ∫ |ψ|² dx = 1 (Unitarity of S-Matrix)',
                formula: '\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot \\mathbf{j} = 0'
            },
            quantum: {
                equation: 'T = \\left[1 + \\frac{\\class{scrub-token scrub-V0}{V_0}^2\\sinh^2(\\kappa a)}{4E(\\class{scrub-token scrub-V0}{V_0} - E)}\\right]^{-1}, \\quad \\kappa = \\frac{\\sqrt{2m(V_0-E)}}{\\hbar}',
                groundEnergy: '\\lim_{\\hbar \\to 0} T = 0 \\quad (\\text{Classical Hard Barrier Limit})',
                wigner: 'Evanescent probability bleeding into forbidden phase zone'
            },
            dimensions: {
                latex: 'E = \\hbar \\omega',
                quantity: 'Energy / Work / Hamiltonian',
                powers: { M: 1, L: 2, T: -2 }
            }
        },
        central_force: {
            id: 'central_force',
            name: 'Schwarzschild Orbital Field',
            icon: '🌌',
            tag: 'ISCO Relativistic',
            coords: 'r, phi',
            velocities: 'dr, dphi',
            params: 'm, M, G, c',
            lagrangianExpr: '0.5 * m * (dr^2 + r^2 * dphi^2) + G * M * m / r',
            latexLagrangian: '\\mathcal{L} = \\frac{1}{2}m\\dot{r}^2 + \\frac{1}{2}m r^2\\dot{\\phi}^2 + \\frac{\\class{scrub-token scrub-G}{G} M m}{r}',
            sliderParam: { name: 'Gravitational Strength (G / G₀)', min: 0.5, max: 4.0, step: 0.1, default: 1.0, unit: ' G₀' },
            deepLink: '/physics/anthropic-tuner?preset=collapse',
            deepLinkText: 'Tune ISCO Collapse in Anthropic Tuner →',
            rosetta: {
                gibbs: '\\mathbf{F} = -\\frac{\\class{scrub-token scrub-G}{G}Mm}{r^2}\\hat{\\mathbf{r}} \\quad (\\text{Newtonian Central Gravity})',
                tensor: 'ds^2 = -\\left(1 - \\frac{2GM}{c^2 r}\\right)c^2 dt^2 + \\left(1 - \\frac{2GM}{c^2 r}\\right)^{-1}dr^2 + r^2 d\\Omega^2',
                forms: 'R^\\mu_{\\ \\nu} = \\mathbf{d}\\omega^\\mu_{\\ \\nu} + \\omega^\\mu_{\\ \\lambda}\\wedge\\omega^\\lambda_{\\ \\nu} \\quad (\\text{Curvature 2-Form})'
            },
            symmetries: {
                continuous: 'Rotational SO(3) & Time Translation Invariance',
                conserved: 'Orbital Angular Momentum L_z = m r² dφ/dt & Relativistic Energy E',
                formula: '\\frac{dL_z}{dt} = 0, \\quad r_{\\text{ISCO}} = \\frac{6GM}{c^2}'
            },
            quantum: {
                equation: '\\left[\\frac{1}{r^2}\\frac{\\partial}{\\partial r}\\left(r^2\\frac{\\partial}{\\partial r}\\right) - \\frac{\\hat{L}^2}{\\hbar^2 r^2} + \\frac{2m}{\\hbar^2}(E - V)\\right]\\psi = 0',
                groundEnergy: 'E_n = -\\frac{\\mu (G M m)^2}{2\\hbar^2 n^2} \\quad (\\text{Gravitational Bound Spectrum})',
                wigner: 'Precessing Keplerian phase torus with Boyer-Lindquist distortion'
            },
            dimensions: {
                latex: 'r_s = \\frac{2 \\class{scrub-token scrub-G}{G} M}{c^2}',
                quantity: 'Length / Spatial Extent / Radius',
                powers: { L: 1 }
            }
        }
    };

    // =========================================================================
    // 2. MAIN COCKPIT ENGINE CLASS
    // =========================================================================
    class PhysicsCockpitEngine {
        constructor() {
            this.activeSystemId = 'sho';
            this.activePrism = 'variational';
            this.isRunning = true;
            this.soundEnabled = false;
            this.audioCtx = null;
            this.simTime = 0;
            this.animFrameId = null;
            this.casCache = {}; // Cache for SymPy results to eliminate redundant API calls

            // DOM elements
            this.canvas = document.getElementById('cosmic-arena-canvas');
            this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
            this.dpr = window.devicePixelRatio || 1;

            this.initDOMElements();
            this.initURLParams();
            this.bindEvents();
            this.initScrubbableMath();
            this.initCanvas();
            this.updateCockpitView();
        }

        initDOMElements() {
            // Crucible Pills
            this.systemPills = document.querySelectorAll('.crucible-system-pill');
            // Prism Tabs
            this.prismTabs = document.querySelectorAll('.prism-tab');

            // Interactive Controls
            this.playPauseBtn = document.getElementById('arena-play-pause');
            this.resetBtn = document.getElementById('arena-reset');
            this.soundToggleBtn = document.getElementById('arena-sound-toggle');
            this.paramSlider = document.getElementById('arena-param-slider');
            this.paramLabel = document.getElementById('arena-param-label');
            this.paramVal = document.getElementById('arena-param-val');
            this.deepLinkBtn = document.getElementById('arena-deep-link');
            this.statusBadge = document.getElementById('arena-status-badge');

            // Telemetry Cells
            this.telemQ = document.getElementById('telem-q');
            this.telemP = document.getElementById('telem-p');
            this.telemV = document.getElementById('telem-v');
            this.telemE = document.getElementById('telem-e');

            // Math & CAS Display
            this.equationDisplay = document.getElementById('arena-equation-display');
            this.casConsole = document.getElementById('cockpit-cas-console');
        }

        initURLParams() {
            const urlParams = new URLSearchParams(window.location.search);
            const sys = urlParams.get('system');
            const prism = urlParams.get('prism');
            if (sys && CRUCIBLE_SYSTEMS[sys]) {
                this.activeSystemId = sys;
            }
            if (prism && ['variational', 'noether', 'quantum', 'rosetta', 'dimensions'].includes(prism)) {
                this.activePrism = prism;
            }
        }

        bindEvents() {
            // System Crucible Selection
            this.systemPills.forEach(pill => {
                pill.addEventListener('click', () => {
                    const sysId = pill.dataset.system;
                    if (sysId && CRUCIBLE_SYSTEMS[sysId]) {
                        this.setSystem(sysId);
                    }
                });
            });

            // Prism Selector Tabs
            this.prismTabs.forEach(tab => {
                tab.addEventListener('click', () => {
                    const prismId = tab.dataset.prism;
                    if (prismId) {
                        this.setPrism(prismId);
                    }
                });
            });

            // Play / Pause
            if (this.playPauseBtn) {
                this.playPauseBtn.addEventListener('click', () => {
                    this.isRunning = !this.isRunning;
                    this.playPauseBtn.innerHTML = this.isRunning
                        ? '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg> Pause'
                        : '<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Resume';
                });
            }

            // Reset Simulation
            if (this.resetBtn) {
                this.resetBtn.addEventListener('click', () => {
                    this.simTime = 0;
                    this.resetActiveSimulation();
                });
            }

            // Parameter Slider
            if (this.paramSlider) {
                this.paramSlider.addEventListener('input', (e) => {
                    const val = parseFloat(e.target.value);
                    const sys = CRUCIBLE_SYSTEMS[this.activeSystemId];
                    if (this.paramVal) {
                        this.paramVal.textContent = val.toFixed(2) + (sys.sliderParam.unit || '');
                    }
                    this.onParameterChange(val);
                    if (this.scrubber) {
                        const varMap = { sho: 'k', relativistic: 'v', chaos: 'l2', em_field: 'A', quantum_barrier: 'V0', central_force: 'G' };
                        const activeVar = varMap[this.activeSystemId];
                        if (activeVar) {
                            this.scrubber.setTokenValue(activeVar, val);
                        }
                    }
                });
            }

            // Harmonic Audio Toggle
            if (this.soundToggleBtn) {
                this.soundToggleBtn.addEventListener('click', () => {
                    this.soundEnabled = !this.soundEnabled;
                    this.soundToggleBtn.classList.toggle('active', this.soundEnabled);
                    if (this.soundEnabled) {
                        this.initAudio();
                        this.playTone(440, 'sine', 0.2, 0.08);
                    }
                });
            }

            // Micro-challenges launch hooks
            document.querySelectorAll('.challenge-action-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const targetMode = btn.dataset.targetMode;
                    const targetVal = parseFloat(btn.dataset.targetVal);
                    if (targetMode === 'noether') {
                        this.setSystem('sho');
                        this.setPrism('noether');
                    } else if (targetMode === 'quantum') {
                        this.setSystem('quantum_barrier');
                        this.setPrism('quantum');
                    } else if (targetMode === 'collapse') {
                        this.setSystem('central_force');
                        this.setPrism('variational');
                    }
                    if (this.paramSlider && !isNaN(targetVal)) {
                        this.paramSlider.value = targetVal;
                        this.paramSlider.dispatchEvent(new Event('input'));
                    }
                    window.scrollTo({ top: this.canvas.getBoundingClientRect().top + window.scrollY - 100, behavior: 'smooth' });
                });
            });
        }

        initCanvas() {
            if (!this.canvas) return;
            const resize = () => {
                const rect = this.canvas.getBoundingClientRect();
                this.width = rect.width;
                this.height = rect.height;
                this.dpr = window.devicePixelRatio || 1;
                this.canvas.width = Math.floor(this.width * this.dpr);
                this.canvas.height = Math.floor(this.height * this.dpr);
                this.ctx.resetTransform();
                this.ctx.scale(this.dpr, this.dpr);
            };
            resize();
            window.addEventListener('resize', resize);

            // Start 60fps Animation Loop
            this.loop = this.loop.bind(this);
            this.animFrameId = requestAnimationFrame(this.loop);
        }

        initAudio() {
            if (!this.audioCtx) {
                const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
                if (AudioCtxClass) this.audioCtx = new AudioCtxClass();
            }
            if (this.audioCtx && this.audioCtx.state === 'suspended') {
                this.audioCtx.resume();
            }
        }

        playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.05) {
            if (!this.soundEnabled || !this.audioCtx) return;
            try {
                const osc = this.audioCtx.createOscillator();
                const gain = this.audioCtx.createGain();
                osc.type = type;
                osc.frequency.setValueAtTime(freq, this.audioCtx.currentTime);
                gain.gain.setValueAtTime(gainVal, this.audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.0001, this.audioCtx.currentTime + duration);
                osc.connect(gain);
                gain.connect(this.audioCtx.destination);
                osc.start();
                osc.stop(this.audioCtx.currentTime + duration);
            } catch (e) {
                // Audio errors safely swallowed
            }
        }

        setSystem(systemId) {
            if (!CRUCIBLE_SYSTEMS[systemId]) return;
            this.activeSystemId = systemId;

            // Update UI Active Pills
            this.systemPills.forEach(p => {
                p.classList.toggle('active', p.dataset.system === systemId);
            });

            this.updateURL();
            this.updateCockpitView();
            this.playTone(320, 'sine', 0.1, 0.04);
        }

        setPrism(prismId) {
            this.activePrism = prismId;

            // Update UI Active Tabs
            this.prismTabs.forEach(t => {
                t.classList.toggle('active', t.dataset.prism === prismId);
            });

            this.updateURL();
            this.updateCockpitView();
            this.playTone(480, 'triangle', 0.1, 0.04);
        }

        updateURL() {
            const url = new URL(window.location.href);
            url.searchParams.set('system', this.activeSystemId);
            url.searchParams.set('prism', this.activePrism);
            window.history.replaceState({}, '', url.toString());
        }

        updateCockpitView() {
            const sys = CRUCIBLE_SYSTEMS[this.activeSystemId];
            if (!sys) return;

            // 1. Update Parameter Slider
            if (this.paramSlider && this.paramLabel && this.paramVal) {
                this.paramLabel.textContent = sys.sliderParam.name;
                this.paramSlider.min = sys.sliderParam.min;
                this.paramSlider.max = sys.sliderParam.max;
                this.paramSlider.step = sys.sliderParam.step;
                this.paramSlider.value = sys.sliderParam.default;
                this.paramVal.textContent = sys.sliderParam.default.toFixed(2) + (sys.sliderParam.unit || '');
                if (this.scrubber) {
                    const varMap = { sho: 'k', relativistic: 'v', chaos: 'l2', em_field: 'A', quantum_barrier: 'V0', central_force: 'G' };
                    const activeVar = varMap[this.activeSystemId];
                    if (activeVar) {
                        this.scrubber.setTokenValue(activeVar, sys.sliderParam.default);
                    }
                }
            }

            // 2. Update Deep Link Button
            if (this.deepLinkBtn) {
                this.deepLinkBtn.href = sys.deepLink;
                this.deepLinkBtn.textContent = sys.deepLinkText;
            }

            // 3. Render Equation Display depending on Prism
            this.renderPrismEquation(sys);

            // 4. Fetch / Render SymPy CAS Insights
            this.fetchSympyCAS(sys);

            // 5. Reset active simulation state for the canvas
            this.resetActiveSimulation();
        }

        renderPrismEquation(sys) {
            if (!this.equationDisplay) return;

            let eqHtml = '';
            if (this.activePrism === 'variational') {
                eqHtml = `\\[ ${sys.latexLagrangian} \\]`;
            } else if (this.activePrism === 'noether') {
                eqHtml = `\\[ ${sys.symmetries.formula} \\quad \\text{(${sys.symmetries.conserved})} \\]`;
            } else if (this.activePrism === 'quantum') {
                eqHtml = `\\[ ${sys.quantum.equation} \\]`;
            } else if (this.activePrism === 'rosetta') {
                eqHtml = `\\[ \\text{Gibbs: } ${sys.rosetta.gibbs} \\]`;
            } else if (this.activePrism === 'dimensions') {
                eqHtml = `\\[ ${sys.dimensions.latex} \\quad\\Longrightarrow\\quad [\\text{${sys.dimensions.quantity}}] \\]`;
            }

            this.equationDisplay.innerHTML = eqHtml;
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this.equationDisplay]).then(() => {
                    if (this.scrubber) {
                        this.scrubber.attach();
                    }
                }).catch(() => {});
            }
        }

        async fetchSympyCAS(sys) {
            if (!this.casConsole) return;

            const cacheKey = `${sys.id}_${this.activePrism}`;
            if (this.casCache[cacheKey]) {
                this.renderCASResult(this.casCache[cacheKey]);
                return;
            }

            this.casConsole.innerHTML = `
                <div style="display:flex;align-items:center;gap:10px;color:var(--text-muted);font-size:0.85rem;padding:8px 0;">
                    <div class="cas-spinner"></div>
                    <span>Evaluating ${this.activePrism} manifold in SymPy CAS worker...</span>
                </div>
            `;

            try {
                let payload = {};
                if (this.activePrism === 'variational') {
                    payload = {
                        mode: 'legendre',
                        lagrangian: sys.lagrangianExpr,
                        coords: sys.coords,
                        velocities: sys.velocities,
                        parameters: sys.params
                    };
                } else if (this.activePrism === 'dimensions') {
                    payload = {
                        mode: 'dimensions',
                        latex: sys.dimensions.latex
                    };
                } else {
                    payload = {
                        mode: 'evaluate',
                        latex: sys.latexLagrangian
                    };
                }

                const res = await fetch('/physics/api/cas-evaluate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                this.casCache[cacheKey] = data;
                this.renderCASResult(data);
            } catch (err) {
                this.casConsole.innerHTML = `<span style="color:#ef4444;font-size:0.85rem;">CAS connection failed. Showing offline analytical reduction.</span>`;
            }
        }

        renderCASResult(data) {
            if (!this.casConsole) return;
            const sys = CRUCIBLE_SYSTEMS[this.activeSystemId];

            if (this.activePrism === 'variational') {
                if (data.success && data.hamiltonian_latex) {
                    const pLatex = data.momenta && data.momenta[0] ? data.momenta[0].latex : 'p = \\partial L / \\partial \\dot{q}';
                    const detLatex = data.hessian ? data.hessian.det_latex : 'W_{ij} \\neq 0';
                    this.casConsole.innerHTML = `
                        <div class="cas-result-grid">
                            <div class="cas-cell">
                                <span class="cas-cell-label">Canonical Momentum</span>
                                <div class="cas-math">\\[ ${pLatex} \\]</div>
                            </div>
                            <div class="cas-cell">
                                <span class="cas-cell-label">Hessian Matrix det(W)</span>
                                <div class="cas-math">\\[ \\det(W) = ${detLatex} \\]</div>
                            </div>
                            <div class="cas-cell full-width">
                                <span class="cas-cell-label">Derived Hamiltonian H(q, p)</span>
                                <div class="cas-math" style="color:#38bdf8;">\\[ H = ${data.hamiltonian_latex} \\]</div>
                            </div>
                        </div>
                    `;
                } else {
                    this.casConsole.innerHTML = `<div class="cas-cell"><span class="cas-cell-label">SymPy Status</span><p>${data.error || 'Singular Lagrangian constraint'}</p></div>`;
                }
            } else if (this.activePrism === 'noether') {
                this.casConsole.innerHTML = `
                    <div class="cas-result-grid">
                        <div class="cas-cell full-width">
                            <span class="cas-cell-label">Continuous Lie Symmetry</span>
                            <div style="color:#38bdf8;font-weight:600;margin-top:4px;">${sys.symmetries.continuous}</div>
                        </div>
                        <div class="cas-cell full-width">
                            <span class="cas-cell-label">Conserved Noether Current</span>
                            <div class="cas-math" style="color:#34d399;">\\[ ${sys.symmetries.formula} \\]</div>
                        </div>
                    </div>
                `;
            } else if (this.activePrism === 'quantum') {
                this.casConsole.innerHTML = `
                    <div class="cas-result-grid">
                        <div class="cas-cell full-width">
                            <span class="cas-cell-label">Semiclassical Boundary Limit (ħ → 0)</span>
                            <div class="cas-math" style="color:#c084fc;">\\[ ${sys.quantum.groundEnergy} \\]</div>
                        </div>
                        <div class="cas-cell full-width">
                            <span class="cas-cell-label">Wigner Quasi-Probability Flow</span>
                            <div style="color:var(--text-muted);font-size:0.85rem;margin-top:4px;">${sys.quantum.wigner}</div>
                        </div>
                    </div>
                `;
            } else if (this.activePrism === 'rosetta') {
                this.casConsole.innerHTML = `
                    <div class="cas-result-grid">
                        <div class="cas-cell">
                            <span class="cas-cell-label">4D Minkowski Tensor Formulation</span>
                            <div class="cas-math">\\[ ${sys.rosetta.tensor} \\]</div>
                        </div>
                        <div class="cas-cell">
                            <span class="cas-cell-label">Cartan Exterior Differential Form</span>
                            <div class="cas-math" style="color:#fbbf24;">\\[ ${sys.rosetta.forms} \\]</div>
                        </div>
                    </div>
                `;
            } else if (this.activePrism === 'dimensions') {
                const dimLatex = data.is_equation ? data.lhs.dimension_latex : (data.dimension_latex || '[M L^2 T^{-2}]');
                const quantity = data.is_equation ? data.lhs.quantity : (data.quantity || 'Energy');
                this.casConsole.innerHTML = `
                    <div class="cas-result-grid">
                        <div class="cas-cell">
                            <span class="cas-cell-label">Base SI Dimension</span>
                            <div class="cas-math" style="color:#34d399;">\\[ ${dimLatex} \\]</div>
                        </div>
                        <div class="cas-cell">
                            <span class="cas-cell-label">Physical Invariant Class</span>
                            <div style="color:#ffffff;font-weight:600;margin-top:6px;">${quantity}</div>
                        </div>
                        <div class="cas-cell full-width">
                            <span class="cas-cell-label">Dimensional Balance (Homogeneity)</span>
                            <div style="color:#38bdf8;font-size:0.9rem;margin-top:4px;">${data.summary || 'Homogeneous [LHS] = [RHS]'}</div>
                        </div>
                    </div>
                `;
            }

            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this.casConsole]).catch(() => {});
            }
        }

        initScrubbableMath() {
            if (typeof window.ScrubbableMath === 'undefined') return;

            const variables = {
                k: { name: 'Spring Stiffness', min: 0.2, max: 3.0, step: 0.05, default: 1.0, unit: ' N/m' },
                v: { name: 'Velocity Ratio', min: 0.1, max: 0.98, step: 0.02, default: 0.60, unit: ' c' },
                l2: { name: 'Arm Length Ratio (l₂/l₁)', min: 0.2, max: 2.0, step: 0.05, default: 1.0, unit: '' },
                A: { name: 'Vector Potential Scale', min: 0.1, max: 3.0, step: 0.1, default: 1.0, unit: ' T·m' },
                V0: { name: 'Barrier Potential', min: 0.5, max: 5.0, step: 0.1, default: 2.2, unit: ' eV' },
                G: { name: 'Gravitational Strength', min: 0.5, max: 4.0, step: 0.1, default: 1.0, unit: ' G₀' }
            };

            this.scrubber = new window.ScrubbableMath({
                container: this.equationDisplay,
                variables: variables,
                onChange: (varId, val, isFinal) => this.onScrubChange(varId, val, isFinal),
                onStart: (varId, val) => {
                    if (this.soundEnabled) {
                        this.playTone(520, 'triangle', 0.08, 0.04);
                    }
                }
            });
        }

        onScrubChange(varId, val, isFinal) {
            this.onParameterChange(val);

            // Sync HTML slider and value badge
            const sys = CRUCIBLE_SYSTEMS[this.activeSystemId];
            if (this.paramSlider) {
                this.paramSlider.value = val;
            }
            if (this.paramVal && sys) {
                this.paramVal.textContent = val.toFixed(2) + (sys.sliderParam.unit || '');
            }

            // Audio pitch feedback if enabled
            if (this.soundEnabled && Math.random() < 0.25) {
                this.playTone(300 + val * 45, 'triangle', 0.03, 0.02);
            }
        }

        onParameterChange(val) {
            // Adjust simulation state live based on parameter
            if (this.activeSystemId === 'sho') {
                this.simState.k = val;
            } else if (this.activeSystemId === 'relativistic') {
                this.simState.v_ratio = val;
            } else if (this.activeSystemId === 'chaos') {
                this.simState.l2 = 95 * val;
            } else if (this.activeSystemId === 'em_field') {
                this.simState.A = val;
            } else if (this.activeSystemId === 'quantum_barrier') {
                this.simState.V0 = val;
            } else if (this.activeSystemId === 'central_force') {
                this.simState.G = val;
            }
        }

        resetActiveSimulation() {
            this.simState = {
                q: 1.0,
                p: 0.0,
                theta1: Math.PI * 0.58,
                theta2: Math.PI * 0.72,
                w1: 0,
                w2: 0,
                trail: [],
                waveX: 45,
                waveK: 0.95,
                k: 1.0,
                v_ratio: 0.6,
                l1: 95,
                l2: 95,
                A: 1.0,
                V0: 2.2,
                G: 1.0
            };
        }

        // =====================================================================
        // 3. 60FPS NUMERICAL CANVAS RENDER LOOP
        // =====================================================================
        loop() {
            if (this.isRunning) {
                this.simTime += 0.016;
                this.stepPhysics(0.016);
            }
            this.renderCanvas();
            this.updateTelemetry();
            this.animFrameId = requestAnimationFrame(this.loop);
        }

        stepPhysics(dt) {
            if (!this.simState) return;

            if (this.activeSystemId === 'sho') {
                // Simple Harmonic Oscillator: dq/dt = p/m, dp/dt = -k q
                const k = this.simState.k || 1.0;
                const m = 1.0;
                
                // If Noether prism with perturbation, wobble time
                let k_eff = k;
                if (this.activePrism === 'noether' && this.paramSlider) {
                    const eps = parseFloat(this.paramSlider.value) || 0;
                    k_eff = k * (1.0 + eps * Math.sin(3.0 * this.simTime));
                }

                const dq = (this.simState.p / m) * dt * 3.0;
                this.simState.q += dq;
                const dp = (-k_eff * this.simState.q) * dt * 3.0;
                this.simState.p += dp;

                this.simState.trail.push({ q: this.simState.q, p: this.simState.p });
                if (this.simState.trail.length > 150) this.simState.trail.shift();

            } else if (this.activeSystemId === 'relativistic') {
                // Relativistic 1D oscillator
                const v_ratio = this.simState.v_ratio || 0.6;
                const omega = 2.0;
                this.simState.q = Math.cos(omega * this.simTime);
                // Relativistic velocity bounded by c
                const v = -Math.sin(omega * this.simTime) * v_ratio;
                const gamma = 1.0 / Math.sqrt(Math.max(0.01, 1.0 - v * v));
                this.simState.p = gamma * v;

                this.simState.trail.push({ q: this.simState.q, p: this.simState.p });
                if (this.simState.trail.length > 150) this.simState.trail.shift();

            } else if (this.activeSystemId === 'chaos') {
                // Double pendulum step
                const g = 9.8, m1 = 10, m2 = 10, l1 = this.simState.l1, l2 = this.simState.l2;
                const t1 = this.simState.theta1, t2 = this.simState.theta2;
                const w1 = this.simState.w1, w2 = this.simState.w2;
                const delta = t1 - t2;

                const den1 = l1 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
                const num1 = -g * (2 * m1 + m2) * Math.sin(t1) - m2 * g * Math.sin(t1 - 2 * t2) - 2 * Math.sin(delta) * m2 * (w2 * w2 * l2 + w1 * w1 * l1 * Math.cos(delta));
                const a1 = num1 / den1;

                const den2 = l2 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
                const num2 = 2 * Math.sin(delta) * (w1 * w1 * l1 * (m1 + m2) + g * (m1 + m2) * Math.cos(t1) + w2 * w2 * l2 * m2 * Math.cos(delta));
                const a2 = num2 / den2;

                this.simState.w1 += a1 * dt * 1.5;
                this.simState.theta1 += this.simState.w1 * dt * 1.5;
                this.simState.w2 += a2 * dt * 1.5;
                this.simState.theta2 += this.simState.w2 * dt * 1.5;

                const x2 = l1 * Math.sin(this.simState.theta1) + l2 * Math.sin(this.simState.theta2);
                const y2 = l1 * Math.cos(this.simState.theta1) + l2 * Math.cos(this.simState.theta2);
                this.simState.trail.push({ x: x2, y: y2 });
                if (this.simState.trail.length > 150) this.simState.trail.shift();

            } else if (this.activeSystemId === 'em_field') {
                const A = this.simState.A || 1.0;
                const omega = 2.0 * A;
                this.simState.q = Math.cos(omega * this.simTime);
                this.simState.p = -Math.sin(omega * this.simTime) * A;
                this.simState.trail.push({ q: this.simState.q, p: this.simState.p });
                if (this.simState.trail.length > 150) this.simState.trail.shift();

            } else if (this.activeSystemId === 'quantum_barrier') {
                this.simState.waveX += dt * 35.0;
                if (this.simState.waveX > 280) this.simState.waveX = 20;

            } else if (this.activeSystemId === 'central_force') {
                const G = this.simState.G || 1.0;
                const r = Math.max(0.4, 1.2 + 0.5 * Math.cos(this.simTime * 1.8));
                this.simState.q = r;
                this.simState.p = Math.sin(this.simTime * 1.8) * Math.sqrt(G);
                this.simState.trail.push({ q: this.simState.q, p: this.simState.p });
                if (this.simState.trail.length > 150) this.simState.trail.shift();
            }
        }

        renderCanvas() {
            if (!this.ctx) return;
            const ctx = this.ctx;
            const w = this.width;
            const h = this.height;

            // Clear with dark matter gradient
            ctx.fillStyle = '#060911';
            ctx.fillRect(0, 0, w, h);

            // Draw subtle background coordinate grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
            ctx.lineWidth = 1;
            const step = 40;
            for (let x = 0; x < w; x += step) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
            }
            for (let y = 0; y < h; y += step) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
            }

            const cx = w * 0.5;
            const cy = h * 0.5;

            // Prism-specific visual manifold rendering
            if (this.activePrism === 'variational' || this.activePrism === 'dimensions') {
                this.renderPhaseSpace(ctx, cx, cy);
            } else if (this.activePrism === 'noether') {
                this.renderNoetherSymmetry(ctx, cx, cy);
            } else if (this.activePrism === 'quantum') {
                this.renderQuantumWave(ctx, cx, cy);
            } else if (this.activePrism === 'rosetta') {
                this.renderRosettaVectorField(ctx, cx, cy);
            }
        }

        renderPhaseSpace(ctx, cx, cy) {
            // Axes
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1.5;
            ctx.beginPath(); ctx.moveTo(40, cy); ctx.lineTo(this.width - 40, cy); ctx.stroke();
            ctx.beginPath(); ctx.moveTo(cx, 30); ctx.lineTo(cx, this.height - 30); ctx.stroke();

            ctx.fillStyle = '#38bdf8';
            ctx.font = '11px monospace';
            ctx.fillText('Coordinate q →', this.width - 120, cy - 8);
            ctx.fillStyle = '#34d399';
            ctx.fillText('Momentum p ↑', cx + 10, 45);

            if (this.activeSystemId === 'chaos') {
                // Double pendulum spatial arms
                if (!this.simState || !this.simState.trail) return;
                const l1 = this.simState.l1 * 0.7;
                const l2 = this.simState.l2 * 0.7;
                const x1 = cx + l1 * Math.sin(this.simState.theta1);
                const y1 = cy + l1 * Math.cos(this.simState.theta1);
                const x2 = cx + (this.simState.trail.length ? this.simState.trail[this.simState.trail.length - 1].x * 0.7 : 0);
                const y2 = cy + (this.simState.trail.length ? this.simState.trail[this.simState.trail.length - 1].y * 0.7 : 0);

                // Trail
                ctx.beginPath();
                for (let i = 0; i < this.simState.trail.length; i++) {
                    const p = this.simState.trail[i];
                    const px = cx + p.x * 0.7;
                    const py = cy + p.y * 0.7;
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
                ctx.lineWidth = 2;
                ctx.stroke();

                // Rods
                ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
                ctx.lineWidth = 3;
                ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();

                // Bobs
                ctx.fillStyle = '#38bdf8';
                ctx.beginPath(); ctx.arc(x1, y1, 7, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#34d399';
                ctx.beginPath(); ctx.arc(x2, y2, 9, 0, Math.PI * 2); ctx.fill();

            } else {
                // Phase space orbit (q, p)
                if (!this.simState || !this.simState.trail) return;
                const scaleQ = 90;
                const scaleP = 90;

                ctx.beginPath();
                for (let i = 0; i < this.simState.trail.length; i++) {
                    const pt = this.simState.trail[i];
                    const px = cx + pt.q * scaleQ;
                    const py = cy - pt.p * scaleP;
                    if (i === 0) ctx.moveTo(px, py);
                    else ctx.lineTo(px, py);
                }
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.5)';
                ctx.lineWidth = 2.5;
                ctx.stroke();

                // Active particle state
                const currX = cx + this.simState.q * scaleQ;
                const currY = cy - this.simState.p * scaleP;

                ctx.shadowColor = '#38bdf8';
                ctx.shadowBlur = 15;
                ctx.fillStyle = '#ffffff';
                ctx.beginPath(); ctx.arc(currX, currY, 7, 0, Math.PI * 2); ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

        renderNoetherSymmetry(ctx, cx, cy) {
            // Animated rotating symmetry ring
            const radius = 95;
            ctx.save();
            ctx.translate(cx, cy);

            ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.lineWidth = 2;
            ctx.beginPath(); ctx.arc(0, 0, radius, 0, Math.PI * 2); ctx.stroke();

            // Symmetries wheel
            const angle = this.simTime * 1.2;
            ctx.rotate(angle);

            for (let i = 0; i < 4; i++) {
                ctx.rotate(Math.PI / 2);
                ctx.strokeStyle = '#38bdf8';
                ctx.lineWidth = 3;
                ctx.beginPath(); ctx.arc(0, 0, radius, 0, Math.PI * 0.25); ctx.stroke();
            }
            ctx.restore();

            // Gauge meter for conserved current
            const gaugeX = cx - 80;
            const gaugeY = cy + 120;
            const gaugeW = 160;
            const gaugeH = 12;

            ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
            ctx.fillRect(gaugeX, gaugeY, gaugeW, gaugeH);

            const isPerturbed = this.paramSlider && parseFloat(this.paramSlider.value) > 0.1;
            const currentConserved = !isPerturbed;

            ctx.fillStyle = currentConserved ? '#34d399' : '#ef4444';
            const fillW = currentConserved ? gaugeW : gaugeW * (0.4 + 0.3 * Math.sin(this.simTime * 6.0));
            ctx.fillRect(gaugeX, gaugeY, fillW, gaugeH);

            ctx.fillStyle = '#ffffff';
            ctx.font = '11px monospace';
            ctx.textAlign = 'center';
            ctx.fillText(currentConserved ? '✓ NOETHER CURRENT CONSERVED (dH/dt = 0)' : '⚠️ SYMMETRY BROKEN (NON-CONSERVED)', cx, gaugeY - 8);
            ctx.textAlign = 'left';
        }

        renderQuantumWave(ctx, cx, cy) {
            const w = this.width;
            const h = this.height;

            // Potential Barrier
            const bx = cx + 20;
            const bw = 30;
            const bh = 140;

            ctx.fillStyle = 'rgba(251, 191, 36, 0.25)';
            ctx.fillRect(bx, cy - bh * 0.5, bw, bh);
            ctx.strokeStyle = '#fbbf24';
            ctx.strokeRect(bx, cy - bh * 0.5, bw, bh);

            ctx.fillStyle = '#fbbf24';
            ctx.font = '10px monospace';
            ctx.fillText('V₀ Barrier', bx + 2, cy - bh * 0.5 - 6);

            // Gaussian Wave Packet
            const packetX = ((this.simState.waveX || 40) / 280) * (w - 100) + 50;
            ctx.beginPath();
            for (let x = 40; x < w - 40; x += 3) {
                const dx = x - packetX;
                const env = Math.exp(-(dx * dx) / (2 * 22 * 22));
                const osc = Math.cos(dx * 0.35 - this.simTime * 8.0);
                const py = cy - env * osc * 55;
                if (x === 40) ctx.moveTo(x, py);
                else ctx.lineTo(x, py);
            }
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Probability Density Envelope |ψ|²
            ctx.beginPath();
            for (let x = 40; x < w - 40; x += 3) {
                const dx = x - packetX;
                const env = Math.exp(-(dx * dx) / (2 * 22 * 22));
                const py = cy - env * 60;
                if (x === 40) ctx.moveTo(x, py);
                else ctx.lineTo(x, py);
            }
            ctx.strokeStyle = 'rgba(192, 132, 252, 0.7)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        renderRosettaVectorField(ctx, cx, cy) {
            // Vector field grid arrows
            const spacing = 35;
            const t = this.simTime;

            for (let x = 60; x < this.width - 60; x += spacing) {
                for (let y = 60; y < this.height - 60; y += spacing) {
                    const dx = (x - cx) / 80;
                    const dy = (y - cy) / 80;

                    // Rotational curl + harmonic divergence
                    const vx = -dy + 0.2 * Math.sin(t + dx);
                    const vy = dx + 0.2 * Math.cos(t + dy);
                    const len = Math.sqrt(vx * vx + vy * vy) || 1;

                    const arrowLen = 14;
                    const ax = x + (vx / len) * arrowLen;
                    const ay = y + (vy / len) * arrowLen;

                    ctx.strokeStyle = 'rgba(56, 189, 248, 0.45)';
                    ctx.lineWidth = 1.2;
                    ctx.beginPath();
                    ctx.moveTo(x, y);
                    ctx.lineTo(ax, ay);
                    ctx.stroke();

                    // Arrowhead
                    ctx.fillStyle = '#34d399';
                    ctx.beginPath();
                    ctx.arc(ax, ay, 2, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }

        updateTelemetry() {
            if (!this.simState) return;
            const q = this.simState.q || (this.simState.theta1 || 0);
            const p = this.simState.p || (this.simState.w1 || 0);
            const v = 0.5 * (this.simState.k || 1.0) * q * q;
            const e = 0.5 * p * p + v;

            if (this.telemQ) this.telemQ.textContent = q.toFixed(2);
            if (this.telemP) this.telemP.textContent = p.toFixed(2);
            if (this.telemV) this.telemV.textContent = v.toFixed(2);
            if (this.telemE) this.telemE.textContent = e.toFixed(2);
        }
    }

    // Auto-mount when DOM is ready
    document.addEventListener('DOMContentLoaded', () => {
        window.PhysicsCockpit = new PhysicsCockpitEngine();
    });

})();
