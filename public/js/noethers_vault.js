/**
 * Noether's Vault - Symmetry & Conservation Mappings
 * Interactive physics sandbox demonstrating Noether's Theorem.
 */

const SYMMETRIES = [
    {
        id: "time_translation",
        title: "Time Translation Invariance",
        category: "Spacetime Symmetry",
        description: "The laws of physics do not change from one moment to the next. Invariance under translations in time leads directly to the conservation of energy.",
        generator: "H = iℏ ∂_t",
        coordinateShift: "t \\to t + \\epsilon",
        conservedCurrent: "T^{\\mu 0} \\quad \\text{(Energy Flux Tensor component)}",
        conservationLaw: "\\partial_\\mu T^{\\mu 0} = 0 \\quad \\text{(Energy Conservation)}",
        accentColor: "#10b981", // emerald
        themeBgColor: "rgba(16, 185, 129, 0.08)",
        themeBorderColor: "rgba(16, 185, 129, 0.35)",
        derivationDesc: "Consider a Lagrangian density \\(\\mathcal{L}(\\phi, \\partial_\\mu \\phi)\\) with no explicit dependence on time (\\(\\partial_0 \\mathcal{L} = 0\\)). The change under an infinitesimal time translation \\(t \\to t + \\epsilon\\) yields the conservation of the canonical energy-momentum tensor's temporal component, representing energy conservation.",
        derivationSteps: [
            "\\delta x^0 = \\epsilon \\implies \\delta \\phi = \\epsilon \\partial_0 \\phi \\quad \\text{and} \\quad \\delta \\mathcal{L} = \\epsilon \\partial_0 \\mathcal{L}",
            "\\text{Noether Current: } J^\\mu = \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\delta \\phi - \\eta^{\\mu 0} \\epsilon \\mathcal{L}",
            "\\text{Define Energy-Momentum: } T^{\\mu 0} = \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\partial^0 \\phi - \\eta^{\\mu 0} \\mathcal{L}",
            "\\text{Euler-Lagrange yields: } \\partial_\\mu T^{\\mu 0} = 0 \\implies \\frac{dE}{dt} = 0"
        ],
        sliders: [
            {
                id: "break_time_symmetry",
                label: "Break Time Symmetry (Vary Potential)",
                min: 0,
                max: 100,
                value: 0,
                step: 1,
                unit: "%",
                description: "Varies gravity periodically: g(t) = g_0 * (1 + A * sin(ωt))."
            }
        ]
    },
    {
        id: "space_translation",
        title: "Spatial Translation Invariance",
        category: "Spacetime Symmetry",
        description: "The laws of physics are homogeneous; they do not depend on where in space they are evaluated. This spatial homogeneity yields the conservation of linear momentum.",
        generator: "p = -iℏ ∇",
        coordinateShift: "\\mathbf{r} \\to \\mathbf{r} + \\boldsymbol{\\epsilon}",
        conservedCurrent: "T^{\\mu i} \\quad \\text{(Momentum Flux Tensor components)}",
        conservationLaw: "\\partial_\\mu T^{\\mu i} = 0 \\quad \\text{(Momentum Conservation)}",
        accentColor: "#00d2ff", // bright blue
        themeBgColor: "rgba(0, 210, 255, 0.08)",
        themeBorderColor: "rgba(0, 210, 255, 0.35)",
        derivationDesc: "Invariance of the action under spatial translations \\(x^i \\to x^i + \\epsilon^i\\) implies that the Lagrangian has no explicit space dependence. The corresponding conserved currents correspond to the spatial columns of the stress-energy tensor, proving linear momentum conservation.",
        derivationSteps: [
            "\\delta x^i = \\epsilon^i \\implies \\delta \\phi = \\epsilon^i \\partial_i \\phi \\quad \\text{and} \\quad \\delta \\mathcal{L} = \\epsilon^i \\partial_i \\mathcal{L}",
            "J^\\mu_i = \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\partial_i \\phi - \\delta^\\mu_i \\mathcal{L} \\equiv T^\\mu_{\\,\\,i}",
            "\\text{Vanishing divergence: } \\partial_\\mu T^\\mu_{\\,\\,i} = 0 \\implies \\frac{d\\mathbf{P}}{dt} = 0"
        ],
        sliders: [
            {
                id: "break_space_symmetry",
                label: "Break Space Homogeneity (Add Hills)",
                min: 0,
                max: 100,
                value: 0,
                step: 1,
                unit: "%",
                description: "Introduces sinusoidal potential barriers along the particle's path."
            }
        ]
    },
    {
        id: "space_rotation",
        title: "Spatial Rotation Invariance",
        category: "Spacetime Symmetry",
        description: "Space is isotropic; there is no preferred direction in the universe. Invariance under coordinate rotations yields conservation of angular momentum.",
        generator: "J = \\mathbf{r} \\times \\mathbf{p}",
        coordinateShift: "\\theta \\to \\theta + \\epsilon",
        conservedCurrent: "M^{\\mu\\nu\\lambda} \\quad \\text{(Angular Momentum current tensor)}",
        conservationLaw: "\\partial_\\mu M^{\\mu\\nu\\lambda} = 0 \\quad \\text{(Angular Momentum Conservation)}",
        accentColor: "#8b5cf6", // violet
        themeBgColor: "rgba(139, 92, 246, 0.08)",
        themeBorderColor: "rgba(139, 92, 246, 0.35)",
        derivationDesc: "Applying an infinitesimal rotation \\(x^i \\to x^i + \\epsilon^i_{\\,\\,j} x^j\\) to the system coordinates. If the Lagrangian is invariant under rotations (isotropy), it results in a conserved antisymmetric current tensor, which corresponds directly to angular momentum conservation.",
        derivationSteps: [
            "\\delta x^i = \\epsilon^i_{\\,\\,j} x^j \\implies J^\\mu_{ij} = x_i T^\\mu_{\\,\\,j} - x_j T^\\mu_{\\,\\,i}",
            "\\text{Rotational Symmetry implies: } T^{\\mu\\nu} = T^{\\nu\\mu} \\text{ (Symmetric tensor)}",
            "\\text{Divergence of angular current: } \\partial_\\mu J^\\mu_{ij} = 0 \\implies \\frac{d\\mathbf{L}}{dt} = 0"
        ],
        sliders: [
            {
                id: "break_rotation_symmetry",
                label: "Break Rotational Isotropy (Asymmetry)",
                min: 0,
                max: 100,
                value: 0,
                step: 1,
                unit: "%",
                description: "Deforms the gravitational potential from spherical to a quadrupole field."
            }
        ]
    },
    {
        id: "gauge_u1",
        title: "Global U(1) Gauge Invariance",
        category: "Internal Symmetry",
        description: "Invariance of a complex field under global phase transformations (rotating the phasor globally in the complex plane) leads directly to the conservation of electric charge.",
        generator: "Q = \\int J^0 d^3x",
        coordinateShift: "\\phi \\to e^{i\\alpha}\\phi",
        conservedCurrent: "J^\\mu = iq(\\phi^* \\partial^\\mu \\phi - \\phi \\partial^\\mu \\phi^*)",
        conservationLaw: "\\partial_\\mu J^\\mu = 0 \\quad \\text{(Charge Conservation)}",
        accentColor: "#ff4e88", // pink
        themeBgColor: "rgba(255, 78, 136, 0.08)",
        themeBorderColor: "rgba(255, 78, 136, 0.35)",
        derivationDesc: "For complex scalar fields \\(\\phi\\), a global phase shift rotation \\(\\phi \\to e^{i \\alpha} \\phi\\) leaves the Lagrangian invariant. By Noether's theorem, this internal phase symmetry produces a conserved 4-vector current, which integrated over space gives conservation of total charge.",
        derivationSteps: [
            "\\delta \\phi = i \\alpha \\phi \\quad \\text{and} \\quad \\delta \\phi^* = -i \\alpha \\phi^* \\quad (\\delta \\mathcal{L} = 0)",
            "J^\\mu = \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} (i \\phi) + \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi^*)} (-i \\phi^*)",
            "\\text{For Klein-Gordon: } J^\\mu = iq \\left( \\phi^* \\partial^\\mu \\phi - \\phi \\partial^\\mu \\phi^* \\right)",
            "\\text{Conservation: } \\partial_\\mu J^\\mu = 0 \\implies \\frac{dQ}{dt} = 0"
        ],
        sliders: [
            {
                id: "u1_phase_shift",
                label: "Adjust Global Phase (θ)",
                min: 0,
                max: 360,
                value: 0,
                step: 2,
                unit: "°",
                description: "Rotates the wave function phase globally. Probability density is invariant."
            }
        ]
    },
    {
        id: "lorentz_boost",
        title: "Lorentz Boost Invariance",
        category: "Spacetime Symmetry",
        description: "Invariance of physical laws under relativistic velocity boosts. This symmetry guarantees that the center of mass moves at a constant velocity.",
        generator: "K_i = t \\partial_i + x_i \\partial_t",
        coordinateShift: "x^\\mu \\to \\Lambda^\\mu_{\\,\\,\\nu} x^\\nu",
        conservedCurrent: "M^{\\mu 0 i} \\quad \\text{(Boost current components)}",
        conservationLaw: "\\partial_\\mu M^{\\mu 0 i} = 0 \\implies \\mathbf{P}t - E\\mathbf{R}_{cm} = \\text{const}",
        accentColor: "#f97316", // orange
        themeBgColor: "rgba(249, 115, 22, 0.08)",
        themeBorderColor: "rgba(249, 115, 22, 0.35)",
        derivationDesc: "Under an infinitesimal Lorentz boost, coordinates transform as \\(\\delta x^i = \\epsilon^i t\\) and \\(\\delta t = \\epsilon^j x_j / c^2\\). Noether's theorem associates this with a conserved quantities representing energy-weighted conservation of the relativistic center-of-mass motion.",
        derivationSteps: [
            "\\delta x^\\mu = \\epsilon^{\\mu\\nu} x_nu \\implies M^{\\mu\\alpha\\beta} = x^\\alpha T^{\\mu\\beta} - x^\\beta T^{\\mu\\alpha}",
            "\\text{Boost conserved component: } J^\\mu_{0i} = t T^\\mu_{\\,\\,i} - x_i T^\\mu_{\\,\\,0}",
            "\\text{Divergence is zero: } \\partial_\\mu J^\\mu_{0i} = 0 \\implies \\mathbf{N} = \\mathbf{P}t - E\\mathbf{R}_{cm} = \\text{const}"
        ],
        sliders: [
            {
                id: "boost_velocity",
                label: "Boost Velocity (v/c)",
                min: 0,
                max: 95,
                value: 0,
                step: 1,
                unit: "%",
                description: "Hyperbolically rotates space and time axes to simulate Lorentz contraction."
            }
        ]
    }
];

let activeSymmetry = SYMMETRIES[0];
let simAnimationId = null;

// Simulation States
let simTime = 0;
let timeData = [];
let quantityData = [];
const maxDataPoints = 150;

// Canvas details
let canvas, ctx;
let chartCanvas, chartCtx;

// Physics parameters
let pendulumAngle = Math.PI / 4;
let pendulumSpeed = 0;
let particleX = 50;
let particleV = 2.5;
let planetR = 110;
let planetAngle = 0;
let planetSpeed = 0.04;
let orbitPoints = [];

// Initialize everything on DOM Load
document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("vault-canvas");
    ctx = canvas.getContext("2d");
    chartCanvas = document.getElementById("chart-canvas");
    chartCtx = chartCanvas.getContext("2d");

    // Setup responsive sizing
    resizeCanvas();
    window.addEventListener("resize", () => {
        resizeCanvas();
    });

    renderSymmetryList();
    loadSymmetry(SYMMETRIES[0].id);
});

function resizeCanvas() {
    if (canvas && chartCanvas) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
        chartCanvas.width = chartCanvas.parentElement.clientWidth;
        chartCanvas.height = chartCanvas.parentElement.clientHeight;
    }
}

// Render the Left Sidebar List
function renderSymmetryList() {
    const container = document.getElementById("symmetry-list");
    container.innerHTML = "";

    SYMMETRIES.forEach(sym => {
        const item = document.createElement("div");
        item.className = "symmetry-item";
        item.id = `sym-item-${sym.id}`;
        item.style.setProperty("--theme-color", sym.accentColor);
        
        item.innerHTML = `
            <h4>${sym.title}</h4>
            <div class="sym-meta">
                <span>${sym.category}</span>
                <span class="generator">${sym.generator}</span>
            </div>
        `;
        
        item.addEventListener("click", () => loadSymmetry(sym.id));
        container.appendChild(item);
    });
}

// Load selected symmetry details and start simulation
function loadSymmetry(id) {
    const sym = SYMMETRIES.find(s => s.id === id);
    if (!sym) return;

    activeSymmetry = sym;

    // Update active class in sidebar
    document.querySelectorAll(".symmetry-item").forEach(el => {
        el.classList.remove("active");
    });
    document.getElementById(`sym-item-${id}`).classList.add("active");

    // Update theme custom variables on the viewer card
    const card = document.getElementById("vault-card");
    card.style.setProperty("--theme-color", sym.accentColor);
    card.style.setProperty("--theme-bg-color", sym.themeBgColor);
    card.style.setProperty("--theme-border-color", sym.themeBorderColor);

    // Update texts
    document.getElementById("active-category").textContent = sym.category;
    document.getElementById("active-symmetry-title").textContent = sym.title;
    document.getElementById("active-symmetry-description").textContent = sym.description;
    document.getElementById("derivation-description").textContent = sym.derivationDesc;

    // Render MathJax formulas
    document.getElementById("math-current").innerHTML = `\\[ J^\\mu = ${sym.conservedCurrent} \\]`;
    document.getElementById("math-conservation").innerHTML = `\\[ ${sym.conservationLaw} \\]`;

    const stepsHtml = sym.derivationSteps.map((step, idx) => `
        <div style="margin-bottom:12px; font-size:1.1rem; color:#ffd700;">
            <span style="color:var(--text-muted); font-size:0.8rem; display:block; margin-bottom:4px;">Step ${idx + 1}</span>
            \\[ ${step} \\]
        </div>
    `).join("");
    document.getElementById("derivation-math").innerHTML = stepsHtml;

    // Typeset MathJax
    if (window.MathJax) {
        MathJax.typesetPromise();
    }

    // Render Sliders
    renderSliders(sym.sliders);

    // Reset Simulation Data
    timeData = [];
    quantityData = [];
    simTime = 0;
    pendulumAngle = Math.PI / 3;
    pendulumSpeed = 0;
    particleX = 50;
    particleV = 2;
    planetR = 100;
    planetAngle = 0;
    planetSpeed = 0.045;
    orbitPoints = [];

    // Set Slider Action listeners
    setupSliderListeners();

    // Start Simulation Loop
    if (simAnimationId) {
        cancelAnimationFrame(simAnimationId);
    }
    
    // Make sure canvas size is updated
    resizeCanvas();
    
    simAnimationId = requestAnimationFrame(simulationLoop);
}

// Dynamically generate sliders
function renderSliders(sliders) {
    const container = document.getElementById("controls-container");
    container.innerHTML = "";

    sliders.forEach(slider => {
        const group = document.createElement("div");
        group.className = "control-group";
        
        group.innerHTML = `
            <label for="${slider.id}">
                ${slider.label}: <strong id="val-${slider.id}" style="color: var(--theme-color);">${slider.value}${slider.unit}</strong>
            </label>
            <input type="range" id="${slider.id}" min="${slider.min}" max="${slider.max}" value="${slider.value}" step="${slider.step}">
            <p style="font-size:0.7rem; color:var(--text-muted); margin: 2px 0 0 0; line-height: 1.3;">${slider.description}</p>
        `;
        
        container.appendChild(group);
    });
}

function setupSliderListeners() {
    activeSymmetry.sliders.forEach(slider => {
        const el = document.getElementById(slider.id);
        if (el) {
            el.addEventListener("input", (e) => {
                const val = e.target.value;
                document.getElementById(`val-${slider.id}`).textContent = `${val}${slider.unit}`;
                
                // Active symmetry breaks status indicators
                const statusEl = document.getElementById("system-status");
                if (parseFloat(val) > 0 && slider.id !== "u1_phase_shift") {
                    statusEl.textContent = "Symmetry Broken (Non-Conserved)";
                    statusEl.className = "status-value status-broken";
                } else {
                    statusEl.textContent = "Symmetric (Conserved)";
                    statusEl.className = "status-value status-conserved";
                }
            });
        }
    });
}

// Master Loop
function simulationLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    let conservedVal = 0;
    let isSymmetric = true;

    // Run active solver
    switch(activeSymmetry.id) {
        case "time_translation":
            conservedVal = runTimeTranslationSim();
            const timeVal = parseFloat(document.getElementById("break_time_symmetry")?.value || 0);
            if (timeVal > 0) isSymmetric = false;
            break;
        case "space_translation":
            conservedVal = runSpaceTranslationSim();
            const spaceVal = parseFloat(document.getElementById("break_space_symmetry")?.value || 0);
            if (spaceVal > 0) isSymmetric = false;
            break;
        case "space_rotation":
            conservedVal = runSpaceRotationSim();
            const rotVal = parseFloat(document.getElementById("break_rotation_symmetry")?.value || 0);
            if (rotVal > 0) isSymmetric = false;
            break;
        case "gauge_u1":
            conservedVal = runGaugeU1Sim();
            isSymmetric = true; // phase is purely global
            break;
        case "lorentz_boost":
            conservedVal = runLorentzBoostSim();
            isSymmetric = true; // interval invariant
            break;
    }

    // Update conservation records
    quantityData.push(conservedVal);
    timeData.push(simTime++);
    if (quantityData.length > maxDataPoints) {
        quantityData.shift();
        timeData.shift();
    }

    // Render moving line chart
    drawChart(isSymmetric);

    simAnimationId = requestAnimationFrame(simulationLoop);
}

// TIME TRANSLATION SIMULATION (PENDULUM WITH TIME VARYING POTENTIAL)
function runTimeTranslationSim() {
    const isBrokenVal = parseFloat(document.getElementById("break_time_symmetry")?.value || 0);
    const A = isBrokenVal / 100.0;
    
    // Vary gravity over time if symmetry is broken
    let g0 = 0.45;
    let w = 0.08;
    let g = g0;
    if (A > 0) {
        g = g0 * (1.0 + A * Math.sin(w * simTime));
    }

    // Verlet integration for simple pendulum
    let L = canvas.height * 0.4;
    let originX = canvas.width / 2;
    let originY = canvas.height * 0.25;
    
    let accel = -(g / L) * Math.sin(pendulumAngle);
    pendulumSpeed += accel;
    pendulumAngle += pendulumSpeed;
    // Friction damping very small
    pendulumSpeed *= 0.9995;

    let bobX = originX + L * Math.sin(pendulumAngle);
    let bobY = originY + L * Math.cos(pendulumAngle);

    // Calculate energy
    let mass = 1.0;
    let kinetic = 0.5 * mass * (L * pendulumSpeed) * (L * pendulumSpeed);
    // Potential energy defined relative to origin center
    let potential = mass * g * (L - L * Math.cos(pendulumAngle));
    let totalEnergy = kinetic + potential;

    // Draw Pendulum on main canvas
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(originX, originY, L, 0, Math.PI * 2);
    ctx.stroke();

    ctx.strokeStyle = activeSymmetry.accentColor;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(originX, originY);
    ctx.lineTo(bobX, bobY);
    ctx.stroke();

    // Draw origin hinge
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(originX, originY, 6, 0, Math.PI * 2);
    ctx.fill();

    // Draw bob
    ctx.fillStyle = activeSymmetry.accentColor;
    ctx.shadowColor = activeSymmetry.accentColor;
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(bobX, bobY, 18, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0; // reset

    // Draw energy text overlay
    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText(`g(t): ${g.toFixed(3)} m/s²`, originX + L + 20, originY);
    ctx.fillText(`Kinetic Energy (K): ${(kinetic * 10).toFixed(1)} J`, originX + L + 20, originY + 20);
    ctx.fillText(`Potential Energy (U): ${(potential * 10).toFixed(1)} J`, originX + L + 20, originY + 40);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Total Energy (E): ${(totalEnergy * 10).toFixed(2)} J`, originX + L + 20, originY + 60);

    return totalEnergy * 10;
}

// SPACE TRANSLATION SIMULATION (PARTICLE ROLL OVER SPACE HILLS)
function runSpaceTranslationSim() {
    const isBrokenVal = parseFloat(document.getElementById("break_space_symmetry")?.value || 0);
    const A = isBrokenVal * 0.7; // Amplitude of hills

    let hillFreq = 0.025;
    let hillHeight = A;

    // If symmetry broken, particle experiences force F = -dU/dx
    // Potential: U(x) = hillHeight * cos(hillFreq * x)
    // Force: F = hillHeight * hillFreq * sin(hillFreq * x)
    let friction = 0.9995;
    let force = 0;
    if (A > 0) {
        force = hillHeight * hillFreq * Math.sin(hillFreq * particleX);
    }
    
    particleV += force * 0.1;
    particleX += particleV;
    particleV *= friction;

    // Wrap around boundaries
    if (particleX > canvas.width + 50) {
        particleX = -50;
    } else if (particleX < -50) {
        particleX = canvas.width + 50;
    }

    // Draw Space Hills Potential
    ctx.strokeStyle = "rgba(255,255,255,0.1)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, canvas.height * 0.65);
    ctx.lineTo(canvas.width, canvas.height * 0.65);
    ctx.stroke();

    if (A > 0) {
        ctx.fillStyle = "rgba(0, 210, 255, 0.05)";
        ctx.strokeStyle = "rgba(0, 210, 255, 0.25)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height * 0.65);
        for (let x = 0; x <= canvas.width; x += 5) {
            let y = canvas.height * 0.65 - hillHeight * Math.cos(hillFreq * x);
            ctx.lineTo(x, y);
        }
        ctx.lineTo(canvas.width, canvas.height);
        ctx.lineTo(0, canvas.height);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();
    }

    // Particle Y position sits on potential landscape
    let particleY = canvas.height * 0.65;
    if (A > 0) {
        particleY = canvas.height * 0.65 - hillHeight * Math.cos(hillFreq * particleX);
    }

    // Draw particle
    ctx.fillStyle = activeSymmetry.accentColor;
    ctx.shadowColor = activeSymmetry.accentColor;
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(particleX, particleY - 10, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw velocity vector arrow
    ctx.strokeStyle = "#ffd700";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(particleX, particleY - 10);
    ctx.lineTo(particleX + particleV * 15, particleY - 10);
    ctx.stroke();

    // Momentum p = m * v (let m = 5)
    let p = 5.0 * particleV;

    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText(`Position (x): ${particleX.toFixed(1)} m`, 20, 40);
    ctx.fillText(`Velocity (v): ${particleV.toFixed(2)} m/s`, 20, 60);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Linear Momentum (p): ${p.toFixed(3)} kg·m/s`, 20, 80);

    return p;
}

// SPATIAL ROTATION SIMULATION (PLANETARY ORBIT WITH DISTORTION)
function runSpaceRotationSim() {
    const isBrokenVal = parseFloat(document.getElementById("break_rotation_symmetry")?.value || 0);
    const A = isBrokenVal / 100.0;

    let centerX = canvas.width / 2;
    let centerY = canvas.height / 2;

    // Planetary gravity.
    // If symmetry broken, force has angular component (quadrupole field)
    let G = 400;
    let dist = planetR;
    let gravityForce = G / (dist * dist);
    
    // Distort orbit mechanics
    if (A > 0) {
        // Break radial central symmetry by making G depend on angle
        // Potential has a cos(2*theta) angular perturbation
        planetSpeed += 0.003 * A * Math.sin(2 * planetAngle);
    }
    
    planetAngle += planetSpeed;
    
    // Vary radius dynamically to simulate elliptic trajectory
    let eccentricity = 0.25;
    let baseR = canvas.height * 0.3;
    
    // Add anisotropic elongation
    let elongation = A * eccentricity * 40 * Math.cos(2 * planetAngle);
    let r = baseR / (1 + eccentricity * Math.cos(planetAngle)) + elongation;

    let planetX = centerX + r * Math.cos(planetAngle);
    let planetY = centerY + r * Math.sin(planetAngle);

    // Save orbit points for tail
    orbitPoints.push({ x: planetX, y: planetY });
    if (orbitPoints.length > 80) orbitPoints.shift();

    // Draw orbit path tail
    ctx.strokeStyle = "rgba(139, 92, 246, 0.2)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    orbitPoints.forEach((p, idx) => {
        if (idx === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
    });
    ctx.stroke();

    // Draw Central Star (Sun)
    ctx.fillStyle = "#fbbf24";
    ctx.shadowColor = "#fbbf24";
    ctx.shadowBlur = 25;
    ctx.beginPath();
    ctx.arc(centerX, centerY, 15, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Draw planet
    ctx.fillStyle = activeSymmetry.accentColor;
    ctx.shadowColor = activeSymmetry.accentColor;
    ctx.shadowBlur = 10;
    ctx.beginPath();
    ctx.arc(planetX, planetY, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Calculate angular momentum L = r * p_theta = r^2 * d_theta/dt (let m = 0.5)
    let L = 0.5 * r * r * planetSpeed * 0.05;

    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText(`Orbit Radius (r): ${r.toFixed(1)} km`, 20, 40);
    ctx.fillText(`Angular Velocity (ω): ${planetSpeed.toFixed(3)} rad/s`, 20, 60);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Angular Momentum (L): ${L.toFixed(3)} J·s`, 20, 80);

    return L;
}

// U(1) GAUGE SYMMETRY (QUANTUM WAVE PACKET & PHASE ANGLE)
function runGaugeU1Sim() {
    const phaseVal = parseFloat(document.getElementById("u1_phase_shift")?.value || 0);
    const theta = (phaseVal * Math.PI) / 180.0; // Global phase rotation

    let centerX = canvas.width / 2;
    let centerY = canvas.height * 0.5;
    let width = canvas.width;

    // Draw complex phasor circle in corner
    let cornerX = canvas.width - 60;
    let cornerY = 60;
    ctx.strokeStyle = "rgba(255,255,255,0.15)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.arc(cornerX, cornerY, 30, 0, Math.PI * 2);
    ctx.stroke();
    
    // Draw phasor arrow representing global phase
    ctx.strokeStyle = activeSymmetry.accentColor;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(cornerX, cornerY);
    ctx.lineTo(cornerX + 30 * Math.cos(theta), cornerY + 30 * Math.sin(theta));
    ctx.stroke();
    ctx.fillStyle = "#ffffff";
    ctx.beginPath();
    ctx.arc(cornerX + 30 * Math.cos(theta), cornerY + 30 * Math.sin(theta), 4, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.font = "10px Space Grotesk, sans-serif";
    ctx.fillText("Global U(1) Phase", cornerX - 40, cornerY + 45);

    // Compute and draw wave packet: Real part Re(ψ) and Probability Density |ψ|²
    // ψ(x) = Amplitude * exp(-(x-x0)²/σ²) * exp(i (kx + θ))
    // Re(ψ) = Amplitude * exp(-(x-x0)²/σ²) * cos(kx + θ)
    // |ψ|² = Amplitude² * exp(-2(x-x0)²/σ²)  -- purely phase independent!
    let k = 0.08;
    let sigma = 70;
    let amp = 80;
    let x0 = centerX;

    // Draw Probability Density (consisting of pure, phase-independent mass envelope)
    ctx.fillStyle = "rgba(255, 78, 136, 0.06)";
    ctx.strokeStyle = "rgba(255, 78, 136, 0.35)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    for (let x = 0; x < width; x += 3) {
        let envelope = amp * Math.exp(-Math.pow(x - x0, 2) / Math.pow(sigma, 2));
        let prob = (Math.pow(envelope, 2) / amp); // |ψ|²
        ctx.lineTo(x, centerY - prob);
    }
    ctx.lineTo(width, centerY);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();

    // Draw Real wave function Re(ψ) which oscillates when phase is shifted
    ctx.strokeStyle = activeSymmetry.accentColor;
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    for (let x = 0; x < width; x += 3) {
        let envelope = amp * Math.exp(-Math.pow(x - x0, 2) / Math.pow(sigma, 2));
        let wave = envelope * Math.cos(k * (x - x0) + theta);
        if (x === 0) ctx.moveTo(x, centerY - wave);
        else ctx.lineTo(x, centerY - wave);
    }
    ctx.stroke();

    // Flat zero axis line
    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, centerY);
    ctx.lineTo(width, centerY);
    ctx.stroke();

    // Total Charge (integral of |ψ|² dx, constant over time & phase independent)
    let totalCharge = 1.0; // Conserved constant value

    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText("ψ(x) = Re[ψ] (cyan wave oscillations)", 20, 40);
    ctx.fillText("|ψ(x)|² = Probability Density (shaded pink envelope)", 20, 60);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Conserved Total Charge (Q): ${totalCharge.toFixed(4)} e`, 20, 80);

    return totalCharge;
}

// LORENTZ BOOST SIMULATION (WARPING COORDINATES IN SPACETIME)
function runLorentzBoostSim() {
    const boostVal = parseFloat(document.getElementById("boost_velocity")?.value || 0);
    const beta = boostVal / 100.0; // v/c
    const gamma = 1.0 / Math.sqrt(1.0 - beta * beta); // Relativistic gamma factor

    let centerX = canvas.width / 2;
    let centerY = canvas.height / 2;

    // Draw Spacetime axes grid.
    // Coordinates (x, t). We draw light cone (x = ±ct) which remains invariant!
    // Light cone coordinates
    ctx.strokeStyle = "rgba(239, 68, 68, 0.25)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(centerX - centerY, canvas.height);
    ctx.lineTo(centerX + centerY, 0);
    ctx.moveTo(centerX + centerY, canvas.height);
    ctx.lineTo(centerX - centerY, 0);
    ctx.stroke();

    ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
    ctx.font = "9px Space Grotesk, sans-serif";
    ctx.fillText("Light Cone (x = ct)", centerX + centerY - 90, 20);

    // Draw boosted grid lines.
    // Every grid line x = const is sheared hyperbolically.
    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 1;
    let gridCount = 8;
    let step = canvas.height / (gridCount * 2);

    // Standard static coordinate grid
    for(let i = -gridCount; i <= gridCount; i++) {
        // vertical
        ctx.beginPath();
        ctx.moveTo(centerX + i * step, 0);
        ctx.lineTo(centerX + i * step, canvas.height);
        ctx.stroke();
        // horizontal
        ctx.beginPath();
        ctx.moveTo(0, centerY + i * step);
        ctx.lineTo(canvas.width, centerY + i * step);
        ctx.stroke();
    }

    // Boosted Coordinate axes (x' and ct')
    // x' axis: ct = beta * x  ==>  y = centerY - beta * (x - centerX)
    // ct' axis: x = beta * ct ==>  x = centerX + beta * (centerY - y)
    ctx.strokeStyle = activeSymmetry.accentColor;
    ctx.lineWidth = 2.5;

    // ct' axis (Time axis)
    ctx.beginPath();
    ctx.moveTo(centerX - beta * centerY, canvas.height);
    ctx.lineTo(centerX + beta * centerY, 0);
    ctx.stroke();

    // x' axis (Space axis)
    ctx.beginPath();
    ctx.moveTo(0, centerY + beta * (centerX));
    ctx.lineTo(canvas.width, centerY - beta * (centerX));
    ctx.stroke();

    // Draw labels
    ctx.fillStyle = activeSymmetry.accentColor;
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText("ct'", centerX + beta * centerY + 10, 20);
    ctx.fillText("x'", canvas.width - 25, centerY - beta * (centerX) - 10);

    // Relativistic Interval s² = x² - c²t² (Invariant conserved quantity)
    // Draw event point A at (x0, t0) and its boosted counterpart
    let evX = 80;
    let evT = -40; // coordinates relative to center
    
    // Hyperbolic rotation mapping
    let evX_prime = gamma * (evX - beta * evT);
    let evT_prime = gamma * (evT - beta * evX);

    // Draw Event Dot
    ctx.fillStyle = "#ffd700";
    ctx.beginPath();
    ctx.arc(centerX + evX_prime, centerY + evT_prime, 6, 0, Math.PI * 2);
    ctx.fill();

    // Draw label
    ctx.fillText("Event A", centerX + evX_prime + 10, centerY + evT_prime + 4);

    let interval = (evX * evX) - (evT * evT);

    ctx.fillStyle = "rgba(255,255,255,0.7)";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText(`Relativistic Lorentz Gamma (γ): ${gamma.toFixed(4)}`, 20, 40);
    ctx.fillText(`Event coordinates: x' = ${evX_prime.toFixed(1)}, ct' = ${evT_prime.toFixed(1)}`, 20, 60);
    ctx.fillStyle = "#ffd700";
    ctx.fillText(`Spacetime Interval (s² = x² - c²t²): ${interval.toFixed(1)} (Constant)`, 20, 80);

    return interval / 100.0;
}

// Chart drawing logic for the Conserved Quantity Plotter
function drawChart(isSymmetric) {
    if (!chartCtx) return;
    
    chartCtx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);

    if (quantityData.length < 2) return;

    // Find min and max for scaling
    let max = Math.max(...quantityData);
    let min = Math.min(...quantityData);
    
    // Padding
    let range = max - min;
    if (range < 1) {
        max += 0.5;
        min -= 0.5;
        range = max - min;
    } else {
        max += range * 0.1;
        min -= range * 0.1;
        range = max - min;
    }

    chartCtx.strokeStyle = isSymmetric ? "#10b981" : "#ef4444"; // green vs red
    chartCtx.lineWidth = 2;
    chartCtx.beginPath();

    let width = chartCanvas.width;
    let height = chartCanvas.height;
    let stepX = width / (maxDataPoints - 1);

    quantityData.forEach((val, idx) => {
        let x = idx * stepX;
        // Map val to y coordinates
        let y = height - ((val - min) / range) * height;
        if (idx === 0) chartCtx.moveTo(x, y);
        else chartCtx.lineTo(x, y);
    });

    chartCtx.stroke();

    // Draw simple grid line at last point
    chartCtx.strokeStyle = "rgba(255,255,255,0.04)";
    chartCtx.lineWidth = 0.8;
    chartCtx.beginPath();
    chartCtx.moveTo(0, height / 2);
    chartCtx.lineTo(width, height / 2);
    chartCtx.stroke();
}
