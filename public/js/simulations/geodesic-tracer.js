document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom CSS for premium styling
    const style = document.createElement('style');
    style.innerHTML = `
        .control-group {
            margin-bottom: 15px;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 12px;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }
        .control-group label {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            color: #e2e8f0;
            margin-bottom: 8px;
            font-family: 'Outfit', 'Inter', sans-serif;
        }
        .control-group input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            background: #1e293b;
            border-radius: 3px;
            outline: none;
        }
        .control-group input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: var(--accent-default, #38bdf8);
            cursor: pointer;
            transition: transform 0.1s;
        }
        .control-group input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.2);
        }
        .toggle-group {
            display: flex;
            gap: 8px;
            margin-top: 4px;
        }
        .toggle-btn {
            flex: 1;
            padding: 6px 12px;
            background: #0f172a;
            border: 1px solid #334155;
            color: #94a3b8;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.8rem;
            font-family: inherit;
            transition: all 0.2s;
            text-align: center;
        }
        .toggle-btn.active {
            background: rgba(56, 189, 248, 0.15);
            border-color: var(--accent-default, #38bdf8);
            color: #f8fafc;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
        }
        .preset-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            margin-top: 8px;
        }
        .preset-btn {
            padding: 6px;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid rgba(255,255,255,0.05);
            color: #cbd5e1;
            font-size: 0.75rem;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.15s;
        }
        .preset-btn:hover {
            background: rgba(56, 189, 248, 0.1);
            border-color: rgba(56, 189, 248, 0.3);
            color: #f8fafc;
        }
        .telemetry-card {
            background: rgba(2, 6, 23, 0.6);
            border: 1px solid rgba(56, 189, 248, 0.1);
            border-radius: 8px;
            padding: 12px;
            margin-top: 15px;
            font-family: 'Fira Code', monospace;
            font-size: 0.8rem;
        }
        .telemetry-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 4px;
        }
        .telemetry-label {
            color: #64748b;
        }
        .telemetry-val {
            color: #38bdf8;
            font-weight: 500;
        }
        .telemetry-status {
            text-align: center;
            font-weight: bold;
            padding: 4px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.75rem;
        }
        .status-orbiting { background: rgba(16, 185, 129, 0.15); color: #10b981; }
        .status-swallowed { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
        .status-escaped { background: rgba(59, 130, 246, 0.15); color: #3b82f6; }
        .status-dilated { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    `;
    document.head.appendChild(style);

    // Inject custom controls markup
    controls.innerHTML = `
        <div class="control-group">
            <label>Spacetime Geometry</label>
            <div class="toggle-group">
                <button id="geom-schwarz" class="toggle-btn active">Schwarzschild</button>
                <button id="geom-kerr" class="toggle-btn">Kerr (Rotating)</button>
            </div>
        </div>

        <div class="control-group" id="spin-group" style="display: none;">
            <label>Black Hole Spin (a): <span id="a-val" style="color: #38bdf8;">0.70</span></label>
            <input type="range" id="a-slider" min="-0.99" max="0.99" step="0.01" value="0.70">
            <div style="font-size: 0.7rem; color: #64748b; margin-top: 4px; text-align: right;">Negative values represent retrograde rotation</div>
        </div>

        <div class="control-group">
            <label>Launch Particle Type</label>
            <div class="toggle-group">
                <button id="type-photon" class="toggle-btn active">Photon (Light)</button>
                <button id="type-probe" class="toggle-btn">Massive Probe</button>
            </div>
        </div>

        <div class="control-group" id="speed-group" style="display: none;">
            <label>Initial Velocity (v/c): <span id="v-val" style="color: #38bdf8;">0.40</span></label>
            <input type="range" id="v-slider" min="0.10" max="0.95" step="0.01" value="0.40">
        </div>

        <div class="control-group">
            <label>Observer Frame</label>
            <div class="toggle-group">
                <button id="frame-coord" class="toggle-btn active">Coordinate (Frozen)</button>
                <button id="frame-proper" class="toggle-btn">Proper (Crosses Horizon)</button>
            </div>
        </div>

        <div class="control-group">
            <label>Orbits & Scenarios Presets</label>
            <div class="preset-grid">
                <button class="preset-btn" id="preset-precession">Einstein Precession</button>
                <button class="preset-btn" id="preset-photonsphere">Photon Sphere Orbit</button>
                <button class="preset-btn" id="preset-framedragging">Frame Dragging</button>
                <button class="preset-btn" id="preset-isco">ISCO Limit</button>
            </div>
        </div>

        <div class="control-group" style="display: flex; gap: 8px; background: transparent; border: none; padding: 0;">
            <button id="reset-sim" class="btn btn-secondary" style="flex: 1;">Clear Paths</button>
            <button id="play-pause" class="btn btn-primary" style="flex: 1; background: #38bdf8; color: #0f172a; font-weight: bold; border: none;">Pause</button>
        </div>

        <div class="telemetry-card" id="telemetry-panel" style="display: none;">
            <div class="telemetry-row">
                <span class="telemetry-label">Radius (r):</span>
                <span class="telemetry-val" id="tele-r">0.00 M</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Angular speed (dφ/dt):</span>
                <span class="telemetry-val" id="tele-omega">0.000 rad/s</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Energy (E):</span>
                <span class="telemetry-val" id="tele-E">0.000</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Ang. Momentum (L):</span>
                <span class="telemetry-val" id="tele-L">0.000</span>
            </div>
            <div class="telemetry-row">
                <span class="telemetry-label">Redshift (1+z):</span>
                <span class="telemetry-val" id="tele-redshift">1.000</span>
            </div>
            <div class="telemetry-status status-orbiting" id="tele-status">ORBITING</div>
        </div>
    `;

    // Elements lookup
    const geomSchwarz = document.getElementById('geom-schwarz');
    const geomKerr = document.getElementById('geom-kerr');
    const spinGroup = document.getElementById('spin-group');
    const aSlider = document.getElementById('a-slider');
    const aVal = document.getElementById('a-val');

    const typePhoton = document.getElementById('type-photon');
    const typeProbe = document.getElementById('type-probe');
    const speedGroup = document.getElementById('speed-group');
    const vSlider = document.getElementById('v-slider');
    const vVal = document.getElementById('v-val');

    const frameCoord = document.getElementById('frame-coord');
    const frameProper = document.getElementById('frame-proper');

    const presetPrecession = document.getElementById('preset-precession');
    const presetPhotonSphere = document.getElementById('preset-photonsphere');
    const presetFrameDragging = document.getElementById('preset-framedragging');
    const presetIsco = document.getElementById('preset-isco');

    const resetBtn = document.getElementById('reset-sim');
    const playPauseBtn = document.getElementById('play-pause');

    const telemetryPanel = document.getElementById('telemetry-panel');
    const teleR = document.getElementById('tele-r');
    const teleOmega = document.getElementById('tele-omega');
    const teleE = document.getElementById('tele-E');
    const teleL = document.getElementById('tele-L');
    const teleRedshift = document.getElementById('tele-redshift');
    const teleStatus = document.getElementById('tele-status');

    // Simulation constants
    const M = 1.0; 
    let a = 0.0; // spin
    let isKerr = false;
    let particleType = 'photon'; // photon, probe
    let initSpeedRatio = 0.40; // speed v/c for probes
    let isCoordinateTime = true; // Coordinate vs Proper time
    let isPlaying = true;

    // Canvas scaling
    let scale = 95; // pixels per M
    let cx, cy;

    // Interactive launch vector state
    let launchOrigin = null;
    let launchTarget = null;
    let isDraggingLaunch = false;

    // Active particle array
    let activeParticles = [];
    // Accretion disk dust particles
    let diskParticles = [];

    // Telemetry focus target
    let focusedParticle = null;

    // Dust particles helper
    function initDisk() {
        diskParticles = [];
        const numDust = 250;
        for (let i = 0; i < numDust; i++) {
            // Distribute dust between 3.5M and 12M
            const r = 3.5 + Math.random() * 8.5;
            const phi = Math.random() * Math.PI * 2;
            diskParticles.push({
                r: r,
                phi: phi,
                color: `rgba(${255 - Math.round(r * 10)}, ${100 + Math.round(r * 10)}, ${220 + Math.round(r * 3)}, ${0.12 + (1/r)*0.2})`,
                size: 1.0 + (10 / r) * Math.random()
            });
        }
    }

    function init() {
        cx = canvas.width / 2;
        cy = canvas.height / 2;
        initDisk();
    }

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 550;
        init();
    }
    window.addEventListener('resize', resize);
    resize();

    // Physics Engine: Kerr Equatorial Geodesic Integration (with Schwarzschild as a=0)
    function getDerivatives(r, phi, pr, E, L, a, mu) {
        const delta = r * r - 2 * M * r + a * a;
        
        // Inside singularity or horizon check
        const rPlus = M + Math.sqrt(Math.max(0, M * M - a * a));
        if (r <= rPlus || delta <= 0) {
            return { dr: 0, dphi: 0, dpr: 0, dt: 1, swallowed: true };
        }

        // Inverse metric components
        const g_tt = -(r * r + a * a + 2 * M * a * a / r) / delta;
        const g_tphi = -(2 * M * a) / (r * delta);
        const g_phiphi = (r - 2 * M) / (r * delta);
        const g_rr = delta / (r * r);

        // Geodesic derivatives with respect to affine parameter lambda
        const dr = g_rr * pr;
        const dphi = -g_tphi * E + g_phiphi * L;
        const dt = -g_tt * E + g_tphi * L;

        // Radial derivatives of inverse metric components
        const v = r * delta;
        const v2 = v * v;

        const dg_tt = (2 * M * r*r*r*r + 4 * M * a*a * r*r - 8 * M*M * a*a * r + 2 * M * a*a*a*a) / v2;
        const dg_tphi = (2 * M * a * (3 * r*r - 4 * M * r + a*a)) / v2;
        const dg_phiphi = (-2 * r*r*r + 8 * M * r*r - 8 * M*M * r + 2 * M * a*a) / v2;
        const dg_rr = (2 * M) / (r * r) - (2 * a * a) / (r * r * r);

        // Derivative of radial momentum
        const dpr = -0.5 * (dg_tt * E * E - 2 * dg_tphi * E * L + dg_phiphi * L * L + dg_rr * pr * pr);

        return { dr, dphi, dpr, dt, swallowed: false };
    }

    // Runge-Kutta 4th-Order (RK4) Step solver
    function rk4Step(state, dlambda, E, L, a, mu) {
        const k1 = getDerivatives(state.r, state.phi, state.pr, E, L, a, mu);
        if (k1.swallowed) return { ...state, swallowed: true };

        const s2 = {
            r: state.r + 0.5 * dlambda * k1.dr,
            phi: state.phi + 0.5 * dlambda * k1.dphi,
            pr: state.pr + 0.5 * dlambda * k1.dpr
        };
        const k2 = getDerivatives(s2.r, s2.phi, s2.pr, E, L, a, mu);
        if (k2.swallowed) return { ...state, swallowed: true };

        const s3 = {
            r: state.r + 0.5 * dlambda * k2.dr,
            phi: state.phi + 0.5 * dlambda * k2.dphi,
            pr: state.pr + 0.5 * dlambda * k2.dpr
        };
        const k3 = getDerivatives(s3.r, s3.phi, s3.pr, E, L, a, mu);
        if (k3.swallowed) return { ...state, swallowed: true };

        const s4 = {
            r: state.r + dlambda * k3.dr,
            phi: state.phi + dlambda * k3.dphi,
            pr: state.pr + dlambda * k3.dpr
        };
        const k4 = getDerivatives(s4.r, s4.phi, s4.pr, E, L, a, mu);
        if (k4.swallowed) return { ...state, swallowed: true };

        return {
            r: state.r + (dlambda / 6) * (k1.dr + 2 * k2.dr + 2 * k3.dr + k4.dr),
            phi: state.phi + (dlambda / 6) * (k1.dphi + 2 * k2.dphi + 2 * k3.dphi + k4.dphi),
            pr: state.pr + (dlambda / 6) * (k1.dpr + 2 * k2.dpr + 2 * k3.dpr + k4.dpr),
            dt: (k1.dt + 2 * k2.dt + 2 * k3.dt + k4.dt) / 6,
            swallowed: false
        };
    }

    // Resolves proper E, L, pr from initial coordinate state
    function resolveInitialConditions(r, phi, vr, vphi, particleType, speedRatio, a) {
        const delta = r * r - 2 * M * r + a * a;
        if (delta <= 0) return null;

        // Metric components at initial radius
        const g_tt = -(1 - 2 * M / r);
        const g_tphi = -2 * M * a / r;
        const g_phiphi = r * r + a * a + 2 * M * a * a / r;
        const g_rr = r * r / delta;

        const w = vphi; // dphi/dt coordinate angular velocity

        // Compute L/E ratio: b
        const num_b = g_tphi - w * (- (r * r + a * a + 2 * M * a * a / r) / delta);
        const den_b = ((r - 2 * M) / (r * delta)) - w * g_tphi;
        
        // Simpler formulation in BL coordinates
        const inv_g_tt = -(r * r + a * a + 2 * M * a * a / r) / delta;
        const inv_g_tphi = -(2 * M * a) / (r * delta);
        const inv_g_phiphi = (r - 2 * M) / (r * delta);

        const b = (inv_g_tphi - w * inv_g_tt) / (inv_g_phiphi - w * inv_g_tphi);

        // Metric constraint constant K
        const K = g_tt + 2 * g_tphi * w + g_phiphi * w * w + g_rr * vr * vr;

        const mu = (particleType === 'photon') ? 0 : 1;
        let E = 1.0;

        if (mu === 0) {
            // For photon, E is arbitrary scaling, set E=1
            E = 1.0;
        } else {
            // For massive probe, v = c * speedRatio
            // We adjust E to match the user's velocity setting relative to local speed of light
            // In coordinate time, the maximum velocity has K = 0.
            // Let's solve E^2 = -1 / (K * (-g^tt + b g^tphi)^2)
            const factor = inv_g_tt - b * inv_g_tphi;
            if (K >= 0) {
                // Hyper-relativistic check, cap speed
                return null;
            }
            E = 1.0 / (Math.sqrt(-K) * Math.abs(-inv_g_tt + b * inv_g_tphi));
        }

        const L = b * E;
        const dt_dlambda = E * (-inv_g_tt + b * inv_g_tphi);
        const pr = vr * dt_dlambda / (delta / (r * r));

        return { E, L, pr, mu };
    }

    // Launch a particle from canvas drag vector
    function launchParticle(xStart, yStart, xEnd, yEnd, type, speed, customParams = null) {
        // Center position relative B-L
        const px = (xStart - cx) / scale;
        const py = (yStart - cy) / scale;
        const r = Math.sqrt(px * px + py * py);
        const phi = Math.atan2(py, px);

        let vr = 0;
        let vphi = 0;

        if (customParams) {
            vr = customParams.vr;
            vphi = customParams.vphi;
        } else {
            // Compute coordinate velocity components from vector dx, dy
            const dx = (xEnd - xStart) / scale;
            const dy = (yEnd - yStart) / scale;

            // Project Cartesian coordinate velocities to polar coordinate velocities
            vr = (px * dx + py * dy) / r;
            vphi = (px * dy - py * dx) / (r * r);

            // Scale velocity according to particle type
            if (type === 'photon') {
                // Light speed coordinate velocity scaling
                // Scale so that it travels at light speed in coordinate terms:
                // g_tt + 2 g_tphi vphi + g_phiphi vphi^2 + g_rr vr^2 = 0
                // Let's scale vector (vr, vphi) by factor s to satisfy K = 0
                const g_tt = -(1 - 2 * M / r);
                const g_tphi = -2 * M * a / r;
                const g_phiphi = r * r + a * a + 2 * M * a * a / r;
                const g_rr = r * r / (r * r - 2 * M * r + a * a);

                const A = g_rr * vr * vr + g_phiphi * vphi * vphi;
                const B = 2 * g_tphi * vphi;
                const C = g_tt;

                // Solve s^2 A + s B + C = 0 for s > 0
                const disc = B * B - 4 * A * C;
                if (disc >= 0 && A > 0) {
                    const s = (-B + Math.sqrt(disc)) / (2 * A);
                    if (s > 0) {
                        vr *= s;
                        vphi *= s;
                    }
                } else {
                    // Fallback scaling
                    const speedScale = 0.05;
                    vr *= speedScale;
                    vphi *= speedScale;
                }
            } else {
                // Probe velocity scaling
                const speedScale = speed * 0.5; // scale to fit speed slider
                vr *= speedScale;
                vphi *= speedScale;
            }
        }

        const conds = customParams ? customParams : resolveInitialConditions(r, phi, vr, vphi, type, speed, a);
        if (!conds) return;

        const particle = {
            r: r,
            phi: phi,
            pr: conds.pr,
            E: conds.E,
            L: conds.L,
            mu: conds.mu,
            type: type,
            color: type === 'photon' ? '#e11d48' : '#38bdf8', // Red laser vs Cyan probe
            path: [{ r: r, phi: phi }],
            swallowed: false,
            escaped: false,
            frozen: false,
            age: 0
        };

        activeParticles.push(particle);
        focusedParticle = particle;
        telemetryPanel.style.display = 'block';
    }

    // Real-time integration path preview during dragging
    function getPreviewPath(xStart, yStart, xEnd, yEnd, type, speed) {
        const px = (xStart - cx) / scale;
        const py = (yStart - cy) / scale;
        const r = Math.sqrt(px * px + py * py);
        const phi = Math.atan2(py, px);

        const dx = (xEnd - xStart) / scale;
        const dy = (yEnd - yStart) / scale;

        let vr = (px * dx + py * dy) / r;
        let vphi = (px * dy - py * dx) / (r * r);

        // Same scaling as active particle
        if (type === 'photon') {
            const g_tt = -(1 - 2 * M / r);
            const g_tphi = -2 * M * a / r;
            const g_phiphi = r * r + a * a + 2 * M * a * a / r;
            const g_rr = r * r / (r * r - 2 * M * r + a * a);

            const A = g_rr * vr * vr + g_phiphi * vphi * vphi;
            const B = 2 * g_tphi * vphi;
            const C = g_tt;

            const disc = B * B - 4 * A * C;
            if (disc >= 0 && A > 0) {
                const s = (-B + Math.sqrt(disc)) / (2 * A);
                if (s > 0) {
                    vr *= s;
                    vphi *= s;
                }
            }
        } else {
            const speedScale = speed * 0.5;
            vr *= speedScale;
            vphi *= speedScale;
        }

        const conds = resolveInitialConditions(r, phi, vr, vphi, type, speed, a);
        if (!conds) return [];

        let state = { r, phi, pr: conds.pr };
        const previewPoints = [{ r: state.r, phi: state.phi }];

        const previewSteps = 70;
        let dlambda = type === 'photon' ? 0.08 : 0.15;

        for (let i = 0; i < previewSteps; i++) {
            const stepResult = rk4Step(state, dlambda, conds.E, conds.L, a, conds.mu);
            if (stepResult.swallowed) break;
            if (stepResult.r > 20) break; // escaped too far
            
            state = stepResult;
            previewPoints.push({ r: state.r, phi: state.phi });
        }

        return previewPoints;
    }

    // Preset Scenarios Loader
    function loadPreset(presetName) {
        activeParticles = [];
        focusedParticle = null;
        telemetryPanel.style.display = 'none';

        if (presetName === 'precession') {
            // Einstein Precession (elliptical orbit)
            isKerr = false;
            a = 0.0;
            particleType = 'probe';
            isCoordinateTime = false; // proper time shows precession beautifully

            // Update UI toggles
            updateUIState();

            // Spawn massive probe in elliptical orbit
            // At r = 8M, vphi = 0.14 rad/s, vr = 0.0
            const r0 = 8.0;
            const conds = resolveInitialConditions(r0, 0, 0.0, 0.10, 'probe', 0.35, 0.0);
            if (conds) {
                // Adjust L to create nice precession
                conds.L = 3.65;
                conds.E = 0.975;
                conds.pr = 0.0;
                
                launchParticle(cx + r0 * scale, cy, cx + r0 * scale, cy, 'probe', 0.35, conds);
            }

        } else if (presetName === 'photonsphere') {
            // Photon Sphere capture around Schwarzschild BH
            isKerr = false;
            a = 0.0;
            particleType = 'photon';
            isCoordinateTime = true;

            updateUIState();

            // Orbit at exactly r = 3M, L/E = 3sqrt(3) ~ 5.196
            const r0 = 3.001; // slightly outside to see orbit decay or spin around
            const conds = {
                E: 1.0,
                L: 3.0 * Math.sqrt(3) * 0.9995, // close to photon sphere impact parameter
                pr: 0.0,
                mu: 0
            };
            launchParticle(cx + r0 * scale, cy, cx + r0 * scale, cy + 10, 'photon', 1.0, conds);

        } else if (presetName === 'framedragging') {
            // Frame dragging of prograde vs retrograde photons
            isKerr = true;
            a = 0.95;
            particleType = 'photon';
            isCoordinateTime = true;

            updateUIState();

            // Retrograde photon: fired opposite to BH rotation direction
            // Gets dragged back around!
            // We launch from r=5M, fired downwards with negative momentum
            const r0 = 3.8;
            const condsRetro = {
                E: 1.0,
                L: -1.2, // negative angular momentum (retrograde)
                pr: -0.15, // moving inwards
                mu: 0
            };
            launchParticle(cx + r0 * scale * Math.cos(-Math.PI/6), cy + r0 * scale * Math.sin(-Math.PI/6), cx, cy, 'photon', 1.0, condsRetro);
            if (activeParticles.length > 0) {
                activeParticles[0].color = '#ef4444'; // Red for retrograde
            }

            // Prograde photon
            const condsPro = {
                E: 1.0,
                L: 3.5, // positive angular momentum (prograde)
                pr: -0.1,
                mu: 0
            };
            launchParticle(cx + r0 * scale * Math.cos(Math.PI/6), cy + r0 * scale * Math.sin(Math.PI/6), cx, cy, 'photon', 1.0, condsPro);
            if (activeParticles.length > 1) {
                activeParticles[1].color = '#10b981'; // Green for prograde
            }

        } else if (presetName === 'isco') {
            // ISCO: Innermost Stable Circular Orbit
            isKerr = false;
            a = 0.0;
            particleType = 'probe';
            isCoordinateTime = false;

            updateUIState();

            // Schwarzschild ISCO is at exactly r = 6M.
            // Circular velocity is sqrt(M/r) in Newtonian, in GR: L = sqrt(12)/2 = sqrt(3) ~ 3.464M
            const r0 = 6.0;
            const conds = {
                E: Math.sqrt(8/9), // ~ 0.943
                L: 2 * Math.sqrt(3), // ~ 3.464
                pr: 0.0,
                mu: 1
            };
            launchParticle(cx + r0 * scale, cy, cx + r0 * scale, cy + 10, 'probe', 0.40, conds);
        }
    }

    // UI Updates helpers
    function updateUIState() {
        if (isKerr) {
            geomKerr.classList.add('active');
            geomSchwarz.classList.remove('active');
            spinGroup.style.display = 'block';
        } else {
            geomSchwarz.classList.add('active');
            geomKerr.classList.remove('active');
            spinGroup.style.display = 'none';
        }

        if (particleType === 'photon') {
            typePhoton.classList.add('active');
            typeProbe.classList.remove('active');
            speedGroup.style.display = 'none';
        } else {
            typeProbe.classList.add('active');
            typePhoton.classList.remove('active');
            speedGroup.style.display = 'block';
        }

        if (isCoordinateTime) {
            frameCoord.classList.add('active');
            frameProper.classList.remove('active');
        } else {
            frameProper.classList.add('active');
            frameCoord.classList.remove('active');
        }

        aSlider.value = a;
        aVal.innerText = Number(a).toFixed(2);
        vSlider.value = initSpeedRatio;
        vVal.innerText = Number(initSpeedRatio).toFixed(2);
    }

    // Event handlers for UI
    geomSchwarz.onclick = () => { isKerr = false; a = 0.0; updateUIState(); };
    geomKerr.onclick = () => { isKerr = true; a = 0.70; updateUIState(); };
    aSlider.oninput = () => { a = parseFloat(aSlider.value); aVal.innerText = a.toFixed(2); };

    typePhoton.onclick = () => { particleType = 'photon'; updateUIState(); };
    typeProbe.onclick = () => { particleType = 'probe'; updateUIState(); };
    vSlider.oninput = () => { initSpeedRatio = parseFloat(vSlider.value); vVal.innerText = initSpeedRatio.toFixed(2); };

    frameCoord.onclick = () => { isCoordinateTime = true; updateUIState(); };
    frameProper.onclick = () => { isCoordinateTime = false; updateUIState(); };

    presetPrecession.onclick = () => loadPreset('precession');
    presetPhotonSphere.onclick = () => loadPreset('photonsphere');
    presetFrameDragging.onclick = () => loadPreset('framedragging');
    presetIsco.onclick = () => loadPreset('isco');

    resetBtn.onclick = () => {
        activeParticles = [];
        focusedParticle = null;
        telemetryPanel.style.display = 'none';
    };

    playPauseBtn.onclick = () => {
        isPlaying = !isPlaying;
        playPauseBtn.innerText = isPlaying ? 'Pause' : 'Play';
        playPauseBtn.style.background = isPlaying ? '#38bdf8' : '#10b981';
    };

    // Canvas Mouse / Touch Events
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        
        // Check if clicking close to an existing particle to focus on it
        let clickedParticle = false;
        for (let p of activeParticles) {
            const px = cx + p.r * Math.cos(p.phi) * scale;
            const py = cy + p.r * Math.sin(p.phi) * scale;
            const dist = Math.sqrt((pos.x - px) ** 2 + (pos.y - py) ** 2);
            if (dist < 12) {
                focusedParticle = p;
                telemetryPanel.style.display = 'block';
                clickedParticle = true;
                break;
            }
        }

        if (!clickedParticle) {
            launchOrigin = pos;
            launchTarget = pos;
            isDraggingLaunch = true;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDraggingLaunch) {
            launchTarget = getMousePos(e);
        }
    });

    canvas.addEventListener('mouseup', () => {
        if (isDraggingLaunch) {
            const dist = Math.sqrt((launchTarget.x - launchOrigin.x)**2 + (launchTarget.y - launchOrigin.y)**2);
            if (dist > 5) {
                launchParticle(launchOrigin.x, launchOrigin.y, launchTarget.x, launchTarget.y, particleType, initSpeedRatio);
            }
            isDraggingLaunch = false;
            launchOrigin = null;
            launchTarget = null;
        }
    });

    // Integration and animation loop
    function stepSimulation() {
        if (!isPlaying) return;

        // Swirl accretion disk dust particles
        for (let p of diskParticles) {
            // Kerr circular orbit velocity frequency Ω = sign(a) * M^(1/2) / (r^(3/2) + a)
            const dir = a === 0 ? 1 : Math.sign(a);
            const omega = dir * Math.sqrt(M) / (Math.pow(p.r, 1.5) + Math.abs(a));
            p.phi += omega * 0.45; // time multiplier
        }

        // Integrate active particles
        for (let p of activeParticles) {
            if (p.swallowed || p.escaped || p.frozen) continue;

            const rPlus = M + Math.sqrt(Math.max(0, M * M - a * a));

            // Select adaptive time step dlambda
            // If Coordinate Time, dlambda = dt_frame / (dt/dlambda)
            // Let's first evaluate dt/dlambda at current state
            const tempDerivs = getDerivatives(p.r, p.phi, p.pr, p.E, p.L, a, p.mu);
            if (tempDerivs.swallowed) {
                p.swallowed = true;
                continue;
            }

            let dlambda = p.type === 'photon' ? 0.08 : 0.12;

            if (isCoordinateTime) {
                // Shrink dlambda dynamically near horizon as dt/dlambda diverges
                const dt_dlambda = tempDerivs.dt;
                dlambda = Math.min(dlambda, 0.45 / dt_dlambda);
                
                // If step size is incredibly tiny, particle is effectively frozen
                if (dlambda < 1e-4) {
                    p.frozen = true;
                    continue;
                }
            }

            const nextState = rk4Step(p, dlambda, p.E, p.L, a, p.mu);

            if (nextState.swallowed) {
                p.swallowed = true;
                p.path.push({ r: rPlus, phi: p.phi });
            } else {
                p.r = nextState.r;
                p.phi = nextState.phi;
                p.pr = nextState.pr;
                p.age += dlambda;

                p.path.push({ r: p.r, phi: p.phi });

                // Escape check
                if (p.r > 28.0) {
                    p.escaped = true;
                }

                // Cap path length
                if (p.path.length > 1200) {
                    p.path.shift();
                }
            }
        }
    }

    function draw() {
        ctx.fillStyle = '#05070f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw coordinate grid helper (radial circles)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
        ctx.lineWidth = 1;
        for (let gridR = 2.0; gridR <= 16.0; gridR += 2.0) {
            ctx.beginPath();
            ctx.arc(cx, cy, gridR * scale, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Draw accretion disk dust particles
        for (let dust of diskParticles) {
            const dx = cx + dust.r * Math.cos(dust.phi) * scale;
            const dy = cy + dust.r * Math.sin(dust.phi) * scale;
            
            ctx.fillStyle = dust.color;
            ctx.beginPath();
            ctx.arc(dx, dy, dust.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw Event Horizon and Ergosphere
        const rPlus = M + Math.sqrt(Math.max(0, M * M - a * a));

        if (isKerr) {
            // Draw Ergosphere in equatorial slice (annulus from rPlus to 2M)
            const grad = ctx.createRadialGradient(cx, cy, rPlus * scale, cx, cy, 2.0 * scale);
            grad.addColorStop(0, 'rgba(124, 58, 237, 0.35)');
            grad.addColorStop(1, 'rgba(124, 58, 237, 0.0)');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(cx, cy, 2.0 * scale, 0, Math.PI * 2);
            ctx.fill();

            // Outer boundary dashed line
            ctx.strokeStyle = 'rgba(139, 92, 246, 0.3)';
            ctx.lineWidth = 1.0;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.arc(cx, cy, 2.0 * scale, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Draw Event Horizon shadow (Central Black Hole)
        ctx.fillStyle = '#000000';
        ctx.shadowBlur = 25;
        ctx.shadowColor = 'rgba(0,0,0,1)';
        ctx.beginPath();
        ctx.arc(cx, cy, rPlus * scale, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        // Draw Event Horizon outline
        ctx.strokeStyle = isKerr ? 'rgba(167, 139, 250, 0.6)' : 'rgba(255,255,255,0.2)';
        ctx.lineWidth = 2.0;
        ctx.beginPath();
        ctx.arc(cx, cy, rPlus * scale, 0, Math.PI * 2);
        ctx.stroke();

        // Draw Event Horizon labels
        ctx.fillStyle = '#94a3b8';
        ctx.font = '10px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`Horizon: r = ${rPlus.toFixed(3)} M`, cx, cy + 5);

        // Draw Photon Sphere dashed circle (r = 3M for Schwarzschild, prograde/retrograde vary, but 3M is nice baseline)
        if (!isKerr) {
            ctx.strokeStyle = 'rgba(249, 115, 22, 0.25)';
            ctx.lineWidth = 1.0;
            ctx.setLineDash([5, 5]);
            ctx.beginPath();
            ctx.arc(cx, cy, 3.0 * scale, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
            
            ctx.fillStyle = 'rgba(249, 115, 22, 0.5)';
            ctx.font = '9px monospace';
            ctx.fillText('Photon Sphere (3M)', cx, cy - 3.0 * scale - 6);
        }

        // Draw Active Particles paths and heads
        for (let p of activeParticles) {
            if (p.path.length < 2) continue;

            // Draw path line
            ctx.beginPath();
            const startX = cx + p.path[0].r * Math.cos(p.path[0].phi) * scale;
            const startY = cy + p.path[0].r * Math.sin(p.path[0].phi) * scale;
            ctx.moveTo(startX, startY);
            for (let i = 1; i < p.path.length; i++) {
                const x = cx + p.path[i].r * Math.cos(p.path[i].phi) * scale;
                const y = cy + p.path[i].r * Math.sin(p.path[i].phi) * scale;
                ctx.lineTo(x, y);
            }

            ctx.strokeStyle = p.color;
            ctx.lineWidth = p.type === 'photon' ? 1.5 : 2.0;
            ctx.stroke();

            // Draw head
            if (!p.swallowed && !p.escaped) {
                const px = cx + p.r * Math.cos(p.phi) * scale;
                const py = cy + p.r * Math.sin(p.phi) * scale;
                
                // Pulsing outer halo for focused particle
                if (focusedParticle === p) {
                    ctx.strokeStyle = p.color;
                    ctx.lineWidth = 1.0;
                    ctx.beginPath();
                    ctx.arc(px, py, 7 + Math.sin(Date.now() / 100) * 2, 0, Math.PI * 2);
                    ctx.stroke();
                }

                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.arc(px, py, p.type === 'photon' ? 3.5 : 4.5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Draw Interactive Drag Launch vector
        if (isDraggingLaunch && launchOrigin && launchTarget) {
            // Draw launch site dot
            ctx.fillStyle = particleType === 'photon' ? '#e11d48' : '#38bdf8';
            ctx.beginPath();
            ctx.arc(launchOrigin.x, launchOrigin.y, 4, 0, Math.PI * 2);
            ctx.fill();

            // Draw launch vector line
            ctx.strokeStyle = particleType === 'photon' ? 'rgba(225, 29, 72, 0.7)' : 'rgba(56, 189, 248, 0.7)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(launchOrigin.x, launchOrigin.y);
            ctx.lineTo(launchTarget.x, launchTarget.y);
            ctx.stroke();

            // Draw arrowhead
            const angle = Math.atan2(launchTarget.y - launchOrigin.y, launchTarget.x - launchOrigin.x);
            ctx.fillStyle = particleType === 'photon' ? '#e11d48' : '#38bdf8';
            ctx.beginPath();
            ctx.moveTo(launchTarget.x, launchTarget.y);
            ctx.lineTo(launchTarget.x - 8 * Math.cos(angle - Math.PI/6), launchTarget.y - 8 * Math.sin(angle - Math.PI/6));
            ctx.lineTo(launchTarget.x - 8 * Math.cos(angle + Math.PI/6), launchTarget.y - 8 * Math.sin(angle + Math.PI/6));
            ctx.fill();

            // Integrate and draw real-time path preview
            const preview = getPreviewPath(launchOrigin.x, launchOrigin.y, launchTarget.x, launchTarget.y, particleType, initSpeedRatio);
            if (preview.length > 1) {
                ctx.strokeStyle = 'rgba(255,255,255,0.15)';
                ctx.lineWidth = 1;
                ctx.setLineDash([3, 4]);
                ctx.beginPath();
                ctx.moveTo(cx + preview[0].r * Math.cos(preview[0].phi) * scale, cy + preview[0].r * Math.sin(preview[0].phi) * scale);
                for (let i = 1; i < preview.length; i++) {
                    ctx.lineTo(cx + preview[i].r * Math.cos(preview[i].phi) * scale, cy + preview[i].r * Math.sin(preview[i].phi) * scale);
                }
                ctx.stroke();
                ctx.setLineDash([]);
            }
        }

        // Update Telemetry Panel
        if (focusedParticle) {
            const p = focusedParticle;
            teleR.innerText = `${p.r.toFixed(3)} M`;
            
            const derivs = getDerivatives(p.r, p.phi, p.pr, p.E, p.L, a, p.mu);
            // Angular velocity dphi/dt = dphi/dlambda / dt/dlambda
            const omega = derivs.swallowed ? 0 : derivs.dphi / derivs.dt;
            teleOmega.innerText = `${omega.toFixed(4)} rad/s`;
            
            teleE.innerText = p.E.toFixed(4);
            teleL.innerText = p.L.toFixed(4);

            // Gravitational time dilation redshift factor 1+z = dt/dtau (for massive probe)
            // Or redshift parameter for light relative to infinity:
            // 1+z = dt/dlambda
            const redshift = derivs.swallowed ? Infinity : derivs.dt;
            teleRedshift.innerText = redshift === Infinity ? 'Infinity' : redshift.toFixed(3);

            // Update status text and class
            teleStatus.className = 'telemetry-status';
            if (p.swallowed) {
                teleStatus.innerText = 'SWALLOWED (IN SINGULARITY)';
                teleStatus.classList.add('status-swallowed');
            } else if (p.escaped) {
                teleStatus.innerText = 'ESCAPED SYSTEM';
                teleStatus.classList.add('status-escaped');
            } else if (p.frozen) {
                teleStatus.innerText = 'TIME DILATED (FROZEN)';
                teleStatus.classList.add('status-dilated');
            } else {
                teleStatus.innerText = 'ACTIVE ORBIT';
                teleStatus.classList.add('status-orbiting');
            }
        }
    }

    // Main animation loop
    function loop() {
        stepSimulation();
        draw();
        requestAnimationFrame(loop);
    }

    // Launch default initial state
    init();
    loadPreset('precession'); // start with Einstein precession preset
    loop();
});
