document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Wave 1 Frequency (f₁): <span id="f1-val" class="math-value">4.0</span> Hz</label>
            <input type="range" id="f1-slider" min="1.0" max="10.0" step="0.1" value="4.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Wave 2 Frequency (f₂): <span id="f2-val" class="math-value">4.2</span> Hz</label>
            <input type="range" id="f2-slider" min="1.0" max="10.0" step="0.1" value="4.2" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Relative Phase (φ): <span id="p-val" class="math-value">0.0</span> rad</label>
            <input type="range" id="p-slider" min="0.0" max="6.28" step="0.1" value="0.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Ripple Wavelength (λ): <span id="w-val" class="math-value">22</span> px</label>
            <input type="range" id="w-slider" min="10" max="50" step="1" value="22" style="width: 100%">
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:5px;">
                • Top: 1D Wave superposition. Adjust frequencies close to each other (e.g. 4.0 & 4.2) to observe **acoustic beats**.<br>
                • Bottom: 2D Ripple Tank. Click and drag the two glowing wave source emitters to warp interference fringes.
            </div>
            <div id="beat-readout">Beat Frequency (f_beat): <span class="math-value">0.2 Hz</span></div>
        </div>
    `;

    const f1Slider = document.getElementById('f1-slider');
    const f2Slider = document.getElementById('f2-slider');
    const pSlider = document.getElementById('p-slider');
    const wSlider = document.getElementById('w-slider');
    const beatReadout = document.getElementById('beat-readout');

    let f1 = 4.0;
    let f2 = 4.2;
    let phase = 0.0;
    let lambda = 22.0; // 2D wavelength

    let time = 0.0;
    let lastTimestamp = performance.now();

    // 2D Ripple Emitter Positions
    let s1 = { x: 0, y: 0, isDragging: false }; // set in resize
    let s2 = { x: 0, y: 0, isDragging: false };

    // Off-screen canvas buffer for fast 2D ripple tank rendering (100x100 grid for performance)
    const gridW = 100;
    const gridH = 100;
    const offscreenCanvas = document.createElement('canvas');
    offscreenCanvas.width = gridW;
    offscreenCanvas.height = gridH;
    const offscreenCtx = offscreenCanvas.getContext('2d');
    const rippleImgData = offscreenCtx.createImageData(gridW, gridH);

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 550;
        
        // Position 2D ripple sources in the bottom half panel
        const tankY = (3 * canvas.height) / 4;
        s1.x = canvas.width / 3;
        s1.y = tankY;
        s2.x = (2 * canvas.width) / 3;
        s2.y = tankY;
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    f1Slider.oninput = () => { f1 = parseFloat(f1Slider.value); document.getElementById('f1-val').innerText = f1.toFixed(1); updateBeat(); };
    f2Slider.oninput = () => { f2 = parseFloat(f2Slider.value); document.getElementById('f2-val').innerText = f2.toFixed(1); updateBeat(); };
    pSlider.oninput = () => { phase = parseFloat(pSlider.value); document.getElementById('p-val').innerText = phase.toFixed(1); };
    wSlider.oninput = () => { lambda = parseFloat(wSlider.value); document.getElementById('w-val').innerText = lambda; };

    function updateBeat() {
        const beatF = Math.abs(f1 - f2);
        if (beatF === 0) {
            beatReadout.innerHTML = `Waves in unison: <span class="math-value">Coherent</span>`;
        } else {
            beatReadout.innerHTML = `Beat Frequency (f_beat): <span class="math-value">${beatF.toFixed(1)} Hz</span>`;
        }
    }
    updateBeat();

    // Mouse events for dragging sources in the 2D tank
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        
        const d1 = Math.sqrt((pos.x - s1.x) ** 2 + (pos.y - s1.y) ** 2);
        const d2 = Math.sqrt((pos.x - s2.x) ** 2 + (pos.y - s2.y) ** 2);

        if (d1 < 18) {
            s1.isDragging = true;
        } else if (d2 < 18) {
            s2.isDragging = true;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        const pos = getMousePos(e);
        const tankTop = canvas.height / 2 + 10;
        const tankBottom = canvas.height - 15;

        if (s1.isDragging) {
            s1.x = Math.max(15, Math.min(canvas.width - 15, pos.x));
            s1.y = Math.max(tankTop, Math.min(tankBottom, pos.y));
        } else if (s2.isDragging) {
            s2.x = Math.max(15, Math.min(canvas.width - 15, pos.x));
            s2.y = Math.max(tankTop, Math.min(tankBottom, pos.y));
        }
    });

    canvas.addEventListener('mouseup', () => {
        s1.isDragging = false;
        s2.isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
        s1.isDragging = false;
        s2.isDragging = false;
    });

    // Render 2D ripples on optimized off-screen buffer
    function updateRippleImage() {
        const data = rippleImgData.data;
        const tankYCenter = (3 * canvas.height) / 4;
        const tankH = canvas.height / 2;

        // Map sources to offscreen coordinates
        const scaleX = canvas.width / gridW;
        const scaleY = tankH / gridH;

        const os1 = {
            x: (s1.x / canvas.width) * gridW,
            y: ((s1.y - (canvas.height / 2)) / tankH) * gridH
        };
        const os2 = {
            x: (s2.x / canvas.width) * gridW,
            y: ((s2.y - (canvas.height / 2)) / tankH) * gridH
        };

        for (let y = 0; y < gridH; y++) {
            for (let x = 0; x < gridW; x++) {
                // Distances to sources
                const d1 = Math.sqrt((x - os1.x) ** 2 + (y - os1.y) ** 2) * scaleX;
                const d2 = Math.sqrt((x - os2.x) ** 2 + (y - os2.y) ** 2) * scaleX;

                // Wave amplitude model: A * sin(kr - wt) / sqrt(r) to show circular dampening
                const amp1 = Math.sin(2 * Math.PI * (d1 / lambda) - time) / Math.sqrt(d1 / 15 + 1);
                // Source 2 incorporates relative phase offset
                const amp2 = Math.sin(2 * Math.PI * (d2 / lambda) - time + phase) / Math.sqrt(d2 / 15 + 1);

                const sum = (amp1 + amp2) / 2.0;

                const idx = (x + y * gridW) * 4;
                const normSum = (sum + 1) / 2; // [0, 1]

                // Color map: deep indigo (troughs) -> cyan (crests)
                data[idx] = Math.floor(10 + normSum * 50);      // R
                data[idx + 1] = Math.floor(15 + normSum * 220);  // G (Cyan accent)
                data[idx + 2] = Math.floor(30 + normSum * 220);  // B
                data[idx + 3] = 255;                             // Alpha
            }
        }

        offscreenCtx.putImageData(rippleImgData, 0, 0);
    }

    // Main animation loop
    function loop(timestamp) {
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 1.0;
        lastTimestamp = timestamp;

        // Wave phase time update
        time += dt * 8; // speed of wave propagation

        // Render off-screen 2D ripple map
        updateRippleImage();

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Deep obsidian background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // ==========================================
        // TOP PANEL: 1D Wave Superposition & Beats
        // ==========================================
        const graphW = canvas.width - 40;
        const graphH = canvas.height / 2 - 60;
        const midY = 120; // centerline of 1D wave

        ctx.fillStyle = 'rgba(10, 15, 30, 0.3)';
        ctx.fillRect(10, 10, canvas.width - 20, canvas.height / 2 - 20);

        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 12px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('1D Wave Interference & Phase Superposition', 20, 25);

        // Draw flat center axis line
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(20, midY);
        ctx.lineTo(canvas.width - 20, midY);
        ctx.stroke();

        // Trace and draw 1D waves
        ctx.lineWidth = 1.2;
        const pointsWave1 = [];
        const pointsWave2 = [];
        const pointsSum = [];

        // Scale factors for plotting
        const spaceScale = 0.04;
        const plotHeight = 22; // Wave amplitude on screen

        for (let x = 20; x < canvas.width - 20; x++) {
            // Wave 1: y1 = A1 * sin(k1*x - w1*t)
            const y1 = Math.sin((x - 20) * spaceScale - time * (f1 / 4.0)) * plotHeight;
            // Wave 2: y2 = A2 * sin(k2*x - w2*t + phase)
            const y2 = Math.sin((x - 20) * spaceScale - time * (f2 / 4.0) + phase) * plotHeight;
            
            pointsWave1.push({ x, y: midY - y1 });
            pointsWave2.push({ x, y: midY - y2 });
            pointsSum.push({ x, y: midY - (y1 + y2) });
        }

        // A. Draw Wave 1 (Semi-transparent Red)
        ctx.strokeStyle = 'rgba(239, 68, 68, 0.35)';
        ctx.beginPath();
        ctx.moveTo(pointsWave1[0].x, pointsWave1[0].y);
        for (let i = 1; i < pointsWave1.length; i++) {
            ctx.lineTo(pointsWave1[i].x, pointsWave1[i].y);
        }
        ctx.stroke();

        // B. Draw Wave 2 (Semi-transparent Blue)
        ctx.strokeStyle = 'rgba(59, 130, 246, 0.35)';
        ctx.beginPath();
        ctx.moveTo(pointsWave2[0].x, pointsWave2[0].y);
        for (let i = 1; i < pointsWave2.length; i++) {
            ctx.lineTo(pointsWave2[i].x, pointsWave2[i].y);
        }
        ctx.stroke();

        // C. Draw Sum Superposition Wave (Glowing Cyan, thick)
        ctx.strokeStyle = '#22d3ee';
        ctx.lineWidth = 3;
        ctx.shadowBlur = 8;
        ctx.shadowColor = '#06b6d4';
        ctx.beginPath();
        ctx.moveTo(pointsSum[0].x, pointsSum[0].y);
        for (let i = 1; i < pointsSum.length; i++) {
            ctx.lineTo(pointsSum[i].x, pointsSum[i].y);
        }
        ctx.stroke();
        ctx.shadowBlur = 0; // reset
        ctx.lineWidth = 1; // reset

        // Labels 1D Graph
        ctx.fillStyle = 'rgba(239, 68, 68, 0.9)';
        ctx.fillText('Wave 1', 25, midY - 35);
        ctx.fillStyle = 'rgba(96, 165, 250, 0.9)';
        ctx.fillText('Wave 2', 80, midY - 35);
        ctx.fillStyle = '#22d3ee';
        ctx.fillText('Superposition (Wave 1 + Wave 2)', 140, midY - 35);

        // ==========================================
        // BOTTOM PANEL: 2D Ripple Tank
        // ==========================================
        const tankY = canvas.height / 2 + 10;
        const tankH = canvas.height / 2 - 20;

        ctx.fillStyle = 'rgba(10, 15, 30, 0.3)';
        ctx.fillRect(10, tankY, canvas.width - 20, tankH);

        // Draw lensed ripple offscreen canvas image stretched across bottom half
        ctx.drawImage(offscreenCanvas, 10, tankY, canvas.width - 20, tankH);

        // Draw Panel Label
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 12px monospace';
        ctx.fillText('2D Wave Interference Ripple Tank (60FPS)', 20, tankY + 25);

        // Draw Emitters bob sources (glowing interactive dots)
        // Source 1 (Cyan)
        ctx.fillStyle = '#22d3ee';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.shadowBlur = 12;
        ctx.shadowColor = '#22d3ee';
        ctx.beginPath();
        ctx.arc(s1.x, s1.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Source 2 (Cyan)
        ctx.shadowColor = '#22d3ee';
        ctx.beginPath();
        ctx.arc(s2.x, s2.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0; // reset

        // Label emitters
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 9px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Source 1', s1.x, s1.y - 12);
        ctx.fillText('Source 2', s2.x, s2.y - 12);

        // Draw horizontal panel dividing line
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height / 2);
        ctx.lineTo(canvas.width, canvas.height / 2);
        ctx.stroke();
    }

    // Start loop
    requestAnimationFrame(loop);
});
