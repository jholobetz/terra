---
trigger: always_on
description: Unified Platform Health & Assessment Protocol for assess commands
---

# 🪐 Unified Platform Assessment Protocol

Whenever the user instructs to run, check, or view an assessment (e.g., matching "assess -h", "run assess", "assess", "assess -p", "assess -q", "assess --all"):

1. **Automatic Intent Recognition**:
   - Classify the input immediately as an invocation of the Platform Assessment & Health Auditor (`scripts/assess`).
   - Do NOT ask for clarification, path verification, or suggest terminal shell aliases.
2. **Deterministic Execution Mapping**:
   - **"assess -h"** / **"run assess -h"** / **"assess help"**: Run `bash scripts/assess -h` (display CLI options & usage).
   - **"run assess"** / **"assess"**: Run `bash scripts/assess` (core suite + Pytest + quick scorecard).
   - **"assess -q"** / **"run assess -q"** / **"quick assess"**: Run `bash scripts/assess -q` (full scorecard skipping pytest in ~3s; strict by default, exits 1 on failure).
   - **"assess -c"** / **"assess --changed"** / **"assess --staged"**: Run `bash scripts/assess -c` (rapid incremental audit of uncommitted/staged files in <100ms).
   - **"assess -s"** / **"assess -q -s"** / **"assess silent"**: Run `bash scripts/assess -q -s` (silent pre-commit gate, zero output, exits 1 on failure).
   - **"assess --permissive"** / **"assess advisory"**: Run `bash scripts/assess --permissive` (advisory run, exits 0 on invariant failure during WIP refactoring).
   - **"assess --diff"** / **"assess diff"**: Run `bash scripts/assess --diff` (telemetry delta comparison against baseline latest.json).
   - **"assess --history"** / **"assess history"**: Run `bash scripts/assess --history` (tabular log of past assessment runs).
   - **"assess --trends"** / **"assess trends"**: Run `bash scripts/assess --trends` (progression velocity and sprint trajectory).
   - **"assess --heal"** / **"assess heal"**: Run `bash scripts/assess --heal` (autonomous self-healing: syncs shard hashes, heals DAG, purges stale cache).
   - **"assess --domain"** / **"assess domain"**: Run `bash scripts/assess --domain "<name>"` (scoped domain telemetry scorecard).
   - **"assess --shard"** / **"assess shard"**: Run `bash scripts/assess --shard "<xx>"` (scoped hex shard partition scorecard).
   - **"assess -i"** / **"assess integrity"**: Run `bash scripts/assess -i` (sitewide integrity shield deep scan).
   - **"assess -p"** / **"run assess -p"** / **"assess prompt"**: Run `bash scripts/assess -p` (AI agent prompt payload with live telemetry in ~3s).
   - **"assess --all"** / **"full assess"**: Run `bash scripts/assess --all` (deep hybrid audit).
   - **"assess --install-hook"**: Run `bash scripts/assess --install-hook` (install 3-second pre-commit git hook).
   - **"assess diagnostics"**: Run `bash scripts/assess --diagnostics`.
3. **Execution Safety**:
   - Always invoke as `bash scripts/assess [args]` within the project working directory.
   - **Web GUI Console**: Available at `http://localhost:8000/physics/admin/assess` (or `/physics/admin`) on the local test server with one-click triggers, self-healing, strict ratchets, and interactive terminal console drawer.
4. **Synthesize Output**:
   - Return the rendered terminal scorecard or the generated prompt payload cleanly to the user.
