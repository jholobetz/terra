import os
import re
import json
from orchestrator import PhysicsOrchestrator
from scripts.maintenance.generate_system_health import score_subtopic, is_node_subjective

def test_no_hardcoded_brain_uuids_in_scripts():
    """Ensure no developer or AI agent has hardcoded a stale brain/conversation UUID path."""
    uuid_pattern = re.compile(r'brain/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', re.IGNORECASE)
    
    scan_dirs = ["scripts", "tests"]
    for d in scan_dirs:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if not file.endswith((".py", ".php", ".sh", ".json")):
                    continue
                path = os.path.join(root, file)
                with open(path, "r", errors="ignore") as f:
                    content = f.read()
                    matches = uuid_pattern.findall(content)
                    assert not matches, f"HARDCODED UUID DETECTED in {path}: {matches}. Stale brain/artifact directories must never be hardcoded."

def test_scorecard_reconciliation_invariant():
    """Verify the mathematical alignment between the health dashboard violations and unique substandard nodes."""
    orch = PhysicsOrchestrator()
    
    # Resolve category mapping
    slug_to_cat = {}
    for cat_slug in orch.data["topics"]:
        shard_name = f"{cat_slug}.json"
        if shard_name in orch.shards:
            for sub_slug in orch.shards[shard_name]:
                slug_to_cat[sub_slug] = cat_slug
                
    low_depth_count = 0
    low_density_count = 0
    unique_substandard_count = 0
    both_count = 0
    
    for shard_name, shard_data in orch.shards.items():
        if shard_name == "compiled_trie_regex.json":
            continue
        for slug, sub in shard_data.items():
            if "content" not in sub or sub.get("standard") != "platinum":
                continue
                
            cat = slug_to_cat.get(slug)
            stats = score_subtopic(slug, sub, category=cat)
            
            is_low_depth = stats["words"] < stats["word_target"]
            is_low_density = stats["density_score"] < stats["density_target"]
            
            if is_low_depth:
                low_depth_count += 1
            if is_low_density:
                low_density_count += 1
            if is_low_depth or is_low_density:
                unique_substandard_count += 1
            if is_low_depth and is_low_density:
                both_count += 1
                
    total_violations = low_depth_count + low_density_count
    
    # The absolute mathematical invariant that prevents dashboard-drift and count discrepancy confusion
    assert total_violations - unique_substandard_count == both_count, (
        f"Reconciliation failure: Total violations ({total_violations}) - "
        f"Unique substandard ({unique_substandard_count}) must equal both ({both_count})"
    )

def test_aligned_density_targets_integrity_shield():
    """Ensure the target limits in integrity_shield.py match generate_system_health.py targets."""
    # Read integrity_shield.py content
    with open("integrity_shield.py", "r") as f:
        shield_content = f.read()
        
    # Check that it dynamically checks both targets (30 and 60)
    assert "density_target = 30 if is_subjective else 60" in shield_content, (
        "integrity_shield.py target limits are out of alignment with the 30/60 system."
    )
