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

    // Force MathJax typesetting on the sandbox display equation
    if (window.MathJax && window.MathJax.typesetPromise) {
        const renderEl = document.querySelector('.equation-render');
        if (renderEl) {
            window.MathJax.typesetPromise([renderEl]).catch(err => console.warn("Sandbox math typesetting failed:", err));
        }
    }

    // 2. Interactive Projectile Motion Sandbox
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
    
    // Sliders & UI Elements
    const sliderVelocity = document.getElementById('slider-velocity');
    const sliderAngle = document.getElementById('slider-angle');
    const sliderDrag = document.getElementById('slider-drag');
    
    const valVelocity = document.getElementById('val-velocity');
    const valAngle = document.getElementById('val-angle');
    const valDrag = document.getElementById('val-drag');
    
    const launchBtn = document.getElementById('launch-btn');
    const clearBtn = document.getElementById('clear-btn');
    
    // Physics parameters & state
    let v0 = parseFloat(sliderVelocity.value);
    let angle = parseFloat(sliderAngle.value);
    let drag = parseFloat(sliderDrag.value);
    const g = 9.81; // standard gravity
    
    let projectiles = [];
    let particles = [];
    let lastTime = performance.now();
    
    // Connect sliders to state
    sliderVelocity.addEventListener('input', (e) => {
        v0 = parseFloat(e.target.value);
        valVelocity.textContent = v0;
    });
    sliderAngle.addEventListener('input', (e) => {
        angle = parseFloat(e.target.value);
        valAngle.textContent = angle;
    });
    sliderDrag.addEventListener('input', (e) => {
        drag = parseFloat(e.target.value);
        valDrag.textContent = drag.toFixed(3);
    });
    
    clearBtn.addEventListener('click', () => {
        projectiles = [];
        particles = [];
    });
    
    // Launch Projectile
    function fireCannon() {
        const logicalWidth = canvas.width / window.devicePixelRatio;
        const logicalHeight = canvas.height / window.devicePixelRatio;
        
        const groundY = logicalHeight - 35;
        const cannonX = 35;
        const cannonY = groundY;
        
        const rad = (angle * Math.PI) / 180;
        const barrelLen = 30;
        
        // Muzzle position
        const mx = cannonX + Math.cos(rad) * barrelLen;
        const my = cannonY - Math.sin(rad) * barrelLen;
        
        // Velocity scale (converts physical m/s to canvas speed per frame)
        const scale = 0.14;
        
        projectiles.push({
            x: mx,
            y: my,
            vx: v0 * Math.cos(rad) * scale,
            vy: -v0 * Math.sin(rad) * scale,
            radius: 4,
            color: '#00ffff', // cyan shell
            trailColor: 'rgba(0, 210, 255, 0.45)',
            path: [],
            active: true
        });
        
        // Spawn muzzle flash smoke particles
        for (let i = 0; i < 8; i++) {
            const pAngle = rad + (Math.random() - 0.5) * 0.4;
            const pSpeed = 1.5 + Math.random() * 3.0;
            particles.push({
                x: mx, y: my,
                vx: pSpeed * Math.cos(pAngle),
                vy: -pSpeed * Math.sin(pAngle),
                radius: 2 + Math.random() * 4,
                color: `rgba(255, 78, 136, ${0.3 + Math.random() * 0.5})`, // orange/pink smoke
                age: 0,
                maxAge: 12 + Math.random() * 8,
                type: 'smoke'
            });
        }
    }
    
    if (launchBtn) launchBtn.addEventListener('click', fireCannon);
    
    // Spawn floor explosion sparks
    function triggerExplosion(ex, ey) {
        for (let i = 0; i < 12; i++) {
            const pAngle = Math.random() * Math.PI; // bounce upwards
            const pSpeed = 1.0 + Math.random() * 3.0;
            particles.push({
                x: ex, y: ey,
                vx: pSpeed * Math.cos(pAngle),
                vy: -pSpeed * Math.sin(pAngle),
                radius: 1.5 + Math.random() * 2,
                color: `rgba(255, 215, 0, ${0.7 + Math.random() * 0.3})`, // gold sparks
                age: 0,
                maxAge: 15 + Math.random() * 10,
                type: 'spark'
            });
        }
    }
    
    // Main loop
    function step(timestamp) {
        const dt = Math.min((timestamp - lastTime) / 1000, 0.1) * 60; // limit and scale dt
        lastTime = timestamp;
        
        const logicalWidth = canvas.width / window.devicePixelRatio;
        const logicalHeight = canvas.height / window.devicePixelRatio;
        const groundY = logicalHeight - 35;
        
        // 1. Update active projectiles
        for (let p of projectiles) {
            if (!p.active) continue;
            
            const speed = Math.sqrt(p.vx * p.vx + p.vy * p.vy) || 0.001;
            
            // Drag force (opposite to velocity direction)
            const fDragX = -drag * speed * p.vx * 0.09;
            const fDragY = -drag * speed * p.vy * 0.09;
            
            // Gravity force (downwards)
            const fGravY = g * 0.022;
            
            // Velocity Verlet/Euler-Cromer integration step
            p.vx += fDragX * dt;
            p.vy += (fDragY + fGravY) * dt;
            
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            
            // Save path coordinates
            p.path.push({ x: p.x, y: p.y });
            if (p.path.length > 250) p.path.shift();
            
            // Ground collision check
            if (p.y >= groundY) {
                p.y = groundY;
                p.active = false;
                triggerExplosion(p.x, p.y);
            }
        }
        
        // 2. Update smoke and spark particles
        for (let i = particles.length - 1; i >= 0; i--) {
            const pt = particles[i];
            pt.x += pt.vx;
            pt.y += pt.vy;
            pt.age++;
            
            if (pt.type === 'spark') {
                pt.vy += 0.08; // sparks experience gravity
            }
            
            if (pt.age >= pt.maxAge) {
                particles.splice(i, 1);
            }
        }
        
        // 3. Render
        ctx.clearRect(0, 0, logicalWidth, logicalHeight);
        
        // Technical dots grid background
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
        
        // Draw Ground Line
        ctx.beginPath();
        ctx.moveTo(0, groundY);
        ctx.lineTo(logicalWidth, groundY);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
        ctx.lineWidth = 2;
        ctx.stroke();
        
        // Draw Projectile Trails
        for (let p of projectiles) {
            if (p.path.length > 1) {
                ctx.beginPath();
                ctx.moveTo(p.path[0].x, p.path[0].y);
                for (let i = 1; i < p.path.length; i++) {
                    ctx.lineTo(p.path[i].x, p.path[i].y);
                }
                ctx.strokeStyle = p.trailColor;
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        }
        
        // Draw Shells
        for (let p of projectiles) {
            if (p.active) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fillStyle = p.color;
                ctx.shadowBlur = 8;
                ctx.shadowColor = p.color;
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }
        
        // Draw Particles (Smoke & Sparks)
        for (let pt of particles) {
            ctx.beginPath();
            ctx.arc(pt.x, pt.y, pt.radius * (1 - pt.age / pt.maxAge), 0, Math.PI * 2);
            ctx.fillStyle = pt.color;
            ctx.fill();
        }
        
        // Draw Cannon Base and Barrel
        const cannonX = 35;
        const cannonY = groundY;
        const rad = (angle * Math.PI) / 180;
        const barrelLen = 30;
        
        // Barrel line
        ctx.beginPath();
        ctx.moveTo(cannonX, cannonY);
        ctx.lineTo(cannonX + Math.cos(rad) * barrelLen, cannonY - Math.sin(rad) * barrelLen);
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.stroke();
        
        // Cannon wheels/base mount
        ctx.beginPath();
        ctx.arc(cannonX, cannonY, 8, 0, Math.PI * 2);
        ctx.fillStyle = '#1e293b';
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.fill();
        ctx.stroke();
        
        requestAnimationFrame(step);
    }
    
    requestAnimationFrame(step);
});
