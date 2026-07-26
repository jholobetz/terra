import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(PROJECT_ROOT, "scripts"))
from terra_lexer import TerraLexer

shard_6d_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/6d/shard_6d.json")

with open(shard_6d_path, "r", encoding="utf-8") as f:
    data_6d = json.load(f)

# Find key for Saha equation in shard_6d.json
target_key = None
for key, formula in data_6d.items():
    if isinstance(formula, dict) and "\\frac{X_i}{X_j}" in formula.get("equation", ""):
        target_key = key
        break

if target_key:
    fmt = data_6d[target_key]
    fmt["title"] = "Nuclear Abundance Ratio (Saha Equation)"
    fmt["equation"] = "\\frac{X_i}{X_j} = \\frac{\\omega_i}{\\omega_j} \\left( \\frac{A_i}{A_j} \\right)^{3/2} \\exp\\left( \\frac{B_i - B_j}{k_B T} \\right)"
    fmt["description"] = "Relates the equilibrium relative abundances of nuclear species to statistical weights, atomic masses, binding energies, and temperature."
    fmt["conceptual_definition"] = "The Saha abundance ratio formula quantifies the equilibrium relative number density $\\frac{X_i}{X_j}$ between two nuclear species $i$ and $j$ in thermal equilibrium at temperature $T$."
    fmt["interpretation"] = "The left side, $\\frac{X_i}{X_j}$, is the relative abundance ratio of species $i$ to species $j$. The ground-state degeneracy ratio $\\frac{\\omega_i}{\\omega_j}$ reflects statistical state availability. The translational partition factor $\\left(\\frac{A_i}{A_j}\\right)^{3/2}$ accounts for mass differences between species with atomic masses $A_i$ and $A_j$. The Boltzmann factor $\\exp\\left(\\frac{B_i - B_j}{k_B T}\\right)$ governs thermal state populations based on nuclear binding energies $B_i$ and $B_j$, Boltzmann constant $k_B$, and absolute temperature $T$."
    fmt["symmetry_origin"] = "Derived from grand canonical ensemble statistical mechanics for ideal gases under nuclear reaction thermal equilibrium."
    fmt["limits_and_boundary"] = "1. **High Temperature Limit ($T \\to \\infty$)**: The Boltzmann factor approaches $\\exp(0) = 1$, reducing the abundance ratio to $\\frac{X_i}{X_j} \\approx \\frac{\\omega_i}{\\omega_j} \\left( \\frac{A_i}{A_j} \\right)^{3/2}$.\n2. **Low Temperature Limit ($T \\to 0$)**: The species with higher binding energy ($B_i > B_j$) dominates exponentially.\n3. **Equal Binding Energy ($B_i = B_j$)**: The exponential factor equals 1, yielding $\\frac{X_i}{X_j} = \\frac{\\omega_i}{\\omega_j} \\left( \\frac{A_i}{A_j} \\right)^{3/2}$."

    # Run TerraLexer normalization over all records in shard_6d.json
    lexer = TerraLexer()
    for f_id, f_record in data_6d.items():
        lexer.normalize_formula(f_record)

    with open(shard_6d_path, "w", encoding="utf-8") as f:
        json.dump(data_6d, f, indent=4, ensure_ascii=False)

    print(f"UPDATED KEY {target_key} IN SHARD_6D SUCCESSFULLY!")
else:
    print("TARGET KEY NOT FOUND IN SHARD_6D")
