document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Muzzle Velocity (v₀): <span id="v-val" class="math-value">55</span> m/s</label>
            <input type="range" id="v-slider" min="15" max="100" value="55" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Cannon Launch Angle (θ): <span id="a-val" class="math-value">45</span>°</label>
            <input type="range" id="angle-slider" min="0" max="90" value="45" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Air Resistance (Cd): <span id="d-val" class="math-value">0.02</span></label>
            <input type="range" id="d-slider" min="0.00" max="0.10" step="0.005" value="0.02" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Cross Wind: <span id="w-val" class="math-value">0.0</span> m/s</label>
            <input type="range" id="w-slider" min="-1.5" max="1.5" step="0.1" value="0.0" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label><input type="checkbox" id="show-vectors" checked> Show Force Vectors (F_vec)</label>
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="launch-btn" class="btn btn-primary" style="flex: 1;">Fire Cannon!</button>
            <button id="clear-btn" class="btn btn-secondary">Clear Trails</button>
        </div>
    `;

    const vSlider = document.getElementById('v-slider');
    const angleSlider = document.getElementById('angle-slider');
    const dSlider = document.getElementById('d-slider');
    const wSlider = document.getElementById('w-slider');
    const showVectorsCheck = document.getElementById('show-vectors');
    const launchBtn = document.getElementById('launch-btn');
    const clearBtn = document.getElementById('clear-btn');

    let v0 = 55;
    let angle = 45;
    let drag = 0.02;
    let wind = 0.0;
    let g = 9.81; // standard gravity

    let projectiles = [];
    let particles = []; // muzzle flash and explosion debris
    let cameraShake = 0;
    let lastTimestamp = performance.now();

    // Cannon base position
    const cannonPos = { x: 70, y: 0 }; // y set in resize

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        cannonPos.y = canvas.height - 60;
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    vSlider.oninput = () => { v0 = parseInt(vSlider.value); document.getElementById('v-val').innerText = v0; };
    angleSlider.oninput = () => { angle = parseInt(angleSlider.value); document.getElementById('a-val').innerText = angle; };
    dSlider.oninput = () => { drag = parseFloat(dSlider.value); document.getElementById('d-val').innerText = drag; };
    wSlider.oninput = () => { wind = parseFloat(wSlider.value); document.getElementById('w-val').innerText = wind; };
    clearBtn.onclick = () => { projectiles = []; particles = []; };

    // Fire!
    launchBtn.onclick = () => {
        const rad = (angle * Math.PI) / 180;
        const barrelLen = 42;
        
        // Muzzle coordinates
        const mx = cannonPos.x + Math.cos(rad) * barrelLen;
        const my = cannonPos.y - Math.sin(rad) * barrelLen;

        // Velocity vector scale
        const scale = 0.23; 
        projectiles.push({
            x: mx,
            y: my,
            vx: v0 * Math.cos(rad) * scale,
            vy: -v0 * Math.sin(rad) * scale,
            radius: 7,
            color: '#e2e8f0', // bright shell
            path: [],
            active: true
        });

        // Trigger camera shake
        cameraShake = 7.0;

        // Spawn muzzle flash smoke particles
        for (let i = 0; i < 15; i++) {
            const pAngle = rad + (Math.random() - 0.5) * 0.4;
            const pSpeed = (2 + Math.random() * 5);
            particles.push({
                x: mx, y: my,
                vx: pSpeed * Math.cos(pAngle),
                vy: -pSpeed * Math.sin(pAngle),
                radius: 3 + Math.random() * 6,
                color: `rgba(249, 115, 22, ${0.4 + Math.random() * 0.6})`, // orange/grey fire
                age: 0,
                maxAge: 15 + Math.random() * 10,
                type: 'smoke'
            });
        }
    };

    // Trigger floor impact explosion debris
    function triggerExplosion(ex, ey) {
        for (let i = 0; i < 18; i++) {
            const pAngle = Math.random() * Math.PI; // bounce upwards
            const pSpeed = (1 + Math.random() * 4);
            particles.push({
                x: ex, y: ey,
                vx: pSpeed * Math.cos(pAngle),
                vy: -pSpeed * Math.sin(pAngle),
                radius: 2 + Math.random() * 3,
                color: `rgba(251, 146, 60, ${0.8 + Math.random() * 0.2})`, // bright spark
                age: 0,
                maxAge: 20 + Math.random() * 15,
                type: 'spark'
            });
        }
    }

    // Main animation and physics loop
    function loop(timestamp) {
        // Enforce time-delta step
        const dt = Math.min(0.04, (timestamp - lastTimestamp) / 1000) * 60;
        lastTimestamp = timestamp;

        if (cameraShake > 0.1) {
            cameraShake *= 0.88; // decay
        } else {
            cameraShake = 0;
        }

        // 1. Update active projectiles
        for (let p of projectiles) {
            if (!p.active) continue;

            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy) || 0.001;
            
            // Forces calculations (scaled down for canvas size representation)
            // Drag force opposite to velocity
            const fDragX = -drag * speed * p.vx * 0.08;
            const fDragY = -drag * speed * p.vy * 0.08;
            
            // Gravity force (pointing down)
            const fGravY = g * 0.02;

            // Wind force (horizontal)
            const fWindX = wind * 0.02;

            // Save force vectors for drawing
            p.fDrag = { x: fDragX, y: fDragY };
            p.fGrav = { x: 0, y: fGravY };
            p.fWind = { x: fWindX, y: 0 };
            p.fNet = { x: fDragX + fWindX, y: fDragY + fGravY };

            // Integrate Velocity Verlet
            p.vx += (fDragX + fWindX) * dt;
            p.vy += (fDragY + fGravY) * dt;

            p.x += p.vx * dt;
            p.y += p.vy * dt;

            // Save trail
            p.path.push({ x: p.x, y: p.y });
            if (p.path.length > 300) p.path.shift();

            // Check floor collision
            if (p.y >= canvas.height - 60) {
                p.y = canvas.height - 60;
                p.active = false;
                triggerExplosion(p.x, p.y);
            }
        }

        // 2. Update particle sparks and smoke
        for (let i = particles.length - 1; i >= 0; i--) {
            const pt = particles[i];
            pt.x += pt.vx;
            pt.y += pt.vy;
            pt.age++;

            if (pt.type === 'spark') {
                pt.vy += 0.15; // sparks experience gravity
            }

            if (pt.age >= pt.maxAge) {
                particles.splice(i, 1);
            }
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Save context and apply camera shake offset
        ctx.save();
        if (cameraShake > 0) {
            const shakeX = (Math.random() - 0.5) * cameraShake;
            const shakeY = (Math.random() - 0.5) * cameraShake;
            ctx.translate(shakeX, shakeY);
        }

        // Deep slate background
        ctx.fillStyle = '#0a0f1d';
        ctx.fillRect(-20, -20, canvas.width + 40, canvas.height + 40);

        // Draw ground / floor landscape
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(-20, canvas.height - 60, canvas.width + 40, 60);

        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(0, canvas.height - 60);
        ctx.lineTo(canvas.width, canvas.height - 60);
        ctx.stroke();

        // 1. Draw projectile trails
        for (let p of projectiles) {
            if (p.path.length < 2) continue;
            ctx.lineWidth = 2.0;
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.45)'; // cyan trail
            ctx.beginPath();
            ctx.moveTo(p.path[0].x, p.path[0].y);
            for (let i = 1; i < p.path.length; i++) {
                ctx.lineTo(p.path[i].x, p.path[i].y);
            }
            ctx.stroke();
        }

        // 2. Draw flying shell bobs
        for (let p of projectiles) {
            if (!p.active) continue;

            // Draw glowing core
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#64ffda';
            ctx.fillStyle = p.color;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0; // reset

            // Draw educational physics force vector diagram overlay
            if (showVectorsCheck.checked && p.fNet) {
                const vectorScale = 450; // amplify for canvas visibility
                ctx.lineWidth = 2.0;

                // A. Gravity vector Fg (red, down)
                drawArrow(p.x, p.y, p.x, p.y + p.fGrav.y * vectorScale, '#ef4444', 'Fg');

                // B. Drag vector Fd (blue, opposite velocity)
                if (drag > 0) {
                    drawArrow(p.x, p.y, p.x + p.fDrag.x * vectorScale, p.y + p.fDrag.y * vectorScale, '#3b82f6', 'Fd');
                }

                // C. Wind vector Fw (orange, horizontal)
                if (Math.abs(wind) > 0) {
                    drawArrow(p.x, p.y, p.x + p.fWind.x * vectorScale, p.y, '#f97316', 'Fw');
                }

                // D. Net resulting acceleration vector (green)
                drawArrow(p.x, p.y, p.x + p.fNet.x * vectorScale, p.y + p.fNet.y * vectorScale, '#22c55e', 'Fnet');
            }
        }

        // Draw vector arrow helper function
        function drawArrow(x1, y1, x2, y2, color, label) {
            const dx = x2 - x1;
            const dy = y2 - y1;
            const len = Math.sqrt(dx * dx + dy * dy);
            if (len < 6) return;

            ctx.strokeStyle = color;
            ctx.fillStyle = color;
            
            // Draw line
            ctx.beginPath();
            ctx.moveTo(x1, y1);
            ctx.lineTo(x2, y2);
            ctx.stroke();

            // Arrow head
            const udx = dx / len;
            const udy = dy / len;
            ctx.beginPath();
            ctx.moveTo(x2, y2);
            ctx.lineTo(x2 - udx * 7 + udy * 3.5, y2 - udy * 7 - udx * 3.5);
            ctx.lineTo(x2 - udx * 7 - udy * 3.5, y2 - udy * 7 + udx * 3.5);
            ctx.closePath();
            ctx.fill();

            // Draw label text
            ctx.font = '9px monospace';
            ctx.fillText(label, x2 + udx * 5, y2 + udy * 5 + 3);
        }

        // 3. Draw explosion/muzzle particles
        for (let pt of particles) {
            ctx.fillStyle = pt.color;
            if (pt.type === 'smoke') {
                // Fading cloud
                const alpha = 1.0 - (pt.age / pt.maxAge);
                ctx.fillStyle = `rgba(249, 115, 22, ${alpha * 0.4})`; // fade orange smoke
            }
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, pt.radius, 0, Math.PI * 2);
            ctx.fill();
        }

        // 4. Draw Cannon / Tank visual representation at bottom-left
        const rad = (angle * Math.PI) / 180;
        const barrelLen = 42;
        const barrelEnd = {
            x: cannonPos.x + Math.cos(rad) * barrelLen,
            y: cannonPos.y - Math.sin(rad) * barrelLen
        };

        // Draw Tank wheels / tread (3 dark grey circles)
        ctx.fillStyle = '#334155';
        ctx.fillRect(cannonPos.x - 45, cannonPos.y, 75, 12);
        
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 1.5;
        for (let i = -3; i <= 2; i++) {
            ctx.beginPath();
            ctx.arc(cannonPos.x - 35 + i * 14, cannonPos.y + 8, 5, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
        }

        // Draw Tank body cabin (grey bevel block)
        ctx.fillStyle = '#64748b';
        ctx.strokeStyle = '#94a3b8';
        ctx.beginPath();
        ctx.moveTo(cannonPos.x - 35, cannonPos.y);
        ctx.lineTo(cannonPos.x + 25, cannonPos.y);
        ctx.lineTo(cannonPos.x + 15, cannonPos.y - 18);
        ctx.lineTo(cannonPos.x - 25, cannonPos.y - 18);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Draw rotating turret dome
        ctx.fillStyle = '#475569';
        ctx.beginPath();
        ctx.arc(cannonPos.x, cannonPos.y - 16, 15, Math.PI, 0); // half circle
        ctx.fill();

        // Draw rotating cannon barrel
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 7.5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(cannonPos.x, cannonPos.y - 16);
        ctx.lineTo(barrelEnd.x, barrelEnd.y);
        ctx.stroke();
        ctx.lineCap = 'butt'; // reset

        // Restore context from camera shake
        ctx.restore();
    }

    // Start loop
    requestAnimationFrame(loop);
});
