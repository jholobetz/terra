(function() {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    let charges = [];
    let currentType = 1; // 1 for positive, -1 for negative
    const sphereRadius = 130;
    let selectedCharge = null;
    let isDragging = false;
    const k = 100000; // electrostatic constant

    // Set canvas size
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500; // Fixed height to prevent collapse
    }
    window.addEventListener('resize', resize);
    resize();

    // Inject specific controls for this simulation
    controls.innerHTML = `
        <div class="control-group">
            <p style="font-size: 0.8rem; margin-bottom: 10px; opacity: 0.8; color: #8892b0;">
                Click canvas to place a charge, or drag placed charges. Double-click to remove.
            </p>
            <div style="display: flex; gap: 8px; margin-bottom: 10px;">
                <button id="btn-pos" class="btn btn-primary" style="background: #ef4444; border:none; flex: 1; cursor: pointer;">Positive (+)</button>
                <button id="btn-neg" class="btn btn-primary" style="background: #3b82f6; border:none; flex: 1; cursor: pointer; opacity: 0.5;">Negative (-)</button>
            </div>
            <button id="btn-clear" class="btn btn-secondary" style="width: 100%; cursor: pointer;">Clear All Charges</button>
        </div>
        <div class="control-group" style="margin-top: 15px;">
            <label><input type="checkbox" id="show-crossings" checked> Highlight Flux Crossings</label>
        </div>
        <div class="stat-card" style="margin-top: 15px; text-align: center; border-top: 2px solid #a855f7; background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 6px;">
            <div style="font-size: 0.85rem; opacity: 0.8; color: #ccd6f6;">Net Electric Flux (ΦE)</div>
            <div id="q-enc-val" style="font-size: 2.2rem; font-weight: bold; color: #a855f7;">0</div>
            <div style="font-size: 0.75rem; opacity: 0.6; color: #8892b0;">
                Exiting lines: <span id="exiting-lines" style="color: #22c55e;">0</span><br>
                Entering lines: <span id="entering-lines" style="color: #ef4444;">0</span>
            </div>
        </div>
    `;

    const btnPos = document.getElementById('btn-pos');
    const btnNeg = document.getElementById('btn-neg');
    const btnClear = document.getElementById('btn-clear');
    const showCrossings = document.getElementById('show-crossings');
    const qEncVal = document.getElementById('q-enc-val');
    const exitingLinesVal = document.getElementById('exiting-lines');
    const enteringLinesVal = document.getElementById('entering-lines');

    // Preset charges (dipole inside/outside sphere)
    function init() {
        charges = [
            { x: canvas.width / 2 - 50, y: canvas.height / 2, type: 1, radius: 12 },
            { x: canvas.width / 2 + 50, y: canvas.height / 2, type: -1, radius: 12 }
        ];
    }
    init();

    btnPos.onclick = () => { currentType = 1; btnPos.style.opacity = 1; btnNeg.style.opacity = 0.5; };
    btnNeg.onclick = () => { currentType = -1; btnNeg.style.opacity = 1; btnPos.style.opacity = 0.5; };
    btnClear.onclick = () => { charges = []; };

    // Get Mouse positions
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    // Canvas click to add or drag
    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        selectedCharge = null;

        // Check if clicked near any charge
        for (let c of charges) {
            const dist = Math.sqrt((pos.x - c.x) ** 2 + (pos.y - c.y) ** 2);
            if (dist < c.radius + 6) {
                selectedCharge = c;
                isDragging = true;
                break;
            }
        }

        // If not dragging, place a charge
        if (!isDragging) {
            charges.push({
                x: pos.x,
                y: pos.y,
                type: currentType,
                radius: 12
            });
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging && selectedCharge) {
            const pos = getMousePos(e);
            selectedCharge.x = Math.max(selectedCharge.radius, Math.min(canvas.width - selectedCharge.radius, pos.x));
            selectedCharge.y = Math.max(selectedCharge.radius, Math.min(canvas.height - selectedCharge.radius, pos.y));
        }
    });

    canvas.addEventListener('mouseup', () => {
        isDragging = false;
        selectedCharge = null;
    });

    // Double click to remove charge
    canvas.addEventListener('dblclick', (e) => {
        const pos = getMousePos(e);
        charges = charges.filter(c => {
            const dist = Math.sqrt((pos.x - c.x) ** 2 + (pos.y - c.y) ** 2);
            return dist >= c.radius + 6;
        });
    });

    // Calculate E field vector E = (Ex, Ey) at point (x, y)
    function getElectricField(x, y) {
        let ex = 0;
        let ey = 0;
        for (let c of charges) {
            const dx = x - c.x;
            const dy = y - c.y;
            const r2 = dx * dx + dy * dy;
            const r = Math.sqrt(r2);
            if (r < c.radius) return { x: 0, y: 0 };
            const E = (k * c.type) / r2;
            ex += E * (dx / r);
            ey += E * (dy / r);
        }
        return { x: ex, y: ey };
    }

    function draw() {
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        let qEnc = 0;
        let exitingLinesCount = 0;
        let enteringLinesCount = 0;
        let intersectionPoints = [];

        // 1. Calculate enclosed charges
        charges.forEach(c => {
            const dist = Math.sqrt((c.x - cx) ** 2 + (c.y - cy) ** 2);
            if (dist < sphereRadius) {
                qEnc += c.type;
            }
        });

        // 2. Trace field lines and find circle crossings
        if (charges.length > 0) {
            const stepSize = 4;
            const maxSteps = 160;

            charges.forEach(c => {
                const numLines = 16;
                for (let i = 0; i < numLines; i++) {
                    const angle = (i * 2 * Math.PI) / numLines;
                    let px = c.x + (c.radius + 2) * Math.cos(angle);
                    let py = c.y + (c.radius + 2) * Math.sin(angle);
                    
                    // Trace forward for positive, backward for negative
                    const dir = c.type; 

                    ctx.strokeStyle = c.type > 0 ? 'rgba(239, 68, 68, 0.25)' : 'rgba(59, 130, 246, 0.25)';
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(px, py);

                    let steps = 0;
                    let prevDistFromCenter = Math.sqrt((px - cx) ** 2 + (py - cy) ** 2);

                    while (steps < maxSteps && px > 0 && px < canvas.width && py > 0 && py < canvas.height) {
                        const E = getElectricField(px, py);
                        const mag = Math.sqrt(E.x * E.x + E.y * E.y);
                        if (mag === 0) break;

                        // Move step along or against field direction
                        px += dir * (E.x / mag) * stepSize;
                        py += dir * (E.y / mag) * stepSize;

                        ctx.lineTo(px, py);

                        // Check intersection with Gaussian Surface
                        const currDistFromCenter = Math.sqrt((px - cx) ** 2 + (py - cy) ** 2);
                        
                        // Crossed from inside to outside, or outside to inside
                        if ((prevDistFromCenter < sphereRadius && currDistFromCenter >= sphereRadius) ||
                            (prevDistFromCenter >= sphereRadius && currDistFromCenter < sphereRadius)) {
                            
                            // Approximate intersection point
                            const theta = Math.atan2(py - cy, px - cx);
                            const ix = cx + sphereRadius * Math.cos(theta);
                            const iy = cy + sphereRadius * Math.sin(theta);

                            // Calculate Ex, Ey at intersection
                            const E_int = getElectricField(ix, iy);
                            const Emag = Math.sqrt(E_int.x * E_int.x + E_int.y * E_int.y);
                            
                            // Normal vector (outward)
                            const nx = Math.cos(theta);
                            const ny = Math.sin(theta);

                            if (Emag > 0) {
                                // Dot product E • n
                                const dot = (E_int.x / Emag) * nx + (E_int.y / Emag) * ny;
                                const isExiting = dot > 0;

                                if (isExiting) {
                                    exitingLinesCount++;
                                } else {
                                    enteringLinesCount++;
                                }

                                intersectionPoints.push({
                                    x: ix, y: iy,
                                    ex: E_int.x / Emag, ey: E_int.y / Emag,
                                    nx: nx, ny: ny,
                                    isExiting: isExiting
                                });
                            }
                        }

                        // Check if hit another charge
                        let hitCharge = false;
                        for (let n of charges) {
                            if (n !== c) {
                                const d = Math.sqrt((px - n.x) ** 2 + (py - n.y) ** 2);
                                if (d < n.radius) {
                                    hitCharge = true;
                                    break;
                                }
                            }
                        }

                        if (hitCharge) break;
                        prevDistFromCenter = currDistFromCenter;
                        steps++;
                    }
                    ctx.stroke();
                }
            });
        }

        // 3. Draw Gaussian Surface (The Sphere)
        ctx.beginPath();
        ctx.arc(cx, cy, sphereRadius, 0, Math.PI * 2);
        ctx.setLineDash([8, 4]);
        // Green color for surface, glowing
        ctx.strokeStyle = '#10b981';
        ctx.lineWidth = 2.5;
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Label Gaussian Surface
        ctx.fillStyle = '#10b981';
        ctx.font = 'bold 12px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('Gaussian Surface (dA)', cx, cy - sphereRadius - 15);

        // 4. Draw crossing points and vectors
        if (showCrossings.checked) {
            intersectionPoints.forEach(pt => {
                // Draw intersection dot
                ctx.fillStyle = pt.isExiting ? '#22c55e' : '#ef4444';
                ctx.beginPath();
                ctx.arc(pt.x, pt.y, 4, 0, Math.PI * 2);
                ctx.fill();

                // Draw local surface normal vector (dA) in green
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(pt.x, pt.y);
                ctx.lineTo(pt.x + pt.nx * 15, pt.y + pt.ny * 15);
                ctx.stroke();

                // Draw electric field vector (E)
                ctx.strokeStyle = '#a855f7';
                ctx.lineWidth = 1.5;
                ctx.beginPath();
                ctx.moveTo(pt.x, pt.y);
                ctx.lineTo(pt.x + pt.ex * 15, pt.y + pt.ey * 15);
                ctx.stroke();
            });
        }

        // 5. Draw Charge Particles
        charges.forEach(c => {
            // Check boundary indicator
            const dist = Math.sqrt((c.x - cx) ** 2 + (c.y - cy) ** 2);
            const isInside = dist < sphereRadius;

            // Highlight ring if inside Gaussian surface
            if (isInside) {
                ctx.strokeStyle = '#10b981';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(c.x, c.y, c.radius + 4, 0, Math.PI * 2);
                ctx.stroke();
            }

            ctx.beginPath();
            ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
            ctx.fillStyle = c.type > 0 ? '#ef4444' : '#3b82f6';
            ctx.fill();
            
            ctx.fillStyle = 'white';
            ctx.font = 'bold 14px sans-serif';
            ctx.textBaseline = 'middle';
            ctx.textAlign = 'center';
            ctx.fillText(c.type > 0 ? '+' : '−', c.x, c.y);
        });

        // Update UI
        qEncVal.innerText = qEnc > 0 ? `+${qEnc} q` : qEnc === 0 ? '0' : `${qEnc} q`;
        exitingLinesVal.innerText = `+${exitingLinesCount}`;
        enteringLinesVal.innerText = `-${enteringLinesCount}`;
        
        requestAnimationFrame(draw);
    }

    draw();
})();