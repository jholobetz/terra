#!/usr/bin/env python3
"""
🪐 Physics Lab: Context-Rich Multi-Agent Critic & Consensus Pipeline (v2.0)
Extracts claims, queries academic APIs and Wikipedia, evaluates alignment
with semantic boosting, and writes verified references directly to shards.
"""

import os
import sys
import re
import json
import argparse
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import date
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure NLTK data path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
sys.path.append(PROJECT_ROOT)

NLTK_DATA_PATH = os.path.join(PROJECT_ROOT, ".venv", "nltk_data")
if os.path.exists(NLTK_DATA_PATH):
    nltk.data.path.append(os.path.abspath(NLTK_DATA_PATH))

# Import verifier components
from scripts.maintenance.semantic_prose_verifier import preprocess_html, get_similarity_score
from scripts.maintenance.generate_system_health import is_node_subjective

# Configuration
LITERATURE_CACHE_PATH = os.path.join(PROJECT_ROOT, "app/config/ref_data/literature_cache.json")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "app/config/content")
SLUG_SHARD_MAP_PATH = os.path.join(PROJECT_ROOT, "slug_shard_map.json")

class MultiAgentCritic:
    def __init__(self, content_dir=CONTENT_DIR, cache_path=LITERATURE_CACHE_PATH):
        self.content_dir = content_dir
        self.cache_path = cache_path
        self.literature_cache = {}
        self.load_cache()
        self.load_shard_map()

    def load_cache(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r") as f:
                try:
                    self.literature_cache = json.load(f)
                except Exception:
                    self.literature_cache = {}

    def load_shard_map(self):
        self.slug_shard_map = {}
        # Only load the global mapping if we are using the standard content directory
        standard_content_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "app/config/content"))
        is_standard_dir = os.path.abspath(self.content_dir) == standard_content_dir
        
        if is_standard_dir and os.path.exists(SLUG_SHARD_MAP_PATH):
            with open(SLUG_SHARD_MAP_PATH, "r") as f:
                self.slug_shard_map = json.load(f)
        else:
            # Build dynamically
            for file in os.listdir(self.content_dir):
                if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json", "entities.json", "global_slug_registry.json", "notation.json", "particles.json", "compiled_trie_regex.json", "pillar_profiles.json"]:
                    path = os.path.join(self.content_dir, file)
                    try:
                        with open(path, "r") as f:
                            data = json.load(f)
                            for slug in data:
                                self.slug_shard_map[slug] = file
                    except Exception:
                        continue

    # Agent 1: Claim Extractor Agent
    def extract_claims(self, html_content):
        """
        Parses draft HTML, identifies core physical assertions, numerical constraints, 
        and key topics to verify.
        """
        clean_text = preprocess_html(html_content)
        if not clean_text:
            return []

        try:
            sentences = sent_tokenize(clean_text)
        except Exception:
            # Simple fallback sentence splitter
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean_text) if s.strip()]

        claims = []
        # Extract sentences containing numbers, physical parameters, or key keywords
        pattern = re.compile(r'\b(law|equation|relation|constant|mass|energy|force|momentum|theory|discovered|formulated|\d+)\b', re.IGNORECASE)
        for idx, sent in enumerate(sentences):
            if len(sent.split()) > 6 and pattern.search(sent):
                claims.append({
                    "id": f"claim_{idx}",
                    "assertion": sent
                })
        
        # Fallback if no claims match: use first two sentences
        if not claims and len(sentences) > 0:
            for idx, sent in enumerate(sentences[:2]):
                claims.append({
                    "id": f"claim_{idx}",
                    "assertion": sent
                })
        return claims

    # Agent 2: Literature Critic Agent (API queries with cache fallback)
    def query_arxiv(self, query, max_results=3):
        """Queries the official arXiv Atom feed API."""
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&max_results={max_results}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            results = []
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title_elem = entry.find('{http://www.w3.org/2005/Atom}title')
                summary_elem = entry.find('{http://www.w3.org/2005/Atom}summary')
                id_elem = entry.find('{http://www.w3.org/2005/Atom}id')
                
                title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "Unknown Title"
                summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
                url_str = id_elem.text.strip() if id_elem is not None else ""
                
                authors = []
                for author in entry.findall('{http://www.w3.org/2005/Atom}author'):
                    name_elem = author.find('{http://www.w3.org/2005/Atom}name')
                    if name_elem is not None:
                        authors.append(name_elem.text.strip())
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": "",
                    "abstract": summary,
                    "url": url_str
                })
            return results
        except Exception:
            return []

    def query_crossref(self, query, rows=3):
        """Queries the official Crossref REST API."""
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.crossref.org/works?query={encoded_query}&rows={rows}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (mailto:admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            items = data.get("message", {}).get("items", [])
            results = []
            for item in items:
                title = item.get("title", ["Unknown Title"])[0]
                doi = item.get("DOI", "")
                url_str = item.get("URL", f"https://doi.org/{doi}" if doi else "")
                
                authors = []
                for author in item.get("author", []):
                    authors.append(f"{author.get('family', '')}, {author.get('given', '')}".strip(", "))
                
                abstract = item.get("abstract", "")
                if abstract:
                    abstract = re.sub(r'<[^>]+>', ' ', abstract).strip()
                else:
                    abstract = f"Metadata record of publication '{title}' by {', '.join(authors[:3])}."
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": doi,
                    "abstract": abstract,
                    "url": url_str
                })
            return results
        except Exception:
            return []

    def query_inspire_hep(self, query, max_results=3):
        """Queries the official INSPIRE-HEP REST API."""
        import time
        time.sleep(1.0)
        encoded_query = urllib.parse.quote(f"find t {query}")
        url = f"https://inspirehep.net/api/literature?q={encoded_query}&size={max_results}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            results = []
            for hit in data.get("hits", {}).get("hits", []):
                metadata = hit.get("metadata", {})
                title = metadata.get("titles", [{"title": "Unknown Title"}])[0].get("title", "Unknown Title")
                authors = [a.get("full_name", "") for a in metadata.get("authors", [])]
                doi = metadata.get("dois", [{"value": ""}])[0].get("value") if metadata.get("dois") else ""
                
                abstracts = metadata.get("abstracts", [])
                abstract = abstracts[0].get("value", "") if abstracts else ""
                if abstract:
                    abstract = re.sub(r'<[^>]+>', ' ', abstract).strip()
                else:
                    abstract = f"High-Energy Physics publication '{title}' by {', '.join(authors[:3])}."
                
                arxiv_value = ""
                if metadata.get("arxiv_eprints"):
                    arxiv_value = metadata.get("arxiv_eprints")[0].get("value", "")
                url_str = f"https://doi.org/{doi}" if doi else (f"https://arxiv.org/abs/{arxiv_value}" if arxiv_value else "")
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": doi,
                    "abstract": abstract,
                    "url": url_str
                })
            return results
        except Exception:
            return []

    def query_semantic_scholar(self, query, max_results=3):
        """Queries Semantic Scholar's open paper search API."""
        import time
        time.sleep(1.0)
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={encoded_query}&limit={max_results}&fields=title,authors,abstract,externalIds,url"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            results = []
            for item in data.get("data", []):
                title = item.get("title", "Unknown Title")
                doi = item.get("externalIds", {}).get("DOI", "")
                authors = [a.get("name", "") for a in item.get("authors", [])]
                abstract = item.get("abstract", "") or ""
                if abstract:
                    abstract = re.sub(r'<[^>]+>', ' ', abstract).strip()
                else:
                    abstract = f"Academic publication '{title}' by {', '.join(authors[:3])}."
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": doi,
                    "abstract": abstract,
                    "url": item.get("url", f"https://doi.org/{doi}" if doi else "")
                })
            return results
        except Exception:
            return []

    def query_google_books(self, query, max_results=3):
        """Queries Google Books API for textbook references."""
        import time
        time.sleep(1.0)
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.googleapis.com/books/v1/volumes?q={encoded_query}&maxResults={max_results}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            results = []
            for item in data.get("items", []):
                volume = item.get("volumeInfo", {})
                title = volume.get("title", "Unknown Title")
                authors = volume.get("authors", [])
                description = volume.get("description", "")
                if description:
                    description = re.sub(r'<[^>]+>', ' ', description).strip()
                else:
                    description = f"Physics monograph/textbook '{title}' by {', '.join(authors[:3])}."
                
                results.append({
                    "title": title,
                    "authors": authors,
                    "doi": "",
                    "abstract": description,
                    "url": volume.get("infoLink", "")
                })
            return results
        except Exception:
            return []

    def query_wikipedia(self, query, max_results=2):
        """Queries Wikipedia API to retrieve lead section summaries of matching articles."""
        import time
        time.sleep(1.0)
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={encoded_query}&format=json&utf8="
        try:
            req = urllib.request.Request(search_url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            search_results = data.get("query", {}).get("search", [])
            results = []
            for item in search_results[:max_results]:
                page_title = item.get("title")
                encoded_title = urllib.parse.quote(page_title)
                summary_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles={encoded_title}&format=json"
                
                req2 = urllib.request.Request(summary_url, headers={'User-Agent': 'PhysicsLabCritic/2.0 (admin@physicslab.org)'})
                with urllib.request.urlopen(req2, timeout=5) as response2:
                    data2 = json.loads(response2.read().decode('utf-8'))
                
                pages = data2.get("query", {}).get("pages", {})
                for page_id, page_data in pages.items():
                    extract = page_data.get("extract", "")
                    if extract:
                        results.append({
                            "title": f"Wikipedia: {page_title}",
                            "authors": ["Wikipedia Contributors"],
                            "doi": "",
                            "abstract": extract,
                            "url": f"https://en.wikipedia.org/wiki/{encoded_title}"
                        })
            return results
        except Exception:
            return []

    def formulate_query(self, title, claims, strategy, context):
        if strategy == "title_only":
            return title
        elif strategy == "domain":
            domain = context.get("domain", "")
            domain_suffixes = {
                "astrophysics": "astrophysics supernova",
                "relativity": "general relativity spacetime",
                "philosophy-of-physics": "philosophy of physics substantivalism",
                "classical-mechanics": "classical mechanics physics",
                "electromagnetism": "electromagnetism physics",
                "thermodynamics-statistical-mechanics": "thermodynamics physics",
                "quantum-physics": "quantum mechanics physics",
                "standard-model": "particle physics model",
                "fluids-nonlinear": "fluid dynamics mechanics",
                "mathematical-methods": "mathematical physics"
            }
            suffix = domain_suffixes.get(domain, "physics")
            return f"{title} {suffix}"
        else: # default
            search_query = title
            if claims:
                words = [w for w in re.findall(r'\b\w{4,}\b', claims[0]["assertion"]) if w.lower() not in ["this", "that", "about", "which", "with", "from", "governed", "represents", "completely", "remains"]]
                if words:
                    search_query += " " + " ".join(words[:2])
            return search_query

    def get_literature_live(self, slug, query, context):
        """Queries live APIs based on domain routing rules."""
        domain = context.get("domain", "")
        
        arxiv_results = []
        crossref_results = []
        inspire_hep_results = []
        google_books_results = []
        semantic_scholar_results = []
        wikipedia_results = []

        # 1. Domain-Specific Routing
        if domain in ["standard-model", "quantum-physics"]:
            inspire_hep_results = self.query_inspire_hep(query)
        elif domain in ["classical-mechanics", "fluids-nonlinear", "thermodynamics-statistical-mechanics", "electromagnetism"]:
            google_books_results = self.query_google_books(query)
        elif domain in ["philosophy-of-physics"]:
            wikipedia_results = self.query_wikipedia(query)
            google_books_results = self.query_google_books(query)

        # 2. General Fallbacks (Semantic Scholar is preferred over Crossref/arXiv)
        semantic_scholar_results = self.query_semantic_scholar(query)

        if len(semantic_scholar_results) < 2 and domain in ["astrophysics", "relativity"]:
            arxiv_results = self.query_arxiv(query)

        if not inspire_hep_results and not google_books_results and not wikipedia_results and not arxiv_results:
            wikipedia_results = self.query_wikipedia(query)
            crossref_results = self.query_crossref(query)

        combined = inspire_hep_results + google_books_results + wikipedia_results + semantic_scholar_results + arxiv_results + crossref_results

        # Deduplicate based on title
        seen_titles = set()
        deduped = []
        for paper in combined:
            norm_title = paper["title"].lower().strip()
            norm_title = re.sub(r'[^\w\s]', '', norm_title)
            if norm_title not in seen_titles:
                seen_titles.add(norm_title)
                deduped.append(paper)

        return deduped

    def get_literature(self, slug, title, claims):
        """Attempts live queries, falls back to cache."""
        if slug in self.literature_cache:
            return self.literature_cache[slug]
        
        # Call live harvester using default strategy
        shard_name = self.slug_shard_map.get(slug, "")
        context = {
            "slug": slug,
            "shard": shard_name,
            "domain": shard_name.replace(".json", "")
        }
        query = self.formulate_query(title, claims, "default", context)
        return self.get_literature_live(slug, query, context)

    # Agent 3: Consensus Judge Agent
    def judge_consensus(self, cms_content, claims, literature, title=None, context=None):
        """
        Evaluates similarity between extracted claims/CMS content and retrieved paper abstracts.
        Returns a consensus score (0.0 to 1.0) and supported citations.
        """
        if not claims or not literature:
            return 0.0, []

        # Combine all abstracts into a single literature text block
        lit_block = " ".join([lit["abstract"] for lit in literature])
        
        # Calculate global similarity between the entire CMS text and the combined abstracts
        global_sim = get_similarity_score(lit_block, cms_content)
        
        supported_citations = []
        similarities = []

        # Prepare title words for exact keyword overlap check
        title_words = []
        if title:
            title_words = [w.lower() for w in re.findall(r'\b\w{3,}\b', title) if w.lower() not in ['and', 'the', 'for', 'with', 'about', 'from']]

        for claim in claims:
            claim_text = claim["assertion"]
            max_sim = 0.0
            best_paper = None
            
            for paper in literature:
                sim = get_similarity_score(paper["abstract"], claim_text)
                
                # Apply context boosts
                if context:
                    paper_text_lower = (paper["title"] + " " + paper["abstract"]).lower()
                    
                    # 1. Neighbor subtopics match boost
                    for neighbor in context.get("neighbors", []):
                        if neighbor in paper_text_lower:
                            sim += 0.02
                            
                    # 2. LaTeX math equations keywords match boost
                    for eq in context.get("equations", []):
                        math_terms = re.findall(r'[a-zA-Z]{3,}', eq)
                        for term in math_terms:
                            if term.lower() in paper_text_lower:
                                sim += 0.01

                if sim > max_sim:
                    max_sim = sim
                    best_paper = paper

            similarities.append(max_sim)

            # Check if there is exact keyword overlap with the subtopic title
            has_keyword_overlap = False
            if title_words and best_paper:
                paper_title_lower = best_paper["title"].lower()
                paper_abstract_lower = best_paper["abstract"].lower()
                has_keyword_overlap = all(w in paper_title_lower or w in paper_abstract_lower for w in title_words)

            if best_paper and (max_sim >= 0.08 or has_keyword_overlap) and best_paper not in supported_citations:
                supported_citations.append(best_paper)

        # Scale consensus score based on global similarity
        consensus_score = min(global_sim * 3.0, 1.0)
        
        # Boost consensus score based on verified supporting citations
        if supported_citations:
            boost = min(len(supported_citations) * 0.08, 0.25)
            consensus_score = min(consensus_score + boost, 1.0)
        else:
            consensus_score = 0.0

        return consensus_score, supported_citations

    def verify_slug(self, slug, write_citations=False):
        """Runs the entire multi-agent verification for a single slug with adaptive query retries."""
        shard_file = self.slug_shard_map.get(slug)
        if not shard_file:
            print(f"❌ Error: Slug '{slug}' not found in active content shards.")
            return False

        shard_path = os.path.join(self.content_dir, shard_file)
        with open(shard_path, "r") as f:
            shard_data = json.load(f)

        node = shard_data.get(slug)
        if not node:
            print(f"❌ Error: Slug '{slug}' not found inside {shard_file}.")
            return False

        title = node.get("title", slug)
        content = node.get("content", "")
        formula_ids = node.get("formula_ids", [])
        parents = node.get("parents", [])

        # Extract context
        neighbors = []
        for match in re.finditer(r'href="/physics/subtopic/([^"]+)"', content):
            neighbors.append(match.group(1))
        neighbor_names = [n.replace("-", " ") for n in set(neighbors)]
        latex_equations = re.findall(r'data-tex="([^"]+)"', content)

        context = {
            "slug": slug,
            "shard": shard_file,
            "formula_ids": formula_ids,
            "parents": parents,
            "neighbors": neighbor_names,
            "equations": latex_equations,
            "domain": shard_file.replace(".json", "")
        }

        # Determine decision threshold based on domain and node subjectivity
        category = context.get("domain")
        if is_node_subjective(slug, node, category=category):
            threshold = 0.35  # Philosophy/interpretation/conceptual nodes have more conceptual flexibility
        else:
            threshold = 0.50

        print("================================================================================")
        print(f"🧑‍🔬 CRITIC PIPELINE: Auditing [{slug}] '{title}'")
        print("================================================================================")

        # Step 1: Claim Extraction
        claims = self.extract_claims(content)
        print(f"🔹 Extracted {len(claims)} physical claim(s):")
        for c in claims[:3]:
            print(f"  * {c['assertion'][:100]}...")

        # Step 2: Retrieve Literature and Evaluate Consensus
        success = False
        final_consensus_score = 0.0
        final_citations = []
        final_literature = []

        # Check cache first
        cached_literature = self.literature_cache.get(slug)
        if cached_literature:
            print(f"🔹 Retrieved {len(cached_literature)} literature record(s) from Cache.")
            consensus_score, citations = self.judge_consensus(content, claims, cached_literature, title, context)
            if consensus_score >= threshold:
                success = True
                final_consensus_score = consensus_score
                final_citations = citations
                final_literature = cached_literature
            else:
                print(f"⚠️ Cached literature failed consensus (Score: {consensus_score:.3f}). Invalidating cache...")
                if slug in self.literature_cache:
                    del self.literature_cache[slug]

        if not success:
            strategies = ["default", "domain", "title_only"]
            for strategy in strategies:
                search_query = self.formulate_query(title, claims, strategy, context)
                print(f"📡 Querying literature APIs using strategy '{strategy}': '{search_query}'...")
                
                literature = self.get_literature_live(slug, search_query, context)
                print(f"🔹 Retrieved {len(literature)} literature record(s) from live APIs.")
                
                if not literature:
                    continue

                consensus_score, citations = self.judge_consensus(content, claims, literature, title, context)
                print(f"   ↳ Consensus Score: {consensus_score:.3f} | Citations: {len(citations)}")
                
                if consensus_score >= threshold:
                    success = True
                    final_consensus_score = consensus_score
                    final_citations = citations
                    final_literature = literature
                    break
                else:
                    if consensus_score > final_consensus_score:
                        final_consensus_score = consensus_score
                        final_citations = citations
                        final_literature = literature

        # Print outcome
        print(f"🔹 Final Consensus Score: {final_consensus_score:.3f} (Threshold: {threshold:.2f})")
        print(f"🔹 Final Verified Citations Count: {len(final_citations)}")

        if success:
            print(f"✓ APPROVED: [{slug}] meets literature consensus criteria.")
            for cit in final_citations[:2]:
                print(f"  📖 Reference: '{cit['title']}' by {', '.join(cit['authors'][:2])} (DOI: {cit['doi'] or 'N/A'})")
            
            # Save the successful results to the literature cache (relevance-gated)
            self.literature_cache[slug] = final_literature
            try:
                with open(self.cache_path, "w") as f:
                    json.dump(self.literature_cache, f, indent=2)
            except Exception:
                pass

            if write_citations:
                citation_list = []
                for cit in final_citations:
                    citation_list.append({
                        "doi": cit["doi"],
                        "title": cit["title"],
                        "authors": cit["authors"],
                        "url": cit["url"]
                    })

                node["verification"] = {
                    "verified_date": str(date.today()),
                    "consensus_score": round(final_consensus_score, 2),
                    "agents": {
                        "extractor": "ClaimExtractor-v1.1",
                        "critic": "LiteratureCritic-v2.0",
                        "judge": "ConsensusJudge-v2.0"
                    },
                    "citations": citation_list
                }
                
                # Write back to shard
                shard_data[slug] = node
                with open(shard_path, "w") as f:
                    json.dump(shard_data, f, indent=2)
                print(f"✓ Added verified citations metadata directly to {shard_file}.")
        else:
            print(f"❌ REJECTED: [{slug}] failed literature consensus criteria.")
            print("  Reason: Low similarity or lack of supporting documentation in academic databases.")

        print("================================================================================")
        return success

def main():
    parser = argparse.ArgumentParser(description="Run Tier 3 Multi-Agent Critic on subtopics.")
    parser.add_argument("--slug", help="Run verification on a single subtopic slug.")
    parser.add_argument("--write-citations", action="store_true", help="Write verification metadata directly to the content shard.")
    args = parser.parse_args()

    critic = MultiAgentCritic()
    if args.slug:
        success = critic.verify_slug(args.slug, write_citations=args.write_citations)
        sys.exit(0 if success else 1)
    else:
        success = True
        for slug in list(critic.literature_cache):
            if slug in critic.slug_shard_map:
                res = critic.verify_slug(slug, write_citations=args.write_citations)
                if not res:
                    success = False
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
