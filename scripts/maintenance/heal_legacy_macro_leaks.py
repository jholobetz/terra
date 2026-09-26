#!/usr/bin/env python3
"""
scripts/maintenance/heal_legacy_macro_leaks.py

Deterministic sitewide healer for the 127 legacy formulas containing leaked
LaTeX macros outside math delimiters.
"""
import glob
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.lib.delimiters import strip_math_blocks, validate_narrative_delimiters

SHARDS_DIR = os.path.join(PROJECT_ROOT, "app", "config", "content", "formulas")

TEX_MACRO_CHECK = re.compile(
    r"\\(to|mu|lambda|theta|partial|nabla|int|sum|frac|sqrt|alpha|beta|gamma|delta|epsilon|sigma|omega|infty|cdot|times|pm|leq|geq|neq|approx|equiv|hat|bar|vec|tilde|mathbf|mathrm)(?![a-zA-Z])"
)

NARRATIVE_FIELDS = [
    "conceptual_definition",
    "intuitive_summary",
    "interpretation",
    "limits_and_boundary",
    "symmetry_origin",
]

def heal_formula_text(fid: str, field: str, text: str) -> str:
    """Repairs leaked LaTeX macros and broken math delimiters in narrative prose."""
    if not text or not isinstance(text, str):
        return text

    t = text

    # 1. Clean literal escaped dollars
    t = t.replace(r"\$\boldsymbol{\tau}\$", r"$\boldsymbol{\tau}$")
    t = t.replace(r"\$\boldsymbol{L}\$", r"$\boldsymbol{L}$")
    t = t.replace(r"\$\boldsymbol{\alpha}\$", r"$\boldsymbol{\alpha}$")
    t = t.replace(r"\$\boldsymbol{I}\$", r"$\boldsymbol{I}$")
    t = t.replace(r"\$\boldsymbol{\omega}\$", r"$\boldsymbol{\omega}$")

    # 2. Specific fragmented delimiter repairs
    t = t.replace(r"f$\text{(x)}$\$", r"$f(x)$")
    t = t.replace(r"f$\text{(x)}$\\", r"$f(x)$")
    t = t.replace(r"\hat{${$\phi$}}$x$", r"$\hat{\phi}(x)$")
    t = t.replace(r"\hat{\phi} f$", r"$\hat{\phi}(f)$")
    t = t.replace(r"$\mathbf{I}$ and $\boldsymbol${$\omega$}", r"$\mathbf{I}$ and $\boldsymbol{\omega}$")
    t = t.replace(r"$\boldsymbol${$\omega$}", r"$\boldsymbol{\omega}$")
    t = t.replace(r"$\boldsymbol${$\alpha$}", r"$\boldsymbol{\alpha}$")

    # Commutator & limit fragments
    t = t.replace(r"equation$[\hat{x}, \hat{p}] \to 0$in", r"equation $[\hat{x}, \hat{p}] \to 0$ in")
    t = t.replace(r"limit$[\hat{x}, \hat{p}] \to 0$signifies", r"limit $[\hat{x}, \hat{p}] \to 0$ signifies")
    t = t.replace(r"by$[$\hat{x}$, $\hat{p}$] = i $\hbar$ where i$is", r"by $[\hat{x}, \hat{p}] = i\hbar$, where $i$ is")
    t = t.replace(r"condition$[$\hat{x}$, $\hat{p}$] \to 0 $thus implies that$i$\hbar \to$ 0 $which", r"condition $[\hat{x}, \hat{p}] \to 0$ thus implies that $i\hbar \to 0$, which")
    t = t.replace(r"constant \hbar \to 0$.", r"constant $\hbar \to 0$.")
    t = t.replace(r"constant $\hbar \to$ 0$.", r"constant $\hbar \to 0$.")
    t = t.replace(r"implies that $\Delta$ x $\Delta$ p \to 0$, meaning that both position$x$and momentum$p$", r"implies that $\Delta x \Delta p \to 0$, meaning that both position $x$ and momentum $p$")
    t = t.replace(r"as \hbar$becomes$significant", r"as $\hbar$ becomes significant")
    t = t.replace(r"uncertainty dominate$.", r"uncertainty dominate.")
    t = t.replace(r"position, $\hat{x} , and momentum, $\hat{p} ,", r"position, $\hat{x}$, and momentum, $\hat{p}$,")
    t = t.replace(r"$\mathbf{E}_{\perp}' \approx \mathbf{E}_{\perp} + \mathbf{v} \times \mathbf{B}. This approximation highlights how a moving observer perceives an additional electric field \mathbf{v} \times \mathbf{B} due to their motion through a magnetic field, which is fundamental to concepts like motional electromotive force. As$v \to c$, the Lorentz factor \gamma approaches infinity. If the term$($\mathbf{E}_{\perp} + \mathbf{v} \times \mathbf{B}$)$is non-zero, the perpendicular electric field \mathbf{E}_{\perp}$'$in the moving frame would become infinitely large, signifying the strong relativistic compression of fields and energy density for observers approaching the speed of light relative to a source$.",
                  r"$\mathbf{E}_{\perp}' \approx \mathbf{E}_{\perp} + \mathbf{v} \times \mathbf{B}$. This approximation highlights how a moving observer perceives an additional electric field $\mathbf{v} \times \mathbf{B}$ due to their motion through a magnetic field, which is fundamental to concepts like motional electromotive force. As $v \to c$, the Lorentz factor $\gamma$ approaches infinity. If the term $(\mathbf{E}_{\perp} + \mathbf{v} \times \mathbf{B})$ is non-zero, the perpendicular electric field $\mathbf{E}_{\perp}'$ in the moving frame would become infinitely large, signifying the strong relativistic compression of fields and energy density for observers approaching the speed of light relative to a source.")

    # 3. Scientific notation
    t = re.sub(r'(\d+(?:\.\d+)?)\s*\\times\s*10\^\{?(-?\d+)\}?', lambda m: f"${m.group(1)} \\times 10^{{{m.group(2)}}}$", t)

    # 4. Physical units with \cdot
    t = re.sub(r'\b(kg|J|N|W)\s*\\cdot\s*([a-zA-Z0-9\^/]+)', lambda m: f"$\\mathrm{{{m.group(1)}}} \\cdot \\mathrm{{{m.group(2)}}}$", t)
    t = re.sub(r'\(N\s*\\cdot\s*m\)', lambda _: "($\\mathrm{N} \\cdot \\mathrm{m}$)", t)
    t = re.sub(r'\(N/m\)\s*or\s*\(W/\(m\s*\\cdot\s*K\)\)', lambda _: "($\\mathrm{N/m}$) or ($\\mathrm{W/(m \\cdot K)}$)", t)
    t = re.sub(r'\(Energy\s*\\times\s*Time\s*/\s*Volume\)', lambda _: "($\\text{Energy} \\times \\text{Time} / \\text{Volume}$)", t)
    t = re.sub(r'\(Voltage\s*\\cdot\s*Time\)', lambda _: "($\\text{Voltage} \\cdot \\text{Time}$)", t)

    # Permittivity units
    t = re.sub(r'\$8\.854\s*\\times\s*10\^\{-12\}\s*\\text\{\s*C\}\^2/\$N\s*\\cdot\s*m\^2', lambda _: r"$8.854 \times 10^{-12} \text{ C}^2/(\mathrm{N} \cdot \mathrm{m}^2)$", t)
    t = re.sub(r'8\.854\s*\\times\s*10\^\{-12\}\s*\\text\{\s*C\}\^2/\(\$N\s*\\cdot\s*m\$\^2\)\)', lambda _: r"$8.854 \times 10^{-12} \text{ C}^2/(\mathrm{N} \cdot \mathrm{m}^2)$)", t)

    # 5. Gauge groups
    t = re.sub(r'SU\(2\)L\s*\\times\s*U\(1\)Y', lambda _: "$\\mathrm{SU}(2)_L \\times \\mathrm{U}(1)_Y$", t)
    t = re.sub(r'SU\(3\)\s*\\times\s*SU\(2\)\s*\\times\s*U\(1\)', lambda _: "$\\mathrm{SU}(3) \\times \\mathrm{SU}(2) \\times \\mathrm{U}(1)$", t)
    t = re.sub(r'4\s*\\times\s*4', lambda _: "$4 \\times 4$", t)

    # 6. Quoted formulas
    t = re.sub(r'"z\s*\\approx\s*([0-9\.]+)"', lambda m: f'"$z \\approx {m.group(1)}$"', t)
    t = re.sub(r'"z\s*\\to\s*([0-9\.]+)"', lambda m: f'"$z \\to {m.group(1)}$"', t)
    t = re.sub(r"'l_p\s*\\to\s*0'", lambda _: '"$l_p \\to 0$"', t)

    # 7. Conversational text mentions
    t = re.sub(r'The arrow\s*\\\((?:\s*\\to\s*)\\\)', lambda _: "The arrow ($\\to$)", t)
    t = re.sub(r'The arrow\s*\\to\s*0', lambda _: "The arrow $\\to 0$", t)
    t = re.sub(r'The arrow\s*\\to', lambda _: "The arrow $\\to$", t)
    t = re.sub(r'The symbol\s*\\to', lambda _: "The symbol $\\to$", t)
    t = re.sub(r'The notation\s*\\to', lambda _: "The notation $\\to$", t)
    t = re.sub(r'The cross product\s*\\times', lambda _: "The cross product $\\times$", t)
    t = re.sub(r'The cross product symbol\s*\\times', lambda _: "The cross product symbol $\\times$", t)
    t = re.sub(r"The\s*'\s*\\times\s*'\s*symbol", lambda _: "The '$\\times$' symbol", t)
    t = re.sub(r'The dot product\s*\\cdot', lambda _: "The dot product $\\cdot$", t)
    t = re.sub(r'The dot product\s*\(\s*\\cdot\s*\)', lambda _: "The dot product $(\\cdot)$", t)
    t = re.sub(r'The curly braces\s*\\\{\s*,\\cdot\s*\\\}', lambda _: "The curly braces $\{ , \\cdot \}$", t)
    t = re.sub(r'operator\s*\(\s*\\nabla\s*\\cdot\s*\)', lambda _: "operator ($\\nabla \\cdot$)", t)
    t = re.sub(r'operator\s*\(\s*\\nabla\s*\)', lambda _: "operator ($\\nabla$)", t)
    t = re.sub(r'gradient operator\s*\(\s*\\nabla\s*\)', lambda _: "gradient operator ($\\nabla$)", t)
    t = re.sub(r'gradient operator\s*\(F\s*=\s*-\s*\\nabla\s*V\)', lambda _: "gradient operator ($\\mathbf{F} = -\\nabla V$)", t)
    t = re.sub(r'gradient operator\s*\(F\s*=\s*-\s*\n\\nabla\s*V\)', lambda _: "gradient operator ($\\mathbf{F} = -\\nabla V$)", t)

    # 8. Bare vector operators & derivatives
    t = re.sub(r'(-\s*\\nabla\s*[A-Za-z])', lambda m: f"${m.group(1)}$", t)
    t = re.sub(r'(-\s*\n\\nabla\s*[A-Za-z])', lambda m: f"${m.group(1).replace(chr(10), ' ')}$", t)
    t = re.sub(r'(\b\\nabla\^2\s*[A-Za-z])', lambda m: f"${m.group(1)}$", t)
    t = re.sub(r'(\b\n\\nabla\^2\s*[A-Za-z])', lambda m: f"${m.group(1).replace(chr(10), ' ')}$", t)
    t = re.sub(r'\(z\s*\\to\s*[∞\\infty]\)', lambda _: "($z \\to \\infty$)", t)
    t = re.sub(r'\br\s*\\to\s*0\b', lambda _: "$r \\to 0$", t)
    t = re.sub(r'\bd\s*\\to\s*0\b', lambda _: "$d \\to 0$", t)
    t = re.sub(r'\bV_C(?:\(r\))?\s*\\to\s*0\b', lambda _: "$V_C \\to 0$", t)
    t = re.sub(r'\(i\s*\\to\s*i\)', lambda _: "($i \\to i$)", t)
    t = re.sub(r'\ba\(t\)\s*\\to\s*1\b', lambda _: "$a(t) \\to 1$", t)

    # Additional patterns
    t = re.sub(r'\b\\nabla\s*=\s*\\nabla\b', lambda _: "$\\nabla = \\nabla$", t)
    t = re.sub(r'\bThe equation\s*\\nabla\s*=\s*\\nabla\b', lambda _: "The equation $\\nabla = \\nabla$", t)
    t = re.sub(r'\\mathbf\{n\}\s*\\times\s*\(\s*\\mathbf\{E\}_1\s*-\s*\\mathbf\{E\}_2\s*\)\s*=\s*0', lambda _: r"$\mathbf{n} \times (\mathbf{E}_1 - \mathbf{E}_2) = 0$", t)
    t = re.sub(r'\\Box\s*=\s*\\frac\{1\}\{c\^2\}\s*\\frac\{\s*\\partial\s*\^2\}\{\s*\\partial\s*t\^2\}\s*-\s*\\nabla\^2', lambda _: r"$\Box = \frac{1}{c^2} \frac{\partial^2}{\partial t^2} - \nabla^2$", t)
    t = re.sub(r'H\s*\\approx\s*c_s\s*/\s*\\Omega', lambda _: r"$H \approx c_s / \Omega$", t)
    t = re.sub(r'\\Omega_\\Lambda\s*\(z\)\s*\\approx\s*\\Omega_m\s*\(z\)\s*\\iff\s*z\s*\\approx\s*0\.3', lambda _: r"$\Omega_\Lambda(z) \approx \Omega_m(z) \iff z \approx 0.3$", t)
    t = re.sub(r'\bz\s*\\approx\s*0\.3\b', lambda _: "$z \\approx 0.3$", t)

    return t

if __name__ == "__main__":
    print("Healer module initialized.")
