import pytest
from scripts.maintenance.hallucination_shield import HallucinationShield

def test_hallucination_shield_checks():
    # Instantiate the shield (will load physical data but we will mock/test the audit_node method directly)
    shield = HallucinationShield()

    # Case 1: Healthy Node (Passes all checks)
    healthy_sub = {
        "title": "Quantum Mechanics Foundations",
        "standard": "platinum",
        "content": (
            "<p>The quantum state of a physical system is represented as a wave function \\( \\psi \\) in Hilbert space. "
            "Under this framework, Planck's constant \\( \\hbar \\) sets the scale of the quantum action, "
            "governing the commutation relations between position and momentum.</p>"
            "<p>By applying the Hamiltonian operator \\( \\hat{H} \\), the system evolves over time in accordance "
            "with the Schrödinger equation. These fundamental principles dictate the wave-particle behavior.</p>"
        )
    }
    violations = shield.audit_node("quantum-foundations", healthy_sub)
    assert len(violations) == 0, f"Expected healthy node to pass, but got: {violations}"

    # Case 2: Symbol-Prose Drift (Uses \hbar but mentions no planck/quantum keywords)
    drift_sub = {
        "title": "Unanchored Math",
        "standard": "platinum",
        "content": (
            "<p>The system is characterized by high velocities and arbitrary coordinate systems. "
            "We simply typeset \\( \\hbar \\) without explaining its meaning or physical role.</p>"
        )
    }
    violations = shield.audit_node("unanchored-math", drift_sub)
    assert len(violations) >= 1
    assert any(v["type"] == "Symbol-Prose Drift" for v in violations)

    # Case 3: Delimiter Leak (Leaking $$ or \\[ inside paragraphs)
    leak_sub_1 = {
        "title": "Leaked Delimiter",
        "standard": "platinum",
        "content": "<p>The equation is given by $$E = mc^2$$, which shows energy-momentum equivalence.</p>"
    }
    violations_1 = shield.audit_node("leak-1", leak_sub_1)
    assert any(v["type"] == "Delimiter Leak" for v in violations_1)

    leak_sub_2 = {
        "title": "Leaked Display Delimiter",
        "standard": "platinum",
        "content": "<p>We compute \\[ \\nabla^2 \\phi = 0 \\] inside the standard paragraph text.</p>"
    }
    violations_2 = shield.audit_node("leak-2", leak_sub_2)
    assert any(v["type"] == "Delimiter Leak" for v in violations_2)

    # Case 4: Glossary Pattern (Listed glossary-like variables following equation)
    glossary_sub = {
        "title": "Glossary Node",
        "standard": "platinum",
        "content": (
            "<p>The electromagnetic field tensor can be written as follows:</p>"
            "<div class=\"math-display\">\\[ F_{\\mu\\nu} = \\partial_\\mu A_\\nu - \\partial_\\nu A_\\mu \\]</div>"
            "<p>where \\( F_{\\mu\\nu} \\) is the electromagnetic field strength tensor, "
            "where \\( A_\\mu \\) denotes the vector potential, "
            "where \\( \\partial_\\mu \\) signifies the partial derivative, "
            "and where \\( J \\) represents the source current density.</p>"
        )
    }
    violations_3 = shield.audit_node("glossary-node", glossary_sub)
    assert any(v["type"] == "Glossary Pattern" for v in violations_3)

    # Case 5: Unbalanced Delimiters (Open delimiter but no close)
    unbalanced_sub = {
        "title": "Unbalanced Brackets",
        "standard": "platinum",
        "content": "<p>We define the metric \\( g_{\\mu\\nu} without closing the parenthesis typesetter.</p>"
    }
    violations_4 = shield.audit_node("unbalanced-node", unbalanced_sub)
    assert any(v["type"] == "Balanced Delimiters" for v in violations_4)
