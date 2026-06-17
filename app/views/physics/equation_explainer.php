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

    <div class="explainer-grid">
        <!-- Left Column: LaTeX Compiler and Sandbox -->
        <div class="explainer-panel-left">
            <div class="glass-card main-explainer-card">
                <h3 style="font-family: 'Space Grotesk', sans-serif; margin-top: 0; color: #ffffff; display: flex; align-items: center; gap: 8px;">
                    <span style="display: inline-block; width: 4px; height: 16px; background: var(--accent-default, #64ffda); border-radius: 2px;"></span>
                    Equation Compiler
                </h3>
                
                <div class="input-group" style="margin-bottom: 20px;">
                    <label for="latex-input" style="display: block; margin-bottom: 8px; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8);">
                        Input LaTeX Equation:
                    </label>
                    <div style="position: relative;">
                        <textarea id="latex-input" 
                                  placeholder="e.g. i \hbar \frac{\partial}{\partial t}\Psi = \hat{H}\Psi" 
                                  autocomplete="off" 
                                  rows="3"
                                  style="width: 100%; padding: 12px; background: rgba(3, 7, 18, 0.75); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; color: #f1f5f9; font-family: 'Fira Code', 'Courier New', monospace; font-size: 0.95rem; line-height: 1.4; resize: vertical; box-sizing: border-box; outline: none; transition: border-color 0.2s;"></textarea>
                        <button id="clear-input-btn" 
                                style="position: absolute; right: 10px; bottom: 12px; background: transparent; border: none; color: var(--text-muted, #94a3b8); cursor: pointer; font-size: 0.75rem; text-transform: uppercase; font-family: 'Space Grotesk', sans-serif; font-weight: 600; transition: color 0.2s;"
                                onmouseover="this.style.color='#f43f5e'"
                                onmouseout="this.style.color='var(--text-muted)'">
                            Clear
                        </button>
                    </div>
                </div>

                <!-- Math Rendering Box -->
                <div class="math-preview-container" style="margin-bottom: 25px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8);">MathJax Render</span>
                        <span id="compiler-status" style="font-size: 0.75rem; color: #10b981; display: flex; align-items: center; gap: 4px;">
                            <span style="width: 6px; height: 6px; background: currentColor; border-radius: 50%; display: inline-block;"></span>
                            Ready
                        </span>
                    </div>
                    <div id="math-preview-box" 
                         style="background: linear-gradient(135deg, rgba(15, 23, 42, 0.5) 0%, rgba(3, 7, 18, 0.8) 100%); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 35px 20px; text-align: center; min-height: 100px; display: flex; align-items: center; justify-content: center; box-sizing: border-box; position: relative; overflow-x: auto;">
                        <div id="math-render-target" style="font-size: 1.6rem; color: #ffd700; transition: color 0.2s;">
                            <!-- LaTeX rendered here -->
                        </div>
                    </div>
                </div>

                <!-- Tokenized Symbols Breakdown Section -->
                <div id="symbols-breakdown" style="display: none; margin-bottom: 25px; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 20px;">
                    <h4 style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted, #94a3b8); margin: 0 0 12px 0; font-family: 'Space Grotesk', sans-serif;">
                        Equation Component Breakdown
                    </h4>
                    <div id="symbols-list" style="display: flex; flex-direction: column; gap: 8px;">
                        <!-- JS populated -->
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Interactive Physical Explanation & Breakdown -->
        <div class="explainer-panel-right">
            <div class="glass-card details-card" style="min-height: 480px; box-sizing: border-box; display: flex; flex-direction: column;">
                
                <!-- Status Banner / Header -->
                <div id="explanation-header-wrapper" style="border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 15px; margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 15px;">
                        <div>
                            <h2 id="formula-title" style="margin: 0 0 4px 0; font-size: 1.4rem; color: #ffffff; font-family: 'Space Grotesk', sans-serif;">
                                Selecting Equation...
                            </h2>
                            <span id="formula-badge" class="badge-status badge-unregistered" style="font-size: 0.7rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 3px 8px; border-radius: 4px; display: inline-block;">
                                Live Analysis
                            </span>
                        </div>
                        <div id="solver-redirect-container" style="display: none;">
                            <a id="solver-redirect-link" href="#" class="btn btn-secondary" style="font-size: 0.78rem; padding: 6px 12px; height: auto; border-radius: 6px; display: inline-flex; align-items: center; gap: 6px; text-decoration: none; font-weight: 600;">
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                                Audit Dimensions
                            </a>
                        </div>
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

                    <!-- Tiers Section (Only shown when formula has detailed breakdowns) -->
                    <div id="official-breakdown" style="display: none; flex-direction: column; gap: 15px;">
                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                1. Interpretation (Local Identity)
                            </h4>
                            <p id="local-interpretation" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>

                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                2. Symmetry &amp; Coordinate Invariance
                            </h4>
                            <p id="symmetry-origin" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>

                        <div class="tier-card" style="background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;">
                            <h4 style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; letter-spacing: 0.05em; font-family: 'Space Grotesk', sans-serif;">
                                3. Limiting Cases &amp; Boundaries
                            </h4>
                            <p id="limits-boundary" style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                                --
                            </p>
                        </div>
                    </div>

                    <!-- Topological Bridges Section -->
                    <div id="topological-bridges" style="display: none; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 15px; margin-top: auto;">
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
    grid-template-columns: 1.1fr 1fr;
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
</script>

<script src="/js/equation_explainer.js" defer></script>
