#!/usr/bin/env python3
"""
Pillar 2: Automatic Neighbor Bolding & Formatting
Resolves all neighbor slugs and titles for the targeted subtopic in subfiles/batch_payload.json,
scans the draft content, and automatically formats their first mention as:
<strong><a href="/physics/subtopic/[slug]" class="subtopic-link">[Neighbor Name]</a></strong>
"""

import os
import sys
import json
import re
import argparse

sys.path.append(os.getcwd())
from orchestrator import PhysicsOrchestrator

PAYLOAD_PATH = "subfiles/batch_payload.json"
CONTENT_DIR = "app/config/content"

def load_aliases():
    aliases = {}
    alias_path = 'subfiles/auto_link_aliases.json'
    if os.path.exists(alias_path):
        with open(alias_path, 'r') as f:
            try:
                aliases = json.load(f)
            except Exception:
                pass

    registry_path = 'global_slug_registry.json'
    if os.path.exists(registry_path):
        with open(registry_path, 'r') as f:
            try:
                registry = json.load(f)
                aliases.update(registry)
            except Exception:
                pass
    return aliases

def format_first_occurrence(tokens, term, slug):
    # Match term with word boundaries (alphanumeric boundary check)
    regex = re.compile(rf'(?<!\w){re.escape(term)}(?!\w)', re.IGNORECASE)
    
    in_link = False
    in_strong = False
    for i, token in enumerate(tokens):
        if i % 2 == 1:
            # Tag or equation
            t_lower = token.lower()
            if t_lower.startswith("<a ") or t_lower.startswith("<a\t") or t_lower == "<a>":
                in_link = True
            elif t_lower == "</a>":
                in_link = False
            elif t_lower == "<strong>":
                in_strong = True
            elif t_lower == "</strong>":
                in_strong = False
        else:
            # Text segment
            if not in_link:
                match = regex.search(token)
                if match:
                    start, end = match.span()
                    matched_text = token[start:end]
                    
                    # If already inside strong, don't double-wrap in strong
                    if in_strong:
                        wrapped = f'<a href="/physics/subtopic/{slug}" class="subtopic-link">{matched_text}</a>'
                    else:
                        wrapped = f'<strong><a href="/physics/subtopic/{slug}" class="subtopic-link">{matched_text}</a></strong>'
                    
                    tokens[i] = token[:start] + wrapped + token[end:]
                    return True
    return False

def check_if_already_linked(content, slug):
    # Checks if a link to this slug already exists in the content
    link_pattern = re.compile(rf'/physics/subtopic/{re.escape(slug)}\b')
    return bool(link_pattern.search(content))

def format_draft(slug, draft_data, search_index, aliases):
    content = draft_data.get("content", "")
    if not content:
        return draft_data

    # Resolve shard of the target subtopic
    target_entry = search_index.get(slug)
    if not target_entry:
        print(f"  ⚠️ Warning: Target '{slug}' not found in search_index.json. Skipping neighbor auto-link.")
        return draft_data
    
    shard_file = target_entry.get("s") if isinstance(target_entry, dict) else target_entry
    if not shard_file:
        print(f"  ⚠️ Warning: Could not resolve shard file for '{slug}'. Skipping neighbor auto-link.")
        return draft_data

    # Resolve neighbors (all other subtopics in the same shard)
    neighbors = []
    for s_slug, s_data in search_index.items():
        if s_slug == slug:
            continue
        s_shard = s_data.get("s") if isinstance(s_data, dict) else s_data
        if s_shard == shard_file:
            title = s_data.get("t", s_slug) if isinstance(s_data, dict) else s_slug
            neighbors.append((s_slug, title))

    # Collect search terms for all neighbors
    # Maps term -> (slug, title)
    term_map = {}
    for n_slug, n_title in neighbors:
        # 1. The title itself
        term_map[n_title.lower()] = (n_slug, n_title)
        # 2. Slug with hyphens to spaces
        term_map[n_slug.replace("-", " ").lower()] = (n_slug, n_title)
        
    # Add aliases that map to these neighbor slugs
    for alias_term, mapped_slug in aliases.items():
        if mapped_slug in [n[0] for n in neighbors]:
            # Find the title for this slug
            n_title = search_index[mapped_slug].get("t", mapped_slug) if isinstance(search_index[mapped_slug], dict) else mapped_slug
            term_map[alias_term.lower()] = (mapped_slug, n_title)

    # Sort terms by length descending to match greedily
    sorted_terms = sorted(term_map.keys(), key=len, reverse=True)

    # Tokenize HTML/equations
    # Odd indices are HTML tags or LaTeX blocks, even indices are plain text segments
    token_pattern = re.compile(r'(<[^>]+>|\\\(.*?\\\)|\\\[.*?\\\])', re.DOTALL)
    tokens = token_pattern.split(content)

    linked_slugs = set()
    # Mark slugs that are already linked in the content
    for n_slug, _ in neighbors:
        if check_if_already_linked(content, n_slug):
            linked_slugs.add(n_slug)

    replacements_count = 0
    for term in sorted_terms:
        n_slug, n_title = term_map[term]
        if n_slug in linked_slugs:
            continue
        
        # Attempt to format the first occurrence of this term
        if format_first_occurrence(tokens, term, n_slug):
            linked_slugs.add(n_slug)
            replacements_count += 1
            print(f"  ✓ Formatted neighbor link: '{term}' -> '{n_slug}'")

    if replacements_count > 0:
        # Reassemble content
        draft_data["content"] = "".join(tokens)
        print(f"  ✓ Automatically formatted {replacements_count} neighbor links in '{slug}'.")
    else:
        print(f"  ✓ No new neighbor links to format in '{slug}'.")

    return draft_data

def main():
    parser = argparse.ArgumentParser(description="🪐 format_neighbors: Automatically format neighbor links in batch payload")
    parser.add_argument("--slug", type=str, help="Specify a single slug to format in batch_payload.json")
    args = parser.parse_args()

    if not os.path.exists(PAYLOAD_PATH):
        print(f"Error: Batch payload file '{PAYLOAD_PATH}' not found.")
        sys.exit(1)

    with open(PAYLOAD_PATH, "r") as f:
        try:
            payload = json.load(f)
        except Exception as e:
            print(f"Error parsing '{PAYLOAD_PATH}': {e}")
            sys.exit(1)

    search_index_path = os.path.join(CONTENT_DIR, "search_index.json")
    if not os.path.exists(search_index_path):
        print(f"Error: search_index.json not found at '{search_index_path}'")
        sys.exit(1)

    with open(search_index_path, "r") as f:
        search_index = json.load(f)

    aliases = load_aliases()
    print(f"Loaded {len(aliases)} auto-link aliases.")

    modified = False
    for slug in list(payload.keys()):
        if args.slug and slug != args.slug:
            continue
        print(f"Processing neighbor formatting for '{slug}'...")
        payload[slug] = format_draft(slug, payload[slug], search_index, aliases)
        modified = True

    if modified:
        with open(PAYLOAD_PATH, "w") as f:
            json.dump(payload, f, indent=4)
        print(f"\n✓ SUCCESS: Saved formatted drafts back to '{PAYLOAD_PATH}'.")
    else:
        print("\nNo drafts were formatted.")

if __name__ == "__main__":
    main()
