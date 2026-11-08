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

    // Load Search Index (Lazily invoked only when offline fallback search is needed)
    let indexLoadPromise = null;
    async function loadIndex() {
        if (searchData) return searchData;
        if (indexLoadPromise) return indexLoadPromise;
        indexLoadPromise = (async () => {
            try {
                const response = await fetch('/physics/search-index');
                if (!response.ok) throw new Error('Search index load failed');
                searchData = await response.json();
                return searchData;
            } catch (e) {
                console.error('Search Index Error:', e);
                return null;
            } finally {
                indexLoadPromise = null;
            }
        })();
        return indexLoadPromise;
    }

    let activeSearchController = null;

    // Modal Control Functions
    function openModal() {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Lock background scrolling
        setTimeout(() => input.focus(), 50); // Autofocus input field
        highlightedIndex = -1;
    }

    function closeModal() {
        if (activeSearchController) {
            activeSearchController.abort();
            activeSearchController = null;
        }
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

    let debounceTimer = null;

    // Offline client-side fallback search (lazily loads /physics/search-index only if API fails)
    async function performFallbackSearch(query) {
        const index = await loadIndex();
        if (!index) {
            results.innerHTML = '<div class="search-placeholder"><p>Search currently unavailable</p><small>Please check your connection and try again.</small></div>';
            resultItems = [];
            highlightedIndex = -1;
            return;
        }

        const qLower = query.toLowerCase();
        const matches = [];
        for (const [slug, entry] of Object.entries(index)) {
            const title = entry.t || slug;
            const keywords = Array.isArray(entry.k) ? entry.k : [];
            const titleMatch = title.toLowerCase().includes(qLower) || slug.toLowerCase().includes(qLower);
            const kwMatch = keywords.some(k => String(k).toLowerCase().includes(qLower));
            if (titleMatch || kwMatch) {
                matches.push({
                    url: `/physics/subtopic/${slug}`,
                    title,
                    type: 'Subtopic',
                    snippet: formatPath(entry.p)
                });
                if (matches.length >= 10) break;
            }
        }

        if (matches.length > 0) {
            results.innerHTML = matches.map(m => `
                <a href="${m.url}" class="modal-search-item">
                    <div class="modal-search-item-header">
                        <span class="modal-search-item-title">${m.title}</span>
                        <span class="modal-search-item-badge">${m.type}</span>
                    </div>
                    <div class="modal-search-item-path">
                        <span>${m.snippet}</span>
                    </div>
                </a>
            `).join('');

            resultItems = Array.from(results.querySelectorAll('.modal-search-item'));
            highlightedIndex = 0;
            updateHighlight();

            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([results]).catch(err => console.warn('MathJax preview error:', err));
            }
        } else {
            results.innerHTML = '<div class="search-placeholder"><p>No matches in the manifold...</p><small>Try searching another physical concept or symbol.</small></div>';
            resultItems = [];
            highlightedIndex = -1;
        }
    }

    // Perform API search request
    async function performSearch(query) {
        if (activeSearchController) {
            activeSearchController.abort();
            activeSearchController = null;
        }

        if (query.length < 2) {
            resetResultsPlaceholder();
            resultItems = [];
            highlightedIndex = -1;
            return;
        }

        const controller = new AbortController();
        activeSearchController = controller;
        const { signal } = controller;

        try {
            const response = await fetch(`/physics/api/search?q=${encodeURIComponent(query)}&limit=10`, { signal });
            if (!response.ok) throw new Error('API search failed');
            const data = await response.json();
            
            if (data.results && data.results.length > 0) {
                results.innerHTML = data.results.map(m => `
                    <a href="${m.url}" class="modal-search-item">
                        <div class="modal-search-item-header">
                            <span class="modal-search-item-title">${m.title}</span>
                            <span class="modal-search-item-badge">${m.type}</span>
                        </div>
                        <div class="modal-search-item-path">
                            <span>${m.snippet}</span>
                        </div>
                    </a>
                `).join('');

                resultItems = Array.from(results.querySelectorAll('.modal-search-item'));
                highlightedIndex = 0;
                updateHighlight();

                if (window.MathJax && window.MathJax.typesetPromise) {
                    window.MathJax.typesetPromise([results]).catch(err => console.warn('MathJax preview error:', err));
                }
            } else {
                // Try AI Semantic Vector Search Fallback
                try {
                    const semRes = await fetch(`/physics/api/semantic-search?q=${encodeURIComponent(query)}&limit=8`, { signal });
                    if (semRes.ok) {
                        const semData = await semRes.json();
                        if (semData.results && semData.results.length > 0) {
                            results.innerHTML = semData.results.map(m => `
                                <a href="${m.url}" class="modal-search-item">
                                    <div class="modal-search-item-header">
                                        <span class="modal-search-item-title">${m.title}</span>
                                        <div style="display: flex; gap: 6px; align-items: center;">
                                            ${m.domain ? `<span class="modal-search-item-badge" style="background: rgba(255, 255, 255, 0.05); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.1);">${m.domain}</span>` : ''}
                                            <span class="modal-search-item-badge" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3);">✨ ${m.confidence} AI Match</span>
                                        </div>
                                    </div>
                                    <div class="modal-search-item-path">
                                        <span>${m.snippet || ''}</span>
                                    </div>
                                </a>
                            `).join('');

                            resultItems = Array.from(results.querySelectorAll('.modal-search-item'));
                            highlightedIndex = 0;
                            updateHighlight();

                            if (window.MathJax && window.MathJax.typesetPromise) {
                                window.MathJax.typesetPromise([results]).catch(err => console.warn('MathJax preview error:', err));
                            }
                            return;
                        }
                    }
                } catch (semErr) {
                    if (semErr && semErr.name === 'AbortError') return;
                    console.warn('Semantic search fallback failed:', semErr);
                }

                results.innerHTML = '<div class="search-placeholder"><p>No matches in the manifold...</p><small>Try searching another physical concept or symbol.</small></div>';
                resultItems = [];
                highlightedIndex = -1;
            }
        } catch (err) {
            if (err && err.name === 'AbortError') return;
            console.warn('API search failed, attempting fallback index...', err);
            await performFallbackSearch(query);
        }
    }

    // Input Searching logic with 250ms debounce
    input.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => performSearch(query), 250);
    });

    // Handle background search query parameter pre-fill
    const urlParams = new URLSearchParams(window.location.search);
    const searchQuery = urlParams.get('search');
    if (searchQuery) {
        openModal();
        input.value = searchQuery;
        performSearch(searchQuery.trim());
    }
});
