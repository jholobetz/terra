import os
import pytest
import tempfile
import json
from scripts.maintenance.semantic_prose_verifier import (
    preprocess_html,
    tokenize_and_lemmatize,
    get_similarity_score,
    check_keywords,
    audit_semantic_prose
)

def test_preprocess_html():
    """Verify HTML tags, MathJax symbols, and SVGs are correctly stripped from text."""
    raw_html = (
        "<p>The Schrödinger equation is a fundamental law, "
        "\\( i\\hbar\\frac{\\partial}{\\partial t}|\\Psi\\rangle = \\hat{H}|\\Psi\\rangle \\). "
        "<div class=\"math-display\">\\[ \\hat{H}\\psi = E\\psi \\]</div>"
        "<svg>some vector graphics path</svg>"
        "It describes quantum systems.</p>"
    )
    processed = preprocess_html(raw_html)
    assert "schrödinger" in processed
    assert "fundamental law" in processed
    assert "quantum systems" in processed
    # Math symbols/markup should be stripped
    assert "i\\hbar" not in processed
    assert "\\hat{H}" not in processed
    assert "svg" not in processed
    assert "vector graphics" not in processed

def test_tokenize_and_lemmatize():
    """Verify that tokenization filters stopwords and lemmatizes correctly."""
    text = "The electrons are orbiting the nucleus of the atom."
    tokens = tokenize_and_lemmatize(text)
    # Stopwords like 'the', 'are', 'of' should be removed
    assert "the" not in tokens
    assert "are" not in tokens
    assert "of" not in tokens
    # Lemmatization should reduce 'electrons' to 'electron'
    assert "electron" in tokens
    assert "orbiting" in tokens or "orbit" in tokens
    assert "nucleus" in tokens
    assert "atom" in tokens

def test_get_similarity_score():
    """Verify similarity scores for identical, similar, and divergent texts."""
    ref = "Quantum superposition is the ability of a system to be in multiple states at once."
    same = "Quantum superposition is the ability of a system to be in multiple states at once."
    similar = "A quantum system can exist in a superposition of multiple states simultaneously."
    different = "Classical thermodynamics describes macrostates using temperature and pressure variables."
    
    score_identical = get_similarity_score(ref, same)
    score_similar = get_similarity_score(ref, similar)
    score_different = get_similarity_score(ref, different)
    
    assert score_identical == pytest.approx(1.0, abs=1e-5)
    assert score_similar > 0.2
    assert score_different < 0.1
    assert score_similar > score_different

def test_check_keywords():
    """Verify keyword presence checker, including lemmatized matching and multi-word keywords."""
    text = "The speed of light in vacuum is a physical constant c. Electrons carry negative charge."
    keywords = ["speed of light", "electron", "proton"]
    
    missing, found = check_keywords(text, keywords)
    assert "speed of light" in found
    assert "electron" in found  # 'electrons' in text lemmatizes to 'electron'
    assert "proton" in missing

def test_audit_semantic_prose_flow():
    """Verify the end-to-end semantic prose audit using temporary files for mock validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        content_dir = os.path.join(tmpdir, "content")
        os.makedirs(content_dir)
        
        # 1. Create a mock content shard containing two subtopics
        shard_data = {
            "test-relation": {
                "title": "Test Relation",
                "content": "<p>This is a test topic about the energy-momentum relation. It includes mass, energy, and momentum in special relativity.</p>",
                "standard": "platinum"
            },
            "test-drift": {
                "title": "Drifting Topic",
                "content": "<p>This text has drifted completely away from the topic and only describes cooking apple pies.</p>",
                "standard": "platinum"
            }
        }
        
        # Write shard map first since verifier depends on it or scans
        shard_path = os.path.join(content_dir, "mechanics.json")
        with open(shard_path, "w") as f:
            json.dump(shard_data, f)
            
        # 2. Create mock references
        ref_data = {
            "test-relation": {
                "title": "Test Relation",
                "reference_prose": "The energy-momentum relation links energy, momentum, and invariant rest mass.",
                "keywords": ["energy", "momentum", "mass", "relativity"]
            },
            "test-drift": {
                "title": "Drifting Topic",
                "reference_prose": "The Schwarzschild metric defines the spacetime metric around a spherical mass.",
                "keywords": ["Schwarzschild", "metric", "spacetime", "mass"]
            }
        }
        ref_path = os.path.join(tmpdir, "semantic_references.json")
        with open(ref_path, "w") as f:
            json.dump(ref_data, f)
            
        # Test 1: Single-slug audit on a passing topic
        assert audit_semantic_prose(content_dir=content_dir, ref_path=ref_path, target_slug="test-relation") is True
        
        # Test 2: Single-slug audit on an unregistered topic (should skip and return True)
        assert audit_semantic_prose(content_dir=content_dir, ref_path=ref_path, target_slug="unregistered-slug") is True
        
        # Test 3: Single-slug audit on a failing topic
        assert audit_semantic_prose(content_dir=content_dir, ref_path=ref_path, target_slug="test-drift") is False
        
        # Test 4: Full audit containing a failing topic (should fail overall)
        assert audit_semantic_prose(content_dir=content_dir, ref_path=ref_path) is False
