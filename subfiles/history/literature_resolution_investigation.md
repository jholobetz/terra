# 🪐 Literature Resolution Fail-Safes for Valid Physics Subtopics

This document investigates the scenario where a valid physics subtopic fails to resolve academic literature citations automatically via arXiv or Crossref APIs, and outlines both current system workarounds and hypothetical architectural solutions.

---

## 🔍 1. Why Do Valid Subtopics Fail to Resolve?

A subtopic can be academically valid and mathematically rigorous but still fail external literature lookups due to three main causes:

1. **Pedagogical/Elementary Topics**:
   * **Example**: Topics like *Vector Addition of Velocities*, *Conservation of Momentum*, or *Vector Fields*.
   * **Cause**: These are foundational, early-undergraduate physics concepts. They are universally accepted textbook material. Modern academic research databases like arXiv or Crossref index novel research publications, not elementary textbooks, leading to zero or low-similarity results.
2. **Niche, Historical, or Interpretive Terminology**:
   * **Example**: *Maxwell's Ether Theory*, *Humean Laws*, or the *Past-Hypothesis*.
   * **Cause**: Historical terms or specific philosophical interpretations are debated in text formats that do not align with the strict abstract vocabularies of modern peer-reviewed publications.
3. **Technical & Network Bottlenecks**:
   * **Cause**: Rate-limiting (HTTP 429), API server outages (HTTP 503), or sandboxed network environments block outbound API requests, resulting in empty responses.

---

## 🛠️ 2. Current Mitigation Mechanisms in the Code

The Physics Lab project already includes two built-in escape hatches to resolve these topics manually without altering database integrity checks:

### A. Pre-Seeding the Literature Cache (`literature_cache.json`)
* **How it works**: The critic agent (`scripts/maintenance/run_critic.py`) checks [literature_cache.json](file:///Users/holobetj/code/gemini/terra/app/config/ref_data/literature_cache.json) before querying external APIs.
* **Workaround**: Developers can manually insert custom paper metadata under the subtopic's slug in the cache:
  ```json
  "vector-addition-velocities": [
    {
      "title": "On the Electrodynamics of Moving Bodies",
      "authors": ["Einstein, Albert"],
      "doi": "10.1002/andp.19053221004",
      "abstract": "The paper deriving the relativistic addition of velocities...",
      "url": "https://doi.org/10.1002/andp.19053221004"
    }
  ]
  ```
* **Result**: The critic pipeline will run successfully offline using this pre-seeded data, calculate similarity scores, and stamp the node.

### B. Curation Portal Manual Overrides (`+ Add Citation Manually`)
* **How it works**: The critic panel view ([critic.php](file:///Users/holobetj/code/gemini/terra/app/views/physics/admin/critic.php)) provides an `✏️ Edit` button leading to a modal where administrators can click `+ Add Citation Manually`.
* **Workaround**: Curators can manually specify the citation details (Title, Authors, DOI, URL).
* **Result**: Submitting the form hits the `/physics/admin/api/update-verification` endpoint managed by `PhysicsController.php`. It writes these citations directly to the subtopic's shard and stamps the node with:
  * `consensus_score: 1.00`
  * `agents: ManualEditor-v1.0`
  This bypasses the automated agent consensus score checks entirely.

---

## 🚀 3. Hypothetical & Architectural Improvements

To make the consensus engine more resilient and reduce manual curation overhead, we could implement the following systems:

### 📚 1. Textbook and Book Registry Integration
* **Concept**: Foundational physics is best cited via standard textbooks (e.g., Griffiths' *Electrodynamics*, Jackson's *Classical Electrodynamics*, Goldstein's *Classical Mechanics*).
* **Implementation**: Integrate APIs like Google Books or Open Library (ISBN search). If arXiv/Crossref return no research articles, fallback to query textbook databases for chapter mappings, retrieving stable ISBN citations instead of DOIs.

### 🌐 2. Wikipedia API Reference Extraction
* **Concept**: Wikipedia's physics entries are community-peer-reviewed and contain comprehensive bibliography sections listing primary literature sources.
* **Implementation**: Write a scraper/API client that queries the Wikipedia entry for the subtopic slug, extracts the references listed in the bibliography, and feeds those citations/DOIs directly into the consensus judge.

### 🧠 3. Query Expansion & Semantic Embeddings
* **Concept**: Keyword searches on Crossref/arXiv are often too narrow or use literal slug terms.
* **Implementation**:
  * Use an LLM to generate semantic synonyms or alternative search queries (e.g., converting `"variable-mass"` to `"systems with variable mass accrete momentum"`).
  * Shift from literal string matching to vector similarity searches (e.g., via the Semantic Scholar API).

### ⚖️ 4. Adaptive Consensus Thresholds
* **Concept**: Currently, `run_critic.py` enforces a rigid consensus score floor of `0.50`.
* **Implementation**: Detect the type of subtopic. If it belongs to a qualitative or conceptual domain (like `philosophy-of-physics.json`), dynamically lower the consensus threshold to `0.35` or automatically waive primary research citations in favor of tertiary educational resources.

### 🗃️ 5. Local Reference Library Shard (`library.json`)
* **Concept**: Maintain a local JSON shard containing standard references for the 100 most common undergraduate physics topics.
* **Implementation**: Create a `library.json` file on disk. When a slug is requested, the system checks this local library first before performing any API requests.
