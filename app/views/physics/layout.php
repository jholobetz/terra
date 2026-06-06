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
    <script src="/js/lib/tex-mml-chtml.js" id="MathJax-script" async></script>
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
            
            <div class="search-container">
                <input type="text" id="search-input" placeholder="Search the manifold..." autocomplete="off">
                <div id="search-results"></div>
            </div>

            <nav>
                <div class="dropdown">
                    <a href="#" class="dropbtn">Topics &blacktriangledown;</a>
                    <div class="dropdown-content">
                        <?php foreach($menu_topics as $slug => $topic): ?>
                            <a href="/physics/topic/<?= $slug ?>"><?= $topic['title'] ?></a>
                        <?php endforeach; ?>
                    </div>
                </div>
                <div class="dropdown">
                    <a href="/physics/simulations" class="dropbtn">Simulations &blacktriangledown;</a>
                    <div class="dropdown-content">
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

    <script src="/js/search_engine.js" defer></script>
</body>
</html>