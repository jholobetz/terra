"""
Structural & Epistemic Integrity Gate for the Formula Derivation Graph
(app/config/formula_derivation_graph.json + .json.gz).

Enforces docs/mandate.md Anti-Goodhart Safeguards #1-#4:
  - Acyclic DAG (0 cycles), 0 dangling edges, 0 self-loops, JSON/GZIP parity
  - Safeguard #1: No star-hub packing (max direct derivation children <= 25)
  - Zero meta-domain ('philosophy-of-physics') hijacking on core-cited formulas
  - Golden Landmark Canary Table (~24 flagship equations across core domains)
  - CAS-verified flag integrity (>= 10,000 verified nodes)
  - Unit tests for Majority-Vote + Core-Domain Precedence in build_formula_graph.py
"""

import gzip
import json
import pathlib
from collections import Counter, defaultdict, deque

import pytest

from scripts.build_formula_graph import META_DOMAINS, _select_best_domain

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "app" / "config" / "content"
GRAPH_JSON = ROOT / "app" / "config" / "formula_derivation_graph.json"
GRAPH_GZ = ROOT / "app" / "config" / "formula_derivation_graph.json.gz"


@pytest.fixture(scope="module")
def graph():
    assert GRAPH_JSON.exists(), f"Missing {GRAPH_JSON}"
    return json.loads(GRAPH_JSON.read_text(encoding="utf-8"))


def test_graph_json_and_gzip_parity(graph):
    """Uncompressed JSON and gzipped production artifact must stay in exact sync."""
    assert GRAPH_GZ.exists(), f"Missing {GRAPH_GZ}"
    with gzip.open(GRAPH_GZ, "rt", encoding="utf-8") as fh:
        gz_graph = json.load(fh)
    assert len(graph["nodes"]) == len(gz_graph["nodes"])
    assert len(graph["links"]) == len(gz_graph["links"])
    assert len(graph["nodes"]) >= 15000


def test_dag_acyclicity_and_referential_integrity(graph):
    """All derivation edges must reference existing nodes, have no self-loops, and form a DAG."""
    nodes = graph["nodes"]
    deriv_links = [l for l in graph["links"] if l.get("type") == "derivation"]

    in_degree = defaultdict(int)
    adj = defaultdict(list)

    for link in deriv_links:
        src = link["source"]
        tgt = link["target"]
        assert src in nodes, f"Dangling link source: {src}"
        assert tgt in nodes, f"Dangling link target: {tgt}"
        assert src != tgt, f"Self-loop detected on {src}"
        adj[src].append(tgt)
        in_degree[tgt] += 1

    # Kahn's topological sort to guarantee 0 cycles
    q = deque(nid for nid in nodes if in_degree[nid] == 0)
    visited = 0
    while q:
        curr = q.popleft()
        visited += 1
        for nxt in adj.get(curr, []):
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                q.append(nxt)

    assert visited == len(nodes), f"Cycle detected in derivation DAG ({len(nodes) - visited} nodes in cycles)"


def test_no_star_hubs_safeguard_1(graph):
    """Mandate Safeguard #1: No single parent hub may pack > 25 direct derivation children."""
    out_counts = Counter(
        l["source"] for l in graph["links"] if l.get("type") == "derivation"
    )
    offenders = {pid: cnt for pid, cnt in out_counts.items() if cnt > 25}
    assert not offenders, f"Star-hub violation (>25 children): {offenders}"


def test_no_meta_domain_hijack_on_core_cited_formulas(graph):
    """No formula directly cited by any core physics domain file may be tagged philosophy-of-physics."""
    categories = json.loads((CONTENT_DIR / "categories.json").read_text(encoding="utf-8"))
    nodes = graph["nodes"]

    core_cited = set()
    for cat_id in categories.keys():
        if cat_id in META_DOMAINS:
            continue
        topic_file = CONTENT_DIR / f"{cat_id}.json"
        if not topic_file.exists():
            continue
        topic_data = json.loads(topic_file.read_text(encoding="utf-8"))
        for sub in topic_data.values():
            if not isinstance(sub, dict):
                continue
            for fid in sub.get("formula_ids", []):
                if isinstance(fid, str):
                    core_cited.add(fid)

    hijacked = [
        fid for fid in core_cited
        if fid in nodes and nodes[fid].get("domain") in META_DOMAINS
    ]
    assert not hijacked, f"Core-cited formulas hijacked by meta-domain: {hijacked[:10]}"


def test_philosophy_domain_ceiling(graph):
    """Prevent regression where philosophy-of-physics absorbs core-physics subtrees."""
    nodes = graph["nodes"]
    phil_nodes = sum(1 for n in nodes.values() if n.get("domain") == "philosophy-of-physics")
    assert phil_nodes <= 1150, f"Philosophy-of-physics node count inflated: {phil_nodes}"

    phil_to_core = sum(
        1
        for l in graph["links"]
        if l.get("type") == "derivation"
        and nodes[l["source"]].get("domain") == "philosophy-of-physics"
        and nodes[l["target"]].get("domain") != "philosophy-of-physics"
    )
    assert phil_to_core <= 165, f"Philosophy -> Core derivation edges regressed: {phil_to_core}"


def test_golden_landmark_canary_table(graph):
    """Flagship physics equations must retain their canonical domains and clean neighborhoods."""
    nodes = graph["nodes"]

    golden_domains = {
        "time-dependent-schrodinger-equation": "quantum-physics",
        "time-independent-schrodinger-equation": "quantum-physics",
        "heisenberg-uncertainty-principle": "quantum-physics",
        "probability-continuity-equation-4c9de9fa": "quantum-physics",
        "quantum-time-evolution-operator-e717a9a3": "quantum-physics",
        "schr-dinger-dynamics-c0e706de": "quantum-physics",
        "entanglement-test-9312ee27": "quantum-physics",
        "pure-state-density-operator-217cc52a": "quantum-physics",
        "the-path-integral-ab6eacde": "quantum-physics",
        "lorentz-factor-exact": "relativity",
        "einstein-field-equations": "relativity",
        "non-relativistic-limit": "relativity",
        "raychaudhuri-source-term-3b7e759f": "relativity",
        "amp-re-maxwell-identity-bf5142b0": "electromagnetism",
        "dirac-equation": "standard-model",
        "navier-stokes-momentum-fluids-27e5bf4d": "fluids-nonlinear",
        "gibbs-entropy-formula-fb0b23b8": "thermodynamics-statistical-mechanics",
        "euler-lagrange-equation": "classical-mechanics",
        "classical-kinetic-energy": "classical-mechanics",
        "stationary-action-principle-8836edf7": "classical-mechanics",
        "big-bang-start-4da62fa5": "astrophysics",
        "einstein-field-equations-simplified": "astrophysics",
        "the-cosmic-fake-6a24a3f4": "theoretical-physics",
        "time-evolution-of-expectation-value": "theoretical-physics",
    }

    for fid, expected_domain in golden_domains.items():
        assert fid in nodes, f"Golden landmark missing from graph: {fid}"
        actual = nodes[fid].get("domain")
        assert actual == expected_domain, (
            f"Golden landmark {fid} drifted: expected '{expected_domain}', got '{actual}'"
        )

    # TDSE must have >= 8 curated downstream derivations
    tdse_curated_children = [
        l["target"]
        for l in graph["links"]
        if l.get("type") == "derivation"
        and l["source"] == "time-dependent-schrodinger-equation"
        and l.get("confidence") == "curated"
    ]
    assert len(tdse_curated_children) >= 8, (
        f"Expected >= 8 curated TDSE derivations, found {len(tdse_curated_children)}"
    )

    # Heisenberg Uncertainty Principle must never re-acquire purged bogus children
    heis_children = {
        l["target"]
        for l in graph["links"]
        if l["source"] == "heisenberg-uncertainty-principle"
    }
    forbidden_heis_children = {
        "cosmic-background-temperature-decay-37a1f40f",
        "accidental-universe-8f17841b",
        "form-invariance-71b023b0",
        "no-preferred-center-fbd9d50c",
        "time-independent-function",
        "energy-to-mass-66805f31",
        "zero-blur-a2235888",
        "weak-gravity-condition-b6c456aa",
        "weak-gravity-conjecture-identity-1-c653591d-ada8fc0d",
    }
    leaked = heis_children & forbidden_heis_children
    assert not leaked, f"Purged bogus Heisenberg children reappeared: {leaked}"


def test_cas_verified_flag_populated(graph):
    """cas_verified must reflect SymPy homogeneity/validation across the catalog."""
    nodes = graph["nodes"]
    cas_verified_count = sum(1 for n in nodes.values() if n.get("cas_verified") is True)
    assert cas_verified_count >= 10000, f"cas_verified count collapsed: {cas_verified_count}"

    for fid in (
        "time-independent-schrodinger-equation",
        "heisenberg-uncertainty-principle",
        "lorentz-factor-exact",
        "dirac-equation",
        "gibbs-entropy-formula-fb0b23b8",
    ):
        assert nodes[fid].get("cas_verified") is True, f"Expected cas_verified=True on {fid}"


def test_select_best_domain_unit_behavior():
    """Unit-test Majority-Vote + Core-Domain Precedence tie-breaking."""
    cat_rank = {
        "classical-mechanics": 0,
        "quantum-physics": 1,
        "relativity": 2,
        "philosophy-of-physics": 3,
    }

    # Core domain always beats philosophy-of-physics even with fewer votes
    assert _select_best_domain(
        {"philosophy-of-physics": 10, "quantum-physics": 1}, cat_rank
    ) == "quantum-physics"

    # Majority vote wins among core domains
    assert _select_best_domain(
        {"classical-mechanics": 3, "relativity": 6}, cat_rank
    ) == "relativity"

    # Exact ties among core domains break deterministically by categories.json rank
    assert _select_best_domain(
        {"relativity": 3, "quantum-physics": 3}, cat_rank
    ) == "quantum-physics"

    # Philosophy-only citations still resolve to philosophy-of-physics
    assert _select_best_domain(
        {"philosophy-of-physics": 4}, cat_rank
    ) == "philosophy-of-physics"
