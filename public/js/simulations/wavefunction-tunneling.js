document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Barrier Height (eV): <span id="v0-val" class="math-value">0.15</span></label>
            <input type="range" id="v0-slider" min="0.00" max="0.40" step="0.01" value="0.15" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Barrier Width: <span id="w-val" class="math-value">12</span> nm</label>
            <input type="range" id="w-slider" min="4" max="30" step="1" value="12" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Wave Packet Energy (k₀): <span id="k0-val" class="math-value">0.80</span></label>
            <input type="range" id="k0-slider" min="0.30" max="1.50" step="0.05" value="0.80" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="play-pause" class="btn btn-primary" style="flex: 1;">Pause</button>
            <button id="reset-sim" class="btn btn-secondary">Reset</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Transmission (T): <span id="trans-val">0.0%</span></div>
            <div>Reflection (R): <span id="refl-val">0.0%</span></div>
            <div style="font-size: 0.75rem; color: #5f6c8d; margin-top: 5px;">
                Note: Pink curve shows the real part Re(Ψ); Blue filled curve shows probability density |Ψ|².
            </div>
        </div>
    `;

    const v0Slider = document.getElementById('v0-slider');
    const wSlider = document.getElementById('w-slider');
    const k0Slider = document.getElementById('k0-slider');
    const v0Val = document.getElementById('v0-val');
    const wVal = document.getElementById('w-val');
    const k0Val = document.getElementById('k0-val');
    const playPauseBtn = document.getElementById('play-pause');
    const resetSimBtn = document.getElementById('reset-sim');
    const transVal = document.getElementById('trans-val');
    const reflVal = document.getElementById('refl-val');

    // Grid details
    const N = 300; // number of grid points
    let psiReal = new Float32Array(N);
    let psiImag = new Float32Array(N);
    let pot = new Float32Array(N);
    let damping = new Float32Array(N);

    // Physical and solver parameters
    const hbar = 1.0;
    const m = 1.0;
    const dx = 1.0;
    const dt = 0.15; // Time step (must satisfy stability dt < dx^2 / (2 * hbar / (2*m*dx^2)) )
    const C = hbar / (2.0 * m * dx * dx); // 0.5

    let V0 = 0.15;
    let barrierWidth = 12;
    let k0 = 0.80;
    let isPlaying = true;
    let initialNorm = 1.0;

    // Set up absorbing boundary damping profiles
    const boundaryWidth = 40;
    const maxDamping = 0.05;
    for (let i = 0; i < N; i++) {
        damping[i] = 1.0;
        if (i < boundaryWidth) {
            const factor = (boundaryWidth - i) / boundaryWidth;
            damping[i] = 1.0 - maxDamping * factor * factor;
        } else if (i > N - boundaryWidth) {
            const factor = (i - (N - boundaryWidth)) / boundaryWidth;
            damping[i] = 1.0 - maxDamping * factor * factor;
        }
    }

    // Set up potential barrier
    function updatePotential() {
        pot.fill(0);
        const mid = Math.floor(N / 2);
        const start = mid - Math.floor(barrierWidth / 2);
        const end = start + barrierWidth;
        for (let i = start; i < end; i++) {
            pot[i] = V0;
        }
    }

    // Initialize Gaussian Wave Packet
    function initWavePacket() {
        const x0 = 60; // Initial center of wave packet
        const sigma = 12; // Width of wave packet

        psiReal.fill(0);
        psiImag.fill(0);

        let sum = 0;
        for (let i = 0; i < N; i++) {
            const x = i;
            const envelope = Math.exp(-((x - x0) ** 2) / (4 * sigma * sigma));
            psiReal[i] = envelope * Math.cos(k0 * x);
            psiImag[i] = envelope * Math.sin(k0 * x);
            sum += psiReal[i] * psiReal[i] + psiImag[i] * psiImag[i];
        }

        // Normalize wave function
        const norm = Math.sqrt(sum);
        for (let i = 0; i < N; i++) {
            psiReal[i] /= norm;
            psiImag[i] /= norm;
        }

        // Measure initial norm on left side
        initialNorm = 0;
        const mid = Math.floor(N / 2) - 10;
        for (let i = 0; i < mid; i++) {
            initialNorm += psiReal[i] * psiReal[i] + psiImag[i] * psiImag[i];
        }
        if (initialNorm === 0) initialNorm = 1.0;
    }

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 450;
    }
    window.addEventListener('resize', resize);
    resize();

    // Sliders input handlers
    v0Slider.oninput = () => {
        V0 = parseFloat(v0Slider.value);
        v0Val.innerText = V0.toFixed(2);
        updatePotential();
    };

    wSlider.oninput = () => {
        barrierWidth = parseInt(wSlider.value);
        wVal.innerText = barrierWidth;
        updatePotential();
    };

    k0Slider.oninput = () => {
        k0 = parseFloat(k0Slider.value);
        k0Val.innerText = k0.toFixed(2);
        initWavePacket();
    };

    playPauseBtn.onclick = () => {
        isPlaying = !isPlaying;
        playPauseBtn.innerText = isPlaying ? 'Pause' : 'Resume';
        playPauseBtn.className = isPlaying ? 'btn btn-primary' : 'btn btn-secondary';
    };

    resetSimBtn.onclick = () => {
        initWavePacket();
    };

    // Initialize state
    updatePotential();
    initWavePacket();

    // Time-step updates (leapfrog scheme)
    function stepPhysics() {
        // Update real part using current imaginary part
        for (let j = 1; j < N - 1; j++) {
            const laplacianImag = psiImag[j + 1] - 2 * psiImag[j] + psiImag[j - 1];
            psiReal[j] -= dt * (-C * laplacianImag + pot[j] * psiImag[j]);
        }

        // Update imaginary part using updated real part
        for (let j = 1; j < N - 1; j++) {
            const laplacianReal = psiReal[j + 1] - 2 * psiReal[j] + psiReal[j - 1];
            psiImag[j] += dt * (-C * laplacianReal + pot[j] * psiReal[j]);
        }

        // Apply boundary dampers
        for (let j = 0; j < N; j++) {
            psiReal[j] *= damping[j];
            psiImag[j] *= damping[j];
        }
    }

    // Real-time coefficients calculation
    function calculateCoefficients() {
        const mid = Math.floor(N / 2);
        const barrierEnd = mid + Math.floor(barrierWidth / 2) + 5;
        const barrierStart = mid - Math.floor(barrierWidth / 2) - 5;

        let leftSum = 0;
        let rightSum = 0;

        for (let i = 0; i < barrierStart; i++) {
            leftSum += psiReal[i] * psiReal[i] + psiImag[i] * psiImag[i];
        }

        for (let i = barrierEnd; i < N; i++) {
            rightSum += psiReal[i] * psiReal[i] + psiImag[i] * psiImag[i];
        }

        const R = (leftSum / initialNorm) * 100;
        const T = (rightSum / initialNorm) * 100;

        reflVal.innerText = R.toFixed(1) + '%';
        transVal.innerText = T.toFixed(1) + '%';
    }

    // Render loop
    function loop() {
        if (isPlaying) {
            // Run multiple physics substeps per frame for smoother/faster simulation
            for (let step = 0; step < 4; step++) {
                stepPhysics();
            }
            calculateCoefficients();
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Clear canvas
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const margin = 50;
        const simWidth = canvas.width - 2 * margin;
        const simHeight = canvas.height - 120;
        const zeroY = canvas.height - margin - 50;

        // Draw potential barrier
        const mid = Math.floor(N / 2);
        const startIdx = mid - Math.floor(barrierWidth / 2);
        const endIdx = startIdx + barrierWidth;

        const startX = margin + (startIdx / N) * simWidth;
        const endX = margin + (endIdx / N) * simWidth;
        const barWidth = endX - startX;
        // Map potential value to visual height
        const barHeight = V0 * 700;

        if (V0 > 0) {
            // Glowing barrier block
            const grad = ctx.createLinearGradient(startX, zeroY, startX, zeroY - barHeight);
            grad.addColorStop(0, 'rgba(249, 115, 22, 0.05)');
            grad.addColorStop(1, 'rgba(249, 115, 22, 0.35)');
            ctx.fillStyle = grad;
            ctx.fillRect(startX, zeroY - barHeight, barWidth, barHeight);

            // Barrier top border line
            ctx.strokeStyle = '#f97316';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(startX, zeroY - barHeight);
            ctx.lineTo(endX, zeroY - barHeight);
            ctx.stroke();

            // Barrier vertical lines
            ctx.strokeStyle = 'rgba(249, 115, 22, 0.5)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(startX, zeroY); ctx.lineTo(startX, zeroY - barHeight);
            ctx.moveTo(endX, zeroY); ctx.lineTo(endX, zeroY - barHeight);
            ctx.stroke();
        }

        // Draw ground baseline
        ctx.strokeStyle = '#2d3748';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(margin, zeroY);
        ctx.lineTo(canvas.width - margin, zeroY);
        ctx.stroke();

        // Draw probability density |Ψ|² and real part Re(Ψ)
        const densityPoints = [];
        const realPoints = [];

        for (let i = 0; i < N; i++) {
            const x = margin + (i / N) * simWidth;
            const p2 = psiReal[i] * psiReal[i] + psiImag[i] * psiImag[i];
            const yDensity = zeroY - p2 * 1000; // scaling factor for visualization
            const yReal = zeroY - psiReal[i] * 180;

            densityPoints.push({ x, y: yDensity });
            realPoints.push({ x, y: yReal });
        }

        // 1. Draw Real Part of Wavefunction Re(Ψ) (Pink wavy line)
        ctx.strokeStyle = 'rgba(236, 72, 153, 0.6)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(realPoints[0].x, realPoints[0].y);
        for (let i = 1; i < N; i++) {
            ctx.lineTo(realPoints[i].x, realPoints[i].y);
        }
        ctx.stroke();

        // 2. Draw Probability Density |Ψ|² (Filled glowing cyan curve)
        ctx.fillStyle = 'rgba(6, 182, 212, 0.2)';
        ctx.beginPath();
        ctx.moveTo(densityPoints[0].x, zeroY);
        for (let i = 0; i < N; i++) {
            ctx.lineTo(densityPoints[i].x, densityPoints[i].y);
        }
        ctx.lineTo(densityPoints[N - 1].x, zeroY);
        ctx.closePath();
        ctx.fill();

        ctx.strokeStyle = '#06b6d4';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(densityPoints[0].x, densityPoints[0].y);
        for (let i = 1; i < N; i++) {
            ctx.lineTo(densityPoints[i].x, densityPoints[i].y);
        }
        ctx.stroke();

        // Draw Damping boundaries zones (shaded dark grey/blue on edges)
        ctx.fillStyle = 'rgba(15, 23, 42, 0.5)';
        const dWidthScreen = (boundaryWidth / N) * simWidth;
        ctx.fillRect(margin, 0, dWidthScreen, canvas.height);
        ctx.fillRect(canvas.width - margin - dWidthScreen, 0, dWidthScreen, canvas.height);

        // Labels
        ctx.fillStyle = '#64748b';
        ctx.font = '12px monospace';
        ctx.fillText('Absorber Zone', margin + 10, zeroY + 30);
        ctx.fillText('Absorber Zone', canvas.width - margin - dWidthScreen + 10, zeroY + 30);
        ctx.fillText('Classical Energy Barrier V(x)', startX - 45, zeroY - barHeight - 10);
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
