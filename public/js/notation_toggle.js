/**
 * Cosmic Obsidian - Multi-Representation Notation Toggle
 * Provides interactive representation switcher for key physical identities.
 */

const THEORIES = [
    {
        id: "maxwell",
        title: "Maxwell's Equations",
        category: "Electromagnetism",
        description: "The classical equations of electrodynamics describing how electric and magnetic fields are generated and altered by each other and by charges and currents.",
        accentColor: "#00d2ff",
        accentBg: "rgba(0, 210, 255, 0.08)",
        accentBorder: "rgba(0, 210, 255, 0.35)",
        representations: [
            {
                id: "gibbs_differential",
                name: "Gibbs Vector (Differential)",
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
                equation: "\\[\\begin{aligned} \\partial_\\mu F^{\\mu\\nu} &= \\mu_0 J^\\nu \\\\ \\partial_{[\\mu} F_{\\nu\\rho]} &= 0 \\end{aligned}\\]",
                insight: "Unifies the 3D electric and magnetic fields into a single, antisymmetric rank-2 field strength tensor \\(F^{\\mu\\nu}\\) on 4D Minkowski spacetime. The sources are combined into a single 4-current vector \\(J^\\nu\\). This structure makes special relativity manifest.",
                utility: "Fundamental in relativistic mechanics, accelerator physics, and particle physics. Expresses electrodynamics in a form that remains invariant under arbitrary coordinate changes (general covariance).",
                glossary: [
                    { symbol: "F^{\\mu\\nu}", name: "Electromagnetic Field Tensor", dimension: "\\mathsf{M}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-1}", link: "/physics/symbols#electromagnetic-tensor" },
                    { symbol: "J^\\nu", name: "Four-Current Density Vector", dimension: "\\mathsf{L}^{-2}\\cdot\\mathsf{I}", link: "/physics/symbols#four-current" },
                    { symbol: "\\partial_\\mu", name: "Four-Gradient Operator", dimension: "\\mathsf{L}^{-1}", link: "/physics/symbols#four-gradient" },
                    { symbol: "\\mu_0", name: "Vacuum Permeability Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-2}\\cdot\\mathsf{I}^{-2}", link: "/physics/constants#mu-0" }
                ]
            },
            {
                id: "differential_forms",
                name: "Differential Forms",
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
        id: "einstein",
        title: "Einstein Field Equations",
        category: "General Relativity",
        description: "The central equations of Einstein's general theory of relativity, describing how the geometry of spacetime responds to the presence of mass, energy, and momentum.",
        accentColor: "#8b5cf6",
        accentBg: "rgba(139, 92, 246, 0.08)",
        accentBorder: "rgba(139, 92, 246, 0.35)",
        representations: [
            {
                id: "standard_tensor",
                name: "Standard Tensor",
                equation: "\\[ G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu} \\]",
                insight: "The standard tensor formulation relating local spacetime curvature (Einstein tensor \\(G_{\\mu\\nu}\\) and metric \\(g_{\\mu\\nu}\\)) to local energy-momentum density (tensor \\(T_{\\mu\\nu}\\)). Geometrically states: 'Spacetime tells matter how to move; matter tells spacetime how to curve.'",
                utility: "Standard interface used to compute cosmological models, stellar collapse, gravitational waves, and black hole solutions (e.g. Schwarzschild and Kerr metrics).",
                glossary: [
                    { symbol: "G_{\\mu\\nu}", name: "Einstein Curvature Tensor", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#einstein-tensor" },
                    { symbol: "g_{\\mu\\nu}", name: "Metric Tensor", dimension: "dimensionless", link: "/physics/symbols#metric-tensor" },
                    { symbol: "T_{\\mu\\nu}", name: "Stress-Energy Tensor", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{-1}\\cdot\\mathsf{T}^{-2}", link: "/physics/symbols#stress-energy-tensor" },
                    { symbol: "G", name: "Newtonian Gravitational Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{3}\\cdot\\mathsf{T}^{-2}", link: "/physics/constants#G" },
                    { symbol: "c", name: "Speed of Light", dimension: "\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#c" },
                    { symbol: "\\Lambda", name: "Cosmological Constant", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#cosmological-constant" }
                ]
            },
            {
                id: "einstein_hilbert_action",
                name: "Einstein-Hilbert Action",
                equation: "\\[ S = \\int_{\\mathcal{M}} \\left( \\frac{R - 2\\Lambda}{16\\pi G/c^4} \\right) \\sqrt{-g} \\, d^4x + S_{\\text{matter}} \\]",
                insight: "Formulates general relativity through the Principle of Least Action. Taking the variational derivative of \\(S\\) with respect to the inverse metric \\(g^{\\mu\\nu}\\) yields the complete Einstein Field Equations.",
                utility: "Crucial for studying quantum gravity, string theory, and cosmological field modifications. Provides a unified starting point to couple gravity to other fundamental forces.",
                glossary: [
                    { symbol: "S", name: "Action Integral", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#action" },
                    { symbol: "R", name: "Ricci Scalar Curvature", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#ricci-scalar" },
                    { symbol: "g", name: "Determinant of Metric Tensor", dimension: "dimensionless", link: "/physics/symbols#metric-determinant" },
                    { symbol: "G", name: "Newtonian Gravitational Constant", dimension: "\\mathsf{M}^{-1}\\cdot\\mathsf{L}^{3}\\cdot\\mathsf{T}^{-2}", link: "/physics/constants#G" },
                    { symbol: "c", name: "Speed of Light", dimension: "\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#c" },
                    { symbol: "\\Lambda", name: "Cosmological Constant", dimension: "\\mathsf{L}^{-2}", link: "/physics/symbols#cosmological-constant" }
                ]
            },
            {
                id: "cartan_tetrad",
                name: "Cartan Tetrad Form (Frame Fields)",
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
        accentBg: "rgba(255, 78, 136, 0.08)",
        accentBorder: "rgba(255, 78, 136, 0.35)",
        representations: [
            {
                id: "position_space",
                name: "Position Space",
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
                equation: "\\[ i\\hbar \\frac{\\partial}{\\partial t} \\phi(\\mathbf{p}, t) = \\frac{\\mathbf{p}^2}{2m} \\phi(\\mathbf{p}, t) + \\int V(\\mathbf{p} - \\mathbf{p}') \\phi(\\mathbf{p}', t) \\, d^3p' \\]",
                insight: "Expresses quantum states in terms of momentum coordinates \\(\\mathbf{p}\\). The kinetic energy becomes a simple multiplication term, while potential energy turns into a convolution integral. Represents the Fourier transform of the position space equation.",
                utility: "Best suited for periodic systems, scattering experiments (e.g. Born approximations), and free-electron field behaviors in solid state physics.",
                glossary: [
                    { symbol: "\\phi(\\mathbf{p}, t)", name: "Momentum-space Wave Function", dimension: "\\mathsf{M}^{-3/2}\\cdot\\mathsf{L}^{-3/2}\\cdot\\mathsf{T}^{3/2}", link: "/physics/symbols#momentum-wave-function" },
                    { symbol: "\\hbar", name: "Reduced Planck Constant", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/constants#h-bar" },
                    { symbol: "m", name: "Particle Mass", dimension: "\\mathsf{M}", link: "/physics/symbols#mass" },
                    { symbol: "\\mathbf{p}", name: "Momentum Coordinates Vector", dimension: "\\mathsf{M}\\cdot\\mathsf{L}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#momentum" },
                    { symbol: "V(\\mathbf{p})", name: "Fourier Transformed Potential", dimension: "dimensionless", link: "/physics/symbols#fourier-potential" }
                ]
            },
            {
                id: "braket_formalism",
                name: "Bra-Ket Formalism (Abstract)",
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
                equation: "\\[ \\langle x_f | U(t_f, t_i) | x_i \\rangle = \\int \\mathcal{D}[x(t)] e^{\\frac{i}{\hbar} S[x(t)]} \\]",
                insight: "Formulates quantum transitions as a sum over histories. The probability amplitude is calculated by integrating over all possible spatial paths connecting the initial and final states, weighted by the exponent of the classical action action phase \\(e^{iS/\\hbar}\\).",
                utility: "Central to quantum field theory, particle physics, and statistical mechanics. Elegant for demonstrating the classical limit (when \\(\\hbar \\to 0\\), the classical path of least action dominates).",
                glossary: [
                    { symbol: "\\mathcal{D}[x(t)]", name: "Functional Path Integration Measure", dimension: "dimensionless", link: "/physics/symbols#path-measure" },
                    { symbol: "S[x(t)]", name: "Classical Action Functional", dimension: "\\mathsf{M}\\cdot\\mathsf{L}^{2}\\cdot\\mathsf{T}^{-1}", link: "/physics/symbols#action" },
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
        accentBg: "rgba(99, 102, 241, 0.08)",
        accentBorder: "rgba(99, 102, 241, 0.35)",
        representations: [
            {
                id: "covariant_form",
                name: "Covariant Spacetime Form",
                equation: "\\[ (i\\gamma^\\mu \\partial_\\mu - m)\\psi = 0 \\]",
                insight: "Standard covariant relativistic formulation. Relies on 4x4 complex matrices (gamma matrices \\(\\gamma^\\mu\\)) to yield an equation that is linear in both spatial and temporal derivatives, satisfying both special relativity and quantum mechanics.",
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

/**
 * Triggers MathJax typesetting asynchronously on specific element.
 */
function typesetMath(elements = null) {
    if (window.MathJax) {
        const run = () => {
            if (window.MathJax.typesetPromise) {
                const target = elements ? (Array.isArray(elements) ? elements : [elements]) : null;
                window.MathJax.typesetPromise(target)
                    .catch(err => console.warn("MathJax typeset error:", err));
            }
        };
        setTimeout(() => {
            if (window.MathJax.typesetPromise) {
                run();
            } else if (window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise.then(run);
            } else {
                setTimeout(run, 100);
            }
        }, 100);
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
            <h4>${theory.title}</h4>
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
function selectTheory(index) {
    activeTheoryIndex = index;
    activeRepIndex = 0;

    // Update active class in list items
    const items = document.querySelectorAll(".theory-item");
    items.forEach((item, idx) => {
        if (idx === index) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    const theory = THEORIES[activeTheoryIndex];
    
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

    // Render tabs for representations
    populateRepTabs();

    // Render content
    renderActiveRepresentation();
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
 * Handles switching the representation tab.
 */
function selectRepresentation(index) {
    activeRepIndex = index;

    // Update active class in tab buttons
    const tabs = document.querySelectorAll(".rep-tab");
    tabs.forEach((tab, idx) => {
        if (idx === index) {
            tab.classList.add("active");
        } else {
            tab.classList.remove("active");
        }
    });

    renderActiveRepresentation();
}

/**
 * Renders active equation mathematical forms, descriptions, and glossary variables.
 */
function renderActiveRepresentation() {
    const theory = THEORIES[activeTheoryIndex];
    const rep = theory.representations[activeRepIndex];

    // Update title
    document.getElementById("active-rep-name").textContent = rep.name;

    // Update math equation content
    const mathRender = document.getElementById("active-math-render");
    mathRender.innerHTML = rep.equation;

    // Update description texts
    document.getElementById("active-rep-insight").innerHTML = rep.insight;
    document.getElementById("active-rep-utility").innerHTML = rep.utility;

    // Render glossary table
    populateGlossaryTable(rep.glossary);

    // Run MathJax typesetting on changed elements
    typesetMath(mathRender);
}

/**
 * Renders the variable glossary table.
 */
function populateGlossaryTable(glossary) {
    const tbody = document.getElementById("glossary-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    if (!glossary || glossary.length === 0) {
        tbody.innerHTML = `<tr><td colspan="3" style="text-align: center; color: var(--text-muted);">No variable glossary available for this representation.</td></tr>`;
        return;
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

    // Typeset math in table columns
    typesetMath(tbody);
}

/**
 * Initial setup when DOM is ready.
 */
document.addEventListener("DOMContentLoaded", () => {
    // Populate theory list
    populateTheoryList();

    // Select first theory by default
    selectTheory(0);
});
