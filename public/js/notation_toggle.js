/**
 * Physics Lab — The Physics Rosetta Stone (Multi-Representation Notation Toggle)
 * Interactive side-by-side representation translator for 5 foundational physical laws.
 */

const THEORIES = [
    {
        id: "maxwell",
        title: "Maxwell's Equations",
        category: "Electromagnetism",
        description: "The classical equations of electrodynamics describing how electric and magnetic fields are generated and altered by each other and by charges and currents.",
        accentColor: "#00d2ff",
        accentBg: "rgba(0, 210, 255, 0.10)",
        accentBorder: "rgba(0, 210, 255, 0.35)",
        representations: [
            {
                id: "gibbs_differential",
                name: "Gibbs Vector (Differential)",
                tags: ["4 Vector PDEs", "Local 3D Calculus", "Engineering & Optics"],
                mappings: [
                    "\\nabla \\cdot \\mathbf{E} \\leftrightarrow \\text{Local Charge}",
                    "\\nabla \\times \\mathbf{E} \\leftrightarrow \\text{Faraday Induction}",
                    "\\text{3D Space} + \\text{Time } t"
                ],
                equation: "\\[\\begin{aligned} \\nabla \\cdot \\mathbf{E} &= \\frac{\\rho}{\\varepsilon_0} \\\\ \\nabla \\times \\mathbf{E} &= -\\frac{\\partial \\mathbf{B}}{\\partial t} \\\\ \\nabla \\cdot \\mathbf{B} &= 0 \\\\ \\nabla \\times \\mathbf{B} &= \\mu_0 \\mathbf{J} + \\mu_0 \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t} \\end{aligned}\\]",
                insight: "Formulates electrodynamics locally at every point in space using 3D vector calculus operators divergence (\\(\\nabla \\cdot\\)) and curl (\\(\\nabla \\times\\)). The divergence of the electric field yields local charge density, while the curl of the electric field matches the change in magnetic fields over time.",
                utility: "Extremely useful for solving local field distributions, wave propagation, waveguides, antenna design, and localized boundary-value problems in engineering and applied physics.",
                glossary: [
                    { symbol: "\\nabla", name: "Del / Nabla Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#nabla-operator" },
                    { symbol: "\\mathbf{E}", name: "Electric Field Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-3}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#electric-field" },
                    { symbol: "\\mathbf{B}", name: "Magnetic Field Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#magnetic-field" },
                    { symbol: "\\rho", name: "Electric Charge Density", dimension: "\\mathsf{L}^{-3}\\cdot\\mathsf{T}\\cdot\\mathsf{I}", link: "/physics/symbols#charge-density" },
                    { symbol: "\\mathbf{J}", name: "Electric Current Density Vector", dimension: "\\mathsf{L}^{-2}\\cdot\\mathsf{I}", link: "/physics/symbols#current-density" },
                    { symbol: "\\varepsilon_0", name: "Vacuum Permittivity Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{-3}\\cdot\\mathsf{T}^{4}\\cdot\\mathsf{I}^{2}", link: "/physics/constants#epsilon-0" },
                    { symbol: "\\mu_0", name: "Vacuum Permeability Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-2}", link: "/physics/constants#mu-0" }
                ]
            },
            {
                id: "gibbs_integral",
                name: "Gibbs Vector (Integral)",
                tags: ["4 Surface/Loop Integrals", "Global Flux & Circulation", "High Symmetry"],
                mappings: [
                    "\\nabla \\cdot \\longrightarrow \\oint_{\\partial V} \\mathbf{E}\\cdot d\\mathbf{a}",
                    "\\nabla \\times \\longrightarrow \\oint_{\\partial S} \\mathbf{E}\\cdot d\\mathbf{l}",
                    "\\rho, \\mathbf{J} \\longrightarrow Q, I"
                ],
                equation: "\\[\\begin{aligned} \\oint_{\\partial V} \\mathbf{E} \\cdot d\\mathbf{a} &= \\frac{Q}{\\varepsilon_0} \\\\ \\oint_{\\partial S} \\mathbf{E} \\cdot d\\mathbf{l} &= -\\frac{d}{dt} \\iint_S \\mathbf{B} \\cdot d\\mathbf{a} \\\\ \\oint_{\\partial V} \\mathbf{B} \\cdot d\\mathbf{a} &= 0 \\\\ \\oint_{\\partial S} \\mathbf{B} \\cdot d\\mathbf{l} &= \\mu_0 I + \\mu_0\\varepsilon_0 \\frac{d}{dt} \\iint_S \\mathbf{E} \\cdot d\\mathbf{a} \\end{aligned}\\]",
                insight: "Describes the global flux and circulation of fields through enclosing 2D surfaces (\\(\\partial V\\)) and bounding loops (\\(\\partial S\\)). These integral forms correspond directly to the classic experimental laws of Gauss, Faraday, and Ampère.",
                utility: "Best for computing fields in systems with high symmetry (spherical, cylindrical, or planar) where integration contours align with the field geometry, allowing rapid analysis of capacitors, solenoids, and wires.",
                glossary: [
                    { symbol: "\\mathbf{E}", name: "Electric Field Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-3}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#electric-field" },
                    { symbol: "\\mathbf{B}", name: "Magnetic Field Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#magnetic-field" },
                    { symbol: "Q", name: "Total Enclosed Electric Charge", dimension: "\\mathsf{T}\\cdot\\mathsf{I}", link: "/physics/symbols#electric-charge" },
                    { symbol: "I", name: "Total Enclosed Electric Current", dimension: "\\mathsf{I}", link: "/physics/symbols#electric-current" },
                    { symbol: "d\\mathbf{a}", name: "Differential Area Vector", dimension: "\\mathsf{L}^{2}", link: "/physics/symbols#area" },
                    { symbol: "d\\mathbf{l}", name: "Differential Path Length Vector", dimension: "\\mathsf{L}", link: "/physics/symbols#length" },
                    { symbol: "\\varepsilon_0", name: "Vacuum Permittivity Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{-3}\\cdot\\mathsf{T}^{4}\\cdot\\mathsf{I}^{2}", link: "/physics/constants#epsilon-0" },
                    { symbol: "\\mu_0", name: "Vacuum Permeability Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-2}", link: "/physics/constants#mu-0" }
                ]
            },
            {
                id: "relativistic_tensor",
                name: "Relativistic Tensor",
                tags: ["4 PDEs → 2 Equations", "Manifestly Lorentz Covariant", "4D Minkowski"],
                mappings: [
                    "\\mathbf{E}, \\mathbf{B} \\longrightarrow F^{\\mu\\nu}",
                    "\\rho, \\mathbf{J} \\longrightarrow J^\\nu",
                    "\\partial_t, \\nabla \\longrightarrow \\partial_\\mu"
                ],
                equation: "\\[\\begin{aligned} \\partial_\\mu F^{\\mu\\nu} &= \\mu_0 J^\\nu \\\\ \\partial_{[\\mu} F_{\\nu\\rho]} &= 0 \\end{aligned}\\]",
                insight: "Unifies the 3D electric and magnetic fields into a single, antisymmetric rank-2 field strength tensor \\(F^{\\mu\\nu}\\) on 4D Minkowski spacetime. The sources are combined into a single 4-current vector \\(J^\\nu\\). This structure makes special relativity manifest.",
                utility: "Fundamental in relativistic mechanics, accelerator physics, and particle physics. Expresses electrodynamics in a form that remains invariant under arbitrary coordinate changes (general covariance).",
                glossary: [
                    { symbol: "F^{\\mu\\nu}", name: "Electromagnetic Field Tensor", dimension: "\\mathsf{M}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#electromagnetic-tensor" },
                    { symbol: "J^\\nu", name: "Four-Current Density Vector", dimension: "\\mathsf{L}^{-2}\\cdot\\mathsf{I}", link: "/physics/symbols#four-current-density" },
                    { symbol: "\\partial_\\mu", name: "Four-Gradient Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#four-gradient" },
                    { symbol: "\\mu_0", name: "Vacuum Permeability Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-2}", link: "/physics/constants#mu-0" }
                ]
            },
            {
                id: "differential_forms",
                name: "Differential Forms",
                tags: ["Coordinate-Free", "2 Lines Total", "Gauge Theory & Topology"],
                mappings: [
                    "F_{\\mu\\nu} \\longrightarrow F = \\tfrac{1}{2} F_{\\mu\\nu} dx^\\mu \\wedge dx^\\nu",
                    "\\partial_{[\\mu}F_{\\nu\\rho]}=0 \\longrightarrow dF = 0",
                    "\\partial_\\mu F^{\\mu\\nu}=\\mu_0 J^\\nu \\longrightarrow d{\\star}F = \\mu_0 J"
                ],
                equation: "\\[\\begin{aligned} dF &= 0 \\\\ d{\\star}F &= \\mu_0 J \\end{aligned}\\]",
                insight: "Expresses electrodynamics completely free of coordinates using differential forms. The field strength becomes a 2-form \\(F\\), and the equations are formulated using the exterior derivative \\(d\\) and Hodge star operator \\(\\star\\). The equation \\(dF=0\\) defines the topological conservation of magnetic flux.",
                utility: "Invaluable in gauge field theory, general relativity, and topological physics. Demonstrates that electrodynamics is fundamentally a geometric/topological statement on a manifold.",
                glossary: [
                    { symbol: "F", name: "Electromagnetic 2-form", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#electromagnetic-form" },
                    { symbol: "J", name: "Source 3-form", dimension: "\\mathsf{I}\\cdot\\mathsf{T}", link: "/physics/symbols#source-form" },
                    { symbol: "d", name: "Exterior Derivative Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#exterior-derivative" },
                    { symbol: "\\star", name: "Hodge Dual Operator", dimension: "dimensionless", link: "/physics/symbols#hodge-dual" },
                    { symbol: "\\mu_0", name: "Vacuum Permeability Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-2}", link: "/physics/constants#mu-0" }
                ]
            }
        ]
    },
    {
        id: "classical",
        title: "Classical Mechanics",
        category: "Analytical Mechanics",
        description: "The evolution of mechanical systems translated from vector forces to variational action principles, phase-space flows, and symplectic Poisson geometry.",
        accentColor: "#10b981",
        accentBg: "rgba(16, 185, 129, 0.10)",
        accentBorder: "rgba(16, 185, 129, 0.35)",
        representations: [
            {
                id: "newtonian_vector",
                name: "Newtonian Vector",
                tags: ["3D Forces", "2nd-Order ODE", "Direct Kinematics"],
                mappings: [
                    "\\mathbf{F} \\leftrightarrow \\text{External Vector Force}",
                    "\\mathbf{p} = m\\dot{\\mathbf{r}}",
                    "\\text{Explicit Constraint Forces Required}"
                ],
                equation: "\\[ \\mathbf{F} = \\frac{d\\mathbf{p}}{dt} = m\\ddot{\\mathbf{r}} \\]",
                insight: "Formulates motion through vector forces acting instantaneously on point masses in inertial Cartesian coordinates. Every holonomic constraint (wires, surfaces, hinges) must be resolved via explicit normal reaction forces.",
                utility: "Ideal for straightforward free-body diagrams, orbital mechanics, dissipative friction systems, and engineering dynamics where forces are known directly.",
                glossary: [
                    { symbol: "\\mathbf{F}", name: "Net Force Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}", link: null },
                    { symbol: "\\mathbf{p}", name: "Linear Momentum", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#linear-momentum" },
                    { symbol: "m", name: "Particle Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" },
                    { symbol: "t", name: "Coordinate Time", dimension: "\\mathsf{T}", link: "/physics/symbols#time-t" }
                ]
            },
            {
                id: "euler_lagrange",
                name: "Euler–Lagrange (Variational)",
                tags: ["Coordinate-Free", "Scalar Energies T − V", "No Constraint Forces"],
                mappings: [
                    "\\mathbf{F} \\longrightarrow L = T - V",
                    "\\mathbf{r} \\longrightarrow q_i \\text{ (Generalized)}",
                    "\\delta S = \\delta \\int L\\,dt = 0"
                ],
                equation: "\\[ \\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) - \\frac{\\partial L}{\\partial q_i} = 0 \\]",
                insight: "Replaces vector forces with a single scalar Lagrangian \\(L(q, \\dot{q}, t) = T - V\\). Extremizing the action functional \\(S = \\int L\\,dt\\) automatically eliminates constraint forces and reveals conserved quantities via Noether's theorem.",
                utility: "Indispensable for coupled pendula, curvilinear coordinates, continuum field theory, general relativity, and path-integral quantization.",
                glossary: [
                    { symbol: "L", name: "Lagrangian Function", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#lagrangian" },
                    { symbol: "q_i", name: "Generalized Coordinates", dimension: "\\text{varies}", link: "/physics/symbols#generalized-coordinates" },
                    { symbol: "\\dot{q}_i", name: "Generalized Velocities", dimension: "\\text{varies}", link: "/physics/symbols#generalized-velocities" },
                    { symbol: "S", name: "Action Functional", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#action-integral" }
                ]
            },
            {
                id: "hamilton_canonical",
                name: "Hamilton's Equations",
                tags: ["2N 1st-Order ODEs", "Phase Space (q, p)", "Legendre Dual"],
                mappings: [
                    "L(q, \\dot{q}) \\xrightarrow{\\text{Legendre}} H(q, p) = \\sum p_i\\dot{q}_i - L",
                    "p_i = \\partial L / \\partial \\dot{q}_i",
                    "\\text{Configuration Space} \\longrightarrow \\text{Phase Space}"
                ],
                equation: "\\[\\begin{aligned} \\dot{q}_i &= \\frac{\\partial H}{\\partial p_i} \\\\ \\dot{p}_i &= -\\frac{\\partial H}{\\partial q_i} \\end{aligned}\\]",
                insight: "Applies a Legendre transformation to trade generalized velocities \\(\\dot{q}_i\\) for canonical momenta \\(p_i\\), turning \\(N\\) second-order equations into \\(2N\\) symmetric first-order phase-space flow equations preserving Liouville volume.",
                utility: "The foundation of statistical mechanics, symplectic numerical integrators, chaos theory, and canonical quantization in quantum mechanics.",
                glossary: [
                    { symbol: "H", name: "Hamiltonian Function", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#hamiltonian" },
                    { symbol: "q_i", name: "Generalized Coordinates", dimension: "\\text{varies}", link: "/physics/symbols#generalized-coordinates" },
                    { symbol: "p_i", name: "Canonical Momentum", dimension: "\\text{varies}", link: "/physics/symbols#canonical-momentum" }
                ]
            },
            {
                id: "poisson_symplectic",
                name: "Poisson Brackets",
                tags: ["Lie Algebra", "Bridge to Quantum [f, H]", "Observable Flow"],
                mappings: [
                    "\\dot{q}_i, \\dot{p}_i \\longrightarrow \\frac{df}{dt} = \\{f, H\\} + \\frac{\\partial f}{\\partial t}",
                    "\\{q_i, p_j\\} = \\delta_{ij}",
                    "\\{\\cdot, \\cdot\\} \\xrightarrow{\\text{Dirac}} \\frac{1}{i\\hbar}[\\cdot, \\cdot]"
                ],
                equation: "\\[ \\frac{df}{dt} = \\{f, H\\} + \\frac{\\partial f}{\\partial t}, \\quad \\{f, g\\} = \\sum_i \\left(\\frac{\\partial f}{\\partial q_i}\\frac{\\partial g}{\\partial p_i} - \\frac{\\partial f}{\\partial p_i}\\frac{\\partial g}{\\partial q_i}\\right) \\]",
                insight: "Elevates dynamics to an algebraic bracket on phase-space observables \\(f(q, p, t)\\). Any observable whose Poisson bracket with \\(H\\) vanishes is an exact constant of motion, and the bracket maps directly to the quantum commutator.",
                utility: "Essential for canonical transformations, perturbation theory, integrable systems, and Dirac's canonical quantization bridge to quantum mechanics.",
                glossary: [
                    { symbol: "\\{f, H\\}", name: "Poisson Bracket", dimension: "\\text{varies}", link: null },
                    { symbol: "H", name: "Hamiltonian Function", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#hamiltonian" },
                    { symbol: "q_i", name: "Generalized Coordinates", dimension: "\\text{varies}", link: "/physics/symbols#generalized-coordinates" },
                    { symbol: "p_i", name: "Canonical Momentum", dimension: "\\text{varies}", link: "/physics/symbols#canonical-momentum" }
                ]
            }
        ]
    },
    {
        id: "einstein",
        title: "Einstein Field Equations",
        category: "General Relativity",
        description: "The central equations of Einstein's general theory of relativity, describing how the geometry of spacetime responds to the presence of mass, energy, and momentum.",
        accentColor: "#8b5cf6",
        accentBg: "rgba(139, 92, 246, 0.10)",
        accentBorder: "rgba(139, 92, 246, 0.35)",
        representations: [
            {
                id: "standard_tensor",
                name: "Standard Tensor",
                tags: ["10 Coupled Nonlinear PDEs", "Curvature = Matter", "Metric g_μν"],
                mappings: [
                    "G_{\\mu\\nu} = R_{\\mu\\nu} - \\tfrac{1}{2} R g_{\\mu\\nu}",
                    "\\text{Curvature} \\longleftrightarrow \\frac{8\\pi G}{c^4} T_{\\mu\\nu}",
                    "\\nabla^\\mu G_{\\mu\\nu} = 0 \\implies \\nabla^\\mu T_{\\mu\\nu} = 0"
                ],
                equation: "\\[ G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu} \\]",
                insight: "The standard tensor formulation relating local spacetime curvature (Einstein tensor \\(G_{\\mu\\nu}\\) and metric \\(g_{\\mu\\nu}\\)) to local energy-momentum density (tensor \\(T_{\\mu\\nu}\\)). Geometrically states: 'Spacetime tells matter how to move; matter tells spacetime how to curve.'",
                utility: "Standard interface used to compute cosmological models, stellar collapse, gravitational waves, and black hole solutions (e.g. Schwarzschild and Kerr metrics).",
                glossary: [
                    { symbol: "G_{\\mu\\nu}", name: "Einstein Curvature Tensor", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#einstein-tensor" },
                    { symbol: "g_{\\mu\\nu}", name: "Metric Tensor", dimension: "dimensionless", link: "/physics/symbols#metric-tensor" },
                    { symbol: "T_{\\mu\\nu}", name: "Stress-Energy Tensor", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{-1}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#stress-energy-tensor" },
                    { symbol: "G", name: "Newtonian Gravitational Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{3}\\cdot\\mathsf{T}^{-2}", link: "/physics/constants#G" },
                    { symbol: "c", name: "Speed of Light", dimension: "\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#c" },
                    { symbol: "\\Lambda", name: "Cosmological Constant", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#cosmological-constant-lambda" }
                ]
            },
            {
                id: "einstein_hilbert_action",
                name: "Einstein–Hilbert Action",
                tags: ["Variational Principle", "Scalar Functional", "Quantum Gravity"],
                mappings: [
                    "\\delta S / \\delta g^{\\mu\\nu} = 0 \\longrightarrow G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\kappa T_{\\mu\\nu}",
                    "\\text{10 Tensor Eqns} \\longrightarrow 1\\text{ Scalar Action}",
                    "\\sqrt{-g}\\,d^4x \\leftrightarrow \\text{Invariant Volume}"
                ],
                equation: "\\[ S = \\int_{\\mathcal{M}} \\left( \\frac{R - 2\\Lambda}{16\\pi G/c^4} \\right) \\sqrt{-g} \\, d^4x + S_{\\text{matter}} \\]",
                insight: "Formulates general relativity through the Principle of Least Action. Taking the variational derivative of \\(S\\) with respect to the inverse metric \\(g^{\\mu\\nu}\\) yields the complete Einstein Field Equations.",
                utility: "Crucial for studying quantum gravity, string theory, and cosmological field modifications. Provides a unified starting point to couple gravity to other fundamental forces.",
                glossary: [
                    { symbol: "S", name: "Action Integral", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#action-integral" },
                    { symbol: "R", name: "Ricci Scalar Curvature", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#ricci-scalar" },
                    { symbol: "g", name: "Determinant of Metric Tensor", dimension: "dimensionless", link: "/physics/symbols#determinant-metric" },
                    { symbol: "G", name: "Newtonian Gravitational Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{3}\\cdot\\mathsf{T}^{-2}", link: "/physics/constants#G" },
                    { symbol: "c", name: "Speed of Light", dimension: "\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#c" },
                    { symbol: "\\Lambda", name: "Cosmological Constant", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#cosmological-constant-lambda" }
                ]
            },
            {
                id: "cartan_tetrad",
                name: "Cartan Tetrad (Frame Fields)",
                tags: ["Orthonormal Frames", "Gauge Theory of Gravity", "Spinors in Curved Space"],
                mappings: [
                    "g_{\\mu\\nu} \\longrightarrow \\eta_{ab}\\,\\theta^a_\\mu\\theta^b_\\nu",
                    "\\Gamma^\\rho_{\\mu\\nu} \\longrightarrow \\omega^a_{\\,b}",
                    "R^\\rho_{\\,\\sigma\\mu\\nu} \\longrightarrow R^a_{\\,b} = d\\omega^a_{\\,b} + \\omega^a_{\\,c}\\wedge\\omega^c_{\\,b}"
                ],
                equation: "\\[\\begin{aligned} T^a &= d\\theta^a + \\omega^a_{\\,\,b} \\wedge \\theta^b = 0 \\\\ R^a_{\\,\,b} &= d\\omega^a_{\\,\,b} + \\omega^a_{\\,\,c} \\wedge \\omega^c_{\\,\,b} \\end{aligned}\\]",
                insight: "Reformulates general relativity in terms of orthonormal frame fields (tetrads/vielbeins \\(\\theta^a\\)) and spin connections \\(\\omega^a_{\\,\,b}\\) rather than coordinate metrics. Represents gravity as a gauge theory of the Poincaré group.",
                utility: "Highly important for coupling spin-1/2 Dirac fermions to gravity in curved spacetime. Essential for Einstein-Cartan theory, supergravity, and loop quantum gravity.",
                glossary: [
                    { symbol: "\\theta^a", name: "Coframe / Tetrad 1-form", dimension: "\\mathsf{L}", link: "/physics/symbols#tetrad" },
                    { symbol: "\\omega^a_{\\,\,b}", name: "Spin Connection 1-form", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#spin-connection" },
                    { symbol: "R^a_{\\,\,b}", name: "Curvature 2-form", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#curvature-form" },
                    { symbol: "T^a", name: "Torsion 2-form", dimension: "\\mathsf{L}", link: "/physics/symbols#torsion-form" }
                ]
            }
        ]
    },
    {
        id: "schrodinger",
        title: "Schrödinger Equation",
        category: "Quantum Mechanics",
        description: "The fundamental equation of non-relativistic quantum mechanics, determining the time-evolution of a quantum system's wave function.",
        accentColor: "#ff4e88",
        accentBg: "rgba(255, 78, 136, 0.10)",
        accentBorder: "rgba(255, 78, 136, 0.35)",
        representations: [
            {
                id: "position_space",
                name: "Position Space",
                tags: ["Wave PDE", "Spatial Probability |ψ|²", "Atoms & Tunneling"],
                mappings: [
                    "\\hat{\\mathbf{p}} \\longrightarrow -i\\hbar\\nabla",
                    "|\\Psi(t)\\rangle \\longrightarrow \\psi(\\mathbf{r}, t) = \\langle\\mathbf{r}|\\Psi(t)\\rangle",
                    "\\hat{T} \\longrightarrow -\\frac{\\hbar^2}{2m}\\nabla^2"
                ],
                equation: "\\[ i\\hbar \\frac{\\partial}{\\partial t} \\psi(\\mathbf{r}, t) = \\left[ -\\frac{\\hbar^2}{2m} \\nabla^2 + V(\\mathbf{r}) \\right] \\psi(\\mathbf{r}, t) \\]",
                insight: "Expresses quantum states as continuous spatial wave functions \\(\\psi(\\mathbf{r}, t)\\). The momentum operator is replaced by its spatial derivative representation \\(-i\\hbar\\nabla\\), turning dynamics into a partial differential wave equation.",
                utility: "The standard formulation used to solve atomic structures (like the Hydrogen atom), quantum wells, barrier tunneling, and molecular systems.",
                glossary: [
                    { symbol: "\\psi(\\mathbf{r}, t)", name: "Position-space Wave Function", dimension: "\\mathsf{L}^{-3/2}", link: "/physics/symbols#wave-function" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "m", name: "Particle Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" },
                    { symbol: "\\nabla^2", name: "Laplacian Operator", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#nabla-operator" },
                    { symbol: "V(\\mathbf{r})", name: "Potential Energy Field", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#potential-energy" }
                ]
            },
            {
                id: "momentum_space",
                name: "Momentum Space",
                tags: ["Fourier Dual", "Algebraic Kinetic Term", "Scattering & Solids"],
                mappings: [
                    "\\psi(\\mathbf{r},t) \\xrightarrow{\\mathcal{F}} \\phi(\\mathbf{p},t)",
                    "-\\frac{\\hbar^2}{2m}\\nabla^2 \\longrightarrow \\frac{\\mathbf{p}^2}{2m}",
                    "V(\\mathbf{r})\\psi \\longrightarrow (V * \\phi)(\\mathbf{p})"
                ],
                equation: "\\[ i\\hbar \\frac{\\partial}{\\partial t} \\phi(\\mathbf{p}, t) = \\frac{\\mathbf{p}^2}{2m} \\phi(\\mathbf{p}, t) + \\int V(\\mathbf{p} - \\mathbf{p}') \\phi(\\mathbf{p}', t) \\, d^3p' \\]",
                insight: "Expresses quantum states in terms of momentum coordinates \\(\\mathbf{p}\\). The kinetic energy becomes a simple multiplication term, while potential energy turns into a convolution integral. Represents the Fourier transform of the position space equation.",
                utility: "Best suited for periodic systems, scattering experiments (e.g. Born approximations), and free-electron field behaviors in solid state physics.",
                glossary: [
                    { symbol: "\\phi(\\mathbf{p}, t)", name: "Momentum-space Wave Function", dimension: "\\mathsf{M}^{-3/2}\\cdot\\mathsf{L}^{-3/2}\\cdot\\mathsf{T}^{3/2}", link: "/physics/symbols#wave-function" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "m", name: "Particle Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" },
                    { symbol: "\\mathbf{p}", name: "Momentum Coordinates Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#linear-momentum" },
                    { symbol: "V(\\mathbf{p})", name: "Fourier Transformed Potential", dimension: "dimensionless", link: "/physics/symbols#fourier-potential" }
                ]
            },
            {
                id: "braket_formalism",
                name: "Bra–Ket Formalism (Abstract)",
                tags: ["Basis-Independent", "Hilbert Space", "Quantum Computing"],
                mappings: [
                    "\\psi(\\mathbf{r},t) \\longrightarrow |\\Psi(t)\\rangle",
                    "-\\frac{\\hbar^2}{2m}\\nabla^2 + V \\longrightarrow \\hat{H}",
                    "\\text{Unitary Flow } U(t) = e^{-i\\hat{H}t/\\hbar}"
                ],
                equation: "\\[ i\\hbar \\frac{d}{dt} |\\Psi(t)\\rangle = \\hat{H} |\\Psi(t)\\rangle \\]",
                insight: "A representation-independent vector description in Hilbert space. Quantum states are coordinate-free vectors (kets \\(|\\Psi\\rangle\\)), and the physical Hamiltonian behaves as a linear self-adjoint operator \\(\\hat{H}\\).",
                utility: "Fundamental for quantum information, quantum computing, spin systems, and algebraic derivation steps. Avoids coordinate details to reveal clean vector-space symmetries.",
                glossary: [
                    { symbol: "|\\Psi(t)\\rangle", name: "Quantum State Vector (Ket)", dimension: "dimensionless", link: "/physics/symbols#state-vector" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "\\hat{H}", name: "Hamiltonian Operator", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#hamiltonian-operator" }
                ]
            },
            {
                id: "path_integral",
                name: "Path Integral (Feynman)",
                tags: ["Sum Over Histories", "Action S[x(t)]", "QFT & Classical Limit"],
                mappings: [
                    "i\\hbar\\partial_t\\psi = \\hat{H}\\psi \\longrightarrow \\int \\mathcal{D}[x]\\,e^{iS/\\hbar}",
                    "\\hbar \\to 0 \\longrightarrow \\delta S = 0 \\text{ (Classical Path)}",
                    "\\text{Manifestly Relativistic in QFT}"
                ],
                equation: "\\[ \\langle x_f | U(t_f, t_i) | x_i \\rangle = \\int \\mathcal{D}[x(t)] e^{\\frac{i}{\\hbar} S[x(t)]} \\]",
                insight: "Formulates quantum transitions as a sum over histories. The probability amplitude is calculated by integrating over all possible spatial paths connecting the initial and final states, weighted by the exponent of the classical action phase \\(e^{iS/\\hbar}\\).",
                utility: "Central to quantum field theory, particle physics, and statistical mechanics. Elegant for demonstrating the classical limit (when \\(\\hbar \\to 0\\), the classical path of least action dominates).",
                glossary: [
                    { symbol: "\\mathcal{D}[x(t)]", name: "Functional Path Integration Measure", dimension: "dimensionless", link: "/physics/symbols#path-measure" },
                    { symbol: "S[x(t)]", name: "Classical Action Functional", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#action-integral" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "U(t_f, t_i)", name: "Time Evolution Operator", dimension: "dimensionless", link: "/physics/symbols#evolution-operator" }
                ]
            }
        ]
    },
    {
        id: "dirac",
        title: "Dirac Equation",
        category: "Relativistic Quantum Mechanics",
        description: "Formulates relativistic quantum mechanics for spin-1/2 fermions, naturally explaining spin and predicting the existence of antimatter.",
        accentColor: "#6366f1",
        accentBg: "rgba(99, 102, 241, 0.10)",
        accentBorder: "rgba(99, 102, 241, 0.35)",
        representations: [
            {
                id: "covariant_form",
                name: "Covariant Spacetime Form",
                tags: ["Natural Units ℏ = c = 1", "4-Component Spinor", "QED & Particle Physics"],
                mappings: [
                    "\\gamma^0 = \\beta, \\quad \\gamma^i = \\beta\\alpha^i",
                    "\\{\\gamma^\\mu, \\gamma^\\nu\\} = 2\\eta^{\\mu\\nu}",
                    "\\text{First-Order in } \\partial_t \\text{ and } \\nabla"
                ],
                equation: "\\[ (i\\gamma^\\mu \\partial_\\mu - m)\\psi = 0 \\]",
                insight: "Standard covariant relativistic formulation. Relies on 4×4 complex matrices (gamma matrices \\(\\gamma^\\mu\\)) to yield an equation that is linear in both spatial and temporal derivatives, satisfying both special relativity and quantum mechanics.",
                utility: "The cornerstone of relativistic field theory, quantum electrodynamics (QED), and particle physics. Expresses electron and quark dynamics in manifestly covariant forms.",
                glossary: [
                    { symbol: "\\psi", name: "Dirac Spinor Wave Function", dimension: "\\mathsf{L}^{-3/2}", link: "/physics/symbols#dirac-spinor" },
                    { symbol: "\\gamma^\\mu", name: "Dirac Gamma Matrices", dimension: "dimensionless", link: "/physics/symbols#gamma-matrices" },
                    { symbol: "\\partial_\\mu", name: "Four-Gradient Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#four-gradient" },
                    { symbol: "m", name: "Fermion Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" }
                ]
            },
            {
                id: "hamiltonian_form",
                name: "Hamiltonian Form",
                tags: ["Schrödinger-Style", "Atomic Fine Structure", "Relativistic Chemistry"],
                mappings: [
                    "\\hat{H}_D = c\\boldsymbol{\\alpha}\\cdot\\hat{\\mathbf{p}} + \\beta mc^2",
                    "\\gamma^0 (i\\gamma^\\mu\\partial_\\mu - m) \\longrightarrow i\\hbar\\partial_t - \\hat{H}_D",
                    "\\text{Explicit } \\hbar, c \\text{ Restored}"
                ],
                equation: "\\[ i\\hbar \\frac{\\partial\\psi}{\\partial t} = \\left( c\\boldsymbol{\\alpha} \\cdot \\hat{\\mathbf{p}} + \\beta m c^2 \\right) \\psi \\]",
                insight: "Formulates the Dirac equation in standard Schrödinger time-evolution form. Explicitly isolates the spatial momentum operators and introduces alpha (\\(\\boldsymbol{\\alpha}\\)) and beta (\\(\\beta\\)) matrices to represent relativistic velocity and rest mass.",
                utility: "Directly useful for computing atomic energy level corrections (fine structure), relativistic corrections in quantum chemistry, and electron tunneling behaviors.",
                glossary: [
                    { symbol: "\\psi", name: "Dirac Spinor Wave Function", dimension: "\\mathsf{L}^{-3/2}", link: "/physics/symbols#dirac-spinor" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "\\boldsymbol{\\alpha}", name: "Dirac Alpha Matrices Vector", dimension: "dimensionless", link: "/physics/symbols#alpha-matrices" },
                    { symbol: "\\beta", name: "Dirac Beta Matrix", dimension: "dimensionless", link: "/physics/symbols#beta-matrix" },
                    { symbol: "\\hat{\\mathbf{p}}", name: "Momentum Operator", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#momentum-operator" },
                    { symbol: "m", name: "Fermion Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" },
                    { symbol: "c", name: "Speed of Light", dimension: "\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#c" }
                ]
            },
            {
                id: "weyl_chiral",
                name: "Weyl Chiral Form",
                tags: ["Left & Right Chirality", "2×2 Pauli Matrices", "Electroweak & Neutrinos"],
                mappings: [
                    "\\psi \\longrightarrow (\\psi_L, \\psi_R)^T",
                    "m \\leftrightarrow \\text{Left–Right Chirality Mixing}",
                    "m = 0 \\implies \\text{Decoupled Weyl Fermions}"
                ],
                equation: "\\[\\begin{aligned} i\\sigma^\\mu \\partial_\\mu \\psi_R &= m \\psi_L \\\\ i\\bar{\\sigma}^\\mu \\partial_\\mu \\psi_L &= m \\psi_R \\end{aligned}\\]",
                insight: "Decomposes the 4-component Dirac spinor into two 2-component Weyl spinors representing left-handed (\\(\\psi_L\\)) and right-handed (\\(\\psi_R\\)) chiral states. The mass term acts as a coupling coefficient that oscillates the particle between left and right chiral states.",
                utility: "Indispensable in high-energy physics, electroweak theory, and neutrino physics. When mass \\(m = 0\\), these equations decouple completely to yield independent Weyl equations.",
                glossary: [
                    { symbol: "\\psi_L", name: "Left-Handed Weyl Spinor", dimension: "\\mathsf{L}^{-3/2}", link: "/physics/symbols#weyl-spinor" },
                    { symbol: "\\psi_R", name: "Right-Handed Weyl Spinor", dimension: "\\mathsf{L}^{-3/2}", link: "/physics/symbols#weyl-spinor" },
                    { symbol: "\\sigma^\\mu", name: "Pauli Vector of Four-Matrices", dimension: "dimensionless", link: "/physics/symbols#pauli-four-vector" },
                    { symbol: "\\partial_\\mu", name: "Four-Gradient Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#four-gradient" },
                    { symbol: "m", name: "Fermion Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" }
                ]
            }
        ]
    }
];

let activeTheoryIndex = 0;
let activeRepIndex = 0;
let compareMode = false;
let compareRepIndex = 1;

/**
 * Triggers MathJax typesetting asynchronously on specific elements.
 */
function typesetMath(elements = null) {
    const target = elements ? (Array.isArray(elements) ? elements.filter(Boolean) : [elements]) : null;
    const run = () => {
        if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
            window.MathJax.typesetPromise(target)
                .catch(err => console.warn("MathJax typeset error:", err));
        }
    };
    if (window.MathJax && typeof window.MathJax.typesetPromise === "function") {
        run();
    } else if (typeof window.ensureMathJax === "function") {
        window.ensureMathJax().then(run).catch(() => {});
    } else if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
        window.MathJax.startup.promise.then(run);
    } else {
        setTimeout(run, 150);
    }
}

/**
 * Strips display math wrappers \[ ... \] for clean clipboard LaTeX copy.
 */
function cleanRawLatex(eqStr) {
    return (eqStr || "").replace(/^\\\[\s*/, "").replace(/\s*\\\]$/, "").trim();
}

function copyLatexToClipboard(text, btn) {
    const raw = cleanRawLatex(text);
    const markCopied = () => {
        if (!btn) return;
        const orig = btn.textContent;
        btn.textContent = "Copied ✓";
        btn.classList.add("copied");
        setTimeout(() => {
            btn.textContent = orig;
            btn.classList.remove("copied");
        }, 1400);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(raw).then(markCopied).catch(() => {});
    }
}

/**
 * Renders the sidebar list of theories.
 */
function populateTheoryList() {
    const listContainer = document.getElementById("theory-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";

    THEORIES.forEach((theory, index) => {
        const div = document.createElement("div");
        div.className = `theory-item ${index === activeTheoryIndex ? "active" : ""}`;
        div.setAttribute("style", `--theme-color: ${theory.accentColor};`);
        div.innerHTML = `
            <div class="theory-item-top">
                <h3>${theory.title}</h3>
                <span class="theory-forms-badge">${theory.representations.length} forms</span>
            </div>
            <p>${theory.category}</p>
        `;
        div.addEventListener("click", () => {
            selectTheory(index);
        });
        listContainer.appendChild(div);
    });
}

/**
 * Handles switching the active theory.
 */
function selectTheory(index, updateURL = true) {
    activeTheoryIndex = index;
    activeRepIndex = 0;

    const theory = THEORIES[activeTheoryIndex];
    compareRepIndex = theory.representations.length > 1 ? 1 : 0;

    // Update active class in list items
    document.querySelectorAll(".theory-item").forEach((item, idx) => {
        item.classList.toggle("active", idx === index);
    });

    // Update theme properties on viewer card
    const viewerCard = document.getElementById("viewer-card");
    if (viewerCard) {
        viewerCard.setAttribute("style", `
            --theme-color: ${theory.accentColor};
            --theme-bg-color: ${theory.accentBg};
            --theme-border-color: ${theory.accentBorder};
        `);
    }

    // Update theory details
    document.getElementById("active-category").textContent = theory.category;
    document.getElementById("active-theory-title").textContent = theory.title;
    document.getElementById("active-theory-description").textContent = theory.description;

    if (updateURL) {
        syncURLParams();
    }

    populateRepTabs();
    populateCompareDropdown();
    renderActiveRepresentation();
}

/**
 * Syncs the active theory and representation into the browser URL.
 */
function syncURLParams() {
    try {
        const theory = THEORIES[activeTheoryIndex];
        const rep = theory ? theory.representations[activeRepIndex] : null;
        const currentUrl = new URL(window.location.href);
        if (theory) currentUrl.searchParams.set("theory", theory.id);
        if (rep) currentUrl.searchParams.set("rep", rep.id);
        window.history.replaceState({}, "", currentUrl.toString());
    } catch (_) {}
}

/**
 * Renders the tab bar for representations.
 */
function populateRepTabs() {
    const tabsContainer = document.getElementById("rep-tabs-container");
    if (!tabsContainer) return;
    tabsContainer.innerHTML = "";

    const theory = THEORIES[activeTheoryIndex];
    theory.representations.forEach((rep, index) => {
        const button = document.createElement("button");
        button.className = `rep-tab ${index === activeRepIndex ? "active" : ""}`;
        button.textContent = rep.name;
        button.addEventListener("click", () => {
            selectRepresentation(index);
        });
        tabsContainer.appendChild(button);
    });
}

/**
 * Populates the comparison representation dropdown.
 */
function populateCompareDropdown() {
    const select = document.getElementById("compare-rep-select");
    if (!select) return;
    const theory = THEORIES[activeTheoryIndex];
    select.innerHTML = "";
    theory.representations.forEach((rep, idx) => {
        const opt = document.createElement("option");
        opt.value = String(idx);
        opt.textContent = rep.name;
        if (idx === compareRepIndex) opt.selected = true;
        select.appendChild(opt);
    });
}

/**
 * Handles switching the representation tab.
 */
function selectRepresentation(index, updateURL = true) {
    activeRepIndex = index;

    // Ensure compareRepIndex differs from activeRepIndex when comparing
    const theory = THEORIES[activeTheoryIndex];
    if (compareRepIndex === activeRepIndex && theory.representations.length > 1) {
        compareRepIndex = activeRepIndex === 0 ? 1 : 0;
        populateCompareDropdown();
    }

    document.querySelectorAll(".rep-tab").forEach((tab, idx) => {
        tab.classList.toggle("active", idx === index);
    });

    if (updateURL) {
        syncURLParams();
    }

    renderActiveRepresentation();
}

function renderTags(containerId, tags) {
    const el = document.getElementById(containerId);
    if (!el) return;
    el.innerHTML = (tags || [])
        .map(t => `<span class="rep-sig-tag">${t}</span>`)
        .join("");
}

/**
 * Renders active equation mathematical forms, translation key, comparison pane, and glossary.
 */
function renderActiveRepresentation() {
    const theory = THEORIES[activeTheoryIndex];
    const rep = theory.representations[activeRepIndex];

    // Primary representation
    document.getElementById("active-rep-name").textContent = rep.name;
    renderTags("active-rep-tags", rep.tags);

    const mathRender = document.getElementById("active-math-render");
    mathRender.innerHTML = rep.equation;

    // Translation Key Strip
    const chipsContainer = document.getElementById("translation-chips");
    const keyBar = document.getElementById("translation-key-bar");
    if (chipsContainer && keyBar) {
        if (rep.mappings && rep.mappings.length > 0) {
            chipsContainer.innerHTML = rep.mappings
                .map(m => `<span class="translation-chip">\\(${m}\\)</span>`)
                .join("");
            keyBar.style.display = "flex";
        } else {
            keyBar.style.display = "none";
        }
    }

    // Comparison pane
    const stageGrid = document.getElementById("math-stage-grid");
    const compareCard = document.getElementById("math-card-compare");
    const bridgeBadge = document.getElementById("compare-bridge-badge");
    const compareRender = document.getElementById("compare-math-render");
    const typesetTargets = [mathRender, chipsContainer];

    if (compareMode && theory.representations.length > 1) {
        const compRep = theory.representations[compareRepIndex] || theory.representations[0];
        document.getElementById("compare-rep-name").textContent = compRep.name;
        renderTags("compare-rep-tags", compRep.tags);
        compareRender.innerHTML = compRep.equation;
        stageGrid.classList.add("is-comparing");
        compareCard.style.display = "flex";
        bridgeBadge.style.display = "flex";
        typesetTargets.push(compareRender);
    } else {
        stageGrid.classList.remove("is-comparing");
        compareCard.style.display = "none";
        bridgeBadge.style.display = "none";
    }

    // Description texts
    const insightEl = document.getElementById("active-rep-insight");
    const utilityEl = document.getElementById("active-rep-utility");
    insightEl.innerHTML = rep.insight;
    utilityEl.innerHTML = rep.utility;
    typesetTargets.push(insightEl, utilityEl);

    // Render glossary table
    const tbody = populateGlossaryTable(rep.glossary);
    if (tbody) typesetTargets.push(tbody);

    // Run MathJax typesetting on all updated containers in one clean pass
    typesetMath(typesetTargets);
}

/**
 * Renders the variable glossary table.
 */
function populateGlossaryTable(glossary) {
    const tbody = document.getElementById("glossary-tbody");
    if (!tbody) return null;
    tbody.innerHTML = "";

    if (!glossary || glossary.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No variable glossary available for this representation.</td></tr>`;
        return null;
    }

    glossary.forEach(item => {
        const tr = document.createElement("tr");

        const tdSymbol = document.createElement("td");
        tdSymbol.className = "var-sym";
        tdSymbol.innerHTML = `\\(${item.symbol}\\)`;

        const tdName = document.createElement("td");
        if (item.link) {
            tdName.innerHTML = `<a href="${item.link}" class="var-link"><strong>${item.name}</strong></a>`;
        } else {
            tdName.innerHTML = `<strong>${item.name}</strong>`;
        }

        const tdDim = document.createElement("td");
        tdDim.className = "var-dim";
        tdDim.innerHTML = `\\(${item.dimension}\\)`;

        tr.appendChild(tdSymbol);
        tr.appendChild(tdName);
        tr.appendChild(tdDim);

        tbody.appendChild(tr);
    });

    return tbody;
}

/**
 * Initial setup when DOM is ready.
 */
document.addEventListener("DOMContentLoaded", () => {
    populateTheoryList();

    // Compare Side-by-Side Toggle
    const compareBtn = document.getElementById("btn-compare-toggle");
    const compareWrap = document.getElementById("compare-select-wrap");
    const compareSelect = document.getElementById("compare-rep-select");

    if (compareBtn) {
        compareBtn.addEventListener("click", () => {
            compareMode = !compareMode;
            compareBtn.classList.toggle("is-comparing", compareMode);
            compareBtn.setAttribute("aria-pressed", String(compareMode));
            if (compareWrap) compareWrap.style.display = compareMode ? "inline-flex" : "none";
            renderActiveRepresentation();
        });
    }

    if (compareSelect) {
        compareSelect.addEventListener("change", (e) => {
            compareRepIndex = parseInt(e.target.value, 10) || 0;
            renderActiveRepresentation();
        });
    }

    // Copy LaTeX buttons
    const copyPrimaryBtn = document.getElementById("btn-copy-latex");
    if (copyPrimaryBtn) {
        copyPrimaryBtn.addEventListener("click", () => {
            const rep = THEORIES[activeTheoryIndex].representations[activeRepIndex];
            copyLatexToClipboard(rep.equation, copyPrimaryBtn);
        });
    }

    const copyCompareBtn = document.getElementById("btn-copy-compare-latex");
    if (copyCompareBtn) {
        copyCompareBtn.addEventListener("click", () => {
            const rep = THEORIES[activeTheoryIndex].representations[compareRepIndex];
            copyLatexToClipboard(rep.equation, copyCompareBtn);
        });
    }

    // URL state hydration (deep-linking)
    const urlParams = new URLSearchParams(window.location.search);
    const reqTheory = urlParams.get("theory") || urlParams.get("id");
    const reqRep = urlParams.get("rep") || urlParams.get("representation");

    let theoryIdx = 0;
    if (reqTheory) {
        const reqLower = reqTheory.toLowerCase().replace(/[- ]/g, "_");
        const foundIdx = THEORIES.findIndex(t =>
            t.id.toLowerCase() === reqLower ||
            t.id.toLowerCase().startsWith(reqLower) ||
            t.title.toLowerCase().includes(reqTheory.toLowerCase())
        );
        if (foundIdx !== -1) {
            theoryIdx = foundIdx;
        }
    }

    selectTheory(theoryIdx, false);

    if (reqRep) {
        const theory = THEORIES[theoryIdx];
        const reqRepLower = reqRep.toLowerCase().replace(/[- ]/g, "_");
        const foundRepIdx = theory.representations.findIndex(r =>
            r.id.toLowerCase() === reqRepLower ||
            r.id.toLowerCase().startsWith(reqRepLower) ||
            r.name.toLowerCase().includes(reqRep.toLowerCase())
        );
        if (foundRepIdx !== -1) {
            selectRepresentation(foundRepIdx, false);
        }
    }
});
