---
name: cas-symbolic-prover
description: >-
  Verify mathematical formulas, asymptotic boundary limits, and dimensional consistency
  using the sandboxed SymPy Computer Algebra System (CAS) engine. Evaluates limits,
  calculates Taylor series, and validates parent-child algebraic derivations.
---

# 🧪 CAS Symbolic Prover Skill

Use this skill whenever verifying the mathematical correctness of a formula, computing asymptotic limits ($x \to 0$, $x \to \infty$), testing Taylor expansions, or validating dimensional invariance.

---

## 1. The CAS Architecture

* **Engine Core**: Located in [`scripts/lib/cas_engine.py`](file:///Users/holobetj/code/gemini/terra/scripts/lib/cas_engine.py).
* **Execution Boundary**: Sandboxed with a strict **2.0-second timeout** and AST parse guards to prevent infinite loops or CPU exhaustion.
* **FlightPHP REST Endpoint**: `/physics/api/cas-evaluate` accepting `latex`, `variable`, `target`, and `operation`.

---

## 2. Testing Limits via Python CLI

You can invoke the CAS engine directly using the Python environment:

```bash
# Evaluate a limit directly using the Python CLI
.venv/bin/python3 -c '
from scripts.lib.cas_engine import evaluate_cas_limit
result = evaluate_cas_limit(
    latex="E = \\frac{m c^2}{\\sqrt{1 - \\frac{v^2}{c^2}}}",
    variable="v",
    target="0"
)
print("Computed Limit:", result)
'

# Run the automated CAS test suite
.venv/bin/python3 -m pytest tests/test_cas_engine.py
```

---

## 3. Standard Verification Workflows

### A. Verifying Limiting Cases in Formula Shards
When drafting or auditing the `limits_and_boundary` field of a formula:
1. Identify the asymptotic physical variables (e.g. $v \ll c$, $\hbar \to 0$, $T \to 0$, $r \to \infty$).
2. Evaluate the symbolic limit in SymPy.
3. Compare the algebraic output against the prose claims in the shard.
4. Ensure the resulting LaTeX in the shard is mathematically exact and cleanly formatted.

### B. Proving Parent &rarr; Child Derivations
To prove that Formula $B$ derives from Formula $A$ under condition $C$:
1. Substitute condition $C$ into Formula $A$.
2. Simplify the difference: $\text{Simplify}(A_{\text{reduced}} - B)$.
3. If the expression simplifies identically to $0$, the derivation edge is formally proven.
