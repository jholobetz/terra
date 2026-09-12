# Strategic Architecture: Long Task Horizons in Physics Lab

In AI agent engineering and computational science, a **Long Task Horizon** refers to an autonomous or semi-autonomous system capable of executing complex, multi-stage, multi-hour (or multi-day) goals across thousands of interdependent steps without drifting, hallucinating, or exceeding resource constraints.

For the **Physics Lab (`terra`)**, long task horizons represent the evolution from **reactive micro-editing** (fixing isolated equations or running small manual batches) to **self-governing, goal-oriented scientific curation**.

---

## 1. The Four Strategic Horizons

```mermaid
flowchart TD
    subgraph Horizon1["1. Ontological Graph Horizon"]
        H1A["13,802 Formulas"] --> H1B["Axiomatic Roots"]
        H1B --> H1C["Global Mathematical DAG"]
    end

    subgraph Horizon2["2. Symbolic Verification Horizon"]
        H2A["LaTeX Equations"] --> H2B["SymPy Symbolic Proofs"]
        H2B --> H2C["Dimensional & Unit Invariance"]
    end

    subgraph Horizon3["3. Interactive Multimodal Horizon"]
        H3A["Formulas & Concepts"] --> H3B["3D WebGL / Phase Portraits"]
        H3B --> H3C["Interactive Lab Simulations"]
    end

    subgraph Horizon4["4. Autonomous Governance Horizon"]
        H4A["Budget Contract ($ Ceiling)"] --> H4B["Self-Healing Integrity Shield"]
        H4B --> H4C["Deterministic Shard Checkpoints"]
    end
```

---

## 🏛️ Horizon 1: The Complete Axiomatic Knowledge Graph

* **The Vision**: Every equation in the 13,802-formula encyclopedia traces its derivation back to a foundational set of physical axioms (e.g., Principle of Least Action, Einstein Equivalence Principle, Quantum Superposition, Noether's Theorem).
* **The Complexity**: Connecting cross-disciplinary boundaries (e.g., linking stellar nucleosynthesis to fluid dynamics, and fluid dynamics back to statistical mechanics and thermodynamics).
* **Autonomous Objective**: Periodic graph-wide audits that detect disconnected sub-islands, identify circular dependencies (derivation cycles), and iteratively resolve ancestral lineages.

---

## 🧪 Horizon 2: Automated Symbolic Verification (Beyond Text)

* **The Vision**: Moving from descriptive prose explanations to **machine-verified algebraic proofs**.
* **The Complexity**: Every physics formula contains mathematical relationships with physical units and boundary limits.
* **Autonomous Objective**: An automated pipeline that:
  1. Extracts LaTeX equations from the 256 JSON shards.
  2. Compiles expressions into symbolic structures (e.g., SymPy / Mathematica).
  3. Verifies dimensional analysis consistency ($[M L T^{-2}]$ vs $[M L^2 T^{-2}]$).
  4. Formally proves asymptotic limits (e.g., verifying that $p = \gamma mv \to mv$ as $v/c \to 0$).

---

## 🎨 Horizon 3: Multimodal & Interactive Simulation Synthesis

* **The Vision**: Automatically generating dynamic visual interactive models for key formulas and theoretical concepts.
* **The Complexity**: Synthesizing mathematically accurate JavaScript / WebGL physics engines that render phase portraits, geodesics, field lines, and wave packet scattering in real-time.
* **Autonomous Objective**: An agent identifies formula clusters suited for interactive demonstration, synthesizes standalone Three.js / Canvas components, and binds them into the front-end interface.

---

## 🛡️ Horizon 4: Autonomous Governance & Hard Guardrails

Real-world long task horizons require robust operational and financial guardrails to prevent drift, error compounding, or resource exhaustion:

### 1. Contract-Driven Execution (Hard Boundaries)
* Long-horizon tasks must never run unconstrained.
* Every background process must operate under an enforceable **Budget & Request Contract**:
  * `--max-cost-dollars <amount>`: Immediate hardware/thread halt if spend touches the ceiling.
  * `--limit <N>`: Hard limit on total API requests.
  * `thinking_budget = 1024`: Strict token bounds on LLM internal reasoning chains to prevent runaway cost inflation.

### 2. The Worker-Auditor Separation Pattern
* An autonomous generation model should never be the sole judge of its own output.
* **Architecture**:
  * **Worker Engine**: Executes generation and enrichment (e.g., Gemini 3.7 Flash).
  * **Auditor (`IntegrityShield`)**: Independent, deterministic Python scripts and schema checkers that audit JSON structure, LaTeX delimiters, citation links, and graph integrity before committing changes to disk.

### 3. Fault-Tolerant State & Idempotency
* Long tasks must withstand operating system interruptions (e.g., macOS App Nap, power management), network drops, and rate limits.
* Atomic, shard-level updates and real-time JSON checkpoint ledgers (`vertex_enricher_checkpoint.json`) allow tasks to be safely paused and resumed with zero data loss or duplication.

---

## 📋 Summary

Long task horizons transform the developer's role into that of **Chief Architect & Director**: establishing high-level scientific goals and safety contracts, while autonomous pipelines carry out the thousands of granular mathematical, structural, and visual verifications required to build a publication-grade physics encyclopedia.
