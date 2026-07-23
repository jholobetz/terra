document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Relative Velocity (v/c): <span id="v-val" class="math-value">0.50</span></label>
            <input type="range" id="v-slider" min="-0.95" max="0.95" step="0.01" value="0.50" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px;">
            <label><input type="checkbox" id="show-lightcone" checked> Show Light Cones (x = ±ct)</label><br>
            <label><input type="checkbox" id="show-moving-grid" checked> Show Moving Coordinate Grid (x', ct')</label><br>
            <label><input type="checkbox" id="show-contraction" checked> Highlight Length Contraction</label><br>
            <label><input type="checkbox" id="show-dilation" checked> Highlight Time Dilation</label>
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="play-pause" class="btn btn-primary" style="flex: 1;">Animate Observer</button>
            <button id="reset-sim" class="btn btn-secondary">Reset</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Lorentz Factor (γ): <span id="gamma-val">1.15</span></div>
            <div>Moving clock elapsed time: <span id="t-prime-val">0.00</span>s</div>
            <div>Stationary clock elapsed time: <span id="t-val">0.00</span>s</div>
        </div>
    `;

    const vSlider = document.getElementById('v-slider');
    const vVal = document.getElementById('v-val');
    const showLightcone = document.getElementById('show-lightcone');
    const showMovingGrid = document.getElementById('show-moving-grid');
    const showContraction = document.getElementById('show-contraction');
    const showDilation = document.getElementById('show-dilation');
    const playPauseBtn = document.getElementById('play-pause');
    const resetSimBtn = document.getElementById('reset-sim');
    const gammaVal = document.getElementById('gamma-val');
    const tPrimeVal = document.getElementById('t-prime-val');
    const tVal = document.getElementById('t-val');

    let beta = 0.50; // v/c
    let gamma = 1 / Math.sqrt(1 - beta * beta);
    let isAnimating = false;
    let observerTime = 0; // proper time t' of the traveling observer
    let lastTimestamp = performance.now();

    // Resize handler
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    vSlider.oninput = () => {
        beta = parseFloat(vSlider.value);
        vVal.innerText = beta.toFixed(2);
        gamma = 1 / Math.sqrt(1 - beta * beta);
        gammaVal.innerText = gamma.toFixed(3);
    };

    playPauseBtn.onclick = () => {
        isAnimating = !isAnimating;
        playPauseBtn.innerText = isAnimating ? 'Pause' : 'Animate Observer';
        playPauseBtn.className = isAnimating ? 'btn btn-secondary' : 'btn btn-primary';
    };

    resetSimBtn.onclick = () => {
        observerTime = 0;
        isAnimating = false;
        playPauseBtn.innerText = 'Animate Observer';
        playPauseBtn.className = 'btn btn-primary';
        tPrimeVal.innerText = '0.00';
        tVal.innerText = '0.00';
    };

    // Main render and physics loop
    function loop(timestamp) {
        // Calculate delta time
        const dt = (timestamp - lastTimestamp) / 1000;
        lastTimestamp = timestamp;

        if (isAnimating) {
            observerTime += dt * 0.8; // scaling factor for simulation speed
            if (observerTime > 4.5) {
                observerTime = 0; // loop animation
            }
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Clear canvas with dark slate background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cx = canvas.width / 2;
        const cy = canvas.height / 2;
        const scale = Math.min(canvas.width, canvas.height) / 10; // Pixels per unit of length/time

        // Draw helper functions
        const toScreen = (x, ct) => {
            return {
                x: cx + x * scale,
                y: cy - ct * scale
            };
        };

        // Draw rest frame grid lines (x, ct)
        ctx.strokeStyle = '#1a2236';
        ctx.lineWidth = 1;
        const maxUnits = 6;
        for (let i = -maxUnits; i <= maxUnits; i++) {
            if (i === 0) continue;
            // Vertical grid lines (constant x)
            let pTop = toScreen(i, maxUnits);
            let pBot = toScreen(i, -maxUnits);
            ctx.beginPath();
            ctx.moveTo(pTop.x, pTop.y);
            ctx.lineTo(pBot.x, pBot.y);
            ctx.stroke();

            // Horizontal grid lines (constant ct)
            let pLeft = toScreen(-maxUnits, i);
            let pRight = toScreen(maxUnits, i);
            ctx.beginPath();
            ctx.moveTo(pLeft.x, pLeft.y);
            ctx.lineTo(pRight.x, pRight.y);
            ctx.stroke();
        }

        // Draw Rest Frame Axes
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.beginPath();
        // Time axis (ct)
        ctx.moveTo(cx, 0); ctx.lineTo(cx, canvas.height);
        // Space axis (x)
        ctx.moveTo(0, cy); ctx.lineTo(canvas.width, cy);
        ctx.stroke();

        // Label rest axes
        ctx.fillStyle = '#94a3b8';
        ctx.font = '12px monospace';
        ctx.fillText('ct (Rest Time)', cx + 10, 20);
        ctx.fillText('x (Rest Space)', canvas.width - 95, cy - 10);

        // Draw Light Cones (x = ±ct)
        if (showLightcone.checked) {
            ctx.strokeStyle = 'rgba(234, 179, 8, 0.4)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([5, 5]);
            
            // Forward and backward light cones
            ctx.beginPath();
            ctx.moveTo(cx - maxUnits * scale, cy - maxUnits * scale);
            ctx.lineTo(cx + maxUnits * scale, cy + maxUnits * scale);
            ctx.moveTo(cx - maxUnits * scale, cy + maxUnits * scale);
            ctx.lineTo(cx + maxUnits * scale, cy - maxUnits * scale);
            ctx.stroke();
            ctx.setLineDash([]); // Reset line dash
            
            ctx.fillStyle = 'rgba(234, 179, 8, 0.8)';
            ctx.fillText('Future Light Cone', cx + 10, cy - 150);
            ctx.fillText('Past Light Cone', cx + 10, cy + 160);
        }

        // Lorentz transformations for moving frame
        // x' -> moving space, ct' -> moving time
        // x = gamma * (x' + beta * ct')
        // ct = gamma * (ct' + beta * x')
        const transform = (xPrime, ctPrime) => {
            const x = gamma * (xPrime + beta * ctPrime);
            const ct = gamma * (ctPrime + beta * xPrime);
            return toScreen(x, ct);
        };

        // Draw moving coordinate grid
        if (showMovingGrid.checked) {
            ctx.lineWidth = 1;

            // Draw constant x' lines (worldlines of moving observers)
            // Color coordinates: cyan (positive velocity) / magenta (negative velocity)
            const gridColor = beta >= 0 ? 'rgba(6, 182, 212, 0.25)' : 'rgba(217, 70, 239, 0.25)';
            ctx.strokeStyle = gridColor;

            for (let i = -maxUnits; i <= maxUnits; i++) {
                ctx.beginPath();
                for (let ctP = -maxUnits; ctP <= maxUnits; ctP += 0.2) {
                    const pt = transform(i, ctP);
                    if (ctP === -maxUnits) {
                        ctx.moveTo(pt.x, pt.y);
                    } else {
                        ctx.lineTo(pt.x, pt.y);
                    }
                }
                ctx.stroke();
            }

            // Draw constant ct' lines (hyperplanes of moving simultaneity)
            for (let i = -maxUnits; i <= maxUnits; i++) {
                ctx.beginPath();
                for (let xP = -maxUnits; xP <= maxUnits; xP += 0.2) {
                    const pt = transform(xP, i);
                    if (xP === -maxUnits) {
                        ctx.moveTo(pt.x, pt.y);
                    } else {
                        ctx.lineTo(pt.x, pt.y);
                    }
                }
                ctx.stroke();
            }
        }

        // Draw Moving Axes (x'=0, ct'=0)
        const axisColor = beta >= 0 ? '#06b6d4' : '#d946ef';
        ctx.strokeStyle = axisColor;
        ctx.lineWidth = 2.5;

        // ct' axis (x'=0)
        ctx.beginPath();
        for (let ctP = -maxUnits; ctP <= maxUnits; ctP += 0.5) {
            const pt = transform(0, ctP);
            if (ctP === -maxUnits) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.stroke();

        // x' axis (ct'=0)
        ctx.beginPath();
        for (let xP = -maxUnits; xP <= maxUnits; xP += 0.5) {
            const pt = transform(xP, 0);
            if (xP === -maxUnits) ctx.moveTo(pt.x, pt.y);
            else ctx.lineTo(pt.x, pt.y);
        }
        ctx.stroke();

        // Label moving axes
        ctx.fillStyle = axisColor;
        const ctLabelPt = transform(0, maxUnits - 0.5);
        const xLabelPt = transform(maxUnits - 0.5, 0);
        ctx.fillText("ct' (Moving Time)", ctLabelPt.x + 12, ctLabelPt.y + 5);
        ctx.fillText("x' (Moving Space)", xLabelPt.x - 100, xLabelPt.y - 12);

        // Highlight Length Contraction Demonstration
        if (showContraction.checked) {
            // Draw a physical rod moving in the frame.
            // Rod ends are at x' = 0 and x' = 2 in the moving frame.
            // In the rest frame, at t=0, the rod ends are at x = 0 and x = 2/gamma.
            const rodLengthPrime = 2.0;
            const rodLengthRest = rodLengthPrime / gamma;

            const ptLeft = transform(0, 0);
            const ptRight = transform(rodLengthPrime, 0);

            // Draw proper length rod along moving x' axis
            ctx.strokeStyle = 'rgba(234, 88, 12, 0.8)';
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.moveTo(ptLeft.x, ptLeft.y);
            ctx.lineTo(ptRight.x, ptRight.y);
            ctx.stroke();

            // Draw contracted length along stationary x axis (t = 0)
            const ptRestRight = toScreen(rodLengthRest, 0);
            ctx.strokeStyle = '#38bdf8';
            ctx.beginPath();
            ctx.moveTo(cx, cy + 12);
            ctx.lineTo(ptRestRight.x, cy + 12);
            ctx.stroke();

            // Draw labels
            ctx.fillStyle = 'rgba(234, 88, 12, 1)';
            ctx.fillText(`Rod Proper Length (L₀ = ${rodLengthPrime.toFixed(1)})`, ptRight.x + 10, ptRight.y + 15);
            ctx.fillStyle = '#38bdf8';
            ctx.fillText(`Contracted Length (L = ${rodLengthRest.toFixed(2)})`, ptRestRight.x + 10, cy + 25);
            
            // Connect projection lines
            ctx.strokeStyle = 'rgba(255,255,255,0.2)';
            ctx.lineWidth = 1;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            // From moving rod end (x'=2, t'=0) along a line of simultaneity in rest frame?
            // Actually, we project the worldline of the rod's right end (x'=2) to rest frame t=0
            const worldlineEndBot = transform(rodLengthPrime, -2);
            const worldlineEndTop = transform(rodLengthPrime, 2);
            ctx.moveTo(worldlineEndBot.x, worldlineEndBot.y);
            ctx.lineTo(worldlineEndTop.x, worldlineEndTop.y);
            ctx.stroke();
            ctx.setLineDash([]);
        }

        // Highlight Time Dilation Demonstration
        if (showDilation.checked) {
            // Visualize a clock at rest in the moving frame (x' = 0)
            // It ticks at ct' = 2.0. In rest frame, this event occurs at:
            // x = gamma * beta * 2.0, ct = gamma * 2.0
            const tickPrime = 2.0;
            const tickRest = gamma * tickPrime;
            const tickX = gamma * beta * tickPrime;

            const ptTick = transform(0, tickPrime);
            const ptRestTick = toScreen(0, tickRest);

            // Draw tick event on moving time axis
            ctx.fillStyle = '#f43f5e';
            ctx.beginPath();
            ctx.arc(ptTick.x, ptTick.y, 6, 0, Math.PI * 2);
            ctx.fill();

            // Draw horizontal projection to rest time axis (ct)
            ctx.strokeStyle = 'rgba(244, 63, 94, 0.4)';
            ctx.lineWidth = 1;
            ctx.setLineDash([3, 3]);
            ctx.beginPath();
            ctx.moveTo(ptTick.x, ptTick.y);
            ctx.lineTo(cx, ptTick.y);
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw rest frame equivalent tick point (showing it's higher on ct axis)
            ctx.fillStyle = '#10b981';
            ctx.beginPath();
            ctx.arc(cx, ptTick.y, 5, 0, Math.PI * 2);
            ctx.fill();

            ctx.fillStyle = '#f43f5e';
            ctx.fillText(`Moving Clock Tick (t' = ${tickPrime.toFixed(1)})`, ptTick.x + 10, ptTick.y - 5);
            ctx.fillStyle = '#10b981';
            ctx.fillText(`Stationary Clock time (t = ${tickRest.toFixed(2)})`, cx - 210, ptTick.y - 5);
        }

        // Draw animated observer moving through spacetime
        if (observerTime > 0 || isAnimating) {
            // Traveling observer moves along the ct' axis (x' = 0)
            // Coordinates: (x' = 0, ct' = observerTime)
            const obsPt = transform(0, observerTime);
            
            // Draw worldline segment traversed so far
            ctx.strokeStyle = '#f59e0b';
            ctx.lineWidth = 3;
            ctx.beginPath();
            const startPt = transform(0, 0);
            ctx.moveTo(startPt.x, startPt.y);
            ctx.lineTo(obsPt.x, obsPt.y);
            ctx.stroke();

            // Project current observer position to rest axes
            const restX = gamma * beta * observerTime;
            const restTime = gamma * observerTime;

            const projX = toScreen(restX, 0);
            const projT = toScreen(0, restTime);

            ctx.strokeStyle = 'rgba(245, 158, 11, 0.3)';
            ctx.lineWidth = 1;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            ctx.moveTo(obsPt.x, obsPt.y);
            ctx.lineTo(projX.x, cy); // down to x axis
            ctx.moveTo(obsPt.x, obsPt.y);
            ctx.lineTo(cx, projT.y); // left to ct axis
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw projected markers on axes
            ctx.fillStyle = '#38bdf8';
            ctx.beginPath(); ctx.arc(projX.x, cy, 4, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#10b981';
            ctx.beginPath(); ctx.arc(cx, projT.y, 4, 0, Math.PI * 2); ctx.fill();

            // Draw traveling observer dot
            ctx.fillStyle = '#fbbf24';
            ctx.beginPath();
            ctx.arc(obsPt.x, obsPt.y, 8, 0, Math.PI * 2);
            ctx.fill();
            // Glow effect
            ctx.strokeStyle = 'rgba(251, 191, 36, 0.5)';
            ctx.lineWidth = 6;
            ctx.beginPath();
            ctx.arc(obsPt.x, obsPt.y, 11, 0, Math.PI * 2);
            ctx.stroke();

            // Update readout values
            tPrimeVal.innerText = observerTime.toFixed(2);
            tVal.innerText = restTime.toFixed(2);
        }
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
