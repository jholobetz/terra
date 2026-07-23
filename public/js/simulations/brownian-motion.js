document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>System Temperature (Speed): <span id="t-val" class="math-value">3.0</span></label>
            <input type="range" id="t-slider" min="0.5" max="8.0" step="0.1" value="3.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Gas Particles Count: <span id="c-val" class="math-value">70</span></label>
            <input type="range" id="c-slider" min="20" max="150" step="5" value="70" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="reset-sim" class="btn btn-secondary" style="width: 100%">Reset Path</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Large Tracer Mass: <span class="math-value">100m</span></div>
            <div>Tracer Displacement (Δr): <span id="disp-val" class="math-value">0</span> px</div>
            <div>Mean Sq. Displacement (MSD): <span id="msd-val" class="math-value">0</span> px²</div>
        </div>
    `;

    const tSlider = document.getElementById('t-slider');
    const cSlider = document.getElementById('c-slider');
    const tVal = document.getElementById('t-val');
    const cVal = document.getElementById('c-val');
    const dispVal = document.getElementById('disp-val');
    const msdVal = document.getElementById('msd-val');
    const resetSimBtn = document.getElementById('reset-sim');

    let temp = 3.0; // scales initial speeds
    let count = 70;
    let particles = [];
    let tracer = null;
    let initialTracerPos = { x: 0, y: 0 };
    let msdHistory = []; // stores { time, msd } for the graph
    let simTime = 0;
    let lastTimestamp = performance.now();

    // Initialize simulation particles
    function init() {
        particles = [];
        
        // 1. Create the large tracer particle (Heavy, e.g. pollen grain)
        tracer = {
            x: canvas.width / 2,
            y: canvas.height / 2,
            vx: 0,
            vy: 0,
            radius: 14,
            mass: 100.0,
            color: '#64ffda',
            path: []
        };
        initialTracerPos = { x: tracer.x, y: tracer.y };
        particles.push(tracer);
        msdHistory = [];
        simTime = 0;

        // 2. Create small, fast-moving background gas particles
        for (let i = 1; i < count; i++) {
            // Place particles randomly, ensuring no initial overlaps
            let x, y, overlap;
            const radius = 4.0;
            let attempts = 0;
            do {
                overlap = false;
                x = radius + Math.random() * (canvas.width - 2 * radius);
                y = radius + Math.random() * (canvas.height - 2 * radius);
                
                // Check overlap with existing particles
                for (let p of particles) {
                    const distSq = (x - p.x) * (x - p.x) + (y - p.y) * (y - p.y);
                    if (distSq < (radius + p.radius) * (radius + p.radius)) {
                        overlap = true;
                        break;
                    }
                }
                attempts++;
            } while (overlap && attempts < 100);

            // Maxwell-Boltzmann like initial velocity distribution
            const theta = Math.random() * 2 * Math.PI;
            const speed = Math.sqrt(-2 * Math.log(Math.random() || 0.001)) * temp * 0.7;

            particles.push({
                x, y,
                vx: speed * Math.cos(theta),
                vy: speed * Math.sin(theta),
                radius,
                mass: 1.0,
                color: 'rgba(148, 163, 184, 0.45)', // semi-transparent slate
                path: null
            });
        }
    }

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        init();
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    tSlider.oninput = () => {
        temp = parseFloat(tSlider.value);
        tVal.innerText = temp.toFixed(1);
        // Scale velocities of all gas particles dynamically to heat/cool the system
        for (let i = 1; i < particles.length; i++) {
            const p = particles[i];
            const currentSpeed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (currentSpeed > 0) {
                // Re-scale to match new temp
                const ratio = temp / 3.0; // normalize
                const theta = Math.atan2(p.vy, p.vx);
                const newSpeed = Math.sqrt(-2 * Math.log(Math.random() || 0.001)) * temp * 0.7;
                p.vx = newSpeed * Math.cos(theta);
                p.vy = newSpeed * Math.sin(theta);
            }
        }
    };

    cSlider.oninput = () => {
        count = parseInt(cSlider.value);
        cVal.innerText = count;
        init();
    };

    resetSimBtn.onclick = () => {
        tracer.path = [];
        initialTracerPos = { x: tracer.x, y: tracer.y };
        msdHistory = [];
        simTime = 0;
    };

    // 2D Elastic collisions check and update
    function handleCollisions() {
        for (let i = 0; i < particles.length; i++) {
            const p1 = particles[i];
            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];

                const dx = p2.x - p1.x;
                const dy = p2.y - p1.y;
                const distSq = dx * dx + dy * dy;
                const minDist = p1.radius + p2.radius;

                if (distSq < minDist * minDist) {
                    const dist = Math.sqrt(distSq) || 0.001;

                    // 1. Resolve overlap (static penetration correction)
                    const overlap = minDist - dist;
                    const nx = dx / dist;
                    const ny = dy / dist;

                    const totalMass = p1.mass + p2.mass;
                    // Move based on mass ratio (light particles move more, heavy tracer moves less)
                    p1.x -= nx * overlap * (p2.mass / totalMass);
                    p1.y -= ny * overlap * (p2.mass / totalMass);
                    p2.x += nx * overlap * (p1.mass / totalMass);
                    p2.y += ny * overlap * (p1.mass / totalMass);

                    // 2. Perform 2D Elastic impulse collision
                    const rvx = p2.vx - p1.vx;
                    const rvy = p2.vy - p1.vy;
                    const velAlongNormal = rvx * nx + rvy * ny;

                    // Do not resolve if velocities are already separating
                    if (velAlongNormal < 0) {
                        const e = 1.0; // Coefficient of restitution (perfectly elastic)
                        const impulseScalar = -(1 + e) * velAlongNormal / (1/p1.mass + 1/p2.mass);

                        // Apply impulse vector
                        p1.vx -= (impulseScalar / p1.mass) * nx;
                        p1.vy -= (impulseScalar / p1.mass) * ny;
                        p2.vx += (impulseScalar / p2.mass) * nx;
                        p2.vy += (impulseScalar / p2.mass) * ny;
                    }
                }
            }
        }
    }

    // Main animation and integration loop
    function loop(timestamp) {
        // Enforce time-delta step
        const dt = Math.min(0.03, (timestamp - lastTimestamp) / 1000) * 60; // scale relative to 60fps
        lastTimestamp = timestamp;

        if (isPlaying = true) { // running
            simTime += dt;

            // Integration & Wall collisions
            for (let p of particles) {
                p.x += p.vx * dt;
                p.y += p.vy * dt;

                // Wall collisions (bounce off boundaries)
                if (p.x - p.radius < 0) {
                    p.x = p.radius;
                    p.vx *= -1;
                } else if (p.x + p.radius > canvas.width) {
                    p.x = canvas.width - p.radius;
                    p.vx *= -1;
                }

                if (p.y - p.radius < 0) {
                    p.y = p.radius;
                    p.vy *= -1;
                } else if (p.y + p.radius > canvas.height) {
                    p.y = canvas.height - p.radius;
                    p.vy *= -1;
                }
            }

            // Resolve all elastic circle-circle collisions
            handleCollisions();

            // Track tracer path
            if (tracer) {
                tracer.path.push({ x: tracer.x, y: tracer.y });
                if (tracer.path.length > 600) {
                    tracer.path.shift();
                }

                // Compute displacement indicators
                const dx = tracer.x - initialTracerPos.x;
                const dy = tracer.y - initialTracerPos.y;
                const displacementSq = dx * dx + dy * dy;
                const displacement = Math.sqrt(displacementSq);

                dispVal.innerText = displacement.toFixed(1);
                msdVal.innerText = Math.round(displacementSq);

                // Record history for MSD plot (every 10 frames)
                if (Math.floor(simTime) % 10 === 0) {
                    msdHistory.push({
                        time: simTime,
                        msd: displacementSq
                    });
                    if (msdHistory.length > 150) {
                        msdHistory.shift();
                    }
                }
            }
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Deep space background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Draw tracer path history (fading cyan neon line)
        if (tracer && tracer.path.length > 1) {
            ctx.lineWidth = 2.5;
            for (let i = 1; i < tracer.path.length; i++) {
                const alpha = (i / tracer.path.length) * 0.6;
                ctx.strokeStyle = `rgba(100, 255, 218, ${alpha})`;
                ctx.beginPath();
                ctx.moveTo(tracer.path[i - 1].x, tracer.path[i - 1].y);
                ctx.lineTo(tracer.path[i].x, tracer.path[i].y);
                ctx.stroke();
            }
        }

        // Draw small gas particles
        for (let i = 1; i < particles.length; i++) {
            const p = particles[i];
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw large heavy tracer (glowing neon cyan)
        if (tracer) {
            // Shadow glow
            ctx.shadowBlur = 12;
            ctx.shadowColor = '#64ffda';
            ctx.fillStyle = tracer.color;
            ctx.beginPath();
            ctx.arc(tracer.x, tracer.y, tracer.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0; // Reset shadow

            // Border ring
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(tracer.x, tracer.y, tracer.radius, 0, Math.PI * 2);
            ctx.stroke();

            // Draw initial starting point indicator (dotted red crosshair)
            ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
            ctx.lineWidth = 1;
            ctx.setLineDash([2, 3]);
            ctx.beginPath();
            ctx.arc(initialTracerPos.x, initialTracerPos.y, 6, 0, Math.PI * 2);
            ctx.moveTo(initialTracerPos.x - 12, initialTracerPos.y);
            ctx.lineTo(initialTracerPos.x + 12, initialTracerPos.y);
            ctx.moveTo(initialTracerPos.x, initialTracerPos.y - 12);
            ctx.lineTo(initialTracerPos.x, initialTracerPos.y + 12);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Render small real-time MSD plot in the bottom right corner
        if (msdHistory.length > 1) {
            const plotW = 120;
            const plotH = 80;
            const plotX = canvas.width - plotW - 20;
            const plotY = canvas.height - plotH - 20;

            // Plot background box (glassmorphism look)
            ctx.fillStyle = 'rgba(15, 23, 42, 0.75)';
            ctx.strokeStyle = 'rgba(51, 65, 85, 0.6)';
            ctx.lineWidth = 1;
            ctx.fillRect(plotX, plotY, plotW, plotH);
            ctx.strokeRect(plotX, plotY, plotW, plotH);

            // Draw axis
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(plotX + 8, plotY + 5);
            ctx.lineTo(plotX + 8, plotY + plotH - 8);
            ctx.lineTo(plotX + plotW - 5, plotY + plotH - 8);
            ctx.stroke();

            // Draw MSD trend curve
            let maxMsd = 1000;
            for (let h of msdHistory) {
                if (h.msd > maxMsd) maxMsd = h.msd;
            }

            ctx.strokeStyle = '#b464ff';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            for (let i = 0; i < msdHistory.length; i++) {
                const px = plotX + 8 + (i / msdHistory.length) * (plotW - 16);
                // Invert Y axis
                const py = plotY + plotH - 8 - (msdHistory[i].msd / maxMsd) * (plotH - 16);
                if (i === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();

            // Label MSD graph
            ctx.fillStyle = '#64748b';
            ctx.font = '8px monospace';
            ctx.textAlign = 'left';
            ctx.fillText('MSD vs Time', plotX + 12, plotY + 12);
        }
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
