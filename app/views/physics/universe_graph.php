<div class="universe-graph-container">

    <!-- Compact Cosmic Instrument Command Header -->
    <header class="ug-header">
        <div class="ug-header-left">
            <h1>Physics Universe Knowledge Graph</h1>
            <p class="ug-tagline">Explore mathematical lineage, upstream axioms, and downstream derivations across all 12 branches of physics.</p>
        </div>

        <!-- Quick Actions & Hop Depth Control -->
        <div class="ug-header-actions">
            <div class="ug-depth-group" role="group" aria-label="Graph Hop Depth">
                <span class="ug-depth-label">Depth</span>
                <button type="button" class="ug-depth-btn" data-depth="1">1</button>
                <button type="button" class="ug-depth-btn active" data-depth="2">2</button>
                <button type="button" class="ug-depth-btn" data-depth="3">3</button>
            </div>
            <button type="button" id="btn-universe-fullscreen" class="ug-action-btn ug-action-primary">
                ⛶ Full Screen Map
            </button>
            <a href="/physics/equation-explainer" class="ug-action-btn">
                🔬 Equation Explainer
            </a>
        </div>
    </header>

    <!-- Main Split-Rail Workspace Grid -->
    <div class="universe-workspace-grid">

        <!-- Left Sticky Rail: Search + Landmark Hubs & Route Finder -->
        <aside class="ug-rail" aria-label="Formula Search and Route Finder">

            <!-- 1. Unified Search & Landmark Hubs Card -->
            <div class="ug-card">
                <div class="ug-card-head">
                    <h2>Find &amp; Center Formula</h2>
                    <span class="ug-count-pill">15,583 Formulas</span>
                </div>

                <div class="ug-search-wrap">
                    <input type="text"
                           id="graph-search-input"
                           class="ug-input"
                           placeholder="Search 'Schrödinger', 'Lorentz', 'Carnot'..."
                           autocomplete="off" />
                    <div id="graph-search-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                </div>

                <div class="ug-sub-label">Landmark Physics Hubs</div>
                <div class="ug-hubs-list" id="landmark-hubs-list">
                    <button type="button" class="hub-btn is-active" data-id="time-dependent-schrodinger-equation">
                        <span>Schrödinger Wave Equation</span>
                        <span class="hub-domain" style="color: #34d399;">Quantum</span>
                    </button>
                    <button type="button" class="hub-btn" data-id="lorentz-factor-exact">
                        <span>Exact Lorentz Factor (γ)</span>
                        <span class="hub-domain" style="color: #38bdf8;">Relativity</span>
                    </button>
                    <button type="button" class="hub-btn" data-id="amp-re-maxwell-identity-bf5142b0">
                        <span>Ampère–Maxwell Law</span>
                        <span class="hub-domain" style="color: #60a5fa;">E&amp;M</span>
                    </button>
                    <button type="button" class="hub-btn" data-id="dirac-equation">
                        <span>Dirac Relativistic Equation</span>
                        <span class="hub-domain" style="color: #c084fc;">QFT</span>
                    </button>
                    <button type="button" class="hub-btn" data-id="navier-stokes-momentum-fluids-27e5bf4d">
                        <span>Navier–Stokes Equations</span>
                        <span class="hub-domain" style="color: #2dd4bf;">Fluids</span>
                    </button>
                    <button type="button" class="hub-btn" data-id="gibbs-entropy-formula-fb0b23b8">
                        <span>Gibbs Entropy Formula</span>
                        <span class="hub-domain" style="color: #fbbf24;">Thermo</span>
                    </button>
                </div>
            </div>

            <!-- 2. Derivation Route Finder Card -->
            <div class="ug-card ug-route-card">
                <div class="ug-card-head">
                    <h2>Derivation Route Finder</h2>
                    <span class="ug-count-pill">Shortest Path</span>
                </div>

                <div class="ug-sample-routes">
                    <button type="button" class="ug-sample-btn" data-start="stationary-action-principle-8836edf7" data-end="pure-state-density-operator-217cc52a">
                        Action ➔ Density Matrix
                    </button>
                    <button type="button" class="ug-sample-btn" data-start="time-dependent-schrodinger-equation" data-end="dirac-equation">
                        Schrödinger ➔ Dirac
                    </button>
                </div>

                <div class="ug-route-inputs">
                    <div class="ug-input-group">
                        <label for="path-start-id">Start Formula</label>
                        <input type="text" id="path-start-id" class="ug-input ug-input-mono" value="stationary-action-principle-8836edf7" placeholder="Search title or ID..." autocomplete="off">
                        <div id="path-start-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                    </div>
                    <div class="ug-input-group">
                        <label for="path-end-id">Target Formula</label>
                        <input type="text" id="path-end-id" class="ug-input ug-input-mono" value="pure-state-density-operator-217cc52a" placeholder="Search title or ID..." autocomplete="off">
                        <div id="path-end-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                    </div>
                </div>

                <button type="button" id="btn-find-path" class="ug-trace-btn">
                    Trace Derivation Route ➔
                </button>

                <!-- Path Result Box -->
                <div id="path-result-box" class="ug-path-result" style="display: none;"></div>
            </div>
        </aside>

        <!-- Right Main Stage: Interactive DAG Canvas + Compact Domain Strip + Active Node Card -->
        <div class="ug-stage">
            <div id="universe-graph-canvas" class="ug-canvas-well">
                <!-- FormulaLineageGraph instance mounts here -->
            </div>

            <!-- Compact 12-Domain Color Legend Strip -->
            <div class="ug-domain-strip" aria-label="Physics Domain Color Legend">
                <span class="ug-legend-item"><span class="ug-dot" style="background: #c084fc;"></span>Theoretical</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #60a5fa;"></span>E&amp;M</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #f472b6;"></span>Astrophysics</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #e879f9;"></span>Philosophy</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #94a3b8;"></span>Classical</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #38bdf8;"></span>Relativity</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #f87171;"></span>Standard Model</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #34d399;"></span>Quantum</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #fbbf24;"></span>Thermo</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #818cf8;"></span>Math Methods</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #2dd4bf;"></span>Fluids</span>
                <span class="ug-legend-item"><span class="ug-dot" style="background: #a78bfa;"></span>Condensed</span>
            </div>

            <!-- Active Node Inspector Card -->
            <div id="active-node-card" class="ug-active-card">
                <div class="ug-active-main">
                    <div class="ug-active-meta">
                        <span id="active-card-domain" class="ug-domain-tag">Quantum Physics</span>
                        <span id="active-card-id" class="ug-formula-id">time-dependent-schrodinger-equation</span>
                    </div>
                    <h2 id="active-card-title" class="ug-active-title">
                        Time-Dependent Schrödinger Equation
                    </h2>
                    <div id="active-card-equation" class="ug-active-eq">
                        \(i\hbar \frac{\partial}{\partial t}\Psi(\mathbf{r}, t) = \hat{H}\Psi(\mathbf{r}, t)\)
                    </div>
                    <p id="active-card-summary" class="ug-active-summary">
                        The fundamental non-relativistic wave equation governing the unitary time evolution of quantum state vectors.
                    </p>
                </div>
                <div class="ug-active-actions">
                    <button type="button" id="btn-copy-graph-latex" class="ug-copy-btn" title="Copy formula LaTeX">Copy LaTeX</button>
                    <a id="btn-open-explainer" href="/physics/equation-explainer?id=time-dependent-schrodinger-equation" class="ug-explainer-cta">
                        <span>Open in Equation Explainer</span>
                        <span>➔</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="/js/formula_graph.js?v=<?= @filemtime(PROJECT_ROOT . '/public/js/formula_graph.js') ?: 1 ?>" nonce="<?= $nonce ?>" defer></script>
<script nonce="<?= $nonce ?>">
document.addEventListener('DOMContentLoaded', () => {
    const canvasContainer = document.getElementById('universe-graph-canvas');
    if (!canvasContainer || !window.FormulaLineageGraph) return;

    const hubBtns = document.querySelectorAll('.hub-btn');
    const depthBtns = document.querySelectorAll('.ug-depth-btn');
    const copyLatexBtn = document.getElementById('btn-copy-graph-latex');
    let currentFormulaId = 'time-dependent-schrodinger-equation';
    let currentEquationLatex = 'i\\hbar \\frac{\\partial}{\\partial t}\\Psi(\\mathbf{r}, t) = \\hat{H}\\Psi(\\mathbf{r}, t)';

    function typesetGraphMath(targets) {
        const list = (Array.isArray(targets) ? targets : [targets]).filter(Boolean);
        if (!list.length) return;
        if (window.MathJax && typeof window.MathJax.typesetPromise === 'function') {
            window.MathJax.typesetPromise(list).catch(() => {});
        } else if (typeof window.ensureMathJax === 'function') {
            window.ensureMathJax().then(mj => mj && mj.typesetPromise && mj.typesetPromise(list)).catch(() => {});
        }
    }

    function syncHubActiveState(activeId) {
        hubBtns.forEach(btn => {
            btn.classList.toggle('is-active', btn.getAttribute('data-id') === activeId);
        });
    }

    function updateActiveCard(node) {
        if (!node) return;
        currentFormulaId = node.id || currentFormulaId;
        currentEquationLatex = node.equation || '';
        document.getElementById('active-card-title').innerText = node.title || node.id;
        document.getElementById('active-card-domain').innerText = node.domain_label || node.domain || 'Physics';
        document.getElementById('active-card-id').innerText = node.id;
        document.getElementById('active-card-summary').innerText = node.summary || 'Click Open in Equation Explainer to inspect full variable definitions, CAS verification, and derivations.';
        document.getElementById('btn-open-explainer').href = `/physics/equation-explainer?id=${encodeURIComponent(node.id)}`;

        const eqBox = document.getElementById('active-card-equation');
        if (eqBox) {
            if (node.equation) {
                eqBox.style.display = 'inline-block';
                eqBox.textContent = `\\(${node.equation}\\)`;
                typesetGraphMath(eqBox);
            } else {
                eqBox.style.display = 'none';
            }
        }
        syncHubActiveState(node.id);
    }

    function loadAndSyncUrl(formulaId) {
        if (!formulaId) return;
        currentFormulaId = formulaId;
        universeGraph.loadFormula(formulaId);
        const url = new URL(window.location);
        url.searchParams.set('id', formulaId);
        window.history.replaceState({}, '', url);
    }

    const universeGraph = new window.FormulaLineageGraph('universe-graph-canvas', {
        depth: 2,
        onNodeClick: (node) => {
            updateActiveCard(node);
            loadAndSyncUrl(node.id);
        },
        onRootLoaded: (node) => {
            updateActiveCard(node);
        }
    });

    // Header Depth Switcher (1 | 2 | 3)
    depthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const d = parseInt(btn.getAttribute('data-depth'), 10) || 2;
            depthBtns.forEach(b => b.classList.toggle('active', b === btn));
            universeGraph.options.depth = d;
            const innerSelect = canvasContainer.querySelector('#graph-depth-select');
            if (innerSelect) innerSelect.value = String(d);
            universeGraph.loadFormula(currentFormulaId);
        });
    });

    // Fullscreen button
    const fsBtn = document.getElementById('btn-universe-fullscreen');
    if (fsBtn) {
        fsBtn.addEventListener('click', () => {
            universeGraph.toggleFullscreen(true);
        });
    }

    // Copy Active Formula LaTeX
    if (copyLatexBtn) {
        copyLatexBtn.addEventListener('click', () => {
            if (!currentEquationLatex || !navigator.clipboard) return;
            navigator.clipboard.writeText(currentEquationLatex).then(() => {
                copyLatexBtn.textContent = 'Copied ✓';
                copyLatexBtn.classList.add('is-copied');
                setTimeout(() => {
                    copyLatexBtn.textContent = 'Copy LaTeX';
                    copyLatexBtn.classList.remove('is-copied');
                }, 1400);
            }).catch(() => {});
        });
    }

    // Hub selection
    hubBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const fid = btn.getAttribute('data-id');
            if (fid) loadAndSyncUrl(fid);
        });
    });

    // Reusable Autocomplete Binder for Search & Route Finder Inputs
    function bindFormulaAutocomplete(inputEl, dropdownEl, onSelect) {
        if (!inputEl || !dropdownEl) return;
        let timer = null;

        inputEl.addEventListener('input', () => {
            clearTimeout(timer);
            const q = inputEl.value.trim();
            if (q.length < 2) {
                dropdownEl.style.display = 'none';
                return;
            }
            timer = setTimeout(async () => {
                try {
                    const res = await fetch(`/physics/api/search?q=${encodeURIComponent(q)}&limit=6`);
                    if (!res.ok) throw new Error(`HTTP ${res.status}`);
                    const data = await res.json();
                    const items = (data.results || []).filter(r => r.type === 'formula' && r.id);
                    if (items.length === 0) {
                        dropdownEl.style.display = 'none';
                        return;
                    }
                    const escapeHtml = (s) => String(s ?? '')
                        .replace(/&/g, '&amp;')
                        .replace(/</g, '&lt;')
                        .replace(/>/g, '&gt;')
                        .replace(/"/g, '&quot;')
                        .replace(/'/g, '&#39;');
                    dropdownEl.innerHTML = items.map(item => `
                        <div class="graph-ac-item" data-id="${encodeURIComponent(item.id)}" data-title="${encodeURIComponent(item.title || item.id)}">
                            <div class="graph-ac-title">${escapeHtml(item.title || item.id)}</div>
                            ${item.equation ? `<div class="graph-ac-eq">\\(${escapeHtml(item.equation)}\\)</div>` : ''}
                        </div>
                    `).join('');
                    dropdownEl.style.display = 'block';
                    dropdownEl.querySelectorAll('.graph-ac-item').forEach(el => {
                        el.addEventListener('click', () => {
                            const id = decodeURIComponent(el.getAttribute('data-id'));
                            const title = decodeURIComponent(el.getAttribute('data-title'));
                            dropdownEl.style.display = 'none';
                            onSelect(id, title);
                        });
                    });
                    typesetGraphMath(dropdownEl);
                } catch (e) {
                    dropdownEl.style.display = 'none';
                }
            }, 220);
        });

        document.addEventListener('click', (e) => {
            if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
                dropdownEl.style.display = 'none';
            }
        });
    }

    // Bind Top Sidebar Search
    const searchInput = document.getElementById('graph-search-input');
    const searchDropdown = document.getElementById('graph-search-dropdown');
    bindFormulaAutocomplete(searchInput, searchDropdown, (id, title) => {
        searchInput.value = title;
        loadAndSyncUrl(id);
    });

    // Bind Route Finder Autocomplete
    const startInput = document.getElementById('path-start-id');
    const startDropdown = document.getElementById('path-start-dropdown');
    bindFormulaAutocomplete(startInput, startDropdown, (id) => {
        startInput.value = id;
    });

    const endInput = document.getElementById('path-end-id');
    const endDropdown = document.getElementById('path-end-dropdown');
    bindFormulaAutocomplete(endInput, endDropdown, (id) => {
        endInput.value = id;
    });

    // Path Finder Execution
    const btnFindPath = document.getElementById('btn-find-path');
    const resultBox = document.getElementById('path-result-box');

    async function runPathSearch() {
        const start = startInput.value.trim();
        const end = endInput.value.trim();
        if (!start || !end || !resultBox) return;

        resultBox.style.display = 'block';
        resultBox.innerHTML = '<span style="color: #64ffda;">Calculating derivation path...</span>';

        try {
            const resp = await fetch(`/physics/api/formula-path?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const res = await resp.json();

            if (res.success && res.data && res.data.found) {
                const modeLabel = res.data.mode === 'bridge' ? 'Shared Axiom Bridge' : 'Direct Derivation Chain';
                let html = `<div style="color: #64ffda; font-weight: 700; margin-bottom: 6px;">✓ ${modeLabel} (${res.data.hops} Steps):</div>`;
                html += `<ol style="margin: 0; padding-left: 18px; color: #cbd5e1; line-height: 1.65;">`;
                const esc = (s) => String(s ?? '')
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
                res.data.path_nodes.forEach(pn => {
                    html += `
                        <li style="margin-bottom: 4px;">
                            <button type="button" class="path-node-focus-btn" data-id="${esc(pn.id)}" title="Center graph on this formula">
                                ${esc(pn.title || pn.id)}
                            </button>
                            <a href="/physics/equation-explainer?id=${encodeURIComponent(pn.id)}" title="Open in Equation Explainer" style="color: #94a3b8; text-decoration: none; font-size: 0.72rem; margin-left: 4px;">↗</a>
                        </li>`;
                });
                html += `</ol>`;
                resultBox.innerHTML = html;

                resultBox.querySelectorAll('.path-node-focus-btn').forEach(b => {
                    b.addEventListener('click', () => {
                        loadAndSyncUrl(b.getAttribute('data-id'));
                    });
                });
            } else {
                const escMsg = String(res.data?.message || 'No derivation path found.')
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;');
                resultBox.innerHTML = `<span style="color: #f87171;">${escMsg}</span>`;
            }
        } catch (e) {
            resultBox.innerHTML = '<span style="color: #f87171;">Route search error.</span>';
        }
    }

    if (btnFindPath) {
        btnFindPath.addEventListener('click', runPathSearch);
    }

    // One-click sample route presets
    document.querySelectorAll('.ug-sample-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            startInput.value = btn.getAttribute('data-start') || '';
            endInput.value = btn.getAttribute('data-end') || '';
            runPathSearch();
        });
    });

    // Initial load: check ?id= query param or default to Time-Dependent Schrödinger Equation
    const urlParams = new URLSearchParams(window.location.search);
    const initialId = urlParams.get('id') || 'time-dependent-schrodinger-equation';
    currentFormulaId = initialId;
    universeGraph.loadFormula(initialId);
});
</script>

<style>
.universe-graph-container {
    max-width: 1320px;
    margin: 0 auto;
    padding: 6px 0 48px 0;
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Compact Command Header */
.ug-header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px 20px;
    padding: 4px 0 12px 0;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.ug-header-left {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.ug-header h1 {
    margin: 0;
    font-size: 1.65rem;
    line-height: 1.15;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffffff 40%, var(--accent-default, #64ffda) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.ug-tagline {
    margin: 0;
    color: var(--text-muted, #94a3b8);
    font-size: 0.88rem;
    line-height: 1.4;
}

.ug-header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.ug-depth-group {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 3px 6px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
}

.ug-depth-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted, #94a3b8);
    padding: 0 5px;
}

.ug-depth-btn {
    background: transparent;
    border: 1px solid transparent;
    color: #cbd5e1;
    width: 24px;
    height: 24px;
    border-radius: 6px;
    font-size: 0.76rem;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.15s ease;
}

.ug-depth-btn:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

.ug-depth-btn.active {
    background: rgba(100, 255, 218, 0.18);
    border-color: rgba(100, 255, 218, 0.45);
    color: #64ffda;
}

.ug-action-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 12px;
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #cbd5e1;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s ease;
}

.ug-action-btn:hover {
    background: rgba(255, 255, 255, 0.09);
    color: #ffffff;
}

.ug-action-primary {
    background: rgba(100, 255, 218, 0.13);
    border-color: rgba(100, 255, 218, 0.45);
    color: #64ffda;
    font-weight: 700;
}

/* Split-Rail Workspace Grid */
.universe-workspace-grid {
    display: grid;
    grid-template-columns: 295px minmax(0, 1fr);
    gap: 18px;
    align-items: start;
}

.ug-rail {
    display: flex;
    flex-direction: column;
    gap: 14px;
    position: sticky;
    top: 84px;
    min-width: 0;
}

.ug-stage {
    display: flex;
    flex-direction: column;
    gap: 12px;
    min-width: 0;
}

.ug-card {
    background: rgba(15, 23, 42, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 14px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}

.ug-route-card {
    border-color: rgba(100, 255, 218, 0.2);
}

.ug-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 10px;
    padding-bottom: 7px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.ug-card-head h2 {
    margin: 0;
    font-size: 0.9rem;
    color: #ffffff;
    font-weight: 700;
}

.ug-count-pill {
    font-size: 0.66rem;
    font-weight: 600;
    color: var(--accent-default, #64ffda);
    background: rgba(100, 255, 218, 0.1);
    border: 1px solid rgba(100, 255, 218, 0.25);
    padding: 2px 7px;
    border-radius: 10px;
    white-space: nowrap;
}

.ug-search-wrap {
    position: relative;
    margin-bottom: 12px;
}

.ug-input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(2, 6, 23, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 8px;
    padding: 7px 10px;
    color: #ffffff;
    font-size: 0.8rem;
    font-family: inherit;
    outline: none;
    transition: border-color 0.2s;
}

.ug-input:focus {
    border-color: var(--accent-default, #64ffda);
}

.ug-input-mono {
    font-family: 'Space Grotesk', monospace;
    font-size: 0.74rem;
    padding: 6px 9px;
}

.ug-sub-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-muted, #94a3b8);
    margin-bottom: 7px;
}

.ug-hubs-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.hub-btn {
    text-align: left;
    background: rgba(2, 6, 23, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 7px;
    padding: 7px 10px;
    color: #f1f5f9;
    font-size: 0.79rem;
    font-family: inherit;
    cursor: pointer;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    transition: all 0.2s ease;
}

.hub-domain {
    font-size: 0.68rem;
    font-weight: 600;
    white-space: nowrap;
}

.hub-btn:hover,
.hub-btn.is-active {
    background: rgba(100, 255, 218, 0.1);
    border-color: rgba(100, 255, 218, 0.38);
    transform: translateX(3px);
}

/* Route Finder Controls */
.ug-sample-routes {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 10px;
}

.ug-sample-btn {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #cbd5e1;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.15s ease;
}

.ug-sample-btn:hover {
    background: rgba(100, 255, 218, 0.14);
    border-color: rgba(100, 255, 218, 0.4);
    color: #64ffda;
}

.ug-route-inputs {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 10px;
}

.ug-input-group {
    position: relative;
}

.ug-input-group label {
    font-size: 0.66rem;
    text-transform: uppercase;
    color: #cbd5e1;
    font-weight: 600;
    display: block;
    margin-bottom: 3px;
}

.ug-trace-btn {
    width: 100%;
    background: linear-gradient(135deg, rgba(100, 255, 218, 0.18) 0%, rgba(56, 189, 248, 0.18) 100%);
    border: 1px solid rgba(100, 255, 218, 0.4);
    color: #64ffda;
    border-radius: 7px;
    padding: 8px 12px;
    font-size: 0.78rem;
    font-weight: 700;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s ease;
}

.ug-trace-btn:hover {
    background: linear-gradient(135deg, rgba(100, 255, 218, 0.28) 0%, rgba(56, 189, 248, 0.28) 100%);
    color: #ffffff;
}

.ug-path-result {
    margin-top: 10px;
    padding: 10px 11px;
    background: rgba(2, 6, 23, 0.85);
    border: 1px solid rgba(100, 255, 218, 0.22);
    border-radius: 8px;
    font-size: 0.76rem;
}

/* Main Graph Well & Compact Domain Strip */
.ug-canvas-well {
    height: 600px;
    width: 100%;
    position: relative;
}

.ug-domain-strip {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px 14px;
    padding: 8px 14px;
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 10px;
}

.ug-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.72rem;
    color: #cbd5e1;
}

.ug-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}

/* Active Node Inspector Card */
.ug-active-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(100, 255, 218, 0.22);
    border-left: 3px solid var(--accent-default, #64ffda);
    border-radius: 12px;
    padding: 16px 18px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 14px;
}

.ug-active-main {
    flex: 1;
    min-width: 260px;
}

.ug-active-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
    flex-wrap: wrap;
}

.ug-domain-tag {
    font-size: 0.7rem;
    text-transform: uppercase;
    color: var(--accent-default, #64ffda);
    font-weight: 700;
    letter-spacing: 0.06em;
}

.ug-formula-id {
    font-size: 0.7rem;
    color: #64748b;
    font-family: monospace;
}

.ug-active-title {
    margin: 0 0 8px 0;
    font-size: 1.15rem;
    color: #ffffff;
    font-weight: 700;
}

.ug-active-eq {
    margin: 0 0 8px 0;
    padding: 8px 12px;
    background: rgba(2, 6, 23, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    color: #ffd700;
    font-size: 1.02rem;
    overflow-x: auto;
    display: inline-block;
    max-width: 100%;
}

.ug-active-summary {
    margin: 0;
    color: #94a3b8;
    font-size: 0.84rem;
    line-height: 1.45;
}

.ug-active-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.ug-copy-btn {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    color: #cbd5e1;
    padding: 9px 12px;
    border-radius: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    white-space: nowrap;
    transition: all 0.15s ease;
}

.ug-copy-btn:hover {
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
}

.ug-copy-btn.is-copied {
    border-color: #34d399;
    color: #34d399;
    background: rgba(16, 185, 129, 0.15);
}

.ug-explainer-cta {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 9px 16px;
    background: var(--accent-default, #64ffda);
    color: #020c1b;
    font-weight: 700;
    border-radius: 8px;
    text-decoration: none;
    font-size: 0.82rem;
    white-space: nowrap;
    transition: all 0.2s ease;
}

.ug-explainer-cta:hover {
    filter: brightness(1.08);
}

/* Autocomplete Dropdown */
.graph-autocomplete-menu {
    position: absolute;
    z-index: 100;
    left: 0;
    right: 0;
    top: calc(100% + 4px);
    background: rgba(15, 23, 42, 0.98);
    border: 1px solid rgba(100, 255, 218, 0.3);
    border-radius: 8px;
    max-height: 260px;
    overflow-y: auto;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.7);
}

.graph-ac-item {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    cursor: pointer;
    transition: background 0.15s;
}

.graph-ac-item:hover {
    background: rgba(100, 255, 218, 0.12);
}

.graph-ac-title {
    font-size: 0.78rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 2px;
}

.graph-ac-eq {
    font-size: 0.74rem;
    color: #ffd700;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.path-node-focus-btn {
    background: none;
    border: none;
    padding: 0;
    color: #38bdf8;
    font-family: inherit;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    text-align: left;
}

.path-node-focus-btn:hover {
    color: #64ffda;
    text-decoration: underline;
}

@media (max-width: 960px) {
    .universe-workspace-grid {
        grid-template-columns: 1fr;
    }
    .ug-rail {
        position: static;
    }
}
</style>
