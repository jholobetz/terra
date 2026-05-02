# TASK: Generate 10 Physics Subtopics (Platinum Standard)

## Targets:
1. `paramagnetism`
2. `curies-law`
3. `ferromagnetism`
4. `exchange-interactions`
5. `magnetic-hysteresis`
6. `bohr-magneton`
7. `macroscopic-ampere-law`
8. `bound-surface-current`
9. `free-currents-magnetism`
10. `spacetime-events`

## Guidelines:
- **Tone:** Senior university lecture style. Fulsome and rigorous.
- **Length:** >800 words per subtopic.
- **Structure:** 4 to 8 numbered sections with `<h3>`.
- **Linking:** ONLY use the provided `authorized_slugs`.
- **Math:** Use `\\(` and `\\)` for inline, and `\\\\[` and `\\\\]` for display-style equations.
- **JSON Format:**
  {
    "slug": {
      "title": "Title",
      "content": "...",
      "formulas": [
        {
          "title": "Formula Name",
          "equation": "LaTeX",
          "breakdown": "Explanation"
        }
      ],
      "parents": ["category-slug"]
    }
  }

## Authorized Slugs for Linking:
[non-conservative-fields, continuity-equation, displacement-current, magnetic-intensity, magnetic-boundary-conditions, laplaces-equation, ampere-maxwell-law, ampere-integral-form, field-intensity-relation, magnetic-interface-condition, moving-charges, permeability-free-space, cross-product, right-hand-rule, principle-of-superposition, infinite-straight-wire, circular-loop, inverse-square-law-physics, orthogonal-vectors, magnetic-source-types, field-directionality, radial-fields, transverse-fields, magnetic-field-conservation, relativistic-correction-magnetism, differential-form-magnetism, integral-form-magnetism, solenoidal-condition, four-momentum, conservation-of-mechanical-energy, closed-path, irrotational-fields, invariant-of-the-motion, gravitational-fields, electrostatic-fields, elastic-forces, symmetries, simply-connected, vorticity, path-independence, gradient-relation, potential-definition, divergent-fields, dirac-delta, greens-function, electrostatic-potential-energy, energy-density, photon-mass, yukawa-potential, static-law, retarded-potentials, maxwells-equations, coulomb-force, field-energy, electromagnetic-4-potential, four-current-density, minkowski-force, gauge-theories, homogeneous-maxwell, four-force-equation, electromagnetic-induction, magnetostatic-circulation, div-curl-zero, cylindrical-coordinates, spherical-coordinates, curl-operator, geometric-bridge, electromagnetic-field-tensor, relativistic-unification, boundary-conditions, field-potential-relation, negative-gradient, equipotential-surface, always-perpendicular, coulomb-potential, voltage, electromotive-force, field-integration, source-summation, potential-difference, gradient-link, acceleration-radiation, larmor-formula, retarded-time, lienard-wiechert, heaviside-feynman, near-field-zone, far-field-zone, oscillating-electric-dipole, relativistic-beaming, bremsstrahlung, synchrotron-radiation, relativistic-larmor, monochromatic-plane-waves, propagation-vector, fourier-synthesis, transverse-nature, polarization, dalembertian-operator, velocity-of-light, paramagnetism, curies-law, ferromagnetism, exchange-interactions, magnetic-hysteresis, bohr-magneton, macroscopic-ampere-law, bound-surface-current, free-currents-magnetism, spacetime-events]

## Output:
A single JSON object containing all 10 subtopics.
