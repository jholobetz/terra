---
trigger: always_on
description: Direct URL Equation Repair Protocol for Physics Lab equation-explainer URLs
---

# 🧮 Direct URL Equation Repair Protocol

Whenever the user provides a local `equation-explainer` URL (matching `http://localhost:8000/physics/equation-explainer...`) or a formula ID/LaTeX snippet in the prompt:

1. **Automatic Intent Recognition**: Classify the input immediately as an Equation Repair / TeX Decorruption task.
2. **Execute Repair Engine**: Run the repair tool instantly using terminal commands:
   ```bash
   scripts/fixlatex "<URL|ID|LaTeX>"
   ```
3. **Verify Integrity**: Confirm that:
   - The formula definition in `app/config/content/formulas/[xx]/shard_[xx].json` is updated.
   - TeX corruptions in prose fields (`description`, `interpretation`, etc.) are sanitized.
   - MariaDB record is updated with `equation_svg = NULL` to trigger clean MathJax rendering.
   - `app/config/formulas_latex_index.json` mapping is synchronized.
4. **Synthesize Output**: Return a concise summary detailing the resolved Formula ID, target shard path, clean LaTeX equation, and applied sanitizations.
