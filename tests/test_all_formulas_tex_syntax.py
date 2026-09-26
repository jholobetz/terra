import json
import os
import re
import glob
import pytest

SHARDS_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "config", "content", "formulas")

def get_all_shard_formulas():
    shard_files = sorted(glob.glob(os.path.join(SHARDS_DIR, "*", "shard_*.json")))
    all_files = shard_files

    formulas = []
    for fpath in all_files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for fid, fval in data.items():
                        if isinstance(fval, dict):
                            formulas.append((fid, fval))
        except Exception:
            continue
    return formulas

ALL_FORMULAS = get_all_shard_formulas()

from scripts.lib.delimiters import (
    strip_math_blocks,
    count_unescaped_dollars,
    validate_narrative_delimiters,
)

NARRATIVE_FIELDS = [
    "conceptual_definition",
    "intuitive_summary",
    "interpretation",
    "limits_and_boundary",
    "symmetry_origin",
]

def test_all_formulas_count():
    assert len(ALL_FORMULAS) >= 14600, f"Expected >= 14600 formulas, found {len(ALL_FORMULAS)}"

def test_all_formulas_tex_dollar_balance():
    corrupted = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            dollar_count = count_unescaped_dollars(text)
            if dollar_count % 2 != 0:
                corrupted.append((fid, field, dollar_count, text[:100]))
    assert len(corrupted) == 0, f"Found {len(corrupted)} unclosed dollar signs: {corrupted[:10]}"

def test_all_formulas_narrative_delimiters():
    violations = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            errs = validate_narrative_delimiters(text)
            for err in errs:
                violations.append((fid, field, err))
    assert len(violations) == 0, f"Found {len(violations)} formula narrative delimiter errors: {violations[:10]}"

def test_all_formulas_no_mangled_tex_macros():
    corrupted_pattern = re.compile(r"\\sqrt\$\{|\$g_\{\$\\mu\$ u\}|\\to'|'\+\$\S+'")
    corrupted = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            match = corrupted_pattern.search(text)
            if match:
                corrupted.append((fid, field, match.group(0)))
    assert len(corrupted) == 0, f"Found {len(corrupted)} corrupted TeX macro instances: {corrupted[:10]}"

LEGACY_LEAKED_FORMULAS = {
    '4d-curl-211eef85', 'acceleration-effect-c89fffcb', 'angular-momentum-approaches-zero',
    'axial-parity-identity-f42e4892', 'boltzmann-distribution', 'boundary-condition-normal-magnetic-field',
    'canonical-commutation-field-momentum', 'complex-flip-e5704062', 'cosmic-timing-720ab189',
    'cosmological-rule-3facc689', 'coulomb-gauge-identity-0e18071a', 'coulomb-potential-energy-656e5c99',
    'coupling-constant-qft-identity-1-7929f982-2f73da30', 'deceleration-parameter-limit',
    'definitive-solution-ee2ed125', 'density-sum-34098eaf', 'derived-values-967adf08',
    'differential-electric-flux-element', 'differential-work-and-potential-energy-change-5d05c37e',
    'differential-work-by-conservative-force-65197ed6', 'directional-derivative-scalar',
    'divergence-of-curl-zero', 'e-field-continuity-de3735c8', 'e-vs-b-48093a69',
    'effective-metric-hamiltonian', 'electric-field-from-electromagnetic-potentials-e7033e68',
    'electromagnetism-5ad10a96', 'electrostatic-potential-energy-of-two-charges-3fe3164b',
    'electrostatic-scalar-potential-from-static-charge-density-138b5385', 'emf-integral-definition-a3d86b92',
    'euler-lagrange-canonical-momentum-derivative-e346526c', 'euler-lagrange-equation',
    'exponential-expansion', 'exponential-growth-d48b2ba1', 'field-canonical-momentum-density-fd1adb0d',
    'field-definition-identity-1-d3934851-f11a1678', 'field-equation-d9a63102', 'field-link-d2faeecc',
    'field-momentum-commutator-component-236b46fb', 'field-operator-acting-on-test-function',
    'field-orientation-52a3ae4d', 'field-pulse-81d83e3f', 'flat-spacetime-limit-minkowski',
    'force-from-potential-energy-gradient-a09c32ed', 'frame-swap-62c711a0',
    'gauge-transformation-identity-1-56b6882c-de339f65', 'gauge-transformation-photon-field',
    'gausss-law-b8aa48e5', 'gausss-law-dielectric-medium',
    'gausss-law-for-electric-fields-differential-form-5eae672d',
    'generalized-flux-rule-for-moving-circuits-349d7995', 'generalized-momentum-component-eca91c83',
    'geodesic-link-d4b6b935', 'geometric-fall-820c9fbf', 'geometric-shield-e45b70a1',
    'geometric-start-ba4d589c', 'gradient-of-a-scalar-field-0c45fd93',
    'gradient-of-a-scalar-potential-4552642a', 'gradient-of-a-scalar-wave-function-876a7237',
    'gradient-of-scalar-potential-b293d129', 'grid-density-36cb87aa', 'higgs-boson-mass-squared-f8646f48',
    'hubble-parameter-evolution', 'integral-geometric-identity-e2f9202c', 'jacobi-metric',
    'low-reynolds-number-limit', 'magnetic-field-vanishes', 'magnetic-push-8cad2818',
    'magnitude-squared-angular-momentum', 'massless-or-high-energy-approximation-15771775',
    'matter-density-parameter-one', 'maxwells-equations-vacuum-formalism-c392d9cd',
    'mhd-induction-relation-fluids-50d163b6', 'minimum-volume-1afd8ce0', 'minkowski-spacetime-interval',
    'moment-inertia-tensor-component', 'monochromaticity-6968c906', 'navier-stokes-momentum-fluids-27e5bf4d',
    'no-motion-61d30ad3', 'one-dimensional-laplace-equation-for-magnetic-vector-potential-2d388f54',
    'optical-theorem-for-forward-scattering-e74af25e', 'orthogonal-triplet-d90b32e7',
    'parallel-axis-theorem', 'poisson-equation-for-magnetic-vector-potential-8dc89e7b',
    'poissons-equation-for-temperature-76971fc1', 'potential-link-1f375717',
    'power-law-density-profile-63fd7682', 'pressure-gradient-force-density-ea32abd5',
    'proof-method-3d88e2ef', 'propagation-rule-0c8a0748', 'quantum-commutator-limit',
    'radial-density-power-law-profile-fe5dbc40', 'redshift', 'redshift-approaches-zero',
    'redshift-approximation', 'relative-change-in-angular-momentum',
    'right-handed-weyl-spinor-field-7df86efa', 'rotation-operator', 'rotational-power',
    'scale-factor-approaches-unity', 'schwarzschild-radius-ratio',
    'schwarzschild-singularity-interval-b0150134', 'shakura-sunyaev-alpha-viscosity-2342c109',
    'spatial-derivative-of-scalar-field-4877778a', 'speed-barrier-2f04e8d8', 'stability-guard-29cfc76f',
    'stokes-theorem', 'stokes-theorem-for-electric-field-be47c565',
    'sturm-liouville-eigenvalue-methods-d8f21012', 'symmetry-source-221e1d3a',
    'tangent-function-of-an-angle-46da7a9a', 'the-monopole-46072aa5',
    'time-varying-gradient-of-scalar-potential-990b0280', 'timelike-condition-66404b96', 'torque',
    'torque-angular-momentum-relation', 'vacuum-resistance-26ee25d2',
    'vector-relation-potential-identity-1-50f70efd-0e0064f7', 'voltage-from-motion-4ba8b13e',
    'w-boson-mass-from-electroweak-unification-c49b69ef', 'wave-equation-electric-field',
    'wave-equation-four-potential', 'weak-field-approximation-of-metric-component-g00-dbd6cd97',
    'work-by-torque', 'work-rule-4da28176', 'yukawa-potential-range-approximation-f736c686',
    'zero-angular-momentum',
}

def test_all_formulas_no_leaked_tex_macros():
    tex_macro_check = re.compile(r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])")
    leaked = []
    for fid, formula in ALL_FORMULAS:
        for field in NARRATIVE_FIELDS:
            text = formula.get(field, "")
            if not text or not isinstance(text, str):
                continue
            text_no_math = strip_math_blocks(text)
            match = tex_macro_check.search(text_no_math)
            if match:
                leaked.append((fid, field, match.group(0)))

    new_leaks = [item for item in leaked if item[0] not in LEGACY_LEAKED_FORMULAS]
    assert len(new_leaks) == 0, f"Found {len(new_leaks)} new leaked TeX macros outside math mode: {new_leaks[:10]}"
    unique_leaked_fids = {item[0] for item in leaked}
    assert len(unique_leaked_fids) <= 127, f"Legacy leaked formula count unexpectedly increased: {len(unique_leaked_fids)} > 127"





