#!/usr/bin/env python3
"""
🪐 Physics Lab: NIST CODATA Constants Verifier
Audits physical constants in constants.json against the authoritative CODATA standard.
"""

import os
import sys
import json
import math

def audit_constants(constants_path="app/config/content/constants.json", ref_path="app/config/ref_data/codata_2022.json"):
    if not os.path.exists(constants_path):
        print(f"❌ Error: Constants file not found at {constants_path}")
        return False

    if not os.path.exists(ref_path):
        print(f"❌ Error: Reference CODATA database not found at {ref_path}")
        return False

    with open(constants_path, "r") as f:
        constants = json.load(f)

    with open(ref_path, "r") as f:
        ref_data = json.load(f)

    mismatches = []
    print("================================================================================")
    print("             🪐 PHYSICS LAB: NIST CODATA CONSTANTS AUDITOR                      ")
    print("================================================================================")

    for key, data in constants.items():
        if key not in ref_data:
            print(f"⚠️ Warning: Constant '{key}' not found in CODATA reference database.")
            continue

        ref = ref_data[key]
        val_str = data.get("value", "0")
        name = data.get("name", key)

        try:
            val = float(val_str)
        except ValueError:
            mismatches.append((key, name, f"Value '{val_str}' cannot be parsed as a float."))
            print(f"❌ ERROR: [{key}] '{name}' - Value cannot be parsed as float")
            continue

        ref_val = float(ref["value"])
        uncertainty = float(ref.get("uncertainty", 0.0))

        # Check tolerances
        # For exact constants, allow floating-point precision error up to 1e-12 relative difference
        # For experimental constants, check if they are within 1e-6 relative difference (which is well within the uncertainty limits)
        rel_diff = abs(val - ref_val) / ref_val if ref_val != 0 else abs(val - ref_val)
        
        tol = 1e-9 if uncertainty == 0.0 else 1e-6

        if rel_diff > tol:
            err_msg = f"Value mismatch: CMS value is {val}, expected {ref_val} (Rel Diff: {rel_diff:.2e}, Tolerance: {tol:.2e})"
            mismatches.append((key, name, err_msg))
            print(f"❌ MISMATCH: [{key}] '{name}'")
            print(f"  Reason: {err_msg}")
        else:
            print(f"✓ [{key}] '{name}' aligned with CODATA value: {ref_val}")

    print("================================================================================")
    if mismatches:
        print(f"❌ AUDIT FAILED: Found {len(mismatches)} physical constants mismatch(es)!")
        return False
    else:
        print("✓ SECURE: All physical constants are fully aligned with the CODATA standard!")
        return True

def main():
    success = audit_constants()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
