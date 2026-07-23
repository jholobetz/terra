<div class="vault-container">
    <div class="vault-header">
        <h1>Noether's Vault</h1>
        <p class="tagline">Explore the deep mathematical symmetry of spacetime and fields, and trace their Noether mappings to conserved physical currents.</p>
    </div>

    <div class="vault-grid">
        <!-- Left Column: Symmetries Directory -->
        <div class="vault-panel-left">
            <div class="glass-card list-card">
                <h3>Symmetries &amp; Generators</h3>
                <p class="ref-sub">Select a continuous symmetry transformation to inspect its infinitesimal generator and conserved physical current.</p>
                <div class="symmetry-list" id="symmetry-list">
                    <!-- JS Populated -->
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Vault Console -->
        <div class="vault-panel-right">
            <div class="glass-card main-vault-card" id="vault-card">
                
                <!-- Active Header -->
                <div class="vault-header-info">
                    <div class="symmetry-meta">
                        <span id="active-category" class="category-badge">Spacetime Symmetry</span>
                        <h2 id="active-symmetry-title">Time Translation Invariance</h2>
                    </div>
                    <p id="active-symmetry-description" class="symmetry-desc">The laws of physics do not change from one moment to the next. Invariance under translations in time leads directly to the conservation of energy.</p>
                </div>

                <!-- Simulation & Interactive Playground -->
                <div class="playground-section">
                    <div class="playground-header">
                        <h4>Interactive Symmetry Sandbox</h4>
                        <span class="sandbox-badge">Real-time Numerical Solver</span>
                    </div>
                    <div class="playground-layout">
                        <!-- Canvas Container -->
                        <div class="canvas-container">
                            <canvas id="vault-canvas"></canvas>
                        </div>
                        <!-- Controls Sidebar -->
                        <div class="controls-sidebar">
                            <div class="sandbox-info">
                                <span class="label">System State:</span>
                                <span id="system-status" class="status-value status-conserved">Symmetric (Conserved)</span>
                            </div>
                            
                            <div id="controls-container" class="sliders-box">
                                <!-- JS Populated Sliders -->
                            </div>
                            
                            <div class="simulation-chart-box">
                                <span class="chart-label">Conserved Quantity Over Time</span>
                                <div class="chart-canvas-wrapper">
                                    <canvas id="chart-canvas"></canvas>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Conservation Law Highlight -->
                <div class="law-highlight-box">
                    <div class="law-header">Conserved Current &amp; Conservation Law</div>
                    <div class="law-math-grid">
                        <div class="math-sub-box">
                            <span class="math-sub-label">Conserved Noether Current \( J^\mu \)</span>
                            <div id="math-current" class="math-render-small">
                                \[ J^\mu = T^{\mu 0} \]
                            </div>
                        </div>
                        <div class="math-sub-box">
                            <span class="math-sub-label">Local Conservation Equation</span>
                            <div id="math-conservation" class="math-render-small highlight-gold">
                                \[ \partial_\mu T^{\mu 0} = 0 \]
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Mathematical Derivation Flows -->
                <div class="derivation-section">
                    <h4>Euler-Lagrange Derivation Flow</h4>
                    <p class="ref-sub">Applying an infinitesimal shift \( \delta \phi \) to the fields in the action functional \( S[\phi] \):</p>
                    <div class="derivation-box">
                        <div id="derivation-math" class="math-render-field">
                            <!-- JS Populated MathJax steps -->
                        </div>
                    </div>
                    <div class="derivation-text-desc">
                        <h5>Physical Mechanism</h5>
                        <p id="derivation-description">Detailed step breakdown of coordinate shifts.</p>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.vault-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.vault-header {
    margin-bottom: 30px;
    text-align: center;
}

.vault-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-default));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.vault-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.vault-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 980px) {
    .vault-grid {
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

/* Sidebar List */
.symmetry-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.symmetry-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-left: 4px solid var(--accent-default);
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.symmetry-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.08);
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.symmetry-item.active {
    background: rgba(99, 102, 241, 0.06);
    border-color: rgba(99, 102, 241, 0.25);
    border-left-color: var(--theme-color, var(--accent-default));
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.05);
}

.symmetry-item h4 {
    margin: 0 0 4px 0;
    font-size: 1.05rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.symmetry-item .sym-meta {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 4px;
}

.symmetry-item .sym-meta .generator {
    font-family: serif;
    font-weight: bold;
    color: var(--theme-color, var(--accent-default));
}

/* Right Panel Console */
.vault-header-info {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 20px;
    margin-bottom: 24px;
}

.symmetry-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 10px;
}

.symmetry-meta h2 {
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
    border: 1px solid var(--theme-border-color, rgba(100, 255, 218, 0.35));
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.1));
    color: var(--theme-color, var(--accent-default));
}

.symmetry-desc {
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
    color: var(--accent-default);
    text-transform: uppercase;
    background: rgba(100, 255, 218, 0.1);
    border: 1px solid rgba(100, 255, 218, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
}

.playground-layout {
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 20px;
}

@media (max-width: 750px) {
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

.status-conserved {
    color: #10b981; /* Green */
}

.status-broken {
    color: #ef4444; /* Red */
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
    accent-color: var(--theme-color, var(--accent-default));
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
    background: var(--theme-color, var(--accent-default));
    cursor: pointer;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
    transition: transform 0.1s;
}

.control-group input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}

.simulation-chart-box {
    margin-top: auto;
    border-top: 1px solid rgba(255, 255, 255, 0.05);
    padding-top: 12px;
}

.chart-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    display: block;
    margin-bottom: 8px;
}

.chart-canvas-wrapper {
    height: 90px;
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 6px;
    overflow: hidden;
}

.chart-canvas-wrapper canvas {
    width: 100%;
    height: 100%;
    display: block;
}

/* Conservation Law Highlight */
.law-highlight-box {
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.02);
}

.law-header {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    padding-bottom: 6px;
}

.law-math-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

@media (max-width: 600px) {
    .law-math-grid {
        grid-template-columns: 1fr;
    }
}

.math-sub-box {
    background: rgba(3, 7, 18, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.02);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}

.math-sub-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    display: block;
    margin-bottom: 8px;
    text-transform: uppercase;
}

.math-render-small {
    font-size: 1.15rem;
    color: #ffffff;
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.highlight-gold {
    color: #ffd700;
}

/* Derivation Section */
.derivation-section h4 {
    margin: 0 0 4px 0;
    font-size: 1.1rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.derivation-box {
    background: rgba(3, 7, 18, 0.5);
    border: 1px solid rgba(100, 255, 218, 0.05);
    border-radius: 8px;
    padding: 20px 10px;
    text-align: center;
    overflow-x: auto;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.2);
}

.derivation-text-desc h5 {
    margin: 0 0 6px 0;
    font-size: 0.88rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.derivation-text-desc p {
    margin: 0;
    font-size: 0.92rem;
    color: var(--text-muted);
    line-height: 1.6;
}
</style>

<script src="/js/noethers_vault.js" nonce="<?= $nonce ?>" defer></script>
