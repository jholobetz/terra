# Sub-equation Composition Architecture

This document details the architectural design, database schema, REST API contracts, and front-end rendering specifications for the **Sub-equation Composition Architecture** in the Physics Lab Digital Encyclopedia.

---

## 1. Executive Summary & Design Rationale

In theoretical physics, complex master equations are almost never monolithic; they are **modular composites built from distinct physical mechanisms**. 

Prior to this architecture, subcomponents in equation explainer tools were often treated as isolated single symbols (e.g. $m$, $e$, or $\frac{1}{2}$). This duplicated the variable breakdown list and failed to convey how composite physical laws are structured.

The **Sub-equation Composition Architecture** establishes a clear separation of concerns:
- **Left Panel (Base Variables & Constants)**: Explains atomic symbols ($m$, $e$, $\hbar$, $\epsilon_0$, $\mathbf{r}_i$).
- **Right Panel (Formula Family Tree & Sub-equations)**: Maps the **structural mathematical terms** and sub-equations ($\sum \frac{\hat{p}_i^2}{2m}$, $\nabla \times \mathbf{B}$, $\mu_0 \mathbf{J}$).

---

## 2. Core Physics Domain Mapping

The table below illustrates how major composite laws break down into canonical sub-equation components:

| Physics Domain | Master Equation | Sub-equation Components |
| :--- | :--- | :--- |
| **Quantum & Solid-State** | Many-Body Electronic Hamiltonian ($\hat{H}$) | • Electronic Kinetic Energy ($\sum \frac{\hat{p}_i^2}{2m}$)<br>• Electron-Nucleus Potential ($\sum V(\mathbf{r}_i - \mathbf{R}_I)$)<br>• Pairwise Coulomb Repulsion ($\frac{1}{2}\sum \frac{e^2}{4\pi\epsilon_0 r_{ij}}$) |
| **Electrodynamics** | Ampère-Maxwell Law ($\nabla \times \mathbf{B} = \mu_0 \mathbf{J} + \mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}$) | • Conduction Current Density ($\mu_0 \mathbf{J}$)<br>• Displacement Current Density ($\mu_0 \epsilon_0 \frac{\partial \mathbf{E}}{\partial t}$) |
| **Fluid Dynamics** | Navier-Stokes Equation ($\rho (\frac{\partial \mathbf{u}}{\partial t} + \mathbf{u} \cdot \nabla \mathbf{u}) = -\nabla p + \mu \nabla^2 \mathbf{u} + \mathbf{f}$) | • Unsteady Acceleration ($\rho \frac{\partial \mathbf{u}}{\partial t}$)<br>• Convective Advection ($\rho (\mathbf{u} \cdot \nabla \mathbf{u})$)<br>• Pressure Gradient ($-\nabla p$)<br>• Viscous Diffusion ($\mu \nabla^2 \mathbf{u}$) |
| **Relativity & Cosmology** | Einstein Field Equations ($G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}$) | • Einstein Spacetime Curvature ($G_{\mu\nu}$)<br>• Cosmological Constant Term ($\Lambda g_{\mu\nu}$)<br>• Stress-Energy-Momentum Source ($\frac{8\pi G}{c^4} T_{\mu\nu}$) |
| **Quantum Field Theory** | Dirac Lagrangian ($\mathcal{L} = \bar{\psi}(i\gamma^\mu \partial_\mu - m)\psi$) | • Kinetic/Gauge Coupling Term ($i\bar{\psi}\gamma^\mu \partial_\mu \psi$)<br>• Rest-Mass Energy Term ($-m\bar{\psi}\psi$) |

---

## 3. Database Schema & Data Modeling

### 3.1 JSON Shards (`app/config/content/formulas/{prefix}/shard_{prefix}.json`)
Formula objects store hierarchy relationships via two primary attributes:
- `parent_formula_id` (`string`): The canonical ID of the master law (if this formula is a sub-equation).
- `subcomponents` (`array` of `string`): Canonical IDs of child subcomponent equations (if this formula is a master equation).

#### Master Equation Example (`many-body-electronic-hamiltonian`):
```json
{
  "id": "many-body-electronic-hamiltonian",
  "title": "Many-Body Electronic Hamiltonian",
  "equation": "\\hat{H} = \\sum_{i} \\frac{\\hat{p}_i^2}{2m} + \\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I) + \\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{r}_j|}",
  "subcomponents": [
    "electronic-kinetic-energy-summation-ba6e4290",
    "electron-nucleus-potential-energy-summation-3a60342d",
    "pairwise-electron-ion-coulomb-like-interaction-from-hamiltonian-8a553347"
  ]
}
```

#### Child Sub-equation Example (`electronic-kinetic-energy-summation-ba6e4290`):
```json
{
  "id": "electronic-kinetic-energy-summation-ba6e4290",
  "title": "Electronic Kinetic Energy Summation",
  "equation": "\\sum_{i} \\frac{\\hat{p}_i^2}{2m}",
  "parent_formula_id": "many-body-electronic-hamiltonian",
  "derivation_type": "DERIVED_FROM",
  "conceptual_definition": "This subequation represents the total quantum kinetic energy operator of all electrons in a multi-particle system."
}
```

### 3.2 MariaDB Relational Table (`formulas`)
The `formulas` table in MariaDB is provisioned with JSON columns for subcomponents and parent links:

```sql
CREATE TABLE IF NOT EXISTS formulas (
    id VARCHAR(255) PRIMARY KEY,
    parent_formula_id VARCHAR(255),
    derivation_type VARCHAR(50),
    constraints JSON,
    related_formula_ids JSON,
    subcomponents JSON,
    title VARCHAR(255) NOT NULL,
    equation MEDIUMTEXT NOT NULL,
    equation_svg MEDIUMTEXT,
    conceptual_definition TEXT,
    intuitive_summary TEXT,
    interpretation TEXT,
    symmetry_origin TEXT,
    limits_and_boundary TEXT,
    semantic_variables JSON,
    unit_system VARCHAR(50) DEFAULT 'SI',
    status VARCHAR(50) DEFAULT 'published'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 4. Backend Hierarchy Resolution & API Contracts

### 4.1 PHP Service Layer (`app/logic/PhysicsService.php`)
`getFormulaWithHierarchy(string $fId)` dynamically resolves parent objects and child subcomponent lists:

```php
public function getFormulaWithHierarchy(string $fId): ?array
{
    $formula = $this->loadFormula($fId);
    if (!$formula) return null;

    $formula['id'] = $fId;

    // 1. Resolve Parent Master Equation
    if (!empty($formula['parent_formula_id'])) {
        $parentId = $formula['parent_formula_id'];
        $parentObj = $this->loadFormula($parentId);
        if ($parentObj) {
            $formula['parent_formula'] = [
                'id' => $parentId,
                'title' => $parentObj['title'] ?? 'Parent Formula',
                'equation' => $parentObj['equation'] ?? '',
                'url' => '/physics/equation-explainer?id=' . urlencode($parentId)
            ];
        }
    }

    // 2. Resolve Child Subcomponents Grid
    if (!empty($formula['subcomponents']) && is_array($formula['subcomponents'])) {
        $resolvedChildren = [];
        foreach ($formula['subcomponents'] as $childId) {
            if (is_string($childId)) {
                $childObj = $this->loadFormula($childId);
                if ($childObj) {
                    $resolvedChildren[] = [
                        'id' => $childId,
                        'title' => $childObj['title'] ?? 'Subcomponent Equation',
                        'equation' => $childObj['equation'] ?? '',
                        'url' => '/physics/equation-explainer?id=' . urlencode($childId)
                    ];
                }
            }
        }
        $formula['subcomponents'] = $resolvedChildren;
    }

    return $formula;
}
```

### 4.2 REST API Response (`GET /physics/api/explain?id=...` or `?latex=...`)
```json
{
  "success": true,
  "formula": {
    "id": "many-body-electronic-hamiltonian",
    "title": "Many-Body Electronic Hamiltonian",
    "equation": "\\hat{H} = \\sum_{i} \\frac{\\hat{p}_i^2}{2m} + \\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I) + \\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{r}_j|}",
    "subcomponents": [
      {
        "id": "electronic-kinetic-energy-summation-ba6e4290",
        "title": "Electronic Kinetic Energy Summation",
        "equation": "\\sum_{i} \\frac{\\hat{p}_i^2}{2m}",
        "url": "/physics/equation-explainer?id=electronic-kinetic-energy-summation-ba6e4290"
      },
      {
        "id": "electron-nucleus-potential-energy-summation-3a60342d",
        "title": "Electron-Nucleus Potential Energy Summation",
        "equation": "\\sum_{i, I} V(\\mathbf{r}_i - \\mathbf{R}_I)",
        "url": "/physics/equation-explainer?id=electron-nucleus-potential-energy-summation-3a60342d"
      },
      {
        "id": "pairwise-electron-ion-coulomb-like-interaction-from-hamiltonian-8a553347",
        "title": "Pairwise Electron-Ion Coulomb-like Interaction (from Hamiltonian)",
        "equation": "\\frac{1}{2}\\sum_{i \\neq j} \\frac{e^2}{4\\pi\\epsilon_0 |\\mathbf{r}_i - \\mathbf{R}_I|}",
        "url": "/physics/equation-explainer?id=pairwise-electron-ion-coulomb-like-interaction-from-hamiltonian-8a553347"
      }
    ]
  }
}
```

---

## 5. Front-End Family Tree UI (`public/js/equation_explainer.js`)

`renderKnowledgeGraphCard(formula)` renders both upward parent links and downward sub-equation grids directly below the main conceptual explanation banner:

```javascript
renderKnowledgeGraphCard(formula) {
    const card = document.getElementById('knowledge-graph-card');
    const details = document.getElementById('knowledge-graph-details');
    if (!card || !details) return;

    const hasParent = formula && (formula.parent_formula || formula.parent_formula_id);
    const hasSubcomponents = formula && Array.isArray(formula.subcomponents) && formula.subcomponents.length > 0;

    if (!hasParent && !hasSubcomponents) {
        card.style.display = 'none';
        return;
    }

    card.style.display = 'flex';
    let html = '';

    // 1. Parent Master Equation Link (Upward)
    if (formula.parent_formula && formula.parent_formula.id) {
        const p = formula.parent_formula;
        const parentUrl = p.url || `/physics/equation-explainer?id=${encodeURIComponent(p.id)}`;
        html += `
            <div style="margin-bottom: 14px; background: rgba(100, 255, 218, 0.05); border: 1px solid rgba(100, 255, 218, 0.2); border-radius: 8px; padding: 12px;">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 4px; font-weight: 600;">⬆ Parent Master Equation</div>
                <a href="${parentUrl}" style="color: var(--accent-default, #64ffda); text-decoration: none; font-weight: 600; font-size: 1.05rem; display: inline-flex; align-items: center; gap: 8px;">
                    <span>${p.title}</span>
                    <span style="color: #ffd700; font-family: monospace;">($\\;${p.equation}\\;$)</span>
                </a>
            </div>
        `;
    }

    // 2. Child Subcomponents Grid (Downward)
    if (hasSubcomponents) {
        html += `
            <div style="margin-top: 10px;">
                <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted, #94a3b8); margin-bottom: 8px; font-weight: 600;">⬇ Formula Component Sub-equations (${formula.subcomponents.length})</div>
                <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 10px;">
        `;
        formula.subcomponents.forEach(child => {
            const childId = typeof child === 'string' ? child : child.id;
            const childTitle = typeof child === 'string' ? childId.replace(/-/g, ' ') : child.title;
            const childEq = (typeof child === 'object' && child.equation) ? child.equation : childId;
            const childUrl = `/physics/equation-explainer?id=${encodeURIComponent(childId)}`;
            html += `
                <a href="${childUrl}" style="display: flex; flex-direction: column; gap: 4px; padding: 10px; background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; text-decoration: none; transition: all 0.2s;">
                    <span style="font-size: 0.82rem; color: #f1f5f9; font-weight: 600;">${childTitle}</span>
                    <span style="font-size: 0.9rem; color: #ffd700;">($\\;${childEq}\\;$)</span>
                </a>
            `;
        });
        html += `</div></div>`;
    }

    details.innerHTML = html;
    this.triggerTypeset([details]);
}
```

---

## 6. Automated Pipeline & Zero-Throttle Ingestion

- **Extraction**: `app/config/unindexed_subcomponents.json` indexes 39,725 candidate sub-expressions across 5,625 master equations.
- **Batch Processing**: [`scripts/maintenance/generate_subcomponent_formulas_vertex.py`](file:///Users/holobetj/code/gemini/terra/scripts/maintenance/generate_subcomponent_formulas_vertex.py) runs 25 concurrent async workers via Gemini 2.5 Flash (`google.genai` SDK).
- **Synchronization**: `php cli_sync.php --force` pushes shard updates into the MariaDB database and validates the system with `integrity_shield.py` and `pytest`.
