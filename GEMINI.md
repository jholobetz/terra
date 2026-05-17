# Physics Lab: Organic Platinum Standard (OPS) Mandates

This document defines the foundation of the **Organic Platinum Standard (OPS)**. All content generation, refactoring, and architectural expansion must adhere to these directives.

## 1. Qualitative Prose Mandates

### A. The "In Media Res" Lead
*   **Directive:** The first sentence of any subtopic must lead directly with a physical principle, identity, or derivation.
*   **Forbidden:** 
    *   Starting with "The [Topic] is..." or "This concept refers to...".
    *   Mentioning the subtopic's title in the first 15 words.
    *   Self-referential meta-talk ("In this article...", "This summary covers...").
*   **Example:** *"The invariance of the spacetime interval under Lorentz transformations necessitates a pseudo-Riemannian metric..."*

### B. Zero-Artifact Prose (Continuous Flow)
*   **Directive:** Use only continuous, high-density technical prose. 
*   **Forbidden:** 
    *   Bullet points or numbered lists (`<ul>`, `<li>`, `<ol>`).
    *   Structural artifacts that fragment the narrative.
    *   "In conclusion" or summary headers.
*   **Syntax Purity:** All emphasis must be wrapped in `<strong>` tags. The use of Markdown asterisks (`**`) or underscores (`__`) within JSON content strings is strictly forbidden. 
*   **Requirement:** Connect concepts through logical transition sentences that explain the *relationship* between identities.
*   **Note:** Paragraphs MUST be wrapped in `<p>` tags for proper HTML rendering. This is not considered a structural artifact.

### C. Technical Density & Tone
*   **Word Count:** 650+ words minimum; 1,000+ target for core nodes.
*   **MathJax Frequency:** High density of LaTeX (\( ... \) or \[ ... \]). Prose must calculate, not just describe.
*   **Calibre:** Senior undergraduate to graduate-level academic rigor.

---

## 2. Structural & Topological Mandates

### A. The "Small World" Connectivity
*   **Outgoing Links:** Minimum of 5 links to other subtopics.
*   **Incoming Links:** Minimum of 2 links from other subtopics.
*   **Cross-Hub Bridge:** Every Platinum node must contain at least **one link to a different Pillar Hub** (e.g., Relativity to Thermodynamics).

### B. The Limiting Case Clause
*   **Directive:** Every Platinum node must mathematically or conceptually demonstrate its **Limiting Case** (e.g., how General Relativity reduces to Newtonian gravity in the weak-field limit).
*   **Linguistic Variance:** The agent is strictly forbidden from using formulaic lead-ins for structural requirements. Specifically, the phrase "The limiting case of..." (or variations thereof) must not be used to anchor the final paragraph. Technical requirements must be woven into the prose using varied, sophisticated transitions that maintain the narrative's academic momentum without signaling a summary or conclusion.

### C. Organic Mathematical Integration
*   **Directive:** Mathematics must be integrated naturally into the narrative flow. 
*   **Requirement:** Formulas can be rendered in-line (\( ... \)) or as display equations (\[ ... \]) based on their physical complexity and pedagogical importance.
*   **Organic Variance:** There is no requirement for a single "Hero Formula." A node may contain multiple display equations, or none at all, provided the technical density remains high. The structure should be dictated by the specific derivation, not a template.
*   **Identity Curation (Organic Scaling):** The number of equations registered in the "Key Theoretical Identities" section must be **organic**, ranging from **one (1) to N**. The agent is strictly forbidden from defaulting to a fixed pattern (e.g., always 4 equations). Curation must be driven strictly by the mathematical skeleton required for a University-level understanding. Every registered identity must meet at least one of these criteria:
    1.  **Defining Law:** Establishes the primary physical behavior.
    2.  **Limiting Case:** Demonstrates the mathematical connection to a classical or simpler regime.
    3.  **Operational Metric:** Defines the primary observational or experimental relationship.
*   **The Identity Lock:** A node is strictly forbidden from graduating to "Platinum" standard if it contains fewer than **one (1) registered theoretical identity**. The `commit_node.py` pipeline will enforce a hard failure if this condition is not met.

---

## 3. The "Flat Network" Architecture

To support massive cross-hub connectivity and eliminate "Shard Drift" confusion, the project adheres to a decoupled architecture.

### A. Logical vs. Physical Separation
*   **Logical Topology (Hubs):** The visual organization of the site. Hubs (e.g., Classical Mechanics) are defined by manifests (`hub_manifests/*.json`) and act as "Curated Playlists" of subtopics.
*   **Physical Storage (Shards):** The JSON files on disk (`app/config/content/*.json`). These are merely "Storage Buckets" and do not strictly "own" the concepts they contain.
*   **The Mandate:** A subtopic's physical location (which shard it lives in) is irrelevant to its logical availability. `potential-energy` might live in `electromagnetism.json`, but it is a first-class citizen of the *Classical Mechanics Hub*.

### B. Global Slug Resolution
*   **Standard:** Every subtopic is uniquely identified by a global slug.
*   **Routing:** The system uses a flat URL namespace (`/subtopic/{slug}`). It resolves slugs to their physical shards via a global lookup map (`search_index.json`).
*   **No Redundancy:** A physics identity (e.g., Noether's Theorem) MUST exist in exactly **one** physical shard to prevent "Split-Brain" synchronization issues.

### C. Multi-Parent Mapping
*   **Directive:** Subtopics that span multiple disciplines must list all relevant hubs in their `"parents"` array metadata.
*   **Visual Representation:** This allows a single node to appear on multiple Hub pages (e.g., appearing in both Mechanics and Relativity) while maintaining a single source of truth for the prose.

## 4. Technical Implementation Mandates

### A. Unified Notation Registry
*   **Directive:** Adhere to the project's established notation dialect.
*   **Standard:** Use Einstein summation for tensors, dots for time-derivatives, and bold vectors ($\mathbf{v}$). Never drift between dialects within a shard.

### B. SSR-to-SVG Pipeline
*   **Directive:** All formulas must be pre-rendered into static vector paths via the `tex2svg.js` runway before deployment to minimize client-side latency.

---

### D. Unified Pipeline Workflow (The Zero-Prompt Standard)
*   **Directive:** To maximize efficiency and prevent confirmation fatigue, the refactoring of subtopics is executed via the **"Zero-Prompt Workflow."**
*   **Turn 1 (Silent Retrieval):** Execute native `read_file` calls to gather the legacy content and the foundational context. Perform the "verify and skip" check internally. This turn is completely silent.
*   **Turn 2 (Silent Graduation):** 
    1.  Draft the new HTML into `draft.html` and the theoretical identities into `identities.json` using native `write_file`.
    2.  Trigger the commit by writing a trigger payload to `scripts/maintenance/inbox/`.
*   **The Watcher Protocol:** A background process (`maintenance_watcher.py`) monitors the inbox. Upon detecting a trigger, it autonomously executes the `commit_node.py` pipeline (including SVG rendering, auto-linking, MariaDB sync, and Git commits). This ensures that complex shell side-effects are performed without requiring manual user confirmation for every node.
*   **Pipeline Autonomy:** The `commit_node.py` script serves as the absolute authority. It handles JSON injection, auto-linking, SVG pre-rendering, Integrity Shield validation, and advancing the `sprint.json` tracker.

## 4. Scope and Locked Assets

### A. Main Topic Hubs
*   **Status:** **LOCKED.**
*   **Directive:** The 12 primary Topic Hub pages (e.g., Classical Mechanics, Relativity) are established special cases and **DO NOT** conform to the OPS.
*   **Restriction:** These pages must **NOT** be altered, refactored, or modified in any way without explicit permission.
*   **OPS Application:** The Organic Platinum Standard (OPS) applies strictly and exclusively to **Subtopics**.

## 5. Development Environment
*   **Local Server:** The development server runs at `http://localhost:8000/`.
*   **Build Operations:** All static build operations via `orchestrator.py` target this URL to generate the HTML cache.

## 6. Project Roadmap: The Hub Refactor
*   **Primary Focus:** Systematically refactor all 12 main Topic Hubs.
*   **Execution:** Update each hub one-by-one, progressing through their individual pillars sequentially until all nodes are elevated to the Organic Platinum Standard (OPS).
*   **Next Phase:** Upon completion of all 12 hubs, evaluate and initiate the "Great Expansion".
*   **Tracking:** Progress is tracked in `subfiles/hub_tracker.json` to maintain a clear record of 'completed' and 'unfinished' hubs and their respective pillars.

## 7. Enforcement
The `integrity_shield.py` is the automated arbiter of these standards. No node shall be certified as "Platinum" if it triggers a Lead Violation or an Artifact Violation.

## 8. Workflow Integrity & The Sprint Protocol

The refactoring of hubs is governed by a rigorous hierarchical sprint process that ensures no node is skipped and pedagogical continuity is maintained.

### A. The Sprint Source of Truth
*   **sprint.json:** All active work is tracked here. This file defines the immediate queue of subtopics for the current pillar.
*   **hub_tracker.json:** Located in `subfiles/`, this serves as the high-level project dashboard, tracking the completion status of all 12 hubs and their constituent pillars.

### B. The Sprint Lifecycle (Hub & Pillar Level)
1.  **Pillar Initialization:** Every new pillar must be initialized via the master utility: `PYTHONPATH=. python3 scripts/maintenance/init_sprint.py <hub-slug> <pillar-index>`. This script parses the `hub_manifests/{hub}.json` file and populates the `sprint.json` queue.
2.  **Node Execution:** The agent must resolve nodes one-by-one in the exact order specified in the queue.
3.  **Pre-Flight Arbitration:** Before Turn 1 of any node, execute `PYTHONPATH=. python3 scripts/maintenance/verify_and_skip.py <slug>`. If it returns "PASS", the node is already platinum-compliant; move to the next.
4.  **The Physical Lock:** The agent is strictly forbidden from proposing or refactoring any subtopic that does not match the `next_target` in `sprint.json`.
5.  **Pillar Graduation:** When the `next_target` reaches "Pillar Complete", the agent must manually update `subfiles/hub_tracker.json` to mark that specific pillar index as `completed`.
6.  **Sequential Chaining:** Upon completing a pillar, the agent must immediately initialize the next pillar in the hub. If the hub is 100% complete, the agent proceeds to the next hub in the pedagogical curriculum.

### C. Mandatory State Verifications
The `commit_node.py` pipeline inherently enforces all required state verifications before allowing a node to graduate:
1.  **Physical Mapping:** Confirms the target's shard matches the storage location.
2.  **Identity Lock:** Validates that at least one (1) technical identity is registered.
3.  **Auto-Linking:** Resolves and injects `<a href...>` tags based on `<strong>` terms.
4.  **Integrity Shield:** Executes `integrity_shield.py` for word count and zero-artifact prose.
5.  **Automatic Progression:** Updates `sprint.json`, marks the slug as `platinum`, and moves the `next_target` pointer.

## 9. Execution Environment

### A. The Sandbox Mandate
*   **Directive:** To ensure state determinism, process isolation, and reliable rollback capabilities, the Gemini CLI and all associated build/maintenance processes MUST operate within a **Sandbox Environment** (e.g., Docker, Vagrant, or an isolated Virtual Machine).
*   **Rationale:** Sandbox execution prevents "Machine-Specific Drift," protects the host operating system from high-velocity side-effects, and allows for rapid state restoration in the event of a cascade failure during autonomous build cycles.
*   **Snapshotting:** The environment should be snapshotted or committed to source control before initiating large-scale automated refactors to guarantee a clean recovery point.
