import os
from scripts.maintenance.pdg_particle_verifier import audit_particles

def test_particle_properties_alignment():
    """Verify that all particle properties in particles.json are aligned with PDG 2024."""
    assert os.path.exists("app/config/content/particles.json")
    assert os.path.exists("app/config/ref_data/pdg_2024.json")
    assert audit_particles() is True
