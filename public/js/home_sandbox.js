document.addEventListener('DOMContentLoaded', () => {
    // 1. Tabbed Navigation Filtering
    const tabButtons = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.topic-card');
    
    if (tabButtons.length > 0 && cards.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                // Remove active class
                tabButtons.forEach(b => b.classList.remove('active'));
                // Add active class
                btn.classList.add('active');
                
                const activeDomain = btn.getAttribute('data-domain');
                
                cards.forEach(card => {
                    const cardDomain = card.getAttribute('data-domain');
                    if (activeDomain === 'all' || cardDomain === activeDomain) {
                        card.classList.remove('hidden');
                    } else {
                        card.classList.add('hidden');
                    }
                });
            });
        });
    }
});
