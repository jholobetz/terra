document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('search-input');
    const results = document.getElementById('search-results');
    let searchData = null;

    if (!input) return;

    input.addEventListener('focus', async () => {
        if (!searchData) {
            input.placeholder = "Loading index...";
            try {
                const response = await fetch('/physics/search-index');
                if (!response.ok) throw new Error('Search index load failed');
                searchData = await response.json();
                input.placeholder = "Search the manifold...";
                console.log('Knowledge Graph indexed:', Object.keys(searchData).length, 'topics');
            } catch (e) {
                input.placeholder = "Search unavailable";
                console.error('Search Engine Error:', e);
            }
        }
    });

    input.addEventListener('input', (e) => {
        if (!searchData) return;
        
        const query = e.target.value.toLowerCase().trim();
        const cleanQuery = query.replace(/[''s]/g, ''); 
        
        if (query.length < 2) {
            results.style.display = 'none';
            return;
        }

        const scoredMatches = [];
        for (const [slug, data] of Object.entries(searchData)) {
            let score = 0;
            const title = data.t.toLowerCase();
            const cleanTitle = title.replace(/[''s]/g, '');

            if (title === query || cleanTitle === cleanQuery) score += 100;
            else if (title.startsWith(query) || cleanTitle.startsWith(cleanQuery)) score += 80;
            else if (title.includes(query) || cleanTitle.includes(cleanQuery)) score += 50;
            else if (data.k && data.k.some(k => k.toLowerCase().includes(query))) score += 20;

            if (score > 0) {
                scoredMatches.push({ slug, score, ...data });
            }
        }

        scoredMatches.sort((a, b) => b.score - a.score || a.t.length - b.t.length);

        if (scoredMatches.length > 0) {
            const limited = scoredMatches.slice(0, 10);
            results.innerHTML = limited.map(m => `
                <a href="/physics/subtopic/${m.slug}" class="search-result-item">
                    <strong>${m.t}</strong>
                    <small>${m.p.join(' &rsaquo; ')}</small>
                </a>
            `).join('');
            results.style.display = 'block';
        } else {
            results.innerHTML = '<div class="search-result-item" style="cursor:default; opacity:0.6;">No matches in the manifold...</div>';
            results.style.display = 'block';
        }
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.style.display = 'none';
        }
    });
});
