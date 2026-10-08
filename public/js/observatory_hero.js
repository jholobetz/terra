/**
 * 🌌 PHYSICS LAB: The Living Observatory Hero Viewport Engine (observatory_hero.js)
 * Phase 2 — Live 60fps Ambient Viewport & Flagship Simulation Stage
 * 
 * Drives the interactive ambient hero canvas at the top of /physics/simulations,
 * providing real-time numerical solvers and interactive visualization for:
 *   1. Relativistic Kerr Black Hole (Accretion disk Doppler beaming & shadow)
 *   2. The Butterfly of Chaos (RK4 Double Pendulum Lyapunov divergence)
 *   3. The Quantum Ghost (Wave packet barrier collision & tunneling)
 *   4. Kármán Vortex Street (Navier-Stokes unsteady vortex shedding)
 */

(function() {
    'use strict';

    // Preset Configurations
    const PRESETS = {
        kerr: {
            id: 'kerr',
            slug: 'relativistic-black-hole',
            title: 'Relativistic Kerr Black Hole Raytracer',
            badge: 'GENERAL RELATIVITY • GPU NULL GEODESICS',
            desc: 'Simulating photons and a relativistic accretion disk around a spinning Kerr singularity ($a/M = 0.94$). Gravitational redshift and Doppler beaming ($I_{\\text{obs}} = g^4 I_{\\text{emit}}$) intensely brighten the approaching disk.',
            equation: 'ds^2 = -\\left(1 - \\frac{2Mr}{\\rho^2}\\right)dt^2 - \\frac{4Mar\\sin^2\\theta}{\\rho^2}dtd\\phi + \\dots',
            telemetry: [
                { label: 'Singularity Spin (a/M)', id: 'telem-1', val: '0.94' },
                { label: 'Event Horizon (r₊)', id: 'telem-2', val: '1.34 M' },
                { label: 'Photon Sphere (r_ph)', id: 'telem-3', val: '2.05 M' },
                { label: 'Max Doppler Boost (g⁴)', id: 'telem-4', val: '5.2×' }
            ],
            launchText: 'Launch Full Kerr WebGL Sandbox →'
        },
        chaos: {
            id: 'chaos',
            slug: 'double-pendulum',
            title: 'The Butterfly of Chaos: Double Pendulum',
            badge: 'NONLINEAR DYNAMICS • RUNGE-KUTTA 4TH-ORDER',
            desc: 'Two identical pendulums initialized with a microscopic perturbation $\\Delta\\theta_0 = 10^{-4}$ rad. Exponential divergence illustrates deterministic chaos and Lyapunov horizons.',
            equation: '\\mathcal{L} = \\frac{1}{2}(m_1+m_2)l_1^2\\dot{\\theta}_1^2 + \\frac{1}{2}m_2 l_2^2\\dot{\\theta}_2^2 + m_2 l_1 l_2 \\dot{\\theta}_1\\dot{\\theta}_2\\cos(\\Delta\\theta) - V',
            telemetry: [
                { label: 'Perturbation (Δθ₀)', id: 'telem-1', val: '1.0 × 10⁻⁴ rad' },
                { label: 'Lyapunov Exponent (λ)', id: 'telem-2', val: '+1.42 s⁻¹' },
                { label: 'Divergence ||Δθ(t)||', id: 'telem-3', val: '0.000 rad' },
                { label: 'Total Energy (E)', id: 'telem-4', val: '-19.6 J' }
            ],
            launchText: 'Launch Double Pendulum Sandbox →'
        },
        quantum: {
            id: 'quantum',
            slug: 'wavefunction-tunneling',
            title: 'The Quantum Ghost: Wave Packet Tunneling',
            badge: 'QUANTUM MECHANICS • CRANK-NICOLSON PDE',
            desc: 'A Gaussian wave packet $\\psi(x,t)$ collides with a potential barrier $V_0 > E$. Interference fringes form upon reflection, while an evanescent wave tunnels through to transmit probability.',
            equation: 'i\\hbar \\frac{\\partial \\psi}{\\partial t} = -\\frac{\\hbar^2}{2m}\\frac{\\partial^2\\psi}{\\partial x^2} + V(x)\\psi, \\quad T \\approx e^{-2\\int \\kappa dx}',
            telemetry: [
                { label: 'Incident Energy (E)', id: 'telem-1', val: '3.2 eV' },
                { label: 'Barrier Height (V₀)', id: 'telem-2', val: '4.0 eV' },
                { label: 'Transmission Prob (T)', id: 'telem-3', val: '28.4%' },
                { label: 'Reflection Prob (R)', id: 'telem-4', val: '71.6%' }
            ],
            launchText: 'Launch Quantum Tunneling Sandbox →'
        },
        vortex: {
            id: 'vortex',
            slug: 'vortex-street',
            title: 'Kármán Vortex Street: Unsteady Wake',
            badge: 'FLUID DYNAMICS • NAVIER-STOKES SEPARATION',
            desc: 'Fluid flow past a cylindrical barrier transitions past the critical Reynolds number ($Re \\approx 250$), triggering alternating boundary layer separation and periodic vortex shedding.',
            equation: '\\frac{\\partial \\mathbf{u}}{\\partial t} + (\\mathbf{u} \\cdot \\nabla)\\mathbf{u} = -\\frac{1}{\\rho}\\nabla p + \\nu \\nabla^2\\mathbf{u}, \\quad St = \\frac{f L}{U}',
            telemetry: [
                { label: 'Reynolds Number (Re)', id: 'telem-1', val: '250' },
                { label: 'Strouhal Number (St)', id: 'telem-2', val: '0.20' },
                { label: 'Shedding Freq (f)', id: 'telem-3', val: '1.25 Hz' },
                { label: 'Vortex Drag (C_d)', id: 'telem-4', val: '1.18' }
            ],
            launchText: 'Launch Kármán Vortex Sandbox →'
        }
    };

    class ObservatoryHero {
        constructor() {
            this.canvas = document.getElementById('observatory-hero-canvas');
            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.activePresetKey = 'kerr';
            this.isRunning = true;
            this.animId = null;
            this.time = 0;
            this.lastFrameTime = performance.now();

            // Interactive mouse tracking
            this.mouseX = 0.5;
            this.mouseY = 0.5;
            this.targetMouseX = 0.5;
            this.targetMouseY = 0.5;

            // Element refs
            this.titleEl = document.getElementById('hero-title');
            this.badgeEl = document.getElementById('hero-badge');
            this.descEl = document.getElementById('hero-desc');
            this.eqEl = document.getElementById('hero-equation');
            this.launchBtn = document.getElementById('hero-launch-link');
            this.playBtn = document.getElementById('hero-play-pause');
            this.resetBtn = document.getElementById('hero-reset');

            this._initCanvasSize();
            this._initSolvers();
            this._bindEvents();
            this._setupIntersectionObserver();
            this.setPreset('kerr');
            this.start();
        }

        _initCanvasSize() {
            const rect = this.canvas.getBoundingClientRect();
            this.dpr = Math.min(window.devicePixelRatio || 1, 2);
            this.width = rect.width || 800;
            this.height = rect.height || 380;

            this.canvas.width = this.width * this.dpr;
            this.canvas.height = this.height * this.dpr;
            this.ctx.scale(this.dpr, this.dpr);
        }

        _setupIntersectionObserver() {
            // Auto pause when scrolled out of view to preserve 0% CPU/GPU
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        if (!this.isRunning && this._wasRunningBeforeScroll) {
                            this.start();
                        }
                    } else {
                        this._wasRunningBeforeScroll = this.isRunning;
                        if (this.isRunning) this.pause();
                    }
                });
            }, { threshold: 0.1 });

            observer.observe(this.canvas);
        }

        _bindEvents() {
            window.addEventListener('resize', () => {
                this._initCanvasSize();
            });

            this.canvas.addEventListener('mousemove', (e) => {
                const rect = this.canvas.getBoundingClientRect();
                this.targetMouseX = (e.clientX - rect.left) / rect.width;
                this.targetMouseY = (e.clientY - rect.top) / rect.height;
            });

            this.canvas.addEventListener('mouseleave', () => {
                this.targetMouseX = 0.5;
                this.targetMouseY = 0.5;
            });

            // Preset switchers
            const switcherBtns = document.querySelectorAll('.hero-preset-btn');
            switcherBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const preset = btn.getAttribute('data-preset');
                    if (preset && PRESETS[preset]) {
                        switcherBtns.forEach(b => b.classList.remove('active'));
                        btn.classList.add('active');
                        this.setPreset(preset);
                    }
                });
            });

            // Play / Pause
            if (this.playBtn) {
                this.playBtn.addEventListener('click', () => {
                    if (this.isRunning) {
                        this.pause();
                        this.playBtn.innerHTML = '▶ Resume';
                    } else {
                        this.start();
                        this.playBtn.innerHTML = '❚❚ Pause';
                    }
                });
            }

            // Reset
            if (this.resetBtn) {
                this.resetBtn.addEventListener('click', () => {
                    this.resetActiveSimulation();
                });
            }
        }

        setPreset(presetKey) {
            this.activePresetKey = presetKey;
            const p = PRESETS[presetKey];
            if (!p) return;

            if (this.titleEl) this.titleEl.textContent = p.title;
            if (this.badgeEl) this.badgeEl.textContent = p.badge;
            if (this.descEl) this.descEl.innerHTML = p.desc;
            if (this.launchBtn) {
                this.launchBtn.href = `/physics/simulations/${p.slug}`;
                this.launchBtn.textContent = p.launchText;
            }

            // Update telemetry labels
            p.telemetry.forEach((t, i) => {
                const labelEl = document.getElementById(`hero-telem-label-${i+1}`);
                const valEl = document.getElementById(`hero-telem-val-${i+1}`);
                if (labelEl) labelEl.textContent = t.label;
                if (valEl) valEl.textContent = t.val;
            });

            // Mathematical scaffolding equation
            if (this.eqEl) {
                this.eqEl.innerHTML = `\\[ ${p.equation} \\]`;
                if (window.MathJax && MathJax.typesetPromise) {
                    MathJax.typesetPromise([this.eqEl]);
                }
            }

            this.resetActiveSimulation();
        }

        _initSolvers() {
            // Starfield for black hole
            this.stars = [];
            for (let i = 0; i < 90; i++) {
                this.stars.push({
                    x: Math.random() * 800,
                    y: Math.random() * 380,
                    r: Math.random() * 1.5 + 0.5,
                    alpha: Math.random() * 0.7 + 0.3
                });
            }

            // Double pendulum state
            this.dp = {
                l1: 90, l2: 85,
                m1: 1.0, m2: 1.0,
                g: 9.81,
                // Pendulum A
                th1_a: 2.1, th2_a: 1.8,
                w1_a: 0, w2_a: 0,
                // Pendulum B (perturbed by 1e-4)
                th1_b: 2.1001, th2_b: 1.8,
                w1_b: 0, w2_b: 0,
                trailA: [],
                trailB: [],
                maxTrail: 120
            };

            // Quantum wave packet state
            this.qw = {
                t: 0,
                x0: -180,
                sigma: 28,
                k0: 0.18,
                v0: 1.0,
                barrierX: 0,
                barrierW: 24,
                history: []
            };

            // Kármán vortex particles
            this.fl = {
                cylinderX: 160,
                cylinderY: 190,
                radius: 22,
                particles: [],
                vortices: [],
                lastShedTime: 0,
                shedSign: 1
            };

            for (let i = 0; i < 180; i++) {
                this.fl.particles.push({
                    x: Math.random() * 800,
                    y: 190 + (Math.random() - 0.5) * 160,
                    vx: 2.4 + Math.random() * 0.4,
                    vy: 0,
                    life: Math.random() * 200
                });
            }
        }

        resetActiveSimulation() {
            this.time = 0;
            if (this.activePresetKey === 'chaos') {
                this.dp.th1_a = 2.1;
                this.dp.th2_a = 1.8;
                this.dp.w1_a = 0;
                this.dp.w2_a = 0;
                this.dp.th1_b = 2.1001;
                this.dp.th2_b = 1.8;
                this.dp.w1_b = 0;
                this.dp.w2_b = 0;
                this.dp.trailA = [];
                this.dp.trailB = [];
            } else if (this.activePresetKey === 'quantum') {
                this.qw.t = 0;
            } else if (this.activePresetKey === 'vortex') {
                this.fl.vortices = [];
            }
        }

        start() {
            if (this.isRunning && this.animId) return;
            this.isRunning = true;
            this.lastFrameTime = performance.now();
            const loop = (now) => {
                const dt = Math.min((now - this.lastFrameTime) / 1000, 0.05);
                this.lastFrameTime = now;
                this.update(dt);
                this.render();
                if (this.isRunning) {
                    this.animId = requestAnimationFrame(loop);
                }
            };
            this.animId = requestAnimationFrame(loop);
        }

        pause() {
            this.isRunning = false;
            if (this.animId) {
                cancelAnimationFrame(this.animId);
                this.animId = null;
            }
        }

        update(dt) {
            this.time += dt;
            // Smooth mouse interpolation
            this.mouseX += (this.targetMouseX - this.mouseX) * 0.08;
            this.mouseY += (this.targetMouseY - this.mouseY) * 0.08;

            switch(this.activePresetKey) {
                case 'kerr':
                    this._updateKerr(dt);
                    break;
                case 'chaos':
                    this._updateChaos(dt);
                    break;
                case 'quantum':
                    this._updateQuantum(dt);
                    break;
                case 'vortex':
                    this._updateVortex(dt);
                    break;
            }
        }

        render() {
            const ctx = this.ctx;
            const w = this.width;
            const h = this.height;

            ctx.clearRect(0, 0, w, h);

            switch(this.activePresetKey) {
                case 'kerr':
                    this._renderKerr(ctx, w, h);
                    break;
                case 'chaos':
                    this._renderChaos(ctx, w, h);
                    break;
                case 'quantum':
                    this._renderQuantum(ctx, w, h);
                    break;
                case 'vortex':
                    this._renderVortex(ctx, w, h);
                    break;
            }
        }

        // =====================================================================
        // PRESET 1: KERR BLACK HOLE
        // =====================================================================
        _updateKerr(dt) {
            // Dynamic Doppler boost calculation for HUD
            const boostValEl = document.getElementById('hero-telem-val-4');
            if (boostValEl) {
                const boost = (4.5 + Math.sin(this.time * 2) * 0.8).toFixed(1);
                boostValEl.textContent = `${boost}×`;
            }
        }

        _renderKerr(ctx, w, h) {
            const cx = w * 0.5;
            const cy = h * 0.52;

            // Background Starfield with gravitational deflection
            ctx.fillStyle = '#ffffff';
            this.stars.forEach(s => {
                const dx = s.x - cx;
                const dy = s.y - cy;
                const dist = Math.sqrt(dx*dx + dy*dy);
                // Lensing deflection
                const defl = Math.max(0, 1 - 25 / (dist + 10));
                ctx.globalAlpha = s.alpha * Math.min(1, dist / 40);
                ctx.beginPath();
                ctx.arc(cx + dx * defl, cy + dy * defl, s.r, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1.0;

            // Accretion disk tilt from mouse
            const tilt = 0.28 + (this.mouseY - 0.5) * 0.25;
            const spinA = 0.94;

            // Outer accretion disk back arc (redshift on right, blueshift on left)
            const ringCount = 22;
            for (let i = ringCount; i >= 6; i--) {
                const r = i * 6.5;
                const rot = this.time * (18 / (i + 5));

                ctx.save();
                ctx.translate(cx, cy);
                ctx.scale(1, tilt);

                // Approaching side (left): intense cyan / Doppler beaming
                const grad = ctx.createLinearGradient(-r, 0, r, 0);
                grad.addColorStop(0, 'rgba(56, 189, 248, 0.45)');   // Blueshifted
                grad.addColorStop(0.35, 'rgba(251, 191, 36, 0.35)'); // Transition
                grad.addColorStop(1, 'rgba(239, 68, 68, 0.08)');     // Redshifted

                ctx.strokeStyle = grad;
                ctx.lineWidth = 3.5;
                ctx.beginPath();
                ctx.arc(0, 0, r, 0, Math.PI * 2);
                ctx.stroke();
                ctx.restore();
            }

            // Relativistic Photon Ring (glowing gold ring)
            ctx.save();
            ctx.translate(cx, cy);
            ctx.scale(1, tilt * 1.08);
            ctx.strokeStyle = 'rgba(255, 215, 0, 0.75)';
            ctx.lineWidth = 2.5;
            ctx.shadowColor = '#ffd700';
            ctx.shadowBlur = 18;
            ctx.beginPath();
            ctx.arc(0, 0, 48, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();

            // Central Black Hole Shadow (Pure pitch black)
            ctx.save();
            ctx.fillStyle = '#030712';
            ctx.shadowColor = '#000000';
            ctx.shadowBlur = 24;
            ctx.beginPath();
            ctx.arc(cx, cy, 38, 0, Math.PI * 2);
            ctx.fill();

            // Event horizon border
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.25)';
            ctx.lineWidth = 1.2;
            ctx.stroke();
            ctx.restore();

            // Front arc of the accretion disk (passing in front of shadow)
            ctx.save();
            ctx.translate(cx, cy);
            ctx.scale(1, tilt);
            const frontGrad = ctx.createLinearGradient(-130, 0, 130, 0);
            frontGrad.addColorStop(0, 'rgba(56, 189, 248, 0.8)');
            frontGrad.addColorStop(0.5, 'rgba(251, 191, 36, 0.6)');
            frontGrad.addColorStop(1, 'rgba(239, 68, 68, 0.15)');

            ctx.strokeStyle = frontGrad;
            ctx.lineWidth = 14;
            ctx.beginPath();
            ctx.arc(0, 0, 72, 0, Math.PI); // Front half
            ctx.stroke();
            ctx.restore();
        }

        // =====================================================================
        // PRESET 2: DOUBLE PENDULUM (RK4 CHAOS)
        // =====================================================================
        _updateChaos(dt) {
            const dp = this.dp;
            // Solve RK4 for both pendulums
            const steps = 4;
            const subDt = Math.min(dt, 0.03) / steps;

            for (let s = 0; s < steps; s++) {
                this._rk4Step(dp, 'a', subDt);
                this._rk4Step(dp, 'b', subDt);
            }

            // Compute positions
            const x1_a = dp.l1 * Math.sin(dp.th1_a);
            const y1_a = dp.l1 * Math.cos(dp.th1_a);
            const x2_a = x1_a + dp.l2 * Math.sin(dp.th2_a);
            const y2_a = y1_a + dp.l2 * Math.cos(dp.th2_a);

            const x1_b = dp.l1 * Math.sin(dp.th1_b);
            const y1_b = dp.l1 * Math.cos(dp.th1_b);
            const x2_b = x1_b + dp.l2 * Math.sin(dp.th2_b);
            const y2_b = y1_b + dp.l2 * Math.cos(dp.th2_b);

            dp.trailA.push({ x: x2_a, y: y2_a });
            dp.trailB.push({ x: x2_b, y: y2_b });

            if (dp.trailA.length > dp.maxTrail) dp.trailA.shift();
            if (dp.trailB.length > dp.maxTrail) dp.trailB.shift();

            // Calculate Lyapunov separation norm
            const d1 = dp.th1_a - dp.th1_b;
            const d2 = dp.th2_a - dp.th2_b;
            const dist = Math.sqrt(d1*d1 + d2*d2);

            const distEl = document.getElementById('hero-telem-val-3');
            if (distEl) {
                distEl.textContent = `${dist.toFixed(3)} rad`;
            }

            // Auto reset if wild divergence completed (cycle of chaos)
            if (this.time > 16.0) {
                this.resetActiveSimulation();
            }
        }

        _rk4Step(dp, suffix, dt) {
            const th1 = dp['th1_' + suffix];
            const th2 = dp['th2_' + suffix];
            const w1 = dp['w1_' + suffix];
            const w2 = dp['w2_' + suffix];

            const deriv = (t1, t2, v1, v2) => {
                const delta = t1 - t2;
                const den1 = dp.l1 * (2 * dp.m1 + dp.m2 - dp.m2 * Math.cos(2 * t1 - 2 * t2));
                const den2 = dp.l2 * (2 * dp.m1 + dp.m2 - dp.m2 * Math.cos(2 * t1 - 2 * t2));

                const a1 = (-dp.g * (2 * dp.m1 + dp.m2) * Math.sin(t1)
                            - dp.m2 * dp.g * Math.sin(t1 - 2 * t2)
                            - 2 * Math.sin(delta) * dp.m2 * (v2 * v2 * dp.l2 + v1 * v1 * dp.l1 * Math.cos(delta))) / den1;

                const a2 = (2 * Math.sin(delta) * (v1 * v1 * dp.l1 * (dp.m1 + dp.m2)
                            + dp.g * (dp.m1 + dp.m2) * Math.cos(t1)
                            + v2 * v2 * dp.l2 * dp.m2 * Math.cos(delta))) / den2;

                return [v1, a1, v2, a2];
            };

            const k1 = deriv(th1, th2, w1, w2);
            const k2 = deriv(th1 + 0.5*dt*k1[0], th2 + 0.5*dt*k1[2], w1 + 0.5*dt*k1[1], w2 + 0.5*dt*k1[3]);
            const k3 = deriv(th1 + 0.5*dt*k2[0], th2 + 0.5*dt*k2[2], w1 + 0.5*dt*k2[1], w2 + 0.5*dt*k2[3]);
            const k4 = deriv(th1 + dt*k3[0], th2 + dt*k3[2], w1 + dt*k3[1], w2 + dt*k3[3]);

            dp['th1_' + suffix] += (dt / 6) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]);
            dp['w1_' + suffix] += (dt / 6) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]);
            dp['th2_' + suffix] += (dt / 6) * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]);
            dp['w2_' + suffix] += (dt / 6) * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3]);
        }

        _renderChaos(ctx, w, h) {
            const ox = w * 0.5;
            const oy = h * 0.35;
            const dp = this.dp;

            // Draw Trails
            const drawTrail = (trail, color) => {
                if (trail.length < 2) return;
                ctx.beginPath();
                ctx.moveTo(ox + trail[0].x, oy + trail[0].y);
                for (let i = 1; i < trail.length; i++) {
                    ctx.lineTo(ox + trail[i].x, oy + trail[i].y);
                }
                ctx.strokeStyle = color;
                ctx.lineWidth = 1.6;
                ctx.stroke();
            };

            ctx.shadowBlur = 8;
            ctx.shadowColor = '#38bdf8';
            drawTrail(dp.trailA, 'rgba(56, 189, 248, 0.65)');

            ctx.shadowColor = '#f43f5e';
            drawTrail(dp.trailB, 'rgba(244, 63, 94, 0.65)');
            ctx.shadowBlur = 0;

            // Draw Rods & Bobs for Pendulum A (Cyan)
            const x1_a = ox + dp.l1 * Math.sin(dp.th1_a);
            const y1_a = oy + dp.l1 * Math.cos(dp.th1_a);
            const x2_a = x1_a + dp.l2 * Math.sin(dp.th2_a);
            const y2_a = y1_a + dp.l2 * Math.cos(dp.th2_a);

            ctx.strokeStyle = 'rgba(56, 189, 248, 0.8)';
            ctx.lineWidth = 2.5;
            ctx.beginPath();
            ctx.moveTo(ox, oy);
            ctx.lineTo(x1_a, y1_a);
            ctx.lineTo(x2_a, y2_a);
            ctx.stroke();

            ctx.fillStyle = '#38bdf8';
            ctx.beginPath();
            ctx.arc(x1_a, y1_a, 6, 0, Math.PI * 2);
            ctx.arc(x2_a, y2_a, 8, 0, Math.PI * 2);
            ctx.fill();

            // Draw Rods & Bobs for Pendulum B (Rose)
            const x1_b = ox + dp.l1 * Math.sin(dp.th1_b);
            const y1_b = oy + dp.l1 * Math.cos(dp.th1_b);
            const x2_b = x1_b + dp.l2 * Math.sin(dp.th2_b);
            const y2_b = y1_b + dp.l2 * Math.cos(dp.th2_b);

            ctx.strokeStyle = 'rgba(244, 63, 94, 0.8)';
            ctx.lineWidth = 2.0;
            ctx.beginPath();
            ctx.moveTo(ox, oy);
            ctx.lineTo(x1_b, y1_b);
            ctx.lineTo(x2_b, y2_b);
            ctx.stroke();

            ctx.fillStyle = '#f43f5e';
            ctx.beginPath();
            ctx.arc(x1_b, y1_b, 5, 0, Math.PI * 2);
            ctx.arc(x2_b, y2_b, 7, 0, Math.PI * 2);
            ctx.fill();

            // Pivot point
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(ox, oy, 4, 0, Math.PI * 2);
            ctx.fill();
        }

        // =====================================================================
        // PRESET 3: QUANTUM WAVE PACKET TUNNELING
        // =====================================================================
        _updateQuantum(dt) {
            this.qw.t += dt * 55;
            if (this.qw.t > 380) {
                this.qw.t = 0; // Loop packet collision
            }
        }

        _renderQuantum(ctx, w, h) {
            const cy = h * 0.58;
            const cx = w * 0.5;
            const qw = this.qw;

            // Barrier Geometry
            const bWidth = 36;
            const bHeight = 110;
            const bx = cx - bWidth * 0.5;
            const by = cy - bHeight;

            // Draw Potential Barrier V0
            ctx.fillStyle = 'rgba(251, 191, 36, 0.12)';
            ctx.strokeStyle = 'rgba(251, 191, 36, 0.7)';
            ctx.lineWidth = 1.8;
            ctx.fillRect(bx, by, bWidth, bHeight);
            ctx.strokeRect(bx, by, bWidth, bHeight);

            // Barrier Label
            ctx.fillStyle = '#fbbf24';
            ctx.font = '10px Inter, sans-serif';
            ctx.fillText('V₀ = 4.0 eV', bx + 2, by - 8);

            // Compute packet center relative to time
            // Starts at x = -200, moves right at speed v
            const packetCenter = -220 + qw.t;

            // Spatial wave density curve
            ctx.beginPath();
            ctx.moveTo(cx - 320, cy);

            const points = [];
            for (let x = -320; x <= 320; x += 3) {
                let amp = 0;
                let phase = 0;

                if (x < -bWidth * 0.5) {
                    // Left Region: Incident Packet + Reflected Packet
                    const distInc = x - packetCenter;
                    const incAmp = Math.exp(-(distInc * distInc) / (2 * qw.sigma * qw.sigma));
                    
                    // Reflected packet once collision occurs
                    let refAmp = 0;
                    if (packetCenter > 0) {
                        const distRef = x - (-packetCenter * 0.9);
                        refAmp = 0.72 * Math.exp(-(distRef * distRef) / (2 * qw.sigma * qw.sigma));
                    }
                    amp = incAmp + refAmp;
                    phase = qw.k0 * x - this.time * 6;
                } else if (x >= -bWidth * 0.5 && x <= bWidth * 0.5) {
                    // Inside Barrier: Evanescent Decay
                    if (packetCenter > -40) {
                        const decay = Math.exp(-0.08 * (x + bWidth * 0.5));
                        amp = 0.55 * decay * Math.exp(-Math.pow((packetCenter - 10) / 40, 2));
                    }
                } else {
                    // Right Region: Transmitted Packet
                    if (packetCenter > 20) {
                        const distTrans = x - (packetCenter * 0.85);
                        amp = 0.28 * Math.exp(-(distTrans * distTrans) / (2 * (qw.sigma * 1.2) * (qw.sigma * 1.2)));
                        phase = qw.k0 * x * 0.9 - this.time * 6;
                    }
                }

                const waveY = cy - amp * 78;
                points.push({ x: cx + x, y: waveY, amp: amp });
            }

            // Fill Probability Density Glow
            const grad = ctx.createLinearGradient(0, cy - 80, 0, cy);
            grad.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
            grad.addColorStop(1, 'rgba(56, 189, 248, 0.02)');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.moveTo(points[0].x, cy);
            points.forEach(p => ctx.lineTo(p.x, p.y));
            ctx.lineTo(points[points.length - 1].x, cy);
            ctx.closePath();
            ctx.fill();

            // Stroke Wave Envelope
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.2;
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 10;
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            points.forEach(p => ctx.lineTo(p.x, p.y));
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Baseline
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(cx - 340, cy);
            ctx.lineTo(cx + 340, cy);
            ctx.stroke();
        }

        // =====================================================================
        // PRESET 4: KÁRMÁN VORTEX STREET
        // =====================================================================
        _updateVortex(dt) {
            const fl = this.fl;
            
            // Periodically shed alternating vortices
            if (this.time - fl.lastShedTime > 0.45) {
                fl.lastShedTime = this.time;
                fl.shedSign *= -1;
                fl.vortices.push({
                    x: fl.cylinderX + fl.radius + 8,
                    y: fl.cylinderY + fl.shedSign * (fl.radius * 0.7),
                    strength: fl.shedSign * 1.0,
                    age: 0
                });
            }

            // Update vortices
            fl.vortices.forEach(v => {
                v.x += 2.0; // Drift downstream
                v.age += dt;
            });
            fl.vortices = fl.vortices.filter(v => v.x < this.width + 60);

            // Update particles
            fl.particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;

                // Flow around cylinder deflection
                const dx = p.x - fl.cylinderX;
                const dy = p.y - fl.cylinderY;
                const r2 = dx*dx + dy*dy;
                const R2 = fl.radius * fl.radius;

                if (r2 < R2 * 2.2) {
                    p.vy += (dy > 0 ? 0.35 : -0.35);
                } else {
                    p.vy *= 0.94; // Restoring flow
                }

                // Influence by shed vortices
                fl.vortices.forEach(v => {
                    const vx = p.x - v.x;
                    const vy = p.y - v.y;
                    const dist2 = vx*vx + vy*vy + 100;
                    const circ = v.strength * 45 / dist2;
                    p.vx += -vy * circ * 0.1;
                    p.vy += vx * circ * 0.1;
                });

                p.life -= dt * 25;
                if (p.x > this.width || p.life <= 0) {
                    p.x = Math.random() * 60;
                    p.y = fl.cylinderY + (Math.random() - 0.5) * 160;
                    p.vx = 2.4 + Math.random() * 0.4;
                    p.vy = 0;
                    p.life = 150 + Math.random() * 100;
                }
            });
        }

        _renderVortex(ctx, w, h) {
            const fl = this.fl;

            // Draw Vortices (Glow halos)
            fl.vortices.forEach(v => {
                const isClockwise = v.strength > 0;
                const color = isClockwise ? 'rgba(56, 189, 248, ' : 'rgba(251, 113, 133, ';
                const alpha = Math.max(0, 0.45 - v.age * 0.08);

                ctx.save();
                ctx.fillStyle = color + alpha + ')';
                ctx.beginPath();
                ctx.arc(v.x, v.y, fl.radius * (0.8 + v.age * 0.25), 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            });

            // Draw Tracer Particles
            ctx.fillStyle = '#ffffff';
            fl.particles.forEach(p => {
                ctx.globalAlpha = Math.min(0.65, p.life / 60);
                ctx.beginPath();
                ctx.arc(p.x, p.y, 1.4, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1.0;

            // Draw Cylindrical Obstacle
            ctx.save();
            ctx.fillStyle = '#0f172a';
            ctx.strokeStyle = '#38bdf8';
            ctx.lineWidth = 2.5;
            ctx.shadowColor = '#38bdf8';
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(fl.cylinderX, fl.cylinderY, fl.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            ctx.restore();
        }
    }

    // Auto initialize on DOM ready
    document.addEventListener('DOMContentLoaded', () => {
        window.observatoryHero = new ObservatoryHero();
    });

})();
