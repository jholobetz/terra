document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Simulation Mode:</label><br>
            <select id="sim-mode" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="chsh">CHSH Auto Sweep (Inequality Test)</option>
                <option value="interactive">Manual Dials (Plot Correlation)</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Physical Theory Model:</label><br>
            <select id="theory-model" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="quantum">Quantum Entanglement (Singlet State)</option>
                <option value="classical">Local Realism (Local Hidden Variables)</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Measurement Rate (Speed):</label><br>
            <input type="range" id="speed-slider" min="1" max="120" step="1" value="25" style="width: 100%">
        </div>
        <div class="control-group" id="manual-controls" style="margin-top: 10px; display: none;">
            <label>Alice Angle (a): <span id="angle-a-val" class="math-value">0°</span></label>
            <input type="range" id="angle-a-slider" min="0" max="180" step="5" value="0" style="width: 100%">
            <label style="margin-top: 8px; display: block;">Bob Angle (b): <span id="angle-b-val" class="math-value">22°</span></label>
            <input type="range" id="angle-b-slider" min="0" max="180" step="5" value="22" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="reset-sim" class="btn btn-secondary" style="width: 100%">Reset Statistics</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>CHSH Sum (S): <span id="chsh-val" class="math-value" style="font-size: 1.25rem; font-weight: bold; color: #fbbf24;">0.00</span></div>
            <div style="font-size: 0.75rem; color: #5f6c8d; margin-top: 8px;">
                • CHSH Auto Sweep measures correlations across 4 angle pairs: (a,b), (a,b'), (a',b), and (a',b').<br>
                • Classical limit: |S| ≤ 2. Quantum limit: |S| ≤ 2.82 (Tsirelson Bound).
            </div>
        </div>
    `;

    const simModeSelect = document.getElementById('sim-mode');
    const theoryModelSelect = document.getElementById('theory-model');
    const speedSlider = document.getElementById('speed-slider');
    const angleASlider = document.getElementById('angle-a-slider');
    const angleBSlider = document.getElementById('angle-b-slider');
    const angleAVal = document.getElementById('angle-a-val');
    const angleBVal = document.getElementById('angle-b-val');
    const manualControls = document.getElementById('manual-controls');
    const chshVal = document.getElementById('chsh-val');
    const resetSimBtn = document.getElementById('reset-sim');

    // Detections & Statistics states
    let mode = 'chsh';
    let model = 'quantum';
    let rate = 25; // updates/measurements per second
    
    // Detector Angles (Degrees)
    let thetaA = 0;
    let thetaB = 22.5;

    // CHSH Sweep Configuration
    // standard maximum violation angles
    const chshAngles = {
        a: 0,
        a_prime: 45,
        b: 22.5,
        b_prime: 67.5
    };
    let activeSweepIndex = 0; // 0: (a,b), 1: (a,b'), 2: (a',b), 3: (a',b')
    let sweepSamples = 120; // number of samples per setting
    
    // Coincidence counters
    // index maps to sweep settings
    let coincidences = [
        { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 }, // (a, b)
        { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 }, // (a, b')
        { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 }, // (a', b)
        { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 }  // (a', b')
    ];

    // Interactive Mode Correlation Map
    let interactiveCoinc = { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 };
    let plottedPoints = []; // list of { diffAngle, correlation }

    // Photon animation states
    let photons = [];
    let AliceLED = { val: 0, timer: 0 }; // 0: off, 1: +, -1: -
    let BobLED = { val: 0, timer: 0 };
    let photonTimer = 0;
    let lastTimestamp = performance.now();

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 450;
        initStats();
    }
    window.addEventListener('resize', resize);
    resize();

    // Initialize statistics
    function initStats() {
        coincidences = [
            { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 },
            { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 },
            { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 },
            { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 }
        ];
        interactiveCoinc = { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 };
        plottedPoints = [];
        activeSweepIndex = 0;
        photons = [];
        chshVal.innerText = '0.00';
    }

    // UI Listeners
    simModeSelect.onchange = () => {
        mode = simModeSelect.value;
        if (mode === 'interactive') {
            manualControls.style.display = 'block';
            initStats();
        } else {
            manualControls.style.display = 'none';
            initStats();
        }
    };

    theoryModelSelect.onchange = () => {
        model = theoryModelSelect.value;
        initStats();
    };

    speedSlider.oninput = () => {
        rate = parseInt(speedSlider.value);
    };

    angleASlider.oninput = () => {
        thetaA = parseFloat(angleASlider.value);
        angleAVal.innerText = thetaA + '°';
        // reset interactive counts on angle change
        interactiveCoinc = { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 };
    };

    angleBSlider.oninput = () => {
        thetaB = parseFloat(angleBSlider.value);
        angleBVal.innerText = thetaB + '°';
        // reset interactive counts on angle change
        interactiveCoinc = { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 };
    };

    resetSimBtn.onclick = initStats;

    // Simulate Quantum singlet state measurements
    function simulateMeasurement(angA, angB) {
        // Convert to Radians
        const radA = (angA * Math.PI) / 180;
        const radB = (angB * Math.PI) / 180;

        let resA, resB;

        if (model === 'quantum') {
            // Quantum entanglement model ( singlet state |Ψ⁻> )
            // Alice's result is random (+1 or -1)
            resA = Math.random() < 0.5 ? 1 : -1;

            // Bob's result is determined by projection onto Alice's collapsed state
            // P(Bob = Alice) = sin^2(A - B), P(Bob != Alice) = cos^2(A - B)
            const diff = radA - radB;
            const probSame = Math.sin(diff) * Math.sin(diff);

            if (Math.random() < probSame) {
                resB = resA;
            } else {
                resB = -resA;
            }
        } else {
            // Local Realism (Classical Local Hidden Variable Model)
            // Einstein's complete model: photon pairs carry a shared hidden polarization angle lambda
            const lambda = Math.random() * Math.PI; // Hidden variable

            // Deterministic local detection based on polarimeter projection
            resA = Math.cos(2 * (radA - lambda)) >= 0 ? 1 : -1;
            resB = - (Math.cos(2 * (radB - lambda)) >= 0 ? 1 : -1); // opposite sign due to singlet analog
        }

        return { resA, resB };
    }

    // Accumulate trial statistic data
    function registerTrial(resA, resB, angA, angB) {
        // Trigger LED flashes
        AliceLED.val = resA;
        AliceLED.timer = 12;
        BobLED.val = resB;
        BobLED.timer = 12;

        if (mode === 'chsh') {
            // CHSH auto sweep statistics
            const coinc = coincidences[activeSweepIndex];
            if (resA === 1 && resB === 1) coinc.pp++;
            else if (resA === 1 && resB === -1) coinc.pm++;
            else if (resA === -1 && resB === 1) coinc.mp++;
            else if (resA === -1 && resB === -1) coinc.mm++;
            coinc.total++;

            // Cycle sweep index when sample depth is reached
            if (coinc.total >= sweepSamples) {
                activeSweepIndex = (activeSweepIndex + 1) % 4;
                // clear next index to start fresh sweep
                coincidences[activeSweepIndex] = { pp: 0, pm: 0, mp: 0, mm: 0, total: 0 };
            }

            // Calculate running CHSH Sum (S)
            calculateCHSH();
        } else {
            // Manual interactive mode statistics
            const coinc = interactiveCoinc;
            if (resA === 1 && resB === 1) coinc.pp++;
            else if (resA === 1 && resB === -1) coinc.pm++;
            else if (resA === -1 && resB === 1) coinc.mp++;
            else if (resA === -1 && resB === -1) coinc.mm++;
            coinc.total++;

            // Periodically plot current measurements to the correlation map
            if (coinc.total > 20 && coinc.total % 10 === 0) {
                const E = (coinc.pp + coinc.mm - coinc.pm - coinc.mp) / coinc.total;
                const diffAngle = Math.abs(angA - angB);
                
                // Add or update plotted point
                let found = false;
                for (let pt of plottedPoints) {
                    if (Math.abs(pt.diffAngle - diffAngle) < 1.0) {
                        pt.correlation = E; // update
                        found = true;
                        break;
                    }
                }
                if (!found) {
                    plottedPoints.push({ diffAngle, correlation: E });
                }
            }
        }
    }

    // Calculates CHSH Sum S = E(a,b) - E(a,b') + E(a',b) + E(a',b')
    function calculateCHSH() {
        const getE = (c) => {
            if (c.total === 0) return 0;
            return (c.pp + c.mm - c.pm - c.mp) / c.total;
        };

        const E0 = getE(coincidences[0]); // E(a, b)
        const E1 = getE(coincidences[1]); // E(a, b')
        const E2 = getE(coincidences[2]); // E(a', b)
        const E3 = getE(coincidences[3]); // E(a', b')

        const S = E0 - E1 + E2 + E3;
        chshVal.innerText = S.toFixed(3);
    }

    // Main animation and physics tick
    function loop(timestamp) {
        const dt = (timestamp - lastTimestamp) / 1000;
        lastTimestamp = timestamp;

        // Photon generation timer
        photonTimer += dt;
        const interval = 1.0 / rate;

        if (photonTimer >= interval) {
            photonTimer = 0;

            // Resolve target angles based on mode
            let angA, angB;
            if (mode === 'chsh') {
                if (activeSweepIndex === 0) { angA = chshAngles.a; angB = chshAngles.b; }
                else if (activeSweepIndex === 1) { angA = chshAngles.a; angB = chshAngles.b_prime; }
                else if (activeSweepIndex === 2) { angA = chshAngles.a_prime; angB = chshAngles.b; }
                else if (activeSweepIndex === 3) { angA = chshAngles.a_prime; angB = chshAngles.b_prime; }
            } else {
                angA = thetaA;
                angB = thetaB;
            }

            // Simulate the quantum/classical measurement outcome
            const outcome = simulateMeasurement(angA, angB);

            // Spawn visual photon wave packets flying outwards
            const cx = canvas.width / 4;
            const cy = canvas.height / 2;
            
            photons.push({
                x1: cx, y1: cy, vx1: -5.5, // Alice left bound
                x2: cx, y2: cy, vx2: 5.5,  // Bob right bound
                angA: angA, angB: angB,
                resA: outcome.resA, resB: outcome.resB,
                phase: 0
            });
        }

        // Animate flying photons
        const cx = canvas.width / 4;
        const aliceX = 60;
        const bobX = canvas.width / 2 - 60;

        for (let i = photons.length - 1; i >= 0; i--) {
            const p = photons[i];
            p.x1 += p.vx1;
            p.x2 += p.vx2;
            p.phase += 0.2;

            // Check hit Alice polarimeter
            if (p.x1 <= aliceX) {
                registerTrial(p.resA, p.resB, p.angA, p.angB);
                photons.splice(i, 1);
            }
        }

        // LEDs timers
        if (AliceLED.timer > 0) AliceLED.timer--;
        if (BobLED.timer > 0) BobLED.timer--;

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Deep space background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cxLeft = canvas.width / 4;
        const cyLeft = canvas.height / 2;
        const cxRight = (3 * canvas.width) / 4;
        const cyRight = canvas.height / 2;

        const aliceX = 60;
        const bobX = canvas.width / 2 - 60;

        // ==========================================
        // LEFT PANEL: EPR Entangled Source & Detectors
        // ==========================================
        ctx.fillStyle = 'rgba(10, 15, 30, 0.3)';
        ctx.fillRect(0, 0, canvas.width / 2, canvas.height);

        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 13px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('EPR Entanglement Source (Singlet State)', 15, 25);

        // Draw Alice & Bob polarimeters (Dials)
        // Alice polarimeter (Left)
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 3;
        ctx.fillStyle = 'rgba(15, 23, 42, 0.6)';
        ctx.beginPath(); ctx.arc(aliceX, cyLeft, 32, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        
        // Bob polarimeter (Right)
        ctx.beginPath(); ctx.arc(bobX, cyLeft, 32, 0, Math.PI * 2); ctx.fill(); ctx.stroke();

        // Draw indicator needles/arrows matching active angles
        let activeAngA, activeAngB;
        if (mode === 'chsh') {
            if (activeSweepIndex === 0) { activeAngA = chshAngles.a; activeAngB = chshAngles.b; }
            else if (activeSweepIndex === 1) { activeAngA = chshAngles.a; activeAngB = chshAngles.b_prime; }
            else if (activeSweepIndex === 2) { activeAngA = chshAngles.a_prime; activeAngB = chshAngles.b; }
            else if (activeSweepIndex === 3) { activeAngA = chshAngles.a_prime; activeAngB = chshAngles.b_prime; }
        } else {
            activeAngA = thetaA;
            activeAngB = thetaB;
        }

        // Draw needle Alice
        const radA = (activeAngA * Math.PI) / 180;
        ctx.strokeStyle = '#ef4444'; // Red Alice needle
        ctx.lineWidth = 2.5;
        ctx.beginPath();
        ctx.moveTo(aliceX - 25 * Math.cos(radA), cyLeft - 25 * Math.sin(radA));
        ctx.lineTo(aliceX + 25 * Math.cos(radA), cyLeft + 25 * Math.sin(radA));
        ctx.stroke();

        // Draw needle Bob
        const radB = (activeAngB * Math.PI) / 180;
        ctx.strokeStyle = '#3b82f6'; // Blue Bob needle
        ctx.beginPath();
        ctx.moveTo(bobX - 25 * Math.cos(radB), cyLeft - 25 * Math.sin(radB));
        ctx.lineTo(bobX + 25 * Math.cos(radB), cyLeft + 25 * Math.sin(radB));
        ctx.stroke();

        // Labels polarimeters
        ctx.fillStyle = '#ef4444';
        ctx.font = 'bold 10px monospace';
        ctx.textAlign = 'center';
        ctx.fillText(`Alice (a = ${activeAngA}°)`, aliceX, cyLeft - 40);

        ctx.fillStyle = '#3b82f6';
        ctx.fillText(`Bob (b = ${activeAngB}°)`, bobX, cyLeft - 40);

        // Draw Alice & Bob detection LED flashes (+/- indicator)
        // Alice LED
        if (AliceLED.timer > 0) {
            ctx.fillStyle = AliceLED.val === 1 ? '#22c55e' : '#ef4444'; // green (+1) vs red (-1)
            ctx.shadowBlur = 12;
            ctx.shadowColor = ctx.fillStyle;
            ctx.beginPath(); ctx.arc(aliceX, cyLeft + 52, 7, 0, Math.PI * 2); ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText(AliceLED.val === 1 ? '+' : '−', aliceX, cyLeft + 55);
        } else {
            ctx.fillStyle = '#1e293b';
            ctx.beginPath(); ctx.arc(aliceX, cyLeft + 52, 6, 0, Math.PI * 2); ctx.fill();
        }

        // Bob LED
        if (BobLED.timer > 0) {
            ctx.fillStyle = BobLED.val === 1 ? '#22c55e' : '#ef4444';
            ctx.shadowBlur = 12;
            ctx.shadowColor = ctx.fillStyle;
            ctx.beginPath(); ctx.arc(bobX, cyLeft + 52, 7, 0, Math.PI * 2); ctx.fill();
            ctx.shadowBlur = 0;
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 9px sans-serif';
            ctx.fillText(BobLED.val === 1 ? '+' : '−', bobX, cyLeft + 55);
        } else {
            ctx.fillStyle = '#1e293b';
            ctx.beginPath(); ctx.arc(bobX, cyLeft + 52, 6, 0, Math.PI * 2); ctx.fill();
        }

        // Draw Entangled Source crystal (glowing central octagon)
        ctx.fillStyle = 'rgba(168, 85, 247, 0.2)';
        ctx.strokeStyle = '#a855f7';
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#a855f7';
        ctx.beginPath();
        for (let i = 0; i < 8; i++) {
            const angle = (i * Math.PI) / 4;
            const sx = cxLeft + 15 * Math.cos(angle);
            const sy = cyLeft + 15 * Math.sin(angle);
            if (i === 0) ctx.moveTo(sx, sy);
            else ctx.lineTo(sx, sy);
        }
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
        ctx.shadowBlur = 0; // reset

        ctx.fillStyle = '#a855f7';
        ctx.font = '8px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Source', cxLeft, cyLeft + 25);

        // Draw flying photon wave packets (cyan glowing wave envelopes)
        for (let p of photons) {
            // Draw left-traveling photon
            drawWavePacket(p.x1, cyLeft, p.phase);
            // Draw right-traveling photon
            drawWavePacket(p.x2, cyLeft, p.phase);
        }

        function drawWavePacket(px, py, phase) {
            ctx.strokeStyle = 'rgba(34, 211, 238, 0.8)'; // cyan wave
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            const width = 16;
            for (let ox = -width; ox <= width; ox += 1) {
                // Gaussian envelope multiplier
                const envelope = Math.exp(-(ox * ox) / (2 * 5 * 5));
                const wx = px + ox;
                const wy = py + Math.sin(ox * 0.8 - phase) * 8 * envelope;
                if (ox === -width) ctx.moveTo(wx, wy);
                else ctx.lineTo(wx, wy);
            }
            ctx.stroke();
        }

        // ==========================================
        // RIGHT PANEL: CHSH Sum and Correlation Map
        // ==========================================
        ctx.fillStyle = 'rgba(5, 7, 15, 0.5)';
        ctx.fillRect(canvas.width / 2, 0, canvas.width / 2, canvas.height);

        // Label Panel
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 13px monospace';
        ctx.textAlign = 'left';
        ctx.fillText(mode === 'chsh' ? 'CHSH Inequality Bar Chart' : 'Entanglement Correlation Map E(Δθ)', canvas.width / 2 + 15, 25);

        if (mode === 'chsh') {
            // RENDER: CHSH Bar Chart
            const chartX = canvas.width / 2 + 30;
            const chartY = 60;
            const chartW = canvas.width / 2 - 60;
            const chartH = canvas.height - 100;

            // Draw chart background box
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(chartX, chartY, chartW, chartH);
            ctx.strokeStyle = '#334155';
            ctx.strokeRect(chartX, chartY, chartW, chartH);

            // Draw axis line (S = 0)
            const zeroY = chartY + chartH / 2;
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(chartX, zeroY);
            ctx.lineTo(chartX + chartW, zeroY);
            ctx.stroke();

            // Draw running S bar value
            const S_val = parseFloat(chshVal.innerText) || 0;
            // Map S from [-3.0, 3.0] to visual height
            const maxS = 3.0;
            const barH = (S_val / maxS) * (chartH / 2);
            
            // Choose color based on whether classical limit is breached (|S| > 2)
            ctx.fillStyle = Math.abs(S_val) > 2.001 ? '#fbbf24' : '#10b981'; // gold (violating) vs green (normal)
            ctx.fillRect(chartX + chartW / 2 - 25, zeroY, 50, -barH); // negative height draws UP

            // Draw Classical Limit Lines (|S| = 2) in red
            const classicalYTop = zeroY - (2.0 / maxS) * (chartH / 2);
            const classicalYBot = zeroY + (2.0 / maxS) * (chartH / 2);

            ctx.strokeStyle = '#ef4444'; // red classical limit line
            ctx.lineWidth = 1.5;
            ctx.setLineDash([5, 3]);
            ctx.beginPath();
            ctx.moveTo(chartX, classicalYTop); ctx.lineTo(chartX + chartW, classicalYTop);
            ctx.moveTo(chartX, classicalYBot); ctx.lineTo(chartX + chartW, classicalYBot);
            ctx.stroke();
            ctx.setLineDash([]);

            // Draw Tsirelson quantum limit line (|S| = 2.828) in gold
            const quantumYTop = zeroY - (2.828 / maxS) * (chartH / 2);
            ctx.strokeStyle = '#f59e0b'; // gold quantum bound
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(chartX, quantumYTop); ctx.lineTo(chartX + chartW, quantumYTop);
            ctx.stroke();

            // Labels for limit lines
            ctx.fillStyle = '#ef4444';
            ctx.font = '9px monospace';
            ctx.textAlign = 'right';
            ctx.fillText('Classical Limit (|S| = 2)', chartX + chartW - 10, classicalYTop - 5);
            ctx.fillStyle = '#f59e0b';
            ctx.fillText('Tsirelson Bound (2.83)', chartX + chartW - 10, quantumYTop - 5);

            // Display running correlations readouts
            ctx.fillStyle = '#94a3b8';
            ctx.font = '10px monospace';
            ctx.textAlign = 'left';
            const getE = (i) => {
                const c = coincidences[i];
                return c.total === 0 ? 0 : (c.pp + c.mm - c.pm - c.mp) / c.total;
            };
            ctx.fillText(`E(a, b)   = ${getE(0).toFixed(2)}`, chartX + 15, chartY + 20);
            ctx.fillText(`E(a, b')  = ${getE(1).toFixed(2)}`, chartX + 15, chartY + 35);
            ctx.fillText(`E(a', b)  = ${getE(2).toFixed(2)}`, chartX + 15, chartY + 50);
            ctx.fillText(`E(a', b') = ${getE(3).toFixed(2)}`, chartX + 15, chartY + 65);

            // Sweep indicator highlight
            ctx.strokeStyle = '#a855f7';
            ctx.lineWidth = 1.5;
            ctx.strokeRect(chartX + 8, chartY + 8 + activeSweepIndex * 15, 110, 15);
        } else {
            // RENDER: Interactive Correlation map E(Δθ) vs Δθ
            const graphX = canvas.width / 2 + 40;
            const graphY = 60;
            const graphW = canvas.width / 2 - 70;
            const graphH = canvas.height - 110;

            // Draw graph background
            ctx.fillStyle = '#0f172a';
            ctx.fillRect(graphX, graphY, graphW, graphH);
            ctx.strokeStyle = '#334155';
            ctx.strokeRect(graphX, graphY, graphW, graphH);

            // Draw axis
            ctx.strokeStyle = '#475569';
            ctx.lineWidth = 1;
            ctx.beginPath();
            // Y-axis (correlation from -1 to 1)
            ctx.moveTo(graphX + 10, graphY + 5);
            ctx.lineTo(graphX + 10, graphY + graphH - 10);
            // X-axis (angle difference from 0 to 90 degrees)
            ctx.moveTo(graphX + 10, graphY + graphH / 2);
            ctx.lineTo(graphX + graphW - 5, graphY + graphH / 2);
            ctx.stroke();

            // Label axes
            ctx.fillStyle = '#64748b';
            ctx.font = '9px monospace';
            ctx.textAlign = 'right';
            ctx.fillText('+1', graphX + 8, graphY + 12);
            ctx.fillText('0', graphX + 8, graphY + graphH / 2 + 4);
            ctx.fillText('-1', graphX + 8, graphY + graphH - 10);
            ctx.textAlign = 'center';
            ctx.fillText('Angle Difference Δθ (deg)', graphX + graphW / 2, graphY + graphH + 15);

            // Draw Theoretical Curves
            // 1. Quantum Curve E = -cos(2Δθ) (purple dashed)
            ctx.strokeStyle = 'rgba(168, 85, 247, 0.45)';
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            for (let deg = 0; deg <= 90; deg += 2) {
                const gx = graphX + 10 + (deg / 90) * (graphW - 20);
                const rad = (deg * Math.PI) / 180;
                // Singlet correlation: E = -cos(2Δθ)
                const E_q = -Math.cos(2 * rad);
                const gy = graphY + graphH / 2 - E_q * (graphH / 2 - 15);
                if (deg === 0) ctx.moveTo(gx, gy);
                else ctx.lineTo(gx, gy);
            }
            ctx.stroke();

            // 2. Classical local realist curve (slate dashed straight lines)
            ctx.strokeStyle = 'rgba(100, 116, 139, 0.4)';
            ctx.beginPath();
            // Connects (0,-1) -> (45,0) -> (90,1)
            const x0 = graphX + 10;
            const y0 = graphY + graphH - 15;
            const x45 = graphX + 10 + (45 / 90) * (graphW - 20);
            const y45 = graphY + graphH / 2;
            const x90 = graphX + 10 + (90 / 90) * (graphW - 20);
            const y90 = graphY + 15;

            ctx.moveTo(x0, y0);
            ctx.lineTo(x45, y45);
            ctx.lineTo(x90, y90);
            ctx.stroke();
            ctx.setLineDash([]); // reset

            // Labels graph curves
            ctx.fillStyle = 'rgba(168, 85, 247, 0.8)';
            ctx.fillText('Quantum Theory', graphX + 60, graphY + 20);
            ctx.fillStyle = 'rgba(100, 116, 139, 0.8)';
            ctx.fillText('Local Realism Limit', graphX + 60, graphY + 35);

            // Draw experimentally plotted data points
            ctx.fillStyle = '#fbbf24'; // Amber dots
            for (let pt of plottedPoints) {
                const deg = pt.diffAngle % 90; // wrap to 90 degrees quadrant
                const gx = graphX + 10 + (deg / 90) * (graphW - 20);
                const gy = graphY + graphH / 2 - pt.correlation * (graphH / 2 - 15);
                
                ctx.beginPath();
                ctx.arc(gx, gy, 4, 0, Math.PI * 2);
                ctx.fill();
            }

            // Draw current active measurement indicator dot (pulsing halo)
            const currentDiff = Math.abs(activeAngA - activeAngB) % 90;
            const curGx = graphX + 10 + (currentDiff / 90) * (graphW - 20);
            const curCoinc = interactiveCoinc;
            const curE = curCoinc.total > 0 ? (curCoinc.pp + curCoinc.mm - curCoinc.pm - curCoinc.mp) / curCoinc.total : 0;
            const curGy = graphY + graphH / 2 - curE * (graphH / 2 - 15);

            ctx.strokeStyle = '#fbbf24';
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.arc(curGx, curGy, 7, 0, Math.PI * 2);
            ctx.stroke();
            
            ctx.fillStyle = '#fbbf24';
            ctx.beginPath();
            ctx.arc(curGx, curGy, 4, 0, Math.PI * 2);
            ctx.fill();
        }

        // Draw middle separator line
        ctx.strokeStyle = '#1e293b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 0);
        ctx.lineTo(canvas.width / 2, canvas.height);
        ctx.stroke();
    }

    // Start simulation loop
    requestAnimationFrame(loop);
});
