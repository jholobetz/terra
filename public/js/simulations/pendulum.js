document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Pendulum Length (L): <span id="len-val" class="math-value">180</span> px</label>
            <input type="range" id="len-slider" min="60" max="280" value="180" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Gravity (g): <span id="g-val" class="math-value">9.8</span> m/s²</label>
            <input type="range" id="g-slider" min="2" max="25" step="0.2" value="9.8" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Air Damping (Friction): <span id="d-val" class="math-value">0.005</span></label>
            <input type="range" id="d-slider" min="0.000" max="0.040" step="0.001" value="0.005" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="reset-sim" class="btn btn-secondary" style="width: 100%">Reset Pendulum</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:5px;">
                • Click & drag the bob to release it from any angle.<br>
                • Solver integrates non-linear ODE: d²θ/dt² = -(g/L) sin θ.
            </div>
            <div>Release Angle (θ₀): <span id="angle-val" class="math-value">45</span>°</div>
        </div>
    `;

    const lenSlider = document.getElementById('len-slider');
    const gSlider = document.getElementById('g-slider');
    const dSlider = document.getElementById('d-slider');
    const resetSimBtn = document.getElementById('reset-sim');
    const angleVal = document.getElementById('angle-val');

    let L = 180; // rod length in pixels
    let g = 9.8; // gravity
    let damping = 0.005; // air friction

    // Pendulum state
    let theta = Math.PI / 4; // angle in radians (45 degrees)
    let omega = 0.0; // angular velocity (rad/s)
    let alpha = 0.0; // angular acceleration
    let isDragging = false;
    let path = [];
    let lastTimestamp = performance.now();

    // Pivot center coordinates
    const pivot = { x: 0, y: 80 }; // x set in resize

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        pivot.x = canvas.width / 2;
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    lenSlider.oninput = () => { L = parseInt(lenSlider.value); document.getElementById('len-val').innerText = L; path = []; };
    gSlider.oninput = () => { g = parseFloat(gSlider.value); document.getElementById('g-val').innerText = g.toFixed(1); };
    dSlider.oninput = () => { damping = parseFloat(dSlider.value); document.getElementById('d-val').innerText = damping.toFixed(3); };
    resetSimBtn.onclick = () => { theta = Math.PI / 4; omega = 0; alpha = 0; path = []; };

    // Mouse drag point bob detection
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        const bobX = pivot.x + L * Math.sin(theta);
        const bobY = pivot.y + L * Math.cos(theta);
        const dist = Math.sqrt((pos.x - bobX) ** 2 + (pos.y - bobY) ** 2);

        if (dist < 28) {
            isDragging = true;
            omega = 0;
            alpha = 0;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            const pos = getMousePos(e);
            const dx = pos.x - pivot.x;
            const dy = pos.y - pivot.y;
            
            // Calculate angle from vertical downwards
            theta = Math.atan2(dx, dy);
            
            // Limit angles slightly to prevent complete wrapping/breaking constraints
            if (theta > Math.PI - 0.05) theta = Math.PI - 0.05;
            if (theta < -Math.PI + 0.05) theta = -Math.PI + 0.05;

            // Display angle
            const deg = Math.round((theta * 180) / Math.PI);
            angleVal.innerText = deg;
            path = []; // clear trail on drag
        }
    });

    canvas.addEventListener('mouseup', () => {
        isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
        isDragging = false;
    });

    // Exact non-linear pendulum ODE integration (Verlet scheme)
    function integrate(dt) {
        if (isDragging) return;

        // Exact pendulum equation: alpha = -(g / L) * sin(theta) - damping * omega
        // We scale g and L slightly to match visual coordinates speed
        const scalingFactor = 4.0;
        alpha = -((g * scalingFactor) / (L * 0.1)) * Math.sin(theta) - damping * omega * 60;

        // Verlet/Semi-implicit Euler integration
        omega += alpha * dt;
        theta += omega * dt;

        // Display current angle in controls
        const deg = Math.round((theta * 180) / Math.PI);
        angleVal.innerText = deg;
    }

    // Main animation loop
    function loop(timestamp) {
        // Enforce time-delta step (scaled to target dt = 0.016s)
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 1.0;
        lastTimestamp = timestamp;

        // Multiple integration steps for numerical stability
        const substeps = 4;
        const subDt = dt / substeps;
        for (let i = 0; i < substeps; i++) {
            integrate(subDt);
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Clear screen
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Bob coordinates
        const bobX = pivot.x + L * Math.sin(theta);
        const bobY = pivot.y + L * Math.cos(theta);

        // 1. Draw bob's trajectory path history (glowing cyan neon line)
        if (!isDragging) {
            path.push({ x: bobX, y: bobY });
            if (path.length > 180) path.shift();
        }

        if (path.length > 1) {
            ctx.lineWidth = 2.0;
            for (let i = 1; i < path.length; i++) {
                const alphaVal = (i / path.length) * 0.45;
                ctx.strokeStyle = `rgba(34, 211, 238, ${alphaVal})`;
                ctx.beginPath();
                ctx.moveTo(path[i - 1].x, path[i - 1].y);
                ctx.lineTo(path[i].x, path[i].y);
                ctx.stroke();
            }
        }

        // Draw dotted path constraint arc on drag
        if (isDragging) {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.arc(pivot.x, pivot.y, L, 0, Math.PI * 2);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // 2. Draw Mechanical suspension rod (sleek metallic truss look)
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 4.0;
        ctx.beginPath();
        ctx.moveTo(pivot.x, pivot.y);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();

        // Inner rod highlight line
        ctx.strokeStyle = '#94a3b8';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(pivot.x, pivot.y);
        ctx.lineTo(bobX, bobY);
        ctx.stroke();

        // 3. Draw pivot bearing joint
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(pivot.x, pivot.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // 4. Draw pendulum bob (metallic sphere with glowing core)
        const bobRadius = 18;
        ctx.shadowBlur = isDragging ? 15 : 10;
        ctx.shadowColor = '#06b6d4';
        
        // Sphere gradient
        const grad = ctx.createRadialGradient(bobX - 5, bobY - 5, 2, bobX, bobY, bobRadius);
        grad.addColorStop(0, '#ffffff'); // specular shine
        grad.addColorStop(0.3, '#22d3ee'); // bright cyan
        grad.addColorStop(1, '#0891b2'); // dark cyan edge
        
        ctx.fillStyle = grad;
        ctx.beginPath();
        ctx.arc(bobX, bobY, bobRadius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        // Draw outer ring border
        ctx.strokeStyle = 'rgba(255,255,255,0.25)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(bobX, bobY, bobRadius, 0, Math.PI * 2);
        ctx.stroke();

        // ==========================================
        // DYNAMIC ENERGY METERS (Kinetic vs Potential)
        // ==========================================
        // Kinetic Energy: KE = 0.5 * m * v^2 = 0.5 * m * (L * omega)^2
        // Potential Energy: PE = m * g * h = m * g * L * (1 - cos(theta))
        // We scale calculations for visual display
        const m = 1.0;
        const ke = 0.5 * m * (L * 0.05 * omega) * (L * 0.05 * omega) * 20;
        const pe = m * g * (L * 0.05) * (1 - Math.cos(theta)) * 20;
        const total = ke + pe;

        const meterX = 25;
        const meterY = canvas.height - 130;
        const meterW = 35;
        const meterH = 95;

        // Draw Energy boxes (glassmorphism look)
        ctx.fillStyle = 'rgba(15, 23, 42, 0.7)';
        ctx.strokeStyle = 'rgba(51, 65, 85, 0.6)';
        ctx.lineWidth = 1;
        ctx.fillRect(meterX - 10, meterY - 15, 150, meterH + 35);
        ctx.strokeRect(meterX - 10, meterY - 15, 150, meterH + 35);

        // A. Kinetic Energy Bar (Cyan)
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(meterX, meterY, meterW, meterH); // background channel
        ctx.fillStyle = '#06b6d4';
        const keBarH = Math.min(meterH, (ke / total) * meterH || 0);
        ctx.fillRect(meterX, meterY + meterH - keBarH, meterW, keBarH);

        // B. Potential Energy Bar (Purple)
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(meterX + 50, meterY, meterW, meterH);
        ctx.fillStyle = '#a855f7';
        const peBarH = Math.min(meterH, (pe / total) * meterH || 0);
        ctx.fillRect(meterX + 50, meterY + meterH - peBarH, meterW, peBarH);

        // C. Total Energy Bar (Green)
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(meterX + 100, meterY, 20, meterH);
        ctx.fillStyle = '#10b981';
        // Total energy remains constant (unless damping is high)
        const totalBarH = Math.min(meterH, (total / 120) * meterH || 0);
        ctx.fillRect(meterX + 100, meterY + meterH - totalBarH, 20, totalBarH);

        // Labels
        ctx.fillStyle = '#94a3b8';
        ctx.font = '9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('KE', meterX + meterW / 2, meterY + meterH + 12);
        ctx.fillText('PE', meterX + 50 + meterW / 2, meterY + meterH + 12);
        ctx.fillText('Total', meterX + 110, meterY + meterH + 12);

        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 8px monospace';
        ctx.fillText('ENERGY METERS', meterX + 65, meterY - 5);
    }

    // Start loop
    requestAnimationFrame(loop);
});
