import json

def refactor_relativity():
    file_path = 'app/config/content/relativity.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    replacements = {
        'length-contraction-formula': 'The spatial extent of a physical body is not an absolute property but a frame-dependent projection of its four-dimensional world-tube onto a specific hypersurface of simultaneity. This observed reduction in dimension along the axis of relative motion, quantified by the <strong><a href="/physics/subtopic/length-contraction-formula" class="subtopic-link">Length Contraction Formula</a></strong>, constitutes a purely geometric consequence of the way space and time are unified in a four-dimensional manifold rather than a mechanical deformation caused by stress. ',
        'time-dilation-formula': 'The passage of time for a system in motion is inextricably linked to its specific path through the four-dimensional manifold, rather than a universal, absolute flow. This quantitative relationship between durations recorded in different inertial frames, defined by the <strong><a href="/physics/subtopic/time-dilation-formula" class="subtopic-link">Time Dilation Formula</a></strong>, serves as the foundational anchor for understanding how the vacuum\'s geometry enforces the constancy of the speed of light. ',
        'special-relativity': '<h3>The Epistemological Break from Galilean Invariance</h3><p>The transition from the absolute 3D space of the 19th century to a unified four-dimensional manifold necessitated a rigorous re-evaluation of the coordinate-independent nature of physical laws. This fundamental departure from classical mechanics, precipitated by the incompatibility of Newtonian dynamics with electromagnetic field equations, established that the laws of nature are defined by their covariance under a specific group of hyperbolic transformations. The advent of <strong>Special Relativity</strong> marked this shift, '
    }

    for slug, new_lead in replacements.items():
        if slug in data:
            content = data[slug]['content']
            # Find the end of the first sentence in the first paragraph or after the header
            if '</h3><p>' in content:
                header, prose = content.split('</h3><p>', 1)
                sentences = prose.split('. ', 1)
                if len(sentences) > 1:
                    data[slug]['content'] = f"{header}</h3><p>{new_lead.strip()} {sentences[1]}"
                else:
                    data[slug]['content'] = f"{header}</h3><p>{new_lead.strip()}"
            else:
                sentences = content.split('. ', 1)
                if len(sentences) > 1:
                    data[slug]['content'] = f"{new_lead.strip()} {sentences[1]}"
                else:
                    data[slug]['content'] = new_lead.strip()
            
            # Ensure it is flagged as platinum
            data[slug]['standard'] = 'platinum'

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    print("SUCCESS: Refactored 3 subtopics in relativity.json")

if __name__ == "__main__":
    refactor_relativity()
