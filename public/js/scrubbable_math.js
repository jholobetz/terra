/**
 * 🌌 PHYSICS LAB: Scrubbable Formula Engine (scrubbable_math.js)
 * Phase 2.4 - The Reactive Mathematical Worldline
 * 
 * Bret Victor-inspired tactile mathematical medium for MathJax 3.x.
 * Converts rendered equation parameter tokens into pointer-interactive,
 * horizontal-scrubbing controllers with real-time feedback, floating HUD badges,
 * bounds clamping, and keyboard accessibility.
 */

(function(global) {
    'use strict';

    class ScrubbableMath {
        /**
         * @param {Object} options
         * @param {HTMLElement|string} [options.container=document] - Element scope to watch for scrub tokens
         * @param {Function} [options.onChange] - Callback fired on drag: (varId, value, isFinal) => {}
         * @param {Function} [options.onStart] - Callback fired when drag begins: (varId, value) => {}
         * @param {Function} [options.onEnd] - Callback fired when drag ends: (varId, value) => {}
         * @param {number} [options.sensitivity=1.0] - Drag sensitivity multiplier
         * @param {Object} [options.variables={}] - Variable metadata dictionary { [varId]: { min, max, step, default, name, unit } }
         */
        constructor(options = {}) {
            this.options = Object.assign({
                container: document,
                onChange: null,
                onStart: null,
                onEnd: null,
                sensitivity: 1.0,
                variables: {}
            }, options);

            this.container = typeof this.options.container === 'string'
                ? document.querySelector(this.options.container)
                : this.options.container;

            this.activeToken = null;
            this.dragState = null;
            this.hudElement = null;

            this.onPointerDown = this.onPointerDown.bind(this);
            this.onPointerMove = this.onPointerMove.bind(this);
            this.onPointerUp = this.onPointerUp.bind(this);
            this.onKeyDown = this.onKeyDown.bind(this);

            this.initHUD();
            this.injectStyles();
        }

        /**
         * Dynamically merges or updates variable profiles.
         */
        setVariables(variables = {}) {
            this.options.variables = Object.assign(this.options.variables || {}, variables);
            if (this.container) {
                this.attach();
            }
        }

        /**
         * Resolves variable metadata and attributes from element or variable profile registry.
         */
        getTokenConfig(token) {
            let varId = token.dataset.var;
            let min = parseFloat(token.dataset.min);
            let max = parseFloat(token.dataset.max);
            let step = parseFloat(token.dataset.step);
            let currentVal = parseFloat(token.dataset.val);
            let name = token.dataset.name;
            let unit = token.dataset.unit;

            // Extract from class string if dataset is incomplete
            const classAttr = token.getAttribute('class') || '';
            if (!varId) {
                // Match scrub-var-NAME or scrub-NAME or data-var="NAME"
                const classDataVar = classAttr.match(/data-var=["']?([a-zA-Z0-9_]+)/);
                if (classDataVar) {
                    varId = classDataVar[1];
                } else {
                    const matchVar = classAttr.match(/scrub-(?:var-|token-)?([a-zA-Z0-9_]+)/);
                    if (matchVar && matchVar[1] !== 'token') {
                        varId = matchVar[1];
                    } else {
                        varId = 'x';
                    }
                }
            }

            // Extract min/max/step/val/name/unit if embedded in class attribute string
            if (isNaN(min)) {
                const matchMin = classAttr.match(/data-min=["']?([0-9.-]+)/);
                if (matchMin) min = parseFloat(matchMin[1]);
            }
            if (isNaN(max)) {
                const matchMax = classAttr.match(/data-max=["']?([0-9.-]+)/);
                if (matchMax) max = parseFloat(matchMax[1]);
            }
            if (isNaN(step)) {
                const matchStep = classAttr.match(/data-step=["']?([0-9.-]+)/);
                if (matchStep) step = parseFloat(matchStep[1]);
            }
            if (isNaN(currentVal)) {
                const matchVal = classAttr.match(/data-val=["']?([0-9.-]+)/);
                if (matchVal) currentVal = parseFloat(matchVal[1]);
            }
            if (!name) {
                const matchName = classAttr.match(/data-name=["']?([^"']+)["']?/);
                if (matchName) name = matchName[1];
            }
            if (unit === undefined || unit === null || unit === '') {
                const matchUnit = classAttr.match(/data-unit=["']?([^"']*)["']?/);
                if (matchUnit) unit = matchUnit[1];
            }

            // Check options.variables profile
            const varDef = (this.options.variables && this.options.variables[varId]) || {};
            min = !isNaN(min) ? min : (varDef.min !== undefined ? varDef.min : 0);
            max = !isNaN(max) ? max : (varDef.max !== undefined ? varDef.max : 10);
            step = !isNaN(step) ? step : (varDef.step !== undefined ? varDef.step : 0.05);
            currentVal = !isNaN(currentVal) ? currentVal : (varDef.default !== undefined ? varDef.default : min);
            name = name || varDef.name || varId;
            unit = unit !== undefined && unit !== null && unit !== '' ? unit : (varDef.unit || '');

            // Store onto dataset for fast continuous access
            token.dataset.var = varId;
            token.dataset.min = min;
            token.dataset.max = max;
            token.dataset.step = step;
            token.dataset.val = currentVal;
            token.dataset.name = name;
            token.dataset.unit = unit;

            return { varId, min, max, step, currentVal, name, unit };
        }

        /**
         * Creates the singleton floating HUD tooltip badge.
         */
        initHUD() {
            if (document.getElementById('scrub-math-hud')) {
                this.hudElement = document.getElementById('scrub-math-hud');
                return;
            }

            const hud = document.createElement('div');
            hud.id = 'scrub-math-hud';
            hud.className = 'scrub-math-hud';
            hud.innerHTML = `
                <div class="hud-label-row">
                    <span class="hud-var-name">Variable</span>
                    <span class="hud-var-unit"></span>
                </div>
                <div class="hud-value-row">
                    <span class="hud-arrow-left">◀</span>
                    <span class="hud-var-value">0.00</span>
                    <span class="hud-arrow-right">▶</span>
                </div>
                <div class="hud-track">
                    <div class="hud-progress"></div>
                </div>
            `;
            document.body.appendChild(hud);
            this.hudElement = hud;
        }

        /**
         * Injects necessary CSS for scrubbable tokens and HUD badge.
         */
        injectStyles() {
            if (document.getElementById('scrubbable-math-styles')) return;

            const style = document.createElement('style');
            style.id = 'scrubbable-math-styles';
            style.textContent = `
                /* Scrubbable Token Base */
                .scrub-token {
                    cursor: ew-resize !important;
                    user-select: none !important;
                    -webkit-user-select: none !important;
                    touch-action: none !important;
                }

                /* HTML Token Styling */
                span.scrub-token, div.scrub-token {
                    display: inline-block !important;
                    cursor: ew-resize !important;
                    color: #38bdf8 !important;
                    font-weight: 700 !important;
                    border-bottom: 1.5px dashed rgba(56, 189, 248, 0.6) !important;
                    padding: 0 3px !important;
                    margin: 0 1px !important;
                    border-radius: 4px !important;
                    transition: background 0.15s ease, color 0.15s ease, box-shadow 0.15s ease !important;
                    position: relative;
                }

                span.scrub-token:hover, span.scrub-token:focus {
                    background: rgba(56, 189, 248, 0.18) !important;
                    color: #ffffff !important;
                    border-bottom-color: #38bdf8 !important;
                    box-shadow: 0 0 10px rgba(56, 189, 248, 0.4) !important;
                    outline: none !important;
                }

                span.scrub-token.scrubbing-active {
                    background: rgba(56, 189, 248, 0.3) !important;
                    color: #ffffff !important;
                    border-bottom-style: solid !important;
                    box-shadow: 0 0 18px rgba(56, 189, 248, 0.6) !important;
                }

                /* MathJax SVG Token Styling (<g class="scrub-token">) */
                g.scrub-token {
                    cursor: ew-resize !important;
                    pointer-events: all !important;
                }

                g.scrub-token path, g.scrub-token use {
                    cursor: ew-resize !important;
                    pointer-events: all !important;
                    fill: #38bdf8 !important;
                    transition: fill 0.15s ease, filter 0.15s ease !important;
                }

                g.scrub-token:hover path, g.scrub-token:hover use,
                g.scrub-token:focus path, g.scrub-token:focus use {
                    fill: #7dd3fc !important;
                    filter: drop-shadow(0 0 6px rgba(56, 189, 248, 0.9)) !important;
                    outline: none !important;
                }

                g.scrub-token.scrubbing-active path, g.scrub-token.scrubbing-active use {
                    fill: #ffffff !important;
                    filter: drop-shadow(0 0 12px rgba(56, 189, 248, 1)) !important;
                }

                /* Floating HUD Badge */
                .scrub-math-hud {
                    position: fixed;
                    z-index: 10000;
                    pointer-events: none;
                    opacity: 0;
                    visibility: hidden;
                    transform: translate(-50%, -100%) translateY(-10px) scale(0.95);
                    transition: opacity 0.15s cubic-bezier(0.16, 1, 0.3, 1), transform 0.15s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.15s;
                    background: rgba(10, 15, 26, 0.92);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    border: 1px solid rgba(56, 189, 248, 0.4);
                    border-radius: 10px;
                    padding: 8px 14px;
                    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(56, 189, 248, 0.2);
                    min-width: 130px;
                    text-align: center;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                }

                .scrub-math-hud.visible {
                    opacity: 1;
                    visibility: visible;
                    transform: translate(-50%, -100%) translateY(-14px) scale(1);
                }

                .hud-label-row {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 6px;
                    margin-bottom: 4px;
                }

                .hud-var-name {
                    font-size: 0.72rem;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    color: var(--text-muted, #94a3b8);
                }

                .hud-var-unit {
                    font-size: 0.72rem;
                    color: #38bdf8;
                    font-family: monospace;
                }

                .hud-value-row {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 8px;
                    margin-bottom: 6px;
                }

                .hud-arrow-left, .hud-arrow-right {
                    font-size: 0.65rem;
                    color: rgba(255, 255, 255, 0.3);
                }

                .hud-var-value {
                    font-family: "Space Mono", monospace, monospace;
                    font-size: 1.15rem;
                    font-weight: 700;
                    color: #ffffff;
                }

                .hud-track {
                    width: 100%;
                    height: 3px;
                    background: rgba(255, 255, 255, 0.12);
                    border-radius: 2px;
                    overflow: hidden;
                }

                .hud-progress {
                    height: 100%;
                    width: 50%;
                    background: linear-gradient(90deg, #38bdf8, #34d399);
                    border-radius: 2px;
                    transition: width 0.05s ease-out;
                }
            `;
            document.head.appendChild(style);
        }

        /**
         * Scans the container for .scrub-token elements and attaches interactive listeners.
         */
        attach() {
            if (!this.container) return;

            const tokens = this.container.querySelectorAll('.scrub-token');
            tokens.forEach(token => {
                this.getTokenConfig(token);

                // Ensure focusable for keyboard accessibility
                if (!token.hasAttribute('tabindex')) {
                    token.setAttribute('tabindex', '0');
                }
                token.removeEventListener('pointerdown', this.onPointerDown);
                token.addEventListener('pointerdown', this.onPointerDown);

                token.removeEventListener('keydown', this.onKeyDown);
                token.addEventListener('keydown', this.onKeyDown);
            });
        }

        /**
         * Pointerdown handler initiating scrub interaction.
         */
        onPointerDown(e) {
            // Only primary mouse button or touch
            if (e.button !== 0 && e.pointerType === 'mouse') return;

            e.preventDefault();
            e.stopPropagation();

            const token = e.currentTarget;
            this.activeToken = token;

            const cfg = this.getTokenConfig(token);
            const varId = cfg.varId;
            const min = cfg.min;
            const max = cfg.max;
            const step = cfg.step;
            const currentVal = cfg.currentVal;
            const name = cfg.name;
            const unit = cfg.unit;

            this.dragState = {
                startX: e.clientX,
                startY: e.clientY,
                startVal: currentVal,
                currentVal: currentVal,
                min: min,
                max: max,
                step: step,
                varId: varId,
                name: name,
                unit: unit,
                pointerId: e.pointerId
            };

            token.classList.add('scrubbing-active');
            try {
                token.setPointerCapture(e.pointerId);
            } catch (err) {
                // Ignore if capture fails in edge browsers
            }

            window.addEventListener('pointermove', this.onPointerMove);
            window.addEventListener('pointerup', this.onPointerUp);
            window.addEventListener('pointercancel', this.onPointerUp);

            this.updateHUD(token, currentVal, name, unit, min, max);
            this.showHUD(token);

            if (typeof this.options.onStart === 'function') {
                this.options.onStart(varId, currentVal);
            }
        }

        /**
         * Pointermove handler calculating horizontal delta and applying precision scrub.
         */
        onPointerMove(e) {
            if (!this.dragState || !this.activeToken) return;

            e.preventDefault();
            const deltaX = e.clientX - this.dragState.startX;

            // Compute value change with pixel sensitivity scaling
            // 200px drag = full range traversal by default
            const range = this.dragState.max - this.dragState.min;
            const pxPerUnit = 240 / (range || 1);
            const valueChange = (deltaX / pxPerUnit) * this.options.sensitivity;

            let rawVal = this.dragState.startVal + valueChange;

            // Clamping
            rawVal = Math.max(this.dragState.min, Math.min(this.dragState.max, rawVal));

            // Step quantization
            const step = this.dragState.step;
            const stepsCount = Math.round((rawVal - this.dragState.min) / step);
            const quantizedVal = parseFloat((this.dragState.min + stepsCount * step).toFixed(4));

            if (quantizedVal !== this.dragState.currentVal) {
                this.dragState.currentVal = quantizedVal;
                this.activeToken.dataset.val = quantizedVal;

                this.updateHUD(
                    this.activeToken,
                    quantizedVal,
                    this.dragState.name,
                    this.dragState.unit,
                    this.dragState.min,
                    this.dragState.max
                );

                if (typeof this.options.onChange === 'function') {
                    this.options.onChange(this.dragState.varId, quantizedVal, false);
                }
            }
        }

        /**
         * Pointerup handler terminating drag.
         */
        onPointerUp(e) {
            if (!this.dragState) return;

            window.removeEventListener('pointermove', this.onPointerMove);
            window.removeEventListener('pointerup', this.onPointerUp);
            window.removeEventListener('pointercancel', this.onPointerUp);

            if (this.activeToken) {
                this.activeToken.classList.remove('scrubbing-active');
                try {
                    this.activeToken.releasePointerCapture(this.dragState.pointerId);
                } catch (err) {}
            }

            this.hideHUD();

            if (typeof this.options.onChange === 'function') {
                this.options.onChange(this.dragState.varId, this.dragState.currentVal, true);
            }

            if (typeof this.options.onEnd === 'function') {
                this.options.onEnd(this.dragState.varId, this.dragState.currentVal);
            }

            this.dragState = null;
            this.activeToken = null;
        }

        /**
         * Keyboard accessibility handler (Arrow keys).
         */
        onKeyDown(e) {
            const token = e.currentTarget;
            if (!token) return;

            let delta = 0;
            if (e.key === 'ArrowRight' || e.key === 'ArrowUp') {
                delta = 1;
            } else if (e.key === 'ArrowLeft' || e.key === 'ArrowDown') {
                delta = -1;
            } else {
                return;
            }

            e.preventDefault();

            const cfg = this.getTokenConfig(token);
            const varId = cfg.varId;
            const min = cfg.min;
            const max = cfg.max;
            const step = cfg.step;
            let currentVal = cfg.currentVal;
            const name = cfg.name;
            const unit = cfg.unit;

            currentVal = Math.max(min, Math.min(max, currentVal + delta * step));
            currentVal = parseFloat(currentVal.toFixed(4));
            token.dataset.val = currentVal;

            this.updateHUD(token, currentVal, name, unit, min, max);
            this.showHUD(token);

            if (typeof this.options.onChange === 'function') {
                this.options.onChange(varId, currentVal, true);
            }

            clearTimeout(this.keyTimeout);
            this.keyTimeout = setTimeout(() => this.hideHUD(), 1200);
        }

        /**
         * Updates contents and position of floating HUD element.
         */
        updateHUD(token, val, name, unit, min, max) {
            if (!this.hudElement) return;

            const nameEl = this.hudElement.querySelector('.hud-var-name');
            const unitEl = this.hudElement.querySelector('.hud-var-unit');
            const valEl = this.hudElement.querySelector('.hud-var-value');
            const progEl = this.hudElement.querySelector('.hud-progress');

            if (nameEl) nameEl.textContent = name;
            if (unitEl) unitEl.textContent = unit;
            if (valEl) valEl.textContent = val.toFixed(2);

            // Progress bar
            const pct = Math.max(0, Math.min(100, ((val - min) / (max - min || 1)) * 100));
            if (progEl) progEl.style.width = `${pct}%`;

            // Position HUD right above the token
            const rect = token.getBoundingClientRect();
            const top = rect.top;
            const left = rect.left + rect.width * 0.5;

            this.hudElement.style.top = `${top}px`;
            this.hudElement.style.left = `${left}px`;
        }

        showHUD(token) {
            if (!this.hudElement) return;
            this.hudElement.classList.add('visible');
        }

        hideHUD() {
            if (!this.hudElement) return;
            this.hudElement.classList.remove('visible');
        }

        /**
         * Updates a token's stored value and triggers HUD refresh if currently focused.
         */
        setTokenValue(varId, newVal) {
            if (!this.container) return;
            const tokens = this.container.querySelectorAll(`.scrub-token[data-var="${varId}"], .scrub-token.scrub-${varId}, .scrub-token.scrub-var-${varId}`);
            tokens.forEach(token => {
                token.dataset.val = newVal;
            });
        }
    }

    // Expose to global scope
    global.ScrubbableMath = ScrubbableMath;

})(typeof window !== 'undefined' ? window : this);
