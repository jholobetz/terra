#!/usr/bin/env python3
"""
GQS Stack Generator Utility
Pre-computes the entire metadata skeleton (parent shard, neighbors, cross-hub bridges,
mathematical identities, and organic paragraph targets) for the top N pending backlog subtopics,
and outputs a single, centralized graduation queue stack JSON file.
"""

import os
import sys
import json
import hashlib
import re

CONTENT_DIR = "app/config/content"
BACKLOG_PATH = "subfiles/expansion_backlog.json"
GQS_PATH = "subfiles/graduation_queue_stack.json"

BRIDGES = {
    "thermodynamics-statistical-mechanics.json": ("minkowski-metric", "Minkowski Metric"),
    "relativity.json": ("hamiltons-principle", "Hamilton's Principle"),
    "quantum-physics.json": ("background-independence", "Background Independence"),
    "astrophysics.json": ("energy-momentum-relation", "Energy-Momentum Relation"),
    "classical-mechanics.json": ("entropy", "Entropy"),
    "philosophy-of-physics.json": ("minkowski-metric", "Minkowski Metric")
}

MATH_TEMPLATES = {
    "thermodynamics-statistical-mechanics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "relativity.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "quantum-physics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "theoretical-physics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "classical-mechanics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "electromagnetism.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "astrophysics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "philosophy-of-physics.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "standard-model.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "fluids-nonlinear.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "mathematical-methods.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "condensed-matter.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    },
    "legacy-orphans.json": {
        "title": "PLACEHOLDER: Localized Title Needed",
        "equation": "\\text{PLACEHOLDER: Localized Equation Needed}",
        "description": "Please override this placeholder with a mathematically localized identity."
    }
}

def normalize_slug(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s

def main():
    limit = 30
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Warning: Invalid limit '{sys.argv[1]}'. Defaulting to 30.")

    # 1. Verify and load search_index.json
    search_index_path = os.path.join(CONTENT_DIR, "search_index.json")
    if not os.path.exists(search_index_path):
        print(f"Error: search_index.json not found at {search_index_path}")
        sys.exit(1)
    with open(search_index_path, "r") as f:
        search_index = json.load(f)

    # 2. Verify and load backlog
    if not os.path.exists(BACKLOG_PATH):
        print(f"Error: expansion backlog not found at {BACKLOG_PATH}")
        sys.exit(1)
    with open(BACKLOG_PATH, "r") as f:
        backlog = json.load(f)

    # 2b. Load backlog math registry (Safeguard 3)
    math_registry_path = "subfiles/backlog_math_registry.json"
    backlog_math_registry = {}
    if os.path.exists(math_registry_path):
        try:
            with open(math_registry_path, "r") as f:
                backlog_math_registry = json.load(f)
            print(f"Loaded {len(backlog_math_registry)} math templates from {math_registry_path}.")
        except Exception as e:
            print(f"Warning: Failed to load {math_registry_path}: {e}")


    # Filter backlog for pending items that exist as legacy-tier nodes in a shard
    pending_items = [item for item in backlog if item.get("status") == "pending" and item.get("suggested_slug") in search_index]
    if not pending_items:
        print("Notice: No pending backlog items found to generate GQS stack.")
        sys.exit(0)

    # Sort pending items by frequency descending
    pending_items.sort(key=lambda x: x.get("frequency", 0), reverse=True)
    selected_items = pending_items[:limit]

    print(f"Generating GQS Stack for the top {len(selected_items)} pending items...")

    stack_data = []

    for index, item in enumerate(selected_items):
        title = item.get("term")
        slug = item.get("suggested_slug") or normalize_slug(title)
        
        # Shard Resolution
        shard_file = None
        entry = search_index.get(slug)
        if entry:
            if isinstance(entry, dict):
                shard_file = entry.get("s")
                title = entry.get("t", title)
            elif isinstance(entry, str):
                shard_file = entry
        
        # Fallback to default shard if unresolved
        if not shard_file:
            shard_file = "theoretical-physics.json"

        # Resolve 5 neighbors in the parent shard
        all_neighbors = []
        for s, data in search_index.items():
            if s == slug:
                continue
            if isinstance(data, dict) and data.get("s") == shard_file:
                all_neighbors.append((s, data.get("t", s)))

        # Sort neighbors deterministic-randomly unique to each target slug to avoid clumping
        all_neighbors.sort(key=lambda x: hashlib.md5((slug + x[0]).encode('utf-8')).hexdigest())
        selected_neighbors = all_neighbors[:5]
        while len(selected_neighbors) < 5:
            selected_neighbors.append(("theoretical-physics-overview", "Theoretical Physics Overview"))

        neighbors_list = [{"slug": n[0], "title": n[1]} for n in selected_neighbors]

        # Resolve Cross-Hub Bridge
        b_slug, b_title = BRIDGES.get(shard_file, ("minkowski-metric", "Minkowski Metric"))
        bridge_dict = {"slug": b_slug, "title": b_title}

        # Resolve Math Template and generate formula ID (Safeguard 3)
        if slug in backlog_math_registry:
            template = backlog_math_registry[slug]
            print(f"  [GQS Stack] Using premium localized mathematical identity for '{slug}'.")
        else:
            template = MATH_TEMPLATES.get(shard_file, MATH_TEMPLATES["theoretical-physics.json"])
            
        hash_id = hashlib.md5(f"{slug}-identity-1".encode('utf-8')).hexdigest()[:8]
        formula_id = f"{slug}-identity-1-{hash_id}"
        identity_dict = {
            "id": formula_id,
            "title": template["title"],
            "equation": template["equation"],
            "description": template["description"]
        }


        # Calculate paragraph count target deterministically
        slug_hash = sum(ord(c) for c in slug)
        paragraphs_target = 4 + (slug_hash % 3)

        # Build Stack Entry
        entry_data = {
            "slug": slug,
            "title": title,
            "shard": shard_file,
            "frequency": item.get("frequency", 0),
            "paragraphs": paragraphs_target,
            "neighbors": neighbors_list,
            "bridge": bridge_dict,
            "identity": identity_dict,
            "status": "pending"
        }
        stack_data.append(entry_data)

    # Write GQS Stack to disk
    with open(GQS_PATH, "w") as f:
        json.dump(stack_data, f, indent=4)

    print(f"✓ SUCCESS: Central GQS Stack written to {GQS_PATH} ({len(stack_data)} nodes pre-resolved).")

    # Synchronize and update active_expansion_sprint.json to align with GQS stack
    active_sprint_path = "subfiles/active_expansion_sprint.json"
    ad_hoc_graduations = []
    
    if os.path.exists(active_sprint_path):
        try:
            with open(active_sprint_path, "r") as f:
                old_sprint = json.load(f)
                ad_hoc_graduations = old_sprint.get("ad_hoc_graduations", [])
                # If there were completed items in the old queue, move them to ad-hoc graduations
                for item in old_sprint.get("queue", []):
                    if item.get("status") == "completed":
                        # Prevent duplicate entries in ad-hoc
                        if not any(ah.get("slug") == item["slug"] for ah in ad_hoc_graduations):
                            from datetime import datetime
                            ad_hoc_graduations.append({
                                "slug": item["slug"],
                                "graduated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
        except Exception as e:
            print(f"Warning: Failed to load old sprint tracker: {e}")

    # Generate new queue structure for active_expansion_sprint.json
    sprint_queue = []
    shards_involved = set()
    for entry in stack_data:
        sprint_queue.append({
            "slug": entry["slug"],
            "title": entry["title"],
            "shard": entry["shard"],
            "frequency": entry["frequency"],
            "status": "pending"
        })
        shards_involved.add(entry["shard"])

    active_target = sprint_queue[0]["slug"] if sprint_queue else None
    
    from datetime import datetime
    new_sprint_data = {
        "sprint_id": "gqs_active_stack",
        "theme": "Graduation Queue Stack (GQS) Pipeline",
        "phase": "Graduation Queue Stack (GQS)",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "shards_involved": sorted(list(shards_involved)),
        "queue": sprint_queue,
        "active_target": active_target,
        "notes": "Managed automatically by the Graduation Queue Stack (GQS) pipeline. Refilled via generate_sprint_queue.py.",
        "ad_hoc_graduations": ad_hoc_graduations
    }

    with open(active_sprint_path, "w") as f:
        json.dump(new_sprint_data, f, indent=4)
        f.write("\n")

    print(f"✓ SUCCESS: Synced and updated {active_sprint_path} with {len(sprint_queue)} active GQS nodes.")

if __name__ == "__main__":
    main()
