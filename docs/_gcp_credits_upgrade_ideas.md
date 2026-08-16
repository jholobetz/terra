# 🚀 GCP Free Credit Utilization Strategy & 10-Day Sprint Plan

> **Document Status**: Strategic Architecture Guide  
> **Budget**: ~$300.00 Google Cloud Platform Trial Credit (Expires in ~10 Days)  
> **Primary Objective**: Execute high-throughput batch compute and AI pipeline jobs to generate **permanent, repo-persisted assets, semantic search indices, and database quality upgrades** before credit expiration.

---

## Executive Summary

With a ~$300.00 one-time credit window expiring in ~10 days, ephemeral infrastructure (like running long-term idle servers) offers diminishing returns. Instead, the optimal strategy focuses on **high-ROI batch processing**, **large-scale LLM knowledge graph refinement**, and **pre-computed mathematical asset generation** that can be committed directly to Git or stored locally.

---

## 1. Top High-ROI Sprint Projects

```
                                 GCP $300 Credit Sprint (10 Days)
                                                │
         ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
         ▼                      ▼                               ▼                      ▼
  [Vertex AI LLM]       [text-embedding-004]           [High-Core Batch VM]     [Cloud Run & GCS]
 Full 9,655 Formula     Dense Vector Semantic          Parallel Headless Node   Serverless Staging
 Shard AI Audit Pass     Search & RAG Index            MathJax SVG Pre-Render   & Coldline Backups
         │                      │                               │                      │
         ▼                      ▼                               ▼                      ▼
  Permanent Shard       Local Vector Database           Instant Page Load      Permanent Free-Tier
  Cleanliness in Git     & Similarity Engine             Zero Client Lag        Live Staging URL
```

---

### Project 1: Full-Repository AI Formula & Shard Decorruption Pass (Highest ROI)
* **Objective**: Leverage Google **Vertex AI (Gemini 1.5 Pro / Gemini 2.0 Flash)** to audit, sanitize, and standardize all **9,655 formulas** across all 256 shard files (`shard_00.json` through `shard_ff.json`).
* **Tasks Executed**:
  1. **Prose TeX Sanitization**: Auto-clean fragmented dollar delimiters, unclosed math braces, and legacy Doxygen/form-feed artifacts (e.g., stray `\f`).
  2. **Semantic Variable Normalization**: Ensure every variable has calibrated SI units, descriptive physical names, and proper symbol types (`variable`, `constant`, `operator`).
  3. **Limiting Cases & Boundary Standardizations**: Auto-derive structured physical limit regimes (e.g., non-relativistic limit $v \ll c$, high-temperature limit $T \to \infty$, weak-coupling limit) for formulas currently lacking them.
  4. **Physical Classification**: Enhance conceptual definitions, symmetry origins, and intuitive summaries across all physics branches.
* **Deliverable**: Committed and validated JSON shard files in `app/config/content/formulas/`.

---

### Project 2: Dense Semantic Vector Embedding Index
* **Objective**: Generate 768/1536-dimensional dense vector embeddings using Vertex AI's `text-embedding-004` across all equations, variables, subtopics, and physical concepts.
* **Capabilities Unlocked**:
  1. **Concept-Based Search**: Natural language query search (e.g., *"two-electron bound state in Fermi sea"* $\to$ matches `Cooper Pair Binding Energy` even without exact keyword overlap).
  2. **Automated Knowledge Graph Clustering**: Compute pairwise cosine similarities across all 9,655 formulas to build high-accuracy subcomponent graphs and family trees.
  3. **RAG Integration**: Power instant AI explanation sidecars with grounded context retrieval.
* **Deliverable**: `app/config/physics_embeddings.json` or an embedded SQLite vector store (`sqlite-vss`).

---

### Project 3: High-Core Parallel Batch Pre-Rendering of MathJax SVGs
* **Objective**: Spin up a 60-vCPU Compute Engine Spot Instance (`c2-standard-60` or `t2d-standard-60`) for 3–5 hours (approx. $10–$15 credit consumption).
* **Tasks Executed**:
  1. Headless Node.js MathJax worker pool renders all 9,655 LaTeX equations into optimized, self-contained SVG vectors.
  2. Populate the `equation_svg` column in the MariaDB `formulas` table.
  3. Export static SVG asset packs for offline or CDN delivery.
* **Benefit**: Reduces client-side CPU overhead to zero and ensures instantaneous equation rendering across mobile and desktop devices.

---

### Project 4: Cloud Run Serverless Staging & Automated Coldline Backups
* **Objective**: Deploy a live, scalable staging instance of Terra that remains **$0.00/month** even after the 10-day trial expires.
* **Architecture**:
  1. **Cloud Run**: Serverless container (PHP 8.2 + Nginx) scaling to 0 when idle (fits within GCP's permanent Always Free Tier: 2M requests/month free).
  2. **Cloud Storage (Coldline/Archive)**: Automated snapshot bucket archiving database dumps and shard releases with lifecycle deletion policies.
  3. **Cloud Build**: Automated CI/CD running the 15,646-link Integrity Shield on every commit.

---

### Project 5: Physics Dataset Export & Publication Artifacts
* **Objective**: Compile and export clean, open datasets from Terra's knowledge graph.
* **Deliverables**:
  1. **Hugging Face Dataset**: Structured JSONL benchmark for AI equation reasoning and physical unit consistency.
  2. **Physics Cheat Sheets & Reference Books**: Vector-rendered PDF equation reference compendia organized by domain (Quantum Mechanics, Thermodynamics, General Relativity, Optics, etc.).

---

## 2. Estimated Credit Budget Breakdown

| Initiative | GCP Service / Resource | Estimated Duration | Projected Cost |
| :--- | :--- | :--- | :--- |
| **1. Full Shard AI Audit** | Vertex AI (Gemini 1.5 Pro / Flash) | 12–24 Hours Batch | ~$80.00 – $120.00 |
| **2. Vector Embeddings** | Vertex AI (`text-embedding-004`) | 1–2 Hours Batch | ~$15.00 – $30.00 |
| **3. SVG Batch Pre-Rendering** | Compute Engine `c2-standard-60` Spot | 4–6 Hours | ~$12.00 – $20.00 |
| **4. Cloud Run Staging & CI** | Cloud Run + Cloud Build + GCS | 10 Days Active | ~$5.00 – $10.00 |
| **5. Model Distillation & Testing** | Vertex AI Model Tuning / Eval | 1–2 Runs | ~$50.00 – $80.00 |
| **Buffer / Safeguard** | Billing alerts set at $250.00 | — | Remaining Credit |
| **Total** | | | **~$162.00 – $260.00** |

---

## 3. Implementation Workflow

### Phase 1: Authentication & Setup (Day 1)
1. Initialize Google Cloud project with billing enabled.
2. Authenticate locally:
   ```bash
   gcloud auth application-default login
   gcloud config set project <YOUR_PROJECT_ID>
   ```
3. Set budget alerts at **$50**, **$150**, and **$250** via Google Cloud Billing Console.

### Phase 2: Batch AI Shard Refinement & Embeddings (Days 2–5)
1. Execute Python batch script iterating over `app/config/content/formulas/*/*.json`.
2. Generate embeddings and save `physics_embeddings.json`.
3. Commit clean shards to local git repository.

### Phase 3: SVG Rendering & Database Sync (Days 6–7)
1. Run parallel headless MathJax rendering job on Compute Engine Spot VM.
2. Sync `equation_svg` to production MariaDB.

### Phase 4: Staging Deployment & Cleanup (Days 8–10)
1. Push container to Cloud Run.
2. Backup all outputs and clean up any persistent disks before credit expiration.
