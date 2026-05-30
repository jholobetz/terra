"""Unit tests for IntegrityShield against a fixture content_dir.

The shield exposes a parametrized constructor (content_dir, schema_path,
target_slug), and the targeted path bypasses PhysicsOrchestrator entirely
via a MockOrchestrator. That makes it directly testable in-process: each
test populates a tempdir with just the files the targeted path reads,
constructs the shield, runs it, and inspects .errors / .warnings.
"""
import json

from integrity_shield import IntegrityShield


def populate(content_dir, *, search_index=None, entities=None, categories=None,
             shards=None, formulas=None):
    """Write the index files plus any subtopic shards into content_dir."""
    (content_dir / "search_index.json").write_text(json.dumps(search_index or {}))
    (content_dir / "entities.json").write_text(json.dumps(entities or {}))
    (content_dir / "categories.json").write_text(json.dumps(categories or {}))
    for filename, payload in (shards or {}).items():
        (content_dir / filename).write_text(json.dumps(payload))
    if formulas is not None:
        (content_dir / "formulas.json").write_text(json.dumps(formulas))


# Reusable platinum prose: ~590 words, contains every tech-density term the
# shield scores against. Density score = 55 (well above the 30 cutoff), word
# count >500 — so it never trips Low Depth or Non-Technical warnings on its
# own. Tests append violations to isolate one check at a time.
_BLOCK = (
    "Conservation of symmetry under translation invariance generates a conserved "
    "current via the variational principle. The hamiltonian generator encodes the "
    "dynamics through unitary evolution of the operator algebra on Hilbert space, "
    "with the lagrangian formulation providing an equivalent action functional. "
    "The tensor structure of the field equations reveals the underlying eigenvalue "
    "spectrum and the manifold geometry of the configuration space. "
)
PLATINUM_PROSE = "<p>" + (_BLOCK * 10) + "</p>"


def platinum_node(content=None, content_extra="", standard="platinum", formula_ids=None):
    return {
        "title": "Test Node",
        "content": content if content is not None else (PLATINUM_PROSE + content_extra),
        "standard": standard,
        "formula_ids": formula_ids or [],
        "parents": [],
    }


# -----------------------------------------------------------------------------
# Happy path
# -----------------------------------------------------------------------------

def test_clean_shard_produces_no_errors(shield_workspace):
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node()}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert shield.errors == [], shield.errors


# -----------------------------------------------------------------------------
# Broken links
# -----------------------------------------------------------------------------

def test_broken_subtopic_link_detected(shield_workspace):
    bad = '<p><a href="/physics/subtopic/does-not-exist">missing</a></p>'
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content_extra=bad)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("Broken Link" in e and "does-not-exist" in e for e in shield.errors), shield.errors


def test_valid_subtopic_link_does_not_trigger(shield_workspace):
    good = '<p><a href="/physics/subtopic/neighbor">linked</a></p>'
    populate(
        shield_workspace,
        search_index={
            "src-node": "test_shard.json",
            "neighbor": "test_shard.json",
        },
        shards={"test_shard.json": {
            "src-node": platinum_node(content_extra=good),
            "neighbor": platinum_node(),
        }},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert not any("Broken Link" in e for e in shield.errors), shield.errors


# -----------------------------------------------------------------------------
# Formula registry
# -----------------------------------------------------------------------------

def test_broken_formula_reference_detected(shield_workspace):
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(formula_ids=["unknown-fid"])}},
        formulas={},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("Broken Formula" in e and "unknown-fid" in e for e in shield.errors), shield.errors


def test_mathjax_compilation_error_in_formula_detected(shield_workspace):
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(formula_ids=["f1"])}},
        formulas={"f1": {"equation": "<span class='mjx-error'>compile failed</span>"}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("MathJax Rendering Error" in e for e in shield.errors), shield.errors


# -----------------------------------------------------------------------------
# Duplicate slugs across shards
# -----------------------------------------------------------------------------

def test_critical_duplicate_across_shards_detected(shield_workspace):
    populate(
        shield_workspace,
        search_index={"src-node": "shard_a.json"},
        shards={
            "shard_a.json": {"src-node": platinum_node()},
            "shard_b.json": {"src-node": platinum_node()},
        },
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("CRITICAL DUPLICATE" in e for e in shield.errors), shield.errors


# -----------------------------------------------------------------------------
# Technical-density warnings
# -----------------------------------------------------------------------------

def test_low_word_count_emits_low_depth_warning(shield_workspace):
    short = "<p>Tiny content. Less than five hundred words.</p>"
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content=short)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("Low Depth" in w for w in shield.warnings), shield.warnings


def test_non_technical_density_emits_warning(shield_workspace):
    # Plenty of words, zero tech terms, zero LaTeX — score = 0, well below cutoff.
    boring = "<p>" + ("the quick brown fox jumps over the lazy dog " * 100) + "</p>"
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content=boring)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("Non-Technical" in w for w in shield.warnings), shield.warnings


# -----------------------------------------------------------------------------
# Platinum-only format gates
# -----------------------------------------------------------------------------

def test_platinum_with_raw_latex_delimiters_blocked(shield_workspace):
    raw_latex = r'<p>\( E = mc^2 \)</p>'
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content_extra=raw_latex)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("SSR VIOLATION" in e for e in shield.errors), shield.errors


def test_legacy_with_raw_latex_does_not_trigger_ssr(shield_workspace):
    # SSR check only runs for standard="platinum"; legacy is exempt.
    raw_latex = r'<p>\( E = mc^2 \)</p>'
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(
            content_extra=raw_latex, standard="legacy")}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert not any("SSR VIOLATION" in e for e in shield.errors), shield.errors


def test_platinum_with_math_display_missing_svg_blocked(shield_workspace):
    raw_display = '<div class="math-display">E = mc^2</div>'
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content_extra=raw_display)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("MATH RENDERING VIOLATION" in e for e in shield.errors), shield.errors


def test_platinum_with_rendered_math_display_passes(shield_workspace):
    rendered = '<div class="math-display"><svg>...</svg></div>'
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        shards={"test_shard.json": {"src-node": platinum_node(content_extra=rendered)}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert not any("MATH RENDERING VIOLATION" in e for e in shield.errors), shield.errors


# -----------------------------------------------------------------------------
# Entity auto-link warning
# -----------------------------------------------------------------------------

def test_unlinked_entity_emits_warning(shield_workspace):
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        entities={"einstein": {"name": "Einstein"}},
        shards={"test_shard.json": {"src-node": platinum_node(
            content_extra="<p>According to Einstein, the field equations couple geometry and matter.</p>"
        )}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert any("Unlinked Entity" in w and "Einstein" in w for w in shield.warnings), shield.warnings


def test_anchor_wrapped_entity_does_not_emit_warning(shield_workspace):
    # The regex excludes occurrences preceded by `>` or followed by `<`,
    # so a properly anchor-wrapped name is exempt.
    populate(
        shield_workspace,
        search_index={"src-node": "test_shard.json"},
        entities={"einstein": {"name": "Einstein"}},
        shards={"test_shard.json": {"src-node": platinum_node(
            content_extra='<p>According to <a href="/physics/entity/einstein">Einstein</a> the geometry couples.</p>'
        )}},
    )
    shield = IntegrityShield(target_slug="src-node")
    shield.run()
    assert not any("Unlinked Entity" in w for w in shield.warnings), shield.warnings
