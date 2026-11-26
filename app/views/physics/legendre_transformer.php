<div class="transformer-container">
    <header class="transformer-header">
        <h1>Symbolic Legendre Transformer</h1>
        <p class="tagline">Live SymPy Computer Algebra engine transforming Lagrangians \(L(q, \dot{q})\) into canonical Hamiltonians \(H(q, p)\), velocity Hessians, and phase-space equations of motion.</p>
    </header>

    <div class="transformer-grid">
        <!-- Left Column: Presets & Custom Lagrangian Editor -->
        <aside class="transformer-panel-left" aria-label="Lagrangian Presets and Parameters">
            <!-- Presets Card -->
            <div class="glass-card presets-card">
                <div class="card-head-row">
                    <h2>Physical Presets</h2>
                    <span class="pill-count">10 Systems</span>
                </div>
                <div class="preset-buttons">
                    <button class="preset-btn active" data-preset="sho">Harmonic Oscillator</button>
                    <button class="preset-btn" data-preset="pendulum">Simple Pendulum</button>
                    <button class="preset-btn" data-preset="duffing">Duffing Oscillator</button>
                    <button class="preset-btn" data-preset="relativistic">Relativistic Particle</button>
                    <button class="preset-btn" data-preset="em_field">Charged Particle (EM)</button>
                    <button class="preset-btn" data-preset="coriolis">Rotating Frame</button>
                    <button class="preset-btn" data-preset="central_force">Central Force (2D)</button>
                    <button class="preset-btn" data-preset="kepler">Kepler Two-Body</button>
                    <button class="preset-btn" data-preset="spherical_3d">Spherical 3D</button>
                    <button class="preset-btn preset-singular" data-preset="singular">Singular (det W = 0)</button>
                </div>
            </div>

            <!-- Configuration Card -->
            <div class="glass-card config-card">
                <div class="card-head-row">
                    <h2>Custom Lagrangian Editor</h2>
                    <span class="pill-count">SymPy CAS</span>
                </div>

                <div class="input-group-row">
                    <div class="input-field-wrapper">
                        <label for="coord-var">Coords (\(q_i\))</label>
                        <input type="text" id="coord-var" value="q" placeholder="q or r, phi" />
                    </div>
                    <div class="input-field-wrapper">
                        <label for="velocity-var">Velocities (\(\dot{q}_i\))</label>
                        <input type="text" id="velocity-var" value="dq" placeholder="dq or dr, dphi" />
                    </div>
                </div>

                <div class="input-field-wrapper full-width">
                    <label for="parameter-vars">Constants (comma-separated)</label>
                    <input type="text" id="parameter-vars" value="m, k" placeholder="e.g. m, k, g, l" />
                </div>

                <div class="input-field-wrapper full-width">
                    <label for="lagrangian-expr">Lagrangian \(L(q, \dot{q})\)</label>
                    <textarea id="lagrangian-expr" rows="2" placeholder="0.5 * m * dq^2 - 0.5 * k * q^2">0.5 * m * dq^2 - 0.5 * k * q^2</textarea>
                </div>

                <button id="compute-btn" class="btn btn-primary btn-block">
                    Compute Legendre Duality &rarr;
                </button>
            </div>
        </aside>

        <!-- Right Column: Live Symbolic Outputs -->
        <div class="transformer-panel-right">
            <div class="glass-card main-viewer-card" id="output-card">

                <!-- Initial Loading / Placeholder State -->
                <div id="output-placeholder" class="output-placeholder">
                    <div class="placeholder-icon">🧮</div>
                    <h2>Initializing SymPy CAS Engine…</h2>
                    <p>Computing canonical momenta, velocity inversion, and Hamiltonian duality.</p>
                </div>

                <!-- Error / Singular Banner -->
                <div id="output-error" class="output-error" style="display: none;">
                    <div class="error-badge">⚠️ Transformation Notice</div>
                    <p id="error-message"></p>
                </div>

                <!-- Output Content -->
                <div id="output-content" class="output-content" style="display: none;">
                    <!-- Compact Output Header + Tab Bar -->
                    <div class="output-top-bar">
                        <div class="rep-tabs">
                            <button class="tab-btn active" data-tab="hamiltonian">Hamiltonian &amp; Steps</button>
                            <button class="tab-btn" data-tab="equations">Equations of Motion</button>
                            <button class="tab-btn" data-tab="geometry">Phase Space Geometry</button>
                        </div>
                        <span id="cas-regularity-badge" class="regularity-badge is-regular">✓ Non-Singular · det(W) ≠ 0</span>
                    </div>

                    <!-- Tab Section: Hamiltonian & 3-Step Derivation Pipeline -->
                    <div class="tab-panel active" id="tab-hamiltonian">
                        <!-- HERO RESULT: Side-by-Side L(q, q̇) ⟹ H(q, p) -->
                        <div class="duality-hero-grid">
                            <div class="duality-pane">
                                <div class="math-label-bar">
                                    <span class="math-label">Input Lagrangian \(L(q, \dot{q})\)</span>
                                </div>
                                <div class="math-box">
                                    <div id="latex-lagrangian" class="math-render-field"></div>
                                </div>
                            </div>

                            <div class="duality-arrow-badge" aria-hidden="true">⟹</div>

                            <div class="duality-pane hero-pane">
                                <div class="math-label-bar">
                                    <span class="math-label accent-hero">Derived Hamiltonian \(H(q, p) = \sum p_i\dot{q}_i - L\)</span>
                                    <button id="copy-latex-btn" class="copy-hamiltonian-btn" title="Copy Hamiltonian LaTeX">
                                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="copy-icon">
                                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                                        </svg>
                                        <span class="btn-text">Copy LaTeX</span>
                                    </button>
                                </div>
                                <div class="math-box hero-box">
                                    <div id="latex-hamiltonian" class="math-render-field"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Numbered 3-Step Symbolic Derivation Pipeline -->
                        <div class="pipeline-section">
                            <h2 class="pipeline-heading">Symbolic Derivation Pipeline</h2>
                            <div class="pipeline-steps-grid">
                                <div class="step-card">
                                    <div class="step-card-header">
                                        <span class="step-num">Step 1</span>
                                        <span class="step-title">Canonical Momenta (\(p_i = \frac{\partial L}{\partial \dot{q}_i}\))</span>
                                    </div>
                                    <div class="math-box step-math-box">
                                        <div id="latex-momentum" class="math-render-field"></div>
                                    </div>
                                </div>

                                <div class="step-card">
                                    <div class="step-card-header">
                                        <span class="step-num">Step 2</span>
                                        <span class="step-title">Velocity Inversion (\(\dot{q}_i(q, p)\))</span>
                                    </div>
                                    <div class="math-box step-math-box">
                                        <div id="latex-inverted-vel" class="math-render-field"></div>
                                    </div>
                                </div>

                                <div class="step-card step-card-wide">
                                    <div class="step-card-header">
                                        <span class="step-num">Step 3</span>
                                        <span class="step-title">Velocity Hessian &amp; Non-Singularity Check (\(W_{ij} = \frac{\partial^2 L}{\partial \dot{q}_i \partial \dot{q}_j}\))</span>
                                    </div>
                                    <div class="math-box step-math-box">
                                        <div id="latex-hessian" class="math-render-field"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Tab Section: Equations of Motion -->
                    <div class="tab-panel" id="tab-equations">
                        <h2 class="tab-section-title">Hamilton's Equations of Motion</h2>
                        <p class="section-desc">First-order symmetric phase-space flow (\(\dot{q}_i = \partial H/\partial p_i,\; \dot{p}_i = -\partial H/\partial q_i\)), replacing the second-order Euler–Lagrange equations.</p>

                        <div id="equations-container">
                            <!-- Dynamically populated for both 1-DOF and multi-DOF systems -->
                        </div>
                    </div>

                    <!-- Tab Section: Geometry -->
                    <div class="tab-panel" id="tab-geometry">
                        <h2 class="tab-section-title">Phase Space Topology</h2>

                        <div class="geometry-insight-grid">
                            <div class="insight-card">
                                <h3>Degrees of Freedom</h3>
                                <p id="dof-text">The system possesses <strong>1 degree of freedom</strong>. In the Lagrangian formulation, this is represented by the tangent bundle \(TQ\) spanned by \((q, \dot{q})\). In the Hamiltonian formulation, this is mapped to a <strong>2D Phase Space Manifold</strong> spanned by the coordinate \(q\) and its momentum \(p\).</p>
                            </div>
                            <div class="insight-card">
                                <h3>Conservation &amp; Energy</h3>
                                <p id="conservation-text">Since the Lagrangian \(L\) contains no explicit time dependency (\(\partial L/\partial t = 0\)), the Hamiltonian \(H(q, p)\) is conserved along trajectories (\(dH/dt = 0\)), constraining phase-space orbits to constant-energy hypersurfaces.</p>
                            </div>
                            <div class="insight-card full-width-card">
                                <h3>Symplectic Structure</h3>
                                <p>Hamilton's equations conserve phase space volume over time. This mathematical property is known as <strong>Liouville's Theorem</strong>, meaning the flow in phase space is a volume-preserving diffeomorphism generated by the symplectic 2-form \(\omega = \sum_i dq_i \wedge dp_i\).</p>
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
    padding-top: 6px;
    max-width: 1260px;
    margin: 0 auto;
}

.transformer-header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    padding: 4px 0 12px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    text-align: left;
}

.transformer-header h1 {
    font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
    font-size: 1.65rem;
    line-height: 1.15;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #ffffff 0%, #a5b4fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.transformer-header .tagline {
    color: var(--text-muted);
    font-size: 0.88rem;
    line-height: 1.4;
    margin: 0;
}

.transformer-grid {
    display: grid;
    grid-template-columns: 310px minmax(0, 1fr);
    gap: 20px;
    align-items: start;
}

.transformer-panel-right {
    min-width: 0;
}

/* Glassmorphic Panel Cards */
.glass-card {
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.28);
}

.card-head-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
    padding-bottom: 7px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.glass-card h2 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    margin: 0;
    color: #ffffff;
}

.pill-count {
    font-size: 0.68rem;
    font-weight: 600;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 2px 7px;
    border-radius: 10px;
}

/* Preset Buttons Grid */
.preset-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
}

.preset-btn {
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #cbd5e1;
    padding: 7px 8px;
    border-radius: 8px;
    font-size: 0.76rem;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: left;
    line-height: 1.25;
}

.preset-btn:hover {
    background: rgba(56, 189, 248, 0.14);
    border-color: rgba(56, 189, 248, 0.45);
    color: #ffffff;
}

.preset-btn.active {
    background: rgba(99, 102, 241, 0.22);
    border-color: #818cf8;
    color: #ffffff;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.22);
}

.preset-btn.preset-singular {
    border-color: rgba(251, 191, 36, 0.25);
    color: #fde68a;
}

/* Form Controls */
.input-group-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-bottom: 10px;
}

.input-field-wrapper {
    display: flex;
    flex-direction: column;
    margin-bottom: 10px;
}

.input-group-row .input-field-wrapper {
    margin-bottom: 0;
}

.input-field-wrapper label {
    font-size: 0.76rem;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 4px;
}

.input-field-wrapper input,
.input-field-wrapper textarea {
    background: rgba(2, 6, 23, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 8px 10px;
    color: #f8fafc;
    font-family: 'JetBrains Mono', 'Fira Code', monospace;
    font-size: 0.82rem;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    width: 100%;
    box-sizing: border-box;
}

.input-field-wrapper input:focus,
.input-field-wrapper textarea:focus {
    border-color: #818cf8;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.btn-block {
    width: 100%;
    padding: 10px;
    font-size: 0.88rem;
    font-weight: 600;
    margin-top: 2px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

/* Output Viewer Area */
.main-viewer-card {
    min-height: 460px;
    padding: 20px;
}

.output-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 80px 20px;
    color: var(--text-muted);
}

.placeholder-icon {
    font-size: 2.5rem;
    margin-bottom: 12px;
    opacity: 0.8;
}

.output-error {
    background: rgba(245, 158, 11, 0.12);
    border: 1px solid rgba(245, 158, 11, 0.4);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 16px;
    color: #fde68a;
    font-size: 0.86rem;
}

.output-error p {
    margin: 4px 0 0 0;
}

.error-badge {
    font-weight: 700;
    color: #fbbf24;
    font-size: 0.82rem;
}

/* Output Top Bar + Tabs + Regularity Badge */
.output-top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding-bottom: 12px;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.rep-tabs {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.tab-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: var(--text-muted);
    padding: 7px 13px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.08);
}

.tab-btn.active {
    color: #ffffff;
    background: rgba(99, 102, 241, 0.2);
    border-color: #818cf8;
}

.regularity-badge {
    font-size: 0.72rem;
    font-weight: 700;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.03em;
    white-space: nowrap;
}

.regularity-badge.is-regular {
    background: rgba(16, 185, 129, 0.14);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34d399;
}

.regularity-badge.is-singular {
    background: rgba(245, 158, 11, 0.14);
    border: 1px solid rgba(245, 158, 11, 0.4);
    color: #fbbf24;
}

.tab-panel {
    display: none;
}

.tab-panel.active {
    display: block;
    animation: fadeIn 0.25s ease;
}

/* HERO RESULT: L => H Side-by-Side */
.duality-hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1.15fr);
    gap: 12px;
    align-items: stretch;
    margin-bottom: 20px;
}

.duality-pane {
    background: rgba(3, 7, 18, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.duality-pane.hero-pane {
    background: rgba(99, 102, 241, 0.08);
    border: 1px solid rgba(129, 140, 248, 0.45);
    box-shadow: 0 0 24px rgba(99, 102, 241, 0.12);
}

.duality-arrow-badge {
    align-self: center;
    font-size: 1.3rem;
    font-weight: 700;
    color: #a5b4fc;
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(129, 140, 248, 0.35);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.math-label-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
}

.math-label {
    font-size: 0.76rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.math-label.accent-hero {
    color: #c7d2fe;
}

.math-box {
    flex: 1;
    background: rgba(2, 6, 23, 0.72);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 14px 12px;
    text-align: center;
    overflow-x: auto;
    display: flex;
    align-items: center;
    justify-content: center;
}

.math-box.hero-box {
    background: rgba(2, 6, 23, 0.85);
    border-color: rgba(129, 140, 248, 0.25);
}

.math-render-field {
    font-size: 1.12rem;
    color: #ffffff;
    width: 100%;
}

.hero-box .math-render-field {
    font-size: 1.25rem;
    color: #ffd700;
}

.copy-hamiltonian-btn {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #cbd5e1;
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    white-space: nowrap;
    transition: all 0.15s ease;
}

.copy-hamiltonian-btn:hover {
    background: rgba(129, 140, 248, 0.2);
    border-color: #818cf8;
    color: #ffffff;
}

.copy-hamiltonian-btn.copied {
    background: rgba(16, 185, 129, 0.15);
    border-color: #34d399;
    color: #34d399;
}

/* Numbered 3-Step Derivation Pipeline */
.pipeline-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin: 0 0 10px 0;
}

.pipeline-steps-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
}

.step-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 12px 14px;
    min-width: 0;
}

.step-card-wide {
    grid-column: 1 / -1;
}

.step-card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
}

.step-num {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #a5b4fc;
    background: rgba(99, 102, 241, 0.18);
    border: 1px solid rgba(129, 140, 248, 0.35);
    padding: 2px 7px;
    border-radius: 6px;
    white-space: nowrap;
}

.step-title {
    font-size: 0.8rem;
    font-weight: 600;
    color: #e2e8f0;
}

.step-math-box {
    padding: 10px 12px;
}

/* Equations & Geometry Tabs */
.tab-section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    color: #ffffff;
    margin: 0 0 6px 0;
}

.section-desc {
    font-size: 0.86rem;
    color: var(--text-muted);
    margin: 0 0 16px 0;
    line-height: 1.5;
}

.math-display-container {
    margin-bottom: 14px;
}

.geometry-insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 12px;
}

.full-width-card {
    grid-column: 1 / -1;
}

.insight-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 16px;
}

.insight-card h3 {
    font-size: 0.9rem;
    color: #a5b4fc;
    margin: 0 0 8px 0;
    font-family: 'Space Grotesk', sans-serif;
}

.insight-card p {
    font-size: 0.86rem;
    line-height: 1.55;
    color: #cbd5e1;
    margin: 0;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@media (max-width: 980px) {
    .transformer-grid {
        grid-template-columns: 1fr;
    }
    .duality-hero-grid {
        grid-template-columns: minmax(0, 1fr);
    }
    .duality-arrow-badge {
        justify-self: center;
        transform: rotate(90deg);
    }
    .pipeline-steps-grid,
    .geometry-insight-grid {
        grid-template-columns: 1fr;
    }
}
</style>

<!-- Load Math.js for expression parsing helpers + SymPy CAS Frontend Controller -->
<script src="/js/lib/math.min.js?v=<?= @filemtime(PROJECT_ROOT . '/public/js/lib/math.min.js') ?: 1 ?>" nonce="<?= $nonce ?>" defer></script>
<script src="/js/legendre_transformer.js?v=<?= @filemtime(PROJECT_ROOT . '/public/js/legendre_transformer.js') ?: 1 ?>" nonce="<?= $nonce ?>" defer></script>
