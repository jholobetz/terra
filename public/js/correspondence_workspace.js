/**
 * Classical-to-Quantum Correspondence Workspace
 * Integrates a Crank-Nicolson quantum solver and Verlet classical integrator.
 */

// Simulation settings
let activeMode = "ehrenfest"; // "ehrenfest" or "phase"
let activePotential = "harmonic"; // "harmonic", "double_well", "barrier"
let simAnimationId = null;

// Physics parameters
let hbar = 1.0;
let mass = 1.0;
let initialX = -2.5;
let initialP = 2.0;
let initialWidth = 0.5;
let potentialScale = 4.0;

// Grids
const N = 120; // Number of spatial grid points
const xMin = -6.0;
const xMax = 6.0;
const dx = (xMax - xMin) / (N - 1);
const xGrid = new Float32Array(N);
const VGrid = new Float32Array(N);

// Quantum State: complex wavefunction ψ represented as two arrays
const psiReal = new Float32Array(N);
const psiImag = new Float32Array(N);

// Classical State
let classX = initialX;
let classP = initialP;

// Canvas details
let canvas, ctx;

// Thomas algorithm helper matrices (preallocated)
const diagReal = new Float32Array(N);
const diagImag = new Float32Array(N);
const rightReal = new Float32Array(N);
const rightImag = new Float32Array(N);

// Wigner/Phase Space details
let phaseParticles = [];
const numPhaseParticles = 120;

// Slider definitions
const SLIDERS_EHRENFEST = [
    { id: "slide-hbar", label: "Planck's Constant (ℏ)", min: 0.1, max: 2.0, value: 0.8, step: 0.05, unit: "" },
    { id: "slide-mass", label: "Particle Mass (m)", min: 0.5, max: 3.0, value: 1.0, step: 0.1, unit: "" },
    { id: "slide-p0", label: "Initial Momentum (p₀)", min: -4.0, max: 4.0, value: 2.0, step: 0.2, unit: "" },
    { id: "slide-v0", label: "Potential Scale (V₀)", min: 1.0, max: 8.0, value: 4.0, step: 0.5, unit: "" }
];

const SLIDERS_PHASE = [
    { id: "slide-cat-dist", label: "Schrödinger Cat Separation", min: 1.0, max: 4.0, value: 2.5, step: 0.1, unit: "σ" },
    { id: "slide-squeeze", label: "Phase Squeezing Factor", min: 0.5, max: 2.0, value: 1.0, step: 0.05, unit: "" }
];

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("correspondence-canvas");
    ctx = canvas.getContext("2d");

    // Initialize coordinate grid
    for (let i = 0; i < N; i++) {
        xGrid[i] = xMin + i * dx;
    }

    // Set UI handlers
    setupUIHandlers();

    // Resize canvas
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initial setup
    setMode("ehrenfest");
});

function resizeCanvas() {
    if (canvas) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
}

function setupUIHandlers() {
    // Mode toggles
    document.getElementById("mode-btn-ehrenfest").addEventListener("click", () => setMode("ehrenfest"));
    document.getElementById("mode-btn-phase").addEventListener("click", () => setMode("phase"));

    // Potential toggles
    document.querySelectorAll(".pot-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".pot-btn").forEach(b => b.classList.remove("active"));
            e.target.classList.add("active");
            setPotential(e.target.getAttribute("data-pot"));
        });
    });

    // Reset button
    document.getElementById("restart-btn").addEventListener("click", () => {
        resetSimulation();
    });
}

function setMode(mode) {
    activeMode = mode;
    
    // UI elements
    document.getElementById("mode-btn-ehrenfest").classList.toggle("active", mode === "ehrenfest");
    document.getElementById("mode-btn-phase").classList.toggle("active", mode === "phase");
    
    const potSelector = document.getElementById("potential-selector-box");
    
    if (mode === "ehrenfest") {
        potSelector.style.display = "block";
        document.getElementById("active-mode-title").textContent = "Ehrenfest's Sandbox";
        document.getElementById("active-mode-description").textContent = "Visualizes classical particle trajectories alongside quantum expectation values (⟨x⟩, ⟨p⟩) to demonstrate where classical and quantum mechanics correspond.";
        
        document.getElementById("math-box-title-1").textContent = "Ehrenfest's Equations";
        document.getElementById("math-formula-1").innerHTML = `
            \\[ \\frac{d}{dt}\\langle \\hat{x} \\rangle = \\frac{\\langle \\hat{p} \\rangle}{m} \\]
            \\[ \\frac{d}{dt}\\langle \\hat{p} \\rangle = -\\langle V'(\\hat{x}) \\rangle \\]
        `;
        document.getElementById("math-desc-1").textContent = "Quantum expectation values trace classical paths exactly when the potential derivative (force) is linear. For non-linear potentials, the quantum wave packet diverges.";
        
        document.getElementById("math-box-title-2").textContent = "Classical Limit (h-bar → 0)";
        document.getElementById("math-formula-2").innerHTML = `
            \\[ \\lim_{\\hbar \\to 0} \\langle \\hat{x} \\rangle(t) = x_{\\text{class}}(t) \\]
        `;
        document.getElementById("math-desc-2").textContent = "As the effective Planck constant is reduced, quantum fluctuations decrease, and the wave packet expectation value matches the classical path.";

        renderSliders(SLIDERS_EHRENFEST);
    } else {
        potSelector.style.display = "none";
        document.getElementById("active-mode-title").textContent = "Phase Space Flows";
        document.getElementById("active-mode-description").textContent = "Compares a classical ensemble density flow (Liouville theorem) with the quantum Wigner quasi-probability distribution showing negative interference fringes.";
        
        document.getElementById("math-box-title-1").textContent = "Classical Liouville Equation";
        document.getElementById("math-formula-1").innerHTML = `
            \\[ \\frac{\\partial \\rho}{\\partial t} = -\\{\\rho, H\\} \\]
        `;
        document.getElementById("math-desc-1").textContent = "In classical phase space, probability density behaves like an incompressible fluid, conserving phase volume under Hamiltonian flow.";
        
        document.getElementById("math-box-title-2").textContent = "Quantum Wigner Flow";
        document.getElementById("math-formula-2").innerHTML = `
            \\[ \\frac{\\partial W}{\\partial t} = -\\{W, H\\}_M \\]
        `;
        document.getElementById("math-desc-2").textContent = "The Wigner function represents quantum states in phase space. The quantum Moyal brackets include h-bar corrections, leading to negative probability density regions.";

        renderSliders(SLIDERS_PHASE);
    }

    if (window.MathJax) {
        MathJax.typesetPromise();
    }

    resetSimulation();
}

function setPotential(pot) {
    activePotential = pot;
    resetSimulation();
}

function renderSliders(sliders) {
    const container = document.getElementById("sliders-container");
    container.innerHTML = "";

    sliders.forEach(slider => {
        const group = document.createElement("div");
        group.className = "control-group";
        
        group.innerHTML = `
            <label for="${slider.id}">
                ${slider.label}: <strong id="val-${slider.id}" style="color: var(--accent-quantum);">${slider.value}${slider.unit}</strong>
            </label>
            <input type="range" id="${slider.id}" min="${slider.min}" max="${slider.max}" value="${slider.value}" step="${slider.step}">
        `;
        
        container.appendChild(group);

        // Add event listener
        document.getElementById(slider.id).addEventListener("input", (e) => {
            const val = parseFloat(e.target.value);
            document.getElementById(`val-${slider.id}`).textContent = `${val}${slider.unit}`;
            
            // Sync variables
            if (slider.id === "slide-hbar") hbar = val;
            if (slider.id === "slide-mass") mass = val;
            if (slider.id === "slide-p0") {
                initialP = val;
                resetSimulation();
            }
            if (slider.id === "slide-v0") {
                potentialScale = val;
                updatePotential();
            }
        });
    });
}

function updatePotential() {
    // Recompute potential profile on grid
    const center = 0.0;
    
    for (let i = 0; i < N; i++) {
        const x = xGrid[i];
        
        if (activePotential === "harmonic") {
            // V(x) = 0.5 * k * x^2
            const k = potentialScale * 0.2;
            VGrid[i] = 0.5 * k * x * x;
        } else if (activePotential === "double_well") {
            // V(x) = v0 * (x^2 - d^2)^2
            // Let d = 2
            const d2 = 4.0;
            const factor = potentialScale * 0.02;
            VGrid[i] = factor * Math.pow(x * x - d2, 2);
        } else if (activePotential === "barrier") {
            // V(x) = v0 * exp(-x^2 / w^2)
            const w = 0.8;
            VGrid[i] = potentialScale * Math.exp(-x * x / (w * w));
        }
    }
}

// Reset quantum wave packet and classical position
function resetSimulation() {
    if (simAnimationId) {
        cancelAnimationFrame(simAnimationId);
    }

    classX = initialX;
    classP = initialP;

    // Read sliders values if present
    const hbarEl = document.getElementById("slide-hbar");
    const massEl = document.getElementById("slide-mass");
    const v0El = document.getElementById("slide-v0");
    if (hbarEl) hbar = parseFloat(hbarEl.value);
    if (massEl) mass = parseFloat(massEl.value);
    if (v0El) potentialScale = parseFloat(v0El.value);

    updatePotential();

    if (activeMode === "ehrenfest") {
        // Initialize wavefunction: Gaussian wave packet
        // ψ(x) = A * exp(-(x - x0)^2 / (4 * σ^2)) * exp(i * p0 * x / ℏ)
        const x0 = initialX;
        const p0 = initialP;
        const sigma = initialWidth;
        
        let normSq = 0.0;
        for (let i = 0; i < N; i++) {
            const x = xGrid[i];
            const envelope = Math.exp(-Math.pow(x - x0, 2) / (4.0 * sigma * sigma));
            const phase = (p0 * x) / hbar;
            
            psiReal[i] = envelope * Math.cos(phase);
            psiImag[i] = envelope * Math.sin(phase);
            
            normSq += (psiReal[i]*psiReal[i] + psiImag[i]*psiImag[i]) * dx;
        }
        
        // Normalize ψ
        const norm = Math.sqrt(normSq);
        for (let i = 0; i < N; i++) {
            psiReal[i] /= norm;
            psiImag[i] /= norm;
        }
    } else {
        // Initialize classical ensemble for Phase Space
        phaseParticles = [];
        const r = 35.0; // cloud radius
        const cx = canvas ? canvas.width / 2 : 300;
        const cy = canvas ? canvas.height / 2 : 200;
        
        for (let i = 0; i < numPhaseParticles; i++) {
            // Spawn inside a circle in phase space (x, p)
            const theta = Math.random() * Math.PI * 2;
            const dist = Math.sqrt(Math.random()) * r;
            
            // Offset coordinates to make it rotate
            phaseParticles.push({
                x: -120 + dist * Math.cos(theta),
                p: 60 + dist * Math.sin(theta)
            });
        }
    }

    simAnimationId = requestAnimationFrame(simulationLoop);
}

// Master loop
function simulationLoop() {
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (activeMode === "ehrenfest") {
        runEhrenfestEngine();
    } else {
        runPhaseSpaceEngine();
    }

    simAnimationId = requestAnimationFrame(simulationLoop);
}

// CRANK-NICOLSON SCHRÖDINGER SOLVER + VERLET INTEGRATOR
function runEhrenfestEngine() {
    // 1. Step Classical Particle (Verlet)
    // Find force: F = -dV/dx. Approximate V'(x) analytically.
    let force = 0;
    if (activePotential === "harmonic") {
        const k = potentialScale * 0.2;
        force = -k * classX;
    } else if (activePotential === "double_well") {
        const factor = potentialScale * 0.02;
        force = -4.0 * factor * classX * (classX * classX - 4.0);
    } else if (activePotential === "barrier") {
        const w = 0.8;
        force = 2.0 * potentialScale * classX * Math.exp(-classX * classX / (w * w)) / (w * w);
    }

    const dt = 0.05; // Time step
    // Velocity Verlet
    classX += (classP / mass) * dt + 0.5 * (force / mass) * dt * dt;
    
    // Recompute force at new position
    let nextForce = 0;
    if (activePotential === "harmonic") {
        const k = potentialScale * 0.2;
        nextForce = -k * classX;
    } else if (activePotential === "double_well") {
        const factor = potentialScale * 0.02;
        nextForce = -4.0 * factor * classX * (classX * classX - 4.0);
    } else if (activePotential === "barrier") {
        const w = 0.8;
        nextForce = 2.0 * potentialScale * classX * Math.exp(-classX * classX / (w * w)) / (w * w);
    }
    
    classP += 0.5 * (force + nextForce) * dt;

    // Boundary check for classical particle
    if (classX > xMax) classX = xMin;
    if (classX < xMin) classX = xMax;

    // 2. Step Quantum Wave function (Crank-Nicolson tridiagonal solver)
    solveTDSECrankNicolson(dt);

    // 3. Compute quantum expectation values
    let expX = 0.0;
    let prob = new Float32Array(N);
    for (let i = 0; i < N; i++) {
        prob[i] = psiReal[i]*psiReal[i] + psiImag[i]*psiImag[i];
        expX += xGrid[i] * prob[i] * dx;
    }

    // 4. Render everything to canvas
    renderEhrenfestCanvas(prob, expX);
}

// Crank-Nicolson Tridiagonal Equation Solver
// Solves (1 + i * dt * H / (2*hbar)) ψ^(n+1) = (1 - i * dt * H / (2*hbar)) ψ^n
function solveTDSECrankNicolson(dt) {
    const alpha = (hbar * dt) / (4.0 * mass * dx * dx); // coupling factor
    
    // Right hand side vector y = (1 - i * dt * H / (2*hbar)) ψ^n
    const yReal = new Float32Array(N);
    const yImag = new Float32Array(N);
    
    for (let j = 1; j < N - 1; j++) {
        const V_term = (dt * VGrid[j]) / (2.0 * hbar);
        
        // H ψ = -hbar^2/(2m) * d2ψ/dx2 + V ψ
        // (1 - i * dt * H / (2*hbar)) ψ_j
        // = (1 - 2i * alpha - i * V_term) ψ_j + i * alpha * (ψ_{j+1} + ψ_{j-1})
        
        const sumReal = psiReal[j+1] + psiReal[j-1];
        const sumImag = psiImag[j+1] + psiImag[j-1];
        
        yReal[j] = psiReal[j] + (2.0 * alpha + V_term) * psiImag[j] - alpha * sumImag;
        yImag[j] = psiImag[j] - (2.0 * alpha + V_term) * psiReal[j] + alpha * sumReal;
    }
    
    // Boundary conditions (infinite potential well at grid edges)
    yReal[0] = 0; yImag[0] = 0;
    yReal[N-1] = 0; yImag[N-1] = 0;

    // Tridiagonal Matrix Diagonal terms for: (1 + i * dt * H / (2*hbar))
    // Diagonal A_j = (1 + 2i * alpha + i * V_term)
    // Off-diagonals B = C = -i * alpha
    // We solve A x = y using Thomas tridiagonal algorithm adapted for complex elements.
    
    // Thomas forward sweep
    const eReal = new Float32Array(N);
    const eImag = new Float32Array(N);
    const fReal = new Float32Array(N);
    const fImag = new Float32Array(N);

    // Border conditions
    // A_0 = 1, f_0 = 0
    eReal[0] = 0; eImag[0] = 0;
    fReal[0] = 0; fImag[0] = 0;

    for (let j = 1; j < N - 1; j++) {
        const V_term = (dt * VGrid[j]) / (2.0 * hbar);
        
        // Complex diagonal elements
        const ajReal = 1.0;
        const ajImag = 2.0 * alpha + V_term;
        const bjReal = 0.0;
        const bjImag = -alpha; // subdiagonal
        const cjReal = 0.0;
        const cjImag = -alpha; // superdiagonal
        
        // Denominator = A_j - B * e_{j-1}
        // Let's compute complex term: term = B * e_{j-1}
        // B is purely imaginary: i*bjImag. e_{j-1} is eReal + i*eImag
        // termReal = -bjImag * eImag
        // termImag = bjImag * eReal
        const termReal = -bjImag * eImag[j-1];
        const termImag = bjImag * eReal[j-1];
        
        const denReal = ajReal - termReal;
        const denImag = ajImag - termImag;
        const denMagSq = denReal*denReal + denImag*denImag;
        
        // e_j = C_j / Denominator
        // C_j is purely imaginary: i * cjImag
        // e_j = (i * cjImag) * (denReal - i * denImag) / denMagSq
        //     = (cjImag * denImag + i * cjImag * denReal) / denMagSq
        eReal[j] = (cjImag * denImag) / denMagSq;
        eImag[j] = (cjImag * denReal) / denMagSq;
        
        // f_j = (y_j - B * f_{j-1}) / Denominator
        // term2 = B * f_{j-1} ==> term2Real = -bjImag * fImag, term2Imag = bjImag * fReal
        const term2Real = -bjImag * fImag[j-1];
        const term2Imag = bjImag * fReal[j-1];
        
        const numReal = yReal[j] - term2Real;
        const numImag = yImag[j] - term2Imag;
        
        // f_j = (numReal + i*numImag) * (denReal - i*denImag) / denMagSq
        fReal[j] = (numReal * denReal + numImag * denImag) / denMagSq;
        fImag[j] = (numImag * denReal - numReal * denImag) / denMagSq;
    }

    // Thomas backward substitution
    psiReal[N-1] = 0.0;
    psiImag[N-1] = 0.0;
    
    for (let j = N - 2; j >= 0; j--) {
        // ψ_j = f_j - e_j * ψ_{j+1}
        // term = e_j * ψ_{j+1}
        const termReal = eReal[j] * psiReal[j+1] - eImag[j] * psiImag[j+1];
        const termImag = eReal[j] * psiImag[j+1] + eImag[j] * psiReal[j+1];
        
        psiReal[j] = fReal[j] - termReal;
        psiImag[j] = fImag[j] - termImag;
    }
}

// Render Ehrenfest Sandbox Canvas
function renderEhrenfestCanvas(prob, expX) {
    const W = canvas.width;
    const H = canvas.height;
    
    // Scale mapping coordinates
    const mapX = (x) => ((x - xMin) / (xMax - xMin)) * W;
    const mapY = (y) => H * 0.7 - y * (H * 0.06);

    // 1. Draw potential barrier V(x) curve
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.fillStyle = "rgba(255,255,255,0.02)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, H * 0.7);
    for (let i = 0; i < N; i++) {
        ctx.lineTo(mapX(xGrid[i]), mapY(VGrid[i]));
    }
    ctx.lineTo(W, H * 0.7);
    ctx.lineTo(W, H);
    ctx.lineTo(0, H);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Zero ground axis
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, H * 0.7);
    ctx.lineTo(W, H * 0.7);
    ctx.stroke();

    // 2. Draw Quantum Wave packet Probability Density
    ctx.fillStyle = "rgba(255, 78, 136, 0.09)";
    ctx.strokeStyle = "#ff4e88"; // Neon Pink
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(0, H * 0.7);
    for (let i = 0; i < N; i++) {
        // scale probability density visually
        const visualHeight = prob[i] * 120.0;
        ctx.lineTo(mapX(xGrid[i]), mapY(VGrid[i] + visualHeight));
    }
    ctx.lineTo(W, H * 0.7);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // 3. Draw Classical Particle (Yellow sphere)
    // Sitting on top of classical potential landscape
    let classV = 0.0;
    if (activePotential === "harmonic") classV = 0.5 * (potentialScale * 0.2) * classX * classX;
    else if (activePotential === "double_well") classV = (potentialScale * 0.02) * Math.pow(classX*classX - 4.0, 2);
    else if (activePotential === "barrier") classV = potentialScale * Math.exp(-classX*classX / 0.64);

    const classPixelX = mapX(classX);
    const classPixelY = mapY(classV);

    ctx.fillStyle = "#ffd700"; // gold
    ctx.shadowColor = "#ffd700";
    ctx.shadowBlur = 12;
    ctx.beginPath();
    ctx.arc(classPixelX, classPixelY - 8, 8, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // 4. Draw vertical expectation markers
    // Classical position marker (dotted yellow)
    ctx.strokeStyle = "rgba(255, 215, 0, 0.4)";
    ctx.lineWidth = 1.2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(classPixelX, 0);
    ctx.lineTo(classPixelX, H * 0.7);
    ctx.stroke();
    
    // Quantum expectation value marker (dotted pink)
    ctx.strokeStyle = "rgba(255, 78, 136, 0.6)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(mapX(expX), 0);
    ctx.lineTo(mapX(expX), H * 0.7);
    ctx.stroke();
    ctx.setLineDash([]); // reset

    // Draw coordinate markers
    ctx.fillStyle = "#ffffff";
    ctx.font = "10px Space Grotesk, sans-serif";
    ctx.fillText("x_class", classPixelX - 18, H * 0.7 + 15);
    ctx.fillStyle = "#ff4e88";
    ctx.fillText("⟨x⟩_quant", mapX(expX) - 20, H * 0.7 + 28);

    // Compute divergence status
    const div = Math.abs(classX - expX);
    const statusEl = document.getElementById("coherence-status");
    if (div > 0.45) {
        statusEl.textContent = "Divergent (Quantum Decohered)";
        statusEl.className = "status-value status-divergent";
    } else {
        statusEl.textContent = "Coherent (Correspondence Lock)";
        statusEl.className = "status-value status-coherent";
    }

    // Legend
    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "11px Space Grotesk, sans-serif";
    ctx.fillText(`Classical Position (x_class): ${classX.toFixed(3)}`, 20, 30);
    ctx.fillStyle = "#ff4e88";
    ctx.fillText(`Quantum Expectation (⟨x⟩): ${expX.toFixed(3)}`, 20, 48);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Divergence Δx: ${div.toFixed(3)}`, 20, 66);
}

// 2D PHASE SPACE SIMULATION (LIOUVILLE vs WIGNER COHERENT CAT STATE)
function runPhaseSpaceEngine() {
    const W = canvas.width;
    const H = canvas.height;
    const centerX = W / 2;
    const centerY = H / 2;

    const catDistVal = parseFloat(document.getElementById("slide-cat-dist")?.value || 2.5);
    const squeezeVal = parseFloat(document.getElementById("slide-squeeze")?.value || 1.0);

    // Increment phase angles for rotation
    let timeScale = 0.02;
    let angle = simTime * timeScale;

    // 1. Draw Wigner Density Background (Quantum phase space representation)
    // We render a Schrödinger's Cat state on a grid of Wigner function:
    // W(x, p) = Coherent blobs + interference fringe in center with negative ripples.
    // Analytical representation:
    // Two coherent states located at ±catDist in x-axis, rotating around origin.
    // Interferences sit exactly at origin, aligned orthogonally to the separation axis.

    const gridSize = 40;
    const cellW = W / gridSize;
    const cellH = H / gridSize;

    // Coordinates in phase space units
    const dX = catDistVal; // Cat separation parameter
    
    // Draw heatmap
    for (let i = 0; i < gridSize; i++) {
        for (let j = 0; j < gridSize; j++) {
            // Coordinate relative to center
            const x = (i - gridSize / 2) * 0.25;
            const p = (j - gridSize / 2) * 0.25;

            // Rotating coordinates to simulate time evolution
            const xr = x * Math.cos(angle) + p * Math.sin(angle);
            const pr = -x * Math.sin(angle) + p * Math.cos(angle);

            // Left blob: centered at -dX
            const g1 = Math.exp(-Math.pow(xr + dX, 2) / squeezeVal - Math.pow(pr, 2) * squeezeVal);
            // Right blob: centered at +dX
            const g2 = Math.exp(-Math.pow(xr - dX, 2) / squeezeVal - Math.pow(pr, 2) * squeezeVal);
            
            // Interference fringe (contains negative oscillatory cos values)
            // Frequency of oscillations increases with separation dX
            const cosTerm = 2.0 * Math.exp(-Math.pow(xr, 2) / squeezeVal - Math.pow(pr, 2) * squeezeVal) * Math.cos(2.0 * pr * dX);

            const wigner = g1 + g2 + cosTerm; // Total Wigner density

            // Draw pixel cells
            if (Math.abs(wigner) > 0.05) {
                let opacity = Math.min(Math.abs(wigner) * 0.45, 0.45);
                
                if (wigner > 0) {
                    // Positive values (blue/cyan)
                    ctx.fillStyle = `rgba(0, 210, 255, ${opacity})`;
                } else {
                    // Negative values (red/pink quantum interference)
                    ctx.fillStyle = `rgba(255, 78, 136, ${opacity * 1.5})`;
                }
                ctx.fillRect(i * cellW, j * cellH, cellW + 1, cellH + 1);
            }
        }
    }

    // Axis dividers
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(W, centerY);
    ctx.moveTo(centerX, 0);
    ctx.lineTo(centerX, H);
    ctx.stroke();

    ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
    ctx.font = "11px Space Grotesk, sans-serif";
    ctx.fillText("Position (x)", W - 80, centerY + 15);
    ctx.fillText("Momentum (p)", centerX + 10, 20);

    // 2. Draw Classical Ensemble Particles (Liouville density points)
    // Classical particles rotate in circles (harmonic oscillator) in phase space.
    // They are initialized in two blobs matching the cat state density.
    ctx.fillStyle = "#ffd700"; // gold particles
    
    phaseParticles.forEach(part => {
        // Rotate particle phase coordinates
        const omega = 0.02;
        // Harmonic orbit
        const prevX = part.x;
        const prevP = part.p;
        
        part.x = prevX * Math.cos(omega) + prevP * Math.sin(omega);
        part.p = -prevX * Math.sin(omega) + prevP * Math.cos(omega);

        // Render classical dots
        ctx.beginPath();
        ctx.arc(centerX + part.x, centerY - part.p, 2, 0, Math.PI * 2);
        ctx.fill();
    });

    // Draw legend/labels
    ctx.fillStyle = "#ffd700";
    ctx.fillText("● Classical Ensemble Flow (Liouville density points)", 20, H - 45);
    ctx.fillStyle = "#00d2ff";
    ctx.fillText("■ Positive Wigner Density (Coherent state blobs)", 20, H - 30);
    ctx.fillStyle = "#ff4e88";
    ctx.fillText("■ Negative Wigner Density (Quantum interference fringes)", 20, H - 15);

    document.getElementById("coherence-status").textContent = "Non-Classical (Wigner Interference)";
    document.getElementById("coherence-status").className = "status-value status-divergent";
}
