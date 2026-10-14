import json
import os

DERIVATIONS_TIER2 = {
    ("app/config/content/formulas/ef/shard_ef.json", "snells-law-of-refraction-74d97afe"): {
        "derivation_type": "VARIATIONAL_MINIMIZATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "t(x) = \\frac{\\sqrt{a^2 + x^2}}{v_1} + \\frac{\\sqrt{b^2 + (d - x)^2}}{v_2}",
                "rationale": "Express the total optical travel time $t$ for a light ray propagating from $(0, a)$ in medium 1 to $(d, -b)$ in medium 2 crossing the interface at horizontal position $x$, invoking Fermat's Principle of Least Time."
            },
            {
                "step": 2,
                "latex": "v_1 = \\frac{c}{n_1}, \\quad v_2 = \\frac{c}{n_2} \\implies t(x) = \\frac{n_1}{c}\\sqrt{a^2 + x^2} + \\frac{n_2}{c}\\sqrt{b^2 + (d - x)^2}",
                "rationale": "Relate propagation velocities to media refractive indices $n_1$ and $n_2$ relative to vacuum light speed $c$."
            },
            {
                "step": 3,
                "latex": "\\frac{dt}{dx} = \\frac{n_1}{c}\\frac{x}{\\sqrt{a^2 + x^2}} - \\frac{n_2}{c}\\frac{d - x}{\\sqrt{b^2 + (d - x)^2}} = 0",
                "rationale": "Differentiate total travel time with respect to the interface crossing coordinate $x$ and set the derivative to zero for stationary action $\\delta \\int dt = 0$."
            },
            {
                "step": 4,
                "latex": "\\sin \\theta_1 = \\frac{x}{\\sqrt{a^2 + x^2}}, \\quad \\sin \\theta_2 = \\frac{d - x}{\\sqrt{b^2 + (d - x)^2}}",
                "rationale": "Identify geometric sines of the angles of incidence $\\theta_1$ and refraction $\\theta_2$ with respect to the interface normal."
            },
            {
                "step": 5,
                "latex": "\\frac{n_1}{c}\\sin\\theta_1 - \\frac{n_2}{c}\\sin\\theta_2 = 0 \\implies n_1 \\sin\\theta_1 = n_2 \\sin\\theta_2",
                "rationale": "Multiply through by $c$ to obtain the canonical invariant relation governing wave refraction across dielectric interfaces."
            }
        ]
    },
    ("app/config/content/formulas/51/shard_51.json", "larmor-formula-aa594928"): {
        "derivation_type": "INTEGRATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\mathbf{E}_{\\text{rad}}(\\mathbf{r}, t) = \\frac{q}{4\\pi \\varepsilon_0 c^2}\\frac{\\hat{\\mathbf{n}} \\times (\\hat{\\mathbf{n}} \\times \\mathbf{a})}{r}, \\quad \\mathbf{B}_{\\text{rad}} = \\frac{1}{c}(\\hat{\\mathbf{n}} \\times \\mathbf{E}_{\\text{rad}})",
                "rationale": "Extract the asymptotic $1/r$ acceleration radiation fields from the Liénard-Wiechert potentials in the non-relativistic limit $\\beta \\ll 1$."
            },
            {
                "step": 2,
                "latex": "|\\mathbf{E}_{\\text{rad}}| = \\frac{q a \\sin\\theta}{4\\pi \\varepsilon_0 c^2 r}",
                "rationale": "Evaluate the transverse field magnitude, where $\\theta$ denotes the polar angle between the acceleration vector $\\mathbf{a}$ and observation unit vector $\\hat{\\mathbf{n}}$."
            },
            {
                "step": 3,
                "latex": "\\mathbf{S} = \\frac{1}{\\mu_0}(\\mathbf{E} \\times \\mathbf{B}) \\implies |\\mathbf{S}| = \\frac{1}{\\mu_0 c}|\\mathbf{E}_{\\text{rad}}|^2 = \\frac{q^2 a^2 \\sin^2\\theta}{16\\pi^2 \\varepsilon_0 c^3 r^2}",
                "rationale": "Compute the outward radial energy flux using the Poynting vector magnitude and the vacuum impedance relation $\\mu_0 c = 1/(\\varepsilon_0 c)$."
            },
            {
                "step": 4,
                "latex": "\\frac{dP}{d\\Omega} = r^2 |\\mathbf{S}| = \\frac{q^2 a^2 \\sin^2\\theta}{16\\pi^2 \\varepsilon_0 c^3}",
                "rationale": "Determine the differential power radiated per unit solid angle $d\\Omega = \\sin\\theta \\, d\\theta \\, d\\phi$, exhibiting the characteristic dipolar $\\sin^2\\theta$ doughnut pattern."
            },
            {
                "step": 5,
                "latex": "P = \\int \\frac{dP}{d\\Omega} d\\Omega = \\frac{q^2 a^2}{16\\pi^2 \\varepsilon_0 c^3} (2\\pi) \\int_0^\\pi \\sin^3\\theta \\, d\\theta = \\frac{\\mu_0 q^2 a^2}{6\\pi c}",
                "rationale": "Integrate over the complete $4\\pi$ celestial sphere using $\\int_0^\\pi \\sin^3\\theta \\, d\\theta = 4/3$ and $\\mu_0 = 1/(\\varepsilon_0 c^2)$ to yield the total radiated power."
            }
        ]
    },
    ("app/config/content/formulas/93/shard_93.json", "relativistic-sum-5e65d748"): {
        "derivation_type": "LORENTZ_TRANSFORMATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "dx = \\gamma (dx' + v dt'), \\quad dt = \\gamma \\left(dt' + \\frac{v}{c^2} dx'\\right)",
                "rationale": "Write the differential standard Lorentz transformation between reference frame $S$ and primed frame $S'$ moving with relative velocity $v$."
            },
            {
                "step": 2,
                "latex": "u \\equiv \\frac{dx}{dt} = \\frac{\\gamma(dx' + v dt')}{\\gamma(dt' + \\frac{v}{c^2}dx')}",
                "rationale": "Form the coordinate velocity quotient in frame $S$, eliminating the Lorentz boost scale factor $\\gamma = 1/\\sqrt{1 - v^2/c^2}$."
            },
            {
                "step": 3,
                "latex": "u = \\frac{dx' + v dt'}{dt' + \\frac{v}{c^2}dx'} = \\frac{\\frac{dx'}{dt'} + v}{1 + \\frac{v}{c^2}\\frac{dx'}{dt'}}",
                "rationale": "Divide numerator and denominator through by the primed differential time increment $dt'$."
            },
            {
                "step": 4,
                "latex": "u' \\equiv \\frac{dx'}{dt'}",
                "rationale": "Identify the physical velocity of the test particle as measured in the primed reference frame $S'$."
            },
            {
                "step": 5,
                "latex": "u = \\frac{u' + v}{1 + u'v/c^2}",
                "rationale": "Substitute $u'$ to obtain the relativistic composition law, ensuring that speeds strictly bounded by $c$ never exceed $c$ under collinear composition."
            }
        ]
    },
    ("app/config/content/formulas/60/shard_60.json", "relativistic-doppler-factor-receding-source-f059487f"): {
        "derivation_type": "LORENTZ_KINEMATICS",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\Delta t = \\gamma \\Delta \\tau = \\frac{\\Delta \\tau}{\\sqrt{1 - \\beta^2}}",
                "rationale": "Apply time dilation to relate the proper period $\\Delta \\tau = 1/f_{\\text{src}}$ between emitted wavefronts in the source rest frame to coordinate period $\\Delta t$ in the observer frame, where $\\beta = v/c$."
            },
            {
                "step": 2,
                "latex": "d = v \\Delta t = \\beta c \\Delta t",
                "rationale": "Account for the additional spatial distance traveled by the receding source during the emission interval before dispatching the second pulse."
            },
            {
                "step": 3,
                "latex": "\\Delta t_{\\text{obs}} = \\Delta t + \\frac{d}{c} = \\Delta t(1 + \\beta)",
                "rationale": "Calculate the total arrival time interval between wavefronts at the observer, combining emission time separation with optical propagation delay $d/c$."
            },
            {
                "step": 4,
                "latex": "\\Delta t_{\\text{obs}} = \\gamma \\Delta \\tau (1 + \\beta) = \\Delta \\tau \\frac{1 + \\beta}{\\sqrt{1 - \\beta^2}}",
                "rationale": "Express observed arrival period in terms of the intrinsic proper source period $\\Delta \\tau$."
            },
            {
                "step": 5,
                "latex": "\\delta = \\frac{f_{\\text{obs}}}{f_{\\text{src}}} = \\frac{\\Delta \\tau}{\\Delta t_{\\text{obs}}} = \\frac{\\sqrt{1 - \\beta^2}}{1 + \\beta} = \\sqrt{\\frac{(1 - \\beta)(1 + \\beta)}{(1 + \\beta)^2}} = \\sqrt{\\frac{1 - \\beta}{1 + \\beta}}",
                "rationale": "Invert periods to frequencies and simplify the radical fraction using difference of squares to establish the exact radial Doppler factor."
            }
        ]
    },
    ("app/config/content/formulas/d1/shard_d1.json", "de-broglie-relation-8bbf6275"): {
        "derivation_type": "LORENTZ_COVARIANT_SYNTHESIS",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "E = h \\nu = \\hbar \\omega, \\quad E = \\sqrt{p^2 c^2 + m^2 c^4}",
                "rationale": "Synthesize the Planck-Einstein quantum hypothesis for photon energy with the relativistic energy-momentum dispersion relation."
            },
            {
                "step": 2,
                "latex": "P^\\mu = \\left(\\frac{E}{c}, \\mathbf{p}\\right), \\quad K^\\mu = \\left(\\frac{\\omega}{c}, \\mathbf{k}\\right)",
                "rationale": "Formulate the relativistic four-momentum vector $P^\\mu$ and four-wavevector $K^\\mu$ describing a propagating matter wave."
            },
            {
                "step": 3,
                "latex": "P^\\mu = \\hbar K^\\mu \\implies \\frac{E}{c} = \\hbar \\frac{\\omega}{c}, \\quad \\mathbf{p} = \\hbar \\mathbf{k}",
                "rationale": "Impose relativistic Lorentz covariance, mandating that the temporal and spatial components of momentum and wavevector share the identical universal coupling constant $\\hbar$."
            },
            {
                "step": 4,
                "latex": "|\\mathbf{k}| = \\frac{2\\pi}{\\lambda}, \\quad \\hbar = \\frac{h}{2\\pi}",
                "rationale": "Connect the spatial wavenumber magnitude $|\\mathbf{k}|$ to spatial wavelength $\\lambda$ and express reduced Planck constant $\\hbar$ in terms of action constant $h$."
            },
            {
                "step": 5,
                "latex": "p = \\hbar |\\mathbf{k}| = \\left(\\frac{h}{2\\pi}\\right)\\left(\\frac{2\\pi}{\\lambda}\\right) \\implies p = \\frac{h}{\\lambda}",
                "rationale": "Cancel the geometric $2\\pi$ factors to produce de Broglie's universal relation associating spatial wavelength with particle momentum."
            }
        ]
    },
    ("app/config/content/formulas/50/shard_50.json", "photoelectric-equation-einstein-identity-1-3be3f842-00b8e623"): {
        "derivation_type": "CONSERVATION_OF_ENERGY",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "E_{\\text{photon}} = h \\nu",
                "rationale": "Adopt Einstein's light-quantum hypothesis that incoming monochromatic electromagnetic radiation exists as localized wave packets carrying discrete energy $h\\nu$."
            },
            {
                "step": 2,
                "latex": "E_{\\text{initial}} = E_{\\text{photon}} + E_e = h\\nu + E_e",
                "rationale": "Formulate the total energy budget for a single quantum absorption event between an incident photon and a bound conduction electron inside the metallic lattice."
            },
            {
                "step": 3,
                "latex": "W_{\\text{escape}} \\ge \\Phi \\equiv E_{\\text{vacuum}} - E_{\\text{Fermi}}",
                "rationale": "Define the material work function $\\Phi$ as the minimum thermodynamic binding energy required to emancipate an electron from the Fermi surface into vacuum."
            },
            {
                "step": 4,
                "latex": "K = h\\nu - W_{\\text{escape}} \\le h\\nu - \\Phi",
                "rationale": "Recognize that electrons originating deeper than the Fermi level lose additional energy via inelastic lattice scattering, creating an energy upper bound."
            },
            {
                "step": 5,
                "latex": "K_{\\max} = h\\nu - \\Phi \\implies h\\nu = \\Phi + K_{\\max}",
                "rationale": "Isolate the maximum kinetic energy $K_{\\max}$ for electrons escaping without collateral scattering, yielding Einstein's fundamental linear energy conservation law."
            }
        ]
    },
    ("app/config/content/formulas/60/shard_60.json", "bernoulli-constant-standard-form-ff90fb4b"): {
        "derivation_type": "STREAMLINE_INTEGRATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "\\frac{\\partial \\mathbf{v}}{\\partial t} + (\\mathbf{v} \\cdot \\nabla)\\mathbf{v} = -\\frac{1}{\\rho}\\nabla P + \\mathbf{g}",
                "rationale": "Begin with the Euler momentum conservation equation for inviscid fluid flow under gravitational body force acceleration $\\mathbf{g} = -g \\nabla z$."
            },
            {
                "step": 2,
                "latex": "(\\mathbf{v} \\cdot \\nabla)\\mathbf{v} = \\nabla\\left(\\frac{1}{2}v^2\\right) - \\mathbf{v} \\times (\\nabla \\times \\mathbf{v})",
                "rationale": "Invoke the vector identity decomposing the convective acceleration term into the kinetic energy gradient and the Lamb vorticity vector."
            },
            {
                "step": 3,
                "latex": "\\frac{\\partial \\mathbf{v}}{\\partial t} = 0, \\quad d\\mathbf{r} \\parallel \\mathbf{v} \\implies \\left[\\mathbf{v} \\times (\\nabla \\times \\mathbf{v})\\right] \\cdot d\\mathbf{r} = 0",
                "rationale": "Specialize to steady flow ($\\partial/\\partial t = 0$) and take the line integral along an infinitesimal streamline displacement $d\\mathbf{r}$ orthogonal to the cross product."
            },
            {
                "step": 4,
                "latex": "\\nabla\\left(\\frac{1}{2}v^2\\right) \\cdot d\\mathbf{r} + \\frac{1}{\\rho}\\nabla P \\cdot d\\mathbf{r} + g\\nabla z \\cdot d\\mathbf{r} = 0",
                "rationale": "Project the gradient terms along the streamline direction $d\\mathbf{r}$, transforming vector partial derivatives into total differentials along the trajectory."
            },
            {
                "step": 5,
                "latex": "d\\left(\\frac{1}{2}v^2 + \\frac{P}{\\rho} + gz\\right) = 0 \\implies P + \\frac{1}{2}\\rho v^2 + \\rho g z = \\text{constant}",
                "rationale": "Integrate along the streamline assuming constant incompressible fluid density $\\rho$ to obtain Bernoulli's invariant energy relation."
            }
        ]
    },
    ("app/config/content/formulas/0c/shard_0c.json", "jeans-mass-critical-threshold-21a223b3"): {
        "derivation_type": "VIRIAL_EQUILIBRIUM",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "2K + U = 0 \\quad (\\text{Virial Equilibrium Boundary})",
                "rationale": "Begin with the Virial Theorem balance condition separating stable oscillatory hydrostatic equilibrium from self-gravitating runaway collapse."
            },
            {
                "step": 2,
                "latex": "K = \\frac{3}{2} N k_B T = \\frac{3}{2}\\left(\\frac{M}{\\mu m_H}\\right)k_B T = \\frac{3}{2} M c_s^2",
                "rationale": "Express the thermal kinetic energy of a spherical isothermal gas cloud of mass $M$ in terms of the Newtonian isothermal sound speed $c_s^2 = k_B T / (\\mu m_H)$."
            },
            {
                "step": 3,
                "latex": "U = -\\frac{3}{5}\\frac{G M^2}{R}",
                "rationale": "Calculate the gravitational self-energy of a uniform spherical gas core of mass $M$ and radius $R$."
            },
            {
                "step": 4,
                "latex": "2\\left(\\frac{3}{2} M c_s^2\\right) < \\frac{3}{5}\\frac{G M^2}{R} \\implies M > \\frac{5 c_s^2 R}{G}",
                "rationale": "Establish the Jeans instability collapse criterion where self-gravity overcomes outward thermal kinetic pressure."
            },
            {
                "step": 5,
                "latex": "M = \\frac{4}{3}\\pi R^3 \\rho \\implies R = \\left(\\frac{3M}{4\\pi\\rho}\\right)^{1/3} \\implies M_J \\approx \\left(\\frac{c_s^2}{G}\\right)^{3/2} \\rho^{-1/2}",
                "rationale": "Substitute radius $R$ in terms of uniform background mass density $\\rho$ and solve for mass $M$ to isolate the critical Jeans mass threshold."
            }
        ]
    },
    ("app/config/content/formulas/6f/shard_6f.json", "chandrasekhar-limit-88f98df2-31bbfff0-c5efb2d1"): {
        "derivation_type": "EXTREME_RELATIVISTIC_EQUILIBRIUM",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "p_F = \\hbar(3\\pi^2 n_e)^{1/3} \\approx \\hbar \\left(\\frac{M}{\\mu_e m_H R^3}\\right)^{1/3}",
                "rationale": "Determine the electron Fermi momentum in a high-density degenerate stellar core with electron number density $n_e = M / (\\mu_e m_H \\frac{4\\pi}{3} R^3)$."
            },
            {
                "step": 2,
                "latex": "E_k \\approx c p_F = \\hbar c \\left(\\frac{M}{\\mu_e m_H}\\right)^{1/3} \\frac{1}{R}",
                "rationale": "Assume ultra-relativistic degenerate electrons where energy scales linearly with momentum $E = cp$, yielding total kinetic energy $E_{\\text{kin}} \\approx N_e c p_F$."
            },
            {
                "step": 3,
                "latex": "E_{\\text{kin}} \\approx N_e c p_F = \\left(\\frac{M}{\\mu_e m_H}\\right) \\hbar c \\left(\\frac{M}{\\mu_e m_H}\\right)^{1/3} \\frac{1}{R} = \\frac{\\hbar c}{R}\\left(\\frac{M}{\\mu_e m_H}\\right)^{4/3}",
                "rationale": "Calculate total internal electron degeneracy kinetic energy across all $N_e = M/(\\mu_e m_H)$ electrons in the star."
            },
            {
                "step": 4,
                "latex": "E_{\\text{grav}} \\approx -\\frac{G M^2}{R} \\implies E_{\\text{total}} = \\frac{1}{R}\\left[\\hbar c \\left(\\frac{M}{\\mu_e m_H}\\right)^{4/3} - G M^2\\right]",
                "rationale": "Combine degeneracy energy and gravitational self-energy, observing that both terms scale identically as $1/R$ in the ultra-relativistic regime."
            },
            {
                "step": 5,
                "latex": "\\hbar c \\left(\\frac{M}{\\mu_e m_H}\\right)^{4/3} \\approx G M^2 \\implies M_{\\text{Ch}} \\approx \\frac{(\\hbar c / G)^{3/2}}{(\\mu_e m_H)^2}",
                "rationale": "Equate the competing energy terms to locate the critical marginal mass where degeneracy pressure can no longer prevent unbounded gravitational collapse."
            }
        ]
    },
    ("app/config/content/formulas/78/shard_78.json", "stefan-boltzmann-law"): {
        "derivation_type": "INTEGRATION",
        "derivation_steps": [
            {
                "step": 1,
                "latex": "u(\\nu, T)\\,d\\nu = \\frac{8\\pi h \\nu^3}{c^3}\\frac{1}{e^{h\\nu/k_B T} - 1}\\,d\\nu",
                "rationale": "Start with Planck's spectral energy density distribution for electromagnetic blackbody cavity radiation at temperature $T$."
            },
            {
                "step": 2,
                "latex": "u(T) = \\int_0^\\infty u(\\nu, T)\\,d\\nu = \\frac{8\\pi h}{c^3}\\int_0^\\infty \\frac{\\nu^3}{e^{h\\nu/k_B T} - 1}\\,d\\nu",
                "rationale": "Integrate the spectral density over all frequencies $\\nu \\in [0, \\infty)$ to find the total volumetric radiation energy density $u(T)$."
            },
            {
                "step": 3,
                "latex": "x \\equiv \\frac{h\\nu}{k_B T} \\implies \\nu = \\frac{k_B T}{h}x, \\quad d\\nu = \\frac{k_B T}{h}dx",
                "rationale": "Transform to dimensionless integration variable $x$, factoring out temperature dependencies."
            },
            {
                "step": 4,
                "latex": "u(T) = \\frac{8\\pi h}{c^3}\\left(\\frac{k_B T}{h}\\right)^4 \\int_0^\\infty \\frac{x^3}{e^x - 1}\\,dx = \\frac{8\\pi k_B^4 T^4}{c^3 h^3}\\left(\\frac{\\pi^4}{15}\\right) = a T^4",
                "rationale": "Evaluate the standard Riemann zeta integral $\\int_0^\\infty \\frac{x^3}{e^x - 1}dx = \\Gamma(4)\\zeta(4) = \\frac{\\pi^4}{15}$, defining radiation constant $a$."
            },
            {
                "step": 5,
                "latex": "P = \\frac{c}{4}u(T) = \\left(\\frac{2\\pi^5 k_B^4}{15 c^2 h^3}\\right)T^4 \\equiv \\sigma T^4",
                "rationale": "Multiply energy density by $c/4$ for hemispherical Lambertian emission flux to establish the Stefan-Boltzmann law with constant $\\sigma = \\frac{2\\pi^5 k_B^4}{15 c^2 h^3}$."
            }
        ]
    }
}

def apply_tier2_derivations():
    count = 0
    shards_to_write = {}
    for (shard_path, fid), update_data in DERIVATIONS_TIER2.items():
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
    print(f"Successfully applied {count} Tier 2 derivation suites across {len(shards_to_write)} shards.")

if __name__ == "__main__":
    apply_tier2_derivations()
