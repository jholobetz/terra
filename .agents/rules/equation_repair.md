---
trigger: always_on
description: Direct URL Equation Repair Protocol for Physics Lab equation-explainer URLs
---

# 🧮 Direct URL Equation Repair Protocol

Whenever the user provides a local `equation-explainer` URL (matching `http://localhost:8000/physics/equation-explainer...`) or a formula ID/LaTeX snippet in the prompt, with or without an accompanying hint or reference text:

1. **Automatic Intent Recognition**: Classify the input immediately as an Equation Repair / TeX Decorruption task.
2. **Execute Repair Engine (Single-Pass Protocol)**:
   - Run the repair tool in **exactly one** terminal invocation:
     ```bash
     scripts/fixlatex "<URL|ID|LaTeX>" ["<hint or reference text>"]
     ```
   - **Zero-Interruption Mandate (No Repetitive Modals)**:
     - **Strict Ban on Terminal Inspection Commands**: Never run `git diff`, `git status`, or shell file inspections via `run_command`. The agent's file tools already track changes in memory.
     - **Strict Ban on Ad-Hoc Terminal Scripts**: Never run one-off `python3 -c` or `php -r` patch commands via `run_command`.
     - **Use Sandboxed Editor for Manual Touch-ups**: If shard prose requires additional manual editing beyond what `fixlatex` handles, edit the shard file directly using the agent's built-in file editing tool (`replace_file_content`), which runs safely inside the sandbox with 0 user prompts.
3. **Verify Integrity**: Confirm that:
   - The formula definition in `app/config/content/formulas/[xx]/shard_[xx].json` is updated.
   - TeX corruptions in prose fields (`description`, `interpretation`, etc.) are sanitized.
   - MariaDB record is updated with `equation_svg = NULL` to trigger clean MathJax rendering.
   - `app/config/formulas_latex_index.json` mapping is synchronized.
4. **Synthesize Output**: Return a concise summary detailing the resolved Formula ID, target shard path, clean LaTeX equation, and applied sanitizations.
