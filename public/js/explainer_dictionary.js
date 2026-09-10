/**
 * 🪐 Physics Lab: Equation Explainer - Physical Variable & Symbol Dictionary
 * Canonical catalog of physical variables, constants, Greek letter symbols,
 * default SI units, physical descriptions, and fallback binders.
 */

const ExplainerDictionary = {
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
        // Core Operators & Differentials
        '\\partial': { name: 'Partial Derivative', type: 'operator', unit: 'operator', desc: 'Represents differentiation with respect to a single variable in multi-variable calculus.' },
        '\\nabla': { name: 'Del / Gradient Operator', type: 'operator', unit: 'operator', desc: 'The vector differential operator representing gradient, divergence, or curl.' },
        '\\Delta': { name: 'Laplacian / Change Operator', type: 'operator', unit: 'operator', desc: 'Denotes either a difference/change in a variable, or the second-order spatial derivative operator.' },
        '\\int': { name: 'Integral Operator', type: 'operator', unit: 'operator', desc: 'Represents continuous summation or the area under a curve.' },
        '\\oint': { name: 'Closed Loop Integral', type: 'operator', unit: 'operator', desc: 'Represents line or surface integration over a closed boundary.' },
        '\\sum': { name: 'Summation Operator', type: 'operator', unit: 'operator', desc: 'Represents discrete addition of a sequence of terms.' },
        '\\prod': { name: 'Product Operator', type: 'operator', unit: 'operator', desc: 'Represents discrete multiplication of a sequence of terms.' },
        '\\sqrt': { name: 'Square Root Operator', type: 'operator', unit: 'operator', desc: 'Represents the principal square root function, returning a number that, when multiplied by itself, yields the operand.' },
        '+': { name: 'Addition Operator', type: 'operator', unit: 'operator', desc: 'Adds mathematical values together.' },
        '-': { name: 'Subtraction Operator', type: 'operator', unit: 'operator', desc: 'Subtracts one mathematical value from another.' },
        '=': { name: 'Equality Relation', type: 'operator', unit: 'operator', desc: 'Asserts that two expressions have the exact same value.' },
        '/': { name: 'Division Operator', type: 'operator', unit: 'operator', desc: 'Denotes division or ratio between two values.' },

        // Logical & Set-Theoretic Operators
        '\\forall': { name: 'Universal Quantifier', type: 'operator', unit: 'logic', desc: 'Asserts that a predicate holds for all elements of a specified domain or set.' },
        '\\exists': { name: 'Existential Quantifier', type: 'operator', unit: 'logic', desc: 'Asserts that there exists at least one element in the domain satisfying the given predicate.' },
        '\\nexists': { name: 'Non-Existence Quantifier', type: 'operator', unit: 'logic', desc: 'Asserts that no element exists in the domain satisfying the given predicate.' },
        '\\in': { name: 'Set Membership', type: 'operator', unit: 'logic', desc: 'Denotes that an element belongs to or is contained within a specified set.' },
        '\\notin': { name: 'Set Non-Membership', type: 'operator', unit: 'logic', desc: 'Denotes that an element does not belong to a specified set.' },
        '\\ni': { name: 'Contains as Member', type: 'operator', unit: 'logic', desc: 'Denotes that a set contains a given element (reversed set membership).' },
        '\\subset': { name: 'Strict Subset', type: 'operator', unit: 'logic', desc: 'Denotes that a set is strictly contained within another set without being identical.' },
        '\\subseteq': { name: 'Subset or Equal', type: 'operator', unit: 'logic', desc: 'Denotes that a set is a subset of or equal to another set.' },
        '\\supset': { name: 'Strict Superset', type: 'operator', unit: 'logic', desc: 'Denotes that a set strictly contains another set.' },
        '\\supseteq': { name: 'Superset or Equal', type: 'operator', unit: 'logic', desc: 'Denotes that a set is a superset of or equal to another set.' },
        '\\cup': { name: 'Set Union', type: 'operator', unit: 'logic', desc: 'Combines all elements belonging to either or both sets.' },
        '\\cap': { name: 'Set Intersection', type: 'operator', unit: 'logic', desc: 'Selects elements that belong simultaneously to both sets.' },
        '\\setminus': { name: 'Set Difference', type: 'operator', unit: 'logic', desc: 'Removes all elements of one set from another set.' },
        '\\emptyset': { name: 'Empty Set', type: 'constant', unit: 'dimensionless', desc: 'The unique set containing no elements, denoted by ∅.' },
        '\\varnothing': { name: 'Empty Set', type: 'constant', unit: 'dimensionless', desc: 'The unique set containing no elements, denoted by ∅.' },
        '\\vdash': { name: 'Syntactic Entailment / Provability', type: 'operator', unit: 'logic', desc: 'Denotes that a formula is provable from a theory or set of axioms within a formal deductive system.' },
        '\\dashv': { name: 'Dual Turnstile', type: 'operator', unit: 'logic', desc: 'Relational logic turnstile representing reverse entailment or adjoint derivation.' },
        '\\models': { name: 'Semantic Entailment / Satisfaction', type: 'operator', unit: 'logic', desc: 'Denotes that every interpretation or model satisfying the premise also satisfies the conclusion.' },
        '\\vDash': { name: 'Double Turnstile / Model Satisfaction', type: 'operator', unit: 'logic', desc: 'Denotes semantic entailment where a model satisfies a formal proposition.' },
        '\\iff': { name: 'Material Biconditional (If and Only If)', type: 'operator', unit: 'logic', desc: 'Logical equivalence asserting that both propositions share the exact same truth value.' },
        '\\implies': { name: 'Material Implication', type: 'operator', unit: 'logic', desc: 'Logical conditional asserting that the truth of the antecedent entails the truth of the consequent.' },
        '\\Rightarrow': { name: 'Implication Arrow', type: 'operator', unit: 'logic', desc: 'Symbolic implication connecting antecedent and consequent.' },
        '\\Leftarrow': { name: 'Left Implication Arrow', type: 'operator', unit: 'logic', desc: 'Symbolic implication from right to left.' },
        '\\Leftrightarrow': { name: 'Equivalence Arrow', type: 'operator', unit: 'logic', desc: 'Symbolic biconditional connecting logically equivalent statements.' },
        '\\land': { name: 'Logical Conjunction (AND)', type: 'operator', unit: 'logic', desc: 'Logical operation that evaluates to true only if both operands are true.' },
        '\\lor': { name: 'Logical Disjunction (OR)', type: 'operator', unit: 'logic', desc: 'Logical operation that evaluates to true if at least one operand is true.' },
        '\\neg': { name: 'Logical Negation (NOT)', type: 'operator', unit: 'logic', desc: 'Inverts the truth value of a proposition.' },
        '\\lnot': { name: 'Logical Negation (NOT)', type: 'operator', unit: 'logic', desc: 'Inverts the truth value of a proposition.' },
        '\\equiv': { name: 'Equivalence Relation / Definition', type: 'operator', unit: 'operator', desc: 'Asserts identical mathematical equivalence, congruency, or definitional equality.' },
        '\\approx': { name: 'Approximation Relation', type: 'operator', unit: 'operator', desc: 'Denotes that two physical or mathematical quantities are approximately equal within acceptable tolerance.' },
        '\\propto': { name: 'Proportionality Relation', type: 'operator', unit: 'operator', desc: 'Denotes that two quantities vary in direct proportion to one another.' },
        '\\sim': { name: 'Asymptotic / Order of Magnitude Relation', type: 'operator', unit: 'operator', desc: 'Indicates asymptotic similarity, order-of-magnitude equivalence, or equivalence relation.' },
        '\\simeq': { name: 'Asymptotically Equal', type: 'operator', unit: 'operator', desc: 'Denotes asymptotic equality or isomorphism between mathematical objects.' },
        '\\cong': { name: 'Congruence / Isomorphism', type: 'operator', unit: 'operator', desc: 'Asserts geometric congruence or algebraic isomorphism.' },
        '\\le': { name: 'Less Than or Equal', type: 'operator', unit: 'operator', desc: 'Inequality relation asserting that the left operand is less than or equal to the right operand.' },
        '\\ge': { name: 'Greater Than or Equal', type: 'operator', unit: 'operator', desc: 'Inequality relation asserting that the left operand is greater than or equal to the right operand.' },
        '\\leq': { name: 'Less Than or Equal', type: 'operator', unit: 'operator', desc: 'Inequality relation asserting that the left operand is less than or equal to the right operand.' },
        '\\geq': { name: 'Greater Than or Equal', type: 'operator', unit: 'operator', desc: 'Inequality relation asserting that the left operand is greater than or equal to the right operand.' },
        '\\ne': { name: 'Inequality (Not Equal)', type: 'operator', unit: 'operator', desc: 'Asserts that two expressions are not equal.' },
        '\\neq': { name: 'Inequality (Not Equal)', type: 'operator', unit: 'operator', desc: 'Asserts that two expressions are not equal.' },
        '\\ll': { name: 'Much Less Than', type: 'operator', unit: 'operator', desc: 'Asymptotic inequality asserting that the left quantity is negligibly small compared to the right.' },
        '\\gg': { name: 'Much Greater Than', type: 'operator', unit: 'operator', desc: 'Asymptotic inequality asserting that the left quantity is orders of magnitude larger than the right.' },
        '\\pm': { name: 'Plus-Minus Operator', type: 'operator', unit: 'operator', desc: 'Indicates a dual solution or statistical uncertainty interval.' },
        '\\mp': { name: 'Minus-Plus Operator', type: 'operator', unit: 'operator', desc: 'Complementary dual solution symbol paired with plus-minus.' },
        '\\to': { name: 'Mapping / Limit Arrow', type: 'operator', unit: 'operator', desc: 'Denotes function mapping, state transition, or limiting convergence.' },
        '\\mapsto': { name: 'Maps To Element Relation', type: 'operator', unit: 'operator', desc: 'Denotes rule-based assignment from an element to its image.' },
        '\\Tr': { name: 'Trace Operator', type: 'operator', unit: 'operator', desc: 'The sum of the diagonal elements of a linear operator or density matrix.' },
        '\\det': { name: 'Determinant', type: 'operator', unit: 'operator', desc: 'A scalar value representing the scaling factor of the transformation described by a matrix.' },

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
        'o': {
            name: 'Origin / Offset',
            type: 'variable',
            unit: 'dimensionless',
            desc: 'The starting point of a coordinate system, or baseline shift.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Observation / Empirical Statement', type: 'variable', unit: 'event', desc: 'An individual observational sentence, proposition, or experimental measurement outcome.', domain: 'philosophy_of_physics' }
            ]
        },
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
                { name: 'Empirical Evidence Set', type: 'variable', unit: 'empirical_space', desc: 'The collection of verified empirical observations and experimental data supporting or falsifying a theoretical model.', domain: 'philosophy_of_physics' },
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
        'O': {
            name: 'Operator / Big O Notation',
            type: 'variable',
            unit: 'dimensionless',
            desc: 'A mathematical action performed on a state vector, or asymptotic growth boundary.',
            domain: 'classical_mechanics',
            alternatives: [
                { name: 'Observation Space / Observables Set', type: 'variable', unit: 'empirical_space', desc: 'The set of all possible empirical observation sentences or observable events.', domain: 'philosophy_of_physics' }
            ]
        },
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
                { name: 'Formal Theory / Axiom System', type: 'variable', unit: 'theoretical_structure', desc: 'A formal set of physical axioms and theoretical laws representing a physical paradigm.', domain: 'philosophy_of_physics' },
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
};

if (typeof window !== 'undefined') {
    window.ExplainerDictionary = ExplainerDictionary;
    if (window.EquationExplainer) {
        Object.assign(window.EquationExplainer, ExplainerDictionary);
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExplainerDictionary;
}
