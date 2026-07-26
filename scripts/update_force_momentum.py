import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shard_da_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/da/shard_da.json")

with open(shard_da_path, "r", encoding="utf-8") as f:
    data_da = json.load(f)

fmt = data_da["force-as-rate-of-change-of-momentum-cc704f96"]
fmt["title"] = "Force as Rate of Change of Momentum"
fmt["equation"] = "\\mathbf{F} = \\frac{d\\mathbf{p}}{dt}"
fmt["description"] = "Defines net external force as the time rate of change of linear momentum."
fmt["conceptual_definition"] = "Newton's Second Law of Motion establishes that the net force $\\mathbf{F}$ acting on an object is equal to the time rate of change of its linear momentum $\\mathbf{p}$."
fmt["interpretation"] = "This vector formulation, $\\mathbf{F} = \\frac{d\\mathbf{p}}{dt}$, is the fundamental statement of dynamics in momentum form. It applies to both constant-mass systems and variable-mass systems (e.g., rocket propulsion). If the net external force $\\mathbf{F}$ is zero, linear momentum $\\mathbf{p}$ is conserved."
fmt["symmetry_origin"] = "Derived from space-translation invariance via Noether's theorem, which dictates that linear momentum is conserved in the absence of net external forces."
fmt["limits_and_boundary"] = "This equation is valid in classical non-relativistic mechanics ($v \\ll c$). For a system with constant mass $m$, it simplifies to $\\mathbf{F} = m \\frac{d\\mathbf{v}}{dt} = m\\mathbf{a}$. At relativistic speeds ($v \\approx c$), momentum generalizes to $\\mathbf{p} = \\gamma m \\mathbf{v}$ where $\\gamma = \\frac{1}{\\sqrt{1 - v^2/c^2}}$."

with open(shard_da_path, "w", encoding="utf-8") as f:
    json.dump(data_da, f, indent=4, ensure_ascii=False)

print("FORCE-AS-RATE-OF-CHANGE-OF-MOMENTUM-CC704F96 UPDATED SUCCESSFULLY!")
