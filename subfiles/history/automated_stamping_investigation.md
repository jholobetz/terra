# 🪐 Automated Literature Stamping & API Flood Analysis

This report investigates the feasibility, network impact, and blocking risks of automating the "Stamp" citation process sitewide for all 1,584 registered reference topics in the Physics Lab encyclopedia.

---

## 📊 1. Quantitative Request Breakdown

Currently, the literature cache [literature_cache.json](file:///Users/holobetj/code/gemini/terra/app/config/ref_data/literature_cache.json) has only **12 entries** cached. 

To stamp all 1,584 registered reference subtopics, the system must process:
* **Total Subtopics**: 1,584
* **Pre-cached Subtopics**: 12
* **Uncached Subtopics requiring live API calls**: 1,572

For each uncached subtopic, the critic agent (`MultiAgentCritic.get_literature` in `run_critic.py`) makes **two separate HTTP GET requests**:
1. One request to the **arXiv API** (`export.arxiv.org`).
2. One request to the **Crossref REST API** (`api.crossref.org`).

$$\text{Total HTTP Requests} = 1,572 \times 2 = 3,144 \text{ requests}$$

---

## ⚡ 2. API Policies & Rate Limit Boundaries

Running an automated loop to fire 3,144 requests will interact with the external APIs as follows:

### A. arXiv API Limits (`export.arxiv.org`)
* **Official Rate Limit**: **Max 1 request every 3 seconds** (and no more than 4 concurrent connections).
* **Enforcement**: Extremely strict. arXiv utilizes automated firewall rules that dynamically block/blacklist IP addresses if requests are sent too rapidly.
* **Unthrottled Run Impact**: Running a loop without delay will trigger the arXiv firewall almost immediately (typically after 10–20 rapid requests), resulting in connection resets and a temporary or permanent IP blacklist.

### B. Crossref REST API Limits (`api.crossref.org`)
* **Official Rate Limit**: Dynamic rate-limiting header based. Typically permits up to **50 requests per second**.
* **Polite Pool Usage**: The critic agent uses a contact email header (`mailto:admin@physicslab.org`), which places it in Crossref's "Polite Pool," yielding higher reliability.
* **Unthrottled Run Impact**: While Crossref is more forgiving than arXiv, sending 1,572 rapid requests can still trigger rate-limit blocks (HTTP 429) or gateway timeouts (HTTP 504 / 503).

---

## ⏱️ 3. Execution Feasibility Scenarios

| Scenario | Execution Strategy | Est. Duration | Outcome |
| :--- | :--- | :--- | :--- |
| **1. Unthrottled Concurrent** | Fire all requests asynchronously. | < 30 seconds | ❌ **Immediate Failure**. arXiv firewall blocks the IP address in seconds; most shards fail to verify. |
| **2. Unthrottled Sequential** | Loop sequentially with no sleep. | ~5–10 minutes | ❌ **Failure**. arXiv blocks the IP after the first ~15 topics; remainder of loop returns empty arrays. |
| **3. Throttled (3s Delay)** | Sleep 3.5 seconds between each subtopic. | ~1.5 hours | ⚠️ **Risk of Transient Failures**. High latency; any single API timeout, connection reset, or transient error can disrupt the long-running script. |

---

## 💡 4. Recommended Best Practice Architecture

To safely stamp the remaining subtopics without flooding or getting blacklisted, we recommend the following approach:

1. **Incremental Sprints (The GQS Pipeline)**:
   * Do not stamp all 1,584 nodes at once. Use the GQS sprint pipeline (`.venv/bin/python3 scripts/maintenance/run_gqs_sprint.py --count <N>`) to graduate and stamp subtopics in controlled batches of $N = 10 \text{ to } 30$ at a time.
2. **Implement Rate Limiting and Backoff in the Agent**:
   * Modify `run_critic.py` to sleep for `3.5 seconds` between calls when running live queries.
   * Add a retry mechanism with exponential backoff (e.g., waiting $2^k$ seconds after an HTTP 429 or connection error).
3. **Pre-Seeded/Shared Cache**:
   * Perform cache harvesting in a separate environment (e.g., on a local machine over a few days), compile the complete [literature_cache.json](file:///Users/holobetj/code/gemini/terra/app/config/ref_data/literature_cache.json), and commit the completed cache file. Once committed, the sitewide stamp script can run 100% offline at disk speeds without triggering a single external API request.
