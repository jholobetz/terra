<?php
// Interactive LaTeX Equation Explainer view
$constantsJson = @file_get_contents(PROJECT_ROOT . '/app/config/content/constants.json') ?: '{}';
?>

<div class="explainer-container">
    <div class="explainer-header" style="margin-bottom: 30px; text-align: center;">
        <h1 style="font-size: 2.5rem; color: #ffffff; margin-bottom: 10px; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 40%, var(--accent-default, #64ffda)); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🔬 Interactive Equation Explainer
        </h1>
        <p class="tagline" style="color: var(--text-muted, #94a3b8); font-size: 1.05rem;">
            Compile LaTeX formulas in real-time, trace their physical origins, and map continuous symmetries directly to conserved quantities.
        </p>
    </div>

    <!-- Math Rendering Box (Full-Width Top Panel) -->
    <div class="glass-card math-preview-fullwidth" style="margin-bottom: 30px; padding: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8); font-family: 'Space Grotesk', sans-serif; font-weight: 600;">MathJax Render</span>
            <span id="compiler-status" style="font-size: 0.78rem; color: #10b981; display: flex; align-items: center; gap: 4px; font-family: 'Space Grotesk', sans-serif; font-weight: 500;">
                <span style="width: 6px; height: 6px; background: currentColor; border-radius: 50%; display: inline-block;"></span>
                Ready
            </span>
        </div>
        <div id="math-preview-box" 
             style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.5) 0%, rgba(3, 7, 18, 0.8) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 40px 24px; min-height: 110px; display: flex; align-items: center; justify-content: flex-start; box-sizing: border-box; position: relative; overflow-x: auto; max-width: 100%; width: 100%; min-width: 0;">
            <div id="math-render-target" style="font-size: 1.8rem; color: #ffd700; transition: color 0.2s; margin: 0 auto; line-height: 1.4;">
                <!-- LaTeX rendered here -->
            </div>
        </div>
    </div>

    <div class="explainer-grid">
        <!-- Left Column: LaTeX Compiler and Sandbox -->
        <div class="explainer-panel-left">
            <div class="glass-card main-explainer-card">
                <h3 style="font-family: 'Space Grotesk', sans-serif; margin-top: 0; color: #ffffff; display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 4px; height: 16px; background: var(--accent-default, #64ffda); border-radius: 2px;"></span>
                    Equation Compiler
                </h3>
                
                <div class="input-group" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <label for="latex-input" style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8); margin: 0;">
                            Input LaTeX Equation:
                        </label>
                        <button id="copy-input-btn" 
                                style="background: transparent; border: none; color: #eab308; cursor: pointer; font-size: 0.75rem; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 600; transition: color 0.2s; padding: 0;"
                                onmouseover="this.style.color='#fde047'"
                                onmouseout="this.style.color='#eab308'">
                            Copy
                        </button>
                    </div>
                    <div style="position: relative;">
                        <textarea id="latex-input" 
                                  placeholder="e.g. i \hbar \frac{\partial}{\partial t}\Psi = \hat{H}\Psi" 
                                  autocomplete="off" 
                                  rows="3"
                                  style="width: 100%; padding: 12px; padding-right: 60px; background: rgba(3, 7, 18, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; color: #f1f5f9; font-family: 'Fira Code', 'Courier New', monospace; font-size: 0.95rem; line-height: 1.4; resize: vertical; box-sizing: border-box; outline: none; transition: border-color 0.2s;"></textarea>
                        <button id="clear-input-btn" 
                                style="position: absolute; right: 10px; bottom: 12px; background: transparent; border: none; color: #f43f5e; cursor: pointer; font-size: 0.75rem; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 600; transition: color 0.2s;"
                                onmouseover="this.style.color='#fda4af'"
                                onmouseout="this.style.color='#f43f5e'">
                            Clear
                        </button>
                    </div>
                </div>


                <!-- Tokenized Symbols Breakdown Section -->
                <div id="symbols-breakdown" style="display: none; margin-bottom: 25px; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 20px;">
                    <h4 style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8); margin: 0 0 15px 0; font-family: 'Space Grotesk', sans-serif;">
                        Equation Component Breakdown
                    </h4>

                    <!-- Dynamic Domain Selector -->
                    <div id="domain-selector-wrapper" style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); padding: 8px 12px; border-radius: 8px;">
                        <span style="font-size: 0.76rem; color: var(--text-muted, #94a3b8); font-family: 'Space Grotesk', sans-serif; font-weight: 500;">Active Physics Domain</span>
                        <select id="active-domain-select" style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(100, 255, 218, 0.15); color: var(--accent-default, #64ffda); border-radius: 6px; padding: 4px 10px; font-family: 'Space Grotesk', sans-serif; font-size: 0.76rem; font-weight: 500; cursor: pointer; outline: none; transition: all 0.2s;" onfocus="this.style.borderColor='var(--accent-default)'" onblur="this.style.borderColor='rgba(100, 255, 218, 0.15)'">
                            <option value="classical_mechanics">Classical Mechanics</option>
                            <option value="thermodynamics">Thermodynamics</option>
                            <option value="electromagnetism">Electromagnetism</option>
                            <option value="quantum_mechanics">Quantum & Particle Physics</option>
                            <option value="optics">Optics & Wave Physics</option>
                        </select>
                    </div>
                    
                    <div id="variables-section">
                        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--accent-default, #64ffda); margin-bottom: 8px; font-weight: 600;">Base Variables & Constants</div>
                        <div id="symbols-list" style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 20px;">
                            <!-- JS populated -->
                        </div>
                    </div>

                    <div id="modifiers-section" style="display: none; border-top: 1px dashed rgba(255, 255, 255, 0.08); padding-top: 15px; margin-top: 15px;">
                        <div style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #a855f7; margin-bottom: 8px; font-weight: 600;">Subscripts, Superscripts & Modifiers</div>
                        <div id="modifiers-list" style="display: flex; flex-direction: column; gap: 8px;">
                            <!-- JS populated -->
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Physical Explanation & Breakdown -->
        <div class="explainer-panel-right">
            <div class="glass-card details-card" style="min-height: 480px; box-sizing: border-box; display: flex; flex-direction: column;">
                
                <!-- Status Banner / Header -->
                <div id="explanation-header-wrapper" style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 15px; margin-bottom: 20px;">
                    <div id="explainer-breadcrumbs" style="display: none; font-size: 0.8rem; font-family: 'Space Grotesk', sans-serif; color: var(--text-muted, #94a3b8); margin-bottom: 8px; align-items: center; gap: 6px;"></div>
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px;">
                        <div>
                            <h2 id="formula-title" style="margin: 0 0 4px 0; font-size: 1.4rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif;">
                                Selecting Equation...
                            </h2>
                        </div>
                        <span id="formula-badge" style="display: none; padding: 4px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;"></span>
                    </div>
                </div>

                <!-- Main Explanation Body -->
                <div id="explanation-content" style="flex: 1; display: flex; flex-direction: column; gap: 20px;">
                    
                    <!-- Fallback Placeholder -->
                    <div id="explainer-placeholder" style="text-align: center; padding: 40px 20px; color: var(--text-muted, #94a3b8); flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;">
                        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.4;">
                            <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <line x1="10" y1="9" x2="8" y2="9"/>
                        </svg>
                        <div>
                            <p style="margin: 0; font-weight: 500;">No Equation Loaded</p>
                            <p style="margin: 4px 0 0 0; font-size: 0.82rem; opacity: 0.7;">Type a LaTeX formula or click one of the quick load examples to analyze.</p>
                        </div>
                    </div>

                    <!-- Section 1: Explanation Banner -->
                    <div id="conceptual-intro-card" style="display: none; background: rgba(100, 255, 218, 0.03); border: 1px solid rgba(100, 255, 218, 0.12); border-radius: 12px; padding: 20px; flex-direction: column; gap: 12px;">
                        <!-- JS populated -->
                    </div>

                    <!-- Section 3: Physical Meaning & Scenarios -->
                    <div id="ai-scenarios-section" style="display: none; flex-direction: column; gap: 12px;">
                        <h3 style="font-size: 1.1rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif; margin: 0; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                            Understand the Physical Meaning
                        </h3>
                        <div id="ai-scenarios-list" style="display: flex; flex-direction: column; gap: 12px;">
                            <!-- Dynamic scenario blocks -->
                        </div>
                    </div>

                    <!-- Tiers Section (Only shown when formula has detailed breakdowns) -->
                    <div id="official-breakdown" style="display: none; flex-direction: column; gap: 15px;">
                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                Interpretation (Local Identity)
                            </h4>
                            <p id="local-interpretation" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>

                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                Symmetry &amp; Coordinate Invariance
                            </h4>
                            <p id="symmetry-origin" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>

                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                Limiting Cases &amp; Boundaries
                            </h4>
                            <p id="limits-boundary" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>
                    </div>

                    <!-- Knowledge Graph Ancestry Card -->
                    <div id="knowledge-graph-card" style="display: none; background: rgba(100, 255, 218, 0.03); border: 1px solid rgba(100, 255, 218, 0.15); border-radius: 12px; padding: 20px; flex-direction: column; gap: 12px;">
                        <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                            🕸️ Knowledge Graph Ancestry &amp; Relational Edges
                        </h4>
                        <div id="knowledge-graph-details" style="font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                            <!-- JS populated -->
                        </div>
                    </div>

                    <!-- Section 4: Live Simulation Sandbox -->
                    <div id="ai-simulation-card" style="display: none !important; background: rgba(15, 23, 42, 0.4); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 20px; flex-direction: column; gap: 15px; margin-top: 10px;">
                        <h3 style="font-size: 1.1rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif; margin: 0; font-weight: 600; display: flex; align-items: center; justify-content: space-between;">
                            <span style="display: flex; align-items: center; gap: 8px;">
                                Interactive Sandbox
                            </span>
                            <!-- Sonification Button -->
                            <button id="sonify-toggle-btn" style="background: rgba(100, 255, 218, 0.05); border: 1px solid rgba(100, 255, 218, 0.2); color: var(--accent-default, #64ffda); padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 0.72rem; font-family: 'Space Grotesk', sans-serif; font-weight: 600; display: flex; align-items: center; gap: 4px; transition: all 0.2s;">
                                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
                                Sonify Math
                            </button>
                        </h3>

                        <!-- Dynamic Simulation Canvas -->
                        <div style="position: relative; width: 100%; height: 180px; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255, 255, 255, 0.04); border-radius: 8px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                            <canvas id="sandbox-canvas" width="400" height="180" style="display: block; width: 100%; height: 100%;"></canvas>
                        </div>

                        <!-- Parameter Sliders Container -->
                        <div id="sandbox-sliders" style="display: flex; flex-direction: column; gap: 12px;">
                            <!-- JS populated sliders -->
                        </div>
                    </div>

                    <!-- Topological Bridges Section -->
                    <div id="topological-bridges" style="display: none; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 20px; margin-top: 10px;">
                        <h4 style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8); margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif;">
                            Topological Bridges (Encyclopedia Contexts)
                        </h4>
                        <div id="bridges-container" style="display: flex; flex-wrap: wrap; gap: 10px;">
                            <!-- JS populated -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<style>
.explainer-container {
    padding-top: 10px;
    max-width: 1200px;
    margin: 0 auto;
    box-sizing: border-box;
}

.explainer-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
    gap: 30px;
    align-items: start;
}

@media (max-width: 950px) {
    .explainer-grid {
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
    box-sizing: border-box;
}

.explainer-example-btn:hover {
    background: rgba(100, 255, 218, 0.08) !important;
    border-color: rgba(100, 255, 218, 0.3) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(100, 255, 218, 0.05);
}

.explainer-example-btn:active {
    transform: translateY(0);
}

/* Badge Styling */
.badge-status {
    border: 1px solid;
}
.badge-platinum {
    background: rgba(100, 255, 218, 0.15);
    border-color: rgba(100, 255, 218, 0.4);
    color: var(--accent-default, #64ffda);
    box-shadow: 0 0 10px rgba(100, 255, 218, 0.15);
}
.badge-draft {
    background: rgba(251, 191, 36, 0.12);
    border-color: rgba(251, 191, 36, 0.3);
    color: #fbbf24;
}
.badge-unregistered {
    background: rgba(148, 163, 184, 0.12);
    border-color: rgba(148, 163, 184, 0.3);
    color: #94a3b8;
}

/* Variable/Constant row layout */
.symbol-row {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 10px 12px;
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.04);
    border-radius: 8px;
    transition: all 0.2s ease;
}
.symbol-row:hover {
    background: rgba(255, 255, 255, 0.04);
    border-color: rgba(255, 255, 255, 0.08);
}
.symbol-badge {
    min-width: 45px;
    height: 32px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(100, 255, 218, 0.08);
    border: 1px solid rgba(100, 255, 218, 0.25);
    border-radius: 6px;
    color: var(--accent-default, #64ffda);
    font-family: 'Space Grotesk', 'Fira Code', monospace;
    font-size: 0.95rem;
    font-weight: 500;
}
.symbol-badge.constant-type {
    background: rgba(244, 63, 94, 0.08);
    border-color: rgba(244, 63, 94, 0.25);
    color: #f43f5e;
}
.symbol-badge.operator-type {
    background: rgba(168, 85, 247, 0.08);
    border-color: rgba(168, 85, 247, 0.25);
    color: #c084fc;
}
.symbol-badge.modifier-type {
    background: rgba(245, 158, 11, 0.08);
    border-color: rgba(245, 158, 11, 0.25);
    color: #fbbf24;
}

/* Ensure MathJax symbols inside badges inherit color-coding */
.symbol-badge mjx-container {
    color: inherit !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Related subtopics link cards */
.bridge-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    background: rgba(100, 255, 218, 0.04);
    border: 1px solid rgba(100, 255, 218, 0.15);
    border-radius: 6px;
    color: #e2e8f0;
    text-decoration: none;
    font-size: 0.82rem;
    transition: all 0.2s ease;
}
.bridge-tag:hover {
    background: rgba(100, 255, 218, 0.08);
    border-color: rgba(100, 255, 218, 0.35);
    color: var(--accent-default, #64ffda);
    transform: translateY(-1px);
}
</style>

<!-- Inject state from PHP to JS -->
<script nonce="<?= $nonce ?>">
window.INITIAL_ID = <?= json_encode($id) ?>;
window.INITIAL_LATEX = <?= json_encode($latex) ?>;
window.INITIAL_FORMULA = <?= json_encode($formula) ?>;
window.INITIAL_SUBTOPICS = <?= json_encode($subtopics) ?>;
window.PHYSICS_CONSTANTS = <?= $constantsJson ?>;
window.SUBTOPIC_SLUG = <?= json_encode($subtopicSlug) ?>;
window.SUBTOPIC_VARIABLES = <?= json_encode($subtopicVariables) ?>;
window.INITIAL_DOMAIN = <?= json_encode($domain) ?>;
</script>

<script src="/js/equation_explainer.js?v=<?= filemtime(PROJECT_ROOT . '/public/js/equation_explainer.js') ?>" defer></script>
