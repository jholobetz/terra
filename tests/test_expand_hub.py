"""
Unit tests for scripts/expand_hub.py (1-Step Hub Expansion Engine).
"""
import copy
import pytest

from scripts.expand_hub import (
    is_single_variable_token,
    resolve_ledger_path,
    update_expansion_ledger,
    validate_manifest,
)


def _make_long_prose(extra_math: str = "") -> str:
    """Builds a valid 5-paragraph OPS 1.0 prose block (~700 words, >=5 outgoing links, >=1 cross-hub)."""
    base_para = (
        "Continuum transport in viscous media couples momentum diffusion, pressure gradients, and "
        "boundary shear across laboratory and geophysical length scales. "
    )
    filler = " ".join([base_para] * 7)
    p1 = (
        f"<p>Buoyant stratification across an incompressible layer couples "
        f"\\( \\nabla \\cdot \\mathbf{{u}} = 0 \\) with thermal forcing in the "
        f"<a href=\"/physics/subtopic/navier-stokes-equations\" class=\"subtopic-link\"><strong>Navier-Stokes Equations</strong></a> "
        f"and <a href=\"/physics/subtopic/euler-fluid-equations\" class=\"subtopic-link\"><strong>Euler Fluid Equations</strong></a> "
        f"while maintaining dynamic stability \\( \\mathrm{{Ra}}_c \\). {filler}</p>"
    )
    p2 = (
        f"<p>Linear perturbation analysis in "
        f"<a href=\"/physics/subtopic/hydrodynamic-stability\" class=\"subtopic-link\"><strong>Hydrodynamic Stability</strong></a> "
        f"yields the canonical law \\( \\mathrm{{TestNum}} = \\frac{{\\alpha \\beta}}{{\\gamma}} \\) "
        f"alongside \\( \\delta \\rho \\) and \\( \\Delta T \\). {extra_math} {filler}</p>"
    )
    p3 = (
        f"<p>Transitioning through a supercritical pitchfork in "
        f"<a href=\"/physics/subtopic/bifurcation-theory\" class=\"subtopic-link\"><strong>Bifurcation Theory</strong></a> "
        f"modulates <a href=\"/physics/subtopic/thermal-transport\" class=\"subtopic-link\"><strong>Thermal Transport</strong></a> "
        f"via \\( h_b(t) \\) and \\( U_{{\\min}} \\). {filler}</p>"
    )
    p4 = (
        f"<p>At high inertia, eddies enter a "
        f"<a href=\"/physics/subtopic/kolmogorov-cascade\" class=\"subtopic-link\"><strong>Kolmogorov Cascade</strong></a> "
        f"characterized by \\( \\Delta U_g \\) and \\( \\omega(k) \\). {filler}</p>"
    )
    p5 = (
        f"<p>In the asymptotic dissipation limit, macroscopic "
        f"<a href=\"/physics/subtopic/entropy\" class=\"subtopic-link\"><strong>Entropy</strong></a> "
        f"production vanishes as \\( \\rho_1 \\) approaches \\( \\rho_2 \\). {filler}</p>"
    )
    return p1 + p2 + p3 + p4 + p5


def _make_valid_manifest() -> dict:
    return {
        "domain": "fluids-nonlinear",
        "append_to_pillar": "5. Instabilities, Vorticity & Fluid Waves",
        "subtopics": {
            "synthetic-test-instability-slug": {
                "title": "Synthetic Test Instability",
                "hero_equation": r"\mathrm{TestNum} = \frac{\alpha \beta}{\gamma}",
                "formula_ids": ["synthetic-test-number-ratio"],
                "content": _make_long_prose(),
                "citations": [
                    {
                        "doi": "10.1000/test1",
                        "title": "Foundational Test Fluid Stability Paper",
                        "authors": ["A. Researcher"],
                        "url": "https://doi.org/10.1000/test1",
                    },
                    {
                        "doi": "10.1000/test2",
                        "title": "Nonlinear Test Dynamics Monograph",
                        "authors": ["B. Physicist"],
                        "url": "https://doi.org/10.1000/test2",
                    },
                ],
                "keywords": ["instability", "fluid", "buoyancy"],
                "incoming_links": [
                    {
                        "from_slug": "hydrodynamic-stability",
                        "sentence": ' See also <a href="/physics/subtopic/synthetic-test-instability-slug" class="subtopic-link"><strong>Synthetic Test Instability</strong></a>.',
                    },
                    {
                        "from_slug": "navier-stokes-equations",
                        "sentence": ' Related analysis appears in <a href="/physics/subtopic/synthetic-test-instability-slug" class="subtopic-link"><strong>Synthetic Test Instability</strong></a>.',
                    },
                ],
            }
        },
        "formulas": [
            {
                "id": "synthetic-test-number-ratio",
                "title": "Synthetic Test Dimensionless Ratio",
                "equation": r"\mathrm{TestNum} = \frac{\alpha \beta}{\gamma}",
                "category": "fluids-nonlinear",
                "record_type": "equation",
                "parent_formula_id": "reynolds-number",
                "derivation_type": "DEFINITION",
                "description": "Dimensionless test ratio comparing thermal forcing parameters against damping rate.",
                "conceptual_definition": "Defines the dimensionless ratio $\\mathrm{TestNum} = \\alpha \\beta / \\gamma$ governing linear stability in synthetic test media.",
                "intuitive_summary": "Measures whether destabilizing forcing parameters overwhelm stabilizing diffusive damping.",
                "interpretation": "When $\\mathrm{TestNum}$ exceeds unity, perturbations amplify exponentially until nonlinear saturation occurs.",
                "symmetry_origin": "Emerges from Buckingham Pi dimensional analysis and scaling invariance of the linearized transport equations.",
                "limits_and_boundary": "As $\\alpha \\to 0$, the ratio vanishes and the fluid layer remains strictly quiescent.",
                "semantic_variables": {
                    "\\mathrm{TestNum}": "Dimensionless test ratio",
                    "\\alpha": "Thermal forcing coefficient",
                    "\\beta": "Coupling parameter",
                    "\\gamma": "Damping rate",
                },
                "cas_validation": {
                    "status": "HOMOGENEOUS",
                    "is_homogeneous": True,
                    "quantity": "Dimensionless Ratio",
                    "dimension_latex": "1",
                    "verified_at": 1700000000,
                },
            }
        ],
    }


def test_single_variable_token_classification():
    # Non-clickable variable / function / delta / isotope tokens
    for tok in ["L", r"\nu", r"\mathrm{Ra}_c", r"U_{\min}", r"k^{-1}", r"\Delta U_g", r"\delta \rho", r"h_b(t)", r"\eta(x, t)", r"{}^{56}\text{Ni}"]:
        assert is_single_variable_token(tok), f"Expected non-clickable token: {tok}"

    # Clickable equations, operators, and composite terms
    for expr in [r"\gamma = \sqrt{A g k}", r"(\mathbf{u} \cdot \nabla)\mathbf{u}", r"\int u \, dx", r"\sin(\pi z / L)", r"\nu \nabla^2 \mathbf{u}"]:
        assert not is_single_variable_token(expr), f"Expected clickable expression: {expr}"


def test_valid_manifest_passes_dry_run():
    manifest = _make_valid_manifest()
    errors, warnings, stats = validate_manifest(manifest)
    assert errors == [], f"Expected zero errors, got: {errors}"
    assert stats["subtopic_count"] == 1
    assert stats["formula_count"] == 1


def test_undefined_clickable_expression_is_blocked():
    manifest = _make_valid_manifest()
    manifest["subtopics"]["synthetic-test-instability-slug"]["content"] = _make_long_prose(
        extra_math=r"We also consider the unmapped operator \( \zeta_1 \zeta_2 + \zeta_3^4 \)."
    )
    errors, _, _ = validate_manifest(manifest)
    assert any("UNDEFINED CLICKABLE" in e for e in errors), f"Expected UNDEFINED CLICKABLE error, got: {errors}"


def test_short_alnum_svg_blocked_unless_whitelisted():
    manifest = _make_valid_manifest()
    manifest["subtopics"]["synthetic-test-instability-slug"]["content"] = _make_long_prose(
        extra_math=r"With bare letter \( L \) and bare number \( 10^8 \)."
    )
    errors, _, _ = validate_manifest(manifest)
    assert any("Bare short/numeric MathJax SVGs disallowed" in e for e in errors)

    # Whitelist exception works
    manifest2 = _make_valid_manifest()
    manifest2["allow_short_tokens"] = ["c"]
    manifest2["subtopics"]["synthetic-test-instability-slug"]["content"] = _make_long_prose(
        extra_math=r"Relativistic speed \( c \) is explicitly whitelisted."
    )
    errors2, _, _ = validate_manifest(manifest2)
    assert errors2 == [], f"Expected whitelisted token to pass, got: {errors2}"


def test_batch_size_over_20_rejected_by_default():
    manifest = _make_valid_manifest()
    base = copy.deepcopy(manifest["subtopics"]["synthetic-test-instability-slug"])
    for i in range(21):
        manifest["subtopics"][f"synthetic-test-slug-{i}"] = copy.deepcopy(base)
    errors, _, _ = validate_manifest(manifest, force_large_batch=False)
    assert any("exceeds recommended cap (20)" in e for e in errors)


def test_ledger_resolution_and_idempotent_append(tmp_path):
    # Priority: --no-ledger > --ledger > manifest['ledger_path'] > None
    assert resolve_ledger_path({}) is None
    assert resolve_ledger_path({"ledger_path": "docs/custom.md"}, no_ledger=True) is None
    assert resolve_ledger_path({"ledger_path": "docs/a.md"}, cli_ledger="docs/b.md").endswith("docs/b.md")

    ledger_file = tmp_path / "phase_6_ledger.md"
    m1 = _make_valid_manifest()
    added1 = update_expansion_ledger(str(ledger_file), m1, "2026-11-21", domain_after_count=26)
    assert added1 == 1
    text1 = ledger_file.read_text(encoding="utf-8")
    assert "## Batch 1 — `fluids-nonlinear`" in text1
    assert "| 1 | Synthetic Test Instability | http://localhost:8000/physics/subtopic/synthetic-test-instability-slug | https://physicslab.ca/physics/subtopic/synthetic-test-instability-slug |" in text1

    # Re-running with same slug is strictly idempotent (0 duplicate rows)
    added_dup = update_expansion_ledger(str(ledger_file), m1, "2026-11-21", domain_after_count=26)
    assert added_dup == 0
    assert ledger_file.read_text(encoding="utf-8") == text1

    # Second batch continues at Batch 2, row 2
    m2 = _make_valid_manifest()
    m2["subtopics"] = {"second-synthetic-slug": {"title": "Second Synthetic Topic"}}
    added2 = update_expansion_ledger(str(ledger_file), m2, "2026-11-22", domain_after_count=27)
    assert added2 == 1
    text2 = ledger_file.read_text(encoding="utf-8")
    assert "## Batch 2 — `fluids-nonlinear`" in text2
    assert "| 2 | Second Synthetic Topic |" in text2

