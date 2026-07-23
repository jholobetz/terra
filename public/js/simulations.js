document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('pendulum-canvas');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const container = document.getElementById('pendulum-canvas-container');
    
    // Resize canvas
    canvas.width = container.clientWidth;
    canvas.height = 400;

    const lengthSlider = document.getElementById('length-slider');
    const lengthVal = document.getElementById('length-val');
    const gravitySlider = document.getElementById('gravity-slider');
    const gravityVal = document.getElementById('gravity-val');

    let r = parseInt(lengthSlider.value);
    let g = parseFloat(gravitySlider.value);
    let angle = Math.PI / 4;
    let angleV = 0;
    let angleA = 0;

    const origin = { x: canvas.width / 2, y: 50 };

    lengthSlider.addEventListener('input', (e) => {
        r = parseInt(e.target.value);
        lengthVal.innerText = r;
    });

    gravitySlider.addEventListener('input', (e) => {
        g = parseFloat(e.target.value);
        gravityVal.innerText = g;
    });

    function draw() {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Physics
        let force = -1 * g / r * Math.sin(angle);
        angleA = force;
        angleV += angleA;
        angle += angleV;

        angleV *= 0.999; // Damping

        // Positions
        let x = r * Math.sin(angle) + origin.x;
        let y = r * Math.cos(angle) + origin.y;

        // Draw line
        ctx.strokeStyle = '#ccd6f6';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(origin.x, origin.y);
        ctx.lineTo(x, y);
        ctx.stroke();

        // Draw bob
        ctx.fillStyle = '#64ffda';
        ctx.beginPath();
        ctx.arc(x, y, 20, 0, Math.PI * 2);
        ctx.fill();

        requestAnimationFrame(draw);
    }

    draw();
});
