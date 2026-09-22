<?php
// Lab Tools Landing Page view - Unified Physics Laboratory & Cosmic Arena
?>

<div class="lab-tools-container" style="padding: 10px 0 60px 0;">
    <!-- Premium Header Section -->
    <header class="simulations-header" style="margin-bottom: 30px; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 25px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 10px;">
            <span class="arena-pill-badge" style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                Experimental &amp; CAS Crucible
            </span>
            <span style="color: var(--text-muted); font-size: 0.85rem;">•</span>
            <span style="color: var(--text-muted); font-size: 0.85rem;">Interactive Manifold v2.4</span>
        </div>
        <h1 style="font-size: 3rem; margin: 0 0 12px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 40%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            The Unified Physics Laboratory
        </h1>
        <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 820px;">
            From visceral 60fps mechanical simulations to exact SymPy Computer Algebra proofs, explore the mathematical symmetries, phase space flows, and quantum transitions governing the physical universe.
        </p>
    </header>

    <!-- ================================================================= -->
    <!-- HERO STAGE: THE COSMIC ARENA                                      -->
    <!-- ================================================================= -->
    <section class="cosmic-arena-section" style="margin-bottom: 50px;">
        <!-- Arena Selector Carousel / Mystery Pills -->
        <div class="arena-carousel-bar">
            <div class="carousel-label">Select Physical Regime:</div>
            <div class="mystery-pills-container">
                <button class="mystery-pill active" data-mode="chaos">
                    <span class="pill-icon">🌀</span>
                    <span class="pill-text">The Butterfly of Chaos</span>
                    <span class="pill-sub">Lagrangian RK4</span>
                </button>
                <button class="mystery-pill" data-mode="quantum">
                    <span class="pill-icon">👻</span>
                    <span class="pill-text">The Quantum Ghost</span>
                    <span class="pill-sub">Wave Packet Tunneling</span>
                </button>
                <button class="mystery-pill" data-mode="collapse">
                    <span class="pill-icon">💥</span>
                    <span class="pill-text">Tuning the Universe to Death</span>
                    <span class="pill-sub">ISCO Gravity Collapse</span>
                </button>
                <button class="mystery-pill" data-mode="noether">
                    <span class="pill-icon">⚡</span>
                    <span class="pill-text">The Breaking of Energy</span>
                    <span class="pill-sub">Noether Time Symmetry</span>
                </button>
            </div>
        </div>

        <!-- The Cosmic Stage Viewport -->
        <div class="cosmic-stage-card">
            <div class="arena-canvas-container">
                <canvas id="cosmic-arena-canvas"></canvas>
                
                <!-- Overlay Status & Live Badges -->
                <div class="arena-overlay-top">
                    <div id="arena-status-badge" class="arena-status-badge">HAMILTONIAN CONSERVED</div>
                    <button id="arena-sound-toggle" class="arena-icon-btn" title="Toggle Harmonic Tone Audio">
                        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
                        </svg>
                    </button>
                </div>

                <!-- Telemetry Dashboard Floating Inset -->
                <div class="arena-telemetry-hud">
                    <div class="telemetry-cell">
                        <span class="telem-label" style="color: #38bdf8;">Coordinate q</span>
                        <span class="telem-val" id="telem-q">0.00</span>
                    </div>
                    <div class="telemetry-cell">
                        <span class="telem-label" style="color: #34d399;">Momentum p</span>
                        <span class="telem-val" id="telem-p">0.00</span>
                    </div>
                    <div class="telemetry-cell">
                        <span class="telem-label" style="color: #fbbf24;">Potential V</span>
                        <span class="telem-val" id="telem-v">0.00</span>
                    </div>
                    <div class="telemetry-cell">
                        <span class="telem-label" style="color: #c084fc;">Total Energy E</span>
                        <span class="telem-val" id="telem-e">0.00</span>
                    </div>
                </div>
            </div>

            <!-- Mathematical Scaffolding & Live Control Console -->
            <div class="arena-console-bar">
                <div class="arena-math-col">
                    <div class="math-banner-header">
                        <span class="console-label">Governing Physical Manifold</span>
                        <span class="color-legend">
                            <span class="dot-q"></span> q: Coord
                            <span class="dot-p"></span> p: Momentum
                            <span class="dot-v"></span> V: Field
                        </span>
                    </div>
                    <div id="arena-equation-display" class="arena-equation-display">
                        <!-- MathJax typeset dynamically -->
                    </div>
                </div>

                <div class="arena-controls-col">
                    <div class="arena-slider-wrapper">
                        <div class="slider-header-line">
                            <span id="arena-param-label" class="param-title">Parameter Dial</span>
                            <span id="arena-param-val" class="param-value">1.00</span>
                        </div>
                        <input type="range" id="arena-param-slider" class="arena-range-slider" min="0.2" max="2.0" step="0.05" value="1.0">
                    </div>

                    <div class="arena-action-buttons">
                        <button id="arena-play-pause" class="btn btn-secondary arena-btn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
                            Pause
                        </button>
                        <button id="arena-reset" class="btn btn-secondary arena-btn">
                            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"></path><path d="M3 3v5h5"></path></svg>
                            Reset
                        </button>
                        <a id="arena-deep-link" href="/physics/legendre-transformer" class="btn btn-primary arena-btn arena-launch-btn">
                            Inspect in Analytical Mechanics Workbench &rarr;
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- ================================================================= -->
    <!-- "WHAT-IF?" PROVOCATIVE MICRO-CHALLENGES                           -->
    <!-- ================================================================= -->
    <div style="margin-bottom: 45px;">
        <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 18px;">
            <h2 style="font-size: 1.4rem; margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 8px;">
                <span style="display: inline-block; width: 6px; height: 18px; background: #fbbf24; border-radius: 3px;"></span>
                "What-If?" Micro-Challenges
            </h2>
            <span style="font-size: 0.88rem; color: var(--text-muted);">Test physical extremes directly in the simulator</span>
        </div>

        <div class="challenges-grid">
            <div class="challenge-card">
                <div class="challenge-badge" style="background: rgba(251, 191, 36, 0.15); color: #fbbf24;">Symmetry &amp; Invariance</div>
                <h4>The Symmetry Thief</h4>
                <p>Can you break energy conservation without breaking spatial momentum? Wobble time in the potential to observe non-zero \(\partial \mathcal{L}/\partial t\).</p>
                <button class="challenge-action-btn" data-target-mode="noether" data-target-val="0.55">
                    Launch Challenge &rarr;
                </button>
            </div>

            <div class="challenge-card">
                <div class="challenge-badge" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8;">Quantum Transitions</div>
                <h4>The Quantum Escape</h4>
                <p>Lower the potential barrier until an incident Gaussian packet splits into an evanescent tunneling wave with \(>25\%\) transmission.</p>
                <button class="challenge-action-btn" data-target-mode="quantum" data-target-val="1.8">
                    Launch Challenge &rarr;
                </button>
            </div>

            <div class="challenge-card">
                <div class="challenge-badge" style="background: rgba(239, 68, 68, 0.15); color: #ef4444;">Relativistic Limits</div>
                <h4>The Gravitational Crunch</h4>
                <p>Crank the gravitational constant \(G\) until the effective Schwarzschild potential loses its barrier and orbits collapse into the black hole horizon.</p>
                <button class="challenge-action-btn" data-target-mode="collapse" data-target-val="3.2">
                    Launch Challenge &rarr;
                </button>
            </div>
        </div>
    </div>

    <!-- ================================================================= -->
    <!-- HEADLINE ANALYTICAL INSTRUMENTS DECK                              -->
    <!-- ================================================================= -->
    <div style="display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 20px;">
        <h2 style="font-size: 1.5rem; margin: 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 8px;">
            <span style="display: inline-block; width: 6px; height: 18px; background: var(--accent-default); border-radius: 3px;"></span>
            Flagship Analytical Engines
        </h2>
        <span style="font-size: 0.88rem; color: var(--text-muted);">SymPy CAS solvers, continuous symmetries &amp; manifold mappers</span>
    </div>
    
    <section class="topics-grid" style="margin-bottom: 50px;">
        <!-- Card 1: Analytical Mechanics Workbench -->
        <a href="/physics/legendre-transformer" class="topic-card card-theoretical" style="--card-accent: var(--accent-theoretical);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <path d="M 20 80 Q 50 20, 80 80" fill="none" stroke="currentColor" stroke-width="1.2"/>
                    <line x1="50" y1="20" x2="50" y2="80" stroke="currentColor" stroke-width="1" stroke-dasharray="2 2"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-theoretical);">
                    <path d="M 20 80 L 80 20" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                    <path d="M 20 20 L 80 80" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                    <circle cx="50" cy="50" r="15" fill="none" stroke="var(--accent-theoretical)" stroke-width="2"/>
                    <line x1="50" y1="20" x2="50" y2="80" stroke="var(--accent-theoretical)" stroke-width="1.5"/>
                    <line x1="20" y1="50" x2="80" y2="50" stroke="var(--accent-theoretical)" stroke-width="1.5"/>
                    <circle cx="50" cy="20" r="3.5" fill="currentColor"/>
                    <circle cx="50" cy="80" r="3.5" fill="currentColor"/>
                </svg>
                <h3>The Analytical Mechanics Workbench</h3>
            </div>
            <p>Compute canonical momentum derivatives \(p_i = \partial L/\partial \dot{q}_i\), verify Hessian non-singularity \(\det(W) \neq 0\), algebraically invert velocities with SymPy CAS, and construct Hamilton's equations.</p>
            <span class="read-more">Open Workbench &rarr;</span>
        </a>

        <!-- Card 2: Symmetry Playground / Noether's Vault -->
        <a href="/physics/noethers-vault" class="topic-card card-theoretical" style="--card-accent: var(--accent-theoretical);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="32" stroke="currentColor" stroke-width="1" fill="none"/>
                    <path d="M 50 15 A 35 35 0 0 1 85 50" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-theoretical);">
                    <circle cx="50" cy="50" r="32" stroke="currentColor" stroke-dasharray="3 3" stroke-width="1" opacity="0.3"/>
                    <circle cx="50" cy="50" r="24" stroke="currentColor" stroke-dasharray="5 2" stroke-width="1.2" opacity="0.4"/>
                    <path d="M 50 15 A 35 35 0 0 1 85 50" fill="none" stroke="var(--accent-theoretical)" stroke-linecap="round" stroke-width="2"/>
                    <polygon points="85,50 81,46 89,46" fill="var(--accent-theoretical)"/>
                    <circle cx="50" cy="50" r="5" fill="var(--accent-theoretical)"/>
                    <line x1="15" y1="50" x2="85" y2="50" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                    <line x1="50" y1="15" x2="50" y2="85" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                </svg>
                <h3>The Symmetry Playground</h3>
            </div>
            <p>Trace continuous Lie group symmetries to conserved Noether currents \(J^\mu\). Map spacetime translations to 4-momentum and spatial rotations to angular momentum conservation.</p>
            <span class="read-more">Launch Playground &rarr;</span>
        </a>

        <!-- Card 3: Quantum-to-Classical Bridge -->
        <a href="/physics/correspondence-workspace" class="topic-card card-quantum" style="--card-accent: var(--accent-quantum);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <circle cx="35" cy="50" r="5" fill="currentColor"/>
                    <path d="M 15 50 Q 25 20, 35 50 T 55 50 T 75 50" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-quantum);">
                    <line x1="15" y1="50" x2="85" y2="50" stroke="currentColor" stroke-width="0.8" opacity="0.2"/>
                    <circle cx="35" cy="50" r="5" fill="#ffd700"/>
                    <path d="M 15 50 Q 25 20, 35 50 T 55 50 T 75 50 T 85 50" fill="none" stroke="var(--accent-quantum)" stroke-width="2" stroke-linecap="round"/>
                    <circle cx="50" cy="50" r="30" stroke="currentColor" stroke-dasharray="3 3" stroke-width="1" opacity="0.3"/>
                    <line x1="35" y1="25" x2="35" y2="75" stroke="var(--accent-quantum)" stroke-dasharray="2 2" stroke-width="1.2"/>
                </svg>
                <h3>The Quantum-to-Classical Bridge</h3>
            </div>
            <p>Cross the correspondence boundary using Ehrenfest's theorem. Contrast point trajectories against spreading wave packets and phase space Wigner distributions.</p>
            <span class="read-more">Cross Bridge &rarr;</span>
        </a>

        <!-- Card 4: The Multiverse Creator -->
        <a href="/physics/anthropic-tuner" class="topic-card card-astrophysics" style="--card-accent: var(--accent-astrophysics);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="28" stroke="currentColor" stroke-width="1"/>
                    <ellipse cx="50" cy="50" rx="35" ry="12" stroke="currentColor" stroke-width="1" transform="rotate(-30 50 50)"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-astrophysics);">
                    <circle cx="50" cy="50" r="10" fill="none" stroke="var(--accent-astrophysics)" stroke-width="1.8"/>
                    <circle cx="50" cy="50" r="28" stroke="currentColor" stroke-dasharray="4 4" stroke-width="1" opacity="0.3"/>
                    <ellipse cx="50" cy="50" rx="35" ry="12" stroke="currentColor" stroke-width="1" fill="none" transform="rotate(-30 50 50)" opacity="0.4"/>
                    <path d="M 15 80 L 40 80" stroke="currentColor" stroke-linecap="round" stroke-width="2" opacity="0.2"/>
                    <circle cx="30" cy="80" r="4.5" fill="var(--accent-astrophysics)"/>
                    <path d="M 60 80 L 85 80" stroke="currentColor" stroke-linecap="round" stroke-width="2" opacity="0.2"/>
                    <circle cx="75" cy="80" r="4.5" fill="var(--accent-astrophysics)"/>
                </svg>
                <h3>The Multiverse Creator</h3>
            </div>
            <p>Tune fundamental physical dials (\(G, c, \hbar, \alpha\)). Benchmark stellar lifetimes, atomic radii, and cosmic expansion rates against anthropic stability bounds.</p>
            <span class="read-more">Tune Multiverse &rarr;</span>
        </a>

        <!-- Card 5: The Rosetta Stone of Physics -->
        <a href="/physics/notation-toggle" class="topic-card card-relativity" style="--card-accent: var(--accent-relativity);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="1.2" fill="none"/>
                    <path d="M 50 50 Q 65 35, 71 21" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-relativity);">
                    <circle cx="50" cy="50" r="30" stroke="currentColor" stroke-width="1.2" fill="none" opacity="0.3"/>
                    <line x1="50" y1="50" x2="50" y2="20" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/>
                    <line x1="50" y1="50" x2="80" y2="50" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/>
                    <path d="M 50 50 Q 65 35, 71 21" fill="none" stroke="var(--accent-relativity)" stroke-linecap="round" stroke-width="2"/>
                    <circle cx="71" cy="21" r="3.5" fill="var(--accent-relativity)"/>
                    <line x1="20" y1="50" x2="80" y2="50" stroke="currentColor" stroke-dasharray="2 2" stroke-width="0.8" opacity="0.4"/>
                    <line x1="50" y1="20" x2="50" y2="80" stroke="currentColor" stroke-dasharray="2 2" stroke-width="0.8" opacity="0.4"/>
                    <path d="M 35 30 Q 30 35, 35 40" fill="none" stroke="currentColor" stroke-linecap="round" stroke-width="1"/>
                    <path d="M 32 30 L 36 30 L 35 34" fill="currentColor"/>
                </svg>
                <h3>The Rosetta Stone of Physics</h3>
            </div>
            <p>Seamlessly toggle physical laws between 3D vector arrows, 4D spacetime tensors (\(\partial_\mu F^{\mu\nu} = \mu_0 J^\nu\)), and Cartan exterior differential forms (\(dF = 0\)).</p>
            <span class="read-more">Toggle Notation &rarr;</span>
        </a>

        <!-- Card 6: Physics Universe Graph -->
        <a href="/physics/universe-graph" class="topic-card card-math-methods" style="--card-accent: var(--accent-math-methods);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <line x1="30" y1="30" x2="50" y2="55" stroke="currentColor" stroke-width="1"/>
                    <line x1="70" y1="30" x2="50" y2="55" stroke="currentColor" stroke-width="1"/>
                    <circle cx="50" cy="55" r="9" fill="none" stroke="currentColor" stroke-width="2"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-math-methods);">
                    <line x1="30" y1="30" x2="50" y2="55" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                    <line x1="70" y1="30" x2="50" y2="55" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                    <line x1="50" y1="55" x2="30" y2="80" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                    <line x1="50" y1="55" x2="70" y2="80" stroke="currentColor" stroke-width="1.5" opacity="0.4"/>
                    <circle cx="30" cy="30" r="7" fill="var(--accent-math-methods)"/>
                    <circle cx="70" cy="30" r="7" fill="var(--accent-math-methods)"/>
                    <circle cx="50" cy="55" r="9" fill="#ffffff" stroke="var(--accent-math-methods)" stroke-width="2"/>
                    <circle cx="30" cy="80" r="6" fill="currentColor"/>
                    <circle cx="70" cy="80" r="6" fill="currentColor"/>
                </svg>
                <h3>Physics Universe Graph</h3>
            </div>
            <p>Explore the complete derivation Directed Acyclic Graph (DAG) across 14,666 formulas with real-time Dijkstra shortest-path derivations and zero isolated nodes.</p>
            <span class="read-more">Launch Universe Graph &rarr;</span>
        </a>

        <!-- Card 7: Equation Explainer -->
        <a href="/physics/equation-explainer" class="topic-card card-quantum" style="--card-accent: var(--accent-quantum);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <text x="50" y="65" font-family="Space Grotesk, serif" font-size="32" font-style="italic" font-weight="bold" fill="currentColor" text-anchor="middle">🔬</text>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-quantum);">
                    <circle cx="45" cy="45" r="20" stroke="var(--accent-quantum)" stroke-width="1.8" fill="none" opacity="0.8"/>
                    <line x1="59" y1="59" x2="85" y2="85" stroke="var(--accent-quantum)" stroke-width="3" stroke-linecap="round"/>
                    <text x="45" y="52" font-family="Space Grotesk, serif" font-size="20" font-weight="bold" fill="currentColor" text-anchor="middle">Ψ</text>
                </svg>
                <h3>The Equation Explainer</h3>
            </div>
            <p>Deconstruct LaTeX physics equations in real-time. Inspect variable dimensions, semantic parameter roles, and boundary limits on an interactive syntax canvas.</p>
            <span class="read-more">Deconstruct Equations &rarr;</span>
        </a>

        <!-- Card 8: Simulations Hub -->
        <a href="/physics/simulations" class="topic-card card-classical" style="--card-accent: var(--accent-classical);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <ellipse cx="50" cy="50" rx="36" ry="16" stroke="currentColor" stroke-width="1.2" fill="none"/>
                    <circle cx="16" cy="41" r="4.5" fill="currentColor"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-classical);">
                    <circle cx="50" cy="50" r="36" stroke="currentColor" stroke-dasharray="4 4" stroke-width="1.2" fill="none" opacity="0.3"/>
                    <ellipse cx="50" cy="50" rx="36" ry="16" stroke="currentColor" stroke-width="1.2" fill="none" transform="rotate(-15 50 50)"/>
                    <circle cx="50" cy="8" fill="none" stroke="var(--accent-classical)" stroke-width="1.5"/>
                    <circle cx="16" cy="41" r="4.5" fill="var(--accent-classical)"/>
                    <circle cx="84" cy="59" r="3" fill="currentColor"/>
                    <line x1="16" y1="41" x2="28" y2="15" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/>
                    <polygon points="28,15 24,19 29,20" fill="currentColor"/>
                </svg>
                <h3>Interactive Simulations Library</h3>
            </div>
            <p>Run 16 real-time numerical solvers for classical mechanics, wave interference, thermodynamics, electromagnetism, and optics directly in your browser.</p>
            <span class="read-more">Explore Simulations &rarr;</span>
        </a>
    </section>

    <!-- ================================================================= -->
    <!-- PHYSICAL REFERENCES & REGISTERS                                   -->
    <!-- ================================================================= -->
    <h2 style="font-size: 1.5rem; margin: 0 0 20px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-block; width: 6px; height: 18px; background: var(--accent-default); border-radius: 3px;"></span>
        Physical Registers &amp; Reference Standards
    </h2>

    <section class="topics-grid">
        <!-- Constants Reference -->
        <a href="/physics/constants" class="topic-card card-thermodynamics" style="--card-accent: var(--accent-thermodynamics);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <text x="50" y="62" font-family="Space Grotesk, serif" font-size="36" font-style="italic" font-weight="bold" fill="currentColor" text-anchor="middle">ℏ</text>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-thermodynamics);">
                    <path d="M 15 50 Q 25 50, 30 30 T 40 70 T 50 20 T 60 80 T 70 30 T 75 50 T 85 50" fill="none" stroke="currentColor" stroke-width="1" opacity="0.4"/>
                    <path d="M 30 30 Q 35 15, 50 15 T 70 30" fill="none" stroke="var(--accent-thermodynamics)" stroke-width="1.5" opacity="0.2"/>
                    <path d="M 30 70 Q 35 85, 50 85 T 70 70" fill="none" stroke="var(--accent-thermodynamics)" stroke-width="1.5" opacity="0.2"/>
                    <text x="50" y="58" font-family="Space Grotesk, serif" font-size="28" font-style="italic" font-weight="bold" fill="var(--accent-thermodynamics)" text-anchor="middle">ℏ</text>
                </svg>
                <h3>Fundamental Physical Constants</h3>
            </div>
            <p>Access exact values, uncertainty metrics, SI definitions, and dimensional groupings for speed of light, Planck's constant, gravitational constant, and fine-structure parameters.</p>
            <span class="read-more">View Constants &rarr;</span>
        </a>

        <!-- Symbol Directory -->
        <a href="/physics/symbols" class="topic-card card-philosophy" style="--card-accent: var(--accent-philosophy);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <polygon points="50,25 25,68 75,68" fill="none" stroke="currentColor" stroke-width="1.8"/>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-philosophy);">
                    <polygon points="50,25 25,68 75,68" fill="none" stroke="var(--accent-philosophy)" stroke-width="1.8" opacity="0.8"/>
                    <circle cx="50" cy="25" r="2.5" fill="currentColor"/>
                    <text x="36" y="58" font-family="Space Grotesk, sans-serif" font-size="18" fill="currentColor" opacity="0.4">&part;</text>
                    <text x="60" y="58" font-family="Space Grotesk, sans-serif" font-size="18" fill="currentColor" opacity="0.4">&Sigma;</text>
                    <circle cx="50" cy="50" r="35" stroke="currentColor" stroke-width="0.8" fill="none" opacity="0.1"/>
                </svg>
                <h3>Symbols &amp; Manifold Lexicon</h3>
            </div>
            <p>A comprehensive lexicon detailing indices, coordinate maps, covariant derivatives, differential operators, and standard field variables used across physical theory.</p>
            <span class="read-more">View Symbols &rarr;</span>
        </a>
    </section>
</div>

<style>
/* =========================================================================
   THE COSMIC ARENA & LAB TOOLS STYLING
   ========================================================================= */

.cosmic-stage-card {
    background: radial-gradient(circle at 50% 0%, rgba(30, 41, 59, 0.4) 0%, rgba(10, 15, 26, 0.95) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: border-color 0.3s ease;
}

.cosmic-stage-card:hover {
    border-color: rgba(56, 189, 248, 0.3);
}

/* Arena Carousel Pills */
.arena-carousel-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}

.carousel-label {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-muted);
}

.mystery-pills-container {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.mystery-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 30px;
    padding: 6px 14px;
    color: var(--text-muted);
    font-size: 0.88rem;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.mystery-pill:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-1px);
}

.mystery-pill.active {
    background: rgba(56, 189, 248, 0.12);
    color: #ffffff;
    border-color: #38bdf8;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.25);
}

.pill-icon {
    font-size: 1.1rem;
}

.pill-text {
    font-weight: 600;
}

.pill-sub {
    font-size: 0.72rem;
    color: var(--text-muted);
    background: rgba(255, 255, 255, 0.06);
    padding: 2px 6px;
    border-radius: 10px;
}

.mystery-pill.active .pill-sub {
    color: #38bdf8;
    background: rgba(56, 189, 248, 0.2);
}

/* Canvas Viewport */
.arena-canvas-container {
    position: relative;
    width: 100%;
    height: 380px;
    background: #060911;
    overflow: hidden;
}

#cosmic-arena-canvas {
    width: 100%;
    height: 100%;
    display: block;
}

/* Overlay Elements */
.arena-overlay-top {
    position: absolute;
    top: 16px;
    right: 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    z-index: 10;
}

.arena-status-badge {
    background: rgba(10, 15, 26, 0.75);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border: 1px solid rgba(52, 211, 153, 0.4);
    color: #34d399;
    font-size: 0.75rem;
    font-family: monospace;
    font-weight: 700;
    letter-spacing: 0.06em;
    padding: 5px 12px;
    border-radius: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.arena-icon-btn {
    background: rgba(10, 15, 26, 0.75);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: var(--text-muted);
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}

.arena-icon-btn:hover, .arena-icon-btn.active {
    color: #38bdf8;
    border-color: #38bdf8;
    background: rgba(56, 189, 248, 0.15);
}

/* Telemetry HUD Inset */
.arena-telemetry-hud {
    position: absolute;
    bottom: 16px;
    left: 16px;
    display: flex;
    gap: 10px;
    background: rgba(10, 15, 26, 0.85);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 8px 14px;
    border-radius: 10px;
    z-index: 10;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.telemetry-cell {
    display: flex;
    flex-direction: column;
    padding: 0 8px;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.telemetry-cell:last-child {
    border-right: none;
    padding-right: 0;
}

.telem-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.telem-val {
    font-family: monospace;
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
}

/* Console Control Bar */
.arena-console-bar {
    display: grid;
    grid-template-columns: 1.2fr 0.8fr;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    background: rgba(15, 23, 42, 0.7);
    backdrop-filter: blur(10px);
}

@media (max-width: 900px) {
    .arena-console-bar {
        grid-template-columns: 1fr;
    }
}

.arena-math-col {
    padding: 20px 24px;
    border-right: 1px solid rgba(255, 255, 255, 0.08);
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.math-banner-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.console-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted);
}

.color-legend {
    font-size: 0.75rem;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
}

.dot-q, .dot-p, .dot-v {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
}
.dot-q { background: #38bdf8; }
.dot-p { background: #34d399; }
.dot-v { background: #fbbf24; }

.arena-equation-display {
    min-height: 52px;
    display: flex;
    align-items: center;
    overflow-x: auto;
    color: #ffffff;
}

.arena-controls-col {
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 16px;
    background: rgba(255, 255, 255, 0.015);
}

.slider-header-line {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
}

.param-title {
    font-size: 0.85rem;
    font-weight: 600;
    color: #e2e8f0;
}

.param-value {
    font-family: monospace;
    font-size: 0.9rem;
    font-weight: 700;
    color: #38bdf8;
}

.arena-range-slider {
    width: 100%;
    -webkit-appearance: none;
    appearance: none;
    height: 6px;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    outline: none;
    cursor: pointer;
}

.arena-range-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #38bdf8;
    cursor: pointer;
    box-shadow: 0 0 10px #38bdf8;
    transition: transform 0.1s;
}

.arena-range-slider::-webkit-slider-thumb:hover {
    transform: scale(1.2);
}

.arena-action-buttons {
    display: flex;
    gap: 8px;
    align-items: center;
}

.arena-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    padding: 8px 14px;
    border-radius: 8px;
    cursor: pointer;
    white-space: nowrap;
}

.arena-launch-btn {
    margin-left: auto;
    font-weight: 600;
    text-decoration: none;
}

/* Micro-Challenges Grid */
.challenges-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
}

.challenge-card {
    background: rgba(15, 23, 42, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 20px;
    display: flex;
    flex-direction: column;
    transition: all 0.25s ease;
}

.challenge-card:hover {
    background: rgba(30, 41, 59, 0.6);
    border-color: rgba(255, 255, 255, 0.18);
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.challenge-badge {
    align-self: flex-start;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 3px 8px;
    border-radius: 12px;
    margin-bottom: 12px;
}

.challenge-card h4 {
    margin: 0 0 8px 0;
    font-size: 1.1rem;
    font-family: 'Space Grotesk', sans-serif;
    color: #ffffff;
}

.challenge-card p {
    margin: 0 0 16px 0;
    font-size: 0.9rem;
    color: var(--text-muted);
    line-height: 1.5;
    flex-grow: 1;
}

.challenge-action-btn {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #ffffff;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
}

.challenge-action-btn:hover {
    background: #38bdf8;
    border-color: #38bdf8;
    color: #05070d;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
}
</style>

<script src="/js/cosmic_arena.js" defer></script>
