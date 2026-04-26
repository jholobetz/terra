document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <label>Initial Velocity: <span id="v-val">50</span></label>
        <input type="range" id="v-slider" min="10" max="100" value="50">
        <label>Launch Angle: <span id="a-val">45</span>°</label>
        <input type="range" id="a-slider" min="0" max="90" value="45">
        <label>Gravity: <span id="g-val">9.8</span></label>
        <input type="range" id="g-slider" min="1" max="20" step="0.1" value="9.8">
        <label>Air Resistance: <span id="d-val">0</span></label>
        <input type="range" id="d-slider" min="0" max="0.1" step="0.001" value="0">
        <button id="launch-btn" class="btn btn-primary" style="margin-top:10px">Launch</button>
    `;

    let v0 = 50, angle = 45, g = 9.8, drag = 0;
    let balls = [];

    const vSlider = document.getElementById('v-slider'), aSlider = document.getElementById('a-slider');
    const gSlider = document.getElementById('g-slider'), dSlider = document.getElementById('d-slider');
    const launchBtn = document.getElementById('launch-btn');

    vSlider.oninput = () => { v0 = parseInt(vSlider.value); document.getElementById('v-val').innerText = v0; };
    aSlider.oninput = () => { angle = parseInt(aSlider.value); document.getElementById('a-val').innerText = angle; };
    gSlider.oninput = () => { g = parseFloat(gSlider.value); document.getElementById('g-val').innerText = g; };
    dSlider.oninput = () => { drag = parseFloat(dSlider.value); document.getElementById('d-val').innerText = drag; };

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
    }
    window.addEventListener('resize', resize);
    resize();

    launchBtn.onclick = () => {
        const rad = (angle * Math.PI) / 180;
        balls.push({
            x: 50, y: canvas.height - 50,
            vx: v0 * Math.cos(rad) * 0.5,
            vy: -v0 * Math.sin(rad) * 0.5,
            path: []
        });
    };

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Floor
        ctx.strokeStyle = '#333';
        ctx.beginPath(); ctx.moveTo(0, canvas.height - 50); ctx.lineTo(canvas.width, canvas.height - 50); ctx.stroke();

        for (let i = balls.length - 1; i >= 0; i--) {
            let b = balls[i];
            
            // Physics
            let speed = Math.sqrt(b.vx * b.vx + b.vy * b.vy);
            let ax = -drag * speed * b.vx;
            let ay = g * 0.1 - drag * speed * b.vy;

            b.vx += ax;
            b.vy += ay;
            b.x += b.vx;
            b.y += b.vy;

            b.path.push({x: b.x, y: b.y});

            // Draw path
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.5)';
            ctx.beginPath();
            for(let p=1; p<b.path.length; p++) {
                ctx.moveTo(b.path[p-1].x, b.path[p-1].y);
                ctx.lineTo(b.path[p].x, b.path[p].y);
            }
            ctx.stroke();

            // Draw ball
            ctx.fillStyle = '#64ffda';
            ctx.beginPath(); ctx.arc(b.x, b.y, 8, 0, Math.PI*2); ctx.fill();

            if (b.y > canvas.height - 50 || b.x > canvas.width) {
                // Keep the last path but stop the ball
                b.y = canvas.height - 50;
                b.vx = 0; b.vy = 0;
                if (balls.length > 5) balls.shift();
            }
        }

        requestAnimationFrame(draw);
    }
    draw();
});
