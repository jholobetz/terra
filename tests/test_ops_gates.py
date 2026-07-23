"""Black-box tests for the OPS static syntax guards in run_gqs_sprint.py.

Each test crafts a batch_payload.json variant, drives the gate via --dry-run,
and asserts both exit code and a substring of the expected violation message.
The happy-path test establishes that the golden prose alone passes every gate.
"""

# Five paragraphs of OPS-shaped prose. Total word count lands inside 650–1000
# after HTML/LaTeX stripping; first word is "Conservation" (no In Media Res
# trigger); title-overlap is avoided when the default title is used.
GOLDEN_PARAGRAPHS = (
    "<p>Conservation of momentum under spatial translation symmetry implies that the "
    "total system momentum remains invariant in the absence of external forces, with "
    "Noether's correspondence providing the formal bridge between continuous symmetries "
    "and conserved currents throughout classical field theory. The action functional "
    "remains invariant under infinitesimal coordinate displacement, yielding a "
    "divergence-free current whose temporal component integrates to the conserved "
    "charge over any spacelike hypersurface, with the four-current encoding the "
    "underlying symmetry generator across spacetime regions. Within Hamiltonian "
    "mechanics the conserved quantity corresponds to a phase-space function whose "
    "Poisson bracket with the Hamiltonian vanishes identically, providing an "
    "equivalent algebraic formulation through the canonical structure of symplectic "
    "geometry. The principle generalizes seamlessly to gauge theories where local "
    "symmetries demand covariant derivatives and field-strength tensors, yielding "
    "conserved currents associated with internal symmetry transformations rather "
    "than spacetime translations across the standard model framework.</p>",

    "<p>Rotational invariance under arbitrary spatial rotations generates conservation "
    "of angular momentum through the corresponding generator algebra, where the "
    "antisymmetric tensor structure encodes three independent conserved components in "
    "three-dimensional space. The angular momentum vector decomposes naturally into "
    "orbital and intrinsic spin contributions, with the latter requiring half-integer "
    "or integer eigenvalues dictated by the representation theory of the rotation "
    "group acting on Hilbert space. Quantum mechanical operators inherit this "
    "algebraic structure through the canonical commutation relations between "
    "components, producing the Casimir invariant whose eigenvalues classify "
    "irreducible representations of the algebra across multiplets. Selection rules "
    "for radiative transitions follow directly from these representations through "
    "the Wigner-Eckart theorem, factoring matrix elements into geometric and reduced "
    "parts that separate spatial dependence from dynamical content within atomic and "
    "nuclear processes.</p>",

    "<p>Temporal translation symmetry mandates conservation of energy through the "
    "corresponding Noether current, with the Hamiltonian playing the role of "
    "generator for time evolution within the canonical framework of classical and "
    "quantum mechanics. Energy decomposes into kinetic and potential contributions "
    "in non-relativistic mechanics, while relativistic dynamics merges these into "
    "the time component of the energy-momentum four-vector together with spatial "
    "momentum components across inertial frames. The stress-energy tensor extends "
    "this concept to continuous field configurations, providing local densities and "
    "fluxes whose conservation equations follow directly from translational "
    "invariance of the action principle on flat backgrounds. Curved spacetime breaks "
    "global translational symmetry, replacing exact energy conservation with "
    "covariant conservation of the stress-energy tensor through the contracted "
    "Bianchi identities and the Einstein field equations governing gravitational "
    "geometry.</p>",

    "<p>Local gauge invariance under phase rotations of complex fields produces "
    "conservation of electric charge through the associated Noether current, "
    "coupling matter fields to the electromagnetic gauge potential via the covariant "
    "derivative prescription throughout abelian theories. Non-abelian extensions "
    "introduce structure constants of the underlying Lie algebra, generating "
    "self-interacting gauge bosons whose field-strength tensors include commutator "
    "terms absent from the abelian case across Yang-Mills constructions. Quantum "
    "chromodynamics realizes this construction across the strong sector, while "
    "electroweak dynamics describes unified weak and electromagnetic interactions "
    "prior to spontaneous breaking by the Higgs mechanism within the standard "
    "model. Anomalies in the path integral measure can destroy classical symmetries "
    "upon quantization, requiring careful cancellation conditions to preserve "
    "renormalizability and unitarity throughout chiral gauge sectors of the "
    "interacting theory.</p>",

    "<p>Spontaneous symmetry breaking transforms exact conservation laws into "
    "approximate or pseudo-conserved quantities, generating Goldstone modes whose "
    "masslessness reflects the residual symmetry of the broken vacuum state across "
    "infrared scales. The associated current remains conserved while the corresponding "
    "charge fails to annihilate the ground state, producing distinctive low-energy "
    "excitations governed by effective Lagrangians constructed from symmetry "
    "considerations alone within phenomenological frameworks. Explicit symmetry "
    "breaking introduces small parameters that lift Goldstone modes to "
    "pseudo-Goldstone bosons, with pions providing the archetypal realization "
    "through chiral symmetry breaking in the light quark sector of hadronic "
    "physics. Anomalous symmetries similarly produce partial conservation laws "
    "whose violations encode quantum effects absent from classical analyses, "
    "manifesting in processes forbidden by classical selection rules yet permitted "
    "through loop diagrams within the full interacting theory.</p>",
)

GOLDEN_CONTENT = "\n".join(GOLDEN_PARAGRAPHS)
DEFAULT_TITLE = "Polytropic Stellar Equilibrium"


def payload(content=GOLDEN_CONTENT, title=DEFAULT_TITLE, slug="conservation-laws"):
    return {slug: {"title": title, "content": content}}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_golden_prose_passes_all_gates(run_gates):
    res = run_gates(payload())
    assert res.returncode == 0, (
        f"Expected golden prose to pass, got exit {res.returncode}.\n"
        f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
    )
    assert "OPS STYLE VIOLATIONS" not in res.stdout
    assert "Guardrail Stage 1 PASS" in res.stdout


# ---------------------------------------------------------------------------
# Structural gates
# ---------------------------------------------------------------------------

def test_scaffolded_placeholder_blocked(run_gates):
    res = run_gates(payload(content="<p>[Paragraph 1 placeholder]</p>"))
    assert res.returncode == 1
    assert "scaffolded placeholder" in res.stdout


def test_no_html_paragraphs_blocked(run_gates):
    res = run_gates(payload(content="Plain text with absolutely no p tags anywhere."))
    assert res.returncode == 1
    assert "No valid HTML paragraphs" in res.stdout


def test_list_item_element_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("</p>", "<li>forbidden</li></p>", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "list elements" in res.stdout


def test_unordered_list_element_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("</p>", "<ul>forbidden</ul></p>", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "list elements" in res.stdout


def test_ordered_list_element_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("</p>", "<ol>forbidden</ol></p>", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "list elements" in res.stdout


def test_heading_element_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("</p>", "<h3>forbidden header</h3></p>", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "heading elements" in res.stdout


# ---------------------------------------------------------------------------
# Markdown residue
# ---------------------------------------------------------------------------

def test_markdown_double_asterisks_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("Conservation", "**Conservation**", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "Markdown residue" in res.stdout


def test_markdown_underscores_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace("Conservation", "__Conservation__", 1)
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "Markdown residue" in res.stdout


# ---------------------------------------------------------------------------
# Word-count band (650–1000)
# ---------------------------------------------------------------------------

def test_word_count_too_low_blocked(run_gates):
    # First two paragraphs only — well under 650.
    res = run_gates(payload(content="\n".join(GOLDEN_PARAGRAPHS[:2])))
    assert res.returncode == 1
    assert "Word count violation" in res.stdout


def test_word_count_too_high_blocked(run_gates):
    # Doubling the golden corpus pushes well past 1000.
    res = run_gates(payload(content=GOLDEN_CONTENT + "\n" + GOLDEN_CONTENT))
    assert res.returncode == 1
    assert "Word count violation" in res.stdout


# ---------------------------------------------------------------------------
# In Media Res
# ---------------------------------------------------------------------------

def test_forbidden_lead_starter_blocked(run_gates):
    bad_lead = (
        "<p>The concept refers to a foundational invariance principle that governs "
        "momentum exchange in isolated systems under spatial translations, with the "
        "remainder of this paragraph extending the original golden content so that "
        "word count remains within the band.</p>"
    )
    bad = bad_lead + "\n" + "\n".join(GOLDEN_PARAGRAPHS[1:])
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "In Media Res violation" in res.stdout
    assert "Starter phrase" in res.stdout


def test_title_appears_in_first_15_words_blocked(run_gates):
    # The golden P1 opens with "Conservation of momentum"; this title is a
    # substring of the first 15 words, which the gate forbids.
    res = run_gates(payload(title="Conservation of Momentum"))
    assert res.returncode == 1
    assert "In Media Res violation" in res.stdout
    assert "Title" in res.stdout


# ---------------------------------------------------------------------------
# Math display delimiters
# ---------------------------------------------------------------------------

def test_math_display_missing_delimiters_blocked(run_gates):
    bad = GOLDEN_CONTENT.replace(
        "</p>",
        '<div class="math-display">E = mc^2</div></p>',
        1,
    )
    res = run_gates(payload(content=bad))
    assert res.returncode == 1
    assert "Math display violation" in res.stdout
