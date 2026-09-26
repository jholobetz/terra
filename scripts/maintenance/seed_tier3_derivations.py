import json
import os

DERIVATIONS_TIER3 = {
    ("app/config/content/formulas/9b/shard_9b.json", "total-field-56c1f6d7"): {
        "derivation_type": "MAGNETOSTATIC_INTEGRATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}, \\quad \\nabla \\cdot \\mathbf{B} = 0 \\implies \\mathbf{B} = \\nabla \\times \\mathbf{A}",
                "rationale": "Start with the magnetostatic Maxwell equations and define the magnetic vector potential $\\mathbf{A}$ via the vanishing divergence condition."
            },
            {
                "step": 2,
                "latex": "\\nabla \\times (\\nabla \\times \\mathbf{A}) = \\nabla(\\nabla \\cdot \\mathbf{A}) - \\nabla^2 \\mathbf{A} = \\mu_0 \\mathbf{J} \\implies \\nabla^2 \\mathbf{A} = -\\mu_0 \\mathbf{J}",
                "rationale": "Impose the Coulomb gauge condition $\\nabla \\cdot \\mathbf{A} = 0$ to decouple the vector components into three independent Poisson equations."
            },
            {
                "step": 3,
                "latex": "\\mathbf{A}(\\mathbf{r}) = \\frac{\\mu_0}{4\\pi} \\int \\frac{\\mathbf{J}(\\mathbf{r}')}{|\\mathbf{r} - \\mathbf{r}'|} d^3 r'",
                "rationale": "Invert the vector Poisson equation using the standard 3D Green's function for the Laplacian operator."
            },
            {
                "step": 4,
                "latex": "\\mathbf{B}(\\mathbf{r}) = \\nabla \\times \\mathbf{A}(\\mathbf{r}) = \\frac{\\mu_0}{4\\pi} \\int \\nabla \\times \\left( \\frac{\\mathbf{J}(\\mathbf{r}')}{|\\mathbf{r} - \\mathbf{r}'|} \\right) d^3 r' = \\frac{\\mu_0}{4\\pi} \\int \\mathbf{J}(\\mathbf{r}') \\times \\frac{\\mathbf{r} - \\mathbf{r}'}{|\\mathbf{r} - \\mathbf{r}'|^3} d^3 r'",
                "rationale": "Compute the curl with respect to field coordinates $\\mathbf{r}$, applying vector cross-product derivatives."
            },
            {
                "step": 5,
                "latex": "\\mathbf{J}(\\mathbf{r}') d^3 r' \\to I d\\mathbf{l}' \\implies \\mathbf{B}(\\mathbf{r}) = \\frac{\\mu_0}{4\\pi} \\int_C \\frac{I d\\mathbf{l}' \\times (\\mathbf{r} - \\mathbf{r}')}{|\\mathbf{r} - \\mathbf{r}'|^3}",
                "rationale": "Specialize the volume current distribution to a thin line filament of steady current $I$ along curve $C$, yielding the Biot-Savart law."
            }
        ]
    },
    ("app/config/content/formulas/ec/shard_ec.json", "matrix-math-8b8a3af3"): {
        "derivation_type": "BOUNDARY_CONDITION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "r_p = \\frac{n_2 \\cos\\theta_1 - n_1 \\cos\\theta_2}{n_2 \\cos\\theta_1 + n_1 \\cos\\theta_2}",
                "rationale": "Begin with the Fresnel reflection amplitude coefficient $r_p$ for parallel-polarized ($p$-polarized or TM) electromagnetic radiation across a planar dielectric boundary."
            },
            {
                "step": 2,
                "latex": "r_p = 0 \\implies n_2 \\cos\\theta_1 = n_1 \\cos\\theta_2",
                "rationale": "Enforce complete transmission without reflection for $p$-polarized light at Brewster's angle of incidence $\\theta_1 = \\theta_B$."
            },
            {
                "step": 3,
                "latex": "n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2 \\implies \\frac{\\sin\\theta_1}{\\cos\\theta_1} = \\frac{\\sin\\theta_2}{\\cos\\theta_2} \\implies \\tan\\theta_1 = \\tan\\theta_2",
                "rationale": "Combine the reflection zero condition with Snell's law of refraction $n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2$."
            },
            {
                "step": 4,
                "latex": "\\sin(\\theta_1 + \\theta_2)\\cos(\\theta_1 - \\theta_2) = 0 \\implies \\theta_1 + \\theta_2 = \\frac{\\pi}{2} \\implies \\theta_2 = \\frac{\\pi}{2} - \\theta_1",
                "rationale": "Solve the trigonometric system, recognizing that the reflected and refracted rays must be mutually perpendicular, extinguishing dipolar re-radiation along the reflection axis."
            },
            {
                "step": 5,
                "latex": "n_1 \\sin\\theta_B = n_2 \\sin\\left(\\frac{\\pi}{2} - \\theta_B\\right) = n_2 \\cos\\theta_B \\implies \\tan\\theta_B = \\frac{n_2}{n_1} \\equiv n",
                "rationale": "Substitute $\\theta_2 = \\pi/2 - \\theta_B$ back into Snell's law to establish Brewster's law for the polarizing angle."
            }
        ]
    },
    ("app/config/content/formulas/57/shard_57.json", "unified-wave-3e179f6c"): {
        "derivation_type": "GAUGE_FIXING",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "F^{\\mu\\nu} = \\partial^\\mu A^\\nu - \\partial^\\nu A^\\mu",
                "rationale": "Express the electromagnetic field strength tensor $F^{\\mu\\nu}$ in terms of the four-potential $A^\\mu = (\\Phi/c, \\mathbf{A})$."
            },
            {
                "step": 2,
                "latex": "\\partial_\\mu F^{\\mu\\nu} = \\mu_0 J^\\nu \\implies \\partial_\\mu(\\partial^\\mu A^\\nu - \\partial^\\nu A^\\mu) = \\mu_0 J^\\nu",
                "rationale": "Substitute the field tensor definition into the covariant inhomogeneous Maxwell equations with four-current density $J^\\nu$."
            },
            {
                "step": 3,
                "latex": "\\partial_\\mu \\partial^\\mu A^\\nu - \\partial^\\nu(\\partial_\\mu A^\\mu) = \\mu_0 J^\\nu",
                "rationale": "Expand the derivatives and commute partial derivative operators $\\partial_\\mu \\partial^\\nu = \\partial^\\nu \\partial_\\mu$."
            },
            {
                "step": 4,
                "latex": "\\partial_\\mu A^\\mu = 0 \\quad (\\text{Lorenz Gauge Condition})",
                "rationale": "Impose the Lorenz gauge condition, which is manifestly Lorentz-invariant and eliminates the gradient divergence term."
            },
            {
                "step": 5,
                "latex": "\\Box A^\\nu = \\mu_0 J^\\nu \\xrightarrow{\\text{Vacuum } J^\\nu=0} \\Box A^\\mu = 0",
                "rationale": "Identify the d'Alembert wave operator $\\Box \\equiv \\partial_\\mu \\partial^\\mu = \\nabla^2 - \\frac{1}{c^2}\\partial_t^2$, establishing the decoupled homogeneous wave equation in vacuum."
            }
        ]
    },
    ("app/config/content/formulas/ad/shard_ad.json", "technical-relation-02b01ceb"): {
        "derivation_type": "SEMICLASSICAL_QUANTIZATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\frac{m_e v^2}{r} = \\frac{e^2}{4\\pi \\varepsilon_0 r^2} \\implies m_e v^2 r = \\frac{e^2}{4\\pi \\varepsilon_0}",
                "rationale": "Balance Coulomb electrostatic attraction against centripetal acceleration for an electron in a circular orbit of radius $r$ around a proton."
            },
            {
                "step": 2,
                "latex": "L = m_e v r = n \\hbar, \\quad n \\in \\{1, 2, 3, \\dots\\}",
                "rationale": "Postulate Bohr's quantization condition that orbital angular momentum $L$ occurs only in integer multiples of the reduced Planck constant $\\hbar$."
            },
            {
                "step": 3,
                "latex": "v = \\frac{n \\hbar}{m_e r} \\implies m_e \\left(\\frac{n \\hbar}{m_e r}\\right)^2 r = \\frac{e^2}{4\\pi \\varepsilon_0} \\implies r_n = \\frac{4\\pi \\varepsilon_0 \\hbar^2}{m_e e^2} n^2 \\equiv a_0 n^2",
                "rationale": "Substitute velocity $v$ into the orbital force balance to isolate the quantized orbital radius $r_n$ in terms of the Bohr radius $a_0$."
            },
            {
                "step": 4,
                "latex": "E = K + U = \\frac{1}{2}m_e v^2 - \\frac{e^2}{4\\pi \\varepsilon_0 r} = -\\frac{1}{2}\\frac{e^2}{4\\pi \\varepsilon_0 r}",
                "rationale": "Apply the Virial Theorem $2K + U = 0$ to express the total mechanical energy in terms of the orbital radius."
            },
            {
                "step": 5,
                "latex": "E_n = -\\frac{1}{2}\\frac{e^2}{4\\pi \\varepsilon_0 (a_0 n^2)} = -\\frac{m_e e^4}{32\\pi^2 \\varepsilon_0^2 \\hbar^2}\\frac{1}{n^2} \\approx -\\frac{13.6 \\text{ eV}}{n^2}",
                "rationale": "Substitute $r_n = a_0 n^2$ and evaluate physical constants to obtain the quantized Rydberg binding energy levels."
            }
        ]
    },
    ("app/config/content/formulas/03/shard_03.json", "free-waves-2fc9d212"): {
        "derivation_type": "CANONICAL_QUANTIZATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "E^2 = \\mathbf{p}^2 c^2 + m^2 c^4",
                "rationale": "Begin with Einstein's relativistic energy-momentum invariant for a free particle of rest mass $m$."
            },
            {
                "step": 2,
                "latex": "E \\to i\\hbar \\frac{\\partial}{\\partial t}, \\quad \\mathbf{p} \\to -i\\hbar \\nabla",
                "rationale": "Apply the standard Schrödinger quantum operator correspondence to energy and linear momentum."
            },
            {
                "step": 3,
                "latex": "-\\hbar^2 \\frac{\\partial^2 \\phi}{\\partial t^2} = -c^2 \\hbar^2 \\nabla^2 \\phi + m^2 c^4 \\phi",
                "rationale": "Promote the classical invariant to an operator eigenvalue equation acting on a scalar wave function $\\phi(\\mathbf{r}, t)$."
            },
            {
                "step": 4,
                "latex": "\\frac{1}{c^2}\\frac{\\partial^2 \\phi}{\\partial t^2} - \\nabla^2 \\phi + \\frac{m^2 c^2}{\\hbar^2}\\phi = 0",
                "rationale": "Divide through by $-c^2 \\hbar^2$ to arrange the equation in relativistic wave form with Compton wavenumber term."
            },
            {
                "step": 5,
                "latex": "\\Box \\equiv -\\partial_\\mu \\partial^\\mu = \\frac{1}{c^2}\\partial_t^2 - \\nabla^2 \\implies (\\Box + m^2)\\phi = 0 \\quad (\\text{Natural Units } c = \\hbar = 1)",
                "rationale": "Express the differential operators using the four-gradient d'Alembertian in natural units to obtain the canonical Klein-Gordon equation."
            }
        ]
    },
    ("app/config/content/formulas/55/shard_55.json", "fermi-golden-rule-interaction-024fbf64"): {
        "derivation_type": "TIME_DEPENDENT_PERTURBATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "i\\hbar \\frac{dc_f(t)}{dt} = H'_{fi} e^{i\\omega_{fi} t}, \\quad \\omega_{fi} \\equiv \\frac{E_f - E_i}{\\hbar}",
                "rationale": "Formulate the first-order Dirac time-dependent perturbation equation for transition amplitude $c_f(t)$ under perturbation $\\hat{H}'$."
            },
            {
                "step": 2,
                "latex": "c_f(t) = -\\frac{i}{\\hbar} H'_{fi} \\int_0^t e^{i\\omega_{fi} t'} dt' = -\\frac{H'_{fi}}{\\hbar} \\frac{e^{i\\omega_{fi} t} - 1}{\\omega_{fi}}",
                "rationale": "Integrate from initial time $t=0$ where $c_i(0)=1$ and $c_f(0)=0$ under a constant perturbation turned on at $t=0$."
            },
            {
                "step": 3,
                "latex": "P_{i \\to f}(t) = |c_f(t)|^2 = \\frac{|H'_{fi}|^2}{\\hbar^2} \\frac{4\\sin^2(\\omega_{fi} t / 2)}{\\omega_{fi}^2} = \\frac{|H'_{fi}|^2 t^2}{\\hbar^2} \\text{sinc}^2\\left(\\frac{\\omega_{fi} t}{2}\\right)",
                "rationale": "Calculate the transition probability as the squared modulus of the complex probability amplitude."
            },
            {
                "step": 4,
                "latex": "\\lim_{t \\to \\infty} \\frac{\\sin^2(\\omega t / 2)}{\\pi t (\\omega / 2)^2} = \\delta(\\omega) = \\hbar \\delta(E_f - E_i)",
                "rationale": "Utilize the standard representation of the Dirac delta distribution in the asymptotic long-time limit $t \\to \\infty$."
            },
            {
                "step": 5,
                "latex": "\\Gamma_{i \\to f} \\equiv \\frac{dP_{i \\to f}}{dt} = \\lim_{t \\to \\infty} \\frac{P_{i \\to f}(t)}{t} = \\frac{2\\pi}{\\hbar} |\\langle f | \\hat{H}' | i \\rangle|^2 \\delta(E_f - E_i)",
                "rationale": "Differentiate with respect to time to extract the steady-state transition rate per unit time, establishing Fermi's Golden Rule."
            }
        ]
    },
    ("app/config/content/formulas/ac/shard_ac.json", "maxwell-boltzmann-speed-distribution"): {
        "derivation_type": "PHASE_SPACE_INTEGRATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "f(\\mathbf{v}) \\, d^3 v = C \\exp\\left(-\\frac{E(\\mathbf{v})}{k_B T}\\right) d^3 v = C \\exp\\left(-\\frac{m(v_x^2 + v_y^2 + v_z^2)}{2 k_B T}\\right) dv_x dv_y dv_z",
                "rationale": "Start with the 3D canonical Boltzmann distribution for classical gas particles of mass $m$ in thermal equilibrium at temperature $T$."
            },
            {
                "step": 2,
                "latex": "\\int_{-\\infty}^\\infty \\dots \\int_{-\\infty}^\\infty f(\\mathbf{v}) d^3 v = 1 \\implies C \\left(\\int_{-\\infty}^\\infty e^{-m v_x^2 / 2k_B T} dv_x\\right)^3 = C \\left(\\frac{2\\pi k_B T}{m}\\right)^{3/2} = 1",
                "rationale": "Normalize the 3D distribution using the product of three independent Gaussian integrals."
            },
            {
                "step": 3,
                "latex": "C = \\left(\\frac{m}{2\\pi k_B T}\\right)^{3/2} \\implies f(\\mathbf{v}) = \\left(\\frac{m}{2\\pi k_B T}\\right)^{3/2} e^{-m v^2 / 2k_B T}",
                "rationale": "Solve for the normalization constant $C$, establishing the isotropic 3D velocity distribution function."
            },
            {
                "step": 4,
                "latex": "d^3 v = v^2 \\sin\\theta \\, dv \\, d\\theta \\, d\\phi \\implies \\int_{\\text{angles}} d^3 v = 4\\pi v^2 dv",
                "rationale": "Transform from Cartesian velocity coordinates to spherical speed coordinates and integrate over all solid angles."
            },
            {
                "step": 5,
                "latex": "f(v)\\,dv = \\left(\\int_{\\Omega} f(\\mathbf{v})\\,d\\Omega\\right) v^2 dv = 4\\pi v^2 \\left(\\frac{m}{2\\pi k_B T}\\right)^{3/2} e^{-mv^2 / 2k_B T} dv",
                "rationale": "Multiply the isotropic distribution by the spherical shell volume element $4\\pi v^2 dv$ to obtain the scalar speed distribution."
            }
        ]
    },
    ("app/config/content/formulas/ab/shard_ab.json", "dimensional-reduction-42f3bbfb"): {
        "derivation_type": "CANONICAL_ENSEMBLE_AVERAGE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "H(q, p) = \\sum_{i=1}^n a_i x_i^2 + H_{\\text{other}}",
                "rationale": "Consider a classical Hamiltonian system where each particle possesses $n$ independent quadratic degrees of freedom $x_i$ in coordinates or momenta."
            },
            {
                "step": 2,
                "latex": "\\langle x_i \\frac{\\partial H}{\\partial x_j} \\rangle = \\frac{1}{Z}\\int x_i \\frac{\\partial H}{\\partial x_j} e^{-\\beta H} d\\Gamma, \\quad \\beta \\equiv \\frac{1}{k_B T}",
                "rationale": "Express the statistical ensemble expectation value in terms of phase-space volume element $d\\Gamma$ and partition function $Z$."
            },
            {
                "step": 3,
                "latex": "\\frac{\\partial H}{\\partial x_j} e^{-\\beta H} = -\\frac{1}{\\beta}\\frac{\\partial}{\\partial x_j}(e^{-\\beta H})",
                "rationale": "Rewrite the integrand using the chain rule derivative of the Boltzmann exponential factor."
            },
            {
                "step": 4,
                "latex": "\\int_{-\\infty}^\\infty x_i \\frac{\\partial}{\\partial x_i}(e^{-\\beta H}) dx_i = \\left[x_i e^{-\\beta H}\\right]_{-\\infty}^\\infty - \\int_{-\\infty}^\\infty e^{-\\beta H} dx_i = - \\int_{-\\infty}^\\infty e^{-\\beta H} dx_i",
                "rationale": "Perform integration by parts on degree of freedom $x_i$, observing that physical boundary terms vanish exponentially as $|x_i| \\to \\infty$."
            },
            {
                "step": 5,
                "latex": "\\langle a_i x_i^2 \\rangle = \\frac{1}{2}\\langle x_i \\frac{\\partial H}{\\partial x_i} \\rangle = \\frac{1}{2\\beta} = \\frac{1}{2}k_B T \\implies U = N \\sum_{i=1}^n \\langle \\varepsilon_i \\rangle = \\frac{1}{2} n N k_B T",
                "rationale": "Sum across all $n$ quadratic degrees of freedom for $N$ non-interacting particles to establish the equipartition internal energy."
            }
        ]
    },
    ("app/config/content/formulas/9a/shard_9a.json", "recombination-era-identity-1-f2d0deec-439586e5"): {
        "derivation_type": "CHEMICAL_POTENTIAL_EQUILIBRIUM",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "p + e^- \\rightleftharpoons H + \\gamma \\implies \\mu_p + \\mu_e = \\mu_H",
                "rationale": "Enforce thermodynamic and chemical equilibrium for hydrogen recombination/ionization, matching Gibbs chemical potentials."
            },
            {
                "step": 2,
                "latex": "n_i = g_i \\left(\\frac{m_i k_B T}{2\\pi \\hbar^2}\\right)^{3/2} \\exp\\left(\\frac{\\mu_i - m_i c^2}{k_B T}\\right)",
                "rationale": "Express non-relativistic ideal gas number densities $n_i$ in terms of internal degeneracy factors $g_i$, thermal de Broglie volumes, and rest-mass energies."
            },
            {
                "step": 3,
                "latex": "\\frac{n_p n_e}{n_H} = \\frac{g_p g_e}{g_H}\\left(\\frac{m_e k_B T}{2\\pi \\hbar^2}\\right)^{3/2}\\exp\\left(-\\frac{(m_p + m_e - m_H)c^2}{k_B T}\\right)",
                "rationale": "Form the equilibrium quotient, eliminating chemical potentials via $\\mu_p + \\mu_e = \\mu_H$ and canceling proton mass factors using $m_p \\approx m_H$."
            },
            {
                "step": 4,
                "latex": "g_p = 2, \\; g_e = 2, \\; g_H = 4 \\implies \\frac{g_p g_e}{g_H} = 1, \\quad (m_p + m_e - m_H)c^2 = E_I = 13.6\\text{ eV}",
                "rationale": "Count spin degeneracy degrees of freedom for protons, electrons, and ground-state hydrogen, identifying ground ionization energy $E_I$."
            },
            {
                "step": 5,
                "latex": "n_p = n_e = X_e n_b, \\; n_H = (1 - X_e)n_b \\implies \\frac{X_e^2}{1 - X_e} = \\frac{1}{n_b}\\left(\\frac{m_e k_B T}{2\\pi \\hbar^2}\\right)^{3/2} \\exp\\left(-\\frac{E_I}{k_B T}\\right)",
                "rationale": "Substitute the fractional ionization $X_e \\equiv n_e/n_b$ in terms of baryon density $n_b$ to yield the canonical cosmological Saha equation."
            }
        ]
    },
    ("app/config/content/formulas/03/shard_03.json", "geodesic-equation-in-general-relativity-e9a37d9e"): {
        "equation": "\\frac{d^2 x^\\mu}{d\\tau^2} + \\Gamma^\\mu_{\\alpha\\beta} \\frac{d x^\\alpha}{d\\tau} \\frac{d x^\\beta}{d\\tau} = 0",
        "derivation_type": "VARIATIONAL_PRINCIPLE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "S = -m c \\int d\\tau = -m c \\int \\sqrt{-g_{\\mu\\nu}(x)\\dot{x}^\\mu \\dot{x}^\\nu} \\, d\\lambda \\quad (\\dot{x}^\\mu \\equiv dx^\\mu/d\\lambda)",
                "rationale": "Formulate the action $S$ for a free point particle of mass $m$ traversing curved spacetime, extremizing proper time $\\tau$ parameterized by affine parameter $\\lambda$."
            },
            {
                "step": 2,
                "latex": "L(x, \\dot{x}) = \\frac{1}{2}g_{\\mu\\nu}(x)\\dot{x}^\\mu \\dot{x}^\\nu",
                "rationale": "Adopt the equivalent quadratic Lagrangian along affine parameterization where $d\\tau = d\\lambda$, generating identical extremal worldlines $\\delta S = 0$."
            },
            {
                "step": 3,
                "latex": "\\frac{\\partial L}{\\partial x^\\sigma} = \\frac{1}{2}(\\partial_\\sigma g_{\\mu\\nu})\\dot{x}^\\mu \\dot{x}^\\nu, \\quad \\frac{\\partial L}{\\partial \\dot{x}^\\sigma} = g_{\\sigma\\mu}\\dot{x}^\\mu",
                "rationale": "Compute the functional derivatives of the Lagrangian with respect to spacetime coordinates and four-velocities."
            },
            {
                "step": 4,
                "latex": "\\frac{d}{d\\tau}\\left(\\frac{\\partial L}{\\partial \\dot{x}^\\sigma}\\right) - \\frac{\\partial L}{\\partial x^\\sigma} = 0 \\implies g_{\\sigma\\mu}\\ddot{x}^\\mu + (\\partial_\\alpha g_{\\sigma\\mu})\\dot{x}^\\alpha \\dot{x}^\\mu - \\frac{1}{2}(\\partial_\\sigma g_{\\mu\\nu})\\dot{x}^\\mu \\dot{x}^\\nu = 0",
                "rationale": "Apply the Euler-Lagrange equations and expand the total proper time derivative using the chain rule $\\frac{d}{d\\tau}g_{\\sigma\\mu} = (\\partial_\\alpha g_{\\sigma\\mu})\\dot{x}^\\alpha$."
            },
            {
                "step": 5,
                "latex": "g_{\\sigma\\mu}\\ddot{x}^\\mu + \\frac{1}{2}(\\partial_\\alpha g_{\\sigma\\beta} + \\partial_\\beta g_{\\sigma\\alpha} - \\partial_\\sigma g_{\\alpha\\beta})\\dot{x}^\\alpha \\dot{x}^\\beta = 0 \\implies \\ddot{x}^\\mu + \\Gamma^\\mu_{\\alpha\\beta}\\dot{x}^\\alpha \\dot{x}^\\beta = 0",
                "rationale": "Symmetrize indices, contract with the inverse metric $g^{\\rho\\sigma}$, and identify the Christoffel symbols of the second kind $\\Gamma^\\mu_{\\alpha\\beta}$ to yield the geodesic equation."
            }
        ]
    },
    ("app/config/content/formulas/f7/shard_f7.json", "relativistic-edge-6bd78c24"): {
        "derivation_type": "RADIATION_HYDROSTATIC_BALANCE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "F_{\\text{rad}} = \\frac{\\sigma_T S}{c} = \\frac{\\sigma_T L}{4\\pi r^2 c}",
                "rationale": "Calculate the outward radiative force exerted on a free electron via Thomson scattering with cross-section $\\sigma_T$ in radiation field of luminosity $L$ and flux $S = L/(4\\pi r^2)$."
            },
            {
                "step": 2,
                "latex": "F_{\\text{grav}} = \\frac{G M (m_p + m_e)}{r^2} \\approx \\frac{G M m_p}{r^2}",
                "rationale": "Determine the inward gravitational force acting on an electron-proton pair in fully ionized hydrogen gas, dominated by proton mass $m_p \\gg m_e$."
            },
            {
                "step": 3,
                "latex": "F_{\\text{rad}} = F_{\\text{grav}} \\implies \\frac{\\sigma_T L}{4\\pi r^2 c} = \\frac{G M m_p}{r^2}",
                "rationale": "Equate outward radiation pressure force to inward gravitational attraction at the boundary of hydrostatic equilibrium."
            },
            {
                "step": 4,
                "latex": "\\frac{\\sigma_T L_{\\text{Edd}}}{4\\pi c} = G M m_p",
                "rationale": "Observe that the radial distance squared $r^2$ cancels identically from both sides of the balance equation, making the stability limit independent of radius."
            },
            {
                "step": 5,
                "latex": "L_{\\text{Edd}} = \\frac{4\\pi G M m_p c}{\\sigma_T}",
                "rationale": "Isolate the critical luminosity $L_{\\text{Edd}}$ beyond which radiation pressure overcomes gravity, causing radiant blowout of stellar atmospheres or accretion disks."
            }
        ]
    },
    ("app/config/content/formulas/26/shard_26.json", "geometric-bending-32fd3f54"): {
        "derivation_type": "NULL_GEODESIC_PERMISSIBLE",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\frac{d^2 u}{d\\phi^2} + u = \\frac{3 G M}{c^2} u^2 \\quad \\left(u \\equiv \\frac{1}{r}\\right)",
                "rationale": "Formulate the Binet orbit equation for null geodesics ($ds^2 = 0$) in the equatorial plane ($\\theta = \\pi/2$) of the Schwarzschild metric."
            },
            {
                "step": 2,
                "latex": "u_0(\\phi) = \\frac{\\sin\\phi}{b} \\implies \\frac{d^2 u_0}{d\\phi^2} + u_0 = 0",
                "rationale": "Establish the unperturbed zeroth-order straight-line trajectory with impact parameter $b$ in the absence of gravity ($M=0$)."
            },
            {
                "step": 3,
                "latex": "u(\\phi) = u_0(\\phi) + u_1(\\phi) \\implies \\frac{d^2 u_1}{d\\phi^2} + u_1 = \\frac{3 G M}{c^2 b^2}\\sin^2\\phi",
                "rationale": "Apply first-order perturbation theory, inserting the zeroth-order straight-line solution into the nonlinear general relativistic curvature source term."
            },
            {
                "step": 4,
                "latex": "u_1(\\phi) = \\frac{G M}{c^2 b^2}(1 + 2\\cos^2\\phi) \\implies u(\\phi) \\approx \\frac{\\sin\\phi}{b} + \\frac{G M}{c^2 b^2}(1 + \\cos^2\\phi)",
                "rationale": "Solve the driven harmonic oscillator differential equation for the first-order perturbation $u_1(\\phi)$ with asymptotic boundary conditions."
            },
            {
                "step": 5,
                "latex": "r \\to \\infty \\implies u(\\phi) = 0 \\implies -\\epsilon + \\frac{2GM}{c^2 b} = 0 \\implies \\delta\\theta = 2\\epsilon = \\frac{4GM}{c^2 b}",
                "rationale": "Locate incoming and outgoing asymptotic ray directions where $u \\to 0$, doubling the deflection angle across both asymptotes to obtain Einstein's relativistic gravitational light bending."
            }
        ]
    }
}

def apply_tier3_derivations():
    count = 0
    shards_to_write = {}
    for (shard_path, fid), update_data in DERIVATIONS_TIER3.items():
        if shard_path not in shards_to_write:
            with open(shard_path, "r", encoding="utf-8") as f:
                shards_to_write[shard_path] = json.load(f)
        
        shard_dict = shards_to_write[shard_path]
        if fid in shard_dict:
            shard_dict[fid]["derivation_type"] = update_data["derivation_type"]
            shard_dict[fid]["derivation_steps"] = update_data["derivation_steps"]
            if "equation" in update_data:
                shard_dict[fid]["equation"] = update_data["equation"]
            count += 1
            print(f"Updated {fid} in {shard_path}")
        else:
            print(f"ERROR: {fid} not in {shard_path}")

    for shard_path, shard_dict in shards_to_write.items():
        with open(shard_path, "w", encoding="utf-8") as f:
            json.dump(shard_dict, f, indent=4, ensure_ascii=False)
            f.write("\n")
    print(f"Successfully applied {count} Tier 3 derivation suites across {len(shards_to_write)} shards.")

if __name__ == "__main__":
    apply_tier3_derivations()
