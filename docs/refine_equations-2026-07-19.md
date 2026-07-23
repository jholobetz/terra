# Refinement Plan for Missing Equations (2026-07-19)

This plan details the phased strategy to resolve the remaining **3,407 unregistered equations** found in the Physics Lab encyclopedia, utilizing the optimized Graduation Queue Stack (GQS) CLI.

---

## Phase 1: Localizing the Baseline Changes
Before proceeding with any new content generations, we must lock in the working implementation of the pipeline:
1. **Commit current updates**: Stage and commit the modified `gqs.py` CLI, the new `scratch/compile_formulas.py` helper, and the new `undefined_formulas_2026-07-19.md` report.
2. **Local browser test**: Load the local development server, perform a hard reload (`Cmd + Shift + R`), and navigate to pages like `hamiltonian-operator` (for $\hbar \to 0$) or `thermodynamics-statistical-mechanics-overview` (for $dU = T dS - P dV + \dots$). Click the equations to verify that the Equation Explainer now displays their complete physical titles, AI-seeded summaries, and variable breakdowns instead of the "Custom Physics Formula" default.

---

## Phase 2: Prioritized Ingestion of High-Impact Equations
Trying to register and AI-seed all 3,407 missing equations at once is highly discouraged (it would likely hit Gemini API rate limit throttles, consume excessive tokens, and prevent quality control).

Instead, we should target the **highest-impact equations** (those referenced in dozens of articles) in small, controlled batches:
1. **Batch 1 (Top 10)**: Run `.venv/bin/python3 gqs.py formula-auto-seed 10` to automatically seed the 10 most common equations (like $\Omega_\Lambda = 1$, $v/c \to 0$, etc.).
2. **Review & Audit**: Verify the quality of these 10 new definitions inside their shards (e.g., checking variable definitions).
3. **Batch 2 (Top 50)**: Once Batch 1 is verified, run a larger pass to clean up the next 50 most common equations.

---

## Phase 3: Continuous Background Processing (Automation)
For the remaining lower-frequency equations, we can automate the pipeline so it runs periodically during off-peak hours without interrupting developer tasks:
* **Cron/Timer scheduling**: We could schedule a background cron job to run the auto-seeder in small increments (e.g., auto-seeding 20 equations every night at midnight). This slowly chips away at the 3,407 list while remaining well within API free-tier limits.

---

## Phase 4: Quality & Integrity Verification
At the end of each batch ingestion:
1. **Run Audits**: Run `python3 gqs.py audit` to run `integrity_shield.py` and confirm that all new formulas are structurally linked, contain no syntax formatting warnings, and pass semantic checks.
2. **Execute Tests**: Run Flight's PHP test suite to ensure database lookups and searches remain fast and correct.
