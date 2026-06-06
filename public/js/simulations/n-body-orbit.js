document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Gravitational Constant (G): <span id="g-val" class="math-value">1.5</span></label>
            <input type="range" id="g-slider" min="0.2" max="6.0" step="0.1" value="1.5" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="preset-threebody" class="btn btn-primary" style="flex: 1; font-size:0.75rem;">Chaotic 3-Body</button>
            <button id="preset-solarsystem" class="btn btn-primary" style="flex: 1; font-size:0.75rem;">Solar System</button>
        </div>
        <div class="control-group" style="margin-top: 10px; display: flex; gap: 10px;">
            <button id="clear-btn" class="btn btn-secondary" style="flex: 1;">Clear All</button>
            <button id="reset-btn" class="btn btn-secondary" style="flex: 1;">Reset</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:5px;">
                • Click & drag to slingshot launch a new planet.<br>
                • Planets merge on collision (conserving momentum).
            </div>
            <div>Total Kinetic Energy: <span id="ke-val" class="math-value">0</span></div>
            <div>Total Potential Energy: <span id="pe-val" class="math-value">0</span></div>
            <div>Total Energy (E): <span id="e-val" class="math-value">0</span></div>
        </div>
    `;

    const gSlider = document.getElementById('g-slider');
    const gVal = document.getElementById('g-val');
    const clearBtn = document.getElementById('clear-btn');
    const resetBtn = document.getElementById('reset-btn');
    const presetThreebody = document.getElementById('preset-threebody');
    const presetSolarsystem = document.getElementById('preset-solarsystem');
    
    const keVal = document.getElementById('ke-val');
    const peVal = document.getElementById('pe-val');
    const eVal = document.getElementById('e-val');

    let G = 1.5;
    let bodies = [];
    let dragStart = null;
    let dragCurrent = null;
    let isDragging = false;
    let lastTimestamp = performance.now();

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
    }
    window.addEventListener('resize', resize);
    resize();

    // Preset configurations
    function loadPresetThreeBody() {
        bodies = [
            // Symmetrical chaotic figure-8 approximation or nice stable orbits
            { x: canvas.width / 2 - 120, y: canvas.height / 2, vx: 0, vy: 1.8, ax: 0, ay: 0, mass: 1200, color: '#f87171', path: [] },
            { x: canvas.width / 2 + 120, y: canvas.height / 2, vx: 0, vy: -1.8, ax: 0, ay: 0, mass: 1200, color: '#60a5fa', path: [] },
            { x: canvas.width / 2, y: canvas.height / 2 + 80, vx: -2.0, vy: 0, ax: 0, ay: 0, mass: 800, color: '#34d399', path: [] }
        ];
    }

    function loadPresetSolarSystem() {
        bodies = [
            // Massive Sun
            { x: canvas.width / 2, y: canvas.height / 2, vx: 0, vy: 0, ax: 0, ay: 0, mass: 10000, color: '#f59e0b', path: [] },
            // Inner planet (Mercury)
            { x: canvas.width / 2, y: canvas.height / 2 - 70, vx: 14.5, vy: 0, ax: 0, ay: 0, mass: 10, color: '#94a3b8', path: [] },
            // Middle planet (Earth)
            { x: canvas.width / 2, y: canvas.height / 2 - 130, vx: 10.7, vy: 0, ax: 0, ay: 0, mass: 50, color: '#60a5fa', path: [] },
            // Outer planet (Mars)
            { x: canvas.width / 2, y: canvas.height / 2 - 200, vx: 8.6, vy: 0, ax: 0, ay: 0, mass: 30, color: '#ef4444', path: [] }
        ];
    }

    // Control events
    gSlider.oninput = () => {
        G = parseFloat(gSlider.value);
        gVal.innerText = G.toFixed(1);
    };

    clearBtn.onclick = () => { bodies = []; };
    resetBtn.onclick = loadPresetThreeBody;
    presetThreebody.onclick = loadPresetThreeBody;
    presetSolarsystem.onclick = loadPresetSolarSystem;

    // Click-and-drag slingshot mouse interactions
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
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging) {
            dragCurrent = getMousePos(e);
        }
    });

    canvas.addEventListener('mouseup', () => {
        if (isDragging && dragStart && dragCurrent) {
            // Launch velocity is proportional to drag vector
            const dx = dragStart.x - dragCurrent.x;
            const dy = dragStart.y - dragCurrent.y;
            const mass = 120; // default medium mass
            
            bodies.push({
                x: dragStart.x,
                y: dragStart.y,
                vx: dx * 0.08, // scale factor
                vy: dy * 0.08,
                ax: 0, ay: 0,
                mass: mass,
                color: '#e2e8f0', // white planet
                path: []
            });
        }
        isDragging = false;
        dragStart = null;
        dragCurrent = null;
    });

    // Compute gravitational accelerations for all bodies
    function computeAccelerations() {
        // Reset accelerations to zero
        for (let b of bodies) {
            b.ax = 0;
            b.ay = 0;
        }

        const softening = 20; // prevents infinite forces at zero distance

        for (let i = 0; i < bodies.length; i++) {
            const b1 = bodies[i];
            for (let j = i + 1; j < bodies.length; j++) {
                const b2 = bodies[j];

                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const distSq = dx * dx + dy * dy;

                if (distSq > 0) {
                    const dist = Math.sqrt(distSq);
                    // Gravitational force: F = G * m1 * m2 / (r^2 + softening)
                    const force = (G * b1.mass * b2.mass) / (distSq + softening);
                    
                    // Accelerations: a = F / m
                    const f1 = force / b1.mass;
                    b1.ax += f1 * (dx / dist);
                    b1.ay += f1 * (dy / dist);

                    const f2 = force / b2.mass;
                    b2.ax -= f2 * (dx / dist);
                    b2.ay -= f2 * (dy / dist);
                }
            }
        }
    }

    // Handles merging of colliding bodies
    function handleCollisions() {
        let merged = new Set();
        let nextBodies = [];

        for (let i = 0; i < bodies.length; i++) {
            if (merged.has(i)) continue;
            let b1 = bodies[i];

            for (let j = i + 1; j < bodies.length; j++) {
                if (merged.has(j)) continue;
                let b2 = bodies[j];

                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const distSq = dx * dx + dy * dy;
                
                const r1 = Math.sqrt(b1.mass) / 2 + 2;
                const r2 = Math.sqrt(b2.mass) / 2 + 2;
                const minDist = r1 + r2;

                if (distSq < minDist * minDist) {
                    // Collision! Merge b2 into b1
                    const totalMass = b1.mass + b2.mass;
                    
                    // Inelastic collision: Conservation of momentum
                    b1.vx = (b1.vx * b1.mass + b2.vx * b2.mass) / totalMass;
                    b1.vy = (b1.vy * b1.mass + b2.vy * b2.mass) / totalMass;
                    
                    // Center of mass position
                    b1.x = (b1.x * b1.mass + b2.x * b2.mass) / totalMass;
                    b1.y = (b1.y * b1.mass + b2.y * b2.mass) / totalMass;

                    b1.mass = totalMass;
                    
                    // Choose more dominant color
                    if (b2.mass > b1.mass) {
                        b1.color = b2.color;
                    }

                    merged.add(j);
                }
            }
            nextBodies.push(b1);
        }
        bodies = nextBodies;
    }

    // Velocity Verlet Integrator (Symplectic integration)
    function integrate(dt) {
        if (bodies.length === 0) return;

        // 1. Update positions: x = x + v*dt + 0.5*a*dt^2
        for (let b of bodies) {
            b.x += b.vx * dt + 0.5 * b.ax * dt * dt;
            b.y += b.vy * dt + 0.5 * b.ay * dt * dt;
            
            // Save current acceleration
            b.prev_ax = b.ax;
            b.prev_ay = b.ay;
        }

        // 2. Compute accelerations at new positions
        computeAccelerations();

        // 3. Update velocities: v = v + 0.5*(a_prev + a_new)*dt
        for (let b of bodies) {
            b.vx += 0.5 * (b.prev_ax + b.ax) * dt;
            b.vy += 0.5 * (b.prev_ay + b.ay) * dt;
        }

        // 4. Resolve merges
        handleCollisions();
    }

    // Calculate total system energies
    function updateEnergies() {
        let ke = 0;
        let pe = 0;

        for (let i = 0; i < bodies.length; i++) {
            const b1 = bodies[i];
            // Kinetic energy: 0.5 * m * v^2
            ke += 0.5 * b1.mass * (b1.vx * b1.vx + b1.vy * b1.vy);

            for (let j = i + 1; j < bodies.length; j++) {
                const b2 = bodies[j];
                const dx = b2.x - b1.x;
                const dy = b2.y - b1.y;
                const dist = Math.sqrt(dx * dx + dy * dy) || 1.0;
                
                // Potential energy: -G * m1 * m2 / r
                pe -= (G * b1.mass * b2.mass) / dist;
            }
        }

        const totalE = ke + pe;

        keVal.innerText = Math.round(ke).toLocaleString();
        peVal.innerText = Math.round(pe).toLocaleString();
        eVal.innerText = Math.round(totalE).toLocaleString();
    }

    // Initial load
    loadPresetThreeBody();

    // Main render and physics loop
    function loop(timestamp) {
        // Enforce time-delta step
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 25; // scale relative to base step
        lastTimestamp = timestamp;

        // Perform multiple sub-steps for orbital integration stability
        const substeps = 4;
        const subDt = dt / substeps;
        for (let step = 0; step < substeps; step++) {
            integrate(subDt);
        }

        updateEnergies();
        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Deep space background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 1. Draw trajectories path trails
        for (let b of bodies) {
            // Append history
            b.path.push({ x: b.x, y: b.y });
            if (b.path.length > 250) b.path.shift();

            if (b.path.length > 1) {
                ctx.lineWidth = 1.2;
                for (let i = 1; i < b.path.length; i++) {
                    const alpha = (i / b.path.length) * 0.45;
                    // Draw trail in matching color
                    ctx.strokeStyle = b.color;
                    ctx.globalAlpha = alpha;
                    ctx.beginPath();
                    ctx.moveTo(b.path[i - 1].x, b.path[i - 1].y);
                    ctx.lineTo(b.path[i].x, b.path[i].y);
                    ctx.stroke();
                }
                ctx.globalAlpha = 1.0; // reset
            }
        }

        // 2. Draw planets/bodies
        for (let b of bodies) {
            // Radius scales with square root of mass
            const radius = Math.max(3, Math.sqrt(b.mass) / 2 + 1);

            // Draw body with glow
            ctx.shadowBlur = 8;
            ctx.shadowColor = b.color;
            ctx.fillStyle = b.color;
            ctx.beginPath();
            ctx.arc(b.x, b.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0; // reset
        }

        // 3. Draw slingshot launcher drag line
        if (isDragging && dragStart && dragCurrent) {
            // Velocity line
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 2.0;
            ctx.beginPath();
            ctx.moveTo(dragStart.x, dragStart.y);
            ctx.lineTo(dragCurrent.x, dragCurrent.y);
            ctx.stroke();

            // Starting point circle (green dot)
            ctx.fillStyle = '#10b981';
            ctx.beginPath();
            ctx.arc(dragStart.x, dragStart.y, 4, 0, Math.PI * 2);
            ctx.fill();

            // Vector arrow head
            const dx = dragStart.x - dragCurrent.x;
            const dy = dragStart.y - dragCurrent.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > 10) {
                const udx = dx / dist;
                const udy = dy / dist;
                const arrowX = dragStart.x;
                const arrowY = dragStart.y;
                
                ctx.fillStyle = '#f59e0b';
                ctx.beginPath();
                ctx.moveTo(arrowX, arrowY);
                // draw arrowhead along vector dir
                ctx.lineTo(arrowX - udx * 8 + udy * 4, arrowY - udy * 8 - udx * 4);
                ctx.lineTo(arrowX - udx * 8 - udy * 4, arrowY - udy * 8 + udx * 4);
                ctx.closePath();
                ctx.fill();
            }
        }
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
