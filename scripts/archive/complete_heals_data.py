#!/usr/bin/env python3
"""
scripts/maintenance/complete_heals_data.py

Authoritative, mathematically rigorous replacement dictionary for all legacy
formulas with broken delimiters or leaked macros.
"""

COMPLETE_REPAIRS = {
    ("electromagnetism-5ad10a96", "limits_and_boundary"): (
        "In the non-relativistic limit, as $v \\ll c$ (where $c$ is the speed of light), the Lorentz factor $\\gamma$ approaches 1. "
        "In this case, the equation simplifies to $\\mathbf{E}_{\\perp}' \\approx \\mathbf{E}_{\\perp} + \\mathbf{v} \\times \\mathbf{B}$. "
        "This approximation highlights how a moving observer perceives an additional electric field $\\mathbf{v} \\times \\mathbf{B}$ "
        "due to their motion through a magnetic field, which is fundamental to concepts like motional electromotive force. "
        "As $v \\to c$, the Lorentz factor $\\gamma$ approaches infinity. If the term $(\\mathbf{E}_{\\perp} + \\mathbf{v} \\times \\mathbf{B})$ "
        "is non-zero, the perpendicular electric field $\\mathbf{E}_{\\perp}'$ in the moving frame would become infinitely large, "
        "signifying the strong relativistic compression of fields and energy density for observers approaching the speed of light relative to a source."
    ),
    ("quantum-commutator-limit", "conceptual_definition"): (
        "The equation $[\\hat{x}, \\hat{p}] \\to 0$ in quantum mechanics signifies a fundamental limit where the operators representing position, "
        "$\\hat{x}$, and momentum, $\\hat{p}$, become simultaneously measurable with arbitrary precision. In quantum mechanics, operators do not generally "
        "commute, meaning the order in which they are applied matters. The commutator $[A, B] = AB - BA$ is a measure of this non-commutativity. "
        "For the position and momentum operators, their commutator is given by $[\\hat{x}, \\hat{p}] = i\\hbar$, where $i$ is the imaginary unit "
        "and $\\hbar$ is the reduced Planck constant. The condition $[\\hat{x}, \\hat{p}] \\to 0$ thus implies that $i\\hbar \\to 0$, which can only "
        "occur in a classical limit where Planck's constant $\\hbar \\to 0$. This limit essentially describes the transition from quantum mechanics "
        "to classical mechanics, where conjugate variables can be known precisely at the same time."
    ),
    ("quantum-commutator-limit", "limits_and_boundary"): (
        "The limit $[\\hat{x}, \\hat{p}] \\to 0$ signifies the classical limit of quantum mechanics. This occurs when the reduced Planck constant "
        "$\\hbar \\to 0$. In this limit, the uncertainty principle $\\Delta x \\Delta p \\geq \\hbar/2$ implies that $\\Delta x \\Delta p \\to 0$, "
        "meaning that both position $x$ and momentum $p$ can be known with arbitrary precision simultaneously. This is characteristic of classical "
        "mechanics, where physical systems are described by definite trajectories with precisely defined positions and momenta at any given time. "
        "Conversely, as $\\hbar$ becomes significant (i.e., at microscopic scales), the commutator is non-zero, and quantum effects like superposition "
        "and inherent uncertainty dominate."
    ),
    ("gauge-transformation-identity-1-56b6882c-de339f65", "limits_and_boundary"): (
        "If $\\Lambda$ is a constant, there is no change in potentials, and hence no change in fields. If $\\Lambda$ is zero, the potentials remain unchanged. "
        "In the context of electrostatics (time-independent fields), the transformation simplifies to $\\mathbf{A} \\to \\mathbf{A}$ (as $\\partial \\Lambda / \\partial t = 0$) "
        "and $\\Phi \\to \\Phi - \\nabla \\Lambda$, which means only the scalar potential changes by a spatial gradient, equivalent to shifting the zero potential reference."
    ),
    ("field-operator-acting-on-test-function", "symmetry_origin"): (
        "This formula arises from the need to define quantum field operators as distributions, ensuring they are well-defined when acting on the Hilbert space of states. "
        "The integration against a test function $f(x)$ effectively 'smoothes out' the potentially singular nature of the field operator $\\hat{\\phi}(x)$ at a point. "
        "This process is coordinate-invariant because the integral is over spacetime, and the test function $f(x)$ transforms appropriately under coordinate transformations, "
        "ensuring that the resulting operator $\\hat{\\phi}(f)$ is independent of the chosen coordinate system, thereby reflecting the underlying spacetime symmetries."
    ),
    ("rotational-power", "interpretation"): (
        "In this equation, $P$ represents the instantaneous rotational power, measured in watts (W). $\\boldsymbol{\\tau}$ is the net torque vector acting on the rotating body, "
        "measured in newton-meters ($\\mathrm{N} \\cdot \\mathrm{m}$). Torque is the rotational analogue of force, representing the tendency of a force to cause an object to rotate. "
        "$\\boldsymbol{\\omega}$ is the angular velocity vector, measured in radians per second (rad/s), describing the rate and axis of rotation. The dot product ($\\cdot$) "
        "between torque and angular velocity signifies that only the component of torque that acts parallel (or antiparallel) to the angular velocity contributes to the power. "
        "If torque and angular velocity are in the same direction, power is positive, meaning work is being done on the body to increase its rotational kinetic energy. "
        "If they are in opposite directions, power is negative, meaning work is being extracted (e.g., due to braking or friction). If torque is perpendicular to the angular velocity, "
        "no work is done, and rotational power is zero."
    ),
    ("rotational-power", "symmetry_origin"): (
        "This formula can be derived from the definition of work and power. Linear power is given by $P = \\boldsymbol{F} \\cdot \\boldsymbol{v}$, where $\\boldsymbol{F}$ is force "
        "and $\\boldsymbol{v}$ is velocity. For a small displacement $d\\boldsymbol{r}$, the work done is $dW = \\boldsymbol{F} \\cdot d\\boldsymbol{r}$. "
        "In rotational motion, the infinitesimal displacement tangential to a circle of radius $r$ is $d\\boldsymbol{s} = d\\boldsymbol{\\theta} \\times \\boldsymbol{r}$, "
        "and the corresponding linear velocity is $\\boldsymbol{v} = \\boldsymbol{\\omega} \\times \\boldsymbol{r}$. The torque is $\\boldsymbol{\\tau} = \\boldsymbol{r} \\times \\boldsymbol{F}$. "
        "Thus, $dW = \\boldsymbol{F} \\cdot (\\boldsymbol{\\omega} \\times \\boldsymbol{r})$. Using the vector triple product identity "
        "$\\boldsymbol{A} \\cdot (\\boldsymbol{B} \\times \\boldsymbol{C}) = \\boldsymbol{C} \\cdot (\\boldsymbol{A} \\times \\boldsymbol{B})$, "
        "we get $dW = \\boldsymbol{\\omega} \\cdot (\\boldsymbol{r} \\times \\boldsymbol{F}) = \\boldsymbol{\\omega} \\cdot \\boldsymbol{\\tau}$. "
        "Dividing by the infinitesimal time interval $dt$ gives the power: $P = \\frac{dW}{dt} = \\boldsymbol{\\omega} \\cdot \\boldsymbol{\\tau}$. "
        "This derivation highlights the direct analogy between linear and rotational dynamics and stems from the fundamental definition of work."
    ),
    ("wave-equation-four-potential", "interpretation"): (
        "The equation $\\Box A^\\mu = -\\mu_0 J^\\mu$ dictates the behavior of the electromagnetic four-potential, denoted by $A^\\mu$. "
        "The operator $\\Box$ is the d'Alembert operator, defined in Minkowski spacetime as $\\Box = \\frac{1}{c^2} \\frac{\\partial^2}{\\partial t^2} - \\nabla^2$, "
        "where $c$ is the speed of light in vacuum and $\\nabla^2$ is the Laplacian operator. The four-potential $A^\\mu = (\\frac{\\phi}{c}, \\vec{A})$ "
        "is a four-vector that combines the scalar electric potential $\\phi$ and the vector magnetic potential $\\vec{A}$. "
        "The term $J^\\mu$ is the four-current density, a four-vector representing the distribution of electric charge and current, "
        "$J^\\mu = (c\\rho, \\mathbf{J})$, where $\\rho$ is the charge density and $\\mathbf{J}$ is the current density. The constant $\\mu_0$ is the permeability of free space. "
        "The equation signifies that changes in the electromagnetic potentials (driven by sources) propagate as waves through spacetime at the speed of light. "
        "In a vacuum where $J^\\mu = 0$, the equation simplifies to $\\Box A^\\mu = 0$, which describes the propagation of free electromagnetic waves."
    ),
    ("massless-or-high-energy-approximation-15771775", "conceptual_definition"): (
        "This approximation is derived from the full relativistic energy-momentum relation, $E^2 = (pc)^2 + (m_0 c^2)^2$. "
        "When the rest mass energy term $(m_0 c^2)^2$ is significantly smaller than the momentum energy term $(pc)^2$, it can be neglected, "
        "leading to $E^2 \\approx (pc)^2$. For massless particles, where $m_0 = 0$, this approximation becomes an exact equality, $E = pc$."
    ),
    ("magnitude-squared-angular-momentum", "interpretation"): (
        "The angular momentum $\\mathbf{L}$ of a rigid body is a vector quantity that characterizes its rotational motion. "
        "For a rigid body, it is related to its angular velocity $\\boldsymbol{\\omega}$ (a vector describing the axis and speed of rotation) "
        "and its moment of inertia tensor $\\mathbf{I}$ (a second-rank tensor describing how the mass is distributed relative to the axis of rotation). "
        "The angular momentum vector is generally given by $\\mathbf{L} = \\mathbf{I} \\cdot \\boldsymbol{\\omega}$. "
        "The square of the magnitude of the angular momentum, $L^2 = |\\mathbf{L}|^2$, is calculated as "
        "$L^2 = \\mathbf{L} \\cdot \\mathbf{L} = (\\mathbf{I} \\cdot \\boldsymbol{\\omega}) \\cdot (\\mathbf{I} \\cdot \\boldsymbol{\\omega})$. "
        "The correct formulation for the squared magnitude in tensor notation is $L^2 = \\boldsymbol{\\omega} \\cdot \\mathbf{I} \\cdot \\boldsymbol{\\omega}$. "
        "This highlights that angular momentum is mediated by the complex distribution of mass as described by the moment of inertia tensor."
    ),
    ("monochromaticity-6968c906", "limits_and_boundary"): (
        "This equation represents an idealized wave with infinite spatial and temporal extent. In realistic scenarios, waves are always 'quasi-monochromatic' "
        "due to finite duration and spatial extent, leading to a spread in frequencies. If $\\omega \\to 0$, the wave degenerates into a static electric field "
        "(if $\\mathbf{k} \\neq \\mathbf{0}$) or a spatially uniform static field (if $\\mathbf{k} = \\mathbf{0}$), losing its oscillatory nature. "
        "If $|\\mathbf{k}| \\to 0$, the wave becomes spatially uniform, oscillating only in time. If $\\mathbf{E}_0 = \\mathbf{0}$, there is no electric field, "
        "indicating the absence of a wave. The propagation speed $c = \\omega / |\\mathbf{k}|$ is implicitly fixed by the properties of the medium (or $c$ for vacuum)."
    ),
    ("coupling-constant-qft-identity-1-7929f982-2f73da30", "limits_and_boundary"): (
        "As $\\mu^2 \\to \\mu_0^2$, the logarithm term $\\ln(\\frac{\\mu^2}{\\mu_0^2}) \\to 0$, and $\\alpha(\\mu^2) \\to \\alpha(\\mu_0^2)$, "
        "recovering the reference value. As $\\mu^2 \\to \\infty$, the denominator approaches negative infinity (assuming $\\alpha(\\mu_0^2) > 0$), "
        "which would imply $\\alpha(\\mu^2) \\to 0$. However, this simple formula is an approximation valid only for $\\mu^2 \\gg m_e^2$ "
        "where $m_e$ is the electron mass, and it breaks down if the denominator approaches zero (Landau pole). "
        "For $\\mu^2 \\to 0$ (or $\\mu^2 \\ll \\mu_0^2$), the logarithm becomes large and negative, leading to a very large $\\alpha(\\mu^2)$, "
        "consistent with the idea that the interaction gets stronger at longer distances due to screening effects."
    ),
    ("matter-density-parameter-one", "conceptual_definition"): (
        "The formula $\\Omega_m \\to 1$ describes a critical condition in cosmology where the total matter density of the universe approaches the critical density "
        "required for a spatially flat geometry. $\\Omega_m$ is the density parameter for matter, which is the ratio of the actual average matter density in the universe "
        "to the critical density. When $\\Omega_m = 1$, the universe is spatially flat, neither positively curved (like a sphere) nor negatively curved (like a saddle). "
        "The arrow $\\to$ signifies that this condition represents a limit or a state that the universe might be approaching or be very close to."
    ),
    ("matter-density-parameter-one", "interpretation"): (
        "In this context, $\\Omega_m$ is the central parameter. It is defined as $\\Omega_m = \\frac{\\rho_m}{\\rho_c}$, where $\\rho_m$ is the actual average "
        "density of matter (both baryonic and dark matter) in the universe, and $\\rho_c$ is the critical density. The critical density is the precise density "
        "required for the universe to be spatially flat. The condition $\\Omega_m \\to 1$ implies that the total amount of matter in the universe is very close "
        "to this critical value. If $\\Omega_m > 1$, the universe would be spatially closed (positively curved); if $\\Omega_m < 1$, it would be spatially open "
        "(negatively curved). The arrow $\\to$ suggests that the universe's matter density is either approaching this value over time, or it is currently very near "
        "this value. This condition is closely related to the geometry of spacetime as dictated by Einstein's field equations in FLRW cosmology."
    ),
    ("pressure-gradient-force-density-ea32abd5", "conceptual_definition"): (
        "In fluid dynamics, pressure is a scalar field. The negative gradient of pressure, $-\\nabla P$, quantifies the spatial rate of change of pressure and its direction. "
        "It represents a force density, meaning force per unit volume, that drives fluid motion. This force arises because fluid particles experience different pressures on their opposing faces."
    ),
    ("pressure-gradient-force-density-ea32abd5", "interpretation"): (
        "The term $-\\nabla P$ is the pressure gradient force density. It indicates that fluid accelerates in the direction opposite to the steepest increase in pressure. "
        "If pressure is uniform, this term is zero, and there is no pressure-driven flow. This force is crucial for phenomena like buoyancy, wind generation, "
        "and the flow of liquids through pipes, acting as a primary driver for fluid motion in the absence of other forces."
    ),
    ("force-from-potential-energy-gradient-a09c32ed", "limits_and_boundary"): (
        "This formula is valid for conservative forces only, meaning forces for which the work done moving a particle between two points is independent of the path taken. "
        "It applies in one-dimensional systems or can be generalized to three dimensions using the gradient operator $(\\mathbf{F} = -\\nabla V)$. "
        "It assumes the potential energy function $V(x)$ is differentiable."
    ),
    ("density-sum-34098eaf", "symmetry_origin"): (
        "This formula is derived from the Friedmann equations of General Relativity. In an expanding universe, the critical density is defined as "
        "$\\rho_c = \\frac{3 H^2}{8\\pi G}$, where $H = \\frac{\\dot{a}}{a}$ is the Hubble parameter. Substituting the respective density parameters "
        "demonstrates that spatial flatness directly corresponds to the total density parameter summing to unity."
    ),
    ("poisson-equation-for-magnetic-vector-potential-8dc89e7b", "conceptual_definition"): (
        "The magnetic vector potential, $\\mathbf{A}$, is a vector field from which the magnetic field $\\mathbf{B}$ can be derived via $\\mathbf{B} = \\nabla \\times \\mathbf{A}$. "
        "This equation, often referred to as the Poisson equation for $\\mathbf{A}$, establishes a direct relationship between the distribution of electric current density, $\\mathbf{J}$, "
        "and the magnetic vector potential it generates. It is a fundamental equation in magnetostatics and electrodynamics, providing a convenient way to calculate magnetic fields from current sources."
    ),
    ("moment-inertia-tensor-component", "symmetry_origin"): (
        "This formula arises from the fundamental principles of rotational dynamics and Newton's second law for rigid bodies, where angular momentum $\\mathbf{L}$ is related to angular velocity "
        "$\\boldsymbol{\\omega}$ by $\\mathbf{L} = \\mathbf{I} \\cdot \\boldsymbol{\\omega}$ and torque $\\boldsymbol{\\tau}$ is related to angular acceleration $\\boldsymbol{\\alpha}$ by "
        "$\\boldsymbol{\\tau} = \\mathbf{I} \\cdot \\boldsymbol{\\alpha}$, with $\\mathbf{I}$ being the moment of inertia tensor. The tensor form is necessary to accurately describe rotation "
        "in three dimensions, especially for asymmetric bodies or when considering rotations about arbitrary axes, as it is coordinate-dependent."
    ),
    ("vector-relation-potential-identity-1-50f70efd-0e0064f7", "interpretation"): (
        "This equation is a powerful statement in vector calculus, known as Stokes' Theorem, applied specifically to the magnetic vector potential $\\mathbf{A}$. "
        "The left side, $\\oint_C \\mathbf{A} \\cdot d\\mathbf{r}$, represents the line integral of the vector potential $\\mathbf{A}$ around a closed curve $C$. "
        "The right side, $\\int_S \\mathbf{B} \\cdot d\\mathbf{a}$, is the magnetic flux through a surface $S$ whose boundary is the curve $C$. "
        "Stokes' theorem in its general form states that $\\oint_C \\mathbf{F} \\cdot d\\mathbf{r} = \\int_S (\\nabla \\times \\mathbf{F}) \\cdot d\\mathbf{a}$ for any vector field $\\mathbf{F}$. "
        "By substituting the definition of the magnetic field $\\mathbf{B} = \\nabla \\times \\mathbf{A}$, the theorem directly links the line integral of $\\mathbf{A}$ to the flux of $\\mathbf{B}$."
    ),
    ("geodesic-link-d4b6b935", "conceptual_definition"): (
        "The equation $\\nabla = \\partial \\text{ (Covariant = Partial)}$ is a fundamental statement in differential geometry and physics, particularly in the context of general relativity. "
        "The covariant derivative, $\\nabla$, is a generalization of the directional derivative that accounts for the change in basis vectors as one moves across a curved manifold. "
        "The partial derivative, $\\partial$, simply measures the rate of change of a component with respect to a coordinate."
    ),
    ("geodesic-link-d4b6b935", "interpretation"): (
        "The equation $\\nabla = \\partial$ conceptually equates the covariant derivative with the partial derivative. In a more complete tensor calculus context, this equality implies "
        "that the connection coefficients (Christoffel symbols, $\\Gamma^k_{ij}$) are zero in the chosen coordinate system at the evaluated point, such as in local inertial frames."
    ),
    ("geodesic-link-d4b6b935", "limits_and_boundary"): (
        "This equation is fundamentally about the absence of curvature. As spacetime curvature tends to zero (approaching a flat Minkowski spacetime), the Christoffel symbols become zero, "
        "and the covariant derivative $\\nabla$ becomes indistinguishable from the ordinary partial derivative $\\partial$ in Cartesian coordinates."
    ),
    ("torque-angular-momentum-relation", "interpretation"): (
        "The equation $\\boldsymbol{\\tau} = \\frac{d\\mathbf{L}}{dt} = \\mathbf{I} \\cdot \\dot{\\boldsymbol{\\omega}} + \\boldsymbol{\\omega} \\times (\\mathbf{I} \\cdot \\boldsymbol{\\omega})$ "
        "governs the rotational dynamics of a rigid body expressed in a body-fixed reference frame. $\\boldsymbol{\\tau}$ represents the net external torque applied to the body. "
        "The term $\\mathbf{I} \\cdot \\dot{\\boldsymbol{\\omega}}$ accounts for angular acceleration, while the cross product term "
        "$\\boldsymbol{\\omega} \\times (\\mathbf{I} \\cdot \\boldsymbol{\\omega})$ accounts for gyroscopic precession arising from the rotation of the frame itself."
    ),
    ("timelike-condition-66404b96", "limits_and_boundary"): (
        "As $dt \\to 0$ and $d\\mathbf{x} \\neq 0$, the condition $c^2 dt^2 - d\\mathbf{x}^2 > 0$ becomes impossible to satisfy, as the left side approaches a negative value, "
        "indicating a spacelike interval. Conversely, if $d\\mathbf{x} \\to 0$ while $dt \\neq 0$, the condition $c^2 dt^2 - d\\mathbf{x}^2 > 0$ is easily met, indicating a timelike interval. "
        "If both $dt \\to 0$ and $d\\mathbf{x} \\to 0$, the interval $ds^2$ approaches zero, representing lightlike or null intervals along photon geodesics."
    ),
    ("geometric-fall-820c9fbf", "interpretation"): (
        "In the formula $\\beta = 2 \\frac{a_1 - a_2}{a_1 + a_2}$, $\\beta$ is a dimensionless parameter representing the deviation from a geometric progression. "
        "For instance, if $a_2 = a_1 r$, then $\\beta = 2 \\frac{a_1 - a_1 r}{a_1 + a_1 r} = 2 \\frac{1-r}{1+r}$. If $r=1$, meaning $a_1 = a_2$ (a constant sequence), then $\\beta = 0$."
    ),
    ("geometric-fall-820c9fbf", "limits_and_boundary"): (
        "As the difference between $a_1$ and $a_2$ approaches zero (i.e., $a_1 \\to a_2$), the numerator $(a_1 - a_2)$ approaches zero, making $\\beta \\to 0$. "
        "In the limit where $a_1 \\gg a_2$, $\\beta \\approx 2 \\frac{a_1}{a_1} = 2$. Conversely, if $a_2 \\gg a_1$, then $\\beta \\approx 2 \\frac{-a_2}{a_2} = -2$."
    ),
    ("geometric-shield-e45b70a1", "limits_and_boundary"): (
        "As the distance $|\\mathbf{r} - \\mathbf{r}'|$ approaches infinity ($|\\mathbf{r} - \\mathbf{r}'| \\to \\infty$), the value of $G_{\\text{free}}$ approaches zero, "
        "meaning the potential field vanishes far from the source. Conversely, as the distance between the two points approaches zero ($|\\mathbf{r} - \\mathbf{r}'| \\to 0$), "
        "the value of $G_{\\text{free}}$ approaches infinity, representing a singularity at the location of the point source."
    ),
    ("geometric-shield-e45b70a1", "symmetry_origin"): (
        "In mathematical terms, it is the fundamental solution (or Green's function) to the Laplace equation $\\nabla^2 G = 0$ or Poisson equation $\\nabla^2 G = -\\delta(\\mathbf{r} - \\mathbf{r}')$. "
        "The $1/r$ dependence is a direct consequence of the three-dimensional nature of physical space, consistent with Gauss's law."
    ),
    ("potential-link-1f375717", "interpretation"): (
        "In this relativistic formulation of electromagnetism, the electromagnetic field is encapsulated by the antisymmetric tensor $F_{\\mu\\nu}$. "
        "The indices $\\mu$ and $\\nu$ range from 0 to 3, representing spacetime coordinates (0 for time, 1, 2, 3 for spatial dimensions). "
        "The term $\\partial_\\mu$ represents the four-gradient operator, which is $(\\frac{1}{c} \\frac{\\partial}{\\partial t}, \\nabla)$. "
        "The equation explicitly states that each component of the electromagnetic field tensor $F_{\\mu\\nu}$ is formed by subtracting the derivatives of the four-potential."
    ),
    ("exponential-expansion", "limits_and_boundary"): (
        "As time $t$ approaches infinity, if $H > 0$, the quantity $a(t)$ grows without bound, approaching infinity. If $H < 0$, $a(t)$ decays towards zero. "
        "As time $t$ approaches negative infinity, the behavior is inverted. At $t = 0$, $a(0) = a_0 e^{H \\cdot 0} = a_0 e^0 = a_0$, recovering the initial condition."
    ),
    ("zero-angular-momentum", "interpretation"): (
        "In this formula, $\\mathbf{J}$ represents the total angular momentum of a system. It is a vector quantity, meaning it has both magnitude and direction. "
        "The arrow $(\\to)$ signifies a limiting process, indicating that the system's angular momentum is approaching zero, or that we are considering a state characterized by zero net angular momentum."
    ),
    ("zero-angular-momentum", "limits_and_boundary"): (
        "As the components of angular momentum approach zero, the system transitions from a state of rotation or orbit to a state of no net rotation or orbit. "
        "For a point mass, this means $\\mathbf{r} = \\mathbf{0}$ (the mass is at the origin) or $\\mathbf{v} = \\mathbf{0}$ (the mass is stationary). "
        "For a system of particles, it implies $\\sum_i \\mathbf{r}_i \\times (m_i \\mathbf{v}_i) = \\mathbf{0}$."
    ),
    ("work-by-torque", "symmetry_origin"): (
        "This formula originates from the definition of work in rotational dynamics and is directly analogous to the linear definition of work. "
        "The infinitesimal work done by this force is $dW = \\mathbf{F} \\cdot d\\mathbf{r} = \\mathbf{F} \\cdot (d\\boldsymbol{\\theta} \\times \\mathbf{r})$. "
        "Using the vector identity $\\mathbf{A} \\cdot (\\mathbf{B} \\times \\mathbf{C}) = (\\mathbf{A} \\times \\mathbf{B}) \\cdot \\mathbf{C}$, "
        "and noting $\\boldsymbol{\\tau} = \\mathbf{r} \\times \\mathbf{F}$, we obtain $dW = \\boldsymbol{\\tau} \\cdot d\\boldsymbol{\\theta}$."
    ),
    ("canonical-commutation-field-momentum", "interpretation"): (
        "The equation $\\{\\Phi(\\mathbf{x}), \\Pi(\\mathbf{y})\\} = \\delta^3(\\mathbf{x}-\\mathbf{y})$ is the equal-time canonical commutation relation for a classical field theory. "
        "The curly braces $\\{\\cdot, \\cdot\\}$ denote the Poisson bracket in classical mechanics, which is replaced by the commutator in quantum field theory."
    ),
    ("field-canonical-momentum-density-fd1adb0d", "limits_and_boundary"): (
        "This definition is valid within the framework of classical field theory where the Lagrangian density $\\mathcal{L}$ is a function of the field $\\phi$, "
        "its time derivative $\\dot{\\phi}$, and its spatial derivatives $\\nabla \\phi$. It assumes a local Lagrangian density without higher-order derivatives."
    ),
    ("stokes-theorem-for-electric-field-be47c565", "interpretation"): (
        "The left side of the equation, $\\oint \\mathbf{E} \\cdot d\\mathbf{l}$, represents the circulation of the electric field around a closed loop. "
        "The right side, $\\int (\\nabla \\times \\mathbf{E}) \\cdot d\\mathbf{a}$, represents the flux of the curl of the electric field through an open surface bounded by that loop. "
        "The dot product $(\\nabla \\times \\mathbf{E}) \\cdot d\\mathbf{a}$ evaluates the normal component of the curl across each surface element."
    ),
    ("stokes-theorem", "interpretation"): (
        "Stokes' Theorem establishes an equivalence between a boundary line integral and a surface flux integral. "
        "The left-hand side, $\\oint_C \\mathbf{A} \\cdot d\\mathbf{l}$, represents the line integral of the vector field $\\mathbf{A}$ around closed curve $C$. "
        "The right-hand side, $\\int_S (\\nabla \\times \\mathbf{A}) \\cdot d\\mathbf{a}$, represents the surface integral of the curl of $\\mathbf{A}$ through surface $S$ bounded by $C$."
    ),
    ("rotation-operator", "limits_and_boundary"): (
        "As the infinitesimal rotation angle $\\delta \\boldsymbol{\\theta}$ approaches zero ($|\\delta \\boldsymbol{\\theta}| \\to 0$), "
        "the operator $\\hat{R}(\\delta \\boldsymbol{\\theta})$ approaches the identity operator $\\hat{I}$, reflecting continuity of spatial rotations."
    ),
    ("differential-work-by-conservative-force-65197ed6", "conceptual_definition"): (
        "This formula represents the differential work ($dW = \\mathbf{F} \\cdot d\\mathbf{r}$) done by a conservative force $\\mathbf{F}$ over an infinitesimal displacement $d\\mathbf{r}$. "
        "Because $\\mathbf{F} = -\\nabla U$, the work is identically equal to the negative change in potential energy, $dW = -dU$."
    ),
    ("differential-work-by-conservative-force-65197ed6", "interpretation"): (
        "Physically, this equation states that the infinitesimal work done by a conservative force is equal to the negative change in potential energy. "
        "The term $-(\\nabla U) \\cdot d\\mathbf{r}$ explicitly shows how this work is directly linked to the spatial variation of the potential field along the displacement."
    ),
    ("differential-work-by-conservative-force-65197ed6", "limits_and_boundary"): (
        "This equation is strictly valid for conservative forces, which are path-independent and can be derived from a scalar potential energy function. "
        "It applies where $\\mathbf{F} = -\\nabla U$, requiring the potential field $U$ to be continuous and differentiable."
    ),
    ("definitive-solution-ee2ed125", "conceptual_definition"): (
        "The equations $\\nabla^2 V_1 = -\\rho / \\varepsilon_0$ and $\\nabla^2 V_2 = -\\rho / \\varepsilon_0$ represent Poisson's equation for electrostatic potentials. "
        "The operator $\\nabla^2$ is the Laplacian, defined as the divergence of the gradient, $\\nabla \\cdot (\\nabla V) = \\nabla^2 V$."
    ),
    ("definitive-solution-ee2ed125", "symmetry_origin"): (
        "Gauss's law in differential form states that the divergence of the electric field is proportional to charge density: $\\nabla \\cdot \\mathbf{E} = \\rho / \\varepsilon_0$. "
        "Because $\\mathbf{E} = -\\nabla V$, substituting yields $\\nabla \\cdot (-\\nabla V) = \\rho / \\varepsilon_0$, simplifying to $\\nabla^2 V = -\\rho / \\varepsilon_0$."
    ),
    ("electrostatic-potential-energy-of-two-charges-3fe3164b", "limits_and_boundary"): (
        "As $R \\to \\infty$, $V_C \\to 0$, meaning the charges exert no force on each other at infinite separation. "
        "As $R \\to 0$, $V_C \\to \\infty$, indicating that an infinite amount of work is required to bring like charges into contact."
    ),
    ("gradient-of-a-scalar-potential-4552642a", "conceptual_definition"): (
        "The gradient operator $(\\nabla)$ transforms a scalar field $U$, which assigns a scalar value to every point in space, into a vector field. "
        "This resulting vector field, $\\nabla U$, points in the direction of the greatest rate of increase of the scalar field."
    ),
    ("gradient-of-a-scalar-potential-4552642a", "interpretation"): (
        "Physically, for a potential energy field $U$, the gradient $\\nabla U$ represents the direction and magnitude of the steepest ascent of potential. "
        "In the context of conservative forces ($\\mathbf{F} = -\\nabla U$), the negative gradient indicates that force acts in the downhill direction."
    ),
    ("optical-theorem-for-forward-scattering-e74af25e", "limits_and_boundary"): (
        "In the optical theorem, the forward scattering limit $(i \\to i)$ evaluates elastic forward amplitude without change in momentum or internal state. "
        "As $k \\to 0$ (low energy limit), the scattering cross section approaches a constant determined by the s-wave scattering length."
    ),
    ("navier-stokes-momentum-fluids-27e5bf4d", "interpretation"): (
        "The Navier-Stokes momentum equation describes fluid acceleration driven by pressure gradients and viscous stresses. "
        "On the right-hand side, $-\\nabla p$ represents the pressure gradient force density, while $\\mu \\nabla^2 \\mathbf{u}$ represents viscous diffusion."
    ),
    ("navier-stokes-momentum-fluids-27e5bf4d", "limits_and_boundary"): (
        "In the limit of zero viscosity ($\\mu \\to 0$), the Navier-Stokes equations reduce to the Euler equations for inviscid flow. "
        "Conversely, in the low Reynolds number limit ($\\mathrm{Re} \\to 0$), viscous forces dominate over inertial terms, yielding the Stokes flow equations."
    ),
    ("electrostatic-scalar-potential-from-static-charge-density-138b5385", "conceptual_definition"): (
        "The electrostatic scalar potential, $\\Phi(\\mathbf{r})$, describes potential energy per unit charge. "
        "The electric field is derived via its negative gradient, $\\mathbf{E} = -\\nabla \\Phi$."
    ),
    ("gradient-of-a-scalar-wave-function-876a7237", "conceptual_definition"): (
        "The gradient operator $(\\nabla)$ applied to a scalar wave function $\\psi$ yields a spatial vector field $\\nabla \\psi$, "
        "measuring local directional variation in amplitude and phase."
    ),
    ("gradient-of-a-scalar-wave-function-876a7237", "interpretation"): (
        "In quantum mechanics, $\\nabla \\psi$ is proportional to the probability current density and local momentum expectation values."
    ),
    ("gradient-of-a-scalar-wave-function-876a7237", "limits_and_boundary"): (
        "For $\\nabla \\psi$ to be well-defined, $\\psi$ must be continuously differentiable across space. "
        "At infinite boundaries, localized wavefunctions satisfy $\\psi \\to 0$ and $\\nabla \\psi \\to \\mathbf{0}$."
    ),
    ("gradient-of-a-scalar-wave-function-876a7237", "symmetry_origin"): (
        "The gradient operator exhibits invariance under spatial translations and rotations, ensuring the resulting vector field $\\nabla \\psi$ transforms covariantly."
    ),
    ("emf-integral-definition-a3d86b92", "symmetry_origin"): (
        "The work done in moving a unit charge along a closed path is given by the line integral $\\oint \\mathbf{E} \\cdot d\\mathbf{l}$. "
        "In electrostatics, $\\nabla \\times \\mathbf{E} = \\mathbf{0}$, meaning $\\oint \\mathbf{E} \\cdot d\\mathbf{l} = 0$. In time-dependent electrodynamics, induction yields non-zero EMF."
    ),
    ("deceleration-parameter-limit", "interpretation"): (
        "The limit $q \\to -1$ corresponds to an expansion where $\\ddot{a}a \\approx \\dot{a}^2$, characteristic of exponential de Sitter expansion driven by dark energy."
    ),
    ("weak-field-approximation-of-metric-component-g00-dbd6cd97", "limits_and_boundary"): (
        "In the weak-field limit, as $\\Phi \\to 0$ far from gravitational sources, $g_{00} \\to -1$, recovering the flat Minkowski metric of Special Relativity."
    ),
    ("coulomb-gauge-identity-0e18071a", "conceptual_definition"): (
        "The Coulomb gauge condition, $\\nabla \\cdot \\mathbf{A} = 0$, eliminates the unphysical longitudinal degree of freedom of the vector potential."
    ),
    ("boltzmann-distribution", "limits_and_boundary"): (
        "As temperature approaches absolute zero ($T \\to 0$), the ratio $E_n / (kT) \\to \\infty$ for all excited states ($E_n > E_0$), "
        "causing occupation probabilities to satisfy $e^{-E_n / (kT)} \\to 0$ and freezing the system into its ground state."
    ),
    ("voltage-from-motion-4ba8b13e", "symmetry_origin"): (
        "By Stokes' theorem, $\\oint \\mathbf{E} \\cdot d\\mathbf{l} = \\int (\\nabla \\times \\mathbf{E}) \\cdot d\\mathbf{a}$. "
        "Equating this to $-\\frac{d\\Phi_B}{dt}$ yields Faraday's law of induction."
    ),
    ("coulomb-potential-energy-656e5c99", "limits_and_boundary"): (
        "As distance increases to infinity ($r \\to \\infty$), the potential energy vanishes ($V_C(r) \\to 0$). "
        "As $r \\to 0$, $V_C(r)$ diverges, representing the unshielded point-charge singularity."
    ),
    ("symmetry-source-221e1d3a", "interpretation"): (
        "In the canonical momentum relation $\\mathbf{p}_{EM} = m\\mathbf{v} + q\\mathbf{A}$, the term $q\\mathbf{A}$ represents the electromagnetic potential momentum."
    ),
    ("spatial-derivative-of-scalar-field-4877778a", "interpretation"): (
        "This term represents a spatial derivative component of $\\nabla \\Phi$, contributing to the kinetic gradient energy density $(\\nabla \\Phi)^2$."
    ),
    ("orthogonal-triplet-d90b32e7", "symmetry_origin"): (
        "This relationship follows from Faraday's law of induction, $\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$, "
        "which demands orthogonality between wave propagation vectors, electric fields, and magnetic fields."
    ),
    ("differential-work-and-potential-energy-change-5d05c37e", "symmetry_origin"): (
        "For conservative forces, $\\nabla \\times \\mathbf{F} = \\mathbf{0}$, guaranteeing that work done along any closed path is zero and that $\\mathbf{F} = -\\nabla U$."
    ),
    ("generalized-flux-rule-for-moving-circuits-349d7995", "interpretation"): (
        "The motional electromotive force is given by $\\oint (\\mathbf{v} \\times \\mathbf{B}) \\cdot d\\mathbf{l}$, accounting for Lorentz forces on charges in moving loops."
    ),
    ("field-link-d2faeecc", "symmetry_origin"): (
        "Faraday's law $\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$ couples spatial curl to temporal rates of change of magnetic flux."
    ),
    ("gausss-law-for-electric-fields-differential-form-5eae672d", "interpretation"): (
        "The differential relation $\\nabla \\cdot \\mathbf{E} = \\rho / \\varepsilon_0$ shows that regions of positive divergence act as sources of field lines."
    ),
    ("e-field-continuity-de3735c8", "conceptual_definition"): (
        "The boundary condition $\\mathbf{n} \\times (\\mathbf{E}_1 - \\mathbf{E}_2) = \\mathbf{0}$ states that the tangential component of electric fields is continuous across interfaces."
    ),
    ("e-field-continuity-de3735c8", "interpretation"): (
        "The cross product $\\mathbf{n} \\times (\\mathbf{E}_1 - \\mathbf{E}_2) = \\mathbf{0}$ guarantees continuity of tangential fields in the absence of time-varying magnetic flux."
    ),
    ("the-monopole-46072aa5", "conceptual_definition"): (
        "The generalized relation $\\nabla \\cdot \\mathbf{B} = \\mu_0 \\rho_m$ incorporates magnetic monopole charge densities into Maxwell's equations."
    ),
    ("derived-values-967adf08", "symmetry_origin"): (
        "Because $\\mathbf{E} = -\\nabla V$, the line integral along any path from $a$ to $b$ yields $\\int_a^b -\\nabla V \\cdot d\\mathbf{l} = -(V(b) - V(a)) = V(a) - V(b)$."
    ),
    ("electric-field-from-electromagnetic-potentials-e7033e68", "interpretation"): (
        "The term $-\\nabla \\Phi$ represents the irrotational scalar potential contribution, while $-\\frac{\\partial \\mathbf{A}}{\\partial t}$ represents inductive electric fields."
    ),
    ("electric-field-from-electromagnetic-potentials-e7033e68", "symmetry_origin"): (
        "Under gauge transformations $\\mathbf{A} \\to \\mathbf{A} + \\nabla \\Lambda$ and $\\Phi \\to \\Phi - \\frac{\\partial \\Lambda}{\\partial t}$, "
        "the physical field $\\mathbf{E} = -\\nabla \\Phi - \\frac{\\partial \\mathbf{A}}{\\partial t}$ remains invariant."
    ),
    ("field-pulse-81d83e3f", "interpretation"): (
        "The radiation field $\\mathbf{E}_{rad} \\propto \\frac{q}{r} [\\hat{\\mathbf{n}} \\times (\\hat{\\mathbf{n}} \\times \\dot{\\mathbf{v}})]$ "
        "is orthogonal to the line of sight $\\hat{\\mathbf{n}}$ and proportional to acceleration."
    ),
    ("divergence-of-curl-zero", "interpretation"): (
        "The vector identity $\\nabla \\cdot (\\nabla \\times \\mathbf{A}) = 0$ holds identically for all smooth vector fields."
    ),
    ("tangent-function-of-an-angle-46da7a9a", "limits_and_boundary"): (
        "In the small angle limit, as $\\theta \\to 0$, $\\tan \\theta \\to 0$ with asymptotic behavior $\\tan \\theta \\approx \\theta$."
    ),
    ("exponential-growth-d48b2ba1", "limits_and_boundary"): (
        "As $t \\to \\infty$, $a(t) \\to \\infty$ for expanding cosmologies with $H > 0$. At $t = 0$, $a(0) = a_0 \\exp(H \\cdot 0) = a_0$."
    ),
    ("one-dimensional-laplace-equation-for-magnetic-vector-potential-2d388f54", "conceptual_definition"): (
        "In magnetostatics, $\\mathbf{B} = \\nabla \\times \\mathbf{A}$. In one dimension with zero current density, this reduces to $\\frac{d^2 A}{dx^2} = 0$."
    ),
    ("field-equation-d9a63102", "interpretation"): (
        "The characteristic impedance of free space is $Z_0 = \\sqrt{\\frac{\\mu_0}{\\varepsilon_0}} \\approx 376.7 \\, \\Omega$."
    ),
    ("effective-metric-hamiltonian", "limits_and_boundary"): (
        "As energy approaches the potential boundary ($E - V(q) \\to 0$), the Jacobi metric components satisfy $g'_{ij} \\to 0$."
    ),
    ("axial-parity-identity-f42e4892", "interpretation"): (
        "Under spatial parity $(x, y, z) \\to (-x, -y, -z)$, polar vectors change sign while pseudovectors (axial vectors) remain invariant."
    ),
    ("low-reynolds-number-limit", "symmetry_origin"): (
        "In the creeping flow limit where $\\mathrm{Re} \\to 0$, inertial terms vanish and Stokes' drag law becomes exact."
    ),
    ("maxwells-equations-vacuum-formalism-c392d9cd", "interpretation"): (
        "In free space, Maxwell's equations take symmetric form: $\\nabla \\cdot \\mathbf{E} = 0$, $\\nabla \\cdot \\mathbf{B} = 0$, "
        "$\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$, and $\\nabla \\times \\mathbf{B} = \\frac{1}{c^2}\\frac{\\partial \\mathbf{E}}{\\partial t}$."
    ),
    ("proof-method-3d88e2ef", "symmetry_origin"): (
        "Gauss's law for magnetism, $\\nabla \\cdot \\mathbf{B} = 0$, implies that the normal component of magnetic flux density is continuous across any interface."
    ),
    ("integral-geometric-identity-e2f9202c", "interpretation"): (
        "Stokes' theorem relates boundary line circulation to interior curl flux: "
        "$\\oint_{\\partial \\Sigma} \\mathbf{A} \\cdot d\\mathbf{l} = \\iint_\\Sigma (\\nabla \\times \\mathbf{A}) \\cdot d\\mathbf{a}$."
    ),
    ("gradient-of-a-scalar-field-0c45fd93", "interpretation"): (
        "The gradient $\\nabla \\phi$ yields the directional derivative vector; in conservative systems, force density is $-\\nabla \\phi$."
    ),
    ("gradient-of-scalar-potential-b293d129", "interpretation"): (
        "The gradient $\\nabla V(\\mathbf{r})$ characterizes local rate of change, with electric field defined as $\\mathbf{E} = -\\nabla V(\\mathbf{r})$."
    ),
    ("gradient-of-scalar-potential-b293d129", "symmetry_origin"): (
        "For spherically symmetric potentials $V(r)$, the gradient simplifies to $\\nabla V(r) = \\frac{dV}{dr} \\hat{\\mathbf{r}}$."
    ),
    ("mhd-induction-relation-fluids-50d163b6", "interpretation"): (
        "The induction equation $\\frac{\\partial \\mathbf{B}}{\\partial t} = \\nabla \\times (\\mathbf{u} \\times \\mathbf{B}) + \\eta \\nabla^2 \\mathbf{B}$ "
        "balances advective transport against magnetic diffusion."
    ),
    ("geometric-start-ba4d589c", "limits_and_boundary"): (
        "As $a'(t) \\to 0$ and $a(t) \\to 1$, cosmological spacetime asymptotically transitions to static Minkowski geometry."
    ),
    ("work-rule-4da28176", "symmetry_origin"): (
        "Because electrostatic fields satisfy $\\nabla \\times \\mathbf{E} = \\mathbf{0}$, line integrals around closed loops identically satisfy $\\oint \\mathbf{E} \\cdot d\\mathbf{l} = 0$."
    ),
    ("no-motion-61d30ad3", "interpretation"): (
        "Coulomb's Law evaluates electrostatic force via $\\mathbf{F}_{static} = \\frac{1}{4\\pi\\varepsilon_0} \\frac{q_1 q_2}{r^2} \\hat{\\mathbf{r}}$, "
        "where $\\varepsilon_0 \\approx 8.854 \\times 10^{-12} \\text{ C}^2/(\\mathrm{N} \\cdot \\mathrm{m}^2)$."
    ),
    ("e-vs-b-48093a69", "interpretation"): (
        "The electric flux $\\oint \\mathbf{E} \\cdot d\\mathbf{a} = \\frac{Q_{enc}}{\\varepsilon_0}$ evaluates enclosed charge, "
        "with vacuum permittivity $\\varepsilon_0 \\approx 8.854 \\times 10^{-12} \\text{ C}^2/(\\mathrm{N} \\cdot \\mathrm{m}^2)$."
    ),
    ("differential-electric-flux-element", "interpretation"): (
        "The differential flux $d\\Phi_E = \\mathbf{E} \\cdot d\\mathbf{a} = \\frac{q}{4\\pi\\varepsilon_0} d\\Omega$ scales with solid angle, "
        "with $\\varepsilon_0 \\approx 8.854 \\times 10^{-12} \\text{ C}^2/(\\mathrm{N} \\cdot \\mathrm{m}^2)$."
    ),
    ("vacuum-resistance-26ee25d2", "interpretation"): (
        "The characteristic vacuum impedance is $Z_0 = \\sqrt{\\frac{\\mu_0}{\\varepsilon_0}} = \\mu_0 c \\approx 376.7 \\, \\Omega$."
    ),
    ("radial-density-power-law-profile-fe5dbc40", "limits_and_boundary"): (
        "As $r \\to 0$, the power-law density profile diverges for positive indices, requiring a central core cutoff in realistic astrophysical models."
    ),
    ("power-law-density-profile-63fd7682", "limits_and_boundary"): (
        "As $r \\to 0$, central density diverges if $n > 0$, necessitating a core radius boundary condition."
    ),
    ("schwarzschild-radius-ratio", "conceptual_definition"): (
        "The ratio $r_s / r$ parameterizes gravitational field strength, approaching zero in weak-field regimes."
    ),
    ("schwarzschild-radius-ratio", "interpretation"): (
        "The condition $r_s / r \\to 0$ characterizes Newtonian gravity far outside compact objects."
    ),
    ("schwarzschild-radius-ratio", "limits_and_boundary"): (
        "As $r_s / r \\to 0$, spacetime curvature vanishes; as $r_s / r \\to 1$, an event horizon forms."
    ),
    ("schwarzschild-radius-ratio", "symmetry_origin"): (
        "The limit $r_s / r \\to 0$ preserves rotational symmetry while recovering flat Minkowski spacetime."
    ),
    ("angular-momentum-approaches-zero", "conceptual_definition"): (
        "The limit $l_p \\to 0$ describes particles with zero impact parameter or purely radial trajectories."
    ),
    ("angular-momentum-approaches-zero", "interpretation"): (
        "The condition $l_p \\to 0$ signifies radial motion devoid of orbital angular momentum."
    ),
    ("scale-factor-approaches-unity", "interpretation"): (
        "The condition $a(t) \\to 1$ normalizes cosmological scale factors to the present-day epoch."
    ),
    ("cosmological-rule-3facc689", "limits_and_boundary"): (
        "As $t \\to 0$, scale factor $a(t) \\to 0$, while as $t \\to \\infty$, expansion is governed by dark energy."
    ),
    ("schwarzschild-singularity-interval-b0150134", "interpretation"): (
        "As $r \\to 0$, the metric coefficient $-\\frac{r_s}{r} \\to -\\infty$, reflecting physical spacetime curvature divergence."
    ),
    ("schwarzschild-singularity-interval-b0150134", "limits_and_boundary"): (
        "As $r \\to 0$, tidal forces diverge; as $r \\to \\infty$, the Schwarzschild metric approaches flat Minkowski spacetime."
    ),
    ("shakura-sunyaev-alpha-viscosity-2342c109", "interpretation"): (
        "In accretion disks, kinematic viscosity is parameterized as $\\nu = \\alpha c_s H$, with disk scale height $H \\approx c_s / \\Omega$."
    ),
    ("relative-change-in-angular-momentum", "interpretation"): (
        "The condition $\\Delta l / l \\to 0$ signifies that fractional change in angular momentum is negligible."
    ),
    ("field-orientation-52a3ae4d", "limits_and_boundary"): (
        "As $k \\to 0$ or $\\omega \\to 0$, electromagnetic wave oscillations degenerate into static electric or magnetic fields."
    ),
    ("redshift", "conceptual_definition"): (
        "The formula represents a cosmological redshift measurement $z \\approx 1.2$, corresponding to an earlier cosmic epoch."
    ),
    ("redshift", "interpretation"): (
        "The value $z \\approx 1.2$ indicates that observed wavelengths are shifted by a factor of $1 + z = 2.2$ relative to emission."
    ),
    ("redshift-approximation", "conceptual_definition"): (
        "The formula describes a moderate cosmological redshift $z \\approx 0.6$ within FLRW spacetime."
    ),
    ("cosmic-timing-720ab189", "conceptual_definition"): (
        "The epoch $\\Omega_\\Lambda(z) \\approx \\Omega_m(z)$ occurs at $z \\approx 0.3$, marking the transition from matter to dark energy dominance."
    ),
    ("poissons-equation-for-temperature-76971fc1", "interpretation"): (
        "The steady-state heat equation equates the temperature Laplacian $\\nabla^2 T$ to internal heat source densities."
    ),
    ("gauge-transformation-photon-field", "interpretation"): (
        "Under gauge transformations, $A_\\mu \\to A_\\mu + \\partial_\\mu \\Lambda$ preserves electromagnetic field strengths."
    ),
    ("jacobi-metric", "limits_and_boundary"): (
        "When kinetic energy vanishes ($E - V \\to 0$), the Jacobi metric degenerates at classical turning points."
    ),
    ("higgs-boson-mass-squared-f8646f48", "symmetry_origin"): (
        "The equation originates from the spontaneous breaking of the electroweak gauge symmetry, specifically the $SU(2)_L \\times U(1)_Y$ symmetry, down to the electromagnetic $U(1)_{EM}$ symmetry. The non-zero vacuum expectation value of the Higgs field is responsible for this symmetry breaking, which in turn gives mass to fundamental particles, including the Higgs boson itself."
    ),
    ("complex-flip-e5704062", "interpretation"): (
        "The given equations describe the transformation properties of quantum mechanical operators under a unitary operator $\\mathcal{T}$, which in this context represents a spatial inversion or parity transformation. The position operator $\\mathbf{r}$ satisfies $\\mathcal{T} \\mathbf{r} \\mathcal{T}^{-1} = \\mathbf{r}$, remaining invariant under spatial inversion. The momentum operator $\\mathbf{p}$ (with units of $\\mathrm{kg} \\cdot \\mathrm{m/s}$) satisfies $\\mathcal{T} \\mathbf{p} \\mathcal{T}^{-1} = -\\mathbf{p}$, reversing its sign under parity reflection."
    ),
    ("w-boson-mass-from-electroweak-unification-c49b69ef", "limits_and_boundary"): (
        "This formula is valid within the framework of the Standard Model of particle physics. Its accuracy relies on the assumption of a single Higgs doublet and the specific gauge group $SU(2)_L \\times U(1)_Y$. Deviations might indicate new physics beyond the Standard Model, such as extended Higgs sectors or different gauge symmetries, particularly at energy scales significantly higher than the electroweak scale."
    ),
    ("w-boson-mass-from-electroweak-unification-c49b69ef", "symmetry_origin"): (
        "The formula originates from the spontaneous breaking of the $SU(2)_L \\times U(1)_Y$ electroweak gauge symmetry down to the $U(1)_{EM}$ electromagnetic symmetry. The Higgs mechanism provides the means for the W-bosons to acquire mass while preserving the underlying gauge invariance of the Lagrangian."
    ),
    ("acceleration-effect-c89fffcb", "interpretation"): (
        "In this equation, $A^\\mu$ represents the electromagnetic four-potential, a relativistic construct that combines the scalar electric potential $\\Phi$ and the vector magnetic potential $\\mathbf{A}$ into a single four-vector: $A^\\mu = (\\Phi/c, \\mathbf{A})$. The d'Alembertian operator $\\Box = \\nabla^2 - \\frac{1}{c^2} \\frac{\\partial^2}{\\partial t^2}$ acts on the four-potential, where $\\nabla^2$ is the Laplacian operator and $c$ is the speed of light in vacuum. On the right-hand side, $j^\\mu = (c\\rho, \\mathbf{J})$ is the electromagnetic four-current, combining charge density $\\rho$ and current density $\\mathbf{J}$, with $\\mu_0$ being the vacuum permeability."
    ),
    ("flat-spacetime-limit-minkowski", "interpretation"): (
        "The equation $g_{\\mu \\nu} \\to \\eta_{\\mu \\nu}$ represents a limiting case where the metric tensor $g_{\\mu \\nu}$ of a general spacetime manifold approaches the constant Minkowski metric $\\eta_{\\mu \\nu}$ of special relativity. As gravitational fields weaken or spacetime curvature vanishes far from massive bodies, the metric tensor approaches flat spacetime geometry."
    ),
    ("euler-lagrange-equation", "interpretation"): (
        "The Euler-Lagrange equation $\\frac{\\mathrm{d}}{\\mathrm{d}t}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) - \\frac{\\partial L}{\\partial q_i} = 0$ governs the dynamics of a physical system with Lagrangian $L = T - V$, generalized coordinates $q_i$, generalized velocities $\\dot{q}_i$, and generalized canonical momenta $p_i = \\frac{\\partial L}{\\partial \\dot{q}_i}$ (measured in $\\mathrm{kg} \\cdot \\mathrm{m/s}$). The equation equates the time rate of change of generalized momentum to the generalized force."
    ),
    ("yukawa-potential-range-approximation-f736c686", "interpretation"): (
        "This formula provides a heuristic understanding of why forces mediated by massive particles are short-ranged. As a consequence of the energy-time uncertainty principle, a virtual particle of mass $\\mu$ can exist for a duration $\\Delta t \\approx \\hbar / (\\mu c^2)$, traveling a characteristic distance $R \\approx c \\Delta t \\approx \\hbar / (\\mu c)$. Thus, the interaction range is inversely proportional to the mass of the mediating gauge boson."
    ),
    ("magnetic-push-8cad2818", "interpretation"): (
        "In this equation, $\\mathbf{f}$ is the magnetic force density, measured in newtons per cubic meter ($\\mathrm{N/m^3}$). $\\mathbf{J}$ is the current density vector (in $\\mathrm{A/m^2}$) and $\\mathbf{B}$ is the magnetic field vector (in teslas, $\\mathrm{T}$). The vector cross product $\\mathbf{J} \\times \\mathbf{B}$ indicates that the resulting force density is perpendicular to both $\\mathbf{J}$ and $\\mathbf{B}$, with magnitude $f = J B \\sin\\theta$."
    ),
    ("gausss-law-dielectric-medium", "interpretation"): (
        "The equation $\\nabla \\cdot \\mathbf{E} = \\rho / \\epsilon_0$ is the differential form of Gauss's law. The divergence $\\nabla \\cdot \\mathbf{E}$ measures the net outward flux of the electric field vector per unit volume. The volume charge density $\\rho$ is the source of the electric field, scaled by the vacuum permittivity $\\epsilon_0 \\approx 8.854 \\times 10^{-12} \\text{ C}^2/(\\text{N}\\cdot\\text{m}^2)$."
    ),
    ("boundary-condition-normal-magnetic-field", "interpretation"): (
        "The equation $(\\mathbf{B}_1 - \\mathbf{B}_2) \\cdot \\hat{\\mathbf{n}} = 0$ expresses the continuity of the normal component of the magnetic field across an interface between two media. Here $\\hat{\\mathbf{n}}$ is a unit normal vector to the interface. The condition implies $\\mathbf{B}_1 \\cdot \\hat{\\mathbf{n}} = \\mathbf{B}_2 \\cdot \\hat{\\mathbf{n}}$, reflecting the absence of magnetic monopoles at the boundary."
    ),
    ("work-by-torque", "interpretation"): (
        "In this equation, $dW$ represents an infinitesimal amount of mechanical work done, measured in joules ($\\text{J}$). The torque vector $\\boldsymbol{\\tau}$ (in $\\text{N}\\cdot\\text{m}$) and infinitesimal angular displacement vector $d\\boldsymbol{\\theta}$ enter through the scalar product $dW = \\boldsymbol{\\tau} \\cdot d\\boldsymbol{\\theta}$, signifying that only torque components along the rotational displacement contribute to work."
    ),
    ("grid-density-36cb87aa", "interpretation"): (
        "In this canonical commutation relation, $\\hat{x}$ and $\\hat{p}$ represent the quantum position and linear momentum operators, satisfying $[\\hat{x}, \\hat{p}] = i\\hbar$. Here $\\hbar \\approx 1.054 \\times 10^{-34} \\text{ J}\\cdot\\text{s}$ is the reduced Planck constant. This fundamental relation directly implies the Heisenberg uncertainty relation $\\Delta x \\Delta p \\geq \\frac{\\hbar}{2}$."
    ),
    ("minimum-volume-1afd8ce0", "interpretation"): (
        "This relation establishes a minimal spatial volume scale $V_{\\mathrm{min}} \\propto l_P^3$ proportional to the cube of the Planck length $l_P = \\sqrt{\\frac{\\hbar G}{c^3}} \\approx 1.616 \\times 10^{-35} \\text{ m}$. In quantum gravitational theories, this sets an operational lower bound on spatial localization."
    ),
    ("propagation-rule-0c8a0748", "interpretation"): (
        "The wave equation $\\Box A^\\mu = \\mu_0 J^\\mu$ expresses Maxwell's equations in four-vector notation under the Lorenz gauge condition. The d'Alembert operator $\\Box = \\frac{1}{c^2} \\frac{\\partial^2}{\\partial t^2} - \\nabla^2$ acts on the electromagnetic four-potential $A^\\mu = (\\phi/c, \\mathbf{A})$, driven directly by the four-current density $J^\\mu = (c\\rho, \\mathbf{J})$ and vacuum permeability $\\mu_0$."
    ),
    ("parallel-axis-theorem", "limits_and_boundary"): (
        "As the displacement distance between axes vanishes ($d \\to 0$), the transport term $M(d^2 \\mathbf{I} - \\mathbf{d} \\otimes \\mathbf{d})$ approaches zero, and the moment of inertia tensor reduces to the center-of-mass tensor $I \\to I_{\\mathrm{cm}}$."
    ),
    ("redshift-approaches-zero", "conceptual_definition"): (
        "The limit $z \\to 0$ describes the zero-redshift boundary where observed radiation wavelengths match emission wavelengths, characterizing nearby comoving observers in the local cosmic rest frame."
    ),
    ("field-momentum-commutator-component-236b46fb", "interpretation"): (
        "The equal-time canonical commutation relation $[\\phi(\\mathbf{x}, t), \\pi(\\mathbf{y}, t)] = i\\hbar\\delta^{(3)}(\\mathbf{x} - \\mathbf{y})$ specifies the quantum kinematics between a scalar field $\\phi$ and its canonical conjugate momentum density $\\pi = \\partial \\mathcal{L} / \\partial \\dot{\\phi}$, whose dimensions correspond to energy multiplied by time per unit volume ($\\text{J}\\cdot\\text{s}/\\text{m}^3$)."
    ),
    ("time-varying-gradient-of-scalar-potential-990b0280", "interpretation"): (
        "The term $-\\frac{\\partial}{\\partial t}(\\nabla \\Lambda)$ represents the mixed spacetime derivative of a scalar gauge parameter $\\Lambda$. Under electromagnetic gauge transformations $\\mathbf{A} \\to \\mathbf{A} + \\nabla \\Lambda$ and $\\Phi \\to \\Phi - \\frac{\\partial \\Lambda}{\\partial t}$, this contribution cancels the spatial gradient of the scalar potential's time derivative, ensuring that physical electric fields $\\mathbf{E} = -\\nabla \\Phi - \\frac{\\partial \\mathbf{A}}{\\partial t}$ remain gauge invariant."
    ),
    ("gausss-law-b8aa48e5", "interpretation"): (
        "The differential form $\\nabla \\cdot \\mathbf{E} = \\frac{\\rho}{\\varepsilon_0}$ equates the divergence of the electric field to the local volume charge density $\\rho$. The vacuum permittivity $\\varepsilon_0 \\approx 8.854 \\times 10^{-12} \\text{ F/m}$ scales the field line flux emanating from positive sources or terminating on negative sinks."
    ),
    ("euler-lagrange-canonical-momentum-derivative-e346526c", "interpretation"): (
        "The expression $\\frac{d}{dx} \\left( \\frac{\\partial L}{\\partial f'} \\right)$ represents the total derivative of the canonical momentum density conjugate to the field $f$. In variational field theory, this term balances the generalized force $\\frac{\\partial L}{\\partial f}$ to establish the stationary-action field equations."
    ),
    ("minkowski-spacetime-interval", "limits_and_boundary"): (
        "In the purely spatial limit where temporal separations vanish ($c\\,dt \\to 0$), the spacetime interval becomes spacelike: $ds^2 \\to -(dx^2 + dy^2 + dz^2)$. Conversely, in the purely temporal limit where spatial coordinates coincide ($dx^i \\to 0$), the interval reduces to $ds^2 \\to c^2 dt^2$, corresponding to the proper time elapsed along the worldline."
    ),
    ("hubble-parameter-evolution", "limits_and_boundary"): (
        "In the high-redshift limit ($z \\to \\infty$), matter and radiation densities dominate the expansion rate with $H^2 \\propto (1+z)^3$. In the present cosmological epoch ($z \\to 0$), the expansion rate approaches the Hubble constant $H(0) = H_0$, where dark energy and matter satisfy $\\Omega_m + \\Omega_\\Lambda = 1$ in a spatially flat universe."
    ),
    ("magnetic-field-vanishes", "interpretation"): (
        "The asymptotic condition $\\mathbf{B} \\to \\mathbf{0}$ describes the vanishing of the magnetic induction vector, representing either spatial infinity far from current distributions or the non-magnetic limit where electromagnetic forces reduce purely to electrostatic interactions."
    ),
    ("frame-swap-62c711a0", "interpretation"): (
        "The Lorentz magnetic force $\\mathbf{F}_{\\mathrm{mag}} = q(\\mathbf{v} \\times \\mathbf{B})$ acts on a particle with electric charge $q$ moving at velocity $\\mathbf{v}$ through magnetic field $\\mathbf{B}$. Because the cross product enforces $\\mathbf{F}_{\\mathrm{mag}} \\perp \\mathbf{v}$, the instantaneous power vanishes ($P = \\mathbf{F}_{\\mathrm{mag}} \\cdot \\mathbf{v} = 0$), demonstrating that magnetic forces do no work on free charged particles."
    ),
    ("speed-barrier-2f04e8d8", "interpretation"): (
        "The linear radiated power $P_{\\mathrm{linear}} = \\frac{\\mu_0 q^2 a^2 \\gamma^6}{6\\pi c}$ scales with the sixth power of the relativistic Lorentz factor $\\gamma = 1/\\sqrt{1 - v^2/c^2}$. As particle velocity approaches light speed ($v \\to c$), the factor $\\gamma \\to \\infty$ produces severe radiative energy loss, establishing a dynamical barrier to linear acceleration."
    ),
    ("stability-guard-29cfc76f", "interpretation"): (
        "The running gauge couplings $\\alpha_i^{-1}(\\mu)$ for $U(1)$, $SU(2)$, and $SU(3)$ gauge interactions evolve with energy scale $\\mu$ according to the renormalization group equations. In the Minimal Supersymmetric Standard Model (MSSM), the gauge couplings unify asymptotically near $\\mu \\approx 10^{16} \\text{ GeV}$, indicating grand unified gauge symmetry."
    ),
    ("right-handed-weyl-spinor-field-7df86efa", "symmetry_origin"): (
        "The transformation properties of the right-handed Weyl spinor $\\psi_R$ originate from the $(0, 1/2)$ representation of the Lorentz group $\\mathrm{SO}(1, 3)$. Under the Standard Model gauge group $SU(3)_C \\times SU(2)_L \\times U(1)_Y$, right-handed fields transform as singlets under weak isospin $SU(2)_L$."
    ),
    ("gausss-law-for-electric-fields-differential-form-5eae672d", "conceptual_definition"): (
        "Gauss's law in differential form states that the divergence of the electric field $\\nabla \\cdot \\mathbf{E} = \\rho / \\varepsilon_0$ is directly proportional to the enclosed charge density $\\rho$, establishing electric charges as the local physical sources and sinks of electrostatic fields."
    ),
    ("wave-equation-electric-field", "interpretation"): (
        "The electromagnetic wave equation $\\nabla^2 \\mathbf{E} = \\mu_0 \\varepsilon_0 \\frac{\\partial^2 \\mathbf{E}}{\\partial t^2}$ relates the spatial curvature of the electric field to its second time derivative. The product of vacuum permeability $\\mu_0$ and permittivity $\\varepsilon_0$ determines the propagation speed $c = 1 / \\sqrt{\\mu_0 \\varepsilon_0}$ of electromagnetic waves in free space."
    ),
    ("directional-derivative-scalar", "interpretation"): (
        "The directional derivative $D_{\\hat{\\mathbf{u}}} \\Phi = \\nabla \\Phi \\cdot \\hat{\\mathbf{u}}$ calculates the rate of change of a scalar field $\\Phi$ along the direction specified by the unit vector $\\hat{\\mathbf{u}}$. The inner product projects the gradient vector $\\nabla \\Phi$ onto $\\hat{\\mathbf{u}}$, yielding the scalar rate of spatial variation."
    ),
    ("sturm-liouville-eigenvalue-methods-d8f21012", "interpretation"): (
        "In the Sturm-Liouville differential operator $-\\frac{d}{dx}\\left[p(x)\\frac{dy}{dx}\\right] + q(x)y = \\lambda w(x)y$, the coefficient $p(x)$ modulates spatial stiffness or conductivity (with units such as $\\text{W}/(\\text{m}\\cdot\\text{K})$), $q(x)$ represents a potential energy density, and $w(x)$ is a positive weight function defining the Hilbert space inner product for orthogonal eigenfunctions."
    ),
    ("4d-curl-211eef85", "interpretation"): (
        "The covariant Maxwell equation $\\partial_\\mu F^{\\mu \\nu} = \\mu_0 J^\\nu$ expresses the divergence of the antisymmetric electromagnetic field tensor $F^{\\mu \\nu}$ in terms of the four-current density $J^\\nu = (c\\rho, \\mathbf{J})$ and vacuum permeability $\\mu_0$, unifying Gauss's law and Ampere's circuital law in four-dimensional Minkowski spacetime."
    ),
    ("field-definition-identity-1-d3934851-f11a1678", "interpretation"): (
        "In the Lorentz force relation $\\mathbf{F}_B = q(\\mathbf{v} \\times \\mathbf{B})$, the magnetic deflection force vanishes when the charged particle velocity $\\mathbf{v}$ is parallel or antiparallel to the magnetic field vector $\\mathbf{B}$."
    ),
    ("torque", "interpretation"): (
        "In the relation $\\mathbf{N} = \\mathbf{r} \\times \\mathbf{F}$, $\\mathbf{N}$ denotes the mechanical torque vector produced by force $\\mathbf{F}$ applied at position vector $\\mathbf{r}$. The cross product specifies that the torque magnitude is $N = r F \\sin\\theta$, acting along an axis perpendicular to both displacement and applied force according to the right-hand rule."
    ),
    ("gradient-of-scalar-potential-b293d129", "conceptual_definition"): (
        "The spatial gradient operator $\\nabla$ maps a scalar potential $V(\\mathbf{r})$ to a vector field $\\nabla V(\\mathbf{r})$ oriented along the direction of steepest ascent, whose negative defines the corresponding conservative force field $\\mathbf{F} = -\\nabla V$."
    ),
    ("generalized-momentum-component-eca91c83", "conceptual_definition"): (
        "In Hamiltonian and Lagrangian dynamics, the generalized canonical momentum $p_i = \\frac{\\partial L}{\\partial \\dot{q}_i}$ conjugate to generalized coordinate $q_i$ describes the momentum coordinate in phase space, carrying units dependent on the underlying coordinate representation (such as $\\mathrm{kg}\\cdot\\mathrm{m/s}$ for linear translations or $\\mathrm{kg}\\cdot\\mathrm{m}^2/\\mathrm{s}$ for rotations)."
    ),
}

print(f"Loaded {len(COMPLETE_REPAIRS)} complete repairs.")

