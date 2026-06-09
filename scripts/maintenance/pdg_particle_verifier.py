#!/usr/bin/env python3
"""
🪐 Physics Lab: PDG Particle Properties Verifier
Audits physical properties in particles.json against the Particle Data Group (PDG) database.
"""

import os
import sys
import json

def audit_particles(particles_path="app/config/content/particles.json", ref_path="app/config/ref_data/pdg_2024.json"):
    if not os.path.exists(particles_path):
        print(f"❌ Error: Particles file not found at {particles_path}")
        return False

    if not os.path.exists(ref_path):
        print(f"❌ Error: Reference PDG database not found at {ref_path}")
        return False

    with open(particles_path, "r") as f:
        particles = json.load(f)

    with open(ref_path, "r") as f:
        ref_data = json.load(f)

    mismatches = []
    print("================================================================================")
    print("             🪐 PHYSICS LAB: PDG PARTICLE PROPERTIES AUDITOR                    ")
    print("================================================================================")

    for key, data in particles.items():
        pdg_id = str(data.get("pdg_id", ""))
        name = data.get("name", key)

        if pdg_id not in ref_data:
            print(f"⚠️ Warning: Particle '{key}' (PDG ID: {pdg_id}) not found in PDG reference database.")
            continue

        ref = ref_data[pdg_id]
        
        # 1. Check Charge
        charge = data.get("charge")
        ref_charge = ref.get("charge")
        if charge != ref_charge:
            err_msg = f"Charge mismatch: CMS value is {charge}, expected {ref_charge}"
            mismatches.append((key, name, err_msg))
            print(f"❌ MISMATCH: [{key}] '{name}' - Charge")
            print(f"  Reason: {err_msg}")
            continue

        # 2. Check Spin
        spin = data.get("spin")
        ref_spin = ref.get("spin")
        if spin != ref_spin:
            err_msg = f"Spin mismatch: CMS value is {spin}, expected {ref_spin}"
            mismatches.append((key, name, err_msg))
            print(f"❌ MISMATCH: [{key}] '{name}' - Spin")
            print(f"  Reason: {err_msg}")
            continue

        # 3. Check Mass (with 1e-6 relative tolerance)
        mass = data.get("mass_mev")
        ref_mass = ref.get("mass_mev")
        rel_diff = abs(mass - ref_mass) / ref_mass if ref_mass != 0 else abs(mass - ref_mass)
        tol = 1e-6

        if rel_diff > tol:
            err_msg = f"Mass mismatch: CMS value is {mass} MeV, expected {ref_mass} MeV (Rel Diff: {rel_diff:.2e}, Tolerance: {tol:.2e})"
            mismatches.append((key, name, err_msg))
            print(f"❌ MISMATCH: [{key}] '{name}' - Mass")
            print(f"  Reason: {err_msg}")
        else:
            print(f"✓ [{key}] '{name}' aligned with PDG ID {pdg_id} (Mass: {ref_mass} MeV, Spin: {ref_spin}, Charge: {ref_charge})")

    print("================================================================================")
    if mismatches:
        print(f"❌ AUDIT FAILED: Found {len(mismatches)} particle properties mismatch(es)!")
        return False
    else:
        print("✓ SECURE: All particle properties are fully aligned with the PDG standard!")
        return True

def main():
    success = audit_particles()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
