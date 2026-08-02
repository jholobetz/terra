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
    activeBinder: null,

    fallbackBinders: [
        {
            signature: 'electrostatic_field_energy',
            // Matches electrostatic field energy equations, e.g., W = \frac{\epsilon_0}{2} \int_V | \mathbf{E} |^2 d\tau or similar variants
            matchPattern: /\\int_?(\{?V\}?)?.*E.*\^2.*d\\tau|\\int_?(\{?V\}?)?.*\\mathbf\{E\}.*\^2.*d\\tau|u_E/,
            name: 'Electrostatic Field Energy',
            domain: 'electromagnetism',
            variableOverrides: {
                'W': { name: 'Electrostatic Energy', unit: 'J', desc: 'The potential energy stored in the electric field of a distribution of charges.' },
                'u_E': { name: 'Electric Field Energy Density', unit: 'J/m³', desc: 'The energy stored per unit volume in the electric field.' },
                'E': { name: 'Electric Field Strength', unit: 'V/m', desc: 'The magnitude of the electric field vector.' },
                '\\tau': { name: 'Infinitesimal Volume Element', unit: 'm³', desc: 'An infinitesimal region of space over which the volume integration is performed.' }
            }
        },
        {
            signature: 'general_relativity_geodesic',
            // Matches geodesic equations, e.g., \frac{d^2 x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta} U^\alpha U^\beta = 0
            matchPattern: /\\frac\{d\^?2\s*[a-zA-Z]+\^?\{?\\mu\}\?\}\{d\\tau\^?2\}|\\Gamma\^?\\mu_\{?\\alpha\\beta\}\?/,
            name: 'Geodesic Equation',
            domain: 'quantum_mechanics', // (relativistic physics domain is mapped here)
            variableOverrides: {
                '\\tau': { name: 'Proper Time', unit: 's', desc: 'The time interval elapsed on a clock carried along the worldline of the particle.' },
                's': { name: 'Spacetime Interval', unit: 'm', desc: 'The invariant distance between two events in spacetime.' }
            }
        }
    ],

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
            description: 'The total conserved energy of a system, encompassing kinetic, potential, and internal forms.',
            contexts: {
                'classical_mechanics': {
                    name: 'Total Energy',
                    unit: 'J',
                    description: 'The total mechanical energy of a system, equal to kinetic plus potential energy.'
                },
                'electromagnetism': {
                    name: 'Electric Field Strength',
                    unit: 'V/m or N/C',
                    description: 'The magnitude of the electric field vector, representing the force per unit charge at a point in space.'
                },
                'thermodynamics': {
                    name: 'Internal Energy',
                    unit: 'J',
                    description: 'The total microscopic energy of a thermodynamic system, including kinetic and potential energies of its particles.'
                }
            },
            featuredEquations: [
                { name: "Mass-Energy Equivalence", latex: "E = m c^2" }
            ]
        },
        'W': {
            name: 'Work Done / Electrostatic Energy',
            defaultUnit: 'J',
            description: 'Work done on a system, or potential energy stored within a system depending on context.',
            contexts: {
                'classical_mechanics': {
                    name: 'Work Done',
                    unit: 'J',
                    description: 'The energy transferred to or from an object via the application of force along a displacement.'
                },
                'electromagnetism': {
                    name: 'Electrostatic Energy',
                    unit: 'J',
                    description: 'The potential energy stored in the electric field of a distribution of charges, or the total work required to assemble the charges.'
                }
            },
            featuredEquations: []
        },
        'V': {
            name: 'Volume / Electric Potential',
            defaultUnit: 'm³ or V',
            description: 'The amount of three-dimensional space enclosed, or electrostatic voltage.',
            contexts: {
                'classical_mechanics': {
                    name: 'Volume',
                    unit: 'm³',
                    description: 'The amount of three-dimensional space enclosed by a closed surface or boundary.'
                },
                'thermodynamics': {
                    name: 'Volume',
                    unit: 'm³',
                    description: 'The volume occupied by a thermodynamic system, acting as an extensive state variable.'
                },
                'electromagnetism': {
                    name: 'Electric Potential',
                    unit: 'V',
                    description: 'The amount of work energy needed to move a unit of electric charge from a reference point to a specific point in an electric field.'
                }
            },
            featuredEquations: []
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
                },
                'electromagnetism': {
                    name: 'Infinitesimal Volume Element',
                    unit: 'm³',
                    description: 'An infinitesimal region of space over which a volume integration is performed.'
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
        'B': { name: 'Boltzmann Subscript', desc: 'Indicates the quantity is scaled or associated with Ludwig Boltzmann.' },
        'e': { name: 'Electron Subscript', desc: 'Indicates properties associated with an electron (e.g. m_e).' },
        'p': { name: 'Planck / Proton Subscript', desc: 'Indicates a quantity evaluated at the Planck scale, or associated with a proton (e.g. l_p, m_p).' },
        
        // Summation and Spacetime Indices
        'i': { name: 'Summation Index', desc: 'A subscript index used to enumerate particles, states, or components (e.g. r_i).' },
        'j': { name: 'Summation Index', desc: 'A subscript index used to enumerate particles, states, or components.' },
        'k': { name: 'Summation Index / State Index', desc: 'A subscript index used to enumerate states, particles, or wave vector components.' },
        'l': { name: 'Summation Index', desc: 'A subscript index used to enumerate particles, states, or components.' },
        'm': { name: 'Summation Index', desc: 'A subscript index used to enumerate components or particles.' },
        'n': { name: 'Summation Index / State Index', desc: 'A subscript index representing state number or particle count.' },
        '\\alpha': { name: 'Spacetime Index / Tensor Index', desc: 'A coordinate index in tensor calculus representing dimensions (e.g., 0 to 3 in spacetime).' },
        '\\beta': { name: 'Spacetime Index / Tensor Index', desc: 'A coordinate index in tensor calculus representing dimensions (e.g., 0 to 3 in spacetime).' },
        '\\gamma': { name: 'Spacetime Index / Tensor Index', desc: 'A coordinate index in tensor calculus representing dimensions (e.g., 0 to 3 in spacetime).' },
        '\\delta': { name: 'Spacetime Index / Tensor Index', desc: 'A coordinate index in tensor calculus representing dimensions (e.g., 0 to 3 in spacetime).' },
        '\\mu': { name: 'Lorentz Index / Spacetime Index', desc: 'A coordinate index in relativity representing dimensions 0, 1, 2, 3 in spacetime.' },
        '\\nu': { name: 'Lorentz Index / Spacetime Index', desc: 'A coordinate index in relativity representing dimensions 0, 1, 2, 3 in spacetime.' },
        
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
        'a': {
            name: 'Acceleration',
            type: 'variable',
            unit: 'm/s²',
            desc: 'The rate of change of velocity of an object with respect to time.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Gauge Index / Color Index', type: 'modifier', unit: 'modifier', desc: 'An index labeling the generators of a gauge group (e.g. 1 to 8 for SU(3) color space).', domain: 'quantum_mechanics' }
            ]
        },
        'b': { name: 'Impact Parameter / Constant', type: 'variable', unit: 'm', desc: 'Perpendicular distance between the path of a projectile and the center of a potential field.' },
        'c': { name: 'Speed of Light', type: 'constant', unit: 'm/s', desc: 'The maximum speed at which all conventional matter and information in the universe can travel.' },
        'd': {
            name: 'Total Differential',
            type: 'operator',
            unit: 'operator',
            desc: 'Represents an infinitesimal change in a variable (e.g. dx, dt).',
            domain: 'calculus',
            alternatives: [
                { name: 'Distance', type: 'variable', unit: 'm', desc: 'The physical space or separation between two points or objects.', domain: 'classical_mechanics' }
            ]
        },
        'e': { name: 'Elementary Charge / Euler\'s Number', type: 'constant', unit: 'C', desc: 'The electric charge carried by a single proton, or the mathematical base of natural logarithms.' },
        'f': { name: 'Frequency', type: 'variable', unit: 'Hz', desc: 'The number of occurrences of a repeating event per unit of time.' },
        'g': {
            name: 'Gravitational Acceleration',
            type: 'constant',
            unit: 'm/s²',
            desc: 'The local acceleration imparted to objects due to gravity (approx. 9.81 m/s² on Earth).',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Gauge Coupling Constant', type: 'variable', unit: 'dimensionless', desc: 'A parameter determining the strength of a gauge interaction (e.g. strong, weak, or electromagnetic coupling).', domain: 'quantum_mechanics' }
            ]
        },
        'h': { name: 'Planck Constant', type: 'constant', unit: 'J·s', desc: 'The quantum of electromagnetic action relating photon energy to frequency.' },
        'i': {
            name: 'Summation Index',
            type: 'modifier',
            unit: 'dimensionless',
            desc: 'A subscript index used to enumerate particles, states, or components (e.g. r_i).',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Imaginary Unit', type: 'constant', unit: 'dimensionless', desc: 'The mathematical constant defined by the property i² = -1.', domain: 'quantum_mechanics' },
                { name: 'Imaginary Unit', type: 'constant', unit: 'dimensionless', desc: 'The mathematical constant defined by the property i² = -1 (sometimes written as j).', domain: 'electromagnetism' }
            ]
        },
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
        'p': {
            name: 'Linear Momentum',
            type: 'variable',
            unit: 'kg·m/s',
            desc: 'The product of the mass and velocity of a body, representing its quantity of motion.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Pressure', type: 'variable', unit: 'Pa', desc: 'The perpendicular force applied per unit area on a boundary.', domain: 'thermodynamics' },
                { name: 'Electric Dipole Moment', type: 'variable', unit: 'C·m', desc: 'A measure of the separation of positive and negative electrical charges in a system.', domain: 'electromagnetism' }
            ]
        },
        'q': { name: 'Electric Charge', type: 'variable', unit: 'C', desc: 'A physical property of matter that causes it to experience a force when placed in an electromagnetic field.' },
        'r': {
            name: 'Position Coordinate',
            type: 'variable',
            unit: 'm',
            desc: 'The coordinate representing spatial position or radial distance of a particle.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Position Vector Magnitude', type: 'variable', unit: 'm', desc: 'The magnitude of the position vector from an origin.', domain: 'quantum_mechanics' },
                { name: 'Radial Distance', type: 'variable', unit: 'm', desc: 'The distance from a central source or line charge.', domain: 'electromagnetism' }
            ]
        },
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
        'B': {
            name: 'Magnetic Field Strength',
            type: 'variable',
            unit: 'T',
            desc: 'The magnetic flux density representing electromagnetic field induction.',
            domain: 'electromagnetism',
            alternatives: [
                { name: 'B Boson Field', type: 'variable', unit: 'varies', desc: 'The gauge field representing the U(1) weak hypercharge gauge boson.', domain: 'quantum_mechanics' },
                { name: 'Creation Operator', type: 'operator', unit: 'operator', desc: 'An operator that adds a particle to a quantum state.', domain: 'quantum_mechanics' }
            ]
        },
        'C': { name: 'Capacitance / Heat Capacity', type: 'variable', unit: 'F or J/K', desc: 'The ability of a body to store electrical charge, or thermal energy needed to change temperature.' },
        'D': {
            name: 'Electric Displacement Field',
            type: 'variable',
            unit: 'C/m²',
            desc: 'The displacement flux density representing electric charge polarization in media.',
            domain: 'electromagnetism',
            alternatives: [
                { name: 'Gauge Covariant Derivative', type: 'operator', unit: 'operator', desc: 'A generalization of the derivative that preserves gauge invariance in field theories.', domain: 'quantum_mechanics' }
            ]
        },
        'E': {
            name: 'Total Energy',
            type: 'variable',
            unit: 'J',
            desc: 'The total kinetic and potential capacity of a physical system.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Electric Field Strength', type: 'variable', unit: 'V/m', desc: 'The force per unit charge exerted on a test charge in an electric field.', domain: 'electromagnetism' },
                { name: 'Total Energy', type: 'variable', unit: 'J', desc: 'The energy eigenvalue or total energy of a quantum state.', domain: 'quantum_mechanics' }
            ]
        },
        'F': {
            name: 'Force',
            type: 'variable',
            unit: 'N',
            desc: 'An interaction that causes an object to undergo a change in velocity.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Helmholtz Free Energy', type: 'variable', unit: 'J', desc: 'A thermodynamic potential that measures the useful work obtainable from a closed thermodynamic system.', domain: 'thermodynamics' }
            ]
        },
        'G': {
            name: 'Gravitational Constant',
            type: 'constant',
            unit: 'm³/(kg·s²)',
            desc: 'Empirical physical constant in Newton\'s law of universal gravitation.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Gibbs Free Energy', type: 'variable', unit: 'J', desc: 'A thermodynamic potential that measures the maximum reversible work that may be performed by a thermodynamic system at constant temperature and pressure.', domain: 'thermodynamics' },
                { name: 'Gluon Field / Einstein Tensor', type: 'variable', unit: 'varies', desc: 'The gauge field representing gluons (strong force carrier), or the Einstein curvature tensor in relativity.', domain: 'quantum_mechanics' }
            ]
        },
        'H': {
            name: 'Hamiltonian',
            type: 'operator',
            unit: 'J',
            desc: 'The operator or function representing the total energy of a physical system.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Enthalpy', type: 'variable', unit: 'J', desc: 'A thermodynamic quantity equivalent to the total heat content of a system.', domain: 'thermodynamics' },
                { name: 'Hamiltonian', type: 'operator', unit: 'J', desc: 'The operator representing the total energy of a quantum system.', domain: 'quantum_mechanics' },
                { name: 'Magnetic Field Strength', type: 'variable', unit: 'A/m', desc: 'The auxiliary magnetic field vector representing magnetization effects in media.', domain: 'electromagnetism' }
            ]
        },
        '\\mathcal{H}': {
            name: 'Hamiltonian Density',
            type: 'variable',
            unit: 'J/m³',
            desc: 'The Hamiltonian per unit volume in field theories.',
            domain: 'quantum_mechanics'
        },
        'I': { name: 'Electric Current / Moment of Inertia', type: 'variable', unit: 'A or kg·m²', desc: 'The rate of flow of electric charge, or resistance to rotational acceleration.' },
        'J': { name: 'Angular Momentum / Current Density', type: 'variable', unit: 'kg·m²/s or A/m²', desc: 'Rotational momentum vector, or flow of electric charge per unit area.' },
        'K': { name: 'Kinetic Energy / Bulk Modulus', type: 'variable', unit: 'J or Pa', desc: 'Energy possessed by an object due to its motion, or resistance to uniform compression.' },
        'L': {
            name: 'Angular Momentum',
            type: 'variable',
            unit: 'kg·m²/s',
            desc: 'The rotational analog of linear momentum, representing the quantity of rotation.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Self-Inductance', type: 'variable', unit: 'H', desc: 'The property of a conductor by which a change in current induces an electromotive force.', domain: 'electromagnetism' },
                { name: 'Luminosity', type: 'variable', unit: 'W', desc: 'The total radiant power emitted by a star, galaxy, or other astronomical object.', domain: 'optics' },
                { name: 'Luminosity', type: 'variable', unit: 'W', desc: 'The total radiant power emitted by an object.', domain: 'thermodynamics' }
            ]
        },
        '\\mathcal{L}': {
            name: 'Lagrangian',
            type: 'variable',
            unit: 'J',
            desc: 'A function describing the state of a dynamic system, equal to kinetic energy minus potential energy (L = T - V).',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Lagrangian Density', type: 'variable', unit: 'J/m³', desc: 'The Lagrangian per unit volume in field theories.', domain: 'quantum_mechanics' }
            ]
        },
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
        'Q': {
            name: 'Total Charge',
            type: 'variable',
            unit: 'C',
            desc: 'The net electrical charge of a system.',
            domain: 'electromagnetism',
            alternatives: [
                { name: 'Heat', type: 'variable', unit: 'J', desc: 'Thermal energy transferred between systems due to a temperature difference.', domain: 'thermodynamics' },
                { name: 'Generalized Coordinate', type: 'variable', unit: 'varies', desc: 'Generalized coordinates in analytical mechanics.', domain: 'classical_mechanics' }
            ]
        },
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
        'U': {
            name: 'Potential Energy',
            type: 'variable',
            unit: 'J',
            desc: 'Position-dependent stored energy of a system.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Internal Energy', type: 'variable', unit: 'J', desc: 'The total of the kinetic and potential energy of all particles stored within a thermodynamic system.', domain: 'thermodynamics' }
            ]
        },

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
        '\\alpha': {
            name: 'Fine-structure Constant',
            type: 'constant',
            unit: 'dimensionless',
            desc: 'The fine-structure constant, measuring the strength of the electromagnetic interaction.',
            domain: 'electromagnetism',
            alternatives: [
                { name: 'Angular Acceleration', type: 'variable', unit: 'rad/s²', desc: 'The rate of change of angular velocity over time.', domain: 'classical_mechanics' },
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' }
            ]
        },
        '\\beta': {
            name: 'Phase Constant',
            type: 'variable',
            unit: 'rad/m',
            desc: 'The phase shift per unit distance of a wave propagating along a path.',
            domain: 'optics',
            alternatives: [
                { name: 'Relativistic Beta', type: 'variable', unit: 'dimensionless', desc: 'Velocity as a fraction of the speed of light (v/c).', domain: 'classical_mechanics' },
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' }
            ]
        },
        '\\gamma': {
            name: 'Lorentz Factor',
            type: 'variable',
            unit: 'dimensionless',
            desc: 'The relativistic scale factor describing time dilation and length contraction.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Surface Tension', type: 'variable', unit: 'N/m', desc: 'The elastic-like force per unit length on a liquid interface.', domain: 'classical_mechanics' },
                { name: 'Gamma Ray / High-Energy Photon', type: 'variable', unit: 'dimensionless', desc: 'High-energy electromagnetic radiation or quantum photon mode.', domain: 'optics' },
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' }
            ]
        },
        '\\delta': {
            name: 'Small Increment',
            type: 'variable',
            unit: 'dimensionless',
            desc: 'A small change or variation in a physical quantity.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Dirac Delta Distribution', type: 'operator', unit: 'dimensionless', desc: 'A generalized function representing an idealized point source or impulse.', domain: 'quantum_mechanics' },
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' }
            ]
        },
        '\\epsilon': { name: 'Permittivity / Emissivity', type: 'variable', unit: 'F/m or dimensionless', desc: 'The measure of a medium\'s resistance to an electric field.' },
        '\\zeta': { name: 'Riemann Zeta Function / Damping Ratio', type: 'variable', unit: 'dimensionless', desc: 'A complex analytical function, or rate at which oscillations decay.' },
        '\\eta': { name: 'Efficiency / Viscosity / Minkowski Metric', type: 'variable', unit: 'dimensionless or Pa·s', desc: 'Ratio of useful work output to input energy, fluid shear resistance, or flat spacetime metric.' },
        '\\theta': { name: 'Angle Coordinate / Polar Angle', type: 'variable', unit: 'rad', desc: 'The angle displacement, or polar coordinate angle in spherical geometry.' },
        '\\iota': { name: 'Unit Vector Index', type: 'variable', unit: 'dimensionless', desc: 'A general vector component index.' },
        '\\kappa': { name: 'Curvature / Thermal Conductivity', type: 'variable', unit: 'm⁻¹ or W/(m·K)', desc: 'The rate of deviation from a straight line, or heat transmission coefficient.' },
        '\\lambda': { name: 'Wavelength / Linear Density', type: 'variable', unit: 'm or kg/m', desc: 'The distance between consecutive identical crests of a wave, or mass per unit length.' },
        '\\mu': {
            name: 'Reduced Mass / Permeability / Friction Coefficient',
            type: 'variable',
            unit: 'kg or H/m or dimensionless',
            desc: 'Effective inertial mass in two-body problems, magnetic field capability, or surface grip factor.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' }
            ]
        },
        '\\nu': {
            name: 'Kinematic Viscosity',
            type: 'variable',
            unit: 'm²/s',
            desc: 'The ratio of dynamic viscosity to density, representing a fluid\'s resistance to shear flow under gravity.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Lorentz Index / Spacetime Index', type: 'modifier', unit: 'modifier', desc: 'A coordinate index in Minkowski space representing components of a four-vector (taking values 0, 1, 2, 3).', domain: 'quantum_mechanics' },
                { name: 'Frequency', type: 'variable', unit: 'Hz', desc: 'The number of wave cycles passing a reference point per unit time.', domain: 'optics' },
                { name: 'Frequency', type: 'variable', unit: 'Hz', desc: 'The frequency of thermal radiation modes or oscillator states.', domain: 'thermodynamics' }
            ]
        },
        '\\xi': { name: 'Dimensionless Variable / Partition Function', type: 'variable', unit: 'dimensionless', desc: 'General scaled displacement, or grand canonical partition function.' },
        '\\pi': { name: 'Pi constant', type: 'constant', unit: 'dimensionless', desc: 'The ratio of a circle\'s circumference to its diameter (approx. 3.14159).' },
        '\\rho': {
            name: 'Mass Density',
            type: 'variable',
            unit: 'kg/m³',
            desc: 'The mass per unit volume of a substance.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Charge Density', type: 'variable', unit: 'C/m³', desc: 'The quantity of electric charge per unit volume.', domain: 'electromagnetism' },
                { name: 'Resistivity', type: 'variable', unit: 'Ω·m', desc: 'A measure of how strongly a material opposes the flow of electric current.', domain: 'electromagnetism' },
                { name: 'Probability Density', type: 'variable', unit: 'varies', desc: 'The probability density function in phase space or state space.', domain: 'thermodynamics' }
            ]
        },
        '\\sigma': { name: 'Stefan-Boltzmann Constant / Surface Density / Spin Operator', type: 'constant', unit: 'W/(m²·K⁴) or C/m² or operator', desc: 'Blackbody radiation rate constant, charge per unit area, or quantum spin matrices.' },
        '\\tau': {
            name: 'Torque / Proper Time / Shear Stress',
            type: 'variable',
            unit: 'N·m or s or Pa',
            desc: 'Rotational force, relativistic invariant proper duration, or sliding drag force.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Infinitesimal Volume Element', type: 'variable', unit: 'm³', desc: 'An infinitesimal region of space over which a volume integration is performed.', domain: 'electromagnetism' },
                { name: 'Pauli Matrices / SU(2) Generator', type: 'operator', unit: 'dimensionless', desc: 'Generators of the SU(2) weak isospin gauge group (Pauli spin matrices).', domain: 'quantum_mechanics' }
            ]
        },
        '\\upsilon': { name: 'Upsilon Meson', type: 'variable', unit: 'dimensionless', desc: 'A bottom-antibottom quark state.' },
        '\\phi': {
            name: 'Azimuth Angle / Scalar Potential',
            type: 'variable',
            unit: 'rad or V',
            desc: 'The horizontal coordinate angle, or electrostatic scalar potential.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Scalar Field', type: 'variable', unit: 'varies', desc: 'A scalar field representing spin-0 particles (such as the Higgs boson or pions) in quantum field theory.', domain: 'quantum_mechanics' }
            ]
        },
        '\\chi': { name: 'Magnetic or Electric Susceptibility', type: 'variable', unit: 'dimensionless', desc: 'The degree of polarization or magnetization in response to an applied field.' },
        '\\psi': { name: 'Quantum Wavefunction', type: 'variable', unit: 'dimensionless', desc: 'The complex probability amplitude vector representing a quantum state.' },
        '\\omega': { name: 'Angular Frequency / Velocity', type: 'variable', unit: 'rad/s', desc: 'Phase progression rate, or speed of rotation.' },

        // Uppercase Greek Letters
        '\\Gamma': {
            name: 'Circulation',
            type: 'variable',
            unit: 'm²/s',
            desc: 'The line integral of fluid velocity around a closed curve, measuring local rotation.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Christoffel Symbol / Affine Connection', type: 'variable', unit: 'dimensionless', desc: 'Represents gravitational force components and spacetime curvature in general relativity.', domain: 'quantum_mechanics' },
                { name: 'Gamma Function', type: 'variable', unit: 'dimensionless', desc: 'A mathematical function that extends the concept of factorials to real and complex numbers.', domain: 'thermodynamics' }
            ]
        },
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

    resolveSymbolInfo(symbol, type = null) {
        let cleanSymbol = symbol.trim().replace(/^\\(mathbf|vec|hat|bar|dot|ddot|tilde|boldsymbol)\{([a-zA-Z\\]+)\}$/, '$2').replace(/[\{\}]/g, '');
        
        // 0. Check active fallback binder overrides
        if (this.activeBinder && this.activeBinder.variableOverrides) {
            const override = this.activeBinder.variableOverrides[symbol] || this.activeBinder.variableOverrides[cleanSymbol];
            if (override) {
                return {
                    name: override.name,
                    type: override.type || 'variable',
                    description: override.desc || override.description,
                    unit: override.unit || 'dimensionless',
                    featuredEquations: []
                };
            }
        }

        // 1. Check integration boundary overrides
        if (type === 'integration_boundary') {
            if (symbol === 'C') {
                return {
                    name: 'Integration Curve / Path Contour',
                    type: 'operator',
                    description: 'The closed or open boundary path over which the line integral is evaluated.',
                    unit: 'dimensionless'
                };
            } else if (symbol === 'S') {
                return {
                    name: 'Integration Surface',
                    type: 'operator',
                    description: 'The two-dimensional surface over which the surface integral is evaluated.',
                    unit: 'dimensionless'
                };
            } else if (symbol === 'V') {
                return {
                    name: 'Integration Volume',
                    type: 'operator',
                    description: 'The three-dimensional volume region over which the volume integral is evaluated.',
                    unit: 'dimensionless'
                };
            }
        }

        // 2. Check constants first
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
        
        // 3. Check variable dictionary with context override
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

        // 4. Check legacy physicsDictionary with active domain override support
        const legacyEntry = this.physicsDictionary[cleanSymbol] || this.physicsDictionary[symbol];
        if (legacyEntry) {
            let activeLegacy = legacyEntry;
            let match = null;
            if (legacyEntry.alternatives) {
                match = legacyEntry.alternatives.find(alt => alt.domain === this.activeDomain);
            }
            if (match) {
                activeLegacy = {
                    name: match.name,
                    type: match.type || legacyEntry.type,
                    unit: match.unit || legacyEntry.unit,
                    desc: match.desc || legacyEntry.desc
                };
            } else if (legacyEntry.domain === this.activeDomain) {
                activeLegacy = legacyEntry;
            }
            
            return {
                name: activeLegacy.name,
                type: activeLegacy.type || 'variable',
                description: activeLegacy.desc || activeLegacy.description || 'Physics variable.',
                unit: activeLegacy.unit || 'dimensionless',
                featuredEquations: []
            };
        }
        
        // 5. Fallback
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
        this.renderSymbolExplanation(symbol, info ? (info.tokenType || info.type) : null);
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

    renderSymbolExplanation(latex, type = null) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        const symbol = latex.trim();
        
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';
        if (this.aiSimulationCard) this.aiSimulationCard.style.display = 'none';
        if (this.solverRedirectContainer) this.solverRedirectContainer.style.display = 'none';

        let symbolInfo = this.resolveSymbolInfo(symbol, type);

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
            let rawLatex = (window.INITIAL_LATEX || '').trim().replace(/^['"\s]+|['"\s]+$/g, '');
            const quotePos = rawLatex.indexOf("'");
            if (quotePos > 0 && /'\s*(?:\\text|\\mathrm|\\mathbf|[a-zA-Z]{2,})/.test(rawLatex.slice(quotePos))) {
                rawLatex = rawLatex.substring(0, quotePos).trim();
            }
            this.latexInput.value = rawLatex;
            this.handleInputChange();
        } else {
            // Set defaults or display placeholder
            this.resetExplanation();
        }
    },

    getCleanLatexFromEq(eqStr) {
        if (eqStr.includes('data-tex=')) {
            const match = eqStr.match(/data-tex="([^"]+)"/);
            if (match) return this.decodeHtmlEntities(match[1]).replace(/\\par\b/g, ' ');
        }
        // Remove math wrappers if string looks raw
        return eqStr.replace(/^\\\[/, '').replace(/\\\]$/, '').trim().replace(/\\par\b/g, ' ');
    },

    decodeHtmlEntities(str) {
        const txt = document.createElement("textarea");
        txt.innerHTML = str;
        return txt.value;
    },

    handleInputChange() {
        let latex = (this.latexInput ? this.latexInput.value : '').trim().replace(/^['"\s]+|['"\s]+$/g, '');
        const quotePos = latex.indexOf("'");
        if (quotePos > 0 && /'\s*(?:\\text|\\mathrm|\\mathbf|[a-zA-Z]{2,})/.test(latex.slice(quotePos))) {
            latex = latex.substring(0, quotePos).trim();
            if (this.latexInput) this.latexInput.value = latex;
        }
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
        if (typeof latex !== 'string' || !latex) return;
        
        let cleanedLatex = latex.replace(/\\par\b/g, ' ').trim();
        
        const knownTexCmds = new Set([
            'delta', 'alpha', 'beta', 'gamma', 'epsilon', 'zeta', 'eta', 'theta', 'iota', 'kappa',
            'lambda', 'mu', 'nu', 'xi', 'pi', 'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
            'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega',
            'frac', 'sqrt', 'left', 'right', 'partial', 'infty', 'approx', 'to', 'le', 'ge', 'ne', 'equiv',
            'sim', 'simeq', 'propto', 'nabla', 'cdot', 'times', 'div', 'pm', 'mp', 'ast', 'star',
            'sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp', 'lim', 'max', 'min', 'sum', 'int', 'prod',
            'text', 'mathrm', 'mathbf', 'mathcal', 'mathbb', 'quad', 'qquad', 'vec', 'hat', 'bar', 'dot', 'ddot'
        ]);

        const parts = cleanedLatex.split(/(\\(?:text|mathrm|mathbf|mathcal|mathbb|operatorname)\{[^{}]*\})/g);
        for (let i = 0; i < parts.length; i++) {
            if (i % 2 === 0) {
                parts[i] = parts[i].replace(/(?<!\\)\b([a-zA-Z]{2,})\b/g, (match) => {
                    if (knownTexCmds.has(match) || knownTexCmds.has(match.toLowerCase())) {
                        return `\\${match}`;
                    }
                    return `\\text{${match}}`;
                });
            }
        }
        let formattedLatex = parts.join('');

        // Enforce equation delimiters
        let mathMarkup = formattedLatex;
        if (!formattedLatex.startsWith('\\[') && !formattedLatex.startsWith('\\(') && !formattedLatex.startsWith('$$') && !formattedLatex.startsWith('$')) {
            mathMarkup = '\\[ ' + formattedLatex + ' \\]';
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
        if (window.MathJax.typesetClear) {
            try {
                window.MathJax.typesetClear(elements);
            } catch (err) {
                console.warn('MathJax typesetClear failed:', err);
            }
        }
        if (window.MathJax.typesetPromise) {
            window.MathJax.typesetPromise(elements)
                .catch(err => console.warn('MathJax typesetting failed:', err));
        } else if (window.MathJax.startup && window.MathJax.startup.promise) {
            window.MathJax.startup.promise.then(() => {
                if (window.MathJax.typesetClear) {
                    try {
                        window.MathJax.typesetClear(elements);
                    } catch (e) {}
                }
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

    triggerGeminiDefineFormula(btnDefine) {
        if (!this.currentLatex) return;

        const originalHtml = btnDefine.innerHTML;
        btnDefine.disabled = true;
        btnDefine.style.opacity = '0.7';
        btnDefine.innerHTML = `<span style="display:inline-block; width:10px; height:10px; border:2px solid currentColor; border-right-color:transparent; border-radius:50%; animation:explainer-spin 0.8s linear infinite; margin-right:5px;"></span> ✨ Researching...`;

        // Inject spin keyframe if not present
        if (!document.getElementById('explainer-spin-style')) {
            const style = document.createElement('style');
            style.id = 'explainer-spin-style';
            style.textContent = `@keyframes explainer-spin { 100% { transform: rotate(360deg); } }`;
            document.head.appendChild(style);
        }

        const adminKey = localStorage.getItem('terra_admin_key') || '';

        fetch(`${BASE_URL}/physics/api/define-formula`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Terra-Admin-Key': adminKey
            },
            body: JSON.stringify({ latex: this.currentLatex })
        })
        .then(res => res.json())
        .then(data => {
            btnDefine.disabled = false;
            btnDefine.style.opacity = '1';
            btnDefine.innerHTML = originalHtml;

            if (data.success && data.formula) {
                // Live update page with official Gemini-defined formula!
                this.currentId = data.formula.id;
                this.fetchSubtopicsForFormula(data.formula.id).then(subtopics => {
                    this.renderFormula(data.formula, subtopics);
                });
            } else {
                alert('Gemini Definition Error: ' + (data.error || 'Unknown error occurred.'));
            }
        })
        .catch(err => {
            btnDefine.disabled = false;
            btnDefine.style.opacity = '1';
            btnDefine.innerHTML = originalHtml;
            console.error('Gemini definition request failed:', err);
            alert('Request failed: ' + err.message);
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
            this.formulaBadge.className = 'badge-status ' + (status.includes('draft') || status.includes('synthesized') ? 'badge-draft' : 'badge-platinum');
            this.formulaBadge.textContent = status.replace('-', ' ').toUpperCase();
        }

        // Show Define button for unregistered/synthesized formulas
        const btnDefine = document.getElementById('btn-define-formula');
        if (btnDefine) {
            const isSynthesized = formula.status === 'synthesized-ast' || formula.title === 'Custom Physical Relation' || formula.is_synthesized;
            btnDefine.style.display = isSynthesized ? 'inline-flex' : 'none';

            if (!btnDefine.getAttribute('data-bound')) {
                btnDefine.setAttribute('data-bound', 'true');
                btnDefine.addEventListener('click', () => {
                    this.triggerGeminiDefineFormula(btnDefine);
                });
            }
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
                    implication: formula.interpretation
                });
            }
            if (formula.symmetry_origin && formula.symmetry_origin !== 'Symmetry derivations pending.') {
                scenarios.push({
                    condition: 'Symmetry & Coordinate Invariance',
                    implication: formula.symmetry_origin
                });
            }
            if (formula.limits_and_boundary && formula.limits_and_boundary !== 'Boundary analysis pending.') {
                scenarios.push({
                    condition: 'Limiting Cases & Boundaries',
                    implication: formula.limits_and_boundary
                });
            }

            // If still empty, use synthesis fallback
            if (scenarios.length === 0) {
                scenarios = synthesis.scenarios;
            }
        }
        this.renderAIScenariosSection(scenarios);

        // Render Knowledge Graph Ancestry card
        this.renderKnowledgeGraphCard(formula);

        // Deconstruct EVERY element in the LaTeX string, merging database semantic definitions for left panel hover list
        this.renderElementsBreakdown(this.currentLatex, formula.semantic_variables || {});

        // Populate Topological Bridges
        this.renderBridges(subtopics);

        // Setup Dimensional Solver Link
        this.setupSolverLink(this.currentLatex);

        // Initialize sandbox simulator
        this.initSandbox(this.currentLatex, formula.semantic_variables || {});
    },

    renderKnowledgeGraphCard(formula) {
        const card = document.getElementById('knowledge-graph-card');
        const details = document.getElementById('knowledge-graph-details');
        if (!card || !details) return;

        const hasParent = formula && (formula.parent_formula || formula.parent_formula_id);
        const hasSubcomponents = formula && Array.isArray(formula.subcomponents) && formula.subcomponents.length > 0;
        const hasOtherMetadata = formula && (formula.derivation_type || formula.constraints);

        if (!hasParent && !hasSubcomponents && !hasOtherMetadata) {
            card.style.display = 'none';
            return;
        }

        card.style.display = 'flex';
        let html = '';

        if (formula.derivation_type) {
            html += `<div style="margin-bottom: 10px;"><strong>Derivation Relationship:</strong> <span class="badge-status badge-platinum" style="font-size: 0.72rem; padding: 2px 6px; background: rgba(100,255,218,0.1); color: var(--accent-default, #64ffda); border: 1px solid rgba(100,255,218,0.3); border-radius: 4px;">${formula.derivation_type}</span></div>`;
        }

        // 1. Parent Master Equation Link
        if (formula.parent_formula && formula.parent_formula.id) {
            const p = formula.parent_formula;
            const parentUrl = p.url || `/physics/equation-explainer?id=${encodeURIComponent(p.id)}`;
            html += `
                <div style="margin-bottom: 14px; background: rgba(100, 255, 218, 0.05); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 8px; padding: 12px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 4px; font-weight: 600;">⬆ Parent Master Equation</div>
                    <a href="${parentUrl}" style="color: var(--accent-default, #64ffda); text-decoration: none; font-weight: 600; font-size: 1.05rem; display: inline-flex; align-items: center; gap: 8px;">
                        <span>${p.title}</span>
                        <span style="color: #ffd700; font-family: monospace;">($\\;${p.equation}\\;$)</span>
                    </a>
                </div>
            `;
        } else if (formula.parent_formula_id) {
            const parentUrl = `/physics/equation-explainer?id=${encodeURIComponent(formula.parent_formula_id)}`;
            const parentName = formula.parent_formula_id.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
            html += `<div style="margin-bottom: 10px;"><strong>Master Parent Law:</strong> <a href="${parentUrl}" style="color: var(--accent-default, #64ffda); text-decoration: none; border-bottom: 1px dashed rgba(100,255,218,0.4); font-weight: 600;">${parentName}</a></div>`;
        }

        // 2. Child Subcomponents Grid
        if (hasSubcomponents) {
            html += `
                <div style="margin-top: 10px;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 8px; font-weight: 600;">⬇ Formula Component Sub-equations (${formula.subcomponents.length})</div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">
            `;
            formula.subcomponents.forEach(child => {
                const childId = typeof child === 'string' ? child : child.id;
                const childTitle = typeof child === 'string' ? childId.replace(/-/g, ' ') : child.title;
                let childEq = (typeof child === 'object' && child.equation) ? child.equation : '';
                // Filter out non-TeX prose strings mistakenly stored as child.equation
                if (childEq && (childEq.includes(' ') && !childEq.includes('\\') && !childEq.includes('=') && !childEq.includes('+') && !childEq.includes('-'))) {
                    childEq = '';
                }
                const childUrl = `/physics/equation-explainer?id=${encodeURIComponent(childId)}`;
                const mathPart = childEq ? `<span style="font-size: 0.9rem; color: #ffd700;">\\(${childEq}\\)</span>` : '';
                html += `
                    <a href="${childUrl}" style="display: flex; flex-direction: column; gap: 4px; padding: 10px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; text-decoration: none; transition: all 0.2s;" onmouseover="this.style.borderColor='rgba(100,255,218,0.4)'; this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='rgba(255,255,255,0.08)'; this.style.transform='none'">
                        <span style="font-size: 0.82rem; color: #f1f5f9; font-weight: 600;">${childTitle}</span>
                        ${mathPart}
                    </a>
                `;
            });
            html += `
                    </div>
                </div>
            `;
        }

        if (formula.constraints) {
            try {
                const c = typeof formula.constraints === 'string' ? JSON.parse(formula.constraints) : formula.constraints;
                const pills = this.formatConstraintsToPills(c);
                if (pills) {
                    html += `<div style="margin-top: 10px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap;"><strong>Active Physical Constraints:</strong> ${pills}</div>`;
                }
            } catch(e) {}
        }
        details.innerHTML = html;
        this.triggerTypeset([details]);
    },

    formatConstraintsToPills(c) {
        if (!c || typeof c !== 'object') return '';
        const pills = [];
        for (const [key, val] of Object.entries(c)) {
            let label = `${key}: ${val}`;
            if (key === 'partial_t' && (val === 0 || val === '0')) {
                label = 'Time-Independent (\\( \\frac{\\partial}{\\partial t} = 0 \\))';
            } else if (key === 'regime') {
                label = `Regime: ${String(val).replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}`;
            } else if (key === 'v_c') {
                label = `Relativistic Limit (\\(v \\to c\\))`;
            } else if (key === 'hbar_0') {
                label = `Classical Limit (\\(\\hbar \\to 0\\))`;
            }
            pills.push(`<span style="display: inline-flex; align-items: center; gap: 4px; padding: 3px 8px; border-radius: 4px; font-size: 0.78rem; background: rgba(168, 85, 247, 0.12); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); font-weight: 500;">${label}</span>`);
        }
        return pills.join(' ');
    },

    renderCustomExplanation(latex) {
        this.currentFormula = null;
        this.currentSubtopics = [];

        // Hide old layout elements
        this.explainerPlaceholder.style.display = 'none';
        this.officialBreakdown.style.display = 'none';
        this.symbolsBreakdown.style.display = 'block';
        this.topologicalBridges.style.display = 'none';

        // Deconstruct EVERY element in the custom LaTeX string first to populate activeBinder
        this.renderElementsBreakdown(latex, {});

        // Synthesize dynamic AI Overview
        const synthesis = this.synthesizeCustomOverview(latex);

        // Title and Badge
        this.formulaTitle.textContent = this.activeBinder ? this.activeBinder.name : (synthesis.title || 'Custom Physics Formula');
        if (this.formulaBadge) {
            this.formulaBadge.className = 'badge-status badge-unregistered';
            this.formulaBadge.textContent = 'Live Analysis';
        }

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
        latex = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');
        
        // 1. Syntactic / Structural Anchor Detection (Rule-Based overrides)
        // Relativistic field theory / Gauge theory / General Relativity: D_\mu, \partial_\mu, \gamma^\mu, \Gamma^\mu, g_{\mu\nu}, R_{\mu\nu}, etc.
        if (/(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)_(?:\\mu|\\nu|\\alpha|\\beta)/.test(latex) || /(?:D|\\partial|\\gamma|\\Gamma|g|R|G|W|B)\^(?:\\mu|\\nu|\\alpha|\\beta)/.test(latex)) {
            return 'quantum_mechanics';
        }
        
        // Vector calculus / Stokes' / Curl / Circulation: \oint_C, \iint_S, \nabla \times
        if (/\\(oint|iint|iiint|int)_\{?[CSV]\}?/.test(latex) || /\\nabla\s*\\times/.test(latex)) {
            if (/(?:\\mathbf\{E\}|\\mathbf\{B\}|\\mathbf\{J\}|\\epsilon_0|\\mu_0|q|e|\\Phi)/.test(latex)) {
                return 'electromagnetism';
            }
            return 'classical_mechanics';
        }

        // Poisson brackets: \{ A, B \} or \{ \rho, H \}
        if (/\\\{\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*,\s*[a-zA-Z0-9\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*\s*\\\}/.test(latex)) {
            return 'classical_mechanics';
        }
        
        // Bra-ket notation: \langle ... \rangle or \mid
        if (/\\langle|\\rangle|\\mid/.test(latex)) {
            return 'quantum_mechanics';
        }
        
        // Thermodynamic differentials: dU, dS, dV, dH, dG, dQ
        if (/\b(dU|dS|dV|dH|dG|dQ|dW)\b/.test(latex)) {
            return 'thermodynamics';
        }
        
        // 2. Co-occurrence / Match Counts
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
        
        // Helper to check if a specific symbol is present in the LaTeX string
        const hasSymbol = (sym) => {
            const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const pattern = /^[a-zA-Z0-9]+$/.test(sym) 
                ? new RegExp('\\b' + escaped + '\\b')
                : new RegExp(escaped);
            return pattern.test(latex);
        };

        // Apply co-occurrence multipliers (Tier 2 HCR)
        
        // Classical Mechanics:
        if (hasSymbol('T') && hasSymbol('V') && (hasSymbol('L') || hasSymbol('\\mathcal{L}'))) {
            counts.classical_mechanics += 3.0; // Lagrangian system indicators
        }
        if (hasSymbol('F') && hasSymbol('m') && hasSymbol('a')) {
            counts.classical_mechanics += 2.0; // Newton's Second Law indicators
        }
        if (hasSymbol('r') && hasSymbol('p') && (hasSymbol('L') || hasSymbol('I'))) {
            counts.classical_mechanics += 2.0; // Angular momentum indicators
        }
        
        // Thermodynamics:
        if (hasSymbol('P') && hasSymbol('V') && hasSymbol('T')) {
            counts.thermodynamics += 3.0; // Ideal gas law / EOS indicators
        }
        if (hasSymbol('k_B') && hasSymbol('T')) {
            counts.thermodynamics += 2.0; // Thermal energy indicators
        }
        if (hasSymbol('U') && hasSymbol('S') && hasSymbol('T')) {
            counts.thermodynamics += 2.5; // Thermodynamic potentials indicators
        }
        if (hasSymbol('S') && hasSymbol('Q') && hasSymbol('T')) {
            counts.thermodynamics += 3.0; // Second law indicators
        }
        
        // Electromagnetism:
        if (hasSymbol('\\epsilon_0') && hasSymbol('\\mu_0')) {
            counts.electromagnetism += 3.0; // Maxwell speed of light indicators
        }
        if (hasSymbol('\\epsilon_0')) {
            counts.electromagnetism += 1.5; // Permittivity of free space indicator
        }
        if (hasSymbol('\\epsilon_0') && (hasSymbol('\\mathbf{E}') || hasSymbol('E'))) {
            counts.electromagnetism += 3.0; // Electrostatic field energy/force indicators
        }
        if (hasSymbol('\\mathbf{E}') && hasSymbol('\\mathbf{B}')) {
            counts.electromagnetism += 2.5; // Electromagnetic fields co-occurrence
        }
        if (hasSymbol('q') && (hasSymbol('\\mathbf{E}') || hasSymbol('\\mathbf{B}'))) {
            counts.electromagnetism += 2.0; // Lorentz force components
        }
        
        // Quantum Mechanics:
        if (hasSymbol('\\hbar') && (hasSymbol('\\psi') || hasSymbol('\\Psi'))) {
            counts.quantum_mechanics += 3.0; // Schrodinger equation components
        }
        if (hasSymbol('i') && hasSymbol('\\hbar') && hasSymbol('\\partial')) {
            counts.quantum_mechanics += 2.5; // Quantum time evolution indicator
        }
        if (hasSymbol('\\hat{H}') && hasSymbol('E')) {
            counts.quantum_mechanics += 2.0; // Eigenvalue equation indicator
        }
        
        // Optics:
        if (hasSymbol('n') && hasSymbol('\\lambda')) {
            counts.optics += 2.0; // Wavelength index dependence
        }
        if (hasSymbol('\\omega') && hasSymbol('k')) {
            counts.optics += 2.0; // Dispersion relation components
        }
        
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
        
        // Save officialVariables for redraw on domain change, normalizing keys to strip delimiters
        this.officialVariables = {};
        if (officialVariables) {
            for (const [key, val] of Object.entries(officialVariables)) {
                const cleanKey = key.trim()
                                    .replace(/^\\\(/, '')
                                    .replace(/\\\)$/, '')
                                    .replace(/^\\\[/, '')
                                    .replace(/\\\]$/, '')
                                    .replace(/^\$\$/, '')
                                    .replace(/\$\$$/, '')
                                    .replace(/^\$/, '')
                                    .replace(/\$/, '')
                                    .trim();
                this.officialVariables[cleanKey] = val;
            }
        }
        
        // Match fallback binders if present
        this.activeBinder = null;
        if (latex) {
            for (const binder of this.fallbackBinders) {
                if (binder.matchPattern.test(latex)) {
                    this.activeBinder = binder;
                    if (!this.activeDomain) {
                        this.activeDomain = binder.domain;
                        if (this.activeDomainSelect) {
                            this.activeDomainSelect.value = binder.domain;
                        }
                    }
                    console.log(`Matched fallback binder: ${binder.name}`);
                    break;
                }
            }
        }
        
        // Run domain auto-detection if activeDomain is empty
        if (!this.activeDomain && latex) {
            const detected = this.detectDomainFromLatex(latex);
            if (detected) {
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

            if (tok.type === 'integration_boundary') {
                let name = 'Integration Boundary / Domain';
                let desc = 'The domain, region, curve, or boundary over which the integral is evaluated.';
                if (symbol === 'C') {
                    name = 'Integration Curve / Path Contour';
                    desc = 'The closed or open boundary path over which the line integral is evaluated.';
                } else if (symbol === 'S') {
                    name = 'Integration Surface';
                    desc = 'The two-dimensional surface over which the surface integral is evaluated.';
                } else if (symbol === 'V') {
                    name = 'Integration Volume';
                    desc = 'The three-dimensional volume region over which the volume integral is evaluated.';
                }
                info = {
                    name: name,
                    type: 'operator',
                    tokenType: 'integration_boundary',
                    description: desc,
                    unit: 'dimensionless',
                    source: 'heuristic'
                };
            } else if (tok.type === 'operator' && symbol.includes('\\frac{')) {
                const isPartial = symbol.includes('\\partial');
                const isTotal = symbol.includes('\\frac{d');
                
                if (isPartial || isTotal) {
                    const cleanSym = symbol.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|vec|hat|bar|tilde|dot|ddot|underline)/g, '');
                    const match = cleanSym.match(/\\frac\{(?:\\partial|d)\^?[0-9]*\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{(?:\\partial|d)\s*([a-zA-Z\\]+)\^?[0-9]*\}/);
                    
                    let name = isPartial ? 'Partial Derivative' : 'Ordinary Derivative';
                    let desc = isPartial 
                        ? 'Represents the rate of change of a multi-variable function with respect to one variable, holding other variables constant.' 
                        : 'Represents the instantaneous rate of change of a dependent variable with respect to an independent variable.';
                    
                    if (match) {
                        const num = match[1];
                        const den = match[2];
                        
                        const denEntry = this.officialVariables[den] || this.physicsDictionary[den];
                        const denName = denEntry ? denEntry.name.split('/')[0].trim() : den;
                        
                        if (num) {
                            const numEntry = this.officialVariables[num] || this.physicsDictionary[num];
                            const numName = numEntry ? numEntry.name.split('/')[0].trim() : num;
                            
                            name = `${isPartial ? 'Partial' : 'Total'} Derivative of ${numName} with respect to ${denName}`;
                            desc = `Represents how the quantity ${numName.toLowerCase()} changes with respect to the variable ${denName.toLowerCase()}.`;
                        } else {
                            name = `${isPartial ? 'Partial' : 'Total'} Derivative Operator`;
                            desc = `The differential operator representing the rate of change with respect to the variable ${denName.toLowerCase()}.`;
                        }
                    }
                    
                    info = {
                        name: name,
                        type: 'operator',
                        description: desc,
                        unit: 'operator',
                        source: 'heuristic'
                    };
                }
            } else if (tok.type === 'spacetime_derivative') {
                const isContravariant = symbol.includes('^');
                info = {
                    name: isContravariant ? 'Contravariant Spacetime Derivative' : 'Covariant Spacetime Derivative',
                    type: 'operator',
                    description: isContravariant 
                        ? 'Partial derivative with respect to a contravariant coordinate index, raising the coordinate index in tensor calculus.' 
                        : 'Partial derivative with respect to a covariant coordinate index, lowering the coordinate index in tensor calculus.',
                    unit: 'operator',
                    source: 'heuristic'
                };
            } else if (tok.type === 'differential_operator') {
                info = {
                    name: 'Differential Operator',
                    type: 'operator',
                    description: 'Represents an infinitesimal change or differential element in calculus (e.g. dx, dt).',
                    unit: 'operator',
                    source: 'heuristic'
                };
            } else if (this.userCustomizations[symbol]) {
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
            } else if (/\\frac\{d/.test(symbol)) {
                info = {
                    name: 'Total Derivative',
                    type: tok.type,
                    description: 'Represents the total rate of change of a quantity with respect to an independent variable.',
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
                    let match = null;
                    if (dictEntry.alternatives) {
                        match = dictEntry.alternatives.find(alt => alt.domain === this.activeDomain);
                    }
                    if (match) {
                        activeEntry = {
                            name: match.name,
                            type: match.type || dictEntry.type,
                            unit: match.unit || dictEntry.unit,
                            desc: match.desc || dictEntry.desc,
                            alternatives: dictEntry.alternatives
                        };
                    } else if (dictEntry.domain === this.activeDomain) {
                        activeEntry = dictEntry;
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

            if (info && info.type === 'modifier') {
                hasModifiers = true;
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

                const updatedRow = this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, targetRow);
                EquationExplainer.triggerTypeset([updatedRow]);
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
        let displaySymbol = symbol;
        if (symbol === '\\sqrt') {
            displaySymbol = '\\sqrt{\\phantom{x}}';
        }
        const mathjaxSymbol = `$${displaySymbol}$`;

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
            return newRow;
        }

        this.bindRowEvents(row, symbol, info);

        if (!existingRow) {
            if (info.type === 'modifier') {
                this.modifiersList.appendChild(row);
            } else {
                this.symbolsList.appendChild(row);
            }
        }
        return row;
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

            const updatedRow = this.renderVariableRow(symbol, { ...updatedInfo, source: 'user' }, row);

            // Retypeset the row
            EquationExplainer.triggerTypeset([updatedRow]);
        });

        cancelBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const updatedRow = this.renderVariableRow(symbol, info, row);

            // Retypeset the row
            EquationExplainer.triggerTypeset([updatedRow]);
        });

        wrapper.querySelector('.edit-var-name').focus();
    },

    extractAllMathTokens(latex, officialVariables = {}) {
        if (!latex) return [];
        latex = latex.replace(/\\par\b/g, ' ')
                     .replace(/\\varepsilon(?![a-zA-Z])/g, '\\epsilon')
                     .replace(/\\vartheta(?![a-zA-Z])/g, '\\theta')
                     .replace(/\\varphi(?![a-zA-Z])/g, '\\phi')
                     .replace(/\\varrho(?![a-zA-Z])/g, '\\rho')
                     .replace(/\\varpi(?![a-zA-Z])/g, '\\pi')
                     .replace(/\\varsigma(?![a-zA-Z])/g, '\\sigma');

        const found = [];
        const seen = new Set();
        const consumedSubtokens = new Set();

        const addToken = (symbol, type) => {
            if (!symbol || seen.has(symbol)) return;
            seen.add(symbol);
            found.push({ symbol, type });
        };

        // Structural LaTeX commands and delimiters to suppress from fallback variable lookup
        const structuralDelimiters = [
            '\\rangle', '\\langle', '\\mid', '|', '(', ')', '[', ']', '{', '}', '+', '-', '=', '/', 
            '\\sum', '\\prod', '\\int', '\\oint', '\\iint', '\\iiint', '\\cdot', '\\times',
            '\\sqrt', '\\frac', '\\partial', '\\text', '\\mathrm', '\\mathsf', '\\left', '\\right'
        ];
        structuralDelimiters.forEach(d => {
            consumedSubtokens.add(d);
            consumedSubtokens.add(d.replace(/^\\/, ''));
        });

        // Priority 1: Match against officialVariables from formula database
        if (officialVariables && typeof officialVariables === 'object') {
            const sortedOfficialKeys = Object.keys(officialVariables).sort((a, b) => b.length - a.length);
            sortedOfficialKeys.forEach(key => {
                if (!key || consumedSubtokens.has(key) || consumedSubtokens.has(key.replace(/^\\/, ''))) return;
                const escaped = key.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp(escaped, 'g');
                if (regex.test(latex)) {
                    const offObj = officialVariables[key];
                    const type = (offObj && typeof offObj === 'object' && offObj.type) ? offObj.type : ((typeof offObj === 'string' && /operator/i.test(offObj)) || key.startsWith('\\hat') || key.includes('\\partial') || key.includes('\\nabla') ? 'operator' : 'variable');
                    addToken(key, type);

                    // Track sub-tokens to consume
                    const subParts = key.match(/\\[a-zA-Z]+|[a-zA-Z]/g) || [];
                    subParts.forEach(part => {
                        const cleanPart = part.replace(/^\\/, '');
                        if (cleanPart.length > 0) {
                            consumedSubtokens.add(cleanPart);
                            consumedSubtokens.add(part);
                            consumedSubtokens.add('\\' + cleanPart);
                        }
                    });
                }
            });
        }

        // Extract subscripts as modifiers from original raw latex
        const subscriptModRegex = /_\{([^\}]+)\}|_([a-zA-Z\\]+)/g;
        let subModMatch;
        while ((subModMatch = subscriptModRegex.exec(latex)) !== null) {
            let content = subModMatch[1] || subModMatch[2];
            content = content.replace(/\\(text|mathrm|mathsf|mathrm)\{([^\}]+)\}/g, '$2').trim();
            if ((/^[a-zA-Z]{2,}$/.test(content) || this.modifierGlossary[content]) && !consumedSubtokens.has(content)) {
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

        // Pre-scan for specific physical constants with subscripts (to prevent stripping their subscripts)
        const constantSubscriptRegex = /\\(epsilon|mu|k|a|m|g|G|N)_(?:0|\{0\}|B|\{B\}|e|\{e\}|p|\{p\}|n|\{n\}|F|\{F\}|A|\{A\})(?![a-zA-Z])/g;
        let constMatch;
        while ((constMatch = constantSubscriptRegex.exec(text)) !== null) {
            const fullMatch = constMatch[0];
            // Normalize: strip curly braces from subscript for token representation
            const normalizedSymbol = fullMatch.replace(/_\{([^\}]+)\}/, '_$1');
            addToken(normalizedSymbol, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for integration boundaries: \oint_C, \iint_S, \int_a^b (run on original text before subscripts are stripped)
        const integralBoundaryRegex = /\\(int|oint|iint|iiint)_\{?([a-zA-Z0-9]+)\}?/g;
        let boundaryMatch;
        while ((boundaryMatch = integralBoundaryRegex.exec(text)) !== null) {
            const boundaryVar = boundaryMatch[2];
            if (boundaryVar && /^[a-zA-Z]$/.test(boundaryVar)) {
                addToken(boundaryVar, 'integration_boundary');
            }
        }

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

        // Pre-scan for mathcal variables: \mathcal{L} or \mathcal{H}
        const mathcalRegex = /\\mathcal\{([a-zA-Z])\}/g;
        let mathcalMatch;
        while ((mathcalMatch = mathcalRegex.exec(text)) !== null) {
            const fullMatch = mathcalMatch[0];
            addToken(fullMatch, 'variable');
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }



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


        // Check for spacetime derivatives: \partial_\mu, \partial^\mu, \partial_\nu, \partial^\nu
        const spacetimeDerivRegex = /\\partial_(?:\\mu|\\nu|\\alpha|\\beta|[a-zA-Z0-9])|\\partial\^(?:\\mu|\\nu|\\alpha|\\beta|[a-zA-Z0-9])/g;
        const spaceMatches = [...text.matchAll(spacetimeDerivRegex)];
        for (const spaceMatch of spaceMatches) {
            const fullMatch = spaceMatch[0];
            addToken(fullMatch, 'spacetime_derivative');
            const idxVar = fullMatch.includes('_') ? fullMatch.split('_')[1] : fullMatch.split('^')[1];
            if (idxVar) {
                addToken(idxVar, 'variable');
            }
        }
        text = text.replace(spacetimeDerivRegex, ' ');

        // Check for partial derivatives: \frac{\partial \Psi}{\partial t}
        const partialRegex = /\\frac\{\\partial\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{\\partial\s*([a-zA-Z\\]+)\}/g;
        let partMatch;
        while ((partMatch = partialRegex.exec(text)) !== null) {
            const fullMatch = partMatch[0];
            const numVar = partMatch[1];
            const denVar = partMatch[2];
            
            addToken(fullMatch, 'operator');
            
            if (numVar) {
                const cleanNum = numVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanNum)) {
                    addToken(cleanNum, 'variable');
                }
            }
            if (denVar) {
                const cleanDen = denVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanDen)) {
                    addToken(cleanDen, 'variable');
                }
            }
            
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for total derivatives: \frac{d\rho}{dt}
        const totalDerivRegex = /\\frac\{d\^?[0-9]*\s*([a-zA-Z\\]+(?:_[a-zA-Z0-9]+|\{[^\}]+\})*)?\}\{d\s*([a-zA-Z\\]+)\^?[0-9]*\}/g;
        let totMatch;
        while ((totMatch = totalDerivRegex.exec(text)) !== null) {
            const fullMatch = totMatch[0];
            const numVar = totMatch[1];
            const denVar = totMatch[2];
            
            addToken(fullMatch, 'operator');
            
            if (numVar) {
                const cleanNum = numVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanNum)) {
                    addToken(cleanNum, 'variable');
                }
            }
            if (denVar) {
                const cleanDen = denVar.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([^\}]+)\}/g, '$2').trim();
                if (/^\\[a-zA-Z]+$|^[a-zA-Z]$/.test(cleanDen)) {
                    addToken(cleanDen, 'variable');
                }
            }

            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // Check for integration differentials: d\mathbf{l}, d\mathbf{S}, d\vec{r}, dx, dy, dt, dm, dV, dA
        const differentialRegex = /\bd(?:\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{([a-zA-Z])\}|([a-zA-Z]))\b/g;
        let diffMatch;
        while ((diffMatch = differentialRegex.exec(text)) !== null) {
            const fullMatch = diffMatch[0];
            const baseVar = diffMatch[2] || diffMatch[3];
            
            // Add 'd' as differential operator
            addToken('d', 'differential_operator');
            
            // Add base variable
            if (baseVar) {
                addToken(baseVar, 'variable');
            }
            
            // Replace the full match to avoid standalone 'd' or baseVar from matching later
            const escaped = fullMatch.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
            const regex = new RegExp(escaped, 'g');
            text = text.replace(regex, ' ');
        }

        // 2b. Pre-scan for official database keys to keep them grouped as unified terms
        if (officialVariables) {
            for (const sym of Object.keys(officialVariables)) {
                if (this.latexContainsSymbol(text, sym)) {
                    const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
                    addToken(sym, isOperator ? 'operator' : 'variable');
                    
                    // Replace matched symbol in text to avoid partial matching later
                    let pattern;
                    const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                    if (sym.startsWith('\\')) {
                        pattern = escaped + '(?![a-zA-Z])';
                    } else if (/^[a-zA-Z0-9_\{\}]+$/.test(sym)) {
                        pattern = '\\b' + escaped + '\\b';
                    } else {
                        pattern = escaped;
                    }
                    const regex = new RegExp(pattern, 'g');
                    text = text.replace(regex, ' ');
                }
            }
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
                let pattern;
                const escaped = sym.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                if (sym.startsWith('\\')) {
                    pattern = escaped + '(?![a-zA-Z])';
                } else if (/^[a-zA-Z0-9_\{\}]+$/.test(sym)) {
                    pattern = '\\b' + escaped + '\\b';
                } else {
                    pattern = escaped;
                }
                const regex = new RegExp(pattern, 'g');
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
            const structuralCmds = new Set([
                '\\frac', '\\left', '\\right', '\\cdot', '\\times', '\\div', 
                '\\iff', '\\implies', '\\ge', '\\le', '\\ast', '\\star',
                '\\boldsymbol', '\\mathbf', '\\mathsf', '\\mathrm', '\\text', '\\mathcal', 
                '\\vec', '\\hat', '\\bar', '\\tilde', '\\dot', '\\ddot', '\\underline'
            ]);
            if (structuralCmds.has(sym) || consumedSubtokens.has(sym) || consumedSubtokens.has(sym.replace(/^\\/, ''))) continue;
            
            const isOperator = this.physicsDictionary[sym] && this.physicsDictionary[sym].type === 'operator';
            addToken(sym, isOperator ? 'operator' : 'variable');
        }

        // 7. Scan for explicit mathematical operators (filtering out basic arithmetic operators)
        const standardOperators = ['\\int', '\\oint', '\\sum', '\\partial', '\\nabla', '\\Delta'];
        standardOperators.forEach(op => {
            if (!consumedSubtokens.has(op) && this.latexContainsSymbol(text, op)) {
                addToken(op, 'operator');
            }
        });

        // 8. Scan for single Roman letters (a-z, A-Z)
        text = text.replace(/\\[a-zA-Z]+/g, ' ');
        const romanPattern = /[a-zA-Z]/g;
        while ((match = romanPattern.exec(text)) !== null) {
            const sym = match[0];
            if (!consumedSubtokens.has(sym) && this.latexContainsSymbol(text, sym)) {
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

        const cleanStylesForSorting = (str) => {
            let res = str;
            let hasStyles = true;
            while (hasStyles) {
                const next = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\{((?:[^{}]|\{[^{}]*\})*)\}/g, '$2');
                if (next === res) {
                    hasStyles = false;
                } else {
                    res = next;
                }
            }
            res = res.replace(/\\(mathbf|mathsf|mathrm|text|boldsymbol|mathcal|vec|hat|bar|tilde|dot|ddot|underline)\s*(\\[a-zA-Z]+|[a-zA-Z0-9])/g, '$2');
            return res;
        };

        const cleanSearch = getCleanSearchString(latex);
        const cleanLatex = cleanStylesForSorting(latex);

        found.sort((a, b) => {
            let indexA = -1;
            if (a.type === 'modifier') {
                const escaped = a.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexA = match ? match.index : latex.indexOf(a.symbol);
            } else {
                const hasStructuralA = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(a.symbol);
                indexA = hasStructuralA ? cleanLatex.indexOf(a.symbol) : cleanSearch.indexOf(a.symbol);
            }
            
            let indexB = -1;
            if (b.type === 'modifier') {
                const escaped = b.symbol.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
                const regex = new RegExp('([_^]\\{?\\s*|\\\\text\\{\\s*)' + escaped);
                const match = latex.match(regex);
                indexB = match ? match.index : latex.indexOf(b.symbol);
            } else {
                const hasStructuralB = /\\(frac|mathbf|mathrm|text|vec|hat|bar|tilde|dot|ddot|underline)/.test(b.symbol);
                indexB = hasStructuralB ? cleanLatex.indexOf(b.symbol) : cleanSearch.indexOf(b.symbol);
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
        
        let text = latex.trim().replace(/\\par\b/g, ' ');

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
        if (typeof text !== 'string' || !text) return text;
        
        const placeholders = [];
        let tempText = text.replace(/\\par\b/g, ' ');
        
        function protect(match) {
            placeholders.push(match);
            return `\uE000MATH_${placeholders.length - 1}\uE000`;
        }

        const greekMap = {
            'Γ': '\\Gamma', 'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta',
            'ε': '\\epsilon', 'θ': '\\theta', 'λ': '\\lambda', 'μ': '\\mu', 'ν': '\\nu',
            'π': '\\pi', 'ρ': '\\rho', 'σ': '\\sigma', 'τ': '\\tau', 'φ': '\\phi',
            'ψ': '\\psi', 'ω': '\\omega', 'Ω': '\\Omega', 'Δ': '\\Delta'
        };

        // 1. Protect existing MathJax delimiters ($$, $, \(\), \[\]) FIRST
        tempText = tempText.replace(/\$\$[\s\S]*?\$\$/g, protect);
        tempText = tempText.replace(/\$[^\$]+\$/g, protect);
        tempText = tempText.replace(/\\\([\s\S]*?\\\)/g, protect);
        tempText = tempText.replace(/\\\[[\s\S]*?\\\]/g, protect);

        // 2. Fix un-delimited equation patterns like "Γ = \frac..." or "var = \frac..."
        tempText = tempText.replace(/([A-Za-z\u0370-\u03FF]+)\s*=\s*(\\[a-zA-Z]+(?:\{[^{}]*\}|\([^)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^\/\*\+\-])+)/g, (match, lhs, rhs) => {
            if (match.includes('\uE000')) return match;
            let cleanLhs = lhs.trim();
            if (greekMap[cleanLhs]) cleanLhs = greekMap[cleanLhs];
            return protect(`\\(${cleanLhs} = ${rhs.trim()}\\)`);
        });

        // 3. Convert limiting case phrases like "(T) approaches zero" or "Γ approaches infinity"
        tempText = tempText.replace(/(\([a-zA-Z0-9_\^ ]+\)|[A-Za-z\u0370-\u03FF]+)\s+approaches\s+(zero|infinity|0|\\infty)/gi, (match, sym, target) => {
            if (match.includes('\uE000')) return match;
            let cleanSym = sym.replace(/^\(|\)$/g, '').trim();
            if (greekMap[cleanSym]) cleanSym = greekMap[cleanSym];
            const texTarget = (target.toLowerCase() === 'infinity') ? '\\infty' : '0';
            return protect(`\\(${cleanSym} \\to ${texTarget}\\)`);
        });

        // Helper for checking if text in parens is a math variable vs English prose
        function isMathParen(innerStr) {
            const s = innerStr.trim();
            if (!s) return false;
            if (s.includes(',') || s.includes(';')) return false;
            if (/\b(or|in|and|of|for|at|to|is|with|where|if|not|by|on|the|an|e\.g\.|i\.e\.|eigenfunctions?|eigenvalues?)\b/i.test(s)) return false;
            // Single English words (3+ letters with no math operators, backslashes, or digits) are prose labels, not math variables
            if (/^[a-zA-Z]{3,}$/.test(s)) return false;
            const units = ['C', 'J', 'K', 's', 'V', 'W', 'Pa', 'Hz', 'N', 'rad', 'mol'];
            if (units.includes(s)) return false;
            const words = s.split(/\s+/);
            if (words.length > 1) {
                const allMath = words.every(w => /^[a-zA-Z0-9_\^\\]+$/.test(w) && !/^[a-zA-Z]{3,}$/.test(w));
                if (!allMath) return false;
            }
            return true;
        }

        // 4. Convert parenthesized variable notations in prose like (Ze)^2, (k_B T), (Z), (e), (a), (k_B), (T)
        tempText = tempText.replace(/\((?:[a-zA-Z0-9_\^\s]|\\_[a-zA-Z0-9]+)+\)(?:\^[0-9a-zA-Z{}]+)?/g, (match) => {
            if (match.includes('\uE000')) return match;
            const innerStr = match.slice(1, match.indexOf(')')).trim();
            if (!isMathParen(innerStr)) return match;
            if (match.includes('^')) {
                const exp = match.slice(match.indexOf(')') + 1);
                return protect(`\\((${innerStr})${exp}\\)`);
            } else {
                return protect(`\\(${innerStr}\\)`);
            }
        });

        // 5. Convert standalone Greek letters in prose to LaTeX (e.g. Γ -> \(\Gamma\))
        tempText = tempText.replace(/([ΓαβγδεθλμνπρστφψωΩΔ])/g, (match) => {
            if (match.includes('\uE000')) return match;
            const tex = greekMap[match] || match;
            return protect(`\\(${tex}\\)`);
        });

        // 5.5. Wrap un-delimited function-like TeX expressions (e.g. G(\mathbf{r}, \mathbf{r}'), \delta(\mathbf{r} - \mathbf{r}'), |\mathbf{r} - \mathbf{r}'|)
        tempText = tempText.replace(/(?:[a-zA-Z]*\\(?:hat|vec|mathbf|mathrm|text|tilde|bar)\{[^}]+\}[a-zA-Z0-9_\^']*(?:\([^)]+\))?|[a-zA-Z]+\(\\[a-zA-Z]+\{[^}]+\}[^)]*\)|\|(?:\\[a-zA-Z]+\{[^}]+\}|[a-zA-Z0-9_\^'\s\-\+\\to\format])+\|)/g, match => {
            if (match.includes('\uE000')) return match;
            return protect(`\\(${match.trim()}\\)`);
        });

        // 6. Wrap remaining un-delimited LaTeX backslash tokens (e.g. \frac{A}{B}, \rho, \nu, \to, \infty)
        tempText = tempText.replace(/(?:(?<!\\)\\([a-zA-Z]+)(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\([^)]*\)|\[[^\]]*\]|[a-zA-Z0-9_\^])*)/g, match => {
            if (match.includes('\uE000')) return match;
            let trimmed = match.trim();
            if (!trimmed) return match;
            let trailingPunct = '';
            const punctMatch = trimmed.match(/[,.;:\)]+$/);
            if (punctMatch) {
                trailingPunct = punctMatch[0];
                trimmed = trimmed.substring(0, trimmed.length - trailingPunct.length);
            }
            const wrapped = `\\(${trimmed}\\)${trailingPunct}`;
            return protect(wrapped);
        });

        // Restore placeholders and escape angle brackets inside math delimiters
        for (let i = 0; i < placeholders.length; i++) {
            let p = placeholders[i];
            if (p.startsWith('$') && !p.startsWith('$$') && p.endsWith('$')) {
                p = `\\(${p.slice(1, -1)}\\)`;
            }
            if (p.startsWith('\\(') && p.endsWith('\\)')) {
                p = p.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            }
            tempText = tempText.replace(`\uE000MATH_${i}\uE000`, () => p);
        }

        // Parse Markdown formatting (bold, italic, numbered list breaks)
        tempText = tempText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        tempText = tempText.replace(/(?<!\*)\*(?!\*)([^*]+)(?<!\*)\*(?!\*)/g, '<em>$1</em>');
        tempText = tempText.replace(/(?:\r?\n|\s)+(?=\d+\.\s+<strong>)/g, '<br><br>');

        return tempText;
    },

    synthesizeCustomOverview(latex) {
        let title = "Custom Physics Relation";
        let intro = "This mathematical expression represents a physical relation between variables.";
        let summary = "It is used to calculate the relative dynamics of the physical system.";
        let scenarios = [];

        // 0. Detect Static Limits of Maxwell's Equations
        if ((latex.includes('\\nabla \\times') || latex.includes('curl')) && (latex.includes('\\to 0') || latex.includes('=0') || latex.includes('\\to\\mathbf{0}')) && (latex.includes('\\mathbf{B}') || latex.includes('B'))) {
            title = "Static Limits of Maxwell's Equations";
            intro = "The steady-state or static limits of Maxwell's equations govern electromagnetic phenomena when charge distributions and currents are non-varying in time.";
            summary = "Under static conditions where fields do not change over time, the electric field is irrotational (curl-free), while magnetic fields are generated purely by steady electric current density.";
            scenarios = [
                {
                    condition: "Interpretation (Local Identity)",
                    implication: "In the static limit, the induced electric field from changing magnetic fields vanishes (\\nabla \\times \\mathbf{E} = 0), allowing the electric field to be represented as the gradient of a scalar electrostatic potential (\\mathbf{E} = -\\nabla V). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density (\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J})."
                },
                {
                    condition: "Symmetry & Coordinate Invariance",
                    implication: "Originates from time-translation invariance (\\partial / \\partial t = 0) and local gauge symmetry under steady current distributions."
                },
                {
                    condition: "Limiting Cases & Boundaries",
                    implication: "Valid in non-radiating, low-frequency, or zero-frequency steady-state electrodynamics where inductive and displacement currents are negligible."
                }
            ];
        }
        // 1. Detect Gauss's Law / Divergence
        else if (latex.includes('\\nabla \\cdot') || latex.includes('\\text{div}')) {
            title = "Vector Field Divergence Relation";
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
            title = "Vector Field Curl Relation";
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
            title = "Time-Dependent Evolution Relation";
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

        return { title, intro, summary, scenarios };
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
