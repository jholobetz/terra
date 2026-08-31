#!/usr/bin/env python3
"""
🪐 Physics Lab: Semantic Prose Verifier
Audits CMS subtopic content against textbook-standard reference descriptions using TF-IDF and NLTK.
"""

import os
import sys
import json
import re
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Configure NLTK data path for the local virtual environment folder
if HAS_NLTK:
    NLTK_DATA_PATH = os.path.join(PROJECT_ROOT, ".venv", "nltk_data")
    if os.path.exists(NLTK_DATA_PATH):
        nltk.data.path.append(os.path.abspath(NLTK_DATA_PATH))

# Threshold parameters
SIMILARITY_THRESHOLD_WARNING = 0.15
SIMILARITY_THRESHOLD_ERROR = 0.08

def preprocess_html(html_content, lowercase=True):
    """
    Strips HTML tags, math blocks, and extracts clean plain text for semantic analysis.
    """
    if not html_content:
        return ""
    
    # Remove MathJax display equations (<div class="math-display">...</div>)
    text = re.sub(r'<div class="math-display".*?</div>', ' ', html_content, flags=re.DOTALL)
    
    # Remove Inline MathJax equations (e.g. \( ... \))
    text = re.sub(r'\\\(.*?\\\)', ' ', text)
    text = re.sub(r'\\\[.*?\\\]', ' ', text)
    
    # Remove SVGs
    text = re.sub(r'<svg.*?</svg>', ' ', text, flags=re.DOTALL)
    
    # Remove all HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower() if lowercase else text

def tokenize_and_lemmatize(text):
    """
    Tokenizes, removes stop words, and lemmatizes the text.
    """
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = re.findall(r'\b\w+\b', text)
        
    try:
        stop_words = set(stopwords.words('english'))
    except Exception:
        stop_words = set()
        
    try:
        lemmatizer = WordNetLemmatizer()
    except Exception:
        lemmatizer = None
        
    cleaned_tokens = []
    for t in tokens:
        t_clean = ''.join(c for c in t if c.isalnum())
        if t_clean and t_clean not in stop_words:
            try:
                lemma = lemmatizer.lemmatize(t_clean) if lemmatizer else t_clean
            except Exception:
                lemma = t_clean
            cleaned_tokens.append(lemma)
    return cleaned_tokens

def get_similarity_score(reference_text, cms_text):
    """
    Calculates TF-IDF cosine similarity between reference and CMS text.
    """
    ref_clean = preprocess_html(reference_text)
    cms_clean = preprocess_html(cms_text)
    
    if not ref_clean or not cms_clean:
        return 0.0
        
    if not HAS_SKLEARN:
        # Fallback simple overlap similarity excluding stop words
        stop_words = {
            'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
            'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'did', 'do',
            'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having',
            'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is',
            'it', 'its', 'itself', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once',
            'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should', 'so',
            'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there', 'these',
            'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we', 'were',
            'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'you', 'your', 'yours', 'yourself',
            'yourselves'
        }
        tokens_ref = {w for w in re.findall(r'\b\w+\b', ref_clean.lower()) if w not in stop_words}
        tokens_cms = {w for w in re.findall(r'\b\w+\b', cms_clean.lower()) if w not in stop_words}
        if not tokens_ref:
            return 0.0
        return float(len(tokens_ref & tokens_cms) / len(tokens_ref))

    def dummy_tokenizer(text):
        return tokenize_and_lemmatize(text)
        
    vectorizer = TfidfVectorizer(tokenizer=dummy_tokenizer, token_pattern=None, lowercase=False)
    try:
        tfidf_matrix = vectorizer.fit_transform([ref_clean, cms_clean])
        # Cosine similarity of L2-normalized vectors is their dot product
        ref_vec = tfidf_matrix[0]
        cms_vec = tfidf_matrix[1]
        similarity = (ref_vec * cms_vec.T).toarray()[0][0]
        return float(similarity)
    except Exception as e:
        print(f"⚠️ Error computing TF-IDF similarity: {e}")
        return 0.0

def check_keywords(cms_text, keywords):
    """
    Verifies that specified keywords (or their lemmas) are present in the CMS text.
    Returns (missing_keywords, found_keywords).
    """
    cms_clean = preprocess_html(cms_text)
    cms_tokens = set(tokenize_and_lemmatize(cms_clean))
    try:
        lemmatizer = WordNetLemmatizer()
    except Exception:
        lemmatizer = None
    
    missing = []
    found = []
    
    for kw in keywords:
        kw_clean = kw.lower().strip()
        
        # Check raw text substring match first (handles hyphenated terms & multi-word terms)
        if kw_clean in cms_clean or kw_clean.replace('-', ' ') in cms_clean or kw_clean.replace(' ', '-') in cms_clean:
            found.append(kw)
            continue

        kw_parts = re.split(r'[\s\-]+', kw_clean)
        
        if len(kw_parts) == 1:
            try:
                kw_lemma = lemmatizer.lemmatize(kw_parts[0]) if lemmatizer else kw_parts[0]
            except Exception:
                kw_lemma = kw_parts[0]
                
            if kw_lemma in cms_tokens or kw_parts[0] in cms_tokens:
                found.append(kw)
            else:
                missing.append(kw)
        else:
            # Multi-word/hyphenated fallback: check if all individual components exist
            parts_found = True
            for part in kw_parts:
                try:
                    part_lemma = lemmatizer.lemmatize(part) if lemmatizer else part
                except Exception:
                    part_lemma = part
                if part_lemma not in cms_tokens and part not in cms_tokens and part not in cms_clean:
                    parts_found = False
                    break
            if parts_found:
                found.append(kw)
            else:
                missing.append(kw)
                    
    return missing, found

def audit_semantic_prose(content_dir="app/config/content", ref_path="app/config/ref_data/semantic_references.json", target_slug=None):
    if not os.path.exists(ref_path):
        print(f"❌ Error: Semantic reference database not found at {ref_path}")
        return False

    with open(ref_path, "r") as f:
        ref_data = json.load(f)

    # If targeting a specific slug and it's not registered, we skip audit
    if target_slug and target_slug not in ref_data:
        print(f"✓ Skipping semantic prose audit for [{target_slug}]: No reference entry defined.")
        return True

    # Load all subtopics using a simple loader to avoid dependency complexity or circular imports
    subtopics = {}
    
    # Read slug shard mapping if available and we are using standard content_dir
    standard_content_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "app/config/content"))
    is_standard_dir = os.path.abspath(content_dir) == standard_content_dir
    
    mapping_path = os.path.join(PROJECT_ROOT, "slug_shard_map.json")
    if is_standard_dir and os.path.exists(mapping_path):
        with open(mapping_path, "r") as f:
            slug_shard_map = json.load(f)
    else:
        # Build mapping on the fly
        slug_shard_map = {}
        for file in os.listdir(content_dir):
            if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json", "entities.json", "global_slug_registry.json", "notation.json", "particles.json", "pillar_profiles.json", "formula_aliases.json"]:
                path = os.path.join(content_dir, file)
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                        for slug in data:
                            slug_shard_map[slug] = file
                except Exception:
                    continue

    # Identify slugs to verify
    slugs_to_check = [target_slug] if target_slug else list(ref_data.keys())
    
    errors = []
    warnings = []
    cached_shards = {}
    
    print("================================================================================")
    print("             🪐 PHYSICS LAB: SEMANTIC PROSE ALIGNMENT AUDITOR                   ")
    print("================================================================================")

    for slug in slugs_to_check:
        if slug not in ref_data:
            continue
            
        ref = ref_data[slug]
        ref_prose = ref.get("reference_prose", "")
        keywords = ref.get("keywords", [])
        title = ref.get("title", slug)

        shard_file = slug_shard_map.get(slug)
        if not shard_file:
            print(f"⚠️ Warning: Slug '{slug}' not found in active content shards.")
            continue

        if shard_file not in cached_shards:
            shard_path = os.path.join(content_dir, shard_file)
            try:
                with open(shard_path, "r") as f:
                    cached_shards[shard_file] = json.load(f)
            except Exception as e:
                print(f"❌ Error reading shard {shard_file}: {e}")
                continue

        cms_node = cached_shards[shard_file].get(slug, {})

        cms_text = cms_node.get("content", "")
        if not cms_text:
            errors.append(f"[{slug}] Content is empty or missing.")
            print(f"❌ ERROR: [{slug}] '{title}' - Content is empty")
            continue

        # 1. Cosine similarity
        similarity = get_similarity_score(ref_prose, cms_text)
        
        # 2. Keywords check
        missing_kws, found_kws = check_keywords(cms_text, keywords)
        
        # Decision logic
        failed = False
        reasons = []

        # Error triggers
        if similarity < SIMILARITY_THRESHOLD_ERROR:
            failed = True
            reasons.append(f"Critical semantic drift: TF-IDF similarity is {similarity:.3f} (Error threshold: {SIMILARITY_THRESHOLD_ERROR})")
            
        # If more than 50% keywords are missing, trigger error
        if len(keywords) > 0 and (len(missing_kws) / len(keywords)) > 0.5:
            failed = True
            reasons.append(f"Critical keyword omission: Missing {len(missing_kws)}/{len(keywords)} core keywords: {missing_kws}")
            
        if failed:
            errors.append(f"[{slug}] {', '.join(reasons)}")
            print(f"❌ FAIL: [{slug}] '{title}'")
            print(f"  Similarity: {similarity:.3f}")
            print(f"  Missing Keywords: {missing_kws}")
            for r in reasons:
                print(f"  Reason: {r}")
        else:
            # Check warning triggers
            warn_reasons = []
            if similarity < SIMILARITY_THRESHOLD_WARNING:
                warn_reasons.append(f"Low semantic similarity: {similarity:.3f} (Warning threshold: {SIMILARITY_THRESHOLD_WARNING})")
            if missing_kws:
                warn_reasons.append(f"Missing keywords: {missing_kws}")

            if warn_reasons:
                warnings.append(f"[{slug}] {', '.join(warn_reasons)}")
                print(f"⚠️ WARNING: [{slug}] '{title}'")
                print(f"  Similarity: {similarity:.3f}")
                print(f"  Missing Keywords: {missing_kws}")
            else:
                print(f"✓ [{slug}] '{title}' aligned semantically (Similarity: {similarity:.3f}, Keywords: {len(found_kws)}/{len(keywords)} found)")

    print("================================================================================")
    if errors:
        print(f"❌ AUDIT FAILED: Found {len(errors)} semantic alignment error(s)!")
        return False
    else:
        if warnings:
            print(f"⚠️ AUDIT PASSED WITH WARNINGS: {len(warnings)} issue(s) flagged.")
        else:
            print("✓ SECURE: All checked subtopics are semantically aligned with scientific references!")
        return True

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else None
    success = audit_semantic_prose(target_slug=target)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
