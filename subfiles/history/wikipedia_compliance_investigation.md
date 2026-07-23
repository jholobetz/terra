# 🪐 Polite & Compliant Wikipedia Integration for the Critic Engine

This report investigates the architectural patterns, rate limits, and compliance boundaries required to integrate Wikipedia verification into the **Physics Lab Literature Critic Engine** without violating terms of service or overloading Wikimedia’s infrastructure.

---

## 🏛️ 1. Wikipedia API Usage Policies & ToS Compliance

Wikimedia Foundation maintains highly open access to their content but enforces strict guidelines to prevent automated scripts from degrading service for human users:

1. **The User-Agent Mandate (Strictly Required)**:
   * **Rule**: All scripts/bots must supply a descriptive `User-Agent` header. It must include the application name, version, and contact email or URL (e.g. `PhysicsLabCritic/2.0 (admin@physicslab.org)`).
   * **Consequence**: Requests with generic headers (like Python’s default `urllib/3.x` or `curl`) are systematically throttled, blocked, or challenged by Wikimedia's security filters (WAF).
2. **API vs. Raw Scraping**:
   * **Rule**: Automated bots should **never** scrape the human-facing website (`https://en.wikipedia.org/wiki/Topic`).
   * **Reason**: HTML pages are heavy and bypassing caching layers to crawl them places severe load on Wikipedia's backend application servers. Instead, scripts must query the dedicated **MediaWiki API** (`https://en.wikipedia.org/w/api.php`) or the **REST API** (`https://en.wikipedia.org/api/rest_v1/`).
3. **Rate Limits**:
   * While the official WMF REST API accommodates peak rates up to **200 requests/second**, standard scripts should run far below this threshold (typically under **1–2 requests/second**) to avoid trigger-blocking.

---

## 🛠️ 2. Architectural Design for Data Minimization

To minimize bandwidth and CPU overhead on Wikipedia’s servers, the critic engine must implement targeted query patterns:

### A. Endpoint Target Isolation
Instead of requesting full article HTML bodies, we query only the metadata required for validation:
* **References Endpoint**: `GET /api/rest_v1/page/references/{title}`
  Retrieves a lightweight JSON dictionary containing only the bibliography list, outbound DOIs, and external links of the page.
* **Summary Endpoint**: `GET /api/rest_v1/page/summary/{title}`
  Retrieves a clean plain-text extract (typically ~2-3 sentences) representing the introduction of the article, bypassing all template markup and edit histories.

### B. Local Cache Shielding (`wikipedia_cache.json`)
To guarantee that we never query the same Wikipedia topic twice:
1. Maintain a persistent cache file: `app/config/ref_data/wikipedia_cache.json`.
2. When the critic runs for a slug, it first checks the cache.
3. If a cache entry is found, the system reads it at disk speeds, creating **zero external network requests**.

---

## 🐍 3. Polite Client Implementation in Python

Below is a Python module implementing strict rate-limiting, custom headers, caching, and exponential backoff to fetch Wikipedia references safely:

```python
import time
import urllib.request
import urllib.parse
import json

class PoliteWikiClient:
    def __init__(self, cache_path="app/config/ref_data/wikipedia_cache.json"):
        self.cache_path = cache_path
        self.cache = {}
        self.load_cache()
        # Polite User-Agent identifying our application and contact email
        self.headers = {
            'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org; https://physicslab.org)'
        }

    def load_cache(self):
        try:
            with open(self.cache_path, "r") as f:
                self.cache = json.load(f)
        except Exception:
            self.cache = {}

    def save_cache(self):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass

    def fetch_references(self, wikipedia_title):
        normalized_title = wikipedia_title.replace(" ", "_")
        
        # 1. Check local cache first (Zero-traffic shield)
        if normalized_title in self.cache:
            return self.cache[normalized_title]

        encoded_title = urllib.parse.quote(normalized_title)
        url = f"https://en.wikipedia.org/api/rest_v1/page/references/{encoded_title}"
        
        # 2. Query with retries and exponential backoff
        backoff = 1.0
        for attempt in range(3):
            try:
                # Polite spacing: enforce 1 second sleep before call
                time.sleep(1.0)
                
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))
                
                # Extract and format references
                references = []
                for ref in data.get("references", []):
                    if "doi" in ref or "url" in ref:
                        references.append({
                            "title": ref.get("title", f"Wikipedia: {wikipedia_title}"),
                            "doi": ref.get("doi", ""),
                            "url": ref.get("url", "")
                        })
                
                # Cache and save results
                self.cache[normalized_title] = references
                self.save_cache()
                return references
                
            except urllib.error.HTTPError as e:
                if e.code in [429, 503]:  # Rate limited or server busy
                    time.sleep(backoff)
                    backoff *= 2.0
                else:
                    break
            except Exception:
                break
        
        return []
```

---

## 📴 4. The Ultimate Solution: Offline Local Mirroring (Zero-Traffic)

For high-scale, high-frequency offline runs (like our automated pipeline testing), hitting Wikipedia REST APIs is still suboptimal. The ultimate way to eliminate network traffic is **local mirroring**:

### A. Kiwix Offline Reader & ZIM Files
* **Concept**: Kiwix is an offline reader for Wikipedia. It stores compressed Wikipedia snapshots inside `.zim` files.
* **Implementation**:
  1. Download a pre-compressed ZIM file containing the physics subset of Wikipedia (e.g. `wikipedia_en_physics.zim`, size ~1.5 GB).
  2. Run a local Kiwix HTTP Server inside a Docker container:
     `docker run -d -v /data:/data -p 8080:80 kiwix/kiwix-serve wikipedia_en_physics.zim`
  3. Query `http://localhost:8080` for references.
  * **Result**: **0% load** on Wikimedia servers, **100% private**, and runs at local local SSD speeds (< 2ms per topic).

### B. Wikidata Static Dumps
* **Concept**: Wikidata compiles structured data for Wikipedia.
* **Implementation**: Import static Wikidata JSON dumps directly into a local SQLite database, allowing the Critic engine to run complex SQL lookup queries locally.
