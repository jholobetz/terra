# Platinum Promotion Candidates — Diagnosis (2026-05-24)

Generated against the corpus state after Sprint 2 alignment. The four nodes below are flagged in `system_health.json` as `pseudo_platinum_count` — they meet the quantitative bar (≥650 words, density ≥60) but are not flagged `"standard": "platinum"`. Each fails at least one OPS qualitative gate; none can be promoted by flag-flip alone.

## Summary

| Slug | Shard | Words | Links | Lead | Artifact | Meta-talk | TF-IDF leakage | Fix size |
|---|---|---|---|---|---|---|---|---|
| `stationary-action` | theoretical-physics | 662 | 5 | ✗ | — | "university-level" | none | **small** |
| `friedmann-equations` | philosophy-of-physics | 714 | 12 | ✗ | `<ul>` `<li>` | — | none | **medium** + shard move |
| `magnetic-matter` | electromagnetism | 622 | 17 | ✗ | `<ul>` `<li>` | "university-level" | none | **medium** (below 650) |
| `relativistic-quantum-field-theory` | standard-model | 646 | 23 | ✗ | — | "university-level" | **yes** | **large** |

## Cross-cutting patterns

1. **`"university-level"` appears in 3/4 nodes.** This is a stock phrase from some shared template that the orchestrator's self-healing routine catches (`orchestrator.py:1638` substitutes it with `"theoretical"`). Worth a one-shot global scrub across the legacy corpus; would unblock these and likely others.
2. **All 4 have lead violations** of the same shape: title appears verbatim in the first ~15 words. Common template artifact.
3. **TF-IDF margins are tight** for `stationary-action` (parent 9 vs runner-up 7) and `friedmann-equations` (parent 7 vs runner-up 6). Rewrites that shift vocabulary could trip the +2 leakage threshold; lead-rewrites should be done with the hub signature in view.

---

## `stationary-action` — smallest scope

- **Shard:** `theoretical-physics.json`
- **Parents:** `[euler-lagrange-equations]` → resolves to hub `theoretical-physics`
- **Words 662, links 5 (exact min), formula_ids 4**

**Current first sentence:**
> "In the variational formulation of physics, Stationary Action refers to the condition where the first variation of the action functional vanishes (\\( \\delta S = 0 \\))…"

**OPS violations:**
- Lead — title `stationary action` in first sentence
- Meta-talk — `"university-level"` elsewhere in content
- Links exactly at the floor of 5; any link removed during the rewrite breaks the OPS minimum

**TF-IDF:** theoretical-physics 9, quantum-physics 7, relativity 6. Parent wins by 2 (right at the leakage tolerance — safe, but no margin for vocabulary drift).

**Recommended fix:**
1. Rewrite the first sentence to lead with `\\( \\delta S = 0 \\)` itself, or with "The vanishing of the first variation of the action functional…" — drop `Stationary Action` from the first 15 words.
2. Find and replace `"university-level"` with `"theoretical"` (the orchestrator's self-healing substitution).
3. Do not add or remove links during the rewrite; the node is exactly at the link floor.
4. Estimated time: 15–20 min.

---

## `friedmann-equations` — needs a shard move

- **Shard:** `philosophy-of-physics.json` ← **structural anomaly**
- **Parents:** `[big-bang-theory]` → resolves to hub `astrophysics` (recursive resolution through `big-bang-theory`'s parents)
- **Words 714, links 12, formula_ids 4**

**Current first sentence:**
> "The Friedmann Equations are the fundamental set of ordinary differential equations that describe the expansion and evolution of the universe as a whole…"

**OPS violations:**
- Lead — title `friedmann equations` in first sentence
- Artifact — `<ul>` / `<li>` present
- No meta-talk hits (cleanest of the four on that axis)

**TF-IDF:** astrophysics 7, fluids-nonlinear 6, classical-mechanics 5, philosophy-of-physics 5. Parent (astrophysics) wins, but only by 1 over fluids-nonlinear — within tolerance but tight.

**Structural anomaly:** Slug lives in `philosophy-of-physics.json` but resolves to the `astrophysics` hub via its parent chain. Either:
- The shard placement is wrong (most likely — Friedmann equations are core cosmology), or
- The parent chain is wrong (the slug should reparent to a philosophy-of-physics-resolving hub if the intent is philosophical framing).

The content reads as straight cosmology (expansion, evolution of the universe), so the shard placement is the bug.

**Recommended fix:**
1. Move the slug from `philosophy-of-physics.json` to `astrophysics.json`. Update `slug_shard_map.json` and `search_index.json` accordingly (or regenerate the search index via `generate_search_index.py`).
2. Rewrite the first sentence to lead in media res — e.g., starting with the FRW metric or the dynamics equation itself.
3. Convert the `<ul>` / `<li>` block to flowing `<p>` prose. Bullets in cosmology usually enumerate equations or assumptions — those become numbered sentences ("The first equation governs… The second equation…").
4. Estimated time: 30–45 min (shard move adds overhead).

---

## `magnetic-matter` — content expansion needed

- **Shard:** `electromagnetism.json`
- **Parents:** `[electromagnetism]` → hub `electromagnetism` (direct)
- **Words 622 (BELOW the 650 floor)**, links 17, formula_ids 4

**Current first sentence:**
> "Magnetism in Matter is the study of how macroscopic materials respond to and generate magnetic fields…"

**OPS violations:**
- Lead — title `magnetism in matter` in first sentence
- Artifact — `<ul>` / `<li>` present
- Meta-talk — `"university-level"`
- **Word count below floor** — needs at least 28 more words, realistically +50 for safety against future word-counter changes

**TF-IDF:** electromagnetism 8, condensed-matter 5. Parent wins by 3 — comfortable.

**Recommended fix:**
1. Convert `<ul>` / `<li>` block to prose — this naturally expands word count if the bullets were terse.
2. Rewrite the first sentence to lead with a physical mechanism — e.g., "Macroscopic materials respond to applied fields through three regimes — diamagnetism, paramagnetism, and ferromagnetism — each rooted in…".
3. Scrub `"university-level"`.
4. Estimated time: 30–40 min.

---

## `relativistic-quantum-field-theory` — largest scope, structural decision required

- **Shard:** `standard-model.json`
- **Parents:** `[standard-model]` → hub `standard-model` (direct)
- **Words 646 (also just below floor)**, links 23, formula_ids 4

**Current first sentence:**
> "Relativistic Quantum Field Theory (QFT) is the mathematical language of modern particle physics, providing the unified framework that merges special relativity and quantum mechanics…"

**OPS violations:**
- Lead — every word of the title appears in the first sentence
- Meta-talk — `"university-level"`
- Word count below floor (646 vs 650)
- **Contextual leakage:** parent `standard-model` scores **8**, but `theoretical-physics` scores **11** — gap of 3, exceeds the +2 validator tolerance. This is a hard OPS failure the validator (`orchestrator.py:1719`) will reject.

**This is the structural one.** The content's vocabulary leans toward general field theory and theoretical formalism rather than standard-model-specific terms (boson, fermion, gauge, electroweak, color, flavor, quarks, baryon, spinor, renormalization). Two possible resolutions:

- **Option A: Reframe content toward standard-model.** Rewrite to foreground gauge bosons, fermion representations, electroweak unification, renormalization in the SM context. Keeps the slug where it is but is a substantial content rewrite, easily 60–90 min.
- **Option B: Move slug to `theoretical-physics.json`.** Treat QFT as the formal framework (theoretical-physics) and have the standard-model hub link to it. Lighter content rewrite, but a shard move + repointing every existing inbound link.

**Recommended fix:**
1. Decide A vs B with intent — what role does this slug play in the curriculum?
2. Either way: rewrite lead, scrub meta-talk, expand past 650 words.
3. Estimated time: 60–90 min including the structural decision.

---

## Order recommended if tackling sequentially

1. **`stationary-action`** — smallest scope, validates the workflow end-to-end before touching anything bigger.
2. **`magnetic-matter`** — mechanical (artifact + word expansion + lead), no structural decisions.
3. **`friedmann-equations`** — adds shard move, but content is otherwise clean.
4. **`relativistic-quantum-field-theory`** — requires a curriculum-level decision (A vs B above), should be deliberate not reactive.

## Adjacent finding worth surfacing

The `"university-level"` phrase pattern across 3/4 nodes suggests a corpus-wide stock phrase. A one-shot pass with `repair_artifacts.py` (or a new `oneshot`) to scrub this phrase across all `standard: legacy` content would reduce the noise floor for future audits without touching graduated platinum nodes.
