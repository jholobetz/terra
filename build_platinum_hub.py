import json
import os
import re

class HubBuilder:
    def __init__(self, topic_slug, content_dir="app/config/content"):
        self.topic_slug = topic_slug
        self.content_dir = content_dir
        self.topic_path = os.path.join(content_dir, "topics", f"{topic_slug}.json")
        self.shard_path = os.path.join(content_dir, f"{topic_slug}.json")
        
        with open(self.shard_path, "r") as f:
            self.shard_data = json.load(f)
            
        with open(self.topic_path, "r") as f:
            self.topic_data = json.load(f)

    def get_safe_snippet(self, content):
        # 1. Standardize delimiters to single-backslash in memory
        content = content.replace('\\\\(', '\\(').replace('\\\\)', '\\)')
        content = content.replace('\\\\\\[', '\\[').replace('\\\\\\]', '\\]')
        
        # 2. Protection: Replace with unique tokens
        content = content.replace('\\(', '___MJ_INLINE_OPEN___').replace('\\)', '___MJ_INLINE_CLOSE___')
        content = content.replace('\\[', '___MJ_DISPLAY_OPEN___').replace('\\]', '___MJ_DISPLAY_CLOSE___')
        
        # 3. Strip HTML
        clean = re.sub(r'<.*?>', '', content)
        
        # 4. Strip Numbered Headers
        clean = re.sub(r'\d+\.\s+[A-Z].*', '', clean)
        
        # 5. Collapse whitespace
        clean = " ".join(clean.split())
        
        # 6. Extract 3 sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean)
        snippet = " ".join(sentences[:3])
        if len(sentences) > 3:
            snippet += "."
            
        # 7. Restore delimiters
        snippet = snippet.replace('___MJ_INLINE_OPEN___', '\\(').replace('___MJ_INLINE_CLOSE___', '\\)')
        snippet = snippet.replace('___MJ_DISPLAY_OPEN___', '\\[').replace('___MJ_DISPLAY_CLOSE___', '\\]')
        
        return snippet

    def build_hub(self, title, metadata, pillars):
        html = f"<p>{metadata['intro']}</p>\n\n"
        html += '<div class="high-signal-banner">\n'
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
                if slug not in self.shard_data: continue
                sub = self.shard_data[slug]
                
                # Check for Frontier terms
                frontier_terms = ["manifold", "topology", "tensor", "bundle", "chaos", "nonlinear", "covariant", "lie", "symplectic", "geodesic", "action"]
                is_frontier = any(t in sub['title'].lower() or t in slug for t in frontier_terms)
                is_foundational = any(t in sub['title'].lower() or t in slug for t in ["newton", "law", "galileo", "static", "force", "energy", "work"])
                level = "Frontier" if is_frontier else ("Foundational" if is_foundational else "Analytical")
                
                snippet = self.get_safe_snippet(sub['content'])
                clean_title = sub['title'].replace('\\\\', '\\')
                
                html += f'        <div class="concept-card">\n'
                html += f'            <div class="concept-anchor">\n'
                html += f'                <span class="level-tag level-{level.lower()}">{level}</span>\n'
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
        print(f"SUCCESS: Platinum Hub built for {self.topic_slug}")

if __name__ == "__main__":
    builder = HubBuilder("classical-mechanics")
    metadata = {
        "field": "Classical Mechanics", "density": "210",
        "intro": "Classical mechanics represents the foundational mathematical edifice of the physical sciences, providing a deterministic framework for describing the evolution of macroscopic systems through the 4D manifold of spacetime. This university-level exposition utilizes the abstract visual manifold as a guide to the underlying symplectic geometry, revealing the hidden symmetries that anchor the physical world in a balance of conserved quantities and invariant laws.",
        "bridges": {
            "Quantum Physics": "Classical mechanics serves as the high-energy, macroscopic limit of quantum mechanics, where the Hamilton-Jacobi equation provides the phase-evolution map.",
            "Relativity": "Newtonian dynamics is the low-velocity approximation of relativity, where Galilean transformations are replaced by the Lorentz group.",
            "Thermodynamics": "The total dynamics of multi-particle systems lead to thermodynamic laws through the ensemble averaging of phase-space states."
        }
    }
    pillars = [
        {"title": "1. Newtonian Foundation", "narrative": "The Newtonian framework establishes the causal structure of the universe by postulating inertial frames where the affine connection vanishes.", "slugs": ["newtons-first-law", "newtons-second-law", "newtons-third-law", "galileo-galilei-physics", "line-element", "vector-definition", "isaac-newton", "homogeneity-of-space"]},
        {"title": "2. Energetics", "narrative": "Energetics shifts focus to the energy landscape, where motion is viewed as the traversal of a potential manifold.", "slugs": ["work-energy-theorem", "total-mechanical-energy", "rayleigh-dissipation", "power-equation", "conservative-force-field", "potential-energy", "kinetic-energy"]},
        {"title": "3. Rigid Bodies", "narrative": "Extending point-particle models to extended objects introduces the SO(3) rotation group and the inertia tensor.", "slugs": ["rotational-dynamics", "torque", "axial-vector", "special-orthogonal-group-so3", "moment-of-force", "static-equilibrium", "rigid-body", "principal-axes", "angular-momentum-parallelism", "axiom-of-inertia"]},
        {"title": "4. Variational Principles", "narrative": "Analytical mechanics derives laws of motion from the stationary properties of a scalar functional.", "slugs": ["action-principle", "generalized-coordinates", "degrees-of-freedom", "lagrange-multipliers", "virtual-displacement", "principal-function", "action-variable", "action-integral", "stationary-action-principle"]},
        {"title": "5. Many-Body Systems", "narrative": "For systems of interacting particles, identifying conserved quantities reduces complexity.", "slugs": ["conservation-of-linear-momentum", "center-of-mass-frame", "reduced-mass", "tsiolkovsky-rocket-equation", "internal-forces", "external-forces", "reynolds-transport-theorem"]},
        {"title": "6. Manifolds & Tensors", "narrative": "Modern mechanics is expressed via differential geometry, where system states are points on manifolds.", "slugs": ["configuration-space", "topology-mechanics", "tangent-bundle", "cotangent-bundle", "contravariant-covariant-vectors", "tensor-mapping", "index-lowering-operation", "metric-tensor", "geodesics", "geodesic-equation"]},
        {"title": "7. Symmetry & Conservation", "narrative": "Noether's theorem proves that every continuous symmetry corresponds to a conserved charge.", "slugs": ["noethers-theorem", "spatial-translation-symmetry", "time-translation-symmetry", "rotational-symmetry", "generator-of-spatial-translations", "poisson-algebra", "symmetry-of-interactions"]}
    ]
    builder.build_hub("Classical Mechanics", metadata, pillars)
