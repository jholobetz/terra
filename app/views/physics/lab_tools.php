<?php
// Lab Tools Landing Page view
?>

<div class="lab-tools-container" style="padding: 10px 0 40px 0;">
    <!-- Premium Header Section -->
    <header class="simulations-header" style="margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 25px;">
        <h1 style="font-size: 3rem; margin: 0 0 10px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 700; background: linear-gradient(135deg, #ffffff 50%, var(--accent-default) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            <?= htmlspecialchars($title) ?>
        </h1>
        <p style="color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; margin: 0; max-width: 750px;">
            A suite of mathematical interpreters, interactive physics engines, and formal physical directories designed to verify algebraic structures and simulate mechanical manifold behaviors.
        </p>
    </header>

    <!-- Main Active Solvers & Translators Grid -->
    <h2 style="font-size: 1.5rem; margin: 0 0 20px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-block; width: 6px; height: 18px; background: var(--accent-default); border-radius: 3px;"></span>
        Analytical &amp; Simulation Engines
    </h2>
    
    <section class="topics-grid" style="margin-bottom: 50px;">
        <!-- Card 1: Dimensional Solver -->
        <a href="/physics/dimensional-solver" class="topic-card card-math-methods" style="--card-accent: var(--accent-math-methods);">
            <div class="card-watermark">
                <svg viewBox="0 0 100 100">
                    <rect x="20" y="45" width="60" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="1.2"/>
                    <text x="50" y="35" font-family="Space Grotesk, sans-serif" font-size="16" font-weight="bold" fill="currentColor" text-anchor="middle">[L][T]⁻¹</text>
                </svg>
            </div>
            <div class="topic-card-header">
                <svg viewBox="0 0 100 100" class="card-icon" style="color: var(--accent-math-methods);">
                    <rect x="20" y="45" width="60" height="10" rx="2" fill="none" stroke="currentColor" stroke-width="1.2" opacity="0.3"/>
                    <line x1="30" y1="45" x2="30" y2="50" stroke="currentColor" stroke-width="1"/>
                    <line x1="40" y1="45" x2="40" y2="52" stroke="currentColor" stroke-width="1"/>
                    <line x1="50" y1="45" x2="50" y2="50" stroke="currentColor" stroke-width="1"/>
                    <line x1="60" y1="45" x2="60" y2="52" stroke="currentColor" stroke-width="1"/>
                    <line x1="70" y1="45" x2="70" y2="50" stroke="currentColor" stroke-width="1"/>
                    <text x="50" y="33" font-family="Space Grotesk, sans-serif" font-size="16" font-weight="bold" fill="var(--accent-math-methods)" text-anchor="middle">[L][T]⁻¹</text>
                    <path d="M 30 65 L 50 80 L 70 65" fill="none" stroke="currentColor" stroke-width="1.2" stroke-dasharray="2 2" opacity="0.5"/>
                    <circle cx="50" cy="80" r="3" fill="currentColor"/>
                </svg>
                <h3>Dimensional Solver</h3>
            </div>
            <p>Verify formulas, compute SI base dimensions, and audit algebraic consistency across classical and quantum equations.</p>
            <span class="read-more">Launch Solver &rarr;</span>
        </a>

        <!-- Card 2: Notation Toggle -->
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
                <h3>Notation Toggle</h3>
            </div>
            <p>Seamlessly translate mathematical formulations between coordinate-free notation, tensor index contractions, and differential forms.</p>
            <span class="read-more">Launch Toggle &rarr;</span>
        </a>

        <!-- Card 3: Noether's Vault -->
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
                <h3>Noether's Vault</h3>
            </div>
            <p>Explore the profound link between physical symmetries and conservation laws. Map continuous coordinate shifts to conserved Noether currents.</p>
            <span class="read-more">Launch Vault &rarr;</span>
        </a>

        <!-- Card 4: Correspondence Workspace -->
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
                <h3>Correspondence Workspace</h3>
            </div>
            <p>Observe the quantum-classical transition. Compare point-particle classical trajectories against quantum wave packet expectation values and phase space flows.</p>
            <span class="read-more">Launch Workspace &rarr;</span>
        </a>

        <!-- Card 5: Anthropic Constant Tuner -->
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
                <h3>Anthropic Constant Tuner</h3>
            </div>
            <p>Adjust the fundamental dials of the universe. Recalculate stellar lifetimes, atomic structures, and cosmic scaling parameters under varying physical constants.</p>
            <span class="read-more">Launch Tuner &rarr;</span>
        </a>

        <!-- Card 6: Genealogy Explorer -->
        <a href="/physics/genealogy-explorer" class="topic-card card-math-methods" style="--card-accent: var(--accent-math-methods);">
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
                <h3>Genealogy Explorer</h3>
            </div>
            <p>Trace the mathematical lineage of physical laws. Interact with a dynamic network graph connecting fundamental axioms to derivations and physical applications.</p>
            <span class="read-more">Launch Explorer &rarr;</span>
        </a>

        <!-- Card 7: Legendre Transformer -->
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
                <h3>Legendre Transformer</h3>
            </div>
            <p>Compute canonical momentum derivatives, solve velocity inversions, and symbolically construct Hamiltonian functions from Lagrangians.</p>
            <span class="read-more">Launch Transformer &rarr;</span>
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
                    <circle cx="50" cy="50" r="8" fill="none" stroke="var(--accent-classical)" stroke-width="1.5"/>
                    <circle cx="16" cy="41" r="4.5" fill="var(--accent-classical)"/>
                    <circle cx="84" cy="59" r="3" fill="currentColor"/>
                    <line x1="16" y1="41" x2="28" y2="15" stroke="currentColor" stroke-linecap="round" stroke-width="1.5"/>
                    <polygon points="28,15 24,19 29,20" fill="currentColor"/>
                </svg>
                <h3>Interactive Simulations</h3>
            </div>
            <p>Run real-time numerical solvers for mechanics, waves, fields, thermodynamics, and quantum systems directly in your browser.</p>
            <span class="read-more">Explore Simulations &rarr;</span>
        </a>

        <!-- Card 9: Equation Explainer -->
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
                <h3>Equation Explainer</h3>
            </div>
            <p>Deconstruct LaTeX physics equations in real-time. Trace mathematical symmetries, examine boundary limits, and analyze semantic variables.</p>
            <span class="read-more">Launch Explainer &rarr;</span>
        </a>
    </section>

    <!-- Reference Directories Section -->
    <h2 style="font-size: 1.5rem; margin: 0 0 20px 0; font-family: 'Space Grotesk', sans-serif; font-weight: 600; color: #ffffff; display: flex; align-items: center; gap: 8px;">
        <span style="display: inline-block; width: 6px; height: 18px; background: var(--accent-default); border-radius: 3px;"></span>
        Physical References &amp; Registers
    </h2>

    <section class="topics-grid">
        <!-- Card 4: Constants Reference -->
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
                <h3>Fundamental Constants</h3>
            </div>
            <p>Access exact values, uncertainty metrics, SI definitions, and dimensional groupings for speed of light, Planck's constant, and more.</p>
            <span class="read-more">View Constants &rarr;</span>
        </a>

        <!-- Card 5: Symbol Directory -->
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
                <h3>Symbols &amp; Notation</h3>
            </div>
            <p>A comprehensive lexicon detailing indices, coordinate maps, partial derivatives, and standard field variables used in physical equations.</p>
            <span class="read-more">View Symbols &rarr;</span>
        </a>
    </section>
</div>
