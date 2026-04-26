(function() {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    let charges = [];
    let currentType = 1; // 1 for positive, -1 for negative
    const sphereRadius = 120;

    // Set canvas size
    function resize() {
        const container = canvas.parentElement;
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    // Inject specific controls for this simulation
    controls.innerHTML = `
        <div class="control-group">
            <p style="font-size: 0.8rem; margin-bottom: 10px; opacity: 0.8;">Click the canvas to place charges.</p>
            <button id="btn-pos" class="btn btn-primary" style="background: #ff4d4d; border:none; margin-bottom: 10px; width: 100%; cursor: pointer;">Current: Positive (+)</button>
            <button id="btn-neg" class="btn btn-primary" style="background: #4d4dff; border:none; margin-bottom: 10px; width: 100%; cursor: pointer; opacity: 0.5;">Switch to Negative (-)</button>
            <button id="btn-clear" class="btn btn-secondary" style="width: 100%; cursor: pointer;">Clear All Charges</button>
        </div>
        <div class="stat-card" style="margin-top: 20px; text-align: center; border-top-color: #b464ff;">
            <div style="font-size: 0.8rem; opacity: 0.7; color: #ccd6f6;">Net Electric Flux (&Phi;<sub>E</sub>)</div>
            <div id="q-enc-val" style="font-size: 2.5rem; font-weight: bold; color: #b464ff;">0</div>
            <div style="font-size: 0.7rem; opacity: 0.5;">(Calculated from Enclosed Charge)</div>
        </div>
    `;

    const btnPos = document.getElementById('btn-pos');
    const btnNeg = document.getElementById('btn-neg');

    btnPos.onclick = () => { currentType = 1; btnPos.style.opacity = 1; btnNeg.style.opacity = 0.5; };
    btnNeg.onclick = () => { currentType = -1; btnNeg.style.opacity = 1; btnPos.style.opacity = 0.5; };
    document.getElementById('btn-clear').onclick = () => { charges = []; };

    canvas.onclick = (e) => {
        const rect = canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        charges.push({ x, y, type: currentType });
    };

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        // Draw Gaussian Surface (The Sphere)
        ctx.beginPath();
        ctx.arc(cx, cy, sphereRadius, 0, Math.PI * 2);
        ctx.setLineDash([8, 4]);
        ctx.strokeStyle = '#64ffda';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.setLineDash([]);
        
        // Label
        ctx.fillStyle = '#64ffda';
        ctx.font = '600 14px Inter';
        ctx.textAlign = 'center';
        ctx.fillText('Gaussian Surface', cx, cy - sphereRadius - 15);

        let qEnc = 0;

        charges.forEach(c => {
            const dist = Math.sqrt(Math.pow(c.x - cx, 2) + Math.pow(c.y - cy, 2));
            const isInside = dist < sphereRadius;
            if (isInside) qEnc += c.type;

            // Draw Charge Particle
            ctx.beginPath();
            ctx.arc(c.x, c.y, 10, 0, Math.PI * 2);
            ctx.fillStyle = c.type > 0 ? '#ff4d4d' : '#4d4dff';
            ctx.fill();
            
            ctx.fillStyle = 'white';
            ctx.font = 'bold 14px Arial';
            ctx.fillText(c.type > 0 ? '+' : '-', c.x, c.y + 4);
        });

        // Update UI
        document.getElementById('q-enc-val').innerText = qEnc > 0 ? `+${qEnc}` : qEnc;
        
        requestAnimationFrame(draw);
    }

    draw();
})();