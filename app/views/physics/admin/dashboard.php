<?php
// Admin Dashboard view
$stats = $health['global_stats'] ?? [];
$scorecard = $health['platinum_scorecard'] ?? [];
$integrity = $health['integrity_summary'] ?? [];
$shards = $health['shard_health'] ?? [];
?>

<div class="admin-dashboard-container" style="padding: 10px 0 40px 0;">
    <!-- Premium Header -->
    <header class="simulations-header" style="margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 25px; display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <h1 style="font-size: 3rem; margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 50%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                <?= htmlspecialchars($title) ?>
            </h1>
            <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 650px;">
                Platform consistency monitoring, qualitative violation audits, and automatic reference indexing controllers.
            </p>
        </div>
        <div style="display: flex; gap: 12px; margin-bottom: 5px;">
            <a href="/physics/admin/editor" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center; gap: 6px;">
                <span>✏️ WYSIWYG Editor</span>
            </a>
            <a href="/physics/admin/critic" class="btn btn-primary" style="display: flex; align-items: center; gap: 6px;">
                <span>🧑‍🔬 Critic Portal</span>
            </a>
        </div>
    </header>

    <!-- Metrics Grid -->
    <section style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 40px;">
        <!-- Card 1: Platinum Ratio -->
        <div class="admin-stat-card">
            <h4>Total Subtopics</h4>
            <div class="stat-value"><?= number_format($stats['total_subtopics'] ?? 0) ?></div>
            <div class="stat-label"><?= $scorecard['flagged_platinum_percentage'] ?? 0 ?>% Platinum (<?= number_format($scorecard['flagged_platinum_count'] ?? 0) ?> graduated)</div>
        </div>

        <!-- Card 2: Words -->
        <div class="admin-stat-card">
            <h4>Encyclopedia Volume</h4>
            <div class="stat-value"><?= number_format($stats['total_words'] ?? 0) ?></div>
            <div class="stat-label">Words of dense academic prose</div>
        </div>

        <!-- Card 3: Links -->
        <div class="admin-stat-card">
            <h4>Connected Nodes</h4>
            <div class="stat-value"><?= number_format($stats['total_links'] ?? 0) ?></div>
            <div class="stat-label">Average of <?= $stats['total_subtopics'] ? round($stats['total_links'] / $stats['total_subtopics'], 1) : 0 ?> links per subtopic</div>
        </div>

        <!-- Card 4: Formulas -->
        <div class="admin-stat-card">
            <h4>Typeset Formulas</h4>
            <div class="stat-value"><?= number_format($stats['total_formula_refs'] ?? 0) ?></div>
            <div class="stat-label">Vector SVGs compiled and stored</div>
        </div>
    </section>

    <!-- Main Workspace Layout -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 30px;">
        <!-- Left Column: Shard Health & Actions -->
        <div>
            <!-- Shards Health Table -->
            <div class="glass-panel" style="margin-bottom: 30px;">
                <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif;">Database Shards Health</h3>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; margin-top: 15px; text-align: left;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); font-size: 0.9rem;">
                                <th style="padding: 12px 8px;">Shard File</th>
                                <th style="padding: 12px 8px;">Subtopics</th>
                                <th style="padding: 12px 8px;">Avg Words</th>
                                <th style="padding: 12px 8px;">Avg Density</th>
                                <th style="padding: 12px 8px;">Violations</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php foreach ($shards as $name => $sdata): ?>
                                <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.95rem; hover: background: rgba(255,255,255,0.01);">
                                    <td style="padding: 12px 8px; font-weight: 600; color: #ffffff;"><?= htmlspecialchars($name) ?></td>
                                    <td style="padding: 12px 8px;"><?= $sdata['count'] ?></td>
                                    <td style="padding: 12px 8px;"><?= round($sdata['avg_words']) ?></td>
                                    <td style="padding: 12px 8px;"><?= round($sdata['avg_density']) ?></td>
                                    <td style="padding: 12px 8px;">
                                        <?php if (($sdata['violations'] ?? 0) > 0): ?>
                                            <span style="color: #ff5555; font-weight: bold;">⚠️ <?= $sdata['violations'] ?></span>
                                        <?php else: ?>
                                            <span style="color: #55ff55;">✓ 0</span>
                                        <?php endif; ?>
                                    </td>
                                </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Controller Console Terminal -->
            <div class="glass-panel">
                <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif; display: flex; justify-content: space-between; align-items: center;">
                    <span>Developer Audit Shell</span>
                    <span style="font-size: 0.8rem; color: var(--text-muted); font-family: monospace;">Localhost execution</span>
                </h3>
                <div style="margin: 15px 0 20px 0; display: flex; gap: 12px;">
                    <button id="btn-autolinker" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                        🔗 Run Auto-Linker
                    </button>
                    <button id="btn-audit" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                        🛡️ Run Structural Audit
                    </button>
                </div>
                <div class="terminal-box">
                    <div class="terminal-header">
                        <span class="terminal-dot red"></span>
                        <span class="terminal-dot yellow"></span>
                        <span class="terminal-dot green"></span>
                        <span style="margin-left: 10px; font-size: 0.75rem; color: var(--text-muted);">sh - integrity_shield.py</span>
                    </div>
                    <pre id="terminal-console">Console initialized. Ready to execute pipeline triggers...</pre>
                </div>
            </div>
        </div>

        <!-- Right Column: Qualitative Gaps & Scorecard -->
        <div>
            <!-- Strict Scorecard -->
            <div class="glass-panel" style="margin-bottom: 30px;">
                <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif;">Organic Quality Scorecard</h3>
                <div style="margin: 20px 0 10px 0;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.95rem;">
                        <span>Platinum Index</span>
                        <span style="font-weight: bold; color: var(--accent-default);"><?= $scorecard['organic_platinum_percentage'] ?? 100 ?>%</span>
                    </div>
                    <div style="width: 100%; height: 8px; background: rgba(255,255,255,0.1); border-radius: 4px; overflow: hidden;">
                        <div style="width: <?= $scorecard['organic_platinum_percentage'] ?? 100 ?>%; height: 100%; background: var(--accent-default);"></div>
                    </div>
                </div>
                
                <ul style="list-style: none; padding: 0; margin: 20px 0 0 0; font-size: 0.95rem; line-height: 2;">
                    <li style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                        <span>In Media Res Violations</span>
                        <span style="font-weight: 600; color: <?= ($scorecard['lead_violations'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $scorecard['lead_violations'] ?? 0 ?></span>
                    </li>
                    <li style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                        <span>Bullet/List Artifacts</span>
                        <span style="font-weight: 600; color: <?= ($scorecard['artifact_violations'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $scorecard['artifact_violations'] ?? 0 ?></span>
                    </li>
                    <li style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                        <span>Low Depth (< 650 words)</span>
                        <span style="font-weight: 600; color: <?= ($scorecard['low_depth_count'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $scorecard['low_depth_count'] ?? 0 ?></span>
                    </li>
                    <li style="display: flex; justify-content: space-between; padding: 4px 0;">
                        <span>Low Technical Density</span>
                        <span style="font-weight: 600; color: <?= ($scorecard['non_technical_count'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $scorecard['non_technical_count'] ?? 0 ?></span>
                    </li>
                </ul>
            </div>

            <!-- Structural Integrity -->
            <div class="glass-panel">
                <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif;">Structural Integrity</h3>
                <ul style="list-style: none; padding: 0; margin: 15px 0 0 0; font-size: 0.95rem; line-height: 2;">
                    <li style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 6px 0;">
                        <span>Broken Internal Links</span>
                        <span style="font-weight: 600; color: <?= ($integrity['broken_links'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $integrity['broken_links'] ?? 0 ?></span>
                    </li>
                    <li style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.05); padding: 6px 0;">
                        <span>Broken Formula IDs</span>
                        <span style="font-weight: 600; color: <?= ($integrity['broken_formulas'] ?? 0) > 0 ? '#ff5555' : '#55ff55' ?>;"><?= $integrity['broken_formulas'] ?? 0 ?></span>
                    </li>
                    <li style="display: flex; justify-content: space-between; padding: 6px 0;">
                        <span>Orphan Subtopics</span>
                        <span style="font-weight: 600; color: <?= ($integrity['orphans_count'] ?? 0) > 0 ? '#ffcc00' : '#55ff55' ?>;"><?= $integrity['orphans_count'] ?? 0 ?></span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</div>

<style>
.glass-panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.admin-stat-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(8px);
}

.admin-stat-card h4 {
    margin: 0 0 10px 0;
    color: var(--text-muted);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Space Grotesk', sans-serif;
}

.admin-stat-card .stat-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 5px;
    font-family: 'Space Grotesk', sans-serif;
}

.admin-stat-card .stat-label {
    font-size: 0.85rem;
    color: var(--text-muted);
}

.terminal-box {
    background: #0d0e12;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 15px;
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
    font-size: 0.85rem;
    margin-top: 15px;
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

.terminal-box pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-all;
    color: #39ff14; /* Glowing green console text */
    max-height: 250px;
    overflow-y: auto;
}
</style>

<script nonce="<?= $nonce ?>">
function runMaintenance(action) {
    const consoleElem = document.getElementById('terminal-console');
    consoleElem.textContent = '[$] Running ' + action + '...\n';
    
    const btn = document.getElementById('btn-autolinker');
    btn.disabled = true;
    
    fetch(BASE_URL + '/physics/admin/api/' + action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        consoleElem.textContent += '\n' + data.logs + '\n\n';
        if (data.success) {
            consoleElem.textContent += '[✓] Execution finished successfully.';
        } else {
            consoleElem.textContent += '[❌] Execution failed.';
        }
    })
    .catch(err => {
        btn.disabled = false;
        consoleElem.textContent += '\nError executing trigger: ' + err;
    });
}

function runFullAudit() {
    const consoleElem = document.getElementById('terminal-console');
    consoleElem.textContent = '[$] Initiating full database audit...\n';
    
    const btn = document.getElementById('btn-audit');
    btn.disabled = true;
    
    // We can simulate full audit by running run_critic with no slug (or query stats)
    fetch(BASE_URL + '/physics/admin/api/run-critic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ slug: '' })
    })
    .then(res => res.json())
    .then(data => {
        btn.disabled = false;
        consoleElem.textContent += '\n' + data.logs + '\n\n';
        if (data.success) {
            consoleElem.textContent += '[✓] Full consensus audit completed successfully.';
        } else {
            consoleElem.textContent += '[❌] Audit detected warning/failure gates.';
        }
    })
    .catch(err => {
        btn.disabled = false;
        consoleElem.textContent += '\nError executing audit: ' + err;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const autolinkerBtn = document.getElementById('btn-autolinker');
    if (autolinkerBtn) {
        autolinkerBtn.addEventListener('click', () => runMaintenance('run-autolinker'));
    }
    const auditBtn = document.getElementById('btn-audit');
    if (auditBtn) {
        auditBtn.addEventListener('click', runFullAudit);
    }
});
</script>
