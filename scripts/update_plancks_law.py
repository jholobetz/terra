import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 1. Update plancks-law in shard_f4.json
shard_f4_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/f4/shard_f4.json")
with open(shard_f4_path, "r", encoding="utf-8") as f:
    data_f4 = json.load(f)

fmt_f4 = data_f4["plancks-law"]
fmt_f4["title"] = "Planck's Law for Blackbody Radiation"
fmt_f4["equation"] = "\\rho(\\nu, T) = \\frac{8\\pi h \\nu^3}{c^3} \\frac{1}{e^{\\frac{h\\nu}{k_B T}} - 1}"
fmt_f4["description"] = "Quantifies the spectral energy density of electromagnetic radiation emitted by a black body in thermal equilibrium at temperature T."
fmt_f4["conceptual_definition"] = "Planck's Law describes the spectral energy density $\\rho(\\nu, T)$ of electromagnetic radiation emitted by a black body in thermal equilibrium at absolute temperature $T$. It bridges quantum mechanics and thermodynamics by establishing that electromagnetic energy is emitted in discrete quanta of energy $E = h\\nu$."
fmt_f4["interpretation"] = "Planck's Law, given by $\\rho(\\nu, T) = \\frac{8\\pi h \\nu^3}{c^3} \\frac{1}{e^{\\frac{h\\nu}{k_B T}} - 1}$, quantifies the energy per unit volume per unit frequency interval within a thermal cavity. The term $\\frac{8\\pi \\nu^2}{c^3}$ represents the density of electromagnetic modes per unit volume in three dimensions. The factor $h\\nu$ is the energy per photon of frequency $\\nu$. The factor $\\frac{1}{e^{\\frac{h\\nu}{k_B T}} - 1}$ is the Bose-Einstein distribution function, representing the average occupation number of photons in a mode at temperature $T$, where $\\nu$ is radiation frequency, $T$ is absolute temperature, $h$ is Planck's constant, $k_B$ is the Boltzmann constant, and $c$ is the speed of light."
fmt_f4["symmetry_origin"] = "Derived from Bose-Einstein statistics applied to an ideal gas of indistinguishable photons (spin-1 bosons) in a three-dimensional cavity under spatial isotropy and thermal equilibrium."
fmt_f4["limits_and_boundary"] = "1. **Rayleigh-Jeans Limit (Low Frequency, $h\\nu \\ll k_B T$)**: Expanding the exponential $e^{\\frac{h\\nu}{k_B T}} \\approx 1 + \\frac{h\\nu}{k_B T}$ yields classical Rayleigh-Jeans law $\\rho(\\nu, T) \\approx \\frac{8\\pi k_B T \\nu^2}{c^3}$.\n2. **Wien Limit (High Frequency, $h\\nu \\gg k_B T$)**: The $-1$ in the denominator becomes negligible, yielding Wien's distribution law $\\rho(\\nu, T) \\approx \\frac{8\\pi h \\nu^3}{c^3} e^{-\\frac{h\\nu}{k_B T}}$, resolving the ultraviolet catastrophe.\n3. **Stefan-Boltzmann Law**: Integrating $\\rho(\\nu, T)$ over all frequencies yields total energy density $U = \\int_0^\\infty \\rho(\\nu, T) d\\nu = a T^4$ where $a = \\frac{8\\pi^5 k_B^4}{15 h^3 c^3}$."

with open(shard_f4_path, "w", encoding="utf-8") as f:
    json.dump(data_f4, f, indent=4, ensure_ascii=False)

# 2. Update spectral-energy-density-of-black-body-radiation-plancks-law in shard_62.json
shard_62_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/shard_62.json")
with open(shard_62_path, "r", encoding="utf-8") as f:
    data_62 = json.load(f)

fmt_62 = data_62["spectral-energy-density-of-black-body-radiation-plancks-law"]
fmt_62["title"] = "Spectral Energy Density of Black-Body Radiation (Planck's Law)"
fmt_62["equation"] = "\\rho(\\nu, T) = \\frac{8\\pi h \\nu^3}{c^3} \\frac{1}{e^{\\frac{h\\nu}{k_B T}} - 1}"
fmt_62["description"] = "Quantifies the spectral energy density of electromagnetic radiation emitted by a black body in thermal equilibrium at temperature T."
fmt_62["conceptual_definition"] = fmt_f4["conceptual_definition"]
fmt_62["interpretation"] = fmt_f4["interpretation"]
fmt_62["symmetry_origin"] = fmt_f4["symmetry_origin"]
fmt_62["limits_and_boundary"] = fmt_f4["limits_and_boundary"]

with open(shard_62_path, "w", encoding="utf-8") as f:
    json.dump(data_62, f, indent=4, ensure_ascii=False)

print("PLANCKS-LAW IN SHARD_F4 AND SHARD_62 UPDATED SUCCESSFULLY!")
