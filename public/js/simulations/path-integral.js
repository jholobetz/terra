document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Planck's Constant (ħ): <span id="hbar-val" class="math-value">0.40</span></label>
            <input type="range" id="hbar-slider" min="0.05" max="1.50" step="0.01" value="0.40" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Path Count (N): <span id="n-val" class="math-value">120</span></label>
            <input type="range" id="n-slider" min="20" max="250" step="5" value="120" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Particle Mass (m): <span id="m-val" class="math-value">1.0</span></label>
            <input type="range" id="m-slider" min="0.2" max="3.0" step="0.1" value="1.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Barrier Configuration:</label><br>
            <select id="barrier-type" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="free">Free Space (No Barrier)</option>
                <option value="single">Single Slit Diffraction</option>
                <option value="double">Double Slit Interference</option>
                <option value="tunnel">Potential Energy Barrier</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="regenerate-paths" class="btn btn-secondary" style="width: 100%">Regenerate Paths</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Transition Probability |Ψ|²: <span id="prob-val" class="math-value">0%</span></div>
            <div style="font-size: 0.75rem; color: #5f6c8d; margin-top: 8px;">
                • Drag the blue target (Bob's detector B) up and down.<br>
                • Observe how the vector chain (right) stretches out (constructive interference) or coils up (destructive interference) as Bob moves.
            </div>
        </div>
    `;

    const hbarSlider = document.getElementById('hbar-slider');
    const nSlider = document.getElementById('n-slider');
    const mSlider = document.getElementById('m-slider');
    const barrierTypeSelect = document.getElementById('barrier-type');
    const hbarVal = document.getElementById('hbar-val');
    const nVal = document.getElementById('n-val');
    const mVal = document.getElementById('m-val');
    const probVal = document.getElementById('prob-val');
    const regenerateBtn = document.getElementById('regenerate-paths');

    // Physical and simulation variables
    let hbar = 0.40;
    let pathCount = 120;
    let mass = 1.0;
    let barrierType = 'free';

    // Source (A) and Detector (B) positions
    let posA = { x: 40, y: 250 };
    let posB = { x: 0, y: 250 }; // x set in resize
    let isDraggingB = false;

    // Paths storage
    let paths = [];
    const numSegments = 40; // discretization segments per path
    const travelTime = 2.0;
    const dt = travelTime / numSegments;

    // Slits / Barrier properties
    const barrierWidth = 20;
    const slitSize = 40;
    const slitSep = 55;
    let barrierV0 = 15.0; // potential barrier height

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        posB.x = canvas.width / 2 - 40;
        posA.y = canvas.height / 2;
        posB.y = canvas.height / 2;
        generatePaths();
    }
    window.addEventListener('resize', resize);
    resize();

    // Generate path fluctuations using Fourier mode expansion:
    // y(x) = y_classical(x) + sum a_n * sin(n * pi * x / L)
    function generatePaths() {
        paths = [];
        const dx = (posB.x - posA.x) / numSegments;
        const numModes = 4;

        for (let j = 0; j < pathCount; j++) {
            const modes = [];
            // Random amplitudes for modes (higher modes are scaled down)
            for (let n = 1; n <= numModes; n++) {
                const maxAmp = 100.0 / n;
                modes.push((Math.random() - 0.5) * maxAmp);
            }

            // Populate discretized coordinates along the path
            const coords = [];
            for (let k = 0; k <= numSegments; k++) {
                const fraction = k / numSegments;
                const x = posA.x + k * dx;
                
                // Classical straight path
                const yClassical = posA.y + fraction * (posB.y - posA.y);
                
                // Add Fourier fluctuations
                let fluctuation = 0;
                for (let n = 1; n <= numModes; n++) {
                    fluctuation += modes[n - 1] * Math.sin(n * Math.PI * fraction);
                }

                coords.push({ x, y: yClassical + fluctuation });
            }

            paths.push({
                coords: coords,
                action: 0,
                phase: 0,
                blocked: false
            });
        }

        calculateActions();
    }

    // Calculate action S = integral(T - V) dt along each path
    function calculateActions() {
        const xBarrier = (posA.x + posB.x) / 2;

        for (let p of paths) {
            let S = 0;
            p.blocked = false;

            for (let k = 0; k < numSegments; k++) {
                const pt1 = p.coords[k];
                const pt2 = p.coords[k + 1];

                const vx = (pt2.x - pt1.x) / dt;
                const vy = (pt2.y - pt1.y) / dt;

                // 1. Kinetic energy T = 0.5 * m * v^2
                const T = 0.5 * mass * (vx * vx + vy * vy);

                // 2. Potential energy V at segment midpoint
                const mx = (pt1.x + pt2.x) / 2;
                const my = (pt1.y + pt2.y) / 2;
                let V = 0;

                // Check potential barrier interactions
                if (Math.abs(mx - xBarrier) < barrierWidth / 2) {
                    if (barrierType === 'tunnel') {
                        V = barrierV0; // potential barrier height
                    } else if (barrierType === 'single') {
                        // Check single slit crossing
                        if (Math.abs(my - canvas.height / 2) > slitSize / 2) {
                            p.blocked = true;
                        }
                    } else if (barrierType === 'double') {
                        // Check double slit crossing
                        const d1 = Math.abs(my - (canvas.height / 2 - slitSep / 2));
                        const d2 = Math.abs(my - (canvas.height / 2 + slitSep / 2));
                        if (d1 > slitSize / 2 && d2 > slitSize / 2) {
                            p.blocked = true;
                        }
                    }
                }

                // Lagrangian L = T - V
                const L = T - V;
                S += L * dt;
            }

            p.action = S;
            p.phase = S / hbar;
        }
    }

    // UI Control listeners
    hbarSlider.oninput = () => {
        hbar = parseFloat(hbarSlider.value);
        hbarVal.innerText = hbar.toFixed(2);
        calculateActions();
    };

    nSlider.oninput = () => {
        pathCount = parseInt(nSlider.value);
        nVal.innerText = pathCount;
        generatePaths();
    };

    mSlider.oninput = () => {
        mass = parseFloat(mSlider.value);
        mVal.innerText = mass.toFixed(1);
        calculateActions();
    };

    barrierTypeSelect.onchange = () => {
        barrierType = barrierTypeSelect.value;
        calculateActions();
    };

    regenerateBtn.onclick = () => {
        generatePaths();
    };

    // Drag Point B Bounding rect calculations
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        const dist = Math.sqrt((pos.x - posB.x) ** 2 + (pos.y - posB.y) ** 2);
        if (dist < 15) {
            isDraggingB = true;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDraggingB) {
            const pos = getMousePos(e);
            // Lock x coordinate, allow vertical drag
            posB.y = Math.max(20, Math.min(canvas.height - 20, pos.y));
            
            // Re-generate paths relative to B's new position
            generatePaths();
        }
    });

    canvas.addEventListener('mouseup', () => {
        isDraggingB = false;
    });

    canvas.addEventListener('mouseleave', () => {
        isDraggingB = false;
    });

    // Draw Loop
    function draw() {
        // Clear canvas
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cxRight = (3 * canvas.width) / 4;
        const cyRight = canvas.height / 2;
        const xBarrier = (posA.x + posB.x) / 2;

        // ==========================================
        // LEFT PANEL: Quantum Paths Workspace
        // ==========================================
        ctx.fillStyle = 'rgba(10, 15, 30, 0.3)';
        ctx.fillRect(0, 0, canvas.width / 2, canvas.height);

        // Labels
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 13px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('Quantum Paths (Sum over Histories)', 15, 25);

        // Draw physical potential barrier representation
        if (barrierType !== 'free') {
            ctx.fillStyle = 'rgba(71, 85, 105, 0.9)'; // solid barrier grey
            ctx.strokeStyle = '#64748b';
            ctx.lineWidth = 1;

            if (barrierType === 'tunnel') {
                // Glow effect for potential barrier
                ctx.fillStyle = 'rgba(236, 72, 153, 0.25)'; // pink potential barrier glow
                ctx.fillRect(xBarrier - barrierWidth / 2, 0, barrierWidth, canvas.height);
                
                ctx.fillStyle = 'rgba(236, 72, 153, 0.8)';
                ctx.font = '9px monospace';
                ctx.fillText('Potential V₀', xBarrier - 25, 12);
            } else if (barrierType === 'single') {
                // Draw top block
                ctx.fillRect(xBarrier - barrierWidth / 2, 0, barrierWidth, canvas.height / 2 - slitSize / 2);
                ctx.strokeRect(xBarrier - barrierWidth / 2, 0, barrierWidth, canvas.height / 2 - slitSize / 2);
                
                // Draw bottom block
                ctx.fillRect(xBarrier - barrierWidth / 2, canvas.height / 2 + slitSize / 2, barrierWidth, canvas.height / 2 - slitSize / 2);
                ctx.strokeRect(xBarrier - barrierWidth / 2, canvas.height / 2 + slitSize / 2, barrierWidth, canvas.height / 2 - slitSize / 2);
            } else if (barrierType === 'double') {
                // Draw top block
                ctx.fillRect(xBarrier - barrierWidth / 2, 0, barrierWidth, canvas.height / 2 - slitSep / 2 - slitSize / 2);
                ctx.strokeRect(xBarrier - barrierWidth / 2, 0, barrierWidth, canvas.height / 2 - slitSep / 2 - slitSize / 2);
                
                // Draw middle block
                const midStart = canvas.height / 2 - slitSep / 2 + slitSize / 2;
                const midHeight = slitSep - slitSize;
                ctx.fillRect(xBarrier - barrierWidth / 2, midStart, barrierWidth, midHeight);
                ctx.strokeRect(xBarrier - barrierWidth / 2, midStart, barrierWidth, midHeight);
                
                // Draw bottom block
                ctx.fillRect(xBarrier - barrierWidth / 2, canvas.height / 2 + slitSep / 2 + slitSize / 2, barrierWidth, canvas.height / 2);
                ctx.strokeRect(xBarrier - barrierWidth / 2, canvas.height / 2 + slitSep / 2 + slitSize / 2, barrierWidth, canvas.height / 2);
            }
        }

        // Draw paths
        for (let p of paths) {
            if (p.blocked) continue; // don't draw blocked paths

            ctx.beginPath();
            ctx.moveTo(p.coords[0].x, p.coords[0].y);
            for (let i = 1; i <= numSegments; i++) {
                ctx.lineTo(p.coords[i].x, p.coords[i].y);
            }

            // Color path according to phase angle
            const hue = (p.phase * (180 / Math.PI)) % 360;
            ctx.strokeStyle = `hsla(${hue}, 80%, 60%, 0.13)`; // semi-transparent phase color
            ctx.lineWidth = 1;
            ctx.stroke();
        }

        // Draw Source A (Green glowing emitter)
        ctx.shadowBlur = 8;
        ctx.shadowColor = '#10b981';
        ctx.fillStyle = '#10b981';
        ctx.beginPath();
        ctx.arc(posA.x, posA.y, 7, 0, Math.PI * 2);
        ctx.fill();

        // Draw Bob Detector B (Blue glowing draggable collector)
        ctx.shadowColor = '#3b82f6';
        ctx.fillStyle = '#60a5fa';
        ctx.beginPath();
        ctx.arc(posB.x, posB.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.arc(posB.x, posB.y, 8, 0, Math.PI * 2);
        ctx.stroke();

        // Labels emitters
        ctx.fillStyle = '#10b981';
        ctx.font = '10px monospace';
        ctx.fillText('Source (A)', posA.x - 25, posA.y - 12);
        ctx.fillStyle = '#60a5fa';
        ctx.fillText('Detector (B)', posB.x - 28, posB.y - 14);

        // ==========================================
        // RIGHT PANEL: Feynman Phase Vector Chain
        // ==========================================
        ctx.fillStyle = 'rgba(5, 7, 15, 0.5)';
        ctx.fillRect(canvas.width / 2, 0, canvas.width / 2, canvas.height);

        // Panel label
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 13px monospace';
        ctx.fillText("Feynman's Phase Vector Sum", canvas.width / 2 + 15, 25);

        // Draw Complex Plane Grid
        ctx.strokeStyle = 'rgba(71, 85, 105, 0.15)';
        ctx.lineWidth = 1;
        
        // Horizontal and Vertical Axes
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2 + 30, cyRight);
        ctx.lineTo(canvas.width - 30, cyRight);
        ctx.moveTo(cxRight, 30);
        ctx.lineTo(cxRight, canvas.height - 30);
        ctx.stroke();

        // Axis Labels
        ctx.fillStyle = 'rgba(148, 163, 184, 0.45)';
        ctx.font = '9px monospace';
        ctx.fillText('Re', canvas.width - 45, cyRight + 12);
        ctx.fillText('Im', cxRight + 8, 40);

        // Concentric Circles
        for (let r = 40; r <= 160; r += 40) {
            ctx.beginPath();
            ctx.arc(cxRight, cyRight, r, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Calculate Feynman Vector Chain and draw head-to-tail
        let sumRe = 0;
        let sumIm = 0;
        let activePathsCount = 0;

        // Normalizing vector length scale
        const vecScale = Math.min(1.6, 200 / pathCount);

        let currX = cxRight;
        let currY = cyRight;

        ctx.lineWidth = 1.5;

        for (let p of paths) {
            if (p.blocked) continue;
            activePathsCount++;

            const cosP = Math.cos(p.phase);
            const sinP = Math.sin(p.phase);

            sumRe += cosP;
            sumIm += sinP;

            // Draw segment vector
            const nextX = currX + cosP * vecScale;
            const nextY = currY - sinP * vecScale; // complex Im goes UP, canvas Y goes DOWN

            // Color code phase vector segment
            const hue = (p.phase * (180 / Math.PI)) % 360;
            ctx.strokeStyle = `hsla(${hue}, 85%, 65%, 0.55)`;

            ctx.beginPath();
            ctx.moveTo(currX, currY);
            ctx.lineTo(nextX, nextY);
            ctx.stroke();

            currX = nextX;
            currY = nextY;
        }

        // Draw resulting propagator vector (Sum Vector)
        if (activePathsCount > 0) {
            // Draw large neon arrow from center to end of chain
            ctx.strokeStyle = '#fbbf24'; // amber/gold resulting vector
            ctx.lineWidth = 3;
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#fbbf24';
            ctx.beginPath();
            ctx.moveTo(cxRight, cyRight);
            ctx.lineTo(currX, currY);
            ctx.stroke();
            ctx.shadowBlur = 0;

            // Resulting arrow head
            const dx = currX - cxRight;
            const dy = currY - cyRight;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist > 5) {
                const udx = dx / dist;
                const udy = dy / dist;
                ctx.fillStyle = '#fbbf24';
                ctx.beginPath();
                ctx.moveTo(currX, currY);
                ctx.lineTo(currX - udx * 10 + udy * 5, currY - udy * 10 - udx * 5);
                ctx.lineTo(currX - udx * 10 - udy * 5, currY - udy * 10 + udx * 5);
                ctx.closePath();
                ctx.fill();
            }

            // Calculate transition probability P = |Ψ|^2
            // normalized by max possible sum (which is when all paths align perfectly in phase)
            const magnitude = dist / (activePathsCount * vecScale);
            const prob = magnitude * magnitude;
            probVal.innerText = (prob * 100).toFixed(1) + '%';

            // Draw a glowing probability magnitude circle at the center
            ctx.strokeStyle = 'rgba(251, 191, 36, 0.2)';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(cxRight, cyRight, dist, 0, Math.PI * 2);
            ctx.stroke();
        } else {
            probVal.innerText = '0%';
        }

        // Middle separator line
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();
    }

    // Start loop
    requestAnimationFrame(loop);
});
