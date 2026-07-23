<div class="transformer-container">
    <div class="transformer-header">
        <h1>Symbolic Legendre Transformer</h1>
        <p class="tagline">Explore the duality of mechanics by mapping Lagrangian equations to their canonical Hamiltonian representations symbolically.</p>
    </div>

    <div class="transformer-grid">
        <!-- Left Column: Inputs & Presets -->
        <div class="transformer-panel-left">
            <!-- Presets Card -->
            <div class="glass-card presets-card">
                <h3>Physical Presets</h3>
                <p class="ref-sub">Select a classical configuration to populate its Lagrangian.</p>
                <div class="preset-buttons">
                    <button class="preset-btn" data-preset="sho">Harmonic Oscillator</button>
                    <button class="preset-btn" data-preset="pendulum">Simple Pendulum</button>
                    <button class="preset-btn" data-preset="em_field">Charged Particle in EM Field</button>
                    <button class="preset-btn" data-preset="relativistic">Relativistic Particle</button>
                </div>
            </div>

            <!-- Configuration Card -->
            <div class="glass-card config-card">
                <h3>Configuration Parameters</h3>
                
                <div class="input-group-row">
                    <div class="input-field-wrapper">
                        <label for="coord-var">Coordinate Variable (<span class="math-sub">\(q\)</span>)</label>
                        <input type="text" id="coord-var" value="q" placeholder="e.g. q, x, theta" />
                    </div>
                    <div class="input-field-wrapper">
                        <label for="velocity-var">Velocity Variable (<span class="math-sub">\(\dot{q}\)</span>)</label>
                        <input type="text" id="velocity-var" value="dq" placeholder="e.g. dq, v, theta_dot" />
                    </div>
                </div>

                <div class="input-field-wrapper full-width">
                    <label for="parameter-vars">Constant Parameters (comma-separated)</label>
                    <input type="text" id="parameter-vars" value="m, k, g, l, q_charge, A_pot, c" placeholder="e.g. m, k, g, l" />
                    <small class="help-text">Constants used in the Lagrangian that are not coordinates.</small>
                </div>

                <div class="input-field-wrapper full-width">
                    <label for="lagrangian-expr">Lagrangian Function <span class="math-sub">\(L(q, \dot{q})\)</span></label>
                    <textarea id="lagrangian-expr" rows="3" placeholder="e.g. 0.5 * m * dq^2 - 0.5 * k * q^2">0.5 * m * dq^2 - 0.5 * k * q^2</textarea>
                    <small class="help-text">Use standard operators (*, /, +, -, ^) and write the velocity variable exactly as defined above.</small>
                </div>

                <button id="compute-btn" class="btn btn-primary btn-block">
                    Compute Legendre Duality &rarr;
                </button>
            </div>
        </div>

        <!-- Right Column: Outputs -->
        <div class="transformer-panel-right">
            <!-- Output Viewer Card -->
            <div class="glass-card main-viewer-card" id="output-card">
                
                <!-- Welcome/Placeholder State -->
                <div id="output-placeholder" class="output-placeholder">
                    <div class="placeholder-icon">🧮</div>
                    <h3>Duality Solver Ready</h3>
                    <p>Configure a Lagrangian system on the left and click <strong>Compute Legendre Duality</strong> to perform the symbolic transformation.</p>
                </div>

                <!-- Error State -->
                <div id="output-error" class="output-error" style="display: none;">
                    <div class="error-badge">⚠️ Transformation Error</div>
                    <p id="error-message"></p>
                </div>

                <!-- Output Content (hidden initially) -->
                <div id="output-content" class="output-content" style="display: none;">
                    <div class="viewer-header-info">
                        <span class="category-badge">Legendre Transformation</span>
                        <h2>Canonical Hamiltonian Structure</h2>
                    </div>

                    <!-- Output Tab Bar -->
                    <div class="rep-tabs-wrapper">
                        <div class="rep-tabs">
                            <button class="tab-btn active" data-tab="hamiltonian">Hamiltonian (H)</button>
                            <button class="tab-btn" data-tab="equations">Equations of Motion</button>
                            <button class="tab-btn" data-tab="geometry">Phase Space Geometry</button>
                        </div>
                    </div>

                    <!-- Tab Section: Hamiltonian -->
                    <div class="tab-panel active" id="tab-hamiltonian">
                        <div class="math-display-container">
                            <div class="math-label-bar">
                                <span class="math-label">Input Lagrangian:</span>
                            </div>
                            <div class="math-box">
                                <div id="latex-lagrangian" class="math-render-field"></div>
                            </div>
                        </div>

                        <div class="math-display-container">
                            <div class="math-label-bar">
                                <span class="math-label">Canonical Momentum Definition (<span class="math-sub">\(p = \frac{\partial L}{\partial \dot{q}}\)</span>):</span>
                            </div>
                            <div class="math-box">
                                <div id="latex-momentum" class="math-render-field"></div>
                            </div>
                        </div>

                        <div class="math-display-container">
                            <div class="math-label-bar">
                                <span class="math-label">Inverted Velocity Relation (<span class="math-sub">\(\dot{q}(p)\)</span>):</span>
                            </div>
                            <div class="math-box">
                                <div id="latex-inverted-vel" class="math-render-field"></div>
                            </div>
                        </div>

                        <div class="math-display-container hero-container">
                            <div class="math-label-bar">
                                <span class="math-label">Hamiltonian Function (<span class="math-sub">\(H(q, p) = p\dot{q} - L\)</span>):</span>
                            </div>
                            <div class="math-box hero-box">
                                <div id="latex-hamiltonian" class="math-render-field"></div>
                            </div>
                            <button id="copy-latex-btn" class="mathjax-inspector-btn copy-hamiltonian-btn">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
                                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                </svg>
                                <span class="btn-text">Copy Hamiltonian LaTeX</span>
                            </button>
                        </div>
                    </div>

                    <!-- Tab Section: Equations of Motion -->
                    <div class="tab-panel" id="tab-equations">
                        <h3>Hamilton's Equations of Motion</h3>
                        <p class="section-desc">The Hamiltonian formulation yields two first-order symmetric differential equations, replacing the single second-order Euler-Lagrange equation.</p>

                        <div class="math-display-container">
                            <div class="math-label-bar">
                                <span class="math-label">Velocity Equation (<span class="math-sub">\(\dot{q} = \frac{\partial H}{\partial p}\)</span>):</span>
                            </div>
                            <div class="math-box">
                                <div id="latex-eq-velocity" class="math-render-field"></div>
                            </div>
                        </div>

                        <div class="math-display-container">
                            <div class="math-label-bar">
                                <span class="math-label">Force Equation (<span class="math-sub">\(\dot{p} = -\frac{\partial H}{\partial q}\)</span>):</span>
                            </div>
                            <div class="math-box">
                                <div id="latex-eq-force" class="math-render-field"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Tab Section: Geometry -->
                    <div class="tab-panel" id="tab-geometry">
                        <h3>Phase Space Topology</h3>
                        
                        <div class="geometry-insight-grid">
                            <div class="insight-card">
                                <h4>Degrees of Freedom</h4>
                                <p>The system possesses <strong>1 degree of freedom</strong>. In the Lagrangian formulation, this is represented by the tangent bundle $TQ$ spanned by $(q, \dot{q})$. In the Hamiltonian formulation, this is mapped to a <strong>2D Phase Space Manifold</strong> spanned by the coordinate $q$ and its momentum $p$.</p>
                            </div>
                            <div class="insight-card">
                                <h4>Conservation &amp; Energy</h4>
                                <p id="conservation-text">Since the Lagrangian $L$ contains no explicit time dependency ($\partial L/\partial t = 0$), the Hamiltonian $H(q, p)$ represents a conserved quantity representing the total energy of the system ($dH/dt = 0$), and orbits in phase space are constrained to curves of constant energy.</p>
                            </div>
                            <div class="insight-card full-width-card">
                                <h4>Symplectic Structure</h4>
                                <p>Hamilton's equations conserve phase space volume over time. This mathematical property is known as **Liouville's Theorem**, meaning the flow in phase space is a volume-preserving diffeomorphism generated by the symplectic 2-form $d\theta = dq \wedge dp$.</p>
                            </div>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.transformer-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.transformer-header {
    margin-bottom: 30px;
    text-align: center;
}

.transformer-header h1 {
    font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.transformer-header .tagline {
    color: var(--text-muted);
    font-size: 1.1rem;
    max-width: 700px;
    margin: 0 auto;
}

.transformer-grid {
    display: grid;
    grid-template-columns: 420px 1fr;
    gap: 30px;
    align-items: start;
}

/* Glassmorphic Panel Cards */
.glass-card {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.glass-card h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.25rem;
    margin: 0 0 8px 0;
    color: #ffffff;
}

.ref-sub {
    font-size: 0.85rem;
    color: var(--text-muted);
    margin: 0 0 20px 0;
}

/* Presets Grid */
.preset-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.preset-btn {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-color);
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    font-family: 'Inter', sans-serif;
}

.preset-btn:hover {
    background: rgba(100, 255, 218, 0.08);
    border-color: rgba(100, 255, 218, 0.3);
    color: var(--accent-color);
    transform: translateY(-1px);
}

.preset-btn:active {
    transform: translateY(0);
}

/* Input Fields */
.input-group-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 16px;
}

.input-field-wrapper {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
}

.input-field-wrapper.full-width {
    margin-bottom: 20px;
}

.input-field-wrapper label {
    font-size: 0.85rem;
    font-weight: 600;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 4px;
}

.math-sub {
    font-family: 'Space Grotesk', serif;
    font-style: italic;
    color: var(--accent-color);
}

.input-field-wrapper input[type="text"], 
.input-field-wrapper textarea {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #ffffff;
    padding: 10px 14px;
    font-family: 'Fira Code', 'Courier New', monospace;
    font-size: 0.9rem;
    transition: all 0.2s ease;
}

.input-field-wrapper textarea {
    resize: vertical;
}

.input-field-wrapper input:focus, 
.input-field-wrapper textarea:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.15);
    background: rgba(15, 23, 42, 0.85);
}

.help-text {
    font-size: 0.75rem;
    color: var(--text-muted);
    opacity: 0.8;
    margin-top: 4px;
}

.btn-block {
    width: 100%;
    padding: 12px;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 8px;
    cursor: pointer;
    font-family: 'Space Grotesk', sans-serif;
}

/* Right Panel / Outputs Viewport */
.main-viewer-card {
    min-height: 540px;
    display: flex;
    flex-direction: column;
}

/* Placeholder State */
.output-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    flex-grow: 1;
    text-align: center;
    padding: 40px;
    color: var(--text-muted);
}

.placeholder-icon {
    font-size: 4rem;
    margin-bottom: 20px;
    opacity: 0.35;
    animation: pulseIcon 3s infinite ease-in-out;
}

@keyframes pulseIcon {
    0%, 100% { transform: scale(1); opacity: 0.35; }
    50% { transform: scale(1.05); opacity: 0.55; }
}

.output-placeholder h3 {
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-size: 1.4rem;
    margin: 0 0 10px 0;
}

.output-placeholder p {
    max-width: 440px;
    font-size: 0.95rem;
    line-height: 1.5;
}

/* Error State */
.output-error {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 20px;
}

.error-badge {
    color: #ef4444;
    font-weight: bold;
    font-size: 0.9rem;
    margin-bottom: 6px;
    font-family: 'Space Grotesk', sans-serif;
}

.output-error p {
    margin: 0;
    font-size: 0.9rem;
    color: var(--text-color);
}

/* Tab Bar inside Output */
.rep-tabs-wrapper {
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 24px;
}

.rep-tabs {
    display: flex;
    gap: 16px;
    margin-bottom: -1px;
}

.tab-btn {
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    color: var(--text-muted);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem;
    font-weight: 500;
    padding: 8px 4px 12px 4px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.tab-btn:hover {
    color: #ffffff;
}

.tab-btn.active {
    color: var(--accent-color);
    border-bottom-color: var(--accent-color);
    font-weight: 600;
}

/* Output Containers */
.tab-panel {
    display: none;
}

.tab-panel.active {
    display: block;
}

.math-display-container {
    background: rgba(3, 7, 18, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 20px;
}

.math-label-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--text-muted);
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.math-box {
    text-align: center;
    padding: 12px 0;
    overflow-x: auto;
}

.math-render-field {
    font-size: 1.25rem;
    color: #ffffff;
}

/* Hero Box Highlight */
.hero-container {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(100, 255, 218, 0.25);
    box-shadow: 0 0 15px rgba(100, 255, 218, 0.05);
    position: relative;
}

.hero-box {
    padding: 24px 0;
}

.hero-box .math-render-field {
    color: #ffd700;
    font-size: 1.5rem;
}

.copy-hamiltonian-btn {
    margin: 8px auto 0 auto;
}

/* Geometry Insights */
.geometry-insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 10px;
}

.geometry-insight-grid .insight-card {
    background: rgba(15, 23, 42, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 10px;
    padding: 16px 20px;
}

.geometry-insight-grid .insight-card.full-width-card {
    grid-column: span 2;
}

.geometry-insight-grid h4 {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--accent-color);
    font-size: 1rem;
    margin: 0 0 8px 0;
}

.geometry-insight-grid p {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--text-muted);
}

.section-desc {
    font-size: 0.9rem;
    color: var(--text-muted);
    margin: -10px 0 20px 0;
    line-height: 1.5;
}

/* Responsive adjustments */
@media (max-width: 900px) {
    .transformer-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<!-- math.js for symbolic differentiation and simplification -->
<script src="/js/lib/math.min.js"></script>
<!-- Client-side controller script -->
<script src="/js/legendre_transformer.js" defer></script>
