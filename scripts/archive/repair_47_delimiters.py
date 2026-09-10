#!/usr/bin/env python3
"""
scripts/maintenance/repair_47_delimiters.py

Surgically repairs the remaining 54 field occurrences across 47 formulas
with narrative delimiter errors. Validates every entry against scripts.lib.delimiters.
"""

import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from scripts.lib.delimiters import validate_narrative_delimiters

REPAIRS = {
    ("00/shard_00.json", "mathematical-proxy-4e628999", "symmetry_origin"):
        "This equation is a direct consequence of the definition of the partial derivative. It asserts that the rate of change of a coordinate $\\bar{x}^\\mu$ with respect to another coordinate $x^\\alpha$, when holding all other $x$ coordinates constant, is represented by the transformation matrix $\\frac{\\partial \\bar{x}^\\mu}{\\partial x^\\alpha}$. Under coordinate transformations, this matrix acts as a Jacobian, which is fundamental to the transformation properties of tensors, ensuring that physical laws remain covariant under coordinate changes.",

    ("06/shard_06.json", "1d-poisson-equation-magnetic-potential", "symmetry_origin"):
        "Under the Coulomb gauge condition ($\\nabla \\cdot \\mathbf{A} = 0$), the vector potential satisfies the Poisson equation $\\nabla^2 A_x = -\\mu_0 J_x$. In one spatial dimension, this reduces directly to $\\frac{d^2 A_x}{dx^2} = -\\mu_0 J_x$.",

    ("0f/shard_0f.json", "equipotential-surface-f83eec6f", "symmetry_origin"):
        "An equipotential surface is characterized by a constant scalar potential $V(\\mathbf{r}) = C$, implying that the differential $dV = \\nabla V \\cdot d\\mathbf{r} = 0$. Because the electric field is $\\mathbf{E} = -\\nabla V$, it follows that $\\mathbf{E} \\cdot d\\mathbf{r} = 0$, meaning the electric field is perpendicular to equipotential surfaces everywhere.",

    ("11/shard_11.json", "structural-survival-b7d99c5f", "interpretation"):
        "The invariance of the action under coordinate transformations ensures that the equations of motion retain their Euler-Lagrange form across all inertial and generalized coordinate systems.",

    ("14/shard_14.json", "field-operator-acting-on-test-function", "interpretation"):
        "The equation $\\hat{\\phi}(f) = \\int \\hat{\\phi}(x) f(x) d^4x$ defines the smeared quantum field operator acting on a smooth test function $f(x)$ of compact support.",

    ("14/shard_14.json", "field-operator-acting-on-test-function", "limits_and_boundary"):
        "In the limit where the test function $f(x)$ approaches a Dirac delta distribution $\\delta^{(4)}(x - x_0)$, the smeared operator $\\hat{\\phi}(f)$ formally approaches the local operator $\\hat{\\phi}(x_0)$.",

    ("1d/shard_1d.json", "technical-relation-3740ce7e", "symmetry_origin"):
        "This formula originates from Poynting's theorem. The electromagnetic energy density $u = \\frac{1}{2} \\left( \\varepsilon_0 E^2 + \\frac{1}{\\mu_0} B^2 \\right)$ yields an average energy density $\\langle u \\rangle = \\frac{1}{2} \\varepsilon_0 E_0^2$ for sinusoidal electromagnetic waves in vacuum.",

    ("1f/shard_1f.json", "static-limits-of-maxwell-s-equations-d128c4d7", "interpretation"):
        "In the static limit, the induced electric field from changing magnetic fields vanishes ($\\nabla \\times \\mathbf{E} = 0$), allowing the electric field to be represented as the gradient of a scalar electrostatic potential ($\\mathbf{E} = -\\nabla V$). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density ($\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}$).",

    ("25/shard_25.json", "monochromaticity-6968c906", "symmetry_origin"):
        "This formula arises as a plane wave solution $e^{i(\\mathbf{k} \\cdot \\mathbf{r} - \\omega t)}$ to the wave equation, reflecting spacetime translation invariance with temporal period $T = 2\\pi/\\omega$ and wavelength $\\lambda = 2\\pi/|\\mathbf{k}|$.",

    ("28/shard_28.json", "big-bounce-identity-1-2db21b48-47486926", "limits_and_boundary"):
        "When the matter density $\\rho$ approaches the critical density $\\rho_{\\text{crit}}$, the factor $\\left(1 - \\frac{\\rho}{\\rho_{\\text{crit}}}\\right)$ approaches zero, causing the Hubble parameter $H$ to vanish and producing a cosmological bounce.",

    ("28/shard_28.json", "poisson-equation-for-magnetic-vector-potential-8dc89e7b", "symmetry_origin"):
        "In the Coulomb gauge $\\nabla \\cdot \\mathbf{A} = 0$, Ampere's law $\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}$ reduces via vector calculus to the vector Poisson equation $\\nabla^2 \\mathbf{A} = -\\mu_0 \\mathbf{J}$.",

    ("2b/shard_2b.json", "unitary-evolution-8b94ea18", "symmetry_origin"):
        "Originating from the Schrodinger equation $i\\hbar \\frac{\\partial |\\psi\\rangle}{\\partial t} = H|\\psi\\rangle$ and the density matrix definition $\\rho = |\\psi\\rangle\\langle\\psi|$, differentiation yields the von Neumann equation $i\\hbar \\frac{\\partial \\rho}{\\partial t} = [H, \\rho]$.",

    ("31/shard_31.json", "curvature-proof-c14eb64c", "symmetry_origin"):
        "The curvature tensor satisfies the algebraic Bianchi identities, ensuring geometric consistency in general relativity.",

    ("32/shard_32.json", "phase-shift-1694fda8", "conceptual_definition"):
        "This formula relates the electromotive force $\\mathcal{E}$ induced in a closed conducting loop to the time rate of change of the magnetic vector potential $\\mathbf{A}$ along the path of the loop.",

    ("32/shard_32.json", "phase-shift-1694fda8", "interpretation"):
        "The equation $\\mathcal{E} = -\\oint \\dot{\\mathbf{A}} \\cdot d\\mathbf{l}$ quantifies the induced electromotive force around a closed path in terms of the time derivative $\\dot{\\mathbf{A}} = \\frac{\\partial \\mathbf{A}}{\\partial t}$ of the vector potential.",

    ("32/shard_32.json", "phase-shift-1694fda8", "symmetry_origin"):
        "This formula is a consequence of Faraday's Law of Induction $\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}$ combined with the vector potential definition $\\mathbf{B} = \\nabla \\times \\mathbf{A}$ and Stokes' theorem.",

    ("32/shard_32.json", "phase-shift-1694fda8", "limits_and_boundary"):
        "As the time rate of change $\\dot{\\mathbf{A}}$ approaches zero, the induced electromotive force $\\mathcal{E}$ vanishes.",

    ("32/shard_32.json", "translational-kinetic-energy-formula-0bff9b78", "symmetry_origin"):
        "The form of kinetic energy as $T = \\frac{1}{2} m v^2$ arises from the principle of least action and Galilean invariance, reflecting time translation symmetry and energy conservation.",

    ("37/shard_37.json", "medium-independence-dd8b7af2", "symmetry_origin"):
        "The continuity of the normal component of magnetic flux density $B_{1n} = B_{2n}$ follows directly from Gauss's law for magnetism $\\nabla \\cdot \\mathbf{B} = 0$.",

    ("38/shard_38.json", "moment-of-inertia-tensor", "symmetry_origin"):
        "The moment of inertia tensor $I_{ij} = \\sum_k m_k (r_k^2 \\delta_{ij} - x_{k,i} x_{k,j})$ is symmetric ($I_{ij} = I_{ji}$) under index permutation, reflecting spatial rotational invariance.",

    ("42/shard_42.json", "condition-for-critical-points-of-a-scalar-potential-a6b83587", "interpretation"):
        "Critical points of a scalar potential occur where the gradient vanishes: $\\nabla V(\\phi) = 0$, indicating stationary equilibrium configurations.",

    ("42/shard_42.json", "condition-for-critical-points-of-a-scalar-potential-a6b83587", "symmetry_origin"):
        "Stationary points of the potential $V(\\phi)$ correspond to field configurations where the variational derivative $\\frac{\\delta S}{\\delta \\phi} = 0$ is satisfied in the static limit.",

    ("5c/shard_5c.json", "second-london-equation-flux-expulsion-7a32210c", "symmetry_origin"):
        "The second London equation $\\nabla^2 \\mathbf{B} = \\frac{1}{\\lambda_L^2} \\mathbf{B}$ follows from the London gauge formulation of the superconducting order parameter, describing the Meissner effect.",

    ("64/shard_64.json", "magnetic-field-definition-22e80712", "symmetry_origin"):
        "The magnetic field $\\mathbf{B} = \\nabla \\times \\mathbf{A}$ is identically divergence-free ($\\nabla \\cdot \\mathbf{B} = 0$) due to the vector calculus identity $\\nabla \\cdot (\\nabla \\times \\mathbf{A}) = 0$.",

    ("67/shard_67.json", "grid-density-36cb87aa", "symmetry_origin"):
        "The canonical commutation relation $[\\hat{x}, \\hat{p}] = i\\hbar$ follows from the representation of momentum as the spatial translation generator $\\hat{p} = -i\\hbar \\frac{\\partial}{\\partial x}$.",

    ("6b/shard_6b.json", "distance-preservation-a3f26c31", "symmetry_origin"):
        "Under an isometric transformation, the Riemannian metric preserves infinitesimal arc length: $ds^2 = g_{\\mu \\nu} dx^\\mu dx^\\nu$.",

    ("71/shard_71.json", "completeness-relation", "conceptual_definition"):
        "The completeness relation (resolution of the identity) states that for an orthonormal basis $\\{|n\\rangle\\}$ of a Hilbert space $\\mathcal{H}$, the identity operator satisfies $\\sum_n |n\\rangle \\langle n| = \\mathbb{I}$.",

    ("75/shard_75.json", "symmetry-persistence-636f2490", "symmetry_origin"):
        "Symmetry persistence ensures that global gauge transformations $\\psi \\to e^{i\\alpha}\\psi$ leave the Lagrangian invariant, generating conserved Noether currents.",

    ("84/shard_84.json", "exclusion-principle-b4790b37", "interpretation"):
        "The anti-symmetry condition $\\Psi(1, 2) = -\\Psi(2, 1)$ requires the total wavefunction to change sign under interchange of two identical fermions, precluding identical quantum states.",

    ("89/shard_89.json", "total-time-derivative-in-hamiltonian-mechanics-bd4731f2", "symmetry_origin"):
        "The total time derivative of an observable $A$ in Hamiltonian mechanics is given by $\\frac{dA}{dt} = \\{A, H\\} + \\frac{\\partial A}{\\partial t}$, generated by the Poisson bracket with $H$.",

    ("8f/shard_8f.json", "symmetry-source-221e1d3a", "symmetry_origin"):
        "Invariance under spatial rotations and Lorentz boosts establishes the conserved angular momentum and stress-energy tensors.",

    ("94/shard_94.json", "aharonov-bohm-link-19c525d5", "symmetry_origin"):
        "The Aharonov-Bohm phase shift $\\Delta\\phi = \\frac{q}{\\hbar} \\oint \\mathbf{A} \\cdot d\\mathbf{l}$ reflects the non-local topological influence of magnetic flux in quantum mechanics.",

    ("9f/shard_9f.json", "pseudo-force-in-non-inertial-frames-cb01b814", "conceptual_definition"):
        "When an observer is in a non-inertial reference frame accelerating at $\\mathbf{a}_{\\text{frame}}$, objects experience a fictitious force $\\mathbf{F}_{\\text{fict}} = -m \\mathbf{a}_{\\text{frame}}$.",

    ("9f/shard_9f.json", "pseudo-force-in-non-inertial-frames-cb01b814", "interpretation"):
        "The fictitious force $\\mathbf{F}_{\\text{fict}} = -m \\mathbf{a}_{\\text{frame}}$ acts in the direction opposite to the frame acceleration, allowing Newton's laws to hold in accelerating frames.",

    ("9f/shard_9f.json", "pseudo-force-in-non-inertial-frames-cb01b814", "limits_and_boundary"):
        "In the limit where the frame acceleration vanishes ($\\mathbf{a}_{\\text{frame}} = 0$), the reference frame is inertial and $\\mathbf{F}_{\\text{fict}} = 0$.",

    ("a1/shard_a1.json", "mass-defect-87f1adbf", "conceptual_definition"):
        "The mass defect $\\Delta m$ is defined as the total mass of $Z$ free protons and $A-Z$ free neutrons minus the true invariant nuclear mass: $\\Delta m = Zm_p + (A-Z)m_n - M_{\\text{nuc}}$.",

    ("a4/shard_a4.json", "scattering-wave-function", "limits_and_boundary"):
        "In the asymptotic limit $r \\to \\infty$, the scattering wavefunction takes the form $\\psi(\\mathbf{r}) \\sim e^{i\\mathbf{k} \\cdot \\mathbf{r}} + f(\\theta, \\phi) \\frac{e^{ikr}}{r}$.",

    ("a4/shard_a4.json", "invariant-momentum-transfer-squared-6552e560", "interpretation"):
        "The Mandelstam variable $t = (p_1 - p_3)^2$ represents the invariant four-momentum transfer squared in particle scattering processes.",

    ("a7/shard_a7.json", "magnetic-field-from-vector-potential-curl", "symmetry_origin"):
        "The definition $\\mathbf{B} = \\nabla \\times \\mathbf{A}$ guarantees the absence of magnetic monopoles via $\\nabla \\cdot \\mathbf{B} = \\nabla \\cdot (\\nabla \\times \\mathbf{A}) = 0$.",

    ("b0/shard_b0.json", "complex-amplitude-solution-harmonic-oscillation", "interpretation"):
        "The solution $\\mathbf{x}(t) = \\mathbf{A} e^{i\\omega t}$ represents harmonic oscillation in the complex plane, with physical displacement $x(t) = A_0 \\cos(\\omega t + \\phi)$.",

    ("bc/shard_bc.json", "von-neumann-equation-d91c4ab1", "limits_and_boundary"):
        "In the classical limit $\\hbar \\to 0$, the von Neumann commutator $\\frac{1}{i\\hbar}[H, \\rho]$ transitions to the classical Poisson bracket $\\{H, \\rho\\}$ via Dirac's correspondence principle.",

    ("cd/shard_cd.json", "geometric-law-5454a60c", "symmetry_origin"):
        "The covariant conservation law $\\nabla_\\mu T^{\\mu\\nu} = 0$ follows from the contracted Bianchi identities $\\nabla_\\mu G^{\\mu\\nu} = 0$ via the Einstein field equations.",

    ("d1/shard_d1.json", "position-uncertainty-confinement-length-325240e0", "interpretation"):
        "For a particle confined to a region of size $L$, the position uncertainty satisfies $\\Delta x \\approx L$, leading to momentum uncertainty $\\Delta p \\ge \\frac{\\hbar}{2L}$ by the Heisenberg uncertainty principle.",

    ("d8/shard_d8.json", "electrostatic-potential-from-charge-distribution-46b485b8", "interpretation"):
        "The electrostatic potential $\\Phi(\\mathbf{r}) = \\frac{1}{4\\pi\\varepsilon_0} \\int \\frac{\\rho(\\mathbf{r}')}{|\\mathbf{r} - \\mathbf{r}'|} d^3\\mathbf{r}'$ superpositionally integrates the contributions of continuous charge density $\\rho$.",

    ("d9/shard_d9.json", "growth-law-edef5bc8-35b90fdb", "limits_and_boundary"):
        "In an Einstein-de Sitter universe, the scale factor evolves as $a(t) \\propto t^{2/3}$ during matter domination.",

    ("de/shard_de.json", "effective-metric-hamiltonian", "symmetry_origin"):
        "The Hamiltonian for a particle in curved spacetime $H = \\frac{1}{2m} g^{\\mu\\nu} p_\\mu p_\\nu$ reflects general covariance under spacetime coordinate transformations.",

    ("e8/shard_e8.json", "electric-potential-difference-definition-a53f5c0b", "interpretation"):
        "The potential difference $\\Delta V = V_B - V_A = -\\int_A^B \\mathbf{E} \\cdot d\\mathbf{l}$ measures the work done per unit charge in moving between points $A$ and $B$.",

    ("e9/shard_e9.json", "faraday-s-law-of-induction-electric-field-curl-a1540a18", "interpretation"):
        "The curl operator $\\nabla \\times \\mathbf{E}$ measures the local circulation density of the electric field induced by time-varying magnetic flux.",

    ("ec/shard_ec.json", "slope-of-the-wave-be799285", "symmetry_origin"):
        "The fundamental canonical commutation relation $[\\hat{q}, \\hat{p}] = i\\hbar$ arises directly from representing momentum as the differential operator $\\hat{p} = -i\\hbar \\frac{\\partial}{\\partial q}$.",

    ("ef/shard_ef.json", "quantum-time-evolution-exponential-factor-f4effee6", "interpretation"):
        "Physically, $\\hat{H}$ serves as the infinitesimal generator of temporal translations. Because $\\hat{H}$ is self-adjoint ($\\hat{H}^\\dagger = \\hat{H}$), the resulting exponential factor is unitary ($\\hat{U}^\\dagger \\hat{U} = \\mathbb{I}$), ensuring probability conservation over time $t$. The imaginary unit $i$ facilitates oscillatory wave dynamics, while the reduced Planck constant $\\hbar$ converts the energy spectrum of $\\hat{H}$ into angular frequencies $\\omega_n = E_n / \\hbar$.",

    ("f2/shard_f2.json", "torque-magnetic-dipole", "symmetry_origin"):
        "The torque on a magnetic dipole $\\boldsymbol{\\tau} = \\mathbf{m} \\times \\mathbf{B}$ arises from the Lorentz force law, reflecting rotational invariance in spatial coordinate systems.",

    ("f5/shard_f5.json", "non-spin-rule-2298445b", "symmetry_origin"):
        "The mathematical identity $\\nabla \\times (\\nabla \\Phi) = 0$ follows directly from the equality of mixed partial derivatives for smooth scalar fields.",

    ("fd/shard_fd.json", "static-limits-of-maxwell-s-equations-1fcb33ff", "interpretation"):
        "In the static limit, the induced electric field from changing magnetic fields vanishes ($\\nabla \\times \\mathbf{E} = 0$), allowing the electric field to be represented as the gradient of a scalar electrostatic potential ($\\mathbf{E} = -\\nabla V$). Simultaneously, the displacement current term vanishes, causing the curl of the magnetic field to depend exclusively on static current density ($\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J}$).",

    ("fe/shard_fe.json", "torque-component-euler-equation", "symmetry_origin"):
        "This formula is derived from Euler's rotational equations of motion, expressing torque $\\boldsymbol{\\tau} = \\frac{d\\mathbf{L}}{dt}$ in the body-fixed principal axes frame."
}


def main():
    formulas_base = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

    # Step 1: Pre-validate all repair texts
    for (rel_path, fid, field), clean_text in REPAIRS.items():
        errs = validate_narrative_delimiters(clean_text)
        assert len(errs) == 0, f"Repair for {fid}[{field}] failed validation: {errs}"

    print(f"Verified all {len(REPAIRS)} repair texts pass validate_narrative_delimiters.")

    # Step 2: Apply repairs grouped by shard
    shards_to_update = {}
    for (rel_path, fid, field), clean_text in REPAIRS.items():
        full_path = os.path.join(formulas_base, rel_path)
        shards_to_update.setdefault(full_path, []).append((fid, field, clean_text))

    updated_fields = 0
    for shard_path, items in shards_to_update.items():
        if not os.path.exists(shard_path):
            print(f"WARN: Shard path not found: {shard_path}")
            continue
        with open(shard_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for fid, field, clean_text in items:
            if fid in data and isinstance(data[fid], dict):
                data[fid][field] = clean_text
                updated_fields += 1
            else:
                print(f"WARN: {fid} not in {shard_path}")

        with open(shard_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)


    print(f"Successfully updated {updated_fields} / {len(REPAIRS)} fields across {len(shards_to_update)} shards.")


if __name__ == "__main__":
    main()
