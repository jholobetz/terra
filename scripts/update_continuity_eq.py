import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shard_b3_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/b3/shard_b3.json")

with open(shard_b3_path, "r", encoding="utf-8") as f:
    data_b3 = json.load(f)

fmt = data_b3["continuity-equation"]
fmt["title"] = "Continuity Equation"
fmt["equation"] = "\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0"
fmt["description"] = "States that the rate of change of a conserved quantity within a volume equals the net flux into or out of that volume."
fmt["conceptual_definition"] = "The continuity equation expresses the fundamental local conservation law for a field quantity (such as mass, charge, or energy). It asserts that the temporal accumulation rate of density $\\rho$ plus the spatial divergence of flux density $\\rho \\mathbf{u}$ equals zero."
fmt["interpretation"] = "The continuity equation, $\\frac{\\partial \\rho}{\\partial t} + \\nabla \\cdot (\\rho \\mathbf{u}) = 0$, balances local density accumulation against net flux divergence. The term $\\frac{\\partial \\rho}{\\partial t}$ is the local rate of change of density $\\rho$ over time $t$. The term $\\nabla \\cdot (\\rho \\mathbf{u})$ is the divergence of flux density $\\rho \\mathbf{u}$ where $\\mathbf{u}$ is velocity. If density is increasing ($\\frac{\\partial \\rho}{\\partial t} > 0$), flux divergence must be negative ($\\nabla \\cdot (\\rho \\mathbf{u}) < 0$), indicating net inflow. Conversely, if density is decreasing ($\\frac{\\partial \\rho}{\\partial t} < 0$), flux divergence is positive ($\\nabla \\cdot (\\rho \\mathbf{u}) > 0$), indicating net outflow. For incompressible flow ($\\rho = \\text{constant}$), it simplifies to $\\nabla \\cdot \\mathbf{u} = 0$."
fmt["symmetry_origin"] = "Derived from fundamental conservation principles (mass/charge conservation) via Gauss's divergence theorem applied to an arbitrary control volume."
fmt["limits_and_boundary"] = "1. **Static Equilibrium ($\\mathbf{u} = 0$)**: Simplifies to $\\frac{\\partial \\rho}{\\partial t} = 0$, meaning density is time-invariant.\n2. **Incompressible Flow ($\\rho = \\text{constant}$)**: Simplifies to solenoidality of velocity field $\\nabla \\cdot \\mathbf{u} = 0$.\n3. **Steady-State Flow ($\\frac{\\partial \\rho}{\\partial t} = 0$)**: Simplifies to divergence-free flux $\\nabla \\cdot (\\rho \\mathbf{u}) = 0$."

with open(shard_b3_path, "w", encoding="utf-8") as f:
    json.dump(data_b3, f, indent=4, ensure_ascii=False)

print("CONTINUITY-EQUATION IN SHARD_B3 UPDATED SUCCESSFULLY!")
