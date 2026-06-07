<div class="explorer-container">
    <div class="explorer-header">
        <h1>Concept Derivation Genealogy Explorer</h1>
        <p class="tagline">Trace the mathematical ancestry and lineage of physical laws. Explore the relational dependencies between fundamental axioms, intermediate derivations, and modern applications.</p>
    </div>

    <div class="explorer-grid">
        <!-- Left Column: Node Inspector Panel -->
        <div class="explorer-panel-left">
            <div class="glass-card inspector-card" id="inspector-card">
                <h3>Node Inspector</h3>
                <p class="ref-sub" id="inspector-tip">Click on any node in the network graph to inspect its mathematical definition and derivation lineage.</p>
                
                <div id="inspector-content" style="display: none;">
                    <div class="inspector-section">
                        <span id="active-node-type" class="category-badge">Core Theory</span>
                        <h4 id="active-node-title" style="margin: 10px 0 6px 0; font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; color: #ffffff;">Schrödinger Equation</h4>
                    </div>

                    <!-- Defining Equation -->
                    <div class="inspector-section" style="margin-top: 15px;">
                        <h5 class="inspector-label">Defining Identity</h5>
                        <div class="math-derivation-box">
                            <div id="active-node-math" class="math-render-small">
                                \[ i\hbar \frac{\partial}{\partial t}\psi = \hat{H}\psi \]
                            </div>
                        </div>
                    </div>

                    <!-- Description -->
                    <div class="inspector-section" style="margin-top: 18px;">
                        <h5 class="inspector-label">Physical Description</h5>
                        <p id="active-node-desc" style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.5; margin: 4px 0 0 0;">
                            Description text.
                        </p>
                    </div>

                    <!-- Lineage lists -->
                    <div class="inspector-section" style="margin-top: 20px;">
                        <h5 class="inspector-label">Derived From (Axioms / Ancestors)</h5>
                        <div id="active-node-ancestors" class="tag-list">
                            <!-- Clickable tags -->
                        </div>
                    </div>

                    <div class="inspector-section" style="margin-top: 18px;">
                        <h5 class="inspector-label">Leads To (Applications / Descendants)</h5>
                        <div id="active-node-descendants" class="tag-list">
                            <!-- Clickable tags -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Network Panel -->
        <div class="explorer-panel-right">
            <div class="glass-card main-explorer-card" id="explorer-card">
                
                <!-- Active Header & Search -->
                <div class="explorer-header-info" style="display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap;">
                    <div class="theory-meta">
                        <span class="category-badge" style="border-color: rgba(234,179,8,0.35); background: rgba(234,179,8,0.1); color: var(--accent-math-methods);">Lineage Network</span>
                        <h2 style="margin: 0; font-size: 1.8rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif;">Derivation Map</h2>
                    </div>
                    
                    <!-- Search Input -->
                    <div class="search-box-container" style="position: relative;">
                        <input type="text" id="node-search" placeholder="Search laws or axioms..." style="background: rgba(3,7,18,0.6); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 8px 16px; font-size: 0.85rem; color: #ffffff; width: 220px; font-family: 'Space Grotesk', sans-serif; outline: none; transition: border-color 0.2s;">
                        <span style="position: absolute; right: 12px; top: 9px; color: var(--text-muted); font-size: 0.8rem; pointer-events: none;">🔍</span>
                    </div>
                </div>

                <!-- Simulation & Interactive Playground -->
                <div class="playground-section" style="position: relative; margin-bottom: 0;">
                    <div class="playground-header">
                        <h4>Force-Directed Derivation Network</h4>
                        <div style="display: flex; gap: 10px; align-items: center;">
                            <button id="reset-forces-btn" class="btn btn-secondary" style="font-size: 0.72rem; padding: 3px 8px; border-radius: 4px;">Recenter Graph</button>
                            <span class="sandbox-badge" style="color: var(--accent-math-methods); background: rgba(234,179,8,0.1); border-color: rgba(234,179,8,0.2);">Interactive Graph</span>
                        </div>
                    </div>
                    
                    <!-- Canvas Container -->
                    <div class="canvas-container" style="aspect-ratio: 16 / 9.5; cursor: grab;">
                        <canvas id="genealogy-canvas"></canvas>
                        
                        <!-- Floating Legend Overlay -->
                        <div class="graph-legend-overlay">
                            <span class="legend-item"><span class="legend-dot" style="background: #3b82f6;"></span> Axiom</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #8b5cf6;"></span> Derivation</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #ff4e88;"></span> Core Theory</span>
                            <span class="legend-item"><span class="legend-dot" style="background: #10b981;"></span> Application</span>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    </div>
</div>

<style>
/* Page Layout */
.explorer-container {
    padding-top: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.explorer-header {
    margin-bottom: 30px;
    text-align: center;
}

.explorer-header h1 {
    font-size: 2.2rem;
    color: #ffffff;
    margin-bottom: 10px;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-math-methods));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.explorer-header .tagline {
    color: var(--text-muted);
    font-size: 1.05rem;
}

.explorer-grid {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 30px;
    align-items: start;
}

@media (max-width: 980px) {
    .explorer-grid {
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

.inspector-card {
    min-height: 500px;
    position: sticky;
    top: 20px;
}

.inspector-card h3 {
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

.inspector-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 6px 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    padding-bottom: 4px;
}

/* Math Derivation box */
.math-derivation-box {
    background: rgba(3, 7, 18, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.03);
    border-radius: 8px;
    padding: 14px 6px;
    text-align: center;
    overflow-x: auto;
}

.math-render-small {
    font-size: 1.1rem;
    color: #ffd700;
    min-height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Clickable Tag Lists */
.tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 6px;
}

.node-tag {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: var(--text-color);
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.78rem;
    cursor: pointer;
    font-family: 'Space Grotesk', sans-serif;
    transition: all 0.2s;
}

.node-tag:hover {
    background: var(--accent-math-methods);
    color: #020617;
    border-color: var(--accent-math-methods);
    transform: translateY(-1px);
}

.node-tag.tag-axiom:hover { background: #3b82f6; border-color: #3b82f6; }
.node-tag.tag-derivation:hover { background: #8b5cf6; border-color: #8b5cf6; }
.node-tag.tag-theory:hover { background: #ff4e88; border-color: #ff4e88; }
.node-tag.tag-application:hover { background: #10b981; border-color: #10b981; }

.tag-empty {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-style: italic;
}

/* Right Panel Layout */
.explorer-header-info {
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 20px;
    margin-bottom: 24px;
}

.category-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    border: 1px solid rgba(234, 179, 8, 0.35);
    background: rgba(234, 179, 8, 0.1);
    color: var(--accent-math-methods);
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
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.canvas-container {
    width: 100%;
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

/* Floating Legend */
.graph-legend-overlay {
    position: absolute;
    bottom: 15px;
    left: 15px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 6px;
    padding: 10px 14px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    pointer-events: none;
    font-size: 0.72rem;
    font-family: 'Space Grotesk', sans-serif;
}

.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-color);
}

.legend-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
}
</style>

<script src="/js/genealogy_explorer.js" nonce="<?= $nonce ?>" defer></script>
