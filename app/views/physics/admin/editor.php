<?php
// Admin WYSIWYG Editor view
?>

<div class="admin-editor-container" style="padding: 10px 0 40px 0;">
    <!-- Premium Header -->
    <header class="simulations-header" style="margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px; display: flex; justify-content: space-between; align-items: flex-end;">
        <div>
            <h1 style="font-size: 3rem; margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 50%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                <?= htmlspecialchars($title) ?>
            </h1>
            <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 650px;">
                Draft and edit encyclopedia shards in real-time under organic quality gate supervision.
            </p>
        </div>
        <div style="display: flex; gap: 12px; margin-bottom: 5px;">
            <a href="/physics/admin/dashboard" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                <span>📊 Dashboard</span>
            </a>
            <a href="/physics/admin/critic" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1);">
                <span>🧑‍🔬 Critic Portal</span>
            </a>
        </div>
    </header>

    <!-- Editor Workspace Grid -->
    <div style="display: grid; grid-template-columns: 280px 1.2fr 1fr; gap: 25px; height: 75vh;">
        <!-- Left Pane: Shard Draft Selector & Metadata -->
        <div class="glass-panel" style="display: flex; flex-direction: column; gap: 15px; height: 100%; overflow-y: auto;">
            <h4 style="margin: 0; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: var(--text-muted);">
                Active Ingestion Drafts
            </h4>
            
            <div style="display: flex; flex-direction: column; gap: 8px;">
                <select id="draft-selector" onchange="loadSelectedDraft()" style="width: 100%; background: #0f1015; border: 1px solid rgba(255,255,255,0.1); border-radius: 6px; padding: 10px; color: #ffffff; font-size: 0.95rem;">
                    <option value="">-- Create New Draft --</option>
                    <?php foreach ($payloads as $slug => $data): ?>
                        <option value="<?= htmlspecialchars($slug) ?>"><?= htmlspecialchars($slug) ?> (<?= htmlspecialchars($data['title']) ?>)</option>
                    <?php endforeach; ?>
                </select>
            </div>

            <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px; display: flex; flex-direction: column; gap: 8px;">
                <label class="meta-label">Load Existing Subtopic</label>
                <div style="display: flex; gap: 8px;">
                    <input type="text" id="existing-slug-input" list="existing-slugs" placeholder="Search subtopics..." style="flex: 1; min-width: 0;" class="meta-input">
                    <datalist id="existing-slugs">
                        <?php foreach ($slugs as $slugSlug): ?>
                            <option value="<?= htmlspecialchars($slugSlug) ?>"></option>
                        <?php endforeach; ?>
                    </datalist>
                    <button onclick="loadExistingSubtopic()" class="btn btn-secondary" style="border: 1px solid rgba(255,255,255,0.1); padding: 8px 12px; font-size: 0.9rem; cursor: pointer;">
                        Load
                    </button>
                </div>
            </div>

            <div style="border-top: 1px solid rgba(255,255,255,0.05); padding-top: 15px; display: flex; flex-direction: column; gap: 12px;">
                <div>
                    <label class="meta-label">Subtopic Slug</label>
                    <input type="text" id="node-slug" placeholder="e.g. conservation-laws" style="width: 100%;" class="meta-input">
                </div>
                <div>
                    <label class="meta-label">Subtopic Title</label>
                    <input type="text" id="node-title" placeholder="e.g. Conservation Laws" style="width: 100%;" class="meta-input">
                </div>
                <div>
                    <label class="meta-label">Parent Hub</label>
                    <input type="text" id="node-parent" placeholder="e.g. classical-mechanics" style="width: 100%;" class="meta-input">
                </div>
                <div>
                    <label class="meta-label">Key Math Identity (ID)</label>
                    <input type="text" id="node-identity-id" placeholder="e.g. mass-energy-rel" style="width: 100%;" class="meta-input">
                </div>
                <div>
                    <label class="meta-label">Math Identity Equation (LaTeX)</label>
                    <textarea id="node-identity-eq" placeholder="E = m c^2" style="width: 100%; height: 60px; font-family: monospace;" class="meta-input"></textarea>
                </div>
            </div>

            <button onclick="saveDraft()" class="btn btn-primary" style="margin-top: auto; width: 100%; font-weight: 600;">
                💾 Save Staged Draft
            </button>
        </div>

        <!-- Center Pane: Rich HTML Editor -->
        <div class="glass-panel" style="display: flex; flex-direction: column; padding: 15px; height: 100%;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: var(--text-muted);">
                    HTML Prose Editor
                </h4>
                <span style="font-size: 0.8rem; color: var(--text-muted);">Wrap paragraphs in &lt;p&gt; tags</span>
            </div>
            <textarea id="prose-editor" oninput="updateEditorMetrics()" placeholder="<p>The invariance of the spacetime interval...</p>" style="flex: 1; width: 100%; background: #07080b; border: 1px solid rgba(255,255,255,0.05); border-radius: 8px; padding: 15px; color: #e0e0e0; font-family: 'Fira Code', monospace; font-size: 0.9rem; line-height: 1.5; resize: none;"></textarea>
        </div>

        <!-- Right Pane: Live Preview & Scorecard Tabs -->
        <div style="display: flex; flex-direction: column; gap: 20px; height: 100%;">
            <!-- Scorecard panel -->
            <div class="glass-panel" style="padding: 18px;">
                <h4 style="margin: 0 0 15px 0; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: var(--text-muted);">
                    Live OPS Scorecard
                </h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.85rem;">
                    <!-- Word count indicator -->
                    <div class="score-indicator" id="indicator-words">
                        <span class="dot"></span>
                        <span class="label">Word Count: 0</span>
                    </div>
                    <!-- In media res indicator -->
                    <div class="score-indicator" id="indicator-lead">
                        <span class="dot"></span>
                        <span class="label">In Media Res Lead</span>
                    </div>
                    <!-- MathJax density indicator -->
                    <div class="score-indicator" id="indicator-density">
                        <span class="dot"></span>
                        <span class="label">Math Density (>=2/para)</span>
                    </div>
                    <!-- Continuous prose indicator -->
                    <div class="score-indicator" id="indicator-structure">
                        <span class="dot"></span>
                        <span class="label">Continuous Prose (No Lists)</span>
                    </div>
                </div>
            </div>

            <!-- Live HTML Rendering Viewport -->
            <div class="glass-panel" style="flex: 1; display: flex; flex-direction: column; overflow: hidden; padding: 18px;">
                <h4 style="margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.85rem; color: var(--text-muted);">
                    Live MathJax Render Preview
                </h4>
                <div id="render-preview" class="preview-viewport" style="flex: 1; overflow-y: auto; background: #07080b; border: 1px solid rgba(255,255,255,0.03); border-radius: 8px; padding: 15px; color: #f0f0f0; font-family: 'Inter', sans-serif; font-size: 1rem; line-height: 1.6;">
                    <p style="color: var(--text-muted); font-style: italic; text-align: center; margin-top: 50px;">Start typing in the editor to view the real-time typeset mathematical layout.</p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Load payloads as JS variable securely -->
<script nonce="<?= $nonce ?>">
const activeDrafts = <?= json_encode($payloads) ?>;
</script>

<style>
.glass-panel {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
}

.meta-label {
    display: block;
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-bottom: 5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: 'Space Grotesk', sans-serif;
}

.meta-input {
    background: #0f1015;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
    font-size: 0.9rem;
    box-sizing: border-box;
}

.meta-input:focus {
    border-color: var(--accent-default);
    outline: none;
}

.score-indicator {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255,255,255,0.03);
    border-radius: 6px;
    padding: 8px 10px;
}

.score-indicator .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #ff5555; /* Default fail red */
    display: inline-block;
    box-shadow: 0 0 6px #ff5555;
}

.score-indicator.pass .dot {
    background: #55ff55;
    box-shadow: 0 0 6px #55ff55;
}

.score-indicator.warning .dot {
    background: #ffcc00;
    box-shadow: 0 0 6px #ffcc00;
}

.preview-viewport p {
    margin: 0 0 20px 0;
}

.preview-viewport strong {
    color: var(--accent-default);
}
</style>

<script nonce="<?= $nonce ?>">
let typesetTimeout = null;

function loadSelectedDraft() {
    const selector = document.getElementById('draft-selector');
    const slug = selector.value;
    
    const slugInput = document.getElementById('node-slug');
    const titleInput = document.getElementById('node-title');
    const parentInput = document.getElementById('node-parent');
    const idInput = document.getElementById('node-identity-id');
    const eqInput = document.getElementById('node-identity-eq');
    const editor = document.getElementById('prose-editor');

    if (slug && activeDrafts[slug]) {
        const d = activeDrafts[slug];
        slugInput.value = slug;
        slugInput.readOnly = true;
        titleInput.value = d.title || '';
        parentInput.value = (d.parents && d.parents[0]) ? d.parents[0] : '';
        editor.value = d.content || '';
        
        if (d.identities && d.identities[0]) {
            idInput.value = d.identities[0].id || '';
            eqInput.value = d.identities[0].equation || '';
        } else {
            idInput.value = '';
            eqInput.value = '';
        }
    } else {
        slugInput.value = '';
        slugInput.readOnly = false;
        titleInput.value = '';
        parentInput.value = '';
        editor.value = '';
        idInput.value = '';
        eqInput.value = '';
    }
    
    updateEditorMetrics();
}

function updateEditorMetrics() {
    const editor = document.getElementById('prose-editor');
    const text = editor.value;
    
    const preview = document.getElementById('render-preview');
    if (text.trim() === '') {
        preview.innerHTML = '<p style="color: var(--text-muted); font-style: italic; text-align: center; margin-top: 50px;">Start typing in the editor to view the real-time typeset mathematical layout.</p>';
        resetIndicators();
        return;
    }

    // Update Live Preview
    preview.innerHTML = text;
    
    // Throttle MathJax typeset updates to prevent keypress lag
    if (typesetTimeout) clearTimeout(typesetTimeout);
    typesetTimeout = setTimeout(() => {
        if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise([preview]).catch(err => console.log('MathJax typeset error:', err));
        }
    }, 500);

    // Evaluate Quality Gate Metrics
    // 1. Word Count (excluding HTML tags and LaTeX math blocks)
    let cleanText = text.replace(/<[^>]+>/g, ' '); // Strip HTML
    cleanText = cleanText.replace(/\\\(.*?\\\)/g, ' '); // Strip inline LaTeX
    cleanText = cleanText.replace(/\\\[.*?\\\]/g, ' '); // Strip display LaTeX
    const words = cleanText.trim().split(/\s+/).filter(w => w.length > 0);
    const wordCount = words.length;

    const indWords = document.getElementById('indicator-words');
    indWords.querySelector('.label').textContent = 'Word Count: ' + wordCount;
    if (wordCount >= 650 && wordCount <= 1000) {
        indWords.className = 'score-indicator pass';
    } else if (wordCount > 0 && wordCount < 650) {
        indWords.className = 'score-indicator warning'; // warn for small drafts
    } else {
        indWords.className = 'score-indicator';
    }

    // 2. In Media Res Lead Rule
    const indLead = document.getElementById('indicator-lead');
    const firstParaMatch = text.match(/<p>(.*?)<\/p>/);
    if (firstParaMatch) {
        const firstPara = firstParaMatch[1].toLowerCase().replace(/<[^>]+>/g, '');
        const bannedPrefixes = ['the ', 'this ', 'in this', 'a ', 'an '];
        const hasBannedPrefix = bannedPrefixes.some(pref => firstPara.startsWith(pref));
        
        // Also check if title is in first 15 words
        const titleVal = document.getElementById('node-title').value.toLowerCase();
        const first15 = firstPara.split(/\s+/).slice(0, 15).join(' ');
        const containsTitle = titleVal && first15.includes(titleVal);

        if (!hasBannedPrefix && !containsTitle) {
            indLead.className = 'score-indicator pass';
        } else {
            indLead.className = 'score-indicator';
        }
    } else {
        indLead.className = 'score-indicator';
    }

    // 3. MathJax Density (At least 2 inline math elements per paragraph)
    const indDensity = document.getElementById('indicator-density');
    const paragraphs = text.match(/<p>.*?<\/p>/g) || [];
    let densityPass = paragraphs.length > 0;
    
    for (let p of paragraphs) {
        const openMatches = p.match(/\\\(/g) || [];
        const closeMatches = p.match(/\\\)/g) || [];
        const mathCount = Math.min(openMatches.length, closeMatches.length);
        if (mathCount < 2) {
            densityPass = false;
            break;
        }
    }
    
    if (densityPass && paragraphs.length > 0) {
        indDensity.className = 'score-indicator pass';
    } else {
        indDensity.className = 'score-indicator';
    }

    // 4. Continuous Prose (No lists)
    const indStructure = document.getElementById('indicator-structure');
    const hasLists = /<(ul|ol|li)\b/i.test(text);
    if (!hasLists && text.trim().length > 0) {
        indStructure.className = 'score-indicator pass';
    } else {
        indStructure.className = 'score-indicator';
    }
}

function resetIndicators() {
    document.getElementById('indicator-words').className = 'score-indicator';
    document.getElementById('indicator-words').querySelector('.label').textContent = 'Word Count: 0';
    document.getElementById('indicator-lead').className = 'score-indicator';
    document.getElementById('indicator-density').className = 'score-indicator';
    document.getElementById('indicator-structure').className = 'score-indicator';
}

function saveDraft() {
    const slug = document.getElementById('node-slug').value.trim();
    const title = document.getElementById('node-title').value.trim();
    const parent = document.getElementById('node-parent').value.trim();
    const id = document.getElementById('node-identity-id').value.trim();
    const equation = document.getElementById('node-identity-eq').value.trim();
    const content = document.getElementById('prose-editor').value.trim();

    if (!slug || !content) {
        alert('Error: Slug and HTML content are required to save a draft.');
        return;
    }

    const identities = [];
    if (id && equation) {
        identities.push({ id, title, equation });
    }

    const payload = {
        slug,
        title,
        content,
        parents: parent ? [parent] : [],
        identities
    };

    fetch(BASE_URL + '/physics/admin/api/save-draft', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('✓ SUCCESS: Draft [' + slug + '] successfully saved to subfiles/batch_payload.json.');
            window.location.reload(); // Refresh to update selectors
        } else {
            alert('❌ ERROR: ' + data.error);
        }
    })
    .catch(err => {
        alert('Error saving draft: ' + err);
    });
}

function loadExistingSubtopic() {
    const slug = document.getElementById('existing-slug-input').value.trim();
    if (!slug) {
        alert('Please select or type a subtopic slug first.');
        return;
    }

    fetch(BASE_URL + '/physics/admin/api/get-subtopic/' + slug)
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            const s = data.subtopic;
            document.getElementById('draft-selector').value = ''; // Reset draft selector
            
            const slugInput = document.getElementById('node-slug');
            slugInput.value = s.slug;
            slugInput.readOnly = true; // Prevent changing slug of existing node directly
            
            document.getElementById('node-title').value = s.title || '';
            document.getElementById('node-parent').value = (s.parents && s.parents[0]) ? s.parents[0] : '';
            document.getElementById('prose-editor').value = s.content || '';
            
            if (s.identities && s.identities[0]) {
                document.getElementById('node-identity-id').value = s.identities[0].id || '';
                document.getElementById('node-identity-eq').value = s.identities[0].equation || '';
            } else {
                document.getElementById('node-identity-id').value = '';
                document.getElementById('node-identity-eq').value = '';
            }
            
            updateEditorMetrics();
            alert('✓ Loaded existing subtopic [' + slug + '] into editor.');
        } else {
            alert('❌ Error: ' + data.error);
        }
    })
    .catch(err => {
        alert('Error loading subtopic: ' + err);
    });
}
</script>
