/**
 * Project Terra - 3D Translucent Cubes Halo Orbit Engine (Option A)
 * Lightweight 60 FPS orbital physics engine using native CSS 3D transforms.
 */

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('halo-orbit-container');
    const wrapper = document.getElementById('halo-cubes-wrapper');
    if (!container || !wrapper) return;

    const cubes = Array.from(wrapper.querySelectorAll('.glass-cube'));
    if (cubes.length === 0) return;

    let baseAngle = 0;
    let speed = 0.0015; // Slow ambient drift
    let isHovered = false;
    let hoveredCube = null;
    let isDragging = false;
    let startX = 0;

    // Orbit Radii (Ellipse)
    const radiusX = 420; // Horizontal width
    const radiusY = 120; // Vertical depth (tilted 3D perspective)

    function updateOrbit() {
        if (!isHovered && !isDragging) {
            baseAngle += speed;
        }

        const count = cubes.length;
        const angleStep = (Math.PI * 2) / count;

        cubes.forEach((cube, i) => {
            if (cube === hoveredCube) return; // Hovered cube stays facing viewer

            const angle = baseAngle + i * angleStep;
            const x = Math.cos(angle) * radiusX;
            const y = Math.sin(angle) * radiusY;

            // Normalized depth (-1 back to +1 front)
            const depth = Math.sin(angle);
            const scale = 0.72 + (depth + 1) * 0.22; // 0.72x back to 1.16x front
            const opacity = 0.4 + (depth + 1) * 0.3;  // 0.4 back to 1.0 front
            const zIndex = Math.round((depth + 1) * 100);

            cube.style.transform = `translate3d(${x}px, ${y}px, ${depth * 80}px) scale(${scale})`;
            cube.style.opacity = opacity;
            cube.style.zIndex = zIndex;
        });

        requestAnimationFrame(updateOrbit);
    }

    // Interactive Hover & Focus
    cubes.forEach(cube => {
        cube.addEventListener('mouseenter', () => {
            isHovered = true;
            hoveredCube = cube;
            cube.classList.add('focused');
            cube.style.transform = `translate3d(${cube.offsetLeft}px, ${cube.offsetTop}px, 140px) scale(1.25) rotateX(0deg)`;
            cube.style.opacity = '1.0';
            cube.style.zIndex = '999';

            // Typeset MathJax if needed
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([cube]);
            }
        });

        cube.addEventListener('mouseleave', () => {
            isHovered = false;
            hoveredCube = null;
            cube.classList.remove('focused');
        });
    });

    // Touch / Mouse Drag to Spin Halo Ring
    container.addEventListener('mousedown', (e) => {
        if (e.target.closest('.glass-cube')) return;
        isDragging = true;
        startX = e.clientX;
        container.style.cursor = 'grabbing';
    });

    window.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const deltaX = e.clientX - startX;
        baseAngle += deltaX * 0.003;
        startX = e.clientX;
    });

    window.addEventListener('mouseup', () => {
        isDragging = false;
        container.style.cursor = 'grab';
    });

    // Touch support for mobile
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            startX = e.touches[0].clientX;
            isDragging = true;
        }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        const deltaX = e.touches[0].clientX - startX;
        baseAngle += deltaX * 0.003;
        startX = e.touches[0].clientX;
    }, { passive: true });

    window.addEventListener('touchend', () => {
        isDragging = false;
    });

    requestAnimationFrame(updateOrbit);
});
