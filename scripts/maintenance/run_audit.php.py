from orchestrator import PhysicsOrchestrator
from assembly_line import ExpansionAssemblyLine
import json

def run_comprehensive_audit():
    orch = PhysicsOrchestrator()
    line = ExpansionAssemblyLine()
    
    print("="*40)
    print("PHYSICS LAB: COMPREHENSIVE PLATINUM AUDIT")
    print("="*40)
    
    # 1. Technical Density & Platinum Status
    print("\n[1/3] TECHNICAL DENSITY & PLATINUM STATUS")
    orch.audit()
    line.check_expansion_gate()
    
    # 2. Registry Identity Audit
    print("\n[2/3] REGISTRY IDENTITY AUDIT")
    orch.audit_registry()
    
    # 3. Integrity Shield (Graph Health)
    print("\n[3/3] INTEGRITY SHIELD (GRAPH HEALTH)")
    orch.validate()
    
    print("\n" + "="*40)
    print("AUDIT COMPLETE")
    print("="*40)

if __name__ == "__main__":
    run_comprehensive_audit()
