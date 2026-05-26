# Shard/Hub Mismatch Audit (2026-05-25)

For each subtopic, the audit compares which shard it lives in against which hub its parent chain resolves to. Two cases were already known from prior diagnostics (`friedmann-equations`, `expansion-law` in philosophy-of-physics shard but resolving to astrophysics). Scanning the full corpus reveals these were the visible tips of two large classes plus a long tail.

## Headline finding

**100 of 1,527 non-orphan subtopics (6.5%) have a shard that doesn't match their resolved hub.** These split into three categories with very different recommended actions.

## Distribution

| Shard hub → Resolved hub | Count | Action class |
|---|---|---|
| philosophy-of-physics → **astrophysics** | 27 | **Migrate** |
| theoretical-physics → **thermodynamics-stat-mech** | 16 | **Migrate** |
| philosophy-of-physics → quantum-physics+theoretical | 16 | Investigate |
| astrophysics → fluids-nonlinear | 11 | Co-parent |
| astrophysics → thermodynamics-stat-mech | 9 | Co-parent |
| classical-mechanics → theoretical-physics | 7 | Co-parent |
| classical-mechanics → relativity | 3 | **Migrate (metric-tensor cluster)** |
| classical-mechanics → electromagnetism | 3 | Investigate (parent-chain quirk) |
| theoretical-physics → classical-mechanics | 2 | Co-parent |
| Singletons (mathematical-methods, condensed-matter, etc.) | 6 | Case-by-case |

## Tier 1 — Migrate (43 + 3 = 46 nodes)

These are clear shard misplacements where the slug's curriculum hub doesn't match its file location. Pure JSON entry moves; no content changes.

### 1a. 27 cosmology nodes in `philosophy-of-physics.json` → `astrophysics.json`

The full set, in current shard order:

```
bbn-theory, adiabatic-cooling, cmb-theory, recombination-era,
quantum-fluctuation, critical-density, horizon-problem, flatness-problem,
inflaton-field, angular-power-spectrum, lambda-cdm, cosmic-dynamics,
energy-conservation [platinum], density-parameter, negative-pressure,
fluid-equation, acceleration-equation, einstein-de-sitter, exponential-expansion,
de-sitter-universe, radiation-only-universe, expansion-law [platinum],
cosmic-gravity, conservation-cosmology, expansion-parameter,
friedmann-equations, big-bang-theory
```

2 platinum (`energy-conservation`, `expansion-law`) — both already flagged in the flag-violations diagnostic. The remaining 25 are legacy. All are unambiguously cosmology/early-universe topics.

**Suspected origin:** philosophy-of-physics shard was likely the "metaphysics of cosmology" bucket at some early stage, then content drifted to focus on physics rather than philosophy. The shard was never resorted.

### 1b. 16 statistical-mechanics nodes in `theoretical-physics.json` → `thermodynamics-statistical-mechanics.json`

```
loschmidts-paradox, quantum-degeneracy-pressure, fermi-dirac-statistics,
macrostate, microstate, multiplicity, density-of-states, ensembles,
microcanonical-ensemble, canonical-ensemble, grand-canonical-ensemble,
identical-particle-symmetry, bose-einstein-statistics,
bose-einstein-condensation, equilibrium-potential, statistical-mean
```

All 16 legacy. Textbook stat-mech topics. Should clearly be in the thermo shard.

### 1c. 3 metric-tensor cluster in `classical-mechanics.json` → `relativity.json`

```
metric-tensor [platinum, parent=relativity]
contravariant-covariant-vectors [platinum, parent=metric-tensor]
index-lowering-operation [platinum, parent=metric-tensor]
```

Three platinum nodes whose top-of-chain parent is `relativity` but who live in `classical-mechanics.json`. Anomalous; almost certainly a migration leftover.

### Migration mechanics

For each migration, the steps are:
1. Read source shard, pop slug entry.
2. Read target shard, insert slug entry.
3. Write both shards back.
4. Run `generate_search_index.py` to regenerate `search_index.json`, `slug_shard_map.json`, and any other derived indices.
5. Run `integrity_shield.py` to verify nothing broke.

The hub_manifests don't reference slugs by shard — only by slug name — so manifest references stay intact. The PHP `PhysicsService.loadShardForSlug` looks up via search_index, so URL routing is unaffected.

A single migration script could process all 46 nodes in one pass.

## Tier 2 — Co-parent (~27 nodes)

These mismatches reflect honest cross-pillar topics. Their shard placement (the discipline) and parent chain (the formalism) both make sense; the issue is that the parent chain doesn't include the shard hub, so the validator only sees one side.

### Examples

- **`astrophysical-fluids`** [platinum] — astrophysics shard, parent `fluids-nonlinear`. Stellar fluid dynamics is genuinely both. Adding `astrophysics` as a co-parent makes resolved_hubs = {fluids-nonlinear, astrophysics}, and both signatures contribute to the leakage check.
- **`stationary-action-principle`** [platinum] — classical-mechanics shard, parent `theoretical-physics`. The Lagrangian/Hamiltonian formalism is theoretical, the application is classical. Both should resolve.
- **`schwarzschild-criterion`** [platinum] — astrophysics shard, parent `thermodynamics-stat-mech`. Stellar thermodynamics.

### Mechanics

Two-line edit per node: append the shard hub to the parents array. Then regenerate search_index. No content changes.

**Caveat:** Co-parenting changes breadcrumbs and related-topic resolution. A node with two parent hubs renders differently. Worth confirming with you before bulk-applying.

## Tier 3 — Investigate (singletons + small clusters)

### `lie-groups` parented to `philosophy-of-physics`
Lie groups is a mathematics topic, currently lives in `mathematical-methods.json` (correct shard), but its sole parent is `philosophy-of-physics`. This is a clear parent-chain bug — Lie groups parent should be `mathematical-methods` (or co-parent it).

### `isaac-newton` parented to `structure-of-spacetime`
Biographical entry in classical-mechanics shard, parent chain reaches philosophy-of-physics via `structure-of-spacetime`. Biographies probably need a different parenting convention — should they parent to the hub for the field they worked in, or to a "people" pseudo-hub? Open question.

### `meissner-effect` parented to `spontaneous-symmetry-breaking`
Resolves to standard-model + theoretical-physics, but lives in condensed-matter. Genuine cross-pillar (Meissner effect is famously the condensed-matter discovery that revealed the Higgs mechanism). Probably co-parent.

### 16 nodes in philosophy-of-physics resolving to quantum-physics+theoretical
This cluster contains quantum-foundations topics (`epr-paradox`, `schmidt-decomposition`, `tensor-product-space`). These have one foot in quantum physics (the mechanics) and one in philosophy (the interpretation). Decision required: are these "physics with philosophical implications" (move to quantum-physics shard) or "philosophy of quantum mechanics" (keep in philosophy-of-physics shard, fix parent chain)? Either is defensible.

### 3 nodes in classical-mechanics resolving to electromagnetism
`simple-harmonic-oscillator-mechanics`, `potential-energy`, `conservative-force-field` — their parent chain reaches electromagnetism via odd routes (`potential-energy → stokes-theorem`, etc.). Parent chain noise rather than shard misplacement.

## Recommended action

The split-by-tier suggests two natural commits:

1. **Tier 1 migration** (46 nodes) — pure organizational cleanup. One script processes all three sub-classes (cosmology, stat-mech, metric-tensor). Pure JSON moves, regenerate indices, run shield. Low risk, well-defined.

2. **Tier 2 co-parenting** (~27 nodes) — slightly more semantic. Changes how breadcrumbs render. Worth a quick visual check on one or two before bulk applying.

3. **Tier 3 singletons** — case-by-case, deferred. Low impact individually.

## Notable cross-cutting observations

1. **philosophy-of-physics shard hosts the most misplacement** — 44 of its nodes (27 cosmology + 16 quantum-foundations + 1 spacetime-causal-topology) resolve elsewhere. The shard has functioned partly as a "homeless content" landing zone. Migrating the 27 cosmology nodes alone reduces the philosophy shard from 281 to 254 subtopics; the 16 quantum-foundations is a further 16. After both migrations philosophy-of-physics would have ~238 nodes — closer to its actual scope.

2. **The cross-pillar pattern is concentrated in classical/theoretical interfaces.** Lagrangian/Hamiltonian formalism, action principles, and statistical methods all genuinely live at the interface. The validator handles this — multi-hub parenting is supported by `_compile_dynamic_signatures`'s recursive resolution — but the current parent chains underuse this affordance.

3. **No mismatches involve `relativity`, `quantum-physics`, `standard-model`, `electromagnetism`, `condensed-matter`, or `fluids-nonlinear` as the shard hub.** These shards house only content that resolves to themselves (or to legitimate co-pillars). The mismatches are concentrated in `philosophy-of-physics`, `theoretical-physics`, and `classical-mechanics` — three shards that have historically absorbed cross-cutting content.
