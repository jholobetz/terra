<div class="workspace-container">
    <div class="workspace-header">
        <h1>Classical-to-Quantum Correspondence Workspace</h1>
        <p class="tagline">Explore the boundary of quantum mechanics and classical dynamics. Visualize wave packet decoherence, quantum tunneling, and phase-space divergence.</p>
    </div>

    <div class="workspace-grid">
        <!-- Left Column: Simulation Modes & Config -->
        <div class="workspace-panel-left">
            <div class="glass-card list-card">
                <h3>Simulation Modes</h3>
                <p class="ref-sub">Choose a correspondence playground to analyze trajectory alignments and divergences.</p>
                
                <div class="mode-select-box">
                    <button class="mode-btn active" id="mode-btn-ehrenfest">
                        <span class="mode-title">Ehrenfest's Sandbox</span>
                        <span class="mode-desc">Expectation Values vs Classical path</span>
                    </button>
                    <button class="mode-btn" id="mode-btn-phase">
                        <span class="mode-title">Phase Space Flows</span>
                        <span class="mode-desc">Classical Liouville vs Quantum Wigner</span>
                    </button>
                </div>

                <div class="potential-select-section" id="potential-selector-box">
                    <h4 style="margin: 20px 0 10px 0; font-family: 'Space Grotesk', sans-serif; color: #ffffff; font-size: 0.95rem;">Potential Landscape V(x)</h4>
                    <div class="potential-list">
                        <button class="pot-btn active" data-pot="harmonic">Harmonic Oscillator</button>
                        <button class="pot-btn" data-pot="double_well">Anharmonic Double Well</button>
                        <button class="pot-btn" data-pot="barrier">Tunneling Barrier</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Console -->
        <div class="workspace-panel-right">
            <div class="glass-card main-workspace-card" id="workspace-card">
                
                <!-- Active Header -->
                <div class="workspace-header-info">
                    <div class="theory-meta">
                        <span id="active-category" class="category-badge">Quantum Dynamics</span>
                        <h2 id="active-mode-title">Ehrenfest's Sandbox</h2>
                    </div>
                    <p id="active-mode-description" class="theory-desc">Visualizes the classical trajectory of a point particle alongside the expectation values of position and momentum for a quantum wave packet.</p>
                </div>

                <!-- Simulation Block -->
                <div class="playground-section">
                    <div class="playground-header">
                        <h4>Real-Time Correspondence Sandbox</h4>
                        <span class="sandbox-badge">Symplectic Integrator</span>
                    </div>
                    <div class="playground-layout">
                        <!-- Canvas -->
                        <div class="canvas-container">
                            <canvas id="correspondence-canvas"></canvas>
                        </div>
                        <!-- Controls Sidebar -->
                        <div class="controls-sidebar">
                            <div class="sandbox-info">
                                <span class="label">Quantum State:</span>
                                <span id="coherence-status" class="status-value status-coherent">Coherent (Phase Lock)</span>
                            </div>
                            
                            <div id="sliders-container" class="sliders-box">
                                <!-- JS Populated Sliders -->
                            </div>
                            
                            <div style="margin-top: 10px; display: flex; gap: 8px;">
                                <button id="restart-btn" class="btn btn-secondary" style="flex: 1; font-size: 0.8rem; padding: 8px;">Reset Wave</button>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Mathematics / Physics Details -->
                <div class="math-details-section">
                    <div class="insight-grid">
                        <div class="insight-card">
                            <h4 id="math-box-title-1">Ehrenfest's Equations</h4>
                            <div id="math-formula-1" class="math-render-field-small">
                                \[ \frac{d}{dt}\langle \hat{x} \rangle = \frac{\langle \hat{p} \rangle}{m} \]
                                \[ \frac{d}{dt}\langle \hat{p} \rangle = -\langle V'(\hat{x}) \rangle \]
                            </div>
                            <p id="math-desc-1" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 10px; line-height: 1.45;">
                                Quantum expectation values trace classical trajectories exactly ONLY when the potential force field is linear (e.g. the Harmonic Oscillator).
                            </p>
                        </div>
                        <div class="insight-card">
                            <h4 id="math-box-title-2">Classical Convergence limit</h4>
                            <div id="math-formula-2" class="math-render-field-small">
                                \[ \lim_{\hbar \to 0} \langle \hat{x} \rangle(t) = x_{\text{class}}(t) \]
                            </div>
                            <p id="math-desc-2" style="font-size: 0.82rem; color: var(--text-muted); margin-top: 10px; line-height: 1.45;">
                                Reducing the effective Planck constant (\( \hbar \)) pushes the quantum wave packet to act as a localized Dirac delta function centered at the classical path.
                            </p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.workspace-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.workspace-header {
    margin-bottom: 30px;
    text-align: center;
}

.workspace-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-quantum));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.workspace-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.workspace-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 980px) {
    .workspace-grid {
        grid-template-columns: 1fr;
    }
}

.glass-card {
    background: rgba(15, 23, 42, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 24px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.list-card {
    max-height: 750px;
    overflow-y: auto;
}

.list-card h3 {
    margin: 0 0 8px 0;
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-size: 1.3rem;
}

.ref-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0;
    margin-bottom: 20px;
    line-height: 1.4;
}

/* Sidebar Mode Selectors */
.mode-select-box {
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 20px;
}

.mode-btn {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-left: 4px solid var(--accent-quantum);
    border-radius: 8px;
    padding: 14px;
    text-align: left;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}

.mode-btn:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.08);
    transform: translateX(3px);
}

.mode-btn.active {
    background: rgba(255, 78, 136, 0.06);
    border-color: rgba(255, 78, 136, 0.25);
    border-left-color: var(--accent-quantum);
}

.mode-btn .mode-title {
    display: block;
    font-size: 1.05rem;
    font-weight: 600;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
    margin-bottom: 4px;
}

.mode-btn .mode-desc {
    display: block;
    font-size: 0.78rem;
    color: var(--text-muted);
    line-height: 1.3;
}

/* Potential Selector Buttons */
.potential-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.pot-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s;
    font-family: 'Space Grotesk', sans-serif;
}

.pot-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.1);
}

.pot-btn.active {
    background: rgba(255, 78, 136, 0.08);
    border-color: rgba(255, 78, 136, 0.3);
    color: #ffffff;
}

/* Right Panel Console */
.workspace-header-info {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 20px;
    margin-bottom: 24px;
}

.theory-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

.theory-meta h2 {
    margin: 0;
    font-size: 1.8rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.category-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid rgba(255, 78, 136, 0.35);
    background: rgba(255, 78, 136, 0.1);
    color: var(--accent-quantum);
}

.theory-desc {
    margin: 0;
    font-size: 0.98rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* Simulation Section */
.playground-section {
    background: rgba(3, 7, 18, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
}

.playground-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    padding-bottom: 10px;
}

.playground-header h4 {
    margin: 0;
    font-size: 1rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.sandbox-badge {
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent-quantum);
    text-transform: uppercase;
    background: rgba(255, 78, 136, 0.1);
    border: 1px solid rgba(255, 78, 136, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
}

.playground-layout {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 20px;
}

@media (max-width: 800px) {
    .playground-layout {
        grid-template-columns: 1fr;
    }
}

.canvas-container {
    width: 100%;
    aspect-ratio: 16 / 10;
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    overflow: hidden;
    position: relative;
}

.canvas-container canvas {
    width: 100%;
    height: 100%;
    display: block;
}

.controls-sidebar {
    display: flex;
    flex-direction: column;
    gap: 16px;
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    padding: 16px;
}

.sandbox-info {
    display: flex;
    justify-content: space-between;
    font-size: 0.82rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 8px;
}

.sandbox-info .label {
    color: var(--text-muted);
}

.sandbox-info .status-value {
    font-weight: bold;
    transition: color 0.3s;
}

.status-coherent {
    color: #10b981;
}

.status-divergent {
    color: #ef4444;
}

.sliders-box {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.control-group label {
    font-size: 0.78rem;
    color: var(--text-muted);
}

.control-group input[type="range"] {
    width: 100%;
    accent-color: var(--accent-quantum);
    background: rgba(255, 255, 255, 0.1);
    height: 6px;
    border-radius: 3px;
    outline: none;
    -webkit-appearance: none;
}

.control-group input[type="range"]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--accent-quantum);
    cursor: pointer;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    transition: transform 0.1s;
}

.control-group input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}

/* Math Details Section */
.math-details-section {
    margin-top: 30px;
}

.insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

@media (max-width: 700px) {
    .insight-grid {
        grid-template-columns: 1fr;
    }
}

.insight-card {
    background: rgba(255, 255, 255, 0.01);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 10px;
    padding: 20px;
}

.insight-card h4 {
    margin: 0 0 10px 0;
    font-size: 0.9rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 8px;
}

.math-render-field-small {
    font-size: 1.1rem;
    color: #ffd700;
    min-height: 70px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(3, 7, 18, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.02);
    border-radius: 6px;
    padding: 10px;
}
</style>

<script src="/js/correspondence_workspace.js" nonce="<?= $nonce ?>" defer></script>
