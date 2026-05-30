import sys
import json
import os
import shutil
import hashlib
from datetime import datetime

# Add current working directory to path to resolve local imports cleanly
sys.path.append(os.getcwd())

from scripts.maintenance.latex_sanitizer import sanitize_latex

ACTIVE_SPRINT_PATH = 'subfiles/active_expansion_sprint.json'


def merge_formula_ids(new_fids, existing_fids):
    """Return new_fids followed by existing_fids with overlaps removed.

    New IDs keep their positional precedence; a non-list existing_fids is
    treated as empty to defend against malformed shard entries.
    """
    if not isinstance(existing_fids, list):
        existing_fids = []
    return new_fids + [fid for fid in existing_fids if fid not in new_fids]


def register_identities(identities_file, slug, orch):
    """Registers new theoretical identities into the formulas registry and updates the slug's formula_ids."""
    if not identities_file or not os.path.exists(identities_file):
        return []

    with open(identities_file, 'r') as f:
        identities_list = json.load(f)

    if not isinstance(identities_list, list):
        print("Error: identities.json must be a list of objects.")
        sys.exit(1)

    formula_registry = orch.data["formula_registry"]
    registered_ids = []

    for item in identities_list:
        # Generate stable hash-based ID if not already suffixed
        raw_id = item.get('id', 'temp-id')
        equation = item.get('equation', '')
        equation = sanitize_latex(equation)
        
        # Consistent with our Temp scripts: Use first 8 chars of hash
        suffix = hashlib.md5(equation.encode()).hexdigest()[:8]
        fid = f"{raw_id}-{suffix}" if not raw_id.endswith(suffix) else raw_id
        
        # Populate registry entry
        formula_registry[fid] = {
            'title': item.get('title', 'Untitled Identity'),
            'equation': equation,
            'interpretation': item.get('interpretation', 'Analysis pending.'),
            'symmetry_origin': item.get('symmetry_origin', 'Theoretical origin under investigation.'),
            'limits_and_boundary': item.get('limits_and_boundary', 'Boundary conditions pending.'),
            'semantic_variables': item.get('semantic_variables', {}),
            'status': 'platinum'
        }
        registered_ids.append(fid)
        print(f"REGISTERED: {fid}")

    # Update formula_registry on disk via orchestrator later, 
    # but for now, we just need the IDs to update the subtopic.
    return registered_ids

def commit_node(slug, html_file, identities_file=None):
    # 1. Read HTML
    if not os.path.exists(html_file):
        print(f"Error: HTML file {html_file} not found.")
        sys.exit(1)
        
    with open(html_file, 'r') as f:
        html_content = f.read()

    # 2. Get Shard and Orchestrator
    from orchestrator import PhysicsOrchestrator
    orch = PhysicsOrchestrator()
    if slug not in orch.slug_to_shard:
        print(f"Error: Slug {slug} not found in any shard.")
        sys.exit(1)
        
    shard_name = orch.slug_to_shard[slug]
    shard_path = os.path.join("app/config/content", shard_name)
    
    # Backup shard
    shutil.copy(shard_path, shard_path + ".bak")

    # Update JSON
    with open(shard_path, 'r') as f:
        shard_data = json.load(f)
        
    # 2a. Handle Identity Registration if provided
    if identities_file:
        new_fids = register_identities(identities_file, slug, orch)
        if new_fids:
            # Retrieve existing formula IDs safely and combine, preserving uniqueness
            existing_fids = shard_data[slug].get('formula_ids', [])
            combined_fids = merge_formula_ids(new_fids, existing_fids)
            shard_data[slug]['formula_ids'] = combined_fids
            
            # Save formula registry to disk immediately
            orch.save_formula_registry()
            print("Saved updated formula registry to disk.")

    # Generate snippet from first ~30 words of text (stripping HTML)
    import re
    text_only = re.sub(r'<[^>]+>', '', html_content)
    snippet = " ".join(text_only.split()[:30]) + "..."
    
    # 3a. Formula Check (Allows empty lists for conceptual/philosophical subtopics as per CLAUDE.md Organic Formula Integration)
    formula_ids = shard_data[slug].get('formula_ids', [])
    if not isinstance(formula_ids, list):
        shard_data[slug]['formula_ids'] = []
        formula_ids = []
    print(f"INFO: [{slug}] has {len(formula_ids)} registered identities. (Dynamic / Organic Curation)")

    shard_data[slug]['content'] = html_content
    shard_data[slug]['standard'] = 'platinum'
    shard_data[slug]['snippet'] = snippet
    
    with open(shard_path, 'w') as f:
        json.dump(shard_data, f, indent=4)
        
    try:
        # 3. Auto Linker
        from auto_linker import run_auto_linker
        run_auto_linker([shard_path], 'app/config/content/search_index.json')
        
        # 4. SVG Rendering
        orch = PhysicsOrchestrator() # Re-init to pick up linked content and new identities in memory
        
        # 4a. Pre-render associated formulas specifically
        subtopic_data = orch.data["subtopics"].get(slug, {})
        formula_ids = subtopic_data.get("formula_ids", [])
        if formula_ids:
            print(f"Pre-rendering {len(formula_ids)} associated formulas...")
            rendering_queue = {}
            for f_id in formula_ids:
                formula = orch.data["formula_registry"].get(f_id)
                if formula and not formula.get("equation", "").startswith("<svg"):
                    rendering_queue[f"REG_{f_id}_#FFD700"] = {
                        "latex": formula["equation"], 
                        "is_display": True, 
                        "color": "#FFD700"
                    }
            if rendering_queue:
                new_svgs = orch.batch_convert_to_svg(rendering_queue)
                for f_id in formula_ids:
                    cache_key = f"REG_{f_id}_#FFD700"
                    if cache_key in orch.svg_cache:
                        orch.data["formula_registry"][f_id]["equation"] = orch.svg_cache[cache_key]
 
        # Save will now write BOTH the shard and the updated formula registry, whitelisted to target slug
        orch.save(target_slugs=[slug], unlock_protected=True)
        
        # 4b. Rebuild Parent Hub Caches
        parents = orch.data["subtopics"].get(slug, {}).get("parents", [])
        for p in parents:
            if p in orch.data["topics"]:
                print(f"Rebuilding hub cache for: {p}")
                try:
                    orch.build(slug=p)
                except Exception as build_err:
                    print(f"Warning: Could not hit local server to build {p}. Deleting cache file instead.")
                
                cache_file = f"public/cache/topic/{p}.html"
                if os.path.exists(cache_file):
                    os.remove(cache_file)

        # 4c. Targeted MariaDB Sync
        print(f"Injecting {slug} into MariaDB...")
        os.system(f"php scripts/maintenance/sync_node.php {slug}")
        
        # 5. Integrity Shield
        from integrity_shield import IntegrityShield
        shield = IntegrityShield(target_slug=slug)
        
        success = shield.run()
        if not success:
            slug_errors = [e for e in shield.errors if f"[{slug}]" in e]
            if slug_errors:
                print(f"Integrity Shield failed for {slug}:")
                for e in slug_errors:
                    print(e)
                raise Exception("Integrity Shield Validation Failed")
            else:
                print("Integrity Shield failed for other reasons, but ignoring for now or you can handle it.")
                
        # 6. Advance Active Sprint
        if not os.path.exists(ACTIVE_SPRINT_PATH):
            print(f"WARNING: Active sprint file not found at {ACTIVE_SPRINT_PATH}. Skipping sprint advancement.")
        else:
            with open(ACTIVE_SPRINT_PATH, 'r') as f:
                sprint = json.load(f)

            found_in_queue = False
            for item in sprint.get('queue', []):
                if item.get('slug') == slug:
                    item['status'] = 'completed'
                    found_in_queue = True
                    break

            if not found_in_queue:
                sprint.setdefault('ad_hoc_graduations', []).append({
                    'slug': slug,
                    'graduated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                print(f"WARNING: [{slug}] was not in the active sprint queue.")
                print(f"         Recorded as ad-hoc graduation in {ACTIVE_SPRINT_PATH}.")
                print(f"         If scope has shifted, re-initialize the sprint via init_sprint.py.")

            next_slug = next(
                (item['slug'] for item in sprint.get('queue', []) if item.get('status') == 'pending'),
                None
            )
            sprint['active_target'] = next_slug
            sprint['last_updated'] = datetime.now().strftime('%Y-%m-%d')

            with open(ACTIVE_SPRINT_PATH, 'w') as f:
                json.dump(sprint, f, indent=4)
                f.write('\n')

            target_msg = next_slug if next_slug else 'Sprint Complete'
            print(f"Successfully committed {slug}. Next target: {target_msg}")

        # 7. Refresh system health snapshot
        print("Refreshing system_health.json...")
        env_prefix = "PYTHONPATH=. " if not os.environ.get('PYTHONPATH') else ""
        rc = os.system(f"{env_prefix}.venv/bin/python3 scripts/maintenance/generate_system_health.py > /dev/null")
        if rc != 0:
            print(f"WARNING: system_health regeneration exited with code {rc}.")
        
    except Exception as e:
        print(f"Failed: {e}")
        # Revert
        shutil.copy(shard_path + ".bak", shard_path)
        print("Reverted shard to backup.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 commit_node.py <slug> <html_file> [identities_json]")
        sys.exit(1)
    
    slug_arg = sys.argv[1]
    html_arg = sys.argv[2]
    ident_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    commit_node(slug_arg, html_arg, ident_arg)
