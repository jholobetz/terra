document.addEventListener('DOMContentLoaded', () => {
    // 1. Tabbed Navigation Filtering
    const tabButtons = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.topic-card');
    
    if (tabButtons.length > 0 && cards.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class
                tabButtons.forEach(b => b.classList.remove('active'));
                // Add active class
                btn.classList.add('active');
                
                const activeDomain = btn.getAttribute('data-domain');
                
                cards.forEach(card => {
                    const cardDomain = card.getAttribute('data-domain');
                    if (activeDomain === 'all' || cardDomain === activeDomain) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            });
        });
    }

    // 2. Interactive Pendulum Simulation Sandbox
    const canvas = document.getElementById('sandbox-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Resize handler
    function resizeCanvas() {
        const rect = canvas.parentNode.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Sliders
    const sliderGravity = document.getElementById('slider-gravity');
    const sliderLength = document.getElementById('slider-length');
    const sliderDamping = document.getElementById('slider-damping');
    
    const valGravity = document.getElementById('val-gravity');
    const valLength = document.getElementById('val-length');
    const valDamping = document.getElementById('val-damping');
    
    // Physics parameters
    let g = parseFloat(sliderGravity.value);
    let L = parseFloat(sliderLength.value);
    let gamma = parseFloat(sliderDamping.value);
    
    // State
    let theta = Math.PI / 4; // Initial angle (45 degrees)
    let omega = 0.0;
    
    // Dragging state
    let isDragging = false;
    let mouseX = 0;
    let mouseY = 0;
    
    // Trail history
    const trail = [];
    const maxTrailLength = 25;
    
    // Connect sliders to state
    sliderGravity.addEventListener('input', (e) => {
        g = parseFloat(e.target.value);
        valGravity.textContent = g.toFixed(1);
    });
    sliderLength.addEventListener('input', (e) => {
        L = parseFloat(e.target.value);
        valLength.textContent = L.toFixed(1);
    });
    sliderDamping.addEventListener('input', (e) => {
        gamma = parseFloat(e.target.value);
        valDamping.textContent = gamma.toFixed(2);
    });
    
    // Coordinate conversion helpers
    function getBobPosition(width, height) {
        const pivotX = width / 2;
        const pivotY = 40;
        const scale = 75; // px per meter
        const cx = pivotX + Math.sin(theta) * (L * scale);
        const cy = pivotY + Math.cos(theta) * (L * scale);
        return { pivotX, pivotY, cx, cy };
    }
    
    // Mouse/Touch Events
    function getMouseCoords(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.touches ? e.touches[0].clientX : e.clientX;
        const clientY = e.touches ? e.touches[0].clientY : e.clientY;
        return {
            x: clientX - rect.left,
            y: clientY - rect.top
        };
    }
    
    function onStart(e) {
        const coords = getMouseCoords(e);
        const logicalWidth = canvas.width / window.devicePixelRatio;
        const logicalHeight = canvas.height / window.devicePixelRatio;
        const { cx, cy } = getBobPosition(logicalWidth, logicalHeight);
        
        const dist = Math.hypot(coords.x - cx, coords.y - cy);
        if (dist < 22) {
            isDragging = true;
            omega = 0;
        }
    }
    
    function onMove(e) {
        if (!isDragging) return;
        const coords = getMouseCoords(e);
        const logicalWidth = canvas.width / window.devicePixelRatio;
        const logicalHeight = canvas.height / window.devicePixelRatio;
        const { pivotX, pivotY } = getBobPosition(logicalWidth, logicalHeight);
        
        const dx = coords.x - pivotX;
        const dy = coords.y - pivotY;
        
        // Calculate angle from vertical (y points down, so dy is positive down)
        theta = Math.atan2(dx, dy);
        omega = 0;
        e.preventDefault();
    }
    
    function onEnd() {
        isDragging = false;
    }
    
    canvas.addEventListener('mousedown', onStart);
    canvas.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onEnd);
    
    canvas.addEventListener('touchstart', onStart, { passive: false });
    canvas.addEventListener('touchmove', onMove, { passive: false });
    window.addEventListener('touchend', onEnd);
    
    // Main loop
    let lastTime = performance.now();
    
    function step(timestamp) {
        const dt = Math.min((timestamp - lastTime) / 1000, 0.1); // Limit dt to 100ms
        lastTime = timestamp;
        
        const logicalWidth = canvas.width / window.devicePixelRatio;
        const logicalHeight = canvas.height / window.devicePixelRatio;
        
        if (!isDragging) {
            // Physics: Euler-Cromer integration
            // theta'' = -(g/L)*sin(theta) - gamma*omega
            const alpha = -(g / L) * Math.sin(theta) - gamma * omega;
            omega += alpha * dt;
            theta += omega * dt;
        }
        
        const { pivotX, pivotY, cx, cy } = getBobPosition(logicalWidth, logicalHeight);
        
        // Save trail position
        trail.push({ x: cx, y: cy });
        if (trail.length > maxTrailLength) {
            trail.shift();
        }
        
        // Draw
        ctx.clearRect(0, 0, logicalWidth, logicalHeight);
        
        // Grid background (subtle technical dots)
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
        ctx.lineWidth = 1;
        const gridSize = 25;
        for (let x = 0; x < logicalWidth; x += gridSize) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, logicalHeight);
            ctx.stroke();
        }
        for (let y = 0; y < logicalHeight; y += gridSize) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(logicalWidth, y);
            ctx.stroke();
        }
        
        // Draw trail (glowing gradient trail)
        if (trail.length > 1) {
            ctx.beginPath();
            ctx.moveTo(trail[0].x, trail[0].y);
            for (let i = 1; i < trail.length; i++) {
                ctx.lineTo(trail[i].x, trail[i].y);
            }
            ctx.strokeStyle = 'rgba(100, 255, 218, 0.15)';
            ctx.lineWidth = 3;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.stroke();
        }
        
        // Draw Rod (technical line with measurement markers)
        ctx.beginPath();
        ctx.moveTo(pivotX, pivotY);
        ctx.lineTo(cx, cy);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
        
        // Draw measurement markers along rod
        const divisions = 5;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
        ctx.lineWidth = 1;
        for (let i = 1; i < divisions; i++) {
            const fraction = i / divisions;
            const mx = pivotX + (cx - pivotX) * fraction;
            const my = pivotY + (cy - pivotY) * fraction;
            // Draw ticks perpendicular to the rod
            const perpX = -Math.cos(theta) * 3;
            const perpY = Math.sin(theta) * 3;
            ctx.beginPath();
            ctx.moveTo(mx - perpX, my - perpY);
            ctx.lineTo(mx + perpX, my + perpY);
            ctx.stroke();
        }
        
        // Draw Pivot
        ctx.beginPath();
        ctx.arc(pivotX, pivotY, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#ffffff';
        ctx.fill();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw Bob (glassmorphic particle with glowing center)
        // Outer glow
        const glowRad = isDragging ? 18 : 14;
        const radGlow = ctx.createRadialGradient(cx, cy, 2, cx, cy, glowRad);
        radGlow.addColorStop(0, 'rgba(100, 255, 218, 0.8)');
        radGlow.addColorStop(0.3, 'rgba(100, 255, 218, 0.4)');
        radGlow.addColorStop(1, 'rgba(100, 255, 218, 0)');
        
        ctx.beginPath();
        ctx.arc(cx, cy, glowRad, 0, Math.PI * 2);
        ctx.fillStyle = radGlow;
        ctx.fill();
        
        // Inner circle
        ctx.beginPath();
        ctx.arc(cx, cy, 7, 0, Math.PI * 2);
        ctx.fillStyle = '#64ffda';
        ctx.shadowBlur = 12;
        ctx.shadowColor = '#64ffda';
        ctx.fill();
        ctx.shadowBlur = 0; // Reset shadow
        
        requestAnimationFrame(step);
    }
    
    requestAnimationFrame(step);
});
