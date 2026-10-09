"""
Unit tests for the Unified Platform Assessment Telemetry & Reporting Engine.
Tests Schema v1.0 structure, strict invariant checks, delta calculations, and frontmatter generation.
"""

import pytest
from scripts.maintenance.run_project_assessment import (
    build_standard_telemetry,
    verify_strict_invariants,
    format_delta,
    generate_markdown_report,
)


@pytest.fixture
def mock_audit_data():
    """Provides canonical, passing raw audit data."""
    return {
        "tests": {
            "status": "PASSING",
            "exit_code": 0,
            "total": 3100,
            "passed": 3100,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "duration": 4.5,
        },
        "diagnostics": {
            "lineage": {
                "total_formulas": 14671,
                "dag_edges": 44691,
                "lhi_score": 95.2,
                "rich_count": 13800,
                "moderate_count": 871,
                "isolated_nodes": 0,
            },
            "gqs": {
                "total_subtopics": 1584,
                "graduated_platinum": 1584,
                "broken_links": 0,
                "lead_violations": 0,
                "artifact_violations": 0,
                "low_depth_count": 0,
                "orphan_subtopics": 0,
            },
            "cas_benchmark": {
                "latency_ms": 250.0,
                "status": "HEALTHY",
            },
            "shards": {
                "shard_count": 256,
                "status": "HEALTHY",
            },
        },
        "docs": {
            "file_count": 9,
            "total_words": 13182,
            "files": [],
        },
        "roadmap": {
            "phase_1": {"title": "Phase 1", "status": "COMPLETED", "progress_pct": 100, "items": []},
            "phase_2": {
                "title": "Phase 2",
                "status": "OPERATIONAL",
                "progress_pct": 100,
                "items": [
                    ("Dual-Layer Hash Sync", "256/256 Shards Synchronized", True),
                    ("Multi-Step Derivations", "102 / 100 Verified Derivation Proofs", True),
                ],
            },
            "phase_3": {"title": "Phase 3", "status": "IN_PROGRESS", "progress_pct": 15, "items": []},
            "ops_2": {
                "title": "OPS 2.0",
                "status": "IN_PROGRESS",
                "progress_pct": 10,
                "items": [
                    ("AI-ism Cliche Scanner", "4 Cliches sitewide", True),
                ],
            },
            "phase_4": {"title": "Phase 4", "status": "STRATEGIC_HORIZON", "progress_pct": 0, "items": []},
        },
    }


def test_telemetry_schema_v1_structure(mock_audit_data):
    """Verifies that build_standard_telemetry adheres to Schema v1.0."""
    strict_passed, violations = verify_strict_invariants(mock_audit_data)
    assert strict_passed is True

    telemetry = build_standard_telemetry(mock_audit_data, mode="quick", strict_passed=strict_passed, violations=violations)

    assert telemetry["meta"]["schema_version"] == "1.0"
    assert "timestamp" in telemetry["meta"]
    assert telemetry["meta"]["mode"] == "quick"

    # Canonical sections
    assert "summary" in telemetry
    assert telemetry["summary"]["platform_grade"] == "A+"
    assert telemetry["summary"]["strict_invariants"] == "PASSED"

    assert "mathematical_manifold" in telemetry
    manifold = telemetry["mathematical_manifold"]
    assert manifold["total_formulas"] == 14671
    assert manifold["dag_edges"] == 44691
    assert manifold["lhi_score"] == 95.2
    assert manifold["isolated_nodes"] == 0
    assert manifold["multi_step_proofs"] == 102
    assert manifold["cas_latency_ms"] == 250.0

    assert "knowledge_web" in telemetry
    web = telemetry["knowledge_web"]
    assert web["total_subtopics"] == 1584
    assert web["broken_links"] == 0
    assert web["lead_violations"] == 0

    assert "roadmap_progress" in telemetry
    assert telemetry["roadmap_progress"]["phase_1_stabilization_pct"] == 100

    assert "infrastructure" in telemetry
    assert telemetry["infrastructure"]["doc_words"] == 13182

    assert "regression_tests" in telemetry
    assert telemetry["regression_tests"]["passed"] == 3100
    assert telemetry["regression_tests"]["failed"] == 0


def test_verify_strict_invariants_passing(mock_audit_data):
    """Verifies that a clean system passes all strict invariant checks."""
    passes, violations = verify_strict_invariants(mock_audit_data)
    assert passes is True
    assert len(violations) == 0


def test_verify_strict_invariants_failing(mock_audit_data):
    """Verifies that invariant violations are properly flagged and cause failure."""
    # Inject violations
    mock_audit_data["diagnostics"]["lineage"]["isolated_nodes"] = 3
    mock_audit_data["diagnostics"]["gqs"]["broken_links"] = 1
    mock_audit_data["roadmap"]["phase_2"]["items"][0] = ("Dual-Layer Hash Sync", "2 Shards Drifted", False)

    passes, violations = verify_strict_invariants(mock_audit_data)
    assert passes is False
    assert len(violations) >= 3
    violation_text = " ".join(violations)
    assert "isolated formula" in violation_text
    assert "broken subtopic cross-link" in violation_text
    assert "Shard drift" in violation_text


def test_format_delta_helper():
    """Verifies delta comparison formatting with directions and ANSI colors."""
    # Positive improvement (standard: higher is better)
    res_pos = format_delta(100, 90, higher_is_better=True)
    assert "+10" in res_pos
    assert "\x1b[92m" in res_pos  # Green

    # Decrease when lower is better (e.g. isolated nodes dropped from 5 to 0)
    res_dec = format_delta(0, 5, higher_is_better=False)
    assert "-5" in res_dec
    assert "\x1b[92m" in res_dec  # Green

    # Regressive increase when lower is better (e.g. broken links increased from 0 to 4)
    res_bad = format_delta(4, 0, higher_is_better=False)
    assert "+4" in res_bad
    assert "\x1b[91m" in res_bad  # Red

    # Stable (no change)
    res_stable = format_delta(15, 15, higher_is_better=True)
    assert "stable" in res_stable


def test_generate_markdown_report_frontmatter(mock_audit_data):
    """Verifies that generated markdown reports contain machine-readable YAML frontmatter."""
    strict_passed, violations = verify_strict_invariants(mock_audit_data)
    telemetry = build_standard_telemetry(mock_audit_data, mode="quick", strict_passed=strict_passed, violations=violations)

    md_content = generate_markdown_report(telemetry, mock_audit_data)
    assert md_content.startswith("---\n")
    assert 'schema_version: "1.0"' in md_content
    assert "timestamp:" in md_content
    assert 'platform_grade: "A+"' in md_content
    assert 'strict_invariants: "PASSED"' in md_content
    assert "---\n\n# 🪐 Physics Lab — Platform Assessment Report" in md_content
    assert "## 🧮 2. Mathematical Manifold & Lineage Architecture" in md_content
    assert "## 🏛️ 3. Subtopic Knowledge Web & OPS Quality Gates" in md_content
    assert "## 📋 4. Roadmap Realization" in md_content


def test_print_telemetry_diff_rendering(capsys, mock_audit_data):
    """Verifies that print_telemetry_diff formats side-by-side terminal diff cleanly."""
    from scripts.maintenance.run_project_assessment import print_telemetry_diff
    strict_passed, violations = verify_strict_invariants(mock_audit_data)
    curr = build_standard_telemetry(mock_audit_data, mode="quick", strict_passed=strict_passed, violations=violations)

    # Clone for prev with slight variations
    prev = dict(curr)
    prev["mathematical_manifold"] = dict(curr["mathematical_manifold"])
    prev["mathematical_manifold"]["total_formulas"] = 14660

    print_telemetry_diff(curr, prev, target_label="test_baseline")
    captured = capsys.readouterr().out

    assert "PLATFORM TELEMETRY DIFF" in captured
    assert "Formulas Cataloged:" in captured
    assert "(+11)" in captured
    assert "Strict Gate Status:" in captured


def test_audit_cache_freshness():
    """Verifies that audit_cache_freshness returns valid disk cache structure."""
    from scripts.maintenance.run_project_assessment import audit_cache_freshness
    res = audit_cache_freshness()
    assert "total_cached" in res
    assert "fresh_count" in res
    assert "stale_count" in res
    assert "freshness_pct" in res
    assert "status" in res
    assert res["total_cached"] >= 0
    assert 0.0 <= res["freshness_pct"] <= 100.0


def test_audit_git_changed_execution(capsys):
    """Verifies that audit_git_changed runs rapidly without unhandled exceptions."""
    from scripts.maintenance.run_project_assessment import audit_git_changed
    audit_git_changed(strict=False)
    captured = capsys.readouterr().out
    assert "GIT INCREMENTAL AUDIT" in captured
    assert "Audit completed in" in captured


def test_heal_all_execution(capsys):
    """Verifies that heal_all runs smoothly and reports remediation counts."""
    from scripts.maintenance.run_project_assessment import heal_all
    heal_all()
    captured = capsys.readouterr().out
    assert "AUTONOMOUS PLATFORM SELF-HEALING" in captured
    assert "Shard Hash Registry:" in captured
    assert "Lineage Derivation DAG:" in captured


def test_audit_domain_scope_execution(capsys):
    """Verifies that audit_domain_scope resolves a domain and prints scorecard."""
    from scripts.maintenance.run_project_assessment import audit_domain_scope
    audit_domain_scope("quantum")
    captured = capsys.readouterr().out
    assert "DOMAIN TELEMETRY SCORECARD" in captured
    assert "Quantum Physics & Mechanics" in captured
    assert "Total Subtopics:" in captured


def test_audit_shard_scope_execution(capsys):
    """Verifies that audit_shard_scope resolves a hex shard and prints scorecard."""
    from scripts.maintenance.run_project_assessment import audit_shard_scope
    audit_shard_scope("00")
    captured = capsys.readouterr().out
    assert "HEX SHARD SCORECARD" in captured
    assert "Shard 00" in captured
    assert "Formula Count:" in captured


def test_audit_ratchets_clean(mock_audit_data):
    """Verifies that audit_ratchets passes when metrics meet or exceed baseline."""
    from scripts.maintenance.run_project_assessment import audit_ratchets
    passed, violations, warnings, details = audit_ratchets(mock_audit_data)
    assert passed is True
    assert len(violations) == 0


def test_audit_ratchets_regressions(mock_audit_data):
    """Verifies that ratchets catch LHI drop, formula loss, and CAS latency spike."""
    from scripts.maintenance.run_project_assessment import audit_ratchets

    # Simulate LHI regression
    mock_audit_data["diagnostics"]["lineage"]["lhi_score"] = 92.0
    # Simulate formula count drop
    mock_audit_data["diagnostics"]["lineage"]["total_formulas"] = 14000
    # Simulate CAS latency spike
    mock_audit_data["diagnostics"]["cas_benchmark"]["latency_ms"] = 650.0

    passed, violations, warnings, details = audit_ratchets(mock_audit_data)
    assert passed is False
    assert len(violations) >= 3
    violation_str = " ".join(violations)
    assert "LHI" in violation_str
    assert "Formula count dropped" in violation_str
    assert "CAS latency" in violation_str
