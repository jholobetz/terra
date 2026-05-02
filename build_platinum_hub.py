import json
import os
import re

class HubBuilder:
    def __init__(self, topic_slug, content_dir="app/config/content"):
        self.topic_slug = topic_slug
        self.content_dir = content_dir
        self.topic_path = os.path.join(content_dir, "topics", f"{topic_slug}.json")
        self.shard_path = os.path.join(content_dir, f"{topic_slug}.json")
        
        from orchestrator import PhysicsOrchestrator
        self.orch = PhysicsOrchestrator(content_dir=content_dir)
        
        with open(self.shard_path, "r") as f:
            self.shard_data = json.load(f)
            
        with open(self.topic_path, "r") as f:
            self.topic_data = json.load(f)

    def mask_mathjax(self, text):
        placeholders = []
        def replace_mj(match):
            placeholder = f" __MJ_BLOCK_{len(placeholders)}__ "
            placeholders.append(match.group(0))
            return placeholder
        
        # Mask display (using high-count backslashes to catch all variants)
        text = re.sub(r'\\{1,4}\[.*?\\{1,4}\]', replace_mj, text, flags=re.DOTALL)
        # Mask inline
        text = re.sub(r'\\{1,4}\(.*?\\{1,4}\)', replace_mj, text, flags=re.DOTALL)
        return text, placeholders

    def unmask_mathjax(self, text, placeholders):
        for i, val in enumerate(placeholders):
            # Clean the value to ensure it has standard single-backslash delimiters in memory
            # So that json.dump will make it double-backslash in the file.
            clean_val = val.strip()
            # Convert \\( to \( if needed (Python memory standard)
            if clean_val.startswith('\\\\('): clean_val = clean_val.replace('\\\\(', '\\(')
            if clean_val.endswith('\\\\)'): clean_val = clean_val.replace('\\\\)', '\\)')
            
            text = text.replace(f"__MJ_BLOCK_{i}__", clean_val)
        return text

    def get_level(self, slug):
        foundational_terms = ["newton", "law", "galileo", "vector", "static", "force", "energy", "work", "torque"]
        frontier_terms = ["manifold", "topology", "tensor", "bundle", "chaos", "nonlinear", "covariant", "lie", "symplectic", "geodesic", "action"]
        
        title = self.shard_data.get(slug, {}).get("title", "").lower()
        if any(term in title or term in slug for term in frontier_terms):
            return "Frontier"
        if any(term in title or term in slug for term in foundational_terms):
            return "Foundational"
        return "Analytical"

    def get_safe_snippet(self, content):
        # 1. Mask MathJax
        masked, placeholders = self.mask_mathjax(content)
        
        # 2. Strip HTML tags
        clean = re.sub(r'<.*?>', '', masked)
        
        # 3. Remove numbered headers (e.g. 1. History)
        clean = re.sub(r'\n\s*\d+\.\s+.*', '', clean)
        
        # 4. Collapse whitespace
        clean = " ".join(clean.split())
        
        # 5. Split sentences safely
        sentences = clean.split(". ")
        snippet_masked = ". ".join(sentences[:3])
        if len(sentences) > 3:
            snippet_masked += "."
        
        # 6. Unmask
        final_snippet = self.unmask_mathjax(snippet_masked, placeholders)
        
        # 7. Final Sanity: If display math survived into snippet, hide it (too big for cards)
        final_snippet = re.sub(r'\\{1,4}\[.*?\\{1,4}\]', '', final_snippet)
        
        return final_snippet

    def build_hub(self, title, metadata, pillars):
        html = f"<p>{metadata['intro']}</p>\n\n"
        html += f'<div class="high-signal-banner">\n'
        html += f'    <div class="signal-item"><strong>Field:</strong> {metadata["field"]}</div>\n'
        html += f'    <div class="signal-item"><strong>Standard:</strong> Platinum</div>\n'
        html += f'    <div class="signal-item"><strong>Technical Density:</strong> {metadata["density"]}</div>\n'
        html += f'    <div class="signal-item"><strong>Bridges:</strong> {len(metadata["bridges"])}</div>\n'
        html += '</div>\n'

        for pillar in pillars:
            html += f'\n<section class="concept-pillar">\n'
            html += f'    <h3 class="pillar-header">{pillar["title"]}</h3>\n'
            html += f'    <p class="pillar-narrative">{pillar["narrative"]}</p>\n'
            html += '    <div class="concept-grid">\n'
            
            for slug in pillar['slugs']:
                if slug not in self.shard_data:
                    continue
                    
                sub = self.shard_data[slug]
                level = self.get_level(slug)
                level_class = f"level-{level.lower()}"
                
                # Fix title mathjax if present (ensure single backslash in memory)
                clean_title = sub["title"].replace('\\\\(', '\\(').replace('\\\\)', '\\)')
                
                snippet = self.get_safe_snippet(sub['content'])
                
                html += f'        <div class="concept-card">\n'
                html += f'            <div class="concept-anchor">\n'
                html += f'                <span class="level-tag {level_class}">{level}</span>\n'
                html += f'                <h4><strong><a href="/physics/subtopic/{slug}" class="subtopic-link">{clean_title}</a></strong></h4>\n'
                html += '            </div>\n'
                html += '            <div class="concept-detail">\n'
                html += f'                <p>{snippet}</p>\n'
                html += '            </div>\n'
                html += '        </div>\n'
            
            html += '    </div>\n</section>\n'

        # Bridge Matrix
        html += '\n<div class="bridge-matrix">\n    <h3>Cross-Disciplinary Bridges</h3>\n'
        for field, bridge in metadata['bridges'].items():
            html += f'    <div class="bridge-item">\n        <strong>{field}:</strong>\n        <p>{bridge}</p>\n    </div>\n'
        html += '</div>'

        self.topic_data["content"] = html
        with open(self.topic_path, "w") as f:
            json.dump(self.topic_data, f, indent=4)
        print(f"SUCCESS: Platinum Hub repaired with Robust MathJax logic for {self.topic_slug}")

if __name__ == "__main__":
    builder = HubBuilder("classical-mechanics")
    
    metadata = {
        "field": "Classical Mechanics",
        "density": "210",
        "intro": "Classical mechanics represents the foundational mathematical edifice of the physical sciences, providing a deterministic framework for describing the evolution of macroscopic systems through the 4D manifold of spacetime. This university-level exposition utilizes the abstract visual manifold as a guide to the underlying symplectic geometry, revealing the hidden symmetries that anchor the physical world in a balance of conserved quantities and invariant laws.",
        "bridges": {
            "Quantum Physics": "Classical mechanics serves as the high-energy, macroscopic limit of quantum mechanics, where the Hamilton-Jacobi equation provides the phase-evolution map that anticipates wave dynamics.",
            "Relativity": "Newtonian dynamics is the low-velocity approximation of relativity, where Galilean transformations are replaced by the Lorentz group to account for the finiteness of light speed.",
            "Thermodynamics": "The total dynamics of multi-particle systems lead to thermodynamic laws through the ensemble averaging of phase-space states."
        }
    }
    
    pillars = [
        {
            "title": "1. Newtonian Foundation & Spacetime Geometry",
            "narrative": "The Newtonian framework establishes the causal structure of the universe by postulating inertial frames where the affine connection vanishes and the metric remains locally flat. It characterizes force as the generator of momentum flux, providing a deterministic map linking space geometry to the temporal evolution of matter.",
            "slugs": ["newtons-first-law", "newtons-second-law", "newtons-third-law", "galileo-galilei-physics", "line-element", "vector-definition", "isaac-newton", "homogeneity-of-space"]
        },
        {
            "title": "2. Energetics & Conservative Fields",
            "narrative": "Energetics shifts focus to the energy landscape, where motion is viewed as the traversal of a potential manifold. Total mechanical energy acts as a global invariant, allowing the resolution of complex dynamics without explicit recourse to infinitesimal forces at every point.",
            "slugs": ["work-energy-theorem", "total-mechanical-energy", "rayleigh-dissipation", "power-equation"]
        },
        {
            "title": "3. Rigid Bodies & Rotational Dynamics",
            "narrative": "Extending point-particle models to extended objects introduces the SO(3) rotation group and the inertia tensor. Diagonalizing this tensor reveals principal axes—orientations where angular momentum and velocity vectors achieve parallelism, decoupling the Euler equations.",
            "slugs": ["rotational-dynamics", "torque", "axial-vector", "special-orthogonal-group-so3", "moment-of-force", "static-equilibrium", "rigid-body"]
        },
        {
            "title": "4. Variational Principles",
            "narrative": "Analytical mechanics derives laws of motion from the stationary properties of a scalar functional. The Principle of Least Action unifies all dynamics, asserting that nature follows paths that make the action integral stationary under small variations.",
            "slugs": ["action-principle", "generalized-coordinates", "degrees-of-freedom", "lagrange-multipliers", "virtual-displacement"]
        },
        {
            "title": "5. Many-Body Systems & Conservation",
            "narrative": "For systems of interacting particles, identifying conserved quantities reduces complexity. The conservation of linear momentum and the analysis of the center-of-mass frame provide the essential constraints for resolving multi-particle collisions and orbits.",
            "slugs": ["conservation-of-linear-momentum", "center-of-mass-frame", "reduced-mass", "tsiolkovsky-rocket-equation", "internal-forces", "external-forces"]
        },
        {
            "title": "6. Mathematical Foundations: Manifolds & Tensors",
            "narrative": "Modern mechanics is expressed via differential geometry, where system states are points on differentiable manifolds. Tensors ensure laws remain objective under coordinate shifts, providing the language for describing 4D subatomic bits and cosmic expansion.",
            "slugs": ["configuration-space", "topology-mechanics", "tangent-bundle", "cotangent-bundle", "contravariant-covariant-vectors", "tensor-mapping", "index-lowering-operation"]
        },
        {
            "title": "7. Symmetry & Noetherian Charges",
            "narrative": "Noether's theorem proves that every continuous symmetry corresponds to a conserved charge. Symmetries of space and time dictate the possible interactions of matter, anchoring laws in geometric invariance.",
            "slugs": ["noethers-theorem", "spatial-translation-symmetry", "time-translation-symmetry", "rotational-symmetry", "generator-of-spatial-translations"]
        }
    ]
    
    builder.build_hub("Classical Mechanics", metadata, pillars)
