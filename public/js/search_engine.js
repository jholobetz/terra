document.addEventListener('DOMContentLoaded', () => {
    // Spotlight Search Modal DOM Elements
    const trigger = document.getElementById('search-modal-trigger');
    const modal = document.getElementById('search-modal');
    const input = document.getElementById('modal-search-input');
    const results = document.getElementById('modal-search-results');
    const closeBtn = document.querySelector('.close-modal-btn');
    const backdrop = document.querySelector('.search-modal-backdrop');
    
    let searchData = null;
    let highlightedIndex = -1;
    let resultItems = [];

    if (!modal || !input) return;

    // Helper: format pathway breadcrumbs nicely (e.g., quantum-physics -> Quantum Physics)
    function formatPath(pathArray) {
        if (!pathArray || !Array.isArray(pathArray)) return '';
        return pathArray.map(slug => 
            slug.split('-')
                .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                .join(' ')
        ).join(' &rsaquo; ');
    }

    // Load Search Index
    async function loadIndex() {
        if (searchData) return;
        input.placeholder = "Loading encyclopedia index...";
        try {
            const response = await fetch('/physics/search-index');
            if (!response.ok) throw new Error('Search index load failed');
            searchData = await response.json();
            input.placeholder = "Search equations, topics, and constants...";
            console.log('Spotlight Search Engine initialized:', Object.keys(searchData).length, 'topics indexed.');
        } catch (e) {
            input.placeholder = "Search currently unavailable";
            console.error('Search Index Error:', e);
        }
    }

    // Modal Control Functions
    function openModal() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Lock background scrolling
        loadIndex();
        setTimeout(() => input.focus(), 50); // Autofocus input field
        highlightedIndex = -1;
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
        input.value = '';
        resetResultsPlaceholder();
        highlightedIndex = -1;
    }

    function resetResultsPlaceholder() {
        results.innerHTML = `
            <div class="search-placeholder">
                <p>Search the mathematical manifold</p>
                <small>Type to search subtopics, physical constants, or defining equations...</small>
            </div>
        `;
    }

    // Trigger Listeners
    if (trigger) trigger.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (backdrop) backdrop.addEventListener('click', closeModal);

    // Global Hotkeys (Cmd+K / Ctrl+K and Escape)
    document.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            if (modal.classList.contains('active')) {
                closeModal();
            } else {
                openModal();
            }
        }
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Keyboard Arrow Navigation
    input.addEventListener('keydown', (e) => {
        if (!modal.classList.contains('active') || resultItems.length === 0) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            highlightedIndex = (highlightedIndex + 1) % resultItems.length;
            updateHighlight();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            highlightedIndex = (highlightedIndex - 1 + resultItems.length) % resultItems.length;
            updateHighlight();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const activeIndex = highlightedIndex >= 0 ? highlightedIndex : 0;
            if (resultItems[activeIndex]) {
                resultItems[activeIndex].click();
            }
        }
    });

    function updateHighlight() {
        resultItems.forEach((item, index) => {
            if (index === highlightedIndex) {
                item.classList.add('highlighted');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('highlighted');
            }
        });
    }

    // Input Searching logic
    input.addEventListener('input', (e) => {
        if (!searchData) return;
        
        const query = e.target.value.toLowerCase().trim();
        const cleanQuery = query.replace(/[''s]/g, ''); 
        
        if (query.length < 2) {
            resetResultsPlaceholder();
            resultItems = [];
            highlightedIndex = -1;
            return;
        }

        const scoredMatches = [];
        for (const [slug, data] of Object.entries(searchData)) {
            let score = 0;
            const title = data.t.toLowerCase();
            const cleanTitle = title.replace(/[''s]/g, '');

            // 1. Base Score (Title matching)
            if (title === query || cleanTitle === cleanQuery) score += 1000;
            else if (title.startsWith(query) || cleanTitle.startsWith(cleanQuery)) score += 800;
            else if (title.includes(query) || cleanTitle.includes(cleanQuery)) score += 500;
            else if (data.k && data.k.some(k => k.toLowerCase().includes(query))) score += 200;

            if (score > 0) {
                // 2. Density weight bonus
                score += (data.w || 0) * 0.5;

                // 3. Platinum Standard Bonus
                if (data.pl) score *= 1.2;

                scoredMatches.push({ slug, score, ...data });
            }
        }

        // Sort by score descending, then by title length
        scoredMatches.sort((a, b) => b.score - a.score || a.t.length - b.t.length);

        if (scoredMatches.length > 0) {
            const limited = scoredMatches.slice(0, 10);
            results.innerHTML = limited.map(m => `
                <a href="/physics/subtopic/${m.slug}" class="modal-search-item">
                    <div class="modal-search-item-header">
                        <span class="modal-search-item-title">${m.t}</span>
                        ${m.pl ? '<span class="modal-search-item-badge">Platinum</span>' : ''}
                    </div>
                    <div class="modal-search-item-path">
                        <span>${formatPath(m.p)}</span>
                        ${m.s ? `<span style="opacity:0.4;">&bull; ${m.s.replace('.json', '')}</span>` : ''}
                    </div>
                </a>
            `).join('');

            // Collect items for arrow navigation
            resultItems = Array.from(results.querySelectorAll('.modal-search-item'));
            highlightedIndex = 0;
            updateHighlight();

            // Render MathJax equations in search results dynamically!
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([results]).catch(err => console.warn('MathJax preview error:', err));
            }
        } else {
            results.innerHTML = '<div class="search-placeholder"><p>No matches in the manifold...</p><small>Try searching another physical concept or symbol.</small></div>';
            resultItems = [];
            highlightedIndex = -1;
        }
    });

    // Handle background search query parameter pre-fill
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        openModal();
        input.value = searchQuery;
        
        // Wait for the index to load before running search query
        const checkIndex = setInterval(() => {
            if (searchData) {
                clearInterval(checkIndex);
                input.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }, 50);
        setTimeout(() => clearInterval(checkIndex), 3000);
    }
});
