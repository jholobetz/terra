# Task: Refactor 10 Subtopics
Generate a JSON object where each key is a subtopic slug.
Each subtopic must have:
- "title": string
- "parents": array of strings (top-level categories)
- "content": string (HTML with 6 sections, university-level depth, MathJax)
- "formulas": array of objects { "title", "equation", "breakdown" }
- "visual_config": object { "type", "color", "complexity" }

## Targets:
1. `flux-balance`
2. `intrinsic-spin`
3. `laplacian-operator`
4. `harmonic-functions-physics`
5. `neutral-equilibrium-physics`
6. `gradient-potential-relationship`
7. `maximum-principle-harmonic`
8. `poynting-theorem-physics`
9. `gausss-theorem`
10. `stokes-theorem`

## Reference Links (ensure these are used as strong/a links in content):
- flux-balance: gausss-law, conservation-law, local-conservation, faradays-law
- intrinsic-spin: fermi-dirac-statistics, anomalous-magnetic-moment
- laplacian-operator: potential-theory, poisson-equation, laplace-equation, schrodinger-equation
- harmonic-functions-physics: laplace-equation, potential-theory, entropy
- neutral-equilibrium-physics: potential-energy, cyclic-coordinates, lagrangian, noethers-theorem
- gradient-potential-relationship: potential-energy, equipotential-surface
- maximum-principle-harmonic: laplace-equation, potential-theory, static-equilibrium
- poynting-theorem-physics: total-mechanical-energy, kinetic-energy, electromagnetic-radiation
- gausss-theorem: vector-calculus, flux-balance, divergence, conservation-law, gausss-law, greens-identities
- stokes-theorem: vector-calculus, curl, right-hand-rule, faradays-law, amperes-law, differential-forms

## Technical Standards:
- University level.
- 6 sections per subtopic.
- MathJax: `\\(` for inline, `\\\\[` for display.
- Every formula referenced in content MUST be in the "formulas" array.
- Avoid AI fluff.
- Use `<strong><a href="/physics/subtopic/slug" class="subtopic-link">Title</a></strong>` for internal links.

