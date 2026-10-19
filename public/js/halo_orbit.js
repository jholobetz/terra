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
    const angularVelocity = 0.0015; // Continuous ambient drift per 60Hz tick
    let isHovered = false;
    let hoveredCube = null;
    let isDragging = false;
    let startX = 0;

    // Lifecycle & Visibility Gating (prevents idle background GPU/CPU drain)
    let isInViewport = true;
    let isWindowFocused = document.hasFocus ? document.hasFocus() : true;
    let rafId = null;
    let lastFrameTime = 0;
    const frameInterval = 1000 / 30; // Cap at 30fps
    const baseTickMs = 1000 / 60;    // Reference 60Hz tick for angularVelocity

    // Orbit Radii (Ellipse)
    const radiusX = 480; // Horizontal width (matches 960px ring)
    const radiusY = 140; // Vertical depth (tilted 3D perspective, matches 280px ring)

    // Pre-render MathJax equations once on load
    if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([wrapper]);
    }

    function shouldAnimate() {
        return !document.hidden && isWindowFocused && isInViewport;
    }

    function renderOrbitPositions() {
        const count = cubes.length;
        const angleStep = (Math.PI * 2) / count;

        cubes.forEach((cube, i) => {
            const angle = baseAngle + i * angleStep;
            const x = Math.cos(angle) * radiusX;
            const y = Math.sin(angle) * radiusY;
            const depth = Math.sin(angle); // Normalized depth (-1 back to +1 front)
            const zVal = depth * 80;

            if (cube === hoveredCube) {
                cube.style.transition = 'transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s';
                cube.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, ${(zVal + 120).toFixed(1)}px) scale(1.25)`;
                cube.style.opacity = '1';
                cube.style.zIndex = '999';
                return;
            }

            const scale = 0.72 + (depth + 1) * 0.22; // 0.72x back to 1.16x front
            const opacity = 0.4 + (depth + 1) * 0.3;  // 0.4 back to 1.0 front
            const zIndex = Math.round((depth + 1) * 100);

            cube.style.transition = 'none';
            cube.style.transform = `translate3d(${x.toFixed(1)}px, ${y.toFixed(1)}px, ${zVal.toFixed(1)}px) scale(${scale.toFixed(3)})`;
            cube.style.opacity = opacity.toFixed(2);
            cube.style.zIndex = String(zIndex);
        });
    }

    function updateOrbit(timestamp) {
        if (!shouldAnimate()) {
            rafId = null;
            return;
        }

        if (!lastFrameTime) lastFrameTime = timestamp;
        const elapsed = timestamp - lastFrameTime;

        if (elapsed >= frameInterval) {
            const tickScale = Math.min(elapsed / baseTickMs, 3.0);
            lastFrameTime = timestamp - (elapsed % frameInterval);

            if (!isDragging) {
                baseAngle += angularVelocity * tickScale;
            }
            renderOrbitPositions();
        }

        rafId = requestAnimationFrame(updateOrbit);
    }

    function startLoop() {
        if (rafId === null && shouldAnimate()) {
            lastFrameTime = 0;
            rafId = requestAnimationFrame(updateOrbit);
        }
    }

    function stopLoop() {
        if (rafId !== null) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    }

    // Option A Dynamic Orbital Tracking Interaction
    cubes.forEach(cube => {
        cube.addEventListener('mouseenter', () => {
            isHovered = true;
            hoveredCube = cube;
            cube.classList.add('focused');
            renderOrbitPositions();

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
            renderOrbitPositions();

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
        renderOrbitPositions();
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

    container.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        const deltaX = e.touches[0].clientX - startX;
        baseAngle += deltaX * 0.003;
        startX = e.touches[0].clientX;
        renderOrbitPositions();
    }, { passive: true });

    window.addEventListener('touchend', () => {
        isDragging = false;
    });

    // Pause when tab is hidden or window loses focus
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) stopLoop();
        else startLoop();
    });

    window.addEventListener('focus', () => {
        isWindowFocused = true;
        startLoop();
    });

    window.addEventListener('blur', () => {
        isWindowFocused = false;
        stopLoop();
    });

    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                isInViewport = entry.isIntersecting;
                if (isInViewport) startLoop();
                else stopLoop();
            });
        }, { threshold: 0.05 });
        observer.observe(container);
    }

    // Initial static layout + start RAF loop if active
    renderOrbitPositions();
    startLoop();
});
