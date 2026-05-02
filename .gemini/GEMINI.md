# Physics Lab: Foundation Mandates & Technical Standards

This document serves as the **Supreme Authority** for all architectural, stylistic, and procedural decisions in the Physics Lab project. All AI assistants MUST adhere to these standards to maintain the "Gold Standard" of a university-level digital encyclopedia.

---

## 1. Architectural Mandates: The Sharded Knowledge Graph

To ensure O(1) performance and context efficiency as we scale to 18,000 subtopics, the project uses a **Sharded Relational JSON** model.

### 1.1 Data Structure (`app/config/content/`)
The database is sharded into modular JSON files by top-level category:
- `categories.json`: Defines the 12 major physics modules.
- `formulas.json`: The global registry of 4,600+ unique mathematical identities (Platinum Standard).
- `constants.json`: Normalized physical constants ($\hbar, c, G$, etc.).
- `entities.json`: Historical figures and research facilities.
- `search_index.json`: Master metadata map for lazy loading and discovery.
- `[category-slug].json`: Subtopic shards containing 150-500 topics each.

### 1.2 Relational Integrity
- **Formulas:** Never hardcode a formula object. Reference it by ID: `"formula_ids": ["schrodinger-identity-8c31"]`.
- **Hierarchy:** Use the `parents` array (Poly-hierarchy). A topic can belong to multiple categories: `"parents": ["quantum-mechanics", "theoretical-physics"]`.
- **Entities:** Historical names (Einstein, Noether) are automatically linked via the `orchestrator.py` entity linking logic using `entities.json` aliases.
- **Constants:** Use standardized LaTeX symbols from `constants.json` to ensure sitewide numerical consistency.

---

## 2. The "Blob Strategy" for Context Efficiency

All AI assistants MUST adhere to these rules to prevent token exhaustion:
1.  **Local Orchestration:** Treat data shards as local "blobs." Never read or transmit files > 1MB into the chat history.
2.  **Server-Side Processing:** Perform all batch updates, interlinking, and validation using Python scripts (`orchestrator.py`, `integrity_shield.py`) on the server.
3.  **Surgical Peeking:** Use `grep_search` or `read_file` with precise line ranges to inspect data.
4.  **Batch Compression:** Use sub-agents to draft content and "blob" the final validated objects into shards in a single turn.

---

## 3. Governance & Quality Gating

NO change is considered complete until it passes the **Integrity Shield**.

### 3.1 The Integrity Shield (`integrity_shield.py`)
Mandatory checks before any commit:
1.  **Schema Validation:** Every shard must pass `app/config/subtopic.schema.json`.
2.  **Navigational Health:** 0 Broken Links (100% resolution required).
3.  **Relational Health:** Every Formula ID must resolve in the registry.
4.  **Technical Density:** Content must meet the "University Level" score (LaTeX-to-word ratio).
5.  **Historical Integrity:** All key entities from `entities.json` must be linked.
6.  **Protected Slug Isolation:** No protected main topic slugs may exist within subtopic shards.

### 3.2 Main Topic Immutability
The 12 core topics are **Locked**.
- **Source of Truth:** Content lives exclusively in `app/config/content/topics/[slug].json`. 
- **Registry Hygiene:** `categories.json` MUST only contain metadata (title and shard path). The orchestrator automatically strips content from this file during save to prevent "split-brain" synchronization errors.
- **Save Safeguard:** The `orchestrator.py` will refuse to overwrite core topic shards unless `unlock_protected=True` is explicitly passed.

### 3.3 Post-Update Validation
After syncing, verify live rendering using `curl`:
```bash
# Check for MathJax (exactly one backslash in final HTML) and link hygiene
curl -s http://localhost/physics/subtopic/slug | grep -E "\\\\\\(|\\\\\\\\\\["
```

---

## 4. Content Quality Standards: The "Platinum Standard"

- **Technical Scope:** Every subtopic must contain **4 to 8 distinct sections** of rigorous technical explanation, depending on the breadth of available academic material. This flexibility ensures depth for complex theories while maintaining integrity for specialized niche topics.
- **Factuality & Integrity:** All content MUST be derived from established physical principles and academic consensus. **Zero Tolerance for Hallucinations**: AI assistants must not invent terminology, historical dates, or physical relationships. If reliable data for a section is unavailable, the section count should be reduced toward the minimum threshold (4) rather than padded with speculative content.
- **Main Topic Layout:** Main topics must use the bulleted layout with high verbosity (**3-4 sentences per bullet point**) to provide deep technical context.
- **MathJax 3 Configuration:** 
    - **Delimiters:** Use `\\(` and `\\)` for inline, and `\\\\[` and `\\\\]` for display-style equations in raw JSON content.
    - **JSON Escaping:** TeX commands starting with JSON escape characters (e.g., `\\nu`, `\\rho`, `\\tau`) MUST be double-escaped in the shard file to prevent "eaten" backslashes.
    - **No HTML Escaping:** Equations in formula cards MUST NOT be passed through `htmlspecialchars()`, as alignment characters like `&` are essential for MathJax parsing.
- **Linking Convention:** Use `<strong><a href="/physics/subtopic/slug" class="subtopic-link">Title</a></strong>` for internal subtopic links and `/physics/topic/slug` for main modules.
- **No Linguistic Artifacts:** Zero tolerance for doubled words or "AI Fluff."

---

## 5. Discovery & Aesthetics

### 5.1 The "See Also" Engine
Horizontal discovery is automated. The site uses `search_index.json` to suggest "Related Concepts" based on keyword overlap.

### 5.2 Abstract Diagram Engine
Every subtopic features a stylized visual aid generated by `public/js/diagram_engine.js`.
- Configuration is stored in the subtopic JSON: `"visual_config": {"type": "wave", "color": "#64ffda", "complexity": 7}`.

---

## 6. Performance & Static-First Deployment

- **Lazy Loading:** The PHP Controller MUST only load the specific JSON shard required for the requested slug (O(1) access via `search_index.json`).
- **Static Pre-rendering:** For production-grade performance, all subtopics should be pre-rendered into static HTML.
    - **Command:** `python3 -c "from orchestrator import PhysicsOrchestrator; PhysicsOrchestrator().build()"`
    - **Logic:** The site serves the `.html` cache if available, bypassing all JSON/Logic overhead.

---

## 7. Expansion Workflow

To create new content, follow the **Assembly Line**:
1.  **Identify:** Select a term from `subfiles/expansion_backlog.json`.
2.  **Category Check:** Verify if the term already exists as a Main Topic in `app/config/content/categories.json`.
    - **If it is a Main Topic:** Upgrade the existing entry in `categories.json` to "Platinum Standard" depth.
    - **If it is a New Concept:** Add it as a subtopic to the relevant category shard.
3.  **Brief:** Run `python3 pack_context.py [Term] [Parent]` to generate the AI prompt.
4.  **Generate:** Task a sub-agent with the research brief.
5.  **Ingest:** Use `orchestrator.add_subtopic()` to shard and link.
6.  **Shield:** Run `integrity_shield.py`.
7.  **Commit:** `orchestrator.save()` handles the automatic Git commit.

---

## 8. Logical Taxonomy & Module Boundaries

All content must be categorized into one or more of the 12 primary modules:
1. Classical Mechanics, 2. Electromagnetism, 3. Relativity, 4. Quantum Physics, 5. The Standard Model, 6. Astrophysics & Cosmology, 7. Theoretical Physics, 8. Philosophy of Physics, 9. Thermodynamics & Statistical Mechanics, 10. Condensed Matter Physics, 11. Fluid Dynamics & Nonlinear Systems, 12. Mathematical Methods in Physics.

---

## 9. Strategic Priority: Consolidation First (Foundational Mandate)

To ensure long-term scalability and institutional-grade quality, the project follows a **Density-First** strategy. Volume expansion is strictly gated by the health of the existing graph.

- **Refactoring Mandate:** Technical density (Latex-to-word ratio) and conceptual depth of existing stubs MUST be prioritized over the creation of new subtopics.
- **The 10% Expansion Gate:** The "Great Expansion" of new terms from the backlog is **PROHIBITED** unless the `integrity_shield.py` reports that "Non-Technical" or "Low-Depth" warnings constitute **less than 10%** of the total subtopic pool.
- **Consistency over Volume:** A smaller, "Platinum Standard" encyclopedia is preferred over a larger, shallow one. Every refactoring turn must aim for a Technical Density Score > 50.

---

## 10. Technical Consolidation: The RefactorEngine Workflow

The `refactor_engine.py` is the **exclusive authorized pathway** for batch subtopic upgrades. Manual shard editing is deprecated to prevent "Technical Debt" and "Formula Drift."

### 10.1 Automated Quality Enforcement
- **Scoring Formula:** `(MathJax_Count * 15) + (Technical_Keyword_Score)`. Any content falling below 50 is flagged for immediate refactoring.
- **Context Preservation:** The engine mandates the preservation of established navigational pathways. AI assistants are prohibited from discarding existing internal links during refactoring.

### 10.2 "Bulletproof" Execution Standards
All batch updates must follow the atomic ingestion pipeline:
1.  **Local Formula Definition:** Sub-agents MUST define new equations in a local `formulas` array.
2.  **Automated Sanitization:** The engine must handle all MathJax backslash escaping to ensure JSON validity.
3.  **Atomic Ingestion:** Shards and the global formula registry must be updated simultaneously via `ingest_subtopic_platinum`.
4.  **Zero-Error Validation:** Any batch that introduces a "Broken Link" or "Broken Formula" error MUST be reverted or fixed before the next turn.

---

## 11. Environment & Deployment

To maintain testing consistency across sessions, all automation and validation tools must target the authorized live environment.

- **Primary Test Server:** `http://172.16.1.208`
- **Build Protocol:** The `orchestrator.build()` method uses this address to pre-render static HTML. Any change to the server IP must be updated here first to ensure tool synchronization.

