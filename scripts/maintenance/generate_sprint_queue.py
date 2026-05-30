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
        "title": "Canonical Partition Function and Phase Space Density",
        "equation": "Z = \\int e^{-\\beta H(\\mathbf{q}, \\mathbf{p})} \\frac{d^N \\mathbf{q} \\, d^N \\mathbf{p}}{h^{3N}}",
        "description": "Defines the canonical partition function by integrating the Boltzmann factor over the classical phase space volume element."
    },
    "relativity.json": {
        "title": "Invariant Spacetime Interval",
        "equation": "ds^2 = g_{\\mu\\nu} d x^\\mu d x^\\nu",
        "description": "Establishes the invariant metric interval under general coordinate transformations."
    },
    "quantum-physics.json": {
        "title": "Schrödinger Time Evolution Operator",
        "equation": "U(t, t_0) = e^{-i H (t - t_0) / \\hbar}",
        "description": "Defines the unitary time-evolution operator for a time-independent Hamiltonian."
    },
    "theoretical-physics.json": {
        "title": "Euler-Lagrange Field Equation",
        "equation": "\\partial_\\mu \\left( \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\right) - \\frac{\\partial \\mathcal{L}}{\\partial \\phi} = 0",
        "description": "Derives the equations of motion for a continuous field from the extremization of the action."
    },
    "classical-mechanics.json": {
        "title": "Hamilton's Canonical Equations of Motion",
        "equation": "\\dot{q}_i = \\frac{\\partial H}{\\partial p_i}, \\quad \\dot{p}_i = -\\frac{\\partial H}{\\partial q_i}",
        "description": "Establishes the canonical equations governing particle trajectories in classical phase space."
    },
    "electromagnetism.json": {
        "title": "Maxwell-Ampère Law with Displacement Current",
        "equation": "\\nabla \\times \\mathbf{B} = \\mu_0 \\mathbf{J} + \\mu_0 \\varepsilon_0 \\frac{\\partial \\mathbf{E}}{\\partial t}",
        "description": "Formulates the generation of magnetic fields from electric currents and time-varying electric fields."
    },
    "astrophysics.json": {
        "title": "Friedmann Equation for Cosmic Expansion",
        "equation": "\\left(\\frac{\\dot{a}}{a}\\right)^2 = \\frac{8\\pi G}{3}\\rho - \\frac{k c^2}{a^2} + \\frac{\\Lambda c^2}{3}",
        "description": "Governs the expansion rate of the universe based on its energy-density components, spatial curvature, and cosmological constant."
    },
    "philosophy-of-physics.json": {
        "title": "Heisenberg Uncertainty Principle",
        "equation": "\\sigma_x \\sigma_p \\ge \\frac{\\hbar}{2}",
        "description": "Sets the fundamental limit of precision with which certain pairs of physical properties of a particle can be known simultaneously."
    },
    "standard-model.json": {
        "title": "Covariant Dirac Equation",
        "equation": "(i \\gamma^\\mu D_\\mu - m)\\psi = 0",
        "description": "Describes the relativistic quantum mechanics of spin-1/2 fermions interacting with gauge fields."
    },
    "fluids-nonlinear.json": {
        "title": "Incompressible Navier-Stokes Equations",
        "equation": "\\rho \\left(\\frac{\\partial \\mathbf{u}}{\\partial t} + \\mathbf{u} \\cdot \\nabla \\mathbf{u}\\right) = -\\nabla p + \\mu \\nabla^2 \\mathbf{u}",
        "description": "Governs the motion of viscous, incompressible fluid substances under spatial velocity and pressure gradients."
    },
    "mathematical-methods.json": {
        "title": "Generalized Fourier Transform",
        "equation": "\\hat{f}(\\xi) = \\int_{-\\infty}^{\\infty} f(x) e^{-2\\pi i x \\xi} dx",
        "description": "Transforms a spatial or temporal function into its constituent spectral frequency components."
    },
    "condensed-matter.json": {
        "title": "Bloch Particle Wavefunction",
        "equation": "\\psi_{\\mathbf{k}}(\\mathbf{r}) = e^{i \\mathbf{k} \\cdot \\mathbf{r}} u_{\\mathbf{k}}(\\mathbf{r})",
        "description": "Formulates the quantum wavefunction of a particle residing in a periodic potential structure like a crystal lattice."
    },
    "legacy-orphans.json": {
        "title": "Euler-Lagrange Field Equation",
        "equation": "\\partial_\\mu \\left( \\frac{\\partial \\mathcal{L}}{\\partial (\\partial_\\mu \\phi)} \\right) - \\frac{\\partial \\mathcal{L}}{\\partial \\phi} = 0",
        "description": "Derives the equations of motion for a continuous field from the extremization of the action."
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

        # Resolve Math Template and generate formula ID
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
