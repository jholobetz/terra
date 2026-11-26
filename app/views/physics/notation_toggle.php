<div class="toggle-container">
    <header class="toggle-header">
        <h1>The Physics Rosetta Stone</h1>
        <p class="tagline">Translate fundamental physical laws across vector calculus, relativistic tensors, differential forms, Hilbert space, and variational mechanics.</p>
    </header>

    <div class="toggle-grid">
        <!-- Left Column: Equation Selector List -->
        <aside class="toggle-panel-left" aria-label="Physical Theories">
            <div class="glass-card list-card">
                <div class="list-card-header">
                    <h2>Physical Laws</h2>
                    <span class="theory-count-pill">5 Laws</span>
                </div>
                <div class="theory-list" id="theory-list">
                    <!-- JS Populated -->
                </div>
            </div>
        </aside>

        <!-- Right Column: Interactive Representation Viewer -->
        <div class="toggle-panel-right">
            <div class="glass-card main-viewer-card" id="viewer-card">
                <div class="viewer-header-info">
                    <div class="theory-meta">
                        <span id="active-category" class="category-badge">Electromagnetism</span>
                        <h2 id="active-theory-title">Maxwell's Equations</h2>
                    </div>
                    <p id="active-theory-description" class="theory-desc">The classical equations of electrodynamics.</p>
                </div>

                <!-- Representation Tab Bar + Rosetta Compare Controls -->
                <div class="rep-tabs-wrapper">
                    <div class="rep-tabs" id="rep-tabs-container">
                        <!-- JS Populated -->
                    </div>
                    <div class="compare-controls">
                        <button type="button" id="btn-compare-toggle" class="btn-compare-toggle" aria-pressed="false" title="Compare two formulations side-by-side">
                            <span class="compare-icon">⇄</span> Compare Side-by-Side
                        </button>
                        <div class="compare-select-wrap" id="compare-select-wrap" style="display: none;">
                            <label for="compare-rep-select" class="compare-vs-label">vs:</label>
                            <select id="compare-rep-select" class="compare-rep-select" aria-label="Compare against representation"></select>
                        </div>
                    </div>
                </div>

                <!-- Active Equation Math Display (Single or Side-by-Side Rosetta Compare) -->
                <div class="math-stage-grid" id="math-stage-grid">
                    <div class="math-display-container" id="math-card-primary">
                        <div class="math-label-bar">
                            <div class="math-label-left">
                                <span class="math-label"><strong id="active-rep-name" class="accent-text">Gibbs Vector (Differential)</strong></span>
                                <div class="rep-tags-strip" id="active-rep-tags"></div>
                            </div>
                            <button type="button" id="btn-copy-latex" class="btn-copy-latex" title="Copy raw LaTeX to clipboard">Copy LaTeX</button>
                        </div>
                        <div class="math-box">
                            <div id="active-math-render" class="math-render-field">
                                <!-- MathJax Equations go here -->
                            </div>
                        </div>
                    </div>

                    <div class="compare-bridge-badge" id="compare-bridge-badge" style="display: none;" aria-hidden="true">⟺</div>

                    <div class="math-display-container math-compare-card" id="math-card-compare" style="display: none;">
                        <div class="math-label-bar">
                            <div class="math-label-left">
                                <span class="math-label"><strong id="compare-rep-name" class="accent-text">Relativistic Tensor</strong></span>
                                <div class="rep-tags-strip" id="compare-rep-tags"></div>
                            </div>
                            <button type="button" id="btn-copy-compare-latex" class="btn-copy-latex" title="Copy comparison LaTeX to clipboard">Copy LaTeX</button>
                        </div>
                        <div class="math-box">
                            <div id="compare-math-render" class="math-render-field">
                                <!-- Comparison MathJax Equation -->
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Visual Translation Key Strip -->
                <div class="translation-key-bar" id="translation-key-bar">
                    <span class="translation-key-label">Translation Key</span>
                    <div class="translation-chips" id="translation-chips">
                        <!-- JS Populated MathJax Mapping Chips -->
                    </div>
                </div>

                <!-- Description & Insight Section -->
                <div class="insight-section">
                    <div class="insight-grid">
                        <div class="insight-card">
                            <h3>Physical Interpretation &amp; Insight</h3>
                            <p id="active-rep-insight">Select a representation to view its physical description.</p>
                        </div>
                        <div class="insight-card">
                            <h3>Formulation Utility</h3>
                            <p id="active-rep-utility">Explanation of why and when this formulation is used by physicists.</p>
                        </div>
                    </div>
                </div>

                <!-- Semantic Glossary Table -->
                <div class="glossary-section" id="glossary-section">
                    <h3>Semantic Variable Glossary</h3>
                    <p class="ref-sub">Click variable names to jump directly to their definitions in the Constants &amp; Symbols Registry.</p>
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
    padding-top: 6px;
    max-width: 1260px;
    margin: 0 auto;
}

.toggle-header {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
    padding: 4px 0 12px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    text-align: left;
}

.toggle-header h1 {
    font-size: 1.65rem;
    line-height: 1.15;
    color: #ffffff;
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-color));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.toggle-header .tagline {
    color: var(--text-muted);
    font-size: 0.88rem;
    line-height: 1.4;
    margin: 0;
}

.toggle-grid {
    display: grid;
    grid-template-columns: 275px minmax(0, 1fr);
    gap: 20px;
    align-items: start;
}

.toggle-panel-right {
    min-width: 0;
}

@media (max-width: 960px) {
    .toggle-grid {
        grid-template-columns: 1fr;
    }
}

.glass-card {
    background: rgba(15, 23, 42, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 20px;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
}

.list-card {
    position: sticky;
    top: 84px;
    padding: 16px;
}

@media (max-width: 960px) {
    .list-card {
        position: static;
    }
}

.list-card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.list-card h2 {
    margin: 0;
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
    font-size: 1.05rem;
}

.theory-count-pill {
    font-size: 0.7rem;
    font-weight: 600;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 2px 8px;
    border-radius: 10px;
}

.ref-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-top: 0;
    margin-bottom: 14px;
    line-height: 1.4;
}

/* Sidebar List */
.theory-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.theory-item {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-left: 3px solid var(--theme-color, var(--accent-color));
    border-radius: 10px;
    padding: 11px 12px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.theory-item:hover {
    background: rgba(255, 255, 255, 0.06);
    border-color: rgba(255, 255, 255, 0.12);
    border-left-color: var(--theme-color, var(--accent-color));
    transform: translateX(3px);
}

.theory-item.active {
    background: rgba(100, 255, 218, 0.07);
    border-color: rgba(255, 255, 255, 0.18);
    border-left-color: var(--theme-color, var(--accent-color));
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
}

.theory-item-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 3px;
}

.theory-item h3 {
    margin: 0;
    font-size: 0.92rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.theory-forms-badge {
    font-size: 0.66rem;
    font-weight: 600;
    color: var(--theme-color, var(--accent-color));
    background: rgba(255, 255, 255, 0.05);
    padding: 1px 6px;
    border-radius: 8px;
    white-space: nowrap;
}

.theory-item p {
    margin: 0;
    font-size: 0.76rem;
    color: var(--text-muted);
    line-height: 1.3;
}

/* Viewer Card */
.viewer-header-info {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 14px;
    margin-bottom: 16px;
}

.theory-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}

.theory-meta h2 {
    margin: 0;
    font-size: 1.45rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.category-badge {
    padding: 3px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid var(--theme-border-color, rgba(100, 255, 218, 0.35));
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.1));
    color: var(--theme-color, var(--accent-color));
}

.theory-desc {
    margin: 0;
    font-size: 0.88rem;
    color: var(--text-muted);
    line-height: 1.45;
}

/* Representation Tabs + Compare Controls */
.rep-tabs-wrapper {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.rep-tabs {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
}

.rep-tab {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.07);
    color: var(--text-muted);
    padding: 7px 13px;
    border-radius: 8px;
    font-size: 0.82rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'Space Grotesk', sans-serif;
}

.rep-tab:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.16);
}

.rep-tab.active {
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.12));
    border-color: var(--theme-border-color, rgba(100, 255, 218, 0.45));
    color: #ffffff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
}

.compare-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.btn-compare-toggle {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #cbd5e1;
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-compare-toggle:hover {
    background: rgba(255, 255, 255, 0.09);
    color: #ffffff;
}

.btn-compare-toggle.is-comparing {
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.14));
    border-color: var(--theme-color, var(--accent-color));
    color: #ffffff;
    box-shadow: 0 0 12px var(--theme-bg-color, rgba(100, 255, 218, 0.2));
}

.compare-select-wrap {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.compare-vs-label {
    font-size: 0.74rem;
    font-weight: 700;
    text-transform: uppercase;
    color: var(--text-muted);
}

.compare-rep-select {
    background: rgba(3, 7, 18, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #ffffff;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 0.78rem;
    font-family: 'Space Grotesk', sans-serif;
    outline: none;
}

/* Math Stage Grid (Single vs Side-by-Side Compare) */
.math-stage-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr);
    gap: 12px;
    margin-bottom: 14px;
    align-items: stretch;
}

.math-stage-grid.is-comparing {
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
}

@media (max-width: 820px) {
    .math-stage-grid.is-comparing {
        grid-template-columns: minmax(0, 1fr);
    }
    .compare-bridge-badge {
        justify-self: center;
        transform: rotate(90deg);
    }
}

.compare-bridge-badge {
    align-self: center;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--theme-color, var(--accent-color));
    background: var(--theme-bg-color, rgba(100, 255, 218, 0.1));
    border: 1px solid var(--theme-border-color, rgba(100, 255, 218, 0.35));
    width: 38px;
    height: 38px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 18px var(--theme-bg-color, rgba(100, 255, 218, 0.18));
}

.math-display-container {
    background: rgba(3, 7, 18, 0.55);
    border: 1px solid var(--theme-border-color, rgba(255, 255, 255, 0.08));
    border-radius: 12px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

.math-label-bar {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 12px;
}

.math-label-left {
    display: flex;
    flex-direction: column;
    gap: 6px;
    min-width: 0;
}

.math-label {
    font-size: 0.78rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.accent-text {
    color: var(--theme-color, var(--accent-color));
}

.rep-tags-strip {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.rep-sig-tag {
    font-size: 0.68rem;
    font-weight: 600;
    color: #cbd5e1;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.09);
    padding: 2px 7px;
    border-radius: 10px;
}

.btn-copy-latex {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: var(--text-muted);
    padding: 4px 10px;
    border-radius: 6px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s ease;
}

.btn-copy-latex:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #ffffff;
}

.btn-copy-latex.copied {
    border-color: #34d399;
    color: #34d399;
    background: rgba(52, 211, 153, 0.12);
}

.math-box {
    flex: 1;
    padding: 18px 12px;
    text-align: center;
    overflow-x: auto;
    border-radius: 8px;
    background: rgba(2, 6, 23, 0.78);
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: inset 0 0 28px var(--theme-bg-color, rgba(100, 255, 218, 0.04));
    display: flex;
    align-items: center;
    justify-content: center;
}

.math-render-field {
    font-size: 1.32rem;
    color: #ffd700;
    min-height: 54px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
}

.math-stage-grid.is-comparing .math-render-field {
    font-size: 1.08rem;
}

/* Translation Key Strip */
.translation-key-bar {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
    padding: 10px 14px;
    margin-bottom: 18px;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid var(--theme-border-color, rgba(100, 255, 218, 0.2));
    border-left: 3px solid var(--theme-color, var(--accent-color));
    border-radius: 10px;
}

.translation-key-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--theme-color, var(--accent-color));
    white-space: nowrap;
}

.translation-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
}

.translation-chip {
    background: rgba(2, 6, 23, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 0.84rem;
    color: #e2e8f0;
    display: inline-flex;
    align-items: center;
}

/* Description & Insight */
.insight-section {
    margin-bottom: 22px;
}

.insight-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
}

@media (max-width: 700px) {
    .insight-grid {
        grid-template-columns: 1fr;
    }
}

.insight-card {
    background: rgba(255, 255, 255, 0.015);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 10px;
    padding: 16px;
}

.insight-card h3 {
    margin: 0 0 8px 0;
    font-size: 0.84rem;
    color: #ffffff;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    padding-bottom: 6px;
}

.insight-card p {
    margin: 0;
    font-size: 0.88rem;
    color: var(--text-muted);
    line-height: 1.55;
}

/* Glossary Section */
.glossary-section h3 {
    margin: 0 0 4px 0;
    font-size: 0.96rem;
    color: #ffffff;
    font-family: 'Space Grotesk', sans-serif;
}

.table-wrapper {
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    background: rgba(3, 7, 18, 0.25);
    overflow-x: auto;
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
    padding: 9px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    font-family: 'Space Grotesk', sans-serif;
    text-transform: uppercase;
    font-size: 0.72rem;
    letter-spacing: 0.5px;
}

.glossary-table td {
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-color);
}

.glossary-table tbody tr {
    transition: background 0.15s;
}

.glossary-table tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
}

.var-sym {
    font-family: 'Space Grotesk', monospace;
    font-weight: bold;
    color: var(--theme-color, var(--accent-color));
}

.var-link {
    color: var(--text-color);
    text-decoration: none;
    border-bottom: 1px dotted var(--text-muted);
    font-weight: 500;
    transition: border-color 0.2s, color 0.2s;
}

.var-link:hover {
    color: var(--theme-color, var(--accent-color));
    border-bottom-color: var(--theme-color, var(--accent-color));
}

.var-dim {
    font-family: monospace;
    color: var(--text-muted);
}
</style>

<script src="/js/notation_toggle.js?v=<?= @filemtime(PROJECT_ROOT . '/public/js/notation_toggle.js') ?: 1 ?>" nonce="<?= $nonce ?>" defer></script>
