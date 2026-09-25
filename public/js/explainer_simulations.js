/**
 * 🪐 Physics Lab: Equation Explainer - Interactive Simulations & Sonification Module
 * Manages 2D canvas vector field animations (divergence, curl, waves, scaling)
 * and Web Audio API mathematical parameter sonification.
 */

const ExplainerSimulations = {
    initSandbox(latex, variables) {
        this.stopSandbox();
        this.stopSonification();

        if (!this.sandboxCanvas) return;

        this.sandboxCtx = this.sandboxCanvas.getContext('2d');

        // 1. Classify Sandbox Type
        if (latex.includes('\\nabla \\cdot') || latex.includes('\\text{div}')) {
            this.sandboxType = 'divergence';
        } else if (latex.includes('\\nabla \\times') || latex.includes('\\text{curl}')) {
            this.sandboxType = 'curl';
        } else if (latex.includes('\\partial') && latex.includes('\\partial t') || latex.includes('\\dot') || latex.includes('\\frac{d}{dt}') || latex.includes('\\ddot') || latex.includes('\\int') || latex.includes('\\oint')) {
            this.sandboxType = 'wave';
        } else {
            this.sandboxType = 'scaling';
        }

        // 2. Extract active variables
        const tokens = this.extractAllMathTokens(latex, variables);
        const vars = tokens.filter(t => t.type === 'variable');

        // Reset parameters
        this.sandboxParams = {};
        this.sandboxSliders.innerHTML = '';

        // Default parameters based on type
        if (this.sandboxType === 'divergence') {
            this.sandboxParams['strength'] = 5; // Divergence value (-10 to 10)
            this.createSlider('strength', 'Field Strength / Charge (ρ)', 'dimensionless', -10, 10, 5, 0.5);
        } else if (this.sandboxType === 'curl') {
            this.sandboxParams['vorticity'] = 5; // Rotational velocity (-10 to 10)
            this.createSlider('vorticity', 'Vorticity / Circulation (Γ)', 'rad/s', -10, 10, 5, 0.5);
        } else if (this.sandboxType === 'wave') {
            this.sandboxParams['frequency'] = 5;
            this.sandboxParams['amplitude'] = 4;
            this.createSlider('frequency', 'Angular Frequency (ω)', 'Hz', 1, 15, 5, 0.2);
            this.createSlider('amplitude', 'Wave Amplitude (A)', 'dimensionless', 1, 8, 4, 0.2);
        } else {
            // General scaling parameters
            this.sandboxParams['input'] = 5;
            this.createSlider('input', 'Control Input Variable', 'dimensionless', 0, 10, 5, 0.1);
        }

        // Check for General Relativity / Black Hole Metric formulas
        if (latex.includes('g_{\\mu\\nu}') || latex.includes('Schwarzschild') || latex.includes('Kerr') || (latex.includes('\\Delta') && latex.includes('r^2')) || latex.includes('r_s') || latex.includes('2GM') || (latex.includes('R_{\\mu\\nu}'))) {
            const grBanner = document.createElement('div');
            grBanner.style.cssText = 'margin-top: 10px; padding: 10px 12px; background: rgba(56, 189, 248, 0.08); border: 1px solid rgba(56, 189, 248, 0.25); border-radius: 6px; display: flex; flex-direction: column; gap: 6px;';
            grBanner.innerHTML = `
                <div style="font-size: 0.78rem; font-weight: 700; color: #38bdf8; text-transform: uppercase; letter-spacing: 0.05em;">GPU Relativistic Model</div>
                <div style="font-size: 0.8rem; color: #cbd5e1;">Raymarch null geodesics, event horizons, and accretion disk beaming in full WebGL2.</div>
                <a href="/physics/simulations/relativistic-black-hole" target="_blank" style="display: inline-flex; align-items: center; justify-content: center; gap: 6px; padding: 6px 10px; background: var(--accent-default, #38bdf8); color: #020617; font-size: 0.78rem; font-weight: 600; border-radius: 4px; text-decoration: none; margin-top: 4px; transition: opacity 0.15s;">
                    Launch Black Hole Raytracer &rarr;
                </a>
            `;
            this.sandboxSliders.appendChild(grBanner);
        }

        // 3. Start render loop
        this.startSandboxLoop();
    },

    createSlider(name, label, unit, min, max, val, step) {
        this.sandboxParams[name] = val;

        const sliderWrapper = document.createElement('div');
        sliderWrapper.style.cssText = 'display: flex; flex-direction: column; gap: 4px;';

        const labelRow = document.createElement('div');
        labelRow.style.cssText = 'display: flex; justify-content: space-between; font-size: 0.82rem; color: #cbd5e1;';
        
        const labelText = document.createElement('span');
        labelText.textContent = label;

        const valText = document.createElement('span');
        valText.style.cssText = 'font-weight: 600; color: var(--accent-default, #64ffda); font-family: "Fira Code", monospace;';
        valText.textContent = `${val} ${unit !== 'dimensionless' ? unit : ''}`;

        labelRow.appendChild(labelText);
        labelRow.appendChild(valText);

        const input = document.createElement('input');
        input.type = 'range';
        input.min = min;
        input.max = max;
        input.value = val;
        input.step = step;
        input.style.cssText = 'width: 100%; height: 4px; border-radius: 2px; background: rgba(255, 255, 255, 0.1); outline: none; cursor: pointer; accent-color: var(--accent-default, #64ffda);';

        input.addEventListener('input', (e) => {
            const numVal = parseFloat(e.target.value);
            this.sandboxParams[name] = numVal;
            valText.textContent = `${numVal} ${unit !== 'dimensionless' ? unit : ''}`;
            this.updateSonificationParameters();
        });

        sliderWrapper.appendChild(labelRow);
        sliderWrapper.appendChild(input);
        this.sandboxSliders.appendChild(sliderWrapper);
    },

    stopSandbox() {
        if (this.sandboxAnimationId) {
            cancelAnimationFrame(this.sandboxAnimationId);
            this.sandboxAnimationId = null;
        }
    },

    startSandboxLoop() {
        let time = 0;

        const render = () => {
            if (!this.sandboxCanvas || !this.sandboxCtx) return;

            const w = this.sandboxCanvas.width;
            const h = this.sandboxCanvas.height;
            const ctx = this.sandboxCtx;

            ctx.clearRect(0, 0, w, h);

            // Draw base grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
            ctx.lineWidth = 1;
            const step = 20;
            for (let x = 0; x < w; x += step) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();
            }
            for (let y = 0; y < h; y += step) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }

            // Draw active animation
            time += 0.05;
            if (this.sandboxType === 'divergence') {
                this.drawDivergence(ctx, w, h, time, this.sandboxParams['strength']);
            } else if (this.sandboxType === 'curl') {
                this.drawCurl(ctx, w, h, time, this.sandboxParams['vorticity']);
            } else if (this.sandboxType === 'wave') {
                this.drawWave(ctx, w, h, time, this.sandboxParams['frequency'], this.sandboxParams['amplitude']);
            } else {
                this.drawScaling(ctx, w, h, time, this.sandboxParams['input']);
            }

            if (typeof window !== 'undefined' && window.requestAnimationFrame) {
                this.sandboxAnimationId = window.requestAnimationFrame(render);
            }
        };

        render();
    },

    drawDivergence(ctx, w, h, t, strength) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw central source/sink node
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, Math.PI * 2);
        ctx.fillStyle = strength > 0 ? '#10b981' : (strength < 0 ? '#f43f5e' : 'rgba(255, 255, 255, 0.2)');
        ctx.fill();

        // Particle stream lines
        const numStreams = 12;
        for (let i = 0; i < numStreams; i++) {
            const angle = (i * Math.PI * 2) / numStreams;
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);

            ctx.strokeStyle = strength > 0 ? 'rgba(16, 185, 129, 0.12)' : (strength < 0 ? 'rgba(244, 63, 94, 0.12)' : 'rgba(255, 255, 255, 0.06)');
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + cos * 150, cy + sin * 150);
            ctx.stroke();

            // Animate moving flow dots
            if (strength !== 0) {
                const speed = Math.abs(strength) * 0.4;
                const offset = (t * speed) % 150;
                const distance = strength > 0 ? offset : (150 - offset);
                
                ctx.beginPath();
                ctx.arc(cx + cos * distance, cy + sin * distance, 3, 0, Math.PI * 2);
                ctx.fillStyle = strength > 0 ? 'var(--accent-default, #64ffda)' : '#f43f5e';
                ctx.fill();
            }
        }
    },

    drawCurl(ctx, w, h, t, vorticity) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw center rotation core
        ctx.beginPath();
        ctx.arc(cx, cy, 8, 0, Math.PI * 2);
        ctx.fillStyle = vorticity !== 0 ? 'var(--accent-default, #64ffda)' : 'rgba(255, 255, 255, 0.2)';
        ctx.fill();

        // Draw rotating circles
        const rings = [35, 65, 95];
        rings.forEach((r, idx) => {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.stroke();

            // Rotating flow node
            if (vorticity !== 0) {
                const dir = vorticity > 0 ? 1 : -1;
                const speed = Math.abs(vorticity) * 0.08 / (idx + 1);
                const angle = t * speed * dir + (idx * Math.PI / 1.5);
                
                const px = cx + Math.cos(angle) * r;
                const py = cy + Math.sin(angle) * r;
                
                ctx.beginPath();
                ctx.arc(px, py, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = vorticity > 0 ? 'var(--accent-default, #64ffda)' : '#a78bfa';
                ctx.fill();
            }
        });
    },

    drawWave(ctx, w, h, t, freq, amp) {
        ctx.strokeStyle = 'var(--accent-default, #64ffda)';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = 'rgba(100, 255, 218, 0.4)';
        ctx.shadowBlur = 10;
        
        ctx.beginPath();
        for (let x = 0; x < w; x++) {
            const k = 0.04;
            const omega = freq * 0.05;
            const y = h / 2 + (amp * 10) * Math.sin(k * x - omega * t);
            
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        ctx.shadowBlur = 0;
    },

    drawScaling(ctx, w, h, t, input) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw Slope Line
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(20, h - 20);
        ctx.lineTo(w - 20, 20);
        ctx.stroke();

        // Draw active slider position dot
        const startX = 40;
        const endX = w - 40;
        const startY = h - 30;
        const endY = 30;

        const currentX = startX + (endX - startX) * (input / 10);
        const currentY = startY + (endY - startY) * (input / 10);

        ctx.beginPath();
        ctx.arc(currentX, currentY, 6, 0, Math.PI * 2);
        ctx.fillStyle = '#ffd700';
        ctx.shadowColor = 'rgba(255, 215, 0, 0.4)';
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
    },

    toggleSonification() {
        if (this.isSonifying) {
            this.stopSonification();
        } else {
            this.startSonification();
        }
    },

    startSonification() {
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContextClass();
            
            this.audioOscillator = this.audioCtx.createOscillator();
            this.audioGain = this.audioCtx.createGain();

            this.audioOscillator.type = 'sine';
            
            // Connect nodes
            this.audioOscillator.connect(this.audioGain);
            this.audioGain.connect(this.audioCtx.destination);
            
            this.audioOscillator.start();
            this.isSonifying = true;

            // Set button state
            if (this.sonifyToggleBtn) {
                this.sonifyToggleBtn.innerHTML = `
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/></svg>
                    Stop Audio
                `;
                this.sonifyToggleBtn.style.background = 'rgba(244, 63, 94, 0.1)';
                this.sonifyToggleBtn.style.color = '#f43f5e';
                this.sonifyToggleBtn.style.borderColor = 'rgba(244, 63, 94, 0.3)';
            }

            this.updateSonificationParameters();
        } catch (e) {
            console.warn('Audio Context failed to initialize:', e);
        }
    },

    stopSonification() {
        if (this.audioOscillator) {
            try {
                this.audioOscillator.stop();
            } catch (err) {}
            this.audioOscillator.disconnect();
            this.audioOscillator = null;
        }
        if (this.audioGain) {
            this.audioGain.disconnect();
            this.audioGain = null;
        }
        if (this.audioCtx) {
            this.audioCtx.close();
            this.audioCtx = null;
        }
        
        this.isSonifying = false;
        
        // Reset button state
        if (this.sonifyToggleBtn) {
            this.sonifyToggleBtn.innerHTML = `
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                Sonify Math
            `;
            this.sonifyToggleBtn.style.background = 'rgba(100, 255, 218, 0.05)';
            this.sonifyToggleBtn.style.color = 'var(--accent-default, #64ffda)';
            this.sonifyToggleBtn.style.borderColor = 'rgba(100, 255, 218, 0.2)';
        }
    },

    updateSonificationParameters() {
        if (!this.isSonifying || !this.audioOscillator || !this.audioGain) return;

        let baseFrequency = 300;
        let gainVal = 0.15;

        if (this.sandboxType === 'divergence') {
            const strength = this.sandboxParams['strength'] || 0;
            baseFrequency = 300 + (strength * 20);
            gainVal = 0.05 + (Math.abs(strength) * 0.02);
        } else if (this.sandboxType === 'curl') {
            const vorticity = this.sandboxParams['vorticity'] || 0;
            baseFrequency = 350 + (vorticity * 15);
            gainVal = 0.05 + (Math.abs(vorticity) * 0.02);
        } else if (this.sandboxType === 'wave') {
            const freq = this.sandboxParams['frequency'] || 5;
            const amp = this.sandboxParams['amplitude'] || 4;
            baseFrequency = 200 + (freq * 30);
            gainVal = 0.02 + (amp * 0.03);
        } else {
            const input = this.sandboxParams['input'] || 5;
            baseFrequency = 250 + (input * 40);
        }

        const t = this.audioCtx.currentTime;
        this.audioOscillator.frequency.setTargetAtTime(baseFrequency, t, 0.05);
        this.audioGain.gain.setTargetAtTime(gainVal, t, 0.05);
    }
};

if (typeof window !== 'undefined') {
    window.ExplainerSimulations = ExplainerSimulations;
    if (window.EquationExplainer) {
        Object.assign(window.EquationExplainer, ExplainerSimulations);
    }
}
