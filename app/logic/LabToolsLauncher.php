<?php

namespace App\Logic;

/**
 * 🌌 PHYSICS LAB: Lab Tools Encyclopedia Launcher Resolver (Phase 2.5)
 * 
 * Maps subtopic encyclopedia articles to their optimal interactive Lab Tool,
 * CAS duality workbench, or numerical simulation with pre-hydrated URL parameters.
 */
class LabToolsLauncher
{
    /**
     * High-precision curated subtopic mappings.
     */
    private static array $specificMappings = [
        // 1. Analytical Mechanics Workbench (Legendre Transformer)
        'lagrangian-mechanics' => [
            'url' => '/physics/legendre-transformer?preset=sho&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Open in Analytical Workbench',
            'badge_label' => 'SymPy CAS Duality',
            'description' => 'Compute canonical momentum derivatives, evaluate Hessian determinants, and derive Hamilton\'s equations symbolically.',
            'icon' => '🧮',
            'theme' => 'classical'
        ],
        'hamiltonian-mechanics' => [
            'url' => '/physics/legendre-transformer?preset=sho&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Invert in CAS Workbench',
            'badge_label' => 'Legendre Dual',
            'description' => 'Invert generalized velocities and verify phase space symplectic conservation laws.',
            'icon' => '🧮',
            'theme' => 'classical'
        ],
        'euler-lagrange-equations' => [
            'url' => '/physics/legendre-transformer?preset=pendulum&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Evaluate Euler-Lagrange in CAS',
            'badge_label' => 'Variational Extremum',
            'description' => 'Solve extremal stationary action curves for coupled harmonic and nonlinear pendula.',
            'icon' => '🧮',
            'theme' => 'classical'
        ],
        'action-principle' => [
            'url' => '/physics/legendre-transformer?preset=sho&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Test Stationary Action',
            'badge_label' => 'Hamilton\'s Principle',
            'description' => 'Vary paths to minimize the action integral δS = 0 in phase space.',
            'icon' => '🧮',
            'theme' => 'classical'
        ],
        'simple-harmonic-oscillator-mechanics' => [
            'url' => '/physics/legendre-transformer?preset=sho&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Derive SHO Hamiltonian',
            'badge_label' => 'Quadratic Potential',
            'description' => 'Perform symbolic Legendre transformation on quadratic harmonic potentials.',
            'icon' => '🌀',
            'theme' => 'classical'
        ],
        'relativistic-mechanics' => [
            'url' => '/physics/legendre-transformer?preset=relativistic&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Compute Relativistic Hessian',
            'badge_label' => 'Lorentz Invariant',
            'description' => 'Symbolically evaluate the velocity-dependent relativistic mass and canonical momentum.',
            'icon' => '🪐',
            'theme' => 'relativity'
        ],
        'holonomic-constraints' => [
            'url' => '/physics/legendre-transformer?preset=singular&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Inspect Singular Constraints',
            'badge_label' => 'Dirac Brackets',
            'description' => 'Analyze degenerate Lagrangians with vanishing Hessian determinant det(W) = 0.',
            'icon' => '🧮',
            'theme' => 'theoretical'
        ],
        'central-force' => [
            'url' => '/physics/legendre-transformer?preset=central_force&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Invert 2D Central Potential',
            'badge_label' => 'Angular Momentum',
            'description' => 'Compute curvilinear 2D central force canonical momenta and cyclic coordinate conservation.',
            'icon' => '🪐',
            'theme' => 'classical'
        ],
        'keplers-second-law' => [
            'url' => '/physics/legendre-transformer?preset=kepler&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Derive Kepler Hamiltonian',
            'badge_label' => 'Areal Velocity / p_phi',
            'description' => 'Perform exact Legendre duality on the gravitational two-body problem with cyclic azimuthal angle.',
            'icon' => '🛰️',
            'theme' => 'astrophysics'
        ],
        'rotational-dynamics' => [
            'url' => '/physics/legendre-transformer?preset=coriolis&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Analyze Rotating Frame Duality',
            'badge_label' => 'Coriolis / Gauge Shift',
            'description' => 'Evaluate velocity-coupled rotating frames with non-diagonal momentum shifts and centrifugal potential.',
            'icon' => '🌀',
            'theme' => 'classical'
        ],
        'coupled-oscillations' => [
            'url' => '/physics/legendre-transformer?preset=duffing&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Analyze Anharmonic Duality',
            'badge_label' => 'Duffing Quartic',
            'description' => 'Perform exact canonical Legendre transformation on nonlinear quartic oscillator potentials.',
            'icon' => '🎛️',
            'theme' => 'classical'
        ],

        // 2. Noether's Vault (Symmetries & Conserved Currents)
        'noethers-theorem' => [
            'url' => '/physics/noethers-vault?symmetry=time_translation',
            'tool_name' => 'Noether\'s Vault',
            'action_label' => 'Test Symmetries in Noether\'s Vault',
            'badge_label' => 'Lie Symmetry ↔ Current',
            'description' => 'Perturb continuous spacetime coordinates to observe non-zero current divergence ∂_μ J^μ ≠ 0.',
            'icon' => '🏛️',
            'theme' => 'theoretical'
        ],
        'conserved-charge' => [
            'url' => '/physics/noethers-vault?symmetry=gauge_u1',
            'tool_name' => 'Noether\'s Vault',
            'action_label' => 'Inspect Global U(1) Charge',
            'badge_label' => 'Internal Symmetry',
            'description' => 'Rotate complex field phasors globally to verify electric charge conservation.',
            'icon' => '⚡',
            'theme' => 'theoretical'
        ],
        'four-momentum' => [
            'url' => '/physics/noethers-vault?symmetry=space_translation',
            'tool_name' => 'Noether\'s Vault',
            'action_label' => 'Trace Spatial Homogeneity',
            'badge_label' => 'Momentum Flux Tensor',
            'description' => 'Verify linear momentum conservation from translational invariance of the Lagrangian.',
            'icon' => '🏛️',
            'theme' => 'relativity'
        ],
        'lorentz-transformation' => [
            'url' => '/physics/noethers-vault?symmetry=lorentz_boost',
            'tool_name' => 'Noether\'s Vault',
            'action_label' => 'Simulate Lorentz Boost Invariance',
            'badge_label' => 'Poincaré Generator',
            'description' => 'Hyperbolically rotate spacetime axes to observe center-of-mass invariants.',
            'icon' => '🌌',
            'theme' => 'relativity'
        ],

        // 3. Classical-to-Quantum Correspondence Workspace
        'ehrenfest-theorem' => [
            'url' => '/physics/correspondence-workspace?mode=ehrenfest&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Launch Ehrenfest\'s Sandbox',
            'badge_label' => 'Expectation vs Classical',
            'description' => 'Track wave packet expectation values ⟨x⟩, ⟨p⟩ alongside Newton-Verlet trajectories.',
            'icon' => '⚛️',
            'theme' => 'quantum'
        ],
        'schrodinger-equation' => [
            'url' => '/physics/correspondence-workspace?mode=ehrenfest&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Simulate Schrödinger Wave Packet',
            'badge_label' => 'Crank-Nicolson Solver',
            'description' => 'Propagate complex quantum wavefunctions across arbitrary potential barriers.',
            'icon' => '⚛️',
            'theme' => 'quantum'
        ],
        'wave-packet' => [
            'url' => '/physics/correspondence-workspace?mode=ehrenfest&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Observe Wave Packet Dispersion',
            'badge_label' => 'Dispersive Medium',
            'description' => 'Contrast coherent state dispersion against harmonic oscillator restoration.',
            'icon' => '👻',
            'theme' => 'quantum'
        ],
        'quantum-tunneling' => [
            'url' => '/physics/correspondence-workspace?mode=ehrenfest&pot=barrier',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Simulate Barrier Penetration',
            'badge_label' => 'Evanescent Decay',
            'description' => 'Observe wave packet splitting and calculate transmission coefficients across finite potential walls.',
            'icon' => '👻',
            'theme' => 'quantum'
        ],
        'born-rule' => [
            'url' => '/physics/correspondence-workspace?mode=phase&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Inspect Wigner Phase Flow',
            'badge_label' => 'Quasi-Probability',
            'description' => 'Map quantum state probabilities into Wigner phase space with Moyal bracket dynamics.',
            'icon' => '⚛️',
            'theme' => 'quantum'
        ],

        // 4. Anthropic Constant Tuner & Cosmological Sandbox
        'fine-structure-constant' => [
            'url' => '/physics/anthropic-tuner?preset=weak_alpha',
            'tool_name' => 'The Multiverse Creator',
            'action_label' => 'Tune Fine-Structure Constant (α)',
            'badge_label' => 'Atomic Stability Dial',
            'description' => 'Vary α to test the stability of atomic orbitals, chemistry, and molecular bonding.',
            'icon' => '🌌',
            'theme' => 'astrophysics'
        ],
        'universal-gravitation' => [
            'url' => '/physics/anthropic-tuner?preset=weak_gravity',
            'tool_name' => 'The Multiverse Creator',
            'action_label' => 'Tune Gravitational Constant (G)',
            'badge_label' => 'Cosmic Dial',
            'description' => 'Adjust the universal gravitational constant to simulate planetary orbits and stellar lifetimes.',
            'icon' => '🪐',
            'theme' => 'astrophysics'
        ],
        'black-hole-thermodynamics' => [
            'url' => '/physics/anthropic-tuner?preset=collapse',
            'tool_name' => 'The Multiverse Creator',
            'action_label' => 'Simulate ISCO Gravitational Collapse',
            'badge_label' => 'Event Horizon Limit',
            'description' => 'Crank gravity to collapse orbital trajectories past the Innermost Stable Circular Orbit.',
            'icon' => '🌌',
            'theme' => 'astrophysics'
        ],

        // 5. The Rosetta Stone (Notation Toggle)
        'maxwells-equations' => [
            'url' => '/physics/notation-toggle?theory=maxwell&rep=relativistic_tensor',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Compare Maxwell Formalisms',
            'badge_label' => 'Vectors ↔ Tensors ↔ Forms',
            'description' => 'Toggle electrodynamics between 3D Gibbs vector calculus, 4D spacetime tensors, and Cartan differential forms.',
            'icon' => '📐',
            'theme' => 'electromagnetism'
        ],
        'einstein-field-equations' => [
            'url' => '/physics/notation-toggle?theory=einstein&rep=standard_tensor',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Toggle General Relativity Formalisms',
            'badge_label' => 'Curvature Geometry',
            'description' => 'Compare the Einstein tensor equation with the Einstein-Hilbert action and Cartan tetrad forms.',
            'icon' => '📐',
            'theme' => 'relativity'
        ],
        'differential-forms' => [
            'url' => '/physics/notation-toggle?theory=maxwell&rep=differential_forms',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Inspect Cartan Exterior Calculus',
            'badge_label' => 'dF = 0 Flux Invariant',
            'description' => 'Explore coordinate-free exterior differential forms and Hodge star dualities.',
            'icon' => '📐',
            'theme' => 'math-methods'
        ],
        'dirac-equation' => [
            'url' => '/physics/notation-toggle?theory=dirac&rep=covariant_form',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Toggle Dirac Spinor Formalisms',
            'badge_label' => 'Clifford Algebra',
            'description' => 'Compare covariant gamma matrix formulation with Hamiltonian and Weyl two-component spinors.',
            'icon' => '📐',
            'theme' => 'standard-model'
        ],

        // 6. Direct Flagship Simulation Matches
        'pendulum' => [
            'url' => '/physics/simulations/pendulum',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Run Chaotic Pendulum Simulation',
            'badge_label' => 'RK4 Poincaré Section',
            'description' => 'Explore deterministic chaos, period-doubling bifurcations, and phase-space attractors.',
            'icon' => '⏳',
            'theme' => 'classical'
        ],
        'double-pendulum' => [
            'url' => '/physics/simulations/double-pendulum',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Launch Double Pendulum Chaos Solver',
            'badge_label' => 'Lyapunov Exponent',
            'description' => 'Run live Runge-Kutta 4th-order coupled pendula with extreme sensitivity to initial conditions.',
            'icon' => '⏳',
            'theme' => 'classical'
        ],
        'projectile-motion' => [
            'url' => '/physics/simulations/projectile-motion',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Launch Newton\'s Orbital Cannon',
            'badge_label' => 'Keplerian Trajectories',
            'description' => 'Simulate spherical central-force gravity, sub-orbital trajectories, orbital insertion, and cosmic escape.',
            'icon' => '🪐',
            'theme' => 'classical'
        ],
        'reynolds-number' => [
            'url' => '/physics/simulations/vortex-street',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Simulate Kármán Vortex Shedding',
            'badge_label' => 'Navier-Stokes Solver',
            'description' => 'Simulate boundary-layer separation and alternating vortex street shedding past a cylinder.',
            'icon' => '🌊',
            'theme' => 'fluids'
        ],
        'second-law-of-thermodynamics' => [
            'url' => '/physics/simulations/maxwells-demon',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Test Maxwell\'s Demon Paradox',
            'badge_label' => 'Information Entropy',
            'description' => 'Filter hot and cold particles to explore Landauer\'s principle and entropic cost.',
            'icon' => '🔥',
            'theme' => 'thermodynamics'
        ]
    ];

    /**
     * Domain fallback mappings for encyclopedia subtopics without an explicit override.
     */
    private static array $domainFallbacks = [
        'classical-mechanics' => [
            'url' => '/physics/legendre-transformer?preset=sho&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Open in Analytical Workbench',
            'badge_label' => 'SymPy CAS Duality',
            'description' => 'Evaluate Lagrangian-to-Hamiltonian Legendre transformations and canonical phase trajectories.',
            'icon' => '🧮',
            'theme' => 'classical'
        ],
        'quantum-physics' => [
            'url' => '/physics/correspondence-workspace?mode=ehrenfest&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Launch Quantum Correspondence',
            'badge_label' => 'Crank-Nicolson Solver',
            'description' => 'Observe wave packet evolution, expectation value divergence, and phase space Wigner distributions.',
            'icon' => '⚛️',
            'theme' => 'quantum'
        ],
        'relativity' => [
            'url' => '/physics/notation-toggle?theory=einstein&rep=standard_tensor',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Compare Relativistic Formalisms',
            'badge_label' => 'Tensor Geometry',
            'description' => 'Toggle equations between 3D vector projections, 4D spacetime tensors, and exterior forms.',
            'icon' => '📐',
            'theme' => 'relativity'
        ],
        'electromagnetism' => [
            'url' => '/physics/notation-toggle?theory=maxwell&rep=relativistic_tensor',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Compare Electromagnetic Formalisms',
            'badge_label' => 'Gibbs vs Covariant',
            'description' => 'Switch between Gibbs vector calculus, 4D relativistic tensors, and differential forms.',
            'icon' => '⚡',
            'theme' => 'electromagnetism'
        ],
        'astrophysics' => [
            'url' => '/physics/anthropic-tuner?preset=collapse',
            'tool_name' => 'The Multiverse Creator',
            'action_label' => 'Tune Cosmological Dials',
            'badge_label' => 'Cosmic Scaling',
            'description' => 'Simulate gravitational stability bounds, nuclear fusion pressure, and orbital limits.',
            'icon' => '🌌',
            'theme' => 'astrophysics'
        ],
        'theoretical-physics' => [
            'url' => '/physics/noethers-vault?symmetry=time_translation',
            'tool_name' => 'Noether\'s Vault',
            'action_label' => 'Test Symmetries in Noether\'s Vault',
            'badge_label' => 'Symmetry & Conservation',
            'description' => 'Trace continuous Lie group symmetries to conserved physical Noether currents.',
            'icon' => '🏛️',
            'theme' => 'theoretical'
        ],
        'standard-model' => [
            'url' => '/physics/notation-toggle?theory=dirac&rep=covariant_form',
            'tool_name' => 'The Rosetta Stone of Physics',
            'action_label' => 'Inspect Quantum Field Formalisms',
            'badge_label' => 'Dirac Spinors',
            'description' => 'Compare Dirac equation representations across covariant, Hamiltonian, and chiral forms.',
            'icon' => '📐',
            'theme' => 'standard-model'
        ],
        'thermodynamics-statistical-mechanics' => [
            'url' => '/physics/simulations/maxwells-demon',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Launch Thermodynamic Simulation',
            'badge_label' => 'Entropy Sandbox',
            'description' => 'Explore microstates, Maxwell-Boltzmann velocity distributions, and information entropy.',
            'icon' => '🔥',
            'theme' => 'thermodynamics'
        ],
        'fluids-nonlinear' => [
            'url' => '/physics/simulations/vortex-street',
            'tool_name' => 'Simulations Observatory',
            'action_label' => 'Run Nonlinear Fluid Simulation',
            'badge_label' => 'Fluid Shedding',
            'description' => 'Observe vorticity shedding, boundary-layer turbulence, and nonlinear chaotic flow.',
            'icon' => '🌊',
            'theme' => 'fluids'
        ],
        'condensed-matter' => [
            'url' => '/physics/correspondence-workspace?mode=phase&pot=harmonic',
            'tool_name' => 'Correspondence Workspace',
            'action_label' => 'Explore Phase Space Manifold',
            'badge_label' => 'Phase Coherence',
            'description' => 'Analyze collective quantum states and phase space dynamics in lattice structures.',
            'icon' => '⚛️',
            'theme' => 'condensed'
        ],
        'mathematical-methods' => [
            'url' => '/physics/legendre-transformer?preset=central_force&autorun=1',
            'tool_name' => 'Analytical Mechanics Workbench',
            'action_label' => 'Symbolic CAS Workspace',
            'badge_label' => 'SymPy CAS Engine',
            'description' => 'Invert coupled curvilinear coordinates, evaluate Jacobian determinants, and solve stationary metrics.',
            'icon' => '🧮',
            'theme' => 'math-methods'
        ],
        'philosophy-of-physics' => [
            'url' => '/physics/anthropic-tuner?preset=standard',
            'tool_name' => 'The Multiverse Creator',
            'action_label' => 'Explore Cosmological Constants',
            'badge_label' => 'Anthropic Crucible',
            'description' => 'Test the fine-tuning of fundamental physical constants against anthropic boundaries.',
            'icon' => '🌌',
            'theme' => 'philosophy'
        ]
    ];

    /**
     * Resolves the optimal Lab Tool launcher for a given subtopic slug.
     * 
     * @param string $slug Subtopic slug identifier
     * @param string $parentSlug Parent category slug or domain
     * @return array Launcher metadata array
     */
    public static function resolve(string $slug, string $parentSlug = ''): array
    {
        // 1. Direct match in curated mappings
        if (isset(self::$specificMappings[$slug])) {
            return self::$specificMappings[$slug];
        }

        // 2. Canonical alias or partial slug match
        $normalizedSlug = strtolower(trim($slug));
        foreach (self::$specificMappings as $pattern => $config) {
            if (strpos($normalizedSlug, $pattern) !== false || strpos($pattern, $normalizedSlug) !== false) {
                return $config;
            }
        }

        // 3. Domain fallback
        $normalizedParent = strtolower(trim($parentSlug));
        if (!empty($normalizedParent) && isset(self::$domainFallbacks[$normalizedParent])) {
            return self::$domainFallbacks[$normalizedParent];
        }

        // 4. Default to Unified Physics Cockpit
        return [
            'url' => '/physics/lab-tools',
            'tool_name' => 'The Unified Physics Laboratory',
            'action_label' => 'Open in Lab Tools Cockpit',
            'badge_label' => 'Crucible & Prisms',
            'description' => 'Explore the mathematical symmetries, phase space flows, and quantum transitions governing this physical manifold.',
            'icon' => '🔬',
            'theme' => 'default'
        ];
    }
}
