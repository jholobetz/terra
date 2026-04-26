document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('simulation-canvas');
    const ctx = canvas.getContext('2d');
    const controls = document.getElementById('controls');

    controls.innerHTML = `
        <label>Frequency: <span id="f-val">0.1</span></label>
        <input type="range" id="f-slider" min="0.01" max="0.5" step="0.01" value="0.1">
        <label>Wavelength: <span id="w-val">20</span></label>
        <input type="range" id="w-slider" min="5" max="100" step="1" value="20">
        <p style="font-size:0.8rem; color:#8892b0; margin-top:15px">Interference occurs where the peaks and troughs of two waves overlap.</p>
    `;

    let freq = 0.1, lambda = 20, time = 0;

    const fSlider = document.getElementById('f-slider'), wSlider = document.getElementById('w-slider');
    fSlider.oninput = () => { freq = parseFloat(fSlider.value); document.getElementById('f-val').innerText = freq; };
    wSlider.oninput = () => { lambda = parseFloat(wSlider.value); document.getElementById('w-val').innerText = lambda; };

    function resize() {
        canvas.width = 400; // Keep smaller for performance
        canvas.height = 400;
    }
    resize();

    function draw() {
        const imageData = ctx.createImageData(canvas.width, canvas.height);
        const data = imageData.data;

        const s1 = { x: canvas.width / 3, y: canvas.height / 2 };
        const s2 = { x: 2 * canvas.width / 3, y: canvas.height / 2 };

        for (let y = 0; y < canvas.height; y++) {
            for (let x = 0; x < canvas.width; x++) {
                let d1 = Math.sqrt((x-s1.x)**2 + (y-s1.y)**2);
                let d2 = Math.sqrt((x-s2.x)**2 + (y-s2.y)**2);

                let v1 = Math.sin(d1 / lambda - time);
                let v2 = Math.sin(d2 / lambda - time);
                let sum = (v1 + v2) / 2;

                let idx = (x + y * canvas.width) * 4;
                let color = (sum + 1) * 127;
                data[idx] = color * 0.4;     // R
                data[idx+1] = color;         // G (Accent color mix)
                data[idx+2] = color * 0.8;   // B
                data[idx+3] = 255;           // A
            }
        }

        ctx.putImageData(imageData, 0, 0);
        time += freq;
        requestAnimationFrame(draw);
    }
    draw();
});
