# Platinum Flag-Violation Nodes — Diagnosis (2026-05-24)

Generated after the legacy `"university-level"` scrub. These 33 nodes are flagged `"standard": "platinum"` but fail at least one OPS qualitative gate as scored by `generate_system_health.py:90-98`. All were graduated before one or more gates were tightened.

## Headline finding

**All 33 are lead-only violations. Zero have artifact violations** (`<ul>`/`<li>` in content). The bullet ban was enforced longer than the in-media-res rule, so platinum graduations cleared the artifact gate but predate strict lead checking.

## Compounding issues

| Compounding issue | Count |
|---|---|
| Also has banned meta-talk phrase | 6 |
| Has TF-IDF contextual leakage (validator-rejecting) | 4 |
| Has words < 650 (OPS floor) | 1 |
| Has links < 5 (OPS floor) | 2 |
| Has duplicate link targets | 1 |
| Has zero formula identities | 0 |

## Per-shard distribution

```
philosophy-of-physics.json                    12  ← 36% of total
classical-mechanics.json                       6  ← all share a template
thermodynamics-statistical-mechanics.json      5
mathematical-methods.json                      2
fluids-nonlinear.json                          2
condensed-matter.json                          2
quantum-physics.json                           1
relativity.json                                1
standard-model.json                            1
electromagnetism.json                          1
```

`philosophy-of-physics.json` carries a disproportionate share — consistent with the weak-signal hub problem (see "Cross-cutting" below).

---

## Tier 1 — Critical (TF-IDF leakage, 4 nodes)

These four will be **rejected by `validate_platinum_standard:1719`** on any re-graduation attempt. Content rewrite alone is unlikely to fix them — they need either reparenting, content reframing toward the parent hub's vocabulary, or a shard move.

### `expansion-law` (philosophy-of-physics.json)
- Parent resolves to `astrophysics` (score 9). Loses to `philosophy-of-physics` (score 13).
- **Structural anomaly:** same shape as `friedmann-equations` from the prior diagnostic — slug lives in `philosophy-of-physics.json` but parent chain resolves to `astrophysics`. Two slugs with this exact pattern is no longer accidental; suggests a class of cosmology nodes that ended up in the philosophy shard.
- **Recommended:** shard-move to `astrophysics.json`, then lead rewrite. Or, if the intent is philosophical framing of expansion, reparent to a philosophy-of-physics-resolving slug and tune content vocabulary.

### `crystal-lattice` (condensed-matter.json)
- Parent `condensed-matter` (score 10). Loses to `philosophy-of-physics` (score 13).
- Content presumably leans on generic words ("physical", "reality", "laws", "manifold") that dominate the philosophy-of-physics signature.
- **Recommended:** content rewrite to foreground condensed-matter vocabulary — `lattice`, `fermi`, `phonon`, `electron`, `periodic`, `crystal`, `reciprocal`. Same root cause as `area-law` below.

### `area-law` (thermodynamics-statistical-mechanics.json)
- Parent `thermodynamics-statistical-mechanics` (score 10). Loses to `philosophy-of-physics` (score 13).
- Black-hole entropy is genuinely cross-pillar (thermo + astro + philosophy), so this leakage is partly content-honest, partly signature-pollution.
- **Recommended:** rewrite to lead harder on `entropy`, `boltzmann`, `temperature`, `statistical`, `heat`, `thermal` to clear the +2 margin.

### `leptons` (standard-model.json) — worst offender
- Parent resolves to `quantum-physics` (score 8). Loses to **three** hubs simultaneously: `standard-model` (13), `electromagnetism` (11), `philosophy-of-physics` (12).
- The parent chain points to `quantum-physics` but the content reads as standard-model. Reparenting from `quantum-physics` → `standard-model` would *fix* the leakage (parent score 13 wins) without any content rewrite.
- **Recommended:** **reparent first**, then re-run validator. This is the easiest fix in the leakage tier.

---

## Tier 2 — Compound violations (8 nodes with multiple issues)

These have a lead violation plus at least one mechanical OPS failure. Roughly ordered by effort.

| Slug | Shard | Compounding issue(s) |
|---|---|---|
| `generalized-coordinates` | classical-mechanics | meta-talk + **0 outgoing links** |
| `degrees-of-freedom` | classical-mechanics | meta-talk + **0 outgoing links** |
| `monochromatic-plane-waves` | electromagnetism | meta-talk + words=629 (below 650 floor) |
| `kinetic-energy` | classical-mechanics | meta-talk × 2 (`"university-level"`, `"this investigation"`) |
| `total-mechanical-energy` | classical-mechanics | meta-talk |
| `power-equation` | classical-mechanics | meta-talk |
| `big-freeze` | thermodynamics | duplicate link target `dark-energy-theory` |

**Notable:** `generalized-coordinates` and `degrees-of-freedom` have **zero** outgoing links yet are flagged platinum. Either the 5-link minimum (`validate_platinum_standard:1672`) was added after they graduated, or the gate was bypassed. They need at least 5 links each plus the lead rewrite.

**Notable:** five of the six classical-mechanics flag-violators share the `"university-level"` meta-talk pattern. Likely a single graduation batch ran on a shared template — a focused re-run of those five against the current validator after a meta-talk scrub would likely surface the same lead issue and nothing else.

---

## Tier 3 — Lead-only (21 remaining nodes)

Pure first-sentence rewrites. No structural decisions, no link work, no shard moves. Each ~10–15 min if content is otherwise solid.

| Shard | Slugs |
|---|---|
| philosophy-of-physics | `scientific-realism`, `ontological-commitments`, `instrumentalism`, `structure-of-spacetime`, `arrow-of-time`, `physical-causality`, `time-symmetric-laws`, `humean-laws`, `energy-conservation`, `transactional-interpretation`, `strong-energy-condition` (11) |
| thermodynamics-stat-mech | `heat-death`, `temperature-gradient-equation`, `thermodynamics-second-law` (3) |
| fluids-nonlinear | `reynolds-number`, `supersonic-jets` (2) |
| mathematical-methods | `vector-calculus`, `ckm-matrix` (2) |
| condensed-matter | `nearly-free-electron-model` (1) |
| classical-mechanics | `rigid-body` (1) |
| quantum-physics | `standing-wave` (1) |
| relativity | `special-relativity` (1) |

---

## Cross-cutting observations

### 1. philosophy-of-physics signature is polluting other hubs' validations

Three of the four Tier-1 leakages lose to `philosophy-of-physics`. Its TF-IDF signature (from the orchestrator's startup log) includes `vacuum`, `manifold`, `causal`, `quantum`, `topology`, `physical`, `success`, `rungs`, `universe`, `requirements`, `reality`, `laws`, `measurement`. Half of those are generic enough to appear in *any* physics prose — `physical`, `reality`, `laws`, `manifold`, `universe`, `quantum`. This is the weak-signal pillar problem I flagged in the original deep analysis: a pillar with low silo factor (philosophy-of-physics had 0.53 in the prior health snapshot, but its signature is contaminated with cross-pillar words from heterogeneous platinum content).

**Implication:** the TF-IDF validator will keep producing false-positive leakage errors for condensed-matter, thermo, and standard-model nodes that legitimately reference philosophical concepts. This isn't fixed by content rewrites — it's a signature-quality issue. A diagnostic of *which words drive each leakage* (i.e., which philosophy-of-physics signature terms actually appear in the offending content) would let us refine the signature, possibly by adding a stop-list of generic-physics words on top of the existing TF-IDF.

### 2. philosophy-of-physics shard houses cosmology

Two nodes (`expansion-law` here, `friedmann-equations` in the prior diagnostic) live in `philosophy-of-physics.json` but resolve via parent chain to `astrophysics`. Worth an audit: how many philosophy-of-physics-shard nodes have parents resolving outside philosophy-of-physics? If it's a pattern, those slugs should be migrated en masse to their resolved hub's shard.

### 3. Two nodes graduated with zero outgoing links

`generalized-coordinates` and `degrees-of-freedom`. The 5-link OPS minimum exists in code (`validate_platinum_standard:1672`) but didn't gate these. Either:
- Graduation happened before the gate was added, or
- The `unlock_protected=True` path in `orchestrator.save` was used to push them through.

Either way, the current validator should be re-run against the existing platinum set as a periodic audit — a "shield strict mode" that applies platinum gates to platinum nodes, not just to new graduations. (This is essentially what `flag_violations` measures, but only for lead/artifact; extending it to all OPS gates would catch the link-floor regressions automatically.)

### 4. classical-mechanics graduated a templated batch

Five of the six classical-mechanics flag-violators share the `"university-level"` meta-talk. The sixth (`rigid-body`) doesn't — different content origin. This suggests `commit_node.py` runs on a templated draft frequently, and a single bad template propagates.

---

## Recommended fix order

1. **`leptons` (reparent only)** — one-line metadata change, likely fixes everything. Validates the workflow before bigger investment.
2. **`generalized-coordinates`, `degrees-of-freedom`** — add 5 links each + lead rewrite + meta-talk scrub. Mechanical, scoped.
3. **classical-mechanics meta-talk batch** (`total-mechanical-energy`, `power-equation`, `kinetic-energy`) — single-phrase scrub + lead rewrite per node. Possible to batch with a shared edit pattern.
4. **`monochromatic-plane-waves`** — add ~30 words + scrub + lead rewrite.
5. **`big-freeze`** — remove the duplicate link + lead rewrite.
6. **Tier 3 lead-only (21 nodes)** — straightforward but volume-heavy. Could be done in batches grouped by shard.
7. **TF-IDF leakage Tier 1 minus leptons** (`expansion-law`, `crystal-lattice`, `area-law`) — defer until signature quality is assessed. Rewriting against a polluted signature wastes effort.

## Adjacent — signature health investigation

Before tackling Tier-1 leakage cases (other than leptons), it's worth doing a one-shot pass on the TF-IDF signatures to identify which words are doing real disambiguating work and which are noise. Cheap: ~1 hour. Pays off by either (a) confirming the signatures are honest, in which case content rewrites are the answer, or (b) finding generic-word pollution, in which case a stop-list addition is the answer and the rewrites can be much lighter.
