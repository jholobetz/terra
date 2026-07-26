import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shard_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/b2/shard_b2.json")

with open(shard_path, "r", encoding="utf-8") as f:
    data = json.load(f)

fmt = data["bernoullis-incompressible-flow-constant-ff90fb4b"]
fmt["title"] = "Bernoulli's Incompressible Flow Constant"
fmt["description"] = "States that total mechanical energy per unit volume remains constant along a streamline for steady, inviscid, incompressible fluid flow."
fmt["conceptual_definition"] = "Bernoulli's principle for incompressible flow asserts the conservation of total mechanical energy per unit volume along a fluid streamline. The total pressure—comprising static pressure $P$, dynamic pressure $\\frac{1}{2}\\rho v^2$, and hydrostatic potential pressure $\\rho g h$—remains constant throughout the flow field."
fmt["interpretation"] = "The equation $P + \\frac{1}{2} \\rho v^2 + \\rho g h = \\text{constant}$ balances three forms of mechanical energy per unit volume along a streamline. The term $P$ is static pressure, representing thermodynamic pressure. The term $\\frac{1}{2}\\rho v^2$ is dynamic pressure, representing kinetic energy density where $\\rho$ is fluid density and $v$ is fluid velocity. The term $\\rho g h$ is hydrostatic pressure, representing gravitational potential energy density at elevation $h$ under gravitational acceleration $g$. An increase in fluid velocity $v$ produces a corresponding drop in static pressure $P$ or elevation $h$ to maintain a constant total head."
fmt["symmetry_origin"] = "Derived from Euler's equations of motion for inviscid fluid flow, which express momentum conservation (Newton's second law) combined with energy conservation under time-translation invariance."
fmt["limits_and_boundary"] = "The equation is strictly valid under five fundamental ideal flow assumptions:\n1. **Incompressible Flow**: Constant fluid density ($\\rho = \\text{constant}$).\n2. **Inviscid Flow**: Viscous shear forces and friction are negligible ($\\mu = 0$).\n3. **Steady Flow**: Fluid properties at any spatial point are time-invariant ($\\frac{\\partial \\mathbf{v}}{\\partial t} = 0$).\n4. **Streamline Flow**: Applied along a single streamline (or throughout irrotational flow fields where $\\nabla \\times \\mathbf{v} = 0$).\n5. **No External Work or Heat Exchange**: No pumps, turbines, or heat additions."

with open(shard_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("BERNOULLIS-INCOMPRESSIBLE-FLOW-CONSTANT-FF90FB4B UPDATED SUCCESSFULLY!")
