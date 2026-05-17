# Physics Lab: Organic Platinum Standard (OPS) & Technical Foundations

This document is the **Supreme Authority** for all architectural, stylistic, and procedural decisions in the Physics Lab project. All AI assistants MUST adhere to these mandates to maintain the "Gold Standard" of a university-level digital encyclopedia.

---

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
    *   Structural artifacts that fragment the narrative (e.g., summary headers).
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
*   **Link Preservation:** When refactoring, AI assistants MUST first extract all internal links and ensure they are contextually re-integrated.

### B. The Limiting Case Clause
*   **Directive:** Every Platinum node must mathematically or conceptually demonstrate its **Limiting Case** (e.g., how General Relativity reduces to Newtonian gravity).
*   **Linguistic Variance:** The agent is strictly forbidden from using formulaic lead-ins like "The limiting case of...". Technical requirements must be woven into the narrative organically.

### C. Organic Mathematical Integration
*   **Identity Curation (Organic Scaling):** The number of equations registered in the "Key Theoretical Identities" section must be **organic (1 to N)**. Curation must be driven strictly by the mathematical skeleton required for a University-level understanding. Every registered identity must meet at least one of these criteria:
    1.  **Defining Law:** Establishes the primary physical behavior.
    2.  **Limiting Case:** Demonstrates the connection to a classical or simpler regime.
    3.  **Operational Metric:** Defines the primary observational or experimental relationship.
*   **The Identity Lock:** A node is strictly forbidden from graduating to "Platinum" standard if it contains fewer than **one (1) registered theoretical identity**.

---

## 3. The Sharded Knowledge Graph Architecture

To ensure O(1) performance and context efficiency, the project uses a **Sharded Relational JSON** model.

### A. Physical Storage (Shards)
*   The database lives in `app/config/content/`. Shards (e.g., `astrophysics.json`) are "Storage Buckets" and do not strictly "own" the concepts they contain.
*   **Global Slug Resolution:** Every subtopic is uniquely identified by a global slug. The system resolves slugs via a global lookup map (`search_index.json`).
*   **No Redundancy:** A physics identity MUST exist in exactly **one** physical shard.

### B. Logical Topology (Hubs)
*   Hubs are "Curated Playlists" defined by manifests (`hub_manifests/*.json`). 
*   **Multi-Parent Mapping:** Subtopics spanning multiple disciplines must list all relevant hubs in their `"parents"` array metadata.

### C. Unified Notation Registry
*   Adhere to the project's established notation dialect: Einstein summation for tensors, dots for time-derivatives, and bold vectors ($\mathbf{v}$).

---

## 4. Operational Protocols

### A. The "Zero-Prompt" Workflow
To maximize efficiency, the refactoring of subtopics is executed via a background watcher protocol:
1.  **Turn 1 (Silent Retrieval):** Execute native `read_file` calls to gather legacy content. Perform the "verify and skip" check internally.
2.  **Turn 2 (Silent Graduation):** 
    - Draft new HTML into `draft.html` and identities into `identities.json`.
    - Trigger the commit by writing a trigger payload to `scripts/maintenance/inbox/`.
3.  **The Watcher Protocol:** `maintenance_watcher.py` autonomously executes `commit_node.py` (SVG rendering, auto-linking, MariaDB sync, and Git commits).

### B. Structured Retrieval
*   Agents MUST use `PYTHONPATH=. python3 scripts/maintenance/retrieve_concept.py <slug>` to examine content. NEVER use `grep` or line-based `read_file` for content discovery, as this causes context bloat and JSON corruption risk.

### C. Execution Environment (Sandbox)
*   All build and maintenance processes MUST operate within a **Sandbox Environment** (Docker/Vagrant) to ensure state determinism and process isolation.

---

## 5. Scope and Gating

### A. Main Topic Hubs
*   **Status:** **LOCKED.** The 12 primary Topic Hub pages are special cases and **DO NOT** conform to the OPS. They must NOT be altered without explicit permission.

### B. The Integrity Shield
*   `integrity_shield.py` is the automated arbiter. No node graduates if it triggers a Lead Violation, an Artifact Violation (e.g., `**`), or falls below the word count threshold.

### C. Project Roadmap
*   Refactor the 12 main Topic Hubs one-by-one, progressing through individual pillars sequentially. Progress is tracked in `subfiles/hub_tracker.json`.
