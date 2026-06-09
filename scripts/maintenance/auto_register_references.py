#!/usr/bin/env python3
"""
🪐 Physics Lab: Automatic Semantic References Generator & Register
Scans all content shards for unregistered subtopics, extracts canonical prose definitions
and technical keywords from their HTML, and registers them in semantic_references.json.
"""

import os
import sys
import re
import json

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CONTENT_DIR = os.path.join(PROJECT_ROOT, "app/config/content")
REF_PATH = os.path.join(PROJECT_ROOT, "app/config/ref_data/semantic_references.json")

# Simple, robust stop words list to keep keyword extraction local and dependency-free
STOP_WORDS = {
    'the', 'is', 'at', 'which', 'on', 'for', 'and', 'a', 'an', 'of', 'to', 'in', 
    'that', 'it', 'was', 'with', 'as', 'by', 'from', 'this', 'these', 'those', 
    'or', 'but', 'not', 'be', 'have', 'are', 'were', 'been', 'has', 'had', 'do', 
    'does', 'did', 'about', 'also', 'into', 'under', 'above', 'can', 'will', 
    'would', 'should', 'could', 'than', 'then', 'their', 'them', 'they', 'he', 
    'she', 'we', 'you', 'our', 'us', 'its', 'other', 'both', 'between', 'through',
    # Common generic verbs/nouns that make poor technical keywords
    'equation', 'equations', 'system', 'systems', 'theory', 'theories', 
    'value', 'values', 'function', 'functions', 'constant', 'constants', 
    'law', 'laws', 'state', 'states', 'defined', 'defined', 'describes', 
    'describing', 'expressed', 'fundamental', 'physics', 'physical', 
    'particle', 'particles', 'given', 'where', 'first', 'second', 'third'
}

def clean_html(html):
    """Strip HTML tags and convert simple formatting to plain text."""
    if not html:
        return ""
    # Strip MathJax/SVG elements if any
    text = re.sub(r'<svg[^>]*>.*?</svg>', '', html, flags=re.DOTALL)
    # Strip all other HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Clean double spaces and linebreaks
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_reference_prose(html_content):
    """Extract the first valid paragraph of definition prose."""
    # Find paragraph blocks
    paragraphs = re.findall(r'<p>(.*?)</p>', html_content, re.DOTALL)
    for p in paragraphs:
        cleaned = clean_html(p)
        # Skip paragraphs that are too short (e.g. math-only or header snippets)
        if len(cleaned.split()) >= 15:
            # Cap definition at ~3 sentences or 300 characters
            sentences = re.split(r'(?<=[.!?])\s+', cleaned)
            prose = " ".join(sentences[:3])
            if len(prose) > 350:
                prose = prose[:347] + "..."
            return prose
            
    # Fallback to whole cleaned text if no paragraph structure found
    cleaned = clean_html(html_content)
    sentences = re.split(r'(?<=[.!?])\s+', cleaned)
    prose = " ".join(sentences[:3])
    if len(prose) > 350:
        prose = prose[:347] + "..."
    return prose

def generate_keywords(text, title):
    """Extract dominant technical keywords from text, prioritizing title words."""
    words = re.findall(r'\b[a-zA-Z-]{4,}\b', text.lower())
    
    # Count frequencies of non-stop-words
    freq = {}
    for w in words:
        if w not in STOP_WORDS:
            freq[w] = freq.get(w, 0) + 1
            
    # Sort by frequency descending
    sorted_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [w[0] for w in sorted_words[:6]]
    
    # Ensure title words (excluding stop words) are represented if they are technical and present in the text
    title_words = re.findall(r'\b[a-zA-Z-]{4,}\b', title.lower())
    for tw in title_words:
        if tw not in STOP_WORDS and tw not in keywords and tw in words:
            keywords.insert(0, tw)
            
    # Deduplicate while preserving order and limit to max 7 keywords
    seen = set()
    deduped = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            deduped.append(k)
            
    return deduped[:7]

def auto_register_slug(slug, shard_data, references):
    """Generates and registers a reference entry for a single slug."""
    node = shard_data.get(slug, {})
    if not isinstance(node, dict):
        return False
    title = node.get("title", slug)
    content = node.get("content", "")
    
    if not content:
        print(f"⚠️ Warning: Slug [{slug}] has empty content. Skipping registration.")
        return False
        
    prose = extract_reference_prose(content)
    keywords = generate_keywords(clean_html(content), title)
    
    if not prose or not keywords:
        print(f"⚠️ Warning: Could not generate prose or keywords for [{slug}]. Skipping.")
        return False
        
    references[slug] = {
        "title": title,
        "reference_prose": prose,
        "keywords": keywords
    }
    print(f"✓ Registered: [{slug}] '{title}'")
    print(f"  Prose: {prose}")
    print(f"  Keywords: {keywords}")
    return True

def main():
    # 1. Load existing references
    references = {}
    if os.path.exists(REF_PATH):
        try:
            with open(REF_PATH, "r") as f:
                references = json.load(f)
        except Exception as e:
            print(f"❌ Error loading references file: {e}")
            sys.exit(1)
            
    # 2. Scan content shards for unregistered slugs
    print("Scanning content shards for unregistered reference topics...")
    unregistered_slugs = []
    slug_shard_map = {}
    
    for file in os.listdir(CONTENT_DIR):
        if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json", "entities.json", "global_slug_registry.json", "notation.json", "particles.json", "compiled_trie_regex.json", "pillar_profiles.json"]:
            path = os.path.join(CONTENT_DIR, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for slug in data:
                        slug_shard_map[slug] = (path, data)
                        if slug not in references:
                            unregistered_slugs.append(slug)
            except Exception as e:
                print(f"⚠️ Warning: Could not read shard {file}: {e}")
                
    if not unregistered_slugs:
        print("✓ All active subtopics are already registered in the reference database.")
        sys.exit(0)
        
    print(f"Found {len(unregistered_slugs)} unregistered subtopics.")
    
    # 3. Register them
    registered_count = 0
    for slug in unregistered_slugs:
        path, data = slug_shard_map[slug]
        if auto_register_slug(slug, data, references):
            registered_count += 1
            
    # 4. Save references back to disk (alphabetically sorted by slug)
    if registered_count > 0:
        sorted_references = {k: references[k] for k in sorted(references.keys())}
        try:
            with open(REF_PATH, "w") as f:
                json.dump(sorted_references, f, indent=4)
            print(f"\n✓ Successfully registered {registered_count} new reference topics in semantic_references.json!")
        except Exception as e:
            print(f"❌ Failed to save semantic_references.json: {e}")
            sys.exit(1)
    else:
        print("\nNo new reference topics were registered.")

if __name__ == "__main__":
    main()
