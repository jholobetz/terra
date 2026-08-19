<div class="universe-graph-container" style="max-width: 1400px; margin: 0 auto; padding: 24px 20px; font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;">

    <!-- Page Header -->
    <div style="margin-bottom: 24px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
        <div>
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                <span style="font-size: 1.5rem;">🌌</span>
                <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; color: #ffffff; letter-spacing: -0.02em;">
                    Physics Universe Knowledge Graph
                </h1>
                <span style="font-size: 0.72rem; padding: 3px 8px; background: rgba(100, 255, 218, 0.1); color: var(--accent-default, #64ffda); border: 1px solid rgba(100, 255, 218, 0.3); border-radius: 12px; font-weight: 600;">
                    13,773 Formulas • 21,540 Links
                </span>
            </div>
            <p style="margin: 0; color: var(--text-muted, #94a3b8); font-size: 0.95rem; max-width: 800px; line-height: 1.5;">
                Explore the complete mathematical lineage, asymptotic reductions, and structural derivations across all 12 branches of theoretical physics.
            </p>
        </div>

        <!-- Quick Actions & Path Finder Trigger -->
        <div style="display: flex; align-items: center; gap: 10px;">
            <a href="/physics/equation-explainer" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(100, 255, 218, 0.25); color: #cbd5e1; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: all 0.2s;">
                <span>🧮 Equation Explainer</span>
            </a>
            <a href="/physics/noethers-vault" style="display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(100, 255, 218, 0.25); color: #cbd5e1; border-radius: 8px; text-decoration: none; font-size: 0.82rem; font-weight: 600; transition: all 0.2s;">
                <span>🏛️ Noether's Vault</span>
            </a>
        </div>
    </div>

    <!-- Main Workspace Grid -->
    <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px; min-height: 680px;">

        <!-- Left Sidebar: Controls & Path Finder -->
        <div style="display: flex; flex-direction: column; gap: 16px;">

            <!-- Landmark Formula Quick Selector -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 18px; backdrop-filter: blur(10px);">
                <h3 style="font-size: 0.82rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 12px 0; letter-spacing: 0.08em; font-weight: 700;">
                    ⭐ Landmark Physics Hubs
                </h3>
                <div style="display: flex; flex-direction: column; gap: 6px;" id="landmark-hubs-list">
                    <button class="hub-btn" data-id="einstein-hilbert-action-principle-54934f1b" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Einstein-Hilbert Action</span>
                        <span style="font-size: 0.7rem; color: #38bdf8;">Relativity</span>
                    </button>
                    <button class="hub-btn" data-id="dirac-equation" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Dirac Relativistic Equation</span>
                        <span style="font-size: 0.7rem; color: #c084fc;">QFT</span>
                    </button>
                    <button class="hub-btn" data-id="maxwell-stress-tensor-divergence-lorentz-force-e83788ff" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Maxwell Stress Tensor</span>
                        <span style="font-size: 0.7rem; color: #60a5fa;">Electrodynamics</span>
                    </button>
                    <button class="hub-btn" data-id="time-dependent-schrodinger-equation" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Schrödinger Wave Equation</span>
                        <span style="font-size: 0.7rem; color: #34d399;">Quantum</span>
                    </button>
                    <button class="hub-btn" data-id="navier-stokes-momentum-fluids-27e5bf4d" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Navier-Stokes Equations</span>
                        <span style="font-size: 0.7rem; color: #2dd4bf;">Fluids</span>
                    </button>
                    <button class="hub-btn" data-id="boltzmann-factor-a2f1f3cf" style="text-align: left; background: rgba(3, 7, 18, 0.6); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; padding: 8px 10px; color: #f1f5f9; font-size: 0.82rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: all 0.2s;">
                        <span>Boltzmann Factor</span>
                        <span style="font-size: 0.7rem; color: #fbbf24;">Thermodynamics</span>
                    </button>
                </div>
            </div>

            <!-- Mathematical Path Finder Tool -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 12px; padding: 18px; backdrop-filter: blur(10px);">
                <h3 style="font-size: 0.82rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0 0 10px 0; letter-spacing: 0.08em; font-weight: 700; display: flex; align-items: center; gap: 6px;">
                    🧭 Derivation Route Finder
                </h3>
                <p style="font-size: 0.76rem; color: #94a3b8; margin: 0 0 12px 0;">Find the shortest mathematical derivation path connecting two physics laws:</p>
                
                <div style="display: flex; flex-direction: column; gap: 8px; margin-bottom: 12px;">
                    <div>
                        <label style="font-size: 0.7rem; text-transform: uppercase; color: #cbd5e1; font-weight: 600; display: block; margin-bottom: 3px;">Start Equation ID</label>
                        <input type="text" id="path-start-id" value="euler-lagrange-link-97f66630" placeholder="e.g. euler-lagrange-link..." style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 6px 10px; color: #ffffff; font-size: 0.76rem; font-family: monospace; outline: none;">
                    </div>
                    <div>
                        <label style="font-size: 0.7rem; text-transform: uppercase; color: #cbd5e1; font-weight: 600; display: block; margin-bottom: 3px;">Target Equation ID</label>
                        <input type="text" id="path-end-id" value="einstein-hilbert-action-principle-54934f1b" placeholder="e.g. einstein-hilbert..." style="width: 100%; box-sizing: border-box; background: rgba(3, 7, 18, 0.8); border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; padding: 6px 10px; color: #ffffff; font-size: 0.76rem; font-family: monospace; outline: none;">
                    </div>
                </div>

                <button id="btn-find-path" style="width: 100%; background: linear-gradient(135deg, rgba(100,255,218,0.2) 0%, rgba(56,189,248,0.2) 100%); border: 1px solid rgba(100,255,218,0.4); color: #64ffda; border-radius: 6px; padding: 7px 12px; font-size: 0.8rem; font-weight: 700; cursor: pointer; transition: all 0.2s;">
                    Trace Derivation Route ➔
                </button>

                <!-- Path Result Box -->
                <div id="path-result-box" style="display: none; margin-top: 12px; padding: 10px; background: rgba(3,7,18,0.85); border: 1px solid rgba(100,255,218,0.2); border-radius: 8px; font-size: 0.78rem;">
                    <!-- JS populated -->
                </div>
            </div>

            <!-- Domain Color Legend -->
            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 16px;">
                <h4 style="font-size: 0.74rem; text-transform: uppercase; color: #94a3b8; margin: 0 0 10px 0; font-weight: 700;">Physics Domains</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; font-size: 0.72rem;">
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #38bdf8;"></span> Relativity</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #34d399;"></span> Quantum</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #c084fc;"></span> QFT &amp; Fields</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #fbbf24;"></span> Thermo</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #60a5fa;"></span> E&amp;M</span>
                    <span style="display: flex; align-items: center; gap: 5px; color: #cbd5e1;"><span style="width: 8px; height: 8px; border-radius: 50%; background: #2dd4bf;"></span> Fluids</span>
                </div>
            </div>
        </div>

        <!-- Right Main Canvas: Interactive DAG Visualizer -->
        <div style="display: flex; flex-direction: column; gap: 16px;">
            <div id="universe-graph-canvas" style="height: 650px; width: 100%; position: relative;">
                <!-- FormulaLineageGraph instance will mount here -->
            </div>

            <!-- Active Node Preview Card -->
            <div id="active-node-card" style="background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 12px; padding: 18px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        <span id="active-card-domain" style="font-size: 0.72rem; text-transform: uppercase; color: var(--accent-default, #64ffda); font-weight: 700; letter-spacing: 0.06em;">General Relativity</span>
                        <span id="active-card-id" style="font-size: 0.7rem; color: #64748b; font-family: monospace;">einstein-hilbert-action-principle-54934f1b</span>
                    </div>
                    <h2 id="active-card-title" style="margin: 0 0 6px 0; font-size: 1.15rem; color: #ffffff; font-weight: 600;">
                        Einstein-Hilbert Action Principle
                    </h2>
                    <p id="active-card-summary" style="margin: 0; color: #94a3b8; font-size: 0.84rem; max-width: 750px;">
                        The foundational variational principle yielding the Einstein field equations of spacetime curvature.
                    </p>
                </div>
                <div>
                    <a id="btn-open-explainer" href="/physics/equation-explainer?id=einstein-hilbert-action-principle-54934f1b" style="display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; background: var(--accent-default, #64ffda); color: #020c1b; font-weight: 700; border-radius: 8px; text-decoration: none; font-size: 0.84rem; transition: all 0.2s;">
                        <span>Open in Equation Explainer</span>
                        <span>➔</span>
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="/js/formula_graph.js?v=<?= filemtime(PROJECT_ROOT . '/public/js/formula_graph.js') ?>" defer></script>
<script>
document.addEventListener('DOMContentLoaded', () => {
    const canvasContainer = document.getElementById('universe-graph-canvas');
    if (!canvasContainer || !window.FormulaLineageGraph) return;

    const universeGraph = new window.FormulaLineageGraph('universe-graph-canvas', {
        depth: 2,
        onNodeClick: (node) => {
            updateActiveCard(node);
            universeGraph.loadFormula(node.id);
        }
    });

    function updateActiveCard(node) {
        document.getElementById('active-card-title').innerText = node.title;
        document.getElementById('active-card-domain').innerText = node.domain_label || node.domain;
        document.getElementById('active-card-id').innerText = node.id;
        document.getElementById('active-card-summary').innerText = node.summary || 'Click to explore mathematical details and derivations.';
        document.getElementById('btn-open-explainer').href = `/physics/equation-explainer?id=${encodeURIComponent(node.id)}`;
    }

    // Hub selection
    document.querySelectorAll('.hub-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const fid = btn.getAttribute('data-id');
            if (fid) {
                universeGraph.loadFormula(fid);
            }
        });
    });

    // Path Finder
    const btnFindPath = document.getElementById('btn-find-path');
    const resultBox = document.getElementById('path-result-box');

    if (btnFindPath && resultBox) {
        btnFindPath.addEventListener('click', async () => {
            const start = document.getElementById('path-start-id').value.trim();
            const end = document.getElementById('path-end-id').value.trim();
            if (!start || !end) return;

            resultBox.style.display = 'block';
            resultBox.innerHTML = '<span style="color: #64ffda;">Calculating derivation path...</span>';

            try {
                const resp = await fetch(`/physics/api/formula-path?start=${encodeURIComponent(start)}&end=${encodeURIComponent(end)}`);
                const res = await resp.json();

                if (res.success && res.data && res.data.found) {
                    let html = `<div style="color: #64ffda; font-weight: 700; margin-bottom: 6px;">✓ Path Found (${res.data.hops} Steps):</div>`;
                    html += `<ol style="margin: 0; padding-left: 18px; color: #cbd5e1; line-height: 1.6;">`;
                    res.data.path_nodes.forEach(pn => {
                        html += `<li><a href="/physics/equation-explainer?id=${encodeURIComponent(pn.id)}" style="color: #38bdf8; text-decoration: none; font-weight: 600;">${pn.title || pn.id}</a></li>`;
                    });
                    html += `</ol>`;
                    resultBox.innerHTML = html;
                } else {
                    resultBox.innerHTML = `<span style="color: #f87171;">${res.data?.message || 'No direct derivation path found.'}</span>`;
                }
            } catch (e) {
                resultBox.innerHTML = '<span style="color: #f87171;">Route search error.</span>';
            }
        });
    }

    // Initial load with default landmark
    universeGraph.loadFormula('einstein-hilbert-action-principle-54934f1b');
});
</script>

<style>
.hub-btn:hover {
    background: rgba(100, 255, 218, 0.08) !important;
    border-color: rgba(100, 255, 218, 0.3) !important;
    transform: translateX(3px);
}
</style>
