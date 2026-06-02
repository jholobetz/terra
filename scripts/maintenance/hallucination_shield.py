import re
import argparse
import sys
from orchestrator import PhysicsOrchestrator

# Standard symbols mapped to semantic keyword anchors
SYMBOL_ANCHORS = {
    r"\hbar": ["planck", "quantum", "action", "commutator", "h-bar", "constant"],
    r"g_{\mu\nu}": ["metric", "curvature", "spacetime", "manifold", "einstein", "geometry"],
    r"g^{\mu\nu}": ["metric", "curvature", "spacetime", "manifold", "einstein", "geometry"],
    r"\mathcal{L}": ["lagrangian", "density", "action", "integral", "field"],
    r"\hat{H}": ["hamiltonian", "operator", "energy", "eigenstate", "schrodinger"],
    r"\psi": ["wave", "function", "state", "amplitude", "probability", "spinor", "field"],
    r"\Psi": ["wave", "function", "state", "amplitude", "probability", "spinor", "field"],
    r"\nabla": ["derivative", "gradient", "divergence", "curl", "covariant", "differential"],
    r"\partial": ["derivative", "gradient", "divergence", "curl", "differential", "derivative"],
    r"\Gamma": ["christoffel", "connection", "coefficient", "symbol", "affine"],
    r"R_{\mu\nu}": ["ricci", "riemann", "tensor", "curvature", "gravity"],
    r"\eta_{\mu\nu}": ["minkowski", "flat", "metric", "spacetime", "limit"]
}

class HallucinationShield:
    def __init__(self, content_dir="app/config/content"):
        self.orch = PhysicsOrchestrator(content_dir=content_dir)
        self.all_subtopics = self.orch.data["subtopics"]

    def audit_node(self, slug, sub):
        """Audits a single subtopic node for semantic drift and mathematical consistency."""
        content = sub.get("content", "")
        title = sub.get("title", "")
        standard = sub.get("standard", "legacy")
        violations = []

        if not content:
            return violations

        # Check 1: Symbol-Prose Anchor Consistency (Intellectual Drift)
        # If a node uses complex typeset math symbols, it MUST explain their physical context.
        for symbol, anchors in SYMBOL_ANCHORS.items():
            if symbol in content:
                # Extract surrounding plain text to see if the semantic anchor is present
                text_only = re.sub(r'<[^>]+>', ' ', content).lower()
                if not any(anchor in text_only for anchor in anchors):
                    violations.append({
                        "type": "Symbol-Prose Drift",
                        "severity": "Warning",
                        "message": f"Mathematical symbol '{symbol}' is typeset, but none of its expected physical anchors {anchors} appear in the prose text."
                    })

        # Check 2: Delimiter Leaks (Formatting / Raw LaTeX Leakage)
        # Banned raw LaTeX display symbols inside paragraphs.
        p_blocks = re.findall(r'<p>(.*?)</p>', content, re.DOTALL)
        for idx, p in enumerate(p_blocks):
            if "$$" in p:
                violations.append({
                    "type": "Delimiter Leak",
                    "severity": "Critical",
                    "message": f"Paragraph {idx + 1} contains raw display delimiters '$$'. Display equations must use '<div class=\"math-display\">' with '\\[...\\]'."
                })
            if "\\[" in p or "\\]" in p:
                # Verify if it is wrapped in math-display div or leaked inside a standard <p>
                # Standard paragraph should use inline \\( ... \\) only.
                violations.append({
                    "type": "Delimiter Leak",
                    "severity": "Critical",
                    "message": f"Paragraph {idx + 1} contains raw display delimiters '\\[' or '\\]'. Display equations should be outside standard paragraph text."
                })

        # Check 3: The Glossary Pattern (Immediate Variable Coupling Violation)
        # Detect glossary-style bullet-like listings of variable explanations following equations.
        # e.g., "...where A is..., B is..., C is..."
        glossary_regex = r"(?:where|here)\s+(?:\\\(.*?\\\)|[a-zA-Z]|\\[a-zA-Z]+)\s+(?:is|represents|denotes|refers\s+to|signifies)\s+[^,;\.]{1,80}(?:,|\s+and|;)"
        matches = re.findall(glossary_regex, content, re.IGNORECASE)
        if len(matches) >= 3:
            violations.append({
                "type": "Glossary Pattern",
                "severity": "Warning",
                "message": f"Found {len(matches)} consecutive glossary-style variable definitions (e.g., '{matches[0]}'). Symbols must be actively woven into the narrative sentences instead of defined in a listed glossary format."
            })

        # Check 4: Unbalanced Bracket/Delimiter Count
        # Checks if LaTeX delimiters are balanced within the HTML block.
        inline_open = len(re.findall(r'\\\(', content))
        inline_close = len(re.findall(r'\\\)', content))
        if inline_open != inline_close:
            violations.append({
                "type": "Balanced Delimiters",
                "severity": "Critical",
                "message": f"Inline LaTeX delimiters are unbalanced: opened {inline_open} times, closed {inline_close} times."
            })

        return violations

    def run_audit(self, target_slug=None):
        """Audits all graduated platinum nodes or a specific target slug."""
        results = {}
        target_count = 0
        violation_count = 0
        critical_count = 0

        print("================================================================================")
        print("               🪐 PHYSICS LAB: HALLUCINATION & DRIFT SHIELD                    ")
        print("================================================================================")

        for shard_name, shard_data in self.orch.shards.items():
            for slug, sub in shard_data.items():
                if target_slug and slug != target_slug:
                    continue
                
                # We only audit platinum nodes (since they are active and graduated)
                if sub.get("standard") != "platinum":
                    continue

                target_count += 1
                node_violations = self.audit_node(slug, sub)
                if node_violations:
                    results[slug] = {
                        "title": sub.get("title", slug),
                        "shard": shard_name,
                        "violations": node_violations
                    }
                    for v in node_violations:
                        violation_count += 1
                        if v["severity"] == "Critical":
                            critical_count += 1

        # Print results
        if not results:
            print(f"✓ SECURE: Audited {target_count} graduated nodes. Zero drift or mathematical hallucinations detected!")
            print("================================================================================")
            return True

        for slug, info in results.items():
            print(f"\n❌ NODE: {slug} ({info['title']}) | Shard: {info['shard']}")
            for idx, v in enumerate(info["violations"]):
                color = "⚠️" if v["severity"] == "Warning" else "🔥"
                print(f"  {idx + 1}. [{v['type']}] ({v['severity']}) - {v['message']}")

        print("\n================================================================================")
        print(f"AUDIT SUMMARY:")
        print(f"  * Total Graduated Nodes Audited: {target_count}")
        print(f"  * Total Flagged Violations:      {violation_count} ({critical_count} critical, {violation_count - critical_count} warnings)")
        print(f"  * Pass Rate:                     {round((1 - (len(results) / target_count)) * 100, 2)}%")
        print("================================================================================")
        
        return critical_count == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit Physics Lab nodes for drift and hallucinations.")
    parser.add_argument("--slug", help="Audit a specific subtopic slug.")
    args = parser.parse_args()

    shield = HallucinationShield()
    success = shield.run_audit(target_slug=args.slug)
    sys.exit(0 if success else 1)
