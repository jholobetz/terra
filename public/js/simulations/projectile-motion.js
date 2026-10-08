/**
 * 🌌 PHYSICS LAB: Newton's Orbital Cannon & Escape Trajectories
 * 
 * Simulates Sir Isaac Newton's landmark 1728 thought experiment on a spherical
 * gravitating planet. Demonstrates the continuous physical transition from
 * ballistic sub-orbital parabolic arcs to circular orbital insertion (v_circ = 7.91 km/s),
 * bound Keplerian ellipses, and hyperbolic cosmic escape (v_esc = 11.19 km/s).
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
            <label style="font-weight: 600; color: #fff; margin-bottom: 8px; display: block;">Orbital Regime Presets:</label>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                <button id="preset-ballistic" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Sub-Orbital (4.5 km/s)</button>
                <button id="preset-circular" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Circular (7.91 km/s)</button>
                <button id="preset-elliptic" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px;">Elliptic (9.6 km/s)</button>
                <button id="preset-escape" class="btn btn-primary" style="font-size: 0.78rem; padding: 6px; background: linear-gradient(135deg, #0284c7, #c084fc); border: none;">Escape (11.5 km/s)</button>
            </div>
        </div>

        <!-- Muzzle Velocity Slider -->
        <div class="control-group" style="margin-top: 14px;">
            <div style="display: flex; justify-content: space-between;">
                <label>Horizontal Muzzle Speed (v₀):</label>
                <span id="v-val" class="math-value" style="color: #38bdf8; font-weight: 700;">7.91 km/s</span>
            </div>
            <input type="range" id="v-slider" min="1.0" max="14.0" step="0.05" value="7.91" style="width: 100%;">
        </div>

        <!-- Cannon Altitude Slider -->
        <div class="control-group" style="margin-top: 12px;">
            <div style="display: flex; justify-content: space-between;">
                <label>Mountain Altitude (h):</label>
                <span id="h-val" class="math-value" style="color: #34d399; font-weight: 700;">120 km</span>
            </div>
            <input type="range" id="h-slider" min="20" max="400" step="10" value="120" style="width: 100%;">
        </div>

        <!-- Atmosphere Toggle -->
        <div class="control-group" style="margin-top: 12px; display: flex; align-items: center; justify-content: space-between;">
            <label for="atmos-toggle" style="margin-bottom: 0; cursor: pointer;">Atmospheric Friction (Drag):</label>
            <input type="checkbox" id="atmos-toggle" style="width: 18px; height: 18px; accent-color: #38bdf8; cursor: pointer;">
        </div>

        <!-- Action Buttons -->
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 8px;">
            <button id="fire-btn" class="btn btn-primary" style="flex: 1.2; background: linear-gradient(135deg, #0284c7, #2563eb); border: none;">💥 Fire Cannon!</button>
            <button id="clear-btn" class="btn btn-secondary" style="flex: 1;">Clear Trails</button>
            <button id="pause-btn" class="btn btn-secondary">❚❚</button>
        </div>

        <!-- Live Telemetry Readout -->
        <div class="physics-readout" style="margin-top: 16px; font-size: 0.84rem; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 10px; padding: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: var(--text-muted); font-size: 0.72rem; text-transform: uppercase; font-weight: 600;">Trajectory Class</span>
                <span id="regime-badge" style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 700;">
                    CIRCULAR ORBIT (e ≈ 0)
                </span>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.8rem;">
                <div>Eccentricity e: <strong id="e-readout" style="color: #38bdf8;">0.00</strong></div>
                <div>Orbital Energy: <strong id="energy-readout" style="color: #34d399;">-31.3 MJ/kg</strong></div>
                <div>Apogee Altitude: <strong id="apogee-readout" style="color: #fbbf24;">120 km</strong></div>
                <div>Perigee Altitude: <strong id="perigee-readout" style="color: #c084fc;">120 km</strong></div>
            </div>
        </div>
    `;

    // References
    const vSlider = document.getElementById('v-slider');
    const hSlider = document.getElementById('h-slider');
    const atmosToggle = document.getElementById('atmos-toggle');
    const fireBtn = document.getElementById('fire-btn');
    const clearBtn = document.getElementById('clear-btn');
    const pauseBtn = document.getElementById('pause-btn');

    const vVal = document.getElementById('v-val');
    const hVal = document.getElementById('h-val');
    const regimeBadge = document.getElementById('regime-badge');
    const eReadout = document.getElementById('e-readout');
    const energyReadout = document.getElementById('energy-readout');
    const apogeeReadout = document.getElementById('apogee-readout');
    const perigeeReadout = document.getElementById('perigee-readout');

    // Physical Constants & Scaling
    // Real Earth: R_earth = 6371 km, GM = 3.986e5 km³/s²
    // v_circ at surface = sqrt(GM / R) = 7.91 km/s
    // v_esc at surface = sqrt(2 * GM / R) = 11.19 km/s
    const R_EARTH_KM = 6371;
    const GM = 3.986004418e5; // km³/s²

    // State Variables
    let v0_kms = 7.91;
    let altitude_km = 120;
    let hasAtmosphere = false;
    let isRunning = true;

    // Canvas & Trajectory
    let projectiles = [];
    let persistentTrails = [];
    const maxPathPoints = 1200;

    let width = 800;
    let height = 520;
    let dpr = window.devicePixelRatio || 1;

    // Viewport scale: pixels per km
    // Earth radius in pixels: ~140px
    let pxPerKm = 140 / R_EARTH_KM;
    let center = { x: 400, y: 260 };

    function resize() {
        const rect = canvas.parentElement.getBoundingClientRect();
        width = rect.width || 800;
        height = 540;
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
        center = { x: width * 0.5, y: height * 0.52 };
        pxPerKm = 135 / R_EARTH_KM;
    }
    window.addEventListener('resize', resize);
    resize();

    function updateTelemetry() {
        const r0 = R_EARTH_KM + altitude_km;
        // Specific orbital energy: ε = v²/2 - GM/r
        const specificEnergy = (v0_kms * v0_kms) * 0.5 - GM / r0; // in km²/s² (MJ/kg)
        // Specific angular momentum: h = r * v
        const h_ang = r0 * v0_kms;
        // Eccentricity: e = sqrt(1 + 2 * ε * h² / GM²)
        let ecc = Math.sqrt(Math.max(0, 1 + (2 * specificEnergy * h_ang * h_ang) / (GM * GM)));

        // Semi-major axis: a = -GM / (2 * ε)
        let a = specificEnergy < 0 ? -GM / (2 * specificEnergy) : Infinity;
        let r_peri = a * (1 - ecc);
        let r_apo = specificEnergy < 0 ? a * (1 + ecc) : Infinity;

        let peri_alt = r_peri - R_EARTH_KM;
        let apo_alt = specificEnergy < 0 ? (r_apo - R_EARTH_KM) : Infinity;

        // Badge & Color
        if (peri_alt < 0) {
            regimeBadge.textContent = 'SUB-ORBITAL IMPACT';
            regimeBadge.style.color = '#f87171';
            regimeBadge.style.borderColor = 'rgba(239, 68, 68, 0.4)';
            regimeBadge.style.background = 'rgba(239, 68, 68, 0.15)';
        } else if (ecc < 0.03) {
            regimeBadge.textContent = 'CIRCULAR ORBIT (e ≈ 0)';
            regimeBadge.style.color = '#34d399';
            regimeBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
            regimeBadge.style.background = 'rgba(52, 211, 153, 0.15)';
        } else if (specificEnergy < 0) {
            regimeBadge.textContent = 'BOUND ELLIPTICAL ORBIT';
            regimeBadge.style.color = '#38bdf8';
            regimeBadge.style.borderColor = 'rgba(56, 189, 248, 0.4)';
            regimeBadge.style.background = 'rgba(56, 189, 248, 0.15)';
        } else {
            regimeBadge.textContent = 'HYPERBOLIC ESCAPE';
            regimeBadge.style.color = '#c084fc';
            regimeBadge.style.borderColor = 'rgba(192, 132, 252, 0.4)';
            regimeBadge.style.background = 'rgba(192, 132, 252, 0.15)';
        }

        eReadout.textContent = ecc.toFixed(3);
        energyReadout.textContent = `${specificEnergy.toFixed(1)} MJ/kg`;
        perigeeReadout.textContent = `${Math.round(peri_alt)} km`;
        apogeeReadout.textContent = specificEnergy < 0 ? `${Math.round(apo_alt)} km` : '∞ (Unbound)';
    }

    // Sliders
    vSlider.oninput = () => {
        v0_kms = parseFloat(vSlider.value);
        vVal.textContent = `${v0_kms.toFixed(2)} km/s`;
        updateTelemetry();
    };

    hSlider.oninput = () => {
        altitude_km = parseInt(hSlider.value);
        hVal.textContent = `${altitude_km} km`;
        updateTelemetry();
    };

    atmosToggle.onchange = () => {
        hasAtmosphere = atmosToggle.checked;
    };

    // Presets
    document.getElementById('preset-ballistic').onclick = () => {
        v0_kms = 4.50; vSlider.value = v0_kms; vVal.textContent = `${v0_kms.toFixed(2)} km/s`;
        updateTelemetry(); fireCannon();
    };
    document.getElementById('preset-circular').onclick = () => {
        const r0 = R_EARTH_KM + altitude_km;
        v0_kms = Math.sqrt(GM / r0);
        vSlider.value = v0_kms.toFixed(2);
        vVal.textContent = `${v0_kms.toFixed(2)} km/s`;
        updateTelemetry(); fireCannon();
    };
    document.getElementById('preset-elliptic').onclick = () => {
        v0_kms = 9.60; vSlider.value = v0_kms; vVal.textContent = `${v0_kms.toFixed(2)} km/s`;
        updateTelemetry(); fireCannon();
    };
    document.getElementById('preset-escape').onclick = () => {
        v0_kms = 11.50; vSlider.value = v0_kms; vVal.textContent = `${v0_kms.toFixed(2)} km/s`;
        updateTelemetry(); fireCannon();
    };

    fireBtn.onclick = fireCannon;
    clearBtn.onclick = () => { projectiles = []; persistentTrails = []; };
    pauseBtn.onclick = () => {
        isRunning = !isRunning;
        pauseBtn.textContent = isRunning ? '❚❚' : '▶';
    };

    function fireCannon() {
        const r0 = R_EARTH_KM + altitude_km;
        // Cannon fires horizontally eastward (to the right) from North Pole
        projectiles.push({
            x: 0,
            y: r0,
            vx: v0_kms,
            vy: 0,
            path: [{ x: 0, y: r0 }],
            active: true,
            color: v0_kms > 11.19 ? '#c084fc' : (v0_kms > 7.8 ? '#34d399' : '#f87171')
        });
    }

    // RK4 Central Gravity Step
    function stepProjectile(p, dt) {
        if (!p.active) return;

        const f = (x, y, vx, vy) => {
            const r2 = x*x + y*y;
            const r = Math.sqrt(r2);
            if (r <= R_EARTH_KM) return [0, 0, 0, 0];

            // Gravitational acceleration: a = -GM / r² in direction of -r
            const a_grav = GM / r2;
            let ax = -a_grav * (x / r);
            let ay = -a_grav * (y / r);

            // Optional atmospheric drag (exponential scale height ~ 8.5 km)
            if (hasAtmosphere && r < R_EARTH_KM + 120) {
                const alt = r - R_EARTH_KM;
                const rho = Math.exp(-alt / 8.5);
                const speed = Math.sqrt(vx*vx + vy*vy);
                const dragConst = 0.0003;
                ax -= dragConst * rho * speed * vx;
                ay -= dragConst * rho * speed * vy;
            }

            return [vx, vy, ax, ay];
        };

        const k1 = f(p.x, p.y, p.vx, p.vy);
        const k2 = f(p.x + 0.5*dt*k1[0], p.y + 0.5*dt*k1[1], p.vx + 0.5*dt*k1[2], p.vy + 0.5*dt*k1[3]);
        const k3 = f(p.x + 0.5*dt*k2[0], p.y + 0.5*dt*k2[1], p.vx + 0.5*dt*k2[2], p.vy + 0.5*dt*k2[3]);
        const k4 = f(p.x + dt*k3[0], p.y + dt*k3[1], p.vx + dt*k3[2], p.vy + dt*k3[3]);

        p.x += (dt / 6) * (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]);
        p.y += (dt / 6) * (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]);
        p.vx += (dt / 6) * (k1[2] + 2*k2[2] + 2*k3[2] + k4[2]);
        p.vy += (dt / 6) * (k1[3] + 2*k2[3] + 2*k3[3] + k4[3]);

        const r = Math.sqrt(p.x*p.x + p.y*p.y);
        p.path.push({ x: p.x, y: p.y });

        // Check ground impact
        if (r <= R_EARTH_KM) {
            p.active = false;
            persistentTrails.push({ path: p.path, color: p.color });
        }

        // Check solar escape distance boundary
        if (r > R_EARTH_KM * 6) {
            p.active = false;
            persistentTrails.push({ path: p.path, color: p.color });
        }
    }

    // Auto-fire initial circular orbit
    updateTelemetry();
    fireCannon();

    // 60fps Loop
    let lastTime = performance.now();

    function loop(now) {
        requestAnimationFrame(loop);
        const elapsed = Math.min((now - lastTime) / 1000, 0.05);
        lastTime = now;

        if (isRunning) {
            // Speed up time: 10 substeps per frame
            const simDt = 2.8; 
            for (let s = 0; s < 8; s++) {
                projectiles.forEach(p => stepProjectile(p, simDt));
            }
        }

        // Render Canvas
        ctx.clearRect(0, 0, width, height);

        // 1. Draw Coordinate Grid & Distant Stars
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.04)';
        ctx.lineWidth = 1;
        for (let r_ring = 1; r_ring <= 4; r_ring++) {
            ctx.beginPath();
            ctx.arc(center.x, center.y, (R_EARTH_KM * r_ring) * pxPerKm, 0, Math.PI * 2);
            ctx.stroke();
        }

        // 2. Draw Atmospheric Halo
        const earthPxR = R_EARTH_KM * pxPerKm;
        const atmosGrad = ctx.createRadialGradient(center.x, center.y, earthPxR, center.x, center.y, earthPxR + 14);
        atmosGrad.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
        atmosGrad.addColorStop(1, 'rgba(56, 189, 248, 0.0)');
        ctx.fillStyle = atmosGrad;
        ctx.beginPath();
        ctx.arc(center.x, center.y, earthPxR + 14, 0, Math.PI * 2);
        ctx.fill();

        // 3. Draw Spherical Earth
        const earthGrad = ctx.createRadialGradient(center.x - 30, center.y - 40, 15, center.x, center.y, earthPxR);
        earthGrad.addColorStop(0, '#1e3a8a');
        earthGrad.addColorStop(0.7, '#0f172a');
        earthGrad.addColorStop(1, '#020617');

        ctx.fillStyle = earthGrad;
        ctx.beginPath();
        ctx.arc(center.x, center.y, earthPxR, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // 4. Draw Cannon Mountain at North Pole
        const mountainH_px = altitude_km * pxPerKm;
        const cannonX = center.x;
        const cannonY = center.y - earthPxR - mountainH_px;

        // Mountain cone
        ctx.fillStyle = '#475569';
        ctx.beginPath();
        ctx.moveTo(cannonX - 8, center.y - earthPxR);
        ctx.lineTo(cannonX, cannonY);
        ctx.lineTo(cannonX + 8, center.y - earthPxR);
        ctx.closePath();
        ctx.fill();

        // Cannon barrel pointing eastward
        ctx.strokeStyle = '#ffd700';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(cannonX, cannonY);
        ctx.lineTo(cannonX + 12, cannonY);
        ctx.stroke();

        // 5. Draw Persistent Old Trails
        persistentTrails.forEach(t => {
            if (t.path.length < 2) return;
            ctx.beginPath();
            ctx.moveTo(center.x + t.path[0].x * pxPerKm, center.y - t.path[0].y * pxPerKm);
            for (let i = 1; i < t.path.length; i++) {
                ctx.lineTo(center.x + t.path[i].x * pxPerKm, center.y - t.path[i].y * pxPerKm);
            }
            ctx.strokeStyle = t.color;
            ctx.globalAlpha = 0.35;
            ctx.lineWidth = 1.2;
            ctx.stroke();
            ctx.globalAlpha = 1.0;
        });

        // 6. Draw Active Projectiles & Live Trails
        projectiles.forEach(p => {
            if (p.path.length > 1) {
                ctx.beginPath();
                ctx.moveTo(center.x + p.path[0].x * pxPerKm, center.y - p.path[0].y * pxPerKm);
                for (let i = 1; i < p.path.length; i++) {
                    ctx.lineTo(center.x + p.path[i].x * pxPerKm, center.y - p.path[i].y * pxPerKm);
                }
                ctx.strokeStyle = p.color;
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 8;
                ctx.lineWidth = 2.2;
                ctx.stroke();
                ctx.shadowBlur = 0;
            }

            if (p.active) {
                const curPx = center.x + p.x * pxPerKm;
                const curPy = center.y - p.y * pxPerKm;
                ctx.fillStyle = '#ffffff';
                ctx.shadowColor = p.color;
                ctx.shadowBlur = 10;
                ctx.beginPath();
                ctx.arc(curPx, curPy, 4.5, 0, Math.PI * 2);
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        });
    }

    requestAnimationFrame(loop);
});
