
import json
import re

grounding_list = ["flux-balance", "stable-equilibrium-physics", "electroweak-symmetry-group", "electric-potential", "laplacian-operator", "aharonov-bohm-effect", "conservation-of-linear-momentum", "principle-of-complementarity", "total-mechanical-energy", "amperes-law", "mathematical-methods", "electric-field", "generalized-stokes-theorem", "flavor-eigenstates", "vector-calculus", "maxwells-equations", "ferromagnetism", "magnetic-hysteresis", "reduced-density-matrix", "curl", "copenhagen", "magnetic-domains", "faraday-induction", "pilot-wave", "gauge-invariance", "local-realism", "field-definition", "coulomb-force", "covariant-formulation", "helmholtz-theorem", "born-interpretation", "canonical-momentum", "coulomb-gauge", "lenzs-law", "curies-law", "poynting-theorem-physics", "solenoidal-field", "intrinsic-spin", "potential-tool", "diamagnetism", "potential-field", "fundamental-theorem-calculus", "biot-savart-law", "electromagnetic-4-potential", "pbr-theorem", "harmonic-functions-physics", "group-theory-structure", "conservative-force-field", "pmns-matrix", "vector-potential", "vector-fields", "magnetic-mirroring", "electromagnetic-wave-equation", "retardation-physics", "newtons-first-law", "newtons-second-law", "rotational-symmetry", "gradient", "circulation-vorticity", "vector-poisson-equation", "laplace-equation", "ckm-matrix", "divergence", "poisson-equation", "free-currents-magnetism", "gausss-law-for-magnetism", "exchange-interactions", "isaac-newton", "electromagnetic-radiation", "s-matrix", "measurement-apparatus", "configuration-space", "density-matrix", "quantum-entanglement", "quantum-physics", "bound-surface-current", "maxwells-correction", "torque", "newtons-third-law", "non-locality", "faradays-law", "unstable-equilibrium-physics", "gradient-link", "ampere-maxwell-law", "virial-theorem-mechanics", "differential-forms", "emmy-noether", "synchrotron-radiation", "work-energy-theorem", "nabla-operator", "classical-mechanics", "photoelectric-effect", "inner-product", "paramagnetism", "electromagnetic-energy-density", "simple-harmonic-oscillator-mechanics", "stokes-theorem", "s-matrix-basis", "geometric-identity", "electromotive-force", "vector-relation-potential", "taylor-expansion-mechanics", "bohr-magneton", "right-hand-rule", "universal-calculus", "many-worlds", "gausss-theorem", "scalar-field", "adiabatic-invariants", "electromagnetism", "magnetic-matter", "wave-function", "irrotational-fields", "linear-momentum", "neutral-equilibrium-physics", "macroscopic-ampere-law", "de-broglie-hypothesis"]

with open('refactor_batch_23_a.json', 'r') as f:
    data = json.load(f)

for slug, subtopic in data.items():
    content = subtopic['content']
    links = re.findall(r'href="/physics/subtopic/([^"]+)"', content)
    for link in links:
        if link not in grounding_list:
            print(f"ERROR: {slug} contains unauthorized link: {link}")
    
    for parent in subtopic['parents']:
        if parent not in grounding_list:
            print(f"ERROR: {slug} has unauthorized parent: {parent}")
