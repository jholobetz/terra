document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <label>Mass 1: <span id="m1-val">10</span></label>
        <input type="range" id="m1-slider" min="5" max="50" value="10">
        <label>Mass 2: <span id="m2-val">10</span></label>
        <input type="range" id="m2-slider" min="5" max="50" value="10">
        <label>Length 1: <span id="r1-val">150</span></label>
        <input type="range" id="r1-slider" min="50" max="250" value="150">
        <label>Length 2: <span id="r2-val">150</span></label>
        <input type="range" id="r2-slider" min="50" max="250" value="150">
        <label>Gravity: <span id="g-val">1</span></label>
        <input type="range" id="g-slider" min="0.1" max="2" step="0.1" value="1">
    `;

    let r1 = 150, r2 = 150, m1 = 10, m2 = 10, g = 1;
    let a1 = Math.PI / 2, a2 = Math.PI / 2, a1_v = 0, a2_v = 0;

    const m1Slider = document.getElementById('m1-slider'), m2Slider = document.getElementById('m2-slider');
    const r1Slider = document.getElementById('r1-slider'), r2Slider = document.getElementById('r2-slider');
    const gSlider = document.getElementById('g-slider');

    m1Slider.oninput = () => { m1 = parseInt(m1Slider.value); document.getElementById('m1-val').innerText = m1; };
    m2Slider.oninput = () => { m2 = parseInt(m2Slider.value); document.getElementById('m2-val').innerText = m2; };
    r1Slider.oninput = () => { r1 = parseInt(r1Slider.value); document.getElementById('r1-val').innerText = r1; };
    r2Slider.oninput = () => { r2 = parseInt(r2Slider.value); document.getElementById('r2-val').innerText = r2; };
    gSlider.oninput = () => { g = parseFloat(gSlider.value); document.getElementById('g-val').innerText = g; };

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 600;
    }
    window.addEventListener('resize', resize);
    resize();

    let path = [];

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Physics equations for double pendulum
        let num1 = -g * (2 * m1 + m2) * Math.sin(a1);
        let num2 = -m2 * g * Math.sin(a1 - 2 * a2);
        let num3 = -2 * Math.sin(a1 - a2) * m2;
        let num4 = a2_v * a2_v * r2 + a1_v * a1_v * r1 * Math.cos(a1 - a2);
        let den = r1 * (2 * m1 + m2 - m2 * Math.cos(2 * a1 - 2 * a2));
        let a1_a = (num1 + num2 + num3 * num4) / den;

        num1 = 2 * Math.sin(a1 - a2);
        num2 = (a1_v * a1_v * r1 * (m1 + m2));
        num3 = g * (m1 + m2) * Math.cos(a1);
        num4 = a2_v * a2_v * r2 * m2 * Math.cos(a1 - a2);
        den = r2 * (2 * m1 + m2 - m2 * Math.cos(2 * a1 - 2 * a2));
        let a2_a = (num1 * (num2 + num3 + num4)) / den;

        const cx = canvas.width / 2;
        const cy = 200;

        let x1 = r1 * Math.sin(a1) + cx;
        let y1 = r1 * Math.cos(a1) + cy;
        let x2 = x1 + r2 * Math.sin(a2);
        let y2 = y1 + r2 * Math.cos(a2);

        // Trace path
        path.push({x: x2, y: y2});
        if (path.length > 500) path.shift();
        
        ctx.strokeStyle = 'rgba(100, 255, 218, 0.3)';
        ctx.beginPath();
        for(let i=1; i<path.length; i++) {
            ctx.moveTo(path[i-1].x, path[i-1].y);
            ctx.lineTo(path[i].x, path[i].y);
        }
        ctx.stroke();

        ctx.strokeStyle = '#ccd6f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(cx, cy);
        ctx.lineTo(x1, y1);
        ctx.lineTo(x2, y2);
        ctx.stroke();

        ctx.fillStyle = '#64ffda';
        ctx.beginPath(); ctx.arc(x1, y1, m1/2, 0, Math.PI*2); ctx.fill();
        ctx.beginPath(); ctx.arc(x2, y2, m2/2, 0, Math.PI*2); ctx.fill();

        a1_v += a1_a; a2_v += a2_a;
        a1 += a1_v; a2 += a2_v;
        
        a1_v *= 0.999; a2_v *= 0.999; // Minor damping

        requestAnimationFrame(draw);
    }
    draw();
});
