/**
 * Anthropic Constant Tuner & Cosmological Scaling Sandbox
 * Real-time scale calculator and multi-viewport visualizer.
 */

// Universe Constant Dials (relative multipliers, standard = 1.0)
let dialG = 1.0;
let dialC = 1.0;
let dialHbar = 1.0;
let dialAlpha = 1.0;
let dialMe = 1.0;
let dialMp = 1.0;

let simAnimationId = null;
let simTime = 0;

// Canvas details
let canvas, ctx;

// Orbit Angles for Visualizers
let atomAngle = 0;
let planetAngle = 0;
let starPulse = 0;

// Sliders config
const DIALS = [
    { id: "dial-G", label: "Gravitational Constant (G)", min: -3.0, max: 3.0, value: 0.0, step: 0.1, isLog: true, description: "Governs strength of gravitational attraction." },
    { id: "dial-c", label: "Speed of Light (c)", min: 0.2, max: 3.0, value: 1.0, step: 0.1, isLog: false, description: "Governs speed limit and mass-energy equivalence." },
    { id: "dial-hbar", label: "Planck Constant (ℏ)", min: 0.15, max: 4.0, value: 1.0, step: 0.05, isLog: false, description: "Governs quantum fuzziness and uncertainty scale." },
    { id: "dial-alpha", label: "Fine-Structure Constant (α)", min: 0.05, max: 3.0, value: 1.0, step: 0.05, isLog: false, description: "Governs strength of electromagnetic force (atoms/chemistry)." },
    { id: "dial-me", label: "Electron Mass (m_e)", min: 0.1, max: 5.0, value: 1.0, step: 0.1, isLog: false, description: "Governs atomic electron shell mass." },
    { id: "dial-mp", label: "Proton Mass (m_p)", min: 0.1, max: 5.0, value: 1.0, step: 0.1, isLog: false, description: "Governs nuclear mass and gravity scale." }
];

document.addEventListener("DOMContentLoaded", () => {
    canvas = document.getElementById("tuner-canvas");
    ctx = canvas.getContext("2d");

    // UI actions
    document.getElementById("reset-dials-btn").addEventListener("click", resetToStandard);

    // Populate sliders
    renderDials();

    // Resize canvas
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initial check & start loop
    recalculateScaling();
    simAnimationId = requestAnimationFrame(simulationLoop);
});

function resizeCanvas() {
    if (canvas) {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = canvas.parentElement.clientHeight;
    }
}

function renderDials() {
    const container = document.getElementById("dials-sliders-container");
    container.innerHTML = "";

    DIALS.forEach(dial => {
        const group = document.createElement("div");
        group.className = "control-group";
        
        // Formatted value display
        let displayVal = dial.value;
        if (dial.isLog) {
            displayVal = Math.pow(10, dial.value).toFixed(2);
        } else {
            displayVal = dial.value.toFixed(2);
        }

        group.innerHTML = `
            <label for="${dial.id}">
                <span>${dial.label}</span>
                <strong id="val-${dial.id}" style="color: var(--accent-astrophysics);">${displayVal}×</strong>
            </label>
            <input type="range" id="${dial.id}" min="${dial.min}" max="${dial.max}" value="${dial.value}" step="${dial.step}">
            <p style="font-size:0.7rem; color:var(--text-muted); margin: 2px 0 0 0; line-height: 1.3;">${dial.description}</p>
        `;
        
        container.appendChild(group);

        // Slider listeners
        document.getElementById(dial.id).addEventListener("input", (e) => {
            let val = parseFloat(e.target.value);
            let absoluteVal = val;
            
            if (dial.isLog) {
                absoluteVal = Math.pow(10, val);
                document.getElementById(`val-${dial.id}`).textContent = `${absoluteVal.toFixed(2)}×`;
            } else {
                document.getElementById(`val-${dial.id}`).textContent = `${val.toFixed(2)}×`;
            }

            // Sync dial variables
            if (dial.id === "dial-G") dialG = absoluteVal;
            if (dial.id === "dial-c") dialC = absoluteVal;
            if (dial.id === "dial-hbar") dialHbar = absoluteVal;
            if (dial.id === "dial-alpha") dialAlpha = absoluteVal;
            if (dial.id === "dial-me") dialMe = absoluteVal;
            if (dial.id === "dial-mp") dialMp = absoluteVal;

            recalculateScaling();
        });
    });
}

function resetToStandard() {
    DIALS.forEach(dial => {
        const input = document.getElementById(dial.id);
        if (input) {
            input.value = dial.value;
            let displayVal = dial.value;
            if (dial.isLog) {
                displayVal = Math.pow(10, dial.value).toFixed(2);
            } else {
                displayVal = dial.value.toFixed(2);
            }
            document.getElementById(`val-${dial.id}`).textContent = `${displayVal}×`;
        }
    });

    dialG = 1.0;
    dialC = 1.0;
    dialHbar = 1.0;
    dialAlpha = 1.0;
    dialMe = 1.0;
    dialMp = 1.0;

    recalculateScaling();
}

// Recalculate physical quantities relative to standard values
function recalculateScaling() {
    // Bohr Radius ratio: a0 ∝ ℏ / (α * me * c)
    const bohrRadius = dialHbar / (dialAlpha * dialMe * dialC);
    
    // Rydberg Energy ratio: ER ∝ α² * me * c²
    const rydbergEnergy = Math.pow(dialAlpha, 2) * dialMe * Math.pow(dialC, 2);
    
    // Planck Length ratio: lP ∝ sqrt(G * ℏ / c³)
    const planckLength = Math.sqrt((dialG * dialHbar) / Math.pow(dialC, 3));
    
    // Chandrasekhar Limit ratio: Mch ∝ (ℏ * c / (G * mp²))^(3/2) * mp
    const chLimit = Math.pow((dialHbar * dialC) / (dialG * Math.pow(dialMp, 2)), 1.5) * dialMp;
    
    // Main sequence star lifetime ratio: τms ∝ ℏ² / (G * mp³ * c)
    const starLifetime = Math.pow(dialHbar, 2) / (dialG * Math.pow(dialMp, 3) * dialC);

    // Update Table
    updateTable([
        { name: "Bohr Radius (Size of Atoms)", math: "a_0 \\propto \\frac{\\hbar}{\\alpha m_e c}", ratio: bohrRadius, desc: "Determines physical boundary scale of electron shells." },
        { name: "Rydberg Energy (Atomic Bonds)", math: "E_{\\infty} \\propto \\alpha^2 m_e c^2", ratio: rydbergEnergy, desc: "Determines chemical binding energy and material stability." },
        { name: "Planck Length (Quantum Gravity)", math: "\\ell_P \\propto \\sqrt{\\frac{G \\hbar}{c^3}}", ratio: planckLength, desc: "Minimal spatial scale where general covariance breaks down." },
        { name: "Chandrasekhar Limit (Stellar Collapse)", math: "M_{\\text{Ch}} \\propto \\left(\\frac{\\hbar c}{G m_p^2}\\right)^{3/2} m_p", ratio: chLimit, desc: "Mass threshold for stellar ignition and final black hole collapse." },
        { name: "Stellar Lifetime (Main Sequence)", math: "\\tau_{\\text{ms}} \\propto \\frac{\\hbar^2}{G m_p^3 c}", ratio: starLifetime, desc: "Governs duration of fusion burn in standard hydrogen stars." }
    ]);

    // Check boundaries and output warnings
    checkAnthropicBoundaries(bohrRadius, rydbergEnergy, chLimit, starLifetime);
}

function updateTable(metrics) {
    const tbody = document.getElementById("metrics-tbody");
    tbody.innerHTML = "";

    metrics.forEach(m => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td><strong>${m.name}</strong></td>
            <td class="math-def">\\[ ${m.math} \\]</td>
            <td class="val-computed">${m.ratio.toExponential(3)}×</td>
            <td style="color: var(--text-muted); font-size: 0.8rem;">${m.desc}</td>
        `;
        tbody.appendChild(tr);
    });

    if (window.MathJax) {
        MathJax.typesetPromise();
    }
}

// Audits the constants configuration and outputs warning flags
function checkAnthropicBoundaries(bohrRadius, rydbergEnergy, chLimit, starLifetime) {
    const consoleBox = document.getElementById("console-output");
    consoleBox.innerHTML = "";

    const warnings = [];

    // 1. Electromagnetism Boundaries
    if (dialAlpha > 2.2) {
        warnings.push({
            title: "Relativistic Orbit Disintegration",
            desc: "The Fine-Structure Constant (α) is too large. Relativistic nuclear corrections destabilize core electron shells; orbits disintegrate into the nucleus, preventing heavy chemistry."
        });
    } else if (dialAlpha < 0.25) {
        warnings.push({
            title: "Chemical Bond Dissolution",
            desc: "The Fine-Structure Constant (α) is too small. Chemical bond energies (Rydberg scale) are weak, molecules dissolve, and complex chemistry cannot coalesce."
        });
    }

    // 2. Gravity / Stellar Boundaries
    if (dialG > 150.0) {
        warnings.push({
            title: "Instant Black Hole Collapse",
            desc: "Gravity Constant (G) is excessively strong. Stellar mass thresholds (Chandrasekhar Limit) drop, causing all collapsing matter to fall immediately into black holes. Stable planets are crushed."
        });
    } else if (dialG < 0.005) {
        warnings.push({
            title: "Stellar Fusion Deficit",
            desc: "Gravity Constant (G) is too weak. Gas clouds lack the gravitational pressure required to trigger nuclear fusion core ignition. The universe is a cold, dark place."
        });
    }

    // 3. Planck scale
    if (dialHbar > 3.0) {
        warnings.push({
            title: "Macroscopic Quantum Chaos",
            desc: "Planck's Constant (ℏ) is too large. Quantum wave packet spreading and uncertainty effects manifest at macroscopic human scales; fuzzy reality fails coordinate coherence."
        });
    } else if (dialHbar < 0.25) {
        warnings.push({
            title: "Atomic Orbital Collapse",
            desc: "Planck's Constant (ℏ) is too small. Quantum degeneracy pressure fails, causing orbital electrons to fall directly into protons; atoms collapse into point charges."
        });
    }

    // 4. Relativistic Causality
    if (dialC < 0.25) {
        warnings.push({
            title: "Causality Dilatancy Boundary",
            desc: "The speed of light (c) is too slow. Everyday kinetic speeds correspond to relativistic bounds, creating localized time dilation and causality breakdowns that destroy macroscopic structures."
        });
    }

    // 5. Lifespans
    if (starLifetime < 1.0e-5) {
        warnings.push({
            title: "Stellar Flash Burnout",
            desc: "Stellar main sequence lifetimes are too short (less than a few days/hours). Stars exhaust hydrogen fuel in a flash, preventing planetary thermal cycles and biological evolution."
        });
    }

    // Output warnings
    if (warnings.length > 0) {
        warnings.forEach(w => {
            const item = document.createElement("div");
            item.className = "warning-item";
            item.innerHTML = `
                <span class="badge-crit">CRITICAL</span>
                <span><strong>${w.title}</strong>: ${w.desc}</span>
            `;
            consoleBox.appendChild(item);
        });
    } else {
        // Universe is habitable!
        const ok = document.createElement("div");
        ok.className = "console-ok";
        ok.innerHTML = `
            <span>🟢</span>
            <strong>ANTHROPIC CONGRUENCE UNLOCKED</strong>: The physical dials of this universe are balanced. Stable atomic orbitals, nuclear core fusion, and planetary orbital structures are stable. Life is habitable.
        `;
        consoleBox.appendChild(ok);
    }
}

// Master Loop
function simulationLoop() {
    if (!ctx) return;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Multi-viewport dividers
    const W = canvas.width;
    const H = canvas.height;
    const paneW = W / 3;

    // Background panes
    ctx.fillStyle = "rgba(15, 23, 42, 0.15)";
    ctx.fillRect(0, 0, paneW - 2, H);
    ctx.fillRect(paneW + 2, 0, paneW - 4, H);
    ctx.fillRect(paneW * 2 + 2, 0, paneW, H);

    ctx.strokeStyle = "rgba(255,255,255,0.06)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(paneW, 0);
    ctx.lineTo(paneW, H);
    ctx.moveTo(paneW * 2, 0);
    ctx.lineTo(paneW * 2, H);
    ctx.stroke();

    // Orbit incrementers
    atomAngle += 0.05 * (dialC * dialAlpha * dialMe / dialHbar); // Speed scales with constants
    planetAngle += 0.02 * Math.sqrt(dialG * dialMp);
    simTime++;

    // 1. ATOMIC VIEWPORT (Left Pane)
    drawAtomicViewport(0, 0, paneW, H);

    // 2. PLANETARY SYSTEM VIEWPORT (Middle Pane)
    drawPlanetaryViewport(paneW, 0, paneW, H);

    // 3. STELLAR FUSION VIEWPORT (Right Pane)
    drawStellarViewport(paneW * 2, 0, paneW, H);

    simAnimationId = requestAnimationFrame(simulationLoop);
}

// ATOMIC VIEWPORT
function drawAtomicViewport(x, y, w, h) {
    const cx = x + w / 2;
    const cy = h / 2;
    
    // Label
    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText("I. ATOMIC ORBIT SCALE", x + 15, 25);

    // Calculate Bohr Radius relative radius
    const bohrRadius = dialHbar / (dialAlpha * dialMe * dialC);
    let r = 55.0 * bohrRadius;

    // Quantum wave packet fuzziness overlay
    const quantumFuzz = dialHbar * 20.0;

    // Draw grid rings
    ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.arc(cx, cy, 30, 0, Math.PI*2);
    ctx.arc(cx, cy, 60, 0, Math.PI*2);
    ctx.arc(cx, cy, 90, 0, Math.PI*2);
    ctx.stroke();

    // Check states
    const isCollapsed = (dialHbar < 0.25);
    const isRelativisticDisintegrating = (dialAlpha > 2.2);

    if (isCollapsed) {
        // Bohr radius collapses, electron sits inside nucleus
        r = 0;
    }

    if (isRelativisticDisintegrating) {
        // Chaotic loop paths
        ctx.strokeStyle = "rgba(239, 68, 68, 0.25)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        for (let t = 0; t < 100; t++) {
            let chaoticR = r * (0.8 + 0.3 * Math.sin(t * 0.1));
            let ca = t * 0.15 + atomAngle * 0.2;
            ctx.lineTo(cx + chaoticR * Math.cos(ca), cy + chaoticR * Math.sin(ca));
        }
        ctx.stroke();

        ctx.fillStyle = "#ef4444";
        ctx.font = "10px monospace";
        ctx.fillText("ORBIT CRUSHED", cx - 40, cy + r + 35);
    } else if (r > 0) {
        // Draw standard orbit
        ctx.strokeStyle = "rgba(100, 255, 218, 0.25)";
        ctx.lineWidth = 1.5;
        
        // Quantum fuzziness aura
        ctx.fillStyle = `rgba(100, 255, 218, ${Math.min(0.08 / dialHbar, 0.25)})`;
        ctx.beginPath();
        ctx.arc(cx, cy, r + quantumFuzz, 0, Math.PI*2);
        ctx.arc(cx, cy, Math.max(r - quantumFuzz, 0), 0, Math.PI*2);
        ctx.fill();

        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI*2);
        ctx.stroke();

        // Draw Electron dot orbiting
        let ex = cx + r * Math.cos(atomAngle);
        let ey = cy + r * Math.sin(atomAngle);
        
        ctx.fillStyle = "#64ffda"; // electron teal
        ctx.shadowColor = "#64ffda";
        ctx.shadowBlur = 10 + quantumFuzz * 0.5;
        ctx.beginPath();
        ctx.arc(ex, ey, 6, 0, Math.PI*2);
        ctx.fill();
        ctx.shadowBlur = 0;
    }

    // Draw Nucleus (Proton)
    ctx.fillStyle = "#f43f5e"; // red proton
    ctx.shadowColor = "#f43f5e";
    ctx.shadowBlur = 8;
    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, Math.PI*2);
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.font = "11px Space Grotesk, sans-serif";
    ctx.fillText(`Atomic Size: ${bohrRadius.toFixed(3)} a₀`, x + 15, h - 15);
}

// PLANETARY SYSTEM VIEWPORT
function drawPlanetaryViewport(x, y, w, h) {
    const cx = x + w / 2;
    const cy = h / 2;

    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText("II. SOLAR SYSTEM SCALE", x + 15, 25);

    // Gravity orbit scale
    // If G is too strong, orbit decays and planet collapses into star
    const G = dialG;
    let baseOrbitR = 60.0;
    let planetR = baseOrbitR;

    if (G > 150.0) {
        // Gravity too strong, orbit spirals into collapse
        planetR = Math.max(baseOrbitR - simTime * 0.4 % baseOrbitR, 16);
    } else if (G < 0.005) {
        // Gravity too weak, planet flies out
        planetR = baseOrbitR + simTime * 1.5;
    }

    // Orbit path
    if (G < 0.005 && planetR > w) {
        // Draw straight flyaway path
        ctx.strokeStyle = "rgba(255,255,255,0.06)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(cx - 30, cy - 30);
        ctx.lineTo(cx + w, cy - h);
        ctx.stroke();
    } else if (planetR > 0) {
        ctx.strokeStyle = "rgba(251, 191, 36, 0.2)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(cx, cy, planetR, 0, Math.PI*2);
        ctx.stroke();

        // Planet dot orbiting
        let px = cx + planetR * Math.cos(planetAngle);
        let py = cy + planetR * Math.sin(planetAngle);
        
        ctx.fillStyle = "#3b82f6"; // blue planet
        ctx.beginPath();
        ctx.arc(px, py, 6, 0, Math.PI*2);
        ctx.fill();
    }

    // Star (Central Sun)
    ctx.fillStyle = "#fbbf24"; // yellow sun
    ctx.shadowColor = "#fbbf24";
    ctx.shadowBlur = 15;
    ctx.beginPath();
    ctx.arc(cx, cy, 14, 0, Math.PI*2);
    ctx.fill();
    ctx.shadowBlur = 0;

    if (G > 150.0 && planetR <= 16) {
        ctx.fillStyle = "#ef4444";
        ctx.font = "10px monospace";
        ctx.fillText("PLANET COLLAPSED", cx - 45, cy + 35);
    } else if (G < 0.005 && planetR > w) {
        ctx.fillStyle = "#3b82f6";
        ctx.font = "10px monospace";
        ctx.fillText("PLANET ESCAPED", cx - 40, cy + 35);
    }

    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.font = "11px Space Grotesk, sans-serif";
    ctx.fillText(`Relative G: ${dialG.toFixed(3)} G₀`, x + 15, h - 15);
}

// STELLAR FUSION VIEWPORT
function drawStellarViewport(x, y, w, h) {
    const cx = x + w / 2;
    const cy = h / 2;

    ctx.fillStyle = "#ffffff";
    ctx.font = "12px Space Grotesk, sans-serif";
    ctx.fillText("III. STELLAR PRESSURE BALANCE", x + 15, 25);

    // Gravity pull inward = G * mp²
    // Radiation pressure outward = alpha² * me * c² (Rydberg energy)
    const gravityIn = dialG * Math.pow(dialMp, 2);
    const radiationOut = Math.pow(dialAlpha, 2) * dialMe * Math.pow(dialC, 2);
    
    // Balance ratio
    const ratio = radiationOut / gravityIn;
    
    let starR = 40.0;
    let starColor = "#fbbf24"; // standard gold
    let coreCollapse = false;
    let supernovaExplode = false;

    if (dialG > 150.0) {
        // instant collapse to black hole
        starR = 12.0;
        starColor = "#000000";
        coreCollapse = true;
    } else if (dialG < 0.005) {
        // cold gas cloud
        starR = 60.0;
        starColor = "rgba(59, 130, 246, 0.15)";
    } else if (ratio > 10.0) {
        // Radiation pressure explodes star (supernova)
        starR = 50.0 + (simTime * 2.0 % 80);
        starColor = "#ef4444";
        supernovaExplode = true;
    } else if (ratio < 0.1) {
        // Gravity crushes star (white dwarf / superdense)
        starR = 18.0;
        starColor = "#818cf8"; // blue-violet
    } else {
        // stable orbit/pulse
        starR = 35.0 + 3.0 * Math.sin(simTime * 0.05);
    }

    // Render Star
    if (coreCollapse) {
        // Draw Black Hole singularity
        ctx.fillStyle = "#000000";
        ctx.beginPath();
        ctx.arc(cx, cy, starR, 0, Math.PI*2);
        ctx.fill();
        
        // Draw gravitational lensing aura
        ctx.strokeStyle = "#f97316"; // orange lensing
        ctx.lineWidth = 3;
        ctx.shadowColor = "#f97316";
        ctx.shadowBlur = 20;
        ctx.beginPath();
        ctx.arc(cx, cy, starR + 5, 0, Math.PI*2);
        ctx.stroke();
        ctx.shadowBlur = 0;

        ctx.fillStyle = "#f97316";
        ctx.font = "10px monospace";
        ctx.fillText("BLACK HOLE COLLAPSE", cx - 55, cy + starR + 30);
    } else if (supernovaExplode) {
        // Draw expanding plasma shell
        ctx.fillStyle = `rgba(239, 68, 68, ${Math.max(1.0 - (starR-50)/80.0, 0)})`;
        ctx.beginPath();
        ctx.arc(cx, cy, starR, 0, Math.PI*2);
        ctx.fill();

        ctx.strokeStyle = "#f43f5e";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cx, cy, starR, 0, Math.PI*2);
        ctx.stroke();

        ctx.fillStyle = "#ef4444";
        ctx.font = "10px monospace";
        ctx.fillText("SUPERNOVA IN PROGRESS", cx - 60, cy + 80);
    } else {
        // Draw Star Core
        ctx.fillStyle = starColor;
        
        if (dialG >= 0.005) {
            ctx.shadowColor = starColor;
            ctx.shadowBlur = starR * 0.6;
        }
        ctx.beginPath();
        ctx.arc(cx, cy, starR, 0, Math.PI*2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Draw gravity inward arrows
        ctx.strokeStyle = "#f43f5e"; // red inward
        ctx.lineWidth = 1.5;
        drawArrow(cx, cy - starR - 20, cx, cy - starR - 5);
        drawArrow(cx, cy + starR + 20, cx, cy + starR + 5);
        drawArrow(cx - starR - 20, cy, cx - starR - 5, cy);
        drawArrow(cx + starR + 20, cy, cx + starR + 5, cy);

        // Draw pressure outward arrows
        if (dialG >= 0.005) {
            ctx.strokeStyle = "#34d399"; // green outward
            drawArrow(cx, cy - starR + 5, cx, cy - starR + 18);
            drawArrow(cx, cy + starR - 5, cx, cy + starR - 18);
            drawArrow(cx - starR + 5, cy, cx - starR + 18, cy);
            drawArrow(cx + starR - 5, cy, cx + starR + 18, cy);
        }
    }

    ctx.fillStyle = "rgba(255,255,255,0.6)";
    ctx.font = "11px Space Grotesk, sans-serif";
    ctx.fillText(`P_out / P_in: ${ratio.toExponential(2)}`, x + 15, h - 15);
}

function drawArrow(x1, y1, x2, y2) {
    const headlen = 6; // length of head in pixels
    const dx = x2 - x1;
    const dy = y2 - y1;
    const angle = Math.atan2(dy, dx);
    
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.lineTo(x2 - headlen * Math.cos(angle - Math.PI / 6), y2 - headlen * Math.sin(angle - Math.PI / 6));
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headlen * Math.cos(angle + Math.PI / 6), y2 - headlen * Math.sin(angle + Math.PI / 6));
    ctx.stroke();
}
