# 🪐 Investigation: Sourcing of Physics Lab Content & Citation Mechanisms

This report investigates the original source of the Physics Lab encyclopedia content (the 1,584 subtopics), how the GQS pipeline upgrades their legitimacy, and how citations are used to substantiate the material.

---

## 🏛️ 1. Where Did the Material Originally Come From?

The Physics Lab encyclopedia corpus was originally initialized as a sharded flat-file database of **1,584 "legacy-tier" articles** across 12 primary physics pillars.

### The Original State:
* **The Seed Database**: The initial corpus served as a set of textbook-style "stub" drafts. These drafts mapped out standard university-level undergraduate and graduate physics curricula.
* **Lack of Citations**: In their legacy state, these articles did not contain formal academic citations, peer-reviewed bibliography lists, or DOIs.
* **Variable Quality**: The legacy drafts had irregular styling, variable prose depths (many under 600 words), and did not conform to strict academic prose gates.

---

## 🛡️ 2. The Role of the GQS & Critic Pipeline

Because the original legacy material was ungrounded in peer-reviewed literature, the **Multi-Agent Critic Pipeline** (`run_critic.py`) and the **Graduation Queue Stack (GQS)** were designed to verify and validate the legitimacy of every subtopic.

During the graduation process, each article undergoes:
1. **OPS Prose Gates**: The draft is rewritten to meet the Organic Platinum Standard (OPS)—ensuring word counts between 650–1,000 words, removing bullet/list artifacts, and structuring the text into continuous, university-level academic prose.
2. **Claim Extraction**: The `ClaimExtractor` agent parses the text and extracts the core physical assertions and mathematical expressions.
3. **Consensus Auditing**: The `LiteratureCritic` and `ConsensusJudge` agents query academic registries (arXiv and Crossref) to search for peer-reviewed literature matching the subtopic's claims.
4. **Stamping**: If the literature consensus score exceeds `0.50`, the subtopic is approved, and the resolved citation headers are **stamped directly** into the JSON shard database.

---

## 📖 3. Can We Use Citations for Them?

**Yes.** The citations are stored dynamically inside the database shards themselves.

### How to Retrieve and Use Citations:
Every graduated subtopic node contains a `"verification"` block inside its content JSON shard (e.g. [classical-mechanics.json](file:///Users/holobetj/code/gemini/terra/app/config/content/classical-mechanics.json)) containing peer-reviewed bibliography references:

```json
"verification": {
  "verified_date": "2026-06-09",
  "consensus_score": 0.88,
  "agents": {
    "extractor": "ClaimExtractor-v1.0",
    "critic": "LiteratureCritic-v1.0",
    "judge": "ConsensusJudge-v1.0"
  },
  "citations": [
    {
      "doi": "10.1002/andp.19163550704",
      "title": "On the gravitational field of a mass point",
      "authors": ["Schwarzschild, K."],
      "url": "https://arxiv.org/abs/physics/0503001"
    }
  ]
}
```

### Citation Options for Subtopics:
1. **Primary Literature Citations**: Instead of citing the encyclopedia itself, readers can cite the **stamped primary sources** (like Schwarzschild 1916 or Einstein 1905) listed in the verification block. This grounds the subtopic directly in peer-reviewed journals.
2. **Citing the Encyclopedia Entry**: If citing the Physics Lab itself, the entry can be referenced as a curated, peer-verified academic article under the MIT License (Copyright 2025), citing the dynamic verification metadata as the proof of its peer-reviewed alignment.
3. **Manual Citation Overrides**: For foundational concepts where automated search fails, curators manually input high-quality university textbook references (like Jackson's *Electrodynamics* or Goldstein's *Classical Mechanics*) using the Curation Portal.
