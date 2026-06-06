document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Mass 1 (Upper): <span id="m1-val" class="math-value">12</span></label>
            <input type="range" id="m1-slider" min="5" max="30" value="12" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Mass 2 (Lower): <span id="m2-val" class="math-value">12</span></label>
            <input type="range" id="m2-slider" min="5" max="30" value="12" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Gravity (g): <span id="g-val" class="math-value">1.0</span></label>
            <input type="range" id="g-slider" min="0.2" max="2.5" step="0.1" value="1.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="reset-sim" class="btn btn-secondary" style="width: 100%">Reset Pendulums</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:5px;">
                • Simulates **two identical double pendulums** starting with a microscopic angle difference (Δθ₀ = 0.0001 rad).<br>
                • Watch the **Butterfly Effect** (chaos): they stay aligned, then diverge exponentially.
            </div>
            <div>Chamber Deviation (Δθ): <span id="dev-val" class="math-value">0.0000</span> rad</div>
        </div>
    `;

    const m1Slider = document.getElementById('m1-slider');
    const m2Slider = document.getElementById('m2-slider');
    const gSlider = document.getElementById('g-slider');
    const resetSimBtn = document.getElementById('reset-sim');
    const devVal = document.getElementById('dev-val');

    let r1 = 125; // rod length 1 (pixels)
    let r2 = 115; // rod length 2 (pixels)
    let m1 = 12;  // mass 1
    let m2 = 12;  // mass 2
    let g = 1.0;   // gravity scaling

    // Double Pendulum A (Cyan)
    let pA = {
        a1: Math.PI / 2, // angle 1
        a2: Math.PI / 2, // angle 2
        v1: 0.0,         // velocity 1
        v2: 0.0,         // velocity 2
        path: []
    };

    // Double Pendulum B (Magenta) - microscopically perturbed by 0.0001 rad
    let pB = {
        a1: Math.PI / 2 + 0.0001, 
        a2: Math.PI / 2, 
        v1: 0.0, 
        v2: 0.0,
        path: []
    };

    let isDragging = false;
    let dragBobIndex = 0; // 1: upper, 2: lower
    let lastTimestamp = performance.now();

    // Pivot center coordinates
    const pivot = { x: 0, y: 180 }; // set in resize

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 550;
        pivot.x = canvas.width / 2;
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    m1Slider.oninput = () => { m1 = parseInt(m1Slider.value); document.getElementById('m1-val').innerText = m1; };
    m2Slider.oninput = () => { m2 = parseInt(m2Slider.value); document.getElementById('m2-val').innerText = m2; };
    gSlider.oninput = () => { g = parseFloat(gSlider.value); document.getElementById('g-val').innerText = g.toFixed(1); };
    
    resetSimBtn.onclick = () => {
        pA.a1 = Math.PI / 2; pA.a2 = Math.PI / 2; pA.v1 = 0; pA.v2 = 0; pA.path = [];
        pB.a1 = Math.PI / 2 + 0.0001; pB.a2 = Math.PI / 2; pB.v1 = 0; pB.v2 = 0; pB.path = [];
    };

    // Mouse drag-and-drop settings for custom release
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        
        // Coordinates of Pendulum A bobs
        const x1 = pivot.x + r1 * Math.sin(pA.a1);
        const y1 = pivot.y + r1 * Math.cos(pA.a1);
        const x2 = x1 + r2 * Math.sin(pA.a2);
        const y2 = y1 + r2 * Math.cos(pA.a2);

        const dist1 = Math.sqrt((pos.x - x1) ** 2 + (pos.y - y1) ** 2);
        const dist2 = Math.sqrt((pos.x - x2) ** 2 + (pos.y - y2) ** 2);

        if (dist2 < 25) {
            isDragging = true;
            dragBobIndex = 2;
        } else if (dist1 < 25) {
            isDragging = true;
            dragBobIndex = 1;
        }

        if (isDragging) {
            pA.v1 = 0; pA.v2 = 0; pA.path = [];
            pB.v1 = 0; pB.v2 = 0; pB.path = [];
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const pos = getMousePos(e);
            
            if (dragBobIndex === 1) {
                // Drag upper bob
                const dx = pos.x - pivot.x;
                const dy = pos.y - pivot.y;
                pA.a1 = Math.atan2(dx, dy);
                // Perturb B slightly
                pB.a1 = pA.a1 + 0.0001;
            } else if (dragBobIndex === 2) {
                // Drag lower bob relative to upper bob position
                const x1 = pivot.x + r1 * Math.sin(pA.a1);
                const y1 = pivot.y + r1 * Math.cos(pA.a1);
                const dx = pos.x - x1;
                const dy = pos.y - y1;
                pA.a2 = Math.atan2(dx, dy);
                pB.a2 = pA.a2;
            }
        }
    });

    canvas.addEventListener('mouseup', () => {
        isDragging = false;
        dragBobIndex = 0;
    });

    canvas.addEventListener('mouseleave', () => {
        isDragging = false;
        dragBobIndex = 0;
    });

    // Runge-Kutta 4th Order (RK4) Derivatives calculator
    function getDerivatives(a1, a2, v1, v2) {
        const mu = 1 + m1 / m2;
        const dAngle = a1 - a2;

        // Equations of motion for double pendulum
        const num1 = g * (Math.sin(a2) * Math.cos(dAngle) - mu * Math.sin(a1)) - (r2 * v2 * v2 + r1 * v1 * v1 * Math.cos(dAngle)) * Math.sin(dAngle);
        const den1 = r1 * (mu - Math.cos(dAngle) * Math.cos(dAngle));
        const alpha1 = num1 / den1;

        const num2 = g * mu * (Math.sin(a1) * Math.cos(dAngle) - Math.sin(a2)) + (mu * r1 * v1 * v1 + r2 * v2 * v2 * Math.cos(dAngle)) * Math.sin(dAngle);
        const den2 = r2 * (mu - Math.cos(dAngle) * Math.cos(dAngle));
        const alpha2 = num2 / den2;

        return [v1, v2, alpha1, alpha2];
    }

    // Runge-Kutta 4th Order (RK4) Solver Step
    function rk4Step(p, dt) {
        const [da1_1, da2_1, dv1_1, dv2_1] = getDerivatives(p.a1, p.a2, p.v1, p.v2);

        const a1_k2 = p.a1 + da1_1 * 0.5 * dt;
        const a2_k2 = p.a2 + da2_1 * 0.5 * dt;
        const v1_k2 = p.v1 + dv1_1 * 0.5 * dt;
        const v2_k2 = p.v2 + dv2_1 * 0.5 * dt;
        const [da1_2, da2_2, dv1_2, dv2_2] = getDerivatives(a1_k2, a2_k2, v1_k2, v2_k2);

        const a1_k3 = p.a1 + da1_2 * 0.5 * dt;
        const a2_k3 = p.a2 + da2_2 * 0.5 * dt;
        const v1_k3 = p.v1 + dv1_2 * 0.5 * dt;
        const v2_k3 = p.v2 + dv2_2 * 0.5 * dt;
        const [da1_3, da2_3, dv1_3, dv2_3] = getDerivatives(a1_k3, a2_k3, v1_k3, v2_k3);

        const a1_k4 = p.a1 + da1_3 * dt;
        const a2_k4 = p.a2 + da2_3 * dt;
        const v1_k4 = p.v1 + dv1_3 * dt;
        const v2_k4 = p.v2 + dv2_3 * dt;
        const [da1_4, da2_4, dv1_4, dv2_4] = getDerivatives(a1_k4, a2_k4, v1_k4, v2_k4);

        p.a1 += (dt / 6) * (da1_1 + 2 * da1_2 + 2 * da1_3 + da1_4);
        p.a2 += (dt / 6) * (da2_1 + 2 * da2_2 + 2 * da2_3 + da2_4);
        p.v1 += (dt / 6) * (dv1_1 + 2 * dv1_2 + 2 * dv1_3 + dv1_4);
        p.v2 += (dt / 6) * (dv2_1 + 2 * dv2_2 + 2 * dv2_3 + dv2_4);
    }

    // Main animation and physics tick
    function loop(timestamp) {
        // Enforce time-delta step (scaled to dt = 0.016s)
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 15; // scale factor
        lastTimestamp = timestamp;

        if (!isDragging) {
            // Integrate both double pendulums using RK4 solver
            const substeps = 5;
            const subDt = dt / substeps;
            for (let i = 0; i < substeps; i++) {
                rk4Step(pA, subDt);
                rk4Step(pB, subDt);
            }

            // Calculate current divergence of angles (Butterfly Effect Lyapunov indicator)
            const d1 = Math.abs(pA.a1 - pB.a1);
            const d2 = Math.abs(pA.a2 - pB.a2);
            const dev = Math.sqrt(d1 * d1 + d2 * d2);
            devVal.innerText = dev.toFixed(4);
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Clear screen
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Calculate visual joints coordinates
        // Pendulum A
        const ax1 = pivot.x + r1 * Math.sin(pA.a1);
        const ay1 = pivot.y + r1 * Math.cos(pA.a1);
        const ax2 = ax1 + r2 * Math.sin(pA.a2);
        const ay2 = ay1 + r2 * Math.cos(pA.a2);

        // Pendulum B
        const bx1 = pivot.x + r1 * Math.sin(pB.a1);
        const by1 = pivot.y + r1 * Math.cos(pB.a1);
        const bx2 = bx1 + r2 * Math.sin(pB.a2);
        const by2 = by1 + r2 * Math.cos(pB.a2);

        // 1. Draw trajectory paths
        if (!isDragging) {
            pA.path.push({ x: ax2, y: ay2 });
            pB.path.push({ x: bx2, y: by2 });
            if (pA.path.length > 320) pA.path.shift();
            if (pB.path.length > 320) pB.path.shift();
        }

        // Draw trail A (Cyan neon)
        if (pA.path.length > 1) {
            ctx.lineWidth = 1.8;
            for (let i = 1; i < pA.path.length; i++) {
                const alpha = (i / pA.path.length) * 0.45;
                ctx.strokeStyle = `rgba(34, 211, 238, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(pA.path[i - 1].x, pA.path[i - 1].y);
                ctx.lineTo(pA.path[i].x, pA.path[i].y);
                ctx.stroke();
            }
        }

        // Draw trail B (Magenta neon)
        if (pB.path.length > 1) {
            ctx.lineWidth = 1.8;
            for (let i = 1; i < pB.path.length; i++) {
                const alpha = (i / pB.path.length) * 0.45;
                ctx.strokeStyle = `rgba(236, 72, 153, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(pB.path[i - 1].x, pB.path[i - 1].y);
                ctx.lineTo(pB.path[i].x, pB.path[i].y);
                ctx.stroke();
            }
        }

        // 2. Draw mechanical rods (Pendulums structures)
        // Draw Pendulum B (Magenta - drawn first so it sits slightly behind A)
        ctx.strokeStyle = 'rgba(236, 72, 153, 0.45)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(pivot.x, pivot.y);
        ctx.lineTo(bx1, by1);
        ctx.lineTo(bx2, by2);
        ctx.stroke();

        // Draw Pendulum A (Cyan - sits in front)
        ctx.strokeStyle = 'rgba(34, 211, 238, 0.7)';
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.moveTo(pivot.x, pivot.y);
        ctx.lineTo(ax1, ay1);
        ctx.lineTo(ax2, ay2);
        ctx.stroke();

        // Inner rods highlights
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(pivot.x, pivot.y);
        ctx.lineTo(ax1, ay1);
        ctx.lineTo(ax2, ay2);
        ctx.stroke();

        // 3. Draw pivot bearing joints
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(pivot.x, pivot.y, 8, 0, Math.PI * 2);
        ctx.arc(ax1, ay1, 6, 0, Math.PI * 2);
        ctx.arc(bx1, by1, 5, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // 4. Draw Bob spheres (metallic spheres)
        // Bob B (Magenta)
        ctx.fillStyle = '#db2777';
        ctx.beginPath();
        ctx.arc(bx1, by1, m1 / 2, 0, Math.PI * 2);
        ctx.arc(bx2, by2, m2 / 2, 0, Math.PI * 2);
        ctx.fill();

        // Bob A (Cyan)
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#06b6d4';
        
        // Upper bob A
        const grad1 = ctx.createRadialGradient(ax1 - 3, ay1 - 3, 1, ax1, ay1, m1 / 2);
        grad1.addColorStop(0, '#ffffff'); grad1.addColorStop(1, '#0891b2');
        ctx.fillStyle = grad1;
        ctx.beginPath(); ctx.arc(ax1, ay1, m1 / 2, 0, Math.PI * 2); ctx.fill();

        // Lower bob A
        const grad2 = ctx.createRadialGradient(ax2 - 3, ay2 - 3, 1, ax2, ay2, m2 / 2);
        grad2.addColorStop(0, '#ffffff'); grad2.addColorStop(1, '#0891b2');
        ctx.fillStyle = grad2;
        ctx.beginPath(); ctx.arc(ax2, ay2, m2 / 2, 0, Math.PI * 2); ctx.fill();

        ctx.shadowBlur = 0; // reset
    }

    // Start loop
    requestAnimationFrame(loop);
});
