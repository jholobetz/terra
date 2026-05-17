from orchestrator import PhysicsOrchestrator

orch = PhysicsOrchestrator()

test_html = """
<p>In modern university-level physics, we often explore complex systems.</p>
<h3>2. <a href="/physics/subtopic/action-functional" class="subtopic-link"><strong>The Action Functional</strong></a> on a Spacetime Manifold</h3>
<p>Imagine a world where friction doesn't exist.</p>
"""

print("--- Original HTML ---")
print(test_html)

print("\n--- Running Sanitization ---")
sanitized = orch.sanitize_content(test_html)

print("\n--- Sanitized HTML ---")
print(sanitized)
