/**
 * 🔬 PHYSICS LAB: Interactive Equation Explainer
 * 
 * Manages the LaTeX equation compiler workbench, handles real-time lookups to the database,
 * performs fallback symbol tokenization, and connects analytical tools together.
 */

const EquationExplainer = {
    // State variables
    currentId: null,
    currentLatex: '',
    currentFormula: null,
    currentSubtopics: [],
    
    // User customizations storage (loaded from localStorage)
    userCustomizations: {},
    
    // DOM Elements
    latexInput: null,
    clearBtn: null,
    mathRenderTarget: null,
    compilerStatus: null,
    formulaTitle: null,
    formulaBadge: null,
    officialBreakdown: null,
    symbolsBreakdown: null,
    symbolsList: null,
    topologicalBridges: null,
    bridgesContainer: null,
    explainerPlaceholder: null,
    solverRedirectContainer: null,
    solverRedirectLink: null,
    
    // Debounce timer
    debounceTimer: null,
    
    // Comprehensive physics dictionary mapping standard variables, constants, and operators
    physicsDictionary: {
        // Operators
        '\\partial': { name: 'Partial Derivative', type: 'operator', unit: 'operator', desc: 'Represents differentiation with respect to a single variable in multi-variable calculus.' },
        '\\nabla': { name: 'Del / Gradient Operator', type: 'operator', unit: 'operator', desc: 'The vector differential operator representing gradient, divergence, or curl.' },
        '\\Delta': { name: 'Laplacian / Change Operator', type: 'operator', unit: 'operator', desc: 'Denotes either a difference/change in a variable, or the second-order spatial derivative operator.' },
        '\\int': { name: 'Integral Operator', type: 'operator', unit: 'operator', desc: 'Represents continuous summation or the area under a curve.' },
        '\\oint': { name: 'Closed Loop Integral', type: 'operator', unit: 'operator', desc: 'Represents line or surface integration over a closed boundary.' },
        '\\sum': { name: 'Summation Operator', type: 'operator', unit: 'operator', desc: 'Represents discrete addition of a sequence of terms.' },
        '+': { name: 'Addition Operator', type: 'operator', unit: 'operator', desc: 'Adds mathematical values together.' },
        '-': { name: 'Subtraction Operator', type: 'operator', unit: 'operator', desc: 'Subtracts one mathematical value from another.' },
        '=': { name: 'Equality Relation', type: 'operator', unit: 'operator', desc: 'Asserts that two expressions have the exact same value.' },
        '/': { name: 'Division Operator', type: 'operator', unit: 'operator', desc: 'Denotes division or ratio between two values.' },

        // Lowercase Roman Letters
        'a': { name: 'Acceleration', type: 'variable', unit: 'm/s²', desc: 'The rate of change of velocity of an object with respect to time.' },
        'b': { name: 'Impact Parameter / Constant', type: 'variable', unit: 'm', desc: 'Perpendicular distance between the path of a projectile and the center of a potential field.' },
        'c': { name: 'Speed of Light', type: 'constant', unit: 'm/s', desc: 'The maximum speed at which all conventional matter and information in the universe can travel.' },
        'd': { name: 'Total Differential / Distance', type: 'operator', unit: 'operator', desc: 'Represents an infinitesimal change in a variable, or physical distance.' },
        'e': { name: 'Elementary Charge / Euler\'s Number', type: 'constant', unit: 'C', desc: 'The electric charge carried by a single proton, or the mathematical base of natural logarithms.' },
        'f': { name: 'Frequency', type: 'variable', unit: 'Hz', desc: 'The number of occurrences of a repeating event per unit of time.' },
        'g': { name: 'Gravitational Acceleration', type: 'constant', unit: 'm/s²', desc: 'The local acceleration imparted to objects due to gravity (approx. 9.81 m/s² on Earth).' },
        'h': { name: 'Planck Constant', type: 'constant', unit: 'J·s', desc: 'The quantum of electromagnetic action relating photon energy to frequency.' },
        'i': { name: 'Imaginary Unit / Summation Index', type: 'constant', unit: 'dimensionless', desc: 'The mathematical constant defined by i² = -1, or a counting index in sums.' },
        'j': { name: 'Current Density / Index', type: 'variable', unit: 'A/m²', desc: 'The flow of electric current per unit cross-sectional area.' },
        'k': {
            name: 'Boltzmann Constant',
            type: 'constant',
            unit: 'J/K',
            desc: 'A physical constant relating the average relative kinetic energy of particles in a gas with the thermodynamic temperature.',
            alternatives: [
                { name: 'Spring Constant', type: 'variable', unit: 'N/m', desc: 'The force constant representing the stiffness of a spring (Hooke\'s Law).' },
                { name: 'Wave Vector', type: 'variable', unit: 'rad/m', desc: 'A vector indicating the direction and rate of space-phase variation of a wave.' },
                { name: 'Thermal Conductivity', type: 'variable', unit: 'W/(m·K)', desc: 'The measure of a material\'s ability to conduct heat.' }
            ]
        },
        'l': { name: 'Length / Angular Quantum Number', type: 'variable', unit: 'm', desc: 'The physical size of an object, or orbital angular momentum quantum number.' },
        'm': { name: 'Mass', type: 'variable', unit: 'kg', desc: 'A fundamental measure of the amount of matter in a body and its resistance to acceleration.' },
        'n': { name: 'Refractive Index / Particle Density', type: 'variable', unit: 'dimensionless or m⁻³', desc: 'The ratio of speed of light in vacuum to that in a medium, or particles per unit volume.' },
        'o': { name: 'Origin / Offset', type: 'variable', unit: 'dimensionless', desc: 'The starting point of a coordinate system, or baseline shift.' },
        'p': { name: 'Momentum / Pressure', type: 'variable', unit: 'kg·m/s or Pa', desc: 'The product of mass and velocity of a body, or force applied per unit area.' },
        'q': { name: 'Electric Charge', type: 'variable', unit: 'C', desc: 'A physical property of matter that causes it to experience a force when placed in an electromagnetic field.' },
        'r': { name: 'Radius / Position Vector', type: 'variable', unit: 'm', desc: 'Radial distance from a center, or the spatial position vector of a particle.' },
        's': { name: 'Seconds / Proper Time Interval', type: 'variable', unit: 's', desc: 'The SI unit of time, or the invariant interval traversed by a clock.' },
        't': { name: 'Time', type: 'variable', unit: 's', desc: 'The progress of existence and events in the past, present, and future.' },
        'u': { name: 'Velocity Component / Specific Internal Energy', type: 'variable', unit: 'm/s or J/kg', desc: 'Speed along a particular coordinate direction, or internal energy per unit mass.' },
        'v': { name: 'Velocity', type: 'variable', unit: 'm/s', desc: 'The rate of change of position of an object with respect to time.' },
        'w': { name: 'Width / Angular Velocity Component', type: 'variable', unit: 'm or rad/s', desc: 'Horizontal size, or rate of rotation along a particular axis.' },
        'x': { name: 'Cartesian Coordinate X', type: 'variable', unit: 'm', desc: 'The spatial displacement along the horizontal coordinate dimension.' },
        'y': { name: 'Cartesian Coordinate Y', type: 'variable', unit: 'm', desc: 'The spatial displacement along the vertical coordinate dimension.' },
        'z': { name: 'Cartesian Coordinate Z', type: 'variable', unit: 'm', desc: 'The spatial displacement along the depth coordinate dimension.' },

        // Uppercase Roman Letters
        'A': { name: 'Area / Vector Potential', type: 'variable', unit: 'm² or V·s/m', desc: 'The measure of a 2D surface, or the electrodynamic magnetic vector potential.' },
        'B': { name: 'Magnetic Field Strength', type: 'variable', unit: 'T', desc: 'The magnetic flux density representing electromagnetic field induction.' },
        'C': { name: 'Capacitance / Heat Capacity', type: 'variable', unit: 'F or J/K', desc: 'The ability of a body to store electrical charge, or thermal energy needed to change temperature.' },
        'D': { name: 'Electric Displacement Field', type: 'variable', unit: 'C/m²', desc: 'The displacement flux density representing electric charge polarization in media.' },
        'E': { name: 'Total Energy / Electric Field', type: 'variable', unit: 'J or V/m', desc: 'The quantitative property representing potential/kinetic capacity, or electrical force field.' },
        'F': { name: 'Force / Helmholtz Free Energy', type: 'variable', unit: 'N or J', desc: 'An interaction that changes the motion of an object, or thermodynamic work capacity.' },
        'G': { name: 'Gravitational Constant / Gibbs Free Energy', type: 'constant', unit: 'm³·kg⁻¹·s⁻²', desc: 'Empirical constant of gravitational interaction, or chemical potential energy.' },
        'H': { name: 'Hamiltonian / Enthalpy', type: 'variable', unit: 'J', desc: 'The operator representing the total energy of a system, or thermodynamic heat content.' },
        'I': { name: 'Electric Current / Moment of Inertia', type: 'variable', unit: 'A or kg·m²', desc: 'The rate of flow of electric charge, or resistance to rotational acceleration.' },
        'J': { name: 'Angular Momentum / Current Density', type: 'variable', unit: 'kg·m²/s or A/m²', desc: 'Rotational momentum vector, or flow of electric charge per unit area.' },
        'K': { name: 'Kinetic Energy / Bulk Modulus', type: 'variable', unit: 'J or Pa', desc: 'Energy possessed by an object due to its motion, or resistance to uniform compression.' },
        'L': { name: 'Angular Momentum / Lagrangian', type: 'variable', unit: 'kg·m²/s or J', desc: 'Orbital momentum, or kinetic energy minus potential energy in mechanics.' },
        'M': { name: 'Total Mass / Magnetization', type: 'variable', unit: 'kg or A/m', desc: 'The total inertial mass of a system, or net magnetic dipole moment density.' },
        'N': { name: 'Number of Particles / Normal Force', type: 'variable', unit: 'dimensionless or N', desc: 'The total count of atoms/molecules, or perpendicular contact force.' },
        'O': { name: 'Operator / Big O Notation', type: 'variable', unit: 'dimensionless', desc: 'A mathematical action performed on a state vector, or asymptotic growth boundary.' },
        'P': {
            name: 'Pressure',
            type: 'variable',
            unit: 'Pa',
            desc: 'The perpendicular force exerted per unit area on the boundary of a system.',
            alternatives: [
                { name: 'Power', type: 'variable', unit: 'W', desc: 'The rate at which work is done or energy is transferred.' },
                { name: 'Probability', type: 'variable', unit: 'dimensionless', desc: 'The likelihood of a specific event occurring, ranging from 0 to 1.' },
                { name: 'Momentum', type: 'variable', unit: 'kg·m/s', desc: 'The product of the mass and velocity of an object (uppercase variant).' }
            ]
        },
        'Q': { name: 'Heat / Total Charge', type: 'variable', unit: 'J or C', desc: 'Thermal energy transferred due to temperature difference, or net electrical charge.' },
        'R': { name: 'Ideal Gas Constant / Resistance / Radius', type: 'constant', unit: 'J/(mol·K) or Ω or m', desc: 'Universal gas constant, electrical resistance, or spatial radius.' },
        'S': {
            name: 'Entropy',
            type: 'variable',
            unit: 'J/K',
            desc: 'A thermodynamic quantity representing the degree of disorder or randomness in a system.',
            alternatives: [
                { name: 'Action', type: 'variable', unit: 'J·s', desc: 'The path integral of the Lagrangian over time representing the trajectory of a system.' },
                { name: 'Poynting Vector', type: 'variable', unit: 'W/m²', desc: 'The directional energy flux density of an electromagnetic field.' }
            ]
        },
        'T': {
            name: 'Temperature',
            type: 'variable',
            unit: 'K',
            desc: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.',
            alternatives: [
                { name: 'Time Period', type: 'variable', unit: 's', desc: 'The duration of one complete cycle of a repeating wave or oscillation.' },
                { name: 'Tension', type: 'variable', unit: 'N', desc: 'Axial pulling force transmitted through a string, rope, or chain.' },
                { name: 'SU(3) Gauge Generator', type: 'variable', unit: 'dimensionless', desc: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.' }
            ]
        },
        'U': { name: 'Internal Energy / Potential Energy', type: 'variable', unit: 'J', desc: 'Energy stored within a thermodynamic system, or position-dependent energy.' },
        'V': { name: 'Volume / Electric Potential', type: 'variable', unit: 'm³ or V', desc: 'The amount of three-dimensional space enclosed, or electrostatic voltage.' },
        'W': { name: 'Work Done / Watt', type: 'variable', unit: 'J or W', desc: 'Energy transferred by a force acting over a distance, or SI unit of power.' },
        'X': { name: 'Reactance / General Coordinate', type: 'variable', unit: 'Ω or m', desc: 'Opposition of a circuit element to alternating current, or generic coordinate.' },
        'Y': {
            name: 'Young\'s Modulus',
            type: 'variable',
            unit: 'Pa',
            desc: 'The measure of tensile elasticity or stiffness of a solid material.',
            alternatives: [
                { name: 'Weak Hypercharge', type: 'variable', unit: 'dimensionless', desc: 'The generator of the U(1) weak hypercharge gauge group.' },
                { name: 'Spherical Harmonic', type: 'variable', unit: 'dimensionless', desc: 'Angular wavefunction solutions to Laplace\'s equation in spherical coordinates.' }
            ]
        },
        'Z': { name: 'Atomic Number / Partition Function', type: 'variable', unit: 'dimensionless', desc: 'Protons in a nucleus, or the statistical sum over microstates.' },

        // Lowercase Greek Letters
        '\\alpha': { name: 'Fine-structure Constant / Angular Acceleration', type: 'constant', unit: 'dimensionless or rad/s²', desc: 'Strength of electromagnetic coupling, or rate of angular velocity change.' },
        '\\beta': { name: 'Phase Constant / Relativistic Beta', type: 'variable', unit: 'rad/m or dimensionless', desc: 'Phase shift per unit distance, or velocity as a fraction of speed of light (v/c).' },
        '\\gamma': { name: 'Lorentz Factor / Surface Tension / Gamma Ray', type: 'variable', unit: 'dimensionless or N/m', desc: 'Relativistic scale factor, force per unit length on liquid interface, or high-energy photon.' },
        '\\delta': { name: 'Dirac Delta / Small Increment', type: 'operator', unit: 'dimensionless', desc: 'Singular distribution representing an idealized point source, or a small variation.' },
        '\\epsilon': { name: 'Permittivity / Emissivity', type: 'variable', unit: 'F/m or dimensionless', desc: 'The measure of a medium\'s resistance to an electric field.' },
        '\\zeta': { name: 'Riemann Zeta Function / Damping Ratio', type: 'variable', unit: 'dimensionless', desc: 'A complex analytical function, or rate at which oscillations decay.' },
        '\\eta': { name: 'Efficiency / Viscosity / Minkowski Metric', type: 'variable', unit: 'dimensionless or Pa·s', desc: 'Ratio of useful work output to input energy, fluid shear resistance, or flat spacetime metric.' },
        '\\theta': { name: 'Angle Coordinate / Polar Angle', type: 'variable', unit: 'rad', desc: 'The angle displacement, or polar coordinate angle in spherical geometry.' },
        '\\iota': { name: 'Unit Vector Index', type: 'variable', unit: 'dimensionless', desc: 'A general vector component index.' },
        '\\kappa': { name: 'Curvature / Thermal Conductivity', type: 'variable', unit: 'm⁻¹ or W/(m·K)', desc: 'The rate of deviation from a straight line, or heat transmission coefficient.' },
        '\\lambda': { name: 'Wavelength / Linear Density', type: 'variable', unit: 'm or kg/m', desc: 'The distance between consecutive identical crests of a wave, or mass per unit length.' },
        '\\mu': { name: 'Reduced Mass / Permeability / Friction Coefficient', type: 'variable', unit: 'kg or H/m or dimensionless', desc: 'Effective inertial mass in two-body problems, magnetic field capability, or surface grip factor.' },
        '\\nu': { name: 'Frequency / Kinematic Viscosity', type: 'variable', unit: 'Hz or m²/s', desc: 'The wave frequency, or ratio of dynamic viscosity to density.' },
        '\\xi': { name: 'Dimensionless Variable / Partition Function', type: 'variable', unit: 'dimensionless', desc: 'General scaled displacement, or grand canonical partition function.' },
        '\\pi': { name: 'Pi constant', type: 'constant', unit: 'dimensionless', desc: 'The ratio of a circle\'s circumference to its diameter (approx. 3.14159).' },
        '\\rho': { name: 'Mass or Charge Density / Resistivity', type: 'variable', unit: 'kg/m³ or C/m³ or Ω·m', desc: 'Mass/charge per unit volume, or material opposition to current flow.' },
        '\\sigma': { name: 'Stefan-Boltzmann Constant / Surface Density / Spin Operator', type: 'constant', unit: 'W/(m²·K⁴) or C/m² or operator', desc: 'Blackbody radiation rate constant, charge per unit area, or quantum spin matrices.' },
        '\\tau': { name: 'Torque / Proper Time / Shear Stress', type: 'variable', unit: 'N·m or s or Pa', desc: 'Rotational force, relativistic invariant proper duration, or sliding drag force.' },
        '\\upsilon': { name: 'Upsilon Meson', type: 'variable', unit: 'dimensionless', desc: 'A bottom-antibottom quark state.' },
        '\\phi': { name: 'Azimuth Angle / Scalar Potential', type: 'variable', unit: 'rad or V', desc: 'The horizontal coordinate angle, or electrostatic scalar potential.' },
        '\\chi': { name: 'Magnetic or Electric Susceptibility', type: 'variable', unit: 'dimensionless', desc: 'The degree of polarization or magnetization in response to an applied field.' },
        '\\psi': { name: 'Quantum Wavefunction', type: 'variable', unit: 'dimensionless', desc: 'The complex probability amplitude vector representing a quantum state.' },
        '\\omega': { name: 'Angular Frequency / Velocity', type: 'variable', unit: 'rad/s', desc: 'Phase progression rate, or speed of rotation.' },

        // Uppercase Greek Letters
        '\\Gamma': { name: 'Gamma Function / Circulation / Connection', type: 'variable', unit: 'dimensionless or m²/s', desc: 'Factorial function generalization, fluid rotation line integral, or Christoffel symbol.' },
        '\\Delta': { name: 'Laplacian / Change Operator', type: 'operator', unit: 'operator', desc: 'Represents spatial second derivatives, or finite difference increment.' },
        '\\Theta': { name: 'Step Function / Temperature Scale', type: 'variable', unit: 'dimensionless or K', desc: 'Heaviside unit step function, or bulk temperature parameter.' },
        '\\Lambda': { name: 'Cosmological Constant / Baryon', type: 'constant', unit: 'm⁻² or GeV', desc: 'Energy density of space causing cosmic acceleration, or hyperon state.' },
        '\\Xi': { name: 'Cascade Baryon / Dimensionless coordinate', type: 'variable', unit: 'dimensionless', desc: 'Baryon state with strangeness -2, or generic axis coordinate.' },
        '\\Pi': { name: 'Product Operator / Pion Group', type: 'operator', unit: 'operator', desc: 'Discrete multiplication product, or pion triplet states.' },
        '\\Sigma': { name: 'Summation Operator / Baryon', type: 'operator', unit: 'operator', desc: 'Discrete summation operator, or strange baryon group.' },
        '\\Phi': { name: 'Magnetic Flux / Potential Function', type: 'variable', unit: 'Wb or V', desc: 'Total magnetic field lines through a surface, or general field potential.' },
        '\\Psi': { name: 'Quantum Wavefunction', type: 'variable', unit: 'dimensionless', desc: 'The complex probability amplitude vector representing a quantum state.' },
        '\\Omega': { name: 'Solid Angle / Resistance / Omega Baryon', type: 'variable', unit: 'sr or Ω', desc: '3D spatial projection angle, electrical impedance unit, or strangeness -3 hyperon.' }
    },

    init() {
        this.activeDomain = '';
        this.loadReferrerContext();
        this.loadUserCustomizations();
        this.cacheElements();
        this.bindEvents();
        this.loadInitialState();
    },

    loadReferrerContext() {
        const urlParams = new URLSearchParams(window.location.search);
        const contextParam = urlParams.get('context');
        if (contextParam) {
            const DOMAIN_MAP = {
                'thermodynamics-statistical-mechanics': 'thermodynamics',
                'classical-mechanics': 'mechanics',
                'standard-model': 'particle_physics',
                'astrophysics': 'astrophysics',
                'relativity': 'relativity',
                'quantum-physics': 'quantum'
            };
            this.activeDomain = DOMAIN_MAP[contextParam] || contextParam;
            return;
        }

        const referrer = document.referrer;
        if (referrer && referrer.includes('/physics/subtopic/')) {
            const parts = referrer.split('/');
            const subtopicSlug = parts[parts.length - 1].split('?')[0];
            
            fetch(`${BASE_URL}/physics/search-index`)
                .then(res => res.json())
                .then(index => {
                    const entry = index[subtopicSlug];
                    if (entry && entry.s) {
                        const shard = entry.s.replace('.json', '');
                        const DOMAIN_MAP = {
                            'thermodynamics-statistical-mechanics': 'thermodynamics',
                            'classical-mechanics': 'mechanics',
                            'standard-model': 'particle_physics',
                            'astrophysics': 'astrophysics',
                            'relativity': 'relativity',
                            'quantum-physics': 'quantum'
                        };
                        this.activeDomain = DOMAIN_MAP[shard] || '';
                        if (this.activeDomain) {
                            console.log(`Detected active domain: ${this.activeDomain} from referrer subtopic ${subtopicSlug}`);
                            if (this.latexInput && this.latexInput.value.trim() && !this.currentId) {
                                this.renderElementsBreakdown(this.latexInput.value.trim(), {});
                            }
                        }
                    }
                })
                .catch(err => console.warn('Could not determine referrer context:', err));
        }
    },

    getDynamicOverrides(latex) {
        const overrides = {};
        if (!latex) return overrides;

        // Layer 3: Subscript and Syntactic Grammar checks
        if (/T\^([a-d])|T\_([a-d])|T\^\{([a-d])\}|T\_\{([a-d])\}/.test(latex)) {
            overrides['T'] = { 
                name: 'SU(3) Gauge Generator', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.' 
            };
        }
        
        if (/T\_[0if]|T\_\{[0if]\}/.test(latex)) {
            overrides['T'] = { 
                name: 'Temperature', 
                type: 'variable', 
                unit: 'K', 
                description: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.' 
            };
        }

        if (/Y\_[lL]\^([mM])|Y\_\{[lL]\}\^\{([mM])\}/.test(latex)) {
            overrides['Y'] = { 
                name: 'Spherical Harmonic', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'Angular wavefunction solutions to Laplace\'s equation in spherical coordinates.' 
            };
        }
        
        if (/Y\s*\/\s*2|\frac\{\s*Y\s*\}\{\s*2\s*\}/.test(latex)) {
            overrides['Y'] = { 
                name: 'Weak Hypercharge', 
                type: 'variable', 
                unit: 'dimensionless', 
                description: 'The generator of the U(1) weak hypercharge gauge group.' 
            };
        }

        // Layer 2: Heuristic Token Co-occurrence (Semantic Clustering)
        const tokens = this.extractAllMathTokens(latex).map(t => t.symbol);
        
        const SEMANTIC_CLUSTERS = [
            {
                domain: 'thermodynamics',
                indicators: ['P', 'V', 'n', 'R', 'S', 'Q', 'U', '\\Delta', 'k_B'],
                overrides: {
                    'T': { name: 'Temperature', type: 'variable', unit: 'K', description: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.' },
                    'k': { name: 'Boltzmann Constant', type: 'constant', unit: 'J/K', description: 'A physical constant relating the average kinetic energy of particles in a gas with the thermodynamic temperature.' },
                    'P': { name: 'Pressure', type: 'variable', unit: 'Pa', description: 'Force applied perpendicular to the surface of an object per unit area.' },
                    'S': { name: 'Entropy', type: 'variable', unit: 'J/K', description: 'A thermodynamic quantity representing the degree of disorder or randomness in a system.' }
                }
            },
            {
                domain: 'harmonic_motion',
                indicators: ['f', '\\omega', '\\nu', '\\lambda', '\\sin', '\\cos', 'A'],
                overrides: {
                    'T': { name: 'Time Period', type: 'variable', unit: 's', description: 'The time taken for one complete cycle of a repeating wave or oscillation.' }
                }
            },
            {
                domain: 'dynamics',
                indicators: ['F', 'm', 'a', '\\theta', '\\mu_s', 'g', 'N'],
                overrides: {
                    'T': { name: 'Tension', type: 'variable', unit: 'N', description: 'The pulling force transmitted axially by means of a string, cable, or chain.' },
                    'k': { name: 'Spring Constant', type: 'variable', unit: 'N/m', description: 'The force constant representing the stiffness of a spring (Hooke\'s Law).' }
                }
            },
            {
                domain: 'gauge_theory',
                indicators: ['D_\\mu', 'g_s', 'W_\\mu', 'B_\\mu', '\\tau^a', 'G_\\mu^a', 'T^a', '\\tau', 'Y', 'g', 'g\''],
                overrides: {
                    'T': { name: 'SU(3) Gauge Generator', type: 'variable', unit: 'dimensionless', description: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.' },
                    'Y': { name: 'Weak Hypercharge', type: 'variable', unit: 'dimensionless', description: 'The generator of the U(1) weak hypercharge gauge group.' }
                }
            }
        ];

        let bestDomain = null;
        let maxOverlap = 0;

        SEMANTIC_CLUSTERS.forEach(cluster => {
            const overlap = cluster.indicators.filter(ind => tokens.includes(ind) || latex.includes(ind)).length;
            if (overlap >= 2 && overlap > maxOverlap) {
                maxOverlap = overlap;
                bestDomain = cluster;
            }
        });

        const activeCluster = SEMANTIC_CLUSTERS.find(c => c.domain === this.activeDomain);
        if (activeCluster) {
            Object.entries(activeCluster.overrides).forEach(([sym, val]) => {
                if (!overrides[sym]) {
                    overrides[sym] = val;
                }
            });
        }

        if (bestDomain) {
            Object.entries(bestDomain.overrides).forEach(([sym, val]) => {
                if (!overrides[sym]) {
                    overrides[sym] = val;
                }
            });
        }

        return overrides;
    },

    loadUserCustomizations() {
        try {
            // Load custom definitions from local storage
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('physics_explainer_custom_')) {
                    const symbol = key.replace('physics_explainer_custom_', '');
                    const value = JSON.parse(localStorage.getItem(key));
                    if (value) {
                        this.userCustomizations[symbol] = value;
                    }
                }
            }
        } catch (err) {
            console.warn('Could not load user customizations:', err);
        }
    },

    cacheElements() {
        this.latexInput = document.getElementById('latex-input');
        this.clearBtn = document.getElementById('clear-input-btn');
        this.mathRenderTarget = document.getElementById('math-render-target');
        this.compilerStatus = document.getElementById('compiler-status');
        
        this.formulaTitle = document.getElementById('formula-title');
        this.formulaBadge = document.getElementById('formula-badge');
        
        this.officialBreakdown = document.getElementById('official-breakdown');
        this.symbolsBreakdown = document.getElementById('symbols-breakdown');
        this.symbolsList = document.getElementById('symbols-list');
        this.topologicalBridges = document.getElementById('topological-bridges');
        this.bridgesContainer = document.getElementById('bridges-container');
        this.explainerPlaceholder = document.getElementById('explainer-placeholder');
        this.solverRedirectContainer = document.getElementById('solver-redirect-container');
        this.solverRedirectLink = document.getElementById('solver-redirect-link');
    },

    bindEvents() {
        // Debounced input compiling
        this.latexInput.addEventListener('input', () => {
            this.setCompilerStatus('Compiling...', '#fbbf24');
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.handleInputChange();
            }, 400);
        });

        // Clear button
        this.clearBtn.addEventListener('click', () => {
            this.latexInput.value = '';
            this.handleInputChange();
            this.latexInput.focus();
        });
    },

    loadInitialState() {
        if (window.INITIAL_FORMULA) {
            // Server pre-loaded from formula ID or initial lookup
            const formula = window.INITIAL_FORMULA;
            this.currentId = formula.id;
            this.currentLatex = formula.latex_source || this.getCleanLatexFromEq(formula.equation);
            this.latexInput.value = this.currentLatex;
            
            this.compileMathJax(this.currentLatex);
            this.renderFormula(formula, window.INITIAL_SUBTOPICS || []);
        } else if (window.INITIAL_LATEX) {
            // Just raw LaTeX passed
            this.latexInput.value = window.INITIAL_LATEX;
            this.handleInputChange();
        } else {
            // Set defaults or display placeholder
            this.resetExplanation();
        }
    },

    getCleanLatexFromEq(eqStr) {
        if (eqStr.includes('data-tex=')) {
            const match = eqStr.match(/data-tex="([^"]+)"/);
            if (match) return this.decodeHtmlEntities(match[1]);
        }
        // Remove math wrappers if string looks raw
        return eqStr.replace(/^\\\[/, '').replace(/\\\]$/, '').trim();
    },

    decodeHtmlEntities(str) {
        const txt = document.createElement("textarea");
        txt.innerHTML = str;
        return txt.value;
    },

    handleInputChange() {
        const latex = this.latexInput.value.trim();
        this.currentLatex = latex;
        this.currentId = null; // Typing custom formula clears registered ID

        if (latex === '') {
            this.mathRenderTarget.innerHTML = '<span style="font-family: \'Space Grotesk\', sans-serif; font-size: 1.1rem; opacity: 0.5;">Enter an equation to compile...</span>';
            this.setCompilerStatus('Ready', '#10b981');
            this.resetExplanation();
            return;
        }

        // 1. Compile MathJax preview
        this.compileMathJax(latex);

        // 2. Perform database lookup
        this.lookupFormulaByLatex(latex);
    },

    compileMathJax(latex) {
        // Enforce equation delimiters
        let mathMarkup = latex;
        if (!latex.startsWith('\\[') && !latex.startsWith('\\(') && !latex.startsWith('$$') && !latex.startsWith('$')) {
            mathMarkup = '\\[ ' + latex + ' \\]';
        }

        this.mathRenderTarget.innerHTML = mathMarkup;

        if (window.MathJax && window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise([this.mathRenderTarget])
                .then(() => {
                    this.setCompilerStatus('Ready', '#10b981');
                })
                .catch((err) => {
                    console.error('MathJax Compilation Error:', err);
                    this.setCompilerStatus('Syntax Error', '#ef4444');
                });
        } else {
            this.setCompilerStatus('Renderer Offline', '#f59e0b');
        }
    },

    setCompilerStatus(text, color) {
        this.compilerStatus.textContent = text;
        this.compilerStatus.style.color = color;
        const dot = this.compilerStatus.querySelector('span') || document.createElement('span');
        dot.style.background = color;
        // Make dot pulse if compiling
        if (text === 'Compiling...') {
            dot.style.animation = 'pulse 1s infinite alternate';
        } else {
            dot.style.animation = '';
        }
    },

    lookupFormulaByLatex(latex) {
        // Request database matching
        fetch(`${BASE_URL}/physics/api/explain?latex=` + encodeURIComponent(latex))
            .then(res => res.json())
            .then(data => {
                if (data.success && data.formula) {
                    // Match found! Load official sharded content
                    this.currentId = data.formula.id;
                    
                    // Fetch referencing subtopics
                    this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                        this.renderFormula(data.formula, subtopics);
                    });
                } else {
                    // Unregistered equation: parse variables and constants locally
                    this.renderCustomExplanation(latex);
                }
            })
            .catch(err => {
                console.warn('API lookup failed, falling back to local analysis:', err);
                this.renderCustomExplanation(latex);
            });
    },

    fetchSubtopicsForFormula(id) {
        return fetch(`${BASE_URL}/physics/search-index`)
            .then(res => res.json())
            .then(index => {
                const results = [];
                const cleanId = id.replace(/-/g, ' ');
                for (const [slug, item] of Object.entries(index)) {
                    const isSubtopic = item.s && !item.s.startsWith('topics/');
                    if (isSubtopic && item.k) {
                        const hasFormula = item.k.some(kw => kw === cleanId || kw === id.toLowerCase() || kw.includes(cleanId));
                        if (hasFormula) {
                            results.push({
                                slug: slug,
                                title: item.t
                            });
                        }
                    }
                }
                return results;
            })
            .catch(err => {
                console.warn('Could not load referencing subtopics:', err);
                return [];
            });
    },

    renderFormula(formula, subtopics) {
        this.currentFormula = formula;
        this.currentSubtopics = subtopics;

        // Display status
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'flex';
        this.symbolsBreakdown.style.display = 'block';
        
        // Populate Title and Badge
        this.formulaTitle.textContent = formula.title;
        
        // Status formatting
        const status = formula.status || 'platinum-draft';
        this.formulaBadge.className = 'badge-status ' + (status.includes('draft') ? 'badge-draft' : 'badge-platinum');
        this.formulaBadge.textContent = status.replace('-', ' ').toUpperCase();

        // Populate Tiers
        document.getElementById('local-interpretation').innerHTML = formula.interpretation || 'No interpretation provided.';
        document.getElementById('symmetry-origin').innerHTML = formula.symmetry_origin || 'Symmetry derivations pending.';
        document.getElementById('limits-boundary').innerHTML = formula.limits_and_boundary || 'Boundary analysis pending.';

        // Deconstruct EVERY element in the LaTeX string, merging database semantic definitions
        this.renderElementsBreakdown(this.currentLatex, formula.semantic_variables || {});

        // Populate Topological Bridges
        this.renderBridges(subtopics);

        // Setup Dimensional Solver Link
        this.setupSolverLink(this.currentLatex);
    },

    renderCustomExplanation(latex) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        // Hide official tiers
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';

        // Title and Badge
        this.formulaTitle.textContent = 'Custom Physics Formula';
        this.formulaBadge.className = 'badge-status badge-unregistered';
        this.formulaBadge.textContent = 'Live Analysis';

        // Deconstruct EVERY element in the custom LaTeX string
        this.renderElementsBreakdown(latex, {});

        // Setup Dimensional Solver Link
        this.setupSolverLink(latex);
    },

    /**
     * Extracts all elements/symbols in the LaTeX equation, merges with official mapping,
     * resolves default values, and renders them in order of appearance.
     */
    renderElementsBreakdown(latex, officialVariables) {
        this.symbolsList.innerHTML = '';
        
        const tokens = this.extractAllMathTokens(latex);
        
        if (tokens.length === 0) {
            this.symbolsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">No math variables, constants, or operators detected.</div>';
            return;
        }

        const dynamicOverrides = this.getDynamicOverrides(latex);

        tokens.forEach(tok => {
            const symbol = tok.symbol;
            let info = null;
            
            if (this.userCustomizations[symbol]) {
                info = { ...this.userCustomizations[symbol], type: tok.type, source: 'user' };
            } else if (officialVariables[symbol]) {
                const official = officialVariables[symbol];
                info = {
                    name: official.name || symbol,
                    type: official.type || tok.type,
                    description: official.description || 'Sharded variable reference.',
                    unit: official.unit || 'dimensionless',
                    ref: official.ref || null,
                    source: 'database'
                };
            } else {
                // Try constants.json
                const constants = window.PHYSICS_CONSTANTS || {};
                let foundConstant = null;
                for (const [key, details] of Object.entries(constants)) {
                    if (details.symbol === symbol) {
                        foundConstant = details;
                        break;
                    }
                }
                
                if (foundConstant) {
                    info = {
                        name: foundConstant.name,
                        type: 'constant',
                        description: foundConstant.description,
                        unit: foundConstant.unit,
                        ref: 'constants/' + foundConstant.symbol,
                        source: 'constants'
                    };
                } else if (dynamicOverrides[symbol]) {
                    info = { ...dynamicOverrides[symbol], source: 'dynamic' };
                } else if (this.physicsDictionary[symbol]) {
                    info = { ...this.physicsDictionary[symbol], source: 'dictionary' };
                } else {
                    info = {
                        name: symbol.startsWith('\\') ? symbol.substring(1) + ' Parameter' : symbol + ' Variable',
                        type: tok.type,
                        description: 'Custom parameter. Click Edit to customize name, unit, and definition.',
                        unit: 'dimensionless',
                        source: 'fallback'
                    };
                }
            }

            this.renderVariableRow(symbol, info);
        });

        // Typeset math symbols in badges
        if (window.MathJax) {
            if (window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this.symbolsList])
                    .catch(err => console.warn('MathJax typesetting failed on breakdown:', err));
            } else if (window.MathJax.startup && window.MathJax.startup.promise) {
                window.MathJax.startup.promise.then(() => {
                    window.MathJax.typesetPromise([this.symbolsList])
                        .catch(err => console.warn('MathJax typesetting failed on breakdown (deferred):', err));
                });
            }
        }
    },

    renderVariableRow(symbol, info, existingRow = null) {
        const row = existingRow || document.createElement('div');
        row.className = 'symbol-row';
        row.setAttribute('data-symbol', symbol);
        
        let typeClass = '';
        let badgeTypeLabel = 'Variable';
        if (info.type === 'constant') {
            typeClass = 'constant-type';
            badgeTypeLabel = 'Constant';
        } else if (info.type === 'operator') {
            typeClass = 'operator-type';
            badgeTypeLabel = 'Operator';
        }

        // Wrap badge symbol in MathJax delimiters so it renders as a mathematical character
        const mathjaxSymbol = `$${symbol}$`;

        // Build name link or strong label
        let nameHtml = `<strong class="var-name-lbl" style="color: #ffffff; font-size: 0.92rem;">${info.name}</strong>`;
        if (info.ref) {
            let refUrl = '';
            if (info.ref.startsWith('constants/')) {
                refUrl = `${BASE_URL}/physics/constants#` + info.ref.replace('constants/', '');
            } else if (info.ref.startsWith('symbols/')) {
                refUrl = `${BASE_URL}/physics/symbols#` + info.ref.replace('symbols/', '');
            } else if (info.ref.startsWith('notation/')) {
                refUrl = `${BASE_URL}/physics/symbols#` + info.ref.replace('notation/', '');
            }
            if (refUrl) {
                nameHtml = `<a class="var-name-lbl" href="${refUrl}" target="_blank" style="color: var(--accent-default, #64ffda); text-decoration: none; font-size: 0.92rem; font-weight: 600; border-bottom: 1px dashed rgba(100,255,218,0.3); transition: border-color 0.2s;" onmouseover="this.style.borderColor='var(--accent-default)'" onmouseout="this.style.borderColor='rgba(100,255,218,0.3)'">${info.name}</a>`;
            }
        }

        let disambigHtml = '';
        const dictEntry = this.physicsDictionary[symbol];
        if (dictEntry && dictEntry.alternatives) {
            const allOptions = [
                { name: dictEntry.name, type: dictEntry.type || 'variable', unit: dictEntry.unit || 'dimensionless', description: dictEntry.desc || dictEntry.description || '' },
                ...dictEntry.alternatives.map(alt => ({
                    name: alt.name,
                    type: alt.type || 'variable',
                    unit: alt.unit || 'dimensionless',
                    description: alt.desc || alt.description || ''
                }))
            ];
            const availableOptions = allOptions.filter(opt => opt.name.toLowerCase() !== info.name.toLowerCase());
            if (availableOptions.length > 0) {
                disambigHtml = `
                    <div class="disambiguation-box" style="margin-top: 6px; font-size: 0.74rem; color: var(--text-muted, #94a3b8); display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
                        <span>Context overrides:</span>
                        ${availableOptions.map(opt => `
                            <button class="alt-disambig-btn" 
                                    data-name="${opt.name}" 
                                    data-type="${opt.type}" 
                                    data-unit="${opt.unit}" 
                                    data-desc="${opt.description}"
                                    style="background: rgba(100,255,218,0.05); border: 1px solid rgba(100,255,218,0.15); color: var(--accent-default, #64ffda); padding: 1px 6px; border-radius: 3px; cursor: pointer; font-size: 0.72rem; font-family: inherit; transition: all 0.2s;"
                                    onmouseover="this.style.background='rgba(100,255,218,0.12)'"
                                    onmouseout="this.style.background='rgba(100,255,218,0.05)'">
                                ${opt.name}
                            </button>
                        `).join('')}
                    </div>
                `;
            }
        }

        row.innerHTML = `
            <div class="symbol-badge ${typeClass}" title="${badgeTypeLabel}">${mathjaxSymbol}</div>
            <div class="symbol-content-wrapper" style="flex: 1; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${nameHtml}
                        <button class="edit-var-btn" style="background: transparent; border: none; color: var(--text-muted, #94a3b8); cursor: pointer; padding: 2px; display: inline-flex; align-items: center; justify-content: center; transition: color 0.2s;" title="Edit Definition">
                             <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"/></svg>
                        </button>
                    </div>
                    <span class="var-unit-lbl" style="font-size: 0.76rem; font-family: 'Fira Code', clock, monospace; color: #a8a29e; background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04); ${info.unit && info.unit !== 'dimensionless' && info.unit !== 'operator' ? '' : 'display: none;'}">${info.unit || ''}</span>
                </div>
                <div class="var-desc-lbl" style="font-size: 0.82rem; color: var(--text-muted, #94a3b8); line-height: 1.4;">${info.description || info.desc || ''}</div>
                ${disambigHtml}
            </div>
        `;

        // Clean up any existing listeners on update by cloning (only if updating existingRow)
        if (existingRow) {
            const newRow = row.cloneNode(true);
            row.parentNode.replaceChild(newRow, row);
            
            // Re-setup listeners on newRow
            newRow.addEventListener('mouseenter', () => {
                this.highlightSymbolInMath(symbol, true);
            });
            newRow.addEventListener('mouseleave', () => {
                this.highlightSymbolInMath(symbol, false);
            });

            const editBtn = newRow.querySelector('.edit-var-btn');
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleVarEditForm(newRow, symbol, info);
            });
            return;
        }

        // Interactive Highlight: Hovering over the row highlights the character in the compiled math area
        row.addEventListener('mouseenter', () => {
            this.highlightSymbolInMath(symbol, true);
        });
        row.addEventListener('mouseleave', () => {
            this.highlightSymbolInMath(symbol, false);
        });

        // Edit button click handler
        const editBtn = row.querySelector('.edit-var-btn');
        editBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleVarEditForm(row, symbol, info);
        });

        const bindAltListeners = (targetRow) => {
            const altBtns = targetRow.querySelectorAll('.alt-disambig-btn');
            altBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const newName = btn.getAttribute('data-name');
                    const newType = btn.getAttribute('data-type');
                    const newUnit = btn.getAttribute('data-unit');
                    const newDesc = btn.getAttribute('data-desc');

                    const updatedInfo = {
                        name: newName,
                        type: newType,
                        unit: newUnit,
                        description: newDesc
                    };

                    this.userCustomizations[symbol] = updatedInfo;
                    try {
                        localStorage.setItem('physics_explainer_custom_' + symbol, JSON.stringify(updatedInfo));
                    } catch (err) {
                        console.warn('Could not write custom variable definitions to localStorage:', err);
                    }

                    this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, targetRow);

                    if (window.MathJax && window.MathJax.typesetPromise) {
                        window.MathJax.typesetPromise([targetRow]).catch(err => console.warn(err));
                    }
                });
            });
        };

        bindAltListeners(row);

        if (!existingRow) {
            this.symbolsList.appendChild(row);
        }
    },

    toggleVarEditForm(row, symbol, info) {
        const wrapper = row.querySelector('.symbol-content-wrapper');
        
        wrapper.innerHTML = `
            <div class="edit-var-form" style="display: flex; flex-direction: column; gap: 8px; width: 100%; padding: 4px 0; box-sizing: border-box;">
                <div style="display: flex; gap: 10px;">
                    <input type="text" class="edit-var-name" value="${info.name}" placeholder="Variable Name" style="flex: 2; padding: 4px 8px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; color: #fff; font-size: 0.85rem; font-family: inherit; outline: none;">
                    <input type="text" class="edit-var-unit" value="${info.unit === 'dimensionless' || info.unit === 'operator' ? '' : (info.unit || '')}" placeholder="Unit (e.g. m/s)" style="flex: 1; padding: 4px 8px; background: #030712; border: 1px solid rgba(255,255,255,0.12); border-radius: 4px; color: #fff; font-size: 0.85rem; font-family: inherit; outline: none;">
                </div>
                <textarea class="edit-var-desc" rows="2" placeholder="Describe what this component represents..." style="width: 100%; padding: 6px 8px; background: #030712; border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 4px; color: #fff; font-size: 0.82rem; font-family: inherit; line-height: 1.3; resize: vertical; outline: none; box-sizing: border-box;">${info.description || info.desc || ''}</textarea>
                <div style="display: flex; gap: 8px; justify-content: flex-end;">
                    <button class="save-var-btn" style="background: var(--accent-default, #64ffda); border: none; color: #030712; padding: 3px 10px; border-radius: 4px; font-size: 0.76rem; font-weight: 600; cursor: pointer; transition: opacity 0.2s;">Save</button>
                    <button class="cancel-var-btn" style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #fff; padding: 3px 10px; border-radius: 4px; font-size: 0.76rem; cursor: pointer; transition: background 0.2s;">Cancel</button>
                </div>
            </div>
        `;

        const saveBtn = wrapper.querySelector('.save-var-btn');
        const cancelBtn = wrapper.querySelector('.cancel-var-btn');

        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const newName = wrapper.querySelector('.edit-var-name').value.trim() || symbol;
            const newUnit = wrapper.querySelector('.edit-var-unit').value.trim() || 'dimensionless';
            const newDesc = wrapper.querySelector('.edit-var-desc').value.trim() || '';

            const updatedInfo = {
                name: newName,
                unit: newUnit,
                description: newDesc,
                type: info.type
            };

            this.userCustomizations[symbol] = updatedInfo;
            try {
                localStorage.setItem('physics_explainer_custom_' + symbol, JSON.stringify(updatedInfo));
            } catch (err) {
                console.warn('Could not write custom variable definitions to localStorage:', err);
            }

            this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, row);

            // Retypeset the row
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([row]).catch(err => console.warn(err));
            }
        });

        cancelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.renderVariableRow(symbol, info, row);

            // Retypeset the row
            if (window.MathJax && window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([row]).catch(err => console.warn(err));
            }
        });

        wrapper.querySelector('.edit-var-name').focus();
    },

    extractAllMathTokens(latex) {
        if (!latex) return [];

        let text = latex.trim();

        // 1. Strip LaTeX structure environments
        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, ' ').replace(/\\end\{[a-zA-Z]+\}/g, ' ');

        // 1.5. Parse subscripts BEFORE stripping visual modifiers to detect \text{...} wrappers
        text = text.replace(/_\{([^\}]+)\}/g, (match, content) => {
            // Strip text labels inside \text{...} or \mathrm{...}
            let cleanContent = content;
            let hasLabelText = true;
            while (hasLabelText) {
                const nextContent = cleanContent.replace(/\\(text|mathrm|mathsf|mathrm)\{((?:[^{}]|\{[^{}]*\})*)\}/g, ' ');
                if (nextContent === cleanContent) {
                    hasLabelText = false;
                } else {
                    cleanContent = nextContent;
                }
            }

            // Extract Greek letters (control sequences starting with backslash)
            const greekPattern = /\\[a-zA-Z]+/g;
            const greekMatches = cleanContent.match(greekPattern) || [];

            // Extract single Roman letters
            const plainText = cleanContent.replace(/\\[a-zA-Z]+/g, '').trim();
            const isLabelWord = plainText.length >= 3;

            let activeIndices = [...greekMatches];
            if (!isLabelWord && plainText.length > 0) {
                const letters = plainText.match(/[a-zA-Z]/g) || [];
                activeIndices.push(...letters);
            }

            return activeIndices.length > 0 ? ' ' + activeIndices.join(' ') + ' ' : ' ';
        });

        text = text.replace(/_([a-zA-Z0-9])/g, (match, char) => {
            if (/[a-zA-Z]/.test(char)) {
                return ' ' + char + ' ';
            }
            return ' ';
        });

        // 2. Strip visual modifiers: \hat{H} -> H, \mathbf{p} -> p
        let hasStyles = true;
        while (hasStyles) {
            const nextText = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextText === text) {
                hasStyles = false;
            } else {
                text = nextText;
            }
        }
        text = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');

        const found = [];
        const seen = new Set();

        const addToken = (symbol, type) => {
            if (seen.has(symbol)) return;
            seen.add(symbol);
            found.push({ symbol, type });
        };

        // 3. Scan for standard physical constants symbols from constants.json first
        const constants = window.PHYSICS_CONSTANTS || {};
        for (const [key, details] of Object.entries(constants)) {
            const sym = details.symbol;
            if (this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'constant');
                // Replace matched constant in text with space to avoid partial matching later
                const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(escaped, 'g');
                text = text.replace(regex, ' ');
            }
        }

        // 5. Strip braces
        text = text.replace(/[\{\}]/g, ' ');

        // 5b. Split adjacent plain Roman letters (Strategy A)
        // E.g., F = \frac d dt (mv) -> F = \frac d d t (m v)
        text = text.replace(/(\\[a-zA-Z]+)|([a-zA-Z]+)/g, (match, latexCmd, plainWord) => {
            if (latexCmd) {
                return latexCmd;
            }
            if (plainWord && plainWord.length > 1) {
                return plainWord.split('').join(' ');
            }
            return plainWord;
        });

        // 6. Scan for multi-character LaTeX Greek letters & symbols
        const greekPattern = /\\[a-zA-Z]+/g;
        let match;
        while ((match = greekPattern.exec(text)) !== null) {
            const sym = match[0];
            // Skip structural and formatting LaTeX commands
            const structuralCmds = new Set([
                '\\frac', '\\left', '\\right', '\\sqrt', '\\cdot', '\\times', '\\div', 
                '\\iff', '\\implies', '\\ge', '\\le', '\\ast', '\\star',
                '\\boldsymbol', '\\mathbf', '\\mathsf', '\\mathrm', '\\text', '\\mathcal', 
                '\\vec', '\\hat', '\\bar', '\\tilde', '\\dot', '\\ddot', '\\underline'
            ]);
            if (structuralCmds.has(sym)) continue;
            
            const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
            addToken(sym, isOperator ? 'operator' : 'variable');
        }

        // 7. Scan for explicit mathematical operators
        const standardOperators = ['+', '-', '=', '/', '\\int', '\\oint', '\\sum', '\\partial', '\\nabla', '\\Delta'];
        standardOperators.forEach(op => {
            if (this.latexContainsSymbol(text, op)) {
                addToken(op, 'operator');
            }
        });

        // 8. Scan for single Roman letters (a-z, A-Z)
        const romanPattern = /[a-zA-Z]/g;
        while ((match = romanPattern.exec(text)) !== null) {
            const sym = match[0];
            if (this.latexContainsSymbol(text, sym)) {
                addToken(sym, 'variable');
            }
        }

        // Sort found tokens by order of appearance in the original LaTeX string
        found.sort((a, b) => {
            const indexA = latex.indexOf(a.symbol);
            const indexB = latex.indexOf(b.symbol);
            return indexA - indexB;
        });

        return found;
    },

    highlightSymbolInMath(symbol, active) {
        // Strip leading backslash for HTML text searching
        const cleanSymbol = symbol.startsWith('\\') ? symbol.substring(1) : symbol;
        
        // Find elements in preview box containing symbol
        const mathBox = document.getElementById('math-render-target');
        if (!mathBox) return;

        const elements = mathBox.querySelectorAll('mjx-container, svg, mjx-c, use, text');
        elements.forEach(el => {
            let matches = false;
            
            if (el.tagName === 'mjx-c' || el.tagName === 'text') {
                const cMatch = el.getAttribute('c');
                if (cMatch && cMatch.toLowerCase() === cleanSymbol.toLowerCase()) {
                    matches = true;
                } else if (el.textContent === cleanSymbol) {
                    matches = true;
                }
            } else if (el.tagName === 'use') {
                const href = el.getAttribute('href') || el.getAttribute('xlink:href') || '';
                if (href.toLowerCase().includes(cleanSymbol.toLowerCase())) {
                    matches = true;
                }
            }

            if (matches) {
                if (active) {
                    el.style.filter = 'drop-shadow(0 0 5px var(--accent-default, #64ffda))';
                    el.style.fill = 'var(--accent-default, #64ffda)';
                    el.style.stroke = 'var(--accent-default, #64ffda)';
                    el.style.strokeWidth = '10px';
                } else {
                    el.style.filter = '';
                    el.style.fill = '';
                    el.style.stroke = '';
                    el.style.strokeWidth = '';
                }
            }
        });
    },

    renderBridges(subtopics) {
        if (!subtopics || subtopics.length === 0) {
            this.topologicalBridges.style.display = 'none';
            return;
        }

        this.topologicalBridges.style.display = 'block';
        this.bridgesContainer.innerHTML = '';

        subtopics.forEach(st => {
            const link = document.createElement('a');
            link.href = `${BASE_URL}/physics/subtopic/${st.slug}`;
            link.className = 'bridge-tag';
            link.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
                ${st.title}
            `;
            this.bridgesContainer.appendChild(link);
        });
    },

    resetExplanation() {
        this.explainerPlaceholder.style.display = 'flex';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'none';
        this.topologicalBridges.style.display = 'none';
        
        this.formulaTitle.textContent = 'Selecting Equation...';
        this.formulaBadge.className = 'badge-status badge-unregistered';
        this.formulaBadge.textContent = 'Live Analysis';
        this.solverRedirectContainer.style.display = 'none';
    },

    tokenizeLatexSymbols(latex) {
        // Obsoleted: Replaced by the comprehensive extractAllMathTokens() above
        return [];
    },

    latexContainsSymbol(latex, sym) {
        // Escape regex special chars
        const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
        let regexStr = escaped;
        
        if (sym.startsWith('\\')) {
            regexStr = escaped + '(?![a-zA-Z])';
        } else {
            regexStr = '(?<![a-zA-Z\\\\_])' + escaped + '(?![a-zA-Z])';
        }

        const regex = new RegExp(regexStr);
        return regex.test(latex);
    },

    setupSolverLink(latex) {
        const plainText = this.latexToPlainText(latex);
        if (plainText) {
            this.solverRedirectContainer.style.display = 'block';
            this.solverRedirectLink.href = `${BASE_URL}/physics/dimensional-solver?formula=` + encodeURIComponent(plainText);
        } else {
            this.solverRedirectContainer.style.display = 'none';
        }
    },

    /**
     * Translates LaTeX formulas into standard mathematical programming/ASCIImath style
     * for seamless compatibility with the Dimensional Solver.
     */
    latexToPlainText(latex) {
        if (!latex) return '';
        
        let text = latex.trim();

        // 1. Strip delimiters if present
        text = text.replace(/^\\\(/, '').replace(/\\\)$/, '');
        text = text.replace(/^\\\[/, '').replace(/\\\]$/, '');
        text = text.replace(/^\$\$/, '').replace(/\$\$$/, '');
        text = text.replace(/^\$/, '').replace(/\$/, '');

        // 2. Normalize derivatives and common fraction structures
        text = text.replace(/\\frac\{d\}\{d([a-zA-Z])\}/g, 'd/d$1');
        text = text.replace(/\\frac\{\\partial\}\{\\partial\s*([a-zA-Z])\}/g, 'partial/partial $1');
        
        // General fractions: \frac{A}{B} -> (A) / (B)
        let hasFraction = true;
        while (hasFraction) {
            const nextText = text.replace(/\\frac\{((?:[^{}]|\{[^{}]*\})*)\}\{((?:[^{}]|\{[^{}]*\})*)\}/g, '($1)/($2)');
            if (nextText === text) {
                hasFraction = false;
            } else {
                text = nextText;
            }
        }

        // 3. Strip visual style/font command wrappers: e.g. \mathbf{F} -> F
        let hasStyles = true;
        while (hasStyles) {
            const nextText = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
            if (nextText === text) {
                hasStyles = false;
            } else {
                text = nextText;
            }
        }
        
        // Command blocks without curly braces: e.g. \mathbf F -> F
        text = text.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s+([a-zA-Z0-9])/g, '$2');

        // 4. Clean braces around exponents & subscripts: e.g. _{ext} -> _ext, ^{2} -> ^2
        text = text.replace(/_\{([^}]+)\}/g, '_$1');
        text = text.replace(/\^\{([^}]+)\}/g, '^$1');

        // 5. Map LaTeX Greek letters & symbols to plain text identifiers
        const greekMap = {
            '\\hbar': 'hbar',
            '\\epsilon_0': 'eps0',
            '\\epsilon': 'epsilon',
            '\\mu_0': 'mu0',
            '\\mu': 'mu',
            '\\pi': 'pi',
            '\\omega': 'omega',
            '\\rho': 'rho',
            '\\sigma': 'sigma',
            '\\lambda': 'lambda',
            '\\nu': 'nu',
            '\\theta': 'theta',
            '\\xi': 'xi',
            '\\eta': 'eta',
            '\\partial': 'partial',
            '\\delta': 'delta',
            '\\Delta': 'Delta',
            '\\alpha': 'alpha',
            '\\beta': 'beta',
            '\\gamma': 'gamma',
            '\\tau': 'tau',
            '\\phi': 'phi',
            '\\psi': 'psi',
            '\\chi': 'chi',
            '\\zeta': 'zeta',
            '\\dots': '...',
            '\\infty': 'inf'
        };
        
        for (const [latexSym, plainSym] of Object.entries(greekMap)) {
            const escapedSym = latexSym.replace(/\\/g, '\\\\');
            const reg = new RegExp(escapedSym, 'g');
            text = text.replace(reg, plainSym);
        }

        // 6. Replace operators
        text = text.replace(/\\cdot/g, ' * ');
        text = text.replace(/\\times/g, ' * ');
        text = text.replace(/\\ast/g, ' * ');
        text = text.replace(/\\star/g, ' * ');
        text = text.replace(/\\div/g, ' / ');

        // 7. Simplify brackets
        text = text.replace(/\\left\(/g, '(').replace(/\\right\)/g, ')');
        text = text.replace(/\\left\[/g, '[').replace(/\\right\]/g, ']');
        text = text.replace(/\\left\\\{/g, '{').replace(/\\right\\\}/g, '}');

        // 8. Simplify matrix blocks
        text = text.replace(/\\begin\{[a-zA-Z]+\}/g, '[').replace(/\\end\{[a-zA-Z]+\}/g, ']');
        text = text.replace(/&/g, ', ').replace(/\\\\/g, ', ');

        // 9. Final cleanups: strip stray backslashes before variables and extra whitespaces
        text = text.replace(/\\([a-zA-Z]+)/g, '$1');
        text = text.replace(/\s+/g, ' ');
        text = text.replace(/\*\s*\*/g, '*');
        text = text.trim();

        return text;
    }
};

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => EquationExplainer.init());
} else {
    EquationExplainer.init();
}
