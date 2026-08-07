/**
 * Project Terra - 3D Translucent Cubes Halo Orbit Engine (Option A - Dynamic Orbital Tracking)
 * Continuous background orbital rotation where focused card glides along the track in sync.
 */

document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('halo-orbit-container');
    const wrapper = document.getElementById('halo-cubes-wrapper');
    if (!container || !wrapper) return;

    const cubes = Array.from(wrapper.querySelectorAll('.glass-cube'));
    if (cubes.length === 0) return;

    let baseAngle = 0;
    let speed = 0.0015; // Continuous ambient drift
    let isHovered = false;
    let hoveredCube = null;
    let isDragging = false;
    let startX = 0;

    // Orbit Radii (Ellipse)
    const radiusX = 440; // Horizontal width
    const radiusY = 130; // Vertical depth (tilted 3D perspective)

    // Pre-render MathJax equations once on load
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([wrapper]);
    }

    function updateOrbit() {
        // Continuous orbital rotation even when a card is selected (Option A)
        if (!isDragging) {
            baseAngle += speed;
        }

        const count = cubes.length;
        const angleStep = (Math.PI * 2) / count;

        cubes.forEach((cube, i) => {
            const angle = baseAngle + i * angleStep;
            const x = Math.cos(angle) * radiusX;
            const y = Math.sin(angle) * radiusY;
            const depth = Math.sin(angle); // Normalized depth (-1 back to +1 front)
            const zVal = depth * 80;

            // Store current computed 3D coordinates
            cube._x = x;
            cube._y = y;
            cube._z = zVal;

            if (cube === hoveredCube) {
                // Option A: Focused card glides along the track while elevated & face-forward
                cube.style.transition = 'transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s';
                cube.style.transform = `translate3d(${x}px, ${y}px, ${zVal + 120}px) scale(1.25) rotateX(0deg)`;
                cube.style.opacity = '1.0';
                cube.style.zIndex = '999';
                return;
            }

            const scale = 0.72 + (depth + 1) * 0.22; // 0.72x back to 1.16x front
            const opacity = 0.4 + (depth + 1) * 0.3;  // 0.4 back to 1.0 front
            const zIndex = Math.round((depth + 1) * 100);

            // Turn off CSS transition during continuous RAF drift for non-hovered cubes
            cube.style.transition = 'none';
            cube.style.transform = `translate3d(${x}px, ${y}px, ${zVal}px) scale(${scale})`;
            cube.style.opacity = opacity;
            cube.style.zIndex = zIndex;
        });

        requestAnimationFrame(updateOrbit);
    }

    // Option A Dynamic Orbital Tracking Interaction
    cubes.forEach(cube => {
        cube.addEventListener('mouseenter', () => {
            isHovered = true;
            hoveredCube = cube;
            cube.classList.add('focused');

            // Shield background cubes from stealing focus
            cubes.forEach(c => {
                if (c !== cube) {
                    c.style.pointerEvents = 'none';
                }
            });
        });

        cube.addEventListener('mouseleave', () => {
            isHovered = false;
            hoveredCube = null;
            cube.classList.remove('focused');

            // Restore pointer events to all cubes
            cubes.forEach(c => {
                c.style.pointerEvents = 'auto';
            });
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
