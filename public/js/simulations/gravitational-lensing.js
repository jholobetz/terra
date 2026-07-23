document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Inject custom controls
    controls.innerHTML = `
        <div class="control-group">
            <label>Black Hole Mass (M): <span id="m-val" class="math-value">30</span></label>
            <input type="range" id="m-slider" min="15" max="55" step="1" value="30" style="width: 100%">
        </div>
        <div class="control-group" style="margin-top: 10px;">
            <label>Visualization Mode:</label><br>
            <select id="viz-mode" style="width: 100%; padding: 6px; background: #0f172a; color: #f8fafc; border: 1px solid #334155; border-radius: 4px; margin-top: 4px;">
                <option value="grid">Spacetime Coordinate Grid</option>
                <option value="starfield">Starfield (Double Images)</option>
            </select>
        </div>
        <div class="control-group" style="margin-top: 15px; display: flex; gap: 10px;">
            <button id="reset-sim" class="btn btn-secondary" style="width: 100%">Reset Simulation</button>
        </div>
        <div class="physics-readout" style="margin-top: 15px; font-size: 0.85rem; color: #8892b0; border-top: 1px solid #2d3748; padding-top: 10px;">
            <div>Event Horizon (Rs): <span id="rs-val" class="math-value">60</span> px</div>
            <div>Photon Sphere (Rph): <span id="rph-val" class="math-value">90</span> px</div>
            <div>Einstein Radius (RE): <span id="re-val" class="math-value">110</span> px</div>
            <div style="font-size: 0.75rem; color: #5f6c8d; margin-top: 8px;">
                • Left Panel: Side view of photon trajectories (GR geodesics) shot from the left.<br>
                • Right Panel: Drag the red source circle to see it lens into two images and form Einstein rings.
            </div>
        </div>
    `;

    const mSlider = document.getElementById('m-slider');
    const vizModeSelect = document.getElementById('viz-mode');
    const mVal = document.getElementById('m-val');
    const rsVal = document.getElementById('rs-val');
    const rphVal = document.getElementById('rph-val');
    const reVal = document.getElementById('re-val');
    const resetSimBtn = document.getElementById('reset-sim');

    let M = 30; // Mass scaling parameter
    let rs = 2 * M;
    let rph = 3 * M;
    let re = Math.sqrt(4 * M * 100); // Einstein radius scaling
    let vizMode = 'grid';
    let isPlaying = true;

    // Interactive lensed source
    let source = { x: 0, y: 0, radius: 10, isDragging: false };
    let stars = [];

    // Left panel light rays definition
    let rays = [];

    // Initialize simulation parameters and objects
    function init() {
        rs = 2 * M;
        rph = 1.5 * rs; // 3 * M
        re = Math.sqrt(4 * M * 100); // RE = sqrt(4GM * D) in pixels

        rsVal.innerText = Math.round(rs);
        rphVal.innerText = Math.round(rph);
        reVal.innerText = Math.round(re);

        const cxRight = (3 * canvas.width) / 4;
        const cyRight = canvas.height / 2;

        // Reset interactive source
        source.x = cxRight + 70;
        source.y = cyRight - 50;
        source.isDragging = false;

        // Generate stars for right panel background
        stars = [];
        for (let i = 0; i < 180; i++) {
            // Distribute stars randomly on the right panel
            const rx = cxRight + (Math.random() - 0.5) * (canvas.width / 2 - 40);
            const ry = cyRight + (Math.random() - 0.5) * (canvas.height - 40);
            
            // Source coordinates relative to right center
            stars.push({
                sx: rx - cxRight,
                sy: ry - cyRight,
                brightness: 0.3 + Math.random() * 0.7,
                size: 1 + Math.random() * 1.5
            });
        }

        // Initialize left panel photon rays
        initRays();
    }

    // Left Panel: side-view photon geodesics initialization
    function initRays() {
        rays = [];
        const cxLeft = canvas.width / 4;
        const cyLeft = canvas.height / 2;

        // Spawn 15 parallel rays on the left side
        const numRays = 13;
        for (let i = 0; i < numRays; i++) {
            // Spacing above and below horizontal centerline (impact parameters)
            const b = (i - (numRays - 1) / 2) * 16;
            if (b === 0) continue; // skip exact direct hit

            rays.push({
                path: [{ x: 10, y: cyLeft + b }],
                x: 10,
                y: cyLeft + b,
                vx: 1.0, // moving right
                vy: 0.0,
                ax: 0,
                ay: 0,
                b: b,
                active: true,
                swallowed: false
            });
        }
    }

    // Resize canvas
    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        init();
    }
    window.addEventListener('resize', resize);
    resize();

    // Event listeners
    mSlider.oninput = () => {
        M = parseInt(mSlider.value);
        mVal.innerText = M;
        rs = 2 * M;
        rph = 1.5 * rs;
        re = Math.sqrt(4 * M * 100);

        rsVal.innerText = Math.round(rs);
        rphVal.innerText = Math.round(rph);
        reVal.innerText = Math.round(re);

        initRays();
    };

    vizModeSelect.onchange = () => {
        vizMode = vizModeSelect.value;
    };

    resetSimBtn.onclick = () => {
        init();
    };

    // Mouse events on lensed source (Right Panel)
    function getMousePos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    canvas.addEventListener('mousedown', (e) => {
        const pos = getMousePos(e);
        const dist = Math.sqrt((pos.x - source.x) ** 2 + (pos.y - source.y) ** 2);
        if (dist < source.radius + 10) {
            source.isDragging = true;
        }
    });

    canvas.addEventListener('mousemove', (e) => {
        if (source.isDragging) {
            const pos = getMousePos(e);
            const cxRight = (3 * canvas.width) / 4;
            // Bound inside right panel
            source.x = Math.max(canvas.width / 2 + 20, Math.min(canvas.width - 20, pos.x));
            source.y = Math.max(20, Math.min(canvas.height - 20, pos.y));
        }
    });

    canvas.addEventListener('mouseup', () => {
        source.isDragging = false;
    });

    canvas.addEventListener('mouseleave', () => {
        source.isDragging = false;
    });

    // Relativistic Ray Integration for Left Panel
    // Uses post-Newtonian Cartesian GR photon bending acceleration:
    // a = - (2M/r^3 + 3M*L^2/r^5) * r_vec
    function stepRays() {
        const cxLeft = canvas.width / 4;
        const cyLeft = canvas.height / 2;
        const dt = 1.4; // integration step

        for (let ray of rays) {
            if (!ray.active) continue;

            const dx = ray.x - cxLeft;
            const dy = ray.y - cyLeft;
            const r2 = dx * dx + dy * dy;
            const r = Math.sqrt(r2);

            // 1. Swallowed check (within event horizon)
            if (r < rs) {
                ray.active = false;
                ray.swallowed = true;
                continue;
            }

            // 2. Offscreen check
            if (ray.x > canvas.width / 2 || ray.x < 0 || ray.y < 0 || ray.y > canvas.height) {
                ray.active = false;
                continue;
            }

            // 3. Post-Newtonian GR acceleration
            const L = dx * ray.vy - dy * ray.vx; // angular momentum L
            const accelMag = (2 * M) / (r2 * r) + (3 * M * L * L) / (r2 * r2 * r);
            
            ray.ax = -accelMag * dx;
            ray.ay = -accelMag * dy;

            // 4. Integrate position & velocity (Velocity Verlet approximation)
            ray.x += ray.vx * dt + 0.5 * ray.ax * dt * dt;
            ray.y += ray.vy * dt + 0.5 * ray.ay * dt * dt;

            ray.vx += ray.ax * dt;
            ray.vy += ray.ay * dt;

            // Normalize velocity to keep speed of light (c = 1) constant
            const vMag = Math.sqrt(ray.vx * ray.vx + ray.vy * ray.vy);
            if (vMag > 0) {
                ray.vx /= vMag;
                ray.vy /= vMag;
            }

            // 5. Save path point
            ray.path.push({ x: ray.x, y: ray.y });
            if (ray.path.length > 500) {
                ray.path.shift();
            }
        }
    }

    // Main render and physics loop
    function loop(timestamp) {
        if (isPlaying) {
            stepRays();
        }

        draw();
        requestAnimationFrame(loop);
    }

    function draw() {
        // Deep space background
        ctx.fillStyle = '#05070f';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const cxLeft = canvas.width / 4;
        const cyLeft = canvas.height / 2;
        const cxRight = (3 * canvas.width) / 4;
        const cyRight = canvas.height / 2;

        // ==========================================
        // LEFT PANEL: Relativistic Geodesic Paths
        // ==========================================
        
        // Draw Left Panel boundaries
        ctx.fillStyle = 'rgba(10, 15, 30, 0.3)';
        ctx.fillRect(0, 0, canvas.width / 2, canvas.height);

        // Draw Left Panel Labels
        ctx.fillStyle = '#94a3b8';
        ctx.font = 'bold 13px monospace';
        ctx.textAlign = 'left';
        ctx.fillText('Photon Geodesic Paths (Side View)', 15, 25);

        // Draw Photon Sphere (Dashed orange ring)
        ctx.strokeStyle = 'rgba(249, 115, 22, 0.45)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.arc(cxLeft, cyLeft, rph, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);
        
        ctx.fillStyle = 'rgba(249, 115, 22, 0.8)';
        ctx.font = '9px monospace';
        ctx.fillText('Photon Sphere (3M)', cxLeft - 45, cyLeft - rph - 6);

        // Draw Event Horizon Shadow (Black circle)
        ctx.fillStyle = '#000000';
        ctx.shadowBlur = 15;
        ctx.shadowColor = 'rgba(0,0,0,1)';
        ctx.beginPath();
        ctx.arc(cxLeft, cyLeft, rs, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0; // reset

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(cxLeft, cyLeft, rs, 0, Math.PI * 2);
        ctx.stroke();

        ctx.fillStyle = '#ffffff';
        ctx.font = '9px monospace';
        ctx.fillText('Event Horizon (2M)', cxLeft - 45, cyLeft - rs - 6);

        // Draw Geodesic ray trajectories
        for (let ray of rays) {
            if (ray.path.length < 2) continue;

            // Draw line trail
            ctx.beginPath();
            ctx.moveTo(ray.path[0].x, ray.path[0].y);
            for (let i = 1; i < ray.path.length; i++) {
                ctx.lineTo(ray.path[i].x, ray.path[i].y);
            }
            
            // Style based on state
            if (ray.swallowed) {
                ctx.strokeStyle = 'rgba(220, 38, 38, 0.55)'; // Red for swallowed photons
                ctx.lineWidth = 1.5;
            } else {
                ctx.strokeStyle = 'rgba(34, 211, 238, 0.65)'; // Cyan for escaping photons
                ctx.lineWidth = 1.5;
            }
            ctx.stroke();

            // Draw active photon head dot
            if (ray.active) {
                ctx.fillStyle = '#22d3ee';
                ctx.beginPath();
                ctx.arc(ray.x, ray.y, 3.5, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // ==========================================
        // RIGHT PANEL: Observer's Lensed View
        // ==========================================
        
        ctx.fillStyle = 'rgba(5, 7, 15, 0.5)';
        ctx.fillRect(canvas.width / 2, 0, canvas.width / 2, canvas.height);

        // Draw Panel Label
        ctx.fillStyle = '#94a3b8';
        ctx.textAlign = 'left';
        ctx.font = 'bold 13px monospace';
        ctx.fillText("Observer's Lensed View (Front)", canvas.width / 2 + 15, 25);

        // Draw Einstein Ring boundary helper (very faint dashed green circle)
        ctx.strokeStyle = 'rgba(16, 185, 129, 0.12)';
        ctx.lineWidth = 1;
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.arc(cxRight, cyRight, re, 0, Math.PI * 2);
        ctx.stroke();
        ctx.setLineDash([]);

        // RENDER METHOD: Einstein lensing equation mapping
        // Source pos: s_vec, Apparent pos: r_vec
        // r^2 - s*r - RE^2 = 0 => r = (s + sqrt(s^2 + 4RE^2)) / 2
        function lensCoordinates(sx, sy) {
            const s = Math.sqrt(sx * sx + sy * sy);
            if (s === 0) {
                // Perfect singularity align yields Einstein Ring
                return [
                    { x: cxRight + re, y: cyRight, mag: 1 },
                    { x: cxRight - re, y: cyRight, mag: 1 }
                ];
            }

            // Image 1 (Outer, positive parity)
            const r1 = (s + Math.sqrt(s * s + 4 * re * re)) / 2;
            const x1 = cxRight + (sx / s) * r1;
            const y1 = cyRight + (sy / s) * r1;
            const mag1 = 1 / (1 - Math.pow(re / r1, 4));

            // Image 2 (Inner, negative parity, opposite side)
            const r2 = (s - Math.sqrt(s * s + 4 * re * re)) / 2; // negative
            const x2 = cxRight + (sx / s) * r2;
            const y2 = cyRight + (sy / s) * r2;
            const mag2 = 1 / (Math.pow(re / r2, 4) - 1);

            return [
                { x: x1, y: y1, mag: Math.min(5, Math.abs(mag1)) },
                { x: x2, y: y2, mag: Math.min(5, Math.abs(mag2)) }
            ];
        }

        // Draw coordinates grid mode
        if (vizMode === 'grid') {
            ctx.lineWidth = 1;
            // Draw lensed concentric rings
            ctx.strokeStyle = 'rgba(139, 92, 246, 0.2)'; // purple grid
            
            const stepRad = 25;
            for (let rSrc = stepRad; rSrc <= 160; rSrc += stepRad) {
                ctx.beginPath();
                // Sweep angle
                for (let a = 0; a <= 2 * Math.PI + 0.05; a += 0.05) {
                    const sx = rSrc * Math.cos(a);
                    const sy = rSrc * Math.sin(a);
                    const imgs = lensCoordinates(sx, sy);
                    
                    if (a === 0) ctx.moveTo(imgs[0].x, imgs[0].y);
                    else ctx.lineTo(imgs[0].x, imgs[0].y);
                }
                ctx.stroke();

                // Draw inner images circle sweep (if outside horizon shadow)
                ctx.beginPath();
                for (let a = 0; a <= 2 * Math.PI + 0.05; a += 0.05) {
                    const sx = rSrc * Math.cos(a);
                    const sy = rSrc * Math.sin(a);
                    const imgs = lensCoordinates(sx, sy);
                    
                    // Don't draw inner image if swallowed by black hole shadow
                    const innerD = Math.sqrt((imgs[1].x - cxRight) ** 2 + (imgs[1].y - cyRight) ** 2);
                    if (innerD > rs - 2) {
                        if (a === 0) ctx.moveTo(imgs[1].x, imgs[1].y);
                        else ctx.lineTo(imgs[1].x, imgs[1].y);
                    }
                }
                ctx.stroke();
            }

            // Draw lensed radial rays
            const numRays = 12;
            for (let i = 0; i < numRays; i++) {
                const a = (i * 2 * Math.PI) / numRays;
                const cosA = Math.cos(a);
                const sinA = Math.sin(a);

                // Outer image ray line
                ctx.beginPath();
                for (let rSrc = 10; rSrc <= 200; rSrc += 4) {
                    const imgs = lensCoordinates(rSrc * cosA, rSrc * sinA);
                    if (rSrc === 10) ctx.moveTo(imgs[0].x, imgs[0].y);
                    else ctx.lineTo(imgs[0].x, imgs[0].y);
                }
                ctx.stroke();

                // Inner image ray line
                ctx.beginPath();
                for (let rSrc = 10; rSrc <= 200; rSrc += 4) {
                    const imgs = lensCoordinates(rSrc * cosA, rSrc * sinA);
                    const innerD = Math.sqrt((imgs[1].x - cxRight) ** 2 + (imgs[1].y - cyRight) ** 2);
                    if (innerD > rs - 2) {
                        if (rSrc === 10) ctx.moveTo(imgs[1].x, imgs[1].y);
                        else ctx.lineTo(imgs[1].x, imgs[1].y);
                    }
                }
                ctx.stroke();
            }
        } 
        // Draw starfield mode
        else if (vizMode === 'starfield') {
            for (let star of stars) {
                const imgs = lensCoordinates(star.sx, star.sy);

                // Draw outer image
                ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness})`;
                const size1 = Math.max(1, star.size * Math.sqrt(imgs[0].mag));
                ctx.beginPath();
                ctx.arc(imgs[0].x, imgs[0].y, size1, 0, Math.PI * 2);
                ctx.fill();

                // Draw inner image (if outside black hole shadow)
                const d2 = Math.sqrt((imgs[1].x - cxRight) ** 2 + (imgs[1].y - cyRight) ** 2);
                if (d2 > rs) {
                    ctx.fillStyle = `rgba(255, 255, 255, ${star.brightness * 0.7})`; // slightly dimmer
                    const size2 = Math.max(0.8, star.size * Math.sqrt(imgs[1].mag));
                    ctx.beginPath();
                    ctx.arc(imgs[1].x, imgs[1].y, size2, 0, Math.PI * 2);
                    ctx.fill();
                }
            }
        }

        // Draw central Event Horizon Shadow (observer's point of view)
        ctx.fillStyle = '#000000';
        ctx.beginPath();
        // A black hole's visual shadow is actually larger than its event horizon due to gravitational lensing!
        // The critical impact parameter is b_crit = 3*sqrt(3) * M ≈ 5.19 * M ≈ 2.6 * Rs.
        // Thus, the shadow radius in observer view is 3*sqrt(3)*M:
        const shadowRadius = Math.sqrt(27) * M * 0.6; // scaled for canvas
        ctx.arc(cxRight, cyRight, shadowRadius, 0, Math.PI * 2);
        ctx.fill();

        ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.arc(cxRight, cyRight, shadowRadius, 0, Math.PI * 2);
        ctx.stroke();

        // Draw Interactive Lensed Source Object (Red Circle)
        // 1. Draw its lensed images (glow arcs/circles)
        const srcOffset = {
            x: source.x - cxRight,
            y: source.y - cyRight
        };
        const srcImgs = lensCoordinates(srcOffset.x, srcOffset.y);

        // Outer image (banana arc)
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ef4444';
        ctx.fillStyle = '#f87171';
        
        // Render outer lensed image
        const outerRad = Math.max(3, source.radius * Math.sqrt(srcImgs[0].mag));
        ctx.beginPath();
        ctx.arc(srcImgs[0].x, srcImgs[0].y, outerRad, 0, Math.PI * 2);
        ctx.fill();

        // Inner lensed image
        const innerD = Math.sqrt((srcImgs[1].x - cxRight) ** 2 + (srcImgs[1].y - cyRight) ** 2);
        if (innerD > shadowRadius) {
            const innerRad = Math.max(2, source.radius * Math.sqrt(srcImgs[1].mag));
            ctx.beginPath();
            ctx.arc(srcImgs[1].x, srcImgs[1].y, innerRad, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.shadowBlur = 0; // reset

        // 2. Draw actual draggable raw source object on top (semi-transparent red outline)
        ctx.fillStyle = 'rgba(239, 68, 68, 0.18)';
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(source.x, source.y, source.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();

        // Center dot on actual source
        ctx.fillStyle = '#ef4444';
        ctx.beginPath();
        ctx.arc(source.x, source.y, 3, 0, Math.PI * 2);
        ctx.fill();

        // ==========================================
        // MIDDLE SEPARATOR LINE
        // ==========================================
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
