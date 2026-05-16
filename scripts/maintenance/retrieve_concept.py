import json
import os
import re
import sys

CONTENT_DIR = "app/config/content"
CACHE_FILE = "slug_shard_map.json"

def build_cache():
    mapping = {}
    # Subtopic shards
    for file in os.listdir(CONTENT_DIR):
        if file.endswith(".json") and file not in ["categories.json", "formulas.json", "constants.json", "search_index.json", "entities.json", "global_slug_registry.json"]:
            path = os.path.join(CONTENT_DIR, file)
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    for slug in data:
                        mapping[slug] = file
            except Exception:
                continue
    
    # Topic shards
    topic_dir = os.path.join(CONTENT_DIR, "topics")
    if os.path.exists(topic_dir):
        for file in os.listdir(topic_dir):
            if file.endswith(".json"):
                slug = file.replace(".json", "")
                mapping[slug] = f"topics/{file}"
                
    with open(CACHE_FILE, "w") as f:
        json.dump(mapping, f, indent=2)
    return mapping

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return build_cache()

def minify_payload(data):
    """Removes heavy-weight fields that are not needed for prose research."""
    keys_to_remove = ["snippet_svg", "snippet", "hero_math_svg"] # Removing hero_math_svg if it exists, keeping hero_math if it's text
    # Also check if hero_math looks like an SVG
    if "hero_math" in data and "<svg" in str(data["hero_math"]):
        keys_to_remove.append("hero_math")
        
    minified = {k: v for k, v in data.items() if k not in keys_to_remove}
    return minified

def retrieve(slug):
    cache = load_cache()
    if slug not in cache:
        # Re-build cache in case of new slugs
        cache = build_cache()
        if slug not in cache:
            return None
            
    shard_file = cache[slug]
    path = os.path.join(CONTENT_DIR, shard_file)
    
    with open(path, "r") as f:
        data = json.load(f)
        
    if shard_file.startswith("topics/"):
        # Main topics are the whole file
        return minify_payload(data)
    else:
        # Subtopics are keys in the file
        concept_data = data.get(slug)
        if concept_data:
            return minify_payload(concept_data)
    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 retrieve_concept.py [slug]")
        sys.exit(1)
        
    slug = sys.argv[1]
    result = retrieve(slug)
    if result:
        print(json.dumps(result, indent=2))
    else:
        print(f"ERROR: Slug [{slug}] not found.")
        sys.exit(1)
