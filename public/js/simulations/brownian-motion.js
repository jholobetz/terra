document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <label>Temperature (Speed): <span id="t-val">2</span></label>
        <input type="range" id="t-slider" min="0.1" max="10" step="0.1" value="2">
        <label>Particle Count: <span id="c-val">50</span></label>
        <input type="range" id="c-slider" min="10" max="200" step="1" value="50">
        <p style="font-size:0.8rem; color:#8892b0; margin-top:15px">The larger highlight shows the random walk of a single tracer particle.</p>
    `;

    let temp = 2, count = 50;
    let particles = [];

    const tSlider = document.getElementById('t-slider'), cSlider = document.getElementById('c-slider');
    tSlider.oninput = () => { temp = parseFloat(tSlider.value); document.getElementById('t-val').innerText = temp; };
    cSlider.oninput = () => { count = parseInt(cSlider.value); document.getElementById('c-val').innerText = count; init(); };

    function init() {
        particles = [];
        for (let i = 0; i < count; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5),
                vy: (Math.random() - 0.5),
                radius: i === 0 ? 10 : 3,
                color: i === 0 ? '#64ffda' : '#8892b0',
                path: i === 0 ? [] : null
            });
        }
    }

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
        init();
    }
    window.addEventListener('resize', resize);
    resize();

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];
            p.x += p.vx * temp;
            p.y += p.vy * temp;

            // Wall collisions
            if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

            if (p.path) {
                p.path.push({x: p.x, y: p.y});
                if (p.path.length > 200) p.path.shift();
                ctx.strokeStyle = 'rgba(100, 255, 218, 0.4)';
                ctx.beginPath();
                for(let j=1; j<p.path.length; j++) {
                    ctx.moveTo(p.path[j-1].x, p.path[j-1].y);
                    ctx.lineTo(p.path[j].x, p.path[j].y);
                }
                ctx.stroke();
            }

            ctx.fillStyle = p.color;
            ctx.beginPath(); ctx.arc(p.x, p.y, p.radius, 0, Math.PI*2); ctx.fill();
        }

        requestAnimationFrame(draw);
    }
    draw();
});
