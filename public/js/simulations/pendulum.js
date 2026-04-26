document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    // Controls
    controls.innerHTML = `
        <label>Length: <span id="len-val">150</span>px</label>
        <input type="range" id="len-slider" min="50" max="300" value="150">
        <label>Gravity: <span id="g-val">0.5</span></label>
        <input type="range" id="g-slider" min="0.1" max="2" step="0.1" value="0.5">
    `;

    const lenSlider = document.getElementById('len-slider');
    const gSlider = document.getElementById('g-slider');
    const lenVal = document.getElementById('len-val');
    const gVal = document.getElementById('g-val');

    let r = 150;
    let g = 0.5;
    let angle = Math.PI / 4;
    let angleV = 0;
    let angleA = 0;

    function resize() {
        canvas.width = canvas.parentElement.clientWidth;
        canvas.height = 500;
    }
    window.addEventListener('resize', resize);
    resize();

    lenSlider.oninput = () => { r = parseInt(lenSlider.value); lenVal.innerText = r; };
    gSlider.oninput = () => { g = parseFloat(gSlider.value); gVal.innerText = g; };

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        let force = -1 * g / r * Math.sin(angle);
        angleA = force;
        angleV += angleA;
        angle += angleV;
        angleV *= 0.999;

        let x = r * Math.sin(angle) + canvas.width / 2;
        let y = r * Math.cos(angle) + 100;

        ctx.strokeStyle = '#ccd6f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(canvas.width / 2, 100);
        ctx.lineTo(x, y);
        ctx.stroke();

        ctx.fillStyle = '#64ffda';
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, Math.PI * 2);
        ctx.fill();

        requestAnimationFrame(draw);
    }
    draw();
});
