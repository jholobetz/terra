<div class="universe-graph-container" style="max-width: 1400px; margin: 0 auto; padding: 24px 20px; font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;">

    <!-- Page Header -->
    <div style="margin-bottom: 22px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap;">
                <span style="font-size: 1.5rem;">🌌</span>
                <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">
                    Physics Universe Knowledge Graph
                </h1>
                <span style="font-size: 0.72rem; padding: 3px 10px; background: rgba(100, 255, 218, 0.1); color: var(--accent-default, #64ffda); border: 1px solid rgba(100, 255, 218, 0.3); border-radius: 12px; font-weight: 600;">
                    14,681 Formulas • 14,108 Derivation Links
                </span>
            </div>
            <p style="margin: 0; color: var(--text-muted, #94a3b8); font-size: 0.95rem; line-height: 1.5;">
                Explore the complete mathematical lineage, upstream axiomatic foundations, and downstream derived consequences across all 12 branches of theoretical physics.
            </p>
        </div>

        <!-- Quick Actions -->
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <button type="button" id="btn-universe-fullscreen" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: rgba(100, 255, 218, 0.14); border: 1px solid rgba(100, 255, 218, 0.45); color: #64ffda; border-radius: 8px; font-size: 0.82rem; font-weight: 700; font-family: 'Space Grotesk', sans-serif; cursor: pointer; transition: all 0.2s;">
                <span>⛶ Full Screen Map</span>
            </button>
            <a href="/physics/equation-explainer" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(100, 255, 218, 0.25); color: #cbd5e1; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: all 0.2s;">
                <span>🔬 Equation Explainer</span>
            </a>
        </div>
    </div>

    <!-- Main Workspace Grid -->
    <div class="universe-workspace-grid">

        <!-- Left Sidebar: Search, Landmark Hubs & Route Finder -->
        <div style="display: flex; flex-direction: column; gap: 16px;">

            <!-- 1. Formula Search Bar -->
            <div style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(100, 255, 218, 0.22); border-radius: 12px; padding: 16px; backdrop-filter: blur(10px); position: relative;">
                <label for="graph-search-input" style="font-size: 0.78rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 8px 0; letter-spacing: 0.08em; font-weight: 700; display: block;">
                    🔍 Find &amp; Center Formula
                </label>
                <div style="position: relative;">
                    <input type="text"
                           id="graph-search-input"
                           placeholder="Search 'Schrödinger', 'Lorentz', 'Carnot'..."
                           autocomplete="off"
                           style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.85); border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 8px; padding: 8px 12px; color: #ffffff; font-size: 0.82rem; font-family: 'Space Grotesk', sans-serif; outline: none; transition: border-color 0.2s;" />
                    <div id="graph-search-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                </div>
            </div>

            <!-- 2. Landmark Formula Quick Selector -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 18px; backdrop-filter: blur(10px);">
                <h3 style="font-size: 0.82rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 12px 0; letter-spacing: 0.08em; font-weight: 700;">
                    ⭐ Landmark Physics Hubs
                </h3>
                <div style="display: flex; flex-direction: column; gap: 6px;" id="landmark-hubs-list">
                    <button class="hub-btn is-active" data-id="time-dependent-schrodinger-equation" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Schrödinger Wave Equation</span>
                        <span style="font-size: 0.7rem; color: #34d399;">Quantum</span>
                    </button>
                    <button class="hub-btn" data-id="lorentz-factor-exact" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Exact Lorentz Factor (γ)</span>
                        <span style="font-size: 0.7rem; color: #38bdf8;">Relativity</span>
                    </button>
                    <button class="hub-btn" data-id="amp-re-maxwell-identity-bf5142b0" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Ampère–Maxwell Law</span>
                        <span style="font-size: 0.7rem; color: #60a5fa;">Electrodynamics</span>
                    </button>
                    <button class="hub-btn" data-id="dirac-equation" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Dirac Relativistic Equation</span>
                        <span style="font-size: 0.7rem; color: #c084fc;">QFT</span>
                    </button>
                    <button class="hub-btn" data-id="navier-stokes-momentum-fluids-27e5bf4d" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Navier–Stokes Equations</span>
                        <span style="font-size: 0.7rem; color: #2dd4bf;">Fluids</span>
                    </button>
                    <button class="hub-btn" data-id="gibbs-entropy-formula-fb0b23b8" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Gibbs Entropy Formula</span>
                        <span style="font-size: 0.7rem; color: #fbbf24;">Thermodynamics</span>
                    </button>
                </div>
            </div>

            <!-- 3. Mathematical Path Finder Tool -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 12px; padding: 18px; backdrop-filter: blur(10px);">
                <h3 style="font-size: 0.82rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 8px 0; letter-spacing: 0.08em; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                    🧭 Derivation Route Finder
                </h3>
                <p style="font-size: 0.75rem; color: #94a3b8; margin: 0 0 12px 0; line-height: 1.4;">
                    Trace the shortest derivation path between two formulas (search by name or ID):
                </p>
                
                <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;">
                    <div style="position: relative;">
                        <label for="path-start-id" style="font-size: 0.68rem; text-transform: uppercase; color: #cbd5e1; font-weight: 600; display: block; margin-bottom: 3px;">Start Formula</label>
                        <input type="text" id="path-start-id" value="stationary-action-principle-8836edf7" placeholder="Search title or ID..." autocomplete="off" style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 6px 10px; color: #ffffff; font-size: 0.76rem; font-family: 'Space Grotesk', monospace; outline: none;">
                        <div id="path-start-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                    </div>
                    <div style="position: relative;">
                        <label for="path-end-id" style="font-size: 0.68rem; text-transform: uppercase; color: #cbd5e1; font-weight: 600; display: block; margin-bottom: 3px;">Target Formula</label>
                        <input type="text" id="path-end-id" value="pure-state-density-operator-217cc52a" placeholder="Search title or ID..." autocomplete="off" style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 6px 10px; color: #ffffff; font-size: 0.76rem; font-family: 'Space Grotesk', monospace; outline: none;">
                        <div id="path-end-dropdown" class="graph-autocomplete-menu" style="display: none;"></div>
                    </div>
                </div>

                <button id="btn-find-path" style="width: 100%; background: linear-gradient(135deg, rgba(100,255,218,0.2) 0%, rgba(56,189,248,0.2) 100%); border: 1px solid rgba(100,255,218,0.4); color: #64ffda; border-radius: 6px; padding: 8px 12px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s;">
                    Trace Derivation Route ➔
                </button>

                <!-- Path Result Box -->
                <div id="path-result-box" style="display: none; margin-top: 12px; padding: 10px 12px; background: rgba(3,7,18,0.85); border: 1px solid rgba(100,255,218,0.2); border-radius: 8px; font-size: 0.78rem;">
                    <!-- JS populated -->
                </div>
            </div>

            <!-- 4. Domain Color Legend -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
                <h4 style="font-size: 0.74rem; text-transform: uppercase; color: #94a3b8; margin: 0 0 10px 0; font-weight: 700;">Physics Domains</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.72rem;">
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #c084fc;"></span> Theoretical</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #60a5fa;"></span> E&amp;M</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #f472b6;"></span> Astrophysics</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #e879f9;"></span> Philosophy</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #94a3b8;"></span> Classical</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #38bdf8;"></span> Relativity</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #f87171;"></span> Standard Model</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #34d399;"></span> Quantum</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #fbbf24;"></span> Thermo</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #818cf8;"></span> Math Methods</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #2dd4bf;"></span> Fluids</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #a78bfa;"></span> Condensed</span>
                </div>
            </div>
        </div>

        <!-- Right Main Canvas: Interactive DAG Visualizer -->
        <div style="display: flex; flex-direction: column; gap: 16px; min-width: 0;">
            <div id="universe-graph-canvas" style="height: 650px; width: 100%; position: relative;">
                <!-- FormulaLineageGraph instance will mount here -->
            </div>

            <!-- Active Node Preview Card -->
            <div id="active-node-card" style="background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(100, 255, 218, 0.22); border-radius: 12px; padding: 18px 20px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="flex: 1; min-width: 260px;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap;">
                        <span id="active-card-domain" style="font-size: 0.72rem; text-transform: uppercase; color: var(--accent-default, #64ffda); font-weight: 700; letter-spacing: 0.06em;">Quantum Physics</span>
                        <span id="active-card-id" style="font-size: 0.7rem; color: #64748b; font-family: monospace;">time-dependent-schrodinger-equation</span>
                    </div>
                    <h2 id="active-card-title" style="margin: 0 0 8px 0; font-size: 1.2rem; color: #ffffff; font-weight: 700;">
                        Time-Dependent Schrödinger Equation
                    </h2>
                    <div id="active-card-equation" style="margin: 0 0 8px 0; padding: 8px 12px; background: rgba(2, 6, 23, 0.7); border: 1px solid rgba(255, 255, 255, 0.07); border-radius: 8px; color: #ffd700; font-size: 1.05rem; overflow-x: auto; display: inline-block; max-width: 100%;">
                        \(i\hbar \frac{\partial}{\partial t}\Psi(\mathbf{r}, t) = \hat{H}\Psi(\mathbf{r}, t)\)
                    </div>
                    <p id="active-card-summary" style="margin: 0; color: #94a3b8; font-size: 0.85rem; line-height: 1.45;">
                        The fundamental non-relativistic wave equation governing the unitary time evolution of quantum state vectors.
                    </p>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <a id="btn-open-explainer" href="/physics/equation-explainer?id=time-dependent-schrodinger-equation" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; background: var(--accent-default, #64ffda); color: #020c1b; font-weight: 700; border-radius: 8px; text-decoration: none; font-size: 0.84rem; transition: all 0.2s; white-space: nowrap;">
                        <span>Open in Equation Explainer</span>
                        <span>➔</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="/js/formula_graph.js?v=<?= filemtime(PROJECT_ROOT . '/public/js/formula_graph.js') ?>" nonce="<?= $nonce ?>" defer></script>
<script nonce="<?= $nonce ?>">
document.addEventListener('DOMContentLoaded', () => {
    const canvasContainer = document.getElementById('universe-graph-canvas');
    if (!canvasContainer || !window.FormulaLineageGraph) return;

    const hubBtns = document.querySelectorAll('.hub-btn');

    function syncHubActiveState(activeId) {
        hubBtns.forEach(btn => {
            if (btn.getAttribute('data-id') === activeId) {
                btn.classList.add('is-active');
            } else {
                btn.classList.remove('is-active');
            }
        });
    }

    function updateActiveCard(node) {
        if (!node) return;
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
                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise([eqBox]).catch(() => {});
                }
            } else {
                eqBox.style.display = 'none';
            }
        }
        syncHubActiveState(node.id);
    }

    function loadAndSyncUrl(formulaId) {
        if (!formulaId) return;
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

    const fsBtn = document.getElementById('btn-universe-fullscreen');
    if (fsBtn) {
        fsBtn.addEventListener('click', () => {
            universeGraph.toggleFullscreen(true);
        });
    }

    // Hub selection
    hubBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const fid = btn.getAttribute('data-id');
            if (fid) {
                loadAndSyncUrl(fid);
            }
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
                    const data = await res.json();
                    const items = (data.results || []).filter(r => r.type === 'formula' && r.id);
                    if (items.length === 0) {
                        dropdownEl.style.display = 'none';
                        return;
                    }
                    dropdownEl.innerHTML = items.map(item => `
                        <div class="graph-ac-item" data-id="${encodeURIComponent(item.id)}" data-title="${encodeURIComponent(item.title || item.id)}">
                            <div class="graph-ac-title">${item.title || item.id}</div>
                            ${item.equation ? `<div class="graph-ac-eq">\\(${item.equation}\\)</div>` : ''}
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
                    if (window.MathJax && window.MathJax.typesetPromise) {
                        window.MathJax.typesetPromise([dropdownEl]).catch(() => {});
                    }
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

    if (btnFindPath && resultBox) {
        btnFindPath.addEventListener('click', async () => {
            const start = startInput.value.trim();
            const end = endInput.value.trim();
            if (!start || !end) return;

            resultBox.style.display = 'block';
            resultBox.innerHTML = '<span style="color: #64ffda;">Calculating derivation path...</span>';

            try {
                const resp = await fetch(`/physics/api/formula-path?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
                const res = await resp.json();

                if (res.success && res.data && res.data.found) {
                    const modeLabel = res.data.mode === 'bridge' ? 'Shared Axiom Bridge' : 'Direct Derivation Chain';
                    let html = `<div style="color: #64ffda; font-weight: 700; margin-bottom: 6px;">✓ ${modeLabel} (${res.data.hops} Steps):</div>`;
                    html += `<ol style="margin: 0; padding-left: 18px; color: #cbd5e1; line-height: 1.65;">`;
                    res.data.path_nodes.forEach(pn => {
                        html += `
                            <li style="margin-bottom: 4px;">
                                <button type="button" class="path-node-focus-btn" data-id="${pn.id}" title="Center graph on this formula">
                                    ${pn.title || pn.id}
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
                    resultBox.innerHTML = `<span style="color: #f87171;">${res.data?.message || 'No derivation path found.'}</span>`;
                }
            } catch (e) {
                resultBox.innerHTML = '<span style="color: #f87171;">Route search error.</span>';
            }
        });
    }

    // Initial load: check ?id= query param or default to Time-Dependent Schrödinger Equation
    const urlParams = new URLSearchParams(window.location.search);
    const initialId = urlParams.get('id') || 'time-dependent-schrodinger-equation';
    universeGraph.loadFormula(initialId);
});
</script>

<style>
.universe-workspace-grid {
    display: grid;
    grid-template-columns: 320px minmax(0, 1fr);
    gap: 20px;
    min-height: 680px;
}

@media (max-width: 960px) {
    .universe-workspace-grid {
        grid-template-columns: 1fr;
    }
}

.hub-btn:hover,
.hub-btn.is-active {
    background: rgba(100, 255, 218, 0.1) !important;
    border-color: rgba(100, 255, 218, 0.38) !important;
    transform: translateX(3px);
}

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
</style>
