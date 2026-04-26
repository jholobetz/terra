document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <button id="add-pos" class="btn btn-primary" style="margin-bottom:5px">+ Add Positive Charge</button>
        <button id="add-neg" class="btn btn-secondary" style="margin-bottom:5px">- Add Negative Charge</button>
        <button id="clear-btn" class="btn btn-secondary">Clear All</button>
        <p style="font-size:0.8rem; color:#8892b0; margin-top:15px">Field lines are drawn from positive to negative charges.</p>
    `;

    let charges = [];
    const k = 1000;

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
    }
    window.addEventListener('resize', resize);
    resize();

    document.getElementById('add-pos').onclick = () => {
        charges.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, q: 1 });
    };
    document.getElementById('add-neg').onclick = () => {
        charges.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, q: -1 });
    };
    document.getElementById('clear-btn').onclick = () => charges = [];

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        if (charges.length > 0) {
            const step = 25;
            for (let x = 0; x < canvas.width; x += step) {
                for (let y = 0; y < canvas.height; y += step) {
                    let ex = 0, ey = 0;
                    
                    for (let c of charges) {
                        let dx = x - c.x;
                        let dy = y - c.y;
                        let r2 = dx * dx + dy * dy;
                        let r = Math.sqrt(r2);
                        if (r < 10) continue;
                        
                        let f = (k * c.q) / r2;
                        ex += f * (dx / r);
                        ey += f * (dy / r);
                    }

                    let mag = Math.sqrt(ex * ex + ey * ey);
                    if (mag > 0) {
                        ctx.strokeStyle = `rgba(100, 255, 218, ${Math.min(mag/2, 0.5)})`;
                        ctx.beginPath();
                        ctx.moveTo(x, y);
                        ctx.lineTo(x + (ex/mag)*15, y + (ey/mag)*15);
                        ctx.stroke();
                    }
                }
            }
        }

        for (let c of charges) {
            ctx.fillStyle = c.q > 0 ? '#ff4d4d' : '#4d79ff';
            ctx.beginPath(); ctx.arc(c.x, c.y, 10, 0, Math.PI*2); ctx.fill();
            ctx.fillStyle = '#fff'; ctx.textAlign = 'center'; ctx.fillText(c.q > 0 ? '+' : '-', c.x, c.y+4);
        }

        requestAnimationFrame(draw);
    }
    draw();
});
