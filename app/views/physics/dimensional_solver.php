<div class="solver-container">
    <div class="solver-header">
        <h1>Dimensional Solver &amp; Algebraic Consistency Engine</h1>
        <p class="tagline">Verify physical formulas, evaluate dimensional integrity, and reduce equations to their SI base dimensions.</p>
    </div>

    <div class="solver-grid">
        <!-- Left Column: Input and Analysis Panel -->
        <div class="solver-panel-left">
            <div class="glass-card main-solver-card">
                <h3>Equation Analyzer</h3>
                <div class="input-group">
                    <label for="formula-input">Enter Physical Formula:</label>
                    <div class="input-wrapper" style="align-items: flex-start;">
                        <input type="text" id="formula-input" placeholder="e.g. G * M / c^2" autocomplete="off" style="height: 48px; box-sizing: border-box;">
                        <div class="solver-button-group" style="display: flex; flex-direction: column; gap: 6px; margin: 0; box-sizing: border-box;">
                            <button id="solve-btn" class="btn btn-primary" style="height: 48px; padding: 0 24px; margin: 0; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 0.95rem; line-height: 1;">Analyze</button>
                            <button id="clear-formula-btn" class="btn btn-secondary" style="height: 24px; padding: 0 16px; margin: 0; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 500; line-height: 1;">Clear</button>
                        </div>
                    </div>
                </div>

                <div class="operator-keyboard" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 15px; margin-bottom: 25px;">
                    <button class="keyboard-btn" data-val=" + ">+</button>
                    <button class="keyboard-btn" data-val=" - ">-</button>
                    <button class="keyboard-btn" data-val=" * ">*</button>
                    <button class="keyboard-btn" data-val=" / ">/</button>
                    <button class="keyboard-btn" data-val="^">^</button>
                    <button class="keyboard-btn" data-val="^2">x²</button>
                    <button class="keyboard-btn" data-val="^0.5">√x</button>
                    <button class="keyboard-btn" data-val="(">(</button>
                    <button class="keyboard-btn" data-val=")">)</button>
                    <button class="keyboard-btn" data-val="sin(">sin</button>
                    <button class="keyboard-btn" data-val="cos(">cos</button>
                    <button class="keyboard-btn" data-val="exp(">exp</button>
                </div>

                <div class="examples-section">
                    <h4>Quick Load Examples:</h4>
                    <div class="examples-grid">
                        <button class="example-btn" data-formula="G * M / c^2">Schwarzschild Radius</button>
                        <button class="example-btn" data-formula="hbar / (m_e * c)">Compton Wavelength</button>
                        <button class="example-btn" data-formula="m * c^2">Mass-Energy Equivalence</button>
                        <button class="example-btn" data-formula="hbar^2 / (m_e * e^2 * (4 * pi * eps0))">Bohr Radius</button>
                        <button class="example-btn" data-formula="(hbar * G / c^3)^0.5">Planck Length</button>
                        <button class="example-btn" data-formula="e^2 / (4 * pi * eps0 * hbar * c)">Fine-structure Constant</button>
                        <button class="example-btn" data-formula="k_B * T / hbar">Thermal Frequency</button>
                        <button class="example-btn" data-formula="G * M * m / r^2">Newtonian Gravitational Force</button>
                    </div>
                </div>

                <!-- Analysis Output Panel -->
                <div id="output-panel" class="output-panel" style="display: none;">
                    <div class="output-row matched-concept-container">
                        <span class="output-label">Resolved Concept:</span>
                        <span id="resolved-concept" class="concept-badge">Length</span>
                    </div>

                    <div class="math-preview-box">
                        <div class="math-label">Parsed Expression:</div>
                        <div id="math-expression-render" class="math-render-field">\[ G \cdot M / c^2 \]</div>
                    </div>

                    <div class="output-metrics">
                        <div class="metric-card">
                            <span class="metric-title">SI Base Dimension</span>
                            <div id="dimension-vector-render" class="metric-math">\[ \mathsf{L}^1 \]</div>
                        </div>
                        <div class="metric-card">
                            <span class="metric-title">SI Unit Equivalents</span>
                            <div id="si-units-render" class="metric-math">\[ \text{m} \]</div>
                        </div>
                    </div>

                    <div class="steps-section">
                        <h4>Derivation Resolution Steps:</h4>
                        <ul id="derivation-steps" class="steps-list">
                            <!-- JS populated -->
                        </ul>
                    </div>
                </div>

                <div id="error-panel" class="error-panel" style="display: none;">
                    <svg class="error-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span id="error-message">Error message details go here.</span>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Registry -->
        <div class="solver-panel-right">
            <div class="glass-card reference-card">
                <h3>Symbols &amp; Constants Registry</h3>
                <p class="ref-sub">Click a symbol in the list to insert it into the formula editor.</p>
                <div class="search-bar-wrapper">
                    <input type="text" id="registry-search" placeholder="Filter variables and constants..." autocomplete="off">
                </div>
                <div class="reference-list-wrapper">
                    <table class="reference-table">
                        <thead>
                            <tr>
                                <th>Symbol</th>
                                <th>Name</th>
                                <th>Dimension</th>
                            </tr>
                        </thead>
                        <tbody id="reference-tbody">
                            <!-- JS populated from PHP array -->
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Parser Inspector Card -->
            <div id="inspector-card" class="glass-card" style="margin-top: 20px; display: none;">
                <h3 style="display: flex; justify-content: space-between; align-items: center; cursor: pointer; margin: 0;" id="inspector-toggle-header">
                    <span>Parser Inspector &amp; Token Audit</span>
                    <span id="inspector-toggle-icon" style="font-size: 0.8rem; opacity: 0.7; font-weight: 500;">[Show Details]</span>
                </h3>
                <div id="inspector-panel" style="display: none; flex-direction: column; gap: 16px; margin-top: 15px; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 15px;">
                    <div>
                        <span class="metric-title" style="display: block; margin-bottom: 8px; font-size: 0.78rem; text-transform: uppercase; color: var(--accent-color); font-weight: bold; letter-spacing: 0.5px;">1. Tokenized Stream</span>
                        <div id="token-stream-container" style="display: flex; flex-wrap: wrap; gap: 8px; font-family: monospace;"></div>
                    </div>
                    <div>
                        <span class="metric-title" style="display: block; margin-bottom: 8px; font-size: 0.78rem; text-transform: uppercase; color: var(--accent-color); font-weight: bold; letter-spacing: 0.5px;">2. Reverse Polish Notation (RPN) Queue</span>
                        <div id="rpn-queue-container" style="display: flex; flex-wrap: wrap; gap: 8px; align-items: center; font-family: monospace;"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* Page Styles */
.solver-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.solver-header {
    margin-bottom: 30px;
    text-align: center;
}

.solver-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.solver-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.solver-grid {
    display: grid;
    grid-template-columns: 1.3fr 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 950px) {
    .solver-grid {
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

.main-solver-card h3, .reference-card h3 {
    margin: 0 0 15px 0;
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-size: 1.3rem;
}

/* Input Styles */
.input-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 25px;
}

.input-group label {
    font-size: 0.9rem;
    color: var(--text-muted);
}

.input-wrapper {
    display: flex;
    gap: 12px;
}

#formula-input {
    flex: 1;
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #ffffff;
    padding: 12px 16px;
    font-size: 1.05rem;
    outline: none;
    transition: all 0.25s ease;
    font-family: 'Space Grotesk', monospace;
}

#formula-input:focus {
    border-color: var(--accent-color);
    box-shadow: 0 0 15px rgba(100, 255, 218, 0.15);
    background: rgba(3, 7, 18, 0.85);
}

/* Examples Section */
.examples-section {
    margin-bottom: 30px;
}

.examples-section h4 {
    margin: 0 0 12px 0;
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.examples-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.example-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 0.78rem;
    cursor: pointer;
    transition: all 0.2s;
}

.example-btn:hover {
    background: rgba(100, 255, 218, 0.08);
    border-color: rgba(100, 255, 218, 0.3);
    color: #ffffff;
}

/* Output Panel Styles */
.output-panel {
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 25px;
    animation: fadeIn 0.3s ease-out;
}

.matched-concept-container {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20px;
}

.output-label {
    font-size: 0.9rem;
    color: var(--text-muted);
}

.concept-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.math-preview-box {
    background: rgba(3, 7, 18, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 20px;
    text-align: center;
}

.math-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    text-align: left;
    margin-bottom: 8px;
}

.math-render-field {
    font-size: 1.25rem;
    overflow-x: auto;
}

.output-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 25px;
}

.metric-card {
    background: rgba(3, 7, 18, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}

.metric-title {
    display: block;
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 6px;
}

.metric-math {
    font-size: 1.15rem;
    overflow-x: auto;
}

.steps-section h4 {
    margin: 0 0 10px 0;
    font-size: 0.85rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.steps-list {
    margin: 0;
    padding-left: 20px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    color: var(--text-color);
    font-size: 0.9rem;
}

.steps-list li code {
    background: rgba(255, 255, 255, 0.05);
    padding: 1px 5px;
    border-radius: 4px;
    font-family: monospace;
}

/* Error Panel Styles */
.error-panel {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
    padding: 14px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.9rem;
    margin-top: 15px;
    animation: fadeIn 0.2s ease-out;
}

.error-icon {
    flex-shrink: 0;
}

/* Reference Panel Styles */
.ref-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: -8px;
    margin-bottom: 15px;
}

.search-bar-wrapper {
    margin-bottom: 15px;
}

#registry-search {
    background: rgba(3, 7, 18, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #ffffff;
    padding: 10px 14px;
    font-size: 0.88rem;
    outline: none;
    width: 100%;
    box-sizing: border-box;
    transition: all 0.2s;
}

#registry-search:focus {
    border-color: var(--accent-color);
}

.reference-list-wrapper {
    max-height: 480px;
    overflow-y: auto;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    background: rgba(3, 7, 18, 0.2);
}

.reference-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.85rem;
    text-align: left;
}

.reference-table th {
    background: rgba(15, 23, 42, 0.7);
    color: var(--text-muted);
    font-weight: 600;
    padding: 10px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
}

.reference-table td {
    padding: 10px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-color);
}

.reference-table tbody tr {
    cursor: pointer;
    transition: background 0.15s;
}

.reference-table tbody tr:hover {
    background: rgba(100, 255, 218, 0.04);
}

.ref-sym {
    font-family: 'Space Grotesk', monospace;
    font-weight: bold;
    color: var(--accent-color);
}

.ref-dim {
    font-family: monospace;
    color: var(--text-muted);
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

/* Concept Badges */
.concept-badge {
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid rgba(255, 255, 255, 0.15);
}

.badge-dimensionless {
    background: rgba(168, 85, 247, 0.15);
    border-color: rgba(168, 85, 247, 0.4);
    color: #c084fc;
}
.badge-mass {
    background: rgba(244, 63, 94, 0.15);
    border-color: rgba(244, 63, 94, 0.4);
    color: #fb7185;
}
.badge-length {
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.4);
    color: #34d399;
}
.badge-time {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.4);
    color: #60a5fa;
}
.badge-current {
    background: rgba(251, 191, 36, 0.15);
    border-color: rgba(251, 191, 36, 0.4);
    color: #fbbf24;
}
.badge-temperature {
    background: rgba(236, 72, 153, 0.15);
    border-color: rgba(236, 72, 153, 0.4);
    color: #f472b6;
}
.badge-energy, .badge-force, .badge-power, .badge-pressure, .badge-momentum, .badge-voltage, .badge-charge, .badge-frequency, .badge-density, .badge-action, .badge-derived, .badge-area, .badge-volume {
    background: rgba(100, 255, 218, 0.1);
    border-color: rgba(100, 255, 218, 0.35);
    color: #64ffda;
}
.badge-unknown {
    background: rgba(249, 115, 22, 0.15);
    border-color: rgba(249, 115, 22, 0.4);
    color: #fdba74;
}

/* MathJax Color-Coding Classes */
.math-color-mass { color: #fb7185 !important; }
.math-color-length { color: #34d399 !important; }
.math-color-time { color: #60a5fa !important; }
.math-color-current { color: #fbbf24 !important; }
.math-color-temp { color: #f472b6 !important; }
.math-color-error { color: #ef4444 !important; }
.math-color-dimensionless { color: #c084fc !important; }
.math-color-derived { color: #64ffda !important; }

/* Operator Keyboard Styles */
.keyboard-btn {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--accent-color, #64ffda);
    padding: 8px 14px;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    font-family: 'Fira Code', monospace;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    align-items: center;
    justify-content: center;
    outline: none;
}

.keyboard-btn:hover {
    background: rgba(100, 255, 218, 0.08);
    border-color: rgba(100, 255, 218, 0.3);
    color: #ffffff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(100, 255, 218, 0.1);
}

.keyboard-btn:active {
    transform: translateY(0);
}
</style>

<!-- Pass variables list from PHP registry to JS -->
<script nonce="<?= $nonce ?>">
window.NOTATION_DATA = <?php echo json_encode($notation); ?>;
</script>

<script src="/js/dimensional_solver.js" defer></script>
