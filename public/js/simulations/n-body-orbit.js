/**
 * 🌌 PHYSICS LAB: N-Body Gravitational Choreography & Lagrange Dynamics
 *
 * High-precision symplectic Velocity Verlet N-body gravitational simulator featuring:
 * - 6 zero-drift barycentric presets (Chenciner–Montgomery Figure-8, Keplerian Solar System,
 *   Lagrange L4/L5 Trojan Equilateral Points, Binary Star + Circumbinary Planets,
 *   Hierarchical Star–Planet–Moon Hill Sphere, and Chaotic 3-Body Scattering)
 * - Real-time forward-integrated slingshot trajectory prediction curve
 * - Selectable launch body mass classes (Asteroid, Rocky Planet, Gas Giant, Companion Star)
 * - Barycenter (R_CM) rest-frame lock, velocity/gravity vector overlays, and conservation telemetry
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject Glassmorphic Controls Panel
    controls.innerHTML = `
        <!-- 1. Celestial Choreography Presets -->
        <div class="control-group">
            <label style="font-weight: 600; color: #fff; margin-bottom: 6px; display: block; font-size: 0.8rem;">
                Celestial Choreography Presets:
            </label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button type="button" data-preset="figure8" class="btn btn-primary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px; background: linear-gradient(135deg, #0284c7, #6366f1); border: none;">
                    ∞ Figure-8 (3-Body)
                </button>
                <button type="button" data-preset="lagrange" class="btn btn-secondary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px;">
                    △ Lagrange L4 / L5
                </button>
                <button type="button" data-preset="solarsystem" class="btn btn-secondary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px;">
                    ☀️ Kepler Solar System
                </button>
                <button type="button" data-preset="binary" class="btn btn-secondary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px;">
                    ✦ Binary + Planets
                </button>
                <button type="button" data-preset="hierarchical" class="btn btn-secondary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px;">
                    🌙 Star–Planet–Moon
                </button>
                <button type="button" data-preset="chaotic3" class="btn btn-secondary nbody-preset-btn" style="font-size: 0.74rem; padding: 6px 8px;">
                    ⚡ Chaotic 3-Body
                </button>
            </div>
        </div>

        <!-- 2. Gravitational Constant & Time Warp Sliders -->
        <div class="control-group">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                <label for="g-slider">Gravitational Constant (G):</label>
                <span id="g-val" class="math-value" style="color: #38bdf8; font-weight: 700;">1.50</span>
            </div>
            <input type="range" id="g-slider" min="0.3" max="4.5" step="0.05" value="1.50" style="width: 100%;">
        </div>

        <div class="control-group">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                <label for="speed-slider">Simulation Time Rate:</label>
                <span id="speed-val" class="math-value" style="color: #34d399; font-weight: 700;">1.0×</span>
            </div>
            <input type="range" id="speed-slider" min="0.2" max="2.5" step="0.1" value="1.0" style="width: 100%;">
        </div>

        <!-- 3. Slingshot Launch Body Class -->
        <div class="control-group">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; font-size: 0.78rem;">
                <label for="launch-mass-select" style="margin: 0; color: #cbd5e1;">Slingshot Launch Body:</label>
                <span style="font-size: 0.68rem; color: #64ffda;">Drag on canvas to aim</span>
            </div>
            <select id="launch-mass-select" style="width: 100%; background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(100, 255, 218, 0.3); color: #f8fafc; border-radius: 6px; padding: 6px 8px; font-size: 0.76rem; outline: none; cursor: pointer;">
                <option value="5">☄️ Test Asteroid (m = 5 — Probe)</option>
                <option value="45" selected>🌍 Rocky Planet (m = 45 — Terrestrial)</option>
                <option value="320">🪐 Gas Giant (m = 320 — Jovian)</option>
                <option value="2200">🌟 Companion Star (m = 2,200 — Stellar)</option>
            </select>
        </div>

        <!-- 4. Visual & Frame Toggles -->
        <div class="control-group" style="display: grid; grid-template-columns: 1fr 1fr; gap: 7px; font-size: 0.75rem; color: #cbd5e1;">
            <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; margin: 0;">
                <input type="checkbox" id="toggle-barycenter" checked style="accent-color: #64ffda; cursor: pointer;">
                <span>Barycenter (R_CM)</span>
            </label>
            <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; margin: 0;">
                <input type="checkbox" id="toggle-com-lock" checked style="accent-color: #64ffda; cursor: pointer;">
                <span>Lock Rest Frame</span>
            </label>
            <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; margin: 0;">
                <input type="checkbox" id="toggle-vectors" style="accent-color: #38bdf8; cursor: pointer;">
                <span>Velocity / Force Vecs</span>
            </label>
            <label style="display: flex; align-items: center; gap: 6px; cursor: pointer; margin: 0;">
                <input type="checkbox" id="toggle-collisions" checked style="accent-color: #f59e0b; cursor: pointer;">
                <span>Merge Collisions</span>
            </label>
        </div>

        <!-- 5. Transport & Trail Actions -->
        <div class="control-group" style="display: flex; gap: 8px; padding-top: 2px;">
            <button type="button" id="pause-btn" class="btn btn-primary" style="flex: 1; font-size: 0.78rem; padding: 7px;">❚❚ Pause</button>
            <button type="button" id="reset-btn" class="btn btn-secondary" style="flex: 1; font-size: 0.78rem; padding: 7px;">⟲ Reset</button>
            <button type="button" id="clear-btn" class="btn btn-secondary" style="flex: 0.8; font-size: 0.78rem; padding: 7px;">Clear</button>
        </div>
    `;

    // Mount Live Manifold State & Conservation Telemetry Bar underneath at the bottom of the main simulation
    // Note: .canvas-panel in physics.css defaults to display:flex (row), which would squeeze #canvas-container
    // horizontally if a sibling is added without flex-direction: column.
    const canvasContainer = document.getElementById('canvas-container') || canvas.parentElement;
    const canvasPanel = canvasContainer ? canvasContainer.parentElement : null;
    if (canvasPanel && canvasPanel.classList.contains('canvas-panel')) {
        canvasPanel.style.flexDirection = 'column';
        canvasPanel.style.alignItems = 'stretch';
        canvasPanel.style.background = 'transparent';
        canvasPanel.style.border = 'none';
        canvasPanel.style.boxShadow = 'none';
        canvasPanel.style.overflow = 'visible';
        canvasContainer.style.background = '#000000';
        canvasContainer.style.borderRadius = '10px';
        canvasContainer.style.overflow = 'hidden';
        canvasContainer.style.border = '1px solid rgba(255, 255, 255, 0.08)';
        canvasContainer.style.boxShadow = '0 12px 40px rgba(0, 0, 0, 0.6)';
    }

    let bottomTelemetry = document.getElementById('nbody-bottom-telemetry');
    if (!bottomTelemetry && canvasContainer) {
        bottomTelemetry = document.createElement('div');
        bottomTelemetry.id = 'nbody-bottom-telemetry';
        bottomTelemetry.className = 'physics-readout';
        bottomTelemetry.style.cssText = 'width: 100%; box-sizing: border-box; margin-top: 14px; background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 10px; padding: 14px 18px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4); backdrop-filter: blur(12px);';
        bottomTelemetry.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.74rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em; font-family: 'Space Grotesk', sans-serif;">
                        🌌 Manifold State
                    </span>
                    <span id="regime-badge" style="background: rgba(100, 255, 218, 0.14); color: #64ffda; border: 1px solid rgba(100, 255, 218, 0.35); border-radius: 6px; padding: 2px 9px; font-size: 0.72rem; font-weight: 700; font-family: 'Space Grotesk', monospace;">
                        FIGURE-8 CHOREOGRAPHY
                    </span>
                </div>
                <span style="font-size: 0.74rem; color: #64748b;">
                    Click &amp; drag on simulation to aim and inject a new body with live orbit preview
                </span>
            </div>
            <div style="display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px;">
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Bodies (N)</div>
                    <strong id="n-val" style="font-size: 0.98rem; color: #f8fafc; font-family: 'Space Grotesk', monospace;">3</strong>
                </div>
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Virial 2T/|V|</div>
                    <strong id="virial-val" style="font-size: 0.98rem; color: #64ffda; font-family: 'Space Grotesk', monospace;">1.00</strong>
                </div>
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Kinetic (T)</div>
                    <strong id="ke-val" style="font-size: 0.98rem; color: #38bdf8; font-family: 'Space Grotesk', monospace;">0</strong>
                </div>
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Potential (V)</div>
                    <strong id="pe-val" style="font-size: 0.98rem; color: #f472b6; font-family: 'Space Grotesk', monospace;">0</strong>
                </div>
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Total E = T+V</div>
                    <strong id="e-val" style="font-size: 0.98rem; color: #34d399; font-family: 'Space Grotesk', monospace;">0</strong>
                </div>
                <div style="background: rgba(2, 6, 23, 0.65); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 8px 10px;">
                    <div style="font-size: 0.66rem; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.04em;">Ang. Mom. |L_z|</div>
                    <strong id="lz-val" style="font-size: 0.98rem; color: #fbbf24; font-family: 'Space Grotesk', monospace;">0</strong>
                </div>
            </div>
        `;
        canvasContainer.insertAdjacentElement('afterend', bottomTelemetry);
    }

    // DOM References
    const gSlider = document.getElementById('g-slider');
    const gVal = document.getElementById('g-val');
    const speedSlider = document.getElementById('speed-slider');
    const speedVal = document.getElementById('speed-val');
    const launchMassSelect = document.getElementById('launch-mass-select');
    const toggleBarycenter = document.getElementById('toggle-barycenter');
    const toggleComLock = document.getElementById('toggle-com-lock');
    const toggleVectors = document.getElementById('toggle-vectors');
    const toggleCollisions = document.getElementById('toggle-collisions');
    const pauseBtn = document.getElementById('pause-btn');
    const resetBtn = document.getElementById('reset-btn');
    const clearBtn = document.getElementById('clear-btn');

    const regimeBadge = document.getElementById('regime-badge');
    const nVal = document.getElementById('n-val');
    const virialVal = document.getElementById('virial-val');
    const keVal = document.getElementById('ke-val');
    const peVal = document.getElementById('pe-val');
    const eVal = document.getElementById('e-val');
    const lzVal = document.getElementById('lz-val');

    // Simulation State
    let G = 1.5;
    let timeScale = 1.0;
    let softeningSq = 16; // epsilon^2 softening parameter
    let isRunning = true;
    let activePreset = 'figure8';
    let bodies = [];
    let mergerFlashes = [];
    let stars = [];

    // Canvas Dimensions & High-DPI Scaling
    let width = 800;
    let height = 540;
    let dpr = 1;

    // Slingshot Drag State
    let isDragging = false;
    let dragStart = null;
    let dragCurrent = null;
    let predictedPath = [];

    function generateStars() {
        stars = [];
        for (let i = 0; i < 110; i++) {
            stars.push({
                x: Math.random() * width,
                y: Math.random() * height,
                r: Math.random() * 1.3 + 0.3,
                alpha: Math.random() * 0.55 + 0.15
            });
        }
    }

    function resize() {
        const rect = canvas.parentElement.getBoundingClientRect();
        width = Math.max(320, rect.width || 800);
        height = 540;
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = `${width}px`;
        canvas.style.height = `${height}px`;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        generateStars();
    }
    window.addEventListener('resize', resize);
    resize();

    // Compute Barycenter (Center of Mass position & velocity)
    function computeBarycenter(bodyList = bodies) {
        let totalMass = 0;
        let rx = 0, ry = 0;
        let vx = 0, vy = 0;
        for (const b of bodyList) {
            totalMass += b.mass;
            rx += b.mass * b.x;
            ry += b.mass * b.y;
            vx += b.mass * b.vx;
            vy += b.mass * b.vy;
        }
        if (totalMass <= 0) {
            return { x: width / 2, y: height / 2, vx: 0, vy: 0, totalMass: 0 };
        }
        return {
            x: rx / totalMass,
            y: ry / totalMass,
            vx: vx / totalMass,
            vy: vy / totalMass,
            totalMass
        };
    }

    // Shift system into zero-momentum barycentric rest frame centered on canvas
    function zeroCenterOfMassDrift(recenterPosition = true) {
        if (bodies.length === 0) return;
        const com = computeBarycenter(bodies);
        const cx = width / 2;
        const cy = height / 2;
        for (const b of bodies) {
            b.vx -= com.vx;
            b.vy -= com.vy;
            if (recenterPosition) {
                const dx = cx - com.x;
                const dy = cy - com.y;
                b.x += dx;
                b.y += dy;
            }
        }
    }

    // Compute Newtonian Plummer-softened accelerations for any list of bodies
    function computeAccelerationsFor(bodyList) {
        for (const b of bodyList) {
            b.ax = 0;
            b.ay = 0;
        }
        const n = bodyList.length;
        for (let i = 0; i < n; i++) {
            const b1 = bodyList[i];
            for (let j = i + 1; j < n; j++) {
                const b2 = bodyList[j];
                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const r2 = dx * dx + dy * dy + softeningSq;
                const invR3 = 1.0 / (r2 * Math.sqrt(r2));
                const s = G * invR3;

                b1.ax += s * b2.mass * dx;
                b1.ay += s * b2.mass * dy;
                b2.ax -= s * b1.mass * dx;
                b2.ay -= s * b1.mass * dy;
            }
        }
    }

    // Circular orbital speed helper at distance r around central mass M under softened gravity
    function circularSpeed(M, r) {
        const r2 = r * r + softeningSq;
        return Math.sqrt((G * M * r * r) / (r2 * Math.sqrt(r2)));
    }

    // =========================================================================
    // 6 CELESTIAL MECHANICS PRESETS
    // =========================================================================
    function applyPreset(presetName) {
        activePreset = presetName;
        mergerFlashes = [];
        const cx = width / 2;
        const cy = height / 2;

        // Highlight active preset button
        document.querySelectorAll('.nbody-preset-btn').forEach(btn => {
            if (btn.getAttribute('data-preset') === presetName) {
                btn.className = 'btn btn-primary nbody-preset-btn';
                btn.style.background = 'linear-gradient(135deg, #0284c7, #6366f1)';
                btn.style.border = 'none';
            } else {
                btn.className = 'btn btn-secondary nbody-preset-btn';
                btn.style.background = '';
                btn.style.border = '';
            }
        });

        if (presetName === 'figure8') {
            // Exact Chenciner-Montgomery (2000) / Moore (1993) 3-Body Figure-8 Choreography
            softeningSq = 1.5;
            const M0 = 1100;
            const L = Math.min(width, height) * 0.31;
            const vScale = Math.sqrt((G * M0) / L);

            const x1 = -0.97000436 * L;
            const y1 = 0.24308753 * L;
            const vx3 = -0.93240737 * vScale;
            const vy3 = -0.86473146 * vScale;
            const vx1 = -0.5 * vx3;
            const vy1 = -0.5 * vy3;

            bodies = [
                { name: 'Alpha', x: cx + x1, y: cy + y1, vx: vx1, vy: vy1, ax: 0, ay: 0, mass: M0, color: '#38bdf8', path: [] },
                { name: 'Beta',  x: cx - x1, y: cy - y1, vx: vx1, vy: vy1, ax: 0, ay: 0, mass: M0, color: '#f472b6', path: [] },
                { name: 'Gamma', x: cx,      y: cy,      vx: vx3, vy: vy3, ax: 0, ay: 0, mass: M0, color: '#64ffda', path: [] }
            ];
            regimeBadge.textContent = 'FIGURE-8 CHOREOGRAPHY';
        } else if (presetName === 'lagrange') {
            // Star + Gas Giant + L4 (+60°) & L5 (-60°) Equilateral Trojan Asteroids
            softeningSq = 12;
            const mStar = 13500;
            const mGiant = 360;
            const R = Math.min(width, height) * 0.34;
            const omega = Math.sqrt((G * (mStar + mGiant)) / Math.pow(R * R + softeningSq, 1.5));

            // Barycentric radii
            const rStar = -R * (mGiant / (mStar + mGiant));
            const rGiant = R * (mStar / (mStar + mGiant));

            // L4 (+60 deg) and L5 (-60 deg) form equilateral triangles with Star and Giant
            const cos60 = 0.5;
            const sin60 = Math.sqrt(3) / 2;
            const l4x = rStar + R * cos60;
            const l4y = R * sin60;
            const l5x = rStar + R * cos60;
            const l5y = -R * sin60;

            bodies = [
                { name: 'Primary Star', x: cx + rStar, y: cy, vx: 0, vy: rStar * omega, ax: 0, ay: 0, mass: mStar, color: '#fbbf24', path: [] },
                { name: 'Jovian Giant', x: cx + rGiant, y: cy, vx: 0, vy: rGiant * omega, ax: 0, ay: 0, mass: mGiant, color: '#f97316', path: [] },
                { name: 'L4 Trojan (Ahead +60°)', x: cx + l4x, y: cy + l4y, vx: -l4y * omega, vy: l4x * omega, ax: 0, ay: 0, mass: 2, color: '#64ffda', path: [] },
                { name: 'L5 Trojan (Behind -60°)', x: cx + l5x, y: cy + l5y, vx: -l5y * omega, vy: l5x * omega, ax: 0, ay: 0, mass: 2, color: '#c084fc', path: [] }
            ];
            regimeBadge.textContent = 'LAGRANGE L4/L5 EQUILATERAL';
        } else if (presetName === 'solarsystem') {
            // Central Star + 4 Keplerian Planets in Barycentric Rest Frame
            softeningSq = 16;
            const mSun = 12000;
            const r1 = 62,  m1 = 12;
            const r2 = 104, m2 = 32;
            const r3 = 154, m3 = 48;
            const r4 = 215, m4 = 120;

            bodies = [
                { name: 'Helios',  x: cx, y: cy,      vx: 0, vy: 0, ax: 0, ay: 0, mass: mSun, color: '#fbbf24', path: [] },
                { name: 'Mercury', x: cx, y: cy - r1, vx: circularSpeed(mSun, r1), vy: 0, ax: 0, ay: 0, mass: m1, color: '#94a3b8', path: [] },
                { name: 'Venus',   x: cx + r2, y: cy, vx: 0, vy: circularSpeed(mSun, r2), ax: 0, ay: 0, mass: m2, color: '#f472b6', path: [] },
                { name: 'Terra',   x: cx, y: cy + r3, vx: -circularSpeed(mSun, r3), vy: 0, ax: 0, ay: 0, mass: m3, color: '#38bdf8', path: [] },
                { name: 'Jove',    x: cx - r4, y: cy, vx: 0, vy: -circularSpeed(mSun, r4), ax: 0, ay: 0, mass: m4, color: '#34d399', path: [] }
            ];
            regimeBadge.textContent = 'KEPLERIAN SOLAR SYSTEM';
        } else if (presetName === 'binary') {
            // Binary Star Pair + 2 Circumbinary ("Tatooine") Planets
            softeningSq = 20;
            const mA = 4500;
            const mB = 4000;
            const mTot = mA + mB;
            const sep = 92;
            const rA = sep * (mB / mTot);
            const rB = sep * (mA / mTot);
            const omegaBin = Math.sqrt((G * mTot) / Math.pow(sep * sep + softeningSq, 1.5));

            const rP1 = 168;
            const rP2 = 228;
            const vP1 = circularSpeed(mTot, rP1);
            const vP2 = circularSpeed(mTot, rP2);

            bodies = [
                { name: 'Primary Star A',   x: cx - rA, y: cy, vx: 0, vy: -rA * omegaBin, ax: 0, ay: 0, mass: mA, color: '#fbbf24', path: [] },
                { name: 'Companion Star B', x: cx + rB, y: cy, vx: 0, vy: rB * omegaBin,  ax: 0, ay: 0, mass: mB, color: '#f97316', path: [] },
                { name: 'Kepler-16b',       x: cx, y: cy - rP1, vx: vP1, vy: 0,           ax: 0, ay: 0, mass: 25, color: '#38bdf8', path: [] },
                { name: 'Outer Planet',     x: cx, y: cy + rP2, vx: -vP2, vy: 0,          ax: 0, ay: 0, mass: 35, color: '#c084fc', path: [] }
            ];
            regimeBadge.textContent = 'CIRCUMBINARY ORBITS';
        } else if (presetName === 'hierarchical') {
            // Hierarchical Star - Planet - Moon (Hill Sphere Epicycle)
            softeningSq = 8;
            const mStar = 13500;
            const mPlanet = 480;
            const mMoon = 2;
            const rOrbit = 175;
            const rMoon = 20; // Inside Hill radius r_H = R * (mPlanet / (3*mStar))^(1/3) ≈ 40px

            const vPlanet = circularSpeed(mStar, rOrbit);
            const vMoonRel = circularSpeed(mPlanet, rMoon);

            bodies = [
                { name: 'Central Star', x: cx, y: cy, vx: 0, vy: 0, ax: 0, ay: 0, mass: mStar, color: '#fbbf24', path: [] },
                { name: 'Giant Planet', x: cx + rOrbit, y: cy, vx: 0, vy: vPlanet, ax: 0, ay: 0, mass: mPlanet, color: '#38bdf8', path: [] },
                { name: 'Lunar Satellite', x: cx + rOrbit + rMoon, y: cy, vx: 0, vy: vPlanet + vMoonRel, ax: 0, ay: 0, mass: mMoon, color: '#64ffda', path: [] }
            ];
            regimeBadge.textContent = 'HILL SPHERE HIERARCHY';
        } else {
            // Chaotic 3-Body Scattering (Zero Net Momentum)
            softeningSq = 24;
            bodies = [
                { name: 'Star 1', x: cx - 115, y: cy - 45, vx: 0.55,  vy: 1.55,  ax: 0, ay: 0, mass: 1350, color: '#f87171', path: [] },
                { name: 'Star 2', x: cx + 115, y: cy - 35, vx: 0.45,  vy: -1.65, ax: 0, ay: 0, mass: 1250, color: '#60a5fa', path: [] },
                { name: 'Star 3', x: cx,       y: cy + 95, vx: -1.10, vy: 0.15,  ax: 0, ay: 0, mass: 1100, color: '#34d399', path: [] }
            ];
            regimeBadge.textContent = 'CHAOTIC 3-BODY SCATTERING';
        }

        zeroCenterOfMassDrift(true);
        computeAccelerationsFor(bodies);
        updateTelemetry();

        // Sync URL preset parameter
        if (window.history && window.history.replaceState) {
            const url = new URL(window.location.href);
            url.searchParams.set('preset', presetName);
            window.history.replaceState({}, '', url);
        }
    }

    // Body radius helper
    function getBodyRadius(mass) {
        if (mass >= 8000) return 15;
        if (mass >= 2000) return 11;
        return Math.max(3.5, Math.min(10, Math.pow(mass, 0.34) * 1.35));
    }

    // Handle inelastic momentum-conserving collisions
    function handleCollisions() {
        if (!toggleCollisions.checked || bodies.length < 2) return;
        const merged = new Set();
        const nextBodies = [];

        for (let i = 0; i < bodies.length; i++) {
            if (merged.has(i)) continue;
            const b1 = bodies[i];

            for (let j = i + 1; j < bodies.length; j++) {
                if (merged.has(j)) continue;
                const b2 = bodies[j];

                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const distSq = dx * dx + dy * dy;
                const minDist = (getBodyRadius(b1.mass) + getBodyRadius(b2.mass)) * 0.82;

                if (distSq < minDist * minDist) {
                    const totalMass = b1.mass + b2.mass;
                    const mergeX = (b1.x * b1.mass + b2.x * b2.mass) / totalMass;
                    const mergeY = (b1.y * b1.mass + b2.y * b2.mass) / totalMass;

                    b1.vx = (b1.vx * b1.mass + b2.vx * b2.mass) / totalMass;
                    b1.vy = (b1.vy * b1.mass + b2.vy * b2.mass) / totalMass;
                    b1.x = mergeX;
                    b1.y = mergeY;
                    if (b2.mass > b1.mass) {
                        b1.color = b2.color;
                        b1.name = b2.name;
                    }
                    b1.mass = totalMass;

                    mergerFlashes.push({ x: mergeX, y: mergeY, r: minDist, alpha: 1.0, color: b1.color });
                    merged.add(j);
                }
            }
            nextBodies.push(b1);
        }
        bodies = nextBodies;
    }

    // Symplectic Velocity Verlet Step
    function integrate(dt) {
        if (bodies.length === 0) return;

        for (const b of bodies) {
            b.x += b.vx * dt + 0.5 * b.ax * dt * dt;
            b.y += b.vy * dt + 0.5 * b.ay * dt * dt;
            b.prev_ax = b.ax;
            b.prev_ay = b.ay;
        }

        computeAccelerationsFor(bodies);

        for (const b of bodies) {
            b.vx += 0.5 * (b.prev_ax + b.ax) * dt;
            b.vy += 0.5 * (b.prev_ay + b.ay) * dt;
        }

        handleCollisions();

        if (toggleComLock.checked && bodies.length > 0) {
            const com = computeBarycenter(bodies);
            const driftX = (width / 2 - com.x) * 0.04;
            const driftY = (height / 2 - com.y) * 0.04;
            for (const b of bodies) {
                b.vx -= com.vx;
                b.vy -= com.vy;
                b.x += driftX;
                b.y += driftY;
            }
        }
    }

    // Forward-integrate predicted trajectory while aiming slingshot
    function computePredictedTrajectory() {
        if (!isDragging || !dragStart || !dragCurrent) {
            predictedPath = [];
            return;
        }

        const launchMass = parseFloat(launchMassSelect.value) || 45;
        const vx = (dragStart.x - dragCurrent.x) * 0.085;
        const vy = (dragStart.y - dragCurrent.y) * 0.085;

        // Clone bodies for fast lookahead integration
        const simBodies = bodies.map(b => ({
            x: b.x, y: b.y, vx: b.vx, vy: b.vy, ax: b.ax, ay: b.ay, mass: b.mass
        }));
        const probeIdx = simBodies.length;
        simBodies.push({
            x: dragStart.x,
            y: dragStart.y,
            vx: vx,
            vy: vy,
            ax: 0,
            ay: 0,
            mass: launchMass
        });

        computeAccelerationsFor(simBodies);
        predictedPath = [{ x: dragStart.x, y: dragStart.y }];

        const stepDt = 0.28;
        for (let step = 0; step < 130; step++) {
            for (const b of simBodies) {
                b.x += b.vx * stepDt + 0.5 * b.ax * stepDt * stepDt;
                b.y += b.vy * stepDt + 0.5 * b.ay * stepDt * stepDt;
                b.prev_ax = b.ax;
                b.prev_ay = b.ay;
            }
            computeAccelerationsFor(simBodies);
            for (const b of simBodies) {
                b.vx += 0.5 * (b.prev_ax + b.ax) * stepDt;
                b.vy += 0.5 * (b.prev_ay + b.ay) * stepDt;
            }
            const probe = simBodies[probeIdx];
            predictedPath.push({ x: probe.x, y: probe.y });
        }
    }

    // Calculate Energies, Angular Momentum L_z, and Virial Ratio 2T/|V|
    function updateTelemetry() {
        let ke = 0;
        let pe = 0;
        let lz = 0;
        const com = computeBarycenter(bodies);

        for (let i = 0; i < bodies.length; i++) {
            const b1 = bodies[i];
            const v2 = b1.vx * b1.vx + b1.vy * b1.vy;
            ke += 0.5 * b1.mass * v2;

            const rx = b1.x - com.x;
            const ry = b1.y - com.y;
            const pvx = b1.vx - com.vx;
            const pvy = b1.vy - com.vy;
            lz += b1.mass * (rx * pvy - ry * pvx);

            for (let j = i + 1; j < bodies.length; j++) {
                const b2 = bodies[j];
                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const dist = Math.sqrt(dx * dx + dy * dy + softeningSq);
                pe -= (G * b1.mass * b2.mass) / dist;
            }
        }

        const totalE = ke + pe;
        const virial = Math.abs(pe) > 1e-3 ? (2 * ke) / Math.abs(pe) : 0;

        nVal.textContent = String(bodies.length);
        virialVal.textContent = virial.toFixed(2);
        keVal.textContent = Math.round(ke).toLocaleString();
        peVal.textContent = Math.round(pe).toLocaleString();
        eVal.textContent = Math.round(totalE).toLocaleString();
        lzVal.textContent = Math.round(Math.abs(lz)).toLocaleString();
    }

    // =========================================================================
    // UI & MOUSE INTERACTION BINDINGS
    // =========================================================================
    document.querySelectorAll('.nbody-preset-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const preset = btn.getAttribute('data-preset');
            if (preset) applyPreset(preset);
        });
    });

    gSlider.addEventListener('input', () => {
        G = parseFloat(gSlider.value);
        gVal.textContent = G.toFixed(2);
        computeAccelerationsFor(bodies);
    });

    speedSlider.addEventListener('input', () => {
        timeScale = parseFloat(speedSlider.value);
        speedVal.textContent = `${timeScale.toFixed(1)}×`;
    });

    pauseBtn.addEventListener('click', () => {
        isRunning = !isRunning;
        pauseBtn.textContent = isRunning ? '❚❚ Pause' : '▶ Resume';
    });

    resetBtn.addEventListener('click', () => {
        applyPreset(activePreset);
    });

    clearBtn.addEventListener('click', () => {
        bodies = [];
        predictedPath = [];
        regimeBadge.textContent = 'CUSTOM SANDBOX';
        updateTelemetry();
    });

    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        dragStart = pos;
        dragCurrent = pos;
        isDragging = true;
        computePredictedTrajectory();
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            dragCurrent = getMousePos(e);
            computePredictedTrajectory();
        }
    });

    window.addEventListener('mouseup', () => {
        if (isDragging && dragStart && dragCurrent) {
            const dx = dragStart.x - dragCurrent.x;
            const dy = dragStart.y - dragCurrent.y;
            const launchMass = parseFloat(launchMassSelect.value) || 45;
            const colorMap = {
                5: '#64ffda',
                45: '#38bdf8',
                320: '#f97316',
                2200: '#fbbf24'
            };

            bodies.push({
                name: 'Injected Body',
                x: dragStart.x,
                y: dragStart.y,
                vx: dx * 0.085,
                vy: dy * 0.085,
                ax: 0,
                ay: 0,
                mass: launchMass,
                color: colorMap[launchMass] || '#e2e8f0',
                path: []
            });

            if (toggleComLock.checked) {
                zeroCenterOfMassDrift(false);
            }
            computeAccelerationsFor(bodies);
            updateTelemetry();
        }
        isDragging = false;
        dragStart = null;
        dragCurrent = null;
        predictedPath = [];
    });

    // =========================================================================
    // RENDERING PIPELINE
    // =========================================================================
    function drawArrow(x1, y1, x2, y2, color, lineWidth = 1.5) {
        const dx = x2 - x1;
        const dy = y2 - y1;
        const len = Math.hypot(dx, dy);
        if (len < 4) return;

        ctx.save();
        ctx.strokeStyle = color;
        ctx.fillStyle = color;
        ctx.lineWidth = lineWidth;
        ctx.beginPath();
        ctx.moveTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        const ux = dx / len;
        const uy = dy / len;
        ctx.beginPath();
        ctx.moveTo(x2, y2);
        ctx.lineTo(x2 - ux * 6 + uy * 3.2, y2 - uy * 6 - ux * 3.2);
        ctx.lineTo(x2 - ux * 6 - uy * 3.2, y2 - uy * 6 + ux * 3.2);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
    }

    function draw() {
        // 1. Deep Space Radial Gradient Background
        const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, width * 0.7);
        bgGrad.addColorStop(0, '#0f172a');
        bgGrad.addColorStop(0.6, '#070b19');
        bgGrad.addColorStop(1, '#020617');
        ctx.fillStyle = bgGrad;
        ctx.fillRect(0, 0, width, height);

        // 2. Background Starfield
        for (const s of stars) {
            ctx.fillStyle = `rgba(226, 232, 240, ${s.alpha})`;
            ctx.beginPath();
            ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
            ctx.fill();
        }

        // 3. Barycenter Reference Rings & Crosshair
        const com = computeBarycenter(bodies);
        if (toggleBarycenter.checked && bodies.length > 0) {
            ctx.save();
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.06)';
            ctx.lineWidth = 1;
            [75, 150, 225].forEach(rad => {
                ctx.beginPath();
                ctx.arc(com.x, com.y, rad, 0, Math.PI * 2);
                ctx.stroke();
            });

            // Barycenter Crosshair (⊕)
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.55)';
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.arc(com.x, com.y, 5, 0, Math.PI * 2);
            ctx.moveTo(com.x - 9, com.y);
            ctx.lineTo(com.x + 9, com.y);
            ctx.moveTo(com.x, com.y - 9);
            ctx.lineTo(com.x, com.y + 9);
            ctx.stroke();

            ctx.fillStyle = 'rgba(100, 255, 218, 0.7)';
            ctx.font = '600 10px "Space Grotesk", monospace';
            ctx.fillText('R_CM', com.x + 8, com.y - 7);
            ctx.restore();
        }

        // 4. Draw Lagrange Equilateral Triangle Overlay when in 'lagrange' preset
        if (activePreset === 'lagrange' && bodies.length >= 4) {
            ctx.save();
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.22)';
            ctx.lineWidth = 1.2;
            ctx.beginPath();
            ctx.moveTo(bodies[0].x, bodies[0].y);
            ctx.lineTo(bodies[1].x, bodies[1].y);
            ctx.lineTo(bodies[2].x, bodies[2].y);
            ctx.closePath();
            ctx.moveTo(bodies[0].x, bodies[0].y);
            ctx.lineTo(bodies[1].x, bodies[1].y);
            ctx.lineTo(bodies[3].x, bodies[3].y);
            ctx.closePath();
            ctx.stroke();
            ctx.restore();
        }

        // 5. Draw Orbital Trajectory Ribbons
        for (const b of bodies) {
            if (isRunning) {
                b.path.push({ x: b.x, y: b.y });
                const maxTrail = activePreset === 'figure8' ? 360 : 260;
                if (b.path.length > maxTrail) b.path.shift();
            }

            if (b.path.length > 2) {
                ctx.save();
                ctx.lineCap = 'round';
                for (let i = 1; i < b.path.length; i++) {
                    const frac = i / b.path.length;
                    ctx.strokeStyle = b.color;
                    ctx.globalAlpha = frac * 0.65;
                    ctx.lineWidth = 1.0 + frac * 1.6;
                    ctx.beginPath();
                    ctx.moveTo(b.path[i - 1].x, b.path[i - 1].y);
                    ctx.lineTo(b.path[i].x, b.path[i].y);
                    ctx.stroke();
                }
                ctx.restore();
            }
        }

        // 6. Draw Collision Merger Flashes
        for (let i = mergerFlashes.length - 1; i >= 0; i--) {
            const fl = mergerFlashes[i];
            ctx.save();
            ctx.strokeStyle = fl.color;
            ctx.globalAlpha = fl.alpha;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(fl.x, fl.y, fl.r, 0, Math.PI * 2);
            ctx.stroke();
            ctx.restore();
            fl.r += 1.4;
            fl.alpha -= 0.04;
            if (fl.alpha <= 0) mergerFlashes.splice(i, 1);
        }

        // 7. Draw Celestial Bodies & Optional Vectors
        for (const b of bodies) {
            const radius = getBodyRadius(b.mass);

            // Outer Corona / Atmosphere Glow
            ctx.save();
            const glowGrad = ctx.createRadialGradient(b.x, b.y, radius * 0.3, b.x, b.y, radius * 2.8);
            glowGrad.addColorStop(0, b.color);
            glowGrad.addColorStop(1, 'rgba(0, 0, 0, 0)');
            ctx.fillStyle = glowGrad;
            ctx.globalAlpha = b.mass >= 2000 ? 0.55 : 0.32;
            ctx.beginPath();
            ctx.arc(b.x, b.y, radius * 2.8, 0, Math.PI * 2);
            ctx.fill();

            // Solid Core
            ctx.globalAlpha = 1.0;
            ctx.fillStyle = b.color;
            ctx.beginPath();
            ctx.arc(b.x, b.y, radius, 0, Math.PI * 2);
            ctx.fill();

            // Specular highlight on core
            ctx.fillStyle = 'rgba(255, 255, 255, 0.45)';
            ctx.beginPath();
            ctx.arc(b.x - radius * 0.28, b.y - radius * 0.28, Math.max(1.2, radius * 0.32), 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();

            // Velocity (cyan) and Gravitational Acceleration (amber) vectors
            if (toggleVectors.checked) {
                drawArrow(b.x, b.y, b.x + b.vx * 8, b.y + b.vy * 8, '#38bdf8', 1.5);
                drawArrow(b.x, b.y, b.x + b.ax * 45, b.y + b.ay * 45, '#f59e0b', 1.3);
            }
        }

        // 8. Draw Slingshot Launcher & Real-Time Forward-Integrated Trajectory Preview
        if (isDragging && dragStart && dragCurrent) {
            computePredictedTrajectory();

            // Predicted curved orbit path
            if (predictedPath.length > 1) {
                ctx.save();
                ctx.setLineDash([5, 5]);
                ctx.strokeStyle = 'rgba(100, 255, 218, 0.8)';
                ctx.lineWidth = 1.8;
                ctx.beginPath();
                ctx.moveTo(predictedPath[0].x, predictedPath[0].y);
                for (let i = 1; i < predictedPath.length; i++) {
                    ctx.lineTo(predictedPath[i].x, predictedPath[i].y);
                }
                ctx.stroke();
                ctx.restore();
            }

            // Pullback line & velocity launch arrow
            const vx = (dragStart.x - dragCurrent.x) * 0.085;
            const vy = (dragStart.y - dragCurrent.y) * 0.085;
            drawArrow(dragStart.x, dragStart.y, dragStart.x + vx * 10, dragStart.y + vy * 10, '#f59e0b', 2.2);

            ctx.save();
            ctx.fillStyle = '#64ffda';
            ctx.beginPath();
            ctx.arc(dragStart.x, dragStart.y, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#f8fafc';
            ctx.font = '600 11px "Space Grotesk", monospace';
            const speedMag = Math.hypot(vx, vy).toFixed(1);
            ctx.fillText(`v₀ = ${speedMag}`, dragStart.x + 10, dragStart.y - 10);
            ctx.restore();
        }
    }

    // Hydrate initial preset from URL query parameter (?preset=...)
    const urlParams = new URLSearchParams(window.location.search);
    const initialPreset = urlParams.get('preset') || 'figure8';
    applyPreset(initialPreset);

    // Main Symplectic Animation Loop
    let lastTimestamp = performance.now();
    function loop(timestamp) {
        const elapsed = Math.min(0.035, (timestamp - lastTimestamp) / 1000);
        lastTimestamp = timestamp;

        if (isRunning) {
            const totalDt = elapsed * 24 * timeScale;
            const substeps = 8;
            const subDt = totalDt / substeps;
            for (let s = 0; s < substeps; s++) {
                integrate(subDt);
            }
            updateTelemetry();
        }

        draw();
        requestAnimationFrame(loop);
    }

    requestAnimationFrame(loop);
});
