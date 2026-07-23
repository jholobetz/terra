"""Tests for the quality breakdown surfaced inside `gqs.py status`.

print_quality_breakdown reads system_health.json and renders the
platinum classification + qualitative violations alongside the CTA
dashboard. Tests pin both the success-path rendering and the silent
no-op behavior when system_health.json is missing/malformed.
"""
import json

from gqs import print_quality_breakdown


def test_missing_health_file_prints_nothing(tmp_path, capsys):
    missing = tmp_path / "nope.json"
    print_quality_breakdown(str(missing))
    assert capsys.readouterr().out == ""


def test_malformed_json_prints_nothing(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json")
    print_quality_breakdown(str(bad))
    assert capsys.readouterr().out == ""


def test_missing_platinum_scorecard_prints_nothing(tmp_path, capsys):
    # File exists but is missing the platinum_scorecard key — silent no-op.
    health = tmp_path / "health.json"
    health.write_text(json.dumps({"global_stats": {}, "integrity_summary": {}}))
    print_quality_breakdown(str(health))
    assert capsys.readouterr().out == ""


def test_well_formed_health_renders_breakdown(tmp_path, capsys):
    health = tmp_path / "health.json"
    health.write_text(json.dumps({
        "last_updated": "2026-05-29 20:21:57",
        "platinum_scorecard": {
            "flagged_platinum_count": 783,
            "flagged_platinum_percentage": 49.43,
            "organic_platinum_count": 741,
            "organic_platinum_percentage": 46.78,
            "flag_violations": 42,
            "pseudo_platinum_count": 0,
            "lead_violations": 525,
            "artifact_violations": 97,
            "low_depth_count": 896,
            "non_technical_count": 909,
        },
        "integrity_summary": {
            "broken_links": 0,
            "broken_formulas": 0,
            "orphans_count": 314,
        },
    }))
    print_quality_breakdown(str(health))
    out = capsys.readouterr().out

    # Section header surfaces the file's timestamp so freshness is visible.
    assert "QUALITY BREAKDOWN" in out
    assert "2026-05-29 20:21:57" in out

    # Both platinum counts must be present with their CTA-aligned semantics.
    assert "Flagged" in out and "783" in out
    assert "Organic" in out and "741" in out
    assert "Flag violations" in out and "42" in out

    # Qualitative section surfaces the four violation counters.
    assert "Lead-rule" in out and "525" in out
    assert "Artifact" in out and "97" in out
    assert "Low depth" in out and "896" in out
    assert "Non-technical" in out and "909" in out

    # Integrity section surfaces broken links / formulas / orphans.
    assert "Broken links" in out
    assert "Orphans" in out and "314" in out
