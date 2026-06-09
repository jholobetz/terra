import os
from scripts.maintenance.nist_constants_verifier import audit_constants

def test_physical_constants_alignment():
    """Verify that all physical constants in constants.json are aligned with CODATA 2022."""
    assert os.path.exists("app/config/content/constants.json")
    assert os.path.exists("app/config/ref_data/codata_2022.json")
    assert audit_constants() is True
