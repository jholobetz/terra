document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group" style="display: flex; flex-direction: column; gap: 8px;">
            <button id="add-pos" class="btn btn-primary" style="background: #ef4444; border: none;">+ Add Positive Charge (+q)</button>
            <button id="add-neg" class="btn btn-primary" style="background: #3b82f6; border: none;">- Add Negative Charge (-q)</button>
            <button id="clear-btn" class="btn btn-secondary">Clear Charges</button>
        </div>
        <div class="control-group" style="margin-top: 15px;">
            <label><input type="checkbox" id="show-field-lines" checked> Trace Field Lines</label><br>
            <label><input type="checkbox" id="show-vector-grid" checked> Show Vector Field Grid</label><br>
            <label><input type="checkbox" id="show-equipotentials" checked> Show Equipotential Glow</label>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div style="font-size:0.75rem; color: #64748b;">
                • Drag charges to move them.<br>
                • Double-click a charge to remove it.<br>
                • Positive charges radiate lines outward, negative charges attract them.
            </div>
        </div>
    `;

    const addPosBtn = document.getElementById('add-pos');
    const addNegBtn = document.getElementById('add-neg');
    const clearBtn = document.getElementById('clear-btn');
    const showFieldLines = document.getElementById('show-field-lines');
    const showVectorGrid = document.getElementById('show-vector-grid');
    const showEquipotentials = document.getElementById('show-equipotentials');

    let charges = [];
    let selectedCharge = null;
    let isDragging = false;
    const k = 120000; // electrostatic constant in simulation units

    // Initialize with a dipole
    function init() {
        charges = [
            { x: canvas.width / 3, y: canvas.height / 2, q: 1, radius: 12 },
            { x: (2 * canvas.width) / 3, y: canvas.height / 2, q: -1, radius: 12 }
        ];
    }

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        if (charges.length === 0) {
            init();
        }
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    addPosBtn.onclick = () => {
        charges.push({
            x: Math.random() * (canvas.width - 60) + 30,
            y: Math.random() * (canvas.height - 60) + 30,
            q: 1.0,
            radius: 12
        });
    };

    addNegBtn.onclick = () => {
        charges.push({
            x: Math.random() * (canvas.width - 60) + 30,
            y: Math.random() * (canvas.height - 60) + 30,
            q: -1.0,
            radius: 12
        });
    };

    clearBtn.onclick = () => {
        charges = [];
    };

    // Mouse events for drag-and-drop
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        selectedCharge = null;

        // Check if clicked on a charge
        for (let c of charges) {
            const dist = Math.sqrt((pos.x - c.x) ** 2 + (pos.y - c.y) ** 2);
            if (dist < c.radius + 6) {
                selectedCharge = c;
                isDragging = true;
                break;
            }
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (isDragging && selectedCharge) {
            const pos = getMousePos(e);
            // Contain within canvas boundaries
            selectedCharge.x = Math.max(selectedCharge.radius, Math.min(canvas.width - selectedCharge.radius, pos.x));
            selectedCharge.y = Math.max(selectedCharge.radius, Math.min(canvas.height - selectedCharge.radius, pos.y));
        }
    });

    canvas.addEventListener('mouseup', () => {
        isDragging = false;
        selectedCharge = null;
    });

    canvas.addEventListener('mouseleave', () => {
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

    // Calculate electric field vector E = (Ex, Ey) at point (x, y)
    function getElectricField(x, y) {
        let ex = 0;
        let ey = 0;
        for (let c of charges) {
            const dx = x - c.x;
            const dy = y - c.y;
            const r2 = dx * dx + dy * dy;
            const r = Math.sqrt(r2);
            if (r < c.radius) {
                // Inside charge, field is zero or extremely small to avoid infinity
                return { x: 0, y: 0, v: 0 };
            }
            // E = k * q / r^2
            const E = (k * c.q) / r2;
            ex += E * (dx / r);
            ey += E * (dy / r);
        }
        return { x: ex, y: ey };
    }

    // Calculate electrical potential V at point (x, y)
    function getPotential(x, y) {
        let potential = 0;
        for (let c of charges) {
            const dx = x - c.x;
            const dy = y - c.y;
            const r = Math.sqrt(dx * dx + dy * dy);
            if (r < c.radius) continue;
            // V = k * q / r
            potential += (k * c.q * 0.05) / r;
        }
        return potential;
    }

    // Trace field lines from source charges
    function drawFieldLines() {
        if (charges.length === 0) return;

        ctx.lineWidth = 1.2;
        const stepSize = 4;
        const maxSteps = 200;

        charges.forEach(c => {
            // Field lines radiate out of positive charges, and trace backwards into negative charges
            if (c.q <= 0) return; // Only start trace from positive charges for simplicity

            const numLines = 16;
            for (let i = 0; i < numLines; i++) {
                const angle = (i * 2 * Math.PI) / numLines;
                let px = c.x + (c.radius + 2) * Math.cos(angle);
                let py = c.y + (c.radius + 2) * Math.sin(angle);

                ctx.strokeStyle = 'rgba(100, 255, 218, 0.4)';
                ctx.beginPath();
                ctx.moveTo(px, py);

                let steps = 0;
                let hitNegative = false;

                while (steps < maxSteps && px > 0 && px < canvas.width && py > 0 && py < canvas.height) {
                    const E = getElectricField(px, py);
                    const mag = Math.sqrt(E.x * E.x + E.y * E.y);

                    if (mag === 0) break;

                    // Step along E field direction
                    px += (E.x / mag) * stepSize;
                    py += (E.y / mag) * stepSize;

                    ctx.lineTo(px, py);

                    // Check if we hit a negative charge
                    for (let n of charges) {
                        if (n.q < 0) {
                            const d = Math.sqrt((px - n.x) ** 2 + (py - n.y) ** 2);
                            if (d < n.radius) {
                                hitNegative = true;
                                break;
                            }
                        }
                    }

                    if (hitNegative) break;
                    steps++;
                }
                ctx.stroke();

                // Draw tiny arrowheads at midpoint of the line to show direction
                if (steps > 20) {
                    // Re-calculate coordinate at mid-step
                    let mx = c.x + (c.radius + 2) * Math.cos(angle);
                    let my = c.y + (c.radius + 2) * Math.sin(angle);
                    const midStep = Math.floor(steps * 0.45);
                    for (let s = 0; s < midStep; s++) {
                        const E = getElectricField(mx, my);
                        const mag = Math.sqrt(E.x * E.x + E.y * E.y);
                        if (mag === 0) break;
                        mx += (E.x / mag) * stepSize;
                        my += (E.y / mag) * stepSize;
                    }

                    const E = getElectricField(mx, my);
                    const mag = Math.sqrt(E.x * E.x + E.y * E.y);
                    if (mag > 0) {
                        const dx = E.x / mag;
                        const dy = E.y / mag;
                        
                        // Rotate arrow head
                        ctx.fillStyle = 'rgba(100, 255, 218, 0.7)';
                        ctx.beginPath();
                        ctx.moveTo(mx, my);
                        ctx.lineTo(mx - dx * 8 + dy * 4, my - dy * 8 - dx * 4);
                        ctx.lineTo(mx - dx * 8 - dy * 4, my - dy * 8 + dx * 4);
                        ctx.closePath();
                        ctx.fill();
                    }
                }
            }
        });
    }

    // Draw Vector Field Grid (small arrow vectors)
    function drawVectorGrid() {
        const step = 28;
        ctx.lineWidth = 1.2;

        for (let x = step / 2; x < canvas.width; x += step) {
            for (let y = step / 2; y < canvas.height; y += step) {
                // Don't draw arrows too close to charges
                let nearCharge = false;
                for (let c of charges) {
                    if (Math.sqrt((x - c.x) ** 2 + (y - c.y) ** 2) < c.radius + 10) {
                        nearCharge = true;
                        break;
                    }
                }
                if (nearCharge) continue;

                const E = getElectricField(x, y);
                const mag = Math.sqrt(E.x * E.x + E.y * E.y);

                if (mag > 0.1) {
                    const arrowLen = Math.min(16, 4 + mag * 0.02);
                    const dx = (E.x / mag) * arrowLen;
                    const dy = (E.y / mag) * arrowLen;

                    // Color based on strength (opacity)
                    const opacity = Math.min(0.7, 0.15 + mag * 0.003);
                    ctx.strokeStyle = `rgba(165, 180, 252, ${opacity})`;
                    ctx.beginPath();
                    ctx.moveTo(x - dx / 2, y - dy / 2);
                    ctx.lineTo(x + dx / 2, y + dy / 2);
                    ctx.stroke();

                    // Arrowhead
                    if (arrowLen > 6) {
                        ctx.fillStyle = `rgba(165, 180, 252, ${opacity})`;
                        const hx = x + dx / 2;
                        const hy = y + dy / 2;
                        const udx = E.x / mag;
                        const udy = E.y / mag;
                        ctx.beginPath();
                        ctx.moveTo(hx, hy);
                        ctx.lineTo(hx - udx * 4 + udy * 2, hy - udy * 4 - udx * 2);
                        ctx.lineTo(hx - udx * 4 - udy * 2, hy - udy * 4 + udx * 2);
                        ctx.closePath();
                        ctx.fill();
                    }
                }
            }
        }
    }

    // Render Equipotential Potential Glow (pixel-level map of potential V)
    function drawEquipotentialGlow() {
        const resolution = 4; // grid cell size
        for (let x = 0; x < canvas.width; x += resolution) {
            for (let y = 0; y < canvas.height; y += resolution) {
                const V = getPotential(x, y);
                const absV = Math.abs(V);
                if (absV > 0.8) {
                    const opacity = Math.min(0.2, absV * 0.005);
                    if (V > 0) {
                        // Positive potential: Red glow
                        ctx.fillStyle = `rgba(239, 68, 68, ${opacity})`;
                    } else {
                        // Negative potential: Blue glow
                        ctx.fillStyle = `rgba(59, 130, 246, ${opacity})`;
                    }
                    ctx.fillRect(x, y, resolution, resolution);
                }
            }
        }
    }

    // Render loop
    function draw() {
        // Clear screen
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // 1. Draw Equipotential potential background
        if (showEquipotentials.checked) {
            drawEquipotentialGlow();
        }

        // 2. Draw Vector field grid
        if (showVectorGrid.checked) {
            drawVectorGrid();
        }

        // 3. Draw continuous field lines
        if (showFieldLines.checked) {
            drawFieldLines();
        }

        // 4. Draw charge boundary disks (+ and -)
        charges.forEach(c => {
            // outer ring
            ctx.strokeStyle = c.q > 0 ? '#ef4444' : '#3b82f6';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.arc(c.x, c.y, c.radius + 3, 0, Math.PI * 2);
            ctx.stroke();

            // inner circle
            ctx.fillStyle = c.q > 0 ? '#f87171' : '#60a5fa';
            ctx.beginPath();
            ctx.arc(c.x, c.y, c.radius, 0, Math.PI * 2);
            ctx.fill();

            // Sign text (+ or -)
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 15px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(c.q > 0 ? '+' : '−', c.x, c.y);
        });

        requestAnimationFrame(draw);
    }

    // Start simulation loop
    draw();
});
