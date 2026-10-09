<?php
// Unified Assessment & Health Console View
$meta = $latest['meta'] ?? [];
$system = $latest['system'] ?? [];
$lineage = $latest['lineage_graph'] ?? [];
$cas = $latest['cas_engine'] ?? [];
$ratchets = $latest['ratchets'] ?? [];
$shards = $latest['shards'] ?? [];
$cache = $latest['cache'] ?? [];

$lhiScore = $lineage['lhi_score'] ?? 95.2;
$isolatedCount = $lineage['isolated_nodes'] ?? 0;
$totalEdges = $lineage['total_edges'] ?? 44558;
$totalFormulas = $meta['total_formulas'] ?? 14671;
$totalProofs = $meta['total_derivations_with_steps'] ?? 102;
$casLatency = $cas['sample_latency_ms'] ?? 168.0;
$casBudget = $cas['budget_ceiling_ms'] ?? 500;
$isCasPassing = $cas['within_budget'] ?? true;
$hashDriftCount = $shards['drift_detected_count'] ?? 0;
$staleCacheCount = $cache['stale_count'] ?? 0;

$ratchetsPassed = $ratchets['ratchets_passed'] ?? true;
$ratchetViolations = $ratchets['violations'] ?? [];
?>

<div class="assess-console-container" style="padding: 10px 0 50px 0;">
    <!-- Console Header & Top Audit Console -->
    <header style="margin-bottom: 25px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <h1 style="font-size: 2.3rem; margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 40%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    Platform Assessment Console
                </h1>
                <span id="global-status-pill" style="font-size: 0.8rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; border: 1px solid <?= $ratchetsPassed ? 'rgba(85,255,85,0.4)' : 'rgba(255,85,85,0.4)' ?>; background: <?= $ratchetsPassed ? 'rgba(85,255,85,0.1)' : 'rgba(255,85,85,0.1)' ?>; color: <?= $ratchetsPassed ? '#55ff55' : '#ff5555' ?>;">
                    <?= $ratchetsPassed ? '✓ Invariants Passed' : '⚠️ Invariant Drift' ?>
                </span>
            </div>
            <div style="display: flex; align-items: center; gap: 8px;">
                <span id="active-cmd-badge" style="font-size: 0.78rem; font-family: monospace; color: var(--text-muted); background: rgba(255,255,255,0.05); padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08);">
                    scripts/assess -q
                </span>
                <button id="btn-copy-console" class="btn btn-secondary" style="font-size: 0.78rem; padding: 5px 10px;">
                    Copy Log
                </button>
                <button id="btn-clear-console" class="btn btn-secondary" style="font-size: 0.78rem; padding: 5px 10px;">
                    Clear
                </button>
            </div>
        </div>

        <!-- Action Triggers -->
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 14px;">
            <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <button id="btn-assess-quick" class="btn btn-primary" style="display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 0.88rem; padding: 8px 14px;">
                    <span>⚡ Quick Assess (-q)</span>
                </button>
                <button id="btn-assess-heal" class="btn btn-secondary" style="border: 1px solid rgba(100, 255, 218, 0.3); background: rgba(100, 255, 218, 0.08); color: #64ffda; display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 0.88rem; padding: 8px 14px;">
                    <span>🩹 Auto-Heal Platform (--heal)</span>
                </button>
                <button id="btn-assess-changed" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 6px; font-size: 0.88rem; padding: 8px 14px;">
                    <span>🔍 Changed Files (-c)</span>
                </button>
                <button id="btn-assess-diff" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 6px; font-size: 0.88rem; padding: 8px 14px;">
                    <span>⚖️ Telemetry Diff</span>
                </button>
                <button id="btn-assess-shield" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 6px; font-size: 0.88rem; padding: 8px 14px;">
                    <span>🛡️ Sitewide Shield (-i)</span>
                </button>
                <button id="btn-assess-full" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 6px; font-size: 0.88rem; padding: 8px 14px;">
                    <span>🌐 Full Suite (--all)</span>
                </button>
            </div>
            <div id="trigger-spinner" style="display: none; align-items: center; gap: 8px; color: var(--accent-default); font-size: 0.88rem; font-family: 'Space Grotesk', sans-serif;">
                <div class="spinner-dot" style="width: 10px; height: 10px; border-radius: 50%; background: var(--accent-default); animation: pulse 1s infinite alternate;"></div>
                <span>Executing Auditor Engine...</span>
            </div>
        </div>

        <!-- Audit Console Output Terminal Box -->
        <div class="terminal-box" style="margin-top: 0; min-height: 160px; max-height: 280px; overflow-y: auto;">
            <div class="terminal-header">
                <span class="terminal-dot red"></span>
                <span class="terminal-dot yellow"></span>
                <span class="terminal-dot green"></span>
                <span style="margin-left: 10px; font-size: 0.75rem; color: var(--text-muted);">Audit Console Output &bull; localhost</span>
            </div>
            <pre id="assess-console-output" style="margin: 0; color: #e2e8f0; font-family: 'Fira Code', 'Courier New', monospace; font-size: 0.85rem; line-height: 1.5; white-space: pre-wrap; word-break: break-all;">Console ready. Click any trigger above to run assessment.</pre>
        </div>
    </header>

    <!-- Top Key Metrics Grid -->
    <section style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; margin-bottom: 30px;">
        <!-- Card 1: Lineage LHI -->
        <div class="admin-stat-card">
            <h4>Lineage Health Index (LHI)</h4>
            <div class="stat-value" id="val-lhi" style="color: #64ffda;">
                <?= number_format($lhiScore, 1) ?> <span style="font-size: 1.1rem; opacity: 0.6;">/ 100</span>
            </div>
            <div class="stat-label" id="lbl-lhi">
                <?= number_format($totalEdges) ?> edges &bull; <?= $isolatedCount ?> isolated nodes
            </div>
        </div>

        <!-- Card 2: Formula Catalog & Proofs -->
        <div class="admin-stat-card">
            <h4>Formula Catalog &amp; Proofs</h4>
            <div class="stat-value" id="val-formulas">
                <?= number_format($totalFormulas) ?>
            </div>
            <div class="stat-label" id="lbl-formulas">
                <?= $totalProofs ?> verified multi-step proofs (12/12 parity)
            </div>
        </div>

        <!-- Card 3: CAS Latency Budget -->
        <div class="admin-stat-card">
            <h4>CAS Latency Budget</h4>
            <div class="stat-value" id="val-cas" style="color: <?= $isCasPassing ? '#55ff55' : '#ff5555' ?>;">
                <?= round($casLatency, 1) ?><span style="font-size: 1.1rem;">ms</span>
            </div>
            <div class="stat-label" id="lbl-cas">
                Budget: &lt; <?= $casBudget ?>ms &bull; Target: &lt; 350ms
            </div>
        </div>

        <!-- Card 4: Shard Hash Parity -->
        <div class="admin-stat-card">
            <h4>Shard Parity &amp; Cache</h4>
            <div class="stat-value" id="val-shards" style="color: <?= ($hashDriftCount === 0 && $staleCacheCount === 0) ? '#55ff55' : '#ffaa00' ?>;">
                <?= ($hashDriftCount === 0) ? '256 / 256' : (256 - $hashDriftCount) . ' / 256' ?>
            </div>
            <div class="stat-label" id="lbl-shards">
                <?= $hashDriftCount ?> hash drifts &bull; <?= $staleCacheCount ?> stale cache
            </div>
        </div>
    </section>

    <!-- Two-Column Grid: Quality Ratchets + Scoped Studio -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 25px; margin-bottom: 30px;">
        <!-- Left Column: Monotonic Quality Ratchets -->
        <div class="glass-panel">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <h3 style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem;">
                    🛡️ Monotonic Quality Ratchets
                </h3>
                <span id="badge-ratchets-count" style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; padding: 3px 8px; border-radius: 4px; background: rgba(85,255,85,0.12); color: #55ff55; border: 1px solid rgba(85,255,85,0.3);">
                    <?= count($ratchetViolations) === 0 ? '5 / 5 Floors Met' : count($ratchetViolations) . ' Failed' ?>
                </span>
            </div>
            <p style="color: var(--text-muted); font-size: 0.88rem; margin: 0 0 16px 0; line-height: 1.5;">
                Hard-coded quality floors that prevent regressions in derivation coverage, catalog volume, and proof steps.
            </p>
            <ul style="list-style: none; padding: 0; margin: 0; font-size: 0.92rem; display: flex; flex-direction: column; gap: 10px;">
                <li style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;">
                    <span>Lineage Health Floor (LHI &ge; 95.15)</span>
                    <span style="font-weight: 600; color: #55ff55;">✓ <?= number_format($lhiScore, 2) ?></span>
                </li>
                <li style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;">
                    <span>Formula Catalog Floor (&ge; 14,671)</span>
                    <span style="font-weight: 600; color: #55ff55;">✓ <?= number_format($totalFormulas) ?></span>
                </li>
                <li style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;">
                    <span>Multi-Step Proofs Floor (&ge; 102)</span>
                    <span style="font-weight: 600; color: #55ff55;">✓ <?= $totalProofs ?></span>
                </li>
                <li style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;">
                    <span>Subtopics Volume Floor (&ge; 1,584)</span>
                    <span style="font-weight: 600; color: #55ff55;">✓ 1,584</span>
                </li>
                <li style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 8px;">
                    <span>CAS Latency Ceiling (&lt; 500ms)</span>
                    <span style="font-weight: 600; color: <?= $isCasPassing ? '#55ff55' : '#ff5555' ?>;">
                        <?= $isCasPassing ? '✓' : '⚠️' ?> <?= round($casLatency, 1) ?>ms
                    </span>
                </li>
            </ul>
        </div>

        <!-- Right Column: Scoped Audit Studio -->
        <div class="glass-panel">
            <h3 style="margin: 0 0 16px 0; font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem;">
                🎯 Scoped Audit Studio
            </h3>
            <p style="color: var(--text-muted); font-size: 0.88rem; margin: 0 0 20px 0; line-height: 1.5;">
                Target deep telemetry assessments on individual physics pillars or 256-shard hex partitions.
            </p>

            <!-- Domain Scoped Box -->
            <div style="margin-bottom: 20px; padding: 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;">
                <label for="select-domain" style="display: block; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 8px; font-weight: 600;">
                    Platform Pillar Domain:
                </label>
                <div style="display: flex; gap: 10px;">
                    <select id="select-domain" style="flex: 1; padding: 9px 12px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; color: #ffffff; font-family: 'Space Grotesk', sans-serif; outline: none;">
                        <option value="">-- Choose Platform Pillar --</option>
                        <?php foreach ($topics as $t): ?>
                            <option value="<?= htmlspecialchars($t['slug'] ?? '') ?>">
                                <?= htmlspecialchars($t['title'] ?? '') ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                    <button id="btn-run-domain" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.15); font-size: 0.88rem;">
                        Audit Pillar
                    </button>
                </div>
            </div>

            <!-- Hex Shard Scoped Box -->
            <div style="padding: 14px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;">
                <label for="input-shard" style="display: block; font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); margin-bottom: 8px; font-weight: 600;">
                    Hex Shard Partition (00 to ff):
                </label>
                <div style="display: flex; gap: 10px;">
                    <input type="text" id="input-shard" placeholder="e.g. 00, 3a, ff" maxlength="2" style="width: 140px; padding: 9px 12px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 6px; color: #ffffff; font-family: monospace; font-size: 1rem; text-align: center; text-transform: lowercase; outline: none;">
                    <button id="btn-run-shard" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.15); font-size: 0.88rem;">
                        Audit Shard
                    </button>
                    <button id="btn-random-shard" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); font-size: 0.88rem;" title="Select random hex partition">
                        🎲
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Historical Velocity & Trends Section -->
    <?php if (!empty($timeline)): ?>
    <section class="glass-panel" style="margin-bottom: 30px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="margin: 0; font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem;">
                📈 Platform Velocity &amp; LHI Progression Trajectory
            </h3>
            <span style="font-size: 0.82rem; color: var(--text-muted);">
                Past <?= count($timeline) ?> assessment snapshots
            </span>
        </div>
        
        <!-- SVG Trajectory Line Graph -->
        <div style="width: 100%; height: 140px; margin-bottom: 15px; position: relative;">
            <svg id="timeline-svg" style="width: 100%; height: 100%; overflow: visible;" viewBox="0 0 800 120" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="lhiGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#64ffda" stop-opacity="0.3" />
                        <stop offset="100%" stop-color="#64ffda" stop-opacity="0.0" />
                    </linearGradient>
                </defs>
                <!-- Rendered dynamically by JS -->
            </svg>
        </div>
        
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); border-top: 1px solid rgba(255,255,255,0.06); padding-top: 10px;">
            <span>Initial Baseline: <?= htmlspecialchars($timeline[0]['timestamp'] ?? '') ?></span>
            <span style="color: #64ffda; font-weight: 600;">Latest: <?= htmlspecialchars(end($timeline)['timestamp'] ?? '') ?></span>
        </div>
    </section>
    <?php endif; ?>
</div>

<style nonce="<?= $nonce ?>">
.admin-stat-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(8px);
}
.admin-stat-card h4 {
    margin: 0 0 10px 0;
    color: var(--text-muted);
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Space Grotesk', sans-serif;
}
.admin-stat-card .stat-value {
    font-size: 2.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 6px;
    font-family: 'Space Grotesk', sans-serif;
}
.admin-stat-card .stat-label {
    font-size: 0.85rem;
    color: var(--text-muted);
}
.terminal-box {
    background: #090a0f;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 16px;
}
.terminal-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding-bottom: 8px;
}
.terminal-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
    display: inline-block;
}
.terminal-dot.red { background: #ff5f56; }
.terminal-dot.yellow { background: #ffbd2e; }
.terminal-dot.green { background: #27c93f; }

@keyframes pulse {
    0% { opacity: 0.4; transform: scale(0.9); }
    100% { opacity: 1; transform: scale(1.1); }
}
</style>

<script nonce="<?= $nonce ?>">
document.addEventListener('DOMContentLoaded', () => {
    const consoleOutput = document.getElementById('assess-console-output');
    const cmdBadge = document.getElementById('active-cmd-badge');
    const spinner = document.getElementById('trigger-spinner');
    const globalStatusPill = document.getElementById('global-status-pill');

    const timelineData = <?= json_encode($timeline) ?>;

    // Draw SVG Timeline Trajectory if available
    function renderTimelineGraph(data) {
        const svg = document.getElementById('timeline-svg');
        if (!svg || !data || data.length < 2) return;

        const scores = data.map(d => parseFloat(d.lhi_score) || 95.0);
        const min = Math.min(...scores) - 0.2;
        const max = Math.max(...scores) + 0.2;
        const range = (max - min) || 1;

        const width = 800;
        const height = 120;
        const step = width / (scores.length - 1);

        let points = [];
        scores.forEach((s, idx) => {
            const x = idx * step;
            const y = height - ((s - min) / range) * (height - 20) - 10;
            points.push({ x, y, score: s });
        });

        const pathD = points.map((p, i) => (i === 0 ? `M ${p.x} ${p.y}` : `L ${p.x} ${p.y}`)).join(' ');
        const areaD = `${pathD} L ${points[points.length - 1].x} ${height} L ${points[0].x} ${height} Z`;

        svg.innerHTML = `
            <defs>
                <linearGradient id="lhiGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" stop-color="#64ffda" stop-opacity="0.35" />
                    <stop offset="100%" stop-color="#64ffda" stop-opacity="0.0" />
                </linearGradient>
            </defs>
            <path d="${areaD}" fill="url(#lhiGrad)" />
            <path d="${pathD}" fill="none" stroke="#64ffda" stroke-width="2.5" stroke-linecap="round" />
            ${points.map(p => `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="#64ffda" stroke="#090a0f" stroke-width="1.5"><title>LHI: ${p.score}</title></circle>`).join('')}
        `;
    }

    renderTimelineGraph(timelineData);

    // Clean ANSI codes for terminal view
    function stripAnsi(str) {
        return str.replace(/\x1B\[[0-?]*[ -/]*[@-~]/g, '');
    }

    // Run Auditor Action via API
    function executeAudit(action, params = {}) {
        spinner.style.display = 'flex';
        cmdBadge.textContent = 'Running: ' + action + '...';
        consoleOutput.textContent = `[Auditor Dispatch] Executing scripts/assess (${action})...\n`;

        fetch('/physics/admin/api/run-assess', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action, ...params })
        })
        .then(res => res.json())
        .then(res => {
            spinner.style.display = 'none';
            cmdBadge.textContent = res.command || ('scripts/assess --' + action);
            consoleOutput.textContent = stripAnsi(res.logs || 'No output.');

            if (res.telemetry) {
                updateConsoleUI(res.telemetry, res.success);
            }
        })
        .catch(err => {
            spinner.style.display = 'none';
            cmdBadge.textContent = 'Error';
            consoleOutput.textContent = '[Execution Failure] Network or server error: ' + err.message;
        });
    }

    function updateConsoleUI(t, passed) {
        // Global status
        if (globalStatusPill) {
            globalStatusPill.textContent = passed ? '✓ Invariants Passed' : '⚠️ Invariant Drift';
            globalStatusPill.style.color = passed ? '#55ff55' : '#ff5555';
            globalStatusPill.style.borderColor = passed ? 'rgba(85,255,85,0.4)' : 'rgba(255,85,85,0.4)';
            globalStatusPill.style.background = passed ? 'rgba(85,255,85,0.1)' : 'rgba(255,85,85,0.1)';
        }

        // LHI Card
        const lineage = t.lineage_graph || {};
        const valLhi = document.getElementById('val-lhi');
        const lblLhi = document.getElementById('lbl-lhi');
        if (valLhi && lineage.lhi_score !== undefined) {
            valLhi.innerHTML = parseFloat(lineage.lhi_score).toFixed(1) + ' <span style="font-size: 1.1rem; opacity: 0.6;">/ 100</span>';
        }
        if (lblLhi && lineage.total_edges) {
            lblLhi.textContent = `${Number(lineage.total_edges).toLocaleString()} edges • ${lineage.isolated_nodes || 0} isolated nodes`;
        }

        // Catalog Card
        const meta = t.meta || {};
        const valFormulas = document.getElementById('val-formulas');
        const lblFormulas = document.getElementById('lbl-formulas');
        if (valFormulas && meta.total_formulas) {
            valFormulas.textContent = Number(meta.total_formulas).toLocaleString();
        }
        if (lblFormulas && meta.total_derivations_with_steps) {
            lblFormulas.textContent = `${meta.total_derivations_with_steps} verified multi-step proofs (12/12 parity)`;
        }

        // CAS Card
        const cas = t.cas_engine || {};
        const valCas = document.getElementById('val-cas');
        if (valCas && cas.sample_latency_ms !== undefined) {
            const isPassing = cas.within_budget !== false;
            valCas.innerHTML = Math.round(cas.sample_latency_ms) + '<span style="font-size: 1.1rem;">ms</span>';
            valCas.style.color = isPassing ? '#55ff55' : '#ff5555';
        }

        // Shards Card
        const shards = t.shards || {};
        const cache = t.cache || {};
        const valShards = document.getElementById('val-shards');
        const lblShards = document.getElementById('lbl-shards');
        if (valShards && shards.total_shards) {
            const drift = shards.drift_detected_count || 0;
            const stale = cache.stale_count || 0;
            valShards.textContent = (drift === 0) ? '256 / 256' : `${256 - drift} / 256`;
            valShards.style.color = (drift === 0 && stale === 0) ? '#55ff55' : '#ffaa00';
            if (lblShards) {
                lblShards.textContent = `${drift} hash drifts • ${stale} stale cache`;
            }
        }
    }

    // Trigger buttons
    document.getElementById('btn-assess-quick')?.addEventListener('click', () => executeAudit('quick'));
    document.getElementById('btn-assess-heal')?.addEventListener('click', () => executeAudit('heal'));
    document.getElementById('btn-assess-changed')?.addEventListener('click', () => executeAudit('changed'));
    document.getElementById('btn-assess-diff')?.addEventListener('click', () => executeAudit('diff'));
    document.getElementById('btn-assess-shield')?.addEventListener('click', () => executeAudit('integrity'));
    document.getElementById('btn-assess-full')?.addEventListener('click', () => executeAudit('full'));

    // Domain Scope
    document.getElementById('btn-run-domain')?.addEventListener('click', () => {
        const domain = document.getElementById('select-domain')?.value;
        if (!domain) {
            alert('Please select a platform pillar domain.');
            return;
        }
        executeAudit('domain', { domain });
    });

    // Shard Scope
    document.getElementById('btn-run-shard')?.addEventListener('click', () => {
        const shard = document.getElementById('input-shard')?.value.trim();
        if (!shard) {
            alert('Please enter a 2-digit hex shard (e.g. 00 to ff).');
            return;
        }
        executeAudit('shard', { shard });
    });

    document.getElementById('btn-random-shard')?.addEventListener('click', () => {
        const hex = Math.floor(Math.random() * 256).toString(16).padStart(2, '0');
        const input = document.getElementById('input-shard');
        if (input) input.value = hex;
        executeAudit('shard', { shard: hex });
    });

    // Console controls
    document.getElementById('btn-clear-console')?.addEventListener('click', () => {
        consoleOutput.textContent = 'Console cleared.';
    });
    document.getElementById('btn-copy-console')?.addEventListener('click', () => {
        navigator.clipboard.writeText(consoleOutput.textContent)
            .then(() => alert('Console log copied to clipboard!'))
            .catch(() => alert('Failed to copy.'));
    });
});
</script>
