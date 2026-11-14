"""Regression tests for view monolith decomposition, CSS/JS asset extraction, and CSP nonce hygiene."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
VIEWS_DIR = ROOT / "app" / "views" / "physics"


def test_all_physics_views_under_1000_lines():
    """Ensure no physics view template regresses into a >1,000-line HTML/CSS/JS monolith."""
    oversized = []
    for view_path in sorted(VIEWS_DIR.rglob("*.php")):
        line_count = sum(1 for _ in view_path.open(encoding="utf-8"))
        if line_count >= 1000:
            oversized.append(f"{view_path.relative_to(ROOT)} ({line_count} lines)")

    assert not oversized, f"Physics view templates must remain under 1,000 lines: {oversized}"


def test_extracted_static_assets_exist_and_contain_no_php_tags():
    """Verify extracted CSS and JS bundles exist, are non-empty, and contain zero raw PHP tags."""
    expected_assets = [
        ROOT / "public" / "js" / "topic_constellation.js",
        ROOT / "public" / "css" / "topic_constellation.css",
        ROOT / "public" / "css" / "equation_explainer.css",
        ROOT / "public" / "css" / "lab_tools.css",
        ROOT / "public" / "js" / "simulations_directory.js",
    ]
    for asset in expected_assets:
        assert asset.exists(), f"Missing extracted asset: {asset.relative_to(ROOT)}"
        content = asset.read_text(encoding="utf-8")
        assert len(content.strip()) > 200, f"Extracted asset unexpectedly small: {asset.relative_to(ROOT)}"
        assert "<?php" not in content and "<?=" not in content, (
            f"Raw PHP tag leaked into static asset {asset.relative_to(ROOT)}"
        )


def test_layout_extra_css_hook_and_controller_wiring():
    """Verify layout.php renders $extra_css in <head> and PhysicsController wires extracted CSS + cache invalidation."""
    layout_html = (VIEWS_DIR / "layout.php").read_text(encoding="utf-8")
    head_section = layout_html.split("</head>")[0]
    assert "$extra_css" in head_section, "layout.php must render $extra_css stylesheets inside <head>"

    controller_php = (ROOT / "app" / "controllers" / "PhysicsController.php").read_text(encoding="utf-8")
    for css_name in ("lab_tools.css", "equation_explainer.css", "topic_constellation.css"):
        assert css_name in controller_php, f"PhysicsController.php must wire '{css_name}' via extra_css"

    assert "topic_constellation.js" in controller_php, (
        "PhysicsController::isHubCacheStale() must check topic_constellation.js mtime"
    )


def test_inline_executable_scripts_have_csp_nonce():
    """Ensure every executable inline <script> in physics views carries a CSP nonce attribute."""
    script_tag_re = re.compile(r"<script\b([^>]*)>", re.IGNORECASE)
    violations = []

    for view_path in sorted(VIEWS_DIR.rglob("*.php")):
        content = view_path.read_text(encoding="utf-8")
        for match in script_tag_re.finditer(content):
            attrs = match.group(1)
            # External scripts with src=... are allowed via 'self' (though nonced too)
            if re.search(r"\bsrc\s*=", attrs, re.IGNORECASE):
                continue
            # Non-executable JSON data islands do not execute under CSP script-src
            if re.search(r'\btype\s*=\s*["\']application/(?:ld\+)?json["\']', attrs, re.IGNORECASE):
                continue
            if not re.search(r"\bnonce\s*=", attrs, re.IGNORECASE):
                line_no = content[: match.start()].count("\n") + 1
                violations.append(f"{view_path.relative_to(ROOT)}:{line_no} -> <script{attrs}>")

    assert not violations, (
        "Executable inline <script> tags without nonce are blocked by SecurityHeadersMiddleware CSP:\n"
        + "\n".join(violations)
    )
