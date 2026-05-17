import json

def refactor_cm():
    file_path = "app/config/content/classical-mechanics.json"
    with open(file_path, "r") as f:
        data = json.load(f)

    # Virtual Displacement
    vd_content = r"""<p>The infinitesimal, hypothetical change in a system's coordinates that occurs without the passage of time and satisfies the instantaneous <strong>Holonomic Constraints</strong>—termed virtual displacement—establishes the foundational variational tool for the derivation of d'Alembert's Principle and the stationary action principle. In university-level mechanics, a virtual displacement (\( \delta \mathbf{r} \)) is not a physical displacement that follows the actual laws of motion, but a mathematical 'Probe' into the space of possible configurations allowed by the manifold's geometry. By analyzing how the system's energy and work respond to these perturbations, physicists can identify the physical trajectory as the one for which the <strong>Virtual Work</strong> of the constraint forces identically vanishes, providing a globally consistent map for the <strong>Total Dynamics</strong> that is decoupled from the choice of an external Euclidean frame.</p>

                    <h3>1. d'Alembert's Principle and the Equilibrium of Motion</h3>
                    <p>The concept of virtual displacement is most rigorously applied in <strong>d'Alembert's Principle</strong>, which generalizes the principle of virtual work to dynamical systems. This principle asserts that for any virtual displacement consistent with the constraints, the sum of the applied forces and the inertial forces must perform zero work: \( \sum (\mathbf{F}_i - \dot{\mathbf{p}}_i) \cdot \delta \mathbf{r}_i = 0 \). In university-level theory, this statement is the bridge between the Newtonian and Lagrangian formalisms. It reveals that the physical motion of a system is an <strong>Equilibrium State</strong> in a higher-dimensional functional space, anchoring <strong>Scientific Realism</strong> in the realization that the laws of physics are the result of nature optimizing its dynamical cost across the 4D <strong>Block Universe</strong>.</p>

                    <h3>2. Constraints and the Principle of Virtual Work</h3>
                    <p>Virtual displacements are defined such that they are 'Perpendicular' to the constraint forces in the <strong>Configuration Space Manifold</strong>. This geometric restriction ensures that the work done by these internal forces is zero during a virtual variation, a property known as the <strong>Principle of Virtual Work</strong>. By eliminating the necessity of calculating complex constraint forces (such as tension or normal forces), virtual displacement allows for a direct derivation of the <strong>Euler-Lagrange Equations</strong>. This reduction of complexity is the cornerstone of <strong>Analytical Mechanics</strong>, providing the necessary scaffolding for formulating theories of <strong>Total Dynamics</strong> in systems with many degrees of freedom, from rigid bodies to relativistic fields.</p>

                    <h3>3. The Hero Formula and the Variational Identity</h3>
                    <p>The mathematical essence of the virtual displacement program is captured by the identity that defines the first variation of the coordinate vector. This relation serves as the 'Master Probe' from which all variational principles are derived, representing the state of <strong>Variational Equilibrium</strong>:</p>
                    \[ \delta \mathbf{r}_i = \sum_{j=1}^{f} \frac{\partial \mathbf{r}_i}{\partial q_j} \delta q_j \]
                    <p>This 'Hero Formula' underscores that a virtual displacement (\( \delta \mathbf{r}_i \)) is a linear mapping from the variations of the <strong>Generalized Coordinates</strong> (\( \delta q_j \)). It provides the visual anchor for understanding how the abstract geometric perturbations of the manifold dictate the physical deviations in Euclidean space, revealing the deep coupling between the system's internal structure and the flow of time within the Newtonian regime.</p>

                    <h3>4. Virtual vs. Actual Displacement</h3>
                    <p>A critical distinction in university-level dynamics is the difference between a virtual displacement and an actual physical displacement (\( d\mathbf{r} \)). While the actual displacement occurs over a finite time interval (\( dt \)) and must obey the <strong>Total Dynamics</strong> of the system, a virtual displacement is a 'Freeze-Frame' variation that ignores the passage of time. This independence from the temporal parameter allows physicists to probe the <strong>Symmetry</strong> of the constraints at a specific instant, ensuring that the resulting equations of motion are <strong>Manifestly Covariant</strong> and stable against small fluctuations of the vacuum.</p>

                    <h3>5. The Limiting Case: From Constrained to Free Particles</h3>
                    <p>The framework of virtual displacement serves as the parent logic for the **Limiting Case** of unconstrained Newtonian mechanics. As the restrictions on a particle are conceptually removed, the virtual displacement reduces identically to an arbitrary infinitesimal vector in Euclidean space. In this limit, d'Alembert's Principle contracts into <strong>Newton's Second Law</strong> (\( \mathbf{F} = m\mathbf{a} \)), and the complex variational logic of the manifold aligns with the intuitive vector sum of forces. This reduction demonstrates that virtual displacement is an <strong>Effective Ontology</strong>—a more general and robust language that captures the essential causal structure of physics across all scales, from the simple trajectories of classical objects to the complex interactions of modern field theories.</p>"""

    data["virtual-displacement"].update({
        "title": "Virtual Displacement",
        "content": vd_content,
        "snippet": "The infinitesimal, hypothetical change in a system's coordinates that occurs without the passage of time and satisfies instantaneous constraints—termed virtual displacement—establishes the foundational variational tool for modern mechanics. It acts as a mathematical probe into the space of possible configurations, providing the bridge between Newtonian forces and the stationarity of the Action Functional within the configuration space manifold.",
        "snippet_svg": "The infinitesimal, hypothetical change in a system's coordinates that occurs without the passage of time and satisfies instantaneous constraints—termed virtual displacement—establishes the foundational variational tool for modern mechanics. It acts as a mathematical probe into the space of possible configurations, providing the bridge between Newtonian forces and the stationarity of the Action Functional within the configuration space manifold.",
        "hero_math": r"\[ \delta \mathbf{r}_i = \sum_{j=1}^{f} \frac{\partial \mathbf{r}_i}{\partial q_j} \delta q_j \]",
        "standard": "platinum"
    })

    # Lagrange Multipliers
    lm_content = r"""<p>The extremization of a scalar functional subject to a set of auxiliary algebraic restrictions—formulated through the method of Lagrange multipliers—establishes the primary mathematical framework for the analysis of constrained dynamical systems within the configuration space manifold. This technique, developed by Joseph-Louis Lagrange, allows for the determination of the physical trajectories by embedding the <strong>Holonomic Constraints</strong> directly into the <strong>Action Functional</strong> (\( S \)). In university-level mechanics, Lagrange multipliers (\( \lambda \)) are not merely auxiliary variables but are the fundamental physical identifiers of the <strong>Constraint Forces</strong>, providing a globally consistent map for the <strong>Total Dynamics</strong> where the restrictions of the geometry are treated as active participants in the equations of motion.</p>

                    <h3>1. Constrained Extremization and the Augmented Lagrangian</h3>
                    <p>In the variational program, the physical path is identified as the stationary point of an <strong>Augmented Lagrangian</strong> (\( L' = L + \sum \lambda_k f_k \)), where \( f_k(q, t) = 0 \) represent the constraint equations. By requiring that the first variation of the action functional vanishes for both the <strong>Generalized Coordinates</strong> and the multipliers, the global requirement of stationarity is transformed into a system of coupled differential-algebraic equations. This method reveals that the system is not merely 'Forced' to follow a path but is in a state of <strong>Variational Equilibrium</strong>, where the multipliers represent the 'Cost' required to maintain the system on the sub-manifold, anchoring <strong>Scientific Realism</strong> in the realization that constraints have a tangible dynamical origin.</p>

                    <h3>2. Physical Interpretation: Forces of Constraint</h3>
                    <p>The deepest physical insight provided by the method is the realization that the Lagrange multipliers are proportional to the actual <strong>Forces of Constraint</strong> acting on the system. For a multiplier \( \lambda \) associated with a geometric constraint, the quantity \( \lambda \frac{\partial f}{\partial q_i} \) represents the generalized force (such as tension or normal force) required to keep the coordinate \( q_i \) in compliance with the restriction. This link proves that the abstract mathematical process of extremization is equivalent to the Newtonian balance of forces, providing the necessary scaffolding for formulating theories of <strong>Total Dynamics</strong> in systems where the internal connectivity is as critical as the external interactions.</p>

                    <h3>3. The Hero Formula and the Augmented Identity</h3>
                    <p>The mathematical anchor for constrained dynamics is the identity that defines the stationary condition for the augmented system. This relation serves as the definitive gatekeeper for the well-definedness of the equations of motion across the manifold:</p>
                    \[ \frac{d}{dt} \left( \frac{\partial L}{\partial \dot{q}_i} \right) - \frac{\partial L}{\partial q_i} = \sum_{k=1}^{m} \lambda_k \frac{\partial f_k}{\partial q_i} \]
                    <p>This 'Hero Formula' underscores that the deviation from the unconstrained Euler-Lagrange equations is exactly balanced by the weighted sum of the <strong>Lagrange Multipliers</strong>. It provides the visual anchor for understanding how the scalar energy landscape is 'Reshaped' by the presence of constraints, revealing the deep coupling between the system's topological restrictions and its physical trajectories through the 4D <strong>Block Universe</strong>.</p>

                    <h3>4. Statistical Mechanics and Information Entropy</h3>
                    <p>Beyond classical mechanics, Lagrange multipliers are the foundational tool for <strong>Statistical Mechanics</strong> and <strong>Information Theory</strong>. In the derivation of the <strong>Boltzmann Distribution</strong>, multipliers are used to maximize the <strong>Gibbs Entropy</strong> subject to the constraint of constant total energy and particle number. Here, the multiplier (\( \beta = 1/k_B T \)) identifies the temperature as the fundamental parameter that regulates the flow of energy between degrees of freedom. This application proves that the method is a universal and robust language for capturing the essential <strong>Symmetry</strong> and stability of physical systems at both the macroscopic and subatomic scales.</p>

                    <h3>5. The Limiting Case: From Constrained to Free Variation</h3>
                    <p>The method of Lagrange multipliers serves as the parent logic for the **Limiting Case** of unconstrained analytical mechanics. As the strength of the restrictions is conceptually reduced and the constraints are removed (\( f_k \to 0 \)), the multipliers identically vanish, and the augmented equations reduce to the standard <strong>Euler-Lagrange Equations</strong>. In this limit, the complex interactions between the geometry and the dynamics decouple, and the system follows the path dictated solely by the unconstrained scalar potential. This reduction proves that Lagrange multipliers are an <strong>Effective Ontology</strong>—a powerful mathematical lens that resolves the underlying unity between the rigid structure of the world and the flexible flow of motion.</p>"""

    data["lagrange-multipliers"].update({
        "title": "Lagrange Multipliers",
        "content": lm_content,
        "snippet": "The extremization of a scalar functional subject to auxiliary restrictions—formally through the method of Lagrange multipliers—establishes the primary framework for constrained dynamical systems. In university-level mechanics, these multipliers identify the physical forces of constraint, embedding the manifold's geometry directly into the stationarity condition of the Action Functional.",
        "snippet_svg": "The extremization of a scalar functional subject to auxiliary restrictions—formally through the method of Lagrange multipliers—establishes the primary framework for constrained dynamical systems. In university-level mechanics, these multipliers identify the physical forces of constraint, embedding the manifold's geometry directly into the stationarity condition of the Action Functional.",
        "hero_math": r"\[ \frac{d}{dt} \left( \frac{\partial L}{\partial \dot{q}_i} \right) - \frac{\partial L}{\partial q_i} = \sum_{k=1}^{m} \lambda_k \frac{\partial f_k}{\partial q_i} \]",
        "standard": "platinum"
    })

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

def refactor_tp():
    file_path = "app/config/content/theoretical-physics.json"
    with open(file_path, "r") as f:
        data = json.load(f)

    # Principal Function
    pf_content = r"""<p>The time-dependent solution to the Hamilton-Jacobi equation—formally termed Hamilton's principal function—establishes the foundational bridge between the variational history of a system and its wave-like propagation through configuration space. In university-level mechanics, the principal function (\( S(q, t) \)) is the action integral evaluated along the physical path as a function of its upper endpoint. Unlike the standard action functional which operates on fixed paths, the principal function serves as a generating function of a <strong>Canonical Transformation</strong> that reduces the dynamics to a state of equilibrium. By treating the action as a field rather than a number, this formalism reveals the underlying wave-particle duality inherent in classical trajectories, providing the primary mathematical scaffolding for the 4D <strong>Block Universe</strong>.</p>

                    <h3>1. The Hamilton-Jacobi Identity and Dynamics</h3>
                    <p>Hamilton's principal function satisfies the <strong>Hamilton-Jacobi Equation</strong>, a first-order non-linear partial differential equation: \( H(q, \frac{\partial S}{\partial q}, t) + \frac{\partial S}{\partial t} = 0 \). In university-level theory, this equation is the most complete statement of classical mechanics. It identifies the principal function as the phase of a propagating wave-front in configuration space, where the trajectories are the rays orthogonal to the surfaces of constant \( S \). This geometric representation allows for the <strong>Total Dynamics</strong> to be viewed as the evolution of a field, anchoring <strong>Scientific Realism</strong> in the realization that particles are merely the 'Markers' of a deeper variational wavefront.</p>

                    <h3>2. Principal Function as a Generating Function</h3>
                    <p>The principal function acts as a <strong>Type-2 Generating Function</strong> (\( F_2 \)) for a canonical transformation that transforms the coordinates and momenta into constant values (the initial state). The transformation equations, \( p_i = \frac{\partial S}{\partial q_i} \) and \( Q_i = \frac{\partial S}{\partial P_i} \), ensure that the new Hamiltonian is identically zero. This reduction proves that the complexity of motion is a coordinate-dependent artifact; in the 'Frame' defined by the principal function, the system is stationary. This insight is fundamental to <strong>Analytical Mechanics</strong>, providing the link between the flow of time and the <strong>Symmetry</strong> of the state space manifold.</p>

                    <h3>3. The Hero Formula and the Wavefront Identity</h3>
                    <p>The mathematical anchor of the Hamilton-Jacobi program is the identity that relates the total time-derivative of the principal function to the Lagrangian. This relation serves as the definitive gatekeeper for the wave-like interpretation of mechanics:</p>
                    \[ \frac{dS}{dt} = L \]
                    <p>This 'Hero Formula' underscores that the principal function (\( S \)) is the temporal accumulation of the <strong>Lagrangian</strong> along the optimal path. It provides the visual anchor for understanding how the scalar energy landscape dictates the growth of the action field, revealing the deep unity between the integral history of a system and its local differential evolution through the 4D <strong>Block Universe</strong>.</p>

                    <h3>4. Quantum Origins: The WKB Approximation</h3>
                    <p>At the subatomic scale, Hamilton's principal function is revealed as the macroscopic limit of the quantum phase. In the <strong>WKB Approximation</strong>, the wave function is expressed as \( \psi \sim e^{iS/\hbar} \), where \( S \) is the classical principal function. As the action becomes large relative to the <strong>Quantum of Action</strong> (\( \hbar \)), the Schrödinger equation reduces identically to the Hamilton-Jacobi equation. This derivation proves that classical mechanics is the 'Geometric Optics' limit of quantum wave mechanics, where the principal function guides the 'Rays' of physical trajectories through the vacuum.</p>

                    <h3>5. The Limiting Case: From Wavefronts to Trajectories</h3>
                    <p>Hamilton's principal function serves as the parent logic for the **Limiting Case** of standard Newtonian trajectories. As the system transitions from the field-based Hamilton-Jacobi description to the point-particle limit, the surfaces of constant action contract into the individual paths governed by <strong>Newton's Second Law</strong>. In this limit, the complex partial differential equations of the wavefront reduce to the simple ordinary differential equations of force-vectors. This reduction proves that the principal function is an <strong>Effective Ontology</strong>—a high-level map that resolves the underlying unity between the continuous propagation of energy and the discrete motion of matter.</p>"""

    data["principal-function"].update({
        "title": "Hamilton's Principal Function",
        "content": pf_content,
        "snippet": "The time-dependent solution to the Hamilton-Jacobi equation—formally termed Hamilton's principal function—establishes the bridge between variational history and wave-like propagation. In university-level mechanics, it serves as the action evaluated along physical paths, providing the generating function that reduces complex dynamics to a state of equilibrium within the configuration space manifold.",
        "snippet_svg": "The time-dependent solution to the Hamilton-Jacobi equation—formally termed Hamilton's principal function—establishes the bridge between variational history and wave-like propagation. In university-level mechanics, it serves as the action evaluated along physical paths, providing the generating function that reduces complex dynamics to a state of equilibrium within the configuration space manifold.",
        "hero_math": r"\[ \frac{dS}{dt} = L \]",
        "standard": "platinum"
    })

    # Action Integral
    ai_content = r"""<p>The temporal integration of the Lagrangian scalar along a specific path in configuration space—termed the action integral—establishes the primary physical quantity optimized by nature to determine the laws of motion. Formulated as the fundamental functional of the <strong>Variational Program</strong>, the action integral (\( S \)) assigns a single numerical 'Cost' to every possible history of a system. In university-level mechanics, the action integral is not merely a mathematical abstraction but the definitive informational measure of a system's evolution, where the stationarity condition (\( \delta S = 0 \)) reveals the underlying geometric structure of the 4D <strong>Block Universe</strong> and the coupling between energy and time.</p>

                    <h3>1. Definition and Dimensionality</h3>
                    <p>Mathematically, the action integral is defined as \( S = \int_{t_1}^{t_2} L(q, \dot{q}, t) dt \). The units of action are <strong>Energy \(\times\) Time</strong> (Joule-seconds), which are identically the same as the units of <strong>Angular Momentum</strong>. In university-level theory, this dimensional coincidence is a hint of the deep link between the action integral and the <strong>Symmetry</strong> of rotations. The action serves as the 'Global Currency' of dynamics; by extremizing this total sum, the system identifies the trajectory that minimizes the 'Waste' of dynamical potential, anchoring <strong>Scientific Realism</strong> in the optimality of physical laws.</p>

                    <h3>2. Action as a Functional of Histories</h3>
                    <p>The action integral operates as a <strong>Functional</strong>, taking an entire function (the path) as its input and returning a scalar. This path-based view is the cornerstone of <strong>Analytical Mechanics</strong>. It implies that the physics of a system is not determined by its state at a single instant, but by its entire history between two fixed boundary conditions. This holistic requirement ensures that the resulting <strong>Euler-Lagrange Equations</strong> are stable and globally consistent, providing the necessary scaffolding for formulating theories of <strong>Total Dynamics</strong> in both classical and relativistic regimes.</p>

                    <h3>3. The Hero Formula and the Action Definition</h3>
                    <p>The mathematical anchor for the variational program is the identity that defines the total accumulation of the Lagrangian over time. This relation serves as the definitive gatekeeper for the stationarity condition:</p>
                    \[ S[q(t)] = \int_{t_1}^{t_2} [T(\dot{q}) - V(q)] \, dt \]
                    <p>This 'Hero Formula' underscores that the action integral (\( S \)) is the net difference between kinetic and potential energy integrated over the system's duration. It provides the visual anchor for understanding how the scalar energy landscape dictates the physical paths, revealing the deep coupling between the system's internal energy and the geometric flow of the manifold.</p>

                    <h3>4. The Quantum of Action: Planck's Constant</h3>
                    <p>In the regime of <strong>Quantum Physics</strong>, the action integral takes on its most fundamental role as the phase of the system's probability amplitude. The <strong>Quantum of Action</strong> (\( \hbar \)) defines the scale at which the discrete nature of the action integral becomes apparent. In Feynman's path integral, every possible path is weighted by the factor \( e^{iS/\hbar} \). This proves that the classical 'Action Integral' is actually the macroscopic summary of constructive quantum interference, where the most stable path is the only one that survives the <strong>De-coherence</strong> of the vacuum.</p>

                    <h3>5. The Limiting Case: From Integration to Forces</h3>
                    <p>The action integral serves as the parent logic for the **Limiting Case** of instantaneous Newtonian forces. As the integration interval (\( \Delta t \)) is conceptually reduced to an infinitesimal point, the global optimization of the action integral reduces identically to the local application of <strong>Newton's Second Law</strong> (\( \mathbf{F} = m\mathbf{a} \)). In this limit, the holistic history of the system collapses into a sequence of force-driven events. This reduction proves that the action integral is an <strong>Effective Ontology</strong>—a more comprehensive and robust language that captures the essential causal structure of physics across all temporal and spatial scales.</p>"""

    data["action-integral"].update({
        "title": "Action Integral",
        "content": ai_content,
        "snippet": "The temporal integration of the Lagrangian scalar along a specific path—termed the action integral—establishes the primary physical quantity optimized by nature to determine the laws of motion. In university-level theory, it serves as the foundational functional of the variational program, providing a holistic measure of a system's evolution and the coupling between energy and time.",
        "snippet_svg": "The temporal integration of the Lagrangian scalar along a specific path—termed the action integral—establishes the primary physical quantity optimized by nature to determine the laws of motion. In university-level theory, it serves as the foundational functional of the variational program, providing a holistic measure of a system's evolution and the coupling between energy and time.",
        "hero_math": r"\[ S[q(t)] = \int_{t_1}^{t_2} [T(\dot{q}) - V(q)] \, dt \]",
        "standard": "platinum"
    })

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    refactor_cm()
    refactor_tp()
