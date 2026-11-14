(function() {
    'use strict';

    function initSimulationsDirectory() {
        const searchInput = document.getElementById('sim-search-input');
        const filterPills = document.querySelectorAll('.sim-filter-pill');
        const cards = document.querySelectorAll('.sim-card');
        const countBadge = document.getElementById('sim-visible-count');
        const noResults = document.getElementById('sim-no-results');
        const resetBtn = document.getElementById('sim-reset-filters-btn');

        let activeCategory = 'all';
        let searchQuery = '';

        function applyFilters() {
            let visibleCount = 0;
            const query = searchQuery.trim().toLowerCase();

            cards.forEach(card => {
                const cardCat = card.getAttribute('data-category');
                const cardTitle = card.getAttribute('data-title') || '';
                const cardDesc = card.getAttribute('data-desc') || '';
                const cardKeywords = card.getAttribute('data-keywords') || '';
                const cardSlug = card.getAttribute('data-slug') || '';

                const matchesCategory = (activeCategory === 'all' || cardCat === activeCategory);
                const matchesSearch = !query ||
                    cardTitle.includes(query) ||
                    cardDesc.includes(query) ||
                    cardKeywords.includes(query) ||
                    cardSlug.includes(query);

                if (matchesCategory && matchesSearch) {
                    card.classList.remove('hidden');
                    visibleCount++;
                } else {
                    card.classList.add('hidden');
                }
            });

            if (countBadge) {
                countBadge.textContent = visibleCount;
            }

            if (noResults) {
                noResults.style.display = (visibleCount === 0) ? 'block' : 'none';
            }
        }

        // Category Pill Clicks
        filterPills.forEach(pill => {
            pill.addEventListener('click', function() {
                filterPills.forEach(p => {
                    p.classList.remove('active');
                    p.style.background = 'rgba(255, 255, 255, 0.04)';
                    p.style.color = 'var(--text-muted)';
                    p.style.borderColor = 'rgba(255, 255, 255, 0.08)';
                });

                this.classList.add('active');
                this.style.background = 'rgba(56, 189, 248, 0.15)';
                this.style.color = '#38bdf8';
                this.style.borderColor = 'rgba(56, 189, 248, 0.4)';

                activeCategory = this.getAttribute('data-category') || 'all';
                applyFilters();
            });
        });

        // Real-Time Search Typing
        if (searchInput) {
            searchInput.addEventListener('input', function(e) {
                searchQuery = e.target.value;
                applyFilters();
            });
        }

        // Reset Filters Button
        if (resetBtn) {
            resetBtn.addEventListener('click', function() {
                if (searchInput) searchInput.value = '';
                searchQuery = '';
                const allPill = document.querySelector('.sim-filter-pill[data-category="all"]');
                if (allPill) allPill.click();
            });
        }

        // Ensure MathJax renders formulas cleanly in cards
        if (window.MathJax && MathJax.typesetPromise) {
            MathJax.typesetPromise();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSimulationsDirectory);
    } else {
        initSimulationsDirectory();
    }
})();
