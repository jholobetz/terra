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
    <div class="admin-critic-grid">
        <!-- Left: Registered Reference Topics -->
        <div class="glass-panel" style="height: 70vh; display: flex; flex-direction: column; overflow: hidden;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0; margin-bottom: 5px;">
                <h3 style="margin: 0; font-family: 'Space Grotesk', sans-serif;">Registered Reference Topics</h3>
                <button id="btn-open-register-modal" class="btn-action primary" style="font-size: 0.8rem; padding: 5px 12px; border-radius: 4px;">+ Register Reference</button>
            </div>
            
            <div style="flex: 1; overflow-y: auto; margin-top: 15px;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; table-layout: fixed;">
                    <thead>
                        <tr style="border-bottom: 1px solid rgba(255,255,255,0.1); color: var(--text-muted); font-size: 0.9rem;">
                            <th style="padding: 12px 8px; width: 25%;">Subtopic Slug</th>
                            <th style="padding: 12px 8px; width: 45%;">Academic References</th>
                            <th style="padding: 12px 8px; text-align: center; width: 15%;">Consensus</th>
                            <th style="padding: 12px 8px; text-align: right; width: 15%;">Curation Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($references as $slug => $ref): ?>
                            <?php 
                            $hasCache = isset($cache[$slug]);
                            $subtopic = $subtopics[$slug] ?? null;
                            $verification = $subtopic ? ($subtopic['verification'] ?? null) : null;
                            $isVerified = !empty($verification);
                            $citations = $verification ? ($verification['citations'] ?? []) : [];
                            ?>
                            <tr style="border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.95rem;">
                                <td style="padding: 12px 8px;">
                                    <div style="font-weight: 600; color: #ffffff;"><?= htmlspecialchars($ref['title']) ?></div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted); font-family: monospace;"><?= htmlspecialchars($slug) ?></div>
                                </td>
                                <td style="padding: 12px 8px; font-size: 0.85rem; color: var(--text-muted);">
                                    <?php if ($isVerified && !empty($citations)): ?>
                                        <?php foreach ($citations as $cit): ?>
                                            <div style="color: #ffffff; margin-bottom: 4px; display: flex; align-items: flex-start; gap: 4px;">
                                                <span>📖</span>
                                                <div>
                                                    <div>
                                                        <?php if (!empty($cit['url'])): ?>
                                                            <a href="<?= htmlspecialchars($cit['url']) ?>" target="_blank" style="color: #00ffff; text-decoration: none;"><?= htmlspecialchars($cit['title'] ?? '') ?></a>
                                                        <?php else: ?>
                                                            <?= htmlspecialchars($cit['title'] ?? '') ?>
                                                        <?php endif; ?>
                                                    </div>
                                                    <div style="font-family: monospace; font-size: 0.7rem; color: var(--text-muted); margin-top: 1px;">
                                                        DOI: <?= htmlspecialchars(($cit['doi'] ?? '') ?: 'arXiv identifier') ?>
                                                    </div>
                                                </div>
                                            </div>
                                        <?php endforeach; ?>
                                    <?php elseif ($hasCache): ?>
                                        <span style="color: #ff9900; font-style: italic;">Cache loaded (<?= count($cache[$slug]) ?> papers) - Pending Stamp</span>
                                    <?php else: ?>
                                        <span style="color: #ff9900; font-style: italic;">No cached literature abstracts</span>
                                    <?php endif; ?>
                                </td>
                                <td style="padding: 12px 8px; text-align: center;">
                                    <?php if ($isVerified): ?>
                                        <span class="badge badge-pass" style="background: rgba(85,255,85,0.1); color: #55ff55; border: 1px solid rgba(85,255,85,0.2); padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">Verified</span>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; font-family: monospace;">Score: <?= number_format(is_array($verification) ? ($verification['consensus_score'] ?? 0.0) : 0.0, 2) ?></div>
                                    <?php else: ?>
                                        <span class="badge badge-warn" style="background: rgba(255,153,0,0.1); color: #ff9900; border: 1px solid rgba(255,153,0,0.2); padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold;">Pending</span>
                                    <?php endif; ?>
                                </td>
                                <td style="padding: 12px 8px; text-align: right;">
                                    <div style="display: flex; justify-content: flex-end; gap: 8px;">
                                        <button class="btn-action btn-critic-audit" data-slug="<?= $slug ?>" title="Run dry-run consensus check">🔍 Audit</button>
                                        <button class="btn-action primary btn-critic-stamp" data-slug="<?= $slug ?>" title="Stamp verified DOIs into JSON shard">📖 Stamp</button>
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

<style nonce="<?= $nonce ?>">
body.physics-lab main.container {
    max-width: 1600px;
    width: 95%;
}

.admin-critic-grid {
    display: grid;
    grid-template-columns: 1.5fr 1fr;
    gap: 30px;
}

@media (max-width: 1024px) {
    .admin-critic-grid {
        grid-template-columns: 1fr;
    }
    .glass-panel {
        height: auto !important;
        min-height: 400px;
    }
}

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

/* Custom scrollbar for the table container and terminal console */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.01);
}
::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2);
}
</style>

<script nonce="<?= $nonce ?>">
function runCritic(slug, writeCitations) {
    const consoleElem = document.getElementById('terminal-console');
    const titleElem = document.getElementById('console-title');
    
    titleElem.textContent = 'run_critic.py --slug ' + slug + (writeCitations ? ' --write-citations' : '');
    consoleElem.textContent = '[$] Initializing Consensus Critic pipeline for [' + slug + ']...\n';
    
    // Disable all buttons in rows during run
    const buttons = document.querySelectorAll('.btn-action');
    buttons.forEach(btn => btn.disabled = true);

    fetch(BASE_URL + '/physics/admin/api/run-critic', {
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
                consoleElem.textContent += '\n[✓] Stamped peer-reviewed citations block to JSON shard on disk and synced to MariaDB. Reloading page...';
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            }
        } else {
            if (data.logs && data.logs.includes('REJECTED')) {
                consoleElem.textContent += '[!] Consensus Critic run complete: Slug rejected (does not meet literature consensus threshold).';
            } else {
                consoleElem.textContent += '[❌] Consensus Critic execution failed (error running agent script).';
            }
        }
    })
    .catch(err => {
        buttons.forEach(btn => btn.disabled = false);
        consoleElem.textContent += '\nError executing critic agent: ' + err;
    });
}

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.btn-critic-audit').forEach(btn => {
        btn.addEventListener('click', () => {
            const slug = btn.getAttribute('data-slug');
            runCritic(slug, false);
        });
    });
    document.querySelectorAll('.btn-critic-stamp').forEach(btn => {
        btn.addEventListener('click', () => {
            const slug = btn.getAttribute('data-slug');
            runCritic(slug, true);
        });
    });

    // Modal elements
    const modal = document.getElementById('register-modal');
    const openBtn = document.getElementById('btn-open-register-modal');
    const closeBtn = document.getElementById('btn-close-register-modal');
    const cancelBtn = document.getElementById('btn-cancel-register');
    const form = document.getElementById('register-reference-form');
    const selectElem = document.getElementById('reg-slug');
    const errorDiv = document.getElementById('register-error');

    if (openBtn && modal) {
        openBtn.addEventListener('click', () => {
            modal.style.display = 'flex';
        });
    }

    const closeModal = () => {
        if (modal) {
            modal.style.display = 'none';
        }
        if (form) {
            form.reset();
        }
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    };

    if (closeBtn) {
        closeBtn.addEventListener('click', closeModal);
    }
    if (cancelBtn) {
        cancelBtn.addEventListener('click', closeModal);
    }

    // Stopwords list for keyword extraction
    const stopWords = new Set([
        "the", "and", "of", "in", "to", "a", "is", "that", "for", "on", "with", "as", "by", "at", "an", "be", "this", "are", 
        "from", "which", "it", "its", "was", "were", "or", "but", "not", "he", "she", "they", "has", "have", "had", 
        "first", "second", "third", "law", "system", "systems", "every", "other", "every other", "each", "both", "all",
        "provides", "provided", "capable", "describing", "concept", "theory", "principle", "definition", "classical", "quantum"
    ]);

    function extractKeywords(text) {
        if (!text) return "";
        // Strip HTML, remove punctuation, split into lowercase words
        const cleanText = text.replace(/<[^>]*>/g, '').toLowerCase();
        const words = cleanText.match(/[a-z\-]{3,}/g) || [];

        // Count word frequencies
        const wordCounts = {};
        words.forEach(word => {
            if (!stopWords.has(word)) {
                wordCounts[word] = (wordCounts[word] || 0) + 1;
            }
        });

        // Sort words by frequency
        const sortedWords = Object.keys(wordCounts).sort((a, b) => wordCounts[b] - wordCounts[a]);

        // Return top 7 keywords as a comma-separated list
        return sortedWords.slice(0, 7).join(", ");
    }

    if (selectElem) {
        selectElem.addEventListener('change', () => {
            const slug = selectElem.value;
            const selectedOption = selectElem.options[selectElem.selectedIndex];
            const title = selectedOption.getAttribute('data-title') || '';
            
            const titleInput = document.getElementById('reg-title');
            const proseInput = document.getElementById('reg-prose');
            const keywordsInput = document.getElementById('reg-keywords');

            if (titleInput) {
                titleInput.value = title;
            }

            if (!slug) {
                if (proseInput) proseInput.value = "";
                if (keywordsInput) keywordsInput.value = "";
                return;
            }

            // Fetch subtopic details to auto-populate prose & keywords
            if (proseInput) {
                proseInput.value = "Loading description...";
            }
            if (keywordsInput) {
                keywordsInput.value = "Extracting key terms...";
            }

            fetch(BASE_URL + '/physics/admin/api/get-subtopic/' + slug)
                .then(res => res.json())
                .then(data => {
                    if (data.success && data.subtopic) {
                        const snippet = data.subtopic.snippet || '';
                        
                        if (proseInput) {
                            proseInput.value = snippet;
                        }
                        if (keywordsInput) {
                            keywordsInput.value = extractKeywords(snippet || data.subtopic.content || '');
                        }
                    } else {
                        if (proseInput) proseInput.value = "";
                        if (keywordsInput) keywordsInput.value = "";
                    }
                })
                .catch(err => {
                    console.error("Error fetching subtopic:", err);
                    if (proseInput) proseInput.value = "";
                    if (keywordsInput) keywordsInput.value = "";
                });
        });
    }

    if (form) {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const slug = document.getElementById('reg-slug').value;
            const title = document.getElementById('reg-title').value;
            const prose = document.getElementById('reg-prose').value;
            const keywords = document.getElementById('reg-keywords').value;

            if (!slug || !title || !prose || !keywords) {
                if (errorDiv) {
                    errorDiv.textContent = 'All fields are required.';
                    errorDiv.style.display = 'block';
                }
                return;
            }

            const submitBtn = document.getElementById('btn-submit-register');
            if (submitBtn) {
                submitBtn.disabled = true;
            }

            fetch(BASE_URL + '/physics/admin/api/register-reference', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    slug: slug,
                    title: title,
                    reference_prose: prose,
                    keywords: keywords
                })
            })
            .then(res => res.json())
            .then(data => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
                if (data.success) {
                    closeModal();
                    window.location.reload();
                } else {
                    if (errorDiv) {
                        errorDiv.textContent = data.error || 'Failed to register reference.';
                        errorDiv.style.display = 'block';
                    }
                }
            })
            .catch(err => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
                if (errorDiv) {
                    errorDiv.textContent = 'Network error: ' + err;
                    errorDiv.style.display = 'block';
                }
            });
        });
    }
});
</script>

<style nonce="<?= $nonce ?>">
#btn-close-register-modal {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.5rem;
    cursor: pointer;
    transition: color 0.2s;
}
#btn-close-register-modal:hover {
    color: #ffffff !important;
}
</style>

<!-- Modal Container -->
<div id="register-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.6); z-index: 10000; align-items: center; justify-content: center; backdrop-filter: blur(8px);">
    <div class="glass-panel" style="width: 550px; max-width: 90%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); border: 1px solid rgba(255, 255, 255, 0.1);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <h3 style="margin: 0; font-family: 'Space Grotesk', sans-serif;">Register Reference Topic</h3>
            <button id="btn-close-register-modal">&times;</button>
        </div>
        
        <form id="register-reference-form" style="display: flex; flex-direction: column; gap: 15px;">
            <div style="display: flex; flex-direction: column; gap: 6px;">
                <label for="reg-slug" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">Select Subtopic Slug</label>
                <select id="reg-slug" name="slug" style="background: #090a0d; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 12px; color: #ffffff; width: 100%; font-size: 0.9rem; cursor: pointer;">
                    <option value="">-- Select an unregistered subtopic --</option>
                    <?php foreach ($unregisteredSubtopics as $sub): ?>
                        <option value="<?= htmlspecialchars($sub['slug']) ?>" data-title="<?= htmlspecialchars($sub['title']) ?>">
                            <?= htmlspecialchars($sub['title']) ?> (<?= htmlspecialchars($sub['slug']) ?>)
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div style="display: flex; flex-direction: column; gap: 6px;">
                <label for="reg-title" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">Reference Title</label>
                <input type="text" id="reg-title" name="title" placeholder="e.g. Energy-Momentum Relation" style="background: #090a0d; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 12px; color: #ffffff; width: 100%; font-size: 0.9rem;">
            </div>

            <div style="display: flex; flex-direction: column; gap: 6px;">
                <label for="reg-prose" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">Canonical Reference Prose (Textbook Standard)</label>
                <textarea id="reg-prose" name="reference_prose" rows="5" placeholder="Enter textbook prose standard for this subtopic..." style="background: #090a0d; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 12px; color: #ffffff; width: 100%; font-size: 0.9rem; resize: vertical; font-family: inherit; line-height: 1.5;"></textarea>
            </div>

            <div style="display: flex; flex-direction: column; gap: 6px;">
                <label for="reg-keywords" style="font-size: 0.85rem; color: var(--text-muted); font-weight: 500;">Key Technical Terms (Comma-separated)</label>
                <input type="text" id="reg-keywords" name="keywords" placeholder="e.g. energy, momentum, mass, invariant" style="background: #090a0d; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; padding: 8px 12px; color: #ffffff; width: 100%; font-size: 0.9rem;">
            </div>

            <div id="register-error" style="color: #ff5f56; font-size: 0.85rem; display: none; margin-top: 5px;"></div>

            <div style="display: flex; justify-content: flex-end; gap: 10px; margin-top: 10px;">
                <button type="button" id="btn-cancel-register" class="btn-action">Cancel</button>
                <button type="submit" id="btn-submit-register" class="btn-action primary">Register Reference</button>
            </div>
        </form>
    </div>
</div>
