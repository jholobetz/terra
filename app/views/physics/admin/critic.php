<?php
// Admin Critic Portal view
?>

<div class="admin-critic-container" style="padding: 10px 0 40px 0;">
    <!-- Premium Header -->
    <header class="simulations-header" style="margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <h1 style="font-size: 3rem; margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 50%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                <?= htmlspecialchars($title) ?>
            </h1>
            <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 650px;">
                Audit physical assertions against arXiv/Crossref academic registries and commit verified citation headers.
            </p>
        </div>
        <div style="display: flex; gap: 12px; margin-bottom: 5px;">
            <a href="/physics/admin/dashboard" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                <span>📊 Dashboard</span>
            </a>
            <a href="/physics/admin/editor" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                <span>✏️ WYSIWYG Editor</span>
            </a>
        </div>
    </header>

    <!-- Main Grid -->
    <div style="display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px;">
        <!-- Left: Registered Reference Topics -->
        <div class="glass-panel" style="height: 70vh; display: flex; flex-direction: column; overflow: hidden;">
            <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif;">Registered Reference Topics</h3>
            
            <div style="flex: 1; overflow-y: auto; margin-top: 15px;">
                <table style="width: 100%; border-collapse: collapse; text-align: left;">
                    <thead>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); font-size: 0.9rem;">
                            <th style="padding: 12px 8px;">Subtopic Slug</th>
                            <th style="padding: 12px 8px;">Academic References</th>
                            <th style="padding: 12px 8px; text-align: center;">Consensus</th>
                            <th style="padding: 12px 8px; text-align: right;">Curation Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($references as $slug => $ref): ?>
                            <?php 
                            $hasCache = isset($cache[$slug]);
                            $citationsCount = $hasCache ? count($cache[$slug]) : 0;
                            ?>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.95rem;">
                                <td style="padding: 12px 8px;">
                                    <div style="font-weight: 600; color: #ffffff;"><?= htmlspecialchars($ref['title']) ?></div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;"><?= htmlspecialchars($slug) ?></div>
                                </td>
                                <td style="padding: 12px 8px; font-size: 0.85rem; color: var(--text-muted);">
                                    <?php if ($hasCache): ?>
                                        <span style="color: #ffffff;">📖 <?= htmlspecialchars($cache[$slug][0]['title']) ?></span>
                                        <div style="font-family: monospace; font-size: 0.7rem; color: var(--text-muted); margin-top: 3px;">
                                            DOI: <?= htmlspecialchars($cache[$slug][0]['doi'] ?: 'arXiv identifier') ?>
                                        </div>
                                    <?php else: ?>
                                        <span style="color: #ff9900; font-style: italic;">No cached literature abstracts</span>
                                    <?php endif; ?>
                                </td>
                                <td style="padding: 12px 8px; text-align: center;">
                                    <?php if ($hasCache): ?>
                                        <span class="badge badge-pass" style="background: rgba(85,255,85,0.1); color: #55ff55; border: 1px solid rgba(85,255,85,0.2); padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">Verified</span>
                                    <?php else: ?>
                                        <span class="badge badge-warn" style="background: rgba(255,153,0,0.1); color: #ff9900; border: 1px solid rgba(255,153,0,0.2); padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">Pending</span>
                                    <?php endif; ?>
                                </td>
                                <td style="padding: 12px 8px; text-align: right;">
                                    <div style="display: flex; justify-content: flex-end; gap: 8px;">
                                        <button onclick="runCritic('<?= $slug ?>', false)" class="btn-action" title="Run dry-run consensus check">🔍 Audit</button>
                                        <button onclick="runCritic('<?= $slug ?>', true)" class="btn-action primary" title="Stamp verified DOIs into JSON shard">📖 Stamp</button>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Right: Critic Inspector Console -->
        <div class="glass-panel" style="height: 70vh; display: flex; flex-direction: column;">
            <h3 style="margin-top: 0; font-family: 'Space Grotesk', sans-serif;">Consensus Judge Console</h3>
            <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 5px;">View detailed logs of extracted physical claims and their corresponding academic papers.</p>
            
            <div class="terminal-box" style="flex: 1; display: flex; flex-direction: column; margin-top: 15px; padding: 12px;">
                <div class="terminal-header">
                    <span class="terminal-dot red"></span>
                    <span class="terminal-dot yellow"></span>
                    <span class="terminal-dot green"></span>
                    <span id="console-title" style="margin-left: 10px; font-size: 0.75rem; color: var(--text-muted);">critic_agent.log</span>
                </div>
                <pre id="terminal-console" style="flex: 1; margin: 0; font-size: 0.85rem; line-height: 1.4; color: #00ffff; text-shadow: 0 0 4px rgba(0, 255, 255, 0.2); overflow-y: auto;">Critic portal loaded. Select an action (Audit / Stamp) to trigger claim extraction and literature cross-referencing...</pre>
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

.btn-action {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-action:hover {
    background: rgba(255,255,255,0.08);
    border-color: rgba(255,255,255,0.15);
}

.btn-action.primary {
    background: var(--accent-default);
    border-color: var(--accent-default);
    font-weight: 600;
}

.btn-action.primary:hover {
    background: #00bfff;
    border-color: #00bfff;
}

.terminal-box {
    background: #090a0d;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
}

.terminal-header {
    display: flex;
    align-items: center;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    padding-bottom: 8px;
    margin-bottom: 8px;
}

.terminal-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
    display: inline-block;
}

.terminal-dot.red { background: #ff5f56; }
.terminal-dot.yellow { background: #ffbd2e; }
.terminal-dot.green { background: #27c93f; }
</style>

<script>
function runCritic(slug, writeCitations) {
    const consoleElem = document.getElementById('terminal-console');
    const titleElem = document.getElementById('console-title');
    
    titleElem.textContent = 'run_critic.py --slug ' + slug + (writeCitations ? ' --write-citations' : '');
    consoleElem.textContent = '[$] Initializing Consensus Critic pipeline for [' + slug + ']...\n';
    
    // Disable all buttons in rows during run
    const buttons = document.querySelectorAll('.btn-action');
    buttons.forEach(btn => btn.disabled = true);

    fetch('/physics/admin/api/run-critic', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ slug: slug, write_citations: writeCitations })
    })
    .then(res => res.json())
    .then(data => {
        buttons.forEach(btn => btn.disabled = false);
        consoleElem.textContent = data.logs + '\n';
        if (data.success) {
            consoleElem.textContent += '[✓] Consensus Critic run succeeded.';
            if (writeCitations) {
                consoleElem.textContent += '\n[✓] Stamped peer-reviewed citations block to JSON shard on disk.';
            }
        } else {
            consoleElem.textContent += '[❌] Consensus Critic run failed.';
        }
    })
    .catch(err => {
        buttons.forEach(btn => btn.disabled = false);
        consoleElem.textContent += '\nError executing critic agent: ' + err;
    });
}
</script>
