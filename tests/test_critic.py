import os
import pytest
import tempfile
import json
from scripts.maintenance.run_critic import MultiAgentCritic

def test_extract_claims():
    """Verify that key physical assertions are successfully isolated from draft HTML."""
    critic = MultiAgentCritic()
    html_content = (
        "<p>The Schwarzschild metric describes the spacetime geometry around a static, spherically symmetric mass.</p>"
        "<p>This metric is derived directly from the Einstein field equations with a vacuum energy of zero in 1916.</p>"
        "<p>We also like baking apple pies on sunny Sunday afternoons in Switzerland.</p>"
    )
    claims = critic.extract_claims(html_content)
    assertions = [c["assertion"] for c in claims]
    
    # Core physics sentences should be extracted
    assert any("schwarzschild metric" in a for a in assertions)
    assert any("einstein field equations" in a for a in assertions)
    # Trivial non-physics sentences should be skipped or not prioritized
    assert not any("apple pies" in a for a in assertions)

def test_judge_consensus():
    """Verify that consensus scores and citation listings match expectations under varying alignments."""
    critic = MultiAgentCritic()
    cms_content = "We calculate the exact gravitational field of a static mass point in general relativity."
    claims = [{"id": "c1", "assertion": "spherically symmetric gravitational field of a static mass"}]
    
    # Test 1: Supported case
    literature = [
        {
            "title": "On the gravitational field of a mass point",
            "authors": ["Schwarzschild, K."],
            "doi": "10.1002/andp.19163550704",
            "abstract": "We calculate the exact gravitational field of a static mass point in general relativity.",
            "url": "https://doi.org/10.1002/andp.19163550704"
        }
    ]
    score, citations = critic.judge_consensus(cms_content, claims, literature)
    assert score > 0.50
    assert len(citations) == 1
    
    # Test 2: Divergent case (neutral/contradictory)
    different_lit = [
        {
            "title": "Molecular theory of polymer solutions",
            "authors": ["Flory, P. J."],
            "doi": "10.1063/1.1723702",
            "abstract": "We describe thermodynamic properties of macromolecules dissolved in organic solvents.",
            "url": "https://doi.org/10.1063/1.1723702"
        }
    ]
    score_diff, citations_diff = critic.judge_consensus(cms_content, claims, different_lit)
    assert score_diff < 0.20
    assert len(citations_diff) == 0

def test_verify_slug_from_mock_workspace():
    """Test verification end-to-end using temporary directory workspace structures."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = os.path.join(tmpdir, "content")
        os.makedirs(content_dir)
        
        # Write mock shard
        shard_data = {
            "test-slug": {
                "title": "Test Subtopic",
                "content": "<p>This is a test topic about the energy-momentum relation. It relates mass, energy, and momentum in relativity.</p>",
                "standard": "platinum"
            }
        }
        shard_path = os.path.join(content_dir, "mechanics.json")
        with open(shard_path, "w") as f:
            json.dump(shard_data, f)
            
        # Write mock cache
        ref_lit = {
            "test-slug": [
                {
                    "title": "Relativistic Mechanics",
                    "authors": ["Einstein, A."],
                    "doi": "10.1002/andp.19053221004",
                    "abstract": "We discuss energy-momentum relations and rest mass.",
                    "url": "https://doi.org/10.1002/andp.19053221004"
                }
            ]
        }
        cache_path = os.path.join(tmpdir, "literature_cache.json")
        with open(cache_path, "w") as f:
            json.dump(ref_lit, f)
            
        # Instantiate critic in mock workspace
        critic = MultiAgentCritic(content_dir=content_dir, cache_path=cache_path)
        
        # Verify slug succeeds and updates shard with citations if flag is set
        assert critic.verify_slug("test-slug", write_citations=True) is True
        
        # Read shard back and assert citation structure is appended
        with open(shard_path, "r") as f:
            updated_shard = json.load(f)
            
        node = updated_shard["test-slug"]
        assert "verification" in node
        assert node["verification"]["consensus_score"] > 0.50
        assert len(node["verification"]["citations"]) == 1
        assert node["verification"]["citations"][0]["doi"] == "10.1002/andp.19053221004"

def test_commit_node_critic_import():
    """Verify commit_node has correctly resolved the critic imports."""
    from scripts.maintenance.commit_node import HAS_CRITIC
    assert HAS_CRITIC is True
