# Physics Lab Agent Directives (GEMINI.md)

This file contains automated directives and workflow protocols for AI assistants working in the Physics Lab repository.

---

## 🧮 Direct URL Equation Repair Protocol

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
4. **Synthesize Output**: Return a concise summary to the user detailing:
   - Resolved Formula ID
   - Target Shard Path
   - Cleaned LaTeX equation
   - Summary of applied prose decorruptions
