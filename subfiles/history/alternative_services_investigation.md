# 🪐 Alternative Verification Services for the Critic Engine

This report investigates other academic, scientific, and open literature databases that can be integrated into the **Physics Lab Literature Critic Engine** to verify the legitimacy of subtopics and compile peer-reviewed citation listings.

---

## 🏛️ 1. Domain-Specific Scientific Databases

For advanced physics subtopics, querying general academic indexes can produce noise. Integrating specialized, domain-specific databases offers high-accuracy, high-relevance citations:

### A. INSPIRE-HEP (High-Energy Physics & Standard Model)
* **Description**: Run by CERN, DESY, Fermilab, IHEP, and SLAC, INSPIRE-HEP is the primary database for High-Energy Physics, Particle Physics, Quantum Field Theory, and Cosmology.
* **API Details**: Free, open REST API (`https://inspirehep.net/api/literature`) requiring **no authentication tokens**.
* **Use Case**: Ideal for the `standard-model.json`, `quantum-physics.json`, and `theoretical-physics.json` shards.
* **Query Example**: `https://inspirehep.net/api/literature?q=find+t+majorana+neutrino`

### B. NASA ADS (Astrophysics Data System)
* **Description**: Run by the Smithsonian Astrophysical Observatory (SAO) under a NASA grant. It is the gold-standard index for Astronomy, Astrophysics, Cosmology, and general Physics literature.
* **API Details**: Free REST API (`https://api.adsabs.harvard.edu/v1/search/query`) requiring a free developer API token.
* **Use Case**: Indispensable for the `astrophysics.json` and `relativity.json` shards.

---

## 📚 2. General Academic Graphs

General academic search engines index across all disciplines, providing excellent coverage for multidisciplinary topics and mathematical physics:

### A. Semantic Scholar (Allen Institute for AI)
* **Description**: A free, AI-powered academic search engine indexing over 200 million papers.
* **API Details**: Free, structured REST API. Highly recommended over Google Scholar because it does not block bots and provides programmatic access to paper abstracts, fields of study, and citation counts.
* **Use Case**: General-purpose backup for all shards. Excellent for generating abstract-based semantic embeddings.

### B. OpenCitations
* **Description**: An open infrastructure organization providing free, unrestricted access to global academic citation data.
* **API Details**: Free, token-less REST API (`https://opencitations.net/index/coci/api/v1`) mapping connections between DOIs.
* **Use Case**: Can be used to verify the academic impact/consensus of a paper once retrieved.

---

## 📖 3. Textbook & Monograph Registries (ISBN APIs)

Foundational undergraduate topics (like *Vector Fields* or *Conservation of Momentum*) are rarely the subject of modern journal papers but are covered in standard physics textbooks. Querying textbook registries allows us to cite canonical monographs:

### A. Open Library (Internet Archive)
* **Description**: An open, editable library catalog database.
* **API Details**: Free, token-less REST API (`https://openlibrary.org/api/books`).
* **Use Case**: Ideal for finding canonical textbook entries (like Griffiths' *Introduction to Electrodynamics* or Jackson's *Classical Electrodynamics*).

### B. Google Books API
* **Description**: Indexes millions of scanned books.
* **API Details**: Free REST API (`https://www.googleapis.com/books/v1/volumes`) with high search limits.
* **Use Case**: Retrieves exact ISBNs, publisher names, and author credits for standard physics literature references.

---

## 🗃️ 4. Overview of Service Attributes

| Service Name | Primary Focus | API Token Required? | Target Shards |
| :--- | :--- | :---: | :--- |
| **INSPIRE-HEP** | Particle Physics & QFT | No | `standard-model.json`, `quantum-physics.json` |
| **NASA ADS** | Astrophysics & Relativity | Yes (Free) | `astrophysics.json`, `relativity.json` |
| **Semantic Scholar** | General Academic / AI | No | General validation backup |
| **Open Library** | Textbook Catalogs (ISBN) | No | Foundational/pedagogical topics |
| **Google Books** | Book Metadata & Textbooks | No | Textbook-level reference stamping |
