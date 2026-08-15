"""
Track 2 Test Suite: Batch AST Auto-Remediation & Shard Scanner
==============================================================
Validates:
  - Multi-tier delimiter and prose tokenization
  - Unwrapped TeX command repair
  - Structured semantic variable normalization and operator classification
  - Strict idempotency guarantees (f(f(x)) === f(x))
"""

import pytest
from scripts.batch_auto_remediation import TerraASTNormalizer, TokenType


@pytest.fixture
def normalizer():
    return TerraASTNormalizer()


def test_unwrapped_euler_lagrange_delimiters_repaired(normalizer):
    corrupted = (
        "1. **Conservative Systems**: For systems where all forces are derivable from a potential $, "
        "the Lagrangian is = T - V$. If $ does not explicitly depend on $, then = $-\\frac{\\partial V}{\\partial $q_i$}$, "
        "representing the generalized conservative force. "
        "2. **Cyclic Coordinates**: If = $\\frac{\\partial L}{\\partial $q_i$} = 0$, then $ is a cyclic coordinate, "
        "and its conjugate momentum = \\frac{\\partial L}{\\partial \\dot{q}_i}$ is a conserved quantity. "
        "3. **Non-Conservative Forces**: In the presence of non-conservative forces, the Euler-Lagrange equation is often "
        "extended to $\\frac{d}{dt}$\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) $- \\frac{\\partial L}{\\partial $q_i$}$ = Q_i^{\\text{nc}}$, "
        "where ^{\\text{nc}}$ is the generalized non-conservative force. "
        "In this context, = $\\frac{\\partial L}{\\partial $q_i$}$ still represents the generalized force component."
    )

    cleaned = normalizer.normalize_text(corrupted)

    # 1. Check parity: dollar signs must be balanced (even count)
    assert cleaned.count("$") % 2 == 0
    # 2. Check that the fractured Euler-Lagrange equation is unified
    assert "$\\frac{d}{dt}\\left(\\frac{\\partial L}{\\partial \\dot{q}_i}\\right) - \\frac{\\partial L}{\\partial q_i} = Q_i^{\\text{nc}}$" in cleaned
    # 3. Check that potential V and coordinate q_i are restored
    assert "$L = T - V$" in cleaned
    assert "$F_i = -\\frac{\\partial V}{\\partial q_i}$" in cleaned
    assert "$p_i = \\frac{\\partial L}{\\partial \\dot{q}_i}$" in cleaned
    assert "$Q_i^{\\text{nc}}$" in cleaned


def test_idempotency_guarantee(normalizer):
    sample = "Under canonical quantization $[\\hat{q}_i, \\hat{p}_j] = i\\hbar \\delta_{ij}$ on cotangent bundle $T^*Q$."
    pass1 = normalizer.normalize_text(sample)
    pass2 = normalizer.normalize_text(pass1)
    pass3 = normalizer.normalize_text(pass2)

    assert pass1 == pass2
    assert pass2 == pass3


def test_semantic_variable_upgrade_and_operator_tagging(normalizer):
    legacy_vars = {
        "\\nabla": "\\(\\nabla\\) - The del gradient operator.",
        "\\nabla^2": "Laplacian operator m^-2.",
        "p_i": "Conjugate momentum kg*m/s.",
        "": "Empty key"
    }

    norm_vars, modified = normalizer.normalize_semantic_variables(legacy_vars)

    assert modified is True
    assert "" not in norm_vars
    assert "\\nabla" in norm_vars
    assert norm_vars["\\nabla"]["type"] == "operator"
    assert "\\nabla^2" in norm_vars
    assert norm_vars["\\nabla^2"]["type"] == "operator"
    assert "p_i" in norm_vars
    assert norm_vars["p_i"]["type"] == "variable"


def test_nested_frac_dollar_sanitization(normalizer):
    sample = "Equation $\\frac{$E$}{$c^2$}$ yields mass $m$."
    cleaned = normalizer.normalize_text(sample)

    assert cleaned == "Equation $\\frac{E}{c^2}$ yields mass $m$."
