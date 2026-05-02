import json

file_path = "/srv/www/terra/app/config/content/categories.json"

with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 1. Condensed Matter Physics
data["condensed-matter"]["content"] = """<p>Condensed Matter Physics investigates the macroscopic and microscopic physical properties of matter in its condensed phases, primarily solids and liquids. Rooted in the principles of <a href="/physics/subtopic/quantum-mechanics" class="subtopic-link"><strong>Quantum Mechanics</strong></a> and <a href="/physics/subtopic/statistical-mechanics" class="subtopic-link"><strong>Statistical Mechanics</strong></a>, it seeks to understand how the complex interactions between vast numbers of atoms and electrons give rise to emergent phenomena like <a href="/physics/subtopic/superconductivity" class="subtopic-link"><strong>Superconductivity</strong></a>, magnetism, and topological phases.</p>

                    <h3>1. Crystal Lattices and Bloch's Theorem</h3>
                    <p>The foundation of solid-state physics relies on the periodicity of the <a href="/physics/subtopic/crystal-lattice" class="subtopic-link"><strong>Crystal Lattice</strong></a>. According to <a href="/physics/subtopic/blochs-theorem" class="subtopic-link"><strong>Bloch's Theorem</strong></a>, the energy eigenstates for an electron in a periodic potential are plane waves modulated by a periodic function. This yields the wave function \\( \\psi_{\\mathbf{k}}(\\mathbf{r}) = e^{i \\mathbf{k} \\cdot \\mathbf{r}} u_{\\mathbf{k}}(\\mathbf{r}) \\). The allowable energy states form continuous bands separated by band gaps, directly dictating whether a material behaves as a conductor, insulator, or semiconductor.</p>

                    <h3>2. The Fermi Gas and Electronic Heat Capacity</h3>
                    <p>In metals, conduction electrons can be approximated as a <a href="/physics/subtopic/free-electron-model" class="subtopic-link"><strong>Free Electron Gas</strong></a> obeying Fermi-Dirac statistics. At absolute zero, electrons fill states up to the <a href="/physics/subtopic/fermi-energy" class="subtopic-link"><strong>Fermi Energy</strong></a> (\\( E_F \\)). The probability of occupation at temperature \\( T \\) is given by \\( f(E) = \\frac{1}{e^{(E - \\mu)/k_B T} + 1} \\). This model successfully explains the linear temperature dependence of the electronic heat capacity at low temperatures, \\( C_v = \\gamma T \\), where only electrons near the Fermi surface contribute to thermal excitations.</p>

                    <h3>3. Lattice Vibrations and Phonons</h3>
                    <p>The thermal and acoustic properties of solids are mediated by quantized lattice vibrations known as <a href="/physics/subtopic/phonons" class="subtopic-link"><strong>Phonons</strong></a>. In the harmonic approximation, the Hamiltonian of the lattice is decoupled into independent quantum harmonic oscillators. The dispersion relation \\( \\omega(\\mathbf{q}) \\) defines the frequency of these modes. The <a href="/physics/subtopic/debye-model" class="subtopic-link"><strong>Debye Model</strong></a> approximates this at low temperatures, correctly predicting the lattice heat capacity dependence \\( C_v \\propto T^3 \\) and identifying the maximum phonon frequency, the Debye frequency \\( \\omega_D \\).</p>

                    <h3>4. Superconductivity and BCS Theory</h3>
                    <p>At critical low temperatures, certain materials undergo a phase transition to a state of zero electrical resistance, known as <a href="/physics/subtopic/superconductivity" class="subtopic-link"><strong>Superconductivity</strong></a>. This is microscopically explained by the <a href="/physics/subtopic/bcs-theory" class="subtopic-link"><strong>BCS Theory</strong></a>, where a weak attractive interaction mediated by phonons causes electrons to pair up into <a href="/physics/subtopic/cooper-pairs" class="subtopic-link"><strong>Cooper Pairs</strong></a>. The macroscopic ground state is separated from excited states by an energy gap \\( \\Delta \\), defined at absolute zero by the gap equation: \\\\[ \\Delta \\approx 1.764 k_B T_c \\\\] This gap prevents low-energy scattering, resulting in perfect conductivity and the Meissner effect.</p>

                    <h3>5. Magnetism and Exchange Interactions</h3>
                    <p>The magnetic properties of materials, such as ferromagnetism and antiferromagnetism, arise from the <a href="/physics/subtopic/exchange-interaction" class="subtopic-link"><strong>Exchange Interaction</strong></a> between electron spins, a purely quantum mechanical effect related to the Pauli exclusion principle. The <a href="/physics/subtopic/heisenberg-model" class="subtopic-link"><strong>Heisenberg Hamiltonian</strong></a> models this phenomenon: \\\\[ \\mathcal{H} = - \\sum_{\\langle i, j \\rangle} J_{ij} \\mathbf{S}_i \\cdot \\mathbf{S}_j \\\\] where \\( J_{ij} \\) is the exchange integral. A positive \\( J \\) aligns spins (ferromagnetism), while a negative \\( J \\) leads to anti-alignment.</p>

                    <h3>6. Topological Phases of Matter</h3>
                    <p>Modern condensed matter explores <a href="/physics/subtopic/topological-insulators" class="subtopic-link"><strong>Topological Phases of Matter</strong></a>, phases that do not break symmetries but are characterized by global topological invariants, such as the Chern number. In the <a href="/physics/subtopic/quantum-hall-effect" class="subtopic-link"><strong>Quantum Hall Effect</strong></a>, a two-dimensional electron gas in a strong magnetic field exhibits quantized Hall conductance \\( \\sigma_{xy} = \\nu \\frac{e^2}{h} \\). These systems feature insulating bulk states but robust, gapless conducting edge states protected by time-reversal symmetry.</p>"""
data["condensed-matter"]["formula_ids"] = [
    "bloch-theorem-8c31",
    "fermi-dirac-distribution-55ff",
    "heisenberg-hamiltonian-f5c7"
]

# 2. Fluid Dynamics and Nonlinear Systems
data["fluids-nonlinear"]["content"] = """<p>Fluid Dynamics is the comprehensive study of the macroscopic motion of continuous media, encompassing both liquids and gases. Coupled with the analysis of <a href="/physics/subtopic/nonlinear-dynamics" class="subtopic-link"><strong>Nonlinear Systems</strong></a>, it addresses complex phenomena ranging from laminar flow to turbulent chaos. This field utilizes a synthesis of vector calculus, conservation laws, and <a href="/physics/subtopic/chaos-theory" class="subtopic-link"><strong>Chaos Theory</strong></a> to explore the intricate, deeply nonlinear evolution of fluid parcels and dynamical states over time.</p>

                    <h3>1. The Navier-Stokes Equations</h3>
                    <p>The cornerstone of fluid dynamics is the <a href="/physics/subtopic/navier-stokes-equations" class="subtopic-link"><strong>Navier-Stokes Equations</strong></a>, which govern the momentum conservation of a viscous fluid. Derived from Newton's second law, the incompressible formulation is: \\\\[ \\rho \\left( \\frac{\\partial \\mathbf{u}}{\\partial t} + \\mathbf{u} \\cdot \\nabla \\mathbf{u} \\right) = -\\nabla p + \\mu \\nabla^2 \\mathbf{u} + \\mathbf{f} \\\\] The nonlinear convective term \\( \\mathbf{u} \\cdot \\nabla \\mathbf{u} \\) is responsible for the rich complexity of fluid motion, coupling velocity components and leading to the energy cascade observed in turbulent regimes.</p>

                    <h3>2. Conservation of Mass and the Continuity Equation</h3>
                    <p>Fundamental to any fluid analysis is the conservation of mass, expressed through the <a href="/physics/subtopic/continuity-equation" class="subtopic-link"><strong>Continuity Equation</strong></a>. In differential form, it equates the rate of change of density to the divergence of the mass flux: \\( \\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0 \\). For an incompressible fluid where density \\( \\rho \\) is constant, this rigorously reduces to \\( \\nabla \\cdot \\mathbf{u} = 0 \\), restricting the velocity field to be purely solenoidal.</p>

                    <h3>3. Bernoulli's Principle and Potential Flow</h3>
                    <p>In the limit of inviscid, irrotational flow (where \\( \\nabla \\times \\mathbf{u} = 0 \\)), the velocity field can be represented by a scalar potential \\( \\mathbf{u} = \\nabla \\phi \\). Along a streamline in a steady, incompressible flow, energy conservation yields <a href="/physics/subtopic/bernoullis-principle" class="subtopic-link"><strong>Bernoulli's Principle</strong></a>: \\\\[ \\frac{1}{2} \\rho v^2 + p + \\rho g z = \\text{constant} \\\\] This powerful theorem relates kinetic energy, static pressure, and gravitational potential energy, serving as the basis for aerodynamics and hydrostatics.</p>

                    <h3>4. Vorticity and Circulation</h3>
                    <p>To study the rotational nature of fluid motion, physicists define <a href="/physics/subtopic/vorticity" class="subtopic-link"><strong>Vorticity</strong></a> as \\( \\boldsymbol{\\omega} = \\nabla \\times \\mathbf{u} \\). According to Kelvin's Circulation Theorem, for an inviscid, barotropic fluid subject to conservative body forces, the circulation \\( \\Gamma = \\oint \\mathbf{u} \\cdot d\\mathbf{l} \\) around a closed material loop remains constant over time. The evolution of vorticity itself is governed by the <a href="/physics/subtopic/vorticity-equation" class="subtopic-link"><strong>Vorticity Transport Equation</strong></a>, highlighting the stretching and tilting of vortex tubes.</p>

                    <h3>5. The Reynolds Number and Turbulence</h3>
                    <p>The transition from smooth, laminar flow to chaotic <a href="/physics/subtopic/turbulence" class="subtopic-link"><strong>Turbulence</strong></a> is characterized by the dimensionless <a href="/physics/subtopic/reynolds-number" class="subtopic-link"><strong>Reynolds Number</strong></a> (\\( Re \\)): \\\\[ Re = \\frac{\\rho U L}{\\mu} \\\\] This ratio of inertial forces to viscous forces dictates the flow regime. At high \\( Re \\), inertial nonlinearities dominate, cascading kinetic energy from large macro-eddies down to the Kolmogorov microscale, where it is ultimately dissipated into heat by viscosity.</p>

                    <h3>6. Chaos Theory and Strange Attractors</h3>
                    <p>Beyond continuous fluids, the study of <a href="/physics/subtopic/nonlinear-dynamics" class="subtopic-link"><strong>Nonlinear Systems</strong></a> reveals that even simple deterministic differential equations can exhibit extreme sensitivity to initial conditions&mdash;a hallmark of <a href="/physics/subtopic/chaos-theory" class="subtopic-link"><strong>Chaos Theory</strong></a>. Systems such as the <a href="/physics/subtopic/lorenz-equations" class="subtopic-link"><strong>Lorenz Attractor</strong></a> describe chaotic convection, where trajectories in phase space converge onto a fractal structure known as a strange attractor, making long-term predictability fundamentally impossible.</p>"""
data["fluids-nonlinear"]["formula_ids"] = [
    "navier-stokes-momentum-8c31",
    "bernoulli-equation-55ff",
    "reynolds-number-f5c7"
]

# 3. Mathematical Methods in Physics
data["mathematical-methods"]["content"] = """<p>Mathematical Methods in Physics provides the rigorous formal language required to map the fundamental mechanics of the universe. Serving as the essential bridge between pure abstract mathematics and theoretical physics, it encompasses advanced techniques in <a href="/physics/subtopic/differential-geometry" class="subtopic-link"><strong>Differential Geometry</strong></a>, <a href="/physics/subtopic/group-theory" class="subtopic-link"><strong>Group Theory</strong></a>, and <a href="/physics/subtopic/functional-analysis" class="subtopic-link"><strong>Functional Analysis</strong></a>. These tools constitute the definitive <strong>Universal Calculus</strong> enabling the formulation of everything from quantum state spaces to the spacetime curvature of general relativity.</p>

                    <h3>1. Complex Analysis and Contour Integration</h3>
                    <p>The extension of calculus to the complex plane is indispensable for theoretical physics. <a href="/physics/subtopic/complex-analysis" class="subtopic-link"><strong>Complex Analysis</strong></a> hinges on analytic functions which satisfy the Cauchy-Riemann equations. The powerful <a href="/physics/subtopic/cauchy-residue-theorem" class="subtopic-link"><strong>Residue Theorem</strong></a> states that the closed contour integral of a meromorphic function is determined solely by its singularities: \\\\[ \\oint_C f(z) dz = 2\\pi i \\sum \\text{Res}(f, z_k) \\\\] This theorem is crucial for evaluating difficult real integrals in quantum mechanics and calculating Feynman propagators.</p>

                    <h3>2. Linear Algebra and Hilbert Spaces</h3>
                    <p>Quantum mechanics demands the mathematical structure of infinite-dimensional <a href="/physics/subtopic/hilbert-spaces" class="subtopic-link"><strong>Hilbert Spaces</strong></a>. Physical states are represented as vectors \\( |\\psi\\rangle \\), and observables are Hermitian linear operators \\( \\hat{A} \\). The <a href="/physics/subtopic/spectral-theorem" class="subtopic-link"><strong>Spectral Theorem</strong></a> guarantees that these operators have real eigenvalues, defining the possible outcomes of a measurement. The geometry of this space, governed by the inner product \\( \\langle \\phi | \\psi \\rangle \\), directly yields transition amplitudes and probabilities.</p>

                    <h3>3. Differential Equations and Green's Functions</h3>
                    <p>Most laws of physics are expressed as partial differential equations (PDEs), from the heat equation to the Schrödinger equation. A sophisticated method for solving inhomogeneous linear PDEs involves <a href="/physics/subtopic/greens-functions" class="subtopic-link"><strong>Green's Functions</strong></a>. By finding the solution \\( G(x, x') \\) to a point source \\( L G(x, x') = \\delta(x - x') \\) (where \\( L \\) is a differential operator and \\( \\delta \\) is the Dirac delta), the general solution for any source distribution \\( \\rho(x) \\) is elegantly constructed via the integral \\( \\psi(x) = \\int G(x, x') \\rho(x') dx' \\).</p>

                    <h3>4. Group Theory and Representation</h3>
                    <p>The symmetry properties of physical systems are formally categorized by <a href="/physics/subtopic/group-theory" class="subtopic-link"><strong>Group Theory</strong></a>. In particle physics, continuous symmetries are described by <a href="/physics/subtopic/lie-groups" class="subtopic-link"><strong>Lie Groups</strong></a> (such as SU(2) and SU(3)), generated by corresponding Lie algebras. The commutation relations between generators, \\( [T_a, T_b] = i f_{abc} T_c \\), dictate the structure constants of the group. The representations of these groups define the multiplet structures of elementary particles in the Standard Model.</p>

                    <h3>5. Differential Geometry and Tensors</h3>
                    <p>General relativity necessitates the language of <a href="/physics/subtopic/differential-geometry" class="subtopic-link"><strong>Differential Geometry</strong></a> to describe physics on curved manifolds. Vectors and dual vectors are generalized into <a href="/physics/subtopic/tensor-calculus" class="subtopic-link"><strong>Tensors</strong></a>. The covariant derivative \\( \\nabla_\\mu \\) replaces the partial derivative, utilizing Christoffel symbols \\( \\Gamma^\\lambda_{\\mu\\nu} \\) to ensure equations remain invariant under arbitrary coordinate transformations. The curvature of the manifold itself is captured by the Riemann tensor \\( R^\\rho_{\\sigma\\mu\\nu} \\).</p>

                    <h3>6. The Calculus of Variations</h3>
                    <p>The deep underlying principle of both classical and quantum field theory is formulated through the <a href="/physics/subtopic/calculus-of-variations" class="subtopic-link"><strong>Calculus of Variations</strong></a>. Instead of finding the extrema of functions, it seeks the stationary points of functionals, specifically the action integral \\( S = \\int \\mathcal{L} dt \\). Minimizing the action yields the <a href="/physics/subtopic/euler-lagrange-equations" class="subtopic-link"><strong>Euler-Lagrange Equations</strong></a>: \\\\[ \\frac{\\partial \\mathcal{L}}{\\partial q_i} - \\frac{d}{dt} \\left( \\frac{\\partial \\mathcal{L}}{\\partial \\dot{q}_i} \\right) = 0 \\\\] which provide a coordinate-independent derivation of the fundamental equations of motion.</p>"""
data["mathematical-methods"]["formula_ids"] = [
    "cauchy-residue-theorem-8c31",
    "euler-lagrange-equation-55ff",
    "lie-algebra-commutation-f5c7"
]

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)
