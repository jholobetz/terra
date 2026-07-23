document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Gate Operation Mode:</label><br>
            <select id="demon-mode" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="auto">Auto Demon (Sorting)</option>
                <option value="manual">Manual Gate (You are the Demon)</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Thermal Velocity (Temp): <span id="temp-val" class="math-value">3.0</span></label>
            <input type="range" id="temp-slider" min="1.0" max="6.0" step="0.2" value="3.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; flex-direction: column; gap: 8px;">
            <button id="btn-gate" class="btn btn-primary" style="display: none; background: #a855f7; border: none;">Open Gate (Spacebar)</button>
            <button id="erase-memory" class="btn btn-secondary">Erase Demon Memory</button>
            <button id="reset-sim" class="btn btn-secondary">Reset System</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size: 0.75rem; color: #64748b; margin-bottom: 8px;">
                • Auto Mode: Demon opens the gate only for fast particles going Left and slow particles going Right.<br>
                • Manual Mode: Press & hold Spacebar or the Open Gate button to sort.
            </div>
            <div>Demon Memory: <span id="bit-count" class="math-value">0</span> bits</div>
            <div>Erased heat dissipated: <span id="heat-diss" class="math-value">0</span> kBT ln2</div>
        </div>
    `;

    const demonModeSelect = document.getElementById('demon-mode');
    const tempSlider = document.getElementById('temp-slider');
    const tempVal = document.getElementById('temp-val');
    const btnGate = document.getElementById('btn-gate');
    const eraseMemoryBtn = document.getElementById('erase-memory');
    const resetSimBtn = document.getElementById('reset-sim');
    const bitCountVal = document.getElementById('bit-count');
    const heatDissVal = document.getElementById('heat-diss');

    let particles = [];
    const numParticles = 55;
    const pRadius = 5;

    // Simulation states
    let mode = 'auto';
    let baseTemp = 3.0;
    let gateOpen = false;
    let gateTargetHeight = 0; // 0 for closed, 1 for open
    let gateCurrentHeight = 0; // sliding door interpolation

    // Demon variables
    let bitsStored = 0;
    let bitsHistory = []; // list of '0's and '1's
    let heatDissipated = 0;
    let entropyHistory = [];
    let simTime = 0;
    let lastTimestamp = performance.now();

    // Heat burst display
    let heatBurstTimer = 0;

    // Gate dimensions
    let boxWidth = 0; // set in resize
    let midX = 0;
    let gateTop = 160;
    let gateBottom = 260;
    const gateHeight = gateBottom - gateTop;

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 450;
        boxWidth = canvas.width - 200;
        midX = boxWidth / 2;
        initParticles();
    }
    window.addEventListener('resize', resize);
    resize();

    // Initialize gas particles
    function initParticles() {
        particles = [];
        entropyHistory = [];
        bitsHistory = [];
        bitsStored = 0;
        heatDissipated = 0;
        simTime = 0;
        bitCountVal.innerText = '0';
        heatDissVal.innerText = '0';

        for (let i = 0; i < numParticles; i++) {
            // Distribute half left, half right
            const isLeft = i < numParticles / 2;
            let x;
            if (isLeft) {
                x = 15 + Math.random() * (midX - 30);
            } else {
                x = midX + 15 + Math.random() * (midX - 30);
            }
            const y = 15 + Math.random() * (canvas.height - 30);

            // Maxwell-Boltzmann distribution seeds
            const theta = Math.random() * 2 * Math.PI;
            const speed = Math.sqrt(-2 * Math.log(Math.random() || 0.01)) * baseTemp * 0.7;

            particles.push({
                x, y,
                vx: speed * Math.cos(theta),
                vy: speed * Math.sin(theta),
                radius: pRadius,
                mass: 1.0,
                // Color represents individual speed (red for hot, blue for cold)
                speed: speed
            });
        }
    }

    // UI Listeners
    demonModeSelect.onchange = () => {
        mode = demonModeSelect.value;
        if (mode === 'manual') {
            btnGate.style.display = 'block';
        } else {
            btnGate.style.display = 'none';
        }
    };

    tempSlider.oninput = () => {
        baseTemp = parseFloat(tempSlider.value);
        tempVal.innerText = baseTemp.toFixed(1);
    };

    // Manual gate press holding
    btnGate.onmousedown = () => { if (mode === 'manual') gateOpen = true; };
    btnGate.onmouseup = () => { if (mode === 'manual') gateOpen = false; };
    btnGate.addEventListener('touchstart', () => { if (mode === 'manual') gateOpen = true; });
    btnGate.addEventListener('touchend', () => { if (mode === 'manual') gateOpen = false; });

    // Keyboard Spacebar gate control
    window.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && mode === 'manual') {
            e.preventDefault();
            gateOpen = true;
        }
    });
    window.addEventListener('keyup', (e) => {
        if (e.code === 'Space' && mode === 'manual') {
            gateOpen = false;
        }
    });

    eraseMemoryBtn.onclick = () => {
        if (bitsStored > 0) {
            heatDissipated += bitsStored;
            bitsStored = 0;
            bitsHistory = [];
            heatBurstTimer = 35; // trigger heat display frames
            bitCountVal.innerText = '0';
            heatDissVal.innerText = heatDissipated;
        }
    };

    resetSimBtn.onclick = initParticles;

    // Calculate mean speed of the gas
    function getAverageSpeed() {
        let sum = 0;
        for (let p of particles) {
            sum += Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        }
        return sum / particles.length || 1.0;
    }

    // Auto Demon sorting logic
    function runDemonLogic() {
        if (mode !== 'auto') return;

        const avgSpeed = getAverageSpeed();
        let shouldOpen = false;

        // Demon monitors particles within 45px of the gate
        const monitorRange = 45;

        for (let p of particles) {
            const dx = p.x - midX;
            const dy = p.y - (gateTop + gateHeight / 2);
            
            // Check if particle is inside gate y-channel and close to midX
            if (p.y >= gateTop && p.y <= gateBottom && Math.abs(dx) < monitorRange) {
                const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);

                // Case 1: Fast particle on the right moving left
                if (dx > 0 && p.vx < 0 && speed > avgSpeed * 1.05) {
                    shouldOpen = true;
                    // Write '1' (hot decision bit) if it successfully crosses
                    if (p.x + p.vx < midX && !p.hasCrossed) {
                        bitsStored++;
                        bitsHistory.push('1');
                        p.hasCrossed = true;
                    }
                }
                // Case 2: Slow particle on the left moving right
                else if (dx < 0 && p.vx > 0 && speed < avgSpeed * 0.95) {
                    shouldOpen = true;
                    // Write '0' (cold decision bit) if it successfully crosses
                    if (p.x + p.vx > midX && !p.hasCrossed) {
                        bitsStored++;
                        bitsHistory.push('0');
                        p.hasCrossed = true;
                    }
                }
            } else {
                p.hasCrossed = false; // Reset crossing tag when out of range
            }
        }

        // Limit memory history size
        if (bitsHistory.length > 18) {
            bitsHistory.shift();
        }

        bitCountVal.innerText = bitsStored;
        gateOpen = shouldOpen;
    }

    // Resolves particle-particle elastic collisions
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
                    const overlap = minDist - dist;
                    const nx = dx / dist;
                    const ny = dy / dist;

                    // Push apart
                    p1.x -= nx * overlap * 0.5;
                    p1.y -= ny * overlap * 0.5;
                    p2.x += nx * overlap * 0.5;
                    p2.y += ny * overlap * 0.5;

                    // Elastic impulse velocity update
                    const rvx = p2.vx - p1.vx;
                    const rvy = p2.vy - p1.vy;
                    const velAlongNormal = rvx * nx + rvy * ny;

                    if (velAlongNormal < 0) {
                        const impulse = -2 * velAlongNormal / 2; // identical mass
                        p1.vx -= impulse * nx;
                        p1.vy -= impulse * ny;
                        p2.vx += impulse * nx;
                        p2.vy += impulse * ny;
                    }
                }
            }
        }
    }

    // Perform integration and boundary collisions
    function stepPhysics(dt) {
        // Interpolate gate slider position
        gateTargetHeight = gateOpen ? 1.0 : 0.0;
        gateCurrentHeight += (gateTargetHeight - gateCurrentHeight) * 0.25;

        // Current visual gate opening channel
        const currentOpenTop = gateTop + (gateHeight / 2) * gateCurrentHeight;
        const currentOpenBottom = gateBottom - (gateHeight / 2) * gateCurrentHeight;

        for (let p of particles) {
            // Integrate
            p.x += p.vx * dt;
            p.y += p.vy * dt;

            // Box outer wall collisions
            if (p.x - p.radius < 10) { p.x = 10 + p.radius; p.vx *= -1; }
            if (p.x + p.radius > boxWidth - 10) { p.x = boxWidth - 10 - p.radius; p.vx *= -1; }
            if (p.y - p.radius < 10) { p.y = 10 + p.radius; p.vy *= -1; }
            if (p.y + p.radius > canvas.height - 10) { p.y = canvas.height - 10 - p.radius; p.vy *= -1; }

            // Middle Divider wall collisions
            const prevX = p.x - p.vx * dt;
            
            // If particle crossed divider boundary mid-step
            if ((prevX < midX && p.x + p.radius > midX) || (prevX > midX && p.x - p.radius < midX)) {
                // Check if it is inside the CURRENT gate opening channel
                const insideGate = p.y >= currentOpenTop && p.y <= currentOpenBottom;
                
                if (!insideGate) {
                    // Solid wall collision: reflect
                    p.vx *= -1;
                    p.x = prevX; // reset position to avoid crossing solid line
                }
            }
        }

        // Handle particle collisions
        handleCollisions();
    }

    // Calculate temperatures (speeds) and Shannon entropy
    function updateMetrics() {
        let sumSpeedL = 0, countL = 0;
        let sumSpeedR = 0, countR = 0;

        for (let p of particles) {
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            if (p.x < midX) {
                sumSpeedL += speed * speed;
                countL++;
            } else {
                sumSpeedR += speed * speed;
                countR++;
            }
        }

        // Temperature is proportional to average kinetic energy
        const tempL = countL > 0 ? sumSpeedL / countL : 0;
        const tempR = countR > 0 ? sumSpeedR / countR : 0;

        // Position Shannon entropy: S_pos = - sum P_i ln P_i
        const pL = countL / numParticles;
        const pR = countR / numParticles;
        const sPos = -((pL > 0 ? pL * Math.log(pL) : 0) + (pR > 0 ? pR * Math.log(pR) : 0));

        // Thermal entropy: S_thermal = 1.5 * ln(T)
        const sTherm = 1.2 * ((pL > 0 && tempL > 0 ? pL * Math.log(tempL) : 0) + (pR > 0 && tempR > 0 ? pR * Math.log(tempR) : 0));
        
        // Total normalized entropy S
        const totalEntropy = sPos + sTherm;

        // Record history
        if (Math.floor(simTime) % 6 === 0) {
            entropyHistory.push({
                time: simTime,
                entropy: totalEntropy
            });
            if (entropyHistory.length > 140) {
                entropyHistory.shift();
            }
        }

        return { tempL, tempR, countL, countR };
    }

    // Main animation loop
    function loop(timestamp) {
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 15;
        lastTimestamp = timestamp;

        if (isPlaying = true) {
            simTime += dt;
            runDemonLogic();
            stepPhysics(dt);
        }

        const metrics = updateMetrics();
        draw(metrics);

        if (heatBurstTimer > 0) {
            heatBurstTimer--;
        }

        requestAnimationFrame(loop);
    }

    function draw(m) {
        // Clear screen
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 1. Draw temperature color fills in background chambers
        // Chamber A (Left) - warm red/pink
        const maxTemp = baseTemp * baseTemp * 2.0;
        const opacityL = Math.min(0.25, m.tempL / maxTemp * 0.3);
        ctx.fillStyle = `rgba(239, 68, 68, ${opacityL})`;
        ctx.fillRect(10, 10, midX - 10, canvas.height - 20);

        // Chamber B (Right) - cold blue/indigo
        const opacityR = Math.min(0.25, m.tempR / maxTemp * 0.3);
        ctx.fillStyle = `rgba(59, 130, 246, ${opacityR})`;
        ctx.fillRect(midX, 10, midX - 10, canvas.height - 20);

        // Draw outer box border
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 4;
        ctx.strokeRect(10, 10, boxWidth - 20, canvas.height - 20);

        // Draw solid middle divider segments
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 4;
        
        // Top divider segment
        ctx.beginPath();
        ctx.moveTo(midX, 10);
        ctx.lineTo(midX, gateTop);
        ctx.stroke();

        // Bottom divider segment
        ctx.beginPath();
        ctx.moveTo(midX, gateBottom);
        ctx.lineTo(midX, canvas.height - 10);
        ctx.stroke();

        // Draw sliding gate doors
        ctx.strokeStyle = '#a855f7'; // Purple gate
        ctx.lineWidth = 5;

        // Current gate sliding door positions
        const openTop = gateTop + (gateHeight / 2) * gateCurrentHeight;
        const openBottom = gateBottom - (gateHeight / 2) * gateCurrentHeight;

        ctx.beginPath();
        ctx.moveTo(midX, gateTop);
        ctx.lineTo(midX, openTop);
        ctx.moveTo(midX, gateBottom);
        ctx.lineTo(midX, openBottom);
        ctx.stroke();

        // Draw gate indicators (glowing LED on divider)
        ctx.fillStyle = gateOpen ? '#22c55e' : '#ef4444';
        ctx.beginPath();
        ctx.arc(midX, gateTop - 10, 4, 0, Math.PI * 2);
        ctx.arc(midX, gateBottom + 10, 4, 0, Math.PI * 2);
        ctx.fill();

        // Draw gas particles (color mapped to speed)
        ctx.lineWidth = 1;
        for (let p of particles) {
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
            const ratio = Math.min(1.0, speed / (baseTemp * 1.5));
            
            // Interpolate color from cold blue (0) to hot red (1)
            const r = Math.floor(59 + ratio * 180);
            const g = Math.floor(130 - ratio * 40);
            const b = Math.floor(246 - ratio * 180);

            ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
            ctx.strokeStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }

        // Draw "Demon" character guarding the gate (floating purple circle with eyes)
        const demonX = midX;
        const demonY = (gateTop + gateBottom) / 2;
        ctx.fillStyle = 'rgba(168, 85, 247, 0.2)';
        ctx.strokeStyle = '#a855f7';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(demonX, demonY, 12, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Demon eyes (glow green when open, red when closed)
        ctx.fillStyle = gateOpen ? '#22c55e' : '#ef4444';
        ctx.beginPath();
        ctx.arc(demonX - 4, demonY - 2, 2, 0, Math.PI * 2);
        ctx.arc(demonX + 4, demonY - 2, 2, 0, Math.PI * 2);
        ctx.fill();

        // Draw Chamber Labels
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`Chamber A (L)`, midX / 2, 30);
        ctx.fillText(`Chamber B (R)`, midX + midX / 2, 30);

        ctx.font = '10px monospace';
        ctx.fillStyle = 'rgba(239, 68, 68, 0.8)';
        ctx.fillText(`Temp: ${Math.round(m.tempL * 10)} K`, midX / 2, 45);
        ctx.fillStyle = 'rgba(96, 165, 250, 0.8)';
        ctx.fillText(`Temp: ${Math.round(m.tempR * 10)} K`, midX + midX / 2, 45);

        // ==========================================
        // RIGHT PANEL: Demon Statistics and Memory
        // ==========================================
        const panelX = boxWidth + 10;
        
        ctx.fillStyle = 'rgba(15, 23, 42, 0.6)';
        ctx.fillRect(boxWidth, 0, 200, canvas.height);

        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(boxWidth, 0);
        ctx.lineTo(boxWidth, canvas.height);
        ctx.stroke();

        // Section Title: Demon Memory
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("DEMON'S MEMORY TAPE", panelX, 25);

        // Draw scrolling bits tape
        const tapeY = 38;
        const tapeH = 20;
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(panelX, tapeY, 180, tapeH);
        ctx.strokeStyle = '#334155';
        ctx.strokeRect(panelX, tapeY, 180, tapeH);

        ctx.font = 'bold 10px monospace';
        ctx.textAlign = 'center';
        for (let i = 0; i < bitsHistory.length; i++) {
            const bit = bitsHistory[i];
            const bx = panelX + 10 + i * 9;
            ctx.fillStyle = bit === '1' ? '#ef4444' : '#60a5fa'; // hot bit vs cold bit
            ctx.fillText(bit, bx, tapeY + 14);
        }

        // Section Title: Entropy Graph
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 11px monospace';
        ctx.textAlign = 'left';
        ctx.fillText("THERMAL ENTROPY S", panelX, 85);

        // Draw Entropy Plot
        if (entropyHistory.length > 1) {
            const graphX = panelX;
            const graphY = 95;
            const graphW = 180;
            const graphH = 90;

            ctx.fillStyle = '#0f172a';
            ctx.fillRect(graphX, graphY, graphW, graphH);
            ctx.strokeStyle = '#334155';
            ctx.strokeRect(graphX, graphY, graphW, graphH);

            // Draw axis
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(graphX + 8, graphY + 5);
            ctx.lineTo(graphX + 8, graphY + graphH - 8);
            ctx.lineTo(graphX + graphW - 5, graphY + graphH - 8);
            ctx.stroke();

            // Find scale
            let minEnt = 100, maxEnt = -100;
            for (let h of entropyHistory) {
                if (h.entropy < minEnt) minEnt = h.entropy;
                if (h.entropy > maxEnt) maxEnt = h.entropy;
            }
            // Add padding to range
            minEnt -= 0.1;
            maxEnt += 0.1;
            const range = maxEnt - minEnt || 1.0;

            ctx.strokeStyle = '#a855f7';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            for (let i = 0; i < entropyHistory.length; i++) {
                const gx = graphX + 8 + (i / entropyHistory.length) * (graphW - 16);
                const gy = graphY + graphH - 8 - ((entropyHistory[i].entropy - minEnt) / range) * (graphH - 16);
                if (i === 0) ctx.moveTo(gx, gy);
                else ctx.lineTo(gx, gy);
            }
            ctx.stroke();
        }

        // Landauer Heat Erasure Animation effect
        if (heatBurstTimer > 0) {
            ctx.fillStyle = `rgba(239, 68, 68, ${heatBurstTimer / 45})`; // fading red overlay on right panel
            ctx.fillRect(boxWidth, 0, 200, canvas.height);
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 12px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('HEAT DISSIPATION BURST!', boxWidth + 100, canvas.height / 2 + 50);
            ctx.font = '9px monospace';
            ctx.fillText('Memory Erasure Cost: ΔS = kBT ln2', boxWidth + 100, canvas.height / 2 + 70);
        }
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
