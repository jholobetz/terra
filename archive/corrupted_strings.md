# Formula Catalog Integrity Audit: Corrupted Strings, Prose Bleed & Non-Equations (`docs/corrupted_strings.md`)

**Date:** 2026-11-03 (Remediated & Locked: 2026-11-07)  
**Status:** ✅ **REMEDIATED & LOCKED IN CI**
* **6 explicit garbage/placeholder records purged** (`uninterpretable-mathematical-fragment-9276d06a`, `invalid-mathematical-equation-placeholder-6cea8024`, `undefined-mathematical-expression-59452236`, `invalid-input-not-a-latex-equation`, `invalid-relation-four-momentum-squared-and-momentum-component-d9144d58`, `generic-mathematical-identifier-39b8b9bb`), recalibrating the catalog to **14,681 verified formulas**.
* **257 corrupted/control-character `equation` strings repaired** across the 256 hex shards (`0` corrupted equations remaining), and **1,151 prose fields sanitized** of stray ASCII control characters (`\x89`, `\x08`, `\x0c`, `\r`).
* **25 zero-affinity parent–child links resolved** (19 bare constants/SI prefixes/standalone rules detached to honest `DEFINITION` roots; 6 cross-domain false positives re-parented to their true physical parent laws).
* **Permanent CI & LHI Gates Active**: [`scripts/maintenance/audit_lineage_health.py`](../scripts/maintenance/audit_lineage_health.py) and [`tests/test_auto_draft_lineage.py`](../tests/test_auto_draft_lineage.py) now enforce `0` corrupted equations and `0` zero-affinity parent–child links across all 256 shards.

**Context:** Discovered while auditing **Bucket A** (16 zero-affinity parent–child links) during the Parent–Child Affinity dry run ([`docs/unfuckit.md`](unfuckit.md)). A subsequent deep scan across all **14,687 formulas** in the 256 hex shards (`app/config/content/formulas/[00-ff]/shard_[00-ff].json`) revealed a critical integrity blind spot that [`integrity_shield.py`](../integrity_shield.py) and [`scripts/assess`](../scripts/assess) were completely missing.

---

## 1. Executive Summary: What the Full-Catalog Scan Found

Across all **14,687 formulas**, there are **~110 corrupted or invalid `equation` strings (~0.75% of the catalog)**, plus **38 bare numbers / SI prefixes**:

### Category 1: "Prose-Bleed" Equations (~75 formulas)
In these records, the `equation` field contains **raw English prose sentences** (often starting or ending with a stray parenthesis or comma), even though the record's `title` and `conceptual_definition` describe a real physics equation:
* [`classical-velocity-limit-f2d70293`](../app/config/content/formulas/05/shard_05.json)
  * **Title**: *Non-Relativistic Velocity Limit Condition*
  * **Current `equation`**: `"v \\to 0\n)', the relativistic effects become negligible, and the object's behavior is well-described by classical Newtonian mechanics, where velocity can increase indefinitely. As '"`
  * **Inside `conceptual_definition`**: Contains the actual math `$v/c \to 0$` ($v \ll c$).
* [`first-generation-quark-components-3f9640ac`](../app/config/content/formulas/06/shard_06.json)
  * **Title**: *First Generation Left-Handed Quark Doublet*
  * **Current `equation`**: `") and the down quark ("`
  * **Inside `conceptual_definition`**: Contains the actual math `$Q_L = \begin{pmatrix} u \\ d \end{pmatrix}_L$`.
* [`quantum-number-definition-55238a7a`](../app/config/content/formulas/0a/shard_0a.json)
  * **Title**: *Definition of a Discrete Quantum Number*
  * **Current `equation`**: `"is an integer, known as the quantum number, which labels the specific allowed quantum state for that degree of freedom."`
  * **Inside `conceptual_definition`**: Contains the actual math `$n_i \in \mathbb{Z}$`.

### Category 2: Raw MathML & Control-Character Corruptions (~20 formulas)
In these records, unescaped backslashes (`\p`, `\t`, `\r`) or scraped MathML tags corrupted the `equation` field:
* [`canonical-momentum-definition`](../app/config/content/formulas/84/shard_84.json):
  * **Current `equation`**: `'p = \\frac{ tial L}{ tial v} = mv'` (`\par` was eaten from `\partial`)
* [`canonical-momentum-density-four-vector-field-theory`](../app/config/content/formulas/90/shard_90.json):
  * **Current `equation`**: `'\\pi^\\mu \\equiv \\frac{ tial \\mathcal{L}}{ tial ( tial_\\mu \\phi)}'`
* [`total-mass-of-two-particle-system-922d9f5e`](../app/config/content/formulas/b4/shard_b4.json):
  * **Current `equation`**: `'extit{M} = extit{m}_1 +'` (`\t` was eaten from `\textit` and equation truncated)
* [`angular-frequency-definition-60aa52f0`](../app/config/content/formulas/43/shard_43.json) & 10 others:
  * **Current `equation`**: `'math xmlns="http://www.w3.org/1998/Math/MathML"'` or `'/mo/mrow/msub/math'` (while `conceptual_definition` has the real equation `$\omega = \frac{d\theta}{dt}$`).

### Category 3: Explicit "Unrecoverable / Invalid" Garbage Placeholders (~10 formulas)
When an old auto-drafting script fed a broken token to the LLM, the LLM literally titled the formula "Invalid" or "Undefined", and the script saved it anyway (none of these are referenced by any subtopic):
* [`uninterpretable-mathematical-fragment-9276d06a`](../app/config/content/formulas/18/shard_18.json): Title: *Syntactically Invalid Mathematical String* | Eq: `'\\text{Unrecoverable Fragment}'`
* [`invalid-mathematical-equation-placeholder-6cea8024`](../app/config/content/formulas/46/shard_46.json): Title: *Non-Mathematical or Syntactically Invalid String* | Eq: `''`
* [`undefined-mathematical-expression-59452236`](../app/config/content/formulas/b4/shard_b4.json): Title: *Undefined Mathematical Expression* | Eq: `'\\text{N/A}'`
* [`invalid-input-not-a-latex-equation`](../app/config/content/formulas/b4/shard_b4.json): Title: *Invalid Input: Not a LaTeX Equation* | Eq: `'b1,b2,b3'`
* [`invalid-relation-four-momentum-squared-and-momentum-component-d9144d58`](../app/config/content/formulas/5b/shard_5b.json): Title: *Invalid Equality: Four-Momentum Norm Squared and a Spatial Momentum Component* | Eq: `'P^2 = p_y'`

### Category 4: Bare Numbers & SI Prefixes (38 formulas)
During an earlier prose sweep to make every `$ ... $` expression in prose resolve to a formula ID, inline numbers like `$10^{-3}$`, `$10^2$`, `$1/2$`, `$1/4$`, and `$10^{-15}$` were turned into standalone formula records and then force-parented onto physics laws to avoid "isolated node" penalties.

---

## 2. Root-Cause Analysis: Why Did Our Existing Audits Miss This?

1. **How they were created**: During an earlier batch run to reach "100% Prose Equation Closure," a regex extracted strings between `$ ... $` from prose that had mismatched delimiters—capturing the **English sentence between two equations** instead of the equation itself. When passed to the LLM auto-drafter, the LLM wrote a real physics `title` and put the real LaTeX equation inside `conceptual_definition`, while the script left the broken input string inside `"equation"`.
2. **Why `integrity_shield.py` passed them**: [`integrity_shield.py`](../integrity_shield.py) only checked that `{` and `}` braces were balanced! Because `"approaches the speed of light"` and `'math xmlns="http://www.w3.org/1998/Math/MathML"'` have zero `{` and zero `}`, they passed every check.

---

## 3. Remediation Plan (No Shortcuts)

To restore 100% mathematical integrity across the formula catalog:

1. **Purge the ~10 Explicit Garbage / "Invalid String" Records**:
   * Delete records that are literally placeholders for invalid input (`uninterpretable-mathematical-fragment-9276d06a`, `invalid-mathematical-equation-placeholder-6cea8024`, `undefined-mathematical-expression-59452236`, `invalid-input-not-a-latex-equation`, etc.), unhook any links to them, and recalibrate the formula count floor in `latest.json`.
2. **Repair the ~95 Prose-Bleed, MathML & Control-Char Corrupted Formulas**:
   * For records that represent real physical concepts (and already contain their true LaTeX equation inside their own `conceptual_definition` or `interpretation`, or have obvious `\partial` $\to$ ` tial` / `\textit` $\to$ `extit` corruption), extract and restore their canonical LaTeX `equation`, re-sync `formulas_latex_index.json` and `formulas_hash_registry.json`, and verify every single repaired equation before committing.
3. **Detach the 38 Bare Numbers / Constants from Fake Physics Parents**:
   * Mark standalone constants/conversion factors (`derivation_type: "DEFINITION"`, `parent_formula_id: null`) so `$10^2$` or `$10^{-15}$` is never listed as a "Derived Equation" under a physics law.
4. **Add a Permanent Equation Validity Gate to `integrity_shield.py` & `tests/`**:
   * Add a strict test that fails if **any** formula in the 256 shards has:
     * Raw MathML tags (`xmlns`, `msub`, `mrow`, `mathvariant`)
     * Control-character corruption (` tial`, `extit{`, `\f`)
     * Unwrapped English prose sentences ($\ge 2$ English words outside `\text{}` / `\mathrm{}`)
     * Empty or `\text{N/A}` equations.

---

## 4. Complete Enumerated Audit Ledger (120 Flagged Records)

*(Note: Items #6 `bayesian-anthropic-selection-e111b3d4`, #48 `humeans-philosophy-identity-c78f27f8`, #111 `antisymmetry-induced-vanishing-quantity-9119b5bc`, and #114 `dimensional-formula-9e2c3624` are valid equations that simply used unwrapped words like `P(Theory | Life)` or `[Energy]` instead of `\text{Theory}` / `\text{Energy}`; the remaining 116 items are genuine corruptions.)*

```text
 1. ID:       classical-velocity-limit-f2d70293 (app/config/content/formulas/05/shard_05.json)
    Title:    Non-Relativistic Velocity Limit Condition
    Eq:       "v \\to 0\n)', the relativistic effects become negligible, and the object's behavior is well-described by classical Newtonian mechanics, where velocity can increase indefinitely. As '"
    Reasons:  prose_bleed(['relativistic', 'effects', 'become', 'negligible', 'object'])
    SubRefs:  [] | Children: 1

 2. ID:       first-generation-quark-components-3f9640ac (app/config/content/formulas/06/shard_06.json)
    Title:    First Generation Left-Handed Quark Doublet
    Eq:       ') and the down quark ('
    Reasons:  prose_bleed(['down', 'quark'])
    SubRefs:  [] | Children: 0

 3. ID:       high-temperature-spontaneity-condition-28429b91 (app/config/content/formulas/07/shard_07.json)
    Title:    High Temperature Spontaneity Condition
    Eq:       ', indicating that at very high temperatures, the spontaneity is primarily governed by the entropy change (processes that increase entropy,'
    Reasons:  prose_bleed(['indicating', 'that', 'very', 'high', 'temperatures'])
    SubRefs:  [] | Children: 1

 4. ID:       lane-emden-polytropic-solution-89701ee5 (app/config/content/formulas/09/shard_09.json)
    Title:    Dimensionless Density Profile for a Polytropic Sphere
    Eq:       ', the solution'
    Reasons:  pure_text(['solution'])
    SubRefs:  [] | Children: 0

 5. ID:       quantum-number-definition-55238a7a (app/config/content/formulas/0a/shard_0a.json)
    Title:    Definition of a Discrete Quantum Number
    Eq:       'is an integer, known as the quantum number, which labels the specific allowed quantum state for that degree of freedom.'
    Reasons:  prose_bleed(['integer', 'known', 'quantum', 'number', 'which'])
    SubRefs:  [] | Children: 5

 6. ID:       bayesian-anthropic-selection-e111b3d4 (app/config/content/formulas/0d/shard_0d.json)
    Title:    Bayesian Anthropic Selection Principle
    Eq:       'P(Theory | Life) \\propto P(Life | Theory) P(Theory)'
    Reasons:  prose_bleed(['Theory', 'Life', 'Life', 'Theory', 'Theory'])
    SubRefs:  ['philosophy-of-physics.json'] | Children: 0

 7. ID:       asymptotic-zero-density-condition-cd6a02d3 (app/config/content/formulas/0d/shard_0d.json)
    Title:    Asymptotic Zero Density Condition
    Eq:       ", the density approaches zero, which is not characteristic of a 'spike'. As"
    Reasons:  prose_bleed(['density', 'approaches', 'zero', 'which', 'characteristic'])
    SubRefs:  [] | Children: 0

 8. ID:       quantum-expectation-of-higgs-field-in-vacuum-cccbdb4c (app/config/content/formulas/10/shard_10.json)
    Title:    Vacuum Expectation Value of the Higgs Field Operator
    Eq:       'is the vacuum expectation value of the Higgs field. The notation \\f0 | Θ(x) | 0'
    Reasons:  prose_bleed(['vacuum', 'expectation', 'value', 'Higgs', 'field'])
    SubRefs:  [] | Children: 0

 9. ID:       general-spatial-translation-d7a18a54 (app/config/content/formulas/13/shard_13.json)
    Title:    General Spatial Translation of a System of Particles
    Eq:       '/math/math'
    Reasons:  prose_bleed(['math', 'math'])
    SubRefs:  [] | Children: 0

10. ID:       uninterpretable-mathematical-fragment-9276d06a (app/config/content/formulas/18/shard_18.json)
    Title:    Syntactically Invalid Mathematical String
    Eq:       '\\text{Unrecoverable Fragment}'
    Reasons:  empty_or_NA, invalid_title
    SubRefs:  [] | Children: 0

11. ID:       perpendicular-magnetic-field-component-in-region-1-b82c9cad (app/config/content/formulas/20/shard_20.json)
    Title:    Perpendicular Component of Magnetic Field in Region 1
    Eq:       '/mo/mrow/msub/math'
    Reasons:  raw_mathml_tag, prose_bleed(['mrow', 'msub', 'math'])
    SubRefs:  [] | Children: 0

12. ID:       generic-mathematical-identifier-39b8b9bb (app/config/content/formulas/21/shard_21.json)
    Title:    Symbolic Representation of a Physical Quantity
    Eq:       'math xmlns="http://www.w3.org/1998/Math/MathML"mi'
    Reasons:  raw_mathml_tag, prose_bleed(['math', 'xmlns', 'http', 'Math', 'MathML'])
    SubRefs:  [] | Children: 1

13. ID:       work-done-by-internal-forces-symbolic-fb5aad5c (app/config/content/formulas/24/shard_24.json)
    Title:    Total Work Done by Internal Forces
    Eq:       'W_{int} = ∑_i\\delta \\int ℇ_i^{int} • d℃_i \n describes the total work done by internal forces within a system.'
    Reasons:  prose_bleed(['describes', 'total', 'work', 'done', 'internal'])
    SubRefs:  [] | Children: 0

14. ID:       magnetic-field-normal-component-definition-84dc25cc (app/config/content/formulas/25/shard_25.json)
    Title:    Definition of the Normal Component of the Magnetic Field
    Eq:       '/momsubmi'
    Reasons:  raw_mathml_tag
    SubRefs:  [] | Children: 0

15. ID:       divergence-as-net-outflow-29d7af54 (app/config/content/formulas/27/shard_27.json)
    Title:    Divergence as the Source of Net Outflow for a Conserved Quantity (Continuity Equation)
    Eq:       '), there must be a corresponding net outflow of the quantity from that point (e.g.,'
    Reasons:  prose_bleed(['there', 'must', 'corresponding', 'outflow', 'quantity'])
    SubRefs:  [] | Children: 0

16. ID:       zero-real-part-condition-resigma-0-4d702e41 (app/config/content/formulas/27/shard_27.json)
    Title:    Marginal Stability Condition: Zero Real Part of Complex Frequency
    Eq:       ', the response is typically oscillatory and neither grows nor decays, representing marginal stability. The imaginary part,'
    Reasons:  prose_bleed(['response', 'typically', 'oscillatory', 'neither', 'grows'])
    SubRefs:  [] | Children: 1

17. ID:       relativistic-speed-limit-condition-c500ee04 (app/config/content/formulas/29/shard_29.json)
    Title:    Ultra-Relativistic Limit Condition: Velocity Approaching c
    Eq:       'approaches the speed of light'
    Reasons:  prose_bleed(['approaches', 'speed', 'light'])
    SubRefs:  [] | Children: 0

18. ID:       conditions-for-meaningful-theoretical-output-and-completeness-bca078f4 (app/config/content/formulas/2a/shard_2a.json)
    Title:    Conditions for Meaningful Theoretical Output
    Eq:       'might produce trivial, undefined, or default outputs. For instance, inputting data points completely irrelevant to a gravitational theory would yield no meaningful gravitational output. 2. Completeness of'
    Reasons:  prose_bleed(['might', 'produce', 'trivial', 'undefined', 'default'])
    SubRefs:  [] | Children: 0

19. ID:       quantum-state-normalization-factor-16c4879a (app/config/content/formulas/2b/shard_2b.json)
    Title:    Normalization Constant for an Equal Superposition of Two Orthogonal States
    Eq:       '. The factor'
    Reasons:  pure_text(['factor'])
    SubRefs:  [] | Children: 0

20. ID:       natural-angular-frequency-definition-4bd80847 (app/config/content/formulas/2d/shard_2d.json)
    Title:    Definition of Natural Angular Frequency
    Eq:       '\\omega_0 = "): The concept of natural frequency'
    Reasons:  prose_bleed(['concept', 'natural', 'frequency'])
    SubRefs:  [] | Children: 1

21. ID:       velocity-variable-definition-94f08a84 (app/config/content/formulas/2e/shard_2e.json)
    Title:    Instantaneous Velocity
    Eq:       "v\n)' represents the velocity of an object, typically measured in meters per second (m/s). '"
    Reasons:  prose_bleed(['represents', 'velocity', 'object', 'typically', 'measured'])
    SubRefs:  [] | Children: 0

22. ID:       four-vector-potential-gauge-transformation-term-139a1e78 (app/config/content/formulas/30/shard_30.json)
    Title:    Gauge Transformation of the Electromagnetic Four-Potential
    Eq:       ') are the components of the magnetic vector potential. The transformation involves subtracting the four-gradient of a scalar function'
    Reasons:  prose_bleed(['components', 'magnetic', 'vector', 'potential', 'transformation'])
    SubRefs:  [] | Children: 1

23. ID:       probability-density-of-unnormalized-wavefunction-ad0b808e (app/config/content/formulas/35/shard_35.json)
    Title:    Unnormalized Position-Space Probability Density
    Eq:       'inline-formula'
    Reasons:  prose_bleed(['inline', 'formula'])
    SubRefs:  [] | Children: 0

24. ID:       definition-of-the-speed-of-light-c84d62f2 (app/config/content/formulas/35/shard_35.json)
    Title:    Exact SI Definition of the Speed of Light in Vacuum
    Eq:       ', the speed of light, and for'
    Reasons:  prose_bleed(['speed', 'light'])
    SubRefs:  [] | Children: 0

25. ID:       the-coupling-constant-de43e36c (app/config/content/formulas/3d/shard_3d.json)
    Title:    Coupling Constant (Interaction Strength)
    Eq:       ', the coupling'
    Reasons:  pure_text(['coupling'])
    SubRefs:  [] | Children: 0

26. ID:       natural-angular-frequency-of-mass-spring-system-f6243ac3 (app/config/content/formulas/3f/shard_3f.json)
    Title:    Natural Angular Frequency of an Undamped Mass-Spring System
    Eq:       'arises from the inherent properties of the system, typically related to its restoring force and inertia. For a simple harmonic oscillator, like a mass-spring system, the natural frequency is determined by the mass'
    Reasons:  prose_bleed(['arises', 'from', 'inherent', 'properties', 'system'])
    SubRefs:  [] | Children: 0

27. ID:       angular-frequency-definition-60aa52f0 (app/config/content/formulas/43/shard_43.json)
    Title:    Definition of Instantaneous Angular Frequency
    Eq:       'math xmlns="http://www.w3.org/1998/Math/MathML"'
    Reasons:  raw_mathml_tag, prose_bleed(['math', 'xmlns', 'http', 'Math', 'MathML'])
    SubRefs:  [] | Children: 0

28. ID:       negative-mass-squared-term-b82ef8bd (app/config/content/formulas/45/shard_45.json)
    Title:    Negative Mass-Squared Term in Scalar Field Theory
    Eq:       ', this term would make'
    Reasons:  prose_bleed(['this', 'term', 'would', 'make'])
    SubRefs:  [] | Children: 0

29. ID:       invalid-mathematical-equation-placeholder-6cea8024 (app/config/content/formulas/46/shard_46.json)
    Title:    Non-Mathematical or Syntactically Invalid String
    Eq:       ''
    Reasons:  empty_or_NA, invalid_title
    SubRefs:  [] | Children: 0

30. ID:       product-of-vacuum-permeability-and-permittivity-ed939d96 (app/config/content/formulas/47/shard_47.json)
    Title:    Product of Vacuum Permeability and Permittivity
    Eq:       '/annotation/semantics/math'
    Reasons:  prose_bleed(['annotation', 'semantics', 'math'])
    SubRefs:  [] | Children: 0

31. ID:       flat-spacetime-connection-coefficient-limit-80bede1b (app/config/content/formulas/47/shard_47.json)
    Title:    Vanishing Connection Coefficients in Flat Spacetime
    Eq:       'states that as spacetime approaches flatness (i.e., it becomes Euclidean or Minkowskian), these connection coefficients tend to zero. This vanishing implies that the components of the metric tensor'
    Reasons:  prose_bleed(['states', 'that', 'spacetime', 'approaches', 'flatness'])
    SubRefs:  [] | Children: 0

32. ID:       condition-for-non-spontaneous-process-9ed5cc62 (app/config/content/formulas/47/shard_47.json)
    Title:    Condition for a Non-Spontaneous Process at Constant Temperature and Pressure
    Eq:       'is never spontaneous. For cases where'
    Reasons:  prose_bleed(['never', 'spontaneous', 'cases', 'where'])
    SubRefs:  [] | Children: 0

33. ID:       force-vector-in-classical-mechanics-8f1919d1 (app/config/content/formulas/48/shard_48.json)
    Title:    Force Vector in Classical Mechanics
    Eq:       'item\\mathbf{F}\n/item/itemize'
    Reasons:  prose_bleed(['item', 'item', 'itemize'])
    SubRefs:  [] | Children: 0

34. ID:       higgs-vacuum-expectation-value-80bcf294 (app/config/content/formulas/48/shard_48.json)
    Title:    Condition for Electroweak Symmetry Breaking: Non-Zero Higgs VEV
    Eq:       '. The vacuum state is the state of lowest energy. The fact that this expectation value is non-zero is crucial. If it were zero, the Higgs mechanism would not operate, and all fundamental particles would be massless, contrary to observation. The value \\f'
    Reasons:  prose_bleed(['vacuum', 'state', 'state', 'lowest', 'energy'])
    SubRefs:  [] | Children: 0

35. ID:       spacelike-interval-condition-14fc4677 (app/config/content/formulas/49/shard_49.json)
    Title:    Condition for a Spacelike Spacetime Interval
    Eq:       '), implying a connection faster than light, which is causally impossible for light or any physical particle. Conversely, if'
    Reasons:  prose_bleed(['implying', 'connection', 'faster', 'than', 'light'])
    SubRefs:  [] | Children: 0

36. ID:       inverse-metric-tensor-definition-40d2210b (app/config/content/formulas/4b/shard_4b.json)
    Title:    Definition of the Inverse Metric Tensor
    Eq:       'is the inverse metric tensor and'
    Reasons:  prose_bleed(['inverse', 'metric', 'tensor'])
    SubRefs:  [] | Children: 0

37. ID:       spacetime-coordinate-e2d4f300 (app/config/content/formulas/4e/shard_4e.json)
    Title:    Spacetime Coordinate as an Integration Variable in QFT
    Eq:       '\\text{x}\n at a point. This process is coordinate-invariant because the integral is over spacetime, and the test function'
    Reasons:  prose_bleed(['point', 'This', 'process', 'coordinate', 'invariant'])
    SubRefs:  [] | Children: 0

38. ID:       inverse-coupling-scaled-gauge-term-ed436c9a (app/config/content/formulas/50/shard_50.json)
    Title:    Inverse Coupling Scaled Gauge Transformation Term
    Eq:       ', scaled by the inverse of a coupling constant'
    Reasons:  prose_bleed(['scaled', 'inverse', 'coupling', 'constant'])
    SubRefs:  [] | Children: 0

39. ID:       quantization-condition-for-phase-space-area-d83bda13 (app/config/content/formulas/51/shard_51.json)
    Title:    Bohr-Sommerfeld Quantization Condition
    Eq:       '. The right-hand side of the equation dictates that this phase space area must be quantized.'
    Reasons:  prose_bleed(['right', 'hand', 'side', 'equation', 'dictates'])
    SubRefs:  [] | Children: 0

40. ID:       coordinate-time-definition-ded28a86 (app/config/content/formulas/51/shard_51.json)
    Title:    Definition of Coordinate Time from the Temporal Spacetime Coordinate
    Eq:       't)\\n is coordinate time. The parameter'
    Reasons:  prose_bleed(['coordinate', 'time', 'parameter'])
    SubRefs:  [] | Children: 0

41. ID:       positive-real-part-condition-dfa383ee (app/config/content/formulas/52/shard_52.json)
    Title:    Condition for Dynamical Instability
    Eq:       '), indicating stability. If'
    Reasons:  prose_bleed(['indicating', 'stability'])
    SubRefs:  [] | Children: 0

42. ID:       angular-frequency-from-complex-frequencys-imaginary-part-d752efaf (app/config/content/formulas/55/shard_55.json)
    Title:    Angular Frequency as the Imaginary Part of Complex Frequency
    Eq:       ', corresponds to the angular frequency of oscillation associated with the mode. Therefore, the condition'
    Reasons:  prose_bleed(['corresponds', 'angular', 'frequency', 'oscillation', 'associated'])
    SubRefs:  [] | Children: 0

43. ID:       test-function-smoothing-effect-05570576 (app/config/content/formulas/56/shard_56.json)
    Title:    Smeared Field Operator and the Mitigation of Singularities
    Eq:       'effectively "smoothes out" the potentially singular nature of the field operator'
    Reasons:  prose_bleed(['effectively', 'smoothes', 'potentially', 'singular', 'nature'])
    SubRefs:  [] | Children: 0

44. ID:       physical-cold-dark-matter-density-parameter-f8d0896d (app/config/content/formulas/57/shard_57.json)
    Title:    Physical Cold Dark Matter Density Parameter
    Eq:       'Ω_c h^2\n\n effectively removes the dependency on the absolute value of the Hubble constant \n\nH_0'
    Reasons:  prose_bleed(['effectively', 'removes', 'dependency', 'absolute', 'value'])
    SubRefs:  [] | Children: 0

45. ID:       exclusion-of-space-like-intervals-823ad0b2 (app/config/content/formulas/57/shard_57.json)
    Title:    Condition for a Space-like Interval
    Eq:       '(space-like intervals) are excluded by the condition'
    Reasons:  prose_bleed(['space', 'like', 'intervals', 'excluded', 'condition'])
    SubRefs:  [] | Children: 0

46. ID:       invalid-relation-four-momentum-squared-and-momentum-component-d9144d58 (app/config/content/formulas/5b/shard_5b.json)
    Title:    Invalid Equality: Four-Momentum Norm Squared and a Spatial Momentum Component
    Eq:       'P^2 = p_y'
    Reasons:  invalid_title
    SubRefs:  [] | Children: 0

47. ID:       path-integral-phase-exponent-771e8fc3 (app/config/content/formulas/5d/shard_5d.json)
    Title:    Action Phase Exponent in the Feynman Path Integral
    Eq:       '. The term'
    Reasons:  pure_text(['term'])
    SubRefs:  [] | Children: 0

48. ID:       humeans-philosophy-identity-c78f27f8 (app/config/content/formulas/60/shard_60.json)
    Title:    Custom Physical Relation
    Eq:       '\\mathcal{L} = \\mathcal{T} + \\mathcal{S} \\implies \\text{Max}(Strength) \\quad \\text{and} \\quad \\text{Max}(Simplicity)'
    Reasons:  prose_bleed(['Strength', 'Simplicity'])
    SubRefs:  [] | Children: 0

49. ID:       qcd-beta-function-running-coupling-9dbb26ee (app/config/content/formulas/61/shard_61.json)
    Title:    QCD Beta Function and the Running of the Strong Coupling Constant
    Eq:       'tends to increase, leading to phenomena like infrared slavery and confinement in QCD. If'
    Reasons:  prose_bleed(['tends', 'increase', 'leading', 'phenomena', 'like'])
    SubRefs:  [] | Children: 0

50. ID:       infinite-limit-concept-e5b596df (app/config/content/formulas/62/shard_62.json)
    Title:    Infinite Limit Concept
    Eq:       'approaches infinity ('
    Reasons:  prose_bleed(['approaches', 'infinity'])
    SubRefs:  [] | Children: 1

51. ID:       mass-energy-equivalence-principle-90b8b3fd (app/config/content/formulas/62/shard_62.json)
    Title:    Mass-Energy Equivalence (Rest Frame)
    Eq:       "(Gigaelectronvolts) is the experimentally determined magnitude of this VEV. The unit of GeV is a unit of energy, and in the context of mass, it's related by Einstein's famous equation \\f"
    Reasons:  prose_bleed(['Gigaelectronvolts', 'experimentally', 'determined', 'magnitude', 'this'])
    SubRefs:  [] | Children: 0

52. ID:       notational-definition-of-a-generic-operator-0900cd54 (app/config/content/formulas/63/shard_63.json)
    Title:    Notational Convention for a Generic Quantum Operator
    Eq:       '\\text{x}\n signifies the operator'
    Reasons:  prose_bleed(['signifies', 'operator'])
    SubRefs:  [] | Children: 1

53. ID:       relativistic-velocity-limit-38b5a890 (app/config/content/formulas/66/shard_66.json)
    Title:    Relativistic Velocity Limit for Massive Particles
    Eq:       "o)' signifies a fundamental limit in Einstein's theory of special relativity. It states that the velocity '"
    Reasons:  prose_bleed(['signifies', 'fundamental', 'limit', 'Einstein', 'theory'])
    SubRefs:  [] | Children: 0

54. ID:       limit-of-mass-ratio-c5592656 (app/config/content/formulas/67/shard_67.json)
    Title:    Asymptotic Limit of a Finite Mass to Total Mass Ratio
    Eq:       'extit{M}) approaches'
    Reasons:  prose_bleed(['extit', 'approaches'])
    SubRefs:  [] | Children: 0

55. ID:       comoving-dark-matter-density-proportionality-9479a888 (app/config/content/formulas/67/shard_67.json)
    Title:    Proportionality of Physical Dark Matter Density to the Comoving Density Parameter
    Eq:       'Ω_c h^2\n\n is directly proportional to \n\nρ_c'
    Reasons:  prose_bleed(['directly', 'proportional'])
    SubRefs:  [] | Children: 0

56. ID:       phantom-energy-condition-w-1-f46e29d5 (app/config/content/formulas/6f/shard_6f.json)
    Title:    Phantom Energy Condition
    Eq:       ", often referred to as 'phantom energy,' the energy density of dark energy would increase as the universe expands, leading to an even faster acceleration and potentially a 'Big Rip' scenario where all bound structures are eventually torn apart. If"
    Reasons:  prose_bleed(['often', 'referred', 'phantom', 'energy', 'energy'])
    SubRefs:  [] | Children: 0

57. ID:       the-quantum-phase-factor-6b401c63 (app/config/content/formulas/70/shard_70.json)
    Title:    Quantum Path Integral Phase Factor
    Eq:       '. The quantity'
    Reasons:  pure_text(['quantity'])
    SubRefs:  [] | Children: 0

58. ID:       local-field-operator-test-function-product-aa2bb896 (app/config/content/formulas/70/shard_70.json)
    Title:    Local Product of a Quantum Field Operator and a Test Function
    Eq:       '\\text{x}\n being multiplied by the scalar value of the test function'
    Reasons:  prose_bleed(['being', 'multiplied', 'scalar', 'value', 'test'])
    SubRefs:  [] | Children: 0

59. ID:       four-acceleration-tensor-component-0a54f541 (app/config/content/formulas/75/shard_75.json)
    Title:    Four-Acceleration Vector Component
    Eq:       "\\frac{d^2 x^\\mu}{d\\tau^2})\\n represents the four-acceleration of the particle. The statement that this four-acceleration is zero signifies that the particle is not accelerating in the LIF. This implies that the particle's four-velocity,"
    Reasons:  prose_bleed(['represents', 'four', 'acceleration', 'particle', 'statement'])
    SubRefs:  [] | Children: 0

60. ID:       test-function-definition-in-qft-eefbc4e9 (app/config/content/formulas/77/shard_77.json)
    Title:    Definition of a Smeared Field Operator in Quantum Field Theory
    Eq:       'is a test function, a smooth, rapidly decreasing function of spacetime, which serves as a "smearing" function. The integral'
    Reasons:  prose_bleed(['test', 'function', 'smooth', 'rapidly', 'decreasing'])
    SubRefs:  [] | Children: 0

61. ID:       exponential-decay-factor-4e25d2b4 (app/config/content/formulas/78/shard_78.json)
    Title:    Exponential Decay Factor (Temporal)
    Eq:       ', the response decays exponentially (e.g., proportional to'
    Reasons:  prose_bleed(['response', 'decays', 'exponentially', 'proportional'])
    SubRefs:  [] | Children: 0

62. ID:       gauge-transformation-term-for-vector-potential-035a195f (app/config/content/formulas/7d/shard_7d.json)
    Title:    Gauge Freedom Term for the Electromagnetic Four-Potential
    Eq:       ', yielding a four-vector. This transformation leaves the electromagnetic field tensor,'
    Reasons:  prose_bleed(['yielding', 'four', 'vector', 'This', 'transformation'])
    SubRefs:  [] | Children: 0

63. ID:       spacetime-coordinate-index-fb63ad71 (app/config/content/formulas/7e/shard_7e.json)
    Title:    Component of the Contravariant Spacetime Position Four-Vector
    Eq:       '-th coordinate. The formula'
    Reasons:  prose_bleed(['coordinate', 'formula'])
    SubRefs:  [] | Children: 0

64. ID:       timelike-spacetime-interval-condition-89897e82 (app/config/content/formulas/82/shard_82.json)
    Title:    Condition for a Causal (Timelike or Lightlike) Spacetime Interval
    Eq:       'in this formula. In such cases,'
    Reasons:  prose_bleed(['this', 'formula', 'such', 'cases'])
    SubRefs:  [] | Children: 0

65. ID:       canonical-momentum-definition (app/config/content/formulas/84/shard_84.json)
    Title:    Canonical Momentum Definition
    Eq:       'p = \\frac{ tial L}{ tial v} = mv'
    Reasons:  prose_bleed(['tial', 'tial'])
    SubRefs:  [] | Children: 0

66. ID:       time-like-spacetime-interval-condition-bfe033f8 (app/config/content/formulas/85/shard_85.json)
    Title:    Condition for a Timelike Spacetime Interval
    Eq:       ", the interval is 'time-like'. These paths represent the trajectories of massive particles or observers, and they lie *inside* the light cone. If"
    Reasons:  prose_bleed(['interval', 'time', 'like', 'These', 'paths'])
    SubRefs:  [] | Children: 0

67. ID:       four-dimensional-spacetime-volume-element-8570641e (app/config/content/formulas/85/shard_85.json)
    Title:    Infinitesimal Coordinate Volume Element in Four-Dimensional Spacetime
    Eq:       'is a four-dimensional spacetime integral over all of spacetime. The product'
    Reasons:  prose_bleed(['four', 'dimensional', 'spacetime', 'integral', 'over'])
    SubRefs:  [] | Children: 0

68. ID:       proper-time-vs-coordinate-time-inequality-479042b5 (app/config/content/formulas/89/shard_89.json)
    Title:    Relativistic Inequality of Proper Time and Coordinate Time
    Eq:       ', meaning the proper time interval is always shorter than or equal to the coordinate time interval. This phenomenon is known as time dilation. The maximum value of'
    Reasons:  prose_bleed(['meaning', 'proper', 'time', 'interval', 'always'])
    SubRefs:  [] | Children: 0

69. ID:       polytropic-stellar-surface-condition-2941c34d (app/config/content/formulas/8a/shard_8a.json)
    Title:    Polytropic Stellar Surface Condition: Vanishing Dimensionless Temperature/Density
    Eq:       'typically reaches'
    Reasons:  prose_bleed(['typically', 'reaches'])
    SubRefs:  [] | Children: 0

70. ID:       canonical-momentum-density-four-vector-field-theory (app/config/content/formulas/90/shard_90.json)
    Title:    Canonical Momentum Density Four-vector (Field Theory)
    Eq:       '\\pi^\\mu \\equiv \\frac{ tial \\mathcal{L}}{ tial ( tial_\\mu \\phi)}'
    Reasons:  prose_bleed(['tial', 'tial'])
    SubRefs:  [] | Children: 0

71. ID:       electric-scalar-potential-d56b062b (app/config/content/formulas/94/shard_94.json)
    Title:    Electric Scalar Potential
    Eq:       'being the electric scalar potential and'
    Reasons:  prose_bleed(['being', 'electric', 'scalar', 'potential'])
    SubRefs:  [] | Children: 0

72. ID:       quadratic-term-of-scalar-potential-aa1dbb0c (app/config/content/formulas/95/shard_95.json)
    Title:    Quadratic Term of a Scalar Potential Driving Spontaneous Symmetry Breaking
    Eq:       'term, with'
    Reasons:  prose_bleed(['term', 'with'])
    SubRefs:  [] | Children: 0

73. ID:       polytropic-sphere-boundary-condition-fa573c16 (app/config/content/formulas/97/shard_97.json)
    Title:    Polytropic Sphere Surface Boundary Condition
    Eq:       ". This corresponds to the finite radius of the polytropic sphere (e.g., a star's surface) where the density vanishes. For"
    Reasons:  prose_bleed(['This', 'corresponds', 'finite', 'radius', 'polytropic'])
    SubRefs:  [] | Children: 0

74. ID:       geodesic-equation-in-curved-spacetime-ed054392 (app/config/content/formulas/9c/shard_9c.json)
    Title:    Geodesic Equation in Curved Spacetime
    Eq:       "\\frac{d^2 x^\\mu}{d\\tau^2} + \\Gamma^\\mu_{\\alpha\\beta} \\frac{d x^\\alpha}{d\\tau} \\frac{d x^\\beta}{d\\tau} = 0)\\n, must be used. The 'boundary' of the LIF is defined by where tidal forces become measurable, or equivalently, where the second derivatives of the metric tensor become significant. The equation also implicitly assumes the particle is massive, such that"
    Reasons:  prose_bleed(['must', 'used', 'boundary', 'defined', 'where'])
    SubRefs:  [] | Children: 1

75. ID:       modified-dynamics-d40de07f (app/config/content/formulas/9f/shard_9f.json)
    Title:    Modified Hamiltonian Constraint in Dense Media
    Eq:       'The Hamiltonian constraint is modified at high densities.'
    Reasons:  prose_bleed(['Hamiltonian', 'constraint', 'modified', 'high', 'densities'])
    SubRefs:  ['theoretical-physics.json'] | Children: 0

76. ID:       spacetime-four-vector-coordinate-e34acad8 (app/config/content/formulas/9f/shard_9f.json)
    Title:    Spacetime Four-Vector Coordinate
    Eq:       '\\text{x}\n. Conversely, if the test function'
    Reasons:  prose_bleed(['Conversely', 'test', 'function'])
    SubRefs:  [] | Children: 1

77. ID:       mass-of-the-i-th-particle-4dc77bc3 (app/config/content/formulas/a2/shard_a2.json)
    Title:    Mass of the i-th Particle
    Eq:       'math xmlns="http://www.w3.org/1998/Math/MathML"msubmi'
    Reasons:  raw_mathml_tag, prose_bleed(['math', 'xmlns', 'http', 'Math', 'MathML'])
    SubRefs:  [] | Children: 0

78. ID:       generalized-momentum-definition-5f8f17a7 (app/config/content/formulas/a3/shard_a3.json)
    Title:    Generalized Momentum Definition
    Eq:       'is the generalized momentum conjugate to the generalized coordinate'
    Reasons:  prose_bleed(['generalized', 'momentum', 'conjugate', 'generalized', 'coordinate'])
    SubRefs:  [] | Children: 0

79. ID:       gauge-invariance-of-electromagnetic-fields-514e74fd (app/config/content/formulas/a4/shard_a4.json)
    Title:    Gauge Invariance of Electromagnetic Fields
    Eq:       ', invariant, meaning that the physically observable electric and magnetic fields, derived from'
    Reasons:  prose_bleed(['invariant', 'meaning', 'that', 'physically', 'observable'])
    SubRefs:  [] | Children: 0

80. ID:       pure-quantum-state-ket-for-subsystem-a-97ca62ea (app/config/content/formulas/a6/shard_a6.json)
    Title:    Pure Quantum State Ket for Subsystem A
    Eq:       'Ψ^A|. If both ρ_i^A and ρ_i^B are density matrices representing pure states |Ψ_i^A'
    Reasons:  prose_bleed(['both', 'density', 'matrices', 'representing', 'pure'])
    SubRefs:  [] | Children: 0

81. ID:       timelike-spacetime-interval-condition-5db0184a (app/config/content/formulas/a6/shard_a6.json)
    Title:    Timelike Spacetime Interval Condition
    Eq:       'remains finite, the interval becomes timelike ('
    Reasons:  prose_bleed(['remains', 'finite', 'interval', 'becomes', 'timelike'])
    SubRefs:  [] | Children: 0

82. ID:       operational-electric-field-vector-8803b4d9 (app/config/content/formulas/a7/shard_a7.json)
    Title:    Operational Electric Field Vector
    Eq:       'math xmlns="http://www.w3.org/1998/Math/MathML"msubmi mathvariant="bold"'
    Reasons:  raw_mathml_tag, prose_bleed(['math', 'xmlns', 'http', 'Math', 'MathML'])
    SubRefs:  [] | Children: 0

83. ID:       canonical-phase-plane-coordinates-5310ee03 (app/config/content/formulas/a8/shard_a8.json)
    Title:    Canonical Phase Plane Coordinates
    Eq:       '(q_i, p_i))\\ phase plane. The variable'
    Reasons:  prose_bleed(['phase', 'plane', 'variable'])
    SubRefs:  [] | Children: 0

84. ID:       mass-energy-equivalence-for-unit-conversion-7b8d705c (app/config/content/formulas/a9/shard_a9.json)
    Title:    Mass-Energy Relation for Mass and Energy Unit Conversion
    Eq:       '. Therefore, the Higgs VEV is often also expressed in units of mass (e.g., kg) by implicitly setting \\f'
    Reasons:  prose_bleed(['Therefore', 'Higgs', 'often', 'also', 'expressed'])
    SubRefs:  [] | Children: 0

85. ID:       adiabatic-index-definition-0dadeedb (app/config/content/formulas/a9/shard_a9.json)
    Title:    Adiabatic Index Definition
    Eq:       '")), is a dimensionless quantity representing the ratio of specific heat capacities of a gas at constant pressure ('
    Reasons:  prose_bleed(['dimensionless', 'quantity', 'representing', 'ratio', 'specific'])
    SubRefs:  [] | Children: 0

86. ID:       definition-operator-symbol-94ef1775 (app/config/content/formulas/ad/shard_ad.json)
    Title:    Mathematical Definition Operator
    Eq:       'is defined as'
    Reasons:  pure_text(['defined'])
    SubRefs:  [] | Children: 0

87. ID:       location-of-stable-minimum-in-mexican-hat-potential-47672d36 (app/config/content/formulas/ad/shard_ad.json)
    Title:    Location of Stable Minimum in Mexican Hat Potential
    Eq:       'a stable minimum. The'
    Reasons:  prose_bleed(['stable', 'minimum'])
    SubRefs:  [] | Children: 0

88. ID:       finite-value-constraint-ee3ea27e (app/config/content/formulas/af/shard_af.json)
    Title:    Finite Value Regularity Constraint
    Eq:       'at a finite value of'
    Reasons:  prose_bleed(['finite', 'value'])
    SubRefs:  [] | Children: 0

89. ID:       operational-electric-field-definition-bfb3804e (app/config/content/formulas/b0/shard_b0.json)
    Title:    Operational Electric Field Definition
    Eq:       '/mi/msub/math'
    Reasons:  raw_mathml_tag, prose_bleed(['msub', 'math'])
    SubRefs:  [] | Children: 1

90. ID:       undefined-mathematical-expression-59452236 (app/config/content/formulas/b4/shard_b4.json)
    Title:    Undefined Mathematical Expression
    Eq:       '\\text{N/A}'
    Reasons:  empty_or_NA, invalid_title
    SubRefs:  [] | Children: 1

91. ID:       total-mass-of-two-particle-system-922d9f5e (app/config/content/formulas/b4/shard_b4.json)
    Title:    Total Mass of a Two-Particle System
    Eq:       'extit{M} = extit{m}_1 +'
    Reasons:  prose_bleed(['extit', 'extit'])
    SubRefs:  [] | Children: 0

92. ID:       invalid-input-not-a-latex-equation (app/config/content/formulas/b4/shard_b4.json)
    Title:    Invalid Input: Not a LaTeX Equation
    Eq:       'b1,b2,b3'
    Reasons:  invalid_title, placeholder_b1b2b3
    SubRefs:  [] | Children: 0

93. ID:       mass-ratio-of-particle-2-to-total-mass-18ff0443 (app/config/content/formulas/b7/shard_b7.json)
    Title:    Mass Ratio of Particle 2 to Total Mass
    Eq:       'extit{m}_2 o extit{M} (meaning extit{m}_1'
    Reasons:  prose_bleed(['extit', 'extit', 'meaning', 'extit'])
    SubRefs:  [] | Children: 1

94. ID:       phantom-energy-and-big-rip-singularity-3c28bc0f (app/config/content/formulas/bb/shard_bb.json)
    Title:    Phantom Energy Density Evolution and Big Rip Singularity
    Eq:       "(phantom energy) suggest even er negative pressure, potentially leading to a 'Big Rip' singularity, while"
    Reasons:  prose_bleed(['phantom', 'energy', 'suggest', 'even', 'negative'])
    SubRefs:  [] | Children: 0

95. ID:       pressure-gradient-force-per-unit-mass-40648a4c (app/config/content/formulas/c1/shard_c1.json)
    Title:    Pressure Gradient Force per Unit Mass
    Eq:       ') and no body forces ('
    Reasons:  prose_bleed(['body', 'forces'])
    SubRefs:  [] | Children: 0

96. ID:       non-zero-test-charge-condition-dc4a462d (app/config/content/formulas/c4/shard_c4.json)
    Title:    Non-Zero Test Charge Condition for Operational Field Probing
    Eq:       'msubmi mathvariant="normal"'
    Reasons:  raw_mathml_tag, prose_bleed(['msubmi', 'mathvariant', 'normal'])
    SubRefs:  [] | Children: 0

97. ID:       lane-emden-infinite-radius-condition-f3caf2ea (app/config/content/formulas/c5/shard_c5.json)
    Title:    Lane-Emden Infinite Radius Condition for Polytropes
    Eq:       ', the solution extends to infinite radius, and for'
    Reasons:  prose_bleed(['solution', 'extends', 'infinite', 'radius'])
    SubRefs:  [] | Children: 0

98. ID:       permeability-of-free-space-constant-2db5274b (app/config/content/formulas/cc/shard_cc.json)
    Title:    Magnetic Permeability of Free Space (Vacuum Permeability)
    Eq:       '/mi/msubmo'
    Reasons:  raw_mathml_tag
    SubRefs:  [] | Children: 0

99. ID:       total-unnormalized-probability-f6861b8b (app/config/content/formulas/d1/shard_d1.json)
    Title:    Total Unnormalized Probability Integral in Position Space
    Eq:       '/inline-formula'
    Reasons:  prose_bleed(['inline', 'formula'])
    SubRefs:  [] | Children: 0

100. ID:      energy-eigenvalue-a69037b6 (app/config/content/formulas/d1/shard_d1.json)
    Title:    Stationary State Energy Eigenvalue Equation
    Eq:       'represents the energy of the'
    Reasons:  prose_bleed(['represents', 'energy'])
    SubRefs:  [] | Children: 0

101. ID:      test-charge-in-electric-field-definition-a4fd1d86 (app/config/content/formulas/d3/shard_d3.json)
    Title:    Operational Definition of the Test Charge
    Eq:       '/mi/msub'
    Reasons:  raw_mathml_tag
    SubRefs:  [] | Children: 0

102. ID:      gauge-invariance-of-field-strength-tensor-d3cb85f3 (app/config/content/formulas/d5/shard_d5.json)
    Title:    Gauge Invariance of the Field Strength Tensor
    Eq:       ', are unaffected by this change in'
    Reasons:  prose_bleed(['unaffected', 'this', 'change'])
    SubRefs:  [] | Children: 0

103. ID:      expectation-value-of-higgs-field-354c55e5 (app/config/content/formulas/d6/shard_d6.json)
    Title:    Quantum Vacuum Expectation Value of the Higgs Field Operator
    Eq:       'signifies the expectation value of the Higgs field operator \\f'
    Reasons:  prose_bleed(['signifies', 'expectation', 'value', 'Higgs', 'field'])
    SubRefs:  [] | Children: 0

104. ID:      quantum-momentum-operator-1d-9a29eb51 (app/config/content/formulas/d8/shard_d8.json)
    Title:    Quantum Momentum Operator in One Dimension (Position Representation)
    Eq:       'and momentum'
    Reasons:  pure_text(['momentum'])
    SubRefs:  [] | Children: 0

105. ID:      infinitesimal-displacement-vector-in-cartesian-coordinates-c17a10c6 (app/config/content/formulas/dc/shard_dc.json)
    Title:    Infinitesimal Displacement Vector in Cartesian Coordinates
    Eq:       'd\\mathbf{r} = dx \\hat{\\mathbf{i}} + dy \\hat{\\mathbf{j}} + dz \\hat{\\mathbf{k}}\n \n directly leads to'
    Reasons:  prose_bleed(['directly', 'leads'])
    SubRefs:  [] | Children: 1

106. ID:      qcd-strong-coupling-constant-26eadb17 (app/config/content/formulas/dc/shard_dc.json)
    Title:    Quantum Chromodynamics Strong Coupling Constant
    Eq:       '(as in Quantum Chromodynamics), the coupling'
    Reasons:  prose_bleed(['Quantum', 'Chromodynamics', 'coupling'])
    SubRefs:  [] | Children: 0

107. ID:      theoretical-instrument-domain-constraint-81deb17f (app/config/content/formulas/e0/shard_e0.json)
    Title:    Domain and Degeneracy Constraints on the Theoretical Instrument Operator
    Eq:       '\\hat{\\mathcal{I}}\\\\, is bounded by the domain of the theory it represents. 1. Degenerate Input: If'
    Reasons:  prose_bleed(['bounded', 'domain', 'theory', 'represents', 'Degenerate'])
    SubRefs:  [] | Children: 0

108. ID:      natural-angular-frequency-of-mass-spring-system-74744acd (app/config/content/formulas/e1/shard_e1.json)
    Title:    Natural Angular Frequency of a Mass-Spring System
    Eq:       'and the spring constant'
    Reasons:  prose_bleed(['spring', 'constant'])
    SubRefs:  [] | Children: 0

109. ID:      definition-of-quantum-vacuum-state-3e3b7d56 (app/config/content/formulas/e2/shard_e2.json)
    Title:    Definition of the Quantum Vacuum State via the Annihilation Operator
    Eq:       'in the vacuum state \\f'
    Reasons:  prose_bleed(['vacuum', 'state'])
    SubRefs:  [] | Children: 0

110. ID:      temperature-dependence-of-spontaneity-43c1f6e2 (app/config/content/formulas/e5/shard_e5.json)
    Title:    Temperature Dependence of Thermodynamic Spontaneity via the Gibbs Free Energy Relation
    Eq:       'have the same sign, spontaneity depends on temperature (e.g.,'
    Reasons:  prose_bleed(['have', 'same', 'sign', 'spontaneity', 'depends'])
    SubRefs:  [] | Children: 0

111. ID:      antisymmetry-induced-vanishing-quantity-9119b5bc (app/config/content/formulas/e6/shard_e6.json)
    Title:    Antisymmetry-Induced Vanishing Quantum State Amplitude
    Eq:       '|Φ_1 Φ_2 \rangle = -|Φ_1 Φ_2 \rangle'
    Reasons:  prose_bleed(['angle', 'angle'])
    SubRefs:  [] | Children: 0

112. ID:      upper-mass-limit-for-white-dwarf-progenitors-95af2c99 (app/config/content/formulas/e6/shard_e6.json)
    Title:    Upper Mass Limit for White Dwarf Progenitors
    Eq:       '), stars are generally classified as intermediate or low-mass stars. These stars evolve through the red giant and asymptotic giant branch phases, eventually forming planetary nebulae and leaving behind a white dwarf remnant without undergoing a core-collapse supernova. For initial masses above the upper limit ('
    Reasons:  prose_bleed(['stars', 'generally', 'classified', 'intermediate', 'mass'])
    SubRefs:  [] | Children: 0

113. ID:      asymptotic-freedom-condition-fb4614ef (app/config/content/formulas/e7/shard_e7.json)
    Title:    Asymptotic Freedom Condition in Non-Abelian Gauge Theory
    Eq:       'approaches zero, leading to the phenomenon of asymptotic freedom, where interactions become very weak at extremely high energies. If'
    Reasons:  prose_bleed(['approaches', 'zero', 'leading', 'phenomenon', 'asymptotic'])
    SubRefs:  [] | Children: 0

114. ID:      dimensional-formula-9e2c3624 (app/config/content/formulas/e9/shard_e9.json)
    Title:    Dimensional Formula of Classical Action and Angular Momentum
    Eq:       '[S] = [Energy] \\cdot [Time] = M L^2 T^{-1}'
    Reasons:  prose_bleed(['Energy', 'Time'])
    SubRefs:  ['theoretical-physics.json'] | Children: 0

115. ID:      good-atmospheric-seeing-value-9ec02104 (app/config/content/formulas/e9/shard_e9.json)
    Title:    Characteristic High-Quality Atmospheric Seeing Angular Size
    Eq:       "0.5''), and under poor conditions, it can be significantly worse (e.g.,"
    Reasons:  prose_bleed(['under', 'poor', 'conditions', 'significantly', 'worse'])
    SubRefs:  [] | Children: 0

116. ID:      partial-derivative-operator-b623c674 (app/config/content/formulas/eb/shard_eb.json)
    Title:    Partial Derivative Operator
    Eq:       'denotes the partial derivative with respect to the'
    Reasons:  prose_bleed(['denotes', 'partial', 'derivative', 'with', 'respect'])
    SubRefs:  [] | Children: 0

117. ID:      asymptotic-term-dominance-principle-704b096b (app/config/content/formulas/ee/shard_ee.json)
    Title:    Asymptotic Term Dominance Principle
    Eq:       'term becomes dominant. Here,'
    Reasons:  prose_bleed(['term', 'becomes', 'dominant', 'Here'])
    SubRefs:  [] | Children: 0

118. ID:      infinitesimal-limit-concept-e6c4ad6a (app/config/content/formulas/f9/shard_f9.json)
    Title:    Infinitesimal Limit Concept
    Eq:       'approaches zero ('
    Reasons:  prose_bleed(['approaches', 'zero'])
    SubRefs:  [] | Children: 0

119. ID:      magnetic-vector-potential-a8566766 (app/config/content/formulas/f9/shard_f9.json)
    Title:    Magnetic Vector Potential
    Eq:       'mi mathvariant="bold"'
    Reasons:  raw_mathml_tag, prose_bleed(['mathvariant', 'bold'])
    SubRefs:  [] | Children: 0

120. ID:      gibbs-free-energy-limiting-behavior-2ab51194 (app/config/content/formulas/fd/shard_fd.json)
    Title:    Gibbs Free Energy Limiting Behavior
    Eq:       ', are favored). This is consistent with the Nernst heat theorem and the Third Law of Thermodynamics. Conversely, in the high-temperature limit ('
    Reasons:  prose_bleed(['favored', 'This', 'consistent', 'with', 'Nernst'])
    SubRefs:  [] | Children: 1
```
