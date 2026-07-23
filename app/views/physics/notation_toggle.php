<div class="toggle-container">
    <div class="toggle-header">
        <h1>Multi-Representation Notation Toggle</h1>
        <p class="tagline">Explore the mathematical manifold of physical equations through alternative notation systems and coordinate frameworks.</p>
    </div>

    <div class="toggle-grid">
        <!-- Left Column: Equation Selector List -->
        <div class="toggle-panel-left">
            <div class="glass-card list-card">
                <h3>Physical Theories</h3>
                <p class="ref-sub">Select a fundamental law to toggle between its representations.</p>
                <div class="theory-list" id="theory-list">
                    <!-- JS Populated -->
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Representation Viewer -->
        <div class="toggle-panel-right">
            <div class="glass-card main-viewer-card" id="viewer-card">
                <div class="viewer-header-info">
                    <div class="theory-meta">
                        <span id="active-category" class="category-badge">Quantum Mechanics</span>
                        <h2 id="active-theory-title">Schrödinger Equation</h2>
                    </div>
                    <p id="active-theory-description" class="theory-desc">Describes how the quantum state of a physical system changes in time.</p>
                </div>

                <!-- Representation Tab Bar -->
                <div class="rep-tabs-wrapper">
                    <div class="rep-tabs" id="rep-tabs-container">
                        <!-- JS Populated -->
                    </div>
                </div>

                <!-- Active Equation Math Display -->
                <div class="math-display-container">
                    <div class="math-label-bar">
                        <span class="math-label">Mathematical Representation: <strong id="active-rep-name" class="accent-text">Differential Form</strong></span>
                    </div>
                    <div class="math-box">
                        <div id="active-math-render" class="math-render-field">
                            <!-- MathJax Equations go here -->
                        </div>
                    </div>
                </div>

                <!-- Description & Insight Section -->
                <div class="insight-section">
                    <div class="insight-grid">
                        <div class="insight-card">
                            <h4>Physical Interpretation &amp; Insight</h4>
                            <p id="active-rep-insight">Select a representation to view its physical description.</p>
                        </div>
                        <div class="insight-card">
                            <h4>Formulation Utility</h4>
                            <p id="active-rep-utility">Explanation of why and when this formulation is used by physicists.</p>
                        </div>
                    </div>
                </div>

                <!-- Semantic Glossary Table -->
                <div class="glossary-section" id="glossary-section">
                    <h4>Semantic Variable Glossary</h4>
                    <p class="ref-sub">Click variable names to link directly to their definitions in the Constants &amp; Symbols Registry.</p>
                    <div class="table-wrapper">
                        <table class="glossary-table">
                            <thead>
                                <tr>
                                    <th>Symbol</th>
                                    <th>Variable Name</th>
                                    <th>Base Dimension</th>
                                </tr>
                            </thead>
                            <tbody id="glossary-tbody">
                                <!-- JS Populated -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.toggle-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.toggle-header {
    margin-bottom: 30px;
    text-align: center;
}

.toggle-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.toggle-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.toggle-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 950px) {
    .toggle-grid {
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
    max-height: 700px;
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
.theory-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.theory-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-left: 4px solid var(--accent-color);
    border-radius: 8px;
    padding: 16px;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.theory-item:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(255, 255, 255, 0.08);
    transform: translateX(4px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.theory-item.active {
    background: rgba(100, 255, 218, 0.06);
    border-color: rgba(100, 255, 218, 0.2);
    border-left-color: var(--theme-color, var(--accent-color));
    box-shadow: 0 4px 20px rgba(100, 255, 218, 0.05);
}

.theory-item h4 {
    margin: 0 0 6px 0;
    font-size: 1.05rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.theory-item p {
    margin: 0;
    font-size: 0.82rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Viewer Card */
.viewer-header-info {
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
    border: 1px solid var(--theme-border-color, rgba(100, 255, 218, 0.35));
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.1));
    color: var(--theme-color, var(--accent-color));
}

.theory-desc {
    margin: 0;
    font-size: 0.98rem;
    color: var(--text-muted);
    line-height: 1.5;
}

/* Representation Tabs */
.rep-tabs-wrapper {
    margin-bottom: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.rep-tabs {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    padding-bottom: 12px;
}

.rep-tab {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: var(--text-muted);
    padding: 8px 16px;
    border-radius: 6px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Space Grotesk', sans-serif;
}

.rep-tab:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.12);
}

.rep-tab.active {
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.1));
    border-color: var(--theme-border-color, rgba(100, 255, 218, 0.35));
    color: #ffffff;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

/* Math Box */
.math-display-container {
    background: rgba(3, 7, 18, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
}

.math-label-bar {
    margin-bottom: 15px;
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.accent-text {
    color: var(--theme-color, var(--accent-color));
}

.math-box {
    padding: 24px 12px;
    text-align: center;
    overflow-x: auto;
    border-radius: 8px;
    background: rgba(3, 7, 18, 0.7);
    border: 1px solid rgba(100, 255, 218, 0.1);
    box-shadow: 0 0 20px rgba(100, 255, 218, 0.03);
}

.math-render-field {
    font-size: 1.45rem;
    color: #ffd700;
    min-height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Description & Insight */
.insight-section {
    margin-bottom: 30px;
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

.insight-card p {
    margin: 0;
    font-size: 0.92rem;
    color: var(--text-muted);
    line-height: 1.6;
}

/* Glossary Section */
.glossary-section h4 {
    margin: 0 0 6px 0;
    font-size: 1rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.table-wrapper {
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    background: rgba(3, 7, 18, 0.2);
    overflow: hidden;
}

.glossary-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    text-align: left;
}

.glossary-table th {
    background: rgba(15, 23, 42, 0.7);
    color: var(--text-muted);
    font-weight: 600;
    padding: 10px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.glossary-table td {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-color);
}

.glossary-table tbody tr {
    transition: background 0.15s;
}

.glossary-table tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}

.var-sym {
    font-family: 'Space Grotesk', monospace;
    font-weight: bold;
    color: var(--accent-color);
}

.var-link {
    color: var(--text-color);
    text-decoration: none;
    border-bottom: 1px dotted var(--text-muted);
    font-weight: 500;
    transition: border-color 0.2s, color 0.2s;
}

.var-link:hover {
    color: var(--accent-color);
    border-bottom-color: var(--accent-color);
}

.var-dim {
    font-family: monospace;
    color: var(--text-muted);
}
</style>

<script src="/js/notation_toggle.js" defer></script>
