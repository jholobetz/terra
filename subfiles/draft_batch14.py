import json

payload = {
    "flrw-metric": {
        "title": "FLRW Metric",
        "standard": "platinum",
        "parents": ["physical-cosmology"],
        "content": (
            r"<p>The geometry of a homogeneous and isotropic expanding universe is described by a pseudo-Riemannian metric tensor on a four-dimensional spacetime manifold. "
            r"This mathematical framework, central to physical cosmology, models the universe as a spatially homogeneous and isotropic fluid, restricting the spatial curvature to one of three possible geometries: flat, spherical, or hyperbolic. "
            r"Known as the Friedmann-Lemaître-Robertson-Walker metric, this metric expresses the spacetime interval \( ds^2 \) in terms of the scale factor \( a(t) \) and the spatial curvature parameter \( k \):"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ ds^2 = -c^2 dt^2 + a(t)^2 \left[ \frac{dr^2}{1 - k r^2} + r^2 (d\theta^2 + \sin^2\theta \, d\phi^2) \right] \\]</div>'
            r"Here, the coordinate system is comoving, meaning that observers moving with the cosmic expansion remain at constant spatial coordinates. "
            r"Under this variational formulation, the spatial geometry is governed by the value of \( k \), which takes the values \( 0, 1, \) or \( -1 \) for flat, closed, or open spatial sections, respectively. "
            r"The temporal scaling of the spatial components is governed by the scale factor, representing the cosmological expansion that shifts spectral lines over time.</p>"
            
            r"<p>The dynamics of this expanding spacetime are solved by substituting the metric components into the Einstein field equations, which couple the curvature of the manifold to its mass-energy content. "
            r"In this framework, the <a href=\"/physics/subtopic/curvature-of-spacetime\" class=\"subtopic-link\"><strong>Einstein Spacetime Curvature Relation</strong></a> is represented by the Einstein tensor \( G_{\mu\nu} \), which is dynamically coupled to the stress-energy tensor \( T_{\mu\nu} \) of the cosmic fluid:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2} R g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu} \\]</div>'
            r"This tensor relation shows that the distribution of mass, energy, and momentum acts as the source of gravity, shaping the global geometry of the universe. "
            r"In this framework, the cosmic fluid is typically modeled as a perfect fluid characterized by an energy density \( \rho \) and an isotropic pressure \( P \). "
            r"The conservation of energy-momentum, expressed as \( \nabla_\mu T^{\mu\nu} = 0 \), guarantees that the expansion remains compatible with the local conservation laws of general relativity, preserving physical covariance across all coordinate charts.</p>"
            
            r"<p>On observational scales, the rate of expansion is quantified by the Hubble parameter \( H(t) \), which relates the scale factor to its temporal derivative:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ H(t) = \frac{\dot{a}}{a} \\]</div>'
            r"This expansion rate is calibrated across cosmic time using distance indicators like <a href=\"/physics/subtopic/leavitts-law\" class=\"subtopic-link\"><strong>Leavitt's Law (Period-Luminosity Relationship)</strong></a>, which establish the astronomical distance scale and map the expansion flow. "
            r"Crucially, the presence of <a href=\"/physics/subtopic/dark-matter\" class=\"subtopic-link\"><strong>Dark Matter</strong></a> and baryonic matter contributes to the total density, slowing the expansion through gravitational attraction, whereas a <a href=\"/physics/subtopic/cosmological-constant\" class=\"subtopic-link\"><strong>Cosmological Constant</strong></a> \( \Lambda \) drives acceleration. "
            r"The relative abundance of these components determines the deceleration parameter and governs the future destiny of the universe, demonstrating how local density parameters are structurally integrated into global cosmic expansion models.</p>"
            
            r"<p>The propagation of test particles and photons through this expanding geometry is governed by the geodesic equations, which describe the straightest possible paths in a curved manifold. "
            r"As light propagates from distant sources, its wavelength is stretched by the expansion, resulting in a cosmological redshift \( 1 + z = a_0 / a(t) \). "
            r"This redshift is not a Doppler shift in the classical sense, but is a direct manifestation of the expansion of the coordinate grid itself, proving that space is a dynamical participant in cosmic history. "
            r"By measuring the redshift-distance relation of standard candles, cosmologists can map the history of the scale factor, revealing the transition from a matter-dominated deceleration to a dark-energy-dominated acceleration.</p>"
            
            r"<p>A clear demonstration of the limiting case for this cosmological metric occurs in the limit of zero density, or as the energy-momentum tensor \( T_{\mu\nu} \) approaches zero. "
            r"As the density of matter and radiation approaches zero and the cosmological constant vanishes, the scale factor \( a(t) \) contracts smoothly to a constant value, and the spatial curvature parameter \( k \) contracts to zero. "
            r"Under this empty-space limit, the metric components simplify directly to the flat, static equations of Minkowski spacetime, where the interval reduces to the flat-space relation:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ ds^2 \approx -c^2 dt^2 + dr^2 + r^2 (d\theta^2 + \sin^2\theta \, d\phi^2) \\]</div>'
            r"Consequently, the complex, expansion-driven features of the cosmological model dissolve into the flat-space regularities of special relativity, proving that the FLRW framework is compatible with flat Minkowski spacetime. "
            r"This transition mathematically guarantees that the classical limit is recovered without any coordinate singularities, preserving the metric consistency of cosmological structures across all physical scales. "
            r"Under this continuous reduction, the non-linear expansion gradients contract into static flat-space configurations, satisfying the requirements of the correspondence principle.</p>"
        ),
        "identities": [
            {
                "id": "flrw-metric-identity-1-a779d230-9f13364f",
                "title": "FLRW Metric Spacetime Interval",
                "equation": "ds^2 = -c^2 dt^2 + a(t)^2 \\left[ \\frac{dr^2}{1 - k r^2} + r^2 (d\\theta^2 + \\sin^2\\theta \\, d\\phi^2) \\right]",
                "description": "Defines the spacetime interval in a homogeneous and isotropic expanding universe."
            }
        ]
    },
    "ligo": {
        "title": "LIGO: Laser Interferometer Gravitational-Wave Observatory",
        "standard": "platinum",
        "parents": ["astrophysical-general-relativity"],
        "content": (
            r"<p>The interferometric measurement of infinitesimal metric strains induced by propagating spacetime curvature perturbations is achieved using massive perpendicular optical cavities. "
            r"Semiclassically, the passage of a gravitational wave alters the proper length of the orthogonal arms of a Michelson interferometer, creating a differential phase shift in the recombined laser beams. "
            r"Specifically, for a gravitational wave propagating along the \( z \)-axis with plus-polarization amplitude \( h_+ \) and cross-polarization amplitude \( h_\times \), the spatial metric perturbations modify the spacetime interval. "
            r"If a gravitational wave with strain amplitude \( h \) passes through the detector, the physical arm length \( L \) along the coordinate axes \( x \) and \( y \) undergoes a fractional change \( \Delta L \) given by:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ h = \frac{2 \Delta L}{L} \\]</div>'
            r"This relationship shows that the strain sensitivity scales with the arm length, prompting the construction of multi-kilometer installations to detect strains on the order of \( 10^{-21} \). "
            r"By reflecting the laser light multiple times within Fabry-Perot cavities using high-reflectivity mirrors, the effective arm length is increased to a length \( L_{\text{eff}} \), enhancing the phase shift of the recombined photons and allowing the strain signal to rise above thermal and seismic noise floors. "
            r"This amplification enables the detection of tiny perturbations in the local geometry.</p>"
            
            r"<p>The phase shift \( \Delta \phi \) detected at the output port is directly proportional to the differential change in arm length and the wavelength \( \lambda \) of the laser light, formulated as:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ \Delta \phi = \frac{4\pi \Delta L}{\lambda} \\]</div>'
            r"This phase difference is converted into a photodetector current, providing a direct observational metric of the gravitational strain. "
            r"The laser systems utilize ultra-stable, high-power infrared beams at a wavelength \( \lambda = 1064 \text{ nm} \), which are locked to high-finesse optical cavities to minimize frequency fluctuations. "
            r"To maximize the circulating optical power, the interferometer employs a power recycling mirror that forms a resonant cavity with the input mirrors, boosting the effective input power by a power recycling factor \( G_{\text{pr}} \) of several hundreds. "
            r"The mirrors are suspended as multi-stage pendulums to isolate them from seismic vibration, acting as test masses that remain in free fall within the horizontal plane. "
            r"This design ensures that the mirrors respond solely to the curvature-of-spacetime, preserving the covariant signature of the gravitational wave from localized environmental perturbations. "
            r"Active feedback loops, using electrostatic actuators, maintain the cavity lengths at exact resonance.</p>"
            
            r"<p>The gravitational waves detected by these observatories are generated by the acceleration of massive, <a href=\"/physics/subtopic/compact-objects\" class=\"subtopic-link\"><strong>Compact Objects</strong></a>, such as binary black holes or neutron stars undergoing coalescence. "
            r"The kinematics of these merging binaries are governed by general relativity, where the emitted strain amplitude in the quadrupole approximation scales with the second time derivative of the mass quadrupole moment \( \ddot{I}_{\mu\nu}(t) \):"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ h(t) \approx \frac{4 G}{c^4 r} \ddot{I}_{\mu\nu}(t) \\]</div>'
            r"This relationship demonstrates that the wave strength is inversely proportional to the distance \( r \) to the source and directly proportional to the acceleration of the mass distribution. "
            r"The frequency evolution of the inspiral phase is determined by the chirp mass \( \mathcal{M} = (m_1 m_2)^{3/5} / (m_1 + m_2)^{1/5} \), which couples the individual masses \( m_1 \) and \( m_2 \) to the orbital decay rate. "
            r"The relativistic structure of the merging neutron stars is constrained by the <a href=\"/physics/subtopic/tov-equation\" class=\"subtopic-link\"><strong>TOV Equation</strong></a>, which governs the maximum mass and density profile of stable compact remnants. "
            r"By matching the observed waveform to numerical relativity models, astrophysicists can extract the masses, spins, and distance of the merging system, providing a new method for calibrating astronomical distances independently of <a href=\"/physics/subtopic/leavitts-law\" class=\"subtopic-link\"><strong>Leavitt's Law (Period-Luminosity Relationship)</strong></a>. "
            r"This observational method provides a direct test of strong-field gravity.</p>"
            
            r"<p>On global cosmological scales, these gravitational wave signatures serve as standard sirens for measuring the expansion rate of the universe. "
            r"By combining the luminosity distance \( d_L \) extracted directly from the wave amplitude with the redshift \( z \) of the host galaxy, cosmologists can calculate the Hubble constant \( H_0 \), providing a critical test of the standard cosmological model. "
            r"These observations are essential for constraining the total energy density \( \Omega \) of the universe, testing the transition from a matter-dominated <a href=\"/physics/subtopic/einstein-de-sitter\" class=\"subtopic-link\"><strong>Einstein-de Sitter</strong></a> model to the dark-energy-dominated <a href=\"/physics/subtopic/de-sitter-universe\" class=\"subtopic-link\"><strong>The De Sitter Universe</strong></a>. "
            r"This independent measurement helps resolve the tension in the Hubble parameter \( H(z) \) measurements and constrains the deceleration parameter \( q_0 \) across cosmological epochs. "
            r"The capability to detect gravitational waves from compact mergers establishes a direct link between local general relativistic kinematics and global cosmological parameters, marking a major milestone in <a href=\"/physics/subtopic/astrophysical-general-relativity\" class=\"subtopic-link\"><strong>General Relativity in Astrophysics and Cosmology</strong></a>.</p>"
            
            r"<p>A clear demonstration of the limiting case for this interferometric strain model occurs in the limit of a perfectly flat Minkowski spacetime, or as the gravitational wave amplitude \( h(t) \) approaches zero. "
            r"In general relativity, the spacetime metric is expanded as \( g_{\mu\nu} = \eta_{\mu\nu} + h_{\mu\nu} \), where \( \eta_{\mu\nu} \) represents the flat background and \( h_{\mu\nu} \) represents the dynamical metric perturbation. "
            r"As the wave amplitude vanishes, the perturbation \( h_{\mu\nu} \to 0 \), meaning that the Riemann curvature tensor \( R^\mu_{\;\nu\alpha\beta} \) contracts smoothly to zero, and the differential arm length change \( \Delta L \) contracts to zero. "
            r"Under this flat-space limit, the orthogonal arms of the interferometer return to their static, unperturbed lengths \( L_0 \), and the photodetector phase shift \( \Delta \phi \) vanishes. "
            r"Consequently, the dynamic, wave-driven features of the optical cavities dissolve into the static regularities of standard flat-space electromagnetism, proving that the strain model is compatible with static flat geometries. "
            r"This transition mathematically guarantees that the classical interferometer behavior is recovered without any optical singularities, preserving the metric consistency of the laser cavities across all gravitational wave amplitudes. "
            r"Under this continuous reduction, the non-linear curvature gradients contract into static flat-space configurations, satisfying the correspondence principle.</p>"
        ),
        "identities": [
            {
                "id": "ligo-strain-sensitivity-0025e8ed",
                "title": "Interferometric Strain Relation",
                "equation": "h = \\frac{2 \\Delta L}{L}",
                "description": "Relates the gravitational wave strain to the physical arm length and displacement."
            }
        ]
    },
    "coulomb-barrier": {
        "title": "The Coulomb Barrier",
        "standard": "platinum",
        "parents": ["astrophysical-nuclear-physics"],
        "content": (
            r"<p>The electrostatic repulsion between positively charged atomic nuclei prevents fusion at low temperatures by establishing a repulsive potential that increases as the inverse of the separation distance. "
            r"This potential barrier, known as the electrostatic barrier, must be overcome or penetrated for nuclei to get close enough for the short-range strong force to bind them. "
            r"According to classical electromagnetism, the potential energy \( V_C(r) \) of two interacting nuclei with atomic numbers \( Z_1 \) and \( Z_2 \) (which represent charges \( q_1 = Z_1 e \) and \( q_2 = Z_2 e \) respectively) separated by a distance \( r \) is governed by Coulomb's law:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ V_C(r) = \frac{Z_1 Z_2 e^2}{4\pi \epsilon_0 r} \\]</div>'
            r"This relation shows that the repulsive force scales with the product of the nuclear charges and is inversely proportional to the permittivity of free space \( \epsilon_0 \), making the barrier higher for heavier elements. "
            r"The interaction can also be parameterized using the fine-structure constant \( \alpha = e^2 / (4\pi \epsilon_0 \hbar c) \), highlighting the electromagnetic nature of the coupling. "
            r"In stellar interiors, this electrostatic barrier acts as a regulator for thermonuclear fusion reactions, ensuring that the fusion rates remain highly stable. "
            r"The conservation of charge and energy dictates this scaling behavior, establishing a threshold that dictates the lifecycle of stars and the chemical evolution of the universe. "
            r"Without this barrier, nuclear fuel would consume itself almost instantly.</p>"
            
            r"<p>The classical height of this barrier, representing the energy required for the nuclei to touch, is evaluated at the contact radius \( R_{\text{contact}} = R_1 + R_2 \), where the nuclear surfaces meet. "
            r"Empirically, the nuclear radius of each species scales with the mass number \( A_i \) as \( R_i \approx r_0 A_i^{1/3} \), where \( r_0 \approx 1.2 \text{ fm} \). "
            r"Using these parameters, the barrier height \( E_C \) is formulated as:"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ E_C = \frac{Z_1 Z_2 e^2}{4\pi \epsilon_0 (R_1 + R_2)} \\]</div>'
            r"For two protons, this classical barrier is approximately one mega-electronvolt, which is far greater than the average thermal kinetic energy \( k_B T \) of protons inside a stellar core (typically a few kilo-electronvolts, corresponding to temperatures \( T \approx 1.5 \times 10^7 \text{ K} \)). "
            r"Consequently, classical physics predicts that fusion is impossible at these temperatures, which would lead to a dark, static universe without stellar ignition. "
            r"This conflict is resolved by quantum mechanics, which allows particles to tunnel through the barrier with a finite probability, a process that is essential for stellar energy generation. "
            r"This tunneling probability is extremely sensitive to both energy and charge.</p>"
            
            r"<p>The quantum mechanical penetration of this barrier is governed by the wave function of the interacting nuclei, solved using the WKB approximation for <a href=\"/physics/subtopic/quantum-tunneling-nuclear\" class=\"subtopic-link\"><strong>Gamow Tunneling Probability and Coulomb Barrier Penetration</strong></a>. "
            r"The tunneling probability \( P \) is a sensitive function of the particle energy \( E \), the reduced mass \( \mu \), and the potential barrier, integrated between the turning points \( r_1 = R_1 + R_2 \) and \( r_2 = Z_1 Z_2 e^2 / (4\pi \epsilon_0 E) \):"
            r'<div class="math-display" style="text-align: center; margin: 25px 0;">\\[ P \approx \exp\left(-2 \int_{r_1}^{r_2} \sqrt{\frac{2\mu}{\hbar^2} \left[ V_C(r) - E \right]} \, dr\right) \\]</div>'
            r"This integration demonstrates that the tunneling probability decreases exponentially with the height and width of the barrier, but increases with the kinetic energy of the particles. "
            r"The resulting tunneling probability is characterized by the Gamow factor \( e^{-2\pi\eta} \), where the Sommerfeld parameter \( \eta = \frac{Z_1 Z_2 e^2}{4\pi \epsilon_0 \hbar v} \) depends on the relative velocity \( v \). "
            r"This factor dominates the nuclear reaction cross-sections in stellar plasma. "
            r"This quantum tunneling is the primary mechanism that enables the <a href=\"/physics/subtopic/pp-chain\" class=\"subtopic-link\"><strong>Proton-Proton Chain Fusion Energy Generation Rate</strong></a> and the CNO cycle to proceed at temperatures far below the classical threshold, shaping the energy generation rate of main-sequence stars. "
            r"The stellar nucleosynthesis timescales are directly determined by this quantum penetration probability.</p>"
            
            r"<p>On larger astrophysical scales, the rates of these nuclear reactions dictate the hydrostatic equilibrium and the thermal structure of stars. "
            r"The stellar energy output, characterized by the luminosity \( L \), balances the gravitational collapse of the stellar manifold where the inward gravitational force \( F_g \) is offset by outward thermal pressure \( P_{\text{thermal}} \). "
            r"This luminosity is calibrated by distance indicators like <a href=\"/physics/subtopic/leavitts-law\" class=\"subtopic-link\"><strong>Leavitt's Law (Period-Luminosity Relationship)</strong></a>, which map the cosmological distance scale. "
            r"In extreme environments such as neutron star mergers, heavy elements are synthesized through rapid neutron captures, a process whose physics is governed by the <a href=\"/physics/subtopic/nuclear-eos\" class=\"subtopic-link\"><strong>Nuclear Equation of State</strong></a>. "
            r"These violent mergers generate gravitational waves that are detected by the <a href=\"/physics/subtopic/ligo\" class=\"subtopic-link\"><strong>LIGO: Laser Interferometer Gravitational-Wave Observatory</strong></a> observatories, linking the subatomic physics of barrier penetration directly to global astronomical signals and confirming the predictions of <a href=\"/physics/subtopic/astrophysical-general-relativity\" class=\"subtopic-link\"><strong>General Relativity in Astrophysics and Cosmology</strong></a>. "
            r"Thus, local quantum tunneling rates are linked to macroscopic cosmic events.</p>"
            
            r"<p>A mathematical demonstration of the limiting case for this electrostatic barrier occurs in the limit of zero charge, or as the atomic numbers \( Z_1 \) and \( Z_2 \) approach zero. "
            r"As the charges vanish, the electrostatic potential \( V_C(r) \to 0 \), and the barrier height \( E_C \) vanishes. "
            r"Under this neutral-particle limit, the Schrödinger wave equation simplifies directly to the flat, unperturbed Helmholtz equation for a free particle, \( (\nabla^2 + k^2)\psi = 0 \), where the wave number is \( k = \sqrt{2\mu E}/\hbar \), and the tunneling probability \( P \) becomes exactly unity. "
            r"Consequently, the complex, repulsion-driven features of the interaction dissolve into the regularities of simple vacuum propagation, proving that the electrostatic barrier model is compatible with neutral particle dynamics. "
            r"This transition mathematically guarantees that the classical free-particle limit is recovered without any physical singularities, preserving the consistency of nuclear models across all charge scales. "
            r"The physical fields contract smoothly to their vacuum expectations, satisfying the correspondence principle.</p>"
        ),
        "identities": [
            {
                "id": "coulomb-barrier-identity-1-e01acce2-9f13364f",
                "title": "Coulomb Potential Energy",
                "equation": "V_C(r) = \\frac{Z_1 Z_2 e^2}{4\\pi \\epsilon_0 r}",
                "description": "Expresses the electrostatic potential energy between two charged nuclei."
            }
        ]
    }
}

with open("subfiles/batch_payload.json", "w") as f:
    json.dump(payload, f, indent=4)
print("Payload written successfully to subfiles/batch_payload.json")
