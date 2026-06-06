document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Inflow Velocity (u₀): <span id="vel-val" class="math-value">0.08</span></label>
            <input type="range" id="vel-slider" min="0.02" max="0.15" step="0.01" value="0.08" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Viscosity / Reynolds Number (ω): <span id="omega-val" class="math-value">1.82</span></label>
            <input type="range" id="omega-slider" min="1.00" max="1.93" step="0.01" value="1.82" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Obstacle Diameter: <span id="r-val" class="math-value">18</span> px</label>
            <input type="range" id="r-slider" min="8" max="28" step="2" value="18" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Visualization Mode:</label><br>
            <select id="viz-mode" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="vorticity">Vorticity (Rotational Curl)</option>
                <option value="velocity">Velocity Magnitude</option>
                <option value="pressure">Density (Pressure)</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="play-pause" class="btn btn-primary" style="flex: 1;">Pause</button>
            <button id="reset-sim" class="btn btn-secondary">Reset</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Est. Reynolds Number (Re): <span id="re-val">150</span></div>
            <div style="font-size: 0.75rem; color: #5f6c8d; margin-top: 5px;">
                Red indicates counter-clockwise rotation, blue clockwise rotation. Semi-transparent particles show the local fluid velocity.
            </div>
        </div>
    `;

    const velSlider = document.getElementById('vel-slider');
    const omegaSlider = document.getElementById('omega-slider');
    const rSlider = document.getElementById('r-slider');
    const vizModeSelect = document.getElementById('viz-mode');
    const velVal = document.getElementById('vel-val');
    const omegaVal = document.getElementById('omega-val');
    const rVal = document.getElementById('r-val');
    const reVal = document.getElementById('re-val');
    const playPauseBtn = document.getElementById('play-pause');
    const resetSimBtn = document.getElementById('reset-sim');

    // LBM D2Q9 grid configurations
    const NX = 180;
    const NY = 60;
    const size = NX * NY;

    // Lattice constants
    const w = new Float32Array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36]);
    const cx = new Int32Array([0, 1, 0, -1, 0, 1, -1, -1, 1]);
    const cy = new Int32Array([0, 0, 1, 0, -1, 1, 1, -1, -1]);
    const opp = new Int32Array([0, 3, 4, 1, 2, 7, 8, 5, 6]);

    // D2Q9 distribution arrays
    let f = new Float32Array(9 * size);
    let f2 = new Float32Array(9 * size);

    // Macroscopic variables
    let rho = new Float32Array(size);
    let ux = new Float32Array(size);
    let uy = new Float32Array(size);
    let barrier = new Uint8Array(size);

    // Flow particles
    const numParticles = 800;
    let particles = [];

    // Simulation params
    let inletVel = 0.08;
    let omega = 1.82; // collision frequency
    let obstacleR = 9; // radius
    let isPlaying = true;
    let vizMode = 'vorticity';

    // Helper: grid index
    function idx(x, y) {
        return x * NY + y;
    }

    // Set up cylinder obstacle
    function setupObstacle() {
        barrier.fill(0);
        const ox = Math.floor(NX / 4);
        const oy = Math.floor(NY / 2);
        
        for (let x = 0; x < NX; x++) {
            for (let y = 0; y < NY; y++) {
                const distSq = (x - ox) * (x - ox) + (y - oy) * (y - oy);
                if (distSq < obstacleR * obstacleR) {
                    barrier[idx(x, y)] = 1;
                }
            }
        }
    }

    // Initialize fluid variables and LBM distribution functions to equilibrium
    function initFluid() {
        setupObstacle();

        // Initial uniform density and velocity
        for (let x = 0; x < NX; x++) {
            for (let y = 0; y < NY; y++) {
                const index = idx(x, y);
                rho[index] = 1.0;
                
                // Add a small perturbation to seed the symmetry breaking (vortex shedding)
                ux[index] = inletVel;
                uy[index] = barrier[index] ? 0 : 0.001 * Math.sin((x * Math.PI) / NX);

                // Compute equilibrium distributions
                for (let i = 0; i < 9; i++) {
                    const cu = 3 * (cx[i] * ux[index] + cy[i] * uy[index]);
                    const u2 = 1.5 * (ux[index] * ux[index] + uy[index] * uy[index]);
                    const feq = w[i] * rho[index] * (1 + cu + 0.5 * cu * cu - u2);
                    
                    f[i * size + index] = feq;
                    f2[i * size + index] = feq;
                }
            }
        }

        // Initialize particles
        particles = [];
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * NX,
                y: Math.random() * NY,
                age: Math.random() * 100
            });
        }

        updateReynolds();
    }

    function updateReynolds() {
        // Viscosity: nu = (1/omega - 0.5) / 3
        const nu = (1.0 / omega - 0.5) / 3.0;
        // Re = u_inlet * Diameter / nu
        const diam = obstacleR * 2;
        const Re = (inletVel * diam) / nu;
        reVal.innerText = Math.round(Re);
    }

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = Math.max(320, Math.floor(canvas.width * (NY / NX)));
    }
    window.addEventListener('resize', resize);
    resize();

    // UI Listeners
    velSlider.oninput = () => {
        inletVel = parseFloat(velSlider.value);
        velVal.innerText = inletVel.toFixed(2);
        updateReynolds();
    };

    omegaSlider.oninput = () => {
        omega = parseFloat(omegaSlider.value);
        omegaVal.innerText = omega.toFixed(2);
        updateReynolds();
    };

    rSlider.oninput = () => {
        obstacleR = parseInt(rSlider.value) / 2;
        rVal.innerText = parseInt(rSlider.value);
        setupObstacle();
        updateReynolds();
    };

    vizModeSelect.onchange = () => {
        vizMode = vizModeSelect.value;
    };

    playPauseBtn.onclick = () => {
        isPlaying = !isPlaying;
        playPauseBtn.innerText = isPlaying ? 'Pause' : 'Resume';
        playPauseBtn.className = isPlaying ? 'btn btn-primary' : 'btn btn-secondary';
    };

    resetSimBtn.onclick = () => {
        initFluid();
    };

    // LBM Step (Collision + Streaming + Boundaries)
    function stepLBM() {
        // Collision and Streaming to f2
        for (let x = 0; x < NX; x++) {
            for (let y = 0; y < NY; y++) {
                const index = idx(x, y);
                if (barrier[index]) continue;

                // 1. Compute macroscopic properties (rho, ux, uy)
                let r = 0;
                let tx = 0;
                let ty = 0;

                for (let i = 0; i < 9; i++) {
                    const val = f[i * size + index];
                    r += val;
                    tx += val * cx[i];
                    ty += val * cy[i];
                }

                if (r > 0) {
                    ux[index] = tx / r;
                    uy[index] = ty / r;
                    rho[index] = r;
                }

                // Force inlet velocity profile on the left boundary
                if (x === 0) {
                    ux[index] = inletVel;
                    uy[index] = 0;
                    r = 1.0;
                }

                // 2. Collision step & streaming directly
                const u2 = 1.5 * (ux[index] * ux[index] + uy[index] * uy[index]);
                for (let i = 0; i < 9; i++) {
                    const cu = 3 * (cx[i] * ux[index] + cy[i] * uy[index]);
                    const feq = w[i] * r * (1 + cu + 0.5 * cu * cu - u2);
                    const fval = f[i * size + index];
                    const collided = fval - omega * (fval - feq);

                    // Streaming target cell
                    let nextX = x + cx[i];
                    let nextY = y + cy[i];

                    // Solid walls (bounce back) at top/bottom boundary
                    if (nextY < 0 || nextY >= NY) {
                        f2[opp[i] * size + index] = collided;
                        continue;
                    }

                    // Open outlet boundary at right edge (copy from second-to-last column)
                    if (nextX >= NX) {
                        continue;
                    }

                    if (nextX < 0) {
                        // Left boundary handled at collision/macro level
                        continue;
                    }

                    // Solid obstacle bounce-back
                    const nextIndex = idx(nextX, nextY);
                    if (barrier[nextIndex]) {
                        f2[opp[i] * size + index] = collided;
                    } else {
                        f2[i * size + nextIndex] = collided;
                    }
                }
            }
        }

        // Outlet open boundary update
        for (let y = 0; y < NY; y++) {
            const indexEnd = idx(NX - 1, y);
            const indexPrev = idx(NX - 2, y);
            for (let i = 0; i < 9; i++) {
                f2[i * size + indexEnd] = f2[i * size + indexPrev];
            }
        }

        // Swap buffers f and f2
        const temp = f;
        f = f2;
        f2 = temp;
    }

    // Update tracers particles flowing with velocity fields
    function updateParticles() {
        for (let i = 0; i < numParticles; i++) {
            const p = particles[i];
            
            // Grid cell coordinate
            const gx = Math.floor(p.x);
            const gy = Math.floor(p.y);

            if (gx >= 0 && gx < NX - 1 && gy >= 0 && gy < NY - 1) {
                const index = idx(gx, gy);
                // Simple Euler integration
                p.x += ux[index] * 1.5;
                p.y += uy[index] * 1.5;
            } else {
                p.x = 0;
                p.y = Math.random() * NY;
            }

            p.age += 1;
            
            // Reset particles if they hit barrier or exit or get too old
            const pIndex = idx(Math.floor(p.x), Math.floor(p.y));
            if (p.x >= NX - 1 || p.x < 0 || p.y >= NY || p.y < 0 || barrier[pIndex] || p.age > 180) {
                p.x = 0;
                p.y = Math.random() * NY;
                p.age = 0;
            }
        }
    }

    // Initialize simulation
    initFluid();

    // Render loop
    function loop() {
        if (isPlaying) {
            // Run 2 physics cycles per frame for optimal speed
            stepLBM();
            stepLBM();
            updateParticles();
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Set up drawing dimensions
        const scaleX = canvas.width / NX;
        const scaleY = canvas.height / NY;

        const imgData = ctx.createImageData(canvas.width, canvas.height);
        const data = imgData.data;

        // Map vorticity color palette
        // Pre-calculate macroscopic variables for rendering
        for (let cyScreen = 0; cyScreen < canvas.height; cyScreen++) {
            const gy = Math.floor(cyScreen / scaleY);
            const yBounded = Math.max(0, Math.min(NY - 1, gy));

            for (let cxScreen = 0; cxScreen < canvas.width; cxScreen++) {
                const gx = Math.floor(cxScreen / scaleX);
                const xBounded = Math.max(0, Math.min(NX - 1, gx));
                
                const index = idx(xBounded, yBounded);
                const pixelIndex = (cxScreen + cyScreen * canvas.width) * 4;

                if (barrier[index]) {
                    // Obstacle: dark grey/black
                    data[pixelIndex] = 15;
                    data[pixelIndex + 1] = 23;
                    data[pixelIndex + 2] = 42;
                    data[pixelIndex + 3] = 255;
                    continue;
                }

                // Render based on selected visualization mode
                if (vizMode === 'vorticity') {
                    // Vorticity = curl = d(uy)/dx - d(ux)/dy
                    // Approximated by finite differences
                    const leftIdx = idx(Math.max(0, xBounded - 1), yBounded);
                    const rightIdx = idx(Math.min(NX - 1, xBounded + 1), yBounded);
                    const topIdx = idx(xBounded, Math.max(0, yBounded - 1));
                    const botIdx = idx(xBounded, Math.min(NY - 1, yBounded + 1));

                    const curl = (uy[rightIdx] - uy[leftIdx]) - (ux[botIdx] - ux[topIdx]);
                    
                    // Normalize curl value for visualization
                    const intensity = Math.max(-1, Math.min(1, curl * 25));
                    
                    if (intensity >= 0) {
                        // Positive curl: Red/Orange
                        data[pixelIndex] = Math.floor(15 + intensity * 230); // R
                        data[pixelIndex + 1] = Math.floor(23 + intensity * 80);  // G
                        data[pixelIndex + 2] = Math.floor(42 - intensity * 20);  // B
                    } else {
                        // Negative curl: Blue/Cyan
                        const absIntensity = Math.abs(intensity);
                        data[pixelIndex] = Math.floor(15 - absIntensity * 10);
                        data[pixelIndex + 1] = Math.floor(23 + absIntensity * 150);
                        data[pixelIndex + 2] = Math.floor(42 + absIntensity * 210);
                    }
                } else if (vizMode === 'velocity') {
                    // Velocity magnitude
                    const speed = Math.sqrt(ux[index] * ux[index] + uy[index] * uy[index]);
                    const intensity = Math.min(1.0, speed / (inletVel * 2.2));
                    
                    // Palette: Deep indigo to bright cyan/yellow
                    data[pixelIndex] = Math.floor(10 + intensity * 100);
                    data[pixelIndex + 1] = Math.floor(15 + intensity * 220);
                    data[pixelIndex + 2] = Math.floor(30 + intensity * 240);
                } else {
                    // Density (Pressure)
                    const p = rho[index];
                    // Map local density variance
                    const intensity = Math.max(0, Math.min(1, (p - 0.98) / 0.04));
                    
                    // Palette: Dark violet to bright green
                    data[pixelIndex] = Math.floor(intensity * 120);
                    data[pixelIndex + 1] = Math.floor(intensity * 230);
                    data[pixelIndex + 2] = Math.floor(120 + intensity * 100);
                }
                data[pixelIndex + 3] = 255; // Alpha
            }
        }

        ctx.putImageData(imgData, 0, 0);

        // Draw obstacle cylinder on top with nice glassmorphic glow
        const ox = Math.floor(NX / 4);
        const oy = Math.floor(NY / 2);
        const screenX = ox * scaleX;
        const screenY = oy * scaleY;
        const screenR = obstacleR * scaleX;

        // Draw shadow/glow behind cylinder
        const glowGrad = ctx.createRadialGradient(screenX, screenY, screenR - 2, screenX, screenY, screenR + 12);
        glowGrad.addColorStop(0, 'rgba(0,0,0,0.8)');
        glowGrad.addColorStop(0.5, 'rgba(100, 255, 218, 0.15)');
        glowGrad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = glowGrad;
        ctx.beginPath();
        ctx.arc(screenX, screenY, screenR + 12, 0, Math.PI * 2);
        ctx.fill();

        // Solid cylinder block
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#64ffda';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(screenX, screenY, screenR, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Draw tracer particles
        ctx.fillStyle = 'rgba(248, 250, 252, 0.45)';
        for (let i = 0; i < numParticles; i++) {
            const p = particles[i];
            const px = p.x * scaleX;
            const py = p.y * scaleY;
            ctx.beginPath();
            ctx.arc(px, py, 1.2, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
