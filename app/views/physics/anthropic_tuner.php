<div class="tuner-container">
    <div class="tuner-header">
        <h1>Anthropic Constant Tuner &amp; Cosmological Sandbox</h1>
        <p class="tagline">Adjust the fundamental physical dials of the universe. Recalculate atomic orbits, stellar lifetimes, and gravitational limits to observe the boundaries of stable matter.</p>
    </div>

    <div class="tuner-grid">
        <!-- Left Column: Universe Constant Dials -->
        <div class="tuner-panel-left">
            <div class="glass-card list-card">
                <h3>Universe Dials</h3>
                <p class="ref-sub">Adjust these sliders to vary the fundamental constants of nature relative to our standard universe value.</p>
                
                <div class="sliders-list" id="dials-sliders-container">
                    <!-- JS Populated Sliders -->
                </div>

                <div style="margin-top: 20px; display: flex; gap: 8px;">
                    <button id="reset-dials-btn" class="btn btn-secondary" style="width: 100%; font-size: 0.8rem; padding: 10px;">Reset to Standard Universe</button>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Scaling Console -->
        <div class="tuner-panel-right">
            <div class="glass-card main-tuner-card" id="tuner-card">
                
                <!-- Active Header -->
                <div class="tuner-header-info">
                    <div class="theory-meta">
                        <span class="category-badge">Cosmic Scaling</span>
                        <h2 style="margin: 0; font-size: 1.8rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif;">Cosmological Sandbox</h2>
                    </div>
                    <p class="theory-desc">Visualizes the structural impact of fundamental variables across three scales: atomic quantum orbitals, planetary solar systems, and stellar core fusion pressure.</p>
                </div>

                <!-- Simulation & Interactive Playground -->
                <div class="playground-section">
                    <div class="playground-header">
                        <h4>Scale Visualizer (Atomic, Planetary, Stellar)</h4>
                        <span class="sandbox-badge">Multi-Scale Solver</span>
                    </div>
                    <!-- Canvas Container -->
                    <div class="canvas-container" style="aspect-ratio: 16 / 8;">
                        <canvas id="tuner-canvas"></canvas>
                    </div>
                </div>

                <!-- Recalculated Scaling Parameters Table -->
                <div class="parameters-section" style="margin-bottom: 25px;">
                    <h4 style="margin: 0 0 12px 0; font-family: 'Space Grotesk', sans-serif; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 6px;">
                        <span style="display:inline-block; width:4px; height:14px; background:var(--accent-astrophysics); border-radius:2px;"></span>
                        Recalculated Scaling Metrics
                    </h4>
                    <div class="table-wrapper">
                        <table class="glossary-table">
                            <thead>
                                <tr>
                                    <th>Physical Metric</th>
                                    <th>Mathematical Definition</th>
                                    <th>Computed Value (Relative)</th>
                                    <th>Physical Description</th>
                                </tr>
                            </thead>
                            <tbody id="metrics-tbody">
                                <!-- JS Populated -->
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Anthropic Warnings Console -->
                <div class="warnings-console-section" id="warnings-console-box">
                    <h4 style="margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; color: #ffffff; font-size: 1.1rem; display: flex; align-items: center; gap: 6px;">
                        <span style="display:inline-block; width:4px; height:14px; background:#ef4444; border-radius:2px;"></span>
                        Anthropic Boundaries Console
                    </h4>
                    <div class="console-box" id="console-output">
                        <!-- JS Populated Warning Messages -->
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.tuner-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.tuner-header {
    margin-bottom: 30px;
    text-align: center;
}

.tuner-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-astrophysics));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.tuner-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.tuner-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 980px) {
    .tuner-grid {
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
    max-height: 850px;
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

.sliders-list {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.control-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    background: rgba(255,255,255,0.01);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 12px;
}

.control-group label {
    font-size: 0.82rem;
    color: var(--text-color);
    display: flex;
    justify-content: space-between;
}

.control-group input[type="range"] {
    width: 100%;
    accent-color: var(--accent-astrophysics);
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
    background: var(--accent-astrophysics);
    cursor: pointer;
    box-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
    transition: transform 0.1s;
}

.control-group input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}

/* Right Panel Console */
.tuner-header-info {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 20px;
    margin-bottom: 24px;
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
    color: var(--accent-astrophysics);
    text-transform: uppercase;
    background: rgba(249, 115, 22, 0.1);
    border: 1px solid rgba(249, 115, 22, 0.2);
    padding: 2px 8px;
    border-radius: 4px;
}

.canvas-container {
    width: 100%;
    background: #020617;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    overflow: hidden;
}

.canvas-container canvas {
    width: 100%;
    height: 100%;
    display: block;
}

/* Table design */
.table-wrapper {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    background: rgba(3, 7, 18, 0.2);
    overflow: hidden;
}

.glossary-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.86rem;
    text-align: left;
}

.glossary-table th {
    background: rgba(15, 23, 42, 0.7);
    color: var(--text-muted);
    font-weight: 600;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.glossary-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-color);
}

.math-def {
    font-family: monospace;
    color: #ffd700;
}

.val-computed {
    font-family: monospace;
    font-weight: bold;
    color: var(--accent-astrophysics);
}

/* Warnings Console */
.console-box {
    background: #020617;
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 8px;
    padding: 16px;
    min-height: 80px;
    max-height: 200px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 0.88rem;
    line-height: 1.5;
    color: var(--text-color);
}

.warning-item {
    margin-bottom: 8px;
    color: #fca5a5; /* light red */
    display: flex;
    align-items: flex-start;
    gap: 8px;
}

.warning-item:last-child {
    margin-bottom: 0;
}

.warning-item .badge-crit {
    background: rgba(239, 68, 68, 0.2);
    border: 1px solid #ef4444;
    color: #ef4444;
    font-weight: bold;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 0.7rem;
    text-transform: uppercase;
    flex-shrink: 0;
}

.console-ok {
    color: #6ee7b7; /* green */
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>

<script src="/js/anthropic_tuner.js" nonce="<?= $nonce ?>" defer></script>
