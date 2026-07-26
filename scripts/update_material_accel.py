import json
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
shard_path = os.path.join(PROJECT_ROOT, "app/config/content/formulas/03/shard_03.json")

with open(shard_path, "r", encoding="utf-8") as f:
    data = json.load(f)

fmt = data["material-acceleration-of-fluid-element-d7327a65"]
fmt["title"] = "Material Acceleration of Fluid Element"
fmt["description"] = "Quantifies the total Lagrangian acceleration experienced by an infinitesimal fluid parcel, combining local temporal acceleration and spatial convective acceleration."
fmt["conceptual_definition"] = "The material acceleration represents the total rate of change of fluid velocity $\\mathbf{v}$ for a moving fluid element in an Eulerian reference frame. Denoted by the material derivative $\\frac{D\\mathbf{v}}{Dt} = \\frac{\\partial \\mathbf{v}}{\\partial t} + (\\mathbf{v} \\cdot \\nabla)\\mathbf{v}$, it captures both the local time variation of the velocity field at a fixed spatial point and the advective change as the fluid parcel moves into regions of differing velocity."
fmt["interpretation"] = "The expression $\\frac{\\partial \\mathbf{v}}{\\partial t} + (\\mathbf{v} \\cdot \\nabla)\\mathbf{v}$ calculates the total acceleration of a fluid parcel. The first term $\\frac{\\partial \\mathbf{v}}{\\partial t}$ is the local acceleration, which measures how the velocity vector $\\mathbf{v}(\\mathbf{r}, t)$ changes with time $t$ at a fixed spatial coordinate $\\mathbf{r}$. The second term $(\\mathbf{v} \\cdot \\nabla)\\mathbf{v}$ is the convective (advective) acceleration, which accounts for the acceleration a fluid parcel experiences due to its spatial displacement through a non-uniform velocity field. Together, they form the non-linear acceleration term $\\frac{D\\mathbf{v}}{Dt}$ on the left-hand side of the Navier-Stokes and Euler equations."
fmt["symmetry_origin"] = "Derived via the multivariable chain rule for the material derivative $\\frac{D}{Dt} = \\frac{\\partial}{\\partial t} + \\mathbf{v} \\cdot \\nabla$ applied to the velocity field $\\mathbf{v}(\\mathbf{r}(t), t)$. It expresses Galilean invariance, ensuring fluid acceleration transforms consistently between inertial reference frames."
fmt["limits_and_boundary"] = "For steady flows ($\\frac{\\partial \\mathbf{v}}{\\partial t} = 0$), material acceleration reduces entirely to the convective term $(\\mathbf{v} \\cdot \\nabla)\\mathbf{v}$. For spatially uniform flows ($\\nabla \\mathbf{v} = 0$), convective acceleration vanishes, leaving only local acceleration $\\frac{\\partial \\mathbf{v}}{\\partial t}$. At solid boundaries satisfying the no-slip condition ($\\mathbf{v} = 0$), convective acceleration vanishes at the wall."

with open(shard_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("MATERIAL-ACCELERATION-OF-FLUID-ELEMENT-D7327A65 UPDATED SUCCESSFULLY!")
