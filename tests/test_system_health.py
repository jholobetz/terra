"""Unit tests for score_subtopic in generate_system_health.py.

The dashboard relabeling exposes two distinct "platinum" definitions:
  - flagged_platinum_count: matches the CTA disk scan (standard == "platinum")
  - organic_platinum_count: subset that also passes lead + artifact gates
This file pins down the per-subtopic classifier that drives both counters.
"""
from scripts.maintenance.generate_system_health import score_subtopic, TECH_TERMS


def node(content="<p>generic prose</p>", title="Generic Topic", standard="legacy"):
    return {"content": content, "title": title, "standard": standard}


# -----------------------------------------------------------------------------
# is_flagged: pure mapping from standard field to boolean
# -----------------------------------------------------------------------------

def test_legacy_subtopic_is_not_flagged():
    s = score_subtopic("test-node", node(standard="legacy"))
    assert s["is_flagged"] is False
    assert s["is_organic_platinum"] is False
    assert s["has_flag_violation"] is False


def test_missing_standard_field_treated_as_legacy():
    s = score_subtopic("test-node", {"content": "<p>x</p>", "title": "X"})
    assert s["is_flagged"] is False


def test_platinum_standard_is_flagged():
    s = score_subtopic("test-node", node(standard="platinum"))
    assert s["is_flagged"] is True


# -----------------------------------------------------------------------------
# is_organic_platinum: flagged AND no qualitative violations
# -----------------------------------------------------------------------------

def test_clean_platinum_is_organic():
    # Title and slug are both absent from the opening 150 chars; no <ul>/<li>.
    s = score_subtopic("orbital-mechanics", node(
        title="Orbital Mechanics",
        standard="platinum",
        content="<p>Conservation of energy in central-force problems governs the dynamics.</p>",
    ))
    assert s["is_flagged"] is True
    assert s["is_organic_platinum"] is True
    assert s["has_flag_violation"] is False


def test_title_in_opening_triggers_lead_violation():
    s = score_subtopic("orbital-mechanics", node(
        title="Orbital Mechanics",
        standard="platinum",
        content="<p>Orbital mechanics is the study of motion in central-force fields.</p>",
    ))
    assert s["has_lead_violation"] is True
    assert s["is_organic_platinum"] is False
    assert s["has_flag_violation"] is True


def test_slug_words_in_opening_trigger_lead_violation():
    # Slug "orbital-mechanics" becomes "orbital mechanics" — appears in opening.
    s = score_subtopic("orbital-mechanics", node(
        title="Wholly Different Title",
        standard="platinum",
        content="<p>Orbital mechanics describes central-force motion in detail.</p>",
    ))
    assert s["has_lead_violation"] is True


def test_unordered_list_triggers_artifact_violation():
    s = score_subtopic("test-node", node(
        title="X",
        standard="platinum",
        content="<p>Intro paragraph.</p><ul><li>bad</li></ul>",
    ))
    assert s["has_artifact_violation"] is True
    assert s["is_organic_platinum"] is False
    assert s["has_flag_violation"] is True


def test_list_item_alone_triggers_artifact_violation():
    # The check is OR of <ul> or <li>; standalone <li> also forbidden.
    s = score_subtopic("test-node", node(
        title="X",
        standard="platinum",
        content="<p>Intro.</p><li>bad</li>",
    ))
    assert s["has_artifact_violation"] is True


# -----------------------------------------------------------------------------
# is_pseudo_platinum: meets quant but not flagged
# -----------------------------------------------------------------------------

def test_high_quality_legacy_is_pseudo_platinum():
    # 650+ words AND density >= 60. Density gets 15 per LaTeX block plus 5 per
    # tech term. Pack enough tech terms and a few LaTeX blocks.
    tech_run = " ".join(TECH_TERMS * 5)  # 55 tech-term occurrences
    body = " ".join(["physical concepts and"] * 200) + " " + tech_run
    content = f"<p>{body} \\( E = mc^2 \\) and \\[ F = ma \\]</p>"
    s = score_subtopic("test-node", node(content=content, standard="legacy"))
    assert s["meets_quant"] is True
    assert s["is_flagged"] is False
    assert s["is_pseudo_platinum"] is True


def test_low_density_legacy_is_not_pseudo_platinum():
    # 650+ words but zero tech terms and no LaTeX — density = 0.
    body = " ".join(["the quick brown fox jumps"] * 200)
    s = score_subtopic("test-node", node(content=f"<p>{body}</p>", standard="legacy"))
    assert s["meets_quant"] is False
    assert s["is_pseudo_platinum"] is False


# -----------------------------------------------------------------------------
# Word + density mechanics
# -----------------------------------------------------------------------------

def test_word_count_excludes_html_tags():
    s = score_subtopic("test-node", node(content="<p>one two three</p>"))
    # Only the three English words count; <p>/</p> are stripped.
    assert s["words"] == 3


def test_density_credits_tech_terms():
    # No LaTeX, two tech terms ("symmetry", "tensor") → score = 2 * 5 = 10.
    s = score_subtopic("test-node", node(content="<p>symmetry and tensor stuff</p>"))
    assert s["density_score"] == 10


def test_density_credits_latex_blocks():
    # \\( and \\[ each count for 15. Two blocks → 30. No tech terms.
    s = score_subtopic("test-node", node(content=r"<p>see \( a \) and \[ b \]</p>"))
    assert s["density_score"] == 30


def test_subjective_subtopic_lowers_density_target():
    # Node in philosophy-of-physics category/parent gets density target 30
    sub = node(content="<p>some content</p>", standard="platinum")
    sub["parents"] = ["philosophy-of-physics"]
    s = score_subtopic("philosophical-concept", sub, category="philosophy-of-physics")
    assert s["is_subjective"] is True
    assert s["density_target"] == 30
    assert s["word_target"] == 500


def test_lexical_subjectivity_detection():
    # No math, high density of subjective terms vs objective terms
    content = "<p>This thought experiment explores the realism of quantum interpretations and ontological commitments.</p>"
    s = score_subtopic("conceptual-subtopic", node(content=content))
    assert s["is_subjective"] is True
    assert s["density_target"] == 30


def test_objective_subtopic_retains_density_target_60():
    # Standard physics node gets target 60
    s = score_subtopic("tensor-math", node(content="<p>symmetry and tensor operator</p>"), category="relativity")
    assert s["is_subjective"] is False
    assert s["density_target"] == 60
