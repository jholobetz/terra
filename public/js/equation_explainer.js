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
    navigationStack: [],

    variableDictionary: {
        'm': {
            name: 'Mass',
            defaultUnit: 'kg',
            description: 'A fundamental measure of the amount of matter in an object, which acts as a quantitative measure of inertia (resistance to acceleration) and determines the strength of its gravitational attraction.',
            featuredEquations: [
                { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" },
                { name: "Kinetic Energy", latex: "E_k = \\frac{1}{2} m v^2" }
            ]
        },
        't': {
            name: 'Time',
            defaultUnit: 's',
            description: 'The continuous, progressive sequence of events in which change occurs. It acts as the independent variable in dynamical equations of motion.',
            featuredEquations: [
                { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" },
                { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\frac{d\\mathbf{v}}{dt}" }
            ]
        },
        'x': {
            name: 'Position / Displacement',
            defaultUnit: 'm',
            description: 'A coordinate representing the location of a particle along a specific axis, or the displacement from an equilibrium position.',
            featuredEquations: [
                { name: "Simple Harmonic Oscillator", latex: "\\ddot{x} + \\omega^2 x = 0" }
            ]
        },
        'y': {
            name: 'Position Coordinate',
            defaultUnit: 'm',
            description: 'A coordinate representing the vertical or transverse location of a particle in space.',
            featuredEquations: []
        },
        'z': {
            name: 'Position Coordinate',
            defaultUnit: 'm',
            description: 'A coordinate representing the longitudinal or altitude location of a particle in space.',
            featuredEquations: []
        },
        'r': {
            name: 'Radial Distance / Radius',
            defaultUnit: 'm',
            description: 'The radial distance from a central source or origin, typically used in spherical or cylindrical coordinate systems.',
            featuredEquations: [
                { name: "Universal Gravitation", latex: "\\mathbf{F}_g = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}" },
                { name: "Coulomb's Law", latex: "F_e = \\frac{1}{4\\pi\\epsilon_0} \\frac{q_1 q_2}{r^2}" }
            ]
        },
        '\\mathbf{r}': {
            name: 'Position Vector',
            defaultUnit: 'm',
            description: 'A vector pointing from the coordinate origin to the current spatial location of a particle.',
            featuredEquations: [
                { name: "Torque Definition", latex: "\\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F}" }
            ]
        },
        'v': {
            name: 'Speed / Velocity Magnitude',
            defaultUnit: 'm/s',
            description: 'The rate of change of position with respect to time, representing the speed of a particle.',
            featuredEquations: [
                { name: "Kinetic Energy", latex: "E_k = \\frac{1}{2} m v^2" }
            ]
        },
        '\\mathbf{v}': {
            name: 'Velocity Vector',
            defaultUnit: 'm/s',
            description: 'The vector rate of change of position, describing both the speed and direction of motion.',
            featuredEquations: [
                { name: "Linear Momentum", latex: "\\mathbf{p} = m \\mathbf{v}" }
            ]
        },
        'a': {
            name: 'Acceleration Magnitude',
            defaultUnit: 'm/s²',
            description: 'The rate of change of speed or velocity magnitude with respect to time.',
            featuredEquations: []
        },
        '\\mathbf{a}': {
            name: 'Acceleration Vector',
            defaultUnit: 'm/s²',
            description: 'The vector rate of change of velocity: \\mathbf{a} = \\frac{d\\mathbf{v}}{dt}.',
            featuredEquations: [
                { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" }
            ]
        },
        'p': {
            name: 'Momentum / Pressure',
            defaultUnit: 'kg·m/s or Pa',
            description: 'A symbol representing momentum or pressure depending on context.',
            contexts: {
                'mechanics': {
                    name: 'Linear Momentum ($p$)',
                    unit: 'kg·m/s',
                    description: 'The magnitude of linear momentum, representing the quantity of motion of a particle.'
                },
                'thermodynamics': {
                    name: 'Pressure ($p$ or $P$)',
                    unit: 'Pa (Pascals)',
                    description: 'The force applied perpendicular to the surface of an object per unit area, emerging from gas particle collisions.'
                }
            },
            featuredEquations: [
                { name: "Ideal Gas Law", latex: "P V = N k_B T" }
            ]
        },
        '\\mathbf{p}': {
            name: 'Linear Momentum Vector',
            defaultUnit: 'kg·m/s',
            description: 'The product of mass and velocity vector: \\mathbf{p} = m\\mathbf{v}. A conserved quantity in translationally invariant systems.',
            featuredEquations: [
                { name: "Linear Momentum", latex: "\\mathbf{p} = m \\mathbf{v}" },
                { name: "De Broglie Wave Relation", latex: "\\mathbf{p} = \\hbar \\mathbf{k}" }
            ]
        },
        'F': {
            name: 'Force Magnitude',
            defaultUnit: 'N',
            description: 'The magnitude of an interaction that causes an object with mass to accelerate.',
            featuredEquations: []
        },
        '\\mathbf{F}': {
            name: 'Force Vector',
            defaultUnit: 'N',
            description: 'The vector representation of any interaction that, when unopposed, will change the motion of an object.',
            featuredEquations: [
                { name: "Newton's Second Law", latex: "\\mathbf{F} = m \\mathbf{a}" }
            ]
        },
        'E': {
            name: 'Total Energy',
            defaultUnit: 'J',
            description: 'The total conserved energy of a system, encompassing kinetic, potential, and internal forms. Time translation symmetry leads to energy conservation.',
            featuredEquations: [
                { name: "Mass-Energy Equivalence", latex: "E = m c^2" }
            ]
        },
        'L': {
            name: 'Angular Momentum Magnitude',
            defaultUnit: 'kg·m²/s',
            description: 'The rotational analog of linear momentum.',
            featuredEquations: []
        },
        '\\mathbf{L}': {
            name: 'Angular Momentum Vector',
            defaultUnit: 'kg·m²/s',
            description: 'The vector rotational momentum, defined as \\mathbf{L} = \\mathbf{r} \\times \\mathbf{p}. Angular momentum is conserved in systems with rotational symmetry.',
            featuredEquations: [
                { name: "Rotational Dynamics", latex: "\\boldsymbol{\\tau} = \\frac{d\\mathbf{L}}{dt}" }
            ]
        },
        'k': {
            name: 'Stiffness / Boltzmann Constant / Wave Number',
            defaultUnit: 'N/m or J/K or rad/m',
            description: 'A physical parameter representing stiffness, the Boltzmann constant, or wave number depending on context.',
            contexts: {
                'mechanics': {
                    name: 'Spring Stiffness (Hooke\'s Constant)',
                    unit: 'N/m',
                    description: 'The rigidity of a spring or elastic medium, defining restoring force per unit of displacement: $F = -kx$.'
                },
                'thermodynamics': {
                    name: 'Boltzmann Constant ($k_B$)',
                    unit: 'J/K',
                    description: 'A physical constant relating average gas kinetic energy with thermodynamic temperature: $E = \\frac{3}{2} k_B T$.'
                }
            },
            featuredEquations: [
                { name: "Ideal Gas Law", latex: "P V = N k_B T" },
                { name: "Simple Harmonic Oscillator", latex: "\\ddot{x} + \\omega^2 x = 0" }
            ]
        },
        'T': {
            name: 'Temperature / Tension / Period',
            defaultUnit: 'K or N or s',
            description: 'A symbol representing temperature, tension, or period depending on context.',
            contexts: {
                'mechanics': {
                    name: 'Tension / Period',
                    unit: 'N or s',
                    description: 'In dynamics, tension force in a string/cable, or period (time per cycle) of periodic motion.'
                },
                'thermodynamics': {
                    name: 'Absolute Temperature',
                    unit: 'K (Kelvin)',
                    description: 'A measure of the average kinetic energy of the particles in a system, starting from absolute zero (0 K).'
                }
            },
            featuredEquations: [
                { name: "Ideal Gas Law", latex: "P V = N k_B T" }
            ]
        },
        '\\omega': {
            name: 'Angular Frequency',
            defaultUnit: 'rad/s',
            description: 'A scalar measure of rotation rate or oscillation frequency, representing $2\\pi f$.',
            featuredEquations: [
                { name: "Simple Harmonic Oscillator", latex: "\\ddot{x} + \\omega^2 x = 0" }
            ]
        },
        '\\tau': {
            name: 'Torque / Shear Stress',
            defaultUnit: 'N·m or Pa',
            contexts: {
                'mechanics': {
                    name: 'Torque',
                    unit: 'N·m',
                    description: 'The rotational equivalent of force, representing the tendency of a force to rotate an object about an axis.'
                }
            },
            featuredEquations: []
        },
        '\\boldsymbol{\\tau}': {
            name: 'Torque Vector',
            defaultUnit: 'N·m',
            description: 'The vector representation of torque, defined as \\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F}.',
            featuredEquations: [
                { name: "Torque Definition", latex: "\\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F}" },
                { name: "Rotational Dynamics", latex: "\\boldsymbol{\\tau} = \\frac{d\\mathbf{L}}{dt}" }
            ]
        },
        '\\psi': {
            name: 'Quantum Wavefunction',
            defaultUnit: 'probability amplitude',
            description: 'A complex wavefunction describing the probability amplitude of a quantum state.',
            featuredEquations: []
        },
        '\\Psi': {
            name: 'Wavefunction (Time-Dependent)',
            defaultUnit: 'probability amplitude',
            description: 'The time-dependent quantum state wave function satisfying the Schrödinger equation.',
            featuredEquations: [
                { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" }
            ]
        }
    },
    
    // User customizations storage (loaded from localStorage)
    userCustomizations: {},
    
    // DOM Elements
    latexInput: null,
    clearBtn: null,
    mathRenderTarget: null,
    compilerStatus: null,
    formulaTitle: null,
    formulaBadge: null,
    conceptualIntroCard: null,
    
    aiScenariosSection: null,
    aiScenariosList: null,
    aiSimulationCard: null,
    sandboxCanvas: null,
    sandboxSliders: null,
    sonifyToggleBtn: null,
    
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
    
    // Sandbox State
    sandboxCtx: null,
    sandboxAnimationId: null,
    sandboxType: 'scaling', // 'divergence', 'curl', 'wave', 'scaling'
    sandboxParams: {},      // variable -> numericValue
    
    // Audio State
    audioCtx: null,
    audioOscillator: null,
    audioGain: null,
    isSonifying: false,
    
    // Glossary of standard subscripts and superscripts as modifiers
    modifierGlossary: {
        // Subscripts
        'ext': { name: 'External', desc: 'Indicates a quantity exerted on the system by the external environment.' },
        'abs': { name: 'Absolute', desc: 'Indicates a quantity measured relative to a fixed, absolute reference frame.' },
        'int': { name: 'Internal', desc: 'Indicates a quantity originating from or acting within the boundaries of the system.' },
        'net': { name: 'Net', desc: 'The vector or scalar sum of all individual contributions (e.g., net force).' },
        'eff': { name: 'Effective', desc: 'The net functional value of a parameter under specific real-world conditions.' },
        'max': { name: 'Maximum', desc: 'The peak upper limit of a varying physical quantity.' },
        'min': { name: 'Minimum', desc: 'The absolute lower limit of a varying physical quantity.' },
        'init': { name: 'Initial', desc: 'The starting state of a variable before a process or transformation.' },
        'final': { name: 'Final', desc: 'The ending state of a variable at the conclusion of a process.' },
        'tot': { name: 'Total', desc: 'The accumulated sum of all components in a system.' },
        'in': { name: 'Incoming / Input', desc: 'Indicates a quantity entering a boundary or input channel.' },
        'out': { name: 'Outgoing / Output', desc: 'Indicates a quantity leaving a boundary or output channel.' },
        'sys': { name: 'System', desc: 'Refers to the specific thermodynamic or mechanical system under study.' },
        'surr': { name: 'Surroundings', desc: 'Refers to the environment outside the defined system boundaries.' },
        'avg': { name: 'Average', desc: 'The mean value of a parameter evaluated over a spatial or temporal interval.' },
        
        // Superscripts
        '\\circ': { name: 'Standard State', desc: 'Plimsoll symbol indicating the quantity is evaluated under standard thermodynamic reference conditions (e.g. 1 bar).' },
        '\\dagger': { name: 'Hermitian Adjoint', desc: 'Represents the conjugate transpose of an operator in quantum mechanics.' },
        'T': { name: 'Matrix Transpose', desc: 'Represents the transpose operation on a matrix or vector.' },
        '\\top': { name: 'Matrix Transpose', desc: 'Represents the transpose operation on a matrix or vector.' },
        '*': { name: 'Complex Conjugate', desc: 'Represents the complex conjugate of a complex quantity.' },
        '\\ast': { name: 'Complex Conjugate', desc: 'Represents the complex conjugate of a complex quantity.' },
        '\\prime': { name: 'Primed Reference Frame', desc: 'Denotes coordinates or quantities measured in a moving reference frame.' },
        '+': { name: 'Positive Charge', desc: 'Denotes that the particle or state carries a positive elementary electric charge.' },
        '-': { name: 'Negative Charge', desc: 'Denotes that the particle or state carries a negative elementary electric charge.' },
        '0': { name: 'Neutral Charge', desc: 'Denotes that the particle or state carries no electric charge.' }
    },
    
    // Comprehensive physics dictionary mapping standard variables, constants, and operators
    physicsDictionary: {
        // Operators
        '\\partial': { name: 'Partial Derivative', type: 'operator', unit: 'operator', desc: 'Represents differentiation with respect to a single variable in multi-variable calculus.' },
        '\\nabla': { name: 'Del / Gradient Operator', type: 'operator', unit: 'operator', desc: 'The vector differential operator representing gradient, divergence, or curl.' },
        '\\Delta': { name: 'Laplacian / Change Operator', type: 'operator', unit: 'operator', desc: 'Denotes either a difference/change in a variable, or the second-order spatial derivative operator.' },
        '\\int': { name: 'Integral Operator', type: 'operator', unit: 'operator', desc: 'Represents continuous summation or the area under a curve.' },
        '\\oint': { name: 'Closed Loop Integral', type: 'operator', unit: 'operator', desc: 'Represents line or surface integration over a closed boundary.' },
        '\\sum': { name: 'Summation Operator', type: 'operator', unit: 'operator', desc: 'Represents discrete addition of a sequence of terms.' },
        '\\sqrt': { name: 'Square Root Operator', type: 'operator', unit: 'operator', desc: 'Represents the principal square root function, returning a number that, when multiplied by itself, yields the operand.' },
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
            domain: 'thermodynamics',
            alternatives: [
                { name: 'Spring Constant', type: 'variable', unit: 'N/m', desc: 'The force constant representing the stiffness of a spring (Hooke\'s Law).', domain: 'classical_mechanics' },
                { name: 'Wave Vector', type: 'variable', unit: 'rad/m', desc: 'A vector indicating the direction and rate of space-phase variation of a wave.', domain: 'optics' },
                { name: 'Thermal Conductivity', type: 'variable', unit: 'W/(m·K)', desc: 'The measure of a material\'s ability to conduct heat.', domain: 'thermodynamics' }
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
            domain: 'thermodynamics',
            alternatives: [
                { name: 'Power', type: 'variable', unit: 'W', desc: 'The rate at which work is done or energy is transferred.', domain: 'classical_mechanics' },
                { name: 'Probability', type: 'variable', unit: 'dimensionless', desc: 'The likelihood of a specific event occurring, ranging from 0 to 1.', domain: 'quantum_mechanics' },
                { name: 'Momentum', type: 'variable', unit: 'kg·m/s', desc: 'The product of the mass and velocity of an object (uppercase variant).', domain: 'classical_mechanics' }
            ]
        },
        'Q': { name: 'Heat / Total Charge', type: 'variable', unit: 'J or C', desc: 'Thermal energy transferred due to temperature difference, or net electrical charge.' },
        'R': { name: 'Ideal Gas Constant / Resistance / Radius', type: 'constant', unit: 'J/(mol·K) or Ω or m', desc: 'Universal gas constant, electrical resistance, or spatial radius.' },
        'S': {
            name: 'Entropy',
            type: 'variable',
            unit: 'J/K',
            desc: 'A thermodynamic quantity representing the degree of disorder or randomness in a system.',
            domain: 'thermodynamics',
            alternatives: [
                { name: 'Action', type: 'variable', unit: 'J·s', desc: 'The path integral of the Lagrangian over time representing the trajectory of a system.', domain: 'classical_mechanics' },
                { name: 'Poynting Vector', type: 'variable', unit: 'W/m²', desc: 'The directional energy flux density of an electromagnetic field.', domain: 'electromagnetism' }
            ]
        },
        'T': {
            name: 'Temperature',
            type: 'variable',
            unit: 'K',
            desc: 'Thermodynamic temperature scale measuring the average kinetic energy of the particles.',
            domain: 'thermodynamics',
            alternatives: [
                { name: 'Time Period', type: 'variable', unit: 's', desc: 'The duration of one complete cycle of a repeating wave or oscillation.', domain: 'optics' },
                { name: 'Tension', type: 'variable', unit: 'N', desc: 'Axial pulling force transmitted through a string, rope, or chain.', domain: 'classical_mechanics' },
                { name: 'SU(3) Gauge Generator', type: 'variable', unit: 'dimensionless', desc: 'Generators of the SU(3) color gauge group in quantum chromodynamics, typically represented by the Gell-Mann matrices.', domain: 'quantum_mechanics' }
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
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Weak Hypercharge', type: 'variable', unit: 'dimensionless', desc: 'The generator of the U(1) weak hypercharge gauge group.', domain: 'quantum_mechanics' },
                { name: 'Spherical Harmonic', type: 'variable', unit: 'dimensionless', desc: 'Angular wavefunction solutions to Laplace\'s equation in spherical coordinates.', domain: 'quantum_mechanics' }
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
        
        // 1. Resolve Active Domain
        const domainParam = urlParams.get('domain') || window.INITIAL_DOMAIN;
        if (domainParam) {
            const DOMAIN_MAP = {
                'classical-mechanics': 'classical_mechanics',
                'thermodynamics-statistical-mechanics': 'thermodynamics',
                'electromagnetism': 'electromagnetism',
                'quantum-physics': 'quantum_mechanics',
                'quantum_mechanics': 'quantum_mechanics',
                'particle-physics': 'quantum_mechanics',
                'standard-model': 'quantum_mechanics',
                'optics': 'optics'
            };
            this.activeDomain = DOMAIN_MAP[domainParam] || domainParam;
            if (this.activeDomainSelect && this.activeDomain) {
                this.activeDomainSelect.value = this.activeDomain;
            }
        }
        
        // 2. Resolve Subtopic variables (from Query param or injected script state)
        const subtopicParam = urlParams.get('subtopic') || window.SUBTOPIC_SLUG;
        if (subtopicParam) {
            window.SUBTOPIC_SLUG = subtopicParam;
            if (!window.SUBTOPIC_VARIABLES || Object.keys(window.SUBTOPIC_VARIABLES).length === 0) {
                fetch(`${BASE_URL}/physics/api/subtopic-variables/${subtopicParam}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success) {
                            window.SUBTOPIC_VARIABLES = data.variables || {};
                            if (this.latexInput && this.latexInput.value.trim()) {
                                this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                            }
                        }
                    })
                    .catch(err => console.warn('Could not fetch subtopic variables:', err));
            }
        }

        // 3. Resolve HTTP Referrer Context (when deep linking from a subtopic page without parameters)
        const referrer = document.referrer;
        if (!subtopicParam && referrer && referrer.includes('/physics/subtopic/')) {
            const parts = referrer.split('/');
            const subtopicSlug = parts[parts.length - 1].split('?')[0];
            window.SUBTOPIC_SLUG = subtopicSlug;
            
            // Fetch variables for the referrer subtopic
            fetch(`${BASE_URL}/physics/api/subtopic-variables/${subtopicSlug}`)
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.SUBTOPIC_VARIABLES = data.variables || {};
                        if (this.latexInput && this.latexInput.value.trim()) {
                            this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                        }
                    }
                })
                .catch(err => console.warn('Could not fetch subtopic variables from referrer:', err));
            
            // Map the referrer subtopic back to its physics domain
            fetch(`${BASE_URL}/physics/search-index`)
                .then(res => res.json())
                .then(index => {
                    const entry = index[subtopicSlug];
                    if (entry && entry.s) {
                        const shard = entry.s.replace('.json', '');
                        const DOMAIN_MAP = {
                            'classical-mechanics': 'classical_mechanics',
                            'thermodynamics-statistical-mechanics': 'thermodynamics',
                            'electromagnetism': 'electromagnetism',
                            'quantum-physics': 'quantum_mechanics',
                            'particle-physics': 'quantum_mechanics',
                            'standard-model': 'quantum_mechanics',
                            'optics': 'optics'
                        };
                        this.activeDomain = DOMAIN_MAP[shard] || '';
                        if (this.activeDomain) {
                            console.log(`Detected active domain: ${this.activeDomain} from referrer subtopic ${subtopicSlug}`);
                            if (this.activeDomainSelect) {
                                this.activeDomainSelect.value = this.activeDomain;
                            }
                            if (this.latexInput && this.latexInput.value.trim() && !this.currentId) {
                                this.renderElementsBreakdown(this.latexInput.value.trim(), {});
                            }
                        }
                    }
                })
                .catch(err => console.warn('Could not determine referrer context:', err));
        } else if (!domainParam && !subtopicParam) {
            // Legacy context param fallback
            const contextParam = urlParams.get('context');
            if (contextParam) {
                const DOMAIN_MAP = {
                    'classical-mechanics': 'classical_mechanics',
                    'thermodynamics-statistical-mechanics': 'thermodynamics',
                    'electromagnetism': 'electromagnetism',
                    'quantum-physics': 'quantum_mechanics',
                    'particle-physics': 'quantum_mechanics',
                    'standard-model': 'quantum_mechanics',
                    'optics': 'optics'
                };
                this.activeDomain = DOMAIN_MAP[contextParam] || contextParam;
                if (this.activeDomainSelect && this.activeDomain) {
                    this.activeDomainSelect.value = this.activeDomain;
                }
            }
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

    isSingleSymbol(latex) {
        const cleaned = latex.trim().replace(/^\\\[/, '').replace(/\\\]$/, '').replace(/^\$\$/, '').replace(/\$\$/, '').replace(/^\$/, '').replace(/\$/, '').trim();
        const innerMatch = cleaned.match(/^\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol)\{([a-zA-Z\\]+)\}$/);
        if (innerMatch) {
            return innerMatch[2].length <= 10;
        }
        const simpleCleaned = cleaned.replace(/\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol|mathrm|mathsf)/g, '').replace(/[\{\}]/g, '');
        return simpleCleaned.length <= 4 && !/[=+\-*\/<>|]/.test(simpleCleaned);
    },

    resolveSymbolInfo(symbol) {
        let cleanSymbol = symbol.trim().replace(/^\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol)\{([a-zA-Z\\]+)\}$/, '$2').replace(/[\{\}]/g, '');
        
        // 1. Check constants first
        const constants = window.PHYSICS_CONSTANTS || {};
        for (const [key, details] of Object.entries(constants)) {
            if (details.symbol === symbol || details.symbol === cleanSymbol) {
                // Predefine prominent featured equations for constants
                const constantEquations = {
                    'h-bar': [
                        { name: "Schrödinger Equation", latex: "i \\hbar \\frac{\\partial}{\\partial t}\\Psi = \\hat{H}\\Psi" },
                        { name: "Heisenberg Uncertainty Principle", latex: "\\Delta x \\Delta p \\ge \\frac{\\hbar}{2}" }
                    ],
                    'c': [
                        { name: "Mass-Energy Equivalence", latex: "E = m c^2" },
                        { name: "Einstein Field Equations", latex: "G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}" }
                    ],
                    'G': [
                        { name: "Universal Gravitation", latex: "\\mathbf{F}_g = -G \\frac{m_1 m_2}{r^2} \\hat{\\mathbf{r}}" },
                        { name: "Einstein Field Equations", latex: "G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}" }
                    ],
                    'k-B': [
                        { name: "Ideal Gas Law", latex: "P V = N k_B T" },
                        { name: "Boltzmann Entropy Formula", latex: "S = k_B \\ln \\Omega" }
                    ],
                    'epsilon-0': [
                        { name: "Gauss's Law", latex: "\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\epsilon_0}" },
                        { name: "Coulomb's Law", latex: "F_e = \\frac{1}{4\\pi\\epsilon_0} \\frac{q_1 q_2}{r^2}" }
                    ],
                    'mu-0': [
                        { name: "Ampere's Law", latex: "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}" },
                        { name: "Speed of Light Relation", latex: "c = \\frac{1}{\\sqrt{\\epsilon_0 \\mu_0}}" }
                    ]
                };

                return {
                    name: details.name,
                    type: 'constant',
                    description: details.description || details.desc || 'Fundamental physical constant.',
                    value: details.value,
                    unit: details.unit,
                    featuredEquations: constantEquations[key] || []
                };
            }
        }
        
        // 2. Check variable dictionary with context override
        const dictEntry = this.variableDictionary[cleanSymbol] || this.variableDictionary[symbol];
        if (dictEntry) {
            let activeCtx = null;
            if (this.activeDomain && dictEntry.contexts && dictEntry.contexts[this.activeDomain]) {
                activeCtx = dictEntry.contexts[this.activeDomain];
            } else if (dictEntry.contexts) {
                const firstCtxKey = Object.keys(dictEntry.contexts)[0];
                activeCtx = dictEntry.contexts[firstCtxKey];
            }
            
            return {
                name: activeCtx ? activeCtx.name : dictEntry.name,
                type: 'variable',
                description: activeCtx ? activeCtx.description : dictEntry.description,
                unit: activeCtx ? (activeCtx.unit || dictEntry.defaultUnit) : dictEntry.defaultUnit,
                featuredEquations: dictEntry.featuredEquations || []
            };
        }
        
        // 3. Fallback
        return {
            name: symbol.startsWith('\\') ? symbol.substring(1).charAt(0).toUpperCase() + symbol.substring(2) + ' Parameter' : symbol + ' Variable',
            type: 'variable',
            description: 'This symbol represents a variable or parameter within the current physical equation.',
            unit: 'dimensionless',
            featuredEquations: []
        };
    },

    drillDownIntoSymbol(symbol, info) {
        this.pushToNavigationStack();
        this.updateUrlParams(symbol, null);
        if (this.latexInput) {
            this.latexInput.value = symbol;
        }
        this.compileMathJax(symbol);
        this.renderSymbolExplanation(symbol);
    },

    pushToNavigationStack() {
        const currentItem = {
            id: this.currentId,
            latex: this.currentLatex,
            formula: this.currentFormula,
            subtopics: this.currentSubtopics,
            title: this.formulaTitle.textContent || this.formulaTitle.innerHTML
        };
        if (this.navigationStack.length > 0) {
            const last = this.navigationStack[this.navigationStack.length - 1];
            if (last.latex === currentItem.latex) return;
        }
        this.navigationStack.push(currentItem);
    },

    popNavigationStack() {
        if (this.navigationStack.length === 0) return;
        const previous = this.navigationStack.pop();
        
        this.currentId = previous.id;
        this.currentLatex = previous.latex;
        this.currentFormula = previous.formula;
        this.currentSubtopics = previous.subtopics;
        
        this.latexInput.value = previous.latex;
        
        this.compileMathJax(previous.latex);
        if (previous.formula) {
            this.renderFormula(previous.formula, previous.subtopics);
        } else {
            this.renderCustomExplanation(previous.latex);
        }
        
        this.updateUrlParams(previous.latex, previous.id);
        this.renderBreadcrumbs();
    },

    updateUrlParams(latex, id) {
        const url = new URL(window.location);
        if (latex) {
            url.searchParams.set('latex', latex);
        } else {
            url.searchParams.delete('latex');
        }
        if (id) {
            url.searchParams.set('id', id);
        } else {
            url.searchParams.delete('id');
        }
        window.history.pushState({}, '', url);
    },

    renderBreadcrumbs() {
        const container = document.getElementById('explainer-breadcrumbs');
        if (!container) return;
        
        console.log("Rendering breadcrumbs, navigation stack length:", this.navigationStack.length);
        
        if (this.navigationStack.length === 0) {
            container.style.display = 'none';
            container.innerHTML = '';
            return;
        }
        
        try {
            container.style.display = 'flex';
            container.innerHTML = '';
            
            const backBtn = document.createElement('button');
            backBtn.style.background = 'transparent';
            backBtn.style.border = 'none';
            backBtn.style.color = 'var(--accent-default, #64ffda)';
            backBtn.style.cursor = 'pointer';
            backBtn.style.fontSize = '0.8rem';
            backBtn.style.padding = '0';
            backBtn.style.display = 'inline-flex';
            backBtn.style.alignItems = 'center';
            backBtn.style.gap = '4px';
            backBtn.style.marginRight = '8px';
            backBtn.innerHTML = `
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                Back
            `;
            backBtn.addEventListener('click', () => {
                this.popNavigationStack();
            });
            container.appendChild(backBtn);
            
            this.navigationStack.forEach((item, index) => {
                const link = document.createElement('span');
                link.style.cursor = 'pointer';
                link.style.textDecoration = 'underline';
                link.style.textUnderlineOffset = '2px';
                link.style.color = 'var(--text-muted, #94a3b8)';
                
                let text = '';
                if (item.formula) {
                    text = item.title.replace(/\([^\)]+\)/g, '').trim();
                } else {
                    text = '\\( ' + (item.latex || '') + ' \\)';
                }
                
                link.innerHTML = text;
                link.addEventListener('click', () => {
                    while (this.navigationStack.length > index) {
                        this.popNavigationStack();
                    }
                });
                container.appendChild(link);
                
                const separator = document.createElement('span');
                separator.textContent = ' › ';
                separator.style.color = 'rgba(255,255,255,0.2)';
                container.appendChild(separator);
            });
            
            const currentLabel = document.createElement('span');
            currentLabel.style.color = '#ffffff';
            currentLabel.style.fontWeight = '500';
            currentLabel.innerHTML = '\\( ' + (this.latexInput ? this.latexInput.value : '') + ' \\)';
            container.appendChild(currentLabel);
            
            this.triggerTypeset([container]);
        } catch (e) {
            console.error("Error rendering breadcrumbs:", e);
        }
    },

    renderSymbolExplanation(latex) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        const symbol = latex.trim();
        
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';
        if (this.aiSimulationCard) this.aiSimulationCard.style.display = 'none';
        if (this.solverRedirectContainer) this.solverRedirectContainer.style.display = 'none';

        let symbolInfo = this.resolveSymbolInfo(symbol);

        this.formulaTitle.innerHTML = `${symbolInfo.name} (\\( ${symbol} \\))`;
        if (this.formulaBadge) {
            this.formulaBadge.style.display = 'inline-block';
            if (symbolInfo.type === 'constant') {
                this.formulaBadge.className = 'badge-status';
                this.formulaBadge.style.background = 'rgba(234, 179, 8, 0.1)';
                this.formulaBadge.style.color = '#eab308';
                this.formulaBadge.style.border = '1px solid rgba(234, 179, 8, 0.25)';
                this.formulaBadge.textContent = 'Physical Constant';
            } else {
                this.formulaBadge.className = 'badge-status';
                this.formulaBadge.style.background = 'rgba(59, 130, 246, 0.1)';
                this.formulaBadge.style.color = '#3b82f6';
                this.formulaBadge.style.border = '1px solid rgba(59, 130, 246, 0.25)';
                this.formulaBadge.textContent = 'Physical Variable';
            }
        }

        if (this.conceptualIntroCard) {
            this.conceptualIntroCard.style.display = 'flex';
            
            let valRow = '';
            if (symbolInfo.type === 'constant' && symbolInfo.value) {
                valRow = `
                    <div style="margin-top: 8px; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-family: 'Fira Code', monospace; font-size: 0.88rem;">
                        <span style="color: var(--text-muted, #94a3b8);">Numerical Value:</span>
                        <strong style="color: #fbbf24; margin-left: 6px;">${symbolInfo.value}</strong> 
                        <span style="color: #a8a29e; margin-left: 6px;">${symbolInfo.unit || ''}</span>
                    </div>
                `;
            } else if (symbolInfo.unit && symbolInfo.unit !== 'dimensionless') {
                valRow = `
                    <div style="margin-top: 8px; padding: 10px; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-family: 'Fira Code', monospace; font-size: 0.88rem;">
                        <span style="color: var(--text-muted, #94a3b8);">Standard SI Unit:</span>
                        <strong style="color: var(--accent-default, #64ffda); margin-left: 6px;">${symbolInfo.unit}</strong>
                    </div>
                `;
            }

            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Symbol Definition
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${this.wrapTextMathDelimiters(symbolInfo.description)}
                </div>
                ${valRow}
            `;
        }

        this.renderSymbolContextEquations(symbol, symbolInfo);
        this.renderBreadcrumbs();
        this.triggerTypeset([this.formulaTitle, this.conceptualIntroCard]);
    },

    renderSymbolContextEquations(symbol, symbolInfo) {
        this.symbolsList.innerHTML = '';
        
        let equations = symbolInfo.featuredEquations || [];
        
        if (equations.length === 0) {
            this.symbolsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic; padding: 10px;">Select another equation in the editor to see it breakdown into its components.</div>';
            return;
        }

        const header = document.createElement('div');
        header.style.fontSize = '0.85rem';
        header.style.textTransform = 'uppercase';
        header.style.letterSpacing = '0.05em';
        header.style.color = 'var(--text-muted, #94a3b8)';
        header.style.marginBottom = '12px';
        header.style.fontFamily = "'Space Grotesk', sans-serif";
        header.textContent = `Featured Equations with ${symbol}`;
        this.symbolsList.appendChild(header);

        equations.forEach(eq => {
            const row = document.createElement('div');
            row.className = 'symbol-row';
            row.style.cursor = 'pointer';
            row.style.transition = 'all 0.2s';
            row.style.border = '1px solid rgba(255, 255, 255, 0.04)';
            
            row.addEventListener('mouseover', () => {
                row.style.background = 'rgba(100, 255, 218, 0.03)';
                row.style.borderColor = 'rgba(100, 255, 218, 0.2)';
            });
            row.addEventListener('mouseout', () => {
                row.style.background = '';
                row.style.borderColor = 'rgba(255, 255, 255, 0.04)';
            });
            
            row.addEventListener('click', () => {
                this.navigationStack = [];
                this.latexInput.value = eq.latex;
                this.handleInputChange();
            });

            row.innerHTML = `
                <div class="symbol-badge" style="background: rgba(100, 255, 218, 0.05); border-color: rgba(100, 255, 218, 0.15); color: var(--accent-default, #64ffda); font-size: 0.8rem; padding: 4px 8px; border-radius: 4px; font-family: 'Space Grotesk', sans-serif;">EQ</div>
                <div class="symbol-content-wrapper" style="flex: 1; display: flex; flex-direction: column; gap: 4px;">
                    <strong style="color: #ffffff; font-size: 0.92rem;">${eq.name}</strong>
                    <div style="font-family: 'Fira Code', monospace; font-size: 0.82rem; color: var(--text-muted, #94a3b8); margin-top: 2px;">$${eq.latex}$</div>
                </div>
            `;
            this.symbolsList.appendChild(row);
        });

        this.triggerTypeset([this.symbolsList]);
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
        this.copyBtn = document.getElementById('copy-input-btn');
        this.mathRenderTarget = document.getElementById('math-render-target');
        this.compilerStatus = document.getElementById('compiler-status');
        
        this.formulaTitle = document.getElementById('formula-title');
        this.formulaBadge = document.getElementById('formula-badge');
        this.conceptualIntroCard = document.getElementById('conceptual-intro-card');
        
        this.aiScenariosSection = document.getElementById('ai-scenarios-section');
        this.aiScenariosList = document.getElementById('ai-scenarios-list');
        this.aiSimulationCard = document.getElementById('ai-simulation-card');
        this.sandboxCanvas = document.getElementById('sandbox-canvas');
        this.sandboxSliders = document.getElementById('sandbox-sliders');
        this.sonifyToggleBtn = document.getElementById('sonify-toggle-btn');
        
        this.officialBreakdown = document.getElementById('official-breakdown');
        this.symbolsBreakdown = document.getElementById('symbols-breakdown');
        this.symbolsList = document.getElementById('symbols-list');
        this.modifiersSection = document.getElementById('modifiers-section');
        this.modifiersList = document.getElementById('modifiers-list');
        this.topologicalBridges = document.getElementById('topological-bridges');
        this.bridgesContainer = document.getElementById('bridges-container');
        this.explainerPlaceholder = document.getElementById('explainer-placeholder');
        this.solverRedirectContainer = document.getElementById('solver-redirect-container');
        this.solverRedirectLink = document.getElementById('solver-redirect-link');
        this.activeDomainSelect = document.getElementById('active-domain-select');
    },

    bindEvents() {
        if (this.activeDomainSelect) {
            this.activeDomainSelect.addEventListener('change', (e) => {
                this.activeDomain = e.target.value;
                if (this.latexInput && this.latexInput.value.trim()) {
                    this.renderElementsBreakdown(this.latexInput.value.trim(), this.officialVariables || {});
                }
            });
        }

        // Handle browser back/forward buttons natively
        window.addEventListener('popstate', () => {
            const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            const latex = urlParams.get('latex');
            
            this.navigationStack = []; // Reset stack on external history change
            
            if (id) {
                fetch(`${BASE_URL}/physics/api/explain?latex=` + encodeURIComponent(latex || '') + `&id=${id}`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.success && data.formula) {
                            this.currentId = data.formula.id;
                            this.currentLatex = data.formula.latex_source || this.getCleanLatexFromEq(data.formula.equation);
                            this.latexInput.value = this.currentLatex;
                            this.compileMathJax(this.currentLatex);
                            this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                                this.renderFormula(data.formula, subtopics);
                            });
                        }
                    });
            } else if (latex) {
                this.latexInput.value = latex;
                this.compileMathJax(latex);
                if (this.isSingleSymbol(latex)) {
                    this.renderSymbolExplanation(latex);
                } else {
                    this.lookupFormulaByLatex(latex);
                }
            } else {
                this.resetExplanation();
            }
        });

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

        // Copy button to copy LaTeX input to clipboard
        if (this.copyBtn) {
            this.copyBtn.addEventListener('click', () => {
                const latex = this.latexInput.value;
                if (!latex) return;
                
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(latex).then(() => {
                        this.copyBtn.textContent = 'Copied!';
                        this.copyBtn.style.color = 'var(--accent-default, #64ffda)';
                        setTimeout(() => {
                            this.copyBtn.textContent = 'Copy';
                            this.copyBtn.style.color = '#eab308';
                        }, 1500);
                    });
                } else {
                    // Fallback
                    this.latexInput.select();
                    document.execCommand('copy');
                    this.copyBtn.textContent = 'Copied!';
                    this.copyBtn.style.color = 'var(--accent-default, #64ffda)';
                    setTimeout(() => {
                        this.copyBtn.textContent = 'Copy';
                        this.copyBtn.style.color = '#eab308';
                    }, 1500);
                }
            });
        }

        // Sonification toggle
        if (this.sonifyToggleBtn) {
            this.sonifyToggleBtn.addEventListener('click', () => {
                this.toggleSonification();
            });
        }
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

        // 2. Route single symbols directly
        if (this.isSingleSymbol(latex)) {
            this.renderSymbolExplanation(latex);
            return;
        }

        // 3. Perform database lookup
        this.lookupFormulaByLatex(latex);
    },

    compileMathJax(latex) {
        // Enforce equation delimiters
        let mathMarkup = latex;
        if (!latex.startsWith('\\[') && !latex.startsWith('\\(') && !latex.startsWith('$$') && !latex.startsWith('$')) {
            mathMarkup = '\\[ ' + latex + ' \\]';
        }

        this.mathRenderTarget.innerHTML = mathMarkup;

        if (window.MathJax) {
            if (window.MathJax.typesetPromise) {
                window.MathJax.typesetPromise([this.mathRenderTarget])
                    .then(() => {
                        this.setCompilerStatus('Ready', '#10b981');
                    })
                    .catch((err) => {
                        console.error('MathJax Compilation Error:', err);
                        this.setCompilerStatus('Syntax Error', '#ef4444');
                    });
            } else if (window.MathJax.startup && window.MathJax.startup.promise) {
                this.setCompilerStatus('Loading Engine...', '#f59e0b');
                window.MathJax.startup.promise.then(() => {
                    window.MathJax.typesetPromise([this.mathRenderTarget])
                        .then(() => {
                            this.setCompilerStatus('Ready', '#10b981');
                        })
                        .catch((err) => {
                            console.error('MathJax Compilation Error (deferred):', err);
                            this.setCompilerStatus('Syntax Error', '#ef4444');
                        });
                });
            } else {
                this.setCompilerStatus('Renderer Offline', '#f59e0b');
            }
        } else {
            this.setCompilerStatus('Renderer Offline', '#f59e0b');
        }
    },

    triggerTypeset(elements) {
        if (!window.MathJax) {
            console.warn('MathJax not loaded yet.');
            return;
        }
        if (window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise(elements)
                .catch(err => console.warn('MathJax typesetting failed:', err));
        } else if (window.MathJax.startup && window.MathJax.startup.promise) {
            window.MathJax.startup.promise.then(() => {
                window.MathJax.typesetPromise(elements)
                    .catch(err => console.warn('MathJax typesetting failed (deferred):', err));
            });
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
        this.officialBreakdown.style.display = 'none'; // Keep legacy tiers container hidden, we map them below
        this.symbolsBreakdown.style.display = 'block';
        
        // Populate Title and Badge
        this.formulaTitle.textContent = formula.title;
        
        // Status formatting
        const status = formula.status || 'platinum-draft';
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status ' + (status.includes('draft') ? 'badge-draft' : 'badge-platinum');
            this.formulaBadge.textContent = status.replace('-', ' ').toUpperCase();
        }

        const synthesis = this.synthesizeCustomOverview(this.currentLatex);

        // Populate Conceptual Definition / Google-style summary at the top
        if (this.conceptualIntroCard) {
            const definition = this.wrapTextMathDelimiters(formula.conceptual_definition || synthesis.intro);
            const summary = this.wrapTextMathDelimiters(formula.intuitive_summary || synthesis.summary);
            
            this.conceptualIntroCard.style.display = 'flex';
            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Explanation
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${definition}
                </div>
                <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                    ${summary}
                </div>
            `;
            this.triggerTypeset([this.conceptualIntroCard]);
        }

        // Build and render scenarios
        let scenarios = formula.scenarios;
        if (!scenarios || scenarios.length === 0) {
            // Map legacy tiers to scenarios
            scenarios = [];
            if (formula.interpretation && formula.interpretation !== 'No interpretation provided.') {
                scenarios.push({
                    condition: 'Interpretation (Local Identity)',
                    implication: formula.interpretation.replace(/<[^>]*>/g, '') // Strip HTML tags for clean text
                });
            }
            if (formula.symmetry_origin && formula.symmetry_origin !== 'Symmetry derivations pending.') {
                scenarios.push({
                    condition: 'Symmetry & Coordinate Invariance',
                    implication: formula.symmetry_origin.replace(/<[^>]*>/g, '')
                });
            }
            if (formula.limits_and_boundary && formula.limits_and_boundary !== 'Boundary analysis pending.') {
                scenarios.push({
                    condition: 'Limiting Cases & Boundaries',
                    implication: formula.limits_and_boundary.replace(/<[^>]*>/g, '')
                });
            }

            // If still empty, use synthesis fallback
            if (scenarios.length === 0) {
                scenarios = synthesis.scenarios;
            }
        }
        this.renderAIScenariosSection(scenarios);

        // Deconstruct EVERY element in the LaTeX string, merging database semantic definitions for left panel hover list
        this.renderElementsBreakdown(this.currentLatex, formula.semantic_variables || {});

        // Populate Topological Bridges
        this.renderBridges(subtopics);

        // Setup Dimensional Solver Link
        this.setupSolverLink(this.currentLatex);

        // Initialize sandbox simulator
        this.initSandbox(this.currentLatex, formula.semantic_variables || {});
    },

    renderCustomExplanation(latex) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        // Hide old layout elements
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';

        // Title and Badge
        this.formulaTitle.textContent = 'Custom Physics Formula';
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status badge-unregistered';
            this.formulaBadge.textContent = 'Live Analysis';
        }

        // Synthesize dynamic AI Overview
        const synthesis = this.synthesizeCustomOverview(latex);

        if (this.conceptualIntroCard) {
            this.conceptualIntroCard.style.display = 'flex';
            this.conceptualIntroCard.innerHTML = `
                <h4 style="font-size: 0.8rem; text-transform: uppercase; color: var(--accent-default, #64ffda); margin: 0; letter-spacing: 0.1em; display: flex; align-items: center; gap: 6px; font-family: 'Space Grotesk', sans-serif;">
                    ✦ Explanation
                </h4>
                <div class="conceptual-definition" style="font-size: 1.05rem; line-height: 1.5; color: #f8fafc; font-weight: 500; font-family: 'Space Grotesk', sans-serif;">
                    ${this.wrapTextMathDelimiters(synthesis.intro)}
                </div>
                <div class="intuitive-summary" style="font-size: 0.92rem; line-height: 1.5; color: var(--text-muted, #94a3b8); border-left: 2px solid var(--accent-default, #64ffda); padding-left: 12px; font-style: italic; margin-top: 4px;">
                    ${this.wrapTextMathDelimiters(synthesis.summary)}
                </div>
            `;
            this.triggerTypeset([this.conceptualIntroCard]);
        }

        // Render AI scenarios
        this.renderAIScenariosSection(synthesis.scenarios);

        // Deconstruct EVERY element in the custom LaTeX string
        this.renderElementsBreakdown(latex, {});

        // Setup Dimensional Solver Link
        this.setupSolverLink(latex);

        // Initialize sandbox simulator
        this.initSandbox(latex, {});
    },

    /**
     * Extracts all elements/symbols in the LaTeX equation, merges with official mapping,
     * resolves default values, and renders them in order of appearance.
     */
    detectDomainFromLatex(latex) {
        if (!latex) return null;
        
        // Define anchor symbols for each domain
        const ANCHORS = {
            thermodynamics: [
                'T', 'S', 'Q', 'U', 'H', '\\Omega', '\\ln', 'k_B', 'R', 'P', 'V',
                '\\beta', '\\mu', 'N_A'
            ],
            electromagnetism: [
                '\\mathbf{E}', '\\mathbf{B}', '\\mathbf{J}', '\\rho', '\\epsilon_0',
                '\\mu_0', '\\Phi', '\\mathbf{A}', 'q', 'e', 'E_x', 'E_y', 'E_z',
                'B_x', 'B_y', 'B_z', '\\nabla \\times', '\\nabla \\cdot'
            ],
            quantum_mechanics: [
                '\\hbar', '\\Psi', '\\psi', '\\hat{H}', '\\phi', '\\hat{p}', '\\hat{x}',
                '\\mid', '\\rangle', '\\langle', 'i', '\\psi^*', '\\Psi^*', '\\hat{A}',
                '\\hat{B}', '\\psi_n', 'E_n', '\\dagger'
            ],
            optics: [
                'n', '\\lambda', 'f', '\\theta', '\\omega', 'k', 'I', 'I_0',
                '\\sin', '\\cos', '\\lambda', '\\nu'
            ]
        };
        
        const counts = {
            classical_mechanics: 0,
            thermodynamics: 0,
            electromagnetism: 0,
            quantum_mechanics: 0,
            optics: 0
        };
        
        // Count matches for each domain
        for (const [domain, symbols] of Object.entries(ANCHORS)) {
            symbols.forEach(sym => {
                const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const pattern = /^[a-zA-Z0-9]+$/.test(sym) 
                    ? new RegExp('\\b' + escaped + '\\b', 'g')
                    : new RegExp(escaped, 'g');
                    
                const matches = latex.match(pattern);
                if (matches) {
                    counts[domain] += matches.length;
                }
            });
        }
        
        // Check for classical mechanics anchors
        const classicalAnchors = ['x', 'v', 'a', 'F', 'm', 'p', 't', '\\tau', 'g', 'r'];
        classicalAnchors.forEach(sym => {
            const pattern = new RegExp('\\b' + sym + '\\b', 'g');
            const matches = latex.match(pattern);
            if (matches) {
                counts.classical_mechanics += matches.length;
            }
        });
        
        let bestDomain = null;
        let maxCount = 0;
        for (const [domain, count] of Object.entries(counts)) {
            if (count > maxCount) {
                maxCount = count;
                bestDomain = domain;
            }
        }
        
        return bestDomain;
    },

    renderElementsBreakdown(latex, officialVariables) {
        this.symbolsList.innerHTML = '';
        if (this.modifiersList) {
            this.modifiersList.innerHTML = '';
        }
        
        // Save officialVariables for redraw on domain change
        this.officialVariables = officialVariables || {};
        
        // If it's a custom/live-compiled formula, run domain auto-detection
        const isOfficial = this.currentId || (officialVariables && Object.keys(officialVariables).length > 0);
        if (!isOfficial && latex) {
            const detected = this.detectDomainFromLatex(latex);
            if (detected && detected !== this.activeDomain) {
                this.activeDomain = detected;
                if (this.activeDomainSelect) {
                    this.activeDomainSelect.value = detected;
                }
                console.log(`Auto-detected active domain: ${detected}`);
            }
        }

        const tokens = this.extractAllMathTokens(latex, this.officialVariables);
        
        if (tokens.length === 0) {
            this.symbolsList.innerHTML = '<div style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">No math variables, constants, or operators detected.</div>';
            if (this.modifiersSection) {
                this.modifiersSection.style.display = 'none';
            }
            return;
        }

        const dynamicOverrides = this.getDynamicOverrides(latex);
        let hasModifiers = false;

        tokens.forEach(tok => {
            const symbol = tok.symbol;
            let info = null;
            
            if (tok.type === 'modifier') {
                hasModifiers = true;
            }

            if (this.userCustomizations[symbol]) {
                info = { ...this.userCustomizations[symbol], type: tok.type, source: 'user' };
            } else if (window.SUBTOPIC_VARIABLES && window.SUBTOPIC_VARIABLES[symbol]) {
                const local = window.SUBTOPIC_VARIABLES[symbol];
                info = {
                    name: local.name || symbol,
                    type: local.type || tok.type,
                    description: local.description || 'Contextual subtopic reference.',
                    unit: local.unit || 'dimensionless',
                    ref: window.SUBTOPIC_SLUG ? 'subtopic/' + window.SUBTOPIC_SLUG : null,
                    source: 'subtopic_context'
                };
            } else if (this.officialVariables[symbol]) {
                const official = this.officialVariables[symbol];
                info = {
                    name: official.name || symbol,
                    type: official.type || tok.type,
                    description: official.description || 'Sharded variable reference.',
                    unit: official.unit || 'dimensionless',
                    ref: official.ref || null,
                    source: 'database'
                };
            } else if (tok.type === 'modifier' && this.modifierGlossary[symbol]) {
                const glossaryEntry = this.modifierGlossary[symbol];
                info = {
                    name: glossaryEntry.name,
                    type: 'modifier',
                    description: glossaryEntry.desc,
                    unit: 'modifier',
                    source: 'glossary'
                };
            } else if (/\\(int|oint|iint|iiint)/.test(symbol)) {
                info = {
                    name: 'Definite/Indefinite Integral',
                    type: tok.type,
                    description: 'Accumulates quantities over the differential range.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (/\\frac\{\\partial/.test(symbol)) {
                info = {
                    name: 'Partial Derivative',
                    type: tok.type,
                    description: 'Represents the rate of change of the numerator with respect to the denominator.',
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (/\\(dot|ddot)/.test(symbol)) {
                info = {
                    name: 'Time Derivative',
                    type: tok.type,
                    description: 'Represents the rate of change with respect to time.',
                    unit: 'dimensionless',
                    source: 'heuristic'
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
                    const dictEntry = this.physicsDictionary[symbol];
                    let activeEntry = dictEntry;
                    
                    // Check if there is an override matching the active domain
                    if (dictEntry.domain === this.activeDomain) {
                        activeEntry = dictEntry;
                    } else if (dictEntry.alternatives) {
                        const match = dictEntry.alternatives.find(alt => alt.domain === this.activeDomain);
                        if (match) {
                            activeEntry = {
                                name: match.name,
                                type: match.type || dictEntry.type,
                                unit: match.unit || dictEntry.unit,
                                desc: match.desc || dictEntry.desc,
                                alternatives: dictEntry.alternatives
                            };
                        }
                    }
                    
                    info = {
                        name: activeEntry.name,
                        type: activeEntry.type || tok.type,
                        description: activeEntry.desc || activeEntry.description,
                        unit: activeEntry.unit || 'dimensionless',
                        alternatives: dictEntry.alternatives,
                        source: 'dictionary'
                    };
                } else {
                    info = {
                        name: symbol.startsWith('\\') ? symbol.substring(1) + (tok.type === 'modifier' ? ' Modifier' : ' Parameter') : symbol + (tok.type === 'modifier' ? ' Subscript/Modifier' : ' Variable'),
                        type: tok.type,
                        description: tok.type === 'modifier' ? 'Custom modifier constraint. Click Edit to customize definition.' : 'Custom parameter. Click Edit to customize name, unit, and definition.',
                        unit: tok.type === 'modifier' ? 'modifier' : 'dimensionless',
                        source: 'fallback'
                    };
                }
            }

            this.renderVariableRow(symbol, info);
        });

        if (this.modifiersSection) {
            this.modifiersSection.style.display = hasModifiers ? 'block' : 'none';
        }

        const typesetTargets = [this.symbolsList];
        if (hasModifiers && this.modifiersList) {
            typesetTargets.push(this.modifiersList);
        }
        this.triggerTypeset(typesetTargets);
    },

    bindRowEvents(targetRow, symbol, info) {
        // Highlight on hover
        targetRow.addEventListener('mouseenter', () => {
            this.highlightSymbolInMath(symbol, true);
        });
        targetRow.addEventListener('mouseleave', () => {
            this.highlightSymbolInMath(symbol, false);
        });

        // Edit button
        const editBtn = targetRow.querySelector('.edit-var-btn');
        if (editBtn) {
            editBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleVarEditForm(targetRow, symbol, info);
            });
        }

        // Drill down click handler on badge
        const badge = targetRow.querySelector('.symbol-badge');
        if (badge) {
            badge.style.cursor = 'pointer';
            badge.addEventListener('click', (e) => {
                e.stopPropagation();
                this.drillDownIntoSymbol(symbol, info);
            });
        }

        // Drill down click handler on name
        const nameLbl = targetRow.querySelector('.var-name-lbl');
        if (nameLbl) {
            nameLbl.addEventListener('click', (e) => {
                e.stopPropagation();
                this.drillDownIntoSymbol(symbol, info);
            });
        }

        // Alternate disambiguation options
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
                EquationExplainer.triggerTypeset([targetRow]);
            });
        });
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
        } else if (info.type === 'modifier') {
            typeClass = 'modifier-type';
            badgeTypeLabel = 'Modifier';
        }

        // Wrap badge symbol in MathJax delimiters so it renders as a mathematical character
        const mathjaxSymbol = `$${symbol}$`;

        // Build name link or strong label
        let nameHtml = `<span class="var-name-lbl" style="color: var(--accent-default, #64ffda); text-decoration: none; font-size: 0.92rem; font-weight: 600; cursor: pointer; border-bottom: 1px dashed rgba(100,255,218,0.3); transition: border-color 0.2s;" onmouseover="this.style.borderColor='var(--accent-default)'" onmouseout="this.style.borderColor='rgba(100,255,218,0.3)'">${info.name}</span>`;

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
            <div class="symbol-badge ${typeClass}" title="${badgeTypeLabel}" style="cursor: pointer;">${mathjaxSymbol}</div>
            <div class="symbol-content-wrapper" style="flex: 1; display: flex; flex-direction: column;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${nameHtml}
                        <button class="edit-var-btn" style="background: transparent; border: none; color: var(--text-muted, #94a3b8); cursor: pointer; padding: 2px; display: inline-flex; align-items: center; justify-content: center; transition: color 0.2s;" title="Edit Definition">
                             <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4z"/></svg>
                        </button>
                    </div>
                    <span class="var-unit-lbl" style="font-size: 0.76rem; font-family: 'Fira Code', clock, monospace; color: #a8a29e; background: rgba(255,255,255,0.04); padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.04); ${info.unit && info.unit !== 'dimensionless' && info.unit !== 'operator' && info.unit !== 'modifier' ? '' : 'display: none;'}">${info.unit || ''}</span>
                </div>
                <div class="var-desc-lbl" style="font-size: 0.82rem; color: var(--text-muted, #94a3b8); line-height: 1.4;">${info.description || info.desc || ''}</div>
                ${disambigHtml}
            </div>
        `;

        if (existingRow) {
            const newRow = row.cloneNode(true);
            row.parentNode.replaceChild(newRow, row);
            this.bindRowEvents(newRow, symbol, info);
            return;
        }

        this.bindRowEvents(row, symbol, info);

        if (!existingRow) {
            if (info.type === 'modifier') {
                this.modifiersList.appendChild(row);
            } else {
                this.symbolsList.appendChild(row);
            }
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
            EquationExplainer.triggerTypeset([row]);
        });

        cancelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.renderVariableRow(symbol, info, row);

            // Retypeset the row
            EquationExplainer.triggerTypeset([row]);
        });

        wrapper.querySelector('.edit-var-name').focus();
    },

    extractAllMathTokens(latex, officialVariables = {}) {
        if (!latex) return [];

        const found = [];
        const seen = new Set();

        const addToken = (symbol, type) => {
            if (seen.has(symbol)) return;
            seen.add(symbol);
            found.push({ symbol, type });
        };

        // Extract subscripts as modifiers from original raw latex
        const subscriptModRegex = /_\{([^\}]+)\}|_([a-zA-Z])/g;
        let subModMatch;
        while ((subModMatch = subscriptModRegex.exec(latex)) !== null) {
            let content = subModMatch[1] || subModMatch[2];
            // Clean text/mathrm wrapping: \text{ext} -> ext
            content = content.replace(/\\(text|mathrm|mathsf|mathrm)\{([^\}]+)\}/g, '$2').trim();
            // If the cleaned content is a word of length >= 2, it's a modifier
            if (/^[a-zA-Z]{2,}$/.test(content)) {
                addToken(content, 'modifier');
            }
        }

        // Extract superscripts as modifiers from original raw latex
        const superscriptModRegex = /\^\{([^\}]+)\}|\^([a-zA-Z0-9+\-\*\\/]+|\*|\+|0|\-|\\dagger|\\circ|\\prime)/g;
        let superModMatch;
        while ((superModMatch = superscriptModRegex.exec(latex)) !== null) {
            let content = superModMatch[1] || superModMatch[2];
            content = content.trim();
            const isStandardModifier = this.modifierGlossary[content] || 
                                       content === '\'' || 
                                       content === '\\prime' ||
                                       /^(T|\top|\dagger|\circ|\*|\ast|\+|-|0)$/.test(content);
            if (isStandardModifier) {
                addToken(content, 'modifier');
            } else if (/\\(dagger|circ|prime)\b/.test(content)) {
                const cmdMatch = content.match(/\\(dagger|circ|prime)/);
                if (cmdMatch) {
                    addToken('\\' + cmdMatch[1], 'modifier');
                }
            } else if (/^[a-zA-Z]{2,}$/.test(content) && !/^[0-9]+$/.test(content)) {
                addToken(content, 'modifier');
            }
        }

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
            const isLabelWord = plainText.length >= 3 && !/\d/.test(plainText);

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

        // 2b. Pre-scan for official database keys to keep them grouped as unified terms
        if (officialVariables) {
            for (const sym of Object.keys(officialVariables)) {
                if (this.latexContainsSymbol(text, sym)) {
                    const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
                    addToken(sym, isOperator ? 'operator' : 'variable');
                    
                    // Replace matched symbol in text to avoid partial matching later
                    const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                    const regex = new RegExp(escaped, 'g');
                    text = text.replace(regex, ' ');
                }
            }
        }



        // Check for partial derivatives: \frac{\partial \Psi}{\partial t}
        const partialRegex = /\\frac\{\\partial\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)\}\{\\partial\s*([a-zA-Z\\]+)\}/g;
        let partMatch;
        while ((partMatch = partialRegex.exec(text)) !== null) {
            const fullMatch = partMatch[0];
            addToken(fullMatch, 'operator');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for dot derivatives: \dot{q} or \dot q
        const dotRegex = /\\(dot|ddot)\{([a-zA-Z\\]+)\}|\\(dot|ddot)\s*([a-zA-Z])/g;
        let dotMatch;
        while ((dotMatch = dotRegex.exec(text)) !== null) {
            const fullMatch = dotMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for subscripts: q_i or k_B
        const subscriptRegex = /([a-zA-Z\\]+)_([a-zA-Z0-9]+|\{[a-zA-Z0-9]+\})/g;
        let subMatch;
        while ((subMatch = subscriptRegex.exec(text)) !== null) {
            const fullMatch = subMatch[0];
            if (fullMatch.startsWith('\\partial') || fullMatch.startsWith('\\nabla')) continue;
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

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
                '\\frac', '\\left', '\\right', '\\cdot', '\\times', '\\div', 
                '\\iff', '\\implies', '\\ge', '\\le', '\\ast', '\\star',
                '\\boldsymbol', '\\mathbf', '\\mathsf', '\\mathrm', '\\text', '\\mathcal', 
                '\\vec', '\\hat', '\\bar', '\\tilde', '\\dot', '\\ddot', '\\underline'
            ]);
            if (structuralCmds.has(sym)) continue;
            
            const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
            addToken(sym, isOperator ? 'operator' : 'variable');
        }

        // 7. Scan for explicit mathematical operators (filtering out basic arithmetic operators)
        const standardOperators = ['\\int', '\\oint', '\\sum', '\\partial', '\\nabla', '\\Delta'];
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
        // using a cleaned LaTeX string to avoid false positives inside formatting commands
        const getCleanSearchString = (str) => {
            let clean = str;
            // 1. Replace \text{...} and \mathrm{...} environments with spaces
            clean = clean.replace(/\\(text|mathrm|mathsf)\{([^\}]+)\}/g, match => ' '.repeat(match.length));
            // 2. Replace structural/formatting commands with spaces
            const structuralRegex = /\\(frac|left|right|sqrt|cdot|times|div|iff|implies|ge|le|ast|star|boldsymbol|mathbf|mathsf|mathrm|text|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\b/g;
            clean = clean.replace(structuralRegex, match => ' '.repeat(match.length));
            // 3. Replace word-like subscripts of 3+ letters (e.g. _{ext}, _ext) with spaces
            clean = clean.replace(/_\{[a-zA-Z]{3,\}\}/g, match => ' '.repeat(match.length));
            clean = clean.replace(/_[a-zA-Z]{3,}/g, match => ' '.repeat(match.length));
            return clean;
        };

        const cleanSearch = getCleanSearchString(latex);

        found.sort((a, b) => {
            let indexA = -1;
            if (a.type === 'modifier') {
                const escaped = a.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexA = match ? match.index : latex.indexOf(a.symbol);
            } else {
                const hasStructuralA = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(a.symbol);
                indexA = hasStructuralA ? latex.indexOf(a.symbol) : cleanSearch.indexOf(a.symbol);
            }
            
            let indexB = -1;
            if (b.type === 'modifier') {
                const escaped = b.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexB = match ? match.index : latex.indexOf(b.symbol);
            } else {
                const hasStructuralB = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(b.symbol);
                indexB = hasStructuralB ? latex.indexOf(b.symbol) : cleanSearch.indexOf(b.symbol);
            }
            
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
        this.stopSandbox();
        this.stopSonification();
        
        this.explainerPlaceholder.style.display = 'flex';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'none';
        if (this.modifiersSection) this.modifiersSection.style.display = 'none';
        if (this.modifiersList) this.modifiersList.innerHTML = '';
        this.topologicalBridges.style.display = 'none';
        if (this.conceptualIntroCard) this.conceptualIntroCard.style.display = 'none';
        if (this.aiScenariosSection) this.aiScenariosSection.style.display = 'none';
        if (this.aiSimulationCard) this.aiSimulationCard.style.display = 'none';
        
        this.formulaTitle.textContent = 'Selecting Equation...';
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status badge-unregistered';
            this.formulaBadge.textContent = 'Live Analysis';
        }
        if (this.solverRedirectContainer) {
            this.solverRedirectContainer.style.display = 'none';
        }
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
            if (this.solverRedirectContainer) {
                this.solverRedirectContainer.style.display = 'block';
            }
            if (this.solverRedirectLink) {
                this.solverRedirectLink.href = `${BASE_URL}/physics/dimensional-solver?formula=` + encodeURIComponent(plainText);
            }
        } else {
            if (this.solverRedirectContainer) {
                this.solverRedirectContainer.style.display = 'none';
            }
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
    },

    renderAIScenariosSection(scenarios) {
        this.aiScenariosList.innerHTML = '';
        if (!scenarios || scenarios.length === 0) {
            this.aiScenariosSection.style.display = 'none';
            return;
        }

        this.aiScenariosSection.style.display = 'flex';
        scenarios.forEach(sc => {
            const card = document.createElement('div');
            card.className = 'ai-scenario-card';
            card.style.cssText = 'background: rgba(100, 255, 218, 0.02); border: 1px solid rgba(100, 255, 218, 0.08); border-radius: 8px; padding: 15px;';
            
            // Automatically detect and wrap parenthesized LaTeX expressions in math delimiters
            const conditionHtml = this.wrapTextMathDelimiters(sc.condition);
            const implicationHtml = this.wrapTextMathDelimiters(sc.implication);

            card.innerHTML = `
                <h4 style="font-size: 0.9rem; font-weight: 600; color: var(--accent-default, #64ffda); margin: 0 0 6px 0; font-family: 'Space Grotesk', sans-serif;">
                    ${conditionHtml}
                </h4>
                <p style="margin: 0; font-size: 0.92rem; line-height: 1.5; color: #cbd5e1;">
                    ${implicationHtml}
                </p>
            `;
            this.aiScenariosList.appendChild(card);
        });

        this.triggerTypeset([this.aiScenariosList]);
    },

    wrapTextMathDelimiters(text) {
        if (typeof text !== 'string') return text;
        
        // Protect existing math blocks by temporarily replacing them with placeholders
        const placeholders = [];
        let tempText = text;
        
        tempText = tempText.replace(/\$\$.*?\$\$/g, match => {
            placeholders.push(match);
            return `__MATH_PLACEHOLDER_${placeholders.length - 1}__`;
        });
        tempText = tempText.replace(/\$.*?\$/g, match => {
            placeholders.push(match);
            return `__MATH_PLACEHOLDER_${placeholders.length - 1}__`;
        });
        tempText = tempText.replace(/\\\(.*?\\\)/g, match => {
            placeholders.push(match);
            return `__MATH_PLACEHOLDER_${placeholders.length - 1}__`;
        });
        tempText = tempText.replace(/\\\[.*?\\\]/g, match => {
            placeholders.push(match);
            return `__MATH_PLACEHOLDER_${placeholders.length - 1}__`;
        });
        
        // Match raw math blocks composed of backslash tokens, operators, and single variables/constants
        tempText = tempText.replace(/(?:\S*\\\S+|[\+\-\*\/\=\<\>]+|\b[a-zA-Z0-9]\b)(?:\s+(?:\S*\\\S+|[\+\-\*\/\=\<\>]+|\b[a-zA-Z0-9]\b))*/g, match => {
            if (!match.includes('\\')) {
                return match; // Only wrap if it contains a LaTeX command/backslash
            }
            
            let trimmed = match.trim();
            
            // Extract trailing punctuation
            let trailingPunct = '';
            const punctMatch = trimmed.match(/[,.;:]+$/);
            if (punctMatch) {
                trailingPunct = punctMatch[0];
                trimmed = trimmed.substring(0, trimmed.length - trailingPunct.length);
            }
            
            return `\\(${trimmed}\\)${trailingPunct}`;
        });
        
        // Restore placeholders using a callback function to prevent JS replacement string gotchas
        for (let i = 0; i < placeholders.length; i++) {
            tempText = tempText.replace(`__MATH_PLACEHOLDER_${i}__`, () => placeholders[i]);
        }
        
        return tempText;
    },

    synthesizeCustomOverview(latex) {
        let intro = "This mathematical expression represents a physical relation between variables.";
        let summary = "It is used to calculate the relative dynamics of the physical system.";
        let scenarios = [];

        // 1. Detect Gauss's Law / Divergence
        if (latex.includes('\\nabla \\cdot') || latex.includes('\\text{div}')) {
            let fieldSymbol = 'E';
            const match = latex.match(/\\nabla\s*\\cdot\s*(\\mathbf\{[A-Z]\}|[A-Za-z])/);
            if (match) {
                fieldSymbol = match[1];
            }
            intro = `The mathematical statement represents the <strong>Divergence</strong> of the vector field $${fieldSymbol}$. This is a foundational relation in field theory, measuring whether a given point in space acts as a source or a sink for the field lines.`;
            summary = `It states that the net flux of the field exiting an infinitesimal volume around a point is determined by the local source density.`;
            scenarios = [
                {
                    condition: `Positive Divergence (\\( \\nabla \\cdot ${fieldSymbol} > 0 \\))`,
                    implication: "The point acts as a source. Field lines diverge outward from this region (e.g., positive charges acting as sources of electric fields)."
                },
                {
                    condition: `Negative Divergence (\\( \\nabla \\cdot ${fieldSymbol} < 0 \\))`,
                    implication: "The point acts as a sink. Field lines converge inward toward this region (e.g., negative charges acting as sinks of electric fields)."
                },
                {
                    condition: `Zero Divergence (\\( \\nabla \\cdot ${fieldSymbol} = 0 \\))`,
                    implication: "The field is solenoidal. Field lines pass through the volume continuously without starting or stopping (e.g., magnetic fields, where the absence of magnetic monopoles guarantees zero divergence)."
                }
            ];
        }
        // 2. Detect Maxwell-Faraday / Curl
        else if (latex.includes('\\nabla \\times') || latex.includes('\\text{curl}')) {
            let fieldSymbol = 'E';
            const match = latex.match(/\\nabla\s*\\times\s*(\\mathbf\{[A-Z]\}|[A-Za-z])/);
            if (match) {
                fieldSymbol = match[1];
            }
            intro = `The mathematical statement defines the <strong>Curl</strong> of the vector field $${fieldSymbol}$. This operator measures the rotational intensity, vorticity, or circulation of the field around a point.`;
            summary = `It quantifies the tendency of the vector field lines to curl or rotate around a given axis.`;
            scenarios = [
                {
                    condition: `Non-Zero Curl (\\( \\nabla \\times ${fieldSymbol} \\neq 0 \\))`,
                    implication: "The field possesses circulation or rotational eddies, indicating the presence of vortex sources (e.g., induced electric fields resulting from changing magnetic flux)."
                },
                {
                    condition: `Zero Curl (\\( \\nabla \\times ${fieldSymbol} = 0 \\))`,
                    implication: "The field is conservative or irrotational. Its line integral around any closed loop is zero, allowing it to be represented as the gradient of a scalar potential."
                }
            ];
        }
        // 3. Detect Schrödinger / Time-dependent Rate equation
        else if (latex.includes('\\partial') && latex.includes('\\partial t') || latex.includes('\\dot') || latex.includes('\\frac{d}{dt}') || latex.includes('\\ddot')) {
            intro = "This formula defines the <strong>temporal evolution</strong> (dynamics) of a physical system. It establishes how the state vector or physical quantities change with time.";
            summary = "It maps the rate of change of the system variables directly to the governing operator forces or energies.";
            scenarios = [
                {
                    condition: "Positive Time Derivative (\\( d/dt > 0 \\))",
                    implication: "The physical quantity or state magnitude is increasing or accumulating over time."
                },
                {
                    condition: "Negative Time Derivative (\\( d/dt < 0 \\))",
                    implication: "The physical quantity is decreasing, decaying, or dissipating over time."
                },
                {
                    condition: "Zero Time Derivative (\\( d/dt = 0 \\))",
                    implication: "The system is in a stationary state, steady-state configuration, or thermal equilibrium."
                }
            ];
        }
        // 4. Detect Action / Integrals
        else if (latex.includes('\\int') || latex.includes('\\oint')) {
            intro = "This formula represents an <strong>integral accumulation</strong> of physical quantities across a specific mathematical domain (boundary path, surface area, or volume space).";
            summary = "It summates local densities to calculate a global macroscopic quantity (such as total energy, mass, charge, or action).";
            scenarios = [
                {
                    condition: "Closed Loop Integration (\\( \\oint \\))",
                    implication: "Accumulates quantities along a closed path or boundary. If the result is zero, the system is conservative; if non-zero, it represents net circulation or enclosed sources."
                },
                {
                    condition: "Infinite Bounds (\\( -\\infty \\) to \\( \\infty \\))",
                    implication: "Accumulates the quantity across all space (e.g., probability normalization in quantum mechanics summing to exactly 1)."
                }
            ];
        }
        // 5. Detect Gauge Symmetries / Lie Groups (e.g. SU(3)_C x SU(2)_L x U(1)_Y)
        else if (latex.includes('SU(') || latex.includes('U(1)') || latex.includes('SO(')) {
            intro = "This formula defines the <strong>Gauge Symmetry Group</strong> governing the interactions of a field theory. Product groups of this type specify the mathematical structure of force-carrying fields and charge conservation.";
            summary = "Each factor in the symmetry group dictates a specific type of charge conservation and its corresponding gauge bosons.";
            scenarios = [];
            
            if (latex.includes('SU(3)')) {
                scenarios.push({
                    condition: "SU(3) Color Symmetry",
                    implication: "Dictates the strong nuclear force (Quantum Chromodynamics). Governs color-charged interactions mediated by 8 gluons, exhibiting confinement and asymptotic freedom."
                });
            }
            if (latex.includes('SU(2)')) {
                scenarios.push({
                    condition: "SU(2) Weak Isospin Symmetry",
                    implication: "Governs the electroweak weak isospin sector. Acts on left-handed chirality states and is mediated by 3 gauge bosons."
                });
            }
            if (latex.includes('U(1)')) {
                scenarios.push({
                    condition: "U(1) Symmetries",
                    implication: "Governs abelian phase transformations. Often represents Weak Hypercharge (U(1)_Y) in electroweak theory, or Electromagnetism (U(1)_em) mediated by a single massless boson (photon)."
                });
            }
            if (latex.includes('\\times')) {
                scenarios.push({
                    condition: "Electroweak Symmetry Breaking",
                    implication: "At low energy scales, the Higgs mechanism breaks the electroweak SU(2)_L x U(1)_Y symmetry down to electromagnetic U(1)_em, mixing gauge fields into physical W+, W-, Z bosons and the photon."
                });
            }
        } else {
            scenarios = [
                {
                    condition: "Scaling Limits (Direct Proportionality)",
                    implication: "Increasing the numerator variables results in a proportional increase in the left-hand side of the relation."
                },
                {
                    condition: "Inverse Scaling (Inverse Proportionality)",
                    implication: "Increasing the denominator variables causes the left-hand side quantity to decay."
                }
            ];
        }

        return { intro, summary, scenarios };
    },

    initSandbox(latex, variables) {
        this.stopSandbox();
        this.stopSonification();

        if (!this.sandboxCanvas) return;

        this.sandboxCtx = this.sandboxCanvas.getContext('2d');
        // this.aiSimulationCard.style.display = 'flex';

        // 1. Classify Sandbox Type
        if (latex.includes('\\nabla \\cdot') || latex.includes('\\text{div}')) {
            this.sandboxType = 'divergence';
        } else if (latex.includes('\\nabla \\times') || latex.includes('\\text{curl}')) {
            this.sandboxType = 'curl';
        } else if (latex.includes('\\partial') && latex.includes('\\partial t') || latex.includes('\\dot') || latex.includes('\\frac{d}{dt}') || latex.includes('\\ddot') || latex.includes('\\int') || latex.includes('\\oint')) {
            this.sandboxType = 'wave';
        } else {
            this.sandboxType = 'scaling';
        }

        // 2. Extract active variables
        const tokens = this.extractAllMathTokens(latex, variables);
        const vars = tokens.filter(t => t.type === 'variable');

        // Reset parameters
        this.sandboxParams = {};
        this.sandboxSliders.innerHTML = '';

        // Default parameters based on type
        if (this.sandboxType === 'divergence') {
            this.sandboxParams['strength'] = 5; // Divergence value (-10 to 10)
            this.createSlider('strength', 'Field Strength / Charge (ρ)', 'dimensionless', -10, 10, 5, 0.5);
        } else if (this.sandboxType === 'curl') {
            this.sandboxParams['vorticity'] = 5; // Rotational velocity (-10 to 10)
            this.createSlider('vorticity', 'Vorticity / Circulation (Γ)', 'rad/s', -10, 10, 5, 0.5);
        } else if (this.sandboxType === 'wave') {
            this.sandboxParams['frequency'] = 5;
            this.sandboxParams['amplitude'] = 4;
            this.createSlider('frequency', 'Angular Frequency (ω)', 'Hz', 1, 15, 5, 0.2);
            this.createSlider('amplitude', 'Wave Amplitude (A)', 'dimensionless', 1, 8, 4, 0.2);
        } else {
            // General scaling parameters
            this.sandboxParams['input'] = 5;
            this.createSlider('input', 'Control Input Variable', 'dimensionless', 0, 10, 5, 0.1);
        }

        // 3. Start render loop
        this.startSandboxLoop();
    },

    createSlider(name, label, unit, min, max, val, step) {
        this.sandboxParams[name] = val;

        const sliderWrapper = document.createElement('div');
        sliderWrapper.style.cssText = 'display: flex; flex-direction: column; gap: 4px;';

        const labelRow = document.createElement('div');
        labelRow.style.cssText = 'display: flex; justify-content: space-between; font-size: 0.82rem; color: #cbd5e1;';
        
        const labelText = document.createElement('span');
        labelText.textContent = label;

        const valText = document.createElement('span');
        valText.style.cssText = 'font-weight: 600; color: var(--accent-default, #64ffda); font-family: "Fira Code", monospace;';
        valText.textContent = `${val} ${unit !== 'dimensionless' ? unit : ''}`;

        labelRow.appendChild(labelText);
        labelRow.appendChild(valText);

        const input = document.createElement('input');
        input.type = 'range';
        input.min = min;
        input.max = max;
        input.value = val;
        input.step = step;
        input.style.cssText = 'width: 100%; height: 4px; border-radius: 2px; background: rgba(255, 255, 255, 0.1); outline: none; cursor: pointer; accent-color: var(--accent-default, #64ffda);';

        input.addEventListener('input', (e) => {
            const numVal = parseFloat(e.target.value);
            this.sandboxParams[name] = numVal;
            valText.textContent = `${numVal} ${unit !== 'dimensionless' ? unit : ''}`;
            this.updateSonificationParameters();
        });

        sliderWrapper.appendChild(labelRow);
        sliderWrapper.appendChild(input);
        this.sandboxSliders.appendChild(sliderWrapper);
    },

    stopSandbox() {
        if (this.sandboxAnimationId) {
            cancelAnimationFrame(this.sandboxAnimationId);
            this.sandboxAnimationId = null;
        }
    },

    startSandboxLoop() {
        const fps = 60;
        let time = 0;

        const render = () => {
            if (!this.sandboxCanvas || !this.sandboxCtx) return;

            const w = this.sandboxCanvas.width;
            const h = this.sandboxCanvas.height;
            const ctx = this.sandboxCtx;

            ctx.clearRect(0, 0, w, h);

            // Draw base grid
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
            ctx.lineWidth = 1;
            const step = 20;
            for (let x = 0; x < w; x += step) {
                ctx.beginPath();
                ctx.moveTo(x, 0);
                ctx.lineTo(x, h);
                ctx.stroke();
            }
            for (let y = 0; y < h; y += step) {
                ctx.beginPath();
                ctx.moveTo(0, y);
                ctx.lineTo(w, y);
                ctx.stroke();
            }

            // Draw active animation
            time += 0.05;
            if (this.sandboxType === 'divergence') {
                this.drawDivergence(ctx, w, h, time, this.sandboxParams['strength']);
            } else if (this.sandboxType === 'curl') {
                this.drawCurl(ctx, w, h, time, this.sandboxParams['vorticity']);
            } else if (this.sandboxType === 'wave') {
                this.drawWave(ctx, w, h, time, this.sandboxParams['frequency'], this.sandboxParams['amplitude']);
            } else {
                this.drawScaling(ctx, w, h, time, this.sandboxParams['input']);
            }

            this.sandboxAnimationId = requestAnimationFrame(render);
        };

        render();
    },

    drawDivergence(ctx, w, h, t, strength) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw central source/sink node
        ctx.beginPath();
        ctx.arc(cx, cy, 6, 0, Math.PI * 2);
        ctx.fillStyle = strength > 0 ? '#10b981' : (strength < 0 ? '#f43f5e' : 'rgba(255, 255, 255, 0.2)');
        ctx.fill();

        // Particle stream lines
        const numStreams = 12;
        for (let i = 0; i < numStreams; i++) {
            const angle = (i * Math.PI * 2) / numStreams;
            const cos = Math.cos(angle);
            const sin = Math.sin(angle);

            ctx.strokeStyle = strength > 0 ? 'rgba(16, 185, 129, 0.12)' : (strength < 0 ? 'rgba(244, 63, 94, 0.12)' : 'rgba(255, 255, 255, 0.06)');
            ctx.lineWidth = 1.5;
            ctx.beginPath();
            ctx.moveTo(cx, cy);
            ctx.lineTo(cx + cos * 150, cy + sin * 150);
            ctx.stroke();

            // Animate moving flow dots
            if (strength !== 0) {
                const speed = Math.abs(strength) * 0.4;
                const offset = (t * speed) % 150;
                const distance = strength > 0 ? offset : (150 - offset);
                
                ctx.beginPath();
                ctx.arc(cx + cos * distance, cy + sin * distance, 3, 0, Math.PI * 2);
                ctx.fillStyle = strength > 0 ? 'var(--accent-default, #64ffda)' : '#f43f5e';
                ctx.fill();
            }
        }
    },

    drawCurl(ctx, w, h, t, vorticity) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw center rotation core
        ctx.beginPath();
        ctx.arc(cx, cy, 8, 0, Math.PI * 2);
        ctx.fillStyle = vorticity !== 0 ? 'var(--accent-default, #64ffda)' : 'rgba(255, 255, 255, 0.2)';
        ctx.fill();

        // Draw rotating circles
        const rings = [35, 65, 95];
        rings.forEach((r, idx) => {
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.arc(cx, cy, r, 0, Math.PI * 2);
            ctx.stroke();

            // Rotating flow node
            if (vorticity !== 0) {
                const dir = vorticity > 0 ? 1 : -1;
                const speed = Math.abs(vorticity) * 0.08 / (idx + 1);
                const angle = t * speed * dir + (idx * Math.PI / 1.5);
                
                const px = cx + Math.cos(angle) * r;
                const py = cy + Math.sin(angle) * r;
                
                ctx.beginPath();
                ctx.arc(px, py, 3.5, 0, Math.PI * 2);
                ctx.fillStyle = vorticity > 0 ? 'var(--accent-default, #64ffda)' : '#a78bfa';
                ctx.fill();
            }
        });
    },

    drawWave(ctx, w, h, t, freq, amp) {
        ctx.strokeStyle = 'var(--accent-default, #64ffda)';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = 'rgba(100, 255, 218, 0.4)';
        ctx.shadowBlur = 10;
        
        ctx.beginPath();
        for (let x = 0; x < w; x++) {
            // y = Amplitude * sin(k * x - omega * t)
            const k = 0.04;
            const omega = freq * 0.05;
            const y = h / 2 + (amp * 10) * Math.sin(k * x - omega * t);
            
            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }
        ctx.stroke();
        
        ctx.shadowBlur = 0; // Reset shadow
    },

    drawScaling(ctx, w, h, t, input) {
        const cx = w / 2;
        const cy = h / 2;

        // Draw Slope Line
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(20, h - 20);
        ctx.lineTo(w - 20, 20);
        ctx.stroke();

        // Draw active slider position dot
        const startX = 40;
        const endX = w - 40;
        const startY = h - 30;
        const endY = 30;

        const currentX = startX + (endX - startX) * (input / 10);
        const currentY = startY + (endY - startY) * (input / 10);

        ctx.beginPath();
        ctx.arc(currentX, currentY, 6, 0, Math.PI * 2);
        ctx.fillStyle = '#ffd700';
        ctx.shadowColor = 'rgba(255, 215, 0, 0.4)';
        ctx.shadowBlur = 8;
        ctx.fill();
        ctx.shadowBlur = 0;
    },

    toggleSonification() {
        if (this.isSonifying) {
            this.stopSonification();
        } else {
            this.startSonification();
        }
    },

    startSonification() {
        try {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            this.audioCtx = new AudioContextClass();
            
            this.audioOscillator = this.audioCtx.createOscillator();
            this.audioGain = this.audioCtx.createGain();

            this.audioOscillator.type = 'sine';
            
            // Connect nodes
            this.audioOscillator.connect(this.audioGain);
            this.audioGain.connect(this.audioCtx.destination);
            
            this.audioOscillator.start();
            this.isSonifying = true;

            // Set button state
            this.sonifyToggleBtn.innerHTML = `
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/></svg>
                Stop Audio
            `;
            this.sonifyToggleBtn.style.background = 'rgba(244, 63, 94, 0.1)';
            this.sonifyToggleBtn.style.color = '#f43f5e';
            this.sonifyToggleBtn.style.borderColor = 'rgba(244, 63, 94, 0.3)';

            this.updateSonificationParameters();
        } catch (e) {
            console.warn('Audio Context failed to initialize:', e);
        }
    },

    stopSonification() {
        if (this.audioOscillator) {
            try {
                this.audioOscillator.stop();
            } catch (err) {}
            this.audioOscillator.disconnect();
            this.audioOscillator = null;
        }
        if (this.audioGain) {
            this.audioGain.disconnect();
            this.audioGain = null;
        }
        if (this.audioCtx) {
            this.audioCtx.close();
            this.audioCtx = null;
        }
        
        this.isSonifying = false;
        
        // Reset button state
        this.sonifyToggleBtn.innerHTML = `
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
            Sonify Math
        `;
        this.sonifyToggleBtn.style.background = 'rgba(100, 255, 218, 0.05)';
        this.sonifyToggleBtn.style.color = 'var(--accent-default, #64ffda)';
        this.sonifyToggleBtn.style.borderColor = 'rgba(100, 255, 218, 0.2)';
    },

    updateSonificationParameters() {
        if (!this.isSonifying || !this.audioOscillator || !this.audioGain) return;

        let baseFrequency = 300; // Default central pitch (Hz)
        let gainVal = 0.15;      // Default volume

        if (this.sandboxType === 'divergence') {
            const strength = this.sandboxParams['strength'] || 0;
            baseFrequency = 300 + (strength * 20); // Pitch maps to source/sink intensity
            gainVal = 0.05 + (Math.abs(strength) * 0.02);
        } else if (this.sandboxType === 'curl') {
            const vorticity = this.sandboxParams['vorticity'] || 0;
            baseFrequency = 350 + (vorticity * 15);
            gainVal = 0.05 + (Math.abs(vorticity) * 0.02);
        } else if (this.sandboxType === 'wave') {
            const freq = this.sandboxParams['frequency'] || 5;
            const amp = this.sandboxParams['amplitude'] || 4;
            baseFrequency = 200 + (freq * 30); // Pitch maps to angular frequency
            gainVal = 0.02 + (amp * 0.03);      // Volume maps to wave amplitude
        } else {
            const input = this.sandboxParams['input'] || 5;
            baseFrequency = 250 + (input * 40);
        }

        // Apply parameter slides smoothly
        const t = this.audioCtx.currentTime;
        this.audioOscillator.frequency.setTargetAtTime(baseFrequency, t, 0.05);
        this.audioGain.gain.setTargetAtTime(gainVal, t, 0.05);
    }
};

// Start initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => EquationExplainer.init());
} else {
    EquationExplainer.init();
}
