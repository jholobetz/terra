<?php
$counts = [
    'all' => count($notation),
    'constant' => 0,
    'variable' => 0,
    'tensor' => 0,
    'vector' => 0,
    'operator' => 0
];
foreach ($notation as $item) {
    $type = $item['type'] ?? 'variable';
    if (isset($counts[$type])) {
        $counts[$type]++;
    } elseif ($type === 'variable-state' || $type === 'density') {
        $counts['variable']++;
    }
}
?>
<article class="physics-page" style="--accent-color: var(--accent-default);">
    <header class="page-header">
        <span class="category-tag">Fundamental Reference</span>
        <h1>Fundamental Symbols & Notation Reference</h1>
        <p class="lead-prose">
            The mathematical language of the physical universe. This unified reference catalog lists the variables, operators, tensors, and constants that structure the equations of physics.
        </p>
    </header>

    <div class="search-and-filter-wrapper" style="margin-top: 30px; margin-bottom: 30px; display: flex; flex-direction: column; gap: 20px;">
        <div class="search-container" style="position: relative; max-width: 500px; width: 100%;">
            <input type="text" id="notation-search" placeholder="Search by name, symbol, or description..." style="width: 100%; padding: 12px 20px 12px 45px; font-size: 0.95rem; border-radius: 8px; border: 1px solid #233554; background: rgba(17, 34, 64, 0.6); color: #fff; box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.2); outline: none; transition: border-color 0.2s, box-shadow 0.2s;" />
            <svg class="search-icon" style="position: absolute; left: 15px; top: 50%; transform: translateY(-50%); width: 18px; height: 18px; fill: #8892b0;" viewBox="0 0 24 24">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <span class="search-clear" id="search-clear-btn" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); cursor: pointer; color: #8892b0; font-weight: bold; font-size: 1.2rem; display: none; transition: color 0.2s;">&times;</span>
        </div>

        <div class="notation-filter" style="display: flex; flex-wrap: wrap; gap: 10px;">
            <button class="btn btn-secondary filter-btn active" data-type="all">All Notation <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['all'] ?>)</span></button>
            <button class="btn btn-secondary filter-btn" data-type="constant">Constants <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['constant'] ?>)</span></button>
            <button class="btn btn-secondary filter-btn" data-type="variable">Variables <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['variable'] ?>)</span></button>
            <button class="btn btn-secondary filter-btn" data-type="tensor">Tensors <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['tensor'] ?>)</span></button>
            <button class="btn btn-secondary filter-btn" data-type="vector">Vectors <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['vector'] ?>)</span></button>
            <button class="btn btn-secondary filter-btn" data-type="operator">Operators <span class="filter-count" style="opacity: 0.6; font-size: 0.8em; margin-left: 4px;">(<?= $counts['operator'] ?>)</span></button>
        </div>
    </div>

    <div class="notation-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 25px;">
        <?php foreach ($notation as $slug => $item): 
            $type = $item['type'] ?? 'variable';
            $originSlug = $item['origin_subtopic'] ?? '';
            $originUrl = $originSlug ? '/physics/subtopic/' . $originSlug : '';
        ?>
            <section class="notation-card" data-type="<?= $type ?>" data-symbol="<?= htmlspecialchars($item['symbol']) ?>" id="<?= $slug ?>" style="background: #112240; border: 1px solid #233554; border-radius: 12px; padding: 25px; transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease; position: relative;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; gap: 15px;">
                    <div>
                        <h3 style="margin: 0; font-size: 1.25rem; color: #fff;"><?= htmlspecialchars($item['name']) ?></h3>
                        <span style="font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1px; color: var(--accent-color); font-weight: bold; margin-top: 4px; display: inline-block;">
                            <?= htmlspecialchars(str_replace('-', ' ', $type)) ?>
                        </span>
                    </div>
                    <span class="symbol-container" data-symbol="<?= htmlspecialchars($item['symbol']) ?>" style="background: rgba(100, 255, 218, 0.08); color: var(--accent-color); padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 1.15rem; display: inline-block; white-space: nowrap;">
                        \( <?= $item['symbol'] ?> \)
                    </span>
                </div>
                
                <div class="notation-meta" style="margin-bottom: 15px; font-size: 0.85rem; font-family: 'JetBrains Mono', monospace; color: #8892b0;">
                    <?php if ($type === 'constant' && isset($item['value'])): ?>
                        <span style="color: #fff; word-break: break-all;">Value: <?= htmlspecialchars($item['value']) ?> <?= htmlspecialchars($item['unit'] ?? '') ?></span>
                    <?php elseif (isset($item['dimensions'])): ?>
                        <span>Dimensions: <?= htmlspecialchars($item['dimensions']) ?></span>
                    <?php endif; ?>
                </div>

                <p style="margin: 0 0 15px 0; font-size: 0.92rem; color: #ccd6f6; line-height: 1.5;">
                    <?= htmlspecialchars($item['description']) ?>
                </p>

                <?php if ($originUrl): ?>
                    <div style="font-size: 0.82rem; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 12px; margin-top: 10px;">
                        <span style="color: #8892b0;">Origin: </span>
                        <a href="<?= $originUrl ?>" class="subtopic-link" style="color: var(--accent-color); text-decoration: none; font-weight: bold;"><strong><?= htmlspecialchars(ucwords(str_replace('-', ' ', $originSlug))) ?></strong></a>
                    </div>
                <?php endif; ?>
            </section>
        <?php endforeach; ?>
    </div>

    <footer style="margin-top: 60px; padding-top: 30px; border-top: 1px solid #233554; text-align: center;">
        <a href="/physics" class="btn btn-secondary">&larr; Back to Lab Home</a>
    </footer>
</article>

<style>
    #notation-search:focus {
        border-color: var(--accent-color) !important;
        box-shadow: 0 0 10px rgba(100, 255, 218, 0.15) !important;
    }
    .search-clear:hover {
        color: #fff !important;
    }
    .notation-card:hover {
        transform: translateY(-4px);
        border-color: var(--accent-color);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    .notation-card:target {
        border-color: var(--accent-color);
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.15);
    }
    .filter-btn {
        font-size: 0.8rem !important;
        padding: 6px 14px !important;
        border-radius: 20px !important;
        display: flex;
        align-items: center;
        transition: all 0.2s ease-in-out;
    }
    .filter-btn.active {
        background: var(--accent-color) !important;
        color: #0a192f !important;
        border-color: var(--accent-color) !important;
        font-weight: 700;
    }
    
    @keyframes cardFadeIn {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>

<script nonce="<?= $nonce ?>">
document.addEventListener('DOMContentLoaded', () => {
    const filterButtons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.notation-card');
    const searchInput = document.getElementById('notation-search');
    const clearBtn = document.getElementById('search-clear-btn');

    let currentFilter = 'all';

    function updateFilters() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
        
        // Show/hide clear button
        if (clearBtn) {
            clearBtn.style.display = query.length > 0 ? 'block' : 'none';
        }

        cards.forEach(card => {
            try {
                const cardType = card.getAttribute('data-type') || '';
                const h3 = card.querySelector('h3');
                const cardName = h3 ? h3.textContent.toLowerCase() : '';
                const cardSymbol = (card.getAttribute('data-symbol') || '').toLowerCase();
                const p = card.querySelector('p');
                const cardDesc = p ? p.textContent.toLowerCase() : '';

                // Type filtering
                let typeMatches = false;
                if (currentFilter === 'all') {
                    typeMatches = true;
                } else if (currentFilter === 'variable') {
                    // Match any variable variations and density
                    typeMatches = cardType.includes('variable') || cardType === 'density';
                } else {
                    typeMatches = cardType === currentFilter;
                }

                // Search filtering
                const searchMatches = !query || 
                                      cardName.includes(query) || 
                                      cardSymbol.includes(query) || 
                                      cardDesc.includes(query);

                if (typeMatches && searchMatches) {
                    if (card.style.display === 'none' || !card.style.display) {
                        card.style.display = 'block';
                        card.style.animation = 'none';
                        card.offsetHeight; // trigger reflow
                        card.style.animation = 'cardFadeIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards';
                        
                        // Clean up animation on finish to allow smooth hover transitions
                        card.addEventListener('animationend', () => {
                            card.style.animation = '';
                        }, { once: true });
                    }
                } else {
                    card.style.display = 'none';
                }
            } catch (e) {
                console.error("Error updating card filters:", e);
            }
        });
    }

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.getAttribute('data-type');
            updateFilters();
        });
    });

    searchInput.addEventListener('input', updateFilters);

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        updateFilters();
        searchInput.focus();
    });
});
</script>
