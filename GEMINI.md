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

### C. Organic Mathematical Integration
*   **Directive:** Mathematics must be integrated naturally into the narrative flow. 
*   **Requirement:** Formulas can be rendered in-line (\( ... \)) or as display equations (\[ ... \]) based on their physical complexity and pedagogical importance.
*   **Organic Variance:** There is no requirement for a single "Hero Formula." A node may contain multiple display equations, or none at all, provided the technical density remains high. The structure should be dictated by the specific derivation, not a template.

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

### D. Sprint V3 Protocol (Sectional Assembly)
*   **Directive:** For complex or high-priority nodes, utilize sectional generation to prevent turn-limit timeouts.
*   **Workflow:**
    1.  **Lead Draft:** Generate the "In Media Res" lead independently.
    2.  **Core Expansion:** Flesh out technical prose and MathJax identities.
    3.  **Validation Check:** Immediate local validation with `integrity_shield.py`.
    4.  **Correction:** If rejected, only refactor the specific violating section.

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
*   **The Sprint Source of Truth:** All refactoring sequences must be governed by a `sprint.json` file in the root directory. This file is initialized at the start of every pillar by a literal read of the relevant `hub_manifests/{hub}.json`.
*   **The Physical Lock:** The agent is strictly forbidden from proposing or refactoring any subtopic that does not match the `next_target` defined in `sprint.json`.
*   **Mandatory State Verifications:** Before certifying a node as "Platinum" in the tracker, the following four checks must be performed:
    1.  **Physical Mapping Check:** Confirm that the target's `shard` in the tracker matches the storage location defined in `app/config/content/search_index.json`.
    2.  **Link-Check Audit:** Run a verification script/command to ensure every `subtopic-link` created in the prose exists as a valid slug in the search index.
    3.  **Integrity Shield Certification:** Execute `integrity_shield.py` and confirm a "PASS" result for word count, lead compliance, and zero-artifact prose.
    4.  **Parentage Parity:** Verify that the target node's `"parents"` array in the JSON shard includes the Hub slug currently being graduated.
*   **The Update Cycle:** Every successful elevation must be immediately followed by an update to `sprint.json`, marking the slug as `platinum` and moving the `next_target` pointer to the literal next item in the manifest array.
