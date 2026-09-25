import json
import os

DERIVATIONS = {
    ("app/config/content/formulas/10/shard_10.json", "wave-equation-physics-816dc899"): {
        "derivation_type": "DEDUCTION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
                "rationale": "Start with Faraday's law of induction in vacuum without magnetic monopoles."
            },
            {
                "step": 2,
                "latex": "\\nabla \\times (\\nabla \\times \\mathbf{E}) = -\\frac{\\partial}{\\partial t}(\\nabla \\times \\mathbf{B})",
                "rationale": "Take the curl of both sides and commute spatial derivatives with time differentiation."
            },
            {
                "step": 3,
                "latex": "\\nabla \\times (\\nabla \\times \\mathbf{E}) = \\nabla(\\nabla \\cdot \\mathbf{E}) - \\nabla^2 \\mathbf{E}",
                "rationale": "Apply the standard vector Laplacian identity for arbitrary 3D vector fields."
            },
            {
                "step": 4,
                "latex": "\\nabla \\cdot \\mathbf{E} = 0, \\quad \\nabla \\times \\mathbf{B} = \\mu_0 \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}",
                "rationale": "Substitute Gauss's law for electric charge in source-free vacuum ($\\rho=0$) and the Ampère-Maxwell law with zero conduction current ($\\mathbf{J}=0$)."
            },
            {
                "step": 5,
                "latex": "-\\nabla^2 \\mathbf{E} = -\\mu_0 \\varepsilon_0 \\frac{\\partial^2 \\mathbf{E}}{\\partial t^2} \\implies \\nabla^2 \\mathbf{E} - \\frac{1}{c^2}\\frac{\\partial^2 \\mathbf{E}}{\\partial t^2} = 0",
                "rationale": "Combine identities and equate the propagation speed to the speed of light $c = 1/\\sqrt{\\mu_0 \\varepsilon_0}$."
            }
        ]
    },
    ("app/config/content/formulas/7c/shard_7c.json", "local-energy-conservation-in-electromagnetism-7fd769fd"): {
        "derivation_type": "CONSERVATION_LAW",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}, \\quad \\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}",
                "rationale": "Begin with Maxwell's two curl equations describing time-varying electric and magnetic fields in the presence of current density $\\mathbf{J}$."
            },
            {
                "step": 2,
                "latex": "\\mathbf{B} \\cdot (\\nabla \\times \\mathbf{E}) - \\mathbf{E} \\cdot (\\nabla \\times \\mathbf{B}) = -\\mathbf{B} \\cdot \\frac{\\partial \\mathbf{B}}{\\partial t} - \\mu_0 \\mathbf{J} \\cdot \\mathbf{E} - \\mu_0 \\varepsilon_0 \\mathbf{E} \\cdot \\frac{\\partial \\mathbf{E}}{\\partial t}",
                "rationale": "Form the dot product of $\\mathbf{B}$ with Faraday's law and subtract the dot product of $\\mathbf{E}$ with the Ampère-Maxwell law."
            },
            {
                "step": 3,
                "latex": "\\nabla \\cdot (\\mathbf{E} \\times \\mathbf{B}) = \\mathbf{B} \\cdot (\\nabla \\times \\mathbf{E}) - \\mathbf{E} \\cdot (\\nabla \\times \\mathbf{B})",
                "rationale": "Invoke the vector calculus divergence product rule for the cross product of two vector fields."
            },
            {
                "step": 4,
                "latex": "\\nabla \\cdot (\\mathbf{E} \\times \\mathbf{B}) = -\\frac{1}{2}\\frac{\\partial}{\\partial t}\\left(\\mu_0 \\varepsilon_0 |\\mathbf{E}|^2 + |\\mathbf{B}|^2\\right) - \\mu_0 \\mathbf{J} \\cdot \\mathbf{E}",
                "rationale": "Express the time-derivative terms as derivatives of squared field amplitudes using $\\mathbf{F} \\cdot \\frac{\\partial \\mathbf{F}}{\\partial t} = \\frac{1}{2}\\frac{\\partial}{\\partial t}|\\mathbf{F}|^2$."
            },
            {
                "step": 5,
                "latex": "\\frac{\\partial}{\\partial t}\\left(\\frac{1}{2}\\varepsilon_0 E^2 + \\frac{1}{2\\mu_0} B^2\\right) + \\nabla \\cdot \\left(\\frac{1}{\\mu_0}\\mathbf{E} \\times \\mathbf{B}\\right) = -\\mathbf{J}\\cdot\\mathbf{E} \\implies \\frac{\\partial u}{\\partial t} + \\nabla \\cdot \\mathbf{S} = -\\mathbf{J}\\cdot\\mathbf{E}",
                "rationale": "Divide through by $\\mu_0$ and identify electromagnetic energy density $u$ and the Poynting flux vector $\\mathbf{S} = \\frac{1}{\\mu_0}(\\mathbf{E}\\times\\mathbf{B})$."
            }
        ]
    },
    ("app/config/content/formulas/bb/shard_bb.json", "dirac-equation-relativistic"): {
        "derivation_type": "FACTORIZATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "-\\hbar^2 \\partial_t^2 \\psi + c^2 \\hbar^2 \\nabla^2 \\psi - m^2 c^4 \\psi = 0 \\implies \\left(\\Box - \\frac{m^2 c^2}{\\hbar^2}\\right)\\psi = 0",
                "rationale": "Start from the relativistic energy-momentum invariant $E^2 = c^2 p^2 + m^2 c^4$ in the second-order Klein-Gordon differential representation."
            },
            {
                "step": 2,
                "latex": "(i\\hbar \\gamma^\\mu \\partial_\\mu - mc)(i\\hbar \\gamma^\\nu \\partial_\\nu + mc)\\psi = 0",
                "rationale": "Postulate a first-order linear differential operator ansatz that factors the second-order Klein-Gordon operator."
            },
            {
                "step": 3,
                "latex": "-\\hbar^2 \\gamma^\\mu \\gamma^\\nu \\partial_\\mu \\partial_\\nu - m^2 c^2 = -\\frac{\\hbar^2}{2}\\{\\gamma^\\mu, \\gamma^\\nu\\}\\partial_\\mu \\partial_\\nu - m^2 c^2",
                "rationale": "Expand the product and decompose the matrix operator into symmetric and antisymmetric spacetime index contributions under commuting partial derivatives."
            },
            {
                "step": 4,
                "latex": "\\{\\gamma^\\mu, \\gamma^\\nu\\} = 2\\eta^{\\mu\\nu} I_4",
                "rationale": "Enforce equality with the d'Alembertian $\\eta^{\\mu\\nu}\\partial_\\mu \\partial_\\nu$, requiring the four matrices $\\gamma^\\mu$ to satisfy the anticommutation relations of the Clifford algebra $\\mathrm{Cl}_{1,3}(\\mathbb{R})$."
            },
            {
                "step": 5,
                "latex": "(i\\hbar \\gamma^\\mu \\partial_\\mu - mc)\\psi = 0",
                "rationale": "Demand that each component of the four-component Dirac spinor $\\psi$ satisfies the linear factor, ensuring positive-definite probability density $\\rho = \\psi^\\dagger \\psi > 0$."
            }
        ]
    },
    ("app/config/content/formulas/61/shard_61.json", "algebraic-uncertainty-bound-9e7e0df3"): {
        "derivation_type": "DEDUCTION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\Delta \\hat{A} = \\hat{A} - \\langle \\hat{A} \\rangle, \\quad \\Delta \\hat{B} = \\hat{B} - \\langle \\hat{B} \\rangle \\implies [\\Delta \\hat{A}, \\Delta \\hat{B}] = [\\hat{A}, \\hat{B}]",
                "rationale": "Define shifted Hermitian deviation operators and note that scalar expectation value shifts leave the commutator invariant."
            },
            {
                "step": 2,
                "latex": "|\\langle \\psi | \\phi \\rangle|^2 \\le \\langle \\psi | \\psi \\rangle \\langle \\phi | \\phi \\rangle \\quad \\text{where} \\quad |\\psi\\rangle = \\Delta \\hat{A}|\\Psi\\rangle, \\; |\\phi\\rangle = \\Delta \\hat{B}|\\Psi\\rangle",
                "rationale": "Apply the Cauchy-Schwarz inequality in Hilbert space to the state vectors generated by the deviation operators."
            },
            {
                "step": 3,
                "latex": "\\langle \\Delta \\hat{A} \\Delta \\hat{B} \\rangle = \\frac{1}{2}\\langle \\{\\Delta \\hat{A}, \\Delta \\hat{B}\\} \\rangle + \\frac{1}{2}\\langle [\\Delta \\hat{A}, \\Delta \\hat{B}] \\rangle",
                "rationale": "Decompose the operator product into its Hermitian anticommutator and anti-Hermitian commutator components."
            },
            {
                "step": 4,
                "latex": "|\\langle \\Delta \\hat{A} \\Delta \\hat{B} \\rangle|^2 = \\frac{1}{4}|\\langle \\{\\Delta \\hat{A}, \\Delta \\hat{B}\\} \\rangle|^2 + \\frac{1}{4}|\\langle [\\hat{A}, \\hat{B}] \\rangle|^2 \\ge \\frac{1}{4}|\\langle [\\hat{A}, \\hat{B}] \\rangle|^2",
                "rationale": "Recognize that the expectation values of the anticommutator and commutator are purely real and purely imaginary respectively, rendering their modulus-squared additive."
            },
            {
                "step": 5,
                "latex": "\\sigma_A^2 \\sigma_B^2 \\ge |\\langle \\Delta \\hat{A} \\Delta \\hat{B} \\rangle|^2 \\ge \\frac{1}{4}|\\langle [\\hat{A}, \\hat{B}] \\rangle|^2 \\implies \\sigma_A \\sigma_B \\ge \\frac{1}{2}|\\langle [\\hat{A}, \\hat{B}] \\rangle|",
                "rationale": "Substitute the definitions of variance $\\sigma_A^2 = \\langle \\Delta \\hat{A}^2 \\rangle$ and take the positive square root to establish the general Robertson uncertainty bound."
            }
        ]
    },
    ("app/config/content/formulas/f4/shard_f4.json", "plancks-law"): {
        "derivation_type": "STATISTICAL_SUM",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "E_n = n h \\nu, \\quad n \\in \\{0, 1, 2, \\dots\\}",
                "rationale": "Postulate Planck's quantum hypothesis that electromagnetic cavity modes of frequency $\\nu$ exchange energy only in discrete packets of size $h\\nu$."
            },
            {
                "step": 2,
                "latex": "Z = \\sum_{n=0}^\\infty e^{-n h\\nu / (k_B T)} = \\frac{1}{1 - e^{-h\\nu / (k_B T)}}",
                "rationale": "Calculate the canonical partition function for a single oscillator mode using the sum of an infinite geometric series with ratio $e^{-h\\nu/k_B T} < 1$."
            },
            {
                "step": 3,
                "latex": "\\langle E \\rangle = -\\frac{\\partial \\ln Z}{\\partial \\beta} = \\frac{h\\nu e^{-h\\nu / (k_B T)}}{1 - e^{-h\\nu / (k_B T)}} = \\frac{h\\nu}{e^{h\\nu / (k_B T)} - 1}",
                "rationale": "Derive the mean energy per cavity mode from the logarithmic derivative of the partition function with respect to $\\beta = 1/k_B T$."
            },
            {
                "step": 4,
                "latex": "g(\\nu)\\,d\\nu = 2 \\cdot \\frac{4\\pi \\nu^2 V}{c^3}\\,d\\nu = \\frac{8\\pi \\nu^2 V}{c^3}\\,d\\nu",
                "rationale": "Determine the density of standing wave spatial modes per unit volume in a 3D box, including a factor of 2 for orthogonal transverse photon polarizations."
            },
            {
                "step": 5,
                "latex": "\\rho(\\nu, T)\\,d\\nu = \\frac{g(\\nu)}{V}\\langle E \\rangle\\,d\\nu \\implies \\rho(\\nu, T) = \\frac{8\\pi h \\nu^3}{c^3}\\frac{1}{e^{h\\nu / (k_B T)} - 1}",
                "rationale": "Multiply the spatial mode density by the average mode energy to produce the exact blackbody spectral energy density."
            }
        ]
    },
    ("app/config/content/formulas/87/shard_87.json", "carnot-efficiency-factor-47f8b746"): {
        "derivation_type": "THERMODYNAMIC_CYCLE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\eta = \\frac{W_{\\text{net}}}{Q_{\\text{in}}} = \\frac{Q_H - Q_C}{Q_H} = 1 - \\frac{Q_C}{Q_H}",
                "rationale": "Define thermal engine efficiency as the ratio of net mechanical work extracted to heat absorbed from the hot reservoir, invoking the First Law of Thermodynamics $W_{\\text{net}} = Q_H - Q_C$."
            },
            {
                "step": 2,
                "latex": "\\Delta S_{\\text{cycle}} = \\oint \\frac{\\delta Q_{\\text{rev}}}{T} = 0",
                "rationale": "Apply the Second Law of Thermodynamics to a fully reversible Carnot cycle, noting that entropy is a state function whose cyclic path integral vanishes."
            },
            {
                "step": 3,
                "latex": "\\oint \\frac{\\delta Q_{\\text{rev}}}{T} = \\frac{Q_H}{T_H} - \\frac{Q_C}{T_C} = 0",
                "rationale": "Evaluate the line integral along two reversible isotherms (at temperatures $T_H$ and $T_C$) and two reversible adiabats (where $\\delta Q = 0$)."
            },
            {
                "step": 4,
                "latex": "\\frac{Q_C}{Q_H} = \\frac{T_C}{T_H}",
                "rationale": "Equate the entropy input and output, establishing that the ratio of heat exchanged is directly proportional to absolute thermodynamic temperatures."
            },
            {
                "step": 5,
                "latex": "\\eta_{\\text{Carnot}} = 1 - \\frac{Q_C}{Q_H} = 1 - \\frac{T_{\\text{cold}}}{T_{\\text{hot}}}",
                "rationale": "Substitute the heat ratio into the thermal efficiency definition to obtain the universal upper bound for any heat engine operating between two thermal reservoirs."
            }
        ]
    },
    ("app/config/content/formulas/56/shard_56.json", "expansion-clock-26a3aced"): {
        "derivation_type": "GENERAL_RELATIVITY_SOL",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "ds^2 = -c^2 dt^2 + a^2(t)\\left[\\frac{dr^2}{1 - kr^2} + r^2(d\\theta^2 + \\sin^2\\theta\\,d\\phi^2)\\right]",
                "rationale": "Adopt the Friedmann-Lemaître-Robertson-Walker (FLRW) metric representing a spatially homogeneous and isotropic universe with curvature parameter $k \\in \\{-1, 0, +1\\}$."
            },
            {
                "step": 2,
                "latex": "\\Gamma^0_{ij} = \\frac{a\\dot{a}}{c^2} \\tilde{g}_{ij}, \\quad \\Gamma^i_{0j} = \\frac{\\dot{a}}{a}\\delta^i_j",
                "rationale": "Calculate the non-vanishing Christoffel connection coefficients from metric derivatives $\\Gamma^\\mu_{\\alpha\\beta} = \\frac{1}{2}g^{\\mu\\nu}(\\partial_\\alpha g_{\\beta\\nu} + \\partial_\\beta g_{\\alpha\\nu} - \\partial_\\nu g_{\\alpha\\beta})$."
            },
            {
                "step": 3,
                "latex": "R_{00} = -3\\frac{\\ddot{a}}{a}, \\quad R_{ij} = \\left[\\frac{\\ddot{a}}{a} + 2\\left(\\frac{\\dot{a}}{a}\\right)^2 + \\frac{2kc^2}{a^2}\\right]g_{ij}",
                "rationale": "Compute the components of the Ricci curvature tensor by contracting the Riemann curvature tensor $R_{\\mu\\nu} = R^\\alpha_{\\ \\mu\\alpha\\nu}$."
            },
            {
                "step": 4,
                "latex": "G_{00} = R_{00} - \\frac{1}{2}R g_{00} = 3\\left[\\left(\\frac{\\dot{a}}{a}\\right)^2 + \\frac{kc^2}{a^2}\\right]",
                "rationale": "Construct the time-time component of the Einstein tensor $G_{\\mu\\nu} = R_{\\mu\\nu} - \\frac{1}{2}R g_{\\mu\\nu}$."
            },
            {
                "step": 5,
                "latex": "T_{\\mu\\nu} = (\\rho + p/c^2)u_\\mu u_\\nu + p g_{\\mu\\nu} \\implies T_{00} = \\rho c^2",
                "rationale": "Model cosmic matter and energy as a comoving perfect fluid with rest-frame 4-velocity $u^\\mu = (c, 0, 0, 0)$ and total energy density $\\rho$."
            },
            {
                "step": 6,
                "latex": "G_{00} - \\Lambda c^2 g_{00} = \\frac{8\\pi G}{c^4} T_{00} \\implies H^2(t) = \\left(\\frac{\\dot{a}}{a}\\right)^2 = \\frac{8\\pi G}{3}\\rho - \\frac{kc^2}{a^2} + \\frac{\\Lambda c^2}{3}",
                "rationale": "Substitute $G_{00}$ and $T_{00}$ into Einstein's field equations with cosmological constant $\\Lambda$ and identify the Hubble expansion rate $H = \\dot{a}/a$."
            }
        ]
    },
    ("app/config/content/formulas/58/shard_58.json", "exact-gravitational-redshift-factor-schwarzschild-5a0de121"): {
        "derivation_type": "GEOMETRIC_RELATIVITY",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "ds^2 = -c^2 d\\tau^2 = -\\left(1 - \\frac{2GM}{c^2 r}\\right)c^2 dt^2 + \\left(1 - \\frac{2GM}{c^2 r}\\right)^{-1}dr^2 + r^2 d\\Omega^2",
                "rationale": "Consider the Schwarzschild metric describing the static, spherically symmetric spacetime exterior to a mass $M$."
            },
            {
                "step": 2,
                "latex": "d\\tau = \\sqrt{1 - \\frac{2GM}{c^2 r}} \\, dt",
                "rationale": "Enforce static rest conditions $dr = d\\theta = d\\phi = 0$ for a stationary observer or emitter at coordinate radius $r$, relating local proper time $\\tau$ to coordinate time $t$."
            },
            {
                "step": 3,
                "latex": "\\Delta t_e = \\Delta t_o",
                "rationale": "Note that because the Schwarzschild metric is static and time-translation invariant, light pulses emitted with coordinate time interval $\\Delta t_e$ arrive at an asymptotic observer with identical coordinate separation $\\Delta t_o$."
            },
            {
                "step": 4,
                "latex": "\\frac{\\nu_\\infty}{\\nu(r)} = \\frac{\\Delta \\tau(r)}{\\Delta \\tau_\\infty} = \\frac{\\sqrt{1 - \\frac{2GM}{c^2 r}}\\,\\Delta t}{\\Delta t} = \\sqrt{1 - \\frac{2GM}{c^2 r}}",
                "rationale": "Relate the emitted proper frequency $\\nu(r) = 1/\\Delta \\tau(r)$ to the observed frequency $\\nu_\\infty = 1/\\Delta \\tau_\\infty$ detected by a distant observer where $r \\to \\infty$."
            },
            {
                "step": 5,
                "latex": "1 + z = \\frac{\\nu(r)}{\\nu_\\infty} = \\frac{1}{\\sqrt{1 - \\frac{2GM}{c^2 r}}} \\implies z = \\frac{1}{\\sqrt{1 - 2GM/(rc^2)}} - 1",
                "rationale": "Use the kinematic redshift definition $z = (\\lambda_\\infty - \\lambda_e)/\\lambda_e = (\\nu_e - \\nu_\\infty)/\\nu_\\infty$ to obtain the exact general relativistic spectral shift."
            }
        ]
    },
    ("app/config/content/formulas/b7/shard_b7.json", "hamiltons-equations"): {
        "derivation_type": "LEGENDRE_TRANSFORMATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "dL = \\sum_i \\left( \\frac{\\partial L}{\\partial q_i} dq_i + \\frac{\\partial L}{\\partial \\dot{q}_i} d\\dot{q}_i \\right) + \\frac{\\partial L}{\\partial t} dt",
                "rationale": "Write the total differential of the Lagrangian $L(q_i, \\dot{q}_i, t)$ in generalized configuration velocity space."
            },
            {
                "step": 2,
                "latex": "p_i \\equiv \\frac{\\partial L}{\\partial \\dot{q}_i}, \\quad \\dot{p}_i = \\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) = \\frac{\\partial L}{\\partial q_i}",
                "rationale": "Define the canonical conjugate momentum $p_i$ and apply the Euler-Lagrange equations of motion to replace the generalized force term."
            },
            {
                "step": 3,
                "latex": "H(q_i, p_i, t) \\equiv \\sum_i p_i \\dot{q}_i - L(q_i, \\dot{q}_i, t)",
                "rationale": "Perform a Legendre transformation to transition from generalized velocities $\\dot{q}_i$ to generalized momenta $p_i$, defining the Hamiltonian state function."
            },
            {
                "step": 4,
                "latex": "dH = \\sum_i (p_i d\\dot{q}_i + \\dot{q}_i dp_i) - dL = \\sum_i (\\dot{q}_i dp_i - \\dot{p}_i dq_i) - \\frac{\\partial L}{\\partial t} dt",
                "rationale": "Calculate the total differential $dH$, substituting the expanded differential $dL$ and observing exact cancellation of all $d\\dot{q}_i$ terms."
            },
            {
                "step": 5,
                "latex": "dH = \\sum_i \\left(\\frac{\\partial H}{\\partial q_i} dq_i + \\frac{\\partial H}{\\partial p_i} dp_i\\right) + \\frac{\\partial H}{\\partial t} dt \\implies \\dot{q}_i = \\frac{\\partial H}{\\partial p_i}, \\quad \\dot{p}_i = -\\frac{\\partial H}{\\partial q_i}",
                "rationale": "Equate partial coefficients across independent coordinate variations $dq_i$ and momentum variations $dp_i$ to yield Hamilton's $2N$ first-order canonical equations of motion."
            }
        ]
    },
    ("app/config/content/formulas/73/shard_73.json", "virial-theorem"): {
        "derivation_type": "TIME_AVERAGING",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "G \\equiv \\sum_i \\mathbf{p}_i \\cdot \\mathbf{r}_i",
                "rationale": "Define the virial scalar moment $G$ for a discrete collection of interacting particles with positions $\\mathbf{r}_i$ and linear momenta $\\mathbf{p}_i$."
            },
            {
                "step": 2,
                "latex": "\\frac{dG}{dt} = \\sum_i \\dot{\\mathbf{p}}_i \\cdot \\mathbf{r}_i + \\sum_i \\mathbf{p}_i \\cdot \\dot{\\mathbf{r}}_i = \\sum_i \\mathbf{F}_i \\cdot \\mathbf{r}_i + \\sum_i m_i |\\dot{\\mathbf{r}}_i|^2",
                "rationale": "Take the total time derivative using the product rule and substitute Newton's second law $\\dot{\\mathbf{p}}_i = \\mathbf{F}_i$ and $\\mathbf{p}_i = m_i \\dot{\\mathbf{r}}_i$."
            },
            {
                "step": 3,
                "latex": "\\sum_i m_i |\\dot{\\mathbf{r}}_i|^2 = 2 \\sum_i \\frac{1}{2}m_i v_i^2 = 2K \\implies \\frac{dG}{dt} = 2K + \\sum_i \\mathbf{F}_i \\cdot \\mathbf{r}_i",
                "rationale": "Identify the total instantaneous kinetic energy $K$ of the multi-particle system."
            },
            {
                "step": 4,
                "latex": "\\langle \\frac{dG}{dt} \\rangle \\equiv \\lim_{\\tau \\to \\infty} \\frac{1}{\\tau} \\int_0^\\tau \\frac{dG}{dt} dt = \\lim_{\\tau \\to \\infty} \\frac{G(\\tau) - G(0)}{\\tau} = 0",
                "rationale": "Time-average the derivative over an extended duration $\\tau$, recognizing that for spatially bounded trajectories $G(t)$ remains finite, causing the asymptotic ratio to vanish."
            },
            {
                "step": 5,
                "latex": "\\mathbf{F}_i = -\\nabla_i U \\implies \\sum_i \\mathbf{r}_i \\cdot \\mathbf{F}_i = -k U = U \\implies 2\\langle K \\rangle + \\langle U \\rangle = 0",
                "rationale": "Apply Euler's homogeneous function theorem for inverse-square forces where potential energy $U \\propto r^{-1}$ has degree $k=-1$, yielding the classical virial equilibrium."
            }
        ]
    }
}

def apply_derivations():
    count = 0
    shards_to_write = {}
    for (shard_path, fid), update_data in DERIVATIONS.items():
        if shard_path not in shards_to_write:
            with open(shard_path, "r", encoding="utf-8") as f:
                shards_to_write[shard_path] = json.load(f)
        
        shard_dict = shards_to_write[shard_path]
        if fid in shard_dict:
            shard_dict[fid]["derivation_type"] = update_data["derivation_type"]
            shard_dict[fid]["derivation_steps"] = update_data["derivation_steps"]
            count += 1
            print(f"Updated {fid} in {shard_path}")
        else:
            print(f"ERROR: {fid} not in {shard_path}")

    for shard_path, shard_dict in shards_to_write.items():
        with open(shard_path, "w", encoding="utf-8") as f:
            json.dump(shard_dict, f, indent=4, ensure_ascii=False)
            f.write("\n")
    print(f"Successfully applied {count} derivation suites across {len(shards_to_write)} shards.")

if __name__ == "__main__":
    apply_derivations()
