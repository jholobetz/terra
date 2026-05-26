# TF-IDF Signature Audit (2026-05-25)

Diagnoses the quality of `orchestrator.PhysicsOrchestrator.HUB_SIGNATURES` — the dynamically-computed per-hub vocabulary the OPS validator uses to detect "contextual leakage" during graduation. The flag-violations diagnostic flagged signature quality as suspect; this audit confirms it and proposes a one-knob fix.

## Method

Across 412 platinum documents:
1. Tokenize each (title weighted 3×, then content), filter the existing stop-word list, lowercase.
2. Compute document frequency (DF) per token and per-doc TF.
3. Resolve each platinum doc's hub via the parent chain (same algorithm as `_compile_dynamic_signatures:218-237`).
4. Score each token's TF-IDF aggregate per hub; take the top 15 per hub as the signature.
5. **Cross-tabulate** signature words across hubs to find duplicates.
6. **Frequency-tabulate** signature words against corpus prevalence to find background vocabulary.
7. Simulate the same compilation with a DF ceiling filter to preview the fix.

## Headline findings

### 1. Eight words pollute multiple hub signatures

| Word | # hubs containing it | DF | DF % |
|---|---|---|---|
| `energy` | 8 | 378 | 92% |
| `manifold` | 8 | 383 | 93% |
| `vacuum` | 8 | 334 | 81% |
| `requirements` | 6 | 265 | 64% |
| `field` | 3 | 354 | 86% |
| `mass` | 3 | 215 | 52% |
| `vector` | 3 | 220 | 53% |
| `magnetic` | 3 | 83 | 20% |

`energy`, `manifold`, and `vacuum` each appear in **8 of 12** hub signatures while themselves being in **80%+ of all platinum documents**. They are background vocabulary that survived the top-15 cutoff because TF-IDF's IDF term doesn't punish them hard enough at this corpus size — at df = 380, IDF ≈ 0.74; at df = 200, IDF ≈ 1.14. The discrimination is real but not strong enough to push them out.

### 2. 44 of ~180 signature words appear in >40% of platinum docs

That is, roughly **a quarter of all signature vocabulary across all hubs is corpus-background prose**. The worst offenders:

- `physical` — in 94% of docs, sole signature word for `philosophy-of-physics`
- `manifold` — 93%, in 8 signatures
- `energy` — 92%, in 8 signatures
- `through` — 90%, in `fluids-nonlinear` and `mathematical-methods`
- `classical` — 88%, in `quantum-physics` signature
- `space` — 87%, in `classical-mechanics` and `theoretical-physics`
- `field` — 86%, in 3 signatures
- `universe` — 85%, in `philosophy-of-physics` and `thermodynamics`

### 3. Signature quality is worst for philosophy-of-physics

| Hub | Unique words | Shared words | Noisy (df > 40%) |
|---|---|---|---|
| philosophy-of-physics | 6 | 9 | **11** |
| classical-mechanics | 7 | 8 | 9 |
| quantum-physics | 10 | 5 | 8 |
| theoretical-physics | 8 | 7 | 8 |
| thermodynamics-stat-mech | 8 | 7 | 8 |
| astrophysics | 9 | 6 | 7 |
| mathematical-methods | 6 | 9 | 7 |
| standard-model | 11 | 4 | 7 |
| electromagnetism | 10 | 5 | 6 |
| fluids-nonlinear | 7 | 8 | 6 |
| relativity | 15 | 0 | 5 |
| condensed-matter | 9 | 6 | 4 |

**philosophy-of-physics has 11 of 15 signature words in the "noisy" bucket** — meaning its supposed disambiguating vocabulary is mostly corpus-background. This is exactly why it wins 3 of the 4 Tier-1 leakage cases: any platinum content that says "physical", "manifold", "energy", "universe" appears to match philosophy-of-physics, when really it just matches "any physics writing."

**relativity has the cleanest signature** (0 shared, 5 noisy) — fitting since relativity vocabulary (`lorentz`, `metric`, `spacetime`, `proper`, `interval`, `frame`, `events`, `observer`) is genuinely discipline-specific.

## Proposed fix: DF ceiling filter in `_compile_dynamic_signatures`

Add a corpus-prevalence ceiling: words appearing in more than X% of platinum documents are excluded from signature compilation. Standard practice in TF-IDF systems when domain-background vocabulary dominates the corpus.

**Concrete change to `orchestrator.py:246`** (inside the score-accumulation loop):

```python
DF_CEILING = 0.60  # exclude words in >60% of platinum docs as background vocab

for word, count in sub_tf.items():
    if df.get(word, 0) / num_platinum > DF_CEILING:
        continue
    w_tf = count / doc_len
    w_tfidf = w_tf * idf.get(word, 0.0)
    for hub in resolved_hubs:
        hub_word_scores[hub][word] += w_tfidf
```

Three new lines. The threshold could be a class constant for easy tuning.

## Simulation: signatures with 60% DF ceiling

Below is what each signature becomes when high-DF background vocabulary is filtered. **Removed** words were polluting; **added** words are the next-most-disambiguating tokens that moved into the top-15.

### philosophy-of-physics — the biggest improvement
- **Before:** `selectioning, vacuum, manifold, causal, quantum, topology, physical, success, rungs, universe, requirements, ontological, reality, laws, measurement`
- **After:** `selectioning, quantum, topology, success, rungs, requirements, ontological, reality, laws, measurement, theories, specific, ontic, argument, realism`
- Removed: `vacuum, manifold, causal, physical, universe` (all corpus background)
- Added: `theories, specific, ontic, argument, realism` (actual philosophy vocabulary)

### astrophysics
- Removed: `energy, vacuum, manifold`
- Added: `black, ricci, cosmology` (named astrophysics objects/methods)

### standard-model
- Removed: `vacuum, field, manifold, theory`
- Added: `majorana, violation, interaction, left` (actual SM vocabulary)

### theoretical-physics
- Removed: `system, field, space, manifold, energy`
- Added: `quantum, routhian, symmetry, global, equations`

### fluids-nonlinear
- Removed: `vacuum, manifold, limit, energy, through`
- Added: `viscosity, navier, wind, layer, viscous` (textbook fluids vocab)

### condensed-matter
- Removed: `vacuum, manifold, energy`
- Added: `band, majorana, reveals`

### thermodynamics-statistical-mechanics
- Removed: `vacuum, universe, manifold, energy`
- Added: `initial, equilibrium, death, gas`

### relativity — minimal change (already clean)
- Removed: `metric` (df = 71%, just above ceiling)
- Added: `speed`

(Full simulation in `/tmp/sig_simulation.json` if needed for further analysis.)

## Implications for the 3 remaining Tier-1 leakage cases

The Tier-1 leakage cases from the flag-violations diagnostic — `expansion-law`, `crystal-lattice`, `area-law` — all lose to `philosophy-of-physics` in the current validator. With the new philosophy-of-physics signature (`selectioning, quantum, topology, success, rungs, requirements, ontological, reality, laws, measurement, theories, specific, ontic, argument, realism`), none of these words are likely to appear in cosmology/condensed-matter/thermodynamics content the way `physical, manifold, causal, universe` did.

**Predicted outcome of applying the fix:** all 3 Tier-1 leakage cases pass the validator without any content rewrites. That converts 3 nodes from "structural fix required" to "Tier-3 lead-only (prose rewrite)" — the easiest tier.

This is potentially the highest-leverage line-of-code change available on this corpus right now.

## Caveats

1. **Threshold tuning.** I used 60% for the simulation. At 50% the filter removes `mass` (52%) and `vector` (53%) — words that arguably are disambiguating in their proper context. At 70% it leaves `requirements` (64%) and `reveals` (67%) in signatures, which look like template-prose artifacts. **60% looks like the right balance**, but worth verifying after the change by re-running the audit.

2. **Template artifacts still present.** Even at 60% DF, `selectioning`, `rungs`, `requirements`, `reveals` appear in multiple signatures. These look like recurring template phrases ("the requirements for...", "this analysis reveals...", "rungs of the ladder of being"). They're below the DF ceiling because they're not literally everywhere, just somewhere across multiple pillars. **A separate cleanup pass on these template phrases would be a follow-up to the DF-ceiling change.**

3. **No effect on existing platinum nodes.** This change only affects future calls to `_compile_dynamic_signatures`. The signatures are recomputed on every orchestrator init, so the next graduation (or any other pipeline run) picks up the new signatures automatically.

4. **The orchestrator's existing hard-coded fallback signatures** (`HUB_SIGNATURES` at line 1605) are used only when the platinum count is < 5, so they're irrelevant in practice. Worth noting that those static fallback signatures are themselves a sort of "ground truth" and could be compared against the dynamic ones as a sanity check.

## Recommended next step

Implement the 3-line change. It's the cleanest path to resolving 3 of the 3 remaining Tier-1 leakage cases and reduces the false-positive rate of the contextual-leakage check across all future graduations. The blast radius is well-understood — dynamic signatures regenerate on init, no migration needed, and the existing audit machinery (`generate_system_health.py`) can re-verify the corpus state afterward.
