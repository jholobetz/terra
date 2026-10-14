import json
import os

DERIVATIONS_TIER4 = {
    ("app/config/content/formulas/9c/shard_9c.json", "noether-rule-58a13a95"): {
        "derivation_type": "CONTINUOUS_SYMMETRY_INVARIANCE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\phi(x) \\to \\phi'(x) = \\phi(x) + \\alpha \\, \\delta\\phi(x) \\implies \\delta S = \\int d^4 x \\, \\delta\\mathcal{L} = 0",
                "rationale": "Consider an infinitesimal continuous global symmetry transformation parameterized by constant $\\alpha$, leaving the action integral invariant."
            },
            {
                "step": 2,
                "latex": "\\delta\\mathcal{L} = \\frac{\\partial \\mathcal{L}}{\\partial \\phi}\\delta\\phi + \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\delta(\\partial_\\mu \\phi)",
                "rationale": "Compute the first-order variation of the Lagrangian density $\\mathcal{L}(\\phi, \\partial_\\mu \\phi)$ under the field variation."
            },
            {
                "step": 3,
                "latex": "\\delta(\\partial_\\mu \\phi) = \\partial_\\mu(\\delta\\phi), \\quad \\frac{\\partial \\mathcal{L}}{\\partial \\phi} = \\partial_\\mu\\left(\\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\right)",
                "rationale": "Commute variation with spacetime derivatives and substitute the Euler-Lagrange equations of motion for field $\\phi$."
            },
            {
                "step": 4,
                "latex": "\\delta\\mathcal{L} = \\partial_\\mu\\left(\\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\right)\\delta\\phi + \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\partial_\\mu(\\delta\\phi) = \\partial_\\mu\\left[\\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\delta\\phi\\right]",
                "rationale": "Combine the two terms into a total spacetime four-divergence via the product rule."
            },
            {
                "step": 5,
                "latex": "J^\\mu \\equiv \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)}\\delta\\phi \\implies \\partial_\\mu J^\\mu = 0",
                "rationale": "Define the Noether four-current $J^\\mu$, demonstrating that symmetry invariance $\\delta\\mathcal{L} = 0$ implies exact local four-current conservation."
            }
        ]
    },
    ("app/config/content/formulas/de/shard_de.json", "higgs-kibble-mechanism-identity-1-246b2a79-548a3047"): {
        "derivation_type": "SPONTANEOUS_SYMMETRY_BREAKING",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\mathcal{L} = -\\frac{1}{4}F_{\\mu\\nu}F^{\\mu\\nu} + |D_\\mu \\phi|^2 - V(\\phi), \\quad V(\\phi) = -\\mu^2|\\phi|^2 + \\lambda|\\phi|^4 \\quad (\\mu^2 > 0)",
                "rationale": "Start with the Abelian $U(1)$ gauge Higgs Lagrangian with Mexican-hat scalar potential $V(\\phi)$ and covariant derivative $D_\\mu = \\partial_\\mu - i g A_\\mu$."
            },
            {
                "step": 2,
                "latex": "\\frac{\\partial V}{\\partial |\\phi|} = 0 \\implies |\\phi_0| = \\sqrt{\\frac{\\mu^2}{2\\lambda}} \\equiv \\frac{v}{\\sqrt{2}}",
                "rationale": "Calculate the degenerate ring of vacuum expectation values that minimizes potential energy, spontaneously breaking $U(1)$ symmetry."
            },
            {
                "step": 3,
                "latex": "\\phi(x) = \\frac{1}{\\sqrt{2}}\\left(v + h(x)\\right)e^{i\\theta(x)/v} \\xrightarrow{\\text{Unitary Gauge}} \\phi(x) = \\frac{1}{\\sqrt{2}}\\left(v + h(x)\\right)",
                "rationale": "Choose the unitary gauge where the Goldstone phase $\\theta(x)$ is gauged away, being eaten by the gauge field."
            },
            {
                "step": 4,
                "latex": "|D_\\mu \\phi|^2 = \\left|\\left(\\partial_\\mu - ig A_\\mu\\right)\\frac{v + h}{\\sqrt{2}}\\right|^2 = \\frac{1}{2}(\\partial_\\mu h)^2 + \\frac{1}{2}g^2 v^2 A_\\mu A^\\mu + g^2 v h A_\\mu A^\\mu + \\frac{1}{2}g^2 h^2 A_\\mu A^\\mu",
                "rationale": "Expand the scalar kinetic term in the unitary gauge around the classical vacuum expectation value $v$."
            },
            {
                "step": 5,
                "latex": "\\mathcal{L}_{\\text{mass}} = \\frac{1}{2}(g v)^2 A_\\mu A^\\mu \\equiv \\frac{1}{2}m_A^2 A_\\mu A^\\mu \\implies m_A = g v",
                "rationale": "Identify the quadratic gauge field mass term from the vacuum coupling, demonstrating that the gauge boson acquires physical mass $m_A = g v$."
            }
        ]
    },
    ("app/config/content/formulas/66/shard_66.json", "classical-yukawa-potential-pole-7e982f85"): {
        "derivation_type": "GREENS_FUNCTION_INVERSION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "(\\nabla^2 - \\mu^2)\\phi(\\mathbf{r}) = g \\delta^3(\\mathbf{r}) \\quad \\left(\\mu \\equiv \\frac{mc}{\\hbar}\\right)",
                "rationale": "Consider the static limit of the Klein-Gordon field equation sourced by a point coupling charge $g$ at the origin, with inverse Compton screening length $\\mu$."
            },
            {
                "step": 2,
                "latex": "\\frac{1}{r}\\frac{d^2}{dr^2}(r \\phi) - \\mu^2 \\phi = 0 \\quad (r > 0)",
                "rationale": "Express the Laplacian in spherically symmetric radial coordinates away from the point source at $r=0$."
            },
            {
                "step": 3,
                "latex": "u(r) \\equiv r \\phi(r) \\implies \\frac{d^2 u}{dr^2} - \\mu^2 u = 0 \\implies u(r) = A e^{-\\mu r} + B e^{+\\mu r}",
                "rationale": "Solve the homogeneous second-order linear radial differential equation."
            },
            {
                "step": 4,
                "latex": "\\lim_{r \\to \\infty} \\phi(r) = 0 \\implies B = 0 \\implies \\phi(r) = A \\frac{e^{-\\mu r}}{r}",
                "rationale": "Enforce asymptotic decay boundary conditions at infinity, discarding the unphysical exponentially diverging solution."
            },
            {
                "step": 5,
                "latex": "\\lim_{\\mu \\to 0} \\nabla^2 \\phi = g \\delta^3(\\mathbf{r}) \\implies A = -\\frac{g}{4\\pi} \\implies V(r) \\propto -g^2 \\frac{e^{-\\mu r}}{r}",
                "rationale": "Match the short-range limit $r \\to 0$ to the Coulomb Poisson Green's function to determine normalization, establishing the screened Yukawa potential."
            }
        ]
    },
    ("app/config/content/formulas/02/shard_02.json", "yang-mills-curvature-general-3f6b1546"): {
        "derivation_type": "COVARIANT_COMMUTATOR",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "D_\\mu = \\partial_\\mu - i g A_\\mu = \\partial_\\mu - i g A^a_\\mu T^a",
                "rationale": "Define the gauge-covariant derivative acting on matter fields transforming under a non-Abelian Lie group with generators $[T^a, T^b] = i f^{abc} T^c$."
            },
            {
                "step": 2,
                "latex": "[D_\\mu, D_\\nu]\\psi = \\left[(\\partial_\\mu - ig A_\\mu)(\\partial_\\nu - ig A_\\nu) - (\\partial_\\nu - ig A_\\nu)(\\partial_\\mu - ig A_\\mu)\\right]\\psi",
                "rationale": "Compute the commutator of two covariant derivatives acting on an arbitrary matter field $\\psi$."
            },
            {
                "step": 3,
                "latex": "[D_\\mu, D_\\nu] = -ig\\left(\\partial_\\mu A_\\nu - \\partial_\\nu A_\\mu - ig[A_\\mu, A_\\nu]\\right) \\equiv -ig F_{\\mu\\nu}",
                "rationale": "Expand derivative terms using the product rule and observe exact cancellation of all undifferentiated field derivatives."
            },
            {
                "step": 4,
                "latex": "A_\\mu = A^b_\\mu T^b, \\; A_\\nu = A^c_\\nu T^c \\implies [A_\\mu, A_\\nu] = A^b_\\mu A^c_\\nu [T^b, T^c] = i f^{abc} A^b_\\mu A^c_\\nu T^a",
                "rationale": "Decompose the gauge connection matrices into Lie algebra generator components using group structure constants $f^{abc}$."
            },
            {
                "step": 5,
                "latex": "F_{\\mu\\nu} = F^a_{\\mu\\nu}T^a \\implies F^a_{\\mu\\nu} = \\partial_\\mu A^a_\\nu - \\partial_\\nu A^a_\\mu + g f^{abc} A^b_\\mu A^c_\\nu",
                "rationale": "Extract generator coefficients to establish the Yang-Mills field strength tensor, featuring nonlinear self-interaction terms."
            }
        ]
    },
    ("app/config/content/formulas/a6/shard_a6.json", "debye-specific-heat-90ea8693"): {
        "derivation_type": "PHONON_DENSITY_OF_STATES",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "g(\\omega) = \\frac{3V\\omega^2}{2\\pi^2 v_s^3}, \\quad \\int_0^{\\omega_D} g(\\omega)\\,d\\omega = 3N \\implies \\omega_D = v_s\\left(6\\pi^2\\frac{N}{V}\\right)^{1/3}",
                "rationale": "Adopt Debye's continuum model of acoustic phonons with linear dispersion $\\omega = v_s k$, cut off at Debye frequency $\\omega_D$ to normalize total vibrational modes to $3N$."
            },
            {
                "step": 2,
                "latex": "U(T) = \\int_0^{\\omega_D} \\frac{\\hbar\\omega}{e^{\\hbar\\omega/k_B T} - 1} g(\\omega)\\,d\\omega = \\frac{9N\\hbar}{\\omega_D^3}\\int_0^{\\omega_D} \\frac{\\omega^3}{e^{\\hbar\\omega/k_B T} - 1}\\,d\\omega",
                "rationale": "Integrate the Planck harmonic oscillator energy over the density of vibrational states to find the total internal thermal lattice energy."
            },
            {
                "step": 3,
                "latex": "x \\equiv \\frac{\\hbar\\omega}{k_B T}, \\quad x_D \\equiv \\frac{\\hbar\\omega_D}{k_B T} = \\frac{\\Theta_D}{T} \\implies U(T) = 9N k_B T \\left(\\frac{T}{\\Theta_D}\\right)^3 \\int_0^{x_D} \\frac{x^3}{e^x - 1}\\,dx",
                "rationale": "Transform to dimensionless variable $x$, defining the characteristic Debye temperature $\\Theta_D \\equiv \\hbar\\omega_D / k_B$."
            },
            {
                "step": 4,
                "latex": "T \\ll \\Theta_D \\implies x_D \\to \\infty, \\quad \\int_0^\\infty \\frac{x^3}{e^x - 1}\\,dx = \\frac{\\pi^4}{15} \\implies U(T) \\approx \\frac{3\\pi^4}{5} N k_B T \\left(\\frac{T}{\\Theta_D}\\right)^3",
                "rationale": "Take the low-temperature limit $T \\ll \\Theta_D$ where the upper integration bound extends to infinity, evaluating the Riemann zeta integral."
            },
            {
                "step": 5,
                "latex": "C_V \\equiv \\frac{\\partial U}{\\partial T} = \\frac{\\partial}{\\partial T}\\left[\\frac{3\\pi^4}{5} N k_B \\frac{T^4}{\\Theta_D^3}\\right] = \\frac{12\\pi^4}{5} N k_B \\left(\\frac{T}{\\Theta_D}\\right)^3",
                "rationale": "Differentiate internal energy with respect to temperature to establish Debye's $T^3$ lattice heat capacity law."
            }
        ]
    },
    ("app/config/content/formulas/bb/shard_bb.json", "london-equation-8bf340c8"): {
        "derivation_type": "SUPERCONDUCTING_ELECTRODYNAMICS",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "m_s \\frac{d\\mathbf{v}_s}{dt} = q_s \\mathbf{E} \\implies \\frac{\\partial \\mathbf{J}_s}{\\partial t} = \\frac{n_s q_s^2}{m_s}\\mathbf{E} \\quad (\\text{First London Equation})",
                "rationale": "Model superconducting carriers of mass $m_s$, charge $q_s$, and density $n_s$ accelerating without resistance under an applied electric field, where $\\mathbf{J}_s = n_s q_s \\mathbf{v}_s$."
            },
            {
                "step": 2,
                "latex": "\\frac{\\partial}{\\partial t}(\\nabla \\times \\mathbf{J}_s) = \\frac{n_s q_s^2}{m_s}(\\nabla \\times \\mathbf{E}) = -\\frac{n_s q_s^2}{m_s}\\frac{\\partial \\mathbf{B}}{\\partial t}",
                "rationale": "Take the curl of both sides and substitute Faraday's law of electromagnetic induction $\\nabla \\times \\mathbf{E} = -\\partial\\mathbf{B}/\\partial t$."
            },
            {
                "step": 3,
                "latex": "\\nabla \\times \\mathbf{J}_s = -\\frac{n_s q_s^2}{m_s}\\mathbf{B} \\quad (\\text{Second London Equation})",
                "rationale": "Integrate with respect to time and set the integration constant to zero, embodying the Meissner effect where static interior magnetic flux is expelled."
            },
            {
                "step": 4,
                "latex": "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}_s \\implies \\nabla \\times (\\nabla \\times \\mathbf{B}) = \\mu_0 (\\nabla \\times \\mathbf{J}_s) = -\\frac{\\mu_0 n_s q_s^2}{m_s}\\mathbf{B}",
                "rationale": "Take the curl of Ampère's circuital law in magnetostatic equilibrium and substitute the Second London Equation."
            },
            {
                "step": 5,
                "latex": "\\nabla \\times (\\nabla \\times \\mathbf{B}) = \\nabla(\\nabla \\cdot \\mathbf{B}) - \\nabla^2 \\mathbf{B} = -\\nabla^2 \\mathbf{B} \\implies \\nabla^2 \\mathbf{B} = \\frac{1}{\\lambda_L^2}\\mathbf{B}, \\quad \\lambda_L \\equiv \\sqrt{\\frac{m_s}{\\mu_0 n_s q_s^2}}",
                "rationale": "Apply $\\nabla \\cdot \\mathbf{B} = 0$ to arrive at the Helmholtz screening equation, demonstrating exponential magnetic flux expulsion with London penetration depth $\\lambda_L$."
            }
        ]
    },
    ("app/config/content/formulas/54/shard_54.json", "superconducting-gap-equation-ident-4f2aa7e5"): {
        "derivation_type": "BOGOLIUBOV_VALATIN_TRANSFORMATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "H_{\\text{BCS}} = \\sum_{\\mathbf{k}\\sigma} \\xi_{\\mathbf{k}} c_{\\mathbf{k}\\sigma}^\\dagger c_{\\mathbf{k}\\sigma} + \\sum_{\\mathbf{k}\\mathbf{k}'} V_{\\mathbf{k}\\mathbf{k}'} c_{\\mathbf{k}\\uparrow}^\\dagger c_{-\\mathbf{k}\\downarrow}^\\dagger c_{-\\mathbf{k}'\\downarrow} c_{\\mathbf{k}'\\uparrow}",
                "rationale": "Formulate the effective reduced BCS pairing Hamiltonian with attractive phonon-mediated interaction $V_{\\mathbf{k}\\mathbf{k}'} < 0$ between time-reversed electron pairs."
            },
            {
                "step": 2,
                "latex": "\\Delta_{\\mathbf{k}} \\equiv -\\sum_{\\mathbf{k}'} V_{\\mathbf{k}\\mathbf{k}'} \\langle c_{-\\mathbf{k}'\\downarrow} c_{\\mathbf{k}'\\uparrow} \\rangle",
                "rationale": "Apply mean-field approximation, defining the pairing order parameter gap $\\Delta_{\\mathbf{k}}$ from the Cooper pair expectation value."
            },
            {
                "step": 3,
                "latex": "\\gamma_{\\mathbf{k}0} = u_{\\mathbf{k}} c_{\\mathbf{k}\\uparrow} - v_{\\mathbf{k}} c_{-\\mathbf{k}\\downarrow}^\\dagger, \\quad \\gamma_{\\mathbf{k}1}^\\dagger = v_{\\mathbf{k}} c_{\\mathbf{k}\\uparrow} + u_{\\mathbf{k}} c_{-\\mathbf{k}\\downarrow}^\\dagger",
                "rationale": "Perform the Bogoliubov-Valatin canonical transformation to diagonalize the mean-field Hamiltonian into free fermionic Bogoliubov quasiparticles."
            },
            {
                "step": 4,
                "latex": "E_{\\mathbf{k}} = \\sqrt{\\xi_{\\mathbf{k}}^2 + |\\Delta_{\\mathbf{k}}|^2}, \\quad u_{\\mathbf{k}} v_{\\mathbf{k}} = \\frac{\\Delta_{\\mathbf{k}}}{2E_{\\mathbf{k}}}",
                "rationale": "Obtain the quasiparticle dispersion relation $E_{\\mathbf{k}}$ with energy gap $\\Delta_{\\mathbf{k}}$ and determine the coherence factor product $u_{\\mathbf{k}} v_{\\mathbf{k}}$."
            },
            {
                "step": 5,
                "latex": "\\langle c_{-\\mathbf{k}\\downarrow} c_{\\mathbf{k}\\uparrow} \\rangle = u_{\\mathbf{k}} v_{\\mathbf{k}} \\xrightarrow{T=0} \\frac{\\Delta_{\\mathbf{k}}}{2E_{\\mathbf{k}}} \\implies \\Delta_{\\mathbf{k}} = -\\sum_{\\mathbf{k}'} V_{\\mathbf{k}\\mathbf{k}'} \\frac{\\Delta_{\\mathbf{k}'}}{2E_{\\mathbf{k}'}}",
                "rationale": "Substitute coherence factors into the gap definition at zero temperature to establish the self-consistent BCS gap integral equation."
            }
        ]
    },
    ("app/config/content/formulas/21/shard_21.json", "hall-conductivity-quantization-law-5524fc65"): {
        "derivation_type": "TKNN_TOPOLOGICAL_INVARIANT",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\hat{H} = \\frac{1}{2m}(\\mathbf{p} + e\\mathbf{A})^2 \\implies E_n = \\left(n + \\frac{1}{2}\\right)\\hbar\\omega_c, \\quad \\omega_c \\equiv \\frac{eB}{m}",
                "rationale": "Solve the 2D Schrödinger equation in a perpendicular magnetic field $B$ using the Landau gauge, yielding discrete, highly degenerate Landau levels."
            },
            {
                "step": 2,
                "latex": "N_{\\Phi} = \\frac{B A}{\\Phi_0} = \\frac{e B A}{h} \\implies n_B = \\frac{eB}{h}",
                "rationale": "Calculate the total degenerate orbital capacity per unit area for each filled Landau level in terms of the magnetic flux quantum $\\Phi_0 = h/e$."
            },
            {
                "step": 3,
                "latex": "j_x = -e n_e v_d, \\quad \\mathbf{E} + \\mathbf{v}_d \\times \\mathbf{B} = 0 \\implies v_d = \\frac{E_y}{B}",
                "rationale": "Balance the transverse electric Hall force against the Lorentz magnetic force, finding the uniform guiding-center drift velocity $v_d$."
            },
            {
                "step": 4,
                "latex": "j_x = -e(\\nu n_B)\\left(-\\frac{E_y}{B}\\right) = \\nu e \\left(\\frac{eB}{h}\\right)\\frac{E_y}{B} = \\nu \\frac{e^2}{h} E_y",
                "rationale": "Express the 2D areal carrier density as $n_e = \\nu n_B$ where $\\nu \\in \\mathbb{Z}$ represents the integer number of fully occupied Landau levels."
            },
            {
                "step": 5,
                "latex": "\\sigma_{xy} \\equiv \\frac{j_x}{E_y} = \\nu \\frac{e^2}{h} \\equiv n \\frac{e^2}{h} \\quad (n \\in \\mathbb{Z})",
                "rationale": "Isolate the Hall conductivity $\\sigma_{xy}$, demonstrating that it is topologically quantized in integer multiples of the fundamental conductance quantum $e^2/h$."
            }
        ]
    },
    ("app/config/content/formulas/be/shard_be.json", "navier-stokes-momentum-viscous-form-7b93eee6"): {
        "derivation_type": "CAUCHY_CONTINUUM_MOMENTUM",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\rho \\frac{D\\mathbf{v}}{Dt} = \\rho\\left[\\frac{\\partial \\mathbf{v}}{\\partial t} + (\\mathbf{v}\\cdot\\nabla)\\mathbf{v}\\right] = \\nabla \\cdot \\boldsymbol{\\sigma} + \\mathbf{f}",
                "rationale": "Start with Cauchy's momentum equation for continuum mechanics, relating material acceleration to internal stress tensor $\\boldsymbol{\\sigma}$ and body forces $\\mathbf{f}$."
            },
            {
                "step": 2,
                "latex": "\\boldsymbol{\\sigma} = -P \\mathbf{I} + \\boldsymbol{\\tau}",
                "rationale": "Decompose the total stress tensor into isotropic thermodynamic pressure $P$ and viscous deviatoric shear stress tensor $\\boldsymbol{\\tau}$."
            },
            {
                "step": 3,
                "latex": "\\tau_{ij} = 2\\mu \\varepsilon_{ij} + \\lambda (\\nabla \\cdot \\mathbf{v})\\delta_{ij}, \\quad \\varepsilon_{ij} = \\frac{1}{2}\\left(\\frac{\\partial v_i}{\\partial x_j} + \\frac{\\partial v_j}{\\partial x_i}\\right)",
                "rationale": "Apply the Stokesian constitutive relation for an isotropic Newtonian fluid, expressing viscous stress in terms of dynamic shear viscosity $\\mu$, bulk viscosity $\\lambda$, and strain rate $\\varepsilon_{ij}$."
            },
            {
                "step": 4,
                "latex": "\\nabla \\cdot \\boldsymbol{\\tau} = \\mu \\nabla^2 \\mathbf{v} + (\\lambda + \\mu)\\nabla(\\nabla \\cdot \\mathbf{v})",
                "rationale": "Compute the divergence of the viscous stress tensor, grouping the vector Laplacian and velocity divergence gradient terms."
            },
            {
                "step": 5,
                "latex": "\\rho \\left( \\frac{\\partial \\mathbf{v}}{\\partial t} + (\\mathbf{v} \\cdot \\nabla)\\mathbf{v} \\right) = -\\nabla P + \\mu \\nabla^2 \\mathbf{v} + (\\lambda + \\mu) \\nabla (\\nabla \\cdot \\mathbf{v}) + \\mathbf{f}",
                "rationale": "Assemble the pressure gradient, viscous dissipation, and external body force terms to establish the full compressible Navier-Stokes momentum equation."
            }
        ]
    },
    ("app/config/content/formulas/9c/shard_9c.json", "tov-equation-identity-1-6e8eb3b1-43637a35"): {
        "derivation_type": "EINSTEIN_FIELD_SOL",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "ds^2 = -e^{2\\Phi(r)} c^2 dt^2 + \\left(1 - \\frac{2GM(r)}{c^2 r}\\right)^{-1}dr^2 + r^2 d\\Omega^2, \\quad M(r) = \\int_0^r 4\\pi r'^2 \\rho(r') dr'",
                "rationale": "Adopt the static, spherically symmetric interior metric line element sourced by enclosed gravitational mass $M(r)$."
            },
            {
                "step": 2,
                "latex": "T^\\mu_{\\ \\nu} = \\text{diag}(-\\rho c^2, P, P, P)",
                "rationale": "Represent interior stellar matter as a static perfect fluid with energy density $\\rho(r)$ and isotropic pressure $P(r)$."
            },
            {
                "step": 3,
                "latex": "\\nabla_\\mu T^\\mu_{\\ r} = 0 \\implies \\frac{dP}{dr} = -(\\rho c^2 + P)\\frac{d\\Phi}{dr}",
                "rationale": "Enforce local energy-momentum conservation $\\nabla_\\mu T^{\\mu\\nu} = 0$, relating the radial pressure gradient to the metric potential gradient $d\\Phi/dr$."
            },
            {
                "step": 4,
                "latex": "G^r_{\\ r} = \\frac{8\\pi G}{c^4} T^r_{\\ r} \\implies \\frac{d\\Phi}{dr} = \\frac{G}{c^2 r^2}\\left[M(r) + \\frac{4\\pi r^3 P}{c^2}\\right]\\left(1 - \\frac{2GM(r)}{c^2 r}\\right)^{-1}",
                "rationale": "Solve the radial Einstein field equation $G^r_{\\ r} = \\frac{8\\pi G}{c^4} P$ to determine the gravitational metric acceleration potential $d\\Phi/dr$."
            },
            {
                "step": 5,
                "latex": "\\frac{dP}{dr} = -\\frac{G M(r) \\rho}{r^2} \\left(1 + \\frac{P}{\\rho c^2}\\right)\\left(1 + \\frac{4\\pi r^3 P}{M(r)c^2}\\right)\\left(1 - \\frac{2GM(r)}{c^2 r}\\right)^{-1}",
                "rationale": "Substitute $d\\Phi/dr$ into the radial pressure gradient to establish the Tolman-Oppenheimer-Volkoff relativistic hydrostatic equilibrium equation."
            }
        ]
    },
    ("app/config/content/formulas/bb/shard_bb.json", "hawking-temperature-schwarzschild"): {
        "derivation_type": "HORIZON_SURFACE_GRAVITY",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "ds^2 = -\\left(1 - \\frac{2GM}{c^2 r}\\right)c^2 dt^2 + \\left(1 - \\frac{2GM}{c^2 r}\\right)^{-1}dr^2 + r^2 d\\Omega^2",
                "rationale": "Consider the exterior Schwarzschild metric with event horizon radius $r_s = 2GM/c^2$."
            },
            {
                "step": 2,
                "latex": "\\kappa \\equiv \\lim_{r \\to r_s} \\frac{1}{2\\sqrt{-g_{00} g_{rr}}}\\left|\\frac{\\partial g_{00}}{\\partial r}\\right| = \\frac{c^2}{4GM}",
                "rationale": "Calculate the black hole event horizon surface gravity $\\kappa$, measuring the redshifted acceleration required to hold a test mass at the horizon."
            },
            {
                "step": 3,
                "latex": "t \\to -i \\tau_E \\implies ds^2 = \\left(1 - \\frac{r_s}{r}\\right)c^2 d\\tau_E^2 + \\left(1 - \\frac{r_s}{r}\\right)^{-1}dr^2",
                "rationale": "Perform Wick rotation to Euclidean signature spacetime with imaginary time coordinate $\\tau_E$."
            },
            {
                "step": 4,
                "latex": "\\rho \\equiv \\sqrt{r - r_s} \\implies ds^2 \\approx \\rho^2 \\left(\\frac{\\kappa}{c}\\right)^2 d\\tau_E^2 + \\left(\\frac{2 c^2}{\\kappa}\\right)^2 d\\rho^2 \\implies \\Delta\\tau_E = \\frac{2\\pi c}{\\kappa}",
                "rationale": "Expand near the horizon $\\rho \\to 0$ into standard 2D polar coordinates, identifying the required thermal Euclidean time period $\\beta_E = 2\\pi c/\\kappa$ to eliminate conical singularities."
            },
            {
                "step": 5,
                "latex": "k_B T_H = \\frac{\\hbar}{\\beta_E} = \\frac{\\hbar \\kappa}{2\\pi c} = \\frac{\\hbar c^3}{8\\pi G M} \\implies T_H = \\frac{\\hbar c^3}{8\\pi G M k_B}",
                "rationale": "Relate the Euclidean periodicity to KMS thermal equilibrium temperature, establishing Hawking's black hole radiation temperature."
            }
        ]
    },
    ("app/config/content/formulas/69/shard_69.json", "friedmann-acceleration-equation-expansion-4aa65f2c"): {
        "derivation_type": "GENERAL_RELATIVITY_SOL",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "H^2 = \\left(\\frac{\\dot{a}}{a}\\right)^2 = \\frac{8\\pi G}{3}\\rho - \\frac{kc^2}{a^2} + \\frac{\\Lambda c^2}{3}",
                "rationale": "Start with the First Friedmann Equation governing cosmic expansion in the FLRW metric."
            },
            {
                "step": 2,
                "latex": "\\dot{\\rho} + 3\\frac{\\dot{a}}{a}\\left(\\rho + \\frac{P}{c^2}\\right) = 0 \\implies \\dot{\\rho} = -3\\frac{\\dot{a}}{a}\\left(\\rho + \\frac{P}{c^2}\\right)",
                "rationale": "Apply the continuity equation of cosmic thermodynamics arising from local conservation of stress-energy $\\nabla_\\mu T^{\\mu\\nu} = 0$."
            },
            {
                "step": 3,
                "latex": "\\frac{d}{dt}\\left(\\dot{a}^2\\right) = 2\\dot{a}\\ddot{a} = \\frac{d}{dt}\\left[\\frac{8\\pi G}{3}\\rho a^2 - kc^2 + \\frac{\\Lambda c^2}{3}a^2\\right]",
                "rationale": "Differentiate the First Friedmann Equation multiplied through by $a^2$ with respect to cosmic time $t$."
            },
            {
                "step": 4,
                "latex": "2\\dot{a}\\ddot{a} = \\frac{8\\pi G}{3}(\\dot{\\rho} a^2 + 2a\\dot{a}\\rho) + \\frac{2\\Lambda c^2}{3}a\\dot{a}",
                "rationale": "Expand the derivatives using the product rule and observe that spatial curvature constant $k$ drops out completely."
            },
            {
                "step": 5,
                "latex": "2\\dot{a}\\ddot{a} = \\frac{8\\pi G}{3}\\left[-3 a\\dot{a}\\left(\\rho + \\frac{P}{c^2}\\right) + 2a\\dot{a}\\rho\\right] + \\frac{2\\Lambda c^2}{3}a\\dot{a} \\implies \\frac{\\ddot{a}}{a} = -\\frac{4\\pi G}{3c^2}(\\rho c^2 + 3P) + \\frac{\\Lambda c^2}{3}",
                "rationale": "Substitute $\\dot{\\rho}$ and divide both sides by $2a\\dot{a}$ to isolate the cosmic acceleration parameter $\\ddot{a}/a$, yielding the Second Friedmann Equation."
            }
        ]
    }
}

def apply_tier4_derivations():
    count = 0
    shards_to_write = {}
    for (shard_path, fid), update_data in DERIVATIONS_TIER4.items():
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
    print(f"Successfully applied {count} Tier 4 derivation suites across {len(shards_to_write)} shards.")

if __name__ == "__main__":
    apply_tier4_derivations()
