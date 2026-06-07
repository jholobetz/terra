<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title ?? 'Physics Lab') ?> - Terra</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- MathJax Static-Safe Configuration -->
    <script src="/js/mathjax_config.js"></script>
    <script src="/js/lib/tex-chtml-full.js" id="MathJax-script" defer></script>
    <script src="/js/hub_interactions.js"></script>
    
    <link rel="stylesheet" href="/css/physics.css">
</head>
<body class="physics-lab">

    <?php if ($is_preview ?? false): ?>
        <div class="preview-banner">
            PREVIEW MODE ACTIVE: Viewing changes from sharded JSON files 
            &nbsp;&nbsp;|&nbsp;&nbsp; 
            <a href="?preview=0">Exit Preview</a>
        </div>
    <?php endif; ?>

    <header class="main-header">
        <div class="container nav-wrapper">
            <a href="/physics" class="logo">Physics Lab</a>
            
            <div class="search-trigger-container">
                <button id="search-modal-trigger" class="search-modal-trigger">
                    <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <span>Search...</span>
                    <kbd class="shortcut">⌘K</kbd>
                </button>
            </div>

            <nav>
                <div class="dropdown">
                    <a href="#" class="dropbtn btn btn-secondary">Topics &blacktriangledown;</a>
                    <div class="dropdown-content dropdown-content-secondary">
                        <?php foreach($menu_topics as $slug => $topic): ?>
                            <a href="/physics/topic/<?= $slug ?>"><?= $topic['title'] ?></a>
                        <?php endforeach; ?>
                    </div>
                </div>
                <a href="/physics/dimensional-solver" class="btn btn-secondary">Solver</a>
                <div class="dropdown">
                    <a href="/physics/simulations" class="dropbtn btn btn-primary">Simulations &blacktriangledown;</a>
                    <div class="dropdown-content dropdown-content-primary">
                        <?php foreach($menu_simulations as $slug => $sim): ?>
                            <a href="/physics/simulations/<?= $slug ?>"><?= $sim['title'] ?></a>
                        <?php endforeach; ?>
                    </div>
                </div>
            </nav>
        </div>
    </header>

    <main class="container">
        <?= $body_content ?>
    </main>

    <footer class="main-footer">
        <p>&copy; <?= date('Y') ?> Physics Lab Digital Encyclopedia. All rights reserved.</p>
    </footer>

    <!-- Spotlight Search Modal -->
    <div id="search-modal" class="search-modal">
        <div class="search-modal-backdrop"></div>
        <div class="search-modal-container">
            <div class="search-modal-content">
                <div class="search-modal-header">
                    <svg class="search-icon" viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    <input type="text" id="modal-search-input" placeholder="Search equations, topics, and constants..." autocomplete="off">
                    <button class="close-modal-btn">&times;</button>
                </div>
                <div class="search-modal-body">
                    <div class="search-tips">
                        <span>Press <kbd>Esc</kbd> to close</span>
                        <span>Use <kbd>↑</kbd> <kbd>↓</kbd> to navigate</span>
                    </div>
                    <div id="modal-search-results" class="modal-search-results">
                        <div class="search-placeholder">
                            <p>Search the mathematical manifold</p>
                            <small>Type to search subtopics, physical constants, or defining equations...</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="/js/search_engine.js" defer></script>
</body>
</html>