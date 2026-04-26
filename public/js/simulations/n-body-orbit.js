document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <label>Gravitational Constant (G): <span id="g-val">1</span></label>
        <input type="range" id="g-slider" min="0.1" max="10" step="0.1" value="1">
        <button id="reset-btn" class="btn btn-secondary" style="margin-top:10px">Reset & Randomize</button>
        <p style="font-size:0.8rem; color:#8892b0; margin-top:15px">Click to add a massive body.</p>
    `;

    let G = 1;
    let bodies = [];

    const gSlider = document.getElementById('g-slider');
    const resetBtn = document.getElementById('reset-btn');

    gSlider.oninput = () => { G = parseFloat(gSlider.value); document.getElementById('g-val').innerText = G; };

    function createRandomBody() {
        return {
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            mass: Math.random() * 100 + 50,
            color: '#64ffda',
            path: []
        };
    }

    function init() {
        bodies = [];
        for(let i=0; i<3; i++) bodies.push(createRandomBody());
    }

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        init();
    }
    window.addEventListener('resize', resize);
    resize();

    resetBtn.onclick = init;
    canvas.onclick = (e) => {
        const rect = canvas.getBoundingClientRect();
        bodies.push({
            x: e.clientX - rect.left,
            y: e.clientY - rect.top,
            vx: 0, vy: 0,
            mass: 200,
            color: '#e6f1ff',
            path: []
        });
    };

    function draw() {
        ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; // Motion blur effect
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Physics: N-Body Interaction
        for (let i = 0; i < bodies.length; i++) {
            let b1 = bodies[i];
            for (let j = 0; j < bodies.length; j++) {
                if (i === j) continue;
                let b2 = bodies[j];

                let dx = b2.x - b1.x;
                let dy = b2.y - b1.y;
                let distSq = dx * dx + dy * dy + 100; // Softening factor to prevent infinity
                let force = (G * b1.mass * b2.mass) / distSq;
                let accel = force / b1.mass;
                let dist = Math.sqrt(distSq);

                b1.vx += (dx / dist) * accel;
                b1.vy += (dy / dist) * accel;
            }
        }

        // Update positions and draw
        for (let b of bodies) {
            b.x += b.vx;
            b.y += b.vy;

            // Draw Body
            ctx.fillStyle = b.color;
            ctx.beginPath();
            ctx.arc(b.x, b.y, Math.sqrt(b.mass), 0, Math.PI * 2);
            ctx.fill();

            // Screen wrap
            if (b.x < 0) b.x = canvas.width;
            if (b.x > canvas.width) b.x = 0;
            if (b.y < 0) b.y = canvas.height;
            if (b.y > canvas.height) b.y = 0;
        }

        requestAnimationFrame(draw);
    }
    draw();
});
