/**
 * 🌌 PHYSICS LAB: Damped-Driven Chaotic Pendulum & Poincaré Bifurcations
 * Equation: d²θ/dt² + γ dθ/dt + ω₀² sin(θ) = F₀ cos(ω_d t)
 * 
 * Integrates via Runge-Kutta 4th-order (RK4) with real-time phase space (θ, dθ/dt)
 * and stroboscopic Poincaré recurrence sections displaying Feigenbaum period-doubling
 * cascades into deterministic chaos.
 */

document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject Modern Glassmorphic Controls
    controls.innerHTML = `
        <!-- Presets Row -->
        <div class="control-group">
            <label style="font-weight: 600; color: #fff; margin-bottom: 8px; display: block;">Dynamical Regime Presets:</label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button id="preset-undriven" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Harmonic (F₀=0)</button>
                <button id="preset-period1" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Limit Cycle (F₀=0.5)</button>
                <button id="preset-period2" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Period-2 (F₀=1.07)</button>
                <button id="preset-chaos" class="btn btn-primary" style="font-size: 0.78rem; padding: 6px; background: linear-gradient(135deg, #0284c7, #7c3aed); border: none;">Chaos (F₀=1.20)</button>
            </div>
        </div>

        <!-- Sliders -->
        <div class="control-group" style="margin-top: 14px;">
            <div style="display: flex; justify-content: space-between;">
                <label>Drive Amplitude (F₀):</label>
                <span id="f-val" class="math-value" style="color: #38bdf8; font-weight: 700;">1.20</span>
            </div>
            <input type="range" id="f-slider" min="0.00" max="1.55" step="0.01" value="1.20" style="width: 100%;">
        </div>

        <div class="control-group" style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between;">
                <label>Damping Ratio (γ):</label>
                <span id="d-val" class="math-value" style="color: #34d399; font-weight: 700;">0.50</span>
            </div>
            <input type="range" id="d-slider" min="0.10" max="0.80" step="0.02" value="0.50" style="width: 100%;">
        </div>

        <div class="control-group" style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between;">
                <label>Drive Frequency (ω_d):</label>
                <span id="wd-val" class="math-value" style="color: #fbbf24; font-weight: 700;">0.67</span>
            </div>
            <input type="range" id="wd-slider" min="0.20" max="1.40" step="0.01" value="0.67" style="width: 100%;">
        </div>

        <!-- Action Buttons -->
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 8px;">
            <button id="toggle-sim-btn" class="btn btn-secondary" style="flex: 1;">❚❚ Pause</button>
            <button id="clear-poincare-btn" class="btn btn-secondary" style="flex: 1;">Clear Poincaré</button>
            <button id="reset-sim-btn" class="btn btn-secondary">↺ Reset</button>
        </div>

        <!-- Live Telemetry Readout -->
        <div class="physics-readout" style="margin-top: 16px; font-size: 0.84rem; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; font-weight: 600;">Active Regime</span>
                <span id="regime-badge" style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700;">
                    DETERMINISTIC CHAOS
                </span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.8rem;">
                <div>Angle θ: <strong id="theta-readout" style="color: #38bdf8;">0.00 rad</strong></div>
                <div>Velocity ω: <strong id="omega-readout" style="color: #34d399;">0.00 rad/s</strong></div>
                <div>Drive Phase ϕ: <strong id="phase-readout" style="color: #fbbf24;">0.00 rad</strong></div>
                <div>Poincaré Dots: <strong id="dots-count" style="color: #ffd700;">0</strong></div>
            </div>
        </div>
    `;

    // References
    const fSlider = document.getElementById('f-slider');
    const dSlider = document.getElementById('d-slider');
    const wdSlider = document.getElementById('wd-slider');
    const toggleBtn = document.getElementById('toggle-sim-btn');
    const clearPoincareBtn = document.getElementById('clear-poincare-btn');
    const resetBtn = document.getElementById('reset-sim-btn');

    const fVal = document.getElementById('f-val');
    const dVal = document.getElementById('d-val');
    const wdVal = document.getElementById('wd-val');
    const regimeBadge = document.getElementById('regime-badge');
    const thetaReadout = document.getElementById('theta-readout');
    const omegaReadout = document.getElementById('omega-readout');
    const phaseReadout = document.getElementById('phase-readout');
    const dotsCount = document.getElementById('dots-count');

    // Physical Parameters
    let F0 = 1.20;       // Driving force amplitude
    let gamma = 0.50;    // Damping coefficient
    let omega_d = 0.667; // Driving frequency (approx 2/3)
    let omega0_sq = 1.0; // Natural frequency squared (g/L = 1)

    // State Variables
    let theta = 0.2;     // Angle in radians
    let omega = 0.0;     // Angular velocity
    let time = 0.0;      // Simulation time
    let isRunning = true;
    let isDragging = false;

    // Phase Space & Poincaré Trajectory Buffers
    let phaseTrail = [];
    const maxPhaseTrail = 400;
    let poincarePoints = [];
    const maxPoincare = 800;
    let lastStrobePhase = 0;

    // Viewport Geometry
    let width = 800;
    let height = 500;
    let dpr = window.devicePixelRatio || 1;

    function resize() {
        const rect = canvas.parentElement.getBoundingClientRect();
        width = rect.width || 800;
        height = 520;
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resize);
    resize();

    function updateRegimeBadge() {
        if (F0 < 0.1) {
            regimeBadge.textContent = 'DAMPED HARMONIC';
            regimeBadge.style.color = '#34d399';
            regimeBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
            regimeBadge.style.background = 'rgba(52, 211, 153, 0.15)';
        } else if (F0 < 0.95) {
            regimeBadge.textContent = 'PERIOD-1 LIMIT CYCLE';
            regimeBadge.style.color = '#38bdf8';
            regimeBadge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
            regimeBadge.style.background = 'rgba(56, 189, 248, 0.15)';
        } else if (F0 < 1.15) {
            regimeBadge.textContent = 'PERIOD-2 BIFURCATION';
            regimeBadge.style.color = '#fbbf24';
            regimeBadge.style.borderColor = 'rgba(251, 191, 36, 0.4)';
            regimeBadge.style.background = 'rgba(251, 191, 36, 0.15)';
        } else {
            regimeBadge.textContent = 'DETERMINISTIC CHAOS';
            regimeBadge.style.color = '#f87171';
            regimeBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
            regimeBadge.style.background = 'rgba(239, 68, 68, 0.15)';
        }
    }

    // Sliders
    fSlider.oninput = () => { F0 = parseFloat(fSlider.value); fVal.textContent = F0.toFixed(2); updateRegimeBadge(); };
    dSlider.oninput = () => { gamma = parseFloat(dSlider.value); dVal.textContent = gamma.toFixed(2); };
    wdSlider.oninput = () => { omega_d = parseFloat(wdSlider.value); wdVal.textContent = omega_d.toFixed(2); };

    // Presets
    document.getElementById('preset-undriven').onclick = () => {
        F0 = 0.0; fSlider.value = F0; fVal.textContent = F0.toFixed(2); updateRegimeBadge();
    };
    document.getElementById('preset-period1').onclick = () => {
        F0 = 0.50; fSlider.value = F0; fVal.textContent = F0.toFixed(2); updateRegimeBadge();
    };
    document.getElementById('preset-period2').onclick = () => {
        F0 = 1.07; fSlider.value = F0; fVal.textContent = F0.toFixed(2); updateRegimeBadge();
    };
    document.getElementById('preset-chaos').onclick = () => {
        F0 = 1.20; fSlider.value = F0; fVal.textContent = F0.toFixed(2); updateRegimeBadge();
    };

    toggleBtn.onclick = () => {
        isRunning = !isRunning;
        toggleBtn.textContent = isRunning ? '❚❚ Pause' : '▶ Resume';
    };
    clearPoincareBtn.onclick = () => { poincarePoints = []; dotsCount.textContent = '0'; };
    resetBtn.onclick = () => {
        theta = 0.2; omega = 0.0; time = 0.0;
        phaseTrail = []; poincarePoints = [];
        dotsCount.textContent = '0';
    };

    // RK4 Equations of Motion:
    // dθ/dt = ω
    // dω/dt = -γ ω - ω₀² sin(θ) + F₀ cos(ω_d t)
    function rk4Step(dt) {
        const f = (t, th, w) => {
            return [
                w,
                -gamma * w - omega0_sq * Math.sin(th) + F0 * Math.cos(omega_d * t)
            ];
        };

        const k1 = f(time, theta, omega);
        const k2 = f(time + 0.5 * dt, theta + 0.5 * dt * k1[0], omega + 0.5 * dt * k1[1]);
        const k3 = f(time + 0.5 * dt, theta + 0.5 * dt * k2[0], omega + 0.5 * dt * k2[1]);
        const k4 = f(time + dt, theta + dt * k3[0], omega + dt * k3[1]);

        theta += (dt / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]);
        omega += (dt / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
        time += dt;

        // Wrap angle to [-π, π] for phase plane analysis
        while (theta > Math.PI) theta -= 2 * Math.PI;
        while (theta < -Math.PI) theta += 2 * Math.PI;

        // Record Poincaré Stroboscopic Point when drive phase cycles through 2π
        const currentPhase = (omega_d * time) % (2 * Math.PI);
        if (currentPhase < lastStrobePhase) {
            // Drive cycle just rolled over
            poincarePoints.push({ th: theta, w: omega });
            if (poincarePoints.length > maxPoincare) poincarePoints.shift();
            dotsCount.textContent = poincarePoints.length;
        }
        lastStrobePhase = currentPhase;

        phaseTrail.push({ th: theta, w: omega });
        if (phaseTrail.length > maxPhaseTrail) phaseTrail.shift();
    }

    // Interactive Dragging
    canvas.addEventListener('mousedown', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;

        // Left viewport: Pendulum pivot at (width * 0.24, 160)
        const pivX = width * 0.24;
        const pivY = 160;
        const bobX = pivX + 130 * Math.sin(theta);
        const bobY = pivY + 130 * Math.cos(theta);

        const dist = Math.sqrt((mx - bobX)**2 + (my - bobY)**2);
        if (dist < 32) {
            isDragging = true;
            omega = 0;
        }
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const rect = canvas.getBoundingClientRect();
        const mx = e.clientX - rect.left;
        const my = e.clientY - rect.top;
        const pivX = width * 0.24;
        const pivY = 160;
        theta = Math.atan2(mx - pivX, my - pivY);
        omega = 0;
    });

    window.addEventListener('mouseup', () => { isDragging = false; });

    // Main 60fps Loop
    let lastTime = performance.now();

    function loop(now) {
        requestAnimationFrame(loop);
        const elapsed = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        if (isRunning && !isDragging) {
            // Substep RK4 for numerical stability
            const substeps = 10;
            const subDt = elapsed / substeps;
            for (let i = 0; i < substeps; i++) {
                rk4Step(subDt);
            }
        }

        // Telemetry Update
        thetaReadout.textContent = `${theta.toFixed(2)} rad`;
        omegaReadout.textContent = `${omega.toFixed(2)} rad/s`;
        const drivePhase = (omega_d * time) % (2 * Math.PI);
        phaseReadout.textContent = `${drivePhase.toFixed(2)} rad`;

        // Render Canvas
        ctx.clearRect(0, 0, width, height);

        // -------------------------------------------------------------
        // VIEWPORT 1: REAL-SPACE SWINGING PENDULUM (LEFT 48%)
        // -------------------------------------------------------------
        const v1Width = width * 0.48;
        const pivX = v1Width * 0.5;
        const pivY = 140;
        const rodLen = 135;

        // Viewport 1 Panel Background
        ctx.fillStyle = 'rgba(15, 23, 42, 0.4)';
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.06)';
        ctx.lineWidth = 1;
        ctx.fillRect(10, 10, v1Width - 20, height - 20);
        ctx.strokeRect(10, 10, v1Width - 20, height - 20);

        // Title
        ctx.fillStyle = '#94a3b8';
        ctx.font = '600 12px Inter, sans-serif';
        ctx.fillText('PHYSICAL SYSTEM & DRIVING TORQUE', 24, 34);

        // Drive Force Vector Visualization (External torque arrow)
        const driveForce = F0 * Math.cos(omega_d * time);
        const arrowLen = driveForce * 40;
        ctx.strokeStyle = '#fbbf24';
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(pivX, pivY - 35);
        ctx.lineTo(pivX + arrowLen, pivY - 35);
        ctx.stroke();

        ctx.fillStyle = '#fbbf24';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText(`Drive F(t): ${driveForce.toFixed(2)}`, pivX + arrowLen + (arrowLen >= 0 ? 8 : -70), pivY - 32);

        // Pivot base
        ctx.fillStyle = '#475569';
        ctx.fillRect(pivX - 25, pivY - 12, 50, 8);

        // Pendulum Rod
        const bobX = pivX + rodLen * Math.sin(theta);
        const bobY = pivY + rodLen * Math.cos(theta);

        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(pivX, pivY);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();

        // Pendulum Bob (Cyan Glow)
        ctx.save();
        ctx.shadowColor = '#38bdf8';
        ctx.shadowBlur = 16;
        ctx.fillStyle = isDragging ? '#34d399' : '#0284c7';
        ctx.beginPath();
        ctx.arc(bobX, bobY, 14, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();

        // Pivot center dot
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(pivX, pivY, 4, 0, Math.PI * 2);
        ctx.fill();

        // -------------------------------------------------------------
        // VIEWPORT 2: PHASE SPACE & POINCARÉ RECURRENCE SECTION (RIGHT 50%)
        // -------------------------------------------------------------
        const v2Left = width * 0.49;
        const v2Width = width * 0.50;
        const psCenterX = v2Left + v2Width * 0.5;
        const psCenterY = height * 0.52;
        const psScaleX = (v2Width - 50) / (2 * Math.PI); // Maps [-π, π] across width
        const psScaleY = 55;                            // Maps ω (approx [-3, 3])

        // Panel Background
        ctx.fillStyle = 'rgba(2, 6, 23, 0.7)';
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
        ctx.lineWidth = 1;
        ctx.fillRect(v2Left, 10, v2Width - 10, height - 20);
        ctx.strokeRect(v2Left, 10, v2Width - 10, height - 20);

        // Title
        ctx.fillStyle = '#38bdf8';
        ctx.font = '600 12px Inter, sans-serif';
        ctx.fillText('PHASE SPACE (θ, dθ/dt) & POINCARÉ RECURRENCE SECTION', v2Left + 18, 34);

        // Coordinate Axes (θ = 0, ω = 0)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1;
        // Horizontal axis (θ)
        ctx.beginPath();
        ctx.moveTo(v2Left + 15, psCenterY);
        ctx.lineTo(v2Left + v2Width - 25, psCenterY);
        ctx.stroke();
        // Vertical axis (ω)
        ctx.beginPath();
        ctx.moveTo(psCenterX, 45);
        ctx.lineTo(psCenterX, height - 25);
        ctx.stroke();

        ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
        ctx.font = '10px Inter, sans-serif';
        ctx.fillText('-π', v2Left + 20, psCenterY - 6);
        ctx.fillText('+π', v2Left + v2Width - 40, psCenterY - 6);
        ctx.fillText('+ω', psCenterX + 6, 58);
        ctx.fillText('-ω', psCenterX + 6, height - 32);

        // Draw Continuous Phase Space Orbit Trail
        if (phaseTrail.length > 2) {
            ctx.beginPath();
            let first = true;
            for (let i = 0; i < phaseTrail.length; i++) {
                const px = psCenterX + phaseTrail[i].th * psScaleX;
                const py = psCenterY - phaseTrail[i].w * psScaleY;

                // Handle toroidal boundary wrapping jump
                if (i > 0 && Math.abs(phaseTrail[i].th - phaseTrail[i-1].th) > 3.0) {
                    first = true;
                }

                if (first) {
                    ctx.moveTo(px, py);
                    first = false;
                } else {
                    ctx.lineTo(px, py);
                }
            }
            ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
            ctx.lineWidth = 1.2;
            ctx.stroke();
        }

        // Draw Poincaré Recurrence Strobe Points (Gold dots)
        ctx.save();
        ctx.fillStyle = '#ffd700';
        ctx.shadowColor = '#ffd700';
        ctx.shadowBlur = 6;
        poincarePoints.forEach(pt => {
            const px = psCenterX + pt.th * psScaleX;
            const py = psCenterY - pt.w * psScaleY;
            ctx.beginPath();
            ctx.arc(px, py, 2.2, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.restore();

        // Current State Point in Phase Space
        const curPx = psCenterX + theta * psScaleX;
        const curPy = psCenterY - omega * psScaleY;
        ctx.save();
        ctx.fillStyle = '#34d399';
        ctx.shadowColor = '#34d399';
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(curPx, curPy, 5.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    requestAnimationFrame(loop);
});
