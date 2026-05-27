#!/usr/bin/env python3
import json
import os
import sys
import re
import hashlib

def normalize_slug(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s

def main():
    # Detect batch mode and extract flags to preserve slug parsing compatibility
    batch_mode = False
    if "--batch" in sys.argv:
        batch_mode = True
        sys.argv.remove("--batch")
    elif "-b" in sys.argv:
        batch_mode = True
        sys.argv.remove("-b")

    if len(sys.argv) < 2:
        print("Usage: python3 bootstrap_expansion.py <term_name_or_slug> [parent_shard.json] [--batch | -b]")
        sys.exit(1)
        
    raw_target = sys.argv[1]
    slug = normalize_slug(raw_target)
    
    # 1. Paths configuration
    content_dir = "app/config/content"
    search_index_path = os.path.join(content_dir, "search_index.json")
    formulas_path = os.path.join(content_dir, "formulas.json")
    entities_path = os.path.join(content_dir, "entities.json")
    categories_path = os.path.join(content_dir, "categories.json")
    
    # Verify paths exist
    if not os.path.exists(search_index_path):
        print(f"Error: search_index.json not found at {search_index_path}")
        sys.exit(1)
        
    with open(search_index_path, "r") as f:
        search_index = json.load(f)
        
    # 2. Shard Resolution
    shard_file = None
    title = raw_target
    
    # If user provided a specific parent shard argument
    if len(sys.argv) > 2:
        shard_file = sys.argv[2]
        if not shard_file.endswith(".json"):
            shard_file += ".json"
    else:
        # Resolve via search index or backlog
        entry = search_index.get(slug)
        if entry:
            if isinstance(entry, dict):
                shard_file = entry.get("s")
                title = entry.get("t", title)
            elif isinstance(entry, str):
                shard_file = entry
        
        # Check expansion backlog if still not found
        backlog_path = "subfiles/expansion_backlog.json"
        if not shard_file and os.path.exists(backlog_path):
            with open(backlog_path, "r") as f:
                backlog = json.load(f)
            for item in backlog:
                if item.get("suggested_slug") == slug:
                    title = item.get("term", title)
                    break
                    
    # Fallback to theoretical-physics.json if totally unresolved
    if not shard_file:
        shard_file = "theoretical-physics.json"
        print(f"Target shard unresolved. Defaulting to: {shard_file}")
        
    print(f"Target Slug:  {slug}")
    print(f"Target Title: {title}")
    print(f"Parent Shard: {shard_file}")

    # 3. Find 5 Hub Neighbors
    all_neighbors = []
    for s, data in search_index.items():
        if s == slug: continue
        if isinstance(data, dict) and data.get("s") == shard_file:
            all_neighbors.append((s, data.get("t", s)))
            
    # Sort neighbors to ensure deterministic/popular selection
    all_neighbors.sort(key=lambda x: len(x[1]), reverse=True)
    
    selected_neighbors = all_neighbors[:5]
    while len(selected_neighbors) < 5:
        # Fallback padding if shard is small
        selected_neighbors.append(("theoretical-physics-overview", "Theoretical Physics Overview"))
        
    print(f"Selected Neighbors:")
    for n_slug, n_title in selected_neighbors:
        print(f"  - {n_title} ({n_slug})")
        
    # 4. Cross-Hub Bridge Mapping
    BRIDGES = {
        "thermodynamics-statistical-mechanics.json": ("minkowski-metric", "Minkowski Metric"),
        "relativity.json": ("hamiltons-principle", "Hamilton's Principle"),
        "quantum-physics.json": ("background-independence", "Background Independence"),
        "astrophysics.json": ("energy-momentum-relation", "Energy-Momentum Relation"),
        "classical-mechanics.json": ("entropy", "Entropy"),
        "philosophy-of-physics.json": ("minkowski-metric", "Minkowski Metric")
    }
    bridge_slug, bridge_title = BRIDGES.get(shard_file, ("minkowski-metric", "Minkowski Metric"))
    print(f"Selected Bridge:    {bridge_title} ({bridge_slug})")
    
    # 5. Math Identity Scaffolding
    MATH_TEMPLATES = {
        "thermodynamics-statistical-mechanics.json": {
            "title": "Canonical Partition Function and Phase Space Density",
            "equation": "\\[ Z = \\int e^{-\\beta H(\\mathbf{q}, \\mathbf{p})} \\frac{d^N \\mathbf{q} \\, d^N \\mathbf{p}}{h^{3N}} \\]",
            "description": "Defines the canonical partition function by integrating the Boltzmann factor over the classical phase space volume element."
        },
        "relativity.json": {
            "title": "Invariant Spacetime Interval",
            "equation": "\\[ ds^2 = g_{\\mu\\nu} d x^\\mu d x^\\nu \\]",
            "description": "Establishes the invariant metric interval under general coordinate transformations."
        },
        "quantum-physics.json": {
            "title": "Schrödinger Time Evolution Operator",
            "equation": "\\[ U(t, t_0) = e^{-i H (t - t_0) / \\hbar} \\]",
            "description": "Defines the unitary time-evolution operator for a time-independent Hamiltonian."
        },
        "theoretical-physics.json": {
            "title": "Euler-Lagrange Field Equation",
            "equation": "\\[ \\partial_\\mu \\left( \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\right) - \\frac{\\partial \\mathcal{L}}{\\partial \\phi} = 0 \\]",
            "description": "Derives the equations of motion for a continuous field from the extremization of the action."
        },
        "classical-mechanics.json": {
            "title": "Hamilton's Canonical Equations of Motion",
            "equation": "\\[ \\dot{q}_i = \\frac{\\partial H}{\\partial p_i}, \\quad \\dot{p}_i = -\\frac{\\partial H}{\\partial q_i} \\]",
            "description": "Establishes the canonical equations governing particle trajectories in classical phase space."
        }
    }
    
    template = MATH_TEMPLATES.get(shard_file, MATH_TEMPLATES["theoretical-physics.json"])
    # Generate unique formula ID using target slug hash
    hash_id = hashlib.md5(f"{slug}-identity-1".encode('utf-8')).hexdigest()[:8]
    formula_id = f"{slug}-identity-1-{hash_id}"
    
    identities_data = [
        {
            "id": formula_id,
            "title": template["title"],
            "equation": template["equation"],
            "description": template["description"]
        }
    ]
    
    # 6. Scaffold draft.html content
    html_content = f"""<!-- 
  =========================================================================
  DRAFT GRADUATION FILE FOR: {title} ({slug})
  STANDARD: Organic Platinum Standard (OPS)
  RULES & DIRECTIVES:
  1. In Media Res Lead: Start FIRST paragraph immediately with a physical principle.
     DO NOT start with "{title} is..." or "This concept refers to...".
     DO NOT use "{title}" in the first 15 words.
  2. Technical density: 650 to 1,000 words. RIGOROUS academic prose (senior undergraduate).
  3. No lists or bullet points: Wrap ALL narrative in <p> tags.
  4. Bold key terms using <strong>...</strong> only. NO markdown double asterisks (**).
  5. Satisfy the Limiting Case: Mathematically or conceptually outline a transition/limit.
  =========================================================================
-->

<p>
  [START IN MEDIA RES: Introduce a core physical principle or differential equation governing the system...]
  For this target, the mathematical skeleton maps onto the physical identities defined in 
  the associated formula <a href="/physics/subtopic/{selected_neighbors[0][0]}" class="subtopic-link"><strong>{selected_neighbors[0][1]}</strong></a>.
</p>

<p>
  [DEVELOPMENT PARAGRAPH: Elaborate on the mechanical, fields, or thermodynamic dynamics...]
  These properties establish the foundational principles governing the behavior of
  <a href="/physics/subtopic/{selected_neighbors[1][0]}" class="subtopic-link"><strong>{selected_neighbors[1][1]}</strong></a>
  and shape the topological configurations of
  <a href="/physics/subtopic/{selected_neighbors[2][0]}" class="subtopic-link"><strong>{selected_neighbors[2][1]}</strong></a>.
</p>

<p>
  [DEVELOPMENT PARAGRAPH: Discuss physical conservation laws, symmetries, or variational methods...]
  Under these boundary constraints, the local fluctuations correspond to the dynamics of
  <a href="/physics/subtopic/{selected_neighbors[3][0]}" class="subtopic-link"><strong>{selected_neighbors[3][1]}</strong></a>
  and diagonalize the state variables of
  <a href="/physics/subtopic/{selected_neighbors[4][0]}" class="subtopic-link"><strong>{selected_neighbors[4][1]}</strong></a>.
</p>

<p>
  [LIMITING CASE PARAGRAPH: Detail the mathematical limiting case/boundary approximation...]
  In the classical approximation limit where the physical coupling constant approaches zero or under flat asymptotes,
  this curved coordinate structure reduces cleanly to the flat tangent boundaries defined by the
  <a href="/physics/subtopic/{bridge_slug}" class="subtopic-link"><strong>{bridge_title}</strong></a>.
  This smooth transition guarantees invariant conservation across all local reference manifolds.
</p>
"""

    # Write files to disk
    draft_path = f"draft_{slug}.html" if batch_mode else "draft.html"
    identities_path_out = f"identities_{slug}.json" if batch_mode else "identities.json"

    with open(draft_path, "w") as f:
        f.write(html_content)
    print(f"SCAFFOLD: Successfully wrote {draft_path} to workspace.")
    
    with open(identities_path_out, "w") as f:
        json.dump(identities_data, f, indent=4)
    print(f"SCAFFOLD: Successfully wrote {identities_path_out} to workspace.")
    
    # 7. Print operational tips
    print("\n" + "="*60)
    print("SCAFFOLD COMPLETE & READY FOR GRADUATION!")
    print("="*60)
    print(f"1. Open the file '{draft_path}' in your editor and compose the prose.")
    print(f"2. Open '{identities_path_out}' to review/edit the scaffolded physical identity.")
    if batch_mode:
        print(f"3. Compile this node alongside others using the batch orchestrator:")
        print(f"   .venv/bin/python3 scripts/maintenance/batch_graduate.py {slug}")
    else:
        print(f"3. Run the compiler once finished to graduate the subtopic:")
        print(f"   .venv/bin/python3 scripts/maintenance/commit_node.py {slug} {draft_path} {identities_path_out}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
