#!/usr/bin/env python3
import os
import sys
import json
import re

# Add project root to sys.path to allow loading orchestrator
sys.path.append(os.getcwd())

try:
    from orchestrator import PhysicsOrchestrator
except ImportError:
    print("Error: Could not import PhysicsOrchestrator. Ensure you run this script from the project root directory.")
    sys.exit(1)

def normalize_slug(text):
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s]+', '-', s)
    return s

# Pre-defined MathJax identity templates matching physical disciplines
MATHJAX_TEMPLATES = {
    "classical-mechanics.json": [
        {
            "id": "euler-lagrange-equation",
            "title": "Euler-Lagrange Equation of Motion",
            "equation": "\\frac{d}{dt} \\left( \\frac{\\partial L}{\\partial \\dot{q}_i} \\right) - \\frac{\\partial L}{\\partial q_i} = 0",
            "interpretation": "The Euler-Lagrange equations establish the critical path of stationary action in configuration space, dictating the classical trajectory of a dynamical system under generalized coordinate constraints.",
            "symmetry_origin": "Derived directly from Hamilton's Principle of Least Action, asserting that the physical path taken by a system is an extremum of the action integral.",
            "limits_and_boundary": "Valid for conservative holonomic systems. Under non-conservative forces, generalized forces Q_i must be added to the right-hand side.",
            "semantic_variables": {
                "L": "Lagrangian function defined as kinetic minus potential energy (T - V)",
                "q_i": "Generalized coordinates parameterizing the system configuration space",
                "\\dot{q}_i": "Generalized velocities representing the first time-derivative of coordinates"
            }
        }
    ],
    "quantum-physics.json": [
        {
            "id": "schrodinger-equation",
            "title": "Time-Dependent Schrödinger Equation",
            "equation": "i\\hbar \\frac{\\partial}{\\partial t} |\\Psi(t)\\rangle = \\hat{H} |\\Psi(t)\\rangle",
            "interpretation": "The Schrödinger equation governs the continuous, unitary time-evolution of a quantum system's state vector within a complex Hilbert space.",
            "symmetry_origin": "Rooted in the time-translation invariance of physical laws, mapping the Hamiltonian operator as the generator of temporal translations.",
            "limits_and_boundary": "Valid in the non-relativistic regime. In high-energy regimes, this must be upgraded to the Dirac or Klein-Gordon covariant wave equations.",
            "semantic_variables": {
                "i": "Imaginary unit satisfying i^2 = -1",
                "\\hbar": "Reduced Planck constant establishing the scale of quantum action",
                "|\\Psi(t)\\rangle": "State vector representing the quantum state in Hilbert space",
                "\\hat{H}": "Hamiltonian operator representing the total energy of the system"
            }
        }
    ],
    "relativity.json": [
        {
            "id": "einstein-field-equations",
            "title": "Einstein Field Equations",
            "equation": "G_{\\mu\\nu} + \\Lambda g_{\\mu\\nu} = \\frac{8\\pi G}{c^4} T_{\\mu\\nu}",
            "interpretation": "The field equations establish the geometric feedback loop of general relativity, asserting that mass-energy density curves spacetime, while spacetime curvature dictates the geodesic motion of mass-energy.",
            "symmetry_origin": "Constructed from the general covariance of pseudo-Riemannian manifolds, requiring the field equations to be tensor equations under arbitrary coordinate transformations.",
            "limits_and_boundary": "Reduces to Newtonian gravitation in the weak-field, slow-motion limit (non-relativistic limit) and asymptotically approaches flat Minkowski space.",
            "semantic_variables": {
                "G_{\\mu\\nu}": "Einstein tensor representing the curvature of spacetime",
                "g_{\\mu\\nu}": "Metric tensor describing the pseudo-Riemannian spacetime geometry",
                "\\Lambda": "Cosmological constant representing vacuum energy density",
                "T_{\\mu\\nu}": "Stress-energy-momentum tensor representing the density of mass, energy, and momentum flow"
            }
        }
    ],
    "thermodynamics-statistical-mechanics.json": [
        {
            "id": "boltzmann-entropy",
            "title": "Boltzmann Entropy Relation",
            "equation": "S = k_B \\ln \\Omega",
            "interpretation": "The Boltzmann entropy relation connects the macroscopic thermodynamic state of a system to its microscopic statistical configurations, quantifying thermodynamic entropy as the logarithmic measure of available microstates.",
            "symmetry_origin": "Originates from the fundamental postulate of statistical mechanics, asserting that all accessible microstates are equally probable in a microcanonical ensemble.",
            "limits_and_boundary": "Valid for macroscopic systems containing large numbers of degrees of freedom. Fluctuations about the mean become significant at nanoscopic scales.",
            "semantic_variables": {
                "S": "Thermodynamic entropy representing molecular disorder",
                "k_B": "Boltzmann constant linking temperature to microscopic energy",
                "\\Omega": "Number of microstates corresponding to the observed macrostate"
            }
        }
    ],
    "electromagnetism.json": [
        {
            "id": "maxwell-faraday-equation",
            "title": "Maxwell-Faraday Equation",
            "equation": "\\nabla \\times \\mathbf{E} = -\\frac{\\partial \\mathbf{B}}{\\partial t}",
            "interpretation": "The Maxwell-Faraday equation states that a time-varying magnetic field induces a spatially circulating, non-conservative electric field.",
            "symmetry_origin": "Expresses Faraday's law of induction in differential form, demonstrating a fundamental unification between the vector electric and magnetic field topologies.",
            "limits_and_boundary": "Maintains exact relativistic covariance. Subject to quantum electrodynamic (QED) vacuum polarization corrections under extreme field strengths.",
            "semantic_variables": {
                "\\nabla \\times": "Curl operator representing field circulation density",
                "\\mathbf{E}": "Electric field vector",
                "\\mathbf{B}": "Magnetic flux density vector",
                "t": "Temporal coordinate"
            }
        }
    ],
    "astrophysics.json": [
        {
            "id": "schwarzschild-radius",
            "title": "Schwarzschild Gravitational Radius",
            "equation": "R_s = \\frac{2GM}{c^2}",
            "interpretation": "The Schwarzschild radius defines the spherical event horizon of a non-rotating, spherically symmetric black hole, representing the boundary where the escape velocity equals the speed of light.",
            "symmetry_origin": "Derived as the singular coordinate boundary of the vacuum Schwarzschild metric under complete spherical symmetry.",
            "limits_and_boundary": "Valid for static, uncharged stellar masses. Upgraded to Kerr metric horizons for rotating stellar configurations.",
            "semantic_variables": {
                "R_s": "Schwarzschild event horizon radius",
                "G": "Newtonian gravitational constant",
                "M": "Total mass of the gravitating body",
                "c": "Speed of light in vacuum"
            }
        }
    ],
    "standard-model.json": [
        {
            "id": "dirac-covariant-equation",
            "title": "Covariant Dirac Equation",
            "equation": "(i\\gamma^\\mu \\partial_\\mu - m)\\psi = 0",
            "interpretation": "The Dirac equation provides the fully relativistic description of spin-1/2 fermions, predicting the existence of antimatter and naturally incorporating spin quantum states.",
            "symmetry_origin": "Constructed from the requirement that the wave equation be first-order in both space and time derivatives to satisfy Lorentz covariance.",
            "limits_and_boundary": "Reduces to the Pauli Schrödinger equation in the non-relativistic limit. Generates infinite negative-energy states resolved by Dirac sea or QFT field quantization.",
            "semantic_variables": {
                "\\gamma^\\mu": "Dirac matrices satisfying the Clifford algebra anti-commutation relations",
                "\\partial_\\mu": "Four-gradient operator",
                "m": "Rest mass of the fermion",
                "\\psi": "Four-component Dirac spinor wave function"
            }
        }
    ],
    "philosophy-of-physics.json": [
        {
            "id": "bell-inequality",
            "title": "CHSH Bell Inequality",
            "equation": "|E(a,b) - E(a,b') + E(a',b) + E(a',b')| \\leq 2",
            "interpretation": "The CHSH Bell inequality establishes a rigid mathematical ceiling for correlations obtainable by any local-realist hidden variable theory.",
            "symmetry_origin": "Derived from the dual assumptions of local action and counterfactual definiteness.",
            "limits_and_boundary": "Violated up to the Tsirelson bound of 2\\sqrt{2} by quantum entangled states, proving the non-local character of quantum reality.",
            "semantic_variables": {
                "E(a,b)": "Expectation value of joint measurements at detector settings a and b",
                "a, a'": "Measurement settings for the first detector",
                "b, b'": "Measurement settings for the second detector"
            }
        }
    ]
}

# Default generic template if a shard doesn't have custom ones
DEFAULT_TEMPLATE = [
    {
        "id": "generic-conservation-law",
        "title": "Generalized Local Conservation Relation",
        "equation": "\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot \\mathbf{J} = 0",
        "interpretation": "This relation expresses that the local time-rate of change of a conserved density is exactly balanced by the divergence of its current density flux.",
        "symmetry_origin": "Directly mandated by Noether's theorem, asserting that continuous global symmetries correspond to conserved currents.",
        "limits_and_boundary": "Maintains universal validity across classical, relativistic, and quantum fields assuming isolated systems.",
        "semantic_variables": {
            "\\rho": "Conserved quantity density (charge, mass, energy, probability)",
            "\\mathbf{J}": "Flux current density vector of the conserved quantity",
            "\\nabla \\cdot": "Divergence operator mapping flow density"
        }
    }
]

def load_backlog():
    backlog_path = "subfiles/expansion_backlog.json"
    if os.path.exists(backlog_path):
        with open(backlog_path, 'r') as f:
            return json.load(f)
    return []

def select_shard_interactive(orch):
    shards = sorted(list(set(orch.slug_to_shard.values())))
    print("\nNo auto-shard could be resolved. Please select a parent physics shard from the list:")
    for idx, shard in enumerate(shards):
        print(f"  {idx + 1:2d}) {shard}")
    
    while True:
        try:
            choice = input(f"Select parent shard (1-{len(shards)}): ").strip()
            if not choice: continue
            val = int(choice)
            if 1 <= val <= len(shards):
                return shards[val - 1]
        except ValueError:
            pass
        print(f"Invalid choice. Please enter a number between 1 and {len(shards)}.")

def find_term_mentions(term, orch):
    """Searches through all existing subtopics to find which shard mentions this term the most."""
    shard_counts = {}
    term_pattern = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
    
    for sub_slug, sub_data in orch.data["subtopics"].items():
        content = sub_data.get("content", "")
        matches = len(term_pattern.findall(content))
        if matches > 0:
            shard = orch.slug_to_shard.get(sub_slug)
            if shard:
                shard_counts[shard] = shard_counts.get(shard, 0) + matches
                
    if shard_counts:
        # Return shard with maximum occurrences of the term
        sorted_shards = sorted(shard_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_shards[0][0]
    return None

def resolve_topology_links(target_slug, shard_name, orch):
    """Identifies 5 nearest neighbors in the same shard, and 1 bridge in a different hub."""
    # Find all topics in the same shard
    same_shard_slugs = [slug for slug, sh in orch.slug_to_shard.items() if sh == shard_name and slug != target_slug]
    
    # Let's filter to subtopics that are already platinum
    platinum_same_shard = [slug for slug in same_shard_slugs if orch.data["subtopics"].get(slug, {}).get("standard") == "platinum"]
    
    # Fallback to any active subtopic if we don't have enough platinum ones
    candidates = platinum_same_shard if len(platinum_same_shard) >= 5 else same_shard_slugs
    
    # Grab up to 5 neighboring slugs
    neighbors = candidates[:5]
    while len(neighbors) < 5 and same_shard_slugs:
        # If still short, backfill from same_shard_slugs
        for s in same_shard_slugs:
            if s not in neighbors:
                neighbors.append(s)
            if len(neighbors) == 5:
                break
                
    # If the shard has fewer than 5 subtopics total, backfill from other shards
    if len(neighbors) < 5:
        all_slugs = list(orch.data["subtopics"].keys())
        for s in all_slugs:
            if s != target_slug and s not in neighbors:
                neighbors.append(s)
            if len(neighbors) == 5:
                break

    # Resolve 1 Cross-Hub Bridge: find a slug in a different shard
    bridge_slug = None
    all_shards = set(orch.slug_to_shard.values())
    other_shards = [sh for sh in all_shards if sh != shard_name]
    
    for osh in other_shards:
        osh_slugs = [slug for slug, sh in orch.slug_to_shard.items() if sh == osh and orch.data["subtopics"].get(slug, {}).get("standard") == "platinum"]
        if osh_slugs:
            bridge_slug = osh_slugs[0]
            break
            
    if not bridge_slug:
        # Fallback to any slug in a different shard
        for osh in other_shards:
            osh_slugs = [slug for slug, sh in orch.slug_to_shard.items() if sh == osh]
            if osh_slugs:
                bridge_slug = osh_slugs[0]
                break
                
    if not bridge_slug:
        # Complete fallback
        bridge_slug = "four-momentum" # standard relativity topic
        
    return neighbors, bridge_slug

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bootstrap_expansion.py [term_or_slug]")
        print("Example: python3 bootstrap_expansion.py \"Block Universe\"")
        print("Example: python3 bootstrap_expansion.py relativistic-thermodynamics")
        sys.exit(1)

    input_arg = sys.argv[1].strip()
    
    # 1. Initialize orchestrator
    print("Loading Physics Registry and Orchestrator state...")
    orch = PhysicsOrchestrator()
    
    # 2. Match Slug and Term
    backlog = load_backlog()
    backlog_match = None
    
    # Standardize input
    normalized_input = normalize_slug(input_arg)
    
    # Try direct slug lookup in backlog
    for item in backlog:
        if item.get("suggested_slug") == normalized_input or item.get("term", "").lower() == input_arg.lower():
            backlog_match = item
            break
            
    if backlog_match:
        term = backlog_match.get("term")
        slug = backlog_match.get("suggested_slug")
        print(f"Matched Backlog Candidate: '{term}' (frequency: {backlog_match.get('frequency')}) -> slug: {slug}")
    else:
        # Custom term
        slug = normalized_input
        term = input_arg
        print(f"Scaffolding custom physical subtopic: '{term}' -> slug: {slug}")
        
    # Check if slug already exists in subtopics
    existing_node = orch.data["subtopics"].get(slug)
    if existing_node:
        if existing_node.get("standard") == "platinum":
            print(f"WARNING: The subtopic '{slug}' is already marked as 'platinum' in the shard.")
            overwrite = input("Do you still want to scaffold it (y/n)? ").strip().lower()
            if overwrite != 'y':
                print("Aborting.")
                sys.exit(0)
        else:
            print(f"Found existing unfinished subtopic '{slug}' in database. Will scaffold fresh draft.")

    # 3. Determine Parent Shard
    shard_name = None
    if existing_node:
        shard_name = orch.slug_to_shard.get(slug)
    else:
        # Search which shard mentions this term the most
        print(f"Scanning existing shards for mentions of '{term}' to identify parent category...")
        shard_name = find_term_mentions(term, orch)
        
    if shard_name:
        print(f"Auto-resolved Parent Shard: {shard_name} based on occurrence density.")
    else:
        # Fallback to interactive choice
        shard_name = select_shard_interactive(orch)

    # 4. Resolve Topology
    print("Calculating nearest topological neighbor links for Small-World Connectivity...")
    neighbors, bridge_slug = resolve_topology_links(slug, shard_name, orch)
    
    print(f"Resolved Neighbors (Same Shard):")
    for n in neighbors:
        title = next((t for t, s in orch.registry.items() if s == n), n)
        print(f"  - {title} ({n})")
    print(f"Resolved Cross-Hub Bridge: {bridge_slug}")

    # 5. Scaffold Identities
    print("Constructing senior-level theoretical identities based on discipline...")
    identities_list = MATHJAX_TEMPLATES.get(shard_name, DEFAULT_TEMPLATE)
    
    # Customize the identities list to match the current slug
    for idx, item in enumerate(identities_list):
        item['id'] = f"{slug}-identity-{idx + 1}"
        
    # Write identities.json to project root
    identities_path = "identities.json"
    with open(identities_path, "w") as f:
        json.dump(identities_list, f, indent=4)
    print(f"✓ Identities scaffolding saved to {identities_path}")

    # 6. Scaffold draft.html
    # Let's generate titles and anchors for neighbors and bridges
    neighbor_links_html = []
    for n in neighbors:
        title = next((t for t, s in orch.registry.items() if s == n), n)
        neighbor_links_html.append(f'<a href="/physics/subtopic/{n}" class="subtopic-link"><strong>{title}</strong></a>')
        
    bridge_title = next((t for t, s in orch.registry.items() if s == bridge_slug), bridge_slug)
    bridge_link_html = f'<a href="/physics/subtopic/{bridge_slug}" class="subtopic-link"><strong>{bridge_title}</strong></a>'

    # Build warning and draft content
    draft_html_content = f"""<!-- 
  =============================================================================
  PLATINUM GRADUATION DRAFT: {slug}
  =============================================================================
  DIRECTIONS FOR UNIVERSITY-LEVEL GRADUATION (OPS MANDATES):
  
  1. THE "IN MEDIA RES" LEAD:
     The first sentence MUST lead directly with a physical principle, identity,
     or derivation. Do NOT start with "The [Topic] is..." or "This concept refers to...".
     Do NOT mention the topic title in the first 15 words of the prose.
     
  2. ZERO-ARTIFACT CONTINUOUS PROSE:
     Use ONLY high-density, academic paragraphs. Absolutely NO bullet points, 
     numbered lists, or structural headers separating the text. 
     Connect all concepts through logical transition sentences explaining the relationships.
     All paragraphs MUST be wrapped in standard <p>...</p> tags.
     
  3. MATHEMATICAL DENSITY:
     Ensure a high density of MathJax equations: Inline \\( ... \\) and Display \\[ ... \\].
     Derive physical properties and calculate, do not just describe!
     
  4. THE LIMITING CASE CLAUSE:
     You MUST mathematically demonstrate the limiting case (e.g., how the relativistic 
     model reduces to classical Newtonian gravity, or thermodynamic limits).
     
  5. SMALL-WORLD CONNECTIVITY:
     Integrate links to at least 5 subtopics and 1 cross-hub bridge in the text.
     Pre-calculated targets have been generated below.
     
  6. NO MARKDOWN BOLD (**):
     You are strictly forbidden from using markdown bold (**) inside HTML text.
     Use standard HTML <strong> tags.
  =============================================================================
-->

<p>
  The topological invariance of the physical state-space coordinates under generalized dynamical symmetries dictates that the primary phase-space density must satisfy a covariant evolution equation. In particular, this necessitates an organic integration of the fundamental physical parameters, demonstrating that
  \\[
     {identities_list[0]['equation']}
  \\]
  which directly governs the local space-time progression of the system.
</p>

<p>
  Under rigorous analytic formulation, we define the constituent fields of this equation to establish the exact boundaries of physical observables. The operator manifolds represent coordinate actions, where each variable correlates with a continuous structural degree of freedom. By examining the symmetry origins of these transformations, we prove that conservation laws are locally invariant under coordinate rotations.
</p>

<p>
  In the limiting case, the generalized covariant behavior asymptotically collapses to the classical framework. Specifically, as the quantum perturbation parameter approaches zero, or as the velocity ratio satisfies the weak-field restriction \\( v/c \\ll 1 \\), the non-linear curvature tensors simplify into standard linear derivatives, yielding the classical Newtonian limit of force coordinates.
</p>

<p>
  To resolve the broader topological network, this physical system integrates dynamically with other curricular nodes. The spatial boundaries link directly with {neighbor_links_html[0]}, which establishes the background configuration. Further, the local potentials map onto {neighbor_links_html[1]} and influence the structural stability of {neighbor_links_html[2]}. These interactions are deeply symmetric, sharing energy coordinate exchanges with both {neighbor_links_html[3]} and {neighbor_links_html[4]}. Crucially, the mathematical foundation bridges disciplines, transferring thermodynamic entropic states to the study of {bridge_link_html}, which resolves local vacuum singularities across separate pillar hubs.
</p>
"""

    draft_path = "draft.html"
    with open(draft_path, "w") as f:
        f.write(draft_html_content)
    print(f"✓ Prose drafting template saved to {draft_path}")

    # 7. Update global_slug_registry.json if not present
    registry_path = "global_slug_registry.json"
    modified_registry = False
    
    # Check if title already mapped
    if term not in orch.registry and slug not in orch.registry.values():
        with open(registry_path, "r") as f:
            registry_data = json.load(f)
            
        registry_data[term] = slug
        with open(registry_path, "w") as f:
            json.dump(registry_data, f, indent=4)
            
        print(f"✓ Registered '{term}' -> '{slug}' in global_slug_registry.json")
        modified_registry = True
        
    # 8. Check if the subtopic exists in the shard. If not, add a blank one!
    shard_path = os.path.join("app/config/content", shard_name)
    with open(shard_path, "r") as f:
        shard_data = json.load(f)
        
    if slug not in shard_data:
        # Create blank pending node
        shard_data[slug] = {
            "title": term,
            "content": "",
            "standard": "pending",
            "snippet": "",
            "parents": [shard_name.replace(".json", "")],
            "formula_ids": []
        }
        with open(shard_path, "w") as f:
            json.dump(shard_data, f, indent=4)
        print(f"✓ Created pending subtopic node '{slug}' inside shard '{shard_name}'")

    print("\n=========================================================================")
    print("⚡ SCAFFOLDING COMPLETED SUCCESSFULLY")
    print("=========================================================================")
    print(f"1. Prose draft template:  [draft.html](file://{os.path.abspath(draft_path)})")
    print(f"2. Physical identities:   [identities.json](file://{os.path.abspath(identities_path)})")
    print(f"3. Target Shard:          {shard_path}")
    print("=========================================================================")
    print("NEXT STEPS:")
    print("  a) Open and refine the prose in `draft.html` and the formulas in `identities.json`.")
    print("  b) Ensure your prose is highly dense, between 650 to 1,000 words, and is academic.")
    print("  c) Trigger the watcher graduation by creating a trigger file in `scripts/maintenance/inbox/`:")
    print(f"     e.g. Write '{{\"slug\": \"{slug}\", \"html\": \"draft.html\", \"identities\": \"identities.json\"}}' to scripts/maintenance/inbox/{slug}.json")
    print(f"  d) Alternatively, run the commit script directly:")
    print(f"     python3 scripts/maintenance/commit_node.py {slug} draft.html identities.json")
    print("=========================================================================")

if __name__ == "__main__":
    main()
