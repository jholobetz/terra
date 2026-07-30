import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "scripts"))
from terra_lexer import TerraLexer

shard_48_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/48/shard_48.json")

with open(shard_48_path, "r", encoding="utf-8") as f:
    data_48 = json.load(f)

fmt = data_48["many-body-electronic-hamiltonian"]
fmt["title"] = "Many-Body Electronic Hamiltonian"
fmt["equation"] = "\\hat{H} = \\sum_{i} \\frac{\\hat{p}_i^2}{2m} + \\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I) + \\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{r}_j|}"
fmt["description"] = "Represents the total energy operator for interacting electrons moving in the static Coulomb potential of fixed atomic nuclei under the Born-Oppenheimer approximation."
fmt["conceptual_definition"] = "The many-body electronic Hamiltonian describes the quantum state of a multi-electron system in an atom, molecule, or solid-state crystal. Formulated under the Born-Oppenheimer approximation, it contains the electronic kinetic energy, the attractive electron-nucleus potential, and the repulsive electron-electron Coulomb interaction."
fmt["interpretation"] = "The many-body electronic Hamiltonian $\\hat{H} = \\sum_{i} \\frac{\\hat{p}_i^2}{2m} + \\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I) + \\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{r}_j|}$ defines the quantum energy operator of an $N$-electron system. The operator $\\hat{H}$ represents total energy. The first term $\\sum_{i} \\frac{\\hat{p}_i^2}{2m}$ sums the single-particle kinetic energy of each electron $i$, where $\\hat{p}_i = -i\\hbar \\nabla_i$ is the electron momentum operator and $m$ is electron mass. The second term $\\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I)$ is the attractive Coulomb potential energy between electron $i$ at position $\\mathbf{r}_i$ and nucleus $I$ at fixed position $\\mathbf{R}_I$. The final term $\\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{r}_j|}$ accounts for the mutual Coulomb repulsion between all electron pairs $(i, j)$ separated by distance $|\\mathbf{r}_i - \\mathbf{r}_j|$. The prefactor $\\frac{1}{2}$ avoids double-counting pairs, while $i \\neq j$ excludes self-interaction."
fmt["symmetry_origin"] = "Originates from rotational $SO(3)$ symmetry and space translation symmetry within periodic crystal lattices (leading to Bloch's theorem). It applies the Born-Oppenheimer approximation, which decouples fast electronic motion from massive, slow nuclear dynamics."
fmt["limits_and_boundary"] = "1. **Non-Interacting Limit ($e \\to 0$)**: Reduces to a sum of independent single-particle Hamiltonians.\n2. **Electron Cusp Condition ($|\\mathbf{r}_i - \\mathbf{r}_j| \\to 0$)**: Coulomb repulsion diverges to $+\\infty$, creating a cusp in the wave function.\n3. **Large Separation Limit ($|\\mathbf{r}_i - \\mathbf{r}_j| \\to \\infty$)**: Inter-electron repulsion vanishes."

# Normalize record
lexer = TerraLexer()
lexer.normalize_formula(fmt)

with open(shard_48_path, "w", encoding="utf-8") as f:
    json.dump(data_48, f, indent=4, ensure_ascii=False)

print("UPDATED MANY-BODY-ELECTRONIC-HAMILTONIAN IN SHARD_48 SUCCESSFULLY!")
