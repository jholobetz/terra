<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $title ?? 'Physics Lab' ?> - Terra</title>

    <!-- MathJax Configuration -->
    <script nonce="<?= $nonce ?>">
        window.MathJax = {
            tex: {
                inlineMath: [['\\(', '\\)']],
                displayMath: [['\\[', '\\]']],
                processEscapes: true
            },
            options: {
                processHtmlClass: 'tex2jax_process'
            }
        };
    </script>
    <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async nonce="<?= $nonce ?>"></script>
    
    <style>
        :root { --bg: #0a192f; --text: #ccd6f6; --accent: #64ffda; --card-bg: #112240; }
        body { font-family: 'Inter', system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 20px; }
        main { max-width: 1000px; margin: 0 auto; padding-top: 40px; }
        li { margin-bottom: 1rem; }
        h1, h2, h3 { color: var(--accent); }
        nav { border-bottom: 1px solid #233554; padding-bottom: 20px; margin-bottom: 30px; display: flex; gap: 25px; justify-content: flex-end; align-items: center; }
        nav a { color: var(--accent); text-decoration: none; font-weight: 600; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; display: inline-flex; align-items: center; line-height: 1; }
        nav a:hover { text-decoration: underline; }
        .stats-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .stat-card { background: var(--card-bg); padding: 25px; border-radius: 8px; border-top: 3px solid var(--accent); }
        
        /* Home Page Tile Layout */
        .hero { text-align: center; padding: 60px 0; }
        .hero h1 { font-size: 3rem; margin-bottom: 10px; }
        .subtitle { font-size: 1.2rem; opacity: 0.8; margin-bottom: 30px; }
        .btn { display: inline-block; padding: 12px 24px; border-radius: 4px; text-decoration: none; font-weight: 600; margin: 10px; transition: all 0.2s; }
        .btn-primary { background: var(--accent); color: var(--bg); }
        .btn-secondary { border: 1px solid var(--accent); color: var(--accent); }
        .btn:hover { opacity: 0.9; transform: translateY(-2px); }
        
        .topics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; margin-top: 40px; }
        .topic-card { background: var(--card-bg); padding: 30px; border-radius: 12px; border: 1px solid #233554; transition: all 0.3s ease; display: flex; flex-direction: column; text-decoration: none; color: inherit; }
        .topic-card:hover { transform: translateY(-5px); border-color: var(--accent); box-shadow: 0 10px 30px -15px rgba(2,12,27,0.7); }
        .read-more { color: var(--accent); text-decoration: none; font-weight: 600; margin-top: auto; padding-top: 15px; display: inline-block; }

        /* Subtopic Links */
        .subtopic-link {
            color: #b464ff;
            text-decoration: none;
        }
        .subtopic-link:hover { /* Brighter shade for better accessibility */
            color: #c990ff;
            text-decoration: underline;
        }

        /* Breadcrumbs */
        .breadcrumb { display: flex; align-items: center; margin-bottom: 20px; font-size: 0.85rem; color: #8892b0;justify-content: flex-start; border-bottom: none; padding-bottom: 0; gap: 8px;}
        .breadcrumb a { color: var(--accent); text-decoration: none; text-transform: none; letter-spacing: 0; font-weight: normal; }
        .breadcrumb a:hover { text-decoration: underline; }
        .breadcrumb span { opacity: 0.7; padding-left: 2px; }

        /* Topic Page Equations */
        .equations-list { list-style: none; padding: 0; }
        .equation-item { margin-bottom: 20px; }
        mjx-container { color: #FFD700; }
        .equation-container { cursor: pointer; transition: color 0.2s ease; }
        .equation-container:hover { color: var(--accent); }
        .breakdown { color: var(--accent); padding-top: 10px; }

        /* Dropdown Menu */
        .dropdown { position: relative; display: inline-flex; align-items: center; }
        .dropdown-content { 
            display: none; 
            position: absolute; 
            background-color: var(--card-bg); 
            min-width: 220px; 
            box-shadow: 0px 10px 20px rgba(0,0,0,0.4); 
            z-index: 1000; 
            border: 1px solid #233554;
            border-radius: 8px;
            top: 100%;
            right: 0;
        }
        .dropdown-content a { 
            color: var(--text); 
            padding: 12px 20px; 
            text-decoration: none; 
            display: block; 
            text-transform: none; 
            font-size: 0.9rem;
            letter-spacing: 0.5px;
            border-bottom: 1px solid #233554;
            margin: 0;
        }
        .dropdown-content a:last-child { border-bottom: none; }
        .dropdown-content a:hover { background-color: #1d2d44; color: var(--accent); text-decoration: none; }
        .dropdown:hover .dropdown-content { display: block; }
        .dropbtn { cursor: default; }

        /* Draft Badge */
        .draft-badge {
            background: #ff4757;
            color: #fff;
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 800;
            text-transform: uppercase;
            margin-right: 8px;
            display: inline-block;
            line-height: 1;
            vertical-align: middle;
            letter-spacing: 0.5px;
        }
    </style>
</head>
<body>
    <?php if ($is_preview ?? false): ?>
        <div style="background: #ff4757; color: white; text-align: center; padding: 10px; font-weight: bold; position: sticky; top: 0; z-index: 9999; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">
            PREVIEW MODE ACTIVE: Viewing changes from physics_content.php 
            &nbsp;&nbsp;|&nbsp;&nbsp; 
            <a href="?preview=0" style="color: white; text-decoration: underline;">Exit Preview</a>
        </div>
    <?php endif; ?>
    <nav>
        <a href="/physics">Home</a>
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

    <main>
        <?= $body_content ?>
    </main>
</body>
</html>