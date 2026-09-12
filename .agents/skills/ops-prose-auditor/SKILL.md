---
name: ops-prose-auditor
description: >-
  Audit, validate, and enforce the Organic Platinum Standard (OPS) quality gates on
  Physics Lab subtopic encyclopedia articles. Verifies In Media Res leads, continuous
  zero-artifact HTML prose, MathJax frequency (2-4 per paragraph), word count bounds,
  and topological graph connectivity.
---

# 🏛️ OPS Prose Auditor Skill

Use this skill whenever auditing, reviewing, drafting, or editing encyclopedia subtopic articles in `app/config/content/*.json`.

---

## 1. Quick Quality Gate Checklist

Every subtopic article must satisfy the **Organic Platinum Standard (OPS)**:

| Quality Gate | Standard Requirement | Verification Method |
| :--- | :--- | :--- |
| **"In Media Res" Lead** | The first sentence MUST lead directly with a physical principle, identity, or derivation. The article title MUST NOT appear in the first 15 words. No meta-talk ("This article covers..."). | Text inspection of `<p>` tag #1 |
| **Continuous Technical Prose** | Strictly prohibited: `<ul>`, `<ol>`, `<li>`, fragmented headings (`<h2>`, `<h3>`), and markdown artifacts (`**`, `__`) inside JSON content strings. Use `<strong>` and `<em>` tags only. | Regex & `integrity_shield.py` |
| **MathJax Frequency** | Every single paragraph MUST contain at least **2 to 4 distinct inline MathJax expressions** (e.g. \( g_{\mu\nu} \), \( |\Psi\rangle \)) to prevent visual walls of text. | Regex count `\([^\)]+\)` or `\$[^\$]+\$` |
| **Variable Coupling** | Every physical parameter, coordinate, or operator must be coupled directly with its mathematical symbol on first mention (e.g. "metric tensor \( g_{\mu\nu} \)"). | Prose review |
| **Word Count Cushion** | Standard subtopics: **650 to 1,000 words** of stripped prose (~800–950 raw words). Category Hub Overviews: **800 to 1,000 words**. | Word count excluding HTML tags |
| **Topological Symmetries** | Minimum **5 outgoing links**, minimum **2 incoming links**, and minimum **1 cross-hub bridge** connecting to a completely different primary Pillar Hub. | Graph linker check |

---

## 2. Automated Verification Commands

Run the following commands using the project virtual environment (`.venv/`):

```bash
# Run sitewide integrity shield audit (validates OPS gates across all 14 shards)
.venv/bin/python3 integrity_shield.py

# Audit a single subtopic slug
.venv/bin/python3 gqs.py audit <subtopic-slug>

# Check GQS graduation backlog and platform metrics
.venv/bin/python3 gqs.py status
```

---

## 3. Standard Remediation Workflow

When a subtopic fails an OPS audit:

1. **Fixing the Opening Sentence**:
   * *Bad*: `<p>The Schwarzschild metric is a solution to the Einstein field equations...</p>`
   * *Good*: `<p>Static spherical symmetry in vacuum spacetime constrains the pseudo-Riemannian metric tensor \( g_{\mu\nu} \) through the field equations \( R_{\mu\nu} = 0 \), yielding an invariant line element \( ds^2 \) uniquely parameterized by gravitational radius \( r_s = \frac{2GM}{c^2} \).</p>`

2. **Purging Markdown Artifacts**:
   * Replace any `**bold text**` with `<strong>bold text</strong>`.
   * Replace any `*italic text*` with `<em>italic text</em>`.
   * Convert list items into continuous, explanatory analytical paragraphs wrapped in `<p>` tags.

3. **Boosting Inline MathJax Density**:
   * If a paragraph has fewer than 2 inline MathJax expressions, couple bare nouns to their mathematical symbols (e.g. change "wavevector" to "wavevector \( \mathbf{k} \)", "energy density" to "energy density \( \rho_E \)").

4. **Preserving Delimiters**:
   * Ensure inline math uses valid LaTeX delimiters (`\( ... \)` or `$ ... $`).
   * Never let HTML tags penetrate into math mode (e.g. `\( \mathbf{F} = m \mathbf{a} \)`, NOT `\( <strong>F</strong> = m \mathbf{a} \)`).
