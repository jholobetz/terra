/**
 * cosmic_arena.js - The Cosmic Arena & Unified Physics Cockpit Engine
 * Physics Lab Digital Encyclopedia & Mathematical Manifold
 * 
 * Drives the 60fps high-DPI interactive hero simulation stage across 4 physical regimes:
 * 1. The Butterfly of Chaos (Double Pendulum RK4 + Phase Space)
 * 2. The Quantum Ghost (1D Wave Packet Tunneling & Splitting)
 * 3. Tuning the Universe to Death (Relativistic Gravitational ISCO Collapse)
 * 4. The Breaking of Energy (Noether Time Symmetry Perturbation & Resonance)
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('cosmic-arena-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    let width = 0;
    let height = 0;
    let dpr = window.devicePixelRatio || 1;

    // UI Elements
    const pills = document.querySelectorAll('.mystery-pill');
    const playPauseBtn = document.getElementById('arena-play-pause');
    const resetBtn = document.getElementById('arena-reset');
    const soundToggleBtn = document.getElementById('arena-sound-toggle');
    const paramSlider = document.getElementById('arena-param-slider');
    const paramLabel = document.getElementById('arena-param-label');
    const paramVal = document.getElementById('arena-param-val');
    const equationDisplay = document.getElementById('arena-equation-display');
    const statusBadge = document.getElementById('arena-status-badge');
    const deepLinkBtn = document.getElementById('arena-deep-link');
    
    // Telemetry displays
    const telemQ = document.getElementById('telem-q');
    const telemP = document.getElementById('telem-p');
    const telemV = document.getElementById('telem-v');
    const telemE = document.getElementById('telem-e');

    // State Variables
    let currentMode = 'chaos'; // 'chaos', 'quantum', 'collapse', 'noether'
    let isRunning = true;
    let soundEnabled = false;
    let audioCtx = null;
    let animFrameId = null;
    let simTime = 0;

    // Mouse Interaction
    const mouse = { x: null, y: null, active: false };

    // --- Audio Engine (Subtle harmonic synthesis) ---
    function initAudio() {
        if (!audioCtx) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            if (AudioContextClass) {
                audioCtx = new AudioContextClass();
            }
        }
        if (audioCtx && audioCtx.state === 'suspended') {
            audioCtx.resume();
        }
    }

    function playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.05) {
        if (!soundEnabled || !audioCtx) return;
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + duration);
        } catch (e) {
            // Audio context failure gracefully ignored
        }
    }

    // --- High DPI Canvas Resizing ---
    function resize() {
        const rect = canvas.getBoundingClientRect();
        width = rect.width;
        height = rect.height;
        dpr = window.devicePixelRatio || 1;
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        ctx.resetTransform();
        ctx.scale(dpr, dpr);
    }
    resize();
    window.addEventListener('resize', resize);

    // --- Mode Configurations ---
    const MODES = {
        chaos: {
            title: "The Butterfly of Chaos",
            paramName: "Arm Length Ratio (l₂ / l₁)",
            paramMin: 0.2,
            paramMax: 2.0,
            paramStep: 0.05,
            paramDefault: 1.0,
            unit: "",
            equation: "\\[ \\mathcal{L} = \\frac{1}{2}(m_1+m_2)l_1^2\\dot{\\theta}_1^2 + \\frac{1}{2}m_2 l_2^2\\dot{\\theta}_2^2 + m_2 l_1 l_2 \\dot{\\theta}_1\\dot{\\theta}_2\\cos(\\theta_1-\\theta_2) + (m_1+m_2)g l_1\\cos\\theta_1 + m_2 g l_2\\cos\\theta_2 \\]",
            deepLinkUrl: "/physics/legendre-transformer?preset=double_pendulum",
            deepLinkText: "Inspect in Analytical Mechanics Workbench →",
            colorCoupledHint: "Coordinate <strong style='color:#38bdf8;'>θ</strong> | Momentum <strong style='color:#34d399;'>p_θ</strong> | Gravity Potential <strong style='color:#fbbf24;'>V(θ)</strong>"
        },
        quantum: {
            title: "The Quantum Ghost",
            paramName: "Potential Barrier Height (V₀)",
            paramMin: 0.5,
            paramMax: 5.0,
            paramStep: 0.1,
            paramDefault: 2.2,
            unit: " eV",
            equation: "\\[ i\\hbar\\frac{\\partial \\psi}{\\partial t} = -\\frac{\\hbar^2}{2m}\\frac{\\partial^2 \\psi}{\\partial x^2} + V_0\\,\\Theta(x)\\psi \\quad\\Longrightarrow\\quad T = \\left(1 + \\frac{V_0^2\\sinh^2(\\kappa a)}{4E(V_0 - E)}\\right)^{-1} \\]",
            deepLinkUrl: "/physics/correspondence-workspace",
            deepLinkText: "Analyze Wave Packet in Correspondence Workspace →",
            colorCoupledHint: "Wave Packet <strong style='color:#38bdf8;'>|ψ(x)|²</strong> | Kinetic Phase <strong style='color:#34d399;'>Re(ψ)</strong> | Barrier <strong style='color:#fbbf24;'>V₀</strong>"
        },
        collapse: {
            title: "Tuning the Universe to Death",
            paramName: "Gravitational Dial (G / G₀)",
            paramMin: 0.5,
            paramMax: 4.0,
            paramStep: 0.1,
            paramDefault: 1.0,
            unit: " G₀",
            equation: "\\[ V_{\\text{eff}}(r) = -\\frac{GM}{r} + \\frac{L^2}{2\\mu r^2} - \\frac{GML^2}{c^2 r^3} \\quad\\Longrightarrow\\quad r_{\\text{ISCO}} = \\frac{6GM}{c^2} \\]",
            deepLinkUrl: "/physics/anthropic-tuner",
            deepLinkText: "Tune Fundamental Constants in Multiverse Creator →",
            colorCoupledHint: "Orbital Radius <strong style='color:#38bdf8;'>r</strong> | Angular Momentum <strong style='color:#34d399;'>L</strong> | Effective Potential <strong style='color:#fbbf24;'>V_eff</strong>"
        },
        noether: {
            title: "The Breaking of Energy",
            paramName: "Time Symmetry Perturbation (ε)",
            paramMin: 0.0,
            paramMax: 1.0,
            paramStep: 0.05,
            paramDefault: 0.0,
            unit: "",
            equation: "\\[ V(q, t) = \\frac{1}{2}k\\left[1 + \\varepsilon\\cos(\\omega_p t)\\right]q^2 \\quad\\Longrightarrow\\quad \\frac{dE}{dt} = -\\frac{\\partial \\mathcal{L}}{\\partial t} = \\frac{1}{2}\\varepsilon k \\omega_p\\sin(\\omega_p t)q^2 \\neq 0 \\]",
            deepLinkUrl: "/physics/noethers-vault",
            deepLinkText: "Explore Symmetries in Noether's Vault →",
            colorCoupledHint: "Displacement <strong style='color:#38bdf8;'>q</strong> | Canonical Momentum <strong style='color:#34d399;'>p</strong> | Perturbed Potential <strong style='color:#fbbf24;'>V(q,t)</strong>"
        }
    };

    // =========================================================================
    // SIMULATION STATE 1: DOUBLE PENDULUM (Runge-Kutta 4)
    // =========================================================================
    const chaosState = {
        l1: 95,
        l2: 95,
        m1: 10,
        m2: 10,
        g: 9.8,
        theta1: Math.PI / 2 + 0.1,
        theta2: Math.PI / 2 + 0.1,
        omega1: 0.0,
        omega2: 0.0,
        trail: [],
        maxTrail: 160,
        initialEnergy: 0,
        reset() {
            this.theta1 = Math.PI * 0.58;
            this.theta2 = Math.PI * 0.72;
            this.omega1 = 0;
            this.omega2 = 0;
            this.trail = [];
            this.initialEnergy = this.getEnergy().total;
        },
        derivatives(t1, t2, w1, w2) {
            const g = this.g;
            const m1 = this.m1;
            const m2 = this.m2;
            const l1 = this.l1;
            const l2 = this.l2;
            const delta = t1 - t2;

            const den1 = l1 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
            const num1 = -g * (2 * m1 + m2) * Math.sin(t1) - m2 * g * Math.sin(t1 - 2 * t2) - 2 * Math.sin(delta) * m2 * (w2 * w2 * l2 + w1 * w1 * l1 * Math.cos(delta));
            const alpha1 = num1 / den1;

            const den2 = l2 * (2 * m1 + m2 - m2 * Math.cos(2 * t1 - 2 * t2));
            const num2 = 2 * Math.sin(delta) * (w1 * w1 * l1 * (m1 + m2) + g * (m1 + m2) * Math.cos(t1) + w2 * w2 * l2 * m2 * Math.cos(delta));
            const alpha2 = num2 / den2;

            return [w1, alpha1, w2, alpha2];
        },
        step(dt) {
            // RK4 integration
            const [w1, a1, w2, a2] = this.derivatives(this.theta1, this.theta2, this.omega1, this.omega2);

            const t1_k2 = this.theta1 + 0.5 * dt * w1;
            const w1_k2 = this.omega1 + 0.5 * dt * a1;
            const t2_k2 = this.theta2 + 0.5 * dt * w2;
            const w2_k2 = this.omega2 + 0.5 * dt * a2;
            const [w1_2, a1_2, w2_2, a2_2] = this.derivatives(t1_k2, t2_k2, w1_k2, w2_k2);

            const t1_k3 = this.theta1 + 0.5 * dt * w1_2;
            const w1_k3 = this.omega1 + 0.5 * dt * a1_2;
            const t2_k3 = this.theta2 + 0.5 * dt * w2_2;
            const w2_k3 = this.omega2 + 0.5 * dt * a2_2;
            const [w1_3, a1_3, w2_3, a2_3] = this.derivatives(t1_k3, t2_k3, w1_k3, w2_k3);

            const t1_k4 = this.theta1 + dt * w1_3;
            const w1_k4 = this.omega1 + dt * a1_3;
            const t2_k4 = this.theta2 + dt * w2_3;
            const w2_k4 = this.omega2 + dt * a2_3;
            const [w1_4, a1_4, w2_4, a2_4] = this.derivatives(t1_k4, t2_k4, w1_k4, w2_k4);

            this.theta1 += (dt / 6) * (w1 + 2 * w1_2 + 2 * w1_3 + w1_4);
            this.omega1 += (dt / 6) * (a1 + 2 * a1_2 + 2 * a1_3 + a1_4);
            this.theta2 += (dt / 6) * (w2 + 2 * w2_2 + 2 * w2_3 + w2_4);
            this.omega2 += (dt / 6) * (a2 + 2 * a2_2 + 2 * a2_3 + a2_4);

            // Coordinates
            const x1 = this.l1 * Math.sin(this.theta1);
            const y1 = this.l1 * Math.cos(this.theta1);
            const x2 = x1 + this.l2 * Math.sin(this.theta2);
            const y2 = y1 + this.l2 * Math.cos(this.theta2);

            this.trail.push({ x: x2, y: y2 });
            if (this.trail.length > this.maxTrail) this.trail.shift();
        },
        getEnergy() {
            const m1 = this.m1, m2 = this.m2, l1 = this.l1, l2 = this.l2, g = this.g;
            const t1 = this.theta1, t2 = this.theta2, w1 = this.omega1, w2 = this.omega2;
            const T = 0.5 * m1 * (l1 * w1) ** 2 + 0.5 * m2 * ((l1 * w1) ** 2 + (l2 * w2) ** 2 + 2 * l1 * l2 * w1 * w2 * Math.cos(t1 - t2));
            const V = -(m1 + m2) * g * l1 * Math.cos(t1) - m2 * g * l2 * Math.cos(t2);
            return { kinetic: T, potential: V, total: T + V };
        }
    };

    // =========================================================================
    // SIMULATION STATE 2: QUANTUM WAVE PACKET TUNNELING
    // =========================================================================
    const quantumState = {
        N: 200,
        packetX: 45,
        packetK: 0.95,
        sigma: 9.0,
        barrierX: 110,
        barrierWidth: 16,
        V0: 2.2,
        energyE: 2.0,
        time: 0,
        hasChimed: false,
        reset() {
            this.time = 0;
            this.packetX = 45;
            this.hasChimed = false;
        },
        getTransmission() {
            const E = this.energyE;
            const V0 = this.V0;
            if (E >= V0) {
                const k1 = Math.sqrt(E);
                const k2 = Math.sqrt(E - V0);
                const a = this.barrierWidth * 0.1;
                const T = 1 / (1 + (V0 * V0 * Math.sin(k2 * a) ** 2) / (4 * E * (E - V0)));
                return Math.min(1.0, Math.max(0.0, T));
            } else {
                const a = this.barrierWidth * 0.1;
                const kappa = Math.sqrt(V0 - E);
                const denom = 1 + (V0 * V0 * Math.sinh(kappa * a) ** 2) / (4 * E * (V0 - E));
                return Math.min(1.0, Math.max(0.0, 1 / denom));
            }
        },
        step(dt) {
            this.time += dt * 1.8;
            this.packetX += dt * 18;
            if (this.packetX > 250) {
                this.reset();
            }
            if (!this.hasChimed && this.packetX > this.barrierX) {
                this.hasChimed = true;
                playTone(587.33, 'triangle', 0.2, 0.06); // D5 chime
            }
        }
    };

    // =========================================================================
    // SIMULATION STATE 3: GRAVITATIONAL ACCRETION & ISCO COLLAPSE
    // =========================================================================
    const collapseState = {
        G: 1.0,
        M: 1000,
        c: 65,
        particles: [],
        collapsedCount: 0,
        reset() {
            this.particles = [];
            this.collapsedCount = 0;
            const count = 48;
            for (let i = 0; i < count; i++) {
                const radius = 60 + Math.random() * 110;
                const angle = (i / count) * Math.PI * 2 + Math.random() * 0.2;
                // Circular Keplerian orbital speed: v = sqrt(G*M / r)
                const speed = Math.sqrt((this.G * this.M) / radius) * (0.95 + Math.random() * 0.1);
                this.particles.push({
                    x: Math.cos(angle) * radius,
                    y: Math.sin(angle) * radius,
                    vx: -Math.sin(angle) * speed,
                    vy: Math.cos(angle) * speed,
                    trail: [],
                    alive: true,
                    mass: 1.0
                });
            }
        },
        step(dt) {
            const isco = (6 * this.G * this.M) / (this.c * this.c);
            const horizon = (2 * this.G * this.M) / (this.c * this.c);

            for (const p of this.particles) {
                if (!p.alive) continue;
                const r2 = p.x * p.x + p.y * p.y;
                const r = Math.sqrt(r2);

                if (r < horizon + 4) {
                    p.alive = false;
                    this.collapsedCount++;
                    playTone(130.81, 'sawtooth', 0.12, 0.04); // C3 plunge thud
                    continue;
                }

                // General Relativistic Effective Potential Force:
                // a = - (G*M / r^2) * (1 + 3*(L/c)^2 / r^2)
                const L2 = (p.x * p.vy - p.y * p.vx) ** 2;
                const grCorrection = 1.0 + (3.0 * L2) / (this.c * this.c * r2);
                const force = -(this.G * this.M * grCorrection) / (r2 * r);

                p.vx += force * p.x * dt;
                p.vy += force * p.y * dt;
                p.x += p.vx * dt;
                p.y += p.vy * dt;

                p.trail.push({ x: p.x, y: p.y });
                if (p.trail.length > 28) p.trail.shift();
            }
        }
    };

    // =========================================================================
    // SIMULATION STATE 4: NOETHER SYMMETRY BREAKING
    // =========================================================================
    const noetherState = {
        q: 60.0,
        p: 0.0,
        m: 2.0,
        k: 1.8,
        epsilon: 0.0,
        omegaP: 1.2,
        time: 0,
        phaseTrail: [],
        maxTrail: 180,
        reset() {
            this.q = 65.0;
            this.p = 0.0;
            this.time = 0;
            this.phaseTrail = [];
        },
        step(dt) {
            this.time += dt;
            // Parametric oscillator: V(q, t) = 0.5 * k * [1 + eps * cos(omegaP * t)] * q^2
            const currentK = this.k * (1.0 + this.epsilon * Math.cos(this.omegaP * this.time));
            
            // Symplectic Euler integration
            const force = -currentK * this.q;
            this.p += force * dt;
            this.q += (this.p / this.m) * dt;

            this.phaseTrail.push({ q: this.q, p: this.p });
            if (this.phaseTrail.length > this.maxTrail) this.phaseTrail.shift();

            if (this.epsilon > 0.01 && Math.abs(this.q) > 130) {
                // Dissipate slightly to prevent infinite escape
                this.p *= 0.985;
            }
        },
        getEnergy() {
            const T = (this.p * this.p) / (2 * this.m);
            const currentK = this.k * (1.0 + this.epsilon * Math.cos(this.omegaP * this.time));
            const V = 0.5 * currentK * this.q * this.q;
            return { kinetic: T, potential: V, total: T + V };
        }
    };

    // Initialize all states
    chaosState.reset();
    quantumState.reset();
    collapseState.reset();
    noetherState.reset();

    // =========================================================================
    // RENDERING PIPELINES
    // =========================================================================

    function drawGrid(cx, cy, step = 35) {
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.035)';
        ctx.lineWidth = 1;
        for (let x = (cx % step); x < width; x += step) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
            ctx.stroke();
        }
        for (let y = (cy % step); y < height; y += step) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
            ctx.stroke();
        }
        ctx.restore();
    }

    function renderChaos() {
        const cx = width * 0.48;
        const cy = height * 0.38;
        drawGrid(cx, cy);

        // Compute Cartesian coordinates
        const x1 = cx + chaosState.l1 * Math.sin(chaosState.theta1);
        const y1 = cy + chaosState.l1 * Math.cos(chaosState.theta1);
        const x2 = x1 + chaosState.l2 * Math.sin(chaosState.theta2);
        const y2 = y1 + chaosState.l2 * Math.cos(chaosState.theta2);

        // Draw iridescent phase trajectory trail
        if (chaosState.trail.length > 1) {
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(cx + chaosState.trail[0].x, cy + chaosState.trail[0].y);
            for (let i = 1; i < chaosState.trail.length; i++) {
                const pt = chaosState.trail[i];
                ctx.lineTo(cx + pt.x, cy + pt.y);
            }
            const grad = ctx.createLinearGradient(cx - 150, cy - 150, cx + 150, cy + 150);
            grad.addColorStop(0, 'rgba(56, 189, 248, 0.1)');
            grad.addColorStop(0.5, 'rgba(192, 132, 252, 0.4)');
            grad.addColorStop(1, 'rgba(52, 211, 153, 0.85)');
            ctx.strokeStyle = grad;
            ctx.lineWidth = 2.2;
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 8;
            ctx.stroke();
            ctx.restore();
        }

        // Draw Pendulum Rods
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.35)';
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        // Pivot 0
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        ctx.fill();

        // Bob 1 (Coordinate q)
        ctx.fillStyle = '#38bdf8';
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 12;
        ctx.beginPath();
        ctx.arc(x1, y1, 8.5, 0, Math.PI * 2);
        ctx.fill();

        // Bob 2 (Momentum p tip)
        ctx.fillStyle = '#34d399';
        ctx.shadowColor = '#34d399';
        ctx.shadowBlur = 15;
        ctx.beginPath();
        ctx.arc(x2, y2, 10, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Update Telemetry
        const nrg = chaosState.getEnergy();
        telemQ.textContent = `${(chaosState.theta1 % (Math.PI * 2)).toFixed(2)} rad`;
        telemP.textContent = `${(chaosState.omega2 * chaosState.l2).toFixed(2)} kg·m/s`;
        telemV.textContent = `${nrg.potential.toFixed(1)} J`;
        telemE.textContent = `${nrg.total.toFixed(1)} J`;
        statusBadge.textContent = 'HAMILTONIAN CONSERVED';
        statusBadge.style.color = '#34d399';
        statusBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
    }

    function renderQuantum() {
        const cx = 40;
        const cy = height * 0.55;
        drawGrid(cx, cy);

        const w = width - 80;
        const xBarrierLeft = cx + (quantumState.barrierX / 200) * w;
        const bWidth = (quantumState.barrierWidth / 200) * w;
        const vHeight = (quantumState.V0 / 5.0) * (height * 0.45);

        // Draw Potential Barrier V0 (Amber)
        ctx.save();
        ctx.fillStyle = 'rgba(251, 191, 36, 0.15)';
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#fbbf24';
        ctx.shadowBlur = 10;
        ctx.fillRect(xBarrierLeft, cy - vHeight, bWidth, vHeight);
        ctx.strokeRect(xBarrierLeft, cy - vHeight, bWidth, vHeight);

        // Barrier Label
        ctx.fillStyle = '#fbbf24';
        ctx.font = '12px Space Grotesk, sans-serif';
        ctx.fillText(`V₀ = ${quantumState.V0.toFixed(1)} eV`, xBarrierLeft + 4, cy - vHeight - 8);
        ctx.restore();

        // Incident Energy baseline
        const eHeight = (quantumState.energyE / 5.0) * (height * 0.45);
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(cx, cy - eHeight);
        ctx.lineTo(cx + w, cy - eHeight);
        ctx.stroke();
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        ctx.font = '11px monospace';
        ctx.fillText(`E = ${quantumState.energyE.toFixed(1)} eV`, cx + 8, cy - eHeight - 5);
        ctx.restore();

        // Calculate and Draw Wave Packet Profile |psi(x)|^2
        const T = quantumState.getTransmission();
        const R = 1.0 - T;
        const px = cx + (quantumState.packetX / 200) * w;
        const sigma = (quantumState.sigma / 200) * w;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(cx, cy);

        const samples = 140;
        for (let i = 0; i <= samples; i++) {
            const x = cx + (i / samples) * w;
            let amp = 0;

            if (px < xBarrierLeft) {
                // Approaching packet
                const d = (x - px) / sigma;
                amp = Math.exp(-0.5 * d * d) * Math.cos(0.18 * (x - px));
            } else {
                // Split packet into reflected and transmitted lobes
                const dRef = (x - (2 * xBarrierLeft - px)) / (sigma * 1.1);
                const dTrans = (x - px) / (sigma * 1.1);
                const refAmp = -Math.sqrt(R) * Math.exp(-0.5 * dRef * dRef) * Math.cos(0.18 * (x - px));
                const transAmp = Math.sqrt(T) * Math.exp(-0.5 * dTrans * dTrans) * Math.cos(0.18 * (x - px));
                amp = refAmp + transAmp;
            }

            const y = cy - amp * (height * 0.28);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }

        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 14;
        ctx.stroke();

        // Shaded probability density under curve
        ctx.lineTo(cx + w, cy);
        ctx.lineTo(cx, cy);
        const grad = ctx.createLinearGradient(cx, cy - height * 0.3, cx, cy);
        grad.addColorStop(0, 'rgba(56, 189, 248, 0.35)');
        grad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
        ctx.fillStyle = grad;
        ctx.fill();
        ctx.restore();

        // Update Telemetry
        telemQ.textContent = `${quantumState.packetX.toFixed(1)} Å`;
        telemP.textContent = `k = ${quantumState.packetK.toFixed(2)} Å⁻¹`;
        telemV.textContent = `${quantumState.V0.toFixed(2)} eV`;
        telemE.textContent = `T = ${(T * 100).toFixed(1)}%`;
        statusBadge.textContent = T > 0.05 ? `TUNNELING ACTIVE (${(T * 100).toFixed(1)}%)` : 'CLASSICAL TOTAL REFLECTION';
        statusBadge.style.color = T > 0.05 ? '#38bdf8' : '#fbbf24';
        statusBadge.style.borderColor = T > 0.05 ? 'rgba(56, 189, 248, 0.4)' : 'rgba(251, 191, 36, 0.4)';
    }

    function renderCollapse() {
        const cx = width * 0.5;
        const cy = height * 0.5;
        drawGrid(cx, cy);

        const G = collapseState.G;
        const isco = (6 * G * collapseState.M) / (collapseState.c * collapseState.c);
        const horizon = (2 * G * collapseState.M) / (collapseState.c * collapseState.c);

        // Draw ISCO Boundary (Amber dashed)
        ctx.save();
        ctx.strokeStyle = 'rgba(251, 191, 36, 0.45)';
        ctx.setLineDash([5, 5]);
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(cx, cy, isco, 0, Math.PI * 2);
        ctx.stroke();

        // Event Horizon (Black hole core)
        ctx.fillStyle = '#05070d';
        ctx.beginPath();
        ctx.arc(cx, cy, horizon, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#c084fc';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#c084fc';
        ctx.shadowBlur = 18;
        ctx.stroke();

        // Singularity glow
        ctx.fillStyle = '#c084fc';
        ctx.beginPath();
        ctx.arc(cx, cy, 3, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();

        // Draw Orbiting Particles & relativistic trails
        for (const p of collapseState.particles) {
            if (!p.alive) continue;
            if (p.trail.length > 1) {
                ctx.save();
                ctx.beginPath();
                ctx.moveTo(cx + p.trail[0].x, cy + p.trail[0].y);
                for (let i = 1; i < p.trail.length; i++) {
                    ctx.lineTo(cx + p.trail[i].x, cy + p.trail[i].y);
                }
                ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
                ctx.lineWidth = 1.2;
                ctx.stroke();
                ctx.restore();
            }

            ctx.save();
            ctx.fillStyle = '#38bdf8';
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(cx + p.x, cy + p.y, 2.8, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }

        // Telemetry
        telemQ.textContent = `r_ISCO = ${isco.toFixed(1)} R_g`;
        telemP.textContent = `L = ${(collapseState.particles.filter(p => p.alive).length).toString()} bodies`;
        telemV.textContent = `G = ${G.toFixed(2)} G₀`;
        telemE.textContent = `Plunged: ${collapseState.collapsedCount}`;
        
        if (G > 2.0) {
            statusBadge.textContent = 'RELATIVISTIC RUNAWAY COLLAPSE';
            statusBadge.style.color = '#ef4444';
            statusBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
        } else {
            statusBadge.textContent = 'STABLE KEPLERIAN EQUILIBRIUM';
            statusBadge.style.color = '#34d399';
            statusBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
        }
    }

    function renderNoether() {
        const cx = width * 0.48;
        const cy = height * 0.5;
        drawGrid(cx, cy);

        // Draw Phase Space Inset Coordinate Axes (q vs p)
        ctx.save();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(cx - 150, cy);
        ctx.lineTo(cx + 150, cy);
        ctx.moveTo(cx, cy - 110);
        ctx.lineTo(cx, cy + 110);
        ctx.stroke();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.font = '11px Space Grotesk, sans-serif';
        ctx.fillText('+q (Coordinate)', cx + 105, cy - 8);
        ctx.fillText('+p (Momentum)', cx + 8, cy - 95);
        ctx.restore();

        // Draw Phase Space Orbit Trace
        if (noetherState.phaseTrail.length > 1) {
            ctx.save();
            ctx.beginPath();
            ctx.moveTo(cx + noetherState.phaseTrail[0].q, cy - noetherState.phaseTrail[0].p * 0.7);
            for (let i = 1; i < noetherState.phaseTrail.length; i++) {
                const pt = noetherState.phaseTrail[i];
                ctx.lineTo(cx + pt.q, cy - pt.p * 0.7);
            }
            ctx.strokeStyle = noetherState.epsilon > 0.05 ? '#fbbf24' : '#34d399';
            ctx.lineWidth = 2.0;
            ctx.shadowColor = ctx.strokeStyle;
            ctx.shadowBlur = 10;
            ctx.stroke();
            ctx.restore();
        }

        // Active State Point (q, p)
        const curQ = cx + noetherState.q;
        const curP = cy - noetherState.p * 0.7;
        ctx.save();
        ctx.fillStyle = '#38bdf8';
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 14;
        ctx.beginPath();
        ctx.arc(curQ, curP, 6, 0, Math.PI * 2);
        ctx.fill();

        // Vector momentum arrow
        ctx.strokeStyle = '#34d399';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(curQ, curP);
        ctx.lineTo(curQ, curP - noetherState.p * 0.35);
        ctx.stroke();
        ctx.restore();

        // Telemetry
        const nrg = noetherState.getEnergy();
        telemQ.textContent = `${noetherState.q.toFixed(2)} m`;
        telemP.textContent = `${noetherState.p.toFixed(2)} kg·m/s`;
        telemV.textContent = `${nrg.potential.toFixed(1)} J`;
        telemE.textContent = `${nrg.total.toFixed(1)} J`;

        if (noetherState.epsilon > 0.02) {
            statusBadge.textContent = 'SYMMETRY BROKEN: dE/dt ≠ 0';
            statusBadge.style.color = '#fbbf24';
            statusBadge.style.borderColor = 'rgba(251, 191, 36, 0.4)';
        } else {
            statusBadge.textContent = 'NOETHER CONSERVED: ∂L/∂t = 0';
            statusBadge.style.color = '#34d399';
            statusBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
        }
    }

    // =========================================================================
    // MAIN TICK / ANIMATION LOOP
    // =========================================================================
    let lastTick = performance.now();

    function loop(now) {
        const dt = Math.min((now - lastTick) / 1000, 0.05);
        lastTick = now;

        if (isRunning) {
            simTime += dt;
            if (currentMode === 'chaos') {
                chaosState.step(dt * 1.5);
            } else if (currentMode === 'quantum') {
                quantumState.step(dt);
            } else if (currentMode === 'collapse') {
                collapseState.step(dt * 1.4);
            } else if (currentMode === 'noether') {
                noetherState.step(dt * 2.2);
            }
        }

        // Render Active Mode
        ctx.clearRect(0, 0, width, height);
        if (currentMode === 'chaos') {
            renderChaos();
        } else if (currentMode === 'quantum') {
            renderQuantum();
        } else if (currentMode === 'collapse') {
            renderCollapse();
        } else if (currentMode === 'noether') {
            renderNoether();
        }

        animFrameId = requestAnimationFrame(loop);
    }
    animFrameId = requestAnimationFrame(loop);

    // =========================================================================
    // MODE SWITCHING & UI SYNCHRONIZATION
    // =========================================================================

    function switchMode(modeKey) {
        if (!MODES[modeKey]) return;
        currentMode = modeKey;

        // Update active class on pills
        pills.forEach(p => {
            if (p.getAttribute('data-mode') === modeKey) {
                p.classList.add('active');
            } else {
                p.classList.remove('active');
            }
        });

        const cfg = MODES[modeKey];
        paramLabel.textContent = cfg.paramName;
        paramSlider.min = cfg.paramMin;
        paramSlider.max = cfg.paramMax;
        paramSlider.step = cfg.paramStep;
        paramSlider.value = cfg.paramDefault;
        paramVal.textContent = cfg.paramDefault + cfg.unit;

        deepLinkBtn.href = cfg.deepLinkUrl;
        deepLinkBtn.textContent = cfg.deepLinkText;

        // Render Equation with MathJax
        equationDisplay.innerHTML = cfg.equation;
        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([equationDisplay]).catch(err => console.warn(err));
        }

        // Reset corresponding mode state
        if (modeKey === 'chaos') {
            chaosState.l2 = chaosState.l1 * cfg.paramDefault;
            chaosState.reset();
        } else if (modeKey === 'quantum') {
            quantumState.V0 = cfg.paramDefault;
            quantumState.reset();
        } else if (modeKey === 'collapse') {
            collapseState.G = cfg.paramDefault;
            collapseState.reset();
        } else if (modeKey === 'noether') {
            noetherState.epsilon = cfg.paramDefault;
            noetherState.reset();
        }

        playTone(440, 'sine', 0.1, 0.04);
    }

    // Event: Click Pill
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            const mode = pill.getAttribute('data-mode');
            switchMode(mode);
        });
    });

    // Event: Slider Input
    paramSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        const cfg = MODES[currentMode];
        paramVal.textContent = val + cfg.unit;

        if (currentMode === 'chaos') {
            chaosState.l2 = chaosState.l1 * val;
        } else if (currentMode === 'quantum') {
            quantumState.V0 = val;
        } else if (currentMode === 'collapse') {
            collapseState.G = val;
        } else if (currentMode === 'noether') {
            noetherState.epsilon = val;
        }
    });

    // Event: Play / Pause
    playPauseBtn.addEventListener('click', () => {
        isRunning = !isRunning;
        playPauseBtn.innerHTML = isRunning 
            ? `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg> Pause`
            : `<svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg> Resume`;
    });

    // Event: Reset
    resetBtn.addEventListener('click', () => {
        if (currentMode === 'chaos') chaosState.reset();
        else if (currentMode === 'quantum') quantumState.reset();
        else if (currentMode === 'collapse') collapseState.reset();
        else if (currentMode === 'noether') noetherState.reset();
        playTone(523.25, 'sine', 0.12, 0.05); // C5 ping
    });

    // Event: Audio Toggle
    soundToggleBtn.addEventListener('click', () => {
        initAudio();
        soundEnabled = !soundEnabled;
        soundToggleBtn.classList.toggle('active', soundEnabled);
        soundToggleBtn.title = soundEnabled ? "Harmonic Audio Enabled" : "Harmonic Audio Muted";
        if (soundEnabled) playTone(523.25, 'triangle', 0.18, 0.06);
    });

    // Challenge Cards Click Handlers
    const challengeBtns = document.querySelectorAll('.challenge-action-btn');
    challengeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const targetMode = btn.getAttribute('data-target-mode');
            const targetVal = parseFloat(btn.getAttribute('data-target-val'));
            if (targetMode && MODES[targetMode]) {
                switchMode(targetMode);
                paramSlider.value = targetVal;
                paramSlider.dispatchEvent(new Event('input'));
                window.scrollTo({
                    top: canvas.getBoundingClientRect().top + window.scrollY - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Initial equation render
    switchMode('chaos');
});
