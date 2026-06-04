import json

payload = {
    "source-of-gravity": {
        "title": "The Source of Gravity",
        "standard": "platinum",
        "parents": ["einstein-field-equations"],
        "content": (
            r"<p>The curvature of spacetime in a pseudo-Riemannian manifold is determined not simply by the distribution of mass, but by the complete stress-energy tensor. "
            r"This geometric framework, central to general relativity, establishes that all forms of mass, energy, and momentum density collectively act as the source of gravity. "
            r"Unlike classical Newtonian gravitation, where mass alone couples to the gravitational potential, the field equations couple the Einstein tensor \( G_{\mu\nu} \) to the relativistic <a href=\"/physics/subtopic/stress-energy-tensor\" class=\"subtopic-link\"><strong>The Stress-Energy Tensor (\(T_{\mu\nu}\))</strong></a>. "
            r"In this variational formulation, the metric tensor \( g_{\mu\nu} \) is dynamically solved, showing that pressure, shear stresses, and energy flux contribute to the gravitational <a href=\"/physics/subtopic/fields-theory\" class=\"subtopic-link\"><strong>Fields Theory</strong></a>. "
            r"The conservation equations \( \nabla_\mu T^{\mu\nu} = 0 \) dictate the local distribution of these sources, ensuring that covariant coordinate transformations preserve physical covariance from a covariant lagrangian density.</p>"
            
            r"<p>A fundamental manifestation of this relativistic source coupling is the inclusion of pressure alongside energy density. "
            r"In highly dense environments, the pressure \( P \) of a fluid becomes a significant driver of gravitational force, which is mathematically represented by the active gravitational mass density in the relativistic generalization of the Poisson equation:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \nabla^2 \Phi = 4\pi G \left( \rho + \frac{3P}{c^2} \right) \\]</div>'
            r"This relation demonstrates that pressure acts as an attractive source of gravity, adding to the rest-mass density \( \rho \). "
            r"In classical systems, the pressure contribution is negligible due to the large factor of \( c^2 \) in the denominator, recovering the standard Newtonian Poisson equation. "
            r"However, under extreme conditions, such as the core of a collapsing star, the pressure gradient cannot be ignored. "
            r"The field equations dictate that this pressure term acts dynamically, which leads to general relativistic instabilities when the state equation crosses critical thresholds. "
            r"This pressure-driven gravity is crucial for understanding the stability limits of compact bodies in <a href=\"/physics/subtopic/astrophysical-general-relativity\" class=\"subtopic-link\"><strong>General Relativity in Astrophysics and Cosmology</strong></a>.</p>"
            
            r"<p>The dynamic coupling of the metric tensor and stress-energy sources is also observed in the radiative sector of the theory. "
            r"As compact binary systems, such as binary black holes, orbit one another, their time-varying quadrupole moments generate ripples in the metric known as gravitational waves. "
            r"These waves carry energy and momentum away from the source, causing the orbit to decay, a phenomenon verified to high precision by the <a href=\"/physics/subtopic/ligo\" class=\"subtopic-link\"><strong>LIGO: Laser Interferometer Gravitational-Wave Observatory</strong></a> interferometers. "
            r"The metric perturbations \( h_{\mu\nu} \) propagate at the speed of light \( c \), carrying information about the source dynamics through the background manifold. "
            r"In the weak-field limit, the wave equation is governed by the linearized field equations:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \square \bar{h}_{\mu\nu} = -\frac{16\pi G}{c^4} T_{\mu\nu} \\]</div>'
            r"This wave propagation demonstrates how localized energy-momentum sources dynamically couple to the global <a href=\"/physics/subtopic/curvature-of-spacetime\" class=\"subtopic-link\"><strong>Einstein Spacetime Curvature Relation</strong></a>. "
            r"The resulting gravitational radiation acts as a messenger of the extreme physics in compact mergers, linking local stress-energy distributions to observational metrics at cosmic distances.</p>"
            
            r"<p>On global cosmological scales, the contribution of negative pressure to the gravitational field introduces a repulsive effect. "
            r"When the stress-energy tensor is dominated by a <a href=\"/physics/subtopic/cosmological-constant\" class=\"subtopic-link\"><strong>Cosmological Constant</strong></a> \( \Lambda \) or <a href=\"/physics/subtopic/dark-energy-theory\" class=\"subtopic-link\"><strong>Dark Energy Theory</strong></a>, the equation of state yields a negative pressure \( P = -\rho c^2 \). "
            r"Substituting this <a href=\"/physics/subtopic/negative-pressure\" class=\"subtopic-link\"><strong>Negative Pressure</strong></a> into the active mass density yields a net negative source term \( \rho + 3P/c^2 = -2\rho \), leading to the accelerated expansion of the universe. "
            r"This phenomenon is probed observationally through distance indicators like <a href=\"/physics/subtopic/leavitts-law\" class=\"subtopic-link\"><strong>Leavitt's Law (Period-Luminosity Relationship)</strong></a>, which calibrate the expansion rate across cosmic time. "
            r"The physical nature of this dark energy source remains a key query, prompting debates between <a href=\"/physics/subtopic/scientific-realism\" class=\"subtopic-link\"><strong>Scientific Realism</strong></a> and various <a href=\"/physics/subtopic/ontological-interpretation\" class=\"subtopic-link\"><strong>Ontological Interpretation</strong></a> models of the cosmic vacuum. "
            r"In these debates, the cosmological constant is either viewed as a fundamental geometric property of the manifold or as the vacuum energy density of a quantum field operator.</p>"
            
            r"<p>A rigorous reduction of this general relativistic source coupling to the classical regime occurs in the weak-field, slow-motion limit. "
            r"In this classical limit, the spatial components of the stress-energy tensor \( T_{ij} \) are negligible compared to the energy density component \( T_{00} \approx \rho c^2 \). "
            r"As the velocities of the gravitating bodies become small compared to the speed of light \( v \ll c \), and the fields remain weak, the metric tensor converges to the flat Minkowski metric perturbed by a static Newtonian potential \( \Phi \):"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ g_{00} \approx -\left(1 + \frac{2\Phi}{c^2}\right) \\]</div>'
            r"Under this systematic limit, the field equations contract smoothly to the classical Poisson equation, where the spatial curvature vanishes, the spherical symmetry is preserved, and the force of gravity is represented as a conservative gradient. "
            r"This mathematical reduction preserves the physical consistency of <a href=\"/physics/subtopic/general-relativity\" class=\"subtopic-link\"><strong>General Relativity</strong></a> across all scales, proving that the relativistic description of mass-energy coupling recovers Newtonian gravitation without any structural singularities.</p>"
        ),
        "identities": [
            {
                "id": "source-of-gravity-identity-1-d00f71db-9f13364f",
                "title": "Einstein Field Equations",
                "equation": "G_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}",
                "description": "Relates the geometry of spacetime curvature to the distribution of mass-energy and momentum."
            }
        ]
    },
    "history-of-the-universe": {
        "title": "History of the Universe",
        "standard": "platinum",
        "parents": ["physical-cosmology"],
        "content": (
            r"<p>The thermal evolution of an expanding Friedmann-Lemaître-Robertson-Walker spacetime manifold governs the physical phases of cosmic history. "
            r"This expansion of the coordinate grid, which is systematically investigated within <a href=\"/physics/subtopic/early-universe-cosmology\" class=\"subtopic-link\"><strong>Early Universe Cosmology</strong></a>, shifts the relative densities of radiation, baryonic matter, and dark energy across astronomical epochs. "
            r"According to the classical field equations of general relativity, the temporal scaling of the dimensionless cosmic scale factor \( a(t) \) determines the temperature and density of the primordial plasma, linking particle physics to global geometry. "
            r"On the largest observable scales, the rate of expansion is quantified by the Hubble parameter \( H(t) \), which satisfies the first Friedmann relation:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ H^2 = \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G}{3}\rho - \frac{k c^2}{a^2} + \frac{\Lambda c^2}{3} \\]</div>'
            r"This fundamental differential equation couples the total energy-momentum density \( \rho(t) \) to the spatial curvature parameter \( k \). "
            r"As the scale factor increases, the radiation energy density decays rapidly, causing the universe to transition from a hot, dense plasma to a cold, matter-dominated epoch. "
            r"The conservation of energy-momentum, expressed as \( \dot{\rho} + 3H(\rho + P/c^2) = 0 \), dictates this scaling behavior, guaranteeing that the expansion remains compatible with general relativity. "
            r"In this framework, the thermal history is not merely a background process but is dynamically coupled to the changing geometry of the manifold itself, establishing the temporal milestones of cosmic structure formation.</p>"
            
            r"<p>At the earliest observable epoch, the dynamics of the expansion are believed to have been dominated by <a href=\"/physics/subtopic/inflaton-field\" class=\"subtopic-link\"><strong>The Inflaton Field</strong></a>. "
            r"This scalar field, operating in the high-energy regime of grand unified theories, drove a brief period of exponential expansion that resolved <a href=\"/physics/subtopic/flatness-threshold-critical\" class=\"subtopic-link\"><strong>The Flatness Problem</strong></a>. "
            r"Under this inflationary scenario, the energy density of the scalar field remained nearly constant, forcing the scale factor to grow by dozens of orders of magnitude in a tiny fraction of a second. "
            r"The kinematics of the inflation phase are governed by the Friedmann acceleration equation:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \frac{\ddot{a}}{a} = -\frac{4\pi G}{3}\left(\rho + \frac{3P}{c^2}\right) + \frac{\Lambda c^2}{3} \\]</div>'
            r"This acceleration relation demonstrates that a field with negative pressure, satisfying \( P < -\rho c^2/3 \), generates repulsive gravity. "
            r"This cosmic acceleration flattened the spatial geometry of the manifold, driving the curvature parameter \( k \) toward zero. "
            r"Primordial quantum fluctuations in the scalar field were stretched to macroscopic scales, seeding the density perturbations that would later grow under gravity. "
            r"High-precision measurements of these temperature fluctuations by the <a href=\"/physics/subtopic/planck-satellite\" class=\"subtopic-link\"><strong>Planck Satellite</strong></a> confirm that the primordial geometry is flat to within a fraction of a percent, providing strong evidence for the inflationary paradigm. "
            r"The inflation field eventually decayed, transferring its energy to standard model particles through reheating, populating the universe with a hot, dense plasma.</p>"
            
            r"<p>As the inflaton field decayed, it reheated the universe, populating the coordinate grid with a relativistic plasma of standard model particles and <a href=\"/physics/subtopic/dark-matter\" class=\"subtopic-link\"><strong>Dark Matter</strong></a>. "
            r"The cooling of this plasma as the scale factor expanded governed the sequential steps of big bang nucleosynthesis and recombination. "
            r"In the radiation-dominated era, the energy density of relativistic species scaled inversely with the fourth power of the scale factor:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \rho_r(a) = \rho_{r,0} a^{-4} \\]</div>'
            r"This dilution law arises because the photon wavelengths are redshifted by the expansion, adding a factor of \( a^{-1} \) to the volume dilution \( a^{-3} \). "
            r"Once the temperature dropped below the binding energy of hydrogen, neutral atoms formed, and the background radiation field decoupled from baryonic matter. "
            r"This relic radiation, propagating through the expanding manifold, is observed today as the cosmic microwave background, carrying a snapshot of the young universe. "
            r"The acoustic peaks in this radiation spectrum represent the eigenvalues of sound waves propagating in the plasma, constraining the primordial abundance of normal and dark matter. "
            r"By analyzing the angular scale of these peaks, astrophysicists can determine the composition of the universe, confirming that non-baryonic dark matter dominates the matter budget.</p>"
            
            r"<p>The subsequent growth of structure was driven by the gravitational collapse of dark matter perturbations into galactic halos. "
            r"As these potential wells deepened, baryonic gas fell into them, cooling and condensing to ignite the first generation of stars. "
            r"This stellar birth initiated the <a href=\"/physics/subtopic/stellar-lifecycle\" class=\"subtopic-link\"><strong>Stellar Lifecycles</strong></a>, where thermonuclear fusion inside stellar cores synthesized heavy elements. "
            r"These stellar systems evolved over millions of years, culminating in spectacular <a href=\"/physics/subtopic/type-ia-supernovae\" class=\"subtopic-link\"><strong>Type Ia Supernovae</strong></a> that enriched the interstellar medium. "
            r"The expansion history during this matter-dominated epoch was dominated by pressureless dust, where the matter density \( \rho_m \) scaled as \( a^{-3} \). "
            r"The competition between the gravitational attraction of this matter and the cosmic expansion shaped the large-scale structure, establishing the network of filaments and voids observed in the galaxy distribution. "
            r"The synthesis of heavy elements through stellar nucleosynthesis and supernovae explosions provided the raw materials for planets and life, linking the microscopic processes of stellar physics to the macroscopic history of the cosmos.</p>"
            
            r"<p>A formal mathematical limit for this cosmic timeline is recovered in the limit of late-time expansion, where the matter and radiation densities approach zero. "
            r"As the scale factor \( a(t) \) becomes arbitrarily large, the fractional energy densities of radiation \( \Omega_r \) and matter \( \Omega_m \) contract smoothly to zero. "
            r"Under this dilute limit, the Friedmann equation simplifies directly to a de Sitter metric, where the expansion rate is governed entirely by the cosmological constant \( \Lambda \):"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ H^2 \approx \frac{\Lambda c^2}{3} \\]</div>'
            r"Consequently, the complex, thermal history of the early universe dissolves into the static, exponential expansion of a vacuum-dominated spacetime. "
            r"This transition mathematically guarantees that the classical cosmological model converges to a stable de Sitter boundary, preserving the metric consistency of the universe across all temporal regimes. "
            r"Under this continuous reduction, the dynamic, matter-filled coordinate grids contract into a homogeneous, dark-energy-dominated vacuum. "
            r"The universe enters a state of perpetual acceleration, where distant galaxies are pushed beyond the cosmic horizon, leaving local groups in isolated, cold space.</p>"
        ),
        "identities": [
            {
                "id": "friedmann-acceleration-cosmology-8869b3df-2d71483c",
                "title": "Friedmann Acceleration Equation",
                "equation": "\\frac{\\ddot{a}}{a} = -\\frac{4\\pi G}{3}\\left(\\rho + \\frac{3P}{c^2}\\right) + \\frac{\\Lambda c^2}{3}",
                "description": "Governs the expansion rate acceleration of a homogeneous and isotropic universe."
            }
        ]
    },
    "cosmic-budget": {
        "title": "The Cosmic Budget (Energy Inventory)",
        "standard": "platinum",
        "parents": ["cosmological-density"],
        "content": (
            r"<p>The macroscopic geometry of the expanding universe is constrained by the sum of its fractional energy densities, which must equal unity in a spatially flat manifold. "
            r"This fractional inventory, known as the cosmic energy inventory, scales the contributions of matter, radiation, and dark energy relative to the total <a href=\"/physics/subtopic/cosmological-density\" class=\"subtopic-link\"><strong>Cosmological Density</strong></a>. "
            r"According to general relativity, the spatial curvature of the cosmic metric is dynamically coupled to this energy distribution through the Friedmann equations. "
            r"By normalizing the individual energy densities to the <a href=\"/physics/subtopic/critical-density\" class=\"subtopic-link\"><strong>Critical Density</strong></a>, the sum rule for the dimensionless parameters \( \Omega_i \) is formulated as:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \Omega_m + \Omega_r + \Omega_k + \Omega_\Lambda = 1 \\]</div>'
            r"In this expression, \( \Omega_m \), \( \Omega_r \), \( \Omega_k \), and \( \Omega_\Lambda \) represent the matter, radiation, spatial curvature, and dark energy density parameters, respectively. "
            r"This sum rule guarantees that the global geometry remains consistent with the conservation of energy-momentum, forcing the spatial curvature to vanish when the total density equals the critical density. "
            r"The precise determination of these parameters allows cosmologists to reconstruct the geometric history of the universe, demonstrating that our cosmos is flat to within observational precision. "
            r"The flatness of the universe implies a delicate balance between the expansion rate and the total energy content, which is a central pillar of the standard cosmological model.</p>"
            
            r"<p>At any given epoch, the absolute scale of this energy inventory is set by the critical density, which is defined in terms of the <a href=\"/physics/subtopic/hubble-parameter\" class=\"subtopic-link\"><strong>Hubble Parameter</strong></a> \( H(t) \) and Newton's gravitational constant \( G \). "
            r"The critical density represents the boundary threshold between an open universe that expands forever and a closed universe that eventually collapses, written mathematically as:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \rho_c = \frac{3 H^2}{8\pi G} \\]</div>'
            r"This relationship shows that the critical density scales with the square of the expansion rate, meaning it was much higher in the early universe when the expansion was more rapid. "
            r"By comparing the observed physical density of each cosmic component to this critical value, cosmologists can map the spatial distribution of mass-energy. "
            r"The measurement of these density parameters is a key goal of observational cosmology, as the relative budget dictates the future deceleration or acceleration of the coordinate grid. "
            r"In a flat universe, the actual density equals the critical density, meaning that any deviation from flatness must be compensated by a change in the expansion rate or the energy content of the vacuum.</p>"
            
            r"<p>The dynamics of the expansion are governed by the different scaling laws of the cosmic components as the scale factor \( a(t) \) increases. "
            r"Because the energy densities of radiation, matter, and the <a href=\"/physics/subtopic/cosmological-constant\" class=\"subtopic-link\"><strong>Cosmological Constant</strong></a> scale differently, the relative budget changes over time, written as a function of the scale factor:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \rho(a) = \rho_{c} \left[ \Omega_{r,0} a^{-4} + \Omega_{m,0} a^{-3} + \Omega_{k,0} a^{-2} + \Omega_{\Lambda,0} \right] \\]</div>'
            r"This scaling relation shows that the radiation density \( \rho_r \propto a^{-4} \) dominated the early universe, but was quickly surpassed by the matter density \( \rho_m \propto a^{-3} \). "
            r"The matter sector is composed of normal baryonic matter and non-baryonic <a href=\"/physics/subtopic/dark-matter\" class=\"subtopic-link\"><strong>Dark Matter</strong></a>, which together drive the gravitational clustering that forms galaxies. "
            r"The dark matter component makes up the majority of the matter budget, providing the gravitational potential wells necessary for structure growth. "
            r"The spatial curvature density \( \rho_k \propto a^{-2} \) represents the geometric deviation from flatness, which remains close to zero in our universe. "
            r"As the universe expands, the matter and radiation densities continue to dilute, while the dark energy density remains constant, leading to a transition in the dominant component of the budget.</p>"
            
            r"<p>In the modern cosmological epoch, the cosmic inventory has transitioned to a state dominated by dark energy, which represents about 70 percent of the total budget. "
            r"This dark energy component, often parameterized as a cosmological constant \( \Lambda \) in the action lagrangian, exhibits a constant energy density that does not dilute with expansion. "
            r"Because dark energy has a <a href=\"/physics/subtopic/negative-pressure\" class=\"subtopic-link\"><strong>Negative Pressure</strong></a>, it generates a repulsive gravitational effect that drives the accelerated expansion of the universe. "
            r"This transition from matter domination to dark energy domination occurred at a scale factor \( a \approx 0.6 \text{ when the diluting matter density fell below the constant dark energy density} \). "
            r"The physical mechanism behind this constant density remains a major theoretical challenge, as quantum field theory predicts a vacuum energy density that is many orders of magnitude larger than the observed value. "
            r"This mismatch, known as the cosmological constant problem, is one of the most significant crises in theoretical physics.</p>"
            
            r"<p>A rigorous mathematical limit for this energy inventory occurs in the asymptotic future, where the scale factor approaches infinity and all diluting components vanish. "
            r"As the scale factor \( a(t) \to \infty \), the fractional densities of radiation, matter, and curvature contract smoothly to zero. "
            r"Under this limiting case, the cosmic budget simplifies directly to a pure de Sitter state, where the dark energy parameter \( \Omega_\Lambda \) reaches exactly unity:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \Omega_\Lambda \approx 1  \\]</div>'
            r"Consequently, the complex, multi-component energy inventory of the early universe dissolves into the static homogeneity of a pure cosmological constant. "
            r"This transition mathematically guarantees that the cosmic evolution converges to a stable geometric boundary, preserving the metric consistency of the universe across all epochs. "
            r"Under this continuous reduction, the dynamic, matter-filled coordinate grids contract into a homogeneous, dark-energy-dominated vacuum. "
            r"The universe becomes increasingly cold and dark, as all other forms of energy are diluted to infinity, leaving a vacuum state governed entirely by the cosmological constant.</p>"
        ),
        "identities": [
            {
                "id": "energy-pie-92cd1760",
                "title": "Cosmic Density Parameter Sum Rule",
                "equation": "\\Omega_m + \\Omega_r + \\Omega_k + \\Omega_\\Lambda = 1",
                "description": "Expresses the sum of fractional energy densities (matter, radiation, and cosmological constant) in a flat universe."
            }
        ]
    }
}

with open("subfiles/batch_payload.json", "w") as f:
    json.dump(payload, f, indent=4)
print("Payload written successfully to subfiles/batch_payload.json")
