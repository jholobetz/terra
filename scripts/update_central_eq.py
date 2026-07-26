import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shard_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/69/shard_69.json")

with open(shard_path, "r", encoding="utf-8") as f:
    data = json.load(f)

fmt = data["nearly-free-electron-central-equation-89f54ae3"]
fmt["title"] = "The Central Equation"
fmt["description"] = "Governs the Fourier components of electronic wavefunctions in a periodic crystal potential, determining energy band gaps in solid-state physics."
fmt["conceptual_definition"] = "The Central Equation is the fundamental matrix eigenvalue equation derived from the time-independent Schrödinger equation for an electron moving in a periodic crystal lattice. Formulated in reciprocal space using plane-wave expansions, it determines how periodic lattice potentials scatter plane-wave states and open energy band gaps at Brillouin zone boundaries."
fmt["interpretation"] = "The equation $(\\lambda_{\\mathbf{k}-\\mathbf{G}} - E) C_{\\mathbf{k}-\\mathbf{G}} + \\sum_{\\mathbf{G'}} V_{\\mathbf{G}-\\mathbf{G'}} C_{\\mathbf{k}-\\mathbf{G'}} = 0$ represents a system of coupled linear secular equations for the expansion coefficients $C_{\\mathbf{k}-\\mathbf{G}}$ of a Bloch electron wavefunction. The kinetic energy term $(\\lambda_{\\mathbf{k}-\\mathbf{G}} - E) C_{\\mathbf{k}-\\mathbf{G}}$ represents the unperturbed energy $\\lambda_{\\mathbf{k}-\\mathbf{G}} = \\frac{\\hbar^2 |\\mathbf{k} - \\mathbf{G}|^2}{2m}$ relative to total energy $E$. The summation term $\\sum_{\\mathbf{G'}} V_{\\mathbf{G}-\\mathbf{G'}} C_{\\mathbf{k}-\\mathbf{G'}}$ calculates Bragg scattering between plane-wave components $C_{\\mathbf{k}-\\mathbf{G'}}$ mediated by Fourier components $V_{\\mathbf{G}-\\mathbf{G'}}$ of the periodic lattice potential $V(\\mathbf{r})$. Non-trivial solutions require the secular determinant to vanish, yielding energy eigenvalues $E(\\mathbf{k})$ and energy band gaps at zone boundaries."
fmt["symmetry_origin"] = "Originates from continuous spatial translation symmetry broken into discrete lattice translation symmetry $V(\\mathbf{r} + \\mathbf{R}) = V(\\mathbf{r})$. By Bloch's theorem, the electronic wavefunctions $\\psi_{\\mathbf{k}}(\\mathbf{r}) = e^{i \\mathbf{k} \\cdot \\mathbf{r}} u_{\\mathbf{k}}(\\mathbf{r})$ expand into reciprocal lattice plane waves, decoupling the Schrödinger equation into independent matrix blocks for each crystal momentum $\\mathbf{k}$ inside the first Brillouin zone."
fmt["limits_and_boundary"] = "In the free-electron limit ($V(\\mathbf{r}) \\to 0$), all Fourier components vanish ($V_{\\mathbf{G}-\\mathbf{G'}} = 0$), reducing the equation to $(\\lambda_{\\mathbf{k}-\\mathbf{G}} - E) C_{\\mathbf{k}-\\mathbf{G}} = 0$. This recovers parabolic free-electron dispersion $E = \\lambda_{\\mathbf{k}-\\mathbf{G}} = \\frac{\\hbar^2 |\\mathbf{k}-\\mathbf{G}|^2}{2m}$. Near Brillouin zone boundaries where $\\lambda_{\\mathbf{k}} \\approx \\lambda_{\\mathbf{k}-\\mathbf{G}}$, two plane waves dominate ($2 \\times 2$ determinant), producing a band gap of magnitude $E_g = 2 |V_{\\mathbf{G}}|$."

with open(shard_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("NEARLY-FREE-ELECTRON-CENTRAL-EQUATION-89F54AE3 UPDATED WITH RIGOROUS MATH DELIMITERS!")
